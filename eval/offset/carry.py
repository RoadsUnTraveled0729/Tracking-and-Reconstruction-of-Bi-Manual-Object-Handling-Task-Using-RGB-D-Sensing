"""Vendored grip/carry analysis core.

Pure functions copied from the frozen v1 analysis so eval/ can run
them on any recording without dragging in that script's Unity-log
inputs. Provenance (copied 2026-08-25, all from
v1/integration/analyze_object_offset.py):

- recompose_zxy, from_to_rotation: lines 47-63
- world-frame transforms (P, D, M, cam_pos, leveling): lines 42-43,
  94-104, 116-118
- box center from marker pose: line 112
- carry classifier: lines 165-170
- held-frame mask and per-hand fit: lines 185-198
- residual after decoupling: lines 206-215
- segment-length measurement seg(): lines 311-327

validate_eval.py re-runs this module on the pinned R1 inputs and
asserts the pinned per-hand grip numbers reproduce, so copy drift is
detectable.
"""

import numpy as np

P = np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]], float)
D = np.diag([1.0, -1.0, 1.0])

K = 7            # motion window, frames
MOVE_DIST = 0.03  # m over K frames
CARRY_HEIGHT = 0.06  # m above the tabletop


def recompose_zxy(deg):
    """Unity ZXY-applied Euler degrees -> R = Ry.Rx.Rz."""
    x, y, z = np.radians(np.asarray(deg, dtype=float))
    cx, sx = np.cos(x), np.sin(x)
    cy, sy = np.cos(y), np.sin(y)
    cz, sz = np.cos(z), np.sin(z)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Ry @ Rx @ Rz


def from_to_rotation(a, b):
    v, c = np.cross(a, b), float(np.dot(a, b))
    s = np.linalg.norm(v)
    if s < 1e-12:
        return np.eye(3) if c > 0 else -np.eye(3)
    Km = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]],
                   [-v[1], v[0], 0]]) / s
    return np.eye(3) + s * Km + (1 - c) * (Km @ Km)


class LeveledWorld:
    """Transforms into the leveled desk world (gravity = +y) for one
    calibration, as the v1 analysis builds them."""

    def __init__(self, calib):
        T_dc = np.linalg.inv(np.array(calib["T_cam_desk"]))
        self.M = P @ T_dc[:3, :3] @ D          # person space -> local
        self.cam_pos = P @ T_dc[:3, 3]
        g = np.array(calib["scene_geometry"]["gravity_up_unity"], float)
        self.g = g / np.linalg.norm(g)
        self.G = from_to_rotation(self.g, np.array([0.0, 1.0, 0.0]))
        self.drop = calib["scene_geometry"]["origin_above_tabletop_m"]
        self.cube = calib["scene_geometry"]["object_cube_size_m"]

    def level(self, p):
        return (self.G @ np.atleast_2d(np.asarray(p, float)).T).T

    def wrist_world(self, w_cam):
        """Camera-frame landmark positions -> leveled desk world."""
        return self.level((self.M @ (w_cam * [1, -1, 1]).T).T + self.cam_pos)

    def object_world(self, unity_pos, unity_euler):
        """Object unity position/euler columns -> leveled marker track
        and per-frame leveled rotation matrices."""
        obj = self.level(unity_pos)
        R_obj = np.array([self.G @ recompose_zxy(e) for e in unity_euler])
        return obj, R_obj

    def box_center(self, obj, R_obj):
        return obj + R_obj @ np.array([0.0, -self.cube / 2.0, 0.0])

    def height_above_table(self, obj):
        return obj[:, 1] + self.drop


def moving_mask(obj, k=K, dist=MOVE_DIST):
    n = len(obj)
    disp = np.linalg.norm(obj[k:] - obj[:-k], axis=1)
    moving = np.zeros(n, bool)
    moving[k // 2:k // 2 + len(disp)] = disp > dist
    return moving


def carried_mask(obj, world, k=K, dist=MOVE_DIST, height=CARRY_HEIGHT):
    return (world.height_above_table(obj) > height) | moving_mask(obj, k, dist)


def nearest_wrist(obj, wr_left, wr_right):
    """0 = left nearer, 1 = right nearer (NaN-safe argmin)."""
    dists = np.stack([np.linalg.norm(obj - wr_left, axis=1),
                      np.linalg.norm(obj - wr_right, axis=1)])
    with np.errstate(invalid="ignore"):
        nearer = np.nanargmin(np.where(np.isfinite(dists), dists, np.inf),
                              axis=0)
    return nearer, dists


def fit_grip(obj, R_obj, wr, wrist_flag, det, carried, nearer):
    """Per-hand object-frame grip vector fit + decoupling residual.

    Returns dict side -> {hold mask, mu, sd, d_loc, resid}."""
    out = {}
    for si, side in enumerate(("left", "right")):
        d_loc = np.einsum("nij,ni->nj", R_obj, wr[side] - obj)
        hold = det & carried & (nearer == si) \
            & (wrist_flag[side] == 0) & np.isfinite(d_loc).all(axis=1)
        if hold.sum() == 0:
            out[side] = {"hold": hold, "mu": None, "sd": None,
                         "d_loc": d_loc, "resid": np.full(len(obj), np.nan)}
            continue
        mu = d_loc[hold].mean(axis=0)
        sd = d_loc[hold].std(axis=0)
        pred = obj + np.einsum("nij,j->ni", R_obj, mu)
        resid = np.linalg.norm(pred - wr[side], axis=1)
        out[side] = {"hold": hold, "mu": mu, "sd": sd, "d_loc": d_loc,
                     "resid": resid}
    return out


def seg_lengths(lm):
    """Median landmark-to-landmark segment lengths (camera frame)."""
    def seg(a, b):
        pa = lm[[f"{a}_x", f"{a}_y", f"{a}_z"]].values
        pb = lm[[f"{b}_x", f"{b}_y", f"{b}_z"]].values
        return float(np.nanmedian(np.linalg.norm(pa - pb, axis=1)))

    def mid(a, b):
        return (lm[[f"{a}_x", f"{a}_y", f"{a}_z"]].values
                + lm[[f"{b}_x", f"{b}_y", f"{b}_z"]].values) / 2

    torso = float(np.nanmedian(np.linalg.norm(
        mid("left_shoulder", "right_shoulder")
        - mid("left_hip", "right_hip"), axis=1)))
    return {
        "shoulder_width": seg("left_shoulder", "right_shoulder"),
        "upper_arm_R": seg("right_shoulder", "right_elbow"),
        "upper_arm_L": seg("left_shoulder", "left_elbow"),
        "forearm_R": seg("right_elbow", "right_wrist"),
        "forearm_L": seg("left_elbow", "left_wrist"),
        "torso_hip_to_midshoulder": torso,
    }


# ---------------------------------------------------------------------------
# R4-side classifiers (eval additions, not vendored).
#
# The vendored R1 classifier (carried_mask + nearest_wrist) fails on
# R4: the box slides along a desk-level wire at ~3 cm height and a
# median 6.4 cm/s (under both the 6 cm height and the 3 cm / 7 frame
# motion branches), and during the hand-over the true holder's wrist
# is occluded, so nearest-wrist assigns the visible far wrist.
# Evidence and constants: eval/DECISIONS.md E-005/E-006.
# ---------------------------------------------------------------------------

HOLD_RADIUS = 0.25       # m, |wrist - box center| while holding (bimodal gap)
REST_DIST = 0.04         # m from a rest-cluster centroid = "away from rest"
FOREARM_TOL = 0.30       # fractional deviation from median forearm length


def rest_referenced_carried(obj, world, envelope):
    """Carried = inside the motion envelope AND away from both rest
    positions (or moving, or clearly lifted)."""
    n = len(obj)
    a, b = envelope
    inside = np.zeros(n, bool)
    inside[a:b + 1] = True
    rest_pre = np.nanmedian(obj[:a], axis=0) if a > 0 else None
    rest_post = np.nanmedian(obj[b + 1:], axis=0) if b + 1 < n else None
    away = np.ones(n, bool)
    for rest in (rest_pre, rest_post):
        if rest is not None and np.all(np.isfinite(rest)):
            away &= np.linalg.norm(obj - rest, axis=1) > REST_DIST
    lifted = world.height_above_table(obj) > CARRY_HEIGHT
    return inside & (away | moving_mask(obj) | lifted)


def forearm_ok(lm, side, tol=FOREARM_TOL):
    """Frames where the measured forearm length is physically
    plausible (rejects depth-collapse frames where elbow and wrist
    land on the same surface)."""
    pa = lm[[f"{side}_elbow_x", f"{side}_elbow_y",
             f"{side}_elbow_z"]].to_numpy()
    pb = lm[[f"{side}_wrist_x", f"{side}_wrist_y",
             f"{side}_wrist_z"]].to_numpy()
    L = np.linalg.norm(pa - pb, axis=1)
    med = np.nanmedian(L)
    with np.errstate(invalid="ignore"):
        return np.abs(L - med) < tol * med


def holding_mask(center, wr_side, wrist_flag_side, det, carried,
                 forearm_valid, radius=HOLD_RADIUS):
    """Per-hand independent holding classification: this hand holds
    the box when its wrist is measured, geometrically plausible, and
    within the hold radius of the box center, on a carried frame with
    a measured marker. Both hands may hold simultaneously."""
    mag = np.linalg.norm(wr_side - center, axis=1)
    with np.errstate(invalid="ignore"):
        near = mag < radius
    return det & carried & near & (wrist_flag_side == 0) & forearm_valid \
        & np.isfinite(wr_side).all(axis=1)

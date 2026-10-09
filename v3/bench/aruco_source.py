"""ArUco object source for the wrist-to-object bench (D-035).

Reads the thesis's marker-size-corrected ArUco CSVs
(eval/output/<stem>_aruco_raw_scaled.csv: per-frame marker poses in the
RealSense colour-optical frame, metres, 45 mm scale already applied by
eval/gt/scale_correction.py) and the scene calibrations
(eval/output/scene_calibration_<alias>c.json). eval/ is read-only for
V3 (D-007 copy-only), so the transforms are REIMPLEMENTED here:

- LeveledWorld: copied from eval/offset/carry.py class LeveledWorld
  (itself copied from v1/integration/analyze_object_offset.py lines
  42-43, 94-104, 112, 116-118). Same P, D, M, cam_pos, gravity
  levelling G, box centre and table height.
- Camera -> world object pose: v1/aruco/calibrate_scene.py main (the
  per-frame loop, T_w = T_desk_cam @ T_cam_obj) followed by
  v1/aruco/frames.py unity_from_world (P t, P R P). The composition
  leveled R_obj = G P R_desk_cam R_cam_obj P equals carry.py's
  G @ recompose_zxy(euler_unity_zxy(P R_w P)) away from gimbal lock;
  tests/test_aruco_source.py checks it against the thesis's
  <stem>_scaled_object_world.csv.

The V3 bench uses the RAW per-frame ArUco pose (undetected frames NaN).
The thesis graded against the filtered, gap-filled world track
(v1/aruco/filter_object_track.py); that difference is logged in D-035.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

V3_ROOT = Path(__file__).resolve().parents[1]
REPO = V3_ROOT.parent
EVAL_OUT = REPO / "eval" / "output"
EVAL_REPORTS = REPO / "eval" / "reports"

# Stems and aliases copied from eval/common/paths.py (R4_STEM, R5_STEM,
# R6B_STEM, R7_STEM, ALIAS); calibration names follow its calib_for
# rule (<alias>c = marker-size corrected).
STEMS = {"r4": "recording_20260825_070152",
         "r5": "recording_20260825_222315",
         "r6b": "recording_20260831_065553",
         "r7": "recording_20260909_000024"}

# Marker ids: v1/aruco/frames.py MARKERS (wall 0, object 1, desk 2)
OBJECT_ID = 1

# P and D: eval/offset/carry.py lines 24-25
P = np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]], float)
D = np.diag([1.0, -1.0, 1.0])


def aruco_csv(stem):
    return EVAL_OUT / f"{stem}_aruco_raw_scaled.csv"


def calib_path(alias):
    return EVAL_OUT / f"scene_calibration_{alias}c.json"


def inspection_path(stem):
    return EVAL_REPORTS / f"{stem}_inspection.json"


def recompose_zxy(deg):
    """Unity ZXY Euler degrees -> Ry.Rx.Rz (carry.py recompose_zxy,
    identical to vendor/v1/root_frame.py recompose_zxy)."""
    x, y, z = np.radians(np.asarray(deg, dtype=float))
    cx, sx = np.cos(x), np.sin(x)
    cy, sy = np.cos(y), np.sin(y)
    cz, sz = np.cos(z), np.sin(z)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Ry @ Rx @ Rz


def from_to_rotation(a, b):
    """eval/offset/carry.py from_to_rotation (copied)."""
    v, c = np.cross(a, b), float(np.dot(a, b))
    s = np.linalg.norm(v)
    if s < 1e-12:
        return np.eye(3) if c > 0 else -np.eye(3)
    Km = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]],
                   [-v[1], v[0], 0]]) / s
    return np.eye(3) + s * Km + (1 - c) * (Km @ Km)


class LeveledWorld:
    """Levelled desk world (gravity = +y, Unity axis order) for one
    scene calibration. Reimplements eval/offset/carry.py LeveledWorld."""

    def __init__(self, calib):
        T_dc = np.linalg.inv(np.array(calib["T_cam_desk"], float))
        self.R_dc = T_dc[:3, :3]
        self.t_dc = T_dc[:3, 3]
        self.M = P @ self.R_dc @ D            # solver space -> local
        self.cam_pos = P @ self.t_dc
        g = np.array(calib["scene_geometry"]["gravity_up_unity"], float)
        self.g = g / np.linalg.norm(g)
        self.G = from_to_rotation(self.g, np.array([0.0, 1.0, 0.0]))
        self.drop = calib["scene_geometry"]["origin_above_tabletop_m"]
        self.cube = calib["scene_geometry"]["object_cube_size_m"]

    def level(self, p):
        return (self.G @ np.atleast_2d(np.asarray(p, float)).T).T

    def world_from_cam(self, p_cam):
        """Camera-optical points (N, 3) -> levelled world; the same
        chain as carry.py wrist_world (flip to solver space, M, cam_pos,
        level)."""
        p_cam = np.atleast_2d(np.asarray(p_cam, float))
        return self.level((self.M @ (p_cam * [1, -1, 1]).T).T
                          + self.cam_pos)

    def rot_from_cam(self, R_cam):
        """Camera-optical marker rotations (N, 3, 3) -> levelled world
        rotations G P R_desk_cam R P (calibrate_scene.py + frames.py
        unity_from_world, then carry.py levelling)."""
        A = self.G @ P @ self.R_dc
        return np.einsum("ij,njk,kl->nil", A, np.asarray(R_cam, float), P)

    def object_world(self, unity_pos, unity_euler):
        """Thesis path (carry.py object_world): Unity position/Euler
        columns of <stem>_*object_world*.csv -> levelled track."""
        obj = self.level(unity_pos)
        R_obj = np.array([self.G @ recompose_zxy(e) for e in unity_euler])
        return obj, R_obj

    def box_center(self, obj, R_obj):
        """Marker origin + R (0, -cube/2, 0): carry.py box_center."""
        return obj + R_obj @ np.array([0.0, -self.cube / 2.0, 0.0])

    def height_above_table(self, obj):
        return obj[:, 1] + self.drop


def load_world(alias):
    return LeveledWorld(json.loads(calib_path(alias).read_text()))


def read_object(stem, world, marker_id=OBJECT_ID):
    """Per-frame object pose from the scaled ArUco CSV.

    Returns a dict of arrays indexed by ArUco row: frame, time_s,
    det (bool), obj_cam (N, 3), R_cam (N, 3, 3), obj (levelled world
    marker origin), R_obj (levelled), center (levelled box centre).
    Undetected frames are NaN."""
    df = pd.read_csv(aruco_csv(stem))
    m = f"m{marker_id}"
    det = df[f"{m}_detected"].to_numpy() == 1
    t = df[[f"{m}_tx", f"{m}_ty", f"{m}_tz"]].to_numpy(dtype=float)
    R = np.stack([df[[f"{m}_r{i}1", f"{m}_r{i}2", f"{m}_r{i}3"]]
                  .to_numpy(dtype=float) for i in (1, 2, 3)], axis=1)
    t[~det] = np.nan
    R[~det] = np.nan
    obj = world.world_from_cam(t)
    R_obj = world.rot_from_cam(R)
    return {"frame": df["frame"].to_numpy(dtype=int),
            "time_s": df["time_s"].to_numpy(dtype=float),
            "det": det, "obj_cam": t, "R_cam": R,
            "obj": obj, "R_obj": R_obj,
            "center": world.box_center(obj, R_obj)}


def align(obj, frames):
    """Select ArUco rows for the given V3 frame indices (frame index
    equality, offset 0: D-035). Returns a dict of the same keys,
    row-aligned with `frames`; raises when a frame has no ArUco row."""
    index = {int(f): i for i, f in enumerate(obj["frame"])}
    missing = [int(f) for f in frames if int(f) not in index]
    if missing:
        raise ValueError(f"{len(missing)} V3 frames have no ArUco row "
                         f"(first {missing[:5]})")
    rows = np.array([index[int(f)] for f in frames])
    return {k: v[rows] for k, v in obj.items()}


def check_alignment(aruco_t, v3_t):
    """Per-frame time agreement after frame-index alignment. The
    tolerance is half the median frame period of the V3 CSV (D-035).
    Returns a dict: n, max_abs_dt_s, half_frame_s, ok."""
    aruco_t = np.asarray(aruco_t, float)
    v3_t = np.asarray(v3_t, float)
    dt = np.abs(aruco_t - v3_t)
    half = 0.5 * float(np.median(np.diff(v3_t)))
    return {"n": int(len(dt)), "max_abs_dt_s": float(np.max(dt)),
            "median_abs_dt_s": float(np.median(dt)),
            "half_frame_s": half, "ok": bool(np.max(dt) < half)}

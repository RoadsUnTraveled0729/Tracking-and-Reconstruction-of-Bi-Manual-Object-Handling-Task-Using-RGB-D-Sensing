"""Chain-fallback per-joint solve for blocked landmarks (KINEMATIC_MODEL.md §10).

The kinematic chain is traceable: hips (L23/L24 root) -> shoulders ->
elbows -> wrists. When a landmark is blocked (empty cell from the
extractor's visibility gate / depth window, or a filter gap too long to
interpolate), only the joints that NEED it hold their last valid angle;
every joint whose landmarks survive keeps solving live. A held joint's
children are implicitly reconstructed by the parent chain's forward
kinematics x fixed bone length — guessing in angle space, which stays
bone-length consistent and reachable, unlike guessing the 3D point.

Landmark requirements per joint (= exactly what a blocked landmark costs):

  root frame   : L23 + L24 + one shoulder (either — the shoulder only
                 selects the coronal plane; its component along the hip
                 line is discarded by the cross product)
  R sh swing   : L12 + L14   (solved against the current-or-held root)
  R twist+elbow: ... + L16   (wrist blocked costs only these 3 DOF)
  left arm     : mirror, L11/L13/L15

Straight-elbow twist unobservability (§6.3) unifies with occlusion:
unobservable ⇒ hold last valid twist (supersedes the old θτ := 0
convention for streaming; the pure solvers in shoulder.py are unchanged).

Before the first valid sample a joint emits rest: root (0, 180, 0)
(facing the camera), all arm angles 0.
"""
import numpy as np

from root_frame import build_root_frame, euler_unity_zxy, recompose_zxy
from shoulder import solve_left_arm, solve_right_arm

# Live-mask bits: set = joint solved from this frame's landmarks,
# clear = held at its last valid value (or rest).
BIT_ROOT, BIT_R_SWING, BIT_R_TWIST, BIT_R_ELBOW, \
    BIT_L_SWING, BIT_L_TWIST, BIT_L_ELBOW = (1 << i for i in range(7))
MASK_ALL = (1 << 7) - 1
BIT_NAMES = ("root", "R_swing", "R_twist", "R_elbow",
             "L_swing", "L_twist", "L_elbow")

ROOT_REST_DEG = np.array([0.0, 180.0, 0.0])

LANDMARKS = ("left_hip", "right_hip", "left_shoulder", "right_shoulder",
             "left_elbow", "right_elbow", "left_wrist", "right_wrist")


def _ok(p):
    return p is not None and bool(np.all(np.isfinite(p)))


class ChainFallbackSolver:
    """Stateful per-frame solve with hold-last-valid per joint.

    solve(points) -> (angles13, live_mask)
      points: dict landmark-name -> xyz in Unity space; a blocked landmark
        is absent, None, or contains NaN.
      angles13: root x,y,z | R sh θy,θz,θτ | R elb ey,ez |
                L sh θy,θz,θτ | L elb ey,ez  (degrees, PSA packet order)
      live_mask: BIT_* set for every joint solved live this frame.
    """

    def __init__(self):
        self.root = ROOT_REST_DEG.copy()
        self.R_root = recompose_zxy(ROOT_REST_DEG)
        self.rsh = np.zeros(3)
        self.relb = np.zeros(2)
        self.lsh = np.zeros(3)
        self.lelb = np.zeros(2)

    def solve(self, points):
        p = {k: (np.asarray(points[k], dtype=float) if k in points
                 and points[k] is not None else None) for k in LANDMARKS}
        ok = {k: _ok(p[k]) for k in LANDMARKS}
        mask = 0

        # Root: both hips + either shoulder as the tilt reference.
        ref = (p["right_shoulder"] if ok["right_shoulder"]
               else p["left_shoulder"] if ok["left_shoulder"] else None)
        if ok["left_hip"] and ok["right_hip"] and ref is not None:
            self.R_root = build_root_frame(p["left_hip"], p["right_hip"], ref)
            self.root = euler_unity_zxy(self.R_root)
            mask |= BIT_ROOT

        mask |= self._arm(p, ok, "right_shoulder", "right_elbow",
                          "right_wrist", solve_right_arm, self.rsh, self.relb,
                          BIT_R_SWING, BIT_R_TWIST, BIT_R_ELBOW)
        mask |= self._arm(p, ok, "left_shoulder", "left_elbow",
                          "left_wrist", solve_left_arm, self.lsh, self.lelb,
                          BIT_L_SWING, BIT_L_TWIST, BIT_L_ELBOW)

        angles = np.concatenate(
            [self.root, self.rsh, self.relb, self.lsh, self.lelb])
        return angles, mask

    def _arm(self, p, ok, sh_n, el_n, wr_n, solver, state_sh, state_el,
             bit_swing, bit_twist, bit_elbow):
        if not (ok[sh_n] and ok[el_n]):
            return 0  # shoulder chain unobservable -> whole arm holds
        if ok[wr_n]:
            wr = p[wr_n]
        else:
            # Fake straight-arm wrist: keeps the pure solver applicable,
            # makes twist unobservable by construction (perp part = 0),
            # and yields ey = 0, both of which are discarded below.
            wr = p[el_n] + (p[el_n] - p[sh_n])
        sh, elb, twist_ok = solver(p[sh_n], p[el_n], wr, self.R_root)
        live = bit_swing
        if ok[wr_n] and twist_ok:
            live |= bit_twist
        else:
            sh[2] = state_sh[2]  # hold last twist (blocked or unobservable)
        if ok[wr_n]:
            live |= bit_elbow
            state_el[:] = elb
        state_sh[:] = sh
        return live


def points_from_row(row):
    """Extractor CSV row (pandas Series) -> points dict for solve();
    missing cells (NaN) mark the landmark blocked."""
    return {k: np.array([row[f"{k}_x"], row[f"{k}_y"], row[f"{k}_z"]],
                        dtype=float) for k in LANDMARKS}

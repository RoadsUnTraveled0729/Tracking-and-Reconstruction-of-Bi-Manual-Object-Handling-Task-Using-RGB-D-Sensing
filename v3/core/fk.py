"""Forward kinematics of the 13-angle v1 chain (D-037).

Built on the VERBATIM vendored v1 modules so the conventions cannot
drift: root R = vendor/v1/root_frame.py recompose_zxy(root x, y, z);
shoulder R = vendor/v1/shoulder.py recompose_shoulder(ty, tz, tt) =
Ry.Rz.Rx; elbow R = shoulder._ry(ey) @ shoulder._rz(ez). Precedent:
eval/failure/moving_window_check.py fk_wrist (with
eval/inspect/check_v1_overlay.py fk_arm_dirs):

    elbow = anchor + Lu * R_root @ up
    wrist = elbow + Lf * R_root @ fore
    right: up = R_sh x,        fore = R_sh R_elb x
    left:  up = M R_sh x,      fore = M R_sh R_elb x,  M = MIRROR

The left form is the vendored solve_left_arm docstring's
"M.R.M, rest arm = -x": (M R M)(M x) = M R x.

All positions are in the solver (Unity) space, i.e. camera optical
with y flipped (vendor/v1/root_frame.py unity_from_sensor).

Anchors (D-037): (a) the measured shoulder landmark; (b) the right hip
L24 plus a per-recording hip-to-shoulder offset expressed in the root
frame, offset = median over the recording of R_root^T (shoulder - L24).
"""
import sys
from pathlib import Path

import numpy as np

_VENDOR = Path(__file__).resolve().parents[1] / "vendor" / "v1"
if str(_VENDOR) not in sys.path:
    sys.path.insert(0, str(_VENDOR))

from root_frame import recompose_zxy                       # noqa: E402
from shoulder import MIRROR, _ry, _rz, recompose_shoulder  # noqa: E402

_X = np.array([1.0, 0.0, 0.0])
SIDE_INDEX = {"right": 3, "left": 8}   # PSA order, vendor/v1/occlusion.py


def arm_dirs(sh_deg, elb_deg, side):
    """Unit upper-arm and forearm directions in the ROOT frame."""
    R_sh = recompose_shoulder(sh_deg)
    ey, ez = np.radians(np.asarray(elb_deg, dtype=float))
    up = R_sh @ _X
    fore = R_sh @ (_ry(ey) @ _rz(ez)) @ _X
    if side == "left":
        up, fore = MIRROR * up, MIRROR * fore
    elif side != "right":
        raise ValueError(f"side must be right or left, got {side!r}")
    return up, fore


def fk_arm(angles13, side, Lu, Lf, anchor):
    """One frame: (elbow, wrist) solver-space positions from the 13
    PSA-order angles (degrees), bone lengths (m) and the shoulder
    anchor (solver space). NaN in any used angle gives NaN."""
    a = np.asarray(angles13, dtype=float)
    si = SIDE_INDEX[side]
    used = np.r_[a[:3], a[si:si + 5]]
    if not np.all(np.isfinite(used)):
        nan = np.full(3, np.nan)
        return nan, nan.copy()
    R_root = recompose_zxy(a[:3])
    up, fore = arm_dirs(a[si:si + 3], a[si + 3:si + 5], side)
    elbow = np.asarray(anchor, float) + Lu * (R_root @ up)
    return elbow, elbow + Lf * (R_root @ fore)


def fk_arm_series(A, side, Lu, Lf, anchors):
    """Per-frame fk_arm over (N, 13) angles and (N, 3) anchors. Lu, Lf
    are scalars or (N,) arrays. Returns (elbows, wrists), (N, 3)."""
    A = np.asarray(A, float)
    n = len(A)
    Lu = np.broadcast_to(np.asarray(Lu, float), (n,))
    Lf = np.broadcast_to(np.asarray(Lf, float), (n,))
    el = np.full((n, 3), np.nan)
    wr = np.full((n, 3), np.nan)
    for i in range(n):
        el[i], wr[i] = fk_arm(A[i], side, Lu[i], Lf[i], anchors[i])
    return el, wr


def root_matrices(A):
    """(N, 13) angles -> (N, 3, 3) root rotations (NaN rows stay NaN)."""
    A = np.asarray(A, float)
    out = np.full((len(A), 3, 3), np.nan)
    for i, a in enumerate(A):
        if np.all(np.isfinite(a[:3])):
            out[i] = recompose_zxy(a[:3])
    return out


def hip_shoulder_offset(A, hip_r, shoulder):
    """Per-recording offset of a shoulder from the right hip L24 in
    the root frame: component-wise median over frames of
    R_root^T (shoulder - hip). Solver space. D-037."""
    R = root_matrices(A)
    d = np.einsum("nji,nj->ni", R, np.asarray(shoulder, float)
                  - np.asarray(hip_r, float))
    ok = np.isfinite(d).all(axis=1)
    if not ok.any():
        raise ValueError("no frame with root, hip and shoulder")
    return np.median(d[ok], axis=0), int(ok.sum())


def hip_anchor(A, hip_r, offset):
    """Anchor (b): hip L24 + R_root @ offset per frame."""
    R = root_matrices(A)
    return np.asarray(hip_r, float) + np.einsum("nij,j->ni", R, offset)

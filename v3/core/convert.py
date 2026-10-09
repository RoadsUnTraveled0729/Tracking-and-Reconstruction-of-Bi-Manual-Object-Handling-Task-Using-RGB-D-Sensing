"""Quaternion state -> v1 angle interface (the comparability contract).

V3's internal representation is unit quaternions (D-005); the 13 output
angles use v1's exact definitions. Root angles are produced by the
VERBATIM vendored euler_unity_zxy on matrix_from_quat(q). Shoulder and
elbow angles invert the vendored recompose_shoulder parameterization
R = Ry(ty) * Rz(tz) * Rx(tt) (v1 has no matrix-side extractor -- its
solvers work from landmarks -- so the inversion lives here and the
oracle-identity tests close the loop through the landmark path to
1e-9 deg).

Left-arm quaternions live in v1's MIRRORED right-hand space (see
solver_q.py); their angle extraction is therefore identical to the
right arm's, exactly as in v1.

Angle order (PSA packet, vendor/v1/occlusion.py): root x,y,z |
R sh ty,tz,tt | R elb ey,ez | L sh ty,tz,tt | L elb ey,ez.
"""
import sys
from pathlib import Path

import numpy as np

_VENDOR = Path(__file__).resolve().parents[1] / "vendor" / "v1"
if str(_VENDOR) not in sys.path:
    sys.path.insert(0, str(_VENDOR))

from root_frame import euler_unity_zxy  # noqa: E402  vendored, verbatim

from core.representation import matrix_from_quat  # noqa: E402

GIMBAL_EPS = 1e-8  # matches vendored shoulder.GIMBAL_EPS


def root_angles(q_root):
    """Root quaternion -> Unity ZXY Euler degrees via the VENDORED trig."""
    return euler_unity_zxy(matrix_from_quat(q_root))


def shoulder_angles(q_sh):
    """Shoulder quaternion -> (ty, tz, tt) degrees, inverting
    R = Ry(ty) * Rz(tz) * Rx(tt).

    Column 0 of R is Ry*Rz*x_hat = (cy*cz, sz, -sy*cz), so
    tz = asin(R[1,0]) and ty = atan2(-R[2,0], R[0,0]); at the gimbal
    (|sz| ~ 1) v1 sets ty := 0 (axial rotation folds into the twist).
    Un-swinging leaves Rx(tt): tt = atan2(N[2,1], N[1,1]).
    """
    R = matrix_from_quat(q_sh)
    sz = float(np.clip(R[1, 0], -1.0, 1.0))
    tz = np.arcsin(sz)
    ty = 0.0 if 1.0 - abs(sz) < GIMBAL_EPS else float(
        np.arctan2(-R[2, 0], R[0, 0]))
    cy, sy = np.cos(ty), np.sin(ty)
    cz, szc = np.cos(tz), np.sin(tz)
    Ry_inv = np.array([[cy, 0, -sy], [0, 1, 0], [sy, 0, cy]])
    Rz_inv = np.array([[cz, szc, 0], [-szc, cz, 0], [0, 0, 1]])
    N = Rz_inv @ (Ry_inv @ R)
    tt = float(np.arctan2(N[2, 1], N[1, 1]))
    return np.degrees(np.array([ty, tz, tt]))


def elbow_angles(q_elb):
    """Elbow quaternion -> (ey, ez) degrees, inverting
    R = Ry(ey) * Rz(ez). Same column-0 geometry as the shoulder swing;
    v1's elbow solve has no gimbal branch (ez == 0 by construction),
    so none is applied here."""
    R = matrix_from_quat(q_elb)
    ez = np.arcsin(float(np.clip(R[1, 0], -1.0, 1.0)))
    ey = float(np.arctan2(-R[2, 0], R[0, 0]))
    return np.degrees(np.array([ey, ez]))


def angles13(q_root, q_rsh, q_relb, q_lsh, q_lelb):
    """Assemble the 13-angle PSA-order vector from the joint quats."""
    return np.concatenate([
        root_angles(q_root),
        shoulder_angles(q_rsh), elbow_angles(q_relb),
        shoulder_angles(q_lsh), elbow_angles(q_lelb),
    ])

"""Per-frame landmark solve producing quaternion joint state.

Reimplements the v1 solver geometry (vendor/v1/root_frame.py and
shoulder.py) with quaternion outputs. The branch logic (gimbal ty := 0,
straight-elbow twist tt := 0) matches solve_right_arm exactly; the
oracle-identity tests pin the whole path against the VERBATIM vendored
solvers to 1e-9 deg. Epsilon constants are imported from the vendored
module so they can never drift.

Left arm: v1 defines left angles as the right-solver angles of the
sagittally mirrored pose. The left joint quaternions returned here
therefore live in that MIRRORED space -- correct for prediction,
filtering, and blending (mirroring is a conjugation; the manifold
geometry is identical), and convert.py extracts their angles exactly
like the right arm's, which is precisely v1's definition.

Statelessness: this module solves one frame from whatever landmarks are
present and reports what was solvable. Hold/predict/blend policy is the
occlusion strategies' job (Phase 4), not the solver's.
"""
import sys
from pathlib import Path

import numpy as np

_VENDOR = Path(__file__).resolve().parents[1] / "vendor" / "v1"
if str(_VENDOR) not in sys.path:
    sys.path.insert(0, str(_VENDOR))

from shoulder import GIMBAL_EPS, TWIST_EPS, MIRROR  # noqa: E402  vendored

from core.representation import (  # noqa: E402
    matrix_from_quat, qmul, quat_about, quat_from_matrix, qrotate,
)

_X = np.array([1.0, 0.0, 0.0])
_Y = np.array([0.0, 1.0, 0.0])
_Z = np.array([0.0, 0.0, 1.0])


def _normalize(v):
    n = np.linalg.norm(v)
    if n == 0.0:
        raise ValueError("zero-length vector in solve")
    return v / n


def solve_root_q(p_lhip, p_rhip, p_ref):
    """Root frame as a quaternion; same construction as the vendored
    build_root_frame (hip line primary, reference shoulder selects the
    coronal plane, up recovered by the final cross)."""
    p_lhip = np.asarray(p_lhip, dtype=float)
    p_rhip = np.asarray(p_rhip, dtype=float)
    p_ref = np.asarray(p_ref, dtype=float)
    r = _normalize(p_rhip - p_lhip)
    s = p_ref - p_rhip
    f = _normalize(np.cross(r, s))
    u = np.cross(f, r)
    return quat_from_matrix(np.stack([r, u, f], axis=-1))


def solve_right_arm_q(p_sh, p_el, p_wr, q_root):
    """Right arm from Unity-space landmarks and the root quaternion.

    Returns (q_sh, q_elb, twist_ok): shoulder quat Ry(ty)Rz(tz)Rx(tt),
    elbow quat Ry(ey)Rz(ez), and whether the twist was observable
    (straight elbow -> tt := 0 and twist_ok False, exactly v1's
    solve_right_arm convention).
    """
    p_sh = np.asarray(p_sh, dtype=float)
    p_el = np.asarray(p_el, dtype=float)
    p_wr = np.asarray(p_wr, dtype=float)
    R_root_T = matrix_from_quat(q_root).T

    a = _normalize(R_root_T @ (p_el - p_sh))
    sz = float(np.clip(a[1], -1.0, 1.0))
    tz = np.arcsin(sz)
    ty = 0.0 if 1.0 - abs(sz) < GIMBAL_EPS else float(
        np.arctan2(-a[2], a[0]))

    q_swing = qmul(quat_about(_Y, ty), quat_about(_Z, tz))
    f = R_root_T @ (p_wr - p_el)
    fp = qrotate(qmul(quat_about(_Z, -tz), quat_about(_Y, -ty)), f)
    perp = float(np.hypot(fp[1], fp[2]))
    twist_ok = perp >= TWIST_EPS * np.linalg.norm(f)
    tt = float(np.arctan2(-fp[1], fp[2])) if twist_ok else 0.0
    q_sh = qmul(q_swing, quat_about(_X, tt))

    R_arm_T = matrix_from_quat(q_sh).T @ R_root_T
    g = _normalize(R_arm_T @ (p_wr - p_el))
    ez = np.arcsin(float(np.clip(g[1], -1.0, 1.0)))
    ey = float(np.arctan2(-g[2], g[0]))
    q_elb = qmul(quat_about(_Y, ey), quat_about(_Z, ez))
    return q_sh, q_elb, twist_ok


def solve_left_arm_q(p_sh, p_el, p_wr, q_root):
    """Left arm via v1's mirror definition: express both segment
    vectors in the root basis, flip x, run the identical right-arm
    solve with an identity root. Returned quats live in the mirrored
    space (see module docstring)."""
    R_root_T = matrix_from_quat(q_root).T
    u = MIRROR * (R_root_T @ (np.asarray(p_el, dtype=float)
                              - np.asarray(p_sh, dtype=float)))
    f = MIRROR * (R_root_T @ (np.asarray(p_wr, dtype=float)
                              - np.asarray(p_el, dtype=float)))
    zero = np.zeros(3)
    return solve_right_arm_q(zero, u, u + f,
                             np.array([1.0, 0.0, 0.0, 0.0]))


def _finite(p):
    return p is not None and bool(np.all(np.isfinite(p)))


def solve_frame_q(points):
    """Solve every joint solvable from this frame's landmarks.

    points: dict v1-landmark-name -> xyz (Unity space); blocked
    landmarks are absent, None, or NaN.

    Returns a dict with 'root', 'r_sh', 'r_elb', 'l_sh', 'l_elb'
    (unit quaternion or None when unsolvable this frame), plus
    'r_twist_ok' / 'l_twist_ok' (False when the arm was unsolvable or
    the twist unobservable). Landmark requirements mirror
    vendor/v1/occlusion.py: root needs both hips + either shoulder;
    an arm needs shoulder + elbow (wrist missing -> v1's fake
    straight-arm wrist, so the swing still solves and twist/elbow are
    reported unobservable).
    """
    p = {k: (np.asarray(v, dtype=float) if v is not None else None)
         for k, v in points.items()}
    ok = {k: _finite(p.get(k)) for k in
          ("left_hip", "right_hip", "left_shoulder", "right_shoulder",
           "left_elbow", "right_elbow", "left_wrist", "right_wrist")}

    out = {"root": None, "r_sh": None, "r_elb": None,
           "l_sh": None, "l_elb": None,
           "r_twist_ok": False, "l_twist_ok": False}

    ref = (p["right_shoulder"] if ok["right_shoulder"]
           else p["left_shoulder"] if ok["left_shoulder"] else None)
    if ok["left_hip"] and ok["right_hip"] and ref is not None:
        out["root"] = solve_root_q(p["left_hip"], p["right_hip"], ref)

    if out["root"] is not None:
        for side, solver in (("r", solve_right_arm_q),
                             ("l", solve_left_arm_q)):
            names = (("right_shoulder", "right_elbow", "right_wrist")
                     if side == "r" else
                     ("left_shoulder", "left_elbow", "left_wrist"))
            sh_n, el_n, wr_n = names
            if not (ok[sh_n] and ok[el_n]):
                continue
            if ok[wr_n]:
                wr = p[wr_n]
                wrist_seen = True
            else:
                wr = p[el_n] + (p[el_n] - p[sh_n])  # v1 fake wrist
                wrist_seen = False
            q_sh, q_elb, twist_ok = solver(p[sh_n], p[el_n], wr,
                                           out["root"])
            out[f"{side}_sh"] = q_sh
            out[f"{side}_elb"] = q_elb if wrist_seen else None
            out[f"{side}_twist_ok"] = bool(twist_ok and wrist_seen)
    return out

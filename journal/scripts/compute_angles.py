"""Milestone M3 of the journal track (J-009): the joint angles of the
worked-example frame, Method A (frozen thesis code) and Method B
(right-handed, J-002, J-008), with every intermediate quantity dumped so
that the derivation document can substitute the numbers step by step.

Input: a pick JSON written by select_perfect_frame.py (default
journal/data/perfect_frame.json). The 8 landmarks' camera coordinates are
read from model_landmarks[k]["xyz_med5_m"]: the deprojection with the 5x5
median of nonzero depth returns, which is the frozen extractor's
--depth-window 5 default and the value the thesis pipeline uses (the pick
JSON's model_landmarks_note). The single-pixel deprojection xyz_px_m is
read as well and the output states whether the two agree.

Method A (exactly the frozen code, imported from v1/kinematics, never
copied or edited):
    p' = unity_from_sensor(p)                    {Camera} -> {Camera'}
    R_A = build_root_frame(p23', p24', p12')     columns [r | u | f]
    root Euler = euler_unity_zxy(R_A)            (x, y, z), R = Ry Rx Rz
    right arm = solve_right_arm(p12', p14', p16', R_A)
    left arm  = solve_left_arm(p11', p13', p15', R_A)
    13-vector in the PSA order of v1/kinematics/occlusion.py:
    root x, y, z | R sh th_y, th_z, th_t | R elb ey, ez |
    L sh th_y, th_z, th_t | L elb ey, ez   (degrees)

Method B (J-002, J-008; no flip, all points stay in {Camera}):
    x = normalize(p23 - p24)    subject's left
    s = p12 - p24
    z = normalize(x cross s)    subject's forward
    y = z cross x               subject's up
    R_B = [x | y | z]           (columns, in {Camera})
    root Euler: the same ZXY formulas (euler_unity_zxy) applied to R_B. The
    reading is relative to the {Camera} axes (x right, y DOWN, z forward),
    not to the y-up {Camera'} of Method A, so its numbers are not Unity
    Euler angles.
    Arms. The frozen swing-twist solver measures the upper-arm swing from
    a rest direction of local +x. In Method B the root x axis is the
    subject's LEFT, so at rest:
      - the LEFT upper arm points along local +x: the frozen right-arm
        formulas apply directly, solve_right_arm(p11, p13, p15, R_B);
      - the RIGHT upper arm points along local -x: both of its segment
        vectors are first expressed in the Method B root basis,
        R_B^T (p14 - p12) and R_B^T (p16 - p14), then their x components
        are negated by M = diag(-1, 1, 1) (the frozen MIRROR), and the
        frozen right-arm solve runs on the mirrored vectors with an
        identity root, solve_right_arm(0, u, u + f, I). This is the same
        call pattern as the frozen solve_left_arm. The mirror is applied
        so that the right arm's rest maps onto +x, the rest direction the
        frozen formulas (thesis eqs. 3.15-3.24) assume; nothing else of
        the solver is changed (J-012).
    World reconstruction of the Method B right arm therefore uses
    R_B M R_sh M with rest -x, and of the left arm R_B R_sh with rest +x.

Method B native (J-013; no mirror, written to angles_method_b_native.json):
    Same root R_B and root Euler as Method B. Rest (T-pose in {L24*}):
    right upper arm and forearm along local -x, left along local +x.
    Swing R_sw = Ry(th_y) Rz(th_z) (the frozen _ry/_rz matrices, standard
    right-handed rotations). The twist th_t is the right-handed rotation
    by th_t about the arm's own rest axis (the outward axis): for the left
    arm the axis is +x, R_tw = Rx(th_t); for the right arm the axis is -x,
    R_tw = R_{-x}(th_t) = Rx(-th_t). R_sh = R_sw R_tw. Zero twist: the
    forearm's component perpendicular to the arm axis points along local
    +z (the thesis convention).
    Right arm, a = normalize(R_B^T (p14 - p12)):
        a = Ry Rz (-1, 0, 0)^T = (-cos th_z cos th_y, -sin th_z,
                                  cos th_z sin th_y)^T
        th_z = -asin(a_y),  th_y = atan2(a_z, -a_x)
        f' = Rz(-th_z) Ry(-th_y) R_B^T (p16 - p14)
           = Rx(-th_t) (f_par, 0, |f_perp|)^T
           -> (f'_y, f'_z) = |f_perp| (sin th_t, cos th_t)
        th_t = atan2(f'_y, f'_z)
        R_arm = R_B Ry(th_y) Rz(th_z) Rx(-th_t),
        g = normalize(R_arm^T (p16 - p14)) = Ry(ey) Rz(ez) (-1, 0, 0)^T
        ez = -asin(g_y),  ey = atan2(g_z, -g_x)
    Left arm: the thesis formulas unchanged in R_B (rest +x):
        th_z = asin(a_y), th_y = atan2(-a_z, a_x), th_t = atan2(-f'_y, f'_z),
        ez = asin(g_y), ey = atan2(-g_z, g_x).
    Gimbal (th_y := 0) and straight-elbow (th_t := 0) conventions and their
    thresholds are the frozen GIMBAL_EPS and TWIST_EPS.

Tolerances and their sources:
    TOL_BRIEF = 1e-9: the M3 brief (recompose_zxy reproduces R_A, and the
        unit dot product of the reconstructed and measured upper-arm
        direction is at least 1 - 1e-9).
    TOL_EXACT = 1e-12: the worker's choice for relations that hold exactly
        in real arithmetic (det = 1, R_B^T F R_A = diag(-1, 1, 1), the
        replicated intermediates against the frozen function outputs). The
        inputs are unit vectors and metre-scale points, so float64 round-off
        is of order 1e-15; 1e-12 leaves three decades of margin. No
        measurement behind the value beyond that estimate.

Run:
    /home/luo/anaconda3/bin/python journal/scripts/compute_angles.py \
        [--pick journal/data/perfect_frame.json] [--native-b]
Outputs: journal/data/angles_method_a.json, journal/data/angles_method_b.json
and journal/data/angles_method_b_native.json. With --native-b only the
native file is written (A and B are still computed in memory for the
comparison) and only the native section is printed; the A and B files
and their checks are unchanged by the native solve.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
DEFAULT_PICK = REPO / "journal" / "data" / "perfect_frame.json"
OUT_A = REPO / "journal" / "data" / "angles_method_a.json"
OUT_B = REPO / "journal" / "data" / "angles_method_b.json"
OUT_BN = REPO / "journal" / "data" / "angles_method_b_native.json"

# v1 is frozen: import only; do not write bytecode into v1/kinematics.
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO / "v1" / "kinematics"))
from root_frame import (  # noqa: E402
    SENSOR_TO_UNITY, build_root_frame, euler_unity_zxy, normalize,
    recompose_zxy, unity_from_sensor, wrap_deg)
from shoulder import (  # noqa: E402
    GIMBAL_EPS, MIRROR, TWIST_EPS, _rx, _ry, _rz, solve_left_arm,
    solve_right_arm)

TOL_BRIEF = 1e-9
TOL_EXACT = 1e-12

F = np.diag(SENSOR_TO_UNITY)   # {Camera} -> {Camera'}, diag(1, -1, 1)
M = np.diag(MIRROR)            # sagittal mirror in a root basis, diag(-1, 1, 1)
X_HAT = np.array([1.0, 0.0, 0.0])

LANDMARK_IDS = (11, 12, 13, 14, 15, 16, 23, 24)
ANGLE_NAMES = (
    "root_x", "root_y", "root_z",
    "R_sh_th_y", "R_sh_th_z", "R_sh_th_t", "R_elb_ey", "R_elb_ez",
    "L_sh_th_y", "L_sh_th_z", "L_sh_th_t", "L_elb_ey", "L_elb_ez",
)

CHECKS = []
NATIVE_CHECKS = []   # kept apart so the A and B JSON 'checks' are unchanged


def check(name, ok, detail, sink=CHECKS):
    sink.append({"name": name, "pass": bool(ok), "detail": detail})


def sig(obj):
    """numpy / nested containers -> plain floats with 12 significant digits."""
    if isinstance(obj, dict):
        return {k: sig(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sig(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return sig(obj.tolist())
    if isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    if isinstance(obj, (int, np.integer)):
        return int(obj)
    if isinstance(obj, (float, np.floating)):
        x = float(obj)
        if not np.isfinite(x):
            return None if np.isnan(x) else x
        return float(f"{x:.12g}")
    return obj


def deg_rad(rad):
    rad = float(rad)
    return {"rad": rad, "deg": float(np.degrees(rad))}


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------
def load_points(pick_path):
    pick = json.loads(Path(pick_path).read_text())
    ml = pick["model_landmarks"]
    med5 = {k: np.array(ml[str(k)]["xyz_med5_m"], dtype=float)
            for k in LANDMARK_IDS}
    px = {k: np.array(ml[str(k)]["xyz_px_m"], dtype=float)
          for k in LANDMARK_IDS}
    same = all(np.array_equal(med5[k], px[k]) for k in LANDMARK_IDS)
    meta = {
        "pick_json": str(Path(pick_path).resolve().relative_to(REPO))
        if Path(pick_path).resolve().is_relative_to(REPO) else str(pick_path),
        "bag": pick["bag"],
        "frame_index": pick["frame_index"],
        "hw_frame_number": pick.get("hw_frame_number"),
        "input_field": "model_landmarks[k].xyz_med5_m",
        "input_field_reason": (
            "5x5 median of nonzero aligned depth returns, deprojected with "
            "rs2_deproject_pixel_to_point: the frozen extractor's "
            "--depth-window 5 default, the values the thesis pipeline uses "
            "(pick JSON model_landmarks_note)"),
        "xyz_px_m_equals_xyz_med5_m_for_all_8": same,
        "units": "metres (positions), radians and degrees (angles)",
        "coordinate_frame_input": pick.get("coordinate_frame"),
    }
    return med5, meta


# ---------------------------------------------------------------------------
# Root frame and Euler, with intermediates
# ---------------------------------------------------------------------------
def root_intermediates_a(p):
    """Replicates build_root_frame on {Camera'} points; compared to it."""
    r_raw = p[24] - p[23]
    r_norm = np.linalg.norm(r_raw)
    r = r_raw / r_norm
    s = p[12] - p[24]
    rxs = np.cross(r, s)
    rxs_norm = np.linalg.norm(rxs)
    f = rxs / rxs_norm
    u = np.cross(f, r)
    R = np.stack([r, u, f], axis=-1)
    R_frozen = build_root_frame(p[23], p[24], p[12])
    check("A: replicated R_root equals build_root_frame",
          np.max(np.abs(R - R_frozen)) <= TOL_EXACT,
          f"max abs diff {np.max(np.abs(R - R_frozen)):.3e}")
    d = {
        "hip_vector_r_raw_p24_minus_p23": r_raw, "hip_vector_norm": r_norm,
        "r_X_L24": r, "s_p12_minus_p24": s,
        "r_cross_s": rxs, "r_cross_s_norm": rxs_norm,
        "f_Z_L24": f, "u_Y_L24": u, "u_norm": np.linalg.norm(u),
        "r_dot_s": float(r @ s),
        "R_root_columns_r_u_f": R_frozen,
        "det_R_root": np.linalg.det(R_frozen),
    }
    return R_frozen, d


def root_intermediates_b(p):
    x_raw = p[23] - p[24]
    x_norm = np.linalg.norm(x_raw)
    x = x_raw / x_norm
    s = p[12] - p[24]
    xs = np.cross(x, s)
    xs_norm = np.linalg.norm(xs)
    z = xs / xs_norm
    y = np.cross(z, x)
    R = np.stack([x, y, z], axis=-1)
    d = {
        "hip_vector_x_raw_p23_minus_p24": x_raw, "hip_vector_norm": x_norm,
        "x_X_L24star": x, "s_p12_minus_p24": s,
        "x_cross_s": xs, "x_cross_s_norm": xs_norm,
        "z_Z_L24star": z, "y_Y_L24star": y, "y_norm": np.linalg.norm(y),
        "x_dot_s": float(x @ s),
        "R_root_columns_x_y_z": R,
        "det_R_root": np.linalg.det(R),
    }
    return R, d


def euler_intermediates(R, label):
    """The entries read by euler_unity_zxy and its asin/atan2 arguments."""
    m12_raw = R[1, 2]
    m12 = float(np.clip(m12_raw, -1.0, 1.0))
    lock = abs(m12) > 1.0 - 1e-8   # frozen threshold, root_frame.py
    x = -np.arcsin(m12)
    y = np.arctan2(R[0, 2], R[2, 2])
    z = np.arctan2(R[1, 0], R[1, 1])
    frozen = euler_unity_zxy(R)
    mine = np.degrees([x, y, z])
    if not lock:
        check(f"{label}: replicated Euler equals euler_unity_zxy",
              np.max(np.abs(mine - frozen)) <= TOL_EXACT,
              f"max abs diff {np.max(np.abs(mine - frozen)):.3e} deg")
    rec = recompose_zxy(frozen)
    err = np.max(np.abs(rec - R))
    d = {
        "decomposition": "R = Ry(y) Rx(x) Rz(z); x = asin(-m12), "
                         "y = atan2(m02, m22), z = atan2(m10, m11)",
        "m12": m12_raw, "m12_clipped": m12, "asin_argument_minus_m12": -m12,
        "m02": R[0, 2], "m22": R[2, 2], "m10": R[1, 0], "m11": R[1, 1],
        "atan2_y_arguments_m02_m22": [R[0, 2], R[2, 2]],
        "atan2_z_arguments_m10_m11": [R[1, 0], R[1, 1]],
        "gimbal_lock": bool(lock),
        "x": deg_rad(np.radians(frozen[0])),
        "y": deg_rad(np.radians(frozen[1])),
        "z": deg_rad(np.radians(frozen[2])),
        "euler_deg_x_y_z": frozen,
        "recompose_zxy": rec,
        "recompose_max_abs_error": err,
    }
    return frozen, d, err


# ---------------------------------------------------------------------------
# Arm solve, with intermediates (replicates solve_right_arm step by step)
# ---------------------------------------------------------------------------
def arm_chain(p_sh, p_el, p_wr, R_root, label):
    """Replicates shoulder.solve_right_shoulder + solve_right_arm exactly
    (same expressions, same order) and checks the result against the frozen
    solve_right_arm called with the same arguments."""
    p_sh, p_el, p_wr = (np.asarray(v, dtype=float) for v in (p_sh, p_el, p_wr))
    R_root = np.asarray(R_root, dtype=float)
    # Shoulder swing
    v_up = p_el - p_sh
    v_up_root = R_root.T @ v_up
    v_up_root_norm = np.linalg.norm(v_up_root)
    a = normalize(v_up_root)
    sz = float(np.clip(a[1], -1.0, 1.0))
    th_z = np.arcsin(sz)
    gimbal = 1.0 - abs(sz) < GIMBAL_EPS
    th_y = 0.0 if gimbal else np.arctan2(-a[2], a[0])
    # Twist
    v_fa = p_wr - p_el
    f = R_root.T @ v_fa
    f_after_ry = _ry(-th_y) @ f
    fp = _rz(-th_z) @ f_after_ry
    perp = np.hypot(fp[1], fp[2])
    twist_thr = TWIST_EPS * np.linalg.norm(f)
    twist_ok = bool(perp >= twist_thr)
    th_t = np.arctan2(-fp[1], fp[2]) if twist_ok else np.nan
    sh = np.degrees(np.array([th_y, th_z, th_t]))
    if not twist_ok:
        sh[2] = 0.0
    # Elbow (the frozen code converts to degrees and back; same here)
    yr, zr, tr = np.radians(sh)
    Ry, Rz, Rx = _ry(yr), _rz(zr), _rx(tr)
    R_sh = Ry @ Rz @ Rx
    R_arm = R_root @ R_sh
    g_raw = R_arm.T @ v_fa
    g = normalize(g_raw)
    ez = np.arcsin(np.clip(g[1], -1.0, 1.0))
    ey = np.arctan2(-g[2], g[0])
    elb = np.degrees(np.array([ey, ez]))

    sh_f, elb_f, ok_f = solve_right_arm(p_sh, p_el, p_wr, R_root)
    diff = max(np.nanmax(np.abs(sh - sh_f)), np.max(np.abs(elb - elb_f)))
    check(f"{label}: replicated arm angles equal solve_right_arm",
          diff <= TOL_EXACT and ok_f == twist_ok,
          f"max abs diff {diff:.3e} deg")
    d = {
        "solver_inputs": {"p_sh": p_sh, "p_el": p_el, "p_wr": p_wr,
                          "R_root": R_root},
        "upper_arm_v_in_solver_root_R_T_v": v_up_root,
        "upper_arm_v_in_solver_root_norm": v_up_root_norm,
        "a_unit": a,
        "sz_a_y": sz,
        "th_z_asin_argument": sz,
        "th_y_atan2_arguments_minus_a_z_a_x": [-a[2], a[0]],
        "gimbal": bool(gimbal),
        "th_y": deg_rad(th_y), "th_z": deg_rad(th_z),
        "forearm_f_in_solver_root": f,
        "f_after_Ry_minus_th_y": f_after_ry,
        "f_prime_unswung_Rz_minus_th_z_Ry_minus_th_y_f": fp,
        "twist_atan2_arguments_minus_fp_y_fp_z": [-fp[1], fp[2]],
        "perp_hypot_fp_y_fp_z": perp,
        "twist_threshold_TWIST_EPS_times_norm_f": twist_thr,
        "twist_ok": twist_ok,
        "th_t": deg_rad(np.radians(sh[2])),
        "Ry_th_y": Ry, "Rz_th_z": Rz, "Rx_th_t": Rx,
        "R_sh_Ry_Rz_Rx": R_sh,
        "R_arm_R_root_R_sh": R_arm,
        "g_raw_R_arm_T_forearm": g_raw,
        "g_unit": g,
        "ez_asin_argument_g_y": float(np.clip(g[1], -1.0, 1.0)),
        "ey_atan2_arguments_minus_g_z_g_x": [-g[2], g[0]],
        "ey": deg_rad(ey), "ez": deg_rad(ez),
        "shoulder_deg_th_y_th_z_th_t": sh_f,
        "elbow_deg_ey_ez": elb_f,
    }
    # Shoulder and elbow composed, R_sh Ry(ey) Rz(ez): maps the rest
    # direction onto the forearm direction (forward check).
    R_sh_elb = R_sh @ _ry(np.radians(elb_f[0])) @ _rz(np.radians(elb_f[1]))
    d["R_sh_R_elbow_Ry_ey_Rz_ez"] = R_sh_elb
    return sh_f, elb_f, R_sh, R_sh_elb, d


def forward_check(label, R_world, rest, measured_vec, what, sink=CHECKS):
    """Unit dot product of the reconstructed and the measured direction."""
    recon = R_world @ rest
    meas = normalize(np.asarray(measured_vec, dtype=float))
    dot = float(recon @ meas)
    check(f"{label}: forward {what} direction reproduced (dot >= 1 - 1e-9)",
          dot >= 1.0 - TOL_BRIEF, f"dot = {dot:.15f}", sink)
    return {"rest": rest, "reconstructed_unit": recon, "measured_unit": meas,
            "dot": dot}


# ---------------------------------------------------------------------------
# Method A
# ---------------------------------------------------------------------------
def method_a(cam):
    p = {k: unity_from_sensor(cam[k]) for k in LANDMARK_IDS}
    R, root = root_intermediates_a(p)
    det = np.linalg.det(R)
    check("A: det(R_root_A) = +1", abs(det - 1.0) <= TOL_EXACT,
          f"det = {det:.15f}")
    euler, eul, rec_err = euler_intermediates(R, "A")
    check("A: recompose_zxy(root Euler A) reproduces R_root_A",
          rec_err <= TOL_BRIEF, f"max abs error {rec_err:.3e}")

    # Right arm: the frozen call, solve_right_arm(p12', p14', p16', R_A).
    sh_r, el_r, R_sh_r, R_chain_r, dr = arm_chain(
        p[12], p[14], p[16], R, "A right arm")
    dr["upper_arm_v_Camera_prime_p14_minus_p12"] = p[14] - p[12]
    dr["forearm_v_Camera_prime_p16_minus_p14"] = p[16] - p[14]
    dr["rest_direction_local"] = "+x"
    dr["forward_upper"] = forward_check(
        "A right arm", R @ R_sh_r, X_HAT, p[14] - p[12], "upper-arm")
    dr["forward_forearm"] = forward_check(
        "A right arm", R @ R_chain_r, X_HAT, p[16] - p[14], "forearm")

    # Left arm: the frozen call, solve_left_arm(p11', p13', p15', R_A),
    # which mirrors the root-basis vectors and calls solve_right_arm.
    u_root = R.T @ (p[13] - p[11])
    f_root = R.T @ (p[15] - p[13])
    u = MIRROR * u_root
    f = MIRROR * f_root
    sh_l, el_l, R_sh_l, R_chain_l, dl = arm_chain(
        np.zeros(3), u, u + f, np.eye(3), "A left arm (mirrored)")
    sh_lf, el_lf, _ = solve_left_arm(p[11], p[13], p[15], R)
    diff = max(np.max(np.abs(sh_l - sh_lf)), np.max(np.abs(el_l - el_lf)))
    check("A left arm: replicated angles equal solve_left_arm",
          diff <= TOL_EXACT, f"max abs diff {diff:.3e} deg")
    dl = {
        "upper_arm_v_Camera_prime_p13_minus_p11": p[13] - p[11],
        "forearm_v_Camera_prime_p15_minus_p13": p[15] - p[13],
        "upper_arm_in_root_R_T_v": u_root,
        "forearm_in_root_R_T_v": f_root,
        "mirror_M": M,
        "upper_arm_mirrored_u_M_R_T_v": u,
        "forearm_mirrored_f_M_R_T_v": f,
        "rest_direction_local": "-x (mirrored to +x for the solve)",
        "mirrored_solve": dl,
    }
    # World reconstruction of the left arm: R_A M R_sh M, rest -x.
    dl["forward_upper"] = forward_check(
        "A left arm", R @ M @ R_sh_l @ M, -X_HAT, p[13] - p[11], "upper-arm")
    dl["forward_forearm"] = forward_check(
        "A left arm", R @ M @ R_chain_l @ M, -X_HAT, p[15] - p[13], "forearm")

    angles = np.concatenate([euler, sh_r, el_r, sh_lf, el_lf])
    out = {
        "method": "A",
        "description": (
            "Frozen thesis code: points flipped into the left-handed "
            "{Camera'} by F = diag(1,-1,1), root x = L23 -> L24 (subject's "
            "right); v1/kinematics root_frame.py and shoulder.py imported"),
        "points_Camera": {f"L{k}": cam[k] for k in LANDMARK_IDS},
        "points_Camera_prime_flipped": {f"L{k}": p[k] for k in LANDMARK_IDS},
        "F": F,
        "root_frame": root,
        "root_euler": eul,
        "right_arm": dr,
        "left_arm": dl,
        "angles13_names": list(ANGLE_NAMES),
        "angles13_deg": angles,
        "angles13_rad": np.radians(angles),
    }
    return out, R, angles


# ---------------------------------------------------------------------------
# Method B
# ---------------------------------------------------------------------------
def method_b(cam):
    p = cam
    R, root = root_intermediates_b(p)
    det = np.linalg.det(R)
    check("B: det(R_root_B) = +1", abs(det - 1.0) <= TOL_EXACT,
          f"det = {det:.15f}")
    euler, eul, rec_err = euler_intermediates(R, "B")
    eul["reading_note"] = (
        "Same ZXY formulas as Method A applied to R_B, a rotation of the "
        "right-handed {Camera} (x right, y DOWN, z forward); the angles are "
        "relative to {Camera} axes, not to the y-up {Camera'}, and are not "
        "Unity Euler angles")
    check("B: recompose_zxy(root Euler B) reproduces R_root_B",
          rec_err <= TOL_BRIEF, f"max abs error {rec_err:.3e}")

    # Right arm: rest = local -x; mirror x in the root basis, then the
    # frozen right-arm solve with an identity root (J-012).
    u_root = R.T @ (p[14] - p[12])
    f_root = R.T @ (p[16] - p[14])
    u = MIRROR * u_root
    f = MIRROR * f_root
    sh_r, el_r, R_sh_r, R_chain_r, dr_inner = arm_chain(
        np.zeros(3), u, u + f, np.eye(3), "B right arm (mirrored)")
    dr = {
        "upper_arm_v_Camera_p14_minus_p12": p[14] - p[12],
        "forearm_v_Camera_p16_minus_p14": p[16] - p[14],
        "upper_arm_in_root_R_T_v": u_root,
        "forearm_in_root_R_T_v": f_root,
        "mirror_M": M,
        "upper_arm_mirrored_u_M_R_T_v": u,
        "forearm_mirrored_f_M_R_T_v": f,
        "rest_direction_local": "-x (mirrored to +x for the solve, J-012)",
        "mirrored_solve": dr_inner,
    }
    dr["forward_upper"] = forward_check(
        "B right arm", R @ M @ R_sh_r @ M, -X_HAT, p[14] - p[12], "upper-arm")
    dr["forward_forearm"] = forward_check(
        "B right arm", R @ M @ R_chain_r @ M, -X_HAT, p[16] - p[14],
        "forearm")

    # Left arm: rest = local +x; the frozen right-arm formulas directly.
    sh_l, el_l, R_sh_l, R_chain_l, dl = arm_chain(
        p[11], p[13], p[15], R, "B left arm (direct)")
    dl["upper_arm_v_Camera_p13_minus_p11"] = p[13] - p[11]
    dl["forearm_v_Camera_p15_minus_p13"] = p[15] - p[13]
    dl["rest_direction_local"] = "+x (no mirror)"
    dl["forward_upper"] = forward_check(
        "B left arm", R @ R_sh_l, X_HAT, p[13] - p[11], "upper-arm")
    dl["forward_forearm"] = forward_check(
        "B left arm", R @ R_chain_l, X_HAT, p[15] - p[13], "forearm")

    angles = np.concatenate([euler, sh_r, el_r, sh_l, el_l])
    out = {
        "method": "B",
        "description": (
            "Right-handed {Camera}, no flip (J-008); root x = L24 -> L23 "
            "(subject's left, J-002); R_B = [x | y | z]; arms: right arm "
            "mirrored to rest +x, left arm direct (J-012)"),
        "points_Camera": {f"L{k}": p[k] for k in LANDMARK_IDS},
        "root_frame": root,
        "root_euler": eul,
        "right_arm": dr,
        "left_arm": dl,
        "angles13_names": list(ANGLE_NAMES),
        "angles13_deg": angles,
        "angles13_rad": np.radians(angles),
    }
    return out, R, angles


# ---------------------------------------------------------------------------
# Method B native (J-013): right arm rest -x without mirror, left arm rest +x
# ---------------------------------------------------------------------------
def native_arm(p_sh, p_el, p_wr, R_root, side):
    """Native right-handed swing-twist in the root R_root. side 'right':
    rest -x, twist R_{-x}(th_t) = Rx(-th_t); side 'left': rest +x, twist
    Rx(th_t) (the thesis formulas). Every intermediate is returned."""
    right = side == "right"
    sgn = -1.0 if right else 1.0            # rest direction = sgn * x_hat
    rest = sgn * X_HAT
    p_sh, p_el, p_wr = (np.asarray(v, dtype=float) for v in (p_sh, p_el, p_wr))
    R_root = np.asarray(R_root, dtype=float)
    # Swing: a = Ry Rz (sgn x_hat) = sgn (cz cy, sz, -cz sy)
    v_up = p_el - p_sh
    v_up_root = R_root.T @ v_up
    a = normalize(v_up_root)
    ay = float(np.clip(a[1], -1.0, 1.0))
    th_z = sgn * np.arcsin(ay)              # right: -asin(a_y); left: asin(a_y)
    gimbal = 1.0 - abs(ay) < GIMBAL_EPS
    if right:
        y_args = [a[2], -a[0]]              # atan2(a_z, -a_x)
    else:
        y_args = [-a[2], a[0]]              # atan2(-a_z, a_x)
    th_y = 0.0 if gimbal else np.arctan2(*y_args)
    # Twist: f' = Rz(-th_z) Ry(-th_y) f = R_tw(th_t) (f_par, 0, |f_perp|)
    v_fa = p_wr - p_el
    f = R_root.T @ v_fa
    f_after_ry = _ry(-th_y) @ f
    fp = _rz(-th_z) @ f_after_ry
    perp = np.hypot(fp[1], fp[2])
    twist_thr = TWIST_EPS * np.linalg.norm(f)
    twist_ok = bool(perp >= twist_thr)
    if right:
        t_args = [fp[1], fp[2]]             # Rx(-th_t) e_z = (0, s, c)
    else:
        t_args = [-fp[1], fp[2]]            # Rx(th_t) e_z = (0, -s, c)
    th_t = np.arctan2(*t_args) if twist_ok else 0.0
    rx_arg = sgn * th_t                     # R_tw = Rx(rx_arg)
    Ry, Rz, R_tw = _ry(th_y), _rz(th_z), _rx(rx_arg)
    R_sh = Ry @ Rz @ R_tw
    R_arm = R_root @ R_sh
    # Zero-twist convention: un-twisting f' must leave its perpendicular
    # part on local +z (y component 0, z component >= 0).
    f_untwisted = R_tw.T @ fp
    check(f"B-native {side} arm: un-twisted forearm perpendicular part on "
          f"local +z (|y| <= 1e-12 |f|, z >= 0)",
          (not twist_ok) or (abs(f_untwisted[1]) <= TOL_EXACT * np.linalg.norm(f)
                             and f_untwisted[2] >= 0.0),
          f"f_untwisted = ({f_untwisted[0]:.6e}, {f_untwisted[1]:.3e}, "
          f"{f_untwisted[2]:.6e})", NATIVE_CHECKS)
    # Elbow: g = Ry(ey) Rz(ez) (sgn x_hat) in the arm frame
    g_raw = R_arm.T @ v_fa
    g = normalize(g_raw)
    gy = float(np.clip(g[1], -1.0, 1.0))
    ez = sgn * np.arcsin(gy)                # right: -asin(g_y); left: asin(g_y)
    e_args = [g[2], -g[0]] if right else [-g[2], g[0]]
    ey = np.arctan2(*e_args)
    R_elb = _ry(ey) @ _rz(ez)
    sh = np.degrees(np.array([th_y, th_z, th_t]))
    elb = np.degrees(np.array([ey, ez]))
    fwd_up = forward_check(f"B-native {side} arm", R_root @ R_sh, rest, v_up,
                           "upper-arm", NATIVE_CHECKS)
    fwd_fa = forward_check(f"B-native {side} arm", R_arm @ R_elb, rest, v_fa,
                           "forearm", NATIVE_CHECKS)
    if right:
        forms = {
            "a": "Ry(th_y) Rz(th_z) (-1,0,0) = (-cz cy, -sz, cz sy)",
            "th_z": "-asin(a_y)", "th_y": "atan2(a_z, -a_x)",
            "twist": "R_tw = R_{-x}(th_t) = Rx(-th_t); f' = Rx(-th_t) "
                     "(f_par, 0, |f_perp|) -> (f'_y, f'_z) = |f_perp| "
                     "(sin th_t, cos th_t); th_t = atan2(f'_y, f'_z)",
            "elbow": "g = Ry(ey) Rz(ez) (-1,0,0); ez = -asin(g_y), "
                     "ey = atan2(g_z, -g_x)",
        }
    else:
        forms = {
            "a": "Ry(th_y) Rz(th_z) (1,0,0) = (cz cy, sz, -cz sy)",
            "th_z": "asin(a_y)", "th_y": "atan2(-a_z, a_x)",
            "twist": "R_tw = Rx(th_t); (f'_y, f'_z) = |f_perp| "
                     "(-sin th_t, cos th_t); th_t = atan2(-f'_y, f'_z)",
            "elbow": "g = Ry(ey) Rz(ez) (1,0,0); ez = asin(g_y), "
                     "ey = atan2(-g_z, g_x)",
        }
    d = {
        "side": side,
        "rest_direction_local": "-x" if right else "+x",
        "closed_forms": forms,
        "solver_inputs": {"p_sh": p_sh, "p_el": p_el, "p_wr": p_wr,
                          "R_root": R_root},
        "upper_arm_v_Camera": v_up,
        "upper_arm_v_in_root_R_T_v": v_up_root,
        "upper_arm_v_in_root_norm": np.linalg.norm(v_up_root),
        "a_unit": a,
        "th_z_asin_argument_a_y": ay,
        "th_z_sign_factor": sgn,
        ("th_y_atan2_arguments_a_z_minus_a_x" if right
         else "th_y_atan2_arguments_minus_a_z_a_x"): y_args,
        "gimbal": bool(gimbal),
        "th_y": deg_rad(th_y), "th_z": deg_rad(th_z),
        "forearm_v_Camera": v_fa,
        "forearm_f_in_root": f,
        "f_after_Ry_minus_th_y": f_after_ry,
        "f_prime_unswung_Rz_minus_th_z_Ry_minus_th_y_f": fp,
        ("twist_atan2_arguments_fp_y_fp_z" if right
         else "twist_atan2_arguments_minus_fp_y_fp_z"): t_args,
        "perp_hypot_fp_y_fp_z": perp,
        "twist_threshold_TWIST_EPS_times_norm_f": twist_thr,
        "twist_ok": twist_ok,
        "th_t": deg_rad(th_t),
        "Rx_argument_of_R_tw": deg_rad(rx_arg),
        "f_untwisted_R_tw_T_f_prime": f_untwisted,
        "Ry_th_y": Ry, "Rz_th_z": Rz, "R_tw": R_tw,
        "R_sh_Ry_Rz_R_tw": R_sh,
        "R_arm_R_root_R_sh": R_arm,
        "g_raw_R_arm_T_forearm": g_raw,
        "g_unit": g,
        "ez_asin_argument_g_y": gy,
        ("ey_atan2_arguments_g_z_minus_g_x" if right
         else "ey_atan2_arguments_minus_g_z_g_x"): e_args,
        "ey": deg_rad(ey), "ez": deg_rad(ez),
        "R_elbow_Ry_ey_Rz_ez": R_elb,
        "R_arm_R_elbow": R_arm @ R_elb,
        "shoulder_deg_th_y_th_z_th_t": sh,
        "elbow_deg_ey_ez": elb,
        "forward_upper": fwd_up,
        "forward_forearm": fwd_fa,
    }
    return sh, elb, R_arm, R_elb, d


def classify_native(a, b):
    if abs(a) <= TOL_BRIEF and abs(b) <= TOL_BRIEF:
        return "zero (same and sign)"
    return classify(a, b)


def method_b_native(cam, out_a, R_A, out_b, R_B, ang_a, ang_b):
    p = cam
    sh_r, el_r, Rarm_r, Relb_r, dr = native_arm(
        p[12], p[14], p[16], R_B, "right")
    sh_l, el_l, Rarm_l, Relb_l, dl = native_arm(
        p[11], p[13], p[15], R_B, "left")

    # Mirror identity (the J-012 equivalence, now a check, not a step):
    # right arm  R_arm,Bn = F R_arm,A M  and  R_B M R_sh,B(mirrored) M,
    # left arm   R_arm,Bn = R_arm,B(direct).
    ida = {}
    A_r = out_a["right_arm"]
    Rarm_A_r = np.asarray(A_r["R_arm_R_root_R_sh"])
    Rchain_A_r = R_A @ np.asarray(A_r["R_sh_R_elbow_Ry_ey_Rz_ez"])
    Rsh_Bm_r = np.asarray(out_b["right_arm"]["mirrored_solve"]["R_sh_Ry_Rz_Rx"])
    Rarm_Bd_l = np.asarray(out_b["left_arm"]["R_arm_R_root_R_sh"])
    pairs = [
        ("right: R_arm_Bnative = F R_arm_A M", Rarm_r, F @ Rarm_A_r @ M),
        ("right: R_arm_Bnative R_elb_Bnative = F R_arm_A R_elb_A M",
         Rarm_r @ Relb_r, F @ Rchain_A_r @ M),
        ("right: R_arm_Bnative = R_B M R_sh_B(mirrored, J-012) M",
         Rarm_r, R_B @ M @ Rsh_Bm_r @ M),
        ("left: R_arm_Bnative = R_arm_B(direct)", Rarm_l, Rarm_Bd_l),
    ]
    for name, lhs, rhs in pairs:
        err = float(np.max(np.abs(lhs - rhs)))
        check(f"B-native mirror identity, {name}", err <= TOL_EXACT,
              f"max abs diff {err:.3e}", NATIVE_CHECKS)
        ida[name] = {"lhs": lhs, "rhs": rhs, "max_abs_diff": err}

    euler = ang_b[:3]
    angles = np.concatenate([euler, sh_r, el_r, sh_l, el_l])
    rows = []
    for i, n in enumerate(ANGLE_NAMES):
        rows.append({"name": n, "A_deg": ang_a[i], "Bnative_deg": angles[i],
                     "Bnative_minus_A_deg": angles[i] - ang_a[i],
                     "Bnative_plus_A_deg": angles[i] + ang_a[i],
                     "relation": classify_native(ang_a[i], angles[i])})
    # The derivation (J-013) predicts: right arm all five angles change
    # sign, left arm all five equal. Tested here, not assumed.
    pred = {n: ("sign" if n.startswith("R_") else "same")
            for n in ANGLE_NAMES[3:]}
    ok = all(r["relation"] in (pred[r["name"]], "zero (same and sign)")
             for r in rows[3:])
    check("B-native vs A relation table matches the derivation "
          "(right arm: sign on all five; left arm: same on all five)",
          ok, "; ".join(f"{r['name']} {r['relation']}" for r in rows[3:]),
          NATIVE_CHECKS)
    out = {
        "method": "B-native",
        "description": (
            "Right-handed {Camera}, no flip (J-008); root R_B as Method B "
            "(J-002); arms solved natively in {L24*} without mirror (J-013): "
            "right arm rest -x, twist right-handed about -x (Rx(-th_t)); "
            "left arm rest +x, thesis formulas"),
        "points_Camera": {f"L{k}": p[k] for k in LANDMARK_IDS},
        "root_frame": out_b["root_frame"],
        "root_euler": out_b["root_euler"],
        "right_arm": dr,
        "left_arm": dl,
        "mirror_identity": ida,
        "angles13_names": list(ANGLE_NAMES),
        "angles13_deg": angles,
        "angles13_rad": np.radians(angles),
        "comparison_A_Bnative": {"table": rows,
                                 "derivation_prediction": pred},
    }
    return out, angles, rows


def classify(a, b):
    if abs(a - b) <= TOL_BRIEF:
        return "same"
    if abs(a + b) <= TOL_BRIEF:
        return "sign"
    if abs(wrap_deg(180.0 - a) - wrap_deg(b)) <= TOL_BRIEF:
        return "B = wrap(180 - A)"
    return "other"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pick", default=str(DEFAULT_PICK))
    ap.add_argument("--native-b", action="store_true",
                    help="write only angles_method_b_native.json and print "
                         "only the native Method B section (J-013)")
    args = ap.parse_args()
    t0 = time.perf_counter()

    cam, meta = load_points(args.pick)
    out_a, R_A, ang_a = method_a(cam)
    out_b, R_B, ang_b = method_b(cam)

    rel = R_B.T @ F @ R_A
    rel_err = np.max(np.abs(rel - M))
    check("R_B^T F R_A = diag(-1, 1, 1)", rel_err <= TOL_EXACT,
          f"max abs error {rel_err:.3e}")

    rows = []
    for i, n in enumerate(ANGLE_NAMES):
        rows.append({"name": n, "A_deg": ang_a[i], "B_deg": ang_b[i],
                     "B_minus_A_deg": ang_b[i] - ang_a[i],
                     "relation": classify(ang_a[i], ang_b[i])})
    comparison = {"R_B_T_F_R_A": rel, "R_B_T_F_R_A_max_abs_error_vs_M": rel_err,
                  "table": rows}

    run = {"script": "journal/scripts/compute_angles.py",
           "tolerances": {"TOL_BRIEF": TOL_BRIEF, "TOL_EXACT": TOL_EXACT},
           "frozen_constants": {"GIMBAL_EPS": GIMBAL_EPS,
                                "TWIST_EPS": TWIST_EPS,
                                "euler_lock_threshold": 1e-8}}
    out_n, ang_n, rows_n = method_b_native(
        cam, out_a, R_A, out_b, R_B, ang_a, ang_b)

    for out in (out_a, out_b):
        out["meta"] = meta
        out["run"] = run
        out["comparison_A_B"] = comparison
        out["checks"] = CHECKS
    out_n["meta"] = meta
    out_n["run"] = run
    out_n["checks"] = NATIVE_CHECKS
    out_n["checks_A_B_of_the_same_run"] = CHECKS
    if not args.native_b:
        OUT_A.write_text(json.dumps(sig(out_a), indent=1) + "\n")
        OUT_B.write_text(json.dumps(sig(out_b), indent=1) + "\n")
    OUT_BN.write_text(json.dumps(sig(out_n), indent=1) + "\n")

    print(f"pick: {meta['pick_json']}  bag {meta['bag']}  "
          f"frame {meta['frame_index']}")
    print(f"input: {meta['input_field']} (5x5 median deprojection); "
          f"xyz_px_m equals it for all 8: "
          f"{meta['xyz_px_m_equals_xyz_med5_m_for_all_8']}")
    n_fail = 0
    if not args.native_b:
        print()
        print(f"{'angle':<11} {'A (deg)':>12} {'B (deg)':>12} "
              f"{'B - A':>12}  relation")
        for r in rows:
            print(f"{r['name']:<11} {r['A_deg']:12.6f} {r['B_deg']:12.6f} "
                  f"{r['B_minus_A_deg']:12.6f}  {r['relation']}")
        sign_only = [r["name"] for r in rows if r["relation"] == "sign"]
        arm_diff = float(np.max(np.abs(ang_b[3:] - ang_a[3:])))
        comparison["arm_angles_max_abs_B_minus_A_deg"] = arm_diff
        print()
        print(f"max |B - A| over the 10 arm angles: {arm_diff:.3e} deg")
        print("differ by sign only: " + (", ".join(sign_only) or "none"))
        print("other relations: " + (", ".join(
            f"{r['name']} ({r['relation']})" for r in rows
            if r["relation"] not in ("same", "sign")) or "none"))
        print()
        for c in CHECKS:
            print(f"{'PASS' if c['pass'] else 'FAIL'}  {c['name']}  "
                  f"[{c['detail']}]")
        n_fail = sum(not c["pass"] for c in CHECKS)
        print()
        print(f"{len(CHECKS) - n_fail} PASS / {n_fail} FAIL; wrote "
              f"{OUT_A.relative_to(REPO)} and {OUT_B.relative_to(REPO)}")

    print()
    print("Method B native (J-013): arm angles against Method A")
    print(f"{'angle':<11} {'A (deg)':>14} {'B-native':>14} "
          f"{'Bn - A':>14} {'Bn + A':>14}  relation")
    for r in rows_n:
        print(f"{r['name']:<11} {r['A_deg']:14.9f} {r['Bnative_deg']:14.9f} "
              f"{r['Bnative_minus_A_deg']:14.9f} "
              f"{r['Bnative_plus_A_deg']:14.9f}  {r['relation']}")
    print()
    for side in ("right_arm", "left_arm"):
        d = out_n[side]
        print(f"{side}: rest {d['rest_direction_local']}; "
              f"a = {np.array2string(d['a_unit'], precision=9)}; "
              f"f' = {np.array2string(d['f_prime_unswung_Rz_minus_th_z_Ry_minus_th_y_f'], precision=9)}; "
              f"g = {np.array2string(d['g_unit'], precision=9)}; "
              f"Rx argument of R_tw = {d['Rx_argument_of_R_tw']['deg']:.9f} deg")
    print()
    for c in NATIVE_CHECKS:
        print(f"{'PASS' if c['pass'] else 'FAIL'}  {c['name']}  [{c['detail']}]")
    n_fail_n = sum(not c["pass"] for c in NATIVE_CHECKS)
    print()
    print(f"native: {len(NATIVE_CHECKS) - n_fail_n} PASS / {n_fail_n} FAIL; "
          f"wrote {OUT_BN.relative_to(REPO)}; "
          f"{time.perf_counter() - t0:.3f} s")
    return 1 if (n_fail or n_fail_n) else 0


if __name__ == "__main__":
    sys.exit(main())

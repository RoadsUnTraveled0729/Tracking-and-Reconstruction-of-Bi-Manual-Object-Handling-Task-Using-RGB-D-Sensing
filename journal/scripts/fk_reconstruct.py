"""Milestone M5 of the journal track (J-009, J-015): forward kinematics
from the computed joint angles of both methods, rebuilding the 8-landmark
skeleton (L11-L16, L23, L24) of the worked-example frame, comparing it
with the measured landmarks, and drawing it on the colour frame.

Inputs (defaults):
    journal/data/perfect_frame.json           measured {Camera} points
        (model_landmarks[k].xyz_med5_m), colour intrinsics, RGB frame
        journal/figures/perfect_frame_rgb.png
    journal/data/angles_method_a.json         13 angles, Method A
    journal/data/angles_method_b_native.json  13 angles, Method B native

Chain parameters (held constant by a retarget; all measured on the same
frame, J-015):
    origin       P24: {Camera'}P24 = F {Camera}P24 (A), {Camera}P24 (B)
    root R       recompose_zxy(root Euler x, y, z) (frozen, R = Ry Rx Rz);
                 A in {Camera'}, B in {Camera}
    link offsets {L24}P_kORG = R_meas^T (P_k - P24), k = 23, 12, 11, with
                 R_meas the root built from the measured points
                 (build_root_frame for A, the J-002 construction for B)
    lengths      L_ua = |P14 - P12|, |P13 - P11|; L_fa = |P16 - P14|,
                 |P15 - P13| (F is an isometry, so A and B share them)
    rest         A: right +x; left -x through the frozen mirror
                 M = diag(-1, 1, 1): left local rotation M R M.
                 B native (J-013): right -x, left +x, no mirror.

Homogeneous chain, thesis eqs. (3.2), (3.5), (3.6), right arm of Method A:
    T(Camera'->L24) = [R_root | P24]        T(L24->L12) = [I | o_12]
    T(L12->L14)     = [R_sh  | L_ua R_sh e] T(L14->L16) = [I | L_fa R_elb e]
    P16 = T(Camera'->L24) T(L24->L12) T(L12->L14) (L_fa R_elb e, 1)^T
with e = +x, R_sh = Ry(t_y) Rz(t_z) Rx(t_t), R_elb = Ry(e_y) Rz(e_z).
Left arm of Method A: R_sh -> M R_sh M, R_elb -> M R_elb M, e = -x
(equivalently R_root M R_sh R_elb (+x), the inverse of solve_left_arm).
Method A is then un-flipped, {Camera}P = F {Camera'}P.
Method B native: R_root = R_B, right arm R_sh = Ry Rz Rx(-t_t), e = -x;
left arm R_sh = Ry Rz Rx(t_t), e = +x; no flip.

Projection (pinhole, distortion coefficients all 0 in the JSON):
    u = fx x / z + ppx,  v = fy y / z + ppy.

Sensitivity: each of the 13 angles of each method is perturbed by +1 deg
on its own, and the displacement magnitude of every landmark is reported.
A single-angle perturbation rotates the downstream points about a fixed
line by +-1 deg, and the A and B axes are the same physical line (J-015),
so the two 13 x 8 magnitude tables agree landmark by landmark although
the B-native step corresponds to -1 deg in A on the sign-flipped angles.

Tolerances (J-015):
    TOL_3D = 1e-9 m and TOL_PX = 1e-6 px: the M5 brief (float64 round-off
        plus the 12-significant-digit rounding of the angle JSONs).
    TOL_SENS = 1e-9 m for the A-versus-B sensitivity magnitudes, the same
        value as TOL_3D (worker's choice, J-015).
    TOL_EXACT = 1e-12 for identities that hold exactly in real arithmetic
        (as compute_angles.py).
    STEP_DEG = 1.0: the brief's sensitivity step.

Run (about 1 s):
    /home/luo/anaconda3/bin/python journal/scripts/fk_reconstruct.py
Outputs: journal/data/fk_reconstruction.json and
journal/figures/fk_reconstruction.png. Exit status 1 if any check fails.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "journal" / "data"
FIGS = REPO / "journal" / "figures"
DEFAULT_PICK = DATA / "perfect_frame.json"
DEFAULT_A = DATA / "angles_method_a.json"
DEFAULT_BN = DATA / "angles_method_b_native.json"
DEFAULT_RGB = FIGS / "perfect_frame_rgb.png"
OUT_JSON = DATA / "fk_reconstruction.json"
OUT_PNG = FIGS / "fk_reconstruction.png"

# v1 is frozen: import only; do not write bytecode into v1/kinematics.
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO / "v1" / "kinematics"))
sys.path.insert(0, str(REPO / "journal" / "scripts"))
from root_frame import (  # noqa: E402
    SENSOR_TO_UNITY, build_root_frame, normalize, recompose_zxy)
from shoulder import MIRROR, _rx, _ry, _rz  # noqa: E402

TOL_3D = 1e-9
TOL_PX = 1e-6
TOL_SENS = 1e-9
TOL_EXACT = 1e-12
STEP_DEG = 1.0

F = np.diag(SENSOR_TO_UNITY)   # {Camera} <-> {Camera'}, diag(1, -1, 1)
M = np.diag(MIRROR)            # sagittal mirror, diag(-1, 1, 1)
X_HAT = np.array([1.0, 0.0, 0.0])
LANDMARK_IDS = (11, 12, 13, 14, 15, 16, 23, 24)
CONNECTIONS = [(11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
               (11, 23), (12, 24), (23, 24)]   # select_perfect_frame.py
ANGLE_NAMES = (
    "root_x", "root_y", "root_z",
    "R_sh_th_y", "R_sh_th_z", "R_sh_th_t", "R_elb_ey", "R_elb_ez",
    "L_sh_th_y", "L_sh_th_z", "L_sh_th_t", "L_elb_ey", "L_elb_ez",
)

CHECKS = []


def check(name, ok, detail):
    CHECKS.append({"name": name, "pass": bool(ok), "detail": detail})


def plain(obj):
    """numpy / nested containers -> JSON-able Python objects."""
    if isinstance(obj, dict):
        return {str(k): plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [plain(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return plain(obj.tolist())
    if isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    if isinstance(obj, (int, np.integer)):
        return int(obj)
    if isinstance(obj, (float, np.floating)):
        return float(obj)
    return obj


def hom(R, p):
    """3x3 rotation and 3-vector -> 4x4 homogeneous transformation (3.2)."""
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = p
    return T


def apply(T, p):
    return (T @ np.append(p, 1.0))[:3]


# ---------------------------------------------------------------------------
# Chain parameters
# ---------------------------------------------------------------------------
def root_b_measured(p):
    """J-002 Method B root from measured {Camera} points, columns [x|y|z]."""
    x = normalize(p[23] - p[24])
    z = normalize(np.cross(x, p[12] - p[24]))
    y = np.cross(z, x)
    return np.stack([x, y, z], axis=-1)


def chain_params(cam, method):
    """Constant link parameters of one method, measured on the frame."""
    if method == "A":
        p = {k: F @ cam[k] for k in LANDMARK_IDS}       # {Camera'}
        R_meas = build_root_frame(p[23], p[24], p[12])
        frame = "Camera'"
    else:
        p = dict(cam)
        R_meas = root_b_measured(p)
        frame = "Camera"
    offs = {k: R_meas.T @ (p[k] - p[24]) for k in (23, 12, 11)}
    return {
        "frame": frame,
        "origin_P24": p[24],
        "R_root_measured": R_meas,
        "offset_L24_P_L23ORG": offs[23],
        "offset_L24_P_L12ORG": offs[12],
        "offset_L24_P_L11ORG": offs[11],
        "L_upper_right_P14_P12": float(np.linalg.norm(p[14] - p[12])),
        "L_fore_right_P16_P14": float(np.linalg.norm(p[16] - p[14])),
        "L_upper_left_P13_P11": float(np.linalg.norm(p[13] - p[11])),
        "L_fore_left_P15_P13": float(np.linalg.norm(p[15] - p[13])),
        "rest_right": "+x" if method == "A" else "-x",
        "rest_left": ("-x via the frozen mirror (local rotations M R M)"
                      if method == "A" else "+x"),
    }


# ---------------------------------------------------------------------------
# Forward kinematics (homogeneous chain, thesis eqs. 3.2, 3.5, 3.6)
# ---------------------------------------------------------------------------
def arm_local(ang_deg, side, method):
    """Local shoulder rotation, elbow rotation and rest direction e such that
    upper arm = R_sh e and forearm = R_sh R_elb e in the root basis."""
    ty, tz, tt, ey, ez = np.radians(ang_deg)
    if method == "A":
        R_sh = _ry(ty) @ _rz(tz) @ _rx(tt)
        R_elb = _ry(ey) @ _rz(ez)
        if side == "right":
            return R_sh, R_elb, X_HAT
        return M @ R_sh @ M, M @ R_elb @ M, -X_HAT     # inverse of the mirror
    # Method B native (J-013)
    if side == "right":
        return _ry(ty) @ _rz(tz) @ _rx(-tt), _ry(ey) @ _rz(ez), -X_HAT
    return _ry(ty) @ _rz(tz) @ _rx(tt), _ry(ey) @ _rz(ez), X_HAT


def fk(prm, ang_deg, method):
    """13 angles (deg) -> 8 points in {Camera}, plus the chain transforms."""
    ang = np.asarray(ang_deg, dtype=float)
    R_root = recompose_zxy(ang[:3])
    T_root = hom(R_root, prm["origin_P24"])              # {Camera'} or {Camera}
    out = {24: apply(T_root, np.zeros(3)),
           23: apply(T_root, prm["offset_L24_P_L23ORG"])}
    tr = {"T_frame_L24": T_root}
    for side, sh_id, el_id, wr_id, idx, Lua, Lfa in (
            ("right", 12, 14, 16, slice(3, 8),
             prm["L_upper_right_P14_P12"], prm["L_fore_right_P16_P14"]),
            ("left", 11, 13, 15, slice(8, 13),
             prm["L_upper_left_P13_P11"], prm["L_fore_left_P15_P13"])):
        R_sh, R_elb, e = arm_local(ang[idx], side, method)
        T_sh = hom(np.eye(3), prm[f"offset_L24_P_L{sh_id}ORG"])   # (3.5)
        T_el = hom(R_sh, Lua * (R_sh @ e))                         # (3.5)
        T_wr = hom(np.eye(3), Lfa * (R_elb @ e))
        T0_sh = T_root @ T_sh
        T0_el = T0_sh @ T_el                                       # (3.6)
        out[sh_id] = apply(T0_sh, np.zeros(3))
        out[el_id] = apply(T0_el, np.zeros(3))
        out[wr_id] = apply(T0_el @ T_wr, np.zeros(3))
        tr[f"T_L24_L{sh_id}"] = T_sh
        tr[f"T_L{sh_id}_L{el_id}"] = T_el
        tr[f"L{el_id}_P_L{wr_id}ORG"] = T_wr[:3, 3]
    if method == "A":
        cam = {k: F @ out[k] for k in LANDMARK_IDS}     # un-flip
    else:
        cam = {k: out[k] for k in LANDMARK_IDS}
    return cam, out, tr


def fk_vector_form(prm, ang_deg, method):
    """The same FK written as plain vector sums (no 4x4), as a cross-check;
    the left arm of Method A uses R_root M R_sh R_elb (+x), the direct
    inverse of solve_left_arm, instead of M R M on -x."""
    ang = np.asarray(ang_deg, dtype=float)
    R = recompose_zxy(ang[:3])
    o = prm["origin_P24"]
    q = {24: o.copy(), 23: o + R @ prm["offset_L24_P_L23ORG"],
         12: o + R @ prm["offset_L24_P_L12ORG"],
         11: o + R @ prm["offset_L24_P_L11ORG"]}
    ty, tz, tt, ey, ez = np.radians(ang[3:8])
    if method == "A":
        Rs, Re, e = _ry(ty) @ _rz(tz) @ _rx(tt), _ry(ey) @ _rz(ez), X_HAT
    else:
        Rs, Re, e = _ry(ty) @ _rz(tz) @ _rx(-tt), _ry(ey) @ _rz(ez), -X_HAT
    q[14] = q[12] + prm["L_upper_right_P14_P12"] * (R @ Rs @ e)
    q[16] = q[14] + prm["L_fore_right_P16_P14"] * (R @ Rs @ Re @ e)
    ty, tz, tt, ey, ez = np.radians(ang[8:13])
    Rs, Re = _ry(ty) @ _rz(tz) @ _rx(tt), _ry(ey) @ _rz(ez)
    if method == "A":
        q[13] = q[11] + prm["L_upper_left_P13_P11"] * (R @ M @ Rs @ X_HAT)
        q[15] = q[13] + prm["L_fore_left_P15_P13"] * (R @ M @ Rs @ Re @ X_HAT)
        return {k: F @ q[k] for k in LANDMARK_IDS}
    q[13] = q[11] + prm["L_upper_left_P13_P11"] * (R @ Rs @ X_HAT)
    q[15] = q[13] + prm["L_fore_left_P15_P13"] * (R @ Rs @ Re @ X_HAT)
    return q


def project(p, K):
    return np.array([K["fx"] * p[0] / p[2] + K["ppx"],
                     K["fy"] * p[1] / p[2] + K["ppy"]])


def errors(rec, meas, K):
    e3 = {k: float(np.linalg.norm(rec[k] - meas[k])) for k in LANDMARK_IDS}
    epx = {k: float(np.linalg.norm(project(rec[k], K) - project(meas[k], K)))
           for k in LANDMARK_IDS}
    v3, vpx = np.array(list(e3.values())), np.array(list(epx.values()))
    return {"per_landmark_3d_m": {f"L{k}": e3[k] for k in LANDMARK_IDS},
            "per_landmark_px": {f"L{k}": epx[k] for k in LANDMARK_IDS},
            "max_3d_m": float(v3.max()),
            "rms_3d_m": float(np.sqrt(np.mean(v3 ** 2))),
            "max_px": float(vpx.max()),
            "rms_px": float(np.sqrt(np.mean(vpx ** 2)))}


def sensitivity(prm, ang_deg, method):
    base, _, _ = fk(prm, ang_deg, method)
    tab = np.zeros((13, len(LANDMARK_IDS)))
    for i in range(13):
        a = np.array(ang_deg, dtype=float)
        a[i] += STEP_DEG
        pert, _, _ = fk(prm, a, method)
        tab[i] = [np.linalg.norm(pert[k] - base[k]) for k in LANDMARK_IDS]
    return tab


# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
def draw_skel(ax, uv, color, lw, ls="-", ms=0, mfc="none", z=3, label=None):
    for a, b in CONNECTIONS:
        ax.plot([uv[a][0], uv[b][0]], [uv[a][1], uv[b][1]], color=color,
                lw=lw, ls=ls, zorder=z, solid_capstyle="round")
    if ms:
        pts = np.array([uv[k] for k in LANDMARK_IDS])
        ax.plot(pts[:, 0], pts[:, 1], ls="none", marker="o", ms=ms,
                mec=color, mfc=mfc, mew=1.6, zorder=z + 1, label=label)


# Figure text sizes in points at the 13 in drawing width. The figure is
# printed at 6.3 in (build_docx.py FIG_WIDTH), a factor 0.48, so 14 pt titles
# print at about 6.8 pt and 13 pt tick labels at about 6.3 pt.
FONT_TITLE = 14
FONT_LABEL = 13
FONT_TICK = 13
N_TICKS = 4            # at most four major ticks per 3D axis


def make_figure(rgb, K, meas, rec_a, rec_b, err_a, err_b, meta):
    uv_m = {k: project(meas[k], K) for k in LANDMARK_IDS}
    uv_a = {k: project(rec_a[k], K) for k in LANDMARK_IDS}
    uv_b = {k: project(rec_b[k], K) for k in LANDMARK_IDS}
    fig = plt.figure(figsize=(13.0, 10.6))
    gs = fig.add_gridspec(2, 2, hspace=0.16, wspace=0.06,
                          left=0.02, right=0.98, top=0.94, bottom=0.04)
    yel, cya, mag = "#ffd400", "#00e5ff", "#ff2bd6"
    titles = [
        "(a) Measured landmarks projected\nonto the colour image",
        "(b) Implemented convention, rebuilt and un-flipped\n"
        "to {Camera} (cyan), over measured (yellow)",
        "(c) Right-handed convention, rebuilt (magenta),\n"
        "over measured (yellow)",
    ]
    # The reconstruction errors are in Table 4, not in the panel titles.
    del err_a, err_b
    for i, title in enumerate(titles):
        ax = fig.add_subplot(gs[i // 2, i % 2])
        ax.imshow(rgb)
        ax.set_xlim(0, K["width"])
        ax.set_ylim(K["height"], 0)
        ax.set_axis_off()
        ax.set_title(title, fontsize=FONT_TITLE)
        if i == 0:
            draw_skel(ax, uv_m, yel, 2.2, ms=6, mfc=yel)
            for k in LANDMARK_IDS:
                u, v = uv_m[k]
                dx = 10 if k in (11, 13, 15, 23) else -10
                ax.text(u + dx, v - 8, f"L{k}", color="white", fontsize=FONT_LABEL,
                        ha="left" if dx > 0 else "right", zorder=6,
                        bbox=dict(fc="black", ec="none", alpha=0.6, pad=1.2))
        else:
            col = cya if i == 1 else mag
            draw_skel(ax, uv_m, yel, 1.2, ms=4, mfc=yel, z=3)
            draw_skel(ax, uv_a if i == 1 else uv_b, col, 2.2, ls=(0, (4, 3)),
                      ms=11, z=5)
    # (d) 3D stick figures in {Camera}: plot axes (x, z, y) with y down
    ax = fig.add_subplot(gs[1, 1], projection="3d")
    styles = [("measured", meas, "#c9a400", "o", 9, 3.0, "-"),
              ("implemented", rec_a, "#00a8c0", "x", 9, 1.8, "--"),
              ("right-handed", rec_b, "#d4009f", "+", 12, 1.0, ":")]
    for name, pts, col, mk, ms, lw, ls in styles:
        for a, b in CONNECTIONS:
            ax.plot([pts[a][0], pts[b][0]], [pts[a][2], pts[b][2]],
                    [pts[a][1], pts[b][1]], color=col, lw=lw, ls=ls)
        arr = np.array([pts[k] for k in LANDMARK_IDS])
        ax.plot(arr[:, 0], arr[:, 2], arr[:, 1], ls="none", marker=mk,
                ms=ms, color=col, mfc="none" if mk == "o" else col,
                mew=1.6, label=name)
    arr = np.array([meas[k] for k in LANDMARK_IDS])
    lo, hi = arr.min(axis=0), arr.max(axis=0)
    c, half = (lo + hi) / 2, (hi - lo).max() / 2 + 0.03
    ax.set_xlim(c[0] - half, c[0] + half)
    ax.set_ylim(c[2] - half, c[2] + half)
    ax.set_zlim(c[1] + half, c[1] - half)      # y down: inverted axis
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=12, azim=-70)
    ax.set_xlabel("x (m)", fontsize=FONT_LABEL, labelpad=10)
    ax.set_ylabel("z (m)", fontsize=FONT_LABEL, labelpad=10)
    ax.set_zlabel("y (m, down)", fontsize=FONT_LABEL, labelpad=20)
    ax.tick_params(labelsize=FONT_TICK, pad=6)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.set_major_locator(MaxNLocator(N_TICKS))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=3,
              fontsize=FONT_LABEL, framealpha=0.9)
    ax.set_title("(d) Stick figures in the sensor frame {Camera}\n"
                 "(fixed view, elevation 12 deg, azimuth -70 deg)",
                 fontsize=FONT_TITLE)
    fig.savefig(OUT_PNG, dpi=110)
    plt.close(fig)


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pick", default=str(DEFAULT_PICK))
    ap.add_argument("--angles-a", default=str(DEFAULT_A))
    ap.add_argument("--angles-b", default=str(DEFAULT_BN))
    ap.add_argument("--rgb", default=str(DEFAULT_RGB))
    args = ap.parse_args()
    t0 = time.perf_counter()

    pick = json.loads(Path(args.pick).read_text())
    ja = json.loads(Path(args.angles_a).read_text())
    jb = json.loads(Path(args.angles_b).read_text())
    K = pick["intrinsics"]
    check("intrinsics: distortion coefficients all zero (pinhole exact)",
          all(c == 0.0 for c in K["coeffs"]), f"coeffs {K['coeffs']}")
    meas = {k: np.array(pick["model_landmarks"][str(k)]["xyz_med5_m"], float)
            for k in LANDMARK_IDS}
    for name, j in (("A", ja), ("B native", jb)):
        same = all(np.array_equal(meas[k], np.array(j["points_Camera"][f"L{k}"]))
                   for k in LANDMARK_IDS)
        check(f"{name}: angle JSON points_Camera equal the pick JSON "
              f"xyz_med5_m", same, f"equal for all 8: {same}")
        check(f"{name}: angle names in the PSA order",
              tuple(j["angles13_names"]) == ANGLE_NAMES, "")
    ang_a = np.array(ja["angles13_deg"], dtype=float)
    ang_b = np.array(jb["angles13_deg"], dtype=float)

    prm = {"A": chain_params(meas, "A"), "B": chain_params(meas, "B")}
    for m, ang in (("A", ang_a), ("B", ang_b)):
        d = float(np.max(np.abs(recompose_zxy(ang[:3])
                                - prm[m]["R_root_measured"])))
        prm[m]["R_root_from_euler"] = recompose_zxy(ang[:3])
        prm[m]["R_root_euler_vs_measured_max_abs"] = d
        check(f"{m}: recompose_zxy(root Euler) equals the measured root "
              f"(<= {TOL_3D:g})", d <= TOL_3D, f"max abs diff {d:.3e}")
    for m in ("A", "B"):
        o12, o23 = prm[m]["offset_L24_P_L12ORG"], prm[m]["offset_L24_P_L23ORG"]
        ok = abs(o12[2]) <= TOL_EXACT and max(abs(o23[1]), abs(o23[2])) \
            <= TOL_EXACT
        check(f"{m}: root-frame offsets by construction (L23 on the x axis, "
              f"L12 in the x-y plane)", ok,
              f"L23 offset {np.array2string(o23, precision=6)}, "
              f"L12 offset z {o12[2]:.2e}")

    rec_a, rec_a_prime, tr_a = fk(prm["A"], ang_a, "A")
    rec_b, _, tr_b = fk(prm["B"], ang_b, "B")
    for m, rec, ang in (("A", rec_a, ang_a), ("B", rec_b, ang_b)):
        vf = fk_vector_form(prm[m], ang, m)
        d = max(float(np.linalg.norm(vf[k] - rec[k])) for k in LANDMARK_IDS)
        check(f"{m}: homogeneous chain equals the vector-sum form "
              f"(<= {TOL_EXACT:g} m)", d <= TOL_EXACT, f"max {d:.3e} m")
    err_a = errors(rec_a, meas, K)
    err_b = errors(rec_b, meas, K)
    for m, err in (("A", err_a), ("B native", err_b)):
        for k in LANDMARK_IDS:
            e3 = err["per_landmark_3d_m"][f"L{k}"]
            ep = err["per_landmark_px"][f"L{k}"]
            check(f"{m}: L{k} reproduced in 3D (<= {TOL_3D:g} m)",
                  e3 <= TOL_3D, f"{e3:.3e} m")
            check(f"{m}: L{k} reproduced in pixels (<= {TOL_PX:g} px)",
                  ep <= TOL_PX, f"{ep:.3e} px")
    d_ab = max(float(np.linalg.norm(rec_a[k] - rec_b[k])) for k in LANDMARK_IDS)

    # Full-precision diagnostic: the same FK on the in-memory float64 angles
    # of compute_angles.py (no 12-digit JSON rounding), floor of the method.
    import compute_angles as ca
    out_a, R_A, fa = ca.method_a(meas)
    out_b, R_B, fb = ca.method_b(meas)
    _, fn, _ = ca.method_b_native(meas, out_a, R_A, out_b, R_B, fa, fb)
    full = {}
    for m, ang in (("A", fa), ("B", fn)):
        rec, _, _ = fk(prm[m], ang, m)
        full[m] = errors(rec, meas, K)
        full[m]["angles13_deg_float64"] = ang
        full[m]["angles_json_minus_float64_max_abs_deg"] = float(np.max(
            np.abs((ang_a if m == "A" else ang_b) - ang)))

    sens_a = sensitivity(prm["A"], ang_a, "A")
    sens_b = sensitivity(prm["B"], ang_b, "B")
    sdiff = float(np.max(np.abs(sens_a - sens_b)))
    check(f"sensitivity: |dP| tables of A and B native agree landmark by "
          f"landmark (<= {TOL_SENS:g} m)", sdiff <= TOL_SENS,
          f"max abs diff {sdiff:.3e} m")
    lm = list(LANDMARK_IDS)

    reproj = {f"L{k}": (project(meas[k], K) - np.array(
        [pick["model_landmarks"][str(k)]["u_int"],
         pick["model_landmarks"][str(k)]["v_int"]])).tolist()
        for k in LANDMARK_IDS}

    rgb = plt.imread(args.rgb)
    meta = {"bag": pick["bag"], "frame_index": pick["frame_index"],
            "hw_frame_number": pick.get("hw_frame_number")}
    make_figure(rgb, K, meas, rec_a, rec_b, err_a, err_b, meta)

    n_fail = sum(not c["pass"] for c in CHECKS)
    out = {
        "script": "journal/scripts/fk_reconstruct.py",
        "decision": "J-015 (J-009 M5)",
        "meta": meta,
        "inputs": {"pick": str(Path(args.pick).resolve().relative_to(REPO)),
                   "angles_a": str(Path(args.angles_a).resolve().relative_to(REPO)),
                   "angles_b_native": str(Path(args.angles_b).resolve().relative_to(REPO)),
                   "rgb": str(Path(args.rgb).resolve().relative_to(REPO)),
                   "measured_field": "model_landmarks[k].xyz_med5_m ({Camera}, m)"},
        "intrinsics": K,
        "tolerances": {"TOL_3D_m": TOL_3D, "TOL_PX": TOL_PX,
                       "TOL_SENS_m": TOL_SENS, "TOL_EXACT": TOL_EXACT,
                       "STEP_DEG": STEP_DEG},
        "chain_parameters": {"A": prm["A"], "B_native": prm["B"]},
        "angles13_names": list(ANGLE_NAMES),
        "angles13_deg": {"A": ang_a, "B_native": ang_b},
        "transforms_A_Camera_prime": tr_a,
        "transforms_B_native_Camera": tr_b,
        "measured_Camera": {f"L{k}": meas[k] for k in LANDMARK_IDS},
        "reconstructed_Camera": {
            "A_unflipped": {f"L{k}": rec_a[k] for k in LANDMARK_IDS},
            "B_native": {f"L{k}": rec_b[k] for k in LANDMARK_IDS}},
        "reconstructed_A_Camera_prime": {f"L{k}": rec_a_prime[k]
                                         for k in LANDMARK_IDS},
        "errors": {"A": err_a, "B_native": err_b,
                   "A_vs_B_native_max_3d_m": d_ab},
        "errors_float64_angles_diagnostic": full,
        "measured_projection_minus_u_int_v_int_px": reproj,
        "sensitivity": {
            "step_deg": STEP_DEG,
            "landmarks": [f"L{k}" for k in lm],
            "rows": list(ANGLE_NAMES),
            "A_displacement_m": sens_a,
            "B_native_displacement_m": sens_b,
            "max_abs_A_minus_B_m": sdiff,
            "note": ("+1 deg on one angle at a time; Bn = -A on the right-arm "
                     "angles and root_x, root_z_B = 180 - root_z_A, so the "
                     "B step is a -1 deg step in A about the same line; a "
                     "rotation by +-h about a fixed line moves a point by "
                     "2 sin(h/2) times its distance to the line")},
        "checks": CHECKS,
        "summary": f"{len(CHECKS) - n_fail} PASS / {n_fail} FAIL",
    }
    OUT_JSON.write_text(json.dumps(plain(out), indent=1) + "\n")

    # ---------------------------------------------------------------- print
    print(f"pick: {meta['bag']} frame {meta['frame_index']}")
    for m in ("A", "B"):
        p = prm[m]
        print(f"{m} chain ({p['frame']}): P24 "
              f"{np.array2string(p['origin_P24'], precision=6)}; offsets "
              f"L23 {np.array2string(p['offset_L24_P_L23ORG'], precision=6)} "
              f"L12 {np.array2string(p['offset_L24_P_L12ORG'], precision=6)} "
              f"L11 {np.array2string(p['offset_L24_P_L11ORG'], precision=6)}")
    p = prm["A"]
    print(f"lengths (m): upper R {p['L_upper_right_P14_P12']:.6f} "
          f"fore R {p['L_fore_right_P16_P14']:.6f} "
          f"upper L {p['L_upper_left_P13_P11']:.6f} "
          f"fore L {p['L_fore_left_P15_P13']:.6f}")
    print()
    print(f"{'lm':<4} {'A 3D (m)':>10} {'A px':>10} {'Bn 3D (m)':>10} "
          f"{'Bn px':>10}")
    for k in LANDMARK_IDS:
        n = f"L{k}"
        print(f"{n:<4} {err_a['per_landmark_3d_m'][n]:10.2e} "
              f"{err_a['per_landmark_px'][n]:10.2e} "
              f"{err_b['per_landmark_3d_m'][n]:10.2e} "
              f"{err_b['per_landmark_px'][n]:10.2e}")
    for m, err in (("A", err_a), ("B native", err_b)):
        print(f"{m}: max 3D {err['max_3d_m']:.3e} m, RMS 3D "
              f"{err['rms_3d_m']:.3e} m, max px {err['max_px']:.3e}, RMS px "
              f"{err['rms_px']:.3e}")
    print(f"A versus B native reconstruction, max 3D {d_ab:.3e} m")
    for m in ("A", "B"):
        print(f"diagnostic, float64 angles ({m}): max 3D "
              f"{full[m]['max_3d_m']:.3e} m, max px {full[m]['max_px']:.3e}; "
              f"JSON angle rounding max "
              f"{full[m]['angles_json_minus_float64_max_abs_deg']:.2e} deg")
    print()
    print(f"sensitivity: |dP| (mm) for +{STEP_DEG:g} deg, A / B native")
    print(f"{'angle':<10} " + " ".join(f"{'L' + str(k):>13}" for k in lm))
    for i, n in enumerate(ANGLE_NAMES):
        print(f"{n:<10} " + " ".join(
            f"{1e3 * sens_a[i, j]:6.2f}/{1e3 * sens_b[i, j]:6.2f}"
            for j in range(len(lm))))
    print(f"max |A - B| over the 13 x 8 table: {sdiff:.3e} m")
    print()
    for c in CHECKS:
        print(f"{'PASS' if c['pass'] else 'FAIL'}  {c['name']}  "
              f"[{c['detail']}]")
    print()
    print(f"{out['summary']}; wrote {OUT_JSON.relative_to(REPO)} and "
          f"{OUT_PNG.relative_to(REPO)}; {time.perf_counter() - t0:.3f} s")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())

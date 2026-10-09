"""Figure 1 of the journal track: the initial root-frame triads of two
frame conventions drawn on a schematic (MediaPipe-style) ideal T-pose.

Only the 8 landmarks the kinematic model uses are drawn: L11/L12
shoulders, L13/L14 elbows, L15/L16 wrists, L23/L24 hips.

Method A (current code, v1/kinematics/root_frame.py, imported, not copied):
    {Camera} (right-handed: x right, y down, z forward) is mapped to the
    left-handed {Camera'} by F = diag(1, -1, 1) (unity_from_sensor), then
    build_root_frame(p23', p24', p12') gives R_A = [r | u | f] with
    r = normalize(p24' - p23') (subject's right), s = p12' - p24',
    f = normalize(r x s) (forward), u = f x r (up).

Method B (journal convention, J-002, UNCERTAIN until the author confirms):
    stay in the right-handed {Camera}, root frame at L24 with the hip axis
    reversed:
    x_B = normalize(L23 - L24)          subject's LEFT
    s   = L12 - L24
    z_B = normalize(x_B x s)            subject's FORWARD (toward the camera)
    y_B = z_B x x_B                     subject's UP
    R_B = [x_B | y_B | z_B]

Shared-orientation rule (thesis eq. 3.13 and 3.14): at rest the shoulder,
elbow and wrist frames carry the root orientation with the origin moved to
the landmark, so the same triad is drawn at all 8 landmarks.

Proportions (J-003): segment lengths derived from Table 3.1 of the thesis
(writing/v9/scripts/build_ch3.py, frame 533 of recording_20260831_065553).
Figure conventions: J-004. Run:
    /home/luo/anaconda3/bin/python journal/scripts/make_tpose_frames_fig.py
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
OUT_PNG = REPO / "journal" / "figures" / "fig1_tpose_frames.png"

# v1 is frozen: import only; do not write bytecode into v1/kinematics.
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO / "v1" / "kinematics"))
from root_frame import build_root_frame, unity_from_sensor, SENSOR_TO_UNITY  # noqa: E402

F = np.diag(SENSOR_TO_UNITY)  # {Camera} -> {Camera'}, diag(1, -1, 1)

# ---------------------------------------------------------------------------
# Table 3.1 of the thesis ({Camera} column, metres, printed to two decimals).
# Source: writing/v9/scripts/build_ch3.py, section 3.5, Table 3.1.
# ---------------------------------------------------------------------------
TABLE_3_1_CAMERA = {
    11: (0.22, -0.34, 1.36),
    12: (-0.16, -0.33, 1.31),
    13: (0.28, -0.03, 1.38),
    14: (-0.20, -0.04, 1.19),
    15: (0.24, 0.20, 1.25),
    16: (-0.20, 0.11, 1.06),
    23: (0.12, 0.18, 0.99),
    24: (-0.06, 0.19, 0.99),
}

NAMES = {
    11: "left shoulder", 12: "right shoulder",
    13: "left elbow", 14: "right elbow",
    15: "left wrist", 16: "right wrist",
    23: "left hip", 24: "right hip",
}

CONNECTIONS = [(11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
               (11, 23), (12, 24), (23, 24)]

# Subject depth in {Camera}: brief value (J-003); R_A and R_B do not depend on it.
SUBJECT_Z_M = 2.0

# Axis colours: presentation/defense_2026/anim/coordinate_axes.py AXIS_COLORS.
AXIS_COLORS = {"x": "#FF4040", "y": "#40E070", "z": "#408CFF"}


def dist(a, b):
    return float(np.linalg.norm(np.subtract(a, b)))


def proportions_from_table():
    """Segment lengths of the schematic, from Table 3.1 (J-003)."""
    t = {k: np.array(v) for k, v in TABLE_3_1_CAMERA.items()}
    d = {
        "shoulder width |L11-L12|": dist(t[11], t[12]),
        "hip width |L23-L24|": dist(t[23], t[24]),
        "right upper arm |L12-L14|": dist(t[12], t[14]),
        "left upper arm |L11-L13|": dist(t[11], t[13]),
        "right forearm |L14-L16|": dist(t[14], t[16]),
        "left forearm |L13-L15|": dist(t[13], t[15]),
        "right hip-shoulder 3D |L24-L12|": dist(t[24], t[12]),
        "left hip-shoulder 3D |L23-L11|": dist(t[23], t[11]),
        "right hip-shoulder vertical |y24-y12|": abs(t[24][1] - t[12][1]),
        "left hip-shoulder vertical |y23-y11|": abs(t[23][1] - t[11][1]),
    }
    geom = {
        "shoulder_w": d["shoulder width |L11-L12|"],
        "hip_w": d["hip width |L23-L24|"],
        "upper_arm": 0.5 * (d["right upper arm |L12-L14|"] + d["left upper arm |L11-L13|"]),
        "forearm": 0.5 * (d["right forearm |L14-L16|"] + d["left forearm |L13-L15|"]),
        # Vertical separation only: Table 3.1 is before the hip depth
        # preparation of thesis Section 2.6, so the hip z is not trusted
        # for a length (J-003).
        "torso_h": 0.5 * (d["right hip-shoulder vertical |y24-y12|"]
                          + d["left hip-shoulder vertical |y23-y11|"]),
        # Hip row height in {Camera}: mean hip y of Table 3.1.
        "hip_y": 0.5 * (t[23][1] + t[24][1]),
    }
    return d, geom


def ideal_tpose(geom):
    """Ideal T-pose in {Camera}: facing the camera, all landmarks at one z."""
    hy = geom["hip_y"]
    sy = hy - geom["torso_h"]           # shoulders above the hips (y down)
    hw, sw = 0.5 * geom["hip_w"], 0.5 * geom["shoulder_w"]
    ua, fa = geom["upper_arm"], geom["forearm"]
    z = SUBJECT_Z_M
    # Subject faces the camera, so the subject's right is camera -x.
    return {
        24: np.array([-hw, hy, z]), 23: np.array([hw, hy, z]),
        12: np.array([-sw, sy, z]), 11: np.array([sw, sy, z]),
        14: np.array([-sw - ua, sy, z]), 13: np.array([sw + ua, sy, z]),
        16: np.array([-sw - ua - fa, sy, z]), 15: np.array([sw + ua + fa, sy, z]),
    }


def method_b_root(p23, p24, p12):
    """Method B, right-handed {Camera}; formulas as in the module docstring."""
    x = p23 - p24
    x = x / np.linalg.norm(x)           # x_B = normalize(L23 - L24): subject's left
    s = p12 - p24                       # spine-side vector, selects the torso plane
    z = np.cross(x, s)
    z = z / np.linalg.norm(z)           # z_B = normalize(x_B x s): subject's forward
    y = np.cross(z, x)                  # y_B = z_B x x_B: subject's up
    return np.stack([x, y, z], axis=-1)


def fmt_vec(v):
    return "(" + ", ".join(f"{c + 0.0:+.4f}" for c in v) + ")"


def fmt_mat(m, indent="    "):
    return "\n".join(indent + "[" + "  ".join(f"{c + 0.0:+.4f}" for c in row) + "]" for row in m)


def physical_direction(col):
    """Name a {Camera} unit vector by the subject-facing-camera anatomy."""
    names = {
        (1, 0, 0): "camera +x = subject's LEFT",
        (-1, 0, 0): "camera -x = subject's RIGHT",
        (0, -1, 0): "camera -y = subject's UP",
        (0, 1, 0): "camera +y = subject's DOWN",
        (0, 0, -1): "camera -z = subject's FORWARD (toward camera)",
        (0, 0, 1): "camera +z = subject's BACKWARD (away from camera)",
    }
    key = tuple(int(round(c)) for c in col)
    if np.allclose(col, key, atol=1e-9) and key in names:
        return names[key]
    return "oblique"


def report(d, geom, P, R_A, R_B):
    print("=== Proportions from thesis Table 3.1 (frame 533, {Camera}, 2-decimal inputs) ===")
    for k, v in d.items():
        print(f"  {k:40s} {v:.4f} m")
    print("  schematic values used:")
    for k, v in geom.items():
        print(f"    {k:12s} {v:.4f} m")
    print(f"    subject z  {SUBJECT_Z_M:.4f} m (brief value)")
    print()
    print("=== Ideal T-pose landmarks ===")
    for k in (11, 12, 13, 14, 15, 16, 23, 24):
        print(f"  L{k} {NAMES[k]:15s} {{Camera}} {fmt_vec(P[k])}   "
              f"{{Camera'}} {fmt_vec(unity_from_sensor(P[k]))}")
    print()
    print("=== Root inputs ===")
    for k in (23, 24, 12):
        print(f"  p{k}  {{Camera}} {fmt_vec(P[k])}   {{Camera'}} {fmt_vec(unity_from_sensor(P[k]))}")
    print()
    print("=== Method A: R_A = build_root_frame(F p23, F p24, F p12), in {Camera'} coordinates ===")
    print(fmt_mat(R_A))
    print(f"  det(R_A) = {np.linalg.det(R_A):+.12f}")
    print()
    print("=== Method B: R_B = [x_B | y_B | z_B], in {Camera} coordinates ===")
    print(fmt_mat(R_B))
    print(f"  det(R_B) = {np.linalg.det(R_B):+.12f}")
    print()
    print("=== R_B^T R_A (as asked; note: mixes {Camera} and {Camera'} components) ===")
    print(fmt_mat(R_B.T @ R_A))
    FR_A = F @ R_A
    print()
    print("=== R_A columns in physical {Camera} (F R_A, undoing the y flip) ===")
    print(fmt_mat(FR_A))
    print(f"  det(F R_A) = {np.linalg.det(FR_A):+.12f}  (A's triad is left-handed in {{Camera}})")
    print()
    print("=== R_B^T (F R_A): A's axes expressed in B's frame, same physical space ===")
    print(fmt_mat(R_B.T @ FR_A))
    print()
    print("=== Column-by-column comparison in physical {Camera} ===")
    verdict = {}
    for i, ax in enumerate("xyz"):
        a, b = FR_A[:, i], R_B[:, i]
        dot = float(a @ b)
        verdict[ax] = dot
        print(f"  {ax}: A {fmt_vec(a)} [{physical_direction(a)}]")
        print(f"     B {fmt_vec(b)} [{physical_direction(b)}]")
        print(f"     A . B = {dot:+.6f}  -> {'SAME' if dot > 1 - 1e-9 else 'OPPOSITE' if dot < -1 + 1e-9 else 'DIFFERENT'}")
    expected = (np.isclose(verdict["x"], -1.0) and np.isclose(verdict["y"], 1.0)
                and np.isclose(verdict["z"], 1.0))
    print()
    print("Expectation 'same y, same z, opposite x': " + ("PASS" if expected else "FAIL"))
    return expected


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------
ARROW_LEN = 0.110      # page length of the in-plane triad arrows, metres of image plane (J-004)
Z_RING_R = 0.020       # radius of the circled-dot / circled-cross symbol (J-004)
Z_ARROW_LEN = 0.065    # short foreshortened z arrow (J-004)
Z_ARROW_DIR = np.array([1.0, -1.0]) / np.sqrt(2.0)  # page up-right (y down on the page)
LABEL_DY = 0.055       # landmark label offset below the dot (J-004)


def draw_arrow(ax, origin, vec, color, lw=2.2, zorder=6, head=0.022):
    ax.annotate("", xy=(origin[0] + vec[0], origin[1] + vec[1]), xytext=(origin[0], origin[1]),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                mutation_scale=12, shrinkA=0, shrinkB=0),
                zorder=zorder)


def draw_out_of_page(ax, c, color, toward_viewer, r=Z_RING_R, zorder=7):
    ax.add_patch(Circle(c, r, facecolor="white", edgecolor=color, lw=1.6, zorder=zorder))
    if toward_viewer:
        ax.add_patch(Circle(c, r * 0.30, facecolor=color, edgecolor=color, zorder=zorder + 1))
    else:
        k = r * 0.68
        ax.plot([c[0] - k, c[0] + k], [c[1] - k, c[1] + k], color=color, lw=1.6, zorder=zorder + 1)
        ax.plot([c[0] - k, c[0] + k], [c[1] + k, c[1] - k], color=color, lw=1.6, zorder=zorder + 1)


def draw_triad(ax, origin, R_phys):
    """Draw a frame whose columns are given in physical {Camera} components.

    Page coordinates = (camera x, camera y) with y increasing downward.
    In-plane columns become fixed-length arrows; a column along camera z is
    drawn as a circled dot (toward the viewer, camera -z) or a circled cross
    (away from the viewer, camera +z) with a short diagonal arrow.
    """
    o = np.asarray(origin[:2], float)
    for i, name in enumerate("xyz"):
        col = R_phys[:, i]
        inplane = col[:2]
        n = np.linalg.norm(inplane)
        color = AXIS_COLORS[name]
        if n > 0.5:
            v = inplane / n * ARROW_LEN
            draw_arrow(ax, o, v, color)
            u = v / ARROW_LEN
            perp = np.array([-u[1], u[0]])
            # Label beside the tip: below a horizontal arrow (clear of the
            # neighbouring triads), left of a vertical arrow (clear of z).
            if abs(u[0]) >= abs(u[1]):
                side = perp if perp[1] > 0 else -perp
            else:
                side = perp if perp[0] < 0 else -perp
            tip = o + v + u * 0.012 + side * 0.022
            ax.text(tip[0], tip[1], name, color=color, fontsize=8.5, fontweight="bold",
                    ha="center", va="center", zorder=9)
        if abs(col[2]) > 0.5:
            toward = col[2] < 0          # camera -z points at the camera = the viewer
            v = Z_ARROW_DIR * Z_ARROW_LEN
            draw_arrow(ax, o, v, color, lw=1.4, zorder=5)
            draw_out_of_page(ax, o, color, toward)
            ax.text(o[0] + v[0] + 0.016, o[1] + v[1] - 0.006, "z", color=color, fontsize=8.5,
                    fontweight="bold", ha="left", va="center", zorder=9)


def draw_camera_axes(ax, corner, y_down, title):
    """Camera axes in a corner: x right; y down ({Camera}) or up ({Camera'}); z into the page."""
    c = np.asarray(corner, float)
    L = 0.11
    draw_arrow(ax, c, np.array([L, 0.0]), "black", lw=1.6)
    draw_arrow(ax, c, np.array([0.0, L if y_down else -L]), "black", lw=1.6)
    draw_out_of_page(ax, c, "black", toward_viewer=False, r=0.02)
    ax.text(c[0] + L + 0.02, c[1], "x", fontsize=9, ha="left", va="center")
    ax.text(c[0], c[1] + (L + 0.03 if y_down else -L - 0.03), "y", fontsize=9, ha="center", va="center")
    ax.text(c[0] - 0.035, c[1] + 0.035 * (1 if not y_down else -1), "z", fontsize=9,
            ha="center", va="center")
    ax.text(c[0] + L + 0.08, c[1], title, fontsize=9.5,
            ha="left", va="center", fontweight="bold")


def draw_panel(ax, P, R_phys, title, y_down_cam, cam_title):
    ax.set_facecolor("white")
    for a, b in CONNECTIONS:
        ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]], color="#9a9a9a", lw=3.0,
                solid_capstyle="round", zorder=2)
    for k, p in P.items():
        ax.add_patch(Circle(p[:2], 0.012, facecolor="white", edgecolor="#333333", lw=1.0, zorder=3))
    for k, p in P.items():
        draw_triad(ax, p, R_phys)
    for k, p in P.items():
        if k == 24:
            ax.text(p[0] - 0.03, p[1] + LABEL_DY, f"L{k}\n{NAMES[k]}", fontsize=8, ha="right",
                    va="top", zorder=9)
        elif k == 23:
            ax.text(p[0] + 0.03, p[1] + LABEL_DY, f"L{k}\n{NAMES[k]}", fontsize=8, ha="left",
                    va="top", zorder=9)
        else:
            ax.text(p[0], p[1] + LABEL_DY, f"L{k}\n{NAMES[k]}", fontsize=8, ha="center",
                    va="top", zorder=9)
    draw_camera_axes(ax, (-0.80, -0.76 if y_down_cam else -0.62), y_down_cam, cam_title)
    ax.set_title(title, fontsize=10.5)
    ax.set_aspect("equal")
    ax.set_xlim(-0.88, 0.88)
    ax.set_ylim(0.36, -0.86)            # camera y down on the page
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#bbbbbb")


def make_figure(P, FR_A, R_B):
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.7))
    draw_panel(axes[0], P, FR_A,
               "(a) Implemented convention (left-handed camera frame)\n"
               "torso x axis from L23 to L24",
               y_down_cam=False, cam_title="{Camera'}")
    draw_panel(axes[1], P, R_B,
               "(b) Right-handed convention\n"
               "torso x axis from L24 to L23",
               y_down_cam=True, cam_title="{Camera}")
    # No in-figure legend: the caption of Figure 1 explains the view, the
    # axis colours and the circled symbols.
    fig.subplots_adjust(left=0.01, right=0.99, top=0.89, bottom=0.02, wspace=0.03)
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PNG, dpi=200, facecolor="white")
    plt.close(fig)


def main():
    d, geom = proportions_from_table()
    P = ideal_tpose(geom)
    Pp = {k: unity_from_sensor(v) for k, v in P.items()}
    R_A = build_root_frame(Pp[23], Pp[24], Pp[12])
    R_B = method_b_root(P[23], P[24], P[12])
    ok = report(d, geom, P, R_A, R_B)
    FR_A = F @ R_A
    make_figure(P, FR_A, R_B)
    print()
    print(f"Wrote {OUT_PNG.relative_to(REPO)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

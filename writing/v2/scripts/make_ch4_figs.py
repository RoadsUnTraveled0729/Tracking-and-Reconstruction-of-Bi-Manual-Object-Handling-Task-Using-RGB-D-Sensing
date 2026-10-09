"""Chapter 4 figures. All real-data panels use the pinned artifacts in
aruco/dataset/ (recording_20260224_083945) and the real color intrinsics;
nothing is invented. Outputs to writing/v2/figures/ as ch4_fig*.png."""
import json
import shutil
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

ROOT = "/home/luo/Desktop/New_SandBox"
sys.path.insert(0, f"{ROOT}/aruco")
from frames import geodesic_deg, inv_T, make_T, rt_from_row

DS = f"{ROOT}/aruco/dataset"
FIG = f"{ROOT}/writing/v2/figures"
FRAME = 100

# real color intrinsics (Chapter 2 running example)
FX, FY, CX, CY = 607.5626, 607.0234, 323.9403, 248.0233

raw = pd.read_csv(f"{DS}/recording_20260224_083945_aruco_raw.csv")
world = pd.read_csv(f"{DS}/recording_20260224_083945_object_world.csv")
filt = pd.read_csv(f"{DS}/recording_20260224_083945_object_world_filtered.csv")
calib = json.load(open(f"{DS}/scene_calibration.json"))
row = raw[raw.frame == FRAME].iloc[0]
IMG = plt.imread(f"{ROOT}/integration/dataset/real_color_frame100.png")

T_cam_desk = np.array(calib["T_cam_desk"])
T_cam_wall = np.array(calib["T_cam_wall"])
T_desk_cam = inv_T(T_cam_desk)

AX_C = {"x": "#d62728", "y": "#2ca02c", "z": "#1f77b4"}


def px(p):
    return FX * p[0] / p[2] + CX, FY * p[1] / p[2] + CY


def box(ax, x, y, w, h, text, fc="#eef3fa", ec="#4a6a9a", fs=8.6, lw=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012",
                                fc=fc, ec=ec, lw=lw, mutation_scale=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def arrow(ax, p0, p1, color="#333333", lw=1.4, style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=13,
                                 color=color, lw=lw, linestyle=ls,
                                 shrinkA=0, shrinkB=0))


# ---------------------------------------------------------------- fig 1
# offline pipeline dataflow with the alignment and calibration blocks
fig, ax = plt.subplots(figsize=(9.4, 5.4))
ax.set_xlim(0, 100); ax.set_ylim(0, 60); ax.axis("off")

box(ax, 2, 26, 12, 9, "bag recording\n(color + depth +\ncalibration)", fc="#f5eedd", ec="#8a6d1a")
box(ax, 19, 26, 14, 9, "frame extraction\nand depth-to-color\nalignment (Ch. 2)", fc="#f5eedd", ec="#8a6d1a")

# branch A (top)
box(ax, 40, 46, 12, 8, "MediaPipe Pose\n8 landmarks")
box(ax, 55, 46, 12, 8, "depth lifting\nto 3D (Ch. 2)")
box(ax, 70, 46, 12, 8, "smoothing\n(Ch. 2)")
box(ax, 40, 34.5, 42, 6.5, "kinematic solve (Ch. 3): joint angles per frame")

# branch B (bottom)
box(ax, 40, 15, 12, 8, "ArUco detection\n+ subpixel corners", fc="#eaf5ea", ec="#3a7a3a")
box(ax, 55, 15, 12, 8, "per-marker\nplanar PnP pose", fc="#eaf5ea", ec="#3a7a3a")
box(ax, 70, 15, 12, 8, "world anchoring\n+ object filter", fc="#eaf5ea", ec="#3a7a3a")
box(ax, 47, 3, 20, 7, "static scene calibration\n(first 10 frames, frozen)", fc="#fdeaea", ec="#a04040")

box(ax, 86.5, 26, 11.5, 9, "data fusion:\nper-frame fused\nrecord (4.4)", fc="#efe8f7", ec="#6a4a9a")

arrow(ax, (14, 30.5), (19, 30.5))
arrow(ax, (33, 32.5), (40, 50)); arrow(ax, (33, 28.5), (40, 19))
arrow(ax, (52, 50), (55, 50)); arrow(ax, (67, 50), (70, 50))
arrow(ax, (76, 46), (76, 41))
arrow(ax, (52, 19), (55, 19)); arrow(ax, (67, 19), (70, 19))
arrow(ax, (61, 15), (59, 10), color="#a04040")
arrow(ax, (67, 6.5), (76, 15), color="#a04040")
arrow(ax, (82, 37.8), (86.5, 33)); arrow(ax, (82, 19), (86.5, 28))
arrow(ax, (98, 30.5), (99.8, 30.5))
ax.text(99.0, 33.2, "to Unity\n(Ch. 5)", fontsize=8, ha="center")
ax.text(61, 57, "landmark branch (person)", fontsize=9.5, style="italic", ha="center", color="#4a6a9a")
ax.text(61, 25.6, "marker branch (scene and object)", fontsize=9.5, style="italic", ha="center", color="#3a7a3a")
plt.tight_layout()
plt.savefig(f"{FIG}/ch4_fig1_pipeline.png", dpi=200); plt.close()

# ---------------------------------------------------------------- fig 2
# conceptual independence diagram
fig, ax = plt.subplots(figsize=(8.6, 4.4))
ax.set_xlim(0, 100); ax.set_ylim(0, 52); ax.axis("off")
box(ax, 36, 42, 28, 8, "one recorded session\n(a single bag file)", fc="#f5eedd", ec="#8a6d1a", fs=9.5)
box(ax, 4, 20, 37, 13, "landmark chain (Ch. 2, 3)\ndepth channel + learned detector\n$\\rightarrow$ wrist trajectory", fs=9)
box(ax, 59, 20, 37, 13, "marker chain (this chapter)\ncolor channel + fiducial geometry\n$\\rightarrow$ object trajectory", fc="#eaf5ea", ec="#3a7a3a", fs=9)
box(ax, 28, 2, 44, 9, "one desk-anchored world frame\nwrist and object compared in Chapter 6", fc="#efe8f7", ec="#6a4a9a", fs=9.5)
arrow(ax, (44, 42), (26, 33)); arrow(ax, (56, 42), (74, 33))
arrow(ax, (24, 20), (40, 11)); arrow(ax, (76, 20), (60, 11))
ax.text(50, 27, "no shared code\nno shared data\ndifferent physics", ha="center",
        va="center", fontsize=8.2, style="italic", color="#555555")
plt.tight_layout()
plt.savefig(f"{FIG}/ch4_fig2_independence.png", dpi=200); plt.close()

# ---------------------------------------------------------------- fig 3
# real frame 100 with the three detected markers outlined
# outlines from the pipeline's own frame-100 poses: project the four known
# marker-frame corners through the detected (R, t) and the real intrinsics
SIZES = {0: 0.150, 2: 0.050, 1: 0.050}
roles = {0: "id 0  wall\n150 mm, plumb\ngravity reference", 2: "id 2  desk\n50 mm, world\nanchor (frozen)",
         1: "id 1  object\n50 mm, on the\ncarried 70 mm cube"}
off = {0: (-345, 45), 2: (95, -55), 1: (60, 45)}
fig, ax = plt.subplots(figsize=(8.4, 6.3))
ax.imshow(IMG); ax.axis("off")
for mid in (0, 2, 1):
    R, t = rt_from_row(row, mid)
    L = SIZES[mid] / 2
    q = np.array([px(R @ np.array([sx * L, sy * L, 0.0]) + t)
                  for sx, sy in [(-1, 1), (1, 1), (1, -1), (-1, -1)]])
    ax.add_patch(Polygon(q, closed=True, fill=False, ec="#ffd60a", lw=2.2))
    for p in q:
        ax.plot(*p, "o", color="#d62728", ms=3.5)
    cen = q.mean(axis=0)
    dx, dy = off[mid]
    ax.annotate(roles[mid], xy=cen, xytext=(cen[0] + dx, cen[1] + dy),
                fontsize=9, color="white", ha="left", va="center",
                bbox=dict(boxstyle="round,pad=0.3", fc="black", alpha=0.72),
                arrowprops=dict(arrowstyle="->", color="#ffd60a", lw=1.6))
plt.tight_layout()
plt.savefig(f"{FIG}/ch4_fig3_markers_photo.png", dpi=200); plt.close()

# ---------------------------------------------------------------- fig 4
# planar two-lobe ambiguity + measured separations
fig = plt.figure(figsize=(9.6, 4.0))
ax = fig.add_subplot(121)
ax.set_xlim(-2.4, 2.4); ax.set_ylim(-0.5, 4.4)
ax.set_aspect("equal"); ax.axis("off")
ax.plot(0, 0, "s", color="black", ms=9)
ax.text(0, -0.36, "camera", ha="center", fontsize=9)
for xe in (-0.9, 0.9):
    ax.plot([0, xe * 1.9], [0, 3.9], color="#999999", lw=1.0, ls=":")
th = np.radians(24)
c0 = np.array([0.0, 3.4])
for sgn, col, lab in [(+1, "#1f77b4", "lobe 1: tilted toward"),
                      (-1, "#d62728", "lobe 2: tilted away")]:
    d = np.array([np.cos(sgn * th), np.sin(sgn * th) * 0.0])
    dvec = np.array([np.cos(np.pi / 2 - sgn * th), np.sin(np.pi / 2 - sgn * th)])
    p0, p1 = c0 - 0.85 * np.array([dvec[1], -dvec[0]]), c0 + 0.85 * np.array([dvec[1], -dvec[0]])
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=col, lw=3.0)
    n = dvec
    ax.add_patch(FancyArrowPatch(c0, c0 + 0.75 * n, arrowstyle="-|>",
                                 mutation_scale=13, color=col, lw=1.6))
ax.text(0, 4.25, "two plane tilts, nearly the same image", ha="center", fontsize=9.5)
ax.text(-2.3, 2.0, "the two poses reproject\nalmost identically when\nthe marker is small in\nthe image and near\nfronto-parallel", fontsize=8.4, va="center")
ax.set_title("(a) the planar pose ambiguity", fontsize=10)

ax2 = fig.add_subplot(122)
names = ["desk id 2\n(0.58 m)", "object id 1\n(0.93 m)", "wall id 0\n(3.38 m)"]
seps = [64, 62, 23]
cols = ["#3a7a3a", "#3a7a3a", "#a04040"]
b = ax2.bar(names, seps, color=cols, width=0.55)
ax2.axhline(40, color="black", ls="--", lw=1.2)
ax2.text(-0.42, 42, "40$^\\circ$ policy threshold", fontsize=8.6, ha="left")
for r, v in zip(b, seps):
    ax2.text(r.get_x() + r.get_width() / 2, v + 1.2, f"{v}$^\\circ$", ha="center", fontsize=9)
ax2.set_ylabel("separation between the two pose solutions (deg)", fontsize=8.6)
ax2.set_ylim(0, 75)
ax2.tick_params(labelsize=8.6)
ax2.set_title("(b) measured lobe separations, frame 100 ranges", fontsize=10)
plt.tight_layout()
plt.savefig(f"{FIG}/ch4_fig4_lobes.png", dpi=200); plt.close()

# ---------------------------------------------------------------- fig 5
# measured drift: desk per-frame vs frozen anchor; wall in the desk frame
R_cd, t_cd = T_cam_desk[:3, :3], T_cam_desk[:3, 3]
T_desk_wall_cal = T_desk_cam @ T_cam_wall
t_dev, a_dev, tt = [], [], []
w_dev, wt = [], []
for _, r in raw.iterrows():
    g2 = rt_from_row(r, 2)
    if g2 is not None:
        a_dev.append(geodesic_deg(R_cd, g2[0]))
        t_dev.append(1000 * np.linalg.norm(g2[1] - t_cd))
        tt.append(r.time_s)
    g0 = rt_from_row(r, 0)
    if g0 is not None and g2 is not None:
        # validator definition: wall in the desk frame using the PER-FRAME
        # desk detection (no calibration involved), vs the calibrated pose
        Tw = inv_T(make_T(*g2)) @ make_T(*g0)
        w_dev.append(1000 * np.linalg.norm(Tw[:3, 3] - T_desk_wall_cal[:3, 3]))
        wt.append(r.time_s)
a_dev, w_dev = np.array(a_dev), np.array(w_dev)
fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.4))
axs[0].plot(tt, a_dev, color="#3a7a3a", lw=0.8)
axs[0].axhline(np.percentile(a_dev, 95), color="black", ls="--", lw=1.1)
axs[0].text(29.5, np.percentile(a_dev, 95) + 0.004,
            f"p95 = {np.percentile(a_dev, 95):.3f}$^\\circ$", ha="right", fontsize=8.6)
axs[0].set_xlabel("time (s)", fontsize=9); axs[0].set_ylabel("desk orientation vs frozen anchor (deg)", fontsize=8.6)
axs[0].set_title("(a) desk marker orientation drift", fontsize=10)
axs[1].plot(wt, w_dev, color="#a04040", lw=0.8)
axs[1].axhline(np.percentile(w_dev, 95), color="black", ls="--", lw=1.1)
axs[1].text(29.5, np.percentile(w_dev, 95) + 0.25,
            f"p95 = {np.percentile(w_dev, 95):.1f} mm", ha="right", fontsize=8.6)
axs[1].set_xlabel("time (s)", fontsize=9); axs[1].set_ylabel("wall position in the desk frame\nvs calibration (mm)", fontsize=8.6)
axs[1].set_title("(b) camera-invariance check at the wall", fontsize=10)
for a in axs:
    a.tick_params(labelsize=8.6); a.grid(alpha=0.25)
plt.tight_layout()
plt.savefig(f"{FIG}/ch4_fig5_anchor_drift.png", dpi=200); plt.close()

# ---------------------------------------------------------------- fig 6
# the three frames and the transform chain on the real photo
fig, ax = plt.subplots(figsize=(8.4, 6.3))
ax.imshow(IMG); ax.axis("off")
for (R, t), mid, alen in [((T_cam_desk[:3, :3], T_cam_desk[:3, 3]), 2, 0.055),
                          (rt_from_row(row, 1), 1, 0.055)]:
    o = px(t)
    for k, axis in zip("xyz", np.eye(3)):
        tip = px(R @ (alen * axis) + t)
        ax.add_patch(FancyArrowPatch(o, tip, arrowstyle="-|>", mutation_scale=12,
                                     color=AX_C[k], lw=2.4))
        ax.annotate(k, tip, xytext=(tip[0] + 7, tip[1] - 4), fontsize=10,
                    color=AX_C[k], fontweight="bold")
o_desk, o_obj = px(T_cam_desk[:3, 3]), px(rt_from_row(row, 1)[1])
ax.annotate("world frame $\\mathcal{W}$\n(desk marker, frozen)", o_desk,
            xytext=(o_desk[0] + 95, o_desk[1] + 45), fontsize=9, color="white",
            bbox=dict(boxstyle="round,pad=0.3", fc="black", alpha=0.72),
            arrowprops=dict(arrowstyle="->", color="#ffd60a", lw=1.4))
ax.annotate("object frame $\\mathcal{O}$\n(moves with the cube)", o_obj,
            xytext=(o_obj[0] + 70, o_obj[1] - 55), fontsize=9, color="white",
            bbox=dict(boxstyle="round,pad=0.3", fc="black", alpha=0.72),
            arrowprops=dict(arrowstyle="->", color="#ffd60a", lw=1.4))
cam_xy = (40, 452)
ax.text(*cam_xy, "camera frame $\\mathcal{C}$\n(the viewpoint itself)", fontsize=9,
        color="white", ha="left", va="center",
        bbox=dict(boxstyle="round,pad=0.3", fc="black", alpha=0.72))
dark = dict(boxstyle="round,pad=0.25", fc="black", alpha=0.72)
ax.add_patch(FancyArrowPatch((150, 430), (o_desk[0] - 8, o_desk[1] + 10),
             arrowstyle="-|>", mutation_scale=13, color="#7fd4ff", lw=1.8,
             connectionstyle="arc3,rad=-0.25"))
ax.text(230, 428, "$T^{cam}_{desk}$ (calibrated once)", fontsize=9.5,
        color="#7fd4ff", bbox=dark)
ax.add_patch(FancyArrowPatch((110, 435), (o_obj[0] - 10, o_obj[1] + 12),
             arrowstyle="-|>", mutation_scale=13, color="#ffb3b3", lw=1.8,
             connectionstyle="arc3,rad=0.32"))
ax.text(96, 300, "$T^{cam}_{obj}(t)$\n(each frame)", fontsize=9.5,
        color="#ffb3b3", ha="center", bbox=dark)
ax.add_patch(FancyArrowPatch((o_desk[0] + 6, o_desk[1] - 14), (o_obj[0] + 8, o_obj[1] + 14),
             arrowstyle="-|>", mutation_scale=13, color="#b7ff9e", lw=1.8,
             connectionstyle="arc3,rad=0.25"))
ax.text(o_desk[0] + 62, (o_desk[1] + o_obj[1]) / 2 + 20,
        "$T^{desk}_{obj}(t)=(T^{cam}_{desk})^{-1}\\,T^{cam}_{obj}(t)$",
        fontsize=9.5, color="#b7ff9e", bbox=dark)
plt.tight_layout()
plt.savefig(f"{FIG}/ch4_fig6_frames_photo.png", dpi=200); plt.close()

# ---------------------------------------------------------------- fig 7
shutil.copy(f"{DS}/recording_20260224_083945_object_world_filtered.qc.png",
            f"{FIG}/ch4_fig7_filter_qc.png")

# ---------------------------------------------------------------- fig 8
# the reconstructed scene in the world frame, from the pipeline outputs only
t_cam_w = T_desk_cam[:3, 3]
t_wall_w = T_desk_wall_cal[:3, 3]
R_wall_w = T_desk_wall_cal[:3, :3]
p_obj = filt[["tx", "ty", "tz"]].to_numpy()
tsec = filt.time_s.to_numpy()

fig = plt.figure(figsize=(9.8, 4.5))
ax = fig.add_subplot(121)
ax.set_aspect("equal")
sc = ax.scatter(p_obj[:, 0], p_obj[:, 1], c=tsec, cmap="viridis", s=4)
ax.plot(0, 0, "s", color="#3a7a3a", ms=9)
ax.plot(t_cam_w[0], t_cam_w[1], "^", color="black", ms=10)
ax.plot(t_wall_w[0], t_wall_w[1], "o", color="#a04040", ms=9)
wall_dir = R_wall_w[:2, 0] / np.linalg.norm(R_wall_w[:2, 0])
ax.plot([t_wall_w[0] - 1.1 * wall_dir[0], t_wall_w[0] + 1.1 * wall_dir[0]],
        [t_wall_w[1] - 1.1 * wall_dir[1], t_wall_w[1] + 1.1 * wall_dir[1]],
        color="#a04040", lw=3, alpha=0.45)
ax.annotate("desk marker\n(world origin)", (0, 0), xytext=(0.28, -0.30), fontsize=8.6,
            arrowprops=dict(arrowstyle="->", lw=1.0))
ax.annotate("camera", t_cam_w[:2], xytext=(0.42, -0.75), fontsize=8.6,
            arrowprops=dict(arrowstyle="->", lw=1.0))
ax.annotate("wall marker\n(and wall line)", t_wall_w[:2], xytext=(0.15, 2.30), fontsize=8.6,
            arrowprops=dict(arrowstyle="->", lw=1.0))
ax.text(0.75, 0.62, "carried-object\npath (30 s)", fontsize=8.6)
ax.set_xlabel("world x (m)", fontsize=9); ax.set_ylabel("world y (m)", fontsize=9)
ax.tick_params(labelsize=8.6); ax.grid(alpha=0.25)
ax.set_title("(a) reconstructed scene, top view", fontsize=10)

ax2 = fig.add_subplot(122, projection="3d")
ax2.scatter(p_obj[:, 0], p_obj[:, 1], p_obj[:, 2], c=tsec, cmap="viridis", s=3)
xx, yy = np.meshgrid(np.linspace(-0.25, 0.75, 2), np.linspace(-0.45, 0.75, 2))
ax2.plot_surface(xx, yy, np.full_like(xx, calib["scene_geometry"]["origin_above_tabletop_m"] * -1),
                 alpha=0.18, color="#8a6d1a")
ax2.scatter([0], [0], [0], color="#3a7a3a", s=60, marker="s")
ax2.scatter(*t_cam_w, color="black", s=60, marker="^")
ax2.text(0.03, -0.06, 0.03, "origin", fontsize=8)
ax2.text(t_cam_w[0], t_cam_w[1] - 0.1, t_cam_w[2] + 0.05, "camera", fontsize=8)
ax2.set_xlabel("x (m)", fontsize=8); ax2.set_ylabel("y (m)", fontsize=8)
ax2.set_zlabel("z, out of the desk marker (m)", fontsize=8)
ax2.tick_params(labelsize=7.5)
ax2.set_title("(b) object trajectory over the tabletop plane", fontsize=10)
cb = fig.colorbar(sc, ax=ax2, shrink=0.65, pad=0.12)
cb.set_label("time (s)", fontsize=8.5); cb.ax.tick_params(labelsize=8)
plt.tight_layout()
plt.savefig(f"{FIG}/ch4_fig8_scene_recon.png", dpi=200); plt.close()

print("done:", *[f"ch4_fig{i}" for i in range(1, 9)])

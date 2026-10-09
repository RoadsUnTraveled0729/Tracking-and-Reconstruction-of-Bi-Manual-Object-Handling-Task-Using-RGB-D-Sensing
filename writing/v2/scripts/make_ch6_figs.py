"""Chapter 6 figures.

fig1 scenario timeline computed from the pinned filtered object track
     (height above tabletop, speed, cumulative rotation; phases annotated)
fig2 measured scene layout, side + top view, both camera placements
     (all coordinates from the two pinned scene calibrations)
fig3 copy of the pinned offset-analysis figure (object_offset_analysis.png)
fig4 composed comparison: real color frame 100 vs the integrated Unity still
fig5 occlusion honesty stills, 2x2 grid (held wrist / elbow / hip / pose)
"""
import json
import shutil

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle, Wedge

ROOT = "/home/luo/Desktop/New_SandBox"
OUT = f"{ROOT}/writing/v2/figures"

calib = json.load(open(f"{ROOT}/aruco/dataset/scene_calibration.json"))
calib328 = json.load(open(f"{ROOT}/aruco/dataset/scene_calibration_328.json"))
sg = calib["scene_geometry"]
df = pd.read_csv(
    f"{ROOT}/aruco/dataset/recording_20260224_083945_object_world_filtered.csv")

# ---------------------------------------------------------------- fig 1
p0 = np.asarray(sg["tabletop_point_world"], float)
P = df[["tx", "ty", "tz"]].to_numpy()
t = df["time_s"].to_numpy()
h = (P - p0)[:, 2]                       # along the desk normal (world z)
speed = np.zeros(len(P))
speed[1:] = np.linalg.norm(np.diff(P, axis=0), axis=1) / np.diff(t)
R = df[[f"r{i}{j}" for i in (1, 2, 3) for j in (1, 2, 3)]].to_numpy()
R = R.reshape(-1, 3, 3)
dang = [0.0]
for i in range(1, len(R)):
    d = R[i - 1].T @ R[i]
    dang.append(np.degrees(np.arccos(np.clip((np.trace(d) - 1) / 2, -1, 1))))
cum = np.cumsum(dang)

fig, axes = plt.subplots(3, 1, figsize=(10.5, 7.2), sharex=True)
axes[0].plot(t, 100 * h, color="#2e5e8c", lw=1.2)
axes[0].axhline(3.5, color="#888888", ls="--", lw=0.9)
axes[0].text(29.8, 4.3, "resting: half cube edge (3.5 cm)", fontsize=8,
             ha="right", color="#555555")
axes[0].axvspan(13.4, 23.5, color="#f2e8c8", alpha=0.6)
axes[0].text(18.4, 19.5, "parked on the desk\n(13.4 to 23.5 s)", fontsize=8.5,
             ha="center", color="#7a6a20")
axes[0].set_ylabel("marker height above\ntabletop (cm)")
axes[0].text(4.5, 9.0, "lifted, carried,\nturned", fontsize=8.5, ha="center",
             color="#2e5e8c")
axes[0].text(26.2, 9.0, "picked back up\n(new grip)", fontsize=8.5,
             ha="center", color="#2e5e8c")

axes[1].plot(t, 100 * speed, color="#8c3e2e", lw=1.0)
axes[1].axvspan(13.4, 23.5, color="#f2e8c8", alpha=0.6)
axes[1].set_ylabel("marker speed\n(cm/s)")

axes[2].plot(t, cum, color="#3e7a3e", lw=1.2)
axes[2].axvspan(13.4, 23.5, color="#f2e8c8", alpha=0.6)
axes[2].set_ylabel("cumulative rotation\n(deg)")
axes[2].set_xlabel("time (s)")
axes[2].text(7.0, 400, f"total {cum[-1]:.0f} deg swept,\n"
             "net change 26 deg", fontsize=8.5, ha="center", color="#3e7a3e")
for ax in axes:
    ax.grid(alpha=0.25)
fig.align_ylabels(axes)
fig.tight_layout()
fig.savefig(f"{OUT}/ch6_fig1_timeline.png", dpi=200)
plt.close(fig)

# ---------------------------------------------------------------- fig 2
def cam_world(c):
    T = np.array(c["T_cam_desk"])
    Rm, tr = T[:3, :3], T[:3, 3]
    return -Rm.T @ tr

cam224 = cam_world(calib)
cam328 = cam_world(calib328)
wall = np.array(calib["poses_world"]["wall"]["T_world"])[:3, 3]

fig, (axs, axt) = plt.subplots(1, 2, figsize=(11.2, 5.0))

# side view: world y (toward the wall) vs world z (desk normal, up)
axs.set_title("side view (desk marker frame)", fontsize=10)
axs.add_patch(Rectangle((-0.7, -0.05), 1.5, 0.05, fc="#d9c9a3", ec="#8a7440"))
axs.text(-0.66, -0.16, "desk (top at z = 0)", fontsize=8, color="#8a7440")
axs.add_patch(Rectangle((wall[1], -0.6), 0.06, 2.2, fc="#c9c9d9",
                        ec="#666688"))
axs.text(wall[1] - 0.05, 1.7, "wall", fontsize=8.5, ha="right",
         color="#666688")
axs.plot(0, 0, marker="s", ms=9, color="#b26a00")
axs.text(0.55, 0.04, "desk marker id2\n(50 mm, world origin)", fontsize=8,
         color="#b26a00", va="center")
axs.plot(wall[1], wall[2], marker="s", ms=9, color="#666688")
axs.text(wall[1] - 0.08, wall[2], "wall marker id0\n(150 mm, plumb)",
         fontsize=8, ha="right", color="#666688")
for cam, name, col, tx, ty in (
        (cam224, "camera, recording 224\n(desk edge)", "#2e7d32",
         -0.55, -0.40),
        (cam328, "camera, recording 328\n(high, looking down)", "#b03030",
         -0.36, 0.86)):
    axs.plot(cam[1], cam[2], marker="o", ms=8, color=col)
    axs.text(tx, ty, name, fontsize=8, ha="center", color=col)
    axs.add_patch(FancyArrowPatch((cam[1], cam[2]), (0.35, 0.12),
                                  arrowstyle="-|>", color=col, lw=1.0,
                                  ls=":", mutation_scale=10))
axs.text(1.0, 0.35, "person and cube\nwork here", fontsize=8.5,
         ha="center", style="italic", color="#555555")
axs.set_xlim(-1.1, 3.4); axs.set_ylim(-0.65, 1.9)
axs.set_xlabel("world y toward the wall (m)")
axs.set_ylabel("world z, desk normal (m)")
axs.set_aspect("equal"); axs.grid(alpha=0.25)

# top view: world x vs world y
axt.set_title("top view", fontsize=10)
axt.add_patch(Rectangle((-0.7, -0.7), 1.5, 1.1, fc="#d9c9a3", ec="#8a7440"))
axt.text(-0.62, -0.62, "desk", fontsize=8.5, color="#8a7440")
axt.add_patch(Rectangle((-1.0, wall[1]), 3.0, 0.06, fc="#c9c9d9",
                        ec="#666688"))
axt.plot(0, 0, marker="s", ms=9, color="#b26a00")
axt.plot(wall[0], wall[1], marker="s", ms=9, color="#666688")
axt.text(wall[0], wall[1] - 0.12, "id0", fontsize=8, ha="center",
         color="#666688", va="top")
for cam, name, col in ((cam224, "224", "#2e7d32"), (cam328, "328",
                                                    "#b03030")):
    axt.plot(cam[0], cam[1], marker="o", ms=8, color=col)
    axt.text(cam[0] + 0.09, cam[1], name, fontsize=8.5, color=col,
             va="center")
    w = Wedge((cam[0], cam[1]), 3.6, 90 - 27.8, 90 + 27.8, fc=col, alpha=0.06)
    axt.add_patch(w)
axt.text(0.15, 0.75, "object path\n(1.94 m)", fontsize=8, ha="center",
         color="#2e5e8c")
axt.plot(P[::12, 0], P[::12, 1], ".", ms=2.0, color="#2e5e8c", alpha=0.6)
axt.set_xlim(-1.5, 2.0); axt.set_ylim(-1.0, 3.3)
axt.set_xlabel("world x (m)"); axt.set_ylabel("world y (m)")
axt.set_aspect("equal"); axt.grid(alpha=0.25)

fig.tight_layout()
fig.savefig(f"{OUT}/ch6_fig2_layout.png", dpi=200)
plt.close(fig)

# ---------------------------------------------------------------- fig 3
shutil.copy(f"{ROOT}/integration/dataset/object_offset_analysis.png",
            f"{OUT}/ch6_fig3_offset.png")

# ---------------------------------------------------------------- fig 4
fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.6))
for ax, path, title in (
        (axes[0], f"{ROOT}/integration/dataset/real_color_frame100.png",
         "sensor color image, frame 100"),
        (axes[1], f"{ROOT}/integration/dataset/integrated_still.png",
         "integrated Unity reconstruction (sensor view inset top right)")):
    ax.imshow(mpimg.imread(path))
    ax.set_title(title, fontsize=10)
    ax.axis("off")
fig.tight_layout()
fig.savefig(f"{OUT}/ch6_fig4_compare.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- fig 5
stills = [
    ("held_wrist_hold.png", "right wrist blocked (frames 400 to 444)"),
    ("held_elbow_hold.png", "right elbow blocked (frames 500 to 544)"),
    ("held_hip_hold.png", "left hip blocked (frames 600 to 629)"),
    ("held_pose_loss.png", "whole pose blocked (frames 700 to 709)"),
]
fig, axes = plt.subplots(2, 2, figsize=(10.8, 7.6))
for ax, (fn, title) in zip(axes.flat, stills):
    ax.imshow(mpimg.imread(
        f"{ROOT}/kinematics/dataset/occlusion_masked/{fn}"))
    ax.set_title(title, fontsize=9.5)
    ax.axis("off")
fig.tight_layout()
fig.savefig(f"{OUT}/ch6_fig5_occlusion.png", dpi=200, bbox_inches="tight")
plt.close(fig)

print("ch6 figures written")

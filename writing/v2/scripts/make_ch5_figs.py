"""Chapter 5 figures.

fig1 communication architecture (senders -> shm packets -> Unity receivers)
fig2 the coordinate spaces and the person-to-scene anchor M (real numbers)
fig3 rig hierarchy and per-bone rotation composition
fig4 copy of the pinned plot-first Python preview (scene_preview.png)
fig5 copy of the pinned Pipeline B Unity scene still (real_scene_224_still.png)
fig6 copy of the pinned integrated scene still (integrated_still.png)
"""
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = "/home/luo/Desktop/New_SandBox"
OUT = f"{ROOT}/writing/v2/figures"


def box(ax, x, y, w, h, text, fc="#eef3fb", ec="#3a5a8c", fs=8.6, lw=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25",
                                fc=fc, ec=ec, lw=lw, mutation_scale=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def arrow(ax, p, q, color="#3a5a8c", lw=1.4, style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, color=color,
                                 lw=lw, linestyle=ls, mutation_scale=13,
                                 shrinkA=2, shrinkB=2))


# ---------------------------------------------------------------- fig 1
fig, ax = plt.subplots(figsize=(10.6, 5.6))
ax.set_xlim(0, 100); ax.set_ylim(0, 56); ax.axis("off")

ax.text(13, 54, "Python senders", fontsize=10, ha="center", weight="bold")
ax.text(50, 54, "shared memory channels (/dev/shm)", fontsize=10,
        ha="center", weight="bold")
ax.text(87, 54, "Unity receivers", fontsize=10, ha="center", weight="bold")

lanes = [
    (46, "send_landmarks.py\n(filtered landmark CSV)",
     "pose_stream\nPSE1, 180 B per frame\n8 landmarks, camera frame",
     "PoseStreamReceiver\nlandmark skeleton\n(spheres + bone lines)"),
    (34, "send_arm_angles.py\n(solved joint angles)",
     "arm angle stream\nPSA5, 72 B per frame\n13 angles + live mask",
     "ArmAngleReceiver\ndrives the rig arms\nred markers on held joints"),
    (22, "send_scene_poses.py\n(calibration + filtered\nobject world CSV)",
     "aruco_scene  PSB3, 100 B, once\naruco_object  PSB2, 44 B per frame\npose + live flag",
     "ArucoSceneReceiver\nbuilds the real scene,\nplays the object track"),
    (10, "send_integrated_scene.py\n(both pipelines' outputs)",
     "aruco_scene  PSB3, 100 B, once\nintegrated_scene  PSI1, 108 B\nperson + object in ONE packet",
     "IntegratedSceneReceiver\nscene + anchored person\n(subclass of the scene receiver)"),
]
for y, s, m, r in lanes:
    box(ax, 2, y, 22, 9, s, fc="#eef7ee", ec="#2e7d32")
    box(ax, 36, y, 28, 9, m, fc="#fff8e8", ec="#b26a00")
    box(ax, 76, y, 22, 9, r)
    arrow(ax, (24.6, y + 4.5), (35.4, y + 4.5))
    arrow(ax, (64.6, y + 4.5), (75.4, y + 4.5))

ax.text(50, 4.2,
        "every packet: little-endian, fixed size, 4-byte magic; seqlock for tear-free reads\n"
        "(writer makes the counter odd while writing, even when stable; the reader copies, then re-checks);\n"
        "UDP to 127.0.0.1:9750 as the drop-in alternative transport",
        fontsize=8, ha="center", style="italic", color="#444444")
fig.savefig(f"{OUT}/ch5_fig1_comm.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- fig 2
fig, ax = plt.subplots(figsize=(10.4, 5.4))
ax.set_xlim(0, 100); ax.set_ylim(0, 54); ax.axis("off")

box(ax, 36, 42, 28, 8, "camera frame C\nRGB-D optical frame\n(x right, y down, z forward)",
    fc="#f4f4f4", ec="#555555")
box(ax, 4, 22, 26, 8, "person space (Pipeline A)\nq = F p, F = diag(1, -1, 1)\nlandmarks, joint angles",
    fc="#eef7ee", ec="#2e7d32")
box(ax, 70, 22, 26, 8, "world W (Pipeline B)\ndesk marker frame\nobject track, scene poses",
    fc="#fff8e8", ec="#b26a00")
box(ax, 37, 3, 26, 8, "Unity scene\nleft-handed, y up\np = P p_W (y/z swap)",
    fc="#eef3fb", ec="#3a5a8c")

arrow(ax, (44, 41.4), (20, 30.8), color="#2e7d32")
ax.text(27, 37.5, "F = diag(1, -1, 1)\n(flip y)", fontsize=8.4, color="#2e7d32",
        ha="center")
arrow(ax, (56, 41.4), (80, 30.8), color="#b26a00")
ax.text(74, 37.5, "R_desk_cam, t_desk_cam\n(calibrated camera pose,\nChapter 4)",
        fontsize=8.4, color="#b26a00", ha="center")
arrow(ax, (81, 21.4), (56, 11.4), color="#3a5a8c")
ax.text(74, 15.5, "P (y/z swap)", fontsize=8.4, color="#3a5a8c", ha="center")
arrow(ax, (18, 21.4), (42, 11.4), color="#b03030", lw=2.2)
ax.text(22.5, 14.2, "p_scene = M q + P t_desk_cam\nM = P R_desk_cam F",
        fontsize=9, color="#b03030", ha="center", weight="bold")

ax.text(50, 51.5,
        "det M = (-1)(+1)(-1) = +1: the two handedness flips cancel",
        fontsize=8.6, ha="center", style="italic", color="#444444")
ax.text(4, 3.2,
        "measured anchor (20260224):\n"
        "M = R_Unity(camera) Rx(-90 deg), residual 6e-17\n"
        "anchor Euler (4.5, -1.0, -1.8) deg\n"
        "camera at Unity (0.003, 0.168, -0.567) m",
        fontsize=8.2, ha="left", va="bottom", color="#333333",
        bbox=dict(boxstyle="round", fc="#f8f8f8", ec="#aaaaaa"))
fig.savefig(f"{OUT}/ch5_fig2_anchor.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- fig 3
fig, ax = plt.subplots(figsize=(10.4, 5.8))
ax.set_xlim(0, 100); ax.set_ylim(0, 58); ax.axis("off")

ax.text(20, 56, "rig bone hierarchy (driven bones)", fontsize=10,
        ha="center", weight="bold")
box(ax, 10, 44, 20, 7, "DEF-spine\n(hip / root bone)", fc="#eef3fb")
box(ax, 1, 30, 18, 7, "DEF-upper_arm.R", fc="#eef3fb")
box(ax, 22, 30, 18, 7, "DEF-upper_arm.L", fc="#eef3fb")
box(ax, 1, 16, 18, 7, "DEF-forearm.R", fc="#eef3fb")
box(ax, 22, 16, 18, 7, "DEF-forearm.L", fc="#eef3fb")
arrow(ax, (16, 43.4), (10, 37.8)); arrow(ax, (25, 43.4), (31, 37.8))
arrow(ax, (10, 29.4), (10, 23.8)); arrow(ax, (31, 29.4), (31, 23.8))
ax.text(20, 8.5,
        "below the hips: rest pose (leg landmarks\nare not tracked); root translated each frame\n"
        "to the anchored pelvis point; uniform display\nscale 0.523 (3.25 m rig to a 1.70 m person)",
        fontsize=8.2, ha="center", style="italic", color="#444444")

ax.text(71, 56, "applied world rotation per bone", fontsize=10,
        ha="center", weight="bold")
rows = [
    ("hip", "R_bone = qA . R_root . C_hip"),
    ("upper arm (R)", "R_bone = qA . R_root R_sh . C_ua"),
    ("forearm (R)", "R_bone = qA . R_root R_sh R_el . C_fa"),
]
y = 46
for name, f in rows:
    box(ax, 46, y, 50, 6.5, f"{name}:   {f}", fc="#fff8e8", ec="#b26a00",
        fs=9)
    y -= 10
ax.text(71, 17,
        "C_* = the bone's authored rest rotation, captured once at spawn\n"
        "(absorbs the FBX's own bone axis conventions)\n"
        "R_chain = solved angles assembled in the ZXY-applied order (Chapter 3)\n"
        "qA = the person anchor; identity in the standalone Pipeline A scene",
        fontsize=8.4, ha="center", color="#333333")
ax.text(71, 6,
        "the anchor PRE-multiplies; the conjugation qA R qA' C\n"
        "cancels the anchor out of the pose (Section 5.2.2)",
        fontsize=8.6, ha="center", color="#b03030", style="italic")
fig.savefig(f"{OUT}/ch5_fig3_rig.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- copies
shutil.copy(f"{ROOT}/integration/dataset/scene_preview.png",
            f"{OUT}/ch5_fig4_preview.png")
shutil.copy(f"{ROOT}/aruco/dataset/real_scene_224_still.png",
            f"{OUT}/ch5_fig5_scene_unity.png")
shutil.copy(f"{ROOT}/integration/dataset/integrated_still.png",
            f"{OUT}/ch5_fig6_integrated.png")
print("ch5 figures written")

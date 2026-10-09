#!/usr/bin/env python3
"""Regenerate the frame-derived Chapter 3 figures from the rail-recording pipeline CSV.

V7 rewrite round: the Chapter 3 worked example is pinned to frame 533 of
the rail recording, so every figure
drawn from landmark data comes from the same filtered CSV and the same
frame:
  ch3_fig_torso_photo.png  (input vectors + finished frame on the photo)
  ch3_fig_arm_photo.png    (arm segments on the photo)
  ch3_fig_swing_twist.png  (panel (a) draws the measured frame-533 local
                            arm direction a_hat)
Colour intrinsics come from the rail marker-run metadata. Drawing
code carried from the V6 script.

Run: python writing/v7/scripts/make_ch3_figs.py
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cv2

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "v1" / "kinematics"))
from root_frame import build_root_frame  # noqa: E402

OUT = REPO / "writing" / "v7" / "figures"
FRAME = 533
IMGPATH = OUT / "src" / f"r6b_frame{FRAME:05d}.png"
CSVF = REPO / "v1" / "mediapipe" / "output" / "recording_20260831_065553_landmarks_filtered.csv"
META = REPO / "v1" / "aruco" / "output" / "recording_20260831_065553_aruco_raw.meta.json"

intr = json.loads(META.read_text())["color_intrinsics"]
FX, FY, CX, CY = intr["fx"], intr["fy"], intr["ppx"], intr["ppy"]
F = np.array([1.0, -1.0, 1.0])

names = ["left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
         "left_wrist", "right_wrist", "left_hip", "right_hip"]
with open(CSVF) as f:
    for row in csv.DictReader(f):
        if int(row["frame"]) == FRAME:
            break
P_cam = {n: np.array([float(row[n + "_x"]), float(row[n + "_y"]),
                      float(row[n + "_z"])]) for n in names}
P = {n: F * P_cam[n] for n in names}


def px(p_cam):
    return (int(round(FX * p_cam[0] / p_cam[2] + CX)),
            int(round(FY * p_cam[1] / p_cam[2] + CY)))


def axes3d_clean(ax, lim=1.0):
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)
    ax.set_box_aspect([1, 1, 1])
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
    ax.xaxis.pane.fill = ax.yaxis.pane.fill = ax.zaxis.pane.fill = False


def arrow3(ax, o, d, color, label=None, lw=2.2, ls="-", fs=13):
    ax.quiver(o[0], o[1], o[2], d[0], d[1], d[2], color=color, lw=lw,
              arrow_length_ratio=0.12, linestyle=ls)
    if label:
        e = np.asarray(o) + np.asarray(d) * 1.18
        ax.text(e[0], e[1], e[2], label, color=color, fontsize=fs)

# =====================================================================
# torso frame on the real photo: (a) input vectors, (b) axes
# =====================================================================
img0 = cv2.imread(str(IMGPATH))
assert img0 is not None

imgA = img0.copy()
p24px, p23px, p12px = px(P_cam["right_hip"]), px(P_cam["left_hip"]), px(P_cam["right_shoulder"])
cv2.arrowedLine(imgA, p23px, p24px, (0, 60, 230), 3, cv2.LINE_AA, tipLength=0.09)
cv2.arrowedLine(imgA, p24px, p12px, (30, 200, 255), 3, cv2.LINE_AA, tipLength=0.09)
for p, name in [(p24px, "L24"), (p23px, "L23"), (p12px, "L12")]:
    cv2.circle(imgA, p, 6, (255, 255, 255), -1, cv2.LINE_AA)
    cv2.circle(imgA, p, 6, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(imgA, name, (p[0] + 10, p[1] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (255, 255, 255), 2, cv2.LINE_AA)
cv2.putText(imgA, "hip line p24 - p23", (p24px[0] - 55, p24px[1] + 42),
            cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0, 60, 230), 2, cv2.LINE_AA)
cv2.putText(imgA, "s = p12 - p24", (p12px[0] - 190, p12px[1] - 12),
            cv2.FONT_HERSHEY_SIMPLEX, 0.62, (30, 200, 255), 2, cv2.LINE_AA)

imgB = img0.copy()
p23u, p24u, p12u = P["left_hip"], P["right_hip"], P["right_shoulder"]
r = (p24u - p23u) / np.linalg.norm(p24u - p23u)
s = p12u - p24u
fw = np.cross(r, s); fw /= np.linalg.norm(fw)
up = np.cross(fw, r)
o_cam = P_cam["right_hip"]
for a, col, lbl, dx, dy in [(r, (0, 0, 255), "x (right)", -95, 24),
                            (up, (0, 200, 0), "y (up)", 8, -8),
                            (fw, (255, 80, 0), "z (forward)", 10, 22)]:
    tip_cam = o_cam + 0.30 * (F * a)
    cv2.arrowedLine(imgB, px(o_cam), px(tip_cam), col, 3, cv2.LINE_AA, tipLength=0.12)
    t = px(tip_cam)
    cv2.putText(imgB, lbl, (t[0] + dx, t[1] + dy), cv2.FONT_HERSHEY_SIMPLEX, 0.62, col, 2, cv2.LINE_AA)
cv2.circle(imgB, px(o_cam), 6, (255, 255, 255), -1, cv2.LINE_AA)
cv2.putText(imgB, "origin: L24", (px(o_cam)[0] - 40, px(o_cam)[1] + 46),
            cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2, cv2.LINE_AA)

fig, axs = plt.subplots(1, 2, figsize=(11, 4.3))
axs[0].imshow(cv2.cvtColor(imgA, cv2.COLOR_BGR2RGB)); axs[0].axis("off")
axs[0].set_title("(a) the two input vectors (the worked-example frame)", fontsize=11)
axs[1].imshow(cv2.cvtColor(imgB, cv2.COLOR_BGR2RGB)); axs[1].axis("off")
axs[1].set_title("(b) the finished torso frame projected onto the image", fontsize=11)
plt.tight_layout()
plt.savefig(OUT / "ch3_fig_torso_photo.png", dpi=150, bbox_inches="tight")
plt.close()

# =====================================================================
# arm segments drawn on the real photo (both arms)
# =====================================================================
imgC = img0.copy()
segs = [("right_shoulder", "right_elbow", (0, 140, 255), "R upper arm"),
        ("right_elbow", "right_wrist", (0, 60, 230), "R forearm"),
        ("left_shoulder", "left_elbow", (255, 180, 40), "L upper arm"),
        ("left_elbow", "left_wrist", (230, 90, 0), "L forearm")]
for a, b, col, lbl in segs:
    pa, pb = px(P_cam[a]), px(P_cam[b])
    cv2.arrowedLine(imgC, pa, pb, col, 3, cv2.LINE_AA, tipLength=0.1)
lm = {"right_shoulder": "L12", "right_elbow": "L14", "right_wrist": "L16",
      "left_shoulder": "L11", "left_elbow": "L13", "left_wrist": "L15"}
for n, lbl in lm.items():
    p = px(P_cam[n])
    cv2.circle(imgC, p, 5, (255, 255, 255), -1, cv2.LINE_AA)
    cv2.circle(imgC, p, 5, (0, 0, 0), 1, cv2.LINE_AA)
    dx = -58 if "right" in n else 10
    cv2.putText(imgC, lbl, (p[0] + dx, p[1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (255, 255, 255), 2, cv2.LINE_AA)
cv2.putText(imgC, "subject's RIGHT arm", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
            (0, 140, 255), 2, cv2.LINE_AA)
cv2.putText(imgC, "subject's LEFT arm", (400, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
            (255, 180, 40), 2, cv2.LINE_AA)
cv2.imwrite(str(OUT / "ch3_fig_arm_photo.png"), imgC)

# =====================================================================
# swing-twist schematic; panel (a) draws the measured frame-533 local
# arm direction
# =====================================================================
R_root = build_root_frame(P["left_hip"], P["right_hip"], P["right_shoulder"])
ua = P["right_elbow"] - P["right_shoulder"]
a_hat = R_root.T @ ua
a_hat = a_hat / np.linalg.norm(a_hat)

fig = plt.figure(figsize=(11, 5.0))
ax = fig.add_subplot(1, 2, 1, projection="3d")
axes3d_clean(ax, 1.05)
arrow3(ax, [0, 0, 0], [1.0, 0, 0], "#bbb", None, lw=1.5)
ax.text(1.06, 0, -0.07, "rest arm $+\\hat{x}$", color="#888", fontsize=11)
arrow3(ax, [0, 0, 0], [0, 1.0, 0], "royalblue", "z", lw=1.5)
arrow3(ax, [0, 0, 0], [0, 0, 1.0], "green", "y", lw=1.5)
a_plot = np.array([a_hat[0], a_hat[2], a_hat[1]])    # plot basis (x, z, y-up)
arrow3(ax, [0, 0, 0], a_plot, "crimson", None, lw=2.6)
ax.text(a_plot[0] + 0.05, a_plot[1] + 0.05, a_plot[2] - 0.25,
        "$\\hat{a}$ observed\nupper arm", color="crimson", fontsize=11)
th = np.linspace(0, 1, 40)
arc = np.array([(1 - t) * np.array([0.55, 0, 0]) + t * 0.55 * a_plot for t in th])
arc = 0.55 * arc / np.linalg.norm(arc, axis=1, keepdims=True)
ax.plot(arc[:, 0], arc[:, 1], arc[:, 2], color="purple", lw=2, ls="--")
ax.text(0.42, 0.1, -0.42, "swing $R_y(\\theta_y)R_z(\\theta_z)$", color="purple", fontsize=11)
ax.set_title("(a) swing aims the arm; $\\hat{a}=(c_yc_z,\\ s_z,\\ -s_yc_z)$", fontsize=11)
ax.view_init(elev=16, azim=-48)

ax = fig.add_subplot(1, 2, 2, projection="3d")
axes3d_clean(ax, 1.05)
arrow3(ax, [-0.6, 0, 0], [1.5, 0, 0], "crimson", None, lw=2.6)
tt = np.linspace(0, 2 * np.pi, 60)
ax.plot(0.55 * np.ones_like(tt), 0.52 * np.cos(tt), 0.52 * np.sin(tt),
        color="purple", lw=1.6, ls=":")
arrow3(ax, [0.55, 0, 0], [0, 0.52, 0], "royalblue", None, lw=2.2)
tw = np.radians(38)
arrow3(ax, [0.55, 0, 0], [0, 0.52 * np.cos(tw), -0.52 * np.sin(tw)], "darkorange", None, lw=2.2)
ys, zs = np.meshgrid(np.linspace(-0.62, 0.62, 2), np.linspace(-0.62, 0.62, 2))
ax.plot_surface(0.55 * np.ones_like(ys), ys, zs, alpha=0.12, color="gray")
ax.view_init(elev=14, azim=-55)
ax.set_title("(b) twist $R_x(\\theta_t)$ rolls about the arm axis", fontsize=11)
ax.text2D(0.02, 0.92, "arm axis (un-swung back to $+\\hat{x}$)", color="crimson",
          fontsize=10, transform=ax.transAxes)
ax.text2D(0.02, 0.84, "$+\\hat{z}$: zero-twist forearm direction\n(elbow flexes forward)",
          color="royalblue", fontsize=10, transform=ax.transAxes)
ax.text2D(0.02, 0.72, "twisted forearm $\\perp$ component", color="darkorange",
          fontsize=10, transform=ax.transAxes)
ax.text2D(0.02, 0.06, "gray: y-z plane $\\perp$ to the axis, where the twist is read:\n"
          "$\\theta_t=\\mathrm{atan2}(-f'_y,\\ f'_z)$", fontsize=10, transform=ax.transAxes)
plt.tight_layout()
plt.savefig(OUT / "ch3_fig_swing_twist.png", dpi=150, bbox_inches="tight")
plt.close()

print("a_hat drawn:", np.round(a_hat, 4))
print("saved ch3 torso/arm/swing-twist figures to", OUT)

#!/usr/bin/env python3
"""D-085: condensed-local Figure 3.7 generator with clear lower legend.

Copied data preparation, plot helpers and swing-twist construction from
writing/v7/scripts/make_ch3_figs.py. The lower legend and two panel (a)
text anchors move to clear the plot borders.
The shared V7/V8 assets and original generator remain unchanged. Frame 533,
its root/arm calculation, plot vectors, view angles and illustrative twist
angle are the original values. No photographic figures are generated here.
"""
import csv
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "v1" / "kinematics"))
from root_frame import build_root_frame

OUT = REPO / "writing" / "v8" / "condensed" / "figures"
FRAME = 533
CSVF = REPO / "v1" / "mediapipe" / "output" / "recording_20260831_065553_landmarks_filtered.csv"
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

R_root = build_root_frame(P["left_hip"], P["right_hip"], P["right_shoulder"])
ua = P["right_elbow"] - P["right_shoulder"]
a_hat = R_root.T @ ua
a_hat = a_hat / np.linalg.norm(a_hat)

fig = plt.figure(figsize=(11, 5.0))
ax = fig.add_subplot(1, 2, 1, projection="3d")
axes3d_clean(ax, 1.05)
arrow3(ax, [0, 0, 0], [1.0, 0, 0], "#bbb", None, lw=1.5)
# D-085: keep this text inside the plot border and above its vector.
ax.text(0.66, 0, 0.15, "rest arm $+\\hat{x}$", color="#888", fontsize=11)
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
# D-085: move the complete operator label left of the right plot border.
ax.text(0.04, 0.1, -0.78, "swing $R_y(\\theta_y)R_z(\\theta_z)$", color="purple", fontsize=11)
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
# D-085: place the two-line legend below the plotted axes instead of across them.
ax.text2D(0.02, -0.06, "gray: y-z plane $\\perp$ to the axis, where the twist is read:\n"
          "$\\theta_t=\\mathrm{atan2}(-f'_y,\\ f'_z)$", fontsize=10, transform=ax.transAxes)
plt.tight_layout()
plt.savefig(OUT / "ch3_fig_swing_twist.png", dpi=150, bbox_inches="tight")
plt.close()

print("a_hat drawn:", np.round(a_hat, 4))
print("saved", OUT / "ch3_fig_swing_twist.png")

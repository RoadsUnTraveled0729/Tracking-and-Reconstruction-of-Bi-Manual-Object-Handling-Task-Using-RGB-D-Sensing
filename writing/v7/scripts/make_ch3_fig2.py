#!/usr/bin/env python3
"""Regenerate the co-located-frames figure with the rail frame-533 wrist.

V7 rewrite round: the Chapter 3 worked example is pinned to frame 533 of
the rail recording, and this figure prints the same wrist
coordinates as Table 3.1. Drawing code carried from the V6 script.

Output: writing/v7/figures/ch3_fig_colocated.png
Run:    python writing/v7/scripts/make_ch3_fig2.py
"""
import csv
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "writing" / "v7" / "figures" / "ch3_fig_colocated.png"
CSVF = REPO / "v1" / "mediapipe" / "output" / "recording_20260831_065553_landmarks_filtered.csv"
FRAME = 533

with open(CSVF) as f:
    for row in csv.DictReader(f):
        if int(row["frame"]) == FRAME:
            break
w_cam = np.array([float(row["right_wrist_x"]), float(row["right_wrist_y"]),
                  float(row["right_wrist_z"])])


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


fig = plt.figure(figsize=(7.2, 6.0))
ax = fig.add_subplot(projection="3d")
axes3d_clean(ax, 1.05)
arrow3(ax, [0, 0, 0], [0.95, 0, 0], "crimson", "x  (same in $\\mathcal{C}$ and $\\mathcal{P}$)")
arrow3(ax, [0, 0, 0], [0, 0.95, 0], "royalblue", "z  (same in $\\mathcal{C}$ and $\\mathcal{P}$, depth)")
arrow3(ax, [0, 0, 0], [0, 0, -0.95], "green", "y of camera frame $\\mathcal{C}$ (down)")
arrow3(ax, [0, 0, 0], [0, 0, 0.95], "darkorange", "y of person space $\\mathcal{P}$ (up)", ls="--")
scale = 0.75 / w_cam[2]
pt = np.array([w_cam[0], w_cam[2], -w_cam[1]]) * scale   # plot basis: (x, z, physical up)
ax.scatter(*pt, color="purple", s=55)
ax.text(pt[0] - 1.35, pt[1], pt[2] + 0.28,
        "ONE physical wrist point (the worked-example frame):\n"
        "read in camera frame $\\mathcal{C}$: (%+.2f, %+.2f, %.2f)\n"
        "read in person space $\\mathcal{P}$: (%+.2f, %+.2f, %.2f)"
        % (w_cam[0], w_cam[1], w_cam[2], w_cam[0], -w_cam[1], w_cam[2]),
        color="purple", fontsize=10)
ax.plot([pt[0], pt[0]], [pt[1], pt[1]], [0, pt[2]], color="gray", ls=":", lw=1.2)
ax.scatter([0], [0], [0], color="black", s=40)
ax.text(0.05, 0.02, -0.22, "one shared origin\n(the optical centre)", fontsize=10)
ax.set_title("Camera frame $\\mathcal{C}$ and person space $\\mathcal{P}=F\\,\\mathcal{C}$,"
             " $F=\\mathrm{diag}(1,-1,1)$: only y flips", fontsize=11)
ax.view_init(elev=18, azim=-55)
plt.tight_layout()
plt.savefig(OUT, dpi=150, bbox_inches="tight")
plt.close()
print("saved", OUT, "| wrist cam:", np.round(w_cam, 4))

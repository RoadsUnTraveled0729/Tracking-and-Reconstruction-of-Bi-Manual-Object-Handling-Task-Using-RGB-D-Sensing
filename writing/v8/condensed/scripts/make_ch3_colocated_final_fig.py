# D-073: local copy of frozen V7 generator; numbers and point geometry unchanged.
#!/usr/bin/env python3
"""Regenerate the co-located-frames figure with the rail frame-533 wrist.

V7 rewrite round: the Chapter 3 worked example is pinned to frame 533 of
the rail recording, and this figure prints the same wrist
coordinates as Table 3.1. Drawing code carried from the V6 script.

Output: writing/v8/condensed/figures/ch3_fig_colocated.png
Run:    python writing/v8/condensed/scripts/make_ch3_colocated_final_fig.py
"""
import csv
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[4]
OUT = REPO / "writing" / "v8" / "condensed" / "figures" / "ch3_fig_colocated.png"
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
arrow3(ax, [0, 0, 0], [0.95, 0, 0], "crimson", "x (both)", fs=11)
arrow3(ax, [0, 0, 0], [0, 0.95, 0], "royalblue", "z (both, depth)", fs=11)
arrow3(ax, [0, 0, 0], [0, 0, -0.95], "green", "Camera y (down)", fs=11)
arrow3(ax, [0, 0, 0], [0, 0, 0.95], "darkorange", "Camera' y (up)", ls="--", fs=11)
scale = 0.75 / w_cam[2]
pt = np.array([w_cam[0], w_cam[2], -w_cam[1]]) * scale   # plot basis: (x, z, physical up)
ax.scatter(*pt, color="purple", s=55)
ax.text2D(0.01, 0.93,
        "One physical wrist point (worked-example frame):\n"
        "Camera: (%+.2f, %+.2f, %.2f) m\n"
        "Camera': (%+.2f, %+.2f, %.2f) m"
        % (w_cam[0], w_cam[1], w_cam[2], w_cam[0], -w_cam[1], w_cam[2]),
        transform=ax.transAxes, color="purple", fontsize=10, va="top")
ax.plot([pt[0], pt[0]], [pt[1], pt[1]], [0, pt[2]], color="gray", ls=":", lw=1.2)
ax.scatter([0], [0], [0], color="black", s=40)
ax.text2D(0.08, 0.43, "one shared origin\n(the optical centre)",
          transform=ax.transAxes, fontsize=10)
ax.set_title("Raw camera frame {Camera} and y-up camera frame {Camera'}\n"
             "Same optical origin; Camera' is not person-centred", fontsize=11)
ax.text2D(0.02, 0.02, r"$F=\mathrm{diag}(1,-1,1)$: only y changes sign",
          transform=ax.transAxes, fontsize=10)
ax.view_init(elev=18, azim=-55)
plt.tight_layout()
plt.savefig(OUT, dpi=150, bbox_inches="tight")
plt.close()
print("saved", OUT, "| wrist cam:", np.round(w_cam, 4))

#!/usr/bin/env python3
"""Chapter 2 experimental-setup figure (supervisor round 2026-08-03).

Annotates the pinned real colour frame (frame 100 of the evaluation
recording) with the elements of the physical setup: the three ArUco
markers (outlines projected through the pipeline's own frame-100 poses
and the real colour intrinsics), the desk, the person, and the carried
cube. Output: writing/v4/figures/ch2_fig_setup.png. Nothing is invented;
marker outlines come from aruco/dataset artifacts.
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Polygon

ROOT = "/home/luo/Desktop/New_SandBox"
sys.path.insert(0, f"{ROOT}/v1/aruco")
from frames import rt_from_row

FRAME = 100
FX, FY, CX, CY = 607.5626, 607.0234, 323.9403, 248.0233

raw = pd.read_csv(f"{ROOT}/v1/aruco/dataset/recording_20260224_083945_aruco_raw.csv")
row = raw[raw.frame == FRAME].iloc[0]
IMG = plt.imread(f"{ROOT}/v1/integration/dataset/real_color_frame100.png")


def px(p):
    return FX * p[0] / p[2] + CX, FY * p[1] / p[2] + CY


SIZES = {0: 0.150, 2: 0.050, 1: 0.050}
labels = {0: "wall marker (id 0)\n150 mm, assumed plumb", 2: "desk marker (id 2)\n50 mm, world anchor",
          1: "object marker (id 1)\non the 70 mm cube"}
off = {0: (-330, 60), 2: (90, -50), 1: (70, 60)}

fig, ax = plt.subplots(figsize=(8.4, 6.3))
ax.imshow(IMG)
ax.axis("off")

for mid in (0, 2, 1):
    R, t = rt_from_row(row, mid)
    L = SIZES[mid] / 2
    q = np.array([px(R @ np.array([sx * L, sy * L, 0.0]) + t)
                  for sx, sy in [(-1, 1), (1, 1), (1, -1), (-1, -1)]])
    ax.add_patch(Polygon(q, closed=True, fill=False, ec="#ffd60a", lw=2.2))
    cen = q.mean(axis=0)
    dx, dy = off[mid]
    ax.annotate(labels[mid], xy=cen, xytext=(cen[0] + dx, cen[1] + dy),
                fontsize=9, color="white", ha="left", va="center",
                bbox=dict(boxstyle="round,pad=0.3", fc="black", alpha=0.72),
                arrowprops=dict(arrowstyle="->", color="#ffd60a", lw=1.6))

# scene callouts (person, desk, camera viewpoint note)
ax.annotate("person at the desk,\ncarrying the cube", xy=(255, 90), xytext=(45, 65),
            fontsize=9, color="white", ha="left", va="center",
            bbox=dict(boxstyle="round,pad=0.3", fc="black", alpha=0.72),
            arrowprops=dict(arrowstyle="->", color="white", lw=1.4))
ax.annotate("desk surface", xy=(210, 455), xytext=(40, 350),
            fontsize=9, color="white", ha="left", va="center",
            bbox=dict(boxstyle="round,pad=0.3", fc="black", alpha=0.72),
            arrowprops=dict(arrowstyle="->", color="white", lw=1.4))
ax.text(8, 470, "view from the RGB-D camera at the desk edge, chest height, 1.5 to 2 m from the person",
        fontsize=8.5, color="white",
        bbox=dict(boxstyle="round,pad=0.3", fc="black", alpha=0.72))

plt.tight_layout()
out = f"{ROOT}/writing/v6/figures/ch2_fig_setup.png"
plt.savefig(out, dpi=200)
print("saved", out)

#!/usr/bin/env python3
"""Chapter 2 system-flow figure (V7 rewrite round).

The V6 flow diagram redrawn against the V7 chapter structure: the
kinematic solve feeds the pose recovery stage (the new Chapter 5),
which is conditioned on the object track; the combined record streams
into Unity in Chapter 6. Layout carried from the V6 script.

Output: writing/v7/figures/ch2_fig_flow.png
Run:    python writing/v7/scripts/make_ch2_fig1.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "writing" / "v7" / "figures" / "ch2_fig_flow.png"


def box(ax, x, y, w, h, text, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012",
                                fc=fc, ec="0.25", lw=1.1))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=8.4)


def arrow(ax, x0, y0, x1, y1, text=None):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=13, color="0.2", lw=1.2))
    if text:
        ax.text((x0+x1)/2 + 0.005, (y0+y1)/2, text, fontsize=7.3,
                color="0.25", ha="left")


fig, ax = plt.subplots(figsize=(10.5, 5.6))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
C_SENS, C_A, C_B, C_F = "#dbe9f6", "#e3f2df", "#fdeeda", "#ece1f2"

box(ax, 0.01, 0.42, 0.14, 0.16, "RealSense D435\nrecording, 640x480\nat 30 fps (Chapter 2)", C_SENS)
box(ax, 0.19, 0.42, 0.14, 0.16, "Frame replay +\ndepth-to-color\nalignment (Chapter 2)", C_SENS)

box(ax, 0.37, 0.68, 0.14, 0.15, "MediaPipe Pose,\n8 landmarks +\nvisibility (Chapter 2)", C_A)
box(ax, 0.54, 0.68, 0.13, 0.15, "Depth fusion +\ngating + filter\n(Chapter 2)", C_A)
box(ax, 0.70, 0.68, 0.13, 0.15, "Kinematic solver,\njoint angles\n(Chapter 3)", C_A)
box(ax, 0.86, 0.68, 0.13, 0.15, "Pose recovery on\ntracking failure\n(Chapter 5)", C_A)

box(ax, 0.37, 0.17, 0.14, 0.15, "ArUco detection,\nplanar pose per\nmarker (Chapter 2)", C_B)
box(ax, 0.54, 0.17, 0.13, 0.15, "Scene calibration\n+ world anchoring\n(Chapter 4)", C_B)
box(ax, 0.70, 0.17, 0.13, 0.15, "Object track\ncleaning, world\nframe (Chapter 4)", C_B)

box(ax, 0.70, 0.42, 0.12, 0.15, "Streaming,\nshared frame index\n(Chapter 6)", C_F)
box(ax, 0.86, 0.42, 0.13, 0.15, "Unity avatar and\nscene (Chapter 6)", C_F)

arrow(ax, 0.15, 0.50, 0.19, 0.50)
arrow(ax, 0.33, 0.53, 0.37, 0.74, "color + depth")
arrow(ax, 0.33, 0.47, 0.37, 0.26, "color")
arrow(ax, 0.51, 0.755, 0.54, 0.755)
arrow(ax, 0.67, 0.755, 0.70, 0.755)
arrow(ax, 0.83, 0.755, 0.86, 0.755)
arrow(ax, 0.51, 0.245, 0.54, 0.245)
arrow(ax, 0.67, 0.245, 0.70, 0.245)
# the object track conditions the recovery, and both streams feed Unity
arrow(ax, 0.835, 0.30, 0.905, 0.68)
ax.text(0.906, 0.615, "object pose", fontsize=7.3, color="0.25", ha="left")
arrow(ax, 0.925, 0.68, 0.80, 0.57)
arrow(ax, 0.765, 0.32, 0.765, 0.42)
arrow(ax, 0.82, 0.495, 0.86, 0.495)
ax.text(0.79, 0.62, "shared memory / UDP (Chapter 6)", fontsize=7.3,
        color="0.25", ha="right")
ax.text(0.01, 0.30, "Chapter 7 evaluates the reconstruction against\n"
                    "the designed object path; Chapter 8 examines\n"
                    "a real-time variant of this whole flow.",
        fontsize=8.2, color="0.3", style="italic", va="top")
ax.text(0.45, 0.93, "Pipeline A: person tracking", fontsize=9.5, color="#3a6b35")
ax.text(0.45, 0.055, "Pipeline B: scene and object tracking", fontsize=9.5, color="#8a5a1e")
plt.tight_layout()
plt.savefig(OUT, dpi=150)
print("saved", OUT)

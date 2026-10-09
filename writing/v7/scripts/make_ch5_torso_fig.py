#!/usr/bin/env python3
"""Chapter 5 figure: the torso repair on camera rays.

A wrong depth sample slides a torso landmark along its own camera ray
while the pixel it came from stays correct, so the repair puts the
landmark back on that ray at its remembered depth.

Sign of the corruption: the sample comes off a surface in front of the
trunk (the hand, the carried object, the desk edge), so the landmark
lands nearer the camera than the body. Absolute depth does not settle
that on its own, because the participant also stands back at times and
carries both hips farther away; referenced to the shoulder-midpoint
depth, which cancels the standing distance, the more-deviant hip is
nearer on 98 percent of the R5 torso failure frames.

The worst torso window on R5 is frames 1182-1544, and the RIGHT hip is
the corrupt one there: its depth falls to 1.02 m against a right-hip
clean median of 1.41 m over the manipulation phase, frames 656-1983.
The left hip's own low of 1.10 m belongs to the earlier window,
frames 956-1130. Over the torso failure frames the more-deviant hip
sits a median 0.30 m nearer than its clean value. Panel (a) therefore
draws the right hip as the corrupt one, and both panels carry that
sign.

Numbers from v1/mediapipe/output/recording_20260825_222315_landmarks_raw.csv
with the torso mask of eval/failure/detect_failures.py
(eval/output/recovery_r5/failure_mask.csv, column fail_torso).

The main panel is a top-down view of the camera and the two hips,
which is where the whole construction lives (the ray, the depth, the
repaired point). The small
panel beside it shows the depth-jump gate that decides when a landmark
is repaired at all; its trace is drawn, not measured, so the panel is
labelled a schematic in its title, its axis and the chapter caption.

Output: writing/v7/figures/ch5_fig_torso.png
Run:    python writing/v7/scripts/make_ch5_torso_fig.py
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "writing" / "v7" / "figures" / "ch5_fig_torso.png"

C_INK = "#22223b"
C_GOOD = "#1a7f5a"
C_BAD = "#c1121f"
C_RAY = "#8d99ae"
C_MEM = "#e07a1f"
C_BLUE = "#1d6fb8"

fig = plt.figure(figsize=(11.0, 5.0))

# ---------------------------------------------------------------- (a)
ax = fig.add_axes([0.02, 0.05, 0.60, 0.88])
ax.set_aspect("equal")
ax.axis("off")
ax.set_xlim(-1.02, 1.10)
ax.set_ylim(-0.30, 2.66)

cam = np.array([0.0, 0.0])

# camera body
ax.add_patch(Rectangle((-0.12, -0.16), 0.24, 0.16, fc="#dee2e6",
                       ec=C_INK, lw=1.4, zorder=6))
ax.plot([-0.05, 0.0], [0.0, 0.0], color=C_INK, lw=3.0, zorder=7)
ax.text(0.0, -0.22, "camera", fontsize=11.5, color=C_INK, ha="center",
        va="top")

# the two hip landmarks: the pixel directions (the rays) stay correct
d_left = np.array([-0.300, 1.0])
d_right = np.array([0.135, 1.0])
z_true = 1.72
z_mem = 1.72
z_bad = 1.30          # the corrupt sample lands nearer the camera

pL_true = d_left * z_true
pR_fix = d_right * z_mem
pR_bad = d_right * z_bad

# rays
for d in (d_left, d_right):
    end = d * 2.56
    ax.plot([cam[0], end[0]], [cam[1], end[1]], color=C_RAY, lw=1.3,
            ls=(0, (5, 4)), zorder=2)
ax.text(*(d_left * 2.30 + np.array([-0.07, 0.0])),
        "the camera ray\nthrough the pixel", fontsize=10.5, color=C_RAY,
        ha="right", va="center")

# remembered-depth line (a plane of constant depth, seen edge on)
ax.plot([-0.86, 0.62], [z_mem, z_mem], color=C_MEM, lw=1.6,
        ls=(0, (1, 2.4)), zorder=3)
ax.text(-0.90, z_mem, "remembered\ndepth", fontsize=10.5, color=C_MEM,
        ha="right", va="center")

# the corrupt sample and the slide back along the ray
ax.add_patch(FancyArrowPatch(tuple(pR_bad), tuple(pR_fix - d_right * 0.06),
                             arrowstyle="-|>", mutation_scale=15,
                             color=C_GOOD, lw=2.2, zorder=8))
ax.text(*(0.5 * (pR_bad + pR_fix) + np.array([0.11, 0.07])),
        "put back on\nits own ray", fontsize=10.5, color=C_GOOD,
        ha="left", va="center")

# rebuilt hip line
ax.plot([pL_true[0], pR_fix[0]], [pL_true[1], pR_fix[1]], color=C_BLUE,
        lw=3.4, zorder=7, solid_capstyle="round")
ax.text(pL_true[0] - 0.06, pL_true[1] - 0.22,
        "the hip line, rebuilt", fontsize=11.5, color=C_BLUE,
        ha="right", va="center")

# points
ax.scatter(*pL_true, s=100, c=[C_INK], edgecolors="white", linewidths=1.4,
           zorder=10)
ax.scatter(*pR_bad, s=100, c=[C_BAD], edgecolors="white", linewidths=1.4,
           zorder=10)
ax.scatter(*pR_fix, s=112, c=[C_GOOD], edgecolors="white", linewidths=1.4,
           zorder=11)

ax.text(pL_true[0] - 0.10, pL_true[1] + 0.30, "the hip that\nstayed correct",
        fontsize=11, color=C_INK, ha="right", va="center")
ax.text(pR_bad[0] + 0.15, pR_bad[1] - 0.10,
        "the other hip, its depth taken\noff a nearer surface, so it sits\n"
        "in front of the body",
        fontsize=11, color=C_BAD, ha="left", va="center")
ax.text(pR_fix[0] + 0.14, pR_fix[1] + 0.16, "repaired hip",
        fontsize=11, color=C_GOOD, ha="left", va="center")

ax.set_title("(a) A wrong depth moves the landmark along its ray, "
             "and only along its ray",
             fontsize=12, color=C_INK, y=0.99)

# ---------------------------------------------------------------- (b)
axb = fig.add_axes([0.685, 0.20, 0.29, 0.58])
n = 90
f = np.arange(n)
# a drawn illustration of the gate, not a recorded depth trace
depth = 1.80 + 0.012 * np.sin(f / 7.0) + 0.004 * np.cos(f / 2.3)
depth[52:74] -= 0.24
mem = np.full(n, 1.80)

axb.fill_between(f, mem - 0.10, mem + 0.10, color=C_MEM, alpha=0.16,
                 lw=0)
axb.plot(f, mem, color=C_MEM, lw=1.8)
axb.plot(f, depth, color=C_INK, lw=1.8)
axb.plot(f[52:74], depth[52:74], color=C_BAD, lw=2.6)

axb.text(4, 1.80 + 0.115, "remembered depth,\nwith the allowed band",
         fontsize=9.6, color=C_MEM, ha="left", va="bottom")
axb.text(63, 1.545, "outside the band, toward\nthe camera: the landmark\nis repaired",
         fontsize=9.6, color=C_BAD, ha="center", va="top")

axb.set_xlim(0, n - 1)
axb.set_ylim(1.40, 2.06)
axb.set_xlabel("frame", fontsize=10.5, color=C_INK)
axb.set_ylabel("depth (m), schematic", fontsize=10.5, color=C_INK)
axb.tick_params(labelsize=9.5, colors=C_INK)
for s in ("top", "right"):
    axb.spines[s].set_visible(False)
for s in ("left", "bottom"):
    axb.spines[s].set_color(C_INK)
axb.set_title("(b) The depth-jump gate (schematic)", fontsize=12,
              color=C_INK)

fig.savefig(OUT, dpi=200, facecolor="white")
print("saved", OUT)

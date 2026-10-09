#!/usr/bin/env python3
"""Chapter 6 coordinate-conversion figure (V7 rewrite round).

One panel showing the four frames the integration layer works with and
the three maps between them: the camera frame and the person space of
Chapter 3 (joined by the y flip), the desk world of Chapter 4 and the
Unity scene frame (joined by the y/z swap), and the anchor that carries
person space into the Unity scene. Handedness is labelled on every
frame, because each single map flips it and the anchor composes two.

Sources: v1/KINEMATIC_MODEL.md section 3 (the flip), v1/ARUCO_MODEL.md
section 5 (the swap), v1/INTEGRATION.md section 1 (the anchor),
Unity/Assets/Scripts/IntegratedSceneReceiverV2.cs (how the receiver
builds the anchor node).

Output: writing/v7/figures/ch6_fig_frames.png
Run:    python writing/v7/scripts/make_ch6_frames_fig.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "writing" / "v7" / "figures" / "ch6_fig_frames.png"

CX, CY, CZ = "#c0392b", "#1e8449", "#1f4e99"
L = 0.052          # triad arm length in axes units


def triad(ax, cx, cy, ydir, zsym, labels=("x", "y", "z")):
    """Axis triad: x to the right, y up or down, z through the page."""
    ax.add_patch(FancyArrowPatch((cx, cy), (cx + L, cy), arrowstyle="-|>",
                                 mutation_scale=10, color=CX, lw=1.6))
    ax.text(cx + L + 0.008, cy, labels[0], color=CX, fontsize=8.4,
            va="center")
    ax.add_patch(FancyArrowPatch((cx, cy), (cx, cy + ydir * L * 1.35),
                                 arrowstyle="-|>", mutation_scale=10,
                                 color=CY, lw=1.6))
    ax.text(cx + 0.006, cy + ydir * L * 1.5, labels[1], color=CY,
            fontsize=8.4, ha="left", va="center")
    # z through the page: circle with a cross (away) or a dot (toward)
    ax.add_patch(Circle((cx - 0.030, cy - 0.030), 0.011, fc="white",
                        ec=CZ, lw=1.4, zorder=3))
    if zsym == "away":
        ax.plot([cx - 0.038, cx - 0.022], [cy - 0.038, cy - 0.022],
                color=CZ, lw=1.2, zorder=4)
        ax.plot([cx - 0.038, cx - 0.022], [cy - 0.022, cy - 0.038],
                color=CZ, lw=1.2, zorder=4)
    else:
        ax.add_patch(Circle((cx - 0.030, cy - 0.030), 0.0032, fc=CZ,
                            ec=CZ, zorder=4))
    ax.text(cx - 0.048, cy - 0.030, labels[2], color=CZ, fontsize=8.4,
            ha="right", va="center")


def frame_box(ax, x, y, w, h, title, sub, hand, cx, cy, ydir, zsym, labels):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012",
                                fc="#f7f7fa", ec="0.35", lw=1.1))
    ax.text(x + w / 2, y + h - 0.045, title, ha="center", va="center",
            fontsize=9.2)
    ax.text(x + w / 2, y + h - 0.095, sub, ha="center", va="center",
            fontsize=7.8, color="0.35")
    ax.text(x + w / 2, y + 0.035, hand, ha="center", va="center",
            fontsize=8.2, style="italic", color="0.25")
    triad(ax, cx, cy, ydir, zsym, labels)


def arrow(ax, x0, y0, x1, y1, rad=0.0):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=14, color="0.2", lw=1.5,
                                 connectionstyle=f"arc3,rad={rad}"))


fig, ax = plt.subplots(figsize=(10.6, 5.4))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

BW, BH = 0.235, 0.345

# camera frame -> person space (Pipeline A)
frame_box(ax, 0.02, 0.60, BW, BH, "Camera frame",
          "where every measurement starts", "right-handed",
          0.115, 0.755, -1, "away", ("x right", "y down", "z depth"))
frame_box(ax, 0.35, 0.60, BW, BH, "Person space",
          "where the kinematic model works", "left-handed",
          0.445, 0.700, +1, "away", ("x right", "y up", "z depth"))

# desk world -> Unity scene (Pipeline B)
frame_box(ax, 0.02, 0.05, BW, BH, "Desk world",
          "where the object track lives", "right-handed",
          0.115, 0.150, +1, "away", ("x right", "z out of\nthe marker",
                                     "y"))
frame_box(ax, 0.70, 0.325, BW, BH, "Unity scene",
          "where everything is drawn", "left-handed",
          0.795, 0.425, +1, "away", ("x right", "y up", "z forward"))

BB = dict(fc="white", ec="none", pad=1.6)

arrow(ax, 0.265, 0.775, 0.345, 0.775)
ax.text(0.305, 0.860, "flip\nthe y axis", ha="center", fontsize=8.6,
        bbox=BB)
ax.text(0.305, 0.700, "one axis\nreversed", ha="center", fontsize=7.6,
        color="0.35", bbox=BB)

arrow(ax, 0.598, 0.680, 0.695, 0.560, rad=-0.12)
ax.text(0.648, 0.880, "anchor: undo the flip, rotate into\nthe world by the "
                      "calibrated camera\npose, then swap",
        ha="left", va="center", fontsize=8.4, bbox=BB)

arrow(ax, 0.265, 0.225, 0.695, 0.425, rad=-0.10)
ax.text(0.470, 0.330, "swap the second and third axes", ha="center",
        fontsize=8.6, bbox=BB)
ax.text(0.470, 0.288, "one axis pair exchanged", ha="center", fontsize=7.6,
        color="0.35", bbox=BB)

ax.text(0.02, 0.978,
        "Each single map reverses handedness once; the anchor composes two "
        "of them, so it is a plain rotation and the person is not mirrored.",
        fontsize=8.6, color="0.2", ha="left")
ax.text(0.70, 0.275,
        "The whole scene is then rotated so that\nthe measured gravity "
        "direction becomes\nthe screen's vertical.",
        fontsize=7.9, color="0.35", ha="left", va="top")

plt.tight_layout()
plt.savefig(OUT, dpi=150)
print("saved", OUT)

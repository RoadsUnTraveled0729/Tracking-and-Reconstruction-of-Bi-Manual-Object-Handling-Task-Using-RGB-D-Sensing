#!/usr/bin/env python3
"""Draw Figure 3.4 as the D-080 illustrative torso construction.

The subject faces the viewer: right hip L24 and right shoulder L12 are
on the viewer's left; left hip L23 is on the viewer's right. Panel (a)
draws the hip vector L23 -> L24 and s = L12 - L24. Panel (b) places every
root axis at L24: x toward subject right, y up the trunk, and z out of
the chest toward the viewer, represented by a dot in a circle.

All drawing coordinates, sizes and colours are illustration layout under
D-080. No photographic landmarks or experimental measurements are loaded.
The printed mathematical identity and numerical worked example are intact.

Run with the thesis Python. Output is figures/ch3_fig_torso_schematic.png.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Polygon

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "writing/v9/figures/ch3_fig_torso_schematic.png"

INK = "#20252b"
OUTLINE = "#aeb4bc"
FILL = "#f1f3f5"
HIP = "#ba3039"
SPINE = "#b78a00"
UP = "#22734d"
FORWARD = "#235e9a"

# Front-view drawing coordinates only, with the subject's right on the left.
L24 = np.array([-0.55, 0.65])
L23 = np.array([0.55, 0.65])
L12 = np.array([-0.80, 2.10])
LEFT_SHOULDER = np.array([0.80, 2.10])


def arrow(ax, start, stop, colour, width=2.0, head=13, gap=0):
    ax.add_patch(FancyArrowPatch(start, stop, arrowstyle="-|>",
                                 mutation_scale=head, linewidth=width,
                                 color=colour, shrinkA=gap, shrinkB=gap,
                                 zorder=5))


def torso(ax):
    outline = [(-0.24, 2.42), L12, L24, (0, 0.49), L23,
               LEFT_SHOULDER, (0.24, 2.42)]
    ax.add_patch(Polygon(outline, closed=True, facecolor=FILL,
                         edgecolor=OUTLINE, linewidth=1.0, zorder=1))
    ax.add_patch(Circle((0, 2.79), 0.30, facecolor=FILL,
                        edgecolor=OUTLINE, linewidth=1.0, zorder=1))
    ax.plot([-0.24, -0.24], [2.42, 2.59], color=OUTLINE, lw=1)
    ax.plot([0.24, 0.24], [2.42, 2.59], color=OUTLINE, lw=1)
    ax.plot([L12[0], LEFT_SHOULDER[0]], [L12[1], LEFT_SHOULDER[1]],
            color=OUTLINE, lw=0.9, zorder=2)
    ax.plot([L24[0], L23[0]], [L24[1], L23[1]],
            color=OUTLINE, lw=0.9, zorder=2)


def landmark(ax, point, name, description, position):
    ax.plot(*point, marker="o", markersize=4.0, color=INK, zorder=7)
    ax.text(*position, name + "\n" + description, fontsize=8.2,
            color=INK, ha="center", va="center", linespacing=1.2, zorder=8)


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    fig = plt.figure(figsize=(6.3, 3.85), facecolor="white")
    left = fig.add_axes([0.015, 0.145, 0.475, 0.715])
    right = fig.add_axes([0.510, 0.145, 0.475, 0.715])
    for ax in (left, right):
        ax.set_xlim(-1.65, 1.55)
        ax.set_ylim(-0.28, 3.25)
        ax.set_aspect("equal")
        ax.axis("off")
        torso(ax)

    fig.text(0.5, 0.965, "Torso-frame construction: schematic front view",
             ha="center", va="center", fontsize=10.2, color=INK)
    left.set_title("(a) Input vectors", fontsize=9.8, pad=6, color=INK)
    right.set_title("(b) Root frame at L24", fontsize=9.8, pad=6, color=INK)

    arrow(left, L23, L24, HIP, gap=3)
    arrow(left, L24, L12, SPINE, gap=3)
    landmark(left, L24, "L24", "right hip", (-0.59, 0.22))
    landmark(left, L23, "L23", "left hip", (0.62, 0.22))
    landmark(left, L12, "L12", "right shoulder", (-0.89, 2.36))
    left.text(0, 0.91, "hip vector", ha="center", va="center",
              fontsize=8.4, color=HIP)
    left.text(-1.03, 1.36, "$s$", ha="center", va="center",
              fontsize=12, color=SPINE)
    left.text(0, -0.20, "$s = L12 - L24$", ha="center", va="center",
              fontsize=9, color=SPINE)

    # Every axis starts at L24. The in-page arrows span the torso plane;
    # the concentric circle and point encode the out-of-page direction.
    arrow(right, L24, (-1.42, L24[1]), HIP)
    arrow(right, L24, (L24[0], 2.14), UP)
    right.add_patch(Circle(L24, 0.09, facecolor="white", edgecolor=FORWARD,
                           linewidth=1.7, zorder=8))
    right.add_patch(Circle(L24, 0.025, facecolor=FORWARD, edgecolor=FORWARD,
                           linewidth=0.5, zorder=9))
    right.text(-1.38, 0.92, "$x$", fontsize=12, ha="center", color=HIP)
    right.text(-0.33, 2.08, "$y$", fontsize=12, ha="center", color=UP)
    right.text(-0.32, 0.77, "$z$", fontsize=12, ha="center", color=FORWARD)
    right.text(-1.10, 0.28, "subject right", fontsize=8, color=HIP,
               ha="center", va="center")
    right.text(-0.14, 1.63, "trunk up", fontsize=8, color=UP,
               ha="left", va="center")
    right.annotate("L24 origin\nright hip", xy=L24, xytext=(0.44, 0.22),
                   fontsize=8.2, color=INK, ha="center", va="center",
                   arrowprops=dict(arrowstyle="-", color=INK, linewidth=0.8,
                                   shrinkA=3, shrinkB=8))

    fig.text(0.5, 0.075,
             "Subject's right is on the left of the page.",
             ha="center", va="center", fontsize=8.4, color=INK)
    fig.text(0.5, 0.032,
             "Dot in circle: z points toward the viewer, out of the chest.",
             ha="center", va="center", fontsize=8.4, color=FORWARD)
    fig.savefig(OUT, dpi=240, facecolor="white")
    plt.close(fig)
    print("saved", OUT)


if __name__ == "__main__":
    main()

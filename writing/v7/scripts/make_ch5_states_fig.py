#!/usr/bin/env python3
"""Chapter 5 figure: what one frame does inside the solver layer.

The whole chapter in one panel: the landmarks of a frame are checked by
the detectors, whatever they flag is removed, the removed points are
rebuilt where a rebuild is available, in dependency order (the wrist
before the elbow, because the two-link solve consumes the wrist), the
unchanged closed-form solve of Chapter 3 then runs on the assembled
points, and each of the seven joint groups leaves the layer in one of
three states. The bottom strip states
what the three output states mean and how each one is drawn. The
chain is linear: the rebuild stage, not the detectors, hands the
assembled points to the solve.

Output: writing/v7/figures/ch5_fig_states.png
Run:    python writing/v7/scripts/make_ch5_states_fig.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "writing" / "v7" / "figures" / "ch5_fig_states.png"

C_INK = "#22223b"
C_LINE = "#4a4e69"
C_MEAS = "#1a7f5a"
C_HELD = "#c1121f"
C_CONS = "#1d6fb8"
C_BOX = "#f1f3f5"

W, H = 11.6, 7.6
LEAD = 0.34            # line spacing inside a box
PAD_T, PAD_B = 0.60, 0.22

fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")


def box(x, top, w, title, lines):
    """Draw a box whose top edge is at `top`; returns its bottom edge."""
    h = PAD_T + LEAD * len(lines) + PAD_B
    y = top - h
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                                fc=C_BOX, ec=C_LINE, lw=1.5))
    ax.text(x + w / 2, top - 0.20, title, fontsize=11.5, color=C_INK,
            ha="center", va="top", fontweight="bold")
    for i, ln in enumerate(lines):
        ax.text(x + 0.22, top - PAD_T - 0.16 - LEAD * i, ln,
                fontsize=10.0, color=C_INK, ha="left", va="center")
    return y


def arrow(x0, y0, x1, y1):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=16, color=C_LINE, lw=1.8))


ax.text(W / 2, H - 0.12, "One frame through the solver layer",
        fontsize=13.5, color=C_INK, ha="center", va="top",
        fontweight="bold")

TOP = 6.95
b1 = box(0.22, TOP, 2.55, "landmarks",
         ["the eight body points of", "this frame, each with", "its source flag"])
b2 = box(3.15, TOP, 2.75, "detectors",
         ["the six tests mark the", "points that are wrong; a",
          "marked point is removed"])
b3 = box(6.30, TOP, 5.08, "rebuild, in dependency order",
         ["torso landmark on its ray at the remembered depth",
          "shoulder or hip from its partner across the pair",
          "wrist from the object pose while the hand holds it",
          "elbow by two-link inverse kinematics"])

TOP2 = 4.45
b4 = box(2.05, TOP2, 3.55, "the solve of Chapter 3",
         ["unchanged: torso frame,", "shoulder swing and twist,",
          "elbow flexion"])
b5 = box(6.30, TOP2, 5.08, "seven joint groups leave the layer",
         ["root; swing, twist and elbow of each arm.",
          "Every group carries one of the states below."])

# the chain is linear: landmarks -> detectors -> rebuild -> solve ->
# groups. The rebuild stage hands the assembled points to the solve;
# nothing goes from the detectors straight into the solve.
mid1 = (TOP + b1) / 2
arrow(2.79, mid1, 3.13, mid1)
arrow(5.92, mid1, 6.28, mid1)
ax.add_patch(FancyArrowPatch((6.70, b3 - 0.02), (5.05, TOP2 + 0.02),
                             arrowstyle="-|>", mutation_scale=16,
                             color=C_LINE, lw=1.8,
                             connectionstyle="arc3,rad=0.28"))
ax.text(5.50, 4.77, "the assembled points", fontsize=10.0,
        color=C_LINE, ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.14", fc="white", ec="none"))
mid2 = TOP2 - 0.95
arrow(5.62, mid2, 6.28, mid2)

# --- the three output states ----------------------------------------
SEP = min(b4, b5) - 0.34
ax.plot([0.22, W - 0.22], [SEP, SEP], color="#ced4da", lw=1.2)
ax.text(0.22, SEP - 0.18, "the three output states", fontsize=11.5,
        color=C_INK, ha="left", va="top", fontweight="bold")

states = [
    (0.22, C_MEAS, "measured",
     ["every landmark the group needs",
      "was measured on this frame"], "drawn plain"),
    (4.05, C_HELD, "held",
     ["a landmark is missing and nothing rebuilt it,",
      "or the twist is unobservable; the last value stands"],
     "drawn as a red joint"),
    (7.85, C_CONS, "constrained",
     ["the group used a rebuilt landmark,",
      "or its output was rate limited"], "drawn as a blue joint"),
]
y0 = SEP - 0.78
for x, col, name, lines, draw in states:
    ax.add_patch(Circle((x + 0.20, y0), 0.155, fc=col, ec="white", lw=1.4))
    ax.text(x + 0.50, y0, name, fontsize=11.5, color=col, ha="left",
            va="center", fontweight="bold")
    for i, ln in enumerate(lines):
        ax.text(x + 0.50, y0 - 0.36 - 0.32 * i, ln, fontsize=10.0,
                color=C_INK, ha="left", va="center")
    ax.text(x + 0.50, y0 - 0.36 - 0.32 * len(lines), draw, fontsize=10.0,
            color=col, ha="left", va="center", style="italic")

fig.savefig(OUT, dpi=200, facecolor="white")
print("saved", OUT)

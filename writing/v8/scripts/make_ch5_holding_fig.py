#!/usr/bin/env python3
"""Chapter 5 figure: the holding state of one hand.

The state machine that decides whether a hand holds the object: the
five conditions of the instantaneous test, and the rules for entering
the state, staying in it through a wrist failure, and leaving it. This
is panel (b) of the v7 grip figure (make_ch5_grip_fig.py) on its own;
the offset panel became its own figure (make_ch5_offset_fig.py).

Output: writing/v8/figures/ch5_fig_holding.png
Run:    python writing/v8/scripts/make_ch5_holding_fig.py
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "writing" / "v8" / "figures" / "ch5_fig_holding.png"

C_LM = "#22223b"
C_BONE = "#4a4e69"
C_BAD = "#c1121f"
C_OK = "#2a9d8f"

fig = plt.figure(figsize=(7.0, 4.9))
ax = fig.add_axes([0.02, 0.04, 0.96, 0.88])
ax.axis("off")
ax.set_xlim(0, 11.4)
ax.set_ylim(0, 6.9)


def box(xy, w, h, text, fc, ec, fs=10.5):
    ax.add_patch(FancyBboxPatch((xy[0] - w / 2, xy[1] - h / 2), w, h,
                                boxstyle="round,pad=0.10,rounding_size=0.18",
                                fc=fc, ec=ec, lw=2.0, zorder=4))
    ax.text(xy[0], xy[1], text, fontsize=fs, color=C_LM, ha="center",
            va="center", zorder=5, fontweight="bold")


def arrow(a, b, color, rad=0.0, lw=2.0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=15,
                                 color=color, lw=lw, zorder=3,
                                 connectionstyle=f"arc3,rad={rad}",
                                 shrinkA=6, shrinkB=6))


P_OFF = np.array([2.3, 5.2])
P_ON = np.array([7.3, 5.2])
box(P_OFF, 3.0, 1.05, "not holding", "#e9ecef", C_BONE)
box(P_ON, 3.0, 1.05, "holding", "#d7f0ec", C_OK)

arrow(P_OFF + np.array([1.5, 0.28]), P_ON - np.array([1.5, -0.28]),
      C_OK, rad=-0.30)
arrow(P_ON - np.array([1.5, 0.28]), P_OFF + np.array([1.5, -0.28]),
      C_BAD, rad=-0.30)

ax.text(4.80, 6.62,
        "enter: the instantaneous test passes on\nfive frames in a row",
        fontsize=9.2, color=C_OK, ha="center", va="center")
ax.text(4.80, 3.90,
        "exit: the object comes to rest, or a cleanly\n"
        "measured wrist sits beyond the release radius,\n"
        "for five frames in a row",
        fontsize=9.2, color=C_BAD, ha="center", va="center")

# self-loop on holding: persistence
ax.add_patch(FancyArrowPatch((8.55, 5.60), (8.55, 4.80),
                             arrowstyle="-|>", mutation_scale=14,
                             color=C_OK, lw=2.0, zorder=3,
                             connectionstyle="arc3,rad=-1.1"))
ax.text(9.75, 6.15, "stay through\na wrist failure", fontsize=9.2,
        color=C_OK, ha="center", va="center")

ax.text(0.15, 2.86,
        "instantaneous test, all five conditions on the same frame:",
        fontsize=9.6, color=C_LM, ha="left", va="center",
        fontweight="bold")
# the five conditions of carry.holding_mask + carry.forearm_ok
for i, t in enumerate((
        "the object marker is measured",
        "the object is being carried, not at rest",
        "the wrist is measured and not flagged by a detector",
        "the wrist lies within the hold radius of the object centre",
        "the forearm length is plausible for that arm")):
    ax.text(0.45, 2.36 - 0.46 * i, "-  " + t, fontsize=9.4,
            color="#343a40", ha="left", va="center")

ax.set_title("The holding state of one hand", fontsize=12, color=C_LM)

fig.savefig(OUT, dpi=200, facecolor="white")
print("saved", OUT)

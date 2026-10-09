#!/usr/bin/env python3
"""Chapter 5 figure: the hand-object offset and the grip state machine.

(a) The offset expressed in the object's own frame: while the grasp
holds, the wrist sits at a fixed point of that frame, so the same
offset carried by a later object pose predicts where the wrist is.
(b) The state machine that decides which hand the object informs,
with the five conditions of its instantaneous test and its entry,
persistence and exit rules.

Output: writing/v7/figures/ch5_fig_grip.png
Run:    python writing/v7/scripts/make_ch5_grip_fig.py
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import (FancyArrowPatch, FancyBboxPatch, Circle,
                                Rectangle, Polygon)
from matplotlib.transforms import Affine2D

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "writing" / "v7" / "figures" / "ch5_fig_grip.png"

C_LM = "#22223b"
C_BONE = "#4a4e69"
C_OBJ = "#1d6fb8"
C_MU = "#7b2cbf"
C_BAD = "#c1121f"
C_OK = "#2a9d8f"
C_GHOST = "#adb5bd"

fig = plt.figure(figsize=(10.4, 4.9))
axa = fig.add_axes([0.02, 0.06, 0.44, 0.86])
axb = fig.add_axes([0.50, 0.06, 0.48, 0.86])
for ax in (axa, axb):
    ax.axis("off")

# =====================================================================
# (a) the offset in the object frame
# =====================================================================
axa.set_xlim(-0.6, 6.6)
axa.set_ylim(-1.1, 4.6)
axa.set_aspect("equal")


def cube(ax, c, ang, s=1.05, alpha=1.0):
    """Draw the marked cube at centre c rotated by ang degrees; return
    the object frame axes (origin, x unit, y unit) in page units."""
    tr = Affine2D().rotate_deg_around(c[0], c[1], ang) + ax.transData
    ax.add_patch(Rectangle((c[0] - s / 2, c[1] - s / 2), s, s,
                           fc="#cfe3f7", ec=C_OBJ, lw=2.0, alpha=alpha,
                           transform=tr, zorder=3))
    ax.add_patch(Rectangle((c[0] - s / 4, c[1] - s / 4), s / 2, s / 2,
                           fc="white", ec=C_OBJ, lw=1.2, alpha=alpha,
                           transform=tr, zorder=4))
    a = np.radians(ang)
    ux = np.array([np.cos(a), np.sin(a)])
    uy = np.array([-np.sin(a), np.cos(a)])
    return np.asarray(c, float), ux, uy


def frame_axes(ax, o, ux, uy, L=0.85, lab=("", ""), color=C_OBJ, fs=9.5):
    for u, t in ((ux, lab[0]), (uy, lab[1])):
        ax.add_patch(FancyArrowPatch(o, o + L * u, arrowstyle="-|>",
                                     mutation_scale=12, color=color,
                                     lw=1.6, zorder=6))
        if t:
            ax.annotate(t, o + (L + 0.20) * u, fontsize=fs, color=color,
                        ha="center", va="center", zorder=7)


def wrist_hand(ax, w, color=C_LM):
    ax.add_patch(Circle(w, 0.115, fc=color, ec=color, lw=1.5, zorder=8))


# time A: the grasp is tracked, the offset is fitted
cA = np.array([1.35, 2.60])
oA, uxA, uyA = cube(axa, cA, 12.0)
frame_axes(axa, oA, uxA, uyA, lab=("", ""))
wA = oA + 0.62 * uxA - 0.86 * uyA
axa.plot([oA[0], wA[0]], [oA[1], wA[1]], color=C_MU, lw=2.4, zorder=7)
axa.add_patch(FancyArrowPatch(oA, wA, arrowstyle="-|>", mutation_scale=14,
                              color=C_MU, lw=2.4, zorder=7))
wrist_hand(axa, wA)
axa.plot([wA[0], wA[0] - 1.05], [wA[1], wA[1] - 0.70], color=C_BONE,
         lw=3.0, solid_capstyle="round", zorder=5)
axa.annotate("measured wrist", wA + np.array([0.20, -0.05]), fontsize=9,
             color=C_LM, ha="left", va="center")
axa.annotate("offset $h$", 0.5 * (oA + wA) + np.array([0.34, 0.34]),
             fontsize=10.5, color=C_MU, ha="left", fontweight="bold")
axa.add_patch(Circle(oA, 0.085, fc=C_OBJ, ec="white", lw=1.2, zorder=9))
axa.annotate("$o$", oA + np.array([-0.46, -0.40]), fontsize=13,
             color=C_OBJ, ha="center", va="center",
             bbox=dict(fc="white", ec="none", pad=0.6))
axa.annotate("object axes $R_{\\mathrm{obj}}$",
             oA + np.array([-1.00, 1.00]), fontsize=10,
             color=C_OBJ, ha="left")
axa.annotate("the grasp is tracked:\nthe offset is fitted", (1.35, -0.35),
             fontsize=9.5, color="#343a40", ha="center", va="center")

# time B: the wrist is lost, the same offset is carried
cB = np.array([4.75, 2.05])
oB, uxB, uyB = cube(axa, cB, -34.0)
frame_axes(axa, oB, uxB, uyB, lab=("", ""))
wB = oB + 0.62 * uxB - 0.86 * uyB
axa.add_patch(FancyArrowPatch(oB, wB, arrowstyle="-|>", mutation_scale=14,
                              color=C_MU, lw=2.4, ls="--", zorder=7))
axa.add_patch(Circle(wB, 0.13, fc="white", ec=C_MU, lw=2.2, zorder=8))
axa.annotate("recovered wrist", wB + np.array([0.22, -0.16]), fontsize=9,
             color=C_MU, ha="left", va="center")
axa.annotate("the wrist is lost:\nthe same offset is carried\nby the measured object pose",
             (4.75, -0.45), fontsize=9.5, color="#343a40", ha="center",
             va="center")

axa.add_patch(FancyArrowPatch((2.55, 3.35), (3.85, 3.15), arrowstyle="-|>",
                              mutation_scale=13, color=C_GHOST, lw=1.8,
                              connectionstyle="arc3,rad=-0.20", zorder=2))
axa.annotate("the object moves and turns", (3.30, 3.80), fontsize=9,
             color="#6c757d", ha="center")
axa.set_title("(a) The hand-object offset", fontsize=12, color=C_LM)

# =====================================================================
# (b) the grip state machine
# =====================================================================
axb.set_xlim(0, 11.4)
axb.set_ylim(0, 6.9)


def box(ax, xy, w, h, text, fc, ec, fs=10.5, bold=True):
    ax.add_patch(FancyBboxPatch((xy[0] - w / 2, xy[1] - h / 2), w, h,
                                boxstyle="round,pad=0.10,rounding_size=0.18",
                                fc=fc, ec=ec, lw=2.0, zorder=4))
    ax.text(xy[0], xy[1], text, fontsize=fs, color=C_LM, ha="center",
            va="center", zorder=5,
            fontweight="bold" if bold else "normal")


def arrow(ax, a, b, color, rad=0.0, lw=2.0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=15,
                                 color=color, lw=lw, zorder=3,
                                 connectionstyle=f"arc3,rad={rad}",
                                 shrinkA=6, shrinkB=6))


P_OFF = np.array([2.3, 5.2])
P_ON = np.array([7.3, 5.2])
box(axb, P_OFF, 3.0, 1.05, "not holding", "#e9ecef", C_BONE)
box(axb, P_ON, 3.0, 1.05, "holding", "#d7f0ec", C_OK)

arrow(axb, P_OFF + np.array([1.5, 0.28]), P_ON - np.array([1.5, -0.28]),
      C_OK, rad=-0.30)
arrow(axb, P_ON - np.array([1.5, 0.28]), P_OFF + np.array([1.5, -0.28]),
      C_BAD, rad=-0.30)

axb.text(4.20, 6.62,
         "enter: the instantaneous test passes on\n"
         "five frames in a row",
         fontsize=9.2, color=C_OK, ha="center", va="center")
axb.text(4.80, 3.90,
         "exit: the object comes to rest, or a cleanly\n"
         "measured wrist sits beyond the release radius,\n"
         "for five frames in a row",
         fontsize=9.2, color=C_BAD, ha="center", va="center")

# self-loop on holding: persistence
axb.add_patch(FancyArrowPatch((8.55, 5.60), (8.55, 4.80),
                              arrowstyle="-|>", mutation_scale=14,
                              color=C_OK, lw=2.0, zorder=3,
                              connectionstyle="arc3,rad=-1.1"))
axb.text(9.55, 6.15, "stay through\na wrist failure", fontsize=9.2,
         color=C_OK, ha="center", va="center")

axb.text(0.15, 2.86,
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
    axb.text(0.45, 2.36 - 0.46 * i, "-  " + t, fontsize=9.4,
             color="#343a40", ha="left", va="center")

axb.set_title("(b) The grip state machine", fontsize=12, color=C_LM)

fig.savefig(OUT, dpi=200, facecolor="white")
print("saved", OUT)

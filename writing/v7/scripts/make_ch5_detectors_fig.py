#!/usr/bin/env python3
"""Chapter 5 figure: what each tracking-failure detector measures.

Six small panels, one per detector, each drawing the single geometric
quantity that detector compares against a fixed tolerance: the
acquisition flag, the rigid segment length, the angle between the two
torso lines, the shoulder-to-hip width ratio, the between-frame landmark
step, and the wrist-to-object distance during a grip. The thesis names
the detectors rather than using the internal D1-D6 codes. Method figure
only; how often each detector fires belongs to the evaluation chapter.

Output: writing/v7/figures/ch5_fig_detectors.png
Run:    python writing/v7/scripts/make_ch5_detectors_fig.py
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, Arc, Rectangle

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "writing" / "v7" / "figures" / "ch5_fig_detectors.png"

C_BONE = "#4a4e69"
C_LM = "#22223b"
C_BAD = "#c1121f"
C_MEA = "#7b2cbf"
C_OBJ = "#1d6fb8"
C_GHOST = "#adb5bd"
C_FILL = "#dee2e6"

fig, axes = plt.subplots(2, 3, figsize=(10.4, 6.6))
fig.patch.set_facecolor("white")


def setup(ax, title, sub):
    ax.set_xlim(-1.55, 1.55)
    ax.set_ylim(-1.75, 1.45)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=11.5, color=C_LM, fontweight="bold",
                 pad=2)
    ax.text(0, -1.72, sub, fontsize=8.8, color="#343a40", ha="center",
            va="bottom", linespacing=1.35)


def bone(ax, a, b, color=C_BONE, lw=3.0, ls="-", z=3):
    ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=lw, ls=ls,
            solid_capstyle="round", zorder=z)


def lm(ax, p, fc=C_LM, ec=C_LM, r=0.075, z=6):
    ax.add_patch(Circle(p, r, fc=fc, ec=ec, lw=1.5, zorder=z))


def measure(ax, a, b, off, label, color=C_MEA, fs=9.0, dl=(0.0, 0.14)):
    a, b = np.asarray(a, float), np.asarray(b, float)
    u = (b - a) / np.linalg.norm(b - a)
    n = np.array([-u[1], u[0]]) * off
    ax.annotate("", xy=a + n, xytext=b + n,
                arrowprops=dict(arrowstyle="<|-|>", color=color, lw=1.5))
    m = 0.5 * (a + b) + n + np.array(dl)
    ax.text(m[0], m[1], label, fontsize=fs, color=color, ha="center",
            va="center")


# shared skeleton geometry for the torso panels
SH_L, SH_R = np.array([0.62, 0.62]), np.array([-0.62, 0.70])
HP_L, HP_R = np.array([0.46, -0.52]), np.array([-0.40, -0.52])


def torso(ax, sl=SH_L, sr=SH_R, hl=HP_L, hr=HP_R, fill=True):
    if fill:
        q = np.array([sr, sl, hl, hr])
        ax.fill(q[:, 0], q[:, 1], color=C_FILL, ec="none", zorder=1)
    bone(ax, sr, sl, lw=3.4)
    bone(ax, hr, hl, lw=3.4)
    bone(ax, sr, hr, lw=2.0)
    bone(ax, sl, hl, lw=2.0)
    for p in (sl, sr, hl, hr):
        lm(ax, p)


# --- acquisition ---------------------------------------------------
ax = axes[0][0]
setup(ax, "acquisition",
      "the landmark detector declines the sample:\n"
      "visibility below the gate, or no valid depth")
S, E, W = np.array([-0.75, 0.85]), np.array([0.15, 0.10]), np.array([0.05, -0.85])
bone(ax, S, E)
bone(ax, E, W, color=C_GHOST, ls=":")
lm(ax, S)
lm(ax, E)
ax.add_patch(Circle(W, 0.11, fc="white", ec=C_BAD, lw=2.0, ls=":", zorder=6))
for s in (1, -1):
    ax.plot([W[0] - 0.20, W[0] + 0.20], [W[1] - s * 0.20, W[1] + s * 0.20],
            color=C_BAD, lw=2.2, zorder=7)
ax.text(0.46, -0.60, "no usable\nwrist sample", fontsize=8.6, color=C_BAD,
        ha="left", va="center")

# --- segment length ------------------------------------------------
ax = axes[0][1]
setup(ax, "segment length",
      "a rigid segment cannot change length:\n"
      "the measured length against its calibrated value")
S, E = np.array([-0.85, 0.80]), np.array([0.05, 0.00])
W_true = np.array([-0.05, -0.85])
W_bad = np.array([0.85, -0.95])
bone(ax, S, E)
bone(ax, E, W_true, color=C_GHOST, ls="--", lw=2.0)
bone(ax, E, W_bad, color=C_BAD)
lm(ax, S)
lm(ax, E)
lm(ax, W_true, fc="white", ec=C_GHOST)
lm(ax, W_bad, fc=C_BAD, ec=C_BAD)
measure(ax, S, E, 0.22, "upper arm", dl=(-0.02, 0.10))
measure(ax, E, W_bad, -0.26, "", color=C_BAD)
ax.text(1.02, -0.05, "forearm,\ntoo long", fontsize=9.0, color=C_BAD,
        ha="center", va="center")

# --- torso line angle ----------------------------------------------
ax = axes[0][2]
setup(ax, "torso line angle",
      "the hip line and the shoulder line stay\n"
      "near-parallel on a rigid trunk")
sr_bad = np.array([-0.62, 1.02])
torso(ax, sr=sr_bad, fill=True)
apex = np.array([-0.95, -0.10])
for (a, b) in ((HP_R, HP_L), (sr_bad, SH_L)):
    u = (b - a) / np.linalg.norm(b - a)
    ax.plot([apex[0], apex[0] + 1.15 * u[0]], [apex[1], apex[1] + 1.15 * u[1]],
            color=C_MEA, lw=1.5, ls="--", zorder=4)
th = [np.degrees(np.arctan2((b - a)[1], (b - a)[0]))
      for a, b in ((HP_R, HP_L), (sr_bad, SH_L))]
ax.add_patch(Arc(apex, 1.55, 1.55, theta1=min(th), theta2=max(th),
                 color=C_MEA, lw=2.0, zorder=5))
ax.text(-1.05, -0.80, "angle between\nthe two lines", fontsize=8.8,
        color=C_MEA, ha="left", va="center")

# --- torso width ratio ---------------------------------------------------
ax = axes[1][0]
setup(ax, "torso width ratio",
      "the ratio of the two widths is fixed\n"
      "by the subject's build")
torso(ax)
measure(ax, SH_R, SH_L, 0.30, "shoulder width", color=C_OBJ,
        dl=(0.0, 0.15))
measure(ax, HP_R, HP_L, -0.28, "hip width", color=C_OBJ, dl=(0.0, -0.15))

# --- landmark step -------------------------------------------------
ax = axes[1][1]
setup(ax, "landmark step",
      "a landmark cannot jump from one frame\n"
      "to the next during a slow task")
S = np.array([-0.85, 0.85])
E_prev = np.array([-0.15, 0.05])
E_now = np.array([0.85, -0.55])
bone(ax, S, E_prev, color=C_GHOST, ls="--", lw=2.2)
bone(ax, S, E_now)
lm(ax, S)
lm(ax, E_prev, fc="white", ec=C_GHOST)
lm(ax, E_now, fc=C_BAD, ec=C_BAD)
ax.add_patch(FancyArrowPatch(E_prev, E_now, arrowstyle="-|>",
                             mutation_scale=14, color=C_BAD, lw=2.0,
                             zorder=7,
                             connectionstyle="arc3,rad=-0.25"))
ax.text(-0.30, -0.30, "previous frame", fontsize=8.6, color=C_GHOST,
        ha="center")
ax.text(0.36, 0.30, "step in one\nframe interval", fontsize=8.8,
        color=C_BAD, ha="center", va="center")

# --- grip plausibility ---------------------------------------------
ax = axes[1][2]
setup(ax, "grip plausibility",
      "a wrist reported this far from the object\n"
      "it holds is a wrong measurement")
box_c = np.array([-0.45, 0.30])
ax.add_patch(Rectangle(box_c - 0.34, 0.68, 0.68, fc="#cfe3f7", ec=C_OBJ,
                       lw=2.0, zorder=4))
ax.add_patch(Rectangle(box_c - 0.19, 0.38, 0.38, fc="white", ec=C_OBJ,
                       lw=1.2, zorder=5))
lm(ax, box_c, fc=C_OBJ, ec=C_OBJ, r=0.05, z=6)
W_bad = np.array([0.85, -0.75])
lm(ax, W_bad, fc=C_BAD, ec=C_BAD)
ax.plot([box_c[0], W_bad[0]], [box_c[1], W_bad[1]], color=C_BAD, lw=1.6,
        ls="--", zorder=5)
ax.add_patch(Circle(box_c, 0.98, fc="none", ec=C_BAD, lw=1.3, ls=":",
                    zorder=3))
ax.text(box_c[0], box_c[1] - 1.10, "release radius", fontsize=8.6,
        color=C_BAD, ha="center", va="top")
ax.text(0.88, -0.35, "reported\nwrist", fontsize=8.6, color=C_BAD,
        ha="center", va="center")
ax.text(-0.45, -0.35, "object centre", fontsize=8.6, color=C_OBJ,
        ha="center")

fig.tight_layout(rect=(0, 0.01, 1, 1), h_pad=2.6, w_pad=1.0)
fig.savefig(OUT, dpi=200, facecolor="white")
print("saved", OUT)

# D-082: show the full Scene geometry and its inverse Camera' conversion.
#!/usr/bin/env python3
"""Chapter 5 information-flow figure (supervisor comment C27, round of
2026-09-05), the Chapter 5 counterpart of Figure 3.1.

One glance shows how the recovery layer sits between the earlier
chapters and the later ones: the filtered landmarks of Chapter 2, the
calibrated arm lengths of Chapter 3 and the object pose of Chapter 4
enter on the left; the failure detectors remove wrong landmarks; the
three rebuild cases put back what can be put back, from state carried
between frames; the unchanged solve of Chapter 3 runs on the assembled
points; the seven joint groups leave with a state each, to the
reconstruction of Chapter 6 and the evaluation of Chapter 7. Box shapes
and colours follow the flow-figure family (make_ch3_flow_fig.py).

Output: writing/v8/condensed/figures/ch5_fig_flow.png
Run:    python writing/v8/condensed/scripts/make_ch5_flow_final_fig.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

REPO = Path(__file__).resolve().parents[4]
OUT = REPO / "writing" / "v8" / "condensed" / "figures" / "ch5_fig_flow.png"

C_IN = "#cfd8e4"      # inputs (device grey of the family)
C_FRAME = "#dbe9f6"   # detector / solve stages
C_ANGLE = "#e3f2df"   # rebuild stages
C_REC = "#f6f1cf"     # carried state (record)
C_OUT = "#e2e2e8"     # chapter output


def box(ax, x, y, w, h, text, fc, fs=8.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.010",
                                fc=fc, ec="0.25", lw=1.1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def device(ax, x, y, w, h, text, fs=8.4):
    ax.add_patch(Rectangle((x, y), w, h, fc=C_IN, ec="0.25", lw=1.1))
    ax.add_patch(Rectangle((x, y), 0.008, h, fc="0.25", ec="0.25", lw=0.6))
    ax.text(x + w / 2 + 0.004, y + h / 2, text, ha="center", va="center",
            fontsize=fs)


def record(ax, x, y, w, h, text, fs=8.0):
    ax.add_patch(Rectangle((x, y), w, h, fc=C_REC, ec="0.25", lw=1.1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def arrow(ax, x0, y0, x1, y1, rad=0.0, label=None, lx=0.0, ly=0.012,
          ls="-"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=12, color="0.2", lw=1.2,
                                 linestyle=ls,
                                 connectionstyle=f"arc3,rad={rad}"))
    if label:
        ax.text((x0 + x1) / 2 + lx, (y0 + y1) / 2 + ly, label,
                ha="center", va="bottom", fontsize=7.4, color="0.25")


fig, ax = plt.subplots(figsize=(11.4, 6.4))
ax.set_xlim(-0.012, 1.012)
ax.set_ylim(0, 1)
ax.axis("off")

# --- input column ------------------------------------------------------
device(ax, 0.005, 0.70, 0.140, 0.24,
       "Filtered landmarks\nwith source flags\n(eight upper-body\npoints, Chapter 2)", 8.0)
device(ax, 0.005, 0.39, 0.140, 0.22,
       "Calibrated arm\nlengths $L_1$, $L_2$\nand the chain\n(Chapter 3)", 8.0)
device(ax, 0.005, 0.07, 0.140, 0.22,
       "Object pose in\n{Scene}: swap,\ngravity alignment,\nfloor placement\n(Section 5.3)", 8.0)

# --- detectors (top) ---------------------------------------------------
box(ax, 0.205, 0.72, 0.150, 0.20,
    "Failure detectors\nSection 5.2\nwrong landmarks\nare removed", C_FRAME)

# --- carried state (bottom) -------------------------------------------
record(ax, 0.205, 0.05, 0.150, 0.26,
       "State carried\nbetween frames:\nholding state,\noffset $h$,\n"
       "direction memories\nSection 5.3")

# --- rebuild stack (centre) -------------------------------------------
RX, RW = 0.415, 0.200
box(ax, RX, 0.665, RW, 0.145,
    "Case A: wrist from the\nelbow along the forearm\nmemory, Section 5.3",
    C_ANGLE)
box(ax, RX, 0.475, RW, 0.145,
    "Case B: Scene wrist from\nobject pose and offset;\nconvert to {Camera'}\nequation (5.7), Section 5.4",
    C_ANGLE)
box(ax, RX, 0.285, RW, 0.145,
    "Case C: elbow by two-link\ninverse kinematics\nSection 5.5", C_ANGLE)
# a light bracket behind the stack, so the three cases read as one stage
ax.add_patch(Rectangle((RX - 0.018, 0.255), RW + 0.036, 0.585,
                       fc="none", ec="0.55", lw=0.9, ls=(0, (3, 3)),
                       zorder=0))
ax.text(RX + RW / 2 + 0.035, 0.87, "rebuild, in dependency order",
        ha="center", va="center", fontsize=8.0, color="0.35")

# --- solve -------------------------------------------------------------
box(ax, 0.700, 0.47, 0.110, 0.15,
    "The solve of\nChapter 3,\nunchanged", C_FRAME)

# --- outputs -----------------------------------------------------------
box(ax, 0.845, 0.40, 0.150, 0.29,
    "Seven joint groups,\neach with a state:\nmeasured, held,\nconstrained\nSection 5.6",
    C_OUT, 8.2)
box(ax, 0.86, 0.80, 0.120, 0.13, "Chapter 6\nreconstruction", C_OUT, 8.2)
box(ax, 0.86, 0.16, 0.120, 0.13, "Chapter 7\nevaluation", C_OUT, 8.2)

# --- arrows ------------------------------------------------------------
# landmarks -> detectors -> rebuild stack
arrow(ax, 0.145, 0.82, 0.205, 0.82)
arrow(ax, 0.355, 0.82, 0.415, 0.77, rad=-0.15)
ax.text(0.386, 0.838, "surviving\nlandmarks", ha="center", va="bottom",
        fontsize=6.8, color="0.25")
# object pose -> carried state -> Case B
arrow(ax, 0.145, 0.18, 0.205, 0.18)
arrow(ax, 0.355, 0.25, 0.415, 0.53, rad=-0.25)
ax.text(0.300, 0.325, "$h$, holding\nstate", ha="center", va="bottom",
        fontsize=7.4, color="0.25")
# L1, L2 -> Case A and Case C (the shared arrow forks at the input edge)
arrow(ax, 0.145, 0.50, 0.415, 0.72, rad=-0.18, label="$L_2$, forearm\nmemory",
      lx=-0.010, ly=0.020)
arrow(ax, 0.145, 0.50, 0.415, 0.40, rad=0.18, label="$L_1$, $L_2$",
      lx=-0.030, ly=0.010)
# stack -> solve (assembled points), solve -> joint groups
arrow(ax, RX + RW + 0.018, 0.545, 0.700, 0.545)
ax.text(0.6665, 0.570, "Camera'\npoints", ha="center", va="bottom",
        fontsize=6.8, color="0.25")
arrow(ax, 0.810, 0.545, 0.845, 0.545)
# joint groups -> Chapter 6 and Chapter 7
arrow(ax, 0.92, 0.69, 0.92, 0.80)
arrow(ax, 0.92, 0.40, 0.92, 0.29)
# joint groups -> carried state (next frame), dashed, routed below the solve
arrow(ax, 0.845, 0.43, 0.355, 0.12, rad=-0.35, ls="--")
ax.text(0.60, 0.035, "next frame: the states and\nthe last angles", ha="center",
        va="bottom", fontsize=7.4, color="0.25")

fig.savefig(OUT, dpi=200, bbox_inches="tight")
print("saved", OUT)

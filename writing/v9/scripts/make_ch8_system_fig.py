#!/usr/bin/env python3
"""Chapter 8 system design figure: the offline pass against the causal
structure, stage by stage (rewrite of Chapter 8, 2026-09-07: how the
offline pipeline was transferred to real time and what the proposed
system structure is).

Two bands share one column grid so that each live stage sits under the
offline stage it replaces. Fill colour says what happened to a stage in
the transfer:
  lane colour (green landmark, orange marker) = same construction as
      offline (unchanged);
  amber = adapted, a causal replacement of a stage that read the future;
  violet = new wiring, a part that exists only in the causal structure;
  grey with a dashed edge = offline only, an analysis tool over a
      finished recording with no causal counterpart.

Regenerated 2026-09-11 for the round-1 fix pass (FIX_DECISIONS.md G8 and
G1, Chapter_8.txt MUST FIX 4 and SHOULD FIX 2): the offline analysis box
reads "fitted line" where it read "reference path", the lower band header
reads "Causal structure (this chapter)", and the legend and the footer
follow the causal vocabulary of the Figure 8.1 caption.

Layout and helpers follow writing/v8/scripts/make_ch2_fig1.py and
writing/v7/scripts/make_ch6_arch_fig.py so the three diagrams read as
one family. Sources checked: v2/V2.md; v2/broker/capture_broker.py
(one device, alignment once, session clock from hardware timestamps);
v2/person/v2_person.py and v2/common/object_link.py (GripTracker,
ObjectPoseReader, the one-way link); v2/object/v2_object.py (plausibility
gate ahead of CausalObjectFilter, world anchoring by import);
v2/integration/v2_integrate.py (delay buffer at capture time minus the
declared delay, INTERP / HELD / BLEND, display smoother at packet write);
the offline stages as Chapters 2, 4, 5 and 7 describe them.

Output: writing/v9/figures/ch8_fig_system.png
Run:    python writing/v9/scripts/make_ch8_system_fig.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "writing" / "v9" / "figures" / "ch8_fig_system.png"

C_A, C_B = "#e3f2df", "#fdeeda"          # unchanged, lane colours
C_ADAPT = "#fff0c2"                      # adapted for causality
C_NEW = "#ece1f2"                        # new wiring
C_OFF = "#e9e9e9"                        # offline only
C_REC = "#f6f1cf"                        # a shared-memory record
C_DEV = "#cfd8e4"                        # the source itself
FS = 7.0


def box(ax, x, y, w, h, text, fc, fs=FS, dashed=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008",
                                fc=fc, ec="0.25", lw=1.0,
                                ls="--" if dashed else "-"))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def record(ax, x, y, w, h, text, fs=FS):
    ax.add_patch(Rectangle((x, y), w, h, fc=C_REC, ec="0.25", lw=1.0))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def device(ax, x, y, w, h, text, fs=FS):
    ax.add_patch(Rectangle((x, y), w, h, fc=C_DEV, ec="0.25", lw=1.0))
    ax.add_patch(Rectangle((x, y), 0.007, h, fc="0.25", ec="0.25", lw=0.5))
    ax.text(x + w / 2 + 0.004, y + h / 2, text, ha="center", va="center",
            fontsize=fs)


def arrow(ax, x0, y0, x1, y1, rad=0.0, text=None, tx=None, ty=None,
          ha="left"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=10, color="0.2", lw=1.0,
                                 connectionstyle=f"arc3,rad={rad}"))
    if text:
        ax.text(tx if tx is not None else (x0 + x1) / 2,
                ty if ty is not None else (y0 + y1) / 2, text,
                fontsize=6.4, color="0.25", ha=ha, va="center",
                bbox=dict(fc="white", ec="none", pad=1.0))


fig, ax = plt.subplots(figsize=(9.6, 6.8))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

# column grid (x, width); the same for both bands
X0, W0 = 0.010, 0.080     # source
X1, W1 = 0.100, 0.100     # capture process / frame replay
X2, W2 = 0.208, 0.070     # frame buffer
X3, W3 = 0.288, 0.088     # detection
X4, W4 = 0.400, 0.092     # filtering
X5, W5 = 0.516, 0.094     # recovery / cleaning
X6, W6 = 0.634, 0.074     # solve / anchoring
X7, W7 = 0.732, 0.078     # tables / records
X8, W8 = 0.832, 0.086     # merger / analysis
X9, W9 = 0.936, 0.058     # display
H = 0.130


def band(y0, title, color):
    ax.text(0.5, y0 + 0.415, title, fontsize=9.2, color=color, ha="center")
    ax.plot([0.005, 0.995], [y0 + 0.402, y0 + 0.402], color="0.6", lw=0.6)
    yA, yM, yB = y0 + 0.255, y0 + 0.140, y0 + 0.020
    return yA, yM, yB


# ---------------------------------------------------------------- offline
yA, yM, yB = band(0.560, "Offline pass (Chapters 2 to 7)", "0.2")
device(ax, X0, yM, W0, H, "Recording\n(bag file)")
box(ax, X1, yM, W2 + X2 - X1, H,
    "Frame replay and\ndepth to colour\nalignment, inside\nevery script", C_OFF, dashed=True)
box(ax, X3, yA, W3, H, "MediaPipe\nlandmarks with\nsensor depth", C_A)
box(ax, X4, yA, W4, H, "Whole signal\nfilter: zero phase,\ncentred despike,\ngap bridging", C_A)
box(ax, X5, yA, W5, H, "Pose recovery:\nepisodes over\ntheir full extent,\nwhole episode\noffset", C_A)
box(ax, X6, yA, W6, H, "Kinematic\nsolve", C_A)
record(ax, X7, yA, W7, H, "Angle table,\nstates per\nframe")
box(ax, X3, yB, W3, H, "ArUco detection,\nplanar pose", C_B)
box(ax, X4, yB, W4, H, "Zero phase filter,\ncleaning rule on\nthe finished track", C_B)
box(ax, X5, yB, W5, H, "World anchoring", C_B)
record(ax, X7, yB, W7, H, "Object track\ntable")
box(ax, X8, yM + 0.06, W8, H + 0.02,
    "Analysis tools:\nfitted line,\nsynthetic\nmasking, manual\nlabels", C_OFF, dashed=True)
box(ax, X8, yB - 0.005, W8, H - 0.015, "Figures and\nUnity replay\nfrom the tables", C_OFF, dashed=True)

arrow(ax, X0 + W0, yM + H / 2, X1, yM + H / 2)
arrow(ax, X2 + W2, yM + H * 0.7, X3, yA + H * 0.4)
arrow(ax, X2 + W2, yM + H * 0.3, X3, yB + H * 0.6)
for xa, xb, y in ((X3 + W3, X4, yA), (X4 + W4, X5, yA), (X5 + W5, X6, yA),
                  (X6 + W6, X7, yA), (X3 + W3, X4, yB), (X4 + W4, X5, yB)):
    arrow(ax, xa, y + H / 2, xb, y + H / 2)
arrow(ax, X5 + W5, yB + H / 2, X7, yB + H / 2)
# the cleaned track is read by the recovery as a table
arrow(ax, X7 + 0.02, yB + H, X5 + W5 * 0.6, yA, rad=0.25,
      text="cleaned track,\nread as a table", tx=X6 + 0.005, ty=yM + H * 0.55, ha="left")
arrow(ax, X7 + W7, yA + H * 0.4, X8, yM + 0.06 + H + 0.02 - 0.02, rad=-0.1)
arrow(ax, X7 + W7, yB + H * 0.6, X8, yM + 0.06 + 0.02, rad=0.1)
arrow(ax, X7 + W7, yB + H * 0.3, X8, yB + 0.05)

# ------------------------------------------------------------------ live
yA, yM, yB = band(0.060, "Causal structure (this chapter)", "0.2")
device(ax, X0, yM, W0, H, "Sensor, or\nthe recording\nreplayed")
box(ax, X1, yM, W1, H, "Capture process:\none device, aligns\nonce, session\nclock", C_NEW)
record(ax, X2, yM, W2, H, "Shared\nframe\nbuffer")
box(ax, X3, yA, W3, H, "MediaPipe\nlandmarks with\nsensor depth", C_A)
box(ax, X4, yA, W4, H, "Causal filter:\ntrailing despike,\nOne Euro\nsmoother", C_ADAPT)
box(ax, X5, yA, W5, H, "Pose recovery:\nonline grip\ntracker, bounded\nentry and exit", C_ADAPT)
box(ax, X6, yA, W6, H, "Kinematic\nsolve", C_A)
record(ax, X7, yA, W7, H, "Person record:\nangles, live\nbits, states")
box(ax, X3, yB, W3, H, "ArUco detection,\nplanar pose", C_B)
box(ax, X4, yB, W4, H, "Cleaning rule on\neach sample,\nthen the causal\nfilter", C_ADAPT)
box(ax, X5, yB, W5, H, "World anchoring", C_B)
record(ax, X7, yB, W7, H, "Object\nrecord")
box(ax, X8, yM - 0.055, W8, H + 0.11,
    "Merger:\nrenders at\ncapture time\nminus a declared\ndelay; interpolates,\nholds, blends back;\ndisplay smoother", C_NEW, fs=6.5)
record(ax, X9, yM + 0.075, W9, H - 0.025, "Combined\nrecord", fs=7.0)
box(ax, X9, yM - 0.075, W9, H - 0.025, "Unity\nreceiver", C_A, fs=7.0)

arrow(ax, X0 + W0, yM + H / 2, X1, yM + H / 2)
arrow(ax, X1 + W1, yM + H / 2, X2, yM + H / 2)
arrow(ax, X2 + W2, yM + H * 0.7, X3, yA + H * 0.4)
arrow(ax, X2 + W2, yM + H * 0.3, X3, yB + H * 0.6)
for xa, xb, y in ((X3 + W3, X4, yA), (X4 + W4, X5, yA), (X5 + W5, X6, yA),
                  (X6 + W6, X7, yA), (X3 + W3, X4, yB), (X4 + W4, X5, yB)):
    arrow(ax, xa, y + H / 2, xb, y + H / 2)
arrow(ax, X5 + W5, yB + H / 2, X7, yB + H / 2)
# the one-way link: the landmark branch reads the object record
arrow(ax, X7 + 0.02, yB + H, X5 + W5 * 0.6, yA, rad=0.25,
      text="object record,\none way link", tx=X6 + 0.005, ty=yM + H * 0.55, ha="left")
arrow(ax, X7 + W7, yA + H * 0.4, X8, yM + H + 0.03, rad=-0.1)
arrow(ax, X7 + W7, yB + H * 0.6, X8, yM - 0.03, rad=0.1)
arrow(ax, X8 + W8, yM + H / 2 + 0.01, X9, yM + 0.075 + (H - 0.025) / 2)
arrow(ax, X9 + W9 / 2, yM + 0.075, X9 + W9 / 2, yM - 0.075 + H - 0.025)

# legend (bottom left, under the live source)
lx, ly = 0.010, 0.135
items = [(C_A, "-", "unchanged, same construction as offline"),
         (C_ADAPT, "-", "adapted, a causal replacement"),
         (C_NEW, "-", "new wiring, only in the causal structure"),
         (C_OFF, "--", "offline only, no causal counterpart"),
         (C_REC, "-", "record in shared memory")]
for i, (fc, ls, label) in enumerate(items):
    y = ly - i * 0.026
    ax.add_patch(Rectangle((lx, y), 0.022, 0.018, fc=fc, ec="0.25", lw=0.8, ls=ls))
    ax.text(lx + 0.030, y + 0.009, label, fontsize=6.6, va="center", color="0.2")

ax.text(0.995, 0.012, "Landmark lane above, marker lane below in each band; "
        "each causal stage sits under the offline stage it replaces.",
        fontsize=6.8, color="0.35", style="italic", va="center", ha="right")
plt.tight_layout()
plt.savefig(OUT, dpi=200)
print("saved", OUT)

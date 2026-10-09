# D-073: condensed-local copy; frame labels follow current Craig notation.
#!/usr/bin/env python3
"""Chapter 3 information-flow figure (supervisor comment C21, round of
2026-08-31).

One glance shows how the sections of the chapter come together: the
calibrated landmarks enter from the sensing stage; the three torso
landmarks establish the root frame and its homogeneous transformation
with respect to the y-up camera frame Camera'; the elbow landmark carried into the root
frame yields the shoulder angles and the shoulder/elbow frame
transformations; the wrist landmark carried into the elbow frame yields
the elbow flexion; the wrist itself stays a tracked point. Box shapes
and colours follow the Chapter 2/6 flow-figure family
(make_ch2_fig1.py, make_ch6_arch_fig.py).

V8 (2026-09-06): the three landmark input boxes now say that the
landmarks arrive after the pose recovery of Chapter 5, so that this
figure agrees with Figure 2.3 and with Chapter 5.

Output: writing/v9/figures/ch3_fig_flow.png
Run:    python writing/v9/scripts/make_ch3_flow_final_fig.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "writing" / "v9" / "figures" / "ch3_fig_flow.png"

C_IN = "#cfd8e4"      # inputs (device grey of the family)
C_FRAME = "#dbe9f6"   # frame/T construction stages
C_ANGLE = "#e3f2df"   # angle extraction stages
C_REC = "#f6f1cf"     # transported quantities (records)
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


def arrow(ax, x0, y0, x1, y1, rad=0.0, label=None, lx=0.0, ly=0.012):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=12, color="0.2", lw=1.2,
                                 connectionstyle=f"arc3,rad={rad}"))
    if label:
        ax.text((x0 + x1) / 2 + lx, (y0 + y1) / 2 + ly, label,
                ha="center", va="bottom", fontsize=7.4, color="0.25")


fig, ax = plt.subplots(figsize=(11.4, 6.2))
ax.set_xlim(-0.012, 1.012)
ax.set_ylim(0, 1)
ax.axis("off")

# --- input column: the calibrated landmarks, grouped by their use ------
device(ax, 0.005, 0.60, 0.135, 0.30,
       "Torso landmarks\nhips L23, L24\nshoulder L12\n(Camera',\nChapter 2, after\nthe recovery of\nChapter 5)", 7.6)
device(ax, 0.005, 0.225, 0.135, 0.175,
       "Elbow landmark\nL14 (after the\nrecovery of\nChapter 5)", 7.6)
device(ax, 0.005, 0.03, 0.135, 0.165,
       "Wrist landmark\nL16 (after the\nrecovery of\nChapter 5)", 7.6)

# --- top band: root frame ---------------------------------------------
box(ax, 0.205, 0.635, 0.185, 0.24,
    "Torso root frame\nSection 3.2\naxes from the hip line\nand spine side,"
    "\norigin at L24", C_FRAME)
record(ax, 0.435, 0.66, 0.155, 0.19,
       "Root pose w.r.t.\ny-up camera frame\n" + r"${}^{\mathrm{Camera}'}_{\mathrm{L24}}T$")
box(ax, 0.645, 0.66, 0.16, 0.19,
    "Torso pose angles\nSection 3.4.1\nread from " + r"${}^{\mathrm{Camera}'}_{\mathrm{L24}}R$", C_ANGLE)

# --- middle band: shoulder --------------------------------------------
box(ax, 0.205, 0.335, 0.185, 0.22,
    "Shoulder frame at L12\nSection 3.3.3\nroot orientation,\n"
    "origin moved to L12:\n" + r"${}^{\mathrm{L24}}_{\mathrm{L12}}T$", C_FRAME)
box(ax, 0.435, 0.335, 0.185, 0.22,
    "Upper arm into the\nroot frame,\nswing + twist\n"
    "Section 3.4.2", C_ANGLE)
record(ax, 0.66, 0.35, 0.145, 0.19,
       "Shoulder angles\n$t_y$, $t_z$, $t_t$\nand " + r"${}^{\mathrm{L12}}_{\mathrm{L14}}T$")

# --- bottom band: elbow + wrist ---------------------------------------
box(ax, 0.435, 0.075, 0.185, 0.21,
    "Wrist into the elbow\nframe, flexion\nSection 3.4.3", C_ANGLE)
box(ax, 0.205, 0.075, 0.185, 0.21,
    "Elbow frame at L14\nSection 3.3.3\nshoulder rotation\napplied to the arm",
    C_FRAME)

# --- output -----------------------------------------------------------
box(ax, 0.845, 0.335, 0.15, 0.35,
    "Thirteen angles\nper frame\ntorso 3, each arm\nswing, twist, flexion\n"
    "(wrist stays a\ntracked point,\nSection 3.4.4)\nto Chapter 6", C_OUT, 8.2)

# --- arrows -----------------------------------------------------------
arrow(ax, 0.140, 0.755, 0.205, 0.755)
arrow(ax, 0.390, 0.755, 0.435, 0.755)
arrow(ax, 0.590, 0.755, 0.645, 0.755)
# The root transform feeds the shoulder band (chain) and the elbow band
arrow(ax, 0.512, 0.660, 0.512, 0.555, label=r"${}^{\mathrm{Camera}'}_{\mathrm{L24}}T$", lx=0.030, ly=-0.030)
arrow(ax, 0.297, 0.635, 0.297, 0.555, label=r"${}^{\mathrm{Camera}'}_{\mathrm{L24}}T$", lx=0.032, ly=-0.030)
# landmarks into their stages: the elbow landmark forms the upper-arm
# vector of the swing+twist stage; the wrist landmark enters the
# flexion stage (both routed through the gaps between the frame boxes)
arrow(ax, 0.140, 0.295, 0.470, 0.335, rad=0.10)
arrow(ax, 0.140, 0.110, 0.500, 0.075, rad=0.15)
# shoulder band flow
arrow(ax, 0.390, 0.470, 0.435, 0.470)
arrow(ax, 0.620, 0.445, 0.660, 0.445)
# shoulder rotation builds the elbow frame (stated inside the box)
arrow(ax, 0.297, 0.335, 0.297, 0.285)
# elbow frame into the flexion stage
arrow(ax, 0.390, 0.18, 0.435, 0.18)
# outputs to the angle set
arrow(ax, 0.805, 0.755, 0.918, 0.685, rad=-0.25)
arrow(ax, 0.805, 0.445, 0.845, 0.475)
arrow(ax, 0.620, 0.18, 0.845, 0.40, rad=0.18)

fig.savefig(OUT, dpi=200, bbox_inches="tight")
print("saved", OUT)

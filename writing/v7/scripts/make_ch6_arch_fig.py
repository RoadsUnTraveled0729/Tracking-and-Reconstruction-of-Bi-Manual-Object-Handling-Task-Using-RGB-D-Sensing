#!/usr/bin/env python3
"""Chapter 6 architecture figure: processes and records (V7 rewrite round).

Draws the running structure of the integration layer as it exists in the
source: one capture process publishing aligned frames into a shared frame
buffer, the two branch processes reading that buffer, the object record
feeding back into the person process for the recovery stage, and the
merger pairing both records on the shared session clock into the static
scene record and the combined per-tick record that Unity reads.

Layout follows the Chapter 2 flow figure (make_ch2_fig1.py) so the two
diagrams read as one family. Sources: v2/broker/capture_broker.py,
v2/common/shm_ring.py, v2/person/v2_person.py, v2/object/v2_object.py,
v2/common/object_link.py, v2/common/person_shm_v2.py,
v2/integration/v2_integrate.py.

Output: writing/v7/figures/ch6_fig_arch.png
Run:    python writing/v7/scripts/make_ch6_arch_fig.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "writing" / "v7" / "figures" / "ch6_fig_arch.png"

C_SENS, C_A, C_B, C_M, C_REC, C_U = ("#dbe9f6", "#e3f2df", "#fdeeda",
                                     "#ece1f2", "#f6f1cf", "#e2e2e8")
C_DEV = "#cfd8e4"


def box(ax, x, y, w, h, text, fc, fs=8.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.010",
                                fc=fc, ec="0.25", lw=1.1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def device(ax, x, y, w, h, text, fs=8.2):
    """The source itself: a squared box with a doubled left edge, so it
    reads as hardware or a stored session rather than as a process."""
    ax.add_patch(Rectangle((x, y), w, h, fc=C_DEV, ec="0.25", lw=1.1))
    ax.add_patch(Rectangle((x, y), 0.010, h, fc="0.25", ec="0.25", lw=0.6))
    ax.text(x + w / 2 + 0.005, y + h / 2, text, ha="center", va="center",
            fontsize=fs)


def record(ax, x, y, w, h, text, fs=7.8):
    """A shared-memory record: square corners, so it reads as memory."""
    ax.add_patch(Rectangle((x, y), w, h, fc=C_REC, ec="0.25", lw=1.1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def arrow(ax, x0, y0, x1, y1, rad=0.0):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=12, color="0.2", lw=1.2,
                                 connectionstyle=f"arc3,rad={rad}"))


fig, ax = plt.subplots(figsize=(11.4, 5.6))
ax.set_xlim(-0.012, 1.012)
ax.set_ylim(0, 1)
ax.axis("off")

# --- source and broker -------------------------------------------------
device(ax, 0.005, 0.42, 0.105, 0.17,
       "RGB-D source\nthe recording, or\nthe live camera", 7.8)
box(ax, 0.125, 0.42, 0.120, 0.17,
    "Capture process\naligns depth to\ncolour, stamps the\nsession clock", C_SENS, 7.8)
record(ax, 0.252, 0.430, 0.108, 0.150,
       "Shared frame\nbuffer\none writer,\nmany readers", 7.2)

# --- the two pipeline processes and their records ----------------------
box(ax, 0.375, 0.715, 0.140, 0.175,
    "Landmark branch\nlandmarks, filtering,\nkinematic solve,\npose recovery", C_A, 7.9)
record(ax, 0.530, 0.720, 0.125, 0.165,
       "Person record\npelvis, thirteen\nangles, live mask,\nsolver tags", 7.6)

box(ax, 0.375, 0.115, 0.140, 0.175,
    "Marker branch\nmarker detection,\nworld pose,\ncleaning step", C_B, 7.9)
record(ax, 0.530, 0.120, 0.125, 0.165,
       "Object record\nposition, Euler\nangles, live flag", 7.6)

# --- merger, its two output records, and the receiver ------------------
box(ax, 0.675, 0.395, 0.115, 0.215,
    "Merger\npairs the records\non the session\nclock at a fixed\noutput delay,\n"
    "display smoother", C_M, 7.9)
record(ax, 0.815, 0.635, 0.110, 0.140,
       "Static scene record\nwritten once", 7.6)
record(ax, 0.815, 0.230, 0.110, 0.140,
       "Combined record\nwritten per\noutput tick", 7.6)
box(ax, 0.940, 0.395, 0.055, 0.215, "Unity\nreceiver", C_U, 8.2)

# --- connections -------------------------------------------------------
arrow(ax, 0.110, 0.505, 0.125, 0.505)
arrow(ax, 0.245, 0.505, 0.252, 0.505)
arrow(ax, 0.360, 0.545, 0.375, 0.740)
arrow(ax, 0.360, 0.465, 0.375, 0.270)
ax.text(0.362, 0.660, "colour + depth", fontsize=7.2, color="0.25", ha="left")
ax.text(0.362, 0.350, "colour", fontsize=7.2, color="0.25", ha="left")
arrow(ax, 0.515, 0.800, 0.530, 0.800)
arrow(ax, 0.515, 0.200, 0.530, 0.200)
arrow(ax, 0.655, 0.780, 0.700, 0.615, rad=-0.12)
arrow(ax, 0.655, 0.215, 0.700, 0.390, rad=0.12)
arrow(ax, 0.802, 0.545, 0.815, 0.665)
arrow(ax, 0.802, 0.455, 0.815, 0.340)
arrow(ax, 0.925, 0.680, 0.965, 0.612, rad=-0.10)
arrow(ax, 0.925, 0.290, 0.965, 0.395, rad=0.10)

# the object record conditions the recovery inside Pipeline A
arrow(ax, 0.560, 0.290, 0.450, 0.710, rad=0.30)
ax.text(0.545, 0.470, "object pose for the\nrecovery of Chapter 5",
        fontsize=7.2, color="0.25", ha="right", va="center",
        bbox=dict(fc="white", ec="none", pad=1.4))

ax.text(0.445, 0.945, "Landmark branch: person tracking", fontsize=9.4,
        color="#3a6b35", ha="center")
ax.text(0.445, 0.050, "Marker branch: scene and object tracking", fontsize=9.4,
        color="#8a5a1e", ha="center")
ax.text(0.005, 0.320,
        "Rounded boxes are processes;\nsquare boxes are shared-memory\n"
        "records; the box at the left is\nthe source itself. Every record\n"
        "is fixed size and names the\nframe it belongs to.",
        fontsize=7.8, color="0.3", style="italic", va="top")

plt.tight_layout()
plt.savefig(OUT, dpi=150)
print("saved", OUT)

#!/usr/bin/env python3
"""Chapter 6 reconstruction figure: two Unity frames of the rail recording.

Rail-only round (2026-09-01): the panels are two frames captured from
the running Unity scene fed by the rail recording's RECOVERY stream
(autonomous editor capture, eval/unity_check/run_unity_capture.py --stem
recording_20260831_065553 --angles-csv eval/output/recovery_r6b/
angles_recovery.csv, E-027 layer; the per-frame PNGs are named by the
streamed frame index). The two captures are copied to writing/v9/
figures/src/r6b_unity_f00114.png and r6b_unity_f00700.png so the figure
rebuilds without Unity. Frame 114: the desk move, the cube on the desk.
Frame 700: the slide, the hand on the cube on the rail. Red spheres are
the held/constrained group markers of the receiver, on the joint they
mark (recaptured 2026-09-07 with HeldMarkers.cs placing the push toward
the rendering camera; the earlier captures floated them off the body).

Output: writing/v9/figures/ch6_fig_unity.png
Run:    python writing/v9/scripts/make_ch6_unity_fig.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "writing" / "v9" / "figures" / "src"
OUT = REPO / "writing" / "v9" / "figures" / "ch6_fig_unity.png"

# source captures are 640 x 480 Unity renders; used whole
UNITY_BOX = (0, 0, 640, 480)

# direct labels, in cropped-panel pixel coordinates (origin upper left):
# (text, text anchor, arrow tip, horizontal alignment)
LABELS_A = [
    ("wall marker", (18, 62), (118, 148), "left"),
    ("object cube", (18, 430), (176, 372), "left"),
    ("desk marker", (604, 452), (348, 430), "right"),
    ("held group markers", (604, 96), (402, 64), "right"),
]
LABELS_B = [
    ("wall marker", (18, 62), (118, 148), "left"),
    ("object cube", (18, 430), (272, 300), "left"),
    ("desk marker", (604, 452), (348, 430), "right"),
]

PANELS = [("r6b_unity_f00114.png", "(a)", LABELS_A),
          ("r6b_unity_f00700.png", "(b)", LABELS_B)]

fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.3))
for ax, (name, tag, labels) in zip(axes, PANELS):
    img = Image.open(SRC / name).crop(UNITY_BOX)
    ax.imshow(img)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ax.spines.values():
        side.set_edgecolor("0.4")
        side.set_linewidth(0.9)
    ax.set_title(tag, fontsize=11, loc="left", pad=5)
    for text, at, tip, ha in labels:
        ax.annotate(text, xy=tip, xytext=at, ha=ha, va="center",
                    fontsize=8.4, color="0.08",
                    bbox=dict(fc="white", ec="0.55", lw=0.7,
                              boxstyle="round,pad=0.22", alpha=0.92),
                    arrowprops=dict(arrowstyle="-", color="0.15", lw=1.0,
                                    shrinkA=2, shrinkB=1))

plt.tight_layout()
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print("saved", OUT)

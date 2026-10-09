#!/usr/bin/env python3
"""Chapter 8 figure: measured per-stage cost against the frame budget.

One-glance panel: every timed stage as a horizontal bar (median, with a
whisker out to the 99th percentile) on a linear time axis, against the
33.3 ms budget of a 30 frames-per-second camera. The two detectors
dominate; the kinematic solve is more than twenty times cheaper than the
detector that feeds it.

ONE RUN ONLY. Every value here, stages and branch totals alike, comes
from the per-stage profile blocks of v2/dataset/r6b_probe_baseline_off.txt (rail recording, recovery and gate off; rail-only round 2026-09-01),
the run with the object-conditioned recovery and the other opt-in live
features switched off:
  broker   "[stage] align+publish ms"        2.36 / 2.54 / 2.67
  person   "=== per-stage profile (ms) ==="  mediapipe, deproj+filt,
           solve, and that block's total row 8.78 / 22.62 / 26.61
  object   "=== per-stage profile (ms) ==="  detect, pnp, filter+map,
           and that block's total row       13.27 / 14.11 / 14.63
The end-to-end numbers of the FULL-feature run are deliberately not
drawn here; they live in Table 8.3 of the chapter.

Output: writing/v7/figures/ch8_fig_cost.png
Run:    python writing/v7/scripts/make_ch8_cost_fig.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "writing" / "v7" / "figures" / "ch8_fig_cost.png"

C_CAP = "#4a4e69"      # capture
C_PER = "#7b2cbf"      # person branch
C_OBJ = "#1b7f79"      # object branch
C_TOT = "#343a40"      # branch end-to-end
C_BUD = "#c1121f"      # budget line

BUDGET = 33.3

# (label, p50, p99, colour, is_total)
ROWS = [
    ("marker branch, end to end",             14.13, 16.40, C_OBJ, True),
    ("marker: filtering and world mapping",     0.17,  0.22, C_OBJ, False),
    ("marker: planar pose estimation",          0.15,  0.23, C_OBJ, False),
    ("marker: detection",                      13.79, 16.03, C_OBJ, False),
    ("landmark branch, end to end",             8.03, 12.64, C_PER, True),
    ("landmark: kinematic solve",               0.18,  0.25, C_PER, False),
    ("landmark: deprojection and filtering",    0.41,  0.57, C_PER, False),
    ("landmark: pose detection",                7.42, 12.00, C_PER, False),
    ("capture: alignment and publication",      2.41,  3.08, C_CAP, False),
]

fig, ax = plt.subplots(figsize=(10.2, 5.0))
ys = range(len(ROWS))

for y, (label, p50, p99, colour, is_total) in zip(ys, ROWS):
    h = 0.56 if is_total else 0.44
    ax.barh(y, p50, height=h, color=colour,
            alpha=1.0 if is_total else 0.80,
            edgecolor=colour, zorder=3)
    ax.plot([p50, p99], [y, y], color=colour, lw=1.4, zorder=4)
    ax.plot([p99, p99], [y - 0.17, y + 0.17], color=colour, lw=1.4,
            zorder=4)
    if p50 >= 2.0:
        ax.text(p50 - 0.45, y, f"{p50:.2f}", va="center", ha="right",
                fontsize=10, color="white",
                fontweight="bold" if is_total else "normal", zorder=5)
    else:
        ax.text(p50 + 0.45, y, f"{p50:.2f}", va="center", ha="left",
                fontsize=10, color=colour, zorder=5)
    off = 3.2 if p50 < 2.0 else 0.6
    ax.text(p99 + off, y, f"p99 {p99:.2f}", va="center", ha="left",
            fontsize=8.5, color="#495057", zorder=5)

ax.axvline(BUDGET, color=C_BUD, ls="--", lw=1.8, zorder=2)
ax.text(BUDGET - 0.7, len(ROWS) - 0.55,
        "frame budget 33.3 ms at 30 fps", color=C_BUD, fontsize=10,
        va="top", ha="right")

ax.set_yticks(list(ys))
ax.set_yticklabels([r[0] for r in ROWS], fontsize=10)
for tick, row in zip(ax.get_yticklabels(), ROWS):
    tick.set_color(row[3])
ax.set_xlim(0, 39)
ax.set_ylim(-0.7, len(ROWS) - 0.25)
ax.set_xlabel("time per frame (ms)", fontsize=10.5)
ax.set_xticks([0, 5, 10, 15, 20, 25, 30, 33.3])
ax.set_xticklabels(["0", "5", "10", "15", "20", "25", "30", "33.3"],
                   fontsize=9.5)
ax.grid(axis="x", ls=":", color="#adb5bd", zorder=0)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)

fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=200)
print("saved", OUT)

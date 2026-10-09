#!/usr/bin/env python3
"""Chapter 8 figure: where the end-to-end delay of the live path goes.

One-glance timeline of a single captured frame: capture and publication,
the two branches computing concurrently (median bar, lighter extension to
the 99th percentile), and the merger's fixed declared delay of two frame
intervals before that frame is rendered. The compute finishes well inside
the first frame interval, so the delay a viewer sees is the declared one.

Numbers (do not edit without re-reading the sources):
  align and publish 2.36 ms          v2/dataset/r6b_probe_baseline.txt
                                     ("[stage] align+publish ms")
  landmark branch p50 9.0 / p99 25.1 v2/dataset/r6b_probe_validation.txt
                                     (the FULL-feature run)
  marker branch p50 13.1 / p99 15.1  v2/dataset/r6b_probe_validation.txt
                                     (the FULL-feature run)
  declared delay 2 frames 66.7 ms    v2/dataset/r6b_probe_baseline.txt
                                     ("delay 2 frame(s) = 66.7 ms")

Output: writing/v7/figures/ch8_fig_latency.png
Run:    python writing/v7/scripts/make_ch8_latency_fig.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "writing" / "v7" / "figures" / "ch8_fig_latency.png"

C_CAP = "#4a4e69"
C_PER = "#7b2cbf"
C_OBJ = "#1b7f79"
C_DEL = "#c1121f"
C_GRID = "#adb5bd"

FRAME = 33.3
DELAY = 66.7
PUB = 2.36  # r6b_probe_baseline.txt (full run) align+publish p50

fig, ax = plt.subplots(figsize=(10.2, 4.0))

for k in (0, 1, 2, 3):
    ax.axvline(k * FRAME, color=C_GRID, ls=":", lw=1.0, zorder=1)
    ax.text(k * FRAME + 1.2, 3.62, f"frame k+{k}" if k else "frame k",
            fontsize=9, color="#495057", ha="left", va="bottom")

# capture and publication
ax.barh(3.0, PUB, left=0.0, height=0.42, color=C_CAP, zorder=3)
ax.text(PUB + 1.5, 3.0, "depth alignment and publication to the shared frame buffer",
        fontsize=9.5, va="center", color=C_CAP)

# landmark branch
ax.barh(2.2, 8.4, left=PUB, height=0.42, color=C_PER, zorder=3)
ax.barh(2.2, 13.0 - 8.4, left=PUB + 8.4, height=0.42, color=C_PER,
        alpha=0.32, zorder=3)
ax.text(PUB + 13.0 + 1.5, 2.2, "landmark branch: median 8.4, p99 13.0",
        fontsize=9.5, va="center", color=C_PER)

# marker branch
ax.barh(1.4, 14.0, left=PUB, height=0.42, color=C_OBJ, zorder=3)
ax.barh(1.4, 16.7 - 14.0, left=PUB + 14.0, height=0.42, color=C_OBJ,
        alpha=0.32, zorder=3)
ax.text(PUB + 16.7 + 1.5, 1.4, "marker branch: median 14.0, p99 16.7",
        fontsize=9.5, va="center", color=C_OBJ)

# declared delay
ax.annotate("", xy=(DELAY, 0.55), xytext=(0.0, 0.55),
            arrowprops=dict(arrowstyle="<->", color=C_DEL, lw=1.6))
ax.text(DELAY / 2.0, 0.72,
        "declared output delay: two frame intervals, 66.7 ms",
        fontsize=10, color=C_DEL, ha="center")
ax.axvline(DELAY, color=C_DEL, lw=1.8, zorder=2)
ax.text(DELAY + 2.0, 0.22, "the merger renders frame k\nand sends it onward",
        fontsize=9.5, color=C_DEL, va="center")

ax.set_xlim(-1.5, 112)
ax.set_ylim(0.0, 3.9)
ax.set_yticks([])
ax.set_xlabel("time since the frame was captured (ms)", fontsize=10.5)
ax.set_xticks([0, 33.3, 66.7, 100])
ax.set_xticklabels(["0", "33.3", "66.7", "100"], fontsize=9.5)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)

fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=200)
print("saved", OUT)

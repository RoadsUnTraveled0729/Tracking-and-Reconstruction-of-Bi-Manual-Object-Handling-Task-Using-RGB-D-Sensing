#!/usr/bin/env python3
"""Figure 7.2 (v4): the solver benchmark, trimmed to the two implementations
the system actually runs (user decision 2026-07-31).

Data: the pinned realtime/dataset/bench_solver.csv, arms filtered to
  scalar-loop  -> "per-frame solver (deployed)"
  numpy-vec    -> "vectorized numpy (offline batch)"
Left panel: per-frame latency at N=1. Right panel: us/frame vs batch size.
Replaces the v2 copy of bench_solver.png (numba/GPU panels), which would
contradict the trimmed Table 7.2.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

CSV = "/home/luo/Desktop/New_SandBox/realtime/dataset/bench_solver.csv"
OUT = "/home/luo/Desktop/New_SandBox/writing/v4/figures/ch7_fig2_bench_v4.png"

LABELS = {"scalar-loop": "per-frame solver (deployed)",
          "numpy-vec": "vectorized numpy (offline batch)"}
COLORS = {"scalar-loop": "#e6a117", "numpy-vec": "#1f77b4"}

df = pd.read_csv(CSV)
df = df[df.impl.isin(LABELS)].copy()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.6))

# left: N=1 latency bars
n1 = df[df.n == 1].set_index("impl").loc[list(LABELS)]
bars = ax1.barh([LABELS[i] for i in n1.index], n1.us_per_frame,
                color=[COLORS[i] for i in n1.index], height=0.5)
for b, v in zip(bars, n1.us_per_frame):
    ax1.text(v + 2, b.get_y() + b.get_height() / 2, f"{v:.0f}",
             va="center", fontsize=10)
ax1.set_xlim(0, 125)
ax1.invert_yaxis()
ax1.set_xlabel("per-frame latency at N = 1 (µs)")
ax1.set_title("Real-time case: one frame at a time", fontsize=11)
ax1.spines[["top", "right"]].set_visible(False)

# right: us/frame vs batch size (log-log)
for impl in LABELS:
    d = df[df.impl == impl].sort_values("n")
    ax2.plot(d.n, d.us_per_frame, "-o", ms=4, color=COLORS[impl],
             label=LABELS[impl])
ax2.set_xscale("log")
ax2.set_yscale("log")
ax2.set_xlabel("batch size N (frames)")
ax2.set_ylabel("µs per frame (log)")
ax2.set_title("Batch regime: offline reprocessing", fontsize=11)
ax2.legend(fontsize=9, frameon=False)
ax2.grid(True, which="both", alpha=0.25)
ax2.spines[["top", "right"]].set_visible(False)

fig.suptitle("13-angle kinematic solve: deployed per-frame solver vs "
             "vectorized batch solver", fontsize=12, x=0.02, ha="left")
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("saved", OUT)

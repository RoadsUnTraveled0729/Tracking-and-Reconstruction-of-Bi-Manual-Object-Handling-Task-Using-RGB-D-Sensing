#!/usr/bin/env python3
"""Chapter 7 figure: frames the failure detectors reject over the rail
recording (recording_20260831_065553), one band per entity, the same
drawing as fig_failures in make_ch7_figs.py (which stays pinned to the
loop recording). Annotations name the rail recording's own windows
(eval/reports/r6b_failure_mask.md): the right-wrist visibility gap
mid-slide (frames 550-639, acquisition detector) and the torso window
from frame 632 to the end, where the two hips read depths 19 cm apart.
The idle left arm is low-visibility for almost the whole take.

Output: writing/v7/figures/ch7_fig_failures_rail.png
Run:    python writing/v7/scripts/make_ch7_rail_failures_fig.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v7" / "figures"
STEM = "recording_20260831_065553"
RECOV = REPO / "eval" / "output" / "recovery_r6b"
REPORTS = REPO / "eval" / "reports"
plt.rcParams.update({"font.size": 9, "axes.titlesize": 10,
                     "figure.dpi": 200, "savefig.dpi": 200,
                     "font.family": "DejaVu Sans"})


def runs(mask):
    idx = np.flatnonzero(mask)
    if idx.size == 0:
        return []
    brk = np.flatnonzero(np.diff(idx) > 1)
    return list(zip(np.r_[idx[0], idx[brk + 1]].tolist(),
                    np.r_[idx[brk], idx[-1]].tolist()))


fm = pd.read_csv(RECOV / "failure_mask.csv")
t = fm["time_s"].to_numpy()
ph = json.loads((REPORTS / f"{STEM}_inspection.json").read_text())["phases"]
rows = [("torso", "fail_torso", "tab:purple"),
        ("left arm", "fail_arm_L", "tab:blue"),
        ("right arm", "fail_arm_R", "tab:red")]
span0 = ph["person_present"][0] + 5
step, half = 1.6, 0.30
ypos = [(len(rows) - 1 - k) * step for k in range(len(rows))]
fig, ax = plt.subplots(figsize=(9.0, 3.1))
pcts = {}
for k, (label, col, colour) in enumerate(rows):
    y = ypos[k]
    m = fm[col].to_numpy().astype(bool)
    ax.add_patch(plt.Rectangle((t[0], y - half), t[-1] - t[0], 2 * half,
                               facecolor="0.93", edgecolor="none"))
    for a, b in runs(m):
        ax.add_patch(plt.Rectangle((t[a], y - half), max(t[b] - t[a], 0.08),
                                   2 * half, facecolor=colour, edgecolor="none"))
    pct = 100.0 * m[span0:].mean()
    pcts[label] = pct
    ax.text(t[-1] + 0.6, y, f"{pct:.1f}%", va="center", fontsize=8.5, color=colour)
for a, b in [ph["approach"], ph["manipulation"]]:
    ax.axvline(t[a], color="0.55", lw=0.8, ls=":")
ax.text(t[ph["approach"][0]] + 0.4, ypos[0] + 0.90, "approach", fontsize=8, color="0.35")
ax.text(t[ph["manipulation"][0]] + 0.4, ypos[0] + 0.90, "manipulation", fontsize=8, color="0.35")
ann = [(632, 899, ypos[0], "the two hips read depths 19 cm apart"),
       (100, 517, ypos[1], "idle arm, low visibility"),
       (550, 639, ypos[2], "right wrist not seen mid-slide")]
for a, b, y, label in ann:
    ax.annotate(label, xy=(0.5 * (t[a] + t[b]), y + half),
                xytext=(0.5 * (t[a] + t[b]), y + 0.62), ha="center",
                fontsize=7.5, color="0.2",
                arrowprops=dict(arrowstyle="-", lw=0.7, color="0.4"))
ax.set_yticks(ypos)
ax.set_yticklabels([r[0] for r in rows])
ax.set_ylim(-0.9, ypos[0] + 1.25)
ax.set_xlim(t[0], t[-1] + 3.2)
ax.set_xlabel("time (s)")
ax.set_title("frames the failure detectors reject, over the rail recording")
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.tick_params(axis="y", length=0)
fig.tight_layout()
out = FIG / "ch7_fig_failures_rail.png"
fig.savefig(out)
print("wrote", out, {k: round(v, 1) for k, v in pcts.items()})

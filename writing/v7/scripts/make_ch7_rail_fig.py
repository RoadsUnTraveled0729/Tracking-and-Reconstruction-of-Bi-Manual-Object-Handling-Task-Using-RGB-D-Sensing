#!/usr/bin/env python3
"""Chapter 7 rail-scenario figure (scenario separation round, E-023).

Reproduces the rail evaluation view for the thesis from the cleaned
object track of the rail recording, using the same segmentation and
total-least-squares fit as eval/gt/eval_rail_scenario.py (imported, not
copied). Differences from the eval report figure: thesis wording in the
titles (no recording shorthand), Chapter 2/3 figure typography.

Output: writing/v7/figures/ch7_fig_rail.png
Run:    python writing/v7/scripts/make_ch7_rail_fig.py
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "eval" / "common"))
sys.path.insert(0, str(REPO / "eval" / "gt"))
import eval_rail_scenario as ers  # noqa: E402

STEM = "recording_20260831_065553"

track = ers.load_track(STEM)
seg = ers.segment(track)
xyz, t = track["xyz"], track["time_s"]
c, d, along, resid_vec, _ = ers.fit_line(xyz[seg["rail"]])
if d[0] < 0:
    d = -d
    along = -along

P = xyz[track["valid"]]
Tv = t[track["valid"]]
fig = plt.figure(figsize=(12, 5.0))
ax = fig.add_subplot(121, projection="3d")
sc = ax.scatter(P[:, 0], P[:, 2], P[:, 1], c=Tv, s=3, cmap="viridis")
lo, hi = along.min(), along.max()
ends = np.array([c + lo * d, c + hi * d])
ax.plot(ends[:, 0], ends[:, 2], ends[:, 1], "r-", lw=2,
        label="fitted rail line")
ax.set_xlabel("x (m)")
ax.set_ylabel("z (m)")
ax.set_zlabel("y up (m)")
ax.set_title("tracked trajectory and the rail line (colour = time)",
             fontsize=10)
ax.legend(loc="upper left", fontsize=8)
fig.colorbar(sc, ax=ax, shrink=0.55, label="time (s)")
ax2 = fig.add_subplot(222)
ax2.plot(along * 100, resid_vec[:, 1] * 100, ".", ms=2.5)
ax2.axhline(0, color="r", lw=1)
ax2.set_ylabel("vertical deviation (cm)")
ax2.set_title("deviation from the rail line along the slide", fontsize=10)
ax3 = fig.add_subplot(224)
ax3.plot(along * 100, resid_vec[:, 2] * 100, ".", ms=2.5)
ax3.axhline(0, color="r", lw=1)
ax3.set_xlabel("position along the rail (cm)")
ax3.set_ylabel("depth deviation (cm)")
plt.tight_layout()
out = REPO / "writing" / "v7" / "figures" / "ch7_fig_rail.png"
plt.savefig(out, dpi=160)
print("saved", out)

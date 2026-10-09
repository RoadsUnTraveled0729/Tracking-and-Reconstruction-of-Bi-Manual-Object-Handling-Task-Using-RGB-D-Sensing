#!/usr/bin/env python3
"""Figure 7.5 with correct marker-origin labels; the input track is unchanged."""
import sys
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from ch7_trail_data import REPO, ROOT, WAYPOINTS
from draw_ch7_trajectories import settle_3d, trim
sys.path.insert(0, str(REPO / "eval/gt"))
import eval_rail_scenario as ers  # noqa: E402

track = ers.load_track("recording_20260831_065553")
phase = ers.segment(track)
xyz = track["xyz"] * 100
c, d, along, _, _ = ers.fit_line(track["xyz"][phase["rail"]])
ends = np.array([c + along.min() * d, c + along.max() * d]) * 100
waypoints = json.loads(WAYPOINTS.read_text())["waypoints"]
reference = np.array([waypoints[name] for name in ("start", "W1", "W2", "W3")]) * 100
fig = plt.figure(figsize=(8, 3.9), layout="constrained")
ax = fig.add_subplot(111, projection="3d")
ax.plot(reference[:, 0], reference[:, 2], reference[:, 1], "--", color="0.2", lw=1,
        label="Waypoint reference")
ax.plot(ends[:, 0], ends[:, 2], ends[:, 1], color="0.5", lw=1, label="Fitted rail line")
ax.plot(xyz[:, 0], xyz[:, 2], xyz[:, 1], color="tab:green", lw=1.2,
        label="Marker origin")
for name, point in zip(("Start", "W1", "W2", "W3"), reference):
    ax.scatter(point[0], point[2], point[1], color="0.2", s=20)
    ax.text(point[0], point[2], point[1], name, fontsize=9)
ax.set_xlabel("x (cm)", labelpad=14); ax.set_ylabel("z (cm)", labelpad=10); ax.set_zlabel("y (cm)", labelpad=6)
points = np.vstack([xyz[track["valid"]], reference])
span = np.ptp(points, axis=0)
ax.set_box_aspect(span[[0, 2, 1]], zoom=0.9)
ax.zaxis.set_major_locator(MaxNLocator(nbins=2))
ax.view_init(elev=25, azim=-58)
content = settle_3d(fig, ax)
fig.legend(loc="upper center", bbox_to_anchor=(0.5, content.y0 - 0.01), ncol=3, fontsize=9, frameon=False)
out = ROOT / "figures/ch7_fig_rail_traj.png"
fig.savefig(out, dpi=260, bbox_inches="tight", pad_inches=0.05)
trim(out)
print("saved", out)

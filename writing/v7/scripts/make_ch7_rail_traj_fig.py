#!/usr/bin/env python3
"""Chapter 7 figure: the reconstructed object trajectory of the rail
recording in the gravity-levelled world, with the designed reference
path drawn as an axis-aligned polyline (user definition, 2026-09-01):
  leg 1  from the parked start straight back, away from the camera
         (z only), to W1, the foot of the lift at the rail's depth;
  leg 2  straight up (y only) to W2, the start of the rail at rail
         height;
  leg 3  along the rail (x only) to W3, the far end of the rail.
The corner positions come from the physical geometry, not from the
track's own corners: the parked start (mean of the parked frames), the
depth and height of the rail line fitted to the slide samples, and the
far end of that line. Track, segmentation, levelling and the line fit
come from eval/gt/eval_rail_scenario.py (imported, not re-implemented);
the reference path is written to eval/reports/r6b_waypoints.json so the
chapter text can cite it.

Output: writing/v7/figures/ch7_fig_rail_traj.png
Run:    python writing/v7/scripts/make_ch7_rail_traj_fig.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "eval" / "common"))
sys.path.insert(0, str(REPO / "eval" / "gt"))
sys.path.insert(0, str(REPO / "eval" / "offset"))
import eval_rail_scenario as ers  # noqa: E402

STEM = "recording_20260831_065553"
OUT = REPO / "writing" / "v7" / "figures" / "ch7_fig_rail_traj.png"
WP_OUT = REPO / "eval" / "reports" / "r6b_waypoints.json"

track = ers.load_track(STEM)
seg = ers.segment(track)
xyz, t, fr, valid = track["xyz"], track["time_s"], track["frame"], track["valid"]
idx = seg["idx"]
P = xyz[idx]
h = np.convolve(P[:, 1], np.ones(9) / 9, mode="same")
desk_y, rail_y = seg["desk_y"], seg["rail_y"]

start = xyz[seg["parked"]].mean(axis=0)
c, d, along, _, _ = ers.fit_line(xyz[seg["rail"]])
if d[0] < 0:
    d, along = -d, -along
ends = np.array([c + along.min() * d, c + along.max() * d])
rail_y = float(c[1])                      # height of the fitted rail line
rail_z = float(c[2])                      # depth of the fitted rail line
x_end = float(ends[1, 0])                 # far end of the rail line
W = {"start": start,
     "W1": np.array([start[0], start[1], rail_z]),   # straight back
     "W2": np.array([start[0], rail_y, rail_z]),     # straight up
     "W3": np.array([start[0] + (x_end - start[0]), rail_y, rail_z])}  # along the rail
legs = {"leg1_back_cm": float(rail_z - start[2]) * 100,
        "leg2_up_cm": float(rail_y - start[1]) * 100,
        "leg3_rail_cm": float(x_end - start[0]) * 100}
# where the track actually turns, for the text (not part of the reference)
h = np.convolve(P[:, 1], np.ones(9) / 9, mode="same")
k_lift = int(np.flatnonzero(h > desk_y + 0.01)[0])
k_rail = int(np.flatnonzero(h >= rail_y - 0.005)[0])
turns = {"lift_begins_frame": int(fr[idx[k_lift]]), "rail_reached_frame": int(fr[idx[k_rail]]),
         "last_frame": int(fr[idx[-1]]), "parked_frames": [int(fr[seg["parked"][0]]), int(fr[seg["parked"][-1]])]}
spec = {"stem": STEM, "frame": "gravity-levelled desk world (x, y up, z away from the camera), metres",
        "definition": {"leg1": "from the parked start straight back (z only) to W1, the foot of the lift at the depth of the fitted rail line",
                       "leg2": "straight up (y only) to W2, the start of the rail at the height of the fitted rail line",
                       "leg3": "along the rail (x only) to W3, the far end of the fitted rail line"},
        "waypoints": {k: [round(float(v), 4) for v in W[k]] for k in W},
        "legs_cm": {k: round(v, 2) for k, v in legs.items()},
        "rail_line": {"height_m": round(rail_y, 4), "depth_m": round(rail_z, 4),
                      "x_from_m": round(float(ends[0, 0]), 4), "x_to_m": round(x_end, 4)},
        "desk_level_m": round(desk_y, 4), "track_turns": turns}
WP_OUT.write_text(json.dumps(spec, indent=1))
for k in ("start", "W1", "W2", "W3"):
    print("%-5s x=%+.3f y=%+.3f z=%+.3f" % (k, *W[k]))
print("legs (cm):", spec["legs_cm"], "| track turns:", turns)

fig = plt.figure(figsize=(9, 6.6))
ax = fig.add_subplot(111, projection="3d")
ref = np.vstack([start, W["W1"], W["W2"], W["W3"]])
ax.plot(ref[:, 0], ref[:, 2], ref[:, 1], color="tab:red", lw=2.2, ls="--",
        label="reference path: back to W1, up to W2, along the rail to W3")
ax.plot(ends[:, 0], ends[:, 2], ends[:, 1], color="k", lw=1.2, alpha=0.7, label="fitted rail line")
ax.plot(P[:, 0], P[:, 2], P[:, 1], color="tab:blue", lw=1.3, label="tracked cube centre")
ax.scatter(start[0], start[2], start[1], s=60, color="white", edgecolor="k", zorder=6)
ax.text(start[0], start[2], start[1] - 0.02, "start", fontsize=9)
for k in ("W1", "W2", "W3"):
    w = W[k]
    ax.scatter(w[0], w[2], w[1], s=80, color="tab:red", edgecolor="k", zorder=6)
    ax.text(w[0], w[2], w[1] + 0.012, k, fontsize=10, weight="bold")
ax.set_xlabel("x (m)")
ax.set_ylabel("z (m), away from the camera")
ax.set_zlabel("height above the desk marker (m)")
ax.set_box_aspect((np.ptp(P[:, 0]), np.ptp(P[:, 2]), np.ptp(P[:, 1]) * 2.0))
ax.view_init(elev=22, azim=-50)
ax.legend(loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig(OUT, dpi=160)
print("saved", OUT)

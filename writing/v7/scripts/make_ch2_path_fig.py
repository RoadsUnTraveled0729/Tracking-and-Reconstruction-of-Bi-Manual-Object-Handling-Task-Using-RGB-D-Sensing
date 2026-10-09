#!/usr/bin/env python3
"""Chapter 2 designed-object-path figure (V7 rewrite round).

Draws the designed loop of the handling task: the eight stations and
the straight segments between them, in the gravity-leveled world frame,
over the desk plane. Geometry comes from the frozen R5 path
specification. The figure shows the design only; the measured
trajectory and its comparison against this polyline belong to the
evaluation chapter, and no speed information appears anywhere.

Output: writing/v7/figures/ch2_fig_path.png
Run:    python writing/v7/scripts/make_ch2_path_fig.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[3]
spec = json.loads((REPO / "eval" / "gt" / "labeled_path_r5.json").read_text())

wps = {w["id"]: np.array(w["leveled_xyz"]) for w in spec["waypoints"]}
order = [w["id"] for w in spec["waypoints"]]
short = {"W1_start": "W1 start", "W2_back_end": "W2 back",
         "W3_desk_handover": "W3 handover", "W4_left_end": "W4 left",
         "W5_forward_end": "W5 forward", "W6_lift_top": "W6 lift top",
         "W7_wire_handover": "W7 wire handover", "W8_wire_left": "W8 wire left"}

P = np.array([wps[k] for k in order])
loop = np.vstack([P, P[0]])          # the task returns to the start

# matplotlib's third axis renders vertically, so plot (x, z, y): the
# leveled frame's y (up) becomes the plot's vertical axis.
fig = plt.figure(figsize=(8.4, 6.6))
ax = fig.add_subplot(111, projection="3d")

# desk plane at the mean height of the five desk stations
desk_y = float(P[:5, 1].mean())
xs = [P[:, 0].min() - 0.12, P[:, 0].max() + 0.12]
zs = [P[:, 2].min() - 0.12, P[:, 2].max() + 0.12]
X, Z = np.meshgrid(xs, zs)
ax.plot_surface(X, Z, np.full_like(X, desk_y - 0.01),
                color="#d8c49a", alpha=0.35, shade=False)

ax.plot(loop[:, 0], loop[:, 2], loop[:, 1], "-", color="#c1121f",
        lw=2.0, zorder=4)
ax.scatter(P[:, 0], P[:, 2], P[:, 1], s=60, color="#c1121f",
           edgecolor="black", depthshade=False, zorder=5)

off = {"W1_start": (0.015, -0.05), "W2_back_end": (-0.06, 0.035),
       "W3_desk_handover": (-0.03, -0.055), "W4_left_end": (0.025, 0.02),
       "W5_forward_end": (0.025, -0.03), "W6_lift_top": (0.025, 0.015),
       "W7_wire_handover": (0.0, 0.045), "W8_wire_left": (-0.16, 0.03)}
for k in order:
    p = wps[k]
    dx, dy = off[k]
    ax.text(p[0] + dx, p[2], p[1] + dy, short[k], fontsize=9, zorder=6)

# wire level guide through the three elevated stations
wire_y = float(P[5:, 1].mean())
wire_z = float(P[5:, 2].mean())
ax.plot([P[7, 0] - 0.10, P[5, 0] + 0.10], [wire_z, wire_z],
        [wire_y, wire_y], color="#6c757d", lw=1.2, ls=":")
ax.text(P[7, 0] - 0.13, wire_z, wire_y - 0.05, "wire level",
        fontsize=8.5, color="#495057")
ax.text(xs[0] + 0.03, zs[0] + 0.06, desk_y + 0.012, "desk surface",
        fontsize=8.5, color="#7a6a45")

ax.set_xlabel("x (m)")
ax.set_ylabel("z (m)")
ax.set_zlabel("height (m)", labelpad=8)
ax.set_title("The designed loop: eight stations and the straight "
             "segments between them", fontsize=10)
ax.view_init(elev=24, azim=-55)
ax.set_box_aspect((np.ptp(xs), np.ptp(zs),
                   max(np.ptp(P[:, 1]) + 0.15, 0.4)))

out = REPO / "writing" / "v7" / "figures" / "ch2_fig_path.png"
plt.savefig(out, dpi=200, bbox_inches="tight")
print("saved", out)

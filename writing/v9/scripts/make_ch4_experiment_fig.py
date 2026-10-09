#!/usr/bin/env python3
"""Chapter 4 figure: the object marker as the camera sees it (supervisor
round 5, C49: show images of the experiment in Chapter 4).

A 2 by 2 grid of colour frames of the rail recording at the four moments
of the task that the Chapter 7 strip uses (figures/ch7_frames_strip.json):
the cube grasped on the desk (frame 95), the lift onto the rail (505),
the slide along the rail (700) and the far end of the rail (898). On each
frame the detected object marker is outlined and its frame O drawn from
the pose the detector returns, and the world frame W is drawn on the desk
marker. The wall marker is left undrawn.

Inputs: the colour frames figures/src/r6b_frame{idx:05d}.png (extracted
by make_ch7_frame_strip.py --extract), the UNSCALED raw detections
v1/aruco/output/<stem>_aruco_raw.csv (the E-009a scale acts along the
camera ray, so the marker centre projects to the same pixel either way,
but only the unscaled pose puts the axis tips and the outline on the
printed marker), and the colour intrinsics of
eval/output/<stem>_aruco_raw_scaled.meta.json. The axis drawer is
writing/v9/scripts/frame_draw.py, shared with Figure 2.5.

Output: writing/v9/figures/ch4_fig_experiment.png
Run:    python writing/v9/scripts/make_ch4_experiment_fig.py
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
import pandas as pd
import cv2

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "v1" / "aruco"))
sys.path.insert(0, str(REPO / "writing" / "v9" / "scripts"))
from frames import rt_from_row, make_T  # noqa: E402
from frame_draw import draw_axes, project  # noqa: E402

STEM = "recording_20260831_065553"
EOUT = REPO / "eval" / "output"
FIGD = REPO / "writing" / "v9" / "figures"
SRC = FIGD / "src"
OUT = FIGD / "ch4_fig_experiment.png"
OBJ_ID, DESK_ID = 1, 2
HALF = 0.025          # half side of the marker as the frozen extractor declared it (50 mm)
AXIS_LEN = 0.035      # metres, both frames
OUTLINE = "#ffd200"   # the yellow of Figure 2.6 (ch2_fig_aruco.png)

PANELS = [("a", 95, "grasp on the desk"),
          ("b", 505, "lift onto the rail"),
          ("c", 700, "slide along the rail"),
          ("d", 898, "far end of the rail")]

meta = json.loads((EOUT / f"{STEM}_aruco_raw_scaled.meta.json").read_text())
INTR = meta["color_intrinsics"]
raw = pd.read_csv(REPO / "v1" / "aruco" / "output" / f"{STEM}_aruco_raw.csv")

fig, axes = plt.subplots(2, 2, figsize=(10.4, 8.0))
fig.subplots_adjust(left=0.01, right=0.99, top=0.96, bottom=0.01,
                    wspace=0.03, hspace=0.10)

for ax, (tag, idx, label) in zip(axes.ravel(), PANELS):
    img = cv2.cvtColor(cv2.imread(str(SRC / f"r6b_frame{idx:05d}.png")),
                       cv2.COLOR_BGR2RGB)
    ax.imshow(img)
    row = raw[raw.frame == idx].iloc[0]
    T_obj = make_T(*rt_from_row(row, OBJ_ID))
    T_desk = make_T(*rt_from_row(row, DESK_ID))

    # outline of the detected object marker: its four corners in the
    # marker frame carried through the detected pose and projected
    corners = np.array([[-HALF, -HALF, 0], [HALF, -HALF, 0],
                        [HALF, HALF, 0], [-HALF, HALF, 0]])
    cam = (T_obj[:3, :3] @ corners.T).T + T_obj[:3, 3]
    uv = project(cam, INTR)
    ax.add_patch(Polygon(uv, closed=True, fill=False, ec=OUTLINE, lw=2.0))

    # the object frame O and the world frame W
    uv_o = project(T_obj[:3, 3][None, :], INTR)[0]
    o_lab = (-46, -34) if uv_o[0] < 400 else (-52, -34)
    draw_axes(ax, T_obj, AXIS_LEN, "O", INTR, label_dxy=o_lab, fs=11,
              lw=2.0)
    draw_axes(ax, T_desk, AXIS_LEN, "W", INTR, label_dxy=(58, -40), fs=11,
              lw=2.0)

    # a magnified detail of the cube in the upper right corner, over the
    # cabinet, so the outline and the axes read at print size
    ins = ax.inset_axes([0.665, 0.635, 0.325, 0.355])
    ins.imshow(img)
    cx, cy = uv_o
    ins.set_xlim(cx - 72, cx + 72)
    ins.set_ylim(cy + 60, cy - 60)
    ins.add_patch(Polygon(uv, closed=True, fill=False, ec=OUTLINE, lw=2.5))
    draw_axes(ins, T_obj, AXIS_LEN, None, INTR, lw=2.5)
    ins.set_xticks([]); ins.set_yticks([])
    for sp in ins.spines.values():
        sp.set_edgecolor("white"); sp.set_linewidth(1.5)
    ins.text(0.03, 0.05, "detail of the cube", transform=ins.transAxes,
             fontsize=8, color="white", ha="left", va="bottom",
             bbox=dict(boxstyle="round,pad=0.2", fc="black", ec="none",
                       alpha=0.55))

    ax.set_xlim(0, img.shape[1])
    ax.set_ylim(img.shape[0], 0)
    ax.set_axis_off()
    ax.set_title(f"({tag}) {label}, frame {idx}", fontsize=11, loc="left")

fig.savefig(OUT, dpi=200)
print("saved", OUT)

#!/usr/bin/env python3
"""Appendix C figures (V7 rewrite round).

  appC_fig_landmarks.png  the eight upper-body landmarks this system uses,
                          drawn on the pinned worked-example frame (frame
                          270 of the rail recording) at the pixels
                          the extractor sampled.
  appC_fig_vectors.png    the same eight landmarks as metric position
                          vectors from the sensor origin, the form the
                          deprojection of Appendix D produces.

Pixels and positions are read from the frozen raw landmark CSV of the
primary recording, not recomputed, so the figure and the worked example
in the text carry the same numbers.

Output: writing/v7/figures/appC_fig_landmarks.png, appC_fig_vectors.png
Run:    python writing/v7/scripts/make_appC_figs.py
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import cv2

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v7" / "figures"
SRC = FIG / "src" / "r6b_frame00533.png"
CSV = (REPO / "v1" / "mediapipe" / "output"
       / "recording_20260831_065553_landmarks_raw.csv")
META_FX, META_FY = 607.561279296875, 607.0150756835938
META_CX, META_CY = 323.93756103515625, 248.0174102783203
FRAME = 533

NAMES = [("left_shoulder", 11), ("right_shoulder", 12),
         ("left_elbow", 13), ("right_elbow", 14),
         ("left_wrist", 15), ("right_wrist", 16),
         ("left_hip", 23), ("right_hip", 24)]
BONES = [(11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
         (11, 23), (12, 24), (23, 24)]

row = next(r for r in csv.DictReader(open(CSV)) if int(r["frame"]) == FRAME)
pos, px = {}, {}
for name, idx in NAMES:
    p = np.array([float(row[f"{name}_{a}"]) for a in "xyz"])
    pos[idx] = p
    px[idx] = (int(round(META_FX * p[0] / p[2] + META_CX)),
               int(round(META_FY * p[1] / p[2] + META_CY)))
    print("L%-2d %-15s xyz=(%+.4f, %+.4f, %+.4f) pixel=%s vis=%.4f"
          % (idx, name, p[0], p[1], p[2], px[idx], float(row[f"{name}_vis"])))

# ---- Figure C.1: landmarks on the frame -----------------------------------
img = cv2.imread(str(SRC))
assert img is not None, SRC
ov = img.copy()
for a, b in BONES:
    cv2.line(ov, px[a], px[b], (255, 255, 255), 2, cv2.LINE_AA)
for name, idx in NAMES:
    u, v = px[idx]
    cv2.circle(ov, (u, v), 7, (60, 220, 60), -1, cv2.LINE_AA)
    cv2.circle(ov, (u, v), 7, (0, 90, 0), 2, cv2.LINE_AA)
    label = "L%d" % idx
    cv2.putText(ov, label, (u + 10, v - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.58,
                (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(ov, label, (u + 10, v - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.58,
                (80, 255, 80), 1, cv2.LINE_AA)
out1 = FIG / "appC_fig_landmarks.png"
cv2.imwrite(str(out1), ov)
print("saved", out1)

# ---- Figure C.2: the same landmarks as vectors from the sensor ------------
fig = plt.figure(figsize=(7.4, 5.6))
ax = fig.add_subplot(111, projection="3d")
for a, b in BONES:
    pa, pb = pos[a], pos[b]
    ax.plot([pa[0], pb[0]], [pa[2], pb[2]], [-pa[1], -pb[1]],
            color="0.55", lw=1.6)
for name, idx in NAMES:
    p = pos[idx]
    ax.plot([0, p[0]], [0, p[2]], [0, -p[1]], color="#5b8fd6", lw=0.8,
            alpha=0.75)
    ax.scatter([p[0]], [p[2]], [-p[1]], color="#2a9d8f", s=34,
               edgecolors="black", linewidths=0.5, depthshade=False)
    ax.text(p[0], p[2], -p[1] + 0.045, "L%d" % idx, fontsize=8.5)
ax.scatter([0], [0], [0], color="black", s=45, marker="s", depthshade=False)
# Label positions are set per axis rather than by one scale factor: the
# generic placement put "sensor origin" on top of the z arrow's label and
# the y label on top of the x axis title.
ax.text(-0.13, 0, 0.10, "sensor origin", fontsize=8.5)
for vec, lab, col, at in (
        ((0.22, 0, 0), "x right", "#c1121f", (0.25, 0, 0.03)),
        ((0, 0.40, 0), "z forward", "#0077b6", (-0.02, 0.44, 0.06)),
        ((0, 0, -0.16), "y down", "#2a9d8f", (0.115, 0, -0.135))):
    ax.quiver(0, 0, 0, vec[0], vec[1], vec[2], color=col, lw=1.6,
              arrow_length_ratio=0.22)
    ax.text(at[0], at[1], at[2], lab, fontsize=8, color=col)
ax.set_xlabel("x (m)", fontsize=9)
ax.set_ylabel("z, depth (m)", fontsize=9)
ax.set_zlabel("height above the optical axis (m)", fontsize=9)
ax.tick_params(labelsize=7)
ax.view_init(elev=16, azim=-72)
ax.set_box_aspect((1.0, 1.5, 1.0))
plt.tight_layout()
out2 = FIG / "appC_fig_vectors.png"
plt.savefig(out2, dpi=190, bbox_inches="tight")
print("saved", out2)

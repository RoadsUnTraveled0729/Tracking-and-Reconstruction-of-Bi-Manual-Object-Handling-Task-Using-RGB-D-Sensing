#!/usr/bin/env python3
"""Chapter 2 ArUco detection figure (V7 rewrite round).

Runs the ArUco detector (DICT_5X5_50, the project dictionary) on the
pinned R6B scene frame and shows the detections: the full frame with the
three detected markers outlined, and one zoom panel per marker with the
four detected corners drawn in detection order.

Output: writing/v7/figures/ch2_fig_aruco.png
Run:    python writing/v7/scripts/make_ch2_aruco_fig.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import cv2
from matplotlib.patches import Polygon

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "writing" / "v7" / "figures" / "src" / "r6b_frame00533.png"

img = cv2.cvtColor(cv2.imread(str(SRC)), cv2.COLOR_BGR2RGB)

aruco = cv2.aruco
params = aruco.DetectorParameters()
params.cornerRefinementMethod = aruco.CORNER_REFINE_APRILTAG
detector = aruco.ArucoDetector(
    aruco.getPredefinedDictionary(aruco.DICT_5X5_50), params)
corners, ids, _ = detector.detectMarkers(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY))
found = {int(i): c.reshape(4, 2) for i, c in zip(ids.flatten(), corners)}
print("detected markers:", sorted(found))

roles = {0: "wall (id 0)", 2: "desk (id 2)", 1: "object (id 1)"}
corner_colors = ["#e63946", "#f4a261", "#2a9d8f", "#457b9d"]

fig = plt.figure(figsize=(8.4, 7.4))
gs = fig.add_gridspec(2, 3, height_ratios=[2.1, 1.0], hspace=0.08, wspace=0.06)

ax = fig.add_subplot(gs[0, :])
ax.imshow(img)
ax.axis("off")
ax.set_title("(a) full frame: the three detected markers", fontsize=10)
for mid, q in found.items():
    ax.add_patch(Polygon(q, closed=True, fill=False, ec="#ffd60a", lw=2.0))
    cen = q.mean(axis=0)
    ax.text(cen[0], cen[1] - 30, roles[mid], fontsize=9, color="white",
            ha="center",
            bbox=dict(boxstyle="round,pad=0.25", fc="black", alpha=0.72))

for k, mid in enumerate((0, 2, 1)):
    q = found[mid]
    cen = q.mean(axis=0)
    half = max(q[:, 0].ptp(), q[:, 1].ptp()) * 0.9 + 12
    x0, x1 = int(cen[0] - half), int(cen[0] + half)
    y0, y1 = int(cen[1] - half), int(cen[1] + half)
    axz = fig.add_subplot(gs[1, k])
    axz.imshow(img[max(y0, 0):y1, max(x0, 0):x1])
    axz.axis("off")
    axz.set_title(f"({chr(98 + k)}) {roles[mid]}", fontsize=10)
    for j, (u, v) in enumerate(q):
        axz.plot(u - x0, v - y0, "o", ms=7, mec="black",
                 mfc=corner_colors[j])
        axz.annotate(str(j), (u - x0 + 5, v - y0 - 5), fontsize=9,
                     color="white",
                     bbox=dict(boxstyle="round,pad=0.15", fc="black",
                               alpha=0.72))

out = REPO / "writing" / "v7" / "figures" / "ch2_fig_aruco.png"
plt.savefig(out, dpi=200, bbox_inches="tight")
print("saved", out)

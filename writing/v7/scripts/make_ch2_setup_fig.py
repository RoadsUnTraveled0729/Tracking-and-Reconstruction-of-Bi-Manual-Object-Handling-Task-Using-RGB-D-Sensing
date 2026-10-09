#!/usr/bin/env python3
"""Chapter 2 recording-setup figure (R6B rail round).

Annotates the pinned R6B scene frame (frame 533 of the rail recording)
with the elements of the physical setup: the three ArUco markers
(outlines from a direct detection on this frame, so no marker size or
pose model is involved), the rail, the working area drawn on grid
paper, the person, and the desk.

Output: writing/v7/figures/ch2_fig_setup.png
Run:    python writing/v7/scripts/make_ch2_setup_fig.py
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
h, w = img.shape[:2]

aruco = cv2.aruco
detector = aruco.ArucoDetector(
    aruco.getPredefinedDictionary(aruco.DICT_5X5_50),
    aruco.DetectorParameters())
corners, ids, _ = detector.detectMarkers(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY))
found = {int(i): c.reshape(4, 2) for i, c in zip(ids.flatten(), corners)}
print("detected markers:", sorted(found))

labels = {0: "wall marker (id 0)", 2: "desk marker (id 2)\nworld anchor",
          1: "object marker (id 1)\non the carried cube"}
off = {0: (46, -40), 2: (110, -30), 1: (-60, -110)}

fig, ax = plt.subplots(figsize=(8.4, 6.3))
ax.imshow(img)
ax.axis("off")

for mid, q in sorted(found.items()):
    ax.add_patch(Polygon(q, closed=True, fill=False, ec="#ffd60a", lw=2.2))
    cen = q.mean(axis=0)
    dx, dy = off.get(mid, (60, 60))
    ax.annotate(labels.get(mid, f"marker id {mid}"), xy=cen,
                xytext=(cen[0] + dx, cen[1] + dy),
                fontsize=9, color="white", ha="left", va="center",
                bbox=dict(boxstyle="round,pad=0.3", fc="black", alpha=0.72),
                arrowprops=dict(arrowstyle="->", color="#ffd60a", lw=1.6))

callouts = [
    ("person performing\nthe rail task", (400, 135), (468, 52)),
    ("rail resting\non the desk", (420, 352), (500, 300)),
    ("working area drawn\non grid paper", (280, 408), (30, 430)),
    ("desk surface", (600, 445), (486, 468)),
]
for text, xy, xytext in callouts:
    ax.annotate(text, xy=xy, xytext=xytext,
                fontsize=9, color="white", ha="left", va="center",
                bbox=dict(boxstyle="round,pad=0.3", fc="black", alpha=0.72),
                arrowprops=dict(arrowstyle="->", color="white", lw=1.4))

ax.text(8, 16, "view from the RGB-D camera at the desk edge",
        fontsize=8.5, color="white",
        bbox=dict(boxstyle="round,pad=0.3", fc="black", alpha=0.72))

plt.tight_layout()
out = REPO / "writing" / "v7" / "figures" / "ch2_fig_setup.png"
plt.savefig(out, dpi=200)
print("saved", out)

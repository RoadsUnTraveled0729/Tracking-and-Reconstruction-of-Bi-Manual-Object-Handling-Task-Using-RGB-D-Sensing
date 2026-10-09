#!/usr/bin/env python3
"""Extract the pinned V7 figure frame from the R6B rail recording.

Frame selection:
  - frame 533: mid-slide scene frame (cube on the rail in the right
    hand). Top of the representative-frame shortlist of the R6B
    inspection report (min landmark visibility 0.578, max marker
    reprojection 0.215 px); all three markers detected.

The rail composite of make_ch2_rail_figs.py keeps its own frame 750
panel (figures/src/r6b_frame00750.jpg); this script pins the frame the
setup, MediaPipe, and ArUco figures share.

Output: writing/v7/figures/src/r6b_frame00533.png
Run:    python writing/v7/scripts/extract_r6b_frames.py
"""
import sys
from pathlib import Path

import cv2
import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "v1" / "mediapipe"))
sys.path.insert(0, str(REPO / "eval" / "common"))

from extract_landmarks_to_csv import open_bag  # noqa: E402
import pyrealsense2 as rs                      # noqa: E402

WANT = {533}
BAG = REPO / "Video" / "recording_20260831_065553.bag"
OUT = REPO / "writing" / "v7" / "figures" / "src"
OUT.mkdir(parents=True, exist_ok=True)

pipe, align, intrinsics, color_format = open_bag(BAG)
idx = 0
while idx <= max(WANT):
    try:
        frames = pipe.wait_for_frames(timeout_ms=5000)
    except RuntimeError:
        break
    frames = align.process(frames)
    color = frames.get_color_frame()
    if not color:
        continue
    if idx in WANT:
        img = np.asanyarray(color.get_data())
        if color_format == rs.format.rgb8:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        path = OUT / f"r6b_frame{idx:05d}.png"
        cv2.imwrite(str(path), img)
        print("saved", path)
    idx += 1
pipe.stop()
print("frames seen:", idx)

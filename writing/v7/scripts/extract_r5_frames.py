#!/usr/bin/env python3
"""Extract the two pinned V7 figure frames from the R5 primary recording.

Frame selection (writing/v7/DECISIONS.md D17):
  - frame 1236: mid-task scene frame (person reaching for the cube; the
    same frame as the frozen R5 marker-overlay report figure). Both arm
    failure flags are clear at this frame; the torso detector fires, which
    is acceptable for scene and landmark figures but not for numerics.
  - frame  270: worked-example frame. Every failure detector is clear,
    all eight landmark visibilities exceed 0.85, and no filter flag is
    set, verified against the frozen failure mask and the filtered
    landmark CSV.
  - frame  269: the frame Figure E.2 draws. It is the nearest frame to
    the worked-example frame on which the marker extractor recorded the
    near-degenerate ambiguity flag (wall marker, lobes 38.6 deg apart);
    on frame 270 itself the same pair opens to 40.4 deg and the flag is
    clear.

Output: writing/v7/figures/src/r5_frame00269.png, r5_frame00270.png,
        r5_frame01236.png
Run:    python writing/v7/scripts/extract_r5_frames.py
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

WANT = {269, 270, 1236}
BAG = REPO / "Video" / "recording_20260825_222315.bag"
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
        path = OUT / f"r5_frame{idx:05d}.png"
        cv2.imwrite(str(path), img)
        print("saved", path)
    idx += 1
pipe.stop()
print("frames seen:", idx)

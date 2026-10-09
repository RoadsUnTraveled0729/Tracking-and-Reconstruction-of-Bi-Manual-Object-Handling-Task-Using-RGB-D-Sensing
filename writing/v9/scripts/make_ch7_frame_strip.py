#!/usr/bin/env python3
"""Chapter 7 colour-frame strip of the rail task (supervisor C33).

Four colour frames of the recording at the moments the protocol schematic
names: the cube grasped on the desk, the lift onto the rail, the slide,
and the far end of the rail. The frames are read from the bag file with
the same reader as writing/v7/scripts/extract_r6b_frames.py.

Two steps:
  --extract   grab the candidate frames listed in CANDIDATES from the bag
              into figures/src/r6b_frame{idx:05d}.png (run once; slow)
  (default)   compose the four frames named in ch7_frames_strip.json into
              one strip, figures/ch7_fig_frames_strip.png

The chosen frames were picked by looking at the candidates (2026-09-07):
see the json for the frame numbers and the moment each shows.

Output: writing/v9/figures/ch7_fig_frames_strip.png
Run:    python writing/v9/scripts/make_ch7_frame_strip.py [--extract]
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FIGD = REPO / "writing" / "v9" / "figures"
SRC = FIGD / "src"
OUT = FIGD / "ch7_fig_frames_strip.png"
CHOICE = FIGD / "ch7_frames_strip.json"
BAG = REPO / "Video" / "recording_20260831_065553.bag"

CANDIDATES = {40, 60, 95, 110, 114, 130, 250, 350, 505, 515, 525, 560,
              700, 750, 800, 850, 880, 895, 898, 899}


def extract():
    import cv2
    import numpy as np
    sys.path.insert(0, str(REPO / "v1" / "mediapipe"))
    sys.path.insert(0, str(REPO / "eval" / "common"))
    from extract_landmarks_to_csv import open_bag  # noqa: E402
    import pyrealsense2 as rs  # noqa: E402
    SRC.mkdir(parents=True, exist_ok=True)
    pipe, align, intrinsics, color_format = open_bag(BAG)
    idx = 0
    while idx <= max(CANDIDATES):
        try:
            frames = pipe.wait_for_frames(timeout_ms=5000)
        except RuntimeError:
            break
        frames = align.process(frames)
        color = frames.get_color_frame()
        if not color:
            continue
        if idx in CANDIDATES:
            img = np.asanyarray(color.get_data())
            if color_format == rs.format.rgb8:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            path = SRC / f"r6b_frame{idx:05d}.png"
            cv2.imwrite(str(path), img)
            print("saved", path)
        idx += 1
    pipe.stop()
    print("frames seen:", idx)


def compose():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from PIL import Image
    spec = json.loads(CHOICE.read_text())
    panels = spec["panels"]
    fig, axes = plt.subplots(1, len(panels), figsize=(3.2 * len(panels), 2.9))
    for ax, p in zip(axes, panels):
        img = Image.open(SRC / f"r6b_frame{p['frame']:05d}.png")
        if "crop" in spec:
            img = img.crop(tuple(spec["crop"]))
        ax.imshow(img)
        ax.set_xticks([])
        ax.set_yticks([])
        for side in ax.spines.values():
            side.set_edgecolor("0.4")
            side.set_linewidth(0.9)
        ax.set_title(f"({p['tag']}) {p['label']}, frame {p['frame']}",
                     fontsize=9.5, loc="left", pad=4)
    plt.tight_layout(w_pad=0.6)
    plt.savefig(OUT, dpi=200, bbox_inches="tight")
    print("saved", OUT)


if __name__ == "__main__":
    if "--extract" in sys.argv:
        extract()
    else:
        compose()

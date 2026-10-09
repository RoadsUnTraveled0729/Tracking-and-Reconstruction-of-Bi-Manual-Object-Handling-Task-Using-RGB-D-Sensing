#!/usr/bin/env python3
"""Chapter 7 colour-frame strip of the two-hand rail take (supervisor
round 6, C50; E-034): the right-hand slide, both hands at the cube, the
left-hand slide, and the far end after the release.

Same two steps and layout as make_ch7_frame_strip.py, on the take
recording_20260909_000024 (alias r7):
  --extract   grab the candidate frames listed in CANDIDATES from the bag
              into figures/src/r7_frame{idx:05d}.png (run once; slow)
  (default)   compose the four frames named in ch7_handover_frames.json
              into figures/ch7_fig_handover_frames.png

The frame numbers of the moments come from the hand-over analysis
(eval/reports/r7_handover.json: left hand at the cube from frame 864,
right hand until 1022) and from looking at the candidates.

Output: writing/v8/condensed/figures/ch7_fig_handover_frames.png
Run:    python writing/v8/condensed/scripts/make_ch7_handover_frames.py [--extract]
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
FIGD = REPO / "writing" / "v8" / "condensed" / "figures"
SRC = FIGD / "src"
OUT = FIGD / "ch7_fig_handover_frames.png"
CHOICE = FIGD / "ch7_handover_frames.json"
BAG = REPO / "Video" / "recording_20260909_000024.bag"

CANDIDATES = {300, 450, 600, 650, 700, 750, 800, 850, 864, 880, 900, 920,
              950, 980, 1000, 1022, 1042, 1060, 1100, 1200, 1400, 1497}


def extract():
    import cv2
    import numpy as np
    sys.path.insert(0, str(REPO / "v1" / "mediapipe"))
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
            path = SRC / f"r7_frame{idx:05d}.png"
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
        img = Image.open(SRC / f"r7_frame{p['frame']:05d}.png")
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

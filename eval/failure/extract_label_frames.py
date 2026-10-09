#!/usr/bin/env python3
"""Extract the frames to label for the natural-failure evaluation.

User direction 2026-08-26: the synthetic-masking evaluation grades the
recovery on stand-in frames; the frames that MATTER are the natural
failure windows, so the wrist is labeled manually there and the depth
map supplies the third coordinate.

This script selects the label set - failure-window frames (from the
frozen failure mask) that fall INSIDE a grip episode (recovery only
applies to a holding hand), sampled every STEP frames - and saves for
each one the color image (png) and the aligned depth (npy, uint16),
plus meta.json with the color intrinsics so the labels can be
deprojected later.

Output: eval/output/label_frames_<alias>/  (alias r5 or r6b, from --stem)
Run:    python eval/failure/extract_label_frames.py [--stem STEM]
Then:   python eval/failure/label_wrists.py --dir <that folder>

2026-09-06: --stem added so the rail recording (R6B, the thesis
recording) can be extracted as well; the failure mask and grip episodes
are read from eval/output/recovery_<alias>/. The extracted sets are
copied to eval/labels/frames_<alias>/ (tracked in git) so a machine
without the bag files can label them.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "v1" / "mediapipe"))
sys.path.insert(0, str(HERE.parents[0] / "common"))

import paths                                    # noqa: E402
from extract_landmarks_to_csv import open_bag   # noqa: E402
import pyrealsense2 as rs                       # noqa: E402

import argparse
_ap = argparse.ArgumentParser()
_ap.add_argument("--stem", default=paths.R5_STEM)
STEM = _ap.parse_args().stem
ALIAS = paths.ALIAS[STEM]
OUT = paths.EVAL_OUT / f"label_frames_{ALIAS}"
RECOV = paths.EVAL_OUT / f"recovery_{ALIAS}"
STEP = 5           # label every 5th frame of a window
MIN_RUN = 5        # ignore failure blips shorter than this


def failure_runs(mask):
    m = np.asarray(mask, bool)
    d = np.diff(m.astype(int))
    starts = list(np.where(d == 1)[0] + 1)
    stops = list(np.where(d == -1)[0])
    if m[0]:
        starts.insert(0, 0)
    if m[-1]:
        stops.append(len(m) - 1)
    return [(a, b) for a, b in zip(starts, stops) if b - a + 1 >= MIN_RUN]


def main():
    fm = pd.read_csv(RECOV / "failure_mask.csv")
    eps = json.loads((RECOV / "grip_episodes.json").read_text())

    need = {}                                   # frame -> set of sides
    for side, col in (("left", "fail_arm_L"), ("right", "fail_arm_R")):
        holding = np.zeros(len(fm), bool)
        for e in eps["episodes"][side]:
            holding[e["start"]:e["stop"] + 1] = True
        for a, b in failure_runs(fm[col]):
            for f in range(a, b + 1, STEP):
                if holding[f]:
                    need.setdefault(f, set()).add(side)
    frames = sorted(need)
    print(f"[info] {len(frames)} frames to extract "
          f"({sum(len(s) for s in need.values())} wrist labels wanted)")

    OUT.mkdir(parents=True, exist_ok=True)
    pipeline, align, intr, color_format = open_bag(paths.bag(STEM))
    depth_scale = (pipeline.get_active_profile().get_device()
                   .first_depth_sensor().get_depth_scale())
    saved = 0
    idx = -1
    want = set(frames)
    try:
        while want:
            try:
                fs = pipeline.wait_for_frames(timeout_ms=5000)
            except RuntimeError:
                break
            idx += 1
            if idx not in want:
                continue
            fs = align.process(fs)
            c, d = fs.get_color_frame(), fs.get_depth_frame()
            if not c or not d:
                print(f"[warn] frame {idx}: missing stream, skipped")
                want.discard(idx)
                continue
            img = np.asanyarray(c.get_data())
            if color_format == rs.format.rgb8:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(OUT / f"f{idx:05d}.png"), img)
            np.save(OUT / f"f{idx:05d}_depth.npy",
                    np.asanyarray(d.get_data()))
            want.discard(idx)
            saved += 1
    finally:
        pipeline.stop()

    meta = {
        "stem": STEM, "step": STEP, "depth_scale": depth_scale,
        "intrinsics": {
            "width": intr.width, "height": intr.height,
            "ppx": intr.ppx, "ppy": intr.ppy,
            "fx": intr.fx, "fy": intr.fy,
            "model": str(intr.model).split(".")[-1],
            "coeffs": list(intr.coeffs),
        },
        "frames": {str(f): sorted(need[f]) for f in frames},
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1))
    print(f"[+] {saved} frames -> {OUT} (+ meta.json)")
    if want:
        print(f"[warn] {len(want)} wanted frames never appeared: "
              f"{sorted(want)[:10]}")


if __name__ == "__main__":
    main()

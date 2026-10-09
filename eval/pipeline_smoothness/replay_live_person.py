#!/usr/bin/env python3
"""Deterministic offline replay of the v1 live person path (Pipeline A).

Runs the frozen v1 live-path objects, imported unchanged from
v1/realtime/person/realtime_person.py and the modules it imports, on every
frame of a bag, and logs the intermediate values the live loop does not
dump:

  bag frame -> depth->color align -> MediaPipe (VIDEO mode) ->
  visibility gate + 5x5 median depth (deproject_landmarks)   [stage raw]
  -> CausalLandmarkFilter: trailing Hampel despike + One-Euro  [stage live_filtered]
  -> unity_from_sensor -> ChainFallbackSolver -> 13 angles    [what PSR1 carries]

Differences from realtime_person.main(), all deliberate:
  - playback is set_real_time(False), so every recorded frame is processed
    once and the frame index equals the bag frame index used by the defence
    films (the paced run can drop frames under load; see README);
  - nothing is written to shared memory; the 13 angles and mask that would
    be written are logged instead;
  - the per-landmark raw and filtered xyz are logged.
The loop body (align, rel_s, mp_ts, detect_for_video, deproject, filter,
solve) is the same sequence of calls as realtime_person.main().

Usage:
  /home/luo/anaconda3/bin/python replay_live_person.py --bag BAG --out CSV
      [--delegate cpu|gpu] [--paced]
"""
import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True  # never write into the frozen v1 tree

import cv2
import numpy as np
import pyrealsense2 as rs
import mediapipe as mp

REPO = Path(__file__).resolve().parents[2]
V1 = REPO / "v1"
LIVE = V1 / "realtime/person/realtime_person.py"

spec = importlib.util.spec_from_file_location("realtime_person", LIVE)
rp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rp)   # module top level only; main() is not run

NAMES = [rp.LANDMARK_NAMES[i] for i in rp.TORSO_AND_ARMS]


def open_bag_every_frame(bag_path, paced=False):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(str(bag_path), repeat_playback=False)
    profile = pipeline.start(config)
    profile.get_device().as_playback().set_real_time(paced)
    intrinsics = (profile.get_stream(rs.stream.color)
                  .as_video_stream_profile().get_intrinsics())
    color_format = profile.get_stream(rs.stream.color).format()
    align = rs.align(rs.stream.color)
    return pipeline, align, intrinsics, color_format


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bag", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="heavy")
    ap.add_argument("--delegate", default="cpu")
    ap.add_argument("--min-vis", type=float, default=0.5)      # realtime_person default
    ap.add_argument("--depth-window", type=int, default=5)     # realtime_person default
    ap.add_argument("--paced", action="store_true",
                    help="set_real_time(True) as in realtime_person.open_bag_realtime; "
                         "frames may then be dropped and wall_s shows delivery timing")
    args = ap.parse_args()

    model_path = rp.resolve_model(args.model, V1 / "mediapipe/models")
    landmarker, delegate = rp.make_landmarker(model_path, args.delegate)
    pipeline, align, intrinsics, color_format = open_bag_every_frame(args.bag, args.paced)
    filt = rp.CausalLandmarkFilter()       # live defaults, unchanged
    solver = rp.ChainFallbackSolver()

    cols = ["frame", "time_s", "wall_s", "has_pose"]
    for n in NAMES:
        cols += [f"{n}_{s}" for s in ("rx", "ry", "rz", "vis", "src",
                                      "fx", "fy", "fz")]
    cols += [f"a{i}" for i in range(13)] + ["mask"]
    rows = []
    frame_count, first_ts, last_mp_ts = 0, None, -1
    t_start = time.monotonic()
    try:
        while True:
            try:
                frames = pipeline.wait_for_frames(timeout_ms=5000)
            except RuntimeError:
                break
            aligned = align.process(frames)
            color_frame = aligned.get_color_frame()
            depth_frame = aligned.get_depth_frame()
            if not color_frame or not depth_frame:
                continue
            ts_ms = frames.get_timestamp()
            if first_ts is None:
                first_ts = ts_ms
            rel_s = (ts_ms - first_ts) / 1000.0
            color = np.asanyarray(color_frame.get_data())
            rgb = (color if color_format == rs.format.rgb8
                   else cv2.cvtColor(color, cv2.COLOR_BGR2RGB))
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,
                                data=np.ascontiguousarray(rgb))
            mp_ts = max(int(rel_s * 1000), last_mp_ts + 1)
            last_mp_ts = mp_ts
            result = landmarker.detect_for_video(mp_image, mp_ts)

            row = [frame_count, rel_s, time.monotonic() - t_start, 0]
            points = {}
            per = {n: [np.nan] * 8 for n in NAMES}
            if result and result.pose_landmarks:
                row[3] = 1
                lms = rp.deproject_landmarks(result.pose_landmarks[0],
                                             depth_frame, intrinsics,
                                             rp.TORSO_AND_ARMS, args.min_vis,
                                             args.depth_window)
                for idx in rp.TORSO_AND_ARMS:
                    name = rp.LANDMARK_NAMES[idx]
                    xyz = lms[idx]["xyz"]
                    fx = filt(name, np.asarray(xyz) if xyz is not None else None)
                    raw3 = list(xyz) if xyz is not None else [np.nan] * 3
                    f3 = list(fx) if fx is not None else [np.nan] * 3
                    per[name] = raw3 + [lms[idx]["visibility"], lms[idx]["src"]] + f3
                    if fx is not None:
                        points[name] = rp.unity_from_sensor(fx)
            angles, mask = solver.solve(points)
            for n in NAMES:
                row += per[n]
            row += list(angles) + [mask]
            rows.append(row)
            frame_count += 1
    finally:
        pipeline.stop()
    wall = time.monotonic() - t_start

    import pandas as pd
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=cols).to_csv(out, index=False, float_format="%.9g")
    meta = {"bag": str(args.bag), "delegate_requested": args.delegate,
            "delegate_used": delegate, "model": str(model_path),
            "frames": frame_count, "wall_s": round(wall, 1),
            "min_vis": args.min_vis, "depth_window": args.depth_window,
            "filter": {"window": filt.window, "k": filt.k,
                       "abs_floor_m": filt.abs_floor,
                       "max_rejects": filt.MAX_REJECTS,
                       "one_euro": "freq 30, min_cutoff 1.0, beta 1.0 (CausalLandmarkFilter defaults)"},
            "live_module": str(LIVE.relative_to(REPO)),
            "playback": ("set_real_time(True): recorded pacing, as the live loop"
                         if args.paced else
                         "set_real_time(False): every recorded frame, once")}
    out.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"[done] {frame_count} frames, delegate {delegate}, {wall:.1f} s -> {out}")


if __name__ == "__main__":
    main()

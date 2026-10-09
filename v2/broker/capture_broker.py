#!/usr/bin/env python3
# Filename: v2/broker/capture_broker.py
"""v2 capture broker: the ONLY process that opens the RealSense device
(or the bag standing in for it). Publishes aligned color+depth frames to
the PSF1 shared-memory ring for Pipeline A, Pipeline B, and the live
calibrator. Two processes cannot both open one physical camera -- this
broker is what makes a single live sensor feed both pipelines.

  --source bag   v1's open_bag_realtime() semantics: the pinned recording
                 played at recorded pacing (the live-camera stand-in and
                 the automated test path).
  --source live  config.enable_stream(...) on the physical D435 at the
                 bag's exact profile (640x480 bgr8 color + 640x480 z16
                 depth, 30 fps) so every downstream branch behaves
                 identically. --record tees the session to a bag so any
                 live run is re-analyzable offline.

Depth->color alignment happens HERE, once, instead of per-pipeline
(align leaves color untouched, so Pipeline B is unaffected).

Consumers derive the shared session clock from the ring header:
time_s = (hw_ts_ms - t0_hw_ms) / 1000 -- hardware timestamps end to end,
one clock for both pipelines (thesis 8.3.1).

Usage:
  python capture_broker.py --source bag [--bag ...] [--max-frames N]
  python capture_broker.py --source live [--record out.bag]
      [--width 640 --height 480 --fps 30]
  common: [--ring /dev/shm/rt_frames] [--nslots 8] [--sync-file PATH]
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pyrealsense2 as rs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                 # repo root (v2/broker/ -> repo)
sys.path.insert(0, str(ROOT / "v2/common"))

from shm_ring import DEFAULT_NSLOTS, DEFAULT_PATH, FrameRingWriter


def open_bag(bag_path):
    """v1's open_bag_realtime(): recorded pacing, no repeat."""
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(str(bag_path), repeat_playback=False)
    profile = pipeline.start(config)
    profile.get_device().as_playback().set_real_time(True)
    return pipeline, profile


def open_live(width, height, fps, record_path):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
    config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
    if record_path:
        config.enable_record_to_file(str(record_path))
    profile = pipeline.start(config)
    return pipeline, profile


def assert_profile(profile, want_w, want_h, want_fps):
    """Fail loudly if the negotiated profile is not what was asked for
    (the classic silent failure is a USB2 port downgrading the modes)."""
    ok = True
    for stream in (rs.stream.color, rs.stream.depth):
        sp = profile.get_stream(stream).as_video_stream_profile()
        got = (sp.width(), sp.height(), sp.fps())
        print(f"[info] negotiated {stream}: {got[0]}x{got[1]} @ {got[2]} fps")
        if got != (want_w, want_h, want_fps):
            print(f"[ERROR] wanted {want_w}x{want_h} @ {want_fps} fps "
                  f"for {stream} -- check the camera is on a USB 3.x port")
            ok = False
    if not ok:
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=("bag", "live"), required=True)
    ap.add_argument("--bag", default=str(ROOT / "Video/recording_20260224_083945.bag"))
    ap.add_argument("--record", default=None,
                    help="live only: tee the session to this bag file")
    ap.add_argument("--width", type=int, default=640)
    ap.add_argument("--height", type=int, default=480)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--ring", default=DEFAULT_PATH)
    ap.add_argument("--nslots", type=int, default=DEFAULT_NSLOTS)
    ap.add_argument("--max-frames", type=int, default=None)
    ap.add_argument("--sync-file", default=None,
                    help="start barrier: touch <sync>.ready.broker after "
                         "init, start the device only once <sync> exists")
    args = ap.parse_args()

    if args.record and args.source != "live":
        sys.exit("[ERROR] --record only makes sense with --source live")

    if args.sync_file:
        Path(args.sync_file + ".ready.broker").touch()
        while not Path(args.sync_file).exists():
            time.sleep(0.005)

    playback = None
    if args.source == "bag":
        pipeline, profile = open_bag(args.bag)
        playback = profile.get_device().as_playback()
        print(f"[info] source: bag {args.bag} (recorded pacing)")
    else:
        pipeline, profile = open_live(args.width, args.height, args.fps,
                                      args.record)
        print("[info] source: live device"
              + (f", recording to {args.record}" if args.record else ""))
        assert_profile(profile, args.width, args.height, args.fps)

    color_sp = profile.get_stream(rs.stream.color).as_video_stream_profile()
    intrinsics = color_sp.get_intrinsics()
    color_format = profile.get_stream(rs.stream.color).format()
    depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()
    align = rs.align(rs.stream.color)

    writer = FrameRingWriter(args.ring, color_sp.width(), color_sp.height(),
                             int(color_format), depth_scale, intrinsics,
                             nslots=args.nslots)
    print(f"[info] ring {args.ring}: {args.nslots} slots x "
          f"{writer.slot_size} B, color format {color_format}, "
          f"depth scale {depth_scale:.6f} m/unit")

    publish_ms = []
    hw_deltas = []
    last_hw = None
    domain_printed = False
    t_start = time.monotonic()
    n = 0
    misses = 0
    try:
        while args.max_frames is None or n < args.max_frames:
            try:
                frames = pipeline.wait_for_frames(timeout_ms=1000)
                misses = 0
            except RuntimeError:
                # short timeout so end-of-source is detected promptly:
                # a stopped playback ends the run at once, a live device
                # gets a few retries before it is declared gone
                if playback is not None and \
                        playback.current_status() == rs.playback_status.stopped:
                    break
                misses += 1
                if misses >= 5:
                    print("[ERROR] no frames for 5 s -- source gone")
                    break
                continue
            t0 = time.perf_counter()
            aligned = align.process(frames)
            color_frame = aligned.get_color_frame()
            depth_frame = aligned.get_depth_frame()
            if not color_frame or not depth_frame:
                continue
            if not domain_printed:
                print(f"[info] timestamp domain: "
                      f"{color_frame.get_frame_timestamp_domain()}")
                domain_printed = True
            hw_ts = frames.get_timestamp()
            color = np.asanyarray(color_frame.get_data())
            depth = np.asanyarray(depth_frame.get_data())
            writer.write(hw_ts, time.monotonic(), color, depth)
            publish_ms.append((time.perf_counter() - t0) * 1e3)
            if last_hw is not None:
                hw_deltas.append(hw_ts - last_hw)
            last_hw = hw_ts
            n += 1
    finally:
        writer.close(eof=True)
        pipeline.stop()

    wall = time.monotonic() - t_start
    print(f"[done] published {n} frames in {wall:.1f} s "
          f"({n / wall:.1f} fps sustained)")
    if publish_ms:
        a = np.asarray(publish_ms)
        print(f"[stage] align+publish ms: p50 {np.percentile(a, 50):.2f}  "
              f"p95 {np.percentile(a, 95):.2f}  "
              f"p99 {np.percentile(a, 99):.2f}  max {a.max():.2f}")
    if hw_deltas:
        d = np.asarray(hw_deltas)
        print(f"[jitter] inter-frame hw delta ms: p50 {np.percentile(d, 50):.2f}  "
              f"p95 {np.percentile(d, 95):.2f}  p99 {np.percentile(d, 99):.2f}  "
              f"max {d.max():.2f}  (nominal {1000.0 / args.fps:.2f})")


if __name__ == "__main__":
    main()

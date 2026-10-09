#!/usr/bin/env python3
# Filename: v2/broker/check_ring_parity.py
"""M1 parity check: every frame of the pinned bag must come through the
broker's ring intact.

  1. Spawns capture_broker --source bag and consumes EVERY publication
     from the ring (sequential fetch, not latest-wins): counts frames,
     verifies frame_idx is gapless, hw timestamps strictly increasing,
     and records sha256(color)+sha256(depth) at probe frames.
  2. Re-reads the same bag directly (offline pacing, same align) and
     compares frame count and probe checksums.

Exit 0 with PASS lines on success, exit 1 with FAIL lines otherwise.

Usage: python check_ring_parity.py [--bag ...] [--probe 0 100 500 898]
"""
import argparse
import hashlib
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pyrealsense2 as rs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "v2/common"))

from shm_ring import FrameRingReader

RING = "/dev/shm/rt_frames_parity"
SYNC = "/dev/shm/rt_go_parity"


def digest(sample):
    return (hashlib.sha256(sample.color.tobytes()).hexdigest(),
            hashlib.sha256(sample.depth.tobytes()).hexdigest())


def consume_ring(probe):
    reader = FrameRingReader(RING, wait_s=30.0)
    hashes = {}
    hw = []
    lapped = 0
    c = 0
    while True:
        try:
            nc, sample = reader.latest(c, timeout_s=10.0)
        except TimeoutError:
            print("[FAIL] ring writer went silent without EOF")
            return None
        if sample is None:
            break                                   # EOF, nothing new
        # consume sequentially: fetch every publication we skipped
        for want in range(c + 1, nc + 1):
            s = sample if want == nc else reader.fetch(want)
            if s is None:
                lapped += 1
                continue
            if s.frame_idx != want - 1:
                print(f"[FAIL] publication {want} carries frame_idx "
                      f"{s.frame_idx}")
                return None
            hw.append(s.hw_ts_ms)
            if s.frame_idx in probe:
                hashes[s.frame_idx] = digest(s)
        c = nc
    return c, hashes, np.asarray(hw), lapped


def read_bag_direct(bag, probe):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(str(bag), repeat_playback=False)
    profile = pipeline.start(config)
    profile.get_device().as_playback().set_real_time(False)
    align = rs.align(rs.stream.color)
    hashes = {}
    n = 0
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
            if n in probe:
                color = np.asanyarray(color_frame.get_data())
                depth = np.asanyarray(depth_frame.get_data())
                hashes[n] = (hashlib.sha256(color.tobytes()).hexdigest(),
                             hashlib.sha256(depth.tobytes()).hexdigest())
            n += 1
    finally:
        pipeline.stop()
    return n, hashes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bag", default=str(ROOT / "Video/recording_20260224_083945.bag"))
    ap.add_argument("--probe", type=int, nargs="+", default=[0, 100, 500, 898])
    args = ap.parse_args()
    probe = set(args.probe)

    for p in (RING, SYNC, SYNC + ".ready.broker"):
        Path(p).unlink(missing_ok=True)
    broker = subprocess.Popen(
        [sys.executable, str(HERE / "capture_broker.py"), "--source", "bag",
         "--bag", args.bag, "--ring", RING, "--sync-file", SYNC])
    try:
        t0 = time.monotonic()
        while not Path(SYNC + ".ready.broker").exists():
            if broker.poll() is not None or time.monotonic() - t0 > 30:
                sys.exit("[FAIL] broker never became ready")
            time.sleep(0.02)
        Path(SYNC).touch()
        result = consume_ring(probe)
        broker.wait(timeout=30)
    finally:
        if broker.poll() is None:
            broker.kill()
    if result is None:
        sys.exit(1)
    n_ring, ring_hashes, hw, lapped = result

    n_direct, direct_hashes = read_bag_direct(args.bag, probe)

    failures = 0

    def check(ok, label):
        nonlocal failures
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
        if not ok:
            failures += 1

    check(lapped == 0, f"no lapped publications (lapped={lapped})")
    check(n_ring == n_direct,
          f"frame count ring {n_ring} == direct {n_direct}")
    check(bool(np.all(np.diff(hw) > 0)),
          "hw timestamps strictly increasing across the ring")
    for idx in sorted(probe):
        if idx >= n_direct:
            continue
        ok = ring_hashes.get(idx) == direct_hashes.get(idx)
        check(ok, f"frame {idx} color+depth sha256 identical")
    span = (hw[-1] - hw[0]) / 1000.0 if len(hw) > 1 else 0.0
    print(f"[info] {n_ring} frames, hw span {span:.1f} s")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

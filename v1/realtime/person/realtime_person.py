#!/usr/bin/env python3
# Filename: realtime/person/realtime_person.py
"""Real-time Pipeline A: bag playback (live-camera emulation) -> landmarks ->
causal filter -> 13-angle solve -> PSR1 shared memory.

The bag plays at the RECORDED pacing (`set_real_time(True)`) so this loop
behaves exactly like a live RealSense; swapping the source for a real camera
is a one-line change in open_bag_realtime(). Everything downstream of the
frame is CAUSAL (this frame + past frames only) — the offline zero-phase
filters are not legal here (thesis/D1_limitations.md §10):

  frame -> depth->color align -> MediaPipe (VIDEO mode, GPU) ->
  visibility gate + 5x5 median depth (extract_landmarks_to_csv helpers) ->
  causal despike (trailing Hampel: reject = missing; the absolute floor is
  35 mm — wider than offline's 20 mm because a TRAILING window has MAD ~ 0
  at motion onset and would flag genuine acceleration) ->
  One-Euro smoothing (per landmark axis; min_cutoff 1 Hz — the offline
  0.05 Hz tuning costs ~9 frames of lag live, measured) ->
  ChainFallbackSolver (kinematics/occlusion.py — already causal) ->
  /dev/shm/rt_person  PSR1 (84 B, seqlock):
      u32 'PSR1' | u32 seq | i32 frame | f32 time_s
      3f pelvis (person space = camera frame, y flipped)
      13f angles (PSA5 order) | u16 live mask | 2x pad

Solver backend: ChainFallbackSolver, the same per-frame scalar solver
(shoulder.py / root_frame.py) as offline Pipeline A — bench_solver.py's
"scalar loop" arm, 99 us/frame at N=1, 0.3% of the 33 ms budget; the
vectorized batch solver would change nothing end-to-end at N=1 (91 us).
--parallel-arms runs the L/R arm solves in two threads (measured SLOWER at
N=1: 151 us — the flag exists to demonstrate that result in situ).

Usage:
  python realtime_person.py [--bag ../../Video/recording_20260224_083945.bag]
      [--profile] [--dump-csv ../output/rt_person_dump.csv]
      [--parallel-arms] [--shm /dev/shm/rt_person] [--max-frames N]
"""
import argparse
import mmap
import struct
import sys
import time
from collections import deque
from pathlib import Path

import numpy as np
import pyrealsense2 as rs
import mediapipe as mp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                 # repo root (realtime/person/ -> repo)
sys.path.insert(0, str(ROOT / "mediapipe"))
sys.path.insert(0, str(ROOT / "kinematics"))

from extract_landmarks_to_csv import (LANDMARK_NAMES, TORSO_AND_ARMS,
                                      deproject_landmarks, make_landmarker,
                                      resolve_model)
from filter_landmarks import OneEuro
from occlusion import ChainFallbackSolver, LANDMARKS          # Pipeline A
from root_frame import unity_from_sensor

MAGIC = 0x31525350  # 'PSR1'
FMT = "<IIif3f13fH2x"
PACKET_SIZE = struct.calcsize(FMT)
assert PACKET_SIZE == 84


def open_bag_realtime(bag_path):
    """Like extract_landmarks_to_csv.open_bag but paced at the recorded
    frame rate — the live-camera stand-in. A real camera replaces this with
    config.enable_stream(...) and no playback object."""
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(str(bag_path), repeat_playback=False)
    profile = pipeline.start(config)
    profile.get_device().as_playback().set_real_time(True)
    intrinsics = (profile.get_stream(rs.stream.color)
                  .as_video_stream_profile().get_intrinsics())
    color_format = profile.get_stream(rs.stream.color).format()
    align = rs.align(rs.stream.color)
    return pipeline, align, intrinsics, color_format


class CausalLandmarkFilter:
    """Per-landmark causal cleanup: trailing-Hampel despike + One-Euro.

    Despike: a sample deviating from the median of the trailing window by
    more than max(abs_floor, k * 1.4826 * MAD) on any axis is REJECTED and
    treated as missing this frame (the solver's fallback holds the joint) —
    the causal analogue of filter_landmarks.py step 1. Accepted samples
    update the window and pass through a per-axis One-Euro filter
    (offline-tuned min_cutoff/beta; ~1 frame of effective lag at 30 fps).
    """

    MAX_REJECTS = 3   # a "spike" persisting this long is real motion —
                      # accept and re-seed the window, else the stale
                      # trailing median rejects everything after it

    def __init__(self, freq=30.0, window=11, k=3.0, abs_floor=0.035,
                 min_cutoff=1.0, beta=1.0):
        self.window = window
        self.k, self.abs_floor = k, abs_floor
        self.hist = {n: deque(maxlen=window) for n in LANDMARKS}
        self.euro = {n: [OneEuro(freq, min_cutoff, beta) for _ in range(3)]
                     for n in LANDMARKS}
        self.rejects = {n: 0 for n in LANDMARKS}

    def __call__(self, name, xyz):
        """xyz (3,) or None -> filtered xyz or None (missing/rejected)."""
        if xyz is None:
            return None
        h = self.hist[name]
        if len(h) >= 5:
            arr = np.asarray(h)
            med = np.median(arr, axis=0)
            mad = np.median(np.abs(arr - med), axis=0)
            thr = np.maximum(self.abs_floor, self.k * 1.4826 * mad)
            if (np.any(np.abs(xyz - med) > thr)
                    and self.rejects[name] < self.MAX_REJECTS):
                self.rejects[name] += 1
                return None                      # spike -> missing
            if self.rejects[name] >= self.MAX_REJECTS:
                h.clear()                        # sustained -> real motion
        self.rejects[name] = 0
        h.append(np.asarray(xyz, float))
        return np.array([f(v) for f, v in zip(self.euro[name], xyz)])


class ShmWriter:
    def __init__(self, path):
        self.path = Path(path)
        self.path.write_bytes(b"\x00" * PACKET_SIZE)
        self._f = open(self.path, "r+b")
        self._mm = mmap.mmap(self._f.fileno(), PACKET_SIZE)
        self._seq = 0

    def write(self, frame, t, pelvis, angles13, mask):
        self._seq += 1                                     # odd: busy
        self._mm[4:8] = struct.pack("<I", self._seq)
        self._mm[:] = struct.pack(FMT, MAGIC, self._seq, frame, t,
                                  *pelvis, *angles13, mask)
        self._seq += 1                                     # even: stable
        self._mm[4:8] = struct.pack("<I", self._seq)


class Stopwatch:
    def __init__(self):
        self.stages = {}

    def add(self, name, dt):
        self.stages.setdefault(name, []).append(dt)

    def report(self):
        print("\n=== per-stage profile (ms) ===")
        total = None
        for name, ts in self.stages.items():
            a = np.asarray(ts) * 1e3
            print(f"  {name:12s} p50 {np.percentile(a, 50):7.2f}  "
                  f"p95 {np.percentile(a, 95):7.2f}  "
                  f"p99 {np.percentile(a, 99):7.2f}  max {a.max():7.2f}")
            if name == "total":
                total = a
        return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bag", default=str(ROOT / "Video/recording_20260224_083945.bag"))
    ap.add_argument("--model", default="heavy")
    ap.add_argument("--delegate", default="auto")
    ap.add_argument("--min-vis", type=float, default=0.5)
    ap.add_argument("--depth-window", type=int, default=5)
    ap.add_argument("--shm", default="/dev/shm/rt_person")
    ap.add_argument("--dump-csv", default=None)
    ap.add_argument("--profile", action="store_true")
    ap.add_argument("--parallel-arms", action="store_true",
                    help="run L/R arm solves in 2 threads (measured slower; "
                         "kept for the study)")
    ap.add_argument("--max-frames", type=int, default=None)
    ap.add_argument("--sync-file", default=None,
                    help="start barrier: touch <sync>.ready.person after "
                         "init, open the bag only once <sync> exists (the "
                         "launcher creates it when every pipeline is ready "
                         "— emulates both pipelines sharing one camera)")
    args = ap.parse_args()

    model_path = resolve_model(args.model, ROOT / "mediapipe/models")
    landmarker, delegate = make_landmarker(model_path, args.delegate)
    print(f"[info] MediaPipe {args.model} on {delegate}, bag: {args.bag}")

    if args.sync_file:
        Path(args.sync_file + ".ready.person").touch()
        while not Path(args.sync_file).exists():
            time.sleep(0.005)

    pipeline, align, intrinsics, color_format = open_bag_realtime(args.bag)
    filt = CausalLandmarkFilter()
    solver = ChainFallbackSolver()
    writer = ShmWriter(args.shm)
    watch = Stopwatch()
    pool = None
    if args.parallel_arms:
        from concurrent.futures import ThreadPoolExecutor
        pool = ThreadPoolExecutor(2)
        from occlusion import (BIT_L_ELBOW, BIT_L_SWING, BIT_L_TWIST,
                               BIT_R_ELBOW, BIT_R_SWING, BIT_R_TWIST)
        from shoulder import solve_left_arm, solve_right_arm

    dump_rows = []
    import cv2

    frame_count = 0
    first_ts = None
    last_mp_ts = -1
    last_pelvis = np.zeros(3)
    t_start = time.monotonic()

    try:
        while args.max_frames is None or frame_count < args.max_frames:
            try:
                frames = pipeline.wait_for_frames(timeout_ms=5000)
            except RuntimeError:
                break
            t0 = time.perf_counter()
            aligned = align.process(frames)
            color_frame = aligned.get_color_frame()
            depth_frame = aligned.get_depth_frame()
            if not color_frame or not depth_frame:
                continue
            t1 = time.perf_counter()

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
            t2 = time.perf_counter()

            points = {}
            if result and result.pose_landmarks:
                lms = deproject_landmarks(result.pose_landmarks[0],
                                          depth_frame, intrinsics,
                                          TORSO_AND_ARMS, args.min_vis,
                                          args.depth_window)
                for idx in TORSO_AND_ARMS:
                    name = LANDMARK_NAMES[idx]
                    xyz = lms[idx]["xyz"]
                    fx = filt(name, np.asarray(xyz) if xyz is not None else None)
                    if fx is not None:
                        points[name] = unity_from_sensor(fx)
            t3 = time.perf_counter()

            if pool is None:
                angles, mask = solver.solve(points)
            else:
                # study variant: root on this thread, arms in parallel
                p = {k: (np.asarray(points[k], float) if k in points else None)
                     for k in LANDMARKS}
                ok = {k: (p[k] is not None and np.all(np.isfinite(p[k])))
                      for k in LANDMARKS}
                mask = 0
                ref = (p["right_shoulder"] if ok["right_shoulder"]
                       else p["left_shoulder"] if ok["left_shoulder"] else None)
                if ok["left_hip"] and ok["right_hip"] and ref is not None:
                    from root_frame import build_root_frame, euler_unity_zxy
                    solver.R_root = build_root_frame(p["left_hip"],
                                                     p["right_hip"], ref)
                    solver.root = euler_unity_zxy(solver.R_root)
                    from occlusion import BIT_ROOT
                    mask |= BIT_ROOT
                fr = pool.submit(solver._arm, p, ok, "right_shoulder",
                                 "right_elbow", "right_wrist",
                                 solve_right_arm, solver.rsh, solver.relb,
                                 BIT_R_SWING, BIT_R_TWIST, BIT_R_ELBOW)
                fl = pool.submit(solver._arm, p, ok, "left_shoulder",
                                 "left_elbow", "left_wrist",
                                 solve_left_arm, solver.lsh, solver.lelb,
                                 BIT_L_SWING, BIT_L_TWIST, BIT_L_ELBOW)
                mask |= fr.result() | fl.result()
                angles = np.concatenate([solver.root, solver.rsh, solver.relb,
                                         solver.lsh, solver.lelb])

            if "left_hip" in points and "right_hip" in points:
                last_pelvis = 0.5 * (points["left_hip"] + points["right_hip"])
            t4 = time.perf_counter()

            writer.write(frame_count, rel_s, last_pelvis, angles, mask)
            t5 = time.perf_counter()

            watch.add("align+get", t1 - t0)
            watch.add("mediapipe", t2 - t1)
            watch.add("deproj+filt", t3 - t2)
            watch.add("solve", t4 - t3)
            watch.add("shm-write", t5 - t4)
            watch.add("total", t5 - t0)

            if args.dump_csv:
                dump_rows.append([frame_count, rel_s, *last_pelvis,
                                  *angles, mask, (t5 - t0) * 1e3])
            frame_count += 1
    finally:
        pipeline.stop()
        if pool is not None:
            pool.shutdown()

    wall = time.monotonic() - t_start
    print(f"[done] {frame_count} frames in {wall:.1f} s "
          f"({frame_count / wall:.1f} fps sustained)")
    if args.profile or True:
        total = watch.report()
        if total is not None:
            budget = 1000.0 / 30.0
            print(f"  30 fps budget {budget:.1f} ms -> p99 headroom "
                  f"{budget - np.percentile(total, 99):.1f} ms")

    if args.dump_csv:
        import csv as csvmod
        out = Path(args.dump_csv)
        out.parent.mkdir(exist_ok=True)
        cols = (["frame", "time_s", "pel_x", "pel_y", "pel_z"]
                + [f"a{i}" for i in range(13)] + ["mask", "compute_ms"])
        with open(out, "w", newline="") as f:
            w = csvmod.writer(f)
            w.writerow(cols)
            w.writerows(dump_rows)
        print(f"[csv] {out}")


if __name__ == "__main__":
    main()

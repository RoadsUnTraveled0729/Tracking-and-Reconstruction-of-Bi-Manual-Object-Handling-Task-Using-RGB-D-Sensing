#!/usr/bin/env python3
# Filename: v2/person/v2_person.py
"""v2 Pipeline A: PSF1 frame ring -> landmarks -> causal filter ->
13-angle solve -> PSR1 shared memory.

A thin fork of realtime/person/realtime_person.py (v1, frozen): the ONLY
structural change is the frame source. v1 opened the bag itself; v2 reads
the capture broker's ring, so a live camera and bag playback are the same
code path. Everything downstream is reused by import from the v1 module:
CausalLandmarkFilter (both v1 causal-filter trap fixes included by
construction), ChainFallbackSolver, ShmWriter/PSR1.

Consumption is latest-wins (reader.latest): if this pipeline runs slower
than the broker publishes, intermediate publications are skipped -- the
correct live semantics (a slow consumer drops frames), counted and
reported at exit.

time_s in PSR1 is the SHARED session clock (hw_ts_ms - t0_hw_ms)/1000
from the ring header, so Pipeline A and B timestamps agree exactly.

Usage:
  python v2_person.py [--ring /dev/shm/rt_frames] [--shm /dev/shm/rt_person_v2]
      [--model heavy] [--dump-csv ../output/v2_person_dump.csv]
      [--profile] [--max-frames N] [--sync-file PATH]
      [--filter-freq 30] [--min-cutoff 1.0] [--beta 1.0]
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import cv2
import pyrealsense2 as rs
import mediapipe as mp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                 # repo root (v2/person/ -> repo)
sys.path.insert(0, str(ROOT / "v2/common"))
sys.path.insert(0, str(ROOT / "v1/realtime/person"))

import realtime_person                 # self-configures mediapipe/ + kinematics/
from realtime_person import CausalLandmarkFilter, ShmWriter, Stopwatch
from extract_landmarks_to_csv import (LANDMARK_NAMES, TORSO_AND_ARMS,
                                      deproject_landmarks, make_landmarker,
                                      resolve_model)
from occlusion import ChainFallbackSolver
from root_frame import unity_from_sensor
from shm_ring import FrameRingReader


class DepthArray:
    """Adapter: the ring's copied depth ndarray, quacking like the
    rs.depth_frame that deproject_landmarks() consumes (get_data /
    get_units are the only two calls it makes)."""

    def __init__(self, depth, depth_scale):
        self._depth = depth
        self._scale = depth_scale

    def get_data(self):
        return self._depth

    def get_units(self):
        return self._scale


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ring", default="/dev/shm/rt_frames")
    ap.add_argument("--shm", default="/dev/shm/rt_person_v2")
    ap.add_argument("--model", default="heavy")
    ap.add_argument("--delegate", default="auto")
    ap.add_argument("--min-vis", type=float, default=0.5)
    ap.add_argument("--depth-window", type=int, default=5)
    ap.add_argument("--dump-csv", default=None)
    ap.add_argument("--profile", action="store_true")
    ap.add_argument("--max-frames", type=int, default=None)
    ap.add_argument("--sync-file", default=None,
                    help="start barrier: touch <sync>.ready.person after "
                         "init, attach to the ring only once <sync> exists")
    ap.add_argument("--filter-freq", type=float, default=30.0)
    ap.add_argument("--min-cutoff", type=float, default=1.0)
    ap.add_argument("--beta", type=float, default=1.0)
    ap.add_argument("--robust-occlusion", action="store_true",
                    help="use RobustChainSolver (segment-length gate + "
                         "sphere wrist recovery, occlusion_ext.py) "
                         "instead of the hold-last baseline")
    ap.add_argument("--object-recovery", action="store_true",
                    help="E-014 live: read Pipeline B's object pose and "
                         "feed the solver's obj input (object-derived "
                         "wrist during failures); requires "
                         "--robust-occlusion and --calib")
    ap.add_argument("--obj-shm", default="/dev/shm/rt_object_v2")
    ap.add_argument("--calib", default=None,
                    help="scene calibration JSON (for --object-recovery)")
    args = ap.parse_args()
    if args.object_recovery and not (args.robust_occlusion and args.calib):
        sys.exit("[ERROR] --object-recovery requires --robust-occlusion "
                 "and --calib")

    model_path = resolve_model(args.model, ROOT / "v1/mediapipe/models")
    landmarker, delegate = make_landmarker(model_path, args.delegate)
    print(f"[info] MediaPipe {args.model} on {delegate}, ring: {args.ring}")

    if args.sync_file:
        Path(args.sync_file + ".ready.person").touch()
        while not Path(args.sync_file).exists():
            time.sleep(0.005)

    reader = FrameRingReader(args.ring, wait_s=30.0)
    color_format = rs.format(reader.color_format)
    intrinsics = reader.intrinsics()
    filt = CausalLandmarkFilter(freq=args.filter_freq,
                                min_cutoff=args.min_cutoff, beta=args.beta)
    if args.robust_occlusion:
        from occlusion_ext import RobustChainSolver
        solver = RobustChainSolver()
        print("[info] robust occlusion solver (gate + sphere recovery)")
    else:
        solver = ChainFallbackSolver()
    if args.robust_occlusion:
        # PSR2 = PSR1 with the solver tags in the former pad bytes
        from person_shm_v2 import ShmWriterV2
        writer = ShmWriterV2(args.shm)
    else:
        writer = ShmWriter(args.shm)
    link_reader = link_tracker = None
    if args.object_recovery:
        import json
        from object_link import GripTracker, ObjectPoseReader
        calib = json.loads(Path(args.calib).read_text())
        link_reader = ObjectPoseReader(args.obj_shm, calib)
        link_tracker = GripTracker(
            float(calib["scene_geometry"]["object_cube_size_m"]))
        print(f"[info] object recovery on ({args.obj_shm}, cube "
              f"{link_tracker.center_off[1]*-2000:.0f} mm)")
    watch = Stopwatch()

    dump_rows = []
    consumed = 0
    skipped = 0
    last_c = 0
    last_mp_ts = -1
    last_pelvis = np.zeros(3)
    t_start = time.monotonic()
    t0_hw = None

    while args.max_frames is None or consumed < args.max_frames:
        try:
            c, sample = reader.latest(last_c, timeout_s=10.0)
        except TimeoutError:
            print("[WARNING] ring writer went silent without EOF")
            break
        if sample is None:
            break                                     # broker EOF
        skipped += c - last_c - 1
        last_c = c
        t0 = time.perf_counter()
        if t0_hw is None:
            t0_hw = reader.t0_hw_ms
        rel_s = (sample.hw_ts_ms - t0_hw) / 1000.0

        rgb = (sample.color if color_format == rs.format.rgb8
               else cv2.cvtColor(sample.color, cv2.COLOR_BGR2RGB))
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,
                            data=np.ascontiguousarray(rgb))
        mp_ts = max(int(rel_s * 1000), last_mp_ts + 1)
        last_mp_ts = mp_ts
        result = landmarker.detect_for_video(mp_image, mp_ts)
        t1 = time.perf_counter()

        points = {}
        if result and result.pose_landmarks:
            depth_frame = DepthArray(sample.depth, reader.depth_scale)
            lms = deproject_landmarks(result.pose_landmarks[0], depth_frame,
                                      intrinsics, TORSO_AND_ARMS,
                                      args.min_vis, args.depth_window)
            for idx in TORSO_AND_ARMS:
                name = LANDMARK_NAMES[idx]
                xyz = lms[idx]["xyz"]
                fx = filt(name, np.asarray(xyz) if xyz is not None else None)
                if fx is not None:
                    points[name] = unity_from_sensor(fx)
        t2 = time.perf_counter()

        if link_tracker is not None:
            oc = link_reader.read(sample.frame_idx)
            fa_len = {"right": solver.L.get("forearm_R"),
                      "left": solver.L.get("forearm_L")}
            obs, d6 = link_tracker.update(sample.frame_idx, points, oc,
                                          fa_len)
            for side in d6:
                points.pop(f"{side}_wrist", None)
            out = solver.solve(points, obj=obs)
        else:
            obs = None
            out = solver.solve(points)
        angles, mask = out[0], out[1]
        tags = out[2] if len(out) > 2 else (0,) * 7
        if "left_hip" in points and "right_hip" in points:
            last_pelvis = 0.5 * (points["left_hip"] + points["right_hip"])
        t3 = time.perf_counter()

        if args.robust_occlusion:
            writer.write(sample.frame_idx, rel_s, last_pelvis, angles,
                         mask, tags)
        else:
            writer.write(sample.frame_idx, rel_s, last_pelvis, angles, mask)
        t4 = time.perf_counter()

        watch.add("mediapipe", t1 - t0)
        watch.add("deproj+filt", t2 - t1)
        watch.add("solve", t3 - t2)
        watch.add("shm-write", t4 - t3)
        watch.add("total", t4 - t0)
        if args.dump_csv:
            dump_rows.append([sample.frame_idx, rel_s, *last_pelvis,
                              *angles, mask, (t4 - t0) * 1e3, *tags,
                              int(obs is not None
                                  and obs.get("right") is not None),
                              int(obs is not None
                                  and obs.get("left") is not None)])
        consumed += 1

    wall = time.monotonic() - t_start
    print(f"[done] consumed {consumed} frames ({skipped} skipped by "
          f"latest-wins) in {wall:.1f} s ({consumed / wall:.1f} fps sustained)")
    if args.robust_occlusion:
        print(f"[robust] gated {solver.gated}, recovered {solver.recovered}, "
              f"stabilized {solver.stabilized}, "
              f"calibrated forearm lengths "
              f"{ {k: round(v, 3) for k, v in solver.L.items()} } m")
    if link_tracker is not None:
        link_tracker.close(last_c)
        sk = np.asarray(link_reader.skews) if link_reader.skews else \
            np.zeros(1)
        print(f"[recovery] obj-recovered {solver.obj_recovered}, "
              f"grip {link_tracker.summary()}, "
              f"B-A frame skew p50 {np.percentile(sk, 50):.0f} "
              f"p99 {np.percentile(sk, 99):.0f} "
              f"(dropped {link_reader.skew_dropped} stale)")
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
                + [f"a{i}" for i in range(13)] + ["mask", "compute_ms"]
                + [f"tag_{i}" for i in range(7)]
                + ["rec_right", "rec_left"])
        with open(out, "w", newline="") as f:
            w = csvmod.writer(f)
            w.writerow(cols)
            w.writerows(dump_rows)
        print(f"[csv] {out}")


if __name__ == "__main__":
    main()

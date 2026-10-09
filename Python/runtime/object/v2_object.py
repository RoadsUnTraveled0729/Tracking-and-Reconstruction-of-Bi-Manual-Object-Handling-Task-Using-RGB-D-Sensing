#!/usr/bin/env python3
# Filename: runtime/object/v2_object.py
"""v2 Pipeline B: PSF1 frame ring -> ArUco detect + IPPE -> desk-anchored
object pose -> causal filter -> PSB2 shared memory.

A thin fork of realtime/object/realtime_object.py (v1, frozen): the ONLY
structural change is the frame source (the capture broker's ring instead
of opening the bag itself). The causal stack is reused by import from the
v1 module: CausalObjectFilter (with its deliberately duplicated One-Euro
-- pipeline independence), LobeTracker, the frozen-or-live scene
calibration JSON. No mediapipe/ code is imported.

time_s in PSB2 is the SHARED session clock (hw_ts_ms - t0_hw_ms)/1000
from the ring header, so Pipeline A and B timestamps agree exactly.

Usage:
  python v2_object.py [--ring /dev/shm/rt_frames] [--shm /dev/shm/rt_object_v2]
      [--calib ../../core/aruco/output/scene_calibration.json]
      [--dump-csv ../output/v2_object_dump.csv] [--profile]
      [--max-frames N] [--sync-file PATH]
"""
import argparse
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import pyrealsense2 as rs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                 # repo root (runtime/object/ -> repo)
sys.path.insert(0, str(ROOT / "runtime/common"))
sys.path.insert(0, str(ROOT / "core/realtime/object"))

import realtime_object                 # self-configures aruco/ path
from realtime_object import OBJECT_ID, CausalObjectFilter
from extract_aruco_poses import (ARUCO_DICT_ID, LobeTracker, camera_matrices,
                                 solve_marker_pose)
from frames import (euler_unity_zxy, geodesic_deg, inv_T, make_T,
                    unity_from_world)
from send_scene_poses import ObjectWriter
from shm_ring import FrameRingReader


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ring", default="/dev/shm/rt_frames")
    ap.add_argument("--shm", default="/dev/shm/rt_object_v2")
    ap.add_argument("--calib", default=str(ROOT / "core/aruco/output/scene_calibration.json"))
    ap.add_argument("--dump-csv", default=None)
    ap.add_argument("--profile", action="store_true")
    ap.add_argument("--max-frames", type=int, default=None)
    ap.add_argument("--sync-file", default=None,
                    help="start barrier (see v2_person.py --sync-file)")
    ap.add_argument("--plausibility-gate", action="store_true",
                    help="E-019 live: reject a desk-anchored sample "
                         "faster than V_MAX / W_MAX versus the last "
                         "KEPT sample (physically implausible for the "
                         "slow-manipulation task); rejects become "
                         "ordinary dropouts (live=0)")
    args = ap.parse_args()
    if args.plausibility_gate:
        from runtime_parameters import V_MAX, W_MAX_DEG
        print(f"[info] plausibility gate on ({V_MAX} m/s, "
              f"{W_MAX_DEG} deg/s, E-019)")
    else:
        V_MAX = W_MAX_DEG = None

    calib = json.loads(Path(args.calib).read_text())
    T_desk_cam = inv_T(np.asarray(calib["T_cam_desk"], float))
    size_m = float(calib["markers"][str(OBJECT_ID)]["size_m"])
    print(f"[info] calibration: {args.calib} "
          f"(object marker {size_m*1000:.0f} mm)")

    det_params = cv2.aruco.DetectorParameters()
    det_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_APRILTAG
    detector = cv2.aruco.ArucoDetector(
        cv2.aruco.getPredefinedDictionary(ARUCO_DICT_ID), det_params)
    tracker = LobeTracker()

    if args.sync_file:
        Path(args.sync_file + ".ready.object").touch()
        while not Path(args.sync_file).exists():
            time.sleep(0.005)

    reader = FrameRingReader(args.ring, wait_s=30.0)
    color_format = rs.format(reader.color_format)
    K, dist = camera_matrices(reader.intrinsics())
    filt = CausalObjectFilter()
    writer = ObjectWriter(args.shm)

    stages = {n: [] for n in ("detect", "pnp", "filter+map", "total")}
    dump = []
    consumed = 0
    skipped = 0
    detected_count = 0
    last_c = 0
    last_pos_u = np.zeros(3)
    last_eul_u = np.zeros(3)
    last_kept = None                   # (t, pos, R) of last gate-kept
    gate_rejects = 0
    t0_hw = None
    t_start = time.monotonic()

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

        img = sample.color
        if color_format == rs.format.rgb8:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        corners, ids, _ = detector.detectMarkers(img)
        t1 = time.perf_counter()

        live = 0
        if ids is not None and OBJECT_ID in ids.ravel():
            i = int(np.flatnonzero(ids.ravel() == OBJECT_ID)[0])
            sol = solve_marker_pose(corners[i].reshape(4, 2), size_m,
                                    K, dist, None, tracker)
            t2 = time.perf_counter()
            if sol is not None:
                R_cam, t_cam, _reproj, _ambig = sol
                T_obj = T_desk_cam @ make_T(R_cam, t_cam)
                if args.plausibility_gate:
                    if last_kept is not None:
                        dt = rel_s - last_kept[0]
                        dp = np.linalg.norm(T_obj[:3, 3] - last_kept[1])
                        dr = geodesic_deg(last_kept[2], T_obj[:3, :3])
                        if dp > V_MAX * dt or dr > W_MAX_DEG * dt:
                            gate_rejects += 1
                            sol = None    # implausible -> dropout
                    if sol is not None:
                        last_kept = (rel_s, T_obj[:3, 3].copy(),
                                     T_obj[:3, :3].copy())
            if sol is not None:
                res = filt(T_obj[:3, 3], T_obj[:3, :3])
                if res is not None:
                    t_f, R_f = res
                    pos_u, R_u = unity_from_world(R_f, t_f)
                    last_pos_u = pos_u
                    last_eul_u = euler_unity_zxy(R_u)
                    live = 1
                    detected_count += 1
        else:
            t2 = time.perf_counter()
        t3 = time.perf_counter()

        writer.write(sample.frame_idx, rel_s, last_pos_u, last_eul_u, live)
        t4 = time.perf_counter()

        stages["detect"].append(t1 - t0)
        stages["pnp"].append(t2 - t1)
        stages["filter+map"].append(t3 - t2)
        stages["total"].append(t4 - t0)
        if args.dump_csv:
            dump.append([sample.frame_idx, rel_s, live, *last_pos_u,
                         *last_eul_u, (t4 - t0) * 1e3])
        consumed += 1

    wall = time.monotonic() - t_start
    print(f"[done] consumed {consumed} frames ({skipped} skipped by "
          f"latest-wins) in {wall:.1f} s ({consumed / wall:.1f} fps "
          f"sustained), object live on {detected_count}")
    if args.plausibility_gate:
        print(f"[gate] E-019 plausibility gate rejected {gate_rejects} "
              f"detected sample(s)")
    print("\n=== per-stage profile (ms) ===")
    for name, ts in stages.items():
        a = np.asarray(ts) * 1e3
        print(f"  {name:12s} p50 {np.percentile(a, 50):7.2f}  "
              f"p95 {np.percentile(a, 95):7.2f}  "
              f"p99 {np.percentile(a, 99):7.2f}  max {a.max():7.2f}")

    if args.dump_csv:
        import csv as csvmod
        out = Path(args.dump_csv)
        out.parent.mkdir(exist_ok=True)
        with open(out, "w", newline="") as f:
            w = csvmod.writer(f)
            w.writerow(["frame", "time_s", "live", "ux", "uy", "uz",
                        "ex", "ey", "ez", "compute_ms"])
            w.writerows(dump)
        print(f"[csv] {out}")


if __name__ == "__main__":
    main()

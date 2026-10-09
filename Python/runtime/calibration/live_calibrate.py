#!/usr/bin/env python3
# Filename: runtime/calibration/live_calibrate.py
"""v2 live scene calibration: collect marker observations from the
capture broker's frame ring, then hand them to the UNCHANGED v1
calibrator (aruco/calibrate_scene.py) via subprocess -- zero logic
duplication, output JSON schema identical by construction.

Phase A (gravity seed): mirror of the extractor's tabletop logic
(aruco/extract_aruco_poses.py): a plane fitted to depth annuli around
the desk marker (plus the object's annulus when the cube demonstrably
rests on the desk), averaged over the first 10 valid desk frames, then
frozen. Running this BEFORE any pose solving guarantees every written
row had the gravity seed available for wall-lobe disambiguation --
slightly more conservative than the extractor, same policy.

Phase B (observations): fresh LobeTrackers, then the extractor's exact
per-frame solve on every ring frame, rows written in the extractor's
exact CSV column layout with the matching .meta.json, until both static
markers (wall id 0, desk id 2) have --calib-frames detections.

Phase C: subprocess aruco/calibrate_scene.py --csv <collected> --out
<json>. --cube-size passes through for a session where the cube never
rests on the desk.

Usage (normally via run_v2.py --calibrate):
  python live_calibrate.py [--ring /dev/shm/rt_frames]
      [--out runtime/output/scene_calibration_live.json]
      [--calib-frames 10] [--skip 30] [--timeout 30]
      [--cube-size M] [--compare aruco/output/scene_calibration.json]
"""
import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import pyrealsense2 as rs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                 # repo root
sys.path.insert(0, str(ROOT / "runtime/common"))
sys.path.insert(0, str(ROOT / "core/aruco"))

from extract_aruco_poses import (ARUCO_DICT_ID, ARUCO_DICT_NAME, LobeTracker,
                                 camera_matrices, estimate_tabletop,
                                 intrinsics_to_dict, sample_depth,
                                 solve_marker_pose)
from frames import MARKER_IDS, MARKERS
from shm_ring import FrameRingReader


def gray_of(sample, color_format):
    return cv2.cvtColor(sample.color, cv2.COLOR_RGB2GRAY
                        if color_format == rs.format.rgb8
                        else cv2.COLOR_BGR2GRAY)


def detect(detector, gray):
    corners_list, ids, _ = detector.detectMarkers(gray)
    found = {}
    if ids is not None:
        for c, mid in zip(corners_list, ids.flatten()):
            if int(mid) in MARKERS:
                found[int(mid)] = c
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ring", default="/dev/shm/rt_frames")
    ap.add_argument("--out", default=str(ROOT / "runtime/output/scene_calibration_live.json"))
    ap.add_argument("--calib-frames", type=int, default=10)
    ap.add_argument("--skip", type=int, default=30,
                    help="ring frames to skip before phase A (live "
                         "auto-exposure settle; use 0 on bag playback)")
    ap.add_argument("--timeout", type=float, default=30.0,
                    help="per-phase timeout")
    ap.add_argument("--depth-window", type=int, default=5)
    ap.add_argument("--cube-size", type=float, default=None,
                    help="passed through to calibrate_scene.py when the "
                         "cube never rests on the desk")
    ap.add_argument("--compare", default=None,
                    help="existing calibration JSON to diff against")
    args = ap.parse_args()

    out_json = Path(args.out)
    out_json.parent.mkdir(exist_ok=True)
    out_csv = out_json.parent / "live_aruco_raw.csv"
    out_meta = out_csv.with_suffix(".meta.json")

    reader = FrameRingReader(args.ring, wait_s=args.timeout)
    color_format = rs.format(reader.color_format)
    intr = reader.intrinsics()
    K, dist = camera_matrices(intr)

    det_params = cv2.aruco.DetectorParameters()
    det_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_APRILTAG
    detector = cv2.aruco.ArucoDetector(
        cv2.aruco.getPredefinedDictionary(ARUCO_DICT_ID), det_params)

    last_c = 0
    skipped = 0
    while skipped < args.skip:
        last_c, sample = reader.latest(last_c, timeout_s=args.timeout)
        if sample is None:
            sys.exit("[ERROR] ring ended during the auto-exposure skip")
        skipped += 1

    # ---- phase A: gravity seed (the extractor's tabletop logic) ------
    grav_samples, grav_pts_desk, grav_pts_obj = [], [], []
    gravity_up = None
    tabletop_point_desk = None
    tabletop_point_obj = None
    t0 = time.monotonic()
    frames_seen = 0
    while len(grav_samples) < 10:
        if time.monotonic() - t0 > args.timeout:
            sys.exit(f"[ERROR] gravity seed: only {len(grav_samples)}/10 "
                     f"valid desk-annulus frames in {args.timeout:.0f} s "
                     f"({frames_seen} frames seen) -- is the desk marker "
                     f"(id 2) in view with clear desk around it?")
        try:
            last_c, sample = reader.latest(last_c, timeout_s=args.timeout)
        except TimeoutError:
            sys.exit("[ERROR] ring writer went silent during phase A")
        if sample is None:
            sys.exit("[ERROR] ring ended during phase A")
        frames_seen += 1
        found = detect(detector, gray_of(sample, color_format))
        if 2 not in found:
            continue
        est = estimate_tabletop(sample.depth, reader.depth_scale,
                                [found[2]], intr, args.depth_window)
        if est is None:
            continue
        up_sample = est[0]
        grav_pts_desk.append(est[2][0])
        if 1 in found:
            est2 = estimate_tabletop(sample.depth, reader.depth_scale,
                                     [found[2], found[1]], intr,
                                     args.depth_window)
            if est2 is not None and float(np.degrees(np.arccos(
                    np.clip(np.dot(est[0], est2[0]), -1, 1)))) < 15.0:
                up_sample = est2[0]
                grav_pts_obj.append(est2[2][1])
        grav_samples.append(up_sample)
    up = np.mean(grav_samples, axis=0)
    gravity_up = up / np.linalg.norm(up)
    tabletop_point_desk = np.mean(grav_pts_desk, axis=0)
    if grav_pts_obj:
        tabletop_point_obj = np.mean(grav_pts_obj, axis=0)
    print(f"[info] gravity seed frozen from {len(grav_samples)} frames "
          f"({len(grav_pts_obj)} with the object annulus): "
          f"{np.round(gravity_up, 4).tolist()}")

    # ---- phase B: observations in the extractor's exact CSV layout ---
    header = ["frame", "time_s"]
    for mid in MARKER_IDS:
        p = f"m{mid}"
        header += [f"{p}_detected", f"{p}_tx", f"{p}_ty", f"{p}_tz"]
        header += [f"{p}_r{i}{j}" for i in (1, 2, 3) for j in (1, 2, 3)]
        header += [f"{p}_reproj_px", f"{p}_ambig", f"{p}_u", f"{p}_v",
                   f"{p}_depth_z"]

    trackers = {mid: LobeTracker() for mid in MARKER_IDS}
    det_counts = {mid: 0 for mid in MARKER_IDS}
    t0 = time.monotonic()
    frame_count = 0
    t0_hw = reader.t0_hw_ms
    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        while (det_counts[0] < args.calib_frames
               or det_counts[2] < args.calib_frames):
            if time.monotonic() - t0 > args.timeout:
                sys.exit(f"[ERROR] observations: wall {det_counts[0]} and "
                         f"desk {det_counts[2]} of {args.calib_frames} "
                         f"needed detections in {args.timeout:.0f} s -- "
                         f"are both static markers in view?")
            try:
                last_c, sample = reader.latest(last_c, timeout_s=args.timeout)
            except TimeoutError:
                sys.exit("[ERROR] ring writer went silent during phase B")
            if sample is None:
                sys.exit("[ERROR] ring ended during phase B")
            found = detect(detector, gray_of(sample, color_format))
            rel_s = (sample.hw_ts_ms - t0_hw) / 1000.0
            row = [frame_count, f"{rel_s:.6f}"]
            for mid in MARKER_IDS:
                pose = (solve_marker_pose(found[mid], MARKERS[mid][1], K,
                                          dist, gravity_up, trackers[mid])
                        if mid in found else None)
                if pose is None:
                    row += [0] + [""] * 17
                    continue
                R, t, reproj, ambig = pose
                det_counts[mid] += 1
                u, v = np.asarray(found[mid]).reshape(4, 2).mean(axis=0)
                u, v = int(round(u)), int(round(v))
                dz = sample_depth(sample.depth, reader.depth_scale, u, v,
                                  args.depth_window)
                row += [1]
                row += [f"{x:.6f}" for x in t]
                row += [f"{x:.9f}" for x in R.flatten()]
                row += [f"{reproj:.4f}", ambig, u, v, f"{dz:.6f}"]
            writer.writerow(row)
            frame_count += 1
    print(f"[info] observations: {frame_count} frames, detections "
          + ", ".join(f"id{m} {det_counts[m]}" for m in MARKER_IDS))

    meta = {
        "source": f"live ring {args.ring} (runtime/calibration/live_calibrate.py)",
        "aruco_dict": ARUCO_DICT_NAME,
        "markers": {str(mid): {"role": MARKERS[mid][0],
                               "size_m": MARKERS[mid][1]}
                    for mid in MARKER_IDS},
        "frames_total": frame_count,
        "detections": {str(mid): det_counts[mid] for mid in MARKER_IDS},
        "tabletop": {
            "up_cam": [float(x) for x in gravity_up],
            "point_desk_cam": [float(x) for x in tabletop_point_desk],
            "point_obj_cam": None if tabletop_point_obj is None
                             else [float(x) for x in tabletop_point_obj],
            "frames_averaged": len(grav_samples),
            "obj_frames_averaged": len(grav_pts_obj),
            "note": "seed gravity from the desk-marker depth annulus; "
                    "authoritative gravity = wall marker in-plane up "
                    "(calibrate_scene.py)",
        },
        "color_intrinsics": intrinsics_to_dict(intr),
        "export_time": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    out_meta.write_text(json.dumps(meta, indent=2))

    # ---- phase C: the unchanged v1 calibrator ------------------------
    cmd = [sys.executable, str(ROOT / "core/aruco/calibrate_scene.py"),
           "--csv", str(out_csv), "--out", str(out_json),
           "--calib-frames", str(args.calib_frames)]
    if args.cube_size is not None:
        cmd += ["--cube-size", str(args.cube_size)]
    rc = subprocess.call(cmd)
    if rc != 0:
        sys.exit(f"[ERROR] calibrate_scene.py failed (exit {rc})")
    print(f"[done] live calibration: {out_json}")

    if args.compare:
        a = json.loads(Path(args.compare).read_text())
        b = json.loads(out_json.read_text())
        print(f"\n=== diff vs {args.compare} ===")
        for name in ("desk", "wall", "camera"):
            pa = np.asarray(a["poses_world"][name]["unity_position"])
            pb = np.asarray(b["poses_world"][name]["unity_position"])
            ea = np.asarray(a["poses_world"][name]["unity_euler_zxy_deg"])
            eb = np.asarray(b["poses_world"][name]["unity_euler_zxy_deg"])
            de = np.abs((eb - ea + 180.0) % 360.0 - 180.0)
            print(f"  {name:7s} pos delta {np.linalg.norm(pb - pa)*1e3:7.2f} mm"
                  f"   euler delta max {de.max():6.3f} deg")
        ga = np.asarray(a["scene_geometry"]["gravity_up_unity"])
        gb = np.asarray(b["scene_geometry"]["gravity_up_unity"])
        ang = np.degrees(np.arccos(np.clip(np.dot(ga, gb), -1, 1)))
        print(f"  gravity angle delta {ang:.3f} deg")
        print(f"  seed dev: frozen {a['scene_geometry']['gravity_seed_dev_deg']:.3f}"
              f" vs live {b['scene_geometry']['gravity_seed_dev_deg']:.3f} deg")


if __name__ == "__main__":
    main()

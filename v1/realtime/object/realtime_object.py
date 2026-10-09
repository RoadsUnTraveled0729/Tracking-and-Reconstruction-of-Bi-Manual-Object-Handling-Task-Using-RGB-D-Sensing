#!/usr/bin/env python3
# Filename: realtime/object/realtime_object.py
"""Real-time Pipeline B: bag playback (live-camera emulation) -> ArUco
detect + IPPE -> desk-anchored object pose -> causal filter -> PSB2 shm.

The static scene is the frozen offline calibration (calibrate-once design,
ARUCO_MODEL.md §3-4 — the anchor is a scene property, legitimately
precomputed; the merger ships it to Unity as PSB3). This loop handles only
the MOVING object, causally:

  color frame -> detectMarkers (APRILTAG refine) -> IPPE on marker id 1
  (lobes well-separated -> best reprojection, same policy as offline) ->
  T_desk_obj = T_desk_cam · T_cam_obj ->
  causal filter: trailing-Hampel despike (reject -> dropout) +
  One-Euro position + complementary geodesic rotation filter
      R_f <- R_f · exp(alpha · log(R_fᵀ R_meas))
  -> /dev/shm/rt_object, PSB2 (44 B, same layout the offline sender uses).

Marker covered / rejected: hold the last pose, live=0 (the honest-flag
convention shared with the whole system). No mediapipe/ code is imported —
pipeline independence; the One-Euro class is deliberately duplicated.

Usage:
  python realtime_object.py [--bag ../../Video/recording_20260224_083945.bag]
      [--calib ../../aruco/output/scene_calibration.json]
      [--shm /dev/shm/rt_object] [--dump-csv ../output/rt_object_dump.csv]
      [--profile] [--max-frames N]
"""
import argparse
import json
import sys
import time
from collections import deque
from pathlib import Path

import cv2
import numpy as np
import pyrealsense2 as rs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                 # repo root (realtime/object/ -> repo)
sys.path.insert(0, str(ROOT / "aruco"))

from extract_aruco_poses import (ARUCO_DICT_ID, LobeTracker, camera_matrices,
                                 solve_marker_pose)
from filter_object_track import exp_so3, log_so3
from frames import euler_unity_zxy, inv_T, make_T, unity_from_world
from send_scene_poses import ObjectWriter

OBJECT_ID = 1


class OneEuro:
    """Causal One-Euro filter, one scalar channel (duplicated from
    Pipeline A's filter_landmarks.py — pipelines share no code)."""

    def __init__(self, freq, min_cutoff, beta, d_cutoff=1.0):
        self.freq, self.min_cutoff, self.beta, self.d_cutoff = \
            freq, min_cutoff, beta, d_cutoff
        self._x = self._dx = None

    @staticmethod
    def _alpha(cutoff, freq):
        tau = 1.0 / (2 * np.pi * cutoff)
        return 1.0 / (1.0 + tau * freq)

    def __call__(self, x):
        if self._x is None:
            self._x, self._dx = x, 0.0
            return x
        dx = (x - self._x) * self.freq
        a_d = self._alpha(self.d_cutoff, self.freq)
        self._dx = a_d * dx + (1 - a_d) * self._dx
        cutoff = self.min_cutoff + self.beta * abs(self._dx)
        a = self._alpha(cutoff, self.freq)
        self._x = a * x + (1 - a) * self._x
        return self._x


class CausalObjectFilter:
    """Causal cleanup of the world-frame object pose."""

    MAX_REJECTS = 3   # a "spike" persisting this long is real motion —
                      # accept and re-seed, else a stale trailing window
                      # rejects everything forever (causal-filter lockout)

    def __init__(self, freq=30.0, window=7, k=3.0, abs_floor=0.02,
                 pos_min_cutoff=0.8, pos_beta=2.0, rot_cutoff_hz=3.0):
        self.hist = deque(maxlen=window)
        self.k, self.abs_floor = k, abs_floor
        self.euro = [OneEuro(freq, pos_min_cutoff, pos_beta) for _ in range(3)]
        tau = 1.0 / (2 * np.pi * rot_cutoff_hz)
        self.alpha_rot = 1.0 / (1.0 + tau * freq)
        self.R_f = None
        self.rejects = 0

    def __call__(self, t_w, R_w):
        """Measured world pose -> (t_filtered, R_filtered) or None if the
        sample is rejected as a spike (caller treats it as a dropout)."""
        if len(self.hist) >= 4:
            arr = np.asarray(self.hist)
            med = np.median(arr, axis=0)
            mad = np.median(np.abs(arr - med), axis=0)
            thr = np.maximum(self.abs_floor, self.k * 1.4826 * mad)
            if (np.any(np.abs(t_w - med) > thr)
                    and self.rejects < self.MAX_REJECTS):
                self.rejects += 1
                return None
            if self.rejects >= self.MAX_REJECTS:
                self.hist.clear()          # re-seed on sustained "spike"
        self.rejects = 0
        self.hist.append(t_w.copy())
        t_f = np.array([f(v) for f, v in zip(self.euro, t_w)])
        if self.R_f is None:
            self.R_f = R_w.copy()
        else:
            self.R_f = self.R_f @ exp_so3(
                self.alpha_rot * log_so3(self.R_f.T @ R_w))
        return t_f, self.R_f


def open_bag_realtime(bag_path):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(str(bag_path), repeat_playback=False)
    profile = pipeline.start(config)
    profile.get_device().as_playback().set_real_time(True)
    intrinsics = (profile.get_stream(rs.stream.color)
                  .as_video_stream_profile().get_intrinsics())
    color_format = profile.get_stream(rs.stream.color).format()
    return pipeline, intrinsics, color_format


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bag", default=str(ROOT / "Video/recording_20260224_083945.bag"))
    ap.add_argument("--calib", default=str(ROOT / "aruco/output/scene_calibration.json"))
    ap.add_argument("--shm", default="/dev/shm/rt_object")
    ap.add_argument("--dump-csv", default=None)
    ap.add_argument("--profile", action="store_true")
    ap.add_argument("--max-frames", type=int, default=None)
    ap.add_argument("--sync-file", default=None,
                    help="start barrier (see realtime_person.py --sync-file)")
    args = ap.parse_args()

    calib = json.loads(Path(args.calib).read_text())
    T_desk_cam = inv_T(np.asarray(calib["T_cam_desk"], float))
    size_m = float(calib["markers"][str(OBJECT_ID)]["size_m"])
    print(f"[info] frozen calibration: {args.calib} "
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

    pipeline, intrinsics, color_format = open_bag_realtime(args.bag)
    K, dist = camera_matrices(intrinsics)
    filt = CausalObjectFilter()
    writer = ObjectWriter(args.shm)

    stages = {n: [] for n in ("detect", "pnp", "filter+map", "total")}
    dump = []
    frame_count = 0
    detected_count = 0
    first_ts = None
    last_pos_u = np.zeros(3)
    last_eul_u = np.zeros(3)
    t_start = time.monotonic()

    try:
        while args.max_frames is None or frame_count < args.max_frames:
            try:
                frames = pipeline.wait_for_frames(timeout_ms=5000)
            except RuntimeError:
                break
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue
            t0 = time.perf_counter()
            ts_ms = frames.get_timestamp()
            if first_ts is None:
                first_ts = ts_ms
            rel_s = (ts_ms - first_ts) / 1000.0

            img = np.asanyarray(color_frame.get_data())
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

            writer.write(frame_count, rel_s, last_pos_u, last_eul_u, live)
            t4 = time.perf_counter()

            stages["detect"].append(t1 - t0)
            stages["pnp"].append(t2 - t1)
            stages["filter+map"].append(t3 - t2)
            stages["total"].append(t4 - t0)
            if args.dump_csv:
                dump.append([frame_count, rel_s, live, *last_pos_u,
                             *last_eul_u, (t4 - t0) * 1e3])
            frame_count += 1
    finally:
        pipeline.stop()

    wall = time.monotonic() - t_start
    print(f"[done] {frame_count} frames in {wall:.1f} s "
          f"({frame_count / wall:.1f} fps sustained), "
          f"object live on {detected_count}")
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

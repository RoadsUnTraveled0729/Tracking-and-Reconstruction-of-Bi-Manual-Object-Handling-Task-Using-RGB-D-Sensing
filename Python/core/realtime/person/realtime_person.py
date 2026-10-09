"""Causal landmark filtering and person-stream transport helpers."""
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

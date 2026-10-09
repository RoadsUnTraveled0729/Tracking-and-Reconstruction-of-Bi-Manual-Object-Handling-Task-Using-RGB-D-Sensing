"""Causal object filtering shared by the synchronized runtime."""
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

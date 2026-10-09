"""Object-track filtering and SO(3) interpolation helpers."""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

from frames import (R_COLS, chordal_mean, euler_unity_zxy, geodesic_deg,
                    unity_from_world)


def hampel_mask(pos, window, k, abs_floor):
    """pos: (F, 3) with NaNs. True where a sample spikes on any axis."""
    df = pd.DataFrame(pos)
    roll = df.rolling(window, center=True, min_periods=3)
    med = roll.median()
    resid = (df - med).abs()
    mad = (df - med).abs().rolling(window, center=True, min_periods=3).median()
    thresh = np.maximum(abs_floor, k * 1.4826 * mad)
    return (resid > thresh).any(axis=1).to_numpy() & np.isfinite(pos).all(axis=1)


def nan_runs(mask):
    idx = np.flatnonzero(np.diff(np.concatenate(([False], mask, [False]))))
    return list(zip(idx[::2], idx[1::2]))


def log_so3(R):
    """Rotation matrix -> axis-angle vector (rad), atan2-conditioned."""
    v = 0.5 * np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    s = np.linalg.norm(v)
    ang = np.arctan2(s, 0.5 * (np.trace(R) - 1.0))
    if s < 1e-12:
        return np.zeros(3)
    return v / s * ang


def exp_so3(w):
    """Axis-angle vector (rad) -> rotation matrix (Rodrigues)."""
    ang = np.linalg.norm(w)
    if ang < 1e-12:
        return np.eye(3)
    a = w / ang
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * (K @ K)


def geodesic_interp(Ra, Rb, s):
    """Interpolate from Ra (s=0) to Rb (s=1) along the SO(3) geodesic."""
    return Ra @ exp_so3(s * log_so3(Ra.T @ Rb))

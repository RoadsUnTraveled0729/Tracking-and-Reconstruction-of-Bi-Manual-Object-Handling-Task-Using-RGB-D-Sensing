"""Landmark filtering helpers and the causal One-Euro filter."""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, medfilt, savgol_filter

LANDMARKS = ["left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
             "left_wrist", "right_wrist", "left_hip", "right_hip"]

FLAG_RAW, FLAG_GLITCH_INTERP, FLAG_MISS_INTERP, FLAG_MISS = 0, 1, 2, 3


def hampel_mask(pos, window, k, abs_floor):
    """pos: (F, 3) with NaNs. True where a sample is a spike on any axis."""
    df = pd.DataFrame(pos)
    roll = df.rolling(window, center=True, min_periods=3)
    med = roll.median()
    resid = (df - med).abs()
    mad = (df - med).abs().rolling(window, center=True, min_periods=3).median()
    thresh = np.maximum(abs_floor, k * 1.4826 * mad)
    return (resid > thresh).any(axis=1).to_numpy() & np.isfinite(pos).all(axis=1)


def nan_runs(mask):
    """Yield (start, stop) index ranges of consecutive True values."""
    idx = np.flatnonzero(np.diff(np.concatenate(([False], mask, [False]))))
    return list(zip(idx[::2], idx[1::2]))


def fill_gaps(pos, t, max_gap, edge_fill=0):
    """Linearly interpolate NaN runs of length <= max_gap (interior only).
    Boundary runs (a landmark missing from frame 0, e.g. MediaPipe warm-up
    hallucinations gated by visibility, or missing through the last frame)
    cannot be interpolated — with edge_fill > 0, runs of length <= edge_fill
    touching either end are backfilled with the nearest valid sample
    (constant extrapolation) so the downstream solver never snaps from a
    held rest pose to the first live pose. The smoother runs after this, so
    the constant segment blends into the motion.
    Returns (filled positions, mask of samples that were filled)."""
    out = pos.copy()
    filled = np.zeros(len(pos), dtype=bool)
    missing = ~np.isfinite(pos).all(axis=1)
    valid_idx = np.flatnonzero(~missing)
    if len(valid_idx) < 2:
        return out, filled
    for start, stop in nan_runs(missing):
        run = stop - start
        interior = start > valid_idx[0] and stop <= valid_idx[-1]
        if interior and run <= max_gap:
            for ax in range(3):
                out[start:stop, ax] = np.interp(t[start:stop], t[~missing], pos[~missing, ax])
            filled[start:stop] = True
        elif not interior and run <= edge_fill:
            src = valid_idx[0] if start == 0 else valid_idx[-1]
            out[start:stop] = pos[src]
            filled[start:stop] = True
    return out, filled


class OneEuro:
    """Causal One-Euro filter (Casiez et al. 2012), one scalar channel."""

    def __init__(self, freq, min_cutoff, beta, d_cutoff=1.0):
        self.freq, self.min_cutoff, self.beta, self.d_cutoff = freq, min_cutoff, beta, d_cutoff
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


def smooth_segment(seg, method, fs, args):
    """Smooth one gap-free (N, 3) segment. Returns the segment unchanged when
    it is too short for the requested method."""
    n = len(seg)
    out = seg.copy()
    if method == "savgol":
        if n >= args.smooth_window:
            for ax in range(3):
                out[:, ax] = savgol_filter(seg[:, ax], args.smooth_window, args.smooth_polyorder)
    elif method == "median":
        w = args.smooth_window if args.smooth_window % 2 else args.smooth_window + 1
        if n >= w:
            for ax in range(3):
                out[:, ax] = medfilt(seg[:, ax], w)
    elif method == "butter":
        b, a = butter(args.butter_order, args.cutoff_hz, fs=fs)
        padlen = 3 * max(len(a), len(b))
        if n > padlen:
            for ax in range(3):
                out[:, ax] = filtfilt(b, a, seg[:, ax])
    elif method == "oneeuro":
        for ax in range(3):
            f = OneEuro(fs, args.oneeuro_mincutoff, args.oneeuro_beta)
            out[:, ax] = [f(v) for v in seg[:, ax]]
    return out


def smooth_landmark(pos, method, fs, args):
    """Apply the chosen smoother per contiguous valid segment."""
    if method == "none":
        return pos.copy()
    out = pos.copy()
    valid = np.isfinite(pos).all(axis=1)
    for start, stop in nan_runs(valid):
        out[start:stop] = smooth_segment(pos[start:stop], method, fs, args)
    return out

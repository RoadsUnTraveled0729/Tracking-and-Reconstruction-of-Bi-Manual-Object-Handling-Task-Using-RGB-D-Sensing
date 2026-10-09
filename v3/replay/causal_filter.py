"""Causal per-landmark cleanup: trailing-Hampel despike + One-Euro.

Copy-adapted from v1 (realtime/person/realtime_person.py
CausalLandmarkFilter; OneEuro copied VERBATIM from
mediapipe/filter_landmarks.py). Constants come from the config filter
block; the defaults there are v1's measured live tuning (D-015):
min_cutoff 1.0 Hz (the offline 0.05 Hz costs ~9 frames of lag in a
causal setting, v1 measurement), despike window 11 / k 3.0 /
abs floor 35 mm / max rejects 3.

Everything here is causal: this frame and past frames only.
"""
from collections import deque

import numpy as np

from core.skeleton import V1_LANDMARKS


class OneEuro:
    """Causal One-Euro filter (Casiez et al. 2012), one scalar channel.
    Verbatim copy of mediapipe/filter_landmarks.py OneEuro."""

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


class CausalLandmarkFilter:
    """Per-landmark causal cleanup, v1 semantics.

    Despike: a sample deviating from the trailing-window median by more
    than max(abs_floor, k * 1.4826 * MAD) on any axis is REJECTED and
    treated as missing this frame. A spike persisting max_rejects
    frames is real motion: accept and re-seed the window. Accepted
    samples pass through per-axis One-Euro.
    """

    def __init__(self, cfg_filter, landmarks=V1_LANDMARKS):
        f = cfg_filter
        self.window = int(f["despike_window"])
        self.k = float(f["despike_k"])
        self.abs_floor = float(f["despike_abs_floor_m"])
        self.max_rejects = int(f["despike_max_rejects"])
        freq = float(f["freq_hz"])
        mc, beta, dc = (float(f["min_cutoff"]), float(f["beta"]),
                        float(f["d_cutoff"]))
        self.hist = {n: deque(maxlen=self.window) for n in landmarks}
        self.euro = {n: [OneEuro(freq, mc, beta, dc) for _ in range(3)]
                     for n in landmarks}
        self.rejects = {n: 0 for n in landmarks}

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
                    and self.rejects[name] < self.max_rejects):
                self.rejects[name] += 1
                return None                      # spike -> missing
            if self.rejects[name] >= self.max_rejects:
                h.clear()                        # sustained -> real motion
        self.rejects[name] = 0
        h.append(np.asarray(xyz, float))
        return np.array([f(v) for f, v in zip(self.euro[name], xyz)])

#!/usr/bin/env python3
# Filename: v2/common/display_lpf.py
"""Display smoother for the merger's Unity output (E-018).

Vendored verbatim from eval/unity_check/send_scene_r5.py (provenance:
AngleLPF + _wrap, R5 round 2026-08-26); in v2 the merger IS the Unity
sender, so the smoother lives here. DISPLAY ONLY: it shapes the PSI2
packet at write time; every dump CSV stays unfiltered.

First-order low-pass (gain alpha) plus an output rate cap (max_step
per tick). Both parts are needed: the solver's transitions are 3-5
frame RAMPS at its slew bound, and any unity-gain linear filter
eventually follows a ramp at the ramp's own slope (measured on R5: a
single pole passed 14.7 of 15 deg/frame; a 2nd-order Butterworth 16
deg/frame with up to 52 deg of overshoot). The low-pass rounds
corners and kills isolated spikes; the rate cap bounds the on-screen
speed. Defaults: alpha 0.5 (tracking error p95 2.1 deg on the R5
recovery track), max_step 8 deg/tick for angles; the pelvis reuses
the class with max_step 0.02 m/tick (wrap is inert at metre scale).
alpha >= 1 with max_step = 0 disables.
"""
import numpy as np


def _wrap(d):
    return (d + 180.0) % 360.0 - 180.0


class AngleLPF:
    def __init__(self, alpha=0.5, max_step=8.0):
        self.alpha = alpha
        self.max_step = max_step
        self.y = None

    def __call__(self, x):
        x = np.asarray(x, float)
        if self.alpha >= 1.0 and not self.max_step:
            return x
        if self.y is None:
            self.y = x.copy()
            return x.copy()
        target = self.y + min(self.alpha, 1.0) * _wrap(x - self.y)
        d = _wrap(target - self.y)
        if self.max_step:
            d = np.clip(d, -self.max_step, self.max_step)
        self.y = _wrap(self.y + d)
        return self.y.copy()

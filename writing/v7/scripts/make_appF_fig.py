#!/usr/bin/env python3
"""Appendix F figure: characteristics of the four candidate smoothers.

The four candidates are the ones the filtering stage of the pipeline can
select: the zero-phase Butterworth low-pass used for the results, the
Savitzky-Golay polynomial smoother, the rolling median, and the causal
One Euro filter. Every parameter is the one the frozen filter run used,
read from the filter metadata of the rail recording.

  (a) how each candidate answers a CONSTRUCTED test signal, not recorded
      data: a still-move-still position profile with added broadband
      noise and one single-frame spike. Constructing the signal keeps
      the comparison readable, because the motion underneath is known
      exactly and can be drawn beside the four outputs. The main
      panel: shape following, spike handling and lag are all visible at
      once.
  (b) the gain against frequency of the two linear candidates, with the
      cutoff and the band that carries deliberate upper-body motion.

Output: writing/v7/figures/appF_fig_filters.png
Run:    python writing/v7/scripts/make_appF_fig.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt, freqz, medfilt, savgol_filter

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v7" / "figures"
META = (REPO / "v1" / "mediapipe" / "output"
        / "recording_20260831_065553_landmarks_filtered.meta.json")

par = json.loads(META.read_text())["params"]
FS = par["fs_hz"]
CUT = par["cutoff_hz"]
ORDER = par["butter_order"]
WIN = par["smooth_window"]
POLY = par["smooth_polyorder"]
MINCUT = par["oneeuro_mincutoff"]
BETA = par["oneeuro_beta"]
print("parameters:", par)


class OneEuro:
    """Causal One Euro filter, one scalar channel (the pipeline's own class)."""

    def __init__(self, freq, min_cutoff, beta, d_cutoff=1.0):
        self.freq, self.min_cutoff = freq, min_cutoff
        self.beta, self.d_cutoff = beta, d_cutoff
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


# ---- the constructed test signal (not recorded data) ---------------------
# A still-move-still position profile with broadband noise and one
# single-frame spike added. The underlying motion is known by
# construction, which is what lets panel (a) draw it beside the four
# filter outputs.
n = 210
t = np.arange(n) / FS
clean = np.zeros(n)
move = slice(60, 130)
u = np.linspace(0, 1, move.stop - move.start)
clean[move.start:move.stop] = 0.30 * (3 * u ** 2 - 2 * u ** 3)   # smooth move
clean[move.stop:] = 0.30
rng = np.random.default_rng(7)
noisy = clean + rng.normal(0, 0.004, n)
noisy[95] += 0.06                                                # one spike

b, a = butter(ORDER, CUT, fs=FS)
y_butter = filtfilt(b, a, noisy)
y_savgol = savgol_filter(noisy, WIN, POLY)
y_median = medfilt(noisy, WIN if WIN % 2 else WIN + 1)
f = OneEuro(FS, MINCUT, BETA)
y_oneeuro = np.array([f(v) for v in noisy])

fig = plt.figure(figsize=(11.0, 7.4))
gs = fig.add_gridspec(2, 1, height_ratios=[1.65, 1.0], hspace=0.32)

ax = fig.add_subplot(gs[0])
ax.plot(t, noisy, color="0.78", lw=1.0,
        label="constructed test signal (noise and one spike)")
ax.plot(t, clean, color="0.35", lw=1.2, ls="--",
        label="the known motion underneath")
for y, col, lab in ((y_savgol, "#c1121f",
                     "Savitzky-Golay, window %d, order %d" % (WIN, POLY)),
                    (y_median, "#2a9d8f", "rolling median, window %d" % WIN),
                    (y_oneeuro, "#b5179e",
                     "One Euro, causal (min cutoff %.2f Hz, beta %.1f)"
                     % (MINCUT, BETA)),
                    (y_butter, "#0077b6",
                     "Butterworth, order %d, %.0f Hz, zero phase"
                     % (ORDER, CUT))):
    ax.plot(t, y, color=col, lw=1.7, label=lab)
ax.annotate("single-frame spike", xy=(t[95], noisy[95]),
            xytext=(t[95] - 1.25, noisy[95] + 0.012), fontsize=9,
            arrowprops=dict(arrowstyle="->", color="0.35", lw=1.0))
ax.annotate("the causal filter arrives late", xy=(t[135], y_oneeuro[135]),
            xytext=(t[152], 0.155), fontsize=9, color="#b5179e",
            arrowprops=dict(arrowstyle="->", color="#b5179e", lw=1.0))
ax.set_ylim(-0.035, 0.44)
ax.set_xlabel("time (s)")
ax.set_ylabel("position (m)")
ax.grid(True, color="0.92", lw=0.5)
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.legend(fontsize=8.6, loc="upper left", frameon=False, ncol=2)
ax.set_title("(a) the four candidates on one constructed test signal, "
             "not recorded data", fontsize=11)

ax = fig.add_subplot(gs[1])
w, h = freqz(b, a, worN=2048, fs=FS)
ax.plot(w, np.abs(h) ** 2, color="#0077b6", lw=1.8,
        label="Butterworth, forward and backward (gain squared)")
sg = savgol_filter(np.eye(101)[50], WIN, POLY)
wg, hg = freqz(sg, 1.0, worN=2048, fs=FS)
ax.plot(wg, np.abs(hg), color="#c1121f", lw=1.8,
        label="Savitzky-Golay, window %d, order %d" % (WIN, POLY))
ax.axvline(CUT, color="0.45", ls="--", lw=1.0)
ax.text(CUT + 0.15, 0.90, "%.0f Hz cutoff" % CUT, fontsize=8.8, color="0.35")
ax.axvspan(0, 5.0, color="#8ecae6", alpha=0.22)
ax.text(0.15, 0.10, "the band that carries\ndeliberate upper-body motion",
        fontsize=8.8, color="0.3", ha="left")
ax.set_xlim(0, FS / 2)
ax.set_ylim(0, 1.08)
ax.set_xlabel("frequency (Hz)")
ax.set_ylabel("gain")
ax.grid(True, color="0.92", lw=0.5)
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.legend(fontsize=8.8, loc="upper right", frameon=False)
ax.set_title("(b) gain against frequency of the two linear candidates, "
             "at the recorded frame rate", fontsize=11)

out = FIG / "appF_fig_filters.png"
plt.savefig(out, dpi=170, bbox_inches="tight")
print("saved", out)
print("spike residue after each filter (m): butter %.4f savgol %.4f "
      "median %.4f oneeuro %.4f"
      % (y_butter[95] - clean[95], y_savgol[95] - clean[95],
         y_median[95] - clean[95], y_oneeuro[95] - clean[95]))

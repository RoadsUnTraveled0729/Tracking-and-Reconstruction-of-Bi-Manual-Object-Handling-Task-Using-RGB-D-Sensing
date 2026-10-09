#!/usr/bin/env python3
"""Chapter 2 signal-filtering result figures (V7 rewrite round).

Three separate figures, one mechanism each, per the supervisor's request
to split the old combined filtering panel into larger labeled figures
and to show the results after filtering:

  ch2_fig_filter_despike.png  the Hampel despike: a raw right-wrist
                              sample deviating by centimetres for one
                              frame, removed and replaced.
  ch2_fig_filter_gap.png      gap bridging: right-wrist samples lost
                              to the visibility gate, bridged by
                              interpolation (short gaps only; long
                              gaps stay empty).
  ch2_fig_filter_smooth.png   the zero-phase Butterworth low-pass:
                              raw jitter against the filtered track.

Data: the R6B rail-recording landmark CSVs (raw and filtered).
Run:  python writing/v7/scripts/make_ch2_filter_figs.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
STEM = "recording_20260831_065553"
raw = pd.read_csv(REPO / "v1" / "mediapipe" / "output" / f"{STEM}_landmarks_raw.csv")
fil = pd.read_csv(REPO / "v1" / "mediapipe" / "output" / f"{STEM}_landmarks_filtered.csv")
OUT = REPO / "writing" / "v7" / "figures"

AX = {"x": "x (m)", "y": "y (m)", "z": "z (m)"}


def series(df, lm, ax):
    return pd.to_numeric(df[f"{lm}_{ax}"], errors="coerce").to_numpy()


def despike_fig():
    lm, lo, hi = "right_wrist", 505, 575
    t = np.arange(lo, hi)
    flags = pd.to_numeric(fil[f"{lm}_flag"], errors="coerce").to_numpy()[lo:hi]
    fig, axes = plt.subplots(3, 1, figsize=(7.6, 6.4), sharex=True)
    for k, axname in enumerate("xyz"):
        a = axes[k]
        rr = series(raw, lm, axname)[lo:hi]
        ff = series(fil, lm, axname)[lo:hi]
        a.plot(t, rr, color="#adb5bd", lw=1.4, label="raw")
        a.plot(t, ff, color="#1d3557", lw=1.8, label="filtered")
        g = flags == 1
        a.plot(t[g], rr[g], "x", color="#c1121f", ms=9, mew=2.2,
               label="flagged spike")
        a.set_ylabel(AX[axname], fontsize=11)
        a.tick_params(labelsize=10)
        a.grid(alpha=0.3)
    axes[0].legend(fontsize=10, loc="upper right")
    axes[0].set_title("Despiking the right wrist: the flagged sample "
                      "deviates for a single frame", fontsize=11)
    axes[-1].set_xlabel("frame", fontsize=11)
    fig.tight_layout()
    out = OUT / "ch2_fig_filter_despike.png"
    fig.savefig(out, dpi=200)
    print("saved", out)


def gap_fig():
    lm, lo, hi = "right_wrist", 600, 700
    t = np.arange(lo, hi)
    flags = pd.to_numeric(fil[f"{lm}_flag"], errors="coerce").to_numpy()[lo:hi]
    fig, axes = plt.subplots(3, 1, figsize=(7.6, 6.4), sharex=True)
    for k, axname in enumerate("xyz"):
        a = axes[k]
        rr = series(raw, lm, axname)[lo:hi]
        ff = series(fil, lm, axname)[lo:hi]
        a.plot(t, rr, color="#adb5bd", lw=1.4, label="raw")
        a.plot(t, ff, color="#1d3557", lw=1.8, label="filtered")
        b = (flags == 1) | (flags == 2)
        a.plot(t[b], ff[b], "o", color="#e76f51", ms=5,
               label="replaced or bridged")
        a.set_ylabel(AX[axname], fontsize=11)
        a.tick_params(labelsize=10)
        a.grid(alpha=0.3)
    axes[0].legend(fontsize=10, loc="upper right")
    axes[0].set_title("Bridging right-wrist dropouts: lost samples are "
                      "interpolated over short gaps", fontsize=11)
    axes[-1].set_xlabel("frame", fontsize=11)
    fig.tight_layout()
    out = OUT / "ch2_fig_filter_gap.png"
    fig.savefig(out, dpi=200)
    print("saved", out)


def smooth_fig():
    lm, lo, hi = "right_wrist", 650, 890
    zoom_lo, zoom_hi = 780, 840
    t = np.arange(lo, hi)
    rr = series(raw, lm, "z")[lo:hi]
    ff = series(fil, lm, "z")[lo:hi]
    fig, (a, b) = plt.subplots(2, 1, figsize=(7.6, 6.0))
    a.plot(t, rr, color="#adb5bd", lw=1.2, label="raw")
    a.plot(t, ff, color="#1d3557", lw=1.8, label="filtered")
    a.axvspan(zoom_lo, zoom_hi, color="#ffd60a", alpha=0.25)
    a.set_ylabel("z (m)", fontsize=11)
    a.set_title("Smoothing the right-wrist depth: raw jitter against "
                "the filtered track", fontsize=11)
    a.legend(fontsize=10, loc="upper right")
    a.grid(alpha=0.3)
    tz = np.arange(zoom_lo, zoom_hi)
    b.plot(tz, series(raw, lm, "z")[zoom_lo:zoom_hi], color="#adb5bd",
           lw=1.4, marker=".", ms=4, label="raw")
    b.plot(tz, series(fil, lm, "z")[zoom_lo:zoom_hi], color="#1d3557",
           lw=1.9, label="filtered")
    b.set_xlabel("frame", fontsize=11)
    b.set_ylabel("z (m)", fontsize=11)
    b.set_title("Enlargement of the shaded window", fontsize=11)
    b.legend(fontsize=10, loc="upper right")
    b.grid(alpha=0.3)
    for axx in (a, b):
        axx.tick_params(labelsize=10)
    fig.tight_layout()
    out = OUT / "ch2_fig_filter_smooth.png"
    fig.savefig(out, dpi=200)
    print("saved", out)


despike_fig()
gap_fig()
smooth_fig()

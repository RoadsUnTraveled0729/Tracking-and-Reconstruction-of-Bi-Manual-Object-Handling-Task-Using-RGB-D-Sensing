#!/usr/bin/env python3
# Filename: mediapipe/filter_landmarks.py
# Glitch filtering stage: *_landmarks_raw.csv -> *_landmarks_filtered.csv.
#
# The raw CSV from extract_landmarks_to_csv.py is never modified — this stage
# reads it and writes a separate filtered CSV, so the strict raw baseline
# stays available for comparison and evaluation.
#
# Three steps, each per landmark, each configurable/disable-able:
#   1. Despike (Hampel): a sample whose deviation from the centered rolling
#      median exceeds max(abs_floor, k * 1.4826 * MAD) on any axis is a glitch
#      and is invalidated. The MAD term adapts the threshold to how fast the
#      landmark is genuinely moving, so fast motion is not flagged.
#   2. Gap fill: NaN runs (missing depth or removed glitches) up to --max-gap
#      frames are linearly interpolated over time; longer runs stay NaN.
#      Leading/trailing runs up to --edge-fill frames are backfilled with the
#      nearest valid sample (warm-up frames can't be interpolated — without
#      this the solver holds rest and SNAPS to the first live pose).
#   3. Smooth — method selectable via --smooth:
#        butter  (default) zero-phase Butterworth low-pass (filtfilt); the
#                biomechanics standard — human upper-body motion is < ~5 Hz,
#                broadband jitter above the cutoff is removed with no lag
#        savgol  Savitzky-Golay polynomial smoothing (mild, preserves peaks)
#        median  rolling median (strong despike, staircases smooth motion)
#        oneeuro causal One-Euro filter (adds lag; the real-time candidate,
#                included for offline preview/comparison)
#        none    despike + gap fill only
#      Zero-phase methods are valid only because this stage is offline.
#
# A per-sample provenance flag is written alongside each landmark:
#   0 = raw sample kept   1 = glitch replaced by interpolation
#   2 = missing, interpolated   3 = missing, left empty
#
# Usage:
#   python filter_landmarks.py                      # newest *_raw.csv in output/
#   python filter_landmarks.py --csv output/x_landmarks_raw.csv --plot

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


def qc_plot(t, raw, filt, flags, out_png):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(len(LANDMARKS), 3, figsize=(15, 2.1 * len(LANDMARKS)),
                             sharex=True, constrained_layout=True)
    for r, name in enumerate(LANDMARKS):
        for c, ax_name in enumerate("xyz"):
            ax = axes[r, c]
            ax.plot(t, raw[name][:, c], color="0.75", lw=1.0, label="raw")
            ax.plot(t, filt[name][:, c], color="#3b6fb6", lw=1.2, label="filtered")
            g = flags[name] == FLAG_GLITCH_INTERP
            if g.any():
                ax.plot(t[g], raw[name][g, c], "x", color="#c25a1e", ms=5,
                        label="glitch removed")
            ax.grid(True, color="0.92", lw=0.5)
            ax.set_axisbelow(True)
            for s in ("top", "right"):
                ax.spines[s].set_visible(False)
            if c == 0:
                ax.set_ylabel(name.replace("_", "\n"), fontsize=8)
            if r == 0:
                ax.set_title(f"{ax_name} (m, camera frame)", fontsize=9)
    axes[0, -1].legend(loc="upper right", fontsize=7, frameon=False)
    axes[-1, 1].set_xlabel("time (s)")
    fig.suptitle("Raw vs filtered landmarks", fontsize=11)
    fig.savefig(out_png, dpi=110)
    plt.close(fig)


def main():
    script_dir = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Filter landmark glitches: raw CSV -> filtered CSV.")
    ap.add_argument("--csv", default=None,
                    help="Raw landmark CSV (default: newest *_landmarks_raw.csv in output/)")
    ap.add_argument("--out", default=None,
                    help="Output CSV (default: <input with _raw -> _filtered>)")
    ap.add_argument("--hampel-window", type=int, default=7, help="Despike window, frames (default 7)")
    ap.add_argument("--hampel-k", type=float, default=3.0, help="MAD multiplier (default 3.0)")
    ap.add_argument("--hampel-floor", type=float, default=0.02,
                    help="Absolute deviation floor in meters below which nothing is flagged (default 0.02)")
    ap.add_argument("--max-gap", type=int, default=5,
                    help="Longest NaN run to interpolate, frames (default 5)")
    ap.add_argument("--edge-fill", type=int, default=0,
                    help="Backfill leading/trailing NaN runs up to this many "
                         "frames with the nearest valid sample (default 0 = off)")
    ap.add_argument("--smooth", choices=["butter", "savgol", "median", "oneeuro", "none"],
                    default="butter", help="Smoothing method (default butter)")
    ap.add_argument("--cutoff-hz", type=float, default=3.0,
                    help="butter: low-pass cutoff in Hz (default 3.0)")
    ap.add_argument("--butter-order", type=int, default=4, help="butter: filter order (default 4)")
    ap.add_argument("--smooth-window", type=int, default=9,
                    help="savgol/median: window in frames, odd (default 9)")
    ap.add_argument("--smooth-polyorder", type=int, default=2, help="savgol: order (default 2)")
    ap.add_argument("--oneeuro-mincutoff", type=float, default=0.05,
                    help="oneeuro: min cutoff Hz (default 0.05, from ENSC498 tuning)")
    ap.add_argument("--oneeuro-beta", type=float, default=1.0,
                    help="oneeuro: speed coefficient (default 1.0, from ENSC498 tuning)")
    ap.add_argument("--no-despike", action="store_true", help="Skip the Hampel step")
    ap.add_argument("--plot", action="store_true", help="Also write a raw-vs-filtered QC PNG")
    args = ap.parse_args()

    if args.csv:
        csv_path = Path(args.csv)
    else:
        candidates = sorted((script_dir / "output").glob("*_landmarks_raw.csv"),
                            key=lambda p: p.stat().st_mtime)
        if not candidates:
            sys.exit("[ERROR] No *_landmarks_raw.csv in output/ — run extract_landmarks_to_csv.py first")
        csv_path = candidates[-1]
    if not csv_path.exists():
        sys.exit(f"[ERROR] CSV not found: {csv_path}")
    if args.out:
        out_csv = Path(args.out)
    elif "_raw" in csv_path.stem:
        out_csv = csv_path.with_name(csv_path.name.replace("_raw", "_filtered"))
    else:
        out_csv = csv_path.with_name(csv_path.stem + "_filtered.csv")

    df = pd.read_csv(csv_path)
    t = df["time_s"].to_numpy()
    fs = 1.0 / float(np.median(np.diff(t))) if len(t) > 1 else 30.0
    print(f"[INFO] {csv_path.name}: {len(df)} frames, fs={fs:.1f} Hz, smooth={args.smooth}")
    out = df.copy()
    raw_by_lm, filt_by_lm, flags_by_lm = {}, {}, {}
    stats = {}

    for name in LANDMARKS:
        cols = [f"{name}_x", f"{name}_y", f"{name}_z"]
        if any(c not in df.columns for c in cols):
            sys.exit(f"[ERROR] CSV lacks columns for {name}")
        pos = df[cols].to_numpy(float)
        flags = np.full(len(pos), FLAG_RAW, dtype=int)
        missing_before = ~np.isfinite(pos).all(axis=1)

        work = pos.copy()
        if not args.no_despike:
            spikes = hampel_mask(work, args.hampel_window, args.hampel_k, args.hampel_floor)
            work[spikes] = np.nan
        else:
            spikes = np.zeros(len(pos), dtype=bool)

        work, filled = fill_gaps(work, t, args.max_gap, args.edge_fill)
        still_missing = ~np.isfinite(work).all(axis=1)
        flags[spikes & filled] = FLAG_GLITCH_INTERP
        flags[missing_before & filled] = FLAG_MISS_INTERP
        flags[still_missing] = FLAG_MISS

        work = smooth_landmark(work, args.smooth, fs, args)

        out[cols] = work
        out[f"{name}_flag"] = flags
        raw_by_lm[name], filt_by_lm[name], flags_by_lm[name] = pos, work, flags
        rms = float(np.sqrt(np.nanmean(np.sum((work - pos) ** 2, axis=1))))
        stats[name] = {"glitches_removed": int(spikes.sum()),
                       "missing_interpolated": int((missing_before & filled).sum()),
                       "left_empty": int(still_missing.sum()),
                       "rms_correction_mm": round(rms * 1000, 2)}
        # Split the missing cells by the extractor's reason code when present
        # (occlusion vs depth hole; _src carries through out = df.copy()).
        src_col = f"{name}_src"
        if src_col in df.columns:
            src = pd.to_numeric(df[src_col], errors="coerce").to_numpy()
            stats[name]["missing_low_vis"] = int((missing_before & (src == 1)).sum())
            stats[name]["missing_no_depth"] = int((missing_before & (src == 2)).sum())
        print(f"  {name:15s} glitches={spikes.sum():3d}  filled={(missing_before & filled).sum():3d}  "
              f"empty={still_missing.sum():3d}  rms correction={rms*1000:5.1f} mm")

    out.to_csv(out_csv, index=False, float_format="%.6f")
    meta = {
        "source_csv": str(csv_path),
        "output_csv": str(out_csv),
        "params": {"hampel_window": args.hampel_window, "hampel_k": args.hampel_k,
                   "hampel_floor_m": args.hampel_floor, "max_gap": args.max_gap,
                   "edge_fill": args.edge_fill,
                   "despike": not args.no_despike, "smooth": args.smooth,
                   "cutoff_hz": args.cutoff_hz, "butter_order": args.butter_order,
                   "smooth_window": args.smooth_window, "smooth_polyorder": args.smooth_polyorder,
                   "oneeuro_mincutoff": args.oneeuro_mincutoff, "oneeuro_beta": args.oneeuro_beta,
                   "fs_hz": round(fs, 3)},
        "flag_legend": {"0": "raw", "1": "glitch interpolated", "2": "missing interpolated",
                        "3": "missing"},
        "src_legend": {"0": "ok", "1": "low_vis (blocked)", "2": "no_depth",
                       "note": "per-landmark {name}_src from the extractor, "
                               "carried through unchanged"},
        "stats": stats,
        "export_time": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    meta_path = out_csv.with_suffix(".meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"[+] CSV:  {out_csv}\n[+] Meta: {meta_path}")

    if args.plot:
        png = out_csv.with_suffix(".qc.png")
        qc_plot(t, raw_by_lm, filt_by_lm, flags_by_lm, png)
        print(f"[+] QC plot: {png}")


if __name__ == "__main__":
    main()

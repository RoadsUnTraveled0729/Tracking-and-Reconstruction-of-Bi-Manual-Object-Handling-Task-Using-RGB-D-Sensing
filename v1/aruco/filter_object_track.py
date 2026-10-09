#!/usr/bin/env python3
# Filename: aruco/filter_object_track.py
"""Object-track filtering stage: *_object_world.csv -> *_object_world_filtered.csv.

The raw per-frame PnP track is never modified — this stage reads it and
writes a separate filtered CSV, mirroring the Pipeline A landmark filter's
philosophy (raw stays available as the strict baseline). Pipeline B owns its
own implementation (no code shared with mediapipe/ — pipeline independence).

Steps, all in the WORLD (desk) frame:
  1. Despike (Hampel) on position: deviation from the centered rolling
     median beyond max(abs_floor, k*1.4826*MAD) on any axis -> invalidated.
  2. Gap bridge: undetected/despiked runs up to --max-gap frames are
     interpolated — position linearly over time, rotation along the
     geodesic (axis-angle of RaᵀRb, matrices only — no quaternions per
     project policy). Leading/trailing runs hold the nearest valid pose
     (can't interpolate past the data), keeping `detected=0`.
  3. Smooth: position with a Savitzky-Golay polynomial (frame-to-frame
     polynomial fit, zero-phase, offline-only); rotation with a centered
     rolling chordal mean (SVD projection back to SO(3), frames.py).

The `detected` column keeps the ORIGINAL detection flag: a bridged frame
carries a usable interpolated pose but is still marked 0 so downstream
consumers (red tint in Unity) stay honest. Consumers should apply the pose
columns on every frame and use `detected` only as the live/inferred flag.
Unity columns (unity_p*, unity_e*) are re-derived from the filtered world
pose with the same frames.py mapping as the raw exporter.

Usage:
  python filter_object_track.py                 # newest *_object_world.csv
  python filter_object_track.py --csv output/x_object_world.csv --plot
"""
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


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Filter the object world track.")
    ap.add_argument("--csv", default=None,
                    help="Object world CSV (default: newest *_object_world.csv in output/)")
    ap.add_argument("--out", default=None,
                    help="Output CSV (default: <input>_filtered.csv)")
    ap.add_argument("--hampel-window", type=int, default=7)
    ap.add_argument("--hampel-k", type=float, default=3.0)
    ap.add_argument("--hampel-floor", type=float, default=0.02,
                    help="Absolute spike floor in meters (default 0.02)")
    ap.add_argument("--max-gap", type=int, default=8,
                    help="Longest undetected run to bridge, frames (default 8)")
    ap.add_argument("--smooth-window", type=int, default=9,
                    help="Savitzky-Golay window, odd frames (default 9)")
    ap.add_argument("--smooth-polyorder", type=int, default=2)
    ap.add_argument("--rot-window", type=int, default=5,
                    help="Rotation rolling chordal-mean window, odd (default 5)")
    ap.add_argument("--plot", action="store_true", help="Write a raw-vs-filtered QC PNG")
    args = ap.parse_args()

    if args.csv:
        csv_path = Path(args.csv)
    else:
        cands = sorted(here.glob("output/*_object_world.csv"),
                       key=lambda p: p.stat().st_mtime)
        if not cands:
            sys.exit("[ERROR] no *_object_world.csv in output/")
        csv_path = cands[-1]
    out_csv = Path(args.out) if args.out else \
        csv_path.with_name(csv_path.stem + "_filtered.csv")

    df = pd.read_csv(csv_path)
    n = len(df)
    t = df["time_s"].to_numpy(float)
    det = df["detected"].to_numpy(int) == 1
    pos = df[["tx", "ty", "tz"]].to_numpy(float)
    Rs = df[R_COLS].to_numpy(float).reshape(n, 3, 3)
    pos[~det] = np.nan
    print(f"[INFO] {csv_path.name}: {n} frames, {int(det.sum())} detected")

    # 1. despike positions (rotation rides along: a spiked PnP solve is
    # wrong as a whole, so its rotation is dropped with it)
    spikes = hampel_mask(pos, args.hampel_window, args.hampel_k, args.hampel_floor)
    valid = det & ~spikes
    pos[spikes] = np.nan
    print(f"[INFO] despike: {int(spikes.sum())} frames invalidated")

    # 2. bridge gaps
    filled = np.zeros(n, dtype=bool)
    missing = ~valid
    vidx = np.flatnonzero(valid)
    if len(vidx) < 2:
        sys.exit("[ERROR] fewer than 2 valid frames")
    for start, stop in nan_runs(missing):
        run = stop - start
        interior = start > vidx[0] and stop <= vidx[-1]
        if interior and run <= args.max_gap:
            a, b = start - 1, stop            # nearest valid neighbors
            for i in range(start, stop):
                s = (t[i] - t[a]) / (t[b] - t[a])
                pos[i] = (1 - s) * pos[a] + s * pos[b]
                Rs[i] = geodesic_interp(Rs[a], Rs[b], s)
            filled[start:stop] = True
        else:
            # boundary run: hold the first/last valid pose of the track.
            # interior run longer than max_gap: hold the previous valid
            # pose (E-022, 2026-08-28; before this the run was held at
            # the LAST valid pose of the whole recording, which dragged
            # the smoothed neighbours toward an unrelated position)
            if start == 0:
                src = vidx[0]
            elif not interior:
                src = vidx[-1]
            else:
                src = start - 1
            pos[start:stop] = pos[src]
            Rs[start:stop] = Rs[src]

    # 3a. smooth position: Savitzky-Golay per axis (single gap-free track now)
    smoothed = pos.copy()
    if n >= args.smooth_window:
        for ax in range(3):
            smoothed[:, ax] = savgol_filter(pos[:, ax], args.smooth_window,
                                            args.smooth_polyorder)
    # 3b. smooth rotation: centered rolling chordal mean
    Rsm = Rs.copy()
    h = args.rot_window // 2
    for i in range(n):
        lo, hi = max(0, i - h), min(n, i + h + 1)
        Rsm[i] = chordal_mean(Rs[lo:hi])

    # honesty check: smoothing must not move MEASURED frames materially
    dev = np.linalg.norm(smoothed[valid] - df[["tx", "ty", "tz"]].to_numpy(float)[valid],
                         axis=1)
    rdev = np.array([geodesic_deg(Rsm[i], Rs[i]) for i in np.flatnonzero(valid)])
    print(f"[INFO] smoothing deviation on measured frames: pos median "
          f"{np.median(dev)*1000:.1f} mm / max {dev.max()*1000:.1f} mm, "
          f"rot median {np.median(rdev):.2f} deg / max {rdev.max():.2f} deg")

    # frame-to-frame step improvement
    step_raw = np.linalg.norm(np.diff(df[["tx", "ty", "tz"]].to_numpy(float), axis=0), axis=1)
    step_f = np.linalg.norm(np.diff(smoothed, axis=0), axis=1)
    both = det[1:] & det[:-1]
    print(f"[INFO] frame-to-frame step p95: raw {np.percentile(step_raw[both], 95)*1000:.1f} mm "
          f"-> filtered {np.percentile(step_f[both], 95)*1000:.1f} mm")

    out = df.copy()
    out[["tx", "ty", "tz"]] = smoothed
    out[R_COLS] = Rsm.reshape(n, 9)
    pu = np.zeros((n, 3))
    eu = np.zeros((n, 3))
    for i in range(n):
        p_u, R_u = unity_from_world(Rsm[i], smoothed[i])
        pu[i] = p_u
        eu[i] = euler_unity_zxy(R_u)
    out[["unity_px", "unity_py", "unity_pz"]] = pu
    out[["unity_ex", "unity_ey", "unity_ez"]] = eu
    out["filled"] = filled.astype(int)   # bridged (interpolated) frames
    out.to_csv(out_csv, index=False, float_format="%.9f")

    meta = {
        "source_csv": str(csv_path),
        "output_csv": str(out_csv),
        "params": {k: getattr(args, k.replace("-", "_")) for k in
                   ("hampel_window", "hampel_k", "hampel_floor", "max_gap",
                    "smooth_window", "smooth_polyorder", "rot_window")},
        "frames": n,
        "detected": int(det.sum()),
        "despiked": int(spikes.sum()),
        "bridged": int(filled.sum()),
        "held_boundary": int((~valid & ~filled).sum()),
        "smooth_dev_pos_mm": {"median": round(float(np.median(dev)) * 1000, 2),
                              "max": round(float(dev.max()) * 1000, 2)},
        "smooth_dev_rot_deg": {"median": round(float(np.median(rdev)), 3),
                               "max": round(float(rdev.max()), 3)},
        "export_time": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    meta_path = out_csv.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2))
    print(f"[+] CSV:  {out_csv}\n[+] Meta: {meta_path}")

    if args.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        raw_u = df[["unity_px", "unity_py", "unity_pz"]].to_numpy(float)
        fig, axes = plt.subplots(4, 1, figsize=(13, 10), sharex=True,
                                 constrained_layout=True)
        for c, name in enumerate(["x (right)", "y (up)", "z (fwd)"]):
            ax = axes[c]
            r = np.where(det, raw_u[:, c], np.nan)
            ax.plot(t, r, color="0.75", lw=1.0, label="raw (detected)")
            ax.plot(t, pu[:, c], color="#3b6fb6", lw=1.2, label="filtered")
            if filled.any():
                ax.plot(t[filled], pu[filled, c], ".", color="#c25a1e", ms=4,
                        label="bridged gap")
            ax.set_ylabel(f"unity {name} (m)", fontsize=9)
            ax.grid(True, color="0.92", lw=0.5)
            ax.set_axisbelow(True)
            for s in ("top", "right"):
                ax.spines[s].set_visible(False)
        axes[0].legend(loc="best", fontsize=8, frameon=False)
        ax = axes[3]
        ax.plot(t[1:], np.where(both, step_raw, np.nan) * 1000, color="0.75",
                lw=1.0, label="raw step")
        ax.plot(t[1:], step_f * 1000, color="#3b6fb6", lw=1.2, label="filtered step")
        ax.set_ylabel("frame step (mm)", fontsize=9)
        ax.set_xlabel("time (s)")
        ax.grid(True, color="0.92", lw=0.5)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.legend(loc="best", fontsize=8, frameon=False)
        fig.suptitle(f"{csv_path.stem}: raw vs filtered object track", fontsize=11)
        png = out_csv.with_suffix(".qc.png")
        fig.savefig(png, dpi=110)
        print(f"[+] QC plot: {png}")


if __name__ == "__main__":
    main()

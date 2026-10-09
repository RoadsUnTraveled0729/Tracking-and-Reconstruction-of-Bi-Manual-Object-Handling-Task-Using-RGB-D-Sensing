#!/usr/bin/env python3
"""Per-angle offset table: V3 (RTMPose/COCO) vs v1 (MediaPipe/
BlazePose) on the same recording (V3_PLAN.md risks: the COCO wrist is
the wrist crease, BlazePose's is the wrist joint -- the twist and
elbow angle definitions shift with it; measure, never assume).

Method: solve BOTH raw extractions frame-by-frame through the SAME
vendored ChainFallbackSolver (camera frame -> Unity flip -> solve,
stateful, causal; no smoothing on either side so the comparison is
definitional, not filter-dependent). For each of the 13 angles,
statistics of wrap_deg(V3 - v1) over frames where the angle's group
is LIVE in both solves: circular mean (the offset), circular std, and
p95 |deviation from the mean|.

Run: /home/luo/anaconda3/bin/python v3/bench/v1_offset_table.py
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

V3_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V3_ROOT.parent
sys.path.insert(0, str(V3_ROOT))
VENDOR = V3_ROOT / "vendor" / "v1"
if str(VENDOR) not in sys.path:
    sys.path.insert(0, str(VENDOR))

from occlusion import (BIT_NAMES, ChainFallbackSolver,   # noqa: E402 vendored
                       LANDMARKS)
from bench.metrics import ANGLE_NAMES, GROUP_ANGLES, wrap_deg  # noqa: E402

SENSOR_TO_UNITY = np.array([1.0, -1.0, 1.0])

# angle index -> owning group bit index (inverse of GROUP_ANGLES)
ANGLE_GROUP = np.empty(len(ANGLE_NAMES), dtype=int)
for g, idxs in enumerate(GROUP_ANGLES):
    for i in idxs:
        ANGLE_GROUP[i] = g


def solve_csv(df):
    """Causal stateful solve of a raw extraction CSV. Returns
    (frames (N,), angles (N, 13), masks (N,))."""
    solver = ChainFallbackSolver()
    frames, angles, masks = [], [], []
    for _, row in df.iterrows():
        pts = {}
        for name in LANDMARKS:
            v = np.array([row.get(f"{name}_x", np.nan),
                          row.get(f"{name}_y", np.nan),
                          row.get(f"{name}_z", np.nan)], dtype=float)
            pts[name] = None if np.any(np.isnan(v)) else v * SENSOR_TO_UNITY
        a, m = solver.solve(pts)
        frames.append(int(row["frame"]))
        angles.append(a)
        masks.append(m)
    return (np.asarray(frames), np.asarray(angles),
            np.asarray(masks, dtype=int))


def circ_mean_deg(d):
    r = np.radians(d)
    return float(np.degrees(np.arctan2(np.sin(r).mean(), np.cos(r).mean())))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--v1-csv", default=str(
        REPO_ROOT / "v1/kinematics/dataset/real_20260224/"
                    "recording_20260224_083945_landmarks_raw.csv"))
    ap.add_argument("--v3-csv", default=str(
        V3_ROOT / "output/extraction_recording_20260224_083945.csv"))
    args = ap.parse_args()

    f1, a1, m1 = solve_csv(pd.read_csv(args.v1_csv))
    f3, a3, m3 = solve_csv(pd.read_csv(args.v3_csv))
    common, i1, i3 = np.intersect1d(f1, f3, return_indices=True)
    a1, m1 = a1[i1], m1[i1]
    a3, m3 = a3[i3], m3[i3]
    print(f"v1: {args.v1_csv}")
    print(f"v3: {args.v3_csv}")
    print(f"common frames: {len(common)} "
          f"(v1 {len(f1)}, v3 {len(f3)}); no smoothing on either side; "
          "vendored ChainFallbackSolver both sides")

    print(f"\n{'angle':>11} {'group':>8} {'n':>4} {'offset':>8} "
          f"{'cstd':>7} {'p95dev':>7}")
    for j, name in enumerate(ANGLE_NAMES):
        g = ANGLE_GROUP[j]
        live = ((m1 >> g) & 1).astype(bool) & ((m3 >> g) & 1).astype(bool)
        d = wrap_deg(a3[live, j] - a1[live, j])
        mu = circ_mean_deg(d)
        dev = np.abs(wrap_deg(d - mu))
        cstd = float(np.sqrt(np.mean(dev ** 2)))
        print(f"{name:>11} {BIT_NAMES[g]:>8} {live.sum():>4} "
              f"{mu:>8.2f} {cstd:>7.2f} {np.percentile(dev, 95):>7.2f}")
    print("\nNOTE: 'offset' is the definitional bias to subtract before "
          "quoting any V3-vs-v1 angle comparison; large cstd means the "
          "two detectors disagree beyond a constant shift for that "
          "angle. v1's calibrated grip offset is never reused (plan "
          "risk).")


if __name__ == "__main__":
    main()

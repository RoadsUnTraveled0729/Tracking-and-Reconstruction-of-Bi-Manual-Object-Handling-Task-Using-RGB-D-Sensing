"""One-pass cleaning filter for the object track (E-019).

Around handovers the marker is undetected for a run of frames. The
track filter holds the previous valid pose across an over-long run
(E-022; before that fix it held the last valid pose of the whole
recording, which made the smoothed neighbours swing tens of
centimetres). This script is the single guard behind the filter: it
blanks any detected sample whose step from its predecessor is not
physically possible. On R5 after E-022 it blanks none. Everything
downstream (Unity sender, recovery, analysis)
just reads a clean track and no consumer needs marker-robustness
logic of its own - the marker side stays simple, the engineering
focus stays on the rig (user direction 2026-08-26).

Rule, physical and recording-independent: keep a sample only if it
is detected, finite, and moves from the LAST KEPT sample at no more
than V_MAX (translation) and W_MAX (rotation) - rates, so a real gap
allows proportionally more travel. Everything else has its pose
blanked and detected cleared; consumers already hold the last pose
on blank rows with the live flag off.

Bounds, from the clean data of two recordings:
  V_MAX 1.0 m/s   (clean maxima: R1 0.26, R5 0.41 m/s)
  W_MAX 400 deg/s (clean maxima: R1 82, R5 179 deg/s)
Zero rows are removed on R1; on R5 only the handover corruption goes.

Run: python eval/common/clean_object_track.py [--stem STEM]
Writes <filtered track>_clean.csv next to the input; the paths
accessor prefers it once it exists.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "offset"))
import paths  # noqa: E402
import carry  # noqa: E402

V_MAX = 1.0        # m/s
W_MAX_DEG = 400.0  # deg/s
POSE_COLS = ["unity_px", "unity_py", "unity_pz",
             "unity_ex", "unity_ey", "unity_ez"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R5_STEM)
    args = ap.parse_args()

    src = paths.object_world_filtered(args.stem)
    if src.name.endswith("_clean.csv"):
        src = Path(str(src)[:-len("_clean.csv")] + ".csv")
    df = pd.read_csv(src)
    pos = df[["unity_px", "unity_py", "unity_pz"]].to_numpy()
    R = np.array([carry.recompose_zxy(e) for e in
                  df[["unity_ex", "unity_ey", "unity_ez"]].to_numpy()])
    t = df["time_s"].to_numpy()
    det = df["detected"].to_numpy() == 1

    n = len(df)
    keep = np.zeros(n, bool)
    last = None
    for i in range(n):
        if not det[i] or not np.isfinite(pos[i]).all():
            continue
        if last is None:
            keep[i] = True
            last = i
            continue
        dt = float(t[i] - t[last])
        if dt <= 0:
            continue
        v = float(np.linalg.norm(pos[i] - pos[last])) / dt
        cosang = (np.trace(R[last].T @ R[i]) - 1.0) / 2.0
        w = float(np.degrees(np.arccos(
            np.clip(cosang, -1.0, 1.0)))) / dt
        if v <= V_MAX and w <= W_MAX_DEG:
            keep[i] = True
            last = i

    out = df.copy()
    out.loc[~keep, POSE_COLS] = np.nan
    out.loc[~keep, "detected"] = 0
    dst = src.with_name(src.stem + "_clean.csv")
    out.to_csv(dst, index=False, float_format="%.6f")
    dropped = int((det & ~keep).sum())
    blanked = int((~keep).sum())
    print(f"[+] {dst}")
    print(f"    kept {int(keep.sum())}/{n} rows; rejected {dropped} "
          f"detected-but-implausible, blanked {blanked - dropped} "
          "undetected rows the filter had smoothed over")


if __name__ == "__main__":
    main()

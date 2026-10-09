"""Marker-size scale correction for R4 (eval/DECISIONS.md E-009).

APPLIED FACTORS come from eval/common/marker_size.py - the single
traceable source of the 45 mm black-square assumption (user-set
2026-08-25). For a planar square, the PnP translation scales exactly
linearly with the declared size, so the correction is an exact
post-hoc rescale of each marker's translation by
(assumed / declared). Rotations, pixel coordinates, and reprojection
errors are unaffected. The depth-derived PnP/depth ratios are still
computed and stored as diagnostics (they measured ~1.145, implying
~43.6 mm; the drawn-path spans support ~44-45).

Writes:
  eval/reports/r4_marker_scale.json      (the fitted factors + spread)
  eval/output/<stem>_aruco_raw_scaled.csv (corrected copy)
  eval/output/<stem>_aruco_raw_scaled.meta.json

The factors are UNCERTAIN until the physical prints are measured with
a ruler; the JSON records the implied sizes to check against.

Run: python eval/gt/scale_correction.py [--stem STEM]
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "common"))
import marker_size
import paths

DECLARED = marker_size.DECLARED_M


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R4_STEM)
    args = ap.parse_args()
    stem = args.stem
    alias = paths.ALIAS[stem]
    df = pd.read_csv(paths.ARUCO_OUT / f"{stem}_aruco_raw.csv")
    report = {"stem": stem, "reference": "depth-median z (metric)",
              "markers": {}}
    out = df.copy()
    for mid, decl in DECLARED.items():
        det = df[f"m{mid}_detected"] == 1
        tz = df.loc[det, f"m{mid}_tz"].to_numpy()
        dz = df.loc[det, f"m{mid}_depth_z"].to_numpy()
        ok = np.isfinite(dz) & (dz > 0)
        ratio = tz[ok] / dz[ok]
        med = float(np.median(ratio))
        scale = marker_size.SCALE[mid]
        report["markers"][str(mid)] = {
            "declared_mm": decl * 1000,
            "assumed_black_square_mm":
                marker_size.ASSUMED_BLACK_SQUARE_M[mid] * 1000,
            "scale_applied": round(scale, 4),
            "scale_source": "eval/common/marker_size.py (USER "
                            "ASSUMPTION 45 mm, E-009)",
            "diag_ratio_median": round(med, 4),
            "diag_ratio_p5": round(float(np.percentile(ratio, 5)), 4),
            "diag_ratio_p95": round(float(np.percentile(ratio, 95)), 4),
            "diag_depth_implied_mm": round(decl / med * 1000, 1),
            "n": int(ok.sum()),
        }
        for ax in ("tx", "ty", "tz"):
            out[f"m{mid}_{ax}"] = df[f"m{mid}_{ax}"] * scale
        print(f"  id{mid}: scale {scale:.4f} (assumed "
              f"{marker_size.ASSUMED_BLACK_SQUARE_M[mid]*1000:.0f} mm / "
              f"declared {decl * 1000:.0f}; depth diagnostic implies "
              f"{decl / med * 1000:.1f} mm)")

    paths.EVAL_OUT.mkdir(parents=True, exist_ok=True)
    out_csv = paths.EVAL_OUT / f"{stem}_aruco_raw_scaled.csv"
    out.to_csv(out_csv, index=False, float_format="%.6f")

    meta_in = paths.ARUCO_OUT / f"{stem}_aruco_raw.meta.json"
    meta = json.loads(meta_in.read_text())
    meta["scale_correction"] = report["markers"]
    meta["scale_correction_note"] = (
        "translations rescaled per marker by ASSUMED black-square "
        "sizes from eval/common/marker_size.py (45 mm user assumption, "
        "E-009); tabletop block is depth-based and unchanged")
    (paths.EVAL_OUT / f"{stem}_aruco_raw_scaled.meta.json").write_text(
        json.dumps(meta, indent=1))

    paths.EVAL_REPORTS.mkdir(parents=True, exist_ok=True)
    report_json = paths.EVAL_REPORTS / f"{alias}_marker_scale.json"
    report_json.write_text(json.dumps(report, indent=1))
    print(f"[+] {out_csv}")
    print(f"[+] {report_json}")


if __name__ == "__main__":
    main()

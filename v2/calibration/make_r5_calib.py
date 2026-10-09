#!/usr/bin/env python3
# Filename: v2/calibration/make_r5_calib.py
"""Build the v2 live calibration for R5 from the frozen eval calibration.

Why a separate file: eval/output/scene_calibration_r5c.json was produced
by calibrate_scene.py from the SCALE-CORRECTED ArUco track (the printed
black squares are 45 mm, not the 50 mm the extractor declared -- E-009,
eval/common/marker_size.py), so every transform in it is true-scale, but
its markers table still records the DECLARED 50 mm sizes. The v2 object
worker (v2/object/v2_object.py) feeds markers["1"].size_m straight into
PnP on live frames; with 0.050 the live translations would come out
~11 percent long against the true-scale desk anchor. This script writes
a copy whose marker sizes are the TRUE printed sizes, so live PnP is
consistent with the calibrated transforms at the source -- one clean
calibration file, no scale layer in the live path.

Sensor-round note (checklist, not implemented here): a live-camera
session that recalibrates via v2/calibration/live_calibrate.py must be
given the same true marker sizes, or the markers must be reprinted at
their declared size and measured.

Usage:
    python v2/calibration/make_r5_calib.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "eval" / "common"))

from marker_size import ASSUMED_BLACK_SQUARE_M  # noqa: E402

SRC = ROOT / "eval" / "output" / "scene_calibration_r5c.json"
OUT = ROOT / "v2" / "output" / "scene_calibration_r5_v2.json"


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--alias", default="r5",
                    help="calibration alias: reads eval/output/"
                         "scene_calibration_<alias>c.json, writes v2/output/"
                         "scene_calibration_<alias>_v2.json (default r5)")
    args = ap.parse_args()
    src = ROOT / "eval" / "output" / f"scene_calibration_{args.alias}c.json"
    out = ROOT / "v2" / "output" / f"scene_calibration_{args.alias}_v2.json"
    calib = json.loads(src.read_text())
    changed = []
    for mid, blk in calib["markers"].items():
        true_m = ASSUMED_BLACK_SQUARE_M[int(mid)]
        if abs(blk["size_m"] - true_m) > 1e-9:
            changed.append(f"id{mid} {blk['size_m']*1000:.0f}->"
                           f"{true_m*1000:.0f} mm")
            blk["size_m"] = true_m
    calib["v2_note"] = (
        "marker sizes replaced with the TRUE printed sizes "
        "(eval/common/marker_size.py, E-009) so live PnP matches the "
        "scale-corrected transforms; source: " + str(src.name))
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(calib, indent=1))
    print(f"[+] {out}")
    print(f"    sizes corrected: {', '.join(changed) if changed else 'none'}")


if __name__ == "__main__":
    main()

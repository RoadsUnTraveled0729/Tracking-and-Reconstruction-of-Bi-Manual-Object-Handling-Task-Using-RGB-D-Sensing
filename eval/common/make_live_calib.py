#!/usr/bin/env python3
"""Derive the live-pipeline calibration from the scale-corrected R4
calibration.

v2/object/v2_object.py takes the object marker size for its live PnP
from the calib json's markers block (v2_object.py:60). The
scale-corrected calibration eval/output/scene_calibration_r4c.json has
45 mm-consistent T matrices (USER ASSUMPTION, eval/common/
marker_size.py) but still carries the DECLARED 50 mm sizes in its
markers block, so a live run mixing the two would place the object at
50/45 scale against a 45-scale scene. This script writes a copy whose
markers block carries the ASSUMED sizes, making the whole live chain
45 mm-consistent.

Usage:
  python eval/common/make_live_calib.py
  -> eval/output/scene_calibration_r4c_live.json
"""
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from marker_size import ASSUMED_BLACK_SQUARE_M  # noqa: E402

ROOT = HERE.parents[1]
SRC = ROOT / "eval/output/scene_calibration_r4c.json"
DST = ROOT / "eval/output/scene_calibration_r4c_live.json"


def main():
    calib = json.loads(SRC.read_text())
    for mid, size in ASSUMED_BLACK_SQUARE_M.items():
        if str(mid) in calib["markers"]:
            calib["markers"][str(mid)]["size_m"] = size
    calib["live_calib_note"] = (
        "markers sizes set to ASSUMED_BLACK_SQUARE_M "
        "(eval/common/marker_size.py, USER ASSUMPTION 45 mm) so the "
        "live v2 object PnP matches the scale-corrected T matrices; "
        "derived by eval/common/make_live_calib.py from "
        + SRC.name)
    DST.write_text(json.dumps(calib, indent=1))
    print(f"[+] {DST}")
    for mid, blk in calib["markers"].items():
        print(f"    marker {mid} ({blk['role']}): size_m {blk['size_m']}")


if __name__ == "__main__":
    main()

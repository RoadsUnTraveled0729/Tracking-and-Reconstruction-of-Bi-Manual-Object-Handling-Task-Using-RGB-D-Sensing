#!/usr/bin/env python3
"""Rig sizing check for a Unity capture (eval/unity_check/, E-036).

IntegratedSceneReceiver sizes the avatar for the recording replayed from
the side-channel file the launcher writes (/tmp/r5_rig_sizing, built from
eval/reports/<alias>_rig_sizing.json) and, at Play start, dumps the
segment lengths it measured on the scaled rig (rig_dimensions.csv) next
to a note of what it was asked for (rig_sizing_used.txt). This answers,
in numbers, "was this capture's rig sized from the intended recording":

  1. every requested length is found in the measured rig to 1e-3 m: rows
     upper_arm_R, upper_arm_L, forearm_R, forearm_L and
     torso_hip_to_midshoulder against segment_lengths_m of the json;
  2. when --used is given, the note names the sizing file as its source
     (an unsized capture writes "none"), carries the stem of the json
     when the json states one, and repeats the requested lengths.

Usage:
  python eval/unity_check/check_rig_sizing.py \
      --sizing eval/reports/r7_rig_sizing.json \
      --rig-dimensions eval/output/unity_check_r7/rig_dimensions.csv \
      --used eval/output/unity_check_r7/rig_sizing_used.txt
"""
import argparse
import json
import sys
from pathlib import Path

TOL_M = 1e-3
# sizing json key -> row of rig_dimensions.csv (DumpRigDimensions)
ROWS = {"upper_arm_R": "upper_arm_R", "upper_arm_L": "upper_arm_L",
        "forearm_R": "forearm_R", "forearm_L": "forearm_L",
        "torso": "torso_hip_to_midshoulder"}
SIZING_FLAG = "/tmp/defense_axes_capture/r5_rig_sizing"   # IntegratedSceneReceiver.SizingOverridePath

npass = nfail = 0


def check(name, ok, detail=""):
    global npass, nfail
    npass += bool(ok)
    nfail += not ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}"
          + (f" - {detail}" if detail else ""))


def read_rig(path):
    """rig_dimensions.csv (segment,meters) as {segment: float}."""
    rows = {}
    with open(path) as f:
        header = f.readline().strip()
        if header != "segment,meters":
            sys.exit(f"FAIL: {path} does not start with 'segment,meters' "
                     f"(got {header!r})")
        for line in f:
            line = line.strip()
            if not line:
                continue
            seg, val = line.split(",", 1)
            rows[seg] = float(val)
    return rows


def read_used(path):
    """rig_sizing_used.txt (key=value lines) as {key: str}."""
    kv = {}
    for line in Path(path).read_text().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()
    return kv


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sizing", required=True,
                    help="eval/reports/<alias>_rig_sizing.json of the "
                         "recording the capture replayed")
    ap.add_argument("--rig-dimensions", required=True,
                    help="rig_dimensions.csv the receiver wrote for the "
                         "capture")
    ap.add_argument("--used", default=None,
                    help="rig_sizing_used.txt written next to it")
    args = ap.parse_args()

    sizing = json.loads(Path(args.sizing).read_text())
    want = sizing.get("segment_lengths_m")
    if not isinstance(want, dict):
        sys.exit(f"FAIL: {args.sizing} carries no segment_lengths_m")
    rig = read_rig(args.rig_dimensions)
    print(f"sizing         {args.sizing}")
    print(f"rig dimensions {args.rig_dimensions}")
    if args.used:
        print(f"sizing note    {args.used}")

    for key, row in ROWS.items():
        if key not in want:
            check(f"{row}: sizing json carries {key}", False, "key missing")
            continue
        if row not in rig:
            check(f"{row}: rig_dimensions.csv carries the row", False,
                  "row missing")
            continue
        req = float(want[key])
        d = rig[row] - req
        check(f"{row} measured on the scaled rig equals the sizing json "
              f"within {TOL_M * 1000:.0f} mm", abs(d) < TOL_M,
              f"rig {rig[row]:.4f} m vs sizing {req:.4f} m "
              f"(diff {d * 1000:+.2f} mm)")

    if args.used:
        used = read_used(args.used)
        src = used.get("source", "")
        check("rig_sizing_used.txt names the sizing file as its source",
              src == SIZING_FLAG, f"source={src or '(absent)'}")
        stem = sizing.get("stem")
        if stem is None:
            print("       (sizing json states no stem; stem check skipped)")
        else:
            check("rig_sizing_used.txt carries the stem of the sizing json",
                  used.get("stem") == stem,
                  f"note stem={used.get('stem', '(absent)')} vs json {stem}")
        for key in ROWS:
            k = f"requested_{key}"
            try:
                v = float(used[k])
            except (KeyError, ValueError):
                v = None
            ok = (v is not None and key in want
                  and abs(v - float(want[key])) < TOL_M)
            check(f"{k} equals the sizing json", ok,
                  f"note {used.get(k, '(absent)')} vs json {want.get(key)}")

    print(f"\n=== {npass} passed, {nfail} failed ===")
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()

"""Build synthetic-occlusion datasets by masking landmarks of a VERIFIED
real recording (KINEMATIC_MODEL.md §10 validation).

Ground truth for every scenario is the unmasked solve of the same CSV, so
hold error and recovery are exactly measurable. Each scenario blanks the
xyz cells of chosen landmarks over chosen frame windows; everything else
is byte-identical to the base CSV.

Scenarios (window frames are inside the fully-live region of the base):
  wrist_short  raw CSV, R wrist frames 300-302 (3)  -> filter repairs it
  wrist_long   filtered, R wrist 400-444 (45)       -> R twist+elbow hold
  elbow_long   filtered, R elbow 500-544 (45)       -> whole R arm holds
  hip          filtered, L hip 600-629 (30)         -> root holds, arms live
  root_ref     filtered, R shoulder 750-779 (30)    -> root live via L
                                                       shoulder, R arm holds
  pose_loss    filtered, ALL landmarks 700-709 (10) -> everything holds

Run: python make_masked_dataset.py [--base <filtered_csv>] [--raw <raw_csv>]
Outputs masked CSVs + scenarios.json manifest into output/occlusion/.
"""
import argparse
import json
from pathlib import Path

import pandas as pd

ALL = ["left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
       "left_wrist", "right_wrist", "left_hip", "right_hip"]

SCENARIOS = [
    # name, source, landmarks, start, stop (exclusive)
    ("wrist_short", "raw", ["right_wrist"], 300, 303),
    ("wrist_long", "filtered", ["right_wrist"], 400, 445),
    ("elbow_long", "filtered", ["right_elbow"], 500, 545),
    ("hip", "filtered", ["left_hip"], 600, 630),
    ("root_ref", "filtered", ["right_shoulder"], 750, 780),
    ("pose_loss", "filtered", ALL, 700, 710),
]


def mask(df, landmarks, start, stop):
    out = df.copy()
    rows = (out["frame"] >= start) & (out["frame"] < stop)
    for name in landmarks:
        out.loc[rows, [f"{name}_x", f"{name}_y", f"{name}_z"]] = float("nan")
    return out


def main():
    here = Path(__file__).resolve().parent
    base_dir = here / "dataset" / "real_20260224"
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", type=Path, default=base_dir /
                    "recording_20260224_083945_landmarks_filtered.csv")
    ap.add_argument("--raw", type=Path, default=base_dir /
                    "recording_20260224_083945_landmarks_raw.csv")
    ap.add_argument("--out-dir", type=Path, default=here / "output" / "occlusion")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    sources = {"filtered": pd.read_csv(args.base), "raw": pd.read_csv(args.raw)}
    manifest = {"base_filtered": str(args.base), "base_raw": str(args.raw),
                "scenarios": {}}
    for name, source, landmarks, start, stop in SCENARIOS:
        out_csv = args.out_dir / f"masked_{name}.csv"
        mask(sources[source], landmarks, start, stop).to_csv(
            out_csv, index=False, float_format="%.6f")
        manifest["scenarios"][name] = {
            "csv": str(out_csv), "source": source, "landmarks": landmarks,
            "start": start, "stop": stop}
        print(f"[+] {name:12s} {source:8s} {landmarks if len(landmarks) < 8 else 'ALL'} "
              f"frames {start}-{stop - 1} -> {out_csv.name}")
    # Combined CSV with every filtered-source window applied (windows are
    # disjoint) — for the Unity demo video, not part of the validation.
    combo = sources["filtered"].copy()
    for name, source, landmarks, start, stop in SCENARIOS:
        if source == "filtered":
            combo = mask(combo, landmarks, start, stop)
    combo_csv = args.out_dir / "masked_all_windows.csv"
    combo.to_csv(combo_csv, index=False, float_format="%.6f")
    manifest["combo_csv"] = str(combo_csv)
    print(f"[+] combo (all filtered windows) -> {combo_csv.name}")

    with open(args.out_dir / "scenarios.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"[+] manifest: {args.out_dir / 'scenarios.json'}")


if __name__ == "__main__":
    main()

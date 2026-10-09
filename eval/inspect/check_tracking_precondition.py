#!/usr/bin/env python3
"""Recording validity check: is MediaPipe actually tracking the body?
(ASSUMPTIONS.md A6, eval/DECISIONS.md E-013)

An accuracy-evaluation window needs a measurement to grade, so the
evaluated landmarks must be TRACKED there (src == 0: visibility above
threshold AND valid depth). Occlusion robustness is tested separately
by synthetically masking tracked segments (truth available by
construction) - natural occlusion stretches carry no truth and are
case-study material only.

Run this right after extracting a new recording - it answers "is this
take usable?" before leaving the room:

  python v1/mediapipe/extract_landmarks_to_csv.py --bag <bag>
  python eval/inspect/check_tracking_precondition.py --stem <stem>

Criteria (per evaluated landmark, over the person-present span):
  coverage >= MIN_COVERAGE (default 0.95)
  longest continuous gap <= MAX_GAP_S (default 0.5 s)
Torso landmarks (hips, shoulders) must pass for ANY evaluation;
a hand's landmarks (elbow, wrist) must pass for THAT hand's
evaluation windows.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

TORSO = ("left_hip", "right_hip", "left_shoulder", "right_shoulder")
HANDS = {"left": ("left_elbow", "left_wrist"),
         "right": ("right_elbow", "right_wrist")}


def longest_run(mask):
    best = cur = 0
    for v in mask:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", required=True)
    ap.add_argument("--csv", default=None,
                    help="raw landmarks csv (default: v1/mediapipe/"
                         "output/<stem>_landmarks_raw.csv)")
    ap.add_argument("--min-coverage", type=float, default=0.95)
    ap.add_argument("--max-gap-s", type=float, default=0.5)
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()

    csv = Path(args.csv) if args.csv else \
        ROOT / f"v1/mediapipe/output/{args.stem}_landmarks_raw.csv"
    df = pd.read_csv(csv)
    t = df["time_s"].to_numpy()
    fps = 1.0 / np.median(np.diff(t))

    def tracked_col(name):
        # older extractions carry no _src columns; finite xyz means
        # the landmark passed the visibility + depth gates there
        if f"{name}_src" in df.columns:
            return (df[f"{name}_src"] == 0).to_numpy()
        return np.isfinite(df[f"{name}_x"].to_numpy())

    # person-present span: torso fully tracked marks presence; the
    # span runs from the first to the last such frame (entry/retreat
    # trimmed; short mid-span losses stay inside and count against
    # the torso landmarks, as they should).
    present = np.ones(len(df), bool)
    for k in TORSO:
        present &= tracked_col(k)
    if not present.any():
        print("FAIL: no frame has the full torso tracked")
        sys.exit(1)
    i0, i1 = np.argmax(present), len(present) - np.argmax(present[::-1])
    span = np.zeros(len(df), bool)
    span[i0:i1] = True
    print(f"{csv.name}: {len(df)} frames @ {fps:.1f} fps, "
          f"person-present span {t[i0]:.1f}-{t[i1 - 1]:.1f} s "
          f"({int(span.sum())} frames)")

    result = {"stem": args.stem, "span_s": [float(t[i0]),
                                            float(t[i1 - 1])],
              "criteria": {"min_coverage": args.min_coverage,
                           "max_gap_s": args.max_gap_s},
              "landmarks": {}, "verdicts": {}}

    def judge(name):
        tracked = tracked_col(name) & span
        cov = tracked[span].mean()
        gap_s = longest_run(~tracked[span]) / fps
        ok = cov >= args.min_coverage and gap_s <= args.max_gap_s
        result["landmarks"][name] = {"coverage": round(float(cov), 4),
                                     "longest_gap_s": round(gap_s, 2),
                                     "pass": bool(ok)}
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:15s} "
              f"coverage {100 * cov:5.1f} %  longest gap {gap_s:4.1f} s")
        return ok

    torso_ok = all([judge(k) for k in TORSO])
    hand_ok = {}
    for hand, names in HANDS.items():
        hand_ok[hand] = all([judge(k) for k in names]) and torso_ok

    result["verdicts"] = {
        "torso": torso_ok,
        "left_hand_windows": hand_ok["left"],
        "right_hand_windows": hand_ok["right"],
    }
    print(f"VERDICT: torso {'PASS' if torso_ok else 'FAIL'} | "
          f"left-hand evaluation {'PASS' if hand_ok['left'] else 'FAIL'}"
          f" | right-hand evaluation "
          f"{'PASS' if hand_ok['right'] else 'FAIL'}")
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(result, indent=1))
        print(f"[json] {args.json_out}")
    sys.exit(0 if torso_ok and all(hand_ok.values()) else 1)


if __name__ == "__main__":
    main()

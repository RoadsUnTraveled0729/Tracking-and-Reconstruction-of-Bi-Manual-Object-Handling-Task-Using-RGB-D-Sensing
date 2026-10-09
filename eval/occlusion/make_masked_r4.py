"""Regenerate the six synthetic occlusion scenarios on R4.

Same scenario designs, landmark sets, and window durations as the
frozen v1 make_masked_dataset.py (R1), with the windows placed at the
SAME run fractions applied within R4's person-present span (the v3
D-019 precedent) - entry/retreat frames have nothing to mask. Each
window is then verified fully-live for its masked landmarks in the
base CSV (a synthetic mask on top of a real gap would have no truth);
if not, the window slides forward to the nearest fully-live span and
the shift is recorded in the manifest.

Run: python eval/occlusion/make_masked_r4.py
Outputs masked CSVs + scenarios_r4.json into eval/output/occlusion_r4/.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "common"))
import paths

ALL = ["left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
       "left_wrist", "right_wrist", "left_hip", "right_hip"]

# (name, source, landmarks, r1_start, r1_stop_exclusive) - verbatim
# from v1/kinematics/make_masked_dataset.py:30-38; R1 base is 899
# frames.
R1_SCENARIOS = [
    ("wrist_short", "raw", ["right_wrist"], 300, 303),
    ("wrist_long", "filtered", ["right_wrist"], 400, 445),
    ("elbow_long", "filtered", ["right_elbow"], 500, 545),
    ("hip", "filtered", ["left_hip"], 600, 630),
    ("root_ref", "filtered", ["right_shoulder"], 750, 780),
    ("pose_loss", "filtered", ALL, 700, 710),
]
R1_LEN = 899


def live_span_ok(df, landmarks, start, stop):
    sub = df[(df["frame"] >= start) & (df["frame"] < stop)]
    if len(sub) != stop - start:
        return False
    for name in landmarks:
        if sub[[f"{name}_x", f"{name}_y", f"{name}_z"]].isna().any().any():
            return False
    return True


def place_window(df, landmarks, want_start, dur, present, taken):
    """Slide forward (then backward) from want_start to the nearest
    fully-live, non-overlapping window. Returns (start, shift)."""
    lo, hi = present
    for delta in range(0, hi - lo):
        for start in ({want_start + delta, want_start - delta}):
            stop = start + dur
            if start < lo or stop > hi + 1:
                continue
            if any(not (stop <= a or start >= b) for a, b in taken):
                continue
            if live_span_ok(df, landmarks, start, stop):
                return start, start - want_start
    raise RuntimeError(f"no live window of {dur} frames for {landmarks}")


def mask(df, landmarks, start, stop):
    out = df.copy()
    rows = (out["frame"] >= start) & (out["frame"] < stop)
    for name in landmarks:
        out.loc[rows, [f"{name}_x", f"{name}_y", f"{name}_z"]] = float("nan")
    return out


def main():
    stem = paths.R4_STEM
    out_dir = paths.EVAL_OUT / "occlusion_r4"
    out_dir.mkdir(parents=True, exist_ok=True)
    sources = {
        "filtered": pd.read_csv(paths.R4_LM_FILTERED),
        "raw": pd.read_csv(paths.R4_LM_RAW),
    }
    insp = json.loads(
        (paths.EVAL_REPORTS / f"{stem}_inspection.json").read_text())
    present = insp["phases"]["person_present"]
    span = present[1] - present[0]

    manifest = {"base_filtered": str(paths.R4_LM_FILTERED),
                "base_raw": str(paths.R4_LM_RAW),
                "person_present": present,
                "scenarios": {}}
    taken = []
    for name, source, landmarks, r1_a, r1_b in R1_SCENARIOS:
        dur = r1_b - r1_a
        want = present[0] + int(round(r1_a / R1_LEN * span))
        start, shift = place_window(sources[source], landmarks, want, dur,
                                    present, taken)
        stop = start + dur
        taken.append((start, stop))
        out_csv = out_dir / f"masked_{name}.csv"
        mask(sources[source], landmarks, start, stop).to_csv(
            out_csv, index=False, float_format="%.6f")
        manifest["scenarios"][name] = {
            "csv": str(out_csv), "source": source, "landmarks": landmarks,
            "start": int(start), "stop": int(stop),
            "r1_window": [r1_a, r1_b], "shift_from_fraction": int(shift)}
        print(f"[+] {name:12s} {source:8s} frames {start}-{stop - 1} "
              f"(shift {shift:+d} from the R1 fraction)")

    with open(out_dir / "scenarios_r4.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"[+] manifest: {out_dir / 'scenarios_r4.json'}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Automatic weak occlusion labels over a V3 extraction CSV, and the
score separation they imply (V3_PLAN.md Phase 3 gate recalibration).

Weak labels (no human input; noisy by construction):
  depth_front  joint depth nearer than the frame's torso median by
               more than gate.depth_front_margin_m: the sample most
               likely lies on the OCCLUDER, not the joint.
  velocity     camera-frame step exceeding gate.velocity_max_m_s
               between consecutive frames with valid xyz.
  no_depth     src == 2 in the extraction (none in the pinned bag).

For each joint class the script reports the score distribution of
weak-occluded vs clean samples and the Youden-J-optimal provisional
score threshold against the weak labels. These numbers PROPOSE
thresholds; the config nulls stay null until the manual labeling pass
(tools/label_gate.py, user step) confirms or corrects them (D-006).

Run: any python with pandas/numpy (no onnxruntime):
    /home/luo/anaconda3/bin/python v3/bench/gate_weak_labels.py
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

V3_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V3_ROOT))

from core.skeleton import JOINT_CLASS, V1_LANDMARKS  # noqa: E402

TORSO = ("left_shoulder", "right_shoulder", "left_hip", "right_hip")


def youden_threshold(scores_occ, scores_clean):
    """Score threshold maximizing TPR - FPR for 'flag when score < t'
    (occluded = positive). Returns (threshold, tpr, fpr)."""
    cand = np.unique(np.round(np.concatenate([scores_occ, scores_clean]), 3))
    best = (None, 0.0, 0.0, -1.0)
    for t in cand:
        tpr = float(np.mean(scores_occ < t)) if scores_occ.size else 0.0
        fpr = float(np.mean(scores_clean < t)) if scores_clean.size else 0.0
        j = tpr - fpr
        if j > best[3]:
            best = (float(t), tpr, fpr, j)
    return best[:3]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", default=str(
        V3_ROOT / "output/extraction_recording_20260224_083945.csv"))
    ap.add_argument("--config", default=str(V3_ROOT / "configs/default.json"))
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text())
    margin = cfg["gate"]["depth_front_margin_m"]
    vmax = cfg["gate"]["velocity_max_m_s"]
    fps = cfg["filter"]["freq_hz"]

    df = pd.read_csv(args.csv)
    n = len(df)
    print(f"extraction: {args.csv}")
    print(f"frames {n}; depth_front margin {margin} m; velocity max "
          f"{vmax} m/s at {fps} Hz")

    torso_z = df[[f"{t}_z" for t in TORSO]].median(axis=1)

    weak = {}      # name -> bool array (any weak label)
    reasons = {name: {"depth_front": 0, "velocity": 0, "no_depth": 0}
               for name in V1_LANDMARKS}
    for name in V1_LANDMARKS:
        z = df[f"{name}_z"]
        xyz = df[[f"{name}_x", f"{name}_y", f"{name}_z"]].to_numpy()
        front = (z < torso_z - margin).fillna(False).to_numpy()
        step = np.linalg.norm(np.diff(xyz, axis=0), axis=1) * fps
        vel = np.zeros(n, dtype=bool)
        vel[1:] = step > vmax
        vel &= ~np.isnan(xyz).any(axis=1)
        nod = (df[f"{name}_src"] == 2).to_numpy()
        reasons[name]["depth_front"] = int(front.sum())
        reasons[name]["velocity"] = int(vel.sum())
        reasons[name]["no_depth"] = int(nod.sum())
        weak[name] = front | vel | nod

    print("\nweak-label counts per landmark (of "
          f"{n} frames):")
    print(f"{'landmark':>15} {'depth_front':>11} {'velocity':>8} "
          f"{'no_depth':>8} {'any':>5}")
    for name in V1_LANDMARKS:
        r = reasons[name]
        print(f"{name:>15} {r['depth_front']:>11} {r['velocity']:>8} "
              f"{r['no_depth']:>8} {int(weak[name].sum()):>5}")

    print("\nscore separation and provisional thresholds per joint "
          "class (occluded = weak-labeled):")
    print(f"{'class':>9} {'n_occ':>6} {'n_clean':>8} {'occ_med':>8} "
          f"{'clean_med':>9} {'thresh':>7} {'tpr':>5} {'fpr':>5}")
    proposal = {}
    for cls in ("shoulder", "elbow", "wrist", "hip"):
        names = [nm for nm in V1_LANDMARKS if JOINT_CLASS[nm] == cls]
        occ, clean = [], []
        for nm in names:
            s = df[f"{nm}_score"].to_numpy()
            m = weak[nm]
            occ.append(s[m])
            clean.append(s[~m])
        occ = np.concatenate(occ)
        clean = np.concatenate(clean)
        if occ.size == 0:
            print(f"{cls:>9} {0:>6} {clean.size:>8} {'-':>8} "
                  f"{np.median(clean):>9.3f} {'-':>7} {'-':>5} {'-':>5}")
            proposal[cls] = None
            continue
        t, tpr, fpr = youden_threshold(occ, clean)
        proposal[cls] = t
        print(f"{cls:>9} {occ.size:>6} {clean.size:>8} "
              f"{np.median(occ):>8.3f} {np.median(clean):>9.3f} "
              f"{t:>7.3f} {tpr:>5.2f} {fpr:>5.2f}")

    print("\nprovisional thresholds (NOT applied to the config; the "
          "manual labeling pass confirms or corrects them):")
    print(json.dumps(proposal, indent=2))


if __name__ == "__main__":
    main()

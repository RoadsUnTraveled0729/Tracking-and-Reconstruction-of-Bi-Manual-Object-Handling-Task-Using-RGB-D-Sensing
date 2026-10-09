"""Assertions over the eval/ track's own machinery and outputs.

Check families:
1. Vendored-function regression: the carry/grip core rerun on the
   pinned R1 inputs (R1 classifier, R1 nearest-wrist semantics) must
   reproduce the pinned per-hand grip numbers from
   v1/integration/dataset/analyze_object_offset_output.txt within
   0.3 cm - detects drift in the copied functions.
2. R4 fit sanity: enough held frames per hand, grip std bounded,
   limb-length left-right symmetry, hold-radius separation.

Run: python eval/validate/validate_eval.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "common"))
sys.path.insert(0, str(HERE.parents[0] / "offset"))
import carry
import paths

FAILURES = []

# Pinned R1 numbers (v1/OBJECT_OFFSET.md section 3 / section 5,
# analyze_object_offset_output.txt).
PINNED_R1 = {
    "left": {"mu": (+3.8, -8.2, +8.6), "sd": (3.8, 2.8, 2.5),
             "frames": 314},
    "right": {"mu": (-11.0, -10.6, +5.3), "sd": (1.8, 0.9, 0.8),
              "frames": 249},
}


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}"
          + (f" -- {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def r1_regression():
    stem = paths.R1_STEM
    calib = json.load(open(paths.R1_CALIB))
    world = carry.LeveledWorld(calib)
    lm = pd.read_csv(paths.MP_OUT / f"{stem}_landmarks_filtered_v2.csv")
    ofil = pd.read_csv(paths.ARUCO_OUT / f"{stem}_object_world_filtered.csv")
    n = min(len(lm), len(ofil))
    lm, ofil = lm.iloc[:n], ofil.iloc[:n]
    obj, R_obj = world.object_world(
        ofil[["unity_px", "unity_py", "unity_pz"]].to_numpy(),
        ofil[["unity_ex", "unity_ey", "unity_ez"]].to_numpy())
    det = ofil["detected"].to_numpy() == 1
    wr = {s: world.wrist_world(
        lm[[f"{s}_wrist_x", f"{s}_wrist_y", f"{s}_wrist_z"]].to_numpy())
        for s in ("left", "right")}
    wrist_flag = {s: lm[f"{s}_wrist_flag"].to_numpy()
                  for s in ("left", "right")}
    carried = carry.carried_mask(obj, world)
    nearer, _ = carry.nearest_wrist(obj, wr["left"], wr["right"])
    fit = carry.fit_grip(obj, R_obj, wr, wrist_flag, det, carried, nearer)
    for side in ("left", "right"):
        pin = PINNED_R1[side]
        f = fit[side]
        check(f"R1 regression: {side} held-frame count matches pinned",
              abs(int(f["hold"].sum()) - pin["frames"]) <= 3,
              f"{int(f['hold'].sum())} vs pinned {pin['frames']}")
        if f["mu"] is None:
            check(f"R1 regression: {side} fit exists", False)
            continue
        dmu = np.max(np.abs(np.array(f["mu"]) * 100 - np.array(pin["mu"])))
        dsd = np.max(np.abs(np.array(f["sd"]) * 100 - np.array(pin["sd"])))
        check(f"R1 regression: {side} grip mean within 0.3 cm of pinned",
              dmu < 0.3, f"max delta {dmu:.2f} cm")
        check(f"R1 regression: {side} grip std within 0.3 cm of pinned",
              dsd < 0.3, f"max delta {dsd:.2f} cm")


def r4_sanity():
    rep = json.load(open(paths.EVAL_REPORTS
                         / f"{paths.R4_STEM}_offset_fit.json"))
    for side in ("left", "right"):
        ph = rep["per_hand"][side]
        check(f"R4: {side} hand has enough held frames (>=100)",
              ph is not None and ph["held_frames"] >= 100,
              f"{ph['held_frames'] if ph else 0}")
        if ph:
            check(f"R4: {side} grip std bounded (< 15 cm per axis)",
                  max(ph["std_cm"]) < 15.0, f"std {ph['std_cm']} cm")
            check(f"R4: {side} held magnitude p95 under the hold radius",
                  ph["wrist_to_center_p95_cm"] < rep["hold_radius_m"] * 100,
                  f"p95 {ph['wrist_to_center_p95_cm']} cm")
    seg = rep["segment_lengths_m"]
    check("R4: forearm left-right symmetry (< 2.5 cm)",
          abs(seg["forearm_R"] - seg["forearm_L"]) < 0.025,
          f"R {seg['forearm_R']} vs L {seg['forearm_L']} m")
    check("R4: upper-arm left-right symmetry (< 2.5 cm)",
          abs(seg["upper_arm_R"] - seg["upper_arm_L"]) < 0.025,
          f"R {seg['upper_arm_R']} vs L {seg['upper_arm_L']} m")


def fusion_firewall():
    """Flag 9 (fusion display fill) must never reach error statistics:
    the fusion CSV lives only under eval/output/, no reports file
    references it, and the analysis input CSVs carry no flag 9."""
    fusion_name = f"{paths.R4_STEM}_landmarks_fusion_display.csv"
    stray = [p for p in paths.EVAL_REPORTS.rglob("*") if p.is_file()
             and fusion_name in p.read_text(errors="ignore")]
    check("no reports artifact references the fusion-display CSV",
          not stray, ", ".join(str(s) for s in stray))
    lmf = pd.read_csv(paths.MP_OUT
                      / f"{paths.R4_STEM}_landmarks_filtered.csv")
    flag_cols = [c for c in lmf.columns if c.endswith("_flag")]
    has9 = bool((lmf[flag_cols] == 9).any().any())
    check("analysis landmark CSV contains no flag-9 samples", not has9)


def main():
    print("=== 1. vendored-core regression on pinned R1 ===")
    r1_regression()
    print("\n=== 2. R4 fit sanity ===")
    r4_sanity()
    print("\n=== 3. fusion-display firewall ===")
    fusion_firewall()
    print(f"\n=== {'ALL PASS' if not FAILURES else 'FAILED'} "
          f"({len(FAILURES)} failures) ===")
    sys.exit(1 if FAILURES else 0)


if __name__ == "__main__":
    main()

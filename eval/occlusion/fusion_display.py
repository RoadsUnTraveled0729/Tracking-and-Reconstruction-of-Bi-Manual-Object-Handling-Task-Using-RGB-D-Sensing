"""Display-only fusion filling (stage 5c).

Produces a Unity-bound landmark CSV in which wrist gaps during
established grip episodes are filled from box_center + fitted grip
offset, carrying flag 9 (FUSION_DISPLAY) in the wrist flag column.
HARD RULE: flag-9 samples are for the Unity display ONLY and must
never enter any error statistic; validate_eval.py asserts no eval
report was computed from this file.

Run: python eval/occlusion/fusion_display.py
Output: eval/output/<stem>_landmarks_fusion_display.csv
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
from fit_offset import load_tracks

FLAG_FUSION_DISPLAY = 9


def main():
    stem = paths.R4_STEM
    calib, world, lm, obj, R_obj, det, wr, wrist_flag, t = \
        load_tracks(stem, str(paths.r4_calib()))
    out_df = pd.read_csv(paths.R4_LM_FILTERED)
    n = min(len(out_df), len(obj))
    constancy = json.loads(
        (paths.EVAL_REPORTS / f"{stem}_stage2_constancy.json").read_text())
    fitrep = json.loads(
        (paths.EVAL_REPORTS / f"{stem}_offset_fit.json").read_text())

    # inverse of LeveledWorld.wrist_world: leveled -> camera frame
    Ginv = world.G.T
    Minv = np.linalg.inv(world.M)
    filled = {}
    for side in ("left", "right"):
        info = constancy["per_hand"][side]
        if info is None:
            continue
        mu = np.array(fitrep["per_hand"][side]["mu_cm"]) / 100.0
        pred_lev = obj + np.einsum("nij,j->ni", R_obj, mu)
        gap = ~np.isfinite(wr[side]).all(axis=1)
        fill = np.zeros(n, bool)
        for a, b in [e["frames"] for e in info.get("episodes", [])]:
            fill[a:b + 1] = True
        # also the long occluded stretch between episodes while carried
        insp = json.loads((paths.EVAL_REPORTS
                           / f"{stem}_inspection.json").read_text())
        carried = carry.rest_referenced_carried(
            obj, world, insp["phases"]["manipulation"])
        fill |= carried
        fill &= gap[:n] & det[:n]
        p_cam = ((Minv @ (Ginv @ pred_lev.T
                          - world.cam_pos[:, None])).T * [1, -1, 1])
        for j, ax in enumerate(("x", "y", "z")):
            col = f"{side}_wrist_{ax}"
            vals = out_df[col].to_numpy(dtype=float)
            vals[np.flatnonzero(fill)] = p_cam[fill, j]
            out_df[col] = vals
        flags = out_df[f"{side}_wrist_flag"].to_numpy(dtype=float)
        flags[np.flatnonzero(fill)] = FLAG_FUSION_DISPLAY
        out_df[f"{side}_wrist_flag"] = flags
        filled[side] = int(fill.sum())

    out = paths.EVAL_OUT / f"{stem}_landmarks_fusion_display.csv"
    out_df.to_csv(out, index=False, float_format="%.6f")
    print(f"[+] {out} (filled: {filled}) - DISPLAY ONLY, flag 9")


if __name__ == "__main__":
    main()

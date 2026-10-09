"""Visibility-gate miss rate and threshold sensitivity (stage 5a).

Uses the permissive --min-vis 0.0 extraction (positions retained at
every visibility) plus the raw per-cell visibility scores. For each
candidate threshold: how many wrist samples would the gate KEEP whose
position is demonstrably wrong, and how much data would it discard.

"Demonstrably wrong" has two independent definitions here:
  1. offset test (held frames only): |wrist - (box_center + fitted
     grip offset)| > 3 * max(fitted std) - the stage-2 reference
     chain used as an evaluation reference;
  2. segment test (any manipulation frame): apparent forearm length
     deviates more than 30 percent from the recording median (the
     E-007 physics gate).

Run: python eval/occlusion/gate_sweep.py
Outputs eval/reports/r4_gate_sweep.{json,md,png}.
"""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "common"))
sys.path.insert(0, str(HERE.parents[0] / "offset"))
import carry
import paths
from fit_offset import load_tracks

THRESHOLDS = [0.3, 0.4, 0.5, 0.6, 0.7]


def main():
    stem = paths.R4_STEM
    vis0 = pd.read_csv(paths.R4_LM_RAW_VIS0)
    calib, world, lm, obj, R_obj, det, wr_f, wrist_flag, t = \
        load_tracks(stem, str(paths.r4_calib()))
    n = min(len(vis0), len(obj))
    center = world.box_center(obj, R_obj)
    insp = json.loads(
        (paths.EVAL_REPORTS / f"{stem}_inspection.json").read_text())
    manip = insp["phases"]["manipulation"]
    in_manip = np.zeros(n, bool)
    in_manip[manip[0]:manip[1] + 1] = True
    carried = carry.rest_referenced_carried(obj, world,
                                            manip)[:n]
    fitrep = json.loads((paths.EVAL_REPORTS
                         / f"{stem}_offset_fit.json").read_text())

    report = {"stem": stem, "thresholds": THRESHOLDS, "sides": {}}
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for side, color in (("left", "tab:red"), ("right", "tab:blue")):
        vis = vis0[f"{side}_wrist_vis"].to_numpy()[:n]
        w_cam = vis0[[f"{side}_wrist_x", f"{side}_wrist_y",
                      f"{side}_wrist_z"]].to_numpy()[:n]
        have = np.isfinite(w_cam).all(axis=1)
        w_lev = world.wrist_world(w_cam)
        mu = np.array(fitrep["per_hand"][side]["mu_cm"]) / 100.0
        sd3 = 3 * max(fitrep["per_hand"][side]["std_cm"]) / 100.0
        pred = obj + np.einsum("nij,j->ni", R_obj, mu)
        off_err = np.linalg.norm(w_lev - pred, axis=1)
        # offset test is valid only where the hand demonstrably holds
        # the box: the contiguous grip episodes established by the
        # stage-4 fit (measured frames; the hand does not release
        # mid-episode).
        constancy = json.loads(
            (paths.EVAL_REPORTS
             / f"{stem}_stage2_constancy.json").read_text())
        holdish = np.zeros(n, bool)
        for ep in (constancy["per_hand"][side] or {}).get("episodes", []):
            a, b = ep["frames"]
            holdish[a:b + 1] = True
        holdish &= have
        wrong_offset = holdish & (off_err > sd3)
        # segment test
        el = vis0[[f"{side}_elbow_x", f"{side}_elbow_y",
                   f"{side}_elbow_z"]].to_numpy()[:n]
        L = np.linalg.norm(w_cam - el, axis=1)
        med = np.nanmedian(L)
        wrong_seg = in_manip & have & np.isfinite(L) \
            & (np.abs(L - med) > 0.3 * med)
        rows = []
        for th in THRESHOLDS:
            kept = have & (vis > th)
            miss_off = int((kept & wrong_offset).sum())
            miss_seg = int((kept & wrong_seg).sum())
            n_hold = int((kept & holdish).sum())
            n_manip = int((kept & in_manip).sum())
            rows.append({
                "threshold": th,
                "kept_cells": int(kept.sum()),
                "kept_fraction": round(float(kept.mean()), 3),
                "miss_offset": miss_off,
                "miss_offset_rate": round(miss_off / n_hold, 4)
                if n_hold else None,
                "miss_segment": miss_seg,
                "miss_segment_rate": round(miss_seg / n_manip, 4)
                if n_manip else None,
            })
        report["sides"][side] = rows
        axes[0].plot([r["threshold"] for r in rows],
                     [100 * (r["miss_segment_rate"] or 0) for r in rows],
                     "o-", c=color, label=f"{side} segment test")
        axes[0].plot([r["threshold"] for r in rows],
                     [100 * (r["miss_offset_rate"] or 0) for r in rows],
                     "s--", c=color, label=f"{side} offset test")
        axes[1].plot([r["threshold"] for r in rows],
                     [100 * r["kept_fraction"] for r in rows],
                     "o-", c=color, label=side)
    axes[0].axvline(0.5, color="k", ls=":", lw=1)
    axes[0].set_xlabel("visibility threshold")
    axes[0].set_ylabel("kept-but-wrong rate (percent)")
    axes[0].legend(fontsize=8)
    axes[0].set_title("gate miss rate (dotted line = current 0.5)")
    axes[1].axvline(0.5, color="k", ls=":", lw=1)
    axes[1].set_xlabel("visibility threshold")
    axes[1].set_ylabel("wrist cells kept (percent)")
    axes[1].legend(fontsize=8)
    axes[1].set_title("data retention")
    fig.tight_layout()
    out_png = paths.EVAL_REPORTS / "r4_gate_sweep.png"
    fig.savefig(out_png, dpi=120)

    out_json = paths.EVAL_REPORTS / "r4_gate_sweep.json"
    out_json.write_text(json.dumps(report, indent=1))
    md = ["# Visibility-gate sweep on R4", "",
          "Wrist cells; wrong = offset test (vs box + fitted grip, "
          "> 3 std) on holding-range frames, or segment test (forearm "
          "length off by > 30 percent) on manipulation frames.", ""]
    for side, rows in report["sides"].items():
        md += [f"## {side} wrist", "",
               "| thresh | kept | kept frac | wrong-offset kept (rate) | "
               "wrong-segment kept (rate) |", "|---|---|---|---|---|"]
        for r in rows:
            md.append(f"| {r['threshold']} | {r['kept_cells']} | "
                      f"{r['kept_fraction']} | {r['miss_offset']} "
                      f"({r['miss_offset_rate']}) | {r['miss_segment']} "
                      f"({r['miss_segment_rate']}) |")
        md.append("")
    (paths.EVAL_REPORTS / "r4_gate_sweep.md").write_text("\n".join(md))
    for f in (out_json, out_png):
        print(f"[+] {f}")


if __name__ == "__main__":
    main()

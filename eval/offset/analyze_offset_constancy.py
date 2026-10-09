"""Stage 4 driver, stage-2 half: kinematic wrist graded by offset
constancy against the calibrated ArUco reference.

Primary metric: the MAGNITUDE of the wrist-to-box-center vector on
held frames, per hand - median, p95, and drift over time. Supporting:
the full 3D vector in the object frame (grip analysis, from the
stage-3 fit). Error budget: stage-1 path RMS + survey uncertainty
set the floor below which discrepancies cannot be attributed to the
kinematic method; PENDING while the survey is.

Usage:
    python eval/offset/analyze_offset_constancy.py [--stem STEM]

Outputs eval/reports/<stem>_stage2_constancy.{json,md} and _constancy.png.
"""

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import theilslopes

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "common"))
import carry
import paths
from fit_offset import load_tracks

PATH_GATE = 0.05  # m, "near the labeled path" for the consistency check


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R4_STEM)
    args = ap.parse_args()
    stem = args.stem

    calib, world, lm, obj, R_obj, det, wr, wrist_flag, t = \
        load_tracks(stem, str(paths.r4_calib()))
    n = len(obj)
    center = world.box_center(obj, R_obj)
    insp = json.loads(
        (paths.EVAL_REPORTS / f"{stem}_inspection.json").read_text())
    carried = carry.rest_referenced_carried(
        obj, world, insp["phases"]["manipulation"])
    fitrep = json.loads(
        (paths.EVAL_REPORTS / f"{stem}_offset_fit.json").read_text())
    stage1 = json.loads(
        (paths.EVAL_REPORTS / f"{stem}_stage1_path.json").read_text())
    survey_ready = stage1.get("point_to_path_cm") != "PENDING SURVEY"

    report = {"stem": stem, "per_hand": {}, "manipulation_window":
              insp["phases"]["manipulation"]}
    fig, axes = plt.subplots(2, 1, figsize=(13, 7), sharex=True)

    print(f"=== {stem}: stage-2 offset constancy (held frames) ===")
    hold_masks = {}
    for side, color in (("left", "tab:red"), ("right", "tab:blue")):
        f_ok = carry.forearm_ok(lm, side)
        hold = carry.holding_mask(center, wr[side], wrist_flag[side], det,
                                  carried, f_ok)
        hold_masks[side] = hold
        m = np.linalg.norm(wr[side] - center, axis=1)
        hm, ht = m[hold], t[hold]
        if hold.sum() < 30:
            report["per_hand"][side] = None
            continue
        slope, intercept, lo, hi = theilslopes(hm * 100, ht / 60.0)
        half = ht[0] + (ht[-1] - ht[0]) / 2
        first = np.median(hm[ht <= half]) * 100
        second = np.median(hm[ht > half]) * 100
        # Per contiguous grip episode (gap > 15 frames starts a new
        # one): within-episode constancy is the rigid-grip claim;
        # across-episode shifts are regrips, reported separately.
        idx = np.flatnonzero(hold)
        brk = np.flatnonzero(np.diff(idx) > 15)
        starts = np.r_[idx[0], idx[brk + 1]]
        stops = np.r_[idx[brk], idx[-1]]
        episodes = []
        for a, b in zip(starts, stops):
            e = idx[(idx >= a) & (idx <= b)]
            if e.size < 30:
                continue
            em, et = m[e], t[e]
            es, ei, _, _ = theilslopes(em * 100, et / 60.0)
            episodes.append({
                "frames": [int(a), int(b)],
                "n": int(e.size),
                "median_cm": round(float(np.median(em)) * 100, 1),
                "std_cm": round(float(np.std(em)) * 100, 2),
                "slope_cm_per_min": round(float(es), 1),
            })
        entry = {
            "held_frames": int(hold.sum()),
            "median_cm": round(float(np.median(hm)) * 100, 1),
            "p95_cm": round(float(np.percentile(hm, 95)) * 100, 1),
            "drift_theilsen_cm_per_min": round(float(slope), 2),
            "drift_ci_cm_per_min": [round(float(lo), 2),
                                    round(float(hi), 2)],
            "first_half_median_cm": round(float(first), 1),
            "second_half_median_cm": round(float(second), 1),
            "episodes": episodes,
            "grip_vector_mu_cm": fitrep["per_hand"][side]["mu_cm"],
            "grip_vector_std_cm": fitrep["per_hand"][side]["std_cm"],
        }
        report["per_hand"][side] = entry
        print(f"  {side}: {entry['held_frames']} held frames, "
              f"|wrist-center| median {entry['median_cm']} cm, "
              f"p95 {entry['p95_cm']} cm, whole-span drift {slope:+.2f} "
              f"cm/min (CI {lo:+.2f}..{hi:+.2f}), halves "
              f"{first:.1f} -> {second:.1f} cm")
        for e in episodes:
            print(f"    episode {e['frames'][0]}-{e['frames'][1]} "
                  f"({e['n']} fr): median {e['median_cm']} cm, "
                  f"std {e['std_cm']} cm, slope {e['slope_cm_per_min']:+.1f} "
                  f"cm/min")
        ax = axes[0]
        ax.plot(t, m * 100, c=color, lw=0.6, alpha=0.4)
        ax.plot(ht, hm * 100, ".", c=color, ms=2.5, label=f"{side} held")
        tt = np.array([ht[0], ht[-1]])
        ax.plot(tt, intercept + slope * (tt / 60.0), c=color, lw=1.5,
                ls="--")

    # Error budget
    if survey_ready:
        s1 = stage1["point_to_path_cm"]
        sigma_survey_cm = 100 * (stage1.get("survey_sigma_m") or 0.0)
        floor = float(np.hypot(s1["p95"], sigma_survey_cm))
        report["error_budget_cm"] = {
            "stage1_p95": s1["p95"], "survey_sigma": sigma_survey_cm,
            "floor": round(floor, 2)}
    else:
        report["error_budget_cm"] = "PENDING SURVEY"
        print("  error budget: PENDING SURVEY (needs stage-1 path RMS + "
              "survey sigma)")

    # Consistency check: held frames near the labeled path
    if survey_ready:
        import path_metrics as pm
        sys.path.insert(0, str(HERE.parents[0] / "gt"))
        spec = pm.load_path(HERE.parents[0] / "gt" / "labeled_path.json")
        rows = []
        for side in ("left", "right"):
            hold = hold_masks[side]
            for f in np.flatnonzero(hold):
                _, dist, _, _ = pm.point_to_path(center[f], spec)
                if dist < PATH_GATE:
                    m_ = float(np.linalg.norm(wr[side][f] - center[f]))
                    rows.append((side, f, m_))
        report["consistency_near_path"] = {"n": len(rows)}
        # spread(m) vs sqrt(stage1^2 + fit spread^2) computed per hand
        for side in ("left", "right"):
            ms = np.array([r[2] for r in rows if r[0] == side])
            if ms.size < 30:
                continue
            spread = float(np.std(ms)) * 100
            fit_sd = max(fitrep["per_hand"][side]["std_cm"])
            bound = float(np.hypot(stage1["point_to_path_cm"]["p95"],
                                   fit_sd))
            report["consistency_near_path"][side] = {
                "spread_cm": round(spread, 2), "bound_cm": round(bound, 2),
                "ok": spread <= bound * 1.2}
    else:
        report["consistency_near_path"] = "PENDING SURVEY"
        print("  consistency check: PENDING SURVEY")

    axes[0].set_ylabel("|wrist - box center| (cm)")
    axes[0].set_ylim(0, 40)
    axes[0].legend(fontsize=8)
    axes[0].set_title(f"{stem}: offset magnitude on held frames "
                      "(dashes = Theil-Sen drift)")
    ax = axes[1]
    for side, ls in (("left", "-"), ("right", "--")):
        hold = hold_masks[side]
        d_loc = np.einsum("nij,ni->nj", R_obj, wr[side] - obj)
        for j, (axname, c) in enumerate(zip(
                ("x", "normal", "z"),
                ("tab:green", "tab:orange", "tab:purple"))):
            y = np.where(hold, d_loc[:, j], np.nan)
            ax.plot(t, y * 100, ls, c=c, lw=0.9,
                    label=f"{axname}" if side == "left" else None)
    ax.set_ylabel("object-frame components (cm)")
    ax.set_xlabel("time (s)")
    ax.legend(fontsize=8, ncol=3, title="solid left, dashed right")
    fig.tight_layout()
    out_png = paths.EVAL_REPORTS / f"{stem}_stage2_constancy.png"
    fig.savefig(out_png, dpi=120)

    out_json = paths.EVAL_REPORTS / f"{stem}_stage2_constancy.json"
    out_json.write_text(json.dumps(report, indent=1))
    print(f"[+] {out_json}")
    print(f"[+] {out_png}")


if __name__ == "__main__":
    main()

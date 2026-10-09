#!/usr/bin/env python3
"""E-020 experiment: does torso-capsule swivel pruning improve the
recovered elbow? (The DH/joint-limit idea, tested.)

E-013-compliant: synthetic elbow masks INSIDE genuinely tracked, clean
stretches; truth = the measured elbow the mask hid. Regimes:

  short   15-frame masks (well under the 45-frame memory horizon; the
          upper-arm EMA prior is fresh - hypothesis: limits change
          nothing)
  long    75-frame masks (the frozen prior goes stale while the arm
          keeps moving - the regime the limits target)
  object  long masks of elbow AND wrist, the wrist recovered from the
          object (full E-014 path; R5 grip episodes only)

Each regime runs limits OFF vs ON; metrics are computed on the masked
frames only. R1 runs the landmark-only regimes as the cross-recording
regression (limits must not make any R1 number worse).

Output: eval/reports/r5_joint_limit_ik.{md,json}
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE.parents[0] / "common"))
sys.path.insert(0, str(REPO / "v1" / "kinematics"))

import paths                                    # noqa: E402
import recovery_core                            # noqa: E402
from occlusion_ext import RobustChainSolver     # noqa: E402

SHORT, LONG, LEAD = 15, 75, 90     # LEAD clears the 60-frame self-calib
MIN_RUN = 180
GAP = 75                           # between tiled windows in one run
ARM = {"left": ("left_shoulder", "left_elbow", "left_wrist"),
       "right": ("right_shoulder", "right_elbow", "right_wrist")}
FLEX_IDX = {"right": 6, "left": 11}


def clean_runs(ok, min_len):
    runs, start = [], None
    for i, v in enumerate(ok):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start >= min_len:
                runs.append((start, i - 1))
            start = None
    if start is not None and len(ok) - start >= min_len:
        runs.append((start, len(ok) - 1))
    return runs


def windows_from_runs(runs, length):
    wins = []
    for a, b in runs:
        s = a + LEAD
        while s + length - 1 <= b:
            wins.append((s, s + length - 1))
            s += length + GAP
    return wins


def run_pass(lm_df, side, mask, elbow_limits, seg_len, w_hat=None,
             mask_wrist=False):
    """One solve pass; returns per-frame elbow points, angles, and the
    limit-intervention count."""
    sh, el, wr = ARM[side]
    solver = RobustChainSolver(seg_len=seg_len,
                               elbow_limits=elbow_limits)
    n = len(lm_df)
    elbows = np.full((n, 3), np.nan)
    angles = np.zeros((n, 13))
    for i, (_, row) in enumerate(lm_df.iterrows()):
        pts = recovery_core.solver_points(row)
        if mask[i]:
            pts.pop(el, None)
            if mask_wrist:
                pts.pop(wr, None)
        # an obj dict (sides may be None) engages the E-014 elbow-IK
        # path for a missing elbow with a measured wrist - the path
        # under test; obj=None would fall back to the memory recovery
        obj = {"left": None, "right": None}
        if mask_wrist and w_hat is not None \
                and np.all(np.isfinite(w_hat[i])):
            obj[side] = w_hat[i]
        out = solver.solve(pts, obj=obj)
        angles[i] = out[0]
        e = solver.last_points.get(el)
        if e is not None and np.all(np.isfinite(e)):
            elbows[i] = e
    return elbows, angles, solver.limit_applied


def truth_arrays(lm_df, side):
    sh, el, wr = ARM[side]
    n = len(lm_df)
    e_true = np.full((n, 3), np.nan)
    ok = np.zeros(n, bool)
    for i, (_, row) in enumerate(lm_df.iterrows()):
        pts = recovery_core.solver_points(row)
        if all(k in pts for k in (sh, el, wr)):
            e_true[i] = pts[el]
            ok[i] = True
    return e_true, ok


def metrics(elbows, angles, e_true, a_true, mask, side):
    m = mask & np.isfinite(elbows).all(1) & np.isfinite(e_true).all(1)
    err = np.linalg.norm(elbows[m] - e_true[m], axis=1) * 100.0
    fx = FLEX_IDX[side]
    d = np.abs((angles[m][:, fx] - a_true[m][:, fx] + 180) % 360 - 180)
    if not len(err):
        return {"frames": 0}
    return {"frames": int(m.sum()),
            "elbow_cm": {"median": round(float(np.median(err)), 2),
                         "p95": round(float(np.percentile(err, 95)), 2),
                         "max": round(float(err.max()), 2)},
            "flex_deg": {"median": round(float(np.median(d)), 2),
                         "max": round(float(d.max()), 2)}}


def main():
    results = {}
    for stem in (paths.R5_STEM, paths.R1_STEM):
        alias = paths.ALIAS[stem]
        results[alias] = {}
        lm_df = pd.read_csv(paths.lm_filtered(stem))
        n = len(lm_df)

        inputs = None
        seg_len = None
        if alias == "r5":
            inputs = recovery_core.build_inputs(stem)
            lm_df = inputs["lm_df"]
            n = inputs["n"]
            seg_len = inputs["seg_len"]

        for side in ("left", "right"):
            e_true, ok = truth_arrays(lm_df, side)
            allowed = ok.copy()
            if inputs is not None:
                # inside grip episodes, outside real failures
                allowed &= inputs["holding"][side][:n]
                allowed &= ~inputs["fail"][side][:n]
            runs = clean_runs(allowed, MIN_RUN)
            scen = {"short": windows_from_runs(runs, SHORT),
                    "long": windows_from_runs(runs, LONG)}
            # truth angles: unmasked pass, limits off
            a_true = run_pass(lm_df, side, np.zeros(n, bool), False,
                              seg_len)[1]
            results[alias][side] = {}
            for name, wins in scen.items():
                if not wins:
                    continue
                mask = np.zeros(n, bool)
                for a, b in wins:
                    mask[a:b + 1] = True
                entry = {"windows": len(wins)}
                for lim in (False, True):
                    el_p, an_p, hits = run_pass(lm_df, side, mask, lim,
                                                seg_len)
                    entry["on" if lim else "off"] = metrics(
                        el_p, an_p, e_true, a_true, mask, side)
                    if lim:
                        entry["on"]["limit_applied"] = hits
                results[alias][side][name] = entry
                # full E-014 path: elbow+wrist masked, wrist from object
                if inputs is not None and name == "long":
                    entry = {"windows": len(wins)}
                    for lim in (False, True):
                        el_p, an_p, hits = run_pass(
                            lm_df, side, mask, lim, seg_len,
                            w_hat=inputs["w_hat_solver"][side],
                            mask_wrist=True)
                        entry["on" if lim else "off"] = metrics(
                            el_p, an_p, e_true, a_true, mask, side)
                        if lim:
                            entry["on"]["limit_applied"] = hits
                    results[alias][side]["object"] = entry
            print(f"[{alias}/{side}] " + json.dumps(
                results[alias][side], indent=None)[:400])

    out = paths.EVAL_REPORTS / "r5_joint_limit_ik.json"
    out.write_text(json.dumps(results, indent=1))
    # (the .md report is hand-authored; this harness pins the raw
    # numbers in the json and prints the summary table)
    for alias in results:
        for side in results[alias]:
            for name, e in results[alias][side].items():
                if "off" not in e or e["off"].get("frames", 0) == 0:
                    continue
                o, l = e["off"], e["on"]
                print(f"  {alias}/{side}/{name} ({e['windows']} win, "
                      f"{o['frames']} f): off "
                      f"{o['elbow_cm']['median']}/{o['elbow_cm']['p95']}"
                      f" cm -> on {l['elbow_cm']['median']}/"
                      f"{l['elbow_cm']['p95']} cm, interventions "
                      f"{l.get('limit_applied', 0)}")
    print(f"[+] {out}")


if __name__ == "__main__":
    main()

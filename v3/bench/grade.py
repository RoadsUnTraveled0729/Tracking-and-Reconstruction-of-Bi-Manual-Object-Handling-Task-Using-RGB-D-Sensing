#!/usr/bin/env python3
"""Grade strategies over the S-type scenario manifest (D-003 metrics).

For each scenario x strategy: replay the masked CSV through the causal
pipeline, derive truth by replaying the UNMASKED base CSV through the
identical pipeline (never stored), and evaluate: E_occ mean/max,
E_reacq (K from config), recovery time, teleport count against the
manifest's derived budgets, continuity p95, and the honesty confusion
(expected groups x window, slop from config). Hard-gate verdicts
follow bench.json.

Run: /home/luo/anaconda3/bin/python v3/bench/grade.py [--strategies
baseline_hold]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

V3_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V3_ROOT))

from bench import metrics as m                       # noqa: E402
from replay.runner import run_csv                    # noqa: E402
from strategies.strategy_base import build           # noqa: E402
import strategies.baseline_hold                      # noqa: E402,F401
import strategies.s2_quat_prediction                 # noqa: E402,F401
from bench.paths import apply_overrides, repo_path                    # noqa: E402

STATUS_COLS = [f"status_{g}" for g in m.GROUP_NAMES]


def twist_gate_mask(man, base_csv, cfg):
    """D-033: (T-1, 13) teleport mask from the ORACLE twist_ok of the
    unmasked base CSV (the observability the budgets were derived
    under; scenario-independent, so an occlusion window cannot exempt
    its own reacquisition steps), or None for manifests without
    teleport_twist_gate (the D-003 ungated count)."""
    gate = man.get("teleport_twist_gate", "none")
    if gate == "none":
        return None
    if gate != "oracle_twist_ok":
        raise ValueError(f"unknown teleport_twist_gate {gate!r}")
    from bench.oracle import (oracle_angles, require_twist_min_bend,
                              twist_observable)
    min_bend = require_twist_min_bend(man, "scenario manifest")
    orc = oracle_angles(base_csv, cfg)
    return m.twist_step_valid(*twist_observable(orc, min_bend))


def grade_scenario(scn, base_csv, cfg, budgets, strategy_name, truth_df,
                   warmup, valid=None, test=None):
    """valid: D-033 teleport mask (twist_gate_mask) or None. test: an
    already-run output table for this scenario (the injection check of
    bench/teleport_injection_check.py), else the strategy is run."""
    if test is None:
        strat = build(strategy_name, cfg)
        test = run_csv(str(repo_path(scn["csv"])), cfg, strat)
    A = test[list(m.ANGLE_NAMES)].to_numpy()
    T = truth_df[list(m.ANGLE_NAMES)].to_numpy()
    gerr = m.group_error(m.angle_error(A, T))
    start, stop = scn["start"], scn["stop"]
    k = cfg["budget"]["reacq_k"]
    occ = m.e_occ(gerr, start, stop)
    reacq = m.e_reacq(gerr, stop, k)
    rec = m.recovery_time(gerr, stop, cfg["budget"]["recovery_deg"],
                          cfg["budget"]["recovery_sustain_frames"])
    # teleport and continuity exclude warmup, matching the budget
    # derivation and v1's warm-up exclusions (rest-pose snap and
    # filter convergence are start-of-stream artifacts, not strategy
    # behavior)
    steps = m.angle_steps(A)[warmup:]
    tele = m.teleport_count(steps, budgets,
                            None if valid is None else valid[warmup:])
    cont = m.continuity_p95(steps)
    g_idx = [m.GROUP_NAMES.index(g) for g in scn["expected_groups"]]
    windows = [(g, start, stop) for g in g_idx]
    hon = m.honesty_confusion(test[STATUS_COLS].to_numpy(), windows,
                              cfg["budget"]["honesty_boundary_slop_frames"])
    sel = np.array(g_idx)
    return {
        "e_occ_mean": float(occ["mean"][sel].max()),
        "e_occ_max": float(occ["max"][sel].max()),
        "e_reacq": float(reacq[sel].max()),
        "recovery": float(rec[sel].max()),
        "teleports": tele["count"],
        "worst_step": tele["worst_step_deg"],
        "cont_p95": float(cont.max()),
        "false_measured": hon["false_measured"],
        "est_coverage": hon["estimated_coverage"],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(V3_ROOT / "configs/default.json"))
    ap.add_argument("--manifest", default=None,
                    help="default: config paths.scenario_manifest")
    ap.add_argument("--strategies", default="baseline_hold")
    ap.add_argument("--realtime-txt", default=None,
                    help="replay/realtime.py output for the same model "
                         "variant; its total p99 verdict is reported as "
                         "the latency_p99 hard gate")
    ap.add_argument("--set", action="append", default=[],
                    help="config override key.path=json (repeatable), "
                         "e.g. strategy.s2_quat_prediction.smoother="
                         "quat_one_euro")
    args = ap.parse_args()

    cfg = apply_overrides(json.loads(Path(args.config).read_text()),
                          args.set)
    if args.manifest is None:
        args.manifest = str(repo_path(cfg["paths"]["scenario_manifest"]))
    # the active manifest also feeds S2's derived step caps (D-032)
    cfg["paths"]["scenario_manifest"] = args.manifest
    man = json.loads(Path(args.manifest).read_text())
    budgets = np.array([man["teleport_budget_deg"][a]
                        for a in m.ANGLE_NAMES])
    fm_max = cfg["budget"]["false_measured_max"]
    warmup = json.loads((V3_ROOT / "configs/bench.json").read_text())[
        "latency"]["warmup_frames"]

    print(f"manifest: {args.manifest} (derived {man['derived_at']}, "
          f"commit {man['derived_from_commit'][:9]}, variant "
          f"{man.get('variant', 'rtmpose-m (pre-M3 manifest)')})")
    print(f"base csv: {man['base_csv']}")
    s2c = cfg["strategy"]["s2_quat_prediction"]
    if any(sn == "s2_quat_prediction" for sn in args.strategies.split(",")):
        print(f"s2: smoother {s2c.get('smoother', 'none')}, warm_start "
              f"{s2c.get('warm_start', False)}, step caps "
              f"{s2c.get('step_cap_source', 'fixed')}; bones.project "
              f"{cfg.get('bones', {}).get('project', False)}"
              + (f"; overrides {args.set}" if args.set else ""))
    base_csv = str(repo_path(man["base_csv"]))
    valid = twist_gate_mask(man, base_csv, cfg)
    print(f"teleport twist gate: {man.get('teleport_twist_gate', 'none')}"
          + ("" if valid is None else
             f" (r_twist steps counted {int(valid[warmup:, 5].sum())}, "
             f"l_twist {int(valid[warmup:, 10].sum())} of "
             f"{len(valid) - warmup})"))
    summary = []
    for strategy_name in args.strategies.split(","):
        print(f"\n=== strategy: {strategy_name} ===")
        truth_strat = build(strategy_name, cfg)
        truth = run_csv(base_csv, cfg, truth_strat)
        n_tele = n_hon = 0
        print(f"{'scenario':>12} {'e_occ':>7} {'e_max':>7} {'reacq':>7} "
              f"{'recov':>6} {'tele':>4} {'wstep':>7} {'fmeas':>6} "
              f"{'estcov':>6}")
        for scn in man["scenarios"]:
            r = grade_scenario(scn, base_csv, cfg, budgets,
                               strategy_name, truth, warmup, valid)
            rec = ("inf" if np.isinf(r["recovery"])
                   else f"{r['recovery']:.0f}")
            print(f"{scn['name']:>12} {r['e_occ_mean']:>7.2f} "
                  f"{r['e_occ_max']:>7.2f} {r['e_reacq']:>7.2f} "
                  f"{rec:>6} {r['teleports']:>4} {r['worst_step']:>7.2f} "
                  f"{r['false_measured']:>6.3f} {r['est_coverage']:>6.2f}")
            gate_fail = []
            if r["teleports"] > 0:
                gate_fail.append("teleport")
            if r["false_measured"] >= fm_max:
                gate_fail.append("honesty")
            if gate_fail:
                print(f"{'':>12} HARD GATE FAIL: {', '.join(gate_fail)}")
            n_tele += "teleport" in gate_fail
            n_hon += "honesty" in gate_fail
        summary.append((strategy_name, n_tele, n_hon,
                        len(man["scenarios"])))

    lat = "not measured (no --realtime-txt)"
    if args.realtime_txt:
        lines = [ln for ln in Path(args.realtime_txt).read_text()
                 .splitlines() if ln.startswith("budget check")]
        if len(lines) != 1:
            sys.exit(f"[ERROR] {args.realtime_txt}: expected one "
                     "'budget check' line from replay/realtime.py")
        lat = f"{lines[0]} ({Path(args.realtime_txt).name})"
    print("\nhard gates (bench.json ranking.hard_gates):")
    print(f"  latency_p99: {lat}")
    for name, nt, nh, n in summary:
        print(f"  {name:>18}: teleport_zero "
              f"{'PASS' if nt == 0 else 'FAIL'} ({nt}/{n} scenarios fail),"
              f" honesty_false_measured {'PASS' if nh == 0 else 'FAIL'} "
              f"({nh}/{n} fail)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""D-033 teleport rule check (M4): budgets, S2 caps, synthetic teleport
injection, and cap activity on the clean windows.

1. Budget table per angle: the D-003 clean_run manifest vs the D-033
   oracle_union manifest (twist steps gated by the oracle elbow bend,
   budget.twist_min_bend_deg).
2. S2 per-track caps (derive_step_caps) under both manifests.
3. Injection: S2 (active config) is run on the pose_loss scenario; one
   copy gets a single step of INJECT_FACTOR x the angle's budget added
   to r_swing_z from the first frame after the occlusion window where
   R_swing is MEASURED on (a step function: one step of that size plus
   the natural step), a second copy the same on r_elbow_y / R_elbow.
   Graded with bench/grade.py grade_scenario on the D-033 manifest and
   its twist mask. Expected: both injections FAIL the teleport gate,
   the un-injected output PASSes.
4. Cap activity: fraction of clean-window frames (stop inclusive) on
   which each S2 track's output step was bound by its cap, for the
   manifest caps and for the legacy fixed caps.

Run: /home/luo/anaconda3/bin/python v3/bench/teleport_rule_check.py
       --out-txt v3/dataset/phase5_teleport_rule_check.txt
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

V3_ROOT = Path(__file__).resolve().parents[1]
if str(V3_ROOT) not in sys.path:
    sys.path.insert(0, str(V3_ROOT))

import bench.metrics as m                                            # noqa: E402
from bench.grade import grade_scenario, twist_gate_mask             # noqa: E402
from bench.paths import apply_overrides, repo_path, repo_rel         # noqa: E402
from replay.runner import run_csv                                    # noqa: E402
from strategies.strategy_base import build                           # noqa: E402
import strategies.s2_quat_prediction as s2mod                        # noqa: E402

# master decision 2026-09-25 (D-033): inject 1.5 x the angle's budget
INJECT_FACTOR = 1.5
INJECTIONS = (("r_swing_z", "R_swing"), ("r_elbow_y", "R_elbow"))
TRACKS = ["root"] + [f"{s}_{k}" for s in ("r", "l")
                     for k in ("swing", "twist", "elbow")]


def cap_activity(cfg, windows, clean_dir, variant):
    """{track: (capped frames, frames)} over all windows."""
    tot = {t: [0, 0] for t in TRACKS}
    for w in windows:
        csv = Path(clean_dir) / f"extraction_{Path(w['bag']).stem}__{variant}.csv"
        strat = build("s2_quat_prediction", cfg)
        flags = []
        orig = strat.update

        def upd(t, points, scores, _o=orig, _s=strat):
            out = _o(t, points, scores)
            row = {"root": _s.root.capped}
            for sd in ("r", "l"):
                for k in ("swing", "twist", "elbow"):
                    row[f"{sd}_{k}"] = _s.arms[sd][k].capped
            flags.append(row)
            return out
        strat.update = upd
        tab = run_csv(str(csv), cfg, strat)
        fr = tab["frame"].to_numpy()
        sel = (fr >= int(w["start"])) & (fr <= int(w["stop"]))
        for t in TRACKS:
            a = np.array([f[t] for f in flags], dtype=bool)[sel]
            tot[t][0] += int(a.sum())
            tot[t][1] += int(a.size)
    return tot


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--config", default=str(V3_ROOT / "configs/default.json"))
    ap.add_argument("--old-manifest", default=str(
        V3_ROOT / "configs/scenarios_20260224__rtmpose-x_yolox-m.json"))
    ap.add_argument("--windows-file",
                    default=str(V3_ROOT / "configs/clean_windows.json"))
    ap.add_argument("--clean-csv-dir", default=str(V3_ROOT / "output/clean"))
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--out-txt", default=None)
    args = ap.parse_args()

    lines = []

    def out(s=""):
        print(s)
        lines.append(s)

    cfg = apply_overrides(json.loads(Path(args.config).read_text()), args.set)
    new_p = str(repo_path(cfg["paths"]["scenario_manifest"]))
    new = json.loads(Path(new_p).read_text())
    old = json.loads(Path(args.old_manifest).read_text())
    variant = new.get("variant", cfg["model"]["variant"])
    s2c = cfg["strategy"]["s2_quat_prediction"]
    out("V3 D-033 teleport rule check (bench/teleport_rule_check.py)")
    out(f"variant {variant}; D-003 manifest {repo_rel(Path(args.old_manifest))}"
        f"; D-033 manifest {repo_rel(Path(new_p))} (derived "
        f"{new['derived_at']}, twist_min_bend_deg "
        f"{new.get('twist_min_bend_deg')})")
    out(f"S2: smoother {s2c.get('smoother')}, warm_start "
        f"{s2c.get('warm_start')}, step_cap_source "
        f"{s2c.get('step_cap_source')}; overrides {args.set}")
    out(f"D-033 note: {new['teleport_budget_note']}")
    out()
    out("1. Teleport budgets (deg per frame)")
    out(f"{'angle':>10} {'D-003':>8} {'D-033':>8} {'ratio':>7}")
    for an in m.ANGLE_NAMES:
        a, b = old["teleport_budget_deg"][an], new["teleport_budget_deg"][an]
        r = f"{b / a:7.2f}" if a > 1e-6 else f"{'n/a':>7}"
        out(f"{an:>10} {a:8.3f} {b:8.3f} {r}")

    out()
    out("2. S2 step caps (deg per frame; 0.8 x smallest non-degenerate "
        "budget of the track's angles, D-021 rule / D-032)")
    caps_new = s2mod.derive_step_caps(dict(s2c, step_cap_source="manifest"),
                                      new["teleport_budget_deg"])
    caps_old_man = s2mod.derive_step_caps(
        dict(s2c, step_cap_source="manifest"), old["teleport_budget_deg"])
    caps_fixed = s2mod.derive_step_caps(dict(s2c, step_cap_source="fixed"),
                                        None)
    out(f"{'track':>8} {'fixed':>7} {'D-003m':>7} {'D-033m':>7}")
    for t in TRACKS:
        out(f"{t:>8} {caps_fixed[t]:7.3f} {caps_old_man[t]:7.3f} "
            f"{caps_new[t]:7.3f}")

    out()
    out(f"3. Injection check: +{INJECT_FACTOR} x budget, one step "
        "(step function) on the first frame after the pose_loss window "
        "whose group is MEASURED; graded on the D-033 manifest with its "
        "twist mask")
    cfg["paths"]["scenario_manifest"] = new_p
    budgets = np.array([new["teleport_budget_deg"][a] for a in m.ANGLE_NAMES])
    warmup = json.loads((V3_ROOT / "configs/bench.json").read_text())[
        "latency"]["warmup_frames"]
    base_csv = str(repo_path(new["base_csv"]))
    valid = twist_gate_mask(new, base_csv, cfg)
    truth = run_csv(base_csv, cfg, build("s2_quat_prediction", cfg))
    scn = next((s for s in new["scenarios"] if s["name"] == "pose_loss"),
               None)
    if scn is None:
        raise ValueError("scenario manifest has no 'pose_loss' scenario")
    test = run_csv(str(repo_path(scn["csv"])), cfg,
                   build("s2_quat_prediction", cfg))
    verdicts = []
    r0 = grade_scenario(scn, base_csv, cfg, budgets, "s2_quat_prediction",
                        truth, warmup, valid, test=test)
    ok0 = r0["teleports"] == 0
    out(f"  un-injected S2: teleports {r0['teleports']}, worst step "
        f"{r0['worst_step']:.2f} deg -> {'PASS' if ok0 else 'FAIL'} "
        "(expected PASS)")
    verdicts.append(ok0)
    fr = test["frame"].to_numpy()
    for an, grp in INJECTIONS:
        j = m.ANGLE_NAMES.index(an)
        st = test[f"status_{grp}"].to_numpy()
        cand = np.where((fr > scn["stop"]) & (st == m.MEASURED))[0]
        if len(cand) == 0:
            raise ValueError(
                f"scenario {scn['name']!r}: no MEASURED {grp} frame after "
                f"the window stop (frame {scn['stop']}), so the {an} "
                "injection has no reacquisition frame")
        t0 = int(cand[0])
        delta = INJECT_FACTOR * budgets[j]
        inj = test.copy()
        inj.loc[inj.index[t0:], an] = inj[an].to_numpy()[t0:] + delta
        nat = float(abs(m.wrap_deg(test[an].to_numpy()[t0]
                                   - test[an].to_numpy()[t0 - 1])))
        step = float(abs(m.wrap_deg(inj[an].to_numpy()[t0]
                                    - inj[an].to_numpy()[t0 - 1])))
        r = grade_scenario(scn, base_csv, cfg, budgets, "s2_quat_prediction",
                           truth, warmup, valid, test=inj)
        fail = r["teleports"] > 0
        out(f"  inject {an:>9} +{delta:.3f} deg (budget {budgets[j]:.3f}) at "
            f"frame {int(fr[t0])}: natural step {nat:.3f}, injected step "
            f"{step:.3f} deg; teleports {r['teleports']} -> "
            f"{'FAIL' if fail else 'PASS'} (expected FAIL)")
        verdicts.append(fail)
    out(f"  injection check: {'OK' if all(verdicts) else 'ERROR'} "
        f"({sum(verdicts)}/{len(verdicts)} as expected)")

    out()
    out("4. Cap activity on the clean windows (fraction of window frames "
        "whose output step was bound by the track cap; S2 as configured)")
    wins = json.loads(Path(args.windows_file).read_text())["windows"]
    act_new = cap_activity(cfg, wins, args.clean_csv_dir, variant)
    cfg_fixed = apply_overrides(cfg, [
        "strategy.s2_quat_prediction.step_cap_source=\"fixed\""])
    act_fixed = cap_activity(cfg_fixed, wins, args.clean_csv_dir, variant)
    out(f"{'track':>8} {'fixed caps':>11} {'D-033 caps':>11}")
    for t in TRACKS:
        a, b = act_fixed[t], act_new[t]
        out(f"{t:>8} {a[0] / a[1]:11.3f} {b[0] / b[1]:11.3f}")
    out(f"  frames: {act_new['root'][1]} over {len(wins)} windows")
    if args.out_txt:
        Path(args.out_txt).write_text("\n".join(lines) + "\n")
    return 0 if all(verdicts) else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Smoother / S2-setting sweep on the clean windows (M4, D-029..D-032).

Each configuration is a list of config overrides (bench CLIs' --set);
for each, bench/grade_clean.py runs s2_quat_prediction on the four
clean windows (its CSV is read back) and, with --gates, bench/grade.py
grades the six S-type scenarios. Per configuration and per track kind
the table reports, over windows x the kind's angles (identically-zero
elbow_z excluded):

  rms0   mean RMS vs the oracle at lag 0 (deg)
  |lag|  mean |best lag| (frames)
  rmsL   mean RMS at the best lag (deg)
  d2/o   geometric mean of second-diff RMS causal / oracle

Kinds: root = root_x,y,z; swing = r/l_swing_y,z; twist = r/l_twist;
elbow = r/l_elbow_y. Tracks of different kinds are independent state
machines (the root couples into the arm MEASUREMENTS through the solve
chain, not into the arm tracks' smoothing), so one grid run with every
kind at the same (min_cutoff, beta) scores every kind at that point.

Selection rule for quat_one_euro (stated in D-029 before the grid was
run), per kind: (1) feasible = d2/o <= 1.5; choose the feasible point
with the lowest rms0; (2) if none is feasible, choose the lowest d2/o
among points whose rms0 is not above the smoother-"none" rms0 of that
kind; (3) if that set is empty too, keep "none"-equivalent behaviour
for that kind is impossible inside one smoother, so choose the lowest
rms0 point and flag it.

Generalised in M5 (D-038): --smoother names the smoother and --grid /
--fixed give its parameter grid as JSON ({param: [values]} and {param:
value}); without --grid, quat_one_euro keeps the M4 axes --min-cutoffs
x --betas with d_cutoff fixed. Every point applies the same parameters
to every kind. --jobs runs grid points in parallel (each point is an
independent grade_clean.py subprocess; results do not depend on the
order). Besides the selection rule above, the table reports an
alternative, lag-weighted rule (M5 brief, informational): among the
feasible points (d2/o <= 1.5) minimise rms0 + LAG_WEIGHT_DEG x |lag|,
LAG_WEIGHT_DEG = 0.5 deg per frame of mean |best lag| (a master-brief
value with no measured source), so the master can see whether a
smoother's advantage is lag rather than lag-0 RMS.

Run: /home/luo/anaconda3/bin/python v3/bench/sweep_smoother.py grid
       --base-set strategy.s2_quat_prediction.warm_start=true ...
     /home/luo/anaconda3/bin/python v3/bench/sweep_smoother.py grid
       --smoother tangent_kf --grid '{"q_w": [..], "r_v": [..]}'
       --fixed '{"q_r": 1.0}' --jobs 16
"""
import argparse
import itertools
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

V3_ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
KIND_ANGLES = {"root": ["root_x", "root_y", "root_z"],
               "swing": ["r_swing_y", "r_swing_z", "l_swing_y",
                         "l_swing_z"],
               "twist": ["r_twist", "l_twist"],
               "elbow": ["r_elbow_y", "l_elbow_y"]}
S2 = "strategy.s2_quat_prediction"
LAG_WEIGHT_DEG = 0.5    # deg per frame of |lag|; M5 brief, no source


def smoother_of(sets):
    """grade_clean.py sets the smoother per --smoothers entry (it
    overrides strategy.s2_quat_prediction.smoother), so the smoother
    named in the overrides must be passed as --smoothers."""
    name = "none"
    for s in sets:
        if s.startswith(f"{S2}.smoother="):
            name = s.split("=", 1)[1].strip('"')
    return name


def run_clean(sets, out_csv, variant=None, manifest=None):
    cmd = [PY, str(V3_ROOT / "bench/grade_clean.py"), "--strategies",
           "s2_quat_prediction", "--smoothers", smoother_of(sets),
           "--out-txt", "", "--out-csv", str(out_csv)]
    for s in sets:
        cmd += ["--set", s]
    if variant:
        cmd += ["--variant", variant]
    if manifest:
        cmd += ["--manifest", manifest]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    return pd.read_csv(out_csv)


def run_gates(sets, out_txt, manifest=None):
    cmd = [PY, str(V3_ROOT / "bench/grade.py"), "--strategies",
           "s2_quat_prediction"]
    for s in sets:
        cmd += ["--set", s]
    if manifest:
        cmd += ["--manifest", manifest]
    txt = subprocess.run(cmd, check=True, capture_output=True,
                         text=True).stdout
    Path(out_txt).write_text(txt)
    fails = txt.count("HARD GATE FAIL")
    tele = sum("teleport" in ln for ln in txt.splitlines()
               if "HARD GATE FAIL" in ln)
    blk = txt.split("=== strategy: s2_quat_prediction ===")[-1]
    wstep = [float(ln.split()[6]) for ln in blk.splitlines()
             if len(ln.split()) == 9 and ln.split()[0] != "scenario"]
    return fails, tele, max(wstep) if wstep else float("nan")


def kind_metrics(df, kind, windows=None):
    d = df[df["angle"].isin(KIND_ANGLES[kind])]
    if windows:
        d = d[d["window"].isin(windows)]
    r = d["second_diff_rms_causal"] / d["second_diff_rms_oracle"]
    return {"rms0": float(d["rms_vs_oracle_lag0"].mean()),
            "lag": float(d["best_lag"].abs().mean()),
            "rmsL": float(d["rms_vs_oracle_best_lag"].mean()),
            "d2o": float(np.exp(np.mean(np.log(r))))}


def choose(rows, none_rows):
    """rows: [(point, {kind: metrics})]; none_rows: {kind: metrics}."""
    pick = {}
    for kind in KIND_ANGLES:
        feas = [(mt[kind]["rms0"], p) for p, mt in rows
                if mt[kind]["d2o"] <= 1.5]
        if feas:
            pick[kind] = (min(feas)[1], "rule 1 (d2/o <= 1.5, min rms0)")
            continue
        ok = [(mt[kind]["d2o"], p) for p, mt in rows
              if mt[kind]["rms0"] <= none_rows[kind]["rms0"]]
        if ok:
            pick[kind] = (min(ok)[1], "rule 2 (no point meets d2/o <= "
                          "1.5; min d2/o with rms0 <= none)")
            continue
        pick[kind] = (min((mt[kind]["rms0"], p) for p, mt in rows)[1],
                      "rule 3 (FLAG: every point costs rms0 vs none)")
    return pick


def choose_lag_weighted(rows, weight=LAG_WEIGHT_DEG, bound=1.5):
    """Alternative rule (informational): among points with d2/o <=
    bound, minimise rms0 + weight x |lag|; None when none is feasible."""
    pick = {}
    for kind in KIND_ANGLES:
        feas = [(mt[kind]["rms0"] + weight * mt[kind]["lag"], p)
                for p, mt in rows if mt[kind]["d2o"] <= bound]
        pick[kind] = min(feas)[1] if feas else None
    return pick


def _fmt(v):
    return f"{v:g}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("mode", choices=("grid", "configs"))
    ap.add_argument("--base-set", action="append", default=[])
    ap.add_argument("--configs", default=None,
                    help="configs mode: JSON file {name: [--set ...]}")
    ap.add_argument("--min-cutoffs", default="0.25,0.5,1,2,4")
    ap.add_argument("--betas", default="0,0.1,0.5,2")
    ap.add_argument("--d-cutoff", type=float, default=None,
                    help="default: config filter.d_cutoff")
    ap.add_argument("--smoother", default="quat_one_euro",
                    help="grid mode: smoother to sweep")
    ap.add_argument("--grid", default=None,
                    help='grid mode: JSON {param: [values]} (default for '
                         'quat_one_euro: --min-cutoffs x --betas)')
    ap.add_argument("--fixed", default=None,
                    help="grid mode: JSON {param: value} held fixed")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--gates", action="store_true")
    ap.add_argument("--work", default=str(V3_ROOT / "output/smoother_sweep"))
    ap.add_argument("--out-txt", default=None)
    args = ap.parse_args()
    work = Path(args.work)
    work.mkdir(parents=True, exist_ok=True)
    cfg = json.loads((V3_ROOT / "configs/default.json").read_text())
    dc = (args.d_cutoff if args.d_cutoff is not None
          else float(cfg["filter"]["d_cutoff"]))
    lines = []

    def out(s=""):
        print(s, flush=True)
        lines.append(s)

    out("V3 S2 smoother / settings sweep (bench/sweep_smoother.py; M4)")
    out(f"variant {cfg['model']['variant']}; base overrides "
        f"{args.base_set}; clean windows configs/clean_windows.json")
    out("per kind: rms0 / |lag| / rmsL (deg, frames, deg) and d2/o = "
        "geomean second-diff RMS causal / oracle over windows x the "
        "kind's angles; gates = bench/grade.py S-type hard-gate "
        "failures (teleport count, worst step deg)")
    hdr = (f"{'config':>26} " + " ".join(
        f"{k + ':rms0':>11} {'|lag|':>5} {'rmsL':>6} {'d2/o':>6}"
        for k in KIND_ANGLES) + ("  gates" if args.gates else ""))

    if args.mode == "configs":
        confs = json.loads(Path(args.configs).read_text())
        out(hdr)
        for name, sets in confs.items():
            df = run_clean(args.base_set + sets, work / f"{name}.csv")
            mt = {k: kind_metrics(df, k) for k in KIND_ANGLES}
            g = ""
            if args.gates:
                f, t, w = run_gates(args.base_set + sets,
                                    work / f"{name}__grade.txt")
                g = f"  {f} fail ({t} tele), wstep {w:.2f}"
            out(f"{name:>26} " + " ".join(
                f"{mt[k]['rms0']:>11.3f} {mt[k]['lag']:>5.2f} "
                f"{mt[k]['rmsL']:>6.3f} {mt[k]['d2o']:>6.3f}"
                for k in KIND_ANGLES) + g)
    else:
        if args.grid is None:
            if args.smoother != "quat_one_euro":
                sys.exit("[ERROR] --grid is required for smoother "
                         f"{args.smoother}")
            grid = {"min_cutoff": [float(x) for x in
                                   args.min_cutoffs.split(",")],
                    "beta": [float(x) for x in args.betas.split(",")]}
            fixed = {"d_cutoff": dc}
        else:
            grid = json.loads(args.grid)
            fixed = json.loads(args.fixed) if args.fixed else {}
        names = list(grid)
        if args.smoother == "quat_one_euro" and args.grid is None:
            mcs, bts = grid["min_cutoff"], grid["beta"]
            out(f"grid: min_cutoff {mcs} Hz x beta {bts} (per rad/s) for "
                f"every kind at once; d_cutoff {dc} Hz (config "
                "filter.d_cutoff, the v1 landmark One-Euro value)")
        else:
            out(f"grid ({args.smoother}): " + " x ".join(
                f"{n} {grid[n]}" for n in names) + f"; fixed {fixed}; "
                "every kind at the same point")
        out(hdr)
        df0 = run_clean(args.base_set + [f"{S2}.smoother=none"],
                        work / "none.csv")
        none_rows = {k: kind_metrics(df0, k) for k in KIND_ANGLES}
        out(f"{'none':>26} " + " ".join(
            f"{none_rows[k]['rms0']:>11.3f} {none_rows[k]['lag']:>5.2f} "
            f"{none_rows[k]['rmsL']:>6.3f} {none_rows[k]['d2o']:>6.3f}"
            for k in KIND_ANGLES))
        points = list(itertools.product(*(grid[n] for n in names)))

        def label(pt):
            if args.smoother == "quat_one_euro" and args.grid is None:
                return f"qoe mc={pt[0]} b={pt[1]}"
            tag = {"quat_one_euro": "qoe", "tangent_kf": "kf"}.get(
                args.smoother, args.smoother)
            return f"{tag} " + " ".join(f"{n}={_fmt(v)}"
                                        for n, v in zip(names, pt))

        def run_point(pt):
            params = {k: dict(fixed, **dict(zip(names, pt)))
                      for k in KIND_ANGLES}
            sets = args.base_set + [
                f"{S2}.smoother={args.smoother}",
                f"{S2}.smoother_params={json.dumps(params)}"]
            fname = "_".join(_fmt(v) for v in pt)
            df = run_clean(sets, work / f"{args.smoother}_{fname}.csv")
            return {k: kind_metrics(df, k) for k in KIND_ANGLES}

        if args.jobs > 1:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(args.jobs) as ex:
                mts = list(ex.map(run_point, points))
        else:
            mts = [run_point(pt) for pt in points]
        rows = []
        for pt, mt in zip(points, mts):
            rows.append((pt, mt))
            out(f"{label(pt):>26} " + " ".join(
                f"{mt[k]['rms0']:>11.3f} {mt[k]['lag']:>5.2f} "
                f"{mt[k]['rmsL']:>6.3f} {mt[k]['d2o']:>6.3f}"
                for k in KIND_ANGLES))
        out()
        out("selection (rule in the module docstring and D-029):")
        pick = choose(rows, none_rows)
        chosen = {}
        edge = lambda pt: [n for n, v in zip(names, pt)
                           if len(grid[n]) > 1
                           and v in (min(grid[n]), max(grid[n]))]
        for k, (pt, why) in pick.items():
            chosen[k] = dict(fixed, **dict(zip(names, pt)))
            mt = dict(rows)[pt][k]
            e = edge(pt)
            out(f"  {k:>6}: " + " ".join(f"{n} {_fmt(v)}" for n, v in
                                          zip(names, pt))
                + f" -> rms0 {mt['rms0']:.3f} |lag| {mt['lag']:.2f} rmsL "
                f"{mt['rmsL']:.3f} d2/o {mt['d2o']:.3f}  [{why}]"
                + (f" GRID EDGE in {e}" if e else ""))
        out(f"chosen smoother_params: {json.dumps(chosen)}")
        if args.smoother != "quat_one_euro" or args.grid is not None:
            out()
            out(f"alternative lag-weighted rule (informational): among "
                f"d2/o <= 1.5, min rms0 + {LAG_WEIGHT_DEG} deg x |lag|")
            alt = choose_lag_weighted(rows)
            for k, pt in alt.items():
                if pt is None:
                    out(f"  {k:>6}: no feasible point")
                    continue
                mt = dict(rows)[pt][k]
                out(f"  {k:>6}: " + " ".join(f"{n} {_fmt(v)}" for n, v in
                                              zip(names, pt))
                    + f" -> rms0 {mt['rms0']:.3f} |lag| {mt['lag']:.2f} "
                    f"rmsL {mt['rmsL']:.3f} d2/o {mt['d2o']:.3f} score "
                    f"{mt['rms0'] + LAG_WEIGHT_DEG * mt['lag']:.3f}"
                    + (f" GRID EDGE in {edge(pt)}" if edge(pt) else ""))
    if args.out_txt:
        Path(args.out_txt).write_text("\n".join(lines) + "\n")
        print(f"[+] {args.out_txt}")


if __name__ == "__main__":
    main()

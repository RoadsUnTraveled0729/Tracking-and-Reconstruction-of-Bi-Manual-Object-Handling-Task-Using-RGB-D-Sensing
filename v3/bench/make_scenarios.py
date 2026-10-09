#!/usr/bin/env python3
"""Build the S-type masked scenarios on the V3 extraction and fill the
manifest (windows, expected non-measured groups, derived teleport
budgets). Adapted from v1's kinematics/make_masked_dataset.py: same
durations and landmark choices, NEW frame windows on the V3 extraction
(v1 frame indices are never reused, plan risk).

Window placement (auto-proposed; flagged for human confirmation in
D-019): anchored at fixed fractions of the run, disjoint, all inside
[warmup_frames, N-40]. The whole extraction is landmark-complete
(dataset/phase3_extraction.txt), so any span is a clean span; the
fractions spread the windows across different task phases.

Teleport budgets (D-003): per-angle 1.5 x p99.9 of the CLEAN run's
per-frame steps, where the clean run is the full causal pipeline
(filter + baseline solver) on the unmasked extraction -- derived here,
recorded in the manifest, never hardcoded.

Truth for grading is NOT stored (derived at grade time by running the
identical pipeline on the unmasked CSV).

Run: /home/luo/anaconda3/bin/python v3/bench/make_scenarios.py
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

V3_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V3_ROOT.parent
sys.path.insert(0, str(V3_ROOT))

from bench.metrics import (ANGLE_NAMES, TWIST_ANGLES, angle_steps,  # noqa: E402
                           teleport_budget, twist_step_valid)
from strategies.strategy_base import build                            # noqa: E402
import strategies.baseline_hold                                       # noqa: E402,F401
from replay.runner import run_csv                                    # noqa: E402
from bench.paths import repo_path, repo_rel                          # noqa: E402

ALL = ["left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
       "left_wrist", "right_wrist", "left_hip", "right_hip"]

# name, landmarks, duration, anchor fraction, expected non-measured
# groups while masked (v1 occlusion semantics: wrist costs twist+elbow;
# elbow costs the whole arm; hip costs the root; a shoulder costs its
# arm while the root survives via the other shoulder; pose loss costs
# everything)
SCENARIOS = [
    ("wrist_short", ["right_wrist"], 3, 0.30,
     ["R_twist", "R_elbow"]),
    ("wrist_long", ["right_wrist"], 45, 0.45,
     ["R_twist", "R_elbow"]),
    ("elbow_long", ["right_elbow"], 45, 0.60,
     ["R_swing", "R_twist", "R_elbow"]),
    ("hip", ["left_hip"], 30, 0.70,
     ["root"]),
    ("pose_loss", ALL, 10, 0.79,
     ["root", "R_swing", "R_twist", "R_elbow",
      "L_swing", "L_twist", "L_elbow"]),
    ("root_ref", ["right_shoulder"], 30, 0.88,
     ["R_swing", "R_twist", "R_elbow"]),
]


def mask(df, landmarks, start, stop):
    out = df.copy()
    rows = (out["frame"] >= start) & (out["frame"] < stop)
    for name in landmarks:
        out.loc[rows, [f"{name}_x", f"{name}_y", f"{name}_z"]] = np.nan
    return out


def oracle_union_steps(args, cfg, base_path, warmup):
    """D-033: per-frame wrap-aware steps of the oracle angles (offline
    zero-phase filter + stateless solve, bench/oracle.py) over the base
    CSV after warmup and over each clean window (stop inclusive) of the
    same variant. Steps are taken within each segment only, and a step
    touching a NaN (unsolvable) oracle frame is dropped, so no step
    spans two recordings or a gap. Returns ((N, 13) steps, note)."""
    from bench.oracle import (oracle_angles, require_twist_min_bend,
                              twist_observable)
    min_bend = require_twist_min_bend(cfg["budget"], "config budget")
    variant = args.variant
    meta_p = Path(base_path).with_suffix(".meta.json")
    if variant is None and meta_p.exists():
        variant = json.loads(meta_p.read_text()).get("variant")
    variant = variant or cfg["model"]["variant"]
    segs = []
    orc = oracle_angles(str(base_path), cfg)
    segs.append(("pinned", orc[orc["frame"] >= warmup]))
    wins = json.loads(Path(args.windows_file).read_text())
    if not wins.get("stop_inclusive"):
        raise ValueError("clean_windows.json must declare stop_inclusive")
    for w in wins["windows"]:
        csv = (Path(args.clean_csv_dir)
               / f"extraction_{Path(w['bag']).stem}__{variant}.csv")
        o = oracle_angles(str(csv), cfg)
        segs.append((w["name"], o[(o["frame"] >= int(w["start"]))
                                  & (o["frame"] <= int(w["stop"]))]))
    parts = []
    for name, seg in segs:
        st = angle_steps(seg[list(ANGLE_NAMES)].to_numpy(dtype=float))
        keep = np.all(np.isfinite(st), axis=1)
        # D-033 twist gating: a twist step enters the derivation only
        # when the oracle solve had the twist observable (solver
        # twist_ok) on both frames; masked steps become NaN and are
        # skipped by teleport_budget's nanpercentile
        valid = twist_step_valid(*twist_observable(
            seg, min_bend))
        st = np.where(valid, st, np.nan)[keep]
        parts.append(st)
        ntw = [int(np.isfinite(st[:, ANGLE_NAMES.index(a)]).sum())
               for a in TWIST_ANGLES]
        print(f"  oracle steps {name:>18}: {len(st)} (twist-observable "
              f"r {ntw[0]}, l {ntw[1]})")
    steps = np.vstack(parts)
    ntw = [int(np.isfinite(steps[:, ANGLE_NAMES.index(a)]).sum())
           for a in TWIST_ANGLES]
    note = (f"D-033: 1.5 x p99.9 of ORACLE per-frame steps (bench/oracle.py"
            f" zero-phase angles) over the base CSV (warmup {warmup} "
            f"excluded) UNION the clean windows of "
            f"{Path(args.windows_file).name} for variant {variant} "
            f"({len(steps)} steps); twist steps only where the oracle "
            f"twist_ok is true AND the elbow bend is >= "
            f"{min_bend} deg on both "
            f"frames (r_twist {ntw[0]}, l_twist "
            f"{ntw[1]} steps); the same mask gates the teleport count")
    return steps, note


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base-csv", default=str(
        V3_ROOT / "output/extraction_recording_20260224_083945.csv"))
    ap.add_argument("--config", default=str(V3_ROOT / "configs/default.json"))
    ap.add_argument("--manifest", default=str(
        V3_ROOT / "configs/scenarios_20260224.json"))
    ap.add_argument("--out-manifest", default=None,
                    help="where to write the filled manifest (default: "
                         "--manifest, in place); --manifest is the "
                         "template read for the fixed fields")
    ap.add_argument("--out-dir", default=str(V3_ROOT / "output/scenarios"))
    ap.add_argument("--budget-source", default="clean_run",
                    choices=("clean_run", "oracle_union"),
                    help="clean_run (D-003): steps of the causal baseline "
                         "run on the base CSV; oracle_union (D-033): steps "
                         "of the offline zero-phase oracle (bench/oracle.py)"
                         " over the base CSV (post-warmup) UNION the clean "
                         "windows of --windows-file")
    ap.add_argument("--windows-file",
                    default=str(V3_ROOT / "configs/clean_windows.json"))
    ap.add_argument("--clean-csv-dir", default=str(V3_ROOT / "output/clean"))
    ap.add_argument("--variant", default=None,
                    help="oracle_union: variant of the clean-window "
                         "extractions; default the base CSV's meta.json "
                         "variant, else config model.variant")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text())
    manifest = json.loads(Path(args.manifest).read_text())
    warmup = json.loads((V3_ROOT / "configs/bench.json").read_text())[
        "latency"]["warmup_frames"]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    base_path = repo_path(args.base_csv)
    base = pd.read_csv(base_path)
    n = int(base["frame"].max()) + 1

    # windows: anchored, then checked disjoint and in-bounds
    windows = {}
    for name, lms, dur, frac, groups in SCENARIOS:
        start = int(round(frac * n))
        windows[name] = (start, start + dur)
        assert warmup <= start and start + dur <= n - 40, name
    spans = sorted(windows.values())
    for a, b in zip(spans, spans[1:]):
        assert a[1] <= b[0], f"overlap: {a} {b}"

    if args.budget_source == "clean_run":
        # clean run -> derived teleport budgets
        print("clean baseline run for teleport budgets...")
        strat = build("baseline_hold", cfg)
        clean = run_csv(str(base_path), cfg, strat)
        steps = angle_steps(clean[list(ANGLE_NAMES)].to_numpy())
        budgets = teleport_budget(steps[warmup:],
                                  cfg["budget"]["teleport_safety"])
        budget_note = (f"1.5 x p99.9 of clean-run per-frame steps, warmup "
                       f"{warmup} excluded, full causal pipeline (filter "
                       "+ baseline solver)")
    else:
        steps, budget_note = oracle_union_steps(args, cfg, base_path,
                                                warmup)
        budgets = teleport_budget(steps, cfg["budget"]["teleport_safety"])

    scenarios_out = []
    for name, lms, dur, frac, groups in SCENARIOS:
        start, stop = windows[name]
        out_csv = out_dir / f"masked_{name}.csv"
        mask(base, lms, start, stop).to_csv(out_csv, index=False,
                                            float_format="%.6f")
        scenarios_out.append({
            "name": name, "type": "S", "source": "raw",
            "landmarks": lms if len(lms) < 8 else ["ALL"],
            "duration_frames": dur, "start": start, "stop": stop,
            "expected_groups": groups, "mode": "nan",
            "csv": repo_rel(out_csv),
        })
        print(f"  {name:12s} frames {start}-{stop - 1} "
              f"({dur:2d}) {lms if len(lms) < 8 else 'ALL'}")

    git_commit = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
        capture_output=True, text=True).stdout.strip()
    # repository-relative when under the repo (M3, D-028); consumers
    # resolve with bench.paths.repo_path
    manifest["base_csv"] = repo_rel(base_path)
    meta_p = base_path.with_suffix(".meta.json")
    if meta_p.exists():
        manifest["variant"] = json.loads(meta_p.read_text()).get("variant")
    manifest["scenarios"] = scenarios_out
    # full precision: rounding to 4 decimals would flatten the 1e-9
    # floor for identically-zero angles back to 0 (see teleport_budget)
    manifest["teleport_budget_deg"] = {
        an: float(b) for an, b in zip(ANGLE_NAMES, budgets)}
    manifest["teleport_budget_note"] = (
        budget_note)
    manifest["teleport_budget_source"] = args.budget_source
    # D-033: graders apply the same twist observability mask to the
    # teleport count when the manifest declares it (clean_run manifests
    # keep the ungated D-003 count)
    manifest["teleport_twist_gate"] = (
        "oracle_twist_ok" if args.budget_source == "oracle_union"
        else "none")
    if args.budget_source == "oracle_union":
        from bench.oracle import require_twist_min_bend
        manifest["twist_min_bend_deg"] = require_twist_min_bend(
            cfg["budget"], "config budget")
    manifest["derived_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    manifest["derived_from_commit"] = git_commit
    manifest["_comment"] = ("S-type scenarios on the V3 extraction. "
                            "Windows auto-proposed at fixed run "
                            "fractions (D-019, pending human "
                            "confirmation); teleport budgets derived, "
                            "never hardcoded (D-003). low_conf mode "
                            "deferred until gate thresholds exist "
                            "(D-017).")
    out_manifest = args.out_manifest or args.manifest
    Path(out_manifest).write_text(json.dumps(manifest, indent=2))
    print(f"manifest: {out_manifest}")
    print("teleport budgets (deg):",
          json.dumps(manifest["teleport_budget_deg"]))


if __name__ == "__main__":
    main()

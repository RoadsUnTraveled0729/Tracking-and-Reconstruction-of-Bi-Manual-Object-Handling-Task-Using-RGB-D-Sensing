#!/usr/bin/env python3
# Filename: v2/integration/validate_v2_r5.py
"""R5 real-time probe validation (PoC-weight, not parity-weight).

Checks the dumps of a `run_v2.py --source bag --probe-r5 --dump` run
against the FROZEN offline references of the R5 evaluation round
(eval/output/recovery_r5/). The bar is the plan's: the stack sustains
real time, the live angles track the offline recovery reference within
the established causal bounds, and every ported feature demonstrably
FIRES where the offline study says it should. Exact parity is not the
goal (live landmarks pass a causal One-Euro filter; offline used the
zero-phase chain).

Run:
    python v2/integration/run_v2.py --source bag --probe-r5 --dump
    python v2/integration/validate_v2_r5.py
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "v2/output"
REF = ROOT / "eval/output/recovery_r5"          # default; --alias overrides

ANGLE_COLS = ["root_ex", "root_ey", "root_ez", "Rsh_y", "Rsh_z",
              "Rsh_tau", "Rel_y", "Rel_z", "Lsh_y", "Lsh_z", "Lsh_tau",
              "Lel_y", "Lel_z"]
GROUPS = {"root": [0, 1, 2], "R_shoulder": [3, 4, 5], "R_elbow": [6, 7],
          "L_shoulder": [8, 9, 10], "L_elbow": [11, 12]}
N_FRAMES = 2099
FRAME_BUDGET_MS = 1000.0 / 30.0

checks = []
check_records = []


def check(name, ok, detail):
    checks.append(bool(ok))
    check_records.append({"name": name, "passed": bool(ok), "detail": detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


def wrap(d):
    return (np.asarray(d, float) + 180.0) % 360.0 - 180.0


def paired_angles(live, ref, lag, need, tags, columns):
    """Pair live frame f with reference f-lag; positive lag is live delay.

    Each side must independently be measured at its paired frame. Join by
    frame ID, not row position: consumers can miss different source frames.
    """
    shifted_ref = ref.copy()
    shifted_ref["frame"] = shifted_ref["frame"] + lag
    pairs = live.merge(shifted_ref, on="frame", suffixes=("_l", "_r"),
                       validate="one_to_one")
    a = pairs[[f"a{i}" for i in range(13)]].to_numpy(float)
    b = pairs[ANGLE_COLS].to_numpy(float)
    valid = ((pairs["mask"].to_numpy(int) & need) == need)
    valid &= ((pairs["live_mask"].to_numpy(int) & need) == need)
    for i in tags:
        valid &= pairs[f"tag_{i}_l"].to_numpy(int) == 0
        valid &= pairs[f"tag_{i}_r"].to_numpy(int) == 0
    valid &= np.isfinite(a[:, columns]).all(axis=1)
    valid &= np.isfinite(b[:, columns]).all(axis=1)
    return a[valid], b[valid], pairs.loc[valid, "frame"].to_numpy(int)


def compare_angles(live, ref, one_handed=False):
    if one_handed:
        need, tags = 14, range(1, 4)
        groups = {g: GROUPS[g] for g in ("R_shoulder", "R_elbow")}
    else:
        need, tags, groups = 127, range(7), GROUPS
    columns = sorted(sum(groups.values(), []))
    candidates = []
    for lag in range(-10, 11):
        a, b, frames = paired_angles(live, ref, lag, need, tags, columns)
        median = (float(np.median(np.abs(wrap(a-b))[:, columns]))
                  if len(frames) else None)
        candidates.append({"lag_frames": lag, "paired_frames": len(frames),
                           "pooled_median_deg": median})
    eligible = [c for c in candidates if c["pooled_median_deg"] is not None]
    report = {"pairing": "live frame f versus reference frame f-lag",
              "one_handed": one_handed, "candidates": candidates,
              "lag_frames": None, "groups": {}, "paired_live_frames": []}
    if not eligible:
        return report
    # Preserve historical ascending-lag tie behavior; flat minima do not
    # establish a unique physical delay.
    best = min(eligible, key=lambda c: c["pooled_median_deg"])
    report.update(best)
    a, b, frames = paired_angles(live, ref, best["lag_frames"], need,
                                tags, columns)
    err = np.abs(wrap(a-b))
    report["paired_live_frames"] = frames.tolist()
    report["per_angle"] = {ANGLE_COLS[i]: {
        "median_deg": float(np.median(err[:, i])),
        "p95_deg": float(np.percentile(err[:, i], 95))}
        for i in columns}
    for group, idx in groups.items():
        report["groups"][group] = {
            "median_deg": float(np.median(err[:, idx])),
            "p95_deg": float(np.percentile(err[:, idx], 95))}
    report["worst_group_median_deg"] = max(
        g["median_deg"] for g in report["groups"].values())
    report["worst_group_p95_deg"] = max(
        g["p95_deg"] for g in report["groups"].values())
    return report


def input_manifest(directories):
    return [{"path": str(p.resolve()), "bytes": p.stat().st_size,
             "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
            for directory, names in directories for name in names
            for p in [directory / name]]


def main():
    global OUT, REF, N_FRAMES
    checks.clear()
    check_records.clear()
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--alias", default="r5",
                    help="offline reference eval/output/recovery_<alias>/ "
                         "(default r5); the frame count is read from it")
    ap.add_argument("--one-handed", action="store_true",
                    help="the task uses one hand (rail recording): the "
                         "left-hand estimate and episode checks are "
                         "reported but not required")
    ap.add_argument("--input-dir", type=Path, default=OUT)
    ap.add_argument("--reference-dir", type=Path)
    ap.add_argument("--report-json", type=Path)
    args = ap.parse_args()
    OUT = args.input_dir
    REF = args.reference_dir or ROOT / f"eval/output/recovery_{args.alias}"
    live = pd.read_csv(OUT / "v2_person_dump.csv")
    obj = pd.read_csv(OUT / "v2_object_dump.csv")
    merge = pd.read_csv(OUT / "v2_integrate_dump.csv")
    ref = pd.read_csv(REF / "angles_recovery.csv")
    fm = pd.read_csv(REF / "failure_mask.csv")
    eps = json.loads((REF / "grip_episodes.json").read_text())
    N_FRAMES = int(fm["frame"].max()) + 1

    # 1. real-time sustained
    check("person coverage", len(live) >= N_FRAMES - 10,
          f"{len(live)}/{N_FRAMES} frames consumed")
    p99 = float(np.percentile(live["compute_ms"], 99))
    check("person compute p99 in budget", p99 < FRAME_BUDGET_MS,
          f"{p99:.1f} ms vs {FRAME_BUDGET_MS:.1f} ms")
    op99 = float(np.percentile(obj["compute_ms"], 99))
    check("object compute p99 in budget", op99 < FRAME_BUDGET_MS,
          f"{op99:.1f} ms")
    iv = np.diff(merge["mono"].to_numpy(float)) * 1e3
    check("merger cadence p99 < 40 ms", np.percentile(iv, 99) < 40.0,
          f"{np.percentile(iv, 99):.1f} ms over {len(merge)} ticks")

    # 2. live angles track the offline recovery reference (causal
    #    bounds; both indexed by bag frame, xcorr for residual lag)
    angle_report = compare_angles(live, ref, args.one_handed)
    lag = angle_report["lag_frames"]
    has_pairs = lag is not None
    check("causal lag <= 4 frames", has_pairs and abs(lag) <= 4,
          f"lag {lag} frames; see JSON for every lag and sample count")
    worst_med = angle_report.get("worst_group_median_deg")
    worst_p95 = angle_report.get("worst_group_p95_deg")
    check("worst group median < 5 deg on clean frames",
          has_pairs and worst_med < 5.0,
          f"{worst_med} deg ({len(angle_report['paired_live_frames'])} paired frames)")
    check("worst group p95 < 20 deg on clean frames",
          has_pairs and worst_p95 < 20.0, f"{worst_p95} deg")

    # 3. the ported features fire where the offline study fired
    both = live["rec_right"].sum() > 0 and live["rec_left"].sum() > 0
    check("wrist estimates published (both hands)"
          if not args.one_handed else
          "wrist estimates published (working hand)",
          both if not args.one_handed else live["rec_right"].sum() > 0,
          f"rec R {int(live['rec_right'].sum())} / "
          f"L {int(live['rec_left'].sum())} frames")
    fmm = live.merge(fm, on="frame")
    lw = ((fmm["fail_arm_L"] == 1)
          & ((fmm["tag_5"] == 2) | (fmm["tag_6"] == 2))).sum()
    rw = ((fmm["fail_arm_R"] == 1)
          & ((fmm["tag_2"] == 2) | (fmm["tag_3"] == 2))).sum()
    check("CONSTRAINED output inside offline failure windows",
          (lw > 0) if not args.one_handed else (rw > 0),
          f"L {int(lw)} frames, R {int(rw)} frames")
    for side, col in (("left", "rec_left"), ("right", "rec_right")):
        span = np.zeros(N_FRAMES, bool)
        for e in eps["episodes"][side]:
            span[e["start"]:e["stop"] + 1] = True
        if span.sum() == 0:
            print(f"[skip] {side} estimates cover offline episodes: "
                  f"no offline episode on this side")
            continue
        rec = np.zeros(N_FRAMES, bool)
        f_idx = live["frame"].to_numpy(int)
        rec[f_idx[live[col].to_numpy(bool)]] = True
        cov = (rec & span).sum() / max(span.sum(), 1)
        check(f"{side} estimates cover offline episodes", cov > 0.6,
              f"{cov * 100:.0f} percent of {int(span.sum())} "
              f"offline holding frames")
    check("object live coverage", (obj["live"] == 1).sum() > 0.90 * len(obj),
          f"{int((obj['live'] == 1).sum())}/{len(obj)}")
    tag_ticks = (merge["tags"] != 0).sum()
    check("tags reach the merger output", tag_ticks > 200,
          f"{int(tag_ticks)} ticks with non-measured tags")

    print(f"\n{'ALL PASS' if all(checks) else 'FAILURES PRESENT'} "
          f"({sum(checks)}/{len(checks)})")
    print("(old-recording regression: run_v2.py --source bag --dump "
          "+ validate_v2.py, flags off)")
    if args.report_json:
        report = {"alias": args.alias, "angle_comparison": angle_report,
                  "checks": check_records,
                  "inputs": input_manifest([
                      (OUT, ["v2_person_dump.csv", "v2_object_dump.csv",
                             "v2_integrate_dump.csv"]),
                      (REF, ["angles_recovery.csv", "failure_mask.csv",
                             "grip_episodes.json"])])}
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    sys.exit(0 if all(checks) else 1)


if __name__ == "__main__":
    main()

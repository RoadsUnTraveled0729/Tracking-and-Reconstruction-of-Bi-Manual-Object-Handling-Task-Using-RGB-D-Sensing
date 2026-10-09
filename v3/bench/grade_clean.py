#!/usr/bin/env python3
"""Clean-window bench: smoothness and agreement of the causal V3 path
against the offline zero-phase oracle (D-024) and against v1 (D-026).

For every clean window (configs/clean_windows.json, D-025) x strategy
x smoother, the WHOLE extraction CSV is replayed through the causal
pipeline (replay.runner.run_csv: CausalLandmarkFilter -> Unity flip
-> strategy) and through the oracle (bench/oracle.py, whole
recording, zero phase), then both are sliced to the window. Per angle:
RMS vs oracle at lag 0, best lag (|s| <= max_lag, positive = causal
lags the oracle) and RMS at that lag, second-difference RMS of the
causal output, the oracle and the raw (unfiltered, stateless) solve.
Per window x strategy: teleport count against the S-type manifest
budgets (informational here: those budgets were derived on the
2026-02-24 recording), joint-limit violation fraction (informational
while every limit is null), bone-length p95 deviation of the filtered
landmarks the strategy received against the oracle's median bone
lengths in the window.

v1 agreement (right arm, the windows that have a v1 series in
eval/pipeline_smoothness): V3 causal, V3 oracle and V3 raw against
the v1 film angles (MediaPipe, offline zero-phase filter), and V3
raw against the v1 raw_gated angles; the D-018 offset (pinned table
dataset/phase3_v1_offset_table.txt, measured for rtmpose-m) is
subtracted, the best lag is found on the offset-corrected series, and
the circular mean and circular std of the residual at that lag are
reported. Frame alignment V3 vs defence series: offset 0 (D-025).

None of this is external truth: the oracle is the same detector
output smoothed with look-ahead, v1 is a different detector. The
three D-003 hard gates are NOT evaluated here (grade.py on the S-type
scenarios does that); the clean metrics only rank (bench.json
ranking.clean_metrics, D-026).

Run: /home/luo/anaconda3/bin/python v3/bench/grade_clean.py
       --strategies baseline_hold,s2_quat_prediction [--smoothers none]
       [--windows all] [--variant rtmpose-m]
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

V3_ROOT = Path(__file__).resolve().parents[1]
REPO = V3_ROOT.parent
sys.path.insert(0, str(V3_ROOT))

from bench.paths import apply_overrides, repo_path                    # noqa: E402
from bench import metrics as m                       # noqa: E402
from bench.oracle import (oracle_angles, raw_angles,   # noqa: E402
                          require_twist_min_bend, twist_observable)
from core.skeleton import V1_LANDMARKS               # noqa: E402
from replay.runner import run_csv                    # noqa: E402
from strategies.strategy_base import build           # noqa: E402
import strategies.baseline_hold                      # noqa: E402,F401
import strategies.s2_quat_prediction                 # noqa: E402,F401

from strategies.smoother_base import SMOOTHERS     # noqa: E402
# smoothers apply to s2_quat_prediction only; other strategies run
# with "none" and skip the rest
# v1 series per clean window: eval/pipeline_smoothness/
# compare_film_vs_live.py PAGES (page 16 = right_elbow 180-540,
# page 14 = 180042 3-109); columns <v1angle>_<series>
V1_SERIES = {"right_elbow": "eval/pipeline_smoothness/series_p16.csv",
             "180042": "eval/pipeline_smoothness/series_p14.csv"}
V1_ANGLES = {"sh_y": "r_swing_y", "sh_z": "r_swing_z",
             "sh_twist": "r_twist", "el_y": "r_elbow_y",
             "el_z": "r_elbow_z"}
RIGHT_ARM = ("r_swing_y", "r_swing_z", "r_twist", "r_elbow_y")
# V3-vs-v1 per-angle offset table per model variant: offsets are a
# property of the detector, so a variant without its own table gets no
# v1-agreement rows (D-018 for rtmpose-m; D-028 for the M3 pin; D-034
# for rtmpose-l)
V1_OFFSET_TABLES = {"rtmpose-m": "dataset/phase3_v1_offset_table.txt",
                    "rtmpose-x_yolox-m":
                        "dataset/phase5_v1_offset_table.txt",
                    "rtmpose-l":
                        "dataset/phase5_v1_offset_table__rtmpose-l.txt"}


def sha16(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def read_offsets(path):
    """D-018 per-angle offsets from the pinned offset-table text."""
    off = {}
    for line in Path(path).read_text().splitlines():
        parts = line.split()
        if len(parts) == 6 and parts[0] in m.ANGLE_NAMES:
            off[parts[0]] = float(parts[3])
    missing = [a for a in m.ANGLE_NAMES if a not in off]
    if missing:
        raise ValueError(f"offset table {path} lacks {missing}")
    return np.array([off[a] for a in m.ANGLE_NAMES])


def window_rows(tab, s0, s1, what):
    w = tab.set_index("frame").loc[s0:s1]
    if len(w) != s1 - s0 + 1 or not np.array_equal(
            w.index.to_numpy(), np.arange(s0, s1 + 1)):
        raise ValueError(f"{what}: frames {s0}-{s1} not all present")
    return w


def angles_of(w):
    return w[list(m.ANGLE_NAMES)].to_numpy(dtype=float)


def points_of(w):
    return {n: w[[f"{n}_f{a}" for a in "xyz"]].to_numpy(dtype=float)
            for n in V1_LANDMARKS}


def bone_p95(points, ref):
    """p95 fractional bone-length deviation per bone over the frames
    where both ends exist (causal-filter rejections leave NaN rows)."""
    L = m.bone_lengths(points)
    return np.array([
        m.bone_length_deviation(L[np.isfinite(L[:, b]), b:b + 1],
                                ref[b:b + 1])["p95"][0]
        if np.isfinite(L[:, b]).any() else np.nan
        for b in range(L.shape[1])])


def v1_agreement(x, ref, offset, max_lag):
    """x, ref: (T,) V3 and v1 series; offset: D-018 value (deg).
    Returns (lag, residual circular mean, residual circular std)."""
    xc = x - offset
    lag, _ = m.best_lag(xc, ref, max_lag=max_lag, criterion="rms")
    a, b = m.lag_overlap(xc[:, None], ref[:, None], lag)
    mu, sd = m.circular_residual(a, b)
    return int(lag), float(mu[0]), float(sd[0])


def angle_means(df):
    """Per (strategy, smoother): means over windows x the 13 angles of
    rms0, |best lag|, rmsL and second-diff RMS causal, plus d2/o = the
    geometric mean of causal / oracle second-diff RMS. Angles that are
    identically zero in the oracle (second-diff RMS oracle <= 1e-6
    deg/frame^2, the D-032 degenerate threshold; float round-off leaves
    ~1e-15 on v1's elbow_z pair) are excluded from every column, since
    they contribute 0 to every smoother and 0/0 to the ratio (M5,
    D-038). Rows in input order."""
    keep = df[df["second_diff_rms_oracle"] > 1e-6]
    rows = []
    for (st, sm), d in keep.groupby(["strategy", "smoother"], sort=False):
        r = d["second_diff_rms_causal"] / d["second_diff_rms_oracle"]
        rows.append({"strategy": st, "smoother": sm, "n": len(d),
                     "rms0": float(d["rms_vs_oracle_lag0"].mean()),
                     "lag": float(d["best_lag"].abs().mean()),
                     "rmsL": float(d["rms_vs_oracle_best_lag"].mean()),
                     "d2c": float(d["second_diff_rms_causal"].mean()),
                     "d2o": float(np.exp(np.mean(np.log(r))))})
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--config", default=str(V3_ROOT / "configs/default.json"))
    ap.add_argument("--bench", default=str(V3_ROOT / "configs/bench.json"))
    ap.add_argument("--windows-file",
                    default=str(V3_ROOT / "configs/clean_windows.json"))
    ap.add_argument("--manifest", default=None,
                    help="teleport budgets; default: config "
                         "paths.scenario_manifest")
    ap.add_argument("--strategies", default="baseline_hold,s2_quat_prediction")
    ap.add_argument("--smoothers", default="none")
    ap.add_argument("--windows", default="all")
    ap.add_argument("--set", action="append", default=[],
                    help="config override key.path=json (repeatable)")
    ap.add_argument("--variant", default=None,
                    help="default: config model.variant")
    ap.add_argument("--csv-dir", default=str(V3_ROOT / "output/clean"))
    ap.add_argument("--v1-offsets", default=None,
        help="V3-vs-v1 offset table (bench/v1_offset_table.py output); "
             "default: V1_OFFSET_TABLES[variant] when the variant has "
             "one (rtmpose-m: D-018; others: D-028), else v1 agreement "
             "is skipped")
    ap.add_argument("--out-txt", default=None,
                    help="default dataset/phase5_clean__<variant>.txt "
                         "(the M2 rtmpose-m table is pinned as "
                         "dataset/phase5_clean_baseline.txt); '' = none")
    ap.add_argument("--out-csv", default=None,
                    help="default <csv-dir>/clean_grade__<variant>.csv")
    args = ap.parse_args()

    smoothers = args.smoothers.split(",")
    bad = [s for s in smoothers if s not in SMOOTHERS]
    if bad:
        sys.exit(f"[ERROR] unknown smoother(s) {bad}; available now: "
                 f"{sorted(SMOOTHERS)}")
    strat_names = args.strategies.split(",")
    cfg = apply_overrides(json.loads(Path(args.config).read_text()),
                          args.set)
    if args.variant is None:
        args.variant = cfg["model"]["variant"]
    if args.out_txt is None:
        args.out_txt = str(V3_ROOT / f"dataset/phase5_clean__{args.variant}.txt")
    bench = json.loads(Path(args.bench).read_text())
    max_lag = int(bench["ranking"]["clean_max_lag_frames"])
    clean_metrics = bench["ranking"]["clean_metrics"]
    wins = json.loads(Path(args.windows_file).read_text())
    if not wins.get("stop_inclusive"):
        sys.exit("[ERROR] clean_windows.json must declare stop_inclusive")
    windows = wins["windows"]
    if args.windows != "all":
        names = args.windows.split(",")
        unknown = set(names) - {w["name"] for w in windows}
        if unknown:
            sys.exit(f"[ERROR] unknown window(s) {sorted(unknown)}")
        windows = [w for w in windows if w["name"] in names]
    if args.manifest is None:
        args.manifest = str(repo_path(cfg["paths"]["scenario_manifest"]))
    man = json.loads(Path(args.manifest).read_text())
    budgets = np.array([man["teleport_budget_deg"][a] for a in m.ANGLE_NAMES])
    # D-033 twist gate, resolved once before any window runs: the bend
    # threshold is required when the gate is declared (D-006)
    tw_gate = man.get("teleport_twist_gate", "none")
    if tw_gate not in ("none", "oracle_twist_ok"):
        raise ValueError(f"unknown teleport_twist_gate {tw_gate!r}")
    tw_min_bend = (require_twist_min_bend(man, args.manifest)
                   if tw_gate == "oracle_twist_ok" else None)
    cfg["paths"]["scenario_manifest"] = args.manifest   # S2 caps (D-032)
    offsets = None
    off_path = args.v1_offsets or V1_OFFSET_TABLES.get(args.variant)
    if off_path is not None:
        offsets = read_offsets(V3_ROOT / off_path)
    limits = {k: cfg["joint_limits"][k] for k in m.ANGLE_NAMES}
    limits_all_null = all(v is None for v in limits.values())

    lines = []

    def out(s=""):
        print(s)
        lines.append(s)

    out("V3 clean-window bench (bench/grade_clean.py; D-024 oracle, "
        "D-025 windows, D-026 clean metrics)")
    out(f"variant {args.variant}; strategies {','.join(strat_names)}; "
        f"smoothers {','.join(smoothers)}; max_lag {max_lag} frames")
    if args.set or smoothers != ["none"]:
        s2c = cfg["strategy"]["s2_quat_prediction"]
        out(f"s2: warm_start {s2c.get('warm_start', False)}, step caps "
            f"{s2c.get('step_cap_source', 'fixed')}, smoother_params "
            f"{json.dumps(s2c.get('smoother_params'))}; bones.project "
            f"{cfg.get('bones', {}).get('project', False)}"
            + (f"; overrides {args.set}" if args.set else ""))
    o = cfg["oracle"]
    out(f"oracle: centered Hampel w{o['hampel_window']} k{o['hampel_k']} "
        f"floor {o['hampel_floor_m']} m, gap fill <= {o['max_gap']}, "
        f"Butterworth order {o['butter_order']} {o['cutoff_hz']} Hz "
        f"filtfilt, fs = 1/median(dt); whole recording, then window")
    out(f"teleport budgets: {Path(args.manifest).name} (derived "
        f"{man['derived_at']} on the 2026-02-24 recording; informational "
        "on clean windows)")
    out("joint limits: " + ("all null in default.json -> fraction not "
                            "defined (n/a)" if limits_all_null else "set"))
    out("units: angles and RMS in deg, second-diff RMS in deg/frame^2, "
        "lag in frames (+ = lags the reference), bone dev as fraction")
    out("NOT external truth: oracle = same detector smoothed with "
        "look-ahead; v1 = different detector (self-consistency only)")
    out(f"'*' after a lag: at the search bound +-{max_lag}, the true lag "
        "may be larger. Every replay starts at bag frame 0 (causal state "
        "from the stream start); a window starting before frame "
        f"{bench['latency']['warmup_frames']} (bench.json "
        "latency.warmup_frames) includes start-of-stream convergence")

    csv_rows = []
    scores = {s: {} for s in strat_names}
    for win in windows:
        stem = Path(win["bag"]).stem
        csv = Path(args.csv_dir) / f"extraction_{stem}__{args.variant}.csv"
        if not csv.exists():
            sys.exit(f"[ERROR] missing extraction {csv}; see README "
                     "'clean-window baselines'")
        meta_p = csv.with_suffix(".meta.json")
        if meta_p.exists():
            meta = json.loads(meta_p.read_text())
            if meta.get("variant") != args.variant:
                sys.exit(f"[ERROR] {meta_p} variant {meta.get('variant')} "
                         f"!= {args.variant}")
        s0, s1 = int(win["start"]), int(win["stop"])
        orc_full = oracle_angles(csv, cfg)
        fs = orc_full.attrs["fs_hz"]
        orc = window_rows(orc_full, s0, s1, "oracle")
        raw = window_rows(raw_angles(csv), s0, s1, "raw")
        O, R = angles_of(orc), angles_of(raw)
        if not (np.all(np.isfinite(O)) and np.all(np.isfinite(R))):
            sys.exit(f"[ERROR] {win['name']}: oracle or raw has NaN "
                     "angles inside the window (not a clean window)")
        # D-033: twist-gated teleport count when the manifest declares
        # it (mask from this window's oracle twist_ok)
        tvalid = (m.twist_step_valid(*twist_observable(orc, tw_min_bend))
                  if tw_gate == "oracle_twist_ok" else None)
        o_pts = points_of(orc)
        bone_ref = np.nanmedian(m.bone_lengths(o_pts), axis=0)
        d2_o, d2_r = m.second_diff_rms(O), m.second_diff_rms(R)
        bone_o = bone_p95(o_pts, bone_ref)
        bone_r = bone_p95(points_of(raw), bone_ref)
        v1 = None
        if win["name"] in V1_SERIES and (REPO / V1_SERIES[win["name"]]).exists():
            v1 = pd.read_csv(REPO / V1_SERIES[win["name"]])
            if not np.array_equal(v1["frame"].to_numpy(),
                                  np.arange(s0, s1 + 1)):
                sys.exit(f"[ERROR] {V1_SERIES[win['name']]} frames do not "
                         f"match window {s0}-{s1}")
        out()
        out(f"=== window {win['name']}: frames {s0}-{s1} ({s1 - s0 + 1}), "
            f"fs {fs:.3f} Hz, csv sha256 {sha16(csv)}.. ===")
        out(f"{'strategy':>18} {'smoother':>8} {'angle':>10} "
            f"{'rms0':>7} {'lag':>4} {'rmsL':>7} {'d2_caus':>8} "
            f"{'d2_orac':>8} {'d2_raw':>8} {'tele':>4}")
        agree_rows = []
        for sname in strat_names:
            for smoother in smoothers:
                if smoother != "none" and sname != "s2_quat_prediction":
                    continue
                scfg = apply_overrides(cfg, [
                    f"strategy.s2_quat_prediction.smoother=\"{smoother}\""])
                caus_full = run_csv(csv, scfg, build(sname, scfg))
                caus = window_rows(caus_full, s0, s1, sname)
                A = angles_of(caus)
                rms0 = m.rms_vs_ref(A, O)
                lags, rmsl = m.best_lag(A, O, max_lag=max_lag)
                d2_c = m.second_diff_rms(A)
                tele = m.teleport_count(m.angle_steps(A), budgets, tvalid)
                c_pts = points_of(caus)
                bone_c = bone_p95(c_pts, bone_ref)
                jl = m.joint_limit_violations(A, limits)
                jl_frac = (float("nan") if limits_all_null
                           else jl["fraction"])
                st = caus[[f"status_{g}" for g in m.GROUP_NAMES]].to_numpy()
                nonmeas = (st != m.MEASURED).sum(axis=0)
                nonmeas_by_angle = np.empty(len(m.ANGLE_NAMES), dtype=int)
                for g, idx in enumerate(m.GROUP_ANGLES):
                    nonmeas_by_angle[list(idx)] = nonmeas[g]
                miss = caus["n_missing"].to_numpy()
                for j, an in enumerate(m.ANGLE_NAMES):
                    mark = "*" if abs(int(lags[j])) == max_lag else " "
                    out(f"{sname:>18} {smoother:>8} {an:>10} "
                        f"{rms0[j]:>7.3f} {lags[j]:>4d}{mark}{rmsl[j]:>7.3f} "
                        f"{d2_c[j]:>8.3f} {d2_o[j]:>8.3f} {d2_r[j]:>8.3f} "
                        f"{tele['per_angle_counts'][j]:>4d}")
                    row = {"window": win["name"], "variant": args.variant,
                           "strategy": sname, "smoother": smoother,
                           "angle": an, "rms_vs_oracle_lag0": rms0[j],
                           "best_lag": int(lags[j]),
                           "rms_vs_oracle_best_lag": rmsl[j],
                           "second_diff_rms_causal": d2_c[j],
                           "second_diff_rms_oracle": d2_o[j],
                           "second_diff_rms_raw": d2_r[j],
                           "teleport_frames_angle":
                               int(tele["per_angle_counts"][j]),
                           "teleport_budget_deg": budgets[j],
                           "teleport_frames_any": tele["count"],
                           "joint_limit_fraction": jl_frac}
                    for b, bn in enumerate(m.BONE_NAMES):
                        row[f"bone_p95_causal_{bn}"] = bone_c[b]
                        row[f"bone_p95_oracle_{bn}"] = bone_o[b]
                        row[f"bone_p95_raw_{bn}"] = bone_r[b]
                    row["non_measured_frames_group"] = int(
                        nonmeas_by_angle[j])
                    row["causal_reject_frames"] = int((miss > 0).sum())
                    csv_rows.append(row)
                    key = f"{win['name']}:{an}"
                    vals = {"second_diff_rms": d2_c[j],
                            "rms_vs_oracle_lag0": rms0[j],
                            "best_lag": abs(int(lags[j]))}
                    label = (sname if smoother == "none"
                             else f"{sname}+{smoother}")
                    for metric in clean_metrics:
                        scores.setdefault(label, {})[
                            f"{metric}:{key}"] = float(vals[metric])
                out(f"{'':>18} {'':>8} teleport frames (any angle) "
                    f"{tele['count']}, worst step {tele['worst_step_deg']:.2f} "
                    f"deg = {tele['worst_ratio']:.2f} x budget; joint-limit "
                    f"fraction {'n/a' if limits_all_null else f'{jl_frac:.4f}'}")
                out(f"{'':>18} {'':>8} non-MEASURED frames per group "
                    + " ".join(f"{g}={int(c)}" for g, c in
                               zip(m.GROUP_NAMES, nonmeas))
                    + f"; frames with a causal-filter reject "
                    f"{int((miss > 0).sum())} ({int(miss.sum())} "
                    "landmark-frames)")
                out(f"{'':>18} {'':>8} bone p95 dev (r_up r_fore l_up "
                    f"l_fore): causal "
                    + " ".join(f"{v:.3f}" for v in bone_c)
                    + "; oracle " + " ".join(f"{v:.3f}" for v in bone_o)
                    + "; raw " + " ".join(f"{v:.3f}" for v in bone_r))
                if v1 is not None and offsets is not None:
                    for v1a, an in V1_ANGLES.items():
                        j = m.ANGLE_NAMES.index(an)
                        lag, mu, sd = v1_agreement(
                            A[:, j], v1[f"{v1a}_film"].to_numpy(float),
                            offsets[j], max_lag)
                        agree_rows.append((f"causal {sname}/{smoother}",
                                           "v1 film", an, lag, mu, sd))
                        for r in csv_rows:
                            if (r["window"] == win["name"]
                                    and r["strategy"] == sname
                                    and r["smoother"] == smoother
                                    and r["angle"] == an):
                                r["v1film_lag"] = lag
                                r["v1film_resid_mean"] = mu
                                r["v1film_resid_cstd"] = sd
        if v1 is not None and offsets is not None:
            for v1a, an in V1_ANGLES.items():
                j = m.ANGLE_NAMES.index(an)
                ref_f = v1[f"{v1a}_film"].to_numpy(float)
                ref_r = v1[f"{v1a}_raw_gated"].to_numpy(float)
                agree_rows.append(("oracle", "v1 film", an,
                                   *v1_agreement(O[:, j], ref_f, offsets[j],
                                                 max_lag)))
                agree_rows.append(("raw", "v1 film", an,
                                   *v1_agreement(R[:, j], ref_f, offsets[j],
                                                 max_lag)))
                agree_rows.append(("raw", "v1 raw_gated", an,
                                   *v1_agreement(R[:, j], ref_r, offsets[j],
                                                 max_lag)))
            out(f"v1 agreement ({V1_SERIES[win['name']]}), offsets from "
                f"{Path(off_path).name} subtracted, residual at the best "
                "lag:")
            out(f"{'V3 series':>36} {'v1 series':>13} {'angle':>10} "
                f"{'offset':>7} {'lag':>4} {'resid_mean':>10} {'cstd':>7}")
            for src, ref_name, an, lag, mu, sd in agree_rows:
                j = m.ANGLE_NAMES.index(an)
                out(f"{src:>36} {ref_name:>13} {an:>10} {offsets[j]:>7.2f} "
                    f"{lag:>4d} {mu:>10.3f} {sd:>7.3f}")
        elif win["name"] in V1_SERIES:
            out("v1 agreement: skipped (series file absent or no D-018 "
                f"offsets for variant {args.variant})")
        else:
            out("v1 agreement: no v1 series for this window")

    out()
    out(f"clean-metric mean rank (bench.json ranking.clean_metrics "
        f"{clean_metrics} x windows x 13 angles, best_lag as |lag|; "
        "INFORMATIONAL: the D-003 hard gates come from grade.py on the "
        "S-type scenarios and are not applied here)")
    scores = {k: v for k, v in scores.items() if v}
    if len(scores) > 1:
        ranked = m.rank_strategies(scores, {s: {} for s in scores})
        for r in ranked:
            out(f"  {r['strategy']:>18}  mean rank {r['mean_rank']:.3f}")
    else:
        out("  (one strategy: nothing to rank)")
    out()
    df = pd.DataFrame(csv_rows)
    out("13-angle means over windows x angles (angles identically zero in"
        " the oracle, i.e. elbow_z, excluded; n = window-angle pairs; "
        "rms0 / rmsL deg, |lag| frames, d2_caus deg/frame^2 arithmetic "
        "mean, d2/o geometric mean of causal / oracle):")
    out(f"{'strategy':>18} {'smoother':>13} {'n':>3} {'rms0':>7} "
        f"{'|lag|':>6} {'rmsL':>7} {'d2_caus':>8} {'d2/o':>6}")
    for r in angle_means(df):
        out(f"{r['strategy']:>18} {r['smoother']:>13} {r['n']:>3d} "
            f"{r['rms0']:>7.3f} {r['lag']:>6.2f} {r['rmsL']:>7.3f} "
            f"{r['d2c']:>8.3f} {r['d2o']:>6.3f}")
    out()
    out("right-arm summary (sh_y = r_swing_y, sh_z = r_swing_z, "
        "sh_twist = r_twist, el_y = r_elbow_y):")
    out(f"{'window':>18} {'strategy':>18} {'smoother':>13} {'angle':>10} {'rms0':>7} "
        f"{'lag':>4} {'rmsL':>7} {'d2_caus':>8} {'d2_orac':>8} "
        f"{'d2_raw':>8}")
    for _, r in df[df["angle"].isin(RIGHT_ARM)].iterrows():
        out(f"{r['window']:>18} {r['strategy']:>18} {r['smoother']:>13} {r['angle']:>10} "
            f"{r['rms_vs_oracle_lag0']:>7.3f} {int(r['best_lag']):>4d}"
            f"{'*' if abs(int(r['best_lag'])) == max_lag else ' '}"
            f"{r['rms_vs_oracle_best_lag']:>7.3f} "
            f"{r['second_diff_rms_causal']:>8.3f} "
            f"{r['second_diff_rms_oracle']:>8.3f} "
            f"{r['second_diff_rms_raw']:>8.3f}")

    out_csv = Path(args.out_csv) if args.out_csv else (
        Path(args.csv_dir) / f"clean_grade__{args.variant}.csv")
    df.to_csv(out_csv, index=False, float_format="%.6f")
    if args.out_txt:
        Path(args.out_txt).write_text("\n".join(lines) + "\n")
        print(f"[+] {args.out_txt}")
    print(f"[+] {out_csv}")


if __name__ == "__main__":
    main()

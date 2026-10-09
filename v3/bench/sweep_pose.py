#!/usr/bin/env python3
"""Pose-model sweep (M3, D-028): named variants x the pinned bag and
the clean-window bags.

Two modes:

  run    (env v3rt, GPU) for every variant x bag: the detector stage
         exactly as extraction and realtime run it (build_detector,
         non-paced, config det_freq), recording per frame the float
         COCO-17 keypoints, their scores, whether a person was found
         and the detector-stage latency. Saved to
         <out-dir>/<variant>__<bagstem>.npz. Every onnx is hash-checked
         before its run (verify_variant_files).

  table  (numpy + pandas, no GPU) the sweep table from the npz files,
         the clean-window bench CSVs (bench/grade_clean.py
         clean_grade__<variant>.csv), the S-type grade texts
         (bench/grade.py, one per variant) and the realtime texts
         (replay/realtime.py, one per variant).

Keypoint-side metrics, per variant (eight landmarks = COCO 5..12:
shoulders, elbows, wrists, hips):
  found        frames with a person / frames
  score        mean keypoint score per landmark over found frames
  step p95     p95 of the per-frame 2D keypoint step in px, over
               consecutive frame pairs where both frames have a person
               (pinned bag: post-warmup frames; clean bags: inside the
               window, stop inclusive)
  det p99      detector-stage latency p99 in ms on the pinned bag,
               post-warmup (bench.json latency.warmup_frames)

Solver-side metrics come from grade_clean.py's CSV (see its docstring);
aggregation rules are in the table header and in D-028.

Run:
  LD_LIBRARY_PATH=$NVLIB /home/luo/anaconda3/envs/v3rt/bin/python \\
      v3/bench/sweep_pose.py run --variants rtmpose-m,rtmpose-x
  /home/luo/anaconda3/bin/python v3/bench/sweep_pose.py table \\
      --variants rtmpose-m,rtmpose-x --out-txt v3/dataset/phase5_pose_sweep.txt

M4 recap (D-033 manifests, D-032 caps, D-031 warm start; both S2
smoothers; [F] compares with the pinned M3 selection), from v3/:
  /home/luo/anaconda3/bin/python bench/sweep_pose.py table \\
      --variants rtmpose-m,rtmpose-x,rtmpose-x_yolox-m,rtmpose-l,\\
rtmpose-l_yolox-m,rtmw-dw-l-m --smoothers none,quat_one_euro \\
      --csv-dir output/recap --grade-dir output/recap \\
      --realtime-dir output/pose_sweep \\
      --realtime-override rtmpose-x_yolox-m:quat_one_euro=\\
dataset/phase5_realtime__rtmpose-x_yolox-m__quat_one_euro.txt \\
      --m3-table dataset/phase5_pose_sweep.txt \\
      --out-txt dataset/phase5_pose_sweep_recapped.txt
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

import numpy as np

V3_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V3_ROOT.parent
sys.path.insert(0, str(V3_ROOT))

from bench.paths import repo_path                                   # noqa: E402

# COCO-17 indices 5..12 in COCO order (core/skeleton.py COCO_IDX)
LM_IDX = list(range(5, 13))
LM_NAMES = ["l_sh", "r_sh", "l_el", "r_el", "l_wr", "r_wr", "l_hip",
            "r_hip"]
PINNED = "pinned"


def bag_list(cfg, windows_file):
    """[(name, bag path, start, stop inclusive or None)]. A relative
    window bag path is repository-relative (bench/paths.py repo_path,
    eval/recordings_archive/DECISIONS.md RA-002); an absolute one is
    used as written."""
    wins = json.loads(Path(windows_file).read_text())
    out = [(PINNED, cfg["paths"]["bag"], None, None)]
    for w in wins["windows"]:
        out.append((w["name"], str(repo_path(w["bag"])), int(w["start"]),
                    int(w["stop"])))
    return out


def run_one(cfg, bag, variant, variants, device, out_npz):
    from core.skeleton import COCO_IDX
    from detector.factory import apply_variant, build_detector
    from replay.bag_source import BagSource

    cfg = apply_variant(cfg, variant, variants)
    src = BagSource(bag, paced=False)
    det = build_detector(cfg, str(REPO_ROOT),
                         img_wh=(src.intrinsics.width,
                                 src.intrinsics.height),
                         device=device,
                         key_indices=sorted(COCO_IDX.values()))
    frames, kps, scs, found, lat, det_ran = [], [], [], [], [], []
    for idx, t_s, color, depth in src.frames():
        t0 = time.perf_counter()
        kp, sc, diag = det(color)
        lat.append((time.perf_counter() - t0) * 1000)
        frames.append(idx)
        det_ran.append(bool(diag["det_ran"]))
        if kp is None:
            found.append(False)
            kps.append(np.full((17, 2), np.nan))
            scs.append(np.full(17, np.nan))
        else:
            found.append(True)
            kps.append(np.asarray(kp, dtype=float))
            scs.append(np.asarray(sc, dtype=float))
    src.close()
    np.savez_compressed(out_npz, frame=np.asarray(frames),
                        kp=np.asarray(kps), score=np.asarray(scs),
                        found=np.asarray(found), lat_ms=np.asarray(lat),
                        det_ran=np.asarray(det_ran))
    return len(frames), int(np.sum(found))


def kp_stats(z, s0, s1, warmup):
    """Keypoint metrics on frames [s0, s1] (inclusive) or, when s0 is
    None, on frames >= warmup."""
    fr = z["frame"]
    sel = (fr >= warmup) if s0 is None else ((fr >= s0) & (fr <= s1))
    kp, sc, fd = z["kp"][sel], z["score"][sel], z["found"][sel]
    score = np.nanmean(sc[fd][:, LM_IDX], axis=0)
    both = fd[1:] & fd[:-1]
    step = np.linalg.norm(np.diff(kp[:, LM_IDX], axis=0), axis=2)[both]
    return {"frames": int(sel.sum()), "found": int(fd.sum()),
            "score": score, "step_p95": np.percentile(step, 95, axis=0)}


def parse_grade(path):
    """{strategy: {"teleport": n_fail, "honesty": n_fail, "n": n}} from
    a bench/grade.py text."""
    out, cur = {}, None
    for line in Path(path).read_text().splitlines():
        mt = re.match(r"=== strategy: (\S+) ===", line)
        if mt:
            cur = mt.group(1)
            out[cur] = {"teleport": 0, "honesty": 0, "n": 0}
            continue
        if cur is None:
            continue
        parts = line.split()
        if len(parts) == 9 and parts[0] != "scenario":
            out[cur]["n"] += 1
        if "HARD GATE FAIL" in line:
            for g in ("teleport", "honesty"):
                if g in line:
                    out[cur][g] += 1
    return out


def parse_realtime(path):
    """(detect p99, total p99, verdict) from a replay/realtime.py text."""
    det = tot = None
    verdict = None
    for line in Path(path).read_text().splitlines():
        parts = line.split()
        if parts[:1] == ["detect"]:
            det = float(parts[3])
        elif parts[:1] == ["total"]:
            tot = float(parts[3])
        elif line.startswith("budget check"):
            verdict = parts[-1]
    return det, tot, verdict


def geomean_ratio(df, base, col, keys):
    """Geometric mean over (window, angle) of df[col] / base[col],
    over pairs where the base value is > 0 (identically-zero angles,
    r_elbow_z and l_elbow_z, are excluded)."""
    a = df.set_index(keys)[col]
    b = base.set_index(keys)[col]
    a, b = a.align(b, join="inner")
    ok = (b > 0) & (a > 0)
    return float(np.exp(np.mean(np.log(a[ok] / b[ok])))), int(ok.sum())


def grade_path(grade_dir, variant, smoother):
    """bench/grade.py text of one variant and S2 smoother: smoother none
    -> s_grade__<variant>.txt, else s_grade__<variant>__<smoother>.txt."""
    stem = (f"s_grade__{variant}" if smoother == "none"
            else f"s_grade__{variant}__{smoother}")
    return Path(grade_dir) / f"{stem}.txt"


def select_for_smoother(out, args, names, base_name, agg, dfs, base, keys,
                        sm, tag, rt_dir, rt_override):
    """Sections [C], [D], [E] for one S2 smoother; returns (winner,
    {variant: verdict}).
    baseline_hold has no smoother, so it appears under smoother none
    only. The selection rule is D-028's, unchanged."""
    out()
    out("[C] causal strategies on each variant's clean extraction "
        "(M2 metrics): d2_caus ratio (geomean vs the reference "
        "variant's same strategy), mean rms0 and rmsL vs own oracle "
        "(deg), mean |lag| (frames); means over windows x 11 "
        "non-degenerate angles" + tag)
    out(f"{'variant':>18} {'strategy':>18} {'d2c_rat':>7} {'d2c':>7} "
        f"{'rms0':>7} {'rmsL':>7} {'|lag|':>6}")
    strategies = (("baseline_hold", "s2_quat_prediction") if sm == "none"
                  else ("s2_quat_prediction",))
    for v in names:
        for s in strategies:
            dv, db = dfs[v], base
            d = dv[(dv["strategy"] == s) & (dv["smoother"] == sm)]
            bb = db[(db["strategy"] == s) & (db["smoother"] == sm)]
            if d.empty:
                continue
            rat, _ = geomean_ratio(d, bb, "second_diff_rms_causal", keys)
            nz = d[~d["angle"].isin(["r_elbow_z", "l_elbow_z"])]
            out(f"{v:>18} {s:>18} {rat:>7.3f} "
                f"{nz['second_diff_rms_causal'].mean():>7.3f} "
                f"{nz['rms_vs_oracle_lag0'].mean():>7.3f} "
                f"{nz['rms_vs_oracle_best_lag'].mean():>7.3f} "
                f"{nz['best_lag'].abs().mean():>6.2f}")

    out()
    out("[D] hard gates (D-003) and latency: S-type grade of "
        "s2_quat_prediction on each variant's own extraction and "
        "manifest (bench/grade.py), realtime total p99 on the pinned "
        "bag (replay/realtime.py, paced, s2_quat_prediction, no shm)"
        + tag)
    out(f"{'variant':>18} {'det_p50':>7} {'det_p99':>7} {'rt_det99':>8} "
        f"{'tot_p99':>7} {'lat':>4} {'s2_tele':>7} {'s2_hon':>6} "
        f"{'bh_tele':>7} {'gates':>5}")
    gates = {}
    for v in names:
        g = parse_grade(grade_path(args.grade_dir, v, sm))
        rt = rt_override.get((v, sm), rt_dir / f"realtime__{v}.txt")
        rdet, rtot, verdict = parse_realtime(rt)
        s2 = g.get("s2_quat_prediction", {})
        bh = g.get("baseline_hold")
        ok = (verdict == "PASS" and s2.get("n", 0) > 0
              and s2["teleport"] == 0 and s2["honesty"] == 0)
        gates[v] = ok
        bh_col = (f"{bh['teleport']:>3}/{bh['n']:<3}" if bh is not None
                  else f"{'n/a':>7}")
        out(f"{v:>18} {agg[v]['det_p50']:>7.2f} {agg[v]['det_p99']:>7.2f} "
            f"{rdet:>8.2f} {rtot:>7.2f} {verdict:>4} "
            f"{s2.get('teleport', -1):>3}/{s2.get('n', 0):<3} "
            f"{s2.get('honesty', -1):>2}/{s2.get('n', 0):<3} "
            f"{bh_col} "
            f"{'PASS' if ok else 'FAIL':>5}")
    out("  (s2_tele / s2_hon / bh_tele = scenarios failing that gate / "
        "scenarios; baseline_hold is the reference behaviour and is not "
        "gated)")
    if rt_override or args.realtime_dir:
        used = [f"{v}: {rt_override[(v, sm)].name}" for v in names
                if (v, sm) in rt_override]
        out("  (realtime: " + (", ".join(used) + "; others: "
                               if used else "")
            + f"{rt_dir}/realtime__<variant>.txt)")

    out()
    out("[E] selection (D-028 rule, stated before the numbers): "
        "(1) disqualify a variant whose s2_quat_prediction fails any "
        "D-003 hard gate; (2) a candidate beats the reference only if "
        "its d2_raw ratio < 1 AND its mean oracle bone p95 (four bones) "
        "<= the reference's; (3) among those, lowest d2_raw ratio wins; "
        "(4) no candidate beats the reference -> keep the reference"
        + tag)
    ref_bone = float(np.mean(agg[base_name]["bone"]))
    beaters = []
    verdicts = {}
    for v in names:
        mb = float(np.mean(agg[v]["bone"]))
        verdict = ("disqualified (gates)" if not gates[v] else
                   "reference" if v == base_name else
                   "beats reference" if (agg[v]["d2_raw"] < 1.0
                                         and mb <= ref_bone) else
                   "does not beat reference")
        verdicts[v] = verdict
        if verdict == "beats reference":
            beaters.append((agg[v]["d2_raw"], v))
        out(f"{v:>18} d2_raw ratio {agg[v]['d2_raw']:.3f}  mean bone "
            f"{mb:.4f} (ref {ref_bone:.4f})  -> {verdict}")
    winner = min(beaters)[1] if beaters else base_name
    out(f"WINNER: {winner}" if not tag else
        f"WINNER (S2 smoother {sm}): {winner}")
    return winner, verdicts


def compare_m3(out, m3_table, names, smoothers, results):
    """Section [F]: verdicts and winner of a pinned earlier table (the
    M3 sweep, dataset/phase5_pose_sweep.txt) next to this one."""
    old, old_winner = {}, None
    for line in Path(m3_table).read_text().splitlines():
        mt = re.match(r"\s*(\S+) d2_raw ratio .* -> (.+)$", line)
        if mt:
            old[mt.group(1)] = mt.group(2).strip()
        mw = re.match(r"WINNER: (\S+)", line)
        if mw:
            old_winner = mw.group(1)
    out()
    out(f"[F] against the pinned M3 selection ({Path(m3_table).name}; "
        "pre-D-033 budgets, fixed D-021 caps, cold start)")
    out(f"{'variant':>18} {'M3':>24} "
        + " ".join(f"{'now, ' + sm:>26}" for sm in smoothers))
    for v in names:
        out(f"{v:>18} {old.get(v, 'n/a'):>24} "
            + " ".join(f"{results[sm][1][v]:>26}" for sm in smoothers))
    for sm in smoothers:
        win = results[sm][0]
        same = "UNCHANGED" if win == old_winner else "CHANGED"
        out(f"winner, S2 smoother {sm}: {win} (M3 {old_winner}) "
            f"-> {same}")


def table(args, cfg):
    import pandas as pd
    names = args.variants.split(",")
    base_name = names[0]
    warmup = json.loads((V3_ROOT / "configs/bench.json").read_text())[
        "latency"]["warmup_frames"]
    bags = bag_list(cfg, args.windows_file)
    lines = []

    def out(s=""):
        print(s)
        lines.append(s)

    out("V3 pose-model sweep (bench/sweep_pose.py; M3, D-028)")
    out(f"variants {','.join(names)}; reference {base_name}; det_freq "
        f"{cfg['detect']['det_freq']}; device cuda (onnxruntime-gpu); "
        "non-paced detector runs")
    out(f"pinned bag {cfg['paths']['bag']} (post-warmup, {warmup} frames "
        "excluded); clean windows configs/clean_windows.json (D-025)")
    out("NOT external truth: every solver-side number is self-consistency"
        " (each variant against its own offline oracle, D-024)")
    if args.smoothers != "none":
        out(f"inputs: clean-window CSVs {args.csv_dir}; S-type grades "
            f"{args.grade_dir} (each grade text names its manifest and S2 "
            f"settings); S2 smoothers {args.smoothers}")

    out()
    out("[A] keypoint side: found / frames, mean score over the eight "
        "landmarks, 2D step p95 px per landmark")
    hdr = (f"{'variant':>18} {'bag':>18} {'found':>9} {'score':>6} "
           + " ".join(f"{n:>6}" for n in LM_NAMES))
    out(hdr)
    agg = {}
    for v in names:
        agg[v] = {"clean_step": [], "clean_score": []}
        for bname, bag, s0, s1 in bags:
            p = Path(args.out_dir) / f"{v}__{Path(bag).stem}.npz"
            z = np.load(p)
            st = kp_stats(z, s0, s1, warmup)
            out(f"{v:>18} {bname:>18} {st['found']:>4}/{st['frames']:<4} "
                f"{np.mean(st['score']):>6.3f} "
                + " ".join(f"{x:>6.2f}" for x in st["step_p95"]))
            if bname == PINNED:
                lat = z["lat_ms"][z["frame"] >= warmup]
                agg[v]["det_p50"] = float(np.percentile(lat, 50))
                agg[v]["det_p99"] = float(np.percentile(lat, 99))
                agg[v]["pinned_found"] = f"{st['found']}/{st['frames']}"
                agg[v]["pinned_score"] = float(np.mean(st["score"]))
                agg[v]["pinned_score_lm"] = st["score"]
            else:
                agg[v]["clean_step"].append(st["step_p95"])
                agg[v]["clean_score"].append(st["score"])
    out()
    out("[A2] per-landmark mean score on the pinned bag")
    out(f"{'variant':>18} " + " ".join(f"{n:>6}" for n in LM_NAMES))
    for v in names:
        out(f"{v:>18} " + " ".join(f"{x:>6.3f}"
                                   for x in agg[v]["pinned_score_lm"]))

    out()
    out("[B] solver side on the clean windows (grade_clean.py CSVs; "
        "d2 = second-difference RMS deg/frame^2; ratios are geometric "
        f"means over windows x angles of variant / {base_name}, "
        "identically-zero angles excluded; bone = oracle-side p95 "
        "fractional bone-length deviation, mean over the four windows)")
    keys = ["window", "angle"]
    dfs = {}
    for v in names:
        dfs[v] = pd.read_csv(Path(args.csv_dir) / f"clean_grade__{v}.csv")
    base = dfs[base_name]
    out(f"{'variant':>18} {'d2_raw':>7} {'d2_orac':>7} {'rawRA':>7} "
        f"{'r_up':>6} {'r_fore':>6} {'l_up':>6} {'l_fore':>6} "
        f"{'raw_rup':>7} {'step':>6}")
    for v in names:
        d = dfs[v][dfs[v]["strategy"] == "baseline_hold"]
        bb = base[base["strategy"] == "baseline_hold"]
        r_raw, n_raw = geomean_ratio(d, bb, "second_diff_rms_raw", keys)
        r_orc, _ = geomean_ratio(d, bb, "second_diff_rms_oracle", keys)
        ra = d[d["angle"].isin(["r_swing_y", "r_swing_z", "r_twist",
                                "r_elbow_y"])]
        rawra = float(ra["second_diff_rms_raw"].mean())
        per_win = d.groupby("window").first()
        bone = [float(per_win[f"bone_p95_oracle_{b}"].mean())
                for b in ("r_upper_arm", "r_forearm", "l_upper_arm",
                          "l_forearm")]
        raw_rup = float(per_win["bone_p95_raw_r_upper_arm"].mean())
        step = float(np.mean(agg[v]["clean_step"]))
        agg[v].update(d2_raw=r_raw, d2_orac=r_orc, bone=bone,
                      step=step, rawra=rawra)
        out(f"{v:>18} {r_raw:>7.3f} {r_orc:>7.3f} {rawra:>7.3f} "
            + " ".join(f"{x:>6.3f}" for x in bone)
            + f" {raw_rup:>7.3f} {step:>6.2f}")
    out(f"  (d2 ratios over {n_raw} window-angle pairs; rawRA = mean raw "
        "d2 over the four right-arm angles x windows, deg/frame^2; step "
        "= mean clean-window 2D step p95 over eight landmarks x windows,"
        " px)")

    smoothers = args.smoothers.split(",")
    legacy = smoothers == ["none"]
    rt_dir = Path(args.realtime_dir or args.grade_dir)
    rt_override = {}
    for item in args.realtime_override or []:
        key, path = item.split("=", 1)
        rt_override[tuple(key.split(":", 1))] = Path(path)
    results = {}
    for sm in smoothers:
        tag = "" if legacy else f" -- S2 smoother {sm}"
        results[sm] = select_for_smoother(out, args, names, base_name, agg,
                                          dfs, base, keys, sm, tag, rt_dir,
                                          rt_override)
    if args.m3_table:
        compare_m3(out, args.m3_table, names, smoothers, results)

    if args.out_txt:
        Path(args.out_txt).write_text("\n".join(lines) + "\n")
        print(f"[+] {args.out_txt}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("mode", choices=("run", "table"))
    ap.add_argument("--config", default=str(V3_ROOT / "configs/default.json"))
    ap.add_argument("--windows-file",
                    default=str(V3_ROOT / "configs/clean_windows.json"))
    ap.add_argument("--variants", default="rtmpose-m",
                    help="comma-separated names from configs/"
                         "model_variants.json; the first is the reference")
    ap.add_argument("--out-dir", default=str(V3_ROOT / "output/pose_sweep"))
    ap.add_argument("--csv-dir", default=str(V3_ROOT / "output/clean"))
    ap.add_argument("--grade-dir", default=str(V3_ROOT / "output/pose_sweep"),
                    help="holds s_grade__<variant>.txt and "
                         "realtime__<variant>.txt")
    ap.add_argument("--smoothers", default="none",
                    help="table: comma-separated S2 smoothers; sections "
                         "[C] [D] [E] are repeated per smoother (M4); "
                         "grades are read from s_grade__<variant>.txt "
                         "(none) and s_grade__<variant>__<smoother>.txt")
    ap.add_argument("--realtime-dir", default=None,
                    help="table: holds realtime__<variant>.txt "
                         "(default: --grade-dir)")
    ap.add_argument("--realtime-override", action="append",
                    metavar="VARIANT:SMOOTHER=PATH",
                    help="table: a realtime text measured for one "
                         "variant and smoother (repeatable)")
    ap.add_argument("--m3-table", default=None,
                    help="table: an earlier table text (the pinned M3 "
                         "sweep) whose [E] verdicts and winner are "
                         "compared in section [F]")
    ap.add_argument("--device", default="cuda", choices=("cuda", "cpu"))
    ap.add_argument("--out-txt", default=None)
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text())
    if args.mode == "table":
        table(args, cfg)
        return

    if args.device == "cuda":
        from detector.rtmpose_detector import ensure_cuda_env
        ensure_cuda_env(cfg["model"].get("cuda_lib_dirs"))
    from detector.factory import load_variants, verify_variant_files
    variants = load_variants()
    names = args.variants.split(",")
    for name in names:
        verify_variant_files(name, REPO_ROOT, variants)
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    for name in names:
        for bname, bag, s0, s1 in bag_list(cfg, args.windows_file):
            p = Path(args.out_dir) / f"{name}__{Path(bag).stem}.npz"
            t0 = time.monotonic()
            n, f = run_one(cfg, bag, name, variants, args.device, p)
            print(f"{name:>18} {bname:>18} frames {n} found {f} "
                  f"({time.monotonic() - t0:.1f} s) -> {p.name}", flush=True)


if __name__ == "__main__":
    main()

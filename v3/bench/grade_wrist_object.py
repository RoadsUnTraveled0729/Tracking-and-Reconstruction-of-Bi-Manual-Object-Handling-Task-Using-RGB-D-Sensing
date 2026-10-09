"""Wrist-to-object bench (M7; D-035, D-036, D-037).

Per recording x series x hand, on the frames where that hand holds the
object (bench/holding.py, the thesis geometry rule on the MEASURED V3
wrist):

  v_real = measured RGB-D wrist landmark - ArUco object marker origin
  v_rec  = FK wrist (core/fk.py, 13 angles + oracle-median bone
           lengths) - the same marker origin
  |v_rec - v_real| = |FK wrist - measured wrist| (the object position
           cancels), median / p95 in metres, and its median signed
           components in the levelled desk world (x right, y up, z).

Two FK anchors: (a) the measured shoulder landmark of that side (tests
the arm chain only); (b) the measured right hip L24 + R_root @ offset,
offset = per-recording median of R_root^T (shoulder - L24) on the
oracle (tests the root too).

Grip-vector constancy: per hold run (holding.hold_runs, the thesis
stage-4 split), the 3D standard deviation sqrt(sum of per-axis
variances) of R_obj^T (wrist - box centre), for the measured wrist
(the depth-side floor) and the FK wrists; the frame-weighted mean over
runs is tabulated. |wrist - box centre| median / p95 for measured,
FK(a), FK(b). Stage-3-style residual of the measured wrist against a
single per-hand object-frame grip vector (thesis r4_stage3 table).

Series: the offline zero-phase oracle angles (bench/oracle.py, D-024)
and every causal strategy x smoother (replay/runner.py run_csv; the
smoother applies to s2_quat_prediction only).

Usage (v3rt):
  python bench/grade_wrist_object.py --recordings r4,r5,r6b,r7 \
      --strategies baseline_hold,s2_quat_prediction \
      --smoothers none,quat_one_euro --variant rtmpose-l
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

from bench import aruco_source as src                     # noqa: E402
from bench import holding                                 # noqa: E402
from bench.metrics import ANGLE_NAMES                     # noqa: E402
from bench.oracle import oracle_angles, read_landmarks    # noqa: E402
from bench.paths import apply_overrides, repo_path        # noqa: E402
from core import fk                                       # noqa: E402
from replay.runner import run_csv                         # noqa: E402
from strategies.smoother_base import SMOOTHERS            # noqa: E402
from strategies.strategy_base import build                # noqa: E402
import strategies.baseline_hold                           # noqa: E402,F401
import strategies.s2_quat_prediction                      # noqa: E402,F401

FLIP = np.array([1.0, -1.0, 1.0])     # vendor/v1/root_frame.py SENSOR_TO_UNITY
SIDES = ("right", "left")

# Thesis R4 reference numbers (MediaPipe landmarks, v1 filtered track):
# eval/reports/r4_stage3_offset_fit.md (resid, |wrist-center| stage 3)
# and eval/reports/r4_stage4_ground_truth.md (stage-2 constancy table).
THESIS_R4 = {
    "right": {"stage3_resid_med_cm": 10.2, "stage3_resid_p95_cm": 21.7,
              "stage4_dist_med_cm": 14.6, "stage4_dist_p95_cm": 17.9,
              "held": 494,
              "runs": [(254, 388, 134, 0.64), (478, 713, 235, 1.54),
                       (1028, 1112, 85, 2.04)]},
    "left": {"stage3_resid_med_cm": 2.6, "stage3_resid_p95_cm": 6.1,
             "stage4_dist_med_cm": 13.4, "stage4_dist_p95_cm": 17.3,
             "held": 158, "runs": [(674, 832, 158, 1.87)]},
}


def sha16(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def extraction_csv(stem, variant, csv_dir):
    return Path(csv_dir) / f"extraction_{stem}__{variant}.csv"


def unity_pts(df_or_tab, name, suffix=""):
    cols = [f"{name}_{suffix}{a}" for a in "xyz"]
    return df_or_tab[cols].to_numpy(dtype=float)


def pct(x, q):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return float(np.percentile(x, q)) if x.size else float("nan")


def grip_std(w, center, R_obj, runs, hold):
    """Frame-weighted mean over runs of the 3D std of R^T (w - c),
    plus the per-run list [(start, stop, n, std3d, std of |w - c|)]
    (the latter is the thesis stage-4 per-episode std)."""
    d = np.einsum("nji,nj->ni", R_obj, w - center)
    per, tot, wsum = [], 0.0, 0
    for a, b, _ in runs:
        e = np.flatnonzero(hold)
        e = e[(e >= a) & (e <= b)]
        e = e[np.isfinite(d[e]).all(axis=1)]
        if e.size < 2:
            continue
        s = float(np.sqrt(np.sum(np.var(d[e], axis=0))))
        smag = float(np.std(np.linalg.norm(d[e], axis=1)))
        per.append((a, b, int(e.size), s, smag))
        tot += s * e.size
        wsum += e.size
    return (tot / wsum if wsum else float("nan")), per


def stage3_resid(w, obj, R_obj, hold):
    """Thesis stage-3 residual (carry.py fit_grip): one object-frame
    grip vector per hand from the marker origin, |obj + R mu - w|."""
    d = np.einsum("nji,nj->ni", R_obj, w - obj)
    ok = hold & np.isfinite(d).all(axis=1)
    if not ok.any():
        return float("nan"), float("nan")
    mu = d[ok].mean(axis=0)
    r = np.linalg.norm(obj + np.einsum("nij,j->ni", R_obj, mu) - w, axis=1)
    return float(np.median(r[ok])), pct(r[ok], 95)


def evaluate_recording(alias, cfg, variant, csv_dir, strategies, smoothers,
                       out):
    stem = src.STEMS[alias]
    csv = extraction_csv(stem, variant, csv_dir)
    df = pd.read_csv(csv)
    frames = df["frame"].to_numpy(dtype=int)
    if not np.array_equal(frames, np.arange(len(frames))):
        raise ValueError(f"{csv}: frames are not 0..n-1")
    world = src.load_world(alias)
    obj = src.align(src.read_object(stem, world), frames)
    al = src.check_alignment(obj["time_s"], df["time_s"].to_numpy())
    out(f"=== {alias} {stem}: {len(df)} frames, csv sha256 {sha16(csv)}.., "
        f"aruco sha256 {sha16(src.aruco_csv(stem))}.. ===")
    out(f"  alignment (D-035): frame index offset 0; max |dt| "
        f"{al['max_abs_dt_s'] * 1e3:.3f} ms, median "
        f"{al['median_abs_dt_s'] * 1e3:.3f} ms over {al['n']} frames, "
        f"half frame {al['half_frame_s'] * 1e3:.2f} ms -> "
        f"{'PASS' if al['ok'] else 'FAIL'}")
    if not al["ok"]:
        raise ValueError(f"{alias}: ArUco and V3 time_s disagree")
    det = obj["det"]
    center, R_obj, o = obj["center"], obj["R_obj"], obj["obj"]
    env = json.loads(src.inspection_path(stem).read_text())[
        "phases"]["manipulation"]
    carried = holding.rest_referenced_carried(
        o, world.height_above_table(o), env)
    out(f"  object detected {int(det.sum())}/{len(det)}; manipulation "
        f"envelope {env}; carried {int(carried.sum())}")

    raw = read_landmarks(df)                        # camera frame
    meas_w, hold, runs = {}, {}, {}
    for side in SIDES:
        wr_cam = raw[f"{side}_wrist"]
        clean = (df[f"{side}_wrist_src"].to_numpy() == 0) \
            & np.isfinite(wr_cam).all(axis=1)
        meas_w[side] = world.world_from_cam(wr_cam)
        f_ok = holding.forearm_ok(raw[f"{side}_elbow"], wr_cam)
        hold[side] = holding.holding_mask(center, meas_w[side], clean, det,
                                          carried, f_ok)
        dist = np.linalg.norm(meas_w[side] - center, axis=1)
        _, eps = holding.grip_episodes(hold[side], carried, dist, clean)
        runs[side] = holding.hold_runs(hold[side])
        out(f"  {side:>5} holding {int(hold[side].sum())} frames; hold runs "
            f"(gap>15 split, >=30) {[(a, b, n) for a, b, n in runs[side]]}; "
            f"grip_episodes (state machine) {eps}")

    # oracle: angles, filtered Unity landmarks, bone lengths, offsets
    ot = oracle_angles(csv, cfg)
    O = ot[list(ANGLE_NAMES)].to_numpy(dtype=float)
    fl = {n: unity_pts(ot, n, "f") for n in
          ("right_hip", "right_shoulder", "left_shoulder", "right_elbow",
           "left_elbow", "right_wrist", "left_wrist")}
    bones, offs = {}, {}
    for side in SIDES:
        Lu = float(np.nanmedian(np.linalg.norm(
            fl[f"{side}_shoulder"] - fl[f"{side}_elbow"], axis=1)))
        Lf = float(np.nanmedian(np.linalg.norm(
            fl[f"{side}_elbow"] - fl[f"{side}_wrist"], axis=1)))
        bones[side] = (Lu, Lf)
        offs[side], n_off = fk.hip_shoulder_offset(
            O, fl["right_hip"], fl[f"{side}_shoulder"])
        out(f"  {side:>5} bones (oracle median) Lu {Lu:.4f} m, Lf "
            f"{Lf:.4f} m; hip-to-shoulder offset (root frame, n "
            f"{n_off}) ({offs[side][0]:+.4f}, {offs[side][1]:+.4f}, "
            f"{offs[side][2]:+.4f}) m")

    series = [("oracle", "zero-phase", O)]
    for sname in strategies:
        for sm in smoothers:
            if sm != "none" and sname != "s2_quat_prediction":
                continue
            scfg = apply_overrides(cfg, [
                f"strategy.s2_quat_prediction.smoother=\"{sm}\""])
            tab = run_csv(csv, scfg, build(sname, scfg))
            if not np.array_equal(tab["frame"].to_numpy(dtype=int), frames):
                raise ValueError("runner frames differ from the CSV")
            series.append((sname, sm, tab[list(ANGLE_NAMES)]
                           .to_numpy(dtype=float)))

    rows, per_run = [], []
    hip_u = raw["right_hip"] * FLIP
    for side in SIDES:
        h = hold[side]
        mw = meas_w[side]
        d_meas = np.linalg.norm(mw - center, axis=1)
        g_meas, g_meas_runs = grip_std(mw, center, R_obj, runs[side], h)
        r3m, r3p = stage3_resid(mw, o, R_obj, h)
        rows.append({"recording": alias, "hand": side, "series": "measured",
                     "smoother": "", "anchor": "", "n_hold": int(h.sum()),
                     "n_eval": int(h.sum()),
                     "err_med_m": np.nan, "err_p95_m": np.nan,
                     "dx_med_m": np.nan, "dy_med_m": np.nan,
                     "dz_med_m": np.nan,
                     "dist_med_m": float(np.median(d_meas[h])) if h.any()
                     else np.nan, "dist_p95_m": pct(d_meas[h], 95),
                     "grip_std_m": g_meas, "stage3_resid_med_m": r3m,
                     "stage3_resid_p95_m": r3p, "anchor_err_med_m": np.nan,
                     "anchor_err_p95_m": np.nan})
        per_run += [(alias, side, "measured", "", "", *r) for r in g_meas_runs]
        sh_u = raw[f"{side}_shoulder"] * FLIP
        Lu, Lf = bones[side]
        for sname, sm, A in series:
            anchors = {"a": sh_u, "b": fk.hip_anchor(A, hip_u, offs[side])}
            for an, anc in anchors.items():
                _, wu = fk.fk_arm_series(A, side, Lu, Lf, anc)
                fw = world.world_from_cam(wu * FLIP)
                ev = h & np.isfinite(fw).all(axis=1)
                err = np.linalg.norm(fw - mw, axis=1)
                comp = fw - mw
                dist = np.linalg.norm(fw - center, axis=1)
                g, g_runs = grip_std(fw, center, R_obj, runs[side], ev)
                # anchor displacement from the measured shoulder (0 for a)
                aerr = np.linalg.norm(anc - sh_u, axis=1)
                rows.append({
                    "recording": alias, "hand": side, "series": sname,
                    "smoother": sm, "anchor": an, "n_hold": int(h.sum()),
                    "n_eval": int(ev.sum()),
                    "err_med_m": float(np.median(err[ev])) if ev.any()
                    else np.nan, "err_p95_m": pct(err[ev], 95),
                    "dx_med_m": float(np.median(comp[ev, 0])) if ev.any()
                    else np.nan,
                    "dy_med_m": float(np.median(comp[ev, 1])) if ev.any()
                    else np.nan,
                    "dz_med_m": float(np.median(comp[ev, 2])) if ev.any()
                    else np.nan,
                    "dist_med_m": float(np.median(dist[ev])) if ev.any()
                    else np.nan, "dist_p95_m": pct(dist[ev], 95),
                    "grip_std_m": g, "stage3_resid_med_m": np.nan,
                    "stage3_resid_p95_m": np.nan,
                    "anchor_err_med_m": float(np.median(aerr[ev]))
                    if ev.any() else np.nan,
                    "anchor_err_p95_m": pct(aerr[ev], 95)})
                per_run += [(alias, side, sname, sm, an, *r) for r in g_runs]
    return rows, per_run


def cm(x):
    return "   nan" if not np.isfinite(x) else f"{x * 100:6.2f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--config", default=str(V3_ROOT / "configs/default.json"))
    ap.add_argument("--recordings", default="r4,r5,r6b,r7")
    ap.add_argument("--strategies", default="baseline_hold,s2_quat_prediction")
    ap.add_argument("--smoothers", default="none,quat_one_euro")
    ap.add_argument("--variant", required=True)
    ap.add_argument("--manifest", default=None,
                    help="S2 cap manifest; default: config paths."
                         "scenario_manifest, allowed only when the config "
                         "variant equals --variant")
    ap.add_argument("--csv-dir", default=str(V3_ROOT / "output/objects"))
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--out-txt", default=None)
    ap.add_argument("--out-csv", default=None)
    args = ap.parse_args()

    cfg = apply_overrides(json.loads(Path(args.config).read_text()), args.set)
    if args.manifest is None:
        if cfg["model"]["variant"] != args.variant:
            sys.exit(f"[ERROR] config variant {cfg['model']['variant']} != "
                     f"--variant {args.variant}; pass --manifest")
        args.manifest = str(repo_path(cfg["paths"]["scenario_manifest"]))
    cfg["paths"]["scenario_manifest"] = args.manifest
    smoothers = args.smoothers.split(",")
    bad = [s for s in smoothers if s not in SMOOTHERS]
    if bad:
        sys.exit(f"[ERROR] unknown smoother(s) {bad}")
    strategies = args.strategies.split(",")
    aliases = args.recordings.split(",")
    unknown = [a for a in aliases if a not in src.STEMS]
    if unknown:
        sys.exit(f"[ERROR] unknown recording(s) {unknown}")
    if args.out_txt is None:
        args.out_txt = str(V3_ROOT /
                           f"dataset/phase5_wrist_object__{args.variant}.txt")
    if args.out_csv is None:
        args.out_csv = str(V3_ROOT /
                           f"output/objects/wrist_object__{args.variant}.csv")

    lines = []

    def out(s=""):
        print(s, flush=True)
        lines.append(s)

    out("V3 wrist-to-object bench (bench/grade_wrist_object.py; D-035 "
        "ArUco source, D-036 holding rule, D-037 FK anchors)")
    out(f"variant {args.variant}; manifest {Path(args.manifest).name}; "
        f"strategies {','.join(strategies)}; smoothers {','.join(smoothers)}"
        f"; S2 smoother_params "
        f"{json.dumps(cfg['strategy']['s2_quat_prediction'].get('smoother_params'))}")
    out(f"holding constants {json.dumps(holding.CONFIG)}")
    out("Units: cm in the tables. err = |FK wrist - measured wrist| = "
        "|v_rec - v_real| on the hand's holding frames; d* = median signed "
        "FK - measured components in the levelled desk world (x right, "
        "y up, z); dist = |wrist - box centre|; grip = frame-weighted mean "
        "over hold runs of the 3D std of R_obj^T (wrist - centre); res3 = "
        "measured-wrist residual against one object-frame grip vector per "
        "hand (thesis stage 3); anc = |anchor - measured shoulder| (0 for "
        "anchor a).")
    out()
    rows, per_run = [], []
    for alias in aliases:
        r, p = evaluate_recording(alias, cfg, args.variant, args.csv_dir,
                                  strategies, smoothers, out)
        rows += r
        per_run += p
        out()
    res = pd.DataFrame(rows)
    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(args.out_csv, index=False, float_format="%.6f")

    out("[A] |v_rec - v_real| and |wrist - centre| per recording x hand x "
        "series x anchor (cm)")
    out(f"{'rec':>4} {'hand':>5} {'series':>18} {'smoother':>13} {'anc':>3} "
        f"{'n':>5} {'err_med':>7} {'err_p95':>7} {'dx':>6} {'dy':>6} "
        f"{'dz':>6} {'dist_md':>7} {'dist95':>7} {'grip':>6} {'res3md':>6} "
        f"{'res3_95':>7} {'anc_md':>6} {'anc_95':>6}")
    for r in rows:
        out(f"{r['recording']:>4} {r['hand']:>5} {r['series']:>18} "
            f"{r['smoother']:>13} {r['anchor']:>3} {r['n_eval']:>5} "
            f"{cm(r['err_med_m']):>7} {cm(r['err_p95_m']):>7} "
            f"{cm(r['dx_med_m'])} {cm(r['dy_med_m'])} {cm(r['dz_med_m'])} "
            f"{cm(r['dist_med_m']):>7} {cm(r['dist_p95_m']):>7} "
            f"{cm(r['grip_std_m'])} {cm(r['stage3_resid_med_m'])} "
            f"{cm(r['stage3_resid_p95_m']):>7} {cm(r['anchor_err_med_m'])} "
            f"{cm(r['anchor_err_p95_m'])}")
    out()
    out("[B] grip-vector 3D std per hold run (cm): measured floor and "
        "s2_quat_prediction / oracle with anchor a")
    for rec, side, s, sm, an, a, b, n, sd, smag in per_run:
        if s in ("measured", "oracle") or (s == "s2_quat_prediction"
                                           and an == "a"):
            out(f"  {rec:>4} {side:>5} {s:>18} {sm:>13} {an:>1} run {a}-{b} "
                f"n {n:>4} std3d {sd * 100:6.2f} std|w-c| {smag * 100:5.2f}")
    out()
    if "r4" in aliases:
        out("[C] Thesis R4 (MediaPipe landmarks, v1 filtered object track; "
            "eval/reports/r4_stage3_offset_fit.md, r4_stage4_ground_truth.md)"
            " beside V3 R4 measured (rtmpose-type RGB-D wrist, raw ArUco). "
            "CAVEAT: different landmark model and wrist definition (COCO "
            "crease vs BlazePose joint, D-018), so these are context, not "
            "a like-for-like test.")
        for side in SIDES:
            t = THESIS_R4[side]
            v = res[(res.recording == "r4") & (res.hand == side)
                    & (res.series == "measured")].iloc[0]
            out(f"  {side:>5} thesis held {t['held']}, |w-c| med/p95 "
                f"{t['stage4_dist_med_cm']}/{t['stage4_dist_p95_cm']}, "
                f"stage-3 resid med/p95 {t['stage3_resid_med_cm']}/"
                f"{t['stage3_resid_p95_cm']}, runs "
                f"{[(a, b, n) for a, b, n, _ in t['runs']]} std(|w-c|) "
                f"{[s for *_, s in t['runs']]}")
            vr = [r for r in per_run if r[0] == "r4" and r[1] == side
                  and r[2] == "measured"]
            out(f"  {'':>5} V3     held {int(v['n_hold'])}, |w-c| med/p95 "
                f"{v['dist_med_m'] * 100:.1f}/{v['dist_p95_m'] * 100:.1f}, "
                f"stage-3 resid med/p95 {v['stage3_resid_med_m'] * 100:.1f}/"
                f"{v['stage3_resid_p95_m'] * 100:.1f}, runs "
                f"{[(r[5], r[6], r[7]) for r in vr]} std(|w-c|) "
                f"{[round(r[9] * 100, 2) for r in vr]}")
    Path(args.out_txt).write_text("\n".join(lines) + "\n")
    print(f"wrote {args.out_txt}\nwrote {args.out_csv}")


if __name__ == "__main__":
    main()

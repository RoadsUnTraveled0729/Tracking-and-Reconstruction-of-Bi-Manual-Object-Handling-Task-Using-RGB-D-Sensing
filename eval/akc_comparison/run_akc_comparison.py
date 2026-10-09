#!/usr/bin/env python3
"""M2: AKC (akc.py) next to our occlusion recovery on our recordings.

Experiments (eval/akc_comparison/README.md, DECISIONS.md AKC-033 on):

  P1   their protocol: r7 right arm, the three Chapter 7 windows, elbow
       (M-E) and elbow + shoulder (M-ES) masks; MASK_ALL for every
       method, MASK_Z (pixel kept, depth dropped) for AKC only; outage
       sweep 15..90 frames anchored at 445; KF sweep.
  P2a  our synthetic protocol: r7 S1_arm (elbow + wrist removed) via
       harness_recovery.masked_inputs; regression against the pinned
       Chapter 7 synthetic.json.
  P2b  our natural protocol: r5 labelled wrist frames; regression
       against the pinned eval/reports/r5_recovery_labeled.json.
  Arm-length variation (paper Table VI mirror) on r5, r6b, r7; timing.

Frames: AKC works in the camera frame (x right, y down, z forward, m).
Our solver works in the Unity flip of it (root_frame.unity_from_sensor:
y negated); every comparison is made in the camera frame after
multiplying solver-space y by -1 (AKC-042).

Outputs: eval/akc_comparison/results/*.csv, run_info.json (committed,
byte-identical across reruns except timing.csv, which holds the only
wall-clock numbers); per-frame tracks under eval/output/akc_comparison/
(gitignored). Charts: charts.py (reads results/*.csv only).

Run:  /home/luo/anaconda3/bin/python eval/akc_comparison/run_akc_comparison.py
      [--quick]  P1 only        [--charts-only]  redraw charts only
"""
import sys

sys.dont_write_bytecode = True   # no __pycache__ under v1/ or writing/

import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import platform  # noqa: E402
import subprocess  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RESULTS = HERE / "results"
TRACKS = REPO / "eval" / "output" / "akc_comparison"
for _folder in ("eval/failure", "eval/common", "eval/inspect",
                "eval/offset", "v1/kinematics"):
    sys.path.insert(0, str(REPO / _folder))
sys.path.insert(0, str(HERE))

import akc  # noqa: E402
import paths  # noqa: E402
import recovery_core as rc  # noqa: E402
import harness_recovery as hr  # noqa: E402
from root_frame import recompose_zxy  # noqa: E402
from check_v1_overlay import fk_arm_dirs  # noqa: E402

# --------------------------------------------------------------------------
# Constants (sources in DECISIONS.md)
# --------------------------------------------------------------------------

FLIP = np.array([1.0, -1.0, 1.0])     # root_frame.unity_from_sensor (AKC-042)
CM = 100.0
PEARSON_MIN_STD_M = 0.001             # AKC-036
REG_TOL_CM = 1e-6                     # brief: P2a regression tolerance
OUTAGE_ANCHOR = 445                   # AKC-040 (start of a Chapter 7 window)
OUTAGE_DURATIONS = tuple(hr.DURATIONS)    # 15..90, harness_recovery.py:104
SIDE = "right"                        # Chapter 7 synthetic side
FLOAT_FMT = "%.6f"                    # AKC-045

SYNTH_JSON = REPO / "writing/v9/audit_evidence/ch7_restructured/synthetic.json"
NATURAL_JSON = REPO / "writing/v9/audit_evidence/ch7_restructured/natural.json"
LABELED_JSON = paths.EVAL_REPORTS / "r5_recovery_labeled.json"
LABELS_JSON = REPO / "eval/labels/frames_r5/labels.json"
LABELS_META = REPO / "eval/labels/frames_r5/meta.json"

# Vendored FK (below) and the file it was copied from.
FK_SOURCE = REPO / "writing/v9/scripts/evaluate_ch7_restructured.py"
FK_SOURCE_SHA256 = \
    "344068805d7b94f504236cc7b84c5b9243526a38e8b4d4431f550b80833cbef3"

MODULES = ["v1/kinematics/occlusion.py", "v1/kinematics/occlusion_ext.py",
           "v1/kinematics/root_frame.py", "eval/failure/recovery_core.py",
           "eval/failure/harness_recovery.py",
           "eval/inspect/check_v1_overlay.py",
           "writing/v9/scripts/evaluate_ch7_restructured.py",
           "eval/akc_comparison/akc.py",
           "eval/akc_comparison/run_akc_comparison.py"]

# Radial rescale fallbacks of the full-length output (AKC-053), summed
# over every run_akc call of the run; written to run_info.json.
RESCALE_COUNT = {"runs": 0, "corrected_frames": 0, "elbow": 0,
                 "shoulder": 0}

STEMS = {"r5": paths.R5_STEM, "r6b": paths.R6B_STEM, "r7": paths.R7_STEM}
JOINTS = ("shoulder", "elbow", "wrist")
TAG = {"right": "R", "left": "L"}
OTHER = {"right": "left", "left": "right"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    p = Path(path).resolve()
    try:
        return str(p.relative_to(REPO.resolve()))
    except ValueError:
        return str(path)


INPUTS = set()


def note(path):
    INPUTS.add(Path(path).resolve())
    return path


# --------------------------------------------------------------------------
# Vendored forward kinematics.
# Source: writing/v9/scripts/evaluate_ch7_restructured.py fk() :186-195
# (thesis V9, frozen; sha256 FK_SOURCE_SHA256, asserted in main()).
# Copied verbatim except for the function name; writing/ is never
# imported from, so no bytecode or import side effects land there.
# --------------------------------------------------------------------------

def fk(angles, shoulders, lengths, side):
    tag, start = ('R', 3) if side == 'right' else ('L', 8)
    elbows, wrists = [], []
    for i, a in enumerate(angles):
        root = recompose_zxy(a[:3])
        up, fore = fk_arm_dirs(a[start:start + 3], a[start + 3:start + 5], side)
        e = shoulders[i] + lengths['upper_arm_' + tag] * (root @ up)
        elbows.append(e)
        wrists.append(e + lengths['forearm_' + tag] * (root @ fore))
    return dict(elbow=np.asarray(elbows), wrist=np.asarray(wrists))


# --------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------

def load_lm(path):
    """CSV -> dict landmark -> (xyz (n,3), vis (n,)), camera frame."""
    df = pd.read_csv(note(path))
    assert np.array_equal(df.frame.to_numpy(), np.arange(len(df))), path
    out = {}
    for side in ("left", "right"):
        for j in JOINTS:
            name = f"{side}_{j}"
            out[name] = (df[[f"{name}_{a}" for a in "xyz"]].to_numpy(float),
                         df[f"{name}_vis"].to_numpy(float))
    return out


def lengths_for(stem, side):
    p = note(paths.EVAL_REPORTS / f"{stem}_offset_fit.json")
    seg = json.loads(Path(p).read_text())["segment_lengths_m"]
    t = TAG[side]
    return {"l_f": float(seg[f"forearm_{t}"]),
            "l_u": float(seg[f"upper_arm_{t}"]),
            "l_s": float(seg["shoulder_width"])}


def win_mask(n, a, b):
    m = np.zeros(n, bool)
    m[a:b + 1] = True
    return m


# --------------------------------------------------------------------------
# AKC runner (causal, whole recording, one arm)
# --------------------------------------------------------------------------

def run_akc(lm, side, lengths, mode="ray", weights=akc.W_C, kf=None,
            ekf=False, sigma_l=akc.DEFAULT_SIGMA_L, always_correct=True,
            feedback=False, mask=None, mask_joints=(), mask_mode="all",
            drop=None, wrist_override=None, output_shrunk=False,
            ekf_anchor="filtered"):
    """Returns dict of (n,3) arrays e, s, w, ref_e, ref_s, ref_w (camera
    frame, NaN where undefined), src_* lists and per-step seconds.

    mask/mask_joints/mask_mode: synthetic masks. "all" removes the
    landmark (Obs(None, None)); "z" keeps the pixel projected from the
    unmasked xyz and drops xyz (AKC-038).
    drop: per-frame bool; removes elbow and wrist (our failure mask
    applied to AKC input, P2b "-fm" rows, AKC-048).
    output_shrunk: output the search-time points at s l (M2 behaviour,
    KF sweep row only; AKC-053).
    ekf_anchor: EKF elbow constraint anchor, "filtered" (Stage-3 Kalman
    wrist, default) or "raw" (Stage-4 wrist p_w, KF sweep row only;
    AKC-056).
    """
    arm = akc.AkcArm(side, lengths, weights=weights, kf=kf, mode=mode,
                     always_correct=always_correct, feedback=feedback,
                     ekf=ekf, sigma_l=sigma_l, output_shrunk=output_shrunk,
                     ekf_anchor=ekf_anchor)
    names = {"shoulder": f"{side}_shoulder", "elbow": f"{side}_elbow",
             "wrist": f"{side}_wrist",
             "other_shoulder": f"{OTHER[side]}_shoulder"}
    n = len(lm[names["wrist"]][0])
    res = {k: np.full((n, 3), np.nan)
           for k in ("e", "s", "w", "ref_e", "ref_s", "ref_w")}
    src = {k: [""] * n for k in ("elbow", "shoulder", "wrist")}
    dts = np.zeros(n)
    perf = time.perf_counter
    for i in range(n):
        lms = {}
        for key, name in names.items():
            xyz_all, vis_all = lm[name]
            xyz = xyz_all[i]
            xyz = xyz if np.isfinite(xyz).all() else None
            vis = float(vis_all[i])
            if drop is not None and drop[i] and key in ("elbow", "wrist"):
                lms[key] = (None, None, 0.0)
            elif mask is not None and mask[i] and key in mask_joints:
                if mask_mode == "all":
                    lms[key] = (None, None, 0.0)
                else:
                    uv = None if xyz is None else akc.project(xyz)
                    lms[key] = (None, uv, vis)
            else:
                lms[key] = (xyz, None, vis)
        obs = akc.occlusion_filter(lms, side)
        wo = None if wrist_override is None else wrist_override[i]
        t0 = perf()
        o = arm.step(obs, wrist_override=wo)
        dts[i] = perf() - t0
        for k, v in (("e", o.e), ("s", o.s), ("w", o.w), ("ref_e", o.ref_e),
                     ("ref_s", o.ref_s), ("ref_w", o.ref_w)):
            if v is not None:
                res[k][i] = v
        for j in src:
            src[j][i] = o.src.get(j, "")
        RESCALE_COUNT["corrected_frames"] += int(o.corrected)
        RESCALE_COUNT["elbow"] += int(o.rescaled_e)
        RESCALE_COUNT["shoulder"] += int(o.rescaled_s)
    RESCALE_COUNT["runs"] += 1
    res["src"] = src
    res["dt"] = dts
    return res


# --------------------------------------------------------------------------
# Our solver runner: run_variant with a solver subclass that only records
# last_points (post-recovery points, solver space) after each solve.
# --------------------------------------------------------------------------

_BASE_SOLVER = rc.RobustChainSolver
TRACE_NAMES = [f"{s}_{j}" for s in ("left", "right") for j in JOINTS]


class RecordingSolver(_BASE_SOLVER):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trace = []

    def solve(self, points, obj=None):
        out = super().solve(points, obj=obj)
        lp = self.last_points
        self.trace.append({k: np.asarray(lp[k], float).copy()
                           for k in TRACE_NAMES
                           if lp.get(k) is not None
                           and np.all(np.isfinite(lp[k]))})
        return out


def run_ours(inp, variant):
    # rc.run_variant constructs rc.RobustChainSolver by module-global name,
    # so the module attribute is swapped for RecordingSolver (same solve,
    # plus the last_points trace) for this call only and restored in the
    # finally clause, also when run_variant raises.
    rc.RobustChainSolver = RecordingSolver
    try:
        t0 = time.perf_counter()
        res = rc.run_variant(inp, variant)
        wall = time.perf_counter() - t0
    finally:
        rc.RobustChainSolver = _BASE_SOLVER
    n = inp["n"]
    tr = {k: np.full((n, 3), np.nan) for k in TRACE_NAMES}
    for i, d in enumerate(res["solver"].trace):
        for k, v in d.items():
            tr[k][i] = v
    res["trace"] = tr
    res["wall_s"] = wall
    return res


def filtered_shoulders(inp, side):
    """Unmasked filtered shoulder in solver space (Chapter 7 synthetic())."""
    df = inp["lm_df"]
    return df[[f"{side}_shoulder_{a}" for a in "xyz"]].to_numpy(float) * FLIP


def ours_points(res, shoulders_solver, seg_len, side, sh_override=None):
    """FK elbow/wrist and the shoulder used, camera frame (n,3) each."""
    sh = shoulders_solver.copy()
    if sh_override is not None:
        sh[sh_override] = res["trace"][f"{side}_shoulder"][sh_override]
    p = fk(res["angles"], sh, seg_len, side)
    return {"e": p["elbow"] * FLIP, "w": p["wrist"] * FLIP, "s": sh * FLIP}


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------

MET_COLS = ["n", "n_missing", "rmse_x", "rmse_y", "rmse_z", "rmse_3d",
            "pearson_x", "pearson_y", "pearson_z", "median", "p95", "max"]


def metrics(pred, ref, pearson=True):
    """Errors in cm. Pearson r per axis; NaN when the reference std over
    the scored frames is below PEARSON_MIN_STD_M (AKC-036), when the
    prediction is constant on that axis (hold-last; r undefined), or
    when pearson is False (pooled rows, AKC-037)."""
    pred = np.asarray(pred, float).reshape(-1, 3)
    ref = np.asarray(ref, float).reshape(-1, 3)
    ok = np.isfinite(pred).all(1) & np.isfinite(ref).all(1)
    out = {"n": int(ok.sum()), "n_missing": int((~ok).sum())}
    if not ok.any():
        out.update({k: np.nan for k in MET_COLS[2:]})
        return out
    d = (pred[ok] - ref[ok]) * CM
    e = np.linalg.norm(d, axis=1)
    for j, a in enumerate("xyz"):
        out[f"rmse_{a}"] = float(np.sqrt(np.mean(d[:, j] ** 2)))
        r = np.nan
        if pearson and ok.sum() > 2 and ref[ok][:, j].std() >= \
                PEARSON_MIN_STD_M and np.ptp(pred[ok][:, j]) > 0:
            r = float(np.corrcoef(pred[ok][:, j], ref[ok][:, j])[0, 1])
        out[f"pearson_{a}"] = r
    out["rmse_3d"] = float(np.sqrt(np.mean(e ** 2)))
    out["median"] = float(np.median(e))
    out["p95"] = float(np.percentile(e, 95, method="linear"))
    out["max"] = float(e.max())
    return out


def write_csv(df, name):
    RESULTS.mkdir(parents=True, exist_ok=True)
    df.to_csv(RESULTS / name, index=False, float_format=FLOAT_FMT,
              lineterminator="\n")
    print(f"OK: wrote results/{name} ({len(df)} rows)", flush=True)


def write_track(name, frames, arrays, extra=None):
    TRACKS.mkdir(parents=True, exist_ok=True)
    cols = {"frame": frames}
    for k, v in arrays.items():
        for j, a in enumerate("xyz"):
            cols[f"{k}_{a}"] = v[:, j]
    for k, v in (extra or {}).items():
        cols[k] = v
    pd.DataFrame(cols).to_csv(TRACKS / name, index=False,
                              float_format=FLOAT_FMT, lineterminator="\n")


# --------------------------------------------------------------------------
# Context shared by the experiments
# --------------------------------------------------------------------------

class Ctx:
    pass


def chapter7_windows():
    sel = json.loads(Path(note(SYNTH_JSON)).read_text())["selection"]
    wins = [(int(w["start"]), int(w["stop"]), w["window"])
            for w in sel["selected"]]
    assert [(a, b) for a, b, _ in wins] == [(490, 534), (445, 489),
                                            (557, 601)], wins
    return wins


def build_ctx():
    c = Ctx()
    c.wins = chapter7_windows()
    c.stem = paths.R7_STEM
    c.raw = load_lm(paths.lm_raw(c.stem))
    c.filt = load_lm(paths.lm_filtered(c.stem))
    c.n = len(c.raw["right_wrist"][0])
    c.len = lengths_for(c.stem, SIDE)
    c.base = rc.build_inputs(c.stem)
    assert c.base["n"] == c.n
    c.w_hat_before = c.base["w_hat_solver"][SIDE].copy()
    c.plain = run_ours(c.base, "plain")
    c.sh_solver = filtered_shoulders(c.base, SIDE)
    c.plain_pts = ours_points(c.plain, c.sh_solver, c.base["seg_len"], SIDE)
    c.meas = {j[0]: c.filt[f"{SIDE}_{j}"][0] for j in JOINTS}   # R-meas
    c.akc_cfg = {"AKC-literal": dict(mode="literal"),
                 "AKC-ray": dict(mode="ray"),
                 "AKC-EKF": dict(mode="ray", ekf=True)}
    c.unmasked = {m: run_akc(c.raw, SIDE, c.len, **kw)
                  for m, kw in c.akc_cfg.items()}
    c.asserts = {}
    return c


# --------------------------------------------------------------------------
# P1: their protocol on r7
# --------------------------------------------------------------------------

MASKS = {"M-E": ("elbow",), "M-ES": ("elbow", "shoulder")}


def null_lm(base, a, b, joints, side=SIDE):
    inp = dict(base)
    df = base["lm_df"].copy()
    cols = [f"{side}_{j}_{ax}" for j in joints for ax in "xyz"]
    df.loc[df.index[a:b + 1], cols] = np.nan
    inp["lm_df"] = df
    return inp


def score_rows(rows, base_row, pred, refs, a, b, joints):
    for jn in joints:
        k = jn[0]
        for rname, ref in refs.items():
            if ref is None or ref.get(k) is None:
                continue
            m = metrics(pred[k][a:b + 1], ref[k][a:b + 1])
            rows.append(dict(base_row, joint=jn, reference=rname, **m))


def hold(track, a, b):
    """Reference value at a-1 held over [a, b] (AKC-039)."""
    out = track.copy()
    out[a:b + 1] = track[a - 1]
    return out


def p1(c):
    rows, per_window = [], {}
    kf_self = {"e": c.unmasked["AKC-ray"]["ref_e"],
               "s": c.unmasked["AKC-ray"]["ref_s"]}
    frames = np.arange(c.n)
    c.p1_runs = {}
    # unmasked sanity rows (mask none): every method against R-meas
    for a, b, wname in c.wins:
        base_row = dict(recording="r7", window=f"{a}-{b}", mask="none",
                        mask_mode="none", reference_note="")
        for m in c.akc_cfg:
            u = c.unmasked[m]
            score_rows(rows, dict(base_row, method=m),
                       {"e": u["e"], "s": u["s"]}, {"R-meas": c.meas},
                       a, b, ("elbow", "shoulder"))
        score_rows(rows, dict(base_row, method="KF-only"), kf_self,
                   {"R-meas": c.meas}, a, b, ("elbow", "shoulder"))
        score_rows(rows, dict(base_row, method="ours-plain"),
                   c.plain_pts, {"R-meas": c.meas}, a, b,
                   ("elbow", "shoulder"))
    for mask_name, mjoints in MASKS.items():
        scored = ("elbow",) if mask_name == "M-E" else ("elbow", "shoulder")
        for a, b, wname in c.wins:
            wm = win_mask(c.n, a, b)
            wlab = f"{a}-{b}"
            # --- AKC, both mask modes
            for mode in ("all", "z"):
                mm = "MASK_ALL" if mode == "all" else "MASK_Z"
                ray_run = None
                for m, kw in c.akc_cfg.items():
                    r = run_akc(c.raw, SIDE, c.len, mask=wm,
                                mask_joints=mjoints, mask_mode=mode, **kw)
                    if m == "AKC-ray":
                        ray_run = r
                    c.p1_runs[(mask_name, mm, wlab, m)] = r
                    u = c.unmasked[m]
                    score_rows(rows, dict(recording="r7", window=wlab,
                                          mask=mask_name, mask_mode=mm,
                                          method=m, reference_note=""),
                               {"e": r["e"], "s": r["s"]},
                               {"R-self": {"e": u["e"], "s": u["s"]},
                                "R-meas": c.meas}, a, b, scored)
                    write_track(
                        f"tracks_r7_p1-{wlab}-{mask_name}-{mm}_{m}.csv",
                        frames, {k: r[k] for k in ("e", "s", "w", "ref_e",
                                                   "ref_s", "ref_w")},
                        {"masked": wm.astype(int), "src_e": r["src"]["elbow"],
                         "src_s": r["src"]["shoulder"],
                         "src_w": r["src"]["wrist"]})
                score_rows(rows, dict(recording="r7", window=wlab,
                                      mask=mask_name, mask_mode=mm,
                                      method="KF-only",
                                      reference_note="ref_e/ref_s of AKC-ray"),
                           {"e": ray_run["ref_e"], "s": ray_run["ref_s"]},
                           {"R-self": kf_self, "R-meas": c.meas}, a, b,
                           scored)
            # --- hold-last (MASK_ALL only)
            for rname, ref in (("R-self", c.plain_pts), ("R-meas", c.meas)):
                held = {k: hold(ref[k], a, b) for k in ("e", "s")}
                score_rows(rows, dict(recording="r7", window=wlab,
                                      mask=mask_name, mask_mode="MASK_ALL",
                                      method="hold-last",
                                      reference_note="R-self = ours plain FK"),
                           held, {rname: ref}, a, b, scored)
            # --- ours
            inp = null_lm(c.base, a, b, mjoints)
            assert np.array_equal(inp["w_hat_solver"][SIDE], c.w_hat_before,
                                  equal_nan=True)
            sh_over = wm if "shoulder" in mjoints else None
            for m, variant in (("ours-memory", "masked"),
                               ("ours-IK", "recovery")):
                r = run_ours(inp, variant)
                c.p1_runs[(mask_name, "MASK_ALL", wlab, m)] = r
                pts = ours_points(r, c.sh_solver, c.base["seg_len"], SIDE,
                                  sh_over)
                r["pts"] = pts
                score_rows(rows, dict(recording="r7", window=wlab,
                                      mask=mask_name, mask_mode="MASK_ALL",
                                      method=m, reference_note=""),
                           pts, {"R-self": c.plain_pts, "R-meas": c.meas},
                           a, b, scored)
                write_track(f"tracks_r7_p1-{wlab}-{mask_name}-MASK_ALL_{m}.csv",
                            frames, pts, {"masked": wm.astype(int)})
                if mask_name == "M-E":
                    grow = (r["solver"].recovered.get("right_elbow", 0)
                            - c.plain["solver"].recovered.get("right_elbow", 0))
                    wr_same = np.array_equal(
                        r["trace"]["right_wrist"][a:b + 1],
                        c.plain["trace"]["right_wrist"][a:b + 1],
                        equal_nan=True)
                    key = f"p1_mask_injection_{wlab}_{m}"
                    c.asserts[key] = dict(recovered_elbow_growth=int(grow),
                                          window=b - a + 1,
                                          wrist_unchanged=bool(wr_same))
                    assert grow == b - a + 1, (key, grow)
                    assert wr_same, key
            print(f"PASS: P1 {mask_name} window {wlab}", flush=True)
    df = pd.DataFrame(rows)
    # pooled rows over the three windows, recomputed from the per-frame
    # arrays (not averages of window statistics); Pearson NaN (AKC-037)
    df_pooled = pooled_p1(c, df)
    out = pd.concat([df, df_pooled], ignore_index=True)
    cols = ["recording", "window", "mask", "mask_mode", "method", "joint",
            "reference", "reference_note"] + MET_COLS
    out = out[cols]
    write_csv(out, "p1_synthetic_elbow.csv")
    return out


def _pred_ref(c, mask_name, mm, wlab, method, joint, reference):
    """Recover the (pred, ref) window arrays for one P1 row."""
    a, b = (int(x) for x in wlab.split("-"))
    k = joint[0]
    kf_self = {"e": c.unmasked["AKC-ray"]["ref_e"],
               "s": c.unmasked["AKC-ray"]["ref_s"]}
    if mask_name == "none":
        if method in c.akc_cfg:
            pred = c.unmasked[method][k]
        elif method == "KF-only":
            pred = kf_self[k]
        else:
            pred = c.plain_pts[k]
        ref = c.meas[k]
    elif method in c.akc_cfg:
        pred = c.p1_runs[(mask_name, mm, wlab, method)][k]
        ref = c.unmasked[method][k] if reference == "R-self" else c.meas[k]
    elif method == "KF-only":
        r = c.p1_runs[(mask_name, mm, wlab, "AKC-ray")]
        pred = r["ref_" + k]
        ref = kf_self[k] if reference == "R-self" else c.meas[k]
    elif method == "hold-last":
        ref = c.plain_pts[k] if reference == "R-self" else c.meas[k]
        pred = hold(ref, a, b)
    else:
        pred = c.p1_runs[(mask_name, mm, wlab, method)]["pts"][k]
        ref = c.plain_pts[k] if reference == "R-self" else c.meas[k]
    return pred[a:b + 1], ref[a:b + 1]


def pooled_p1(c, df):
    rows = []
    keys = ["recording", "mask", "mask_mode", "method", "joint", "reference",
            "reference_note"]
    for kv, g in df.groupby(keys, sort=False):
        d = dict(zip(keys, kv))
        P, R = [], []
        for wlab in g["window"]:
            p, r = _pred_ref(c, d["mask"], d["mask_mode"], wlab, d["method"],
                             d["joint"], d["reference"])
            P.append(p)
            R.append(r)
        m = metrics(np.concatenate(P), np.concatenate(R), pearson=False)
        rows.append(dict(d, window="pooled", **m))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# P1 outage sweep
# --------------------------------------------------------------------------

def outage(c):
    rows = []
    kf_self = c.unmasked["AKC-ray"]["ref_e"]
    for dur in OUTAGE_DURATIONS:
        a, b = OUTAGE_ANCHOR, OUTAGE_ANCHOR + dur - 1
        wm = win_mask(c.n, a, b)
        r = run_akc(c.raw, SIDE, c.len, mode="ray", mask=wm,
                    mask_joints=("elbow",), mask_mode="all")
        preds = {"KF-only": (r["ref_e"], kf_self),
                 "AKC-ray": (r["e"], c.unmasked["AKC-ray"]["e"])}
        inp = null_lm(c.base, a, b, ("elbow",))
        for m, variant in (("ours-memory", "masked"), ("ours-IK", "recovery")):
            o = run_ours(inp, variant)
            pts = ours_points(o, c.sh_solver, c.base["seg_len"], SIDE)
            preds[m] = (pts["e"], c.plain_pts["e"])
        for m, (pred, rself) in preds.items():
            for rname, ref in (("R-self", rself), ("R-meas", c.meas["e"])):
                rows.append(dict(recording="r7", anchor=a, duration=dur,
                                 window=f"{a}-{b}", mask="M-E",
                                 mask_mode="MASK_ALL", method=m,
                                 joint="elbow", reference=rname,
                                 **metrics(pred[a:b + 1], ref[a:b + 1])))
        print(f"PASS: outage {dur}", flush=True)
    df = pd.DataFrame(rows)
    write_csv(df, "p1_outage_sweep.csv")
    return df


# --------------------------------------------------------------------------
# KF sweep (reported, never used to retune; AKC-044)
# --------------------------------------------------------------------------

def sweep_configs():
    d = dict(akc.DEFAULT_KF)
    cfgs = [("default", "-", {}, "raw")]
    for v in (1.0, 2.5, 5.0, 10.0, 20.0):
        cfgs.append(("sigma_a", v, dict(kf=dict(d, sigma_a=v)), "raw"))
    ratio = d["sigma_z"] / d["sigma_xy"]
    for v in (0.005, 0.01, 0.02):
        cfgs.append(("sigma_xy", v, dict(kf=dict(d, sigma_xy=v,
                                                 sigma_z=ratio * v)), "raw"))
    for v in (2.0, 5.0, 10.0):
        cfgs.append(("sigma_z_ratio", v,
                     dict(kf=dict(d, sigma_z=v * d["sigma_xy"])), "raw"))
    for v in (0.005, 0.02, 0.05):
        cfgs.append(("sigma_l_ekf", v, dict(ekf=True, sigma_l=v), "raw"))
    # EKF anchored on the Stage-4 wrist p_w (M2 behaviour) at the default
    # sigma_l (AKC-056).
    cfgs.append(("ekf_anchor", "raw", dict(ekf=True, ekf_anchor="raw"),
                 "raw"))
    for name, w in (("W_A", akc.W_A), ("W_B", akc.W_B), ("W_C", akc.W_C)):
        cfgs.append(("weights", name, dict(weights=w), "raw"))
    for v in (True, False):
        cfgs.append(("always_correct", v, dict(always_correct=v), "raw"))
    for v in (False, True):
        cfgs.append(("feedback", v, dict(feedback=v), "raw"))
    for v in ("ray", "literal"):
        cfgs.append(("mode", v, dict(mode=v), "raw"))
    cfgs.append(("input", "filtered", {}, "filtered"))
    cfgs.append(("output_shrunk", True, dict(output_shrunk=True), "raw"))
    return cfgs


def kf_sweep(c):
    rows = []
    for param, value, kw, src in sweep_configs():
        kw = dict(dict(mode="ray"), **kw)
        lm = c.raw if src == "raw" else c.filt
        u = run_akc(lm, SIDE, c.len, **kw)
        acc = {("AKC", "R-self"): ([], []), ("AKC", "R-meas"): ([], []),
               ("KF-only", "R-self"): ([], []),
               ("KF-only", "R-meas"): ([], [])}
        for a, b, _ in c.wins:
            wm = win_mask(c.n, a, b)
            r = run_akc(lm, SIDE, c.len, mask=wm, mask_joints=("elbow",),
                        mask_mode="all", **kw)
            sl = slice(a, b + 1)
            for (meth, rname), (P, R) in acc.items():
                P.append(r["e"][sl] if meth == "AKC" else r["ref_e"][sl])
                if rname == "R-meas":
                    R.append(c.meas["e"][sl])
                else:
                    R.append(u["e"][sl] if meth == "AKC" else u["ref_e"][sl])
        for (meth, rname), (P, R) in acc.items():
            m = metrics(np.concatenate(P), np.concatenate(R), pearson=False)
            rows.append(dict(param=param, value=str(value), input=src,
                             method=meth, joint="elbow", reference=rname,
                             windows="490-534,445-489,557-601",
                             mask="M-E", mask_mode="MASK_ALL",
                             n=m["n"], median=m["median"],
                             rmse_3d=m["rmse_3d"], p95=m["p95"],
                             max=m["max"]))
        print(f"OK: sweep {param}={value}", flush=True)
    df = pd.DataFrame(rows)
    write_csv(df, "kf_sweep.csv")
    return df


# --------------------------------------------------------------------------
# P2a: our synthetic protocol (r7 S1_arm)
# --------------------------------------------------------------------------

P2A_PINNED = {"hold-last": "hold-last", "ours-memory": "direction memory",
              "ours-object": "object-assisted"}


def p2a(c):
    pinned = json.loads(Path(SYNTH_JSON).read_text())["results"]
    pin = {(r["start"], r["method"], r["joint"]): r for r in pinned}
    rows = []
    ray_u = c.unmasked["AKC-ray"]
    for a, b, wname in c.wins:
        wlab = f"{a}-{b}"
        inp, em = hr.masked_inputs(c.stem, c.n, SIDE, (a, b), "S1_arm")
        assert em.sum() == hr.WIN and np.array_equal(em, win_mask(c.n, a, b))
        w_hat_before = inp["w_hat_solver"][SIDE].copy()
        runs = {"hold-last": rc.run_hold_baseline(inp),
                "ours-memory": run_ours(inp, "masked"),
                "ours-object": run_ours(inp, "recovery")}
        assert np.array_equal(inp["w_hat_solver"][SIDE], w_hat_before,
                              equal_nan=True)
        assert np.isfinite(w_hat_before[a:b + 1]).all()
        preds = {}
        for m, r in runs.items():
            preds[m] = ours_points(r, c.sh_solver, c.base["seg_len"], SIDE)
        # Chapter 7 regression (solver-space norms equal camera-space norms)
        for m, pts in preds.items():
            for jn in ("elbow", "wrist"):
                k = jn[0]
                err = np.linalg.norm(pts[k][a:b + 1]
                                     - c.plain_pts[k][a:b + 1], axis=1) * CM
                want = pin[(a, P2A_PINNED[m], jn)]["median"]
                diff = abs(float(np.median(err)) - want)
                c.asserts[f"p2a_regression_{wlab}_{m}_{jn}"] = dict(
                    median=float(np.median(err)), pinned=want,
                    abs_diff=diff)
                assert diff <= REG_TOL_CM, (wlab, m, jn, diff)
        w_cam = w_hat_before * FLIP
        for m, wo in (("AKC-ray", None), ("AKC-hybrid", w_cam)):
            r = run_akc(c.raw, SIDE, c.len, mode="ray", mask=em,
                        mask_joints=("elbow", "wrist"), mask_mode="all",
                        wrist_override=wo)
            preds[m] = {"e": r["e"], "w": r["w"], "s": r["s"]}
            srcw = r["src"]["wrist"][a:b + 1]
            want_src = "kf_pred" if wo is None else "override"
            c.asserts[f"p2a_wrist_source_{wlab}_{m}"] = sorted(set(srcw))
            assert set(srcw) == {want_src}, (m, set(srcw))
            write_track(f"tracks_r7_p2a-{wlab}-S1_arm_{m}.csv",
                        np.arange(c.n), {k: r[k] for k in ("e", "s", "w")},
                        {"masked": em.astype(int),
                         "src_w": r["src"]["wrist"]})
        for m, pts in preds.items():
            rself = ({"e": ray_u["e"], "w": ray_u["w"]} if m.startswith("AKC")
                     else c.plain_pts)
            for jn in ("elbow", "wrist"):
                k = jn[0]
                for rname, ref in (("R-self", rself[k]),
                                   ("R-meas", c.meas[k])):
                    rows.append(dict(recording="r7", window=wlab,
                                     window_label=wname, mask="S1_arm",
                                     mask_mode="MASK_ALL", method=m,
                                     joint=jn, reference=rname,
                                     **metrics(pts[k][a:b + 1],
                                               ref[a:b + 1])))
        print(f"PASS: P2a window {wlab} (Chapter 7 regression)", flush=True)
    df = pd.DataFrame(rows)
    write_csv(df, "p2a_wrist_synthetic.csv")
    return df


# --------------------------------------------------------------------------
# P2b: our natural protocol (r5 labelled wrists)
# --------------------------------------------------------------------------

ANGLE_COLS = hr.ANGLE_COLS
PINNED_METHODS = ("recovered", "measured", "hold", "plain_fk", "hold_fk",
                  "recovery_fk")


def _stat2(v):
    """eval_labeled_recovery.stat(): numpy default percentile, 2 dp."""
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return {"n": 0}
    return {"n": int(v.size), "median": round(float(np.median(v)), 2),
            "p95": round(float(np.percentile(v, 95)), 2),
            "max": round(float(v.max()), 2)}


def p2b(c):
    stem = paths.R5_STEM
    pinned = json.loads(Path(note(LABELED_JSON)).read_text())
    natural = json.loads(Path(note(NATURAL_JSON)).read_text())
    labels = json.loads(Path(note(LABELS_JSON)).read_text())
    note(LABELS_META)
    inp = rc.build_inputs(stem)
    n_inp = inp["n"]
    lm = inp["lm_df"]
    angles = {}
    for name in ("plain", "hold", "recovery"):
        p = note(paths.EVAL_OUT / "recovery_r5" / f"angles_{name}.csv")
        angles[name] = pd.read_csv(p)[ANGLE_COLS].to_numpy(float)

    def lm_pt(f, name):
        v = lm.loc[f, [f"{name}_{a}" for a in "xyz"]].to_numpy(float)
        return v * FLIP if np.all(np.isfinite(v)) else np.full(3, np.nan)

    # 1. recompute the pinned per-frame values of ours (regression)
    recomputed = 0
    for row in pinned["rows"]:
        f, side = row["frame"], row["side"]
        L = labels[str(f)][side]
        truth = np.asarray(L["xyz_cam"], float) * FLIP
        est = {"recovered": inp["w_hat_solver"][side][f],
               "measured": lm_pt(f, f"{side}_wrist")}
        fail = inp["fail"][side]
        held = np.full(3, np.nan)
        for g in range(f - 1, -1, -1):
            if not fail[g]:
                cand = lm_pt(g, f"{side}_wrist")
                if np.all(np.isfinite(cand)):
                    held = cand
                    break
        est["hold"] = held
        sh = lm_pt(f, f"{side}_shoulder")
        for name in ("plain", "hold", "recovery"):
            p = fk(angles[name][f:f + 1], sh[None, :], inp["seg_len"], side)
            est[f"{name}_fk"] = p["wrist"][0]
        for m in PINNED_METHODS:
            d = (float(np.linalg.norm(est[m] - truth)) * CM
                 if np.all(np.isfinite(est[m])) else float("nan"))
            want = row[f"{m}_cm"]
            got = round(d, 2)
            want_nan = want is None or (isinstance(want, float)
                                        and np.isnan(want))
            ok = (np.isnan(got) and want_nan) or (got == want)
            assert ok, (f, side, m, got, want)
            recomputed += 1
    for side in ("left", "right"):
        for m in ("plain_fk", "hold_fk", "recovery_fk"):
            v = [r[f"{m}_cm"] for r in pinned["rows"]
                 if r["side"] == side and r["group"] == "failure"]
            s = _stat2(v)
            ps = pinned["summary"]["failure"][side][m]
            ns = natural["summary"]["failure"][side][m]
            assert s == {k: ps[k] for k in ("n", "median", "p95", "max")}, \
                (side, m, s, ps)
            assert (ns["n"], ns["median"], ns["p95"], ns["maximum"]) == \
                (ps["n"], ps["median"], ps["p95"], ps["max"]), (side, m)
    c.asserts["p2b_regression"] = dict(per_frame_values_recomputed=recomputed,
                                       summary_equal=True)
    print(f"PASS: P2b ours regression ({recomputed} per-frame values)",
          flush=True)

    # 2. AKC runs over the whole recording (causal), both arms
    csvs = {"vis0": paths.lm_raw_vis0(stem), "raw": paths.lm_raw(stem)}
    lms = {k: load_lm(v) for k, v in csvs.items()}
    n_all = len(lms["raw"]["right_wrist"][0])
    runs = {}
    for side in ("left", "right"):
        L = lengths_for(stem, side)
        fail = np.zeros(n_all, bool)
        fail[:n_inp] = inp["fail"][side]
        w_cam = np.full((n_all, 3), np.nan)
        w_cam[:n_inp] = inp["w_hat_solver"][side] * FLIP
        for cname, lmx in lms.items():
            for meth, kw in (("AKC-ray", {}),
                             ("AKC-hybrid", dict(wrist_override=w_cam)),
                             ("AKC-ray-fm", dict(drop=fail)),
                             ("AKC-hybrid-fm", dict(drop=fail,
                                                    wrist_override=w_cam))):
                r = run_akc(lmx, side, L, mode="ray", **kw)
                runs[(side, cname, meth)] = r
                write_track(f"tracks_r5_p2b-{cname}-{side}_{meth}.csv",
                            np.arange(n_all),
                            {k: r[k] for k in ("e", "s", "w", "ref_w")},
                            {"src_w": r["src"]["wrist"],
                             "fail": fail.astype(int)})
    c.r5_runs = runs

    # 3. per-frame label errors
    rows = []
    for row in pinned["rows"]:
        f, side, grp = row["frame"], row["side"], row["group"]
        lab = np.asarray(labels[str(f)][side]["xyz_cam"], float)
        for m in PINNED_METHODS:
            rows.append(dict(kind="frame", input="pinned", side=side,
                             group=grp, frame=f, method=f"ours-{m}",
                             wrist_src="", error_cm=row[f"{m}_cm"]))
        for (s2, cname, meth), r in runs.items():
            if s2 != side:
                continue
            w = r["w"][f]
            e = (float(np.linalg.norm(w - lab)) * CM
                 if np.isfinite(w).all() else np.nan)
            rows.append(dict(kind="frame", input=cname, side=side, group=grp,
                             frame=f, method=meth,
                             wrist_src=r["src"]["wrist"][f], error_cm=e))
            if meth == "AKC-hybrid-fm" and r["src"]["wrist"][f] == "override":
                # our object wrist used as is: must equal ours-recovered
                assert round(e, 2) == row["recovered_cm"], (f, side, e)
    fr = pd.DataFrame(rows)
    summ = []
    for (inp_name, side, grp, meth), g in fr.groupby(
            ["input", "side", "group", "method"], sort=False):
        if inp_name == "pinned":
            # copied, not recomputed: the pinned summary is the reference
            ps = pinned["summary"][grp][side][meth[len("ours-"):]]
            summ.append(dict(kind="summary", input=inp_name, side=side,
                             group=grp, frame=-1, method=meth, wrist_src="",
                             error_cm=np.nan, n=ps["n"], median=ps["median"],
                             p95=ps["p95"], max=ps["max"]))
            continue
        v = g["error_cm"].to_numpy(float)
        v = v[np.isfinite(v)]
        summ.append(dict(kind="summary", input=inp_name, side=side,
                         group=grp, frame=-1, method=meth, wrist_src="",
                         error_cm=np.nan, n=int(v.size),
                         median=float(np.median(v)) if v.size else np.nan,
                         p95=float(np.percentile(v, 95, method="linear"))
                         if v.size else np.nan,
                         max=float(v.max()) if v.size else np.nan))
    df = pd.concat([fr, pd.DataFrame(summ)], ignore_index=True)
    for k in ("n", "median", "p95", "max"):
        if k not in df:
            df[k] = np.nan
    write_csv(df, "p2b_natural_labels.csv")
    return df


# --------------------------------------------------------------------------
# Arm-length variation (paper Table VI mirror)
# --------------------------------------------------------------------------

def r5_elbow_only_frames(lm, side="right"):
    """Frames where AKC's gate drops the elbow but keeps the wrist: xyz
    missing or vis < 0.7 on the elbow, finite xyz and vis >= 0.7 on the
    wrist, in the 0.5-gated raw CSV (AKC-047)."""
    e, ev = lm[f"{side}_elbow"]
    w, wv = lm[f"{side}_wrist"]
    with np.errstate(invalid="ignore"):
        eok = np.isfinite(e).all(1) & (ev >= akc.VIS_MIN)
        wok = np.isfinite(w).all(1) & (wv >= akc.VIS_MIN)
    return ~eok & wok


def arm_lengths(c, full=True):
    rows = []

    def add(alias, side, region, method, e, s, w, frames):
        st = akc.arm_length_stats(e[frames], s[frames], w[frames])
        row = dict(recording=alias, side=side, region=region, method=method,
                   n=st["n"])
        for seg in ("forearm", "upper"):
            for k in ("min", "max", "range", "std"):
                row[f"{seg}_{k}_cm"] = st[f"{seg}_{k}"] * CM
        rows.append(row)

    stems = STEMS if full else {"r7": paths.R7_STEM}
    for alias, stem in stems.items():
        raw = c.raw if alias == "r7" else load_lm(paths.lm_raw(stem))
        n = len(raw["right_wrist"][0])
        if alias == "r7":
            base, plain = c.base, c.plain
        else:
            base = rc.build_inputs(stem)
            plain = run_ours(base, "plain")
        allf = np.ones(n, bool)
        for side in ("right", "left"):
            L = lengths_for(stem, side)
            add(alias, side, "full", "raw", raw[f"{side}_elbow"][0],
                raw[f"{side}_shoulder"][0], raw[f"{side}_wrist"][0], allf)
            akc_runs = {}
            for m, kw in (("AKC-literal", dict(mode="literal")),
                          ("AKC-ray", dict(mode="ray"))):
                if alias == "r7" and side == SIDE:
                    akc_runs[m] = c.unmasked[m]
                else:
                    akc_runs[m] = run_akc(raw, side, L, **kw)
            k = akc_runs["AKC-ray"]
            add(alias, side, "full", "KF-only", k["ref_e"], k["ref_s"],
                k["ref_w"], allf)
            for m, r in akc_runs.items():
                add(alias, side, "full", m, r["e"], r["s"], r["w"], allf)
            sh = filtered_shoulders(base, side)
            pts = ours_points(plain, sh, base["seg_len"], side)
            nb = base["n"]
            add(alias, side, "full", "ours", pts["e"], pts["s"], pts["w"],
                np.ones(nb, bool))
            if alias == "r5" and side == "right":
                eo = r5_elbow_only_frames(raw, side)
                c.asserts["r5_right_elbow_only_frames"] = int(eo.sum())
                add(alias, side, "r5 natural elbow-only", "raw",
                    raw[f"{side}_elbow"][0], raw[f"{side}_shoulder"][0],
                    raw[f"{side}_wrist"][0], eo)
                add(alias, side, "r5 natural elbow-only", "KF-only",
                    k["ref_e"], k["ref_s"], k["ref_w"], eo)
                for m, r in akc_runs.items():
                    add(alias, side, "r5 natural elbow-only", m, r["e"],
                        r["s"], r["w"], eo)
                add(alias, side, "r5 natural elbow-only", "ours", pts["e"],
                    pts["s"], pts["w"], eo[:nb])
            if alias == "r7" and side == SIDE:
                fore = np.linalg.norm(raw["right_elbow"][0]
                                      - raw["right_wrist"][0], axis=1)
                fore = fore[np.isfinite(fore)]
                p5, p95 = np.percentile(fore, [5, 95], method="linear")
                kr = akc.arm_length_stats(k["e"], k["s"], k["w"])
                c.asserts["sanity_r7_forearm_band"] = dict(
                    raw_p5_m=float(p5), raw_p95_m=float(p95),
                    akc_ray_min_m=kr["forearm_min"],
                    akc_ray_max_m=kr["forearm_max"],
                    inside=bool(p5 <= kr["forearm_min"]
                                and kr["forearm_max"] <= p95))
    # inside the P1 masked windows (M-E, MASK_ALL)
    for a, b, _ in c.wins:
        wl = f"{a}-{b}"
        fr = win_mask(c.n, a, b)
        ray = c.p1_runs[("M-E", "MASK_ALL", wl, "AKC-ray")]
        add("r7", SIDE, f"P1 M-E {wl}", "KF-only", ray["ref_e"],
            ray["ref_s"], ray["ref_w"], fr)
        for m in ("AKC-literal", "AKC-ray"):
            r = c.p1_runs[("M-E", "MASK_ALL", wl, m)]
            add("r7", SIDE, f"P1 M-E {wl}", m, r["e"], r["s"], r["w"], fr)
        for m in ("ours-memory", "ours-IK"):
            p = c.p1_runs[("M-E", "MASK_ALL", wl, m)]["pts"]
            add("r7", SIDE, f"P1 M-E {wl}", m, p["e"], p["s"], p["w"], fr)
    df = pd.DataFrame(rows)
    write_csv(df, "arm_length_range.csv")
    return df


# --------------------------------------------------------------------------
# Timing (wall clock; timing.csv is the only non-reproducible output)
# --------------------------------------------------------------------------

def timing(c):
    rows = []
    for m, r in c.unmasked.items():
        us = r["dt"] * 1e6
        rows.append(dict(recording="r7", method=m, scope="AkcArm.step",
                         n=len(us), mean_us=float(us.mean()),
                         p95_us=float(np.percentile(us, 95,
                                                    method="linear")),
                         note="perf_counter around AkcArm.step only; "
                              "occlusion_filter and CSV access excluded"))
    for m, variant in (("ours-plain", "plain"), ("ours-memory", "masked"),
                       ("ours-IK", "recovery")):
        r = run_ours(c.base, variant)
        rows.append(dict(recording="r7", method=m, scope="run_variant",
                         n=c.n, mean_us=r["wall_s"] / c.n * 1e6,
                         p95_us=np.nan,
                         note="run_variant wall time / n; includes pandas "
                              "iterrows and the recording solver subclass"))
    df = pd.DataFrame(rows)
    write_csv(df, "timing.csv")
    return df


# --------------------------------------------------------------------------
# run_info.json (no wall-clock fields)
# --------------------------------------------------------------------------

def run_info(c, quick):
    for stem in STEMS.values():
        for p in (paths.lm_raw(stem), paths.lm_filtered(stem),
                  paths.calib_for(stem), paths.object_world_filtered(stem),
                  paths.EVAL_REPORTS / f"{stem}_offset_fit.json",
                  paths.EVAL_REPORTS / f"{stem}_inspection.json",
                  paths.EVAL_OUT / f"recovery_{paths.ALIAS[stem]}"
                  / "failure_mask.csv"):
            if Path(p).exists():
                note(p)
    note(paths.lm_raw_vis0(paths.R5_STEM))
    info = {
        "script": "eval/akc_comparison/run_akc_comparison.py",
        "mode": "quick (P1 only)" if quick else "full",
        "python": platform.python_version(),
        "numpy": np.__version__, "pandas": pd.__version__,
        "dt_s": akc.DEFAULT_KF["dt"],
        "akc_defaults": {"kf": akc.DEFAULT_KF, "sigma_l": akc.DEFAULT_SIGMA_L,
                         "vis_min": akc.VIS_MIN, "prox_frac": akc.PROX_FRAC,
                         "weights": {k: vars(w) | {"theta_deg":
                                                   list(w.theta_deg)}
                                     for k, w in (("W_A", akc.W_A),
                                                  ("W_B", akc.W_B),
                                                  ("W_C", akc.W_C))},
                         "default_weights": "W_C", "default_mode": "ray",
                         "always_correct": True, "feedback": False,
                         "ekf_anchor": "filtered"},
        "lengths_m": {a: {s: lengths_for(st, s) for s in ("right", "left")}
                      for a, st in STEMS.items()},
        "windows": [dict(start=a, stop=b, label=w) for a, b, w in c.wins],
        "outage": dict(anchor=OUTAGE_ANCHOR, durations=list(OUTAGE_DURATIONS)),
        "pearson_min_std_m": PEARSON_MIN_STD_M,
        "percentile_method": "numpy linear",
        "p2a_regression_tolerance_cm": REG_TOL_CM,
        "frame_conversion": "camera = solver * (1, -1, 1)",
        "fk_source_sha256": FK_SOURCE_SHA256,
        "asserts": c.asserts,
        "inputs_sha256": {rel(p): sha256(p) for p in sorted(INPUTS)},
        "modules_sha256": {m: sha256(REPO / m) for m in MODULES},
    }
    # --quick never overwrites the committed full-run record
    out = (TRACKS / "run_info_quick.json") if quick \
        else (RESULTS / "run_info.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(info, indent=2, sort_keys=True,
                              default=_json_default) + "\n")
    print(f"OK: wrote {rel(out)}", flush=True)


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="P1 only")
    ap.add_argument("--charts-only", action="store_true")
    args = ap.parse_args()
    if args.charts_only:
        subprocess.run([sys.executable, str(HERE / "charts.py")], check=True)
        return
    assert sha256(FK_SOURCE) == FK_SOURCE_SHA256, "FK source changed"
    RESULTS.mkdir(parents=True, exist_ok=True)
    c = build_ctx()
    p1(c)
    if not args.quick:
        outage(c)
        p2a(c)
        p2b(c)
        arm_lengths(c)
        kf_sweep(c)
        timing(c)
    c.asserts["akc_full_length_rescale_fallbacks"] = dict(RESCALE_COUNT)
    run_info(c, args.quick)
    subprocess.run([sys.executable, str(HERE / "charts.py")], check=True)
    print("PASS: all experiment asserts held", flush=True)


if __name__ == "__main__":
    main()

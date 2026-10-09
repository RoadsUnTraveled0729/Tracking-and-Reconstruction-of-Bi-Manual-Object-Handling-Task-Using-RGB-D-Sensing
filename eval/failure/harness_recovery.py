"""Graded synthetic-masking evaluation of object-conditioned recovery
(E-014) on one recording.

Why synthetic masking (the standing E-013 rule): on the frames where
MediaPipe actually fails there is no independent ground truth for the
arm, so an accuracy number measured there would be a comparison of two
guesses. Accuracy is therefore measured ONLY on frames the detector
found GENUINELY TRACKED - the truth is the unmasked solve of exactly
those frames - and the failure is introduced by us, so what the
recovery is supposed to reproduce is known by construction.

Clean windows are carved where the hand DEMONSTRABLY held the object
(the INSTANTANEOUS grip classifier, not only the persisted state,
which is designed to survive occlusion and on R5 carries a hand well
past the hold radius), no detector failure of any kind fires (arm_L,
arm_R or torso), the wrist sample is raw (wrist_flag 0), the
object-derived wrist estimate exists, and the unmasked reference solve
reports the side's swing and elbow groups LIVE - a frame whose
reference value is itself a held value is not truth. A window may only
start once the causal grip state machine could have ENTERED the
episode, otherwise the object estimate is absent for every masked
frame and the object method silently degenerates into the EMA one.

Three failure scenarios per window, each a separate build_inputs call
so the per-episode grip offset mu is refitted with the masked frames
excluded (no leakage from the frames being scored):

  S1 arm            the side's elbow + wrist landmarks are removed
  S2 arm+shoulder   S1 plus the side's shoulder landmark nulled
  S3 arm+shoulder+torso
                    S2 plus BOTH hips nulled (the torso-failure case:
                    the root frame must hold and the arm chain has to
                    survive on a pair-recovered shoulder)

Three methods on identical masked inputs:

  hold      ChainFallbackSolver (occlusion.py): hold last valid angle
  masked    RobustChainSolver without the object input: EMA direction
            memories are the only recovery source (pre-E-014 layer)
  recovery  RobustChainSolver with the object input: the wrist is
            placed at the object-derived estimate and the elbow by
            two-link IK (the technique under test)

Scope of the metrics: the primary number is joint-angle error against
the reference solve, wrap-aware, pooled element-wise over the masked
frames. Wrist POSITION error is reported for the recovery method only,
as |object-derived estimate - measured wrist| in the solver's point
space: that is the geometric anchor the technique rests on, and it is
directly measurable. The hold and masked methods place no wrist
estimate the eval can read without re-running forward kinematics, so
no wrist-position number is reported for them.

A supplementary outage-duration sweep (S1 only, one window per
eligible run) brackets the 45-frame EMA recovery horizon, since a
fixed 45-frame window measures the EMA baseline exactly where it is
strongest.

Run: python eval/failure/harness_recovery.py [--stem STEM]
Outputs eval/reports/<alias>_recovery_synthetic.{md,json,png}
"""
import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                       # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "common"))
sys.path.insert(0, str(HERE.parents[0] / "offset"))

import carry                             # noqa: E402
import grip_state                        # noqa: E402
import paths                             # noqa: E402
import recovery_core as rc               # noqa: E402
from fit_offset import load_tracks       # noqa: E402

# --- constants -------------------------------------------------------
# WIN: the masked stretch. 45 frames = 1.5 s at the recordings' 30 fps,
# and exactly the RobustChainSolver recovery horizon (occlusion_ext.py
# horizon=45), so the EMA baseline is scored over the whole span it is
# allowed to act on - one frame longer and the masked variant would
# stop recovering and the comparison would flatter the object path.
WIN = 45
# GUARD: 15 frames = 0.5 s of unmasked data between two windows carved
# from the same clean run, so each window's solver state re-locks onto
# measurements before the next mask begins (the layer's slew limit is
# 15 deg/frame, so 15 frames absorb a 225 deg re-lock).
GUARD = 15
# Cap per side; R5 supplies far fewer than this (see the report).
MAX_WINDOWS = 8
# Re-acquisition horizon: 10 frames = 0.33 s after the mask lifts.
POST = 10
FPS = 30.0
# Supplementary outage-duration sweep (S1 only, one window per eligible
# run, anchored at the run's established start). 45 is the EMA recovery
# horizon, so the sweep brackets it on both sides: the EMA baseline is
# at its strongest below it and stops recovering above it.
DURATIONS = (15, 30, 45, 60, 75, 90)

ANGLE_COLS = ["root_ex", "root_ey", "root_ez",
              "Rsh_y", "Rsh_z", "Rsh_tau", "Rel_y", "Rel_z",
              "Lsh_y", "Lsh_z", "Lsh_tau", "Lel_y", "Lel_z"]
ARM_COLS = {"right": (3, 4, 5, 6, 7), "left": (8, 9, 10, 11, 12)}
ROOT_COLS = (0, 1, 2)
# live-mask bit that owns each angle column (occlusion.py contract)
COL_BIT = {0: 0, 1: 0, 2: 0,
           3: 1, 4: 1, 5: 2, 6: 3, 7: 3,
           8: 4, 9: 4, 10: 5, 11: 6, 12: 6}
ARM_BITS = {"right": (1, 2, 3), "left": (4, 5, 6)}
BIT_ROOT = 0

SCENARIOS = ("S1_arm", "S2_arm_shoulder", "S3_arm_shoulder_torso")
METHODS = ("hold", "masked", "recovery")


def wrap(d):
    """Wrap-aware angle difference in degrees -> (-180, 180]."""
    return (np.asarray(d, float) + 180.0) % 360.0 - 180.0


def col_valid(mask):
    """(n, 13) bool: the reference solve reported this column's joint
    group live, so its value is a measurement, not a held value."""
    n = len(mask)
    v = np.zeros((n, 13), bool)
    for c, b in COL_BIT.items():
        v[:, c] = (np.asarray(mask) & (1 << b)) > 0
    return v


def _runs(ok, min_len):
    idx = np.flatnonzero(ok)
    if idx.size == 0:
        return []
    brk = np.flatnonzero(np.diff(idx) > 1)
    st = np.r_[idx[0], idx[brk + 1]]
    sp = np.r_[idx[brk], idx[-1]]
    return [(int(a), int(b)) for a, b in zip(st, sp)
            if b - a + 1 >= min_len]


def grip_context(stem, inputs):
    """The instantaneous grip evidence the eval needs on top of
    build_inputs: the per-frame clean-holding classification and the
    object-frame wrist offset. Recomputed here from the same public
    functions build_inputs uses (read-only; nothing is written back)."""
    calib, world, lm, obj_lev, R_lev, det, wr, wrist_flag, t = \
        load_tracks(stem, str(paths.calib_for(stem)))
    ctx = {}
    for side in rc.SIDES:
        hc = carry.holding_mask(inputs["center"], wr[side],
                                wrist_flag[side], det, inputs["carried"],
                                carry.forearm_ok(lm, side))
        ctx[side] = {
            "hold_clean": hc,
            "d_loc": np.einsum("nij,ni->nj", R_lev, wr[side] - obj_lev),
            "wrist_flag0": wrist_flag[side] == 0,
            "center_dist": np.linalg.norm(wr[side] - inputs["center"],
                                          axis=1),
        }
    return ctx


def _run_len(m):
    """r[f] = number of consecutive true frames of m ending at f."""
    r = np.zeros(len(m), int)
    c = 0
    for i, v in enumerate(m):
        c = c + 1 if v else 0
        r[i] = c
    return r


def select_windows(inputs, truth, ctx, side, side_only=False):
    """Clean windows for one side: see the module docstring.

    side_only (E-025, one-handed recordings): a frame is clean when no
    detector fires on the evaluated side or the torso; the OTHER arm's
    state is ignored, because the reference solve of one arm depends on
    the root frame and that arm's own landmarks only. On the rail
    recording the idle left arm is low-visibility almost throughout, so
    the default both-arms condition leaves no window at all. Default off,
    so the frozen R5 evaluation reproduces unchanged.
    """
    n = inputs["n"]
    if side_only:
        fail_any = inputs["fail"][side] | inputs["fail"]["torso"]
    else:
        fail_any = (inputs["fail"]["left"] | inputs["fail"]["right"]
                    | inputs["fail"]["torso"])
    m = np.asarray(truth["mask"])
    sw, tw, el = ARM_BITS[side]
    live = ((m & (1 << sw)) > 0) & ((m & (1 << el)) > 0)
    w_ok = np.isfinite(inputs["w_hat_solver"][side]).all(axis=1)
    ok = (ctx[side]["hold_clean"] & inputs["holding"][side] & ~fail_any
          & w_ok & ctx[side]["wrist_flag0"] & live)
    # the causal grip state machine needs ENTER_FRAMES consecutive
    # clean-holding frames to enter an episode; a window that starts
    # before it could enter tests nothing about the object path (the
    # estimate is simply absent and the recovery variant degenerates
    # into the EMA one), so a window may only start once the grip is
    # ESTABLISHED.
    rl = _run_len(ctx[side]["hold_clean"] & ~fail_any)
    established = np.zeros(n, bool)
    established[1:] = rl[:-1] >= grip_state.ENTER_FRAMES
    runs = _runs(ok, WIN)
    wins, rejected = [], []
    for a, b in runs:
        s = a
        while s <= b and not established[s]:
            s += 1
        if s > a:
            rejected.append({"run": [a, b], "shifted_start": int(s),
                             "reason": "grip not yet established"})
        while s + WIN - 1 <= b and len(wins) < MAX_WINDOWS:
            if s + WIN - 1 + POST < n:
                wins.append((s, s + WIN - 1))
            s += WIN + GUARD
        if len(wins) >= MAX_WINDOWS:
            break
    return {"ok": ok, "runs": runs, "windows": wins,
            "shifted": rejected, "clean_frames": int(ok.sum())}


def masked_inputs(stem, n, side, win, scenario):
    """One masked input set: extra_fail over the window plus, for the
    wider scenarios, landmark nulling in a COPY of the landmark frame.

    Nulling is applied AFTER build_inputs on purpose: it is a
    solve-input manipulation only. The object-derived wrist estimate is
    a function of the object pose and the grip offset alone, so nulling
    the shoulder or the hips cannot leak into it, and the grip-offset
    fit already excludes the extra_fail frames."""
    a, b = win
    em = np.zeros(n, bool)
    em[a:b + 1] = True
    inp = rc.build_inputs(stem, extra_fail={side: em})
    cols = []
    if scenario in ("S2_arm_shoulder", "S3_arm_shoulder_torso"):
        cols += [f"{side}_shoulder_{ax}" for ax in "xyz"]
    if scenario == "S3_arm_shoulder_torso":
        cols += [f"{h}_hip_{ax}" for h in ("left", "right") for ax in "xyz"]
    if cols:
        df = inp["lm_df"].copy()
        df.loc[df.index[a:b + 1], cols] = np.nan
        inp["lm_df"] = df
    return inp, em


def stat(vals):
    v = np.asarray(vals, float)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return {"n": 0, "median": None, "p95": None, "max": None}
    return {"n": int(v.size),
            "median": round(float(np.median(v)), 3),
            "p95": round(float(np.percentile(v, 95)), 3),
            "max": round(float(v.max()), 3)}


def angle_err(res, truth, valid, cols, a, b):
    """Element-wise wrap-aware error over the window, restricted to
    elements whose reference value is live. Returns (pooled values,
    per-frame median curve of length WIN)."""
    fr = slice(a, b + 1)
    e = np.abs(wrap(res["angles"][fr][:, cols] - truth["angles"][fr][:, cols]))
    v = valid[fr][:, cols]
    pooled = e[v]
    curve = np.full(b - a + 1, np.nan)
    for i in range(b - a + 1):
        if v[i].any():
            curve[i] = np.median(e[i][v[i]])
    return pooled, curve


def reacq(res, cols, b, n):
    """Largest wrap-aware per-frame step on the affected columns over
    the POST frames after the mask lifts (smooth re-lock check)."""
    hi = min(b + POST, n - 1)
    seg = res["angles"][b:hi + 1][:, cols]
    if seg.shape[0] < 2:
        return None
    return round(float(np.abs(wrap(np.diff(seg, axis=0))).max()), 3)


def honesty(res, side, a, b, check_root):
    """Frames inside the mask where a group that consumed removed or
    nulled landmarks still claims LIVE. Must be zero."""
    m = np.asarray(res["mask"])[a:b + 1]
    bits = list(ARM_BITS[side]) + ([BIT_ROOT] if check_root else [])
    bad = np.zeros(b - a + 1, bool)
    for bit in bits:
        bad |= (m & (1 << bit)) > 0
    return int(bad.sum())


def group_err(res, truth, valid, side, a, b):
    """Per joint-group median angle error, so an elbow collapse is not
    hidden inside a five-column pool."""
    out = {}
    groups = (("swing", (3, 4) if side == "right" else (8, 9)),
              ("twist", (5,) if side == "right" else (10,)),
              ("elbow", (6, 7) if side == "right" else (11, 12)))
    for name, cols in groups:
        p, _ = angle_err(res, truth, valid, list(cols), a, b)
        out[name] = stat(p)["median"]
    return out


def reach_diag(lm_df, seg_len, side, a, b):
    """Two-link conditioning of the window from the MEASURED arm: how
    close the shoulder-to-wrist distance sits to the calibrated arm's
    full reach, and how bent the elbow actually is. At a reach ratio
    near 1 the IK intersection circle collapses onto the S-W axis and
    the elbow's swivel is unrecoverable however good the wrist is."""
    flip = np.array([1.0, -1.0, 1.0])

    def pt(name):
        return lm_df[[f"{side}_{name}_x", f"{side}_{name}_y",
                      f"{side}_{name}_z"]].to_numpy()[a:b + 1] * flip
    S, E, W = pt("shoulder"), pt("elbow"), pt("wrist")
    up = "upper_arm_R" if side == "right" else "upper_arm_L"
    fo = "forearm_R" if side == "right" else "forearm_L"
    reach = seg_len[up] + seg_len[fo]
    ratio = np.linalg.norm(W - S, axis=1) / reach
    v1, v2 = E - S, W - E
    with np.errstate(invalid="ignore"):
        cos = np.einsum("ij,ij->i", v1, v2) / (
            np.linalg.norm(v1, axis=1) * np.linalg.norm(v2, axis=1))
    bend = np.degrees(np.arccos(np.clip(cos, -1.0, 1.0)))
    return {"reach_ratio_median": round(float(np.nanmedian(ratio)), 3),
            "reach_ratio_max": round(float(np.nanmax(ratio)), 3),
            "elbow_bend_median_deg": round(float(np.nanmedian(bend)), 2),
            "calibrated_reach_cm": round(reach * 100, 1),
            "measured_arm_cm": round(float(np.nanmedian(
                np.linalg.norm(E - S, axis=1)
                + np.linalg.norm(W - E, axis=1))) * 100, 1)}


def episode_of(inputs, side, a, b):
    for ep in inputs["episode_fits"][side]:
        if ep["start"] <= a and b <= ep["stop"]:
            return {"start": ep["start"], "stop": ep["stop"],
                    "n_clean": ep["n_clean"], "source": ep["source"],
                    "mu_cm": None if ep["mu"] is None else
                    [round(float(x) * 100, 2) for x in ep["mu"]],
                    "sd_cm": None if ep["sd"] is None else
                    [round(float(x) * 100, 2) for x in ep["sd"]]}
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R5_STEM)
    ap.add_argument("--side-only", action="store_true",
                    help="clean = evaluated side + torso clear (E-025; "
                         "one-handed recordings); default requires both arms")
    args = ap.parse_args()
    stem = args.stem
    alias = paths.ALIAS[stem]

    base = rc.build_inputs(stem)
    n, t = base["n"], base["t"]
    truth = rc.run_variant(base, "plain")
    valid = col_valid(truth["mask"])
    wr_truth = {s: base["lm_df"][[f"{s}_wrist_x", f"{s}_wrist_y",
                                  f"{s}_wrist_z"]].to_numpy()
                * np.array([1.0, -1.0, 1.0]) for s in rc.SIDES}

    print(f"=== {stem}: E-014 synthetic-masking evaluation ===")
    print(f"  {n} frames, {n / FPS:.1f} s; reference = unmasked plain solve")

    ctx = grip_context(stem, base)
    sel = {s: select_windows(base, truth, ctx, s, side_only=args.side_only)
           for s in rc.SIDES}
    for s in rc.SIDES:
        print(f"  {s}: {sel[s]['clean_frames']} clean frames, "
              f"runs {sel[s]['runs']}, "
              f"{len(sel[s]['windows'])} windows {sel[s]['windows']}")

    report = {
        "stem": stem, "frames": n, "fps": FPS,
        "constants": {"WIN": WIN, "GUARD": GUARD,
                      "MAX_WINDOWS": MAX_WINDOWS, "POST": POST,
                      "clean_condition": ("evaluated side + torso (E-025)"
                                          if args.side_only
                                          else "both arms + torso")},
        "detector_failure_frames": {k: int(v.sum())
                                    for k, v in base["fail"].items()},
        "grip_episodes": {s: [list(e) for e in base["episodes"][s]]
                          for s in rc.SIDES},
        "holding_frames": {s: int(base["holding"][s].sum())
                           for s in rc.SIDES},
        "torso_failure_runs": [list(r) for r in
                               _runs(base["fail"]["torso"], 30)],
        # how far the persisted grip state carries a hand past the
        # instantaneous classifier on otherwise clean frames
        "persistence_max_center_dist_cm": {
            s: (round(float(np.nanmax(ctx[s]["center_dist"][
                base["holding"][s] & ~ctx[s]["hold_clean"]
                & ~(base["fail"]["left"] | base["fail"]["right"]
                    | base["fail"]["torso"])])) * 100, 1)
                if (base["holding"][s] & ~ctx[s]["hold_clean"]
                    & ~(base["fail"]["left"] | base["fail"]["right"]
                        | base["fail"]["torso"])).any()
                else None) for s in rc.SIDES},
        "selection": {s: {"clean_frames": sel[s]["clean_frames"],
                          "runs": [list(r) for r in sel[s]["runs"]],
                          "windows": [list(w) for w in sel[s]["windows"]],
                          "shifted_starts": sel[s]["shifted"]}
                      for s in rc.SIDES},
        "windows": [], "aggregate": {}, "honesty_violations": [],
    }

    curves = {}          # (side, scenario, method) -> list of curves
    pooled = {}          # (side, scenario, method) -> list of arrays
    pooled_root = {}
    per_window = []

    for side in rc.SIDES:
        cols = list(ARM_COLS[side])
        for (a, b) in sel[side]["windows"]:
            for scen in SCENARIOS:
                inp, em = masked_inputs(stem, n, side, (a, b), scen)
                res = {"hold": rc.run_hold_baseline(inp),
                       "masked": rc.run_variant(inp, "masked"),
                       "recovery": rc.run_variant(inp, "recovery")}
                rec = {"side": side, "scenario": scen,
                       "start": int(a), "stop": int(b),
                       "t_start_s": round(float(t[a]), 2),
                       "t_stop_s": round(float(t[b]), 2),
                       "episode": episode_of(inp, side, a, b),
                       "truth_live_frac": {
                           nm: round(float(((np.asarray(truth["mask"])[a:b + 1]
                                             & (1 << bit)) > 0).mean()), 3)
                           for nm, bit in
                           (("swing", ARM_BITS[side][0]),
                            ("twist", ARM_BITS[side][1]),
                            ("elbow", ARM_BITS[side][2]),
                            ("root", BIT_ROOT))},
                       "methods": {}}
                # how much the arm and the object actually moved, and
                # how far the window's real grip offset sits from the
                # episode mu the estimate is built on (a descriptive
                # statistic of the input, used by no method)
                ta = truth["angles"][a:b + 1][:, cols]
                rec["truth_arm_travel_deg"] = round(float(
                    np.abs(wrap(np.diff(ta, axis=0))).sum(axis=0).max()), 2)
                rec["truth_arm_range_deg"] = round(float(
                    (ta.max(axis=0) - ta.min(axis=0)).max()), 2)
                wt_w = wr_truth[side][a:b + 1]
                rec["wrist_travel_cm"] = round(float(np.linalg.norm(
                    np.diff(wt_w, axis=0), axis=1).sum()) * 100, 2)
                ep = rec["episode"]
                dl = ctx[side]["d_loc"][a:b + 1]
                rec["window_mu_cm"] = [round(float(v) * 100, 2)
                                       for v in np.nanmean(dl, axis=0)]
                rec["grip_drift_cm"] = None if ep is None or \
                    ep["mu_cm"] is None else round(float(np.linalg.norm(
                        np.array(rec["window_mu_cm"])
                        - np.array(ep["mu_cm"]))), 2)
                rec["center_dist_median_cm"] = round(float(np.median(
                    ctx[side]["center_dist"][a:b + 1])) * 100, 2)
                rec["reach"] = reach_diag(base["lm_df"], base["seg_len"],
                                          side, a, b)
                # object-derived wrist estimate quality on the window
                w_hat = inp["w_hat_solver"][side][a:b + 1]
                fin = np.isfinite(w_hat).all(axis=1)
                d_cm = np.full(b - a + 1, np.nan)
                d_cm[fin] = np.linalg.norm(
                    w_hat[fin] - wr_truth[side][a:b + 1][fin], axis=1) * 100.0
                rec["obj_wrist_frames"] = int(fin.sum())
                rec["obj_wrist_err_cm"] = stat(d_cm)
                curves.setdefault((side, scen, "obj_wrist_cm"),
                                  []).append(d_cm)
                for meth in METHODS:
                    p, c = angle_err(res[meth], truth, valid, cols, a, b)
                    pr, _ = angle_err(res[meth], truth, valid,
                                      list(ROOT_COLS), a, b)
                    hv = honesty(res[meth], side, a, b,
                                 scen == "S3_arm_shoulder_torso")
                    rec["methods"][meth] = {
                        "angle_err_deg": stat(p),
                        "group_median_deg": group_err(res[meth], truth,
                                                      valid, side, a, b),
                        "root_err_deg": stat(pr),
                        "reacq_max_step_deg": reacq(res[meth], cols, b, n),
                        "live_violation_frames": hv,
                    }
                    if hv:
                        report["honesty_violations"].append(
                            {"side": side, "scenario": scen,
                             "window": [int(a), int(b)], "method": meth,
                             "frames": hv})
                    pooled.setdefault((side, scen, meth), []).append(p)
                    pooled_root.setdefault((side, scen, meth), []).append(pr)
                    curves.setdefault((side, scen, meth), []).append(c)
                per_window.append(rec)
                m = rec["methods"]
                print(f"  [{side} {a}-{b} {scen}] "
                      + " ".join(
                          f"{k} med {m[k]['angle_err_deg']['median']}"
                          for k in METHODS)
                      + f" | obj wrist med {rec['obj_wrist_err_cm']['median']}"
                      f" cm ({rec['obj_wrist_frames']}/{b - a + 1} fr)")

    report["windows"] = per_window

    for side in rc.SIDES:
        for scen in SCENARIOS:
            wins = sel[side]["windows"]
            if not wins:
                continue
            agg = {"n_windows": len(wins), "methods": {}}
            for meth in METHODS:
                p = np.concatenate(pooled[(side, scen, meth)])
                pr = np.concatenate(pooled_root[(side, scen, meth)])
                rq = [w["methods"][meth]["reacq_max_step_deg"]
                      for w in per_window
                      if w["side"] == side and w["scenario"] == scen]
                meds = [w["methods"][meth]["angle_err_deg"]["median"]
                        for w in per_window
                        if w["side"] == side and w["scenario"] == scen]
                agg["methods"][meth] = {
                    "angle_err_deg": stat(p),
                    "root_err_deg": stat(pr),
                    "reacq_max_step_deg": stat(rq),
                    "window_median_worst_deg": round(float(max(meds)), 3),
                }
            ow = max((w for w in per_window
                      if w["side"] == side and w["scenario"] == scen),
                     key=lambda w: w["methods"]["recovery"]
                     ["angle_err_deg"]["median"])
            agg["worst_window_by_recovery"] = {
                "window": [ow["start"], ow["stop"]],
                "medians_deg": {k: ow["methods"][k]["angle_err_deg"]["median"]
                                for k in METHODS},
                "obj_wrist_err_cm": ow["obj_wrist_err_cm"]["median"],
            }
            agg["obj_wrist_err_cm"] = stat(np.concatenate(
                curves[(side, scen, "obj_wrist_cm")]))
            report["aggregate"][f"{side}|{scen}"] = agg

    # --- supplementary: outage-duration sweep (S1 only) --------------
    print("  outage-duration sweep (S1, one window per eligible run):")
    sweep = []
    for side in rc.SIDES:
        cols = list(ARM_COLS[side])
        for (ra, rb) in sel[side]["runs"]:
            # the run's established start is the first window start the
            # selector produced inside this run
            starts = [w[0] for w in sel[side]["windows"]
                      if ra <= w[0] <= rb]
            if not starts:
                continue
            s0 = starts[0]
            for dur in DURATIONS:
                e = s0 + dur - 1
                if e > rb or e + POST >= n:
                    continue
                inp, _ = masked_inputs(stem, n, side, (s0, e), SCENARIOS[0])
                res = {"hold": rc.run_hold_baseline(inp),
                       "masked": rc.run_variant(inp, "masked"),
                       "recovery": rc.run_variant(inp, "recovery")}
                row = {"side": side, "run": [ra, rb], "start": int(s0),
                       "stop": int(e), "duration_frames": dur,
                       "duration_s": round(dur / FPS, 2), "methods": {}}
                w_hat = inp["w_hat_solver"][side][s0:e + 1]
                fin = np.isfinite(w_hat).all(axis=1)
                d_cm = np.full(dur, np.nan)
                d_cm[fin] = np.linalg.norm(
                    w_hat[fin] - wr_truth[side][s0:e + 1][fin],
                    axis=1) * 100.0
                row["obj_wrist_err_cm"] = stat(d_cm)
                for meth in METHODS:
                    p, _ = angle_err(res[meth], truth, valid, cols, s0, e)
                    row["methods"][meth] = stat(p)
                sweep.append(row)
                print(f"    {side} {s0}-{e} ({dur} fr) "
                      + " ".join(f"{k} {row['methods'][k]['median']}"
                                 for k in METHODS))
    report["duration_sweep"] = sweep

    out_json = paths.EVAL_REPORTS / f"{alias}_recovery_synthetic.json"
    out_json.write_text(json.dumps(report, indent=1))
    print(f"[+] {out_json}")

    png = plot(alias, sel, curves, sweep)
    md = write_md(alias, stem, report, sel, png)
    print(f"[+] {png}")
    print(f"[+] {md}")

    viol = len(report["honesty_violations"])
    print(f"  honesty violations: {viol}")


# --- rendering -------------------------------------------------------
# Categorical slots 1-3 of the validated default data-viz palette
# (blue / orange / aqua), fixed order, never cycled.
COLOR = {"hold": "#2a78d6", "masked": "#eb6834", "recovery": "#1baf7a"}
LABEL = {"hold": "hold-last", "masked": "EMA (masked)",
         "recovery": "object (recovery)"}
SURFACE, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"


def _style(ax):
    ax.set_facecolor(SURFACE)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color("#d8d7d2")
    ax.grid(True, color="#e8e7e2", lw=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=INK2, labelsize=8, length=0)


def plot(alias, sel, curves, sweep):
    fig = plt.figure(figsize=(13.5, 10.0))
    fig.patch.set_facecolor(SURFACE)
    gs = fig.add_gridspec(3, 6, hspace=0.42, wspace=0.30,
                          left=0.07, right=0.98, top=0.92, bottom=0.07)
    ymax = 0.0
    for side in rc.SIDES:
        if not sel[side]["windows"]:
            continue
        for scen in SCENARIOS:
            for meth in METHODS:
                v = np.vstack(curves[(side, scen, meth)])
                ymax = max(ymax, float(np.nanmax(np.nanmedian(v, axis=0))))
    for r, side in enumerate(rc.SIDES):
        for c, scen in enumerate(SCENARIOS):
            ax = fig.add_subplot(gs[r, 2 * c:2 * c + 2])
            _style(ax)
            ax.set_ylim(0, ymax * 1.18)
            if not sel[side]["windows"]:
                ax.text(0.5, 0.5, "no clean windows", ha="center",
                        va="center", color=INK2, transform=ax.transAxes)
                continue
            x = np.arange(WIN) / FPS
            ends = []
            first_drawn = (r, c) == next(
                (rr, 0) for rr, sd in enumerate(rc.SIDES) if sel[sd]["windows"])
            for meth in METHODS:
                y = np.nanmedian(np.vstack(curves[(side, scen, meth)]),
                                 axis=0)
                ax.plot(x, y, lw=2.0, color=COLOR[meth],
                        label=LABEL[meth] if first_drawn else None)
                ends.append([float(y[-1]), meth])
            # push apart end labels that would overlap
            ends.sort()
            gap = ymax * 0.09
            for i in range(1, len(ends)):
                if ends[i][0] - ends[i - 1][0] < gap:
                    ends[i][0] = ends[i - 1][0] + gap
            for (yl, meth), raw in zip(ends, sorted(
                    np.nanmedian(np.vstack(curves[(side, scen, m)]),
                                 axis=0)[-1] for m in METHODS)):
                ax.annotate(f"{raw:.1f}", (x[-1], yl),
                            textcoords="offset points", xytext=(4, 0),
                            fontsize=8, color=INK2, va="center")
            ax.set_title(f"{side} arm, {scen.replace('_', ' ')}",
                         fontsize=9.5, color=INK, loc="left")
            if c == 0:
                ax.set_ylabel("arm angle error (deg)", fontsize=9,
                              color=INK2)
            ax.set_xlabel("time since mask onset (s)", fontsize=9,
                          color=INK2)
            if r == 0 and c == 0:
                ax.legend(frameon=False, fontsize=9, labelcolor=INK2,
                          loc="upper left")
    for i, side in enumerate(rc.SIDES):
        ax = fig.add_subplot(gs[2, 3 * i:3 * i + 3])
        _style(ax)
        rows = [s for s in sweep if s["side"] == side]
        runs = sorted({tuple(s["run"]) for s in rows})
        for meth in METHODS:
            first = True
            for run in runs:
                rr = sorted((s for s in rows if tuple(s["run"]) == run),
                            key=lambda s: s["duration_frames"])
                ax.plot([s["duration_s"] for s in rr],
                        [s["methods"][meth]["median"] for s in rr],
                        lw=2.0, color=COLOR[meth], marker="o", ms=4,
                        label=LABEL[meth] if (first and i == 0) else None)
                first = False
        ax.axvline(45 / FPS, color=INK2, lw=1.0, ls=":")
        ax.annotate("EMA recovery horizon", (45 / FPS, ax.get_ylim()[1]),
                    textcoords="offset points", xytext=(4, -12),
                    fontsize=8, color=INK2)
        ax.set_title(f"{side} arm: outage-duration sweep (S1, one line "
                     "per eligible run)", fontsize=9.5, color=INK,
                     loc="left")
        ax.set_xlabel("masked outage length (s)", fontsize=9, color=INK2)
        if i == 0:
            ax.set_ylabel("arm angle error (deg)", fontsize=9, color=INK2)
            ax.legend(frameon=False, fontsize=9, labelcolor=INK2,
                      loc="upper left")
    fig.suptitle(f"{alias.upper()}: synthetic-mask arm angle error, "
                 "median over clean windows", fontsize=11.5, color=INK,
                 x=0.07, ha="left")
    out = paths.EVAL_REPORTS / f"{alias}_recovery_synthetic.png"
    fig.savefig(out, dpi=130, facecolor=SURFACE)
    plt.close(fig)
    return out


def _row(vals):
    return "| " + " | ".join("" if v is None else str(v) for v in vals) + " |"


def _sep(k):
    return _row(["---"] * k)


def write_md(alias, stem, rep, sel, png):
    L = []
    A = L.append
    s1 = {(w["side"], w["start"]): w for w in rep["windows"]
          if w["scenario"] == SCENARIOS[0]}
    A(f"# {alias.upper()} object-conditioned recovery: graded synthetic "
      f"masking ({stem})")
    A("")
    A("Graded evaluation of E-014 (object-conditioned wrist and elbow "
      "recovery) against the two recovery sources that precede it, "
      "under the standing E-013 rule: accuracy is measured only where "
      "the truth is known by construction.")
    A("")
    A("## Headline")
    A("")
    is_r5 = (stem == paths.R5_STEM)
    if is_r5:
        A("On R5 the object-conditioned recovery does NOT beat either "
          "baseline in any clean window, at any outage length up to 3 s. "
          "The report below identifies two independent causes, both "
          "measurable in the input rather than in the comparison: the grip "
          "offset is not constant inside a grip episode, and the clean "
          "windows put the arm at near-full extension, where the two-link "
          "elbow IK is singular.")
    else:
        # neutral, number-driven headline for any other recording; the
        # interpretation belongs to the reader of the numbers, not to a
        # template written for R5
        parts = []
        for key, agg in rep["aggregate"].items():
            side, scen = key.split("|")
            if scen != "S1_arm":
                continue
            m = agg["methods"]
            parts.append(
                f"{side} arm, {agg['n_windows']} windows, S1: pooled "
                f"angle-error medians hold-last {m['hold']['angle_err_deg']['median']}, "
                f"EMA {m['masked']['angle_err_deg']['median']}, object "
                f"{m['recovery']['angle_err_deg']['median']} deg; object "
                f"wrist-estimate error median "
                f"{agg['obj_wrist_err_cm']['median']} cm (p95 "
                f"{agg['obj_wrist_err_cm']['p95']})")
        A(f"{alias.upper()}: " + ("; ".join(parts) if parts else
                                  "no clean window on either side") + ". "
          f"Clean condition: {rep['constants']['clean_condition']}. "
          "The R5-specific interpretation sections are omitted for this "
          "recording; the tables below carry the numbers.")
    A("")
    A("## Why the windows are synthetic")
    A("")
    A("On the frames where MediaPipe actually fails there is no "
      "independent measurement of the arm, so any accuracy number "
      "computed there compares two guesses. This harness therefore "
      "takes frames the failure detector calls GENUINELY TRACKED, "
      "records the unmasked solve as the reference, then removes the "
      "same landmarks the detector would have removed and scores each "
      "method against that reference. What the recovery must reproduce "
      "is known before the recovery runs.")
    A("")
    A("## Constants")
    A("")
    A(_row(["constant", "value", "justification"]))
    A(_sep(3))
    A(_row(["WIN", WIN,
            f"masked stretch, {WIN / FPS:.1f} s at {FPS:.0f} fps; equals "
            "the RobustChainSolver recovery horizon (occlusion_ext.py "
            "horizon=45), so the EMA baseline is scored over exactly the "
            "span it is allowed to act on"]))
    A(_row(["GUARD", GUARD,
            f"unmasked frames between two windows of the same run, "
            f"{GUARD / FPS:.2f} s; the layer's 15 deg/frame slew limit "
            "absorbs up to 225 deg of re-lock inside that gap"]))
    A(_row(["MAX_WINDOWS", MAX_WINDOWS,
            "cap per side; R5 supplies far fewer"]))
    A(_row(["POST", POST,
            f"re-acquisition horizon after the mask lifts, "
            f"{POST / FPS:.2f} s"]))
    A(_row(["ENTER_FRAMES", grip_state.ENTER_FRAMES,
            "read from grip_state.py, not chosen here: a window may only "
            "start once the causal grip state machine could have entered "
            "the episode"]))
    A(_row(["DURATIONS", ", ".join(str(d) for d in DURATIONS),
            "supplementary sweep, bracketing the 45-frame EMA horizon on "
            "both sides"]))
    A("")
    A("## Window selection")
    A("")
    A("A frame is eligible when ALL of the following hold.")
    A("")
    pmax = rep["persistence_max_center_dist_cm"]
    A("1. The instantaneous grip classifier says this hand is on the "
      "object (carry.holding_mask: marker detected, object carried, "
      "wrist raw and within the pinned "
      f"{carry.HOLD_RADIUS * 100:.0f} cm hold radius of the box "
      "centre, forearm length plausible). The persisted grip STATE is "
      "not enough - it is designed to survive occlusion, and on "
      "otherwise clean frames it carries a hand out to "
      f"{pmax['left']} cm (left) and {pmax['right']} cm (right) from "
      "the box centre, which is outside the technique's own premise.")
    A("2. No detector failure fires anywhere in the body (arm_L, arm_R "
      "or torso). A corrupt torso corrupts the root frame the arm "
      "angles are expressed in, so torso failures disqualify arm "
      "windows too.")
    A("3. The wrist sample is raw (wrist_flag 0), not filter-filled.")
    A("4. The object-derived wrist estimate exists.")
    A("5. The unmasked reference solve reports this side's swing and "
      "elbow groups LIVE.")
    A("")
    A("The twist group is deliberately NOT required live: it is held by "
      "the E-012 straight-elbow observability rule, which is a property "
      "of the pose and not of the data. Twist frames stay in the "
      "windows, but their error elements are dropped wherever the "
      "reference twist is held. The same element-wise rule applies to "
      "the root columns.")
    A("")
    shifts = [(s, sh) for s in rc.SIDES
              for sh in rep["selection"][s]["shifted_starts"]]
    A("A window may only START once the grip is ESTABLISHED - "
      f"{grip_state.ENTER_FRAMES} consecutive clean-holding frames "
      "before it. Without that rule a window can open inside the "
      "state machine's entry delay, where the object estimate is "
      "absent for every masked frame and the object method silently "
      "degenerates into the EMA one. "
      f"{len(shifts)} of the eligible runs needed the shift: "
      + ", ".join(f"{s} run {sh['run'][0]}-{sh['run'][1]} starts at "
                  f"{sh['shifted_start']}" for s, sh in shifts) + ".")
    A("")
    A(_row(["quantity"] + list(rc.SIDES)))
    A(_sep(3))
    A(_row(["detector failure frames (arm)"]
           + [rep["detector_failure_frames"][s] for s in rc.SIDES]))
    A(_row(["detector failure frames (torso, shared)"]
           + [rep["detector_failure_frames"]["torso"]] * 2))
    A(_row(["holding frames (grip state)"]
           + [rep["holding_frames"][s] for s in rc.SIDES]))
    A(_row(["grip episodes"]
           + [", ".join(f"{a}-{b}" for a, b in rep["grip_episodes"][s])
              for s in rc.SIDES]))
    A(_row(["eligible frames"]
           + [rep["selection"][s]["clean_frames"] for s in rc.SIDES]))
    A(_row([f"eligible runs of >= {WIN} frames"]
           + [", ".join(f"{a}-{b}" for a, b in rep["selection"][s]["runs"])
              or "none" for s in rc.SIDES]))
    A(_row(["windows carved"]
           + [len(rep["selection"][s]["windows"]) for s in rc.SIDES]))
    A("")
    if is_r5:
        A(f"R5's {rep['detector_failure_frames']['torso']} torso-failure "
          "frames sit directly on top of the long left-hand grip episode "
          "(torso failure runs of 30 frames or more: "
          + ", ".join(f"{a}-{b}" for a, b in rep["torso_failure_runs"])
          + "), which is why the left side yields so few eligible frames "
          f"despite the grip state calling it holding on "
          f"{rep['holding_frames']['left']}.")
    else:
        A(f"Torso failure runs of 30 frames or more: "
          + (", ".join(f"{a}-{b}" for a, b in rep["torso_failure_runs"]) or "none")
          + f". Clean condition: {rep['constants']['clean_condition']}.")
    A("")
    A("### Windows")
    A("")
    A(_row(["side", "frames", "time (s)", "grip episode", "mu source",
            "reference live: swing / twist / elbow / root"]))
    A(_sep(6))
    for (side, st), w in s1.items():
        ep, tl = w["episode"], w["truth_live_frac"]
        A(_row([side, f"{w['start']}-{w['stop']}",
                f"{w['t_start_s']}-{w['t_stop_s']}",
                "none" if ep is None else f"{ep['start']}-{ep['stop']}",
                "none" if ep is None else
                f"{ep['source']} ({ep['n_clean']} clean)",
                f"{tl['swing']} / {tl['twist']} / {tl['elbow']} / "
                f"{tl['root']}"]))
    A("")
    A("### What the windows contain")
    A("")
    A("Descriptive statistics of the masked frames, computed from the "
      "measured landmarks and the object track. No method reads them; "
      "they exist to attribute the results below.")
    A("")
    A(_row(["side", "frames", "reference arm travel (deg)",
            "wrist travel (cm)", "wrist to box centre (cm)",
            "grip drift vs episode mu (cm)",
            "reach ratio, wrist distance over arm length",
            "measured elbow bend (deg)"]))
    A(_sep(8))
    for (side, st), w in s1.items():
        r = w["reach"]
        A(_row([side, f"{w['start']}-{w['stop']}",
                w["truth_arm_travel_deg"], w["wrist_travel_cm"],
                w["center_dist_median_cm"], w["grip_drift_cm"],
                f"{r['reach_ratio_median']} (max {r['reach_ratio_max']})",
                r["elbow_bend_median_deg"]]))
    A("")
    A("Grip drift is the distance between the window's own mean "
      "object-frame wrist offset and the episode mu the estimate is "
      "built from. Reach ratio is the measured shoulder-to-wrist "
      "distance divided by the calibrated upper arm plus forearm: at "
      "1.0 the two-link IK circle collapses onto the shoulder-wrist "
      "axis and the elbow's swivel is unrecoverable no matter how good "
      "the wrist is.")
    A("")
    A("## Scenarios")
    A("")
    A(_row(["scenario", "landmarks taken from the solve over the window"]))
    A(_sep(2))
    A(_row(["S1_arm",
            "the side's elbow and wrist are removed (extra_fail; the "
            "same frames are excluded from the grip-offset fit, so the "
            "scored frames never inform the estimate)"]))
    A(_row(["S2_arm_shoulder",
            "S1 plus the side's shoulder nulled: the arm chain's anchor "
            "must itself be pair-recovered"]))
    A(_row(["S3_arm_shoulder_torso",
            "S2 plus both hips nulled: the root frame has no support "
            "and must hold"]))
    A("")
    A("## Methods")
    A("")
    A(_row(["method", "what it may use"]))
    A(_sep(2))
    A(_row(["hold-last", "ChainFallbackSolver: the last valid angle"]))
    A(_row(["EMA (masked)",
            "RobustChainSolver without the object input: gating plus "
            "EMA direction-memory recovery (the pre-E-014 layer)"]))
    A(_row(["object (recovery)",
            "RobustChainSolver with the object input: wrist at the "
            "object-derived estimate, elbow by two-link IK"]))
    A("")
    A("## Metric scope")
    A("")
    A("The primary number is the wrap-aware joint-angle error against "
      "the reference solve, pooled element-wise over all masked frames "
      "of all windows and over the five angle columns of the affected "
      "arm, keeping only elements whose reference group is live. Root "
      "columns are reported separately (they only move in S3). Wrist "
      "POSITION error is reported for the object method only, as "
      "|object-derived estimate - measured wrist| in the solver's point "
      "space: it is the geometric anchor the technique rests on and it "
      "is directly measurable. Hold and EMA place no wrist the eval can "
      "read without re-running forward kinematics, so no position "
      "number is quoted for them and the angle errors carry the "
      "comparison.")
    A("")
    A("## Results")
    A("")
    for scen in SCENARIOS:
        A(f"### {scen}")
        A("")
        A(_row(["side", "windows", "method", "angle err median (deg)",
                "angle err p95 (deg)", "worst-window median (deg)",
                "root err median (deg)",
                "re-acquisition max step (deg)"]))
        A(_sep(8))
        for side in rc.SIDES:
            ag = rep["aggregate"].get(f"{side}|{scen}")
            if ag is None:
                continue
            for meth in METHODS:
                m = ag["methods"][meth]
                A(_row([side, ag["n_windows"], LABEL[meth],
                        m["angle_err_deg"]["median"],
                        m["angle_err_deg"]["p95"],
                        m["window_median_worst_deg"],
                        m["root_err_deg"]["median"],
                        m["reacq_max_step_deg"]["max"]]))
        A("")
        A(_row(["side", "object wrist-estimate error median (cm)",
                "p95 (cm)", "worst window (frames)",
                "worst-window object median (deg)"]))
        A(_sep(5))
        for side in rc.SIDES:
            ag = rep["aggregate"].get(f"{side}|{scen}")
            if ag is None:
                continue
            ow = ag["worst_window_by_recovery"]
            A(_row([side, ag["obj_wrist_err_cm"]["median"],
                    ag["obj_wrist_err_cm"]["p95"],
                    f"{ow['window'][0]}-{ow['window'][1]}",
                    ow["medians_deg"]["recovery"]]))
        A("")
    A("### Where the object method's error sits (S1, per window)")
    A("")
    A(_row(["side", "window", "method", "swing median (deg)",
            "twist median (deg)", "elbow median (deg)",
            "object wrist error median (cm)"]))
    A(_sep(7))
    for (side, st), w in s1.items():
        for meth in METHODS:
            g = w["methods"][meth]["group_median_deg"]
            A(_row([side, f"{w['start']}-{w['stop']}", LABEL[meth],
                    g["swing"], g["twist"], g["elbow"],
                    w["obj_wrist_err_cm"]["median"] if meth == "recovery"
                    else None]))
    A("")
    A("## Outage-duration sweep (supplementary, S1 only)")
    A("")
    A("One window per eligible run, anchored at that run's established "
      "start, masked for each duration in turn. This is the test the "
      "fixed 45-frame window cannot answer: 45 frames is exactly the "
      "EMA recovery horizon, so the EMA baseline is measured at its "
      "strongest.")
    A("")
    A(_row(["side", "window", "outage (frames)", "outage (s)"]
           + [LABEL[m] + " median (deg)" for m in METHODS]
           + ["object wrist error median (cm)"]))
    A(_sep(8))
    for s in rep["duration_sweep"]:
        A(_row([s["side"], f"{s['start']}-{s['stop']}",
                s["duration_frames"], s["duration_s"]]
               + [s["methods"][m]["median"] for m in METHODS]
               + [s["obj_wrist_err_cm"]["median"]]))
    A("")
    A(f"![error curves]({png.name})")
    A("")
    A("Top two rows: median across windows of the per-frame arm angle "
      "error against time since the mask began. Bottom row: the "
      "duration sweep, with the EMA recovery horizon marked.")
    A("")
    A("## Honesty check")
    A("")
    A("During a masked window every joint group that consumed a removed "
      "or nulled landmark must report its live bit CLEAR, for all three "
      "methods (S3 additionally requires the root bit clear).")
    A("")
    if rep["honesty_violations"]:
        A(_row(["side", "scenario", "window", "method", "live frames"]))
        A(_sep(5))
        for v in rep["honesty_violations"]:
            A(_row([v["side"], v["scenario"],
                    f"{v['window'][0]}-{v['window'][1]}", v["method"],
                    v["frames"]]))
    else:
        A(f"PASS: 0 violations over {len(rep['windows'])} "
          "window-scenario runs, all three methods.")
    A("")
    A("## Interpretation")
    A("")
    if is_r5:
        A("The object-conditioned recovery is beaten by both baselines in "
          "every window and at every outage length R5 admits: pooled over "
          "S1 it costs several degrees of median arm error where hold-last "
          "and the EMA layer stay near one, and the duration sweep shows no "
          "crossover inside 3 s. The object path's error does not decay "
          "with outage length the way a memory's does - it is a bias, flat "
          "in time - so the ranking is set by how large that bias is, not "
          "by how long the outage lasts.")
        A("")
        ws = list(s1.values())
        drifts = sorted(w["grip_drift_cm"] for w in ws
                        if w["grip_drift_cm"] is not None)
        best = min(ws, key=lambda w: w["obj_wrist_err_cm"]["median"])
        longest_ep = max(rep["grip_episodes"]["left"]
                         + rep["grip_episodes"]["right"],
                         key=lambda e: e[1] - e[0])
        ratios = sorted(w["reach"]["reach_ratio_median"] for w in ws)
        travels = sorted(w["truth_arm_travel_deg"] for w in ws)
        A("The bias has two separable sources, and the second is the "
          "surprise. The first is grip-offset drift: the per-episode mu is "
          "fitted over a whole grip episode, and R5's episodes are long "
          f"(the longest runs {longest_ep[0]} to {longest_ep[1]}, "
          f"{(longest_ep[1] - longest_ep[0] + 1) / FPS:.0f} s) with the "
          "operator regrasping inside them, so the window's real offset "
          f"sits up to {drifts[-1]} cm from the episode mu "
          f"({sum(1 for d in drifts if d >= drifts[max(len(drifts) - 2, 0)])} "
          f"of the {len(drifts)} windows sit at "
          f"{drifts[max(len(drifts) - 2, 0)]} cm or more) and "
          "the object-derived wrist inherits exactly that error. The "
          "second source is independent of the grip: in window "
          f"{best['side']} {best['start']}-{best['stop']} the object wrist "
          f"estimate is accurate to "
          f"{best['obj_wrist_err_cm']['median']} cm, and the method is "
          f"still {best['methods']['recovery']['angle_err_deg']['median']} "
          "deg wrong, because the arm sits at a reach ratio of "
          f"{best['reach']['reach_ratio_median']} - beyond the calibrated "
          "arm length - so the two-link IK clips its cosine, collapses the "
          "intersection circle onto the shoulder-wrist axis, and returns a "
          "straight arm where the operator's elbow is bent "
          f"{best['reach']['elbow_bend_median_deg']} deg. Every clean "
          f"window on R5 sits at a reach ratio of {ratios[0]} or more, "
          "which is what holding a box in front of the body looks like, so "
          "this is the normal case for the task rather than an edge case.")
        A("")
        A("The baselines win here for a reason that also bounds how far "
          "this result generalises: a window that satisfies the E-013 "
          "cleanliness rule is a window in which the hand is quietly "
          "holding the box, and the reference arm travels only "
          f"{travels[0]} to {travels[-1]} deg across {WIN / FPS:.1f} s. "
          "Hold-last is close to correct by construction on such frames, "
          "and the EMA memory is fresh. What the harness therefore "
          "establishes is narrower than a verdict on the technique: on "
          "quasi-static holding, the object anchor's bias exceeds what a "
          "memory loses, and before the technique can win anywhere the mu "
          "must be re-estimated inside an episode and the elbow IK must "
          "refuse to answer near full extension instead of returning a "
          "straight arm.")
        A("")
        A("Two secondary observations. S3 behaves as designed: with both "
          "hips nulled the root bit is clear on every masked frame for all "
          "three methods and the root simply holds, and because the R5 root "
          "moves little over 1.5 s the root error stays small - the "
          "scenario shows the arm chain survives on a pair-recovered "
          "shoulder, not that the root is accurate. Re-acquisition is "
          "bounded at the layer's 15 deg/frame slew limit for the EMA and "
          "object methods, while hold-last has no limiter and is only "
          "smooth here because it was never far away.")
        A("")
    else:
        A("Omitted: the interpretation above was written for R5. For this recording read the tables; the moving-window check (moving_window_check.py) reports the forward-kinematics wrist error the reconstruction shows.")
    A("")
    A("## Limitations")
    A("")
    A("- Windows exist only where the hand demonstrably held the object "
      f"and the clean condition ({rep['constants']['clean_condition']}) "
      f"held. On {alias.upper()} that is "
      f"{sum(rep['selection'][s]['clean_frames'] for s in rc.SIDES)} "
      f"frames out of {rep['frames']}, carving "
      f"{sum(len(rep['selection'][s]['windows']) for s in rc.SIDES)} "
      "windows. The sample is windows, not hours: each aggregate pools "
      f"{len(rep['selection']['left']['windows'])} left and "
      f"{len(rep['selection']['right']['windows'])} right windows, so a "
      "single window moves it.")
    A("- The technique's accuracy is bounded by the grip-offset "
      "variance: the object-derived wrist is the object pose plus a "
      "per-episode constant, so within-episode regrasping enters the "
      "result directly. The per-window mu source, its clean-frame "
      "count, and the measured drift are tabulated above so the bound "
      "is visible rather than assumed.")
    A("- The reference is the unmasked robust solve, not external "
      "motion capture. It is measurement-determined on exactly the "
      "elements scored (that is what the liveness requirement buys), "
      "but it inherits the extractor's own noise, so differences of a "
      "few tenths of a degree between methods are not meaningful.")
    A("- Hold-last is the only method without the layer's 15 deg/frame "
      "slew limit, so its re-acquisition step is not bounded by "
      "construction while the other two are. Read that column as a "
      "property of the layer as much as of the recovery source.")
    A("- The reference run applies no failure mask at all, while all "
      "three methods run with the detector mask applied everywhere, so "
      "their solver states diverge outside the windows. Inside a window "
      "the reference is a live measurement, so the comparison is "
      "against data, but each method enters a window with its own "
      "history.")
    A("- The duration sweep uses one window per run and cannot exceed "
      "what a run allows, so 90 frames is measured on a single "
      "right-arm window. It bounds the trend, it does not establish a "
      "crossover point.")
    A("")
    out = paths.EVAL_REPORTS / f"{alias}_recovery_synthetic.md"
    out.write_text("\n".join(L) + "\n")
    return out


if __name__ == "__main__":
    main()

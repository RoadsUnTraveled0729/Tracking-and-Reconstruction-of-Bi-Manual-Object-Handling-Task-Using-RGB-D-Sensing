"""V3 grading metrics (V3_PLAN.md Phase 0; V3_DECISIONS.md D-003/D-004).

Pure functions on numpy arrays. Nothing here touches configs, files,
detectors, or strategies; grade.py wires these to data. Frozen before
any strategy exists so the Phase 4 bake-off cannot be gamed.

Angle vocabulary is v1's, defined by vendor/v1/occlusion.py:
angles13 order = root x,y,z | R sh ty,tz,ttau | R elb ey,ez |
L sh ty,tz,ttau | L elb ey,ez (degrees). The seven joint groups are
the v1 live-mask bits, in bit order. Group error reduction is MAX over
member angles (D-004: a group is as wrong as its worst DOF).

Statuses: MEASURED = 0, ESTIMATED = 1, LOST = 2 per group per frame.
"""
import math

import numpy as np

ANGLE_NAMES = (
    "root_x", "root_y", "root_z",
    "r_swing_y", "r_swing_z", "r_twist", "r_elbow_y", "r_elbow_z",
    "l_swing_y", "l_swing_z", "l_twist", "l_elbow_y", "l_elbow_z",
)

# v1 BIT_NAMES order (vendor/v1/occlusion.py) -> angles13 indices
GROUP_NAMES = ("root", "R_swing", "R_twist", "R_elbow",
               "L_swing", "L_twist", "L_elbow")
GROUP_ANGLES = ((0, 1, 2), (3, 4), (5,), (6, 7), (8, 9), (10,), (11, 12))

MEASURED, ESTIMATED, LOST = 0, 1, 2
STATUS_NAMES = ("MEASURED", "ESTIMATED", "LOST")


def wrap_deg(a):
    """Map angles (deg) to (-180, 180]."""
    a = np.asarray(a, dtype=float)
    return -((-a + 180.0) % 360.0 - 180.0)


def angle_error(out, truth):
    """|wrap_deg(out - truth)| elementwise; shapes must match, (T, 13)."""
    out = np.asarray(out, dtype=float)
    truth = np.asarray(truth, dtype=float)
    if out.shape != truth.shape:
        raise ValueError(f"shape mismatch: {out.shape} vs {truth.shape}")
    return np.abs(wrap_deg(out - truth))


def group_error(err13):
    """(T, 13) per-angle error -> (T, 7) per-group error, MAX over members."""
    err13 = np.asarray(err13, dtype=float)
    if err13.ndim != 2 or err13.shape[1] != len(ANGLE_NAMES):
        raise ValueError(f"expected (T, 13), got {err13.shape}")
    return np.stack([err13[:, idx].max(axis=1) for idx in GROUP_ANGLES],
                    axis=1)


def e_occ(gerr, start, stop):
    """Error over the occlusion window [start, stop).

    gerr: (T, 7) group error. Returns {"mean": (7,), "max": (7,)}.
    """
    win = np.asarray(gerr, dtype=float)[start:stop]
    if win.shape[0] == 0:
        raise ValueError(f"empty window [{start}, {stop})")
    return {"mean": win.mean(axis=0), "max": win.max(axis=0)}


def e_reacq(gerr, stop, k=5):
    """Mean group error over the first k frames after the window,
    rows [stop, stop + k). Returns (7,)."""
    gerr = np.asarray(gerr, dtype=float)
    tail = gerr[stop:stop + k]
    if tail.shape[0] < k:
        raise ValueError(f"only {tail.shape[0]} frames after stop={stop}, "
                         f"need {k}")
    return tail.mean(axis=0)


def recovery_time(gerr, stop, thresh_deg=5.0, sustain=3):
    """Frames after the window until group error < thresh_deg sustained
    for `sustain` consecutive frames; inf if never (or the tail is too
    short to ever satisfy the sustain requirement). Returns (7,).

    The returned value is the delay: 0 means recovered immediately at
    frame `stop`.
    """
    gerr = np.asarray(gerr, dtype=float)
    tail = gerr[stop:]
    n = tail.shape[0]
    out = np.full(len(GROUP_NAMES), math.inf)
    below = tail < thresh_deg
    for g in range(len(GROUP_NAMES)):
        for t in range(n - sustain + 1):
            if below[t:t + sustain, g].all():
                out[g] = float(t)
                break
    return out


def angle_steps(angles):
    """(T, 13) angle track -> (T-1, 13) wrap-aware absolute per-frame
    steps in degrees."""
    angles = np.asarray(angles, dtype=float)
    if angles.shape[0] < 2:
        raise ValueError("need at least 2 frames")
    return np.abs(wrap_deg(np.diff(angles, axis=0)))


def teleport_budget(clean_steps, safety=1.5, floor_deg=1e-9):
    """Per-angle step budget = safety x p99.9 of clean-run steps,
    floored at floor_deg.

    clean_steps: (N, 13) steps from a clean (no-occlusion) run of the
    SAME pipeline. Derived, recorded in the scenario manifest, never
    hardcoded. Returns (13,).

    The floor exists for angles that are identically zero by
    construction (v1's elbow ez): their clean p99.9 is exactly 0 and
    float64 noise (~1e-14 deg, measured) would count as teleports
    against a zero budget. 1e-9 deg sits far above the noise and far
    below any real motion.
    """
    clean_steps = np.asarray(clean_steps, dtype=float)
    # NaN = a step excluded from the derivation (D-033: twist steps
    # with the twist unobservable on either frame); nanpercentile equals
    # percentile on NaN-free input, so D-003 budgets are unchanged
    return np.maximum(safety * np.nanpercentile(clean_steps, 99.9,
                                                axis=0),
                      floor_deg)


TWIST_ANGLES = ("r_twist", "l_twist")


def twist_step_valid(r_twist_ok, l_twist_ok):
    """D-033 step mask. r/l_twist_ok: (T,) per-frame twist
    observability (the solver's twist_ok, core/solver_q.py: elbow bent
    past v1's TWIST_EPS and wrist seen). Returns a (T-1, 13) bool mask:
    True everywhere except the r_twist / l_twist columns, which are True
    only when the twist was observable on BOTH frames of the step. Used
    by the budget derivation (masked steps become NaN) and by
    teleport_count(valid=...)."""
    ok = {"r_twist": np.asarray(r_twist_ok, dtype=bool),
          "l_twist": np.asarray(l_twist_ok, dtype=bool)}
    n = len(ok["r_twist"])
    if len(ok["l_twist"]) != n or n < 2:
        raise ValueError("twist_ok arrays must share length >= 2")
    valid = np.ones((n - 1, len(ANGLE_NAMES)), dtype=bool)
    for an in TWIST_ANGLES:
        valid[:, ANGLE_NAMES.index(an)] = ok[an][:-1] & ok[an][1:]
    return valid


def teleport_count(steps, budget, valid=None):
    """Hard-gate teleport check. steps: (T-1, 13); budget: (13,);
    valid: optional (T-1, 13) bool mask (D-033, twist_step_valid): a
    step with valid False is neither counted nor reported as worst.
    valid None = every step counts (the D-003 behaviour).

    Returns {"count": frames where ANY angle exceeds its budget,
             "worst_step_deg", "worst_ratio", "per_angle_counts": (13,)}.
    Gate passes iff count == 0.
    """
    steps = np.asarray(steps, dtype=float)
    budget = np.asarray(budget, dtype=float)
    if valid is not None:
        valid = np.asarray(valid, dtype=bool)
        if valid.shape != steps.shape:
            raise ValueError(f"valid {valid.shape} != steps {steps.shape}")
        steps = np.where(valid, steps, 0.0)
    exceed = steps > budget[None, :]
    ratio = np.divide(steps, budget[None, :],
                      out=np.zeros_like(steps), where=budget[None, :] > 0)
    return {
        "count": int(exceed.any(axis=1).sum()),
        "worst_step_deg": float(steps.max()),
        "worst_ratio": float(ratio.max()),
        "per_angle_counts": exceed.sum(axis=0),
    }


def continuity_p95(steps):
    """p95 |per-frame step| per angle over the FULL run. (T-1, 13) ->
    (13,). Applies to R-type runs too (no truth needed)."""
    return np.percentile(np.asarray(steps, dtype=float), 95, axis=0)


def joint_limit_violations(angles, limits):
    """Joint-limit violation fraction.

    angles: (T, 13); limits: dict angle_name -> (lo, hi) deg or None
    (unconstrained). Returns {"fraction": overall fraction of
    constrained samples out of range, "per_angle": dict name ->
    fraction for constrained angles only}.
    """
    angles = np.asarray(angles, dtype=float)
    per_angle = {}
    bad = 0
    total = 0
    for i, name in enumerate(ANGLE_NAMES):
        lim = limits.get(name)
        if lim is None:
            continue
        lo, hi = lim
        v = np.mean((angles[:, i] < lo) | (angles[:, i] > hi))
        per_angle[name] = float(v)
        bad += v * angles.shape[0]
        total += angles.shape[0]
    return {"fraction": float(bad / total) if total else 0.0,
            "per_angle": per_angle}


def bone_length_deviation(lengths, ref_lengths):
    """Fractional bone-length deviation |l - ref| / ref.

    lengths: (T, B) reconstructed bone lengths; ref_lengths: (B,)
    calibrated. Returns {"p95": (B,), "max": (B,)}.
    """
    lengths = np.asarray(lengths, dtype=float)
    ref = np.asarray(ref_lengths, dtype=float)
    if np.any(ref <= 0):
        raise ValueError("reference bone lengths must be positive")
    dev = np.abs(lengths - ref[None, :]) / ref[None, :]
    return {"p95": np.percentile(dev, 95, axis=0), "max": dev.max(axis=0)}


BONE_NAMES = ("r_upper_arm", "r_forearm", "l_upper_arm", "l_forearm")
BONE_ENDS = (("right_shoulder", "right_elbow"), ("right_elbow", "right_wrist"),
             ("left_shoulder", "left_elbow"), ("left_elbow", "left_wrist"))


def bone_lengths(points):
    """Per-frame arm bone lengths in metres.

    points: dict landmark name -> (T, 3) positions (any common frame;
    lengths are flip-invariant), NaN where missing. Returns (T, 4) in
    BONE_NAMES order; NaN where either end is missing.
    """
    cols = []
    for a, b in BONE_ENDS:
        pa = np.asarray(points[a], dtype=float)
        pb = np.asarray(points[b], dtype=float)
        if pa.shape != pb.shape or pa.ndim != 2 or pa.shape[1] != 3:
            raise ValueError(f"expected matching (T, 3) for {a}/{b}")
        cols.append(np.linalg.norm(pb - pa, axis=1))
    return np.stack(cols, axis=1)


def second_diff_rms(angles):
    """Frame-to-frame jitter: RMS of the second difference of each
    angle track, wrap-aware on the first difference. (T, 13) or (T,)
    -> (13,) or scalar, degrees per frame^2.

    Port of delta_stats in eval/pipeline_smoothness/
    compare_film_vs_live.py (d = wrap(diff(x)); sqrt(mean(diff(d)^2))).
    NaN in the input propagates to that angle's result.
    """
    a = np.asarray(angles, dtype=float)
    if a.shape[0] < 3:
        raise ValueError("need at least 3 frames")
    d = wrap_deg(np.diff(a, axis=0))
    d2 = np.diff(d, axis=0)
    return np.sqrt(np.mean(d2 ** 2, axis=0))


def rms_vs_ref(out, ref):
    """RMS of the wrapped difference out - ref per angle at lag 0.
    Shapes must match; (T, 13) -> (13,)."""
    out = np.asarray(out, dtype=float)
    ref = np.asarray(ref, dtype=float)
    if out.shape != ref.shape:
        raise ValueError(f"shape mismatch: {out.shape} vs {ref.shape}")
    return np.sqrt(np.mean(wrap_deg(out - ref) ** 2, axis=0))


def lag_overlap(x, ref, s):
    """Overlap of x[i] with ref[i - s] (s > 0: x lags ref by s)."""
    n = x.shape[0]
    return x[max(0, s):n + min(0, s)], ref[max(0, -s):n - max(0, s)]


def best_lag(out, ref, max_lag=10, criterion="rms", tie_tol_deg=1e-9):
    """Integer frame shift s in [-max_lag, max_lag] minimising the
    wrapped error between out[i] and ref[i - s], per angle; positive
    s means out LAGS ref by s frames.

    criterion "rms" (the V3 score) or "mean_abs" (the criterion of
    best_lag in eval/pipeline_smoothness/compare_film_vs_live.py,
    kept so that pinned table can be reproduced). Errors within
    tie_tol_deg of the minimum count as ties and go to the smallest
    |s|, then to the more negative s, so an angle that is zero by
    construction (v1 elbow ez, float64 noise ~1e-14 deg) reports lag 0
    instead of a noise-picked shift. tie_tol_deg 1e-9 is the same
    noise floor as teleport_budget's floor_deg.

    out, ref: (T, 13) or (T,). Returns (lags int array, error at the
    best lag), each (13,) or scalar.
    """
    out = np.asarray(out, dtype=float)
    ref = np.asarray(ref, dtype=float)
    if out.shape != ref.shape:
        raise ValueError(f"shape mismatch: {out.shape} vs {ref.shape}")
    if criterion not in ("rms", "mean_abs"):
        raise ValueError(f"unknown criterion {criterion!r}")
    if out.shape[0] <= 2 * max_lag:
        raise ValueError(f"series of {out.shape[0]} frames too short for "
                         f"max_lag {max_lag}")
    scalar = out.ndim == 1
    if scalar:
        out, ref = out[:, None], ref[:, None]
    lags = np.arange(-max_lag, max_lag + 1)
    errs = np.empty((len(lags), out.shape[1]))
    for i, s in enumerate(lags):
        a, b = lag_overlap(out, ref, int(s))
        d = np.abs(wrap_deg(a - b))
        errs[i] = (np.sqrt(np.mean(d ** 2, axis=0)) if criterion == "rms"
                   else np.mean(d, axis=0))
    order = np.argsort(np.abs(lags), kind="stable")   # 0, -1, 1, -2, 2 ...
    near = errs[order] <= errs.min(axis=0)[None, :] + tie_tol_deg
    pick = order[np.argmax(near, axis=0)]              # first near-min
    best = lags[pick].astype(int)
    err = errs[pick, np.arange(out.shape[1])]
    if scalar:
        return int(best[0]), float(err[0])
    return best, err


def circular_residual(out, ref, offset_deg=0.0):
    """Circular mean and circular std (RMS about the circular mean) of
    wrap(out - ref - offset), per angle; the statistic of
    bench/v1_offset_table.py. (T, 13) -> ((13,), (13,))."""
    d = wrap_deg(np.asarray(out, dtype=float) - np.asarray(ref, dtype=float)
                 - np.asarray(offset_deg, dtype=float))
    r = np.radians(d)
    mu = np.degrees(np.arctan2(np.sin(r).mean(axis=0),
                               np.cos(r).mean(axis=0)))
    dev = wrap_deg(d - mu)
    return mu, np.sqrt(np.mean(dev ** 2, axis=0))


def latency_summary(samples_ms, warmup=0):
    """Percentile summary of per-frame latency samples in ms, with the
    first `warmup` frames split out.

    Returns {"n", "p50", "p95", "p99", "max"} for the post-warmup
    samples plus {"warmup_n", "warmup_max"}.
    """
    samples_ms = np.asarray(samples_ms, dtype=float)
    body = samples_ms[warmup:]
    if body.shape[0] == 0:
        raise ValueError("no samples after warmup")
    head = samples_ms[:warmup]
    return {
        "n": int(body.shape[0]),
        "p50": float(np.percentile(body, 50)),
        "p95": float(np.percentile(body, 95)),
        "p99": float(np.percentile(body, 99)),
        "max": float(body.max()),
        "warmup_n": int(head.shape[0]),
        "warmup_max": float(head.max()) if head.shape[0] else 0.0,
    }


def latency_pass(summary, budget_ms):
    """Hard gate: total p99 must fit the frame budget."""
    return bool(summary["p99"] <= budget_ms)


def occlusion_conditional_p99(samples_ms, active, warmup=0):
    """p99 latency over frames where an occlusion strategy was active.

    active: (T,) bool mask, same length as samples_ms. A strategy that
    only blows the budget while active still fails. Returns float, or
    nan if no active frames after warmup.
    """
    samples_ms = np.asarray(samples_ms, dtype=float)
    active = np.asarray(active, dtype=bool)
    if samples_ms.shape != active.shape:
        raise ValueError("samples and active mask must align")
    sel = samples_ms[warmup:][active[warmup:]]
    if sel.shape[0] == 0:
        return math.nan
    return float(np.percentile(sel, 99))


def honesty_confusion(status, windows, slop=2):
    """Status honesty vs the scenario manifest.

    status: (T, 7) ints in {MEASURED, ESTIMATED, LOST}.
    windows: list of (group_index, start, stop) truth-occluded windows
      (group_index in 0..6, frames [start, stop)).
    slop: frames around each window boundary excluded from judgment
      (detector latency at boundaries is not dishonesty).

    Returns {"matrix": (2, 3) counts [truth occluded/visible x status],
             "false_measured": fraction of judged occluded frames
                               reported MEASURED (hard gate < 1%),
             "estimated_coverage": fraction of judged occluded frames
                               reported ESTIMATED,
             "judged_occluded": count, "judged_visible": count}.
    """
    status = np.asarray(status)
    if status.ndim != 2 or status.shape[1] != len(GROUP_NAMES):
        raise ValueError(f"expected (T, 7), got {status.shape}")
    t_n = status.shape[0]
    occluded = np.zeros((t_n, len(GROUP_NAMES)), dtype=bool)
    judged = np.ones((t_n, len(GROUP_NAMES)), dtype=bool)
    for g, start, stop in windows:
        occluded[start:stop, g] = True
        judged[max(0, start - slop):min(t_n, start + slop), g] = False
        judged[max(0, stop - slop):min(t_n, stop + slop), g] = False
    matrix = np.zeros((2, 3), dtype=int)
    for truth_row, truth_mask in ((0, occluded), (1, ~occluded)):
        sel = status[judged & truth_mask]
        for s in (MEASURED, ESTIMATED, LOST):
            matrix[truth_row, s] = int((sel == s).sum())
    judged_occ = int(matrix[0].sum())
    judged_vis = int(matrix[1].sum())
    return {
        "matrix": matrix,
        "false_measured": (matrix[0, MEASURED] / judged_occ
                           if judged_occ else 0.0),
        "estimated_coverage": (matrix[0, ESTIMATED] / judged_occ
                               if judged_occ else 0.0),
        "judged_occluded": judged_occ,
        "judged_visible": judged_vis,
    }


def _average_ranks(values):
    """Ranks (1-based, ties averaged) for a list of scalars, low = good."""
    order = np.argsort(values, kind="stable")
    ranks = np.empty(len(values), dtype=float)
    i = 0
    while i < len(values):
        j = i
        while (j + 1 < len(values)
               and values[order[j + 1]] == values[order[i]]):
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def rank_strategies(scores, gates, tie_break_key=None):
    """Frozen ranking rule (D-003).

    scores: {strategy: {metric_scenario_key: float}} where lower is
      better; every strategy must carry the same keys.
    gates: {strategy: {gate_name: bool}}; any False disqualifies.
    tie_break_key: score key used to break mean-rank ties (the
      wrist_long scenario per bench.json).

    Returns a list of dicts ordered best first:
      {"strategy", "disqualified", "failed_gates", "mean_rank"}.
    Disqualified strategies are excluded from ranking and listed last
    with mean_rank None.
    """
    names = sorted(scores)
    keys = None
    for n in names:
        k = sorted(scores[n])
        if keys is None:
            keys = k
        elif k != keys:
            raise ValueError(f"strategy {n} has mismatched score keys")
    failed = {n: sorted(g for g, ok in gates.get(n, {}).items() if not ok)
              for n in names}
    qualified = [n for n in names if not failed[n]]
    mean_rank = {}
    if qualified and keys:
        per_key = np.stack([_average_ranks([scores[n][k] for n in qualified])
                            for k in keys])
        for i, n in enumerate(qualified):
            mean_rank[n] = float(per_key[:, i].mean())

    def sort_key(n):
        tie = scores[n].get(tie_break_key, 0.0) if tie_break_key else 0.0
        return (mean_rank[n], tie, n)

    ordered = sorted(qualified, key=sort_key)
    out = [{"strategy": n, "disqualified": False, "failed_gates": [],
            "mean_rank": mean_rank[n]} for n in ordered]
    out += [{"strategy": n, "disqualified": True, "failed_gates": failed[n],
             "mean_rank": None} for n in names if failed[n]]
    return out

"""Offline zero-phase oracle for the clean-window bench (D-024).

The defence films (presentation/defense_2026, pages 13-16) were built
from landmarks filtered offline by v1/mediapipe/filter_landmarks.py with
the settings in presentation/defense_2026/anim/bank_axes_kinematics.py
lines 217-220. This module REIMPLEMENTS that filter (it never imports
it; V3 reuse is copy-only, D-007) and feeds the result through the V3
solve: centered Hampel -> NaN gap interpolation -> Butterworth
filtfilt per contiguous segment -> Unity flip -> core.solver_q
.solve_frame_q -> core.convert.angles13. tests/test_oracle.py
reproduces the film's filtered landmarks from the film's raw
landmarks.

Semantics copied from filter_landmarks.py (read, not imported):
- Hampel: pandas rolling window, center=True, min_periods; residual
  |x - median|; MAD = rolling median of the residual (same window);
  a sample is a spike when ANY axis residual exceeds
  max(floor, k * mad_scale * MAD) and all three axes are finite.
  Spikes become NaN.
- Gap fill: NaN runs strictly inside the valid span of length
  <= max_gap are linearly interpolated over time_s against every valid
  sample (np.interp); runs touching either end are backfilled with the
  nearest valid sample only when their length <= edge_fill (0 = off).
- Butterworth: butter(order, cutoff_hz, fs=fs) with fs = 1 / median
  (diff(time_s)); filtfilt per axis on each contiguous finite segment;
  a segment of length <= scipy's default filtfilt padlen
  (3 * max(len(a), len(b))) is left unfiltered, exactly as v1 does.

The oracle is NOT external truth: it is the same detector output,
smoothed with look-ahead. RMS against it measures agreement with a
zero-lag smoothed version of the same measurement (self-consistency),
not accuracy against the true arm angle.

Everything runs on the WHOLE recording, then callers slice their
window, because the film filtered whole recordings.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt

V3_ROOT = Path(__file__).resolve().parents[1]
if str(V3_ROOT) not in sys.path:
    sys.path.insert(0, str(V3_ROOT))

from bench.metrics import ANGLE_NAMES, GROUP_ANGLES, GROUP_NAMES  # noqa: E402
from core import convert, solver_q                     # noqa: E402
from core.skeleton import V1_LANDMARKS                 # noqa: E402

SENSOR_TO_UNITY = np.array([1.0, -1.0, 1.0])  # same flip as replay/runner.py

FLAG_RAW, FLAG_GLITCH_INTERP, FLAG_MISS_INTERP, FLAG_MISS = 0, 1, 2, 3

_REQUIRED_KEYS = ("hampel_window", "hampel_k", "hampel_floor_m",
                  "hampel_min_periods", "mad_scale", "max_gap",
                  "edge_fill", "butter_order", "cutoff_hz", "fs")


def _ocfg(cfg):
    """The oracle block, checked: every key present and non-null
    (D-006: fail loudly, never default)."""
    o = cfg["oracle"] if "oracle" in cfg else None
    if o is None:
        raise KeyError("config has no 'oracle' block")
    for k in _REQUIRED_KEYS:
        if o.get(k) is None:
            raise ValueError(f"oracle.{k} is missing or null")
    if o["fs"] != "median_dt":
        raise ValueError(f"oracle.fs must be 'median_dt', got {o['fs']!r}")
    return o


def sample_rate(t):
    """fs as filter_landmarks.py derives it: 1 / median frame step."""
    t = np.asarray(t, dtype=float)
    if len(t) < 2:
        raise ValueError("need at least 2 timestamps to derive fs")
    return 1.0 / float(np.median(np.diff(t)))


def hampel_mask(pos, window, k, floor, min_periods, mad_scale):
    """pos: (F, 3) with NaNs. True where a sample is a spike on any
    axis (centered window)."""
    df = pd.DataFrame(pos)
    med = df.rolling(window, center=True, min_periods=min_periods).median()
    resid = (df - med).abs()
    mad = resid.rolling(window, center=True,
                        min_periods=min_periods).median()
    thresh = np.maximum(floor, k * mad_scale * mad)
    return ((resid > thresh).any(axis=1).to_numpy()
            & np.isfinite(pos).all(axis=1))


def _runs(mask):
    """(start, stop) index ranges of consecutive True values."""
    idx = np.flatnonzero(np.diff(np.concatenate(([False], mask, [False]))))
    return list(zip(idx[::2], idx[1::2]))


def fill_gaps(pos, t, max_gap, edge_fill):
    """Linear interpolation of interior NaN runs <= max_gap; edge runs
    <= edge_fill backfilled with the nearest valid sample. Returns
    (filled positions, mask of filled samples)."""
    out = pos.copy()
    filled = np.zeros(len(pos), dtype=bool)
    missing = ~np.isfinite(pos).all(axis=1)
    valid_idx = np.flatnonzero(~missing)
    if len(valid_idx) < 2:
        return out, filled
    for start, stop in _runs(missing):
        run = stop - start
        interior = start > valid_idx[0] and stop <= valid_idx[-1]
        if interior and run <= max_gap:
            for ax in range(3):
                out[start:stop, ax] = np.interp(t[start:stop], t[~missing],
                                                pos[~missing, ax])
            filled[start:stop] = True
        elif not interior and run <= edge_fill:
            src = valid_idx[0] if start == 0 else valid_idx[-1]
            out[start:stop] = pos[src]
            filled[start:stop] = True
    return out, filled


def butter_segments(pos, fs, order, cutoff_hz):
    """Zero-phase Butterworth per axis on each contiguous finite
    segment; segments too short for filtfilt's default padding stay
    as they are."""
    out = pos.copy()
    b, a = butter(order, cutoff_hz, fs=fs)
    padlen = 3 * max(len(a), len(b))   # scipy filtfilt default padlen
    valid = np.isfinite(pos).all(axis=1)
    for start, stop in _runs(valid):
        if stop - start > padlen:
            for ax in range(3):
                out[start:stop, ax] = filtfilt(b, a, pos[start:stop, ax])
    return out


def filter_landmark(pos, t, o, fs):
    """One landmark (F, 3) camera-frame track -> (filtered (F, 3),
    flags (F,)) with the filter_landmarks.py flag legend."""
    pos = np.asarray(pos, dtype=float)
    flags = np.full(len(pos), FLAG_RAW, dtype=int)
    missing_before = ~np.isfinite(pos).all(axis=1)
    work = pos.copy()
    spikes = hampel_mask(work, int(o["hampel_window"]), float(o["hampel_k"]),
                         float(o["hampel_floor_m"]),
                         int(o["hampel_min_periods"]),
                         float(o["mad_scale"]))
    work[spikes] = np.nan
    work, filled = fill_gaps(work, t, int(o["max_gap"]), int(o["edge_fill"]))
    still_missing = ~np.isfinite(work).all(axis=1)
    flags[spikes & filled] = FLAG_GLITCH_INTERP
    flags[missing_before & filled] = FLAG_MISS_INTERP
    flags[still_missing] = FLAG_MISS
    work = butter_segments(work, fs, int(o["butter_order"]),
                           float(o["cutoff_hz"]))
    return work, flags


def read_landmarks(df):
    """CSV DataFrame -> {name: (F, 3) camera-frame xyz, NaN = missing}."""
    return {name: df[[f"{name}_x", f"{name}_y", f"{name}_z"]]
            .to_numpy(dtype=float) for name in V1_LANDMARKS}


def filter_landmarks(df, cfg):
    """Oracle landmark filter on a whole extraction. Returns
    ({name: filtered (F, 3) camera frame}, {name: flags (F,)}, fs)."""
    o = _ocfg(cfg)
    t = df["time_s"].to_numpy(dtype=float)
    fs = sample_rate(t)
    raw = read_landmarks(df)
    filt, flags = {}, {}
    for name in V1_LANDMARKS:
        filt[name], flags[name] = filter_landmark(raw[name], t, o, fs)
    return filt, flags, fs


def solve_table(df, pts_cam):
    """Stateless per-frame solve. pts_cam: {name: (F, 3) camera frame}.
    Returns a DataFrame: frame, time_s, the 13 angles (NaN where the
    owning group is unsolvable this frame), r/l_twist_ok, and the
    Unity-space landmark columns <name>_fx/_fy/_fz (same naming as
    replay.runner.run_csv)."""
    n = len(df)
    unity = {k: v * SENSOR_TO_UNITY[None, :] for k, v in pts_cam.items()}
    angles = np.full((n, len(ANGLE_NAMES)), np.nan)
    tw = np.zeros((n, 2), dtype=bool)
    ident = np.array([1.0, 0.0, 0.0, 0.0])
    g = {name: i for i, name in enumerate(GROUP_NAMES)}
    for i in range(n):
        pts = {k: (v[i] if np.all(np.isfinite(v[i])) else None)
               for k, v in unity.items()}
        s = solver_q.solve_frame_q(pts)
        q = {k: (s[k] if s[k] is not None else ident)
             for k in ("root", "r_sh", "r_elb", "l_sh", "l_elb")}
        a = convert.angles13(q["root"], q["r_sh"], q["r_elb"],
                             q["l_sh"], q["l_elb"])
        for key, groups in (("root", ("root",)),
                            ("r_sh", ("R_swing", "R_twist")),
                            ("r_elb", ("R_elbow",)),
                            ("l_sh", ("L_swing", "L_twist")),
                            ("l_elb", ("L_elbow",))):
            if s[key] is None:
                for gn in groups:
                    a[list(GROUP_ANGLES[g[gn]])] = np.nan
        angles[i] = a
        tw[i] = (s["r_twist_ok"], s["l_twist_ok"])
    out = pd.DataFrame({"frame": df["frame"].to_numpy(dtype=int),
                        "time_s": df["time_s"].to_numpy(dtype=float)})
    for j, an in enumerate(ANGLE_NAMES):
        out[an] = angles[:, j]
    out["r_twist_ok"] = tw[:, 0]
    out["l_twist_ok"] = tw[:, 1]
    for name in V1_LANDMARKS:
        for c, ax in enumerate("xyz"):
            out[f"{name}_f{ax}"] = unity[name][:, c]
    return out


def oracle_angles(csv_path, cfg):
    """Oracle table for a whole extraction CSV: filtered landmarks
    solved statelessly. Extra columns <name>_flag carry the filter
    provenance flags. df.attrs['fs_hz'] records the derived rate."""
    df = pd.read_csv(csv_path)
    filt, flags, fs = filter_landmarks(df, cfg)
    out = solve_table(df, filt)
    for name in V1_LANDMARKS:
        out[f"{name}_flag"] = flags[name]
    out.attrs["fs_hz"] = fs
    return out


def raw_angles(csv_path):
    """The unfiltered reference: raw CSV landmarks solved statelessly,
    no Hampel, no fill, no smoothing (the 'raw' column)."""
    df = pd.read_csv(csv_path)
    return solve_table(df, read_landmarks(df))


def require_twist_min_bend(mapping, where):
    """D-006/D-033: the elbow-bend threshold of the twist gate, read from
    a config budget block or a scenario manifest. The key must be
    present and non-null wherever the oracle twist gate is in force (a
    missing value would silently reduce the gate to twist_ok alone, the
    vacuous gate D-033 records), so this raises ValueError naming the
    key and the source instead of returning None."""
    v = mapping.get("twist_min_bend_deg") if hasattr(mapping, "get") \
        else None
    if v is None:
        raise ValueError(
            f"{where}: 'twist_min_bend_deg' is missing or null; it is "
            "required when the D-033 oracle twist gate is in force "
            "(D-006: no silent fallback)")
    float(v)            # non-numeric values fail here, loudly
    return v


def twist_observable(tab, min_bend_deg):
    """D-033 twist observability per frame for r and l: the solver's
    twist_ok AND an elbow bend >= min_bend_deg, with sin(bend) =
    |forearm perpendicular to the upper-arm axis| / |forearm| computed
    from the table's Unity-space landmark columns <name>_fx/_fy/_fz (a
    rigid root rotation leaves the ratio unchanged, so it equals the
    solver's root-frame value). NaN landmarks -> False. min_bend_deg
    None -> twist_ok alone: an explicit argument for callers that want
    the ungated solver flag (tests, diagnostics); the D-033 gate paths
    obtain the threshold through require_twist_min_bend, which never
    returns None. Returns (r_ok, l_ok) bool arrays."""
    out = []
    for sd, nm in (("r", "right"), ("l", "left")):
        ok = tab[f"{sd}_twist_ok"].to_numpy(dtype=bool)
        if min_bend_deg is not None:
            def P(n):
                return tab[[f"{n}_fx", f"{n}_fy", f"{n}_fz"]].to_numpy(
                    dtype=float)
            u = P(f"{nm}_elbow") - P(f"{nm}_shoulder")
            f = P(f"{nm}_wrist") - P(f"{nm}_elbow")
            with np.errstate(invalid="ignore", divide="ignore"):
                u = u / np.linalg.norm(u, axis=1, keepdims=True)
                perp = np.linalg.norm(
                    f - (f * u).sum(axis=1)[:, None] * u, axis=1)
                s = perp / np.linalg.norm(f, axis=1)
            thr = np.sin(np.radians(float(min_bend_deg)))
            ok = ok & np.nan_to_num(s >= thr, nan=False).astype(bool)
        out.append(ok)
    return out[0], out[1]

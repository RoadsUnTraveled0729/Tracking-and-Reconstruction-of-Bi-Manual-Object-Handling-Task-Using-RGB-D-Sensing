#!/usr/bin/env python3
"""Measured behaviour of offline and causal smoothers on the pinned R6b wrist.

Inputs (read only, hash-checked against presentation/defense_2026/FILTER_DEMO_BRIEF.json):
  presentation/defense_2026/media/provenance/filter_demo_raw_r6b.csv
  v1/mediapipe/filter_landmarks.py (frozen V1 filter functions)

Pipeline per candidate, on the right-wrist x, y, z (metres, camera frame):
  1. Common despiked baseline: frozen hampel_mask (window 7, k 3, floor 0.02 m),
     flagged samples set to NaN, then frozen fill_gaps (max gap 5 frames, no
     edge fill). This is the "despiked raw" reference for every metric.
  2. Each candidate smoother runs per contiguous valid segment of the baseline.
  3. Metrics are taken only on frames inside segments longer than 15 frames
     (the frozen Butterworth leaves shorter segments unfiltered), see
     presentation/defense_2026/DECISIONS.md D-160 to D-168.

Outputs (written next to this script):
  results.csv   one row per candidate x axis (x, y, z, norm)
  summary.csv   the 3-D norm rows only
  chart_filter_offline.png, chart_filter_realtime.png  (2466x1110 px)
  run_info.json  hashes, frame counts, thresholds and the excerpt window

Run:  /home/luo/anaconda3/bin/python \
        presentation/defense_2026/experiments/filter_metrics/filter_metrics.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
sys.dont_write_bytecode = True   # never write __pycache__ into frozen or deck folders
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
from scipy.signal import butter, lfilter, lfilter_zi

HERE = Path(__file__).resolve().parent
DECK = HERE.parents[1]                      # presentation/defense_2026
REPO = DECK.parents[1]
BRIEF = json.loads((DECK/"FILTER_DEMO_BRIEF.json").read_text())

# Constants. Sources are logged in presentation/defense_2026/DECISIONS.md D-160 to D-168.
FAST_PERCENTILE = 80.0      # fast-motion frames: despiked-raw 3-D speed >= 80th percentile
MIN_SEGMENT = 16            # frozen butter filters a segment only when n > 3*max(len(a),len(b)) = 15
MAX_LAG = 15                # cross-correlation search range, +-15 frames (about 0.5 s)
EMA_ALPHA = 0.3             # naive causal baseline, set by the brief
EXCERPT_FRAMES = 120        # 4 s at 29.98 Hz, rounded to whole frames


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_frozen():
    impl = REPO/BRIEF["implementation"]
    assert digest(impl) == BRIEF["implementation_sha256"], "frozen filter file changed"
    spec = importlib.util.spec_from_file_location("frozen_filter_metrics_source", impl)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FROZEN = load_frozen()


def load_data():
    csv_path = REPO/BRIEF["source_csv"]
    assert digest(csv_path) == BRIEF["source_sha256"], "pinned CSV changed"
    data = pd.read_csv(csv_path)
    times = data["time_s"].to_numpy(float)
    pos = data[[f"right_wrist_{a}" for a in "xyz"]].to_numpy(float)
    fs = 1.0/float(np.median(np.diff(times)))        # same rule as filter_demos.py
    return data["frame"].to_numpy(int), times, pos, fs


def base_args(**override):
    params = dict(BRIEF["parameters"])
    params.pop("fs", None)
    params.update(override)
    return SimpleNamespace(**params)


def per_segment(pos, fn):
    """Apply fn to every contiguous finite segment (N, 3) -> (N, 3)."""
    out = pos.copy()
    valid = np.isfinite(pos).all(axis=1)
    for start, stop in FROZEN.nan_runs(valid):
        out[start:stop] = fn(pos[start:stop])
    return out


def butter_forward(seg, fs, order, cutoff):
    """Causal Butterworth: one forward lfilter pass, steady state at the first sample."""
    b, a = butter(order, cutoff, fs=fs)
    zi = lfilter_zi(b, a)
    out = np.empty_like(seg)
    for ax in range(3):
        out[:, ax], _ = lfilter(b, a, seg[:, ax], zi=zi*seg[0, ax])
    return out


def ema(seg, alpha):
    out = np.empty_like(seg)
    out[0] = seg[0]
    for i in range(1, len(seg)):
        out[i] = alpha*seg[i] + (1-alpha)*out[i-1]
    return out


def candidates(base, fs):
    """name -> (label, mode, filtered array). Order is the reporting order."""
    a = base_args()
    sm = FROZEN.smooth_landmark
    return {
        "despiked_raw": ("Despiked raw", "reference", base.copy()),
        "savgol_9_2": ("Savitzky-Golay 9/2", "offline", sm(base, "savgol", fs, a)),
        "median_9": ("Median 9", "offline", sm(base, "median", fs, a)),
        "butter_3hz_filtfilt": ("Butterworth 3 Hz filtfilt", "offline", sm(base, "butter", fs, a)),
        "butter_2hz_filtfilt": ("Butterworth 2 Hz filtfilt", "offline",
                                sm(base, "butter", fs, base_args(cutoff_hz=2.0))),
        "butter_3hz_forward": ("Butterworth 3 Hz forward", "causal",
                               per_segment(base, lambda s: butter_forward(s, fs, a.butter_order, a.cutoff_hz))),
        "oneeuro_0p05hz": ("One Euro 0.05 Hz", "causal", sm(base, "oneeuro", fs, a)),
        "oneeuro_1hz": ("One Euro 1 Hz", "causal",
                        sm(base, "oneeuro", fs, base_args(oneeuro_mincutoff=1.0))),
        "ema_0p3": ("EMA alpha 0.3", "causal", per_segment(base, lambda s: ema(s, EMA_ALPHA))),
    }


def eval_segments(base):
    valid = np.isfinite(base).all(axis=1)
    return [(s, e) for s, e in FROZEN.nan_runs(valid) if e-s >= MIN_SEGMENT]


def speeds(base, segs, fs):
    """3-D speed (m/s) of the despiked raw, central differences within each segment."""
    v = np.full(len(base), np.nan)
    for s, e in segs:
        g = np.gradient(base[s:e], axis=0)*fs
        v[s:e] = np.linalg.norm(g, axis=1)
    return v


def shake(sig, segs):
    """RMS frame-to-frame displacement per axis and 3-D (m)."""
    d = np.concatenate([np.diff(sig[s:e], axis=0) for s, e in segs])
    return np.sqrt(np.mean(d**2, axis=0)), float(np.sqrt(np.mean(np.sum(d**2, axis=1))))


def deviation(sig, base, fast):
    """RMS filtered-minus-despiked-raw on fast frames, per axis and 3-D distance (m)."""
    d = (sig-base)[fast]
    return np.sqrt(np.mean(d**2, axis=0)), float(np.sqrt(np.mean(np.sum(d**2, axis=1))))


def lag_curve(sig, base, segs, axes):
    """Normalised cross-correlation for shifts -MAX_LAG..MAX_LAG.

    Shift s compares filtered[t] with despiked_raw[t-s]; a positive best shift
    means the filtered signal is delayed. Means are removed per segment; the
    sums run over all evaluated segments and the requested axes.
    """
    shifts = np.arange(-MAX_LAG, MAX_LAG+1)
    corr = []
    for s in shifts:
        num = vf = vr = 0.0
        for a, b in segs:
            f = sig[a:b][:, axes]; r = base[a:b][:, axes]
            f = f-f.mean(axis=0); r = r-r.mean(axis=0)
            if s >= 0: fp, rp = f[s:], r[:len(r)-s]
            else: fp, rp = f[:len(f)+s], r[-s:]
            num += float(np.sum(fp*rp)); vf += float(np.sum(fp*fp)); vr += float(np.sum(rp*rp))
        corr.append(num/np.sqrt(vf*vr))
    return shifts, np.asarray(corr)


def best_lag(sig, base, segs, axes):
    shifts, corr = lag_curve(sig, base, segs, axes)
    i = int(np.argmax(corr))
    sub = float(shifts[i])
    if 0 < i < len(corr)-1:                     # parabolic peak refinement
        y0, y1, y2 = corr[i-1], corr[i], corr[i+1]
        den = y0-2*y1+y2
        if den != 0: sub = float(shifts[i]+0.5*(y0-y2)/den)
    return int(shifts[i]), sub, float(corr[i])


def choose_excerpt(base, segs, fs):
    """Start frame of the 120-frame window with the highest mean |dz/dt|."""
    best = None
    for s, e in segs:
        z = base[s:e, 2]
        vz = np.abs(np.gradient(z))*fs
        for start in range(0, e-s-EXCERPT_FRAMES+1):
            score = float(np.mean(vz[start:start+EXCERPT_FRAMES]))
            if best is None or score > best[1]:
                best = (s+start, score)
    return best


def check_against_films(pos, fs):
    """Frozen smoothers on the raw valid runs must equal the film data (filter_demos.py)."""
    sys.path.insert(0, str(DECK/"anim"))
    import filter_demos                                     # hash-checks and replays the films
    a = base_args()
    worst = 0.0
    for m in ("butter", "oneeuro", "savgol", "median"):
        mine = FROZEN.smooth_landmark(pos, m, fs, a)
        film = filter_demos.DATA["outputs"][m]
        assert np.array_equal(np.isnan(mine), np.isnan(film))
        worst = max(worst, float(np.nanmax(np.abs(mine-film))))
    assert worst == 0.0, worst
    return worst


def main(make_charts=True):
    frames, times, pos, fs = load_data()
    a = base_args()
    mask = FROZEN.hampel_mask(pos, a.hampel_window, a.hampel_k, a.hampel_floor)
    work = pos.copy(); work[mask] = np.nan
    base, filled = FROZEN.fill_gaps(work, times, a.max_gap, a.edge_fill)
    film_error = check_against_films(pos, fs)

    segs = eval_segments(base)
    v = speeds(base, segs, fs)
    in_eval = np.zeros(len(base), bool)
    for s, e in segs: in_eval[s:e] = True
    threshold = float(np.percentile(v[in_eval], FAST_PERCENTILE))
    fast = in_eval & (v >= threshold)
    cands = candidates(base, fs)
    frame_ms = 1000.0/fs

    rows = []
    for key, (label, mode, sig) in cands.items():
        assert np.isfinite(sig[in_eval]).all()
        sh_ax, sh_n = shake(sig, segs)
        dv_ax, dv_n = deviation(sig, base, fast)
        for i, axis in enumerate(["x", "y", "z", "norm"]):
            axes = [i] if i < 3 else [0, 1, 2]
            lag_i, lag_sub, peak = best_lag(sig, base, segs, axes)
            rows.append({
                "candidate": key, "label": label, "mode": mode, "axis": axis,
                "shake_mm": round(1000*(sh_ax[i] if i < 3 else sh_n), 4),
                "fast_deviation_mm": round(1000*(dv_ax[i] if i < 3 else dv_n), 4),
                "lag_frames": lag_i,
                "lag_frames_subframe": round(lag_sub, 4),
                "lag_ms": round(lag_i*frame_ms, 2) if mode == "causal" else "",
                "lag_ms_subframe": round(lag_sub*frame_ms, 2) if mode == "causal" else "",
                "xcorr_peak": round(peak, 6),
            })
    res = pd.DataFrame(rows)
    res.to_csv(HERE/"results.csv", index=False, lineterminator="\n")
    summ = res[res["axis"] == "norm"].drop(columns=["axis"])
    summ.to_csv(HERE/"summary.csv", index=False, lineterminator="\n")

    ex_start, ex_score = choose_excerpt(base, segs, fs)
    info = {
        "source_csv": BRIEF["source_csv"], "source_sha256": BRIEF["source_sha256"],
        "implementation": BRIEF["implementation"], "implementation_sha256": BRIEF["implementation_sha256"],
        "sampling_rate_hz": round(fs, 6), "frames_total": int(len(pos)),
        "hampel_flagged_frames": np.flatnonzero(mask).tolist(),
        "gap_filled_frames": np.flatnonzero(filled).tolist(),
        "evaluated_segments_half_open": [[int(s), int(e)] for s, e in segs],
        "evaluated_frames": int(in_eval.sum()), "shake_pairs": int(sum(e-s-1 for s, e in segs)),
        "fast_speed_percentile": FAST_PERCENTILE, "fast_speed_threshold_m_per_s": round(threshold, 6),
        "fast_frames": int(fast.sum()), "max_lag_frames": MAX_LAG, "frame_ms": round(frame_ms, 4),
        "ema_alpha": EMA_ALPHA,
        "excerpt_frames_inclusive": [int(ex_start), int(ex_start+EXCERPT_FRAMES-1)],
        "excerpt_mean_abs_dz_dt_m_per_s": round(ex_score, 6),
        "film_replay_max_abs_error_m": film_error,
    }
    (HERE/"run_info.json").write_text(json.dumps(info, indent=2)+"\n")
    if make_charts:
        import charts
        charts.render(HERE, times, base, cands, summ, ex_start, EXCERPT_FRAMES, fs)
    print(summ[["candidate", "mode", "shake_mm", "fast_deviation_mm", "lag_frames",
                "lag_frames_subframe", "lag_ms_subframe"]].to_string(index=False))
    print(json.dumps({k: info[k] for k in ("evaluated_frames", "fast_frames",
          "fast_speed_threshold_m_per_s", "excerpt_frames_inclusive")}))


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    main(make_charts="--no-charts" not in sys.argv)

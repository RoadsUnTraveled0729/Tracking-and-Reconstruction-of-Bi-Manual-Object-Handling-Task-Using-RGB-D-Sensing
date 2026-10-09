#!/usr/bin/env python3
"""Film angles (defence pages 14 and 16) vs the v1 live person path.

Reads the defence-film kinematics (offline chain) and the replay CSVs made
by replay_live_person.py plus the unmodified realtime_person.py dumps, and
writes per-frame series, a metrics table, a timing table and plots.

Series (all right arm, degrees, PSA5 conventions):
  film        presentation/.../unified_four/pNN/derived_kinematics.csv:
              offline raw -> centered Hampel -> gap interp -> Butterworth
              3 Hz zero-phase -> solve_right_arm (film producer)
  raw_gated   replay raw landmarks (MediaPipe + visibility gate + 5x5 depth,
              no filter) -> ChainFallbackSolver           [live stage 1]
  despiked    raw landmarks accepted by the causal Hampel (rejects become
              missing, solver holds) -> ChainFallbackSolver [live stage 2]
  live_cpu    replay angles after the full CausalLandmarkFilter (Hampel +
              One-Euro), MediaPipe CPU delegate = same MediaPipe output
              as the film                               [live stage 3]
  live_gpu    same, MediaPipe GPU delegate (the live default)
  live_dump   v1/realtime/person/realtime_person.py run unmodified, paced
              playback, GPU: the values it wrote to shared memory
  oneeuro_only  DIAGNOSTIC, not a live-path stage: raw landmarks through the
              live One-Euro settings with the causal Hampel removed, to
              separate the two halves of CausalLandmarkFilter
Column held_or_repaired_frames: for live-path series, window frames whose
solver bit for that angle is unset (the solver held the last value); for the
film, window frames in which the offline filter repaired (interpolated) at
least one of the six required landmarks.

Usage: /home/luo/anaconda3/bin/python compare_film_vs_live.py
"""
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "v1/kinematics"))
from occlusion import (ChainFallbackSolver, BIT_R_SWING, BIT_R_TWIST,  # noqa: E402
                       BIT_R_ELBOW)
from root_frame import unity_from_sensor  # noqa: E402
sys.path.insert(0, str(REPO / "v1/mediapipe"))
from filter_landmarks import OneEuro  # noqa: E402

DEF = REPO / "presentation/defense_2026"
DATA = HERE / "data"
PLOTS = HERE / "plots"
NAMES = ["left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
         "left_wrist", "right_wrist", "left_hip", "right_hip"]
RIGHT_CHAIN = ["left_hip", "right_hip", "right_shoulder", "right_elbow",
               "right_wrist"]
ANGLE_COL = {"sh_y": 3, "sh_z": 4, "sh_twist": 5, "el_y": 6, "el_z": 7}
ANGLE_BIT = {"sh_y": BIT_R_SWING, "sh_z": BIT_R_SWING,
             "sh_twist": BIT_R_TWIST, "el_y": BIT_R_ELBOW, "el_z": BIT_R_ELBOW}
PAGES = {
    16: {"tag": "p16_right_elbow", "extraction": "p19", "start": 180, "end": 540,
         "angles": ["el_y", "el_z", "sh_y", "sh_z", "sh_twist"],
         "stem": "p16-Elbow_Rotation_Onto_Forearm"},
    14: {"tag": "p14_180042", "extraction": "p17", "start": 3, "end": 109,
         "angles": ["sh_y", "sh_z", "sh_twist", "el_y", "el_z"],
         "stem": "p14-Shoulder_Swing_Rotates_Root_Frame_Onto_Upper_Arm"},
}
MAX_LAG = 10   # frames searched for the best alignment shift; DECISIONS.md PS-004
COLORS = {"film": "#2a78d6", "live_cpu": "#eb6834", "raw_gated": "#1baf7a"}


def wrap(d):
    return (np.asarray(d, float) + 180.0) % 360.0 - 180.0


def solve_series(xyz_by_name):
    """xyz_by_name: name -> (N,3) sensor-frame array, NaN = missing.
    Returns (N,13) angles and (N,) masks from a fresh ChainFallbackSolver,
    exactly as the live loop feeds it (unity_from_sensor, absent if NaN)."""
    n = len(next(iter(xyz_by_name.values())))
    solver = ChainFallbackSolver()
    out, masks = np.zeros((n, 13)), np.zeros(n, int)
    for i in range(n):
        pts = {k: unity_from_sensor(v[i]) for k, v in xyz_by_name.items()
               if np.all(np.isfinite(v[i]))}
        a, m = solver.solve(pts)
        out[i], masks[i] = a, m
    return out, masks


def delta_stats(x):
    d = wrap(np.diff(x))
    d2 = np.diff(d)
    return float(np.std(d)), float(np.mean(np.abs(d))), float(np.sqrt(np.mean(d2 ** 2)))


def best_lag(x, ref):
    """Integer shift s (x[i] vs ref[i - s]) minimising mean |x - ref|;
    positive s = x lags ref by s frames."""
    best = (0, np.inf)
    n = len(x)
    for s in range(-MAX_LAG, MAX_LAG + 1):
        a = x[max(0, s):n + min(0, s)]
        b = ref[max(0, -s):n - max(0, s)]
        e = float(np.mean(np.abs(wrap(a - b))))
        if e < best[1]:
            best = (s, e)
    return best


def main():
    PLOTS.mkdir(exist_ok=True)
    metrics, timing, checks, halfspeed = [], [], {}, []
    for page, cfg in PAGES.items():
        tag, s0, s1 = cfg["tag"], cfg["start"], cfg["end"]
        film = pd.read_csv(DEF / f"bank_processing/unified_four/p{page}/derived_kinematics.csv"
                           ).set_index("frame")
        ffilt = pd.read_csv(DEF / f"bank_processing/{cfg['extraction']}/landmarks_filtered.csv")
        fraw = pd.read_csv(DEF / f"bank_processing/{cfg['extraction']}/landmarks_raw.csv")
        cpu = pd.read_csv(DATA / f"{tag}_replay_cpu.csv")
        gpu = pd.read_csv(DATA / f"{tag}_replay_gpu.csv")
        paced = pd.read_csv(DATA / f"{tag}_replay_gpu_paced.csv")
        dump = pd.read_csv(DATA / f"{tag}_live_paced_dump.csv")
        n = len(cpu)
        assert len(fraw) == n and len(film) == n and len(gpu) == n

        # Check 1: replay raw landmarks == film raw landmarks (CSV rounding).
        raw_diff = max(float(np.nanmax(np.abs(
            cpu[[f"{k}_r{a}" for a in "xyz"]].to_numpy()
            - fraw[[f"{k}_{a}" for a in "xyz"]].to_numpy()))) for k in NAMES)
        miss_diff = int(sum((cpu[f"{k}_rx"].isna() != fraw[f"{k}_x"].isna()).sum()
                            for k in NAMES))
        # Check 2: film derived angles reproduced by ChainFallbackSolver on
        # the film's filtered landmarks (convention check; twist may differ
        # where the film sets 0 and the live solver holds the last value).
        fl = {k: ffilt[[f"{k}_{a}" for a in "xyz"]].to_numpy(float) for k in NAMES}
        film_resolved, _ = solve_series(fl)
        conv = {a: float(np.nanmax(np.abs(wrap(film_resolved[:, c]
                                               - film[a].to_numpy()))))
                for a, c in ANGLE_COL.items()}
        # Stage series.
        raw = {k: cpu[[f"{k}_r{a}" for a in "xyz"]].to_numpy(float) for k in NAMES}
        filt = {k: cpu[[f"{k}_f{a}" for a in "xyz"]].to_numpy(float) for k in NAMES}
        desp = {k: np.where(np.isnan(filt[k]), np.nan, raw[k]) for k in NAMES}
        oe = {}
        for k in NAMES:   # live CausalLandmarkFilter One-Euro defaults: 30, 1.0, 1.0
            fs = [OneEuro(30.0, 1.0, 1.0) for _ in range(3)]
            oe[k] = np.array([[f(v) for f, v in zip(fs, r)] if np.all(np.isfinite(r))
                              else [np.nan] * 3 for r in raw[k]])
        a_oe, m_oe = solve_series(oe)
        a_raw, m_raw = solve_series(raw)
        a_desp, m_desp = solve_series(desp)
        a_live_re, _ = solve_series(filt)
        a_cpu = cpu[[f"a{i}" for i in range(13)]].to_numpy(float)
        a_gpu = gpu[[f"a{i}" for i in range(13)]].to_numpy(float)
        a_paced = paced[[f"a{i}" for i in range(13)]].to_numpy(float)
        # Check 3: recomputing the live angles from the logged filtered
        # landmarks reproduces the logged live angles (float32 round-trip).
        live_recompute = float(np.max(np.abs(wrap(a_live_re - a_cpu))))
        # Live dump (unmodified realtime_person.py): align by bag time.
        t_bag = cpu["time_s"].to_numpy()
        idx = np.searchsorted(t_bag, dump["time_s"].to_numpy() - 1e-3)
        idx = np.clip(idx, 0, n - 1)
        tol = np.abs(t_bag[idx] - dump["time_s"].to_numpy())
        dump_frames = idx[tol < 0.5 / 30]
        a_dump = np.full((n, 13), np.nan)
        a_dump[dump_frames] = dump[[f"a{i}" for i in range(13)]].to_numpy(float)[tol < 0.5 / 30]
        m_dump = np.zeros(n, int)
        m_dump[dump_frames] = dump["mask"].to_numpy()[tol < 0.5 / 30]
        checks[page] = {
            "replay_raw_vs_film_raw_max_abs_m": raw_diff,
            "replay_vs_film_missing_mismatch": miss_diff,
            "film_angles_resolved_by_live_solver_max_abs_deg_all_frames": conv,
            "live_angles_recomputed_from_logged_filtered_max_abs_deg": live_recompute,
            "dump_rows": int(len(dump)), "dump_rows_aligned": int(len(dump_frames)),
            "dump_duplicate_frames": int(len(dump_frames) - len(np.unique(dump_frames))),
            "bag_frames": int(n), "dropped_frames_paced_dump": int(n - len(np.unique(dump_frames))),
            "dump_vs_gpu_replay_max_abs_deg_right_arm": float(np.nanmax(np.abs(wrap(
                a_dump[:, 3:8] - a_gpu[:, 3:8])))),
            "paced_replay_vs_gpu_replay_max_abs_deg_right_arm": float(np.max(np.abs(wrap(
                a_paced[:, 3:8] - a_gpu[:, 3:8])))),
            "gpu_vs_cpu_raw_landmark_max_abs_m": max(float(np.nanmax(np.abs(
                gpu[[f"{k}_r{a}" for a in "xyz"]].to_numpy()
                - cpu[[f"{k}_r{a}" for a in "xyz"]].to_numpy()))) for k in RIGHT_CHAIN),
        }
        # Delivery timing of the paced replay (what the live loop sees).
        wall = paced["wall_s"].to_numpy()
        dw = np.diff(wall) * 1e3
        dt = np.diff(paced["time_s"].to_numpy()) * 1e3
        timing.append({"page": page, "frames_bag": n, "frames_paced": len(paced),
                       "bag_interval_ms_mean": float(np.mean(dt)),
                       "delivery_interval_ms_mean": float(np.mean(dw)),
                       "delivery_interval_ms_std": float(np.std(dw)),
                       "delivery_interval_ms_p05": float(np.percentile(dw, 5)),
                       "delivery_interval_ms_p95": float(np.percentile(dw, 95)),
                       "delivery_interval_ms_max": float(np.max(dw)),
                       "effective_fps": float((len(paced) - 1) / (wall[-1] - wall[0])),
                       "recorded_span_s": float(t_bag[-1] - t_bag[0]),
                       "delivered_span_s": float(wall[-1] - wall[0])})

        w = slice(s0, s1 + 1)
        frames = np.arange(n)[w]
        series_out = pd.DataFrame({"frame": frames, "time_s": t_bag[w]})
        # Rejection / gating counts inside the window, right chain.
        gated = {k: int(np.isnan(raw[k][w, 0]).sum()) for k in RIGHT_CHAIN}
        rejected = {k: int((np.isfinite(raw[k][w, 0]) & np.isnan(filt[k][w, 0])).sum())
                    for k in RIGHT_CHAIN}
        film_repaired = int((film.loc[s0:s1, "required_repaired_points"] > 0).sum())
        checks[page]["window"] = [s0, s1]
        checks[page]["window_gated_frames"] = gated
        checks[page]["window_causal_hampel_rejected_frames"] = rejected
        checks[page]["window_film_frames_with_repaired_points"] = film_repaired
        # Half-speed film mapping (provenance of the built film).
        prov = json.loads((DEF / f"committee_materials/unified_four/provenance/{cfg['stem']}.json"
                           ).read_text())
        mapping = np.asarray(prov["output_source_frames"])
        moving = mapping[60:len(mapping) - 60]   # 2 s holds at 30 fps excluded; PS-005
        for a in cfg["angles"]:
            c = ANGLE_COL[a]
            ser = {"film": film[a].to_numpy(float), "raw_gated": a_raw[:, c],
                   "despiked": a_desp[:, c], "live_cpu": a_cpu[:, c],
                   "live_gpu": a_gpu[:, c], "live_dump": a_dump[:, c],
                   "oneeuro_only": a_oe[:, c]}
            masks = {"raw_gated": m_raw, "despiked": m_desp, "live_cpu": cpu["mask"].to_numpy(),
                     "live_gpu": gpu["mask"].to_numpy(), "live_dump": m_dump,
                     "oneeuro_only": m_oe}
            ref = ser["film"][w]
            for name, x in ser.items():
                xw = x[w]
                series_out[f"{a}_{name}"] = xw
                row = {"page": page, "angle": a, "series": name,
                       "frames": int(np.isfinite(xw).sum())}
                row["delta_std_deg"], row["delta_mean_abs_deg"], row["d2_rms_deg"] = delta_stats(xw)
                if name != "film":
                    diff = wrap(xw - ref)
                    row["mean_abs_diff_vs_film_deg"] = float(np.nanmean(np.abs(diff)))
                    row["max_abs_diff_vs_film_deg"] = float(np.nanmax(np.abs(diff)))
                    lag, err = best_lag(xw, ref)
                    row["best_lag_frames"] = lag
                    row["mean_abs_diff_at_best_lag_deg"] = err
                    row["held_or_repaired_frames"] = int(((masks[name][w] & ANGLE_BIT[a]) == 0).sum())
                else:
                    row["held_or_repaired_frames"] = int((film.loc[s0:s1, "required_repaired_points"] > 0).sum())
                metrics.append(row)
            # Half speed: film value per screen frame vs per source frame.
            screen = film[a].to_numpy(float)[moving]
            ds = wrap(np.diff(screen))
            dsrc = wrap(np.diff(ref))
            halfspeed.append({"page": page, "angle": a,
                              "source_deg_per_source_frame_mean_abs": float(np.mean(np.abs(dsrc))),
                              "source_deg_per_source_frame_max_abs": float(np.max(np.abs(dsrc))),
                              "film_deg_per_screen_frame_mean_abs": float(np.mean(np.abs(ds))),
                              "film_deg_per_screen_frame_max_abs": float(np.max(np.abs(ds))),
                              "film_screen_frames_with_zero_change": int(np.sum(ds == 0)),
                              "film_screen_frames": int(len(ds)),
                              "source_deg_per_s_at_30fps_mean_abs": float(np.mean(np.abs(dsrc)) * 30),
                              "film_deg_per_s_on_screen_mean_abs": float(np.mean(np.abs(ds)) * 30),
                              "live_cpu_deg_per_frame_mean_abs": float(np.mean(np.abs(wrap(np.diff(a_cpu[w, c]))))),
                              "live_cpu_delta_std_deg": float(np.std(wrap(np.diff(a_cpu[w, c]))))})
            if a == "el_z":   # identically 0 by construction (v1/kinematics/shoulder.py): no plot
                continue
            # Plot: values on top, differences to the film below.
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True,
                                           gridspec_kw={"height_ratios": [2, 1]})
            for name, lw in (("raw_gated", 1.0), ("film", 2.0), ("live_cpu", 1.5)):
                ax1.plot(frames, ser[name][w], color=COLORS[name], lw=lw,
                         label={"film": "film (offline zero-phase filter)",
                                "live_cpu": "live path (causal Hampel + One-Euro)",
                                "raw_gated": "live path, raw gated landmarks (no filter)"}[name])
            ax1.set_ylabel(f"{a} (deg)")
            ax1.legend(loc="best", fontsize=8, frameon=False)
            ax1.set_title(f"Page {page}, {a}: film vs live path, source frames {s0}-{s1}")
            for name in ("raw_gated", "live_cpu"):
                ax2.plot(frames, wrap(ser[name][w] - ref), color=COLORS[name], lw=1.2,
                         label=f"{name} - film")
            ax2.axhline(0, color="#52514e", lw=0.8)
            ax2.set_ylabel("difference (deg)")
            ax2.set_xlabel("source frame (30 fps bag)")
            ax2.legend(loc="best", fontsize=8, frameon=False)
            for ax in (ax1, ax2):
                ax.grid(color="#e0dfdb", lw=0.5)
                for s in ("top", "right"):
                    ax.spines[s].set_visible(False)
            fig.tight_layout()
            fig.savefig(PLOTS / f"p{page}_{a}.png", dpi=110)
            plt.close(fig)
        series_out.to_csv(HERE / f"series_p{page}.csv", index=False, float_format="%.6f")

    pd.DataFrame(metrics).to_csv(HERE / "metrics.csv", index=False, float_format="%.4f")
    pd.DataFrame(timing).to_csv(HERE / "timing_paced.csv", index=False, float_format="%.3f")
    pd.DataFrame(halfspeed).to_csv(HERE / "half_speed.csv", index=False, float_format="%.4f")
    (HERE / "checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()

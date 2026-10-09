#!/usr/bin/env python3
# Filename: v2/integration/validate_v2.py
"""Validate the v2 stack on the pinned recording.

Part 1 re-runs v1's checks (validate_realtime.py, same thresholds) on
the v2 pipeline dumps: coverage, causal-vs-offline angle bounds, lag,
live fractions, pelvis/object agreement, compute budgets.

Part 2 checks what is NEW in v2 -- the delay-buffer merger:
  - steady output cadence (p99 close to the 33.3 ms tick)
  - declared delay honoured: person samples used as brackets are the
    newest available minus the delay, measured via tau vs sample stamps
  - state accounting: measured + interp + held + blend == ticks
  - interpolation honesty: every INTERP tick's output recomputes exactly
    from its bracket rows (wrap-aware lerp for the 13 joint parameters,
    position lerp + SO(3) geodesic for the object) -- no invented poses
  - object dropout handling: every live=0 run in the object dump is
    classified; short runs are bridged (BRIDGE flag), long runs are held
    with olive=0 and end in a BLEND ramp
  - PSI2 shm region well-formed

Inputs: v2/output/v2_person_dump.csv, v2_object_dump.csv,
v2_integrate_dump.csv from `python run_v2.py --source bag --dump`.
"""
import struct
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "v1/kinematics"))
sys.path.insert(0, str(ROOT / "v1/aruco"))

FRAME_S = 1.0 / 30.0
MEASURED, INTERP, HELD, BLEND = 0, 1, 2, 3
FAILURES = []


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}"
          + (f" -- {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def wrap(a):
    return (np.asarray(a) + 180.0) % 360.0 - 180.0


def main():
    out = ROOT / "v2/output"
    rt_p = pd.read_csv(out / "v2_person_dump.csv")
    rt_o = pd.read_csv(out / "v2_object_dump.csv")
    it = pd.read_csv(out / "v2_integrate_dump.csv")

    # ================= part 1: v1's checks on the v2 pipelines ========
    check("person dump covers the recording",
          len(rt_p) >= 890 and (np.diff(rt_p.frame) > 0).all(),
          f"{len(rt_p)} frames, strictly increasing")
    check("object dump covers the recording",
          len(rt_o) >= 890 and (np.diff(rt_o.frame) > 0).all(),
          f"{len(rt_o)} frames")

    from occlusion import ChainFallbackSolver, points_from_row
    from root_frame import unity_from_sensor
    lm = pd.read_csv(ROOT / "v1/mediapipe/output/"
                     "recording_20260224_083945_landmarks_filtered_v2.csv")
    solver = ChainFallbackSolver()
    ref_angles = np.full((len(lm), 13), np.nan)
    ref_pelvis = np.full((len(lm), 3), np.nan)
    for i, (_, row) in enumerate(lm.iterrows()):
        pts = {k: unity_from_sensor(v) for k, v in points_from_row(row).items()
               if np.all(np.isfinite(v))}
        ref_angles[i], _ = solver.solve(pts)
        if "left_hip" in pts and "right_hip" in pts:
            ref_pelvis[i] = 0.5 * (pts["left_hip"] + pts["right_hip"])

    n = min(len(rt_p), len(ref_angles))
    rt_a = rt_p[[f"a{i}" for i in range(13)]].to_numpy()[:n]
    d = np.abs(wrap(rt_a - ref_angles[:n]))
    W = 60
    groups = {"root xyz": range(0, 3), "R shoulder": range(3, 6),
              "R elbow": range(6, 8), "L shoulder": range(8, 11),
              "L elbow": range(11, 13)}
    print("\n  causal-vs-offline angle difference (deg, after warm-up):")
    med_all, p95_all = [], []
    for gname, idx in groups.items():
        g = d[W:, list(idx)]
        print(f"    {gname:11s} median {np.nanmedian(g):6.2f}  "
              f"p95 {np.nanpercentile(g, 95):6.2f}  "
              f"max {np.nanmax(g):7.2f}")
        med_all.append(np.nanmedian(g))
        p95_all.append(np.nanpercentile(g, 95))
    check("causal person angles track the offline solve",
          max(med_all) < 5.0 and max(p95_all) < 20.0,
          f"worst joint-group median {max(med_all):.2f} deg (<5), "
          f"p95 {max(p95_all):.2f} deg (<20)")

    sig_rt = rt_a[W:, 4]
    sig_ref = ref_angles[W:n, 4]
    lags = range(-15, 16)
    cors = [np.corrcoef(sig_rt[max(0, k):len(sig_ref) + min(0, k)],
                        sig_ref[max(0, -k):len(sig_ref) - max(0, k)])[0, 1]
            for k in lags]
    best = list(lags)[int(np.argmax(cors))]
    check("causal lag is a few frames", abs(best) <= 4,
          f"cross-correlation peak at {best} frames "
          f"({best * 33.3:.0f} ms, r={max(cors):.3f})")

    live_frac = (rt_p["mask"].to_numpy()[W:n] == 127).mean()
    check("person joints live after warm-up", live_frac > 0.95,
          f"{live_frac*100:.1f}% of frames all-13-joints live")

    pel = rt_p[["pel_x", "pel_y", "pel_z"]].to_numpy()[:n]
    dp = np.linalg.norm(pel[W:] - ref_pelvis[W:n], axis=1) * 1e3
    check("pelvis matches offline", np.nanmedian(dp) < 20,
          f"median {np.nanmedian(dp):.1f} mm, "
          f"p95 {np.nanpercentile(dp, 95):.1f} mm")

    ref_o = pd.read_csv(ROOT / "v1/aruco/output/"
                        "recording_20260224_083945_object_world_filtered.csv")
    m = min(len(rt_o), len(ref_o))
    live = rt_o.live.to_numpy()[:m].astype(bool)
    check("object live coverage close to offline detections",
          live.sum() >= 0.95 * ref_o.detected.sum(),
          f"rt live {live.sum()} vs offline detected "
          f"{int(ref_o.detected.sum())}")
    pos_rt = rt_o[["ux", "uy", "uz"]].to_numpy()[:m]
    pos_ref = ref_o[["unity_px", "unity_py", "unity_pz"]].to_numpy()[:m]
    sel = live & ref_o.detected.to_numpy()[:m].astype(bool)
    sel[:W] = False
    do = np.linalg.norm(pos_rt[sel] - pos_ref[sel], axis=1) * 1e3
    check("object position matches offline filter", np.median(do) < 20,
          f"median {np.median(do):.1f} mm, "
          f"p95 {np.percentile(do, 95):.1f} mm")

    for nm, df_ in (("person", rt_p), ("object", rt_o)):
        c = df_.compute_ms.to_numpy()
        check(f"{nm} per-frame compute fits the 30 fps budget",
              np.percentile(c, 99) < 33.3,
              f"p99 {np.percentile(c, 99):.1f} ms (budget 33.3)")

    # ================= part 2: the delay-buffer merger ================
    print()
    iv = np.diff(it.mono.to_numpy()) * 1e3
    check("steady output cadence", np.percentile(iv, 99) < 40.0,
          f"tick interval p50 {np.percentile(iv, 50):.2f} ms, "
          f"p99 {np.percentile(iv, 99):.2f} ms (nominal 33.33)")
    check("render time never regresses",
          bool((np.diff(it.tau.to_numpy()) >= 0).all()),
          f"{len(it)} ticks, tau monotonic")

    p_by_frame = {int(r.frame): r for r in rt_p.itertuples()}
    o_by_frame = {int(r.frame): r for r in rt_o.itertuples()}

    # declared delay: on ticks that interpolate the person, the future
    # bracket is the newest sample the output waits for -- its stamp
    # minus tau must stay under the declared delay (plus half a frame
    # of tick phase)
    delay_frames = int(sys.argv[sys.argv.index("--delay-frames") + 1]) \
        if "--delay-frames" in sys.argv else 2
    pi = it[it.p_state == INTERP]
    ahead = [p_by_frame[int(r.p_f1)].time_s - r.tau for r in pi.itertuples()
             if int(r.p_f1) in p_by_frame]
    ahead = np.asarray(ahead)
    check("declared delay honoured",
          np.percentile(ahead, 95) <= (delay_frames + 0.5) * FRAME_S
          and ahead.min() > 0,
          f"future-bracket lead over tau: p50 {np.median(ahead)*1e3:.1f} ms, "
          f"p95 {np.percentile(ahead, 95)*1e3:.1f} ms "
          f"(declared {delay_frames * 33.3:.0f} ms)")

    # state accounting
    for stream, col in (("person", "p_state"), ("object", "o_state")):
        states = it[col].to_numpy()
        total = sum((states == s).sum() for s in (MEASURED, INTERP, HELD,
                                                  BLEND))
        check(f"{stream} states partition the ticks", total == len(it),
              f"measured {(states == 0).sum()}  interp {(states == 1).sum()}"
              f"  held {(states == 2).sum()}  blend {(states == 3).sum()}"
              f"  of {len(it)}")

    # interpolation honesty: recompute every INTERP tick from brackets
    from root_frame import wrap_deg
    from filter_object_track import geodesic_interp
    from frames import euler_unity_zxy, recompose_zxy
    acols = [f"a{i}" for i in range(13)]
    worst_p = 0.0
    n_pi = 0
    for r in pi.itertuples():
        f0, f1 = int(r.p_f0), int(r.p_f1)
        if f0 not in p_by_frame or f1 not in p_by_frame:
            continue
        b0, b1 = p_by_frame[f0], p_by_frame[f1]
        s = (r.tau - b0.time_s) / (b1.time_s - b0.time_s)
        a0 = np.array([getattr(b0, c) for c in acols])
        a1 = np.array([getattr(b1, c) for c in acols])
        expect = wrap_deg(a0 + s * wrap_deg(a1 - a0))
        got = np.array([getattr(r, c) for c in acols])
        worst_p = max(worst_p, np.abs(wrap(got - expect)).max())
        n_pi += 1
    # thresholds allow for the f32 transport: the merger interpolates
    # PSR1/PSB2 packet values, the validator recomputes from f64 dumps
    check("person interpolation lies between its brackets",
          n_pi > 0 and worst_p < 5e-3,
          f"{n_pi} interp ticks recomputed, worst angle error "
          f"{worst_p:.2e} deg")

    oi = it[it.o_state == INTERP]
    worst_pos = 0.0
    worst_rot = 0.0
    n_oi = 0
    for r in oi.itertuples():
        f0, f1 = int(r.o_f0), int(r.o_f1)
        if f0 not in o_by_frame or f1 not in o_by_frame:
            continue
        b0, b1 = o_by_frame[f0], o_by_frame[f1]
        s = (r.tau - b0.time_s) / (b1.time_s - b0.time_s)
        p0 = np.array([b0.ux, b0.uy, b0.uz])
        p1 = np.array([b1.ux, b1.uy, b1.uz])
        expect_pos = (1 - s) * p0 + s * p1
        got_pos = np.array([r.ox, r.oy, r.oz])
        worst_pos = max(worst_pos, np.abs(got_pos - expect_pos).max())
        R = geodesic_interp(recompose_zxy([b0.ex, b0.ey, b0.ez]),
                            recompose_zxy([b1.ex, b1.ey, b1.ez]), s)
        expect_eul = euler_unity_zxy(R)
        got_eul = np.array([r.oex, r.oey, r.oez])
        worst_rot = max(worst_rot, np.abs(wrap(got_eul - expect_eul)).max())
        n_oi += 1
    check("object interpolation lies between its brackets",
          n_oi > 0 and worst_pos < 1e-5 and worst_rot < 5e-3,
          f"{n_oi} interp ticks recomputed, worst pos error "
          f"{worst_pos:.2e} m, worst rot error {worst_rot:.2e} deg")

    # object dropout handling: classify every live=0 run of the dump
    lv = rt_o.live.to_numpy().astype(bool)
    tso = rt_o.time_s.to_numpy()
    runs = []
    i = 0
    while i < len(lv):
        if not lv[i]:
            j = i
            while j < len(lv) and not lv[j]:
                j += 1
            runs.append((i, j - 1, j - i))
            i = j
        else:
            i += 1
    print(f"\n  object live=0 runs in the dump: "
          f"{[(a, b, l) for a, b, l in runs]}")
    bridged_short = True
    held_long = True
    long_run_ticks = 0
    for a, b, length in runs:
        t_lo = tso[a] - 1e-6
        t_hi = tso[min(b + 1, len(tso) - 1)] + 1e-6
        span = it[(it.tau > t_lo) & (it.tau < t_hi)]
        if a < W or b == len(lv) - 1:
            continue                        # causal warm-up / trailing edge
        if length <= 2:
            # bracket gap <= max_gap: crossed by flagged interpolation
            if not ((span.o_state == INTERP)
                    & (span["flags"].to_numpy() & 32 > 0)).any() \
                    and len(span) > 0:
                bridged_short = False
        else:
            # bracket gap beyond max_gap: held mid-gap, honestly dead
            held = span[span.o_state == HELD]
            long_run_ticks += len(held)
            if len(held) == 0 or not (held.olive == 0).all():
                held_long = False
    check("short object dropouts are bridged and flagged",
          bridged_short)
    check("long object occlusions are held with olive=0",
          held_long, f"{long_run_ticks} held ticks over long runs")
    n_blend = int((it.o_state == BLEND).sum())
    check("reacquisition after long occlusions blends",
          n_blend > 0, f"{n_blend} object blend ticks")

    psi = Path("/dev/shm/integrated_scene_v2")
    ok = psi.exists() and psi.stat().st_size == 112
    if ok:
        magic = struct.unpack_from("<I", psi.read_bytes(), 0)[0]
        ok = magic == 0x32495350
    check("PSI2 shm region well-formed", ok)

    print(f"\n{len(FAILURES)} failure(s)" if FAILURES else "\nALL PASS")
    sys.exit(1 if FAILURES else 0)


if __name__ == "__main__":
    main()

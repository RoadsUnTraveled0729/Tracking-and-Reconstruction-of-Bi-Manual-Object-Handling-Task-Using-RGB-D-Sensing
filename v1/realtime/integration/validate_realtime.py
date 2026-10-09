#!/usr/bin/env python3
# Filename: realtime/integration/validate_realtime.py
"""Validate the real-time pipeline against the offline reference.

Inputs: the --dump CSVs of a full run
(`python run_realtime.py --dump --profile`):
  realtime/output/rt_person_dump.csv    frame, time, pelvis, 13 angles,
                                        mask, compute_ms
  realtime/output/rt_object_dump.csv    frame, time, live, unity pos/euler,
                                        compute_ms

Reference: the OFFLINE solves on the same bag — Pipeline A's
ChainFallbackSolver over the zero-phase-filtered landmark CSV (exactly what
send_integrated_scene.py streams) and Pipeline B's filtered object world
CSV. The real-time path may differ ONLY by what causality costs: the
One-Euro lag (a frame or two) and bounded amplitude differences — plus the
warm-up stretch, where the causal filter has no history. Checks assert
those bounds; per-joint stats are printed so the causal cost is quantified,
not hand-waved (REALTIME.md quotes them).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                 # repo root
sys.path.insert(0, str(ROOT / "kinematics"))

FAILURES = []


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def wrap(a):
    return (np.asarray(a) + 180.0) % 360.0 - 180.0


def main():
    rt_p = pd.read_csv(HERE.parent / "output/rt_person_dump.csv")
    rt_o = pd.read_csv(HERE.parent / "output/rt_object_dump.csv")

    # ---- structural
    check("person dump covers the recording",
          len(rt_p) >= 890 and (np.diff(rt_p.frame) > 0).all(),
          f"{len(rt_p)} frames, strictly increasing")
    check("object dump covers the recording",
          len(rt_o) >= 890 and (np.diff(rt_o.frame) > 0).all(),
          f"{len(rt_o)} frames")

    # ---- offline person reference: same solver, zero-phase-filtered CSV
    from occlusion import ChainFallbackSolver, points_from_row
    from root_frame import unity_from_sensor
    lm = pd.read_csv(ROOT / "mediapipe/output/"
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
    # skip the causal warm-up (filter history + MediaPipe warm-up)
    W = 60
    groups = {"root xyz": range(0, 3), "R shoulder": range(3, 6),
              "R elbow": range(6, 8), "L shoulder": range(8, 11),
              "L elbow": range(11, 13)}
    print("\n  causal-vs-offline angle difference (deg, after warm-up):")
    med_all, p95_all = [], []
    for gname, idx in groups.items():
        g = d[W:, list(idx)]
        med, p95, mx = (np.nanmedian(g), np.nanpercentile(g, 95),
                        np.nanmax(g))
        med_all.append(med)
        p95_all.append(p95)
        print(f"    {gname:11s} median {med:6.2f}  p95 {p95:6.2f}  max {mx:7.2f}")
    check("causal person angles track the offline solve",
          max(med_all) < 5.0 and max(p95_all) < 20.0,
          f"worst joint-group median {max(med_all):.2f} deg (<5), "
          f"p95 {max(p95_all):.2f} deg (<20)")

    # lag estimate by cross-correlation on a moving angle (R shoulder θz)
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
          f"median {np.nanmedian(dp):.1f} mm, p95 {np.nanpercentile(dp, 95):.1f} mm")

    # ---- object vs offline filtered world CSV
    ref_o = pd.read_csv(ROOT / "aruco/output/"
                        "recording_20260224_083945_object_world_filtered.csv")
    m = min(len(rt_o), len(ref_o))
    live = rt_o.live.to_numpy()[:m].astype(bool)
    check("object live coverage close to offline detections",
          live.sum() >= 0.95 * ref_o.detected.sum(),
          f"rt live {live.sum()} vs offline detected {int(ref_o.detected.sum())}")
    pos_rt = rt_o[["ux", "uy", "uz"]].to_numpy()[:m]
    pos_ref = ref_o[["unity_px", "unity_py", "unity_pz"]].to_numpy()[:m]
    sel = live & ref_o.detected.to_numpy()[:m].astype(bool)
    sel[:W] = False
    do = np.linalg.norm(pos_rt[sel] - pos_ref[sel], axis=1) * 1e3
    check("object position matches offline filter", np.median(do) < 20,
          f"median {np.median(do):.1f} mm, p95 {np.percentile(do, 95):.1f} mm "
          f"(causal vs zero-phase smoothing)")

    # ---- real-time budgets
    for nm, df_ in (("person", rt_p), ("object", rt_o)):
        c = df_.compute_ms.to_numpy()
        check(f"{nm} per-frame compute fits the 30 fps budget",
              np.percentile(c, 99) < 33.3,
              f"p99 {np.percentile(c, 99):.1f} ms (budget 33.3)")

    # ---- PSI1 region left by the merger
    psi = Path("/dev/shm/integrated_scene")
    ok = psi.exists() and psi.stat().st_size == 108
    if ok:
        import struct
        magic = struct.unpack_from("<I", psi.read_bytes(), 0)[0]
        ok = magic == 0x31495350
    check("PSI1 shm region well-formed", ok)

    print(f"\n{'ALL PASS' if not FAILURES else 'FAILURES: ' + str(FAILURES)}"
          f" ({14 - len(FAILURES)} checks)" if False else
          f"\n{len(FAILURES)} failure(s)" if FAILURES else "\nALL PASS")
    sys.exit(1 if FAILURES else 0)


if __name__ == "__main__":
    main()

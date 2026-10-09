"""Part-1 v2 validation re-referenced to the recording actually played.

v2/integration/validate_v2.py part 1 compares the v2 dumps against
offline references hardcoded to the pinned R1 stems, and its
"person joints live" check assumes a subject who never leaves the
frame. On R4 those comparisons are spurious. This validator reruns the
part-1 checks (same thresholds, same math, ported from
v2/integration/validate_v2.py:53-144 on 2026-08-25) with:

- offline references taken from the stem given on the CLI;
- person-liveness graded per joint group against the OFFLINE solve's
  own availability (the causal pipeline should keep a group live
  roughly wherever the offline solve could), instead of demanding
  all-13-live on frames where the subject is out of scene or an arm
  is genuinely occluded.

Part 2 of validate_v2.py (merger checks) is recording-independent and
its verdict comes from running the original script unchanged.

Usage:
    python eval/validate/validate_v2_r4.py [--stem STEM]
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
import paths

sys.path.insert(0, str(paths.REPO / "v1/kinematics"))
from occlusion import ChainFallbackSolver, points_from_row  # noqa: E402
from root_frame import unity_from_sensor  # noqa: E402

FAILURES = []
W = 60  # warm-up frames, as in validate_v2.py


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}"
          + (f" -- {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def wrap(a):
    return (np.asarray(a) + 180.0) % 360.0 - 180.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R4_STEM)
    ap.add_argument("--person-dump",
                    default=str(paths.REPO / "v2/output/v2_person_dump.csv"),
                    help="also accepts v1 realtime rt_person_dump.csv "
                         "(same column contract)")
    ap.add_argument("--object-dump",
                    default=str(paths.REPO / "v2/output/v2_object_dump.csv"))
    args = ap.parse_args()
    stem = args.stem

    rt_p = pd.read_csv(args.person_dump)
    rt_o = pd.read_csv(args.object_dump)

    lm = pd.read_csv(paths.MP_OUT / f"{stem}_landmarks_filtered.csv")
    ref_o = pd.read_csv(paths.ARUCO_OUT / f"{stem}_object_world_filtered.csv")

    check("person dump covers the recording",
          len(rt_p) == len(lm) and (np.diff(rt_p.frame) > 0).all(),
          f"{len(rt_p)} frames vs offline {len(lm)}, strictly increasing")
    check("object dump covers the recording",
          len(rt_o) == len(ref_o) and (np.diff(rt_o.frame) > 0).all(),
          f"{len(rt_o)} frames vs offline {len(ref_o)}")

    solver = ChainFallbackSolver()
    ref_angles = np.full((len(lm), 13), np.nan)
    ref_mask = np.zeros(len(lm), dtype=int)
    ref_pelvis = np.full((len(lm), 3), np.nan)
    for i, (_, row) in enumerate(lm.iterrows()):
        pts = {k: unity_from_sensor(v) for k, v in points_from_row(row).items()
               if np.all(np.isfinite(v))}
        ref_angles[i], ref_mask[i] = solver.solve(pts)
        if "left_hip" in pts and "right_hip" in pts:
            ref_pelvis[i] = 0.5 * (pts["left_hip"] + pts["right_hip"])

    n = min(len(rt_p), len(ref_angles))
    rt_a = rt_p[[f"a{i}" for i in range(13)]].to_numpy()[:n]
    rt_mask = rt_p["mask"].to_numpy()[:n].astype(int)

    # Angle agreement graded only where BOTH sides solved the group
    # from live data; held values are compared by the liveness check.
    groups = {"root xyz": (1, range(0, 3)),
              "R shoulder": (2 | 4, range(3, 6)),
              "R elbow": (8, range(6, 8)),
              "L shoulder": (16 | 32, range(8, 11)),
              "L elbow": (64, range(11, 13))}
    d = np.abs(wrap(rt_a - ref_angles[:n]))
    print("\n  causal-vs-offline angle difference "
          "(deg, after warm-up, both-live frames only):")
    med_all, p95_all = [], []
    for gname, (bits, idx) in groups.items():
        both = ((rt_mask & bits) == bits) & ((ref_mask[:n] & bits) == bits)
        both[:W] = False
        g = d[both][:, list(idx)]
        if g.size == 0:
            print(f"    {gname:11s} no both-live frames")
            continue
        med, p95 = np.nanmedian(g), np.nanpercentile(g, 95)
        print(f"    {gname:11s} median {med:6.2f}  p95 {p95:6.2f}  "
              f"max {np.nanmax(g):7.2f}  ({int(both.sum())} frames)")
        med_all.append(med)
        p95_all.append(p95)
    check("causal person angles track the offline solve",
          max(med_all) < 5.0 and max(p95_all) < 20.0,
          f"worst joint-group median {max(med_all):.2f} deg (<5), "
          f"p95 {max(p95_all):.2f} deg (<20)")

    sig_rt = rt_a[W:, 4]
    sig_ref = ref_angles[W:n, 4]
    ok = np.isfinite(sig_rt) & np.isfinite(sig_ref)
    sig_rt, sig_ref = sig_rt[ok], sig_ref[ok]
    lags = range(-15, 16)
    cors = [np.corrcoef(sig_rt[max(0, k):len(sig_ref) + min(0, k)],
                        sig_ref[max(0, -k):len(sig_ref) - max(0, k)])[0, 1]
            for k in lags]
    best = list(lags)[int(np.argmax(cors))]
    check("causal lag is a few frames", abs(best) <= 4,
          f"cross-correlation peak at {best} frames "
          f"({best * 33.3:.0f} ms, r={max(cors):.3f})")

    print("\n  per-group live fraction, causal vs offline (after warm-up):")
    fracs_ok = True
    for gname, (bits, _) in groups.items():
        rt_live = ((rt_mask[W:] & bits) == bits).mean()
        ref_live = ((ref_mask[W:n] & bits) == bits).mean()
        print(f"    {gname:11s} rt {rt_live*100:5.1f}%  "
              f"offline {ref_live*100:5.1f}%")
        if rt_live < 0.9 * ref_live:
            fracs_ok = False
    check("causal liveness tracks offline availability per group "
          "(rt >= 90% of offline)", fracs_ok)

    pel = rt_p[["pel_x", "pel_y", "pel_z"]].to_numpy()[:n]
    dp = np.linalg.norm(pel[W:] - ref_pelvis[W:n], axis=1) * 1e3
    check("pelvis matches offline", np.nanmedian(dp) < 20,
          f"median {np.nanmedian(dp):.1f} mm, "
          f"p95 {np.nanpercentile(dp, 95):.1f} mm")

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

    print(f"\n=== {'ALL PASS' if not FAILURES else 'FAILED'}: "
          f"{9 - len(FAILURES)}/9 part-1 checks ===")
    sys.exit(0 if not FAILURES else 1)


if __name__ == "__main__":
    main()

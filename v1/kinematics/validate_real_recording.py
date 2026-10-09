"""Validate the root + right-arm solve on a REAL recording (no ground truth).

Without injected truth, correctness on real data means:
  1. Root frame invariants hold on every frame: det(R) = +1, orthonormal,
     Euler decode->recompose round-trips.
  2. The solve is an exact inverse: the 4 solved angles (shoulder θy, θz,
     θτ + elbow ey) must RECONSTRUCT both measured segment directions
       â_rec = Ry(θy)·Rz(θz)·x̂            (upper arm, torso frame)
       f̂_rec = Ry·Rz·Rx(θτ)·Ry(ey)·Rz(ez)·x̂   (forearm)
     to machine precision - i.e. the model fully explains the observed
     geometry frame by frame.
  3. Physical plausibility: elbow ey stays in [-180, 0], angles are
     continuous (jumps bounded by sensor jitter), twist flagged
     unobservable only when the elbow is actually near-straight.

Run: python validate_real_recording.py <landmark_csv>
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from root_frame import build_root_frame, euler_unity_zxy, recompose_zxy, \
    unity_from_sensor, wrap_deg, normalize
from shoulder import solve_left_arm, solve_right_arm, _rx, _ry, _rz

X = np.array([1.0, 0.0, 0.0])
LANDMARKS = ("left_hip", "right_hip", "right_shoulder", "right_elbow",
             "right_wrist", "left_shoulder", "left_elbow", "left_wrist")


def main():
    csv = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if csv is None:
        sys.exit("usage: validate_real_recording.py <landmark_csv>")
    df = pd.read_csv(csv)
    n0 = len(df)

    # Per-joint availability (§10 chain requirements) over ALL frames —
    # the chain-fallback solver keeps these joints live; the rest hold.
    have = {k: df[[f"{k}_{c}" for c in "xyz"]].notna().all(axis=1)
            & (df["has_pose"] == 1) for k in LANDMARKS}
    joint_live = {
        "root": have["left_hip"] & have["right_hip"]
                & (have["right_shoulder"] | have["left_shoulder"]),
        "R swing": have["right_shoulder"] & have["right_elbow"],
        "R twist+elbow": have["right_shoulder"] & have["right_elbow"]
                         & have["right_wrist"],
        "L swing": have["left_shoulder"] & have["left_elbow"],
        "L twist+elbow": have["left_shoulder"] & have["left_elbow"]
                         & have["left_wrist"],
    }
    print(f"{csv.name}: per-joint availability over {n0} frames "
          f"(blocked landmarks cost only their own joints):")
    for name, live in joint_live.items():
        n = int(live.sum())
        print(f"  {name:14s} live {n}/{n0} ({100 * n / n0:.1f}%), "
              f"held {n0 - n}")

    df = df[df["has_pose"] == 1].dropna(
        subset=[f"{k}_{c}" for k in LANDMARKS for c in "xyz"])
    print(f"frames with ALL landmarks (used for the exact-inverse checks "
          f"below): {len(df)}/{n0}")

    dets, orth, rt = [], [], []
    rec_ua, rec_fa, rec_lua, rec_lfa = [], [], [], []
    roots, shs, els, flags = [], [], [], []
    lshs, lels, lflags = [], [], []
    for _, row in df.iterrows():
        p = {k: unity_from_sensor([row[f"{k}_x"], row[f"{k}_y"], row[f"{k}_z"]])
             for k in LANDMARKS}
        R = build_root_frame(p["left_hip"], p["right_hip"], p["right_shoulder"])
        dets.append(np.linalg.det(R))
        orth.append(np.max(np.abs(R.T @ R - np.eye(3))))
        e = euler_unity_zxy(R)
        rt.append(np.max(np.abs(recompose_zxy(e) - R)))
        roots.append(e)

        sh, el, ok = solve_right_arm(p["right_shoulder"], p["right_elbow"],
                                     p["right_wrist"], R)
        shs.append(sh)
        els.append(el)
        flags.append(ok)

        y, z, t = np.radians(sh)
        ey, ez = np.radians(el)
        a_rec = R @ (_ry(y) @ _rz(z) @ X)
        f_rec = R @ (_ry(y) @ _rz(z) @ _rx(t) @ (_ry(ey) @ _rz(ez) @ X))
        a_meas = normalize(p["right_elbow"] - p["right_shoulder"])
        f_meas = normalize(p["right_wrist"] - p["right_elbow"])
        # atan2(|cross|, dot) is well-conditioned near 0 (arccos is not)
        rec_ua.append(np.degrees(np.arctan2(
            np.linalg.norm(np.cross(a_rec, a_meas)), a_rec @ a_meas)))
        rec_fa.append(np.degrees(np.arctan2(
            np.linalg.norm(np.cross(f_rec, f_meas)), f_rec @ f_meas)))

        # LEFT arm (§9): reconstruction chain Ry(-θy)·Rz(-θz)·Rx(θτ)·Ry(-ey),
        # rest -x̂
        lsh, lel, lok = solve_left_arm(p["left_shoulder"], p["left_elbow"],
                                       p["left_wrist"], R)
        lshs.append(lsh)
        lels.append(lel)
        lflags.append(lok)
        ly, lz, lt = np.radians(lsh)
        ley = np.radians(lel[0])
        la_rec = R @ (_ry(-ly) @ _rz(-lz) @ -X)
        lf_rec = R @ (_ry(-ly) @ _rz(-lz) @ _rx(lt) @ (_ry(-ley) @ -X))
        la_meas = normalize(p["left_elbow"] - p["left_shoulder"])
        lf_meas = normalize(p["left_wrist"] - p["left_elbow"])
        rec_lua.append(np.degrees(np.arctan2(
            np.linalg.norm(np.cross(la_rec, la_meas)), la_rec @ la_meas)))
        rec_lfa.append(np.degrees(np.arctan2(
            np.linalg.norm(np.cross(lf_rec, lf_meas)), lf_rec @ lf_meas)))

    roots, shs, els = np.array(roots), np.array(shs), np.array(els)
    lshs, lels = np.array(lshs), np.array(lels)
    flags = np.array(flags)
    ok_all = True

    def report(label, val, tol):
        nonlocal ok_all
        good = val <= tol
        ok_all &= good
        print(f"  [{'PASS' if good else 'FAIL'}] {label}: {val:.3e}")

    print("\n1. Root-frame invariants (worst frame):")
    report("max |det(R) - 1|", np.max(np.abs(np.array(dets) - 1)), 1e-12)
    report("max |R^T R - I|", np.max(orth), 1e-12)
    report("max Euler round-trip", np.max(rt), 1e-12)

    print("\n2. Solve reconstructs measured directions (worst frame, deg):")
    report("R upper-arm reconstruction angle", np.max(rec_ua), 1e-6)
    report("R forearm reconstruction angle", np.max(rec_fa), 1e-6)
    report("L upper-arm reconstruction angle", np.max(rec_lua), 1e-6)
    report("L forearm reconstruction angle", np.max(rec_lfa), 1e-6)

    print("\n3. Plausibility:")
    ey = els[:, 0]
    in_range = (ey <= 1e-9) & (ey >= -180.0)
    print(f"  [{'PASS' if in_range.all() else 'FAIL'}] elbow ey in [-180, 0] "
          f"on all frames (range {ey.min():.1f} .. {ey.max():.1f})")
    ok_all &= in_range.all()
    print(f"  twist unobservable (near-straight elbow) on "
          f"{np.count_nonzero(~flags)}/{len(flags)} frames; "
          f"|ey| on those frames max "
          f"{np.max(np.abs(ey[~flags])) if (~flags).any() else 0:.2f} deg")
    ley = lels[:, 0]
    l_in = (ley <= 1e-9) & (ley >= -180.0)
    print(f"  [{'PASS' if l_in.all() else 'FAIL'}] LEFT elbow ey in [-180, 0] "
          f"on all frames (range {ley.min():.1f} .. {ley.max():.1f})")
    ok_all &= l_in.all()
    for name, arr in (("root", roots), ("R shoulder", shs), ("R elbow", els),
                      ("L shoulder", lshs), ("L elbow", lels)):
        jump = np.max(np.abs(wrap_deg(np.diff(arr[flags] if name != 'root'
                                              else arr, axis=0))), axis=0)
        print(f"  {name} mean {np.round(arr.mean(axis=0), 1)}, "
              f"std {np.round(arr.std(axis=0), 1)}, "
              f"max frame-to-frame jump {np.round(jump, 1)} deg")

    print(f"\n{'ALL PASS' if ok_all else 'FAILURES PRESENT'}")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()

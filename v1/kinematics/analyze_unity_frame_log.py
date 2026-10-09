"""Quantify the Unity-side mapping error per frame.

Input: unity_frame_log.csv from ArmAngleLogger (measured world segment
directions for every stream frame the rig actually displayed, plus the
authored rest directions), and the landmark CSV that was streamed.

For each logged frame the expected directions are predicted INDEPENDENTLY
from the solved angles (KINEMATIC_MODEL.md §6-9):

  pred = R_root · chain(angles) · chain_ref⁻¹ · rest_dir

with chain_ref the reference chain at the character's rest (root (0,180,0)
after the y-180 anchor cancellation -> identity here because rest_dir was
captured at authored rest, so chain_ref = I) — i.e. pred = R_root · chain
· rest_dir expressed with rest_dir in the character's authored frame.

Reported: per-segment angular error stats over all frames, count of frames
above thresholds, and frame coverage (received vs sent).

Run: python analyze_unity_frame_log.py <unity_frame_log.csv> <landmark_csv>
"""
import sys

import numpy as np
import pandas as pd

from send_arm_angles import compute_angles
from shoulder import _rx, _ry, _rz
from root_frame import recompose_zxy

X = np.array([1.0, 0.0, 0.0])


def ang_err(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    return np.degrees(np.arctan2(np.linalg.norm(np.cross(a, b)), a @ b))


def main():
    log_path, csv_path = sys.argv[1], sys.argv[2]
    with open(log_path) as f:
        rest_line = f.readline()
    rest = np.array([float(v) for v in rest_line.split(",")[1:]]).reshape(4, 3)
    rest_rua, rest_rfa, rest_lua, rest_lfa = rest
    log = pd.read_csv(log_path, skiprows=1)

    angles = {r[0]: r for r in compute_angles(csv_path)}
    n_sent = len(angles)

    errs = {k: [] for k in ("R upper arm", "R forearm", "L upper arm", "L forearm")}
    for _, row in log.iterrows():
        rec = angles.get(int(row["frame"]))
        if rec is None:
            continue
        (_, _, rx_, ry_, rz_, sy, sz, st, ey, ez,
         ly, lz, lt, ley, lez, _mask) = rec
        R_root = recompose_zxy((rx_, ry_, rz_))
        # rest_dir = C·v_bone (captured at authored rest, no packet), and
        # the receiver sets bone.rotation = qRoot·chain·C, so
        # pred = R_root · chain · rest_dir with no reference terms.
        shR = _ry(np.radians(sy)) @ _rz(np.radians(sz)) @ _rx(np.radians(st))
        elR = _ry(np.radians(ey)) @ _rz(np.radians(ez))
        d_rua = R_root @ shR
        d_rfa = R_root @ shR @ elR
        shL = _ry(np.radians(-ly)) @ _rz(np.radians(-lz)) @ _rx(np.radians(lt))
        elL = _ry(np.radians(-ley)) @ _rz(np.radians(-lez))
        d_lua = R_root @ shL
        d_lfa = R_root @ shL @ elL

        meas = {"R upper arm": row[["rua_x", "rua_y", "rua_z"]].to_numpy(float),
                "R forearm":  row[["rfa_x", "rfa_y", "rfa_z"]].to_numpy(float),
                "L upper arm": row[["lua_x", "lua_y", "lua_z"]].to_numpy(float),
                "L forearm":  row[["lfa_x", "lfa_y", "lfa_z"]].to_numpy(float)}
        pred = {"R upper arm": d_rua @ rest_rua,
                "R forearm":  d_rfa @ rest_rfa,
                "L upper arm": d_lua @ rest_lua,
                "L forearm":  d_lfa @ rest_lfa}
        for k in errs:
            errs[k].append(ang_err(meas[k], pred[k]))

    got = sorted(set(int(f) for f in log["frame"]))
    missing = sorted(set(angles) - set(got))
    invalid = sorted(set(got) - set(angles))
    print(f"frames sent: {n_sent}, displayed & logged: {len(got)}, "
          f"missed: {len(missing)}"
          + (f" (ids {missing[:10]}{'...' if len(missing) > 10 else ''})"
             if missing else "")
          + (f"; logged-but-invalid-input: {invalid}" if invalid else ""))
    print(f"\nper-frame angular error, rig vs solved angles (deg):")
    print(f"{'segment':<14} {'mean':>8} {'median':>8} {'p99':>8} {'max':>8} "
          f"{'>0.1 deg':>9} {'>1 deg':>7}")
    worst = 0.0
    for k, v in errs.items():
        v = np.array(v)
        worst = max(worst, v.max())
        print(f"{k:<14} {v.mean():8.4f} {np.median(v):8.4f} "
              f"{np.percentile(v, 99):8.4f} {v.max():8.4f} "
              f"{np.count_nonzero(v > 0.1):9d} {np.count_nonzero(v > 1):7d}")
    ok = worst < 0.1
    print(f"\n{'PASS' if ok else 'CHECK'}: worst frame {worst:.4f} deg "
          f"(float32 packet + quaternion pipeline; <0.1 deg expected)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

"""Vectorized (batched) kinematic solve — real-time phase.

Batched re-implementation of the full per-frame chain (root frame + both
arms) operating on (N, 3) landmark arrays instead of one frame at a time.
The scalar solvers in shoulder.py / root_frame.py remain the validated
reference and are NOT modified; this module must decode identically
(selftest gate: max |Δangle| ≤ 1e-10 deg on every dataset and recording,
NaN/observability patterns matching exactly).

Math is unchanged (KINEMATIC_MODEL.md §3-§9); only the evaluation is
batched: elementary rotations are built as (N, 3, 3) stacks and applied
with einsum. Matrix application order mirrors the scalar code exactly so
floating-point rounding stays bit-comparable.

Entry points:
  build_root_frame_vec(p23, p24, p12)          -> (N,3,3)
  solve_right_arm_vec(p12, p14, p16, R_root)   -> sh(N,3), elb(N,2), ok(N)
  solve_left_arm_vec(p11, p13, p15, R_root)    -> sh(N,3), elb(N,2), ok(N)
  solve_all_vec(P)  dict of (N,3) -> angles(N,13), twist_ok pair
  python shoulder_vec.py --selftest            equivalence vs scalar
"""
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[2]    # repo root (realtime/bench/)
sys.path.insert(0, str(_ROOT / "kinematics"))

from root_frame import normalize
from shoulder import GIMBAL_EPS, TWIST_EPS, MIRROR


# ---------------------------------------------------------------- batched
# elementary rotation stacks: angle array (N,) -> (N, 3, 3)

def _rx_v(rad):
    c, s = np.cos(rad), np.sin(rad)
    o, z = np.ones_like(c), np.zeros_like(c)
    return np.stack([
        np.stack([o, z, z], -1),
        np.stack([z, c, -s], -1),
        np.stack([z, s, c], -1),
    ], -2)


def _ry_v(rad):
    c, s = np.cos(rad), np.sin(rad)
    o, z = np.ones_like(c), np.zeros_like(c)
    return np.stack([
        np.stack([c, z, s], -1),
        np.stack([z, o, z], -1),
        np.stack([-s, z, c], -1),
    ], -2)


def _rz_v(rad):
    c, s = np.cos(rad), np.sin(rad)
    o, z = np.ones_like(c), np.zeros_like(c)
    return np.stack([
        np.stack([c, -s, z], -1),
        np.stack([s, c, z], -1),
        np.stack([z, z, o], -1),
    ], -2)


def _mv(R, v):
    """Batched matrix @ vector: (N,3,3) @ (N,3) -> (N,3)."""
    return np.einsum("nij,nj->ni", R, v)


def _mtv(R, v):
    """Batched matrix.T @ vector."""
    return np.einsum("nji,nj->ni", R, v)


def _mm(A, B):
    """Batched matrix @ matrix."""
    return np.einsum("nij,njk->nik", A, B)


# ---------------------------------------------------------------- solves

def build_root_frame_vec(p23, p24, p12):
    """Batched L24 root frame; identical math to root_frame.build_root_frame
    (which already broadcasts — thin alias kept for the module's API)."""
    r = normalize(p24 - p23)
    s = p12 - p24
    f = normalize(np.cross(r, s))
    u = np.cross(f, r)
    return np.stack([r, u, f], axis=-1)


def solve_right_arm_vec(p12, p14, p16, R_root):
    """Batched right-arm solve, mirroring shoulder.solve_right_arm.

    Inputs (N,3) landmark positions (Unity space) and (N,3,3) root frames.
    Returns (shoulder_deg (N,3), elbow_deg (N,2), twist_ok (N,) bool);
    shoulder twist is 0 where unobservable (straight elbow, θτ := 0),
    exactly the scalar solve_right_arm convention — twist_ok carries the
    observability flag.
    """
    p12, p14, p16 = (np.asarray(p, float) for p in (p12, p14, p16))
    R_root = np.asarray(R_root, float)

    # swing from the upper-arm direction in the torso basis
    a = normalize(_mtv(R_root, p14 - p12))
    sz = np.clip(a[:, 1], -1.0, 1.0)
    th_z = np.arcsin(sz)
    gimbal = 1.0 - np.abs(sz) < GIMBAL_EPS
    th_y = np.where(gimbal, 0.0, np.arctan2(-a[:, 2], a[:, 0]))

    # twist: un-swing the forearm, read the angle in the y-z plane
    f = _mtv(R_root, p16 - p14)
    fp = _mv(_rz_v(-th_z), _mv(_ry_v(-th_y), f))
    perp = np.hypot(fp[:, 1], fp[:, 2])
    twist_ok = perp >= TWIST_EPS * np.linalg.norm(f, axis=-1)
    with np.errstate(invalid="ignore"):
        th_t = np.where(twist_ok, np.arctan2(-fp[:, 1], fp[:, 2]), np.nan)

    # elbow in the fully-rotated arm frame; θτ := 0 where unobservable —
    # the scalar solve_right_arm applies the same convention to the
    # RETURNED shoulder twist (not just internally), so mirror that.
    t_eff = np.where(twist_ok, th_t, 0.0)
    chain = _mm(_mm(_ry_v(th_y), _rz_v(th_z)), _rx_v(t_eff))
    R_arm = _mm(R_root, chain)
    g = normalize(_mtv(R_arm, p16 - p14))
    ez = np.arcsin(np.clip(g[:, 1], -1.0, 1.0))
    ey = np.arctan2(-g[:, 2], g[:, 0])

    sh = np.degrees(np.stack([th_y, th_z, t_eff], -1))
    elb = np.degrees(np.stack([ey, ez], -1))
    return sh, elb, twist_ok


def solve_left_arm_vec(p11, p13, p15, R_root):
    """Batched left arm: sagittal mirror into the identical right solve."""
    p11, p13, p15 = (np.asarray(p, float) for p in (p11, p13, p15))
    R_root = np.asarray(R_root, float)
    u = MIRROR * _mtv(R_root, p13 - p11)
    f = MIRROR * _mtv(R_root, p15 - p13)
    zero = np.zeros_like(u)
    eye = np.broadcast_to(np.eye(3), R_root.shape)
    return solve_right_arm_vec(zero, u, u + f, eye)


def solve_all_vec(p23, p24, p11, p12, p13, p14, p15, p16):
    """Full 13-angle batch solve on fully valid frames (no fallback logic —
    occlusion handling stays in ChainFallbackSolver; this is the fast path
    for offline batches and the benchmark).

    Returns angles (N,13) in PSA packet order
    (root xyz | R sh | R elb | L sh | L elb) and the two twist_ok arrays.
    """
    from root_frame import euler_unity_zxy
    R_root = build_root_frame_vec(p23, p24, p12)
    root = euler_unity_zxy(R_root)
    rsh, relb, rok = solve_right_arm_vec(p12, p14, p16, R_root)
    lsh, lelb, lok = solve_left_arm_vec(p11, p13, p15, R_root)
    return np.concatenate([root, rsh, relb, lsh, lelb], axis=-1), rok, lok


# ---------------------------------------------------------------- selftest

def _selftest():
    import sys
    from pathlib import Path

    import pandas as pd

    from root_frame import build_root_frame, unity_from_sensor
    from shoulder import solve_left_arm, solve_right_arm

    names = ("left_hip", "right_hip", "left_shoulder", "right_shoulder",
             "left_elbow", "right_elbow", "left_wrist", "right_wrist")
    sources = sorted((_ROOT / "kinematics").glob("dataset/*_landmarks.csv")) + [
        _ROOT / "mediapipe/output" /
        f"recording_{stem}_landmarks_{kind}.csv"
        for stem in ("20260224_083945", "20260225_230607", "20260328_021733")
        for kind in ("raw" + ("_v2" if stem == "20260224_083945" else ""),
                     "filtered" + ("_v2" if stem == "20260224_083945" else ""))
    ]

    worst = 0.0
    total = 0
    for src in sources:
        if not Path(src).exists():
            print(f"  [skip] {src}")
            continue
        df = pd.read_csv(src)
        P = {}
        valid = np.ones(len(df), bool)
        for n in names:
            xyz = df[[f"{n}_x", f"{n}_y", f"{n}_z"]].to_numpy(float)
            P[n] = unity_from_sensor(xyz)
            valid &= np.isfinite(xyz).all(axis=1)
        idx = np.flatnonzero(valid)
        if not len(idx):
            print(f"  [skip] {Path(src).name}: no fully valid frames")
            continue
        S = {n: P[n][idx] for n in names}

        ang_v, rok_v, lok_v = solve_all_vec(
            S["left_hip"], S["right_hip"], S["left_shoulder"],
            S["right_shoulder"], S["left_elbow"], S["right_elbow"],
            S["left_wrist"], S["right_wrist"])

        # scalar reference, frame by frame
        ang_s = np.empty_like(ang_v)
        rok_s = np.empty(len(idx), bool)
        lok_s = np.empty(len(idx), bool)
        from root_frame import euler_unity_zxy
        for k in range(len(idx)):
            Rr = build_root_frame(S["left_hip"][k], S["right_hip"][k],
                                  S["right_shoulder"][k])
            root = euler_unity_zxy(Rr)
            rsh, relb, rko = solve_right_arm(
                S["right_shoulder"][k], S["right_elbow"][k],
                S["right_wrist"][k], Rr)
            lsh, lelb, lko = solve_left_arm(
                S["left_shoulder"][k], S["left_elbow"][k],
                S["left_wrist"][k], Rr)
            ang_s[k] = np.concatenate([root, rsh, relb, lsh, lelb])
            rok_s[k], lok_s[k] = rko, lko

        if not (np.array_equal(rok_v, rok_s) and np.array_equal(lok_v, lok_s)):
            print(f"  [FAIL] {Path(src).name}: twist_ok mismatch")
            sys.exit(1)
        nan_match = np.array_equal(np.isnan(ang_v), np.isnan(ang_s))
        if not nan_match:
            print(f"  [FAIL] {Path(src).name}: NaN pattern mismatch")
            sys.exit(1)
        d = np.nanmax(np.abs(ang_v - ang_s)) if len(idx) else 0.0
        worst = max(worst, d)
        total += len(idx)
        print(f"  [ok] {Path(src).name}: {len(idx)} frames, "
              f"max |Δ| = {d:.3e} deg")

    print(f"\nselftest: {total} frames, worst |Δangle| = {worst:.3e} deg "
          f"(gate 1e-10)")
    if worst > 1e-10:
        print("SELFTEST FAIL")
        sys.exit(1)
    print("SELFTEST PASS")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        _selftest()

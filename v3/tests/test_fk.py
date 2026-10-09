"""core/fk.py: round trip through solver_q on random poses, closure on
the oracle's own filtered landmarks, and the hip anchor (D-037)."""
import json

import numpy as np
import pandas as pd
import pytest

from core import convert, fk, solver_q
from core.representation import quat_from_matrix

V3 = fk._VENDOR.parents[1]
_SH = __import__("shoulder")


def _rand_rot(rng):
    q = rng.normal(size=4)
    q /= np.linalg.norm(q)
    return q


def test_round_trip_10k_random_poses():
    """FK of convert.angles13 of a random pose -> landmarks ->
    solver_q.solve_frame_q -> angles13 reproduces the angles (1e-6 deg)
    and FK of the re-solved angles reproduces the landmarks (1e-9 m)."""
    rng = np.random.default_rng(20260925)
    worst_a = worst_p = 0.0
    for _ in range(10000):
        q_root = _rand_rot(rng)
        qs = []
        for _side in ("r", "l"):
            ty, tt = rng.uniform(-179, 179, 2)
            tz = rng.uniform(-80, 80)
            ey = rng.uniform(-170, -10)
            qs.append(quat_from_matrix(_SH.recompose_shoulder([ty, tz, tt])))
            qs.append(quat_from_matrix(_SH._ry(np.radians(ey))))
        A = convert.angles13(q_root, *qs)
        R_root = fk.recompose_zxy(A[:3])
        hip_r = rng.normal(size=3)
        hip_l = hip_r - 0.3 * R_root[:, 0]
        sh_r = hip_r + R_root @ np.array([0.05, 0.5, 0.0])
        sh_l = sh_r + R_root @ np.array([-0.35, 0.01, 0.02])
        Lu, Lf = rng.uniform(0.2, 0.35, 2)
        el_r, wr_r = fk.fk_arm(A, "right", Lu, Lf, sh_r)
        el_l, wr_l = fk.fk_arm(A, "left", Lu, Lf, sh_l)
        s = solver_q.solve_frame_q({
            "left_hip": hip_l, "right_hip": hip_r,
            "left_shoulder": sh_l, "right_shoulder": sh_r,
            "left_elbow": el_l, "right_elbow": el_r,
            "left_wrist": wr_l, "right_wrist": wr_r})
        B = convert.angles13(s["root"], s["r_sh"], s["r_elb"],
                             s["l_sh"], s["l_elb"])
        d = (B - A + 180.0) % 360.0 - 180.0
        worst_a = max(worst_a, float(np.max(np.abs(d))))
        for side, sh, el, wr in (("right", sh_r, el_r, wr_r),
                                 ("left", sh_l, el_l, wr_l)):
            e2, w2 = fk.fk_arm(B, side, Lu, Lf, sh)
            worst_p = max(worst_p, float(np.max(np.abs(e2 - el))),
                          float(np.max(np.abs(w2 - wr))))
    assert worst_a < 1e-6, worst_a
    assert worst_p < 1e-9, worst_p


def test_closure_on_oracle_clean_window():
    """On the oracle's filtered landmarks of the right_elbow clean
    window (180-540), FK with per-frame bone lengths anchored at the
    filtered shoulder equals the filtered elbow and wrist to 1e-6 m on
    every frame, both arms."""
    from bench.oracle import oracle_angles
    from bench.metrics import ANGLE_NAMES
    cfg = json.loads((V3 / "configs/default.json").read_text())
    variant = cfg["model"]["variant"]
    csv = (V3 / "output/clean" /
           f"extraction_ENSC498_right_elbow_bend_test_right_elbow__{variant}"
           ".csv")
    if not csv.exists():
        pytest.skip(f"clean-window extraction absent: {csv}")
    ot = oracle_angles(csv, cfg).iloc[180:541]
    A = ot[list(ANGLE_NAMES)].to_numpy(dtype=float)
    assert np.isfinite(A).all(), "window must be fully solvable"

    def pts(n):
        return ot[[f"{n}_f{a}" for a in "xyz"]].to_numpy(dtype=float)

    for side in ("right", "left"):
        sh, el, wr = pts(f"{side}_shoulder"), pts(f"{side}_elbow"), \
            pts(f"{side}_wrist")
        Lu = np.linalg.norm(el - sh, axis=1)
        Lf = np.linalg.norm(wr - el, axis=1)
        e2, w2 = fk.fk_arm_series(A, side, Lu, Lf, sh)
        assert np.max(np.linalg.norm(e2 - el, axis=1)) < 1e-6
        assert np.max(np.linalg.norm(w2 - wr, axis=1)) < 1e-6


def test_hip_anchor_rigid_torso():
    """A rigid torso: the offset is recovered exactly and the hip
    anchor reproduces the shoulder on every frame."""
    rng = np.random.default_rng(1)
    off = np.array([-0.27, 0.5, 0.03])
    A = np.zeros((30, 13))
    A[:, :3] = rng.uniform(-40, 40, (30, 3))
    hip = rng.normal(size=(30, 3))
    R = fk.root_matrices(A)
    sh = hip + np.einsum("nij,j->ni", R, off)
    est, n = fk.hip_shoulder_offset(A, hip, sh)
    assert n == 30 and np.allclose(est, off, atol=1e-12)
    assert np.allclose(fk.hip_anchor(A, hip, est), sh, atol=1e-12)


def test_left_is_mirror_of_right():
    """Same angle values on both sides give root-frame directions that
    are sagittal mirror images (vendor shoulder.py solve_left_arm)."""
    up_r, fo_r = fk.arm_dirs([20, 30, 40], [-60, 0], "right")
    up_l, fo_l = fk.arm_dirs([20, 30, 40], [-60, 0], "left")
    assert np.allclose(up_l, up_r * [-1, 1, 1])
    assert np.allclose(fo_l, fo_r * [-1, 1, 1])
    e, w = fk.fk_arm(np.full(13, np.nan), "right", 0.3, 0.25, np.zeros(3))
    assert np.isnan(e).all() and np.isnan(w).all()

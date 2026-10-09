"""Oracle identity: the quaternion path must reproduce the VERBATIM
vendored v1 solvers to 1e-9 deg (the comparability contract, D-005).

Path under test:   landmarks -> core.solver_q -> quats -> core.convert
Reference oracle:  landmarks -> vendor/v1 solve_right_arm /
                   solve_left_arm / build_root_frame + euler_unity_zxy

Covers 10000 random poses plus every singular branch: +-180 wrap,
shoulder gimbal (arm vertical), straight elbow (twist unobservable),
and root gimbal (euler lock).
"""
import sys
from pathlib import Path

import numpy as np
import pytest

VENDOR = Path(__file__).resolve().parents[1] / "vendor" / "v1"
if str(VENDOR) not in sys.path:
    sys.path.insert(0, str(VENDOR))

import root_frame as v1_root      # noqa: E402  vendored
import shoulder as v1_shoulder    # noqa: E402  vendored

from core import convert, solver_q          # noqa: E402
from bench.metrics import wrap_deg          # noqa: E402

TOL_DEG = 1e-9
N_RANDOM = 10000


def wrapped_close(a, b, tol=TOL_DEG):
    return np.all(np.abs(wrap_deg(np.asarray(a) - np.asarray(b))) < tol)


def random_root_points(rng):
    while True:
        p23 = rng.uniform(-1, 1, 3)
        p24 = p23 + rng.normal(size=3) * 0.3
        p12 = p24 + rng.normal(size=3) * 0.5
        if (np.linalg.norm(p24 - p23) > 0.05
                and np.linalg.norm(np.cross(p24 - p23, p12 - p24)) > 0.01):
            return p23, p24, p12


def random_arm_points(rng, p_sh):
    while True:
        p_el = p_sh + rng.normal(size=3) * 0.3
        p_wr = p_el + rng.normal(size=3) * 0.3
        u = p_el - p_sh
        f = p_wr - p_el
        if (np.linalg.norm(u) > 0.05 and np.linalg.norm(f) > 0.05
                and np.linalg.norm(np.cross(u, f))
                > 1e-3 * np.linalg.norm(u) * np.linalg.norm(f)):
            return p_el, p_wr


def test_random_pose_identity():
    rng = np.random.default_rng(42)
    for _ in range(N_RANDOM):
        p23, p24, p12 = random_root_points(rng)

        R_ref = v1_root.build_root_frame(p23, p24, p12)
        root_ref = v1_root.euler_unity_zxy(R_ref)
        q_root = solver_q.solve_root_q(p23, p24, p12)
        assert wrapped_close(convert.root_angles(q_root), root_ref)

        p14, p16 = random_arm_points(rng, p12)
        sh_ref, elb_ref, tw_ref = v1_shoulder.solve_right_arm(
            p12, p14, p16, R_ref)
        q_sh, q_elb, tw = solver_q.solve_right_arm_q(p12, p14, p16, q_root)
        assert tw == tw_ref
        assert wrapped_close(convert.shoulder_angles(q_sh), sh_ref)
        assert wrapped_close(convert.elbow_angles(q_elb), elb_ref)

        p11 = p23 + rng.normal(size=3) * 0.4
        p13, p15 = random_arm_points(rng, p11)
        sh_ref, elb_ref, tw_ref = v1_shoulder.solve_left_arm(
            p11, p13, p15, R_ref)
        q_sh, q_elb, tw = solver_q.solve_left_arm_q(p11, p13, p15, q_root)
        assert tw == tw_ref
        assert wrapped_close(convert.shoulder_angles(q_sh), sh_ref)
        assert wrapped_close(convert.elbow_angles(q_elb), elb_ref)


def test_wrap_crossing_root():
    """Root yaw near +-180 (person facing away): both paths must agree
    through the seam."""
    for dz in (-0.02, -0.01, 0.0, 0.01, 0.02):
        p23 = np.array([0.1, 0.0, 0.0])
        p24 = np.array([-0.1, 0.0, dz])       # right hip left of left hip
        p12 = p24 + np.array([0.0, 0.5, 0.0])
        ref = v1_root.euler_unity_zxy(v1_root.build_root_frame(p23, p24, p12))
        got = convert.root_angles(solver_q.solve_root_q(p23, p24, p12))
        assert wrapped_close(got, ref)
        assert abs(abs(wrap_deg(ref[1])) - 180.0) < 15.0  # near the seam


def test_shoulder_gimbal_arm_vertical():
    """Arm straight up in the root basis: tz = 90 deg, v1 sets ty := 0."""
    p23, p24 = np.array([0.0, 0.0, 0.0]), np.array([0.2, 0.0, 0.0])
    p12 = np.array([0.2, 0.5, 0.0])
    R_ref = v1_root.build_root_frame(p23, p24, p12)
    q_root = solver_q.solve_root_q(p23, p24, p12)
    p14 = p12 + np.array([0.0, 0.3, 0.0])      # straight up = root +y
    p16 = p14 + np.array([0.0, 0.0, 0.2])      # bend forward
    sh_ref, elb_ref, tw_ref = v1_shoulder.solve_right_arm(
        p12, p14, p16, R_ref)
    q_sh, q_elb, tw = solver_q.solve_right_arm_q(p12, p14, p16, q_root)
    assert sh_ref[0] == 0.0                     # v1 gimbal branch taken
    assert tw == tw_ref
    assert wrapped_close(convert.shoulder_angles(q_sh), sh_ref)
    assert wrapped_close(convert.elbow_angles(q_elb), elb_ref)


def test_straight_elbow_twist_unobservable():
    """Wrist collinear with the upper arm: twist_ok False, tt := 0 on
    both paths, ey decodes 0."""
    p23, p24 = np.array([0.0, 0.0, 0.0]), np.array([0.2, 0.0, 0.0])
    p12 = np.array([0.2, 0.5, 0.0])
    R_ref = v1_root.build_root_frame(p23, p24, p12)
    q_root = solver_q.solve_root_q(p23, p24, p12)
    p14 = p12 + np.array([0.25, -0.05, 0.1])
    p16 = p14 + (p14 - p12)                     # exact continuation
    sh_ref, elb_ref, tw_ref = v1_shoulder.solve_right_arm(
        p12, p14, p16, R_ref)
    q_sh, q_elb, tw = solver_q.solve_right_arm_q(p12, p14, p16, q_root)
    assert tw_ref is np.False_ or tw_ref == False  # noqa: E712
    assert tw == bool(tw_ref)
    assert sh_ref[2] == 0.0
    assert wrapped_close(convert.shoulder_angles(q_sh), sh_ref)
    assert wrapped_close(convert.elbow_angles(q_elb), elb_ref)
    assert abs(convert.elbow_angles(q_elb)[0]) < 1e-6


def test_root_gimbal_lock():
    """Person's forward pointing straight up in world: euler lock branch
    (x = +-90) must agree through the quaternion roundtrip."""
    p23 = np.array([0.0, 0.0, 0.0])
    p24 = np.array([0.3, 0.0, 0.0])
    p12 = p24 + np.array([0.0, 0.0, -0.5])     # forward = cross(x, -z) = +y
    R_ref = v1_root.build_root_frame(p23, p24, p12)
    assert abs(R_ref[1, 2]) > 1.0 - 1e-8        # lock branch active
    ref = v1_root.euler_unity_zxy(R_ref)
    got = convert.root_angles(solver_q.solve_root_q(p23, p24, p12))
    assert wrapped_close(got, ref, tol=1e-6)    # asin conditioning at lock


def test_solve_frame_q_full_and_blocked():
    """solve_frame_q availability rules mirror vendor/v1/occlusion.py."""
    rng = np.random.default_rng(7)
    p23, p24, p12 = random_root_points(rng)
    p14, p16 = random_arm_points(rng, p12)
    p11 = p23 + np.array([-0.05, 0.02, 0.03])
    p13, p15 = random_arm_points(rng, p11)
    pts = {"left_hip": p23, "right_hip": p24,
           "right_shoulder": p12, "right_elbow": p14, "right_wrist": p16,
           "left_shoulder": p11, "left_elbow": p13, "left_wrist": p15}

    out = solver_q.solve_frame_q(pts)
    assert all(out[k] is not None
               for k in ("root", "r_sh", "r_elb", "l_sh", "l_elb"))
    R_ref = v1_root.build_root_frame(p23, p24, p12)
    sh_ref, elb_ref, _ = v1_shoulder.solve_right_arm(p12, p14, p16, R_ref)
    assert wrapped_close(convert.shoulder_angles(out["r_sh"]), sh_ref)
    assert wrapped_close(convert.elbow_angles(out["r_elb"]), elb_ref)

    # wrist blocked: swing still solves (fake wrist), elbow None,
    # twist reported unobservable
    blocked = dict(pts)
    blocked["right_wrist"] = np.full(3, np.nan)
    out = solver_q.solve_frame_q(blocked)
    assert out["r_sh"] is not None
    assert out["r_elb"] is None
    assert out["r_twist_ok"] is False

    # hip blocked: no root, and (per current-frame availability) no arms
    blocked = dict(pts)
    del blocked["left_hip"]
    out = solver_q.solve_frame_q(blocked)
    assert out["root"] is None and out["r_sh"] is None

    # shoulder-as-root-reference fallback: right shoulder gone, root
    # still solves via the left shoulder
    blocked = dict(pts)
    blocked["right_shoulder"] = None
    out = solver_q.solve_frame_q(blocked)
    assert out["root"] is not None
    assert out["r_sh"] is None                  # right arm needs its shoulder
    assert out["l_sh"] is not None

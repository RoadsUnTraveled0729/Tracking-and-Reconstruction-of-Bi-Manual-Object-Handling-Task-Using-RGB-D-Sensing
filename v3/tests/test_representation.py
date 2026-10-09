"""Unit tests for core/representation.py (Phase 2). Pure numpy."""
import numpy as np
import pytest

from core import representation as rep


def rand_quat(rng):
    q = rng.normal(size=4)
    q = q / np.linalg.norm(q)
    return q if q[0] >= 0 else -q


def test_quat_matrix_roundtrip():
    rng = np.random.default_rng(1)
    for _ in range(200):
        q = rand_quat(rng)
        R = rep.matrix_from_quat(q)
        assert np.allclose(R @ R.T, np.eye(3), atol=1e-12)
        assert np.linalg.det(R) == pytest.approx(1.0)
        q2 = rep.quat_from_matrix(R)
        assert np.allclose(q, q2, atol=1e-12)


def test_qmul_matches_matrix_product():
    rng = np.random.default_rng(2)
    for _ in range(50):
        a, b = rand_quat(rng), rand_quat(rng)
        left = rep.matrix_from_quat(rep.qmul(a, b))
        right = rep.matrix_from_quat(a) @ rep.matrix_from_quat(b)
        assert np.allclose(left, right, atol=1e-12)


def test_quat_about_matches_axis_matrices():
    a = 0.7
    c, s = np.cos(a), np.sin(a)
    Rx = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    Ry = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    Rz = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    for axis, R in (([1, 0, 0], Rx), ([0, 1, 0], Ry), ([0, 0, 1], Rz)):
        M = rep.matrix_from_quat(rep.quat_about(np.array(axis, float), a))
        assert np.allclose(M, R, atol=1e-12)


def test_qexp_qlog_inverse():
    rng = np.random.default_rng(3)
    for _ in range(100):
        v = rng.normal(size=3)
        v = v / np.linalg.norm(v) * rng.uniform(1e-8, np.pi - 1e-6)
        assert np.allclose(rep.qlog(rep.qexp(v)), v, atol=1e-9)
    assert np.allclose(rep.qlog(rep.QUAT_ID), np.zeros(3))


def test_qrotate_matches_matrix():
    rng = np.random.default_rng(4)
    q = rand_quat(rng)
    v = rng.normal(size=3)
    assert np.allclose(rep.qrotate(q, v),
                       rep.matrix_from_quat(q) @ v, atol=1e-12)


def test_slerp_endpoints_midpoint_hemisphere():
    q0 = rep.QUAT_ID
    q1 = rep.quat_about(np.array([0.0, 0.0, 1.0]), np.pi / 2)
    assert np.allclose(rep.slerp(q0, q1, 0.0), q0, atol=1e-12)
    assert np.allclose(rep.slerp(q0, q1, 1.0), q1, atol=1e-12)
    mid = rep.slerp(q0, q1, 0.5)
    expect = rep.quat_about(np.array([0.0, 0.0, 1.0]), np.pi / 4)
    assert np.allclose(mid, expect, atol=1e-12)
    # -q1 is the same orientation; slerp must take the short arc
    mid2 = rep.slerp(q0, -q1, 0.5)
    assert np.allclose(mid2, expect, atol=1e-12)


def test_angle_between():
    q0 = rep.QUAT_ID
    q1 = rep.quat_about(np.array([1.0, 0.0, 0.0]), 0.3)
    assert rep.angle_between(q0, q1) == pytest.approx(0.3, abs=1e-12)
    assert rep.angle_between(q1, q1) == pytest.approx(0.0, abs=1e-12)


def test_swing_twist_decomposition():
    rng = np.random.default_rng(5)
    axis = np.array([1.0, 0.0, 0.0])
    for _ in range(100):
        q = rand_quat(rng)
        swing, twist = rep.swing_twist(q, axis)
        # recomposition (orientation equality up to sign)
        rec = rep.qmul(swing, twist)
        assert (np.allclose(rec, q, atol=1e-12)
                or np.allclose(rec, -q, atol=1e-12))
        # twist is purely about the axis
        assert twist[2] == pytest.approx(0.0, abs=1e-12)
        assert twist[3] == pytest.approx(0.0, abs=1e-12)
        # swing carries the axis exactly where q does
        assert np.allclose(rep.qrotate(swing, axis),
                           rep.qrotate(q, axis), atol=1e-10)


def test_quat_one_euro_constant_input_is_identity():
    f = rep.QuatOneEuro(freq=30.0, min_cutoff=0.05, beta=1.0)
    q = rep.quat_about(np.array([0.0, 1.0, 0.0]), 0.4)
    for _ in range(10):
        out = f(q)
    assert rep.angle_between(out, q) < 1e-12


def test_quat_one_euro_smooths_noise():
    rng = np.random.default_rng(6)
    base = rep.quat_about(np.array([0.0, 0.0, 1.0]), 0.5)
    f = rep.QuatOneEuro(freq=30.0, min_cutoff=0.5, beta=0.0)
    raw_dev, flt_dev = [], []
    for _ in range(300):
        noise = rep.qexp(rng.normal(scale=0.02, size=3))
        q = rep.qmul(base, noise)
        out = f(q)
        raw_dev.append(rep.angle_between(q, base))
        flt_dev.append(rep.angle_between(out, base))
    assert np.std(flt_dev[50:]) < 0.5 * np.std(raw_dev[50:])


def test_quat_one_euro_step_converges():
    f = rep.QuatOneEuro(freq=30.0, min_cutoff=1.0, beta=0.1)
    q0 = rep.QUAT_ID
    q1 = rep.quat_about(np.array([0.0, 1.0, 0.0]), 1.0)
    f(q0)
    errs = [rep.angle_between(f(q1), q1) for _ in range(120)]
    assert errs[-1] < 1e-3
    assert errs[0] > errs[-1]


def test_quat_one_euro_reset_and_validation():
    with pytest.raises(ValueError):
        rep.QuatOneEuro(freq=0.0)
    f = rep.QuatOneEuro(freq=30.0)
    q1 = rep.quat_about(np.array([1.0, 0.0, 0.0]), 0.8)
    f(rep.QUAT_ID)
    f.reset()
    assert np.allclose(f(q1), q1, atol=1e-12)  # first sample after reset


def test_qnormalize_rejects_zero():
    with pytest.raises(ValueError):
        rep.qnormalize(np.zeros(4))


def test_quat_one_euro_ramp_lag_is_first_order():
    # beta 0: constant alpha; steady-state lag of a constant-rate ramp
    # about one axis = (1 - alpha) / alpha samples (first-order EMA)
    f = rep.QuatOneEuro(freq=30.0, min_cutoff=2.0, beta=0.0)
    rate = np.radians(0.4)
    ax = np.array([0.0, 0.0, 1.0])
    for i in range(400):
        q = rep.quat_about(ax, rate * i)
        y = f(q)
    tau = 1.0 / (2 * np.pi * 2.0)
    a = 1.0 / (1.0 + tau * 30.0)
    lag = rep.angle_between(q, y) / rate
    assert lag == pytest.approx((1 - a) / a, rel=1e-3)

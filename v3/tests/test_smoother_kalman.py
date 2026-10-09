"""M5 smoother (ii): tangent-space constant-velocity Kalman filter
(strategies/smoother_kalman.py, D-038)."""
import json
from pathlib import Path

import numpy as np
import pytest

from core import convert
from core.representation import (angle_between, qconj, qlog, qmul,
                                  quat_about)
from strategies.s2_quat_prediction import (S2QuatPrediction, _with_decay,
                                           project_v1_swing,
                                           smoother_params_for)
from strategies.smoother_base import SMOOTHERS, build_smoother
from strategies.smoother_kalman import TangentKalmanSmoother

V3 = Path(__file__).resolve().parents[1]
X, Y, Z = np.eye(3)
FREQ = 30.0
KINDS = ("root", "swing", "twist", "elbow")
# ramp axis per kind (world frame of the synthetic truth below)
AX = {"root": Z, "twist": X, "swing": Y, "elbow": Y}


def _cfg():
    return json.loads((V3 / "configs/default.json").read_text())


def _s2():
    return _cfg()["strategy"]["s2_quat_prediction"]


def _params(name, kind):
    s2 = _s2()
    return _with_decay(smoother_params_for(s2, name)[kind], s2)


def _mk(name, kind, params=None):
    return build_smoother(
        name, kind, params if params is not None else _params(name, kind),
        FREQ, projector=(project_v1_swing if kind in ("swing", "elbow")
                         else None))


def _truth(kind, a_deg):
    """Synthetic orientation per kind; swing/elbow stay on Ry*Rz."""
    if kind in ("swing", "elbow"):
        return qmul(quat_about(Y, np.radians(a_deg)),
                    quat_about(Z, np.radians(10.0)))
    return quat_about(AX[kind], np.radians(a_deg))


def _err_deg(kind, q_out, a_deg):
    """Signed error of q_out along the ramp axis (world frame), deg."""
    e = qlog(qmul(q_out, qconj(_truth(kind, a_deg))))
    return float(np.degrees(e @ AX[kind]))


def _ramp_lag(name, kind, rate=1.0, sigma=0.5, n=400, skip=100, seed=0):
    """Mean lag in frames on a rate deg/frame ramp with N(0, sigma) deg
    noise, after `skip` settling frames."""
    s = _mk(name, kind)
    rng = np.random.default_rng(seed)
    e = []
    for i in range(n):
        a = rate * i
        e.append(_err_deg(kind, s.update(_truth(kind, a + rng.normal(
            0.0, sigma)), True), a))
    return -float(np.mean(e[skip:])) / rate


# -- registration and config plumbing ------------------------------------

def test_registered_and_config_plumbing():
    assert SMOOTHERS["tangent_kf"] is TangentKalmanSmoother
    cfg = _cfg()
    s2 = cfg["strategy"]["s2_quat_prediction"]
    kf = s2["smoother_params"]["tangent_kf"]
    assert set(kf) == set(KINDS)
    for k in KINDS:
        assert kf[k]["lag_frames"] == 0          # off: PSV3 has no lag
        assert kf[k]["decay_lambda"] is None     # inherits S2's lambda
    cfg["strategy"]["s2_quat_prediction"]["smoother"] = "tangent_kf"
    st = S2QuatPrediction(cfg)
    tracks = [("root", st.root)] + [(k, st.arms[s][k]) for s in ("r", "l")
                                    for k in ("swing", "twist", "elbow")]
    for kind, tr in tracks:
        sm = tr.smoother
        assert isinstance(sm, TangentKalmanSmoother) and sm.kind == kind
        assert sm.decay == s2["decay_lambda"] == 0.8
        assert sm.lag == 0
        assert sm.r_v == pytest.approx(kf[kind]["r_v"] * (np.pi / 180) ** 2)
        assert sm.q_w == pytest.approx(kf[kind]["q_w"] * (np.pi / 180) ** 2)
        assert (sm.sp.projector is project_v1_swing) == (
            kind in ("swing", "elbow"))
    # legacy flat params (sweep overrides) still reach the smoother
    flat = {k: {"q_w": 10.0, "q_r": 1.0, "r_v": 2.0} for k in KINDS}
    s2f = dict(s2, smoother="tangent_kf", smoother_params=flat)
    assert smoother_params_for(s2f, "tangent_kf") is flat
    # quat_one_euro keeps its own block
    assert smoother_params_for(s2, "quat_one_euro")["elbow"]["beta"] == 2.0


def test_smoother_params_for_missing_block_names_it():
    """Review finding 3: a nested smoother_params without the selected
    smoother's block raises and names that block (no silent fallback to
    the whole dict)."""
    s2 = _cfg()["strategy"]["s2_quat_prediction"]
    nested = {"quat_one_euro": s2["smoother_params"]["quat_one_euro"]}
    s2n = dict(s2, smoother_params=nested)
    with pytest.raises(ValueError, match=r"smoother_params\.tangent_kf"):
        smoother_params_for(s2n, "tangent_kf")
    assert smoother_params_for(s2n, "none") == {}


def test_missing_or_bad_params_raise():
    with pytest.raises(ValueError):
        TangentKalmanSmoother("root", None, FREQ)
    with pytest.raises(ValueError):
        TangentKalmanSmoother("root", {"q_w": 1.0, "q_r": 1.0, "r_v": None,
                                       "decay_lambda": 0.8}, FREQ)
    with pytest.raises(ValueError):
        TangentKalmanSmoother("root", {"q_w": 1.0, "q_r": 1.0, "r_v": 0.0,
                                       "decay_lambda": 0.8}, FREQ)


# -- behaviour -----------------------------------------------------------

@pytest.mark.parametrize("kind", KINDS)
def test_identity_on_constant_input(kind):
    s = _mk("tangent_kf", kind)
    q = _truth(kind, 37.0)
    for _ in range(200):
        out = s.update(q, True)
        assert angle_between(out, q) < 1e-9


@pytest.mark.parametrize("kind", ["swing", "elbow"])
def test_output_on_v1_manifold(kind):
    s = _mk("tangent_kf", kind)
    rng = np.random.default_rng(1)
    for i in range(200):
        q = qmul(quat_about(Y, np.radians(30 + 20 * np.sin(i / 5)
                                          + rng.normal(0, 2))),
                 quat_about(Z, np.radians(40 * np.cos(i / 7))))
        out = s.update(q if (i % 9 or i == 0) else None, True)
        assert np.isclose(np.linalg.norm(out), 1.0, atol=1e-12)
        assert abs(convert.shoulder_angles(out)[2]) < 1e-6


def test_twist_is_about_x_and_unwraps_through_180():
    s = _mk("tangent_kf", "twist")
    prev = None
    for i in range(80):
        out = s.update(quat_about(X, np.radians(150 + 2 * i)), True)
        assert np.allclose(out[2:], 0.0, atol=1e-12)
        if prev is not None:     # no jump when the angle crosses 180
            assert np.degrees(angle_between(prev, out)) < 3.0
        prev = out


@pytest.mark.parametrize("kind", KINDS)
def test_ramp_lag_zero_and_below_quat_one_euro(kind):
    """1 deg/frame ramp, N(0, 0.5 deg) noise, default.json params: the
    constant-velocity model has no steady-state ramp lag (measured
    0.039-0.042 frames); quat_one_euro with its D-034 params lags 0.61
    (twist) to 1.57 (elbow) frames on the same ramp and noise."""
    lag_kf = _ramp_lag("tangent_kf", kind)
    lag_qoe = _ramp_lag("quat_one_euro", kind)
    assert abs(lag_kf) < 0.1
    assert lag_qoe > 0.5
    assert abs(lag_kf) < lag_qoe


@pytest.mark.parametrize("kind", KINDS)
def test_convergence_after_step(kind):
    """20 deg step: the output converges to within 0.1 deg (measured 9
    to 23 frames with the default params; the CV model overshoots by
    2.4-3.0 deg, the known price of a velocity state; quat_one_euro
    settles in 3-8 frames without overshoot)."""
    s = _mk("tangent_kf", kind)
    for _ in range(60):
        s.update(_truth(kind, 0.0), True)
    err = [_err_deg(kind, s.update(_truth(kind, 20.0), True), 20.0)
           for _ in range(60)]
    assert max(abs(e) for e in err[30:]) < 0.1
    assert max(err) < 0.2 * 20.0          # overshoot bounded (15 % seen)


@pytest.mark.parametrize("kind", ["root", "twist"])
def test_predict_only_velocity_decays_at_s2_lambda(kind):
    """After a 1 deg/frame ramp, missing frames (update(None)) continue
    the motion with per-frame increments shrinking by lambda = 0.8
    (config s2_quat_prediction.decay_lambda), as S2's own prediction
    does."""
    s = _mk("tangent_kf", kind)
    for i in range(120):
        s.update(_truth(kind, float(i)), True)
    outs = [s.update(None, True) for _ in range(8)]
    inc = [np.degrees(angle_between(a, b)) for a, b in zip(outs, outs[1:])]
    for a, b in zip(inc, inc[1:]):
        assert b / a == pytest.approx(0.8, rel=1e-6)
    assert 0.5 < inc[0] < 1.0     # the velocity estimate was ~1 deg/frame


def test_s2_predicted_frame_resyncs_to_track_output():
    s = _mk("tangent_kf", "root")
    for i in range(30):
        s.update(_truth("root", float(i)), True)
    q_track = _truth("root", 50.0)
    assert s.update(q_track, False) is q_track
    assert angle_between(s.x, q_track) < 1e-12
    w_before = s.w.copy()
    s.update(_truth("root", 51.0), False)
    assert np.allclose(s.w, 0.8 * w_before)


def test_covariance_symmetric_positive_definite_10k():
    rng = np.random.default_rng(2)
    for kind in ("root", "twist"):
        s = _mk("tangent_kf", kind)
        for i in range(10000):
            r = rng.random()
            q = _truth(kind, 30 * np.sin(i / 40) + rng.normal(0, 1))
            if r < 0.05:
                s.update(None, True)
            elif r < 0.1:
                s.update(q, False)
            else:
                s.update(q, True)
            P = s.covariance()
            if P is None:
                continue
            assert np.array_equal(P, P.T)
            assert np.all(np.linalg.eigvalsh(P) > 0)


def test_matches_generic_numpy_kalman_on_scalar_track():
    """The closed-form 2x2 Joseph update equals a textbook matrix
    Kalman filter (F, Q, H, R, Joseph form) on the twist angle."""
    p = {"q_w": 300.0, "q_r": 2.0, "r_v": 0.5, "decay_lambda": 0.8}
    s = TangentKalmanSmoother("twist", p, FREQ)
    dt, d2r = 1 / FREQ, (np.pi / 180) ** 2
    qw, qr, R = p["q_w"] * d2r, p["q_r"] * d2r, p["r_v"] * d2r
    F = np.array([[1, dt], [0, 1]])
    Q = qw * np.array([[dt ** 3 / 3, dt ** 2 / 2], [dt ** 2 / 2, dt]]) \
        + qr * np.array([[dt, 0], [0, 0]])
    H = np.array([[1.0, 0.0]])
    rng = np.random.default_rng(3)
    z = np.radians(np.cumsum(rng.normal(0, 1.0, 300)))
    x = P = None
    for i, zi in enumerate(z):
        out = s.update(quat_about(X, zi), True)
        if i == 0:
            x = np.array([zi, 0.0])
        elif i == 1:
            x = np.array([zi, (zi - z[0]) / dt])
            P = R * np.array([[1, 1 / dt], [1 / dt, 2 / dt ** 2]])
        else:
            x = F @ x
            P = F @ P @ F.T + Q
            K = P @ H.T / (H @ P @ H.T + R)
            x = x + (K * (zi - x[0])).ravel()
            A = np.eye(2) - K @ H
            P = A @ P @ A.T + R * K @ K.T
            assert np.allclose(s.covariance(), P, rtol=1e-10, atol=1e-18)
        assert 2 * np.arctan2(out[1], out[0]) == pytest.approx(
            (x[0] + np.pi) % (2 * np.pi) - np.pi, abs=1e-9)


@pytest.mark.parametrize("k", [0, 1, 2, 4])
def test_two_point_init_spans_unmeasured_frames(k):
    """Review finding 2: with k update(None) frames between the first
    and second sample of a 1 deg/frame ramp, the two samples are k + 1
    frames apart, so the initial velocity is 1 deg/frame for every k
    (the old max(k, 1) interval gave 1.0, 2.0, 1.5, 1.25 for k = 0, 1,
    2, 4) and P0 uses the same interval T = (k + 1) dt."""
    p = {"q_w": 300.0, "q_r": 2.0, "r_v": 0.5, "decay_lambda": 0.8}
    s = TangentKalmanSmoother("twist", p, FREQ)
    dt, R = 1 / FREQ, p["r_v"] * (np.pi / 180) ** 2
    s.update(quat_about(X, 0.0), True)
    for _ in range(k):
        s.update(None, False)
    s.update(quat_about(X, np.radians(k + 1.0)), True)
    w_deg_per_frame = float(np.degrees(np.ravel(s.w)[0]) * dt)
    assert w_deg_per_frame == pytest.approx(1.0, rel=1e-9)
    T = (k + 1) * dt
    P0 = R * np.array([[1, 1 / T], [1 / T, 2 / T ** 2]])
    assert np.allclose(s.covariance(), P0, rtol=1e-10, atol=1e-18)


def test_lag_frames_option_delays_and_smooths():
    """Optional fixed-lag RTS (off by default): with lag_frames 3 the
    output tracks the ramp 3 frames late and with less noise than the
    causal filter."""
    base = dict(_params("tangent_kf", "root"))
    rng = np.random.default_rng(4)
    noise = rng.normal(0, 0.5, 400)
    res = {}
    for L in (0, 3):
        s = _mk("tangent_kf", "root", dict(base, lag_frames=L))
        e = []
        for i in range(400):
            out = s.update(_truth("root", i + noise[i]), True)
            e.append(_err_deg("root", out, float(i - L)))
        res[L] = np.asarray(e[100:])
    assert abs(res[3].mean()) < 0.1          # centred on frame t - 3
    assert res[3].std() < res[0].std()


def test_update_speed_under_50_us():
    """Mean time per measured update (best of 3 runs of 2000 updates,
    so a transiently loaded machine does not fail the test)."""
    import time
    for kind in KINDS:
        qs = [_truth(kind, 0.5 * i) for i in range(2000)]
        best = np.inf
        for _ in range(3):
            s = _mk("tangent_kf", kind)
            t0 = time.perf_counter()
            for q in qs:
                s.update(q, True)
            best = min(best, (time.perf_counter() - t0) / len(qs) * 1e6)
        assert best < 50.0, f"{kind}: {best:.1f} us per update"

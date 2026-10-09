"""M4 smoother hook, warm start and derived step caps (D-027, D-029,
D-031, D-032) plus the legacy regression of S2 (smoother none)."""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from core import convert
from core.representation import angle_between, qmul, quat_about
from strategies.s2_quat_prediction import (_JointTrack, derive_step_caps,
                                           project_v1_swing)
from strategies.smoother_base import (NoSmoother, QuatOneEuroSmoother,
                                      build_smoother)

V3 = Path(__file__).resolve().parents[1]
X, Y, Z = np.eye(3)
FREQ = 30.0
P = {"min_cutoff": 1.0, "beta": 0.0, "d_cutoff": 1.0}


def swing(ty, tz):
    return qmul(quat_about(Y, np.radians(ty)), quat_about(Z, np.radians(tz)))


def test_none_is_identity():
    s = build_smoother("none", "swing", None, FREQ)
    assert isinstance(s, NoSmoother)
    q = swing(10, 20)
    assert s.update(q, True) is q
    with pytest.raises(KeyError):
        build_smoother("no_such_smoother", "swing", None, FREQ)


@pytest.mark.parametrize("kind", ["swing", "elbow"])
def test_quat_one_euro_output_stays_on_v1_manifold(kind):
    s = QuatOneEuroSmoother(kind, P, FREQ, projector=project_v1_swing)
    rng = np.random.default_rng(0)
    for i in range(60):
        q = s.update(swing(30 + 20 * np.sin(i / 5) + rng.normal(0, 2),
                           40 * np.cos(i / 7)), True)
        assert np.isclose(np.linalg.norm(q), 1.0, atol=1e-12)
        # Ry*Rz manifold: no residual x rotation in v1's factorization
        assert abs(convert.shoulder_angles(q)[2]) < 1e-6


def test_twist_output_is_rotation_about_x():
    s = QuatOneEuroSmoother("twist", P, FREQ)
    for i in range(40):
        q = s.update(quat_about(X, np.radians(170 + 5 * i)), True)
        assert np.allclose(q[2:], 0.0, atol=1e-12)
        assert np.isclose(np.linalg.norm(q), 1.0)


def _ramp_lag_frames(kind, rate_deg):
    """Steady-state lag in frames of a constant-rate ramp."""
    s = QuatOneEuroSmoother(kind, P, FREQ, projector=(
        project_v1_swing if kind == "elbow" else None))
    out = []
    for i in range(300):
        a = rate_deg * i
        q = (quat_about(X, np.radians(a)) if kind == "twist"
             else swing(0.0, a * 0.2) if kind == "elbow"
             else quat_about(Z, np.radians(a)))
        out.append(angle_between(q, s.update(q, True)))
    return np.degrees(out[-1]) / (rate_deg * (0.2 if kind == "elbow" else 1))


@pytest.mark.parametrize("kind", ["twist", "root", "elbow"])
def test_ramp_lag_matches_first_order_ema(kind):
    # beta 0: fixed alpha; first-order EMA ramp lag = (1 - a) / a frames
    tau = 1.0 / (2 * np.pi * P["min_cutoff"])
    a = 1.0 / (1.0 + tau * FREQ)
    assert _ramp_lag_frames(kind, 0.5) == pytest.approx((1 - a) / a,
                                                        rel=1e-3)


def test_warm_start_snaps_first_measurement():
    target = swing(40, 30)
    cap = np.radians(1.0)
    cold = _JointTrack(np.array([1.0, 0, 0, 0]), 0.8, cap, 0.5,
                       projector=None, warm_start=False)
    warm = _JointTrack(np.array([1.0, 0, 0, 0]), 0.8, cap, 0.5,
                       projector=None, warm_start=True)
    qc, _, conv_c = cold.update(target)
    qw, _, conv_w = warm.update(target)
    assert np.isclose(angle_between(qc, np.array([1.0, 0, 0, 0])), cap)
    assert not conv_c and cold.capped
    assert angle_between(qw, target) < 1e-12 and conv_w
    # after the first measurement the cap applies to warm tracks too
    qw2, _, _ = warm.update(swing(80, 30))
    assert np.isclose(angle_between(qw, qw2), cap) and warm.capped


def _s2cfg():
    return json.loads((V3 / "configs/default.json").read_text())[
        "strategy"]["s2_quat_prediction"]


def test_derive_step_caps_fixed_is_per_kind_both_sides():
    s2 = dict(_s2cfg(), step_cap_source="fixed")
    caps = derive_step_caps(s2, None)
    for k in ("swing", "twist", "elbow"):
        assert caps[f"r_{k}"] == caps[f"l_{k}"] == s2["step_caps_deg"][k]
    assert caps["root"] == s2["step_caps_deg"]["root"]


def test_derive_step_caps_manifest_per_side_min_and_degenerate():
    s2 = dict(_s2cfg(), step_cap_source="manifest")
    b = {a: 10.0 for a in ("root_x", "root_y", "root_z", "r_swing_y",
                           "r_swing_z", "r_twist", "r_elbow_y",
                           "r_elbow_z", "l_swing_y", "l_swing_z",
                           "l_twist", "l_elbow_y", "l_elbow_z")}
    b.update(root_z=1.0, r_swing_z=2.0, l_swing_y=4.0, r_twist=3.0,
             r_elbow_z=1e-9, l_elbow_z=1e-9, l_elbow_y=6.0)
    caps = derive_step_caps(s2, b)
    f = s2["step_cap_budget_fraction"]
    assert caps["root"] == pytest.approx(f * 1.0)
    assert caps["r_swing"] == pytest.approx(f * 2.0)
    assert caps["l_swing"] == pytest.approx(f * 4.0)
    assert caps["r_twist"] == pytest.approx(f * 3.0)
    assert caps["l_twist"] == pytest.approx(f * 10.0)
    # identically-zero elbow_z (noise-floor budget) is skipped
    assert caps["r_elbow"] == pytest.approx(f * 10.0)
    assert caps["l_elbow"] == pytest.approx(f * 6.0)
    with pytest.raises(ValueError):
        derive_step_caps(s2, None)
    with pytest.raises(ValueError):
        derive_step_caps(dict(s2, step_cap_source="bogus"), b)


def _section(text, strategy):
    m = re.search(rf"=== strategy: {strategy} ===\n(.*?)\n\n", text, re.S)
    return m.group(1)


@pytest.mark.skipif(not (V3 / "output/extraction_recording_20260224_083945"
                         "__rtmpose-x_yolox-m.csv").exists(),
                    reason="pinned-bag extraction not present")
def test_legacy_overrides_reproduce_pre_d033_grade():
    """smoother none + warm_start false + fixed caps on the D-003
    manifest reproduces the pinned pre-D-033 S2 table bit-for-bit (to
    the printed precision)."""
    pinned = (V3 / "dataset/phase5_s_grade__rtmpose-x_yolox-m__pre_d033"
              ".txt").read_text()
    S = "strategy.s2_quat_prediction"
    r = subprocess.run(
        [sys.executable, str(V3 / "bench/grade.py"), "--manifest",
         str(V3 / "configs/scenarios_20260224__rtmpose-x_yolox-m.json"),
         "--strategies", "s2_quat_prediction",
         "--set", f"{S}.warm_start=false",
         "--set", f'{S}.step_cap_source="fixed"',
         "--set", f'{S}.smoother="none"'],
        capture_output=True, text=True, check=True)
    assert "teleport twist gate: none" in r.stdout
    assert (_section(r.stdout, "s2_quat_prediction")
            == _section(pinned, "s2_quat_prediction"))
    gate = [ln for ln in r.stdout.splitlines()
            if "s2_quat_prediction: teleport_zero" in ln]
    assert gate and gate[0] in pinned

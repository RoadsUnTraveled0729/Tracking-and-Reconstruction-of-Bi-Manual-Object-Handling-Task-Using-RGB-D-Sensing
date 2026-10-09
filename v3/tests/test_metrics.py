"""Unit tests for bench/metrics.py (Phase 0). Pure numpy, no markers."""
import math
from pathlib import Path

import numpy as np
import pytest

from bench import metrics as m

N_ANGLES = len(m.ANGLE_NAMES)
N_GROUPS = len(m.GROUP_NAMES)


def test_group_tables_cover_all_angles_once():
    flat = [i for idx in m.GROUP_ANGLES for i in idx]
    assert sorted(flat) == list(range(N_ANGLES))
    assert len(m.GROUP_ANGLES) == N_GROUPS


def test_wrap_deg_seam():
    assert m.wrap_deg(185.0) == pytest.approx(-175.0)
    assert m.wrap_deg(-190.0) == pytest.approx(170.0)
    assert m.wrap_deg(180.0) == pytest.approx(180.0)
    assert m.wrap_deg(-180.0) == pytest.approx(180.0)
    assert m.wrap_deg(540.0) == pytest.approx(180.0)
    assert m.wrap_deg(0.0) == pytest.approx(0.0)


def test_angle_error_crosses_seam():
    out = np.zeros((1, N_ANGLES))
    truth = np.zeros((1, N_ANGLES))
    out[0, 1] = 179.0
    truth[0, 1] = -179.0
    err = m.angle_error(out, truth)
    assert err[0, 1] == pytest.approx(2.0)
    assert err[0, 0] == 0.0


def test_angle_error_shape_mismatch_raises():
    with pytest.raises(ValueError):
        m.angle_error(np.zeros((2, N_ANGLES)), np.zeros((3, N_ANGLES)))


def test_group_error_is_max_over_members():
    err = np.zeros((1, N_ANGLES))
    err[0, 0], err[0, 1], err[0, 2] = 1.0, 5.0, 3.0   # root members
    err[0, 5] = 7.0                                    # R_twist (single)
    g = m.group_error(err)
    assert g.shape == (1, N_GROUPS)
    assert g[0, m.GROUP_NAMES.index("root")] == 5.0
    assert g[0, m.GROUP_NAMES.index("R_twist")] == 7.0
    assert g[0, m.GROUP_NAMES.index("L_elbow")] == 0.0


def test_e_occ_window_stats():
    gerr = np.zeros((10, N_GROUPS))
    gerr[3:6, 0] = [2.0, 4.0, 6.0]
    res = m.e_occ(gerr, 3, 6)
    assert res["mean"][0] == pytest.approx(4.0)
    assert res["max"][0] == pytest.approx(6.0)
    assert res["mean"][1] == 0.0
    with pytest.raises(ValueError):
        m.e_occ(gerr, 5, 5)


def test_e_reacq_first_k_frames():
    gerr = np.zeros((20, N_GROUPS))
    gerr[10:15, 2] = [10.0, 8.0, 6.0, 4.0, 2.0]
    res = m.e_reacq(gerr, 10, k=5)
    assert res[2] == pytest.approx(6.0)
    with pytest.raises(ValueError):
        m.e_reacq(gerr, 18, k=5)


def test_recovery_time_immediate_delayed_never():
    gerr = np.full((30, N_GROUPS), 100.0)
    gerr[10:, 0] = 1.0                      # immediate at window end
    gerr[14:, 1] = 1.0                      # 4 frames late
    gerr[10:, 2] = 1.0
    gerr[12, 2] = 100.0                     # blip breaks the sustain
    res = m.recovery_time(gerr, 10, thresh_deg=5.0, sustain=3)
    assert res[0] == 0.0
    assert res[1] == 4.0
    assert res[2] == 3.0                    # restarts after the blip
    assert math.isinf(res[3])               # never below threshold


def test_recovery_time_tail_too_short_is_inf():
    gerr = np.full((12, N_GROUPS), 100.0)
    gerr[10:, :] = 1.0                      # only 2 frames < sustain=3
    res = m.recovery_time(gerr, 10, thresh_deg=5.0, sustain=3)
    assert all(math.isinf(v) for v in res)


def test_angle_steps_wrap_aware():
    a = np.zeros((3, N_ANGLES))
    a[0, 1], a[1, 1], a[2, 1] = 179.0, -179.0, -178.0
    s = m.angle_steps(a)
    assert s.shape == (2, N_ANGLES)
    assert s[0, 1] == pytest.approx(2.0)    # seam crossing, not 358
    assert s[1, 1] == pytest.approx(1.0)
    with pytest.raises(ValueError):
        m.angle_steps(a[:1])


def test_teleport_budget_and_count():
    rng = np.random.default_rng(0)
    clean = rng.uniform(0.0, 1.0, size=(2000, N_ANGLES))
    budget = m.teleport_budget(clean, safety=1.5)
    assert budget.shape == (N_ANGLES,)
    assert np.all(budget > 1.0) and np.all(budget < 1.6)

    steps = rng.uniform(0.0, 1.0, size=(100, N_ANGLES))
    res = m.teleport_count(steps, budget)
    assert res["count"] == 0
    assert res["worst_ratio"] < 1.0

    steps[50, 3] = 30.0                     # injected teleport
    res = m.teleport_count(steps, budget)
    assert res["count"] == 1
    assert res["worst_step_deg"] == pytest.approx(30.0)
    assert res["per_angle_counts"][3] == 1
    assert res["per_angle_counts"].sum() == 1


def test_teleport_budget_floor_for_identically_zero_angles():
    """An angle that is identically zero by construction (elbow ez)
    must not count float64 noise (~1e-14 deg) as teleports."""
    clean = np.zeros((1000, N_ANGLES))
    budget = m.teleport_budget(clean, safety=1.5)
    assert np.all(budget == 1e-9)
    steps = np.zeros((100, N_ANGLES))
    steps[10, 7] = 3e-14                    # measured noise scale
    assert m.teleport_count(steps, budget)["count"] == 0
    steps[11, 7] = 1e-6                     # a real (if tiny) jump
    assert m.teleport_count(steps, budget)["count"] == 1


def test_continuity_p95():
    steps = np.tile(np.linspace(0.0, 1.0, 101)[:, None], (1, N_ANGLES))
    p95 = m.continuity_p95(steps)
    assert p95.shape == (N_ANGLES,)
    assert p95[0] == pytest.approx(0.95)


def test_joint_limit_violations():
    a = np.zeros((10, N_ANGLES))
    a[:5, 6] = 200.0                        # r_elbow_y out of range
    limits = {name: None for name in m.ANGLE_NAMES}
    limits["r_elbow_y"] = (-5.0, 160.0)
    res = m.joint_limit_violations(a, limits)
    assert res["per_angle"] == {"r_elbow_y": 0.5}
    assert res["fraction"] == pytest.approx(0.5)
    # no constrained angle -> fraction 0, honest empty report
    res = m.joint_limit_violations(a, {name: None for name in m.ANGLE_NAMES})
    assert res["fraction"] == 0.0 and res["per_angle"] == {}


def test_bone_length_deviation():
    ref = np.array([0.30, 0.25])
    lengths = np.tile(ref, (100, 1))
    lengths[10, 0] = 0.33                   # +10 percent once
    res = m.bone_length_deviation(lengths, ref)
    assert res["max"][0] == pytest.approx(0.1)
    assert res["max"][1] == 0.0
    assert res["p95"][0] < 0.1
    with pytest.raises(ValueError):
        m.bone_length_deviation(lengths, np.array([0.3, 0.0]))


def test_latency_summary_and_gate():
    samples = np.full(160, 10.0)
    samples[:60] = 100.0                    # warmup spikes
    samples[100] = 20.0
    s = m.latency_summary(samples, warmup=60)
    assert s["n"] == 100 and s["warmup_n"] == 60
    assert s["warmup_max"] == 100.0
    assert s["max"] == 20.0
    assert s["p50"] == pytest.approx(10.0)
    assert m.latency_pass(s, budget_ms=33.3)
    assert not m.latency_pass({"p99": 34.0}, budget_ms=33.3)
    with pytest.raises(ValueError):
        m.latency_summary(samples, warmup=160)


def test_occlusion_conditional_p99():
    samples = np.full(100, 10.0)
    active = np.zeros(100, dtype=bool)
    assert math.isnan(m.occlusion_conditional_p99(samples, active))
    active[40:60] = True
    samples[40:60] = 50.0                   # only blows budget while active
    p99 = m.occlusion_conditional_p99(samples, active)
    assert p99 == pytest.approx(50.0)
    assert m.latency_summary(samples, warmup=0)["p50"] == 10.0
    with pytest.raises(ValueError):
        m.occlusion_conditional_p99(samples, active[:50])


def test_honesty_perfect_run():
    t_n = 100
    status = np.full((t_n, N_GROUPS), m.MEASURED)
    status[20:50, 1] = m.ESTIMATED
    res = m.honesty_confusion(status, [(1, 20, 50)], slop=2)
    assert res["false_measured"] == 0.0
    assert res["estimated_coverage"] == 1.0
    assert res["matrix"][0, m.MEASURED] == 0
    assert res["judged_occluded"] == 30 - 2 * 2  # slop trims both ends


def test_honesty_false_measured_and_slop():
    t_n = 100
    status = np.full((t_n, N_GROUPS), m.MEASURED)
    status[20:50, 1] = m.ESTIMATED
    status[35, 1] = m.MEASURED              # mid-window lie: counted
    res = m.honesty_confusion(status, [(1, 20, 50)], slop=2)
    assert res["matrix"][0, m.MEASURED] == 1
    assert res["false_measured"] == pytest.approx(1.0 / 26.0)

    status[35, 1] = m.ESTIMATED
    status[21, 1] = m.MEASURED              # within slop: not judged
    res = m.honesty_confusion(status, [(1, 20, 50)], slop=2)
    assert res["matrix"][0, m.MEASURED] == 0


def test_rank_strategies_gates_and_tie_break():
    scores = {
        "a": {"e_occ_wrist_long": 1.0, "e_reacq_hip": 5.0},
        "b": {"e_occ_wrist_long": 2.0, "e_reacq_hip": 4.0},
        "c": {"e_occ_wrist_long": 0.1, "e_reacq_hip": 0.1},
    }
    gates = {
        "a": {"latency_p99": True, "teleport_zero": True},
        "b": {"latency_p99": True, "teleport_zero": True},
        "c": {"latency_p99": True, "teleport_zero": False},
    }
    res = m.rank_strategies(scores, gates,
                            tie_break_key="e_occ_wrist_long")
    assert [r["strategy"] for r in res] == ["a", "b", "c"]
    assert res[0]["mean_rank"] == res[1]["mean_rank"] == 1.5
    assert not res[0]["disqualified"]
    assert res[2]["disqualified"]
    assert res[2]["failed_gates"] == ["teleport_zero"]
    assert res[2]["mean_rank"] is None


def test_rank_strategies_mismatched_keys_raise():
    with pytest.raises(ValueError):
        m.rank_strategies({"a": {"k1": 1.0}, "b": {"k2": 1.0}},
                          {"a": {}, "b": {}})


# ---- clean-window metrics (M2, D-026) --------------------------------

SMOOTHNESS = (Path(__file__).resolve().parents[2]
              / "eval/pipeline_smoothness")


def test_second_diff_rms_known_values():
    t = np.arange(50, dtype=float)
    lin = np.tile(3.0 * t[:, None], (1, N_ANGLES))       # constant velocity
    assert np.allclose(m.second_diff_rms(lin), 0.0)
    quad = np.tile(0.5 * t[:, None] ** 2, (1, N_ANGLES))  # d2 = 1 everywhere
    assert np.allclose(m.second_diff_rms(quad), 1.0)
    alt = np.zeros((10, N_ANGLES))
    alt[1::2, 0] = 1.0                                     # d = +-1, d2 = +-2
    assert m.second_diff_rms(alt)[0] == pytest.approx(2.0)
    with pytest.raises(ValueError):
        m.second_diff_rms(np.zeros((2, N_ANGLES)))


def test_second_diff_rms_wraps_the_seam():
    x = np.zeros((20, N_ANGLES))
    wrapped = m.wrap_deg(170.0 + 2.0 * np.arange(20))  # crosses 180
    x[:, 1] = wrapped
    assert np.any(np.abs(np.diff(wrapped)) > 300.0)   # the seam jump
    assert m.second_diff_rms(x)[1] == pytest.approx(0.0, abs=1e-9)


def test_rms_vs_ref():
    ref = np.zeros((4, N_ANGLES))
    out = np.zeros((4, N_ANGLES))
    out[:, 0] = [1.0, -1.0, 1.0, -1.0]
    out[:, 1] = 179.0
    ref[:, 1] = -179.0
    r = m.rms_vs_ref(out, ref)
    assert r[0] == pytest.approx(1.0)
    assert r[1] == pytest.approx(2.0)
    with pytest.raises(ValueError):
        m.rms_vs_ref(out, ref[:3])


def test_best_lag_recovers_shift_and_sign():
    rng = np.random.default_rng(7)
    base = np.cumsum(rng.normal(size=400))
    ref = np.tile(base[:, None], (1, N_ANGLES))
    out = np.zeros_like(ref)
    for j in range(N_ANGLES):
        s = j - 6                        # shifts -6..+6
        out[:, j] = np.roll(base, s)     # out[i] = ref[i - s]: lags by s
    lags, err = m.best_lag(out, ref, max_lag=10)
    assert list(lags) == [j - 6 for j in range(N_ANGLES)]
    # np.roll wraps the ends; the overlap excludes them, so error is 0
    assert np.all(err < 1e-12)
    lag, e = m.best_lag(base, base)
    assert lag == 0 and e == 0.0


def test_best_lag_tie_goes_to_zero():
    z = np.zeros((40, N_ANGLES))
    lags, err = m.best_lag(z, z)
    assert np.all(lags == 0) and np.all(err == 0.0)
    # float64 noise on an identically-zero angle is a tie, not a lag
    rng = np.random.default_rng(3)
    noise = rng.normal(scale=1e-14, size=(40, N_ANGLES))
    lags, err = m.best_lag(noise, z)
    assert np.all(lags == 0) and np.all(err < 1e-12)
    with pytest.raises(ValueError):
        m.best_lag(np.zeros(15), np.zeros(15), max_lag=10)
    with pytest.raises(ValueError):
        m.best_lag(z, z, criterion="median")


def test_ports_reproduce_pinned_smoothness_table():
    """second_diff_rms and best_lag(criterion='mean_abs') reproduce
    eval/pipeline_smoothness/metrics.csv from series_p16.csv (the
    functions are ports of compare_film_vs_live.py)."""
    s_p = SMOOTHNESS / "series_p16.csv"
    m_p = SMOOTHNESS / "metrics.csv"
    if not (s_p.exists() and m_p.exists()):
        pytest.skip("eval/pipeline_smoothness tables not on disk")
    import pandas as pd
    ser = pd.read_csv(s_p)
    tab = pd.read_csv(m_p)
    tab = tab[tab["page"] == 16].set_index(["angle", "series"])
    for angle in ("el_y", "sh_y", "sh_z", "sh_twist"):
        film = ser[f"{angle}_film"].to_numpy()
        for series in ("film", "raw_gated", "live_cpu"):
            x = ser[f"{angle}_{series}"].to_numpy()
            row = tab.loc[(angle, series)]
            assert m.second_diff_rms(x) == pytest.approx(
                row["d2_rms_deg"], abs=6e-5)
            if series == "film":
                continue
            lag, err = m.best_lag(x, film, max_lag=10, criterion="mean_abs")
            assert lag == int(row["best_lag_frames"])
            assert err == pytest.approx(
                row["mean_abs_diff_at_best_lag_deg"], abs=6e-5)


def test_bone_lengths():
    T = 5
    pts = {n: np.zeros((T, 3)) for n in (
        "right_shoulder", "right_elbow", "right_wrist",
        "left_shoulder", "left_elbow", "left_wrist")}
    pts["right_elbow"][:, 0] = 0.3
    pts["right_wrist"][:, 0] = 0.3
    pts["right_wrist"][:, 1] = 0.25
    pts["left_elbow"][:, 2] = -0.28
    pts["left_wrist"][:, 2] = -0.28
    pts["left_wrist"][2] = np.nan
    b = m.bone_lengths(pts)
    assert b.shape == (T, 4)
    assert np.allclose(b[:, 0], 0.3) and np.allclose(b[:, 1], 0.25)
    assert np.allclose(b[:, 2], 0.28)
    assert np.isnan(b[2, 3]) and b[0, 3] == pytest.approx(0.0)
    dev = m.bone_length_deviation(b[:, :3], [0.3, 0.25, 0.28])
    assert np.allclose(dev["p95"], 0.0)


def test_circular_residual_seam_and_offset():
    ref = np.zeros((4, N_ANGLES))
    out = np.zeros((4, N_ANGLES))
    out[:, 0] = [179.0, -179.0, 179.0, -179.0]    # mean 180, std 1
    out[:, 1] = [10.0, 12.0, 10.0, 12.0]          # offset 11 removes mean
    off = np.zeros(N_ANGLES)
    off[1] = 11.0
    mu, sd = m.circular_residual(out, ref, off)
    assert abs(m.wrap_deg(mu[0] - 180.0)) < 1e-9
    assert sd[0] == pytest.approx(1.0)
    assert mu[1] == pytest.approx(0.0, abs=1e-9)
    assert sd[1] == pytest.approx(1.0)

"""D-033 twist-gated teleport count, bend observability and the
injection acceptance rule."""
import numpy as np
import pandas as pd
import pytest

import bench.metrics as m
from bench.oracle import twist_observable

RT, LT = m.ANGLE_NAMES.index("r_twist"), m.ANGLE_NAMES.index("l_twist")


def test_twist_step_valid_needs_both_frames():
    r = np.array([True, True, False, True, True])
    l_ = np.array([True, False, True, True, True])
    v = m.twist_step_valid(r, l_)
    assert v.shape == (4, 13)
    assert list(v[:, RT]) == [True, False, False, True]
    assert list(v[:, LT]) == [False, False, True, True]
    others = [j for j in range(13) if j not in (RT, LT)]
    assert v[:, others].all()


def test_teleport_count_ignores_masked_twist_only():
    steps = np.zeros((4, 13))
    steps[1, RT] = 20.0            # masked twist jump
    budget = np.full(13, 5.0)
    valid = m.twist_step_valid(np.array([1, 1, 0, 1, 1], bool),
                               np.ones(5, bool))
    assert m.teleport_count(steps, budget)["count"] == 1      # D-003
    t = m.teleport_count(steps, budget, valid)
    assert t["count"] == 0 and t["worst_step_deg"] == 0.0
    steps[2, 0] = 6.0              # non-twist angle: never masked
    assert m.teleport_count(steps, budget, valid)["count"] == 1
    with pytest.raises(ValueError):
        m.teleport_count(steps, budget, valid[:2])


def test_budget_skips_nan_steps():
    rng = np.random.default_rng(1)
    s = np.abs(rng.normal(0, 1, (500, 13)))
    ref = m.teleport_budget(s)
    s2 = s.copy()
    s2[:50, RT] = np.nan
    b = m.teleport_budget(s2)
    assert b[RT] == pytest.approx(1.5 * np.percentile(s[50:, RT], 99.9))
    assert np.array_equal(np.delete(b, RT), np.delete(ref, RT))


def _tab(bend_deg):
    n = len(bend_deg)
    d = {"r_twist_ok": np.ones(n, bool), "l_twist_ok": np.ones(n, bool)}
    for sd in ("right", "left"):
        b = np.radians(np.asarray(bend_deg, float))
        pts = {"shoulder": np.zeros((n, 3)),
               "elbow": np.tile([0.3, 0.0, 0.0], (n, 1)),
               "wrist": np.stack([0.3 + 0.25 * np.cos(b),
                                  0.25 * np.sin(b), np.zeros(n)], 1)}
        for j, arr in pts.items():
            for c, ax in enumerate("xyz"):
                d[f"{sd}_{j}_f{ax}"] = arr[:, c]
    return pd.DataFrame(d)


def test_twist_observable_bend_threshold():
    tab = _tab([0.0, 29.0, 31.0, 90.0, 150.0])
    r, l_ = twist_observable(tab, 30)
    assert list(r) == [False, False, True, True, True]
    assert list(l_) == list(r)
    r0, _ = twist_observable(tab, None)       # solver twist_ok alone
    assert r0.all()
    tab.loc[4, "right_wrist_fx"] = np.nan
    r, _ = twist_observable(tab, 30)
    assert not r[4]


def test_injection_of_1p5_budget_step_fails_gate():
    # the injection rule of bench/teleport_rule_check.py on a synthetic
    # track: a step function of 1.5 x budget always trips the gate when
    # the natural step is below 0.5 x budget
    budget = np.full(13, 4.0)
    A = np.cumsum(np.full((50, 13), 0.5), axis=0)
    base = m.teleport_count(m.angle_steps(A), budget)
    assert base["count"] == 0
    j = m.ANGLE_NAMES.index("r_swing_z")
    A[25:, j] += 1.5 * budget[j]
    t = m.teleport_count(m.angle_steps(A), budget)
    assert t["count"] == 1 and t["per_angle_counts"][j] == 1


# -- review finding 1: the bend threshold is required, never defaulted --

def _cfg():
    import json
    from pathlib import Path
    return json.loads((Path(__file__).resolve().parents[1]
                       / "configs/default.json").read_text())


def test_pinned_config_and_manifest_carry_min_bend():
    import json
    from bench.oracle import require_twist_min_bend
    from bench.paths import repo_path
    cfg = _cfg()
    assert require_twist_min_bend(cfg["budget"], "config") == 30
    man = json.loads(repo_path(cfg["paths"]["scenario_manifest"])
                     .read_text())
    assert man["teleport_twist_gate"] == "oracle_twist_ok"
    assert require_twist_min_bend(man, "manifest") == 30


@pytest.mark.parametrize("bad", [{}, {"twist_min_bend_deg": None}])
def test_require_twist_min_bend_raises_on_missing_or_null(bad):
    from bench.oracle import require_twist_min_bend
    with pytest.raises(ValueError, match="twist_min_bend_deg"):
        require_twist_min_bend(bad, "test")


def test_make_scenarios_oracle_union_raises_without_min_bend():
    from bench.make_scenarios import oracle_union_steps
    cfg = _cfg()
    del cfg["budget"]["twist_min_bend_deg"]
    with pytest.raises(ValueError, match="twist_min_bend_deg"):
        oracle_union_steps(None, cfg, "unused.csv", 60)


def test_grade_twist_gate_raises_without_min_bend():
    from bench.grade import twist_gate_mask
    man = {"teleport_twist_gate": "oracle_twist_ok"}
    with pytest.raises(ValueError, match="twist_min_bend_deg"):
        twist_gate_mask(man, "unused.csv", _cfg())
    # the ungated D-003 manifests need no threshold
    assert twist_gate_mask({"teleport_twist_gate": "none"}, "unused.csv",
                           _cfg()) is None

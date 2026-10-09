"""Config guards (Phase 0). The configs are the single source of every
tunable; these tests pin the plan's values and enforce D-006 (nulls are
deliberate placeholders until their phase fills them from a sourced
run)."""
import json
from pathlib import Path

import pytest

from bench import metrics as m

V3_ROOT = Path(__file__).resolve().parents[1]
CONFIGS = V3_ROOT / "configs"


@pytest.fixture(scope="module")
def default_cfg():
    with open(CONFIGS / "default.json") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def bench_cfg():
    with open(CONFIGS / "bench.json") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def scenarios_cfg():
    with open(CONFIGS / "scenarios_20260224.json") as f:
        return json.load(f)


def test_default_has_all_schema_blocks(default_cfg):
    for key in ("paths", "model", "detect", "depth", "gate", "filter",
                "strategy", "status", "budget", "joint_limits", "bones"):
        assert key in default_cfg, f"missing block: {key}"


def test_paths_bag_is_absolute(default_cfg):
    assert Path(default_cfg["paths"]["bag"]).is_absolute()


def test_detect_values_match_plan(default_cfg):
    d = default_cfg["detect"]
    assert d["det_freq"] == 15
    assert d["margin"] == 0.25
    assert d["kpt_min_score"] == 0.3
    assert d["reacquire_score"] == 0.35
    assert d["reacquire_frames"] == 2
    assert d["box_area_jump"] == 2.0


def test_filter_matches_v1_causal_constants(default_cfg):
    # v1's LIVE tuning (realtime_person.py CausalLandmarkFilter), not
    # the offline 0.05 Hz cutoff, which v1 measured at ~9 frames of
    # lag in the causal setting (D-015)
    f = default_cfg["filter"]
    assert f["freq_hz"] == 30.0
    assert f["min_cutoff"] == 1.0
    assert f["beta"] == 1.0
    assert f["d_cutoff"] == 1.0
    assert f["despike_window"] == 11
    assert f["despike_k"] == 3.0
    assert f["despike_abs_floor_m"] == 0.035
    assert f["despike_max_rejects"] == 3


def test_budget_values_match_plan(default_cfg):
    b = default_cfg["budget"]
    assert b["frame_ms"] == 33.3
    assert b["recovery_deg"] == 5.0
    assert b["recovery_sustain_frames"] == 3
    assert b["reacq_k"] == 5
    assert b["teleport_safety"] == 1.5
    assert b["false_measured_max"] == 0.01
    assert b["honesty_boundary_slop_frames"] == 2


def test_depth_status_bones(default_cfg):
    assert default_cfg["depth"]["window"] == 5
    assert default_cfg["status"]["lost_after_frames"] == 30
    assert default_cfg["bones"]["calibrate_frames"] == 60


def test_gate_thresholds_are_null_until_phase3(default_cfg):
    g = default_cfg["gate"]
    for cls in ("shoulder", "elbow", "wrist", "hip"):
        assert g["score_thresholds"][cls] is None
    assert g["depth_front_margin_m"] == 0.25
    assert g["velocity_max_m_s"] == 4.0


@pytest.fixture(scope="module")
def variants_cfg():
    with open(CONFIGS / "model_variants.json") as f:
        return json.load(f)["variants"]


def test_model_paths_pinned_and_exist(default_cfg, variants_cfg):
    """The variant named in default.json exists in model_variants.json,
    the model block agrees with that entry field by field, and its
    files are on disk (D-023; generalises the D-008 rtmpose-m pin)."""
    mo = default_cfg["model"]
    assert mo["variant"] in variants_cfg, (
        f"default variant {mo['variant']!r} not in model_variants.json")
    entry = variants_cfg[mo["variant"]]
    for key in ("backend", "pose_onnx", "pose_input_size_wh", "det_onnx",
                "det_input_size_wh"):
        assert mo[key] == entry[key], (
            f"default.json model.{key} disagrees with variant table")
    repo = V3_ROOT.parent
    for key in ("det_onnx", "pose_onnx"):
        if entry["backend"] == "rtmo" and key == "det_onnx":
            continue
        assert mo[key] is not None
        assert (repo / mo[key]).exists(), f"{key} not on disk: {mo[key]}"
    assert mo["providers"][0] == "CUDAExecutionProvider"
    for d in mo["cuda_lib_dirs"]:
        assert Path(d).is_dir(), f"cuda lib dir missing: {d}"


def test_variant_table_schema(variants_cfg):
    from detector.factory import BACKENDS
    for name, v in variants_cfg.items():
        assert v["backend"] in BACKENDS, name
        assert v["pose_onnx"] and len(v["pose_sha256"]) == 64, name
        assert v["pose_size_bytes"] > 0, name
        assert len(v["pose_input_size_wh"]) == 2, name
        if v["backend"] == "rtmo":
            assert v["det_onnx"] is None, name
        else:
            assert v["det_onnx"] and len(v["det_sha256"]) == 64, name
            assert v["det_size_bytes"] > 0, name
            assert len(v["det_input_size_wh"]) == 2, name


# Pinned variants, one row per decision: (name, backend, pose input
# (w, h), det input (w, h), pose file stem, det file stem). rtmpose-m is
# the D-008 default kept under its original name; rtmpose-x_yolox-m is
# the M3 pin (D-028, dataset/phase5_pose_sweep.txt), kept as history;
# rtmpose-l is the D-034 re-pin (dataset/phase5_pose_sweep_recapped.txt).
PINNED_VARIANTS = [
    ("rtmpose-m", "rtmpose", [192, 256], [416, 416],
     "rtmpose-m_simcc-body7", "yolox_tiny"),
    ("rtmpose-x_yolox-m", "rtmpose", [288, 384], [640, 640],
     "rtmpose-x_simcc-body7", "yolox_m"),
    ("rtmpose-l", "rtmpose", [288, 384], [416, 416],
     "rtmpose-l_simcc-body7", "yolox_tiny"),
]
DEFAULT_VARIANT = "rtmpose-l"   # D-034 (reverses D-028, supersedes D-008 pose)


@pytest.mark.parametrize("name,backend,pose_wh,det_wh,pose_stem,det_stem",
                         PINNED_VARIANTS)
def test_variant_table_keeps_pins(variants_cfg, name, backend, pose_wh,
                                  det_wh, pose_stem, det_stem):
    """Every pinned variant stays in the table with its decision's
    input sizes and model files."""
    v = variants_cfg[name]
    assert v["backend"] == backend
    assert v["pose_input_size_wh"] == pose_wh
    assert v["det_input_size_wh"] == det_wh
    assert pose_stem in v["pose_onnx"]
    assert det_stem in v["det_onnx"]


def test_default_variant_is_d034_pin(default_cfg):
    """default.json names the D-034 variant and the D-033 oracle_union
    scenario manifest derived on that variant's extraction."""
    assert default_cfg["model"]["variant"] == DEFAULT_VARIANT
    man = json.loads((V3_ROOT.parent / default_cfg["paths"][
        "scenario_manifest"]).read_text())
    assert man["variant"] == DEFAULT_VARIANT
    assert not Path(man["base_csv"]).is_absolute()
    assert all(not Path(s["csv"]).is_absolute() for s in man["scenarios"])
    assert man["teleport_budget_source"] == "oracle_union"
    assert man["teleport_twist_gate"] == "oracle_twist_ok"


def test_joint_limits_cover_all_13_angles(default_cfg):
    jl = default_cfg["joint_limits"]
    for name in m.ANGLE_NAMES:
        assert name in jl, f"missing joint_limits entry: {name}"
        lim = jl[name]
        assert lim is None or (len(lim) == 2 and lim[0] < lim[1])


def test_strategy_blocks_exist(default_cfg):
    s = default_cfg["strategy"]
    assert s["name"] == "baseline_hold"
    for block in ("baseline_hold", "s1_constraint_projection",
                  "s2_quat_prediction", "s3_partial_ik",
                  "s4_multi_hypothesis", "s5_confidence_blend"):
        assert block in s
    assert s["s2_quat_prediction"]["decay_lambda"] == 0.8
    assert s["s1_constraint_projection"]["max_iters"] == 5


def test_bench_ranking_rule_frozen(bench_cfg):
    r = bench_cfg["ranking"]
    assert r["hard_gates"] == ["latency_p99", "teleport_zero",
                               "honesty_false_measured"]
    assert r["tie_break_scenario"] == "wrist_long"
    assert bench_cfg["latency"]["budget_ms"] == 33.3
    assert bench_cfg["latency"]["warmup_frames"] == 60
    assert bench_cfg["sweep"]["det_freq_values"] == [5, 15, 30]


def test_scenarios_schema(scenarios_cfg):
    names = [s["name"] for s in scenarios_cfg["scenarios"]]
    assert len(names) == len(set(names))
    assert set(scenarios_cfg["mask_modes"]) == {"nan", "low_conf"}
    spans = []
    for s in scenarios_cfg["scenarios"]:
        assert s["type"] in scenarios_cfg["types"]
        assert s["duration_frames"] > 0
        # windows were derived on the V3 extraction (make_scenarios,
        # D-019); they must be filled, consistent, and disjoint
        assert s["stop"] - s["start"] == s["duration_frames"]
        assert all(g in ("root", "R_swing", "R_twist", "R_elbow",
                         "L_swing", "L_twist", "L_elbow")
                   for g in s["expected_groups"])
        spans.append((s["start"], s["stop"]))
    for a, b in zip(sorted(spans), sorted(spans)[1:]):
        assert a[1] <= b[0], f"overlapping windows: {a} {b}"
    budgets = scenarios_cfg["teleport_budget_deg"]
    assert set(budgets) == set(m.ANGLE_NAMES)
    # identically-zero angles carry the 1e-9 floor, not 0 (float64
    # noise must not count as teleports)
    assert all(b >= 1e-9 for b in budgets.values())
    assert scenarios_cfg["derived_from_commit"]


def test_tie_break_scenario_exists(bench_cfg, scenarios_cfg):
    names = {s["name"] for s in scenarios_cfg["scenarios"]}
    assert bench_cfg["ranking"]["tie_break_scenario"] in names

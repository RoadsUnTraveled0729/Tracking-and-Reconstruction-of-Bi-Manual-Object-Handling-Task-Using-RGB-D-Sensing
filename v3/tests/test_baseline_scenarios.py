"""Baseline behavior over the S-type scenarios (the v1 33-check
suite's structure, ported to the V3 extraction). Skips when the
extraction or scenarios are absent (fresh clone: run
tools/extract_bag_to_csv.py then bench/make_scenarios.py first)."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from bench import metrics as m
from replay.runner import run_csv
from strategies.strategy_base import build
import strategies.baseline_hold  # noqa: F401  registers

from bench.grade import twist_gate_mask
from bench.paths import repo_path

V3_ROOT = Path(__file__).resolve().parents[1]
_cfg = json.loads((V3_ROOT / "configs/default.json").read_text())
# the manifest follows the pinned model variant (D-028)
MANIFEST = repo_path(_cfg["paths"]["scenario_manifest"])

_man = json.loads(MANIFEST.read_text())
_ready = (_man.get("base_csv") and repo_path(_man["base_csv"]).exists()
          and all(repo_path(s.get("csv", "")).exists()
                  for s in _man["scenarios"]))
pytestmark = pytest.mark.skipif(
    not _ready, reason="V3 extraction/scenarios not generated on this "
                       "machine (run extract_bag_to_csv + make_scenarios)")


@pytest.fixture(scope="module")
def cfg():
    return json.loads((V3_ROOT / "configs/default.json").read_text())


@pytest.fixture(scope="module")
def truth(cfg):
    return run_csv(str(repo_path(_man["base_csv"])), cfg,
                   build("baseline_hold", cfg))


@pytest.fixture(scope="module")
def runs(cfg):
    out = {}
    for scn in _man["scenarios"]:
        out[scn["name"]] = run_csv(str(repo_path(scn["csv"])), cfg,
                                   build("baseline_hold", cfg))
    return out


def scn(name):
    return next(s for s in _man["scenarios"] if s["name"] == name)


@pytest.mark.parametrize("name", [s["name"] for s in _man["scenarios"]])
def test_honesty_is_perfect(name, runs, cfg):
    """nan-mode masking must never produce a false MEASURED."""
    s = scn(name)
    g_idx = [m.GROUP_NAMES.index(g) for g in s["expected_groups"]]
    status = runs[name][[f"status_{g}" for g in m.GROUP_NAMES]].to_numpy()
    hon = m.honesty_confusion(status,
                              [(g, s["start"], s["stop"]) for g in g_idx],
                              cfg["budget"]["honesty_boundary_slop_frames"])
    assert hon["false_measured"] == 0.0


@pytest.mark.parametrize("name", [s["name"] for s in _man["scenarios"]])
def test_masked_groups_not_measured_inside_window(name, runs):
    s = scn(name)
    df = runs[name]
    inside = (df["frame"] >= s["start"] + 1) & (df["frame"] < s["stop"])
    for g in s["expected_groups"]:
        vals = df.loc[inside, f"status_{g}"].to_numpy()
        assert np.all(vals != m.MEASURED), (name, g)


@pytest.mark.parametrize("name", [s["name"] for s in _man["scenarios"]])
def test_recovery_after_window(name, runs, truth):
    """Once landmarks return (allowing the despike re-seed horizon of
    max_rejects + 1 frames), the masked groups' statuses match the
    truth run's again -- MEASURED except where the truth run itself
    has a natural despike rejection -- and MEASURED actually occurs."""
    s = scn(name)
    df = runs[name]
    back = (df["frame"] >= s["stop"] + 4) & (df["frame"] < s["stop"] + 20)
    for g in s["expected_groups"]:
        got = df.loc[back, f"status_{g}"].to_numpy()
        want = truth.loc[back, f"status_{g}"].to_numpy()
        assert np.array_equal(got, want), (name, g)
        assert np.any(got == m.MEASURED), (name, g)


def test_lost_after_threshold_in_long_windows(runs, cfg):
    """45-frame windows: ESTIMATED for lost_after frames, LOST after."""
    lost_after = cfg["status"]["lost_after_frames"]
    for name in ("wrist_long", "elbow_long"):
        s = scn(name)
        df = runs[name].set_index("frame")
        g = s["expected_groups"][-1]
        # first masked frame = held count 1; ESTIMATED while held <=
        # lost_after, so frames start .. start+lost_after-1, LOST from
        # start+lost_after (pandas .loc ranges are inclusive)
        assert (df.loc[s["start"]:s["start"] + lost_after - 1,
                       f"status_{g}"] == m.ESTIMATED).all(), name
        assert (df.loc[s["start"] + lost_after:s["stop"] - 1,
                       f"status_{g}"] == m.LOST).all(), name


def test_unaffected_side_matches_truth_exactly(runs, truth):
    """Masking the right wrist must not change the left arm or the
    root by one bit: identical pipeline, identical inputs there."""
    s = scn("wrist_long")
    df = runs["wrist_long"]
    for col in ("l_swing_y", "l_swing_z", "l_twist", "l_elbow_y",
                "root_x", "root_y", "root_z", "r_swing_y", "r_swing_z"):
        assert np.array_equal(df[col].to_numpy(),
                              truth[col].to_numpy()), col
    for g in ("root", "L_swing", "L_twist", "L_elbow", "R_swing"):
        assert (df[f"status_{g}"] == truth[f"status_{g}"]).all(), g


def test_held_angles_are_frozen_inside_window(runs):
    """The baseline HOLDS: masked-group angles constant during the
    mask (this is the behavior strategies must improve on)."""
    s = scn("elbow_long")
    df = runs["elbow_long"].set_index("frame")
    span = df.loc[s["start"] + 1:s["stop"] - 1]
    for col in ("r_swing_y", "r_swing_z", "r_twist", "r_elbow_y"):
        assert span[col].nunique() == 1, col


def test_root_survives_via_left_shoulder(runs, truth):
    """root_ref scenario: right shoulder masked, root stays MEASURED
    (left shoulder selects the coronal plane), right arm holds."""
    s = scn("root_ref")
    df = runs["root_ref"].set_index("frame")
    span = df.loc[s["start"] + 1:s["stop"] - 1]
    assert (span["status_root"] == m.MEASURED).all()
    assert (span["status_R_swing"] != m.MEASURED).all()


# Pinned baseline_hold teleport outcomes per scenario manifest (the
# grade tables' headline behavior): None = at least one teleport. The
# pre-M3 manifest (rtmpose-m, D-019) is dataset/phase3_baseline_grade.txt;
# the M3 manifest (rtmpose-x_yolox-m, D-028) is
# dataset/phase5_s_grade__rtmpose-x_yolox-m.txt; the D-034 manifest
# (rtmpose-l, D-033 oracle_union budgets, twist steps gated by the
# oracle bend mask) is dataset/phase5_s_grade__rtmpose-l.txt.
BASELINE_TELEPORTS = {
    "scenarios_20260224.json":
        {"wrist_short": 0, "wrist_long": 0, "elbow_long": None,
         "root_ref": None},
    "scenarios_20260224__rtmpose-x_yolox-m.json":
        {"wrist_short": 0, "wrist_long": 1, "elbow_long": 1,
         "pose_loss": 2, "root_ref": 2, "hip": 0},
    "scenarios_20260224__rtmpose-l__oracle_union.json":
        {"wrist_short": 0, "wrist_long": 0, "elbow_long": 0, "hip": 0,
         "pose_loss": 1, "root_ref": 0},
}


@pytest.mark.parametrize("manifest", sorted(BASELINE_TELEPORTS))
def test_baseline_grade_evidence_is_current(cfg, manifest):
    """The pinned grade table's headline behavior reproduces for each
    manifest: baseline_hold teleport counts per scenario (the
    reacquisition snaps strategies must fix)."""
    man = json.loads((V3_ROOT / "configs" / manifest).read_text())
    base = repo_path(man["base_csv"])
    if not base.exists() or not all(repo_path(s["csv"]).exists()
                                    for s in man["scenarios"]):
        pytest.skip(f"{manifest}: extraction or masked CSVs absent")
    budgets = np.array([man["teleport_budget_deg"][a]
                        for a in m.ANGLE_NAMES])
    warmup = json.loads((V3_ROOT / "configs/bench.json").read_text())[
        "latency"]["warmup_frames"]
    by_name = {s["name"]: s for s in man["scenarios"]}
    for name, want in BASELINE_TELEPORTS[manifest].items():
        df = run_csv(str(repo_path(by_name[name]["csv"])), cfg,
                     build("baseline_hold", cfg))
        A = df[list(m.ANGLE_NAMES)].to_numpy()
        # D-033 manifests gate twist steps by the oracle bend mask, as
        # bench/grade.py does; D-003 manifests count every step
        valid = twist_gate_mask(man, base, cfg)
        got = m.teleport_count(m.angle_steps(A)[warmup:], budgets,
                               None if valid is None
                               else valid[warmup:])["count"]
        if want is None:
            assert got >= 1, (manifest, name, got)
        else:
            assert got == want, (manifest, name, got)

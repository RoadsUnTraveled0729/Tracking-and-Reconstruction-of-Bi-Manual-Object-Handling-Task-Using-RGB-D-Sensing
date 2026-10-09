"""bench/holding.py: constants match the thesis sources, the thesis R4
hold runs are reproduced from the MediaPipe-era inputs, and the state
machine / run split behave as their sources (D-036)."""
import json
import re

import numpy as np
import pandas as pd
import pytest

from bench import aruco_source as src
from bench import holding as H

REPO = src.REPO


def _const(path, name):
    txt = (REPO / path).read_text()
    m = re.search(rf"^{name}\s*=\s*([0-9.]+)", txt, re.M)
    assert m, f"{name} not found in {path}"
    return float(m.group(1))


def test_constants_match_thesis_sources():
    if not (REPO / "eval/offset/carry.py").exists():
        pytest.skip("eval/ sources absent")
    c = H.CONFIG
    assert c["hold_radius_m"] == _const("eval/offset/carry.py", "HOLD_RADIUS")
    assert c["forearm_tol"] == _const("eval/offset/carry.py", "FOREARM_TOL")
    assert c["rest_dist_m"] == _const("eval/offset/carry.py", "REST_DIST")
    assert c["move_k_frames"] == _const("eval/offset/carry.py", "K")
    assert c["move_dist_m"] == _const("eval/offset/carry.py", "MOVE_DIST")
    assert c["carry_height_m"] == _const("eval/offset/carry.py",
                                         "CARRY_HEIGHT")
    gs = "eval/failure/grip_state.py"
    assert c["enter_frames"] == _const(gs, "ENTER_FRAMES")
    assert c["exit_frames"] == _const(gs, "EXIT_FRAMES")
    assert c["release_radius_m"] == _const(gs, "RELEASE_RADIUS")


def test_reproduces_thesis_r4_hold_runs():
    """eval/reports/r4_stage4_ground_truth.md stage-2 constancy table:
    right 254-388 (n 134, med 14.3, std 0.64), 478-713 (235, 14.6,
    1.54), 1028-1112 (85, 17.0, 2.04); left 674-832 (158, 13.4, 1.87);
    per hand held 494 / 158, |wrist - centre| med/p95 14.6/17.9 and
    13.4/17.3 cm. Inputs as analyze_offset_constancy.py loads them."""
    stem = src.STEMS["r4"]
    lm_csv = REPO / "v1/mediapipe/output" / f"{stem}_landmarks_filtered.csv"
    of_csv = src.EVAL_OUT / f"{stem}_scaled_object_world_filtered.csv"
    ins = src.inspection_path(stem)
    for p in (lm_csv, of_csv, ins, src.calib_path("r4")):
        if not p.exists():
            pytest.skip(f"thesis input absent: {p}")
    world = src.load_world("r4")
    lm = pd.read_csv(lm_csv)
    of = pd.read_csv(of_csv)
    n = min(len(lm), len(of))
    lm, of = lm.iloc[:n], of.iloc[:n]
    obj, R = world.object_world(
        of[["unity_px", "unity_py", "unity_pz"]].to_numpy(),
        of[["unity_ex", "unity_ey", "unity_ez"]].to_numpy())
    det = of["detected"].to_numpy() == 1
    c = world.box_center(obj, R)
    env = json.loads(ins.read_text())["phases"]["manipulation"]
    carried = H.rest_referenced_carried(obj, world.height_above_table(obj),
                                        env)
    expect = {"right": ([(254, 388, 134, 14.3, 0.64),
                         (478, 713, 235, 14.6, 1.54),
                         (1028, 1112, 85, 17.0, 2.04)], 494, 14.6, 17.9),
              "left": ([(674, 832, 158, 13.4, 1.87)], 158, 13.4, 17.3)}
    for side, (runs_x, held_x, med_x, p95_x) in expect.items():
        cols = [f"{side}_wrist_{a}" for a in "xyz"]
        ecols = [f"{side}_elbow_{a}" for a in "xyz"]
        wr = world.world_from_cam(lm[cols].to_numpy())
        f_ok = H.forearm_ok(lm[ecols].to_numpy(), lm[cols].to_numpy())
        hold = H.holding_mask(c, wr, lm[f"{side}_wrist_flag"].to_numpy() == 0,
                              det, carried, f_ok)
        m = np.linalg.norm(wr - c, axis=1)
        assert int(hold.sum()) == held_x
        assert round(float(np.median(m[hold])) * 100, 1) == med_x
        assert round(float(np.percentile(m[hold], 95)) * 100, 1) == p95_x
        runs = H.hold_runs(hold)
        assert [(a, b, k) for a, b, k in runs] == \
            [(a, b, k) for a, b, k, _, _ in runs_x]
        idx = np.flatnonzero(hold)
        for (a, b, _), (*_, med, sd) in zip(runs, runs_x):
            e = idx[(idx >= a) & (idx <= b)]
            assert round(float(np.median(m[e])) * 100, 1) == med
            assert round(float(np.std(m[e])) * 100, 2) == sd


def test_grip_episodes_enter_exit():
    n = 40
    hold = np.zeros(n, bool)
    hold[5:15] = True
    carried = np.ones(n, bool)
    carried[25:] = False
    dist = np.full(n, 0.1)
    clean = np.ones(n, bool)
    holding, eps = H.grip_episodes(hold, carried, dist, clean)
    # enters at frame 5 after 5 clean frames, stays through the gap,
    # exits after 5 not-carried frames: stop = 29 - 5 = 24
    assert eps == [(5, 24)]
    assert holding[5:25].all() and not holding[25:].any()
    hold2 = hold.copy()
    hold2[5:9] = True
    hold2[9:] = False
    _, eps2 = H.grip_episodes(hold2, carried, dist, clean)
    assert eps2 == []


def test_hold_runs_gap_and_min():
    hold = np.zeros(200, bool)
    hold[10:50] = True          # 40 frames
    hold[60:80] = True          # gap 10 <= 15: same run
    hold[100:120] = True        # gap 20 > 15: new run of 20 < 30: dropped
    assert H.hold_runs(hold) == [(10, 79, 60)]

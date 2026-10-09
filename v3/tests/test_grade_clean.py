"""Tests for bench/grade_clean.py helpers (D-026) and a one-window
smoke run that skips when the gitignored clean extractions are absent."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from bench import grade_clean as gc
from bench import metrics as m

V3_ROOT = Path(__file__).resolve().parents[1]


def test_read_offsets_matches_pinned_d018_table():
    off = gc.read_offsets(V3_ROOT / "dataset/phase3_v1_offset_table.txt")
    assert off.shape == (13,)
    idx = {a: i for i, a in enumerate(m.ANGLE_NAMES)}
    # D-018 headline values
    assert off[idx["root_y"]] == pytest.approx(-7.61)
    assert off[idx["r_swing_y"]] == pytest.approx(9.03)
    assert off[idx["l_swing_y"]] == pytest.approx(-9.45)
    assert off[idx["r_elbow_z"]] == pytest.approx(0.0)


def test_v1_agreement_recovers_lag_and_offset():
    rng = np.random.default_rng(11)
    ref = np.cumsum(rng.normal(size=300))
    x = np.roll(ref, 2) + 9.0 + rng.normal(scale=0.1, size=300)
    lag, mu, sd = gc.v1_agreement(x, ref, 9.0, max_lag=10)
    assert lag == 2
    assert abs(mu) < 0.05
    assert sd == pytest.approx(0.1, abs=0.03)


def test_bone_p95_ignores_rejected_frames():
    T = 20
    pts = {n: np.zeros((T, 3)) for n in (
        "right_shoulder", "right_elbow", "right_wrist",
        "left_shoulder", "left_elbow", "left_wrist")}
    for n, x in (("right_elbow", 0.3), ("right_wrist", 0.55),
                 ("left_elbow", -0.3), ("left_wrist", -0.55)):
        pts[n][:, 0] = x
    pts["right_wrist"][5] = np.nan
    p95 = gc.bone_p95(pts, np.array([0.3, 0.25, 0.3, 0.25]))
    assert np.all(np.isfinite(p95))
    assert np.allclose(p95, 0.0)


def test_unknown_smoother_rejected(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "argv", ["grade_clean.py", "--smoothers",
                                      "no_such_smoother",
                                      "--out-txt", str(tmp_path / "x.txt")])
    with pytest.raises(SystemExit):
        gc.main()


def test_smoke_one_window(monkeypatch, tmp_path):
    win = json.loads((V3_ROOT / "configs/clean_windows.json").read_text())
    w = [x for x in win["windows"] if x["name"] == "180042"][0]
    csv = (V3_ROOT / "output/clean"
           / f"extraction_{Path(w['bag']).stem}__rtmpose-m.csv")
    if not csv.exists():
        pytest.skip("clean extraction not on disk (v3/output is gitignored)")
    out_txt, out_csv = tmp_path / "t.txt", tmp_path / "t.csv"
    monkeypatch.setattr(sys, "argv", [
        "grade_clean.py", "--strategies", "baseline_hold", "--windows",
        "180042", "--out-txt", str(out_txt), "--out-csv", str(out_csv)])
    gc.main()
    df = pd.read_csv(out_csv)
    assert len(df) == 13
    assert set(df["angle"]) == set(m.ANGLE_NAMES)
    assert np.all(np.isfinite(df["rms_vs_oracle_lag0"]))
    assert df.loc[df["angle"] == "r_elbow_z", "best_lag"].item() == 0
    assert "v1 agreement (eval/pipeline_smoothness/series_p14.csv)" \
        in out_txt.read_text()

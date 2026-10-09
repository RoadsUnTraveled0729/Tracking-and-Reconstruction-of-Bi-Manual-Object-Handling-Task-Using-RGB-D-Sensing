"""bench/grade_wrist_object.py smoke run on R6b (skips when the V3
object extraction or the thesis ArUco inputs are absent)."""
import json
import subprocess
import sys

import pandas as pd
import pytest

from bench import aruco_source as src

V3 = src.V3_ROOT


def test_smoke_r6b(tmp_path):
    cfg = json.loads((V3 / "configs/default.json").read_text())
    variant = cfg["model"]["variant"]
    stem = src.STEMS["r6b"]
    csv = V3 / "output/objects" / f"extraction_{stem}__{variant}.csv"
    for p in (csv, src.aruco_csv(stem), src.calib_path("r6b"),
              src.inspection_path(stem)):
        if not p.exists():
            pytest.skip(f"input absent: {p}")
    txt, out_csv = tmp_path / "w.txt", tmp_path / "w.csv"
    r = subprocess.run(
        [sys.executable, str(V3 / "bench/grade_wrist_object.py"),
         "--recordings", "r6b", "--strategies", "baseline_hold",
         "--smoothers", "none", "--variant", variant,
         "--out-txt", str(txt), "--out-csv", str(out_csv)],
        capture_output=True, text=True, cwd=str(V3))
    assert r.returncode == 0, r.stderr[-2000:]
    text = txt.read_text()
    assert "-> PASS" in text
    res = pd.read_csv(out_csv)
    right = res[(res.hand == "right")]
    assert set(right.series) == {"measured", "oracle", "baseline_hold"}
    assert (right.n_hold > 100).all()
    a = right[(right.series == "oracle") & (right.anchor == "a")].iloc[0]
    assert 0.0 < a.err_med_m < 0.05

"""Unit tests for path_metrics (run: python eval/gt/test_path_metrics.py)."""

import json
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import path_metrics as pm

FAIL = []


def check(name, ok):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    if not ok:
        FAIL.append(name)


def test_point_to_segment():
    d, t, r = pm.point_to_segment([0, 1, 0], [0, 0, 0], [2, 0, 0])
    check("perpendicular distance", abs(d - 1.0) < 1e-12 and abs(t) < 1e-12)
    d, t, r = pm.point_to_segment([1, 1, 0], [0, 0, 0], [2, 0, 0])
    check("interior projection", abs(d - 1.0) < 1e-12 and abs(t - 0.5) < 1e-12
          and np.allclose(r, [0, 1, 0]))
    d, t, r = pm.point_to_segment([3, 0, 4], [0, 0, 0], [2, 0, 0])
    check("clamped to endpoint", abs(d - np.sqrt(1 + 16)) < 1e-12
          and t == 1.0)
    d, t, r = pm.point_to_segment([1, 2, 2], [1, 0, 0], [1, 0, 0])
    check("degenerate segment", abs(d - np.sqrt(8)) < 1e-12)


def test_path():
    spec = {
        "frame": "desk_marker_world", "units": "m",
        "survey": {"method": "t", "date": None, "default_sigma_m": 0.002},
        "waypoints": [
            {"id": "A", "xyz": [0, 0, 0], "sigma_m": None,
             "dwell_expected": True},
            {"id": "B", "xyz": [1, 0, 0], "sigma_m": None,
             "dwell_expected": True},
            {"id": "C", "xyz": [1, 1, 0], "sigma_m": None,
             "dwell_expected": True},
        ],
        "segments": [
            {"from": "A", "to": "B", "type": "line",
             "constrained_axes": ["y", "z"]},
            {"from": "B", "to": "C", "type": "line",
             "constrained_axes": ["x", "z"]},
        ],
        "wall_marker_surveyed": {"xyz": None, "sigma_m": None},
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(spec, f)
        name = f.name
    loaded = pm.load_path(name)
    check("load_path complete flag", loaded["complete"] is True)
    i, d, r, per_axis = pm.point_to_path([0.5, 0.1, 0.0], loaded)
    check("nearest segment is A-B", i == 0 and abs(d - 0.1) < 1e-12)
    check("per-axis masks to constrained axes",
          set(per_axis) == {"y", "z"} and abs(per_axis["y"] - 0.1) < 1e-12)
    i, d, r, per_axis = pm.point_to_path([1.2, 0.9, 0.0], loaded)
    check("nearest segment is B-C", i == 1
          and abs(per_axis["x"] - 0.2) < 1e-12)

    bad = dict(spec, segments=[{"from": "A", "to": "ZZ", "type": "line",
                                "constrained_axes": None}])
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(bad, f)
        bname = f.name
    try:
        pm.load_path(bname)
        check("bad segment rejected", False)
    except ValueError:
        check("bad segment rejected", True)


def test_dwells():
    fps = 30.0
    t = np.arange(0, 20, 1 / fps)
    xyz = np.zeros((len(t), 3))
    # move 0-5 s, dwell 5-8 s, move 8-15 s, dwell 15-20 s
    moving1 = t < 5
    xyz[moving1, 0] = 0.1 * t[moving1]
    dwell1 = (t >= 5) & (t < 8)
    xyz[dwell1, 0] = 0.5
    moving2 = (t >= 8) & (t < 15)
    xyz[moving2, 0] = 0.5 + 0.1 * (t[moving2] - 8)
    xyz[t >= 15, 0] = 1.2
    ev = pm.detect_dwells(t, xyz, v_thresh=0.02, min_dur_s=0.5)
    check("two dwells found", len(ev) == 2)
    if len(ev) == 2:
        check("first dwell at x=0.5",
              abs(ev[0]["mean_xyz"][0] - 0.5) < 0.01)
        check("first dwell duration ~3 s",
              2.5 < ev[0]["duration_s"] < 3.5)
        check("second dwell at x=1.2",
              abs(ev[1]["mean_xyz"][0] - 1.2) < 0.01)
    ev2 = pm.detect_dwells(t, xyz, v_thresh=0.02, min_dur_s=0.5,
                           valid=t < 10)
    check("valid mask suppresses the second dwell", len(ev2) == 1)


def main():
    test_point_to_segment()
    test_path()
    test_dwells()
    print(f"=== {'ALL PASS' if not FAIL else 'FAILED'} "
          f"({len(FAIL)} failures) ===")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()

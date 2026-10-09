"""D-030 bone-length projection along the camera ray."""
import numpy as np
import pytest

from replay.bone_projection import (BoneLengthProjector, build_projector,
                                    point_on_ray_at_distance)


def test_ray_point_keeps_pixel_and_hits_length():
    prox = np.array([0.1, 0.0, 1.0])
    dist = np.array([0.4, 0.1, 1.3])
    q, ok = point_on_ray_at_distance(dist, prox, 0.25)
    assert ok
    assert np.linalg.norm(q - prox) == pytest.approx(0.25, abs=1e-12)
    # same pixel = same direction from the camera origin
    assert np.allclose(q / np.linalg.norm(q), dist / np.linalg.norm(dist))
    # of the two intersections, the one nearest the lifted depth
    other = 2 * np.dot(dist / np.linalg.norm(dist), prox)
    assert abs(np.linalg.norm(q) - np.linalg.norm(dist)) <= abs(
        other - np.linalg.norm(q) - np.linalg.norm(dist)) + 1e-12


def test_infeasible_goes_to_closest_ray_point():
    prox = np.array([0.0, 0.0, 1.0])
    dist = np.array([1.0, 0.0, 1.0])     # ray 45 deg off: min dist 0.707
    q, ok = point_on_ray_at_distance(dist, prox, 0.2)
    assert not ok
    d = dist / np.linalg.norm(dist)
    assert np.allclose(q, np.dot(d, prox) * d)


def _frame(sh, el, wr):
    return {"right_shoulder": sh, "right_elbow": el, "right_wrist": wr,
            "left_shoulder": None, "left_elbow": None, "left_wrist": None}


def test_calibration_median_then_tolerance():
    pr = BoneLengthProjector(calibrate_frames=3, tolerance=0.1)
    sh = np.array([0.0, 0.0, 1.0])
    for L in (0.30, 0.31, 0.29):
        f = _frame(sh, sh + [L, 0, 0], sh + [L, 0.25, 0])
        out = pr(f)                     # calibration frames unchanged
        for name in ("right_shoulder", "right_elbow", "right_wrist"):
            assert np.array_equal(out[name], f[name])
    assert pr.length[("right_shoulder", "right_elbow")] == pytest.approx(0.30)
    assert pr.calibrated is False       # left arm never seen
    # within tolerance: untouched
    f = _frame(sh, sh + [0.32, 0, 0], sh + [0.32, 0.25, 0])
    out = pr(f)
    assert np.array_equal(out["right_elbow"], f["right_elbow"])
    # outside tolerance: elbow moved along its ray to 0.30, forearm
    # then measured from the corrected elbow
    f = _frame(sh, sh + [0.05, 0, 0.39], sh + [0.05, 0.25, 0.39])
    out = pr(f)
    assert np.linalg.norm(out["right_elbow"] - sh) == pytest.approx(0.30)
    assert pr.n_projected[("right_shoulder", "right_elbow")] == 1
    assert f["right_elbow"][2] == pytest.approx(1.39)   # input untouched


def test_config_gate_and_null_values():
    assert build_projector({"bones": {"project": False}}) is None
    assert isinstance(build_projector({"bones": {
        "project": True, "calibrate_frames": 60, "tolerance": 0.064}}),
        BoneLengthProjector)
    with pytest.raises(ValueError):
        BoneLengthProjector(None, 0.1)

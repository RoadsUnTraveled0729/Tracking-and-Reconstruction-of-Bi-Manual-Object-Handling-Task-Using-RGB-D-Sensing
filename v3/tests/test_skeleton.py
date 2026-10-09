"""Tests for core/skeleton.py -- the single home of COCO indices."""
import numpy as np
import pytest

from core import skeleton as sk


def test_mapping_is_the_expected_eight():
    assert sk.COCO_IDX == {
        "left_shoulder": 5, "right_shoulder": 6,
        "left_elbow": 7, "right_elbow": 8,
        "left_wrist": 9, "right_wrist": 10,
        "left_hip": 11, "right_hip": 12,
    }
    assert len(set(sk.COCO_IDX.values())) == 8
    assert all(0 <= i < 17 for i in sk.COCO_IDX.values())
    for name, i in sk.COCO_IDX.items():
        assert sk.COCO_NAMES[i] == name


def test_joint_classes_cover_all_landmarks():
    assert set(sk.JOINT_CLASS) == set(sk.COCO_IDX)
    assert set(sk.JOINT_CLASS.values()) == {"shoulder", "elbow",
                                            "wrist", "hip"}
    assert sk.ROOT_REF == "right_shoulder"


def test_points_from_coco():
    rng = np.random.default_rng(0)
    kp = rng.normal(size=(17, 3))
    scores = rng.uniform(size=17)
    pts, sc = sk.points_from_coco(kp, scores)
    assert set(pts) == set(sk.COCO_IDX)
    assert np.allclose(pts["right_wrist"], kp[10])
    assert sc["left_hip"] == pytest.approx(scores[11])
    pts2, sc2 = sk.points_from_coco(kp)
    assert all(v == 1.0 for v in sc2.values())
    with pytest.raises(ValueError):
        sk.points_from_coco(kp[:16])
    with pytest.raises(ValueError):
        sk.points_from_coco(kp, scores[:5])


def test_points_from_coco_2d():
    rng = np.random.default_rng(1)
    kp = rng.normal(size=(17, 2))
    pts, sc = sk.points_from_coco_2d(kp)
    assert np.allclose(pts["left_elbow"], kp[7])
    with pytest.raises(ValueError):
        sk.points_from_coco_2d(rng.normal(size=(17, 3)))

"""Detection-scheduling logic tests (Phase 1). Pure numpy, no ort."""
import numpy as np
import pytest

from detector.box_tracker import BoxTracker, box_from_keypoints

IMG = (640, 480)


def kp_grid(x0=100, y0=100, x1=300, y1=400, score=0.9, n=17):
    """n keypoints spread over a box, uniform score."""
    xs = np.linspace(x0, x1, n)
    ys = np.linspace(y0, y1, n)
    return np.stack([xs, ys], axis=1), np.full(n, score)


def make_tracker(**kw):
    args = dict(det_freq=15, margin=0.25, kpt_min_score=0.3,
                reacquire_score=0.35, reacquire_frames=2,
                box_area_jump=2.0)
    args.update(kw)
    return BoxTracker(IMG, **args)


def test_box_from_keypoints_margin_and_clamp():
    kp, sc = kp_grid(100, 100, 300, 400)
    pad = 0.25 * 300  # larger side is y: 300 px
    box = box_from_keypoints(kp, sc, 0.3, 0.25, IMG)
    assert box == [100 - pad, 100 - pad, 300 + pad, 400 + pad]

    # tall box: the padded bottom exceeds the image and is clamped
    kp2, sc2 = kp_grid(100, 60, 300, 460)
    box2 = box_from_keypoints(kp2, sc2, 0.3, 0.25, IMG)
    assert box2[3] == 480.0
    assert box2[1] == 0.0  # top clamped too: 60 - 100 < 0

    # low-score points are excluded
    sc2 = sc.copy()
    sc2[:] = 0.1
    sc2[0] = sc2[1] = 0.9
    box2 = box_from_keypoints(kp, sc2, 0.3, 0.0, IMG)
    assert box2 == [kp[0, 0], kp[0, 1], kp[1, 0], kp[1, 1]]

    # fewer than 2 confident points -> None
    sc3 = np.full(17, 0.1)
    assert box_from_keypoints(kp, sc3, 0.3, 0.25, IMG) is None


def test_first_frame_detects_then_tracks():
    tr = make_tracker()
    assert "no_box" in tr.needs_detect()
    tr.note_detection([50, 50, 400, 460])
    kp, sc = kp_grid()
    tr.note_pose(kp, sc)
    assert tr.needs_detect() == []          # tracking
    assert tr.box is not None


def test_scheduled_redetect_every_n():
    tr = make_tracker(det_freq=15)
    tr.note_detection([50, 50, 400, 460])
    kp, sc = kp_grid()
    for i in range(14):
        tr.note_pose(kp, sc)
        assert tr.needs_detect() == [], f"early detect at pose {i}"
    tr.note_pose(kp, sc)                    # 15th pose since detection
    assert "scheduled" in tr.needs_detect()
    tr.note_detection([50, 50, 400, 460])   # resets the counter
    tr.note_pose(kp, sc)
    assert tr.needs_detect() == []


def test_low_score_streak_triggers():
    tr = make_tracker()
    tr.note_detection([50, 50, 400, 460])
    kp, good = kp_grid(score=0.9)
    _, bad = kp_grid(score=0.2)
    tr.note_pose(kp, bad)
    assert "low_score" not in tr.needs_detect()   # streak = 1 < 2
    tr.note_pose(kp, bad)
    assert "low_score" in tr.needs_detect()       # streak = 2
    tr.note_detection([50, 50, 400, 460])
    tr.note_pose(kp, good)                        # good frame resets
    tr.note_pose(kp, bad)
    assert "low_score" not in tr.needs_detect()


def test_key_indices_limit_score_check():
    key = np.arange(5, 13)                  # the eight v1 landmarks
    tr = make_tracker(key_indices=key)
    tr.note_detection([50, 50, 400, 460])
    kp, sc = kp_grid(score=0.9)
    sc[5:13] = 0.1                          # only the key joints are bad
    tr.note_pose(kp, sc)
    tr.note_pose(kp, sc)
    assert "low_score" in tr.needs_detect()


def test_area_jump_triggers():
    tr = make_tracker()
    tr.note_detection([50, 50, 400, 460])
    kp, sc = kp_grid(100, 100, 300, 400)
    tr.note_pose(kp, sc)
    assert "area_jump" not in tr.needs_detect()
    kp2, sc2 = kp_grid(150, 150, 250, 250)  # box shrinks well over 2x
    tr.note_pose(kp2, sc2)
    assert "area_jump" in tr.needs_detect()


def test_border_contact_triggers_on_rising_edge_only():
    tr = make_tracker()
    tr.note_detection([50, 50, 400, 460])
    kp, sc = kp_grid(5, 100, 200, 400)      # left edge after margin pad
    tr.note_pose(kp, sc)
    assert "border" in tr.needs_detect()    # first contact fires
    tr.note_detection([50, 50, 400, 460])
    tr.note_pose(kp, sc)                    # SAME edge still touched
    assert "border" not in tr.needs_detect()  # steady contact: no refire
    kp2, sc2 = kp_grid(5, 100, 200, 479)    # bottom edge newly touched
    tr.note_pose(kp2, sc2)
    assert "border" in tr.needs_detect()
    kp3, sc3 = kp_grid(150, 100, 300, 400)  # released: 150 - pad(75) > 0
    tr.note_pose(kp3, sc3)
    assert "border" not in tr.needs_detect()
    kp4, sc4 = kp_grid(5, 100, 200, 400)    # left touched again = rising
    tr.note_pose(kp4, sc4)
    assert "border" in tr.needs_detect()


def test_detector_box_does_not_seed_area_jump():
    """The pose box is tighter than the detector box by construction;
    comparing their areas refired area_jump after every detection
    (D-012). The baseline must reset on note_detection."""
    tr = make_tracker()
    tr.note_detection([0, 0, 640, 480])     # loose detector box
    kp, sc = kp_grid(200, 200, 280, 300)    # much smaller pose box
    tr.note_pose(kp, sc)
    assert "area_jump" not in tr.needs_detect()


def test_person_lost_and_reset():
    tr = make_tracker()
    tr.note_detection([50, 50, 400, 460])
    tr.note_pose(None, None)                # pose could not run
    assert "no_box" in tr.needs_detect()
    tr.note_detection(None)                 # detector found nobody
    assert tr.box is None
    assert "no_box" in tr.needs_detect()
    tr.reset()
    assert tr.needs_detect() == ["no_box"]


def test_config_wiring():
    from detector.rtmpose_detector import BoxTrackerFromConfig
    import json
    from pathlib import Path
    cfg = json.loads((Path(__file__).resolve().parents[1] / "configs" /
                      "default.json").read_text())
    tr = BoxTrackerFromConfig(cfg["detect"], IMG)
    assert tr.det_freq == 15
    assert tr.margin == 0.25
    assert tr.reacquire_frames == 2

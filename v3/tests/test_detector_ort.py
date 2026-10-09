"""Detector tests needing onnxruntime (markers: ort, gpu, bag), plus
stub-model tests of the factory backends that run in the default suite
(no onnxruntime, no model files; D-023).

Run under env v3rt with the CUDA lib dirs on LD_LIBRARY_PATH:

    NV=/home/luo/anaconda3/lib/python3.11/site-packages/nvidia
    LD_LIBRARY_PATH=$NV/cudnn/lib:$NV/cublas/lib:$NV/cuda_runtime/lib:\
$NV/cufft/lib:$NV/curand/lib \
    /home/luo/anaconda3/envs/v3rt/bin/python -m pytest tests/ -m ort
"""
import json
from pathlib import Path

import numpy as np
import pytest

V3_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V3_ROOT.parent


@pytest.fixture(scope="module")
def cfg():
    with open(V3_ROOT / "configs" / "default.json") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def detector(cfg):
    from detector.factory import build_detector
    return build_detector(cfg, str(REPO_ROOT), img_wh=(640, 480),
                          device="cuda")


@pytest.mark.ort
@pytest.mark.gpu
def test_cuda_provider_active(detector):
    for tool in (detector.det, detector.pose):
        assert "CUDAExecutionProvider" in tool.session.get_providers()


@pytest.mark.ort
@pytest.mark.gpu
def test_empty_image_reports_no_person(detector):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    detector.tracker.reset()
    kp, sc, diag = detector(frame)
    assert diag["det_ran"] is True
    assert "no_box" in diag["det_reasons"]
    assert kp is None and sc is None and diag["box"] is None
    # and it keeps trying while nobody is there
    kp, sc, diag = detector(frame)
    assert diag["det_ran"] is True


@pytest.mark.ort
@pytest.mark.gpu
@pytest.mark.bag
def test_bag_smoke_detection_and_shapes(cfg, detector):
    """First 60 aligned color frames of the pinned recording: a person
    must be found on nearly every frame with sane keypoint scores, and
    detection must be amortized (not run every frame)."""
    import pyrealsense2 as rs

    pipe = rs.pipeline()
    rs_cfg = rs.config()
    rs_cfg.enable_device_from_file(cfg["paths"]["bag"], repeat_playback=False)
    profile = pipe.start(rs_cfg)
    profile.get_device().as_playback().set_real_time(False)
    align = rs.align(rs.stream.color)

    detector.tracker.reset()
    detector.frame_idx = -1
    found = 0
    det_runs = 0
    mean_scores = []
    n = 60
    try:
        for _ in range(n):
            frames = pipe.wait_for_frames(timeout_ms=5000)
            frames = align.process(frames)
            color = np.asanyarray(frames.get_color_frame().get_data())
            kp, sc, diag = detector(color)
            det_runs += int(diag["det_ran"])
            if kp is not None:
                assert kp.shape == (17, 2) and sc.shape == (17,)
                found += 1
                mean_scores.append(float(sc[5:13].mean()))
    finally:
        pipe.stop()

    assert found >= n - 5, f"person found on only {found}/{n} frames"
    assert det_runs < n // 2, (
        f"detector ran {det_runs}/{n} frames; box reuse is not working")
    assert np.median(mean_scores) > 0.5, (
        f"median v1-landmark score {np.median(mean_scores):.2f}")


# ----------------------------------------------- stub backends (default suite)

class _StubTopDown:
    """rtmlib RTMPose-like: model(img, [box]) -> ((1, K, 2), (1, K))."""

    def __init__(self, n_kpts):
        self.n_kpts = n_kpts
        self.boxes = []

    def __call__(self, img, bboxes):
        self.boxes.append(list(bboxes[0]))
        kp = np.arange(self.n_kpts * 2, dtype=float).reshape(1, -1, 2)
        return kp, np.full((1, self.n_kpts), 0.9)


class _StubYOLOX:
    def __init__(self, boxes):
        self.boxes = boxes

    def __call__(self, img):
        return np.asarray(self.boxes, dtype=float)


class _StubRTMO:
    """rtmlib RTMO-like: model(img) -> ((N, 17, 2), (N, 17))."""

    def __init__(self, kps, scores):
        self.kps, self.scores = kps, scores

    def __call__(self, img):
        return self.kps, self.scores


def _person(x0, y0, x1, y1):
    kp = np.stack([np.linspace(x0, x1, 17), np.linspace(y0, y1, 17)], 1)
    return kp


def _stub_detector(cfg, backend, person=None):
    from detector.rtmpose_detector import RTMPoseDetector
    return RTMPoseDetector(cfg, str(REPO_ROOT), img_wh=(640, 480),
                           device="cpu", pose_backend=backend,
                           person_detector=person)


def test_rtmw_backend_slices_body17(cfg):
    from detector.factory import WholebodyBackend
    model = _StubTopDown(133)
    det = _stub_detector(cfg, WholebodyBackend(model),
                         _StubYOLOX([[100, 50, 300, 400]]))
    kp, sc, diag = det(np.zeros((480, 640, 3), np.uint8))
    assert kp.shape == (17, 2) and sc.shape == (17,)
    # the first 17 of 133 in order, nothing reordered
    assert np.array_equal(kp, np.arange(34, dtype=float).reshape(17, 2))
    assert diag["det_ran"] and diag["box"] == [100, 50, 300, 400]
    assert model.boxes == [[100, 50, 300, 400]]


def test_topdown_backend_rejects_wrong_keypoint_count(cfg):
    from detector.factory import TopDownPoseBackend
    det = _stub_detector(cfg, TopDownPoseBackend(_StubTopDown(133), 17),
                         _StubYOLOX([[100, 50, 300, 400]]))
    with pytest.raises(ValueError, match="133"):
        det(np.zeros((480, 640, 3), np.uint8))


def test_rtmo_backend_picks_largest_person_and_synthesises_box(cfg):
    from detector.box_tracker import box_from_keypoints
    from detector.factory import RTMOBackend
    small = _person(10, 10, 60, 90)
    large = _person(200, 40, 420, 460)
    kps = np.stack([small, large])
    scores = np.full((2, 17), 0.9)
    det = _stub_detector(cfg, RTMOBackend(_StubRTMO(kps, scores),
                                          cfg["detect"]["kpt_min_score"]))
    assert det.det is None          # no person detector for bottom-up
    kp, sc, diag = det(np.zeros((480, 640, 3), np.uint8))
    assert np.array_equal(kp, large)
    assert diag["det_ran"] is True and diag["det_reasons"] == ["bottom_up"]
    d = cfg["detect"]
    assert diag["box"] == box_from_keypoints(large, scores[1],
                                             d["kpt_min_score"],
                                             d["margin"], (640, 480))


def test_rtmo_backend_empty_frame_reports_no_person(cfg):
    from detector.factory import RTMOBackend
    # rtmlib RTMO returns one all-zero person when nothing passes NMS
    det = _stub_detector(cfg, RTMOBackend(
        _StubRTMO(np.zeros((1, 17, 2)), np.zeros((1, 17))),
        cfg["detect"]["kpt_min_score"]))
    kp, sc, diag = det(np.zeros((480, 640, 3), np.uint8))
    assert kp is None and sc is None and diag["box"] is None


def test_factory_rejects_unknown_backend(cfg):
    import copy
    from detector.factory import make_pose_backend
    bad = copy.deepcopy(cfg)
    bad["model"]["backend"] = "openpose"
    with pytest.raises(ValueError, match="backend"):
        make_pose_backend(bad, str(REPO_ROOT), "cpu")


def test_apply_variant_overlays_model_block(cfg):
    import copy
    from detector.factory import apply_variant, load_variants
    variants = load_variants()
    before = copy.deepcopy(cfg["model"])
    out = apply_variant(cfg, "rtmpose-m_yolox-m", variants)
    assert out["model"]["variant"] == "rtmpose-m_yolox-m"
    assert out["model"]["det_input_size_wh"] == [640, 640]
    assert out["model"]["pose_input_size_wh"] == [192, 256]
    assert cfg["model"] == before   # input not mutated
    with pytest.raises(KeyError):
        apply_variant(cfg, "no-such-variant", variants)

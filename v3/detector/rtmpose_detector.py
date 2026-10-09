"""RTMPose person keypoints via rtmlib + ONNX Runtime (Phase 1).

Explicit YOLOX (person det) + RTMPose classes, NOT rtmlib's Body
wrapper: V3 owns the scheduling (BoxTracker decides when detection
runs; between detections the pose box is reused from the previous
frame's keypoints).

CUDA setup: the CUDA execution provider needs the five CUDA-12 lib
dirs from configs/default.json model.cuda_lib_dirs on LD_LIBRARY_PATH
BEFORE the process starts (the dynamic loader does not re-read the
variable after startup). ensure_cuda_env() re-execs the current
process once with the variable set; call it from any entry point
before importing onnxruntime or rtmlib. See D-008.
"""
import os
import sys

import numpy as np


def ensure_cuda_env(lib_dirs):
    """Re-exec the interpreter once with lib_dirs prepended to
    LD_LIBRARY_PATH if they are not already present. No-op (returns
    False) when the environment is already correct; never returns
    when it re-execs."""
    if not lib_dirs:
        return False
    current = os.environ.get("LD_LIBRARY_PATH", "")
    missing = [d for d in lib_dirs if d not in current.split(":")]
    if not missing:
        return False
    if os.environ.get("V3_CUDA_ENV_REEXEC") == "1":
        raise RuntimeError(
            "LD_LIBRARY_PATH still missing CUDA dirs after re-exec: "
            + ":".join(missing))
    env = dict(os.environ)
    env["LD_LIBRARY_PATH"] = ":".join(list(lib_dirs)
                                      + ([current] if current else []))
    env["V3_CUDA_ENV_REEXEC"] = "1"
    os.execve(sys.executable, [sys.executable] + sys.argv, env)


class RTMPoseDetector:
    """One person's COCO-17 keypoints per frame, detection amortized.

    cfg: the full default.json dict (model + detect blocks are read).
    repo_root: base for the relative onnx paths in the config.
    device: 'cuda' (default, D-008) or 'cpu' (config-free fallback).
    pose_backend / person_detector: pre-built objects (tests inject
    stubs); when None they are loaded from cfg model.backend through
    detector.factory (D-023). Callers should use
    detector.factory.build_detector rather than this class directly.

    self.pose is the pose backend: __call__(img, box) -> (kp17, sc17),
    attribute needs_box (False for bottom-up RTMO) and n_kpts. self.det
    is the YOLOX person detector, None for a bottom-up backend.
    """

    def __init__(self, cfg, repo_root, img_wh, device="cuda",
                 key_indices=None, pose_backend=None,
                 person_detector=None):
        from detector import factory

        de = cfg["detect"]
        self.pose = (pose_backend if pose_backend is not None
                     else factory.make_pose_backend(cfg, repo_root, device))
        if not self.pose.needs_box:
            self.det = None
        elif person_detector is not None:
            self.det = person_detector
        else:
            self.det = factory.make_person_detector(cfg, repo_root, device)
        self.tracker = BoxTrackerFromConfig(de, img_wh, key_indices)
        self.frame_idx = -1

    def __call__(self, frame_bgr):
        """-> (kp17 (17, 2) px, scores17 (17,), diag dict).
        kp17/scores17 are None when no person is available this frame.
        """
        self.frame_idx += 1
        tr = self.tracker
        if not self.pose.needs_box:
            return self._call_bottom_up(frame_bgr)
        reasons = tr.needs_detect()
        det_ran = bool(reasons)
        if det_ran:
            boxes = self.det(frame_bgr)
            tr.note_detection(_largest_box(boxes))
        box = tr.box
        if box is None:
            tr.note_pose(None, None)
            return None, None, {"det_ran": det_ran,
                                "det_reasons": reasons,
                                "box": None,
                                "frame": self.frame_idx}
        kp17, sc17 = self.pose(frame_bgr, box)
        tr.note_pose(kp17, sc17)
        return kp17, sc17, {"det_ran": det_ran, "det_reasons": reasons,
                            "box": box, "frame": self.frame_idx}

    def _call_bottom_up(self, frame_bgr):
        """Bottom-up backend (RTMO): person finding runs on every frame
        (det_ran True, reason 'bottom_up'). The diag box is synthesised
        from this frame's keypoint extent by the tracker's own
        box_from_keypoints rule (detect.kpt_min_score, detect.margin),
        so box-derived diagnostics keep their meaning (D-023)."""
        tr = self.tracker
        kp17, sc17 = self.pose(frame_bgr, None)
        tr.note_pose(kp17, sc17)
        diag = {"det_ran": True, "det_reasons": ["bottom_up"],
                "box": tr.box if kp17 is not None else None,
                "frame": self.frame_idx}
        return kp17, sc17, diag


def _largest_box(boxes):
    """Pick the largest-area person box; None when detection is empty
    (single-person lab scene; area beats score for a cropped stream)."""
    boxes = np.asarray(boxes, dtype=float).reshape(-1, 4) if boxes is not None \
        else np.empty((0, 4))
    if boxes.shape[0] == 0:
        return None
    areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    return boxes[int(np.argmax(areas))].tolist()


def BoxTrackerFromConfig(detect_cfg, img_wh, key_indices=None):
    from detector.box_tracker import BoxTracker
    return BoxTracker(
        img_wh,
        det_freq=detect_cfg["det_freq"],
        margin=detect_cfg["margin"],
        kpt_min_score=detect_cfg["kpt_min_score"],
        reacquire_score=detect_cfg["reacquire_score"],
        reacquire_frames=detect_cfg["reacquire_frames"],
        box_area_jump=detect_cfg["box_area_jump"],
        key_indices=key_indices,
    )

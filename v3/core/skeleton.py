"""COCO-17 -> v1 landmark vocabulary (the ONLY place indices appear).

RTMPose emits COCO-17 keypoints; everything downstream of the detector
speaks the eight v1 landmark names used by the vendored solvers.
BlazePose-to-COCO correspondence for the eight: BlazePose 11/12/13/14/
15/16/23/24 -> COCO 5/6/7/8/9/10/11/12. The root frame reference is
the right shoulder (COCO 6), matching v1's build_root_frame(p23, p24,
p12) call order (left hip, right hip, right shoulder).

Wrist caveat (V3_PLAN.md risks): the COCO wrist is not the BlazePose
wrist point; the shoulder-twist angle definition shifts with it. The
per-angle V3-vs-v1 offset is measured in Phase 3 and reported; v1's
calibrated grip offset is never reused.
"""
import numpy as np

COCO_NAMES = (
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
)

# v1 landmark name -> COCO-17 index (the eight the solvers consume)
COCO_IDX = {
    "left_shoulder": 5,
    "right_shoulder": 6,
    "left_elbow": 7,
    "right_elbow": 8,
    "left_wrist": 9,
    "right_wrist": 10,
    "left_hip": 11,
    "right_hip": 12,
}

V1_LANDMARKS = tuple(COCO_IDX)  # insertion order, fixed

# joint class per landmark, for the per-class gate thresholds (config)
JOINT_CLASS = {
    "left_shoulder": "shoulder", "right_shoulder": "shoulder",
    "left_elbow": "elbow", "right_elbow": "elbow",
    "left_wrist": "wrist", "right_wrist": "wrist",
    "left_hip": "hip", "right_hip": "hip",
}

ROOT_REF = "right_shoulder"  # coronal-plane reference for the root frame


def points_from_coco(kp17, scores17=None):
    """(17, 3) keypoints (+ optional (17,) scores) -> ({name: xyz},
    {name: score}). Scores default to 1.0 when absent."""
    kp17 = np.asarray(kp17, dtype=float)
    if kp17.shape != (17, 3):
        raise ValueError(f"expected (17, 3), got {kp17.shape}")
    points = {name: kp17[i].copy() for name, i in COCO_IDX.items()}
    if scores17 is None:
        scores = {name: 1.0 for name in COCO_IDX}
    else:
        scores17 = np.asarray(scores17, dtype=float)
        if scores17.shape != (17,):
            raise ValueError(f"expected (17,) scores, got {scores17.shape}")
        scores = {name: float(scores17[i]) for name, i in COCO_IDX.items()}
    return points, scores


def points_from_coco_2d(kp17_px, scores17=None):
    """(17, 2) pixel keypoints -> ({name: uv}, {name: score}); the
    detector-side counterpart before depth lifting."""
    kp17_px = np.asarray(kp17_px, dtype=float)
    if kp17_px.shape != (17, 2):
        raise ValueError(f"expected (17, 2), got {kp17_px.shape}")
    points = {name: kp17_px[i].copy() for name, i in COCO_IDX.items()}
    if scores17 is None:
        scores = {name: 1.0 for name in COCO_IDX}
    else:
        scores17 = np.asarray(scores17, dtype=float)
        scores = {name: float(scores17[i]) for name, i in COCO_IDX.items()}
    return points, scores

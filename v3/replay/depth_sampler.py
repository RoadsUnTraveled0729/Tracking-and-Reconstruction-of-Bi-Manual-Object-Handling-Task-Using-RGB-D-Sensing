"""Pixel keypoints -> camera-frame 3D via depth median + deprojection.

Copy-adapted from v1 (mediapipe/extract_landmarks_to_csv.py
sample_depth + deproject_landmarks): median of nonzero depth in a
window x window neighborhood, then rs2_deproject_pixel_to_point (which
honors the stream's distortion model). Differences from v1: input is
COCO-17 pixel keypoints + scores (RTMPose) instead of normalized
MediaPipe landmarks + visibility, and NO score gate is applied here --
the RTMPose score is localization confidence, not visibility, and the
gate thresholds are fitted in Phase 3 (D-006). Every landmark's score
travels with it; src records only geometric failures.

Coordinates: camera (sensor) frame, meters -- the same convention as
the v1 extraction CSVs. The Unity flip (x, -y, z) happens downstream
at solve time, exactly as in v1.
"""
import numpy as np
import pyrealsense2 as rs

from core.skeleton import COCO_IDX

SRC_OK = 0
SRC_NO_DEPTH = 2       # depth hole (v1's SRC_NO_DEPTH meaning)
SRC_OUT_OF_FRAME = 3   # keypoint pixel outside the image


def sample_depth(depth_img, depth_scale, u, v, window):
    """Median of the nonzero depth returns in a window x window
    neighborhood around (u, v), in meters; 0.0 when all zero (hole).
    Verbatim v1 logic."""
    r = window // 2
    patch = depth_img[max(0, v - r):v + r + 1, max(0, u - r):u + r + 1]
    nz = patch[patch > 0]
    if nz.size == 0:
        return 0.0
    return float(np.median(nz)) * depth_scale


def lift_keypoints(kp17_px, scores17, depth_img, depth_scale, intrinsics,
                   window, bones=None):
    """COCO-17 pixel keypoints -> the eight v1 landmarks in 3D.

    bones: optional replay.bone_projection.BoneLengthProjector (D-030,
    stateful across frames; one per stream). When given, arm points
    whose bone length deviates beyond bones.tolerance from the
    calibrated length are moved along their own pixel ray (depth
    only; px unchanged) and their src stays SRC_OK. None (the default,
    used by tools/extract_bag_to_csv.py) keeps the verbatim v1 lift,
    so extraction CSVs stay raw and the CSV replay applies the same
    projection itself (replay/runner.py).

    Returns {v1_name: {"xyz": (3,) camera-frame meters or None,
                       "px": (u, v) ints or None,
                       "score": float, "src": SRC_*}}.
    """
    h, w = depth_img.shape
    out = {}
    for name, idx in COCO_IDX.items():
        u = int(round(float(kp17_px[idx][0])))
        v = int(round(float(kp17_px[idx][1])))
        entry = {"xyz": None, "px": None,
                 "score": float(scores17[idx]), "src": SRC_OK}
        if not (0 <= u < w and 0 <= v < h):
            entry["src"] = SRC_OUT_OF_FRAME
            out[name] = entry
            continue
        entry["px"] = (u, v)
        depth = sample_depth(depth_img, depth_scale, u, v, window)
        if depth <= 0.0:
            entry["src"] = SRC_NO_DEPTH
            out[name] = entry
            continue
        entry["xyz"] = rs.rs2_deproject_pixel_to_point(
            intrinsics, [u, v], depth)
        out[name] = entry
    if bones is not None:
        fixed = bones({k: e["xyz"] for k, e in out.items()})
        for k, e in out.items():
            if e["xyz"] is not None:
                e["xyz"] = [float(c) for c in fixed[k]]
    return out

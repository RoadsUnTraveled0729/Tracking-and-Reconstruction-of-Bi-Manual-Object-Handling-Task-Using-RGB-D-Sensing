#!/usr/bin/env python3
# Filename: mediapipe/extract_landmarks_to_csv.py
# Pipeline A, stage 1+2: bag playback -> MediaPipe pose -> depth deprojection -> CSV.
#
# Reads a RealSense .bag recording offline (as fast as possible, not real time),
# runs MediaPipe PoseLandmarker on every color frame, deprojects the selected
# landmarks through the aligned depth frame + color intrinsics, and writes one
# CSV row per frame with camera-frame XYZ (meters) per landmark.
#
# Base-variant policy: raw output only — no smoothing/filtering of any kind.
# Blocked landmarks (occlusion): visibility below --min-vis, or no depth return
# in the --depth-window neighborhood, write empty xyz cells with a {name}_src
# reason code (0 ok / 1 low_vis / 2 no_depth) — see KINEMATIC_MODEL.md §10.
#
# Usage:
#   python extract_landmarks_to_csv.py --bag ../Video/recording_20260328_021733.bag
#   python extract_landmarks_to_csv.py --bag <file> --model lite --max-frames 60

import argparse
import csv
import json
import platform
import sys
import time
import urllib.request
from pathlib import Path

import cv2
import numpy as np
import pyrealsense2 as rs
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

# MediaPipe Pose indices in scope for this phase (torso + arms).
TORSO_AND_ARMS = [11, 12, 13, 14, 15, 16, 23, 24]

LANDMARK_NAMES = {
    11: "left_shoulder", 12: "right_shoulder",
    13: "left_elbow", 14: "right_elbow",
    15: "left_wrist", 16: "right_wrist",
    23: "left_hip", 24: "right_hip",
}

MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
             "pose_landmarker_{v}/float16/latest/pose_landmarker_{v}.task")

# Per-landmark source/reason codes written to the {name}_src column.
SRC_OK = 0        # xyz valid
SRC_LOW_VIS = 1   # blocked/occluded: MediaPipe visibility below --min-vis,
                  # position would be a hallucinated guess -> dropped
SRC_NO_DEPTH = 2  # pixel out of bounds or no depth return in the window


def resolve_model(model_arg: str, model_dir: Path) -> Path:
    """Accept a variant name (lite/full/heavy) or a direct path to a .task file."""
    p = Path(model_arg)
    if p.suffix == ".task":
        if not p.exists():
            sys.exit(f"[ERROR] Model file not found: {p}")
        return p
    if model_arg not in ("lite", "full", "heavy"):
        sys.exit(f"[ERROR] --model must be lite/full/heavy or a .task path, got: {model_arg}")
    model_path = model_dir / f"pose_landmarker_{model_arg}.task"
    if not model_path.exists():
        model_dir.mkdir(parents=True, exist_ok=True)
        url = MODEL_URL.format(v=model_arg)
        print(f"[INFO] Downloading {url}")
        urllib.request.urlretrieve(url, model_path)
    return model_path


def make_landmarker(model_path: Path, delegate: str):
    """Returns (landmarker, delegate_used). 'auto' = GPU on Linux, CPU elsewhere;
    a failed GPU init falls back to CPU."""
    if delegate == "auto":
        delegate = "gpu" if platform.system() == "Linux" else "cpu"
    delegates = {"cpu": mp_python.BaseOptions.Delegate.CPU,
                 "gpu": mp_python.BaseOptions.Delegate.GPU}

    def build(d):
        options = mp_vision.PoseLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(model_path),
                                               delegate=delegates[d]),
            running_mode=mp_vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=0.3,
            min_pose_presence_confidence=0.3,
            min_tracking_confidence=0.3,
        )
        return mp_vision.PoseLandmarker.create_from_options(options)

    try:
        return build(delegate), delegate
    except RuntimeError as e:
        if delegate != "gpu":
            raise
        print(f"[WARN] GPU delegate failed ({e}); falling back to CPU")
        return build("cpu"), "cpu"


def open_bag(bag_path: Path):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(str(bag_path), repeat_playback=False)
    profile = pipeline.start(config)
    # Process frames as fast as possible instead of pacing to the recording FPS.
    profile.get_device().as_playback().set_real_time(False)
    intrinsics = (profile.get_stream(rs.stream.color)
                  .as_video_stream_profile().get_intrinsics())
    color_format = profile.get_stream(rs.stream.color).format()
    align = rs.align(rs.stream.color)
    return pipeline, align, intrinsics, color_format


def sample_depth(depth_img, depth_scale, u, v, window):
    """Median of the nonzero depth returns in a window x window neighborhood
    around (u, v), in meters. 0.0 when every pixel in the window is a zero
    return (depth hole). window=1 reproduces the old single-pixel sample."""
    r = window // 2
    h, w = depth_img.shape
    patch = depth_img[max(0, v - r):v + r + 1, max(0, u - r):u + r + 1]
    nz = patch[patch > 0]
    if nz.size == 0:
        return 0.0
    return float(np.median(nz)) * depth_scale


def deproject_landmarks(mp_landmarks, depth_frame, intrinsics, indices,
                        min_vis, depth_window):
    """Normalized MediaPipe (x, y) -> pixel -> depth -> camera-frame XYZ (meters).

    Returns {idx: {"xyz": (X, Y, Z) or None, "px": (u, v) or None,
                   "visibility": float, "src": SRC_*}}.
    xyz is None (blocked landmark) when:
      - visibility < min_vis (SRC_LOW_VIS): MediaPipe still emits a position
        for occluded landmarks, but it is a hallucinated guess — dropped here
        so downstream sees an honest gap instead of a wrong point;
      - the pixel is out of bounds or the depth window has no nonzero return
        (SRC_NO_DEPTH).
    Depth is the median of nonzero returns in a depth_window^2 neighborhood
    (single-pixel zero returns at occluder edges no longer kill the landmark).
    """
    w, h = intrinsics.width, intrinsics.height
    depth_img = np.asanyarray(depth_frame.get_data())
    depth_scale = depth_frame.get_units()
    out = {}
    for idx in indices:
        lm = mp_landmarks[idx]
        u, v = int(lm.x * w), int(lm.y * h)
        entry = {"xyz": None, "px": None, "visibility": float(lm.visibility),
                 "src": SRC_NO_DEPTH}
        if entry["visibility"] < min_vis:
            entry["src"] = SRC_LOW_VIS
        elif 0 <= u < w and 0 <= v < h:
            entry["px"] = (u, v)
            depth = sample_depth(depth_img, depth_scale, u, v, depth_window)
            if depth > 0:
                # rs2_deproject handles the stream's distortion model, unlike
                # a bare pinhole (u-cx)*Z/fx formula.
                entry["xyz"] = rs.rs2_deproject_pixel_to_point(intrinsics, [u, v], depth)
                entry["src"] = SRC_OK
        out[idx] = entry
    return out


def intrinsics_to_dict(intr):
    return {"width": intr.width, "height": intr.height,
            "fx": intr.fx, "fy": intr.fy, "ppx": intr.ppx, "ppy": intr.ppy,
            "model": str(intr.model), "coeffs": list(intr.coeffs)}


def main():
    script_dir = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Extract MediaPipe landmark XYZ from a RealSense .bag to CSV.")
    ap.add_argument("--bag", required=True, help="Path to the .bag recording")
    ap.add_argument("--out", default=None,
                    help="Output CSV path (default: output/<bag-stem>_landmarks_raw.csv)")
    ap.add_argument("--model", default="heavy",
                    help="Model variant lite/full/heavy, or path to a .task file (default: heavy)")
    ap.add_argument("--delegate", choices=["auto", "cpu", "gpu"], default="auto",
                    help="MediaPipe inference delegate (default: auto = GPU on Linux)")
    ap.add_argument("--landmarks", type=int, nargs="+", default=TORSO_AND_ARMS,
                    help=f"Landmark indices to export (default: {TORSO_AND_ARMS})")
    ap.add_argument("--max-frames", type=int, default=None,
                    help="Stop after N frames (for smoke tests)")
    ap.add_argument("--min-vis", type=float, default=0.5,
                    help="Visibility gate: landmarks below this are treated as "
                         "blocked and get empty xyz (default: 0.5)")
    ap.add_argument("--depth-window", type=int, default=5,
                    help="Depth sampled as median of nonzero returns in an "
                         "NxN window (odd; 1 = legacy single pixel; default: 5)")
    args = ap.parse_args()
    if args.depth_window < 1 or args.depth_window % 2 == 0:
        sys.exit(f"[ERROR] --depth-window must be odd and >= 1, got {args.depth_window}")

    bag_path = Path(args.bag).resolve()
    if not bag_path.exists():
        sys.exit(f"[ERROR] Bag file not found: {bag_path}")
    out_csv = Path(args.out) if args.out else script_dir / "output" / f"{bag_path.stem}_landmarks_raw.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_meta = out_csv.with_suffix(".meta.json")

    model_path = resolve_model(args.model, script_dir / "models")
    print(f"[INFO] Model: {model_path}")
    landmarker, delegate_used = make_landmarker(model_path, args.delegate)
    print(f"[INFO] Inference delegate: {delegate_used}")

    pipeline, align, intrinsics, color_format = open_bag(bag_path)
    print(f"[INFO] Bag opened: {bag_path.name} "
          f"({intrinsics.width}x{intrinsics.height}, color format {color_format})")

    header = ["frame", "time_s", "has_pose"]
    for idx in args.landmarks:
        name = LANDMARK_NAMES.get(idx, f"lm{idx}")
        header += [f"{name}_x", f"{name}_y", f"{name}_z", f"{name}_vis", f"{name}_src"]

    frame_count = 0
    pose_count = 0
    src_counts = {idx: {SRC_LOW_VIS: 0, SRC_NO_DEPTH: 0} for idx in args.landmarks}
    first_ts_ms = None
    last_mp_ts = -1
    t_start = time.time()

    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        while args.max_frames is None or frame_count < args.max_frames:
            try:
                frames = pipeline.wait_for_frames(timeout_ms=5000)
            except RuntimeError:
                break  # end of bag
            aligned = align.process(frames)
            color_frame = aligned.get_color_frame()
            depth_frame = aligned.get_depth_frame()
            if not color_frame or not depth_frame:
                continue

            ts_ms = frames.get_timestamp()
            if first_ts_ms is None:
                first_ts_ms = ts_ms
            rel_s = (ts_ms - first_ts_ms) / 1000.0

            color = np.asanyarray(color_frame.get_data())
            rgb = color if color_format == rs.format.rgb8 else cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb))

            # VIDEO mode requires strictly increasing integer-ms timestamps.
            mp_ts = max(int(rel_s * 1000), last_mp_ts + 1)
            last_mp_ts = mp_ts
            result = landmarker.detect_for_video(mp_image, mp_ts)

            row = [frame_count, f"{rel_s:.6f}"]
            if result and result.pose_landmarks:
                pose_count += 1
                lms = deproject_landmarks(result.pose_landmarks[0], depth_frame,
                                          intrinsics, args.landmarks,
                                          args.min_vis, args.depth_window)
                row.append(1)
                for idx in args.landmarks:
                    e = lms[idx]
                    if e["xyz"] is not None:
                        row += [f"{c:.6f}" for c in e["xyz"]]
                    else:
                        row += ["", "", ""]
                        src_counts[idx][e["src"]] += 1
                    row.append(f"{e['visibility']:.4f}")
                    row.append(e["src"])
            else:
                row.append(0)
                row += ["", "", "", "", ""] * len(args.landmarks)
            writer.writerow(row)

            frame_count += 1
            if frame_count % 100 == 0:
                print(f"[>] {frame_count} frames ({pose_count} with pose, "
                      f"{frame_count / (time.time() - t_start):.1f} fps)")

    pipeline.stop()
    landmarker.close()

    meta = {
        "source_bag": str(bag_path),
        "output_csv": str(out_csv),
        "model": str(model_path),
        "delegate": delegate_used,
        "landmark_indices": args.landmarks,
        "landmark_names": {str(i): LANDMARK_NAMES.get(i, f"lm{i}") for i in args.landmarks},
        "frames_total": frame_count,
        "frames_with_pose": pose_count,
        "min_vis": args.min_vis,
        "depth_window": args.depth_window,
        "blocked_landmarks": {
            LANDMARK_NAMES.get(i, f"lm{i}"): {
                "low_vis": src_counts[i][SRC_LOW_VIS],
                "no_depth": src_counts[i][SRC_NO_DEPTH],
            } for i in args.landmarks},
        "src_legend": {"0": "ok", "1": "low_vis (blocked)", "2": "no_depth"},
        "color_intrinsics": intrinsics_to_dict(intrinsics),
        "coordinate_frame": "camera (color): X right, Y down, Z forward, meters",
        "smoothing": "none (base variant, raw output)",
        "export_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_s": round(time.time() - t_start, 1),
    }
    with open(out_meta, "w") as f:
        json.dump(meta, f, indent=2)

    blocked_total = sum(c[SRC_LOW_VIS] + c[SRC_NO_DEPTH] for c in src_counts.values())
    print(f"\n[+] Done: {frame_count} frames, {pose_count} with pose "
          f"({time.time() - t_start:.1f}s)")
    print(f"[+] Blocked landmark cells: {blocked_total} "
          f"(low_vis {sum(c[SRC_LOW_VIS] for c in src_counts.values())}, "
          f"no_depth {sum(c[SRC_NO_DEPTH] for c in src_counts.values())})")
    print(f"[+] CSV:  {out_csv}")
    print(f"[+] Meta: {out_meta}")


if __name__ == "__main__":
    main()

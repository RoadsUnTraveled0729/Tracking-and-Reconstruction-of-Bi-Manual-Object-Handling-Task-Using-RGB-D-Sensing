#!/usr/bin/env python3
"""Chapter 9 failure-mode figures (V7 rewrite round).

Two screenshots required by the limitations section
(skill_set/thesis-structure-rules.md rule 3):

  ch9_fig_landmark_failure.png
      Frames 1698 and 1818 of the primary recording; 1818 is inside the
      failure window arm_R 1775-1825 (eval/reports/r5_failure_mask.md,
      confident-but-wrong table: upper arm 47.2 cm against a clean
      median of 25.8 cm, forearm 3.0 cm against 25.5 cm). MediaPipe is
      run in VIDEO mode over the recording, exactly as the extraction
      stage runs it, so the landmarks drawn are the ones the pipeline
      received. Panel (a) is a tracked frame before the window,
      panel (b) is inside it.

  ch9_fig_marker_blocked.png
      Frames 1060 and 1073. The object marker is detected on 2058 of
      the 2099 frames, and the 41 misses are the desk handover, frames
      1067-1109, plus the isolated frame 1013 (counted from
      eval/output/recording_20260825_222315_scaled_object_world.csv;
      the handover window is also named in the limitations of
      eval/reports/r5_waypoint_eval.md). Panel (a) is a detected frame
      just before the gap, panel (b) is inside it.

      Frame 1073 was chosen after extracting and inspecting every frame
      of the gap: the printed square is never fully covered anywhere in
      1067-1109. What loses the pose is a hand crossing the marker
      border, and 1073 is the frame where the finger cuts furthest into
      the top-right corner of the square. The panels carry the
      detector's live result on the frame, not a drawn annotation.

      The crop shows two of the three markers, the object marker and
      the desk marker; the wall marker is outside it.

Both figures are cropped to the same region in each panel so the pair
reads as a before and after.

Output: writing/v7/figures/ch9_fig_landmark_failure.png,
        writing/v7/figures/ch9_fig_marker_blocked.png
        (source frames cached in writing/v7/figures/src/)
Run:    python writing/v7/scripts/make_ch9_failure_figs.py
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cv2
import numpy as np
from matplotlib.patches import Polygon

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "v1" / "mediapipe"))

FIG = REPO / "writing" / "v7" / "figures"
SRC = FIG / "src"
SRC.mkdir(parents=True, exist_ok=True)
BAG = REPO / "Video" / "recording_20260825_222315.bag"
MODEL = REPO / "v1" / "mediapipe" / "models" / "pose_landmarker_heavy.task"

LM_FRAMES = (1698, 1818)       # landmark figure: tracked, then failed
AR_FRAMES = (1060, 1073)       # marker figure: detected, then lost
WANT = sorted(set(LM_FRAMES) | set(AR_FRAMES))
CACHE = SRC / "r5_ch9_landmarks.json"

# Only the landmark figure needs MediaPipe. The marker panels need the
# colour frame alone, so they are extracted by a pass that skips the
# detector; that keeps re-picking a marker frame cheap.

USED = [11, 12, 13, 14, 15, 16, 23, 24]
LINKS = [(11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
         (11, 23), (12, 24), (23, 24)]
MARK = {14: "right elbow", 16: "right wrist"}


def capture_color(frames):
    """Colour frames only, no detector. Used for the marker panels and
    for inspecting candidate frames of the handover gap."""
    missing = [f for f in frames
               if not (SRC / f"r5_frame{f:05d}.png").exists()]
    if not missing:
        return
    from extract_landmarks_to_csv import open_bag  # noqa
    import pyrealsense2 as rs

    pipeline, align, _intr, color_format = open_bag(BAG)
    idx = -1
    try:
        while idx < max(missing):
            try:
                frames_rs = pipeline.wait_for_frames(timeout_ms=5000)
            except RuntimeError:
                break
            idx += 1
            color = align.process(frames_rs).get_color_frame()
            if not color:
                continue
            if idx in missing:
                img = np.asanyarray(color.get_data())
                bgr = (cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                       if color_format == rs.format.rgb8 else img)
                cv2.imwrite(str(SRC / f"r5_frame{idx:05d}.png"), bgr)
                print("captured colour frame", idx)
    finally:
        pipeline.stop()


def capture():
    """One pass over the recording: colour frames plus the MediaPipe
    landmarks of the landmark-figure frames, cached so re-runs skip the
    pass. The marker frames are fetched by the colour-only pass."""
    capture_color(AR_FRAMES)
    missing = [f for f in LM_FRAMES
               if not (SRC / f"r5_frame{f:05d}.png").exists()]
    if not missing and CACHE.exists():
        return json.loads(CACHE.read_text())

    from extract_landmarks_to_csv import open_bag, make_landmarker  # noqa
    import mediapipe as mp
    import pyrealsense2 as rs

    assert MODEL.exists(), f"missing model: {MODEL}"
    landmarker, delegate = make_landmarker(MODEL, "auto")
    print("delegate:", delegate)
    pipeline, align, _intr, color_format = open_bag(BAG)
    out = {}
    idx = -1
    try:
        while idx < max(LM_FRAMES):
            try:
                frames = pipeline.wait_for_frames(timeout_ms=5000)
            except RuntimeError:
                break
            idx += 1
            frames = align.process(frames)
            color = frames.get_color_frame()
            if not color:
                continue
            img = np.asanyarray(color.get_data())
            if color_format == rs.format.rgb8:
                rgb, bgr = img, cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            else:
                bgr, rgb = img, cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # VIDEO mode: every frame must be fed, in order, as the
            # extraction stage does.
            res = landmarker.detect_for_video(
                mp.Image(image_format=mp.ImageFormat.SRGB,
                         data=np.ascontiguousarray(rgb)),
                int(idx * 1000 / 30))
            if idx in LM_FRAMES:
                cv2.imwrite(str(SRC / f"r5_frame{idx:05d}.png"), bgr)
                assert res.pose_landmarks, f"no pose at frame {idx}"
                out[str(idx)] = [[p.x, p.y, p.visibility]
                                 for p in res.pose_landmarks[0]]
                print("captured frame", idx)
    finally:
        pipeline.stop()
    CACHE.write_text(json.dumps(out))
    return out


def draw_skeleton(ax, img, pts, crop):
    x0, y0, x1, y1 = crop
    ax.imshow(img[y0:y1, x0:x1])
    ax.axis("off")
    for a, b in LINKS:
        ax.plot([pts[a][0] - x0, pts[b][0] - x0],
                [pts[a][1] - y0, pts[b][1] - y0],
                "-", color="white", lw=2.0, solid_capstyle="round")
    for i in USED:
        u, v = pts[i][0] - x0, pts[i][1] - y0
        if i in MARK:
            ax.plot(u, v, "o", ms=9, mfc="#e63946", mec="black", mew=1.2)
        else:
            ax.plot(u, v, "o", ms=7, mfc="#43aa4a", mec="black", mew=1.0)


def label(ax, pts, crop, i, dx, dy, text):
    x0, y0 = crop[0], crop[1]
    u, v = pts[i][0] - x0, pts[i][1] - y0
    ax.annotate(text, xy=(u, v), xytext=(u + dx, v + dy), fontsize=10,
                color="white", ha="center",
                bbox=dict(boxstyle="round,pad=0.25", fc="#1d3557", alpha=0.9),
                arrowprops=dict(arrowstyle="->", color="white", lw=1.4))


def landmark_figure(cap):
    w, h = 640, 480
    crop = (140, 25, 540, 355)
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.0))
    titles = ["(a) frame 1698: the right arm is tracked",
              "(b) frame 1818: the elbow landmark sits on the hand"]
    for ax, f, title in zip(axes, LM_FRAMES, titles):
        img = cv2.cvtColor(cv2.imread(str(SRC / f"r5_frame{f:05d}.png")),
                           cv2.COLOR_BGR2RGB)
        pts = [(p[0] * w, p[1] * h) for p in cap[str(f)]]
        draw_skeleton(ax, img, pts, crop)
        ax.set_title(title, fontsize=10)
    label(axes[0], [(p[0] * w, p[1] * h) for p in cap[str(LM_FRAMES[0])]],
          crop, 14, -70, -55, "right elbow")
    label(axes[0], [(p[0] * w, p[1] * h) for p in cap[str(LM_FRAMES[0])]],
          crop, 16, -60, 60, "right wrist")
    label(axes[1], [(p[0] * w, p[1] * h) for p in cap[str(LM_FRAMES[1])]],
          crop, 14, -30, -70, "right elbow and\nright wrist together")
    plt.tight_layout()
    out = FIG / "ch9_fig_landmark_failure.png"
    plt.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("saved", out)


def marker_figure():
    aruco = cv2.aruco
    params = aruco.DetectorParameters()
    params.cornerRefinementMethod = aruco.CORNER_REFINE_APRILTAG
    detector = aruco.ArucoDetector(
        aruco.getPredefinedDictionary(aruco.DICT_5X5_50), params)
    roles = {0: "wall", 1: "object", 2: "desk"}
    crop = (150, 150, 560, 470)
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.0))
    titles = ["(a) frame 1060: the object marker is detected",
              "(b) frame 1073: a finger crosses its border, no pose returned"]
    for ax, f, title in zip(axes, AR_FRAMES, titles):
        img = cv2.cvtColor(cv2.imread(str(SRC / f"r5_frame{f:05d}.png")),
                           cv2.COLOR_BGR2RGB)
        corners, ids, _ = detector.detectMarkers(
            cv2.cvtColor(img, cv2.COLOR_RGB2GRAY))
        found = {int(i): c.reshape(4, 2)
                 for i, c in zip(ids.flatten(), corners)}
        print(f"frame {f}: detected", sorted(found))
        x0, y0, x1, y1 = crop
        ax.imshow(img[y0:y1, x0:x1])
        ax.axis("off")
        ax.set_title(title, fontsize=10)
        for mid, quad in found.items():
            q = quad - np.array([x0, y0])
            if q[:, 0].min() < 0 or q[:, 1].min() < 0:
                continue
            ax.add_patch(Polygon(q, closed=True, fill=False,
                                 ec="#ffd60a", lw=2.2))
            cen = q.mean(axis=0)
            ax.annotate(roles[mid], xy=(cen[0], cen[1]),
                        xytext=(cen[0], cen[1] - 42), fontsize=10,
                        color="white", ha="center",
                        bbox=dict(boxstyle="round,pad=0.25", fc="#1d3557",
                                  alpha=0.9),
                        arrowprops=dict(arrowstyle="->", color="white",
                                        lw=1.4))
        if 1 not in found:
            # bottom-right, clear of the desk marker and its label
            ax.annotate("object marker\nnot detected", xy=(0.78, 0.15),
                        xycoords="axes fraction", fontsize=10, color="white",
                        ha="center",
                        bbox=dict(boxstyle="round,pad=0.3", fc="#9d0208",
                                  alpha=0.92))
    plt.tight_layout()
    out = FIG / "ch9_fig_marker_blocked.png"
    plt.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("saved", out)


if __name__ == "__main__":
    cap = capture()
    landmark_figure(cap)
    marker_figure()

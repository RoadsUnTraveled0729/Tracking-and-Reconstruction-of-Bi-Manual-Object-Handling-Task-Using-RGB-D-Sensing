#!/usr/bin/env python3
"""Chapter 2 MediaPipe landmark figure (V7 rewrite round).

Runs the project's MediaPipe pose model on the pinned R6B scene frame
(frame 533 of the rail recording) in image mode and draws the full
33-landmark output, with the eight upper-body landmarks this system
consumes highlighted and numbered.

Output: writing/v7/figures/ch2_fig_mediapipe.png
Run:    python writing/v7/scripts/make_ch2_mp_fig.py
"""
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "writing" / "v7" / "figures" / "src" / "r6b_frame00533.png"
USED = {11, 12, 13, 14, 15, 16, 23, 24}

# standard BlazePose 33-landmark topology
CONNECTIONS = [(0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),
               (9, 10), (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),
               (17, 19), (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
               (11, 23), (12, 24), (23, 24), (23, 25), (24, 26), (25, 27), (26, 28),
               (27, 29), (28, 30), (29, 31), (30, 32), (27, 31), (28, 32)]

models = sorted((REPO / "v1" / "mediapipe" / "models").glob("pose_landmarker_*.task"))
assert models, "no pose_landmarker model found"
model_path = str(models[0])
print("model:", model_path)

img = cv2.imread(str(SRC))
assert img is not None
h, w = img.shape[:2]

options = mp_vision.PoseLandmarkerOptions(
    base_options=mp_python.BaseOptions(model_asset_path=model_path,
                                       delegate=mp_python.BaseOptions.Delegate.CPU),
    running_mode=mp_vision.RunningMode.IMAGE,
    num_poses=1,
    min_pose_detection_confidence=0.3,
    min_pose_presence_confidence=0.3,
)
landmarker = mp_vision.PoseLandmarker.create_from_options(options)
mp_img = mp.Image(image_format=mp.ImageFormat.SRGB,
                  data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
res = landmarker.detect(mp_img)
assert res.pose_landmarks, "no pose detected"
lms = res.pose_landmarks[0]
print("landmarks:", len(lms))

pts = [(int(round(lm.x * w)), int(round(lm.y * h))) for lm in lms]

ov = img.copy()
for a, b in CONNECTIONS:
    cv2.line(ov, pts[a], pts[b], (255, 255, 255), 2, cv2.LINE_AA)
for i, (u, v) in enumerate(pts):
    if i in USED:
        cv2.circle(ov, (u, v), 7, (60, 220, 60), -1, cv2.LINE_AA)
        cv2.circle(ov, (u, v), 7, (0, 90, 0), 2, cv2.LINE_AA)
        cv2.putText(ov, str(i), (u + 9, v - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(ov, str(i), (u + 9, v - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (80, 255, 80), 1, cv2.LINE_AA)
    else:
        cv2.circle(ov, (u, v), 4, (80, 160, 255), -1, cv2.LINE_AA)

legend = ["green, numbered: the 8 landmarks this system uses",
          "orange: the other 25 of MediaPipe's 33 landmarks"]
y0 = h - 40
for k, line in enumerate(legend):
    y = y0 + 18 * k
    cv2.putText(ov, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(ov, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)

out = REPO / "writing" / "v7" / "figures" / "ch2_fig_mediapipe.png"
cv2.imwrite(str(out), ov)
print("saved", out)

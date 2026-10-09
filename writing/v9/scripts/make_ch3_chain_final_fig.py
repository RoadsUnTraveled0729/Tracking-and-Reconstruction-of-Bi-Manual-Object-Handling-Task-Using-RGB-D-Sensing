#!/usr/bin/env python3
"""Draw Figure 3.3(a) with the L24 annotation above the rail (D-096).

Copied from the frozen V7 generator into the active condensed V8 track.
The frame-533 photo, points, orientations and axis lengths are retained.
Only the L24 drawing and its label are moved in image space.
Run this before make_ch3_condensed_figs.py.
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np
import cv2

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "v1" / "kinematics"))
from root_frame import build_root_frame  # noqa: E402
from shoulder import solve_right_arm, recompose_shoulder  # noqa: E402

FRAME = 533
IMGPATH = REPO / "writing" / "v9" / "figures" / "src" / f"r6b_frame{FRAME:05d}.png"
CSVF = REPO / "v1" / "mediapipe" / "output" / "recording_20260831_065553_landmarks_filtered.csv"
META = REPO / "v1" / "aruco" / "output" / "recording_20260831_065553_aruco_raw.meta.json"
OUT = REPO / "writing" / "v9" / "figures" / "ch3_fig_chain_photo.png"

intr = json.loads(META.read_text())["color_intrinsics"]
FX, FY, CX, CY = intr["fx"], intr["fy"], intr["ppx"], intr["ppy"]
F = np.array([1.0, -1.0, 1.0])

names = ["left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
         "left_wrist", "right_wrist", "left_hip", "right_hip"]
with open(CSVF) as f:
    for row in csv.DictReader(f):
        if int(row["frame"]) == FRAME:
            break
P_cam = {n: np.array([float(row[n + "_x"]), float(row[n + "_y"]),
                      float(row[n + "_z"])]) for n in names}
P = {n: F * P_cam[n] for n in names}


def px(p_cam):
    return (int(round(FX * p_cam[0] / p_cam[2] + CX)),
            int(round(FY * p_cam[1] / p_cam[2] + CY)))


R_root = build_root_frame(P["left_hip"], P["right_hip"], P["right_shoulder"])
sh, el, ok = solve_right_arm(P["right_shoulder"], P["right_elbow"],
                             P["right_wrist"], R_root)
R_arm = R_root @ recompose_shoulder(sh)
print("shoulder solved:", np.round(sh, 2), "twist_ok:", ok)

img = cv2.imread(str(IMGPATH))
assert img is not None

AXCOL = {"x": (0, 0, 235), "y": (40, 190, 40), "z": (235, 120, 0)}  # BGR


def draw_frame(o_name, R, length, tag, tag_dxy, display_dxy=(0, 0)):
    # D-096: translate only the drawn annotation, never the measured points.
    def display_px(point):
        x, y = px(point)
        return (x + display_dxy[0], y + display_dxy[1])

    o_cam = P_cam[o_name]
    for k, axname in enumerate("xyz"):
        a = R[:, k]
        tip_cam = o_cam + length * (F * a)
        cv2.arrowedLine(img, display_px(o_cam), display_px(tip_cam), AXCOL[axname], 3,
                        cv2.LINE_AA, tipLength=0.14)
    p = display_px(o_cam)
    cv2.circle(img, p, 6, (255, 255, 255), -1, cv2.LINE_AA)
    cv2.circle(img, p, 6, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(img, tag, (p[0] + tag_dxy[0], p[1] + tag_dxy[1]),
                cv2.FONT_HERSHEY_SIMPLEX, 0.58, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(img, tag, (p[0] + tag_dxy[0], p[1] + tag_dxy[1]),
                cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 1, cv2.LINE_AA)


# arm segments faintly underneath, so the frames read as sitting on the arm
for a, b in [("right_shoulder", "right_elbow"), ("right_elbow", "right_wrist")]:
    cv2.line(img, px(P_cam[a]), px(P_cam[b]), (200, 200, 200), 2, cv2.LINE_AA)

draw_frame("right_hip", R_root, 0.22, "root frame (L24)", (14, 5),
           display_dxy=(0, -55))
draw_frame("right_shoulder", R_root, 0.13, "L12 frame: root orientation", (-150, -36))
draw_frame("right_elbow", R_arm, 0.16, "L14 arm frame: x along the arm", (-228, 30))

legend = ["x red, y green, z blue; L24 axes shifted up for visibility",
          "subject faces the sensor, so the subject's right is on the left"]
h = img.shape[0]
for k, line in enumerate(legend):
    y = h - 38 + 18 * k
    cv2.putText(img, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.47,
                (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(img, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.47,
                (255, 255, 255), 1, cv2.LINE_AA)

cv2.imwrite(str(OUT), img)
print("saved", OUT)

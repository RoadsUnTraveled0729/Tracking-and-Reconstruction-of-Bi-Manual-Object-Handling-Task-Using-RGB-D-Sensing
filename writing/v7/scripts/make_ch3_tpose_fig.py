#!/usr/bin/env python3
"""Chapter 3 reference-configuration figure from the T-pose photograph.

The participant stands in the T-pose in the laboratory (user photograph,
writing/v7/figures/src/tpose.jpg), which is the zero configuration of
every arm angle of Chapter 3. MediaPipe Pose (the same detector as the
pipeline, image mode) finds the eight landmarks on the photograph, and
the frames of the kinematic chain are drawn at their zero configuration:
  root frame at the right hip L24 (x to the participant's right, y up,
  z out of the chest toward the viewer, drawn foreshortened);
  shoulder frames at L12 and L11 with the root's orientation;
  elbow frames at L14 and L13 with x along the upper arm (the right arm
  along +x, the left along the mirror);
  the left hip L23 with the root's orientation and the two wrists L15,
  L16 with x along the forearm, so that every landmark of the model
  carries its frame in the picture.
The crop keeps the camera on its mount, the desk with the rail, and the
wall marker in the picture; the background is desaturated so the body
and the drawn axes read first. Panel (b) is the existing Unity reference
pose (ch3_fig_reference_pose.png) for comparison.

Output: writing/v7/figures/ch3_fig_tpose.png
Run:    python writing/v7/scripts/make_ch3_tpose_fig.py [--photo PATH]
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v7" / "figures"
sys.path.insert(0, str(REPO / "v1" / "mediapipe"))

ap = argparse.ArgumentParser()
ap.add_argument("--photo", default=str(FIG / "src" / "tpose.jpg"))
ap.add_argument("--crop", default="1000,420,3620,3024",
                help="x0,y0,x1,y1 in source pixels (default: the crop of "
                     "the 4032 by 3024 photograph that keeps the camera on "
                     "its mount at the bottom right, the desk with the "
                     "rail, and the wall marker behind the participant)")
args = ap.parse_args()

img = cv2.imread(args.photo)
assert img is not None, f"photo not found: {args.photo}"
H, W = img.shape[:2]

# --- landmarks with the pipeline's detector, image mode --------------------
import mediapipe as mp  # noqa: E402
from mediapipe.tasks import python as mp_python  # noqa: E402
from mediapipe.tasks.python import vision as mp_vision  # noqa: E402
model = REPO / "v1" / "mediapipe" / "models" / "pose_landmarker_heavy.task"
options = mp_vision.PoseLandmarkerOptions(
    base_options=mp_python.BaseOptions(model_asset_path=str(model)),
    running_mode=mp_vision.RunningMode.IMAGE, num_poses=1)
lm = mp_vision.PoseLandmarker.create_from_options(options).detect(
    mp.Image(image_format=mp.ImageFormat.SRGB,
             data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
assert lm.pose_landmarks, "no person detected on the photograph"
P = {i: (lm.pose_landmarks[0][i].x * W, lm.pose_landmarks[0][i].y * H)
     for i in (11, 12, 13, 14, 15, 16, 23, 24)}
for i, (u, v) in P.items():
    print("L%d pixel (%.0f, %.0f) vis %.2f" % (i, u, v,
                                              lm.pose_landmarks[0][i].visibility))

# --- crop: around the body, widened so the camera (bottom right) and the
# wall marker (behind the head) stay inside ---------------------------------
if args.crop:
    x0, y0, x1, y1 = [int(v) for v in args.crop.split(",")]
else:
    xs = [p[0] for p in P.values()]; ys = [p[1] for p in P.values()]
    x0 = int(max(0, min(xs) - 0.20 * W)); x1 = int(min(W, max(xs) + 0.28 * W))
    y0 = int(max(0, min(ys) - 0.28 * H)); y1 = H
crop = img[y0:y1, x0:x1].copy()

# --- clean the background: desaturate and lift, keep the person readable --
hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV).astype(np.float32)
hsv[..., 1] *= 0.45
hsv[..., 2] = np.clip(hsv[..., 2] * 0.92 + 30, 0, 255)
soft = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

# --- draw the zero-configuration frames -----------------------------------
def pt(i):
    u, v = P[i]
    return np.array([u - x0, v - y0])

def arrow(ax, o, d, colour, label, lw=2.6, fs=10, lab_off=(0, 0)):
    ax.annotate("", xy=(o[0] + d[0], o[1] + d[1]), xytext=(o[0], o[1]),
                arrowprops=dict(arrowstyle="-|>", color=colour, lw=lw,
                                shrinkA=0, shrinkB=0, mutation_scale=16))
    ax.text(o[0] + d[0] + lab_off[0], o[1] + d[1] + lab_off[1], label,
            color=colour, fontsize=fs, weight="bold",
            ha="center", va="center",
            bbox=dict(fc="white", ec="none", alpha=0.75, pad=1.2))

def frame(ax, o, L, label, right_arm_x=None, tag_off=(0, 0)):
    """x to the participant's right = image left (or along the arm when
    right_arm_x is given, a unit image vector), y up, z toward the viewer
    (drawn short and slanted down-left, the usual foreshortening)."""
    x = np.array(right_arm_x) if right_arm_x is not None else np.array([-1.0, 0.0])
    y = np.array([0.0, -1.0])
    z = np.array([-0.45, 0.55])
    arrow(ax, o, L * x, "#d62728", "x", lab_off=(-8 * np.sign(x[0]) if x[0] else 0, -6))
    arrow(ax, o, L * y, "#2ca02c", "y", lab_off=(0, -8))
    arrow(ax, o, 0.6 * L * z, "#1f77b4", "z", lab_off=(-8, 8))
    ax.plot(o[0], o[1], "o", ms=7, mfc="white", mec="k", mew=1.6, zorder=5)
    ax.text(o[0] + tag_off[0], o[1] + tag_off[1], label, fontsize=9.5,
            weight="bold", ha="center", va="center",
            bbox=dict(fc="white", ec="0.3", lw=0.8, boxstyle="round,pad=0.25"))

fig = plt.figure(figsize=(12.5, 6.2))
gs = fig.add_gridspec(1, 2, width_ratios=[1.45, 1.0], wspace=0.04)
ax = fig.add_subplot(gs[0, 0])
ax.imshow(soft)
h = crop.shape[0]
L = 0.085 * h
frame(ax, pt(24), 1.15 * L, "root frame (L24)", tag_off=(-0.13 * h, 0.12 * h))
frame(ax, pt(23), 0.85 * L, "hip (L23)", tag_off=(0.12 * h, 0.12 * h))
frame(ax, pt(12), 0.85 * L, "shoulder frame (L12)", tag_off=(-0.17 * h, -0.11 * h))
frame(ax, pt(11), 0.85 * L, "shoulder frame (L11)", tag_off=(0.17 * h, -0.11 * h))
ua_r = pt(14) - pt(12); ua_r /= np.linalg.norm(ua_r)
ua_l = pt(13) - pt(11); ua_l /= np.linalg.norm(ua_l)
fa_r = pt(16) - pt(14); fa_r /= np.linalg.norm(fa_r)
fa_l = pt(15) - pt(13); fa_l /= np.linalg.norm(fa_l)
frame(ax, pt(14), 0.85 * L, "elbow frame (L14)", right_arm_x=ua_r, tag_off=(-0.02 * h, 0.09 * h))
frame(ax, pt(13), 0.85 * L, "elbow frame (L13)", right_arm_x=-ua_l, tag_off=(0.02 * h, 0.09 * h))
frame(ax, pt(16), 0.75 * L, "wrist (L16)", right_arm_x=fa_r, tag_off=(-0.04 * h, 0.17 * h))
frame(ax, pt(15), 0.75 * L, "wrist (L15)", right_arm_x=-fa_l, tag_off=(0.04 * h, 0.17 * h))
# the chain, faint
for a, b in ((12, 14), (14, 16), (11, 13), (13, 15), (11, 12), (11, 23), (12, 24), (23, 24)):
    ax.plot([pt(a)[0], pt(b)[0]], [pt(a)[1], pt(b)[1]], color="white", lw=1.4, alpha=0.7)
ax.set_xticks([]); ax.set_yticks([])
ax.set_title("(a) the participant in the T-pose, the zero of every arm angle", fontsize=10.5, loc="left")

bx = fig.add_subplot(gs[0, 1])
ref = cv2.cvtColor(cv2.imread(str(FIG / "ch3_fig_reference_pose.png")), cv2.COLOR_BGR2RGB)
bx.imshow(ref); bx.set_xticks([]); bx.set_yticks([]); bx.set_anchor("C")
bx.set_title("(b) the reference configuration of the rig", fontsize=10.5, loc="left")
out = FIG / "ch3_fig_tpose.png"
plt.savefig(out, dpi=170, bbox_inches="tight")
print("saved", out, "crop", (x0, y0, x1, y1))

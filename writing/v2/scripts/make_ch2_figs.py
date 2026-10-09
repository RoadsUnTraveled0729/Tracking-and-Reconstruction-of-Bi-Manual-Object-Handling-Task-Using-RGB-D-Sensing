#!/usr/bin/env python3
"""Generate Chapter 2 figures into writing/v2/figures/."""
import json, shutil
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import cv2
import pandas as pd

ROOT = "/home/luo/Desktop/New_SandBox"
FIG = ROOT + "/writing/v2/figures"
meta = json.load(open(ROOT + "/mediapipe/output/recording_20260224_083945_landmarks_raw_v2.meta.json"))
ci = meta["color_intrinsics"]
fx, fy, cx, cy = ci["fx"], ci["fy"], ci["ppx"], ci["ppy"]
dist = np.array(ci.get("coeffs", [0, 0, 0, 0, 0]), dtype=np.float64)
K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])

img = cv2.imread(ROOT + "/integration/dataset/real_color_frame100.png")
assert img is not None
df = pd.read_csv(ROOT + "/mediapipe/output/recording_20260224_083945_landmarks_filtered_v2.csv")
row = df[df["frame"] == 100].iloc[0]
NAMES = {11: "left_shoulder", 12: "right_shoulder", 13: "left_elbow", 14: "right_elbow",
         15: "left_wrist", 16: "right_wrist", 23: "left_hip", 24: "right_hip"}
P = {}
for lid, name in NAMES.items():
    P[lid] = np.array([row[f"{name}_x"], row[f"{name}_y"], row[f"{name}_z"]])

def to_px(p):
    return int(round(fx * p[0] / p[2] + cx)), int(round(fy * p[1] / p[2] + cy))

# ---- Fig 2.2: landmark overlay on the real frame ----
BONES = [(11, 12), (11, 13), (13, 15), (12, 14), (14, 16), (11, 23), (12, 24), (23, 24)]
ov = img.copy()
for a, b in BONES:
    cv2.line(ov, to_px(P[a]), to_px(P[b]), (255, 255, 255), 2, cv2.LINE_AA)
for lid in NAMES:
    u, v = to_px(P[lid])
    cv2.circle(ov, (u, v), 6, (60, 220, 60), -1, cv2.LINE_AA)
    cv2.circle(ov, (u, v), 6, (0, 90, 0), 1, cv2.LINE_AA)
    cv2.putText(ov, f"L{lid}", (u + 8, v - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(ov, f"L{lid}", (u + 8, v - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (80, 255, 80), 1, cv2.LINE_AA)
cv2.imwrite(FIG + "/fig2_landmarks_frame100.png", ov)

# ---- Fig 2.3: two-panel photo + 3D vectors from sensor origin ----
fig = plt.figure(figsize=(11, 4.6))
ax1 = fig.add_subplot(1, 2, 1)
ax1.imshow(cv2.cvtColor(ov, cv2.COLOR_BGR2RGB))
ax1.set_title("(a) Detected landmarks, frame 100")
ax1.axis("off")
ax2 = fig.add_subplot(1, 2, 2, projection="3d")
# camera frame axes (x right, y down, z forward); display mapping X=x, Y=z, Z=-y
L = 0.35
ax2.quiver(0, 0, 0, L, 0, 0, color="crimson"); ax2.text(L, 0, 0, "x", color="crimson")
ax2.quiver(0, 0, 0, 0, 0, -L, color="seagreen"); ax2.text(0, 0, -L, "y (down)", color="seagreen")
ax2.quiver(0, 0, 0, 0, L, 0, color="royalblue"); ax2.text(0, L, 0, "z (depth)", color="royalblue")
for lid, p in P.items():
    X, Y, Z = p[0], p[2], -p[1]
    ax2.plot([0, X], [0, Y], [0, Z], color="0.75", lw=0.8)
    ax2.scatter(X, Y, Z, color="seagreen", s=25)
    ax2.text(X, Y, Z, f" L{lid}", fontsize=7)
ax2.scatter(0, 0, 0, color="k", s=40, marker="s")
ax2.text(0, 0, 0.06, " sensor origin", fontsize=8)
ax2.set_xlabel("x (m)"); ax2.set_ylabel("z (m)"); ax2.set_zlabel("-y (m)")
ax2.set_title("(b) Position vectors in the camera frame")
ax2.view_init(elev=18, azim=-55)
plt.tight_layout()
plt.savefig(FIG + "/fig3_landmark_vectors.png", dpi=150)
plt.close()

# ---- Fig 2.4: ArUco detection overlay + axes ----
ar = img.copy()
_params = cv2.aruco.DetectorParameters()
_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_APRILTAG
det = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50), _params)
corners, ids, _ = det.detectMarkers(ar)
cv2.aruco.drawDetectedMarkers(ar, corners, ids)
SIZE = {0: 0.150, 2: 0.050, 1: 0.050}
if ids is not None:
    for c, mid in zip(corners, ids.flatten()):
        L = SIZE.get(int(mid), 0.05)
        obj = np.array([[-L/2, L/2, 0], [L/2, L/2, 0], [L/2, -L/2, 0], [-L/2, -L/2, 0]], dtype=np.float64)
        ok, rvec, tvec = cv2.solvePnP(obj, c.reshape(4, 2).astype(np.float64), K, dist,
                                      flags=cv2.SOLVEPNP_IPPE_SQUARE)
        if ok:
            cv2.drawFrameAxes(ar, K, dist, rvec, tvec, L * 0.75, 2)
cv2.imwrite(FIG + "/fig4_aruco_frame100.png", ar)
print("aruco ids detected:", None if ids is None else sorted(ids.flatten().tolist()))

# ---- Fig 2.1: system flow diagram ----
def box(ax, x, y, w, h, text, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012",
                                fc=fc, ec="0.25", lw=1.1))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=8.6)
def arrow(ax, x0, y0, x1, y1, text=None):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=13, color="0.2", lw=1.2))
    if text:
        ax.text((x0+x1)/2 + 0.005, (y0+y1)/2, text, fontsize=7.3, color="0.25", ha="left")
fig, ax = plt.subplots(figsize=(10.5, 5.6))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
C_SENS, C_A, C_B, C_F = "#dbe9f6", "#e3f2df", "#fdeeda", "#ece1f2"
box(ax, 0.02, 0.42, 0.15, 0.16, "RealSense D435\nrecording (.bag)\n640x480 @ 30 fps", C_SENS)
box(ax, 0.22, 0.42, 0.15, 0.16, "Frame replay +\ndepth-to-color\nalignment", C_SENS)
box(ax, 0.44, 0.68, 0.16, 0.15, "MediaPipe Pose\n8 upper-body\nlandmarks + visibility", C_A)
box(ax, 0.64, 0.68, 0.15, 0.15, "Depth fusion +\nvalidity gating +\nglitch filter", C_A)
box(ax, 0.82, 0.68, 0.16, 0.15, "Kinematic solver\njoint angles\n(Chapter 3)", C_A)
box(ax, 0.44, 0.17, 0.16, 0.15, "ArUco detection\nIPPE pose per\nmarker", C_B)
box(ax, 0.64, 0.17, 0.15, 0.15, "Scene calibration\n+ world anchoring\n(desk frame)", C_B)
box(ax, 0.82, 0.17, 0.16, 0.15, "Object track\nfilter (world\nframe)", C_B)
box(ax, 0.70, 0.42, 0.13, 0.15, "Data fusion\n(shared frame\nindex)", C_F)
box(ax, 0.86, 0.42, 0.12, 0.15, "Unity scene\n(Chapter 5)", C_F)
arrow(ax, 0.17, 0.50, 0.22, 0.50)
arrow(ax, 0.37, 0.53, 0.44, 0.74, "color + depth")
arrow(ax, 0.37, 0.47, 0.44, 0.26, "color")
arrow(ax, 0.60, 0.755, 0.64, 0.755)
arrow(ax, 0.79, 0.755, 0.82, 0.755)
arrow(ax, 0.895, 0.68, 0.77, 0.57)
arrow(ax, 0.60, 0.245, 0.64, 0.245)
arrow(ax, 0.79, 0.245, 0.82, 0.245)
arrow(ax, 0.895, 0.32, 0.77, 0.43)
arrow(ax, 0.83, 0.495, 0.86, 0.495)
ax.text(0.845, 0.60, "shm / UDP", fontsize=7.3, color="0.25", ha="center")
ax.text(0.52, 0.93, "Pipeline A: person tracking", fontsize=9.5, color="#3a6b35")
ax.text(0.52, 0.055, "Pipeline B: scene and object tracking", fontsize=9.5, color="#8a5a1e")
plt.tight_layout()
plt.savefig(FIG + "/fig1_system_flow.png", dpi=150)
plt.close()

# ---- Fig 2.5: pinhole + alignment schematic ----
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
ax = axes[0]
ax.set_xlim(-0.6, 3.2); ax.set_ylim(-1.4, 1.4); ax.axis("off")
ax.scatter([0], [0], color="k", s=45, marker="s")
ax.annotate("camera centre", (0, 0), textcoords="offset points", xytext=(-12, -16), fontsize=8)
ax.add_patch(FancyArrowPatch((0, 0), (0.9, 0), arrowstyle="-|>", mutation_scale=12, color="royalblue"))
ax.text(0.92, 0.03, "z (optical axis)", fontsize=8, color="royalblue")
ax.add_patch(FancyArrowPatch((0, 0), (0, -0.7), arrowstyle="-|>", mutation_scale=12, color="seagreen"))
ax.text(0.03, -0.8, "y (down)", fontsize=8, color="seagreen")
ax.plot([0.7, 0.7], [-1.0, 1.0], color="0.3", lw=1.4)
ax.text(0.66, 1.06, "image plane (z = f)", fontsize=8)
Ppt = (2.6, 0.9)
ax.scatter(*Ppt, color="crimson", s=30)
ax.text(Ppt[0]+0.05, Ppt[1], "scene point p = (x, y, z)", fontsize=8)
ax.plot([0, Ppt[0]], [0, Ppt[1]], color="0.55", ls="--", lw=1)
s = 0.7 / Ppt[0]
ax.scatter([0.7], [Ppt[1]*s], color="crimson", s=22, marker="x")
ax.text(0.74, Ppt[1]*s - 0.02, "(u, v)", fontsize=8)
ax.set_title("(a) Pinhole projection geometry", fontsize=10)
ax = axes[1]
ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
ax.add_patch(FancyBboxPatch((0.4, 3.4), 2.8, 1.9, boxstyle="round,pad=0.05", fc="#dbe9f6", ec="0.3"))
ax.text(1.8, 4.35, "depth imager\n640x480\n(IR stereo pair)", ha="center", fontsize=8)
ax.add_patch(FancyBboxPatch((0.4, 0.6), 2.8, 1.9, boxstyle="round,pad=0.05", fc="#e3f2df", ec="0.3"))
ax.text(1.8, 1.55, "colour camera\n640x480\nK: fx fy cx cy", ha="center", fontsize=8)
ax.add_patch(FancyBboxPatch((5.6, 2.0), 3.9, 2.0, boxstyle="round,pad=0.05", fc="#fdeeda", ec="0.3"))
ax.text(7.55, 3.0, "aligned depth image\nsame 640x480 pixel grid\nas the colour image", ha="center", fontsize=8)
ax.add_patch(FancyArrowPatch((3.3, 4.3), (5.6, 3.4), arrowstyle="-|>", mutation_scale=13, color="0.2"))
ax.text(3.6, 4.35, "reproject via extrinsics\n(known baseline) + K", fontsize=7.6)
ax.add_patch(FancyArrowPatch((3.3, 1.6), (5.6, 2.5), arrowstyle="-|>", mutation_scale=13, color="0.2"))
ax.text(3.9, 1.35, "pixel grid reference", fontsize=7.6)
ax.set_title("(b) Depth-to-colour alignment", fontsize=10)
plt.tight_layout()
plt.savefig(FIG + "/fig5_alignment_schematic.png", dpi=150)
plt.close()

# ---- Fig 2.6: copy the filter QC plot ----
shutil.copy(ROOT + "/mediapipe/output/recording_20260224_083945_landmarks_filtered_v2.qc.png",
            FIG + "/fig6_filter_qc.png")

print("figures written to", FIG)

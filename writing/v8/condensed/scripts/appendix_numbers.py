#!/usr/bin/env python3
"""Compute every number the V7 appendix text prints.

Sources, all frozen artifacts of the rail recording
(recording_20260831_065553; rail-only round 2026-09-01, replacing the
R5 loop recording):
  - the raw landmark CSV and its metadata (Appendix C and D examples),
  - the raw marker CSV and its metadata (Appendix E example),
  - the filter metadata (Appendix F parameters),
  - the recorded session file itself (Appendix A file size).

The pinned worked-example frame is 533, the frame of the Chapter 3
worked example (see ch3_numbers.py for the selection criteria).
Rerun this script to regenerate the values hardcoded in
build_appendix.py.
"""
import csv
import json
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[4]
LM_CSV = (REPO / "v1" / "mediapipe" / "output"
          / "recording_20260831_065553_landmarks_raw.csv")
LM_META = LM_CSV.with_suffix("").with_name(LM_CSV.stem + ".meta.json")
FT_META = (REPO / "v1" / "mediapipe" / "output"
           / "recording_20260831_065553_landmarks_filtered.meta.json")
AR_CSV = (REPO / "v1" / "aruco" / "output"
          / "recording_20260831_065553_aruco_raw.csv")
AR_META = AR_CSV.with_suffix("").with_name(AR_CSV.stem + ".meta.json")
BAG = REPO / "Video" / "recording_20260831_065553.bag"
FRAME = 533

np.set_printoptions(precision=6, suppress=True)

lm_meta = json.loads(LM_META.read_text())
ar_meta = json.loads(AR_META.read_text())
ft_meta = json.loads(FT_META.read_text())
intr = lm_meta["color_intrinsics"]
fx, fy = intr["fx"], intr["fy"]
cx, cy = intr["ppx"], intr["ppy"]

print("== Appendix A: the recorded session file")
print("  file size            : %d bytes = %.2f GB" % (BAG.stat().st_size,
                                                       BAG.stat().st_size / 1e9))
ar_rows = list(csv.DictReader(open(AR_CSV)))
print("  frames               : %d" % lm_meta["frames_total"])
print("  duration             : %.2f s (last frame timestamp)"
      % float(ar_rows[-1]["time_s"]))
raw_payload = lm_meta["frames_total"] * 640 * 480 * (2 + 3)
print("  raw pixel payload    : %.2f GB before compression" % (raw_payload / 1e9))
print("  frame rate estimate  : %.2f fps"
      % ((len(ar_rows) - 1) / float(ar_rows[-1]["time_s"])))

print("\n== Appendix B: platform (versions are read at build time)")

print("\n== Appendix C and D: the landmark example, frame %d" % FRAME)
row = next(r for r in csv.DictReader(open(LM_CSV)) if int(r["frame"]) == FRAME)
print("  frame time           : %.3f s" % float(row["time_s"]))
for name in ("right_wrist", "right_shoulder", "right_elbow"):
    p = np.array([float(row[f"{name}_{a}"]) for a in "xyz"])
    u = fx * p[0] / p[2] + cx
    v = fy * p[1] / p[2] + cy
    print("  %-15s vis=%.4f pixel=(%.0f, %.0f) depth=%.3f xyz=(%+.6f, %+.6f, %+.6f)"
          % (name, float(row[f"{name}_vis"]), u, v, p[2], p[0], p[1], p[2]))
z_w = float(row["right_wrist_z"])
u_w = int(fx * float(row["right_wrist_x"]) / z_w + cx)
v_w = int(fy * float(row["right_wrist_y"]) / z_w + cy)
print("  back-projection check: x = %.3f * (%d - %.5f) / %.5f = %+.6f"
      % (z_w, u_w, cx, fx, z_w * (u_w - cx) / fx))
print("                         y = %.3f * (%d - %.5f) / %.5f = %+.6f"
      % (z_w, v_w, cy, fy, z_w * (v_w - cy) / fy))
print("  normalized range for pixel u=%d: [%.4f, %.4f)"
      % (u_w, u_w / 640, (u_w + 1) / 640))
print("  normalized range for pixel v=%d: [%.4f, %.4f)"
      % (v_w, v_w / 480, (v_w + 1) / 480))

print("\n== Appendix D: the deprojection example (object marker centre)")
ar = next(r for r in ar_rows if int(r["frame"]) == FRAME)
u_m, v_m = int(ar["m1_u"]), int(ar["m1_v"])
z_m = float(ar["m1_depth_z"])
x_m = z_m * (u_m - cx) / fx
y_m = z_m * (v_m - cy) / fy
print("  centre pixel         : (%d, %d)" % (u_m, v_m))
print("  depth sample (5x5 median): %.3f m" % z_m)
print("  x = %.3f * (%d - %.5f) / %.5f = %+.6f" % (z_m, u_m, cx, fx, x_m))
print("  y = %.3f * (%d - %.5f) / %.5f = %+.6f" % (z_m, v_m, cy, fy, y_m))
print("  forward projection back : u = %.4f  v = %.4f"
      % (fx * x_m / z_m + cx, fy * y_m / z_m + cy))
print("  intrinsics           : fx=%.4f fy=%.4f cx=%.4f cy=%.4f" % (fx, fy, cx, cy))
print("  distortion model     : %s coeffs=%s" % (intr["model"], intr["coeffs"]))
print("  field of view        : %.2f x %.2f degrees"
      % (2 * np.degrees(np.arctan(intr["width"] / 2 / fx)),
         2 * np.degrees(np.arctan(intr["height"] / 2 / fy))))

print("\n== Appendix E: the marker example, frame %d" % FRAME)
print("  dictionary           : %s" % ar_meta["aruco_dict"])
print("  corner refinement    : %s" % ar_meta["corner_refinement"])
print("  depth window         : %d by %d" % (ar_meta["depth_window"],
                                             ar_meta["depth_window"]))
for mid in ("0", "1", "2"):
    role = ar_meta["markers"][mid]["role"]
    size = ar_meta["markers"][mid]["size_m"]
    t = np.array([float(ar[f"m{mid}_t{a}"]) for a in "xyz"])
    print("  id %s %-6s size %.3f m pixel=(%s, %s) depth=%s t=(%+.6f, %+.6f, %+.6f) range=%.4f"
          % (mid, role, size, ar[f"m{mid}_u"], ar[f"m{mid}_v"],
             ar[f"m{mid}_depth_z"], t[0], t[1], t[2], np.linalg.norm(t)))

R = np.array([[float(ar[f"m1_r{i}{j}"]) for j in (1, 2, 3)] for i in (1, 2, 3)])
print("  object rotation R =\n", R)
print("  det R                : %.12f" % np.linalg.det(R))
tr = np.trace(R)
theta = np.arccos(np.clip((tr - 1) / 2, -1, 1))
axis = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
axis = axis / (2 * np.sin(theta))
print("  trace                : %.6f" % tr)
print("  angle                : %.4f deg" % np.degrees(theta))
print("  unit axis            : (%+.4f, %+.4f, %+.4f)" % tuple(axis))
Kx = np.array([[0, -axis[2], axis[1]],
               [axis[2], 0, -axis[0]],
               [-axis[1], axis[0], 0]])
print("  [w]x =\n", Kx)
print("  [w]x^2 =\n", Kx @ Kx)
print("  sin(theta) = %.4f   1 - cos(theta) = %.4f"
      % (np.sin(theta), 1 - np.cos(theta)))
R_re = np.eye(3) + np.sin(theta) * Kx + (1 - np.cos(theta)) * (Kx @ Kx)
print("  rebuilt R =\n", R_re)
print("  largest difference from the stored rotation: %.2e"
      % np.abs(R_re - R).max())

print("\n== Appendix F: the candidate filter settings")
for k, v in ft_meta["params"].items():
    print("  %-20s %s" % (k, v))

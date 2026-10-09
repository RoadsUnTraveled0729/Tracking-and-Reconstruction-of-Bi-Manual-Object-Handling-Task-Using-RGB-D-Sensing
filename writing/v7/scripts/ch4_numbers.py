#!/usr/bin/env python3
"""Compute every printed number of the V7 Chapter 4 worked example.
Rail-only round (2026-09-01, E-024/E-025): the example runs on the rail
recording recording_20260831_065553 (calibration scene_calibration_r6bc.json,
wall lobe fixed under E-024). Two pinned frames:
  frame 533 - the scene frame (the Chapter 2 and Chapter 3 frame): the
      object marker is detected and the cleaning step keeps it, so the
      same detection carries the chain from the camera frame into the
      world frame.
  frame 786 - the one frame of the recording on which the object marker
      is not detected. The gap is one frame, inside the filter's bridging
      limit, so the filter bridges it; the cleaning rule then blanks the
      row because the marker was never seen on it, and keeps the
      detections on either side (frames 785 and 787).
Sources (rail artifacts):
  eval/output/recording_20260831_065553_aruco_raw_scaled.csv   detections
  eval/output/scene_calibration_r6bc.json                      calibration
  eval/output/..._scaled_object_world.csv                      raw world track
  eval/output/..._scaled_object_world_filtered.csv             filtered track
  eval/output/..._scaled_object_world_filtered.meta.json       filter counts
  eval/output/..._scaled_object_world_filtered_clean.csv       clean track
The chapter text hardcodes the printed values; rerun this script to
regenerate them.  Speed and angular-rate values are deliberately NOT
printed (skill_set/thesis-structure-rules.md rule 1).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "v1" / "aruco"))
sys.path.insert(0, str(REPO / "eval" / "offset"))
from frames import rt_from_row, make_T, inv_T, chordal_mean  # noqa: E402
import carry  # noqa: E402

STEM = "recording_20260831_065553"
OUT = REPO / "eval" / "output"
RAW = OUT / f"{STEM}_aruco_raw_scaled.csv"
WORLD = OUT / f"{STEM}_scaled_object_world.csv"
CALIB = OUT / "scene_calibration_r6bc.json"
TRACK = OUT / f"{STEM}_scaled_object_world_filtered.csv"
CLEAN = OUT / f"{STEM}_scaled_object_world_filtered_clean.csv"
META = OUT / f"{STEM}_scaled_object_world_filtered.meta.json"

SCENE_FRAME = 533
GAP_FRAME = 786

np.set_printoptions(precision=4, suppress=True)

raw = pd.read_csv(RAW)
calib = json.loads(CALIB.read_text())

print("== Static calibration window (the first 10 detections per static marker)")
Rs, ts = [], []
for _, row in raw.iterrows():
    rt = rt_from_row(row, 2)
    if rt is None:
        continue
    Rs.append(rt[0])
    ts.append(rt[1])
    if len(Rs) == 10:
        break
A = np.mean(np.asarray(Rs), axis=0)
print("  element-wise mean of the ten desk rotations A =\n", A)
print("  det A = %.6f   A^T A - I max = %.2e"
      % (np.linalg.det(A), np.abs(A.T @ A - np.eye(3)).max()))
U, S, Vt = np.linalg.svd(A)
print("  singular values of A:", np.round(S, 6))
R_anchor = chordal_mean(Rs)
print("  projected rotation R (chordal mean) =\n", R_anchor)
print("  det R = %.12f   orth resid = %.2e"
      % (np.linalg.det(R_anchor), np.abs(R_anchor.T @ R_anchor - np.eye(3)).max()))
print("  |R - A| max = %.2e" % np.abs(R_anchor - A).max())
t_anchor = np.mean(ts, axis=0)
print("  mean of the ten desk translations t =", np.round(t_anchor, 4))

T_cam_desk = np.array(calib["T_cam_desk"])
print("  stored T_cam_desk translation =", np.round(T_cam_desk[:3, 3], 4))
print("  reproduction max |diff| = %.2e"
      % np.abs(make_T(R_anchor, t_anchor) - T_cam_desk).max())

print("\n== Inverse anchor: the camera pose in the world frame")
T_desk_cam = inv_T(T_cam_desk)
print("  R^T =\n", T_desk_cam[:3, :3])
print("  -R^T t =", np.round(T_desk_cam[:3, 3], 4))
cam_w = T_desk_cam[:3, 3]
_g = np.array(calib["scene_geometry"]["gravity_up_world"])
_tp = np.array(calib["scene_geometry"]["tabletop_point_world"])
print("  range from the world origin to the camera = %.1f cm"
      % (np.linalg.norm(cam_w) * 100))
print("  camera height above the tabletop plane    = %.1f cm"
      % (float(np.dot(cam_w - _tp, _g)) * 100))

print("\n== Frozen scene description (calibrate_scene.py outputs)")
g = calib["scene_geometry"]
print("  gravity up in world       :", np.round(g["gravity_up_world"], 4))
print("  desk stand tilt vs gravity: %.1f deg" % g["desk_stand_tilt_deg"])
print("  tabletop point in world   :", np.round(g["tabletop_point_world"], 4))
print("  origin above tabletop     : %.1f mm" % (g["origin_above_tabletop_m"] * 1000))
print("  object cube edge          : %.0f mm" % (g["object_cube_size_m"] * 1000))
print("  colour field of view      : %.2f x %.2f deg"
      % (g["sensor_fov_x_deg"], g["sensor_fov_y_deg"]))
w = np.array(calib["poses_world"]["wall"]["T_world"])
print("  wall position in world    :", np.round(w[:3, 3], 4))

print("\n== Chain on the scene frame", SCENE_FRAME)
row = raw[raw.frame == SCENE_FRAME].iloc[0]
R_o, t_o = rt_from_row(row, 1)
print("  time = %.3f s" % row["time_s"])
print("  camera-frame object translation t_cam,obj =", np.round(t_o, 4))
print("  camera-frame object rotation R_cam,obj =\n", R_o)
T_w = T_desk_cam @ make_T(R_o, t_o)
print("  world object translation t_desk,obj =", np.round(T_w[:3, 3], 4))
print("  world object rotation R_desk,obj =\n", T_w[:3, :3])
print("  det = %.12f" % np.linalg.det(T_w[:3, :3]))
h = float(np.dot(T_w[:3, 3] - np.array(g["tabletop_point_world"]),
                 np.array(g["gravity_up_world"])))
print("  height of the marker centre above the tabletop plane = %.1f cm" % (h * 100))
d_cam = float(np.linalg.norm(t_o))
print("  range from the camera = %.2f m" % d_cam)

print("\n== Raw detections and the filter behaviour at the one undetected frame")
dw = pd.read_csv(WORLD)
df = pd.read_csv(TRACK)
dc = pd.read_csv(CLEAN)
fmeta = json.loads(META.read_text())
prm = fmeta["params"]
print("  filter parameters: max_gap %d frames, Savitzky-Golay window %d, "
      "polynomial order %d, rotation window %d"
      % (prm["max_gap"], prm["smooth_window"], prm["smooth_polyorder"],
         prm["rot_window"]))
print("  whole-recording counts: despiked %d, bridged %d, held %d"
      % (fmeta["despiked"], fmeta["bridged"], fmeta["held_boundary"]))

raw_xyz = dw[["tx", "ty", "tz"]].to_numpy(float)
fil_xyz = df[["tx", "ty", "tz"]].to_numpy(float)
det_raw = dw["detected"].to_numpy(int) == 1
filled_f = df["filled"].to_numpy(int) == 1
clean_px = dc["unity_px"].to_numpy(float)


def rows(first, last_):
    print("  frame  det  filled  raw tx (m)   filtered tx (m)  clean px (m)"
          "  |filtered - raw| (mm)")
    for i in range(first, last_ + 1):
        dev = (np.linalg.norm(fil_xyz[i] - raw_xyz[i]) * 1000
               if det_raw[i] else float("nan"))
        print("  %5d  %3d  %6d  %11s  %15.6f  %12s  %11s"
              % (i, int(det_raw[i]), int(filled_f[i]),
                 ("%.6f" % raw_xyz[i, 0]) if det_raw[i] else "-",
                 fil_xyz[i, 0],
                 ("%.6f" % clean_px[i]) if np.isfinite(clean_px[i]) else "-",
                 "-" if not det_raw[i] else "%.1f" % dev))


GAP = GAP_FRAME
rows(GAP - 3, GAP + 3)
prev_det = int(np.flatnonzero(det_raw[:GAP])[-1])
next_det = int(np.flatnonzero(det_raw)[np.flatnonzero(det_raw) > GAP][0])
print("  undetected run: frame %d only, 1 frame (within max_gap %d, so the "
      "filter bridges it)" % (GAP, prm["max_gap"]))
for i in (prev_det, GAP, next_det):
    print("    frame %d raw      =" % i, np.round(raw_xyz[i], 4) if det_raw[i] else "-")
    print("    frame %d filtered =" % i, np.round(fil_xyz[i], 4))
print("  bridged row %d: filtered position vs the mean of its neighbours' "
      "detections = %.1f mm" % (GAP, np.linalg.norm(
          fil_xyz[GAP] - 0.5 * (raw_xyz[prev_det] + raw_xyz[next_det])) * 1000))
for i in (prev_det, next_det):
    print("  kept row %d: |filtered - detection| = %.1f mm"
          % (i, np.linalg.norm(fil_xyz[i] - raw_xyz[i]) * 1000))

print("\n== Cleaning decision around frame", GAP)
pos = df[["unity_px", "unity_py", "unity_pz"]].to_numpy()
Rt = np.array([carry.recompose_zxy(e) for e in
               df[["unity_ex", "unity_ey", "unity_ez"]].to_numpy()])
det = df["detected"].to_numpy() == 1
kept = dc["detected"].to_numpy() == 1
rejected = np.flatnonzero(det & ~kept)
blanked = np.flatnonzero(~det & ~kept)
print("  detected samples rejected by the rule :",
      rejected if len(rejected) else "none on this recording")
print("  undetected rows blanked              :", len(blanked), list(blanked))
last = prev_det
for cand in (GAP, next_det):
    step = float(np.linalg.norm(pos[cand] - pos[last]))
    cosang = (np.trace(Rt[last].T @ Rt[cand]) - 1.0) / 2.0
    ang = float(np.degrees(np.arccos(np.clip(cosang, -1.0, 1.0))))
    print("  candidate frame %d against the last kept sample, frame %d: "
          "%.1f mm, %.2f deg over %d frame interval(s); detected=%s -> %s"
          % (cand, last, step * 1000, ang, cand - last, bool(det[cand]),
             "kept" if kept[cand] else "blanked"))
print("  clean track on the blanked row %d: unity_px = %s (blank)"
      % (GAP, dc.loc[GAP, "unity_px"]))
print("  columns the cleaning step blanks:",
      ["unity_px", "unity_py", "unity_pz", "unity_ex", "unity_ey", "unity_ez"])

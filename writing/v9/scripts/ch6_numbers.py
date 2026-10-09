#!/usr/bin/env python3
"""Number source for the Chapter 6 worked example (Section 6.5, frame 533).

Recomputes, from the committed artifacts, every value the displayed
calculation of Section 6.5 prints: the person path of equation (6.2)
(flip F, swap S, the calibrated camera pose R_cam and t_cam, the anchor
rotation A = S R_cam F, the pelvis point through it), the full transform
of Section 6.4 (proper gravity alignment operator G and floor translation
t_f, composed as T(Scene,Unity)), and the object's inverse path through the link (swap undone,
anchor applied). Values are printed at full precision and rounded to
two decimals (supervisor round 5, C48).

Sources:
  eval/output/scene_calibration_r6bc.json   T_cam_desk (the anchor T_CW),
                                            scene_geometry.gravity_up_unity,
                                            origin_above_tabletop_m
  v2/output/v2_person_dump_r6b_full.csv     frame 533 pelvis (y-up camera frame Camera'),
                                            angles, live mask, solver tags,
                                            per-frame compute time, link flags
  v2/output/v2_object_dump_r6b_full.csv     frame 533 object (display axes)
  v2/output/v2_integrate_dump_r6b_full.csv  tick 533 render time tau, the
                                            interpolation brackets, the merged
                                            flags word and the merged tags word
  v1/mediapipe/output/recording_20260831_065553_landmarks_filtered.csv
                                            measured shoulder, elbow, wrist and
                                            hip landmarks of frame 533
  v1/aruco/output/recording_20260831_065553_aruco_raw.csv
                                            frame 533 marker-1 pixel and the
                                            depth reading at that pixel
  Unity/Assets/Scripts/ArucoSceneReceiver.cs  world.rotation =
      FromToRotation(gravityUpLocal, up); floor at DeskThick + LegH =
      0.72 m below the tabletop plane; world.position raised so the floor
      sits at scene y = 0 (BuildDeferredScene).
  Unity/Assets/Scripts/IntegratedSceneReceiver.cs  PersonAnchor at the
      camera pose composed with Rx(-90); pelvis mapped by
      anchor.TransformPoint.

Run: python writing/v9/scripts/ch6_numbers.py
"""
import csv
import json
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
CALIB = REPO / "eval" / "output" / "scene_calibration_r6bc.json"
PERSON = REPO / "v2" / "output" / "v2_person_dump_r6b_full.csv"
OBJECT = REPO / "v2" / "output" / "v2_object_dump_r6b_full.csv"
INTEGRATE = REPO / "v2" / "output" / "v2_integrate_dump_r6b_full.csv"
LANDMARKS = (REPO / "v1" / "mediapipe" / "output"
             / "recording_20260831_065553_landmarks_filtered.csv")
ARUCO = (REPO / "v1" / "aruco" / "output"
         / "recording_20260831_065553_aruco_raw.csv")
FRAME = 533                             # the clean reference frame of
                                        # Chapters 3 and 4 and Appendices C-E
SLOTS = 8                               # frame-buffer slots, Section 6.1.1
DELAY_FRAMES = 2                        # v2_integrate.py --delay-frames
DESK_THICK, LEG_H = 0.03, 0.69          # ArucoSceneReceiver.cs constants
# v2_integrate.py docstring: flags bit0 person interp, bit1 object interp,
# bit2 person blend, bit3 object blend, bit4 person bridge, bit5 object
# bridge; tags bits 2i..2i+1 = solver tag of live-mask group i
# (0 MEASURED, 1 HELD, 2 CONSTRAINED).
FLAG_BITS = ["person interp", "object interp", "person blend",
             "object blend", "person bridge", "object bridge"]
TAG_NAMES = ["MEASURED", "HELD", "CONSTRAINED"]
GROUP_NAMES = ["root", "R shoulder swing", "R shoulder twist", "R elbow",
               "L shoulder swing", "L shoulder twist", "L elbow"]

np.set_printoptions(precision=6, suppress=True)


def r2(a):
    """Two-decimal display with no negative zero."""
    a = np.round(np.asarray(a, dtype=float), 2) + 0.0
    return a


def show(name, full, unit=""):
    full = np.asarray(full, dtype=float)
    print(f"  {name} =")
    print("    full   :", np.array2string(full, precision=6, suppress_small=True).replace("\n", "\n             "))
    print("    2 dec  :", np.array2string(r2(full), precision=2, suppress_small=True).replace("\n", "\n             "), unit)


def row_at(path, frame, key="frame"):
    with open(path) as f:
        for row in csv.DictReader(f):
            if int(row[key]) == frame:
                return row
    raise KeyError(frame)


def rows_of(path, key="frame"):
    with open(path) as f:
        return {int(row[key]): row for row in csv.DictReader(f)}


def axis(i, angle_deg):
    """Elementary rotation about axis i by angle_deg, the construction the
    frozen kinematics use (root_frame.recompose_zxy, shoulder._rx/_ry/_rz)."""
    a = np.radians(float(angle_deg))
    c, s_ = np.cos(a), np.sin(a)
    if i == 0:
        return np.array([[1, 0, 0], [0, c, -s_], [0, s_, c]])
    if i == 1:
        return np.array([[c, 0, s_], [0, 1, 0], [-s_, 0, c]])
    return np.array([[c, -s_, 0], [s_, c, 0], [0, 0, 1]])


def unit(v):
    return np.asarray(v, dtype=float) / np.linalg.norm(v)


def angle_between(a, b):
    return float(np.degrees(np.arccos(np.clip(unit(a) @ unit(b), -1.0, 1.0))))


def from_to_rotation(a, b):
    """Rotation matrix of the shortest rotation carrying unit vector a onto
    unit vector b (Rodrigues), the matrix form of Unity's
    Quaternion.FromToRotation."""
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    v = np.cross(a, b)
    s = np.linalg.norm(v)
    c = float(np.dot(a, b))
    if s < 1e-12:
        return np.eye(3)
    k = v / s
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + s * K + (1 - c) * K @ K


calib = json.loads(CALIB.read_text())
T_cd = np.array(calib["T_cam_desk"], dtype=float)      # anchor T_CW
R_cd, t_cd = T_cd[:3, :3], T_cd[:3, 3]
R_cam = R_cd.T                                          # camera pose in the world, T_WC
t_cam = -R_cd.T @ t_cd
F = np.diag([1.0, -1.0, 1.0])                           # flip, equation (3.1)
S = np.array([[1.0, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])   # swap, equation (6.1)

print("== Fixed matrices")
show("F", F)
show("S", S)
print("== Calibrated camera pose in the world (blocks of T_WC, Table 2.2)")
show("R_cam = R^T", R_cam)
show("t_cam = -R^T t", t_cam, "m")

print("== Person path, equation (6.2), frame", FRAME)
prow = row_at(PERSON, FRAME)
q = np.array([float(prow["pel_x"]), float(prow["pel_y"]), float(prow["pel_z"])])
show("q (y-up camera frame Camera')", q, "m")
A = S @ R_cam @ F
show("A = S R_cam F", A)
print("  det A =", round(float(np.linalg.det(A)), 6))
St = S @ t_cam
show("S t_cam", St, "m")
Aq = A @ q
show("A q", Aq, "m")
pU = Aq + St
show("p_U = A q + S t_cam", pU, "m")
# cross-check the same point by the three named steps of the prose
p_raw = F @ q
p_w = R_cam @ p_raw + t_cam
print("  raw camera point F q      :", p_raw, "->", np.round(p_raw * 100, 1), "cm")
print("  world point R_cam F q + t :", p_w, "->", np.round(p_w * 100, 1), "cm")
print("  display point S p_w       :", S @ p_w, "->", np.round(S @ p_w * 100, 1), "cm")
print("  |p_U - S p_w| =", float(np.linalg.norm(pU - S @ p_w)))
# rounded-operand check: does A(2 dec) q(2 dec) + St(2 dec) print the same?
pU_rounded = r2(A) @ r2(q) + r2(St)
print("  from rounded operands     :", r2(pU_rounded), " true rounded:", r2(pU),
      " same:", bool(np.all(r2(pU_rounded) == r2(pU))))

print("== Gravity alignment and floor placement, Section 6.4")
g = np.array(calib["scene_geometry"]["gravity_up_unity"], dtype=float)
show("gravity up (display axes)", g)
tilt = np.degrees(np.arccos(np.clip(np.dot(g / np.linalg.norm(g), [0, 1, 0]), -1, 1)))
print("  angle to the screen's vertical:", round(float(tilt), 2), "deg")
G = from_to_rotation(g, np.array([0.0, 1.0, 0.0]))
show("G (proper gravity alignment operator)", G)
print("  G g =", G @ g)
drop = float(calib["scene_geometry"]["origin_above_tabletop_m"])
# ArucoSceneReceiver: onPlane = -g * tabletopDrop, so the tabletop plane
# sits at height -drop along g (above the origin when drop < 0); the floor
# is DeskThick + LegH = 0.72 m below the plane; world.position is raised
# by -floorY so that the floor sits at scene y = 0.
plane_h = -drop
floor_h = plane_h - (DESK_THICK + LEG_H)
raise_y = -floor_h
print("  origin above tabletop:", drop, "m; plane height along g:", round(plane_h, 6),
      "m; floor 0.72 m below the plane at", round(floor_h, 6), "m")
print("  raise so the floor sits at zero height:", round(raise_y, 6), "m")
print("  drawn desk top height:", round(plane_h + raise_y, 6), "m")
Gp = G @ pU
show("G p_U (operation value)", Gp, "m")
t_f = np.array([0.0, raise_y, 0.0])
T_scene_unity = np.eye(4)
T_scene_unity[:3, :3] = G
T_scene_unity[:3, 3] = t_f
show("t_f (floor translation)", t_f, "m")
show("T(Scene,Unity) = [G, t_f; 0, 1]", T_scene_unity)
p_scene_h = T_scene_unity @ np.r_[pU, 1.0]
p_scene = p_scene_h[:3]
show("scene point G p_U + t_f", p_scene, "m")
print("  augmented Scene point:", p_scene_h)
print("  |homogeneous result - (G p_U + t_f)| =", float(np.linalg.norm(p_scene - (Gp + t_f))))
print("  scene point in cm:", np.round(p_scene * 100, 1))
print("  above the drawn desk top by:", round((p_scene[1] - (plane_h + raise_y)) * 100, 1), "cm")
ps_rounded = r2(G) @ r2(pU) + np.array([0.0, round(raise_y, 2), 0.0])
print("  from rounded operands     :", r2(ps_rounded), " true rounded:", r2(p_scene),
      " same:", bool(np.all(r2(ps_rounded) == r2(p_scene))))
# the camera itself in the scene, for the prose sentence
cam_scene = G @ St + t_f
print("  camera in display axes (S t_cam) cm:", np.round(St * 100, 1), "; in the scene cm:", np.round(cam_scene * 100, 1))

print("== Object's inverse path through the link, frame", FRAME)
orow = row_at(OBJECT, FRAME)
pUo = np.array([float(orow["ux"]), float(orow["uy"]), float(orow["uz"])])
show("p_U (object record, display axes)", pUo, "m")
pWo = S @ pUo
show("p_W = S p_U", pWo, "m")
show("R (anchor T_cam_desk rotation)", R_cd)
show("t (anchor translation)", t_cd, "m")
pCo = R_cd @ pWo + t_cd
show("p_C = R p_W + t", pCo, "m")
print("  in cm:", np.round(pCo * 100, 1))
pC_rounded = r2(R_cd) @ r2(pWo) + r2(t_cd)
print("  from rounded operands     :", r2(pC_rounded), " true rounded:", r2(pCo),
      " same:", bool(np.all(r2(pC_rounded) == r2(pCo))))

print("== Object marker pose in the camera frame, frame", FRAME)
# The record's Euler angles are the marker basis in display axes; undoing the
# swap on both sides returns the world basis, and the anchor rotation returns
# the camera basis. The marker's face normal is its third basis vector
# (v1/aruco/frames.py recompose_zxy, Unity's Ry Rx Rz order).
euler_o = np.array([float(orow["ex"]), float(orow["ey"]), float(orow["ez"])])
show("object Euler angles (display axes)", euler_o, "deg")
R_u_obj = axis(1, euler_o[1]) @ axis(0, euler_o[0]) @ axis(2, euler_o[2])
R_c_obj = R_cd @ (S @ R_u_obj @ S)
normal_c = R_c_obj[:, 2]
show("marker face normal in the camera frame", normal_c)
# the face turns towards the camera, so the normal is compared with -z
off_axis = angle_between(normal_c, np.array([0.0, 0.0, -1.0]))
print("  face normal off the optical axis:", round(off_axis, 2), "deg")
arow = row_at(ARUCO, FRAME)
pix = (int(round(float(arow["m1_u"]))), int(round(float(arow["m1_v"]))))
depth_z = float(arow["m1_depth_z"])
print("  marker 1 pixel:", pix, " depth image at that pixel:",
      round(depth_z * 100, 1), "cm")
print("  pose depth:", round(pCo[2] * 100, 1), "cm; depth image nearer by:",
      round((pCo[2] - depth_z) * 100, 1), "cm")

print("== Record flags and states, frame", FRAME)
irow = row_at(INTEGRATE, FRAME, key="tick")
mask = int(prow["mask"])
print("  person live mask:", mask, "(bit i = group i)")
for i, name in enumerate(GROUP_NAMES):
    tag = int(prow[f"tag_{i}"])
    print(f"    group {i} {name:<18} live {(mask >> i) & 1}  tag {tag} {TAG_NAMES[tag]}")
prev = row_at(PERSON, FRAME - 1)
print("  previous frame", FRAME - 1, "mask:", prev["mask"], " tags:",
      [int(prev[f"tag_{i}"]) for i in range(7)])
print("  person compute_ms:", round(float(prow["compute_ms"]), 2),
      " object compute_ms:", round(float(orow["compute_ms"]), 2))
print("  object live bit:", orow["live"], " previous frame", FRAME - 1,
      "live bit:", row_at(OBJECT, FRAME - 1)["live"])
print("  link wrist estimate passed to the solve: rec_right",
      prow["rec_right"], " rec_left", prow["rec_left"])
flags = int(irow["flags"])
print("  merger flags:", flags, "->",
      [n for i, n in enumerate(FLAG_BITS) if (flags >> i) & 1] or ["none"])
tags_word = int(irow["tags"])
print("  merger tags word:", tags_word, "->",
      [f"{GROUP_NAMES[i]} {TAG_NAMES[(tags_word >> (2 * i)) & 3]}"
       for i in range(7) if (tags_word >> (2 * i)) & 3])
print("  merger states: p_state", irow["p_state"], " o_state", irow["o_state"])
print("  slot in the frame buffer:", FRAME, "modulo", SLOTS, "=", FRAME % SLOTS)

print("== Timing offsets around the render time")
prows = rows_of(PERSON)
interval = float(np.median(np.diff([float(prows[f]["time_s"]) for f in sorted(prows)])))
print("  median frame interval:", round(interval * 1000, 3), "ms")
p_f0, p_f1 = int(irow["p_f0"]), int(irow["p_f1"])
o_f0, o_f1 = int(irow["o_f0"]), int(irow["o_f1"])
tau = float(irow["tau"])          # v2_integrate_dump_r6b_full.csv tick FRAME
print("  capture published frame", FRAME, "at time_s:", prow["time_s"])
print("  render time tau:", tau)
print("  person bracket:", p_f0, "to", p_f1, " object bracket:", o_f0, "to", o_f1)
print("  frame", p_f0, "time_s:", prows[p_f0]["time_s"],
      " frame", p_f1, "time_s:", prows[p_f1]["time_s"])
print(f"  {p_f0} before tau by:", round((tau - float(prows[p_f0]["time_s"])) * 1000, 1), "ms;",
      f"{p_f1} after tau by:", round((float(prows[p_f1]["time_s"]) - tau) * 1000, 1), "ms")
tick_time = tau + DELAY_FRAMES * interval
newest = max(f for f in prows if float(prows[f]["time_s"]) <= tick_time)
print("  merger tick clock time (tau +", DELAY_FRAMES, "frame intervals):",
      round(tick_time, 6), "s; newest frame published by then:", newest,
      "at", prows[newest]["time_s"])

print("== Bone directions from the recorded angles, frame", FRAME)
# The receiver composes root, shoulder and elbow as equation (6.5) does
# (root_frame.recompose_zxy, shoulder.recompose_shoulder, the elbow pair),
# then the anchor A and the levelling G carry the axis into the Scene frame.
# The measured direction is the landmark difference through F, A and G.
a = [float(prow[f"a{i}"]) for i in range(13)]
print("  root Euler (a0,a1,a2):", [round(v, 1) for v in a[0:3]], "deg")
print("  R shoulder azimuth, elevation, twist (a3,a4,a5):",
      [round(v, 1) for v in a[3:6]], "deg")
print("  R elbow (a6,a7):", [round(v, 1) for v in a[6:8]], "deg;",
      "bend about the up axis:", round(abs(a[6]), 1), "deg,",
      "about the forward axis:", round(abs(a[7]), 1), "deg")
R_root = axis(1, a[1]) @ axis(0, a[0]) @ axis(2, a[2])
R_sh = axis(1, a[3]) @ axis(2, a[4]) @ axis(0, a[5])
R_el = axis(1, a[6]) @ axis(2, a[7])
x_hat = np.array([1.0, 0.0, 0.0])
upper = G @ A @ R_root @ R_sh @ x_hat
fore = G @ A @ R_root @ R_sh @ R_el @ x_hat
show("right upper arm axis (Scene directions)", unit(upper))
show("right forearm axis (Scene directions)", unit(fore))
lrow = row_at(LANDMARKS, FRAME)


def landmark(name):
    v = np.array([float(lrow[f"{name}_{k}"]) for k in "xyz"])
    return F @ v            # the flip of equation (3.1), as the solve applies


upper_m = G @ A @ (landmark("right_elbow") - landmark("right_shoulder"))
fore_m = G @ A @ (landmark("right_wrist") - landmark("right_elbow"))
print("  upper arm off the measured shoulder-to-elbow direction:",
      round(angle_between(upper, upper_m), 2), "deg")
print("  forearm off the measured elbow-to-wrist direction:",
      round(angle_between(fore, fore_m), 2), "deg")
# the hip landmarks are in raw camera axes, the axes F q returns to
hip_raw = [np.array([float(lrow[f"{n}_{k}"]) for k in "xyz"])
           for n in ("left_hip", "right_hip")]
hip_mid = 0.5 * (hip_raw[0] + hip_raw[1])
print("  hip landmark midpoint (raw camera axes):", np.round(hip_mid, 4),
      " raw camera point F q:", np.round(p_raw, 4))
print("  distance between them:", round(float(np.linalg.norm(hip_mid - p_raw)) * 1000, 1), "mm")
print("  hip preparation flags: left", lrow["left_hip_flag"],
      " right", lrow["right_hip_flag"], "(0 = landmark left unchanged)")

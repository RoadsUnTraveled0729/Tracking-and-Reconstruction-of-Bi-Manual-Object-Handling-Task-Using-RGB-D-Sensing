#!/usr/bin/env python3
"""Number source for the Chapter 6 worked example (Section 6.5, frame 548).

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
  v2/output/v2_person_dump_r6b_full.csv     frame 548 pelvis (y-up camera frame Camera')
  v2/output/v2_object_dump_r6b_full.csv     frame 548 object (display axes)
  Unity/Assets/Scripts/ArucoSceneReceiver.cs  world.rotation =
      FromToRotation(gravityUpLocal, up); floor at DeskThick + LegH =
      0.72 m below the tabletop plane; world.position raised so the floor
      sits at scene y = 0 (BuildDeferredScene).
  Unity/Assets/Scripts/IntegratedSceneReceiver.cs  PersonAnchor at the
      camera pose composed with Rx(-90); pelvis mapped by
      anchor.TransformPoint.

Run: python writing/v8/condensed/scripts/ch6_numbers.py
"""
import csv
import json
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[4]
CALIB = REPO / "eval" / "output" / "scene_calibration_r6bc.json"
PERSON = REPO / "v2" / "output" / "v2_person_dump_r6b_full.csv"
OBJECT = REPO / "v2" / "output" / "v2_object_dump_r6b_full.csv"
FRAME = 548
DESK_THICK, LEG_H = 0.03, 0.69          # ArucoSceneReceiver.cs constants

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


def row_at(path, frame):
    with open(path) as f:
        for row in csv.DictReader(f):
            if int(row["frame"]) == frame:
                return row
    raise KeyError(frame)


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

print("== Timing offsets around the render time")
p547 = row_at(PERSON, 547)
print("  frame 547 time_s:", p547["time_s"], " frame 548 time_s:", prow["time_s"])
tau = 18.250815   # v2_integrate_dump_r6b_full.csv tick 548, tau
print("  render time tau:", tau)
print("  547 before tau by:", round((tau - float(p547["time_s"])) * 1000, 1), "ms;",
      "548 after tau by:", round((float(prow["time_s"]) - tau) * 1000, 1), "ms")

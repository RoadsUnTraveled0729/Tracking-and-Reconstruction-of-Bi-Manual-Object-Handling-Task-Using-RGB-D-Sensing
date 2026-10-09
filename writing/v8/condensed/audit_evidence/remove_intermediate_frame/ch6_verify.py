#!/usr/bin/env python3
"""Verify the D-082 Chapter 6 refactor against its numerical sources.

Run with /home/luo/anaconda3/bin/python. This writes only ch6_checks.json
beside this script. The 1e-9 arithmetic and 2e-6 stored-coordinate tolerances
are the existing diagnostic tolerances in D-072, not experiment thresholds.
The authored rig/spawn-axis coincidence remains an unverified assumption.
"""
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import runpy
import sys
from zipfile import ZipFile

import numpy as np
import pandas as pd
from lxml import etree

REPO = Path(__file__).resolve().parents[5]
CONDENSED = REPO / "writing/v8/condensed"
HERE = Path(__file__).resolve().parent
ARITHMETIC_TOL = 1e-9
STORED_TOL = 2e-6
CHECKS, SOURCES = [], {}


def source(path):
    path = Path(path)
    SOURCES[str(path.relative_to(REPO))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return path


def check(label, condition, **details):
    CHECKS.append({"label": label, "status": "PASS" if condition else "FAIL", **details})


def close(label, actual, expected, tolerance=ARITHMETIC_TOL):
    error = float(np.max(np.abs(np.asarray(actual) - np.asarray(expected))))
    check(label, np.isfinite(error) and error <= tolerance,
          max_absolute_difference=error, tolerance=tolerance)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, source(path))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


sys.path.insert(0, str(REPO / "v1/kinematics"))
import root_frame
import shoulder
source(REPO / "v1/kinematics/root_frame.py")
source(REPO / "v1/kinematics/shoulder.py")
frames = module("ch6_frozen_frames", REPO / "v1/aruco/frames.py")
carry = module("ch6_frozen_carry", REPO / "eval/offset/carry.py")

# Compile the unchanged source function without running the overlay CLI or
# importing its solver and video dependencies.
fk_path = source(REPO / "eval/inspect/check_v1_overlay.py")
fk_tree = ast.parse(fk_path.read_text())
fk_function = next(n for n in fk_tree.body if isinstance(n, ast.FunctionDef) and n.name == "fk_arm_dirs")
fk_scope = {"np": np, "_rx": shoulder._rx, "_ry": shoulder._ry, "_rz": shoulder._rz}
exec(compile(ast.Module(body=[fk_function], type_ignores=[]), str(fk_path), "exec"), fk_scope)
fk_arm_dirs = fk_scope["fk_arm_dirs"]

with contextlib.redirect_stdout(io.StringIO()):
    state = runpy.run_path(str(source(CONDENSED / "scripts/ch6_numbers.py")))
source(REPO / "v2/output/v2_object_dump_r6b_full.csv")
before = json.loads(source(HERE / "ch6_values_before.json").read_text())
names = {"F": "F", "S": "S", "R_cam": "R_world_camera", "t_cam": "p_world_camera",
         "A": "R_unity_camera_prime", "St": "p_unity_camera", "q": "pelvis_camera_prime",
         "pU": "pelvis_unity", "G": "G", "Gp": "G_pelvis_unity", "raise_y": "floor_d",
         "p_scene": "pelvis_scene", "cam_scene": "camera_scene", "pUo": "object_unity",
         "pWo": "object_world", "pCo": "object_camera"}
for current, label in names.items():
    close("Baseline value unchanged: " + label, state[current], before[label])

F, S, G, A = (state[key] for key in ("F", "S", "G", "A"))
R, t, q = (state[key] for key in ("R_cam", "t_cam", "q"))
close("6.1 swap equals the frozen conversion matrix", S, frames.WORLD_TO_UNITY)
object_row = state["orow"]
object_rotation = frames.recompose_zxy([float(object_row[k]) for k in ("ex", "ey", "ez")])
object_world_rotation = S @ object_rotation @ S
source_point, source_rotation = frames.unity_from_world(object_world_rotation, state["pWo"])
close("6.1 point swap reproduces the object record", source_point, state["pUo"])
close("6.1 two-sided marker basis conversion", source_rotation, object_rotation)
close("6.1 swap is self-inverse", S @ S, np.eye(3))
close("6.1 swap reverses handedness", np.linalg.det(S), -1.)

T_camera_world = state["T_cd"]
T_world_camera = frames.inv_T(T_camera_world)
close("6.2 inverse calibration rotation", R, T_world_camera[:3, :3])
close("6.2 inverse calibration translation", t, T_world_camera[:3, 3])
close("6.2 inverse flip equals frozen camera point conversion", F @ q, root_frame.unity_from_sensor(q))
close("6.2 full point path", state["pU"], S @ (T_world_camera @ np.r_[F @ q, 1.])[:3])
T_unity_camera_prime = frames.make_T(A, S @ t)
close("6.2 homogeneous point and affine point agree",
      T_unity_camera_prime @ np.r_[q, 1.], np.r_[state["pU"], 1.])
close("6.2 net anchor rotation is proper", np.linalg.det(A), 1.)
close("6.2 net anchor rotation is orthogonal", A.T @ A, np.eye(3))
close("6.3 factored anchor equals full anchor", (S @ R @ S) @ (S @ F), A)
close("6.3 constant factor is Rx(-90 deg)", S @ F, frames.recompose_zxy([-90., 0., 0.]))

person = pd.read_csv(source(REPO / "v2/output/v2_person_dump_r6b_full.csv"))
angles = person[[f"a{i}" for i in range(13)]].to_numpy()
finite = np.isfinite(angles).all(axis=1)
check("6.4 recorded angle rows are finite", bool(finite.all()), count=int(finite.sum()))
errors = {"right upper": [], "right forearm": [], "left upper": [], "left forearm": []}
for values in angles[finite]:
    R0 = root_frame.recompose_zxy(values[:3])
    for side, start in (("right", 3), ("left", 8)):
        sh, el = values[start:start + 3], values[start + 3:start + 5]
        sign = 1. if side == "right" else -1.
        R1 = shoulder.recompose_shoulder(sh * [sign, sign, 1.])
        ey, ez = np.radians(el * sign)
        R2 = shoulder._ry(ey) @ shoulder._rz(ez)
        rest_axis = np.array([sign, 0., 0.])
        upper, forearm = fk_arm_dirs(sh, el, side)
        errors[side + " upper"].append(R0 @ R1 @ rest_axis - R0 @ upper)
        errors[side + " forearm"].append(R0 @ R1 @ R2 @ rest_axis - R0 @ forearm)
for label, differences in errors.items():
    close("6.4 frame chain agrees with frozen FK: " + label, differences, 0.)

close("6.5 Scene/Camera' leading factor includes G once", G @ A,
      state["T_scene_unity"][:3, :3] @ T_unity_camera_prime[:3, :3])
close("6.5 Scene/Camera' leading factor is proper", np.linalg.det(G @ A), 1.)

receiver_path = source(REPO / "Unity/Assets/Scripts/IntegratedSceneReceiver.cs")
receiver = receiver_path.read_text()
for statement in ("Quaternion qA = anchor.rotation;",
                  "hip.rotation = qA * qRoot * cHip;",
                  "upperArm.rotation = qA * qRoot * qSh * cUpperArm;",
                  "forearm.rotation = qA * qRoot * qSh * qElb * cForearm;",
                  "lUpperArm.rotation = qA * qRoot * qShL * cLUpperArm;",
                  "lForearm.rotation = qA * qRoot * qShL * qElbL * cLForearm;",
                  "Vector3 target = anchor.TransformPoint(pelvis);",
                  "anchor.SetParent(world, false);",
                  "cUpperArm = upperArm.rotation;"):
    check("6.5 frozen receiver source: " + statement, statement in receiver)
scene_receiver = source(REPO / "Unity/Assets/Scripts/ArucoSceneReceiver.cs").read_text()
check("6.5 object pose remains local beneath scene parent",
      "objectNode.localPosition = pos;" in scene_receiver and
      "objectNode.localRotation = Quaternion.Euler(euler);" in scene_receiver)

for calibration, capture, label in (
    ("scene_calibration_r6bc.json", "ch7_trails_revision", "rail"),
    ("scene_calibration_r7c.json", "ch7_handover_trails", "handover")):
    cal = json.loads(source(REPO / "eval/output" / calibration).read_text())
    frozen = carry.LeveledWorld(cal)
    floor_d = float(cal["scene_geometry"]["origin_above_tabletop_m"]) + .03 + .69
    floor_translation = np.array([0., floor_d, 0.])
    transform = frames.make_T(frozen.G, floor_translation)
    g = np.asarray(cal["scene_geometry"]["gravity_up_unity"], float)
    close("6.6 G aligns calibrated gravity: " + label, frozen.G @ (g / np.linalg.norm(g)), [0., 1., 0.])
    close("6.6 G is a proper operator: " + label, np.linalg.det(frozen.G), 1.)
    close("6.6 G is orthogonal: " + label, frozen.G.T @ frozen.G, np.eye(3))
    close("6.6 floor point maps to zero: " + label,
          (transform @ np.r_[-frozen.g * floor_d, 1.])[:3], np.zeros(3))
    close("6.6 stated six-decimal offset: " + label, np.round(floor_d, 6),
          .716215 if label == "rail" else .709312)
    log = pd.read_csv(source(CONDENSED / "figures/src" / capture / "unity_person_log.csv")).drop_duplicates("frame")
    pelvis = log[["pel_x", "pel_y", "pel_z"]].to_numpy()
    unity_points = pelvis @ frozen.M.T + frozen.cam_pos
    direct_scene = (transform @ np.c_[unity_points, np.ones(len(unity_points))].T).T[:, :3]
    close("6.6 homogeneous point path agrees with frozen operations: " + label,
          direct_scene, frozen.level(unity_points) + floor_translation)
    close("6.6 final Scene pelvis agrees with captured global hip: " + label,
          direct_scene, log[["hip_x", "hip_y", "hip_z"]].to_numpy(), STORED_TOL)
    close("6.6 inverse transform restores original Unity point: " + label,
          (np.linalg.inv(transform) @ np.c_[direct_scene, np.ones(len(direct_scene))].T).T[:, :3], unity_points)

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
      "m": "http://schemas.openxmlformats.org/officeDocument/2006/math"}
with ZipFile(source(CONDENSED / "Chapter_6_System_Integration.docx")) as archive:
    xml = etree.fromstring(archive.read("word/document.xml"))
    figure_hash = hashlib.sha256(source(CONDENSED / "figures/ch6_fig_frames.png").read_bytes()).hexdigest()
    check("Rebuilt Chapter 6 embeds the regenerated Figure 6.4",
          figure_hash in [hashlib.sha256(archive.read(name)).hexdigest()
                          for name in archive.namelist() if name.startswith("word/media/")])
equations_before = json.loads(source(HERE / "ch6_equations_before.json").read_text())
for number in ("6.1", "6.2", "6.3", "6.4", "6.5"):
    table = next(table for table in xml.xpath("//w:tbl", namespaces=NS)
                 if "".join(table.xpath(".//w:t/text()", namespaces=NS)).strip("() ") == number)
    math = table.find(".//m:oMath", namespaces=NS)
    check("Numbered equation unchanged: " + number,
          hashlib.sha256(etree.tostring(math, method="c14n")).hexdigest() == equations_before[number])
text = " ".join(xml.xpath("//w:t/text() | //m:t/text()", namespaces=NS))
check("Rebuilt Chapter 6 contains no removed-frame term", "levelled" not in text.lower())
check("Spawn-axis coincidence remains explicitly an assumption",
      "rests on an assumption this thesis states rather than establishes" in text)

result = {
    "status": "PASS" if all(c["status"] == "PASS" for c in CHECKS) else "FAIL",
    "checks": CHECKS, "sources": SOURCES,
    "assumptions_unresolved": [
        "The authored bone axes and the rig's complete spawn-axis coincidence are not established by these numerical checks. Equation 6.5 retains that explicit assumption.",
        "Source checks establish how global bone rotations are assigned. Available captured position logs do not contain full bone orientation matrices."
    ],
    "scope": "Chapter 6 equations 6.1-6.6, original numeric example values, current source semantics and captured final Scene positions. No runtime, solver or data modifications."
}
(HERE / "ch6_checks.json").write_text(json.dumps(result, indent=2) + "\n")
print(result["status"], len(CHECKS), "checks; evidence:", HERE / "ch6_checks.json")
for item in CHECKS:
    if item["status"] == "FAIL":
        print(item)
raise SystemExit(0 if result["status"] == "PASS" else 1)

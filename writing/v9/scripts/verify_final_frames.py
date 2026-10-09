#!/usr/bin/env python3
"""Check the final frame-chain corrections and retained OMML regressions.

Run with the thesis Python. --docx optionally checks the assembled document;
without it, checks the three affected parts. Prints a JSON evidence record.
These tolerances check arithmetic and six-decimal storage, not accuracy of
the experiment: 1e-9 follows ch5_worked_example.py; 2e-6 bounds rounded matrix
entries after levelling plus three rounded Euler angles (D-072).
Visual rendering and the stated spawn-axis assumption are outside this check.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd
from lxml import etree

REPO = Path(__file__).resolve().parents[3]
CONDENSED = REPO / "writing/v9"
for folder in ("eval/offset", "eval/common", "eval/failure",
               "v1/kinematics", "writing/v9/scripts"):
    sys.path.insert(0, str(REPO / folder))

import carry
import ch5_worked_example as example
import paths
import recovery_core

ARITHMETIC_TOL = 1e-9
STORED_POSE_TOL = 2e-6
NS = {"m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
      "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docx", type=Path)
    args = parser.parse_args()
    checks, sources = [], {}

    def source(path):
        path = Path(path)
        label = str(path.relative_to(REPO)) if path.is_relative_to(REPO) else str(path)
        sources[label] = hashlib.sha256(path.read_bytes()).hexdigest()
        return path

    def check(label, condition, **evidence):
        checks.append(dict(label=label, status="PASS" if condition else "FAIL", **evidence))

    def close(label, actual, expected, tolerance=ARITHMETIC_TOL):
        difference = np.asarray(actual) - np.asarray(expected)
        error = float(np.max(np.abs(difference)))
        check(label, np.isfinite(error) and error <= tolerance,
              max_absolute_difference=error, tolerance=tolerance)

    stem = paths.R6B_STEM
    calib = json.loads(source(paths.calib_for(stem)).read_text())
    track = pd.read_csv(source(REPO / f"eval/output/{stem}_scaled_object_world_filtered_clean.csv"))
    world = carry.LeveledWorld(calib)
    sensor_pose = np.linalg.inv(np.asarray(calib["T_cam_desk"]))
    swap = np.array([[1., 0., 0.], [0., 0., 1.], [0., 1., 0.]])
    flip = np.diag([1., -1., 1.])
    # The frozen helper reports positions before floor placement. D-082
    # adds the receiver's actual recording-specific translation to Scene.
    floor_shift = np.array([0., calib["scene_geometry"]["origin_above_tabletop_m"] + .03 + .69, 0.])
    rotation_sc = world.G @ swap @ sensor_pose[:3, :3] @ flip
    origin_sc = world.G @ swap @ sensor_pose[:3, 3] + floor_shift
    transform_sc = np.eye(4)
    transform_sc[:3, :3], transform_sc[:3, 3] = rotation_sc, origin_sc
    transform_cs = np.linalg.inv(transform_sc)
    close("swap determinant is minus one", np.linalg.det(swap), -1.)
    close("flip determinant is minus one", np.linalg.det(flip), -1.)
    close("Camera' to Scene rotation is proper", np.linalg.det(rotation_sc), 1.)
    close("Camera' to Scene rotation is orthogonal", rotation_sc.T @ rotation_sc, np.eye(3))

    rotations = track[[f"r{i}{j}" for i in range(1, 4) for j in range(1, 4)]].to_numpy().reshape(-1, 3, 3)
    positions = track[["tx", "ty", "tz"]].to_numpy()
    unity_positions = track[["unity_px", "unity_py", "unity_pz"]].to_numpy()
    unity_euler = track[["unity_ex", "unity_ey", "unity_ez"]].to_numpy()
    finite = (np.isfinite(rotations).all(axis=(1, 2)) & np.isfinite(positions).all(axis=1)
              & np.isfinite(unity_positions).all(axis=1) & np.isfinite(unity_euler).all(axis=1))
    check("finite stored object poses available", bool(finite.any()), count=int(finite.sum()))
    before_floor, scene_rotations = world.object_world(unity_positions[finite], unity_euler[finite])
    scene_positions = before_floor + floor_shift
    close("Chapter 5 Scene origins match frozen carry plus floor placement",
          positions[finite] @ swap.T @ world.G.T + floor_shift,
          scene_positions, STORED_POSE_TOL)
    close("Chapter 5 mapped orientations from World match carry",
          world.G @ swap @ rotations[finite] @ swap, scene_rotations, STORED_POSE_TOL)
    close("floor translation preserves every consecutive object displacement",
          np.diff(scene_positions, axis=0), np.diff(before_floor, axis=0))
    close("basis conversion and gravity alignment preserve object segment lengths",
          np.linalg.norm(np.diff(positions[finite], axis=0), axis=1),
          np.linalg.norm(np.diff(positions[finite] @ swap.T @ world.G.T, axis=0), axis=1))

    inputs, worked = example.build(stem)
    frame = 560  # The existing Section 5.6 worked-example frame.
    before_floor_wrist = worked["w_lev"][frame]
    scene_wrist = before_floor_wrist + floor_shift
    wrist_h = transform_cs @ np.r_[scene_wrist, 1.]
    close("Chapter 5 homogeneous wrist equals recovery input", wrist_h[:3], inputs["w_hat_solver"]["right"][frame])
    close("Chapter 5 homogeneous wrist equals recovery conversion", wrist_h[:3],
          recovery_core._leveled_to_solver_space(before_floor_wrist, world)[0])
    close("Chapter 5 homogeneous coordinate remains one", wrist_h[3], 1.)
    close("Chapter 5 point round trip", transform_sc @ wrist_h, np.r_[scene_wrist, 1.])
    close("Chapter 5 printed inverse matrix", np.round(transform_cs, 2),
          [[1., -.04, .02, .05], [.04, 1., -.05, -.90], [-.02, .05, 1., .51], [0., 0., 0., 1.]])
    close("Chapter 5 printed wrist", np.round(wrist_h[:3], 2), [-.19, -.09, 1.04])

    documents = [args.docx.resolve()] if args.docx else [CONDENSED / name for name in
                 ("Chapter_5_Pose_Recovery.docx", "Chapter_6_System_Integration.docx", "Appendices.docx")]
    for document in documents:
        with ZipFile(source(document)) as archive:
            root = etree.fromstring(archive.read("word/document.xml"))
        # A summation may intentionally omit a limit when its matching Hide
        # property is true. That slot cannot render a visible placeholder.
        # Keep all ordinary and prescript slots subject to the regression check.
        empty = root.xpath(
            ".//m:sub[not(*) and not(parent::m:nary/m:naryPr/m:subHide"
            "[@m:val='1' or @m:val='true' or @m:val='on'])] | "
            ".//m:sup[not(*) and not(parent::m:nary/m:naryPr/m:supHide"
            "[@m:val='1' or @m:val='true' or @m:val='on'])]", namespaces=NS)
        check(document.name + ": no visible empty OMML script slots", not empty, count=len(empty))
        bad_pairs = []
        for prescript in root.xpath(".//m:sPre", namespaces=NS):
            base = "".join(prescript.xpath("./m:e//m:t/text()", namespaces=NS))
            if base in ("R", "T"):
                scripts = ["".join(prescript.xpath(f"./m:{tag}//m:t/text()", namespaces=NS)).strip()
                           for tag in ("sub", "sup")]
                if not all(scripts):
                    bad_pairs.append(base)
        check(document.name + ": framed R and T have both frames", not bad_pairs, count=len(bad_pairs))
        equation_count, bad_grids = 0, []
        for table in root.xpath(".//w:tbl", namespaces=NS):
            cells = table.xpath("./w:tr/w:tc", namespaces=NS)
            if len(cells) != 2 or not cells[0].xpath(".//m:oMath", namespaces=NS):
                continue
            number = "".join(cells[1].xpath(".//w:t/text()", namespaces=NS))
            if not re.fullmatch(r"\([A-Z0-9]+\.\d+\)", number):
                continue
            equation_count += 1
            grid = table.xpath("./w:tblGrid/w:gridCol/@w:w", namespaces=NS)
            widths = [cell.xpath("./w:tcPr/w:tcW/@w:w", namespaces=NS) for cell in cells]
            if len(grid) != 2 or any(width != [column] for width, column in zip(widths, grid)):
                bad_grids.append(number)
        check(document.name + ": equation grid matches cell widths", not bad_grids and equation_count > 0,
              equations=equation_count, mismatches=bad_grids)

    for relative in ("eval/offset/carry.py", "eval/failure/recovery_core.py", "eval/failure/grip_state.py",
                     "eval/offset/fit_offset.py", "eval/common/paths.py", "v1/kinematics/occlusion_ext.py",
                     "writing/v9/scripts/ch5_worked_example.py", "v1/aruco/frames.py",
                     f"v1/mediapipe/output/{stem}_landmarks_filtered.csv",
                     f"eval/reports/{stem}_offset_fit.json", f"eval/reports/{stem}_inspection.json",
                     "eval/output/recovery_r6b/failure_mask.csv", "Unity/Assets/Scripts/IntegratedSceneReceiver.cs"):
        source(REPO / relative)
    source(Path(__file__).resolve())
    failed = sum(item["status"] == "FAIL" for item in checks)
    print(json.dumps(dict(status="FAIL" if failed else "PASS", passed=len(checks) - failed,
                          failed=failed, checks=checks, source_sha256=sources,
                          limitations=["Does not verify Word rendering or the spawn-axis assumption.",
                                       "Representation tolerances are not experimental accuracy claims."]), indent=2))
    return bool(failed)


if __name__ == "__main__":
    sys.exit(main())

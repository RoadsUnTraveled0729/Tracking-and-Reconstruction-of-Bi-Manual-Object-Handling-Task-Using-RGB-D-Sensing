#!/usr/bin/env python3
"""Reproduce D-082's Chapter 5 Scene refactor without changing source data.

The frozen analysis API is imported read-only. Historical API identifiers
remain at that boundary; every new coordinate is explicitly Scene or Camera'.
The baseline DOCX is read from e69dfa6. Arithmetic/storage tolerances inherit
D-072 (1e-9 / 2e-6) and are not experimental accuracy bounds. Frame 560 is
the existing worked-example frame. The .03 and .69 m drawing constants are
parsed from ArucoSceneReceiver.cs instead of introduced as new parameters.

Run with /home/luo/anaconda3/bin/python. Writes only ch5_invariance.json and
ch5_document_changes.json beside this script, after Chapter 5 is rebuilt.
"""

import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd
from lxml import etree

REPO = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
CONDENSED = REPO / "writing/v9"
BASELINE = "e69dfa62eda80bc0ba5d0c4607a3a183a69f71fb"
ARITHMETIC_TOL = 1e-9
STORED_POSE_TOL = 2e-6
FRAME = 560
NS = {"m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
      "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

for folder in ("eval/offset", "eval/common", "eval/failure",
               "v1/kinematics", "writing/v9/scripts"):
    sys.path.insert(0, str(REPO / folder))

import carry
import ch5_worked_example as example
import grip_state
import paths
import recovery_core
from fit_offset import load_tracks


def main():
    checks, hashes, recordings = [], {}, {}

    def source(path):
        path = Path(path).resolve()
        hashes[str(path.relative_to(REPO))] = hashlib.sha256(path.read_bytes()).hexdigest()
        return path

    def check(label, condition, **evidence):
        checks.append(dict(label=label, status="PASS" if condition else "FAIL", **evidence))

    def close(label, actual, expected, tolerance=ARITHMETIC_TOL):
        error = float(np.max(np.abs(np.asarray(actual) - np.asarray(expected))))
        check(label, np.isfinite(error) and error <= tolerance,
              max_absolute_difference=error, tolerance=tolerance)

    receiver = source(REPO / "Unity/Assets/Scripts/ArucoSceneReceiver.cs").read_text()
    desk_thickness = float(re.search(r"DeskThick = ([0-9.]+)f", receiver)[1])
    leg_height = float(re.search(r"LegH = ([0-9.]+)f", receiver)[1])
    swap = np.array([[1., 0., 0.], [0., 0., 1.], [0., 1., 0.]])
    flip = np.diag([1., -1., 1.])
    close("S changes handedness", np.linalg.det(swap), -1.)
    close("F changes handedness", np.linalg.det(flip), -1.)

    # The rail supplies the worked example and the loop supplies the cited
    # offset-scatter result. Use every finite stored pose, without selecting
    # a new experimental sample or changing an existing eligibility mask.
    for stem in (paths.R6B_STEM, paths.R5_STEM):
        alias = paths.ALIAS[stem]
        calibration_path = source(paths.calib_for(stem))
        track = pd.read_csv(source(paths.object_world_filtered(stem)))
        source(paths.lm_filtered(stem))
        calibration, mapping, landmarks, old_object, rotations, _, old_wrists, _, _ = \
            load_tracks(stem, str(calibration_path))
        n = len(old_object)
        track = track.iloc[:n]
        check(alias + ": object and landmark frame identifiers agree",
              np.array_equal(track["frame"], landmarks["frame"]), frames=n)
        distance = (calibration["scene_geometry"]["origin_above_tabletop_m"]
                    + desk_thickness + leg_height)
        floor = np.array([0., distance, 0.])
        camera_world = np.linalg.inv(np.array(calibration["T_cam_desk"]))
        scene_camera = np.eye(4)
        scene_camera[:3, :3] = mapping.G @ swap @ camera_world[:3, :3] @ np.linalg.inv(flip)
        scene_camera[:3, 3] = mapping.G @ swap @ camera_world[:3, 3] + floor
        camera_scene = np.linalg.inv(scene_camera)
        close(alias + ": G is proper", np.linalg.det(mapping.G), 1.)
        close(alias + ": G is orthogonal", mapping.G.T @ mapping.G, np.eye(3))
        close(alias + ": Camera' to Scene rotation is proper",
              np.linalg.det(scene_camera[:3, :3]), 1.)
        close(alias + ": full transforms are inverses", camera_scene @ scene_camera, np.eye(4))

        world_positions = track[["tx", "ty", "tz"]].to_numpy()
        world_rotations = track[[f"r{i}{j}" for i in range(1, 4)
                                 for j in range(1, 4)]].to_numpy().reshape(-1, 3, 3)
        finite = (np.isfinite(world_positions).all(axis=1)
                  & np.isfinite(world_rotations).all(axis=(1, 2))
                  & np.isfinite(old_object).all(axis=1)
                  & np.isfinite(rotations).all(axis=(1, 2)))
        check(alias + ": finite object poses available", bool(finite.any()), count=int(finite.sum()))
        scene_object = old_object + floor
        direct_scene = world_positions[finite] @ swap.T @ mapping.G.T + floor
        close(alias + ": direct World-to-Scene origins match stored display chain",
              direct_scene, scene_object[finite], STORED_POSE_TOL)
        close(alias + ": Scene/MappedMarker orientation matches conjugation chain",
              mapping.G @ swap @ world_rotations[finite] @ swap,
              rotations[finite], STORED_POSE_TOL)
        close(alias + ": every finite object y changes by d",
              scene_object[finite, 1] - old_object[finite, 1], distance)
        close(alias + ": every finite object x/z is unchanged",
              scene_object[finite][:, [0, 2]], old_object[finite][:, [0, 2]])
        close(alias + ": object path step distances survive gravity alignment and floor placement",
              np.linalg.norm(np.diff(direct_scene, axis=0), axis=1),
              np.linalg.norm(np.diff(world_positions[finite], axis=0), axis=1))
        scene_as_camera = (scene_object[finite] @ camera_scene[:3, :3].T
                           + camera_scene[:3, 3])
        close(alias + ": inverse Scene mapping preserves all finite object Camera' points",
              scene_as_camera,
              recovery_core._leveled_to_solver_space(old_object[finite], mapping))

        per_hand = {}
        for side in ("left", "right"):
            scene_wrist = old_wrists[side] + floor
            valid = finite & np.isfinite(old_wrists[side]).all(axis=1)
            old_displacement = old_wrists[side][valid] - old_object[valid]
            scene_displacement = scene_wrist[valid] - scene_object[valid]
            old_offset = np.einsum("nij,ni->nj", rotations[valid], old_displacement)
            scene_offset = np.einsum("nij,ni->nj", rotations[valid], scene_displacement)
            close(alias + ": " + side + " wrist-minus-marker displacement is unchanged",
                  scene_displacement, old_displacement)
            close(alias + ": " + side + " offset observations are unchanged (5.2)",
                  scene_offset, old_offset)
            close(alias + ": " + side + " wrist-marker distances are unchanged",
                  np.linalg.norm(scene_displacement, axis=1),
                  np.linalg.norm(old_displacement, axis=1))
            close(alias + ": " + side + " offset mean is unchanged (5.3)",
                  scene_offset.mean(axis=0), old_offset.mean(axis=0))
            close(alias + ": " + side + " offset component scatter is unchanged",
                  scene_offset.std(axis=0), old_offset.std(axis=0))
            raw_camera = landmarks.loc[valid, [f"{side}_wrist_{axis}" for axis in "xyz"]].to_numpy()
            close(alias + ": " + side + " inverse Scene mapping returns Camera' measurements",
                  scene_wrist[valid] @ camera_scene[:3, :3].T + camera_scene[:3, 3],
                  raw_camera @ flip.T)
            per_hand[side] = dict(finite_wrist_object_samples=int(valid.sum()))
        recordings[alias] = dict(stem=stem, frames=n, finite_object_poses=int(finite.sum()),
                                 floor_translation_m=floor.tolist(), per_hand=per_hand,
                                 T_Scene_CameraPrime=scene_camera.tolist(),
                                 T_CameraPrime_Scene=camera_scene.tolist())

    # Re-run the published worked-example pipeline and its estimator with
    # Scene observations. Retain every original episode, mask and fallback.
    inputs, worked = example.build(paths.R6B_STEM)
    floor = np.array(recordings["r6b"]["floor_translation_m"])
    camera_scene = np.array(recordings["r6b"]["T_CameraPrime_Scene"])
    scene_object = worked["obj"] + floor
    scene_measured = worked["wr_lev"] + floor  # Frozen historical API field.
    scene_observations = np.einsum("nij,ni->nj", worked["R"], scene_measured - scene_object)
    fitted = grip_state.time_local_mu(scene_observations, worked["hold_clean"],
                                      inputs["episodes"][example.SIDE])
    fallback = grip_state.per_frame_mu(inputs["n"], inputs["episode_fits"][example.SIDE])
    fitted[~np.isfinite(fitted).all(axis=1)] = fallback[~np.isfinite(fitted).all(axis=1)]
    finite_offsets = np.isfinite(worked["mu"]).all(axis=1)
    check("rail: estimator finite mask is unchanged (5.4)",
          np.array_equal(np.isfinite(fitted).all(axis=1), finite_offsets),
          finite_estimates=int(finite_offsets.sum()))
    close("rail: all recursive/fallback offsets are unchanged (5.4)",
          fitted[finite_offsets], worked["mu"][finite_offsets])
    predicted = scene_object + np.einsum("nij,nj->ni", worked["R"], fitted)
    finite_predictions = np.isfinite(predicted).all(axis=1)
    camera_wrist = predicted @ camera_scene[:3, :3].T + camera_scene[:3, 3]
    close("rail: every finite reconstructed Camera' wrist is unchanged (5.7)",
          camera_wrist[finite_predictions], worked["w_sol"][finite_predictions])
    accepted = np.isfinite(inputs["w_hat_solver"][example.SIDE]).all(axis=1)
    close("rail: every accepted solver wrist matches the frozen pipeline",
          camera_wrist[accepted], inputs["w_hat_solver"][example.SIDE][accepted])
    close("rail: worked wrist homogeneous inverse matches the solver input",
          camera_scene @ np.r_[predicted[FRAME], 1.],
          np.r_[inputs["w_hat_solver"][example.SIDE][FRAME], 1.])
    close("rail: printed Scene object from full precision",
          np.round(scene_object[FRAME], 2), [-.22, .79, .45])
    close("rail: printed Scene wrist from full precision",
          np.round(predicted[FRAME], 2), [-.21, .85, .48])
    close("rail: printed inverse last column from full precision",
          np.round(camera_scene[:3, 3], 2), [.05, -.90, .51])
    close("rail: printed Camera' wrist stays unchanged",
          np.round(camera_wrist[FRAME], 2), [-.19, -.09, 1.04])
    worked_values = dict(frame=FRAME, time_s=float(worked["t"][FRAME]),
                         object_before_floor_m=worked["obj"][FRAME].tolist(),
                         object_Scene_m=scene_object[FRAME].tolist(),
                         wrist_before_floor_m=worked["w_lev"][FRAME].tolist(),
                         wrist_Scene_m=predicted[FRAME].tolist(),
                         wrist_CameraPrime_m=camera_wrist[FRAME].tolist(),
                         offset_MappedMarker_m=worked["mu"][FRAME].tolist(),
                         offset_Scene_m=(worked["R"][FRAME] @ worked["mu"][FRAME]).tolist(),
                         R_Scene_MappedMarker=worked["R"][FRAME].tolist(),
                         finite_predictions=int(finite_predictions.sum()),
                         accepted_predictions=int(accepted.sum()))

    current_path = source(CONDENSED / "Chapter_5_Pose_Recovery.docx")
    baseline_bytes = subprocess.check_output([
        "git", "show", BASELINE + ":writing/v9/Chapter_5_Pose_Recovery.docx"], cwd=REPO)

    def document(data):
        with ZipFile(io.BytesIO(data)) as archive:
            root = etree.fromstring(archive.read("word/document.xml"))
            media = {name: hashlib.sha256(archive.read(name)).hexdigest()
                     for name in archive.namelist() if name.startswith("word/media/")}
        return root, media

    before, _ = document(baseline_bytes)
    after, embedded = document(current_path.read_bytes())

    def text_of(node):
        return "".join(node.xpath(".//w:t/text() | .//m:t/text()", namespaces=NS)).replace("\u200b", "")

    def equations(root):
        result = {}
        for table in root.xpath(".//w:body/w:tbl", namespaces=NS):
            cells = table.xpath("./w:tr/w:tc", namespaces=NS)
            if len(cells) == 2 and re.fullmatch(r"\(5\.\d+\)", text_of(cells[1])):
                math = cells[0].xpath(".//m:oMath", namespaces=NS)[0]
                result[text_of(cells[1])] = math
        return result

    old_eq, new_eq = equations(before), equations(after)
    check("Chapter 5 numbered equation identifiers are unchanged", old_eq.keys() == new_eq.keys())
    dispositions = []
    for number, math in old_eq.items():
        changed = etree.tostring(math) != etree.tostring(new_eq[number])
        expected_change = number in ("(5.1)", "(5.2)", "(5.7)")
        check(number + ": change stays within D-082 scope", changed == expected_change,
              changed=changed, expected_change=expected_change)
        dispositions.append(dict(number=number, changed=changed,
                                 before=text_of(math), after=text_of(new_eq[number])))
    old_displays = before.xpath(".//w:body/w:p[m:oMath and not(w:r/w:t)]/m:oMath", namespaces=NS)
    new_displays = after.xpath(".//w:body/w:p[m:oMath and not(w:r/w:t)]/m:oMath", namespaces=NS)
    check("Chapter 5 unnumbered display count is unchanged", len(old_displays) == len(new_displays),
          before=len(old_displays), after=len(new_displays))
    changed_displays = [dict(display_index_1based=i, before=text_of(old), after=text_of(new))
                        for i, (old, new) in enumerate(zip(old_displays, new_displays), 1)
                        if etree.tostring(old) != etree.tostring(new)]
    check("Chapter 5 printed prose and OMML omit the removed frame",
          re.search(r"levelled|leveled", text_of(after), flags=re.I) is None)
    for relative in ("scripts/build_ch5.py", "scripts/make_ch5_flow_final_fig.py",
                     "scripts/make_ch5_offset_final_fig.py"):
        script = source(CONDENSED / relative).read_text()
        active = script.split("from pathlib import Path", 1)[1]
        check(relative + ": active source omits the removed frame",
              re.search(r"levelled|leveled|\bR_LM\b|\bT_LP\b|\bT_PL\b|\binL\b", active, re.I) is None)
    for asset in ("ch5_fig_flow.png", "ch5_fig_offset.png"):
        path = source(CONDENSED / "figures" / asset)
        check(asset + ": DOCX embeds the regenerated asset",
              hashlib.sha256(path.read_bytes()).hexdigest() in embedded.values())
    document_changes = dict(baseline_commit=BASELINE,
                            baseline_chapter_sha256=hashlib.sha256(baseline_bytes).hexdigest(),
                            current_chapter_sha256=hashlib.sha256(current_path.read_bytes()).hexdigest(),
                            numbered_equations=dispositions,
                            unnumbered_display_changes=changed_displays)
    (OUT / "ch5_document_changes.json").write_text(json.dumps(document_changes, indent=2) + "\n")

    for relative in ("eval/offset/carry.py", "eval/offset/fit_offset.py", "eval/common/paths.py",
                     "eval/failure/recovery_core.py", "eval/failure/grip_state.py",
                     "v1/aruco/frames.py", "v1/kinematics/occlusion_ext.py",
                     "writing/v9/scripts/ch5_worked_example.py",
                     "eval/unity_check/check_unity_log.py", "eval/output/recovery_r6b/failure_mask.csv",
                     "eval/reports/recording_20260831_065553_offset_fit.json",
                     "eval/reports/recording_20260831_065553_inspection.json",
                     "eval/reports/recording_20260825_222315_offset_fit.json"):
        source(REPO / relative)
    source(Path(__file__))
    failed = sum(item["status"] == "FAIL" for item in checks)
    result = dict(status="FAIL" if failed else "PASS", passed=len(checks) - failed, failed=failed,
                  baseline_commit=BASELINE, recordings=recordings, worked_example=worked_values,
                  checks=checks, source_sha256=hashes,
                  limitations=["Arithmetic and representation invariance, not physical accuracy.",
                               "No experimental files, masks, or source implementations are changed.",
                               "Word/PDF layout is an integration check outside this diagnostic.",
                               "Deferred correctness-audit findings remain outside D-082."])
    (OUT / "ch5_invariance.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(dict(status=result["status"], passed=result["passed"], failed=failed,
                          finite_objects={k: v["finite_object_poses"] for k, v in recordings.items()},
                          changed_unnumbered_displays=len(changed_displays),
                          output=str(OUT / "ch5_invariance.json")), indent=2))
    return bool(failed)


if __name__ == "__main__":
    sys.exit(main())

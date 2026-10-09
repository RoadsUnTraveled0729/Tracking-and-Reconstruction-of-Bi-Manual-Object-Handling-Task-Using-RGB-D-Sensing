#!/usr/bin/env python3
"""Pin the Section 7.3.3 wrist to marker check as coordinate pairs.

Decision D-038 keeps four reconstructed wrist to marker medians in Chapter 7:
the right hand alone and the left hand alone, which are compared with the
author's approximate 16 cm physical reference (REVISION_2026-09-11_BRIEF.md
fact 4), and the two transfer values, which are reported as descriptive
reconstructed geometry and are not graded against that reference because the
grip geometry changes while both hands are on the cube. Until now those four
medians existed only inside eval/reports/r7_handover.json, so Section 7.3.3
was the one part of Chapter 7 that the standalone verifier could compare
against a pinned report but could not rebuild.

This script emits the missing coordinate pairs. It reproduces the definitions
of eval/failure/handover_analysis.py exactly, without importing that module's
report writer, and writes one row per evaluated frame per hand over the whole
rail span: the reconstructed model wrist, the object marker position, the
measured wrist and the cube centre that the inclusion test uses, the per-frame
carried and detected states, the hold distance, the inclusion status and its
reason, and the wrist to marker distance in centimetres. Nothing is excluded
on the size of a distance.

Conventions follow scripts/evaluate_ch7_restructured.py and
scripts/evaluate_ch7_object.py: the emitted coordinate pairs are the
reproducible numerical record, every input is hashed, no exclusion rule
depends on the size of any resulting distance, and no definition was adjusted
to reproduce a published number. The script asserts that its own medians round
to the four values the pinned report carries and fails loudly if they do not.

Run from the repository root:
    /home/luo/anaconda3/bin/python \
    writing/v9/scripts/evaluate_ch7_spatial_check.py
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / 'writing/v9/audit_evidence/ch7_restructured'
for folder in ('eval/common', 'eval/offset', 'eval/gt', 'eval/failure',
               'eval/inspect', 'v1/kinematics'):
    sys.path.insert(0, str(REPO / folder))

import paths
import carry
import eval_rail_scenario as ers
import recovery_core as rc
from moving_window_check import fk_wrist
from root_frame import unity_from_sensor

# Solved joint-angle columns of angles_recovery.csv and the solver-space to
# camera-frame flip, both exactly as eval/failure/handover_analysis.py reads
# them (lines 55 to 57 of that file).
ANGLE_COLS = ['root_ex', 'root_ey', 'root_ez', 'Rsh_y', 'Rsh_z', 'Rsh_tau',
              'Rel_y', 'Rel_z', 'Lsh_y', 'Lsh_z', 'Lsh_tau', 'Lel_y', 'Lel_z']
FLIP = np.array([1.0, -1.0, 1.0])

# The author's physical reference (brief fact 4). An approximate scalar tape
# measurement for a normal single-hand grip, never a per-frame constraint and
# never called ground truth. D-038 applies it to the hand-alone medians only.
PHYSICAL_REFERENCE_CM = 16.0

# The four published medians, as the author gave them (brief fact 5) and as
# build_ch7.py prints them in Section 7.3.3. Targets for the reproduction
# assertion below, never inputs to any calculation.
PUBLISHED_CM = {('right', 'right'): 15.77, ('handover', 'right'): 17.91,
                ('handover', 'left'): 15.85, ('left', 'left'): 14.08}

PARTS = ('right', 'handover', 'left')
PHASE = {'right': 'hand_alone', 'handover': 'transfer', 'left': 'hand_alone'}

SOURCES = set()


def source(path):
    path = Path(path)
    SOURCES.add(path.resolve())
    return path


def read_json(path):
    return json.loads(source(path).read_text())


def save_json(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def stats_cm(values):
    """Statistics on finite distances only, in centimetres.

    handover_analysis.stats_cm drops non-finite values before summarizing and
    keeps everything else; the same rule applies here so the two agree. No
    value is dropped for being large.
    """
    values = np.asarray(values, float)
    values = values[np.isfinite(values)]
    assert values.size
    return dict(n=int(values.size), median=float(np.median(values)),
                p95=float(np.percentile(values, 95, method='linear')),
                maximum=float(values.max()))


def model_wrists(lm, angles, seg_len, world, n):
    """Forward-kinematics wrist of the recovery solve, in the levelled world.

    Root rotation from the solved Euler angles, arm directions from
    check_v1_overlay.fk_arm_dirs, elbow at the same-frame measured shoulder
    plus the calibrated upper-arm length, wrist one calibrated forearm
    further: the bare kinematic-model wrist of D-039, expressed in the
    gravity-levelled desk world rather than in solver space. The shoulder
    anchor is the filtered landmark, which is what the solve itself used.
    """
    out = {}
    for side in rc.SIDES:
        key = 'R' if side == 'right' else 'L'
        upper, fore = seg_len['upper_arm_' + key], seg_len['forearm_' + key]
        sh_cam = lm[[f'{side}_shoulder_{a}' for a in 'xyz']].to_numpy(float)[:n]
        shoulder = np.array([unity_from_sensor(v) for v in sh_cam])
        points = np.full((n, 3), np.nan)
        for i in range(n):
            if np.isfinite(shoulder[i]).all() and np.isfinite(angles[i]).all():
                solved = fk_wrist(angles, i, shoulder, upper, fore, side)
                points[i] = world.wrist_world((solved * FLIP)[None, :])[0]
        out[side] = points
    return out


def evaluate():
    stem = paths.R7_STEM
    alias = paths.ALIAS[stem]
    inp = rc.build_inputs(stem)
    n, t, lm, world, seg_len = (inp['n'], inp['t'], inp['lm_df'], inp['world'],
                                inp['seg_len'])
    center, carried, det = inp['center'], inp['carried'], inp['det']

    track = ers.load_track(stem)
    marker = track['xyz']
    assert np.array_equal(track['frame'], np.arange(len(marker)))
    rail = np.asarray(ers.segment(track)['rail'], int)

    # Levelled marker rotation, read exactly as eval/offset/fit_offset.py
    # reads it. Used only by the inclusion-gate diagnostic below.
    obj_df = pd.read_csv(source(paths.object_world_filtered(stem)))
    _, rotation = world.object_world(
        obj_df[['unity_px', 'unity_py', 'unity_pz']].to_numpy(),
        obj_df[['unity_ex', 'unity_ey', 'unity_ez']].to_numpy())

    ang_df = pd.read_csv(source(paths.EVAL_OUT / f'recovery_{alias}'
                                / 'angles_recovery.csv'))
    assert len(ang_df) >= n and np.array_equal(
        ang_df['frame'].to_numpy()[:n], np.arange(n))
    angles = ang_df[ANGLE_COLS].to_numpy(float)[:n]

    fk = model_wrists(lm, angles, seg_len, world, n)
    measured, wrist_src, substituted, hold, near = {}, {}, {}, {}, {}
    for side in rc.SIDES:
        cam = lm[[f'{side}_wrist_{a}' for a in 'xyz']].to_numpy(float)[:n]
        measured[side] = world.wrist_world(cam)
        wrist_src[side] = lm[f'{side}_wrist_src'].to_numpy(int)[:n]
        # Hold test point: the measured wrist where the extractor reported one,
        # the model wrist where it did not. handover_analysis substitutes on
        # the extractor source code, not on the filter flag.
        point = measured[side].copy()
        miss = ~np.isfinite(point).all(axis=1) | (wrist_src[side] != 0)
        point[miss] = fk[side][miss]
        substituted[side] = miss
        hold[side] = np.linalg.norm(point - center, axis=1)
        with np.errstate(invalid='ignore'):
            near[side] = carried & det & (hold[side] < carry.HOLD_RADIUS)

    # Parts of the slide. The rail span is the contiguous frame range of the
    # detected slide; inside it the transfer runs from the first frame on which
    # the left hand is at the cube to the last on which the right hand is.
    on_rail = np.zeros(n, bool)
    on_rail[rail[0]:rail[-1] + 1] = True
    left_in = int(np.flatnonzero(on_rail & near['left'])[0])
    right_out = int(np.flatnonzero(on_rail & near['right'])[-1])
    assert left_in < right_out
    frames = np.arange(n)
    part = np.full(n, '', dtype=object)
    part[on_rail & (frames < left_in)] = 'right'
    part[on_rail & (frames >= left_in) & (frames <= right_out)] = 'handover'
    part[on_rail & (frames > right_out)] = 'left'

    rows, groups = [], []
    for name in PARTS:
        idx = np.flatnonzero(part == name)
        for side in rc.SIDES:
            distance = np.linalg.norm(fk[side][idx] - marker[idx], axis=1) * 100
            included = near[side][idx] & np.isfinite(distance)
            for k, frame in enumerate(idx):
                reasons = []
                if not near[side][frame]:
                    if not carried[frame]:
                        reasons.append('not carried')
                    if not det[frame]:
                        reasons.append('marker not detected')
                    if not np.isfinite(hold[side][frame]):
                        reasons.append('hold distance not finite')
                    elif not hold[side][frame] < carry.HOLD_RADIUS:
                        reasons.append('wrist beyond hold radius')
                elif not np.isfinite(distance[k]):
                    reasons.append('model wrist or marker position not finite')
                row = dict(recording=alias, side=side, part=name,
                           phase=PHASE[name], frame=int(frame),
                           time_s=float(t[frame]),
                           carried=int(bool(carried[frame])),
                           detected=int(bool(det[frame])),
                           wrist_src=int(wrist_src[side][frame]),
                           substituted=int(bool(substituted[side][frame])),
                           hold_distance_cm=float(hold[side][frame] * 100),
                           included=int(bool(included[k])),
                           exclusion_reason='; '.join(reasons),
                           distance_cm=float(distance[k]))
                for label, point in (('model_wrist', fk[side][frame]),
                                     ('marker', marker[frame]),
                                     ('measured_wrist', measured[side][frame]),
                                     ('cube_centre', center[frame])):
                    row.update({f'{label}_{a}': float(point[j])
                                for j, a in enumerate('xyz')})
                rows.append(row)
            # D-038 grades the two hand-alone medians against the approximate
            # 16 cm physical reference and nothing else. A group with no frame
            # at the cube carries no median and so grades nothing.
            block = dict(part=name, side=side, phase=PHASE[name],
                         graded_against_physical_reference=bool(
                             PHASE[name] == 'hand_alone'
                             and (name, side) in PUBLISHED_CM),
                         first_frame=int(idx[0]), last_frame=int(idx[-1]),
                         rows=int(len(idx)), n_included=int(included.sum()))
            if included.any():
                block.update(stats_cm(distance[included]))
                block['published_cm'] = PUBLISHED_CM.get((name, side))
            else:
                block['n'] = 0
            groups.append(block)

    reproduced = True
    for block in groups:
        target = PUBLISHED_CM.get((block['part'], block['side']))
        if target is None:
            assert block['n'] == 0, (block['part'], block['side'], block['n'])
            continue
        reproduced &= round(block['median'], 2) == target
    intervals = {
        'rail_span': [int(rail[0]), int(rail[-1])],
        'rail_span_rule': 'the contiguous frame range from the first to the '
                          'last sample of the detected rail slide, '
                          'eval/gt/eval_rail_scenario.segment',
        'left_hand_arrives_frame': left_in,
        'right_hand_leaves_frame': right_out,
    }
    intervals['right'] = dict(
        frames=[int(rail[0]), left_in - 1],
        description='right hand alone: the rail span before the left hand '
                    'first reaches the cube')
    intervals['handover'] = dict(
        frames=[left_in, right_out],
        description='transfer: from the first frame on which the left hand is '
                    'at the cube to the last frame on which the right hand is')
    intervals['left'] = dict(
        frames=[right_out + 1, int(rail[-1])],
        description='left hand alone: the rail span after the right hand last '
                    'leaves the cube')

    # Diagnostic, changes nothing above. The hold test is centred on
    # carry.LeveledWorld.box_center, the marker position displaced half a cube
    # along the marker frame negative y axis. On this recording the marker
    # plane faces up, so the outward face normal is the marker frame z axis and
    # a cube centre half a cube along negative z would sit below the marker
    # instead. The two candidate centres are about one cube half-diagonal
    # apart, so the gate could in principle change which frames are at the
    # cube. Rerunning the membership test with the alternative centre, holding
    # the part boundaries at their pinned values, measures whether it does.
    alternative = np.array([marker[i] + rotation[i] @ np.array(
        [0.0, 0.0, -world.cube / 2.0]) for i in range(n)])
    sensitivity = dict(
        centre='marker position displaced half a cube along the marker frame '
               'negative z axis, the outward normal of the upward facing '
               'marker plane, instead of the negative y axis of '
               'carry.LeveledWorld.box_center',
        note='diagnostic only; every reported number above uses the pinned '
             'box_center definition, and the part boundaries are held at the '
             'pinned values so only the at-the-cube membership varies',
        groups=[])
    for name in PARTS:
        idx = np.flatnonzero(part == name)
        for side in rc.SIDES:
            point = measured[side].copy()
            point[substituted[side]] = fk[side][substituted[side]]
            with np.errstate(invalid='ignore'):
                other = (carried & det
                         & (np.linalg.norm(point - alternative, axis=1)
                            < carry.HOLD_RADIUS))
            distance = np.linalg.norm(fk[side][idx] - marker[idx], axis=1) * 100
            keep = other[idx] & np.isfinite(distance)
            block = dict(part=name, side=side, n=int(keep.sum()))
            if keep.any():
                block['median'] = float(np.median(distance[keep]))
            sensitivity['groups'].append(block)
    return rows, groups, intervals, sensitivity, reproduced, stem, alias


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows, groups, intervals, sensitivity, reproduced, stem, alias = evaluate()

    pinned_path = paths.EVAL_REPORTS / f'{alias}_handover.json'
    pinned = read_json(pinned_path)
    pinned_block = {f'{part}/{side}': pinned['parts'][part]
                    [f'{side}_fk_wrist_to_marker_at_cube_cm']
                    for part, side in PUBLISHED_CM}
    for block in groups:
        key = f"{block['part']}/{block['side']}"
        if key not in pinned_block:
            continue
        stated = pinned_block[key]
        assert block['n'] == stated['n'], (key, block['n'], stated['n'])
        for name, other in (('median', 'median'), ('p95', 'p95'),
                            ('maximum', 'max')):
            assert round(block[name], 2) == stated[other], (key, name)
    assert reproduced, 'the four published medians did not reproduce'

    payload = dict(
        purpose='Section 7.3.3 human-object spatial check: the reconstructed '
                'wrist to object-marker distance while one hand and then both '
                'hands are on the cube, rebuilt from coordinate pairs so the '
                'subsection sits inside the reproducibility package rather '
                'than resting on a pinned report.',
        decision='D-038',
        stem=stem, alias=alias,
        recording='the handover recording',
        frame_convention='Gravity-levelled desk world: x along the rail, y up, '
                         'z away from the camera, metres in the coordinate '
                         'columns and centimetres in the distances. The '
                         'levelling rotation is a rigid motion, so every '
                         'distance below is invariant to it.',
        definitions=dict(
            model_wrist='The wrist placed by the kinematic model: the root '
                        'rotation and arm directions of the solved joint '
                        'angles in eval/output/recovery_r7/angles_recovery.csv '
                        '(the causal recovery solve of the pinned chain), '
                        'anchored at the same-frame filtered measured shoulder '
                        'landmark and extended by the recording calibrated '
                        'upper-arm and forearm lengths. This is the bare '
                        'kinematic-model wrist of D-039, not the rendered '
                        'Unity rig wrist of Table 7.4 and not a measured '
                        'wrist. Source eval/failure/handover_analysis.py lines '
                        '122 to 130, forward kinematics '
                        'eval/failure/moving_window_check.fk_wrist.',
            object_point='The ArUco marker centre: the object marker pose '
                         'translation of the cleaned object track, levelled. '
                         'The pose solve lays its four object points out '
                         'symmetrically about the origin at plus and minus '
                         'half the marker side, so the translation origin is '
                         'the geometric centre of the printed black square. '
                         'The point Section 7.3.3 calls the marker origin and '
                         'the point Section 7.2 and D-036 call the marker '
                         'centre are therefore the same physical point, and '
                         'marker centre is the name used here.',
            object_point_chain=[
                'v1/aruco/extract_aruco_poses.py square_object_points, the '
                'four corners at plus and minus half the side about the '
                'origin, so the origin is the centre of the square',
                'v1/aruco/extract_aruco_poses.py solve_marker_pose, '
                'cv2.solvePnPGeneric with SOLVEPNP_IPPE_SQUARE on those '
                'points, giving the camera-frame translation of that centre',
                'eval/gt/scale_correction.py, each translation multiplied by '
                'the assumed over declared side ratio of '
                'eval/common/marker_size.py, 45 over 50 for the object '
                'marker. The object points stay symmetric at any declared '
                'side, so this rescales the distance to the centre and does '
                'not move the reference to another point on the marker',
                'v1/aruco/calibrate_scene.py, the translation carried into '
                'the desk-marker world by the calibrated desk pose and '
                'permuted into the unity_p* columns by '
                'v1/aruco/frames.unity_from_world',
                'v1/aruco/filter_object_track.py, temporal smoothing of the '
                'translation and re-derivation of unity_p*; a smoother moves '
                'the estimate, not the point it estimates',
                'eval/common/clean_object_track.py, implausible samples '
                'blanked, no coordinate changed',
                'eval/gt/eval_rail_scenario.load_track, levelled by the '
                'calibrated gravity rotation of eval/offset/carry.LeveledWorld',
                'eval/failure/handover_analysis.py, the reported distance '
                'from the model wrist to that levelled marker centre'],
            object_point_not_the_cube_centre='The cube centre of '
                'carry.LeveledWorld.box_center is a different point, half a '
                'cube from the marker. It appears in the inclusion test only '
                'and never in a reported distance.',
            measured_wrist='The filtered MediaPipe landmark with aligned '
                           'depth, levelled. It appears here only in the '
                           'inclusion test, never in a reported distance, so '
                           'the evaluation reference convention of D-040 is '
                           'not engaged by it.',
            cube_centre='The marker position displaced half a cube along the '
                        'marker frame negative y axis, '
                        'eval/offset/carry.LeveledWorld.box_center. It is the '
                        'reference point of the hold test only.',
            physical_reference_cm=PHYSICAL_REFERENCE_CM,
            physical_reference_note='Approximately 16 cm, the author tape '
                                    'measurement of brief fact 4 between the '
                                    'physical location corresponding to the '
                                    'MediaPipe wrist landmark and the object '
                                    'ArUco marker origin for a normal '
                                    'single-hand grip. An approximate scalar '
                                    'physical reference, not a per-frame '
                                    'constraint and not a computed quantity.',
            physical_reference_endpoint='The author named the marker origin. '
                                        'The marker origin is the centre of '
                                        'the printed black square, as the '
                                        'chain above establishes, so the tape '
                                        'measurement and the reconstructed '
                                        'distance share one object endpoint '
                                        'as far as the record states it. The '
                                        'record does not fix the wrist '
                                        'endpoint more closely than the '
                                        'physical location corresponding to '
                                        'the detector landmark.'),
        inclusion_rule=dict(
            statement='A frame enters a median when the object marker is '
                      'detected, the cube is carried, and that hand is at the '
                      'cube: the hold point lies closer than the hold radius '
                      'to the cube centre. The hold point is the measured '
                      'wrist where the extractor returned one and the model '
                      'wrist where it did not. A frame whose wrist to marker '
                      'distance is not finite is dropped by the statistic. No '
                      'frame is excluded on the size of a distance.',
            hold_radius_cm=carry.HOLD_RADIUS * 100,
            hold_radius_source='eval/offset/carry.HOLD_RADIUS',
            substitution='eval/failure/handover_analysis.py lines 132 to 140: '
                         'the substitution is decided on the extractor source '
                         'code {side}_wrist_src, not on the filter flag, so a '
                         'frame whose filtered coordinate was interpolated is '
                         'still substituted.',
            carried='eval/offset/carry.rest_referenced_carried over the '
                    'manipulation phase of the recording inspection report: '
                    'inside the motion envelope and away from both rest '
                    'positions, or moving, or clearly lifted.',
            detected='the cleaned object track reports detected equal to 1 on '
                     'that frame'),
        intervals=intervals,
        groups=groups,
        inclusion_sensitivity=sensitivity,
        published_medians_cm={f'{part}/{side}': value
                              for (part, side), value in PUBLISHED_CM.items()},
        grading=dict(
            graded='the two hand-alone medians, which D-038 compares with the '
                   'approximate 16 cm physical reference',
            not_graded='the two transfer medians, which D-038 reports as '
                       'descriptive reconstructed geometry because the grip '
                       'geometry changes while both hands are on the cube'),
        pairs_file=dict(
            name='spatial_check_pairs.csv',
            scope='one row per frame of the rail span for each hand, '
                  'included and excluded alike, so the inclusion rule is '
                  'rebuildable rather than asserted',
            note='the distance column is filled wherever both coordinates are '
                 'finite, including on excluded rows; only rows with included '
                 'equal to 1 enter a median'),
        pinned_report=dict(
            path=str(pinned_path.relative_to(REPO)),
            blocks=pinned_block,
            statistic='*_fk_wrist_to_marker_at_cube_cm, rounded to two '
                      'decimals in that report'),
        reproduces_pinned_report=bool(reproduced),
        provenance=dict(
            numpy=np.__version__, pandas=pd.__version__,
            percentile='numpy.percentile, linear interpolation',
            sources=[]))

    # Inputs read indirectly by recovery_core.build_inputs and
    # eval_rail_scenario.load_track, plus the modules that define the geometry.
    for path in (paths.lm_filtered(stem), paths.calib_for(stem),
                 paths.object_world_filtered(stem),
                 paths.EVAL_REPORTS / f'{stem}_offset_fit.json',
                 paths.EVAL_REPORTS / f'{stem}_inspection.json',
                 paths.EVAL_OUT / f'recovery_{alias}' / 'failure_mask.csv'):
        source(path)
    for name in ('eval/common/paths.py', 'eval/offset/carry.py',
                 'eval/offset/fit_offset.py', 'eval/failure/recovery_core.py',
                 'eval/failure/grip_state.py',
                 'eval/failure/moving_window_check.py',
                 'eval/failure/handover_analysis.py',
                 'eval/gt/eval_rail_scenario.py',
                 'eval/inspect/check_v1_overlay.py',
                 'v1/kinematics/root_frame.py'):
        source(REPO / name)
    source(__file__)
    payload['provenance']['sources'] = [
        dict(path=str(p.relative_to(REPO)),
             sha256=hashlib.sha256(p.read_bytes()).hexdigest())
        for p in sorted(SOURCES)]

    pd.DataFrame(rows).to_csv(OUT / 'spatial_check_pairs.csv', index=False,
                              na_rep='nan')
    save_json('spatial_check.json', payload)
    for block in groups:
        if block['n'] == 0:
            print('PASS: %s part, %s hand: no frame at the cube'
                  % (block['part'], block['side']), flush=True)
            continue
        print('PASS: %s part, %s hand: n %d  median %.2f cm  published %.2f cm'
              % (block['part'], block['side'], block['n'], block['median'],
                 block['published_cm']), flush=True)
    print('PASS: Chapter 7 spatial check evidence saved to', OUT)


if __name__ == '__main__':
    main()

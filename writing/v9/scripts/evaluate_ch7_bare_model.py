#!/usr/bin/env python3
"""Pin the bare kinematic-model wrist error for Chapter 7 and Chapter 9.

Two different quantities are involved, and the thesis must keep them
apart:

  bare model   the measured MediaPipe plus aligned-depth wrist against
               the wrist the kinematic model places directly from the
               solved joint angles, the same-frame measured shoulder
               and the recording's calibrated segment lengths. Nothing
               downstream of the solver takes part: no display
               smoother, no avatar, no rig placement.
  rendered rig the same measured wrist against the captured Unity hand
               bone, which is the same solver output after the causal
               display smoother, the avatar's own arm lengths and the
               pelvis-anchored rig placement (audit_evidence/
               ch7_restructured/human.json, Decision D-031).

Selection is not re-invented here. The accepted frame set comes from
evaluate_ch7_restructured.accepted (Decisions D-031 and D-032), and the
script asserts that the frames it scores are exactly the frames
human.json already reports, so the two quantities are comparable frame
for frame. The forward kinematics is the existing one
(evaluate_ch7_restructured.fk, itself the convention of
v1/kinematics/root_frame.py and eval/inspect/check_v1_overlay.py,
duplicated in eval/failure/moving_window_check.fk_wrist).

Reported scopes, both without any error-dependent exclusion:
  section_7_3_frame_set    the accepted frames of the Unity capture
                           subset, identical to human.json.
  recording_wide_accepted  the accepted frames of the whole recording,
                           which the bare-model quantity does not need
                           a capture for.

Writes only audit_evidence/ch7_restructured/bare_model.json and
bare_model_pairs.csv. Run from the repository root:
  python writing/v9/scripts/evaluate_ch7_bare_model.py
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / 'writing/v9/audit_evidence/ch7_restructured'
for folder in ('eval/failure', 'eval/common', 'eval/inspect', 'eval/offset',
               'eval/unity_check', 'eval', 'v1/kinematics', 'v1/aruco',
               'writing/v9/scripts'):
    sys.path.insert(0, str(REPO / folder))

import evaluate_ch7_restructured as ch7
import paths
from check_unity_log import from_to_rotation, DESK_THICK, LEG_H
from send_scene_r5 import AngleLPF, ANGLE_COLS

# The acceptance gate, the forward kinematics and the reading helpers are
# reused, never re-implemented. ch7.SOURCES collects every input those
# helpers touch; it is reset so this script's provenance lists its own
# inputs only.
ch7.SOURCES = set()
read_csv, read_json, stats, xyz = ch7.read_csv, ch7.read_json, ch7.stats, ch7.xyz

CAPTURES = (('r6b', paths.R6B_STEM, 'ch7_trails_revision', 'r6b_trails',
             ('right',)),
            ('r7', paths.R7_STEM, 'ch7_handover_trails', 'r7',
             ('right', 'left')))
# angles_recovery.csv column groups per side: swing, twist, elbow.
TAG_GROUPS = {'right': (1, 2, 3), 'left': (4, 5, 6)}
SENSOR_FLIP = np.array([1., -1., 1.])
P = np.array([[1., 0, 0], [0, 0, 1.], [0, 1., 0]])
D = np.diag([1., -1., 1.])


def save_json(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def scene_transform(stem, stream):
    """Camera frame to Unity world, exactly as evaluate_ch7_restructured
    builds it for the rendered-rig comparison. The map is a rotation plus
    a translation, so it leaves every distance reported here unchanged;
    it is applied only so the emitted coordinates sit in the same frame
    as human_pairs.csv."""
    calibration = read_json(paths.calib_for(stem))
    T = np.linalg.inv(np.asarray(calibration['T_cam_desk'], float))
    M, cp = P @ T[:3, :3] @ D, P @ T[:3, 3]
    g = np.asarray(calibration['scene_geometry']['gravity_up_unity'], float)
    g /= np.linalg.norm(g)
    G = from_to_rotation(g, np.array([0., 1., 0.]))
    plane = -g * calibration['scene_geometry']['origin_above_tabletop_m']

    def project(q):
        return q - g * np.dot(q - plane, g)

    center = (project(np.zeros(3))
              + project(stream[['opx', 'opy', 'opz']].iloc[0].to_numpy())) / 2
    offset = np.array([0., -(G @ (center - g * (DESK_THICK + LEG_H)))[1], 0.])

    def to_world(points_person_space):
        return (G @ (M @ np.asarray(points_person_space, float).T
                     + cp[:, None])).T + offset

    return to_world


def display_filter_check(angles, stream):
    """The streamed angle and pelvis rows must be the recovery-solve
    output passed through the sender's display smoother. Confirming this
    is what makes the bare-model and rendered-rig numbers two views of
    one solver output rather than two unrelated solves."""
    lpf, pel_lpf = AngleLPF(0.5, 8.0), AngleLPF(0.5, 0.02)
    solved = angles[ANGLE_COLS].to_numpy(float)
    pelvis = angles[['pel_x', 'pel_y', 'pel_z']].to_numpy(float)
    smoothed = np.array([lpf(row) for row in solved])
    pelvis_smoothed = np.array([pel_lpf(row) for row in pelvis])
    frames = angles.index.to_numpy()
    joined = stream.reindex(frames)
    angle_delta = float(abs(joined[[f'a{i}' for i in range(13)]].to_numpy(float)
                            - smoothed).max())
    pelvis_delta = float(abs(joined[['pel_x', 'pel_y', 'pel_z']].to_numpy(float)
                             - pelvis_smoothed).max())
    # Identity up to double-precision arithmetic noise. The bound is an
    # analyst-selected numerical check on a reproduction, in the spirit of
    # D-034; it is not a measurement and gates no frame.
    assert angle_delta < 1e-9 and pelvis_delta < 1e-9
    return dict(frames=int(len(frames)), low_pass_gain=0.5,
                angle_rate_cap_deg_per_frame=8.0,
                pelvis_rate_cap_m_per_frame=0.02,
                max_streamed_angle_delta_deg=angle_delta,
                max_streamed_pelvis_delta_m=pelvis_delta,
                reproduction_tolerance='1e-9, arithmetic noise only')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rendered = read_json(OUT / 'human.json')
    summary, pairs = {}, []
    for alias, stem, folder, stream_alias, sides in CAPTURES:
        log = read_csv(REPO / 'writing/v9/figures/src' / folder
                       / 'unity_person_log.csv')
        stream = read_csv(paths.EVAL_OUT / f'unity_check_{stream_alias}'
                          / 'integrated_stream.csv')
        raw = read_csv(paths.lm_raw(stem))
        filtered = read_csv(paths.lm_filtered(stem))
        mask = read_csv(paths.EVAL_OUT / f'recovery_{alias}/failure_mask.csv')
        angles = read_csv(paths.EVAL_OUT / f'recovery_{alias}/angles_recovery.csv')
        lengths = read_json(paths.EVAL_REPORTS
                            / f'{stem}_offset_fit.json')['segment_lengths_m']
        rig_lengths = pd.read_csv(ch7.source(
            REPO / 'writing/v9/figures/src' / folder
            / 'rig_dimensions.csv')).set_index('segment')['meters'].to_dict()
        frames = raw.index.to_numpy()
        for table in (filtered, mask, angles):
            assert np.array_equal(table.index.to_numpy(), frames)
        np.testing.assert_array_equal(filtered.time_s.to_numpy(),
                                      raw.time_s.to_numpy())
        captured = np.isin(frames, log.index.to_numpy())
        to_world = scene_transform(stem, stream)
        solved = angles[ANGLE_COLS].to_numpy(float)
        summary[alias] = dict(
            stem=stem, recording_frames=int(len(raw)),
            captured_frames=int(len(log)),
            angle_source=str((paths.EVAL_OUT / f'recovery_{alias}'
                              / 'angles_recovery.csv').relative_to(REPO)),
            calibrated_segment_lengths_m={
                k: float(v) for k, v in lengths.items()},
            rendered_rig_segment_lengths_m={
                k: float(v) for k, v in rig_lengths.items()},
            display_filter=display_filter_check(angles, stream),
            joints={})
        for side in sides:
            selected = ch7.accepted(raw, filtered, mask, side, stem)
            in_capture = selected & captured
            assert in_capture.any()
            anchor = xyz(filtered, side + '_shoulder') * SENSOR_FLIP
            model = ch7.fk(solved, anchor, lengths, side)
            swing, twist, elbow_tag = TAG_GROUPS[side]
            tags = {name: angles[f'tag_{k}'].to_numpy(int) for name, k in
                    (('root', 0), ('swing', swing), ('twist', twist),
                     ('elbow', elbow_tag))}
            for joint in ('elbow', 'wrist'):
                name = side + '_' + joint
                model_world = to_world(model[joint])
                measured = {
                    'raw': to_world(xyz(raw, name) * SENSOR_FLIP),
                    'filtered': to_world(xyz(filtered, name) * SENSOR_FLIP)}
                error = {k: np.linalg.norm(model_world - v, axis=1) * 100
                         for k, v in measured.items()}
                # The scene map is rigid, so the reported distance is the
                # distance in the solver's own frame.
                direct = np.linalg.norm(model[joint] - xyz(raw, name)
                                        * SENSOR_FLIP, axis=1) * 100
                assert np.nanmax(np.abs(error['raw'] - direct)) < 1e-9
                entry = {}
                for scope, chosen in (('section_7_3_frame_set', in_capture),
                                      ('recording_wide_accepted', selected)):
                    held = chosen & (tags['twist'] == 1)
                    measured_twist = chosen & (tags['twist'] == 0)
                    entry[scope] = dict(
                        n=int(chosen.sum()),
                        vs_raw_measured=stats(error['raw'][chosen]),
                        vs_filtered_measured=stats(error['filtered'][chosen]),
                        frames=frames[chosen].tolist(),
                        output_tags={k: {str(a): int(b) for a, b in
                                         pd.Series(v[chosen]).value_counts().items()}
                                     for k, v in tags.items()},
                        twist_measured_frames=int(measured_twist.sum()),
                        twist_held_frames=int(held.sum()),
                        vs_raw_measured_twist_measured=(
                            stats(error['raw'][measured_twist])
                            if measured_twist.any() else dict(n=0)),
                        vs_raw_measured_twist_held=(
                            stats(error['raw'][held]) if held.any()
                            else dict(n=0)))
                    for i in np.flatnonzero(chosen):
                        row = dict(recording=alias, side=side, joint=joint,
                                   scope=scope, frame=int(frames[i]),
                                   time_s=float(raw.time_s.iloc[i]),
                                   root_tag=int(tags['root'][i]),
                                   twist_tag=int(tags['twist'][i]),
                                   error_cm=float(error['raw'][i]),
                                   error_vs_filtered_cm=float(error['filtered'][i]))
                        for label, point in (('model', model_world[i]),
                                             ('measured', measured['raw'][i]),
                                             ('measured_filtered',
                                              measured['filtered'][i])):
                            row.update({label + '_' + a: float(point[k])
                                        for k, a in enumerate('xyz')})
                        pairs.append(row)
                reference = rendered[alias]['joints'].get(name)
                assert reference is not None, name
                # human.json lists the frames in the receiver's capture
                # order, which is not chronological; the frame set is what
                # has to match.
                assert entry['section_7_3_frame_set']['frames'] \
                    == sorted(reference['frames'])
                entry['rendered_rig_same_frames'] = dict(
                    n=reference['n'], median=reference['median'],
                    p95=reference['p95'], maximum=reference['maximum'])
                summary[alias]['joints'][name] = entry
    pd.DataFrame(pairs).to_csv(OUT / 'bare_model_pairs.csv', index=False)

    # The values Chapter 9 currently prints, recomputed under their own
    # original definition: whole recording, filtered measured wrist, the
    # only gate being an unsubstituted wrist source. Kept so the change
    # against the accepted-frame result is traceable, not to reuse them.
    old = {}
    stem = paths.R7_STEM
    filtered = read_csv(paths.lm_filtered(stem))
    solved = read_csv(paths.EVAL_OUT
                      / 'recovery_r7/angles_recovery.csv')[ANGLE_COLS].to_numpy(float)
    lengths = read_json(paths.EVAL_REPORTS
                        / f'{stem}_offset_fit.json')['segment_lengths_m']
    for side in ('left', 'right'):
        model = ch7.fk(solved, xyz(filtered, side + '_shoulder') * SENSOR_FLIP,
                       lengths, side)
        distance = np.linalg.norm(
            model['wrist'] - xyz(filtered, side + '_wrist') * SENSOR_FLIP,
            axis=1) * 100
        chosen = (filtered[side + '_wrist_src'].to_numpy() == 0) \
            & np.isfinite(distance)
        old[side] = stats(distance[chosen])
    pinned = read_json(paths.EVAL_REPORTS / 'r7_handover.json')
    old['pinned_report'] = pinned['fk_vs_measured_wrist_cm']
    old['reproduced'] = all(
        round(old[s]['median'], 2) == pinned['fk_vs_measured_wrist_cm'][s]['median']
        and round(old[s]['p95'], 2) == pinned['fk_vs_measured_wrist_cm'][s]['p95']
        and round(old[s]['maximum'], 2) == pinned['fk_vs_measured_wrist_cm'][s]['max']
        for s in ('left', 'right'))
    assert old['reproduced']
    old['definition'] = (
        'Whole recording, filtered measured wrist, gate is an unsubstituted '
        'wrist source only. No failure mask, no person-present span, no '
        'detector warmup, no raw-landmark validity, no capture subset. '
        'Source eval/failure/handover_analysis.py, pinned in '
        'eval/reports/r7_handover.json as fk_vs_measured_wrist_cm.')

    for name in ('eval/failure/handover_analysis.py',
                 'eval/failure/moving_window_check.py',
                 'eval/failure/detect_failures.py',
                 'eval/inspect/check_v1_overlay.py',
                 'eval/unity_check/check_unity_log.py',
                 'eval/unity_check/send_scene_r5.py',
                 'eval/offset/fit_offset.py',
                 'eval/failure/recovery_core.py',
                 'v1/kinematics/root_frame.py',
                 'v1/kinematics/shoulder.py',
                 'Unity/Assets/Scripts/IntegratedSceneReceiver.cs',
                 'writing/v9/scripts/evaluate_ch7_restructured.py'):
        ch7.source(REPO / name)
    ch7.source(__file__)
    save_json('bare_model.json', dict(
        quantity=dict(
            bare_model=(
                'Measured MediaPipe wrist with aligned depth against the '
                'wrist placed by the kinematic model from the solved joint '
                'angles, the same-frame measured shoulder and the '
                'recording calibrated segment lengths. No display '
                'smoother, no avatar proportions, no rig placement.'),
            rendered_rig=(
                'The same measured wrist against the captured Unity hand '
                'bone, which is the same solved angles after the causal '
                'display smoother, the avatar arm lengths and the '
                'pelvis-anchored rig placement (human.json, D-031).'),
            reference_kind=('Measured landmark reference: the MediaPipe '
                            'wrist point deprojected with aligned depth. '
                            'Not a physical or manual reference.'),
            forward_kinematics=(
                'Root rotation from the solved Euler angles through '
                'root_frame.recompose_zxy; arm directions through '
                'check_v1_overlay.fk_arm_dirs; elbow = measured shoulder '
                'plus upper-arm length along the rotated upper-arm '
                'direction; wrist = elbow plus forearm length along the '
                'rotated forearm direction. Identical to '
                'moving_window_check.fk_wrist and to the function '
                'evaluate_ch7_restructured already uses.'),
            segment_lengths=('eval/reports/<stem>_offset_fit.json, '
                             'segment_lengths_m, the same values '
                             'recovery_core.build_inputs supplies to the solve.'),
            anchor='Same-frame filtered measured shoulder landmark.',
            frame_alignment='Exact frame number; no lag and no resampling.',
            selection=('evaluate_ch7_restructured.accepted, Decisions D-031 '
                       'and D-032, asserted equal to the human.json frame '
                       'lists. No rejection uses the size of the error.')),
        recordings=summary, chapter_9_previous_values=old,
        numpy=np.__version__, pandas=pd.__version__,
        percentile='numpy.percentile, linear interpolation',
        sources=[dict(path=str(p.relative_to(REPO)),
                      sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                 for p in sorted(ch7.SOURCES)]))
    print('PASS: bare-model evidence saved to', OUT)


if __name__ == '__main__':
    main()

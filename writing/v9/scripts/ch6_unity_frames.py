#!/usr/bin/env python3
"""Number source for the Chapter 6 Unity figure frames (Section 6.4).

Section 6.4 states, for two frames of the rail sensor-view capture, the
distance from the rendered right hand to the measured right wrist and the
elbow bend the solver reported there. Under section 5 of
writing/v9/REVISION_2026-09-14_BRIEF.md no such number may be typed in the
builder, so this script recomputes both from the archived capture and
writes writing/v9/audit_evidence/ch6_unity_frames.json for build_ch6.py to
read.

Two quantities, two independent sources:

  * rendered-to-measured distances. The rendered joint is the rig joint the
    receiver logs in unity_person_log.csv (rh for the right hand, rel for
    the right elbow). The measured joint is the raw landmark of the same
    recording carried into the same scene frame by EXACTLY the mapping of
    writing/v9/scripts/evaluate_ch7_restructured.py human(), lines 124 to
    166: the flip D and swap P of Section 6.3, the inverse of the
    calibrated T_cam_desk, the gravity alignment G built from
    scene_geometry.gravity_up_unity, and the vertical display offset the
    receiver applies, taken from the projected desk centre of this run's
    own integrated_stream.csv first object row. The helpers come from that
    module, so the two evidence files cannot drift apart.

  * elbow bend. Column Rel_y of eval/output/recovery_<alias>/
    angles_recovery.csv, negated: the hinge of Section 3.4 is authored
    about -y, so the solver writes the bend as a negative rotation and the
    thesis prints its magnitude. PINNED_BEND_DEG below reproduces the two
    values Chapter 6 printed before this file existed (14.4 deg at frame
    114, 31.0 deg at frame 700 of the rail recording) and the run fails if
    the column and the sign convention no longer give them.

Frame-index alignment follows the evaluator: the person log's frame column
is the index, and every other table is reindexed onto it
(read_csv(...).reindex(log.index)), so a frame the dumper skipped is
absent from the log and never silently paired with a neighbour. The
evaluator requires the frame column to be unique and so does this script.
A person log left in eval/output/ can hold more than one editor session
appended to the same file, and then it is not unique;
--allow-duplicate-frames accepts such a file only if every repeated frame
carries byte-equal values in every column, keeps the first row of each and
records how many were dropped. It never reconciles disagreeing rows.

Run (defaults are the rail sensor-view capture of E-037):
  /home/luo/anaconda3/bin/python writing/v9/scripts/ch6_unity_frames.py

Exercise on another capture without touching the audit evidence:
  ... ch6_unity_frames.py --stem recording_20260909_000024 \
      --person-log eval/output/unity_check_r7/unity_person_log.csv \
      --stream eval/output/unity_check_r7/integrated_stream.csv \
      --frames 700 950 --out <scratch>/ch6_unity_frames_r7.json
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

# The mapping and its constants belong to the Chapter 7 evaluator; import
# them rather than restating them (the module only defines functions at
# import time, and it puts eval/common, eval/failure, eval/unity_check and
# v1/kinematics on sys.path for paths and check_unity_log).
from evaluate_ch7_restructured import paths, xyz
from evaluate_ch7_restructured import from_to_rotation, DESK_THICK, LEG_H

# Chapter 6 printed these before this file existed (build_ch6.py around
# line 505 and its source comment, "Rel_y -14.4 / -31.0 deg from
# eval/output/recovery_r6b/angles_recovery.csv"). They are a regression on
# the column choice and the sign convention, not a tolerance to widen.
PINNED_BEND_DEG = {(paths.R6B_STEM, 114): 14.4, (paths.R6B_STEM, 700): 31.0}
BEND_COLUMN = {'right': 'Rel_y', 'left': 'Lel_y'}
BEND_SIGN = -1.0        # solver hinge is negative; the thesis prints |bend|

DEFAULT_PERSON_LOG = 'writing/v9/figures/src/r6b_unity_sensor/unity_person_log.csv'
DEFAULT_STREAM = 'eval/output/unity_check_r6b_v9/integrated_stream.csv'
DEFAULT_OUT = 'writing/v9/audit_evidence/ch6_unity_frames.json'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def read_csv(path):
    """The evaluator's reader: frame is the index and must be unique."""
    frame = pd.read_csv(path)
    assert frame.frame.is_unique, path
    return frame.set_index('frame', drop=False)


def read_person_log(path, allow_duplicates):
    """The evaluator's reader, with the appended-session case made explicit.

    Returns (log, note). A unique frame column takes the evaluator's path
    and the note says so. A repeated frame column is a file that holds two
    editor sessions appended to one log; it is accepted only under the
    explicit flag, only when every repeated frame agrees in every column,
    and the note records the counts."""
    frame = pd.read_csv(path)
    if frame.frame.is_unique:
        return frame.set_index('frame', drop=False), dict(
            rows=int(len(frame)), duplicate_rows_dropped=0, unique_frames=int(len(frame)),
            note='frame column unique, the evaluator convention')
    repeated = frame[frame.frame.duplicated(keep=False)]
    n_repeated_frames = int(repeated.frame.nunique())
    n_dropped = int(len(frame) - frame.frame.nunique())
    if not allow_duplicates:
        sys.exit(f'FAIL: {path} repeats {n_repeated_frames} frames '
                 f'({n_dropped} extra rows); the evaluator requires a unique '
                 'frame column. Pass --allow-duplicate-frames to accept a log '
                 'that holds more than one editor session, which is checked '
                 'for byte-equal repeats first.')
    disagree = sorted(int(key) for key, group in repeated.groupby('frame')
                      if group.drop_duplicates().shape[0] != 1)
    if disagree:
        sys.exit(f'FAIL: {path} repeats {len(disagree)} frames with '
                 f'differing values (first: {disagree[:10]}); the two sessions '
                 'rendered different rigs and no row may be chosen here.')
    log = frame.drop_duplicates(subset='frame', keep='first')
    return log.set_index('frame', drop=False), dict(
        rows=int(len(frame)), duplicate_rows_dropped=n_dropped,
        unique_frames=int(len(log)), repeated_frames=n_repeated_frames,
        note='more than one editor session appended to one log; every '
             'repeated frame agreed in every column and the first row of '
             'each was kept')


def bend_check(angles_path, side, stem):
    """Prove the elbow bend column and sign before any capture exists.

    Prints, for every pinned frame of the stem, the value of every angle
    column, so the choice of column can be audited rather than trusted,
    then asserts that BEND_SIGN * BEND_COLUMN[side] rounds to the value
    Chapter 6 printed. Reads the angle CSV and nothing else."""
    angles = read_csv(angles_path)
    pinned = {frame: value for (pin_stem, frame), value
              in sorted(PINNED_BEND_DEG.items()) if pin_stem == stem}
    if not pinned:
        sys.exit(f'FAIL: no pinned elbow bend is recorded for {stem}')
    column = BEND_COLUMN[side]
    skip = ('frame', 'time_s', 'live_mask')
    names = [c for c in angles.columns
             if c not in skip and not c.startswith(('tag_', 'pel_'))]
    print(f'elbow bend column audit: {angles_path}')
    print(f'pinned {side} elbow bend (build_ch6.py): '
          + ', '.join(f'frame {f} -> {v} deg' for f, v in pinned.items()))
    print(f'{"column":<10}' + ''.join(f'{"frame " + str(f):>14}' for f in pinned)
          + ''.join(f'{"-1x f" + str(f):>14}' for f in pinned))
    for name in names:
        row = [float(angles.loc[f, name]) for f in pinned]
        print(f'{name:<10}' + ''.join(f'{v:>14.4f}' for v in row)
              + ''.join(f'{BEND_SIGN * v:>14.4f}' for v in row))
    ok = True
    for frame, value in pinned.items():
        got = BEND_SIGN * float(angles.loc[frame, column])
        agree = round(got, 1) == value
        ok &= agree
        print(f'{"PASS" if agree else "FAIL"}  frame {frame}: '
              f'{BEND_SIGN:+.0f} * {column} = {got:.4f} deg, rounds to '
              f'{round(got, 1)}, pinned {value}')
    matches = [name for name in names
               if all(round(BEND_SIGN * float(angles.loc[f, name]), 1) == v
                      for f, v in pinned.items())]
    print(f'columns that reproduce every pinned value under the same sign: '
          f'{matches}')
    return 0 if ok and matches == [column] else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--person-log', default=DEFAULT_PERSON_LOG,
                    help='receiver rig-joint log of the capture to score '
                         '(default: %(default)s)')
    ap.add_argument('--stream', default=DEFAULT_STREAM,
                    help="the same run's integrated_stream.csv; its first "
                         'object row fixes the display offset '
                         '(default: %(default)s)')
    ap.add_argument('--stem', default=paths.R6B_STEM,
                    help='recording replayed (default: %(default)s)')
    ap.add_argument('--angles', default=None,
                    help='angles_recovery.csv of the recording; default '
                         'eval/output/recovery_<alias>/angles_recovery.csv')
    ap.add_argument('--side', default='right', choices=('right', 'left'))
    ap.add_argument('--frames', type=int, nargs='+', default=[114, 700],
                    help='frames to report (default: %(default)s)')
    ap.add_argument('--out', default=DEFAULT_OUT,
                    help='JSON to write (default: %(default)s)')
    ap.add_argument('--allow-duplicate-frames', action='store_true',
                    help='accept a person log that holds more than one '
                         'editor session appended to the same file, provided '
                         'every repeated frame agrees in every column; off by '
                         'default, so an archived log is read strictly')
    ap.add_argument('--bend-check', action='store_true',
                    help='audit the elbow bend column against the values '
                         'Chapter 6 printed, from the angle CSV alone; writes '
                         'nothing and needs no capture')
    args = ap.parse_args()

    stem, side = args.stem, args.side
    alias = paths.ALIAS[stem]
    person_log = Path(args.person_log)
    stream_path = Path(args.stream)
    angles_path = Path(args.angles) if args.angles else (
        paths.EVAL_OUT / f'recovery_{alias}/angles_recovery.csv')
    raw_path = paths.lm_raw(stem)
    calib_path = paths.calib_for(stem)
    if args.bend_check:
        if not Path(angles_path).exists():
            sys.exit(f'FAIL: input {angles_path} is missing')
        return bend_check(angles_path, side, stem)
    for path in (person_log, stream_path, angles_path, raw_path, calib_path):
        if not Path(path).exists():
            sys.exit(f'FAIL: input {path} is missing')

    log, log_note = read_person_log(person_log, args.allow_duplicate_frames)
    stream = read_csv(stream_path)
    raw = read_csv(raw_path).reindex(log.index)
    angles = read_csv(angles_path).reindex(log.index)
    calibration = json.loads(Path(calib_path).read_text())

    # ---- evaluate_ch7_restructured.py human(), lines 124 to 166 ----------
    # Copied structure, executed with the imported helpers; every constant
    # below is the evaluator's, with no substitution.
    P = np.array([[1., 0, 0], [0, 0, 1.], [0, 1., 0]])
    D = np.diag([1., -1., 1.])
    T = np.linalg.inv(np.asarray(calibration['T_cam_desk'], float))
    M, cp = P @ T[:3, :3] @ D, P @ T[:3, 3]
    g = np.asarray(calibration['scene_geometry']['gravity_up_unity'], float)
    g /= np.linalg.norm(g)
    G = from_to_rotation(g, np.array([0., 1., 0.]))
    plane = -g * calibration['scene_geometry']['origin_above_tabletop_m']

    def project(q):
        return q - g * np.dot(q - plane, g)

    first_object = stream[['opx', 'opy', 'opz']].iloc[0].to_numpy()
    center = (project(np.zeros(3)) + project(first_object)) / 2
    offset = np.array([0., -(G @ (center - g * (DESK_THICK + LEG_H)))[1], 0.])
    # ---- end of the copied block ----------------------------------------

    # The evaluator's own consistency checks on the log against the stream
    # and against the mapping. They are what proves these constants are the
    # ones this capture was rendered with.
    time_delta = float(abs(log.time_s - raw.time_s).max())
    pelvis_delta = float(abs(xyz(log, 'pel')
                             - xyz(stream.reindex(log.index), 'pel')).max())
    expected_hip = (G @ (M @ xyz(log, 'pel').T + cp[:, None])).T + offset
    hip_delta = float(abs(xyz(log, 'hip') - expected_hip).max())
    assert time_delta <= 1e-5 and pelvis_delta < 1e-5 and hip_delta < 1e-3, (
        time_delta, pelvis_delta, hip_delta)
    assert np.array_equal(log['mask'], stream.reindex(log.index)['mask'])

    measured = {}
    for joint in ('wrist', 'elbow'):
        measured[joint] = (G @ (P @ T[:3, :3] @ xyz(raw, side + '_' + joint).T
                                + cp[:, None])).T + offset
    rendered = {'wrist': xyz(log, side[0] + 'h'),      # rig hand, rh / lh
                'elbow': xyz(log, side[0] + 'el')}     # rig elbow, rel / lel

    column = BEND_COLUMN[side]
    frames, mismatches = {}, []
    for frame in args.frames:
        if frame not in log.index:
            sys.exit(f'FAIL: frame {frame} is not in {person_log} (the dumper '
                     'never writes the final frame of a recording)')
        i = int(np.flatnonzero(log.index.to_numpy() == frame)[0])
        hand_wrist = float(np.linalg.norm(rendered['wrist'][i]
                                          - measured['wrist'][i]) * 100)
        elbow_elbow = float(np.linalg.norm(rendered['elbow'][i]
                                           - measured['elbow'][i]) * 100)
        signed = float(angles[column].iloc[i])
        bend = BEND_SIGN * signed
        entry = dict(hand_to_wrist_cm=hand_wrist,
                     elbow_to_elbow_cm=elbow_elbow,
                     elbow_bend_deg=bend,
                     time_s=float(log.time_s.iloc[i]),
                     mask=int(log['mask'].iloc[i]),
                     root_tag=int(angles.tag_0.iloc[i]),
                     elbow_bend_signed_deg=signed,
                     rendered_hand_m=rendered['wrist'][i].tolist(),
                     measured_wrist_m=measured['wrist'][i].tolist(),
                     rendered_elbow_m=rendered['elbow'][i].tolist(),
                     measured_elbow_m=measured['elbow'][i].tolist())
        pinned = PINNED_BEND_DEG.get((stem, frame))
        if pinned is not None:
            entry['pinned_elbow_bend_deg'] = pinned
            entry['pinned_elbow_bend_reproduced'] = bool(
                round(bend, 1) == pinned)
            if not entry['pinned_elbow_bend_reproduced']:
                mismatches.append((frame, pinned, bend))
        frames[str(frame)] = entry

    if mismatches:
        for frame, pinned, bend in mismatches:
            print(f'FAIL: frame {frame}: {column} gives {bend:.4f} deg, '
                  f'the value Chapter 6 printed is {pinned}')
        sys.exit('FAIL: the elbow bend column or sign convention no longer '
                 'reproduces the printed values; report the columns and their '
                 'values instead of choosing a new one')

    pinned_for_stem = {str(frame): value for (pin_stem, frame), value
                       in sorted(PINNED_BEND_DEG.items()) if pin_stem == stem}
    output = {
        'purpose': 'Chapter 6 Section 6.4 frame numbers: rendered-to-measured '
                   'distances and the elbow bend on the figure frames',
        'units': 'hand_to_wrist_cm and elbow_to_elbow_cm in centimetres; '
                 'elbow_bend_deg in degrees, magnitude of the solved hinge',
        'recording': {'stem': stem, 'alias': alias, 'side': side,
                      'captured_frames': int(len(log)),
                      'recording_frames': int(len(stream)),
                      'person_log': log_note},
        'definitions': {
            'hand_to_wrist_cm': 'distance from the rig hand joint the '
                                'receiver logs (rh/lh of unity_person_log.csv) '
                                'to the raw measured wrist landmark of the '
                                'same frame, both in the levelled scene frame',
            'elbow_to_elbow_cm': 'the same for the rig elbow (rel/lel) and '
                                 'the raw measured elbow landmark',
            'elbow_bend_deg': f'{BEND_SIGN:+.0f} times column {column} of '
                              'angles_recovery.csv, the magnitude of the '
                              'solved elbow hinge of Section 3.4',
            'mapping': 'evaluate_ch7_restructured.py human(), lines 124 to '
                       '166: measured = (G (P T[:3,:3] x + P T[:3,3])) + '
                       'offset, with T = inv(T_cam_desk)',
            'frame_alignment': "the person log's frame column is the index; "
                               'the landmark and angle tables are reindexed '
                               'onto it, as the evaluator does',
            'no_error_attribution': 'D-043 and brief fact 5: the distance is '
                                    'a rendered discrepancy of the whole '
                                    'display path and no share of it is '
                                    'assigned to the rig, the filter or any '
                                    'single stage',
        },
        'mapping_constants': {
            'swap_P': P.tolist(), 'flip_D': D.tolist(),
            'T_inv_cam_desk': T.tolist(),
            'M_swap_rot_flip': M.tolist(), 'cp_swap_translation_m': cp.tolist(),
            'gravity_up_unity_normalised': g.tolist(),
            'G_gravity_alignment': G.tolist(),
            'origin_above_tabletop_m': float(
                calibration['scene_geometry']['origin_above_tabletop_m']),
            'tabletop_plane_point_m': plane.tolist(),
            'desk_thick_m': DESK_THICK, 'leg_h_m': LEG_H,
            'stream_first_object_position_m': first_object.tolist(),
            'projected_desk_centre_m': center.tolist(),
            'display_offset_m': offset.tolist(),
            'camera_to_unity_linear': (G @ P @ T[:3, :3]).tolist(),
            'camera_to_unity_translation': (G @ cp + offset).tolist(),
        },
        'log_consistency': {
            'time_delta_s': time_delta, 'pelvis_delta_m': pelvis_delta,
            'hip_mapping_delta_m': hip_delta,
            'mask_identical_to_stream': True,
            'tolerances': {'time_delta_s': 1e-5, 'pelvis_delta_m': 1e-5,
                           'hip_mapping_delta_m': 1e-3},
        },
        'elbow_bend_source': {
            'path': str(angles_path.relative_to(REPO)),
            'column': column, 'sign': BEND_SIGN,
            'pinned_values_deg': pinned_for_stem,
            'pinned_values_reproduced': (True if pinned_for_stem else None),
            'pinned_note': ('every value Chapter 6 printed for this recording '
                            'is reproduced by this column and sign'
                            if pinned_for_stem else
                            'no value was pinned for this recording, so this '
                            'run is a code-path exercise only'),
            'column_audit': 'run with --bend-check to list every angle column '
                            'at the pinned frames and confirm this column is '
                            'the only one that reproduces them',
        },
        'frames': frames,
        'sources': [],
    }
    for path in (person_log, stream_path, raw_path, angles_path, calib_path,
                 Path(__file__).resolve(),
                 REPO / 'writing/v9/scripts/evaluate_ch7_restructured.py'):
        path = Path(path).resolve()
        output['sources'].append({
            'path': str(path.relative_to(REPO)),
            'bytes': path.stat().st_size, 'sha256': sha256(path)})

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, indent=2, allow_nan=False) + '\n')
    print(out)
    print(f'{stem} ({alias}), {side} arm, {len(log)} captured frames of '
          f'{len(stream)}')
    print(f'log consistency: time {time_delta:.2e} s, pelvis '
          f'{pelvis_delta:.2e} m, hip mapping {hip_delta:.2e} m')
    for frame in args.frames:
        entry = frames[str(frame)]
        pinned = entry.get('pinned_elbow_bend_deg')
        tail = '' if pinned is None else f'  (pinned {pinned}, reproduced)'
        print(f'frame {frame:>5}: hand to wrist {entry["hand_to_wrist_cm"]:.1f} '
              f'cm, elbow to elbow {entry["elbow_to_elbow_cm"]:.1f} cm, '
              f'elbow bend {entry["elbow_bend_deg"]:.1f} deg'
              f' ({column} {entry["elbow_bend_signed_deg"]:.4f}){tail}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

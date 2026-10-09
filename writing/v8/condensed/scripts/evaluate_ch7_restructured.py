#!/usr/bin/env python3
"""Pin Chapter 7 coordinate comparisons without modifying experiment inputs.

Decisions D-031 to D-033 define selection and reference scope. This script
reads local experiment inputs; the emitted coordinate pairs support an
independent statistics check on machines without the recordings.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[4]
OUT = REPO / 'writing/v8/condensed/audit_evidence/ch7_restructured'
for folder in ('eval/failure', 'eval/common', 'eval/inspect',
               'eval/offset', 'eval/unity_check', 'v1/kinematics'):
    sys.path.insert(0, str(REPO / folder))

import paths
import recovery_core as rc
import harness_recovery as hr
import grip_state
from detect_failures import WARMUP_FRAMES
from check_unity_log import from_to_rotation, DESK_THICK, LEG_H
from root_frame import recompose_zxy
from check_v1_overlay import fk_arm_dirs

SOURCES = set()


def source(path):
    path = Path(path)
    SOURCES.add(path.resolve())
    return path


def read_csv(path):
    df = pd.read_csv(source(path))
    assert df.frame.is_unique, path
    return df.set_index('frame', drop=False)


def read_json(path):
    return json.loads(source(path).read_text())


def save_json(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def stats(values):
    values = np.asarray(values, float)
    assert values.size and np.isfinite(values).all()
    return dict(n=len(values), median=float(np.median(values)),
                p95=float(np.percentile(values, 95, method='linear')),
                maximum=float(values.max()))


def xyz(df, prefix):
    return df[[prefix + '_' + a for a in 'xyz']].to_numpy(float)


def accepted(raw, filtered, fm, side, stem):
    """Operational input validity, with no error-dependent exclusions."""
    assert raw.index.equals(filtered.index) and raw.index.equals(fm.index)
    span = read_json(paths.EVAL_REPORTS / f'{stem}_inspection.json')['phases']['person_present']
    ok = ((raw.index.to_numpy() >= span[0] + WARMUP_FRAMES)
          & (raw.index.to_numpy() <= span[1]))
    names = sorted(set(['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']
                       + [side + '_' + j for j in ('shoulder', 'elbow', 'wrist')]))
    for name in names:
        ok &= ((raw[name + '_src'].to_numpy() == 0)
               & (filtered[name + '_src'].to_numpy() == 0)
               & (filtered[name + '_flag'].to_numpy() == 0))
        for df in (raw, filtered):
            points = xyz(df, name)
            ok &= np.isfinite(points).all(axis=1) & (points[:, 2] > 0)
    tag = 'R' if side == 'right' else 'L'
    flags = [f'd1_{tag}', f'd2_{tag}', f'd5_{tag}', f'fail_arm_{tag}',
             'd1_torso', 'd3', 'd4', 'd5_torso', 'fail_torso']
    for flag in flags:
        ok &= fm[flag].to_numpy() == 0
    return ok


def human():
    pairs, summary = [], {}
    P = np.array([[1., 0, 0], [0, 0, 1.], [0, 1., 0]])
    D = np.diag([1., -1., 1.])
    for alias, stem, folder in (
            ('r6b', paths.R6B_STEM, 'ch7_trails_revision'),
            ('r7', paths.R7_STEM, 'ch7_handover_trails')):
        log = read_csv(REPO / 'writing/v8/condensed/figures/src' / folder / 'unity_person_log.csv')
        raw = read_csv(paths.lm_raw(stem)).reindex(log.index)
        filtered = read_csv(paths.lm_filtered(stem)).reindex(log.index)
        fm = read_csv(paths.EVAL_OUT / f'recovery_{alias}/failure_mask.csv').reindex(log.index)
        angles = read_csv(paths.EVAL_OUT / f'recovery_{alias}/angles_recovery.csv').reindex(log.index)
        stream_alias = 'r6b_trails' if alias == 'r6b' else alias
        stream = read_csv(paths.EVAL_OUT / f'unity_check_{stream_alias}/integrated_stream.csv')
        calibration = read_json(paths.calib_for(stem))
        T = np.linalg.inv(np.asarray(calibration['T_cam_desk'], float))
        M, cp = P @ T[:3, :3] @ D, P @ T[:3, 3]
        g = np.asarray(calibration['scene_geometry']['gravity_up_unity'], float)
        g /= np.linalg.norm(g)
        G = from_to_rotation(g, np.array([0., 1., 0.]))
        plane = -g * calibration['scene_geometry']['origin_above_tabletop_m']
        def project(q):
            return q - g * np.dot(q - plane, g)
        center = (project(np.zeros(3)) + project(stream[['opx', 'opy', 'opz']].iloc[0].to_numpy())) / 2
        offset = np.array([0., -(G @ (center - g * (DESK_THICK + LEG_H)))[1], 0.])
        # Pelvis tolerances follow the existing checker; timestamp tolerance
        # is the explicitly provisional serialization check of D-034.
        time_delta = float(abs(log.time_s - raw.time_s).max())
        pelvis_delta = float(abs(xyz(log, 'pel') - xyz(stream.reindex(log.index), 'pel')).max())
        expected_hip = (G @ (M @ xyz(log, 'pel').T + cp[:, None])).T + offset
        hip_delta = float(abs(xyz(log, 'hip') - expected_hip).max())
        assert time_delta <= 1e-5 and pelvis_delta < 1e-5 and hip_delta < 1e-3
        assert np.array_equal(log['mask'], stream.reindex(log.index)['mask'])
        summary[alias] = dict(captured_frames=len(log), recording_frames=len(stream),
                             time_delta_s=time_delta, pelvis_delta_m=pelvis_delta,
                             hip_mapping_delta_m=hip_delta,
                             camera_to_unity_linear=(G @ P @ T[:3, :3]).tolist(),
                             camera_to_unity_translation=(G @ cp + offset).tolist(),
                             joints={})
        for side in (('right',) if alias == 'r6b' else ('right', 'left')):
            selected = accepted(raw, filtered, fm, side, stem)
            assert selected.any()
            root_tags = angles.loc[selected, 'tag_0'].value_counts().to_dict()
            for joint, prefix in (('elbow', side[0] + 'el'), ('wrist', side[0] + 'h')):
                measured = (G @ (P @ T[:3, :3] @ xyz(raw, side + '_' + joint).T
                                  + cp[:, None])).T + offset
                rig = xyz(log, prefix)
                error = np.linalg.norm(rig - measured, axis=1) * 100
                key = side + '_' + joint
                summary[alias]['joints'][key] = dict(
                    **stats(error[selected]), frames=log.index[selected].tolist(),
                    root_output_tags={str(k): int(v) for k, v in root_tags.items()})
                for i in np.flatnonzero(selected):
                    row = dict(recording=alias, side=side, joint=joint,
                               frame=int(log.index[i]), time_s=float(log.time_s.iloc[i]),
                               root_tag=int(angles.tag_0.iloc[i]), error_cm=float(error[i]))
                    for name, point in (('measured', measured[i]), ('rig', rig[i])):
                        row.update({name + '_' + a: float(point[k]) for k, a in enumerate('xyz')})
                    pairs.append(row)
    pd.DataFrame(pairs).to_csv(OUT / 'human_pairs.csv', index=False)
    save_json('human.json', summary)
    return summary


def fk(angles, shoulders, lengths, side):
    tag, start = ('R', 3) if side == 'right' else ('L', 8)
    elbows, wrists = [], []
    for i, a in enumerate(angles):
        root = recompose_zxy(a[:3])
        up, fore = fk_arm_dirs(a[start:start + 3], a[start + 3:start + 5], side)
        e = shoulders[i] + lengths['upper_arm_' + tag] * (root @ up)
        elbows.append(e)
        wrists.append(e + lengths['forearm_' + tag] * (root @ fore))
    return dict(elbow=np.asarray(elbows), wrist=np.asarray(wrists))


def synthetic():
    stem, side = paths.R7_STEM, 'right'
    base = rc.build_inputs(stem)
    truth = rc.run_variant(base, 'plain')
    ctx = hr.grip_context(stem, base)
    raw, filtered = read_csv(paths.lm_raw(stem)), read_csv(paths.lm_filtered(stem))
    fm = read_csv(paths.EVAL_OUT / 'recovery_r7/failure_mask.csv')
    obj = read_csv(paths.object_world_filtered(stem))
    assert np.array_equal(raw.frame, np.arange(base['n']))
    assert np.array_equal(filtered.frame, base['lm_df'].frame)
    for df in (filtered, fm, obj):
        assert np.array_equal(df.frame, raw.frame)
        np.testing.assert_array_equal(df.time_s.to_numpy(), raw.time_s.to_numpy())
    ok = accepted(raw, filtered, fm, side, stem)
    ok &= hr.select_windows(base, truth, ctx, side, side_only=True)['ok']
    for bit in (0, *hr.ARM_BITS[side]):
        ok &= (truth['mask'] & (1 << bit)) != 0
    run_lengths = hr._run_len(ctx[side]['hold_clean'] & ~base['fail'][side] & ~base['fail']['torso'])
    established = np.r_[False, run_lengths[:-1] >= grip_state.ENTER_FRAMES]
    shoulders = xyz(filtered, side + '_shoulder') * [1., -1., 1.]
    reference = fk(truth['angles'], shoulders, base['seg_len'], side)
    candidates = []
    for a, b in hr._runs(ok, hr.WIN):
        for start in range(a, b - hr.WIN + 2):
            stop = start + hr.WIN - 1
            if established[start]:
                extent = np.linalg.norm(reference['wrist'][start:stop + 1]
                                        - reference['wrist'][start], axis=1).max() * 100
                candidates.append(dict(start=start, stop=stop, excursion_cm=float(extent)))
    assert len(candidates) >= 3
    low = min(candidates, key=lambda x: (x['excursion_cm'], x['start']))
    def remaining(chosen):
        return [x for x in candidates if all(x['stop'] < c['start'] or x['start'] > c['stop'] for c in chosen)]
    high = min(remaining([low]), key=lambda x: (-x['excursion_cm'], x['start']))
    mid_target = float(np.median([x['excursion_cm'] for x in candidates]))
    mid = min(remaining([low, high]), key=lambda x: (abs(x['excursion_cm'] - mid_target), x['start']))
    chosen = [dict(low, window='lower motion'), dict(mid, window='intermediate motion'),
              dict(high, window='higher motion')]
    selection = dict(recording='r7', side=side, duration_frames=hr.WIN,
                     reference='Unmasked forward kinematics; all relevant input and output groups valid.',
                     motion='Maximum wrist distance from its first position within each window.',
                     eligible_runs=hr._runs(ok, 1), candidates=candidates, selected=chosen)
    save_json('synthetic_selection.json', selection)
    print('PASS: synthetic selection pinned before masked runs', flush=True)
    rows, results = [], []
    for window in chosen:
        a, b = window['start'], window['stop']
        inp, mask = hr.masked_inputs(stem, base['n'], side, (a, b), 'S1_arm')
        assert ok[a:b + 1].all() and mask.sum() == hr.WIN
        # Fresh complete replay per method; scored samples excluded from grip fitting.
        variants = {'hold-last': rc.run_hold_baseline(inp),
                    'direction memory': rc.run_variant(inp, 'masked'),
                    'object-assisted': rc.run_variant(inp, 'recovery')}
        assert np.isfinite(inp['w_hat_solver'][side][a:b + 1]).all()
        local_clean = ctx[side]['hold_clean'] & ~inp['fail'][side]
        local_mu = grip_state.time_local_mu(ctx[side]['d_loc'], local_clean, inp['episodes'][side])
        assert not local_clean[a:b + 1].any()
        assert np.isfinite(local_mu[a - 1:b + 1]).all()
        np.testing.assert_array_equal(local_mu[a - 1:b + 1],
                                      np.tile(local_mu[a - 1], (b - a + 2, 1)))
        for method, solved in variants.items():
            points = fk(solved['angles'], shoulders, base['seg_len'], side)
            np.testing.assert_array_equal(solved['angles'][a - 1, :8], truth['angles'][a - 1, :8])
            for joint in ('elbow', 'wrist'):
                np.testing.assert_array_equal(points[joint][a - 1], reference[joint][a - 1])
            for joint in ('elbow', 'wrist'):
                errors = np.linalg.norm(points[joint][a:b + 1] - reference[joint][a:b + 1], axis=1) * 100
                results.append(dict(**window, method=method, joint=joint, **stats(errors)))
                for frame in range(a, b + 1):
                    row = dict(window=window['window'], method=method, joint=joint, frame=frame,
                               error_cm=float(errors[frame - a]))
                    for name, point in (('reference', reference[joint][frame]), ('reconstructed', points[joint][frame])):
                        row.update({name + '_' + ax: float(point[k]) for k, ax in enumerate('xyz')})
                    rows.append(row)
        print('PASS: synthetic window', a, b, flush=True)
    pd.DataFrame(rows).to_csv(OUT / 'synthetic_pairs.csv', index=False)
    save_json('synthetic.json', dict(selection=selection, results=results))
    return results


def natural():
    # Historical per-frame values have already been independently recomputed
    # from angles and proxy coordinates; preserve their reported precision.
    pinned = read_json(paths.EVAL_REPORTS / 'r5_recovery_labeled.json')
    labels = read_json(REPO / 'eval/labels/frames_r5/labels.json')
    meta = read_json(REPO / 'eval/labels/frames_r5/meta.json')
    rows = pinned['rows']
    raw = read_csv(paths.lm_raw(paths.R5_STEM))
    filtered = read_csv(paths.lm_filtered(paths.R5_STEM))
    fm = read_csv(paths.EVAL_OUT / 'recovery_r5/failure_mask.csv')
    for row in rows:
        label = labels[str(row['frame'])][row['side']]
        assert label is not None and not label.get('mixed_surface', False)
        assert (row['frame'] in map(int, meta['clean_frames'])) == (row['group'] == 'clean')
        if row['group'] == 'clean':
            frame, side = row['frame'], row['side']
            name, tag = side + '_wrist', 'R' if side == 'right' else 'L'
            assert raw.loc[frame, name + '_src'] == 0
            assert filtered.loc[frame, name + '_flag'] == 0
            assert fm.loc[frame, 'fail_arm_' + tag] == 0
            measured = filtered.loc[frame, [name + '_' + a for a in 'xyz']].to_numpy(float)
            raw_point = raw.loc[frame, [name + '_' + a for a in 'xyz']].to_numpy(float)
            assert np.isfinite(measured).all() and np.isfinite(raw_point).all()
            assert measured[2] > 0 and raw_point[2] > 0
            distance = np.linalg.norm(measured - np.asarray(label['xyz_cam'])) * 100
            assert round(float(distance), 2) == row['measured_cm']
    summary = dict(clean={}, failure={})
    for side in ('left', 'right'):
        clean = [r for r in rows if r['side'] == side and r['group'] == 'clean']
        failure = [r for r in rows if r['side'] == side and r['group'] == 'failure']
        def preserved(group, method):
            s = pinned['summary'][group][side][method]
            return dict(n=s['n'], median=s['median'], p95=s['p95'], maximum=s['max'])
        summary['clean'][side] = preserved('clean', 'measured')
        summary['failure'][side] = {m: preserved('failure', m)
                                    for m in ('plain_fk', 'hold_fk', 'recovery_fk')}
        assert summary['clean'][side]['n'] == len(clean)
        assert all(s['n'] == len(failure) for s in summary['failure'][side].values())
    serial_rows = [{k: (None if isinstance(v, float) and not np.isfinite(v) else v)
                    for k, v in row.items()} for row in rows]
    save_json('natural.json', dict(summary=summary, rows=serial_rows,
                                 reference='Manual bracelet/watch wrist proxy; clean baseline is accepted filtered wrist.'))
    return summary


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    human()
    synthetic()
    natural()
    # Pin dependencies read indirectly by the existing experiment functions.
    for stem in (paths.R7_STEM, paths.R5_STEM):
        alias = paths.ALIAS[stem]
        for path in (paths.lm_raw(stem), paths.lm_filtered(stem), paths.calib_for(stem),
                     paths.object_world_filtered(stem),
                     paths.EVAL_REPORTS / f'{stem}_offset_fit.json',
                     paths.EVAL_REPORTS / f'{stem}_inspection.json'):
            source(path)
        for name in ('angles_plain.csv', 'angles_hold.csv', 'angles_recovery.csv', 'failure_mask.csv'):
            source(paths.EVAL_OUT / f'recovery_{alias}' / name)
    for name in ('eval/failure/recovery_core.py', 'eval/failure/harness_recovery.py',
                 'eval/failure/grip_state.py', 'eval/failure/detect_failures.py',
                 'eval/offset/carry.py', 'eval/offset/fit_offset.py',
                 'eval/inspect/check_v1_overlay.py', 'eval/unity_check/check_unity_log.py',
                 'eval/unity_check/send_scene_r5.py', 'Unity/Assets/Scripts/IntegratedSceneReceiver.cs',
                 'Unity/Assets/Scripts/ArucoSceneReceiver.cs',
                 'v1/kinematics/occlusion.py', 'v1/kinematics/occlusion_ext.py',
                 'v1/kinematics/root_frame.py'):
        source(REPO / name)
    source(__file__)
    save_json('provenance.json', dict(
        numpy=np.__version__, pandas=pd.__version__,
        percentile='numpy.percentile, linear interpolation',
        sources=[dict(path=str(p.relative_to(REPO)), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                 for p in sorted(SOURCES)]))
    print('PASS: Chapter 7 evidence saved to', OUT)


if __name__ == '__main__':
    main()

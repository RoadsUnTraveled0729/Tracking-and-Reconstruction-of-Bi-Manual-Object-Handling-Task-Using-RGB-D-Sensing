#!/usr/bin/env python3
"""Independent source-clock, frame geometry and rotation checks, merged pages 13-16.

Sibling of check_unified_sources.py for the unified_four collection (plan
virtual-wiggling-globe.md, M1, 2026-09-24). The producer is
anim/bank_axes_kinematics.py (derived files in unified_four/pNN, whole-bag
extractions p13, p17, p18, p19 bound by hash). Besides the source-clock and
reconstruction checks of the earlier sibling, every selected frame of pages
14-16 must satisfy the rotation identity the films draw: the X axis of the
rotated frame lies on the bone within ROTATION_TOL_DEG (page 14: root @ Ry @
Rz onto L12->L14; page 15: the arm frame X, shared with the swing frame, on
L12->L14; page 16: arm @ Ry(el_y) @ Rz(el_z) onto L14->L16). The producer is
imported only for fail-closed negative tests. Writes
bank_processing/UNIFIED_FOUR_SOURCE_CHECK.json.
"""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
import cv2
import numpy as np
import pandas as pd
from PIL import Image
from scipy.spatial.transform import Rotation

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRODUCER = HERE.parent / 'anim/bank_axes_kinematics.py'
REPORT = HERE / 'UNIFIED_FOUR_SOURCE_CHECK.json'
NAMES = ['left_hip', 'right_hip', 'left_shoulder', 'right_shoulder',
         'left_elbow', 'right_elbow', 'left_wrist', 'right_wrist']
# Rotation identity bound (brief of 2026-09-24, M1): 1e-3 deg. The measured
# error is about 1e-6 deg or smaller (floating point), so the bound only
# guards against a wrong frame being drawn.
ROTATION_TOL_DEG = 1e-3


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def load(path, name):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def angle(a, b):
    return float(np.degrees(np.arctan2(np.linalg.norm(np.cross(a, b)), np.dot(a, b))))


def rotation_errors(page, q, rec):
    """Angle (deg) between the rotated X axis drawn on the page and its bone,
    from the stored matrices and from an independent SciPy recomputation."""
    upper = q['right_elbow'] - q['right_shoulder']
    fore = q['right_wrist'] - q['right_elbow']
    x = q['right_hip'] - q['left_hip']; x /= np.linalg.norm(x)
    z = np.cross(x, q['right_shoulder'] - q['right_hip']); z /= np.linalg.norm(z)
    root = np.column_stack([x, np.cross(z, x), z])
    a = root.T @ (upper / np.linalg.norm(upper))
    swing = root @ Rotation.from_euler('YZ', [np.arctan2(-a[2], a[0]), np.arcsin(np.clip(a[1], -1, 1))]).as_matrix()
    arm = swing @ Rotation.from_rotvec([np.radians(rec['sh_twist']), 0, 0]).as_matrix()
    elbow = arm @ Rotation.from_euler('YZ', np.radians([rec['el_y'], rec['el_z']])).as_matrix()
    if page == 14:
        pairs = {'stored': (rec['swing_basis'], upper), 'independent': (swing, upper)}
    elif page == 15:
        pairs = {'stored': (rec['upper_arm_basis'], upper), 'independent': (arm, upper)}
    else:
        pairs = {'stored': (rec['elbow_basis'], fore), 'independent': (elbow, fore)}
    out = {k: angle(np.asarray(m)[:, 0], v) for k, (m, v) in pairs.items()}
    if page == 15:
        out['shared_x'] = angle(np.asarray(rec['swing_basis'])[:, 0], np.asarray(rec['upper_arm_basis'])[:, 0])
    return out, {'root': root, 'swing': swing, 'arm': arm, 'elbow': elbow}


def main():
    checks = []
    pages = []

    def check(name, condition, details=None):
        checks.append({'name': name, 'pass': bool(condition), 'details': details})

    producer = load(PRODUCER, 'four_producer_for_checks')
    for page in range(13, 17):
        spec = producer.PAGES[page]
        p = producer.paths(page)
        derived, extraction = p['derived'], p['extraction']
        check(f'p{page} derived folder is unified_four', derived == HERE / 'unified_four' / f'p{page:02d}')
        data = json.loads((derived / 'kinematic_source.json').read_text())
        inference = json.loads((extraction / 'inference_frame_map.json').read_text())
        filtered = pd.read_csv(p['filtered']).set_index('frame')
        raw = pd.read_csv(p['raw']).set_index('frame')
        csv = pd.read_csv(derived / 'derived_kinematics.csv').set_index('frame')
        intr = json.loads(p['raw'].with_suffix('.meta.json').read_text())['color_intrinsics']
        check(f'p{page} intrinsics bound to raw metadata', data['intrinsics'] == intr)
        check(f'p{page} full inference count', inference['frames'] == len(raw) == len(inference['records']))
        ids = [r['color_hardware_frame_number'] for r in inference['records']]
        timestamps = [r['color_timestamp_ms'] for r in inference['records']]
        check(f'p{page} unique increasing color IDs', len(set(ids)) == len(ids) and np.all(np.diff(ids) > 0))
        check(f'p{page} increasing color timestamps', np.all(np.diff(timestamps) > 0))
        clock = np.asarray([r['relative_time_s'] for r in inference['records']])
        check(f'p{page} exact inference CSV clock', np.max(np.abs(clock - raw['time_s'].to_numpy())) <= .00000051)
        for key, binding in data['source_files'].items():
            check(f'p{page} bound source {key}', sha(ROOT / binding['path']) == binding['sha256'])
        reference = json.loads((derived / 'source_reference.json').read_text())
        check(f'p{page} whole-bag extraction reference by hash',
              reference['page'] == page and reference['extraction_page'] == spec['extraction_page'] and
              all(sha(ROOT / b['path']) == b['sha256'] for b in reference['bound_files'].values()))
        start, end = data['source_frame_interval']
        check(f'p{page} window as specified', [start, end] == [spec['start'], spec['end']], [start, end])
        expected = [start]*60 + [f for f in range(start, end+1) for _ in range(2)] + [end]*60
        check(f'p{page} one shared delivery clock', expected == data['output_source_frames'])
        check(f'p{page} records cover the interval', set(data['records']) == {str(f) for f in range(start, end+1)})
        allowed = set(spec.get('allowed_raw_rejections', ()))
        max_matrix = max_angle = max_euler = max_projection = max_swing_label = 0.
        rotation = {'stored': 0., 'independent': 0., 'shared_x': 0.}
        rejected_frames = []
        for frame in range(start, end+1):
            row = filtered.loc[frame]
            rec = data['records'][str(frame)]
            src = inference['records'][frame]
            check(f'p{page} f{frame} source RGB record', rec['source_rgb'] == src)
            image = np.asarray(Image.open(src['cached_png']).convert('RGB'))
            check(f'p{page} f{frame} exact inference RGB', hashlib.sha256(image.tobytes()).hexdigest() == src['inference_rgb_sha256'])
            bad = [n for n in NAMES if raw.loc[frame, n+'_src'] != 0]
            if bad:
                rejected_frames.append({'frame': frame, 'landmarks': bad})
            check(f'p{page} f{frame} raw accepted except filter-interpolated allowed landmarks',
                  all(n in allowed and row[n+'_flag'] != 0 for n in bad), bad)
            check(f'p{page} f{frame} source flags', all(raw.loc[frame, n+'_src'] == v for n, v in rec['raw_src'].items()))
            check(f'p{page} f{frame} filter flags', all(row[n+'_flag'] == v for n, v in rec['filter_flags'].items()))
            q = {n: row[[n+'_'+a for a in 'xyz']].to_numpy(float)*[1, -1, 1] for n in NAMES}
            check(f'p{page} f{frame} filtered source points', all(np.array_equal(q[n], rec['points_camera_prime_m'][n]) for n in q))
            errors, m = rotation_errors(page, q, rec) if page != 13 else ({}, rotation_errors(14, q, rec)[1])
            for k, v in errors.items():
                rotation[k] = max(rotation[k], v)
            root, swing = m['root'], m['swing']
            euler = np.degrees([-np.arcsin(np.clip(root[1, 2], -1, 1)),
                                np.arctan2(root[0, 2], root[2, 2]), np.arctan2(root[1, 0], root[1, 1])])
            max_euler = max(max_euler, float(np.max(np.abs((euler - [rec['root_ex'], rec['root_ey'], rec['root_ez']] + 180) % 360 - 180))))
            u = q['right_elbow']-q['right_shoulder']; u /= np.linalg.norm(u)
            a = root.T @ u
            f = q['right_wrist']-q['right_elbow']; f /= np.linalg.norm(f)
            fp = swing.T @ f
            twist_ok = np.linalg.norm(fp[1:]) >= 1e-6
            tau = np.arctan2(-fp[1], fp[2]) if twist_ok else 0.
            arm = swing @ Rotation.from_rotvec([tau, 0, 0]).as_matrix()
            g = arm.T @ f
            values = np.degrees([np.arctan2(-a[2], a[0]), np.arcsin(a[1]), tau,
                                 np.arctan2(-g[2], g[0]), np.arcsin(np.clip(g[1], -1, 1))])
            saved = [rec[k] for k in ('sh_y', 'sh_z', 'sh_twist', 'el_y', 'el_z')]
            max_angle = max(max_angle, float(np.max(np.abs((values-saved+180) % 360-180))))
            elbow = arm @ Rotation.from_euler('YZ', np.radians(values[3:])).as_matrix()
            max_matrix = max(max_matrix, *(float(np.max(np.abs(b-np.asarray(rec[k])))) for b, k in
                                          [(root, 'root_basis'), (swing, 'swing_basis'), (arm, 'upper_arm_basis'),
                                           (elbow, 'elbow_basis')]))
            max_swing_label = max(max_swing_label, abs(angle(root[:, 0], swing[:, 0]) - rec['swing_angle_deg']),
                                  abs(csv.loc[frame, 'swing_angle_deg'] - rec['swing_angle_deg']))
            for key in ('sh_y', 'sh_z', 'sh_twist', 'el_y', 'el_z'):
                if abs(csv.loc[frame, key] - rec[key]) > 1e-9:
                    check(f'p{page} f{frame} derived CSV {key} equals record', False, [csv.loc[frame, key], rec[key]])
            K = np.array([[intr['fx'], 0, intr['ppx']], [0, intr['fy'], intr['ppy']], [0, 0, 1.]])
            camera = np.vstack([q[n] for n in NAMES]) * [1, -1, 1]
            pixel = cv2.projectPoints(camera, np.zeros(3), np.zeros(3), K, np.zeros(5))[0].reshape(-1, 2)
            analytical = np.column_stack([intr['fx']*camera[:, 0]/camera[:, 2]+intr['ppx'],
                                          intr['fy']*camera[:, 1]/camera[:, 2]+intr['ppy']])
            max_projection = max(max_projection, float(np.max(np.abs(pixel-analytical))))
        if page != 13:
            check(f'p{page} rotated X on the bone, stored frames, every frame', rotation['stored'] < ROTATION_TOL_DEG, rotation['stored'])
            check(f'p{page} rotated X on the bone, independent frames, every frame', rotation['independent'] < ROTATION_TOL_DEG, rotation['independent'])
        if page == 15:
            check('p15 swing and arm frames share X, every frame', rotation['shared_x'] < ROTATION_TOL_DEG, rotation['shared_x'])
        check(f'p{page} independent root/swing/arm/elbow matrices', max_matrix < 1e-11, max_matrix)
        check(f'p{page} independent angle reconstruction', max_angle < 1e-9, max_angle)
        check(f'p{page} independent root Euler reconstruction', max_euler < 1e-9, max_euler)
        check(f'p{page} swing angle label equals root-X to swing-X angle and CSV', max_swing_label < 1e-9, max_swing_label)
        check(f'p{page} independent camera projection', max_projection < 1e-9, max_projection)
        selected = json.loads(Path(ROOT / data['source_files']['selected_precondition']['path']).read_text())
        check(f'p{page} unchanged selected tracking criteria', selected['criteria'] == {'min_coverage': .95, 'max_gap_s': .5})
        check(f'p{page} all selected eligibility verdicts', all(selected['verdicts'].values()), selected['verdicts'])
        processing = json.loads((extraction / 'source_manifest.json').read_text())
        full = json.loads((ROOT / processing['tracking_precondition_full']['path']).read_text())
        pages.append({'page': page, 'source_bag': str(p['bag']), 'selected_interval': [start, end],
                      'derived_folder': str(derived.relative_to(ROOT)),
                      'extraction_folder': str(extraction.relative_to(ROOT)),
                      'source_manifest_sha256': sha(derived / 'kinematic_source.json'),
                      'source_reference_sha256': sha(derived / 'source_reference.json'),
                      'processing_manifest_sha256': sha(extraction / 'source_manifest.json'),
                      'inference_map_sha256': sha(extraction / 'inference_frame_map.json'),
                      'full_recording_tracking_exit_code': processing['tracking_precondition_full_exit_code'],
                      'full_recording_tracking_verdicts': full['verdicts'],
                      'selected_window_tracking_verdicts': selected['verdicts'],
                      'selected_window_tracking_landmarks': selected.get('landmarks'),
                      'raw_rejected_frames_in_window': rejected_frames,
                      'allowed_raw_rejections': sorted(allowed),
                      'rotated_x_vs_bone_max_deg': None if page == 13 else {k: v for k, v in rotation.items() if page == 15 or k != 'shared_x'},
                      'model_view': data['model_view'],
                      'independent_max_angle_error_deg': max_angle,
                      'independent_max_matrix_error': max_matrix,
                      'independent_max_reprojection_error_px': max_projection})
    # Negative cases, temporary folders only.
    negative = []
    real_paths = producer.paths
    for page in (13, 14):
        for name in ('raw_metadata', 'model', 'filtered_csv', 'frozen_method'):
            with tempfile.TemporaryDirectory(prefix='unified_four_negative_') as tmp:
                folder = Path(tmp)
                original = real_paths(page)
                imap = json.loads((original['extraction']/'inference_frame_map.json').read_text())
                processing = json.loads((original['extraction']/'source_manifest.json').read_text())
                if name == 'raw_metadata': imap['raw_metadata']['sha256'] = '0'*64
                elif name == 'model': imap['sources']['model']['sha256'] = '0'*64
                elif name == 'filtered_csv': processing['outputs']['filtered']['sha256'] = '0'*64
                else: processing['source_files']['filter']['sha256'] = '0'*64
                (folder/'inference_frame_map.json').write_text(json.dumps(imap))
                (folder/'source_manifest.json').write_text(json.dumps(processing))
                redirected = {**original, 'folder': folder, 'derived': folder, 'extraction': folder}
                producer.paths = lambda page, redirected=redirected: redirected
                rejected = False
                try:
                    producer.prepare.cache_clear(); producer.prepare(page)
                except ValueError:
                    rejected = True
                finally:
                    producer.paths = real_paths
                untouched = not (folder/'derived_kinematics.csv').exists() and not (folder/'kinematic_source.json').exists()
                negative.append({'case': f'p{page} {name}', 'rejected_before_new_provenance': rejected and untouched})
    producer.prepare.cache_clear()
    # A stale reference hash must be refused.
    with tempfile.TemporaryDirectory(prefix='unified_four_negative_') as tmp:
        original = real_paths(15)
        folder = Path(tmp)
        reference = json.loads((original['folder']/'source_reference.json').read_text())
        reference['bound_files']['filtered_csv']['sha256'] = '0'*64
        (folder/'source_reference.json').write_text(json.dumps(reference))
        redirected = {**original, 'folder': folder, 'derived': folder}
        producer.paths = lambda page, redirected=redirected: redirected
        rejected = False
        try:
            producer.prepare.cache_clear(); producer.prepare(15)
        except ValueError:
            rejected = True
        finally:
            producer.paths = real_paths
        negative.append({'case': 'p15 stale source_reference hash', 'rejected_before_new_provenance':
                         rejected and not (folder/'kinematic_source.json').exists()})
    producer.prepare.cache_clear()
    # The rotation assertion must flag a frame drawn 0.01 deg off the bone.
    data = json.loads((real_paths(16)['derived']/'kinematic_source.json').read_text())
    rec = copy.deepcopy(data['records'][str(data['source_frame_interval'][0])])
    rec['elbow_basis'] = (np.asarray(rec['elbow_basis']) @ Rotation.from_euler('Z', .01, degrees=True).as_matrix()).tolist()
    q = {n: np.asarray(v) for n, v in rec['points_camera_prime_m'].items()}
    flagged = rotation_errors(16, q, rec)[0]['stored'] >= ROTATION_TOL_DEG
    negative.append({'case': 'p16 elbow frame turned 0.01 deg off the forearm', 'rejected_before_new_provenance': bool(flagged)})
    correct = json.loads((HERE/'p13/tracking_precondition_full.json').read_text())
    for name, mutate, code in [
            ('stale_stem', lambda r: r.update(stem='wrong'), 0),
            ('changed_threshold', lambda r: r['criteria'].update(min_coverage=.90), 0),
            ('missing_verdict', lambda r: r.pop('verdicts'), 0),
            ('failure_verdict_with_success_exit', lambda r: r['verdicts'].update(torso=False), 0),
            ('success_verdict_with_failure_exit', lambda r: None, 1)]:
        bad = copy.deepcopy(correct); mutate(bad); rejected = False
        try:
            producer.require_tracking_result(bad, real_paths(13)['bag'].stem, code)
        except ValueError:
            rejected = True
        negative.append({'case': 'tracking ' + name, 'rejected_before_new_provenance': rejected})
    for result in negative:
        check('negative '+result['case'], result['rejected_before_new_provenance'])
    report = {'status': 'PASS' if all(c['pass'] for c in checks) else 'FAIL',
              'passed': sum(c['pass'] for c in checks), 'failed': sum(not c['pass'] for c in checks),
              'rotation_tolerance_deg': ROTATION_TOL_DEG,
              'pages': pages, 'negative_cache_and_checker_cases': negative, 'checks': checks,
              'validator': str(Path(__file__).relative_to(ROOT)), 'validator_sha256': sha(__file__),
              'producers': {'bank_axes_kinematics': sha(PRODUCER),
                            'unified_panels': sha(HERE.parent/'anim/unified_panels.py')},
              'scope': 'Numerical/source-clock audit of the four merged qualitative demos, pages 13-16 (unified_four); not external accuracy. Whole-recording tracking verdicts are listed separately from selected-window verdicts.'}
    REPORT.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], report['passed'], 'PASS', report['failed'], 'FAIL')
    if report['failed']:
        for c in checks:
            if not c['pass']:
                print('FAIL', c['name'], c['details'])
        raise SystemExit(1)


if __name__ == '__main__':
    main()

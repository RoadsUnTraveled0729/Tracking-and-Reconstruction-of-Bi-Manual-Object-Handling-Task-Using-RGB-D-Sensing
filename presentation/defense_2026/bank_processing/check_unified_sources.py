#!/usr/bin/env python3
"""Independent source-clock, frame geometry and negative-cache checks, pages 13-20.

Sibling of check_bank_sources.py for the unified-layout revision. Pages 13-16
are produced by anim/bank_axes_kinematics.py (derived files in pNN/), pages
17-20 by the version-2 anim/bank_kinematics.py (derived files in
unified_v2/pNN/). The producers are imported only for fail-closed negative
tests. check_bank_sources.py and its report are left unchanged.
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
AXES = HERE.parent / 'anim/bank_axes_kinematics.py'
BANK = HERE.parent / 'anim/bank_kinematics.py'
REPORT = HERE / 'UNIFIED_SOURCE_CHECK.json'
NAMES = ['left_hip', 'right_hip', 'left_shoulder', 'right_shoulder',
         'left_elbow', 'right_elbow', 'left_wrist', 'right_wrist']


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


def main():
    checks = []
    pages = []

    def check(name, condition, details=None):
        checks.append({'name': name, 'pass': bool(condition), 'details': details})

    axes, bank = load(AXES, 'axes_producer_for_checks'), load(BANK, 'bank_producer_for_checks')
    for page in range(13, 21):
        producer = axes if page <= 16 else bank
        p = producer.paths(page)
        derived = p['derived']
        extraction = p.get('extraction', p['folder'])
        data = json.loads((derived / 'kinematic_source.json').read_text())
        inference = json.loads((extraction / 'inference_frame_map.json').read_text())
        filtered = pd.read_csv(p['filtered']).set_index('frame')
        raw = pd.read_csv(p['raw']).set_index('frame')
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
        if (p['folder'] / 'source_reference.json').exists() and page <= 16:
            reference = json.loads((p['folder'] / 'source_reference.json').read_text())
            check(f'p{page} shared extraction reference',
                  reference['page'] == page and all(sha(ROOT / b['path']) == b['sha256']
                                                    for b in reference['bound_files'].values()))
        start, end = data['source_frame_interval']
        expected = [start]*60 + [f for f in range(start, end+1) for _ in range(2)] + [end]*60
        check(f'p{page} one shared delivery clock', expected == data['output_source_frames'])
        check(f'p{page} records cover the interval', set(data['records']) == {str(f) for f in range(start, end+1)})
        max_matrix = max_projection = max_angle = max_euler = max_yaw = 0.
        for frame in range(start, end+1):
            row = filtered.loc[frame]
            rec = data['records'][str(frame)]
            src = inference['records'][frame]
            check(f'p{page} f{frame} source RGB record', rec['source_rgb'] == src)
            image = np.asarray(Image.open(src['cached_png']).convert('RGB'))
            check(f'p{page} f{frame} exact inference RGB', hashlib.sha256(image.tobytes()).hexdigest() == src['inference_rgb_sha256'])
            check(f'p{page} f{frame} all eight raw accepted', all(raw.loc[frame, n+'_src'] == 0 for n in NAMES))
            check(f'p{page} f{frame} source flags', all(raw.loc[frame, n+'_src'] == v for n, v in rec['raw_src'].items()))
            check(f'p{page} f{frame} filter flags', all(row[n+'_flag'] == v for n, v in rec['filter_flags'].items()))
            q = {n: row[[n+'_'+a for a in 'xyz']].to_numpy(float)*[1, -1, 1] for n in NAMES}
            check(f'p{page} f{frame} filtered source points', all(np.array_equal(q[n], rec['points_camera_prime_m'][n]) for n in q))
            x = q['right_hip']-q['left_hip']; x /= np.linalg.norm(x)
            s = q['right_shoulder']-q['right_hip']
            z = np.cross(x, s); z /= np.linalg.norm(z)
            root = np.column_stack([x, np.cross(z, x), z])
            # Unity ZXY Euler read directly from matrix entries (root_frame.py doc).
            euler = np.degrees([-np.arcsin(np.clip(root[1, 2], -1, 1)),
                                np.arctan2(root[0, 2], root[2, 2]), np.arctan2(root[1, 0], root[1, 1])])
            max_euler = max(max_euler, float(np.max(np.abs((euler - [rec['root_ex'], rec['root_ey'], rec['root_ez']] + 180) % 360 - 180))))
            yaw = np.degrees(np.arctan2(z[0], z[2]))
            max_yaw = max(max_yaw, float(abs((yaw - rec['root_ey'] + 180) % 360 - 180)))
            u = q['right_elbow']-q['right_shoulder']; u /= np.linalg.norm(u)
            a = root.T @ u
            ty, tz = np.arctan2(-a[2], a[0]), np.arcsin(a[1])
            swing = root @ Rotation.from_euler('YZ', [ty, tz]).as_matrix()
            f = q['right_wrist']-q['right_elbow']; f /= np.linalg.norm(f)
            fp = swing.T @ f
            perp = np.linalg.norm(fp[1:])
            twist_ok = perp >= 1e-6
            tau = np.arctan2(-fp[1], fp[2]) if twist_ok else 0.
            arm = swing @ Rotation.from_rotvec([tau, 0, 0]).as_matrix()
            g = arm.T @ f
            ey, ez = np.arctan2(-g[2], g[0]), np.arcsin(np.clip(g[1], -1, 1))
            values = np.degrees([ty, tz, tau, ey, ez])
            saved = [rec[k] for k in ('sh_y', 'sh_z', 'sh_twist', 'el_y', 'el_z')]
            max_angle = max(max_angle, float(np.max(np.abs((values-saved+180) % 360-180))))
            max_matrix = max(max_matrix, *(float(np.max(np.abs(b-np.asarray(rec[k])))) for b, k in
                                          [(root, 'root_basis'), (swing, 'swing_basis'), (arm, 'upper_arm_basis')]))
            check(f'p{page} f{frame} actual observability', twist_ok == rec['twist_ok'] and abs(perp-rec['perpendicular_fraction']) < 1e-12)
            K = np.array([[intr['fx'], 0, intr['ppx']], [0, intr['fy'], intr['ppy']], [0, 0, 1.]])
            camera = np.vstack([q[n] for n in NAMES]) * [1, -1, 1]
            pixel = cv2.projectPoints(camera, np.zeros(3), np.zeros(3), K, np.zeros(5))[0].reshape(-1, 2)
            analytical = np.column_stack([intr['fx']*camera[:, 0]/camera[:, 2]+intr['ppx'],
                                          intr['fy']*camera[:, 1]/camera[:, 2]+intr['ppy']])
            max_projection = max(max_projection, float(np.max(np.abs(pixel-analytical))))
        check(f'p{page} independent root/swing/arm matrices', max_matrix < 1e-11, max_matrix)
        check(f'p{page} independent angle reconstruction', max_angle < 1e-9, max_angle)
        check(f'p{page} independent root Euler reconstruction', max_euler < 1e-9, max_euler)
        check(f'p{page} top-view Z-hat angle equals root y', max_yaw < 1e-9, max_yaw)
        check(f'p{page} independent camera projection', max_projection < 1e-9, max_projection)
        selected = json.loads(Path(ROOT / data['source_files']['selected_precondition']['path']).read_text())
        check(f'p{page} unchanged selected tracking criteria', selected['criteria'] == {'min_coverage': .95, 'max_gap_s': .5})
        check(f'p{page} all selected eligibility verdicts', all(selected['verdicts'].values()))
        processing = json.loads((extraction / 'source_manifest.json').read_text())
        full = json.loads((ROOT / processing['tracking_precondition_full']['path']).read_text())
        pages.append({'page': page, 'selected_interval': [start, end],
                      'derived_folder': str(derived.relative_to(ROOT)),
                      'extraction_folder': str(extraction.relative_to(ROOT)),
                      'source_manifest_sha256': sha(derived / 'kinematic_source.json'),
                      'processing_manifest_sha256': sha(extraction / 'source_manifest.json'),
                      'inference_map_sha256': sha(extraction / 'inference_frame_map.json'),
                      'full_recording_tracking_exit_code': processing['tracking_precondition_full_exit_code'],
                      'full_recording_tracking_verdicts': full['verdicts'],
                      'selected_window_tracking_verdicts': selected['verdicts'],
                      'model_view': data['model_view'],
                      'independent_max_angle_error_deg': max_angle,
                      'independent_max_matrix_error': max_matrix,
                      'independent_max_reprojection_error_px': max_projection})
    # Fail-closed negative cases, run in temporary folders only.
    negative = []
    for label, producer, page in [('axes', axes, 13), ('axes_reference', axes, 16), ('bank_v2', bank, 17)]:
        real_paths = producer.paths
        for name in ('raw_metadata', 'model', 'filtered_csv', 'frozen_method'):
            with tempfile.TemporaryDirectory(prefix='unified_negative_') as tmp:
                folder = Path(tmp)
                original = real_paths(page)
                source = original.get('extraction', original['folder'])
                imap = json.loads((source/'inference_frame_map.json').read_text())
                processing = json.loads((source/'source_manifest.json').read_text())
                if name == 'raw_metadata': imap['raw_metadata']['sha256'] = '0'*64
                elif name == 'model': imap['sources']['model']['sha256'] = '0'*64
                elif name == 'filtered_csv': processing['outputs']['filtered']['sha256'] = '0'*64
                else: processing['source_files']['filter']['sha256'] = '0'*64
                (folder/'inference_frame_map.json').write_text(json.dumps(imap))
                (folder/'source_manifest.json').write_text(json.dumps(processing))
                if (original['folder']/'source_reference.json').exists() and label != 'bank_v2':
                    (folder/'source_reference.json').write_text((original['folder']/'source_reference.json').read_text())
                redirected = {**original, 'folder': folder, 'derived': folder}
                if 'extraction' in original:
                    redirected['extraction'] = folder
                producer.paths = lambda page, redirected=redirected: redirected
                rejected = False
                try:
                    producer.prepare.cache_clear(); producer.prepare(page)
                except ValueError:
                    rejected = True
                finally:
                    producer.paths = real_paths
                untouched = not (folder/'derived_kinematics.csv').exists() and not (folder/'kinematic_source.json').exists()
                negative.append({'case': f'{label} {name}', 'rejected_before_new_provenance': rejected and untouched})
        producer.prepare.cache_clear()
    correct = json.loads((HERE/'p13/tracking_precondition_full.json').read_text())
    for name, mutate, code in [
            ('stale_stem', lambda r: r.update(stem='wrong'), 0),
            ('changed_threshold', lambda r: r['criteria'].update(min_coverage=.90), 0),
            ('missing_verdict', lambda r: r.pop('verdicts'), 0),
            ('failure_verdict_with_success_exit', lambda r: r['verdicts'].update(torso=False), 0),
            ('success_verdict_with_failure_exit', lambda r: None, 1)]:
        bad = copy.deepcopy(correct); mutate(bad); rejected = False
        try:
            axes.require_tracking_result(bad, axes.paths(13)['bag'].stem, code)
        except ValueError:
            rejected = True
        negative.append({'case': 'tracking ' + name, 'rejected_before_new_provenance': rejected})
    for result in negative:
        check('negative '+result['case'], result['rejected_before_new_provenance'])
    report = {'status': 'PASS' if all(c['pass'] for c in checks) else 'FAIL',
              'passed': sum(c['pass'] for c in checks), 'failed': sum(not c['pass'] for c in checks),
              'pages': pages, 'negative_cache_and_checker_cases': negative, 'checks': checks,
              'validator': str(Path(__file__).relative_to(ROOT)), 'validator_sha256': sha(__file__),
              'producers': {'bank_axes_kinematics': sha(AXES), 'bank_kinematics_v2': sha(BANK),
                            'unified_panels': sha(HERE.parent/'anim/unified_panels.py')},
              'scope': 'Numerical/source-clock audit of new qualitative demos, pages 13-20; not external accuracy. Whole-recording tracking verdicts are listed separately from selected-window verdicts.'}
    REPORT.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], report['passed'], 'PASS', report['failed'], 'FAIL')
    if report['failed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()

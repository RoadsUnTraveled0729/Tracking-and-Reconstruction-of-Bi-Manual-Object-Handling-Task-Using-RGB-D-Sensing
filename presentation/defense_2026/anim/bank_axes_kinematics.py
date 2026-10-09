#!/usr/bin/env python3
"""The four merged kinematics pages 13-16 (unified_four collection).

2026-09-24 round 2 (plan virtual-wiggling-globe.md, M1): page 13 torso frame,
page 14 shoulder swing, page 15 shoulder twist, page 16 elbow. Each page reads
an existing whole-bag exact-inference extraction by reference, bound by hash
in bank_processing/unified_four/pNN/source_reference.json; MediaPipe is not
re-run. Page 13 reads bank_processing/p13, page 14 p17 (180042 arm raise),
page 15 p18 (right_arm_test), page 16 p19 (right_elbow). The model panel draws
the parent frame dim and the rotated frame bright at the page's joint
(unified_panels.compose_four). Derived files go to
bank_processing/unified_four/pNN and films to committee_materials/unified_four.
The earlier version of this producer (pages 13-16 of bank_axes_revision) is
in git history; its collection and derived folders are left unchanged.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from functools import lru_cache

sys.dont_write_bytecode = True
import cv2
import numpy as np
import pandas as pd
from PIL import Image
from scipy.spatial.transform import Rotation
from coordinate_axes import AXIS_COLORS, CAMERA_TO_CAMERA_PRIME as F, make_pinhole_projector
import unified_panels as U

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
# Recordings bank, moved into the repository on 2026-10-06 from
# /home/luo/Desktop/ENSC498/recordings (that old path is now a symlink here).
BANK = ROOT / 'recordings'
WORK = HERE / 'bank_processing'
OUT = HERE / 'committee_materials/unified_four'
DERIVED = WORK / 'unified_four'
PYTHON = Path('/home/luo/anaconda3/bin/python')
MODEL = ROOT / 'v1/mediapipe/models/pose_landmarker_heavy.task'
OUTSTRETCHED = 'ENSC498_arms_outstretched_pose_test_arm_test.bag'
ARM_RAISE = 'ENSC498_right_arm_raise_cube_untouched_test_20260121_180042.bag'
TWIST = 'ENSC498_right_arm_landmark_test_right_arm_test.bag'
ELBOW = 'ENSC498_right_elbow_bend_test_right_elbow.bag'
# Window choices: DECISIONS.md D-088 (13 unchanged T-pose turn; 14 straight-arm
# 180042 3-109; 15 real twist 505-725; 16 unchanged elbow bend).
# allowed_raw_rejections: landmarks whose raw sample may be rejected inside
# the window when the frozen filter interpolated it (flag != 0); D-089.
TORSO_START, TORSO_END = 780, 885
PAGES = {
    13: {'bag': OUTSTRETCHED, 'extraction_page': 13,
         'stem': 'p13-Torso_Frame_From_Standing_T_Pose', 'start': TORSO_START, 'end': TORSO_END},
    14: {'bag': ARM_RAISE, 'extraction_page': 17,
         'stem': 'p14-Shoulder_Swing_Rotates_Root_Frame_Onto_Upper_Arm', 'start': 3, 'end': 109,
         'allowed_raw_rejections': ('right_wrist',)},
    15: {'bag': TWIST, 'extraction_page': 18,
         'stem': 'p15-Shoulder_Twist_About_Upper_Arm_Axis', 'start': 505, 'end': 725},
    16: {'bag': ELBOW, 'extraction_page': 19,
         'stem': 'p16-Elbow_Rotation_Onto_Forearm', 'start': 180, 'end': 540},
}
W, H, FPS = U.W, U.H, U.FPS
AXIS_LENGTH_M = .075
NAMES = U.NAMES
NEEDED = ['left_hip', 'right_hip', 'left_shoulder', 'right_shoulder',
          'right_elbow', 'right_wrist']
ADAPTER = WORK / 'extract_logged_v2.py'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def rel(path):
    path = Path(path).resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='ascii')


def paths(page):
    """Own derived folder plus the (possibly shared) extraction folder."""
    folder = DERIVED / f'p{page:02d}'
    source = WORK / f'p{PAGES[page]["extraction_page"]:02d}'
    return {'folder': folder, 'derived': folder, 'extraction': source,
            'raw': source / 'landmarks_raw.csv',
            'filtered': source / 'landmarks_filtered.csv',
            'bag': BANK / PAGES[page]['bag']}


def require_binding(binding):
    path = Path(binding['path'])
    path = path if path.is_absolute() else ROOT / path
    if not path.is_file() or sha(path) != binding['sha256']:
        raise ValueError(f'Stale or missing bound source: {path}')
    return path


def require_tracking_result(report, stem, exit_code):
    if report.get('stem') != stem:
        raise ValueError('Tracking checker stem does not match this recording.')
    if report.get('criteria') != {'min_coverage': .95, 'max_gap_s': .5}:
        raise ValueError('Tracking checker criteria changed.')
    verdicts = report.get('verdicts', {})
    keys = {'torso', 'left_hand_windows', 'right_hand_windows'}
    if set(verdicts) != keys or any(type(v) is not bool for v in verdicts.values()):
        raise ValueError('Tracking checker did not produce a valid verdict.')
    if set(report.get('landmarks', {})) != set(NAMES):
        raise ValueError('Tracking checker did not grade every required landmark.')
    for result in report['landmarks'].values():
        if not {'coverage', 'longest_gap_s', 'pass'} <= set(result):
            raise ValueError('Incomplete tracking landmark result.')
        if type(result['pass']) is not bool or not np.isfinite([result['coverage'], result['longest_gap_s']]).all():
            raise ValueError('Malformed tracking landmark result.')
    expected = 0 if all(verdicts.values()) else 1
    if exit_code != expected:
        raise ValueError('Tracking checker process exit and actual verdict disagree.')


def validate_ready(page):
    p = paths(page)
    inference = json.loads((p['extraction'] / 'inference_frame_map.json').read_text())
    processing = json.loads((p['extraction'] / 'source_manifest.json').read_text())
    if inference.get('status') != 'COMPLETE' or inference.get('page') != PAGES[page]['extraction_page']:
        raise ValueError('Incomplete or wrong inference-frame manifest.')
    for binding in inference['sources'].values():
        require_binding(binding)
    require_binding(inference['raw_csv'])
    require_binding(inference['raw_metadata'])
    for binding in processing['source_files'].values():
        require_binding(binding)
    for binding in processing['outputs'].values():
        require_binding(binding)
    require_binding(processing['inference_frame_map'])
    result_path = require_binding(processing['tracking_precondition_full'])
    require_tracking_result(json.loads(result_path.read_text()), p['bag'].stem,
                            processing['tracking_precondition_full_exit_code'])
    if p['folder'] != p['extraction']:
        reference = json.loads((p['folder'] / 'source_reference.json').read_text())
        if reference.get('page') != page or reference.get('extraction_page') != PAGES[page]['extraction_page']:
            raise ValueError('Source reference names the wrong page.')
        for binding in reference['bound_files'].values():
            require_binding(binding)
    return inference, processing


def run_logged(command, log, acceptable=(0,)):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    with Path(log).open('w') as f:
        proc = subprocess.run([str(x) for x in command], cwd=ROOT, env=env,
                              stdout=f, stderr=subprocess.STDOUT)
    if proc.returncode not in acceptable:
        raise RuntimeError(f'Command failed ({proc.returncode}); see {log}')
    return proc.returncode


def write_reference(page):
    """Bind a shared extraction by hash instead of re-running MediaPipe."""
    p = paths(page)
    p['folder'].mkdir(parents=True, exist_ok=True)
    files = {'inference_frame_map': p['extraction'] / 'inference_frame_map.json',
             'source_manifest': p['extraction'] / 'source_manifest.json',
             'raw_csv': p['raw'], 'raw_meta': p['raw'].with_suffix('.meta.json'),
             'filtered_csv': p['filtered'], 'filtered_meta': p['filtered'].with_suffix('.meta.json'),
             'tracking_precondition_full': p['extraction'] / 'tracking_precondition_full.json'}
    write_json(p['folder'] / 'source_reference.json', {
        'page': page, 'extraction_page': PAGES[page]['extraction_page'],
        'source_bag': str(p['bag']),
        'bound_files': {k: {'path': rel(v), 'sha256': sha(v)} for k, v in files.items()},
        'note': 'This page reuses an existing exact-inference extraction by reference; MediaPipe was not re-run and the referenced files are not rewritten.'})
    print(f'REFERENCED p{page:02d} -> p{PAGES[page]["extraction_page"]:02d}', flush=True)


def extract(page):
    if paths(page)['folder'] != paths(page)['extraction']:
        write_reference(page)
        return
    p = paths(page)
    p['folder'].mkdir(parents=True, exist_ok=True)
    extractor = ROOT / 'v1/mediapipe/extract_landmarks_to_csv.py'
    filt = ROOT / 'v1/mediapipe/filter_landmarks.py'
    command = [PYTHON, ADAPTER, '--page', str(page), '--bag', p['bag'],
               '--out', p['raw'], '--model', MODEL]
    completed = p['folder'] / 'inference_frame_map.json'
    reuse = False
    if completed.exists():
        old = json.loads(completed.read_text())
        if old['status'] != 'COMPLETE' or old['page'] != page:
            raise ValueError('Cannot reuse an incomplete inference manifest.')
        for binding in old['sources'].values():
            require_binding(binding)
        require_binding(old['raw_csv'])
        require_binding(old['raw_metadata'])
        df = pd.read_csv(p['raw'])
        if len(df) != old['frames'] or df['frame'].tolist() != [r['frame'] for r in old['records']]:
            raise ValueError('Cached inference frame count/IDs changed.')
        if np.max(np.abs(df['time_s'].to_numpy() - [r['relative_time_s'] for r in old['records']])) > .00000051:
            raise ValueError('Cached inference clock changed.')
        reuse = True
    if not reuse:
        if p['raw'].exists():
            raise RuntimeError('Refusing to replace an existing uninstrumented extraction.')
        run_logged(command, p['folder'] / 'extraction.log')
    filter_command = [PYTHON, filt, '--csv', p['raw'], '--out', p['filtered'],
                      '--hampel-window', '7', '--hampel-k', '3',
                      '--hampel-floor', '.02', '--max-gap', '5', '--edge-fill', '0',
                      '--smooth', 'butter', '--cutoff-hz', '3', '--butter-order', '4']
    run_logged(filter_command, p['folder'] / 'filter.log')
    checker = ROOT / 'eval/inspect/check_tracking_precondition.py'
    result_path = p['folder'] / 'tracking_precondition_full.json'
    check_command = [PYTHON, checker, '--stem', p['bag'].stem, '--csv', p['raw'],
                     '--json-out', result_path]
    if result_path.exists():
        result_path.unlink()
    code = run_logged(check_command, p['folder'] / 'tracking_precondition_full.log', (0, 1))
    if not result_path.exists():
        raise RuntimeError('Tracking checker exited without a fresh verdict JSON.')
    require_tracking_result(json.loads(result_path.read_text()), p['bag'].stem, code)
    source_files = {'bag': p['bag'], 'extractor': extractor, 'filter': filt,
                    'logging_adapter': ADAPTER, 'model': MODEL, 'tracking_checker': checker}
    manifest = {
        'page': page, 'source_bag': str(p['bag']),
        'source_files': {k: {'path': rel(v), 'sha256': sha(v)} for k, v in source_files.items()},
        'commands': {'extract': [str(x) for x in command],
                     'filter': [str(x) for x in filter_command],
                     'tracking_precondition_full': [str(x) for x in check_command]},
        'tracking_precondition_full_exit_code': code,
        'tracking_precondition_full': {'path': rel(result_path), 'sha256': sha(result_path)},
        'inference_frame_map': {'path': rel(completed), 'sha256': sha(completed)},
        'outputs': {k: {'path': rel(v), 'sha256': sha(v)} for k, v in p.items()
                    if k in ('raw', 'filtered')},
        'legacy_pose_json_used': False,
        'qualification': 'New offline thesis-method processing; not a new accuracy experiment.'}
    for name in ('raw', 'filtered'):
        meta = p[name].with_suffix('.meta.json')
        manifest['outputs'][name + '_meta'] = {'path': rel(meta), 'sha256': sha(meta)}
    write_json(p['folder'] / 'source_manifest.json', manifest)
    print(f'EXTRACTED p{page:02d}; tracking checker exit {code}', flush=True)


@lru_cache(maxsize=4)
def prepare(page):
    sys.path.insert(0, str(ROOT / 'v1/kinematics'))
    from root_frame import build_root_frame, euler_unity_zxy, recompose_zxy
    from shoulder import solve_right_arm, _ry, _rz, recompose_shoulder, TWIST_EPS
    p = paths(page)
    inference, processing = validate_ready(page)
    raw = pd.read_csv(p['raw']).set_index('frame')
    filtered = pd.read_csv(p['filtered']).set_index('frame')
    inference_path = p['extraction'] / 'inference_frame_map.json'
    assert inference['status'] == 'COMPLETE' and len(raw) == inference['frames']
    assert inference['raw_csv']['sha256'] == sha(p['raw'])
    intr = json.loads(p['raw'].with_suffix('.meta.json').read_text())['color_intrinsics']
    assert np.max(np.abs(intr['coeffs'])) == 0, 'This pinhole renderer requires the recorded zero-distortion stream.'
    K = np.array([[intr['fx'], 0, intr['ppx']], [0, intr['fy'], intr['ppy']], [0, 0, 1.]])
    camera = make_pinhole_projector(intr, source_to_camera=F)
    records = {}
    derived = []
    maxima = dict(root_independent=0., swing_independent=0., arm_independent=0.,
                  root_euler_roundtrip=0., direction=0., projection_px=0., proper_basis=0.,
                  top_view_yaw=0., elbow_direction=0.)
    source_start, source_end = PAGES[page]['start'], PAGES[page]['end']
    for frame, r in filtered.iterrows():
        points = {n: r[[n + '_' + a for a in 'xyz']].to_numpy(float) * [1, -1, 1]
                  for n in NAMES}
        finite = all(np.isfinite(points[n]).all() for n in NEEDED)
        base = {'frame': int(frame), 'time_s': float(r['time_s']),
                'geometry_available': finite,
                'raw_required_valid': bool((raw.loc[frame, [n + '_src' for n in NEEDED]] == 0).all()),
                'raw_all_eight_valid': bool((raw.loc[frame, [n + '_src' for n in NAMES]] == 0).all()),
                'required_repaired_points': int((r[[n + '_flag' for n in NEEDED]] != 0).sum())}
        if not finite:
            derived.append(base)
            continue
        hip = points['right_hip'] - points['left_hip']
        spine = points['right_shoulder'] - points['right_hip']
        if np.linalg.norm(hip) == 0 or np.linalg.norm(np.cross(hip, spine)) == 0:
            base['geometry_available'] = False
            derived.append(base)
            continue
        root = build_root_frame(points['left_hip'], points['right_hip'], points['right_shoulder'])
        sh, el, twist_ok = solve_right_arm(points['right_shoulder'], points['right_elbow'],
                                          points['right_wrist'], root)
        swing = root @ _ry(np.radians(sh[0])) @ _rz(np.radians(sh[1]))
        arm = root @ recompose_shoulder(sh)
        # Elbow-rotated frame: the arm frame turned by the elbow angles; its X
        # axis is the forearm direction (Eq. 3.24 composition, shoulder.py).
        elbow = arm @ _ry(np.radians(el[0])) @ _rz(np.radians(el[1]))
        upper = points['right_elbow'] - points['right_shoulder']
        fore = points['right_wrist'] - points['right_elbow']
        fp = swing.T @ fore
        fraction = float(np.linalg.norm(fp[1:]) / np.linalg.norm(fore))
        root_deg = euler_unity_zxy(root)
        base.update(dict(zip(['root_ex', 'root_ey', 'root_ez'], root_deg)))
        base.update(dict(zip(['sh_y', 'sh_z', 'sh_twist', 'el_y', 'el_z'], np.r_[sh, el])))
        base.update({'swing_angle_deg': U.angle_deg(root[:, 0], swing[:, 0]),
                     'perpendicular_fraction': fraction, 'twist_ok': bool(twist_ok),
                     'upper_length_m': float(np.linalg.norm(upper)),
                     'forearm_length_m': float(np.linalg.norm(fore))})
        derived.append(base)
        if not source_start <= frame <= source_end:
            continue
        allowed = PAGES[page].get('allowed_raw_rejections', ())
        rejected = [n for n in NAMES if raw.loc[frame, n + '_src'] != 0]
        assert all(n in allowed and r[n + '_flag'] != 0 for n in rejected), \
            f'p{page} frame {frame}: raw landmark rejected {rejected}'
        item = inference['records'][int(frame)]
        assert item['frame'] == frame and abs(item['relative_time_s'] - r['time_s']) < .00000051
        photo = Image.open(item['cached_png']).convert('RGB')
        assert sha(item['cached_png']) == item['cached_png_sha256']
        assert hashlib.sha256(np.asarray(photo).tobytes()).hexdigest() == item['inference_rgb_sha256']
        # Independent vector algebra and SciPy rotations check the imported
        # closed-form solver, without the legacy pose JSON outputs.
        x = hip / np.linalg.norm(hip)
        z = np.cross(x, spine); z /= np.linalg.norm(z)
        y = np.cross(z, x)
        independent_root = np.column_stack([x, y, z])
        a = independent_root.T @ (upper / np.linalg.norm(upper))
        ty, tz = np.arctan2(-a[2], a[0]), np.arcsin(np.clip(a[1], -1, 1))
        independent_swing = independent_root @ Rotation.from_euler('YZ', [ty, tz]).as_matrix()
        local_fore = independent_swing.T @ fore
        tau = np.arctan2(-local_fore[1], local_fore[2]) if fraction >= TWIST_EPS else 0.
        independent_arm = independent_swing @ Rotation.from_rotvec([tau, 0, 0]).as_matrix()
        maxima['root_independent'] = max(maxima['root_independent'], float(np.max(np.abs(root - independent_root))))
        maxima['swing_independent'] = max(maxima['swing_independent'], float(np.max(np.abs(swing - independent_swing))))
        maxima['arm_independent'] = max(maxima['arm_independent'], float(np.max(np.abs(arm - independent_arm))))
        maxima['root_euler_roundtrip'] = max(maxima['root_euler_roundtrip'], float(np.max(np.abs(root - recompose_zxy(root_deg)))))
        maxima['direction'] = max(maxima['direction'], float(np.linalg.norm(arm[:, 0] - upper / np.linalg.norm(upper))))
        maxima['elbow_direction'] = max(maxima['elbow_direction'], float(np.linalg.norm(elbow[:, 0] - fore / np.linalg.norm(fore))))
        # The page 15 arc: top-view angle of Z-hat from +z equals root y.
        yaw = np.degrees(np.arctan2(z[0], z[2]))
        maxima['top_view_yaw'] = max(maxima['top_view_yaw'], float(abs((yaw - root_deg[1] + 180) % 360 - 180)))
        origin, basis = points['right_hip'], root
        test = np.vstack([origin, origin + AXIS_LENGTH_M * basis.T])
        independent_px = cv2.projectPoints(test @ F.T, np.zeros(3), np.zeros(3), K, np.zeros(5))[0].reshape(-1, 2)
        maxima['projection_px'] = max(maxima['projection_px'], float(np.max(np.abs(camera(test) - independent_px))))
        maxima['proper_basis'] = max(maxima['proper_basis'], abs(float(np.linalg.det(root)) - 1), float(np.max(np.abs(root.T @ root - np.eye(3)))))
        records[int(frame)] = {**base,
             'points_camera_prime_m': {k: v.tolist() for k, v in points.items()},
             'root_basis': root.tolist(), 'swing_basis': swing.tolist(), 'upper_arm_basis': arm.tolist(),
             'elbow_basis': elbow.tolist(),
             'source_rgb': item,
             'raw_src': {n: int(raw.loc[frame, n + '_src']) for n in NAMES},
             'filter_flags': {n: int(r[n + '_flag']) for n in NAMES}}
    assert len(records) == source_end - source_start + 1
    assert max(maxima.values()) < 1e-9, maxima
    p['derived'].mkdir(parents=True, exist_ok=True)
    pd.DataFrame(derived).to_csv(p['derived'] / 'derived_kinematics.csv', index=False, float_format='%.12g')
    selected_raw = p['derived'] / 'selected_landmarks_raw.csv'
    raw.loc[source_start:source_end].reset_index().to_csv(selected_raw, index=False, float_format='%.6f')
    command = [PYTHON, ROOT / 'eval/inspect/check_tracking_precondition.py', '--stem', p['bag'].stem,
               '--csv', selected_raw, '--json-out', p['derived'] / 'tracking_precondition_selected.json']
    run_logged(command, p['derived'] / 'tracking_precondition_selected.log')
    model_view = U.fit_model_view(page, records, intr)
    mapping = [source_start] * 60 + [i for i in records for _ in range(2)] + [source_end] * 60
    source_files = {'raw_csv': p['raw'], 'filtered_csv': p['filtered'],
                    'raw_meta': p['raw'].with_suffix('.meta.json'),
                    'filter_meta': p['filtered'].with_suffix('.meta.json'),
                    'inference_frame_map': inference_path,
                    'root_formula': ROOT / 'v1/kinematics/root_frame.py',
                    'arm_formula': ROOT / 'v1/kinematics/shoulder.py',
                    'selected_precondition': p['derived'] / 'tracking_precondition_selected.json'}
    if p['folder'] != p['extraction']:
        source_files['source_reference'] = p['folder'] / 'source_reference.json'
    data = {'page': page, 'kind': 'unified_four_kinematics', 'lesson': U.KINDS[page],
            'allowed_raw_rejections': list(PAGES[page].get('allowed_raw_rejections', ())),
            'records': records, 'output_source_frames': mapping, 'intrinsics': intr,
            'source_frame_interval': [source_start, source_end],
            'source_files': {k: {'path': rel(v), 'sha256': sha(v)} for k, v in source_files.items()},
            'processing_manifest': rel(p['extraction'] / 'source_manifest.json'),
            'processing_manifest_sha256': sha(p['extraction'] / 'source_manifest.json'),
            'numeric_checks': maxima, 'twist_eps': TWIST_EPS,
            'model_view': model_view,
            'qualification': 'New offline filtered-input geometric model; no Unity rig, external accuracy result, manual landmark correction, or observed wrist orientation.'}
    write_json(p['derived'] / 'kinematic_source.json', data)
    return data


def render(page, output_index, audit=False):
    data = prepare(page)
    frame = data['output_source_frames'][output_index]
    row = data['records'][frame]
    photo = Image.open(row['source_rgb']['cached_png']).convert('RGB')
    im, record = U.compose(page, frame, row, data['intrinsics'], data['model_view'], photo)
    assert record['congruence_max_abs_source_px'] < 1e-9
    return (im, record) if audit else im


def build(page, preview=False):
    data = prepare(page)
    for folder in ('videos', 'posters', 'review', 'provenance'):
        (OUT / folder).mkdir(parents=True, exist_ok=True)
    stem = PAGES[page]['stem']
    mapping = data['output_source_frames']
    indices = sorted(set([0, 60, len(mapping)//4, len(mapping)//2, 3*len(mapping)//4, len(mapping)-61, len(mapping)-1]))
    for i in indices:
        render(page, i).save(OUT / 'review' / f'{stem}_frame{i:04d}.png')
    poster = OUT / 'posters' / f'{stem}.png'
    render(page, len(mapping)//2).save(poster)
    if preview:
        print(f'PREVIEW p{page:02d}: {rel(poster)}', flush=True)
        return
    movie = OUT / 'videos' / f'{stem}.mp4'
    command = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
               '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264',
               '-preset', 'slow', '-crf', str(CRF), '-threads', '2', '-pix_fmt', 'yuv420p',
               '-movflags', '+faststart', str(movie)]
    proc = subprocess.Popen(command, stdin=subprocess.PIPE)
    previous, pixels = None, None
    for i, frame in enumerate(mapping):
        if frame != previous:
            pixels = render(page, i).tobytes()
            previous = frame
        proc.stdin.write(pixels)
    proc.stdin.close()
    assert proc.wait() == 0
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(movie), '-f', 'null', '-'], check=True)
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames',
        '-select_streams', 'v:0', '-show_entries', 'stream=width,height,nb_read_frames,r_frame_rate,duration',
        '-of', 'json', str(movie)]))['streams'][0]
    assert int(probe['nb_read_frames']) == len(mapping)
    assert [probe['width'], probe['height']] == [W, H]
    audits = [render(page, mapping.index(f), True)[1] for f in data['records']]
    source_manifest = paths(page)['derived'] / 'kinematic_source.json'
    report = {'status': 'PASS', 'page': page, 'filename_stem': stem,
        'kind': 'unified_four_kinematics', 'lesson': U.KINDS[page], 'asset': rel(movie), 'poster': rel(poster),
        'duration_s': len(mapping)/FPS, 'frames': len(mapping), 'fps': FPS, 'dimensions': [W, H],
        'sha256': {'mp4': sha(movie), 'png': sha(poster)},
        'source_manifest': rel(source_manifest), 'source_manifest_sha256': sha(source_manifest),
        'processing_manifest': data['processing_manifest'],
        'processing_manifest_sha256': data['processing_manifest_sha256'],
        'inference_frame_map': data['source_files']['inference_frame_map'],
        'output_source_frames': mapping,
        'source_frame_interval': data['source_frame_interval'],
        'source_bag': str(paths(page)['bag']),
        'source_bag_sha256': json.loads((paths(page)['extraction'] / 'source_manifest.json').read_text())['source_files']['bag']['sha256'],
        'source_kind': 'recorded RGB plus current-thesis filtered-input geometric model',
        'overlay_audits': audits, 'numeric_checks': data['numeric_checks'],
        'decode_check': probe, 'camera_rect': list(U.CAMERA_RECT),
        'source_camera_resampling': 'Exact inference RGB, 640x480 -> 768x576 Lanczos; no crop. Authored axis/chain pixels are audited.',
        'editorial': {'layout': 'unified_panels', 'model_view': data['model_view'],
                      'model_rect': list(U.MODEL_RECT), 'plane_rect': list(U.PLANE_RECT),
                      'axis_lengths_m': {'root': U.ROOT_AXIS_M, 'pair': U.PAIR_AXIS_M,
                                         'rotated_x': 'bone length on pages 14 and 16'},
                      'arc_radius_m': U.ARC_M, 'parent_dim_factor': U.REFERENCE_DIM,
                      'axis_colors': AXIS_COLORS, 'playback_speed': .5,
                      'start_hold_s': 2, 'end_hold_s': 2, 'encoding_crf': CRF, 'encoding_preset': 'slow'},
        'generator': rel(__file__), 'generator_sha256': sha(__file__),
        'layout_renderer': rel(Path(__file__).with_name('unified_panels.py')),
        'layout_renderer_sha256': sha(Path(__file__).with_name('unified_panels.py')),
        'axis_renderer': rel(Path(__file__).with_name('coordinate_axes.py')),
        'axis_renderer_sha256': sha(Path(__file__).with_name('coordinate_axes.py'))}
    write_json(OUT / 'provenance' / f'{stem}.json', report)
    print(f'PASS p{page:02d}: {movie.stat().st_size} bytes, {len(mapping)/FPS:.3f} s', flush=True)


CRF = 19


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--page', type=int, choices=sorted(PAGES))
    parser.add_argument('--extract', action='store_true')
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--build', action='store_true')
    args = parser.parse_args()
    for page in [args.page] if args.page else PAGES:
        if args.extract:
            extract(page)
        if args.preview or args.build:
            build(page, preview=args.preview)


if __name__ == '__main__':
    main()

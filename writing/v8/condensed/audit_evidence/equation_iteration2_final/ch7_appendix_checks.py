"""Independent final read-only equation audit; writes adjacent diagnostics only.

No evaluator or builder is imported. Pinned coordinates, metadata, profiler
output and frozen implementation are read without changing their contents.
Numerical residuals are reported, without redefining experiment tolerances.
Copied from equation_iteration2/ch7_appendix_checks.py so the original first-
delivery audit remains intact. Final Chapter 7 checks include its Scene floor
placement, and the four narrow Appendix presentation corrections are asserted.
"""
import csv
import hashlib
import json
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
from scipy.signal import butter, freqz, savgol_coeffs

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
CONDENSED = REPO / 'writing/v8/condensed'
EVIDENCE = CONDENSED / 'audit_evidence/ch7_restructured'
sources = {}
result = {}


def read(path):
    path = Path(path)
    data = path.read_bytes()
    sources[str(path.relative_to(REPO))] = hashlib.sha256(data).hexdigest()
    return data


def js(path):
    return json.loads(read(path))


def rows(path):
    return list(csv.DictReader(read(path).decode().splitlines()))


def summary(values):
    a = np.asarray(values, dtype=float)
    return dict(n=len(a), median=float(np.percentile(a, 50, method='linear')),
                p95=float(np.percentile(a, 95, method='linear')),
                maximum=float(a.max()))


def error(a, b):
    return {k: abs(a[k] - b[k]) for k in a}


def points(row, prefix):
    return np.array([float(row[prefix + '_' + axis]) for axis in 'xyz'])


def cross_matrix(v):
    x, y, z = v
    return np.array([[0., -z, y], [z, 0., -x], [-y, x, 0.]])


# Read the actual chapter artifacts, without executing their builders.
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'}
inventory = {}
for name in ['Chapter_1_Introduction', 'Chapter_7_Evaluation',
             'Chapter_8_Real_Time_Feasibility', 'Chapter_9_Discussion',
             'Chapter_10_Conclusions_Future_Work', 'FrontMatter_V8_Condensed',
             'Appendices']:
    path = CONDENSED / (name + '.docx')
    read(path)
    with zipfile.ZipFile(path) as z:
        doc = ET.fromstring(z.read('word/document.xml'))
    math = [''.join(m.itertext()) for m in doc.findall('.//m:oMath', ns)]
    texts = [''.join(t.text or '' for t in p.findall('.//w:t', ns))
             for p in doc.findall('.//w:p', ns)]
    tags = [t for t in texts if re.fullmatch(r'\((?:[A-H]|\d+)\.\d+\)', t)]
    inventory[name] = {'math_elements': len(math), 'equation_tags': tags,
                       'math_text': math}
result['actual_docx_inventory'] = inventory
for name in ('ch1', 'ch7', 'ch8', 'ch9', 'ch10', 'frontmatter', 'appendix'):
    read(CONDENSED / 'scripts' / ('build_' + name + '.py'))
for name in ('Thesis_V8_Condensed.docx', 'Thesis_V8_Condensed.pdf'):
    read(REPO / 'writing/v8' / name)

# Every per-frame distance is rebuilt independently from coordinate columns.
human = js(EVIDENCE / 'human.json')
synthetic = js(EVIDENCE / 'synthetic.json')
bare = js(EVIDENCE / 'bare_model.json')['recordings']
for filename, prefixes, keys in [
    ('human_pairs.csv', ('measured', 'rig'), ('recording', 'side', 'joint')),
    ('synthetic_pairs.csv', ('reference', 'reconstructed'), ('window', 'method', 'joint')),
    ('bare_model_pairs.csv', ('measured', 'model'), ('recording', 'side', 'joint', 'scope'))]:
    groups = defaultdict(list)
    row_differences = []
    for row in rows(EVIDENCE / filename):
        dist = float(np.linalg.norm(points(row, prefixes[0]) - points(row, prefixes[1])) * 100)
        groups[tuple(row[k] for k in keys)].append(dist)
        row_differences.append(abs(dist - float(row['error_cm'])))
    out = {}
    for key, values in groups.items():
        got = summary(values)
        if filename == 'human_pairs.csv':
            alias, side, joint = key
            expected = human[alias]['joints'][side + '_' + joint]
        elif filename == 'synthetic_pairs.csv':
            win, method, joint = key
            expected = next(s for s in synthetic['results']
                            if (s['window'], s['method'], s['joint']) == key)
        else:
            alias, side, joint, scope = key
            expected = bare[alias]['joints'][side + '_' + joint][scope]['vs_raw_measured']
        out['/'.join(key)] = {'computed': got, 'absolute_residuals': error(got, expected)}
    result[filename] = {'maximum_row_error_residual_cm': max(row_differences), 'groups': out}

# Waypoint lengths and fresh PCA from locally available frozen full tracks.
obj = js(EVIDENCE / 'object.json')['recordings']
out = {}
receiver_constants = read(REPO / 'eval/unity_check/check_unity_log.py').decode()
matched = re.search(r'DESK_THICK, LEG_H = ([0-9.]+), ([0-9.]+)', receiver_constants)
desk_thickness, leg_height = map(float, matched.groups())
for alias, block in obj.items():
    track = rows(REPO / block['track'])
    accepted = [r for r in track if int(r['detected']) == 1 and int(r['filled']) == 0
                and np.isfinite([float(r['unity_p' + a]) for a in 'xyz']).all()]
    up = np.array(block['gravity_up_unity'])
    up /= np.linalg.norm(up)
    v = np.cross(up, [0., 1., 0.])
    K = cross_matrix(v)
    G = np.eye(3) + K + K @ K / (1 + up[1])
    calibration = js(REPO / block['calibration'])
    floor_translation = np.array([0., calibration['scene_geometry']['origin_above_tabletop_m']
                                   + desk_thickness + leg_height, 0.])
    segs = []
    for i, seg in enumerate(block['segments'], 1):
        a = np.array(block['waypoints']['W' + str(i)]['position_m']) + floor_translation
        b = np.array(block['waypoints']['W' + str(i + 1)]['position_m']) + floor_translation
        length = float(np.linalg.norm(b - a) * 100)
        absolute = abs(length - seg['physical_cm'])
        computed = dict(reconstructed_cm=length, absolute_error_cm=absolute,
                        relative_error_pct=100 * absolute / seg['physical_cm'])
        segs.append({'segment': seg['segment'], 'computed': computed,
                     'residuals': error(computed, seg)})
    start = block['waypoints']['W3']['first_frame']
    # The scatter ends when the W4 averaging interval starts, exactly as
    # the pinned span_frames reports; it does not include the whole dwell.
    stop = block['waypoints']['W4']['first_frame']
    P = np.array([[float(row['unity_p' + a]) for a in 'xyz'] for row in accepted
                  if start <= int(row['frame']) <= stop]) @ G.T + floor_translation
    X = P - P.mean(axis=0)
    C = X.T @ X / len(P)
    eigenvalues, eigenvectors = np.linalg.eigh(C)
    u = eigenvectors[:, -1]
    residual = X @ (np.eye(3) - np.outer(u, u))
    stats = summary(np.linalg.norm(residual, axis=1) * 100)
    angle = float(np.degrees(np.arcsin(abs(u[1]))))
    pinned = block['scatter']['rail_W3_to_W4']
    out[alias] = {'accepted': len(accepted), 'Scene_floor_translation_m': floor_translation.tolist(),
                  'Scene_centroid_m': P.mean(axis=0).tolist(), 'segments': segs,
                  'PCA_computed': stats, 'PCA_summary_residuals': error(stats, pinned),
                  'tilt_deg': angle, 'tilt_residual_deg': abs(angle-pinned['tilt_from_horizontal_deg']),
                  'PCA_eigenvalues_m2': eigenvalues.tolist(),
                  'PCA_objective_residual_m2': float(abs(np.sum(residual**2) - len(P) * sum(eigenvalues[:2])))}
result['equations_7_1_to_7_4'] = out

loop = js(EVIDENCE / 'loop_detection.json')
track = rows(REPO / loop['track'])
result['loop_detection_from_frozen_track'] = {
    'total': len(track), 'detected': sum(int(r['detected']) == 1 for r in track),
    'accepted': int(sum(int(r['detected']) == 1 and int(r['filled']) == 0
                    and np.isfinite([float(r['unity_p'+a]) for a in 'xyz']).all() for r in track))}

# Runtime arithmetic is calculated from the pinned report, not fresh profiling.
profile = read(REPO / 'v2/dataset/r6b_probe_baseline.txt').decode()
alignment = js(REPO / 'v2/dataset/m03_rail_corrected.json')['angle_comparison']
best = min(alignment['candidates'], key=lambda x: x['pooled_median_deg'])
result['chapter8_runtime'] = {'fps_from_displayed_counts': 900 / 31.0,
    'nominal_frame_budget_ms': 1000 / 30, 'buffer_delay_ms_at_nominal_rate': 2 * 1000 / 30,
    'best_alignment_candidate': best, 'pinned_groups': alignment['groups'],
    'pinned_per_angle': alignment.get('per_angle'),
    'profiler_p99_lines': [line for line in profile.splitlines()
                          if 'p99' in line and any(s in line for s in ['detect', 'pnp', 'filter+map', 'mediapipe', 'deproj+filt', 'solve', 'shm-write', 'total'])]}

# Appendix A payload and C/D calibrated pixel equations.
meta_path = REPO / 'v1/mediapipe/output/recording_20260831_065553_landmarks_raw.meta.json'
meta = js(meta_path)
intr = meta['color_intrinsics']
fx, fy, cx, cy = [intr[k] for k in ['fx', 'fy', 'ppx', 'ppy']]
lm = next(r for r in rows(meta_path.with_name(meta_path.name.replace('.meta.json', '.csv')))
          if int(r['frame']) == 533)
ar = next(r for r in rows(REPO / 'eval/output/recording_20260831_065553_aruco_raw_scaled.csv')
          if int(r['frame']) == 533)
deprojection = {}
for name, u, v, z in [('wrist', 209, 308, float(lm['right_wrist_z'])),
                      ('object_depth', 200, 341, float(ar['m1_depth_z']))]:
    p = np.array([z * (u - cx) / fx, z * (v - cy) / fy, z])
    back = [fx * p[0] / p[2] + cx, fy * p[1] / p[2] + cy]
    rounded = np.round(p, 2)
    rounded_back = [fx * rounded[0] / rounded[2] + cx, fy * rounded[1] / rounded[2] + cy]
    deprojection[name] = {'pixel': [u, v], 'point_m': p.tolist(),
                          'exact_reprojection': back, 'rounded_point_reprojection': rounded_back}
result['appendix_A_C_D'] = {'payload_bytes': 900 * 640 * 480 * (2 + 3),
    'payload_decimal_GB': 900 * 640 * 480 * (2 + 3) / 1e9,
    'focal_length_relative_difference_pct': 100 * abs(fx-fy) / fx,
    'FOV_deg_symmetric': [float(2*np.degrees(np.arctan(320/fx))), float(2*np.degrees(np.arctan(240/fy)))],
    'deprojection': deprojection}
fov_spans = {}
for name, width, focal, centre in [('horizontal', intr['width'], fx, cx),
                                  ('vertical', intr['height'], fy, cy)]:
    spans = {}
    for convention, lower, upper in [('boundaries_0_to_size', 0., float(width)),
                                      ('pixel_edges', -0.5, width - 0.5),
                                      ('pixel_centres', 0., width - 1.)]:
        angle = float(np.degrees(np.arctan((upper-centre)/focal)
                                  - np.arctan((lower-centre)/focal)))
        spans[convention] = {'first_pixel_coordinate': lower,
                             'last_pixel_coordinate': upper,
                             'angular_span_deg': angle,
                             'rounded_one_decimal_deg': round(angle, 1)}
    fov_spans[name] = spans
result['appendix_A_C_D']['principal_point_aware_FOV_spans'] = fov_spans
result['appendix_A_C_D']['FOV_interpretation'] = (
    'The centred-principal-point formula produces the nominal 55.6 by 43.1 degree pair. '
    'The recorded off-centre principal point gives 55.5 by 43.1 after rounding, '
    'for both boundary conventions. The earlier audit claim that both pairs round '
    'identically was incorrect; the final audit preserves this correction explicitly.')

R = np.array([[float(ar[f'm1_r{i}{j}']) for j in range(1, 4)] for i in range(1, 4)])
theta = np.arccos((np.trace(R) - 1) / 2)
axis = np.array([R[2,1] - R[1,2], R[0,2] - R[2,0], R[1,0] - R[0,1]]) / (2*np.sin(theta))
K = cross_matrix(axis)
rebuilt = np.eye(3) + np.sin(theta) * K + (1-np.cos(theta)) * K @ K
ranges = {mid: float(np.linalg.norm([float(ar[f'm{mid}_t{a}']) for a in 'xyz'])) for mid in (0, 2, 1)}
result['appendix_E'] = {'stored_rotation': R.tolist(), 'determinant': float(np.linalg.det(R)),
    'orthogonality_max_residual': float(abs(R.T@R-np.eye(3)).max()),
    'theta_deg': float(np.degrees(theta)), 'axis': axis.tolist(),
    'skew': K.tolist(), 'skew_squared': (K@K).tolist(),
    'recomposition_max_residual': float(abs(rebuilt-R).max()),
    'round2_matrix_equal': bool(np.array_equal(np.round(rebuilt, 2), np.round(R, 2))),
    'ranges_m': ranges,
    'old_1e_minus5_claim_present': b'0.00001' in read(CONDENSED / 'scripts/build_appendix.py')}
original_ar = next(r for r in rows(REPO / 'v1/aruco/output/recording_20260831_065553_aruco_raw.csv')
                   if int(r['frame']) == 533)
R_full = np.array([[float(original_ar[f'm1_r{i}{j}']) for j in range(1,4)] for i in range(1,4)])
theta_full = np.arccos((np.trace(R_full) - 1) / 2)
axis_full = np.array([R_full[2,1]-R_full[1,2], R_full[0,2]-R_full[2,0],
                      R_full[1,0]-R_full[0,1]])/(2*np.sin(theta_full))
K_full = cross_matrix(axis_full)
rebuilt_full = np.eye(3)+np.sin(theta_full)*K_full+(1-np.cos(theta_full))*K_full@K_full
result['appendix_E']['original_raw_before_scaled_csv_serialization'] = {
    'rotation': R_full.tolist(), 'theta_deg': float(np.degrees(theta_full)),
    'axis': axis_full.tolist(),
    'recomposition_max_residual': float(abs(rebuilt_full-R_full).max()),
    'round2_matrix_equal': bool(np.array_equal(np.round(rebuilt_full,2),np.round(R_full,2)))}

params = js(REPO / 'v1/mediapipe/output/recording_20260831_065553_landmarks_filtered.meta.json')['params']
b, a = butter(params['butter_order'], params['cutoff_hz'], fs=params['fs_hz'])
_, h = freqz(b, a, worN=[params['cutoff_hz']], fs=params['fs_hz'])
sg = savgol_coeffs(params['smooth_window'], params['smooth_polyorder'])
_, hg = freqz(sg, worN=[params['cutoff_hz']], fs=params['fs_hz'])
read(REPO / 'writing/v7/scripts/make_appF_fig.py')
result['appendix_F'] = {'params': params,
    'cutoff_Hz': params['cutoff_hz'], 'Butterworth_single_pass_amplitude': float(abs(h[0])),
    'Butterworth_two_pass_amplitude': float(abs(h[0])**2),
    'SG_plotted_amplitude': float(abs(hg[0])), 'SG_squared_amplitude': float(abs(hg[0])**2)}
read(REPO / 'v1/mediapipe/filter_landmarks.py')
# An interior steady ramp separates the two mathematical scale definitions.
# The 7-sample window is the frozen metadata value, not a newly tuned rule.
ramp = np.arange(21., dtype=float)
medians = np.array([np.median(ramp[max(0,i-3):min(len(ramp),i+4)]) for i in range(len(ramp))])
residuals = abs(ramp-medians)
result['appendix_F']['MAD_definition_counterexample'] = {
    'signal': 'x_t=t on indices0..20; centre t=10; centered window7',
    'conventional_window_MAD': float(np.median(abs(ramp[7:14]-np.median(ramp[7:14])))),
    'implementation_rolling_residual_median': float(np.median(residuals[7:14]))}

truth = rows(REPO / 'v1/kinematics/dataset/arm_both_truth.csv')
frame742 = next(r for r in truth if int(r['frame']) == 742)
angles = {k: float(v) for k, v in frame742.items() if k not in ('frame', 'time_s')}
result['appendix_H_nonzero_count'] = {'frame': 742, 'angle_fields': angles,
    'stored_angle_count': len(angles), 'nonzero_angle_count': sum(v != 0 for v in angles.values()),
    'maximum_nonzero_angles_any_frame': max(sum(float(v) != 0 for k,v in row.items()
                                              if k not in ('frame','time_s')) for row in truth)}
# Replay the six existing synthetic inputs through the frozen pure solvers.
# This calls no generator, writes no dataset and disables import cache writes.
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO / 'v1/kinematics'))
from root_frame import build_root_frame, euler_unity_zxy
from shoulder import solve_right_arm, solve_left_arm
read(REPO / 'v1/kinematics/root_frame.py')
read(REPO / 'v1/kinematics/shoulder.py')
synthetic_checks = {}
names = ['left_hip', 'right_hip', 'right_shoulder', 'right_elbow',
         'right_wrist', 'left_shoulder', 'left_elbow', 'left_wrist']
for name in ['synthetic', 'shoulder_only', 'shoulder_torso', 'elbow_only', 'arm_full', 'arm_both']:
    lm_rows = rows(REPO / 'v1/kinematics/dataset' / (name + '_landmarks.csv'))
    truth_name = 'synthetic_angles_truth.csv' if name == 'synthetic' else name + '_truth.csv'
    truth_rows = rows(REPO / 'v1/kinematics/dataset' / truth_name)
    errs = []
    for row, tr in zip(lm_rows, truth_rows):
        p = {n: points(row,n)*[1.,-1.,1.] for n in names}
        Rr = build_root_frame(p['left_hip'],p['right_hip'],p['right_shoulder'])
        decoded = euler_unity_zxy(Rr)
        columns = ['euler_'+a for a in 'xyz'] if name == 'synthetic' else ['root_'+a for a in 'xyz']
        expected = [float(tr[c]) for c in columns]
        if name != 'synthetic':
            sh, el, _ = solve_right_arm(p['right_shoulder'],p['right_elbow'],p['right_wrist'],Rr)
            lsh, lel, _ = solve_left_arm(p['left_shoulder'],p['left_elbow'],p['left_wrist'],Rr)
            decoded = np.r_[decoded,sh,el,lsh,lel]
            expected += [float(tr[c]) for c in ['sh_y','sh_z','sh_twist','elbow_y','elbow_z',
                         'l_sh_y','l_sh_z','l_sh_twist','l_elbow_y','l_elbow_z']]
        errs.append(np.max(np.abs((decoded - expected + 180) % 360 - 180)))
    synthetic_checks[name] = {'frames': len(lm_rows), 'maximum_wrapped_angle_residual_deg': float(max(errs))}
result['appendix_H_frozen_synthetic_replay'] = synthetic_checks
read(REPO / 'v1/kinematics/occlusion_ext.py')

# Assert the final printed corrections against independent calculations above.
with zipfile.ZipFile(CONDENSED / 'Appendices.docx') as z:
    appendix_root = ET.fromstring(z.read('word/document.xml'))
appendix_text = '\n'.join(''.join(t.text or '' for t in p.findall('.//w:t', ns))
                         for p in appendix_root.findall('.//w:p', ns))
final_checks = {
    'D_1_vertical_FOV_rounds_to_43_1': round(result['appendix_A_C_D']['FOV_deg_symmetric'][1], 1) == 43.1,
    'D_1_prints_correct_FOV': '55.6 by 43.1 degrees' in appendix_text and '55.6 by 43.2 degrees' not in appendix_text,
    'D_1_nominal_FOV_assumption_explicit': 'Ignoring the small principal-point offset, the focal lengths and image size give a nominal field of view of 55.6 by 43.1 degrees' in appendix_text,
    'F_two_distinct_rolling_medians_described': "Each sample is first compared with its own seven-frame rolling median; a second rolling median of those absolute residuals" in appendix_text,
    'F_two_pass_amplitude_gains_described': 'the two passes multiply their amplitude gains' in appendix_text,
    'F_figure_caption_describes_amplitude_gain': 'The amplitude gain of the two linear candidates against frequency, including both passes of the Butterworth filter' in appendix_text,
    'H_both_arm_nonzero_count_is_eleven': result['appendix_H_nonzero_count']['nonzero_angle_count'] == 11,
    'H_table_prints_eleven': 'torso and both arms, eleven angles nonzero' in appendix_text and 'twelve angles nonzero' not in appendix_text,
    'Appendix_numbered_equation_tags': inventory['Appendices']['equation_tags'] == ['(D.1)', '(D.2)', '(E.1)', '(G.1)'],
    'Chapter_7_numbered_equation_tags': inventory['Chapter_7_Evaluation']['equation_tags'] == ['(7.1)', '(7.2)', '(7.3)', '(7.4)', '(7.5)', '(7.6)'],
}
assert all(final_checks.values()), final_checks
result['final_printed_correction_checks'] = final_checks
result['source_sha256'] = sources
(HERE / 'ch7_appendix_results.json').write_text(json.dumps(result, indent=2) + '\n')
print('WROTE', HERE / 'ch7_appendix_results.json')
print('SOURCE_FILES', len(sources))
print('APPENDIX_H_NONZERO', result['appendix_H_nonzero_count']['nonzero_angle_count'])
print('PCA', json.dumps(result['equations_7_1_to_7_4'], indent=2))

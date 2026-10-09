#!/usr/bin/env python3
"""Independent source-clock, frame geometry, and negative-cache checks.

Checks the saved artifacts without importing the producer's angle solver.
The imported producer is used only for fail-closed cache negative tests.
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
GENERATOR = HERE.parent / 'anim/bank_kinematics.py'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    checks = []
    pages = []
    def check(name, condition, details=None):
        checks.append({'name': name, 'pass': bool(condition), 'details': details})
    for page in range(17, 21):
        folder = HERE / f'p{page:02d}'
        data = json.loads((folder / 'kinematic_source.json').read_text())
        inference = json.loads((folder / 'inference_frame_map.json').read_text())
        filtered = pd.read_csv(folder / 'landmarks_filtered.csv').set_index('frame')
        raw = pd.read_csv(folder / 'landmarks_raw.csv').set_index('frame')
        meta = json.loads((folder / 'landmarks_raw.meta.json').read_text())
        intr = meta['color_intrinsics']
        check(f'p{page} full inference count', inference['frames'] == len(raw) == len(inference['records']))
        ids = [r['color_hardware_frame_number'] for r in inference['records']]
        timestamps = [r['color_timestamp_ms'] for r in inference['records']]
        check(f'p{page} unique increasing color IDs', len(set(ids)) == len(ids) and np.all(np.diff(ids) > 0))
        check(f'p{page} increasing color timestamps', np.all(np.diff(timestamps) > 0))
        clock = np.asarray([r['relative_time_s'] for r in inference['records']])
        check(f'p{page} exact inference CSV clock', np.max(np.abs(clock - raw['time_s'].to_numpy())) <= .00000051)
        start, end = data['source_frame_interval']
        expected = [start]*60 + [f for f in range(start, end+1) for _ in range(2)] + [end]*60
        check(f'p{page} one shared delivery clock', expected == data['output_source_frames'])
        max_matrix = max_projection = max_angle = 0.
        for frame in range(start, end+1):
            row = filtered.loc[frame]
            rec = data['records'][str(frame)]
            src = inference['records'][frame]
            image = np.asarray(Image.open(src['cached_png']).convert('RGB'))
            check(f'p{page} f{frame} exact inference RGB', hashlib.sha256(image.tobytes()).hexdigest() == src['inference_rgb_sha256'])
            check(f'p{page} f{frame} source flags', all(raw.loc[frame, n+'_src'] == v for n, v in rec['raw_src'].items()))
            check(f'p{page} f{frame} filter flags', all(row[n+'_flag'] == v for n, v in rec['filter_flags'].items()))
            q = {n: row[[n+'_'+a for a in 'xyz']].to_numpy(float)*[1,-1,1]
                 for n in rec['points_camera_prime_m']}
            check(f'p{page} f{frame} filtered source points', all(np.array_equal(q[n], rec['points_camera_prime_m'][n]) for n in q))
            x = q['right_hip']-q['left_hip']; x /= np.linalg.norm(x)
            s = q['right_shoulder']-q['right_hip']
            z = np.cross(x,s); z /= np.linalg.norm(z)
            root = np.column_stack([x,np.cross(z,x),z])
            u = q['right_elbow']-q['right_shoulder']; u /= np.linalg.norm(u)
            a = root.T @ u
            ty,tz = np.arctan2(-a[2],a[0]),np.arcsin(a[1])
            swing = root @ Rotation.from_euler('YZ',[ty,tz]).as_matrix()
            f = q['right_wrist']-q['right_elbow']; f /= np.linalg.norm(f)
            fp = swing.T @ f
            perp = np.linalg.norm(fp[1:])
            twist_ok = perp >= 1e-6
            tau = np.arctan2(-fp[1],fp[2]) if twist_ok else 0.
            arm = swing @ Rotation.from_rotvec([tau,0,0]).as_matrix()
            g = arm.T @ f
            ey,ez = np.arctan2(-g[2],g[0]),np.arcsin(np.clip(g[1],-1,1))
            values = np.degrees([ty,tz,tau,ey,ez])
            saved = [rec[k] for k in ('sh_y','sh_z','sh_twist','el_y','el_z')]
            error = np.max(np.abs((values-saved+180)%360-180))
            max_angle = max(max_angle,float(error))
            max_matrix = max(max_matrix,*(float(np.max(np.abs(b-np.asarray(rec[k])))) for b,k in
                               [(root,'root_basis'),(swing,'swing_basis'),(arm,'upper_arm_basis')]))
            check(f'p{page} f{frame} actual observability', twist_ok == rec['twist_ok'] and abs(perp-rec['perpendicular_fraction'])<1e-12)
            basis = arm if page == 19 else swing
            triad = np.vstack([q['right_elbow'], q['right_elbow']+.075*basis.T])
            camera = triad * [1,-1,1]
            K = np.array([[intr['fx'],0,intr['ppx']],[0,intr['fy'],intr['ppy']],[0,0,1.]])
            pixel = cv2.projectPoints(camera,np.zeros(3),np.zeros(3),K,np.zeros(5))[0].reshape(-1,2)
            analytical = np.column_stack([intr['fx']*camera[:,0]/camera[:,2]+intr['ppx'],
                                          intr['fy']*camera[:,1]/camera[:,2]+intr['ppy']])
            max_projection = max(max_projection,float(np.max(np.abs(pixel-analytical))))
        check(f'p{page} independent root/swing/arm matrices', max_matrix<1e-11, max_matrix)
        check(f'p{page} independent angle reconstruction', max_angle<1e-9, max_angle)
        check(f'p{page} independent camera projection', max_projection<1e-9, max_projection)
        selected = json.loads((folder/'tracking_precondition_selected.json').read_text())
        check(f'p{page} unchanged selected tracking criteria', selected['criteria']=={'min_coverage':.95,'max_gap_s':.5})
        check(f'p{page} all selected eligibility verdicts', all(selected['verdicts'].values()))
        pages.append({'page':page,'selected_interval':[start,end],
                      'source_manifest_sha256':sha(folder/'kinematic_source.json'),
                      'processing_manifest_sha256':sha(folder/'source_manifest.json'),
                      'inference_map_sha256':sha(folder/'inference_frame_map.json'),
                      'independent_max_angle_error_deg':max_angle,
                      'independent_max_matrix_error':max_matrix,
                      'independent_max_reprojection_error_px':max_projection})
    # Targeted regressions for the source-review findings. Each altered
    # manifest lives in a temporary directory; canonical source files stay intact.
    sys.path.insert(0,str(GENERATOR.parent))
    spec = importlib.util.spec_from_file_location('bank_producer_for_negative_tests',GENERATOR)
    producer = importlib.util.module_from_spec(spec); spec.loader.exec_module(producer)
    real_paths = producer.paths
    negative = []
    for name, where, key in [('raw_metadata','inference','raw_metadata'),
                             ('filtered_csv','processing','filtered'),
                             ('filtered_metadata','processing','filtered_meta'),
                             ('model','inference','model'),
                             ('frozen_method','processing','filter')]:
        with tempfile.TemporaryDirectory(prefix='bank_negative_') as tmp:
            folder = Path(tmp); original = real_paths(17)
            imap = json.loads((original['folder']/'inference_frame_map.json').read_text())
            processing = json.loads((original['folder']/'source_manifest.json').read_text())
            if name == 'raw_metadata': imap[key]['sha256']='0'*64
            elif where == 'inference': imap['sources'][key]['sha256']='0'*64
            elif name == 'frozen_method': processing['source_files'][key]['sha256']='0'*64
            else: processing['outputs'][key]['sha256']='0'*64
            (folder/'inference_frame_map.json').write_text(json.dumps(imap))
            (folder/'source_manifest.json').write_text(json.dumps(processing))
            producer.paths = lambda page, original=original,folder=folder: {**original,'folder':folder}
            rejected=False
            try: producer.prepare.cache_clear();producer.prepare(17)
            except ValueError: rejected=True
            untouched=not (folder/'derived_kinematics.csv').exists() and not (folder/'kinematic_source.json').exists()
            negative.append({'case':name,'rejected_before_new_provenance':rejected and untouched})
    producer.paths = real_paths
    correct = json.loads((HERE/'p20/tracking_precondition_full.json').read_text())
    for name, mutate, code in [
        ('stale_stem',lambda r:r.update(stem='wrong'),1),
        ('changed_threshold',lambda r:r['criteria'].update(min_coverage=.90),1),
        ('missing_verdict',lambda r:r.pop('verdicts'),1),
        ('failure_exit_without_failure_verdict',lambda r:r.update(verdicts={k:True for k in r['verdicts']}),1),
        ('failure_verdict_with_success_exit',lambda r:None,0)]:
        bad=copy.deepcopy(correct);mutate(bad);rejected=False
        try:producer.require_tracking_result(bad,producer.paths(20)['bag'].stem,code)
        except ValueError:rejected=True
        negative.append({'case':name,'rejected_before_new_provenance':rejected})
    for result in negative:check('negative '+result['case'],result['rejected_before_new_provenance'])
    report={'status':'PASS' if all(c['pass'] for c in checks) else 'FAIL',
            'passed':sum(c['pass'] for c in checks),'failed':sum(not c['pass'] for c in checks),
            'pages':pages,'negative_cache_and_checker_cases':negative,'checks':checks,
            'validator':str(Path(__file__).relative_to(ROOT)),'validator_sha256':sha(__file__),
            'producer_sha256':sha(GENERATOR),
            'scope':'Numerical/source-clock audit of new qualitative demos; not external accuracy. The separate frozen v1 overlay is an enumeration-based diagnostic and does not certify inference-frame identity.'}
    (HERE/'BANK_SOURCE_CHECK.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],report['passed'],'PASS',report['failed'],'FAIL')
    if report['failed']:raise SystemExit(1)


if __name__=='__main__':main()

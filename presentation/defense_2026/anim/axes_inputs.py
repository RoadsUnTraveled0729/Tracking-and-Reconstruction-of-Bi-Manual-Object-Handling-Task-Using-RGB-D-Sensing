#!/usr/bin/env python3
"""Read-only, frame-indexed axis inputs and independently checked projections."""
import hashlib
import json
from pathlib import Path
import sys
from functools import lru_cache
import numpy as np
import pandas as pd

from coordinate_axes import CAMERA_TO_CAMERA_PRIME as F,project_pinhole

ROOT=Path(__file__).resolve().parents[3]
STEMS={'r7':'recording_20260909_000024','r5':'recording_20260825_222315'}
S=np.array([[1.,0,0],[0,0,1],[0,1,0]])


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@lru_cache(maxsize=2)
def load(alias):
    stem=STEMS[alias]
    paths={'filtered':ROOT/f'v1/mediapipe/output/{stem}_landmarks_filtered.csv',
           'raw':ROOT/f'v1/mediapipe/output/{stem}_landmarks_raw.csv',
           'meta':ROOT/f'v1/mediapipe/output/{stem}_landmarks_raw.meta.json',
           'mask':ROOT/f'eval/output/recovery_{alias}/failure_mask.csv',
           'angles':ROOT/f'eval/output/recovery_{alias}/angles_recovery.csv',
           'object':ROOT/f'eval/output/{stem}_scaled_object_world_filtered_clean.csv',
           'calibration':ROOT/f'eval/output/scene_calibration_{alias}c.json'}
    return {'tables':{k:pd.read_csv(v).set_index('frame') for k,v in paths.items() if v.suffix=='.csv'},
            'intrinsics':json.loads(paths['meta'].read_text())['color_intrinsics'],
            'calibration':json.loads(paths['calibration'].read_text()),
            'sources':{k:{'path':str(v.relative_to(ROOT)),'sha256':sha(v)} for k,v in paths.items()}}


@lru_cache(maxsize=5000)
def frame_axes(alias,index,*,arm=False,object_axes=True):
    sys.path.insert(0,str(ROOT/'v1/kinematics'))
    from root_frame import build_root_frame
    from shoulder import solve_right_arm,recompose_shoulder
    data=load(alias);tables=data['tables'];row=tables['filtered'].loc[index];raw=tables['raw'].loc[index]
    flags=tables['mask'].loc[index];saved=tables['angles'].loc[index]
    names=['left_hip','right_hip','right_shoulder','right_elbow','right_wrist']
    p={n:row[[n+'_'+a for a in 'xyz']].values.astype(float)*[1,-1,1] for n in names}
    have={n:bool(np.isfinite(v).all() and int(raw[n+'_src'])==0) for n,v in p.items()}
    root_ok=(int(flags['fail_torso'])==0 and int(saved['tag_0'])==0 and all(have[n] for n in ['left_hip','right_hip','right_shoulder']))
    triads=[];states=[];errors=[]
    if root_ok:
        basis=build_root_frame(p['left_hip'],p['right_hip'],p['right_shoulder'])
        triads.append({'frame_name':'L24','origin':p['right_hip'],'basis':basis,'length':.10,'state':'measured input'})
        if arm and int(flags['fail_arm_R'])==0 and all(int(saved[f'tag_{g}'])==0 for g in [1,2,3]) and have['right_elbow'] and have['right_wrist']:
            sh,el,ok=solve_right_arm(p['right_shoulder'],p['right_elbow'],p['right_wrist'],basis)
            if ok:triads.append({'frame_name':'L14','origin':p['right_elbow'],'basis':basis@recompose_shoulder(sh),'length':.075,'state':'measured input'})
        states.append('L24: measured input')
    else:states.append('L24 omitted: input rejected or not measured')
    if object_axes:
        obj=tables['object'].loc[index]
        if bool(obj['detected']) and not bool(obj.get('filled',0)):
            t=np.asarray(data['calibration']['T_cam_desk']);world_point=obj[['tx','ty','tz']].values.astype(float)
            camera_point=t[:3,:3]@world_point+t[:3,3]
            world_rotation=obj[[f'r{i}{j}' for i in range(1,4) for j in range(1,4)]].values.astype(float).reshape(3,3)
            # MappedMarker changes the marker basis by S; Camera-prime changes
            # the reference basis by F. Both reflections are required.
            mapped_basis=F@t[:3,:3]@world_rotation@S
            triads.append({'frame_name':'MappedMarker','origin':F@camera_point,'basis':mapped_basis,'length':.045,'state':'measured object pose'})
            states.append('MappedMarker: measured pose')
            # Check projection against OpenCV's independent projection path.
            import cv2
            k=data['intrinsics'];K=np.array([[k['fx'],0,k['ppx']],[0,k['fy'],k['ppy']],[0,0,1.]])
            endpoints=np.vstack([camera_point,camera_point+.045*(t[:3,:3]@world_rotation@S).T])
            reference=cv2.projectPoints(endpoints,np.zeros(3),np.zeros(3),K,np.zeros(5))[0].reshape(-1,2)
            checked=project_pinhole(endpoints,k)
            errors.append(float(np.max(np.abs(reference-checked))))
        else:states.append('Object axes omitted: no measured pose')
    for triad in triads:
        assert np.allclose(triad['basis'].T@triad['basis'],np.eye(3),atol=5e-5)
        assert abs(np.linalg.det(triad['basis'])-1)<5e-5
        import cv2
        k=data['intrinsics'];K=np.array([[k['fx'],0,k['ppx']],[0,k['fy'],k['ppy']],[0,0,1.]])
        endpoints=np.vstack([triad['origin'],triad['origin']+triad['length']*triad['basis'].T])@F.T
        reference=cv2.projectPoints(endpoints,np.zeros(3),np.zeros(3),K,np.zeros(5))[0].reshape(-1,2)
        errors.append(float(np.max(np.abs(reference-project_pinhole(endpoints,k)))))
    assert max(errors,default=0.)<1e-10
    return {'frame':index,'triads':triads,'states':states,'projection_max_error_px':max(errors,default=0.),
            'intrinsics':data['intrinsics'],'sources':data['sources']}

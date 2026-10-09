"""Independent numeric backstop for instrumented in-engine frame bases."""
from pathlib import Path
import json,sys,hashlib
import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'r7'
a=pd.read_csv(OUT/'axes_matrices.csv').drop_duplicates(['frame','name']);stream=pd.read_csv(OUT/'integrated_stream.csv').set_index('frame');rig=pd.read_csv(OUT/'unity_person_log.csv').drop_duplicates('frame').set_index('frame')
sys.path.insert(0,str(ROOT/'eval'))
from common import paths
stem=next(k for k,v in paths.ALIAS.items() if v==OUT.name)
cal=json.loads(paths.calib_for(stem).read_text())
world_camera=np.linalg.inv(np.asarray(cal['T_cam_desk']));S=np.eye(3)[[0,2,1]];F=np.diag([1,-1,1]);g=np.array(cal['scene_geometry']['gravity_up_unity']);g/=np.linalg.norm(g)
G=Rotation.align_vectors([[0,1,0]],[g])[0].as_matrix();anchor=G@S@world_camera[:3,:3]@F
results=[]
def check(name,ok,**detail):results.append(dict(name=name,passed=bool(ok),**detail))
def rot(axis,angle):
 v=np.zeros(3);v['xyz'.index(axis)]=np.deg2rad(angle);return Rotation.from_rotvec(v).as_matrix()
max_rotation=max_origin=max_time=max_camera_orth=0.
for row in a.itertuples(index=False):
 f=int(row.frame);s=stream.loc[f];p=rig.loc[f];angles=[s[f'a{i}'] for i in range(13)]
 root=rot('y',angles[1])@rot('x',angles[0])@rot('z',angles[2]);name=row.name
 expected=anchor@root
 if name=='Elbow_R':expected=expected@rot('y',angles[3])@rot('z',angles[4])@rot('x',angles[5])
 if name=='Elbow_L':expected=expected@rot('y',-angles[8])@rot('z',-angles[9])@rot('x',angles[10])
 actual=np.array([[getattr(row,f'r{i}{j}') for j in range(3)]for i in range(3)])
 max_rotation=max(max_rotation,float(np.max(abs(actual-expected))))
 prefix={'Pelvis_parallel_L24':'hip','Shoulder_R':'rsh','Elbow_R':'rel','Shoulder_L':'lsh','Elbow_L':'lel'}[name]
 expected_origin=np.array([p[f'{prefix}_{d}']for d in 'xyz']);actual_origin=np.array([row.origin_x,row.origin_y,row.origin_z])
 max_origin=max(max_origin,float(np.max(abs(actual_origin-expected_origin))))
 max_time=max(max_time,abs(row.time_s-s.time_s))
 camera=np.array([float(v)for v in row.camera_world_4x4.split(';')]).reshape(4,4)
 projection=np.array([float(v)for v in row.projection_4x4.split(';')]).reshape(4,4)
 assert np.isfinite(projection).all() and projection[3,2]!=0
 max_camera_orth=max(max_camera_orth,float(np.max(abs(camera[:3,:3].T@camera[:3,:3]-np.eye(3)))))
check('Composed model bases match independent calibrated axis-angle products',max_rotation<1e-5,max_component_error=max_rotation,tolerance=1e-5)
check('Origins match actual rendered joints, with pelvis named separately from L24',max_origin<2e-6,max_component_error_m=max_origin,tolerance_m=2e-6)
check('Logged source timestamps equal streamed frame timestamps',max_time<2e-5,max_error_s=float(max_time),tolerance_s=2e-5)
check('Captured camera bases are orthonormal',max_camera_orth<2e-5,max_component_error=max_camera_orth)
check('All five model frames are present for each recorded source frame',a.groupby('frame').name.nunique().eq(5).all())
check('No measured wrist orientation is invented',not a.name.str.contains('Wrist').any())
report={'status':'PASS'if all(x['passed']for x in results)else'FAIL','checks':results,'distinct_source_frames':int(a.frame.nunique()),'sources':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in [OUT/'axes_matrices.csv',OUT/'integrated_stream.csv',OUT/'unity_person_log.csv']},'interpretation':'Fresh explanatory rig replay. Model bases precede bone rest offsets. These checks establish application consistency, not anatomical accuracy.'}
(OUT/'axes_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));sys.exit(report['status']!='PASS')

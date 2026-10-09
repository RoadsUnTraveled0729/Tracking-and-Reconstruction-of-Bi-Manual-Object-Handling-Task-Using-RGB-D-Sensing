"""Independent archived packet, applied model and source-clock checks."""
from pathlib import Path
import hashlib,json,sys,struct
import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=HERE/'r5_archived'
SOURCE=ROOT/'eval/output/unity_check_r5/integrated_stream.csv';CAL=ROOT/'eval/output/scene_calibration_r5c.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)=='af952121f3438fca5cd153ad59f4ed1a1b488d5ef01e35b4f985404ccc5b2f60'
assert sha(OUT/'integrated_stream.csv')==sha(SOURCE)
src=pd.read_csv(SOURCE).set_index('frame');axes=pd.read_csv(OUT/'axes_matrices.csv').drop_duplicates(['frame','name']);rig=pd.read_csv(OUT/'unity_person_log.csv').drop_duplicates('frame').set_index('frame')
checks=[]
def check(name,ok,**detail):checks.append(dict(name=name,passed=bool(ok),**detail))
check('Archived CSV copied byte-for-byte',sha(SOURCE)==sha(OUT/'integrated_stream.csv'))
check('Exactly 2099 source packet rows with contiguous IDs',list(src.index)==list(range(2099)))
max_roundtrip=0
for f,row in src.iterrows():
 numbers=[row.time_s]+[row['pel_'+c]for c in 'xyz']+[row['a'+str(i)]for i in range(13)]+[row['op'+c]for c in 'xyz']+[row['oe'+c]for c in 'xyz']
 packed=struct.pack('<if3f13f3f3fHH',int(f),*numbers,int(row['mask']),int(row.obj_live));back=struct.unpack('<if3f13f3f3fHH',packed)
 assert back[0]==f and back[-2:]==(int(row['mask']),int(row.obj_live))
 assert np.array_equal(np.array(back[1:-2],dtype=np.float32),np.array(numbers,dtype=np.float32))
 max_roundtrip=max(max_roundtrip,float(np.max(abs(np.array(back[1:-2])-numbers))))
check('All archived fields survive exact protocol float32 serialization',True,max_float32_rounding=max_roundtrip)
cal=json.loads(CAL.read_text());wc=np.linalg.inv(np.array(cal['T_cam_desk']));S=np.eye(3)[[0,2,1]];F=np.diag([1,-1,1]);g=np.array(cal['scene_geometry']['gravity_up_unity']);g/=np.linalg.norm(g);G=Rotation.align_vectors([[0,1,0]],[g])[0].as_matrix();anchor=G@S@wc[:3,:3]@F

def rot(axis,d):
 v=np.zeros(3);v['xyz'.index(axis)]=np.deg2rad(d);return Rotation.from_rotvec(v).as_matrix()
me=oe=te=ce=be=0.
rest_by_bone={}
for row in axes.itertuples(index=False):
 s=src.loc[row.frame];p=rig.loc[row.frame];a=[s['a'+str(i)]for i in range(13)];m=anchor@rot('y',a[1])@rot('x',a[0])@rot('z',a[2])
 if row.name=='Elbow_R':m=m@rot('y',a[3])@rot('z',a[4])@rot('x',a[5])
 if row.name=='Elbow_L':m=m@rot('y',-a[8])@rot('z',-a[9])@rot('x',a[10])
 actual=np.array([[getattr(row,f'r{i}{j}')for j in range(3)]for i in range(3)]);me=max(me,float(abs(m-actual).max()))
 bonechain=anchor@rot('y',a[1])@rot('x',a[0])@rot('z',a[2])
 if row.name in ['Shoulder_R','Elbow_R']:bonechain=bonechain@rot('y',a[3])@rot('z',a[4])@rot('x',a[5])
 if row.name in ['Shoulder_L','Elbow_L']:bonechain=bonechain@rot('y',-a[8])@rot('z',-a[9])@rot('x',a[10])
 if row.name=='Elbow_R':bonechain=bonechain@rot('y',a[6])@rot('z',a[7])
 if row.name=='Elbow_L':bonechain=bonechain@rot('y',-a[11])@rot('z',-a[12])
 bone=np.array([[getattr(row,f'b{i}{j}')for j in range(3)]for i in range(3)]);rest=bonechain.T@bone
 if row.name not in rest_by_bone:rest_by_bone[row.name]=rest
 be=max(be,float(abs(rest-rest_by_bone[row.name]).max()))
 key={'Pelvis_parallel_L24':'hip','Shoulder_R':'rsh','Elbow_R':'rel','Shoulder_L':'lsh','Elbow_L':'lel'}[row.name]
 oe=max(oe,float(abs(np.array([row.origin_x,row.origin_y,row.origin_z])-p[[key+'_'+c for c in 'xyz']].to_numpy(float)).max()));te=max(te,abs(row.time_s-s.time_s))
 camera=np.fromstring(row.camera_world_4x4,sep=';').reshape(4,4);ce=max(ce,float(abs(camera[:3,:3].T@camera[:3,:3]-np.eye(3)).max()))
check('Logged model bases match independent archived-angle composition',me<1e-5,max_component_error=me)
check('All rendered bone rotations follow all 13 archived angles with constant authored rest offsets',be<1e-5,max_rest_residual_variation=be)
check('Triads remain on logged rendered joints',oe<2e-6,max_origin_error_m=oe)
check('Captured timestamp equals archived source clock',te<2e-5,max_error_s=te)
check('Camera orientation is orthonormal',ce<2e-5,max_error=ce)
check('All five model frames logged for every retained source frame',axes.groupby('frame').name.nunique().eq(5).all() and set(axes.frame)==set(range(2098)))
check('Original binary mask is applied without imported recovery tags',all(int(row['mask'])==int(src.loc[f,'mask'])for f,row in rig.iterrows()))
receiver=(Path('/tmp/defense_axes_capture/Unity/Assets/Scripts/IntegratedSceneReceiver.cs')).read_text();original=(ROOT/'Unity/Assets/Scripts/IntegratedSceneReceiver.cs').read_text()
expected=original.replace('/home/luo/Desktop/New_SandBox/v1/integration/output','/tmp/defense_axes_capture/runtime').replace('/tmp/r5_','/tmp/defense_axes_capture/r5_').replace('/dev/shm/integrated_scene','/dev/shm/defense_axes_integrated_scene').replace('/dev/shm/aruco_scene','/dev/shm/defense_axes_aruco_scene').replace('rigRoot.position += target - hip.position;','rigRoot.position += target - hip.position;\n        DefenseAxes.Update(frame,t,hip,upperArm,forearm,lUpperArm,lForearm,qA*qRoot,qA*qRoot*qSh,qA*qRoot*qShL);')
check('Copied receiver differs only by paths and post-pose axis hook',receiver==expected)
report={'status':'PASS'if all(c['passed']for c in checks)else'FAIL','checks':checks,'sources':{str(p.relative_to(ROOT)):sha(p)for p in [SOURCE,CAL,HERE/'replay_archived_packets.py',HERE/'DefenseAxes.cs',ROOT/'Unity/Assets/Scripts/IntegratedSceneReceiver.cs']},'validator_sha256':sha(Path(__file__)),'limits':['No current recovery tags are transferred.','New archived-packet render; historical exact renderer build is unavailable.','Terminal source frame 2098 is not captured by the unchanged loop.','No anatomical accuracy result.']}
(OUT/'archived_replay_check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));sys.exit(report['status']!='PASS')

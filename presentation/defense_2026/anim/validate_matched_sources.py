#!/usr/bin/env python3
"""Independently check recorded matched-media transforms and frame maps.

Read-only scientific inputs; writes only the independent review JSON.
"""
from pathlib import Path
import json,csv,hashlib,math,datetime,os
import numpy as np
import pandas as pd
p=Path(__file__).resolve().parents[1];root=p.parents[1];os.chdir(root)
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
manifest=p/'media/provenance/matched_evidence.json';d=json.loads(manifest.read_text());report_path=p/'review/MATCHED_EVIDENCE_CHECK.json';rpt=json.loads(report_path.read_text())
assert rpt['evidence_manifest_sha256']==sha(manifest)
assert rpt['generator_sha256']==sha(p/'anim/matched_evidence.py')
source_hashes=[]
for source in d['sources']:
 if Path(source['path']).suffix == '.bag':
  continue
 assert sha(source['path'])==source['sha256'],source['path']
 source_hashes.append(source['path'])
assert sha(d['torso']['image'])==d['torso']['sha256']
assert sha(d['hip_example']['image'])==d['hip_example']['sha256']
rawp=Path('v1/mediapipe/output/recording_20260909_000024_landmarks_raw.csv');filp=rawp.with_name(rawp.name.replace('_raw.csv','_filtered.csv'))
raw=pd.read_csv(rawp).set_index('frame');filt=pd.read_csv(filp).set_index('frame')
meta=json.loads(rawp.with_suffix('.meta.json').read_text());k=meta['color_intrinsics'];assert not any(k['coeffs'])
objp=Path('eval/output/recording_20260909_000024_scaled_object_world_filtered_clean.csv');obj=pd.read_csv(objp).set_index('frame')
calib=json.load(open('eval/output/scene_calibration_r7c.json'));T=np.linalg.inv(np.asarray(calib['T_cam_desk']));P=np.array([[1,0,0],[0,0,1],[0,1,0]],float);F=np.diag([1.,-1,1]);M=P@T[:3,:3]@F;t=P@T[:3,3]
g=np.asarray(calib['scene_geometry']['gravity_up_unity']);g=g/np.linalg.norm(g);up=np.array([0.,1,0]);v=np.cross(g,up);c=g@up;K=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]]);G=np.eye(3)+K+K@K/(1+c)
def project(a):return np.array([k['fx']*a[0]/a[2]+k['ppx'],k['fy']*a[1]/a[2]+k['ppy']])
def rotation(e):
 x,y,z=np.radians(e);cx,sx,cy,sy,cz,sz=math.cos(x),math.sin(x),math.cos(y),math.sin(y),math.cos(z),math.sin(z)
 Rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]);Ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]);Rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
 return Ry@Rx@Rz
maxima={q:0. for q in ['object_transform','target_identity','local_observation','target_camera_prime','target_projection_px','marker_projection_px','input_projection_px','offset_update','circle_segment_lengths','shoulder_source']}
def error(key,a,b):
 value=float(np.max(np.abs(np.asarray(a)-np.asarray(b))));maxima[key]=max(maxima[key],value);assert value<1e-9,(key,value)
records=d['grasp']['records'];assert [x['frame'] for x in records]==list(range(600,741));rows={x['frame']:x for x in records}
for item in d['torso']['landmarks']:
 i=item['id'];name=meta['landmark_names'][str(i)];pt=raw.loc[100,[name+'_'+a for a in 'xyz']].to_numpy(float)
 error('input_projection_px',project(pt),item['source_uv_px']);assert int(raw.loc[100,name+'_src'])==0
assert d['torso']['quadrilateral_order']==[11,12,24,23] and d['torso']['basis_input_ids']==[24,23,12]
for i,rec in enumerate(records):
 idx=rec['frame'];R=np.asarray(rec['marker_rotation_leveled_world']);o=np.asarray(rec['marker_origin_leveled_world_m']);h=np.asarray(rec['object_local_estimate_m']);w=np.asarray(rec['estimated_wrist_leveled_world_m'])
 source_obj=obj.loc[idx,['unity_px','unity_py','unity_pz']].to_numpy(float);source_eul=obj.loc[idx,['unity_ex','unity_ey','unity_ez']].to_numpy(float)
 error('object_transform',o,G@source_obj);error('object_transform',R,G@rotation(source_eul));error('target_identity',w,o+R@h)
 target_prime=np.linalg.solve(M,G.T@w-t);error('target_camera_prime',target_prime,rec['right_wrist_target_camera_prime_m']);error('target_projection_px',project(F@target_prime),rec['wrist_estimate_uv_px'])
 marker_prime=np.linalg.solve(M,G.T@o-t);error('marker_projection_px',project(F@marker_prime),rec['marker_uv_px'])
 sh=filt.loc[idx,['right_shoulder_'+a for a in 'xyz']].to_numpy(float);error('shoulder_source',F@sh,rec['right_shoulder_camera_prime_m'])
 assert raw.loc[idx,'right_shoulder_src']==raw.loc[idx,'right_elbow_src']==0
 assert filt.loc[idx,'right_shoulder_flag']==filt.loc[idx,'right_elbow_flag']==0
 assert rec['holding']
 if rec['clean_offset_update']:
  pw=filt.loc[idx,['right_wrist_'+a for a in 'xyz']].to_numpy(float);wlevel=G@(M@(F@pw)+t);local=R.T@(wlevel-o)
  error('local_observation',local,rec['object_local_observation_m']);error('input_projection_px',project(pw),rec['wrist_input_uv_px'])
 else: assert rec['object_local_observation_m'] is None and rec['wrist_input_uv_px'] is None
 if i:
  prev=np.asarray(records[i-1]['object_local_estimate_m'])
  expected=prev*.98+np.asarray(rec['object_local_observation_m'])*.02 if rec['clean_offset_update'] else prev
  error('offset_update',h,expected)
 assert sha(Path('/tmp/defense_matched_r7')/f'frame_{idx:04d}.png')==rec['rgb_sha256']
for idx in [705,706,707]:
 assert raw.loc[idx,'right_wrist_src']==2 and not rows[idx]['clean_offset_update']
 assert rows[idx]['object_local_estimate_m']==rows[704]['object_local_estimate_m']
fractions=[]
for item in d['elbow_constraints']['records']:
 rr=rows[item['frame']];sh=np.asarray(rr['right_shoulder_camera_prime_m']);wr=np.asarray(rr['right_wrist_target_camera_prime_m']);l1=item['upper_arm_m'];l2=item['forearm_m'];distance=np.linalg.norm(wr-sh)
 assert item['reachable'] and abs(l1-l2)<=distance<=l1+l2
 assert item['selected_elbow'] is None and item['prior'] is None
 n=(wr-sh)/distance;center=sh+(l1*l1-l2*l2+distance*distance)/(2*distance)*n;radius=math.sqrt(max(0,l1*l1-np.linalg.norm(center-sh)**2));error('circle_segment_lengths',center,item['center_camera_prime_m']);error('circle_segment_lengths',radius,item['radius_m'])
 seed=np.array([0.,0,1]) if abs(n[2])<.8 else np.array([0.,1,0]);u=np.cross(n,seed);u/=np.linalg.norm(u);v=np.cross(n,u)
 for angle in np.linspace(0,2*np.pi,137):
  point=center+radius*(math.cos(angle)*u+math.sin(angle)*v);error('circle_segment_lengths',[np.linalg.norm(point-sh),np.linalg.norm(point-wr)],[l1,l2])
 fractions.append(distance/(l1+l2))
mapresults=[]
for asset in rpt['assets']:
 assert sha(asset['path'])==asset['sha256'] and sha(asset['poster'])==asset['poster_sha256']
 assert sha(asset['frame_map'])==asset['frame_map_sha256'];mapping=list(csv.DictReader(open(asset['frame_map'])))
 section='frame_journey' if asset['name']=='matched_frame_journey' else 'grasp';wanted=d[section]['output_source_frames']
 assert [int(row['source_frame']) for row in mapping]==wanted
 assert all(row['same_frame_both_panels']=='True' for row in mapping)
 assert len(mapping)==asset['frames'] and len(mapping)/asset['fps']==asset['duration_s']
 if section=='grasp':
  assert wanted[:210]==[idx for idx in range(600,705) for _ in range(2)]
  assert wanted[210:332]==[705]*122 and wanted[-62:]==[740]*62
 else:assert wanted[:150]==list(range(383,533)) and wanted[150:]==[533]*1170
 mapresults.append({'asset':asset['name'],'frames':len(mapping),'mapping':'PASS','sha256':asset['sha256']})
for tag in ['p_f0','o_f0']:assert int(d['frame_journey']['merger_record'][tag])==532
for tag in ['p_f1','o_f1']:assert int(d['frame_journey']['merger_record'][tag])==533
assert abs(d['frame_journey']['person_record']['time_s']-d['frame_journey']['source_time_s'])<1e-6
result={'status':'PASS','scope':'Independent matched-media source, algebra, projection, history and map review; no detector/solver rerun or new experiment',
 'reviewed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest_sha256':sha(manifest),'generator_sha256':sha(p/'anim/matched_evidence.py'),'generation_report_sha256':sha(report_path),
 'review_script_sha256':sha(__file__),'source_files_hash_checked':source_hashes,'records_checked':len(records),'all_right_shoulders_and_elbows_accepted':True,'wrist_depth_loss_frames':[705,706,707],'offset_freeze_exact':True,'maximum_absolute_residuals':maxima,
 'camera_distortion_coefficients':k['coeffs'],'two_sphere_trials_per_frame':137,'near_extension_fraction_range':[min(fractions),max(fractions)],'frames_above_98_percent':int(sum(x>.98 for x in fractions)),
 'constraints_only_not_runtime_recovery':True,'source_capture_and_render_tick_distinguished':True,'assets':mapresults,
 'limits':['Original bag extraction audit is relied upon; every selected cached RGB file was hash-checked here.','The recorded elbow is measured; ideal circles are endpoint constraints before runtime guards, not observed missing-elbow recovery.','Slide24 uses separately labelled illustrative geometry; its selected elbow is not a recovered R7 measurement.','All playback pauses and process stages are editorial, not measured latency.']}
(p/'review/MATCHED_INDEPENDENT_REVIEW.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: 141 matched frames; independent transforms/projections/local-offset update; 705-707 exact hold; all maps; 141 ideal circles')
print('maxima',maxima);print('near-extension',min(fractions),max(fractions),'count above98',sum(x>.98 for x in fractions))

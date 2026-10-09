from pathlib import Path
import json, subprocess, hashlib, shutil
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation

B=Path('/tmp/codex_solo_scene_20261005')
OLD=Path('/tmp/codex_fable_scene_repair_20261005_01/capture_native')
ROOT=Path('/home/luo/Desktop/bimanual-tracking')
SOURCE=OLD.parent/'pipeline/output/v2_integrate_dump_display.csv'
O=B/'movies';O.mkdir(exist_ok=True)
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
actual=pd.read_csv(SOURCE)
sel=pd.read_csv(OLD/'pairing.csv')
raw=pd.read_csv(ROOT/'presentation/defense_2026/media/provenance/v2_person_dump_r6b_full.csv')
raw=raw[(raw.frame>=269)&(raw.frame<=898)]
idx=np.searchsorted(actual.tau.to_numpy(),raw.time_s.to_numpy(),side='right')-1
assert len(sel)==630 and (sel.tick.to_numpy()==actual.tick.to_numpy()[idx]).all()
assert (sel.source_frame.to_numpy()==raw.frame.to_numpy()).all()
assert (sel.causal_age_s>=0).all()
regression={}
for f in ['unity_person_log.csv','unity_object_log.csv']:
 a=pd.read_csv(B/'runtime'/f).drop_duplicates('frame',keep='last').sort_values('frame')
 b=pd.read_csv(OLD/'runtime'/f).drop_duplicates('frame',keep='last').sort_values('frame')
 assert len(a)==len(b)==897 and a.columns.tolist()==b.columns.tolist()
 delta=np.max(np.abs(a.to_numpy(float)-b.to_numpy(float)),axis=0)
 regression[f]={k:float(v) for k,v in zip(a.columns,delta)}
 assert max(delta)<2e-5,(f,regression[f])
checks=[];poly=None
for tick in [0,250,500,750]:
 state=json.loads((B/'geometry_audit'/f'scene_tick{tick:05d}.json').read_text())
 verts=np.array([[v[k] for k in 'xyz'] for v in state['tableVertices']]);top=verts[:len(verts)//2]
 normal=np.cross(top[1]-top[0],top[2]-top[0]);normal/=np.linalg.norm(normal)
 assert abs(abs(normal[1])-1)<1e-6 and np.ptp(top[:,1])<1e-6
 if poly is None:poly=top
 else:assert np.max(abs(poly-top))<1e-7
 nodes={x['name']:x for x in state['nodes']}
 prev=json.loads((OLD/'geometry_audit'/f'scene_tick{tick:05d}.json').read_text())
 oldnodes={x['name']:x for x in prev['nodes']}
 wall=nodes['aruco_wall'];e=wall['euler'];rot=Rotation.from_euler('zxy',[e['z'],e['x'],e['y']],degrees=True).as_matrix()
 assert abs(rot[1,1])<1e-5 and abs(abs(rot[1,2])-1)<1e-5
 for kind in ['position','euler']:
  assert max(abs(wall[kind][k]-oldnodes['aruco_wall'][kind][k]) for k in 'xyz')<2e-5
 checks.append({'tick':tick,'table_y_range_m':float(np.ptp(top[:,1])),'wall_normal_world':rot[:,1].tolist(),'wall_marker_pose_retained':True})
plog=pd.read_csv(B/'runtime/unity_person_log.csv').drop_duplicates('frame',keep='last')
h=ConvexHull(poly[:,[0,2]]);distance=plog[['hip_x','hip_z']].to_numpy()@h.equations[:,:2].T+h.equations[:,2]
inside=int(np.all(distance<=1e-7,axis=1).sum())
assert inside==0,inside
U=B/'paired_unity';U.mkdir(exist_ok=True)
for i,r in enumerate(sel.itertuples()):
 dest=U/f'f{i:05d}.png';src=B/'r5_frames'/f'f{int(r.tick):05d}.png'
 assert src.exists()
 if not dest.exists():dest.symlink_to(src)
fps=(len(sel)-1)/(sel.time_s.iloc[-1]-sel.time_s.iloc[0])
unity=O/'unity.mp4';rgb=OLD/'movies/fable_repaired_rgb_269_898.mp4';movie=O/'p38_corrected.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(fps),'-i',str(U/'f%05d.png'),'-frames:v','630','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-threads','4','-movflags','+faststart',str(unity)],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(rgb),'-i',str(unity),'-filter_complex','[0:v]scale=960:720:flags=lanczos[l];[1:v]scale=960:720:flags=lanczos[r];[l][r]hstack=inputs=2[v]','-map','[v]','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-threads','4','-movflags','+faststart',str(movie)],check=True)
poster=O/'p38_corrected.png'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(movie),'-vf','select=eq(n\\,231)','-frames:v','1',str(poster)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(movie)],text=True))['streams'][0]
assert probe['width']==1920 and probe['height']==720 and int(probe['nb_read_frames'])==630
manifest={'source':str(SOURCE),'source_sha256':hashfile(SOURCE),'frame_count':897,'paired_frame_count':630,'source_rgb_window':[269,898],'pairing_rule':'Latest displayed causal tau <= RGB timestamp','causal_age_s':{'min':float(sel.causal_age_s.min()),'max':float(sel.causal_age_s.max())},'table_geometry':json.loads((B/'scene_geometry.json').read_text()),'calibration_sha256':hashfile(ROOT/'v2/output/scene_calibration_r6b_v2.json'),'geometry_checks':checks,'pelvis_projection_inside_table_count':inside,'pose_regression_max_differences':regression,'camera':{'position':[.90,1.55,-.90],'target':[0,1.08,.75],'vertical_fov_degrees':46,'resolution':[1440,1080]},'movie':dict(probe,sha256=hashfile(movie)),'scope':'Native Unity replay of the same causal data; table mesh bounds and wall mesh span corrected; camera changed for visibility; no change to recorded body or object data; no new throughput benchmark.'}
(O/'delivery_manifest.json').write_text(json.dumps(manifest,indent=2));shutil.copy2(OLD/'pairing.csv',O/'pairing.csv')
print(json.dumps({'movie':str(movie),'sha256':hashfile(movie),'frames':630,'pelvis_inside_table':inside,'max_pose_difference':max(max(x.values()) for x in regression.values())},indent=2),flush=True)

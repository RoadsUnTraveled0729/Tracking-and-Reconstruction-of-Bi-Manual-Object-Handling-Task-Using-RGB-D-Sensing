import hashlib, importlib.util, json, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[5]
sys.path[:0]=[str(ROOT/'eval/failure'),str(ROOT/'eval/common'),str(ROOT/'v1/kinematics')]
import numpy as np
import pandas as pd
import paths,recovery_core as rc,run_recovery as rr
out=Path('/tmp/m03_historical_rail');out.mkdir(exist_ok=True)
rev='d2544cd'
old=subprocess.check_output(['git','show',rev+':v1/kinematics/occlusion_ext.py'],cwd=ROOT)
modulefile=out/'occlusion_ext_d2544cd.py';modulefile.write_bytes(old)
spec=importlib.util.spec_from_file_location('historical_solver_m03',modulefile)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
rc.RobustChainSolver=mod.RobustChainSolver
inp=rc.build_inputs(paths.R6B_STEM)
res=rc.run_variant(inp,'recovery')
reference=rr.write_variant(out,'recovery',inp['t'],res)
live=pd.read_csv(ROOT/'v2/output/v2_person_dump_r6b_full.csv')
ref=pd.read_csv(reference)
m=live.merge(ref,on='frame',suffixes=('_l','_r'))
la=m[[f'a{i}' for i in range(13)]].to_numpy(float);ra=m[rr.ANGLE_COLS].to_numpy(float)
lv=(m['mask'].to_numpy(int)&14)==14;rv=(m['live_mask'].to_numpy(int)&14)==14
for i in range(1,4):
 lv &= m[f'tag_{i}_l'].to_numpy(int)==0
 rv &= m[f'tag_{i}_r'].to_numpy(int)==0
clean=lv&rv
rows=[]
for k in range(-10,11):
 ix=slice(k,None) if k>0 else slice(None,k) if k<0 else slice(None)
 jx=slice(None,-k) if k>0 else slice(-k,None) if k<0 else slice(None)
 e=np.abs((la[ix]-ra[jx]+180)%360-180)
 oldmask=clean[ix];newmask=lv[ix]&rv[jx]
 d={'lag':k,'old_count':int(oldmask.sum()),'new_count':int(newmask.sum()),'old_pooled_median':float(np.median(e[oldmask,3:8])),'new_pooled_median':float(np.median(e[newmask,3:8]))}
 for policy,mask in [('old',oldmask),('new',newmask)]:
  d[policy+'_per_angle']={rr.ANGLE_COLS[i]:{'median':float(np.median(e[mask,i])),'p95':float(np.percentile(e[mask,i],95))} for i in range(3,8)}
  d[policy+'_worst_group_median']=max(float(np.median(e[mask,3:6])),float(np.median(e[mask,6:8])))
  d[policy+'_worst_group_p95']=max(float(np.percentile(e[mask,3:6],95)),float(np.percentile(e[mask,6:8],95)))
 rows.append(d)
report={'warning':'Historical reconstruction, not untouched original reference. d2544cd solver with current cached preprocessing inputs. Historical metric agreement is checked, not assumed.', 'revision':rev,'solver_sha256':hashlib.sha256(old).hexdigest(),'reference_file':str(reference),'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),'lags':rows}
(out/'report.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='lags'},indent=2))
for policy in ['old','new']:
 best=min(rows,key=lambda d:d[policy+'_pooled_median']);print(policy+' best '+json.dumps(best))

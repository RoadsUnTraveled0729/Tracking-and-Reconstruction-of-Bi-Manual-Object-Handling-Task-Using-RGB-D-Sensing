"""Archive and verify a complete R7 capture; stop only this harness's processes."""
from pathlib import Path
import json,time,os,signal,shutil,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=Path('/tmp/defense_axes_capture');ALIAS=sys.argv[1] if len(sys.argv)>1 else 'r7';OUT=HERE/ALIAS;FRAMES=BASE/'r5_frames'
sys.path.insert(0,str(ROOT/'eval'));from common import paths
STEM=next(k for k,v in paths.ALIAS.items() if v==ALIAS)
N=sum(1 for _ in (OUT/'integrated_stream.csv').open())-1
required=set(range(N-1));deadline=time.monotonic()+600
while True:
 got={int(p.stem[1:])for p in FRAMES.glob('f*.png')}
 missing=required-got
 print('Capture coverage',len(got),'missing required',len(missing),flush=True)
 if not missing:break
 if time.monotonic()>deadline:raise RuntimeError('Incomplete frame coverage')
 time.sleep(10)
(BASE/'r5_autoplay_stop').write_text('stop\n');(BASE/'r5_autoplay_quit').write_text('quit\n')
pids=json.loads((OUT/'processes.json').read_text())
for _ in range(30):
 try:os.kill(pids['unity'],0)
 except ProcessLookupError:break
 time.sleep(1)
os.kill(pids['sender'],signal.SIGTERM)
for name in ['axes_matrices.csv','unity_person_log.csv','unity_object_log.csv','rig_dimensions.csv','rig_sizing_used.txt']:
 shutil.copy2(BASE/'runtime'/name,OUT/name)
(OUT/'stills').mkdir(exist_ok=True)
for f in [100,190,249,600,705,750,950,1042,1259,1497]:shutil.copy2(FRAMES/f'f{f:05d}.png',OUT/'stills'/f'f{f:05d}.png')
py=sys.executable
sizing=subprocess.run([py,str(HERE/'check_rig_sizing_isolated.py'),'--sizing',str(ROOT/f'eval/reports/{ALIAS}_rig_sizing.json'),'--rig-dimensions',str(OUT/'rig_dimensions.csv'),'--used',str(OUT/'rig_sizing_used.txt')],capture_output=True,text=True)
(OUT/'check_rig_sizing.txt').write_text(sizing.stdout+sizing.stderr)
axes=subprocess.run([py,str(HERE/'validate_axes_capture.py'),str(OUT)],capture_output=True,text=True)
(OUT/'axes_validation_stdout.txt').write_text(axes.stdout+axes.stderr)
check=subprocess.run([py,str(ROOT/'eval/unity_check/check_unity_log.py'),'--stem',STEM,'--out',str(OUT),'--person-log',str(OUT/'unity_person_log.csv'),'--object-log',str(OUT/'unity_object_log.csv'),'--frames-dir',str(FRAMES)],capture_output=True,text=True)
print(check.stdout,flush=True)
report={'captured_frames':len(got),'required_frames':N-1,'missing':sorted(missing),'axes_validator_exit':axes.returncode,'sizing_validator_exit':sizing.returncode,'original_unity_checker_exit':check.returncode,'note':'Original Unity checker includes a recording-specific R5 failure-concentration assertion. Preserve its result; inspect applicability for R7 rather than changing its expected outcome.','rendering':f'Fresh {ALIAS} replay, all five recording-specific dimensions, saved recovery and existing display smoother; illustrative model axes visible through mesh.'}
(OUT/'capture_summary.json').write_text(json.dumps(report,indent=2)+'\n')
assert sizing.returncode==axes.returncode==0
print('Final capture archived',flush=True)

"""Launch a separate editor, scoped IPC and unchanged frozen replay sender."""
from pathlib import Path
import subprocess,sys,os,json,time,shutil,urllib.request
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; BASE=Path('/tmp/defense_axes_capture')
ALIAS=sys.argv[1] if len(sys.argv)>1 else 'r7'
assert ALIAS in ('r5','r7')
sys.path.insert(0,str(ROOT/'eval'));from common import paths
STEM=next(k for k,v in paths.ALIAS.items() if v==ALIAS)
OUT=HERE/ALIAS;OUT.mkdir(exist_ok=True)
# Never share an editor or confuse an earlier capture's PNGs with this run.
processes=subprocess.check_output(['ps','-eo','pid,args'],text=True)
if any('Editor/Unity -projectPath '+str(BASE/'Unity') in line for line in processes.splitlines()):
 raise SystemExit('Capture editor already running; leave it untouched.')
for dirname in ['r5_frames','runtime']:
 directory=BASE/dirname
 if directory.exists() and any(directory.iterdir()):
  directory.rename(BASE/(dirname+'_previous_'+str(time.time_ns())))
 directory.mkdir(exist_ok=True)

sys.path.insert(0,str(ROOT/'eval/unity_check'))
from make_rig_sizing import write_flag
write_flag(ROOT/f'eval/reports/{ALIAS}_rig_sizing.json',BASE/'r5_rig_sizing')
for name in ['r5_capture_on','r5_autoplay_on']:(BASE/name).write_text('defense\n')
for name in ['r5_autoplay_stop','r5_autoplay_quit']:(BASE/name).unlink(missing_ok=True)
try:
 req=urllib.request.Request('http://127.0.0.1:8080/mcp',headers={'Accept':'application/json, text/event-stream'})
 with urllib.request.urlopen(req,timeout=2) as r: mcp={'status':r.status}
except Exception as e:mcp={'status':'unavailable','detail':str(e)}
(OUT/'mcp_probe.json').write_text(json.dumps(mcp,indent=2)+'\n')
cmd=[sys.executable,str(ROOT/'eval/unity_check/send_scene_r5.py'),'--stem',STEM,'--angles-csv',str(ROOT/f'eval/output/recovery_{ALIAS}/angles_recovery.csv'),'--scene-shm','/dev/shm/defense_axes_aruco_scene','--shm','/dev/shm/defense_axes_integrated_scene','--speed','0.25','--loop','--dump-csv',str(OUT/'integrated_stream.csv')]
sender=subprocess.Popen(cmd,stdout=open(OUT/'sender.log','w'),stderr=subprocess.STDOUT,start_new_session=True)
for i in range(90):
 if Path('/dev/shm/defense_axes_integrated_scene').exists():break
 if sender.poll() is not None:raise RuntimeError('Sender exited')
 time.sleep(1)
env=dict(os.environ,DISPLAY=os.environ.get('DISPLAY',':0'))
unity=subprocess.Popen([str(Path.home()/'Unity/Hub/Editor/6000.3.19f1/Editor/Unity'),'-projectPath',str(BASE/'Unity'),'-logFile',str(OUT/'editor.log')],env=env,stdout=open(OUT/'editor_stdout.log','w'),stderr=subprocess.STDOUT,start_new_session=True)
(OUT/'processes.json').write_text(json.dumps({'sender':sender.pid,'unity':unity.pid,'sender_command':cmd},indent=2)+'\n')
print('Launched isolated editor',unity.pid,'sender',sender.pid,flush=True)

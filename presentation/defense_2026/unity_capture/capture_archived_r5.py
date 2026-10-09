"""Isolated capture of the archived R5 display packet stream."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,signal,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=Path('/tmp/defense_axes_capture');OUT=HERE/'r5_archived';PROJECT=BASE/'Unity'
STEM='recording_20260825_222315';SOURCE=ROOT/'eval/output/unity_check_r5/integrated_stream.csv';PY=sys.executable
p=argparse.ArgumentParser();p.add_argument('action',choices=['launch','finish']);a=p.parse_args();OUT.mkdir(exist_ok=True)
if a.action=='launch':
 ps=subprocess.check_output(['ps','-eo','pid,args'],text=True)
 assert not any('Editor/Unity -projectPath '+str(PROJECT) in line for line in ps.splitlines()),'Isolated editor already running'
 assert (PROJECT/'Assets/Scripts/DefenseAxes.cs').exists(),'Run the documented original isolated project preparation first'
 for name in ['runtime','r5_frames']:
  d=BASE/name
  if d.exists() and any(d.iterdir()):d.rename(BASE/(name+'_before_archived_'+str(time.time_ns())))
  d.mkdir(exist_ok=True)
 sizing={'stem':STEM,'segment_lengths_m':{'upper_arm_R':.256,'forearm_R':.252,'upper_arm_L':.262,'forearm_L':.247,'torso':.479},'source':'eval/reports/r5_rig_sizing.json capture_note: archived configuration, not current recovery sizing'}
 (OUT/'archived_rig_sizing.json').write_text(json.dumps(sizing,indent=2)+'\n')
 sys.path.insert(0,str(ROOT/'eval/unity_check'));from make_rig_sizing import write_flag
 write_flag(OUT/'archived_rig_sizing.json',BASE/'r5_rig_sizing')
 for name in ['r5_capture_on','r5_autoplay_on']:(BASE/name).write_text('archived replay\n')
 for name in ['r5_autoplay_stop','r5_autoplay_quit','r5_trails.txt']:(BASE/name).unlink(missing_ok=True)
 shutil.copyfile(SOURCE,OUT/'integrated_stream.csv')
 logs=BASE/'private_archived_logs';logs.mkdir(exist_ok=True)
 sender=subprocess.Popen([PY,str(HERE/'replay_archived_packets.py'),'--loop'],stdout=(logs/'sender.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True)
 time.sleep(3)
 env=dict(os.environ,DISPLAY=os.environ.get('DISPLAY',':0'))
 unity=subprocess.Popen([str(Path.home()/'Unity/Hub/Editor/6000.3.19f1/Editor/Unity'),'-projectPath',str(PROJECT),'-logFile',str(logs/'editor.log')],stdout=(logs/'editor_stdout.log').open('w'),stderr=subprocess.STDOUT,env=env,start_new_session=True)
 (logs/'processes.json').write_text(json.dumps({'unity':unity.pid,'sender':sender.pid},indent=2))
 print('Launched',unity.pid,sender.pid)
else:
 frames=BASE/'r5_frames';required=set(range(2098));actual={int(p.stem[1:])for p in frames.glob('f*.png')}
 assert required<=actual,f'Capture incomplete: {len(actual)} frames'
 (BASE/'r5_autoplay_stop').write_text('stop\n');(BASE/'r5_autoplay_quit').write_text('quit\n')
 ids=json.loads((BASE/'private_archived_logs/processes.json').read_text())
 os.kill(ids['sender'],signal.SIGTERM)
 for _ in range(30):
  try:os.kill(ids['unity'],0)
  except ProcessLookupError:break
  time.sleep(1)
 for name in ['axes_matrices.csv','unity_person_log.csv','unity_object_log.csv','rig_dimensions.csv','rig_sizing_used.txt']:shutil.copyfile(BASE/'runtime'/name,OUT/name)
 (OUT/'stills').mkdir(exist_ok=True)
 for f in [900,950,1042,1259,1380,1497,1520,1620,1649]:shutil.copyfile(frames/f'f{f:05d}.png',OUT/'stills'/f'f{f:05d}.png')
 commands=[([PY,str(HERE/'check_rig_sizing_isolated.py'),'--sizing',str(OUT/'archived_rig_sizing.json'),'--rig-dimensions',str(OUT/'rig_dimensions.csv'),'--used',str(OUT/'rig_sizing_used.txt')],'check_rig_sizing.txt'),([PY,str(ROOT/'eval/unity_check/check_unity_log.py'),'--stem',STEM,'--out',str(OUT),'--person-log',str(OUT/'unity_person_log.csv'),'--object-log',str(OUT/'unity_object_log.csv'),'--frames-dir',str(frames)],'check_unity_log_stdout.txt')]
 for cmd,name in commands:
  r=subprocess.run(cmd,capture_output=True,text=True);(OUT/name).write_text(r.stdout+r.stderr);print(name,r.returncode)
 subprocess.run(['ffmpeg','-y','-v','error','-framerate','30','-start_number','0','-i',str(frames/'f%05d.png'),'-frames:v','2098','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-threads','2','-movflags','+faststart',str(OUT/'Archived_Unity_R5_Model_Axes.mp4')],check=True)
 print('Finished archived capture')

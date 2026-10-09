from pathlib import Path
import subprocess,os,time,json
B=Path('/tmp/codex_solo_scene_20261005')
p=B/'Unity/Assets/Scripts/EvalFrameDump.cs'
s=p.read_text();a=s.index('        defenceCamera = source;');b=s.index('        Vector3 target =',a)
s=s[:a]+'''        defenceCamera = new GameObject("DefenceSceneCamera").AddComponent<Camera>();
        defenceCamera.CopyFrom(source);
        defenceCamera.enabled = false;
        defenceCamera.rect = new Rect(0,0,1,1);
        defenceCamera.aspect = 4f/3f;
        defenceCamera.ResetProjectionMatrix();
        defenceCamera.fieldOfView = 46f;
        defenceCamera.transform.position = new Vector3(0.90f,1.55f,-0.90f);
        defenceCamera.transform.LookAt(new Vector3(0f,1.08f,0.75f),Vector3.up);
''' +s[b:]
p.write_text(s)
for old in ['r5_frames','runtime','geometry_audit']:
 (B/old).rename(B/(old+'_sensor'));(B/old).mkdir()
for f in ['r5_autoplay_stop','r5_autoplay_quit']:(B/f).unlink(missing_ok=True)
os.utime(B/'r5_rig_sizing',None)
# Reinitialise the first actual input before launching a fresh engine session.
import sys,csv,mmap
sys.path.insert(0,str(B));from capture_scene import publish,SOURCE,PREFIX
f=Path('/dev/shm/'+PREFIX+'integrated_scene').open('r+b');mm=mmap.mmap(f.fileno(),108)
publish(mm,list(csv.DictReader(SOURCE.open()))[0],40000);mm.close();f.close()
proc=subprocess.Popen(['/home/luo/Unity/Hub/Editor/6000.3.19f1/Editor/Unity','-projectPath',str(B/'Unity'),'-logFile',str(B/'editor_scene.log')],env=dict(os.environ,DISPLAY=':0'),stdout=(B/'editor_scene_stdout.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True)
print('Scene view launched',proc.pid,flush=True)

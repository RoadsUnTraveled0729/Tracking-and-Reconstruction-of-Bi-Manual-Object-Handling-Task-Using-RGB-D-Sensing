"""Copy frozen Unity project and add isolated capture instrumentation."""
from pathlib import Path
import shutil,subprocess,json,hashlib
ROOT=Path(__file__).resolve().parents[3]
BASE=Path('/tmp/defense_axes_capture'); PROJECT=BASE/'Unity'; HERE=Path(__file__).resolve().parent
BASE.mkdir(exist_ok=True);(BASE/'runtime').mkdir(exist_ok=True);(BASE/'frames').mkdir(exist_ok=True)
PROJECT.mkdir(exist_ok=True)
for name in ['Assets','Packages','ProjectSettings','Library']:
 if not (PROJECT/name).exists():subprocess.run(['cp','-a','--reflink=auto',str(ROOT/'Unity'/name),str(PROJECT/name)],check=True)
records=[]
for src in (ROOT/'Unity/Assets').rglob('*.cs'):
 text=src.read_text();orig=text
 text=text.replace('/home/luo/Desktop/New_SandBox/v1/integration/output',str(BASE/'runtime'))
 text=text.replace('/home/luo/Desktop/New_SandBox/v1/kinematics/output',str(BASE/'runtime'))
 text=text.replace('/home/luo/Desktop/New_SandBox/v1/aruco/output/unity_aruco_log.csv',str(BASE/'runtime/unity_aruco_log.csv'))
 text=text.replace('/tmp/r5_',str(BASE)+'/r5_').replace('/tmp/r4_',str(BASE)+'/r4_')
 text=text.replace('/dev/shm/integrated_scene','/dev/shm/defense_axes_integrated_scene').replace('/dev/shm/aruco_scene','/dev/shm/defense_axes_aruco_scene')
 if src.name=='IntegratedSceneReceiver.cs':
  text=text.replace('rigRoot.position += target - hip.position;','rigRoot.position += target - hip.position;\n        DefenseAxes.Update(frame,t,hip,upperArm,forearm,lUpperArm,lForearm,qA*qRoot,qA*qRoot*qSh,qA*qRoot*qShL);')
 if src.name=='EvalFrameDump.cs':
  text=text.replace('int w = sensorPov ? 640 : 1280;','int w = sensorPov ? 1440 : 1920;').replace('int h = sensorPov ? 480 : 720;','int h = sensorPov ? 1080 : 1080;')
  text=text.replace('cam.Render();','DefenseAxes.Record(cam,index,rt.width,rt.height);\n        cam.Render();')
 (PROJECT/src.relative_to(ROOT/'Unity')).write_text(text)
 if text!=orig:records.append({'source':str(src.relative_to(ROOT)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
shutil.copy2(HERE/'DefenseAxes.cs',PROJECT/'Assets/Scripts/DefenseAxes.cs')
shutil.copy2(HERE/'AxesOverlay.shader',PROJECT/'Assets/Shaders/AxesOverlay.shader')
(HERE/'project_copy_manifest.json').write_text(json.dumps({'project':str(PROJECT),'modified_copies':records,'originals_unchanged':True},indent=2)+'\n')
print(PROJECT)

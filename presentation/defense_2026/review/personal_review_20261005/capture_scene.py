from pathlib import Path
import csv, json, mmap, os, shutil, struct, subprocess, sys, time, difflib, hashlib

OLD=Path('/tmp/codex_fable_scene_repair_20261005_01/capture_native')
BASE=Path('/tmp/codex_solo_scene_20261005')
PROJECT=BASE/'Unity'
SOURCE=Path('/tmp/codex_fable_scene_repair_20261005_01/pipeline/output/v2_integrate_dump_display.csv')
ROOT=Path('/home/luo/Desktop/bimanual-tracking')
PREFIX='codex_solo_scene_'

def publish(mm,r,seq):
    vals=[int(r['tick']),float(r['tau'])]+[float(r['pel_'+c]) for c in 'xyz']+[float(r['a'+str(i)]) for i in range(13)]+[float(r[c]) for c in ('ox','oy','oz','oex','oey','oez')]+[int(r[c]) for c in ('mask','olive')]
    mm[4:8]=struct.pack('<I',seq+1);mm[8:]=struct.pack('<if3f13f3f3fHH',*vals);mm[:4]=struct.pack('<I',0x31495350);mm[4:8]=struct.pack('<I',seq+2)

def prepare():
    assert not PROJECT.exists()
    PROJECT.mkdir(parents=True)
    for name in ['Assets','Packages','ProjectSettings','Library']:
        subprocess.run(['cp','-a','--reflink=auto',str(OLD/'Unity'/name),str(PROJECT/name)],check=True)
    for folder in ['runtime','r5_frames','patches']: (BASE/folder).mkdir(exist_ok=True)
    geometry=json.loads((BASE/'scene_geometry.json').read_text())
    verts='\n'.join('        new Vector3('+','.join(f'{v:.9f}f' for v in p)+'),' for p in geometry['table_corners_local_m'])
    for p in (PROJECT/'Assets').rglob('*.cs'):
        orig=p.read_text();s=orig.replace(str(OLD),str(BASE)).replace('codex_fable_capture02_',PREFIX)
        if p.name=='ArucoSceneReceiver.cs':
            a=s.index('    static readonly Vector3[] MeasuredTablePolygon');b=s.index('    void BuildMeasuredTableTop()',a)
            s=s[:a]+'    static readonly Vector3[] MeasuredTablePolygon = new Vector3[] {\n'+verts+'\n    };\n'+s[b:]
            s=s.replace('        // Floor is the existing decorative standard desk height.', '''        // The same table plane and image-derived straight boundaries.
        // Legs are display geometry at the existing standard table height.
        for(int i=0;i<MeasuredTablePolygon.Length;i++){
            Vector3 corner=Vector3.Lerp(MeasuredTablePolygon[i],center,0.12f);
            Quaternion legRot=Quaternion.FromToRotation(Vector3.up,g);
            Slab(world,"desk_leg_"+i,corner-g*(DeskThick+LegH/2f),legRot,
                 new Vector3(0.035f,LegH,0.035f),LegCol);
        }
        // Floor is the existing decorative standard desk height.''')
            s=s.replace('new Vector3(0f, -(WallThick / 2f + 0.004f), (0.8f - markerHeight) / 2f)',
                'new Vector3(Vector3.Dot(center-wallNode.localPosition,wallNode.localRotation*Vector3.right), -(WallThick / 2f + 0.004f), (0.8f - markerHeight) / 2f)')
        if orig!=s:
            p.write_text(s)
            if p.name in ['ArucoSceneReceiver.cs','EvalFrameDump.cs']:
                (BASE/'patches'/f'{p.name}.patch').write_text(''.join(difflib.unified_diff(orig.splitlines(True),s.splitlines(True))))
    cal=json.loads((ROOT/'v2/output/scene_calibration_r6b_v2.json').read_text()); vals=[]
    for name in ['desk','wall','camera']:
        vals+=cal['poses_world'][name]['unity_position']+cal['poses_world'][name]['unity_euler_zxy_deg']
    g=cal['scene_geometry'];vals+=g['gravity_up_unity']+[g['origin_above_tabletop_m'],g['object_cube_size_m'],g['sensor_fov_y_deg']]
    Path('/dev/shm/'+PREFIX+'aruco_scene').write_bytes(struct.pack('<I24f',0x33425350,*vals))
    sizes=json.loads((ROOT/'eval/reports/r6b_rig_sizing.json').read_text())
    (BASE/'r5_rig_sizing').write_text('stem='+sizes['stem']+'\n'+''.join(f'{k}={v}\n' for k,v in sizes['segment_lengths_m'].items()))
    for f in ['r5_capture_on','r5_autoplay_on']:(BASE/f).write_text('scene correction\n')
    f=Path('/dev/shm/'+PREFIX+'integrated_scene').open('w+b');f.truncate(108);mm=mmap.mmap(f.fileno(),108)
    rows=list(csv.DictReader(SOURCE.open()));publish(mm,rows[0],0);mm.close();f.close()
    proc=subprocess.Popen(['/home/luo/Unity/Hub/Editor/6000.3.19f1/Editor/Unity','-projectPath',str(PROJECT),'-logFile',str(BASE/'editor.log')],env=dict(os.environ,DISPLAY=':0'),stdout=(BASE/'editor_stdout.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True)
    (BASE/'manifest.json').write_text(json.dumps({'unity_pid':proc.pid,'status':'prepared','source_csv':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'geometry':geometry},indent=2))
    print('Prepared Unity scene',proc.pid,flush=True)

def capture():
    deadline=time.time()+240
    while not (BASE/'r5_frames/f00000.png').exists():
        if time.time()>deadline:raise RuntimeError('No initial frame; inspect editor.log')
        time.sleep(.2)
    f=Path('/dev/shm/'+PREFIX+'integrated_scene').open('r+b');mm=mmap.mmap(f.fileno(),108)
    rows=list(csv.DictReader(SOURCE.open()))
    for i,r in enumerate(rows):
        publish(mm,r,20000+2*i);deadline=time.time()+10
        while not (BASE/'r5_frames'/f'f{i:05d}.png').exists():
            if time.time()>deadline:raise RuntimeError('Missing frame '+str(i))
            time.sleep(.01)
        if i%150==0:print('Captured',i,flush=True)
    (BASE/'r5_autoplay_stop').write_text('stop\n');(BASE/'r5_autoplay_quit').write_text('quit\n')
    mm.close();f.close()
    manifest=json.loads((BASE/'manifest.json').read_text());manifest.update(status='captured',frame_count=len(rows));(BASE/'manifest.json').write_text(json.dumps(manifest,indent=2));print('Captured all',len(rows),flush=True)

if __name__=='__main__':
    {'prepare':prepare,'capture':capture}[sys.argv[1]]()

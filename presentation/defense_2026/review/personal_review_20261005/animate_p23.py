"""Same-frame two-sphere geometry, derived from recorded endpoints.

The directional prior is a teaching derivation from preceding usable filtered
shoulder/elbow observations, using the implementation's normalized EMA (0.3).
It is not a logged missing-elbow recovery result. Original clip remains intact.
"""
from pathlib import Path
import csv,json,subprocess,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont

B=Path(__file__).resolve().parent
D=json.loads((B/'p23_geometry_source.json').read_text())
records={r['frame']:r for r in D['grasp']['records']}
frame_map=D['grasp']['output_source_frames']
F='/Users/luolanqing/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/fonts/DejaVuSans.ttf'
fonts={n:ImageFont.truetype(F,n) for n in [30,34,38,42]}
WHITE='#FFFFFF';GRAY='#A8A8A8';GREEN='#64D895';BLUE='#83B7FF';AMBER='#F2BE60';PURPLE='#B891FF'
prior={};memory=None
unit=lambda a:a/np.linalg.norm(a)
for row in csv.DictReader((B/'p23_landmarks_filtered.csv').open()):
 k=int(row['frame'])
 if k>740:break
 if k>=600:prior[k]=None if memory is None else memory.copy()
 try:
  s=np.array([float(row['right_shoulder_'+a]) for a in 'xyz'])*[1,-1,1]
  e=np.array([float(row['right_elbow_'+a]) for a in 'xyz'])*[1,-1,1]
  usable=all(int(row[n+'_flag'])==0 for n in ['right_shoulder','right_elbow'])
  if usable and np.isfinite([s,e]).all():
   u=unit(e-s);memory=u if memory is None else unit(.7*memory+.3*u)
 except (ValueError,ZeroDivisionError):pass

theta=np.linspace(0,2*np.pi,181)
projection=np.array([[.91,.16,.35],[.05,-.90,.38]])
projection[0]=unit(projection[0])
projection[1]=unit(projection[1]-np.dot(projection[1],projection[0])*projection[0])
origin=np.array([520.,963.]);scale=720.
def project(q):return np.asarray(q)@projection.T*scale+origin
def line(draw,points,color,width=3):draw.line([tuple(p) for p in project(points)],fill=color,width=width)
def text(draw,xy,t,size=34,color=WHITE,anchor=None):draw.text(xy,t,font=fonts[size],fill=color,anchor=anchor)
def dot(draw,p,color,rad=8):
 x,y=project(p);draw.ellipse((x-rad,y-rad,x+rad,y+rad),fill=color)
def arrow(draw,a,b,color):
 aa,bb=project(np.array([a,b]));draw.line([tuple(aa),tuple(bb)],fill=color,width=5)
 u=unit(bb-aa);v=np.array([-u[1],u[0]])
 draw.polygon([tuple(bb),tuple(bb-17*u+7*v),tuple(bb-17*u-7*v)],fill=color)

geometry={};residuals=[]
for k,r in records.items():
 s=np.array(r['right_shoulder_camera_prime_m']);w=np.array(r['right_wrist_target_camera_prime_m'])
 l1=r['segment_lengths_m']['upper_arm_R'];l2=r['segment_lengths_m']['forearm_R']
 dist=np.linalg.norm(w-s);b=(w-s)/dist
 e1=unit(np.cross(b,np.array([1.,0,0]) if abs(b[0])<.9 else np.array([0.,1,0])))
 e2=np.cross(b,e1)
 a=(l1*l1-l2*l2+dist*dist)/(2*dist);rho=np.sqrt(max(0,l1*l1-a*a))
 circle=np.column_stack([np.full(len(theta),a),rho*np.cos(theta),rho*np.sin(theta)])
 mem=prior[k];assert mem is not None
 m=np.array([mem@b,mem@e1,mem@e2]);perp=np.array([0.,m[1],m[2]])
 selected=np.array([a,0,0])+rho*unit(perp)
 error=max(abs(np.linalg.norm(selected)-l1),abs(np.linalg.norm(selected-[dist,0,0])-l2))
 error=max(error,np.max(np.abs(np.linalg.norm(circle,axis=1)-l1)),np.max(np.abs(np.linalg.norm(circle-[dist,0,0],axis=1)-l2)))
 assert error<1e-12;residuals.append(float(error))
 geometry[k]=(float(dist),l1,l2,circle,m,selected,float(rho))

ff='/opt/homebrew/bin/ffmpeg'
dec=subprocess.Popen([ff,'-v','error','-i',str(B/'p23_media.mp4'),'-vf','crop=896:672:272:86','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen([ff,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1440x1200','-r','30','-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(B/'p23_synchronized_geometry.mp4')],stdin=subprocess.PIPE)
for i,k in enumerate(frame_map):
 raw=dec.stdout.read(896*672*3);assert len(raw)==896*672*3,(i,len(raw))
 im=Image.new('RGB',(1440,1200),'black');im.paste(Image.frombytes('RGB',(896,672),raw),(272,62));dr=ImageDraw.Draw(im)
 text(dr,(272,9),'Recorded RGB',38)
 text(dr,(1168,12),f'Frame {k}',34,GRAY,'ra')
 text(dr,(40,754),'Two-length geometry',38)
 text(dr,(1390,758),'Same frame',34,GRAY,'ra')
 dist,l1,l2,circle,m,selected,rho=geometry[k]
 # Flat circular outlines keep the two length constraints readable.
 # The candidate locus retains the original endpoint-aligned projection.
 for center,radius,color in [(np.zeros(3),l1,GREEN),(np.array([dist,0,0]),l2,BLUE)]:
  x,y=project(center);rr=radius*scale
  dr.ellipse((x-rr,y-rr,x+rr,y+rr),outline=color,width=3)
 line(dr,[[0,0,0],[dist,0,0]],'#606060',2)
 line(dr,circle,AMBER,6)
 arrow(dr,np.zeros(3),m*.17,PURPLE)
 line(dr,[[0,0,0],selected,[dist,0,0]],WHITE,6)
 for p,col in [(np.zeros(3),WHITE),(np.array([dist,0,0]),WHITE),(selected,AMBER)]:dot(dr,p,col)
 # Fixed label regions stay clear of the moving geometric evidence.
 text(dr,(35,825),'Upper arm',34,GREEN);text(dr,(35,868),'L1 = 24.1 cm',30,GREEN)
 text(dr,(1180,825),'Forearm',34,BLUE);text(dr,(1180,868),'L2 = 23.3 cm',30,BLUE)
 text(dr,(35,1000),'Remembered',30,PURPLE);text(dr,(35,1040),'direction',30,PURPLE)
 text(dr,(1180,1000),'Candidate',30,AMBER);text(dr,(1180,1040),'circle',30,AMBER)
 text(dr,(520,1160),'Shoulder',30,WHITE,'mm')
 wp=project([dist,0,0]);text(dr,(wp[0],1160),'Wrist target',30,WHITE,'mm')
 # The orange point is a direction-guided geometric example, not a logged
 # recovery event; the distinction is documented in the notes and manifest.
 if i in [0,210,350]:im.save(B/f'p23_dynamic_{i:03}.png')
 enc.stdin.write(im.tobytes())
 if i%120==0:print('Rendered',i,'source',k,flush=True)
enc.stdin.close();assert enc.wait()==0;assert dec.wait()==0
Image.open(B/'p23_dynamic_000.png').save(B/'p23_synchronized_geometry.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest={'source_video_sha256':sha(B/'p23_media.mp4'),'landmarks_sha256':sha(B/'p23_landmarks_filtered.csv'),
 'output_sha256':sha(B/'p23_synchronized_geometry.mp4'),'frames':len(frame_map),'fps':30,'source_frames':frame_map,
 'duration_s':len(frame_map)/30,'preserved':'All 462 source video frames and their timing; original video remains embedded separately.',
 'geometry':'Same-frame measured shoulder and object-derived wrist target; calibrated lengths 0.241/0.233 m; endpoint-aligned oblique orthographic view.',
 'prior':'Normalized EMA, gain 0.3, from preceding finite shoulder/elbow observations with both filtered flags equal to 0. Teaching derivation, not archived solver state or a logged missing-elbow event.',
 'maximum_length_residual_m':max(residuals),'circle_radius_range_m':[min(g[-1] for g in geometry.values()),max(g[-1] for g in geometry.values())],
 'selected_points_endpoint_basis':{str(k):g[5].tolist() for k,g in geometry.items()}}
(B/'p23_animation_provenance.json').write_text(json.dumps(manifest,indent=2))
print('Done',manifest['output_sha256'],flush=True)

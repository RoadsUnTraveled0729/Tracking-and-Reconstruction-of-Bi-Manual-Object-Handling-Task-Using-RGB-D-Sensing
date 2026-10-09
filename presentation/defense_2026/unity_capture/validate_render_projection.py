"""Check logged Unity triads against independent projection and raster colors."""
from pathlib import Path
import json,sys,hashlib
import numpy as np
import pandas as pd
from PIL import Image
HERE=Path(__file__).resolve().parent;OUT=Path(sys.argv[1])if len(sys.argv)>1 else HERE/'r7'
rows=pd.read_csv(OUT/'axes_matrices.csv').drop_duplicates(['frame','name']);colors=np.array([[255,64,64],[64,224,112],[64,140,255]])
checks=[];samples=[];skipped=[]
for file in sorted((OUT/'stills').glob('f*.png')):
 f=int(file.stem[1:]);im=np.array(Image.open(file).convert('RGB')).astype(int);height,width=im.shape[:2]
 for row in rows[rows.frame==f].itertuples(index=False):
  camera=np.fromstring(row.camera_world_4x4,sep=';').reshape(4,4);P=np.fromstring(row.projection_4x4,sep=';').reshape(4,4)
  view=np.diag([1,1,-1,1])@np.linalg.inv(camera)
  basis=np.array([[getattr(row,f'r{i}{j}')for j in range(3)]for i in range(3)]);origin=np.array([row.origin_x,row.origin_y,row.origin_z])
  def project(q):
   clip=P@view@np.r_[q,1];ndc=clip[:3]/clip[3];return np.array([(ndc[0]+1)*width/2,(1-ndc[1])*height/2])
  a=project(origin)
  for axis in range(3):
   b=project(origin+.12*basis[:,axis]);length=float(np.linalg.norm(b-a));hits=usable=overlaps=0;errs=[]
   for t in [.3,.45,.6,.75,.9]:
    q=project(origin+.12*t*basis[:,axis]);x,y=np.rint(q).astype(int)
    if length<12 or x<6 or y<6 or x>=width-6 or y>=height-6:continue
    # Later triad axes can cover earlier axes where perspective collapses directions.
    covered=False
    for later in range(axis+1,3):
     endpoint=project(origin+.12*basis[:,later]);v=endpoint-a;u=float(np.dot(q-a,v)/max(np.dot(v,v),1e-12));closest=a+np.clip(u,0,1)*v
     if np.linalg.norm(q-closest)<=5:covered=True
    if covered:overlaps+=1;continue
    patch=im[y-5:y+6,x-5:x+6];dist=np.max(np.abs(patch-colors[axis]),axis=2);err=int(dist.min());usable+=1;hits+=err<=48;errs.append(err)
   if usable:
    passed=hits>=max(1,usable-1)
    checks.append({'frame':f,'name':row.name,'axis':'XYZ'[axis],'passed':passed,'color_matches':hits,'usable_samples':usable,'excluded_later_axis_overlap_samples':overlaps,'projected_axis_length_px':length,'minimum_color_errors':errs})
   else:skipped.append({'frame':f,'name':row.name,'axis':'XYZ'[axis],'projected_axis_length_px':length,'excluded_overlap_samples':overlaps,'reason':'No unobscured in-frame sample, or projected axis shorter than12px.'})
report={'validator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'status':'PASS'if all(c['passed']for c in checks)else'FAIL','projection_convention':'world -> inverse(camera.localToWorld) -> diag(1,1,-1,1) -> logged projectionMatrix -> NDC -> top-left image pixels. Unity camera local +Z is forward; perspective view -Z is forward.','diagnostic_tolerances':{'sample_fraction':[.3,.45,.6,.75,.9],'pixel_neighborhood_radius':5,'max_RGB_channel_error':48,'skip_projected_axis_shorter_px':12,'allowed_nonmatching_sample_per_axis':1,'later_axis_overlap_exclusion_distance_px':5},'checks':checks,'skipped_axes':skipped,'passed':sum(c['passed']for c in checks),'failed':sum(not c['passed']for c in checks),'images':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((OUT/'stills').glob('f*.png'))},'matrix_log_sha256':hashlib.sha256((OUT/'axes_matrices.csv').read_bytes()).hexdigest()}
(OUT/'render_projection_check.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['passed'],report['failed']);print([c for c in checks if not c['passed']][:10]);sys.exit(report['status']!='PASS')

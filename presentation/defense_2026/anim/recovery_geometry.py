#!/usr/bin/env python3
"""Diagram-only two-link elbow construction for a half-slide media panel.

Source: V9 Section 5.5, Eqs. 5.8-5.12. All geometry is illustrative.
One faint orthographic silhouette per sphere is temporary; the persistent
ellipse is the projection of the actual 3D intersection circle. A remembered
upper-arm direction selects one solution, not an observed unique elbow.
Native slide text supplies equations, assumptions and full source labels.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import subprocess
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'media'
WIDTH,HEIGHT,DURATION=960,720,11.0
FPS,GIF_FPS=30,10
BG,INK,MUTED='#F7F9FC','#172B40','#66788B'
BLUE,TEAL,AMBER='#245BB5','#087F83','#A7680C'
SHOULDER=np.zeros(3); WRIST=np.array([.24,-.19,0.0])
L1,L2=.26,.25
MEMORY=np.array([.10,-.72,.68]); MEMORY/=np.linalg.norm(MEMORY)
BHAT=WRIST/np.linalg.norm(WRIST)
RIGHT=.94*BHAT+math.sqrt(1-.94**2)*np.array([0,0,1])
UP=np.array([-BHAT[1],BHAT[0],0.0])
SCALE=1000.0; ORIGIN=np.array([329.0,315.0])
TEXT_BOXES=[]

@lru_cache(maxsize=40)
def font(size,bold=False):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf',size)

def label(d,xy,value,size=32,color=INK,bold=False,anchor='mm'):
    assert value.isascii()
    b=d.textbbox(xy,value,font=font(size,bold),anchor=anchor)
    if min(b[:2])<0 or b[2]>WIDTH or b[3]>HEIGHT: raise ValueError(f'Label outside diagram: {value} {b}')
    TEXT_BOXES.append((value,b)); d.text(xy,value,font=font(size,bold),fill=color,anchor=anchor)

def project(points):
    p=np.asarray(points)
    return np.stack([ORIGIN[0]+SCALE*(p @ RIGHT),ORIGIN[1]-SCALE*(p @ UP)],axis=-1)

def geometry(wrist=WRIST):
    b=wrist-SHOULDER; distance=float(np.linalg.norm(b)); direction=b/distance
    a=(L1*L1-L2*L2+distance*distance)/(2*distance)
    center=SHOULDER+a*direction; radius=math.sqrt(L1*L1-a*a)
    n1=np.array([0,0,1.0]); n1-=(n1 @ direction)*direction; n1/=np.linalg.norm(n1)
    n2=np.cross(direction,n1)
    angles=np.linspace(0,2*np.pi,181)
    circle=center+radius*(np.outer(np.cos(angles),n1)+np.outer(np.sin(angles),n2))
    prior=MEMORY-(MEMORY @ direction)*direction
    elbow=center+radius*prior/np.linalg.norm(prior)
    return center,circle,elbow

CENTER,CIRCLE,ELBOW=geometry()

def blend_color(color,strength):
    a=np.array([int(color[i:i+2],16) for i in (1,3,5)])
    b=np.array([int(BG[i:i+2],16) for i in (1,3,5)])
    return tuple(np.round(b+np.clip(strength,0,1)*(a-b)).astype(int))

def line3(d,points,color,width=4):
    d.line([tuple(p) for p in project(points)],fill=color,width=width,joint='curve')

def dot(d,p,color,radius=13,hollow=False):
    x,y=project(p)
    d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=BG if hollow else color,outline=color,width=4)

def silhouette(d,center,radius,color,strength):
    if strength<=0:return
    x,y=project(center); rr=SCALE*radius
    d.ellipse((x-rr,y-rr,x+rr,y+rr),outline=blend_color(color,strength),width=3)

def prior_arrow(d):
    a,b=project([SHOULDER,SHOULDER+L1*MEMORY*1.12]); v=b-a
    length=float(np.linalg.norm(v)); u=v/length
    for k in range(0,int(length)-15,22):
        d.line([tuple(a+u*k),tuple(a+u*min(k+11,length-15))],fill=AMBER,width=5)
    side=np.array([-u[1],u[0]])
    d.polygon([tuple(b),tuple(b-u*18+side*9),tuple(b-u*18-side*9)],fill=AMBER)

def phase_at(t,poster=False):
    if poster or t<.6 or t>=9.2:return 4
    if t<2.4:return 1
    if t<4.1:return 2
    if t<6.3:return 3
    return 4

def frame(t,poster=False):
    TEXT_BOXES.clear(); phase=phase_at(t,poster)
    im=Image.new('RGB',(WIDTH,HEIGHT),BG); d=ImageDraw.Draw(im)
    recap=poster or t<.6 or t>=9.2
    if phase==1:
        silhouette(d,SHOULDER,L1,BLUE,.42)
    elif phase==2:
        silhouette(d,SHOULDER,L1,BLUE,.25)
        silhouette(d,WRIST,L2,TEAL,.42)
    if phase>=3:
        # Trace alternatives on the actual 3D constraint circle. The moving
        # point illustrates the locus; it is not an observed elbow trajectory.
        if phase==3:
            line3(d,CIRCLE,blend_color(BLUE,.20),3)
            count=max(2,min(len(CIRCLE),int(1+(t-4.1)/2.2*(len(CIRCLE)-1))))
            line3(d,CIRCLE[:count],BLUE,6)
            dot(d,CIRCLE[count-1],BLUE,10)
        else:
            line3(d,CIRCLE,BLUE,6)
    if phase==4:
        if not recap and t<7.7:
            prior_arrow(d)
        else:
            line3(d,[SHOULDER,ELBOW,WRIST],INK,9)
            dot(d,ELBOW,AMBER,15)
            ep=project(ELBOW)
            label(d,(float(ep[0]+130),float(ep[1]+43)),'Elbow',50,AMBER,True)
    dot(d,SHOULDER,INK,14)
    dot(d,WRIST,TEAL,14,hollow=True)
    sp,wp=project([SHOULDER,WRIST])
    label(d,(float(sp[0]-90),float(sp[1]-57)),'Shoulder',50,INK,True)
    label(d,(float(wp[0]+60),float(wp[1]-57)),'Wrist',50,TEAL,True)
    label(d,(34,34),'SCHEMATIC',17,MUTED,False,'lt')
    d.rounded_rectangle((32,615,928,691),radius=16,fill='#E9EFF6')
    status={1:'Fixed upper-arm length',2:'Two length constraints',
            3:'Possible elbow positions',4:'Prior selects one elbow'}[phase]
    label(d,(480,653),status,48,INK,True)
    return im

def validate_geometry():
    _,circle,elbow=geometry()
    a=np.abs(np.linalg.norm(circle-SHOULDER,axis=1)-L1)
    b=np.abs(np.linalg.norm(circle-WRIST,axis=1)-L2)
    u=MEMORY-(MEMORY @ BHAT)*BHAT
    expected=CENTER+np.linalg.norm(elbow-CENTER)*u/np.linalg.norm(u)
    # Independent constraint and nearest-prior checks validate the construction.
    prior_point=SHOULDER+L1*MEMORY
    nearest_gap=float(np.linalg.norm(elbow-prior_point)-np.linalg.norm(circle-prior_point,axis=1).min())
    values={'circle_upper_arm_max_error':float(a.max()),'circle_forearm_max_error':float(b.max()),
            'selected_upper_arm_error':abs(float(np.linalg.norm(elbow-SHOULDER)-L1)),
            'selected_forearm_error':abs(float(np.linalg.norm(elbow-WRIST)-L2)),
            'prior_projection_error':float(np.linalg.norm(elbow-expected)),
            'projection_basis_orthogonality':abs(float(RIGHT @ UP))}
    if max(values.values())>1e-12 or nearest_gap>1e-10:raise ValueError('Elbow geometry validation failed')
    return {'scope':'Numerical consistency of an illustrative diagram, not an experiment',**values,
            'selected_distance_minus_sampled_nearest_distance':nearest_gap}

def render(preview_only=False):
    OUT.mkdir(exist_ok=True,parents=True); review=ROOT/'review'; review.mkdir(exist_ok=True,parents=True)
    report=validate_geometry()
    for t in np.linspace(0,DURATION-.01,141):frame(float(t))
    report.update({'width':WIDTH,'height':HEIGHT,'duration_seconds':DURATION,
                   'diagram_labels':['Shoulder','Wrist','Elbow'],'layout_check':'PASS: sampled text bounds',
                   'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    frame(0,poster=True).save(OUT/'recovery_geometry.png')
    for t in [1.5,3.0,5.0,7.0,9.5]:frame(t).save(review/f'recovery_geometry_sample_{t:g}.png')
    (review/'recovery_geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    if preview_only:
        print('PASS: recovery_geometry poster, five sample frames and geometry/layout check');return
    command=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{WIDTH}x{HEIGHT}',
             '-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','19',
             '-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'recovery_geometry.mp4')]
    proc=subprocess.Popen(command,stdin=subprocess.PIPE)
    for i in range(int(DURATION*FPS)):proc.stdin.write(frame(i/FPS).tobytes())
    proc.stdin.close()
    if proc.wait():raise RuntimeError('Elbow video encoding failed')
    frames=[frame(i/GIF_FPS) for i in range(int(DURATION*GIF_FPS))]; frames[-1]=frames[0].copy()
    frames[0].save(OUT/'recovery_geometry.gif',save_all=True,append_images=frames[1:],
                   duration=1000//GIF_FPS,loop=0,disposal=2,optimize=False)
    print('PASS: simplified recovery_geometry GIF, MP4 and poster')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--preview-only',action='store_true')
    render(ap.parse_args().preview_only)

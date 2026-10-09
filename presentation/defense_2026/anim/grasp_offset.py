#!/usr/bin/env python3
"""Diagram-only object-local offset animation for a half-slide media panel.

V9 Sections 5.3-5.4, Eqs. 5.2, 5.4 and 5.7. The proper rotation, cube,
marker origin and wrist share one geometric transform. All geometry and
14-second timing are illustrative. Equations, assumptions and sources live
in the native slide around this 960x720 diagram, rather than inside it.
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

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'media'
WIDTH, HEIGHT, DURATION = 960, 720, 14.0
FPS, GIF_FPS = 30, 10
BG, INK, MUTED = '#F7F9FC', '#172B40', '#66788B'
BLUE, TEAL, AMBER = '#245BB5', '#087F83', '#A7680C'
UPDATE_GAIN = 0.02
OFFSET = np.array([0.10, 0.13, 0.055])
ORIGIN_START = np.array([0.32, 0.04, 0.08])
TRANSLATION = np.array([0.22, 0.045, 0.02])
HALF_EDGE = 0.057
RIGHT = np.array([1.0, 0.0, 0.25]); RIGHT /= np.linalg.norm(RIGHT)
UP = np.array([0.18, 1.0, 0.32]); UP -= (UP @ RIGHT)*RIGHT; UP /= np.linalg.norm(UP)
VIEW = np.cross(RIGHT, UP)
VERTICES = np.array([[x,y,z] for x in [-HALF_EDGE, HALF_EDGE]
                     for y in [-HALF_EDGE, HALF_EDGE] for z in [-2*HALF_EDGE,0.0]])
TEXT_BOXES = []

@lru_cache(maxsize=40)
def font(size, bold=False):
    suffix = '-Bold' if bold else ''
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+suffix+'.ttf',size)

def label(d, xy, value, size=32, color=INK, bold=False, anchor='mm'):
    assert value.isascii()
    b=d.textbbox(xy,value,font=font(size,bold),anchor=anchor)
    if b[0]<0 or b[1]<0 or b[2]>WIDTH or b[3]>HEIGHT:
        raise ValueError(f'Label outside diagram: {value} {b}')
    TEXT_BOXES.append((value,b))
    d.text(xy,value,font=font(size,bold),fill=color,anchor=anchor)

def rotation(u):
    a=math.radians(14.0+68.0*u); c,s=math.cos(a),math.sin(a)
    return np.array([[c,-s,0.0],[s,c,0.0],[0.0,0.0,1.0]])

def flat(points):
    p=np.asarray(points)
    return np.stack([p @ RIGHT, -(p @ UP)],axis=-1)

ALL=[]
for _u in np.linspace(0,1,121):
    _r=rotation(float(_u)); _o=ORIGIN_START+_u*TRANSLATION
    ALL.extend(flat(_o+VERTICES @ _r.T)); ALL.append(flat(_o+_r @ OFFSET))
BOUNDS=np.array(ALL)
MIN,MAX=BOUNDS.min(axis=0),BOUNDS.max(axis=0)
SCALE=min(730/(MAX[0]-MIN[0]),350/(MAX[1]-MIN[1]))
MID=(MIN+MAX)/2

def project(points):
    return (flat(points)-MID)*SCALE+np.array([WIDTH/2,323.0])

def arrow(d,a,b,color,width=6,dashed=False):
    a,b=np.asarray(a,float),np.asarray(b,float)
    v=b-a; n=float(np.linalg.norm(v)); unit=v/max(n,1)
    if dashed:
        for z in range(0,int(n)-14,22):
            d.line([tuple(a+unit*z),tuple(a+unit*min(z+12,n-14))],fill=color,width=width)
    else:
        d.line([tuple(a),tuple(b-unit*13)],fill=color,width=width)
    side=np.array([-unit[1],unit[0]])
    d.polygon([tuple(b),tuple(b-unit*17+side*8),tuple(b-unit*17-side*8)],fill=color)

def cube(d,origin,rot):
    world=origin+VERTICES @ rot.T; pts=project(world)
    faces=[]
    for axis in range(3):
        for sign in [-1,1]:
            normal=np.zeros(3); normal[axis]=sign
            if (rot @ normal) @ VIEW <= 0: continue
            val=(0.0 if sign==1 else -2*HALF_EDGE) if axis==2 else sign*HALF_EDGE
            ids=np.flatnonzero(np.isclose(VERTICES[:,axis],val))
            ctr=pts[ids].mean(axis=0)
            angles=np.arctan2(pts[ids,1]-ctr[1],pts[ids,0]-ctr[0])
            ids=ids[np.argsort(angles)]
            faces.append((float(world[ids].mean(axis=0) @ VIEW),axis,ids))
    shades=['#99D3D3','#B9E4E1','#DDF0ED']
    for _,axis,ids in sorted(faces):
        d.polygon([tuple(pts[i]) for i in ids],fill=shades[axis],outline=TEAL,width=3)
    h=HALF_EDGE*.39
    square=np.array([[-h,-h,0],[h,-h,0],[h,h,0],[-h,h,0]])
    poly=project(origin+square @ rot.T)
    d.polygon([tuple(p) for p in poly],fill=INK)
    h2=h*.40
    inner=np.array([[-h2,-h2,0],[h2,-h2,0],[h2,h2,0],[-h2,h2,0]])
    d.polygon([tuple(p) for p in project(origin+inner @ rot.T)],fill='#F7F9FC')
    return pts

def phase_at(t,poster=False):
    if poster or t<0.7 or t>=12.5: return 3,1.0
    if t<4.0: return 1,0.0
    if t<5.7: return 2,0.0
    u=min(1,max(0,(t-5.7)/6.0)); u=u*u*(3-2*u)
    return 3,u

def frame(t,poster=False):
    TEXT_BOXES.clear()
    phase,u=phase_at(t,poster)
    r=rotation(u); o=ORIGIN_START+u*TRANSLATION; w=o+r @ OFFSET
    op,wp=project([o,w])
    im=Image.new('RGB',(WIDTH,HEIGHT),BG); d=ImageDraw.Draw(im)
    pts=cube(d,o,r)
    color=BLUE if phase==1 else AMBER
    arrow(d,op,wp,color,6,phase==2)
    rad=15
    d.ellipse((wp[0]-rad,wp[1]-rad,wp[0]+rad,wp[1]+rad),
              fill=color if phase==1 else BG,outline=color,width=5)
    mid=(op+wp)/2; v=wp-op; side=np.array([-v[1],v[0]])/np.linalg.norm(v)
    hp=mid+side*33
    label(d,tuple(hp),'h',58,color,True)
    label(d,(float(wp[0]),float(wp[1]-46)),'Wrist',52,color,True)
    label(d,(float(pts[:,0].mean()),float(pts[:,1].max()+40)),'Object',52,TEAL,True)
    label(d,(34,34),'SCHEMATIC',17,MUTED,False,'lt')
    d.rounded_rectangle((32,615,928,691),radius=16,fill='#E9EFF6')
    status={1:'Clean wrist + object',2:'Wrist hidden; h retained',
            3:'Predict wrist from object'}[phase]
    label(d,(480,653),status,48,INK,True)
    return im

def validate_geometry():
    inv=[]; fwd=[]; orth=[]; length=[]
    for u in np.linspace(0,1,141):
        r=rotation(float(u)); o=ORIGIN_START+u*TRANSLATION; w=o+r @ OFFSET
        h=r.T @ (w-o)
        inv.append(float(np.linalg.norm(h-OFFSET)))
        fwd.append(float(np.linalg.norm(o+r @ h-w)))
        orth.append(float(np.max(np.abs(r.T @ r-np.eye(3)))))
        length.append(abs(float(np.linalg.norm(w-o)-np.linalg.norm(OFFSET))))
        if np.linalg.det(r)<=0: raise ValueError('Reflection used as object rotation')
    values={'inverse_offset_max_error':max(inv),'forward_reconstruction_max_error':max(fwd),
            'orthonormality_max_error':max(orth),'offset_norm_max_error':max(length)}
    if max(values.values())>1e-12: raise ValueError('Schematic geometry check failed')
    return {'scope':'Numerical consistency of an illustrative diagram, not an experiment',**values}

def render(preview_only=False):
    OUT.mkdir(exist_ok=True,parents=True)
    review=ROOT/'review'; review.mkdir(exist_ok=True,parents=True)
    report=validate_geometry()
    for t in np.linspace(0,DURATION-0.01,141): frame(float(t))
    report.update({'width':WIDTH,'height':HEIGHT,'duration_seconds':DURATION,
                   'diagram_labels':['Object','Wrist','h'],'layout_check':'PASS: sampled text bounds',
                   'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    frame(0,poster=True).save(OUT/'grasp_offset.png')
    for t in [2.0,4.8,8.5,13.0]: frame(t).save(review/f'grasp_offset_sample_{t:g}.png')
    (review/'grasp_offset_geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    if preview_only:
        print('PASS: grasp_offset poster, four sample frames and geometry/layout check'); return
    command=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{WIDTH}x{HEIGHT}',
             '-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','19',
             '-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'grasp_offset.mp4')]
    proc=subprocess.Popen(command,stdin=subprocess.PIPE)
    for i in range(int(DURATION*FPS)): proc.stdin.write(frame(i/FPS).tobytes())
    proc.stdin.close()
    if proc.wait(): raise RuntimeError('Grasp-offset video encoding failed')
    frames=[frame(i/GIF_FPS) for i in range(int(DURATION*GIF_FPS))]; frames[-1]=frames[0].copy()
    frames[0].save(OUT/'grasp_offset.gif',save_all=True,append_images=frames[1:],
                   duration=1000//GIF_FPS,loop=0,disposal=2,optimize=False)
    print('PASS: simplified grasp_offset GIF, MP4 and poster')

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--preview-only',action='store_true')
    render(ap.parse_args().preview_only)

#!/usr/bin/env python3
"""One metric coordinate-axis renderer for static and moving thesis exhibits.

Basis columns are local X/Y/Z expressed in the projector's source frame.
Reflections are allowed explicitly for Camera-prime, but are never labelled
proper rotations. Projection adds no orientation information to a wrist.
"""
from __future__ import annotations
import math
from pathlib import Path
import numpy as np
from PIL import ImageDraw, ImageFont

AXIS_COLORS={'X':'#FF4040','Y':'#40E070','Z':'#408CFF'}
AXIS_NAMES=('X','Y','Z')
FONT_PATH=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
CAMERA_TO_CAMERA_PRIME=np.diag([1.,-1.,1.])
CANONICAL_ROOT=np.diag([-1.,1.,-1.])


def project_pinhole(points_camera_m,intrinsics):
    points=np.asarray(points_camera_m,dtype=float)
    if points.shape[-1]!=3 or not np.isfinite(points).all() or np.any(points[...,2]<=0):
        raise ValueError('Projection requires finite Camera points in front of the sensor.')
    return np.stack((intrinsics['fx']*points[...,0]/points[...,2]+intrinsics.get('ppx',intrinsics.get('cx')),
                     intrinsics['fy']*points[...,1]/points[...,2]+intrinsics.get('ppy',intrinsics.get('cy'))),axis=-1)


def make_pinhole_projector(intrinsics,*,source_to_camera=None,translation=None,scale=1.,offset=(0.,0.)):
    transform=np.eye(3) if source_to_camera is None else np.asarray(source_to_camera,float)
    translation=np.zeros(3) if translation is None else np.asarray(translation,float)
    def project(points):
        camera=np.asarray(points,float)@transform.T+translation
        return project_pinhole(camera,intrinsics)*scale+np.asarray(offset)
    return project


def make_orthographic_projector(view_R,center,scale_px_per_m,origin_px):
    """view_R rows are screen right, screen up and depth in source coordinates."""
    view=np.asarray(view_R,float);center=np.asarray(center,float)
    if view.shape!=(3,3) or not np.allclose(view@view.T,np.eye(3),atol=1e-10):
        raise ValueError('Orthographic view rows must be orthonormal.')
    def project(points):
        p=(np.asarray(points,float)-center)@view.T
        return np.asarray(origin_px)+p[...,:2]*np.array([1.,-1.])*scale_px_per_m
    return project


def view_matrix(azimuth_deg=25.,elevation_deg=12.):
    """Editorial oblique view of a Y-up source frame, with a fixed camera."""
    a,e=np.radians([azimuth_deg,elevation_deg])
    right=np.array([np.cos(a),0.,-np.sin(a)])
    up=np.array([np.sin(e)*np.sin(a),np.cos(e),np.sin(e)*np.cos(a)])
    return np.stack([right,up,np.cross(right,up)])


def _line(draw,start,end,fill,width,held):
    a,b=np.asarray(start,float),np.asarray(end,float)
    length=float(np.linalg.norm(b-a))
    if not held:draw.line([tuple(a),tuple(b)],fill=fill,width=width)
    elif length>0:
        for lo in np.arange(0,length,14):
            hi=min(lo+8,length)
            draw.line([tuple(a+(b-a)*lo/length),tuple(a+(b-a)*hi/length)],fill=fill,width=width)
    if length>2:
        u=(b-a)/length;n=np.array([-u[1],u[0]]);head=min(16.,length*.22)
        draw.polygon([tuple(b),tuple(b-head*u+head*.43*n),tuple(b-head*u-head*.43*n)],fill=fill)


def draw_triad(draw,origin,basis,projector,length_m,*,labels=True,held=False,line_width=5,label_px=30,label_offsets=None):
    origin=np.asarray(origin,float);basis=np.asarray(basis,float)
    if basis.shape!=(3,3) or not np.isfinite(basis).all() or not np.allclose(basis.T@basis,np.eye(3),atol=5e-5):
        raise ValueError('A displayed triad requires an orthonormal basis.')
    metric=np.vstack([origin,origin+length_m*basis.T]);screen=np.asarray(projector(metric),float)
    if not np.isfinite(screen).all():raise ValueError('Nonfinite projected triad.')
    font=ImageFont.truetype(str(FONT_PATH),label_px);label_bounds=[]
    for i,name in enumerate(AXIS_NAMES):
        _line(draw,screen[0],screen[i+1],AXIS_COLORS[name],line_width,held)
        if labels:
            delta=screen[i+1]-screen[0];norm=np.linalg.norm(delta)
            offset=np.array([7.,-7.]) if norm<1 else delta/max(norm,1)*13+np.array([2.,-5.])
            if label_offsets and name in label_offsets:offset=np.asarray(label_offsets[name],float)
            xy=tuple(screen[i+1]+offset)
            box=draw.textbbox(xy,name,font=font,anchor='mm')
            draw.text(xy,name,font=font,anchor='mm',fill=AXIS_COLORS[name],stroke_width=1,stroke_fill='black')
            label_bounds.append(list(box))
    return {'origin_m':origin.tolist(),'basis_columns':basis.tolist(),'length_m':float(length_m),
            'origin_px':screen[0].tolist(),'endpoints_px':screen[1:].tolist(),
            'determinant':float(np.linalg.det(basis)),'held':bool(held),'label_bounds':label_bounds}


def overlay_mask(before,after):
    """Identify every authored pixel change, leaving the source intact elsewhere."""
    a,b=np.asarray(before),np.asarray(after)
    if a.shape!=b.shape:raise ValueError('Overlay comparison requires matching dimensions.')
    mask=np.any(a!=b,axis=-1)
    ys,xs=np.where(mask)
    return mask,{'changed_pixels':int(mask.sum()),'bounds':None if not len(xs) else [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]}

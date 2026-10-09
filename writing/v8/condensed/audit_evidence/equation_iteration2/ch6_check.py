"""Independent Chapter 6 arithmetic audit; no production/data mutations.

The 1e-9 arithmetic tolerance is inherited from D-072. Decimal checks compare
against the actual printed precision, not experimental-accuracy thresholds.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
S = np.array([[1.,0,0],[0,0,1],[0,1,0]])
F = np.diag([1.,-1,1])
checks = []
sources = {}


def source(name):
    p = ROOT / name
    sources[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    return p


def close(name, actual, expected, decimals=None):
    a, e = np.asarray(actual, dtype=float), np.asarray(expected, dtype=float)
    error = float(np.max(np.abs(a-e)))
    ok = bool(np.array_equal(np.round(a, decimals), e)) if decimals is not None else error <= 1e-9
    checks.append(dict(name=name, passed=ok, actual=a.tolist(), expected=e.tolist(),
                       max_absolute_difference=error, decimal_comparison=decimals))


def axis(i, angle):
    angle = np.radians(angle)
    c, s = np.cos(angle), np.sin(angle)
    if i == 0: return np.array([[1,0,0],[0,c,-s],[0,s,c]])
    if i == 1: return np.array([[c,0,s],[0,1,0],[-s,0,c]])
    return np.array([[c,-s,0],[s,c,0],[0,0,1]])


def normal(v):
    return v / np.linalg.norm(v)


def angle(a,b):
    return np.degrees(np.arccos(np.clip(normal(a) @ normal(b), -1, 1)))


def level(g):
    g = normal(g)
    cross = np.cross(g, [0.,1,0])
    x,y,z = cross
    K = np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
    # Rodrigues form valid here because the pinned g is not antiparallel.
    return np.eye(3) + K + K@K/(1+g[1])


cal = json.loads(source('eval/output/scene_calibration_r6bc.json').read_text())
Tcw = np.asarray(cal['T_cam_desk'])
Twc = np.linalg.inv(Tcw)
R, t = Twc[:3,:3], Twc[:3,3]
G = level(np.asarray(cal['scene_geometry']['gravity_up_unity']))
A = S@R@F
b = S@t
Tup = np.eye(4); Tup[:3,:3]=A; Tup[:3,3]=b
Sp = np.eye(4); Sp[:3,:3]=S
Fp = np.eye(4); Fp[:3,:3]=F
close('6.1 swap involution',S@S,np.eye(3))
close('6.1 swap improper',np.linalg.det(S),-1)
close('6.1 mapped marker rotation proper',np.linalg.det(S@Tcw[:3,:3]@S),1)
close('6.2 inverse calibration rotation',R,Tcw[:3,:3].T)
close('6.2 inverse calibration origin',t,-Tcw[:3,:3].T@Tcw[:3,3])
close('6.2 homogeneous composition',Tup,Sp@Twc@Fp)
close('6.2 anchor proper',np.linalg.det(A),1)
close('6.2 anchor orthogonal',A.T@A,np.eye(3))
close('6.3 separated factors',(S@R@S)@(S@F),A)
close('6.3 fixed pair equals Rx(-90)',S@F,axis(0,-90))
close('6.4 levelling maps calibrated up onto positive y',G@normal(np.asarray(cal['scene_geometry']['gravity_up_unity'])),[0,1,0])
close('6.5 scene rotation omits floor translation',np.linalg.det(G@A),1)

pr=pd.read_csv(source('v2/output/v2_person_dump_r6b_full.csv')).set_index('frame')
orows=pd.read_csv(source('v2/output/v2_object_dump_r6b_full.csv')).set_index('frame')
mr=pd.read_csv(source('v2/output/v2_integrate_dump_r6b_full.csv')).set_index('tick')
lm=pd.read_csv(source('v1/mediapipe/output/recording_20260831_065553_landmarks_filtered.csv')).set_index('frame').loc[548]
p=pr.loc[548]; o=orows.loc[548]; tick=mr.loc[548]
q=p[['pel_x','pel_y','pel_z']].to_numpy(float)
pu=A@q+b
pl=G@pu
floor_drop=float(cal['scene_geometry']['origin_above_tabletop_m'])+0.03+0.69
Tsl=np.eye(4);Tsl[1,3]=floor_drop
ps=(Tsl@np.r_[pl,1])[:3]
close('6.6 rail floor offset cm',100*floor_drop,71.6,1)
cal7=json.loads(source('eval/output/scene_calibration_r7c.json').read_text())
close('6.6 handover floor offset cm',100*(float(cal7['scene_geometry']['origin_above_tabletop_m'])+0.72),70.9,1)
close('6.6 old origin has positive scene height',(Tsl@np.array([0,0,0,1]))[:3],[0,floor_drop,0])
close('6.5 example R World Camera',R,[[1,-.02,-.01],[0,-.48,.88],[-.02,-.88,-.48]],2)
close('6.5 example origin World Camera',t,[-.01,-.39,.43],2)
close('6.5 example anchor matrix',A,[[1,.02,-.01],[-.02,.88,-.48],[0,.48,.88]],2)
close('6.5 example origin Unity Camera',b,[-.01,.43,-.39],2)
close('6.5 example Camera-prime pelvis cm',100*q,[3.,-17.9,99.2],1)
close('6.5 example Unity pelvis cm',100*pu,[.2,-20.5,38.9],1)
close('6.5 example levelling matrix',G,[[1,.02,.01],[-.02,.85,.53],[.01,-.53,.85]],2)
close('6.5 example levelling angle degrees',angle(cal['scene_geometry']['gravity_up_unity'],[0,1,0]),32.,1)
close('6.5 example Levelled pelvis m',pl,[0,.03,.44],2)
close('6.5 example Scene pelvis cm',100*ps,[0,74.8,43.8],1)
close('6.5 example height over drawn desk cm',100*(ps[1]-.72),2.8,1)
close('6.5 example camera Unity origin cm',100*b,[-1.4,43.1,-39.3],1)
po=o[['ux','uy','uz']].to_numpy(float)
pco=Tcw[:3,:3]@S@po+Tcw[:3,3]
close('6.5 example object Unity point cm',100*po,[-23.4,-18.8,42.8],1)
close('6.5 example object Camera point cm',100*pco,[-20.6,15.1,102.1],1)
close('6.5 object return inverse round trip',S@(R@pco+t),po)
close('6.5 object Euler fields deg',o[['ex','ey','ez']].to_numpy(float),[-62.,2.8,-9.7],1)
close('6.5 person sample before render ms',(tick.tau-pr.loc[547].time_s)*1000,4.,0)
close('6.5 person sample after render ms',(p.time_s-tick.tau)*1000,29.,0)
close('6.5 interpolation endpoints',tick[['p_f0','p_f1','o_f0','o_f1']].to_numpy(float),[547,548,546,548])
close('6.5 frame-buffer modulo',548%8,4)
a=np.array([p[f'a{i}'] for i in range(13)])
root=axis(1,a[1])@axis(0,a[0])@axis(2,a[2])
shoulder=axis(1,a[3])@axis(2,a[4])@axis(0,a[5])
elbow=axis(1,a[6])@axis(2,a[7])
u=G@A@root@shoulder@np.array([1.,0,0])
f=G@A@root@shoulder@elbow@np.array([1.,0,0])
point=lambda name:lm[[name+'_'+k for k in 'xyz']].to_numpy(float)*np.array([1.,-1,1])
um=G@A@(point('right_elbow')-point('right_shoulder'))
fm=G@A@(point('right_wrist')-point('right_elbow'))
close('6.5 example right upper-arm axis',u,[-.14,-.93,-.34],2)
close('6.5 example upper-arm directional difference deg',angle(u,um),.2,1)
close('6.5 example forearm directional difference deg',angle(f,fm),6.9,1)
close('6.5 printed joint coordinates deg',a[:8],[-13.6,176.2,-1.3,-44.3,-77.2,-15.1,-22.7,0],1)
for name in ['writing/v8/condensed/scripts/build_ch6.py','writing/v8/Thesis_V8_Condensed.docx','Unity/Assets/Scripts/IntegratedSceneReceiver.cs','Unity/Assets/Scripts/ArucoSceneReceiver.cs']:
    source(name)
result={'status':'PASS' if all(c['passed'] for c in checks) else 'FAIL','passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),'checks':checks,'source_sha256':sources,'limitations':['Equation 6.5 authored/spawn-axis coincidence remains assumed; no new rig capture.','Rounded operands need not reproduce rounded results; thesis explicitly computes before rounding.','Numeric labels correspond to the frame548 branch record, not the interpolated merger output.']}
print(json.dumps(result,indent=2))
raise SystemExit(result['failed'] != 0)

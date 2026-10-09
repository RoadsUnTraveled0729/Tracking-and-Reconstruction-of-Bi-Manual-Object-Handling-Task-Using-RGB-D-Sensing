#!/usr/bin/env python3
"""Compute the worked-example numbers for the v4 per-section example round.

Everything is derived from pinned sources only:
  aruco/output/recording_20260224_083945_aruco_raw.csv
  aruco/output/recording_20260224_083945_object_world.csv
  aruco/output/recording_20260224_083945_object_world_filtered.csv
  aruco/output/scene_calibration.json
  mediapipe/output/recording_20260224_083945_landmarks_filtered_v2.csv

Sections:
  A. chordal mean (4.1) on the ten desk calibration frames
  B. geodesic bridge (4.4) across the real 7-frame object gap
  C. frame-100 chain quantities of 4.3.4 at 4dp
  D. anchor map (5.1): numeric M, pelvis frame 100 through it
  E. Rodrigues (C.1) on the frame-100 object rotation
"""
import json
import numpy as np
import pandas as pd

BASE = "/home/luo/Desktop/New_SandBox/"
raw = pd.read_csv(BASE + "v1/aruco/output/recording_20260224_083945_aruco_raw.csv")
world = pd.read_csv(BASE + "v1/aruco/output/recording_20260224_083945_object_world.csv")
filt = pd.read_csv(BASE + "v1/aruco/output/recording_20260224_083945_object_world_filtered.csv")
cal = json.load(open(BASE + "v1/aruco/output/scene_calibration.json"))
lm = pd.read_csv(BASE + "v1/mediapipe/output/recording_20260224_083945_landmarks_filtered_v2.csv")

def R_of(row, m):
    return np.array([[row[f"{m}_r{i}{j}"] for j in (1, 2, 3)] for i in (1, 2, 3)])

def t_of(row, m):
    return np.array([row[f"{m}_tx"], row[f"{m}_ty"], row[f"{m}_tz"]])

def v4(v):
    return "(" + ", ".join(f"{x:.4f}" for x in np.asarray(v).ravel()) + ")"

def m4(M):
    return " ; ".join("  ".join(f"{x:.4f}" for x in row) for row in np.asarray(M))

print("=== A. chordal mean on the ten desk calibration frames ===")
frames = cal["static_stability"]["2"]["frames"]
print("calib frames:", frames)
Rs = [R_of(raw.iloc[f], "m2") for f in frames]
ts = [t_of(raw.iloc[f], "m2") for f in frames]
A = np.mean(Rs, axis=0)
print("elementwise mean A =", m4(A))
print("det(A) =", f"{np.linalg.det(A):.10f}")
print("|A^T A - I| =", f"{np.max(np.abs(A.T@A - np.eye(3))):.3e}")
U, S, Vt = np.linalg.svd(A)
print("singular values =", ", ".join(f"{s:.7f}" for s in S))
print("det(U V^T) =", f"{np.linalg.det(U@Vt):.6f}")
R = U @ np.diag([1, 1, np.linalg.det(U@Vt)]) @ Vt
print("projected R =", m4(R))
print("det(R) =", f"{np.linalg.det(R):.12f}")
tbar = np.mean(ts, axis=0)
print("mean t =", v4(tbar))
Tcd = np.array(cal["T_cam_desk"])
print("match calibrated R:", f"{np.max(np.abs(R - Tcd[:3,:3])):.3e}",
      " t:", f"{np.max(np.abs(tbar - Tcd[:3,3])):.3e}")
# how far is A from a rotation / spread of inputs
angs = [np.degrees(np.arccos(np.clip((np.trace(R.T@Ri)-1)/2, -1, 1))) for Ri in Rs]
print("input spread about R (deg): max", f"{max(angs):.4f}", "mean", f"{np.mean(angs):.4f}")

print()
print("=== B. geodesic bridge across the 7-frame gap ===")
det = world["detected"].values.astype(int)
gaps, i = [], 0
while i < len(det):
    if det[i] == 0:
        j = i
        while j < len(det) and det[j] == 0:
            j += 1
        gaps.append((i, j - i))
        i = j
    else:
        i += 1
print("gaps (start, len):", gaps)
g0, glen = [g for g in gaps if g[1] == 7][0]
a, b = g0 - 1, g0 + glen
print(f"gap frames {g0}..{g0+glen-1}, endpoints {a} and {b}")
def Rw(row):
    return np.array([[row[f"r{i}{j}"] for j in (1, 2, 3)] for i in (1, 2, 3)])
Ra, Rb = Rw(world.iloc[a]), Rw(world.iloc[b])
pa = world.iloc[a][["tx", "ty", "tz"]].values.astype(float)
pb = world.iloc[b][["tx", "ty", "tz"]].values.astype(float)
D = Ra.T @ Rb
th = np.arccos(np.clip((np.trace(D) - 1) / 2, -1, 1))
w = np.array([D[2, 1] - D[1, 2], D[0, 2] - D[2, 0], D[1, 0] - D[0, 1]]) / (2 * np.sin(th))
print("R_a =", m4(Ra))
print("R_b =", m4(Rb))
print("Delta = Ra^T Rb =", m4(D))
print("trace(Delta) =", f"{np.trace(D):.4f}")
print("theta =", f"{np.degrees(th):.2f} deg ({th:.4f} rad)")
print("axis w =", v4(w), " |w| =", f"{np.linalg.norm(w):.6f}")
print("p_a =", v4(pa), " p_b =", v4(pb))
# midpoint frame: s from time
ta_, tb_ = world.iloc[a]["time_s"], world.iloc[b]["time_s"]
mid = g0 + glen // 2  # frame 882 if gap starts 879 len 7 -> 879..885, mid 882
tm = world.iloc[mid]["time_s"]
s = (tm - ta_) / (tb_ - ta_)
print(f"mid gap frame {mid}: s = {s:.4f}")
def rodrigues(w, ang):
    K = np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * (K @ K)
Rmid = Ra @ rodrigues(w, s * th)
pmid = pa + s * (pb - pa)
print("interpolated R(s) =", m4(Rmid))
print("interpolated p =", v4(pmid))
frow = filt.iloc[mid]
Rf = np.array([[frow[f"r{i}{j}"] for j in (1, 2, 3)] for i in (1, 2, 3)])
pf = frow[["tx", "ty", "tz"]].values.astype(float)
dang = np.degrees(np.arccos(np.clip((np.trace(Rmid.T@Rf)-1)/2, -1, 1)))
print("archived filtered frame", mid, ": filled =", frow["filled"],
      " p =", v4(pf))
print("interp vs archived: pos", f"{np.linalg.norm(pmid-pf)*1000:.2f} mm,",
      "ang", f"{dang:.2f} deg  (residual = the later smoothing stage)")
print("s*theta =", f"{np.degrees(s*th):.2f} deg")

print()
print("=== C. 4.3.4 chain quantities at 4dp ===")
Rcd, tcd = Tcd[:3, :3], Tcd[:3, 3]
print("calibrated desk R =", m4(Rcd))
print("t =", v4(tcd))
print("-R^T t =", v4(-Rcd.T @ tcd))
r100 = raw.iloc[100]
Ro, to = R_of(r100, "m1"), t_of(r100, "m1")
print("obj t (frame100) =", v4(to))
Tinv = np.eye(4); Tinv[:3, :3] = Rcd.T; Tinv[:3, 3] = -Rcd.T @ tcd
To = np.eye(4); To[:3, :3] = Ro; To[:3, 3] = to
Tw = Tinv @ To
print("world pos =", v4(Tw[:3, 3]))
Pm = np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]], float)
pu = Pm @ Tw[:3, 3]
Ru = Pm @ Tw[:3, :3] @ Pm
print("unity pos =", v4(pu))
w100 = world.iloc[100]
print("archived world row 100: t =", v4(w100[["tx","ty","tz"]].values.astype(float)),
      " unity p =", v4(w100[["unity_px","unity_py","unity_pz"]].values.astype(float)),
      " unity e =", v4(w100[["unity_ex","unity_ey","unity_ez"]].values.astype(float)))

print()
print("=== D. anchor map (5.1) ===")
F = np.diag([1.0, -1.0, 1.0])
Rcam = Rcd.T          # camera orientation in the world
tcam = -Rcd.T @ tcd   # camera position in the world
M = Pm @ Rcam @ F
print("R_cam =", m4(Rcam))
print("M = P R_cam F =", m4(M))
print("det(M) =", f"{np.linalg.det(M):.6f}",
      " ortho:", f"{np.max(np.abs(M.T@M-np.eye(3))):.2e}")
print("P t =", v4(Pm @ tcam))
row = lm[lm["frame"] == 100].iloc[0]
h23 = np.array([row["left_hip_x"], row["left_hip_y"], row["left_hip_z"]])
h24 = np.array([row["right_hip_x"], row["right_hip_y"], row["right_hip_z"]])
q = F @ ((h23 + h24) / 2)   # person space pelvis
print("pelvis q (person space) =", v4(q))
Mq = M @ q
print("M q =", v4(Mq))
p = Mq + Pm @ tcam
print("p = M q + P t =", v4(p))

print()
print("=== E. Rodrigues (C.1) on the frame-100 object rotation ===")
print("R (archived, 4dp) =", m4(Ro))
th_o = np.arccos(np.clip((np.trace(Ro) - 1) / 2, -1, 1))
wo = np.array([Ro[2, 1] - Ro[1, 2], Ro[0, 2] - Ro[2, 0], Ro[1, 0] - Ro[0, 1]]) / (2 * np.sin(th_o))
print("trace =", f"{np.trace(Ro):.4f}", " theta =", f"{np.degrees(th_o):.2f} deg ({th_o:.4f} rad)")
print("axis w =", v4(wo), " |w| =", f"{np.linalg.norm(wo):.6f}")
K = np.array([[0, -wo[2], wo[1]], [wo[2], 0, -wo[0]], [-wo[1], wo[0], 0]])
print("[w]x =", m4(K))
print("[w]x^2 =", m4(K @ K))
print("sin(theta) =", f"{np.sin(th_o):.4f}", " 1-cos(theta) =", f"{1-np.cos(th_o):.4f}")
Rre = np.eye(3) + np.sin(th_o) * K + (1 - np.cos(th_o)) * (K @ K)
print("rebuilt R =", m4(Rre))
print("max |rebuilt - archived| =", f"{np.max(np.abs(Rre - Ro)):.3e}")
print("reproj of frame100 object:", f"{r100['m1_reproj_px']:.3f} px")

print()
print("=== extras: A.4 forward projection closure ===")
fx, fy, cx, cy = 607.56, 607.02, 323.94, 248.02
x, y, z = 0.0674, -0.1118, 0.929
print("u =", f"{fx*x/z+cx:.1f}", " v =", f"{fy*y/z+cy:.1f}")

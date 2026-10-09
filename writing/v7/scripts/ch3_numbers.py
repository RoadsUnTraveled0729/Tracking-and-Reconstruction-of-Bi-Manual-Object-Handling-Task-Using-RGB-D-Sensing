#!/usr/bin/env python3
"""Compute every intermediate of the V7 Chapter 3 worked example.

Pinned frame: 533 of the rail recording recording_20260831_065553
(rail-only round 2026-09-01, replacing R5 frame 270 / D17): all eight
landmarks measured raw (every _flag and _src zero), every Chapter 5
failure detector clear in eval/output/recovery_r6b/failure_mask.csv,
outside the 550-639 right-wrist gap. The chapter text hardcodes the
printed values; rerun this script to regenerate them. A
whole-recording sweep at the end checks the reconstruction invariant
and the elbow flexion range on every frame where the solver ran.
"""
import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "v1" / "kinematics"))
from root_frame import (unity_from_sensor, build_root_frame,   # noqa: E402
                        euler_unity_zxy, recompose_zxy, normalize)
from shoulder import (solve_right_arm, solve_left_arm,         # noqa: E402
                      recompose_shoulder, _ry, _rz, _rx)

CSV = REPO / "v1" / "mediapipe" / "output" / "recording_20260831_065553_landmarks_filtered.csv"
FRAME = 533
names = ["left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
         "left_wrist", "right_wrist", "left_hip", "right_hip"]
lm_id = {"left_shoulder": 11, "right_shoulder": 12, "left_elbow": 13,
         "right_elbow": 14, "left_wrist": 15, "right_wrist": 16,
         "left_hip": 23, "right_hip": 24}

rows = list(csv.DictReader(open(CSV)))
row = next(r for r in rows if int(r["frame"]) == FRAME)


def pos(r, n):
    try:
        return np.array([float(r[f"{n}_x"]), float(r[f"{n}_y"]),
                         float(r[f"{n}_z"])])
    except ValueError:
        return None


P_cam = {n: pos(row, n) for n in names}
np.set_printoptions(precision=4, suppress=True)

print("== Camera-frame landmark positions (m), frame", FRAME,
      "t=%.3f s" % float(row["time_s"]))
for n in names:
    p = P_cam[n]
    print(f"  L{lm_id[n]:2d} {n:15s} ({p[0]:+.4f}, {p[1]:+.4f}, {p[2]:+.4f})")

P = {n: unity_from_sensor(P_cam[n]) for n in names}
print("\n== Person-space (F=diag(1,-1,1)) positions")
for n in names:
    p = P[n]
    print(f"  L{lm_id[n]:2d} {n:15s} ({p[0]:+.4f}, {p[1]:+.4f}, {p[2]:+.4f})")

p23, p24, p12 = P["left_hip"], P["right_hip"], P["right_shoulder"]
print("\n== Root frame construction")
d = p24 - p23
print("  p24-p23      =", d, " |.| = %.4f" % np.linalg.norm(d))
r = d / np.linalg.norm(d)
print("  x_hat        =", r)
s = p12 - p24
print("  s = p12-p24  =", s, " |.| = %.4f" % np.linalg.norm(s))
cr = np.cross(r, s)
print("  x x s        =", cr, " |.| = %.4f" % np.linalg.norm(cr))
f = cr / np.linalg.norm(cr)
print("  z_hat        =", f)
u = np.cross(f, r)
print("  y_hat        =", u, " |.| = %.10f" % np.linalg.norm(u))
R = build_root_frame(p23, p24, p12)
print("  R_root =\n", R)
print("  det = %.12f  orth resid = %.2e"
      % (np.linalg.det(R), np.abs(R.T @ R - np.eye(3)).max()))
e = euler_unity_zxy(R)
print("  Euler ZXY-applied (x, y, z) = (%.2f, %.2f, %.2f) deg" % tuple(e))
Rrt = recompose_zxy(e)
print("  round-trip max |dR| = %.2e" % np.abs(Rrt - R).max())
print("  angle(s, x) = %.2f deg (inputs not perpendicular)"
      % np.degrees(np.arccos(np.dot(s / np.linalg.norm(s), r))))

print("\n== Right arm")
p14, p16 = P["right_elbow"], P["right_wrist"]
ua = p14 - p12
print("  upper arm p14-p12 (person) =", ua, " |.|=%.4f" % np.linalg.norm(ua))
ualoc = R.T @ ua
print("  R_root^T * ua =", ualoc)
a = normalize(ualoc)
print("  a_hat (local) =", a)
th_z = np.degrees(np.arcsin(np.clip(a[1], -1, 1)))
th_y = np.degrees(np.arctan2(-a[2], a[0]))
print("  theta_z = asin(%.4f) = %.2f deg   theta_y = atan2(%.4f, %.4f) = %.2f deg"
      % (a[1], th_z, -a[2], a[0], th_y))
fa = p16 - p14
print("  forearm p16-p14 (person) =", fa, " |.|=%.4f" % np.linalg.norm(fa))
floc = R.T @ fa
print("  f = R_root^T * fa =", floc)
fp = _rz(-np.radians(th_z)) @ (_ry(-np.radians(th_y)) @ floc)
print("  f' un-swung =", fp, "  perp |.| = %.4f" % np.hypot(fp[1], fp[2]))
th_t = np.degrees(np.arctan2(-fp[1], fp[2]))
print("  theta_t = atan2(%.4f, %.4f) = %.2f deg" % (-fp[1], fp[2], th_t))
sh, el, ok = solve_right_arm(p12, p14, p16, R)
print("  solver: shoulder (ty,tz,tt) = (%.2f, %.2f, %.2f) elbow (ey,ez)=(%.2f, %.10f) twist_ok=%s"
      % (sh[0], sh[1], sh[2], el[0], el[1], ok))
R_arm = R @ recompose_shoulder(sh)
g = normalize(R_arm.T @ fa)
print("  g_hat in L14 arm frame =", g)
print("  e_y = atan2(%.4f, %.4f) = %.2f deg" % (-g[2], g[0], el[0]))
R_sh = recompose_shoulder(sh)
print("  R_sh Unity ZXY Euler = (%.2f, %.2f, %.2f)" % tuple(euler_unity_zxy(R_sh)))
a_rec = R_sh @ np.array([1.0, 0, 0])
print("  recon arm dir err = %.2e deg"
      % np.degrees(np.arccos(np.clip(np.dot(a_rec, a), -1, 1))))

def print_T(label, Rm, t):
    T = np.eye(4)
    T[:3, :3] = Rm
    T[:3, 3] = t
    print(label)
    for i in range(4):
        print("   [" + "  ".join("%+.2f" % v for v in T[i]) + "]")


print("\n== Homogeneous T matrices of the chain (C15-C20 round)")
print_T("  T_root (root w.r.t. person space): R_root, origin p24", R, p24)
off_sh = R.T @ (p12 - p24)
print("  shoulder origin offset in root coords R_root^T(p12-p24) =",
      np.round(off_sh, 4))
print_T("  T_sh (shoulder w.r.t. root): identity rotation", np.eye(3), off_sh)
off_el = R.T @ (p14 - p12)
print("  elbow origin offset in shoulder coords R_root^T(p14-p12) =",
      np.round(off_el, 4))
print_T("  T_el (elbow w.r.t. shoulder): R_sh (solved swing-twist)",
        recompose_shoulder(sh), off_el)
# chain composition check: T_root * T_sh * T_el applied to origin
# must land on the measured elbow position
T1 = np.eye(4); T1[:3, :3] = R; T1[:3, 3] = p24
T2 = np.eye(4); T2[:3, 3] = off_sh
T3 = np.eye(4); T3[:3, :3] = recompose_shoulder(sh); T3[:3, 3] = off_el
Tc = T1 @ T2 @ T3
print("  chain check: (T_root T_sh T_el) origin =",
      np.round(Tc[:3, 3], 4), " measured p14 =", np.round(p14, 4),
      " |diff| = %.2e m" % np.linalg.norm(Tc[:3, 3] - p14))
# wrist landmark carried into the elbow frame by the inverse chain
w_h = np.linalg.solve(Tc, np.append(p16, 1.0))
print("  wrist in elbow frame (T chain inverse applied to p16) =",
      np.round(w_h[:3], 4), " |.| = %.4f" % np.linalg.norm(w_h[:3]))

print("\n== Left arm (mirror)")
p11, p13, p15 = P["left_shoulder"], P["left_elbow"], P["left_wrist"]
shL, elL, okL = solve_left_arm(p11, p13, p15, R)
print("  solver: shoulder = (%.2f, %.2f, %.2f) elbow ey = %.2f twist_ok=%s"
      % (shL[0], shL[1], shL[2], elL[0], okL))

print("\n== Whole-recording sweep (all frames where the solve ran)")
worst_rec = 0.0
ey_min, ey_max = 0.0, -180.0
worst_rec_L = 0.0
eyL_min, eyL_max = 0.0, -180.0
n_ok = 0
for rr in rows:
    if rr.get("has_pose") != "1":
        continue
    p = {n: pos(rr, n) for n in names}
    if any(v is None for v in p.values()):
        continue
    Pp = {n: unity_from_sensor(p[n]) for n in names}
    Rr = build_root_frame(Pp["left_hip"], Pp["right_hip"], Pp["right_shoulder"])
    shr, elr, okr = solve_right_arm(Pp["right_shoulder"], Pp["right_elbow"],
                                    Pp["right_wrist"], Rr)
    ar = normalize(Rr.T @ (Pp["right_elbow"] - Pp["right_shoulder"]))
    arec = recompose_shoulder(shr) @ np.array([1.0, 0, 0])
    err = np.degrees(np.arccos(np.clip(np.dot(arec, ar), -1, 1)))
    worst_rec = max(worst_rec, err)
    ey_min = min(ey_min, elr[0]); ey_max = max(ey_max, elr[0])
    # left arm: mirror solve, rest direction -x (shoulder.py:144)
    shl, ell, _ = solve_left_arm(Pp["left_shoulder"], Pp["left_elbow"],
                                 Pp["left_wrist"], Rr)
    al = normalize(Rr.T @ (Pp["left_elbow"] - Pp["left_shoulder"]))
    tyL, tzL, _ = np.radians(shl)
    alrec = (_ry(-tyL) @ _rz(-tzL)) @ np.array([-1.0, 0, 0])
    worst_rec_L = max(worst_rec_L,
                      np.degrees(np.arccos(np.clip(np.dot(alrec, al), -1, 1))))
    eyL_min = min(eyL_min, ell[0]); eyL_max = max(eyL_max, ell[0])
    n_ok += 1
print("  frames solved: %d of %d" % (n_ok, len(rows)))
print("  worst arm-direction reconstruction error, right: %.2e deg" % worst_rec)
print("  worst arm-direction reconstruction error, left:  %.2e deg" % worst_rec_L)
print("  right elbow flexion range: [%.2f, %.2f] deg" % (ey_min, ey_max))
print("  left elbow flexion range:  [%.2f, %.2f] deg" % (eyL_min, eyL_max))

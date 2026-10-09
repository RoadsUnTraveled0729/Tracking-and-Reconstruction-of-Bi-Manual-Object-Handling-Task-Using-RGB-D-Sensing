"""Compute every intermediate of the Ch3 worked examples from pinned data."""
import sys, csv
import numpy as np
sys.path.insert(0, "/home/luo/Desktop/New_SandBox/kinematics")
from root_frame import unity_from_sensor, build_root_frame, euler_unity_zxy, recompose_zxy, normalize
from shoulder import solve_right_arm, solve_left_arm, recompose_shoulder, _ry, _rz, _rx

CSV = "/home/luo/Desktop/New_SandBox/kinematics/dataset/real_20260224/recording_20260224_083945_landmarks_filtered.csv"
FRAME = 100
names = ["left_shoulder","right_shoulder","left_elbow","right_elbow","left_wrist","right_wrist","left_hip","right_hip"]
lm_id = {"left_shoulder":11,"right_shoulder":12,"left_elbow":13,"right_elbow":14,"left_wrist":15,"right_wrist":16,"left_hip":23,"right_hip":24}

with open(CSV) as f:
    for row in csv.DictReader(f):
        if int(row["frame"]) == FRAME:
            break
P_cam = {n: np.array([float(row[f"{n}_x"]), float(row[f"{n}_y"]), float(row[f"{n}_z"])]) for n in names}
np.set_printoptions(precision=4, suppress=True)

print("== Camera-frame landmark positions (m), frame", FRAME, "t=%.3f s" % float(row["time_s"]))
for n in names:
    p = P_cam[n]
    print(f"  L{lm_id[n]:2d} {n:15s} ({p[0]:+.4f}, {p[1]:+.4f}, {p[2]:+.4f})")

P = {n: unity_from_sensor(P_cam[n]) for n in names}
print("\n== Person-space (F=diag(1,-1,1)) positions")
for n in names:
    p = P[n]
    print(f"  L{lm_id[n]:2d} {n:15s} ({p[0]:+.4f}, {p[1]:+.4f}, {p[2]:+.4f})")

p23, p24, p12 = P["left_hip"], P["right_hip"], P["left_shoulder"]  # placeholder fix below
p12 = P["right_shoulder"]
print("\n== Root frame construction")
d = p24 - p23
print("  p24-p23      =", d, " |.| = %.4f" % np.linalg.norm(d))
r = d/np.linalg.norm(d)
print("  r_hat        =", r)
s = p12 - p24
print("  s = p12-p24  =", s, " |.| = %.4f" % np.linalg.norm(s))
cr = np.cross(r, s)
print("  r x s        =", cr, " |.| = %.4f" % np.linalg.norm(cr))
f = cr/np.linalg.norm(cr)
print("  f_hat        =", f)
u = np.cross(f, r)
print("  u_hat        =", u, " |.| = %.10f" % np.linalg.norm(u))
R = build_root_frame(p23, p24, p12)
print("  R_root =\n", R)
print("  det = %.12f  orth resid = %.2e" % (np.linalg.det(R), np.abs(R.T@R - np.eye(3)).max()))
e = euler_unity_zxy(R)
print("  Euler ZXY-applied (x, y, z) = (%.2f, %.2f, %.2f) deg" % tuple(e))
Rrt = recompose_zxy(e)
print("  round-trip max |dR| = %.2e" % np.abs(Rrt - R).max())
print("  angle(s, r) = %.2f deg (inputs not perpendicular)" % np.degrees(np.arccos(np.dot(s/np.linalg.norm(s), r))))

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
print("  theta_z = asin(%.4f) = %.2f deg   theta_y = atan2(%.4f, %.4f) = %.2f deg" % (a[1], th_z, -a[2], a[0], th_y))
fa = p16 - p14
print("  forearm p16-p14 (person) =", fa, " |.|=%.4f" % np.linalg.norm(fa))
floc = R.T @ fa
print("  f = R_root^T * fa =", floc)
fp = _rz(-np.radians(th_z)) @ (_ry(-np.radians(th_y)) @ floc)
print("  f' un-swung =", fp, "  perp |.| = %.4f" % np.hypot(fp[1], fp[2]))
th_t = np.degrees(np.arctan2(-fp[1], fp[2]))
print("  theta_tau = atan2(%.4f, %.4f) = %.2f deg" % (-fp[1], fp[2], th_t))
sh, el, ok = solve_right_arm(p12, p14, p16, R)
print("  solver: shoulder (ty,tz,tt) = (%.2f, %.2f, %.2f) elbow (ey,ez)=(%.2f, %.10f) twist_ok=%s" % (sh[0],sh[1],sh[2],el[0],el[1],ok))
R_arm = R @ recompose_shoulder(sh)
g = normalize(R_arm.T @ fa)
print("  g_hat in L14 arm frame =", g)
print("  e_y = atan2(%.4f, %.4f) = %.2f deg" % (-g[2], g[0], el[0]))
# full shoulder matrix and its Unity Euler
R_sh = recompose_shoulder(sh)
print("  R_sh = Ry Rz Rx =\n", R_sh)
print("  R_sh Unity ZXY Euler = (%.2f, %.2f, %.2f)" % tuple(euler_unity_zxy(R_sh)))
# reconstruction check
a_rec = R_sh @ np.array([1.0,0,0])
print("  recon arm dir err = %.2e deg" % np.degrees(np.arccos(np.clip(np.dot(a_rec, a),-1,1))))

print("\n== Left arm (mirror)")
p11, p13, p15 = P["left_shoulder"], P["left_elbow"], P["left_wrist"]
uL = R.T @ (p13 - p11); fL = R.T @ (p15 - p13)
print("  ua local =", uL, " mirrored =", np.array([-1,1,1])*uL)
print("  fa local =", fL, " mirrored =", np.array([-1,1,1])*fL)
shL, elL, okL = solve_left_arm(p11, p13, p15, R)
print("  solver: shoulder = (%.2f, %.2f, %.2f) elbow ey = %.2f twist_ok=%s" % (shL[0],shL[1],shL[2],elL[0],okL))

print("\n== Reference pose (upright facing sensor)")
Rref = np.array([[-1,0,0],[0,1,0],[0,0,-1]], dtype=float)
print("  Euler =", euler_unity_zxy(Rref))

print("\n== Wrist reading sensor vs person space (comment 17)")
pw = P_cam["right_wrist"]
print("  camera  (%.4f, %.4f, %.4f)" % tuple(pw), "-> person (%.4f, %.4f, %.4f)" % tuple(unity_from_sensor(pw)))

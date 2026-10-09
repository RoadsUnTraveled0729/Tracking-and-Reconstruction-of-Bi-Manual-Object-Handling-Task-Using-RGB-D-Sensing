#!/usr/bin/env python3
"""Numerical checks for D1_limitations.md derivations."""
import numpy as np

def Rx(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])

def Ry(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

def Rz(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

d2r = np.deg2rad

# ---------------------------------------------------------------
# 1. Twist sensitivity ~ 1/|sin(ey)| near-straight elbow
# Forearm at flexion ey, twist tau=0: f = Ry(ey) @ x_hat (in arm frame,
# after swing removal the arm axis is x). Perturb the forearm direction
# by angular noise delta in the worst direction (about the arm axis is
# what twist reads); measure decoded twist change.
print("== 1. twist conditioning vs elbow flexion ==")
delta = d2r(1.0)  # 1 deg of forearm angular noise
for ey_deg in (90, 45, 30, 14, 10, 5):
    ey = d2r(-ey_deg)
    f = Ry(ey) @ np.array([1.0, 0, 0])   # zero-twist forearm, flexion plane x-z
    # worst-case noise: rotate f about the arm axis (x) by delta
    f_noisy = Rx(delta) @ f
    # twist decode: tau = atan2(-fy, fz) on the perpendicular part
    tau = np.degrees(np.arctan2(-f_noisy[1], f_noisy[2]))
    amp = abs(tau) / np.degrees(delta)
    pred = 1.0  # rotation about the axis maps 1:1 by construction
    # the amplification appears for TRANSVERSE positional noise:
    # displace the wrist tip by delta (angular, i.e. |dp| = delta * L)
    # in the y direction (out of the flexion plane), L = 1
    fp = f + np.array([0, np.sin(delta), 0])
    fp /= np.linalg.norm(fp)
    tau2 = np.degrees(np.arctan2(-fp[1], fp[2]))
    amp2 = abs(tau2) / np.degrees(delta)
    print(f"  ey={ey_deg:3d} deg: twist err from 1deg transverse noise = "
          f"{abs(tau2):6.2f} deg  (amplification {amp2:5.2f}, "
          f"1/|sin ey| = {1/abs(np.sin(ey)):5.2f})")

# measured case: ey ~ -14 deg, raw jumps 65 deg in twist.
# implied transverse noise: 65 / (1/sin(14deg)) deg of forearm direction noise
imp = 65.0 * abs(np.sin(d2r(14)))
print(f"  measured 65 deg twist jump at ey=-14 => implied forearm direction "
      f"noise {imp:.1f} deg")
# forearm ~0.23 m; landmark jitter ~5-10 mm at each end -> direction noise
for j in (0.005, 0.010, 0.02, 0.054):
    print(f"    {j*1000:4.0f} mm endpoint jitter on 0.23 m forearm = "
          f"{np.degrees(j/0.23):5.2f} deg direction noise")

# ---------------------------------------------------------------
# 2. Gimbal-lock conditioning of ZXY extraction
print("\n== 2. Euler extraction conditioning near x=+-90 ==")
def euler_zxy_extract(R):
    x = np.arcsin(np.clip(-R[1, 2], -1, 1))
    y = np.arctan2(R[0, 2], R[2, 2])
    z = np.arctan2(R[1, 0], R[1, 1])
    return np.degrees([x, y, z])

def compose(xd, yd, zd):
    return Ry(d2r(yd)) @ Rx(d2r(xd)) @ Rz(d2r(zd))

for xd in (0, 45, 80, 89, 89.9):
    R = compose(xd, 37.0, 12.0)
    # perturb by machine-scale rotation eps about a random axis
    eps = 1e-9
    Rp = Rx(eps) @ R
    e0 = euler_zxy_extract(R)
    e1 = euler_zxy_extract(Rp)
    err = np.abs(e1 - e0)
    print(f"  x={xd:5.1f}: d(y,z)/d(eps) ~ {err[1]/np.degrees(eps):8.1f}, "
          f"{err[2]/np.degrees(eps):8.1f}   (1/cos x = "
          f"{1/np.cos(d2r(xd)):8.1f})")

# ---------------------------------------------------------------
# 3. Lever-arm law
print("\n== 3. lever arm ==")
print(f"  0.7 deg at 2.8 m = {d2r(0.7)*2.8*1000:.0f} mm")

# ---------------------------------------------------------------
# 4. IPPE lobe separation ~ 2 x tilt (mirror about viewing ray)
print("\n== 4. lobe separation consistency ==")
print(f"  measured wall separation ~23 deg => tilt ~{23/2:.1f} deg about "
      f"the viewing ray; plumb wall viewed 3 m away slightly off-axis is "
      f"consistent with a ~10-12 deg effective tilt")

# ---------------------------------------------------------------
# 5. angle noise from position noise: sigma_theta ~ sigma_pos / L
print("\n== 5. angle noise from position noise ==")
for L, name in ((0.23, "forearm"), (0.28, "upper arm"), (0.32, "shoulder width")):
    for s in (0.005, 0.010):
        print(f"  {name} L={L} m, sigma={s*1000:.0f} mm -> "
              f"{np.degrees(s/L):4.2f} deg")

# ---------------------------------------------------------------
# 6. arccos vs atan2 conditioning near 0 deg
print("\n== 6. arccos conditioning ==")
a = np.array([1.0, 0, 0])
for t in (1e-3, 1e-6):
    b = Ry(t) @ a
    via_acos = np.degrees(np.arccos(np.clip(np.dot(a, b), -1, 1)))
    via_atan = np.degrees(np.arctan2(np.linalg.norm(np.cross(a, b)), np.dot(a, b)))
    true = np.degrees(t)
    print(f"  true {true:.2e} deg: arccos {via_acos:.2e}, atan2 {via_atan:.2e}")

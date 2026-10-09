"""Chapter 5 worked-example numbers: the person-to-scene anchor transform.

Computes M = P R_desk_cam F from the pinned scene_calibration.json using the
real pipeline helpers (aruco/frames.py), verifies the factorization
M = R_unity(camera) * Rx(-90 deg) that the Unity receiver composes, and maps
the pinned frame-100 pelvis point through the anchor. Cross-checks the
integrated stream against the filtered object CSV at frame 100. Every number
printed here may be quoted in Chapter 5.
"""
import json
import sys

import numpy as np
import pandas as pd

ROOT = "/home/luo/Desktop/New_SandBox"
sys.path.insert(0, f"{ROOT}/aruco")
from frames import WORLD_TO_UNITY, euler_unity_zxy, inv_T

FRAME = 100

calib = json.load(open(f"{ROOT}/aruco/dataset/scene_calibration.json"))
stream = pd.read_csv(f"{ROOT}/integration/dataset/integrated_stream.csv")
filt = pd.read_csv(
    f"{ROOT}/aruco/dataset/recording_20260224_083945_object_world_filtered.csv")


def fmt(v, nd=4):
    a = np.asarray(v, float)
    if a.ndim == 0:
        return f"{a:.{nd}f}"
    if a.ndim == 1:
        return "(" + ", ".join(f"{x:.{nd}f}" for x in a) + ")"
    return "\n".join("  [" + "  ".join(f"{x:9.{nd}f}" for x in r) + "]" for r in a)


P = WORLD_TO_UNITY                       # y/z swap, world -> Unity
F = np.diag([1.0, -1.0, 1.0])            # camera -> person space (y flip)

T_desk_cam = inv_T(np.array(calib["T_cam_desk"]))
R_desk_cam, t_desk_cam = T_desk_cam[:3, :3], T_desk_cam[:3, 3]

print("=== the person-to-scene anchor, from the pinned calibration ===\n")
print("R_desk_cam (camera orientation in the world) =\n" + fmt(R_desk_cam))
print("t_desk_cam (camera position in the world)    =", fmt(t_desk_cam))

M = P @ R_desk_cam @ F
print("\nM = P R_desk_cam F =\n" + fmt(M))
print("  det M =", fmt(np.linalg.det(M), 12),
      "  orthonormality |M^T M - I|_max =",
      f"{np.abs(M.T @ M - np.eye(3)).max():.2e}")

# the factorization the Unity receiver actually composes
R_u_cam = P @ R_desk_cam @ P
Rx_m90 = np.array([[1, 0, 0],
                   [0, np.cos(np.radians(-90)), -np.sin(np.radians(-90))],
                   [0, np.sin(np.radians(-90)), np.cos(np.radians(-90))]])
print("\nR_unity(camera) = P R_desk_cam P =\n" + fmt(R_u_cam))
print("  camera Unity Euler =", fmt(euler_unity_zxy(R_u_cam), 2),
      "  position P t =", fmt(P @ t_desk_cam))
print("factorization residual |R_unity(cam) Rx(-90) - M|_max =",
      f"{np.abs(R_u_cam @ Rx_m90 - M).max():.2e}")
print("anchor node Unity Euler (of M itself) =", fmt(euler_unity_zxy(M), 2))

# identity P F = Rx(-90): the two flips combine into one proper rotation
print("\ncheck P F =\n" + fmt(P @ F), "\n  equals Rx(-90):",
      bool(np.allclose(P @ F, Rx_m90)))

# --- frame-100 pelvis through the anchor ---------------------------------
row = stream[stream.frame == FRAME].iloc[0]
q = np.array([row.pel_x, row.pel_y, row.pel_z])
p_scene = M @ q + P @ t_desk_cam
print(f"\n=== pinned frame {FRAME} ===")
print("pelvis in person space q =", fmt(q))
print("p_scene = M q + P t_desk_cam =", fmt(p_scene))
print(f"  (person mask {int(row['mask'])} = all 7 joints live,"
      f" object live {int(row.obj_live)})")

# stream object pose must be verbatim the filtered world CSV row
fr = filt[filt.frame == FRAME].iloc[0]
sp = np.array([row.opx, row.opy, row.opz])
fp = np.array([fr.unity_px, fr.unity_py, fr.unity_pz])
print("stream object pos =", fmt(sp), " filtered CSV =", fmt(fp),
      f" max |diff| = {np.abs(sp - fp).max():.2e} m")

# --- stream-wide facts quoted in 5.1 -------------------------------------
print(f"\nstream: {len(stream)} frames,"
      f" strictly increasing: {bool((np.diff(stream.frame) > 0).all())},"
      f" object live on {int(stream.obj_live.sum())} frames,"
      f" person fully live (mask 127) on {int((stream['mask'] == 127).sum())}")

# gravity + geometry quoted in 5.4
sg = calib["scene_geometry"]
print("\ngravity_up_unity =", fmt(sg["gravity_up_unity"]),
      "\nseed-vs-wall", f"{sg['gravity_seed_dev_deg']:.2f} deg,",
      "tabletop drop", f"{1000*sg['origin_above_tabletop_m']:.1f} mm,",
      "cube", f"{sg['object_cube_size_m']*1000:.0f} mm,",
      f"FOV {sg['sensor_fov_x_deg']:.1f} x {sg['sensor_fov_y_deg']:.1f} deg")

# tilt of gravity from the world z axis (why the ArucoWorld parent exists)
g = np.asarray(sg["gravity_up_world"], float)
tilt = np.degrees(np.arccos(np.clip(g @ np.array([0, 0, 1.0]), -1, 1)))
print(f"gravity vs desk-marker normal (world z): {tilt:.2f} deg"
      " (= the desk stand tilt the ArucoWorld parent levels out)")

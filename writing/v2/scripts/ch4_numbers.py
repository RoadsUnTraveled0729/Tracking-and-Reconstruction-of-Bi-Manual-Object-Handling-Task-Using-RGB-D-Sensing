"""Chapter 4 worked-example numbers, computed by the real Pipeline B math.

Runs the actual world-anchoring chain (aruco/frames.py) on pinned frame 100
of aruco/dataset/recording_20260224_083945_aruco_raw.csv with the pinned
scene_calibration.json, and cross-checks the result against the pinned
object_world CSV (raw and filtered). Every number printed here may be
quoted in Chapter_4_Offline_Processing_Pipeline.docx.
"""
import json
import sys

import numpy as np
import pandas as pd

ROOT = "/home/luo/Desktop/New_SandBox"
sys.path.insert(0, f"{ROOT}/aruco")
from frames import (WORLD_TO_UNITY, euler_unity_zxy, geodesic_deg, inv_T,
                    make_T, rt_from_row, unity_from_world)

DS = f"{ROOT}/aruco/dataset"
FRAME = 100

raw = pd.read_csv(f"{DS}/recording_20260224_083945_aruco_raw.csv")
world = pd.read_csv(f"{DS}/recording_20260224_083945_object_world.csv")
filt = pd.read_csv(f"{DS}/recording_20260224_083945_object_world_filtered.csv")
calib = json.load(open(f"{DS}/scene_calibration.json"))

row = raw[raw.frame == FRAME].iloc[0]


def fmt(v, nd=4):
    a = np.asarray(v, float)
    if a.ndim == 0:
        return f"{a:.{nd}f}"
    if a.ndim == 1:
        return "(" + ", ".join(f"{x:.{nd}f}" for x in a) + ")"
    return "\n".join("  [" + "  ".join(f"{x:9.{nd}f}" for x in r) + "]" for r in a)


print(f"=== pinned frame {FRAME}, recording_20260224_083945 ===\n")

# --- raw per-marker detections at frame 100 -------------------------------
for mid, name in [(0, "wall"), (2, "desk"), (1, "object")]:
    det = int(row[f"m{mid}_detected"])
    print(f"marker id{mid} ({name}): detected={det}", end="")
    if det:
        print(f"  center px ({int(row[f'm{mid}_u'])}, {int(row[f'm{mid}_v'])})"
              f"  reproj {row[f'm{mid}_reproj_px']:.3f} px"
              f"  ambig {int(row[f'm{mid}_ambig'])}"
              f"  PnP z {row[f'm{mid}_tz']:.4f} m, depth z {row[f'm{mid}_depth_z']:.3f} m"
              f"  (diff {1000*(row[f'm{mid}_tz'] - row[f'm{mid}_depth_z']):+.1f} mm)")
    else:
        print()

R_obj, t_obj = rt_from_row(row, 1)
print("\nT_cam_obj(100): R =\n" + fmt(R_obj) + "\n  t = " + fmt(t_obj))
print("  det R =", fmt(np.linalg.det(R_obj), 12))

# --- calibrated anchor and its closed-form inverse ------------------------
T_cam_desk = np.array(calib["T_cam_desk"])
R_cd, t_cd = T_cam_desk[:3, :3], T_cam_desk[:3, 3]
print("\ncalibrated T_cam_desk (frozen anchor): R =\n" + fmt(R_cd)
      + "\n  t = " + fmt(t_cd))

T_desk_cam = inv_T(T_cam_desk)
print("\nT_desk_cam = closed-form inverse: R^T =\n" + fmt(T_desk_cam[:3, :3])
      + "\n  -R^T t = " + fmt(T_desk_cam[:3, 3])
      + "  (camera position in the world)")
print("  check T_desk_cam @ T_cam_desk == I: max |err| =",
      f"{np.abs(T_desk_cam @ T_cam_desk - np.eye(4)).max():.2e}")

# camera pose in Unity terms (it is rendered in the scene)
p_cam_u, R_cam_u = unity_from_world(T_desk_cam[:3, :3], T_desk_cam[:3, 3])
print("  camera in Unity: pos", fmt(p_cam_u), " Euler",
      fmt(euler_unity_zxy(R_cam_u), 2))

# --- the chain at frame 100 ----------------------------------------------
T_cam_obj = make_T(R_obj, t_obj)
T_desk_obj = T_desk_cam @ T_cam_obj
R_w, t_w = T_desk_obj[:3, :3], T_desk_obj[:3, 3]
print("\nT_desk_obj(100) = T_desk_cam @ T_cam_obj: R =\n" + fmt(R_w)
      + "\n  t = " + fmt(t_w))
print("  det R =", fmt(np.linalg.det(R_w), 12))

# --- Unity map ------------------------------------------------------------
p_u, R_u = unity_from_world(R_w, t_w)
eul = euler_unity_zxy(R_u)
print("\nUnity: p_U = P t =", fmt(p_u), "\n  R_U = P R P =\n" + fmt(R_u))
print("  det R_U =", fmt(np.linalg.det(R_u), 12),
      " Euler (x,y,z) =", fmt(eul, 2))

# --- cross-check against the pinned world CSV -----------------------------
wr = world[world.frame == FRAME].iloc[0]
csv_p = np.array([wr.unity_px, wr.unity_py, wr.unity_pz])
csv_e = np.array([wr.unity_ex, wr.unity_ey, wr.unity_ez])
csv_t = np.array([wr.tx, wr.ty, wr.tz])
print("\npinned object_world row 100: t_w =", fmt(csv_t),
      "\n  unity p =", fmt(csv_p), " euler =", fmt(csv_e, 2))
print("  reproduction error: pos", f"{np.abs(csv_t - t_w).max():.2e} m,",
      "euler", f"{np.abs(csv_e - eul).max():.2e} deg")

# --- filter effect at frame 100 and overall ------------------------------
fr = filt[filt.frame == FRAME].iloc[0]
fp = np.array([fr.tx, fr.ty, fr.tz])
print("\nfiltered row 100: t_w =", fmt(fp),
      f" moved {1000*np.linalg.norm(fp - t_w):.2f} mm, filled={int(fr.filled)}")

det_mask = world.detected == 1
n_missing = int((~det_mask).sum())
p_raw = world.loc[det_mask, ["tx", "ty", "tz"]].to_numpy()
p_fil = filt.loc[det_mask.values, ["tx", "ty", "tz"]].to_numpy()
moved = 1000 * np.linalg.norm(p_raw - p_fil, axis=1)
print(f"\nfilter over the recording: {n_missing} undetected frames,"
      f" filled flag on {int(filt.filled.sum())} frames;"
      f" measured frames moved median {np.median(moved):.1f} mm,"
      f" max {moved.max():.1f} mm")

step_raw = 1000 * np.linalg.norm(np.diff(p_raw, axis=0), axis=1)
allf = filt[["tx", "ty", "tz"]].to_numpy()
step_fil = 1000 * np.linalg.norm(np.diff(allf, axis=0), axis=1)
print(f"  frame-step p95: raw {np.percentile(step_raw, 95):.1f} mm"
      f" -> filtered {np.percentile(step_fil, 95):.1f} mm")

# object travel range (world frame)
pw = world.loc[det_mask, ["tx", "ty", "tz"]].to_numpy()
rng = pw.max(axis=0) - pw.min(axis=0)
d = np.linalg.norm(np.diff(p_fil, axis=0), axis=1)
print(f"  object range (x,y,z) = {fmt(rng, 3)} m;"
      f" path length {np.linalg.norm(np.diff(allf, axis=0), axis=1).sum():.2f} m")

# --- desk anchor drift: per-frame desk detection vs frozen anchor ---------
angs, poss = [], []
for _, r in raw.iterrows():
    got = rt_from_row(r, 2)
    if got is None:
        continue
    Rr, tr = got
    angs.append(geodesic_deg(R_cd, Rr))
    poss.append(1000 * np.linalg.norm(tr - t_cd))
angs, poss = np.array(angs), np.array(poss)
g100 = rt_from_row(row, 2)
print(f"\ndesk anchor drift (per-frame id2 vs frozen): frame 100 "
      f"{geodesic_deg(R_cd, g100[0]):.3f} deg / {1000*np.linalg.norm(g100[1]-t_cd):.2f} mm;"
      f"\n  whole recording rot p95 {np.percentile(angs, 95):.3f} deg"
      f" (max {angs.max():.3f}), pos p95 {np.percentile(poss, 95):.2f} mm")
print(f"  lever-arm effect: 0.088 deg x 3.20 m = "
      f"{np.radians(0.088)*3.20*1000:.1f} mm at the wall")

# --- wall at frame 100 (cross-check role) --------------------------------
got0 = rt_from_row(row, 0)
if got0 is not None:
    R0, t0 = got0
    T_desk_wall_100 = T_desk_cam @ make_T(R0, t0)
    T_desk_wall_cal = T_desk_cam @ np.array(calib["T_cam_wall"])
    print(f"\nwall at frame 100 in desk frame vs calibrated: "
          f"{geodesic_deg(T_desk_wall_cal[:3, :3], T_desk_wall_100[:3, :3]):.3f} deg, "
          f"{1000*np.linalg.norm(T_desk_wall_100[:3, 3]-T_desk_wall_cal[:3, 3]):.1f} mm")
    print("  calibrated wall position in world:", fmt(T_desk_wall_cal[:3, 3], 3),
          " camera:", fmt(T_desk_cam[:3, 3], 3))

# --- P properties ---------------------------------------------------------
P = WORLD_TO_UNITY
print("\nP: det =", f"{np.linalg.det(P):.0f}", " P@P == I:",
      bool(np.allclose(P @ P, np.eye(3))))
print("  det(P R_w P) =", fmt(np.linalg.det(P @ R_w @ P), 12))

# gravity/scene geometry from calibration (quoted in text)
sg = calib["scene_geometry"]
print("\nscene_geometry: stand tilt", f"{sg['desk_stand_tilt_deg']:.2f} deg,",
      "seed-vs-wall", f"{sg['gravity_seed_dev_deg']:.2f} deg,",
      "cube", f"{sg['object_cube_size_m']*1000:.0f} mm,",
      "origin above tabletop", f"{1000*sg['origin_above_tabletop_m']:.1f} mm,",
      f"FOV {sg['sensor_fov_x_deg']:.1f} x {sg['sensor_fov_y_deg']:.1f} deg")

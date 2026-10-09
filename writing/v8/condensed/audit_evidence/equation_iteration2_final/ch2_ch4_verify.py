#!/usr/bin/env python3
"""Final Chapter 2-4 equation audit after D-080/D-082/D-083 corrections.

No experiment, builder, or frozen implementation is executed for mutation.
Rodrigues axis operators and direct geometric constructions are independent
of the frozen functions subsequently compared. Tolerances are numerical
diagnostics (D-072's 1e-9), not experimental acceptance criteria.
The original diagnostic and findings remain in sibling equation_iteration2.
By default, verify the rebuilt chapter parts. --docx PATH additionally reads
the parent's assembled deliverable instead of those parts for identity checks.
"""
import argparse
import ast
import csv
import hashlib
import itertools
import json
import math
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np
from lxml import etree

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
STEM = "recording_20260831_065553"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--docx", type=Path)
args = parser.parse_args()
CHAPTER_NAMES = {2: "Chapter_2_Experimental_Setup",
                 3: "Chapter_3_Kinematic_Modeling", 4: "Chapter_4_Object_Tracking"}
DOCUMENTS = ([args.docx.resolve()] if args.docx else
             [ROOT / f"writing/v8/condensed/{name}.docx" for name in CHAPTER_NAMES.values()])
PATHS = [
    *[str(path.relative_to(ROOT)) for path in DOCUMENTS],
    *[f"writing/v8/condensed/scripts/build_ch{k}.py" for k in (2, 3, 4)],
    "writing/v8/condensed/scripts/eqn.py",
    "v1/kinematics/root_frame.py", "v1/kinematics/shoulder.py",
    "v1/aruco/frames.py", "v1/aruco/calibrate_scene.py",
    "v1/mediapipe/filter_landmarks.py", "v1/kinematics/occlusion_ext.py",
    "v1/aruco/filter_object_track.py", "eval/common/clean_object_track.py",
    "Unity/Assets/Scripts/IntegratedSceneReceiver.cs",
    f"v1/mediapipe/output/{STEM}_landmarks_filtered.csv",
    f"eval/output/{STEM}_aruco_raw_scaled.csv",
    f"eval/output/{STEM}_aruco_raw_scaled.meta.json",
    "eval/output/scene_calibration_r6bc.json",
    *[f"eval/output/{STEM}_scaled_object_world{x}" for x in (
        ".csv", "_filtered.csv", "_filtered_clean.csv", "_filtered.meta.json")],
    "writing/v8/condensed/figures/ch3_fig_tpose_a.png",
    "writing/v8/condensed/figures/ch3_fig_torso_schematic.png",
    "writing/v8/condensed/scripts/make_ch3_torso_schematic_fig.py",
    "writing/v8/condensed/figures/ch2_fig_sensor_scene.png",
    "writing/v8/condensed/figures/ch3_fig_swing_twist.png",
    "writing/v8/condensed/scripts/make_ch2_sensor_scene_final_fig.py",
    "writing/v8/condensed/scripts/make_ch3_swing_twist_final_fig.py",
    "eval/output/recovery_r6b/angles_recovery.csv",
]
manifest = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in PATHS}
checks = []
facts = {}


def check(name, error, tol=1e-9):
    checks.append({"name": name, "max_abs_error": float(error),
                   "tolerance": tol, "pass": bool(error <= tol)})


def equal(name, a, b, tol=1e-9):
    check(name, np.max(np.abs(np.asarray(a, dtype=float) - np.asarray(b, dtype=float))), tol)


def rows(path):
    with (ROOT / path).open() as f:
        return list(csv.DictReader(f))


def unit(x):
    return np.asarray(x) / np.linalg.norm(x)


def op(axis, degree):
    """Rodrigues formula, independently avoids copied Euler matrices."""
    a = np.eye(3)[axis]
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    t = math.radians(degree)
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def euler_product(x, y, z):
    return op(1, y) @ op(0, x) @ op(2, z)


def shoulder_product(y, z, t):
    return op(1, y) @ op(2, z) @ op(0, t)


def transform(R, p):
    T = np.eye(4)
    T[:3, :3], T[:3, 3] = R, p
    return T


def inverse(T):
    return transform(T[:3, :3].T, -T[:3, :3].T @ T[:3, 3])


def solve(u, f):
    a = unit(u)
    tz = math.degrees(math.asin(float(np.clip(a[1], -1, 1))))
    ty = math.degrees(math.atan2(-a[2], a[0])) if abs(a[1]) < 1 - 1e-12 else 0
    fp = op(2, -tz) @ op(1, -ty) @ f
    tt = math.degrees(math.atan2(-fp[1], fp[2]))
    R = shoulder_product(ty, tz, tt)
    g = unit(R.T @ f)
    ey = math.degrees(math.atan2(-g[2], g[0]))
    ez = math.degrees(math.asin(float(np.clip(g[1], -1, 1))))
    return np.array([ty, tz, tt]), np.array([ey, ez]), R, fp, g


sys.path.insert(0, str(ROOT / "v1/kinematics"))
import root_frame
import shoulder
sys.path.insert(0, str(ROOT / "v1/aruco"))
import frames

F = np.diag([1., -1., 1.])
S = np.array([[1., 0, 0], [0, 0, 1.], [0, 1., 0]])
M = np.diag([-1., 1., 1.])
for name, mapping in (("F", F), ("S", S), ("M", M)):
    equal(f"basis map {name} is involutory", mapping @ mapping, np.eye(3))
    equal(f"basis map {name} determinant", np.linalg.det(mapping), -1)

# A ramp distinguishes the conventional window MAD from the implemented
# rolling median of each point's own rolling-median residual.
ramp=np.arange(15,dtype=float)*.01
local_median=np.array([np.median(ramp[max(0,i-3):min(len(ramp),i+4)]) for i in range(len(ramp))])
facts["hampel_definition_counterexample"]={"input_m":ramp,"window":7,"center_index":7,"conventional_window_mad_m":float(np.median(abs(ramp[4:11]-np.median(ramp[4:11])))),"implemented_rolling_residual_median_m":float(np.median(abs(ramp-local_median)[4:11]))}

# Independently evaluate the stated two rolling-median passes, then compare
# their actual spike masks with the frozen filter (including missing values).
sys.path.insert(0, str(ROOT / "v1/mediapipe"))
import filter_landmarks

def centered_median(values):
    result = np.full_like(values, np.nan)
    for index in range(len(values)):
        for axis in range(values.shape[1]):
            window = values[max(0,index-3):min(len(values),index+4),axis]
            finite = window[np.isfinite(window)]
            if len(finite) >= 3:
                result[index,axis] = np.median(finite)
    return result

for label, spike in (("ramp", False), ("spike and missing point", True)):
    samples = np.column_stack([ramp, 2*ramp, -ramp])
    if spike:
        samples[7,1] += .15
        samples[2] = np.nan
    residual = abs(samples-centered_median(samples))
    scale = 1.4826*centered_median(residual)
    expected = ((residual > np.maximum(.02,3*scale)).any(axis=1)
                & np.isfinite(samples).all(axis=1))
    equal("C234-09 stated rolling-residual Hampel mask: " + label,
          expected, filter_landmarks.hampel_mask(samples,7,3.,.02))

root_errors, expansion_errors, arm_errors, elbow_zeros, mirror_errors = [], [], [], [], []
for x, y, z in itertools.product((-80., -31., 0., 47., 80.), (-160., -23., 59., 175.), (-70., 0., 130.)):
    R = euler_product(x, y, z)
    xr, yr, zr = map(math.radians, (x, y, z))
    cx, sx, cy, sy, cz, sz = math.cos(xr), math.sin(xr), math.cos(yr), math.sin(yr), math.cos(zr), math.sin(zr)
    expanded = np.array([[cy*cz+sy*sx*sz, -cy*sz+sy*sx*cz, sy*cx],
                         [cx*sz, cx*cz, -sx],
                         [-sy*cz+cy*sx*sz, sy*sz+cy*sx*cz, cy*cx]])
    expansion_errors.append(np.max(np.abs(R-expanded)))
    got = [math.degrees(math.asin(-R[1, 2])), math.degrees(math.atan2(R[0, 2], R[2, 2])), math.degrees(math.atan2(R[1, 0], R[1, 1]))]
    root_errors.append(np.max(np.abs(euler_product(*got)-R)))
    root_errors.append(np.max(np.abs(root_frame.recompose_zxy(root_frame.euler_unity_zxy(R))-R)))
check("3.15-3.17 independent 60-case matrix expansion", max(expansion_errors))
check("3.17 independent and frozen Euler round trips", max(root_errors))
locks = []
for x, y, z in itertools.product((-90., 90.), (-160., 0., 47.), (-59., 0., 120.)):
    R = euler_product(x, y, z)
    out_y = math.degrees(math.atan2((1 if x > 0 else -1) * R[0, 1], R[0, 0]))
    locks.append(np.max(np.abs(euler_product(x, out_y, 0)-R)))
    locks.append(np.max(np.abs(root_frame.recompose_zxy(root_frame.euler_unity_zxy(R))-R)))
check("3.17 both exact gimbal-lock branches, 18 cases", max(locks))

for y, z, t, e in itertools.product((-133., 0., 53.), (-77., 0., 66.), (-125., 0., 72.), (-170., -90., -19.8)):
    R = shoulder_product(y, z, t)
    u, f = R @ np.array([.32, 0, 0]), R @ op(1, e) @ np.array([.2, 0, 0])
    sh, el, Rs, fp, g = solve(u, f)
    arm_errors += [np.max(np.abs(Rs @ [.32, 0, 0]-u)), np.max(np.abs(Rs @ op(1, el[0]) @ [.2, 0, 0]-f))]
    frozen_sh, frozen_el, _ = shoulder.solve_right_arm(np.zeros(3), u, u+f, np.eye(3))
    arm_errors.append(np.max(np.abs(Rs-shoulder.recompose_shoulder(frozen_sh))))
    elbow_zeros.append(abs(el[1]))
    lsh, lel, _ = shoulder.solve_left_arm(np.zeros(3), M @ u, M @ (u+f), np.eye(3))
    mirror_errors.extend([np.max(abs(lsh-sh)), np.max(abs(lel-el)),
                          np.max(abs(M @ Rs @ M @ [-.32, 0, 0]-M @ u)),
                          np.max(abs(M @ Rs @ op(1, el[0]) @ M @ [-.2, 0, 0]-M @ f))])
check("3.18-3.24 reconstruct both measured segments, 81 cases", max(arm_errors))
check("3.24 ez zero for observable exact geometry", max(elbow_zeros))
check("left mirror preserves angles and reconstructed segment directions", max(mirror_errors))
vertical = []
for z, y, t in itertools.product((-90., 90.), (-76., 39.), (-91., 22.)):
    R = shoulder_product(y, z, t)
    u, f = R @ [.32, 0, 0], R @ op(1, -64.) @ [.2, 0, 0]
    sh, el, _, _, _ = solve(u, f)
    vertical.append(np.max(np.abs(shoulder_product(*sh) @ op(1, el[0]) @ [.2, 0, 0]-f)))
check("3.21 exact vertical shoulder branch folds azimuth into twist", max(vertical))

# Chordal projection must flip the smallest singular direction when needed.
for label, A in (("ordinary", euler_product(12, 34, 56)+np.diag([.01, -.02, .03])),
                 ("reflection branch", np.diag([.8, .5, -.2]))):
    U, sig, Vt = np.linalg.svd(A)
    R = U @ np.diag([1, 1, np.linalg.det(U @ Vt)]) @ Vt
    equal(f"2.1 {label} proper orthogonal result", R.T @ R, np.eye(3))
    equal(f"2.1 {label} det +1", np.linalg.det(R), 1)
    optimal_sq = float(np.sum(sig**2)+3-2*(sig[0]+sig[1]+np.linalg.det(U @ Vt)*sig[2]))
    equal(f"2.1 {label} attains Procrustes minimum", np.sum((A-R)**2), optimal_sq)
    equal(f"2.1 {label} frozen implementation agrees", frames.chordal_mean([A]), R)

landmarks = rows(f"v1/mediapipe/output/{STEM}_landmarks_filtered.csv")
row = next(r for r in landmarks if int(r["frame"]) == 533)
names = {11:"left_shoulder",12:"right_shoulder",13:"left_elbow",14:"right_elbow",15:"left_wrist",16:"right_wrist",23:"left_hip",24:"right_hip"}
camera = {i: np.array([float(row[f"{n}_{a}"]) for a in "xyz"]) for i,n in names.items()}
p = {i: F @ v for i,v in camera.items()}
x = unit(p[24]-p[23]); spine = p[12]-p[24]; z = unit(np.cross(x, spine)); y = np.cross(z,x)
R = np.column_stack([x,y,z])
equal("3.7-3.11 independent frame 533 construction vs frozen", R, root_frame.build_root_frame(p[23],p[24],p[12]))
ua, fa = p[14]-p[12], p[16]-p[14]
u, f = R.T @ ua, R.T @ fa
sh, el, Rsh, fp, g = solve(u,f)
T1 = transform(R,p[24]); T2 = transform(np.eye(3),R.T @ spine); T3 = transform(Rsh,u)
chain = T1 @ T2 @ T3
wrist = inverse(chain) @ np.r_[p[16],1]
equal("3.6 chain reaches measured elbow using homogeneous point", chain @ [0,0,0,1], np.r_[p[14],1])
equal("3.4 inverse chain wrist coordinates vs direct local vector", wrist[:3], Rsh.T @ f)
equal("3.13 shoulder z offset exactly zero", T2[2,3], 0)
equal("3.14 rotation orthogonal and origin in shoulder basis", inverse(T1 @ T2) @ chain, T3)
facts["ch3_frame533"] = {"camera":camera,"camera_prime":p,"hip_length_m":np.linalg.norm(p[24]-p[23]),"spine_length_m":np.linalg.norm(spine),"hip_spine_angle_deg":math.degrees(math.acos(np.dot(x,unit(spine)))),"root_rotation":R,"root_euler_deg":root_frame.euler_unity_zxy(R),"root_T":T1,"shoulder_T":T2,"elbow_T":T3,"upper_arm_camera_prime":ua,"upper_arm_parent":u,"upper_arm_unit":unit(u),"upper_arm_length_m":np.linalg.norm(u),"forearm_parent":f,"forearm_length_m":np.linalg.norm(f),"forearm_unswung":fp,"shoulder_angles_deg":sh,"elbow_angles_deg":el,"forearm_unit_elbow":g,"wrist_elbow_m":wrist[:3],"left_angles_deg":solve(M @ R.T @ (p[13]-p[11]), M @ R.T @ (p[15]-p[13]))[:2],"all_source_flags_zero":{n:{k:row[k] for k in row if k.startswith(n+"_") and (k.endswith("_flag") or k.endswith("_src"))} for n in names.values()}}
def rounded(name, value, printed, digits):
    equal(name, np.round(value,digits),printed)
rounded("Table 3.1 all raw Camera positions",list(camera.values()),[[.22,-.34,1.36],[-.16,-.33,1.31],[.28,-.03,1.38],[-.20,-.04,1.19],[.24,.20,1.25],[-.20,.11,1.06],[.12,.18,.99],[-.06,.19,.99]],2)
rounded("3.5 root axes and rotation",R,[[-1.,-.06,.01],[-.05,.85,.53],[-.04,.53,-.85]],2)
rounded("3.5 shoulder origin in torso",T2[:3,3],[.07,.63,0],2)
rounded("3.5 root Euler values",root_frame.euler_unity_zxy(R),[-32.1,179.5,-3.3],1)
rounded("3.5 upper arm Camera prime and parent vectors",[ua,u],[[-.04,-.29,-.12],[.05,-.31,-.05]],2)
rounded("3.5 arm unit direction",unit(u),[.17,-.97,-.16],2)
rounded("3.5 forearm parent and unswung",[f,fp],[[.01,-.20,.03],[.19,-.06,.03]],2)
rounded("3.5 right shoulder angles",sh,[43.,-76.6,59.9],1)
rounded("3.5 right elbow angles",el,[-19.8,0],1)
rounded("3.5 normalized elbow-frame direction",g,[.94,0,.34],2)
rounded("3.5 elbow frame shoulder-relative rotation",Rsh,[[.17,.95,-.27],[-.97,.12,-.20],[-.16,.30,.94]],2)
rounded("3.5 wrist in elbow frame",wrist[:3],[.19,0,.07],2)
lsh,lel= facts["ch3_frame533"]["left_angles_deg"]
rounded("3.5 left shoulder and elbow angles",np.r_[lsh,lel[0]],[76.1,-53.5,108.9,-37.3],1)

# Concrete counterexamples / dimensional evidence, recorded as findings.
bad_swap = np.diag([-1.,1.,-1.])[:,[0,2,1]]
proper_wrong = np.column_stack([[-1.,0,0],[0,0,-1.],[0,-1.,0]])
facts["baseline_defect_counterexamples"] = {"closing_origin_lhs_dimension":3,"closing_origin_rhs_dimension":len(chain @ [0,0,0,1]),"closing_wrist_matrix_shape":list(chain.shape),"closing_wrist_input_shape":list(p[16].shape),"baseline_g_hat_rhs_norm_m":np.linalg.norm(Rsh.T @ f),"g_hat_required_norm":1,"three_plus_four_per_arm":3+2*4,"actual_stream_field_count":3+2*(3+2),"reference_swap_y_z_determinant":np.linalg.det(bad_swap),"reference_forward_as_up_proper_alternative":proper_wrong,"reference_forward_as_up_proper_euler":root_frame.euler_unity_zxy(proper_wrong),"claimed_90_0_0_matrix":euler_product(90,0,0),"left_zero_pose_positive_x_in_parent":M @ np.eye(3) @ M @ [1.,0,0],"left_zero_pose_upper_arm_direction":[-1.,0,0]}
try:
    inverse(chain) @ p[16]
except ValueError as e:
    facts["baseline_defect_counterexamples"]["closing_wrist_numpy_exception"] = str(e)

# Check the corrected dimensionless and homogeneous expressions directly.
equal("C234-01 corrected elbow-origin product keeps homogeneous coordinate",
      (chain @ [0,0,0,1])[3], 1)
equal("C234-01 corrected wrist inverse keeps homogeneous coordinate", wrist[3], 1)
equal("C234-02 corrected printed normalization yields unit forearm",
      np.linalg.norm((R @ Rsh).T @ (p[16]-p[14]) / np.linalg.norm(p[16]-p[14])), 1)
equal("C234-02 corrected normalized Camera'-based formula matches solved g",
      (R @ Rsh).T @ (p[16]-p[14]) / np.linalg.norm(p[16]-p[14]), g)
equal("C234-03 retained T-pose decodes to the stated angles",
      root_frame.euler_unity_zxy(np.diag([-1.,1.,-1.])), [0.,180.,0.])
zero_twist_errors = []
for azimuth, elevation in itertools.product((-133., 53.), (-77., 66.)):
    swung_forearm = shoulder_product(azimuth, elevation, 0.) @ op(1,-64.) @ [.2,0,0]
    operated = op(2,-elevation) @ op(1,-azimuth) @ swung_forearm
    zero_twist_errors.append(np.max(abs(unit(operated[1:])-[0.,1.])))
check("C234-04 operated perpendicular direction is +z at zero twist",
      max(zero_twist_errors))
equal("C234-05 zero-pose left frame shares root orientation", M @ np.eye(3) @ M, np.eye(3))
equal("C234-05 left arm extends along its negative x", M @ np.eye(3) @ M @ [-1.,0,0], [-1.,0,0])
stored_row = rows("eval/output/recovery_r6b/angles_recovery.csv")[0]
angle_columns = ["root_ex","root_ey","root_ez","Rsh_y","Rsh_z","Rsh_tau",
                 "Rel_y","Rel_z","Lsh_y","Lsh_z","Lsh_tau","Lel_y","Lel_z"]
equal("C234-06 all thirteen stated angular fields exist in the saved output",
      sum(name in stored_row for name in angle_columns), 13)
facts["corrected_frame533_relations"] = {
    "elbow_origin_homogeneous":chain @ [0,0,0,1],
    "wrist_elbow_homogeneous":wrist,
    "dimensionless_g":g,
    "stored_angular_columns":angle_columns,
    "independent_angular_quantities":3+2*4,
}

raw = rows(f"eval/output/{STEM}_aruco_raw_scaled.csv")
cal = json.loads((ROOT / "eval/output/scene_calibration_r6bc.json").read_text())
def rt(r, mid):
    return np.array([float(r[f"m{mid}_r{i}{j}"]) for i in (1,2,3) for j in (1,2,3)]).reshape(3,3), np.array([float(r[f"m{mid}_t{a}"]) for a in "xyz"])
stat = [rt(r,2) for r in raw if int(r["m2_detected"])][:10]
A = np.mean([q[0] for q in stat],axis=0)
U, sig, Vt = np.linalg.svd(A)
anchor = transform(U @ np.diag([1,1,np.linalg.det(U @ Vt)]) @ Vt, np.mean([q[1] for q in stat],axis=0))
equal("2.1 first ten detections reproduce stored anchor", anchor, cal["T_cam_desk"])
inv = inverse(anchor)
equal("4.2 rigid inverse against generic matrix inverse", inv, np.linalg.inv(anchor))
ro,to = rt(next(r for r in raw if int(r["frame"]) == 533),1)
obj = inv @ transform(ro,to)
equal("4.1 object block rotation", obj[:3,:3], inv[:3,:3] @ ro)
equal("4.1 object block translation", obj[:3,3], inv[:3,:3] @ to + inv[:3,3])
B = transform(euler_product(13,-27,69),[.2,-.7,.1])
equal("4.1 recalibrated camera-placement invariance", inverse(B @ anchor) @ (B @ transform(ro,to)),obj)
facts["frozen_anchor_after_camera_move_counterexample_m"] = float(np.linalg.norm((inv @ B @ transform(ro,to))[:3,3]-obj[:3,3]))
gravity = np.array(cal["scene_geometry"]["gravity_up_world"])
tablepoint = np.array(cal["scene_geometry"]["tabletop_point_world"])
facts["ch4_frame533"] = {"rotation_mean":A,"mean_determinant":np.linalg.det(A),"projection_max_change":np.max(abs(anchor[:3,:3]-A)),"anchor":anchor,"inverse_anchor":inv,"camera_range_from_world_cm":100*np.linalg.norm(inv[:3,3]),"camera_height_model_cm":100*np.dot(inv[:3,3]-tablepoint,gravity),"camera_object_position":to,"camera_object_range_cm":100*np.linalg.norm(to),"world_object_T":obj,"object_height_model_cm":100*np.dot(obj[:3,3]-tablepoint,gravity),"gravity_world":gravity,"gravity_tilt_deg":math.degrees(math.acos(gravity[2])),"origin_height_model_mm":-1000*np.dot(tablepoint,gravity),"rail_plus_half_cube_cm":3.8+7/2}
rawmeta = json.loads((ROOT / f"eval/output/{STEM}_aruco_raw_scaled.meta.json").read_text())
intr=rawmeta["color_intrinsics"]
facts["historical_photo_projection_pixels"]={str(i):[int(round(intr["fx"]*camera[i][0]/camera[i][2]+intr["ppx"])),int(round(intr["fy"]*camera[i][1]/camera[i][2]+intr["ppy"]))] for i in (12,23,24)}
seed = unit(inv[:3,:3] @ rawmeta["tabletop"]["up_cam"])
facts["tabletop_model_vs_depth_fit"] = {"normal_angle_deg":math.degrees(math.acos(np.dot(seed,gravity))),"object_fitted_plane_signed_distance_cm":100*np.dot(obj[:3,3]-tablepoint,seed),"object_height_along_gravity_to_fitted_plane_cm":100*np.dot(obj[:3,3]-tablepoint,seed)/np.dot(seed,gravity),"camera_fitted_plane_signed_distance_cm":100*np.dot(inv[:3,3]-tablepoint,seed),"origin_fitted_plane_signed_distance_mm":-1000*np.dot(tablepoint,seed)}
rounded("4.3 printed mean matrix",A,[[1,0,-.02],[-.02,-.48,-.88],[-.01,.88,-.48]],2)
rounded("4.3 printed inverse-anchor translation",inv[:3,3],[-.01,-.39,.43],2)
rounded("4.3 printed Camera object translation",to,[-.21,.16,1.02],2)
rounded("4.3 printed World object translation",obj[:3,3],[-.24,.43,-.19],2)
rounded("4.3 printed World object rotation",obj[:3,:3],[[1,.01,.07],[.05,.52,-.85],[-.05,.86,.52]],2)
rounded("4.3 printed gravity",gravity,[-.02,.53,.85],2)
rounded("4.3 ranges and gravity-model heights",[100*np.linalg.norm(inv[:3,3]),100*np.dot(inv[:3,3]-tablepoint,gravity),100*np.dot(obj[:3,3]-tablepoint,gravity)],[58.4,15.4,6.3],1)
equal("C234-07 horizontal tabletop model has unit gravity normal", np.linalg.norm(gravity), 1.)
equal("C234-07 model origin height equals the saved calibration",
      -np.dot(tablepoint,gravity), cal["scene_geometry"]["origin_above_tabletop_m"])
facts["descriptive_height_discrepancy_cm"] = 3.8+7/2-100*np.dot(obj[:3,3]-tablepoint,gravity)

world = rows(f"eval/output/{STEM}_scaled_object_world.csv")
filtered = rows(f"eval/output/{STEM}_scaled_object_world_filtered.csv")
clean = rows(f"eval/output/{STEM}_scaled_object_world_filtered_clean.csv")
pos = np.array([[float(r[f"unity_p{a}"]) for a in "xyz"] for r in filtered])
rot = np.array([euler_product(*[float(r[f"unity_e{a}"]) for a in "xyz"]) for r in filtered])
ts = np.array([float(r["time_s"]) for r in filtered])
det = np.array([int(r["detected"]) == 1 for r in filtered])
keep = np.zeros(len(filtered),bool); last = None
for i in range(len(filtered)):
    if not det[i] or not np.isfinite(pos[i]).all():
        continue
    if last is None:
        keep[i] = True; last = i; continue
    dt = ts[i]-ts[last]
    angle = math.degrees(math.acos(float(np.clip((np.trace(rot[last].T @ rot[i])-1)/2,-1,1))))
    if dt > 0 and np.linalg.norm(pos[i]-pos[last]) <= dt and angle <= 400*dt:
        keep[i] = True; last = i
equal("4.3 independent full-recording cleaning mask matches pinned CSV", keep, np.array([int(r["detected"])==1 for r in clean]))
invariance = []
for i in (533,785,786,787):
    j = i-1
    world_rot = S @ rot[i] @ S
    previous_world_rot = S @ rot[j] @ S
    invariance += [abs(np.linalg.norm(pos[i]-pos[j])-np.linalg.norm(S @ pos[i]-S @ pos[j])),abs(np.trace(rot[j].T @ rot[i])-np.trace(previous_world_rot.T @ world_rot))]
check("4.3 improper conjugation preserves translation norms and relative rotation trace",max(invariance))
facts["ch4_gap"] = {"detected":int(det.sum()),"total":len(det),"rejected_detected_frames":np.flatnonzero(det & ~keep),"blanked_frames":np.flatnonzero(~keep),"raw_neighbor_x_cm":[100*float(world[i]["tx"]) for i in (785,787)],"interpolated_vs_neighbor_mean_mm":1000*np.linalg.norm(np.array([float(filtered[786][a]) for a in ("tx","ty","tz")])-.5*np.array([[float(world[i][a]) for a in ("tx","ty","tz")] for i in (785,787)]).sum(axis=0)),"gap_step_mm":1000*np.linalg.norm(pos[786]-pos[785]),"gap_angle_deg":math.degrees(math.acos(np.clip((np.trace(rot[785].T @ rot[786])-1)/2,-1,1))),"next_kept_step_mm":1000*np.linalg.norm(pos[787]-pos[785]),"filter_metadata":json.loads((ROOT / f"eval/output/{STEM}_scaled_object_world_filtered.meta.json").read_text())}

# Inspect every expression in the final documents, without running builders.
NS = {"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main", "m":"http://schemas.openxmlformats.org/officeDocument/2006/math"}
def plain(e):
    return "".join(e.xpath(".//w:t/text()|.//m:t/text()",namespaces=NS))
def ascii_text(s):
    return s.encode("ascii","backslashreplace").decode()
doc_lines = []
doc_math = {ch:Counter() for ch in (2,3,4)}
document_text = {ch:[] for ch in (2,3,4)}
for document in DOCUMENTS:
    with zipfile.ZipFile(document) as zf:
        xml = etree.fromstring(zf.read("word/document.xml"))
    body = xml.find("w:body",NS)
    chapter = None if args.docx else next(ch for ch,name in CHAPTER_NAMES.items()
                                         if document.stem == name)
    for index,el in enumerate(body):
        txt=plain(el)
        heading=re.match(r"^Chapter\s+(\d+)\s*:",txt)
        if etree.QName(el).localname=="p" and heading:
            chapter=int(heading[1])
        if chapter in (2,3,4):
            doc_lines.append(f"{document.name} BODY {index}: {ascii_text(txt)}")
            document_text[chapter].append(txt)
            for equation in el.xpath(".//m:oMath",namespaces=NS):
                doc_math[chapter][plain(equation)] += 1
(OUT / "ch2_ch4_document_extract.txt").write_text("\n\n".join(doc_lines)+"\n")
inventory=[]
contexts={}
expected_math={ch:Counter() for ch in (2,3,4)}
sys.path.insert(0,str(ROOT / "writing/v8/condensed/scripts"))
for ch in (2,3,4):
    path = ROOT / f"writing/v8/condensed/scripts/build_ch{ch}.py"
    tree=ast.parse(path.read_text())
    cutoff=next(i for i,n in enumerate(tree.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="doc" for t in n.targets))
    context={"__file__":str(path)}
    exec(compile(ast.Module(tree.body[:cutoff],type_ignores=[]),str(path),"exec"),context)
    contexts[ch]=context
    for i,item in enumerate(context["content"]):
        kind=item[0]
        fragments=[]
        if kind in ("eq","mth"): fragments=[item[1]]
        elif kind=="pm": fragments=[v for k,v in item[1] if k=="m"]
        elif kind=="tbl":
            def collect(value):
                if isinstance(value,tuple) and len(value)==2 and value[0]=="m":
                    fragments.append(value[1])
                elif isinstance(value,(list,tuple)):
                    for child in value: collect(child)
            collect(item[1])
        if fragments:
            math_text=[]
            for fragment in fragments:
                element=etree.fromstring((f'<m:oMath xmlns:m="{NS["m"]}">'+fragment+"</m:oMath>").encode())
                math_text.append(plain(element))
                expected_math[ch][plain(element)] += 1
            inventory.append({"chapter":ch,"content_index":i,"kind":kind,"equation_id":item[2] if kind=="eq" else None,"math_text":math_text,"all_present_in_document":all(doc_math[ch][t] for t in math_text)})
for ch in (2,3,4):
    equal(f"Chapter {ch}: all numbered, inline, unnumbered and table expressions match final DOCX counts",
          sum((expected_math[ch]-doc_math[ch]).values()) + sum((doc_math[ch]-expected_math[ch]).values()),0)
facts["math_coverage_counts"]={str(ch):dict(Counter(x["kind"] for x in inventory if x["chapter"]==ch)) for ch in (2,3,4)}
facts["documents_checked"]=[str(path.relative_to(ROOT)) for path in DOCUMENTS]

def paragraph_with(text):
    return next(item for item in contexts[3]["content"] if item[0]=="pm"
                and any(kind=="t" and text in value for kind,value in item[1]))

def fragments_of(item):
    return [etree.fromstring((f'<m:oMath xmlns:m="{NS["m"]}">'+value+"</m:oMath>").encode())
            for kind,value in item[1] if kind=="m"]

def homogeneous_blocks(expression):
    count=0
    for matrix in expression.xpath(".//m:m",namespaces=NS):
        matrix_rows=matrix.findall("m:mr",NS)
        if (len(matrix_rows)==2 and all(len(row.findall("m:e",NS))==1 for row in matrix_rows)
                and matrix_rows[0].xpath(".//m:sPre",namespaces=NS)
                and plain(matrix_rows[1])=="1"):
            count+=1
    return count

closing = fragments_of(paragraph_with("Its rotation block is the composed swing and twist"))
equal("C234-01 final printed elbow-origin side includes the homogeneous one",
      homogeneous_blocks(closing[1]),1)
equal("C234-01 final printed wrist inverse includes both homogeneous ones",
      homogeneous_blocks(closing[2]),2)
forearm = fragments_of(paragraph_with("The unit forearm direction there is"))
fraction=forearm[1].find(".//m:f",NS)
denominator=fraction.find("m:den",NS)
equal("C234-02 final printed g definition includes a segment-norm denominator",
      int("16" in plain(denominator) and "14" in plain(denominator)
          and bool(denominator.xpath('.//m:begChr[@m:val="|"]',namespaces=NS))),1)
full_text={ch:"\n".join(values) for ch,values in document_text.items()}
equal("C234-03 final prose omits the false alternative T-pose",
      int("forward direction in the up column" not in full_text[3]),1)
equal("C234-04 final prose identifies un-swinging before zero-twist direction",
      int("After un-swinging, the nonzero perpendicular component" in full_text[3]),1)
equal("C234-05 final caption distinguishes right +x and left -x",
      int("the right arm extends along +x and the left arm along -x" in full_text[3]),1)
equal("C234-06 final prose distinguishes stored and independent angular quantities",
      int("thirteen angular values" in full_text[3] and "two redundant elbow elevation fields" in full_text[3]
          and "The angular state has eleven independent quantities" in full_text[3]),1)
equal("C234-07 final Chapter 2 defines the horizontal gravity-normal tabletop model",
      int("horizontal tabletop model through that point, with its normal set by the calibrated gravity direction" in full_text[2]),1)
equal("C234-07 final Chapter 4 uses the model for all height references",
      int("fitted tabletop plane" not in full_text[4] and "horizontal tabletop model" in full_text[4]),1)
equal("C234-08 final prose retains both heights without the unmeasured assurance",
      int("6.3 cm" in full_text[4] and "7.3 cm" in full_text[4]
          and "within what the coarse fitted plane resolves" not in full_text[4]
          and "sources of the discrepancy have not been separated" in full_text[4]),1)
equal("C234-09 final prose identifies two rolling-median passes",
      int("each sample's own centred rolling median" in full_text[2]
          and "second centred 7-frame rolling median over those residuals" in full_text[2]),1)
manifest[str(Path(__file__).resolve().relative_to(ROOT))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

def convert(x):
    if isinstance(x,np.ndarray): return x.tolist()
    if isinstance(x,np.generic): return x.item()
    raise TypeError(type(x).__name__)
(OUT / "ch2_ch4_input_hashes.json").write_text(json.dumps(manifest,indent=2)+"\n")
(OUT / "ch2_ch4_results.json").write_text(json.dumps({"checks":checks,"facts":facts},indent=2,default=convert)+"\n")
(OUT / "ch2_ch4_math_inventory.json").write_text(json.dumps(inventory,indent=2)+"\n")
print(json.dumps({"checks":len(checks),"pass":sum(x["pass"] for x in checks),"fail":[x for x in checks if not x["pass"]],"coverage":facts["math_coverage_counts"],"evidence":str(OUT)},indent=2))
sys.exit(any(not item["pass"] for item in checks))

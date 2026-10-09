#!/usr/bin/env python3
# Filename: aruco/calibrate_scene.py
# Pipeline B, stage 2: static-scene calibration + world anchoring.
#
# The scene is fixed by assumption, so the two static markers (wall id0,
# desk id2) are calibrated ONCE: their camera-frame poses are averaged over
# the first --calib-frames detections (translation = mean, rotation =
# chordal mean, ARUCO_MODEL.md) and never touched again. The desk marker's
# own frame is the WORLD frame — wall, camera and the moving object are all
# expressed in it, so the reconstruction is identical wherever the depth
# camera is placed. The camera's pose falls out for free as
# T_desk_cam = T_cam_desk^-1.
#
# Outputs:
#   output/scene_calibration.json            static transforms + stability
#   output/<stem>_object_world.csv           per-frame object pose in world
#                                            (+ Unity position/Euler)
#
# Usage:
#   python calibrate_scene.py --csv output/recording_20260328_021733_aruco_raw.csv

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from frames import (MARKERS, STATIC_IDS, OBJECT_ID, WORLD_ID, rt_from_row,
                    make_T, inv_T, chordal_mean, geodesic_deg,
                    unity_from_world, euler_unity_zxy, recompose_zxy)


def calibrate_static(df, mid, n_frames):
    """Average the first n_frames detections of marker `mid` (camera frame).

    Returns (T_cam_marker, stats). Translation: mean. Rotation: chordal
    mean. Stats report each sample's deviation from the mean — the
    stability of the static-scene assumption over the calibration window.
    """
    Rs, ts, frames = [], [], []
    for _, row in df.iterrows():
        rt = rt_from_row(row, mid)
        if rt is None:
            continue
        Rs.append(rt[0])
        ts.append(rt[1])
        frames.append(int(row["frame"]))
        if len(Rs) == n_frames:
            break
    if len(Rs) < n_frames:
        sys.exit(f"[ERROR] marker id{mid} has only {len(Rs)} detections, "
                 f"need {n_frames} for calibration")
    R = chordal_mean(Rs)
    t = np.mean(ts, axis=0)
    pos_dev_mm = [float(np.linalg.norm(tk - t) * 1000.0) for tk in ts]
    ang_dev_deg = [geodesic_deg(R, Rk) for Rk in Rs]
    stats = {
        "samples": len(Rs),
        "frames": frames,
        "pos_dev_mm_max": max(pos_dev_mm),
        "pos_dev_mm_mean": float(np.mean(pos_dev_mm)),
        "ang_dev_deg_max": max(ang_dev_deg),
        "ang_dev_deg_mean": float(np.mean(ang_dev_deg)),
    }
    return make_T(R, t), stats


def pose_block(T_world):
    """A world-frame pose as the json-friendly report: matrix + translation
    (world) and position + ZXY Euler (Unity)."""
    R_w, t_w = T_world[:3, :3], T_world[:3, 3]
    p_u, R_u = unity_from_world(R_w, t_w)
    e_u = euler_unity_zxy(R_u)
    # sanity: orthonormal, det +1, Euler round-trip exact
    assert np.abs(R_w @ R_w.T - np.eye(3)).max() < 1e-9
    assert abs(np.linalg.det(R_w) - 1.0) < 1e-9
    assert geodesic_deg(recompose_zxy(e_u), R_u) < 1e-6
    return {
        "T_world": [[float(x) for x in r] for r in T_world],
        "unity_position": [float(x) for x in p_u],
        "unity_euler_zxy_deg": [float(x) for x in e_u],
    }


def main():
    script_dir = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Calibrate the static ArUco scene and anchor everything to the desk marker.")
    ap.add_argument("--csv", default=str(script_dir / "output" / "recording_20260328_021733_aruco_raw.csv"),
                    help="Raw ArUco pose CSV from extract_aruco_poses.py")
    ap.add_argument("--calib-frames", type=int, default=10,
                    help="Number of detections to average per static marker (default: 10)")
    ap.add_argument("--cube-size", type=float, default=None,
                    help="Object cube edge in meters. Required when the box never "
                         "rests on the desk in the recording (hand-held from the "
                         "start), overriding the marker-height auto-calibration.")
    ap.add_argument("--out", default=None,
                    help="Calibration json (default: output/scene_calibration.json)")
    ap.add_argument("--gravity-from", default=None,
                    help="Scene calibration json of an earlier take of the SAME "
                         "physical scene whose calibrated gravity is carried "
                         "over instead of this take's wall marker in-plane up "
                         "(E-034: the wall card had shifted on the two-hand rail "
                         "take). Both calibrations are in the desk-marker frame; "
                         "the camera-to-desk poses must agree within 3 deg and "
                         "3 cm, and this take's depth-fitted tabletop normal "
                         "must agree with the carried gravity to within the "
                         "source take's own seed agreement plus 5 deg; both "
                         "are checked and recorded in the JSON.")
    args = ap.parse_args()

    csv_path = Path(args.csv).resolve()
    if not csv_path.exists():
        sys.exit(f"[ERROR] CSV not found: {csv_path}")
    df = pd.read_csv(csv_path)
    meta = json.loads(csv_path.with_suffix(".meta.json").read_text())
    out_json = Path(args.out) if args.out else csv_path.parent / "scene_calibration.json"
    out_world = csv_path.parent / f"{csv_path.stem.replace('_aruco_raw', '')}_object_world.csv"

    # --- static calibration (camera frame) -------------------------------
    T_cam, stats = {}, {}
    for mid in STATIC_IDS:
        T_cam[mid], stats[mid] = calibrate_static(df, mid, args.calib_frames)
        role = MARKERS[mid][0]
        print(f"[+] id{mid} ({role}): calibrated from {stats[mid]['samples']} frames — "
              f"pos dev max {stats[mid]['pos_dev_mm_max']:.2f} mm, "
              f"rot dev max {stats[mid]['ang_dev_deg_max']:.3f} deg")

    # --- anchor to the desk (world frame) --------------------------------
    T_desk_cam = inv_T(T_cam[WORLD_ID])          # camera pose in world
    T_desk_wall = T_desk_cam @ T_cam[0]          # wall pose in world
    T_desk_desk = np.eye(4)                      # world origin by definition

    # --- scene geometry (ARUCO_MODEL.md): world z (desk marker normal) is
    # NOT gravity — the card may sit on a tilted stand (intentional, so the
    # camera sees it less foreshortened). The AUTHORITATIVE gravity is the
    # wall marker's in-plane up axis: the wall is physically plumb (user-
    # asserted scene property), and the calibrated wall orientation is good
    # to ~1 deg vs ~6 deg for the depth-plane fit, which is demoted to a
    # sign/sanity seed.
    if meta.get("tabletop") is None:
        sys.exit("[ERROR] raw meta has no tabletop fit — re-run the extractor")
    R_dc, t_dc = T_desk_cam[:3, :3], T_desk_cam[:3, 3]
    seed_w = R_dc @ np.array(meta["tabletop"]["up_cam"])
    seed_w /= np.linalg.norm(seed_w)
    up_w = np.array(T_desk_wall[:3, :3][:, 1])
    if np.dot(up_w, seed_w) < 0:
        up_w = -up_w
    up_w /= np.linalg.norm(up_w)
    gravity_carry = None
    if args.gravity_from:
        # E-034: gravity carried over from an earlier calibration of the
        # same scene (desk-marker frame). The wall marker of this take is
        # not trusted; its deviation from the carried gravity is recorded.
        src = json.loads(Path(args.gravity_from).read_text())
        src_T = np.array(src["T_cam_desk"])
        dR = T_cam[WORLD_ID][:3, :3] @ src_T[:3, :3].T
        rot_dev = float(np.degrees(np.arccos(np.clip((np.trace(dR) - 1) / 2, -1, 1))))
        pos_dev = float(np.linalg.norm(T_cam[WORLD_ID][:3, 3] - src_T[:3, 3]))
        if rot_dev > 3.0 or pos_dev > 0.03:
            sys.exit(f"[ERROR] --gravity-from: camera-to-desk pose differs from "
                     f"the source calibration by {rot_dev:.2f} deg / "
                     f"{pos_dev*1000:.0f} mm; not the same scene")
        wall_up_w = up_w.copy()
        up_w = np.array(src["scene_geometry"]["gravity_up_world"], float)
        up_w /= np.linalg.norm(up_w)
        wall_dev = float(np.degrees(np.arccos(np.clip(np.dot(up_w, wall_up_w), -1, 1))))
        gravity_carry = {
            "from": str(Path(args.gravity_from).resolve()),
            "camera_desk_rot_dev_deg": rot_dev,
            "camera_desk_pos_dev_mm": pos_dev * 1000.0,
            "this_take_wall_up_world": [float(x) for x in wall_up_w],
            "wall_up_dev_from_carried_deg": wall_dev,
        }
        print(f"[i] gravity CARRIED OVER from {Path(args.gravity_from).name}: "
              f"camera-desk agreement {rot_dev:.2f} deg / {pos_dev*1000:.1f} mm; "
              f"this take's wall in-plane up deviates {wall_dev:.2f} deg")
    seed_dev = float(np.degrees(np.arccos(np.clip(np.dot(up_w, seed_w), -1, 1))))
    if gravity_carry is not None:
        # the direct check of the carry-over: this take's depth-fitted
        # tabletop normal must agree with the carried gravity about as
        # well as the source take's own seed did (a joint move of camera
        # and desk card would pass the pose check above but fail here)
        if "gravity_seed_dev_deg" not in src["scene_geometry"]:
            sys.exit("[ERROR] --gravity-from: the source calibration carries "
                     "no gravity_seed_dev_deg; re-run calibrate_scene.py on "
                     "the source take first")
        src_seed = float(src["scene_geometry"]["gravity_seed_dev_deg"])
        if seed_dev > src_seed + 5.0:
            sys.exit(f"[ERROR] --gravity-from: this take's tabletop seed is "
                     f"{seed_dev:.2f} deg from the carried gravity against "
                     f"{src_seed:.2f} deg on the source take; the desk card "
                     f"or the desk has moved relative to gravity")
        gravity_carry["source_seed_dev_deg"] = src_seed
        gravity_carry["this_take_seed_dev_deg"] = seed_dev
    table_pt_w = R_dc @ np.array(meta["tabletop"]["point_desk_cam"]) + t_dc
    stand_tilt = float(np.degrees(np.arccos(np.clip(np.dot(up_w, [0, 0, 1]), -1, 1))))
    print(f"[i] gravity = {'carried over' if gravity_carry else 'wall in-plane up'} | "
          f"depth-seed agreement: {seed_dev:.2f} deg | "
          f"desk-marker stand tilt vs gravity: {stand_tilt:.2f} deg")

    # Object cube size: marker assumed centered on the box's front face and
    # the box resting on the desk -> size = 2 x height of the marker center
    # above the tabletop plane (measured at the LOCAL tabletop point next
    # to the box, so gravity error barely leverages in). When the box never
    # rests on the desk (hand-held recording), --cube-size supplies the
    # physically measured edge instead.
    obj_pts = []
    for _, row in df.iterrows():
        rt = rt_from_row(row, OBJECT_ID)
        if rt is not None:
            obj_pts.append((T_desk_cam @ make_T(*rt))[:3, 3])
    if args.cube_size is not None:
        cube_size = float(args.cube_size)
        cube_src = "supplied via --cube-size (box hand-held in this recording)"
        print(f"[i] object cube size: {cube_size*1000:.0f} mm (--cube-size)")
    elif meta["tabletop"].get("point_obj_cam") is not None:
        pt_obj_w = R_dc @ np.array(meta["tabletop"]["point_obj_cam"]) + t_dc
        cube_raw = 2.0 * float(np.mean([np.dot(p - pt_obj_w, up_w) for p in obj_pts]))
        cube_size = float(np.clip(cube_raw, 0.04, 0.15))
        note = "" if cube_size == cube_raw else f" (clamped from {cube_raw:.3f})"
        cube_src = ("2 x marker height above the local tabletop point "
                    "(marker centered on the cube face, box resting)")
        print(f"[i] object cube size (marker centered on face): {cube_size*1000:.0f} mm{note}")
    else:
        sys.exit("[ERROR] no resting-object tabletop point in the meta and no "
                 "--cube-size given — cannot calibrate the cube edge")

    # World origin (desk marker center) height above the tabletop plane, and
    # the sensor's field of view from the calibrated color intrinsics — both
    # streamed to Unity for the real-scene build (desk top placement, sensor
    # POV camera).
    origin_drop = float(-np.dot(table_pt_w, up_w))
    intr = meta["color_intrinsics"]
    fov_y = float(2.0 * np.degrees(np.arctan(intr["height"] / (2.0 * intr["fy"]))))
    fov_x = float(2.0 * np.degrees(np.arctan(intr["width"] / (2.0 * intr["fx"]))))
    print(f"[i] origin above tabletop: {origin_drop*1000:.1f} mm | "
          f"sensor FOV {fov_x:.1f} x {fov_y:.1f} deg")

    # --- object per frame in world (uses the CALIBRATED desk, not per-frame)
    rows = []
    n_det = 0
    for _, row in df.iterrows():
        rt = rt_from_row(row, OBJECT_ID)
        rec = {"frame": int(row["frame"]), "time_s": row["time_s"],
               "detected": 0}
        if rt is not None:
            n_det += 1
            T_w = T_desk_cam @ make_T(*rt)
            R_w, t_w = T_w[:3, :3], T_w[:3, 3]
            p_u, R_u = unity_from_world(R_w, t_w)
            e_u = euler_unity_zxy(R_u)
            rec["detected"] = 1
            rec.update({k: float(v) for k, v in zip(
                ["tx", "ty", "tz"], t_w)})
            rec.update({f"r{i}{j}": float(R_w[i - 1, j - 1])
                        for i in (1, 2, 3) for j in (1, 2, 3)})
            rec.update({k: float(v) for k, v in zip(
                ["unity_px", "unity_py", "unity_pz"], p_u)})
            rec.update({k: float(v) for k, v in zip(
                ["unity_ex", "unity_ey", "unity_ez"], e_u)})
        rows.append(rec)
    world_df = pd.DataFrame(rows)
    world_df.to_csv(out_world, index=False)
    print(f"[+] object in world: {n_det}/{len(df)} frames -> {out_world.name}")

    calib = {
        "source_csv": str(csv_path),
        "world_frame": f"desk marker id{WORLD_ID} own frame (x/y printed plane, "
                       "z out of the face); world->Unity swaps y/z",
        "calib_frames": args.calib_frames,
        "markers": {str(m): {"role": MARKERS[m][0], "size_m": MARKERS[m][1]}
                    for m in MARKERS},
        "static_stability": {str(m): stats[m] for m in STATIC_IDS},
        "scene_geometry": {
            "gravity_up_world": [float(x) for x in up_w],
            "gravity_up_unity": [float(x) for x in (unity_from_world(np.eye(3), up_w)[0])],
            "tabletop_point_world": [float(x) for x in table_pt_w],
            "tabletop_point_unity": [float(x) for x in (unity_from_world(np.eye(3), table_pt_w)[0])],
            "desk_stand_tilt_deg": stand_tilt,
            "gravity_seed_dev_deg": seed_dev,
            "object_cube_size_m": cube_size,
            "origin_above_tabletop_m": origin_drop,
            "sensor_fov_y_deg": fov_y,
            "sensor_fov_x_deg": fov_x,
            "source": ("gravity = carried over from an earlier calibration "
                       "of the same scene (--gravity-from, E-034); this "
                       "take's wall marker is not used for gravity"
                       if gravity_carry else
                       "gravity = calibrated wall marker in-plane up (wall "
                       "physically plumb; the wall slab is exactly vertical "
                       "by construction)")
                      + "; depth plane fit demoted to "
                      "sign/sanity seed; tabletop point from the desk-"
                      f"marker annulus; cube: {cube_src}",
            **({"gravity_carried_over": gravity_carry} if gravity_carry else {}),
        },
        "T_cam_desk": [[float(x) for x in r] for r in T_cam[WORLD_ID]],
        "T_cam_wall": [[float(x) for x in r] for r in T_cam[0]],
        "poses_world": {
            "desk": pose_block(T_desk_desk),
            "wall": pose_block(T_desk_wall),
            "camera": pose_block(T_desk_cam),
        },
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(out_json, "w") as f:
        json.dump(calib, f, indent=2)
    print(f"[+] calibration: {out_json}")
    for name, blk in calib["poses_world"].items():
        p = blk["unity_position"]
        e = blk["unity_euler_zxy_deg"]
        print(f"    {name:>6}: unity pos ({p[0]:+.3f}, {p[1]:+.3f}, {p[2]:+.3f}) m, "
              f"euler ({e[0]:+7.2f}, {e[1]:+7.2f}, {e[2]:+7.2f}) deg")


if __name__ == "__main__":
    main()

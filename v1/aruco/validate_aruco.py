#!/usr/bin/env python3
# Filename: aruco/validate_aruco.py
# Pipeline B validation: detection quality, calibration math, and the
# camera-invariance of the desk-anchored reconstruction (ARUCO_MODEL.md).
#
# PASS/FAIL checks (exit code = number of failures):
#   1  detection coverage: desk + object on every frame; wall reported
#   2  reprojection error per id below 1 px mean
#   3  camera-invariance: the wall's pose recomputed in the desk frame
#      INDEPENDENTLY at every frame (per-frame desk x per-frame wall, no
#      calibration involved) stays tight around the calibrated T_desk_wall
#      — the scene is static, so any spread is pure measurement error and
#      bounds the ground-truth quality of the pipeline
#   4  depth cross-check: PnP tz vs depth-median z per id (a wrong printed
#      size would show as a proportional z bias)
#   5  calibration/world math: chordal mean on synthetic rotations, SO(3)
#      sanity of every stored matrix, Unity mapping round-trip, and the
#      object_world CSV recomputed exactly from the raw CSV
#
# Usage: python validate_aruco.py

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from frames import (MARKERS, STATIC_IDS, OBJECT_ID, WORLD_ID, rt_from_row,
                    make_T, inv_T, chordal_mean, geodesic_deg,
                    unity_from_world, euler_unity_zxy, recompose_zxy,
                    WORLD_TO_UNITY)

OUT = Path(__file__).resolve().parent / "output"
_ap = argparse.ArgumentParser(description="Pipeline B validation")
_ap.add_argument("--stem", default="recording_20260328_021733",
                 help="Recording stem (default: recording_20260328_021733)")
_ap.add_argument("--calib", default=None,
                 help="Calibration json (default: output/scene_calibration.json)")
_args = _ap.parse_args()
RAW = OUT / f"{_args.stem}_aruco_raw.csv"
WORLD = OUT / f"{_args.stem}_object_world.csv"
CALIB = Path(_args.calib) if _args.calib else OUT / "scene_calibration.json"

npass = nfail = 0


def check(name, ok, detail=""):
    global npass, nfail
    npass += ok
    nfail += not ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def main():
    df = pd.read_csv(RAW)
    wdf = pd.read_csv(WORLD)
    calib = json.loads(CALIB.read_text())
    n = len(df)
    print(f"=== Pipeline B validation on {RAW.name} ({n} frames) ===\n")

    # --- 1 coverage ------------------------------------------------------
    print("--- 1. detection coverage ---")
    c = int(df[f"m{WORLD_ID}_detected"].sum())
    check(f"id{WORLD_ID} (desk, world anchor) detected on every frame", c == n, f"{c}/{n}")
    c = int(df[f"m{OBJECT_ID}_detected"].sum())
    check(f"id{OBJECT_ID} (object) detected on >=95% of frames "
          "(hand may cover it while carried)", c >= 0.95 * n, f"{c}/{n}")
    cw = int(df["m0_detected"].sum())
    print(f"[info] id0 (wall) coverage {cw}/{n} "
          f"({n - cw} dropouts — person crossing in front; wall is a cross-check only)")
    amb = df.loc[df.m0_detected == 1, "m0_ambig"]
    print(f"[info] wall planar ambiguity: {int((amb == 1).sum())} frames gravity/continuity-"
          f"resolved (near-degenerate lobes), {int((amb == 0).sum())} clear, "
          f"{int((amb == 2).sum())} unresolved")
    check("no unresolved ambiguous wall frames", int((amb == 2).sum()) == 0)

    # --- 2 reprojection --------------------------------------------------
    print("\n--- 2. reprojection error ---")
    for mid in (0, WORLD_ID, OBJECT_ID):
        r = df.loc[df[f"m{mid}_detected"] == 1, f"m{mid}_reproj_px"]
        check(f"id{mid} mean reprojection < 1 px",
              r.mean() < 1.0, f"mean {r.mean():.3f} px, max {r.max():.3f} px")

    # --- 3 camera-invariance --------------------------------------------
    print("\n--- 3. camera-invariance (wall in desk frame, per frame) ---")
    T_dw_cal = np.array(calib["poses_world"]["wall"]["T_world"])
    # camera position in world: deviation along the camera->wall view ray is
    # monocular scale noise (~z * corner_err_px / marker_px, ~28 mm at 3 m
    # for 0.3 px on a 32 px marker); lateral deviation is the part that
    # would actually move the wall sideways in the scene.
    cam_w = inv_T(np.array(calib["T_cam_desk"]))[:3, 3]
    ray = T_dw_cal[:3, 3] - cam_w
    ray /= np.linalg.norm(ray)
    pos_dev, along_dev, lat_dev, ang_dev = [], [], [], []
    for _, row in df.iterrows():
        w, d = rt_from_row(row, 0), rt_from_row(row, WORLD_ID)
        if w is None or d is None:
            continue
        T_dw = inv_T(make_T(*d)) @ make_T(*w)
        dp = (T_dw[:3, 3] - T_dw_cal[:3, 3]) * 1000.0
        pos_dev.append(np.linalg.norm(dp))
        along_dev.append(abs(np.dot(dp, ray)))
        lat_dev.append(np.linalg.norm(dp - np.dot(dp, ray) * ray))
        ang_dev.append(geodesic_deg(T_dw[:3, :3], T_dw_cal[:3, :3]))
    pos_dev, ang_dev = np.array(pos_dev), np.array(ang_dev)
    along_dev, lat_dev = np.array(along_dev), np.array(lat_dev)
    print(f"[info] {len(pos_dev)} frames | position dev mm: "
          f"mean {pos_dev.mean():.2f}, p95 {np.percentile(pos_dev, 95):.2f}, max {pos_dev.max():.2f}")
    print(f"[info]   along view ray (monocular scale noise): "
          f"p95 {np.percentile(along_dev, 95):.2f} mm | lateral: "
          f"p95 {np.percentile(lat_dev, 95):.2f} mm")
    print(f"[info] rotation dev deg: mean {ang_dev.mean():.3f}, "
          f"p95 {np.percentile(ang_dev, 95):.3f}, max {ang_dev.max():.3f}")

    # The desk anchor itself over the whole recording: its position must be
    # millimeter-static; its orientation drifts slowly with illumination
    # (measured ~0.07 -> ~0.7 deg over the 30 s session) — that drift times
    # the 2.7 m lever arm to the wall is what dominates the wall's lateral
    # spread, so the lateral bound is DERIVED from the measured desk drift
    # instead of hard-coded.
    T_cd_cal = np.array(calib["T_cam_desk"])
    d_rot = np.array([geodesic_deg(T_cd_cal[:3, :3], rt_from_row(r, WORLD_ID)[0])
                      for _, r in df.iterrows() if rt_from_row(r, WORLD_ID)])
    d_pos = np.array([np.linalg.norm(T_cd_cal[:3, 3] - rt_from_row(r, WORLD_ID)[1]) * 1000.0
                      for _, r in df.iterrows() if rt_from_row(r, WORLD_ID)])
    lever_mm = np.linalg.norm(T_dw_cal[:3, 3]) * 1000.0
    lat_bound = 1.5 * (np.radians(np.percentile(d_rot, 95)) * lever_mm
                       + np.percentile(d_pos, 95))
    print(f"[info] desk anchor over all frames: pos p95 {np.percentile(d_pos, 95):.2f} mm, "
          f"rot p95 {np.percentile(d_rot, 95):.3f} deg "
          f"(x {lever_mm/1000:.2f} m lever = {np.radians(np.percentile(d_rot,95))*lever_mm:.1f} mm at the wall)")
    check("desk anchor position static (p95 < 5 mm)",
          np.percentile(d_pos, 95) < 5.0)
    check("desk anchor orientation drift bounded (p95 < 1.5 deg)",
          np.percentile(d_rot, 95) < 1.5)
    check("wall lateral spread explained by desk drift x lever arm",
          np.percentile(lat_dev, 95) < lat_bound,
          f"lateral p95 {np.percentile(lat_dev, 95):.1f} mm < bound {lat_bound:.1f} mm")
    check("wall range scatter within monocular expectation (along-ray p95 < 35 mm)",
          np.percentile(along_dev, 95) < 35.0)
    check("wall stays put in the desk frame (rot p95 < 3 deg)",
          np.percentile(ang_dev, 95) < 3.0)
    # Lobe-choice regression guard: gravity is now DEFINED as the wall's
    # in-plane up (wall physically plumb), so the check inverts — the
    # depth-fit SEED must agree with the chosen wall lobe. The wrong
    # (anti-plumb) lobe sits ~23 deg away, so agreement < 11 deg both
    # proves the lobe choice and that the seed was valid for making it.
    sd = calib["scene_geometry"]["gravity_seed_dev_deg"]
    check("depth-gravity seed agrees with the wall lobe (< 11 deg)",
          sd < 11.0, f"{sd:.2f} deg")

    # --- 4 depth cross-check --------------------------------------------
    print("\n--- 4. depth cross-check (PnP tz vs depth-median z) ---")
    for mid in (0, WORLD_ID, OBJECT_ID):
        m = (df[f"m{mid}_detected"] == 1) & (df[f"m{mid}_depth_z"] > 0)
        bias = (df.loc[m, f"m{mid}_tz"] - df.loc[m, f"m{mid}_depth_z"]) * 1000.0
        rng = df.loc[m, f"m{mid}_tz"].mean()
        check(f"id{mid} PnP z vs depth z within 5% of range",
              abs(bias.mean()) < 0.05 * rng * 1000.0,
              f"bias {bias.mean():+.1f} mm at {rng:.2f} m range, std {bias.std():.1f} mm")

    # --- 5 math sanity ---------------------------------------------------
    print("\n--- 5. calibration & world math ---")
    # chordal mean recovers a known rotation from spread samples
    rng_ = np.random.default_rng(0)
    R_true = recompose_zxy([20.0, -35.0, 55.0])
    samples = []
    for _ in range(200):
        ax = rng_.normal(size=3)
        ax /= np.linalg.norm(ax)
        th = np.radians(rng_.normal(0, 2.0))
        Kx = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
        samples.append((np.eye(3) + np.sin(th) * Kx + (1 - np.cos(th)) * Kx @ Kx) @ R_true)
    err = geodesic_deg(chordal_mean(samples), R_true)
    check("chordal mean recovers known rotation from noisy samples",
          err < 0.3, f"{err:.4f} deg from truth (2 deg noise, 200 samples)")

    for name, blk in calib["poses_world"].items():
        T = np.array(blk["T_world"])
        R = T[:3, :3]
        ok = (np.abs(R @ R.T - np.eye(3)).max() < 1e-9
              and abs(np.linalg.det(R) - 1) < 1e-9)
        p_u, R_u = unity_from_world(R, T[:3, 3])
        rt = geodesic_deg(recompose_zxy(blk["unity_euler_zxy_deg"]), R_u)
        ok = ok and rt < 1e-6 and np.allclose(p_u, blk["unity_position"])
        check(f"stored '{name}' pose: SO(3) + Unity Euler round-trip exact", ok,
              f"round-trip {rt:.2e} deg")

    # Unity mapping preserves rotations (conjugation by the y/z swap)
    Rr = recompose_zxy([10.0, 20.0, 30.0])
    R_u = WORLD_TO_UNITY @ Rr @ WORLD_TO_UNITY
    check("world->Unity conjugation stays SO(3)",
          np.abs(R_u @ R_u.T - np.eye(3)).max() < 1e-12
          and abs(np.linalg.det(R_u) - 1) < 1e-12)

    # object_world CSV recomputes exactly from raw + calibration
    T_desk_cam = inv_T(np.array(calib["T_cam_desk"]))
    max_p = max_a = max_e = 0.0
    for i in range(0, len(df), 97):
        row, wrow = df.iloc[i], wdf.iloc[i]
        rt = rt_from_row(row, OBJECT_ID)
        if rt is None:
            continue
        T_w = T_desk_cam @ make_T(*rt)
        R_csv = np.array([wrow[f"r{i_}{j}"] for i_ in (1, 2, 3)
                          for j in (1, 2, 3)]).reshape(3, 3)
        t_csv = np.array([wrow["tx"], wrow["ty"], wrow["tz"]])
        max_p = max(max_p, np.linalg.norm(T_w[:3, 3] - t_csv))
        max_a = max(max_a, geodesic_deg(T_w[:3, :3], R_csv))
        p_u, R_u = unity_from_world(T_w[:3, :3], T_w[:3, 3])
        e_csv = [wrow["unity_ex"], wrow["unity_ey"], wrow["unity_ez"]]
        max_e = max(max_e, geodesic_deg(recompose_zxy(e_csv), R_u))
    # Euler tolerance 1e-5 deg: a hand-held box reaches x = -89.9 deg
    # (gimbal lock), where the ZXY recomposition legitimately loses a
    # digit; the underlying rotation matrices still match to 1e-14.
    check("object_world CSV reproduces exactly from raw + calibration",
          max_p < 1e-9 and max_a < 1e-6 and max_e < 1e-5,
          f"pos {max_p:.2e} m, rot {max_a:.2e} deg, euler {max_e:.2e} deg")

    print(f"\n=== {npass} passed, {nfail} failed ===")
    sys.exit(nfail)


if __name__ == "__main__":
    main()

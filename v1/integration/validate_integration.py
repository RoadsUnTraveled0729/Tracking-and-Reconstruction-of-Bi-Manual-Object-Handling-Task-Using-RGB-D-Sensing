#!/usr/bin/env python3
# Filename: integration/validate_integration.py
"""Validation of the integrated person + scene reconstruction (INTEGRATION.md).

Checks (exit code = number of failures):
  1. Anchor math: M = P * R_desk_cam * diag(1,-1,1) is a proper rotation,
     equals R_unity(camera) * Rx(-90) (the receiver's composition), and maps
     person-space up EXACTLY onto the depth-fit gravity direction.
  2. Stream integrity: 899 integrated frames, person and object frame
     numbers aligned 1:1 with the source CSVs.
  3. Physical plausibility: pelvis below the tabletop plane (seated) but
     above the floor; person at working distance from the object.
  4. Unity application exactness: the receiver's logged hip world position
     reproduces anchor.TransformPoint(pelvis) recomputed here from first
     principles (gravity alignment + floor drop + anchor pose), float32.
  5. Unity object log matches the object world CSV (float32).

Run AFTER a full Unity pass:
  python send_integrated_scene.py --dump-csv output/integrated_stream.csv
  (Unity in play mode logging output/unity_person_log.csv + unity_object_log.csv)
  python validate_integration.py
"""
import json
import sys
from pathlib import Path

import argparse
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
_ap = argparse.ArgumentParser(description="Integration validation")
_ap.add_argument("--stem", default="recording_20260224_083945",
                 help="Recording stem (default: recording_20260224_083945)")
_ap.add_argument("--landmarks", default=None,
                 help="Landmark CSV (default: mediapipe/output/<stem>_landmarks_filtered_v2.csv)")
_args = _ap.parse_args()
CALIB = HERE.parent / "aruco" / "output" / "scene_calibration.json"
RAW_META = HERE.parent / "aruco" / "output" / f"{_args.stem}_aruco_raw.meta.json"
OBJECT_RAW_CSV = HERE.parent / "aruco" / "output" / f"{_args.stem}_object_world.csv"
OBJECT_CSV = HERE.parent / "aruco" / "output" / f"{_args.stem}_object_world_filtered.csv"
LANDMARKS_CSV = Path(_args.landmarks) if _args.landmarks else \
    HERE.parent / "mediapipe" / "output" / f"{_args.stem}_landmarks_filtered_v2.csv"

DESK_THICK, LEG_H = 0.03, 0.69  # ArucoSceneReceiver constants

npass = nfail = 0


def check(name, ok, detail=""):
    global npass, nfail
    npass += ok
    nfail += not ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def recompose_zxy(deg):
    """Unity ZXY-applied Euler degrees -> R = Ry·Rx·Rz (KINEMATIC_MODEL.md §4)."""
    x, y, z = np.radians(np.asarray(deg, dtype=float))
    cx, sx, cy, sy, cz, sz = np.cos(x), np.sin(x), np.cos(y), np.sin(y), np.cos(z), np.sin(z)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Ry @ Rx @ Rz


def from_to_rotation(a, b):
    """Rotation matrix turning unit vector a into unit vector b about their
    common normal (Unity Quaternion.FromToRotation semantics)."""
    v = np.cross(a, b)
    c = float(np.dot(a, b))
    s = np.linalg.norm(v)
    if s < 1e-12:
        return np.eye(3) if c > 0 else -np.eye(3)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]) / s
    return np.eye(3) + s * K + (1 - c) * (K @ K)


def main():
    calib = json.loads(CALIB.read_text())
    meta = json.loads(RAW_META.read_text())
    stream = pd.read_csv(OUT / "integrated_stream.csv")
    plog = pd.read_csv(OUT / "unity_person_log.csv").drop_duplicates("frame")
    olog = pd.read_csv(OUT / "unity_object_log.csv").drop_duplicates("frame")
    ocsv = pd.read_csv(OBJECT_CSV)

    P = np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]], float)
    D = np.diag([1.0, -1.0, 1.0])
    T_dc = np.linalg.inv(np.array(calib["T_cam_desk"]))
    R_dc, t_dc = T_dc[:3, :3], T_dc[:3, 3]
    M = P @ R_dc @ D
    cam_pos_u = P @ t_dc
    g = np.array(calib["scene_geometry"]["gravity_up_unity"])
    g /= np.linalg.norm(g)

    # --- 1 anchor math ----------------------------------------------------
    print("--- 1. person-anchor math ---")
    check("M is a proper rotation (orthonormal, det +1)",
          np.abs(M @ M.T - np.eye(3)).max() < 1e-12
          and abs(np.linalg.det(M) - 1) < 1e-12)
    R_u_cam = P @ R_dc @ P
    Rxm90 = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float)
    check("M decomposes as R_unity(camera) * Rx(-90) (receiver composition)",
          np.abs(M - R_u_cam @ Rxm90).max() < 1e-12)
    # Gravity is DEFINED by the plumb wall (ARUCO_MODEL.md §2.1); the depth
    # fit is an independent seed. M must map the person-space seed to the
    # exact same angle from scene gravity that the calibration measured —
    # cross-validating the anchor against two independent gravity sources.
    up_cam = np.array(meta["tabletop"]["up_cam"])
    seed_u = M @ (D @ up_cam)
    ang = float(np.degrees(np.arccos(np.clip(np.dot(seed_u, g), -1, 1))))
    dev = calib["scene_geometry"]["gravity_seed_dev_deg"]
    check("M maps the depth-seed up consistently with the calibration",
          abs(ang - dev) < 1e-6 and ang < 11.0,
          f"{ang:.2f} deg vs calibrated {dev:.2f} deg")

    # --- 2 stream integrity ------------------------------------------------
    print("\n--- 2. stream integrity ---")
    check("899 integrated frames", len(stream) == 899, f"{len(stream)}")
    check("frame numbers strictly increasing",
          bool((np.diff(stream.frame.values) > 0).all()))
    same = (stream.loc[stream.obj_live == 1, ["opx", "opy", "opz"]].values
            == ocsv.loc[ocsv.detected == 1, ["unity_px", "unity_py", "unity_pz"]].values)
    check("live object poses in the stream come verbatim from the filtered CSV",
          bool(same.all()), f"{int(same.all(axis=1).sum())} live frames")
    # The filter stage (aruco/filter_object_track.py) must smooth, not
    # invent: on measured (detected) frames the filtered pose stays within
    # raw PnP jitter of the raw pose.
    oraw = pd.read_csv(OBJECT_RAW_CSV)
    det = oraw.detected.values == 1
    dsm = np.linalg.norm(ocsv.loc[det, ["unity_px", "unity_py", "unity_pz"]].values
                         - oraw.loc[det, ["unity_px", "unity_py", "unity_pz"]].values,
                         axis=1)
    check("object filtering stays within raw jitter on measured frames (< 15 mm)",
          bool((dsm < 0.015).all()),
          f"median {np.median(dsm)*1000:.1f} mm, max {dsm.max()*1000:.1f} mm")

    # --- 3 physical plausibility -------------------------------------------
    print("\n--- 3. physical plausibility ---")
    pel = stream[["pel_x", "pel_y", "pel_z"]].values
    pel_scene = (M @ pel.T).T + cam_pos_u
    drop = calib["scene_geometry"]["origin_above_tabletop_m"]
    h_table = pel_scene @ g + drop          # height above the tabletop plane
    h_floor = h_table + DESK_THICK + LEG_H  # above the (decorative) floor
    print(f"[info] pelvis vs tabletop: {h_table.min():+.3f}..{h_table.max():+.3f} m "
          f"| vs floor: {h_floor.min():+.3f}..{h_floor.max():+.3f} m")
    check("pelvis at desk-working height (within 0.35 m of the tabletop plane)",
          bool((np.abs(h_table) < 0.35).all()))
    check("pelvis well above the floor (> 0.3 m)", bool((h_floor > 0.3).all()))
    obj = stream[["opx", "opy", "opz"]].values
    d = np.linalg.norm(pel_scene - obj, axis=1)
    print(f"[info] pelvis-to-object distance: {d.min():.3f}..{d.max():.3f} m")
    check("person at working distance from the object (0.15..1.5 m)",
          bool(((d > 0.15) & (d < 1.5)).all()))

    # The person works AT the desk facing the sensor across it — the root
    # forward axis (from the streamed Euler) must point at the sensor.
    # This is the check that would have caught the receiver's conjugation
    # bug (rig rendered facing away while the data faced the sensor).
    fwd = np.array([(M @ recompose_zxy(stream.loc[i, ["a0", "a1", "a2"]].values))[:, 2]
                    for i in range(len(stream))])
    to_cam = cam_pos_u[None, :] - pel_scene
    for v in (fwd, to_cam):
        v -= g[None, :] * (v @ g)[:, None]          # horizontal components
    fwd /= np.linalg.norm(fwd, axis=1, keepdims=True)
    to_cam /= np.linalg.norm(to_cam, axis=1, keepdims=True)
    face = np.degrees(np.arccos(np.clip(np.sum(fwd * to_cam, axis=1), -1, 1)))
    check("person faces the sensor across the desk (mean < 20 deg)",
          float(face.mean()) < 20.0,
          f"mean {face.mean():.1f} deg, p95 {np.percentile(face, 95):.1f} deg")

    # Desk far edge (the receiver's data-driven extent: object projection
    # + 5 cm) must stop short of the pelvis — legs are untracked, so a
    # desk slab under the person reads as legs-inside-the-table.
    on_plane = -g * drop

    def projp(q):
        q2 = np.atleast_2d(q)
        return np.squeeze(q2 - np.outer((q2 - on_plane) @ g, g))

    live0 = obj[stream.obj_live.values == 1][0]
    span = (projp(live0) - projp(np.zeros(3))).ravel()
    x_ax = span / np.linalg.norm(span)
    far_edge = projp(live0).ravel() + x_ax * 0.05
    clear = (projp(pel_scene) - far_edge) @ x_ax
    check("pelvis clears the desk's far edge (no legs inside the table)",
          bool((clear > -0.02).all()),
          f"min clearance {clear.min()*100:+.1f} cm")

    # --- 4 Unity person application ----------------------------------------
    print("\n--- 4. Unity person application (hip == anchor * pelvis) ---")
    # Reconstruct the receiver's world transform from first principles:
    # gravity alignment G, then the floor-drop translation computed off the
    # first streamed object position (BuildDeferredScene).
    G = from_to_rotation(g, np.array([0.0, 1.0, 0.0]))
    on_plane = -g * drop
    proj = lambda q: q - g * float(np.dot(q - on_plane, g))
    obj0 = stream[["opx", "opy", "opz"]].values[0]
    center = (proj(np.zeros(3)) + proj(obj0)) / 2.0
    floor_pt = center - g * (DESK_THICK + LEG_H)
    world_pos = np.array([0.0, -(G @ floor_pt)[1], 0.0])

    m = plog.merge(stream, on="frame", suffixes=("", "_s"))
    dpel = np.abs(m[["pel_x", "pel_y", "pel_z"]].values
                  - m[["pel_x_s", "pel_y_s", "pel_z_s"]].values).max()
    check("received pelvis matches sent pelvis (float32)",
          dpel < 1e-5, f"max {dpel:.2e} m over {len(m)} frames")
    expect = (G @ (M @ m[["pel_x_s", "pel_y_s", "pel_z_s"]].values.T
                   + cam_pos_u[:, None])).T + world_pos
    dhip = np.abs(m[["hip_x", "hip_y", "hip_z"]].values - expect).max()
    check("hip bone lands on the mapped pelvis point (float32 + FK)",
          dhip < 1e-3, f"max {dhip*1000:.4f} mm over {len(m)} frames")
    cov = len(plog) / 899.0
    check("Unity applied >95% of the 899 frames", cov > 0.95,
          f"{len(plog)}/899 ({cov*100:.1f}%)")

    # --- 5 Unity object log -------------------------------------------------
    print("\n--- 5. Unity object application ---")
    mo = olog.merge(ocsv[ocsv.detected == 1], on="frame")
    dp = np.abs(mo[["px", "py", "pz"]].values
                - mo[["unity_px", "unity_py", "unity_pz"]].values).max()
    de = np.abs(mo[["ex", "ey", "ez"]].values
                - mo[["unity_ex", "unity_ey", "unity_ez"]].values).max()
    check("object poses applied exactly (float32)",
          dp < 1e-5 and de < 1e-3, f"pos {dp*1000:.4f} mm, euler {de:.2e} deg")

    # --- 6 carried-object consistency: object trajectory vs wrists -------
    # The object only moves because a hand moves it, so whenever the object
    # is in motion its trajectory must shadow a wrist's: nearby (within
    # grasp) and moving the same way. This ties Pipeline B's object track
    # to Pipeline A's wrist track — two different sensors/algorithms with
    # no shared code — through the calibrated anchor.
    print("\n--- 6. carried object: trajectory follows the wrists ---")
    lm = pd.read_csv(LANDMARKS_CSV).set_index("frame")
    lm = lm.reindex(stream.frame.values)
    wrists = {}
    for side in ("left", "right"):
        w_cam = lm[[f"{side}_wrist_x", f"{side}_wrist_y", f"{side}_wrist_z"]].values
        wrists[side] = (M @ (w_cam * np.array([1.0, -1.0, 1.0])).T).T + cam_pos_u
    live = stream["obj_live"].values == 1

    K = 7  # displacement window, ~0.23 s at 30 fps
    disp = np.linalg.norm(obj[K:] - obj[:-K], axis=1)
    moving = np.zeros(len(obj), dtype=bool)
    moving[K // 2:K // 2 + len(disp)] = disp > 0.03
    moving &= live
    travel = float(np.sum(np.linalg.norm(np.diff(obj[live], axis=0), axis=1)))
    print(f"[info] object total travel {travel:.2f} m, "
          f"{int(moving.sum())}/{len(obj)} frames in motion")
    check("object actually moves in this recording (travel > 1 m)",
          travel > 1.0, f"{travel:.2f} m")

    dists = np.stack([np.linalg.norm(obj - wrists[s], axis=1)
                      for s in ("left", "right")])          # (2, n), NaN when blocked
    with np.errstate(invalid="ignore"):
        dnear = np.nanmin(dists, axis=0)
    ok_frames = moving & np.isfinite(dnear)
    med = float(np.median(dnear[ok_frames]))
    p95 = float(np.percentile(dnear[ok_frames], 95))
    check("moving object stays within grasp of a wrist (median < 0.30 m)",
          med < 0.30, f"median {med*100:.1f} cm, p95 {p95*100:.1f} cm "
          f"over {int(ok_frames.sum())} moving frames")

    # Velocity agreement with the NEARER wrist over the same window,
    # pooled per-axis Pearson correlation + mean cosine similarity.
    v_obj = obj[K:] - obj[:-K]
    v_wr = np.stack([wrists[s][K:] - wrists[s][:-K] for s in ("left", "right")])
    nearer = np.nanargmin(np.where(np.isfinite(dists), dists, np.inf), axis=0)
    v_near = v_wr[nearer[K // 2:K // 2 + len(v_obj)], np.arange(len(v_obj))]
    m_win = moving[K // 2:K // 2 + len(v_obj)] & np.isfinite(v_near).all(axis=1)
    a, b = v_obj[m_win], v_near[m_win]
    r = float(np.corrcoef(a.ravel(), b.ravel())[0, 1])
    cos = float(np.mean(np.sum(a * b, axis=1)
                        / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1) + 1e-12)))
    check("object velocity correlates with the nearer wrist's (r > 0.8)",
          r > 0.8, f"pooled Pearson r {r:.3f} over {int(m_win.sum())} frames")
    check("object and wrist move in the same direction (mean cos > 0.7)",
          cos > 0.7, f"mean cosine {cos:.3f}")

    print(f"\n=== {npass} passed, {nfail} failed ===")
    sys.exit(nfail)


if __name__ == "__main__":
    main()

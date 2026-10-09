#!/usr/bin/env python3
"""Numeric backstop for the R5 Unity pose check (eval/unity_check/).

The side-by-side video answers "does it look right"; this answers "is the
thing on screen the frame it claims to be, and where does the rendered
person sit against the measurement" in numbers:

  1. Exactness of application. The receivers log every applied frame
     (v1/integration/output/unity_{person,object}_log.csv). Those rows must
     equal, to float32, the rows the sender streamed for the same frame
     number -- if they do, "PNG named f" really is "frame f's data".
  2. Anchor reconstruction. The logged hip world position must reproduce
     anchor.TransformPoint(pelvis) recomputed here from the calibration
     alone (gravity alignment, floor drop, camera pose), as in
     v1/integration/validate_integration.py check 4 but for the R5 stem
     and the marker-size-corrected calibration.
  3. Rendered pose vs measurement, in the recorded image. The logged hand
     positions are mapped back out of Unity's world into the sensor frame
     and projected with the recording's own color intrinsics, then compared
     against the MediaPipe wrists for the same frame. Split by the E-014
     failure mask, this separates "Unity draws the solve faithfully" from
     "the solve was right".

Usage:
  python eval/unity_check/check_unity_log.py
  python eval/unity_check/check_unity_log.py --person-log <csv> \
      --object-log <csv> --frames-dir <dir>   # archived runtime logs (E-036)
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "eval"))
from common import paths as P  # noqa: E402

# ArucoSceneReceiver constants (read-only source of truth)
DESK_THICK, LEG_H = 0.03, 0.69
SENSOR_FLIP = np.array([1.0, -1.0, 1.0])   # person space <-> sensor frame
UNITY_LOGS = REPO / "v1" / "integration" / "output"

npass = nfail = 0
lines = []


def check(name, ok, detail=""):
    global npass, nfail
    npass += bool(ok)
    nfail += not ok
    s = f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail else "")
    print(s)
    lines.append(s)


def info(s):
    print(s)
    lines.append(s)


def from_to_rotation(a, b):
    """Unity Quaternion.FromToRotation(a, b) as a matrix."""
    v = np.cross(a, b)
    c = float(np.dot(a, b))
    s = np.linalg.norm(v)
    if s < 1e-12:
        return np.eye(3) if c > 0 else -np.eye(3)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]) / s
    return np.eye(3) + s * K + (1 - c) * (K @ K)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stem", default=P.R5_STEM)
    ap.add_argument("--out", default=str(P.EVAL_OUT / "unity_check_r5"))
    # Overrides for a capture whose runtime logs were archived elsewhere
    # (the presentation captures move them next to the stills, E-036);
    # the defaults are the live locations the receivers write to.
    ap.add_argument("--person-log",
                    default=str(UNITY_LOGS / "unity_person_log.csv"),
                    help="receiver person log to check")
    ap.add_argument("--object-log",
                    default=str(UNITY_LOGS / "unity_object_log.csv"),
                    help="receiver object log to check")
    ap.add_argument("--frames-dir", default="/tmp/r5_frames",
                    help="directory of the f*.png frame dumps")
    args = ap.parse_args()
    out_dir = Path(args.out)

    calib = json.loads(P.calib_for(args.stem).read_text())
    K = json.loads(P.lm_meta(args.stem).read_text())["color_intrinsics"]
    stream = pd.read_csv(out_dir / "integrated_stream.csv")
    plog = pd.read_csv(args.person_log).drop_duplicates("frame")
    olog = pd.read_csv(args.object_log).drop_duplicates("frame")
    lm = pd.read_csv(P.lm_filtered(args.stem)).set_index("frame")
    unity_png = sorted(Path(args.frames_dir).glob("f*.png"))

    Pm = np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]], float)
    D = np.diag([1.0, -1.0, 1.0])
    T_dc = np.linalg.inv(np.array(calib["T_cam_desk"], float))
    R_dc, t_dc = T_dc[:3, :3], T_dc[:3, 3]
    M = Pm @ R_dc @ D
    cam_pos_u = Pm @ t_dc
    g = np.array(calib["scene_geometry"]["gravity_up_unity"], float)
    g /= np.linalg.norm(g)
    drop = calib["scene_geometry"]["origin_above_tabletop_m"]
    G = from_to_rotation(g, np.array([0.0, 1.0, 0.0]))
    on_plane = -g * drop

    def proj_plane(q):
        return q - g * float(np.dot(q - on_plane, g))

    obj0 = stream[["opx", "opy", "opz"]].to_numpy()[0]
    center = (proj_plane(np.zeros(3)) + proj_plane(obj0)) / 2.0
    floor_pt = center - g * (DESK_THICK + LEG_H)
    world_pos = np.array([0.0, -(G @ floor_pt)[1], 0.0])

    info(f"stem {args.stem}")
    info(f"streamed {len(stream)} frames | Unity applied {len(plog)} distinct "
         f"person frames, {len(olog)} object frames | {len(unity_png)} PNGs")

    # --- 1 exactness of application ---------------------------------------
    info("\n--- 1. the receiver applied the frame it reported ---")
    m = plog.merge(stream, on="frame", suffixes=("", "_s"))
    dpel = np.abs(m[["pel_x", "pel_y", "pel_z"]].to_numpy()
                  - m[["pel_x_s", "pel_y_s", "pel_z_s"]].to_numpy()).max()
    check("logged pelvis == streamed pelvis for the same frame (float32)",
          dpel < 1e-5, f"max {dpel:.2e} m over {len(m)} frames")
    mo = olog.merge(stream, on="frame")
    dp = np.abs(mo[["px", "py", "pz"]].to_numpy()
                - mo[["opx", "opy", "opz"]].to_numpy()).max()
    de = np.abs(mo[["ex", "ey", "ez"]].to_numpy()
                - mo[["oex", "oey", "oez"]].to_numpy()).max()
    check("logged object pose == streamed object pose (float32)",
          dp < 1e-5 and de < 1e-3,
          f"pos {dp*1000:.5f} mm, euler {de:.2e} deg over {len(mo)} frames")
    cov = len(plog) / len(stream)
    check("Unity applied > 99% of the streamed frames", cov > 0.99,
          f"{len(plog)}/{len(stream)} ({cov*100:.1f}%)")
    png_frames = {int(p.stem[1:]) for p in unity_png}
    check("every PNG frame number is a frame Unity actually applied",
          png_frames <= set(plog.frame.astype(int)),
          f"{len(png_frames)} PNGs, "
          f"{len(png_frames - set(plog.frame.astype(int)))} orphans")

    # --- 2 anchor reconstruction ------------------------------------------
    info("\n--- 2. rig placement reproduces the calibrated anchor ---")
    expect = (G @ (M @ m[["pel_x_s", "pel_y_s", "pel_z_s"]].to_numpy().T
                   + cam_pos_u[:, None])).T + world_pos
    dhip = np.abs(m[["hip_x", "hip_y", "hip_z"]].to_numpy() - expect).max()
    check("hip bone lands on the mapped pelvis point",
          dhip < 1e-3, f"max {dhip*1000:.4f} mm over {len(m)} frames")

    # --- 3 rendered hands vs measured wrists, in the recorded image -------
    info("\n--- 3. rendered pose vs measurement, reprojected into the video ---")

    def to_pixels(p_unity):
        """Unity scene world -> person space -> sensor frame -> pixels."""
        p_person = (M.T @ (G.T @ (p_unity - world_pos).T - cam_pos_u[:, None]))
        p_cam = (p_person.T * SENSOR_FLIP)
        u = K["fx"] * p_cam[:, 0] / p_cam[:, 2] + K["ppx"]
        v = K["fy"] * p_cam[:, 1] / p_cam[:, 2] + K["ppy"]
        return u, v, p_cam[:, 2]

    frames = m["frame"].to_numpy(int)
    res = {}
    duv = {}
    for side, cols in (("right", ("rh_x", "rh_y", "rh_z")),
                       ("left", ("lh_x", "lh_y", "lh_z"))):
        u, v, z = to_pixels(m[list(cols)].to_numpy())
        w = lm.reindex(frames)[[f"{side}_wrist_x", f"{side}_wrist_y",
                                f"{side}_wrist_z"]].to_numpy()
        uw = K["fx"] * w[:, 0] / w[:, 2] + K["ppx"]
        vw = K["fy"] * w[:, 1] / w[:, 2] + K["ppy"]
        bad = (z <= 0.05) | ~np.isfinite(w).all(axis=1)
        du, dv = u - uw, v - vw
        du[bad] = dv[bad] = np.nan
        duv[side] = (du, dv)
        res[side] = np.hypot(du, dv)

    fm = pd.read_csv(P.EVAL_OUT / f"recovery_{P.ALIAS[args.stem]}"
                     / "failure_mask.csv").set_index("frame").reindex(frames)
    fail = {"right": fm["fail_arm_R"].to_numpy(bool),
            "left": fm["fail_arm_L"].to_numpy(bool)}
    torso_fail = fm["fail_torso"].to_numpy(bool)
    info(f"E-014 failure mask over these frames: arm_R "
         f"{int(fail['right'].sum())}, arm_L {int(fail['left'].sum())}, "
         f"torso {int(torso_fail.sum())} of {len(frames)}")

    # Arm failures and torso failures are different defects and overlap, so
    # they get their own buckets instead of one merged "failure" number.
    summary = {}
    for side in ("right", "left"):
        r = res[side]
        ok = np.isfinite(r)
        buckets = {
            "clean": ok & ~fail[side] & ~torso_fail,
            "arm_only": ok & fail[side] & ~torso_fail,
            "torso_only": ok & ~fail[side] & torso_fail,
            "arm_and_torso": ok & fail[side] & torso_fail,
        }
        summary[side] = {}
        for name, sel in buckets.items():
            if not sel.any():
                summary[side][name] = {"n": 0}
                continue
            summary[side][name] = {
                "n": int(sel.sum()),
                "median_px": float(np.median(r[sel])),
                "p95_px": float(np.percentile(r[sel], 95)),
            }
            b = summary[side][name]
            info(f"  {side:5s} hand / {name:13s} median {b['median_px']:6.1f} px, "
                 f"p95 {b['p95_px']:6.1f} px  (n={b['n']})")

    # The rig is a fixed-proportion avatar scaled to 1.70 m and its hand bone
    # is not MediaPipe's wrist point, so a standing pixel offset between the
    # two is expected and says nothing about whether the rendered pose
    # FOLLOWS the video. Removing each hand's own median offset separates the
    # two: what is left is the frame-to-frame disagreement.
    info("")
    for side in ("right", "left"):
        du, dv = duv[side]
        clean = np.isfinite(du) & ~fail[side] & ~torso_fail
        bu, bv = np.median(du[clean]), np.median(dv[clean])
        spread = np.hypot(du - bu, dv - bv)
        s = summary[side]
        s["clean_bias_px"] = [float(bu), float(bv)]
        s["clean_debiased_median_px"] = float(np.median(spread[clean]))
        s["clean_debiased_p95_px"] = float(np.percentile(spread[clean], 95))
        info(f"  {side:5s} hand: standing offset ({bu:+.1f}, {bv:+.1f}) px; "
             f"after removing it, clean-frame disagreement median "
             f"{s['clean_debiased_median_px']:.1f} px, "
             f"p95 {s['clean_debiased_p95_px']:.1f} px")

    for side in ("right", "left"):
        s = summary[side]
        check(f"{side} hand follows the measured wrist on clean frames "
              "(de-biased median < 40 px in a 640x480 image)",
              s["clean_debiased_median_px"] < 40.0,
              f"median {s['clean_debiased_median_px']:.1f} px")
    # The one bucket where the rendered arm visibly leaves the video.
    check("left hand disagreement is concentrated on torso-failure frames",
          summary["left"]["torso_only"]["median_px"]
          > 3 * summary["left"]["clean"]["median_px"],
          f"{summary['left']['torso_only']['median_px']:.1f} px vs "
          f"{summary['left']['clean']['median_px']:.1f} px clean")

    info(f"\n=== {npass} passed, {nfail} failed ===")
    (out_dir / "check_unity_log.txt").write_text("\n".join(lines) + "\n")
    (out_dir / "check_unity_log.json").write_text(json.dumps(
        {"stem": args.stem, "streamed": len(stream),
         "applied_person_frames": int(len(plog)),
         "pngs": len(unity_png), "max_pelvis_diff_m": float(dpel),
         "max_object_pos_diff_m": float(dp), "max_hip_diff_m": float(dhip),
         "hand_reprojection": summary,
         "passed": npass, "failed": nfail}, indent=1))
    sys.exit(nfail)


if __name__ == "__main__":
    main()

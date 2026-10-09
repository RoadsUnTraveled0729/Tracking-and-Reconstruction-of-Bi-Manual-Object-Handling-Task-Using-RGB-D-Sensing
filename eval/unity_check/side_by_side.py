#!/usr/bin/env python3
"""Pair the Unity sensor-POV render with the recorded color video (R5).

Left panel  : Unity's SensorPOVCamera render, i.e. a virtual camera sitting
              at the calibrated sensor pose with the calibrated vertical FOV
              -- a replica of the RealSense that made the recording.
Right panel : the same frame's color image straight out of the .bag.

The pairing is an EXACT join on the stream frame number, with no timing
assumption anywhere:
  * Unity's EvalFrameDump names every PNG after ArucoSceneReceiver.lastFrame
    (the frame the receivers applied that Update), written from LateUpdate,
    so f01234.png shows exactly what frame 1234 carried;
  * the bag's i-th color frame is row i of the landmark CSV, whose `frame`
    column is that same number (the extractors walk the bag once, in order).

--lag-scan cross-checks that join without trusting either statement: it
compares the orange object cube's centroid in the Unity render against the
object marker's measured pixel centre (m1_u/m1_v in the scaled ArUco CSV)
over a range of artificial frame offsets. A true pairing puts the minimum
at offset 0; an off-by-N shows up as a shifted minimum.

Outputs (default eval/output/unity_check_r5/):
  side_by_side.mp4              full replay, HUD-stamped on both halves
  still_f<frame>.png            paired stills
  pairing_lag_scan.json/.txt    the off-by-N evidence
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "eval"))
from common import paths as P  # noqa: E402

BAND = 26          # HUD band height, px
FONT = cv2.FONT_HERSHEY_SIMPLEX


def unity_cube_centroid(img):
    """Centroid of the orange object cube in a Unity render, or None.

    The cube is the only strongly orange thing in the scene (desk brown is
    far darker, the rig is grey/white), so a hue window plus a saturation
    and value floor isolates it.
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    m = cv2.inRange(hsv, np.array([5, 140, 90]), np.array([25, 255, 255]))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    if int(m.sum()) < 255 * 25:          # fewer than ~25 px: not visible
        return None
    ys, xs = np.nonzero(m)
    return float(xs.mean()), float(ys.mean())


def load_unity_frames(unity_dir):
    out = {}
    for p in sorted(Path(unity_dir).glob("f*.png")):
        try:
            out[int(p.stem[1:])] = p
        except ValueError:
            continue
    return out


def recompose_zxy(deg):
    """Unity ZXY-applied Euler degrees -> R = Ry.Rx.Rz (KINEMATIC_MODEL.md 4)."""
    x, y, z = np.radians(np.asarray(deg, float))
    cx, sx, cy, sy, cz, sz = (np.cos(x), np.sin(x), np.cos(y),
                              np.sin(y), np.cos(z), np.sin(z))
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Ry @ Rx @ Rz


def project_cube_centre(stem):
    """Pixel track of the object cube's centre, straight from the streamed
    pose -- the exact thing Unity renders.

    ArucoSceneReceiver puts the cube half an edge along the node's local
    -up from the marker (the marker is centred on the cube's front face),
    so the centre in mapped-Unity coordinates is p - (size/2)*R*(0,1,0).
    Mapping back through P (the y/z swap) gives desk-world, T_cam_desk gives
    the camera frame, and the recorded color intrinsics give the pixel.
    Sanity: doing this for the MARKER centre instead reproduces the ArUco
    detector's own m1_u/m1_v to a median 0.15 px, so the projection chain
    itself is not in question.
    """
    calib = json.loads(P.calib_for(stem).read_text())
    K = json.loads(P.lm_meta(stem).read_text())["color_intrinsics"]
    T = np.array(calib["T_cam_desk"], float)
    R, t = T[:3, :3], T[:3, 3]
    size = calib["scene_geometry"]["object_cube_size_m"]
    ob = pd.read_csv(P.object_world_filtered(stem))
    pu = ob[["unity_px", "unity_py", "unity_pz"]].to_numpy(float)
    eu = ob[["unity_ex", "unity_ey", "unity_ez"]].to_numpy(float)
    up = np.array([recompose_zxy(e) @ np.array([0.0, 1.0, 0.0]) for e in eu])
    centre_u = pu - up * (size / 2.0)
    swap = np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]], float)   # Unity <-> world
    pc = (R @ (swap @ centre_u.T)).T + t
    u = K["fx"] * pc[:, 0] / pc[:, 2] + K["ppx"]
    v = K["fy"] * pc[:, 1] / pc[:, 2] + K["ppy"]
    return ob["frame"].to_numpy(int), u, v, ob["detected"].to_numpy(int) == 1


def lag_scan(unity_png, stem, span=6):
    """Off-by-N test in image space.

    For every Unity render, the centroid of the orange cube; for every
    frame, the projected cube centre from the pose that frame streamed.
    The two differ by a bias (only the cube's camera-facing faces are
    orange, and the white marker plate covers the middle of the front
    face), so the comparison is made on FRAME-TO-FRAME DISPLACEMENTS,
    which cancel any bias that is steady over a frame and leave a metric
    that is sharp in the lag: if PNG f actually showed frame f+k, the
    minimum sits at k.
    """
    frames, pu, pv, det = project_cube_centre(stem)
    n = len(frames)
    idx = {int(f): i for i, f in enumerate(frames)}
    cu = np.full(n, np.nan)
    cv_ = np.full(n, np.nan)
    cen = {}
    for f, p in unity_png.items():
        i = idx.get(f)
        if i is None:
            continue
        img = cv2.imread(str(p))
        if img is None:
            continue
        c = unity_cube_centroid(img)
        if c is None:
            continue
        cen[f] = c
        cu[i], cv_[i] = c

    def d(a):
        out = np.full_like(a, np.nan)
        out[1:] = np.diff(a)
        return out

    dcu, dcv, dpu, dpv = d(cu), d(cv_), d(pu), d(pv)
    moving = det & np.isfinite(dpu) & (np.hypot(dpu, dpv) > 1.0)
    rows = []
    for lag in range(-span, span + 1):
        su = np.roll(dcu, -lag)          # the Unity render lag frames later
        sv = np.roll(dcv, -lag)
        ok = moving & np.isfinite(su) & np.isfinite(sv)
        if ok.sum() < 30:
            rows.append({"lag": lag, "n": int(ok.sum()), "median_px": None})
            continue
        r = np.median(np.hypot(su[ok] - dpu[ok], sv[ok] - dpv[ok]))
        rows.append({"lag": lag, "n": int(ok.sum()), "median_px": float(r)})
    return rows, cen, int(moving.sum())


def stamp(img, text, colour=(255, 255, 255)):
    """Add a HUD band with the frame label above the image."""
    h, w = img.shape[:2]
    out = np.zeros((h + BAND, w, 3), np.uint8)
    out[BAND:] = img
    cv2.putText(out, text, (8, BAND - 8), FONT, 0.55, colour, 1, cv2.LINE_AA)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stem", default=P.R5_STEM)
    ap.add_argument("--unity-dir", default="/tmp/r5_frames")
    ap.add_argument("--out", default=str(P.EVAL_OUT / "unity_check_r5"))
    ap.add_argument("--stills",
                    default="300,700,900,1150,1200,1450,1600,1740,1830,2020",
                    help="fixed still frames; the fastest object-motion "
                         "frame is added automatically")
    ap.add_argument("--no-video", action="store_true")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    unity_png = load_unity_frames(args.unity_dir)
    if not unity_png:
        sys.exit(f"FAIL: no Unity PNGs under {args.unity_dir}")

    lm = pd.read_csv(P.lm_filtered(args.stem))
    stream = out_dir / "integrated_stream.csv"
    st = pd.read_csv(stream).set_index("frame") if stream.exists() else None
    aruco_csv = P.EVAL_OUT / f"{args.stem}_aruco_raw_scaled.csv"
    print(f"[info] {len(unity_png)} Unity PNGs, {len(lm)} recorded frames")

    # ---- off-by-N evidence -------------------------------------------------
    rows, cen, n_moving = lag_scan(unity_png, args.stem)
    best = min((r for r in rows if r["median_px"] is not None),
               key=lambda r: r["median_px"])
    txt = [f"object-cube image displacement, Unity render vs streamed pose, "
           f"per frame offset",
           f"({len(cen)} Unity frames with a visible cube, "
           f"{int(n_moving)} frames with the object moving > 1 px/frame)",
           "offset  n     median |dUnity - dStreamed| (px)"]
    for r in rows:
        m = "n/a" if r["median_px"] is None else f"{r['median_px']:8.2f}"
        txt.append(f"{r['lag']:+4d}  {r['n']:5d}  {m}"
                   + ("   <-- minimum" if r is best else ""))
    txt.append(f"minimum at offset {best['lag']:+d} "
               f"({best['median_px']:.2f} px)")
    (out_dir / "pairing_lag_scan.txt").write_text("\n".join(txt) + "\n")
    (out_dir / "pairing_lag_scan.json").write_text(
        json.dumps({"rows": rows, "best_lag": best["lag"],
                    "best_median_px": best["median_px"]}, indent=1))
    print("\n".join(txt))

    # fastest object motion among frames we actually have a render for
    ar = pd.read_csv(aruco_csv)
    sp = np.full(len(ar), 0.0)
    sp[1:] = np.hypot(np.diff(ar["m1_u"].to_numpy(float)),
                      np.diff(ar["m1_v"].to_numpy(float)))
    sp[ar["m1_detected"].to_numpy() != 1] = 0.0
    order = np.argsort(-sp)
    fast = next((int(ar["frame"].iloc[i]) for i in order
                 if int(ar["frame"].iloc[i]) in unity_png), None)
    stills = [int(s) for s in args.stills.split(",") if s.strip()]
    if fast is not None:
        stills = [fast] + stills
    print(f"[info] stills {stills} (fastest object motion: frame {fast}, "
          f"{sp[order[0]]:.1f} px/frame)")

    # ---- bag walk ----------------------------------------------------------
    # Bag reader copied from eval/inspect/check_v1_overlay.py (lines 199-227,
    # 2026-08-26): enable_device_from_file + non-real-time playback walks the
    # color stream once, in recording order, so the i-th color frame is row i.
    import pyrealsense2 as rs
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(str(P.bag(args.stem)), repeat_playback=False)
    profile = pipeline.start(config)
    profile.get_device().as_playback().set_real_time(False)
    color_format = profile.get_stream(rs.stream.color).format()

    tmp = out_dir / "side_by_side_tmp.mp4"
    vw = None
    n_pairs = n_missing = 0
    i = 0
    while i < len(lm):
        try:
            frames = pipeline.wait_for_frames(2000)
        except RuntimeError:
            break
        cf = frames.get_color_frame()
        if not cf:
            continue
        img = np.asanyarray(cf.get_data())
        if color_format == rs.format.rgb8:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        img = np.ascontiguousarray(img)
        row = lm.iloc[i]
        f = int(row["frame"])
        i += 1

        png = unity_png.get(f)
        if png is None:
            n_missing += 1
            continue
        uimg = cv2.imread(str(png))
        if uimg is None:
            n_missing += 1
            continue
        if uimg.shape[:2] != img.shape[:2]:
            uimg = cv2.resize(uimg, (img.shape[1], img.shape[0]))

        extra = ""
        if st is not None and f in st.index:
            extra = (f" mask={int(st.loc[f, 'mask']):03d}"
                     f" obj_live={int(st.loc[f, 'obj_live'])}")
        left = stamp(uimg, f"UNITY  f{f:05d}  t={row['time_s']:.2f}s{extra}",
                     (120, 220, 255))
        right = stamp(img, f"VIDEO  f{f:05d}  t={row['time_s']:.2f}s",
                      (255, 255, 255))
        pair = np.hstack([left, right])
        cv2.line(pair, (left.shape[1], 0), (left.shape[1], pair.shape[0]),
                 (60, 60, 60), 1)

        if f in stills:
            p = out_dir / f"still_f{f:05d}.png"
            cv2.imwrite(str(p), pair)
            print(f"[still] {p}")
        if not args.no_video:
            if vw is None:
                vw = cv2.VideoWriter(str(tmp), cv2.VideoWriter_fourcc(*"mp4v"),
                                     30, (pair.shape[1], pair.shape[0]))
            vw.write(pair)
        n_pairs += 1
    if vw is not None:
        vw.release()
    pipeline.stop()

    print(f"[info] {n_pairs} paired frames, {n_missing} recorded frames with "
          f"no Unity render")
    if vw is not None:
        final = out_dir / "side_by_side.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp),
                        "-c:v", "libx264", "-crf", "22", "-pix_fmt", "yuv420p",
                        str(final)], check=True)
        tmp.unlink()
        print(f"[video] {final} ({n_pairs} frames)")

    (out_dir / "pairing_summary.json").write_text(json.dumps(
        {"stem": args.stem, "unity_pngs": len(unity_png),
         "recorded_frames": len(lm), "paired": n_pairs,
         "unpaired": n_missing, "best_lag": best["lag"],
         "best_median_px": best["median_px"],
         "stills": sorted(set(stills))}, indent=1))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""v1 correctness check: reproject the v1 reconstruction onto the color video.

Chain verified here, camera frame only, NO calibration, NO Unity:
  filtered landmarks (sensor frame) -> unity_from_sensor flip
  -> ChainFallbackSolver / RobustChainSolver -> 13 angles
  -> forward kinematics (KINEMATIC_MODEL conventions, fixed segment
     lengths = median of clean frames) -> joint positions
  -> flip back to sensor frame -> pinhole projection -> overlay.

If the drawn skeleton sits on the real person, the v1 measurement +
solve + model are correct; any Unity mismatch is then downstream
(merger / receiver frame composition).

Outputs:
  <out>/v1_overlay_<solver>.mp4   overlay video (green = measured
                                  landmarks, red = FK right arm,
                                  blue = FK left arm, magenta = root
                                  forward arrow)
  <out>/v1_check_plots.png        root yaw baseline-vs-robust, pelvis
                                  top-down track, FK wrist residuals

Usage:
  python eval/inspect/check_v1_overlay.py \
      --stem recording_20260825_070152 --solver both
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import cv2
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "v1/kinematics"))
sys.path.insert(0, str(ROOT / "v1/mediapipe"))

from occlusion import ChainFallbackSolver, LANDMARKS, points_from_row  # noqa: E402
from occlusion_ext import RobustChainSolver                            # noqa: E402
from root_frame import unity_from_sensor, recompose_zxy                # noqa: E402
from shoulder import _rx, _ry, _rz                                     # noqa: E402

SENSOR_FLIP = np.array([1.0, -1.0, 1.0])   # inverse of unity_from_sensor


def fk_arm_dirs(sh_deg, elb_deg, side):
    """Model-space (root basis) unit directions of upper arm and forearm.

    Right (shoulder.py docstrings): upper = Ry(ty)Rz(tz) x, forearm =
    Ry(ty)Rz(tz)Rx(tau) Ry(ey)Rz(ez) x.  Left mirrors: chain_L =
    Ry(-ty)Rz(-tz)Rx(tau)Ry(-ey)Rz(-ez), rest arm -x (shoulder.py:144).
    """
    ty, tz, tau = np.radians(sh_deg)
    ey, ez = np.radians(elb_deg)
    if side == "right":
        Rsw = _ry(ty) @ _rz(tz)
        Rarm = Rsw @ _rx(tau)
        upper = Rsw @ np.array([1.0, 0, 0])
        fore = Rarm @ (_ry(ey) @ _rz(ez) @ np.array([1.0, 0, 0]))
    else:
        Rsw = _ry(-ty) @ _rz(-tz)
        Rarm = Rsw @ _rx(tau)
        upper = Rsw @ np.array([-1.0, 0, 0])
        fore = Rarm @ (_ry(-ey) @ _rz(-ez) @ np.array([-1.0, 0, 0]))
    return upper, fore


def project(p_cam, K):
    """Sensor-frame xyz -> pixel (u, v); None behind the camera."""
    if p_cam is None or not np.all(np.isfinite(p_cam)) or p_cam[2] <= 0.05:
        return None
    u = K["fx"] * p_cam[0] / p_cam[2] + K["ppx"]
    v = K["fy"] * p_cam[1] / p_cam[2] + K["ppy"]
    return int(round(u)), int(round(v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default="recording_20260825_070152")
    ap.add_argument("--bag", default=None)
    ap.add_argument("--solver", default="both",
                    choices=["baseline", "robust", "both"])
    ap.add_argument("--out", default=str(ROOT / "eval/output/v1_check"))
    ap.add_argument("--video-solver", default="baseline",
                    help="which solver's FK goes into the overlay video")
    ap.add_argument("--recovery", action="store_true",
                    help="render the object-conditioned recovery solve "
                         "(E-014): failure-masked landmarks removed, "
                         "object-derived wrist input, red failure "
                         "banner, yellow object-wrist marker")
    args = ap.parse_args()

    bag = Path(args.bag) if args.bag else ROOT / f"Video/{args.stem}.bag"
    csv = ROOT / f"v1/mediapipe/output/{args.stem}_landmarks_filtered.csv"
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    import json
    meta = json.loads((ROOT / f"v1/mediapipe/output/"
                       f"{args.stem}_landmarks_raw.meta.json").read_text())
    K = meta["color_intrinsics"]

    df = pd.read_csv(csv)
    n = len(df)
    print(f"[info] {n} frames from {csv.name}")

    # ---- offline solve, both solvers, identical input path to v2_person ----
    runs = {}
    fail = w_hat = None
    if args.recovery:
        sys.path.insert(0, str(ROOT / "eval/failure"))
        import recovery_core as rc
        inputs = rc.build_inputs(args.stem)
        res = rc.run_variant(inputs, "recovery")
        runs["recovery"] = (res["angles"], res["mask"])
        which = ["recovery"]
        fail = inputs["fail"]
        w_hat = inputs["w_hat_solver"]
        print("[solve] recovery done "
              f"(obj_recovered {res['solver'].obj_recovered})")
    else:
        which = (["baseline", "robust"] if args.solver == "both"
                 else [args.solver])
    for name in [] if args.recovery else which:
        solver = (RobustChainSolver() if name == "robust"
                  else ChainFallbackSolver())
        A = np.zeros((n, 13))
        M = np.zeros(n, dtype=int)
        pts_flip = []
        for i, (_, row) in enumerate(df.iterrows()):
            pts = {k: unity_from_sensor(v)
                   for k, v in points_from_row(row).items()
                   if np.all(np.isfinite(v))}
            out = solver.solve(pts)
            A[i], M[i] = out[0], out[1]
            pts_flip.append(pts)
        runs[name] = (A, M)
        print(f"[solve] {name} done")

    A, M = runs[args.video_solver if args.video_solver in runs else which[0]]

    # ---- fixed segment lengths: median over frames with both ends measured ----
    def seg_len(a, b):
        d = df[[f"{a}_x", f"{a}_y", f"{a}_z"]].to_numpy() - \
            df[[f"{b}_x", f"{b}_y", f"{b}_z"]].to_numpy()
        L = np.linalg.norm(d, axis=1)
        ok = (df[f"{a}_src"] == 0) & (df[f"{b}_src"] == 0) & np.isfinite(L)
        return float(np.median(L[ok]))

    L_up_r = seg_len("right_shoulder", "right_elbow")
    L_fo_r = seg_len("right_elbow", "right_wrist")
    L_up_l = seg_len("left_shoulder", "left_elbow")
    L_fo_l = seg_len("left_elbow", "left_wrist")
    print(f"[len] upper R {L_up_r:.3f} L {L_up_l:.3f}  "
          f"fore R {L_fo_r:.3f} L {L_fo_l:.3f} m")

    # ---- FK joints per frame (flipped frame), residuals ----
    def get(row, k):
        p = np.array([row[f"{k}_x"], row[f"{k}_y"], row[f"{k}_z"]])
        return unity_from_sensor(p) if np.all(np.isfinite(p)) else None

    fk = {"right": np.full((n, 2, 3), np.nan),   # [elbow, wrist]
          "left": np.full((n, 2, 3), np.nan)}
    res_wrist = {"right": np.full(n, np.nan), "left": np.full(n, np.nan)}
    for i, (_, row) in enumerate(df.iterrows()):
        R_root = recompose_zxy(A[i, :3])
        for side, sh_i, Lu, Lf in (("right", 3, L_up_r, L_fo_r),
                                   ("left", 8, L_up_l, L_fo_l)):
            sh = get(row, f"{side}_shoulder")
            if sh is None:
                continue
            up, fo = fk_arm_dirs(A[i, sh_i:sh_i + 3],
                                 A[i, sh_i + 3:sh_i + 5], side)
            elb = sh + Lu * (R_root @ up)
            wri = elb + Lf * (R_root @ fo)
            fk[side][i, 0], fk[side][i, 1] = elb, wri
            wm = get(row, f"{side}_wrist")
            if wm is not None:
                res_wrist[side][i] = np.linalg.norm(wri - wm)

    for side in ("right", "left"):
        r = res_wrist[side] * 100
        ok = np.isfinite(r)
        print(f"[fk] {side} wrist FK-vs-measured: median "
              f"{np.nanmedian(r):.1f} cm, p95 {np.nanpercentile(r[ok], 95):.1f} cm "
              f"({ok.sum()} frames)")

    # ---- plots ----
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = df["time_s"].to_numpy()
    fig, ax = plt.subplots(3, 1, figsize=(14, 12))
    for name, (Ar, _) in runs.items():
        ax[0].plot(t, Ar[:, 1], label=f"root yaw {name}", lw=1)
    ax[0].set_ylabel("deg"); ax[0].legend(); ax[0].set_title(
        "root yaw (a1) - jumps here = sudden direction changes")
    pel = np.stack([0.5 * (get(row, "left_hip") + get(row, "right_hip"))
                    if get(row, "left_hip") is not None
                    and get(row, "right_hip") is not None
                    else np.full(3, np.nan)
                    for _, row in df.iterrows()])
    ax[1].plot(pel[:, 0], pel[:, 2], ".", ms=2)
    ax[1].set_xlabel("x (m, camera right)"); ax[1].set_ylabel("z (m, depth)")
    ax[1].set_title("pelvis top-down track (camera frame)")
    ax[1].axis("equal")
    for side, c in (("right", "r"), ("left", "b")):
        ax[2].plot(t, res_wrist[side] * 100, c, lw=0.8, label=f"{side}")
    ax[2].set_ylabel("cm"); ax[2].set_xlabel("time (s)")
    ax[2].set_title("FK wrist vs measured wrist residual"); ax[2].legend()
    fig.tight_layout()
    fig.savefig(out_dir / "v1_check_plots.png", dpi=110)
    print(f"[plot] {out_dir / 'v1_check_plots.png'}")

    # ---- overlay video ----
    import pyrealsense2 as rs
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(str(bag), repeat_playback=False)
    profile = pipeline.start(config)
    profile.get_device().as_playback().set_real_time(False)
    color_format = profile.get_stream(rs.stream.color).format()

    tmp = out_dir / "overlay_tmp.mp4"
    vw = cv2.VideoWriter(str(tmp), cv2.VideoWriter_fourcc(*"mp4v"),
                         30, (K["width"], K["height"]))
    BONES = [("left_shoulder", "right_shoulder"), ("left_hip", "right_hip"),
             ("left_shoulder", "left_hip"), ("right_shoulder", "right_hip"),
             ("right_shoulder", "right_elbow"), ("right_elbow", "right_wrist"),
             ("left_shoulder", "left_elbow"), ("left_elbow", "left_wrist")]
    i = 0
    while i < n:
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
        row = df.iloc[i]

        # measured skeleton, green
        mp2d = {}
        for k in LANDMARKS:
            p = np.array([row[f"{k}_x"], row[f"{k}_y"], row[f"{k}_z"]])
            if np.all(np.isfinite(p)):
                mp2d[k] = project(p, K)
        for a, b in BONES:
            if mp2d.get(a) and mp2d.get(b):
                cv2.line(img, mp2d[a], mp2d[b], (0, 200, 0), 1)
        for k, uv in mp2d.items():
            if uv:
                cv2.circle(img, uv, 3, (0, 255, 0), -1)

        # FK skeleton (flip back to sensor before projecting)
        for side, col in (("right", (0, 0, 255)), ("left", (255, 80, 0))):
            sh = None
            p = np.array([row[f"{side}_shoulder_x"],
                          row[f"{side}_shoulder_y"],
                          row[f"{side}_shoulder_z"]])
            if np.all(np.isfinite(p)):
                sh = project(p, K)
            e = fk[side][i, 0] * SENSOR_FLIP
            w = fk[side][i, 1] * SENSOR_FLIP
            e2, w2 = project(e, K), project(w, K)
            if sh and e2:
                cv2.line(img, sh, e2, col, 2)
            if e2 and w2:
                cv2.line(img, e2, w2, col, 2)
            if w2:
                cv2.circle(img, w2, 5, col, 2)

        # root forward arrow from pelvis midpoint
        if np.all(np.isfinite(pel[i])):
            R_root = recompose_zxy(A[i, :3])
            tip = (pel[i] + 0.35 * (R_root @ np.array([0, 0, 1.0])))
            p0 = project(pel[i] * SENSOR_FLIP, K)
            p1 = project(tip * SENSOR_FLIP, K)
            if p0 and p1:
                cv2.arrowedLine(img, p0, p1, (255, 0, 255), 2, tipLength=0.25)

        # recovery mode: failure banner + object-derived wrist marker
        if fail is not None:
            fired = [lbl for key, lbl in (("left", "ARM L"),
                                          ("right", "ARM R"),
                                          ("torso", "TORSO"))
                     if fail[key][i]]
            if fired:
                cv2.rectangle(img, (0, K["height"] - 26),
                              (K["width"], K["height"]), (0, 0, 160), -1)
                cv2.putText(img, "TRACKING FAILURE: " + " ".join(fired),
                            (8, K["height"] - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (255, 255, 255), 1)
        if w_hat is not None:
            for side in ("left", "right"):
                wv = w_hat[side][i]
                if np.all(np.isfinite(wv)):
                    uv = project(wv * SENSOR_FLIP, K)
                    if uv:
                        cv2.drawMarker(img, uv, (0, 220, 255),
                                       cv2.MARKER_CROSS, 12, 2)

        cv2.putText(img, f"f{int(row['frame'])} t={row['time_s']:.2f}s "
                    f"mask={M[i]:03d}", (8, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        vw.write(img)
        i += 1
    vw.release()
    pipeline.stop()

    final = out_dir / f"v1_overlay_{which[0]}.mp4"
    import subprocess
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp),
                    "-c:v", "libx264", "-crf", "22", "-pix_fmt", "yuv420p",
                    str(final)], check=True)
    tmp.unlink()
    print(f"[video] {final} ({i} frames)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""VENDORED COPY - eval/unity_check/send_scene_r5.py

Source:  /home/luo/Desktop/New_SandBox/v1/integration/send_integrated_scene.py
Copied:  2026-08-26 (eval/ track; the v1 tree is frozen and never edited).

Differences from the source, all confined to input selection and the
optional precomputed-angle path; the shared-memory layout, the pacing and
the solve are byte-for-byte the original:

  * stem-driven inputs through eval/common/paths.py (R5 by default), so the
    marker-size-corrected object track and calibration under eval/output/
    are picked up automatically;
  * --angles-csv <file>: skip the internal ChainFallbackSolver solve and
    stream the 13 angles + live mask straight out of that CSV (the
    eval/output/recovery_r5/angles_*.csv variants), pelvis and object pose
    still coming from the landmark/object CSVs. Without it the sender
    solves exactly as v1 does.

Full-system stream: Pipeline B scene + Pipeline A person -> Unity.

  /dev/shm/aruco_scene       PSB3, written once (static desk/wall/camera
                             poses, gravity, tabletop drop, cube size,
                             sensor FOV)
  /dev/shm/integrated_scene  PSI1 (108 B, seqlock), per frame:
      u32 magic 'PSI1' | u32 seq | i32 frame | f32 time_s
      3f pelvis (Pipeline-A Unity space: camera frame, y flipped)
      13f angles: root Euler xyz, R shoulder y/z/twist, R elbow y/z,
                  L shoulder y/z/twist, L elbow y/z          (PSA5 order)
      3f object pos + 3f object Euler (desk world -> Unity, PSB2 pose)
      u16 person live mask (PSA5 bits) | u16 object live

Usage:
  python eval/unity_check/send_scene_r5.py                       # v1 solve
  python eval/unity_check/send_scene_r5.py \
      --angles-csv eval/output/recovery_r5/angles_recovery.csv --loop
"""
import argparse
import mmap
import struct
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "v1" / "kinematics"))
sys.path.insert(0, str(REPO / "v1" / "aruco"))
sys.path.insert(0, str(REPO / "eval"))

from occlusion import ChainFallbackSolver, LANDMARKS          # Pipeline A
from root_frame import unity_from_sensor                      # Pipeline A
from send_scene_poses import write_scene                      # Pipeline B
from common import paths as P                                 # eval/ paths
import json

MAGIC = 0x31495350  # 'PSI1'
FMT = "<IIif3f13f3f3fHH"
PACKET_SIZE = struct.calcsize(FMT)
assert PACKET_SIZE == 108

# Packet angle order (PSA5); the recovery CSVs use these exact names.
ANGLE_COLS = ["root_ex", "root_ey", "root_ez",
              "Rsh_y", "Rsh_z", "Rsh_tau", "Rel_y", "Rel_z",
              "Lsh_y", "Lsh_z", "Lsh_tau", "Lel_y", "Lel_z"]


def load_angles_csv(path):
    """frame -> (13 angles, live mask, pelvis or None) from a
    precomputed angle CSV. Pelvis columns (pel_x/y/z, the solver's
    post-recovery hip midpoint - free of the depth wobble the raw
    hip midpoint carries during torso corruption) are optional."""
    df = pd.read_csv(path)
    missing = [c for c in ANGLE_COLS + ["frame", "live_mask"]
               if c not in df.columns]
    if missing:
        sys.exit(f"[ERROR] {path.name} missing columns: {missing}")
    A = df[ANGLE_COLS].to_numpy(dtype=float)
    m = df["live_mask"].to_numpy(dtype=int)
    if all(c in df.columns for c in ("pel_x", "pel_y", "pel_z")):
        P_ = df[["pel_x", "pel_y", "pel_z"]].to_numpy(dtype=float)
    else:
        P_ = np.full((len(df), 3), np.nan)
    return {int(f): (A[i], int(m[i]), P_[i])
            for i, f in enumerate(df["frame"])}


def _wrap(d):
    return (d + 180.0) % 360.0 - 180.0


class AngleLPF:
    """Causal wrap-aware display smoother on the 13 angle stream, for
    DISPLAY only (user direction 2026-08-26: the residual solver
    steps - the 15 deg/frame slew-limit saturations and the root's
    E-011 re-locks, up to 26 deg/frame - read as visible jumps in
    Unity).

    First-order low-pass (gain alpha) plus an output rate cap
    (max_step deg/frame). Both parts are needed, and why is worth
    recording: the solver's transitions are 3-5 frame RAMPS at its
    slew bound, and ANY unity-gain linear filter eventually follows
    a ramp at the ramp's own slope - measured: a single pole let
    14.7 of 15 deg/frame through, a 2nd-order Butterworth 16
    deg/frame WITH up to 52 deg of overshoot. So the low-pass rounds
    the corners and kills isolated spikes, and the rate cap is what
    actually bounds the on-screen speed, spreading a transition over
    proportionally more frames. Defaults: alpha 0.5 (measured
    tracking error p95 2.1 deg on the R5 recovery track), max_step
    8 deg/frame (240 deg/s - above normal desk motion, roughly half
    the solver's transition bound). alpha >= 1 with max_step = 0
    disables. Analysis CSVs stay unfiltered."""

    def __init__(self, alpha=0.5, max_step=8.0):
        self.alpha = alpha
        self.max_step = max_step
        self.y = None

    def __call__(self, x):
        x = np.asarray(x, float)
        if self.alpha >= 1.0 and not self.max_step:
            return x
        if self.y is None:
            self.y = x.copy()
            return x.copy()
        target = self.y + min(self.alpha, 1.0) * _wrap(x - self.y)
        d = _wrap(target - self.y)
        if self.max_step:
            d = np.clip(d, -self.max_step, self.max_step)
        self.y = _wrap(self.y + d)
        return self.y.copy()


def build_frames(landmark_csv, object_csv, angles_csv=None,
                 lpf_alpha=0.5, lpf_max_step=8.0):
    """One record per frame: person pelvis + angles joined with the object's
    world pose. Missing data holds the last value with the matching live flag
    cleared — same philosophy on both sides.

    Angles come from the real Pipeline A chain-fallback solve unless
    angles_csv supplies them; the pelvis and the object pose always come
    from the CSVs. The streamed angles pass the display low-pass
    (AngleLPF) so bounded solver steps do not read as jumps on the rig."""
    lm = pd.read_csv(landmark_csv)
    ob = pd.read_csv(object_csv)
    if len(lm) != len(ob):
        sys.exit(f"[ERROR] frame count mismatch: {len(lm)} landmarks vs "
                 f"{len(ob)} object rows — not the same recording?")
    pre = load_angles_csv(angles_csv) if angles_csv else None
    solver = None if pre else ChainFallbackSolver()
    lpf = AngleLPF(lpf_alpha, lpf_max_step)
    # pelvis display smoother: same shape, position units - the wrap
    # arithmetic is the identity for meter-scale values; rate cap
    # 2 cm/frame (60 cm/s, above any standing-subject pelvis motion)
    pel_lpf = AngleLPF(lpf_alpha, 0.02 if lpf_max_step else 0.0)
    out = []
    last_pel = np.zeros(3)
    last_obj = ([0.0] * 3, [0.0] * 3)
    have_obj = False
    for i in range(len(lm)):
        row = lm.iloc[i]
        p = {k: unity_from_sensor([row[f"{k}_x"], row[f"{k}_y"], row[f"{k}_z"]])
             for k in LANDMARKS}
        pel_pre = None
        if pre is None:
            angles, mask = solver.solve(p)
        else:
            key = int(row["frame"])
            if key not in pre:
                sys.exit(f"[ERROR] frame {key} absent from {angles_csv.name}")
            angles, mask, pel_pre = pre[key]
        angles = lpf(angles)
        pel = (pel_pre if pel_pre is not None
               and np.all(np.isfinite(pel_pre))
               else (p["left_hip"] + p["right_hip"]) / 2.0)
        if np.all(np.isfinite(pel)):
            last_pel = pel_lpf(pel)
        orow = ob.iloc[i]
        # A filtered object CSV (aruco/filter_object_track.py) carries a
        # usable pose on every row (interior gaps bridged, boundaries held)
        # with `detected` kept as the honesty flag; a raw CSV has NaNs on
        # undetected rows, so those fall back to hold-last.
        if np.isfinite(orow["unity_px"]):
            last_obj = ([orow["unity_px"], orow["unity_py"], orow["unity_pz"]],
                        [orow["unity_ex"], orow["unity_ey"], orow["unity_ez"]])
            have_obj = True
            obj_live = int(orow["detected"])
        else:
            obj_live = 0
        if not have_obj:
            continue
        out.append((int(row["frame"]), float(row["time_s"]),
                    list(last_pel), list(angles), *last_obj, mask, obj_live))
    return out


class ShmWriter:
    def __init__(self, path):
        with open(path, "wb") as f:
            f.write(b"\x00" * PACKET_SIZE)
        self._f = open(path, "r+b")
        self._mm = mmap.mmap(self._f.fileno(), PACKET_SIZE)
        self._seq = 0

    def write(self, frame, t, pel, angles, opos, oeul, mask, olive):
        self._seq += 1  # odd: writer busy
        self._mm[4:8] = struct.pack("<I", self._seq)
        self._mm[8:PACKET_SIZE] = struct.pack(
            "<if3f13f3f3fHH", frame, t, *pel, *angles, *opos, *oeul, mask, olive)
        self._seq += 1  # even: stable
        self._mm[0:4] = struct.pack("<I", MAGIC)
        self._mm[4:8] = struct.pack("<I", self._seq)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stem", default=P.R5_STEM)
    ap.add_argument("--landmarks", type=Path, default=None,
                    help="override paths.lm_filtered(stem)")
    ap.add_argument("--object-csv", type=Path, default=None,
                    help="override paths.object_world_filtered(stem)")
    ap.add_argument("--calib", type=Path, default=None,
                    help="override paths.calib_for(stem)")
    ap.add_argument("--angles-csv", type=Path, default=None,
                    help="stream these precomputed angles + live mask "
                         "instead of solving (eval/output/recovery_r5/*.csv)")
    ap.add_argument("--scene-shm", default="/dev/shm/aruco_scene")
    ap.add_argument("--shm", default="/dev/shm/integrated_scene")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--dump-csv", type=Path, default=None,
                    help="Also write the streamed records to a CSV (validation)")
    ap.add_argument("--lpf-alpha", type=float, default=0.5,
                    help="display smoother low-pass gain on the "
                         "streamed angles (first-order, wrap-aware; "
                         ">= 1 disables the low-pass part)")
    ap.add_argument("--lpf-max-step", type=float, default=8.0,
                    help="display smoother output rate cap, deg/frame "
                         "(0 disables the cap)")
    args = ap.parse_args()

    landmarks = args.landmarks or P.lm_filtered(args.stem)
    object_csv = args.object_csv or P.object_world_filtered(args.stem)
    calib_path = args.calib or P.calib_for(args.stem)
    print(f"[+] stem {args.stem}\n    landmarks {landmarks}\n"
          f"    object    {object_csv}\n    calib     {calib_path}")
    if args.angles_csv:
        print(f"    angles    {args.angles_csv} (internal solve SKIPPED)")

    calib = json.loads(calib_path.read_text())
    frames = build_frames(landmarks, object_csv, args.angles_csv,
                          lpf_alpha=args.lpf_alpha,
                          lpf_max_step=args.lpf_max_step)
    if args.lpf_alpha < 1.0 or args.lpf_max_step:
        print(f"[+] display smoother on angles: alpha {args.lpf_alpha}, "
              f"rate cap {args.lpf_max_step} deg/frame")
    print(f"[+] {len(frames)} integrated frames "
          f"({landmarks.name} + {object_csv.name})")

    if args.dump_csv:
        rows = []
        for f, t, pel, ang, opos, oeul, mask, olive in frames:
            rows.append({"frame": f, "time_s": t, "mask": mask, "obj_live": olive,
                         **{k: v for k, v in zip(("pel_x", "pel_y", "pel_z"), pel)},
                         **{f"a{i}": v for i, v in enumerate(ang)},
                         **{k: v for k, v in zip(("opx", "opy", "opz"), opos)},
                         **{k: v for k, v in zip(("oex", "oey", "oez"), oeul)}})
        args.dump_csv.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(rows).to_csv(args.dump_csv, index=False)
        print(f"[+] dump -> {args.dump_csv}")

    write_scene(args.scene_shm, calib)   # PSB3, once
    w = ShmWriter(args.shm)
    n = 0
    npass = 0
    while True:
        t0 = time.monotonic()
        for f, t, pel, ang, opos, oeul, mask, olive in frames:
            dt = t0 + t / args.speed - time.monotonic()
            if dt > 0:
                time.sleep(dt)
            w.write(f, t, pel, ang, opos, oeul, mask, olive)
            n += 1
        npass += 1
        print(f"[+] streamed {n} frames (pass {npass})", flush=True)
        if not args.loop:
            break
        n = 0


if __name__ == "__main__":
    main()

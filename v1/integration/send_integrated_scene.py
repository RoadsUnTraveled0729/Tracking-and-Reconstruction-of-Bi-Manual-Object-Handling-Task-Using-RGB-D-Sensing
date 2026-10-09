#!/usr/bin/env python3
# Filename: integration/send_integrated_scene.py
"""Full-system stream: Pipeline B scene + Pipeline A person -> Unity.

Evaluation-stage integration (INTEGRATION.md): Pipelines A and B stay
independent; this layer reads BOTH their per-frame outputs for the SAME
recording (the CSVs come from one bag, so frames align 1:1) and streams
them together:

  /dev/shm/aruco_scene       PSB3, written once (reused from Pipeline B's
                             sender: static desk/wall/camera poses, gravity,
                             tabletop drop, cube size, sensor FOV)
  /dev/shm/integrated_scene  PSI1 (108 B, seqlock), per frame:
      u32 magic 'PSI1' | u32 seq | i32 frame | f32 time_s
      3f pelvis (Pipeline-A Unity space: camera frame, y flipped)
      13f angles: root Euler xyz, R shoulder y/z/twist, R elbow y/z,
                  L shoulder y/z/twist, L elbow y/z          (PSA5 order)
      3f object pos + 3f object Euler (desk world -> Unity, PSB2 pose)
      u16 person live mask (PSA5 bits) | u16 object live

Person angles come from the real Pipeline A chain (occlusion.py
ChainFallbackSolver); the object pose comes from Pipeline B's world CSV.
The person -> scene placement math lives entirely on the Unity side
(IntegratedSceneReceiver.cs PersonAnchor); this sender ships person-space
coordinates untouched.

Usage:
  python send_integrated_scene.py            # one pass, real time
  python send_integrated_scene.py --loop --speed 0.5
"""
import argparse
import mmap
import struct
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "kinematics"))
sys.path.insert(0, str(HERE.parent / "aruco"))

from occlusion import ChainFallbackSolver, LANDMARKS          # Pipeline A
from root_frame import unity_from_sensor                      # Pipeline A
from send_scene_poses import write_scene                      # Pipeline B
import json

MAGIC = 0x31495350  # 'PSI1'
FMT = "<IIif3f13f3f3fHH"
PACKET_SIZE = struct.calcsize(FMT)
assert PACKET_SIZE == 108


def build_frames(landmark_csv, object_csv):
    """One record per frame: person pelvis + angles (chain-fallback solve)
    joined with the object's world pose. Missing data holds the last value
    with the matching live flag cleared — same philosophy on both sides."""
    lm = pd.read_csv(landmark_csv)
    ob = pd.read_csv(object_csv)
    if len(lm) != len(ob):
        sys.exit(f"[ERROR] frame count mismatch: {len(lm)} landmarks vs "
                 f"{len(ob)} object rows — not the same recording?")
    solver = ChainFallbackSolver()
    out = []
    last_pel = np.zeros(3)
    last_obj = ([0.0] * 3, [0.0] * 3)
    have_obj = False
    for i in range(len(lm)):
        row = lm.iloc[i]
        p = {k: unity_from_sensor([row[f"{k}_x"], row[f"{k}_y"], row[f"{k}_z"]])
             for k in LANDMARKS}
        angles, mask = solver.solve(p)
        pel = (p["left_hip"] + p["right_hip"]) / 2.0
        if np.all(np.isfinite(pel)):
            last_pel = pel
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
    ap.add_argument("--landmarks", type=Path,
                    default=HERE.parent / "mediapipe" / "output"
                    / "recording_20260224_083945_landmarks_filtered_v2.csv")
    ap.add_argument("--object-csv", type=Path,
                    default=HERE.parent / "aruco" / "output"
                    / "recording_20260224_083945_object_world_filtered.csv")
    ap.add_argument("--calib", type=Path,
                    default=HERE.parent / "aruco" / "output" / "scene_calibration.json")
    ap.add_argument("--scene-shm", default="/dev/shm/aruco_scene")
    ap.add_argument("--shm", default="/dev/shm/integrated_scene")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--dump-csv", type=Path, default=None,
                    help="Also write the streamed records to a CSV (validation)")
    args = ap.parse_args()

    calib = json.loads(args.calib.read_text())
    frames = build_frames(args.landmarks, args.object_csv)
    print(f"[+] {len(frames)} integrated frames "
          f"({args.landmarks.name} + {args.object_csv.name})")

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
    while True:
        t0 = time.monotonic()
        for f, t, pel, ang, opos, oeul, mask, olive in frames:
            dt = t0 + t / args.speed - time.monotonic()
            if dt > 0:
                time.sleep(dt)
            w.write(f, t, pel, ang, opos, oeul, mask, olive)
            n += 1
        print(f"[+] streamed {n} frames")
        if not args.loop:
            break
        n = 0


if __name__ == "__main__":
    main()

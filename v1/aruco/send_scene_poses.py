#!/usr/bin/env python3
# Filename: aruco/send_scene_poses.py
# Pipeline B, stage 3: calibrated scene + object stream -> Unity shared memory.
#
# Static scene (user design: "send the wall and desk frame once"): the
# calibrated world-frame poses of desk, wall and camera are written ONCE to
# /dev/shm/aruco_scene (PSB1, no seqlock — written before the stream starts,
# receiver validates the magic). The moving object is streamed per frame to
# /dev/shm/aruco_object (PSB2, seqlock like the PSA packets). Frames where
# the object marker was not detected hold the last pose with live=0 —
# same philosophy as the Pipeline A occlusion mask (KINEMATIC_MODEL.md §10).
#
# PSB3 (100 B): magic u32 'PSB3', then desk/wall/camera x (pos xyz + Unity
#              ZXY Euler xyz), gravity up (Unity, world-local), world-origin
#              height above the tabletop plane (m), object cube edge (m),
#              sensor vertical FOV (deg) — all f32, world->Unity mapping
#              already applied. Supersedes PSB1 (triads-only scene).
# PSB2 (44 B): magic u32 'PSB2', seq u32 (odd = writer busy), frame i32,
#              time f32, pos 3f, euler 3f, live u16, 2B pad.
#
# Usage:
#   python send_scene_poses.py                    # stream once, real time
#   python send_scene_poses.py --loop --speed 0.5

import argparse
import json
import mmap
import struct
import time
from pathlib import Path

import pandas as pd

MAGIC_SCENE = 0x33425350   # 'PSB3'
MAGIC_OBJECT = 0x32425350  # 'PSB2'
SCENE_FMT = "<I24f"        # 100 bytes
OBJECT_FMT = "<IIif3f3fH2x"  # 44 bytes
OBJECT_SIZE = struct.calcsize(OBJECT_FMT)


def write_scene(path, calib):
    vals = []
    for name in ("desk", "wall", "camera"):
        blk = calib["poses_world"][name]
        vals += list(blk["unity_position"]) + list(blk["unity_euler_zxy_deg"])
    g = calib["scene_geometry"]
    vals += list(g["gravity_up_unity"])
    vals += [g["origin_above_tabletop_m"], g["object_cube_size_m"],
             g["sensor_fov_y_deg"]]
    Path(path).write_bytes(struct.pack(SCENE_FMT, MAGIC_SCENE, *vals))
    print(f"[+] scene written once -> {path} (desk, wall, camera poses + "
          f"gravity, tabletop drop {g['origin_above_tabletop_m']*1000:.0f} mm, "
          f"cube {g['object_cube_size_m']*1000:.0f} mm, "
          f"sensor FOVy {g['sensor_fov_y_deg']:.1f} deg)")


class ObjectWriter:
    def __init__(self, path):
        f = open(path, "w+b")
        f.truncate(OBJECT_SIZE)
        self.mm = mmap.mmap(f.fileno(), OBJECT_SIZE)
        f.close()
        self.seq = 0

    def write(self, frame, t, pos, euler, live):
        self.seq += 1  # odd: writer busy
        self.mm[:OBJECT_SIZE] = struct.pack(
            OBJECT_FMT, MAGIC_OBJECT, self.seq, frame, t, *pos, *euler, live)
        self.seq += 1  # even: stable
        self.mm[4:8] = struct.pack("<I", self.seq)


def main():
    script_dir = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Send the calibrated ArUco scene (once) + object pose stream to Unity.")
    ap.add_argument("--calib", default=str(script_dir / "output" / "scene_calibration.json"))
    ap.add_argument("--world-csv", default=str(script_dir / "output" / "recording_20260328_021733_object_world_filtered.csv"))
    ap.add_argument("--scene-shm", default="/dev/shm/aruco_scene")
    ap.add_argument("--object-shm", default="/dev/shm/aruco_object")
    ap.add_argument("--speed", type=float, default=1.0, help="Playback speed factor")
    ap.add_argument("--loop", action="store_true", help="Loop the recording forever")
    args = ap.parse_args()

    calib = json.loads(Path(args.calib).read_text())
    df = pd.read_csv(args.world_csv)
    write_scene(args.scene_shm, calib)
    w = ObjectWriter(args.object_shm)

    last = None  # (pos, euler) held while the object marker is blocked
    n_sent = n_held = 0
    while True:
        t0 = time.monotonic()
        for _, row in df.iterrows():
            target = t0 + row["time_s"] / args.speed
            dt = target - time.monotonic()
            if dt > 0:
                time.sleep(dt)
            # A filtered CSV (filter_object_track.py) carries a usable pose
            # on every row (gaps bridged, boundaries held) with `detected`
            # kept as the honesty flag; a raw CSV has NaNs when undetected.
            if pd.notna(row["unity_px"]):
                last = ([row["unity_px"], row["unity_py"], row["unity_pz"]],
                        [row["unity_ex"], row["unity_ey"], row["unity_ez"]])
                live = int(row["detected"])
            else:
                live = 0
            if not live:
                n_held += 1
            if last is None:
                continue  # nothing valid yet
            w.write(int(row["frame"]), float(row["time_s"]), last[0], last[1], live)
            n_sent += 1
        print(f"[+] streamed {n_sent} frames ({n_held} held)")
        if not args.loop:
            break
        n_sent = n_held = 0


if __name__ == "__main__":
    main()

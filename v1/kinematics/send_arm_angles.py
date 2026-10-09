"""Stream root + BOTH arms' joint angles to Unity.

Computes, per frame of a landmark CSV, through the real pipeline
(KINEMATIC_MODEL.md §3-10):
  - root Euler (x, y, z)            from L23/L24 + a shoulder (§3-4, §10)
  - R shoulder (θy, θz, θτ)         swing-twist solve (§6)
  - R elbow (ey, ez)                swing in the L14 frame (§7; ez ≡ 0)
  - L shoulder + L elbow            mirror convention (§9)
  - blocked landmarks               chain fallback: affected joints hold
                                    their last valid angle, the rest stay
                                    live; per-joint live mask in the
                                    packet (§10, occlusion.py)

Packet (/dev/shm/pose_arm, 72 bytes LE, seqlock like the other bridges):
  u32 magic 'PSA5' (0x35415350) | u32 seq (odd = mid-update)
  i32 frame | f32 time_s
  f32 root_x, root_y, root_z
  f32 rsh_y, rsh_z, rsh_twist | f32 relb_y, relb_z
  f32 lsh_y, lsh_z, lsh_twist | f32 lelb_y, lelb_z
  u16 live_mask (bits: root, Rswing, Rtwist, Relbow, Lswing, Ltwist,
                 Lelbow; set = solved live, clear = held) | 2B pad
Mirrored in Unity/Assets/Scripts/ArmAngleReceiver.cs — keep in sync.
"""
import argparse
import mmap
import struct
import time
from pathlib import Path

import numpy as np
import pandas as pd

from occlusion import ChainFallbackSolver, LANDMARKS
from root_frame import unity_from_sensor

MAGIC = 0x35415350  # 'PSA5'
PACKET_SIZE = 72


def compute_angles(csv_path):
    """Angles per frame via the chain-fallback solver (occlusion.py):
    EVERY frame yields a row; blocked landmarks make the affected joints
    hold their last valid angle, reported in the trailing live mask.

    Yields (frame, time_s, 13 angles..., live_mask)."""
    df = pd.read_csv(csv_path)
    solver = ChainFallbackSolver()
    out = []
    for i in range(len(df)):
        row = df.iloc[i]
        p = {k: unity_from_sensor([row[f"{k}_x"], row[f"{k}_y"], row[f"{k}_z"]])
             for k in LANDMARKS}
        angles, mask = solver.solve(p)
        out.append((int(row["frame"]), float(row["time_s"]), *angles, mask))
    return out


class ShmWriter:
    def __init__(self, path):
        p = Path(path)
        with open(p, "wb") as f:
            f.write(b"\x00" * PACKET_SIZE)
        self._f = open(p, "r+b")
        self._mm = mmap.mmap(self._f.fileno(), PACKET_SIZE)
        self._seq = 0

    def write(self, frame, t, vals13, mask):
        self._seq += 1  # odd: writer busy
        self._mm[4:8] = struct.pack("<I", self._seq)
        self._mm[8:PACKET_SIZE] = struct.pack(
            "<if13fH2x", frame, t, *vals13, mask)
        self._seq += 1  # even: stable
        self._mm[0:4] = struct.pack("<I", MAGIC)
        self._mm[4:8] = struct.pack("<I", self._seq)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    ap.add_argument("--csv", type=Path,
                    default=here / "output" / "shoulder_only_landmarks.csv")
    ap.add_argument("--shm-path", default="/dev/shm/pose_arm")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--no-loop", action="store_true")
    args = ap.parse_args()

    frames = compute_angles(args.csv)
    print(f"streaming {len(frames)} frames from {args.csv.name} "
          f"to {args.shm_path}")
    w = ShmWriter(args.shm_path)
    period = (frames[1][1] - frames[0][1]) / args.speed if len(frames) > 1 else 1 / 30
    while True:
        for rec in frames:
            w.write(rec[0], rec[1], rec[2:-1], rec[-1])
            time.sleep(period)
        if args.no_loop:
            break


if __name__ == "__main__":
    main()

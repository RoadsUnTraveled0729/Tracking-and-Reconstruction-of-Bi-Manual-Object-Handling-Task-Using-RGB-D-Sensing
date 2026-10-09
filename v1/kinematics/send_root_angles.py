"""Compute root-frame Euler angles from a landmark CSV and stream them to Unity.

Runs the real pipeline per frame: sensor-space CSV -> Unity mapping ->
L24 root frame -> Unity ZXY Euler (KINEMATIC_MODEL.md §3-4), then writes
each frame into shared memory for RootAngleReceiver.cs.

Packet layout (little-endian, 32 bytes, /dev/shm/pose_angles):
  0  u32 magic 'PSA1' (0x31415350)
  4  u32 seq (seqlock: odd = writer mid-update, even = stable)
  8  i32 frame index
  12 f32 time_s
  16 f32 euler_x   20 f32 euler_y   24 f32 euler_z   (degrees, Unity ZXY)
  28 4 bytes padding

With --truth, the computed angles are first cross-checked against a
ground-truth CSV (wrap-aware) and the run aborts if they disagree.
"""
import argparse
import mmap
import struct
import time
from pathlib import Path

import numpy as np
import pandas as pd

from root_frame import build_root_frame, euler_unity_zxy, unity_from_sensor, wrap_deg

MAGIC = 0x31415350  # 'PSA1'
PACKET_SIZE = 32
FPS = 30.0


def landmarks_unity(df, name):
    return unity_from_sensor(df[[f"{name}_x", f"{name}_y", f"{name}_z"]].to_numpy())


def compute_angles(df):
    p23 = landmarks_unity(df, "left_hip")
    p24 = landmarks_unity(df, "right_hip")
    p12 = landmarks_unity(df, "right_shoulder")
    return euler_unity_zxy(build_root_frame(p23, p24, p12))


class ShmWriter:
    def __init__(self, path):
        with open(path, "wb") as f:
            f.write(b"\x00" * PACKET_SIZE)
        self.f = open(path, "r+b")
        self.mm = mmap.mmap(self.f.fileno(), PACKET_SIZE)
        self.seq = 0

    def write(self, frame, t, e):
        body = struct.pack("<if3f4x", frame, t, e[0], e[1], e[2])
        self.seq += 1  # odd: mid-update
        self.mm[4:8] = struct.pack("<I", self.seq)
        self.mm[0:4] = struct.pack("<I", MAGIC)
        self.mm[8:32] = body
        self.seq += 1  # even: stable
        self.mm[4:8] = struct.pack("<I", self.seq)

    def close(self):
        self.mm.close()
        self.f.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    default_csv = Path(__file__).resolve().parent / "output" / "synthetic_landmarks.csv"
    ap.add_argument("--csv", type=Path, default=default_csv)
    ap.add_argument("--truth", type=Path, default=None,
                    help="Ground-truth angle CSV to cross-check before streaming")
    ap.add_argument("--shm-path", default="/dev/shm/pose_angles")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--no-loop", action="store_true")
    ap.add_argument("--check-only", action="store_true",
                    help="Only run the truth cross-check, do not stream")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    if "has_pose" in df.columns:
        df = df[df["has_pose"] == 1].reset_index(drop=True)
    e = compute_angles(df)
    times = df["time_s"].to_numpy()
    frames = df["frame"].to_numpy()

    if args.truth is not None:
        tr = pd.read_csv(args.truth)[["euler_x", "euler_y", "euler_z"]].to_numpy()
        err = np.abs(wrap_deg(e - tr)).max()
        print(f"pipeline vs ground truth: max |angle error| = {err:.3e} deg "
              f"over {len(df)} frames x 3 axes")
        if err > 1e-6:
            raise SystemExit("FAIL: pipeline output does not match injected truth")
        print("PASS")
    if args.check_only:
        return

    w = ShmWriter(args.shm_path)
    dt = 1.0 / (FPS * args.speed)
    print(f"streaming {len(df)} frames to {args.shm_path} "
          f"({'once' if args.no_loop else 'looping'}, speed x{args.speed})")
    try:
        while True:
            for i in range(len(df)):
                w.write(int(frames[i]), float(times[i]), e[i])
                time.sleep(dt)
            if args.no_loop:
                break
    except KeyboardInterrupt:
        pass
    finally:
        w.close()


if __name__ == "__main__":
    main()

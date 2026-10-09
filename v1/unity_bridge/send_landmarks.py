#!/usr/bin/env python3
# Filename: unity_bridge/send_landmarks.py
# Streams a landmark CSV to Unity frame-by-frame, paced to the recorded
# timestamps. Two transports (matching PoseStreamReceiver.cs):
#   shm (default): writes a fixed 180-byte record into /dev/shm/pose_stream,
#       guarded by a seqlock (seq odd while writing, even when stable)
#   udp: sends the same 180-byte packet to a local port
#
# Packet layout (little-endian, 180 bytes):
#   0  u32 magic 'PSE1'
#   4  u32 seq (shm only)
#   8  i32 frame index
#   12 f32 time_s
#   16 i32 landmark count (8)
#   20 8 x { i32 mediapipe_id, f32 x, f32 y, f32 z, i32 valid }
#
# Usage:
#   python send_landmarks.py                          # newest filtered CSV, shm, loop
#   python send_landmarks.py --csv <path> --transport udp --no-loop --speed 2

import argparse
import mmap
import socket
import struct
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

MAGIC = int.from_bytes(b"PSE1", "little")
PACKET_SIZE = 180
LANDMARKS = [(11, "left_shoulder"), (12, "right_shoulder"),
             (13, "left_elbow"), (14, "right_elbow"),
             (15, "left_wrist"), (16, "right_wrist"),
             (23, "left_hip"), (24, "right_hip")]


def build_packets(df):
    """Pre-pack the payload (everything after seq) for every frame."""
    frames = df["frame"].to_numpy(int)
    times = df["time_s"].to_numpy(float)
    pos = {i: df[[f"{n}_x", f"{n}_y", f"{n}_z"]].to_numpy(float) for i, n in LANDMARKS}
    packets = []
    for k in range(len(df)):
        body = struct.pack("<ifi", frames[k], times[k], len(LANDMARKS))
        for i, _ in LANDMARKS:
            p = pos[i][k]
            ok = np.all(np.isfinite(p))
            x, y, z = (p if ok else (0.0, 0.0, 0.0))
            body += struct.pack("<ifffi", i, x, y, z, int(ok))
        packets.append(body)
    return times, packets


class ShmWriter:
    def __init__(self, path):
        self.path = Path(path)
        with open(self.path, "wb") as f:
            f.write(b"\x00" * PACKET_SIZE)
        self.f = open(self.path, "r+b")
        self.mm = mmap.mmap(self.f.fileno(), PACKET_SIZE)
        self.seq = 0
        struct.pack_into("<I", self.mm, 0, MAGIC)

    def send(self, body):
        self.seq += 1                                   # odd: writing
        struct.pack_into("<I", self.mm, 4, self.seq)
        self.mm[8:8 + len(body)] = body
        self.seq += 1                                   # even: stable
        struct.pack_into("<I", self.mm, 4, self.seq)

    def close(self):
        self.mm.close()
        self.f.close()


class UdpWriter:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (host, port)

    def send(self, body):
        packet = struct.pack("<II", MAGIC, 0) + body
        self.sock.sendto(packet, self.addr)

    def close(self):
        self.sock.close()


def main():
    script_dir = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Stream a landmark CSV to Unity (shm or udp).")
    ap.add_argument("--csv", default=None,
                    help="Landmark CSV (default: newest *_landmarks_filtered.csv in ../mediapipe/output)")
    ap.add_argument("--transport", choices=["shm", "udp"], default="shm")
    ap.add_argument("--shm-path", default="/dev/shm/pose_stream")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=9750)
    ap.add_argument("--speed", type=float, default=1.0, help="Playback speed multiplier")
    ap.add_argument("--no-loop", action="store_true", help="Play once instead of looping")
    args = ap.parse_args()

    if args.csv:
        csv_path = Path(args.csv)
    else:
        out_dir = script_dir.parent / "mediapipe" / "output"
        candidates = sorted(out_dir.glob("*_landmarks_filtered.csv"), key=lambda p: p.stat().st_mtime)
        if not candidates:
            sys.exit(f"[ERROR] No *_landmarks_filtered.csv in {out_dir}")
        csv_path = candidates[-1]
    if not csv_path.exists():
        sys.exit(f"[ERROR] CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)
    times, packets = build_packets(df)
    writer = ShmWriter(args.shm_path) if args.transport == "shm" else UdpWriter(args.host, args.port)
    target = args.shm_path if args.transport == "shm" else f"{args.host}:{args.port}"
    print(f"[INFO] Streaming {csv_path.name} ({len(packets)} frames) via {args.transport} -> {target}")
    print("[INFO] Ctrl-C to stop")

    try:
        while True:
            t_start = time.perf_counter()
            for k, body in enumerate(packets):
                due = t_start + (times[k] - times[0]) / args.speed
                delay = due - time.perf_counter()
                if delay > 0:
                    time.sleep(delay)
                writer.send(body)
            if args.no_loop:
                break
            print("[INFO] Loop restart")
    except KeyboardInterrupt:
        print("\n[INFO] Stopped")
    finally:
        writer.close()

    print("[INFO] Done")


if __name__ == "__main__":
    main()

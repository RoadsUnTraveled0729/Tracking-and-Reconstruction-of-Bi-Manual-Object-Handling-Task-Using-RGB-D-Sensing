#!/usr/bin/env python3
# Filename: realtime/integration/realtime_integrate.py
"""Real-time merger: PSR1 (person) + PSB2 (object) -> PSB3 + PSI1.

The real-time counterpart of send_integrated_scene.py. Pipelines A and B
run as independent processes writing their own shm regions; this layer —
the only one allowed to read both — pairs the LATEST stable sample of each
and re-emits the existing Unity contract unchanged:

  /dev/shm/aruco_scene       PSB3 (100 B), written once from the frozen
                             scene calibration (write_scene, Pipeline B)
  /dev/shm/integrated_scene  PSI1 (108 B seqlock) per new person frame,
                             object = latest available sample (its live
                             flag preserved; a stale object > --stale-s
                             is demoted to live=0)

IntegratedSceneReceiver.cs needs no change. Real-time A/B desync is
inherent; the merger measures it (person-vs-object timestamp skew stats
reported at exit) instead of pretending it away.

Usage (normally via run_realtime.py):
  python realtime_integrate.py [--calib ../aruco/output/scene_calibration.json]
      [--person /dev/shm/rt_person] [--object /dev/shm/rt_object]
      [--out /dev/shm/integrated_scene] [--idle-timeout 5]
"""
import argparse
import mmap
import struct
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                 # repo root
sys.path.insert(0, str(ROOT / "aruco"))

PSR1_MAGIC = 0x31525350
PSR1_FMT = "<IIif3f13fH2x"
PSR1_SIZE = struct.calcsize(PSR1_FMT)

PSB2_MAGIC = 0x32425350
PSB2_FMT = "<IIif3f3fH2x"
PSB2_SIZE = struct.calcsize(PSB2_FMT)

PSI1_MAGIC = 0x31495350
PSI1_FMT = "<IIif3f13f3f3fHH"
PSI1_SIZE = struct.calcsize(PSI1_FMT)
assert PSI1_SIZE == 108


class SeqReader:
    """Seqlock reader: returns the unpacked packet or None if unstable."""

    def __init__(self, path, fmt, size, magic):
        self.fmt, self.size, self.magic = fmt, size, magic
        f = open(path, "rb")
        self.mm = mmap.mmap(f.fileno(), size, prot=mmap.PROT_READ)
        f.close()

    def read(self):
        for _ in range(4):
            s0 = struct.unpack_from("<I", self.mm, 4)[0]
            if s0 % 2:
                continue
            data = struct.unpack_from(self.fmt, self.mm, 0)
            s1 = struct.unpack_from("<I", self.mm, 4)[0]
            if s0 == s1 and data[0] == self.magic:
                return data
        return None


class PSI1Writer:
    def __init__(self, path):
        Path(path).write_bytes(b"\x00" * PSI1_SIZE)
        f = open(path, "r+b")
        self.mm = mmap.mmap(f.fileno(), PSI1_SIZE)
        f.close()
        self.seq = 0

    def write(self, frame, t, pelvis, angles13, opos, oeul, mask, olive):
        self.seq += 1
        self.mm[4:8] = struct.pack("<I", self.seq)
        self.mm[:] = struct.pack(PSI1_FMT, PSI1_MAGIC, self.seq, frame, t,
                                 *pelvis, *angles13, *opos, *oeul, mask, olive)
        self.seq += 1
        self.mm[4:8] = struct.pack("<I", self.seq)


def wait_for(path, timeout, what):
    t0 = time.monotonic()
    while not Path(path).exists():
        if time.monotonic() - t0 > timeout:
            sys.exit(f"[ERROR] {what} shm {path} never appeared")
        time.sleep(0.05)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calib", default=str(ROOT / "aruco/output/scene_calibration.json"))
    ap.add_argument("--person", default="/dev/shm/rt_person")
    ap.add_argument("--object", default="/dev/shm/rt_object")
    ap.add_argument("--out", default="/dev/shm/integrated_scene")
    ap.add_argument("--scene-out", default="/dev/shm/aruco_scene")
    ap.add_argument("--stale-s", type=float, default=0.5,
                    help="object sample older than this vs the person "
                         "sample is demoted to live=0")
    ap.add_argument("--idle-timeout", type=float, default=5.0,
                    help="exit after this many seconds without a new "
                         "person frame")
    ap.add_argument("--startup-timeout", type=float, default=30.0)
    args = ap.parse_args()

    # PSB3 once, from the frozen Pipeline B calibration
    import json
    from send_scene_poses import write_scene                  # Pipeline B
    calib = json.loads(Path(args.calib).read_text())
    write_scene(args.scene_out, calib)

    wait_for(args.person, args.startup_timeout, "person")
    wait_for(args.object, args.startup_timeout, "object")
    person = SeqReader(args.person, PSR1_FMT, PSR1_SIZE, PSR1_MAGIC)
    obj = SeqReader(args.object, PSB2_FMT, PSB2_SIZE, PSB2_MAGIC)
    out = PSI1Writer(args.out)

    last_frame = -1
    merged = 0
    skews = []
    obj_frames = set()
    t_last_new = time.monotonic()
    print(f"[info] merging {args.person} + {args.object} -> {args.out}")

    while True:
        p = person.read()
        now = time.monotonic()
        if p is not None:
            _, _, frame, t_p = p[0], p[1], p[2], p[3]
            if frame != last_frame:
                pelvis = p[4:7]
                angles = p[7:20]
                mask = p[20]
                o = obj.read()
                if o is not None:
                    o_frame, t_o = o[2], o[3]
                    opos, oeul, olive = o[4:7], o[7:10], o[10]
                    if abs(t_p - t_o) > args.stale_s:
                        olive = 0
                    skews.append(t_p - t_o)
                    obj_frames.add(o_frame)
                else:
                    opos, oeul, olive = (0.0,) * 3, (0.0,) * 3, 0
                out.write(frame, t_p, pelvis, angles, opos, oeul, mask, olive)
                last_frame = frame
                merged += 1
                t_last_new = now
        if now - t_last_new > args.idle_timeout:
            break
        time.sleep(0.002)

    print(f"[done] merged {merged} person frames, "
          f"{len(obj_frames)} distinct object frames seen")
    if skews:
        a = np.abs(np.asarray(skews)) * 1e3
        print(f"[skew] |person - object| time: p50 {np.percentile(a, 50):.1f} ms, "
              f"p95 {np.percentile(a, 95):.1f} ms, max {a.max():.1f} ms")


if __name__ == "__main__":
    main()

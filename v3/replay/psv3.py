"""PSV3: V3's person output packet for Unity (canonical spec + writer).

The Unity reader is Unity/Assets/Scripts/V3/V3PersonReceiver.cs --
change both files or neither. V3-only shared memory name (D-007): the
v1/v2 receivers never see /dev/shm/v3_person and the V3 receiver reads
nothing else.

Layout (little-endian, 172 bytes, seqlock on seq):

    0   u32 magic 'PSV3' (0x33565350)
    4   u32 seq        (even = stable, odd = writer mid-update)
    8   i32 frame index
    12  f32 time_s     (session clock)
    16  8 x f32[3]     landmark xyz, Unity frame, meters, order:
                       L_Shoulder R_Shoulder L_Elbow R_Elbow
                       L_Wrist R_Wrist L_Hip R_Hip
    112 13 x f32       angles deg, v1 PSA order (root xyz | R sh
                       y,z,tau | R elb ey,ez | L sh y,z,tau |
                       L elb ey,ez)
    164 7 x u8         per-group status, v1 live-mask bit order
                       (root, R_swing, R_twist, R_elbow, L_swing,
                       L_twist, L_elbow): 0 MEASURED, 1 ESTIMATED,
                       2 LOST
    171 u8 pad
"""
import mmap
import os
import struct

import numpy as np

MAGIC = 0x33565350
FMT = "<IIif24f13f7Bx"
SIZE = struct.calcsize(FMT)
assert SIZE == 172

LANDMARK_ORDER = ("left_shoulder", "right_shoulder", "left_elbow",
                  "right_elbow", "left_wrist", "right_wrist",
                  "left_hip", "right_hip")

DEFAULT_PATH = "/dev/shm/v3_person"


class PSV3Writer:
    def __init__(self, path=DEFAULT_PATH):
        self.path = path
        fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o644)
        os.ftruncate(fd, SIZE)
        self._mm = mmap.mmap(fd, SIZE)
        os.close(fd)
        self._seq = 0

    def write(self, frame, time_s, points, angles13, status7):
        """points: dict landmark-name -> xyz (Unity frame); missing or
        NaN landmarks are written as NaN (the reader shows the last
        finite position; statuses carry the honesty signal).
        angles13: (13,) deg; status7: (7,) ints in {0, 1, 2}."""
        flat = []
        for name in LANDMARK_ORDER:
            p = points.get(name)
            if p is None:
                flat += [float("nan")] * 3
            else:
                flat += [float(p[0]), float(p[1]), float(p[2])]
        angles13 = np.asarray(angles13, dtype=float)
        status7 = [int(v) for v in status7]
        if angles13.shape != (13,) or len(status7) != 7:
            raise ValueError("angles13 must be (13,), status7 length 7")
        if any(v not in (0, 1, 2) for v in status7):
            raise ValueError(f"bad status values: {status7}")

        self._seq += 1                      # odd: writer mid-update
        self._mm.seek(4)
        self._mm.write(struct.pack("<I", self._seq))
        payload = struct.pack(FMT, MAGIC, self._seq, int(frame),
                              float(time_s), *flat,
                              *[float(a) for a in angles13], *status7)
        self._seq += 1                      # even: stable
        payload = payload[:4] + struct.pack("<I", self._seq) + payload[8:]
        self._mm.seek(0)
        self._mm.write(payload)

    def close(self, unlink=False):
        self._mm.close()
        if unlink:
            try:
                os.unlink(self.path)
            except FileNotFoundError:
                pass

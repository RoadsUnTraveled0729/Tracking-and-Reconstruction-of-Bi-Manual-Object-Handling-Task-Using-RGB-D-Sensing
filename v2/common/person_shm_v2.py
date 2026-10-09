#!/usr/bin/env python3
# Filename: v2/common/person_shm_v2.py
"""PSR2: the PSR1 person packet with solver tags in the former pad.

Vendored from the frozen v1/realtime/person/realtime_person.py ShmWriter
(provenance: PSR1, 84 B, "<IIif3f13fH2x"); the only change is the magic
and the last two bytes:

  u32 'PSR2' | u32 seq | i32 frame | f32 time_s
  3f pelvis | 13f angles (PSA5 order)
  u16 live mask | u16 tags

tags: bits 2i..2i+1 hold the tag of live-mask group i (7 groups: root,
R swing, R twist, R elbow, L swing, L twist, L elbow), values from
occlusion_ext: 0 MEASURED, 1 HELD, 2 CONSTRAINED. Same size and offsets
as PSR1 through byte 81, so a reader switches on the magic alone.
"""
import mmap
import struct

PSR2_MAGIC = 0x32525350  # 'PSR2'
PSR2_FMT = "<IIif3f13fHH"
PSR2_SIZE = struct.calcsize(PSR2_FMT)
assert PSR2_SIZE == 84
N_GROUPS = 7


def pack_tags(tags):
    """7 group tags (0..2 each) -> u16, 2 bits per group."""
    v = 0
    for i, t in enumerate(tags):
        v |= (int(t) & 0x3) << (2 * i)
    return v


def unpack_tags(v):
    return [(int(v) >> (2 * i)) & 0x3 for i in range(N_GROUPS)]


class ShmWriterV2:
    def __init__(self, path):
        f = open(path, "w+b")
        f.truncate(PSR2_SIZE)
        self.mm = mmap.mmap(f.fileno(), PSR2_SIZE)
        f.close()
        self.seq = 0

    def write(self, frame, t, pelvis, angles13, mask, tags):
        self.seq += 1  # odd: writer busy
        self.mm[4:8] = struct.pack("<I", self.seq)
        self.mm[:PSR2_SIZE] = struct.pack(
            PSR2_FMT, PSR2_MAGIC, self.seq, int(frame), float(t),
            *[float(x) for x in pelvis], *[float(a) for a in angles13],
            int(mask), pack_tags(tags))
        self.seq += 1  # even: stable
        self.mm[4:8] = struct.pack("<I", self.seq)

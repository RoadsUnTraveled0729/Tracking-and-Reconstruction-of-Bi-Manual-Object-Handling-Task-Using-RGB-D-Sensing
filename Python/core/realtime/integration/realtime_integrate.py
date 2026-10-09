"""Shared-memory packet definitions and stable snapshot reader."""
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

"""Shared-memory writers for the calibrated scene and tracked object."""
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

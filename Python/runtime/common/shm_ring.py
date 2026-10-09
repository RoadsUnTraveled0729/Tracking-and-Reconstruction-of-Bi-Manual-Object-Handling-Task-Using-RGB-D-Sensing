#!/usr/bin/env python3
# Filename: runtime/common/shm_ring.py
"""PSF1 shared-memory frame ring: one writer (the capture broker), any
number of readers (Pipeline A, Pipeline B, live calibration).

This is transport infrastructure below the A/B independence boundary --
it replaces the bag file both v1 pipelines already shared, exactly as
/dev/shm and pyrealsense2 are shared (DECISIONS 2026-08-06).

Layout of /dev/shm/rt_frames (all little-endian, no implicit padding):

  header (HDR_SIZE = 128 bytes, zero-padded past the struct):
    u32 magic 'PSF1'   -- written LAST at init; readers wait for it
    u32 version (1)
    u32 nslots
    u32 slot_size
    i32 width, i32 height
    u32 color_format   -- int(rs.format), e.g. bgr8/rgb8
    f64 depth_scale    -- metres per depth unit
    f64 t0_hw_ms       -- hardware timestamp of frame 0 (set before it
                          is published); shared session clock is
                          time_s = (hw_ts_ms - t0_hw_ms) / 1000
    f32 fx, fy, ppx, ppy
    f32 coeffs[5]
    i32 distortion model (int(rs.distortion))
    u32 eof            -- 1 once the writer is done (bag ended / stopped)
    u32 counter        -- frames published so far; slot of publication c
                          is (c - 1) % nslots; bumped AFTER the slot commit

  per slot (slot_size = 32 + color_bytes + depth_bytes):
    u32 seq            -- per-slot seqlock: odd while writing, even stable
    i32 frame_idx      -- publication index (counter - 1 at commit time)
    u32 pad
    f64 hw_ts_ms       -- frames.get_timestamp() of this frame
    f64 mono_ts        -- time.monotonic() at receipt (merger clock map)
    u8  color[width*height*3]   -- as delivered (see color_format)
    u16 depth[width*height]     -- aligned to color, raw units

Readers COPY the payload out and re-check the slot seq (copy-then-verify,
never zero-copy views): a consumer may hold a frame for ~30 ms and must
not be lapped mid-use. Lap protection at 8 slots / 30 fps is ~266 ms.
"""
import mmap
import struct
import time
from pathlib import Path

import numpy as np

MAGIC = 0x31465350  # 'PSF1'
VERSION = 1

HDR_FMT = "<IIIIiiIdd4f5fiII"
HDR_SIZE = 128
assert struct.calcsize(HDR_FMT) <= HDR_SIZE

# offsets of the mutable header fields
_OFF_MAGIC = 0
_OFF_T0 = struct.calcsize("<IIIIiiId")            # after depth_scale
_OFF_EOF = struct.calcsize("<IIIIiiIdd4f5fi")
_OFF_COUNTER = _OFF_EOF + 4

SLOT_HDR_FMT = "<IiIdd"
SLOT_HDR_SIZE = 32
assert struct.calcsize(SLOT_HDR_FMT) <= SLOT_HDR_SIZE

DEFAULT_PATH = "/dev/shm/rt_frames"
DEFAULT_NSLOTS = 8


class FrameSample:
    """One copied-out frame. color: (h, w, 3) uint8 in the header's
    color_format; depth: (h, w) uint16 raw units, aligned to color."""

    __slots__ = ("frame_idx", "hw_ts_ms", "mono_ts", "color", "depth")

    def __init__(self, frame_idx, hw_ts_ms, mono_ts, color, depth):
        self.frame_idx = frame_idx
        self.hw_ts_ms = hw_ts_ms
        self.mono_ts = mono_ts
        self.color = color
        self.depth = depth


class FrameRingWriter:
    """The capture broker's side. Create with the stream geometry, then
    write() once per frame. Header magic is written last so readers can
    poll for a fully initialized ring."""

    def __init__(self, path, width, height, color_format, depth_scale,
                 intrinsics, nslots=DEFAULT_NSLOTS):
        self.path = Path(path)
        self.width, self.height = int(width), int(height)
        self.nslots = int(nslots)
        self.color_bytes = self.width * self.height * 3
        self.depth_px = self.width * self.height
        self.slot_size = SLOT_HDR_SIZE + self.color_bytes + 2 * self.depth_px
        total = HDR_SIZE + self.nslots * self.slot_size

        self.path.write_bytes(b"\x00" * total)
        self._f = open(self.path, "r+b")
        self.mm = mmap.mmap(self._f.fileno(), total)
        self.count = 0

        coeffs = list(intrinsics.coeffs)[:5] + [0.0] * (5 - len(intrinsics.coeffs))
        hdr = struct.pack(HDR_FMT, MAGIC, VERSION, self.nslots,
                          self.slot_size, self.width, self.height,
                          int(color_format), float(depth_scale), float("nan"),
                          float(intrinsics.fx), float(intrinsics.fy),
                          float(intrinsics.ppx), float(intrinsics.ppy),
                          *[float(c) for c in coeffs],
                          int(intrinsics.model), 0, 0)
        # body first, magic last: readers wait for a valid magic word
        self.mm[4:len(hdr)] = hdr[4:]
        self.mm[0:4] = hdr[0:4]

        self._color_views = []
        self._depth_views = []
        for s in range(self.nslots):
            off = HDR_SIZE + s * self.slot_size + SLOT_HDR_SIZE
            self._color_views.append(np.frombuffer(
                self.mm, np.uint8, self.color_bytes, offset=off))
            self._depth_views.append(np.frombuffer(
                self.mm, np.uint16, self.depth_px,
                offset=off + self.color_bytes))
        self._slot_seq = [0] * self.nslots

    def write(self, hw_ts_ms, mono_ts, color, depth):
        """Publish one frame. color (h, w, 3) uint8; depth (h, w) uint16.
        Returns the frame index just published."""
        if self.count == 0:
            struct.pack_into("<d", self.mm, _OFF_T0, float(hw_ts_ms))
        slot = self.count % self.nslots
        off = HDR_SIZE + slot * self.slot_size
        seq = self._slot_seq[slot] + 1                       # odd: writing
        struct.pack_into("<I", self.mm, off, seq)
        struct.pack_into(SLOT_HDR_FMT, self.mm, off, seq, self.count, 0,
                         float(hw_ts_ms), float(mono_ts))
        self._color_views[slot][:] = color.reshape(-1)
        self._depth_views[slot][:] = depth.reshape(-1)
        seq += 1                                             # even: stable
        struct.pack_into("<I", self.mm, off, seq)
        self._slot_seq[slot] = seq
        self.count += 1
        struct.pack_into("<I", self.mm, _OFF_COUNTER, self.count)
        return self.count - 1

    def close(self, eof=True):
        if eof:
            struct.pack_into("<I", self.mm, _OFF_EOF, 1)
        self.mm.flush()


class FrameRingReader:
    """A consumer's side. open() waits for the writer to initialize the
    header, then latest()/fetch() copy frames out."""

    def __init__(self, path=DEFAULT_PATH, wait_s=30.0):
        self.path = Path(path)
        t0 = time.monotonic()
        while True:
            if self.path.exists() and self.path.stat().st_size >= HDR_SIZE:
                f = open(self.path, "rb")
                head = f.read(4)
                if len(head) == 4 and struct.unpack("<I", head)[0] == MAGIC:
                    size = self.path.stat().st_size
                    self.mm = mmap.mmap(f.fileno(), size, prot=mmap.PROT_READ)
                    f.close()
                    break
                f.close()
            if time.monotonic() - t0 > wait_s:
                raise TimeoutError(
                    f"frame ring {self.path} not initialized after {wait_s} s")
            time.sleep(0.001)

        (magic, version, self.nslots, self.slot_size, self.width,
         self.height, cf, self.depth_scale, _t0, self.fx, self.fy,
         self.ppx, self.ppy, c0, c1, c2, c3, c4, self.distortion_model,
         _eof, _cnt) = struct.unpack_from(HDR_FMT, self.mm, 0)
        if version != VERSION:
            raise RuntimeError(f"frame ring version {version}, expected {VERSION}")
        self.color_format = cf
        self.coeffs = [c0, c1, c2, c3, c4]
        self.color_bytes = self.width * self.height * 3
        self.depth_px = self.width * self.height

    @property
    def t0_hw_ms(self):
        return struct.unpack_from("<d", self.mm, _OFF_T0)[0]

    @property
    def eof(self):
        return struct.unpack_from("<I", self.mm, _OFF_EOF)[0] == 1

    @property
    def counter(self):
        return struct.unpack_from("<I", self.mm, _OFF_COUNTER)[0]

    def intrinsics(self):
        """Rebuild an rs.intrinsics for rs2_deproject_pixel_to_point."""
        import pyrealsense2 as rs
        intr = rs.intrinsics()
        intr.width, intr.height = self.width, self.height
        intr.fx, intr.fy = self.fx, self.fy
        intr.ppx, intr.ppy = self.ppx, self.ppy
        intr.model = rs.distortion(self.distortion_model)
        intr.coeffs = self.coeffs
        return intr

    def peek(self, c):
        """Slot HEADER only, no payload copy: (frame_idx, hw_ts_ms,
        mono_ts) of publication c, or None if lapped/unstable. Used by
        the merger for its session-clock mapping."""
        slot = (c - 1) % self.nslots
        off = HDR_SIZE + slot * self.slot_size
        for _ in range(3):
            s0, frame_idx, _pad, hw_ts, mono_ts = struct.unpack_from(
                SLOT_HDR_FMT, self.mm, off)
            if s0 % 2:
                time.sleep(0.0002)
                continue
            s1 = struct.unpack_from("<I", self.mm, off)[0]
            if s1 != s0:
                continue
            if frame_idx != c - 1:
                return None
            return frame_idx, hw_ts, mono_ts
        return None

    def fetch(self, c):
        """Copy out publication c (1-based counter value). Returns a
        FrameSample, or None if that publication was lapped or is being
        overwritten right now."""
        slot = (c - 1) % self.nslots
        off = HDR_SIZE + slot * self.slot_size
        for _ in range(3):
            s0, frame_idx, _pad, hw_ts, mono_ts = struct.unpack_from(
                SLOT_HDR_FMT, self.mm, off)
            if s0 % 2:
                time.sleep(0.0002)
                continue
            a = off + SLOT_HDR_SIZE
            color_buf = self.mm[a:a + self.color_bytes]
            depth_buf = self.mm[a + self.color_bytes:
                                a + self.color_bytes + 2 * self.depth_px]
            s1 = struct.unpack_from("<I", self.mm, off)[0]
            if s1 != s0:
                time.sleep(0.0002)
                continue
            if frame_idx != c - 1:
                return None                                  # lapped
            color = np.frombuffer(color_buf, np.uint8).reshape(
                self.height, self.width, 3)
            depth = np.frombuffer(depth_buf, np.uint16).reshape(
                self.height, self.width)
            return FrameSample(frame_idx, hw_ts, mono_ts, color, depth)
        return None

    def latest(self, last_counter, timeout_s=5.0, poll_s=0.001):
        """Block until a publication NEWER than last_counter exists, then
        return (counter, FrameSample) for the newest one. Returns
        (last_counter, None) on writer EOF with nothing new, and raises
        TimeoutError if the writer goes silent without EOF."""
        t0 = time.monotonic()
        while True:
            c = self.counter
            if c > last_counter:
                sample = self.fetch(c)
                if sample is not None:
                    return c, sample
                # racing the writer on the newest slot: take the previous
                if c - 1 > last_counter:
                    sample = self.fetch(c - 1)
                    if sample is not None:
                        return c - 1, sample
            elif self.eof:
                return last_counter, None
            if time.monotonic() - t0 > timeout_s:
                raise TimeoutError("frame ring writer silent "
                                   f"(counter {c}, eof {self.eof})")
            time.sleep(poll_s)

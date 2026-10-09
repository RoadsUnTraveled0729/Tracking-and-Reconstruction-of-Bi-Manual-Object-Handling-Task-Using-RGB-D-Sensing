#!/usr/bin/env python3
# Filename: v2/integration/v2_integrate.py
"""v2 merger: PSR1 (person) + PSB2 (object) -> PSB3 + PSI2, through a
timestamp-paired delay buffer (thesis 8.3.1 + 8.3.3 in one mechanism).

v1's merger re-emitted the latest stable sample pair per person frame.
v2 instead renders on a steady 30 Hz output tick at a FIXED, DECLARED
delay behind capture:

  render time tau = session_now - delay_frames * (1/30 s)

where session time is the shared hardware-timestamp clock all packets
carry, mapped to this process's monotonic clock through the frame ring's
(hw_ts, mono_ts) pairs with a sliding rate estimate (absorbs bag
playback pacing stretch; rate is ~1 on a live camera).

Per stream at each tick, with the measured samples buffered in a deque:
  - tau within eps of a measured sample        -> emit it (MEASURED)
  - bracketed, gap <= max_gap_frames intervals -> interpolate (INTERP;
    the BRIDGE flag is additionally set when the bracket gap exceeds
    1.6 intervals, i.e. a real dropout was crossed, not routine
    resampling between adjacent frames)
  - no future sample yet, or gap too long      -> hold-last (HELD),
    exactly v1's semantics (object stale demotion kept)
  - first sample after a long gap              -> blend from the held
    pose to it over blend_frames ticks (BLEND) -- an honest ramp,
    never an invented trajectory across the occlusion

Interpolation representations:
  person: the 13 joint parameters + pelvis, componentwise and WRAP-AWARE
    (root y lives at the +-180 seam); interp mask = AND of bracket masks
  object: position lerp + rotation along the SO(3) geodesic
    (geodesic_interp from aruco/filter_object_track.py); only live
    measurements enter the buffer

Output packet PSI2 (112 B, /dev/shm/integrated_scene_v2), identical to
PSI1 through byte 103:

  u32 'PSI2' | u32 seq | i32 tick | f32 tau
  3f pelvis | 13f angles | 3f obj pos | 3f obj euler
  u16 mask (104) | u16 olive (106) | u16 flags (108) | u16 tags (110)
  flags: bit0 person interp   bit1 object interp
         bit2 person blend    bit3 object blend
         bit4 person bridge   bit5 object bridge
  tags (former pad; 0 when Pipeline A writes PSR1): bits 2i..2i+1 =
  solver tag of live-mask group i (0 MEASURED 1 HELD 2 CONSTRAINED),
  elementwise-max across interpolation brackets, floored to HELD on
  merger holds
  (layout duplicated by hand in IntegratedSceneReceiverV2.cs --
   change both or neither)

Unity applies numbers and never creates them: every displayed pose is
measured, between two measurements, held, or a flagged ramp -- and says
which.

Usage (normally via run_v2.py):
  python v2_integrate.py [--person /dev/shm/rt_person_v2]
      [--object /dev/shm/rt_object_v2] [--ring /dev/shm/rt_frames]
      [--out /dev/shm/integrated_scene_v2] [--calib ...]
      [--delay-frames 1] [--max-gap-frames 3] [--blend-frames 2]
      [--stale-s 0.5] [--dump-csv ...]
"""
import argparse
import mmap
import struct
import sys
import time
from collections import deque
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                 # repo root
sys.path.insert(0, str(ROOT / "v2/common"))
sys.path.insert(0, str(ROOT / "v1/realtime/integration"))

import realtime_integrate              # self-configures aruco/ path
from realtime_integrate import (PSB2_FMT, PSB2_MAGIC, PSB2_SIZE, PSR1_FMT,
                                PSR1_MAGIC, PSR1_SIZE, SeqReader, wait_for)
from person_shm_v2 import (PSR2_FMT, PSR2_MAGIC, PSR2_SIZE, N_GROUPS,
                           pack_tags, unpack_tags)

sys.path.insert(0, str(ROOT / "v1/kinematics"))
from root_frame import wrap_deg                        # +-180-seam lerp

from filter_object_track import geodesic_interp        # aruco (via v1 merger)
from frames import euler_unity_zxy, recompose_zxy
from shm_ring import FrameRingReader

PSI2_MAGIC = 0x32495350  # 'PSI2'
PSI2_FMT = "<IIif3f13f3f3fHHHH"
PSI2_SIZE = struct.calcsize(PSI2_FMT)
assert PSI2_SIZE == 112

FRAME_S = 1.0 / 30.0
MEASURED, INTERP, HELD, BLEND = 0, 1, 2, 3
STATE_NAMES = ("measured", "interp", "held", "blend")


class PSI2Writer:
    def __init__(self, path):
        Path(path).write_bytes(b"\x00" * PSI2_SIZE)
        f = open(path, "r+b")
        self.mm = mmap.mmap(f.fileno(), PSI2_SIZE)
        f.close()
        self.seq = 0

    def write(self, tick, tau, pelvis, angles13, opos, oeul, mask, olive,
              flags, tags=0):
        self.seq += 1
        self.mm[4:8] = struct.pack("<I", self.seq)
        self.mm[:] = struct.pack(PSI2_FMT, PSI2_MAGIC, self.seq, tick, tau,
                                 *pelvis, *angles13, *opos, *oeul,
                                 mask, olive, flags, tags)
        self.seq += 1
        self.mm[4:8] = struct.pack("<I", self.seq)


def lerp_angles(a0, a1, s):
    """Componentwise wrap-aware interpolation of joint parameters."""
    a0 = np.asarray(a0, float)
    a1 = np.asarray(a1, float)
    return wrap_deg(a0 + s * wrap_deg(a1 - a0))


def lerp_object(p0, e0, p1, e1, s):
    """Position lerp + SO(3) geodesic between two unity poses."""
    pos = (1.0 - s) * np.asarray(p0, float) + s * np.asarray(p1, float)
    R = geodesic_interp(recompose_zxy(e0), recompose_zxy(e1), s)
    return pos, euler_unity_zxy(R)


class StreamBuffer:
    """Measured samples of one stream + the emit state machine."""

    def __init__(self, max_gap_s, blend_frames, interp_fn, keep=150):
        self.buf = deque(maxlen=keep)   # (t, frame, payload...)
        self.max_gap_s = max_gap_s
        self.blend_frames = blend_frames
        self.interp = interp_fn         # (sample0, sample1, s) -> payload
        self.prev_emit = None           # payload emitted last tick
        self.prev_base_frame = None
        self.blend_left = 0
        self.blend_from = None

    def add(self, t, frame, payload):
        self.buf.append((t, frame, payload))

    def emit(self, tau, eps=0.003, bridge_thresh=1.6 * FRAME_S):
        """-> (state, payload, f0, f1, bridge) or None if buffer empty.
        payload conventions are the caller's; interp_fn does the math."""
        if not self.buf:
            return None
        s0 = s1 = None
        for entry in reversed(self.buf):
            if entry[0] <= tau:
                s0 = entry
                break
            s1 = entry
        if s0 is None:                       # tau before all history
            base, state, out = s1, HELD, s1[2]
            f0 = f1 = s1[1]
            bridge = False
        elif abs(tau - s0[0]) <= eps:
            base, state, out = s0, MEASURED, s0[2]
            f0 = f1 = s0[1]
            bridge = False
        elif s1 is not None and (s1[0] - s0[0]) <= self.max_gap_s:
            frac = (tau - s0[0]) / (s1[0] - s0[0])
            base, state = s0, INTERP
            out = self.interp(s0[2], s1[2], frac)
            f0, f1 = s0[1], s1[1]
            bridge = (s1[0] - s0[0]) > bridge_thresh
        else:                                # gap too long / no future yet
            base, state, out = s0, HELD, s0[2]
            f0 = f1 = s0[1]
            bridge = False

        # blend-on-reacquire: the base measurement jumped across a gap
        # longer than max_gap while we were holding
        if (self.prev_base_frame is not None
                and base[1] != self.prev_base_frame
                and state in (MEASURED, INTERP)
                and self.prev_emit is not None):
            prev_t = next((e[0] for e in self.buf
                           if e[1] == self.prev_base_frame), None)
            if prev_t is not None and (base[0] - prev_t) > self.max_gap_s:
                self.blend_left = self.blend_frames
                self.blend_from = self.prev_emit
        if self.blend_left > 0 and self.blend_from is not None:
            k = self.blend_frames - self.blend_left + 1
            out = self.interp(self.blend_from, out, k / self.blend_frames)
            state = BLEND
            self.blend_left -= 1

        self.prev_base_frame = base[1]
        self.prev_emit = out
        return state, out, f0, f1, bridge


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calib", default=str(ROOT / "v1/aruco/output/scene_calibration.json"))
    ap.add_argument("--person", default="/dev/shm/rt_person_v2")
    ap.add_argument("--object", default="/dev/shm/rt_object_v2")
    ap.add_argument("--ring", default="/dev/shm/rt_frames")
    ap.add_argument("--out", default="/dev/shm/integrated_scene_v2")
    ap.add_argument("--scene-out", default="/dev/shm/aruco_scene")
    ap.add_argument("--delay-frames", type=int, default=2,
                    help="fixed, declared output delay behind capture "
                         "(2 measured on the pinned recording: at 1, "
                         "about 7 percent of ticks miss their future "
                         "bracket because person availability lag "
                         "approaches the frame interval; at 2, none do)")
    ap.add_argument("--max-gap-frames", type=float, default=3.0,
                    help="longest bracket gap bridged by interpolation")
    ap.add_argument("--blend-frames", type=int, default=2,
                    help="ticks to ramp from a held pose to reacquisition")
    ap.add_argument("--stale-s", type=float, default=0.5,
                    help="held object older than this vs tau reports live=0")
    ap.add_argument("--idle-timeout", type=float, default=5.0)
    ap.add_argument("--startup-timeout", type=float, default=60.0)
    ap.add_argument("--dump-csv", default=None)
    ap.add_argument("--display-lpf", action="store_true",
                    help="E-018 display smoother on the PSI2 packet "
                         "(low-pass + rate cap; dump CSV stays raw)")
    ap.add_argument("--lpf-alpha", type=float, default=0.5)
    ap.add_argument("--lpf-max-step", type=float, default=8.0)
    args = ap.parse_args()

    delay_s = args.delay_frames * FRAME_S
    max_gap_s = (args.max_gap_frames + 0.5) * FRAME_S

    # PSB3 once, from the (frozen or live) Pipeline B calibration
    import json
    from send_scene_poses import write_scene               # Pipeline B
    calib = json.loads(Path(args.calib).read_text())
    write_scene(args.scene_out, calib)

    wait_for(args.person, args.startup_timeout, "person")
    wait_for(args.object, args.startup_timeout, "object")

    class PersonReader:
        """PSR1 or PSR2 by magic; PSR1 packets report all-MEASURED tags."""

        def __init__(self, path):
            self.v2 = SeqReader(path, PSR2_FMT, PSR2_SIZE, PSR2_MAGIC)
            self.v1 = SeqReader(path, PSR1_FMT, PSR1_SIZE, PSR1_MAGIC)

        def read(self):
            d = self.v2.read()
            if d is not None:
                return d                       # ..., mask, tags
            d = self.v1.read()
            if d is not None:
                return d + (0,)                # tags: all MEASURED
            return None

    person = PersonReader(args.person)
    obj = SeqReader(args.object, PSB2_FMT, PSB2_SIZE, PSB2_MAGIC)
    ring = FrameRingReader(args.ring, wait_s=args.startup_timeout)
    out = PSI2Writer(args.out)

    def person_interp(pl0, pl1, s):
        pel0, a0, m0, g0 = pl0
        pel1, a1, m1, g1 = pl1
        # tags: elementwise max = the more degraded bracket wins
        return ((1 - s) * np.asarray(pel0) + s * np.asarray(pel1),
                lerp_angles(a0, a1, s), m0 & m1,
                tuple(max(x, y) for x, y in zip(g0, g1)))

    def object_interp(pl0, pl1, s):
        pos, eul = lerp_object(pl0[0], pl0[1], pl1[0], pl1[1], s)
        return (pos, eul)

    pbuf = StreamBuffer(max_gap_s, args.blend_frames, person_interp)
    obuf = StreamBuffer(max_gap_s, args.blend_frames, object_interp)

    lpf = pel_lpf = None
    if args.display_lpf:
        from display_lpf import AngleLPF
        lpf = AngleLPF(args.lpf_alpha, args.lpf_max_step)
        pel_lpf = AngleLPF(args.lpf_alpha,
                           0.02 if args.lpf_max_step else 0.0)
        print(f"[info] display smoother on (alpha {args.lpf_alpha}, "
              f"cap {args.lpf_max_step} deg/tick, pelvis 0.02 m/tick)")

    # session-clock mapping from the ring: newest (t, mono) anchor plus a
    # sliding rate (session seconds per monotonic second)
    clock = deque(maxlen=30)
    ring_c = 0
    t0_hw = None

    last_p_frame = -1
    last_o_frame = -1
    obj_seen = deque(maxlen=60)          # (t, live) every packet, any live
    t_last_new = time.monotonic()
    next_tick = None
    prev_tau = None
    tick = 0
    emit_mono = []
    counts = {"person": dict.fromkeys(STATE_NAMES, 0),
              "object": dict.fromkeys(STATE_NAMES, 0)}
    bridges = {"person": 0, "object": 0}
    dump_rows = []
    print(f"[info] merging {args.person} + {args.object} -> {args.out} "
          f"(delay {args.delay_frames} frame(s) = {delay_s * 1e3:.1f} ms)")

    while True:
        now = time.monotonic()

        c = ring.counter
        while ring_c < c:
            ring_c += 1
            pk = ring.peek(ring_c)
            if pk is not None:
                if t0_hw is None:
                    t0_hw = ring.t0_hw_ms
                clock.append(((pk[1] - t0_hw) / 1000.0, pk[2]))

        p = person.read()
        if p is not None and p[2] != last_p_frame:
            last_p_frame = p[2]
            pbuf.add(p[3], p[2], (np.asarray(p[4:7]), np.asarray(p[7:20]),
                                  p[20], tuple(unpack_tags(p[21]))))
            t_last_new = now
        o = obj.read()
        if o is not None and o[2] != last_o_frame:
            last_o_frame = o[2]
            obj_seen.append((o[3], o[10]))
            if o[10] == 1:
                obuf.add(o[3], o[2], (np.asarray(o[4:7]),
                                      np.asarray(o[7:10])))

        if pbuf.buf and len(clock) >= 2 and next_tick is None:
            next_tick = now
        if next_tick is not None and now >= next_tick:
            t_new, m_new = clock[-1]
            t_old, m_old = clock[0]
            rate = ((t_new - t_old) / (m_new - m_old)
                    if m_new > m_old else 1.0)
            session_now = t_new + (now - m_new) * rate
            tau = session_now - delay_s
            if prev_tau is not None:
                tau = max(tau, prev_tau)     # output time never regresses
            prev_tau = tau

            pe = pbuf.emit(tau)
            oe = obuf.emit(tau)
            flags = 0
            if pe is not None:
                p_state, (pelvis, angles, mask, tags), pf0, pf1, \
                    p_bridge = pe
                if p_state == HELD:
                    # a merger-level hold is at best HELD, group-wise
                    tags = tuple(max(t, 1) for t in tags)
                if p_state == INTERP:
                    flags |= 1
                if p_state == BLEND:
                    flags |= 4
                if p_bridge:
                    flags |= 16
                    bridges["person"] += 1
                counts["person"][STATE_NAMES[p_state]] += 1
            else:
                # No person packet yet: hold the model's REST pose, not
                # all-zeros - the root rest yaw is 180 (occlusion.py
                # ROOT_REST_DEG), so zero angles face the rig backwards
                # and it snaps 180 deg when the person first appears.
                rest = np.zeros(13)
                rest[1] = 180.0
                p_state, pelvis, angles, mask = HELD, np.zeros(3), \
                    rest, 0
                tags = (1,) * N_GROUPS
                pf0 = pf1 = -1
            if oe is not None:
                o_state, (opos, oeul), of0, of1, o_bridge = oe
                if o_state == INTERP:
                    flags |= 2
                if o_state == BLEND:
                    flags |= 8
                if o_bridge:
                    flags |= 32
                    bridges["object"] += 1
                counts["object"][STATE_NAMES[o_state]] += 1
                if o_state in (MEASURED, INTERP, BLEND):
                    olive = 1
                else:
                    # held: v1's staleness rule, judged by the newest
                    # packet AT OR BEFORE tau -- a reacquisition packet
                    # render time has not reached yet must not claim live
                    olive = 0
                    for t_lo, live_lo in reversed(obj_seen):
                        if t_lo <= tau:
                            if abs(tau - t_lo) <= args.stale_s:
                                olive = int(live_lo)
                            break
            else:
                o_state, opos, oeul, olive = HELD, np.zeros(3), np.zeros(3), 0
                of0 = of1 = -1

            if lpf is not None:
                # E-018 display smoother: PSI2 packet only; the dump
                # below stays unfiltered (analysis surface)
                disp_pelvis = pel_lpf(pelvis)
                disp_angles = lpf(angles)
            else:
                disp_pelvis, disp_angles = pelvis, angles
            out.write(tick, tau, disp_pelvis, disp_angles, opos, oeul,
                      int(mask), olive, flags, pack_tags(tags))
            emit_mono.append(now)
            if args.dump_csv:
                dump_rows.append([tick, f"{now:.6f}", f"{tau:.6f}",
                                  p_state, pf0, pf1, o_state, of0, of1,
                                  *[f"{v:.6f}" for v in pelvis],
                                  *[f"{v:.6f}" for v in angles],
                                  int(mask),
                                  *[f"{v:.6f}" for v in opos],
                                  *[f"{v:.6f}" for v in oeul],
                                  olive, flags, pack_tags(tags)])
            tick += 1
            next_tick += FRAME_S
            if now - next_tick > 1.0:        # fell far behind: resync
                next_tick = now

        if now - t_last_new > args.idle_timeout:
            break
        if ring.eof and pbuf.buf and prev_tau is not None \
                and prev_tau >= pbuf.buf[-1][0] + 2 * FRAME_S:
            break                            # source done, buffer drained
        time.sleep(0.002)

    print(f"[done] {tick} output ticks")
    for stream in ("person", "object"):
        c = counts[stream]
        print(f"[{stream}] " + "  ".join(f"{k} {v}" for k, v in c.items())
              + f"  bridge {bridges[stream]}")
    if len(emit_mono) > 2:
        iv = np.diff(np.asarray(emit_mono)) * 1e3
        print(f"[cadence] tick interval ms: p50 {np.percentile(iv, 50):.2f}  "
              f"p95 {np.percentile(iv, 95):.2f}  "
              f"p99 {np.percentile(iv, 99):.2f}  max {iv.max():.2f}")
    if len(clock) >= 2:
        t_new, m_new = clock[-1]
        t_old, m_old = clock[0]
        print(f"[clock] final session rate {((t_new - t_old) / (m_new - m_old)):.4f} "
              f"session s per wall s")

    if args.dump_csv:
        import csv as csvmod
        outp = Path(args.dump_csv)
        outp.parent.mkdir(exist_ok=True)
        cols = (["tick", "mono", "tau", "p_state", "p_f0", "p_f1",
                 "o_state", "o_f0", "o_f1", "pel_x", "pel_y", "pel_z"]
                + [f"a{i}" for i in range(13)]
                + ["mask", "ox", "oy", "oz", "oex", "oey", "oez",
                   "olive", "flags", "tags"])
        with open(outp, "w", newline="") as f:
            w = csvmod.writer(f)
            w.writerow(cols)
            w.writerows(dump_rows)
        print(f"[csv] {outp}")


if __name__ == "__main__":
    main()

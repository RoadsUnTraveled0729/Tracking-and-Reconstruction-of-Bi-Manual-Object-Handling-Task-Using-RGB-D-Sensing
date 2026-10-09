#!/usr/bin/env python3
"""Transport benchmark: TCP vs UDP vs shared memory on one host.

Defence Q&A support (presentation/defense_2026, pages 38-40). Two
processes (multiprocessing, spawn), one writer and one reader, move
fixed-size messages over three transports:

  tcp  loopback TCP, TCP_NODELAY on both ends, u32 length prefix
  udp  loopback UDP datagrams; payloads above UDP_CHUNK bytes are split
       into UDP_CHUNK-byte chunks with an 8-byte header (message index
       u32, chunk index u16, chunk count u16) and reassembled
  shm  mmap over a /dev/shm/bench_transport_* file with the PSV3
       seqlock layout (v3/replay/psv3.py): u32 magic at 0, u32 seq at 4
       (odd = writer mid-update, even = stable), payload after it. The
       reader busy-waits on the seq word, copies the record out and
       re-checks the seq (copy-then-verify, as the Unity reader
       V3PersonReceiver.cs ReadStable does).
  shm_sleep1ms  sensitivity variant of shm (paced regime only): the
       reader sleeps 1 ms between polls, the default poll_s of the
       repository's Python ring reader (v2/common/shm_ring.py latest()).

Every message has the same 24-byte header in all transports:
  0 u32 magic, 4 u32 seq, 8 i32 message index (-1 = end), 12 u32 pad,
  16 i64 t_send_ns (time.perf_counter_ns taken by the writer
  immediately before the send / publish), followed by filler bytes up
  to the message size (172 B or 1,536,032 B).

Regimes:
  paced  30 Hz, N_WARM warm-up + N_MEAS measured messages; one-way
         latency per message (reader clock on completion minus writer
         stamp; CLOCK_MONOTONIC is shared on one host) and reader-side
         inter-arrival jitter (p99 minus p50).
  thru   unpaced for THRU_S seconds after N_WARM warm-up messages;
         delivered messages per second and MB/s at the reader, writer
         send rate, UDP loss from sequence gaps, shm skipped messages
         (latest-value mailbox: an overwritten record is never seen).

Package condition (round 5, --package): per 30 Hz tick the writer moves
one whole per-frame package, the 172 B record plus one 1,536,032 B frame
slot; timed from write start to read complete of both parts
(time.monotonic_ns); 200 warm-up + 1000 measured packages per transport.

Usage:
  python transport_bench.py                 # 2 runs + charts (about 25 min)
  python transport_bench.py --charts-only   # re-render charts from results.csv
  python transport_bench.py --quick --out DIR   # smoke test, small counts
  python transport_bench.py --package       # package condition, 2 runs + chart
  python transport_bench.py --package-chart-only

Temporary files: /dev/shm/bench_transport_<pid>_* only, removed at exit
(normal exit, exception, SIGINT, SIGTERM).
"""
import argparse
import atexit
import csv
import gc
import glob
import json
import math
import mmap
import multiprocessing as mp
import os
import platform
import signal
import socket
import struct
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- constants (sources in DECISIONS.md D-149 to D-159) ----------------------
SIZES = (172, 1536032)          # PSV3 record (v3/replay/psv3.py SIZE);
                                # PSF1 slot (v2/common/shm_ring.py, 8 x
                                # 1,536,032 B ring)
N_WARM = 200                    # brief
N_MEAS = 2000                   # brief
RATE_HZ = 30.0                  # brief; PSV3 writer ~30 fps
THRU_S = 5.0                    # brief
UDP_CHUNK = 60000               # brief "60 KB"; < 65,507 B UDP limit
PACE_SPIN_NS = 2_000_000        # writer sleeps until 2 ms before the
                                # slot, then spins (pacing precision)
SHM_SLEEP_S = 0.001             # v2/common/shm_ring.py latest() poll_s
WRITER_CPU, READER_CPU, PARENT_CPU = 8, 10, 12  # distinct physical
                                # cores (sysfs thread_siblings_list:
                                # 8,24 / 10,26 / 12,28); CPU 2 avoided,
                                # another benchmark was pinned there
SHM_PREFIX = "/dev/shm/bench_transport_"
MAGIC = 0x48435442              # 'BTCH'
END_IDX = -1
UDP_END = 0xFFFFFFFF

HDR = struct.Struct("<IIiIq")   # magic, seq, idx, pad, t_send_ns
assert HDR.size == 24
IDX_TS = struct.Struct("<iIq")  # at offset 8: idx, pad, t_send_ns
U32 = struct.Struct("<I")
UDP_HDR = struct.Struct("<IHH")  # message index, chunk index, count

TRANSPORTS_MAIN = ("tcp", "udp", "shm")
LABEL = {"tcp": "TCP", "udp": "UDP", "shm": "Shared memory",
         "shm_sleep1ms": "Shared memory (1 ms sleep poll)"}
COLOR = {"tcp": "#A8A8A8", "udp": "#FFD088", "shm": "#70B7E6"}

# conceptual, not measured: user-space copies of the payload per message
# in this implementation, and kernel entries (system calls) per message
COPIES = {"tcp": "2 (writer user->kernel, kernel->reader user)",
          "udp": "3 (user->kernel, kernel->user, reassembly copy)",
          "shm": "2 (writer->mapping, mapping->reader copy-out)",
          "shm_sleep1ms": "2 (writer->mapping, mapping->reader copy-out)"}
COPIES_N = {"tcp": 2, "udp": 3, "shm": 2, "shm_sleep1ms": 2}


def n_chunks(size):
    return max(1, math.ceil(size / UDP_CHUNK))


def kernel_calls(transport, size):
    """Conceptual minimum system calls per message (writer + reader)."""
    if transport == "tcp":
        return "2 (1 send + >=1 recv)"
    if transport == "udp":
        n = n_chunks(size)
        return f"{2 * n} ({n} send + {n} recv)"
    return "0 (reader sleeps via nanosleep)" if transport == "shm_sleep1ms" \
        else "0"


def pin(cpu):
    """Pin the calling process to one CPU. Returns (method, affinity)."""
    try:
        import psutil
        p = psutil.Process()
        p.cpu_affinity([cpu])
        return "psutil", list(p.cpu_affinity())
    except ImportError:
        pass
    if hasattr(os, "sched_setaffinity"):
        os.sched_setaffinity(0, {cpu})
        return "os.sched_setaffinity", sorted(os.sched_getaffinity(0))
    return "none (no psutil, no sched_setaffinity)", []


def make_message(size):
    buf = bytearray(size)
    rng = np.random.default_rng(0)
    buf[HDR.size:] = rng.integers(0, 256, size - HDR.size,
                                  dtype=np.uint8).tobytes()
    HDR.pack_into(buf, 0, MAGIC, 0, 0, 0, 0)
    return buf


# ---------------------------------------------------------------- writer
def writer_main(cfg, port, out_q):
    gc.disable()
    method, aff = pin(cfg["writer_cpu"])
    transport, size, regime = cfg["transport"], cfg["size"], cfg["regime"]
    pc = time.perf_counter_ns
    pack_idx = IDX_TS.pack_into

    if transport == "tcp":
        sock = socket.create_connection(("127.0.0.1", port))
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        buf = bytearray(4) + make_message(size)
        U32.pack_into(buf, 0, size)
        sendall = sock.sendall

        def send(k):
            t = pc()
            pack_idx(buf, 12, k, 0, t)
            sendall(buf)

        def finish():
            pack_idx(buf, 12, END_IDX, 0, 0)
            sendall(buf)
            sock.shutdown(socket.SHUT_WR)
            sock.close()

    elif transport == "udp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("127.0.0.1", port))
        msg = make_message(size)
        mv = memoryview(msg)
        nch = n_chunks(size)
        hdrs = [bytearray(UDP_HDR.size) for _ in range(nch)]
        parts = [mv[c * UDP_CHUNK:(c + 1) * UDP_CHUNK] for c in range(nch)]
        sendmsg = sock.sendmsg
        pack_u = UDP_HDR.pack_into

        def send(k):
            t = pc()
            pack_idx(msg, 8, k, 0, t)
            for c in range(nch):
                h = hdrs[c]
                pack_u(h, 0, k, c, nch)
                sendmsg([h, parts[c]])

        def finish():
            end = UDP_HDR.pack(UDP_END, 0, 1)
            for _ in range(10):
                try:
                    sock.send(end)
                except ConnectionRefusedError:
                    break
                time.sleep(0.02)
            sock.close()

    else:  # shm, shm_sleep1ms
        fd = os.open(cfg["shm_path"], os.O_RDWR)
        mm = mmap.mmap(fd, size)
        os.close(fd)
        mmv = memoryview(mm)
        msg = make_message(size)
        mv = memoryview(msg)
        mmv[0:4] = mv[0:4]                  # magic
        seq = [U32.unpack_from(mm, 4)[0] & ~1]
        pack_u32 = U32.pack
        body_src = mv[8:size]

        # The seq word is stored as one 4-byte slice copy of pre-packed
        # bytes (as psv3.py does with mm.write(struct.pack(...))), NOT
        # with struct.pack_into on the mapping: CPython's pack_into
        # zero-fills the target bytes before packing, so a concurrent
        # reader can observe seq == 0 for a moment (found in this
        # benchmark's first full run; see DECISIONS.md D-154).
        def send(k):
            t = pc()
            pack_idx(msg, 8, k, 0, t)       # local buffer, not the mapping
            s = seq[0] + 1
            mmv[4:8] = pack_u32(s)          # odd: writer mid-update
            mmv[8:size] = body_src          # payload
            mmv[4:8] = pack_u32(s + 1)      # even: stable, AFTER payload
            seq[0] = s + 1

        def finish():
            send(END_IDX)
            for v in (body_src, mv, mmv):
                v.release()
            mm.close()

    stats = {"writer_pin_method": method, "writer_affinity": aff}
    if regime == "paced":
        period = int(round(1e9 / RATE_HZ))
        t0 = pc() + 50_000_000
        n_total = cfg["n_warm"] + cfg["n_meas"]
        for k in range(n_total):
            target = t0 + k * period
            rem = target - pc() - PACE_SPIN_NS
            if rem > 0:
                time.sleep(rem / 1e9)
            while pc() < target:
                pass
            send(k)
        stats["n_sent"] = n_total
        # END one period later so the last measured record is not
        # overwritten in the shm mailbox before the reader copies it
        target = t0 + n_total * period
        rem = target - pc() - PACE_SPIN_NS
        if rem > 0:
            time.sleep(rem / 1e9)
    else:
        for k in range(cfg["n_warm"]):
            send(k)
        k = cfg["n_warm"]
        t_start = pc()
        t_end = t_start + int(cfg["thru_s"] * 1e9)
        while pc() < t_end:
            send(k)
            k += 1
        t_stop = pc()
        stats["n_sent_meas"] = k - cfg["n_warm"]
        stats["writer_window_s"] = (t_stop - t_start) / 1e9
    finish()
    out_q.put(("writer", stats))


# ---------------------------------------------------------------- reader
class Recorder:
    """Paced: per-index send/recv stamps. Thru: counters only."""

    def __init__(self, regime, n_warm, n_meas):
        self.paced = regime == "paced"
        self.n_warm = n_warm
        self.count = 0
        self.t_first = 0
        self.t_last = 0
        self.last_idx = -1
        self.duplicates = 0
        if self.paced:
            n = n_warm + n_meas
            self.ts = np.full(n, -1, np.int64)
            self.tr = np.full(n, -1, np.int64)

    def record(self, idx, ts, tr):
        # first reception only: a re-read of an already delivered
        # message is counted as a duplicate and never overwrites stamps
        if idx <= self.last_idx:
            self.duplicates += 1
            return
        self.last_idx = idx
        if self.paced:
            if 0 <= idx < len(self.tr):
                self.ts[idx] = ts
                self.tr[idx] = tr
        elif idx >= self.n_warm:
            if self.count == 0:
                self.t_first = tr
            self.t_last = tr
            self.count += 1


def reader_main(cfg, ready, port_val, out_q):
    gc.disable()
    method, aff = pin(cfg["reader_cpu"])
    transport, size, regime = cfg["transport"], cfg["size"], cfg["regime"]
    rec = Recorder(regime, cfg["n_warm"], cfg["n_meas"])
    record = rec.record
    pc = time.perf_counter_ns
    unpack_idx = IDX_TS.unpack_from
    extra = {}
    deadline = time.monotonic() + cfg["timeout_s"]

    if transport == "tcp":
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        port_val.value = srv.getsockname()[1]
        ready.set()
        srv.settimeout(cfg["timeout_s"])
        conn, _ = srv.accept()
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        conn.settimeout(cfg["timeout_s"])
        cap = max(4 * 1024 * 1024, 3 * (size + 4))
        buf = bytearray(cap)
        mv = memoryview(buf)
        recv_into = conn.recv_into
        start = end = 0
        done = False
        while not done:
            r = recv_into(mv[end:], cap - end)
            tr = pc()                       # completion clock
            if r == 0:
                break
            end += r
            while end - start >= 4:
                n = U32.unpack_from(buf, start)[0]
                if end - start < 4 + n:
                    break
                idx, _, ts = unpack_idx(buf, start + 12)
                start += 4 + n
                if idx == END_IDX:
                    done = True
                    break
                record(idx, ts, tr)
            if start == end:
                start = end = 0
            elif cap - end < size + 4:
                tail = bytes(mv[start:end])
                buf[:len(tail)] = tail
                end -= start
                start = 0
        mv.release()
        conn.close()
        srv.close()

    elif transport == "udp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("127.0.0.1", 0))
        extra["udp_rcvbuf"] = sock.getsockopt(socket.SOL_SOCKET,
                                              socket.SO_RCVBUF)
        port_val.value = sock.getsockname()[1]
        sock.settimeout(cfg["timeout_s"])
        ready.set()
        chunk = bytearray(65536)
        cmv = memoryview(chunk)
        msg = bytearray(size)
        mmv = memoryview(msg)
        unpack_u = UDP_HDR.unpack_from
        recv_into = sock.recv_into
        hs = UDP_HDR.size
        cur = -1
        got = 0
        seen = 0
        partial_drops = 0
        while True:
            try:
                n = recv_into(chunk)
            except socket.timeout:
                extra["udp_end_timeout"] = True
                break
            idx, c, nch = unpack_u(chunk, 0)
            if idx == UDP_END:
                break
            if idx != cur:
                if idx < cur:
                    continue                # stale chunk of a lost message
                if got:
                    partial_drops += 1
                cur, got, seen = idx, 0, 0
            bit = 1 << c
            if seen & bit:
                continue
            seen |= bit
            off = c * UDP_CHUNK
            mmv[off:off + n - hs] = cmv[hs:n]
            got += 1
            if got == nch:
                tr = pc()                   # completion clock
                _, _, ts = unpack_idx(msg, 8)
                record(idx, ts, tr)
                got = 0
                seen = 0
        extra["udp_partial_messages_dropped"] = partial_drops
        cmv.release()
        mmv.release()
        sock.close()

    else:  # shm, shm_sleep1ms
        sleep_s = SHM_SLEEP_S if transport == "shm_sleep1ms" else 0.0
        fd = os.open(cfg["shm_path"], os.O_RDONLY)
        mm = mmap.mmap(fd, size, access=mmap.ACCESS_READ)
        os.close(fd)
        smv = memoryview(mm)
        dst = bytearray(size)
        dmv = memoryview(dst)
        u32 = U32.unpack_from
        seqw = U32.unpack               # seq read as one 4-byte snapshot
        last = seqw(mm[4:8])[0]
        retries = 0
        spins = 0
        sleep = time.sleep
        ready.set()
        while True:
            s1 = seqw(mm[4:8])[0]
            if s1 == last or (s1 & 1):
                if sleep_s:
                    sleep(sleep_s)
                spins += 1
                if (spins & 0xFFFFF) == 0 and time.monotonic() > deadline:
                    extra["shm_timeout"] = True
                    break
                continue
            dmv[:] = smv[:size]             # copy out
            s2 = seqw(mm[4:8])[0]
            if s2 != s1 or u32(dst, 4)[0] != s1:
                retries += 1                # torn: writer overlapped
                continue
            tr = pc()                       # completion clock
            last = s1
            idx, _, ts = unpack_idx(dst, 8)
            if idx == END_IDX:
                break
            record(idx, ts, tr)
        extra["shm_torn_retries"] = retries
        extra["shm_poll"] = ("sleep %.3f s" % sleep_s) if sleep_s \
            else "busy-wait"
        smv.release()
        dmv.release()
        mm.close()

    res = {"reader_pin_method": method, "reader_affinity": aff,
           "count": rec.count, "t_first": rec.t_first,
           "t_last": rec.t_last, "duplicates": rec.duplicates}
    if rec.paced:
        res["ts"] = rec.ts
        res["tr"] = rec.tr
    res.update(extra)
    out_q.put(("reader", res))


# ---------------------------------------------------------------- parent
_CLEANUP_PATHS = set()
_CHILDREN = []


def _cleanup():
    for p in _CHILDREN:
        try:
            if p.is_alive():
                p.terminate()
                p.join(2)
        except Exception:
            pass
    for path in list(_CLEANUP_PATHS) + glob.glob(
            f"{SHM_PREFIX}{os.getpid()}_*"):
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass
        _CLEANUP_PATHS.discard(path)


def _on_signal(signum, _frame):
    raise SystemExit(128 + signum)


def run_condition(ctx, transport, size, regime, counts):
    cfg = {"transport": transport, "size": size, "regime": regime,
           "n_warm": counts["n_warm"], "n_meas": counts["n_meas"],
           "thru_s": counts["thru_s"], "writer_cpu": WRITER_CPU,
           "reader_cpu": READER_CPU, "shm_path": None}
    paced_s = (counts["n_warm"] + counts["n_meas"]) / RATE_HZ
    cfg["timeout_s"] = paced_s + counts["thru_s"] + 60.0
    if transport.startswith("shm"):
        path = f"{SHM_PREFIX}{os.getpid()}_{transport}_{size}_{regime}"
        _CLEANUP_PATHS.add(path)
        fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
        os.ftruncate(fd, size)
        os.close(fd)
        cfg["shm_path"] = path
    q = ctx.Queue()
    ready = ctx.Event()
    port = ctx.Value("i", 0)
    r = ctx.Process(target=reader_main, args=(cfg, ready, port, q))
    _CHILDREN.append(r)
    r.start()
    if not ready.wait(30):
        raise RuntimeError(f"reader not ready: {transport} {size} {regime}")
    w = ctx.Process(target=writer_main, args=(cfg, port.value, q))
    _CHILDREN.append(w)
    w.start()
    got = {}
    t_wall0 = time.monotonic()
    while len(got) < 2:
        kind, payload = q.get(timeout=cfg["timeout_s"] + 30)
        got[kind] = payload
    for p in (w, r):
        p.join(10)
        if p.is_alive():
            p.terminate()
            p.join(2)
        _CHILDREN.remove(p)
    if cfg["shm_path"]:
        os.unlink(cfg["shm_path"])
        _CLEANUP_PATHS.discard(cfg["shm_path"])
    got["wall_s"] = time.monotonic() - t_wall0
    return got


def pct(a, q):
    return float(np.percentile(a, q)) if len(a) else float("nan")


def summarise(run, transport, size, regime, got, counts, raw_dir):
    w, r = got["writer"], got["reader"]
    row = {"run": run, "transport": transport, "size_bytes": size,
           "regime": regime, "reader_poll": "",
           "copies_per_msg_conceptual": COPIES_N[transport],
           "kernel_calls_per_msg_conceptual": kernel_calls(transport, size)}
    if transport.startswith("shm"):
        row["reader_poll"] = r.get("shm_poll", "")
    else:
        row["reader_poll"] = "blocking recv"
    for k in ("n", "p50_us", "p90_us", "p99_us", "max_us", "ia_p50_ms",
              "jitter_ms", "send_jitter_ms", "writer_msgs_per_s",
              "msgs_per_s", "MB_per_s", "loss_pct", "skipped_pct",
              "torn_retries"):
        row[k] = ""
    row["torn_retries"] = r.get("shm_torn_retries", "")
    row["duplicates"] = r.get("duplicates", 0)
    n_warm, n_meas = counts["n_warm"], counts["n_meas"]
    if regime == "paced":
        ts, tr = r["ts"], r["tr"]
        idx = np.arange(len(tr))
        m = (idx >= n_warm) & (tr >= 0)
        lat_us = (tr[m] - ts[m]) / 1000.0
        row["n"] = int(m.sum())
        row["p50_us"] = pct(lat_us, 50)
        row["p90_us"] = pct(lat_us, 90)
        row["p99_us"] = pct(lat_us, 99)
        row["max_us"] = float(lat_us.max()) if len(lat_us) else ""
        # inter-arrival over consecutive measured indices both received
        mi = idx[n_warm:]
        a = tr[n_warm:]
        ok = (a[1:] >= 0) & (a[:-1] >= 0)
        ia_ms = (a[1:] - a[:-1])[ok] / 1e6
        row["ia_p50_ms"] = pct(ia_ms, 50)
        row["jitter_ms"] = pct(ia_ms, 99) - pct(ia_ms, 50)
        s = ts[n_warm:]
        oks = (s[1:] >= 0) & (s[:-1] >= 0)
        sia = (s[1:] - s[:-1])[oks] / 1e6
        row["send_jitter_ms"] = pct(sia, 99) - pct(sia, 50)
        missing = n_meas - row["n"]
        lossv = 100.0 * missing / n_meas
        if transport.startswith("shm"):
            row["skipped_pct"] = lossv
            row["loss_pct"] = 0.0
        else:
            row["loss_pct"] = lossv
            row["skipped_pct"] = 0.0
        os.makedirs(raw_dir, exist_ok=True)
        fn = os.path.join(raw_dir, f"{transport}_{size}B_paced.csv")
        with open(fn, "w", newline="") as f:
            wr = csv.writer(f, lineterminator="\n")
            wr.writerow(["index", "t_send_ns", "t_recv_ns", "latency_us"])
            for i in mi:
                if tr[i] >= 0:
                    wr.writerow([int(i), int(ts[i]), int(tr[i]),
                                 "%.3f" % ((tr[i] - ts[i]) / 1000.0)])
                else:
                    wr.writerow([int(i), "", "", ""])
        del mi
    else:
        n_sent = w["n_sent_meas"]
        cnt = r["count"]
        row["n"] = cnt
        row["writer_msgs_per_s"] = n_sent / w["writer_window_s"]
        if cnt > 1:
            rate = (cnt - 1) / ((r["t_last"] - r["t_first"]) / 1e9)
        else:
            rate = 0.0
        row["msgs_per_s"] = rate
        row["MB_per_s"] = rate * size / 1e6
        lossv = 100.0 * (n_sent - cnt) / n_sent if n_sent else float("nan")
        if transport.startswith("shm"):
            row["skipped_pct"] = lossv
            row["loss_pct"] = 0.0
        else:
            row["loss_pct"] = lossv
            row["skipped_pct"] = 0.0
    meta = {k: v for k, v in r.items() if k not in ("ts", "tr")}
    meta.update(w)
    meta["wall_s"] = got["wall_s"]
    return row, meta


CSV_COLS = ["run", "transport", "size_bytes", "regime", "n", "p50_us",
            "p90_us", "p99_us", "max_us", "ia_p50_ms", "jitter_ms",
            "send_jitter_ms", "writer_msgs_per_s", "msgs_per_s", "MB_per_s",
            "loss_pct", "skipped_pct", "torn_retries", "duplicates",
            "copies_per_msg_conceptual", "kernel_calls_per_msg_conceptual",
            "reader_poll"]


def fmt(v):
    if isinstance(v, float):
        if math.isnan(v):
            return ""
        return "%.4f" % v if abs(v) < 100 else "%.1f" % v
    return v


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=CSV_COLS, lineterminator="\n")
        wr.writeheader()
        for r in rows:
            wr.writerow({k: fmt(r[k]) for k in CSV_COLS})


def conditions():
    out = []
    for regime in ("paced", "thru"):
        for size in SIZES:
            for t in TRANSPORTS_MAIN:
                out.append((t, size, regime))
            if regime == "paced":
                out.append(("shm_sleep1ms", size, regime))
    return out


def environment(counts, pin_parent):
    env = {"date_local": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
           "host_cpu_model": "", "kernel": platform.release(),
           "platform": platform.platform(),
           "python": sys.version.split()[0],
           "python_executable": sys.executable,
           "numpy": np.__version__,
           "logical_cpus": os.cpu_count(),
           "start_method": "spawn",
           "writer_cpu": WRITER_CPU, "reader_cpu": READER_CPU,
           "parent_cpu": PARENT_CPU,
           "parent_pin": pin_parent,
           "counts": counts, "rate_hz": RATE_HZ, "udp_chunk": UDP_CHUNK,
           "pace_spin_ns": PACE_SPIN_NS,
           "shm_poll_main": "busy-wait on the seq word (no sleep)",
           "shm_poll_sensitivity": f"sleep {SHM_SLEEP_S} s between polls",
           "socket_readers": "blocking recv (kernel wake-up)"}
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    env["host_cpu_model"] = line.split(":", 1)[1].strip()
                    break
    except OSError:
        pass
    sib = {}
    for c in (WRITER_CPU, READER_CPU, PARENT_CPU):
        p = f"/sys/devices/system/cpu/cpu{c}/topology/thread_siblings_list"
        try:
            with open(p) as f:
                sib[str(c)] = f.read().strip()
        except OSError:
            sib[str(c)] = "unknown"
    env["thread_siblings"] = sib
    env["writer_reader_different_physical_cores"] = (
        sib.get(str(WRITER_CPU)) != sib.get(str(READER_CPU)))
    for k in ("rmem_default", "rmem_max", "wmem_default", "wmem_max"):
        try:
            with open(f"/proc/sys/net/core/{k}") as f:
                env["net_core_" + k] = int(f.read())
        except OSError:
            pass
    try:
        with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor") \
                as f:
            env["cpufreq_governor_cpu0"] = f.read().strip()
    except OSError:
        pass
    env["loadavg_at_start"] = os.getloadavg()
    env["busy_processes_at_start"] = busy_processes()
    try:
        import psutil
        env["psutil"] = psutil.__version__
    except ImportError:
        env["psutil"] = "not installed (affinity via os.sched_setaffinity)"
    return env


def busy_processes(threshold=20.0, window_s=1.0):
    """Other processes above threshold % CPU over window_s (snapshot),
    recorded so concurrent load on the host is visible."""
    try:
        import psutil
    except ImportError:
        return "psutil not installed"
    procs = []
    for p in psutil.process_iter(["pid", "name"]):
        try:
            p.cpu_percent(None)
            procs.append(p)
        except psutil.Error:
            pass
    time.sleep(window_s)
    out = []
    for p in procs:
        try:
            c = p.cpu_percent(None)
            if c >= threshold and p.pid != os.getpid():
                out.append({"pid": p.pid, "name": p.info["name"],
                            "cpu_percent": round(c, 1),
                            "affinity": p.cpu_affinity()})
        except psutil.Error:
            pass
    return out


# ---------------------------------------------------------------- charts
def fus(v):
    """Microseconds for chart labels: one decimal below 10 us."""
    return f"{v:.1f}" if v < 10 else f"{v:,.0f}"


def fpct(v):
    """Percent for chart labels: two decimals below 0.1 %."""
    return f"{v:.2f}" if v < 0.1 else f"{v:.1f}"


def charts(out_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    rows = list(csv.DictReader(open(os.path.join(out_dir, "results.csv"))))
    raw_dir = os.path.join(out_dir, "raw_latencies", "run1")
    FG, BG, GRID = "#FFFFFF", "#000000", "#666666"
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 22,
        "text.color": FG, "axes.labelcolor": FG, "xtick.color": FG,
        "ytick.color": FG, "axes.edgecolor": FG, "figure.facecolor": BG,
        "axes.facecolor": BG, "savefig.facecolor": BG,
        "axes.titlesize": 28, "axes.labelsize": 24, "xtick.labelsize": 20,
        "ytick.labelsize": 20, "legend.fontsize": 19,
        "grid.color": GRID, "grid.linewidth": 1.0})
    W, H, DPI = 2466, 1110, 100
    size_title = {172: "172 B person record (PSV3), 30 Hz",
                  1536032: "1,536,032 B frame slot (PSF1), 30 Hz"}

    def row(t, s, reg):
        for r in rows:
            if r["transport"] == t and int(r["size_bytes"]) == s \
                    and r["regime"] == reg:
                return r
        return None

    def us_fmt(v, _p):
        if v >= 1000:
            return "%g ms" % (v / 1000)
        return "%g us" % v

    # --- latency CDF
    fig, axes = plt.subplots(1, 2, figsize=(W / DPI, H / DPI), dpi=DPI)
    for ax, size in zip(axes, SIZES):
        lo, hi = float("inf"), 0.0
        for t in TRANSPORTS_MAIN:
            fn = os.path.join(raw_dir, f"{t}_{size}B_paced.csv")
            lat = []
            with open(fn) as f:
                for rr in csv.DictReader(f):
                    if rr["latency_us"]:
                        lat.append(float(rr["latency_us"]))
            lat = np.sort(np.array(lat))
            y = np.arange(1, len(lat) + 1) / len(lat)
            r = row(t, size, "paced")
            p50, p99 = float(r["p50_us"]), float(r["p99_us"])
            lo, hi = min(lo, lat[0]), max(hi, lat[-1])
            ax.step(lat, y, where="post", color=COLOR[t], lw=3.5,
                    label=f"{LABEL[t]}: p50 {fus(p50)} us, "
                          f"p99 {fus(p99)} us")
            ax.plot([p50], [0.5], "o", ms=14, color=COLOR[t],
                    markeredgecolor=FG, markeredgewidth=1.5, zorder=5)
            ax.plot([p99], [0.99], "D", ms=13, color=COLOR[t],
                    markeredgecolor=FG, markeredgewidth=1.5, zorder=5)
        ax.set_xscale("log")
        ax.set_xlim(lo / 1.6, hi * 1.6)
        ax.set_ylim(0, 1.02)
        ax.xaxis.set_major_formatter(FuncFormatter(us_fmt))
        ax.set_xlabel("one-way latency, writer stamp to reader copy "
                      "complete (log)")
        ax.set_ylabel("fraction of messages")
        ax.set_title(size_title[size], pad=16)
        ax.grid(True, which="major")
        ax.axhline(0.5, color=GRID, lw=1, ls=":")
        ax.axhline(0.99, color=GRID, lw=1, ls=":")
        leg = ax.legend(loc="lower right", facecolor=BG, edgecolor=GRID,
                        framealpha=1.0)
        for tx in leg.get_texts():
            tx.set_color(FG)
    fig.text(0.5, 0.015, "Circle = p50, diamond = p99. Loopback, Python "
             "writer and reader on separate cores, 2000 paced messages sent "
             "per curve after 200 warm-up.",
             ha="center", fontsize=19, color=FG)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(os.path.join(out_dir, "chart_transport_latency.png"),
                dpi=DPI)
    plt.close(fig)

    # --- throughput + jitter
    fig, axes = plt.subplots(1, 2, figsize=(W / DPI, H / DPI), dpi=DPI)
    xg = np.arange(len(SIZES))
    bw = 0.26
    glabel = ["172 B record", "1,536,032 B frame"]
    ax = axes[0]
    tvals = {t: [float(row(t, s, "thru")["msgs_per_s"] or 0) for s in SIZES]
             for t in TRANSPORTS_MAIN}
    pos = [v for vs in tvals.values() for v in vs if v > 0]
    y_lo, y_hi = max(min(pos) / 4, 1), max(pos) * 15
    ax.set_yscale("log")
    ax.set_ylim(y_lo, y_hi)
    for j, t in enumerate(TRANSPORTS_MAIN):
        vals = tvals[t]
        xs = xg + (j - 1) * bw
        ax.bar(xs, [v if v > 0 else y_lo for v in vals], bw * 0.92,
               color=COLOR[t], label=LABEL[t])
        for x, v, s in zip(xs, vals, SIZES):
            r = row(t, s, "thru")
            txt = f"{v:,.0f}" if v > 0 else "0 delivered"
            if t == "shm":
                txt += "\nwriter" + (" " if v > 0 else "\n") + \
                    f"{float(r['writer_msgs_per_s']):,.0f}/s"
            lp = float(r["loss_pct"] or 0)
            sp = float(r["skipped_pct"] or 0)
            if lp > 0:
                txt += f"\nloss {fpct(lp)}%"
            if sp > 0:
                txt += f"\nskip {fpct(sp)}%"
            ax.text(x, (v if v > 0 else y_lo) * 1.15, txt, ha="center",
                    va="bottom", fontsize=17 if v > 0 else 15, color=FG)
    ax.set_xticks(xg)
    ax.set_xticklabels(glabel)
    ax.set_ylabel("messages per second (log)")
    ax.set_title("Maximum sustained throughput, unpaced, 5 s", pad=16)
    ax.grid(True, axis="y", which="major")
    ax.set_axisbelow(True)
    leg = ax.legend(loc="upper right", facecolor=BG, edgecolor=GRID,
                    framealpha=1.0)
    for tx in leg.get_texts():
        tx.set_color(FG)

    ax = axes[1]
    jmax = 0.0
    for j, t in enumerate(TRANSPORTS_MAIN):
        vals = [float(row(t, s, "paced")["jitter_ms"]) for s in SIZES]
        xs = xg + (j - 1) * bw
        ax.bar(xs, vals, bw * 0.92, color=COLOR[t], label=LABEL[t])
        jmax = max(jmax, max(vals))
        for x, v, s in zip(xs, vals, SIZES):
            r = row(t, s, "paced")
            txt = f"{v:.3f}"
            lp = float(r["loss_pct"] or 0)
            sp = float(r["skipped_pct"] or 0)
            if lp > 0:
                txt += f"\nloss {fpct(lp)}%"
            if sp > 0:
                txt += f"\nskip {fpct(sp)}%"
            ax.text(x, v + 0.0, txt, ha="center", va="bottom", fontsize=17,
                    color=FG)
    ax.set_ylim(0, jmax * 1.35 if jmax > 0 else 1)
    ax.set_xticks(xg)
    ax.set_xticklabels(glabel)
    ax.set_ylabel("p99 - p50 inter-arrival (ms)")
    ax.set_title("Reader-side jitter at 30 Hz", pad=16)
    ax.grid(True, axis="y", which="major")
    ax.set_axisbelow(True)
    leg = ax.legend(loc="upper left", facecolor=BG, edgecolor=GRID,
                    framealpha=1.0)
    for tx in leg.get_texts():
        tx.set_color(FG)
    fig.text(0.5, 0.015, "Loopback, Python writer and reader on separate "
             "cores. Shared memory is a latest-value mailbox: 'skip' = "
             "records overwritten before the reader copied them.",
             ha="center", fontsize=18, color=FG)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(os.path.join(out_dir, "chart_transport_throughput.png"),
                dpi=DPI)
    plt.close(fig)


# ------------------------------------------------------- package condition
# Round 5 (deck page 41): one whole per-frame package per 30 Hz tick, the
# 172 B person record plus one 1,536,032 B frame slot, moved from a Python
# writer to a separate Python reader process standing in for Unity.
# Timing per package: writer time.monotonic_ns() taken immediately before
# the first byte of the package is written or sent, to reader
# time.monotonic_ns() when both parts have been read consistently (one
# CLOCK_MONOTONIC on one host). A package is lost when the reader never
# completes it. Decisions: presentation/defense_2026/DECISIONS.md D-180 to D-188.
PKG_REC, PKG_FRAME = SIZES      # 172 B person record, 1,536,032 B frame
PKG_BYTES = PKG_REC + PKG_FRAME
PKG_N_MEAS = 1000               # brief (round 5): 1000 packages per run
PKG_N_WARM = N_WARM             # same 200 warm-up as the paced conditions
PKG_TRANSPORTS = ("shm", "udp", "tcp")   # chart order; shm = pipeline
PKG_LABEL = {"shm": "Shared memory", "udp": "UDP", "tcp": "TCP"}
PKG_NCH = n_chunks(PKG_FRAME) + 1        # 26 frame datagrams + 1 record


def pkg_writer_main(cfg, port, out_q):
    gc.disable()
    method, aff = pin(cfg["writer_cpu"])
    transport = cfg["transport"]
    n_total = cfg["n_warm"] + cfg["n_meas"]
    clock = time.monotonic_ns
    pack_idx = IDX_TS.pack_into
    ts_arr = np.full(n_total, -1, np.int64)
    rec = make_message(PKG_REC)
    frame = make_message(PKG_FRAME)

    if transport == "tcp":
        # one framed message: u32 length, then record, then frame
        sock = socket.create_connection(("127.0.0.1", port))
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        buf = bytearray(4) + rec + frame
        U32.pack_into(buf, 0, PKG_BYTES)
        sendall = sock.sendall

        def send(k):
            t = clock()
            pack_idx(buf, 4 + 8, k, 0, t)
            pack_idx(buf, 4 + PKG_REC + 8, k, 0, t)
            sendall(buf)
            return t

        def finish():
            pack_idx(buf, 4 + 8, END_IDX, 0, 0)
            pack_idx(buf, 4 + PKG_REC + 8, END_IDX, 0, 0)
            sendall(buf)
            sock.shutdown(socket.SHUT_WR)
            sock.close()

    elif transport == "udp":
        # frame split into 60,000 B datagrams, then the record as the
        # last datagram; header: package index, chunk index, chunk count
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("127.0.0.1", port))
        fmv = memoryview(frame)
        nfc = n_chunks(PKG_FRAME)
        parts = [fmv[c * UDP_CHUNK:(c + 1) * UDP_CHUNK] for c in range(nfc)]
        parts.append(memoryview(rec))
        hdrs = [bytearray(UDP_HDR.size) for _ in range(PKG_NCH)]
        sendmsg = sock.sendmsg
        pack_u = UDP_HDR.pack_into

        def send(k):
            t = clock()
            pack_idx(frame, 8, k, 0, t)
            pack_idx(rec, 8, k, 0, t)
            for c in range(PKG_NCH):
                h = hdrs[c]
                pack_u(h, 0, k, c, PKG_NCH)
                sendmsg([h, parts[c]])
            return t

        def finish():
            end = UDP_HDR.pack(UDP_END, 0, 1)
            for _ in range(10):
                try:
                    sock.send(end)
                except ConnectionRefusedError:
                    break
                time.sleep(0.02)
            sock.close()

    else:  # shm: two /dev/shm records, each under its own seqlock
        maps = []
        for path, size, msg in ((cfg["shm_frame"], PKG_FRAME, frame),
                                (cfg["shm_rec"], PKG_REC, rec)):
            fd = os.open(path, os.O_RDWR)
            mm = mmap.mmap(fd, size)
            os.close(fd)
            mmv = memoryview(mm)
            mv = memoryview(msg)
            mmv[0:4] = mv[0:4]              # magic
            maps.append({"mm": mm, "mmv": mmv, "mv": mv, "size": size,
                         "msg": msg, "body": mv[8:size],
                         "seq": U32.unpack_from(mm, 4)[0] & ~1})
        pack_u32 = U32.pack

        # Seq words stored as pre-packed 4-byte slice copies, never with
        # struct.pack_into on the mapping (zero-fill; DECISIONS.md D-154).
        # Frame first, then the record: the record's new even seq tells
        # the reader the whole package is in place.
        def publish(m):
            s = m["seq"] + 1
            mmv = m["mmv"]
            mmv[4:8] = pack_u32(s)          # odd: writer mid-update
            mmv[8:m["size"]] = m["body"]    # payload
            mmv[4:8] = pack_u32(s + 1)      # even: stable, AFTER payload
            m["seq"] = s + 1

        def send(k):
            t = clock()
            for m in maps:
                pack_idx(m["msg"], 8, k, 0, t)   # local buffer
            for m in maps:
                publish(m)
            return t

        def finish():
            send(END_IDX)
            for m in maps:
                for v in (m["body"], m["mv"], m["mmv"]):
                    v.release()
                m["mm"].close()

    period = int(round(1e9 / RATE_HZ))
    t0 = clock() + 50_000_000
    for k in range(n_total):
        target = t0 + k * period
        rem = target - clock() - PACE_SPIN_NS
        if rem > 0:
            time.sleep(rem / 1e9)
        while clock() < target:
            pass
        ts_arr[k] = send(k)
    target = t0 + n_total * period          # END one period later
    rem = target - clock() - PACE_SPIN_NS
    if rem > 0:
        time.sleep(rem / 1e9)
    finish()
    out_q.put(("writer", {"writer_pin_method": method,
                          "writer_affinity": aff, "n_sent": n_total,
                          "ts": ts_arr}))


def pkg_reader_main(cfg, ready, port_val, out_q):
    gc.disable()
    method, aff = pin(cfg["reader_cpu"])
    transport = cfg["transport"]
    n_total = cfg["n_warm"] + cfg["n_meas"]
    tr_arr = np.full(n_total, -1, np.int64)
    clock = time.monotonic_ns
    unpack_idx = IDX_TS.unpack_from
    extra = {"mismatched_parts": 0, "duplicates": 0}
    deadline = time.monotonic() + cfg["timeout_s"]
    last = [-1]

    def done_pkg(idx, tr):
        if idx <= last[0]:
            extra["duplicates"] += 1
            return
        last[0] = idx
        if 0 <= idx < n_total:
            tr_arr[idx] = tr

    if transport == "tcp":
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        port_val.value = srv.getsockname()[1]
        ready.set()
        srv.settimeout(cfg["timeout_s"])
        conn, _ = srv.accept()
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        conn.settimeout(cfg["timeout_s"])
        extra["tcp_rcvbuf"] = conn.getsockopt(socket.SOL_SOCKET,
                                              socket.SO_RCVBUF)
        msz = 4 + PKG_BYTES
        cap = max(4 * 1024 * 1024, 3 * msz)
        buf = bytearray(cap)
        mv = memoryview(buf)
        recv_into = conn.recv_into
        start = end = 0
        fin = False
        while not fin:
            r = recv_into(mv[end:], cap - end)
            tr = clock()                    # completion clock
            if r == 0:
                break
            end += r
            while end - start >= 4:
                n = U32.unpack_from(buf, start)[0]
                if end - start < 4 + n:
                    break
                ridx = unpack_idx(buf, start + 4 + 8)[0]
                fidx = unpack_idx(buf, start + 4 + PKG_REC + 8)[0]
                start += 4 + n
                if ridx == END_IDX:
                    fin = True
                    break
                if ridx != fidx:
                    extra["mismatched_parts"] += 1
                    continue
                done_pkg(ridx, tr)
            if start == end:
                start = end = 0
            elif cap - end < msz:
                tail = bytes(mv[start:end])
                buf[:len(tail)] = tail
                end -= start
                start = 0
        mv.release()
        conn.close()
        srv.close()

    elif transport == "udp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("127.0.0.1", 0))
        extra["udp_rcvbuf"] = sock.getsockopt(socket.SOL_SOCKET,
                                              socket.SO_RCVBUF)
        port_val.value = sock.getsockname()[1]
        sock.settimeout(cfg["timeout_s"])
        ready.set()
        chunk = bytearray(65536)
        cmv = memoryview(chunk)
        frame = bytearray(PKG_FRAME)
        fmv = memoryview(frame)
        rec = bytearray(PKG_REC)
        rmv = memoryview(rec)
        nfc = PKG_NCH - 1
        unpack_u = UDP_HDR.unpack_from
        recv_into = sock.recv_into
        hs = UDP_HDR.size
        cur, got, seen = -1, 0, 0
        given_up = 0
        while True:
            try:
                n = recv_into(chunk)
            except socket.timeout:
                extra["udp_end_timeout"] = True
                break
            idx, c, nch = unpack_u(chunk, 0)
            if idx == UDP_END:
                break
            if idx != cur:
                if idx < cur:
                    continue                # stale datagram, package gone
                if got:
                    given_up += 1           # next package started first
                cur, got, seen = idx, 0, 0
            bit = 1 << c
            if seen & bit:
                continue
            seen |= bit
            if c < nfc:
                off = c * UDP_CHUNK
                fmv[off:off + n - hs] = cmv[hs:n]
            else:
                rmv[:n - hs] = cmv[hs:n]
            got += 1
            if got == nch:
                tr = clock()                # completion clock
                got, seen = 0, 0
                if unpack_idx(frame, 8)[0] != idx or \
                        unpack_idx(rec, 8)[0] != idx:
                    extra["mismatched_parts"] += 1
                    continue
                done_pkg(idx, tr)
        extra["udp_packages_given_up"] = given_up
        cmv.release()
        fmv.release()
        rmv.release()
        sock.close()

    else:  # shm, busy-wait reader
        opened = []
        for path, size in ((cfg["shm_frame"], PKG_FRAME),
                           (cfg["shm_rec"], PKG_REC)):
            fd = os.open(path, os.O_RDONLY)
            mm = mmap.mmap(fd, size, access=mmap.ACCESS_READ)
            os.close(fd)
            dst = bytearray(size)
            opened.append((mm, memoryview(mm), dst, memoryview(dst), size))
        (fmm, fsmv, fdst, fdmv, _), (rmm, rsmv, rdst, rdmv, _) = opened
        u32 = U32.unpack_from
        seqw = U32.unpack
        last_r = seqw(rmm[4:8])[0]
        rec_retries = frame_retries = 0
        spins = 0
        ready.set()
        while True:
            s1 = seqw(rmm[4:8])[0]
            if s1 == last_r or (s1 & 1):
                spins += 1
                if (spins & 0xFFFFF) == 0 and time.monotonic() > deadline:
                    extra["shm_timeout"] = True
                    break
                continue
            rdmv[:] = rsmv[:PKG_REC]        # copy the record out
            s2 = seqw(rmm[4:8])[0]
            if s2 != s1 or u32(rdst, 4)[0] != s1:
                rec_retries += 1
                continue
            last_r = s1
            idx = unpack_idx(rdst, 8)[0]
            if idx == END_IDX:
                break
            while True:                     # then the frame, same package
                f1 = seqw(fmm[4:8])[0]
                if f1 & 1:
                    continue
                fdmv[:] = fsmv[:PKG_FRAME]
                f2 = seqw(fmm[4:8])[0]
                if f2 != f1 or u32(fdst, 4)[0] != f1:
                    frame_retries += 1
                    continue
                break
            tr = clock()                    # completion clock
            if unpack_idx(fdst, 8)[0] != idx:
                extra["mismatched_parts"] += 1   # frame already replaced
                continue
            done_pkg(idx, tr)
        extra["shm_record_retries"] = rec_retries
        extra["shm_frame_retries"] = frame_retries
        extra["shm_poll"] = "busy-wait"
        for mm, smv, _d, dmv, _s in opened:
            smv.release()
            dmv.release()
            mm.close()

    res = {"reader_pin_method": method, "reader_affinity": aff,
           "tr": tr_arr}
    res.update(extra)
    out_q.put(("reader", res))


def pkg_run_condition(ctx, transport, counts):
    cfg = {"transport": transport, "n_warm": counts["n_warm"],
           "n_meas": counts["n_meas"], "writer_cpu": WRITER_CPU,
           "reader_cpu": READER_CPU, "shm_frame": None, "shm_rec": None}
    cfg["timeout_s"] = (counts["n_warm"] + counts["n_meas"]) / RATE_HZ + 60.0
    made = []
    if transport == "shm":
        for key, size in (("shm_frame", PKG_FRAME), ("shm_rec", PKG_REC)):
            path = f"{SHM_PREFIX}{os.getpid()}_package_{key}"
            _CLEANUP_PATHS.add(path)
            fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
            os.ftruncate(fd, size)
            os.close(fd)
            cfg[key] = path
            made.append(path)
    q = ctx.Queue()
    ready = ctx.Event()
    port = ctx.Value("i", 0)
    r = ctx.Process(target=pkg_reader_main, args=(cfg, ready, port, q))
    _CHILDREN.append(r)
    r.start()
    if not ready.wait(30):
        raise RuntimeError(f"reader not ready: package {transport}")
    w = ctx.Process(target=pkg_writer_main, args=(cfg, port.value, q))
    _CHILDREN.append(w)
    w.start()
    got = {}
    t_wall0 = time.monotonic()
    while len(got) < 2:
        kind, payload = q.get(timeout=cfg["timeout_s"] + 30)
        got[kind] = payload
    for p in (w, r):
        p.join(10)
        if p.is_alive():
            p.terminate()
            p.join(2)
        _CHILDREN.remove(p)
    for path in made:
        os.unlink(path)
        _CLEANUP_PATHS.discard(path)
    got["wall_s"] = time.monotonic() - t_wall0
    return got


PKG_COLS = ["run", "transport", "package_bytes", "rate_hz", "n", "delivered",
            "lost", "median_ms", "min_ms", "max_ms", "reader_poll",
            "recv_buffer_bytes"]


def pkg_summarise(run, transport, got, counts, raw_dir):
    ts, tr = got["writer"]["ts"], got["reader"]["tr"]
    n_warm, n_meas = counts["n_warm"], counts["n_meas"]
    sel = np.arange(n_warm, n_warm + n_meas)
    ok = tr[sel] >= 0
    ms = (tr[sel][ok] - ts[sel][ok]) / 1e6
    rr = got["reader"]
    row = {"run": run, "transport": transport, "package_bytes": PKG_BYTES,
           "rate_hz": RATE_HZ, "n": n_meas, "delivered": int(ok.sum()),
           "lost": int(n_meas - ok.sum()),
           "median_ms": float(np.median(ms)) if len(ms) else float("nan"),
           "min_ms": float(ms.min()) if len(ms) else float("nan"),
           "max_ms": float(ms.max()) if len(ms) else float("nan"),
           "reader_poll": "busy-wait" if transport == "shm"
           else "blocking recv",
           "recv_buffer_bytes": rr.get("udp_rcvbuf", rr.get("tcp_rcvbuf",
                                                            ""))}
    os.makedirs(raw_dir, exist_ok=True)
    with open(os.path.join(raw_dir, f"package_{transport}.csv"), "w",
              newline="") as f:
        wr = csv.writer(f, lineterminator="\n")
        wr.writerow(["index", "t_write_start_ns", "t_read_complete_ns",
                     "time_ms", "delivered"])
        for i in sel:
            if tr[i] >= 0:
                wr.writerow([int(i), int(ts[i]), int(tr[i]),
                             "%.4f" % ((tr[i] - ts[i]) / 1e6), 1])
            else:
                wr.writerow([int(i), int(ts[i]), "", "", 0])
    meta = {k: v for k, v in rr.items() if k != "tr"}
    meta.update({k: v for k, v in got["writer"].items() if k != "ts"})
    meta["wall_s"] = round(got["wall_s"], 2)
    meta["transport"] = transport
    return row, meta


def pkg_write_csv(path, rows):
    with open(path, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=PKG_COLS, lineterminator="\n")
        wr.writeheader()
        for r in rows:
            out = {}
            for k in PKG_COLS:
                v = r[k]
                if isinstance(v, float) and k.endswith("_ms"):
                    v = "" if math.isnan(v) else "%.4f" % v
                out[k] = v
            wr.writerow(out)


def run_package(out, n_runs, counts):
    """Package condition: n_runs runs of the three transports; writes
    results_package_run<k>.csv, results_package.csv, raw CSVs under
    raw_latencies/package_run<k>/, the package block of environment.json
    and chart_transport_package.png."""
    atexit.register(_cleanup)
    signal.signal(signal.SIGTERM, _on_signal)
    signal.signal(signal.SIGINT, _on_signal)
    stale = glob.glob(SHM_PREFIX + "*")
    if stale:
        print("WARNING: stale files present (not touched):", stale)
    pin_parent = pin(PARENT_CPU)
    ctx = mp.get_context("spawn")
    os.makedirs(out, exist_ok=True)
    penv = {"date_local": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "clock": "time.monotonic_ns (CLOCK_MONOTONIC), writer and "
                     "reader processes on one host",
            "clock_info": str(time.get_clock_info("monotonic")),
            "package": f"{PKG_REC} B record + {PKG_FRAME} B frame = "
                       f"{PKG_BYTES} B per tick",
            "rate_hz": RATE_HZ, "counts": counts,
            "udp_chunk": UDP_CHUNK, "udp_datagrams_per_package": PKG_NCH,
            "writer_cpu": WRITER_CPU, "reader_cpu": READER_CPU,
            "parent_cpu": PARENT_CPU, "parent_pin": pin_parent,
            "host_cpu_model": environment_cpu_model(),
            "python": sys.version.split()[0],
            "python_executable": sys.executable,
            "loadavg_at_start": os.getloadavg(),
            "busy_processes_at_start": busy_processes(), "runs": []}
    for k in ("rmem_default", "rmem_max"):
        try:
            with open(f"/proc/sys/net/core/{k}") as f:
                penv["net_core_" + k] = int(f.read())
        except OSError:
            pass
    all_rows = []
    try:
        for run in range(1, n_runs + 1):
            t0 = time.monotonic()
            rows, metas = [], []
            raw_dir = os.path.join(out, "raw_latencies", f"package_run{run}")
            for t in PKG_TRANSPORTS:
                print(f"package run {run}: {t:4s} ...", end="", flush=True)
                got = pkg_run_condition(ctx, t, counts)
                row, meta = pkg_summarise(run, t, got, counts, raw_dir)
                rows.append(row)
                metas.append(meta)
                print(f" delivered {row['delivered']}/{row['n']} "
                      f"median {row['median_ms']:.3f} ms "
                      f"min {row['min_ms']:.3f} max {row['max_ms']:.3f}")
            pkg_write_csv(os.path.join(out, f"results_package_run{run}.csv"),
                          rows)
            all_rows += rows
            penv["runs"].append({"run": run,
                                 "wall_s": round(time.monotonic() - t0, 1),
                                 "loadavg_at_end": os.getloadavg(),
                                 "busy_processes_at_end": busy_processes(),
                                 "conditions": metas})
        pkg_write_csv(os.path.join(out, "results_package.csv"), all_rows)
        env_path = os.path.join(out, "environment.json")
        env = {}
        if os.path.exists(env_path):
            with open(env_path) as f:
                env = json.load(f)
        env["package_condition"] = penv
        with open(env_path, "w") as f:
            json.dump(env, f, indent=2, default=str)
            f.write("\n")
        chart_package(out)
    finally:
        _cleanup()
    left = glob.glob(f"{SHM_PREFIX}{os.getpid()}_*")
    print("shm files left:", left if left else "none")


def environment_cpu_model():
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return ""


def fms(v):
    """Milliseconds for chart labels, three significant digits."""
    if v >= 10:
        return f"{v:.1f}"
    if v >= 1:
        return f"{v:.2f}"
    return f"{v:.3f}"


# D-259 (round 7, build 60): every baked text of the package chart uses one
# size that reaches 16 pt on the slide. Hidden page 43 places the 12.33 x
# 5.55 in figure 1:1 (measured in the PPTX: 12.330 x 5.550 in, no caption), so
# the figure size equals the slide size (44.4 px at 200 dpi).
PKG_TEXT_PT = 16.0


def chart_package(out_dir, run=1):
    """One bar per transport: median time from write start to read
    complete, a thin whisker from the fastest to the slowest delivered
    package, lost count under each bar. Deck style, 12.33 x 5.55 in."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = [r for r in csv.DictReader(open(
        os.path.join(out_dir, "results_package.csv")))
        if int(r["run"]) == run]
    by = {r["transport"]: r for r in rows}
    env = json.load(open(os.path.join(out_dir, "environment.json")))
    cpu = env.get("package_condition", {}).get("host_cpu_model", "")
    FG, MUTED, RULE, BG = "#FFFFFF", "#BBBBBB", "#666666", "#000000"
    BAR, HIGHLIGHT = "#70B7E6", "#FFD088"
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": PKG_TEXT_PT,
                         "text.color": FG, "axes.labelcolor": FG,
                         "xtick.color": FG, "ytick.color": MUTED,
                         "axes.edgecolor": RULE, "figure.facecolor": BG,
                         "axes.facecolor": BG, "savefig.facecolor": BG})
    fig = plt.figure(figsize=(12.33, 5.55), dpi=200)
    ax = fig.add_axes((0.09, 0.2, 0.89, 0.56))
    xs = np.arange(len(PKG_TRANSPORTS))
    med = [float(by[t]["median_ms"]) for t in PKG_TRANSPORTS]
    lo = [float(by[t]["min_ms"]) for t in PKG_TRANSPORTS]
    hi = [float(by[t]["max_ms"]) for t in PKG_TRANSPORTS]
    ymax = max(hi) * 1.08
    bw = 0.42
    for x, t, m, a, b in zip(xs, PKG_TRANSPORTS, med, lo, hi):
        ax.bar(x, m, bw, color=HIGHLIGHT if t == "shm" else BAR, zorder=2)
        ax.plot([x, x], [a, b], color=FG, lw=1.2, zorder=3)
        for y in (a, b):
            ax.plot([x - 0.045, x + 0.045], [y, y], color=FG, lw=1.2,
                    zorder=3)
        # typical value beside the bar top, clear of the whisker
        ax.text(x + bw / 2 + 0.04, m, f"{fms(m)} ms", ha="left",
                va="bottom", fontsize=PKG_TEXT_PT, fontweight="bold", color=FG,
                zorder=4)
        ax.text(x + bw / 2 + 0.04, m, "typical", ha="left", va="top",
                fontsize=PKG_TEXT_PT, color=MUTED, zorder=4)
    ax.set_xlim(-0.55, len(xs) - 0.25)
    ax.set_ylim(0, ymax)
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{PKG_LABEL[t]}\nlost {by[t]['lost']} of "
                        f"{by[t]['n']}" for t in PKG_TRANSPORTS],
                       fontsize=PKG_TEXT_PT, color=FG)
    ax.tick_params(axis="x", length=0, pad=8)
    ax.tick_params(axis="y", labelsize=PKG_TEXT_PT, color=RULE)
    ax.set_ylabel("Time to move one frame package (ms)", fontsize=PKG_TEXT_PT)
    ax.grid(True, axis="y", color=RULE, lw=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    cpu_short = cpu.split(" Processor")[0]
    cpu_short = " ".join(w for w in cpu_short.split()
                         if not w.endswith("-Core")) or "CPU not recorded"
    fig.text(0.09, 0.945, "Python to Unity stand-in, one frame package "
             "(1.5 MB) at 30 Hz, localhost", fontsize=PKG_TEXT_PT, color=FG,
             ha="left", va="center")
    fig.text(0.09, 0.875, f"Desktop workstation ({cpu_short}, Linux); "
             "the reader is a Python stand-in for Unity.",
             fontsize=PKG_TEXT_PT, color=MUTED, ha="left", va="center")
    fig.text(0.09, 0.82, "Bar: typical package. Thin line: fastest to "
             "slowest delivered package.", fontsize=PKG_TEXT_PT, color=MUTED,
             ha="left", va="center")
    fig.canvas.draw()                   # every text inside the figure
    rend = fig.canvas.get_renderer()
    fb = fig.bbox
    for t in fig.findobj(matplotlib.text.Text):
        if not t.get_text() or not t.get_visible():
            continue
        bb = t.get_window_extent(rend)
        if bb.x0 < fb.x0 - 0.5 or bb.x1 > fb.x1 + 0.5 or \
                bb.y0 < fb.y0 - 0.5 or bb.y1 > fb.y1 + 0.5:
            raise ValueError(f"chart text outside the figure: "
                             f"{t.get_text()!r}")
    fig.savefig(os.path.join(out_dir, "chart_transport_package.png"),
                dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=HERE)
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--quick", action="store_true",
                    help="small counts for a smoke test")
    ap.add_argument("--charts-only", action="store_true")
    ap.add_argument("--package", action="store_true",
                    help="run only the package condition (record + frame "
                         "per 30 Hz tick); leaves results.csv untouched")
    ap.add_argument("--package-chart-only", action="store_true",
                    help="re-render chart_transport_package.png from "
                         "results_package.csv")
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    if args.charts_only:
        charts(out)
        return 0
    if args.package_chart_only:
        chart_package(out)
        return 0
    if args.package:
        pcounts = ({"n_warm": 20, "n_meas": 60} if args.quick
                   else {"n_warm": PKG_N_WARM, "n_meas": PKG_N_MEAS})
        run_package(out, args.runs, pcounts)
        return 0

    atexit.register(_cleanup)
    signal.signal(signal.SIGTERM, _on_signal)
    signal.signal(signal.SIGINT, _on_signal)
    stale = glob.glob(SHM_PREFIX + "*")
    if stale:
        print("WARNING: stale files present (not touched):", stale)

    counts = ({"n_warm": 20, "n_meas": 60, "thru_s": 0.5} if args.quick
              else {"n_warm": N_WARM, "n_meas": N_MEAS, "thru_s": THRU_S})
    pin_parent = pin(PARENT_CPU)
    env = environment(counts, pin_parent)
    ctx = mp.get_context("spawn")
    os.makedirs(out, exist_ok=True)
    env["runs"] = []
    all_rows = {}
    try:
        for run in range(1, args.runs + 1):
            t0 = time.monotonic()
            rows, metas = [], []
            raw_dir = os.path.join(out, "raw_latencies", f"run{run}")
            for (t, s, reg) in conditions():
                print(f"run {run}: {t:13s} {s:8d} B {reg:5s} ...",
                      end="", flush=True)
                got = run_condition(ctx, t, s, reg, counts)
                row, meta = summarise(run, t, s, reg, got, counts, raw_dir)
                meta.update({"transport": t, "size": s, "regime": reg})
                rows.append(row)
                metas.append(meta)
                if reg == "paced":
                    print(f" n={row['n']} p50={row['p50_us']:.1f} us "
                          f"p99={row['p99_us']:.1f} us "
                          f"jitter={row['jitter_ms']:.3f} ms "
                          f"loss={row['loss_pct']:.2f}% "
                          f"skip={row['skipped_pct']:.2f}%")
                else:
                    print(f" {row['msgs_per_s']:,.0f} msg/s "
                          f"({row['MB_per_s']:,.1f} MB/s) writer "
                          f"{row['writer_msgs_per_s']:,.0f}/s "
                          f"loss={row['loss_pct']:.2f}% "
                          f"skip={row['skipped_pct']:.2f}%")
            name = "results.csv" if run == 1 else f"results_run{run}.csv"
            write_csv(os.path.join(out, name), rows)
            all_rows[run] = rows
            env["runs"].append({"run": run,
                                "wall_s": round(time.monotonic() - t0, 1),
                                "loadavg_at_end": os.getloadavg(),
                                "busy_processes_at_end": busy_processes(),
                                "conditions": metas})
        if args.runs >= 2:
            with open(os.path.join(out, "run_to_run.csv"), "w",
                      newline="") as f:
                wr = csv.writer(f, lineterminator="\n")
                wr.writerow(["transport", "size_bytes", "regime",
                             "run1_p50_us", "run2_p50_us", "diff_pct",
                             "run1_msgs_per_s", "run2_msgs_per_s",
                             "thru_diff_pct"])
                for a, b in zip(all_rows[1], all_rows[2]):
                    if a["regime"] == "paced":
                        d = 100.0 * (b["p50_us"] - a["p50_us"]) / a["p50_us"]
                        wr.writerow([a["transport"], a["size_bytes"],
                                     "paced", "%.1f" % a["p50_us"],
                                     "%.1f" % b["p50_us"], "%.1f" % d,
                                     "", "", ""])
                    else:
                        x, y = a["msgs_per_s"], b["msgs_per_s"]
                        d = 100.0 * (y - x) / x if x else float("nan")
                        wr.writerow([a["transport"], a["size_bytes"],
                                     "thru", "", "", "", "%.1f" % x,
                                     "%.1f" % y, "%.1f" % d])
        with open(os.path.join(out, "environment.json"), "w") as f:
            json.dump(env, f, indent=2, default=str)
            f.write("\n")
        charts(out)
    finally:
        _cleanup()
    left = glob.glob(f"{SHM_PREFIX}{os.getpid()}_*")
    print("shm files left:", left if left else "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())

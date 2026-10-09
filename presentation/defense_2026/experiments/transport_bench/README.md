# Transport benchmark: TCP vs UDP vs shared memory

Currency note (2026-10-08): This is a retained benchmark with pinned
workstation conditions and result files. Page references 38-41 belong to
its original deck and are not rebound to the final presentation.
Run the relative transport_bench.py commands below from
presentation/defense_2026/experiments/transport_bench. No benchmark was
rerun for this currency update. Current delivery/navigation is in
[the presentation README](../../README.md).

Decisions: presentation/defense_2026/DECISIONS.md D-149 to D-159

## Purpose

Defence Q&A support for "why does the pipeline use shared memory?"
(thesis Section 6.1, Table 6.1; deck pages 38-40). The pipeline moves
fixed-size records through /dev/shm files written with Python mmap
under a seqlock and read by Unity with MemoryMappedFile every frame
(v3/replay/psv3.py, Unity/Assets/Scripts/V3/V3PersonReceiver.cs,
v2/common/shm_ring.py). This benchmark measures, on this workstation,
what the two socket alternatives would cost for the same two message
sizes: the 172 B PSV3 person record and one 1,536,032 B PSF1 frame
slot.

## Command

    /home/luo/anaconda3/bin/python transport_bench.py            # 2 runs + charts
    /home/luo/anaconda3/bin/python transport_bench.py --charts-only
    /home/luo/anaconda3/bin/python transport_bench.py --quick --out DIR   # smoke test

Run time: 1,242 s wall for the two runs (about 21 minutes; each run
is 8 paced conditions of 2,200 messages at 30 Hz plus 6 unpaced
conditions of 5 s). The only temporary files are
/dev/shm/bench_transport_<pid>_*; the script removes them at exit,
also on an exception, SIGINT or SIGTERM.

## Method (short)

- Two processes (multiprocessing, spawn): writer pinned to CPU 8,
  reader to CPU 10, parent to CPU 12 (psutil; distinct physical cores
  per sysfs thread_siblings_list).
- Same message in every transport: 24-byte header (magic, seq,
  index, pad, t_send_ns) plus filler to 172 B or 1,536,032 B.
- TCP: loopback, TCP_NODELAY on both ends, u32 length prefix,
  blocking recv into a buffer. UDP: loopback, 60,000 B chunks with an
  8-byte header (message index, chunk index, chunk count),
  reassembled; default socket buffers. Shared memory: mmap over a
  /dev/shm file, PSV3 layout (magic at 0, seq at 4, odd while
  writing); the reader busy-waits on the seq word, copies the record
  out and re-checks seq. A sensitivity variant (shm_sleep1ms) sleeps
  1 ms between polls, the default of the repository's Python ring
  reader.
- Paced regime: 30 Hz, 200 warm-up + 2,000 measured messages.
  Latency = reader perf_counter_ns on completion minus the writer's
  perf_counter_ns taken immediately before the send / publish (same
  host, same clock). Jitter = p99 minus p50 of the reader-side
  inter-arrival interval.
- Unpaced regime: 200 warm-up, then 5 s flat out. Throughput =
  messages delivered to the reader per second. UDP loss from index
  gaps; shared-memory "skipped" = records overwritten before the
  reader copied them (latest-value mailbox by design).
- Design choices and their sources: presentation/defense_2026/DECISIONS.md D-149 to D-159.

## Outputs

| File | Holds |
| --- | --- |
| results.csv | run 1, one row per transport x size x regime: n, p50/p90/p99/max latency (us), inter-arrival p50 and jitter (ms), writer-side send jitter, writer and delivered rates, MB/s, loss %, skipped %, seqlock retries, duplicates, conceptual copies and kernel calls per message, reader polling |
| results_run2.csv | the same for run 2 |
| run_to_run.csv | p50 latency and throughput of run 1 vs run 2 per condition |
| raw_latencies/run1, run2 | one CSV per paced condition: index, t_send_ns, t_recv_ns, latency_us (empty = not received); 1.4 MB in total, committed |
| environment.json | CPU model, kernel, Python, affinity, SMT siblings, socket buffer sizes, governor, load, busy processes, per-condition reader and writer metadata |
| chart_transport_latency.png | latency CDF at 30 Hz, 172 B (left) and 1,536,032 B (right), log x, p50 and p99 marked |
| chart_transport_throughput.png | unpaced throughput (left, log) and 30 Hz jitter (right), loss and skip annotated |
| SLIDE_TEXT.md | text for deck pages 38-40 |

## Results summary (results.csv, run 1)

1. 172 B at 30 Hz, p50 / p99 latency: shared memory 2.67 / 3.21 us, UDP 30.67 / 107.4 us, TCP 37.97 / 120.8 us.
2. 1,536,032 B at 30 Hz, p50 / p99: shared memory 54.38 / 73.66 us, TCP 232.2 / 317.1 us, UDP 239.8 / 268.1 us.
3. 30 Hz jitter (p99 - p50 inter-arrival): shared memory 0.0009 ms (172 B) and 0.0084 ms (1,536,032 B); TCP 0.0803 and 0.0808 ms; UDP 0.0774 and 0.0255 ms.
4. Loss at 30 Hz: UDP lost 4.55 % of 1,536,032 B frames (n 1909 of 2000); TCP and shared memory lost none; UDP lost none at 172 B.
5. Unpaced 172 B: shared memory delivered 1,341,725 msg/s (writer 3,053,020/s, 56.05 % skipped), UDP 307,629 msg/s, TCP 246,799 msg/s.
6. Unpaced 1,536,032 B: TCP 5,514.6 msg/s (8,470.6 MB/s), UDP 5,859.7 msg/s (0.0102 % loss); the single-slot shared-memory mailbox delivered 0 while its writer republished 30,081.6 times/s, because the reader never completed a 1.5 MB copy between two overwrites.

Line 6 is a property of a single-slot seqlock with a flat-out writer,
not of shared memory as such; the pipeline's frame path uses a
multi-slot ring (v2/common/shm_ring.py) and publishes at the camera
rate. Run-to-run p50 variation is in run_to_run.csv (within 1.7 %
for every condition except shared memory 172 B, 2.7 vs 2.4 us).

## Caveats

- Loopback only, one machine; no network, no NIC.
- Python endpoints on both sides. The real reader is Unity C#
  (MemoryMappedFile, polled once per rendered frame), which was not
  measured; that per-frame poll adds its own delay, which the 1 ms
  sleep-poll rows (shm_sleep1ms) only approximate.
- The shared-memory rows use a busy-waiting reader, which burns one
  core; the socket readers block in the kernel. Sleep-polling at 1 ms
  moves shared-memory p50 to 518.6 us (172 B) and 598.5 us
  (1,536,032 B).
- Another process (a separate benchmark pinned to CPU 2, listed in
  environment.json) ran during both runs; the benchmark avoided CPU 2
  and its SMT sibling, but shared cache and memory bandwidth were not
  isolated.
- Copies and kernel calls per message are conceptual counts for this
  implementation, not measurements.
- UDP used the default 212,992 B receive buffer (net.core.rmem_max on
  this host); a larger buffer would likely change the 1,536,032 B
  loss figure (not tested).
- A first full run was discarded: the writer then stored the seq word
  with struct.pack_into, which zero-fills before packing, so the
  reader could see seq == 0 for a moment (DECISIONS.md D-154).

## Package condition: one whole frame package per tick (round 5)

Decisions: presentation/defense_2026/DECISIONS.md D-180 to D-188.

Purpose: the author found the p50/p99 charts hard to read and asked
for a simulation of the Python-to-Unity transfer of the whole
per-frame package, in plain terms. This condition answers "how long
does one whole package take to cross each transport, and how many
never arrive?" with one bar per transport. It adds to the benchmark;
the conditions above, results.csv, results_run2.csv, run_to_run.csv
and their charts are unchanged.

Command (writes only the files in the table below; about 4 minutes):

    /home/luo/anaconda3/bin/python transport_bench.py --package
    /home/luo/anaconda3/bin/python transport_bench.py --package-chart-only
    /home/luo/anaconda3/bin/python transport_bench.py --package --quick --out DIR   # smoke test

Method:

- Package: the 172 B person record plus one 1,536,032 B frame slot,
  1,536,204 B per tick, at 30 Hz; 200 warm-up + 1000 measured
  packages per transport per run; two runs; transports in the order
  shared memory, UDP, TCP within each run.
- Writer and reader are separate Python processes (spawn), writer on
  CPU 8, reader on CPU 10, parent on CPU 12, as above. The reader
  stands in for Unity; Unity itself was not measured.
- Time per package: writer time.monotonic_ns() immediately before the
  first byte of the package is written or sent, to reader
  time.monotonic_ns() once both parts have been read whole and carry
  the same package index (CLOCK_MONOTONIC, one host). Lost = a
  measured package the reader never completed.
- Shared memory: two /dev/shm files, one per record, each under its
  own seqlock (seq odd while writing, pre-packed 4-byte seq writes as
  in D-154). The writer writes the frame, then the record; the reader
  busy-waits on the record's seq, copies the record out and checks
  it, then copies the frame out and checks its seq and its package
  index.
- UDP: the frame in 26 datagrams of up to 60,000 B, then the record
  as a 27th datagram, each with the 8-byte header (package index,
  datagram index, count); default receive buffer 212,992 B. A package
  is complete when all 27 datagrams have arrived; it is given up when
  a datagram of a later package arrives first.
- TCP: one framed message per package (u32 length, record, frame),
  TCP_NODELAY, default buffers; blocking recv.

Outputs:

| File | Holds |
| --- | --- |
| results_package.csv | one row per transport per run: n (measured packages), delivered, lost, median_ms, min_ms, max_ms (over delivered packages), reader polling, receive buffer |
| results_package_run1.csv, results_package_run2.csv | the same rows split by run |
| raw_latencies/package_run1, package_run2 | package_<transport>.csv: index, t_write_start_ns, t_read_complete_ns, time_ms, delivered (1/0) |
| environment.json | key package_condition: clock, counts, CPU pins, load and busy processes at start and end, per-transport reader and writer metadata (retries, mismatches, UDP packages given up) |
| chart_transport_package.png | deck page 41: one bar per transport (median), whisker fastest to slowest, lost count under each bar; run 1 |

Results (results_package.csv; time from write start to read complete, ms):

| Transport | Run | Median | Fastest | Slowest | Lost of 1000 |
| --- | --- | ---: | ---: | ---: | ---: |
| Shared memory | 1 | 0.0586 | 0.0556 | 0.1569 | 0 |
| UDP | 1 | 0.3115 | 0.2328 | 0.3618 | 528 |
| TCP | 1 | 0.2946 | 0.1765 | 0.6332 | 0 |
| Shared memory | 2 | 0.0569 | 0.0549 | 0.1667 | 0 |
| UDP | 2 | 0.3130 | 0.2303 | 0.3742 | 668 |
| TCP | 2 | 0.2929 | 0.1931 | 0.5603 | 0 |

These are the idle-machine rerun of 2026-09-28 09:51 PDT (load
average 0.20 at start; no process above 20 % CPU, the
busy_processes() threshold in transport_bench.py, at the start or the
end of either run; environment.json package_condition).
Shared memory moved the typical package about five times faster than
TCP or UDP (0.0586 ms against 0.2946 and 0.3115 ms in run 1) and lost
none. Every delivered package on every transport arrived in under
0.64 ms, well inside the 33.3 ms frame interval. UDP lost 528 and 668
packages of 1000; the reader saw no torn or mismatched package on any
transport (environment.json: shared-memory retries 0, mismatched
parts 0).

An earlier run the same morning, while other deck work loaded the
machine, gave medians 0.0576 / 0.2934 / 0.2876 ms (shared memory /
UDP / TCP, run 1) and UDP losses of 248 and 203; those numbers were
replaced by this rerun and are kept only in DECISIONS.md.

Caveats (package condition):

- In the pipeline itself Unity reads only the records; the frame
  buffer carries images from the capture process to the Python
  branches (thesis Section 6.1.1). The package is the author's
  requested stress case, not a path the pipeline has.
- The shared-memory reader busy-waits; Unity polls once per rendered
  frame, which would add up to one frame interval of waiting and was
  not measured. The record size is the V3 person record (172 B); the
  thesis's Section 6.1.2 person record is 84 B.
- UDP loss varies widely between runs and is not explained by
  machine load: the idle rerun lost 528 and 668 packages of 1000,
  more than the earlier loaded run (248 and 203). The cause was not
  investigated (the benchmark was not tuned); the default 212,992 B
  receive buffer holds about one seventh of one package, so any
  reader delay drops datagrams. The count is an example, not a
  constant.
- One slot per record, not the pipeline's 8-slot frame ring; at 30 Hz
  the reader never fell a package behind (0 mismatches).
- Loopback only; Python endpoints on both sides; one workstation.

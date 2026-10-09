Current scope note (verified 2026-10-08): the benchmark scripts and
pinned outputs described below remain in the repository. Defence page
numbers in the round-4/round-5 descriptions refer to the retired
generated deck, not the final author deck adopted on 2026-10-06. Use
[deck_inventory.md](deck_inventory.md) and the
[presentation README](../presentation/defense_2026/README.md) for current
slide pointers. Benchmark measurements and their original conditions
are preserved; they were not rerun for this documentation correction.

Verified: 2026-09-28 (round-4 update)
Sources: Unity/Assets/Scripts/V3/V3PersonReceiver.cs, v3/replay/psv3.py, v1/realtime/person/realtime_person.py, v2/common/person_shm_v2.py, v1/aruco/send_scene_poses.py, v1/realtime/integration/realtime_integrate.py, v1/integration/send_integrated_scene.py, v2/integration/v2_integrate.py, v1/unity_bridge/send_landmarks.py, v1/kinematics/send_arm_angles.py, v1/kinematics/send_root_angles.py, v2/common/shm_ring.py, v3/dataset/phase4_realtime_e2e.txt, v1/realtime/REALTIME.md, .agent/DECISIONS.md, writing/v9/zh/src/Chapter_6_System_Integration.txt, presentation/defense_2026/experiments/transport_bench/README.md, presentation/defense_2026/DECISIONS.md D-149 to D-159 and D-154
Answers: how Python talks to Unity (shared memory, not sockets), the exact record layout and size of every packet type, the measured latency numbers behind those claims, and (round 4) a measured TCP/UDP/shared-memory comparison plus two unverified seqlock-write observations flagged during that work.

## Round-5 update: package condition (verified 2026-09-28)

Page 41 shows one whole 1,536,204 B package (person record + frame
slot) per 30 Hz tick. Idle rerun, run 1: shared memory 0.0586 ms
median (0.0556-0.1569), TCP 0.2946 (0.1765-0.6332), UDP 0.3115
(0.2328-0.3618) with 528 of 1000 lost; run 2 UDP lost 668. An earlier
run on a loaded machine lost 248 and 203, so the loss is not a load
effect and was not investigated (D-186). The package is a stress case:
Unity reads only the records in the pipeline (D-181).
Source: presentation/defense_2026/experiments/transport_bench/results_package.csv.

## Round-4 update: a measured transport comparison now exists (2026-09-28)

`presentation/defense_2026/experiments/transport_bench/` (D-149 to
D-159) measures TCP, UDP and shared memory head to head on this
workstation, loopback, Python endpoints, for the 172 B PSV3 person
record and the 1,536,032 B PSF1 frame slot at 30 Hz. Headline
(results.csv, run 1): shared memory has the lowest p50/p99 latency
and jitter for both sizes (172 B: 2.67/3.21 us vs 30.67/107.4 us UDP
and 37.97/120.8 us TCP; 1,536,032 B: 54.38/73.66 us vs 232.2/317.1 us
TCP and 239.8/268.1 us UDP), with no loss, against UDP's 4.55% loss
of the large frames at the default 212,992 B receive buffer. This
supports the pipeline's choice of shared memory (D-158), but is not
extended to the real Unity C# reader (polled once per rendered
frame, not measured) or to a flat-out writer, where a single-slot
mailbox starves (D-159). See experiments/transport_bench/README.md
and knowledge/experiments.md for the full method and caveats.

Two unverified seqlock-write observations surfaced while building
that benchmark (D-154), flagged for the author, not independently
tested here:
- `v2/common/shm_ring.py` (the PSF1 writer, lines 136-145) stores its
  slot seq and counter with `struct.pack_into` on the mapping.
  CPython's `struct.pack_into` zero-fills the target bytes before
  packing, so a concurrent reader can transiently read seq == 0
  ("stable, even") and accept a torn record; this was measured to
  actually happen in transport_bench's own writer before it switched
  to a pre-packed byte-slice write (300 paced 1.5 MB publishes
  produced 48 failed verifications in the discarded diagnostic run).
  Whether `shm_ring.py`'s separate `frame_idx` check makes a false
  accept unlikely in practice was not tested.
- `v3/replay/psv3.py` writes the even seq inside the same payload
  write as the data, at offset 4 before the data bytes, so the even
  seq can in principle become visible a few nanoseconds before the
  tail of the record is written. Not tested.

## Mechanism

Fixed-size binary records written into `/dev/shm` files via mmap,
guarded by a seqlock (an odd sequence number means "writer in
progress"; readers retry until they read the same even sequence
before and after the payload). Unity reads each record every frame
with `MemoryMappedFile`
(Unity/Assets/Scripts/V3/V3PersonReceiver.cs).

## Record table

| Magic | Size | /dev/shm path | Writer | Notes |
|---|---:|---|---|---|
| PSV3 | 172 B | v3_person | v3/replay/psv3.py | Format `<IIif24f13f7Bx`; ~30 fps. Confirmed: v3/replay/psv3.py line 33 `FMT = "<IIif24f13f7Bx"`, line 35 `assert SIZE == 172`. |
| PSR1 | 84 B | rt_person | v1/realtime/person/realtime_person.py | Format `<IIif3f13fH2x`; line 64 `assert PACKET_SIZE == 84`. |
| PSR2 | 84 B | rt_person_v2 | v2/common/person_shm_v2.py | line 24 `assert PSR2_SIZE == 84`. |
| PSB2 | 44 B | aruco_object / rt_object / rt_object_v2 | v1/aruco/send_scene_poses.py (offline) and v1/realtime/object/realtime_object.py, v2/object/v2_object.py (real-time; same 44 B layout, confirmed by realtime_object.py comment "PSB2 (44 B, same layout the offline sender uses)") | Format `<IIif3f3fH2x` (realtime_integrate.py). |
| PSB3 / PSB1 | 100 B | aruco_scene | v1/aruco/send_scene_poses.py | Comment: "PSB3 (100 B): magic u32 'PSB3', then desk/wall/camera ...". |
| PSI1 | 108 B | integrated_scene | v1/integration/send_integrated_scene.py | Format `<IIif3f13f3f3fHH` (realtime_integrate.py line 48-50, assert 108). |
| PSI2 | 112 B | integrated_scene_v2 | v2/integration/v2_integrate.py | Format `<IIif3f13f3f3fHHHH`, assert 112 (lines 91-94); 30 ticks/s. |
| PSE1 | 180 B | pose_stream | v1/unity_bridge/send_landmarks.py | line 33 `PACKET_SIZE = 180`. |
| PSA5 | 72 B | pose_arm | v1/kinematics/send_arm_angles.py | line 37 `PACKET_SIZE = 72`. |
| PSA1 | 32 B | pose_angles | v1/kinematics/send_root_angles.py | line 30 `PACKET_SIZE = 32`. |
| PSF1 | ring, 8 slots x 1,536,032 B + 128 B header | rt_frames | v2/common/shm_ring.py | HDR_SIZE = 128 (line 54); DEFAULT_NSLOTS = 8 (line 68); slot_size = SLOT_HDR_SIZE(32) + width*height*3 + 2*width*height (line 97), which for the project's 640x480 frames gives 32 + 921600 + 614400 = 1,536,032 B (arithmetic confirmed from the formula; 640x480 is the project's standard camera resolution used throughout, not independently re-derived from this file). |

## Measurements

- `v3/dataset/phase4_realtime_e2e.txt`: publish stage 0.02 ms
  p50/p95/p99/max; total per frame p99 10.65 ms at 28.7 fps sustained
  over 883 frames (line 2: "frames 883, person found 883, wall 30.7 s
  (28.7 fps sustained)"; line 11: "budget check: total p99 10.65 ms
  vs 33.3 ms -> PASS").
- `v1/realtime/REALTIME.md`: shm write 0.01 ms (p50/p95/p99, line 92);
  sustained end-to-end rate 25.7 fps (line 100). Detector timing
  (Pipeline B, object, APRILTAG refine): p50/p95/p99 12.2/13.2/14.5 ms.

## UDP fallback

The only socket-based transport in the transport code is the UDP
fallback in `v1/unity_bridge/send_landmarks.py`
(`--transport udp`, default host/port 127.0.0.1:9750, same 180-byte
packet format as the shm path). Never measured for latency (no
benchmark file references it). Confirmed by send_landmarks.py lines
4-19 (transport docstring) and 94-120 (argparse `--transport`,
`--port` default 9750).

## Why shared memory over UDP

`.agent/DECISIONS.md`:
- Line ~268 (2026-07-12 entry): "Shared memory (/dev/shm + seqlock)
  chosen over UDP as default per user preference and because it is
  the exact transport the real-time variant needs; UDP kept as
  fallback."
- Line ~462 (2026-08-03 entry): records that the thesis text states
  the transport choice explicitly, "both transports implemented,
  shared memory default over UDP, UDP kept as drop-in", and that the
  shared-memory diagram (Figure 5.2) is drawn from the real PSI1
  108-byte layout.

## Thesis reference

Chapter 6, Section 6.1.2, Table 6.1 states the packet sizes (thesis
text file confirmed to exist and mention Table 6.1:
writing/v9/zh/src/Chapter_6_System_Integration.txt; exact table cell
values were not re-transcribed here -- read that file or the docx
for the thesis-published numbers).

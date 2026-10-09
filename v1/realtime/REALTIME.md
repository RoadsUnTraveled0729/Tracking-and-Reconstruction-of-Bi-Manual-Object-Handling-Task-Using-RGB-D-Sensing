# Real-time phase — bag → Unity live

Everything in this phase lives under `realtime/` — the OFFLINE pipelines
(`mediapipe/`, `kinematics/`, `aruco/`, `integration/`), the major part of
the thesis, are untouched and are only *read* from here (their modules,
outputs, and the frozen calibration). Layout mirrors the pipeline split:
`person/` (A-side), `object/` (B-side), `integration/` (the only code
reading both), `bench/` (the GPU-vs-CPU study), `dataset/` (pinned
artifacts), `output/` (regenerable, gitignored).

The offline pipeline made real-time: the same recording
(`recording_20260224_083945.bag`) played back at recorded pacing
(`playback.set_real_time(True)`) as a live-camera stand-in, processed
frame-by-frame with CAUSAL-only filtering, and streamed to the unchanged
Unity receiver over the existing shared-memory seqlock transport. Also:
the measured answer to "vectorize? threads? GPU or CPU?" — benchmarked,
not assumed (`realtime/bench/bench_solver.py`).

## 1. Architecture (3 processes + Unity)

```
bag ──► [A] realtime/person/realtime_person.py ──► /dev/shm/rt_person   (PSR1, 84 B)
bag ──► [B] realtime/object/realtime_object.py ──► /dev/shm/rt_object   (PSB2, 44 B)
        [I] realtime/integration/realtime_integrate.py  (reads BOTH — the only layer
            allowed to): /dev/shm/aruco_scene (PSB3, once, from the frozen
            calibration) + /dev/shm/integrated_scene (PSI1, per frame)
Unity:  IntegratedSceneReceiver — UNCHANGED (same PSB3 + PSI1 contract)
```

- Pipelines A and B remain fully independent processes (no shared code or
  data; the One-Euro class is duplicated into `aruco/` on purpose).
- **PSR1** = PSI1's person half (frame, time, pelvis, 13 PSA5 angles,
  per-joint live mask). The object side reuses PSB2 verbatim.
- **Start barrier** (`--sync-file`): each pipeline finishes init (MediaPipe
  model load ≈ 0.6 s), touches a ready file, and opens the bag only when
  the launcher releases the barrier — emulating one shared camera.
  Without it the two playbacks start at different wall times: measured
  **567 ms** person-vs-object skew; with it, skew p50 0 ms / max 33.4 ms
  (= exactly one frame, the pairing quantum of two async 30 fps
  processes). The merger measures and reports skew every run.
- Launcher: `realtime/integration/run_realtime.py` (spawns A + B, runs the merger,
  one Ctrl-C teardown; `--dump` writes the validation CSVs, `--profile`
  prints per-stage latency, `--start-delay` holds the barrier so a screen
  capture can start before playback).

## 2. Causal filter substitutions (and their measured cost)

Offline zero-phase filtering is illegal live (D1 §10). Substitutions:

| offline (zero-phase) | real-time (causal) |
|---|---|
| centered Hampel despike | trailing-window Hampel; reject ⇒ missing (solver fallback holds) |
| interior gap interp + edge-fill | not needed — hold-last is the online semantics (declared via live mask) |
| Butterworth 3 Hz filtfilt (landmarks) | One-Euro per axis (min_cutoff 1 Hz, beta 1) |
| Savitzky-Golay + rolling chordal mean (object) | One-Euro position + complementary geodesic rotation filter `R_f ← R_f·exp(α·log(R_fᵀR_meas))`, α from a 3 Hz cutoff |

Two causal-only pitfalls found and fixed (they do not exist offline):

1. **Rejection lockout**: a trailing-window despike whose rejected samples
   don't enter the window rejects *everything* after real fast motion (the
   window goes stale). Object live coverage collapsed 877 → 541 frames.
   Fix: accept + re-seed after 3 consecutive rejections (a "spike" that
   persists is real motion). Coverage: 863/899.
2. **Motion-onset false rejects**: a trailing window has MAD ≈ 0 at the
   onset of motion, so the offline 20 mm absolute floor flags genuine
   acceleration; live floor is 35 mm (still catches the 54 mm-class depth
   spikes). All-joints-live: 92.4 % → 97.3 % of frames.

Tuning cost of causality, measured against the offline solve on the same
bag (`realtime/integration/validate_realtime.py`, ALL PASS, pinned in
`realtime/dataset/validate_realtime_output.txt`):

- angles: worst joint-group median **0.64°**, p95 3.24° (left shoulder,
  the occlusion-prone side); root median 0.24°;
- lag: cross-correlation peak at **3 frames (100 ms)** — was 9 frames with
  the offline One-Euro tuning (min_cutoff 0.05 Hz), hence the 1 Hz retune;
- pelvis: median 2.4 mm; object position vs the offline filtered track:
  median 6.2 mm, p95 13.9 mm (causal vs zero-phase smoothing);
- honesty preserved: object live 863 vs 877 offline detections; person
  97.3 % all-13-joints live after warm-up.

## 3. Latency budget (per-stage, full run, both processes concurrent)

Pipeline A (person), ms:

| stage | p50 | p95 | p99 |
|---|---:|---:|---:|
| depth→color align | 2.3 | 2.5 | 2.7 |
| MediaPipe (GPU, heavy) | 9.2 | 22.1 | 27.6 |
| deproject + causal filter | 0.5 | 0.6 | 0.7 |
| 13-angle solve | **0.2** | 0.2 | 0.3 |
| shm write | 0.01 | 0.01 | 0.01 |
| **total** | 12.2 | 24.9 | **30.7** |

Pipeline B (object), ms: detect (APRILTAG refine) 12.2 / 13.2 / 14.5;
IPPE + filter + map ≈ 0.3; **total p99 14.9**.

Both fit the 33.3 ms / 30 fps budget (person p99 headroom ≈ 2.6 ms —
MediaPipe inference is the whole risk; `--model full` buys ~3× if it ever
tightens). Sustained end-to-end rate 25.7 fps — the limiter is
librealsense playback pacing of this bag (both processes report the
identical 35.0 s for the 30 s recording), not compute.

## 4. Vectorize? Threads? GPU? — the measured answers

`realtime/bench/bench_solver.py` (figure + CSV pinned in
`realtime/dataset/bench_solver.{png,csv}`), all arms verified equal to
the scalar reference ≤ 1e-10° first. Per-frame latency at **N = 1** (the
real-time case) and per-frame cost at batch 100k (the offline case):

| implementation | N=1 (µs) | N=100k (µs/frame) |
|---|---:|---:|
| numba `@njit` kernel | **0.6** | 0.20 |
| numpy vectorized | 91 | 0.53 |
| scalar loop (baseline) | 99 | ~87 |
| numpy + 2 threads (L/R arms) | 151 | 0.33 |
| torch CPU | 262 | 0.18 |
| torch CUDA (+transfer) | 885 | **0.03** |
| CuPy (+transfer) | 1511 | 0.16 |

Deployed solver (clarified 2026-07-31): the live person pipeline calls
`ChainFallbackSolver.solve` (kinematics/occlusion.py), i.e. the SAME
per-frame scalar solver (shoulder.py / root_frame.py) as offline
Pipeline A — the "scalar loop" arm above (99 µs at N=1; 0.2 ms measured
in-pipeline under concurrent load). `shoulder_vec.py` (numpy-vec) is the
verified batch tool, deployed nowhere in the live loop.

Conclusions (quoted from measurement):

1. **Vectorization pays offline, not per frame.** numpy-vec is ~170×
   the scalar loop at batch ≥ 1k, but at N=1 python/numpy call overhead
   dominates (91 µs ≈ the scalar loop). The batch solver
   (`realtime/bench/shoulder_vec.py`, selftest 10,785 frames ≤ 9.6e-14°) is
   the right tool for offline datasets; the real-time loop's solve is
   0.2 ms either way — 0.6 % of the frame budget.
2. **L/R-arm threads do not help the solve** (151 vs 91 µs at N=1):
   sub-100 µs numpy work is smaller than thread handoff. Where threads DO
   help: OpenCV releases the GIL, so *frame-level* threading of the ArUco
   stage measured 11.9 → 6.2 ms/frame (2 threads) — kept out of the demo
   (adds a frame of latency; serial already fits) but noted for headroom.
   The parallelism that actually matters is **process-level**: A and B
   run concurrently on separate cores by design.
3. **GPU loses the real-time case by 3–4 orders of magnitude** (kernel
   launch + host↔device transfer ≈ 1 ms per call vs 0.6–91 µs on CPU) and
   wins only for large offline batches (crossover ≈ 10⁴ frames; at 100k
   torch-CUDA is ~7× numba). The GPU's correct real-time job here is the
   one it already has: MediaPipe inference. **Recommendation: CPU for the
   solve/filter math in real time; GPU only for batch reprocessing.**

## 5. Validation & artifacts

`realtime/integration/validate_realtime.py` — 11 checks, ALL PASS: dump coverage
(899/899 both), causal-vs-offline angle/pelvis/object bounds (§2), lag
≤ 4 frames, live-coverage bounds, per-frame compute p99 < 33.3 ms both
pipelines, PSI1 well-formed.

Unity live demo: `realtime/dataset/unity_realtime_224.mp4` +
`rt_still.png` — captured with the single-invocation procedure (FINDINGS
2026-07-23), lead trimmed from the barrier-file mtime; frame-diff shows
motion from the first second. Dumps pinned as `rt_person_dump.csv` /
`rt_object_dump.csv`.

## 6. Reproduce

```bash
cd realtime
python integration/run_realtime.py --dump --profile   # full pass, ~35 s
python integration/validate_realtime.py               # ALL PASS
python bench/shoulder_vec.py --selftest               # vectorized == scalar
python bench/bench_solver.py                          # the study (needs cupy/torch)
```

Environment note: GPU study deps installed 2026-07-24 — `torch
2.7.1+cu126`, `cupy-cuda12x 13.6.0` (cupy 14.x requires numpy ≥ 2, which
breaks mediapipe; numpy stays pinned 1.26.4).

Hardware (the machine every timing in this file was measured on, read
2026-07-31): AMD Ryzen 9 7950X (16 cores / 32 threads), 64 GB RAM,
NVIDIA GeForce RTX 3080 (10 GB). The GPU's only live job is MediaPipe
inference; all solver arithmetic runs on the CPU.

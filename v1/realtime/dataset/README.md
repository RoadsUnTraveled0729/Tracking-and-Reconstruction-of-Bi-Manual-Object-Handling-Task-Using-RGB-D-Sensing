# Real-time phase verified dataset (2026-07-24, recording 20260224)

Pinned artifacts of the real-time phase (../REALTIME.md). Regenerate with
`python ../integration/run_realtime.py --dump --profile` then
`python ../integration/validate_realtime.py` (fresh outputs land in
`../output/`, gitignored; the copies here are the validated pins). The
OFFLINE artifacts these were compared against stay in
`integration/dataset/` and `kinematics/dataset/`, untouched.

| File | What it is |
|---|---|
| `unity_realtime_224.mp4` / `rt_still.png` | the LIVE demo: bag played at recorded pacing through the 3-process real-time stack into the unchanged Unity receiver; motion from the first second (single-invocation capture, barrier-timed trim). |
| `rt_person_dump.csv` / `rt_object_dump.csv` | per-frame real-time outputs (angles/pelvis/mask + compute ms; object unity pose + live) used by the validator. |
| `validate_realtime_output.txt` | the 11 checks, ALL PASS: causal-vs-offline bounds (worst joint median 0.64°, lag 3 frames, object 6.2 mm), coverage, 30 fps budgets, PSI1 integrity. |
| `bench_solver.csv` / `bench_solver.png` | the GPU-vs-CPU / vectorization study (`../bench/bench_solver.py`): per-frame latency at N=1 (numba 0.6 µs, numpy 91 µs, GPU 0.9–1.5 ms — CPU wins real time) and batch throughput (GPU crossover ≈ 1e4 frames); ArUco stage serial 11.9 ms vs frame-level 2-thread 6.2 ms. All arms verified equal to the scalar solver ≤ 1e-10° before timing; the batch solver itself is `../bench/shoulder_vec.py` (selftest: 10,785 frames, ≤ 9.6e-14°). |

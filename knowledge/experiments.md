Current scope note (verified 2026-10-08): the benchmark scripts and
pinned outputs described below remain in the repository. Defence page
numbers in the round-4/round-5 descriptions refer to the retired
generated deck, not the final author deck adopted on 2026-10-06. Use
[deck_inventory.md](deck_inventory.md) and the
[presentation README](../presentation/defense_2026/README.md) for current
slide pointers. Benchmark measurements and their original conditions
are preserved; they were not rerun for this documentation correction.

Verified: 2026-09-28
Sources: presentation/defense_2026/experiments/{marker_bench,transport_bench,filter_metrics}/README.md, presentation/defense_2026/DECISIONS.md D-134 to D-168
Answers: the purpose, command, outputs, headline numbers, caveats and decision range of each of the three round-4 Q&A experiments (marker_bench, transport_bench, filter_metrics), committed under presentation/defense_2026/experiments/.

## Round-5 additions (verified 2026-09-28)

transport_bench package condition: `python transport_bench.py
--package` (about 4 min, idle machine) then `--package-chart-only`.
One package = 172 B person record + 1,536,032 B frame slot at 30 Hz,
200 warm-up + 1000 measured, two runs. Idle rerun 2026-09-28 09:51
(results_package.csv): run 1 shm 0.0586 ms (0.0556-0.1569), UDP 0.3115
(0.2328-0.3618) lost 528, TCP 0.2946 (0.1765-0.6332); run 2 shm 0.0569,
UDP 0.3130 lost 668, TCP 0.2929. The earlier loaded run lost 248/203,
so UDP loss is not a load effect (D-186). D-180 to D-188.

Typeset filter equations: `python equations/typeset_filters.py`
renders nine ts_ keys with matplotlib 3.9.2 mathtext (STIX, 11.65 pt,
600 dpi) from v1/mediapipe/filter_landmarks.py (sha256 pinned);
`--check` re-renders in memory and exits 1 on any difference.
filter_metrics charts.py `--panel` draws the 6.61 x 5.00 in charts for
pages 48-49. D-189 to D-201.

All three experiments are self-contained, committed, reproducible
Python scripts under `presentation/defense_2026/experiments/`, each
with its own README.md (the primary source) and its own decision
range in DECISIONS.md. They back the six numeric round-4 hidden
pages (36-40, 47-48); see deck_inventory.md and media_inventory.md
for exactly which page uses which output file.

## marker_bench: ArUco vs AprilTag on this workstation

Purpose: answers "why ArUco and not AprilTag?" with a measurement.
Synthetic markers with known corners are composited onto real
640x480 R6b frames, degraded with blur and noise, and timed/scored
against the pinned ArUco configuration (OpenCV ArucoDetector,
DICT_5X5_50, CORNER_REFINE_APRILTAG) and AprilTag 3 (pupil-apriltags,
tag36h11, decimate 1 and 2), plus OpenCV's own DICT_APRILTAG_36h11
dictionary and an unrefined-ArUco reference.

Command:

    cd presentation/defense_2026/experiments
    /home/luo/anaconda3/bin/python -m venv .venv
    .venv/bin/pip install -r marker_bench/requirements.txt
    cd marker_bench
    ../.venv/bin/python marker_bench.py            # full run, about 31 min

Outputs: results.csv (one row per detector x side x tilt x blur x
noise, 810 rows: 6 sizes x 3 tilts x 3 blur x 3 noise x 5 detectors),
summary.csv (per detector/size, aggregated over the other 27
conditions), chart_marker_bench.png (2466x1110, deck page 37),
environment.json, run.log.

Headline numbers (summary.csv, AMD Ryzen 9 7950X, single thread,
640x480): pinned ArUco 26.6 ms/frame at 48 px vs AprilTag 3 3.5 ms
(decimate 2) / 14.4 ms (decimate 1); the CORNER_REFINE_APRILTAG step
alone costs 18.2 ms of the ArUco total (8.4 ms without it). Debiased
corner error at 48 px: ArUco pinned 0.137 px, AprilTag 3 0.095/0.092
px; at 96 px all four detectors lie within 0.069-0.074 px. Every
AprilTag-quad-fitting detector returns corners shifted by about
+0.46 to +0.50 px in x and y before debiasing. Detection reaches
100% for all four from 64 px up.

Caveats: single-threaded, one workstation; synthetic composite (no
lens distortion, no motion blur, no lighting gradient); additive
noise sigma 4/8 is stronger than the D435's visible noise (not
measured); corner error is image-space only, no pose error measured;
transport_bench ran concurrently on other cores during this run.

Decisions: D-134 to D-148 (constants, method, and the D-148 verdict
on "similar performance, AprilTag slower but more accurate" --
UNCERTAIN, partly supported and partly contradicted by both the
measurement and the literature; see knowledge/marker_literature.md
and knowledge/marker_facts.md).

## transport_bench: TCP vs UDP vs shared memory

Purpose: answers "why does the pipeline use shared memory?" by
measuring what the two socket alternatives would cost for the same
two message sizes the pipeline actually uses: the 172 B PSV3 person
record and one 1,536,032 B PSF1 frame slot.

Command:

    /home/luo/anaconda3/bin/python transport_bench.py            # 2 runs + charts

Run time about 21 minutes (1,242 s wall) for two runs, each 8 paced
conditions (2,200 messages at 30 Hz) plus 6 unpaced conditions (5 s
flat out).

Outputs: results.csv / results_run2.csv (14 conditions x run: n,
p50/p90/p99/max latency, jitter, throughput, loss/skip, seqlock
retries, duplicates), run_to_run.csv (repeatability), raw_latencies/
(per-message CSVs), environment.json,
chart_transport_latency.png (deck page 39),
chart_transport_throughput.png (deck page 40), SLIDE_TEXT.md.

Headline numbers (results.csv, run 1): 172 B at 30 Hz p50/p99 --
shared memory 2.67/3.21 us, UDP 30.67/107.4 us, TCP 37.97/120.8 us.
1,536,032 B at 30 Hz p50/p99 -- shared memory 54.38/73.66 us, TCP
232.2/317.1 us, UDP 239.8/268.1 us. UDP lost 4.55% of the large
frames at 30 Hz with the default 212,992 B receive buffer (0.0102%
unpaced). A single-slot shared-memory mailbox delivered 0 of the
1,536,032 B messages under a flat-out writer (30,081.6 publishes/s),
a property of a single-slot seqlock, not of shared memory generally
-- the pipeline's frame path uses a multi-slot ring instead.

Caveats: loopback only, one machine, Python endpoints on both sides
(the real Unity C# reader, polled once per rendered frame, was not
measured); shared-memory rows busy-wait (burns one core), socket
readers block in the kernel; another benchmark process ran
concurrently on a different core; UDP used the default receive
buffer (a larger buffer was not tested); a discarded first full run
found a seqlock zero-fill hazard, fixed before the committed run
(D-154).

Decisions: D-149 to D-159 (constants, method, and the D-158 verdict
scoped to what was measured; D-159, UNCERTAIN, explicitly does not
extend the conclusion to the Unity reader or a flat-out writer). See
knowledge/transport_facts.md for the two unverified seqlock-write
observations flagged during this work (D-154).

## filter_metrics: offline and causal smoothers on the R6b right wrist

Purpose: measured backing for "why Butterworth offline" and "why One
Euro in real time". Runs nine candidate filters/smoothers (despiked
raw; Savitzky-Golay 9/2; median 9; offline Butterworth 3 Hz and 2 Hz
filtfilt; causal Butterworth 3 Hz forward-only; One Euro at two
parameter sets -- 0.05 Hz/beta 1 the offline/film default, 1 Hz/beta
1 the live CausalLandmarkFilter default; EMA alpha 0.3) on one
pinned recording (R6b right wrist, frames 25-549 and 640-899, 785
evaluated frames) and measures shake, fast-motion deviation and lag.

Command:

    /home/luo/anaconda3/bin/python presentation/defense_2026/experiments/filter_metrics/filter_metrics.py

Runtime a few seconds; two consecutive runs give byte-identical
outputs (sha256 checked).

Outputs: results.csv (one row per candidate x axis: x, y, z, norm),
summary.csv (norm/3-D rows only), run_info.json,
chart_filter_offline.png (deck page 47),
chart_filter_realtime.png (deck page 48), SLIDE_TEXT.md.

Headline numbers (summary.csv, 3-D norm, 785 frames): despiked raw
shake 6.38 mm. Offline (all lag 0 frames): Butterworth 3 Hz shake
2.86 mm / deviation 6.53 mm (lowest shake of the compared 9-frame/3 Hz
candidates); Savitzky-Golay 3.29/5.64 mm; median 3.51/7.49 mm;
Butterworth 2 Hz 2.54/7.73 mm. Causal: Butterworth 3 Hz forward
2.88 mm shake / 142.28 ms lag; One Euro 1 Hz 2.48 mm / 85.39 ms; One
Euro 0.05 Hz 2.08 mm / 186.79 ms; EMA 0.3 2.86 mm / 54.89 ms -- One
Euro 1 Hz and EMA both beat causal Butterworth on shake and lag.

These values DIFFER from the unscripted prose table in
thesis/A1_acquisition_filtering.md (lines 165-181; for example shake
raw 10.2 mm there vs 6.38 mm here, Butterworth 3 Hz 1.9 mm there vs
2.86 mm here); the shake ranking agrees between the two but the
deviation ranking does not, and the prose table's data set, speed
threshold and averaging are not recorded, so the cause of the
difference is not established. Do not quote the prose table for a
reproducible number -- see knowledge/filter_facts.md.

Caveats: one recording, one landmark, 26 s of evaluated data; not a
population or accuracy result (no ground truth for the wrist here);
shake counts genuine motion as well as noise, so a filter that lags
or flattens motion scores a lower shake; causal deviation is
dominated by lag, not noise.

Decisions: D-160 to D-168 (metric definitions, percentile and window
choices, and the causal-Butterworth seeding choice; several UNCERTAIN
pending author review, notably D-161's fast-motion percentile and
D-167's choice of which One Euro setting the excerpt plots).

## Also see

The AKC comparison (Kwok, Koenig and Hu's Arm Kinematic Correction
paper re-implemented and run against our recovery, eval/akc_comparison/)
is a separate sub-study, not one of the three round-4 Q&A experiments
above; see knowledge/akc_comparison.md.

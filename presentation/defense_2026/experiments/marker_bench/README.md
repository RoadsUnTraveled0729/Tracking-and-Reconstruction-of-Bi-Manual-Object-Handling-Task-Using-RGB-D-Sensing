# marker_bench: ArUco vs AprilTag on this workstation

Decisions: presentation/defense_2026/DECISIONS.md D-134 to D-148

## Purpose

Answers the defence Q&A question "why ArUco and not AprilTag?" with a
measurement instead of recollection. Synthetic markers with known
corners are composited onto real 640x480 frames of the R6b recording,
degraded with blur and noise, and passed to:

| key | detector | marker |
| --- | --- | --- |
| aruco_5x5 | OpenCV 4.10 ArucoDetector, DICT_5X5_50, default parameters + CORNER_REFINE_APRILTAG (the pinned v1 setting, v1/aruco/extract_aruco_poses.py) | 5x5 id 1 |
| cv_apriltag36h11 | the same OpenCV detector and settings, DICT_APRILTAG_36h11 | tag36h11 id 1 |
| pupil_dec2 | AprilTag 3 C library via pupil-apriltags, tag36h11, library defaults (quad_decimate 2.0) | tag36h11 id 1 |
| pupil_dec1 | as above with quad_decimate 1.0 | tag36h11 id 1 |
| aruco_5x5_norefine | OpenCV ArucoDetector, DICT_5X5_50, all defaults (no corner refinement); timing and accuracy reference, not in the brief | 5x5 id 1 |

cv_apriltag36h11 runs the ArUco detector on AprilTag bit patterns: it is
a dictionary comparison, not a detector comparison. Only pupil_dec2 and
pupil_dec1 exercise the AprilTag detector.

## Commands

    cd presentation/defense_2026/experiments
    /home/luo/anaconda3/bin/python -m venv .venv
    .venv/bin/pip install -r marker_bench/requirements.txt
    cd marker_bench
    ../.venv/bin/python marker_bench.py            # full run, about 31 min
    ../.venv/bin/python marker_bench.py --quick    # 3 s smoke run, writes nothing
    ../.venv/bin/python marker_bench.py --plot-only

The background frames are read from /tmp/defense_2026_causal/camera
(cam_000000.jpg ... cam_000898.jpg); regenerate them first if /tmp was
cleared. The run pins itself to logical core 2 and sets
cv2.setNumThreads(1), pupil-apriltags nthreads=1 and OMP/OPENBLAS/MKL
threads 1, so every number is single-thread.

## Outputs

- results.csv: one row per detector x side (24, 32, 48, 64, 96, 128 px)
  x tilt (0, 30, 45 deg) x blur sigma (0, 0.8, 1.5 px) x noise sigma
  (0, 4, 8 grey levels); 50 frames each. Columns: detection_rate,
  corner_err_mean_px / _p95_px (raw, against the true corners in the
  pixel-centre convention), corner_bias_x/y_px (mean signed offset),
  corner_err_debiased_mean_px / _p95_px (after removing that constant
  offset), time_median_ms / time_p95_ms (150 timings: 50 frames x 3
  repetitions), other_detections_per_frame.
- summary.csv: per detector and side, aggregated over the 27 other
  conditions (rules in write_summary() in marker_bench.py).
- chart_marker_bench.png: 2466x1110, black background. Left: median
  time per frame with a band to p95. Right: debiased corner error; point
  area = detection rate; rates at 24 and 32 px in the text box.
- environment.json: CPU, versions, thread settings, affinity, load
  average, the 50 frames used, the measured marker grey levels.
- run.log: console log of the run.

## Results (summary.csv, AMD Ryzen 9 7950X, one thread, 640x480)

1. Speed: median detection time per frame, all 27 conditions, is 26.6 ms
   for the pinned ArUco (48 px) against 3.5 ms for AprilTag 3 at its
   default decimate 2 and 14.4 ms at decimate 1; the 36h11 dictionary
   in the OpenCV detector costs the same as 5x5 (26.6 ms).
2. The pinned ArUco cost is mostly the CORNER_REFINE_APRILTAG step: the
   same detector without refinement takes 8.4 ms at 48 px.
3. Corner error with the constant offset removed, at 48 px: ArUco
   pinned 0.137 px, 36h11 through OpenCV 0.160 px, AprilTag 3 0.095 px
   (decimate 2) and 0.092 px (decimate 1); at 96 px all four lie
   between 0.069 and 0.074 px. ArUco without refinement: 0.978 px at
   48 px.
4. Detection: all four reach 100 % from 64 px up; at 24 px ArUco pinned
   78 %, AprilTag 3 decimate 1 77 %, decimate 2 52 %, 36h11 through
   OpenCV 30 %.
5. Every detector that uses AprilTag quad fitting returns corners
   shifted by about +0.46 to +0.50 px in x and y (corner_bias columns);
   raw corner error is therefore 0.65 px (ArUco pinned, 96 px) and
   0.71 px (AprilTag 3, 96 px), dominated by that offset.

Noise dependence (results.csv, 48 px, median over tilt and blur): the
pinned ArUco takes 10.9 ms with no added noise, 26.6 ms at sigma 4 and
31.3 ms at sigma 8; AprilTag 3 decimate 2 takes 2.8, 3.5 and 3.8 ms.
The 10.9 ms noise-free figure is consistent with the live pipeline's
12.2 ms p50 (v1/realtime/REALTIME.md line 95).

## Caveats

- The transport benchmark (experiments/transport_bench) ran
  concurrently on other cores during this run (it started 07:28 by its
  environment.json; this run took 1822 s and finished at 07:56). The
  detectors are interleaved per image, so relative comparisons hold;
  absolute times may be slightly affected.
- Synthetic composites: a rendered marker (4x supersampled, grey levels
  50/209 measured from the real printed markers) pasted onto real
  frames; no lens distortion, no motion blur, no lighting gradient
  across the marker. Real markers in the frames are avoided (paste box
  kept 12 px away from every real marker the pinned detector finds);
  the real 5x5 markers still count in aruco_5x5 timings and appear as
  other_detections_per_frame = 3 for the 5x5 detectors.
- Single thread on one core of this workstation; absolute times do not
  transfer to other CPUs or to multi-threaded use.
- Additive Gaussian noise of sigma 4 and 8 is stronger than the D435
  colour stream's visible noise in these frames (not measured); it
  inflates the OpenCV times far more than the AprilTag 3 times.
- The corner error is image-space only; pose error was not measured.
- The debiased error removes one constant 2-D offset per condition; the
  raw error is what a user of each library actually gets.
- The 5x5 marker has 7 modules across and tag36h11 has 8, so at equal
  side the AprilTag modules are 12.5 % smaller; this is part of the
  family, not a rendering error.

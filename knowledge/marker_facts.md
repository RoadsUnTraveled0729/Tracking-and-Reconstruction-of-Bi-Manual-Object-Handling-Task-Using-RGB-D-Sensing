Verified: 2026-09-28 (round-4 update)
Sources: v1/aruco/extract_aruco_poses.py, v1/aruco/frames.py, v1/realtime/object/realtime_object.py, v2/object/v2_object.py, v2/calibration/live_calibrate.py, v1/realtime/bench/bench_solver.py, eval/common/marker_size.py, eval/gt/scale_correction.py, eval/DECISIONS.md, .agent/FINDINGS.md, v1/ARUCO_MODEL.md, thesis/B1_aruco_scene.md, .agent/DECISIONS.md, v1/realtime/REALTIME.md, writing/v9/references.md, eval/recordings_archive/README.md, presentation/defense_2026/experiments/marker_bench/README.md, knowledge/marker_literature.md
Answers: the pinned ArUco detector configuration, the marker size table and the 45 mm rescale, the evidence for corner-refinement choice, detector timing, and the status of AprilTag in this repository (present in test bags and OpenCV; as of round 4, benchmarked against ArUco on this workstation and against the published literature, though still never used in the pipeline).

## Pinned detector configuration

- Dictionary: `DICT_5X5_50`.
- `cv2.aruco.DetectorParameters()` at default except
  `cornerRefinementMethod = cv2.aruco.CORNER_REFINE_APRILTAG`.
- `cv2.aruco.ArucoDetector`.
- Pose: `cv2.solvePnPGeneric(..., flags=cv2.SOLVEPNP_IPPE_SQUARE)`
  with a lobe-separation ambiguity policy.

Confirmed at v1/aruco/extract_aruco_poses.py lines 39-40 (dict) and
274-282 (solvePnPGeneric/IPPE_SQUARE, lobe-separation tiebreak via
`tracker.choose`), and lines 325-331 (`CORNER_REFINE_APRILTAG` with
the measured-scatter comment).

Same detector settings (dictionary, corner refinement) confirmed
present in:
- v1/realtime/object/realtime_object.py (line 153-154)
- v2/object/v2_object.py (line 79-80)
- v2/calibration/live_calibrate.py (line 101-102)
- v1/realtime/bench/bench_solver.py (lines 461-464, DICT_5X5_50 + CORNER_REFINE_APRILTAG)

## Markers (v1/aruco/frames.py MARKERS, lines 26-30)

| id | role | declared size (detector, PnP) |
|---:|---|---:|
| 0 | wall | 0.150 m |
| 2 | desk | 0.050 m |
| 1 | object | 0.050 m |

Printed marker size: 45 mm (user-confirmed 2026-09-01 and
2026-09-25, per AGENTS.md Standing project constraints).

`eval/common/marker_size.py` rescales the desk (id 2) and object
(id 1) markers from the frozen 0.050 m declaration to 0.045 m
(45 mm) -- a factor of 0.9 -- before ground-truth calibration in
`eval/gt/scale_correction.py`. Confirmed: marker_size.py lines 41-46
(`SIZES_M = {1: 0.045, 2: 0.045, ...}`, comment "USER ASSUMPTION
2026-08-25 (E-009)"; `DECLARED_M = {0: 0.150, 1: 0.050, 2: 0.050}`).
The source-code assumption comments are historical; the user-confirmed
45 mm print is the current fixed constraint. Do not reopen it
(Standing project constraints).

## Corner-refinement evidence (prose only; no script reproduces this)

With the default (no refinement), ArUco corners lock to integer
pixels, producing a false-stability artifact: a static desk marker
showed 0.00 mm frame-to-frame scatter. `CORNER_REFINE_APRILTAG`
reveals the true subpixel scatter: desk 0.4 mm / 0.17 deg, and
improves the far wall's position scatter from 37 mm to 7 mm.

Confirmed present at:
- .agent/FINDINGS.md lines 51-55
- v1/ARUCO_MODEL.md lines 48-51
- thesis/B1_aruco_scene.md lines 41-49
- .agent/DECISIONS.md lines 169-174 (2026-07-19 entry; the
  ambiguity-resolution part of this entry is superseded by a later
  lobe-separation entry, but the corner-refinement finding itself
  stands)

## Detector timing

v1/realtime/REALTIME.md line 95 (Pipeline B, object, APRILTAG
refine): detect p50/p95/p99 = 12.2 / 13.2 / 14.5 ms.

## Thesis citations

- Appendix E.1 covers fiducial marker detection and pose recovery
  (writing/v9 Appendices, confirmed: "Appendix E: Fiducial Marker
  Detection and Pose Recovery" at src line 105 of Appendices.txt).
- Reference [48] is AprilTag 2 (J. Wang and E. Olson, IROS 2016),
  confirmed at writing/v9/references.md line 56.
- Chapter 1 cites [29] for ArUco: "ArUco markers balance robustness
  and efficiency for single-camera setups [29]" (Chapter_1_Introduction.txt
  line 14). Reference [29] is M. Kalaitzakis et al., "Fiducial
  markers for pose estimation: Overview, applications and
  experimental comparison," J. Intelligent and Robotic Systems,
  2021 (references.md line 37).

## AprilTag status in this repository

Before the round-4 benchmark, the 2026-09-28 search found no
ArUco-vs-AprilTag comparison (only an unrelated trajectory-revision
decision in writing/v9/DECISIONS.md). That inventory is superseded by
the measured comparison described below, whose committed results are
in [marker_bench/summary.csv](../presentation/defense_2026/experiments/marker_bench/summary.csv).

AprilTag test bags exist in the recordings archive, dated
2026-01-22, and were never scored:
`ENSC498_apriltag_set1_cube_push_test_20260122_153720.bag` and
`ENSC498_apriltag_set2_side_view_test_20260122_154958.bag`.
Confirmed at eval/recordings_archive/README.md lines 15-16 (table
rows), 58 (S3 session description) and 104-111 (per-bag detail for
the Set1 bag; both bags are logged with status "test").

OpenCV 4.10.0 is installed in both interpreters, each with
`DICT_APRILTAG_36h11` and `CORNER_REFINE_APRILTAG` available
(confirmed by direct import 2026-09-28):
- `/home/luo/anaconda3/bin/python` (thesis Python)
- `/home/luo/anaconda3/envs/v3rt/bin/python` (V3 env)

## Round-4 update: a measured comparison and a literature review now exist (2026-09-28)

`presentation/defense_2026/experiments/marker_bench/` (D-134 to
D-148) times the pinned ArUco configuration above (OpenCV
ArucoDetector, DICT_5X5_50, CORNER_REFINE_APRILTAG) against AprilTag
3 (pupil-apriltags, tag36h11) and against OpenCV's own
DICT_APRILTAG_36h11 dictionary, on synthetic markers composited onto
real R6b frames, single-threaded on this workstation. Headline
(summary.csv, single thread, 640x480): the pinned ArUco takes 26.6 ms
per frame at 48 px against 3.5 ms (AprilTag 3, decimate 2) and
14.4 ms (decimate 1); AprilTag 3 is faster, not slower, than the
pinned ArUco, contrary to a common recollection (D-148). Corner
accuracy converges at 96 px (0.069-0.074 px for all four detectors);
below that AprilTag 3 is more accurate once a shared ~0.46-0.50 px
constant corner-fitting offset is removed (D-144). See
experiments/marker_bench/README.md and knowledge/experiments.md for
the full results and caveats (single-threaded, synthetic composite,
no lens distortion, concurrent transport_bench load during the run).

`knowledge/marker_literature.md` reads five ArUco-vs-AprilTag primary
sources in full plus one preprint; its verdict is that "similar
performance, AprilTag slower but more accurate" is version- and
setting-dependent in the published record and not a single supported
statement (D-148 cites it directly).

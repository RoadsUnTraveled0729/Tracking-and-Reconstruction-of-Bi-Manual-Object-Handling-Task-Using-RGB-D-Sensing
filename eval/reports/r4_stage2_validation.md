# Stage 2: pipelines and validation suites on R4

Recording: recording_20260825_070152 (R4). All raw validator stdout is
pinned in r4_stage2_validator_output.txt. Findings are reported, not
fixed, per the no-silent-fixes rule.

## Pipeline runs (frozen code, pinned settings)

- ArUco extraction: 1499 frames; detections wall 1447, object 1495,
  desk 1499. Object ambiguity: 1308 frames gravity-resolved, 0 unresolved.
- Scene calibration (scene_calibration_r4.json, --cube-size 0.07):
  wall pos dev max 6.93 mm / rot 0.481 deg over 10 frames; desk 0.26 mm
  / 0.050 deg; gravity-seed agreement 4.40 deg; desk stand tilt 32.24
  deg (R4 uses a tilted desk-marker stand like Recording 3, unlike
  R1's flat 4.75 deg placement); origin above tabletop -9.7 mm.
- Object filter: 16 despiked; smoothing deviation median 1.8 mm / max
  33.5 mm; step p95 raw 30.1 -> filtered 7.4 mm.
- Landmark filter (--edge-fill 12): left wrist 681 empty cells kept
  honest (45 percent), left elbow 370.
- v2 stack (run_v2 --source bag --dump, R4 calibration): 1499 frames
  at 29.4 fps sustained; person compute p99 23.8 ms, object p99 17.7
  ms; merger cadence p99 35.3 ms.

## Validator matrix

| suite | result | classification |
|---|---|---|
| validate_aruco (R4) | 19/21 | 2 real findings (below) |
| validate_real_recording (R4) | ALL PASS | - |
| validate_occlusion (R1 regression) | 33/33 | regression clean |
| validate_integration (R1 regression) | 20/20 after artifact restore | stale-artifact cause, below |
| validate_v2 unchanged (R1 refs) | 16/22 | 5 spurious (R1-referenced), 1 scenario |
| validate_v2_r4 (R4 refs, part 1) | 6/9 | 3 real findings (below) |
| validate_v2 part 2 (merger) | all pass | recording-independent |

## Findings (failures with established cause or open status)

1. RESOLVED (see E-009 and r4_marker_scale.json) - root cause: the
   new desk/object marker prints are ~43.6 mm, not the declared 50 mm
   (constant PnP/depth ratio 1.145 across the recording; R1 ratio
   ~1.00). Exact post-hoc rescale applied; stages 3-5 recomputed.
   Original finding text kept below for the record.
   ArUco depth cross-check fails on desk and object markers:
   PnP tz vs depth-median z bias desk +80.2 mm at 0.64 m (std 0.6 mm),
   object +143.5 mm at 1.11 m (std 17.6 mm); wall passes (-75.3 mm at
   2.98 m, within 5 percent of range). Same check passed on R1 and R3.
   Systematic, not noise (desk std 0.6 mm). Cause not yet established;
   candidates: depth-sensor calibration drift since February, different
   depth preset/exposure in this capture session, tilted-stand geometry
   sampling the stand surface. [Superseded: the marker-size
   hypothesis proved correct.]
2. EXPLAINED - validate_integration R1 regression (3 failures on first
   run): the working copies v1/integration/output/unity_person_log.csv
   and unity_object_log.csv had been overwritten by the 2026-07-24
   realtime capture session (same mtime as rt_capture_raw.mp4) while
   integrated_stream.csv remained from the 2026-07-23 offline pass.
   Restored the matching pinned dataset/ copies (07-24 files backed up
   in eval/output/backup_20260825/): 20/20 PASS. Pre-existing since
   July; not caused by the v1/ move or by R4 work.
3. FINDING - causal left-shoulder angle p95 22.34 deg exceeds the 20
   deg bound on both-live frames (median 1.37 deg is fine). The left
   arm hovers at the visibility gate all recording; causal one-euro
   lag at occlusion boundaries drives the tail. R4 characteristic, not
   a regression.
4. FINDING - causal liveness runs ~10 percent (relative) below offline
   availability (R shoulder 89.0 vs 99.1 percent; L shoulder 49.4 vs
   55.8): the causal filter pays warm-up after each of R4's many
   occlusion gaps. Motivates the stage-5 fallback work.
5. FINDING - realtime object live 1388 vs offline detected 1495 (92.8
   percent, bound 95): the causal object filter's trailing Hampel
   rejects during the fast wire-path segments (raw step p95 30.1 mm
   per frame vs R1's gentler carry). R4 characteristic.
6. FINDING (for stage 5) - gate-miss specimen: left shoulder around
   34-36 s keeps visibility above the gate while its depth window
   lands on the background (z jumps 1.3 -> 3.4 m). Visible in the
   landmark QC plot; exactly the miss-rate phenomenon stage 5
   quantifies.
7. NOTE - the calibration window (first 10 wall+desk detections,
   frames 0-9) is person-clear: the person enters at frame 45 and the
   wall gap (frames 47-98) starts after; entry-phase calibration is
   sound.

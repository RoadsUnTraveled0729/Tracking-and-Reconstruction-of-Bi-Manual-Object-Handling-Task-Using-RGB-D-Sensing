# Stage 6a: Chapter 7 real-time stack rerun on R4

## v1 realtime stack (frozen code, R4 bag, recorded pacing)

Command: python v1/realtime/integration/run_realtime.py
--bag Video/recording_20260825_070152.bag
--calib v1/aruco/output/scene_calibration_r4.json --dump --profile
(R1 working dumps backed up to eval/output/backup_20260825/realtime/).

Profile (1499 frames, 55.0 s wall incl. startup):

| stage | p50 (ms) | p95 | p99 | max |
|---|---|---|---|---|
| person total | 11.43 | 24.70 | 26.11 | 28.27 |
| mediapipe | 8.42 | 21.81 | 23.23 | 25.27 |
| solve | 0.17 | 0.22 | 0.26 | 0.32 |
| object total | 13.91 | 14.87 | 15.58 | 25.67 |

30 fps budget holds: person p99 headroom 7.2 ms; the closed-form
solve stays under 0.32 ms/frame on R4 (the "lightweight" claim's
number, re-verified on the new recording).

## Validation

- validate_realtime.py unchanged: 5/11 fail, ALL spurious - its
  offline references are hardcoded to the R1 stems (same situation as
  validate_v2, pre-declared in stage 2).
- eval/validate/validate_v2_r4.py generalized with --person-dump /
  --object-dump (the v1 and v2 dumps share one column contract) and
  run against the R4 realtime dumps: pelvis median 5.7 mm, object
  position median 5.4 mm, lag +4 frames (133 ms, r 0.969), budgets
  pass; the same three explained R4 findings as v2 (left-shoulder
  p95 22.3 deg; causal liveness ~10 percent below offline
  availability; object live 1388 vs 1495).

## Parity finding

The v1 realtime dumps and the v2 stack dumps on R4 are different
files (different hashes, different timings) whose derived metrics
agree to every displayed digit - the v2 pipeline-parity property
(pinned on R1 in v2/dataset/m2_pipeline_parity.txt) holds unchanged
on a new recording with heavy occlusion. Strengthens the Ch.7/8.3
story that v2 is a faithful re-architecture.

## Scale caveat (E-009)

The frozen realtime stack computes PnP with the declared 50 mm
marker sizes, so its object positions carry the R4 print-size
inflation. This does not affect any of the numbers above (they are
internal-consistency and latency measurements; both sides of each
comparison carry the same scale). Absolute-accuracy statements about
the realtime track wait on the marker-size confirmation; the durable
physical fix is reprinting the markers at true size before any future
recording.

## Other stage-6 items

- bench_solver.py stays pinned on R1 by design: it is a
  hardware/solver micro-benchmark inside frozen code, not a recording
  measurement; its Ch.7 figure remains valid.
- Representative-frame candidate extracted:
  eval/reports/recording_20260825_070152_frame1225.png (E-010).
- Remaining stage-6 work (worked-example rebase across chapters,
  Unity play pass for integration logs, chapter rewrites) waits on
  the survey, the marker-size ruler check, and the manuscript-target
  decision (v6 English vs v7 Chinese).

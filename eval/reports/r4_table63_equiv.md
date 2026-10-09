# Table 6.3 equivalent: occlusion handling on R4

Synthetic scenarios (R1 designs at R4 fractions; angle error
vs the unmasked truth on the expected-held groups, deg):

| scenario | window | held groups | hold med/p95 | cv med/p95 | sphere med/p95 | reacq step h/c/s (truth) |
|---|---|---|---|---|---|---|
| wrist_short | 530-532 | R_twist,R_elbow | 0.41 / 5.73 | 1.43 / 7.36 | 0.61 / 2.54 | 28.34 / 28.34 / 28.34 (28.34) |
| wrist_long | 691-735 | R_twist,R_elbow | 2.74 / 65.96 | 3.29 / 93.66 | 1.47 / 38.15 | 61.81 / 89.5 / 32.87 (5.22) |
| elbow_long | 853-897 | R_swing,R_twist,R_elbow | 1.51 / 9.46 | 1.91 / 13.06 | 1.51 / 9.46 | 13.45 / 13.56 / 13.45 (8.55) |
| hip | 1015-1044 | root | 3.82 / 6.43 | 3.53 / 7.05 | 3.82 / 6.43 | 20.16 / 20.16 / 20.16 (2.15) |
| root_ref | 1257-1286 | R_swing,R_twist,R_elbow | 1.88 / 11.54 | 5.62 / 24.82 | 1.88 / 11.54 | 11.14 / 16.68 / 11.14 (1.19) |
| pose_loss | 1176-1185 | root,R_swing,R_twist,R_elbow,L_swing,L_twist,L_elbow | 0.59 / 30.4 | 0.58 / 21.73 | 0.59 / 30.4 | 57.22 / 50.91 / 57.22 (10.09) |

Real long left-wrist occlusion (frames 833-1096, box in the left hand), point space vs box_center + fitted grip offset:

- hold-point baseline: median 35.7 cm, p95 37.6 cm (264 frames)
- sphere-constrained: median 7.1 cm, p95 36.6 cm (47 frames; needs a live elbow - the left elbow is also occluded for most of this event)
- hold-point on the same 47 frames: median 5.5 cm, p95 31.3 cm
- cv-extrap: no native point output; graded on angle continuity in the synthetic table

Note: the left grip offset was fitted on measured frames outside this window; regrips inside the window are not observable, so these numbers bound rather than measure the wrist error.

Regression guard on pinned R1 masked data: PASS.

# Inspection: recording_20260825_070152

Frames 1499, duration 49.97 s, 29.98 fps, 640x480.
Frames with pose: 1454 (97.0 percent).

## Anchor check

PASS: desk anchor detected in every frame

## Phases

- entry: frames 0-44 (1.5 s)
- approach: frames 45-223 (6.0 s)
- manipulation: frames 224-1314 (36.4 s)
- retreat: frames 1315-1498 (6.1 s)

## Marker coverage (global)

- m0_wall: 1447/1499 (96.53 percent), 1 gaps
- m1_object: 1495/1499 (99.73 percent), 4 gaps
- m2_desk: 1499/1499 (100.0 percent), 0 gaps

## Landmark status (percent of pose frames, global)

| landmark | ok | low_vis | no_depth | vis median | vis p10 |
|---|---|---|---|---|---|
| left_shoulder | 99.86 | 0.0 | 0.14 | 0.999 | 0.996 |
| right_shoulder | 97.94 | 0.0 | 2.06 | 0.999 | 0.998 |
| left_elbow | 74.55 | 25.45 | 0.0 | 0.659 | 0.239 |
| right_elbow | 99.11 | 0.76 | 0.14 | 0.8 | 0.693 |
| left_wrist | 55.57 | 44.15 | 0.28 | 0.53 | 0.12 |
| right_wrist | 98.76 | 1.17 | 0.07 | 0.934 | 0.784 |
| left_hip | 100.0 | 0.0 | 0.0 | 0.998 | 0.998 |
| right_hip | 99.66 | 0.0 | 0.34 | 0.999 | 0.999 |

## Occlusion events

Total 44; out-of-scene 7; in-scene 37.

Longest 15 in-scene events:

| entity | kind | frames | span | seconds | phases |
|---|---|---|---|---|---|
| left_wrist | landmark-blocked | 264 | 833-1096 | 8.81 | manipulation |
| left_wrist | landmark-blocked | 207 | 175-381 | 6.9 | approach/manipulation |
| left_elbow | landmark-blocked | 189 | 905-1093 | 6.3 | manipulation |
| left_elbow | landmark-blocked | 122 | 184-305 | 4.07 | approach/manipulation |
| marker_wall | marker-not-detected | 52 | 47-98 | 1.73 | approach |
| left_wrist | landmark-blocked | 30 | 1278-1307 | 1.0 | manipulation |
| left_wrist | landmark-blocked | 29 | 545-573 | 0.97 | manipulation |
| left_elbow | landmark-blocked | 28 | 859-886 | 0.93 | manipulation |
| left_elbow | landmark-blocked | 21 | 311-331 | 0.7 | manipulation |
| right_wrist | landmark-blocked | 17 | 45-61 | 0.57 | approach |
| right_elbow | landmark-blocked | 13 | 45-57 | 0.43 | approach |
| right_shoulder | landmark-blocked | 11 | 499-509 | 0.37 | manipulation |
| right_shoulder | landmark-blocked | 7 | 45-51 | 0.23 | approach |
| right_hip | landmark-blocked | 5 | 45-49 | 0.17 | approach |
| right_shoulder | landmark-blocked | 3 | 491-493 | 0.1 | manipulation |

## Wrist liveness per phase (percent ok)

- entry: left 0.0, right 0.0
- approach: left 72.63, right 89.94
- manipulation: left 55.18, right 100.0
- retreat: left 41.3, right 100.0

## Representative-frame shortlist (manipulation phase)

- frame 1225 (t=40.86 s, min vis 0.793, max reproj 0.353 px)
- frame 1226 (t=40.89 s, min vis 0.792, max reproj 0.351 px)
- frame 1224 (t=40.83 s, min vis 0.792, max reproj 0.36 px)
- frame 1228 (t=40.96 s, min vis 0.79, max reproj 0.374 px)
- frame 1223 (t=40.79 s, min vis 0.785, max reproj 0.354 px)
- frame 1227 (t=40.93 s, min vis 0.785, max reproj 0.362 px)
- frame 1229 (t=40.99 s, min vis 0.781, max reproj 0.348 px)
- frame 1222 (t=40.76 s, min vis 0.775, max reproj 0.356 px)
- frame 1230 (t=41.03 s, min vis 0.774, max reproj 0.356 px)
- frame 1221 (t=40.73 s, min vis 0.774, max reproj 0.353 px)

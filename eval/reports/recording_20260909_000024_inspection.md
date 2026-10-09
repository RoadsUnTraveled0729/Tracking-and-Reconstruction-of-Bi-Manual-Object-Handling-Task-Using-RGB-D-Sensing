# Inspection: recording_20260909_000024

Frames 1499, duration 49.97 s, 29.98 fps, 640x480.
Frames with pose: 1499 (100.0 percent).

## Anchor check

PASS: desk anchor detected in every frame

## Phases

- entry: absent
- approach: frames 0-289 (9.7 s)
- manipulation: frames 290-1080 (26.4 s)
- retreat: frames 1081-1498 (13.9 s)

## Marker coverage (global)

- m0_wall: 1499/1499 (100.0 percent), 0 gaps
- m1_object: 1498/1499 (99.93 percent), 1 gaps
- m2_desk: 1499/1499 (100.0 percent), 0 gaps

## Landmark status (percent of pose frames, global)

| landmark | ok | low_vis | no_depth | vis median | vis p10 |
|---|---|---|---|---|---|
| left_shoulder | 100.0 | 0.0 | 0.0 | 1.0 | 0.999 |
| right_shoulder | 100.0 | 0.0 | 0.0 | 1.0 | 1.0 |
| left_elbow | 100.0 | 0.0 | 0.0 | 0.917 | 0.834 |
| right_elbow | 100.0 | 0.0 | 0.0 | 0.918 | 0.882 |
| left_wrist | 100.0 | 0.0 | 0.0 | 0.904 | 0.799 |
| right_wrist | 99.33 | 0.47 | 0.2 | 0.974 | 0.963 |
| left_hip | 100.0 | 0.0 | 0.0 | 0.998 | 0.998 |
| right_hip | 100.0 | 0.0 | 0.0 | 0.999 | 0.998 |

## Occlusion events

Total 3; out-of-scene 0; in-scene 3.

Longest 15 in-scene events:

| entity | kind | frames | span | seconds | phases |
|---|---|---|---|---|---|
| right_wrist | landmark-blocked | 7 | 0-6 | 0.23 | approach |
| right_wrist | landmark-blocked | 3 | 705-707 | 0.1 | manipulation |
| marker_object | marker-not-detected | 1 | 741-741 | 0.03 | manipulation |

## Wrist liveness per phase (percent ok)

- approach: left 100.0, right 97.59
- manipulation: left 100.0, right 99.62
- retreat: left 100.0, right 100.0

## Representative-frame shortlist (manipulation phase)

- frame 1001 (t=33.39 s, min vis 0.951, max reproj 0.378 px)
- frame 1003 (t=33.46 s, min vis 0.951, max reproj 0.347 px)
- frame 1002 (t=33.42 s, min vis 0.95, max reproj 0.36 px)
- frame 1000 (t=33.36 s, min vis 0.95, max reproj 0.431 px)
- frame 999 (t=33.32 s, min vis 0.95, max reproj 0.324 px)
- frame 998 (t=33.29 s, min vis 0.949, max reproj 0.33 px)
- frame 997 (t=33.26 s, min vis 0.949, max reproj 0.323 px)
- frame 1007 (t=33.59 s, min vis 0.948, max reproj 0.324 px)
- frame 1005 (t=33.52 s, min vis 0.948, max reproj 0.409 px)
- frame 1006 (t=33.56 s, min vis 0.948, max reproj 0.319 px)

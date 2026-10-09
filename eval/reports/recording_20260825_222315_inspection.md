# Inspection: recording_20260825_222315

Frames 2099, duration 69.98 s, 29.98 fps, 640x480.
Frames with pose: 2042 (97.3 percent).

## Anchor check

PASS: desk anchor detected in every frame

## Phases

- entry: frames 0-56 (1.9 s)
- approach: frames 57-655 (20.0 s)
- manipulation: frames 656-1983 (44.3 s)
- retreat: frames 1984-2098 (3.8 s)

## Marker coverage (global)

- m0_wall: 2007/2099 (95.62 percent), 1 gaps
- m1_object: 2058/2099 (98.05 percent), 5 gaps
- m2_desk: 2099/2099 (100.0 percent), 0 gaps

## Landmark status (percent of pose frames, global)

| landmark | ok | low_vis | no_depth | vis median | vis p10 |
|---|---|---|---|---|---|
| left_shoulder | 99.85 | 0.0 | 0.15 | 1.0 | 0.999 |
| right_shoulder | 99.46 | 0.0 | 0.54 | 0.999 | 0.999 |
| left_elbow | 89.47 | 10.33 | 0.2 | 0.859 | 0.466 |
| right_elbow | 95.3 | 3.87 | 0.83 | 0.845 | 0.732 |
| left_wrist | 89.72 | 10.28 | 0.0 | 0.823 | 0.448 |
| right_wrist | 98.68 | 0.83 | 0.49 | 0.936 | 0.898 |
| left_hip | 100.0 | 0.0 | 0.0 | 0.998 | 0.997 |
| right_hip | 99.8 | 0.0 | 0.2 | 0.998 | 0.998 |

## Occlusion events

Total 24; out-of-scene 1; in-scene 23.

Longest 15 in-scene events:

| entity | kind | frames | span | seconds | phases |
|---|---|---|---|---|---|
| left_elbow | landmark-blocked | 211 | 1458-1668 | 7.04 | manipulation |
| left_wrist | landmark-blocked | 210 | 1459-1668 | 7.0 | manipulation |
| marker_wall | marker-not-detected | 92 | 60-151 | 3.07 | approach |
| right_elbow | landmark-blocked | 68 | 1826-1893 | 2.27 | manipulation |
| marker_object | marker-not-detected | 20 | 1085-1104 | 0.67 | manipulation |
| right_elbow | landmark-blocked | 16 | 114-129 | 0.53 | approach |
| right_wrist | landmark-blocked | 15 | 57-71 | 0.5 | approach |
| right_elbow | landmark-blocked | 12 | 57-68 | 0.4 | approach |
| right_wrist | landmark-blocked | 10 | 1395-1404 | 0.33 | manipulation |
| marker_object | marker-not-detected | 9 | 1067-1075 | 0.3 | manipulation |
| right_shoulder | landmark-blocked | 7 | 57-63 | 0.23 | approach |
| marker_object | marker-not-detected | 7 | 1077-1083 | 0.23 | manipulation |
| right_hip | landmark-blocked | 4 | 58-61 | 0.13 | approach |
| right_shoulder | landmark-blocked | 4 | 147-150 | 0.13 | approach |
| marker_object | marker-not-detected | 4 | 1106-1109 | 0.13 | manipulation |

## Wrist liveness per phase (percent ok)

- entry: left 0.0, right 0.0
- approach: left 100.0, right 97.5
- manipulation: left 84.19, right 99.1
- retreat: left 100.0, right 100.0

## Representative-frame shortlist (manipulation phase)

- frame 1236 (t=41.23 s, min vis 0.901, max reproj 0.523 px)
- frame 1230 (t=41.03 s, min vis 0.901, max reproj 0.467 px)
- frame 1237 (t=41.26 s, min vis 0.898, max reproj 0.241 px)
- frame 1234 (t=41.16 s, min vis 0.898, max reproj 0.257 px)
- frame 1232 (t=41.1 s, min vis 0.898, max reproj 0.314 px)
- frame 1235 (t=41.2 s, min vis 0.898, max reproj 0.615 px)
- frame 1233 (t=41.13 s, min vis 0.898, max reproj 0.249 px)
- frame 1238 (t=41.3 s, min vis 0.897, max reproj 0.24 px)
- frame 1229 (t=41.0 s, min vis 0.897, max reproj 0.47 px)
- frame 1231 (t=41.06 s, min vis 0.897, max reproj 0.442 px)

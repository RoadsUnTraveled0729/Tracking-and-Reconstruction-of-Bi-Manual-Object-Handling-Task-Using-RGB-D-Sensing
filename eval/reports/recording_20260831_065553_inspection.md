# Inspection: recording_20260831_065553

Frames 900, duration 29.99 s, 29.98 fps, 640x480.
Frames with pose: 900 (100.0 percent).

## Anchor check

PASS: desk anchor detected in every frame

## Phases

- entry: absent
- approach: frames 0-206 (6.9 s)
- manipulation: frames 207-888 (22.7 s)
- retreat: frames 889-899 (0.4 s)

## Marker coverage (global)

- m0_wall: 900/900 (100.0 percent), 0 gaps
- m1_object: 899/900 (99.89 percent), 1 gaps
- m2_desk: 900/900 (100.0 percent), 0 gaps

## Landmark status (percent of pose frames, global)

| landmark | ok | low_vis | no_depth | vis median | vis p10 |
|---|---|---|---|---|---|
| left_shoulder | 100.0 | 0.0 | 0.0 | 0.999 | 0.998 |
| right_shoulder | 100.0 | 0.0 | 0.0 | 0.999 | 0.998 |
| left_elbow | 100.0 | 0.0 | 0.0 | 0.751 | 0.578 |
| right_elbow | 100.0 | 0.0 | 0.0 | 0.779 | 0.65 |
| left_wrist | 12.44 | 87.56 | 0.0 | 0.409 | 0.296 |
| right_wrist | 87.67 | 12.33 | 0.0 | 0.796 | 0.454 |
| left_hip | 99.22 | 0.0 | 0.78 | 0.998 | 0.994 |
| right_hip | 99.89 | 0.0 | 0.11 | 0.998 | 0.996 |

## Occlusion events

Total 26; out-of-scene 0; in-scene 26.

Longest 15 in-scene events:

| entity | kind | frames | span | seconds | phases |
|---|---|---|---|---|---|
| left_wrist | landmark-blocked | 518 | 0-517 | 17.28 | approach/manipulation |
| left_wrist | landmark-blocked | 143 | 757-899 | 4.77 | manipulation/retreat |
| right_wrist | landmark-blocked | 90 | 550-639 | 3.0 | manipulation |
| left_wrist | landmark-blocked | 51 | 655-705 | 1.7 | manipulation |
| left_wrist | landmark-blocked | 27 | 605-631 | 0.9 | manipulation |
| left_wrist | landmark-blocked | 16 | 554-569 | 0.53 | manipulation |
| left_wrist | landmark-blocked | 15 | 710-724 | 0.5 | manipulation |
| right_wrist | landmark-blocked | 14 | 11-24 | 0.47 | approach |
| left_wrist | landmark-blocked | 6 | 726-731 | 0.2 | manipulation |
| left_wrist | landmark-blocked | 4 | 633-636 | 0.13 | manipulation |
| right_wrist | landmark-blocked | 4 | 681-684 | 0.13 | manipulation |
| left_hip | landmark-blocked | 3 | 30-32 | 0.1 | approach |
| left_wrist | landmark-blocked | 3 | 646-648 | 0.1 | manipulation |
| left_wrist | landmark-blocked | 2 | 602-603 | 0.07 | manipulation |
| left_hip | landmark-blocked | 1 | 21-21 | 0.03 | approach |

## Wrist liveness per phase (percent ok)

- approach: left 0.0, right 93.24
- manipulation: left 16.42, right 85.78
- retreat: left 0.0, right 100.0

## Representative-frame shortlist (manipulation phase)

- frame 533 (t=17.78 s, min vis 0.578, max reproj 0.416 px)
- frame 528 (t=17.61 s, min vis 0.568, max reproj 0.392 px)
- frame 750 (t=25.02 s, min vis 0.567, max reproj 0.345 px)
- frame 749 (t=24.98 s, min vis 0.567, max reproj 0.383 px)
- frame 745 (t=24.85 s, min vis 0.565, max reproj 0.534 px)
- frame 532 (t=17.75 s, min vis 0.565, max reproj 0.383 px)
- frame 748 (t=24.95 s, min vis 0.565, max reproj 0.382 px)
- frame 746 (t=24.88 s, min vis 0.561, max reproj 0.395 px)
- frame 744 (t=24.82 s, min vis 0.561, max reproj 0.395 px)
- frame 529 (t=17.65 s, min vis 0.56, max reproj 0.385 px)

# Moving-window recovery check: recording_20260825_222315

All chronologically selected 45-frame windows passing the existing harness rules, selected before recovery errors were computed. No motion threshold or duration retuning is applied. Every selected window is reported, including stationary or unfavourable cases. Reference swing and elbow groups must be live; twist may be held. These are synthetic comparisons with the unmasked solve and measured wrist, not independent anatomical ground truth. Windows do not overlap within either arm. Simultaneous left/right windows share recording frames: 45; 135 arm-frame occurrences cover 90 distinct recording frames. These windows are not independent trials.

## left 1674-1718 (45 frames, truth arm motion 12 deg, object wrist estimate err median 14.0 cm)

| method | angle med (deg) | angle p95 | angle max | FK wrist med (cm) | p95 | max |
|---|---|---|---|---|---|---|
| hold | 2.29 | 10.55 | 11.95 | 4.32 | 6.70 | 6.90 |
| masked | 3.45 | 6.95 | 7.52 | 4.25 | 6.94 | 7.13 |
| recovery | 7.49 | 15.25 | 15.96 | 13.98 | 15.16 | 15.28 |

## right 661-705 (45 frames, truth arm motion 5 deg, object wrist estimate err median 1.2 cm)

| method | angle med (deg) | angle p95 | angle max | FK wrist med (cm) | p95 | max |
|---|---|---|---|---|---|---|
| hold | 1.07 | 3.08 | 4.39 | 2.41 | 2.98 | 3.17 |
| masked | 1.56 | 3.28 | 4.03 | 2.16 | 2.78 | 2.82 |
| recovery | 2.18 | 7.67 | 9.83 | 1.51 | 1.88 | 2.09 |

## right 1674-1718 (45 frames, truth arm motion 15 deg, object wrist estimate err median 6.9 cm)

| method | angle med (deg) | angle p95 | angle max | FK wrist med (cm) | p95 | max |
|---|---|---|---|---|---|---|
| hold | 2.00 | 10.33 | 15.59 | 2.16 | 8.96 | 9.63 |
| masked | 0.96 | 7.09 | 10.64 | 1.40 | 8.39 | 8.62 |
| recovery | 11.75 | 28.03 | 34.43 | 6.87 | 12.88 | 13.16 |

## Reading

The motion column characterizes each eligible outage; it is not a selection criterion. The archived selection lists every eligible frame and run. No conclusion about large moving outages follows if all selected windows contain little movement. Direction fallback has a 45-frame horizon, while the ordinary IK swivel prior persists without that expiry. Historical exploratory windows are retained separately.

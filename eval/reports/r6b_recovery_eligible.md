# Moving-window recovery check: recording_20260831_065553

All chronologically selected 45-frame windows passing the existing harness rules, selected before recovery errors were computed. No motion threshold or duration retuning is applied. Every selected window is reported, including stationary or unfavourable cases. Reference swing and elbow groups must be live; twist may be held. These are synthetic comparisons with the unmasked solve and measured wrist, not independent anatomical ground truth. Windows do not overlap within either arm. Simultaneous left/right windows share recording frames: 0; 225 arm-frame occurrences cover 225 distinct recording frames. These windows are not independent trials.

## right 212-256 (45 frames, truth arm motion 4 deg, object wrist estimate err median 0.5 cm)

| method | angle med (deg) | angle p95 | angle max | FK wrist med (cm) | p95 | max |
|---|---|---|---|---|---|---|
| hold | 24.64 | 58.94 | 58.94 | 1.68 | 2.94 | 3.06 |
| masked | 1.35 | 90.00 | 90.26 | 0.83 | 6.36 | 8.61 |
| recovery | 3.75 | 84.96 | 87.70 | 0.57 | 9.73 | 14.85 |

## right 272-316 (45 frames, truth arm motion 3 deg, object wrist estimate err median 1.0 cm)

| method | angle med (deg) | angle p95 | angle max | FK wrist med (cm) | p95 | max |
|---|---|---|---|---|---|---|
| hold | 29.68 | 46.10 | 46.68 | 2.83 | 3.13 | 3.16 |
| masked | 0.49 | 88.53 | 89.47 | 1.16 | 5.64 | 7.86 |
| recovery | 3.72 | 87.46 | 93.28 | 1.13 | 6.01 | 14.52 |

## right 332-376 (45 frames, truth arm motion 6 deg, object wrist estimate err median 1.2 cm)

| method | angle med (deg) | angle p95 | angle max | FK wrist med (cm) | p95 | max |
|---|---|---|---|---|---|---|
| hold | 23.79 | 57.40 | 57.98 | 2.47 | 4.56 | 4.84 |
| masked | 1.86 | 93.30 | 96.41 | 1.64 | 5.32 | 7.37 |
| recovery | 4.29 | 108.67 | 154.54 | 1.02 | 4.93 | 6.40 |

## right 392-436 (45 frames, truth arm motion 6 deg, object wrist estimate err median 2.5 cm)

| method | angle med (deg) | angle p95 | angle max | FK wrist med (cm) | p95 | max |
|---|---|---|---|---|---|---|
| hold | 15.78 | 89.19 | 93.42 | 1.33 | 1.92 | 2.03 |
| masked | 3.58 | 75.62 | 75.99 | 1.77 | 4.68 | 6.94 |
| recovery | 3.87 | 74.62 | 76.14 | 2.68 | 4.43 | 6.64 |

## right 452-496 (45 frames, truth arm motion 5 deg, object wrist estimate err median 0.9 cm)

| method | angle med (deg) | angle p95 | angle max | FK wrist med (cm) | p95 | max |
|---|---|---|---|---|---|---|
| hold | 19.69 | 96.65 | 97.69 | 0.83 | 1.17 | 1.23 |
| masked | 1.56 | 66.48 | 66.89 | 0.48 | 4.47 | 7.33 |
| recovery | 1.97 | 70.06 | 71.99 | 0.96 | 4.62 | 7.60 |

## Reading

The motion column characterizes each eligible outage; it is not a selection criterion. The archived selection lists every eligible frame and run. No conclusion about large moving outages follows if all selected windows contain little movement. Direction fallback has a 45-frame horizon, while the ordinary IK swivel prior persists without that expiry. Historical exploratory windows are retained separately.

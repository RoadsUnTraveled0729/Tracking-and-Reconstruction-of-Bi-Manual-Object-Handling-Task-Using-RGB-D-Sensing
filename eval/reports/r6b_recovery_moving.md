# Moving-window recovery check: recording_20260831_065553

Synthetic arm masking on the windows carved by harness_recovery.py for this recording (r6b_recovery_synthetic.md). Truth = unmasked solve. Methods on identical masked inputs. This check adds the forward-kinematics wrist error of all three methods, the quantity the reconstruction shows.

## right 212-256 (45 frames, truth arm motion 4 deg, object wrist estimate err median 0.5 cm)

| method | angle med (deg) | angle p95 | angle max | FK wrist med (cm) | p95 | max |
|---|---|---|---|---|---|---|
| hold | 24.64 | 58.94 | 58.94 | 1.68 | 2.94 | 3.06 |
| masked | 1.35 | 90.0 | 90.26 | 0.83 | 6.36 | 8.61 |
| recovery | 3.75 | 84.96 | 87.7 | 0.57 | 9.73 | 14.85 |

## right 272-316 (45 frames, truth arm motion 3 deg, object wrist estimate err median 1.0 cm)

| method | angle med (deg) | angle p95 | angle max | FK wrist med (cm) | p95 | max |
|---|---|---|---|---|---|---|
| hold | 29.68 | 46.1 | 46.68 | 2.83 | 3.13 | 3.16 |
| masked | 0.49 | 88.53 | 89.47 | 1.16 | 5.64 | 7.86 |
| recovery | 3.72 | 87.46 | 93.28 | 1.13 | 6.01 | 14.52 |

## right 332-376 (45 frames, truth arm motion 6 deg, object wrist estimate err median 1.2 cm)

| method | angle med (deg) | angle p95 | angle max | FK wrist med (cm) | p95 | max |
|---|---|---|---|---|---|---|
| hold | 23.79 | 57.4 | 57.98 | 2.47 | 4.56 | 4.84 |
| masked | 1.86 | 93.3 | 96.41 | 1.64 | 5.32 | 7.37 |
| recovery | 4.29 | 108.67 | 154.54 | 1.02 | 4.93 | 6.4 |

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
| recovery | 1.97 | 70.06 | 71.99 | 0.96 | 4.62 | 7.6 |

## Reading

The reading above the tables is left to the consumer of the numbers: the truth arm motion per window (printed in each heading) says how far a held value can drift, and the FK wrist columns say what each method shows. The paragraph written for R5 (a fast desk slide, about 50 deg of arm travel per window) is not repeated here.

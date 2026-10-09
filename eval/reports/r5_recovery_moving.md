# Moving-window recovery check: recording_20260825_222315

Synthetic arm masking on the one tracked MOVING holding stretch (right-hand desk slide). Truth = unmasked solve. Methods on identical masked inputs. Supplement to r5_recovery_synthetic.md; see the docstring of eval/failure/moving_window_check.py for why the main harness's windows are motion-poor.

## right 865-895 (31 frames, truth arm motion 50 deg, object wrist estimate err median 1.2 cm)

| method | angle med (deg) | angle p95 | angle max | FK wrist med (cm) | p95 | max |
|---|---|---|---|---|---|---|
| hold | 1.88 | 10.79 | 50.62 | 2.04 | 10.71 | 15.39 |
| masked | 1.46 | 14.45 | 16.79 | 2.99 | 3.26 | 3.28 |
| recovery | 4.41 | 20.62 | 28.57 | 1.67 | 2.17 | 2.8 |

## right 870-902 (33 frames, truth arm motion 50 deg, object wrist estimate err median 1.3 cm)

| method | angle med (deg) | angle p95 | angle max | FK wrist med (cm) | p95 | max |
|---|---|---|---|---|---|---|
| hold | 3.36 | 18.33 | 49.86 | 2.17 | 21.0 | 21.39 |
| masked | 3.0 | 13.83 | 13.93 | 2.32 | 2.72 | 4.79 |
| recovery | 5.44 | 22.04 | 26.11 | 1.65 | 2.39 | 2.99 |

## Reading

On a moving outage the hold-last wrist position runs away with the motion (max grows with window length) while the object-recovered wrist stays within a few centimeters of the true wrist - the object anchor is live, not a memory. In angle space the recovered twist is conditioned by the elbow swivel prior and can read worse than the smoothed memory methods on short windows; the recovered groups are tagged CONSTRAINED accordingly. The EMA memory method degrades toward hold as its memory goes stale (45-frame horizon), which is why the real 8-second failure windows - graded qualitatively in the overlay video - show hold/EMA leaving the body while the recovery follows the cube.

# Recovered wrist against manual labels (R5)

Recording: recording_20260825_222315. Labels: 20 wrists clicked by the user on natural failure-window frames inside grip episodes and 7 on clean frames outside the failure mask (the reference check). Truth is the clicked pixel deprojected with the aligned depth. Errors in cm, in the solver space. Methods: recovered = object-derived wrist estimate; measured = MediaPipe wrist on that frame; hold = last accepted MediaPipe wrist before the frame; plain_fk / hold_fk / recovery_fk = the wrist the angles of the plain, hold-last and recovery solves place.

## Natural failure windows

| side | method | n | median | p95 | max |
|---|---|---|---|---|---|
| left | recovered | 16 | 13.22 | 16.91 | 19.12 |
| left | measured | 9 | 5.5 | 16.89 | 23.49 |
| left | hold | 16 | 6.63 | 7.26 | 7.28 |
| left | plain_fk | 16 | 12.31 | 14.11 | 14.24 |
| left | hold_fk | 16 | 12.66 | 14.27 | 14.29 |
| left | recovery_fk | 16 | 13.14 | 15.21 | 19.12 |
| right | recovered | 4 | 13.67 | 14.97 | 15.2 |
| right | measured | 4 | 1.1 | 6.49 | 7.44 |
| right | hold | 4 | 15.64 | 17.04 | 17.28 |
| right | plain_fk | 4 | 11.38 | 13.64 | 14.03 |
| right | hold_fk | 4 | 17.6 | 20.0 | 20.39 |
| right | recovery_fk | 4 | 5.22 | 5.46 | 5.46 |
| all | recovered | 20 | 13.35 | 16.33 | 19.12 |
| all | measured | 13 | 5.33 | 13.86 | 23.49 |
| all | hold | 20 | 6.74 | 15.74 | 17.28 |
| all | plain_fk | 20 | 11.73 | 14.08 | 14.24 |
| all | hold_fk | 20 | 12.77 | 17.94 | 20.39 |
| all | recovery_fk | 20 | 12.66 | 14.16 | 19.12 |

## Clean frames (reference check)

| side | method | n | median | p95 | max |
|---|---|---|---|---|---|
| left | recovered | 3 | 5.67 | 5.85 | 5.87 |
| left | measured | 3 | 4.45 | 5.36 | 5.46 |
| left | hold | 3 | 4.31 | 5.19 | 5.29 |
| left | plain_fk | 3 | 3.63 | 5.09 | 5.25 |
| left | hold_fk | 3 | 3.63 | 4.78 | 4.91 |
| left | recovery_fk | 3 | 3.63 | 4.58 | 4.69 |
| right | recovered | 4 | 8.54 | 12.92 | 13.4 |
| right | measured | 4 | 2.09 | 4.78 | 5.11 |
| right | hold | 4 | 2.15 | 4.74 | 5.05 |
| right | plain_fk | 4 | 2.98 | 7.12 | 7.49 |
| right | hold_fk | 4 | 2.98 | 7.12 | 7.49 |
| right | recovery_fk | 4 | 2.98 | 7.12 | 7.49 |
| all | recovered | 7 | 5.87 | 12.44 | 13.4 |
| all | measured | 7 | 3.71 | 5.35 | 5.46 |
| all | hold | 7 | 3.73 | 5.22 | 5.29 |
| all | plain_fk | 7 | 3.63 | 6.82 | 7.49 |
| all | hold_fk | 7 | 3.63 | 6.75 | 7.49 |
| all | recovery_fk | 7 | 3.63 | 6.75 | 7.49 |

## Per frame

| frame | side | group | recovered | measured | hold | plain_fk | hold_fk | recovery_fk | mixed |
|---|---|---|---|---|---|---|---|---|---|
| 1380 | left | clean | 3.0 | 3.7 | 3.7 | 3.4 | 3.4 | 3.4 |  |
| 1400 | left | clean | 5.9 | 5.5 | 5.3 | 3.6 | 3.6 | 3.6 |  |
| 1420 | left | clean | 5.7 | 4.5 | 4.3 | 5.2 | 4.9 | 4.7 |  |
| 1427 | left | failure | 7.1 | 5.1 | 5.3 | 6.4 | 5.5 | 7.1 |  |
| 1432 | left | failure | 8.1 | 5.3 | 5.2 | 7.8 | 7.8 | 8.1 |  |
| 1437 | left | failure | 11.8 | 5.5 | 5.5 | 10.6 | 10.8 | 11.8 |  |
| 1442 | left | failure | 10.2 | 5.8 | 6.6 | 13.4 | 12.9 | 10.2 |  |
| 1447 | left | failure | 12.7 | 7.0 | 6.9 | 13.7 | 13.3 | 12.7 |  |
| 1452 | left | failure | 12.5 | 5.2 | 6.9 | 14.2 | 13.8 | 12.5 |  |
| 1457 | left | failure | 13.1 | 4.0 | 6.7 | 11.3 | 13.5 | 13.1 |  |
| 1462 | left | failure | 13.7 |  | 7.3 | 14.0 | 14.3 | 13.7 |  |
| 1467 | left | failure | 13.1 |  | 6.2 | 12.0 | 12.5 | 13.1 |  |
| 1472 | left | failure | 13.8 |  | 6.0 | 10.5 | 10.6 | 13.8 |  |
| 1477 | left | failure | 13.3 |  | 6.7 | 12.9 | 12.7 | 13.3 |  |
| 1482 | left | failure | 13.9 |  | 7.3 | 14.1 | 14.3 | 13.9 |  |
| 1487 | left | failure | 13.4 |  | 6.7 | 12.6 | 12.9 | 13.4 |  |
| 1492 | left | failure | 13.8 |  | 6.3 | 12.8 | 12.6 | 13.8 |  |
| 1740 | right | clean | 6.9 | 2.9 | 3.0 | 5.0 | 5.0 | 5.0 |  |
| 1760 | right | clean | 5.5 | 5.1 | 5.0 | 7.5 | 7.5 | 7.5 |  |
| 1775 | right | failure | 5.0 | 7.4 | 7.3 | 11.4 | 10.6 | 5.0 |  |
| 1777 | left | failure | 16.2 | 6.0 | 6.5 | 6.3 | 7.4 | 12.6 |  |
| 1787 | left | failure | 19.1 | 23.5 | 7.2 | 6.7 | 8.1 | 19.1 |  |
| 1880 | right | failure | 13.6 | 0.8 | 15.7 | 11.1 | 17.4 | 5.5 |  |
| 1885 | right | failure | 13.7 | 1.1 | 15.6 | 11.3 | 17.8 | 5.4 |  |
| 1890 | right | failure | 15.2 | 1.1 | 17.3 | 14.0 | 20.4 | 5.0 |  |
| 1900 | right | clean | 13.4 | 0.6 | 0.6 | 0.9 | 0.9 | 0.9 |  |
| 1920 | right | clean | 10.2 | 1.2 | 1.3 | 0.7 | 0.7 | 0.7 |  |

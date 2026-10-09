# Recovered wrist against manual labels (R6B)

Recording: recording_20260831_065553. Labels: 21 wrists clicked by the user on natural failure-window frames inside grip episodes and 5 on clean frames outside the failure mask (the reference check). Truth is the clicked pixel deprojected with the aligned depth. Errors in cm, in the solver space. Methods: recovered = object-derived wrist estimate; measured = MediaPipe wrist on that frame; hold = last accepted MediaPipe wrist before the frame; plain_fk / hold_fk / recovery_fk = the wrist the angles of the plain, hold-last and recovery solves place.

## Natural failure windows

| side | method | n | median | p95 | max |
|---|---|---|---|---|---|
| right | recovered | 21 | 4.76 | 5.85 | 5.97 |
| right | measured | 3 | 5.87 | 6.44 | 6.5 |
| right | hold | 21 | 6.28 | 7.04 | 7.06 |
| right | plain_fk | 21 | 4.04 | 4.66 | 6.73 |
| right | hold_fk | 21 | 4.27 | 11.76 | 15.13 |
| right | recovery_fk | 21 | 4.96 | 5.97 | 10.24 |
| all | recovered | 21 | 4.76 | 5.85 | 5.97 |
| all | measured | 3 | 5.87 | 6.44 | 6.5 |
| all | hold | 21 | 6.28 | 7.04 | 7.06 |
| all | plain_fk | 21 | 4.04 | 4.66 | 6.73 |
| all | hold_fk | 21 | 4.27 | 11.76 | 15.13 |
| all | recovery_fk | 21 | 4.96 | 5.97 | 10.24 |

## Clean frames (reference check)

| side | method | n | median | p95 | max |
|---|---|---|---|---|---|
| right | recovered | 5 | 3.2 | 3.86 | 3.87 |
| right | measured | 5 | 4.28 | 4.69 | 4.75 |
| right | hold | 5 | 4.36 | 4.89 | 4.94 |
| right | plain_fk | 5 | 6.94 | 7.61 | 7.7 |
| right | hold_fk | 5 | 4.2 | 5.0 | 5.19 |
| right | recovery_fk | 5 | 9.12 | 9.91 | 10.1 |
| all | recovered | 5 | 3.2 | 3.86 | 3.87 |
| all | measured | 5 | 4.28 | 4.69 | 4.75 |
| all | hold | 5 | 4.36 | 4.89 | 4.94 |
| all | plain_fk | 5 | 6.94 | 7.61 | 7.7 |
| all | hold_fk | 5 | 4.2 | 5.0 | 5.19 |
| all | recovery_fk | 5 | 9.12 | 9.91 | 10.1 |

## Per frame

| frame | side | group | recovered | measured | hold | plain_fk | hold_fk | recovery_fk | mixed |
|---|---|---|---|---|---|---|---|---|---|
| 500 | right | clean | 1.8 | 2.5 | 2.5 | 6.9 | 2.7 | 9.1 |  |
| 520 | right | clean | 2.5 | 4.3 | 4.4 | 7.2 | 4.2 | 9.1 |  |
| 540 | right | clean | 3.2 | 4.8 | 4.7 | 7.7 | 4.1 | 10.1 |  |
| 550 | right | failure | 3.2 |  | 6.2 | 6.7 | 3.8 | 10.2 |  |
| 555 | right | failure | 3.3 |  | 6.5 | 4.3 | 4.3 | 3.3 |  |
| 560 | right | failure | 3.6 |  | 6.3 | 3.9 | 4.1 | 3.6 |  |
| 565 | right | failure | 3.3 |  | 6.2 | 4.0 | 4.2 | 3.3 |  |
| 570 | right | failure | 3.5 |  | 6.1 | 4.1 | 4.2 | 3.5 |  |
| 575 | right | failure | 3.7 |  | 6.0 | 4.0 | 4.0 | 3.7 |  |
| 580 | right | failure | 4.6 |  | 6.2 | 4.0 | 4.1 | 4.6 |  |
| 585 | right | failure | 5.2 |  | 6.2 | 4.0 | 4.1 | 5.2 |  |
| 590 | right | failure | 5.5 |  | 6.3 | 4.4 | 4.6 | 5.5 |  |
| 595 | right | failure | 5.1 |  | 6.2 | 4.2 | 4.2 | 5.1 |  |
| 600 | right | failure | 5.5 |  | 6.1 | 4.0 | 4.1 | 5.5 |  |
| 605 | right | failure | 5.8 |  | 6.7 | 4.6 | 4.6 | 5.8 |  |
| 610 | right | failure | 5.8 |  | 6.4 | 4.7 | 4.8 | 5.8 |  |
| 615 | right | failure | 5.2 |  | 6.2 | 4.3 | 4.7 | 5.2 |  |
| 620 | right | failure | 4.8 |  | 6.5 | 4.4 | 4.4 | 4.8 |  |
| 625 | right | failure | 5.0 |  | 7.0 | 4.5 | 4.4 | 5.0 |  |
| 630 | right | failure | 5.6 |  | 6.8 | 3.9 | 4.7 | 5.6 |  |
| 635 | right | failure | 6.0 |  | 7.1 | 3.9 | 15.1 | 6.0 |  |
| 674 | right | failure | 4.2 | 6.5 | 6.5 | 3.6 | 3.7 | 4.0 |  |
| 679 | right | failure | 4.2 | 5.9 | 6.8 | 3.6 | 5.9 | 3.5 |  |
| 684 | right | failure | 3.7 | 5.2 | 6.7 | 3.1 | 11.8 | 3.0 |  |
| 700 | right | clean | 3.9 | 4.4 | 4.9 | 4.2 | 4.2 | 4.2 |  |
| 720 | right | clean | 3.8 | 3.2 | 3.4 | 5.2 | 5.2 | 5.2 |  |

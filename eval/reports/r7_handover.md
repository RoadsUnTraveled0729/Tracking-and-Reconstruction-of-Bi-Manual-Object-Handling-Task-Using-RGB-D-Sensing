# Hand-over analysis: recording_20260909_000024 (r7)

Right hand carries and slides the cube to the middle of the rail, the
left hand takes over and slides it to the far end (supervisor round 6,
C50). Hand at the cube: a wrist within the hold radius of the cube
centre on a carried frame (measured wrist, or the recovery solve's
forward-kinematics wrist where the wrist was not measured). Errors are
perpendicular distances of the marker origin to the line fitted to all
slide samples (eval_rail_scenario.py), levelled by the carried-over
gravity of the recording of 2026-08-31 (E-034).

- slide frames 426-1498 (1072 frames), extent 42.4 cm, perpendicular median 0.26 / p95 1.65 / max 3.44 cm
- hand-over: left hand at the cube from frame 864, right hand until frame 1022 (5.27 s; both at the cube on 159 frames, runs [[864, 1022]]); at 29.4 to 34.5 cm along the 42.4 cm slide; the cube moves 5.3 cm meanwhile and is still on 113 frames

| part | frames | n | along rail (cm) | travel (cm) | perp median / p95 / max (cm) | vertical median (cm) | undetected / bridged | fail L / R / torso | root constrained |
|---|---|---|---|---|---|---|---|---|---|
| right | 426-863 | 438 | 0.0 to 29.7 | 29.7 | 0.71 / 2.1 / 3.44 | 0.21 | 1 / 7 | 0 / 0 / 163 | 220 |
| handover | 864-1022 | 159 | 29.2 to 34.5 | 5.3 | 0.28 / 1.35 / 1.66 | 0.12 | 0 / 3 | 0 / 0 / 131 | 159 |
| left | 1023-1498 | 476 | 34.6 to 42.4 | 7.8 | 0.1 / 1.15 / 2.37 | 0.05 | 0 / 2 | 63 / 0 / 32 | 38 |

Model wrists (forward kinematics of the recovery solve) per part:

| part | side | at cube (frames) | wrist to rail line median / p95 (cm), whole part | wrist to marker origin median / p95 (cm), at the cube only | swing measured / held / constrained, whole part | twist m / h / c, whole part | elbow m / h / c, whole part |
|---|---|---|---|---|---|---|---|
| right | left | 0 | 29.06 / 31.58 | n/a / n/a | 434 / 0 / 4 | 136 / 300 / 2 | 438 / 0 / 0 |
| right | right | 437 | 15.75 / 17.01 | 15.77 / 17.69 | 431 / 0 / 7 | 427 / 6 / 5 | 438 / 0 / 0 |
| handover | left | 159 | 12.66 / 13.11 | 15.85 / 24.21 | 159 / 0 / 0 | 159 / 0 / 0 | 159 / 0 / 0 |
| handover | right | 159 | 16.34 / 17.47 | 17.91 / 22.86 | 156 / 0 / 3 | 157 / 0 / 2 | 159 / 0 / 0 |
| left | left | 58 | 31.43 / 32.88 | 14.08 / 15.24 | 410 / 18 / 48 | 126 / 301 / 49 | 412 / 19 / 45 |
| left | right | 0 | 31.72 / 32.97 | n/a / n/a | 472 / 0 / 4 | 473 / 0 / 3 | 476 / 0 / 0 |

- FK wrist against the measured wrist (measured frames): right median 0.96 / p95 2.52 cm, left median 1.17 / p95 4.92 cm
- grip episodes (state machine): {"left": [[864, 1080]], "right": [[290, 1063]]}
- failure windows: {"arm_L": [[1156, 1218]], "arm_R": [], "torso": [[651, 758], [809, 965], [994, 1054]]}
- torso replaced (root constrained) runs: [[644, 1060]]; hip depth minus shoulder-mid depth on those frames (m): {"left_hip": {"min_m": -0.273, "median_m": -0.067}, "right_hip": {"min_m": -0.349, "median_m": -0.221}}
- rail level 0.0780 m, desk level 0.0337 m, rail above desk 4.43 cm; wrists substituted by the FK wrist: {'left': 0, 'right': 10}, handover boundary wrists measured: True
- object track: undetected [741], bridged runs [[436, 436], [668, 668], [674, 675], [680, 680], [741, 741], [757, 757], [989, 989], [1012, 1012], [1015, 1015], [1026, 1026], [1077, 1077]]

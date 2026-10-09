# Hip hold (E-034) against the ray repair: recording_20260831_065553 (r6b)

Three root policies on the same masked landmarks: raw (the hips as
measured, hold-last solve), ray (the pinned preparation: a rejected
hip on its camera ray at the remembered depth, E-011b/E-027), hold
(the rejected or unreported hip frozen at its last accepted
position, hip_hold=True). Windows are the frames on which either
policy replaced a hip. Spread is p95 minus p5 about the median.

## Frames 5-820 (816 frames)

| policy | root_ex spread / std (deg) | root_ey spread / std | root_ez spread / std | pelvis drift (cm) |
|---|---|---|---|---|
| raw | 15.34 / 5.52 | 57.57 / 19.68 | 10.79 / 3.49 | n/a |
| ray | 18.05 / 6.15 | 2.25 / 1.47 | 4.22 / 1.53 | 9.5 |
| hold | 21.69 / 7.33 | 3.06 / 1.03 | 0.35 / 0.12 | 0.0 |

- measured shoulder-midpoint drift over the window: 13.37 cm
- pelvis separation ray vs hold: median 8.01 cm, max 15.3 cm
- forward-kinematics wrist separation ray vs hold: right median 7.87 / max 30.29 cm, left median 0.42 / max 16.28 cm

## Frames 823-899 (77 frames)

| policy | root_ex spread / std (deg) | root_ey spread / std | root_ez spread / std | pelvis drift (cm) |
|---|---|---|---|---|
| raw | 7.97 / 2.94 | 11.62 / 5.56 | 2.91 / 0.88 | n/a |
| ray | 1.67 / 0.56 | 1.72 / 0.58 | 1.75 / 0.46 | 1.88 |
| hold | 2.12 / 0.7 | 0.01 / 0.0 | 0.0 / 0.0 | 0.0 |

- measured shoulder-midpoint drift over the window: 2.06 cm
- pelvis separation ray vs hold: median 3.36 cm, max 3.56 cm
- forward-kinematics wrist separation ray vs hold: right median 0.0 / max 0.0 cm, left median 7.23 / max 7.9 cm

## Whole recording

- frames with a replaced hip: 893; frames where any of the thirteen angles differs by more than 0.05 deg between the policies: 895
- largest per-angle difference (deg): root_ex 24.14, root_ey 38.68, root_ez 15.11, Rsh_y 179.7, Rsh_z 16.23, Rsh_tau 89.29, Rel_y 0.0, Rel_z 0.0, Lsh_y 21.33, Lsh_z 17.77, Lsh_tau 22.55, Lel_y 0.0, Lel_z 0.0
- root tagged constrained: ray 893, hold 893 frames
- solver counters: {"ray": {"gated": {"right_hip": 893, "left_hip": 892}, "ray_fixed": {"left_hip": 891, "right_hip": 891}, "occluder_fixed": {"right_hip": 2, "left_hip": 1}}, "hold": {"gated": {"right_hip": 893, "left_hip": 892}, "hip_held": {"right_hip": 893, "left_hip": 892}, "ray_fixed": {}}}

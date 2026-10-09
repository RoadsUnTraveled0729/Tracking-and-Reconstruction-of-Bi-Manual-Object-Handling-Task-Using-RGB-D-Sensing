# Hip hold (E-034) against the ray repair: recording_20260909_000024 (r7)

Three root policies on the same masked landmarks: raw (the hips as
measured, hold-last solve), ray (the pinned preparation: a rejected
hip on its camera ray at the remembered depth, E-011b/E-027), hold
(the rejected or unreported hip frozen at its last accepted
position, hip_hold=True). Windows are the frames on which either
policy replaced a hip. Spread is p95 minus p5 about the median.

## Frames 644-1060 (417 frames)

| policy | root_ex spread / std (deg) | root_ey spread / std | root_ez spread / std | pelvis drift (cm) |
|---|---|---|---|---|
| raw | 25.87 / 7.49 | 98.31 / 30.6 | 6.7 / 1.96 | n/a |
| ray | 4.28 / 2.54 | 4.59 / 4.16 | 2.64 / 0.85 | 8.85 |
| hold | 4.04 / 1.43 | 0.13 / 0.35 | 0.03 / 0.04 | 1.4 |

- measured shoulder-midpoint drift over the window: 5.77 cm
- pelvis separation ray vs hold: median 2.05 cm, max 7.4 cm
- forward-kinematics wrist separation ray vs hold: right median 0.0 / max 23.34 cm, left median 0.0 / max 7.75 cm

## Whole recording

- frames with a replaced hip: 417; frames where any of the thirteen angles differs by more than 0.05 deg between the policies: 419
- largest per-angle difference (deg): root_ex 21.18, root_ey 39.62, root_ez 4.34, Rsh_y 61.06, Rsh_z 11.71, Rsh_tau 41.05, Rel_y 0.0, Rel_z 0.0, Lsh_y 44.82, Lsh_z 13.49, Lsh_tau 39.76, Lel_y 0.0, Lel_z 0.0
- root tagged constrained: ray 417, hold 417 frames
- solver counters: {"ray": {"gated": {"right_hip": 416, "left_hip": 413, "left_wrist": 1}, "ray_fixed": {"left_hip": 413, "right_hip": 408}, "occluder_fixed": {"right_hip": 8}}, "hold": {"gated": {"right_hip": 416, "left_hip": 413, "left_wrist": 1}, "hip_held": {"right_hip": 416, "left_hip": 413}, "ray_fixed": {}}}

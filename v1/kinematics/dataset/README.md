# Verified synthetic datasets

## Blocked-landmark (occlusion) chain fallback (2026-07-18)

`occlusion_masked/`: synthetic-occlusion datasets built by masking
landmarks of the verified 20260224 recording (KINEMATIC_MODEL.md §10);
truth = the unmasked solve, so every check is exact.
`../make_masked_dataset.py` regenerates them; `../validate_occlusion.py`
re-runs the 33 checks (pinned output: `validate_occlusion_output.txt`,
ALL PASS).

| File | What it is |
|---|---|
| `masked_wrist_short.csv` | RAW csv, R wrist gap frames 300-302 — repaired by the filter (flag 2, wrist within 0.30 mm, angles within 0.08°). |
| `masked_wrist_long.csv` | R wrist blocked 400-444 — twist+elbow hold, swing/root/left arm live and EXACT, recovery exact. |
| `masked_elbow_long.csv` | R elbow blocked 500-544 — whole R arm holds, rest live. |
| `masked_hip.csv` | L hip blocked 600-629 — root holds; arms keep solving against the held root (exact vs independent recompute). |
| `masked_root_ref.csv` | R shoulder blocked 750-779 — root stays live via the LEFT shoulder (deviation ≤1.53°); R arm holds. |
| `masked_pose_loss.csv` | ALL landmarks blocked 700-709 — everything holds, exact recovery. |
| `masked_all_windows.csv` | all filtered-source windows combined — the Unity demo stream. |
| `recording_20260224_083945_landmarks_raw_v2.csv` | re-extraction with the visibility gate + 5×5 median depth: 19 low-vis cells caught (warm-up hallucinations frames 0-9), 1 depth-hole wrist recovered, positions unchanged (median 0.00 mm). |
| `unity_occlusion_fallback.mp4` | rig playing the combined masked stream (PSA5): held joints freeze with red marker spheres while everything else keeps tracking live. |
| `unity_mask_log.csv` | per-frame Unity-side log of the live mask + marker states: all 899 frames, every window's mask/markers exact. |
| `held_wrist_hold.png` / `held_elbow_hold.png` / `held_hip_hold.png` / `held_pose_loss.png` | stills from the video inside each window: red spheres exactly on the held joints, rest of the body live. |

## Left arm (mirror) validation (2026-07-17)

Left-arm angles are the sagittal mirror of the right solve
(KINEMATIC_MODEL.md §9). Truth CSVs of all five datasets carry
`l_sh_*` / `l_elbow_*` columns.

| File | What it is |
|---|---|
| `arm_both_landmarks.csv` / `_truth.csv` | torso + BOTH arms moving, left on deliberately different phases (frame 742: all 12 angles nonzero). Decodes ≤2.6e-13 deg. |
| `unity_arm_both.mp4` | rig with both arms + torso reproducing the dataset live (PSA4 bridge). |
| `arm_both_allangles.png` | held frame 742 — both arms posed independently. |
| `real_20260225/unity_real_both_arms.mp4` | the real recording driving hip + both arms live next to the marker skeleton. |

## Real recording 20260224 ("complex") + per-frame rig error (2026-07-17)

`real_20260224/`: recording_20260224_083945.bag through the full pipeline
(897/899 usable frames; 0-1 lack left-arm landmarks). Math ALL PASS
(reconstruction ≤6.4e-14 deg). `unity_frame_log.csv` is the per-frame
measurement of the rig itself (ArmAngleLogger): 897/897 frames displayed,
max angular error 0.0001 deg on every segment, 0 frames off by >0.1 deg —
see KINEMATIC_MODEL.md §8.1.

## Elbow swing validation (2026-07-17)

Known-truth datasets for the RIGHT-elbow swing solve in the L14 upper-arm
frame (`../shoulder.py::solve_right_arm`, KINEMATIC_MODEL.md §7). Truth
CSVs of all four datasets now carry `elbow_y`/`elbow_z` columns (ez ≡ 0 by
derivation — the elbow "up/down" swing is the shoulder twist).

| File | What it is |
|---|---|
| `elbow_only_landmarks.csv` / `_truth.csv` | torso+shoulder swing fixed: flexion ey −10..−150 (0–10 s), shoulder twist ±80 rotating the flexion plane (10–20 s), both together (20–30 s). |
| `arm_full_landmarks.csv` / `_truth.csv` | root + shoulder (3 angles) + elbow flexion all moving; 24–30 s has every angle nonzero simultaneously. |
| `unity_arm_elbow_only.mp4` / `unity_arm_full.mp4` | rig reproducing both datasets live (PSA3 bridge). |
| `elbow_straight.png` | held ey=0: arm perfectly straight (forearm continues the arm axis, 0.02° err). |
| `arm_full_allangles.png` | held arm_full frame 742: root (8.0, −171.7, 5.8) + shoulder (27.8, 30.0, 32.4) + elbow −100.4; both bone dirs match the dataset's landmark dirs to 4 decimals. |

Pinned results: full-pipeline decode vs truth, elbow err ≤2.8e-13 deg over
all four datasets; ez=30 injection re-attributes to twist −30 with the
identical forearm direction (5.6e-17).

## Shoulder swing–twist validation (2026-07-14)

Known-truth datasets for the RIGHT-shoulder swing–twist solve
(`../shoulder.py`, KINEMATIC_MODEL.md §6). 900 frames @ 30 fps each, elbow
held at 90° flexion so twist is observable; generated deterministically by
`../make_synthetic_shoulder_motion.py`.

| File | What it is |
|---|---|
| `shoulder_only_landmarks.csv` | torso fixed at (0,180,0); right arm sweeps θy ±60° (0–8 s), θz ±60° (8–16 s), θτ ±80° (16–24 s), combined (24–30 s). Sensor space, extractor layout. |
| `shoulder_only_truth.csv` | injected root Euler + shoulder (θy, θz, θτ) per frame. |
| `shoulder_torso_landmarks.csv` | the SAME arm trajectory composed with a moving root (yaw ±25°, pitch ±15°, roll ±15°, combined) — tests the solve under a time-varying parent frame. |
| `shoulder_torso_truth.csv` | injected root + shoulder angles per frame. |

Pinned results (`../validate_shoulder.py`, ALL PASS): full-pipeline decode
vs truth max error 8.5e-14 deg (shoulder_only) / 2.0e-13 deg
(shoulder_torso, root simultaneously exact to 1.1e-13 deg); known poses,
gimbal fold-into-twist, and straight-elbow unobservability all behave as
derived.

Unity proof (2026-07-17, `../send_arm_angles.py` → `ArmAngleReceiver.cs`):

| File | What it is |
|---|---|
| `unity_arm_shoulder_only.mp4` | rig right arm reproducing the shoulder_only dataset live (torso fixed). |
| `unity_arm_shoulder_torso.mp4` | rig reproducing shoulder_torso — torso and arm moving simultaneously. |
| `arm_pose_reference.png` | held rest pose: arm out to the person's right, elbow bent, forearm toward camera. |
| `arm_pose_forward.png` | held θy=−90: arm forward, forearm folded across (zero-twist behavior). |
| `arm_twist_p90.png` / `arm_twist_m90.png` | held twist ±90: forearm straight down (internal) / straight up (external). |
| `arm_complex_allangles.png` | held frame 742: ALL six angles nonzero — root (8.0, −171.7, 5.8) + shoulder (27.8, 30.0, 32.4); bone dirs verified against the landmark dirs to 0.02°. |

## Root-frame end-to-end validation (tag0)

Snapshot of the known-truth dataset and proof artifacts that verified the
L24 root-frame construction, the sensor→Unity mapping, and the Unity
ZXY-applied Euler convention end-to-end (2026-07-13). Conventions and
derivations: `../../KINEMATIC_MODEL.md` §3–5.

Regenerate at any time with `python ../make_synthetic_motion.py`
(deterministic — no randomness); this folder pins the exact copy that was
validated, so the checked numbers below stay reproducible against it.

## Files

| File | What it is |
|---|---|
| `synthetic_landmarks.csv` | 900 frames @ 30 fps, 8 torso/arm landmarks of a rigid body in **sensor space** (RealSense optical frame, meters), extractor CSV layout. Motion: yaw ±30° (0–8 s), pitch ±20° (8–16 s), roll ±20° (16–24 s), combined (24–30 s). |
| `synthetic_angles_truth.csv` | The injected ground-truth Euler angles (Unity ZXY-applied convention) per frame. |
| `synthetic_motion.mp4` | Matplotlib 3D animation of the ground-truth motion (pipeline input as seen by the sensor). |
| `unity_rig_root_rotation.mp4` | Unity capture: raw-landmark marker skeleton + angle-driven rig hip reproducing the same motion in sync. |
| `pose_reference.png` | Held reference pose — rig upright facing the camera (sent Euler (0, 180, 0)). |
| `pose_yaw_p30.png` | Held yaw +30° pose. |
| `pose_pitch_p20.png` | Held pitch +20° pose (bow). |
| `pose_roll_p20.png` | Held roll +20° pose (lean). |

## Verified results pinned by this snapshot

- Pipeline decode (`send_root_angles.py --truth ... --check-only`) vs
  injected truth: max error **1.137e-13 deg** over all 900 frames.
- Frame-matched Unity bone rotations equal `Quaternion.Euler(sent) * C`
  exactly (e.g. frame 152: sent (0, 157.706, 0) → bone world
  (6.556, 337.706, 0)).
- det(R) = +1 on every frame; orthonormality residual ~1e-16;
  Euler round-trip (decode → recompose) exact to ~1e-16.

Real-time phase artifacts (the GPU-vs-CPU benchmark, the vectorized
solver) live in `../../realtime/` — this offline dataset is thesis
material and stays as-is.

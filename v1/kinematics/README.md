# kinematics — root frame math and verification

Math conventions and derivations live in `../KINEMATIC_MODEL.md`; this
directory holds the implementation and its verification tooling.

## Files
- `root_frame.py` — shared module: sensor→Unity point mapping, L24 root-frame
  construction, Unity ZXY-applied Euler decode/recompose (§3–4 of the model doc).
- `validate_root_frame.py` — validation on a synthetic reference pose plus the
  real recording (determinant, orthonormality, Euler stats, round-trip,
  gimbal decode). Run: `python validate_root_frame.py [landmark_csv]`.
- `make_synthetic_motion.py` — generates a rigid 8-landmark body animated by
  KNOWN Euler trajectories (yaw/pitch/roll phases), written in sensor space
  with the extractor's CSV layout, plus a ground-truth angle CSV. Output in
  `output/` (gitignored).
- `send_root_angles.py` — computes root Euler angles from any landmark CSV
  through the real pipeline and streams them to Unity via shared memory
  (`/dev/shm/pose_angles`, 32-byte seqlock packet; layout in the docstring
  and mirrored in `Unity/Assets/Scripts/RootAngleReceiver.cs`).
  `--truth x.csv --check-only` runs the ground-truth comparison alone.
- `shoulder.py` — arm solves for BOTH sides: right shoulder swing-twist
  (§6, R_sh = Ry·Rz·Rx, twist innermost about the arm axis, measured from
  the un-swung forearm in the plane ⊥ the axis), right elbow swing (§7,
  solve_right_arm: R_elbow = Ry·Rz in the L14 upper-arm frame; ez ≡ 0
  under the twist convention), and the left arm as its sagittal mirror
  (§9, solve_left_arm: reflected vectors into the same solver).
- `make_synthetic_shoulder_motion.py` — five known-truth datasets:
  `shoulder_only` (torso fixed, arm sweeps θy±60/θz±60/θτ±80 + combo),
  `shoulder_torso` (same arm motion under a moving root), `elbow_only`
  (flexion sweep, then twist rotating the flexion plane, then both),
  `arm_full` (root + shoulder + elbow all moving simultaneously),
  `arm_both` (torso + both arms, left on distinct phases).
- `validate_real_recording.py` — no-truth validation on a real landmark
  CSV: frame invariants, exact-inverse reconstruction of all four segment
  directions from the solved angles, plausibility stats.
- `validate_shoulder.py` — known poses, gimbal + straight-elbow behavior,
  numeric refutation of the draft ZX-plane twist, and full-pipeline decode
  of both datasets vs truth (ALL PASS, ≤2e-13 deg).
- `send_arm_angles.py` — streams root Euler + shoulder swing-twist +
  provisional elbow hinge to Unity (`/dev/shm/pose_arm`, 48-byte 'PSA2'
  seqlock packet; mirrored in `Unity/Assets/Scripts/ArmAngleReceiver.cs`,
  which drives DEF-spine + DEF-upper_arm.R + DEF-forearm.R).
- `dataset/` — committed snapshot of the verified synthetic dataset + proof
  videos/screenshots (git tag `tag0`); see `dataset/README.md`. `output/`
  stays gitignored as regenerable scratch.

## End-to-end verification recipe (2026-07-13, all PASS)
1. `python make_synthetic_motion.py`
2. `python send_root_angles.py --truth output/synthetic_angles_truth.csv --check-only`
   → max decode error 1.1e-13 deg over 900 frames.
3. `python ../mediapipe/plot_skeleton.py --csv output/synthetic_landmarks.csv
   --save output/synthetic_motion.mp4 --no-show` → ground-truth animation.
4. Unity: open scene `rig`, enter Play mode; run `send_root_angles.py` (and
   optionally `../unity_bridge/send_landmarks.py --csv output/synthetic_landmarks.csv`
   for the marker skeleton) → rig hip reproduces the motion;
   capture: `output/unity_rig_root_rotation.mp4`.

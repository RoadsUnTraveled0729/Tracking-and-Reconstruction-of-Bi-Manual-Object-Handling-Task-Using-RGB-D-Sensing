# System preconditions and assumptions

Every physical or statistical assumption the system rests on, each
traced to where it is used in code, where it is measured or
validated, and what breaks when it is violated. The thesis
preconditions section draws from this file; keep it updated in the
same commit as any change that adds or removes an assumption.

Status legend: MEASURED (checked against data on the current primary
recording), VALIDATED (asserted by a validator), ASSUMED (declared,
not independently checked), USER-SET (a value chosen by the user,
traceable and revisable).

## A. Body model

A1. Skeleton segment lengths are fixed (bones are rigid).
- Used: angle-space holding keeps bone lengths exact by construction
  (v1/kinematics/occlusion.py docstring); segment-length gate and
  sphere recovery at every chain link
  (v1/kinematics/occlusion_ext.py); grip-fit forearm sanity gate
  (eval/offset/carry.py forearm_ok, E-007).
- Measured: online per-segment calibration (median of first 60 clean
  samples, occlusion_ext.py) and offline medians
  (eval/offset/carry.py seg_lengths); R4 values are left-right
  symmetric (forearms 0.228/0.221 m, upper arms 0.272/0.273 m).
- If violated: gating would reject good data (tolerance is 30
  percent, gate_tol in occlusion_ext.py); holding would distort
  reach.

A2. The torso is approximately a rigid body: hip width, shoulder
width, and the four hip/shoulder-to-opposite-midpoint diagonals are
constant, and the hip line stays near-parallel to the shoulder line
(axial spine twist bounded: 18.9 deg maximum over all of R1).
- Used: root-frame construction needs the hip line
  (v1/kinematics/root_frame.py build_root_frame); pair-violation
  attribution and contralateral hip/shoulder recovery
  (occlusion_ext.py PAIRS, DIAGONALS); the torso line-consistency
  gate rejects hip/shoulder line rotations that exceed what a rigid
  torso can do (occlusion_ext.py line_tol_deg = 20, hysteresis
  release 10, thresholds from the R1-clean vs R4-corrupt
  distributions - eval/DECISIONS.md E-011).
- Measured: online calibration of the six torso lengths
  (occlusion_ext.py); shoulder width / torso medians in
  eval/offset/carry.py.
- If violated (clothing shift, extreme bending, real axial twist
  beyond 20 deg): the line gate constrains the root to the surviving
  line (honest CONSTRAINED tag); a real sustained twist would be
  under-reported by up to the twist magnitude.

A3. The elbow has one rotational DOF (flexion); no lateral bend
(ez identically 0). Four observable rotational DOF per arm.
- Used: v1/kinematics/shoulder.py solve_right_arm (lines ~101-108).
- Validated: exact-inverse reconstruction checks
  (validate_real_recording.py); elbow ey range check.
- If violated: irreducible reconstruction error at the wrist.

A4. Shoulder twist is unobservable at a straight elbow
(amplification 1/sin(flexion)).
- Used: TWIST_EPS flag in shoulder.py; twist hold in occlusion.py.
- Validated: thesis/check_limits.py section 1; thesis/D1 section 1.
- If ignored: 11x noise amplification at 5 deg flexion (measured).

A5. MediaPipe landmarks correspond to joint centers, one person in
frame, generally facing the camera.
- Used: everywhere upstream (extract_landmarks_to_csv.py, live
  pipelines); left/right disambiguation via the mirror solver.
- Assumed: not independently verified; facing deviation measured 4.5
  deg on R1 (pinned Ch6 number).

A6. MediaPipe is actually tracking the evaluated landmarks
(USER-SET precondition 2026-08-25, eval/DECISIONS.md E-013): an
accuracy-evaluation window is valid only where the landmarks it
grades are tracked - coverage >= 95 percent and no continuous gap
longer than 0.5 s over the person-present span. The torso must pass
for any evaluation; each hand's elbow+wrist must pass for that
hand's windows.
- Enforced: eval/inspect/check_tracking_precondition.py (run right
  after extracting any new recording; exits nonzero on failure).
- Status: R1 passes everything. R4 passes torso and the right hand;
  the LEFT hand FAILS (wrist coverage 55.4 percent, longest gap
  8.8 s - the left-carry phase is occluded by the carried cube) and
  is out of evaluation scope in R4.
- Synthetic occlusion evaluation masks tracked segments, retaining
  the hidden measurement as the reference. Natural failure windows
  are also evaluated quantitatively where manual wrist labels exist:
  [loop labels](eval/reports/r5_recovery_labeled.md) and
  [rail labels](eval/reports/r6b_recovery_labeled.md). Unlabelled
  natural windows remain qualitative; labels have their own reference
  uncertainty and are not a motion-capture ground truth.

## B. Measurement trust

B1. A landmark with visibility below 0.5 is unreliable; its position
is discarded (wrong becomes missing).
- Used: extract_landmarks_to_csv.py --min-vis; live pipelines.
- Measured limitation (R4): high visibility does NOT imply a correct
  depth - 167 right-wrist depth-collapse samples pass every
  visibility threshold up to 0.7 (eval/reports/r4_gate_sweep.md).
  This motivates B2.
- Sensitivity: threshold sweep pinned in the same report.

B2. A measured segment length more than 30 percent off its
calibrated value marks the distal endpoint as wrong (physics
overrides image confidence).
- Used: occlusion_ext.py gate (gate_tol = 0.30); eval fit gate
  (E-007, FOREARM_TOL).
- Validated: validate_occlusion_ext.py (unit + scenario checks);
  clean-right-arm neutrality on R1.
- If tolerance too tight: good data rejected; too loose: depth
  collapse passes. 30 percent sits far from both observed
  populations (real noise a few percent, collapse 40-90 percent).

B3. Depth (RealSense aligned z) is metric and consistent over time.
- Used: deprojection of all landmarks; the tabletop gravity seed;
  the PnP-vs-depth cross-check that exposed the marker-size issue.
- Measured: R1 PnP/depth ratios 0.999-1.008 with correct markers;
  limb lengths consistent R1 vs R4.

B4. During an occlusion gap, a held joint keeps its last measured
angle; a recovered joint follows its remembered direction at
calibrated length for at most the horizon (45 frames), then holds.
- Used: occlusion.py (hold); occlusion_ext.py (recovery, H).
- Validated: 33-check occlusion suite (hold);
  validate_occlusion_ext.py (recovery beats hold at every chain
  level on the R1 scenarios).
- Known cost: hold drift equals true motion during the gap (1.4-7.8
  deg on the R1 windows); recovery error grows with direction-memory
  staleness.

B5. Estimates are never presented as measurements: held and
recovered values carry cleared live-mask bits and tags (held /
constrained / fusion-display-only flag 9); fusion filling is
display-only and firewalled out of statistics.
- Used: occlusion.py live mask; occlusion_ext.py tags;
  eval/occlusion/fusion_display.py.
- Validated: validate_eval.py firewall checks;
  validate_occlusion_ext.py honesty checks.

## C. Scene and markers

C1. Markers are planar squares of known black-square side length;
the marker size constant describes the DETECTED black square, not
the printed card.
- Used: PnP in v1/aruco (frames.py MARKERS); all object/world
  positions scale linearly with it.
- USER-CONFIRMED: printed desk and object black squares are 45 mm
  (2026-09-01 and 2026-09-25; [standing rule](AGENTS.md)). The frozen
  detector declares 0.050 m at PnP time;
  [scale correction](eval/gt/scale_correction.py) multiplies every
  desk and object translation by 0.9 before calibration, using
  [marker_size.py](eval/common/marker_size.py). All thesis numbers
  use the 45 mm scale. Earlier E-009/E-009a assumption labels in
  pinned artifacts are historical provenance; the size is settled.

Historical E-009/E-009a assumption text (superseded by the confirmed
size above; retained as the original diagnostic record):

- USER-SET (R4): desk and object black squares assumed 45 mm
  (declared 50 mm in frozen frames.py). Single source:
  eval/common/marker_size.py; every derived artifact carries the
  assumption label; regeneration commands in that module's
  docstring. Depth diagnostic implies 43.6 mm (= 50 x 7/8,
  consistent with a quiet-zone-inclusive print); ruler measurement
  of the black square settles it (E-009/E-009a).

C2. The desk marker is static and defines the world frame; the wall
marker is static, mounted upright, and its in-plane up axis defines
gravity (seeded and sanity-bounded by the depth tabletop normal,
agreement bound 11 deg).
- Used: calibrate_scene.py; every world-frame quantity.
- Validated: validate_aruco.py static-stability and gravity checks
  (R4: desk pos p95 1.3 mm, seed agreement 4.4 deg).

C3. The tabletop is a horizontal plane.
- Used: gravity seed (extract_aruco_poses.estimate_tabletop);
  height-above-table logic (leveled frame).
- Assumed: spirit-level checked physically by the user (photo).

C4. The camera is stationary per recording; factory color
intrinsics hold.
- Used: PnP, deprojection.
- Measured: identical recorded intrinsics R1/R4; camera-invariance
  checks in validate_aruco.py.

C5. The manipulated object is a rigid 70 mm cube with the marker
centered on one face; box center = marker + R x (0, -cube/2, 0).
- Used: analyze_object_offset.py:112, eval/offset/carry.py
  box_center, Unity receiver.
- ASSUMED: cube size passed explicitly (--cube-size 0.07); the
  half-cube offset direction fixed by the mounting convention.

## D. Evaluation-specific (eval/ track)

D1. While a hand holds the box, the wrist-to-box-center vector is
rigid; on R4 this holds piecewise between regrips, and its MAGNITUDE
is the robust invariant (std 0.6-2.0 cm per grip episode).
- Used: stage-2 constancy metric; box+offset evaluation reference.
- Measured: eval/reports/r4_stage4_ground_truth.md.

D2. A wrist within 0.25 m of the box center on a carried frame is
holding it (bimodal separation: holding 14-22 cm, free 40+ cm).
- USER-REVIEWABLE: E-005; constant HOLD_RADIUS in
  eval/offset/carry.py.

D3. Carried means: inside the manipulation envelope and away from
the rest positions (or moving, or lifted).
- E-006; constants in eval/offset/carry.py.

D4. Dwell means: box-center speed below 2 cm/s sustained 0.5 s on
carried frames.
- E-008 (UNCERTAIN, user-tunable); constants in
  eval/gt/analyze_gt_path.py.

D5. The surveyed labeled path and the desk-marker frame are the same
frame; the wall-marker closure check demonstrates it.
- PENDING SURVEY: eval/gt/labeled_path.json.

## E. Runtime

E1. Offline zero-phase filtering is legal only offline; the live
path substitutes causal filters and accepts their measured lag.
- Used: filter_landmarks.py vs CausalLandmarkFilter;
  thesis/D1 section 10.

E2. The sensor delivers 640x480 depth+color at a steady 30 fps
(frame-count windows assume it).
- Measured: inter-frame jitter p99 33.4 ms on R4 (broker output).

# Decisions

Design/approach decisions and why, one-liner per entry, most recent first.

- 2026-07-24 (real-time phase = own realtime/ folder, offline tree
  frozen): on user request the whole real-time phase moved out of the
  offline pipeline folders into realtime/ (person/ object/ integration/
  bench/ dataset/ output/) — the offline pipelines are the thesis's
  major part and must stay untouched; realtime code only READS them
  (modules via ROOT-relative sys.path, outputs, frozen calibration) and
  keeps the A/B independence split (realtime/integration/ is the only
  reader of both). Verified after the move: full run + 11-check
  validator ALL PASS, selftest, bench smoke.
- 2026-07-24 (real-time = CPU compute, process-level parallelism, causal
  filters, receiver unchanged): the solve stays plain numpy per frame
  (0.2 ms = 0.6% of budget; bench_solver.py shows GPU loses N=1 by 3-4
  orders via launch+transfer, L/R-arm threads lose to handoff overhead —
  the parallelism that pays is A/B as separate processes + MediaPipe on
  GPU). Zero-phase filters replaced causally: trailing Hampel (with
  3-reject re-seed against lockout + 35 mm onset floor) + One-Euro
  (min_cutoff retuned 0.05->1 Hz: lag 9->3 frames); object rotation via
  geodesic complementary filter. A/B start through a barrier
  (--sync-file) so both playbacks begin together (else 567 ms skew);
  merger (now realtime/integration/realtime_integrate.py) pairs latest samples and
  re-emits the OFFLINE PSB3+PSI1 contract so Unity needs no change.
- 2026-07-24 (thesis material = separate thesis/ folder, Markdown+LaTeX):
  thesis-grade rewrites (full derivations, one notation defined in
  00_notation.md, every number tied to a pinned artifact) live in
  thesis/ — 00 notation, A1 acquisition/filtering, A2 kinematic model,
  A3 occlusion, B1 ArUco, C1 integration/evaluation, D1 limitations
  (each limitation statement→math→evidence→mitigation, laws verified
  numerically by thesis/check_limits.py). Format: .md with $$ math —
  agent-accessible + GitHub-renderable; professor's Word review via
  pandoc (recipe in thesis/README.md; pandoc not currently installed).
  Working docs (KINEMATIC_MODEL.md etc.) stay the canonical repo record.
- 2026-07-23 (system accuracy = residual after PER-HAND grip decoupling,
  carried frames only): the object-vs-wrist offset is constant only in
  the object's co-rotating frame and only per holding hand (right-hand
  std < 2 cm/axis; world-frame azimuth swings ±178°), and only while the
  box is actually carried (its own height above the tabletop splits
  carried/resting unambiguously — resting frames have no grip to model).
  Accuracy statement: wrist vs (marker + R_obj·d̄_hand) residual, median
  3.3 cm / RMS 4.2 cm, floor ~1.0 cm on the visibility-clean right-hand
  stretch (OBJECT_OFFSET.md §5, analyze_object_offset.py).
- 2026-07-23 (Pipeline B object-track filter + live-flag semantics):
  aruco/filter_object_track.py (own code, pipeline independence) bridges
  interior detection gaps (position linear, rotation SO(3) geodesic —
  matrices/axis-angle only) and smooths with Savitzky-Golay (position) +
  rolling chordal mean (rotation); senders now apply the pose from EVERY
  row of a filtered CSV and use `detected` purely as the live/red-tint
  honesty flag (raw CSVs still fall back to hold-last on NaN rows).
  Why: hold-last + re-acquire popped up to 2.2 cm/3.4° on the video and
  the user asked for polynomial frame-to-frame smoothing. Guard:
  validator asserts filtered stays < 15 mm from raw detections; accuracy
  stats are computed on measured frames only.
- 2026-07-23 (landmark filter --edge-fill): leading/trailing NaN runs
  (sensor warm-up, e.g. visibility-gated hallucinated left arm frames
  0-9) are backfilled with the nearest valid sample BEFORE smoothing;
  interior interpolation alone left them empty, so the solver held rest
  and snapped 60° in one frame when the arm went live. The 20260224
  filtered_v2 CSV is regenerated with --edge-fill 12; all 899 frames now
  solve live (mask 127).

- 2026-07-19 (user process rule: PLOT IN PYTHON BEFORE UNITY): every
  quantity streamed to Unity must first be drawn and sanity-checked in
  Python against physical reality (integration/plot_integrated_scene.py:
  scene geometry + trajectories + person axes in the leveled desk world,
  with printed facing/clearance/verticality numbers). Reason: the rig
  anchor conjugation bug (below) passed every positional check and 17/17
  validation while rendering the person facing the wrong way — only a
  picture of the data exposed that the DATA was right and the RENDER was
  wrong. Matching assertions (facing, desk clearance) now live in
  validate_integration.py so the class of bug is caught headlessly too.
- 2026-07-19 (rig anchor composition = PRE-multiply, not conjugate):
  bone.rotation = qA·qChain·C_rest (C_rest = authored rest captured at
  spawn, body axes = scene axes). The first implementation used
  qA·qChain·qA⁻¹·C_rest, which cancels the camera orientation out of the
  pose — the rig stood scene-upright but faced ~the camera-yaw away from
  the desk with its legs in the table, while hip POSITION checks all
  passed (position doesn't see orientation). Data-level truth: person
  forward vs pelvis→sensor mean 4.5 deg. Desk slab extent made
  data-driven at the same time (marker→object-projection span + margins,
  not a fixed centered 0.8 m box) — pelvis clears the far edge +22.9 cm.
- 2026-07-19 (gravity = wall-referenced, user-asserted; supersedes
  depth-fit-as-authority): the wall is physically plumb, so the
  calibrated wall marker's in-plane up axis IS gravity (~1 deg accuracy
  vs ~5 deg for the depth fit) — the reconstructed wall is exactly
  vertical and the desk top exactly horizontal BY CONSTRUCTION (verified
  0.0000 deg in-scene). The depth tabletop fit is demoted to a seed
  (sign + wall-lobe disambiguation, needs only ~10 deg): desk-marker
  annulus always, object annulus joins only when its plane agrees within
  15 deg (rejects the hand-held box sweeping the person — in 20260224 it
  bent "gravity" 60+ deg). The desk-marker card tilt is INTENTIONAL
  (user: reduces foreshortening for corner precision) — 31.8 deg on the
  20260328 stand, flat 4.75 deg in 20260224. Cube edge re-measured under
  wall gravity: 70 mm (was 82 under the tilted depth gravity);
  calibrate_scene --cube-size covers hand-held-only recordings.
- 2026-07-19 (integration recording = 20260224, carried object): the
  person actually moves the cube (3.35 m travel), enabling the carried-
  object consistency check: on in-motion frames the object stays median
  14.9 cm from the nearest wrist with velocity correlation r=0.82 /
  direction cosine 0.83 — Pipeline B's object track shadows Pipeline A's
  wrist track through the calibrated anchor with zero shared code
  (validate_integration.py section 6, 17/17). Camera-placement lesson
  banked: the desk-edge camera beats the high camera on every metric
  (wall invariance rot p95 0.54 vs 2.4 deg).
- 2026-07-19 (integration layer, not a pipeline merge): the person+scene
  demo lives in integration/ + IntegratedSceneReceiver.cs and only READS
  both pipelines' outputs (A: filtered landmarks -> occlusion.py angles;
  B: world CSV + calibration) — A and B stay independent per policy. The
  person→scene map is one static proper rotation M = P·R_desk_cam·
  diag(1,−1,1) = R_unity(camera)·Rx(−90°), so Unity just parents a
  PersonAnchor at the calibrated camera pose ∘ Rx(−90°) and captures bone
  rest rotations RELATIVE to it (C = qA⁻¹·rest, bone = qA·chain·C —
  reduces to the validated PSA5 composition at qA = I). Person + object
  ride in ONE 108 B 'PSI1' packet so they cannot desynchronize; frames
  align 1:1 because both CSVs come from the same bag. Validated 13/13
  (anchor maps person-up onto scene gravity to 7e−16; Unity hip lands on
  the mapped pelvis to 0.0009 mm reproduced from first principles).
  INTEGRATION.md.
- 2026-07-19 (IPPE lobe choice = lobe-separation policy; supersedes the
  depth-plane tiebreak below): reprojection error is trusted ONLY when
  the two IPPE lobes are >= 40° apart (desk 64°, object 62°). For
  near-degenerate lobes (wall: 23° at 32 px) reprojection is a BIASED
  discriminator — it picked the anti-plumb lobe on 815/837 frames with
  ratios up to 2.18, overlapping the well-conditioned markers' genuine
  2.15–3.9, so no ratio threshold works; the depth tiebreak that shipped
  first was ALSO wrong (in-quad depth normal at 3 m is >30° biased and
  systematically picked the same wrong lobe). Near-degenerate frames use
  continuity via an outlier-gated LobeTracker (ref updates only within
  30°; one corrupted detection can't poison the lobe; re-acquire after 5
  misses) seeded by plumbness against gravity measured from the tabletop:
  ONE robust depth-plane fit over annuli around the desk marker AND the
  object (inner exclusion 2.2×edge, outer 4×, ±5 cm median gate,
  iterative 15→8 mm refit), frozen after 10 frames. Continuity/gravity is
  NOT applied to well-separated lobes — the gravity seed flips the tilted
  desk card (its mirror lobe is MORE plumb). Result: wall rot p95 22.8° →
  2.4°, plumb 5.35°; 21/21 validation. ARUCO_MODEL.md §2.
- 2026-07-19 (real-scene Unity build = streamed measurements, nothing
  hardcoded): PSB1 → 'PSB3' (100 B) adds gravity up, origin-above-
  tabletop, object cube edge (82 mm = 2× marker height above the LOCAL
  tabletop point; marker centered on the cube face), and the sensor FOV
  from the color intrinsics (43.1° vertical). ArucoSceneReceiver builds
  wall slab / horizontal desk top / object cube / sensor body from those
  numbers under a gravity-aligned ArucoWorld, plus a second camera at the
  sensor pose rendering the calibrated-FOV POV as a 4:3 PiP inset (its
  view visually reproduces the recorded color framing). Desk legs + floor
  are the only decorative elements (recording never sees the floor).
- 2026-07-19 (Pipeline B world frame = desk marker id2, user-chosen): all
  poses — wall, object, and the camera itself (T_desk_cam = T_cam_desk⁻¹)
  — are expressed in the desk marker's own frame, making the
  reconstruction camera-placement invariant by construction; the wall
  marker becomes a built-in cross-check (must stay constant in the desk
  frame). Static markers are calibrated ONCE from the first 10 detections
  (user design: "send wall and desk frame once") and the object stream
  uses the frozen calibrated anchor, not the per-frame desk — this keeps
  the measured 0.8°/session desk orientation drift out of the world frame.
  World→Unity is the y/z axis swap (marker normal = Unity up); packets
  'PSB3' (scene, 100 B, written once, no seqlock; was PSB1 76 B before
  the real-scene build) + 'PSB2' (object, 44 B seqlock, live flag holds
  last pose like PSA5). ARUCO_MODEL.md.
- 2026-07-19 (rotation averaging = chordal matrix mean): static-marker
  rotations are averaged by element-wise-mean + SVD projection onto SO(3)
  (R = U·diag(1,1,det(UVᵀ))·Vᵀ) — stays in matrix representation per the
  no-quaternions policy, minimizes summed squared Frobenius distance, and
  recovers a known rotation to 0.09° from 200 samples of 2° noise
  (validated). The reference project's quaternion nlerp average was
  deliberately not reused.
- 2026-07-19 (ArUco pose = solvePnPGeneric IPPE_SQUARE,
  CORNER_REFINE_APRILTAG) [ambiguity part SUPERSEDED by the
  lobe-separation entry above — the in-quad depth-plane tiebreak
  described here turned out to pick the WRONG lobe]: full 6-DOF from the
  4 corners with the known size. Reference project's depth-deprojected-
  center translation was not reused (PnP translation is cross-checked
  against depth instead).

- 2026-07-17 (LEFT arm = sagittal mirror, not a re-derivation): left angles
  are DEFINED as the right-solver output on M=diag(-1,1,1)-reflected
  root-local vectors (rest arm -x̂) — every §6-7 property carries over by
  conjugation, mirror-symmetric poses give IDENTICAL numbers both sides,
  and anatomical signs stay side-independent (θτ+ = internal rotation on
  both arms). World reconstruction rule: flip y/z-angle signs, keep twist
  (M·Ry·M=Ry(-), M·Rz·M=Rz(-), M·Rx·M=Rx). Packet 'PSA3'->'PSA4' (72 B,
  root + both arms); receiver drives DEF-upper_arm/forearm .L and .R.
- 2026-07-17 (right elbow, user-requested 2-angle swing in the L14 frame):
  implemented generically as R_elbow = Ry(ey)·Rz(ez) in the fully-rotated
  upper-arm frame (R_root·Ry·Rz·Rx(θτ)), rest forearm = +x, same equations
  as the shoulder swing. DERIVED FINDING: ez ≡ 0 identically under our §6
  twist convention — the shoulder twist is measured from the forearm and
  already rotates the flexion plane into x–z, so the elbow's "up/down"
  swing IS the shoulder twist (4 observable DOF from 3 landmarks; injected
  ez=30 decodes as twist −30 with the identical forearm direction). ez kept
  in interface/packet for generality. Provisional hinge in send_arm_angles
  replaced by the formal solve; packet bumped 'PSA2'→'PSA3' (same 48 B,
  pad → elbow_ez) so stale readers can't misread the new layout.
- 2026-07-17 (Unity arm verification): rig arm driven via a NEW 48-byte
  'PSA2' packet (root Euler + shoulder θy/θz/θτ + elbow hinge) rather than
  extending the 32-byte root packet — the shoulder joint order Ry·Rz·Rx is
  not Unity's ZXY, so the receiver composes it with AngleAxis explicitly
  (quaternions as Unity-API intermediates only, per policy). Elbow is a
  PROVISIONAL scalar hinge (angle between segments, applied as Ry(−φ)
  innermost) purely so the rig silhouette matches the plots; the formal
  elbow convention is still an open derivation step. RootAngleReceiver
  disabled in the scene (would fight ArmAngleReceiver over the hip bone).
- 2026-07-14 (right shoulder swing-twist, derived from first principles):
  R_sh = Ry(θy)·Rz(θz)·Rx(θτ) with twist INNERMOST about the rest arm axis
  +x — only then does Rx(θτ)·x̂ = x̂ make the 12→14 vector pure swing and the
  twist a rotation about the arm's own long axis. L12 frame inherits the L24
  root basis (joint angles are relative to the parent segment; a re-derived
  basis would invent a shoulder-girdle DOF). Zero twist = forearm-forward;
  positive twist = internal rotation. NOT Unity's ZXY order — convert the
  matrix via §4 before driving a bone. See KINEMATIC_MODEL.md §6.
- 2026-07-14 (thesis-draft audit, errors to correct in the thesis text):
  (1) twist projection onto the ZX plane is WRONG — that plane CONTAINS the
  rotation axis x; the correct plane is y–z (⊥ to the axis) after un-swinging
  with R_swingᵀ, θτ = atan2(−f′y, f′z). Numeric refutation: at true twist 0
  the draft formula reads 47.9° (= atan(L_ua/L_fa), pure segment geometry)
  and it returns identical values for twist +90° and −90°. (2) The missing
  step was un-swinging before projecting. (3) 12→16 vs 14→16: under the
  CORRECT ⊥ projection they are exactly equivalent (the component ∥ arm axis
  is annihilated), so the draft's vector choice was defensible — its plane
  wasn't; 14→16 adopted for clarity. (4) The draft's generic swing solution
  θz = asin(vy/L), θy = atan2(−vz, vx) is CONFIRMED correct (= Ry·Rz with
  rest +x). Validated: known poses exact; shoulder_only / shoulder_torso
  synthetic datasets decode to ≤2e-13 deg vs injected truth (900 frames each).
- 2026-07-14 (twist observability): with a straight elbow the forearm is
  parallel to the arm axis and axial rotation is UNOBSERVABLE from landmarks
  12/14/16 — fundamental, not a bug; solver flags it (NaN + twist_ok=False)
  below |f′⊥| < 1e-6·|f| instead of returning atan2 noise.

- 2026-07-13 (handedness handling, non-obvious): no sign flip is applied when
  building rotation frames from Unity-space points — the numeric cross-product
  formula satisfies x̂×ŷ=ẑ for Unity's own left-handed basis, so a triad built
  r̂, f̂=r̂×s, û=f̂×r̂ and assembled as columns [r̂|û|f̂] is already a proper
  rotation (det +1, verified on all 899 frames). Sign correctness is pinned by
  the reference-pose test (upright facing sensor → exactly (0,180,0)), not by
  rule-of-thumb. The sensor→Unity reflection (x,-y,z) applies to POINTS only;
  rotations are constructed after it and never reflected. See KINEMATIC_MODEL.md §3.2.
- 2026-07-13 (L24 root frame): trusted primary axis is the hip line
  (r̂ = 23→24 = person's right); the spine-ish vector 24→12 only selects the
  plane; up is recovered as f̂×r̂. User's sketch corrected: its X (24→23) was
  the person's LEFT, its "Y" (lateral×spine) was actually the anterior-
  posterior axis, and its Z came out pointing down — decoded to (90,0,0),
  a rig flat on its back, at the reference pose.
- 2026-07-13 (Euler order): Unity applies Z, then X, then Y (R = Ry·Rx·Rz),
  per Quaternion.Euler docs and behavior — NOT YZX as initially guessed.
  Closed-form extraction (x=asin(-m12), y=atan2(m02,m22), z=atan2(m10,m11))
  with gimbal fallback at x=±90° derived in KINEMATIC_MODEL.md §4.
- 2026-07-13 (rig alignment): reference convention is Unity-humanoid rest =
  facing world +Z, right side +X, identity hip rotation; person facing the
  sensor therefore decodes to y=180° (physically real, sensor looks along +Z).
  Base-variant simplification R_hip = R_body accepted per task; constant
  calibration matrix C deferred to retarget time if the FBX rest pose differs.
- 2026-07-13 (calibration anchor, fixed after user saw rig facing backward):
  RootAngleReceiver's calibration must anchor to the CHARACTER's authored
  rest facing (referenceEuler = (0,0,0) for a +Z-authored rig), NOT to the
  person's reference pose (0,180,0) — the latter silently discards absolute
  yaw and leaves the rig back-to-camera. The sensor->Unity point mapping
  needed no change. See KINEMATIC_MODEL.md §3.4 pitfall note.
- 2026-07-13 (end-to-end verification method): correctness of the root-frame
  math was proven with a synthetic dataset of KNOWN injected rotations run
  through the full pipeline (CSV in sensor space -> decode -> shm -> Unity
  bone), not by eyeballing real data: decode matches truth to 1e-13 deg and
  the rig reproduces the motion on video next to the raw-landmark skeleton.

- 2026-07-12 (user request, brings part of variant 3 forward): Python->Unity
  live streaming bridge built now rather than in the real-time phase. Shared
  memory (/dev/shm + seqlock) chosen over UDP as default per user preference
  and because it is the exact transport the real-time variant needs; UDP kept
  as fallback. Packet layout is fixed 180-byte binary, documented in
  unity_bridge/README.md, duplicated in C# — must stay in sync manually.
- 2026-07-12: bridge displays a marker/bone skeleton beside the FBX character
  instead of driving the rig — retargeting requires joint angles from the
  kinematic solve stage; landmarks alone can't pose a Humanoid rig cleanly.

- 2026-07-12 (user request, scoped exception to base-variant no-smoothing
  policy): glitch filtering exists as a separate stage writing a separate
  *_filtered.csv — the raw CSV remains the untouched strict baseline, and
  which file feeds the kinematic solve stays an explicit downstream choice.
- 2026-07-12: filter uses Hampel (MAD-adaptive despike) + linear gap fill +
  selectable smoother; default switched from SavGol to zero-phase Butterworth
  3 Hz after user judged SavGol output still too shaky. Measured: butter 3 Hz
  shake 1.9 mm vs savgol 2.8 mm vs raw 10.2 mm, at equal fast-motion fidelity
  (4.8 mm); One-Euro rejected as offline default (28 mm lag during motion)
  but kept as --smooth oneeuro since the real-time variant needs a causal
  filter. Zero-phase methods valid only because this phase is offline batch.
- 2026-07-12 (user request re CPU/GPU/RAM management): profiled instead of
  adding speculative CUDA — 8.8 ms/frame median (113 fps ceiling): inference
  6.5 ms (GPU already), align 2.2 ms (CPU, librealsense), rest <0.2 ms.
  Real-time 33 ms budget already met with 4x headroom; further GPU offload
  would cost more in transfer than it saves. Revisit (CUDA librealsense,
  lite model) only if the budget tightens.
- 2026-07-12: MediaPipe delegate defaults to GPU on Linux with automatic CPU
  fallback — 4x throughput on the RTX 3080 (112 vs 27 fps, heavy model) with
  identical detection results (899/899 frames).
- 2026-07-12: Skeleton viewer reads the landmark CSV rather than the bag —
  visualization consumes stage output, keeping stages decoupled per the
  staged-pipeline design (and the same viewer will work for any later stage
  that emits the same CSV shape).
- 2026-07-12: MediaPipe extractor outputs float64-formatted values, not the
  reference project's float16 — float16 only holds ~3 significant digits at
  meter scale (~1 mm quantization at 1.7 m), too coarse to serve as the input
  to a ground-truth comparison.
- 2026-07-12: No smoothing in the extractor even though the ENSC498 reference
  applies a One-Euro filter at this stage — base variant is raw by policy;
  smoothing belongs to variant 2 and can later slot in between the CSV and
  the kinematic solve without changing either interface.
- 2026-07-12: Landmark CSV is wide-format (one row per frame, one column
  group per landmark) and emits a row for every frame even without pose/depth
  (empty cells) — keeps frame indexing aligned across pipeline stages and
  makes a later real-time variant's per-frame record shape identical.
- 2026-07-12: Deprojection uses rs2_deproject_pixel_to_point instead of the
  reference's manual pinhole formula — it respects the stream's distortion
  model at no extra complexity.

- 2026-07-12: Full project brief captured verbatim in BRIEF.md as the
  canonical scope reference, rather than only summarizing into STATE.md.
  Why: brief is large and policy-heavy (rotation representation rules,
  variant scoping, pipeline independence) — summarizing risked losing
  constraints that matter for thesis-level correctness later.
- 2026-07-12 (user policy, logged for traceability): rotation/translation
  matrices and Euler angles are the only representation for reported math,
  logs, and the Unity handoff. Quaternions or other representations are
  allowed only as an internal intermediate, and only with a DECISIONS.md
  entry at the point of use explaining why Euler/matrix alone was
  insufficient and where it converts back.
- 2026-07-12 (user policy): Pipeline A and Pipeline B must stay independent
  end-to-end, converging only at the evaluation/comparison step — do not
  merge them into one pipeline.
- 2026-07-12 (user policy): only variant 1 (base: offline, matrix/Euler,
  no smoothing) is in scope now. Variants 2 (enhanced/smoothing) and 3
  (real-time) are explicitly deferred, but base-pipeline interfaces
  (data structures, function signatures) should stay generic enough to
  extend later without a rewrite. No smoothing/filtering/real-time code,
  even as a stub, unless required for base-pipeline correctness itself.
- 2026-07-12 (user policy): processing model for this phase is fully
  offline/staged — each pipeline stage completes for the whole recording
  before the next stage starts, not a real-time per-frame loop.

- 2026-07-18: Blocked-landmark (occlusion) handling = detect + repair +
  chain fallback (KINEMATIC_MODEL.md §10). (a) Extractor gates landmarks
  on MediaPipe visibility < 0.5 (occluded landmarks are HALLUCINATED
  positions, not missing ones) and samples depth as the 5x5 nonzero-median
  instead of one pixel; a {name}_src reason column (0 ok / 1 low_vis /
  2 no_depth) is written per landmark. (b) Filter unchanged (gaps <= 5
  frames repaired offline; longer gaps stay NaN on purpose). (c) New
  kinematics/occlusion.py ChainFallbackSolver: per-joint hold-last-valid
  along the chain hips->root->shoulders->elbows->wrists — a blocked
  landmark costs exactly its own joints (wrist = twist+elbow only; hip =
  root only, arms keep solving against the held root; either shoulder can
  serve as the root tilt reference, measured deviation <=1.53 deg).
  Why: holding the ANGLE reconstructs the child by parent FK x bone
  length — always bone-length consistent and reachable, unlike guessing
  the 3D point; and the old whole-frame drop let one blocked wrist kill
  the root. Validated: 33/33 exact checks on masked copies of the
  verified 20260224 recording (validate_occlusion.py).
- 2026-07-18: Packet bumped PSA4 -> PSA5 (same 72 B; trailing 4-byte pad
  becomes u16 per-joint live mask + 2B pad, magic 0x35415350). Unity
  receiver shows red marker spheres on held bones. Streaming twist
  convention change: straight-elbow unobservable twist now HOLDS the last
  valid twist instead of θτ := 0 (unifies unobservability with occlusion;
  pure solvers in shoulder.py unchanged).

## 2026-07-28 — Writing v3 restructuring
- V3 structure directive (user): main body = kinematic model + system
  integration only; MediaPipe/ArUco/deprojection internals in Appendix A/B/C
  placed after References; Conclusion short and general (no result digits;
  all numbers verified present in Ch5/6/7); Ch6/7/8 stay as main body
  chapters; slim Ch2 keeps capture setup + communication preliminaries.
- Reference renumbering: single pass at merge time, ordered by first
  appearance in the final text. Old [15] collision resolved (ch1 paper keeps
  15, ch3 paper became 39); old [26] variants unified to full author list.
  Final list 1-54; old-to-new map recorded in writing/v3/references.md.
- Rule 11 (no internal file names in prose) conventions: recording IDs ->
  "Recording 1/2/3", bag file -> "recorded session", raw CSV -> "archived
  track/detections", /dev/shm -> "memory-backed file", synthetic dataset and
  shm channel names -> plain labels. Packet type codes (PSE1, PSA5, PSB2,
  PSB3, PSI1) are thesis-defined protocol identifiers and stay.
- Appendix A carries only pinned sensor facts; datasheet-level D435 specs
  were NOT added because no pinned source exists for them (no-invented-
  numbers rule). Needs a source if ever wanted.
- Rule-14 audit decisions (user-confirmed 2026-07-28): ch3 3.2.2 alternative
  root-frame construction TRIMMED to a generalized claim (no pinned source
  records the actual alternative axis order; defining it would invent
  content); ch3 3.4.4 rejected twist formula KEPT and completed with its
  missing definition clause; ch5 anchor-conjugation bug narrative KEPT as-is
  under rule 14's development-history clause (closes that open question).

- V4 review-round decisions (user-confirmed 2026-07-28): Objective 4 handled
  by BOTH softening Ch1 and adding Section 8.3.5 presenting Yiyang Dong's
  Bayesian-network recovery [16] as the robust missing-data path; the
  duplicated smoother table stays in Ch2 only (Table 6.3 removed, 6.4-6.6
  renumbered); Huang interview kept as attributed industry remark ([51-old]
  Leiserson carries the argument, now [16] global after Ch1 seeding).
  Verified corrections against reviewer's guesses: wall lever arm is 3.2 m
  (scene_calibration.json; pinned 2.8 m in D1/B1 is the 328 scene) so 8.1
  reads 39 mm not 34; 0.843 (46 in-motion frames) and 0.842 (carried frames)
  are both correct and now labeled; dropout counts 22/7/12/21 all reconcile
  (21 = held frames within the 898 displayed).

## V4 round 2 (2026-07-28)
- Patch v4 in place, no v5 tree (user). Numbered-equations conversion split
  into its own future round (user, per recommendation).
- Frame-100 mismatch: full regeneration from the v2 filtered CSV chosen over
  a one-clause explanation (user), because "every number reproduces" is the
  thesis's own standard. Ch3 worked example now traces to
  mediapipe/output/recording_20260224_083945_landmarks_filtered_v2.csv; the
  whole-recording claims (897-frame Unity log etc.) remain statements about
  the pinned instrumented runs.
- Spelling convention: Canadian (-our/-re endings, -ize verbs) per reviewer's
  SFU recommendation; reference titles verbatim.
- Objective 3: reviewer's narrower statement adopted after verifying every
  cited fact (511 deg, 89.9 deg pitch, grip vector in object frame).
- 2026-07-28 (worked-example round): numbered equations remain reserved for
  symbolic formulas; worked-example numerics are displayed but UNNUMBERED
  (MATH kind) so example arithmetic never shifts the citation-grade
  equation numbers. Worked-example values print at 4 decimals per the
  3.2.3 precision convention; C.4's rotation matrix upgraded from 3 to 4
  decimals so it digit-matches the new C.3 Rodrigues example.
- 2026-07-31 (Ch7 benchmark scope): the thesis reports only the two solver
  implementations the system actually carries (deployed per-frame solver;
  vectorized numpy batch tool). The wider study (numba/torch/CuPy/threads/
  GPU crossover) stays in realtime/REALTIME.md and the pinned bench CSV as
  the lab record but is out of the manuscript - report what the system
  runs, not everything that was measured. Batch column quotes the measured
  N=10,000 point rather than the part-extrapolated 100k scalar value.

2026-07-31 style sweep: (a) targeted (not strict) removal of what/how/why:
  only question-style framing, clefts, and "which is what/why" go; plain
  relative clauses stay (user choice via AskUserQuestion). (b) The four
  "honest/honestly" sites deliberately kept in the Data Integrity round
  are removed; this supersedes that earlier decision (user choice).
  (c) "measurement rather than inference" (Ch1/Appendix) kept: technical
  distinction, not a credibility claim. (d) Artifact-sense "pinned" and
  synthetic-vs-real "real data" kept for the same reason.

2026-08-03 (supervisor round, Part 1):
- Citation stability over free rewriting: the Ch1 condensation keeps every
  ref cited in its original first-appearance order (Table 1.1 cites only
  already-mentioned work), and Ch2 keeps a one-sentence One Euro mention,
  so the consolidated [1]-[52] numbering never shifts. Any future cut that
  removes a citation's first appearance must re-check this.
- Filter comparison (old Table 2.3) removed per supervisor ("not within
  the scope"); the 10.2->1.9 mm shake numbers survive in Ch6 prose, the
  28.4 mm One Euro lag number is dropped entirely.
- Two-decimal convention for worked examples: computed at full precision,
  printed to two decimals; decode steps use symbolic m_ij arguments so
  printed asin/atan2 lines stay consistent.
- 3.4/3.5 split: 3.4 ends at solved joint angles; every Unity-specific
  artifact (Euler transmission, Eq 3.18, C_rest, q_A, rig stills, rig
  instrumentation) lives in 3.5. Ch5 keeps the integrated-scene mapping;
  3.5 covers the standalone rig.
- Lit-map visualization skipped (user chose summary table only); setup
  figure sourced from recording frame 100 (user decision).

- 2026-08-03 (supervisor round 2, Part 2 trim): user decisions recorded:
  Ch7 solver benchmark keeps BOTH Table 7.2 and Figure 7.2 (only threading
  prose cut); Ch6 placement experiment kept with Table 6.2 (prose trimmed).
  Shared memory diagram (supervisor request) added as Figure 5.2, drawn as
  a memory block from the real PSI1 108-byte layout of the integration
  sender; the thesis text now states the transport choice explicitly (both
  transports implemented, shared memory default over UDP, UDP kept as
  drop-in) per DECISIONS 2026-07-12 — no invented "UDP first" history.
  Ch8 lever-arm discrepancy resolved in favour of the pinned source
  (D1_limitations.md + check_limits.py: 0.69 deg over 2.8 m lever arm
  = 34 mm; residual below 9 mm), replacing the derived 3.2 m / 39 mm /
  7 mm text that conflicted with Table 8.1 on the same page.

- 2026-08-06 (v2 kickoff): output style rule (user): professional plain
  text only in ALL artifacts (code, comments, names, logs, commit
  messages, reports, docs). No emojis, icons, or decorative Unicode.
  Markers: PASS / FAIL, OK / ERROR / WARNING, [x] / [ ]. ASCII
  punctuation only (->, =>, ===, ---); "deg" not the degree sign in
  program output.
- 2026-08-06: v1 frozen at git tag v1-thesis (all pre-existing folders);
  v1 code is never edited again. v2 lives in a new top-level v2/ folder
  importing the proven v1 modules in place via the same sys.path pattern
  v1 uses; only sanctioned edits outside v2/ are .gitignore, one added
  Unity C# receiver, and .agent records. User chose tag-plus-new-folder
  over copying code into v1/-v2/ trees.
- 2026-08-06 (v2 M1): capture broker process over a threaded single
  process for single-camera frame sharing: preserves the measured
  process-level A/B parallelism (DECISIONS 2026-07-24), keeps MediaPipe
  GPU work in Pipeline A only, and fits the existing seqlock idiom. The
  PSF1 frame ring (v2/common/shm_ring.py, 8 slots, copy-then-verify
  readers) is transport infrastructure below the A/B independence
  boundary -- it replaces the bag file both pipelines already shared.
  Alignment depth->color moves into the broker, paid once. Live profile
  is pinned to the bag's exact profile (640x480 bgr8 + z16 @ 30) with a
  loud assert on the negotiated modes (USB2 downgrade trap).
- 2026-08-06 (v2 M3): the delay buffer lives in the merger
  (v2/integration/v2_integrate.py), one mechanism for thesis 8.3.1
  (timestamp pairing on the shared session clock) and 8.3.3 (render at
  now minus a fixed declared delay, interpolate between bracketing
  measured packets, flag them). Person interpolation is componentwise
  wrap-aware on the 13 joint parameters (root y lives at the +-180
  seam); object is position lerp + SO(3) geodesic; prediction rejected
  per thesis. Default --delay-frames 2 (66.7 ms), measured not assumed:
  at 1 frame ~7 percent of ticks miss their future bracket, at 2 none
  do. Long gaps hold-last exactly as v1; reacquisition blends over 2
  ticks, flagged. Held object ticks judge liveness by the newest packet
  AT OR BEFORE render time (a future reacquisition packet must not
  claim live early). Packet PSI2 (112 B, /dev/shm/integrated_scene_v2)
  extends PSI1 with u16 flags (interp/blend/bridge per stream); the v1
  receiver stays dormant by shm-name separation. Broker detects
  end-of-source promptly (1 s timeout + playback status) so the 5 s
  wait_for_frames tail that depressed v1's sustained-fps figure is gone
  (29.0 fps sustained on the bag).
- 2026-08-06 (v2 M4/M5): live scene calibration collects observations
  from the frame ring in the extractor's exact CSV contract and
  subprocesses the UNCHANGED aruco/calibrate_scene.py (zero logic
  duplication; JSON schema identical by construction). Gravity seed
  phase runs BEFORE any pose solving so every written row has the seed
  for wall-lobe decisions. Bag dress rehearsal reproduces the frozen
  calibration to 0.98 mm / 0.32 deg; the pinned recording needs
  --cube-size 0.07 (cube never rests on the desk during the seed
  frames), same escape hatch v1 documented. Unity: one ADDED file
  Unity/Assets/Scripts/IntegratedSceneReceiverV2.cs (Unity cannot load
  code outside Assets/, the single sanctioned exception to "all v2 code
  in v2/"); inherits ArucoSceneReceiver, person block duplicated from
  the frozen v1 receiver, PSI2 layout hand-duplicated ("change both or
  neither"). Vocabulary: red = held (v1 meaning unchanged), amber =
  bridge/blend only; routine resampling is recorded in the flags field
  but not painted.
- 2026-08-25 (evaluation rebase, professor-directed): the evaluation
  framework changes from cross-pipeline agreement to a two-stage
  ground-truth chain. Stage 1: a physically surveyed labeled path on
  the testbed (steel ruler relative to the desk ArUco origin, survey to
  be provided) grades the ABSOLUTE accuracy of the ArUco box-center
  track. Stage 2: the kinematic wrist is graded by offset constancy
  (magnitude of the wrist-to-box-center vector on held frames; full
  object-frame vector as supporting evidence), with an explicit error
  budget propagating stage-1 error + survey uncertainty. The newest
  50 s bag recording_20260825_070152 becomes the PRIMARY evaluation
  recording (R4, 1499 frames, 640x480@30, person enters -> walks to
  desk -> moves cube along the labeled path -> steps back); the entire
  thesis rebases onto it additively (no pinned R1/R2/R3 artifact is
  deleted or modified; R1 retire-vs-keep decided after results).
  Recording 2 and Recording 3 keep their roles. New analysis code lives
  in a new top-level eval/ track (own README + DECISIONS, v3-style;
  v1 imported or vendored, never edited). Backup take
  recording_20260825_070032 (same session, also healthy) copied to
  Video/ alongside R4. Plan: /home/luo/.claude/plans/ok-i-need-you-
  misty-island.md, approved by the user 2026-08-25.
- 2026-08-25 (mechanical, follows the v1/ move exception): 16 dead
  absolute paths in six LIVE scripts under writing/v6/scripts/ fixed by
  prefixing v1/ (commit 9404fe1). Verified by rerunning ch3_numbers.py
  and ch45_numbers.py and matching the pinned frame-100 values in
  writing/v6/thesis.md. These are live figure/number scripts, not
  frozen v1 code; no frozen file changed.
- 2026-08-25 (user direction): v1 is UNFROZEN. It is developed again
  for more robust occlusion handling and better results. Guard rails:
  pinned R1 artifacts and all existing validators keep passing; new
  capability goes in new modules or behind opt-in flags with new
  validators; baseline solve behavior stays bit-reproducible (the
  eval/ R1 regression checks enforce this).
- 2026-08-25 (E-009 cause revised on user evidence): the marker
  prints are the SAME physical size as R1's. The 0.87 scale factor is
  nonetheless empirically correct (three independent physical checks:
  drawn-path 45 cm span vs tracked 44.7 cm corrected / 51.0
  uncorrected; cube-center desk-slide height 3.7 cm corrected vs 3.5
  cm physical; constancy drift collapse). Reinterpretation: the
  factor is exactly 7/8 - the new prints render the nominal 50 mm
  INCLUDING a white quiet-zone module, so the detected black square
  is 50 * 7/8 = 43.75 mm. Ruler check: black-square side ~43.7 mm on
  the desk marker card. Correction stands; frames.py sizes describe
  the black square, not the card.
- 2026-08-25 (v1 development, first change since unfreezing): robust
  occlusion layer wired into the v2 live pipeline behind an opt-in
  --robust-occlusion flag (run_v2.py passthrough -> v2_person.py).
  The kinematic model itself is UNCHANGED (root_frame.py, shoulder.py,
  occlusion.py untouched); occlusion_ext.py only filters which wrist
  measurements are trusted and supplies constrained estimates, and
  with the flag off behavior is bit-identical (validated). R4 live
  A/B: zero cost, 148 honesty demotions (all right-side depth
  collapse), depth-collapse-window angle error p95 121.7 -> 14.6 deg
  vs the trusted offline reference. Report:
  eval/reports/r4_stage6b_robust_live.md.
- 2026-08-25 (user direction, generalization): the robust layer must
  not be wrist-specific - the chain design makes the same principle
  (fixed segment length -> gate; neighbor + direction memory ->
  recovery) apply at every link. occlusion_ext.py rewritten as the
  universal skeleton-constraint layer: hip pair (root keeps solving
  from a recovered hip), shoulder pair (root tilt reference and arm
  anchor recoverable), elbows, wrists, with proximal-to-distal
  chaining, torso-diagonal attribution for pair violations (never
  guess when attribution is ambiguous), and honesty tags throughout.
  Kinematic model still unchanged. validate_occlusion_ext.py: 21
  checks ALL PASS; recovery beats hold at every chain level on the
  pinned R1 scenarios. Preconditions now traced in ASSUMPTIONS.md
  (user-requested; thesis preconditions section draws from it).

## 2026-08-26 — v2 R5 real-time probe (feature preservation round)

User direction: proof of concept that the rig model runs in real time
in a lightweight way, preserving as much of the frozen R5 evaluation
round's feature set as possible; recording first, with the existing
broker source switch keeping the sensor path identical downstream of
the frame ring. More permission than the v1 freeze (not bound to the
exact v1 transform chain), MediaPipe + ArUco pipeline kept.

Decisions (details + measurements in v2/reports/r5_realtime_probe.md):
- All probe behavior opt-in flags; flags-off stays the pinned validated
  stack (regression: validate_v2.py 22 checks ALL PASS after the port).
  --probe-r5 preset enables the set.
- PSR2 = PSR1 with the 7 solver tags packed in the former pad bytes
  (same 84 B, new magic); merger accepts both, routes tags through the
  delay buffer (elementwise max on brackets, floored HELD on holds)
  into the PSI2 pad. Unity: blue held-sphere = CONSTRAINED (recovered).
- B->A object link: Pipeline A reads PSB2 latest-wins and reconstructs
  the camera-frame pose exactly (involution unity/world maps +
  T_cam_desk); skew guard 3 frames (measured skew p99: 0).
- Grip offset mu fitted ONLINE in solver space (rigid offset is
  frame-invariant; leveled-world detour dropped). Carried = displaced
  from the initial-rest median (first 30 live samples), gating ENTER
  only. EXIT cannot retro-clear like offline: a true release stays
  box-anchored up to 5 frames (the one causality cost).
- E-019 gate ported into Pipeline B ahead of its causal filter;
  E-018 smoother into the merger (packet only, dumps raw).
- Calibration trap fixed at the source: make_r5_calib.py writes the
  true 45 mm marker sizes into the v2 R5 calibration so live PnP is
  consistent with the scale-corrected transforms (E-009).
- validate_v2_r5.py (13 checks, PoC-weight): ALL PASS. 29.6 fps
  sustained, person p99 25.1 ms, recovery cost ~0.06 ms/frame, causal
  lag 3 frames, worst group median 0.47 deg vs the offline recovery
  reference on clean frames; recovery fires inside the offline failure
  windows; episodes match the two-handover structure.

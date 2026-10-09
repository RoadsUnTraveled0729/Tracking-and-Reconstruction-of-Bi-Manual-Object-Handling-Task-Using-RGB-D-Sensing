# Object-conditioned pose recovery on R5 (E-014)

Recording: recording_20260825_222315 (R5, 2099 frames, 69.98 s,
30 fps). Purpose: during the frames where MediaPipe fails to track
the body - the skeleton is off the person while the cube's ArUco
marker remains measured - determine the arm pose from the object's
pose. This report gives the failure study, the full mathematics of
the technique, its evaluation, and the real-time deployability
analysis. Implementation: v1/kinematics/occlusion_ext.py (solver
layer, additive) + eval/failure/ (detection, grip state,
orchestration).

## 1. Failure study: where and why MediaPipe fails on R5

Method: the overlay study video (eval/inspect/check_v1_overlay.py)
projects the measured landmarks and the solved skeleton onto every
color frame; five per-frame detectors (eval/failure/
detect_failures.py) turn "the skeleton is off the body" into an
objective mask. Full detector report: r5_failure_mask.md; events:
r5_failure_events.csv.

Detectors (per frame, per arm or torso; thresholds derived from the
clean reference recording R1 and pinned in r5_failure_mask.md):

    D1  acquisition failure: a landmark's source flag is not "ok"
        (low visibility or no depth sample)
    D2  segment-length implausibility: an apparent upper-arm or
        forearm length deviates > 35 percent from its clean median
        (a rigid segment cannot change length; catches depth
        corruption at full visibility)
    D3  torso line-inconsistency: hip line vs shoulder line 3D angle
        > 22 deg (the torso is rigid; the two lines stay
        near-parallel on all clean data)
    D4  torso width ratio: shoulder-width / hip-width outside a
        20 percent band of its clean median
    D5  velocity spike: a landmark moves > 5 cm in one frame
        (1.5 m/s) between two consecutive measured samples
    D6  grip plausibility (object-aware, applied where grip episodes
        are known, eval/failure/recovery_core.py): while a hand
        holds the object, a measured wrist farther than 0.35 m from
        the box center is a wrong measurement - a held object and
        its holding wrist cannot separate. On R5 it flags 15 frames,
        all inside windows D1-D5 already found; its value is as a
        recording-independent guard

Findings (person-present span, 2037 frames):

    fail_arm_L  350 frames (17.2 pct), largest window 1427-1668 (8.1 s)
    fail_arm_R  183 frames ( 9.0 pct), largest window 1775-1893 (4.0 s)
    fail_torso  625 frames (30.7 pct), largest window 1182-1544 (12.1 s)

Two failure classes emerged:

1. Honest failures (D1): MediaPipe reports low visibility - the hand
   wraps behind the carried cube. The two known windows (left
   1458-1668, right elbow 1826-1893) are of this class.
2. Confident-but-wrong failures (D2-D5 firing while D1 is silent;
   571 torso frames, 98 arm_L, 66 arm_R): the landmark visibility
   stays ~0.98 while the 3D position is wrong because the depth
   sample lands on the wrong surface. The largest is the 12.1 s
   torso window 1182-1544 (one hip's depth splits 31.3 cm from the
   other; clean split 1.3 cm). Both blocked-arm windows are PRECEDED
   by confident-but-wrong stretches (left: forearm 34.7 cm apparent
   length at 1427-1457; right: elbow collapsed onto the wrist,
   upper arm 47.2 cm apparent, at 1775-1825) - the tracker degrades
   geometrically before it admits failure.

In every one of these windows the object marker remains measured
(object coverage 98.05 pct; its longest gap, 0.67 s at 1085-1104,
lies in the two-hand handover). The object is therefore an anchor
that survives exactly the failures that defeat the person tracker.

## 2. Notation and frames

    p_k         3D position of landmark k in the solver frame
                (camera frame with the y axis flipped up,
                "unity_from_sensor"); meters
    o, R_obj    object marker origin and orientation, leveled desk
                world (LeveledWorld: gravity = +y)
    S, E, W     shoulder, elbow, wrist of one arm
    L1, L2      calibrated upper-arm and forearm lengths (medians of
                clean measured frames; R5: right 0.256/0.252 m,
                left 0.262/0.247 m)
    mu          grip offset of one hand, expressed in the OBJECT
                frame; constant while the grasp is rigid
    R_root      torso frame (columns [right | up | forward]) from
                hips + shoulders
    u_seg       EMA direction memory of a segment (alpha = 0.3,
                updated only from fully measured frames)

The leveled world and the solver frame are related by a fixed rigid
map (calibration): x_world = G (M (D x_solver) + c) with M, G, c
from the scene calibration; all lengths and angles are invariant
under it. The implementation computes the wrist estimate in the
leveled world and maps it into the solver frame before the solve
(eval/failure/recovery_core.py).

## 3. The recovery mathematics

### 3.1 Grip-offset model (the object-to-wrist link)

While a hand grips the cube rigidly, the wrist is a fixed point in
the object's frame:

    W(t) = o(t) + R_obj(t) mu                                   (1)

mu is fitted by least squares over the clean held frames of a grip
EPISODE: with d(t) = R_obj(t)^T (W_meas(t) - o(t)),

    mu = mean_{t in episode, clean} d(t)                        (2)

The mean is exactly the least-squares minimizer of
sum |W_meas - o - R_obj mu|^2 because R_obj is orthogonal.

The offset is NOT a per-recording constant: the operator regrasps
between stations (episode means differ by up to 18 cm,
grip_episodes.json) and shifts the hand DURING long episodes
(measured drift up to 13 cm between an episode's mean and the offset
in force at a given moment). mu is therefore estimated TIME-LOCALLY:
within each grip episode, clean held frames update an exponential
moving average of d(t) (gain 0.02 per frame, about 1.7 s of memory);
frames without a clean update - exactly the failure windows - FREEZE
the estimate, so the value used for recovery is the offset in force
immediately before tracking was lost. The average restarts at each
episode boundary (a new grasp is a new offset) after a 5-frame
warm-up; before warm-up the episode mean, then the recording-wide
fit, stand in. This is the same causal estimate an online system
would maintain.

Frames masked as failures are excluded from every fit (no feedback
from corrupt data into the prior).

### 3.2 Holding-hand determination (which arm the object informs)

Equation (1) applies only to a hand that is actually holding.
The instantaneous classifier (hold = marker measured AND carried AND
wrist measured AND |W - box_center| < 0.25 m AND forearm plausible)
needs a measured wrist - unavailable exactly when recovery is
needed. A causal state machine (eval/failure/grip_state.py) supplies
persistence:

    ENTER  clean instantaneous holding for 5 consecutive frames
    STAY   through wrist failure while the object remains carried
           (rigid-grasp persistence: a moving object nobody visibly
           released is still in the hand that held it)
    EXIT   object at rest, or wrist cleanly measured farther than
           0.35 m from the box center, 5 consecutive frames
           (release hysteresis: 0.35 > 0.25)

Both hands may hold simultaneously; R5's handover (frames
~1014-1110) is two overlapping episodes. The NON-holding arm gains
nothing from the object; during its failures the layer keeps its
existing behavior (hold last pose / EMA recovery, honestly tagged).

### 3.3 Wrist from object

On a failure frame of a holding hand:

    W_hat = o + R_obj mu_local                                  (3)

W_hat is a live function of the same-frame measured object pose;
only mu is a prior. Accuracy is bounded by the short-memory grip
variance plus the object-pose error. Two physical plausibility
bounds guard the estimate itself, independent of any recording:
a mu whose magnitude exceeds 0.30 m is discarded (no wrist sits
that far from the center of a hand-held 7 cm cube), and a MEASURED
wrist beyond 0.35 m of the held box center is flagged as a wrong
measurement (detector D6) rather than believed.

### 3.4 Shoulder and torso

The arm solve needs the shoulder S and the torso frame R_root.

- Torso tracked: S is the measured shoulder (or, if only the
  shoulder landmark failed, the rigid-pair recovery rebuilds it from
  the other shoulder along the shoulder-line memory).
- Torso failed (D3/D4 windows): the corrupt joints are repaired on
  their camera RAYS (E-011b): a wrong depth sample moves a landmark
  along its ray while the pixel stays true, so a gated hip or
  shoulder is placed back on its ray at its remembered depth (EMA
  from measured frames); a gated pair takes its position from the
  ray midpoint and its orientation through the line's EMA (raw ray
  directions carry the pixel wobble of hands crossing the torso).
  Corruption that keeps both torso lines agreeing - invisible to
  the line-consistency gate - is caught by a 10 cm depth-jump gate:
  a landmark whose depth leaves its memory by more than 10 cm in
  effect teleported, which no real torso does (clean deviations:
  2.5 cm max on R1, p99 ~5 cm on R5). If nothing survives, the root
  holds. S then comes from the repaired/held torso. Measured on R5:
  the worst torso window's root yaw swing fell from 49 to 15 deg
  and the pelvis depth wander from 22 cm to 0.5 cm; on synthetic
  pixel-preserving depth corruption the repaired hip lands within
  0.2 cm of truth.

The object cannot substitute for the torso. Formally: (1) ties the
object to one point W; the torso pose has 6 DOF; the only constraint
W imposes on the shoulder is the reach inequality

    | |W_hat - S| | <= L1 + L2                                  (4)

one scalar inequality against six unknowns - it can reject a torso
hypothesis, never determine one. This is stated as a limitation, not
patched around.

### 3.5 Two-link inverse kinematics for the elbow

Given S, W_hat, and the calibrated lengths L1, L2, the elbow lies on
the intersection of two spheres:

    |E - S| = L1,    |E - W_hat| = L2                           (5)

Let d = W_hat - S, r = |d|, d_hat = d / r. The law of cosines gives
the angle alpha at the shoulder between d and the upper arm:

    cos(alpha) = (L1^2 + r^2 - L2^2) / (2 L1 r)                 (6)

The intersection is the circle

    center  c = S + L1 cos(alpha) d_hat
    radius  rho = L1 sin(alpha)                                 (7)
    E(phi) = c + rho (cos(phi) u + sin(phi) v)                  (8)

with {u, v, d_hat} any right-handed orthonormal basis. The free
parameter phi is the elbow swivel - the one DOF the wrist position
cannot observe. It is chosen by CONTINUITY: project the remembered
upper-arm direction u_mem (the EMA of the last measured
shoulder-to-elbow direction) onto the circle,

    n_perp = u_mem - (u_mem . d_hat) d_hat
    E = c + rho n_perp / |n_perp|                               (9)

which is the closed-form minimizer of |E - (S + L1 u_mem)| on the
circle - the elbow moves as little as possible from where it was
last seen. With no usable memory (|n_perp| ~ 0 or cold start) a
gravity-down anatomical prior replaces u_mem (elbows hang).

Degenerate cases, all handled by clipping cos(alpha) to [-1, 1]:

    r > L1 + L2   (object out of reach of the calibrated arm):
                  cos(alpha) -> 1, rho -> 0, E -> c on the S-W axis;
                  the arm straightens toward the object - the
                  bounded-error direction is preserved and the
                  output stays finite
    r < |L1 - L2| (over-folded): symmetric clip
    r ~ 0         (wrist at the shoulder): no direction; the two-link
                  solve returns nothing and the elbow is then placed
                  from the direction memory (tag CONSTRAINED); the
                  group holds only when no fresh memory exists
                  (corrected 2026-08-28 to match occlusion_ext.py)

Conditioning near full extension: differentiating (6),
d(alpha)/dr diverges as r -> L1 + L2, so near a straight arm a
centimeter of wrist-estimate error becomes tens of degrees of
flexion error (measured: a 2 cm outward bias at 97 percent of reach
snapped a 21.6 deg flexion straight). Above 98 percent of full
reach the elbow therefore comes from the direction memory (if
fresh) instead of the cosine law, with the wrist still anchored at
W_hat; the IK remains the fallback. Validator check: a biased
near-extension estimate now keeps flexion within 0.9 deg of truth.

### 3.6 Joint angles and observability

The reconstructed triple (S, E, W_hat) feeds the UNCHANGED v1
swing-twist solve (v1/kinematics/shoulder.py): shoulder swing from
the unit upper-arm vector in the root basis
(theta_z = asin(a_y), theta_y = atan2(-a_z, a_x)), twist from the
forearm's perpendicular component, elbow flexion from the forearm in
the fully-rotated arm frame. Two observability rules carry over from
E-012 verbatim, because they are properties of the parameterization,
not of the data source:

- twist is HELD below 15 deg of elbow flexion (1/sin amplification
  near the straight arm), released at 25 deg (hysteresis);
- every arm parameter passes the wrap-aware 15 deg/frame slew
  limit; while the limiter clamps, the group is demoted.

Honesty semantics: any group whose supporting landmarks were
recovered - object wrist, IK elbow, rebuilt torso - has its live
bit CLEARED and its tag set CONSTRAINED. A recovered pose is never
reported as a measurement.

### 3.7 Measured quantities vs priors

    measured, same frame:   o, R_obj (ArUco + depth), all surviving
                            landmarks
    calibrated constants:   L1, L2 (clean-frame medians), scene
                            calibration (fixed rigid map), grip
                            offsets mu (per episode, clean frames)
    causal state:           grip episode state, EMA direction
                            memories, previous output angles
    priors invoked only in degeneracy: gravity-down elbow direction
                            (cold start), held torso (torso failure)

No quantity depends on future frames; nothing is fitted on the
frames being recovered.

## 4. Evaluation

Protocol (per the standing evaluation rule, ASSUMPTIONS.md A6 /
E-013): accuracy numbers come from SYNTHETIC masking of genuinely
tracked grip frames - the masked landmarks' true positions are
known, so the error of every method is measurable. The real failure
windows have no truth and are evaluated qualitatively.

### 4.1 Synthetic-mask results

Two harnesses: eval/failure/harness_recovery.py (45-frame windows in
every clean tracked holding stretch; scenarios S1 masked elbow+wrist,
S2 + shoulder, S3 + both hips) and eval/failure/
moving_window_check.py (the one tracked MOVING holding stretch).
Methods on identical masked inputs: hold-last, EMA recovery (the
pre-E-014 layer), object recovery. Full tables:
r5_recovery_synthetic.md, r5_recovery_moving.md.

What the numbers say, honestly:

1. The wrist anchor is accurate wherever the grasp is rigid. With
   the time-local mu, the object-derived wrist lands within 1.2 cm
   (median) of the true wrist on the desk-slide windows and 4.5 cm
   on the station window - against a 25 cm hold radius. The two
   windows that sit AT the wire handover degrade to 6.9-14.0 cm:
   there the grasp itself changes during the outage, the technique's
   stated worst case (section 6).

2. On a MOVING outage the recovery gives the best wrist position of
   all methods. Right desk slide, 50 deg of true arm motion in one
   second, arm masked: FK wrist error median 1.6 cm / max 3.0 cm
   for the recovery, against hold-last max 21 cm (and growing with
   window length - the outage-duration sweep shows hold's angle
   error rising monotonically). The EMA method is competitive only
   while its memory is fresh; its 45-frame horizon means every
   window longer than 1.5 s decays toward hold, while the object
   anchor does not age.

3. On SHORT, near-stationary outages hold-last is competitive by
   construction - an arm that does not move is held perfectly. The
   harness's station windows (angle medians: hold 0.6-2.8 deg,
   recovery 1.2-3.4 deg on the rigid-grasp windows) show exactly
   that; they measure the benign case, not the failure mode the
   technique exists for.

4. In angle space the recovered twist is conditioned by the elbow
   swivel prior and can read worse than the smoothed memory methods
   (up to ~9-12 deg median on the handover windows). The recovered
   groups are tagged CONSTRAINED for precisely this reason: the
   output is a constrained estimate, not a measurement.

5. Torso-failed scenario (S3): the root holds, its live bit clears
   on every masked frame, and the arm chain keeps solving on the
   pair-recovered shoulder. Honesty violations across all 12
   window-scenario runs and all methods: zero.

The real failure windows are 4-8 s of continuous motion - the
regime of point 2 extended far beyond any memory horizon, where
hold-last is off by tens of centimeters (visible in the overlay);
no synthetic window can grade them because no tracked truth exists
there (E-013), which is why the qualitative evidence below matters.

### 4.2 Qualitative results on the real failure windows

Overlay video: eval/output/recovery_r5_overlay/v1_overlay_recovery
.mp4 (red banner = detected failure, yellow cross = object-derived
wrist estimate, red/blue = solved arms).

- Left-arm window 1427-1668 (8.1 s, cube carried up the right post
  and onto the wire in the left hand): before, the solved left arm
  dangles at the last measured pose while the real arm holds the
  cube aloft; with recovery the left arm tracks the cube through
  the whole window (278 wrist substitutions, 264 IK elbows), tagged
  CONSTRAINED throughout.
- Right-arm window 1775-1893 (4.0 s, wire traverse): same behavior
  (119 wrist substitutions and IK elbows).
- Torso windows 896-931 / 956-1130 / 1182-1544: handled by the
  E-011b ray repairs and the depth-jump gate (root yaw ranges 2.5 /
  15.3 / 13.2 deg; the object correctly contributes nothing;
  section 3.4).
- The object track feeding all of the above is the E-019 cleaned
  track: the handover's 41 undetected rows held at the previous pose (E-022; no detected row is blanked)
  are filtered out once, so the recovery never anchors on them and
  the rendered box holds honestly through the covered stretch.

## 5. Real-time deployability

The technique is causally deployable as designed; nothing in it is
offline-only.

- Causality. Every input at frame t is available at frame t: the
  object pose is measured in the same frame (Pipeline B), the
  failure detectors compare current-frame statistics against
  precomputed thresholds, the grip state machine and the EMA
  memories are strictly past-only, and the IK is a per-frame closed
  form. The offline implementation contains no lookahead
  (validate_occlusion_ext.py exercises the solver frame by frame).
- Calibration phase. The priors need a bounded warm-up: segment
  lengths self-calibrate in the layer's existing 60-frame window;
  a grip offset needs ~15 clean held frames per grasp (0.5 s) -
  in a live system mu is simply fitted online during the first
  clean half-second of each grasp, which is exactly what the
  per-episode fit already does causally.
- Cost. The additions per frame: <= 2 detector evaluations per arm
  (a handful of norms), one 3x3 transform chain for W_hat, and the
  closed-form IK (~50 flops: one acos, one atan2, two cross
  products). The existing robust solve costs 0.34 ms p99 (E-012);
  the additions are microseconds. The 33.3 ms frame budget is
  untouched.
- What a live deployment would need (identified only; v2 is out of
  scope by direction): the object pose and the landmarks must meet
  in one process before the solve (the live pipeline already merges
  the two streams; the solver call gains the obj argument); the
  grip-offset fit becomes an online accumulator per episode; a
  double failure (marker lost while the arm is failed) falls back
  to the existing hold with honest tags - no new failure mode.
- Display smoothing (user review 2026-08-26: the bounded solver
  transitions - 15 deg/frame slew catch-ups, root re-locks up to
  26 deg/frame - read as jumps on the rig): the Unity sender passes
  the angle stream through a causal first-order low-pass plus an
  8 deg/frame output rate cap (eval/unity_check/send_scene_r5.py,
  AngleLPF). The cap, not the low-pass, is what bounds the visible
  speed: the transitions are ramps, and any unity-gain linear
  filter follows a ramp at its own slope (measured on the R5 track:
  a single pole passed 14.7 of 15 deg/frame, a second-order
  Butterworth 16 deg/frame with up to 52 deg of overshoot). With
  the smoother, zero display steps exceed 10 deg/frame and the
  tracking error against the solver output is 2.1 deg p95. Display
  only - every analysis number in this report is unfiltered.

## 6. Generalization to other recordings

Nothing in the technique is fitted to this video:

- Per-recording by DESIGN, refitted causally on any new take: the
  segment lengths (60-frame self-calibration), the grip offsets
  (time-local fit, ~0.5 s per grasp), the scene calibration. These
  are properties of the subject and the scene, not tuning.
- Physical, recording-independent: the plausibility bounds (hold
  radius 0.25 m, release 0.35 m, grip-offset cap 0.30 m, D6), the
  segment-length tolerance (a rigid limb cannot change length), the
  torso line-consistency angle, the slew limit (450 deg/s exceeds
  any desk-manipulation motion), the IK conditioning threshold (a
  property of the cosine law).
- Cross-checked on a different recording: every detector threshold
  is required to fire zero times on the clean reference recording
  R1 before it is accepted (r5_failure_mask.md), so the thresholds
  are not carved around R5's quirks.
- Rerunning the whole chain on a new bag is the pinned command
  sequence in eval/ (extract, precondition check, calibrate, fit,
  detect, recover); only the stem changes.

## 7. Limitations

- The technique recovers the HOLDING arm. The free arm's failures
  keep the hold/EMA behavior.
- The torso is not recoverable from one rigid grasp (section 3.4,
  eq. 4); torso failures rely on the E-011 line gate and holds.
- Accuracy is floored by the within-episode grip variance (the hand
  shifts on the cube) and the elbow swivel prior; the recovered arm
  is honest about this (CONSTRAINED, never MEASURED).
- A regrasp DURING a failure window (no clean frames to update mu)
  keeps the frozen estimate; the error grows with the regrasp
  displacement until tracking returns. Measured: the synthetic
  windows placed at the wire handover show 6.9-14.0 cm of wrist-
  estimate error, against 1.2-4.5 cm on rigid-grasp windows.
- Near full arm extension the flexion-from-distance relation is
  ill-conditioned; the guard (section 3.5) substitutes the direction
  memory there, so a long near-extended outage inherits the memory's
  staleness instead.
- Marker loss during a failure window leaves nothing to anchor on;
  the layer holds (R5: the only marker gap, 0.67 s, lies inside the
  two-hand handover where both wrists were still measured).
- A wrong wrist that drifts away SMOOTHLY (below the velocity gate)
  while reading as clean can mimic a release: in a live causal
  system the grip state machine would then end the episode and
  recovery would stop - the failure degrades to the honest hold, it
  does not corrupt the output. Offline, the retroactive episode
  cleanup plus D6 close this gap.

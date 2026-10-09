# eval/ track decisions

Format follows AGENTS.md (ID, Status, Decision, Why, Alternatives,
Evidence, Reversibility, Review).

ID: E-001
Status: SETTLED
Decision: New top-level eval/ track for all ground-truth evaluation
code; v1 imported read-only or vendored, never edited.
Why: v1 is frozen by standing rule; v2/validate_v2.py (sys.path
import) and v3/vendor (copy with provenance) are the two sanctioned
reuse patterns; the evaluation needs both.
Alternatives: extending v2 (rejected: v2 is the live-pipeline track,
not an analysis track); editing v1 (forbidden).
Evidence: AGENTS.md standing constraints; approved plan of 2026-08-25.
Reversibility: folder move; nothing outside eval/ depends on it yet.
Review: layout in eval/README.md.

ID: E-002
Status: SETTLED
Decision: Stage 1 inspection reads the frozen extractors' raw CSVs
rather than re-reading the bag with new code.
Why: the extractors are the validated measurement instruments the
whole thesis rests on; coverage numbers must come from the same code
path the analysis uses; a second bag reader would be a second source
of truth.
Alternatives: standalone pyrealsense2 inspector (rejected as above).
Evidence: extractor meta JSONs carry frames_total, per-id detections,
blocked-landmark counts natively.
Reversibility: none needed; inspector is additive.
Review: eval/inspect/inspect_recording.py.

ID: E-003
Status: UNCERTAIN
Decision: Phase segmentation constants: person presence = has_pose
runs of at least 15 frames; object moving = marker travel over 3 cm
per 7 frames (constants reused from the v1 carry classifier);
manipulation = envelope from first to last moving frame; entry /
approach / retreat derived from those boundaries.
Why: reuses the one motion definition already pinned in the thesis
(analyze_object_offset.py K=7 / 3 cm); presence run length suppresses
pose flicker at scene edges.
Alternatives: pelvis-to-desk distance thresholds (needs calibration,
adds a constant with no pinned source).
Evidence: resulting phases (entry 0-44, approach 45-223, manipulation
224-1314, retreat 1315-1498) eyeballed against the coverage timeline
and marker-overlay plots and consistent with the recorder's 10 s
preview-wait scenario; not yet checked against the raw video stream
frame by frame.
Reversibility: constants at the top of inspect_recording.py; rerun
regenerates reports.
Review: eval/reports/recording_20260825_070152_coverage_timeline.png.

ID: E-004
Status: SETTLED
Decision: The desk-anchor hard check passed (id 2 detected 1499/1499),
so processing proceeds; R4 stands as the primary recording.
Why: spec condition - the world frame depends on the desk marker.
Alternatives: none (stop condition).
Evidence: v1/aruco extractor meta detections {0: 1447, 1: 1495,
2: 1499}; eval/reports/recording_20260825_070152_inspection.md.
Reversibility: n/a (a fact about the recording).
Review: inspection report anchor section.

ID: E-005
Status: SETTLED
Decision: Held-frame classification on R4 is per hand and independent:
hold = marker measured AND carried AND wrist raw (flag 0) AND wrist
within HOLD_RADIUS = 0.25 m of the box center AND forearm length
plausible. The vendored R1 nearest-wrist rule is kept only for the R1
regression check.
Why: R4 contains a hand-over during which the true holder's wrist is
occluded; nearest-wrist then assigns the visible far wrist (45-50 cm
away) and poisons the fit (right-hand grip std 17.7 cm, residual
median 16 cm). With per-hand classification the stds drop to 4-8 cm
and both-hands segments are handled naturally.
Alternatives: nearest-wrist (fails as above); hidden-state HMM over
holders (unjustified complexity).
Evidence: held-magnitude distribution is bimodal - holding 14-22 cm
vs free 40+ cm (fit plot, diagnostic percentiles: right 5/25/50 pct =
13.7/15.9/18.6 cm vs 75/95 pct = 41.2/49.7 on the mixed mask); 0.25 m
sits in the empty gap.
Reversibility: constant in eval/offset/carry.py; rerun fit_offset.py.
Review: eval/reports/recording_20260825_070152_offset_fit.png top
panel (dots = held frames).

ID: E-006
Status: SETTLED
Decision: Carried classification on R4 = inside the stage-1 motion
envelope AND (farther than REST_DIST = 0.04 m from both rest-cluster
centroids OR moving OR lifted above 6 cm).
Why: the R1 classifier (6 cm height OR 3 cm / 7 frames motion) misses
most of R4's manipulation: the box slides along a desk-level wire at
2.8-3.9 cm leveled height and a median 6.4 cm/s (13 cm/s equivalent
threshold), classifying only 479/1499 frames as carried where the
manipulation phase spans ~1091. Rest-referenced distance separates
"parked at its start/end spot" from "in hand on the wire".
Alternatives: lowering the height/speed thresholds (would misclassify
the parked phases of other recordings; rest-reference is scenario-
agnostic).
Evidence: diagnostic run 2026-08-25 (leveled heights, speed deciles);
carried rises to 988/1499 in 4 segments, consistent with the
manipulation phase minus the wire stretch passing over the rest spot
(frames 390-438).
Reversibility: constants in eval/offset/carry.py.
Review: same plot, shading vs the known scenario.

ID: E-007
Status: SETTLED
Decision: Wrist samples with implausible forearm length (deviation
over 30 percent from the recording median) are excluded from the
grip fit (forearm_ok gate).
Why: R4 contains depth-collapse stretches (right forearm apparent
length falls to 3-10 cm around 38-41 s while visibility stays high);
those wrist positions are demonstrably wrong by the segment-length
argument and would bias the fit.
Alternatives: none reasonable - this is the segment-length constraint
the professor's occlusion spec itself prescribes.
Evidence: fit plot bottom panel; the same frames feed the stage-5
gate miss-rate analysis.
Reversibility: FOREARM_TOL constant.
Review: eval/reports/recording_20260825_070152_offset_fit.png bottom
panel.

ID: E-008
Status: UNCERTAIN
Decision: Dwell detection thresholds: smoothed speed below 2 cm/s
sustained at least 0.5 s, 5-frame smoothing, carried frames only.
Why: the carried-speed histogram is strongly bimodal (tracing motion
5-30 cm/s vs corner pauses under 1 cm/s); 2 cm/s sits in the gap.
The carried-only restriction keeps the parked start/end rests out.
Alternatives: lower threshold (1 cm/s) misses nothing on R4 but was
not stress-tested; per-axis thresholds unjustified.
Evidence: eval/reports/recording_20260825_070152_path_overview.png
(histogram panel). Result on R4: exactly one dwell survives (frames
648-742, 3.14 s, bottom-right corner, cluster std under 1 mm) - the
carrier paused only during the hand-over. UNCERTAIN because the user
may prefer looser thresholds so brief corner slowdowns count as
dwells; rerun analyze_gt_path.py after changing V_THRESH/MIN_DUR_S.
Reversibility: constants at the top of eval/gt/analyze_gt_path.py.
Review: the speed-vs-time panel of the same plot.

ID: E-009
Status: UNCERTAIN
Decision: Per-marker scale correction applied to all R4 ArUco
translations: id2 desk x0.8748, id1 object x0.8700, id0 wall x1.0258
(eval/gt/scale_correction.py; corrected CSV + recalibration under
eval/output/, now the authoritative R4 track via paths.r4_calib()).
Why: the stage-2 depth cross-check failure was root-caused: the
PnP/depth range ratio is 1.1432 (desk) / 1.1494 (object), constant
over the whole recording (p5-p95 within 0.004 for the desk) and
across ranges 0.76-1.08 m - the signature of a marker printed
smaller than declared, not a depth or extrinsics error. Implied
actual sizes: desk 43.7 mm, object 43.5 mm (declared 50; consistent
with a fit-to-page print shrink), wall 153.9 mm (declared 150). R1
ratios are 0.999-1.008 with the old prints. PnP translation scales
exactly linearly with declared size for a planar square, so post-hoc
rescaling is exact.
Alternatives: re-extraction with patched sizes (equivalent, slower);
ignoring (leaves a 14.5 percent scale error in every stage-1/2
number).
Evidence: eval/reports/r4_marker_scale.json; after correction the
right-hand whole-span drift collapsed +21.9 -> -0.01 cm/min, the
left grip std fell to (3.2, 1.0, 1.2) cm, and origin_above_tabletop
moved from -9.7 mm to +10.9 mm - three independent quantities became
physically consistent.
Reversibility: delete eval/output/scene_calibration_r4c.json and the
scaled CSVs; paths.r4_calib() falls back to the uncorrected set.
Review: MEASURE THE PRINTED MARKERS WITH A RULER (black border side
length, all three) and compare with implied_actual_mm in
r4_marker_scale.json; then set Status SETTLED or correct the factors.

ID: E-010
Status: UNCERTAIN
Decision: Frame 1225 (t = 40.86 s) is the candidate running-example
frame replacing R1's frame 100 across the manuscript.
Why: top of the objective stage-1 shortlist - manipulation phase, all
three markers detected (max reprojection 0.353 px), all eight
landmarks src = 0, highest minimum landmark visibility (0.793); the
scene shows the cube held aloft at the top-left corner of the wire
with both arms engaged, which is also narratively representative.
Alternatives: frames 1221-1230 (same cluster, near-identical
quality); any hand-picked frame (rejected - the shortlist is
criteria-driven).
Evidence: eval/reports/recording_20260825_070152_inspection.md
shortlist; extracted image
eval/reports/recording_20260825_070152_frame1225.png.
Reversibility: pick another shortlist frame and rerun the figure
scripts; nothing else depends on the choice yet.
Review: look at the extracted frame; confirm before the manuscript
rebase starts.

ID: E-009a (amends E-009)
Status: SETTLED (as a working assumption; the ruler measurement can
overturn the value)
Decision: Per user direction 2026-08-25, the working black-square
size for the desk and object markers is 45 mm (scale 0.9000 exactly);
wall stays 150 mm. The single source is
eval/common/marker_size.py: ASSUMED_BLACK_SQUARE_M - every dependent
number regenerates from that one constant via the command list in
its docstring, and every derived artifact carries a
scale_source/assumption label.
Why: the user confirmed the marker cards are unchanged from R1 and
chose 45 mm as the value to run all experiments on until measured.
Alternatives: depth-derived 43.7/43.5 mm (kept as diagnostics in
r4_marker_scale.json; note the constancy drift is -0.01 cm/min at
43.6 mm vs +4.4 cm/min at 45 mm - mild evidence for the smaller
value).
Evidence: user message 2026-08-25; drawn-path span 45 cm vs tracked
44.7 (43.6 mm) / 46.0 (45 mm).
Reversibility: edit one constant, rerun the listed commands.
Review: measure the BLACK SQUARE side with a ruler; update
marker_size.py if it differs from 45 mm.

ID: E-011
Status: SETTLED
Decision: The robust chain layer gains a torso line-consistency gate
with symmetric attribution and hysteresis
(v1/kinematics/occlusion_ext.py): when the hip line and shoulder
line disagree by more than 20 deg (release at 10 deg), the pair
whose direction deviates more from its own EMA memory is the corrupt
one; a single endpoint blamed by its torso diagonal is gated
normally, otherwise the whole line is rebuilt around its measured
midpoint along its memory, steered toward the surviving line. Root
and dependent arm groups are demoted to CONSTRAINED.
Why: user review of the first R4 Unity reconstruction ("body changes
direction suddenly"). Diagnosis: hands/cube crossing in front of the
torso poison the landmark depth (visibility stays ~0.98, pair width
stretches <11 percent), rotating one torso line 25-40 deg. R4 shows
both variants: hip-line corruption at 18-24 s (hip line +24 deg,
shoulders +9), shoulder-line corruption at 34.5-36 s (shoulder line
spikes to 59 deg, hips stable). Neither the visibility gate (B1) nor
the width gate (B2) can fire on this mode.
Thresholds (plot-first): hip-vs-shoulder 3D line angle - R1 clean
p95 15.6 / p99 17.3 / max 18.9 deg; R4 corrupt windows 30-59 deg.
Trip 20 deg sits above everything R1 ever does; release 10 holds
through R4's just-under-threshold plateaus. Zero fires on all of R1.
Result (R4, person-present window): root yaw deviation p95 31.6 ->
17.1 deg, max 39.2 -> 21.3 deg; validate_occlusion_ext.py grows to
28 checks (sections 5/5b: synthetic hip- and shoulder-side
corruption; recovery beats trusting the corrupt line 52.8 -> 16.4
and 31.3 -> 7.1 deg p95) - all pass, clean-R1 behavior bit-identical
outside gated frames.
Residual limitation: 24-31 s both lines agree at -10..-23 deg
(consensus corruption or real lean is indistinguishable using
rigidity alone); root yaw there is trusted as measured. A ray-based
reconstruction (keep the reliable pixel rays, resolve the two depths
from the calibrated width) could discriminate further - not
implemented.
Evidence: eval/output/v1_check/root_lines.png,
v1_check_plots.png; overlay video eval/output/v1_check/.
Reversibility: line_tol_deg=None disables the gate entirely
(bit-identical to the pre-E-011 layer).
Review: revisit thresholds if a future recording shows real axial
twist beyond 20 deg.

ID: E-012
Status: SETTLED
Decision: The robust chain layer gains angle-parameter stabilization
(v1/kinematics/occlusion_ext.py, step 6): (a) shoulder twist is HELD
(bit clear, tag HELD) while elbow flexion is below 15 deg, released
above 25 deg (hysteresis) - the same unobservability semantics the
model applies at exact singularity (A4, 1/sin amplification),
widened to the noise-aware threshold; (b) swing yaw is held while
the arm is within 10 deg of vertical (engage 80, release 70 deg of
|theta_z|), where azimuth is positionally meaningless; (c) every arm
parameter (theta_y, theta_z, tau, ey) passes a wrap-aware slew limit
of 15 deg/frame (450 deg/s), and while the limiter actively clamps,
the group bit is cleared and tagged CONSTRAINED (the output is not
the measurement until it converges). The root is excluded (E-011
owns root robustness).
Why: user review - "even the video overlay is not stable" and "once
occlusion happens the skeleton becomes very unstable". Measured
(R4, person-present window): worst per-frame steps Lsh_tau 149.4,
Lsh_y 107.0, Rsh_tau 32.8 deg/frame; 45 frames stepped >15 deg. The
three sources: 1/sin twist amplification near a straight elbow (tau
steps up to 162 deg/frame at 10-15 deg flexion), swing-yaw
degeneracy near a vertical arm (94 deg/frame above 85 deg
elevation), and transition snaps (re-lock after holds, demotion
into constrained recovery).
Thresholds (plot-first): R1 clean bounds - right-arm flexion never
below 30 deg, |theta_z| never above 60 deg, fastest clean right-side
step 11.4 deg/frame - so none of the three mechanisms ever engages
on clean R1 data (verified: zero right-side interventions in the
neutrality check).
Result: R4 max per-frame arm step 149.4 -> 15.0 deg (bound
saturated); frames stepping >15 deg 45 -> 1; p99 solve cost 0.34 ms.
validate_occlusion_ext.py grows to 32 checks (section 6: flexion
hold, honest slewed re-lock, vertical-arm yaw hold, slew-limit
clamp+demote) - all pass.
Note: MediaPipe model tier was checked as a suspect and cleared -
both R1 and R4 extractions and the live pipelines already run
pose_landmarker_heavy on GPU.
Evidence: step distributions in this session; eval/output/v1_check/.
Reversibility: flex_min_deg=None / swing_hold_deg=None /
rate_limit_deg=None disable each mechanism independently.
Review: thresholds if a future scenario includes genuinely fast arm
rotation (>450 deg/s) or overhead work near the vertical pose.

ID: E-012a (amends E-012)
Status: SETTLED
Decision: The swing-yaw vertical-arm hold from E-012 is REMOVED. The
final stabilization set is: (a) twist observability hold below 15
deg flexion (release 25, hysteresis), (b) wrap-aware 15 deg/frame
slew limit on all arm parameters with honest demotion (bit clear +
CONSTRAINED while actively clamping). Root excluded (E-011).
Why: the hold kept the swing bit LIVE while overriding the yaw
value - measured FK-wrist error on nominally live left-arm frames
reached 27.4 cm p95, an inversion where "live" frames were worse
than demoted ones. A stabilizer must never make a live claim
diverge from the measurement. The slew limiter alone bounds the
vertical-arm azimuth flips (94 -> 15 deg/frame) and demotes while
clamping.
Result (R4 final): max per-frame arm step exactly 15.0 deg, zero
violations; FK wrist residual on fully-live frames right 1.3/4.4 cm
left 3.5/4.9 cm (median/p95) - accurate where claimed live, larger
deviations only on demoted frames (right 4.7/13.6, left 3.9/11.2).
validate_occlusion_ext.py stays at 32 checks, all passing.
Evidence: live-vs-demoted residual split in this session.
Reversibility: the E-012 flags; the hold code is deleted, not
parameterized.

ID: E-013
Status: SETTLED (USER-SET precondition)
Decision: Recording validity precondition (ASSUMPTIONS.md A6):
accuracy-evaluation windows require the evaluated landmarks to be
TRACKED - coverage >= 95 percent, no gap > 0.5 s over the
person-present span; enforced by
eval/inspect/check_tracking_precondition.py (run after every new
extraction, before any other use of the take). Occlusion robustness
is evaluated by synthetic masking of tracked segments (truth known
by construction), never on naturally occluded stretches (no truth
exists there); natural occlusion stays as qualitative case-study
material (continuity, honesty tags, recovery behavior).
Why: user direction 2026-08-25 after reviewing R4 f951 - "we shall
have precondition the mediapipe is actually tracking the human
body". At f951 the left elbow/wrist report visibility 0.06-0.22 for
~8 s (hand wrapped behind the carried cube): the pipeline correctly
holds, but nothing can be graded there. Even the heavy model cannot
see through the cube; this is a scenario-protocol issue, not a
model-tier issue.
R4 disposition: torso PASS, right hand PASS, LEFT hand FAIL (wrist
coverage 55.4 percent, longest gap 8.8 s). R4's right-hand carry
segments remain valid evaluation windows; the left-carry phase
(approx 28-36 s) is out of evaluation scope. Left-hand offset-fit
frames (stage 3) were tracked frames by construction and remain
valid, but left-hand path-following coverage is thin.
Re-recording protocol (R5, when on site): same four-phase scenario,
but (1) grip the cube from the side/bottom so the wrist and fingers
stay camera-visible - never wrap the hand behind the cube; (2) keep
the carrying arm slightly off the torso and avoid crossing the
chest with the cube (also prevents the E-011 depth-corruption
windows); (3) after recording, run the extractor + the precondition
checker on-site - a compliant take shows all-PASS in about two
minutes; re-record until it does.
Evidence: eval/reports/r4_tracking_precondition.json; R1 all-PASS
(the checker discriminates correctly).
Reversibility: thresholds are CLI flags on the checker.
Review: with the professor - whether the left-carry phase should be
re-recorded (R5) or the thesis evaluates the right hand only.

ID: E-014
Status: SETTLED
Decision: The robust chain layer gains object-conditioned recovery
(v1/kinematics/occlusion_ext.py, solve(points, obj=None)): during
failure frames of a HOLDING hand, the wrist is placed at the
object-derived estimate W = o + R_obj mu (same-frame measured object
pose + per-episode grip offset), and a missing elbow is placed by
closed-form two-link IK (sphere-intersection circle, swivel = EMA
projection with gravity-down fallback, cosine clip for degeneracies).
Recovered groups demote to CONSTRAINED, never MEASURED. obj=None is
bit-identical to the pre-E-014 layer.
Why: user direction 2026-08-26 (R5 plan task 1) - during MediaPipe
failure the object pose shall determine the pose. The object marker
stays measured through every R5 person-tracking failure window.
Alternatives: eval-side post-processing only (rejected: the solver
layer feeds statistics, overlay, and Unity from one implementation,
and the real-time argument then points at the actual solve path);
constant-velocity extrapolation (already rejected, E-012 note).
Evidence: validate_occlusion_ext.py 32 -> 37 checks all PASS;
eval/reports/r5_object_conditioned_recovery.md (full mathematics);
overlay eval/output/recovery_r5_overlay/.
Reversibility: omit the obj argument.
Review: synthetic-mask numbers in r5_recovery_synthetic.md.

ID: E-015
Status: SETTLED
Decision: MediaPipe failure on R5 is detected per frame by five
binary detectors (eval/failure/detect_failures.py): D1 acquisition
(src != ok), D2 segment length (35 pct), D3 torso line angle
(22 deg), D4 width ratio (20 pct), D5 landmark step (5 cm/frame);
morphological closing bridge 5 / min event 5 frames. Thresholds are
plot-first from R1 with pinned headroom; D3/D4/D5 fire zero times on
R1. SEG_TOL 0.35 is derived from R1's RIGHT arm only: R1's left arm
has real elbow-slide defects (96 frames, documented in
r5_failure_mask.md); forcing zero left-arm fires would need 0.65 and
silence genuine R5 corruption - calibrating to a defect.
Why: task 1 requires an objective definition of "skeleton off the
body" including confident-but-wrong frames (high visibility, wrong
depth), which no visibility gate can catch.
Evidence: eval/reports/r5_failure_mask.md, r5_failure_events.csv,
r5_failure_thresholds.png; sanity windows (left 1458-1668, right
1826-1893) are 100 pct D1-covered.
Reversibility: constants at the top of detect_failures.py.
Review: event boundaries eyeballed against the overlay video.

ID: E-016
Status: SETTLED
Decision: Holding-hand determination for recovery is a causal grip
state machine (eval/failure/grip_state.py): enter after 5 clean
holding frames, persist through wrist failure while the object stays
carried (rigid-grasp persistence), exit on rest or a clean wrist
beyond 0.35 m (hysteresis over HOLD_RADIUS 0.25) for 5 frames. Grip
offsets are fitted PER EPISODE (min 15 clean frames, recording-wide
fallback), masked frames excluded.
Why: the instantaneous classifier needs a measured wrist -
unavailable exactly on recovery frames; and R5's episode fits differ
by up to 18 cm (regrasps between stations) while the global fit
residual is 8 cm median - one mu per grasp, not per recording.
Evidence: eval/output/recovery_r5/grip_episodes.json (6 episodes,
per-episode mu/sd); handover = two overlapping episodes ~1014-1110.
Reversibility: constants at the top of grip_state.py.
Review: episode boundaries vs the overlay video.

ID: E-017
Status: SETTLED
Decision: R5 waypoints are the SIX pause stations detected from the
recording itself (user decision 2026-08-26: no physical survey):
secant speed (+-5 frames) below 4.0 cm/s for >= 0.3 s on the carried
loop span, x-y cluster merge at 6 cm, station dwell >= 0.5 s. Spec:
eval/gt/labeled_path_r5.json (W1_desk_left, W2_desk_center_handover,
W3_desk_right_lift, W4_wire_right, W5_wire_center, W6_wire_left);
detector eval/gt/detect_waypoints.py.
Why: exactly six stations emerge on a broad threshold plateau
(3.0-4.8 cm/s all give six, positions stable to 6.9 mm), matching
the video-derived reference analysis within 10.1 mm; the 1-frame
gradient speed is jitter-flat below 10 cm/s, so the secant speed is
the discriminating statistic.
Alternatives: labeled_path.json 4-corner schema (R4 layout, wrong
scenario); physical survey (declined by user).
Evidence: eval/reports/r5_waypoint_eval.{md,json}, r5_waypoints.png
(threshold sweep panel). Point-to-path median 1.84 cm / p95 7.49 cm;
the closing W6->W1 segment (median 7.27 cm) cuts the two un-paused
left corners - structural, annotated.
Reversibility: constants at the top of detect_waypoints.py.
Review: whether the thesis figure adds the two corner shape points
to the ideal polyline (presentation choice, not measurement).

ID: E-017a (amends E-017)
Status: SETTLED
Decision: R5 waypoints are EIGHT, per the operator's corrected design
(2026-08-26): W1_start (parked rest position), W2_back_end,
W3_desk_handover, W4_left_end, W5_forward_end, W6_lift_top,
W7_wire_handover, W8_wire_left. Both handovers are designed
waypoints. Clustering is by FULL 3D distance (the E-017 x-y merge ran
in the tilted desk-marker projection, which compressed the camera
depth axis and wrongly fused W4/W5, 8.0 cm apart in 3D); the figure
and step decomposition use the gravity-leveled frame.
Why: user correction - designed moves are start -> back ~30 cm ->
left ~45 cm -> forward ~15 cm -> up ~30 cm -> wire with a second
handover; measured steps 28.7 / 32.8 (sequential) / 8.4 / 30.8 cm.
Seven stations are detected on the same 3.0-4.8 cm/s plateau; the
start is added from the rest frames.
Evidence: eval/reports/r5_waypoint_eval.{md,json}, r5_waypoints.png;
point-to-path median 0.80 cm / p95 9.32 cm (closing descent cuts the
un-paused corners - structural).
Reversibility: constants in eval/gt/detect_waypoints.py.
Review: none pending; supersedes the E-017 six-station reading.

ID: E-014a (amends E-014)
Status: SETTLED
Decision: Two refinements from the synthetic-mask evaluation:
(1) the grip offset mu is estimated TIME-LOCALLY (per-episode EMA,
gain 0.02/frame ~ 1.7 s memory, frozen through failure windows,
restarted per episode after a 5-frame warm-up;
grip_state.time_local_mu) instead of a per-episode constant;
(2) above 98 percent of full arm reach the recovered elbow comes
from the direction memory instead of the cosine-law IK (flexion is
ill-conditioned there: d(flexion)/dr diverges as r -> L1+L2), wrist
still anchored at the object estimate.
Why: the harness measured (a) up to 13 cm of within-episode grip
drift (regrips at stations) biasing the constant mu - time-local mu
cuts the wrist-estimate error from 6-10 cm to 1.2-4.5 cm median on
rigid-grasp windows; (b) a 2 cm anchor bias at 97 percent reach
snapping a 21.6 deg flexion straight - the guard keeps it within
0.9 deg (validator check 38).
Evaluation outcome (honest): on moving outages the recovery gives
the best FK wrist position of all methods (1.6 cm median vs hold's
21 cm max within 1 s, r5_recovery_moving.md); on short stationary
outages hold-last is competitive by construction; at handovers (the
grasp changes mid-outage) the estimate degrades to 6.9-14 cm -
stated limitation. Honesty violations: zero.
Evidence: eval/reports/r5_recovery_synthetic.{md,json,png},
r5_recovery_moving.{md,json}; validate_occlusion_ext.py 38 checks.
Reversibility: MU_ALPHA=None-equivalent by using per_frame_mu;
the guard threshold is a constant in occlusion_ext.py.
Review: none pending.

ID: E-014b (amends E-014)
Status: SETTLED
Decision: Two recording-independent plausibility bounds guard the
recovery (user direction 2026-08-26, "the object location and the
wrist should not exceed a range"): D6 - a MEASURED wrist farther
than GRIP_MAX = 0.35 m from the held box center during a grip
episode is flagged as a wrong measurement (removed and recovered),
and MU_MAX = 0.30 m - a grip-offset estimate beyond it is discarded
instead of used. Constants in eval/failure/recovery_core.py.
Why: generalization - the D1-D5 thresholds are verified against R1,
but a confidently-wrong wrist that stays length- and speed-plausible
while drifting far from a held object had no gate; physically a
holding wrist cannot leave the object. GRIP_MAX matches the release
hysteresis radius; MU_MAX exceeds every legitimate fitted offset
(largest R5 episode mu 0.24 m) while rejecting non-grips.
Evidence: on R5, D6 flags 15 frames (all inside D1-D5 windows - no
outcome change on this recording), MU_MAX fires zero times; moving-
window results unchanged (r5_recovery_moving.md).
Reversibility: constants.
Review: none pending; genuinely smooth clean-looking wrist drift in
a live system degrades to the honest hold (limitation noted in the
mathematics report).

ID: E-018
Status: SETTLED
Decision: The Unity sender applies a DISPLAY smoother to the 13-angle
stream (eval/unity_check/send_scene_r5.py AngleLPF): causal
first-order low-pass (alpha 0.5) plus a wrap-aware output rate cap
of 8 deg/frame. --lpf-alpha / --lpf-max-step; alpha >= 1 with cap 0
disables. Analysis CSVs and every reported number stay unfiltered.
Why: user review of the recovery overlay ("i do noticed some of the
jumps ... a simple lpf should work"). Measured jump sources: arm
parameters saturating the solver's 15 deg/frame slew bound over
3-5-frame transition ramps (50-60 frames each) and root yaw re-locks
up to 26 deg/frame (root is excluded from the slew limit, E-011).
A plain LPF alone cannot fix ramps: any unity-gain linear filter
follows a sustained ramp at the ramp's slope - measured, single pole
passed 14.7/15 deg per frame, second-order Butterworth 16 deg/frame
with up to 52 deg overshoot. The rate cap is the part that bounds
on-screen speed; the low-pass rounds corners and spikes.
Result (R5 recovery track): display steps > 10 deg/frame 148 -> 0,
max step 8.0 deg/frame, tracking error vs the solver output median
0.14 / p95 2.1 deg; the largest transient deviation (84 deg for
~0.3 s) occurs during a legitimate large re-lock the display crosses
at capped speed.
Alternatives: first-order EMA alone, 2nd-order Butterworth
(measured, rejected above); smoothing inside the solver (rejected:
the solve output is the measurement record, display concerns stay in
the display path).
Reversibility: CLI flags.
Review: watch the next Unity replay; raise the cap if the rig feels
laggy during fast real motion.

ID: E-011b (amends E-011)
Status: SETTLED
Decision: The torso repairs are ray-based (user review 2026-08-26:
"when the torso landmark miss the data, its still not stable"), the
extension E-011 anticipated. Three parts
(v1/kinematics/occlusion_ext.py):
(1) depth memories: per torso landmark, EMA of the camera depth from
measured frames;
(2) ray repair: a joint gated for corrupt depth is placed back on
its own camera ray (the pixel stays reliable when depth corrupts) at
its remembered depth. A line-gated PAIR takes position (midpoint)
from the ray repairs and orientation from the repaired direction
passed through the line's EMA - raw ray directions carry the pixel
wobble of hands crossing the torso. The calibrated width is NOT
forced onto the repair: apparent width varies 10-15 percent with
pose, and rescaling to the median was measured to inject ~10 cm of
common depth error (rigidity stays a detector, not a projector);
(3) depth-jump gate (z_tol = 0.10 m): consensus corruption - both
lines poisoned together, agreeing - is invisible to the line gate
(E-011's documented residual limitation) but is a depth teleport at
a standing pixel; |z - zmem| > 10 cm gates the joint into the ray
repair. Plot-first: clean deviations 2.5 cm max on R1, p99 ~5 cm on
R5 clean-torso frames; corrupt R5 hips median 23 cm. Zero fires on
R1.
Result: synthetic pixel-preserving depth corruption (validator,
now 39 checks all passing): repaired hip within 0.2 cm of truth,
root p95 8.9 deg vs 54 corrupt. R5 torso windows: root yaw range
8.5 -> 2.5, 49.0 -> 15.3 (the 48 deg consensus flip at the handover
eliminated), 20.8 -> 13.2 deg; streamed pelvis depth wander during
corruption 22 cm -> 0.5 cm (pelvis now exported from the repaired
hips through the angle CSVs and preferred by the Unity sender).
Also: the validator's synthetic corruption now scales points along
their rays (pixel-preserving), the physically faithful model of a
wrong depth sample; the old axis-push also corrupted the pixel.
Reversibility: z_tol=None disables the depth-jump gate; without
depth memories every repair falls back to the pre-E-011b behavior.
Review: the orientation EMA lags a genuine fast torso rotation
during a gated stretch (the deliberate wobble-vs-lag trade; 10 deg
p95 bound pinned in the validator).
E-021 note (2026-08-28): the 8.5/49.0/20.8 baselines above were measured
with the whole repair off. The thesis (Chapter 7, Table 7.7) reports the
ablation that disables the depth-jump check alone, with the line gate and
ray repair active in both arms: 2.5/57.4/13.2 -> 2.5/15.3/13.2 deg; the
repaired values are identical.

ID: E-019  [cause SUPERSEDED by E-022: the handover swing was the filter's gap hold, not detected-but-wrong poses; the cleaning rule blanks no detected row on R5 after the fix]
Status: SETTLED
Decision: The object track is CLEANED once by a simple filter
(eval/common/clean_object_track.py), and every consumer reads the
clean CSV through paths.object_world_filtered() - no marker
robustness logic anywhere else (user direction 2026-08-26: filter
the marker, keep the setup simple, the focus is the rig;
skill_set/marker-simplicity.md). Rule: keep a sample only if
detected, finite, and within V_MAX = 1.0 m/s and W_MAX = 400 deg/s
of the last kept sample (rates, so real gaps allow proportional
travel); rejected and undetected rows are blanked and consumers
hold the last pose with the live flag off.
Why: user review of the side-by-side at the first handover ("the
box lost track drifting very fast"): the marker is half-covered by
hands there, the detector returns detected-but-wrong poses from the
sliver, and the track filter emits positions on undetected rows
smoothed from those wrong neighbors - the streamed box swung tens
of centimeters frame to frame (measured: x -0.066 -> -0.254 ->
-0.062 -> -0.239 across 25 undetected rows).
Bounds from two recordings' clean data: R1 maxima 0.26 m/s / 82
deg/s, R5 clean maxima 0.41 / 179 - both bounds hold 2x headroom
and reject zero clean samples on either recording; on R5 exactly
the handover corruption goes (1 detected row + 41 smoothed
undetected rows).
Reversibility: delete the _clean.csv; the accessor falls back.
Review: rerun clean_object_track.py after every new extraction
(added to the standard chain).

## E-020 (2026-08-26): joint-limited elbow IK - tested, null on this data

User idea: formalize the arm as a manipulator chain (DH-style) and
add joint limits to the recovery; explicitly to be tested, not
assumed. Derivation (derive_limit_bounds.py): of the candidate
limits, flexion cannot discriminate swivel candidates (identical on
the whole circle, cosine law), a swing-twist tau box rejects
genuinely measured poses (R5 left has 241 clean frames at
-150..-120 deg), and only the torso-capsule clearance survives
(TORSO_RADIUS_FRAC 0.334 of shoulder width, strictest clean p1 of
R5+R1 with 20 percent slack). Implemented opt-in in occlusion_ext
(elbow_limits=True; prior kept when feasible, nearest feasible
circle point when not, prior when nothing is feasible; flag-off
bit-identical; validator 39 -> 42 checks). Experiment
(harness_limits.py, E-013 masking on R5+R1 + the natural R5 failure
recovery): ZERO interventions anywhere - the continuity prior never
proposes a torso-penetrating elbow on these tasks; all errors
identical. Disposition: kept as a verified safety guard; the
manipulator formulation goes into the thesis as the presentation of
the recovery; the limit is claimed as a verified invariant, not a
correction. Evidence: eval/reports/r5_joint_limit_ik.{md,json},
r5_limit_bounds.{md,json}. Reversible: flag off (default).

ID: E-021
Status: SETTLED
Decision: The three R5 reports written on 2026-08-26 before E-014b
(mu cap + D6) and E-011b landed - r5_waypoint_eval, r5_recovery_synthetic,
r5_recovery_moving - were regenerated on 2026-08-28 against the committed
code (detect_waypoints.py, harness_recovery.py, moving_window_check.py,
no code change). Material differences: loop frames 1031 (was 1032);
grip episodes shift (left 1014-1065, holding 771 frames), so the
synthetic study carves 3 windows (left 1670-1760 -> 1674-1718, right
661-705 and 1674-1718) instead of 4, eligible frames left 154 / right
304, 9 window-scenario runs; moving-outage rows change by up to 1.7 cm
on the max (masked outage 2 max 4.79, was 3.07). Point-to-path median
0.80 / p95 9.32 / max 13.11 cm unchanged. The thesis (Chapters 7 and
9) cites the regenerated reports only.
Why: the Chapter 7 review found the chapter mixing frozen pre-E-014b
values with re-run values; one code state must back every number.
Reversible: git history holds the 2026-08-26 versions.

ID: E-022
Status: SETTLED (user decision 2026-08-28: "Unfreeze and then fix it" - option (b))
Finding (2026-08-28, Chapter 4 review, verified): the "handover
defect" that E-019 attributes to the detector decoding a half-covered
marker is produced by the track filter. Raw detections through the
first handover are clean (1065 tx -0.0660, 1066 tx -0.0660, 1076 tx
-0.0666); for an interior undetected run longer than --max-gap,
v1/aruco/filter_object_track.py:152-155 holds the run at pos[vidx[-1]],
the last valid frame of the WHOLE recording (tx -0.2386), not the
neighbouring frame, and the Savitzky-Golay window then drags the
adjacent detected rows toward it (1066 filtered tx -0.1303, 6.4 cm off
its own detection). The E-019 cleaning rule removes the contaminated
boundary rows by their implied step, so the downstream results stand,
but the cause stated in E-019 and in the earlier Chapter 4 draft is
wrong. Chapter 4 now describes the true mechanism.
Options: (a) leave the frozen v1 filter as is (current); (b) change
src to the nearest valid neighbour (one line), re-run
filter_object_track.py, clean_object_track.py and every downstream R5
artifact (waypoint evaluation, offset fit, recovery, probe dumps),
and re-verify Chapters 4, 7, 8, 9. (b) changes frozen numbers; the
user decides.
Resolution: R5 unfrozen for this defect; filter_object_track.py now
holds an interior over-long run at the previous valid pose; the R5
chain from filter_object_track.py onward is re-run and every report and
chapter number downstream re-verified (see the E-022 re-run commit).
E-022 re-run result (2026-08-28): chain re-run from filter_object_track.py
(filter, clean, inspect, offset fit, detectors, recovery, waypoints,
synthetic harness, moving check, overlay). The filtered track is now
flat through the handover gap 1067-1075 (tx -0.0660 held from 1066);
the E-019 cleaning rule blanks NO detected row on R5 (was one, frame
1066), so on this recording it is a safety net that never fires. Loop
frames 1032 (was 1031), point-to-path median 0.79 cm (was 0.80), p95
9.32 and max 13.11 unchanged; grip episodes end at 1066 instead of
1065; synthetic windows unchanged (left 1674-1718, right 661-705 and
1674-1718); moving-outage table and failure masks unchanged. The v2
real-time path imports only geodesic_interp from the filter module,
so the Chapter 8 probe numbers are unaffected. harness_recovery.py's
interpretation and limitation sentences are now computed from the
window counts instead of hardcoded.

## E-023 (2026-08-31): scenario separation; no-occlusion rail recording R6B

User direction: the evaluation separates two scenarios - WITHOUT
occlusion and WITH occlusion - and the current focus is the
without-occlusion one. R5 stays the with-occlusion primary; the new
primary of the no-occlusion scenario is R6B =
recording_20260831_065553 (30 s, 900 frames, recorded 2026-08-31 with
the revised setup: a straight horizontal wooden rail raised above the
desk; the cube is lifted from the desk onto the rail and slid to its
far end, so the slide is physically constrained and the rail line is
the ground-truth path). Take 1 of the same session
(recording_20260831_065504, alias r6a) failed the A6 precondition on
every landmark (pose on 661/900 frames) and is kept only as a
rejected take; the user confirmed using the newest take.

R6B chain results: pose on 900/900 frames; torso PASS (hips/shoulders/
elbows at 99-100 percent); object marker 899/900; desk anchor every
frame. Wrist coverage is the usual MediaPipe weak spot, not occlusion:
the idle left arm sits at 12.4 percent ok, the working right wrist at
87.7 percent with one 3.0 s natural gap mid-slide (frames 550-639).
Offset fit: right hand only, mu (-1.0, -2.2, +6.7) cm. The
object-conditioned recovery restores the right wrist on 101 frames
across the natural gaps (elbow IK on the same frames).

Ground truth: detect_waypoints.py stays pinned to the R5 7-station
step plan and is NOT applied to R6B (it detects 2 dwell stations here,
the rail ends). The rail scenario gets its own evaluator,
eval/gt/eval_rail_scenario.py: rail height from the upper mode of the
height histogram (band = half a cube, 3.5 cm), rail line by total
least squares, errors = perpendicular distance of the tracked centre
to the line. R6B result: travel 40.9 cm, perpendicular median 1.01 cm,
p95 2.58 cm, max 2.9 cm-scale, line tilt from horizontal 2.92 deg
(report r6b_rail_eval.md).

Two chain-generality fixes shipped with this round (both minimal, both
validated - validate_occlusion_ext ALL PASS):
- detect_failures.load_recording skips phases that are absent
  (R6B has no entry phase; the loader crashed unpacking None).
- recovery_core.build_inputs tolerates a hand that never held the
  object (per_hand fit None on a one-handed task).
- occlusion_ext depth-jump PAIR rebuild fires only after the width
  length and line memory have calibrated; before that the flagged
  joints fall back to the existing per-joint ray repairs (R6B has hip
  depth blips inside the 60-frame warmup; R5 never exercised this).

## E-024 (2026-09-01): R6B gravity seed and levelled rail evaluation

Finding (while drawing the R6B trajectory for the thesis): the stored
R6B world track showed a 21 cm "rise" during a 22 cm slide along the
desk. Cause chain, verified against the video and the raw files:
- The wall marker is near-degenerate on 898/900 R6B frames (lobes 36
  deg apart) and its lobe is chosen by continuity seeded once by
  plumbness against the depth-plane gravity seed.
- The seed (a plane fitted to a depth annulus around the desk marker)
  was 59 deg off vertical on R6B: the desk marker sits at the front
  edge of the desk in the rail setup, so the annulus reached the desk
  edge, the stand and the floor (on R5 the same fit is 4.3 deg off).
- With that seed the extractor kept the WRONG wall lobe (up axis 19.6
  deg off the camera vertical; the other lobe 3.2 deg off with its
  normal facing the camera). calibrate_scene reported
  gravity_seed_dev_deg 39.7 (R5: 4.9) and a wall pose 35 deg yaw / 67
  deg roll away from R5's for the same wall.
- The object and desk poses were never affected (the object track in
  the desk-marker frame is bit-identical before and after the fix).
  What was wrong: gravity_up (the levelling), T_cam_wall, and every
  height reading taken in the unlevelled desk-marker frame, whose card
  stands on a stand tilted 32 deg from vertical.

Fix 1 (extract_aruco_poses.py): a new seed source, estimate_tabletop_
between(): one plane fitted to the desk surface BETWEEN the desk card
and the object card (the image rectangle spanning both quads plus one
card width each side, from the bottom of the object card to the top of
the desk card), preferred whenever both markers are detected; the
annulus fit stays as the fallback. Same robust refit gates. On R5 the
new seed agrees with the old within 1 deg on all ten calibration frames
(the frozen R5 chain is not re-run). On R6B it is 10 deg off the camera
vertical (the grid paper near the front edge gives a biased stereo
plane), which is inside the seed's ~10 deg requirement: it lies 8 deg
from the correct wall lobe and 30 deg from the wrong one. Meta records
"seed_source". R6B re-extracted: wall lobe now the plumb one (up 3.2
deg from the camera vertical), calibrate_scene seed agreement 6.21 deg,
stand tilt 32.04 deg (R5 31.7), wall Euler (-58, -2, -3) (R5 -58, -2,
-5). The chain from scale_correction through run_recovery was re-run;
recovery counts unchanged (101 object-recovered right-wrist frames).

Fix 2 (eval_rail_scenario.py): the track is levelled by the calibrated
gravity (carry.LeveledWorld, the same frame detect_waypoints.py uses)
before the height-mode segmentation and the line fit; the report
states the frame. Before, "height" was the desk card's in-plane y axis
(58 deg from vertical), and the 2.92 deg "rail tilt" was measured
against it. R6B levelled result: desk level 3.5 cm above the origin
(the marker centre is half a cube above the tabletop, as it must be),
rail level 7.4 cm, rail line 0.05 deg from horizontal, perpendicular
median 0.97 cm, p95 2.36 cm, max 3.08 cm, vertical component median
0.32 cm, travel 40.9 cm (report r6b_rail_eval.md). The evaluator's
"lift" segment is really desk move + lift (25.0 cm, tilt from vertical
88.5 deg); the thesis figure separates them by the waypoints below.

Physical correction: the rail lies FLAT (a 2-by-4: 3.8 cm tall, top
face 8.8 cm wide); the tape photo reads 4 cm at the top and the
levelled track rises 3.6-3.9 cm from desk to rail. The earlier
description "on edge, top face 8.8 cm above the desk" was wrong.

Reference path of the rail recording (user definition, revised the same
day): an axis-aligned polyline, one direction per leg. Leg 1 from the
parked start straight back (z only) to W1, the foot of the lift at the
depth of the fitted rail line; leg 2 straight up (y only) to W2, the
start of the rail at the height of the fitted rail line; leg 3 along
the rail (x only) to W3, the far end of the fitted line. The corners
come from the physical geometry (parked mean over frames 0-91, the
fitted rail line), not from the track's own corners. Written by
writing/v7/scripts/make_ch7_rail_traj_fig.py to eval/reports/
r6b_waypoints.json: legs 25.48 / 3.61 / 37.44 cm; the track begins the
lift at frame 501 and reaches rail height at frame 529. The Chapter 7
figure draws the reference path, the fitted rail line and the tracked
centre, so the track's departures from the designed path are visible.

Unaffected: Chapter 3 worked example (landmarks only), Appendix E
worked example (object pose identical), the recovery reports.
Consequence for the thesis: abstract and Chapter 7 rail numbers
updated to the levelled values; Chapter 2 rail description corrected.

## E-025 (2026-09-01): synthetic-masking evaluation on the rail recording

harness_recovery.py --stem recording_20260831_065553 carved no window:
its clean condition required no detector to fire on EITHER arm, and the
rail task's idle left arm is low-visibility for 88 percent of the
recording. For a one-handed task the other arm's state says nothing
about the evaluated arm's reference solve (one arm's angles depend on
the root frame and that arm's own landmarks), so the harness gains a
--side-only flag: clean = the evaluated side plus the torso. Default
unchanged; r5_recovery_synthetic.{md,json} regenerate with identical
numbers (only the new "clean_condition" constant is added). Two chain-
generality fixes shipped with it: an empty-side statistic no longer
crashes the report, and the figure skips a side without windows. The
report's R5-specific interpretation paragraphs (headline, the torso-
failure explanation, the Interpretation section, the first limitation)
are now gated on the stem; other recordings get a number-driven
headline. moving_window_check.py takes its windows from the harness
report for any stem other than R5 (whose two hand-picked windows stay),
and its R5 Reading paragraph is gated the same way.

R6B result (eval/reports/r6b_recovery_synthetic.md, r6b_recovery_
moving.md): right arm only, 342 clean frames in one run (207-536, the
desk move and the lift; the wrist gap at 550-639 and the torso runs
after it end the run), five 45-frame windows. Truth arm motion per
window 3-8 deg (a slow task). Pooled S1 angle-error medians: hold-last
2.51 deg, EMA 0.60, object 1.34; object wrist-estimate error median
1.02 cm, p95 2.88. FK wrist error medians per window: hold 0.83-2.83
cm, EMA 0.53-1.80, object 0.57-2.68; maxima hold 1.2-4.8 cm, EMA
7.6-9.5, object 7.0-16.5. Reach ratio 0.99-1.00 and elbow bend 14-17
deg in every window (the arm is nearly straight while it pushes the
cube), so the twist column is singular and the angle p95 of the memory
and object methods runs to 90-180 deg. Reading: on a slow outage
hold-last is bounded by the motion and all three methods keep the wrist
within 1-3 cm median; the object method's advantage over holding
appears only where the arm moves fast during the outage (R5's desk
slide, 50 deg per window: recovered 1.6 cm vs hold 21 cm max), and its
worst frames on R6B come from the straight-arm singularity. Thesis
home: Chapter 7, the rail-recording synthetic-masking subsection.

## E-026 (2026-09-01): live probe re-run on the rail recording; Ch4/5/6/8/9 on the rail

Live probe (v2): make_r5_calib.py gained --alias (writes v2/output/
scene_calibration_r6b_v2.json with the true 45 mm sizes from
scene_calibration_r6bc.json); run_v2.py run twice on the rail bag with
--display-lpf --dump --profile, once with --object-recovery
--plausibility-gate (v2/dataset/r6b_probe_baseline.txt) and once without
(r6b_probe_baseline_off.txt). Result: 900/900 frames, 0 skipped, 31.0 s,
29.0 fps sustained, 929 ticks (cadence p50 33.19 / p99 35.26 ms); landmark
branch total p50 8.40 / p99 13.03 ms (off: 8.03 / 12.64; mediapipe 7.42 /
12.00, solve 0.18 / 0.25 off and 0.41 / 0.58 on); marker branch 14.04 /
16.73 (off: 14.13 / 16.40; detect 13.79 / 16.03); align+publish 2.36;
E-019 live gate rejected 19; object live on 829; obj-recovered right
wrist 147 frames; rec R 625 / L 0; B-A skew p50 -1 p99 -1, 0 stale.
validate_v2_r5.py gained --alias and --one-handed (frame count read from
the reference mask; the left-hand checks are skipped; the angle
comparison uses the right-arm groups on frames where that arm is
measured on both sides, because the live torso repair tags the root on
almost every rail frame, the rail-depth hips again): 10 of 12 checks
pass. The two failures are the angle-tracking bounds: lag 5 frames (bound
4; the minimum is shallow, medians 1.24-1.38 deg over lags 3-7) and worst-
group p95 23.13 deg (bound 20), carried entirely by the shoulder azimuth
(median 16.07 / p95 26.70) because the arm hangs within about 15 deg of
straight down through the slide (elevation -76.57 deg at frame 533),
near the azimuth's undefined configuration; elevation 1.44 / 2.30,
twist 7.28 / 15.68, flexion 0.42 / 1.33 deg over 179 frames. Chapter 8
reports these as they are; the loop run (13/13, lag 3, 0.47 deg) is kept
as one comparison sentence. The R5 v2 dumps (gitignored) were copied
aside before the rail run overwrote v2/output.

Thesis: Ch4 worked example on the rail recording (ch4_numbers.py: scene
frame 533, the one undetected frame 786 bridged then blanked, frame 779
despiked-and-bridged and kept; make_ch4_figs.py on the rail); Ch5 task
wording generalized (no bimanual/stations); Ch6 Unity figure from two
rail captures (run_unity_capture.py --stem R6B; frames 114 and 534 copied
to writing/v7/figures/src/); Ch9 rail-led with a new limitation row for
the steady hip-depth offset. Chapter 7 restructured rail-led (E-025) and
its round-1 review applied. Chapter 1 still says "bimanual" (user).
Unity capture note: the R6B render shows the 32 deg root pitch and the
root shifting with the hip depth; two coherent desk-move frames were used.

## E-027 (2026-09-02): steady-occluder hip gate; rail root stabilised; Unity from the recovery stream

Problem (user, 2026-09-01): the rail-recording Unity render pitched the
trunk by about 32 deg and the root shifted with the hip depth, because
the render was driven by the hold-last angle stream (angles_hold.csv)
and both hip depth samples sit on the rail (0.99 m) for frames ~8-631
while the shoulders read 1.31-1.36 m. The user asked for the root to be
stabilised while the recording keeps its "occlusion-free" label (only
the non-occluded frames are analysed).

Findings:
  - The failure-study detectors (D1-D5, detect_failures.py) do not fire
    on 20-631: both hips agree with each other, nothing jumps.
  - The recovery layer (RobustChainSolver) already repaired the hips on
    891/900 frames: the take begins with the hips on the body (1.22 m,
    frames 0-3), the depth slides to 0.99 m over frames 4-11, the E-011b
    depth-jump gate trips at frame 7 and stays tripped (memory frozen at
    1.213 m). So the repair rested entirely on a memory seeded during the
    first seven frames; a take starting with the pelvis behind the rail
    would have seeded the memory on the rail and passed both E-011b gates.
  - The v1 Unity capture streams only the live mask; every unmeasured
    group is drawn red (held or constrained alike).

Decision: add a third, memory-free torso gate to RobustChainSolver.solve
(v1/kinematics/occlusion_ext.py, lean_tol=0.15 m): a hip more than
lean_tol nearer the camera than the shoulder midpoint is gated after the
E-011b gates, and placed on its ray at the shoulder midpoint's depth
(upright trunk). Tolerance: loop clean-frame hip-minus-shoulder-mid depth
p01 -0.10 / p99 +0.10 m; rail hips on the rail -0.20 to -0.32 m.
Counters occluder_gated / occluder_fixed.

Rejected on the way: (a) a sphere-ray placement using the calibrated
trunk diagonal (near-tangent intersections, ill-conditioned, 29 cm
pelvis swings, 1137 loop frames changed); (b) a per-subject lean
constant (eval/common/subject_calibration.json) - removed, nothing
justified the number. With the gate ordered AFTER E-011b the loop
recording changes on frames 143-145 only (validate_occlusion_ext.py:
ALL PASS after the reorder).

Effect on the rail recording (eval/output/recovery_r6b regenerated):
gate fires on frames 5 (right hip) and 6 (both); depth-jump from 7.
Recovered pelvis 1.213 m; trunk tilt from the wall marker's in-plane up
(T_cam_wall col 1): measured median 24.3 deg (frames 20-631: 28.3, p95
30.7), recovered median 8.0, p95 9.6 deg (a lean over the desk). Rail
synthetic masking regenerated (r6b_recovery_synthetic/moving): pooled
S1 medians hold 3.40 / EMA 0.60 / object 1.33 deg (was 2.51 / 0.60 /
1.34); wrist medians unchanged; maxima fall (EMA 8.61 max, object 14.85
max); arm travel per window 4.0/3.0/6.0/6.0/5.2 deg. Thesis Table 7.4,
7.3.1 prose, 7.4 rail paragraph, Ch5 5.5 third-gate paragraph, Ch3
worked-example sentence, Ch6 figure text, Ch9 row updated.

Unity: run_unity_capture.py --stem R6B --angles-csv
eval/output/recovery_r6b/angles_recovery.csv (899 PNGs); Figure 6.3 now
frames 114 and 700 from the recovery stream. Capture caveat: stale
/dev/shm/integrated_scene_v2 + rt_* files from a v2 probe spawn
IntegratedSceneReceiverV2 and stall the dumper (stuck on one frame); a
stale send_scene_r5.py process did the same. Remove both before a capture.

Open item (not fixed): right-wrist FK-vs-measured on the rail recording
median 7.9 cm, p95 9.5 (check_v1_overlay.py --recovery). Per frame:
114 -> 8.8 cm with calibrated lengths (elbow FK error 0.1 cm), 700 ->
1.1 cm. Cause at 114: elbow bent 14.4 deg, below the 15 deg twist hold
threshold, so the shoulder twist is held (tag_2 = 1) and the forearm's
small bend swings with the stale twist. Calibrated segment lengths on
this take: upper R 0.317 / fore R 0.205 m (loop: 0.256 / 0.252) - the
elbow landmark sits low on the sleeve. Ch6 states the 9 cm at frame 114.

Addendum (2026-09-02, review round 1 of the E-027 spans,
writing/reviews/Chapter_35679_e027_round1.txt, 39 findings applied):
  - Worst FK-wrist frames of every rail masking window (Table 7.4
    maxima) are the FIRST masked frames, both methods, all five windows
    (recovery 14.85/14.52/6.40/6.64/7.60 at +0; direction memory
    8.61/7.86/7.37/6.94/7.33 at +0), decaying ~2 cm/frame under the
    15 deg/frame slew limit; from the eighth masked frame on the max is
    <= 2.55 cm (direction memory) / <= 3.77 cm (recovery). Mechanism:
    the reference twist is HELD (elbow bend 14-17 deg < 15 deg engage),
    the rebuilt arm's geometric twist sits ~80-85 deg away in the
    near-degenerate coordinate, and the slew limit walks twist and
    flexion across; while they travel the hand is off. The old Ch7 text
    blamed the elbow circle, which the 98 percent reach guard switches
    off in these windows. Ch7 7.3.1 rewritten accordingly.
  - Measured trunk tilt over frames 12-631 (after the hip depth settles
    at frame 11): median 28.3, p95 30.7 deg (same as 20-631).
  - Twist hold cost on the rail recording (not applied, user decision):
    FK right-wrist error, plain RobustChainSolver, calibrated lengths:
    hold 15/25 -> median 5.2 cm, p95 6.8 (twist not live 575 frames);
    hold 10/15 -> 0.8 / 4.0 (115 frames); no hold -> 0.8 / 3.3. The
    measured twist through the desk move runs -81 to -32 deg with a
    p95 step of 1.09 deg/frame (no noise to protect against here).
  - Correction (review Chapter_5_torso_round1): the rail hip offset
    (hip z minus shoulder-mid z) over frames 12-631 is -0.20 to -0.36 m
    on the filtered landmark CSV (frame 533: -0.34), not -0.20 to -0.32;
    from frame 632 the left hip returns to the body (-0.06 at frame 700).
    The hip-width calibration (first 60 raw frames) learns the rail:
    median 0.188 m at 0.99 m depth vs 0.167 m on the body (frames 0-3).
    Ch5 5.5.7 states this.

## E-028: audit reruns with explicit pairing and eligibility (2026-09-06)

ID: E-028
Status: SETTLED
Decision: Pair live frame f with offline frame f-k at each candidate lag, requiring validity on both paired samples; archive the exact rerun inputs and preserve historical reports.
Why: The old validator shifted rows and reused a simultaneous-frame validity mask, which can admit an invalid reference and mishandle dropped frames.
Alternatives: Relabelling the old numbers without a rerun leaves the audit unresolved; overwriting historical reports loses provenance.
Evidence: M03 and audit_evidence/evaluation_diagnostic.json; validate_v2_r5.py at 9fa9de4.
Reversibility: Restore the old validator from Git; new reports explicitly identify corrected pairing and their inputs.
Review: Check sparse-frame and validity regression tests and all lag sample counts. Lag search remains -10..10 frames with the existing thresholds; the initial exact-tie change is superseded by E-030 below.

ID: E-029
Status: SETTLED
Decision: Select synthetic windows using the existing harness eligibility and 45-frame duration before computing recovery errors; report every selected window and its unmasked motion.
Why: The historical moving supplement contains overlapping windows and invalid reference frames. The existing eligibility and duration provide a bounded selection rule independent of recovery performance.
Alternatives: Shortening outages or selecting only successful cases after scoring would weaken the comparison; historical exploratory results remain available.
Evidence: M02; harness_recovery.py WIN=45, GUARD=15, MAX_WINDOWS=8 and select_windows; approved recommendation.
Reversibility: New reports are additive. Any alternative duration or motion threshold requires a separate declared study.
Review: Check all eligibility exclusions and overlap counts; if no moving window is available, retain that negative result without retuning.


ID: E-030
Status: SETTLED
Decision: Preserve the historical ascending-lag tie behavior in the M03 correction.
Why: Independent review found that preferring zero lag on an exactly flat signal could turn a historical lag failure into a pass without new timing evidence. The correction now changes pairing only.
Alternatives: A new tie rule is unnecessary for the pairing fix; lag identifiability would require a separate method decision.
Evidence: v2/tests/test_validator_pairing.py flat-signal regression; independent rerun_review finding.
Reversibility: Introduce a separately evaluated lag-identification policy.
Review: Check that all candidate medians and counts remain available, and that the shallow minimum is qualified in the thesis.


ID: E-031
Status: SETTLED
Decision: Unity capture of the rail recovery stream redone 2026-09-07 with two receiver fixes: the held-group spheres are placed along the ray to the camera that renders (HeldMarkers.cs, called by EvalFrameDump before the sensor-view render) and the rig trunk length is the record's pelvis-to-mid-shoulder distance for the recording replayed (IntegratedSceneReceiver.torsoM 0.576 m for R6B; 0.479 was the R5 loop value). The person log now also carries the rig's shoulder and elbow positions.
Why: The spheres, pushed toward Camera.main, projected off the joints in the SensorPOVCamera render (thesis Figures 6.3 and 7.9). With the loop trunk the rig's shoulders sat 10 cm below the measured shoulders on R6B (the corrected pelvis sits deeper than the raw hips) and the reaching right hand fell below the desk slab (world y 0.72) on every frame before about 540, so the arm was invisible.
Alternatives: Segment lengths from the rail calibration (moves the hand by about 1 cm; not adopted, D-005). Anchoring the rig at the shoulders (larger change, not needed).
Evidence: check_unity_log.py on the run: 7 PASS, right hand clean median 41.1 px (was 85.3), de-biased 7.1 px; scratch analysis: rig shoulder minus measured shoulder dy -0.001, dz +0.056 m; rig upper arm 0.1 deg from the measured direction, forearm 24.1 deg (held twist on nearly straight elbow). Capture caveat (in addition to the E-027 note): the dumper never writes the recording's last frame (899 of 900), so use frame 898 as the final-station panel.
Reversibility: Receiver defaults in git history; the capture is a three-minute unattended run.
Review: Rerun check_unity_log.py after any receiver change; compare the rig joints in the person log against the landmarks before choosing figure frames.

Addendum to E-031 (same day): desk marker card drawn over the desk slab (Assets/Shaders/PlateOverlay.shader, ZTest Always, desk plate only). The calibrated card centre is 0.4 cm below the fitted tabletop plane; depth frames put it 0.7 to 2.0 cm above the surrounding desk (frames 500 and 700, along calibrated gravity), the resting cube centre 3.7 cm above the plane. The card pose is 1 to 2 cm low, the plane is right at the cube; the calibration is not changed.

ID: E-032
Status: SETTLED
Decision: Unity capture of the rail recovery stream rerun 2026-09-07 night with trails drawn inside the scene (Unity/Assets/Scripts/TrajectoryTrails.cs, armed by /tmp/r5_trails.txt from writing/v8/condensed/scripts/make_ch7_trails.py): the reference path (static, with waypoint balls), the tracked marker origin and the model right wrist (frame-indexed, drawn up to the applied stream frame), all in display axes under the levelled ArucoWorld node. Receiver settings unchanged from E-031. Output eval/output/unity_check_r6b_trails (ignored by git; the record trails.txt and check_unity_log are copied to eval/reports/unity_check_r6b_trails) (trails.txt, integrated_stream.csv, frames 95, 505, 700, 898, check_unity_log.txt).
Why: Supervisor C36 reading (b) and the user's direction "do it if you can" (D9); thesis Figure 7.10.
Evidence: run_unity_capture.py DONE 899 PNGs for 900 streamed frames; check_unity_log.py on the capture: 7 pass, 1 fail (the left-hand torso-failure concentration check, the same as E-031); right hand clean median 41.1 px, de-biased 7.1 px, hip bone on the mapped pelvis to 0.0007 mm, identical to E-031, so the rig is unchanged; the trails land on the drawn cube and the desk in frames 505, 700 and 898.
Reversibility: Delete /tmp/r5_trails.txt and the script is inert; the capture is a three-minute unattended run.
Review: skill_set/unity-capture-checks.md applies; the rig is unchanged.


ID: E-033
Status: SETTLED
Decision: Presentation stills for thesis Figure 7.10 rendered 2026-09-08 from the saved E-032 stream, not from a new capture: writing/v8/condensed/scripts/render_ch7_trails.py replays eval/output/unity_check_r6b_trails/integrated_stream.csv into the shared-memory scene while the opt-in Unity/Assets/Scripts/Chapter7TrailView.cs (armed by /tmp/ch7_trails_view.json, written from the committed eval/reports/unity_check_r6b_trails/trails.txt) draws the waypoint reference, the marker origin path and the model wrist path under the levelled ArucoWorld node and renders one orthographic still per task interval at the interval's last frame (500, 528, 899; intervals from eval/reports/r6b_waypoints.json track_turns). Stills and capture records in writing/v8/condensed/figures/src/ch7_trails_revision/, with manifest.json (SHA-256 of every artefact and of the view config, written only when every still, record and receiver log was produced after the editor launch) and capture.txt (the editor's capture lines). The accepted run launched 2026-09-08 08:25:13 (the first render of 07:37 was superseded by this rerun through the hardened launcher; same camera, same frames). Receiver, stream and rig unchanged.
Why: The first Figure 7.10 (E-032 sensor-pose trails) was reviewed as unclear (writing/v8/condensed/CH7_TRAILS_REVIEW.md); the user approved a redesign under the constraint that the recording stays unchanged (D-015 to D-019 in writing/v8/condensed/DECISIONS.md).
Evidence: validate_ch7_trails_revision.py: 40 protected source files at their recorded hashes (the .bag, the filtered track, angles_recovery.csv, the calibration, the stream, trails.txt), every exported point equal to trails.txt, the receiver's object and pelvis logs at the three endpoints equal to the stream rows, the figure bytes embedded in both docx files. capture.txt records the three captures at frames 500, 528 and 899; the receiver's object and pelvis logs at those frames equal the stream rows to 1 micrometre.
Reversibility: Delete /tmp/ch7_trails_view.json and the script is inert; the renders take a few minutes with the editor closed. check_unity_log.py was not rerun: the stream, receiver and rig are those of E-032.
Review: skill_set/unity-capture-checks.md; the two capture modes (/tmp/r5_trails.txt for TrajectoryTrails.cs, /tmp/ch7_trails_view.json for Chapter7TrailView.cs) must not be armed together (render_ch7_trails.py refuses).

ID: E-034
Status: SETTLED
Decision: The two-hand rail take recording_20260909_000024 (alias r7, recorded 2026-09-09 00:00 on eval/RECORDING_R7_HANDOVER.md; the seven earlier takes of that night are not used, user direction) is accepted as the handover recording of supervisor round 6 (C50) and enters thesis Chapter 7 as Section 7.7 only. The pinned chain of eval/README.md ran on it with one documented difference: the scene calibration takes its gravity from the r6b calibration (calibrate_scene.py --gravity-from eval/output/scene_calibration_r6bc.json), because the wall card had physically shifted between the takes. Three additive tools carry the analysis: eval/gt/rail_waypoints.py (the E-024 reference-path definition for any rail take; r6b_waypoints.json stays pinned), eval/failure/handover_analysis.py (hand at the cube per frame, the handover interval, the rail error per part of the slide, both forward-kinematics wrists, the states and the failure mask) and eval/failure/compare_hip_hold.py (the study below). The recovery layer gains the opt-in RobustChainSolver(hip_hold=True), the user's proposal of 2026-09-09 ("assume people won't move while handling the object; freeze L24 to its last known value when the hand or the object blocks the depth"): a rejected or unreported hip returns to its last accepted position instead of its ray at the remembered depth. It is validated (validate_occlusion_ext.py section 6b, ALL PASS, default path unchanged) and measured, but NOT adopted for the thesis results.
Why: (1) Acceptance: 1499 frames at 30 fps, a pose on every frame, every torso landmark at 100 percent coverage, the right wrist 99.3 percent with a 0.2 s longest gap, the left 100 percent (check_tracking_precondition.py); the object detected on 1498 of 1499 frames. (2) Gravity: the wall card's centre reads 3.096 m against 3.167 m at the same pixel (119, 153), its plane is tilted 44.1 deg to the sensor axis (r33 -0.718) where it faced the sensor on r6b, and its in-plane up lies 28.07 deg from the r6b gravity; the camera-to-desk pose agrees with r6b within 1.01 deg and 5.5 mm, and the depth-fitted desk plane of r7 agrees with the r6b gravity to 5.85 deg (r6b's own seed agreement 6.2) and with the r6b seed to 0.5 deg. With the wall's up the rail evaluation segmented the whole take as rail (desk and rail levels 1.6 cm apart, perpendicular median 3.28 cm); with the carried gravity the line is 0.09 deg from horizontal, the rail level 4.43 cm above the desk (tape 3.8; r6b 3.97), perpendicular median 0.26 / p95 1.65 / max 3.44 cm over 1072 slide frames and 42.4 cm of travel. The carry-over is a data decision with provenance in the calibration JSON (gravity_carried_over), not a marker-side mechanism (skill_set/marker-simplicity.md). (3) Handover (eval/reports/r7_handover.md): a hand is at the cube when its wrist is within HOLD_RADIUS 0.25 m of the cube centre on a carried frame (the FK wrist stands in where the wrist is not measured); the left hand arrives at frame 864 and the right leaves at 1022 (5.27 s, both at the cube on 159 frames, the cube still on 113 of them), at 29.4 to 34.5 cm along the 42.4 cm slide; parts: right 426-863 travel 29.7 cm, perpendicular 0.71 / 2.10 / 3.44 cm; handover 864-1022 5.3 cm, 0.28 / 1.35 / 1.66; left 1023-1498 7.8 cm, 0.10 / 1.15 / 2.37. The grip state machine keeps both episodes open until the cube rests (right 290-1063, left 864-1080) because the released right hand stays within the 0.35 m release radius, so the analysis uses the hold radius, not the episodes, for the hand at the cube. Failure mask: arm_R none, arm_L 1156-1218 (after the release), torso 651-758, 809-965, 994-1054 (326 frames, 21.8 percent): the hands and the cube in front of the pelvis take the hip depth (hips up to 0.273 / 0.349 m nearer than the shoulder midpoint, left / right; r7_handover.json); the E-011b depth-jump gate trips at 644/648 and the ray repair holds both hips through 1060 (ray_fixed 413 / 408, occluder gate 8 frames, root constrained 417 frames). FK wrist against the measured wrist: right median 0.96 cm, left 1.17 (check_v1_overlay.py --recovery); FK wrist steps above 4 cm only at the torso transitions 644-648, 892-894, 1058-1061 (max 23.2 cm), the root change plus the arm slew limit. (4) Hip hold study (eval/reports/r7_hip_hold.md, r6b_hip_hold.md): over r7 frames 644-1060 the root yaw spread is 98.3 deg raw, 4.59 with the ray repair, 0.13 with the hold; pitch 25.9 / 4.28 / 4.04; pelvis drift 8.85 cm (ray) against 1.4 (hold) while the measured shoulder midpoint drifts 5.77 cm; the FK wrists differ little between the policies except at the transitions. On r6b the hold would change the angles on 895 of 900 frames (the hips are rejected from frame 5 to the end), i.e. every root-dependent thesis number, the Unity captures E-031 to E-033 and the Chapter 5 and 6 worked examples. Adopting it is a thesis-wide decision for the user; the thesis keeps the preparation of Section 2.6 for both recordings, states the assumption and the numbers in Section 7.7 and Section 9.2, and the option stays in the code. User decision (2026-09-09 morning, on the size estimate: six chapters, four Unity captures, both chain reruns, review loops on five chapters, and the remaining weekly usage): keep the preparation for this version; revisit after the usage limit resets only if the supervisor asks for the simpler torso rule or the user still wants it, starting with a numbers-only rerun.
Alternatives: Re-hang the wall card and record again (the take is good on the person side and the user asked for this take only); use the depth-fitted desk plane as gravity (0.89 deg rail tilt and a 7.4 cm rail level, worse than the carried gravity); adopt hip_hold for r7 only (two root policies in one thesis) or for both recordings (every root number changes while the thesis is under review).
Evidence: eval/reports/r7_rail_eval.md/.json/.png, r7_failure_mask.md, r7_handover.md/.json/.csv/.png, r7_hip_hold.md/.json/.png, r6b_hip_hold.md, r7_waypoints.json, r7_marker_scale.json, recording_20260909_000024_inspection.md and _offset_fit.json; eval/output/scene_calibration_r7c.json (gravity_carried_over); the raw wall pose statistics of v1/aruco/output/recording_20260909_000024_aruco_raw.csv against the r6b file; validate_occlusion_ext.py ALL PASS (2026-09-09).
Reversibility: Drop --gravity-from and the chain uses the wall card again; hip_hold defaults to False; the tools are additive; r6b outputs untouched (validate_ch7_trails_revision.py PASS).
Review: Opus code review writing/reviews/r7_code_review_round1.txt (findings applied where accepted, listed in the commit message).

ID: E-035
Status: SETTLED
Decision: Unity capture of the r7 recovery stream (eval/unity_check/run_unity_capture.py --stem recording_20260909_000024 --angles-csv eval/output/recovery_r7/angles_recovery.csv --torso-m 0.517 --out eval/output/unity_check_r7; launched 2026-09-09 00:48:56, 1498 PNGs for 1499 streamed frames) and the presentation render of thesis Figure 7.13 from the saved stream (render_ch7_trails.py --alias r7, launched 00:52:16; Unity/Assets/Scripts/Chapter7TrailView.cs extended with the left model wrist, purple measured / pink rebuilt, grey for a held group; one still per part of the slide at frames 863, 1022 and 1498 from the camera of Figure 7.10; stills, manifest.json and capture.txt in writing/v8/condensed/figures/src/ch7_handover_trails/; records in eval/reports/unity_check_r7/). Trunk length 0.517 m by the E-031 rule (median distance from the recovery pelvis to the measured mid-shoulder on torso-clean frames: 0.5166 on r7, 0.5745 on r6b against the documented 0.576), passed through the opt-in file /tmp/r5_torso_m that IntegratedSceneReceiver.cs reads in Awake when present; the r6b default 0.576 is unchanged.
Why: The trail figure of the handover recording needs the saved stream of a capture, as E-033 did for r6b, and both wrists.
Alternatives: Reuse the r6b trunk length (10 cm shoulders error on this subject's r7 landmarks); edit the C# default per recording (breaks the r6b captures' reproducibility).
Evidence: eval/reports/unity_check_r7/check_unity_log.txt: 7 PASS, 1 FAIL (the loop-era "left hand disagreement concentrated on torso-failure frames" check, 22.1 px torso-only against 23.5 clean: on this take the left hand is tracked throughout, so there is no concentration; the same check fails on E-031/E-032); hip bone on the mapped pelvis to 0.0007 mm; both hands de-biased clean median 8.6 px. The r6b view config regenerates byte-identically and validate_ch7_trails_revision.py passes after the script changes.
Reversibility: Delete /tmp/r5_torso_m and the receiver uses its default; the r7 folders are additive.
Review: Same code review as E-034.

ID: E-036
Status: SETTLED
Decision: Size the Unity avatar per replayed recording from that recording's own landmark geometry, supplied through a side-channel file instead of constants in the receiver. eval/unity_check/make_rig_sizing.py writes eval/reports/<alias>_rig_sizing.json with five lengths: the four arm segments are the offset-fit medians of eval/reports/<stem>_offset_fit.json (segment_lengths_m, the same values the recovery of Chapter 5 uses through eval/failure/recovery_core.py), and the trunk is the E-035 rule made explicit: median distance from the recovery pelvis (pel_x, pel_y, pel_z of eval/output/recovery_<alias>/angles_recovery.csv, y negated into the landmark camera frame) to the mid-shoulder of the filtered landmarks on frames with fail_torso == 0. The launchers write /tmp/r5_rig_sizing (key=value lines: stem, upper_arm_R, forearm_R, upper_arm_L, forearm_L, torso) immediately before the editor starts and remove it afterwards; Unity/Assets/Scripts/IntegratedSceneReceiver.cs reads it in Awake, rejects a file older than 3600 s or missing any key, logs one line naming the stem and the five values, and writes rig_sizing_used.txt beside rig_dimensions.csv. The field defaults upperArmRM, forearmRM, upperArmLM, forearmLM and torsoM are 0 (no scaling) and /tmp/r5_torso_m is no longer read. run_unity_capture.py replaces --torso-m with --sizing (default eval/reports/<alias>_rig_sizing.json), aborts when editor.log reports error CS, and copies unity_person_log.csv, unity_object_log.csv, rig_dimensions.csv and rig_sizing_used.txt into --out. eval/unity_check/check_rig_sizing.py verifies a capture's rig_dimensions.csv against its JSON within 1 mm.
Why: Every earlier capture (E-031 to E-035) applied the loop recording's arm medians 0.256/0.252/0.262/0.247 m to replays whose solver ran on other lengths (rail 0.317/0.205 m), so the rendered-joint errors of thesis Tables 7.3 and 7.4 measured a configuration mismatch on top of the display path. The author's 2026-09-14 rule: the avatar must reproduce the geometry the solver used, which is the landmark geometry of the recording being replayed, not the subject's anatomy.
Alternatives: Keep the loop constants and describe the mismatch (D-043, rejected by the author); size from the subject's tape measurements of about 25 cm per segment (rejected: the solver never saw them); use the offset-fit torso_hip_to_midshoulder (raw hip midpoint) for the trunk (rejected: the rendered pelvis is the recovery pelvis, and that value, 0.599 m on r6b, would raise the shoulders by about 2.5 cm, the E-031 defect); carry the lengths in the shared-memory record (rejected: fixed struct layout, larger change than the side channel).
Evidence: make_rig_sizing.py --self-check reproduces the E-035 values with filtered landmarks: r6b 0.5745 m on 620 torso-clean frames, r7 0.5166 m on 1173 (raw landmarks give 0.5748/0.5165; without the y negation 0.1506/0.2432). The 0.576 m that the E-031 r6b capture used is not reproduced by any variant (closest 0.5745, 1.5 mm off) and its inputs are undocumented; the records carry 0.5745. The loop recording under the same rule is 0.4828 m (raw-hip offset-fit value 0.479 m used by the loop capture); its JSON is recorded with used_by_capture false because the loop capture is not re-run. Arm values written: r6b 0.317/0.205 R, 0.310/0.257 L; r7 0.241/0.233 R, 0.252/0.223 L; r5 0.256/0.252 R, 0.262/0.247 L. Unity batch mode has no headless licence on this machine (exit 198, "No valid Unity Editor license found"), so Assembly-CSharp was compiled with the editor's own Roslyn (Editor/Data/DotNetSdkRoslyn/csc.dll) against the generated Assembly-CSharp.csproj references and defines: 0 errors. check_rig_sizing.py fails on every existing capture by construction (loop constants), and passes on a matching fake rig_dimensions.csv.
Reversibility: Delete /tmp/r5_rig_sizing and the receiver leaves the rig as authored (a warning in editor.log); the JSON records and the checker are additive; restoring the constants means reverting the receiver commit.
Review: The three re-run captures (E-037) must each pass check_rig_sizing.py and check_unity_log.py; writing/v9 verify_ch7_restructured.py must invert its D-043 check ("avatar arm lengths are not the calibrated lengths") and re-pin the receiver hash; thesis Sections 6.3, 7.3 and Chapter 9 describe the per-recording sizing (writing/v9/DECISIONS.md D-113 onward).

ID: E-037
Status: SETTLED
Decision: Re-run the three Unity captures of the thesis with the per-recording sizing of E-036, launched by the orchestrator on 2026-09-14 from the automated launchers (the editor licence resolved on the second attempt; the first attempt died before play mode with "No valid Unity Editor license found" and left no capture). Rail sensor-view: run_unity_capture.py --stem recording_20260831_065553 --angles-csv eval/output/recovery_r6b/angles_recovery.csv --out eval/output/unity_check_r6b_v9 (launched 18:00, 899 PNGs for 900 streamed frames, 969 log rows of which 70 are byte-equal repeats of frames re-streamed by the looping sender); its logs, stream and the stills of frames 95, 114, 505, 700 and 898 are archived under writing/v9/figures/src/r6b_unity_sensor/ and figures/src/r6b_unity_f*.png. Rail presentation: writing/v9/scripts/render_ch7_trails.py --alias r6b (launched 18:05:38; carry 500, lift 528, slide 899; 487 unique frames) into figures/src/ch7_trails_revision/. Handover presentation: --alias r7 (launched 18:06:44; right 863, handover 1022, left 1498; 938 unique frames) into figures/src/ch7_handover_trails/.
Why: Tables 7.3 and 7.4, Figures 6.5, 7.3, 7.4 and 7.5 and the Section 6.4 frame numbers must come from captures whose rig carries the replayed recording's own lengths (author's rule, 2026-09-14). Figure 7.6 is kept from the E-035 sensor-view capture as a demonstration figure (author decision, no fourth capture).
Alternatives: A fourth capture for Figure 7.6 (declined by the author); a matched-frame control re-run of the old configuration (not requested; the comparison is a summary one).
Evidence: check_rig_sizing.py 12 of 12 PASS for each of the three runs (every requested length within 0.00 mm of the rendered rig); every editor log holds one "rig sizing override" line and no "error CS"; check_unity_log.py on the sensor-view run 7 PASS, 1 FAIL (the loop-era left-hand concentration check that fails on every rail capture since E-031). ch6_unity_frames.py on the archived sensor-view log: frame 114 hand to measured wrist 13.3 cm, frame 700 6.6 cm, elbow bends 14.4 and 31.0 degrees reproduced from -Rel_y; log consistency time 5.0e-6 s, pelvis 5.5e-7 m, hip mapping 1.2e-6 m.
Reversibility: The V8 archives remain under writing/v8/condensed/figures/src/; eval/output/unity_check_r6b_v9 is regenerable from the launcher.
Review: evaluate_ch7_restructured.py, evaluate_ch7_bare_model.py and the figure scripts are re-run on these archives; verify_ch7_restructured.py pins are regenerated from the new evidence (D-117).
ID: E-038
Status: SETTLED
Decision: The Unity arm match of Unity/Assets/Scripts/IntegratedSceneReceiver.cs MatchArm() now MOVES the elbow and wrist joints along their bones instead of scaling the bones: fore.localPosition *= upM/rigUp and hand.localPosition *= foreM/rigFore, with localScale left as authored (the old code scaled up.localScale by s1, fore.localScale by (foreM/rigFore)/s1 and divided the hand back out). The joint distances are identical to the scaled rig, because scaling a child's local offset scales its world distance by the same factor under a linear parent map, but the mesh keeps its authored thickness. The field comment on upperArmRM/forearmRM/upperArmLM/forearmLM and the log line were updated to describe the joint translation and to print achieved against wanted lengths. The E-037 rail sensor-view capture was re-run under the new match (run_unity_capture.py --stem recording_20260831_065553 --angles-csv eval/output/recovery_r6b/angles_recovery.csv --out eval/output/unity_check_r6b_v9, launched 2026-09-14 22:13:06 local, finished 22:14:22, 899 PNGs for 900 streamed frames) and its logs, stream and the stills of frames 95, 114, 505, 700 and 898 replaced the E-037 archives under writing/v9/figures/src/r6b_unity_sensor/ and figures/src/r6b_unity_f*.png. Figures 6.5 and 7.5 were regenerated from them; the r6b pins of ch7_visual_examples_sources.json were re-pinned (repin_ch7_visual_examples.py, DECISION constant advanced to E-038, r6b scope unchanged). The presentation captures of Figures 7.3, 7.4, 7.10 and 7.13 were NOT re-run: they are unaffected in joint geometry and the author did not ask for new stills.
Why: The per-recording sizing of E-036 gave the rail recording a 0.205 m forearm against the rig's authored 0.317 m, and the uniform bone scale shrank the forearm mesh with it, so the rendered arm read as abnormally thin in the Figure 6.5 and Figure 7.5 stills. The figures are qualitative illustrations of the display path, so a rendering artefact of the sizing mechanism, not of the reconstruction, had to be removed without changing any measured quantity.
Alternatives: Scale along the bone axis only, leaving the two cross-section axes at 1 (rejected: a non-uniform local scale on a parent bone shears the child once the elbow bends away from the scaled axis, so the forearm mesh would skew through the task instead of only thinning); keep the uniform scale and describe the thin forearm in the caption (rejected: the artefact is avoidable and the caption would spend words on the tool); re-author the rig mesh per recording (rejected: far larger change, and the joint chain is what the thesis measures); leave the rig unsized and describe the mismatch (rejected in E-036 by the author).
Evidence: The launcher aborts on error CS, so the completed run is the compile check; ~/.config/unity3d/Editor.log holds 0 occurrences of "error CS", one "rig sizing override from /tmp/r5_rig_sizing: stem=recording_20260831_065553 upper_arm_R=0.3170 forearm_R=0.2050 upper_arm_L=0.3100 forearm_L=0.2570 torso=0.5745", and the two new match lines "DEF-upper_arm.R: upper 0.233 -> 0.317 m (wanted 0.317), forearm 0.317 -> 0.205 m (wanted 0.205)" and "DEF-upper_arm.L: upper 0.233 -> 0.310 m (wanted 0.310), forearm 0.317 -> 0.257 m (wanted 0.257)", i.e. achieved equals wanted at millimetre print precision. check_rig_sizing.py against eval/reports/r6b_rig_sizing.json: 12 of 12 PASS, every length within 0.00 mm. Joint positions unchanged: ch6_unity_frames.py on the new stream reproduces frame 114 hand to measured wrist 13.3226 cm, elbow to elbow 6.3681 cm, elbow bend 14.3767 deg and frame 700 6.5971 cm, 5.7425 cm, 30.9876 deg, all equal to the E-037 values of writing/v9/audit_evidence/ch6_unity_frames.json at HEAD to every recorded decimal (difference 0.00000 cm against the 0.05 cm tolerance); the only changes in that file are the capture's own bookkeeping (person log 1094 rows and 195 repeated frames re-streamed by the looping sender, against 969 and 70) and the stream hash. Tables 7.3 and 7.4 are unchanged: evaluate_ch7_restructured.py and evaluate_ch7_bare_model.py were re-run for the receiver hash pin and their outputs differ from the previous ones in exactly one leaf each, the IntegratedSceneReceiver.cs sha256, with no numeric change, and writing/v9/CH7_RESTRUCTURED.txt rebuilds byte-identical to HEAD. verify_ch7_restructured.py PASS 1157, FAIL 0; check_style.py 0 hits on Chapters 6 and 7; check_refs.py UNRESOLVED none. The re-pin reported, without changing them, the two pre-existing out-of-scope r7 mismatches (writing/v9/scripts/make_ch7_handover_frames.py and writing/v9/figures/src/ch7_handover_trails/editor.log), which this work did not touch.
Reversibility: The change is three lines of MatchArm; restoring the localScale form reverts to the E-037 rendering, and the capture is regenerable from the launcher in about 80 seconds. The E-037 archives remain in git history; writing/v8/condensed/figures/src/ holds the V8 stills.
Review: Any later capture must keep check_rig_sizing.py at 12 of 12 and the ch6_unity_frames.py frame 114 and 700 distances at 13.32 and 6.60 cm, since those are the published Section 6.4 numbers and the new match must not move a joint. The pinned receiver hash in writing/v9/audit_evidence/ch7_restructured/provenance.json and bare_model.json follows any further edit of that file.

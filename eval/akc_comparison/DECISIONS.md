# eval/akc_comparison decisions

Format follows AGENTS.md (ID, Status, Decision, Why, Alternatives,
Evidence, Reversibility, Review). "Paper" is Kwok, Koenig and Hu,
"Seeing Through Occlusion: Deterministic Arm Kinematic Correction for
Robot Teleoperation", arXiv 2606.19240 (June 2026, no code); section
and equation numbers were read from https://arxiv.org/html/2606.19240
on 2026-09-28. Paper values are SETTLED with the paper as evidence;
every gap the paper leaves open is UNCERTAIN unless it was measured.
Plan: /home/luo/.claude/plans/delegated-juggling-key.md (A1-A7).

ID: AKC-001
Status: SETTLED
Decision: The AKC re-implementation and its comparison live in
eval/akc_comparison/ only; akc.py is pure numpy with no repository
imports; the thesis, the deck, v1, v2, v3 and Video/ are not edited.
Why: author decision of 2026-09-28 (results in eval/akc_comparison
only); a self-contained library keeps the paper method separate from
our pipeline so neither can leak into the other.
Alternatives: placing it under v3/ (rejected: V3 isolation rule and
the author's scope); importing v3/replay/bone_projection.py (rejected:
the library must stand alone; the quadratic is re-derived instead).
Evidence: approved plan, author decisions and A7.
Reversibility: folder move.
Review: git status shows no file outside eval/akc_comparison.

ID: AKC-002
Status: SETTLED
Decision: INTRINSICS = fx 607.561279296875, fy 607.0150756835938,
cx 323.93756103515625, cy 248.0174102783203, 640 x 480, no distortion.
Why: the colour-stream intrinsics of our recordings; the AKC pixel
rules (proximity, ray variant, partial update) need them.
Alternatives: per-recording intrinsics (unnecessary: identical for
every recording per the plan's verified facts).
Evidence: measured; v1/mediapipe/output/recording_20260224_083945_
landmarks_raw.meta.json lines 31-39 (fx, fy, ppx, ppy, zero
coefficients); the plan records the values as identical for every
recording (not re-checked here for all stems).
Reversibility: pass K to every function; all accept a K argument.
Review: M2 should assert the meta JSON of each used stem matches.

ID: AKC-003
Status: SETTLED
Decision: VIS_MIN = 0.7; a landmark with visibility below it loses
both xyz and pixel.
Why: paper value.
Alternatives: our pipeline's 0.5 gate (not the paper's method).
Evidence: paper, Section II-C ("below a predefined threshold (e.g.,
0.7) are rejected").
Reversibility: constant.
Review: none.

ID: AKC-004
Status: SETTLED
Decision: PROX_FRAC = 0.05 of the image width (32 px at 640).
Why: paper value for the proximal-joint depth rule.
Alternatives: none.
Evidence: paper, Section II-C ("e.g., 5% of the image width").
Reversibility: constant.
Review: none.

ID: AKC-005
Status: UNCERTAIN
Decision: Proximity rule details: strict comparison (distance < 32 px
drops the depth); applied only to this arm's elbow and shoulder
against this arm's wrist; only when the wrist pixel passed the
visibility gate; the pixel of the proximal joint is kept; a missing
pixel is filled by projecting xyz (our CSVs carry no pixel columns).
Why: the paper says "within a small neighbourhood" without the
operator; a gated-out wrist has no trustworthy pixel; projection is
the only pixel source for our CSVs.
Alternatives: <= 32 px (differs only at exactly 32.0 px); testing the
other shoulder (the paper names proximal joints of the arm only).
Evidence: none beyond the paper text; test (6) checks 31 px (drop)
and 33 px (keep).
Reversibility: one comparison in occlusion_filter.
Review: whether the author accepts projected pixels as the MediaPipe
pixel stand-in (listed as a limitation).

ID: AKC-006
Status: UNCERTAIN
Decision: A NaN or missing visibility counts as below the gate; an xyz
or pixel with any non-finite component counts as missing.
Why: conservative; a comparison with NaN must not pass the gate.
Alternatives: treating missing visibility as 1.0 (rejected: would let
blank CSV rows through).
Evidence: none (defensive choice).
Reversibility: occlusion_filter and _arr.
Review: none expected.

ID: AKC-007
Status: SETTLED
Decision: Stage 3 is a constant-velocity Kalman filter per landmark,
state [p, pdot], x_k = A x_{k-1} + w_k, z_k = H x_k + v_k,
R = diag(sx^2, sy^2, sz^2) with sz > sx = sy.
Why: paper model.
Alternatives: none.
Evidence: paper, Section II-C, Eq. (1)-(3).
Reversibility: none needed.
Review: none.

ID: AKC-008
Status: SETTLED
Decision: dt = 0.03336 s.
Why: our recordings run at 30 Hz; the paper ran at 10 Hz (Section
III-A) and gives no dt.
Alternatives: per-frame dt from time_s (rejected for the library: the
median is stable and keeps A, Q constant).
Evidence: measured; median diff of time_s in
v1/mediapipe/output/recording_20260224_083945_landmarks_raw.csv is
0.033357 s (this task); plan records 0.03336 s median.
Reversibility: kf dict of AkcArm.
Review: M2 may log per-recording medians.

ID: AKC-009
Status: UNCERTAIN
Decision: Q is white-acceleration per axis, G = [dt^2/2, dt],
Q = sigma_a^2 G G^T, sigma_a = 5.0 m/s^2.
Why: the standard discrete constant-velocity model; 5 m/s^2 is a
priori for hand-scale arm motion. Not tuned on scored windows (A1).
Alternatives: 1, 2.5, 10, 20 m/s^2 (the M2 sweep).
Evidence: none; the paper gives no Q.
Reversibility: kf dict; the sweep reports the effect.
Review: M2 kf_sweep.csv.

ID: AKC-010
Status: UNCERTAIN
Decision: sigma_xy = 0.01 m, sigma_z = 0.05 m (ratio 5).
Why: the paper only states sz >> sx, sy; 1 cm lateral and 5 cm depth
are a priori values for MediaPipe landmarks lifted on RealSense depth.
Alternatives: sigma_xy 5 or 20 mm, ratio 2 or 10 (M2 sweep).
Evidence: none; test (5) confirms the z gain (0.375) is below the x
gain (0.648) at steady state with these values.
Reversibility: kf dict.
Review: M2 kf_sweep.csv.

ID: AKC-011
Status: UNCERTAIN
Decision: Each filter initialises at its first full xyz observation
with zero velocity and P0 = diag(sigma_xy^2, sigma_xy^2, sigma_z^2,
v0_sigma^2 x 3), v0_sigma = 1.0 m/s; before that it returns None and
AKC does not run for the arm. P is symmetrised after every update.
Why: the paper gives no initialisation; the measurement covariance is
the natural position prior; 1 m/s covers arm speeds.
Alternatives: initialising from a pixel only (rejected: no depth).
Evidence: none (a priori); test (5) shows the default filter's
constant-velocity prediction error decays from 2.06 cm to 6e-16 m.
Reversibility: CVKalman.init.
Review: none expected.

ID: AKC-012
Status: SETTLED
Decision: A landmark with no observation takes the Kalman prediction.
Why: paper method ("missing coordinates are estimated by the
prediction").
Alternatives: none.
Evidence: paper, Section II-C.
Reversibility: none needed.
Review: none.

ID: AKC-013
Status: UNCERTAIN
Decision: A landmark whose depth was discarded but whose pixel is
kept updates x, y only: the pixel is deprojected at the predicted
depth and H selects x, y; z stays at the prediction.
Why: the paper keeps the 2-D position and predicts the missing
coordinate; deprojecting at the predicted depth is the only way to
turn a pixel into metric x, y without depth.
Alternatives: dropping the landmark entirely (loses the pixel the
paper says is kept); a pixel-space measurement model (nonlinear EKF,
not in the paper).
Evidence: none beyond the paper text; test (5) checks z equals the
prediction exactly.
Reversibility: CVKalman.step.
Review: none expected.

ID: AKC-014
Status: SETTLED
Decision: EKF variant: h(x) = |p_i - p_j|, H_c = [(p_i - p_j)/|p_i -
p_j|, 0, 0, 0], S = H_c P H_c^T + sigma_l^2, K_c = P H_c^T / S,
x <- x + K_c (l - h(x)), P <- (I - K_c H_c) P.
Why: paper equations.
Alternatives: none.
Evidence: paper, Section II-C, Eq. (4)-(6); sigma_l and the P update
form are ours (AKC-015, AKC-016).
Reversibility: none needed.
Review: none.

ID: AKC-015
Status: UNCERTAIN
Decision: sigma_l = 0.02 m.
Why: a priori, of the order of our measured bone-length spread; not
tuned (A1).
Alternatives: 0.005, 0.05 m (M2 sweep).
Evidence: none.
Reversibility: AkcArm(sigma_l=...).
Review: M2 kf_sweep.csv.

ID: AKC-016
Status: UNCERTAIN
Decision: The EKF constraint runs once per frame after the Kalman
updates: elbow to the Stage-4 wrist p_w with l_f, then shoulder to the
constrained elbow with l_u. It is skipped when |p_i - p_j| <= 1e-12 m
or S <= 0.
Why: the paper does not state the order or the anchor; one update per
frame is the paper's single update. Measured in this task: repeating
the hard update (sigma_l 1e-6) many times with the default
anisotropic P does not converge fast and can jump (length error
4.7 mm after 50 repeats, a 12 m excursion at repeat 5), because P
collapses along the old radial direction while the direction turns;
with isotropic position covariance a single step lands on the sphere.
The 1e-12 guard avoids division by a zero direction.
Alternatives: iterated EKF (not in the paper); shoulder first.
Evidence: scratch runs in this task; test (7).
Reversibility: AkcArm.step.
Review: whether M2 EKF numbers are reasonable at sigma_l 0.02.
Annotation (2026-09-28): the elbow anchor is superseded by AKC-056: the
constraint now ties the elbow to the Stage-3 (Kalman) wrist; the p_w
anchor described here is AkcArm(ekf_anchor="raw"). Order, the single
update per frame and the guards are unchanged.

ID: AKC-017
Status: SETTLED
Decision: Stage 4 keeps the wrist; elbow and shoulder depth from
p_e,z = p_w,z +/- sqrt(l_f'^2 - dx^2 - dy^2) and p_s,z = p_e,z +/-
sqrt(l_u'^2 - dx^2 - dy^2), two elbow candidates and two shoulder
candidates per elbow (four configurations); l' = s l during the
search only; a negative radicand falls back to p = anchor + unit(p -
anchor) l with the unscaled length.
Why: paper method ("literal" mode).
Alternatives: none.
Evidence: paper, Section II-D1 Eq. (7)-(9), Section II-D2 (shrink).
Reversibility: none needed.
Review: none.
Annotation (2026-09-28): the output side of "l' during the search only"
is fixed by AKC-053: the chosen branch is output by the same relation
at the unscaled lengths; the search and the fallback are unchanged.

ID: AKC-018
Status: UNCERTAIN
Decision: A second geometry, "ray" mode (library default): the
candidate lies on the camera ray of the landmark pixel (or of the
reference when no pixel is kept), at the roots of that ray with the
sphere of radius l' about the anchor; no root falls back as in
AKC-017.
Why: the literal form fixes x, y in metres, which moves with the depth
used to lift the pixel; the ray form keeps the pixel exactly (plan
A2). Same quadratic as v3/replay/bone_projection.py:43-60 (read, not
imported), but both positive roots are kept as candidates.
Alternatives: literal only (kept as mode "literal" for fidelity).
Evidence: test (2): both modes exact when the reference depth is
true; test (2) literal with x, y lifted at a wrong depth errs 0.25 /
0.49 / 1.22 / 2.44 cm for 1 / 2 / 5 / 10 cm depth error on the
synthetic frame 50.
Reversibility: AkcArm(mode=...).
Review: M2 reports both modes.

ID: AKC-019
Status: UNCERTAIN
Decision: In literal mode with a kept pixel, the reference x, y are
the pixel deprojected at the reference (Kalman) depth; the fallback
direction uses that adjusted reference (literal) or the Kalman
reference (ray).
Why: the paper fixes x, y from the landmark, and its 2-D position is
the pixel; the reference depth is the only depth available.
Alternatives: x, y straight from the Kalman estimate (ignores the kept
pixel).
Evidence: none beyond the paper text; the sensitivity is quantified in
AKC-018.
Reversibility: akc._candidates.
Review: none expected.

ID: AKC-020
Status: SETTLED
Decision: W_a = (w1 0, w2 8, w3 18, s 1.0), W_b = (0, 14, 12, 0.8),
W_c = (1, 19, 20, 0.9); w4 = w5 = 100 for every set; W_c is the
library default.
Why: paper values; W_c is the paper's final set.
Alternatives: none.
Evidence: paper, Section III-E (weight sets), Section II-D2
("w4=w5=100.0").
Reversibility: constants.
Review: none.

ID: AKC-021
Status: UNCERTAIN
Decision: Stage-4 wrist p_w = the measured (unfiltered) wrist xyz,
else wrist_override (our object-derived wrist for the hybrid), else
the wrist Kalman prediction.
Why: the paper keeps the wrist; with no wrist measurement it gives no
rule, and the plan's P2 protocols need both substitutes.
Alternatives: using the filtered wrist always (not "kept").
Evidence: none beyond the paper text and plan A5/P2.
Reversibility: AkcArm.step.
Review: M2 P2a/P2b rows name the wrist source.
Annotation (2026-09-28): p_w is still the Stage-4 wrist for the
correction; since AKC-056 it is no longer the anchor of the EKF length
constraint (the Stage-3 Kalman wrist is), except in
AkcArm(ekf_anchor="raw").

ID: AKC-022
Status: UNCERTAIN
Decision: m5 penalty k = 100.
Why: the paper gives no value; with w5 = 100 the term adds 10^4,
which dominates every distance term in metres, so m5 acts as a hard
veto, matching the paper's stated purpose of eliminating implausible
candidates.
Alternatives: k = 1 (soft in metres).
Evidence: none; paper Section II-D2 Eq. (15) leaves k open.
Reversibility: AkcWeights(k=...).
Review: none expected.

ID: AKC-023
Status: UNCERTAIN
Decision: theta = unsigned angle at the elbow between (s - e) and
(w - e), in degrees; m5 = k when theta < 40 or theta > 180 (bounds
inclusive), and when theta is undefined (degenerate geometry).
Why: the paper gives only the range and does not define theta. An
unsigned angle between two vectors lies in [0, 180], so the paper's
"theta > 180" (hyper-extension) cannot be detected; only over-flexion
(theta < 40) is penalised. A signed angle would need a reference
plane the paper does not give.
Alternatives: a signed angle against the shoulder-line plane (a new
invention).
Evidence: none; paper Section II-D2 ("theta<40 and theta>180"); test
(3) shows the 30-degree configuration rejected and a straight arm
(180 degrees) accepted.
Reversibility: akc.elbow_angle_deg.
Review: author to confirm or supply the paper's convention.

ID: AKC-024
Status: UNCERTAIN
Decision: The correction runs every frame (always_correct=True); the
option False runs it only when the elbow or shoulder lacks a full xyz.
Why: the paper does not say; running every frame is the simplest
reading of "Stage 4" as a pipeline stage (plan A1).
Alternatives: only on occlusion (M2 sweep row).
Evidence: none.
Reversibility: AkcArm(always_correct=...).
Review: M2 kf_sweep.csv.

ID: AKC-025
Status: UNCERTAIN
Decision: No feedback of the AKC output into the Kalman filters by
default; the option feedback=True applies an extra update_xyz with the
chosen elbow and shoulder.
Why: the paper describes Stage 4 after Stage 3 with no loop back.
Alternatives: feedback (M2 sweep row).
Evidence: none; paper silent.
Reversibility: AkcArm(feedback=...).
Review: M2 kf_sweep.csv.
Annotation (2026-09-28): with the full-length output of AKC-053 the
feedback row is 1.00 cm R-self (M2 0.64 cm); the divergence seen under
the first, radial-rescale version of AKC-053 is gone (AKC-053
Evidence).

ID: AKC-026
Status: UNCERTAIN
Decision: m3 = 0 when there is no previous output (first corrected
frame); the previous output is the last emitted elbow and shoulder
(AKC or Kalman).
Why: the paper defines m3 against the previous frame only.
Alternatives: using the Kalman prediction as "previous".
Evidence: none.
Reversibility: akc.cost.
Review: none expected.
Annotation (2026-09-28): "previous output" is refined by AKC-054: on
corrected frames m3 compares with the previous search-time choice (at
l' = s l), not with the full-length output of AKC-053.

ID: AKC-027
Status: UNCERTAIN
Decision: m4 = 0 when the other shoulder is unavailable; the other
shoulder is filtered by its own Kalman filter inside the arm when
given as an Obs, or used as is when given as an xyz.
Why: m4 needs the other shoulder; a single-arm run (or the other
shoulder never seen) must still select.
Alternatives: skipping AKC for that frame.
Evidence: none.
Reversibility: AkcArm.step, akc.cost.
Review: M2 should state which source feeds m4.

ID: AKC-028
Status: UNCERTAIN
Decision: Every cost term in metres.
Why: our pipeline is in metres. The paper does not state the unit
(its result tables use centimetres). m1 to m4 scale together, so their
argmin is unit-free; only the fixed m5 term (k w5) changes weight
relative to the distances, and it dominates in either unit.
Alternatives: centimetres.
Evidence: none; paper silent.
Reversibility: a unit factor in akc.cost.
Review: none expected.

ID: AKC-029
Status: UNCERTAIN
Decision: Numerics: ties keep the first configuration in enumeration
order (elbow roots ascending, then shoulder roots ascending); a
tangent ray gives one candidate; no correction when p_w or either
reference is missing (the Kalman estimates are emitted); P is
symmetrised after each update.
Why: determinism and graceful degradation; exact ties do not occur on
real data.
Alternatives: none considered material.
Evidence: test (8) bit-identical reruns.
Reversibility: akc_correct, AkcArm.step.
Review: none expected.

ID: AKC-030
Status: UNCERTAIN
Decision: Arm lengths l_f, l_u, l_s are inputs to AkcArm; M2 takes
them from eval/reports/<stem>_offset_fit.json segment_lengths_m, the
same values our method uses.
Why: the paper calibrates in a T-pose over 100 frames (Section III);
our recordings have no T-pose (plan A3).
Alternatives: first-N-frame medians (not the paper's either).
Evidence: plan A3; paper T-pose statement.
Reversibility: M2 run script.
Review: M2 run_info.json lists the lengths used.

ID: AKC-031
Status: UNCERTAIN
Decision: Test fixture constants in test_akc.py: synthetic curves
u(t) = unit(0.25 + 0.10 sin(2 pi 0.5 t), 0.45 + 0.10 cos(2 pi 0.4 t),
-0.85 + 0.25 sin(2 pi 0.8 t)), f(t) = unit(0.05 + 0.10 sin(2 pi 0.7 t),
-0.20 + 0.15 sin(2 pi 0.6 t), -0.95); other shoulder (-0.21, -0.10,
1.07) m (l_s 0.361 m); measurement noise 0.5 px pixel and 5 mm depth
(seed 0); mask frames 100-119 (20 frames, pixel kept).
Why: the arm reaches toward the camera so the elbow and shoulder
roots are well separated (the brief's >= 10 cm condition holds on all
200 frames) and the elbow depth accelerates enough for a constant-
velocity prediction to drift over 20 frames; the noise levels are
a priori RealSense/MediaPipe magnitudes. Shoulder (0.15, -0.10, 1.05),
l_u 0.25, l_f 0.23, 2 cm reference noise and the 1e-9 / 1e-12 / 1e-6 /
1 cm tolerances come from the M1 brief.
Alternatives: none tried.
Evidence: test output (all PASS).
Reversibility: test-only.
Review: none expected.
Annotation (2026-09-28): the arm-pointing-away fixture and the other
constants added after the code review are AKC-057.

ID: AKC-032
Status: UNCERTAIN
Decision: Four test checks read the M1 brief narrowly where the literal
wording cannot hold: (a) the constant-velocity exactness check uses
sigma_a = 0 and sigma 1e-9 (with sigma_a > 0 or finite R the
estimate is shrunk toward the zero-velocity prior and is only
asymptotically exact; the default filter's decay is a separate check);
(b) the EKF convergence check uses isotropic position covariance
(AKC-016); (c) the masked-frame elbow criterion is the median < 1 cm
plus max <= max raw wrist error + 1 mm (max was 1.20 cm, equal to the
kept raw wrist error, since AKC keeps the wrist); (d) the m5 check uses
over-flexion (AKC-023).
Why: each literal reading fails for a reason that is a property of the
specified method, not a defect.
Alternatives: lowering the fixture noise until max < 1 cm (rejected:
tunes the fixture to the threshold).
Evidence: first test run: EKF 4.7e-03 after 50 repeats; masked max
1.20 cm with wrist max 1.20 cm.
Reversibility: test-only.
Review: master to accept or ask for the literal criteria.

## M2: experiments (run_akc_comparison.py, 2026-09-28)

ID: AKC-033
Status: SETTLED
Decision: P1 and P2a reuse the three Chapter 7 windows on the r7 right
arm (490-534, 445-489, 557-601, 45 frames each), read from
writing/v9/audit_evidence/ch7_restructured/synthetic.json and asserted.
Why: the windows were selected by the thesis protocol before any masked
run; reusing them keeps our pinned numbers as a regression target and
avoids selecting windows on AKC results.
Alternatives: new windows chosen for this comparison (rejected: a new
selection could favour either method and loses the regression).
Evidence: chapter7_windows() assert; P2a regression, abs diff 0.0 on
all 18 pinned medians (results/run_info.json, asserts).
Reversibility: change chapter7_windows(); every P1/P2a row changes.
Review: none expected.

ID: AKC-034
Status: UNCERTAIN
Decision: Two references per row. R-self (primary): the method's own
unmasked output (AKC: the unmasked run of the same configuration;
KF-only: the unmasked AKC-ray Kalman estimate; ours: the unmasked
plain-solve FK joint, the Chapter 7 protocol). R-meas (secondary): the
unmasked filtered landmark, camera frame.
Why: without Vicon there is no ground truth; R-self measures how well a
method reproduces what it would have output without the occlusion
(their protocol measures against Vicon, ours against R-self), R-meas
puts all methods on one common reference.
Alternatives: raw landmark as R-meas (rejected: noisier than both
outputs); R-meas only (rejected: loses the Chapter 7 protocol).
Evidence: none beyond the protocol text; plan A6.
Reversibility: reference columns only.
Review: whether R-self is the right primary for AKC, whose unmasked
output is itself 2.6 cm from R-meas at the elbow (p1 mask none rows).

ID: AKC-035
Status: SETTLED
Decision: Mask injection. AKC: inside the window the masked landmark is
Obs(None, None, vis 0) (MASK_ALL); runs are causal over the whole
recording from frame 0. Ours: the landmark columns are nulled in a copy
of inputs["lm_df"] after build_inputs without extra_fail, then
run_variant "masked" (ours-memory) and "recovery" (ours-IK); P2a uses
harness_recovery.masked_inputs(..., "S1_arm") unchanged.
Why: extra_fail drops elbow and wrist together (solver_points), so an
elbow-only mask must bypass it; nulling after build_inputs keeps the
object-derived wrist and grip fit untouched.
Alternatives: extra_fail (rejected: removes the wrist as well).
Evidence: asserts in run_info.json: in every M-E window the solver's
recovered right_elbow count grows by exactly 45 for both variants, the
post-recovery right wrist is identical to the unmasked run, and
w_hat_solver is identical before and after nulling.
Reversibility: null_lm() only.
Review: none expected.

ID: AKC-036
Status: UNCERTAIN
Decision: Pearson r per axis is NaN when the reference std over the
scored frames is below 1 mm, or when the prediction is constant on that
axis (hold-last).
Why: r is undefined for a constant series and meaningless for a
reference that does not move beyond sensor noise.
Alternatives: report r always (rejected: produces 0 or noise values).
Evidence: 1 mm is the brief's value (plan A6); no measurement.
Reversibility: PEARSON_MIN_STD_M.
Review: the threshold.

ID: AKC-037
Status: UNCERTAIN
Decision: "pooled" rows recompute every metric from the concatenated
per-frame errors of the three windows (n = 135); Pearson is NaN on
pooled rows.
Why: medians and RMSE do not average across windows; a pooled r would
measure between-window position offsets, not tracking.
Alternatives: mean of window statistics (rejected, see above).
Evidence: none; convention.
Reversibility: pooled_p1().
Review: none expected.

ID: AKC-038
Status: SETTLED
Decision: MASK_Z (pixel kept, depth dropped) runs for AKC only; the
kept pixel is the projection of the unmasked xyz (AKC-005), visibility
kept. Ours has no pixel input and gets MASK_ALL only.
Why: MASK_Z is their depth-occlusion case; stating it as extra
information for AKC keeps the comparison honest.
Alternatives: none; brief.
Evidence: finding: in ray mode the MASK_Z elbow equals the unmasked AKC
elbow exactly (R-self error 0.000 cm on all 135 frames), because with
always_correct the ray-mode output never uses the measured depth except
to rank the two roots.
Reversibility: n/a.
Review: read MASK_Z ray rows as "no loss", not as accuracy.

ID: AKC-039
Status: UNCERTAIN
Decision: hold-last. P1: the reference value at frame a-1 held over the
window, scored against the same reference (R-self row holds ours plain
FK, R-meas row holds the filtered landmark). P2a: run_hold_baseline
(ChainFallbackSolver), the Chapter 7 baseline.
Why: P1 masks only the elbow (and shoulder), a case ChainFallbackSolver
was not designed or pinned for; the held reference is the zero-model
baseline for any reference. P2a must reproduce Chapter 7.
Alternatives: ChainFallbackSolver in P1 too (rejected: not pinned for
elbow-only masks).
Evidence: P2a hold-last medians equal synthetic.json (abs diff 0.0).
Reversibility: hold() and p1().
Review: the P1 definition.

ID: AKC-040
Status: SETTLED
Decision: Outage sweep: M-E MASK_ALL on r7 right, windows [445,
445 + d - 1] for d in harness_recovery.DURATIONS (15 .. 90), methods
KF-only, AKC-ray, ours-memory, ours-IK, both references.
Why: 445 starts a Chapter 7 window; 445-534 is two adjacent clean
Chapter 7 windows, so every duration stays on clean frames. The
durations bracket our 45-frame memory horizon.
Alternatives: other anchors (rejected: not pre-selected).
Evidence: synthetic_selection.json; harness_recovery.py:104.
Reversibility: OUTAGE_ANCHOR.
Review: none expected.

ID: AKC-041
Status: SETTLED
Decision: Errors in cm; median, p95 with numpy method "linear", max,
RMSE per axis and 3-D (sqrt of mean squared 3-D error).
Why: the Chapter 7 stats() uses the same percentile method.
Alternatives: none.
Evidence: evaluate_ch7_restructured.py stats().
Reversibility: metrics().
Review: none expected.

ID: AKC-042
Status: SETTLED
Decision: All comparisons in the camera frame; solver-space points
(ours FK, w_hat_solver) are converted by multiplying y by -1; label
xyz_cam is camera frame already.
Why: root_frame.unity_from_sensor is exactly (x, -y, z); norms are
invariant, so the P2a regression (computed in solver space in Chapter 7)
is unaffected.
Alternatives: none.
Evidence: v1/kinematics/root_frame.py:12-14; P2a regression abs diff 0.
Reversibility: FLIP.
Review: none expected.

ID: AKC-043
Status: UNCERTAIN
Decision: Ours shoulder for FK: the unmasked filtered shoulder (Chapter
7 synthetic()), except on frames where the shoulder itself is masked
(M-ES), where the solver's post-recovery shoulder (last_points, read by
a subclass that only records it) is used.
Why: using the true shoulder on masked frames would feed ours the
information the mask removed.
Alternatives: filtered shoulder everywhere (rejected, leak).
Evidence: the subclass changes no result: P2a medians equal
synthetic.json with abs diff 0.0.
Reversibility: ours_points(sh_override).
Review: none expected.

ID: AKC-044
Status: UNCERTAIN
Decision: Sensitivity sweep, one parameter at a time from the committed
defaults (AKC-009, AKC-010, AKC-015), in the order sigma_a, sigma_xy
(ratio 5 kept), sigma_z/sigma_xy ratio (sigma_xy 0.01), sigma_l (EKF
rows), weights W_A/W_B/W_C, always_correct, feedback, mode, filtered
input; score = pooled median 3-D elbow error over the three P1 windows
(M-E MASK_ALL), R-self and R-meas. Reported only; the defaults are not
changed. The plan's "fallback" item is not swept: akc.py has no switch
for it.
Why: tuning on the scored windows would bias the comparison.
Alternatives: grid search (rejected: same bias, more rows).
Evidence: results/kf_sweep.csv. The EKF rows degrade sharply as sigma_l
tightens (R-self median 12.6 / 5.8 / 1.8 cm at 0.005 / 0.02 / 0.05 m),
not investigated further.
Reversibility: n/a (reporting only).
Review: the EKF behaviour under long masks (candidate for the M3
review of akc.py).
Annotation (2026-09-28): row output_shrunk=True added (AKC-053); the
EKF medians above are the M2 values, see results/kf_sweep.csv for the
current ones.
Annotation (2026-09-28, M3): the EKF degradation above was traced to
the constraint anchor (AKC-056). With the Stage-3 wrist anchor the
sigma_l rows are 3.26 / 1.58 / 1.25 cm R-self at 0.005 / 0.02 / 0.05 m;
the M2 anchor is the new row ekf_anchor=raw (5.12 cm at 0.02 m).

ID: AKC-045
Status: SETTLED
Decision: Output layout: results/*.csv written with float format %.6f
and LF line endings, run_info.json with sorted keys and no wall-clock
field, PNGs without software metadata; timing.csv is the only file that
changes between reruns. Per-frame tracks go to
eval/output/akc_comparison/tracks_<alias>_<exp>_<method>.csv
(gitignored); --quick writes run_info_quick.json there instead of
overwriting results/run_info.json.
Why: byte-identical reruns are the house check.
Alternatives: none.
Evidence: two full runs: sha256 identical for every results file except
timing.csv.
Reversibility: n/a.
Review: none expected.

ID: AKC-046
Status: UNCERTAIN
Decision: Timing: time.perf_counter around AkcArm.step only (not the
occlusion filter or CSV access), mean and p95 per frame on the unmasked
r7 right run; ours = run_variant wall time / n, which includes pandas
iterrows, the recording subclass and both arms.
Why: brief. The two numbers are not like for like (one arm vs both
arms and the whole body chain) and are machine-dependent.
Alternatives: none.
Evidence: results/timing.csv (single run on this workstation).
Reversibility: n/a.
Review: do not quote as a speed comparison without these caveats.

ID: AKC-047
Status: UNCERTAIN
Decision: r5 natural right-elbow-only frames: elbow xyz missing or vis
< 0.7 while the wrist has finite xyz and vis >= 0.7, in the 0.5-gated
raw CSV: 91 frames.
Why: that is the set where AKC's gate drops the elbow and keeps the
wrist, i.e. its intended use case.
Alternatives: the plan's count of 82 (definition not recorded; not
reproduced).
Evidence: run_info.json asserts r5_right_elbow_only_frames = 91.
Reversibility: r5_elbow_only_frames().
Review: whether 82 came from another definition.

ID: AKC-048
Status: UNCERTAIN
Decision: P2b AKC runs, causal over all of r5, both arms: on the vis0
CSV (only AKC's 0.7 gate) and on the 0.5-gated raw CSV; four rows each:
AKC-ray (gate only, KF-predicted wrist when the gate drops it),
AKC-hybrid (our object-derived wrist as wrist_override, used only when
the gate drops the wrist), and the "-fm" versions of both with our
failure mask applied to AKC's input (elbow and wrist removed on failed
frames), so that a present but wrong wrist is not kept.
Why: AKC keeps any wrist that passes its gate; our method removes the
wrists that the failure detectors flag. The -fm rows separate the two
effects.
Alternatives: gate-only rows (rejected: mixes detection and recovery).
Evidence: the vis0 and raw tracks are byte-identical for both arms
(cmp), so the 0.7 gate makes the two inputs equivalent; the AKC-hybrid-fm
wrist equals ours "recovered" on every override frame (asserted, 2 dp).
Reversibility: p2b().
Review: which AKC row is the fair one to quote.

ID: AKC-049
Status: SETTLED
Decision: P2b ours numbers are recomputed from the pinned angle CSVs
(eval/output/recovery_r5/angles_*.csv) exactly as
eval/failure/eval_labeled_recovery.py does and asserted equal, per frame
and 2 dp, to eval/reports/r5_recovery_labeled.json; the summary rows are
copied from that file and asserted equal to natural.json.
Why: the brief's regression target; recomputation proves the FK and the
frame conversion.
Alternatives: copy only (rejected: no check).
Evidence: 162 per-frame values equal; summaries equal.
Reversibility: n/a.
Review: none expected.

ID: AKC-050
Status: UNCERTAIN
Decision: P2a AKC rows: S1_arm (elbow and wrist Obs(None, None)) on the
raw CSV; AKC-ray uses the Kalman-predicted wrist, AKC-hybrid uses the
masked-input object-derived wrist (the one ours-object uses, grip offset
refitted with the window excluded) in the camera frame. AKC R-self is
the unmasked AKC-ray output (its wrist R-self is the measured raw
wrist, which differs from ours R-self, the plain FK wrist).
Why: brief; same masked information for every method.
Alternatives: none.
Evidence: wrist source asserted kf_pred / override on every masked
frame; AKC-hybrid and ours-object wrist R-meas errors are identical
(same wrist), the R-self errors differ only through the reference.
Reversibility: p2a().
Review: compare the hybrid with ours-object on R-meas, not R-self.

ID: AKC-051
Status: UNCERTAIN
Decision: Sanity check "unmasked AKC forearm range on r7 inside the raw
p5-p95 band" FAILS and is reported, not waived: AKC-ray forearm 20.97 to
23.30 cm, raw band 21.09 to 25.22 cm.
Why: akc.py places every feasible candidate at l' = s l (s = 0.9 for
W_C, AKC-020) and falls back to the unscaled l (Eq. 9), so the output
forearm is 0.9 x 23.3 = 20.97 cm on most frames, below the raw p5.
The same shrink explains the unmasked AKC-ray offsets from R-meas
(elbow 2.6 cm, shoulder 5.5 cm pooled; ray mode moves the joint along
its camera ray to meet the shorter length).
Alternatives: apply the shrink only to the feasibility test and output
at the full length (not done: changes the M1 library reading of the
paper, a methodological choice for the master/author).
Evidence: results/arm_length_range.csv; run_info.json asserts
sanity_r7_forearm_band; kf_sweep W_A (s = 1.0) R-meas median 1.65 cm vs
W_C 2.58 cm.
Reversibility: akc._candidates length choice; all AKC rows change.
Review: HIGH. Decide whether the paper's shrink applies to the output.
Annotation (2026-09-28): superseded by AKC-053 (master decision, author
to confirm): the chosen branch is re-solved at the unscaled lengths.
The sanity check now holds (AKC-ray forearm 23.30 cm on every r7
frame, inside 21.09-25.22 cm); the M2 behaviour is the kf_sweep row
output_shrunk=True.

ID: AKC-052
Status: SETTLED
Decision: r6b left arm: AKC and KF-only produce no output (n = 0 rows
kept): the left wrist never passes the 0.7 gate (max vis 0.578 in the
raw CSV), so its filter never initialises.
Why: property of the recording and of the paper's gate.
Alternatives: none.
Evidence: raw CSV counts (left wrist: 0 frames with vis >= 0.7).
Reversibility: n/a.
Review: none expected.

ID: AKC-053
Status: UNCERTAIN
Decision: The branch (root sign or ray-root order) of elbow and
shoulder is chosen by the candidate search at l' = s l exactly as
before (candidates, cost on the search-time candidates, argmin, Eq. 9
fallback); the chosen branch is then re-solved with the paper's own
relation at the unscaled length. Literal: p_e = (x, y of the search
candidate, p_w,z + sign_chosen sqrt(l_f^2 - dx^2 - dy^2)), then the
shoulder likewise with its chosen sign at l_u about that elbow. Ray:
the root of the same index on the same pixel ray at radius l_f about
the wrist, then the shoulder root of the same index at l_u about that
elbow. When such a solve has no root or a different root count than
the search (not expected: the radicand only grows with the length),
the joint falls back to a radial rescale, anchor + unit(cand - anchor)
l (AKC-055), and the fallback is counted. A joint that already fell
back at search time keeps its Eq. 9 point (unscaled length).
AkcArm(output_shrunk=True) keeps the M2 behaviour (output the
search-time points).
Amended 2026-09-28 (master decision): the first version of this entry,
the same day, output the radial rescale p_e = p_w + unit(e' - p_w) l_f
for every frame; it was replaced by the re-solve above because the
radial rescale leaves the pixel ray and is not exact on perfect input
(first-version evidence kept below). The radial rescale now serves only
as the counted fallback.
Why: master decision (2026-09-28, author to confirm). The paper reduces
the preset length "during candidate search" to stabilise the depth
solutions and reports zero arm-length variation (Table VI). The shrunk
output is also constant on feasible frames, but at s l instead of the
calibrated l; its M2 forearm range of 2.33 cm on r7 (AKC-051) came
from mixing Eq. 9 fallback frames, output at the unscaled l, with
feasible frames at s l.
Re-solving with the paper's own formula keeps the pixel (ray) or the
x, y (literal) and the chosen branch. Elbow first, shoulder about the
output elbow, so |p_e - p_w| = l_f and |p_s - p_e| = l_u hold exactly.
The cost stays on the search-time candidates (paper: cost on the
candidates).
Alternatives: (a) shrunk output (M2, kept as output_shrunk=True);
(b) radial rescale for every frame (first version, rejected: not exact
on perfect input, and the feedback row diverged under it); (c) cost on
the full-length chains (checked, changes no output).
Evidence: test_akc.py (2): with true references, pixels and wrist the
W_c (s = 0.9) and W_b (s = 0.8) outputs recover elbow and shoulder
exactly (max error 1.1e-15 m ray, 2.3e-16 m literal, < 1e-9) with 0
radial fallbacks. (2b): with s = 0.8 and 2 cm reference noise the
output lengths equal l_f and l_u to 1e-15 m, output_shrunk=True
returns the search-time points (s l to 8.3e-16 m), and the search-time
argmin and cost are identical with and without output_shrunk. (4): a
constructed ray case whose shoulder root count drops from 2 to 1 at
full length takes the radial fallback and is flagged.
Full run (results/run_info.json asserts
akc_full_length_rescale_fallbacks): 0 elbow and 0 shoulder radial
fallbacks over 181 AKC runs and 269758 corrected frames.
Cost on full-length chains vs on search-time candidates (scratch replay
of the test (3) and test (8) scenarios, W_a/W_b/W_c, ray and literal,
2400 frames): the output chain is identical in every frame.
Run versus M2 (scratch replay of 382 AKC runs: every KF sweep setting,
P1 windows with M-E / M-ES and MASK_ALL / MASK_Z, r5 / r6b / r7 both
arms): the search-time points equal the M2 output in every frame of
every run except the feedback=True runs, whose Kalman filters are fed
the full-length output.
r7 results: unmasked AKC-ray vs R-meas 0.55 cm elbow, 1.77 cm shoulder
(M2 2.62 / 5.47 cm); P1 M-E MASK_ALL pooled AKC-ray median 1.20 cm
R-self, 1.65 cm R-meas (M2 1.23 / 2.58 cm); the feedback=True sweep row
is 1.00 / 1.29 cm. W_a, W_b and W_c give the same kf_sweep numbers
because the scored elbow is identical across the three sets inside the
three windows (0 of 45 frames differ per window, masked and unmasked);
their shoulders and frames outside the windows differ (e.g. 365 of
1485 unmasked r7 frames between W_a and W_c).
First-version evidence (radial rescale, superseded): perfect-input W_c
elbow error median 1.08 cm (ray) / 0.56 cm (literal); unmasked AKC-ray
vs R-meas 1.88 / 2.15 cm; feedback=True row 24.29 cm R-self, the
masked elbow drifting toward the camera by 9.7 to 22.1 cm in 45 frames.
Reversibility: AkcArm(output_shrunk=True) or akc_correct(...,
output_shrunk=True); every AKC row changes back.
Review: HIGH. Author to confirm the reading.
Annotation (2026-09-28, M3 code review): the Why above was reworded;
it first read "reports zero arm-length variation (Table VI), which the
shrunk output cannot give (M2: 2.33 cm forearm range on r7, AKC-051)",
which overstated: the shrunk output is constant (s l) on feasible
frames, and the range came from the Eq. 9 fallback frames at l.

ID: AKC-054
Status: UNCERTAIN
Decision: The temporal term m3 compares each search-time candidate with
the previous frame's search-time choice (not with the full-length
output); frames without a correction carry the Kalman estimate as
before.
Why: keeps the candidate search identical to the paper-literal search
(and to output_shrunk=True): both sides of m3 are at l', so m3 does not
absorb the constant offset between a shrunk candidate and a full-length
previous output.
Alternatives: previous full-length output (would change the search
and mix l' and l inside m3).
Evidence: test_akc.py (2b) AkcArm check (search-time argmin and cost
identical with output_shrunk True / False); the 382-run replay in
AKC-053.
Reversibility: AkcArm.step, the prev_e / prev_s assignment.
Review: whether the paper's m3 refers to the previous output.
Annotation (2026-09-28): unchanged by the amended AKC-053; the output
still differs from the search-time points (length l vs s l), so the
choice still matters.

ID: AKC-055
Status: UNCERTAIN
Decision: When the shoulder candidates rebuilt about the full-length
elbow (AKC-053) have the same count as at search time, the candidate
with the chosen index is taken (same sign / same ray root, both lists
in ascending order); when the count differs (a root appears or
vanishes, or the rebuilt set falls back, Eq. 9), the rebuilt candidate
nearest the search-time shoulder is taken.
Why: the branch is what the search decided; the index carries it when
both lists enumerate the same roots, and nearest-point is the only
defined carry-over when they do not.
Alternatives: always nearest (equivalent in the normal case, less
explicit about the branch).
Evidence: the count-change path runs once in test (2b) (literal,
W_b, frame 83 of the synthetic arm) and the output lengths hold there
to 1e-12.
Reversibility: akc.full_length_chain.
Review: none expected; rare path.
Annotation (2026-09-28): under the amended AKC-053 this rule applies
only inside the counted radial fallback (the full-length solve failed);
the frame-83 case now re-solves at full length without it. The path is
covered by test (4) (constructed ray case) and was taken 0 times in the
full run.

## M3: code-review fixes (2026-09-28)

ID: AKC-056
Status: UNCERTAIN
Decision: The EKF elbow length constraint is anchored on the Stage-3
(Kalman-filtered) wrist estimate, falling back to the Stage-4 wrist p_w
only while the wrist filter is uninitialised; the shoulder constraint
stays anchored on the constrained elbow. The M2 anchor (p_w, the raw
measured wrist when present, AKC-016 / AKC-021) is kept as
AkcArm(ekf_anchor="raw") and reported as the kf_sweep row
ekf_anchor=raw (sigma_l 0.02).
Why: master decision (2026-09-28, author to confirm), from the Opus
code review. The paper's constraint h(x) = ||p_i - p_j|| (Eq. 4-6) is
part of Stage 3, a relation between filtered landmarks; Stage 4 is
where the wrist is "kept". The anchor choice dominates the AKC-EKF
result. Mechanism (review, partly re-measured here): during a mask
the elbow position covariance collapses radially (std about 1.45 cm)
while the tangential covariance keeps growing, so each radial
innovation caused by raw-wrist jitter is mapped by P H_c^T into a
large tangential slide of the elbow; the filtered wrist removes most
of that jitter.
Alternatives: (a) raw anchor p_w (M2, kept as ekf_anchor="raw");
(b) skip the constraint when no filtered wrist exists (equivalent in
every run here: the wrist filter is initialised whenever p_w is a
measurement, and no EKF run uses wrist_override); (c) an iterated or
isotropic EKF (not in the paper, AKC-016).
Evidence: results/kf_sweep.csv, P1 M-E MASK_ALL pooled elbow median,
R-self (n = 135): filtered anchor 3.26 / 1.58 / 1.25 cm at sigma_l
0.005 / 0.02 / 0.05 m; raw anchor at 0.02 m 5.12 cm (M2 values:
14.14 / 5.12 / 1.65 cm, the raw row reproduces 5.12 exactly). R-meas:
filtered 2.97 / 1.71 / 1.69 cm, raw 5.22 cm. Scratch runs in this task
(r7 right, window 490-534, elbow masked, default Q): elbow position
std along the elbow-wrist direction 1.45 cm at frames 500 and 534
(raw anchor); combined std across the two tangential directions
20.4 cm at frame 500 and 67.0 cm at frame 534 (the review reports
14 cm per direction at 500 and 29 to 60 cm at 534, consistent);
raw r7 right wrist frame-to-frame step inside the three windows
median 0.45 cm, p95 1.41 cm (the review quotes 0.42 / 1.23 cm with an
unrecorded definition, not reproduced exactly); |raw wrist - Kalman
wrist| median 0.17 cm, p95 0.58 cm in window 490-534. The effect also
depends on Q: sigma_a 1.0 gives 0.92 cm (raw anchor) and 1.40 cm
(filtered anchor), against 5.12 / 1.58 cm at the default 5.0 (scratch,
same pooled metric). Test (7) checks both anchors inside AkcArm (the
elbow anchor equals the Kalman wrist in 199/199 frames for "filtered"
and the measured wrist in 199/199 for "raw"; the shoulder anchor
equals the constrained elbow in both).
Only the masked AKC-EKF rows move (p1_synthetic_elbow.csv M-E and M-ES
MASK_ALL, 24 rows; kf_sweep.csv sigma_l rows plus the new row); the
unmasked and MASK_Z AKC-EKF rows are unchanged because the kept pixel
fixes the ray and the reference only picks the branch.
Reversibility: AkcArm(ekf_anchor="raw") (run_akc(..., ekf_anchor=
"raw")); the P1 AKC-EKF rows and the sigma_l sweep rows change back.
Review: HIGH. Author to confirm the reading of the paper's constraint
anchor; the AKC-EKF numbers depend on it and on Q.

ID: AKC-057
Status: UNCERTAIN
Decision: Test fixture constants added after the code review
(test_akc.py): (a) the "away" synthetic arm mirrors the z components
of both AKC-031 bone directions (same shoulder, curves and lengths), so
the true elbow and shoulder lie on the "-" root in 200/200 frames;
(b) test (3) computes the expected branch from roots written out in
the test (_hand_roots), not from akc._candidates, and expects 3
candidates when the hand solve about the wrong elbow root has no two
roots; (c) a literal hand case: wrist (0, 0, 1) m, elbow x, y (0.10,
0.05) m, shoulder dx, dy (0.05, -0.20) m about the elbow, l_f 0.23,
l_u 0.25, giving roots z_w -/+ sqrt(0.0404) and z_e -/+ sqrt(0.02);
reference depths 0.80 / 0.85 / 0.62 / 0.70 / 1.15 m chosen to sit
nearer one root; (d) single-term weights (w1 = 1 or w3 = 1, all others
0) so m1 or m3 alone decides, with previous-choice offsets 3 mm
(elbow) and 4 mm (shoulder), c = 0.007 by hand; (e) the m4 flip uses
w1 = 100 with ref_e at the true elbow (fixes the elbow root), w5 = 0
and ref_s 60 % of the way to the wrong shoulder root; (f) the Q check
writes out sigma_a^2 G G^T with G = [dt^2 / 2, dt], sigma_a 5; (g) the
partial update check starts a filter at rest at z = 1.5 m with sigma
1e-9 (near-unit gain) and pixel (400, 300), tolerance 1e-9 m.
Why: each constant isolates one mutation the review found surviving
(m4 removed, literal "-" root replaced by "+", wrong Q, m1 or m3
dropped, m1 against ref_s, partial update at a fixed 1 m depth), and
the EKF anchor mutant (AKC-056). The values are geometric
constructions, not measurements.
Alternatives: none tried.
Evidence: test output (77 PASS); mutation runs in this task: each of
the eight mutants passes the M2 test file and fails the new one.
Reversibility: test-only.
Review: none expected.

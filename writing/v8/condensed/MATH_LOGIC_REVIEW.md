STATUS: COMPLETE

GOAL: Review the finished condensed thesis for mathematical correctness,
logical consistency, and whether its conclusions follow from its evidence.

KEY FINDING: Chapter 5's main equations and worked example check out on
reachable, nondegenerate inputs. Its unreachable-target explanation needs
a mathematical correction. The remaining thesis needs corrections to
evaluation claims, recovery-policy descriptions, and several explanations.

VERIFIED: All nine chapter texts and their equations, plus Appendices A-F,
match the reviewed assembled document. Worked examples, independent
kinematic tests, recovery diagnostics, table sources, and analytical
counterexamples were checked. The structural reference checker passes.

ASSUMPTIONS/UNRESOLVED: Physical accuracy is not established by these
algebra checks. Manual wrist labels, live-camera validation, the hip-depth
method's final presentation, inter-recording segment calibration, and the
historical live comparison inputs remain unresolved.

DECISION: Preserve the manuscript as reviewed. Report corrections and
their evidence separately; do not silently rewrite claims or replace
experiment results during an audit.

NEXT: Resolve the high-priority findings, rerun affected comparisons with
archived inputs, then revise the thesis and review the changed claims.

Reason:
Correct equations on ordinary inputs do not establish correct boundary
handling or independently validated tracking accuracy. Most table entries
were transcribed correctly; several interpretations exceed what those
tables and their protocols support.

Evidence:
The detailed findings below identify the affected section, the problem,
its evidence, and a proposed correction. Archived reviewer records and
reproducibility scripts are in [audit_evidence](audit_evidence/).

Therefore:
The thesis has a sound mathematical core, but a blanket verdict that its
math and logic are correct would be premature. This audit is complete;
the corrections it identifies have not been applied.

## Reviewed revision and scope

- Review date: 2026-09-06.
- Repository revision at review start: 3799c5c; the condensed thesis was
  completed in dbfe450.
- Document: writing/v8/Thesis_V8_Condensed.docx.
- SHA256: d51132ab90387f3d57d8cca5ac409817b3356ba173e5f172ba7427f57d7d4c0a.
- Coverage: abstract, Chapters 1-9, Appendices A-F, relevant source
  equations, implementation, and pinned reports. Native Word equation
  structure was inspected where flattening could obscure the mathematics.
- Focus: correctness, assumptions, metric definitions, and inference.
  This was not a complete literature novelty search, a style review, a
  physical experiment, or a visual inspection of every rendered page.
- Historical result transcription, fresh computations on current local
  outputs, and constructed mathematical counterexamples are distinguished
  throughout. New diagnostics are audit evidence, not replacement thesis
  results.

## Chapter 5 verdict

The user's final priority was to establish Chapter 5's mathematical
correctness before receiving the other feedback. Its central derivation
passes, subject to the following domain and policy qualifications.

| Equations | Verdict | Conditions |
|---|---|---|
| 5.1-5.4, grip relation, inverse offset, least-squares fit, EMA | Correct | Common coordinate frame and proper object rotation; an estimate need not equal the physical wrist |
| 5.5, normalized direction memory | Correct | Unit direction inputs; the stated gain 0.30 keeps the normalization denominator nonzero |
| 5.6, wrist from elbow and forearm memory | Correct construction | Extrapolated direction is a prior, not independently observed motion |
| 5.7, wrist from object pose and offset | Correct | Rigid grip and compatible coordinate frames; grip changes and pose errors remain limitations |
| 5.8-5.11, two-sphere elbow circle | Correct | Positive link lengths, nonzero shoulder-wrist distance, reachable target; boundary circles can collapse to a point |
| 5.12, closest direction-prior point on the circle | Correct | Nonzero prior projection; otherwise the stated fallback supplies a direction |

The exact reachable domain is abs(L1-L2) <= r <= L1+L2. At coincident
shoulder/wrist positions the axis-based parameterization is undefined;
equal-length links can still have infinitely many geometric solutions.
Outside reach, clipping is an approximation, not an exact solution of
both link constraints. This is the actual mathematical correction M04.

The frame-560 worked example reproduces the recorded output. Its 31.7 cm
upper arm and 20.5 cm forearm are recovered by the independently evaluated
elbow construction, and the stored joint-angle output agrees to numerical
precision. This verifies the worked calculation, not physical wrist truth.

M05 and M07 concern discrepancies between the implementation and the
stated twist/memory policies; M06 concerns the corrected torso inputs;
M08 qualifies the offline temporal preparation. None overturns the
ordinary reachable IK derivation. Together they prevent certifying every
claim in Chapter 5 without correction.

## Priority list for the rest of the feedback

HIGH means the issue affects a headline inference, evaluation validity,
or a claimed recovery guarantee. MEDIUM means a material explanation,
assumption, or reproducibility correction. It does not mean the issue
occurs on every frame or invalidates every reported result.

| ID | Priority | Location | Finding |
|---|---|---|---|
| M01 | HIGH | Abstract; 7.1-7.2; 9.3 | Fitted path residual is not an upper bound on tracking error |
| M02 | HIGH | 7.3.2; Table 7.6; 9.3 | Moving-outage comparison violates stated eligibility |
| M03 | HIGH | 8.3; live validator | Shifted angle comparison uses the wrong validity pairing |
| M04 | HIGH | 5.5 | Unreachable IK clipping does not preserve both link constraints |
| M05 | HIGH | 5.5 | Recovered twists bypass the stated low-flexion hold |
| M06 | HIGH | 5.1, 5.6; 7.4 | Load-bearing hip-depth correction is not specified |
| M07 | MEDIUM | 5.3, 5.5 | IK uses direction memory beyond the stated expiry |
| M08 | MEDIUM | Abstract; 5.3-5.4; 6.3; 8 | Offline, causal, and displayed reconstructions are not identical |
| M09 | MEDIUM | 7.3-7.4 | Angular error aggregation and reference meaning are underdefined |
| M10 | MEDIUM | 2.2 | Gravity inference requires an upright marker, not only a plumb wall |
| M11 | MEDIUM | 3.4; equation 3.17 | Gimbal-lock extraction is incomplete in the text |
| M12 | MEDIUM | 2.5; Appendix F | Zero phase does not preserve amplitude, shape, or every event time |
| M13 | MEDIUM | Appendix F | Median-filter ramp and spike claims are false in general |
| M14 | MEDIUM | Appendix E.2 | Pose-lobe separation does not guarantee disambiguation |
| M15 | MEDIUM | 7.3.3 | Shared label error does not affect methods identically |
| M16 | MEDIUM | 6.1 | One packet does not guarantee equal source instants during holds |
| M17 | MEDIUM | 3, 5, 6, 7 | Segment lengths differ materially between recordings and avatar |
| M18 | MEDIUM | 7.1.3; 7.3.2 | Eligible-window and general recovery-benefit claims conflict |

## Detailed findings

### M01. Fitted path residual is not an accuracy upper bound

Section 7.2 says the rail deviation mixes tracking error and how the cube
rides the rail, "so it bounds the tracking error from above."
This implication is false.

The line is fitted to the same tracked points being assessed, using total
least squares in eval/gt/eval_rail_scenario.py. A true trajectory
p=(x,0,0) and measured trajectory q=(x,1,0) have zero fitted-line residual
despite a one-metre position error. Along-line error is also invisible to
distance from an infinite line. Even with an independently surveyed line,
physical departure and measurement error can cancel; their sum does not
generally bound either component.

The loop waypoints also come from the tracked stations, as
eval/reports/r5_waypoint_eval.md discloses. The rail and loop numbers do
match their pinned reports, but they are not independently surveyed
absolute pose errors. The abstract's "known truth" for synthetic masking
likewise means a detector-accepted, unmasked reference, not independently
known anatomy.

Correction: retain the measurements as transverse consistency or path
shape residuals. State their blindness to fitted bias, scale, and
along-path errors. Separate physical ruler checks, algebraic consistency,
synthetic references, and independent tracking accuracy throughout the
abstract, evaluation opening, and conclusion. See evaluation_review.txt
E2 and analytical_checks.json.

### M02. The strongest positive comparison does not follow its protocol

Section 7.3.2 says the two hand-carved moving outages use the same
conditions as the automatic selection, except spacing. Table 7.6 comes
from eval/failure/moving_window_check.py, which instead scores all finite
wrist observations in its hardcoded windows without applying the harness's
reference-liveness and failure conditions.

Reapplying the actual eligibility rule gives:

| Outage, inclusive frames | Scored in table | Eligible | Ineligible frames |
|---|---|---|---|
| 865-895 | 31 | 29 | 894-895 |
| 870-902 | 33 | 24 | 894-902 |

The first excluded frames fail reference joint-group liveness; frames
896-902 additionally have torso detector failures. The two outages overlap
for 26 frames and cover only 38 unique frames. These are two overlapping
examples, not independent replications.

A diagnostic that retains only eligible scoring frames still finds a
recovery advantage. Its recovery medians are approximately 1.7 cm in both
windows, against hold medians of approximately 2.0 and 2.1 cm. However,
hold maxima fall from 15.4/21.4 cm to 9.1/8.6 cm. The large tail values used
in the headline comparison partly come from excluded reference states.
These are post hoc subsets of the existing runs, not newly designed
eligible-only experiments or replacement thesis values.

Correction: rerun with explicit valid windows or label the current table
as an exploratory wrist-only comparison under different conditions.
Disclose overlap. Preserve the observed benefit without claiming that the
current table satisfies the declared protocol. Sources:
evaluation_review.txt E1, evaluation_diagnostic.json, and
moving_eligible_check.txt; implementation lines 97-138 of
eval/failure/moving_window_check.py and selection lines 179-227 of
eval/failure/harness_recovery.py.

### M03. Lag alignment uses an incorrectly shifted validity mask

v2/integration/validate_v2_r5.py:111-116 compares la[k:] with ra[:-k] for
positive lag k, but uses clean[k:], where clean was formed from live and
reference validity at the same original row. This tests reference validity
at the wrong time. The required pairing is live_valid[k:] combined with
reference_valid[:-k], after a correct frame/time join.

On the current local inputs, lag five produces 179 old pairs but only 174
correctly paired valid samples; five old pairs have invalid shifted
references. This is a concrete validator defect, not only a reporting
concern.

Those current CSVs do not reproduce all historical Chapter 8 angle
statistics. Their hashes are recorded in evaluation_diagnostic.json.
The pinned historical validation output still reports 10/12 and lag five,
but its original complete input pair was not established during this
audit. Current recomputation cannot supply a corrected historical value.

Correction: fix validity alignment in the active validator, archive exact
input CSVs and hashes, and rerun lag and angle comparisons. Until then,
the historical alignment/accuracy figures remain qualified. Do not replace
them with current-output values under the same historical label.

### M04. Unreachable wrist clipping relaxes the geometry

The two-link construction is correct on its reachable domain:
abs(L1-L2) <= r <= L1+L2, with special treatment at degeneracies.
Clipping the cosine outside this domain keeps a finite elbow but cannot
create an intersection of the two constraint spheres.

Section 5.5 also says an inner-unreachable wrist clips the cosine "at the
other end." With the chapter's L1=0.317 m and L2=0.205 m, taking r=0.050 m
gives cosine 1.923, which clips to +1, not -1. The resulting elbow is
0.317 m from the shoulder and 0.267 m from the wrist; the required forearm
is 0.205 m. An outer target at r=0.600 m similarly produces a 0.283 m
forearm. Production _ik_elbow reproduces these counterexamples.

Correction: state the exact reachable domain and identify which constraint
the fallback relaxes. If the wrist is projected into reach instead,
report its displacement. The near-full-reach memory substitution and
subsequent slew limiting also need distinction from the exact IK solution.
See recovery_review.txt R1 and v1/kinematics/occlusion_ext.py:324-353.

### M05. Recovered twists do not obey the universal hold claim

Section 5.5 says twist retains its previous value below 15 degrees of
elbow flexion and leaves the layer held. In the implementation, recovery
first clears the group's live bit. The subsequent hold assignment requires
that live bit, so already constrained twists bypass it
(occlusion_ext.py:739-784).

A diagnostic replay of the 900-frame rail recording found 18 constrained
right-arm outputs below 15 degrees with changing twist. At frame 7, elbow
flexion is about -12.4 degrees and twist changes by +3.4 degrees; frame 8
changes it by -2.4 degrees. These are actual solver outputs.

Correction: document the measured-only scope of the implemented hold, or
implement the intended universal rule in an authorized active copy and
regenerate affected results. This audit does not authorize editing frozen
v1. See recovery_diagnostic.py and its saved output.

### M06. The hip-depth method is necessary but insufficiently described

The condensed thesis removes the torso-repair derivation while retaining
its outputs, timing, figures, and Section 7.4 results. The short memory
description also omits the memory-free shoulder-depth gate documented in
eval/DECISIONS.md E-027.

This is more than a missing explanatory paragraph. The frame-560 example
describes the torso as measured, whereas its reproduced root is tagged
CONSTRAINED after internal hip repair. The chain actually evaluated uses a
method not fully specified in the presented model. Reduced yaw spread or
a more upright root is a stability observation, not independent proof of
correct anatomical orientation.

Correction: give the minimum complete preprocessing algorithm, assumptions,
thresholds, and effect on source tags in one defining location. Explicitly
separate corrected torso inputs from directly measured ones in the worked
example. D2 already records the unresolved presentation choice. See
CONDENSE_SUMMARY.md, CH5_PARKED.md, recovery_review.txt, and
evaluation_review.txt E9.

### M07. The stated memory horizon does not apply to every use

Section 5.3 says a direction memory with no update for 45 frames is stale
and unused. Direct memory recovery and the near-reach guard enforce the
horizon, but ordinary IK passes the last direction without an age check
(occlusion_ext.py:710-717).

The replay uses an expired right-arm swivel prior on 45 IK frames,
595-639, with ages 46-90 frames. Retaining an old direction as a regularizer
can be a design choice, but it is not the stated expiration policy.

Correction: distinguish bounded memory extrapolation from a persistent
swivel prior, or enforce the horizon and regenerate the affected outputs.

### M08. Offline, causal, and displayed outputs need separate claims

The abstract says the viewer sees the reconstruction evaluated in the
offline chapters. Section 6.3 and the implementation explicitly apply an
additional display smoother only to the output packet, while evaluation
dumps retain unsmoothed values (v2_integrate.py:404-421). Chapter 8 also
reports nonzero offline/live discrepancies.

The offline grip labels are retrospective: entry can be backdated and
exit frames cleared after confirmation. Extending a test prefix from
eight frames to ten changes already returned holding labels on frames
5-7. Offset warm-up can use a full-episode fit. The mature frame-560 EMA
does use past clean updates; this finding does not establish leakage of
masked wrists into scored offsets. It does invalidate unqualified
past-only descriptions of the whole offline preparation.

Timing quantities also differ: the two-frame output delay, the estimated
five-frame offline/live alignment, processing time, and sensor-to-display
latency are not interchangeable. No complete physical latency measurement
was verified. A pinned landmark maximum of 34.26 ms exceeds the nominal
33.3 ms interval even though its p99 fits. The phrase "a fraction of a
degree on the well-conditioned angles" also overstates the rail results:
reported median elevation and twist errors are 1.44 and 7.28 degrees.

Correction: describe common algorithms and differing outputs. Call the
recovery causal and stateful where appropriate, not stateless. Name each
latency and accuracy statistic with its conditions; qualify replay as
feasibility evidence rather than every-frame deadline or display-equivalence
proof. See evaluation_review.txt E6 and recovery_review.txt R4.

### M09. State exactly which angular metric is reported

Table 7.5 pools five arm columns, including the elbow coordinate that the
kinematic convention makes zero. That adds structurally easy samples to
the aggregate and obscures error in the independent angles. The caption
does not explain weighting or the twist-validity exclusions.

Section 7.4's 53.92 versus 8.86 degrees is a percentile of flattened
absolute wrapped Euler-coordinate differences, not an SO(3) orientation
distance. Its reference is each solver's matching uncorrupted baseline
on a constructed opposing hip-depth corruption, not independent anatomy.

Correction: define aggregation and report nonredundant/per-joint metrics,
or recompute rotation distance from relative matrices. Label the existing
torso statistic as Euler-component deviation and include the corruption
and reference conditions. Sources: harness_recovery.py:105-113,266-278;
validate_occlusion_ext.py:211-235; evaluation_review.txt E4.

### M10. Plumbness alone does not define marker up

Section 2.2 obtains gravity from the wall marker's in-plane up axis on the
assumption that the wall is plumb. Rotating the printed marker by 30
degrees within the same vertical wall leaves the wall plumb but turns that
axis 30 degrees from vertical.

The implementation itself names an upright-mounting assumption
(extract_aruco_poses.py:87-88); calibrate_scene.py:137 uses the marker's
second rotation column. The actual mounting was not independently measured
in this audit.

Correction: state both the vertical-wall and upright-marker requirements,
including how alignment and sign were established. Treat their uncertainty
as shared by gravity-referenced heights and tilts. See kinematics_review.txt
K2 and kinematics_diagnostic.py.

### M11. Equation 3.17 needs its singular branch

The generic inverse of Ry(y) Rx(x) Rz(z) is correct away from gimbal lock.
At x=+/-90 degrees, however, its printed y=atan2(m13,m33) becomes
atan2(0,0). Merely stating that z is set to zero is insufficient.

Using the thesis's one-based indices, the locked branch with z=0 is:

- x=+90 degrees: y=atan2(m12,m11).
- x=-90 degrees: y=atan2(-m12,m11).

For Ry(40) Rx(90) Rz(25), the correct locked triple is (90,15,0), not
(90,0,0). The source implementation already handles both signs correctly;
this is a missing derivation branch, not a newly found code defect.
See root_frame.py:44-52 and kinematics_review.txt K3.

### M12. Filter attenuation contradicts the preservation explanation

Section 2.5 justifies a 3 Hz fourth-order forward/backward Butterworth
filter by saying deliberate motion below roughly 5 Hz remains intact.
The combined amplitude response at 3, 4, and 5 Hz is approximately
0.500, 0.0744, and 0.00995. A 4 Hz motion component retains only about
7.4 percent of its amplitude.

Appendix F also equates zero phase with unchanged shape and event times.
Different frequency components are attenuated differently, so local peaks
can move. The saved constructed example shifts a central peak by one
30 Hz sample despite forward/backward filtering. This is not a measured
shift in the subject's recording.

Correction: distinguish zero phase from amplitude/shape preservation and
acknowledge distortion near the cutoff. Justify the chosen tradeoff using
data or stated assumptions. The cascade interpretation is consistent with
the [SciPy filtfilt documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html);
the specific counterexamples are independently computed in
audit_math_logic.py and kinematics_diagnostic.py.

### M13. A median filter does not generally staircase a ramp

Appendix F says a steady move becomes a staircase and a single-frame spike
has no effect at all. A centred odd-window median reproduces a strictly
monotone ramp at interior samples. Conversely, replacing one member of
the window [0,1,2,3,4,5,6,7,8] by 1000 can change its median from 4 to 5.

Correction: describe rejection of isolated extreme samples under suitable
local conditions, not universal immunity. Plateaus or steps depend on the
input and window; they are not the inevitable response to a steady ramp.
See analytical_checks.json.

### M14. Angular lobe separation is not reprojection distinguishability

Appendix E.2 says affine ambiguity makes the two pose lobes collapse
toward each other and uses 40-degree separation to explain perspective
discrimination. In the orthographic limit, planar points rotated by
+30 or -30 degrees about y project identically, while their normals are
60 degrees apart.

Correction: describe the 40-degree switch as an implementation heuristic.
Angular separation alone does not establish which branch is observable
from noisy corners. The [IPPE authors' explanation](https://github.com/tobycollins/IPPE)
likewise distinguishes two candidate poses and their reprojection errors
and describes near-affine ambiguity. This finding questions the general
explanation, not the verified numerical world-transform equations.

### M15. A shared imperfect label can favour one method

Section 7.3.3 says click/depth limitations affect recovery and baseline
identically. If a reference is y=x+e and an estimate is h, then

    ||h-y||^2 = ||h-x||^2 + ||e||^2 - 2 (h-x).e

The final term is method-dependent. Cube-surface depth used as a wrist
reference is especially problematic for an estimate anchored on that cube.
It can favour recovery; using the same reference does not make relative
errors unbiased.

Correction: skip fully hidden/unlocalizable wrists; record visibility and
depth validity separately, or use an independent reference. Describe
shared uncertainty without claiming identical effects. Labels are still
pending, so no existing natural-failure result was fabricated. The current
labelling handoff's instruction to skip hidden wrists is the stronger rule
to preserve.

### M16. A shared output time is not a shared observation time

Section 6.1 says one combined packet means the reconstruction can never
show the person and object from different instants. StreamBuffer.emit
independently holds stale data for either stream. A person observed at
t=0 and an object observed at t=1 can both be emitted for render time t=1.
The saved diagnostic executes the actual buffer class and reproduces this.

Correction: state that streams are evaluated at a common requested render
time and delivered atomically, with interpolation/hold flags exposing
different observation ages. A shared clock and frame identifier remain
valid synchronization mechanisms; they cannot supply missing observations.
Also replace "the merger is the only stage that reads both branches":
the landmark recovery branch explicitly reads object data earlier in 6.1.

### M17. Segment calibration and avatar proportions need reconciliation

The rail worked examples use an upper arm of 31.7 cm and forearm of
20.5 cm. The loop clean-frame values are 25.8/24.7 cm. Section 6.3 also
specifies loop-derived avatar segment lengths, including 25.6/25.2 cm
for the right arm, while illustrating the rail recording.

An angle-preserving transfer preserves endpoint positions only with the
matching segment lengths and shoulder placement. For directions u,v,
changing lengths changes the endpoint by delta_L1*u + delta_L2*v; an
approximately similar total arm length does not eliminate that error.

Correction: document whether these are effective per-recording model
lengths rather than anatomical lengths, explain the discrepancy, and
identify the exact lengths used in the displayed rail scene. Separate
solver wrist residual from avatar endpoint residual. The discrepancy was
already acknowledged in CONDENSE_SUMMARY.md; its cause and the exact
rendered configuration were not established by this audit.

### M18. Window availability and recovery generalization need narrowing

Section 7.1.3 says neither hand supplies eligible 45-frame windows, while
7.3.2 reports one left and two right windows. Natural blackout intervals
without references and the separate clean intervals used for masking are
different sets and should be named accordingly.

The same discussion describes object-anchor bias as flat in time, memory
as initially unbiased, and a crossover within one second as the operating
case. These are interpretations of two short overlapping examples, not
general consequences of rigid offset recovery. Pose noise, changing grip,
IK guards, and motion direction can alter or reverse those trends. M02
further limits the claimed comparison.

Correction: state what occurred in the selected windows, retain the
negative slow/still results, and name the assumptions behind any expected
drift argument. Likewise replace 7.1.2's claim that any future deviation
can "never" come from algebra with the narrower statement that the
tested inverse identities passed on the tested inputs.

## Smaller corrections and scope qualifications

- Chapter 3's worked answers are correct from full-precision inputs, but
  the claim that rounding only changes the last digit is false for the
  displayed substitutions. atan2(0.06,0.03) is about 63.4 degrees, not
  59.9. More input precision or approximate notation is needed; do not
  replace the correct answer with the rounded-input result.
- Appendix E.4's printed Rodrigues scalars reconstruct the displayed
  matrix with a largest difference about 0.0000204, exceeding its claimed
  0.00001. This is a rounding/presentation issue; the Rodrigues identity
  is correct. The exact-axis formula also needs separate handling at
  zero and 180 degrees if presented as a complete inverse algorithm.
- A positive right-arm local x component points outward rather than
  "across the body" in the Chapter 3 example.
- Chapter 9's "full reported visibility" conflicts with its Figure 9.1
  caption's 0.57 elbow visibility. "Above the threshold" is supported.
- Chapter 1's bimanual framing needs the existing D5/C31 scope decision:
  the primary rail task is one-handed, and the secondary loop supplies
  handovers. Do not imply that every primary result validates bimanual
  manipulation. A comprehensive novelty claim about all prior systems
  was not established by this audit's source review.
- Replaying an avatar does not by itself guarantee that raw imagery never
  leaves a device, as the motivation implies. That is a deployment/data
  handling property, not a consequence of the kinematic representation.
- Appendix D's colour/depth alignment is geometric registration; common
  pixels can still have occlusion and surface-association errors. The
  later depth-substitution limitations correctly acknowledge this.
- Table E.1 distinguishes range from optical-axis depth. They should not
  be compared as if they were the same scalar. The table's pose ranges
  are consistent with norms of its rounded translation vectors.

## What passed, and what each pass means

| Area | Verification | Meaning and limit |
|---|---|---|
| Calibration | Determinant-corrected SVD rotation projection and 45/50 translation scale | Correct algebra under calibration assumptions |
| Rigid transforms | Homogeneous inverse/composition; world anchoring | Correct frame algebra; no proof of physical calibration accuracy |
| Torso frame | Cross-product construction and ordinary Euler inverse | Correct for nondegenerate landmarks; singular text needs M11 |
| Arm model | 1,000 deterministic independently generated shoulder/Euler cases and mirrored arms | Reconstructed vectors/matrices agree to numerical precision |
| Chapter 3 example | Frame 533 recomputed from source inputs | Printed full-precision-derived answers match |
| Recovery | Grip transform, offset least squares, EMA, reachable IK circle/prior minimizer | Correct within stated geometric domain; policies need M04-M07 |
| Chapter 5 example | Frame 560 replay and independent elbow construction | Stored angle output and exact reachable geometry reproduce |
| Unity mapping | Equations 6.1-6.5 checked against code; anchor factorization independently tested | Proper coordinate composition; actual scene appearance was not rerun |
| Depth | Appendix C/D deprojection worked examples | Rounded positions match the stated intrinsics and depths |
| Evaluation tables | Rail, loop, fixed-window and moving-window tables traced to reports | Transcription generally passes; validity and inference need corrections |
| Masking | Removed wrist samples excluded from local and episode offset fitting | No direct scored-wrist leakage found in this path |
| Timing | Tables 8.2/8.3 traced to pinned run summaries | Historical processing measurements, not physical display latency |
| References | 429 recognized references; no unresolved targets | Structural existence only, not semantic or literature validation |

## Reproduction and evidence

Run from the repository root. The analytical script needs NumPy/SciPy;
the recording diagnostics additionally need existing gitignored pipeline
outputs on this workstation. Their saved outputs preserve the audit
observations for a clone without those recordings. No camera is required.

    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/audit_math_logic.py
    /home/luo/anaconda3/bin/python writing/v8/condensed/audit_evidence/kinematics_diagnostic.py
    /home/luo/anaconda3/bin/python writing/v8/condensed/audit_evidence/recovery_diagnostic.py
    /home/luo/anaconda3/bin/python writing/v8/condensed/audit_evidence/evaluation_diagnostic.py
    /home/luo/anaconda3/bin/python writing/v8/condensed/audit_evidence/moving_eligible_diagnostic.py
    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/check_refs.py

Original worked-example checks:

    PYTHONDONTWRITEBYTECODE=1 /home/luo/anaconda3/bin/python writing/v7/scripts/ch3_numbers.py
    PYTHONDONTWRITEBYTECODE=1 /home/luo/anaconda3/bin/python writing/v8/scripts/ch5_worked_example.py

The detailed reviewer records preserve exact source lines, intermediate
values, and qualifications:

- [Kinematics review](audit_evidence/kinematics_review.txt).
- [Recovery review](audit_evidence/recovery_review.txt).
- [Evaluation review](audit_evidence/evaluation_review.txt).
- [Analytical counterexamples](audit_evidence/analytical_checks.json).
- [Kinematic numerical output](audit_evidence/kinematics_diagnostic_output.txt).
- [Recovery diagnostic output](audit_evidence/recovery_diagnostic_output.txt).
- [Evaluation input hashes and diagnostics](audit_evidence/evaluation_diagnostic.json).
- [Eligible-frame comparison](audit_evidence/moving_eligible_check.txt).

These records were produced by three independent topic reviews and a
whole-thesis integration review. Temporary extraction paths mentioned in
the archived reviewer text refer to the review workspace, not extra
required project inputs.

## Recommended correction sequence

1. Correct reference/accuracy language and the moving-window protocol.
   Preserve the demonstrated recovery advantage with its proper limits.
2. Correct the shifted-validity bug and pin comparison inputs before
   regenerating Chapter 8 metrics.
3. Resolve the intended recovery policies and document the complete
   hip-depth preparation. Changes to implementation require new output
   and validation, rather than prose alone.
4. Reconcile model/rig calibration; add missing mathematical conditions
   and correct filter/ambiguity explanations.
5. Recheck abstract and conclusion against the corrected evidence, then
   perform a fresh review of changed sections.

Changes in this audit: review documents, diagnostic scripts/evidence,
and handover/index updates only. The thesis DOCX, chapter builders,
experiment implementations, and existing result files were not edited.

## Status after the correction pass (2026-09-06, evening)

Applied in the condensed builders only (writing/v8/condensed/scripts);
no pipeline, report or result file was changed. Wording fixes carry the
finding as an honest statement of what was done; DECISION items need the
user (a rerun, a changed protocol, or a number that does not exist).

| ID | Status | Where and how |
|---|---|---|
| M01 | wording fixed | Abstract, 7.1, 7.1.1, 7.2, 9.3: the rail line is fitted to the tracked slide samples, so the deviation is a transverse consistency residual, blind to along-line error and to a bias the fit absorbs; the tape length, rail height and tilt stay as separate physical cross-checks; "known truth" and "upper bound" wording removed |
| M02 | wording fixed; rerun is DECISION | 7.3.2 says the two outages were carved by hand and scored on every frame of their windows (the rule excludes 2 and 9 frames), that they share 26 frames of 38, and that Table 7.6 is an exploratory wrist-only comparison; one sentence reports the post hoc eligible-only check (moving_eligible_check.txt); 9.3 quotes medians only. A rerun with eligible-only windows would replace the table: user decision |
| M03 | wording fixed; rerun is DECISION | 8.3 discloses the unshifted validity mask and keeps the historical figures as reported; 9.1 and Table 9.1 list the rerun with corrected pairing on archived inputs |
| M04 | fixed | 5.5: the two-link construction is exact only between the difference and the sum of the link lengths; outside, clipping keeps the upper-arm length and relaxes the forearm; the inner case also clips at one; the reach guard's memory substitution also relaxes the forearm length |
| M05 | documented as implemented; universal hold is DECISION | 5.5: the hold applies to a twist solved from measured landmarks; a twist on a rebuilt arm is constrained and bounded only by the rate limit. Changing the guard needs an implementation change and regenerated results |
| M06 | partly; rule is D2 | 5.6 says the hips carry a replaced depth and the root leaves constrained; the preparation's rule, threshold and memory remain undescribed (decision D2) |
| M07 | documented as implemented; enforcing is DECISION | 5.3 and 5.5: the 45-frame horizon bounds the memory rebuild and the reach guard; the two-link solve takes the last measured direction without an age check |
| M08 | wording fixed | Abstract, 5.3, 5.4, 6.3, 8.1, 8.2, 8.3, 9.3: retrospective offline preparation stated; recovery layer stateful and causal; declared delay, lag-search alignment, per-stage times and the unmeasured sensor-to-screen delay named apart; 34.26 ms maximum beside the p99; the 8.3 accuracy sentence names its angles; display smoother on the output only |
| M09 | wording fixed | Table 7.5 caption states the pooling; 7.4 states the window, the corruption and the per-component Euler measure |
| M10 | fixed in 2.2; 2.4 sentence is a find/replace for the user | 2.2.1 and 2.2.2 state the plumb wall and the upright marker mounting, the latter not measured; the Section 2.4 sentence "is mounted on a plumb wall and gives the vertical gravity reference" is the user's text (find/replace list in the final report) |
| M11 | fixed | 3.4: the locked branch printed after equation (3.17) |
| M12 | Appendix F fixed; 2.5 sentence is a find/replace for the user | Appendix F states what zero phase does and does not preserve; the Section 2.5 "below roughly 5 Hz" sentence is the user's text (find/replace list in the final report) |
| M13 | fixed | Appendix F: what a median filter does to an isolated extreme, a ramp and a peak |
| M14 | fixed | Appendix E.2: the 40 degree switch is a heuristic; angular separation is not reprojection distinguishability |
| M15 | fixed | 7.3.3: shared label uncertainty does not cancel; hidden marks skipped; cube-face depth checked |
| M16 | fixed | 6.1: merger pairs the two output streams; one packet means one render time; the hold flag exposes the older stream |
| M17 | wording; cause is DECISION | Lengths named as calibrated per recording (3.5, 5.6, 6.3, 7.1.3); the avatar rig keeps the loop lengths on a rail replay; the cause of the 31.7/20.5 against 25.8/24.7 cm difference is not established |
| M18 | fixed | 7.1.3 no longer contradicts 7.3.2; 7.1.2 claims only what the tested trajectories show; 7.3.2's bias and drift paragraph is an observation under named assumptions |
| smaller | fixed except C38 and D5 | Chapter 3 rounding sentence and "outward"; E.4 to 0.0001; Table E.1 range against depth; Appendix D registration note; Chapter 1 privacy sentence and "reviewed systems"; "full reported visibility" in 7.1.3, 7.5 and 9.1. Precision items (C38) and the bimanual wording (D5) remain the user's |

## Follow-up after the user's decisions (2026-09-07)

The user approved every recommendation of the correction pass (decision
log writing/v8/condensed/DECISIONS.md D-001 to D-004, eval/DECISIONS.md
E-028 to E-030). Reruns are additive reports; no historical report was
overwritten and no solver policy changed.

| ID | Status | Where and how |
|---|---|---|
| M02 | rerun DONE | eval/failure/moving_window_check.py --eligible-only selects every 45-frame window the harness rule admits before any error is scored (selection archived in eval/reports/*_recovery_eligible_selection.json, reports *_recovery_eligible.md). It returns exactly the five rail windows of Table 7.4 and the three loop windows of Table 7.5 and no other; the reference arm turns by at most 15.4 degrees in any of them, so no eligible moving outage exists. Section 7.3.2 says so and reports the loop wrist errors (recovery 1.5 cm in the right window from 661 against 2.2 and 2.4; 14.0 and 6.9 cm in the two windows from 1674, the error of the object estimate itself). Table 7.6 stays as the exploratory hand-carved comparison. 9.3 reworded |
| M03 | rerun DONE (rail); loop historical | v2/integration/validate_v2_r5.py pairs live frame f with reference f-lag and requires both clean (v2/tests/test_validator_pairing.py, six tests). Rerun on the archived original rail live dumps (v2/dataset/m03_rail_inputs.zip, manifest with SHA256) against a reference rebuilt with the solver of that run (audit_evidence/followup/m03_reconstruct.py, reproduces every historical angle): lag 5 (unchanged), 174 pairs instead of 179, worst group 3.90/23.25 degrees, azimuth 16.42/26.94, twist 7.04/15.09, elevation 1.45/2.30, flexion 0.41/1.18; the same two checks fail. Section 8.3 reports these; the loop run's live dumps were not found, so its figures stand with the first pairing and 8.3 and 9.1 say so |
| M05, M07 | retained by decision D-002 | The measured-only twist hold and the persistent two-link swivel prior stay as implemented and are described as such (5.3, 5.5); a universal hold or an enforced horizon is a separate implementation study |
| M06 (D2) | DONE | Section 2.6 states the preparation (order of the four checks, thresholds, depth memory seeding and 70/30 update, ray replacement, shoulder-midpoint branch); Appendix G gives the exact branching, fallbacks and output tags; constants checked against occlusion_ext.py on 2026-09-07. Chapter 5, Section 7.4 and Chapter 9 point at it; Chapter 9 names the untested occluded start and the live pelvis translation that still uses the original hips |
| M10, M12 | DONE (user-approved replacements) | The two verbatim Section 2.4 and 2.5 sentences replaced with the user's approved wording; exact find/replace pairs in writing/v8/condensed/notes_followup_ch2.md |
| M17 | cause settled by measurement (2026-09-07, D-005) | audit_evidence/followup/m17_segment_diagnostic.py: the 25.8/24.7 cm pair mixed the right upper arm with the LEFT forearm; the same-side, same-rule clean medians are loop right 25.8/25.5 cm and rail right 32.1/19.9 cm, raw against filtered within 0.07 cm, so rounding and filtering do not explain the gap. No anatomical truth exists; elbow localisation stays a hypothesis. Chapter 6 states the rail lengths (31.7/20.5 cm) beside the loop values as effective model lengths. The user measured the subject's arm on 2026-09-07: upper arm and forearm both about 25 cm, so the loop calibration is close to the anatomy and the rail split is consistent with the elbow landmark sitting farther along the arm; Section 6.3 and Chapter 9 (9.1, Table 9.1) say so, the rail recovery keeps its own lengths (D-005) |
| C38 | DONE | See PROF_COMMENTS_CHECKLIST.md C38 |
| D5 | DONE | Chapter 1 and 9.3 scope the bimanual claim (system covers both arms; one-handed primary evaluation; secondary bimanual evidence) |
| word target | DONE | Main body 29,977 words after the additions (Section 2.6, the rerun paragraphs) and trims in Chapters 1, 6, 7, 9; 149 pages |


## Final completion reconciliation, 2026-09-12

The opening verdict and M01-M18 describe the 2026-09-06 review and must be read
with the dated correction passes below it. They are preserved as evidence,
not a current unresolved-items list. D-035 to D-066 subsequently restructure
evaluation and settle notation; D-067 to D-071 complete supported corrections.

The current mathematical defect ledger is DETERMINED_DEFECTS.md. The principal
remaining reproducibility omission was Table 5.1: Chapter 5 now prints the swap,
levelling, mapped-marker conjugation and Person/Levelled wrist conversion.
Chapter 6 distinguishes proper frame relations from handedness-changing maps,
explains local object versus global rig application, and expands the already
valid Scene factor of equation 6.5 without double-applying levelling. Its scene
point example now has dimensionally correct homogeneous coordinates. Chapter 3
corrects the destination named beside equation 3.3 and bounds its inverse claim
to the kinematic chain. Appendix E keeps both frame labels in its worked trace.

M01/M02/M09/M15/M18 now refer to the restructured evaluation, not the old table
and section numbers quoted above. Physical endpoint-distance error remains
separate from line scatter; the current synthetic windows use the unmasked
model reference; natural labels are visible proxies with unquantified label
uncertainty. A clean proxy offset is not a resolution threshold. M17's actual
capture proportions are configuration facts; the thesis does not apportion
the rendered discrepancy among the confounded contributors. M03's corrected
rail comparison and unreproducible historical loop comparison remain distinct.

No current completion correction changes an experimental statistic or reopens
Chapter 10. The Figure 2.5 metric glyph is corrected to use the scaled object
detection, and Figure 6.4 identifies its four pre-levelling frames. Current
bibliography assembly is handled separately under D-069; structural check_refs
counts alone never verified literature citations.

UNRESOLVED_ITEMS.md is the current assumption/limitation and manual-QA list.
The spawn-axis coincidence, physical mounting assumptions, proxy limitations,
confounded capture configuration and missing historical loop live dumps remain
explicitly bounded. DELIVERY_2026-09-12.md records final build and test outputs;
no earlier test result above should be interpreted as a rerun of that build.

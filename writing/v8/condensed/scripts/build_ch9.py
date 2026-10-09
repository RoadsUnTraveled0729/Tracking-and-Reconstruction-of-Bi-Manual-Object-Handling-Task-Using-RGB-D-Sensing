#!/usr/bin/env python3
"""Build writing/v8/condensed/Chapter_9_Discussion.docx.

Thesis revision of 2026-09-11, Phase 2A (author's specification in
writing/v8/condensed/REVISION_2026-09-11_BRIEF.md, section 4). Chapter 9
stays "Chapter 9: Discussion" and interprets Chapters 7 and 8 instead of
repeating their tables. Fixed structure: 9.1 Object Reconstruction and
Physical-Route Error Sources, 9.2 Human-Object Spatial Reconstruction,
9.3 Landmark Failure and Object-Assisted Recovery, 9.4 Torso and Root
Failure and High-Confidence Landmark Errors, 9.5 Single-View
Observability and Model Limits, 9.6 Real-Time and Causal Implications,
9.7 Scope of the Evaluation with Table 9.1. Conclusions and future work
are Chapter 10 (build_ch10.py).

Every number here is printed in Chapters 2 to 8 with the section cited,
or comes from a pinned report already named in the source comments
below. The reasoning the Chapter 7 revision exported (section (b) of
writing/v8/condensed/notes_revision_ch7.md) is carried here in this
chapter's flow. Cross-references follow the Chapter 7 structure of
D-029 and D-038: the object segment lengths and the fitted-line scatter
are Section 7.2, the rendered joint errors under valid landmark
measurements Section 7.3 with its two task subsections, the wrist to
marker spatial check Section 7.3.3, the synthetic landmark removal
Section 7.4.1, the natural occlusion labels Section 7.4.2, the
offline-causal comparison Section 8.3, the runtime Section 8.4 and the
remaining validation gap Section 8.5. Chapter 7 table and figure numbers
are deliberately not cited from this chapter: Section 7.2 is still
gaining tables and every Chapter 7 table and figure number shifts with
it, while the section numbers are stable. Subsection pointers therefore
carry the references instead.

Chapter 7 integration pass of 2026-09-12 (CH7_INTEGRATION_FIXLIST.md,
section build_ch9.py; D-036, D-037, D-038, D-039). Claims whose Chapter 7
evidence the restructure removed are withdrawn here rather than
renumbered: the tracked height histogram against the 3.8 cm rail tape;
the 6.5 cm model wrist to rail-line separation; the rendered hand 15.2
and 12.1 cm from the measured wrist; the handover
effective segment lengths; the object-estimate column of the natural
occlusion set; frames 1462 and 1890 and their per-frame values; the rail
clean-frame 9.1 against 6.9 cm and the rail cuff-seam label set, both
excluded by D-033; the 19.4 against 0.8 cm hip depth split and the
failure-coverage percentages; the 63-frame left-arm rejection of the
handover recording; the up to 23 cm model wrist steps at the hip repair
edges and the 417 repaired frames; the hip-hold comparison and its six
values; the label sets of 21 and 20 frames; the five synthetic windows of
3.0 to 6.0 degrees of arm travel and the 342 eligible rail frames. The
Section 7.4.1 description now matches the rebuilt subsection: three
windows of 45 frames on the handover recording, selected by reference
wrist excursion, with no eligible window on the single-hand recording.
Solver verification is Appendix H under D-037 and is not discussed here.

Section 9.2 carries the two wrist quantities of D-039 to D-043. The bare
kinematic model wrist error and the rendered Unity rig wrist error are
defined separately and never described interchangeably, both against the
accepted raw measured wrist that D-040 fixes as the evaluation reference.
The recording-wide bare model values carry any general statement about
the accuracy of the kinematic model, and the Unity capture subset values
appear only in the contrast with the rendered rig, which is frame-matched
to them (D-041). The author's conditional reading is applied to the
handover recording only, where the bare model wrist is about a centimetre
from the measured wrist and the rendered rig wrist five to seven
centimetres from it: most of the further discrepancy appears downstream of
the kinematic solve, in the rig and display path, and no share of it is
assigned to any stage inside that path. D-043 permits the mismatched rig
proportions to be named as a possible part and forbids quantifying it.
D-042 keeps the single-hand rail recording out of that reading and out of
any numerical comparison with the handover values, because every accepted
frame of it carries a held forearm twist and a constrained root; its
6.78 cm bare model value is therefore not printed here either. The older
0.96 and 1.17 cm figures do reproduce from eval/reports/r7_handover.json,
but under a whole-recording, filtered-wrist and almost ungated definition,
so they are a different quantity and no longer appear in this chapter.

Two later decisions also land here. D-044 defines the task phases once,
in Section 2.1: object acquisition, carry, lift, slide and release. Section 9.1 names
the carry, the lift and the slide of the object route with one pointer to
that definition and does not introduce the terms independently. D-045
confirms that the coarse rail-height cross-check against the 3.8 cm
physical rail height is dropped for good, superseded by the W2 to W3
separation of Section 7.2, which is measured for the marker centre
itself; no claim of this chapter rests on the dropped cross-check. D-046
moves the loop detection coverage to Section 7.4.2, which is now where it
is established and where this chapter cites it; Section 9.1 keeps the
implication for the recovery and introduces no count of its own.

Locked facts applied: the physical route is a tape measurement and is not yet
registered into the world frame, so no point-to-path distance exists
(facts 2 and 3); the approximately 16 cm wrist-to-marker distance is an
approximate scalar for the single-hand grip (facts 4 and 5); the manual wrist
labels are clicked image points (fact 6); object information supplies an
additional geometric constraint (fact 8); the causal result is a replay
at the recorded pace (fact 9). Both failure-mode screenshots stay (rule
3 of skill_set/thesis-structure-rules.md); the marker figure is cited
first, in Section 9.1, so it is Figure 9.1 and the landmark figure 9.2.
Table 9.1 gains a row for the unregistered physical route and one for
the manual-label uncertainty.

Author's instruction of 2026-09-12: the depth-implied marker size of
43.4 to 43.8 mm is dropped from the thesis. It was a diagnostic this
chapter introduced on its own, with no method and no result behind it in
Chapters 2 to 8, and the rebuilt object evaluation already sets the
reconstruction against direct physical route references. The discussion
and its Table 9.1 row are removed, nothing replaces the number, and no
analysis was made to preserve it. Locked fact 1 is unaffected in its own
terms: the markers are 45 mm, the pipeline uses 45 mm, and Table 2.1 of
Chapter 2 is where that is stated. This chapter now prints no marker size
at all. The comment above the affected paragraph records what the
removal leaves stale in build_appendix.py.

Round-1 fix pass of the final review loop (2026-09-11,
writing/reviews/final_2026-09-11/round1/FIX_DECISIONS.md; the item log is
FIXES_ch9-10-app-fm.md in the same directory). Applied here: the marker
branch fails by returning no pose while a wrong-pose decode stays
possible in principle (decision G4); the labelled left failure frames of
the loop recording are never called one early window (locked fact 7);
the geometric detectors are silent over the first hundred frames of the
slide and not through it; the camera axis is "the optical axis" and the
hip step "the hip depth preparation" everywhere (decision G1); the
unpinned "about 80 degrees" is removed (decision G2); Sections 9.2, 9.3
and 9.4 keep the reading and drop the numbers Section 7.3 and Section
7.4.2 already print (decision G3); the chapter closes by handing on to
Chapter 10 (decision G5); the wall marker's unverified mounting reaches
Section 9.5 and Table 9.1. Two items of that pass were superseded by the
Chapter 7 integration pass above: the detectors sentence lost its frame
numbers with the failure-coverage passage of old Section 7.1, and the
synthetic sentence it treated was replaced outright.
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches

H1, H2, P = "h1", "h2", "p"
CAP, TBL, LIN, IMG = "cap", "tbl", "lin", "img"

REPO = Path(__file__).resolve().parents[4]
FIG = REPO / "writing" / "v7" / "figures"

F_MARKER, F_LANDMARK = 1, 2

content = [
(H1, "Chapter 9: Discussion"),

(P, 'This chapter reads the results of Chapters 7 and 8 against the sensing, the model and the carried state. Sections 9.1 and 9.2 separate the error sources of the object route and of the person reconstructed with it. Sections 9.3 and 9.4 read the recovery, the torso and the high-confidence landmark failures. Section 9.5 sorts the limits that remain, Section 9.6 reads the causal comparison, and Section 9.7 bounds the evaluation.'),

(H2, "9.1 Object Reconstruction and Physical-Route Error Sources"),

# Object segment lengths and errors: D-036 and the pinned
# audit_evidence/ch7_restructured/object.json, printed in Section 7.2.
# Rail recording, physical / reconstructed / absolute: 25.5 / 24.36 /
# 1.14, 3.5 / 4.03 / 0.53, 37.5 / 38.59 / 1.09 cm. Handover recording:
# 25.5 / 22.68 / 2.82, 3.5 / 4.35 / 0.85, 37.5 / 40.33 / 2.83 cm. The
# detector-selection bands of the same file are 23.95 to 25.15, 3.76 to
# 4.70 and 37.78 to 38.87 cm on the rail recording and 22.42 to 24.00,
# 4.28 to 4.76 and 38.78 to 40.60 cm on the handover recording; the
# orchestrator's instruction of 2026-09-12 requires the band beside every
# length. The tape values are locked fact 2 (user measurement, message of
# 2026-09-11) and the waypoint roles are D-036. Sign invariance across
# the detector perturbation family is object.json, sensitivity block.
# Segment directions: object.json phase_confirmation
# segment_axis_dominance, depth for W1 to W2, vertical for W2 to W3,
# lateral for W3 to W4.
(P, 'Section 7.2 sets the reconstructed object track against a physical reference for the first time in the evaluation. The reference is a set of tape measurements between marker-centre positions at the four waypoints of the route. The route itself is not registered into the calibrated world frame, so the comparison is of endpoint separations and not of distances from the reconstructed track to the physical path. Registration would need the route expressed in the frame of the desk marker, measured from that marker or carried there by a further marker.'),

(P, 'The two recordings agree on the direction of the disagreement. The three segments are the carry, the lift and the slide of the task phases defined in Section 2.1. The carry reconstructs short on both recordings, by 1.14 centimetres on the rail recording and by 2.82 on the handover recording, while the lift and the slide reconstruct long on both, by between 0.53 and 2.83 centimetres. Each length carries a band that follows from the detector settings which identify the waypoints. On the rail recording the three reconstructed lengths lie between 23.95 and 25.15 centimetres against a measured 25.5, between 3.76 and 4.70 against 3.5, and between 37.78 and 38.87 against 37.5. On the handover recording the same three bands run from 22.42 to 24.00, from 4.28 to 4.76 and from 38.78 to 40.60 centimetres. The direction of each disagreement holds across every setting in that family, so the choice of threshold sets how large the disagreement is and not which way it goes.'),

(P, 'That pattern can be read only so far. The waypoints at the foot and at the top of the lift are single transition samples, because the object does not pause on either side of the rise, so each of them rests on the depth of one frame. The band on the 3.5 centimetre segment is almost a centimetre wide on the rail recording, so its relative error is not a precise quantity and is not quoted as one. The handover recording differs from the tape by more than the rail recording on every segment. The two recordings differ in more than the handover itself, so this comparison does not establish handover as the cause. The direction of the pattern is not traced to a mechanism either: it is a property of the measurements reported, and these recordings do not divide it among the sensing, the calibration and the identification of the waypoints.'),

# Locked fact 3 and MATH_LOGIC_REVIEW.md M01: a line fitted to the
# tracked samples is a within-recording description, not an accuracy
# reference. The fitted-line scatter itself is Section 7.2
# (object.json scatter block, rail 0.83 / 2.12 / 2.92 cm over 248
# samples and handover 0.39 / 1.44 / 2.82 cm over 539); this chapter
# reads it and does not restate it. The three groups of contributors are
# not apportioned by any result of this thesis.
(P, 'The object also slides along a straight guide, so its output can be set against a line fitted to its own samples. Section 7.2 reports the spread of the marker centre about that line for each slide as a within-recording comparison. A line fitted to the tracked samples is not a physical reference: the residual measures only the transverse spread about that line, and it is blind to an error along it and to any offset the fit absorbs.'),

(P, 'That spread has three groups of possible causes, and the recordings do not divide it among them. The first group is the motion the subject performed: hand tremor, a path followed by hand rather than by a guide, and overshoot and undershoot at the ends of a leg. The second group is the physical setup: the flatness of the rail and of the table top and the tolerance of its placement and levelling. The third group is the sensing: how precisely the detector places the four marker corners, the viewing angle of the marker face, the calibrated camera-to-world transformation, and image and depth uncertainty. Nothing reported here shows one group to dominate.'),

# The registration statement that used to stand here has moved into the
# opening paragraph of this section, which is where Section 7.2 now
# raises it (CH7_INTEGRATION_FIXLIST.md 9-2).

# Removed on 2026-09-12, by the author's instruction of that date: the
# depth-implied marker size cross-check, a side of 43.4 to 43.8 mm read
# from the aligned depth against the 45 mm printed square
# (eval/reports/r6b_marker_scale.json and r7_marker_scale.json,
# diag_depth_implied_mm 43.4 and 43.7 on the rail recording, 43.6 and
# 43.8 on the handover recording). The author ruled that the diagnostic
# is dropped unless a claim surviving the Chapter 7 restructure requires
# it. It was introduced in Chapter 9 alone, with no method and no result
# for it anywhere in Chapters 2 to 8, and the rebuilt Section 7.2 now
# carries direct physical route references. No claim of this chapter
# rested on it, so it is withdrawn together with its Table 9.1 row, with
# no substitute number and no new analysis in its place. Locked fact 1
# keeps the 45 mm marker size itself; its printed home is Table 2.1 of
# Chapter 2 and this chapter no longer needs to restate it. Two pointers
# into the removed material belong to other builders and are reported to
# the orchestrator rather than edited here: Appendix E.1 says the depth
# patch stored beside each marker pose is kept because "Section 9.1 uses
# the pair" (build_appendix.py), which is now false.
# The orientation sentence that closed the paragraph is kept and given a
# lead-in of its own. It does not rest on the depth reading: Chapter 4
# hands the claim here ("No second measurement chain checks the streamed
# orientation ... which Section 9.1 takes up", build_ch4.py) and Section
# 9.7 lists it among the missing references.
# Removed on 2026-09-12: the tracked height histogram against the 3.8 cm
# rail tape (0.2 and 0.6 cm above it). The rebuilt Chapter 7 prints
# neither the histogram nor the two rail heights, and
# audit_evidence/ch7_restructured/object.json carries no height
# cross-check, so the claim has no home in the thesis and is withdrawn
# rather than moved (CH7_INTEGRATION_FIXLIST.md 9-3).
(P, 'The object output also carries an orientation, and the evaluation does not reach it. No second measurement chain validates the streamed marker orientation, so the results of Section 7.2 speak for position alone.'),

# Failure mode: object marker blocked. D-046: the loop detection
# coverage is recomputed and pinned in
# audit_evidence/ch7_restructured/loop_detection.json, and Section 7.4.2
# is its printed home, which states that the object marker is detected on
# 2058 of the 2099 frames, that 40 of the 41 frames without it lie in the
# two-hand transfer on the desk and the remaining one at its near edge,
# and that every labelled frame carries a detected marker. This chapter
# therefore no longer introduces the count. It cites Section 7.4.2 and
# keeps the implication, which is its own work. The previous source here
# was eval/output/recording_20260825_222315_scaled_object_world.csv, an
# evaluation output rather than a pinned report, and it is superseded.
# Two counts exist in the pinned file and must not be mixed: 2058 frames
# on which the extractor returned a pose, which is what Chapter 7 prints,
# and 2046 accepted samples under the stricter rule of Section 7.2.
# The rail and handover recordings hold the marker in view almost
# throughout, which Chapter 4 prints for the rail recording in the
# Figure 4.2 caption (899 of 900 frames) and Section 7.2 gives for both
# as accepted-sample counts. No number for either is restated here.
# Chapter 7 writes "the two-hand transfer on the desk" rather than "the
# desk handover", so that the stretch is never confused with the handover
# recording, and this chapter and its figure caption follow that.
# Decision G4 of the round-1 fix pass (FIX_DECISIONS.md): Chapter 7
# Section 7.4 and this paragraph must agree that the observed failure is a
# lost detection while a wrong-pose decode stays possible in principle
# (Appendix E, the two-lobe ambiguity and its discriminator). The pinned
# reports were searched for a recorded wrong-pose decode on the three
# recordings and none carries one; the only pinned ambiguity count is
# eval/reports/r4_stage2_validation.md, "Object ambiguity: 1308 frames
# gravity-resolved, 0 unresolved", and that is a fourth recording. The
# sentence therefore says what the reports show ("none is recorded in the
# pinned reports") and does not claim an observation nothing scored.
(P, f"On these recordings the marker branch fails by returning no pose. A partly covered square can in principle decode with a wrong pose, the two-lobe ambiguity of Appendix E, and the natural failure windows are where such a decode would appear (Section 7.4); none is recorded in the pinned reports of these recordings. Figure 9.{F_MARKER} shows a detected frame just before the two-hand transfer on the desk of the loop recording and a lost frame inside it, where a finger crossing the border of the printed square is enough to lose the pose. Every frame of that recording without a marker pose falls in that transfer or at its near edge (Section 7.4.2)."),

(P, f"The rail and handover recordings hold the marker in view almost throughout, so the loss belongs to the transfer rather than to the marker branch in general. Across that stretch there is no object information to use at all, so an arm rejected there would leave the layer of Chapter 5 with nothing to anchor on, which is the limiting case discussed in Section 9.3. The labelled frames of Section 7.4.2 all carry a detected marker, so the comparison reported there lies outside the gap."),

(IMG, FIG / "ch9_fig_marker_blocked.png", 6.3),
(CAP, f"Figure 9.{F_MARKER}. Object marker loss on the loop recording. Panel (a), frame 1060: both markers are detected, with their four corners outlined. Panel (b), frame 1073, inside the two-hand transfer on the desk: a finger crosses the top-right corner of the printed square and no object pose is returned."),

(H2, "9.2 Human-Object Spatial Reconstruction"),

# Locked facts 4 and 5 and D-038: the approximately 16 cm physical
# reference (user measurement, message of 2026-09-11,
# REVISION_2026-09-11_BRIEF.md section 3 fact 4) and the verified medians
# of eval/reports/r7_handover.json, the *_fk_wrist_to_marker_at_cube_cm
# medians. D-038 keeps the comparison as Section 7.3.3, Human-Object
# Spatial Check, as an approximate external physical check of the
# magnitude of the reconstructed separation and nothing stronger: the
# single-hand medians 15.77 and 14.08 cm may be read against the
# approximately 16 cm reference, the transfer values 17.91 and 15.85 cm
# may not, and the check is neither an anatomical wrist reference nor a
# test of the three-dimensional hand-object offset of Chapter 5.
(P, 'The distance from the model wrist to the marker centre is the one quantity of the human-object pair with an external physical reference. The distance from the location of the MediaPipe wrist landmark to the marker centre was measured with a tape as about 16 centimetres for a normal single-hand grip, and Section 7.3.3 sets the reconstructed separation against it. The reconstructed median is 15.77 centimetres while the right hand holds the cube alone and 14.08 centimetres while the left hand holds it alone. The transfer values, 17.91 and 15.85 centimetres, are not graded against the reference, because the grip geometry changes while the cube passes between the hands. The check is approximate and scalar. It shows that the reconstructed separation between the hand and the object is of the right magnitude under a normal single-hand grip. It is neither an anatomical reference for the wrist nor a test of the three-dimensional hand-object offset the recovery of Chapter 5 carries.'),

# The comparison mixes both branches; locked facts 4 and 8 forbid
# attributing it to MediaPipe or to ArUco alone, and the scalar does not
# constrain the direction of the Chapter 5 offset.
(P, 'Agreement with the approximately 16 centimetres cannot be assigned to one branch because the distance depends on both branches. It depends on where MediaPipe places the wrist, the depth sampled at the wrist pixel, the root and torso reconstruction used to interpret the angles, the effective segment lengths, the marker pose and the calibrated transformation into the world frame. The comparison also depends on the grip of the subject, which varies between episodes, and the precision of a tape measurement on a clothed arm. A difference of one or two centimetres is small beside the terms listed above, none of which this thesis measures separately, so neither branch can be blamed for it. The scalar says nothing about direction either, while the recovery of Chapter 5 carries a three-dimensional offset.'),

# The two wrist quantities, D-039 to D-043. Every value of the next four
# paragraphs is printed in Chapter 7 with the section cited: Section 7.1
# fixes the evaluation reference wrist under D-040, Section 7.3
# distinguishes the bare kinematic-model error from the rendered rig
# error and states the capture configuration under D-043, Section 7.3.1
# states the held twist and constrained root of the rail recording under
# D-042, and Section 7.3.2 prints both scopes of the bare-model wrist
# error under D-041, the held-twist composition of the capture subset and
# the twist regimes. The underlying pinned file is
# audit_evidence/ch7_restructured/bare_model.json. This chapter keeps the
# reading and leaves the definitions and the frame counts to Chapter 7,
# printing only the values the reading needs (decision G3 of the round-1
# fix pass). Note on the decision text: D-041 and D-043 were written
# before Chapter 7 was renumbered and say Table 7.2 where the handover
# rendered-rig table is now Table 7.4. The older 0.96 and 1.17 cm values
# of eval/reports/r7_handover.json do reproduce under their own
# whole-recording, filtered-wrist and almost ungated definition, so they
# are a different quantity and are not printed here.
(P, 'Section 7.3 distinguishes two wrist quantities, and much of the reconstruction error lies between them. The kinematic model wrist is the one the solved angles place; the rendered rig wrist is the one the avatar draws, after the display filtering and the rig and coordinate mapping of Chapter 6. Both are measured against the same evaluation reference, the accepted raw landmark wrist of Section 7.1.'),

(P, 'On the frames the Unity capture of the handover recording saved, the kinematic model wrist lies 0.83 centimetres from the measured wrist on the right arm and 2.34 on the left. The rendered rig wrist on those same frames sits 5.7 and 6.9 centimetres from it (Section 7.3.2). Across the valid-landmark frames of the whole recording the kinematic model wrist lies a median of 1.03 centimetres from the measured wrist on each arm, which is the figure that describes the model itself. The two scopes answer different questions. Section 7.3.2 states why they are not interchangeable: the captured subset holds a larger share of held-twist frames than the recording does, so it is not a representative sample of the recording.'),

(P, 'The kinematic solve on that recording reproduces the wrist it was given to about a centimetre, so most of the further discrepancy appears downstream of the solve, in the rig and display reconstruction path. Where inside that path it arises is not isolated. Part of it may come from the rig proportions, since both captures ran the avatar with the arm lengths of the loop recording rather than with the lengths calibrated on the recording being replayed (Section 7.3). That is a fact about how the capture ran and not a measured share. The rendered figures are end-to-end results under that configuration. They do not separate the stages of the display path or assign any part of the difference to one stage.'),

(P, 'Those distances depend on whether the forearm twist is measured or held. Section 7.3.2 separates the two cases. Where the twist output is measured, the kinematic model wrist stays within a centimetre of the measured wrist. Where it is held, that distance increases to between two and three centimetres. The elbow barely changes between the cases. The reason is geometric. A held twist turns the forearm about the upper-arm axis, which carries the wrist and leaves the elbow where it is. A twist the current frame cannot check therefore affects the wrist rather than the joint above it. The left arm of the captured subset holds the twist on more of its frames, which is why its kinematic model wrist distance is the larger of the two.'),

# The Unity hand beside the cube, and D-042 on the rail recording.
# Removed on 2026-09-12: the 15.2 and 12.1 cm values of old Section 7.3.
# Decision G2 of the round-1 fix pass already recorded that no committed
# record of the two survives, and the rebuilt Chapter 7 prints neither
# (CH7_INTEGRATION_FIXLIST.md 9-8). The live printed homes are Section
# 6.4, which works the difference through on two frames of the rail
# recording (14.1 cm on frame 114 and 6.4 cm on frame 700) and names its
# parts, and Section 7.3.1, whose rendered wrist median over the captured
# single-hand frames is 12.0 cm. D-042: the rail recording's bare model
# wrist value is not a kinematic closure figure, because bare_model.json
# records a held forearm twist on all 100 accepted frames and a
# constrained root on all of them, so the value is not printed and no
# numerical comparison is drawn with the handover figures.
(P, 'The single-hand rail recording does not support that reading, and Section 7.3.1 states why. The right forearm twist is held on every valid-landmark frame and the root is constrained on every one. A kinematic model distance there would describe that output state rather than how closely the kinematic model reproduces its measured inputs, so none is reported. That recording shows the rendered end of the path. The Unity hand lands beside the cube rather than on the measured wrist, a median of 12.0 centimetres from it over the captured frames (Section 7.3.1). Section 6.4 works the same difference through on two frames and gives its parts: a nearly straight elbow holds the twist, the rig shoulder sits deeper in the scene than the measured shoulder landmark, and the avatar keeps the loop arm lengths. Those results are not directly compared with the handover results.'),

# Effective segment lengths: loop 25.6 / 25.2 and rail 31.7 / 20.5 with
# the subject's direct measurement of about 25 cm for both segments
# (Section 6.4; D-004 and D-005, user measurement of 2026-09-07). The
# handover effective lengths 24.1 / 23.3 right and 25.2 / 22.3 left were
# dropped with old Section 7.3 and are not cited here
# (CH7_INTEGRATION_FIXLIST.md 9-9).
(P, 'The segment lengths are effective lengths of the landmark track and not measurements on the body. Each recording calibrates its own pair, and the rail recording\'s 31.7 and 20.5 centimetres split about the same total very differently from the loop recording\'s 25.6 and 25.2, against about 25 centimetres for both segments measured on the subject (Section 6.3). The rail split is consistent with the elbow landmark sitting farther along the arm there.'),

(H2, "9.3 Landmark Failure and Object-Assisted Recovery"),

# Locked fact 8 and the recovery vocabulary of the brief: object
# information supplies an additional geometric constraint; the outcome
# also rests on the offset, the segment lengths, the chain constraints,
# the two-link geometry of Section 5.5 and the carried state.
(P, 'Object information supplied an additional geometric constraint on the frames where an arm was rejected, and that is the whole of its role. The wrist the recovery returns also depends on the hand-object offset carried from earlier frames, on the calibrated segment lengths, on the chain constraints, on the two-link geometry of Section 5.5, and on the state the layer holds. A smaller distance to a manual wrist label does not prove that the arm configuration is correct.'),

# Offset lag and the regrasp: the offset gain is 0.02 (Table 5.1,
# Section 5.3), so the estimate trails a shifting grip; the loop-left
# medians printed in Section 7.4.2 are object-assisted 13.1, hold-last
# 12.7 and plain 12.3 cm (audit_evidence/ch7_restructured/natural.json,
# from eval/reports/r5_recovery_labeled.json). The object-estimate column
# of the old table, 13.2 cm from the label, is not in the rebuilt
# subsection and is not cited here (CH7_INTEGRATION_FIXLIST.md 9-10); the
# ranking has also changed, since the plain solve is now the nearest of
# the three on that arm. Locked fact 7: those medians are taken over the 16
# labelled left failure frames, which are 14 samples from frames 1427 to
# 1492 at five-frame spacing plus the two frames 1777 and 1787
# (r5_recovery_labeled.md rows; the second pair sits in the separate
# arm_L 1777-1798 window of eval/reports/r5_failure_mask.md), so they are
# never described as one early window. Decision G3: only the one median
# the reading needs stays here, the other three are Section 7.4.2's.
# Regrasp during a failure:
# eval/reports/r5_object_conditioned_recovery.md section 7.
(P, 'The offset is the first reason the constraint can be wrong. It is fitted while the hand is visible and updated slowly. A grip that shifts faster than the update therefore leaves the estimate behind. A failure freezes whatever it held (Section 5.3). A regrasp during a failure has no clean wrist measurement to fit a new offset on, so the old one is carried into a grip that no longer matches it. The frozen offset was already wrong over the labelled left failure frames of the loop recording, which run from frame 1427 to frame 1787 in two separate windows, and the recovery inherits that error. Over those frames the object-assisted solve is the farthest of the three methods from the manual wrist label, at 13.1 centimetres against 12.7 for the held angles and 12.3 for the plain solve (Section 7.4.2).'),

# Straight arm along the view axis. Removed on 2026-09-12: frame 1462
# and its 64.4 degree elbow. The detail came from old Figure 7.14, and
# the rebuilt Section 7.4.2 prints per-arm summary statistics only and
# names no frame (CH7_INTEGRATION_FIXLIST.md 9-11). The mechanism that
# remains is the two-link geometry of Section 5.5, which states that near
# full extension a small error in the wrist estimate becomes a large
# error in the flexion angle.
(P, 'Geometry along the optical axis is the second reason. With the arm pointing at the camera, the wrist depth is the coordinate the sensing constrains least, and a small error in the estimated wrist moves the reachable elbow a long way. Where the frozen offset places the wrist too close to the shoulder, the two-link solve of Section 5.5 bends an arm that is nearly straight, because near full extension the shape of the triangle stops depending smoothly on its longest side.'),

# The right arm of the loop recording: object-assisted 5.2, plain 11.4
# and hold-last 17.6 cm from the manual proxy over n = 4 retained frames
# (Section 7.4.2; audit_evidence/ch7_restructured/natural.json, from
# eval/reports/r5_recovery_labeled.json). Removed on 2026-09-12: frame
# 1890 and its 14.0 / 5.0 / 15.2 cm values, which came from old Figure
# 7.15, and the claim that the gain comes from the chain constraints and
# not from the estimate, whose comparator was the deleted object-estimate
# column (CH7_INTEGRATION_FIXLIST.md 9-12).
(P, 'The same constraints can carry the solve toward the label instead. On the right arm of the loop recording, where the whole arm is rejected, the object-assisted solve sits a median of 5.2 centimetres from the manual wrist label against 11.4 for the plain solve and 17.6 for the held angles (Section 7.4.2). Object information supplied the constraint there, and the chain constraints and the calibrated lengths shaped what the solve did with it. The retained set is four frames, so it fixes no general ranking. On these two windows the recovery improved on the baselines only where the detected or held wrist drifted farther than the error of the frozen offset. The constraint can also be missing: a marker gap inside a wrist gap leaves the layer nothing to anchor on.'),

# State and history. Removed on 2026-09-12: the rail clean-frame
# comparison, recovery 9.1 cm against plain 6.9 cm from the label. D-033
# excludes the rail label set from Section 7.4.2 altogether, so those
# values are printed nowhere in the thesis (CH7_INTEGRATION_FIXLIST.md
# 9-13). Also removed: "the worst frames of Table 7.2 come from the same
# rules". Old Table 7.2 was the synthetic-mask wrist deviations; the
# rebuilt synthetic tables report per-window, per-method medians, p95 and
# maxima and locate no frame within a window, so nothing printed supports
# a claim about which frames of an outage are the worst
# (CH7_INTEGRATION_FIXLIST.md 9-14). The frames 7 to 24 mask and the
# twists about 40 degrees apart are printed in Section 8.3; the 15
# degrees per frame limit and the constrained tag are the design
# constants of Section 5.5.
(P, 'State carried from earlier frames reaches past the failure windows themselves. The failure mask removes the right arm on frames 7 to 24 of the rail recording, and the hold of Section 5.5 freezes the twist solved there until the elbow bends past the release after the gap. Frames on which every landmark is measured therefore still carry a twist decided during the gap. Section 8.3 shows the size of that dependence between the two processing paths, which froze shoulder twists about 40 degrees apart on this recording and kept them apart afterwards. When an outage begins, the twist the rebuilt arm needs differs from the held one. The rate limit of Section 5.5 admits 15 degrees of change per frame. The group therefore stays marked constrained until the limited and the solved values agree again.'),

# The rebuilt synthetic comparison: the handover recording, three windows
# of 45 frames selected by reference wrist excursion 0.6, 2.8 and 5.1 cm
# before any method was scored, and no eligible window on the single-hand
# recording (Section 7.4.1, D-032;
# audit_evidence/ch7_restructured/synthetic.json). The reading of the
# three tables is Section 7.4.1's own: no method is closest on every
# window and joint; object assistance reduces the largest wrist deviation
# in the intermediate- and higher-motion windows and increases the elbow
# deviation in the higher-motion window; the lower-motion window favours
# the direction memory. Replaces the five windows of 3.0 to 6.0 degrees
# of arm travel on the rail recording (CH7_INTEGRATION_FIXLIST.md 9-15).
(P, 'The synthetic comparison of Section 7.4.1 measures something narrower than a ranking of the methods. It removes the right elbow and wrist inputs of the handover recording over three windows of 45 frames. The windows were chosen before any method was scored, by how far the unmasked reference wrist travels within each one, from 0.6 centimetres in the quietest to 5.1 in the most active. The single-hand recording offers no window in which the root and the arm are both fully measured under those conditions, so the slow case that recording would have provided is not part of the comparison.'),

(P, 'No method is the closest to the unmasked reconstruction on every window and joint. Object assistance reduces the largest wrist deviation in the two windows with more motion and increases the elbow deviation in the most active of them, while the quietest window favours the direction memory. The comparison is therefore window-dependent. The natural failure windows of the loop recording show a different result for each arm: the same layer on the same parameters improves on both baselines in one window and on neither in the other.'),

(H2, "9.4 Torso and Root Failure and High-Confidence Landmark Errors"),

# Hidden hips and the desk, rail or hand depth: the worked example of
# Section 3.5 decodes the root frame to a 32.1 degree pitch on frame 533
# because the hips read 0.99 m against 1.31 and 1.36 m at the shoulders.
(P, 'The root frame is the reference the arm angles are read against, and it rests on two landmarks the desk hides. A hip pixel that falls where the pelvis meets the rail takes the depth of the rail, and a hand or the cube in front of the pelvis does the same. The worked example of Section 3.5 shows the consequence: the root frame of an upright subject decodes to a pitch of 32.1 degrees because the hips read 0.99 metres where the shoulders read 1.31 and 1.36.'),

# Steady but wrong: both hips take the rail depth together, so a test
# that looks for a jump cannot see the offset. Frame 533, the worked
# example of Section 3.5, lies between the two torso events of
# eval/reports/r6b_failure_events.csv and inside no event of any entity,
# so no detector rejects it. Removed on 2026-09-12: the 19.4 cm against
# 0.8 cm hip depth split and the frame at which the detectors fire. The
# failure-coverage passage of old Section 7.1 carried both, and the
# rebuilt chapter prints neither, nor does it print the frame at which
# the slide starts (CH7_INTEGRATION_FIXLIST.md 9-16).
(P, 'A wrong measurement is not always an unsteady one. On the rail recording both hips take the rail depth together, so the hip line stays plausible and nothing steps between frames. The geometric detectors of Section 5.2 do not reject every frame on which the hips are wrong: the worked example of Section 3.5 is a frame that no detector rejects while the root frame is pitched by 32.1 degrees. A detector that looks for a jump cannot see an offset the two landmarks share, which is the reason the tests of Section 5.2 look at geometry.'),

# High-confidence misplaced landmarks: visibility 0.57 above the 0.50
# visibility gate of Section 2.3, from
# writing/v7/figures/src/r5_ch9_landmarks.json
# (frame 1818: L14 = 0.566, L16 = 0.902); the segment-length test on
# frames 1775 to 1825, upper arm 47.2 cm against a clean 25.8
# (eval/reports/r5_failure_mask.md, arm_R window). Removed on 2026-09-12:
# the left arm of the handover recording rejected on 63 frames after the
# release. That was an old Section 7.3 result; the rebuilt Section 7.3.2
# reports accepted-frame counts and no rejection narrative
# (CH7_INTEGRATION_FIXLIST.md 9-17).
(P, f"The landmark detector reports a position on every frame, even when that position does not match the body part. Figure 9.{F_LANDMARK} shows the difference on two frames of the loop recording. On the second frame, the hand holds the cube in front of the chest and the elbow landmark has slid onto the hand, at a reported visibility of 0.57, above the 0.50 visibility gate of Section 2.3. A confidence threshold cannot catch that failure and the segment-length test can: the upper arm reads 47.2 centimetres there against a clean 25.8. An arm that fails this way while it holds nothing has no object to be constrained by."),

(IMG, FIG / "ch9_fig_landmark_failure.png", 6.3),
(CAP, f"Figure 9.{F_LANDMARK}. Landmark tracking failure on the loop recording. Panel (a), frame 1698: the right elbow and wrist landmarks sit on the elbow and the wrist. Panel (b), frame 1818: the elbow landmark has moved onto the hand, at a reported visibility of 0.57 against 0.90 for the wrist, both above the 0.50 visibility gate."),

# Repair transitions. Removed on 2026-09-12: the 417 repaired frames,
# the three frame ranges 644 to 648, 892 to 894 and 1058 to 1061, and the
# model wrist steps of up to 23 cm between consecutive frames. The trace
# was an old Section 7.3 result and is printed nowhere in the rebuilt
# chapter; the quantity is a forward-kinematics wrist step, which D-039
# has not yet recomputed against the current accepted frame set, so it is
# withdrawn rather than carried forward (CH7_INTEGRATION_FIXLIST.md
# 9-18). Chapter 10 depends on this paragraph and is another writer's
# file. The mechanism itself is Section 2.6 and Section 5.5.
(P, 'The repair of the hips has a cost at its edges. Where the hips enter and leave the repair of Section 2.6, the root frame changes, the arm angles re-solve against the new frame, and the rate limit of Section 5.5 moves the output gradually to the new solution. The step belongs to the root and not to the arm solve. Its size on the handover recording is not among the results this thesis reports.'),

# Hip hold. The rule itself is the documented alternative that the
# reported results leave out (E-034, user decision 2026-09-09), and
# Chapter 10 carries it into future work. Removed on 2026-09-12: the
# whole numerical comparison of the preparation with the hold, on both
# recordings. It was an old Section 7.3 result, the rebuilt chapter
# prints none of it, and Chapter 9 would otherwise be the only home of
# six values (CH7_INTEGRATION_FIXLIST.md 9-19). The reasoning that
# survives needs no number: a frozen root is steady by construction, so
# steadiness cannot show that it is right.
(P, 'A rule that holds the hips at their last accepted position while a hand or the object covers them is the documented alternative to that preparation. A held root is steady whether or not the subject stayed still. Steadiness would therefore not show that it is right. No recording of this thesis measures the pelvis independently. The rule therefore stays an option that the reported results leave out.'),

# The preparation's own assumptions: Appendix G states the untested
# occluded start and what the shoulder-depth check needs.
(P, 'The preparation also needs accepted earlier samples. Its shoulder-depth check can act without them, but no recording of this thesis starts with the hips hidden, so that case is untested (Appendix G).'),

(H2, "9.5 Single-View Observability and Model Limits"),

# Model scope: four of the seven arm rotations and the wrist as a point
# (Sections 3.3.1 and 3.4.4); the rigid torso of Section 3.2 points
# here.
(P, 'Part of what the reconstruction cannot report follows from the model rather than from the sensing. The chain solves four of the seven rotations of an arm: the two shoulder swing angles, the shoulder twist and the elbow flexion. The wrist enters as a tracked point without orientation, because forearm pronation moves no landmark in the set (Section 3.4.4). Fingers, contact points and grip force are outside that set. The torso is one rigid plate with no twist between shoulders and hips, and the legs are not tracked.'),

# Fundamental observability: occlusion; the view-axis degeneracy and the
# undefined azimuth near the hanging arm (Section 3.4.2, the reason
# Section 8.3 gives for its azimuth difference); wrist orientation
# (Section 3.4.4); the swivel ambiguity of the two-link solve; and
# simultaneous body and object loss (Section 9.1).
(P, 'Of the errors the recordings show, one group follows from the single viewpoint and would remain with a perfect detector. Occlusion is the plain case, with the cube over the hand and the desk over the hips and no second view to fill in. Degeneracy along the optical axis is the next. An arm pointing at the camera leaves the wrist depth weakly constrained, and the shoulder azimuth is undefined near the arm hanging straight down (Section 3.4.2). Wrist orientation is unavailable from the landmark set at any image quality, and an arm configuration and its swivel about the shoulder-to-wrist line project to nearly the same image. When the body and the object are lost together, neither branch holds what the other lacks.'),

# Measurement limitations: the detector (Figure 9.2), the depth sample,
# the marker pose and the calibration. Thesis_wide.txt item 1.3: the
# gravity assumption stated in Section 2.2.2 ("The upright mounting was
# not measured") had no home in Chapter 9, so it joins this group and
# Table 9.1.
(P, f"A second group is measurement quality, and a better sensor or detector would reduce it. MediaPipe places a landmark off the body while reporting a usable visibility, as Figure 9.{F_LANDMARK} shows. The depth sampled at a landmark pixel can come from the surface in front of the body. The marker pose carries the noise of the located corners, which grows as the face turns away, and the calibration carries its own uncertainty into every world-frame distance. The gravity direction rests on an assumption of its own: the wall marker's printed up axis was taken as vertical and its mounting was not measured (Section 2.2.2)."),

# State estimation and implementation: the offset lag (Section 5.3), the
# memories and the holding state, the twist hold and the rate limit
# (Section 5.5), the hip depth preparation (Section 2.6) and the causal path
# (Section 9.6). MATH_LOGIC_REVIEW.md M07 and M08.
(P, 'The third group is state estimation and its implementation. The hand-object offset lags a changing grip and freezes at a failure. The direction memories and the holding state carry earlier frames forward, and the twist hold keeps a value the current frame cannot check. The rate limit spreads a step across several frames, and the hip depth preparation changes the frame the angles are read against. The rendering path adds differences of its own after the solve, which Section 9.2 separates from it. Causal initialization and filter lag add further differences, which Section 9.6 discusses. Single-view ambiguity is therefore only one of the causes.'),

(H2, "9.6 Real-Time and Causal Implications"),

# Why the two paths differ: Section 8.1 names the six operations that
# read the future and Section 8.3 reports the differences. Vocabulary of
# the brief: a processing-path difference, never an error against truth.
(P, 'The causal structure of Chapter 8 produced a different output from the offline pass on the same recording. Neither path is the reference for the other, so the two form a within-recording comparison of processing paths. The causal stages hold no sample from the future, so the smoother follows a moving joint late. The online path initializes its states on its first frames rather than on the whole recording, and the hand-object offset warms up over the first clean frames of an episode. Every state the layer carries then depends on what those first frames gave it.'),

# The measured differences: frames 7 to 24 treated differently, twists
# about 40 degrees apart, 12.0 cm at frame 18, elbows up to 24.1 degrees
# apart in the gap, the five-frame alignment with elbow flexion 0.4 and
# azimuth 16.4 degrees at the median and 23.3 degrees p95 for the
# shoulder group, and the azimuth near the undefined configuration
# (Section 8.3; figures/ch8_compare.json and
# v2/dataset/m03_rail_corrected.json).
(P, 'That dependence dominates the numbers. The offline failure mask rebuilt the right arm on frames 7 to 24 of the rail recording while the live gates held it, so the two paths froze shoulder twists about 40 degrees apart (Section 8.3). The rendered wrists sit 12.0 centimetres apart at frame 18, where the offline pass rebuilt the arm and the causal path held it. The frozen twists keep them apart on the later frames where every landmark is measured. Inside the natural gap the rebuilt elbows differ by as much as 24.1 degrees although the wrists nearly coincide, which is the swivel ambiguity of Section 9.5 appearing between two runs of the same structure. At the five-frame alignment that brings the two angle series closest, the elbow flexion differs by a median of 0.4 degrees and the shoulder azimuth by 16.4, with a 95th percentile of 23.3 degrees for the shoulder group. The azimuth is the large one because the arm hangs near the configuration in which it is undefined.'),

# What the comparison means for use; the untested items stay short with
# the pointer to Section 8.5. Locked fact 9: about 29 frames per second
# on a replay at the recorded pace (Section 8.4).
(P, 'A causal run is its own processing path. Its angles are as good as its first frames allow, and two runs of the same structure agree only when they start from the same first frames. A deployment therefore needs its own start, with the object at rest and in view and the arm in a configuration the gates accept. The structure consumed every frame of the rail recording at its recorded pace, about 29 frames per second (Section 8.4), and Section 8.5 lists what the step to the sensor leaves untested.'),

(H2, "9.7 Scope of the Evaluation"),

# One subject, three recordings. Removed on 2026-09-12: the durations of
# about 30, 50 and 70 seconds. Old Section 7.1 carried them; the rebuilt
# Section 7.1 names the three recordings without durations, and only the
# rail recording's 29.99 seconds survives anywhere, in the Appendix A
# table (CH7_INTEGRATION_FIXLIST.md 9-20).
(P, 'The evaluation rests on one subject in one controlled setup, recorded three times. Section 7.1 names the three recordings: the single-hand rail task, the handover on the same rail, and the two-hand loop that supplies the natural occlusion windows. The task is slow, and the desk and the camera did not move within a recording. Nothing here establishes accuracy across subjects, grips, clothing, tasks or scenes.'),

# Locked fact 6 and D-033: the manual wrist proxies are clicked image
# points, deprojected with the aligned depth; the clean frames give 4.5
# and 2.1 cm on the loop recording over n = 3 and n = 4, and the retained
# occluded sets hold 16 and 4 frames (Section 7.4.2;
# audit_evidence/ch7_restructured/natural.json). Removed on 2026-09-12:
# the rail cuff seam at 4.3 cm, whose label set D-033 excludes from
# Section 7.4.2 entirely, and the label sets "of 21 and 20 frames", which
# match nothing the rebuilt chapter prints
# (CH7_INTEGRATION_FIXLIST.md 9-21). The synthetic comparison is three
# windows of 45 frames on the handover recording and none on the
# single-hand recording (Section 7.4.1; 9-22).
(P, 'The references are limited in their own ways. The manual wrist labels are points selected by clicking on the colour image and deprojected with the aligned depth, and each marks a bracelet or a watch rather than the wrist the landmark defines. On clean frames of the loop recording those marks sit 4.5 and 2.1 centimetres from an accepted wrist measurement (Section 7.4.2). These separations limit anatomical interpretation; they do not establish a resolution threshold for differences between methods, since repeated-click and depth uncertainties were not quantified. The label sets are small, three and four clean frames and sixteen and four retained occluded frames, so a single frame moves a 95th percentile. The synthetic comparison covers three windows of 45 frames on the handover recording and no frame of the single-hand recording (Section 7.4.1).'),

# What has no reference at all: the unregistered route (Section 7.2),
# the object orientation, the absent live-camera session (Section 8.5)
# and the upper-body model.
(P, 'Some references are missing rather than limited. The physical route is not registered into the calibrated world frame, so the object comparison of Section 7.2 uses endpoint separations. No distance from the reconstructed track to the physical path exists, and no second measurement chain validates the object orientation. The causal result is a replay at the recorded pace, so no complete live-camera session was validated (Section 8.5). The model covers the upper body only.'),

# The claim the chapter leaves: feasibility, on the tasks and recordings
# that were run (central direction, REVISION_2026-09-11_BRIEF.md
# section 2).
(P, 'The work therefore demonstrates feasibility on the tested tasks and recordings. A single calibrated RGB-D viewpoint carried an upper-body kinematic reconstruction and an independently tracked object in one metric scene. Object information supplied an additional geometric constraint on some failure windows but not on others. The architecture also ran causally at the recorded pace. None of this establishes population-level accuracy. Table 9.1 collects the limitations and their causes. Chapter 10 uses these findings to answer the question of Chapter 1. It also identifies future work to address the limitations.'),

(TBL, [["Limitation", "Cause", "Where it shows on the recordings"],
       ["Landmark failure at high confidence",
        "MediaPipe places a landmark whether or not the body part is there",
        "Loop recording, frames 1775 to 1825: upper arm 47.2 cm against a clean 25.8 cm"],
       ["Object marker blocked",
        "A hand crosses the border of the printed square during the two-hand transfer on the desk",
        "Loop recording: the frames without an object pose fall in that transfer, so no object information exists across it (Section 7.4.2)"],
       ["Hips behind the desk",
        "The hip pixels stay usable, and their depth samples land on the desk, the rail or a crossing hand",
        "The hip depth preparation rejects a measured hip on 858 of the 900 frames of the rail recording (Section 8.3)"],
       ["Steady hip depth offset",
        "Both hip pixels take the rail's depth together, so nothing jumps between frames and a test that looks for a jump cannot see the offset",
        "Root frame pitched 32.1 degrees on frame 533, before the hip depth preparation of Section 2.6 (Section 3.5)"],
       ["Object lengths disagree with the physical reference",
        "Not isolated by these recordings; the detector settings set how large the disagreement is and not which way it goes",
        "Section 7.2: the carry reconstructs short on both recordings, by 1.14 and 2.82 cm, and the lift and the slide reconstruct long, by 0.53 to 2.83 cm"],
       ["Physical route not registered",
        "The measured route is a set of endpoint separations and is not expressed in the calibrated world frame",
        "Section 7.2 compares endpoint separations and reports no distance from the reconstructed track to the physical path"],
       ["Hand-object offset through a regrasp",
        "The offset can only be fitted while the hand is visible, so a regrasp during a failure carries the old one",
        "Loop recording, left arm: the object-assisted solve is the farthest of the three from the manual wrist label, 13.1 cm against 12.7 and 12.3 (Section 7.4.2)"],
       ["Recovery helps on one occluded window and not on the other",
        "Hand-object offset frozen with the estimator's lag; a nearly straight arm along the optical axis",
        "Loop recording, right arm: object-assisted 5.2 cm from the manual wrist label against 11.4 and 17.6, on four retained frames (Section 7.4.2)"],
       ["Rendered output differs from the kinematic solve",
        "The discrepancy appears downstream of the solve, in the rig and display path; the capture ran with the loop recording's arm lengths, and the downstream stages cannot be separated",
        "Handover recording, captured frames: kinematic model wrist 0.83 and 2.34 cm from the measured wrist against 5.7 and 6.9 cm for the rendered rig joint (Section 7.3.2)"],
       ["Segment lengths are effective, not anatomical",
        "The calibrated upper arm and forearm are medians of the landmark track",
        "Rail right arm 31.7 and 20.5 cm, loop right arm 25.6 and 25.2 cm, against about 25 cm for both segments measured on the subject"],
       ["Manual wrist label separation and limited sampling",
        "A clicked point marks a bracelet or a watch, not the wrist the landmark defines, and the sets are small",
        "Clean frames of the loop recording put the mark 4.5 and 2.1 cm from an accepted wrist measurement, on three and four frames (Section 7.4.2)"],
       ["Gravity reference unverified",
        "The wall marker's upright mounting was assumed, not measured",
        "Every gravity-referenced height and tilt of the thesis rests on it (Section 2.2.2)"],
       ["A single subject and three recordings",
        "One rail take, one handover take and one loop take, all of the same subject in the same setup",
        "Synthetic removal uses three windows of one recording and the manual wrist labels come from another (Sections 7.4.1 and 7.4.2)"],
       ["No wrist or hand pose",
        "Pronation moves no landmark in the set",
        "The solver returns four of the seven rotations of an arm"],
       ["No live-sensor session",
        "The capture process has not been run against the camera, and the online offset estimate needs the object at rest at the start",
        "The real-time result comes from the recording replayed at its recorded pace"]]),
(CAP, "Table 9.1. The principal limitations of the system, their causes, and where each one shows on the recordings."),

]

doc = Document()
style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(12)

for item in content:
    kind = item[0]
    if kind == H1:
        doc.add_heading(item[1], level=1)
    elif kind == H2:
        doc.add_heading(item[1], level=2)
    elif kind == P:
        doc.add_paragraph(item[1])
    elif kind == LIN:
        p = doc.add_paragraph(item[1])
        p.paragraph_format.left_indent = Inches(0.3)
    elif kind == CAP:
        p = doc.add_paragraph(item[1])
        p.runs[0].font.size = Pt(10)
        p.runs[0].font.italic = True
    elif kind == IMG:
        path = Path(item[1])
        assert path.exists(), f"missing figure: {path}"
        doc.add_picture(str(path), width=Inches(item[2]))
    elif kind == TBL:
        rows = item[1]
        t = doc.add_table(rows=len(rows), cols=len(rows[0]))
        t.style = "Table Grid"
        for i, r in enumerate(rows):
            for j, c in enumerate(r):
                cell = t.cell(i, j)
                cell.text = c
                for par in cell.paragraphs:
                    for run in par.runs:
                        run.font.size = Pt(10)
                        if i == 0:
                            run.font.bold = True

out = REPO / "writing" / "v8" / "condensed" / "Chapter_9_Discussion.docx"
doc.save(out)
print("saved", out, "| items:", len(content))

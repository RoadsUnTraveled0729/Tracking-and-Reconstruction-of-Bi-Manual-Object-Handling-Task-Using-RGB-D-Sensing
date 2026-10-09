#!/usr/bin/env python3

"""Build writing/v9/Chapter_9_Discussion.docx.

Thesis revision of 2026-09-11, Phase 2A (author's specification in
writing/v9/REVISION_2026-09-11_BRIEF.md, section 4), revised by the round
of 2026-09-14 (writing/v9/REVISION_2026-09-14_BRIEF.md, sections 2, 4, 5
and 6). Chapter 9 stays "Chapter 9: Discussion" and interprets Chapters 7
and 8 instead of repeating their tables.

Structure after the 2026-09-14 renumbering. The supervisor asked for a
general opening and a general first section, and for shorter discussions
in each subsection: "Make the opening paragraph of chapter 9 and section
9.1 more general. Just talk about the overall integrated components of
the thesis and what to manage to show. No need to go through naming each
of the subsection." The opening paragraph therefore names no section, and
the new Section 9.1, The Integrated Reconstruction and Its Evaluation,
describes the integrated components and what the evaluation showed,
without printing a number. The seven sections that existed before the
round keep their titles and their evidence and move down by one:

  9.1 The Integrated Reconstruction and Its Evaluation        (new)
  9.2 Object Reconstruction and Physical-Route Error Sources  (was 9.1)
  9.3 Human-Object Spatial Reconstruction                     (was 9.2)
  9.4 Landmark Failure and Object-Assisted Recovery           (was 9.3)
  9.5 Torso and Root Failure and High-Confidence Landmark
      Errors                                                  (was 9.4)
  9.6 Single-View Observability and Model Limits              (was 9.5)
  9.7 Real-Time and Causal Implications                       (was 9.6)
  9.8 Scope of the Evaluation, with Table 9.1                 (was 9.7)

Each of the seven moved sections is condensed by about 35 percent of its
prose word count (D-119; the draft of 2026-09-14 reached 22 percent, the
final pass the rest). Figure 9.1, Figure 9.2, every number that is this
chapter's own argument and every claim the comment blocks below name
survive. Table 9.1 was trimmed on 2026-09-14 from fifteen rows to the six
the author identified as most important (see the comment above the table
itself); every claim the other nine rows carried stays stated in this
chapter's prose or in the section each row pointed to. Under D-119 the final pass dropped
values that only restated Chapter 7 or Chapter 8 where the reading plus
the section pointer carries the point; each such value stays printed in
its chapter and, where Table 9.1 has a row for it, in that row. The drops
are logged in notes_revision_ch9_v9.md (Final pass). Conclusions and
future work are Chapter 10 (build_ch10.py).

Numbers. The rule of section 5 of the 2026-09-14 brief binds this
chapter: no number that the listed evidence files hold is typed by hand.
The reads are collected below the imports, each with the file and the
field it comes from, and each formatted in the builder. The values that
this chapter restates from Chapter 8 (the frozen twists about 40 degrees
apart, the frame 18 chain separation, the 24.1 degree elbow spread and
the alignment statistics) stay as restatements of Section 8.3 with their
pinned source named in the comment above them, as they were.

Two numerically identical and unrelated quantities now sit in this
chapter, and the prose of Sections 9.3 and 9.7 is worded so that neither
can be read as a restatement of the other. Section 9.3 gives the median
distance from the Unity rendered hand to the measured wrist over the
captured frames of the rail recording, read from human.json, which moves
with each re-capture. Section 9.7 gives the separation between the wrists
of the two forward-kinematics chains at frame 18 of the same recording,
one from the offline pass and one from the causal path, which is a
processing-path difference drawn on the colour image and never a render.
Chapter 8 (build_ch8.py line 254) carries the same wording.

Cross-references follow the Chapter 7 structure of D-029 and D-038: the
object segment lengths and the fitted-line scatter are Section 7.2, the
rendered joint errors under valid landmark measurements Section 7.3 with
its two task subsections, the wrist to marker spatial check Section
7.3.3, the synthetic landmark removal Section 7.4.1, the natural
occlusion labels Section 7.4.2, the offline-causal comparison Section
8.3, the runtime Section 8.4 and the remaining validation gap Section
8.5. Chapter 7 table and figure numbers are deliberately not cited from
this chapter: Section 7.2 is still gaining tables and every Chapter 7
table and figure number shifts with it, while the section numbers are
stable. Subsection pointers therefore carry the references instead.

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

Section 9.3 carries the two wrist quantities of D-039 to D-043. The bare
kinematic model wrist error and the rendered Unity rig wrist error are
defined separately and never described interchangeably, both against the
accepted raw measured wrist that D-040 fixes as the evaluation reference.
The recording-wide bare model values carry any general statement about
the accuracy of the kinematic model, and the Unity capture subset values
appear only in the contrast with the rendered rig, which is frame-matched
to them (D-041). The author's conditional reading is applied to the
handover recording only, where the bare model wrist stays close to the
measured wrist and the rendered rig wrist is the farther of the two from
it: most of the further discrepancy appears downstream of the kinematic
solve, in the rig and display path, and no share of it is assigned to any
stage inside that path. The magnitudes are no longer described in words,
because the three thesis captures are being re-run under E-036 and the
evidence files still hold the values of the captures they replace; the
prose says which quantities are compared and lets the read values carry
the sizes. D-043 forbids quantifying the rig's part, and it still binds
after E-036: the new sizing removes a known configuration mismatch and
licenses no sentence that assigns a share of the rendered difference to
the rig proportions, to the display filter or to any single stage.
D-042 keeps the single-hand rail recording out of that reading and out of
any numerical comparison with the handover values, because every accepted
frame of it carries a held forearm twist and a constrained root; its
6.78 cm bare model value is therefore not printed here either. The older
0.96 and 1.17 cm figures do reproduce from eval/reports/r7_handover.json,
but under a whole-recording, filtered-wrist and almost ungated definition,
so they are a different quantity and no longer appear in this chapter.

Two later decisions also land here. D-044 defines the task phases once,
in Section 2.1: object acquisition, carry, lift, slide and release.
Section 9.2 names the carry, the lift and the slide of the object route
with one pointer to that definition and does not introduce the terms
independently. D-045 confirms that the coarse rail-height cross-check
against the 3.8 cm physical rail height is dropped for good, superseded
by the W2 to W3 separation of Section 7.2, which is measured for the
marker centre itself; no claim of this chapter rests on the dropped
cross-check. D-046 moves the loop detection coverage to Section 7.4.2,
which is now where it is established and where this chapter cites it;
Section 9.2 keeps the implication for the recovery and introduces no
count of its own.

Locked facts applied: the physical route is a tape measurement and is not yet
registered into the world frame, so no point-to-path distance exists
(facts 2 and 3); the approximately 16 cm wrist-to-marker distance is an
approximate scalar for the single-hand grip (facts 4 and 5); the manual wrist
labels are clicked image points (fact 6); object information supplies an
additional geometric constraint (fact 8); the causal result is a replay
at the recorded pace (fact 9). Both failure-mode screenshots stay (rule
3 of skill_set/thesis-structure-rules.md); the marker figure is cited
first, in Section 9.2, so it is Figure 9.1 and the landmark figure 9.2.
Table 9.1 keeps its row for the unregistered physical route and its row
for the manual-label uncertainty.

Locked facts of the 2026-09-14 round, section 4 of that brief, applied in
Section 9.3 and in Table 9.1. The loop recording's 25.6 and 25.2 cm arm
lengths are that recording's landmark medians and are never called
measurements on the subject (fact 1). The subject's direct measurement of
about 25 cm per segment stays as an independent anatomical comparison and
is never a source of any length, and it is quoted no finer than "about 25
centimetres" (fact 2). The rail recording's elbow landmark sits farther
along the arm than the loop recording's, stated as a landmark-placement
observation and never as anatomy or as an anatomical error, with the
shift read from the pinned diagnostic and printed at one decimal place
(fact 3). The left arm of the rail recording is not compared, and the
prose says on how few clean frames it rests (fact 4). No share of the
rendered error is assigned to the rig proportions (fact 5). Nothing in
the chapter compares the old captures with the re-run captures frame by
frame (fact 6).

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
unpinned "about 80 degrees" is removed (decision G2); Sections 9.3, 9.4
and 9.5 keep the reading and drop the numbers Section 7.3 and Section
7.4.2 already print (decision G3); the chapter closes by handing on to
Chapter 10 (decision G5); the wall marker's unverified mounting reaches
Section 9.6 and Table 9.1. Two items of that pass were superseded by the
Chapter 7 integration pass above: the detectors sentence lost its frame
numbers with the failure-coverage passage of old Section 7.1, and the
synthetic sentence it treated was replaced outright.

2026-09-16, C54 (D-128): the supervisor's comment of that date ("you do
not need to add subsection [...] make them all in a bullet format. Also,
ask AI to shorten each of the descriptions in subsections") and the
author's instruction to condense the opening and closing transitions are
applied. The former opening paragraph and the former Section 9.1 (The
Integrated Reconstruction and Its Evaluation) are merged into the
chapter's opening text, about 120 words in two paragraphs, with no
heading and no number. The seven remaining sections renumber down by one
(former 9.2 to 9.1, 9.3 to 9.2, 9.4 to 9.3, 9.5 to 9.4, 9.6 to 9.5, 9.7 to
9.6, 9.8 to 9.7) and every internal "Section 9.x" pointer in the chapter's
own prose and in the Table 9.1 segment-length row follows that map. Each
section is now one lead sentence naming its claim, then three to six
bullets with a bold run-in label (the BUL item kind), replacing the old
paragraphs; Section 9.2 (was 9.3) and Section 9.3 (was 9.4) keep up to
six bullets, the rest three to five. Figure 9.1 and Figure 9.2 stay
inside the bullet group that cites each, Table 9.1 is unchanged apart
from its one renumbered cell, and the closing two sentences of Section
9.7 (feasibility, and the pointer to Chapter 10) stay prose. The chapter
falls from 3,006 to about 1,630 prose words: below the author's roughly
1,500-word target but short of it only where a further cut would have
dropped a number, a definition or a negative result the bullet mechanics
could not carry in fewer words (see notes_c54_ch9.md for the per-section
list). Two bullets that only restated a Table 9.1 cause cell (the object
route's "cause not isolated" reading and the effective-segment-length
reading) and one bullet on the recovery ranking already carried by the
Table 9.1 recovery row were cut outright, since the table keeps them.
Every number, f-string interpolation, negative result and limitation
group the C54 brief names to survive is kept, in prose, in a caption or
in the unchanged table.

2026-09-16, third pass (author): the author re-read the supervisor's
comment ("Make them all in a bullet format") and asked to follow it. The
bullet content list of commit 894f373 is restored under the two-paragraph
opener of the prose pass; the general overview stays as the unnumbered
chapter opening (the supervisor's "no need to add subsection" refers to
the 9.1 heading, not to the transition text). Sections 9.1 to 9.7: lead
sentence plus labelled bullets; Figures 9.1, 9.2 and Table 9.1 unchanged.

2026-09-16, C55 (supervisor): no subsections; one plain-language bullet
per former section (seven bullets, no bold labels), each combining that
section's points in layman's terms; the first bullet is the supervisor's
own example rewrite made impersonal. Numbers live in Table 9.1 and the
figures; the bullets keep one (about 12 centimetres between the offline
and live wrists). No "Section 9.x" pointer remains anywhere; the other
builders point at "Chapter 9".
"""
import json
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches

H1, H2, P = "h1", "h2", "p"
CAP, TBL, LIN, IMG = "cap", "tbl", "lin", "img"
BUL = "bul"  # bullet item (supervisor comment C54, 2026-09-16)
NUM = "num"  # numbered item (C54 mechanics follow-up, 2026-09-16; see list_numbering.py)

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v9" / "figures"
EVID = REPO / "writing" / "v9" / "audit_evidence"
REPORTS = REPO / "eval" / "reports"

F_MARKER, F_LANDMARK = 1, 2


def _load(path):
    with path.open() as handle:
        return json.load(handle)


# ---------------------------------------------------------------------------
# Numbers read at build time (section 5 of REVISION_2026-09-14_BRIEF.md).
# Nothing below is typed by hand, and each read names its file and field.
# ---------------------------------------------------------------------------

# Rendered Unity rig wrist medians against the accepted raw measured wrist,
# over the frames each Unity capture saved. Source:
# writing/v9/audit_evidence/ch7_restructured/human.json, printed in
# Section 7.3.1 and Section 7.3.2:
#   RIG_WRIST_R  = ['r7']['joints']['right_wrist']['median']   (handover)
#   RIG_WRIST_L  = ['r7']['joints']['left_wrist']['median']    (handover)
#   RAIL_RIG_WRIST = ['r6b']['joints']['right_wrist']['median'] (rail)
# Values are centimetres in the file and are printed at one decimal. The
# file is regenerated with each capture under E-036, so the prose states
# what is compared and never the size in words.
_HUMAN = _load(EVID / "ch7_restructured" / "human.json")
RIG_WRIST_R = f"{_HUMAN['r7']['joints']['right_wrist']['median']:.1f}"
RIG_WRIST_L = f"{_HUMAN['r7']['joints']['left_wrist']['median']:.1f}"
RAIL_RIG_WRIST = f"{_HUMAN['r6b']['joints']['right_wrist']['median']:.1f}"

# Bare kinematic model wrist medians against the same reference. Source:
# writing/v9/audit_evidence/ch7_restructured/bare_model.json,
# ['recordings']['r7']['joints'][<joint>][<scope>]['vs_raw_measured']
# ['median'], with <scope> 'section_7_3_frame_set' for the captured subset
# and 'recording_wide_accepted' for the valid-landmark frames of the whole
# recording. Printed in Section 7.3.2. Centimetres in the file, printed at
# two decimals, which is the precision these four values have carried
# since the Chapter 7 restructure and is inside the two-decimal ceiling of
# skill_set/measurement-precision-reporting.md.
_BARE = _load(EVID / "ch7_restructured" / "bare_model.json")


def _bare(joint, scope):
    node = _BARE["recordings"]["r7"]["joints"][joint][scope]
    return f"{node['vs_raw_measured']['median']:.2f}"


BARE_SUBSET_R = _bare("right_wrist", "section_7_3_frame_set")
BARE_SUBSET_L = _bare("left_wrist", "section_7_3_frame_set")
BARE_WIDE_R = _bare("right_wrist", "recording_wide_accepted")
BARE_WIDE_L = _bare("left_wrist", "recording_wide_accepted")

# Calibrated arm segment lengths, the offset-fit medians the recovery of
# Chapter 5 uses and, under E-036, the lengths each replayed capture is
# sized with. Source: eval/reports/<stem>_offset_fit.json,
# ['segment_lengths_m']['upper_arm_R'] and ['forearm_R'], metres in the
# file, printed in centimetres at one decimal. Locked fact 1 of the
# 2026-09-14 round: the loop values are that recording's landmark medians
# and not measurements on the subject.
_LOOP_FIT = _load(REPORTS / "recording_20260825_222315_offset_fit.json")
_RAIL_FIT = _load(REPORTS / "recording_20260831_065553_offset_fit.json")


def _seg(fit, key):
    return f"{fit['segment_lengths_m'][key] * 100:.1f}"


LOOP_UPPER_R = _seg(_LOOP_FIT, "upper_arm_R")
LOOP_FORE_R = _seg(_LOOP_FIT, "forearm_R")
RAIL_UPPER_R = _seg(_RAIL_FIT, "upper_arm_R")
RAIL_FORE_R = _seg(_RAIL_FIT, "forearm_R")

# The elbow-landmark placement observation, locked fact 3 of the
# 2026-09-14 round and open item 1 of section 9 of that brief. Source:
# writing/v9/audit_evidence/followup/m17_segment_diagnostic.json,
# ['comparison']['right']:
#   ELBOW_SHIFT = elbow_shift_along_shoulder_wrist_line_m, metres in the
#     file, printed in centimetres at one decimal. Defined in the file as
#     the median elbow projection fraction on the shoulder-to-wrist line
#     over the rail recording's strict-clean right-arm frames minus the
#     same median over the loop recording's, times the median
#     shoulder-to-wrist distance over the union of those two frame sets.
#   ELBOW_FRAC_RAIL, ELBOW_FRAC_LOOP = the two medians themselves,
#     ['derived_by_policy']['raw']['elbow_projection_fraction_median_rail']
#     and [...]_median_loop, printed at two decimals.
# The clean-frame counts are ['recordings'][<rec>]['arms'][<side>]
# ['n_strict_clean'], the same strict-clean rule per recording. The left
# arm of the rail recording is not compared (locked fact 4). All three
# quantities are landmark placement and never anatomy.
_SEGDIAG = _load(EVID / "followup" / "m17_segment_diagnostic.json")
_ELBOW = _SEGDIAG["comparison"]["right"]
_ELBOW_RAW = _ELBOW["derived_by_policy"]["raw"]
ELBOW_SHIFT = f"{_ELBOW['elbow_shift_along_shoulder_wrist_line_m'] * 100:.1f}"
ELBOW_FRAC_RAIL = f"{_ELBOW_RAW['elbow_projection_fraction_median_rail']:.2f}"
ELBOW_FRAC_LOOP = f"{_ELBOW_RAW['elbow_projection_fraction_median_loop']:.2f}"
CLEAN_RAIL_R = _SEGDIAG["recordings"]["rail"]["arms"]["right"]["n_strict_clean"]
CLEAN_LOOP_R = _SEGDIAG["recordings"]["loop"]["arms"]["right"]["n_strict_clean"]
CLEAN_RAIL_L = _SEGDIAG["recordings"]["rail"]["arms"]["left"]["n_strict_clean"]

# Second pass of the C54 round (2026-09-16, author's feedback on the first
# delivery): the chapter is prose again, in the author's plain voice, with
# two short lists only where the items are parallel (the three limitation
# groups in 9.5, numbered; the missing references in 9.7, bulleted). The
# bold run-in labels are gone. Every number, interpolation, caveat and
# pointer of the first pass is kept; the section numbering 9.1 to 9.7 is
# unchanged. Word target 1,600 to 1,800.
content = [
(H1, "Chapter 9: Discussion"),

(P, "This chapter reads the results of Chapters 7 and 8 as evidence about one integrated system. The system runs two branches from one RGB-D camera and three printed markers. The landmark branch gives a torso pose and four joint angles per arm, and the marker branch gives the world frame and the object pose. A recovery layer marks each joint group as measured, held or constrained, and the same chain also runs causally."),

(P, "Each part was evaluated against a reference of its own. The points below state the conclusions those results support and the limits they reveal. The limits are of three kinds: the view of a single camera, the quality of the measurements, and the values the system carries over from earlier frames."),

# Former 9.1, the supervisor's own example rewrite (C55, 2026-09-16), with
# "we compare" made impersonal because the thesis never uses "we".
(BUL, "", f"Comparing the reconstructed object path with simple tape-measure distances shows a clear pattern in the errors: carry segments come out a bit shorter than they really are, while lift and slide segments come out a bit longer. Within the range of detector settings tested, adjusting them changes the size of the errors, not their direction. Lift points are the least reliable because each one depends on depth from a single video frame. Some extra uncertainty also comes from the wobble and rotation of the object, since those checks rely only on the recording itself, not an external reference. When the system loses the marker, it simply gives no position rather than a wrong one, and these losses happen only outside the labelled parts of the data, so the labelled comparisons remain unaffected. Figure 9.{F_MARKER} shows one such loss, and Figure 7.3 shows the three segments of the reconstructed path."),

(IMG, FIG / "ch9_fig_marker_blocked.png", 6.3),
(CAP, f"Figure 9.{F_MARKER}. Object marker loss on the loop recording. (a) Both markers are detected, their corners outlined. (b) A finger crosses the printed square and no object pose is returned."),

# Former 9.2.
(BUL, "", "The placement of the person and the object together in the scene has one outside check: the tape-measured distance from the wrist to the cube in the hand. The reconstruction comes close to it. The wrist the kinematic model places sits closer to the measured wrist than the wrist the drawn avatar shows, and the difference is not blamed on any single step of the path that draws the avatar. The distance also depends on the state of the forearm twist, measured or held; on the rail recording it is always held, so the avatar hand lands beside the cube. The two recordings also give different arm lengths, because the elbow landmark sits farther down the arm on one of them, and that is a property of the landmark rather than of the person. Figures 7.5 and 7.6 show the video beside the drawn avatar, and Figures 7.8 and 7.9 show a wrist label against the reconstructed arm."),

# Former 9.3.
(BUL, "", "Using the object to place a hidden hand helped on one side and not on the other. The stored hand-to-object distance is learned while the hand is visible and updates slowly, so it lags behind a changing grip and freezes when tracking fails. An arm pointing straight at the camera leaves the wrist depth uncertain, so a small error there moves the elbow a long way, and a twist held through a gap is kept by the frames that follow. In the tests where landmarks were removed on purpose, no method was best on every window and joint. A closer wrist position on its own does not prove that the whole arm is right. Figure 5.3 shows the stored hand-to-object distance, Figure 5.5 the elbow reconstruction, and Figure 7.7 the natural failure frames."),

# Former 9.4.
(BUL, "", f"The torso frame that every arm angle is measured against depends on the two hip landmarks, and the desk can hide them. A hidden hip takes the depth of whatever is in front of it, so an upright person appears tilted forward, and because both hips shift together, no failure detector notices the shift. A landmark can also be wrong while the detector is confident about it: the detector once placed the elbow on the hand (Figure 9.{F_LANDMARK}), and the check on the arm's length caught the mistake. When the hip depth preparation switches on or off, the torso frame moves with it. Holding the hips at their last good position while covered would look steady, but nothing measures the hips independently, so that rule remains untested. Figure 3.4 shows the torso frame built from the hips."),

(IMG, FIG / "ch9_fig_landmark_failure.png", 6.3),
(CAP, f"Figure 9.{F_LANDMARK}. Landmark tracking failure on the loop recording. (a) The right elbow and wrist landmarks sit correctly. (b) The elbow landmark has moved onto the hand."),

# Former 9.5.
(BUL, "", "The model itself solves four of the seven ways an arm can rotate, treats the wrist as a point with no orientation and the torso as one rigid plate, and does not track the legs. The other limits are of three kinds. A single camera cannot see a hand behind the cube or the desk, cannot judge depth well along the line of sight, and cannot tell the turn of a hanging arm or of a wrist. Measurements can be wrong: a landmark can sit off the body, a depth reading can come from the wrong surface, and marker corners can be noisy. The calibration's vertical direction also rests on the mounting angle of the wall marker, which was never measured. Finally, values carried between frames, such as a stored hand-to-object distance or a held angle, can be out of date. Figure 3.6 shows the arm chain and Figure 3.7 the swing and twist of a joint."),

# Former 9.6.
(BUL, "", "Running the system live, frame by frame, gives a different result from processing the whole recording afterwards, because the live version cannot look ahead. In one gap the offline pass rebuilt the arm while the live pass held it, so the two froze the forearm twist at different angles, and their wrists ended up about 12 centimetres apart. The gap did not close once tracking returned. Live runs match each other only if both start from the same first frames, so running it for real needs a defined start, with the object at rest in view. The live version kept pace with the recording, but only as a replay of a file. Chapter 8 lists the points a real camera session still has to prove, and Figure 8.3 draws the offline and live chains on the same frames."),

# Former 9.7.
(BUL, "", "The evaluation rests on one person doing a slow task in one controlled setup, recorded three times. Nothing here shows the accuracy of the system for other people, grips, clothing, tasks or rooms. The wrist labels used for checking are points clicked on a bracelet or a watch, not the exact wrist the detector defines, and the label sets are small, so a single frame can change a summary statistic. Some references are missing altogether. The physical route was never lined up in the same frame of reference as the reconstruction. The object's orientation has no reference of its own. The live result is a replay rather than a camera session, and the model stops at the upper body. Table 9.1 collects the six main limitations with the numbers behind them."),

(TBL, [["Limitation", "Cause", "Evidence on the recordings"],
       ["Object lengths disagree with the physical reference",
        "Not isolated by these recordings; the detector settings set the size of the disagreement, not its direction",
        "Section 7.2: the carry reconstructs short on both recordings, by 1.14 and 2.82 cm, and the lift and the slide reconstruct long, by 0.53 to 2.83 cm"],
       ["Physical route not registered",
        "The measured route is a set of endpoint separations and is not expressed in the calibrated world frame",
        "Section 7.2 compares endpoint separations and reports no distance from the reconstructed track to the physical path"],
       ["Rendered output differs from the kinematic solve",
        "The discrepancy appears downstream of the solve, in the rig and display path, whose stages these results cannot separate",
        f"Handover recording, captured frames: kinematic model wrist {BARE_SUBSET_R} and {BARE_SUBSET_L} cm from the measured wrist against {RIG_WRIST_R} and {RIG_WRIST_L} cm for the rendered rig joint (Section 7.3.2)"],
       ["Segment lengths are effective, not anatomical",
        "The calibrated upper arm and forearm are medians of the landmark track, and the elbow landmark need not sit at the anatomical elbow",
        f"Rail right arm {RAIL_UPPER_R} and {RAIL_FORE_R} cm, loop right arm {LOOP_UPPER_R} and {LOOP_FORE_R} cm, beside an independent measurement of about 25 cm for both segments on the subject; the rail elbow landmark sits {ELBOW_SHIFT} cm farther along the arm"],
       ["Recovery helps on one occluded window and not on the other",
        "Hand-object offset frozen with the estimator's lag; a nearly straight arm along the optical axis",
        "Loop recording, right arm: object-assisted 5.2 cm from the manual wrist label against 11.4 and 17.6, on four retained frames (Section 7.4.2)"],
       ["No live-sensor session",
        "The capture process has not been run against the camera, and the online offset estimate needs the object at rest at the start",
        "The real-time result comes from the recording replayed at its recorded pace"]]),
(CAP, "Table 9.1. The six principal limitations of the system, their causes, and the evidence for each on the recordings."),

# The closing paragraph follows the table (author, 2026-09-16): with the
# whole table kept on one page, a closing paragraph placed before it sat
# alone on a page of its own.
(P, "The results show that the approach works on the tasks that were recorded. They do not establish the accuracy of the system for other people or other tasks. Chapter 10 concludes and sets out future work."),
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
    elif kind == BUL:
        # bullet item (supervisor comment C54, 2026-09-16)
        p = doc.add_paragraph(style="List Bullet")
        if item[1]:
            p.add_run(item[1]).font.bold = True
            p.add_run(" " + item[2])
        else:
            p.add_run(item[2])
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        p.paragraph_format.space_after = Pt(4)
    elif kind == NUM:
        # numbered item, restarted per contiguous run (C54 mechanics
        # follow-up, 2026-09-16; see list_numbering.py)
        p = doc.add_paragraph(style="List Number 2")
        if item[1]:
            p.add_run(item[1]).font.bold = True
            p.add_run(" " + item[2])
        else:
            p.add_run(item[2])
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        p.paragraph_format.space_after = Pt(4)
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
        # Column widths for Table 9.1 (author, 2026-09-16): the third column
        # carries the longest text, so it takes the largest share of the six
        # inches; the whole table then shares its page with the closing
        # paragraph instead of pushing it onto a page of its own.
        if len(rows[0]) == 3:
            from docx.oxml.ns import qn as _qn
            twips = (2088, 2808, 3744)  # 1.45, 1.95 and 2.6 inches, 6.0 in total
            for col, w in zip(t._tbl.tblGrid.findall(_qn("w:gridCol")), twips):
                col.set(_qn("w:w"), str(w))
            for j, w in enumerate(twips):
                for i in range(len(rows)):
                    tcw = t.cell(i, j)._tc.get_or_add_tcPr().get_or_add_tcW()
                    tcw.set(_qn("w:w"), str(w)); tcw.set(_qn("w:type"), "dxa")

out = REPO / "writing" / "v9" / "Chapter_9_Discussion.docx"
from list_numbering import restart_numbered_lists
restart_numbered_lists(doc)

doc.save(out)
print("saved", out, "| items:", len(content))

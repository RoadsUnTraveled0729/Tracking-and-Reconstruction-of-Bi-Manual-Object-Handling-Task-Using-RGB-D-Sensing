#!/usr/bin/env python3
"""Build writing/v8/Chapter_5_Pose_Recovery.docx (V8 rewrite round).

Chapter 5 rewritten for supervisor round 4 (C22-C28, 2026-09-05) on the
user's plan for the chapter (writing/v8/PROF_COMMENTS_ROUND4.md):
occlusion is missing data in an otherwise clean recording, the torso is
assumed measured on every frame, the chapter stays simple.

Structure: opening (transition from Chapter 4, the missing-data cases
A-C in the words of the Chapter 3 chain, Figure 5.1 information flow;
C26, C27), 5.1 Assumptions and Parameters (C28, prose), 5.2 Landmark
Tracking Failures (Figure 5.2), 5.3 Grip Episodes and the
Hand-Object Offset (Table 5.1 notation, C24; Figure 5.3 schematic for
equations 5.1 and 5.2, C23; the offset-unknown paragraph, C25; the
holding state, Figure 5.4; the direction memory, equation 5.5, and the
Case A wrist rebuild, equation 5.6), 5.4 Wrist Recovery from the Object
Pose (equation 5.7), 5.5 Elbow Recovery by Two-Link Inverse Kinematics
(equations 5.8-5.12, Figure 5.5, then the twist hold and the rate
limit), 5.6 Worked Example (Figure 5.6 and one failure frame of the rail recording
through equations 5.7-5.12, numbers from ch5_worked_example.py). On the
user's plan (2026-09-06) the lists, the parameter table, the detector
and joint-group tables and the output-states section became prose; the
three states are defined in the opening. One table remains, the
notation Table 5.1, as in Chapter 3.

Parked (writing/v8/CH5_PARKED.md, verbatim from the V7 build): the whole
of Section 5.5 Torso Repair on Camera Rays (equations 5.12-5.23 of V7,
Figure 5.4 of V7), the reach inequality (equation 5.6 of V7) and every
torso-repair sentence elsewhere. Decision D1 of round 4 taken on the
user's plan item 3 (torso assumed measured); the two torso detectors
stay as a report on that assumption (D4, reversible).

Symbols (C24): one meaning per letter. h is the hand-object offset and
h_k its observation on frame k (was d); the turn about the
shoulder-to-wrist line stays s; the upper-arm direction memory stays
u-hat, as Figure 5.5 draws it, and the forearm memory is f-hat.

Method only (user rule 2026-08-28): what the recovery does and how. No
accuracy numbers, no fire counts, no failure-window frame numbers.
Threshold values that DEFINE the method are design parameters, and the
source of each is named in a comment beside it.

Prose: the user's voice (Chapter 2 sections 2.3-2.5 as the sample) and
the humanizer rules of writing/WRITING_SKILL.md, with the supervisor
constraints of skill_set/thesis-statement-style.md. Canadian spelling.

Sources for every design parameter printed here:
  five detector thresholds, event rules eval/failure/detect_failures.py
                                        eval/reports/r5_failure_mask.md
  grip state and the offset estimator   eval/failure/grip_state.py
  instantaneous holding conditions      eval/offset/carry.py
  plausibility bounds, grip detector    eval/failure/recovery_core.py
  IK, direction memory, horizon, tags   v1/kinematics/occlusion_ext.py
  Unity meaning of the tags             Unity/Assets/Scripts/
                                        IntegratedSceneReceiverV2.cs

E-020 (the joint-limited elbow) is excluded from the thesis by
skill_set/thesis-structure-rules.md rule 4 and is not mentioned.

Pass of 2026-09-06 (condensed build): the manual wrist labels are done
and graded (eval/reports/*_recovery_labeled.md), so the two pending-label
sentences take the result without numbers; Section 5.3 gains the
estimator-lag limit; audit findings M04 to M08 and M17 of
writing/v9/MATH_LOGIC_REVIEW.md corrected in the prose only
(clipping outside reach, scope of the twist hold, scope of the memory
horizon, the retrospective offline preparation, the constrained root of
the worked example, the calibrated lengths). No equation changed.

Revision of 2026-09-11 (Phase 3, continuity and wording only; no method,
parameter, equation, figure, table or number changed): the opening states
what Chapters 3 and 4 provide and what they leave unresolved, and names
the core idea, that object observations provide an additional geometric
constraint when body landmarks become unreliable (brief section 3, locked
fact 8); Section 5.4 says once that equation (5.7) is that constraint and
not a recovery of the wrist on its own; the two old "Section 7.8"
references become Section 7.4.2 and the promise about Chapter 7 names the
unmasked solve under synthetic masking (7.4.1) and the manual wrist labels
on the natural failures (7.4.2); the loop recording is named in Section
5.3 where the text said "the second recording of Chapter 7"; the closing
says what the chapter established, why Chapter 6 follows, and where the
constraint is graded (Section 7.4) and interpreted (Section 9.4). The
approximately 16 cm scalar physical wrist-to-marker reference of locked
fact 4 belongs to Chapter 7 and is not mentioned here; the three-
dimensional object-frame offset of Section 5.3 is a different quantity.

Figures: writing/v8/figures/ch5_fig_flow.png (make_ch5_flow_fig.py),
ch5_fig_detectors.png and ch5_fig_ik.png (unchanged from V7,
writing/v7/scripts/make_ch5_detectors_fig.py, make_ch5_ik_fig.py),
ch5_fig_offset.png (make_ch5_offset_fig.py), ch5_fig_holding.png
(make_ch5_holding_fig.py). ch5_fig_states.png and its script were
removed with the output-states section.

2026-09-12, follow-up to the Chapter 7 restructure (D-029): Section 5.1
no longer names "the plain, masked and recovery solves of Chapter 7".
The rebuilt Chapter 7 has no masked solve; Section 7.4.1 compares
hold-last, direction memory and object-assisted recovery, and Section
7.4.2 compares the plain solve, hold-last and object-assisted recovery.
The sentence now matches Chapter 2 Section 2.6 and Appendix G.4 word for
word. The claim itself is unchanged and was re-verified against the
variant definitions; the comment above the paragraph gives the sources.
No number changed. (The condensation round of 2026-09-15 below shortened
the paragraph around that sentence; the sentence itself is unchanged and
still matches Section 2.6 and Appendix G.4 word for word.)

Historical changelog, superseded by D-082: Craig notation pass of 2026-09-12 (notation only; no method, parameter,
figure, table, equation count or number changed). The 37 rows assigned to
this builder in FRAME_INVENTORY.md section 8.9.5 are applied under D-054's
four classes with the semantic frame names of D-056 and D-058. Chapter 5
uses three frames: person space {Person}, the levelled frame {Levelled} and
the mapped marker frame {MappedMarker}. The letter W, which Chapter 4 uses
for the desk-marker frame and Chapter 5 used for the gravity-levelled frame
32.04 degrees away from it, no longer serves both (C5-37). R_obj becomes
the class-1 rotation with both frames in its script slots; the scene
calibration, which had no symbol anywhere in the thesis, becomes the
class-2 transform from {Levelled} to person space. Under D-061 this chapter
cites {Levelled} and {MappedMarker} to Chapter 6, where the swap of
equation (6.1) and the levelling rotation of Section 6.4 define them, and
carries no defining introduction of its own.

Three substantive defects of FRAME_INVENTORY.md section 9 lived in this
chapter (as Table 5.1 stood) and were deliberately NOT touched by that
pass, because each needed author content rather than a label: S-1, Table
5.1 attributed the object origin and orientation to the transform of
Chapter 4, which they were not, since the axis swap and the levelling sat
between and were printed nowhere; S-2, the object frame declared for the
offset in the table against the mapped marker frame the offset actually
lives in, which needed the handedness change and the conjugation stated;
and the two different values printed under the wrist estimate four lines
apart in Section 5.6, whose numbers are unchanged and which now differ
only by their frame superscript.

Prose condensation of 2026-09-14 (this pass): the chapter body cut from
5851 to about 4900 words and every figure caption cut to at most 30 words,
for the shorter body the author asked for. Only repetition, restatement,
preview sentences, rationale clauses that repeat the rule they justify, and
figure-panel descriptions that the prose already carries were removed. No
number, unit, equation, figure, table, heading, threshold, recovery rule,
output state, stated assumption or source comment changed, and no
cross-reference target lost its last mention; the removed Figure 5.3 panel
sentences and the removed optimality argument for equation (5.12) left every
symbol still defined at first appearance. The cut stops at about 4900 rather
than the 4400 asked for: what remains is rule, definition, threshold,
locked sentence, worked-example value and the mathematics that defines the
symbols of equations (5.1) to (5.12).

Condensation round 2 of 2026-09-15 (CONDENSE2_BRIEF.md, Chapter 5 items;
prose 4952 to 4801 words). Two folds, no method, parameter, equation
number, figure, table, threshold, output state or printed number changed.
Section 5.1: the hip depth paragraph repeated the close of Section 2.6
sentence for sentence, so it keeps the data property in one sentence and
points at Section 2.6 for the checks and the depth memory. The G6
sentence naming which Chapter 7 solves rest on the preparation stays here
verbatim (orchestrator decision of 2026-09-15), as it does in Section 2.6
and Appendix G.4. Section 5.3: the Scene chain
was derived here and again in Sections 6.2 and 6.4, which own it, so the
three unnumbered displays (the mapped-marker chain, the camera chain and
the homogeneous form) and the handedness and conjugation commentary go,
replaced by one pointer sentence naming Sections 6.2 and 6.4. What
equations (5.1), (5.2) and (5.7) need stays defined here: Scene-o, R
(MappedMarker in Scene), the swap S with {MappedMarker} about the marker
centre, G, t_f and its height d, T (Scene to Camera') with its inverse,
and M-h. Section 5.6 still resolves: it names "the swap, gravity
alignment and floor placement of Section 5.3" and prints d = 71.62 cm.
No numbered equation was deleted, so nothing is renumbered. The symbols
P_WO, R_WO, R_WS, P_WS, R_SCENE_CAMERA and P_SCENE_CAMERA_ORG are left
defined above but are no longer used by any display.

Table 5.1 removed 2026-09-14 (readers are systems engineers; a value
stated once in the text is enough). Every one of its twenty symbol rows
is defined where the symbol first appears in the prose or the displayed
mathematics of this chapter, or in the chapter the "Comes from" column
named (Chapter 3, Chapter 4, Section 6.4); the S-1/S-2 defects above
therefore no longer apply to anything printed. The introductory sentence
of Section 5.3 that pointed to the table now says only that every symbol
is defined at first appearance.
"""
# D-073: current frame labels are Camera and Camera'; historical notes
# above retain the terminology of their original decisions. No numeric map changes.
# D-082: all shared Chapter 5 positions are now in Scene. G is the proper
# gravity-alignment operator; t_f includes the recording's floor placement.
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches

from eqn import r, nor, sub, sup, hat, frac, d, eqArr, mat, add_display_eq, \
    add_display_math, add_inline_math

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v9" / "figures"

H1, H2, H3, P, IMG, CAP, TBL, EQ = "h1", "h2", "h3", "p", "img", "cap", "tbl", "eq"
MATH = "mth"   # displayed, unnumbered mathematics
PM = "pm"      # paragraph mixing text runs and inline math
LIN = "lin"    # indented list line (the user's Case A/B/C style)
BUL = "bul"    # bullet item (supervisor comment C54, 2026-09-16)
NUM = "num"  # numbered item (C54 mechanics follow-up, 2026-09-16; see list_numbering.py)


def T(t):
    return ("t", t)


def X(f):
    return ("m", f)


def M(f):
    """A table cell holding inline math instead of text."""
    return ("m", f)


def nary(chr_, sub_, body):
    """OMML n-ary operator (used for the summations of Section 5.3)."""
    return (f'<m:nary><m:naryPr><m:chr m:val="{chr_}"/>'
            f'<m:limLoc m:val="undOvr"/><m:supHide m:val="1"/>'
            f'</m:naryPr><m:sub>{sub_}</m:sub><m:sup/>'
            f'<m:e>{body}</m:e></m:nary>')


# --- symbols -------------------------------------------------------------
p_sh = sub(r("p"), nor("sh"))
p_el = sub(r("p"), nor("el"))
p_wr = sub(r("p"), nor("wr"))
p12 = sub(r("p"), r("12"))
p14 = sub(r("p"), r("14"))
p16 = sub(r("p"), r("16"))
L1 = sub(r("L"), r("1"))
L2 = sub(r("L"), r("2"))
r_c = sub(r("r"), nor("c"))
n1 = sub(r("n"), r("1"))
n2 = sub(r("n"), r("2"))
u_perp = sub(r("u"), nor("⊥"))
p_c = sub(r("p"), nor("c"))
h_k = sub(r("h"), r("k"))
p_wr_k = sub(r("p"), nor("wr,") + r("k"))
o_k = sub(r("o"), r("k"))
bhat = hat(r("b"))
uhat = hat(r("u"))
fhat = hat(r("f"))
u_new = sub(hat(r("u")), nor("new"))
u_old = sub(hat(r("u")), nor("old"))
u_meas = sub(hat(r("u")), nor("meas"))
h_new = sub(r("h"), nor("new"))
h_old = sub(r("h"), nor("old"))
MINUS = r(" − ")
DOT = r(" · ")


# --- Craig frame notation ------------------------------------------------
# D-054 four classes, applied semantically; D-056 and D-058 fix the frame
# names; FRAME_INVENTORY.md sections 2, 7 and 8.9.5 assign the rows applied
# here. A left superscript names the reference frame, a left subscript the
# described frame, and a frame slot never holds a quantity. Word's
# pre-sub-superscript element is <m:sPre>.
# An empty Word script slot renders as a placeholder box, so a slot that
# carries no frame is filled with a zero-width space instead.
ZWS = r("\u200b")


def pre(base, sup_="", sub_=""):
    return ('<m:sPre><m:sPrePr/>'
            f'<m:sub>{sub_ or ZWS}</m:sub><m:sup>{sup_ or ZWS}</m:sup>'
            f'<m:e>{base}</m:e></m:sPre>')


PERSON = nor("Camera'")
SCENE = nor("Scene")
MAPPED = nor("MappedMarker")
WORLD = nor("World")
OBJECT = nor("Object")


def inP(e):
    return pre(e, PERSON)


def inScene(e):
    return pre(e, SCENE)


def inM(e):
    return pre(e, MAPPED)


TWO = pre(r("T"), WORLD, OBJECT)              # C5-05, the Chapter 4 pose
T_CAMERA_SCENE = pre(r("T"), PERSON, SCENE)          # full Scene -> Camera' map
T_SCENE_CAMERA = pre(r("T"), SCENE, PERSON)          # its inverse, Section 5.3
R_SCENE_MAPPED = pre(r("R"), SCENE, MAPPED)          # C5-03, was R_obj
R_SCENE_MAPPED_k = pre(sub(r("R"), r("k")), SCENE, MAPPED)
R_SCENE_MAPPED_kT = sup(d(R_SCENE_MAPPED_k), r("T"))
P_SCENE_ORG = pre(sub(r("P"), SCENE + nor("ORG")), PERSON)   # C5-34
# D-068/D-082: expose improper basis maps and retain G as an operator.
G = r("G")
t_f = sub(r("t"), nor("f"))
R_WO = pre(r("R"), WORLD, OBJECT)
P_WO = pre(sub(r("P"), nor("ObjectORG")), WORLD)
R_WS = pre(r("R"), WORLD, nor("Camera"))
P_WS = pre(sub(r("P"), nor("CameraORG")), WORLD)
R_SCENE_CAMERA = pre(r("R"), SCENE, PERSON)
P_SCENE_CAMERA_ORG = pre(sub(r("P"), nor("Camera'ORG")), SCENE)


def nrm(e):
    return d(e, "|", "|")


def nrm2(e):
    return sup(d(e, "|", "|"), r("2"))


content = [
(H1, "Chapter 5: Pose Recovery During Tracking Failure"),

# --- opening: transition from Chapter 4, scope, the cases, Figure 5.1
# Condensed for the C54 transitions round (2026-09-16): 403 words -> ~284.
# The Case A/B/C and measured/held/constrained content is kept close to
# verbatim in wording and length on the orchestrator's instruction, since
# other chapters cite this passage as "the chapter opening of Chapter 5"
# for the three states; that constraint, not the ~220-word target, sets
# the floor. See writing/v9/notes_c54_transitions_ch5_ch8.md.
(P, "Chapter 3 solves the joint angles from a fully measured chain, and Chapter 4 tracks the carried object in the same scene. Neither handles a frame with a missing wrist or a wrist whose depth belongs to the cube. When body landmarks become unreliable, object observations provide an additional geometric constraint on the region the arm can occupy. This layer applies that constraint between Chapter 2 and the solve of Chapter 3, treating occlusion as missing data on a torso that is assumed to be measured (Section 5.1)."),

(PM, [T("The arm chain has calibrated upper-arm length "),
      X(L1), T(" and forearm length "), X(L2),
      T(", and a missing landmark is rebuilt from the measured landmarks and the carried state in three cases.")]),
(BUL, "", "In Case A a missing wrist is placed at the forearm length from a measured elbow, along the remembered forearm direction (Section 5.3)."),
(BUL, "", "In Case B the wrist of a holding hand is placed from the measured object pose of Chapter 4 and the hand-object offset h (Section 5.4)."),
(BUL, "", "In Case C a missing elbow is placed by two-link inverse kinematics on the two calibrated lengths, from a measured shoulder and a measured or rebuilt wrist (Section 5.5)."),

(P, "Where no case anchors a landmark, the joint holds its last angle. The solve produces seven joint groups, the root and three per arm, and each leaves the layer in one of three states. A group is measured when every landmark it needs was measured and unflagged on this frame, held when it keeps the value it last had, and constrained when it was solved from a rebuilt landmark or with its change limited."),

(P, "The states travel with the angles into Chapters 6 and 7. Figure 5.1 draws this flow, from the Chapter 2 landmarks and the Chapter 4 object pose to the solve."),

(IMG, REPO / "writing" / "v9" / "figures" / "ch5_fig_flow.png", 6.3),
(CAP, "Figure 5.1. Information flow of the recovery layer in the Scene formulation of Section 5.3. Inputs from Chapters 2 to 4, the detectors, the three rebuild cases and the solve."),

# ---------------------------------------------------------------- 5.1
(H2, "5.1 Assumptions and Parameters"),

# Condensation round 2 of 2026-09-15: the mechanism of the preparation was
# folded into a pointer to Section 2.6, and the G6 sentence below was first
# dropped with it and then restored verbatim on the orchestrator's decision
# of the same day, because it states which Chapter 7 solves depend on the
# preparation rather than restating its rationale. It stands word for word
# in Chapter 2 Section 2.6, in Appendix G.4 and here, so fix decision G6
# and the comments in build_ch2.py and build_appendix.py hold. The claim
# was verified against the variant definitions when it was written: the
# solving
# variants run RobustChainSolver, which carries the preparation, while
# hold-last runs ChainFallbackSolver, which has none
# (eval/failure/run_recovery.py variant list; eval/failure/recovery_core.py
# lines 193 and 227-230; eval/failure/compare_hip_hold.py, "the hold-last
# solve, no preparation").
(P, 'The recovery rests on six assumptions, and Chapter 9 takes up the consequences of their failure. The recording is mostly clean: every landmark is measured on most frames, and a failure is a short window the recovery fills. The torso is measured on every frame, so the two hips and the two shoulders are taken as correct, landmark 24 above all, since it is the origin of the root frame of Chapter 3. A lost root frame is outside the scope of this thesis.'),

(P, 'The torso assumption needs one preparation of the recording. The hip landmarks take the depth of the rail in front of the pelvis, and the preparation of Section 2.6 replaces that depth outside this layer. The plain, direction-memory and object-assisted solves of Chapter 7 all rest on this preparation, and the hold-last solve, which keeps the last accepted joint angles, does not.'),

(P, "The grasp is rigid within one grip episode: the wrist keeps a fixed position in the mapped marker frame {MappedMarker} that Chapter 6 establishes, and a regrasp starts a new episode and a new offset. The object marker stays visible while the hand is hidden, since Case B needs a measured object pose on the frame it repairs. Where the marker is lost too, Case A or the held angle takes over. The upper arm and the forearm keep their calibrated lengths through the recording. The subject moves slowly, as the task of Chapter 2 is defined, so a segment direction changes little between frames and the direction memories of Section 5.3 can rely on it."),

(P, "The recovery needs parameters of three kinds. The calibrated constants are the upper-arm and forearm lengths, taken from the clean frames at the start of the recording or from an earlier calibration. The fixed mapping into {Camera'} of Section 5.3 is a calibrated constant as well. The design values were fixed before the recording. They are the detector thresholds, gains, radii, runs, bounds and limits, each defined with its rule in Sections 5.2 to 5.5. The states are estimated on clean frames and carried forward: the hand-object offset per grip episode, the holding state of each hand, and the direction memories of the two arms."),

# ---------------------------------------------------------------- 5.2
(H2, "5.2 Landmark Tracking Failures"),

(P, "A landmark can be wrong in two ways, and only one of them is announced. The source flag of Section 2.3 reports a usable point, a visibility score below the gate of that section, or a depth window with no valid depth sample (Appendix D). The last two are declared failures, already treated as missing. The second way is silent: the pixel is correct and the visibility score is high, but the depth behind it belongs to a hand, to the cube, or to the desk. The point is then lifted tens of centimetres from the body, and the visibility score cannot show it."),

(P, "Geometry shows it. Over a few frames the body is rigid: a limb segment cannot change length, the trunk cannot fold, and a landmark cannot jump across the scene. Each statement becomes a test per frame, and a frame that fails one carries a wrong measurement whatever the source flag says. The object supplies a sixth test: a hand that holds the cube cannot have its wrist far from it. Figure 5.2 draws the six tests."),


(IMG, FIG / "ch5_fig_detectors.png", 6.3),
(CAP, "Figure 5.2. The six failure detectors, one panel each: acquisition, segment-length and line-angle in the upper row, width-ratio, landmark-step and grip-plausibility in the lower. Red marks the firing condition."),

(P, "The acquisition detector is a report rather than a test: it fires on the source flags above. The four geometry detectors turn those statements into numbers, the trunk statement giving two. The segment-length detector compares the upper arm and forearm with the median of that segment over the clean frames, and fires at a departure of 35 percent. The line-angle detector measures the angle between the hip line and the shoulder line, close to parallel while the trunk is rigid, and fires above 22 degrees. The width-ratio detector compares the ratio of shoulder width to hip width with its clean median, and fires at a departure of 20 percent. The landmark-step detector measures the distance each landmark moved between two consecutive usable frames, and fires above 5 centimetres."),
# thresholds: eval/failure/detect_failures.py SEG_TOL 0.35,
# TORSO_LINE_TOL_DEG 22.0, WIDTH_RATIO_BAND 0.20, STEP_TOL_M 0.05;
# grip-plausibility bound GRIP_MAX 0.35 in eval/failure/recovery_core.py

(P, "The grip-plausibility detector uses the object. A wrist reported more than 35 centimetres, the release radius of Section 5.3, from the object centre while that hand holds the cube is a wrong measurement and not a release. That bound is a design choice for the cube and grip of this task, and its suitability elsewhere has not been established. The four geometry thresholds are properties of a human body and of a slow task, each set at the 99th percentile of the clean frames of a separate reference recording plus a safety margin. That recording is clean for the right arm and the torso, while its left arm has a defect that fires the segment-length detector. Widening the tolerance until it stops firing would calibrate the threshold to a defect, so it stays where the clean statistics put it."),

(P, "The per-frame results are combined into three failure masks, one per arm and one for the torso, each set whenever any of its detectors fires and then cleaned twice. Gaps of at most five frames are closed, and runs shorter than five frames are dropped. The grip-plausibility test runs afterwards, because it needs the holding state of Section 5.3, and whatever it flags is added to the arm mask."),

(P, "A flagged arm has its elbow and wrist landmarks removed before the solve, so the detectors turn a wrong measurement into a missing one. The layer reports the torso mask and rebuilds no torso landmark, since under the assumption of Section 5.1 the torso is measured on every frame, after the hip depth preparation named there. The two torso detectors only show the frames in which that assumption fails."),

# ---------------------------------------------------------------- 5.3
(H2, "5.3 Grip Episodes and the Hand-Object Offset"),

# Table 5.1 (the chapter's symbol table) removed 2026-09-14: the sentence
# below already said every symbol is defined where it first appears, and
# that check holds for all twenty rows: p_sh/p_el/p_wr and p12/p14/p16
# here; Scene-o, R (MappedMarker in Scene), G and t_f at the mapped-marker
# chain just below (with Chapter 4 and Sections 6.2 and 6.4 as their
# sources); N
# and c at equations (5.3)-(5.4); u-hat, f-hat and alpha at equation
# (5.5); L1, L2 at the opening of this section (Chapter 3, Section 5.1);
# the object-pose wrist estimate at equation (5.7); b, r, b-hat, j, p_c,
# r_c, n1, n2, s and u_perp across Section 5.5 (equations (5.9)-(5.12)).
# No symbol's definition is withdrawn; only the lookup table is.
(PM, [T("This chapter writes the three landmarks of one arm as "),
      X(p_sh), T(", "), X(p_el), T(" and "), X(p_wr),
      T(" for its shoulder, elbow and wrist. On the right side these are the points Chapter 3 numbers "),
      X(p12), T(", "), X(p14), T(" and "), X(p16),
      T(", and the left arm carries the same names. Every symbol is defined where it first appears, with its frame given there. In the displayed mathematics a left superscript names the frame a quantity is expressed in, and a left subscript the frame a rotation or a transformation describes.")]),

(P, "While a hand grips the cube and does not slide on it, the wrist is a fixed point of the object. The wrist is not on the marker: it sits on the side of the cube, at an offset that changes with every grasp and that nothing in the setup measures directly. The layer estimates it on the frames where both the wrist and the marker are measured, and carries it into the frames where the wrist is lost. Chapter 7 evaluates a wrist reconstructed this way against the unmasked reconstruction on frames where the wrist was measured and then withheld (Section 7.4.1), and against manually labelled wrist positions in the natural failure windows (Section 7.4.2)."),

(PM, [T("On a frame with a measured object pose, the layer receives an origin "),
      X(inScene(r("o"))), T(" and an orientation "), X(R_SCENE_MAPPED),
      T(". Chapter 4 supplies that pose in {World}, and Sections 6.2 and 6.4 derive the chain that carries it into the display frame {Scene}. The chain begins with the swap S, which also turns the object's own marker frame into the left-handed mapped marker frame {MappedMarker} about the same marker centre. It closes with the proper gravity-alignment operator "), X(G),
      T(" and the floor translation "), X(t_f),
      T(" of height d, which Section 6.4 fixes from the recording's calibrated tabletop position and the drawn desk height. The same chain, applied after the flip F of equation (3.1) and the calibrated sensor pose of Chapter 4, gives the fixed transformation "),
      X(T_SCENE_CAMERA),
      T(" from {Camera'} to {Scene}. Its inverse is "), X(T_CAMERA_SCENE),
      T(". Writing "), X(inM(r("h"))),
      T(" for the position of the wrist in the mapped marker axes, the wrist of a holding hand satisfies")]),

(EQ, inScene(p_wr) + r(" = ") + inScene(r("o")) + r(" + ") + R_SCENE_MAPPED + r(" ") + inM(r("h")), "5.1"),

(PM, [T("where "), X(inM(r("h"))),
      T(" is constant for as long as the grasp is rigid.")]),

(PM, [T("The layer computes the offset directly on a frame where both the wrist and the object are measured, with the wrist carried into {Scene} by "),
      X(T_SCENE_CAMERA),
      T(". The displacement from the origin to the wrist is pulled into the mapped marker axes by the transpose, the operation of equation (3.3),")]),

(EQ, inM(h_k) + r(" = ") + R_SCENE_MAPPED_kT + r(" ") + d(inScene(p_wr_k) + MINUS + inScene(o_k)), "5.2"),

(PM, [T("where "), X(r("k")),
      T(" is the frame index. The same floor translation occurs in both positions in equation (5.2) and cancels from their difference. It cancels a second time in the inverse transformation, so the implementation, which forms the offset before the display adds that translation, delivers the identical Camera' point to the solver. Figure 5.3 draws the two equations, on a clean frame and on a later frame where the object has moved and turned and the wrist is hidden.")]),

(IMG, REPO / "writing" / "v9" / "figures" / "ch5_fig_offset.png", 6.3),
(CAP, "Figure 5.3. The hand-object offset. (a) A clean frame, with the wrist and marker origin measured, equation (5.2). (b) The offset carried by the later object pose, equation (5.1)."),

(PM, [T("Each clean frame contributes one observation "), X(inM(h_k)),
      T(" of the same constant. A least squares fit of a single "), X(inM(r("h"))),
      T(" to "), X(r("N")),
      T(" clean frames minimizes the total squared distance between the measured wrists and the wrists equation (5.1) predicts. Because "),
      X(R_SCENE_MAPPED), T(" is orthonormal and leaves lengths unchanged, that objective has three equal forms:")]),

# D-076: prose establishes equality; each complete sum gets its own line.
# A leading binary equals sign renders as an error glyph in LibreOffice.
(MATH, eqArr(
    nary("∑", r("k"), nrm2(inScene(p_wr_k) + MINUS + inScene(o_k) + MINUS + R_SCENE_MAPPED_k + r(" ") + inM(r("h")))),
    nary("∑", r("k"), nrm2(R_SCENE_MAPPED_k + d(inM(h_k) + MINUS + inM(r("h"))))),
    nary("∑", r("k"), nrm2(inM(h_k) + MINUS + inM(r("h")))))),

(PM, [T("The rotation therefore drops out and the fit reduces to the mean of the observations,")]),

(EQ, inM(r("h")) + r(" = ") + frac(r("1"), r("N"))
     + nary("∑", r("k"), inM(h_k)), "5.3"),

(PM, [T("A single offset per recording will not do, because each new grasp puts the hand somewhere else on the cube. Each grasp is one grip episode, the unit the rest of this chapter and Chapters 8 and 9 work in, and the offset belongs to the episode. Within one long episode the hand also shifts a little, so the offset is estimated with a short memory instead of fitted once. On each frame that contributes a clean observation, the estimate moves towards that observation by a small gain "),
      X(r("c")), T(",")]),

(EQ, inM(h_new) + r(" = ") + d(r("1") + MINUS + r("c"))
     + r(" ") + inM(h_old) + r(" + ") + r("c") + r(" ") + inM(h_k), "5.4"),
# gain c = MU_ALPHA 0.02 in eval/failure/grip_state.py

(P, 'Equation (5.4) is a first-order recursive low-pass update, a smoother that can run on a stream of samples [55]. It mixes a little of the new observation into the previous estimate, so the estimate follows the current offset and forgets an old one. The gain of 0.02 weights it towards about the last fifty frames.'),

(P, 'The estimator has three further rules. A frame with no clean observation leaves the estimate untouched, so through a failure window the value in use is the offset from just before tracking was lost. The estimate restarts with each grip episode. Before five clean observations have initialized the local estimate, the mean of equation (5.3) over that episode stands in. This fallback uses the recording-wide fit if the episode has fewer than fifteen clean observations; once the local estimate is available, it takes priority. Flagged arm frames do not enter the local updates or episode means. The recording-wide fallback is fitted over the frames the instantaneous test of this section accepts, so it is gated by the conditions of that test rather than by the cleaned arm failure mask.'),
# MU_WARMUP 5, MU_MIN_FRAMES 15: eval/failure/grip_state.py

(P, "The estimate follows a shift of the grip with a lag set by the gain, so the value frozen at a failure can still carry the offset of the last clean frames. The grasp is also not always as rigid as Section 5.1 assumes. On the loop recording the hand wraps around the cube and shifts on it. Over the frames where the left hand holds the cube, the per-frame offset observations scatter with a standard deviation of 7.0, 2.7 and 6.3 centimetres on the three mapped marker axes. A non-rigid grip and the lag of the estimator are therefore two conditions under which the constraint the object supplies is itself wrong, and Section 7.4.2 reports their cost on the natural failure windows."),
# offset scatter: eval/reports/recording_20260825_222315_offset_fit.json
# (the loop recording, 2099 frames), per_hand.left.std_cm [7.0, 2.7, 6.3]
# over its 468 held frames; the right hand reads [7.0, 2.9, 8.1].  The
# earlier episode-restricted figures (scratchpad diagnostic of 2026-09-06,
# left episode 1110-1828, sd 6.2 / 2.7 / 6.5 cm) had no pinned report and
# were replaced by the pinned per-hand fit on 2026-09-11 (G2)

(P, "Equation (5.1) applies only to a hand that holds the object, so the layer must decide which hand that is. On a frame where everything is measured the decision takes five conditions together. The marker is measured, the object is away from its resting place, and the wrist is measured and unflagged. The wrist lies within the hold radius of the object centre, and the forearm of that arm measures within 30 percent of its own median length. The last condition rejects frames where the elbow and the wrist take their depth from the same near surface and collapse onto each other. The test needs a measured wrist, so the holding decision is carried as a state per hand, with rules for entering and leaving it."),
# five instantaneous conditions: eval/offset/carry.py holding_mask
# (det, carried, wrist flag, HOLD_RADIUS 0.25) and forearm_ok
# (FOREARM_TOL 0.30)

(P, 'The hand enters the holding state after the instantaneous test passes on five consecutive frames. It stays in that state through a wrist failure for as long as the object is still being carried. It leaves the state when the object comes to rest, or when a cleanly measured wrist sits farther than the release radius from the object centre, in either case over five consecutive frames. The release radius of 35 centimetres is wider than the hold radius of 25 centimetres, which stops the state flickering at the boundary. The run of frames between entry and exit is one grip episode. Both hands may hold at once, and a handover is two grip episodes that overlap. Figure 5.4 draws the state and its rules.'),

(P, 'In the offline preparation the state is set after the run that confirms it: an entry starts from the first frame of its five-frame run, and a confirmed exit clears the five frames of the exit run. The warm-up mean of an episode is likewise taken over the whole episode. Section 8.2 describes the version that decides with a delay instead.'),
# retrospective labels: eval/failure/grip_state.py grip_episodes
# (start = f - ENTER_FRAMES + 1; holding[stop + 1:f + 1] = False),
# fit_episode_mu over the whole episode; recovery_core.py fills the
# pre-warm-up frames with that episode mean
# ENTER_FRAMES/EXIT_FRAMES 5, RELEASE_RADIUS 0.35: eval/failure/
# grip_state.py; hold radius 0.25 in eval/offset/carry.py

(IMG, FIG / "ch5_fig_holding.png", 4.8),
(CAP, "Figure 5.4. The holding state of one hand: the five conditions of the instantaneous test, and the rules for entering, staying in and leaving the state."),

(PM, [T("The arm that is not holding gains nothing from the object, and its failures fall back on the direction memory. For every body segment the layer keeps a running average of the unit direction from the landmark nearer the trunk to the one farther from it. Writing "),
      X(uhat), T(" for the memory of the upper arm and "), X(u_meas),
      T(" for the direction measured on the current frame, the update on a frame where both ends are measured is")]),

(EQ, inP(u_new) + r(" = ") + frac(d(r("1") + MINUS + r("α")) + r(" ") + inP(u_old) + r(" + ") + r("α") + r(" ") + inP(u_meas),
                             nrm(d(r("1") + MINUS + r("α")) + r(" ") + inP(u_old) + r(" + ") + r("α") + r(" ") + inP(u_meas))), "5.5"),
# direction memory: dir_alpha 0.3 and the unit renormalisation in
# v1/kinematics/occlusion_ext.py _learn_dir

(PM, [T("with the gain α = 0.30, which weights the memory towards the last few frames. The forearm memory "),
      X(fhat),
      T(" follows equation (5.5) as well. The denominator scales the result back to unit length. The memory is updated only from measured landmarks, so nothing it holds was ever reconstructed.")]),

(PM, [T("Case A follows from this memory. A missing wrist whose elbow is measured is placed at the calibrated forearm length from the elbow, along the remembered forearm direction:")]),

(EQ, inP(p_wr) + r(" = ") + inP(p_el) + r(" + ") + L2 + r(" ") + inP(fhat), "5.6"),
# _try_recover in v1/kinematics/occlusion_ext.py: child = anchor +
# L[seg] * u[seg]; ARM_SEGS shoulder->elbow, elbow->wrist; horizon 45

(PM, [T("A missing elbow whose shoulder is measured is rebuilt by equation (5.6) with "),
      X(L1), T(" and "), X(uhat),
      T(", and Section 5.5 covers the case where the wrist is known and the elbow is placed from it instead. Direction memory rebuilds are allowed for at most forty-five consecutive frames on which the affected landmark farther from the trunk is unmeasured. The rebuild that Section 5.5 uses near full reach is one of them. The counter tracks that landmark, rather than the age of every segment-direction update. The two-link solve of Section 5.5 uses the remembered upper-arm direction without that counter check. When the counter prevents a rebuild, the affected joints hold their last angle, so a gap that nothing anchors is carried in angle space.")]),

# ---------------------------------------------------------------- 5.4
(H2, "5.4 Wrist Recovery From the Object Pose"),

(PM, [T("Case B applies to the holding hand. On a failure frame of a holding hand, the lost wrist is replaced by the point that equation (5.1) predicts from the current object pose and the current offset:")]),

(EQ, inScene(r("w")) + r(" = ") + inScene(r("o")) + r(" + ") + R_SCENE_MAPPED + r(" ") + inM(r("h")), "5.7"),

(PM, [T("The estimate "), X(inScene(r("w"))),
      T(" is a function of a same-frame measurement, and only the offset is carried from the past, on the short memory of Section 5.3. A wrist placed from its last direction drifts the longer the window lasts, while the object-derived wrist follows the cube and does not age. Case B therefore takes priority over Case A whenever the hand holds the cube and the marker is measured.")]),

(P, "Equation (5.7) does not by itself recover the wrist. It supplies one additional geometric constraint, from a measurement the failing branch does not have. The arm that leaves the layer depends on the current offset, the calibrated lengths, the chain constraints, the two-link geometry of Section 5.5 and the state carried from earlier frames."),

(P, "An offset longer than 30 centimetres does not describe a hand gripping a cube of a few centimetres, so the layer discards an estimate built on it and the frame falls back to Case A. The grip-plausibility detector of Section 5.2 removes a measured wrist that sits too far from the object its hand holds, and the object estimate takes over. A release is recognized only by the exit rule of the holding state."),
# MU_MAX 0.30 and GRIP_MAX 0.35 in eval/failure/recovery_core.py

(PM, [T("The wrist estimate of equation (5.7) is formed in {Scene}, including the gravity alignment and floor placement of Section 6.4, while the solve works in the y-up camera frame {Camera'} of Chapter 3. The fixed rigid body transformation "),
      X(T_CAMERA_SCENE),
      T(" of Section 5.3 therefore carries the estimate into that frame before the solve. It undoes the full scene mapping and changes no length and no angle.")]),

# ---------------------------------------------------------------- 5.5
(H2, "5.5 Elbow Recovery by Two-Link Inverse Kinematics"),

(PM, [T("Case C starts from a shoulder and a wrist. The upper arm and the forearm are two rigid links of known length, so placing the elbow is the two-link inverse kinematics problem of a planar manipulator lifted into three dimensions [42]. The two lengths are the calibrated "),
      X(L1), T(" and "), X(L2),
      T(" of Section 5.3. The construction below is written with the measured wrist "),
      X(inP(p_wr)),
      T(". On a failure frame of a holding hand the object-derived estimate "),
      X(inP(r("w"))),
      T(" of equation (5.7) takes its place, once carried into the y-up camera frame, and nothing else changes. The elbow is any point that satisfies both")]),

(EQ, nrm(inP(p_el) + MINUS + inP(p_sh)) + r(" = ") + L1 + r(",        ")
     + nrm(inP(p_el) + MINUS + inP(p_wr)) + r(" = ") + L2, "5.8"),

(PM, [T("The two conditions place the elbow on a sphere of radius "),
      X(L1), T(" about the shoulder and on a sphere of radius "),
      X(L2),
      T(" about the wrist. The spheres meet in a circle when their centres are closer than the sum of the radii and farther apart than the difference, and that circle is the set of all elbows consistent with the two endpoints.")]),

(PM, [T("Let "), X(r("b")),
      T(" be the vector from the shoulder to the wrist, "), X(r("r")),
      T(" its length, and "), X(bhat),
      T(" the unit vector along it. The triangle at the shoulder, the elbow and the wrist has sides "),
      X(L1), T(", "), X(L2), T(" and "), X(r("r")),
      T(", all known. The law of cosines fixes its angle "),
      X(r("j")),
      T(" at the shoulder, between the upper arm and the shoulder-to-wrist line:")]),

(EQ, nor("cos") + r(" ") + r("j") + r(" = ")
     + frac(sup(L1, r("2")) + r(" + ") + sup(r("r"), r("2")) + MINUS + sup(L2, r("2")),
            r("2") + r(" ") + L1 + r(" ") + r("r")), "5.9"),

(PM, [T("The perpendicular from the elbow to the shoulder-to-wrist line has its foot at a distance "),
      X(L1 + r(" ") + nor("cos") + r(" ") + r("j")),
      T(" from the shoulder, and length "),
      X(L1 + r(" ") + nor("sin") + r(" ") + r("j")),
      T(". Neither changes when the triangle turns about that line, so the foot is the centre "),
      X(p_c), T(" of the circle and the perpendicular is its radius "),
      X(r_c), T(":")]),

(EQ, inP(p_c) + r(" = ") + inP(p_sh) + r(" + ") + L1 + r(" ")
     + nor("cos") + r(" ") + r("j") + r(" ") + inP(bhat) + r(",        ")
     + r_c + r(" = ") + L1 + r(" ") + nor("sin") + r(" ") + r("j"), "5.10"),

(PM, [T("The circle lies in the plane through "), X(p_c),
      T(" perpendicular to "), X(bhat),
      T(". Let "), X(n1), T(" and "), X(n2),
      T(" be any two unit vectors that are perpendicular to each other and to "), X(bhat),
      T(", and let "), X(r("s")),
      T(" be the turn about the shoulder-to-wrist line that picks out a point of the circle. Every point of the circle is then")]),

(EQ, inP(p_el) + r(" = ") + inP(p_c) + r(" + ") + r_c
     + d(nor("cos") + r(" ") + r("s") + r(" ") + inP(n1) + r(" + ")
         + nor("sin") + r(" ") + r("s") + r(" ") + inP(n2)), "5.11"),

(PM, [T("The angle "), X(r("s")),
      T(" is the one degree of freedom the two endpoints do not determine, the swivel of the arm about the shoulder-to-wrist line, and Chapter 3 meets it as the shoulder twist that the elbow position cannot determine.")]),

(PM, [T("The direction memory of Section 5.3 picks the point, and here it is read without the age check of that section. It supplies the remembered upper-arm direction "),
      X(uhat),
      T(", and the elbow is placed at the point of the circle nearest that direction. That point follows by removing from the memory its component along the shoulder-to-wrist line, which leaves the perpendicular part "),
      X(u_perp),
      T(", and scaling that part to the radius:")]),

(EQ, inP(u_perp) + r(" = ") + inP(uhat) + MINUS + d(inP(uhat) + DOT + inP(bhat)) + r(" ") + inP(bhat)
     + r(",        ") + inP(p_el) + r(" = ") + inP(p_c) + r(" + ") + r_c + r(" ")
     + frac(inP(u_perp), nrm(inP(u_perp))), "5.12"),

(PM, [T('Equation (5.12) finds, in closed form, the point '), X(p_el), T(' on the circle closest to '), X(p_sh + r(' + ') + L1 + r(' ') + uhat), T(', the elbow the remembered direction would give if it were reachable.')]),

(PM, [T('The memory is unusable when the remembered direction lies along the shoulder-to-wrist line, or when no measured frame has been seen yet. A downward direction then replaces it, since a relaxed elbow hangs downward, and the depth axis of the y-up camera frame is the third candidate. These two fallback directions are perpendicular, so one always gives a point on the circle. Figure 5.5 draws the construction.')]),
# direction candidates in order (memory, (0, -1, 0), (0, 0, 1)):
# v1/kinematics/occlusion_ext.py _ik_elbow

(IMG, REPO / "writing" / "v9" / "figures" / "ch5_fig_ik.png", 6.3),
(CAP, "Figure 5.5. The elbow reconstruction. Spheres of radius L1 and L2 meet in the circle of equation (5.11). The direction memory, in orange, selects the point in the inset."),

(P, "The construction is exact only while the shoulder-to-wrist distance lies between the difference and the sum of the two link lengths. Outside that range no elbow satisfies both conditions of equation (5.8), and the layer clips the cosine of equation (5.9) into its valid range instead. A wrist estimate beyond the reach of the two links clips the cosine at one, the circle radius of equation (5.10) falls to zero, and the elbow collapses onto the shoulder-to-wrist line as a straight arm pointing at the object. A wrist closer to the shoulder than the difference of the lengths pushes the cosine above one as well, since the upper arm is the longer link, and clips at the same end. In both cases the elbow keeps the upper-arm length, while the forearm is left longer or shorter than its calibrated value."),
# clipping: v1/kinematics/occlusion_ext.py _ik_elbow; the inner case
# with L1 > L2 gives cos j > 1 (recovery_review.txt R1: L1 0.317,
# L2 0.205, r 0.05 gives 1.92)

(P, "A single configuration has no answer: a wrist estimate that coincides with the shoulder leaves the shoulder-to-wrist line without a direction, so the two-link solve returns nothing. The elbow is then placed from the shoulder along the upper-arm memory, and the groups that use it leave the layer constrained, not held. Only without a fresh memory does the arm fall back on holding its last angles."),

(PM, [T("Equation (5.9) is ill conditioned near a straight arm: the sensitivity of "),
      X(r("j")), T(" to "), X(r("r")),
      T(" grows without bound as "), X(r("r")), T(" approaches "),
      X(L1 + r(" + ") + L2),
      T(". The elbow is therefore taken from the direction memory above 98 percent of the full reach, with the wrist still anchored at the object-derived estimate, so on those frames the forearm is not in general at its calibrated length either. The two-link solution stays as the fallback where no fresh memory exists.")]),
# reach guard 0.98 of L1+L2 in v1/kinematics/occlusion_ext.py

(P, 'The layer applies two rules to the angles after the solve. The shoulder twist is read from the part of the forearm perpendicular to the upper arm, and that part vanishes as the elbow straightens, as Section 3.4.3 sets out. A twist solved from measured landmarks keeps its previous value below 15 degrees of elbow flexion, and its group leaves the layer held. The hold is released only above 25 degrees. The hold does not reach a twist solved on a rebuilt arm: that group has already left the layer constrained, and below 15 degrees of flexion its twist is bounded only by the rate limit that follows.'),

(P, 'The layer then limits each arm angle to 15 degrees of change between consecutive frames. While the limit is active the group is marked constrained until the limited and the solved value agree again. The limit applies to the arm angles and not to the root.'),
# twist hold tags the group HELD; only the rate limiter produces a
# CONSTRAINED tag without a rebuilt landmark: v1/kinematics/occlusion_ext.py.
# The hold tests the live bit, which a recovered group has already lost,
# so constrained twists pass it (recovery_review.txt R2, frames 7-9)

# ---------------------------------------------------------------- 5.6
(H2, "5.6 Worked Example: Frames 549 and 560"),

(P, "The recovery now runs on one real frame, as Section 3.5 did for the solve. The frame comes from the rail recording, under a second after frame 533 of that section, and it is the one frame of the worked examples on which something is lost, so the recovery has work to show. From frame 550 the landmark detector stops reporting a usable right wrist for about three seconds while the hand slides the cube along the rail, and the acquisition detector of Section 5.2 fires on the right arm. The example takes frame 560, ten frames in, with the right elbow and wrist removed together and both rebuilt, as Section 5.2 sets out. It solves that frame from the state left by frame 549, the last clean wrist frame before the window. The torso landmarks and the right shoulder are reported, with the hip depth replaced by the preparation of Section 2.6. The right hand holds the cube and the marker is measured, so Case B places the wrist and Case C places the elbow. Figure 5.6 puts the two frames side by side."),

(IMG, FIG / "ch5_fig_frames_549_560.png", 5.0),
(CAP, "Figure 5.6. (a) Frame 549, the last clean frame of the right arm. (b) Frame 560, solved from that state, with the elbow and wrist rebuilt."),

(PM, [T("The layer receives the right shoulder in the y-up camera frame and the two lengths of the right arm calibrated on the clean frames of this recording. The Chapter 4 object pose is expressed in {Scene} by the swap, gravity alignment and floor placement of Sections 6.2 and 6.4, with d = 71.6 cm on this recording:")]),
(MATH, eqArr(
    inP(p_sh) + r(" = (−0.16, 0.34, 1.32)"),
    L1 + r(" = 31.7 cm,        ") + L2 + r(" = 20.5 cm"),  # round 5 (C48): centimetres, one decimal (were 0.317 m, 0.205 m)
    inScene(r("o")) + r(" = (−0.22, 0.79, 0.45)"),
    R_SCENE_MAPPED + r(" = ") + mat([
        [r("1.00"), r("0.03"), r("0.04")],
        [r("−0.04"), r("−0.09"), r("0.99")],
        [r("0.03"), r("−1.00"), r("−0.09")]]))),

(PM, [T("The current offset is the recursive estimate of equation (5.4). Its last update came on frame 549, the last clean wrist frame before the window, and it is frozen from there on:")]),
(MATH, inM(r("h")) + r(" = (0.01, −0.04, 0.05),        ") + nrm(inM(r("h"))) + r(" = 0.07 m")),
(P, "The offset is inside the bound of Section 5.4. Equation (5.7) turns it into Scene axes and adds it to the object origin:"),
(MATH, eqArr(
    R_SCENE_MAPPED + r(" ") + inM(r("h")) + r(" = (0.01, 0.06, 0.04)"),
    inScene(r("w")) + r(" = ") + inScene(r("o")) + r(" + ") + R_SCENE_MAPPED + r(" ") + inM(r("h")) + r(" = (−0.21, 0.85, 0.48)"))),
(P, "The wrist lands just above the marker origin."),

(PM, [T("The inverse mapping derived in Section 5.3 gives the fixed transformation "),
      X(T_CAMERA_SCENE),
      T(" from {Scene} to the y-up camera frame {Camera'}. For this recording it is")]),
(MATH, T_CAMERA_SCENE + r(" = ") + mat([
    [r("1.00"), r("−0.04"), r("0.02"), r("0.05")],
    [r("0.04"), r("1.00"), r("−0.05"), r("−0.90")],
    [r("−0.02"), r("0.05"), r("1.00"), r("0.51")],
    [r("0"), r("0"), r("0"), r("1")]])),
(PM, [T("Its rotation block is close to the identity, since the two sets of axes are nearly parallel here, and its last column is "),
      X(P_SCENE_ORG),
      T(", the Scene origin on the drawn floor expressed in the y-up camera frame. Applied to "),
      X(inScene(r("w"))), T(", it gives the wrist estimate the solve receives:")]),
(MATH, mat([[inP(r("w"))], [r("1")]]) + r(" = ") + T_CAMERA_SCENE + r(" ") + mat([[inScene(r("w"))], [r("1")]])),
(MATH, inP(r("w")) + r(" = (−0.19, −0.09, 1.04)")),
(P, "The estimate lies about three centimetres from the wrist measured on frame 549."),

(PM, [T("Case C now has a shoulder and a wrist. The vector between them, its length and its unit vector are")]),
(MATH, eqArr(
    inP(r("b")) + r(" = ") + inP(r("w")) + MINUS + inP(p_sh) + r(" = (−0.02, −0.43, −0.27)"),
    r("r") + r(" = 50.7 cm,        ") + inP(bhat) + r(" = (−0.04, −0.84, −0.54)"))),
(P, "The wrist lies at 97 percent of the full reach of 52.2 cm, under the 98 percent guard of Section 5.5, so the two-link solve runs on a nearly straight arm. The law of cosines of equation (5.9) gives the angle at the shoulder:"),
(MATH, nor("cos") + r(" ") + r("j") + r(" = ")
       + frac(sup(r("31.7"), r("2")) + r(" + ") + sup(r("50.7"), r("2")) + MINUS + sup(r("20.5"), r("2")),
              r("2 · 31.7 · 50.7")) + r(" = 0.98,        ") + r("j") + r(" = 11.0°")),  # round 5 (C48): lengths in cm (were 0.317, 0.507, 0.205 m); (1004.89 + 2570.49 - 420.25) / 3214.38 = 0.9816, acos 11.0 deg
(P, "Equation (5.10) then places the centre of the circle on the shoulder-to-wrist line and fixes its radius:"),
(MATH, eqArr(
    inP(p_c) + r(" = ") + inP(p_sh) + r(" + ") + L1 + r(" ") + nor("cos") + r(" ") + r("j") + r(" ") + inP(bhat) + r(" = (−0.18, 0.07, 1.15)"),
    r_c + r(" = ") + L1 + r(" ") + nor("sin") + r(" ") + r("j") + r(" = 0.06 m"))),
(P, "The circle of possible elbows is small because the arm is nearly straight, so the free turn about the shoulder-to-wrist line can move the elbow by about twelve centimetres."),

(PM, [T("The direction memory of the upper arm was last updated on frame 549. Equation (5.12) removes from it the component along the shoulder-to-wrist line:")]),
(MATH, eqArr(
    inP(uhat) + r(" = (−0.11, −0.91, −0.39),        ") + inP(uhat) + DOT + inP(bhat) + r(" = 0.98"),
    inP(u_perp) + r(" = ") + inP(uhat) + MINUS + d(inP(uhat) + DOT + inP(bhat)) + r(" ") + inP(bhat) + r(" = (−0.07, −0.09, 0.14),        ") + nrm(inP(u_perp)) + r(" = 0.18"))),
(P, "The memory points almost along the shoulder-to-wrist line, and the projection leaves less than a fifth of its length. Scaling that part to the radius gives the elbow:"),
(MATH, inP(p_el) + r(" = ") + inP(p_c) + r(" + ") + r_c + r(" ") + frac(inP(u_perp), nrm(inP(u_perp))) + r(" = (−0.20, 0.04, 1.20)")),

(P, "Both conditions of equation (5.8) hold on the result: the elbow lies 31.7 cm from the shoulder and 20.5 cm from the wrist. It lies six millimetres from the elbow measured on frame 549. The placed upper arm is 0.7 degrees from the remembered direction, so the elbow has moved as little as the new wrist allows. The solve of Chapter 3 then runs on the assembled points and reads an elbow flexion of −28.1 degrees in the convention of Section 3.4.3. The three right-arm groups leave the layer in the constrained state, since two of their landmarks were rebuilt, and so does the root, whose hips carry a replaced depth."),

# Condensed for the C54 transitions round (2026-09-16): 118 words -> 66;
# cross-reference updated, Section 9.4 -> Section 9.3 (Chapter 9 renumbering).
(P, "The layer hands the solve of Chapter 3 an assembled set of landmarks on every frame, with each joint group tagged measured, held or constrained. Chapter 6 transmits these states. The value of the constraint depends on the object being visible and on the conditions Section 5.4 lists. Section 7.4 evaluates it, and Chapter 9 reads the two outcomes. Chapter 8 describes the causal version of the layer."),
# numbers: writing/v9/scripts/ch5_worked_example.py (rail recording,
# frame 560, recovery_r6b pipeline state); no Case A frame exists in
# either recording (script docstring)

]

# --- build ---------------------------------------------------------------
doc = Document()
style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(12)

# D-106: unnumbered display ordinals continuing into the following clause.
DISPLAY_COMMAS = {9, 2}
math_display_index = 0

for item in content:
    kind = item[0]
    if kind == H1:
        doc.add_heading(item[1], level=1)
    elif kind == H2:
        doc.add_heading(item[1], level=2)
    elif kind == H3:
        doc.add_heading(item[1], level=3)
    elif kind == P:
        doc.add_paragraph(item[1])
    elif kind == LIN:
        p = doc.add_paragraph(item[1])
        p.paragraph_format.left_indent = Inches(0.3)
    elif kind == PM:
        p = doc.add_paragraph()
        for typ, val in item[1]:
            if typ == "t":
                p.add_run(val)
            else:
                add_inline_math(p, val)
    elif kind == EQ:
        add_display_eq(doc, item[1], item[2])
    elif kind == MATH:
        math_display_index += 1
        add_display_math(doc, item[1],
                         punctuation="," if math_display_index in DISPLAY_COMMAS else ".")
    elif kind == IMG:
        path = Path(item[1])
        assert path.exists(), f"missing figure: {path}"
        doc.add_picture(str(path), width=Inches(item[2]))
        if path.name == "ch5_fig_offset.png":
            doc.paragraphs[-1].paragraph_format.keep_with_next = True
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
    elif kind == TBL:
        rows = item[1]
        t = doc.add_table(rows=len(rows), cols=len(rows[0]))
        t.style = "Table Grid"
        for i, row_ in enumerate(rows):
            for j, cval in enumerate(row_):
                cell = t.cell(i, j)
                par = cell.paragraphs[0]
                if isinstance(cval, tuple) and cval[0] == "m":
                    add_inline_math(par, cval[1])
                    continue
                if isinstance(cval, tuple):
                    # text followed by an inline math symbol
                    run = par.add_run(cval[0])
                    run.font.size = Pt(10)
                    add_inline_math(par, cval[1])
                    continue
                cell.text = cval
                for par in cell.paragraphs:
                    for run in par.runs:
                        run.font.size = Pt(10)
                        if i == 0:
                            run.font.bold = True

out = REPO / "writing" / "v9" / "Chapter_5_Pose_Recovery.docx"
from list_numbering import restart_numbered_lists
restart_numbered_lists(doc)

doc.save(out)
print("saved", out, "| items:", len(content))

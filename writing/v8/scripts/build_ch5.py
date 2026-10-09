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
limit), 5.6 Worked Example (one failure frame of the loop recording
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

Figures: writing/v8/figures/ch5_fig_flow.png (make_ch5_flow_fig.py),
ch5_fig_detectors.png and ch5_fig_ik.png (unchanged from V7,
writing/v7/scripts/make_ch5_detectors_fig.py, make_ch5_ik_fig.py),
ch5_fig_offset.png (make_ch5_offset_fig.py), ch5_fig_holding.png
(make_ch5_holding_fig.py). ch5_fig_states.png and its script were
removed with the output-states section.
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches

from eqn import r, nor, sub, sup, hat, frac, d, eqArr, mat, add_display_eq, \
    add_display_math, add_inline_math

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v8" / "figures"

H1, H2, H3, P, IMG, CAP, TBL, EQ = "h1", "h2", "h3", "p", "img", "cap", "tbl", "eq"
MATH = "mth"   # displayed, unnumbered mathematics
PM = "pm"      # paragraph mixing text runs and inline math
LIN = "lin"    # indented list line (the user's Case A/B/C style)


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
R_obj = sub(r("R"), nor("obj"))
R_objT = sup(sub(r("R"), nor("obj")), r("T"))
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
R_obj_k = sub(r("R"), nor("obj,") + r("k"))
R_objT_k = sup(sub(r("R"), nor("obj,") + r("k")), r("T"))
bhat = hat(r("b"))
uhat = hat(r("u"))
fhat = hat(r("f"))
u_new = sub(hat(r("u")), nor("new"))
u_old = sub(hat(r("u")), nor("old"))
u_meas = sub(hat(r("u")), nor("meas"))
h_new = sub(r("h"), nor("new"))
h_old = sub(r("h"), nor("old"))
TWO = sub(r("T"), nor("WO"))
MINUS = r(" − ")
DOT = r(" · ")


def nrm(e):
    return d(e, "|", "|")


def nrm2(e):
    return sup(d(e, "|", "|"), r("2"))


content = [
(H1, "Chapter 5: Pose Recovery During Tracking Failure"),

# --- opening: transition from Chapter 4, scope, the cases, Figure 5.1
(P, "Chapter 4 ended with the cleaned object track: for every frame, either a measured pose of the cube in the world frame or a marked gap. Chapter 3 solved the joint angles from the eight filtered landmarks of Chapter 2, and it assumed that all eight are present and correct on every frame. Over a recording that assumption fails on some frames. The hand wraps around the cube it carries, an arm passes in front of the trunk, and the landmark detector then either reports no point or reports a point whose depth belongs to another surface. This chapter handles those frames. It sits between the filtering of Chapter 2 and the solve of Chapter 3, and it uses the object track of Chapter 4 as the measurement that survives while the hand is hidden."),

(P, "The chapter treats occlusion as missing data in an otherwise clean recording. Most frames carry every landmark, and the missing points come in short windows. The torso landmarks are taken as measured on every frame, so the root frame of Chapter 3 is always available and the recovery works on the arms. Section 5.1 states these assumptions and names the parameters the recovery needs."),

(PM, [T("The arm chain of Chapter 3 runs from the shoulder through the elbow to the wrist, with the calibrated upper-arm length "),
      X(L1), T(" and forearm length "), X(L2),
      T(". A missing landmark is rebuilt from the landmarks that are still measured and from state carried over from earlier frames. The chapter covers three cases. In Case A the wrist is missing and the shoulder and elbow are measured. The wrist is then placed at the forearm length from the elbow, along the remembered direction of the forearm (Section 5.3). In Case B the wrist is missing while that hand holds the cube. The wrist is then placed from the measured object pose of Chapter 4 and the hand-object offset h (Section 5.4). Case B takes priority over Case A, because the object pose is measured on the same frame. In Case C the elbow is missing and the shoulder and wrist are known, measured or rebuilt. The elbow is then placed by two-link inverse kinematics on the two calibrated lengths (Section 5.5).")]),

(P, "Where no case anchors a landmark, the joint that needs it holds its last angle, and the output says so. The solve of Chapter 3 produces seven joint groups, the root and three per arm, and each group leaves the layer in one of three states. A group is measured when every landmark it needs was measured and unflagged on this frame. It is held when it keeps the value it last had, and it is constrained when it was solved on this frame from a rebuilt landmark or with its change limited. The states travel with the angles: Chapter 6 draws a held joint and a rebuilt joint in different colours, and Chapter 7 separates the frames that carry a measurement from the frames that carry a reconstruction."),

(P, "Figure 5.1 draws the information flow of the chapter. The filtered landmarks of Chapter 2 enter with their source flags, and the failure detectors of Section 5.2 remove the ones that are wrong. The rebuild stage replaces what it can, using the calibrated lengths of Chapter 3 and the object pose of Chapter 4. The unchanged solve of Chapter 3 then runs on the assembled points, and each of its seven joint groups leaves with a state that Chapter 6 draws and Chapter 7 evaluates."),

(IMG, FIG / "ch5_fig_flow.png", 6.3),
(CAP, "Figure 5.1. Information flow of the recovery layer. The inputs on the left come from Chapters 2 to 4. The detectors remove wrong landmarks, the three rebuild cases replace what they can, and the solve of Chapter 3 runs unchanged. The holding state, the offset and the direction memories are carried from frame to frame. The joint groups leave with a state each, for Chapter 6 and Chapter 7."),

# ---------------------------------------------------------------- 5.1
(H2, "5.1 Assumptions and Parameters"),

(P, "The recovery rests on six assumptions about the recording and the subject, and each one can fail. Chapter 9 lists what happens when it does. The recording is mostly clean: every landmark is measured on most frames, and a failure is a short window. The recovery fills such windows and does not track a hidden arm for long. The torso is measured on every frame. The two hips and the two shoulders are taken as correct, and landmark 24 in particular, which is the origin of the root frame of Chapter 3, so the root frame exists on every frame. Loss of the root frame is outside the scope of this thesis. The two torso detectors of Section 5.2 report the frames on which this assumption fails, and Chapter 7 shows where they fire."),

(P, "The grasp is rigid within one grip episode. While a hand holds the cube, the wrist keeps a fixed position in the object's frame, and a regrasp starts a new episode and a new offset. The object marker stays visible while the hand is hidden. Case B needs a measured object pose on the frame it repairs, and where the marker is lost as well, Case B is unavailable and Case A or the held angle takes over. The bone lengths are constant, so the upper arm and the forearm keep their calibrated lengths through the recording. The subject moves slowly, as the task of Chapter 2 is defined. A landmark cannot jump across the scene between two frames, and the direction of a segment changes little from one frame to the next. The direction memories of Section 5.3 rely on this."),

(P, "The recovery needs parameters of three kinds, and the section that introduces each one states its value. The calibrated constants of the recording are the upper-arm and forearm lengths, taken from the clean frames at the start of the recording or supplied from an earlier calibration (Section 5.3), and the fixed transformation of the scene calibration that carries a world-frame point into person space (Section 2.2.2). The design values were fixed before the recording, and each is stated where its rule is defined: the detector thresholds and the mask cleaning in Section 5.2, the offset gain, the hold and release radii, the entry and exit runs, and the direction memory gain and horizon in Section 5.3, the offset bound in Section 5.4, and the reach guard, the twist hold and the rate limit in Section 5.5. The states are estimated on clean frames of the recording itself and carried forward: the hand-object offset h fitted per grip episode, the holding state of each hand, and the direction memories of the two arms. No parameter is fitted on a flagged frame."),

# ---------------------------------------------------------------- 5.2
(H2, "5.2 Landmark Tracking Failures"),

(P, "A landmark can be wrong in two ways, and only one of them is announced. MediaPipe attaches a source flag to every sample (Section 2.3). The flag says whether the point was usable, whether its visibility score fell below the gate, and whether the depth window around its pixel held no valid depth sample. A sample with either of the last two flags is a declared failure, and the pipeline already treats it as missing. The second way is silent. The pixel is correct and the visibility score is high, but the depth reading behind that pixel belongs to a hand, to the carried cube, or to the desk in front of the subject. The point is then lifted to a position tens of centimetres away from the body. The visibility score cannot show this, because it describes the image and not the depth."),

(P, "Geometry shows it. Over a few frames the body is rigid: a limb segment cannot change length, the trunk cannot fold, and a landmark cannot jump across the scene between two frames of a slow task. Each statement becomes a test per frame. A frame that fails one of them carries a wrong measurement, whatever the detector says about it. A further test uses the object: a hand that holds the cube cannot have its wrist far away from it. Figure 5.2 draws the six tests."),


(IMG, FIG / "ch5_fig_detectors.png", 6.3),
(CAP, "Figure 5.2. The six failure detectors, one panel each. The dark skeleton is the correct geometry and the red element is the condition that fires the detector. The conditions are a declined sample, a segment whose measured length departs from its calibrated value, and a hip line and a shoulder line that no longer agree. The lower row shows a shoulder width and hip width whose ratio has changed, a landmark that moved too far since the previous frame, and a wrist reported far from the object its hand is holding."),

(P, "The acquisition detector is a report rather than a test. It fires wherever the landmark detector marks a sample as low in visibility or without depth. The four geometry detectors turn the rigid-body statements into numbers, and the trunk statement gives two of them. The segment-length detector compares the current upper arm and forearm of an arm with the median of that segment over the clean frames of the recording, and fires at a departure of 35 percent. For the torso, the line-angle detector measures the angle between the hip line and the shoulder line, which stay close to parallel while the trunk is one rigid plate, and fires above 22 degrees. The width-ratio detector compares the ratio of shoulder width to hip width with its clean median, since that ratio is fixed by the subject's build, and fires at a departure of 20 percent. The landmark-step detector measures how far each landmark moved between two consecutive frames on which it was reported usable, and fires above 5 centimetres."),
# thresholds: eval/failure/detect_failures.py SEG_TOL 0.35,
# TORSO_LINE_TOL_DEG 22.0, WIDTH_RATIO_BAND 0.20, STEP_TOL_M 0.05;
# grip-plausibility bound GRIP_MAX 0.35 in eval/failure/recovery_core.py

(P, "The grip-plausibility detector uses the object. While a hand holds the cube, the wrist and the object move together, so a wrist reported more than 0.35 metres from the object centre, the release radius of Section 5.3, is a wrong measurement and not a release. This bound is a statement about a hand and a hand-held object, so it transfers to any recording. The four geometry thresholds are properties of a human body and of a slow task. Their values come from the same statistics on a separate reference recording. Each threshold is set at the 99th percentile of that recording's clean frames plus a safety margin. The reference recording is clean for the right arm and for the torso. Its left arm is not clean: for a stretch of frames the elbow slides along the limb while the upper arm and the forearm trade length. The segment-length detector fires on that stretch. Widening the tolerance until it stops firing would calibrate the threshold to a defect, so the threshold stays where the clean statistics put it."),

(P, "The per-frame results are combined into three failure masks, one per arm and one for the torso. A mask is set whenever any of its detectors fires. Each mask is then cleaned twice. Gaps of at most five frames are closed, so one frame on which the landmark detector recovers does not split a failure in two. Runs shorter than five frames are dropped, so one noisy frame does not open a failure window. The grip-plausibility test runs on the cleaned masks, because it needs the holding state of Section 5.3, and that state is built on the cleaned masks. Whatever it flags is added to the arm mask afterwards."),

(P, "A flagged arm has its elbow and wrist landmarks removed before the solve. The detectors turn a wrong measurement into a missing one, because the solve of Chapter 3 knows what to do with an absent landmark and has no defence against one that is present and wrong. The layer reports the torso mask and does not act on it. Under the assumption of Section 5.1 the torso is measured on every frame, and the two torso detectors only show where that assumption fails. The rest of the chapter is about what can be put back in place of the removed arm points. The recovery starts from the object marker, because it stays measured through the windows in which the landmark detector fails: the marker sits on the carried cube, in clear view of the sensor, while the hand that carries it is hidden behind it."),

# ---------------------------------------------------------------- 5.3
(H2, "5.3 Grip Episodes and the Hand-Object Offset"),

(PM, [T("This chapter writes the three landmarks of one arm as "),
      X(p_sh), T(", "), X(p_el), T(" and "), X(p_wr),
      T(" for its shoulder, elbow and wrist. On the right side these are the points Chapter 3 numbers "),
      X(p12), T(", "), X(p14), T(" and "), X(p16),
      T(", and the left arm carries the same three names. Table 5.1 lists every symbol the chapter uses, with the frame it is expressed in and where it comes from. Each symbol is also defined where it first appears.")]),

(TBL, [["Symbol", "Meaning", "Frame", "Comes from"],
       [M(p_sh + r(", ") + p_el + r(", ") + p_wr), "shoulder, elbow and wrist landmarks of one arm", "person space P", "Chapter 3"],
       [M(r("o")), "origin of the object frame", "levelled world frame W", "Chapter 4, translation column of " ],
       [M(R_obj), "orientation of the object frame", "levelled world frame W", "Chapter 4, rotation block of "],
       [M(r("h")), "hand-object offset: the wrist position in the object's axes", "object frame O", "equation (5.3), per grip episode"],
       [M(h_k), "observation of the offset on frame k", "object frame O", "equation (5.2)"],
       [M(r("N")), "number of clean frames in a fit", "", "equation (5.3)"],
       [M(r("c")), "gain of the offset update, 0.02", "", "equation (5.4)"],
       [M(uhat + r(", ") + fhat), "direction memory of the upper arm and of the forearm, unit vectors", "person space P", "equation (5.5)"],
       [M(r("α")), "gain of the direction memories, 0.30", "", "equation (5.5)"],
       [M(L1 + r(", ") + L2), "calibrated upper-arm and forearm lengths", "", "Chapter 3"],
       [M(r("w")), "wrist estimate from the object pose", "levelled world frame W, then P", "equation (5.7)"],
       [M(r("b") + r(", ") + r("r") + r(", ") + bhat), "shoulder-to-wrist vector, its length, its unit vector", "person space P", "Section 5.5"],
       [M(r("j")), "angle at the shoulder between the upper arm and the shoulder-to-wrist line", "", "equation (5.9)"],
       [M(p_c + r(", ") + r_c), "centre and radius of the elbow circle", "person space P", "equation (5.10)"],
       [M(n1 + r(", ") + n2), "unit vectors spanning the plane of the elbow circle", "person space P", "equation (5.11)"],
       [M(r("s")), "turn about the shoulder-to-wrist line that picks a point of the circle", "", "equation (5.11)"],
       [M(u_perp), "the part of the upper-arm memory perpendicular to the shoulder-to-wrist line", "person space P", "equation (5.12)"]]),
(CAP, "Table 5.1. The symbols of this chapter. The object pose symbols o and R are the translation column and the rotation block of the world-frame object pose of Chapter 4, after levelling by the calibrated gravity direction."),

(P, "While a hand grips the cube and does not slide on it, the wrist is a fixed point of the object. The wrist is not on the marker. It sits somewhere on the side of the cube, at an offset from the marker origin that depends on how the subject took hold of the cube. That offset is not known in general. It changes with every grasp, and nothing in the setup measures it directly. In this work it is estimated from the frames on which both the wrist and the marker are measured, and the estimate is then carried into the frames where the wrist is lost. Chapter 7 reads the accuracy of a wrist reconstructed this way. There the wrist trajectory is compared with the reference path together with the marker trajectory, and the comparison shows how far the tracked and the reconstructed data sit from the ground truth."),

(PM, [T("The object pose is measured on every frame as an origin "),
      X(r("o")), T(" and an orientation "), X(R_obj),
      T(". Both come from Chapter 4 in the world frame of the scene, levelled by the gravity direction of the calibration, so that the offset is fitted in axes whose vertical is the physical vertical. Writing "),
      X(r("h")),
      T(" for the position of the wrist in the object's own axes, the wrist of a holding hand satisfies")]),

(EQ, p_wr + r(" = ") + r("o") + r(" + ") + R_obj + r(" ") + r("h"), "5.1"),

(PM, [T("where "), X(r("h")),
      T(" is constant for as long as the grasp is rigid.")]),

(PM, [T("The offset is fitted from the frames on which both the wrist and the object are measured. The measured wrist is carried into the same world frame by the fixed transformation of the scene calibration. On such a frame the layer reads the offset off directly: the displacement from the origin to the wrist is pulled into the object's axes by the transpose, the operation of equation (3.3),")]),

(EQ, h_k + r(" = ") + R_objT_k + r(" ") + d(p_wr_k + MINUS + o_k), "5.2"),

(PM, [T("where "), X(r("k")),
      T(" is the frame index. Figure 5.3 draws the two equations. Panel (a) shows a clean frame, where the displacement "),
      X(p_wr + MINUS + r("o")),
      T(" is measured in the world axes and read in the object axes as "),
      X(h_k),
      T(". Panel (b) shows a later frame, where the object has moved and turned and the wrist is hidden. The same offset, carried along the new object axes by equation (5.1), gives the wrist.")]),

(IMG, FIG / "ch5_fig_offset.png", 6.3),
(CAP, "Figure 5.3. The hand-object offset. (a) On a clean frame the displacement from the object origin o to the measured wrist is read in the object axes, equation (5.2). (b) On a later frame the object has moved and turned and the wrist is hidden; the same offset, carried by the measured object pose, places the wrist, equation (5.1)."),

(PM, [T("Each clean frame contributes one observation "), X(h_k),
      T(" of the same constant. Fitting a single "), X(r("h")),
      T(" to "), X(r("N")),
      T(" clean frames by least squares means minimising the total squared distance between the measured wrists and the wrists that equation (5.1) predicts. Substituting equation (5.2) into that sum, and using the fact that "),
      X(R_obj), T(" is orthonormal and leaves lengths unchanged, gives")]),

(MATH, nary("∑", r("k"), nrm2(p_wr_k + MINUS + o_k + MINUS + R_obj_k + r(" ") + r("h")))
       + r("  =  ")
       + nary("∑", r("k"), nrm2(R_obj_k + d(h_k + MINUS + r("h"))))
       + r("  =  ")
       + nary("∑", r("k"), nrm2(h_k + MINUS + r("h")))),

(PM, [T("so the rotation drops out and the fit reduces to the mean of the observations,")]),

(EQ, r("h") + r(" = ") + frac(r("1"), r("N"))
     + nary("∑", r("k"), h_k), "5.3"),

(PM, [T("A single offset per recording will not do. The subject may let go of the cube and take it again, and each new grasp puts the hand somewhere else on the cube. Each grasp is one grip episode, which is the unit the rest of this chapter and Chapters 8 and 9 work in, and the offset belongs to the episode and not to the recording. Within one long episode the hand also shifts a little. The offset is therefore estimated with a short memory instead of fitted once. On each frame that contributes a clean observation, the estimate moves towards that observation by a small gain "),
      X(r("c")), T(",")]),

(EQ, h_new + r(" = ") + d(r("1") + MINUS + r("c"))
     + r(" ") + h_old + r(" + ") + r("c") + r(" ") + h_k, "5.4"),
# gain c = MU_ALPHA 0.02 in eval/failure/grip_state.py

(P, "Equation (5.4) is a first-order recursive low-pass update, the cheapest smoother that can run on a stream of samples [55]. It mixes a little of the new observation into the previous estimate, so the estimate follows the offset in force now and forgets an offset from long ago. The gain of 0.02 weights the estimate towards about the last fifty frames. The estimator has three further rules. A frame that contributes no clean observation leaves the estimate untouched, so through a failure window the value in use is the offset from just before tracking was lost. The estimate restarts at the start of each grip episode, because a new grasp is a new offset. During a warm-up of five clean frames the mean of equation (5.3) over that episode stands in. An episode that never gathers fifteen clean frames has no mean worth taking, so it falls back to the offset fitted over the whole recording. No frame that a detector has flagged enters any fit."),
# MU_WARMUP 5, MU_MIN_FRAMES 15: eval/failure/grip_state.py

(P, "Equation (5.1) applies only to a hand that holds the object, so the layer must decide which hand that is. On a frame where everything is measured the decision takes five conditions together. The marker is measured, the object is away from its resting place, and the wrist is measured and unflagged. The wrist lies within the hold radius of the object centre, and the forearm of that arm measures within 30 percent of its own median length. The last condition rejects the frames where the elbow and the wrist take their depth from the same near surface and collapse onto each other, which would otherwise put a plausible wrist next to the cube. The test needs a measured wrist, and that wrist is missing on exactly the frames the recovery exists for. The holding decision is therefore carried as a state per hand, with rules for entering and leaving it."),
# five instantaneous conditions: eval/offset/carry.py holding_mask
# (det, carried, wrist flag, HOLD_RADIUS 0.25) and forearm_ok
# (FOREARM_TOL 0.30)

(P, "The hand enters the holding state after the instantaneous test passes on five consecutive frames. It stays in that state through a wrist failure for as long as the object is still being carried: an object that is moving, and that nobody was seen to release, is still in the hand that held it. It leaves the state when the object comes to rest, or when a cleanly measured wrist sits farther than the release radius from the object centre, in either case over five consecutive frames. The release radius of 0.35 metres is wider than the hold radius of 0.25 metres, so the state does not flicker at the boundary. The run of frames between the entry and the exit is one grip episode. Both hands may hold at once, and a handover is two grip episodes that overlap. Figure 5.4 draws the state and its rules."),
# ENTER_FRAMES/EXIT_FRAMES 5, RELEASE_RADIUS 0.35: eval/failure/
# grip_state.py; hold radius 0.25 in eval/offset/carry.py

(IMG, FIG / "ch5_fig_holding.png", 4.8),
(CAP, "Figure 5.4. The holding state of one hand: the five conditions of the instantaneous test, and the rules for entering the state, staying in it through a wrist failure, and leaving it."),

(PM, [T("The arm that is not holding gains nothing from the object, and its failures fall back on a second piece of carried state, the direction memory. For every body segment the layer keeps a running average of the unit direction from the landmark nearer the trunk to the one farther from it. Writing "),
      X(uhat), T(" for the memory of the upper arm and "), X(u_meas),
      T(" for the direction measured on the current frame, the update on a frame where both ends are measured is")]),

(EQ, u_new + r(" = ") + frac(d(r("1") + MINUS + r("α")) + r(" ") + u_old + r(" + ") + r("α") + r(" ") + u_meas,
                             nrm(d(r("1") + MINUS + r("α")) + r(" ") + u_old + r(" + ") + r("α") + r(" ") + u_meas)), "5.5"),
# direction memory: dir_alpha 0.3 and the unit renormalisation in
# v1/kinematics/occlusion_ext.py _learn_dir

(PM, [T("with the gain α = 0.30, which weights the memory towards the last few frames. The forearm memory "),
      X(fhat),
      T(" follows the same rule. The denominator scales the result back to unit length, because the weighted sum of two unit vectors is shorter than either. The memory is updated only from measured landmarks, so nothing an arm's memory holds was ever reconstructed. Equation (5.4) is the same update with the gain "),
      X(r("c")), T(" and without the scaling.")]),

(PM, [T("Case A of the chapter opening follows from this memory. A missing wrist whose elbow is measured is placed at the calibrated forearm length from the elbow, along the remembered forearm direction:")]),

(EQ, p_wr + r(" = ") + p_el + r(" + ") + L2 + r(" ") + fhat, "5.6"),
# _try_recover in v1/kinematics/occlusion_ext.py: child = anchor +
# L[seg] * u[seg]; ARM_SEGS shoulder->elbow, elbow->wrist; horizon 45

(PM, [T("This is forward kinematics on the memory: the chain of Chapter 3 is stepped one segment forward with the last known direction of that segment. A missing elbow whose shoulder is measured is rebuilt the same way with "),
      X(L1), T(" and "), X(uhat),
      T(", and Section 5.5 covers the case where the wrist is known and the elbow is placed from it instead. A memory that has received no update for forty-five frames is stale and is not used, so a rebuild from memory never outlives the measurement it rests on. The affected joints then hold their last angle. Holding an angle keeps the arm consistent with its own bone lengths, so a gap that nothing anchors is carried in angle space.")]),

# ---------------------------------------------------------------- 5.4
(H2, "5.4 Wrist Recovery from the Object Pose"),

(PM, [T("Case B is the holding hand. On a failure frame of a holding hand, the lost wrist is replaced by the point that equation (5.1) predicts from the current object pose and the current offset:")]),

(EQ, r("w") + r(" = ") + r("o") + r(" + ") + R_obj + r(" ") + r("h"), "5.7"),

(PM, [T("The estimate "), X(r("w")),
      T(" is a function of a same-frame measurement. Only the offset is carried from the past, and it is carried with a memory of about the last fifty frames instead of from the start of the recording. This is the difference between this estimate and the memory of Case A. A wrist placed from its last direction stays near where the arm was when tracking failed, and drifts from the truth the longer the window lasts. The object-derived wrist follows the cube through the whole window and does not age. Case B therefore takes priority over Case A whenever the hand holds the cube and the marker is measured.")]),

(P, "The distance between the hand and the object is guarded at both ends. An offset longer than 0.30 metres does not describe a hand gripping a cube of a few centimetres, so the layer discards an estimate built on such an offset, and the frame falls back to Case A. In the other direction, the grip-plausibility detector of Section 5.2 removes a measured wrist that sits too far from the object its hand holds, and the object estimate takes over. A release is recognised only by the exit rule of the holding state."),
# MU_MAX 0.30 and GRIP_MAX 0.35 in eval/failure/recovery_core.py

(P, "The frames involved need one conversion step. The wrist estimate of equation (5.7) is formed in the gravity-levelled world frame of Chapter 4, while the solve works in the person space of Chapter 3. The two frames are related by the fixed rigid body transformation that the scene calibration of Section 2.2.2 produces, so that transformation carries the estimate into person space before it enters the solve. A rigid body transformation changes no length and no angle, so nothing in the recovery depends on which frame it is written in."),

# ---------------------------------------------------------------- 5.5
(H2, "5.5 Elbow Recovery by Two-Link Inverse Kinematics"),

(PM, [T("Case C starts from a shoulder and a wrist. With both in hand, the elbow follows from the arm's own dimensions. The upper arm and the forearm are two rigid links of known length, so placing the elbow is the two-link inverse kinematics problem of a planar manipulator lifted into three dimensions [42]. The two lengths are the calibrated "),
      X(L1), T(" and "), X(L2),
      T(" of Section 5.3. The construction below is written with the measured wrist "),
      X(p_wr),
      T(". On a failure frame of a holding hand the object-derived estimate "),
      X(r("w")),
      T(" of equation (5.7) takes its place, and nothing else changes. The elbow is any point that satisfies both")]),

(EQ, nrm(p_el + MINUS + p_sh) + r(" = ") + L1 + r(",        ")
     + nrm(p_el + MINUS + p_wr) + r(" = ") + L2, "5.8"),

(PM, [T("The first condition places the elbow on a sphere of radius "),
      X(L1), T(" about the shoulder, and the second on a sphere of radius "),
      X(L2),
      T(" about the wrist. The two spheres meet in a circle when their centres are closer than the sum of the radii and farther apart than the difference. That circle is the set of all elbows consistent with the two endpoints.")]),

(PM, [T("Finding the circle starts from the triangle. Let "), X(r("b")),
      T(" be the vector from the shoulder to the wrist, "), X(r("r")),
      T(" its length, and "), X(bhat),
      T(" the unit vector along it. The triangle with vertices at the shoulder, the elbow and the wrist has sides "),
      X(L1), T(", "), X(L2), T(" and "), X(r("r")),
      T(", all three known. The law of cosines then fixes its angle "),
      X(r("j")),
      T(" at the shoulder, between the upper arm and the shoulder-to-wrist line:")]),

(EQ, nor("cos") + r(" ") + r("j") + r(" = ")
     + frac(sup(L1, r("2")) + r(" + ") + sup(r("r"), r("2")) + MINUS + sup(L2, r("2")),
            r("2") + r(" ") + L1 + r(" ") + r("r")), "5.9"),

(PM, [T("Dropping a perpendicular from the elbow onto the shoulder-to-wrist line completes the construction. The foot of that perpendicular lies at a distance "),
      X(L1 + r(" ") + nor("cos") + r(" ") + r("j")),
      T(" from the shoulder along the line, and the perpendicular itself has length "),
      X(L1 + r(" ") + nor("sin") + r(" ") + r("j")),
      T(". Neither quantity changes when the whole triangle turns about the shoulder-to-wrist line, so the foot is the centre "),
      X(p_c), T(" of the circle and the perpendicular is its radius "),
      X(r_c), T(":")]),

(EQ, p_c + r(" = ") + p_sh + r(" + ") + L1 + r(" ")
     + nor("cos") + r(" ") + r("j") + r(" ") + bhat + r(",        ")
     + r_c + r(" = ") + L1 + r(" ") + nor("sin") + r(" ") + r("j"), "5.10"),

(PM, [T("The circle lies in the plane through "), X(p_c),
      T(" perpendicular to "), X(bhat),
      T(". Let "), X(n1), T(" and "), X(n2),
      T(" be any two unit vectors that are perpendicular to each other and to "), X(bhat),
      T(", and let "), X(r("s")),
      T(" be the turn about the shoulder-to-wrist line that picks out a point of the circle. Every point of the circle is then")]),

(EQ, p_el + r(" = ") + p_c + r(" + ") + r_c
     + d(nor("cos") + r(" ") + r("s") + r(" ") + n1 + r(" + ")
         + nor("sin") + r(" ") + r("s") + r(" ") + n2), "5.11"),

(PM, [T("The angle "), X(r("s")),
      T(" is the one degree of freedom that the two endpoints do not determine. It is the free turn of the elbow about the shoulder-to-wrist line, and a wrist position carries no information about it. Chapter 3 met the same freedom from the other side: the roll of the arm is the shoulder twist, which the elbow position cannot see either.")]),

(PM, [T("The direction memory of Section 5.3 picks the point. It supplies the remembered upper-arm direction "),
      X(uhat),
      T(", and the elbow is placed at the point of the circle closest to where that direction points. That point is found by removing from the remembered direction its component along the shoulder-to-wrist line, which leaves the perpendicular part "),
      X(u_perp),
      T(", and scaling that part to the radius of the circle:")]),

(EQ, u_perp + r(" = ") + uhat + MINUS + d(uhat + DOT + bhat) + r(" ") + bhat
     + r(",        ") + p_el + r(" = ") + p_c + r(" + ") + r_c + r(" ")
     + frac(u_perp, nrm(u_perp)), "5.12"),

(PM, [T("Equation (5.12) minimises, in closed form, the distance from "),
      X(p_el), T(" to the point "),
      X(p_sh + r(" + ") + L1 + r(" ") + uhat),
      T(" over the circle, which is the elbow the remembered direction would give if it were reachable. The argument is short. Every point of the circle lies at the fixed distance "),
      X(r_c),
      T(" from the centre, and the target lies at a fixed distance from the centre as well. The squared distance between the two therefore changes with "),
      X(r("s")),
      T(" only through the dot product of the circle vector with the displacement from the centre to the target. The part of that displacement along "),
      X(bhat),
      T(" contributes nothing, because the circle vector is perpendicular to "),
      X(bhat),
      T(". The remaining part is "),
      X(L1 + r(" ") + u_perp),
      T(", so the product is largest, and the distance smallest, when the circle vector points along "),
      X(u_perp),
      T(". The elbow therefore moves as little as possible from where it was last measured. The memory is unusable when the remembered direction lies along the shoulder-to-wrist line and leaves nothing to project, or when no measured frame has been seen yet. A downward direction then takes its place, since a relaxed elbow hangs. Should the arm point straight down as well, the depth axis of person space is the third candidate. The two fixed directions are perpendicular to each other, so the shoulder-to-wrist line cannot lie along both, and one of them always gives a point of the circle. Figure 5.5 draws the construction.")]),
# direction candidates in order (memory, (0, -1, 0), (0, 0, 1)):
# v1/kinematics/occlusion_ext.py _ik_elbow

(IMG, FIG / "ch5_fig_ik.png", 6.3),
(CAP, "Figure 5.5. The elbow reconstruction. The two shaded surfaces are the sphere of radius L1 about the shoulder, in blue-grey, and the sphere of radius L2 about the wrist, in warm grey, each drawn as the portion of its surface that carries the meeting. The purple ellipse is the circle of equation (5.11) where the two meet, drawn in perspective. The direction memory of the upper arm, in orange, selects one point of the circle by projection, shown alone in the inset, where the circle is seen along its own axis."),

(P, "Neither degenerate configuration needs handling beyond clipping the cosine of equation (5.9) into its valid range. If the wrist estimate lies farther from the shoulder than the two links can reach, the clipped cosine reaches one, and the circle radius of equation (5.10) falls to zero. The elbow then collapses onto the shoulder-to-wrist line, which gives a straight arm pointing at the object. If the two points are closer together than the difference of the link lengths, the cosine is clipped at the other end in the same way. In both cases the output stays finite and keeps pointing in the right direction."),

(P, "There is no answer at all in a single configuration. A wrist estimate that coincides with the shoulder leaves the shoulder-to-wrist line without a direction, and the whole construction hangs on that direction, so the two-link solve returns nothing. The elbow is then placed from the shoulder along the upper-arm memory, as Section 5.3 places any missing landmark from its measured neighbour. The groups that use it leave the layer in the constrained state and not the held state, as the chapter opening defines them. Only when no fresh memory is available either does the arm fall back on holding its last angles."),

(PM, [T("Equation (5.9) is ill conditioned near a straight arm. Differentiating that equation, the sensitivity of "),
      X(r("j")), T(" to "), X(r("r")),
      T(" grows without bound as "), X(r("r")), T(" approaches "),
      X(L1 + r(" + ") + L2),
      T(". Near full extension a small error in the wrist estimate becomes a large error in the flexion angle, because the triangle is nearly flat and its shape stops depending smoothly on its longest side. Above 98 percent of the full reach the elbow is therefore taken from the direction memory instead, with the wrist still anchored at the object-derived estimate. The two-link solution stays as the fallback for the case where no fresh memory exists.")]),
# reach guard 0.98 of L1+L2 in v1/kinematics/occlusion_ext.py

(P, "The layer applies two rules to the angles after the solve, and both come from angles the landmarks cannot determine in some configurations. The shoulder twist is read from the part of the forearm that is perpendicular to the upper arm, and that part vanishes as the elbow straightens, as Section 3.4.3 sets out. Below 15 degrees of elbow flexion the twist keeps its previous value and its group leaves the layer held. The hold is released only above 25 degrees, so that the twist resumes on a measurement worth having. Every arm angle then passes a limit of 15 degrees of change between consecutive frames, which bounds the step the output can take when a joint re-locks after a hold or moves into a reconstruction. While that limit is active, the value leaving the layer is not the value the solve computed, and the group is marked constrained until the two agree again. The limit applies to the arm angles and not to the root."),
# twist hold tags the group HELD; only the rate limiter produces a
# CONSTRAINED tag without a rebuilt landmark: v1/kinematics/occlusion_ext.py

# ---------------------------------------------------------------- 5.6
(H2, "5.6 Worked Example"),

(P, "The recovery now runs on one real frame, so that each equation of this chapter appears with its numbers, as Section 3.5 did for the solve. The frame comes from the same recording and follows the frame of that section by under a second. Frame 533 has every landmark measured. From frame 550 the landmark detector stops reporting a usable right wrist for about three seconds, while the hand slides the cube along the rail. The acquisition detector of Section 5.2 fires on the right arm through that window. The example takes frame 560, ten frames into the window. The right elbow and wrist are removed together, as Section 5.2 prescribes, and both are rebuilt. The torso and the right shoulder are measured, the right hand holds the cube, and the marker is measured. Case B therefore places the wrist and Case C places the elbow."),

(PM, [T("The layer receives the right shoulder in person space, the two calibrated lengths of the right arm, and the object pose of Chapter 4 in the levelled world frame:")]),
(MATH, eqArr(
    p_sh + r(" = (−0.16, 0.34, 1.32)"),
    L1 + r(" = 0.317 m,        ") + L2 + r(" = 0.205 m"),
    r("o") + r(" = (−0.22, 0.08, 0.45)"),
    R_obj + r(" = ") + mat([
        [r("1.00"), r("0.03"), r("0.04")],
        [r("−0.04"), r("−0.09"), r("0.99")],
        [r("0.03"), r("−1.00"), r("−0.09")]]))),

(PM, [T("The offset in force is the recursive estimate of equation (5.4). Its last update came on frame 549, the last clean wrist frame before the window. The estimate is frozen from there on:")]),
(MATH, r("h") + r(" = (0.01, −0.04, 0.05),        ") + nrm(r("h")) + r(" = 0.07 m")),
(P, "The wrist sits about seven centimetres from the marker origin, inside the bound of Section 5.4. Equation (5.7) turns the offset from the object's axes into the levelled world axes and adds it to the object origin:"),
(MATH, eqArr(
    R_obj + r(" ") + r("h") + r(" = (0.01, 0.06, 0.04)"),
    r("w") + r(" = ") + r("o") + r(" + ") + R_obj + r(" ") + r("h") + r(" = (−0.21, 0.13, 0.48)"))),
(P, "The wrist lands five centimetres above the marker origin and a few centimetres to its side, which is the hand resting on top of the cube."),

(P, "The scene calibration of Section 2.2.2 gives the fixed transformation from the levelled world frame to person space. For this recording it is"),
(MATH, mat([
    [r("1.00"), r("−0.04"), r("0.02"), r("0.02")],
    [r("0.04"), r("1.00"), r("−0.05"), r("−0.19")],
    [r("−0.02"), r("0.05"), r("1.00"), r("0.55")],
    [r("0"), r("0"), r("0"), r("1")]])),
(PM, [T("Its rotation block is close to the identity, because the levelled world axes and the person-space axes are nearly parallel in this setup. Its last column is the position of the desk origin in person space. Applied to "),
      X(r("w")), T(", it gives the wrist estimate the solve receives:")]),
(MATH, r("w") + r(" = (−0.19, −0.09, 1.04)")),
(P, "The estimate lies about three centimetres from the wrist measured on frame 549, and the cube has moved on along the rail in the meantime."),

(PM, [T("Case C now has a shoulder and a wrist. The vector between them, its length and its unit vector are")]),
(MATH, eqArr(
    r("b") + r(" = ") + r("w") + MINUS + p_sh + r(" = (−0.02, −0.43, −0.27)"),
    r("r") + r(" = 0.51 m,        ") + bhat + r(" = (−0.04, −0.84, −0.54)"))),
(P, "The wrist lies 0.51 m from the shoulder. That is 97 percent of the full reach of 0.52 m, under the 98 percent guard of Section 5.5, so the two-link solve runs. The arm is nearly straight, and the numbers that follow show what that does to the circle. The law of cosines of equation (5.9) gives the angle at the shoulder:"),
(MATH, nor("cos") + r(" ") + r("j") + r(" = ")
       + frac(sup(r("0.317"), r("2")) + r(" + ") + sup(r("0.507"), r("2")) + MINUS + sup(r("0.205"), r("2")),
              r("2 · 0.317 · 0.507")) + r(" = 0.98,        ") + r("j") + r(" = 11.0°")),
(P, "Equation (5.10) then places the centre of the circle on the shoulder-to-wrist line and fixes its radius:"),
(MATH, eqArr(
    p_c + r(" = ") + p_sh + r(" + ") + L1 + r(" ") + nor("cos") + r(" ") + r("j") + r(" ") + bhat + r(" = (−0.18, 0.07, 1.15)"),
    r_c + r(" = ") + L1 + r(" ") + nor("sin") + r(" ") + r("j") + r(" = 0.06 m"))),
(P, "The circle of possible elbows has a radius of six centimetres. It is small because the arm is nearly straight. The free turn of the elbow about the shoulder-to-wrist line can move it by at most twelve centimetres."),

(PM, [T("The direction memory of the upper arm was last updated on frame 549, well inside the horizon of Section 5.3. Equation (5.12) removes from it the component along the shoulder-to-wrist line:")]),
(MATH, eqArr(
    uhat + r(" = (−0.11, −0.91, −0.39),        ") + uhat + DOT + bhat + r(" = 0.98"),
    u_perp + r(" = ") + uhat + MINUS + d(uhat + DOT + bhat) + r(" ") + bhat + r(" = (−0.07, −0.09, 0.14),        ") + nrm(u_perp) + r(" = 0.18"))),
(P, "The memory points almost along the shoulder-to-wrist line, as it must for a nearly straight arm. The projection removes most of it, and less than a fifth of its length remains. That remaining part chooses the point on the circle. Scaling it to the radius gives the elbow:"),
(MATH, p_el + r(" = ") + p_c + r(" + ") + r_c + r(" ") + frac(u_perp, nrm(u_perp)) + r(" = (−0.20, 0.05, 1.20)")),

(P, "Both conditions of equation (5.8) hold on the result: the elbow lies 0.317 m from the shoulder and 0.205 m from the wrist. It lies six millimetres from the elbow measured on frame 549. The placed upper arm is 0.7 degrees from the remembered direction, so the elbow has moved as little as the new wrist allows. The solve of Chapter 3 then runs on the assembled points and reads an elbow flexion of −28.1 degrees in the convention of Section 3.4.3. The three right-arm groups leave the layer in the constrained state, since two of their landmarks were rebuilt."),

(P, "The positions above are the ones the layer produced when the recording was processed, and the equations evaluated by hand from the printed inputs land on the same wrist and the same elbow to below a millimetre. Chapter 7 evaluates windows like this one against wrist positions labelled by hand in the images."),
# numbers: writing/v8/scripts/ch5_worked_example.py (rail recording,
# frame 560, recovery_r6b pipeline state); no Case A frame exists in
# either recording (script docstring)

]

# Fill the two Table 5.1 cells that name the Chapter 4 pose symbol.
for item in content:
    if item[0] == TBL and item[1][0][0] == "Symbol":
        for row in item[1][1:]:
            if row[3].endswith("column of ") or row[3].endswith("block of "):
                row[3] = (row[3], TWO)

# --- build ---------------------------------------------------------------
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
        add_display_math(doc, item[1])
    elif kind == IMG:
        path = Path(item[1])
        assert path.exists(), f"missing figure: {path}"
        doc.add_picture(str(path), width=Inches(item[2]))
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

out = REPO / "writing" / "v8" / "Chapter_5_Pose_Recovery.docx"
doc.save(out)
print("saved", out, "| items:", len(content))

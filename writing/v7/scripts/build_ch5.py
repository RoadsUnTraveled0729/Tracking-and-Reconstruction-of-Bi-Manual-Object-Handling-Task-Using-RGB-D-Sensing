#!/usr/bin/env python3
"""Build writing/v7/Chapter_5_Pose_Recovery.docx (V7 rewrite round).

Chapter 5 against the V7 TOC: 5.1 Landmark Tracking Failures, 5.2 Grip
Episodes and the Hand-Object Offset, 5.3 Wrist Recovery from the Object
Pose, 5.4 Elbow Recovery by Two-Link Inverse Kinematics, 5.5 Torso Repair
on Camera Rays (5.5.1-5.5.7, detailed round 2026-09-02 at user request:
failure model, ray repair and depth memory, the three gates, pair
rebuild, limits; equations 5.12-5.23), 5.6 Output States of the Solver.

Method only (user rule 2026-08-28): what the recovery does and how. No
accuracy numbers, no synthetic-masking results, no detector fire counts,
no failure-window frame numbers. Those belong to Chapter 7. Threshold
values that DEFINE the method are stated as design parameters; the source
of each is named in a comment beside it.

The internal detector codes D1-D6 are not used: the chapter and
Chapter 7 name the six detectors acquisition, segment length, torso
line angle, torso width ratio, landmark step, and grip plausibility.

Sources for every design parameter printed here:
  five detector thresholds, event rules eval/failure/detect_failures.py
                                        eval/reports/r5_failure_mask.md
  grip state and the offset estimator   eval/failure/grip_state.py
  instantaneous holding conditions      eval/offset/carry.py
  plausibility bounds, grip detector    eval/failure/recovery_core.py
  IK, ray repair, gates, tags, limits   v1/kinematics/occlusion_ext.py
  torso ray repair decision             eval/DECISIONS.md (E-011b)
  the mathematics deliverable           eval/reports/
                                        r5_object_conditioned_recovery.md
  Unity meaning of the tags             Unity/Assets/Scripts/
                                        IntegratedSceneReceiverV2.cs

E-020 (the joint-limited elbow) is excluded from the thesis by
skill_set/thesis-structure-rules.md rule 4 and is not mentioned.

Figures: writing/v7/figures/ch5_fig_detectors.png, ch5_fig_grip.png,
ch5_fig_ik.png, ch5_fig_torso.png, ch5_fig_states.png (see the matching
make_ch5_*.py scripts).
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches
from docx.oxml import parse_xml

from eqn import r, nor, sub, sup, hat, frac, d, add_display_eq, \
    add_display_math, add_inline_math

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v7" / "figures"

H1, H2, H3, P, IMG, CAP, TBL, EQ = "h1", "h2", "h3", "p", "img", "cap", "tbl", "eq"
MATH = "mth"   # displayed, unnumbered mathematics
PM = "pm"      # paragraph mixing text runs and inline math


def T(t):
    return ("t", t)


def X(f):
    return ("m", f)


def nary(chr_, sub_, body):
    """OMML n-ary operator (used for the one summation of this chapter)."""
    return (f'<m:nary><m:naryPr><m:chr m:val="{chr_}"/>'
            f'<m:limLoc m:val="undOvr"/><m:supHide m:val="1"/>'
            f'</m:naryPr><m:sub>{sub_}</m:sub><m:sup/>'
            f'<m:e>{body}</m:e></m:nary>')


# --- symbols -------------------------------------------------------------
# Chapter 3's landmark names (p12, p14, p16) are tied to the arm names
# p_sh, p_el, p_wr once, in Section 5.2.
p_sh = sub(r("p"), nor("sh"))
p_el = sub(r("p"), nor("el"))
p_wr = sub(r("p"), nor("wr"))
p12 = sub(r("p"), r("12"))
p14 = sub(r("p"), r("14"))
p16 = sub(r("p"), r("16"))
p_z = sub(r("p"), r("z"))
R_obj = sub(r("R"), nor("obj"))
R_objT = sup(sub(r("R"), nor("obj")), r("T"))
L1 = sub(r("L"), r("1"))
L2 = sub(r("L"), r("2"))
r_c = sub(r("r"), nor("c"))
z_mem = sub(r("z"), nor("mem"))
n1 = sub(r("n"), r("1"))
n2 = sub(r("n"), r("2"))
u_perp = sub(r("u"), nor("⊥"))
p_c = sub(r("p"), nor("c"))
d_k = sub(r("d"), r("k"))
p_wr_k = sub(r("p"), nor("wr,") + r("k"))
o_k = sub(r("o"), r("k"))
R_obj_k = sub(r("R"), nor("obj,") + r("k"))
bhat = hat(r("b"))
uhat = hat(r("u"))
MINUS = r(" − ")
DOT = r(" · ")


def nrm(e):
    return d(e, "|", "|")


def nrm2(e):
    return sup(d(e, "|", "|"), r("2"))


content = [
(H1, "Chapter 5: Pose Recovery During Tracking Failure"),

(P, "The model of Chapter 3 assumes that the landmarks it needs are present and correct. Over an object-handling task neither assumption holds for the whole recording. A hand passes in front of the trunk, the working hand wraps around the carried object, and in a two-handed task the two hands meet during a handover. Some of the time the landmark detector declines to report a point. The rest of the time it reports a point with full confidence whose three-dimensional position is wrong. A solver that takes every reported landmark at face value follows the wrong points and produces an arm that is nowhere near the real one."),

(P, "This chapter builds a layer around the closed-form solve, without changing it. The layer does three things. It decides which landmarks of the current frame are wrong. It rebuilds what it can from quantities that are still measured, taking the tracked object of Chapter 4 as the anchor for a hand that holds it and the camera geometry as the anchor for a corrupt torso point. And it labels every joint group it emits with the source of its value. Every step runs on the current frame and on state carried forward from earlier frames."),

(P, "The order of the chapter follows the order of the work inside one frame. Section 5.1 defines the failure detectors. Section 5.2 develops the link between a holding hand and the object it holds. The wrist is rebuilt from that link in Section 5.3 and the elbow follows in Section 5.4. Section 5.5 repairs a corrupt torso landmark on its camera ray. Section 5.6 states what leaves the layer."),

# ---------------------------------------------------------------- 5.1
(H2, "5.1 Landmark Tracking Failures"),

(P, "A landmark can be wrong in two ways, and only one of them is announced. MediaPipe attaches a source flag to every sample, marking whether the point was usable, whether its confidence fell below the visibility gate, and whether the depth window around its pixel held no valid depth sample. A sample carrying either of the last two markings is a declared failure, and the pipeline already treats it as missing. The second way is silent. The pixel is correct and the confidence is high, but the depth reading behind that pixel belongs to a hand, to the carried object, or to the desk in front of the person, so the point is lifted to a position tens of centimetres away from the body. Nothing in the confidence score reveals this, because the confidence describes the image, not the depth."),

(P, "Geometry reveals it. Over the short spans that matter here the body is rigid: a limb segment cannot change length, the trunk cannot fold, and a landmark cannot jump across the scene between two frames of a slow task. Each of those statements becomes a per-frame test, and a frame that violates one of them carries a wrong measurement whatever the detector says about it. A sixth test uses the object: a hand that is holding the cube cannot have its wrist far away from it. Table 5.1 lists the six tests and Figure 5.1 draws them."),

(TBL, [["Detector", "What it tests", "Design parameter"],
       ["Acquisition",
        "the landmark detector's own report on the sample",
        "the sample is not marked usable"],
       ["Segment length",
        "an upper arm or a forearm against its calibrated length",
        "a departure of 35 percent from the calibrated median"],
       ["Torso line angle",
        "the hip line against the shoulder line",
        "22 degrees"],
       ["Torso width ratio",
        "shoulder width against hip width",
        "a departure of 20 percent from the calibrated ratio"],
       ["Landmark step",
        "how far a landmark moved since the previous frame",
        "5 centimetres between consecutive frames"],
       ["Grip plausibility",
        "a measured wrist against the object that hand holds",
        "0.35 metres from the object centre"]]),
# thresholds: eval/failure/detect_failures.py SEG_TOL 0.35,
# TORSO_LINE_TOL_DEG 22.0, WIDTH_RATIO_BAND 0.20, STEP_TOL_M 0.05;
# grip-plausibility bound GRIP_MAX 0.35 in
# eval/failure/recovery_core.py.
(CAP, "Table 5.1. The six failure detectors, with the quantity each tests and its design parameter."),

(IMG, FIG / "ch5_fig_detectors.png", 6.3),
(CAP, "Figure 5.1. The six failure detectors, one panel each. The dark skeleton is the correct geometry and the red element is the condition that fires the detector: a declined sample, a segment whose measured length departs from its calibrated value, a hip line and a shoulder line that no longer agree, a shoulder width and hip width whose ratio has changed, a landmark that moved too far since the previous frame, and a wrist reported far from the object its hand is holding."),

(P, "The acquisition detector is a report rather than a test, and it fires wherever the landmark detector marks a sample as low in visibility or without depth. The four geometry detectors each turn one rigidity statement into a number. A bone cannot lengthen, so the segment-length detector compares the current upper arm and forearm of an arm with the median of that segment over the recording's clean frames. The torso line-angle detector measures the three-dimensional angle between the hip line and the shoulder line, which stay close to parallel while the trunk is one rigid plate. The ratio of shoulder width to hip width is fixed by the participant's build, and the torso width-ratio detector compares it with its clean median. The landmark-step detector measures how far each landmark moved between two consecutive frames on which it was reported usable."),

(PM, [T("While a hand holds the cube, the wrist and the object move together, so a wrist reported farther than the release radius of Section 5.2 from the object centre is a wrong measurement and not a release. The bound is a statement about a hand and a hand-held object, so it transfers to any recording; the four geometry thresholds are properties of a human body and of a slow task. Their values come from the distributions of the same statistics on a separate reference recording. Each threshold is set at the 99th percentile of that recording's clean frames plus a safety margin, then cross-checked against the tolerances the rest of this work already uses for the same quantities. The reference recording is clean for the right arm and for the torso, and not for its left arm, where a stretch of frames shows the elbow sliding along the limb while the upper arm and the forearm trade length between them. The segment-length detector fires on that stretch. Widening the tolerance until it stops firing would calibrate the threshold to a defect and would blind the detector to the moderate corruption the recovery stage exists for, so the threshold stays where the clean statistics put it. The acquisition detector carries no threshold of this kind, since it reports the landmark detector's own declarations.")]),

(P, "The per-frame outputs are combined into three failure masks, one for each arm and one for the torso, by taking a mask as set whenever any of its detectors fires. Each mask is then cleaned up twice over. Gaps of at most five frames are closed, so a single frame in which the tracker recovers does not split one failure into two. Runs shorter than five frames are dropped, so an isolated noisy frame does not open a failure window. The grip-plausibility test runs on the cleaned masks rather than alongside the other five, because it needs the holding state of Section 5.2, and that state is itself built on the cleaned masks; whatever it flags is added to the mask afterwards. What remains is a per-frame decision, for each arm and for the torso, on whether this frame's landmarks may be trusted."),

(P, "A flagged arm has its elbow and wrist landmarks removed before the solve. The detectors exist to turn a wrong measurement into a missing one. The solve of Chapter 3 already knows what to do with a landmark that is absent, and it has no defence against one that is present and wrong. The rest of the chapter is about what can be put back in place of the removed points. The object marker is the starting material, because it stays measured through the windows that defeat the person tracker: the marker sits on the carried cube, in clear view of the sensor, exactly while the hand that carries it is hidden behind it."),

# ---------------------------------------------------------------- 5.2
(H2, "5.2 Grip Episodes and the Hand-Object Offset"),

(PM, [T("This chapter writes the three landmarks of one arm as "),
      X(p_sh), T(", "), X(p_el), T(" and "), X(p_wr),
      T(" for its shoulder, elbow and wrist, which on the right side are the points Chapter 3 numbers "),
      X(p12), T(", "), X(p14), T(" and "), X(p16),
      T("; the left arm carries the same three names.")]),

(PM, [T("While a hand grips the cube and does not slide on it, the wrist is a fixed point of the object. The object's pose is measured every frame as an origin "),
      X(r("o")), T(" and an orientation "), X(R_obj),
      T(", both delivered by Chapter 4 in the world frame of the scene and levelled by the gravity direction of the calibration before the fit below, so that the offset is fitted in axes whose vertical is the physical vertical. Writing "),
      X(r("h")),
      T(" for the position of the wrist in the object's own axes, the wrist of a holding hand satisfies")]),

(EQ, p_wr + r(" = ") + r("o") + r(" + ") + R_obj + r(" ") + r("h"), "5.1"),

(PM, [T("where "), X(r("h")),
      T(" is constant for as long as the grasp is rigid.")]),

(PM, [T("The offset itself is fitted from the frames on which both the wrist and the object are measured. On such a frame the offset is read off directly by pulling the measured displacement into the object's axes with the transpose, the operation of equation (3.3):")]),

(EQ, r("d") + r(" = ") + R_objT + r(" ") + d(p_wr + MINUS + r("o")), "5.2"),

(PM, [T("Each frame therefore contributes one observation of the same constant, written "),
      X(d_k), T(" on frame "), X(r("k")),
      T(". Fitting a single "), X(r("h")),
      T(" to a set of "), X(r("N")),
      T(" clean frames by least squares means minimizing the total squared distance between the measured wrists and the wrists that equation (5.1) predicts. Substituting equation (5.2) into that sum and using the fact that "),
      X(R_obj), T(" is orthonormal, which leaves lengths unchanged, gives")]),

(MATH, nary("∑", r("k"), nrm2(p_wr_k + MINUS + o_k + MINUS + R_obj_k + r(" ") + r("h")))
       + r("  =  ")
       + nary("∑", r("k"), nrm2(R_obj_k + d(d_k + MINUS + r("h"))))
       + r("  =  ")
       + nary("∑", r("k"), nrm2(d_k + MINUS + r("h")))),

(PM, [T("so the rotation drops out of the problem and the fit reduces to the mean of the observations,")]),

(EQ, r("h") + r(" = ") + frac(r("1"), r("N"))
     + nary("∑", r("k"), d_k), "5.3"),

(PM, [T("A single offset per recording will not do. The participant may let go of the cube and take it again, and each new grasp puts the hand somewhere else on the face of the cube. One grasp is a grip episode, the unit the rest of this chapter and Chapters 8 and 9 work in, and the offset belongs to the episode rather than to the recording. Within one long episode the hand also shifts. The offset is therefore estimated with a short memory rather than fitted once. On each frame that contributes a clean observation, the estimate moves towards that observation by a small gain "),
      X(r("c")), T(",")]),

(EQ, sub(r("h"), nor("new")) + r(" = ") + d(r("1") + MINUS + r("c"))
     + r(" ") + sub(r("h"), nor("old")) + r(" + ") + r("c") + r(" ") + r("d"), "5.4"),
# gain c = MU_ALPHA 0.02 in eval/failure/grip_state.py

(PM, [T("Equation (5.4) is a first-order recursive low-pass update, the cheapest smoother that can run on a stream of samples [55]. It mixes a little of the new observation into the previous estimate, so the estimate follows the offset in force now and forgets an offset from long ago. A gain of 0.02 weights the estimate towards roughly the last fifty frames. Three rules complete the estimator. A frame that contributes no clean observation leaves the estimate untouched, which means that through a failure window the value in use is the offset that was in force immediately before tracking was lost. The estimate is restarted at the start of each grip episode, because a new grasp is a new offset. During a warm-up of five clean frames the mean of equation (5.3) over that episode stands in. And an episode that never gathers fifteen clean frames of its own has no mean worth taking, so it falls back to the offset fitted over the whole recording. No frame that a detector has flagged enters any fit.")]),

(P, "Equation (5.1) applies only to a hand that holds the object, so the layer must decide which hand that is. On a frame where everything is measured the decision is easy, and it takes five conditions together: the marker is measured, the object is away from its resting place, the wrist is measured and unflagged, the wrist lies within the hold radius of the object centre, and the forearm of that arm measures within 30 percent of its own median length. The last condition rejects the frames where the elbow and the wrist take their depth off the same near surface and collapse onto each other, which would otherwise put a plausible-looking wrist next to the cube. That test needs a measured wrist, and that wrist is missing on exactly the frames the recovery exists for. The holding decision is therefore carried as a state per hand, with rules for entering and leaving it."),
# five instantaneous conditions: eval/offset/carry.py holding_mask
# (det, carried, wrist flag, HOLD_RADIUS 0.25) and forearm_ok
# (FOREARM_TOL 0.30)

(P, "The hand enters the holding state after the instantaneous test passes on five consecutive frames. It stays in that state through a wrist failure for as long as the object is still being carried, on the reasoning that an object which is moving and which nobody was seen to release is still in the hand that held it. It leaves the state when the object comes to rest, or when a cleanly measured wrist sits farther than the release radius from the object centre, in either case sustained over five consecutive frames. The release radius, 0.35 metres, is wider than the hold radius of 0.25 metres, so the state does not flicker at the boundary. The run of frames between the entry and the exit is one grip episode. Both hands may hold at once, and a handover is two grip episodes that overlap. Figure 5.2 shows the offset and the holding state together."),
# ENTER_FRAMES/EXIT_FRAMES 5, RELEASE_RADIUS 0.35, MU_WARMUP 5:
# eval/failure/grip_state.py; hold radius 0.25 in eval/offset/carry.py

(IMG, FIG / "ch5_fig_grip.png", 6.3),
(CAP, "Figure 5.2. (a) The hand-object offset h, drawn in the axes of the object, whose origin o and orientation are measured on every frame. (b) The holding state of one hand: the five conditions of the instantaneous test, and the rules for entering the state, staying in it through a wrist failure, and leaving it."),

(PM, [T("The arm that is not holding gains nothing from the object, and its failures keep the behaviour the solver already had. That behaviour rests on a second piece of carried state, the direction memory: for every body segment the layer keeps a running average of the direction from the segment's proximal landmark to its distal one, updated on frames where both ends were measured, so that nothing an arm's memory holds was ever reconstructed. Only the memory of a torso pair takes more than measurements, since the repair of Section 5.5 also steers it with the surviving line and with the direction between two repaired points. Each update mixes the new direction into the old one by the recursive form of equation (5.4), with a gain of 0.30 that weights the memory towards the last few frames, and the result is scaled back to unit length, since the weighted sum of two unit vectors is generally shorter than either of them. A missing landmark is then rebuilt by stepping the segment's calibrated length from its measured neighbour along that direction. A memory that has received no update for forty-five frames is treated as stale and is not used, so a rebuild from memory never outlives the measurement it rests on, and the affected joints hold their last angle instead. Holding an angle keeps the arm consistent with its own bone lengths, so a gap that nothing anchors is carried in angle space rather than filled with an invented position.")]),
# direction memory: dir_alpha 0.3 and the unit renormalisation, plus
# the 45-frame staleness horizon, in v1/kinematics/occlusion_ext.py

# ---------------------------------------------------------------- 5.3
(H2, "5.3 Wrist Recovery from the Object Pose"),

(PM, [T("On a failure frame of a holding hand the lost wrist is replaced by the point that equation (5.1) predicts from the current object pose and the offset in force:")]),

(EQ, r("w") + r(" = ") + r("o") + r(" + ") + R_obj + r(" ") + r("h"), "5.5"),

(PM, [T("The estimate "), X(r("w")),
      T(" is a live function of a same-frame measurement. Only the offset is carried from the past, and it is carried with a memory of roughly the last fifty frames rather than from the start of the recording. That is the difference between this estimate and a memory-based one: a wrist held at its last value stops where the arm was when tracking failed, and drifts further from the truth the longer the window lasts, while the object-derived wrist follows the cube through the whole window and does not age.")]),

(P, "Two bounds guard the distance between the hand and the object. An offset longer than 0.30 metres does not describe a hand gripping a cube of a few centimetres, so an estimate built on such an offset is discarded and the frame falls back to the memory behaviour. In the other direction, the grip-plausibility detector of Section 5.1 removes a measured wrist that sits too far from the object its hand holds, and the object estimate takes over. A release is recognized only by the exit rule of the holding state."),
# MU_MAX 0.30 and GRIP_MAX 0.35 in eval/failure/recovery_core.py

(PM, [T("The object cannot do more than this. Equation (5.1) ties the object to one point of the body, and one point does not determine a pose. For the shoulder, the wrist estimate says only that the arm must be able to reach it,")]),

(EQ, nrm(r("w") + MINUS + p_sh) + r(" ≤ ") + L1 + r(" + ") + L2, "5.6"),

(PM, [T("with "), X(L1), T(" and "), X(L2),
      T(" the calibrated upper-arm and forearm lengths. That is one scalar inequality against the six degrees of freedom of the torso. It can reject a torso hypothesis and it can never produce one, so a corrupt torso needs a different anchor, developed in Section 5.5.")]),

(P, "One bookkeeping step separates the frames involved. The wrist estimate of equation (5.5) is formed in the gravity-levelled version of the world frame of Chapter 4, while the solve works in the person space of Chapter 3. The two are related by the fixed rigid map that the scene calibration produces, so the estimate is carried into person space by that map before it enters the solve. A rigid map changes no length and no angle, so nothing in the recovery depends on which of the frames it is written in."),

# ---------------------------------------------------------------- 5.4
(H2, "5.4 Elbow Recovery by Two-Link Inverse Kinematics"),

(PM, [T("With a shoulder and a wrist in hand, the elbow follows from the arm's own dimensions. The upper arm and the forearm are two rigid links of known length, so placing the elbow is the two-link inverse kinematics problem of a planar manipulator lifted into three dimensions [42]. The two lengths are calibrated per recording as the median of the measured segment over the first sixty clean frames of that segment, or supplied when a calibration is already available. The construction below is written with the measured wrist "),
      X(p_wr),
      T("; on a failure frame of a holding hand the object-derived estimate "),
      X(r("w")),
      T(" of equation (5.5) takes its place, and nothing else about the construction changes. Writing "),
      X(L1), T(" and "), X(L2),
      T(" for the two lengths, the elbow is any point that satisfies both")]),

(EQ, nrm(p_el + MINUS + p_sh) + r(" = ") + L1 + r(",        ")
     + nrm(p_el + MINUS + p_wr) + r(" = ") + L2, "5.7"),

(PM, [T("The first condition places the elbow on a sphere of radius "),
      X(L1), T(" about the shoulder and the second on a sphere of radius "),
      X(L2),
      T(" about the wrist. Two spheres whose centres are closer together than the sum of their radii and farther apart than the difference meet in a circle, and that circle is the set of all elbows consistent with the measured pair of endpoints.")]),

(PM, [T("The circle is found from the triangle. Let "), X(r("b")),
      T(" be the vector from the shoulder to the wrist, "), X(r("r")),
      T(" its length, and "), X(bhat),
      T(" the unit vector along it. The triangle with vertices at the shoulder, the elbow, and the wrist has sides "),
      X(L1), T(", "), X(L2), T(" and "), X(r("r")),
      T(", all three of which are now known, so the law of cosines fixes its angle "),
      X(r("j")),
      T(" at the shoulder, between the upper arm and the shoulder-to-wrist line:")]),

(EQ, nor("cos") + r(" ") + r("j") + r(" = ")
     + frac(sup(L1, r("2")) + r(" + ") + sup(r("r"), r("2")) + MINUS + sup(L2, r("2")),
            r("2") + r(" ") + L1 + r(" ") + r("r")), "5.8"),

(PM, [T("Dropping a perpendicular from the elbow onto the shoulder-to-wrist line completes the construction. The foot of that perpendicular lies at a distance "),
      X(L1 + r(" ") + nor("cos") + r(" ") + r("j")),
      T(" from the shoulder along the line, and the perpendicular itself has length "),
      X(L1 + r(" ") + nor("sin") + r(" ") + r("j")),
      T(". Neither quantity changes if the whole triangle is turned about the shoulder-to-wrist line, so the foot is the centre "),
      X(p_c), T(" of the circle and the perpendicular is its radius "),
      X(r_c), T(":")]),

(EQ, p_c + r(" = ") + p_sh + r(" + ") + L1 + r(" ")
     + nor("cos") + r(" ") + r("j") + r(" ") + bhat + r(",        ")
     + r_c + r(" = ") + L1 + r(" ") + nor("sin") + r(" ") + r("j"), "5.9"),

(PM, [T("The circle lies in the plane through "), X(p_c),
      T(" perpendicular to "), X(bhat),
      T(". Taking any two unit vectors "), X(n1), T(" and "), X(n2),
      T(" that are perpendicular to each other and to "), X(bhat),
      T(", and writing "), X(r("s")),
      T(" for the turn about the shoulder-to-wrist line that picks out a point of the circle, every point of the circle is")]),

(EQ, p_el + r(" = ") + p_c + r(" + ") + r_c
     + d(nor("cos") + r(" ") + r("s") + r(" ") + n1 + r(" + ")
         + nor("sin") + r(" ") + r("s") + r(" ") + n2), "5.10"),

(PM, [T("The angle "), X(r("s")),
      T(" is the one degree of freedom that the two endpoints do not determine. It is the free turn of the elbow about the shoulder-to-wrist line, and a wrist position carries no information about it at all. Chapter 3 met the same freedom from the other side: the roll of the arm is the shoulder twist, which the elbow position cannot see either.")]),

(PM, [T("Continuity settles it. The direction memory of Section 5.2 supplies the remembered upper-arm direction, written "),
      X(uhat),
      T(", and the elbow is placed at the point of the circle that lies closest to where the remembered direction points. That point is obtained by removing from the remembered direction its component along the shoulder-to-wrist line, which leaves the perpendicular component "),
      X(u_perp),
      T(", and scaling that component to the circle's radius:")]),

(EQ, u_perp + r(" = ") + uhat + MINUS + d(uhat + DOT + bhat) + r(" ") + bhat
     + r(",        ") + p_el + r(" = ") + p_c + r(" + ") + r_c + r(" ")
     + frac(u_perp, nrm(u_perp)), "5.11"),

(PM, [T("Equation (5.11) is the closed-form minimizer of the distance from "),
      X(p_el), T(" to the point "),
      X(p_sh + r(" + ") + L1 + r(" ") + uhat),
      T(" over the circle, which is the elbow the remembered direction would have produced had it been reachable. The argument is short. Every point of the circle lies at the fixed distance "),
      X(r_c),
      T(" from the centre and the target lies at a fixed distance from it as well, so the squared distance between the two changes with "),
      X(r("s")),
      T(" only through the dot product of the circle vector with the displacement from the centre to the target. The part of that displacement along "),
      X(bhat),
      T(" contributes nothing to the product, because the circle vector is perpendicular to "),
      X(bhat),
      T(", and the remaining part is "),
      X(L1 + r(" ") + u_perp),
      T(", so the product is largest, and the distance smallest, when the circle vector points along "),
      X(u_perp),
      T(". The elbow therefore moves as little as possible from where it was last measured. When the memory is unusable, either because the remembered direction happens to lie along the shoulder-to-wrist line and leaves nothing to project, or because no measured frame has been seen yet, a downward direction takes its place, since a relaxed elbow hangs. Should the arm point straight down as well, so that the downward direction leaves nothing to project either, the depth axis of person space serves as a third candidate. The two fixed directions are perpendicular to each other, so the shoulder-to-wrist line cannot lie along both, and one of them always yields a point of the circle. Figure 5.3 draws the construction.")]),
# direction candidates in order (memory, (0, -1, 0), (0, 0, 1)):
# v1/kinematics/occlusion_ext.py

(IMG, FIG / "ch5_fig_ik.png", 6.3),
(CAP, "Figure 5.3. The elbow reconstruction. The two shaded surfaces are the sphere of radius L1 about the shoulder, in blue-grey, and the sphere of radius L2 about the wrist, in warm grey, each drawn as the portion of its surface that carries the meeting; the purple ellipse is the circle of equation (5.10) where the two meet, drawn in perspective. The direction memory of the upper arm, in orange, selects one point of the circle by projection, shown alone in the inset, where the circle is seen along its own axis."),

(P, "Neither degenerate configuration needs handling beyond clipping the cosine of equation (5.8) into its valid range. If the wrist estimate lies farther from the shoulder than the two links can reach, the clipped cosine reaches one, the circle radius of equation (5.9) falls to zero, and the elbow collapses onto the shoulder-to-wrist line, giving the straight arm pointing at the object. If the two points are closer together than the difference of the link lengths, the cosine is clipped at the other end in the same way. In both cases the output stays finite and keeps pointing in the right direction."),

(P, "One configuration has no answer at all. A wrist estimate that coincides with the shoulder leaves the shoulder-to-wrist line without a direction, and the whole construction hangs on that direction, so the two-link solve returns nothing. The elbow is then placed the way Section 5.2 places any orphaned landmark, from the shoulder along the direction memory, and the groups that consume it leave the layer in the constrained state rather than the held state, the two output states that Section 5.6 defines. Only when no fresh memory is available either does the arm fall back on holding its last angles."),

(PM, [T("Conditioning near a straight arm deserves a note, because it is a property of equation (5.8) rather than of the data. Differentiating that equation, the sensitivity of "),
      X(r("j")), T(" to "), X(r("r")),
      T(" grows without bound as "), X(r("r")), T(" approaches "),
      X(L1 + r(" + ") + L2),
      T(": near full extension a small error in the wrist estimate becomes a large error in the flexion angle, because the triangle is nearly flat and its shape stops depending smoothly on its longest side. Above 98 percent of full reach the elbow is therefore taken from the direction memory instead, with the wrist still anchored at the object-derived estimate, and the two-link solution stays as the fallback for the case where no fresh memory exists.")]),
# reach guard 0.98 of L1+L2 in v1/kinematics/occlusion_ext.py

# ---------------------------------------------------------------- 5.5
(H2, "5.5 Torso Repair on Camera Rays"),

(P, "Section 5.3 showed that the object cannot fix a torso, but the torso corruption has a shape of its own that supplies the missing anchor. It is the silent failure of Section 5.1: the landmark detector finds the hip and the shoulder pixels correctly even while a hand, the carried cube, or the desk in front of the person sits between the camera and the trunk, and the depth sample behind the correct pixel is the part that fails. This section states that failure as a model, derives the repair it permits, sets out the three gates that decide when the repair runs, and closes with what the repair cannot do."),

(H3, "5.5.1 The Failure Model"),

(PM, [T("Appendix D lifts a landmark from its pixel (u, v) and the depth sample d behind that pixel through the inverse of the colour intrinsics K,")]),

(EQ, r("p") + r(" = ") + r("d") + r(" ") + sup(r("K"), r("−1")) + r(" ") + sup(d(r("u, v, 1")), r("T")), "5.12"),

(PM, [T("so that the third coordinate of "), X(r("p")), T(" is the depth d itself. The two factors of equation (5.12) come from different sensors and fail independently. The pixel comes from the landmark detector, which reads the colour image and infers the hip from the outline of the body even when the hip itself is hidden. The depth comes from the depth image at that pixel, which reports the nearest surface along that line of sight, whatever it is. When a hand, the cube or the desk edge occupies the pixel, the pixel stays right and d is the depth of the occluder. The corrupt point is therefore")]),

(EQ, sup(r("p"), r("′")) + r(" = ") + frac(sup(r("d"), r("′")), r("d")) + r(" ") + r("p"), "5.13"),

(PM, [T("a scaling of the true point along the ray from the camera origin through it, with "), X(sup(r("d"), r("′"))), T(" smaller than d for a surface in front of the body. Nothing else about the point moves. This is the whole content of the model, and it also explains why a confidence score cannot see the failure: the detector's confidence describes the pixel, and the pixel is correct.")]),

(PM, [T("The effect on the root frame is not small. Section 3.2 builds the trunk from the hip midpoint h and the shoulder midpoint s, and the pitch of the root frame is set by the direction of s − h. A depth error "), X(r("δ")), T(" common to both hips, taken positive toward the camera, leaves the shoulders where they are and moves the hip midpoint by "), X(r("δ")), T(" along the depth axis, so a trunk of height "), X(sub(r("L"), nor("t"))), T(" that stood upright is read as pitched by")]),

(EQ, nor("arctan") + r(" ") + d(frac(r("δ"), sub(r("L"), nor("t")))), "5.14"),

(PM, [T("toward the camera. A hip depth sample taken on a desk edge a few tens of centimetres in front of the pelvis, on a trunk half a metre long, produces a pitch of tens of degrees on a participant who is standing straight. The worked example of Chapter 3 shows exactly this on its frame, and the arm angles of that frame are read against the pitched root. Any arm angle that leaves the layer inherits the error of the frame it is expressed in, so the torso is repaired first.")]),

(H3, "5.5.2 The Ray Repair and the Depth Memory"),

(PM, [T("The model says which part of the measurement to keep. Every point with the pixel (u, v) lies on one ray through the camera origin, with direction "),
      X(frac(r("p"), p_z)), T(", where "), X(p_z),
      T(" is the depth coordinate of the point. Scaling the point by any positive factor leaves its pixel unchanged, because the projection u = f x / z + c divides x by z and the factor cancels; the same holds for v. The flip of equation (3.1) touches only the vertical axis, so the depth coordinate and the ray are the same in camera coordinates and in person space. The repair therefore keeps the ray and replaces only the depth: sliding the point along its ray until its depth equals a chosen value z* gives")]),

(EQ, sub(r("p"), nor("fixed")) + r(" = ") + frac(sup(r("z"), r("*")), p_z) + r(" ") + r("p"), "5.15"),

(PM, [T("which is the unique point with the measured pixel and the depth z*. The construction needs a positive measured depth, and a landmark whose depth sample places it at the camera is left missing. Equation (5.15) undoes equation (5.13) exactly when z* equals the true depth d, so everything below is about choosing z* and about deciding on which frames the substitution is made at all. The three gates of Sections 5.5.3 to 5.5.5 make that decision, and each supplies its own z*.")]),

(PM, [T("The first two gates draw z* from a depth memory. For each torso landmark the layer keeps "), X(z_mem),
      T(", the running average of that landmark's own depth,")]),

(EQ, sub(r("z"), nor("mem,") + r("k")) + r(" = ") + r("(1 − α) ") + sub(r("z"), nor("mem,") + r("k−1")) + r(" + α ") + sub(r("p"), r("z,k")), "5.16"),

(PM, [T("with the same gain α = 0.30 as the direction memories of equation (5.4), seeded with the first measured depth and updated only on frames where the landmark was measured and not gated. How the repair behaves follows from two properties of this memory. It is not updated from repaired values, so once a gate closes on a landmark the memory freezes at the last depth the gate accepted, and the repair holds the landmark at that depth for as long as the gate stays closed. Nor does the staleness limit of Section 5.2 apply to it: a standing trunk keeps its depth for the length of a take, while a limb direction does not, so the depth memory has no horizon. The repair keeps the part of the measurement that survived, the pixel, and replaces the part that failed, the depth. Figure 5.4 draws it.")]),
# depth memory: same dir_alpha 0.3 EMA, no horizon (self.H applies to
# _try_recover and the reach guard only), _ray returns None for z <= 0.05:
# v1/kinematics/occlusion_ext.py

(IMG, FIG / "ch5_fig_torso.png", 6.3),
(CAP, "Figure 5.4. (a) The torso repair, seen from above: the corrupt hip is pulled toward the camera along its ray, and sliding it back to its remembered depth restores the point and the hip line with it. (b) The depth-jump gate, drawn as a schematic illustration; Figure 7.9 shows what this gate does to the pelvis depth of the loop recording. While the measured depth stays inside a band about the remembered value the landmark is used as measured, and a departure beyond the band, here toward the camera, gates it into the repair. The shoulder-depth gate of Section 5.5.5 needs no panel: it is one threshold on the depth difference between a hip and the shoulder midpoint."),

(H3, "5.5.3 Gate One: Rigidity of the Torso"),

(PM, [T("The first gate applies the rigidity of the trunk inside the solve, in two tests, the width test and the line-consistency check. Both blame an endpoint by lengths calibrated per recording: the widths of the two pairs, hip to hip and shoulder to shoulder, and the four torso diagonals from each landmark to the midpoint of the opposite pair, each taken as the median over the first sixty frames on which both endpoints are measured. Until those sixty frames have been collected there is no calibrated length to blame an endpoint against, so neither test can gate a landmark, and over the opening of a take the torso is protected by the two gates below alone. Where the lengths are already known from an earlier calibration they are supplied instead, and the gate is live from the first frame.")]),
# gate_tol 0.30, calib_frames 60, DIAGONALS, seg_len constructor arg:
# v1/kinematics/occlusion_ext.py; _bad is False before self.L is filled

(PM, [T("Under the width test a pair whose measured width departs from its calibrated value by more than 30 percent is suspect. The test is on each width against its own median, not on the shoulder-to-hip ratio the detector of Table 5.1 watches, so the two carry different tolerances. Each endpoint of a suspect pair is then checked by its diagonal, the distance from the endpoint to the midpoint of the other pair, against the calibrated diagonal with the same 30 percent tolerance. Where exactly one endpoint fails its diagonal, that endpoint is gated and repaired on its ray. Where both fail or neither does, the width test alone cannot say which point moved, and the layer keeps both rather than guess. The line-consistency check can still take the pair, but only if the same corruption has also turned one of the two lines.")]),

(PM, [T("The line-consistency check is the rigidity statement of the torso line-angle detector. With the hip line "), X(r("h")), T(" from the left hip to the right hip and the shoulder line "), X(r("s")), T(" from the left shoulder to the right shoulder, the disagreement between the two lines is")]),

(EQ, r("θ") + r(" = ") + nor("arccos") + r(" ") + d(frac(r("h · s"), nrm(r("h")) + r(" ") + nrm(r("s")))), "5.17"),

(PM, [T("Where the two lines disagree by more than 20 degrees, one of them is corrupt, because a rigid trunk keeps them near parallel. The detector of Table 5.1 uses 22 degrees; both figures sit above the largest disagreement the clean frames of the reference recording show, 18.9 degrees. The corrupt line is the one whose direction has moved further from its own direction memory. With the two deviations")]),

(EQ, sub(r("Δ"), r("h")) + r(" = ") + nor("arccos") + r(" ") + d(hat(r("h")) + r(" · ") + sub(hat(r("h")), nor("mem")))
     + r(",      ") + sub(r("Δ"), r("s")) + r(" = ") + nor("arccos") + r(" ") + d(hat(r("s")) + r(" · ") + sub(hat(r("s")), nor("mem"))), "5.18"),

(PM, [T("the corrupt line is the one with the larger deviation, since corruption pulls one line away from its history while a real turn of the body moves both lines together and never opens a disagreement. The check needs both direction memories and cannot trip before they exist. The comparison is made once, on the frame the gate trips, and the line it blames stays the blamed line until the gate releases. Each endpoint of the corrupt line is then checked by its diagonal as above. Where exactly one endpoint fails, only that endpoint is gated. Otherwise the whole line is gated, and both endpoints are placed on their rays at their remembered depths by the pair rebuild of Section 5.5.6.")]),

(PM, [T("The gate has hysteresis: it trips above 20 degrees and releases only when the disagreement falls back under 10 degrees, so a corruption that settles just under 20 degrees does not release the constraint on the frame after it started. While the whole line is gated its direction memory is also mixed each frame with the direction of the surviving line, so a real turn of the trunk still reaches the gated pair.")]),
# line_tol_deg 20.0 (trip), line_release_deg 10.0 (release), have_mem,
# attribution once at trip via _dev, steer toward the surviving line:
# v1/kinematics/occlusion_ext.py; E-011b

(H3, "5.5.4 Gate Two: Depth Jump"),

(PM, [T("The first gate cannot see one kind of corruption. Corruption that takes both endpoints of one line together, a hand across the whole pelvis or a desk edge under both hips, scales the two endpoints by nearly the same factor, so that line keeps its direction and goes on agreeing with the other. A test built on their disagreement cannot see it. The width test misses it as well: a common scaling shrinks the pair's measured width in proportion to the depth, and an occluder a few tens of centimetres in front of the trunk moves it by less than the 30 percent that test allows. Such a landmark gives itself away in depth instead. Its measured depth is compared with its memory,")]),

(EQ, nrm(sub(r("p"), r("z,k")) + r(" − ") + sub(r("z"), nor("mem,") + r("k−1"))) + r(" > 0.10 m"), "5.19"),

(PM, [T("and a departure beyond 10 centimetres gates the landmark into the ray repair of equation (5.15) with z* set to the remembered depth. The band is read against the running average rather than against the previous frame. At thirty frames per second a landmark that leaves its own average by 10 centimetres has moved at 3 metres per second or has stopped being the landmark, and no torso in a desk task does the first. The clean frames of the reference recording deviate from their memory by a few centimetres at most. When both landmarks of a pair are gated on the same frame and the pair's width and direction memory are already calibrated, the pair rebuild of Section 5.5.6 repairs them together. A single gated landmark, and either landmark of a pair before that calibration completes, is repaired on its own ray.")]),
# z_tol 0.10 m: v1/kinematics/occlusion_ext.py; rationale in
# eval/DECISIONS.md E-011b; pair rebuild needs width in self.L and self.u

(H3, "5.5.5 Gate Three: Shoulder Depth"),

(PM, [T("The first two gates compare a measurement with its own history, so a hip whose depth is wrong from the very first frame passes both: the memory it is compared against was seeded from the same wrong depth, by equation (5.16), and nothing ever jumps. A surface that stays in front of the pelvis can produce that. In the recording of Chapter 2 the rail on the desk sits between the camera and the pelvis for almost the whole task. The depth sample behind each hip pixel lands on the rail, at least 20 centimetres nearer the camera than the shoulders for as long as both hips read it. The hips are measured on the body only at the opening of the take, before the participant settles over the desk, and again over the closing frames Section 7.4 describes. A take that began one second later would carry the wrong depth from its first frame. The third gate covers that case with a comparison that needs no history. It compares each hip with the shoulder midpoint "), X(sub(r("s"), nor("mid"))), T(" of the same frame:")]),

(EQ, sub(r("p"), nor("z,hip")) + r(" − ") + sub(r("s"), nor("mid,z")) + r(" < −0.15 m"), "5.20"),

(PM, [T("A hip that satisfies equation (5.20) is gated, and the repair places it on its ray at the depth of the shoulder midpoint, z* = "), X(sub(r("s"), nor("mid,z"))), T(", the depth an upright trunk gives it. The midpoint is the one the shoulders measure at the top of the frame, before any gate has run, so the gate reads the trunk as the sensor reported it. It is evaluated only when both shoulders are reported, and it is tested only on a hip the first two gates have left in place. Intersecting the hip's ray with a sphere of the calibrated diagonal about the shoulder midpoint would fix the depth without reference to a lean, and it is not used here. The diagonal is nearly vertical and the ray nearly horizontal, so the sphere meets the ray almost tangentially, and the depth the intersection returns swings by tens of centimetres under a centimetre of noise.")]),

(PM, [T("The tolerance follows from the geometry of a lean. Here the trunk turns about the hip and keeps its own length, so the angle is measured from the vertical of an upright trunk rather than by the small-offset form of equation (5.14). A trunk of length "), X(sub(r("L"), nor("t"))), T(" leaning by an angle "), X(r("φ")), T(" in the depth direction separates the hip depth from the shoulder depth by")]),

(EQ, r("Δz") + r(" = ") + sub(r("L"), nor("t")) + r(" sin ") + r("φ"), "5.21"),

(PM, [T("so with the participant's trunk length of about 0.48 metres, the value Section 6.3 quotes, the 15 centimetre threshold corresponds to a trunk leaning 18 degrees back from the camera, which a participant working over a desk does not produce. On the clean torso frames of the loop recording, where the hips are measured on the body, the hip-to-shoulder depth difference stays inside 10 centimetres either way over all but the extreme percentile, a lean of 12 degrees. The rail puts the corrupt hips at least 20 centimetres nearer. The threshold sits between the two. The sensor's optical axis is close to horizontal, its tilt being part of the scene calibration of Chapter 4, so an upright trunk puts the two depths within a few centimetres of each other and equation (5.20) reads the lean almost directly.")]),
# lean_tol 0.15 m: v1/kinematics/occlusion_ext.py; loop clean-frame
# p01/p99 -0.10/+0.10, rail hips -0.20..-0.36 over frames 12-631 (the
# filtered landmark CSV; E-027's "0.20-0.32" is stale): review
# writing/reviews/Chapter_5_torso_round1.txt; L_t 47.9 cm: build_ch6.py;
# asin(0.15/0.48) = 18.2 deg, asin(0.10/0.48) = 12.0 deg

(PM, [T("Two consequences of the placement should be stated plainly. The repaired hip sits where an upright trunk would put it, so any real lean the participant has is lost on the frames this gate carries. That is the price of a comparison without history, and it is no larger than the lean the loop recording shows, about 10 centimetres. The precedence between the gates then decides which depth a hip receives when more than one would fire. Because the shoulder-depth gate is tested only on hips the first two gates passed, once a hip's measured depth has left a memory seeded on the body the depth-jump gate settles the repair at the remembered depth, and the shoulder depth is not used. Only while that memory still matches the measurement can the shoulder comparison decide anything, and that is the case of a take that begins with the pelvis already occluded.")]),

(H3, "5.5.6 Rebuilding the Pair"),

(PM, [T("A landmark the shoulder-depth gate takes is placed by equation (5.15) and nothing else, whether one hip or both. A single landmark the first two gates take is placed by equation (5.15) as well; where it has no depth memory to place it at, it is left missing and is rebuilt from its partner by the rule at the end of this section. Behind the rebuild of a pair the first two gates take together, both hips or both shoulders, are two sources of different reliability, and position and orientation are taken from different ones. Let "), X(sub(r("q"), r("a"))), T(" and "), X(sub(r("q"), r("b"))), T(" be the two endpoints after each has been slid to its remembered depth. The position of the pair is their midpoint,")]),

(EQ, r("m") + r(" = ") + frac(r("1"), r("2")) + r(" ") + d(sub(r("q"), r("a")) + r(" + ") + sub(r("q"), r("b"))), "5.22"),

(PM, [T("and taking the midpoint of two ray-repaired points stops the depth of the pelvis from wandering. The orientation comes from the pair's direction memory "), X(sub(hat(r("u")), nor("pair"))), T(", updated by the rule of equation (5.4) with the direction from "), X(sub(r("q"), r("a"))), T(" to "), X(sub(r("q"), r("b"))), T(". Raw per-frame ray directions carry the sideways wobble of the pixels while a hand crosses the trunk; the memory attenuates that wobble while still following a real turn. The two landmarks are then placed symmetrically about the midpoint at the calibrated width w of the pair,")]),

(EQ, sub(r("p"), r("a")) + r(" = ") + r("m") + r(" − ") + frac(r("w"), r("2")) + r(" ") + sub(hat(r("u")), nor("pair"))
     + r(",      ") + sub(r("p"), r("b")) + r(" = ") + r("m") + r(" + ") + frac(r("w"), r("2")) + r(" ") + sub(hat(r("u")), nor("pair")), "5.23"),

(PM, [T("That width is the physical separation of the pair, which the pose of the trunk does not change. Its projection into the image does change, so a single repaired landmark is not pushed to the calibrated width against a measured partner, and rigidity is used there as a test and not as a construction. Before the depth memories exist, in the first frames of a take, the pair is rebuilt about its measured midpoint along the direction memory instead. When neither a ray nor a depth memory is available, the torso frame holds its last value.")]),

(P, "The same pair mechanism serves the case where a torso landmark is missing rather than corrupt. A missing hip is placed at the calibrated hip width from the other hip, along the direction memory of the hip line, and a missing shoulder likewise. Here the staleness limit of Section 5.2 does apply, because a missing landmark is rebuilt from its neighbour by the recovery rule of that section and inherits the horizon that comes with it. The rebuild of a gated pair above is this section's own and carries no horizon, since the depth memory it rests on has none. Rebuilding the shoulder matters beyond the torso, because the shoulder is where each arm chain is anchored: a shoulder that is restored keeps that arm solving instead of freezing it. The root frame of Section 3.2 is then built from the repaired points exactly as from measured ones, and the arm angles are read against it."),

(H3, "5.5.7 What the Repair Cannot Do"),

(P, "The repair rests on the failure model of Section 5.5.1, and it reaches exactly as far as that model holds. It corrects a right pixel over a wrong depth. It does nothing for a wrong pixel: a landmark the detector places on the occluder itself, or a hip it invents on the far side of a desk, keeps a wrong ray, and sliding along a wrong ray cannot recover the point. The first gate may still catch such a landmark through the width or the diagonal it breaks, but the repair that follows is then a repair along the wrong line. A shoulder pair whose own depths are wrong carries the hips to the same wrong depth through the third gate. Chapter 7 measures that case on the loop recording, against manually labelled landmarks."),

(P, "The first two gates depend on a memory that was seeded correctly, and the memory is frozen for as long as the gate stays closed. A participant who steps back while both hips are gated is held at the depth the take began with, and nothing in the layer notices, because the frozen memory is exactly what the repair trusts. The calibration of Section 5.5.3 is open to the same steady offset. The pair widths are taken from the measurement as it arrives, so a take whose opening frames are already occluded calibrates its widths on the occluder, and the rebuild of equation (5.23) then holds the pair at a width learned from the wrong depth. The third gate has no memory to freeze, and pays for it by losing the lean. Chapter 7 reports how each gate behaved on the two recordings, and Chapter 9 states the cases that remain untested."),
# width calibration observes raw input before gating (line ~417); the
# diagonals are observed after gating: v1/kinematics/occlusion_ext.py

# ---------------------------------------------------------------- 5.6
(H2, "5.6 Output States of the Solver"),

(P, "A layer that rebuilds landmarks has to say so. The solve of Chapter 3 does not produce one indivisible pose; it produces seven joint groups, and each group depends on its own small set of landmarks. Table 5.2 lists them. The root takes either shoulder, because the shoulder only selects which plane through the hip line is the plane of the trunk. The grouping makes a partial failure affordable: a lost wrist costs the twist and the flexion of one arm and leaves the other arm and the torso untouched."),

(TBL, [["Joint group", "Landmarks it needs"],
       ["Root", "both hips, and either shoulder"],
       ["Shoulder swing, one arm",
        "that arm's shoulder and elbow, with the current or held root"],
       ["Shoulder twist, one arm",
        "that arm's shoulder, elbow, and wrist"],
       ["Elbow flexion, one arm",
        "that arm's shoulder, elbow, and wrist"]]),
# groups and landmark requirements: v1/kinematics/occlusion.py docstring
(CAP, "Table 5.2. The seven joint groups of the solve and the landmarks each needs. The two arms contribute three groups each and the root contributes the seventh."),

(P, "Each group leaves the layer with one of three states, named measured, held and constrained. A group is measured when every landmark it needs was measured and unflagged on this frame. A group is held when it keeps the value it last had, which happens when a landmark it needs is missing and nothing rebuilt it. A group is constrained when it was solved on this frame but one of the landmarks it used had been rebuilt: a wrist from the object by equation (5.5), an elbow from the circle of equation (5.11), a torso point from its camera ray by equation (5.15), or a landmark placed from its partner along a direction memory."),

(P, "Two limits add to these states without any landmark going missing, and both come from angles that the landmarks cannot determine in some configurations. The shoulder twist is read from the part of the forearm that is perpendicular to the upper arm, and that part vanishes as the elbow straightens, as Section 3.4.3 sets out. Below 15 degrees of elbow flexion the twist keeps its previous value and its group leaves the layer held, and the hold is released again only above 25 degrees, so that the twist resumes on a measurement worth having. The constrained state has one further source of its own. Every arm angle passes a limit of 15 degrees of change between consecutive frames, which bounds the step the output can take when a joint re-locks after a hold or moves into a reconstruction. While that limiter is clamping, the value leaving the layer is not the value the solve computed, so the group is marked constrained until the two agree again. The root is exempt from the limiter, because the torso gates of Section 5.5 already govern it."),
# twist hold tags the group HELD; only the rate limiter produces a
# CONSTRAINED tag without a rebuilt landmark: v1/kinematics/occlusion_ext.py

(P, "Figure 5.5 collects the whole path of one frame through the layer, from the landmarks that arrive to the seven groups that leave it. The states travel with the angles. Chapter 6 carries them into the reconstruction, where a held joint and a reconstructed joint are drawn in different colours so that a viewer can see which parts of the pose are measured, and Chapter 7 uses them to separate the frames that carry a measurement from the frames that carry a reconstruction."),

(IMG, FIG / "ch5_fig_states.png", 6.3),
(CAP, "Figure 5.5. One frame through the solver layer. The detectors decide which landmarks are wrong and remove them, the rebuild stage replaces what it can in dependency order, the wrist before the elbow, the solve of Chapter 3 runs on the assembled points, and each of the seven joint groups leaves with one of the three states. The lower strip gives the meaning of each state and how it is drawn in the reconstruction."),

(P, "No fit in this chapter is ever made on the frames being recovered. Every quantity used on a frame is either measured on that frame, which covers the object pose and the surviving landmarks; a calibrated constant, which covers the segment lengths, the pair widths, and the scene calibration; or a state carried from earlier frames, which covers the holding state, the direction and depth memories, and the previous output angles. Four inputs of the layer do reach past the current frame within the recording. The holding state supplies the first two: each end of a grip episode is confirmed only after its five-frame run of Section 5.2 has completed, and is then dated back to the first frame of that run. The warm-up of an episode is the third, since its frames take the mean offset of the whole episode and so draw on clean frames later in that episode. The fourth sits upstream of the grip machinery: the mask cleaning of Section 5.1 looks at what follows a frame as well as at what precedes it, and the grip machinery inherits those masks through the clean frames it is allowed to fit on."),

# src: the live replacements, one per item, are Chapter 8 section 8.1
#      (writing/v7/scripts/build_ch8.py) and Table 8.1
(P, "Chapter 8 describes the version of this layer that runs while the motion happens, and the four are not replaced in the same way. The offset fit becomes an accumulator that sees only the past, a running mean over the first clean frames of an episode and then a slowly updated moving average. The episode exit becomes a bounded-delay confirmation: the five-frame release condition on a cleanly measured wrist runs as the frames arrive, and the wrist stays anchored to the object until it completes. The entry back-dating has no live counterpart. And the cleaned masks give way to per-frame tests, since the live solver gates each frame on its own as the frame arrives. The accuracy of the recovered pose is evaluated in Chapter 7, and the cost of the layer per frame is reported in Chapter 8."),
]

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
                cell.text = cval
                for par in cell.paragraphs:
                    for run in par.runs:
                        run.font.size = Pt(10)
                        if i == 0:
                            run.font.bold = True

out = REPO / "writing" / "v7" / "Chapter_5_Pose_Recovery.docx"
doc.save(out)
print("saved", out, "| items:", len(content))

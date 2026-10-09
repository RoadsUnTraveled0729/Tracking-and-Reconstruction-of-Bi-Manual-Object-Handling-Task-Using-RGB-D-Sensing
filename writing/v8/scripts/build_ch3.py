#!/usr/bin/env python3
"""Build writing/v8/Chapter_3_Kinematic_Modeling.docx (V8 rewrite round).

Chapter 3 against the V8 TOC: 3.1 Coordinate Systems and Transformations
(old 3.1.1 + 3.1.2 merged), 3.2 Torso Reference Frame, 3.3 The Arm Model
with the NEW 3.3.1 kinematic schematic (supervisor comment C9), 3.4 Joint
Angle Computation with 3.4.4 rewritten as "The Wrist as a Tracked Point"
(C10), and 3.5 Worked Example consolidating the three old per-stage
examples into one continuous solve that cites the schematic labels (C11).
The old Unity-mapping section moves to Chapter 6 and is not built here.

Round of 2026-08-31 (supervisor comments C15-C21, PROF_COMMENTS_ROUND3):
the homogeneous T matrix shown wherever R and t appear (general form
eq 3.2/3.4, chain definitions eq 3.5/3.6, root eq 3.12, shoulder eq
3.13, elbow eq 3.14, all three numerically in Section 3.5), and the
information-flow diagram as the new Figure 3.1 (make_ch3_flow_fig.py);
equations and figures renumbered accordingly.

Worked example pinned to frame 533 of the rail recording
recording_20260831_065553 (rail-only round 2026-09-01; replaced R5
frame 270); every number printed here is produced by
writing/v7/scripts/ch3_numbers.py. The hip landmarks of that frame
take their depth from the rail (0.99 m against 1.33 m at the
shoulders), so the root frame decodes to a 32.08 degree pitch on an
upright subject; the worked example states that plainly.
Figures: writing/v8/figures/ (regenerated from the same frame; see
make_ch3_figs.py, make_ch3_chain_fig.py, make_ch3_fig2.py).

Humanizer pass 2026-09-06 (writing/WRITING_SKILL.md = blader/humanizer,
user direction): prose redrafted against the 35 patterns plus the kept
supervisor constraints; every EQ/MATH/IMG/TBL item, number, citation,
cross-reference and the ten comment anchors (C9-C11, C15-C21) kept;
review loop in writing/reviews/Chapter_3_humanizer_round*.txt. The
worked-frame cross-reference "Figures 3.4 and 3.9" was a renumbering
leftover and now reads 3.4 and 3.8. Body spelling is Canadian
(modelling); the chapter title keeps the TOC spelling.
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches

from eqn import r, nor, sub, sup, hat, frac, mat, d, eqArr, \
    add_display_eq, add_display_math, add_inline_math

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v8" / "figures"

H1, H2, H3, P, IMG, CAP, TBL, EQ = "h1", "h2", "h3", "p", "img", "cap", "tbl", "eq"
MATH = "mth"  # displayed, unnumbered worked-example mathematics
PM = "pm"     # paragraph mixing text runs and inline math


def T(t):
    return ("t", t)


def X(f):
    return ("m", f)


# --- equation-fragment shorthands ---
def Rot(axis, arg=None):
    base = sub(r("R"), r(axis))
    return base + (d(arg) if arg is not None else "")


def t_(axis):
    return sub(r("t"), r(axis))


def cs(letter, axis):
    return sub(r(letter), r(axis))


p23 = sub(r("p"), r("23"))
p24 = sub(r("p"), r("24"))
p12 = sub(r("p"), r("12"))
p14 = sub(r("p"), r("14"))
p16 = sub(r("p"), r("16"))
Rroot = sub(r("R"), nor("root"))
RrootT = sup(sub(r("R"), nor("root")), r("T"))
# Side-explicit subscripts (user direction 2026-08-31): frames and
# transforms that exist once per arm carry the side after the comma,
# "sh,r" for the right shoulder, "sh,l" for the left. The chapter
# derives the right arm; the left counterparts come from the mirror.
Rsh = sub(r("R"), nor("sh,r"))
Troot = sub(r("T"), nor("root"))
Tsh = sub(r("T"), nor("sh,r"))
Tel = sub(r("T"), nor("el,r"))
Tshl = sub(r("T"), nor("sh,l"))
Tell = sub(r("T"), nor("el,l"))
Tarm = sub(r("T"), nor("arm,r"))
Rarm = sub(r("R"), nor("arm,r"))


def blockT(rot, trans):
    """4x4 homogeneous transformation as a 2x2 block matrix."""
    return mat([[rot, trans], [r("0"), r("1")]])
xhat = hat(r("x"))
yhat = hat(r("y"))
zhat = hat(r("z"))
ahat = hat(r("a"))
ghat = hat(r("g"))

content = [
(H1, "Chapter 3: Kinematic Modeling"),

(P, "The previous chapter ends with eight body landmarks per frame, each lifted to a metric 3D position in the camera frame. Appendix C lists the landmark set and how the detector reads it out, and Appendix D covers the lifting. The positions arrive labelled and in a fixed order. On their own, though, they say nothing about how the body segments are oriented relative to one another or how each joint has rotated from one frame to the next. This chapter builds the kinematic model that gives the points that meaning. The model is a chain of coordinate frames rooted at the pelvis and running out through the shoulder and elbow of each arm. The hand model of [41] uses the same hierarchical construction. Once the chain is built, the pose of the body reduces to the orientation and position of the torso plus a small set of joint angles: a swing and a twist for each shoulder, and a flexion angle for each elbow. Chapter 6 maps those angles onto the Unity avatar."),

(P, "The later chapters rely on a few properties of the model. It is closed form: every angle comes directly from the landmark geometry of the current frame, with no optimization and no temporal state. Composing the solved angles rebuilds the rotation they were read from, so the model is invertible and the angle set describes the measured pose instead of approximating it. The same construction also works for both arms, because the left arm is solved by the right-arm equations applied to mirrored segment vectors. The chapter follows the order of the chain: the mathematical tools first, then the torso root frame, the arm model, and the joint angles, with a worked example on one measured frame at the end."),

(P, "Figure 3.1 draws the information flow of the whole chapter. The calibrated landmarks of Chapter 2 enter on the left, each box names the section that builds its contents, and the thirteen angles per frame leave on the right for the avatar of Chapter 6. Section 3.1 defines the transformations written on the arrows and states, once for the whole chapter, the logic behind them."),

(IMG, FIG / "ch3_fig_flow.png", 6.3),
(CAP, "Figure 3.1. The information flow of this chapter. Landmarks enter from the measurements of Chapter 2 (left), after the recovery of Chapter 5 has replaced any that failed. The torso landmarks give the root frame and its transformation with respect to person space, and each arm landmark is then carried through the relative transformations into the frame where its joint is solved. The output is the thirteen-angle pose of one frame (right). The section numbers in the boxes locate each construction."),

(H2, "3.1 Coordinate Systems and Transformations"),

(P, "A coordinate frame is an origin together with three mutually perpendicular unit vectors, labelled x, y and z, which set the directions of the three axes. A point in space is described by how far one travels from the origin along each axis to reach it. The whole kinematic model is built from such frames, one attached to each body segment. When a segment moves, its frame moves with it, so the relationship between two frames captures the orientation of one segment relative to the other. Every number in this chapter belongs to one frame, and the frame is stated wherever a number appears. The two frames at the two ends of the system are defined first."),

(P, "Chapter 2 reports every measurement in the camera frame C. Section 2.2 defines that frame and the scene frames, and Figures 2.4 and 2.5 draw them. Unity instead uses a left-handed frame with y upward, so the body model needs a frame of its own."),

(P, "Figure 2.4(b) also fixes a distinction used throughout this chapter. The frame shown there belongs to the root of the avatar rig and is aligned with the axes of the Unity world. The measured root frame of the body is a different frame, one that rides the torso. At the worked-example frame its yaw decodes to 179.49 degrees because the subject faces the sensor, and Section 3.5 prints that value. Person space itself is anchored at the camera, while the Unity world is anchored at the desk marker of Chapter 4. The reconstruction stays correct across these differences. Every joint angle of this chapter is defined relative to its parent frame, so relative rotations hold the pose of the body and no change of global frame can alter it. The reconstruction places the person into the world through the calibrated camera pose, which Chapter 6 composes once into an anchor node, so the root lands in the right place without the frames ever being equated. And the system has two handedness conversions, the point flip of equation (3.1) below and the axis swap where the object track of Chapter 4 is exported. Both are reflections with determinant -1, so their composition through the calibrated pose has determinant +1 and no net mirror reaches the rendered scene."),

(P, "A right-handed and a left-handed frame have opposite orientations, so the conversion has to change the handedness itself rather than relabel the axes. Throughout this work the conversion is one matrix multiplication applied to every measured point. If p is a landmark position in the camera frame, its position q in the person space P that all the kinematic math uses is"),

(EQ, r("q") + r(" = ") + r("F") + r(" ") + r("p") + r(",        ") + r("F") + r(" = ") + nor("diag") + d(r("1, −1, 1")), "3.1"),

(P, "that is, the y coordinate flips sign and x and z pass through unchanged. Flipping exactly one axis turns a right-handed frame into a left-handed one, and the determinant of F is -1, the sign of a reflection. After the flip, x still points to the right in the image, y points up, and z still points away from the camera, which is the Unity convention. Both frames keep the same origin at the optical centre of the camera, and only the reading of the y axis changes. The flip applies to points only, never to rotation matrices. Every rotation below is built from points that have already been flipped, so every rotation in the pipeline comes out proper. Figure 3.2 shows the two frames drawn from that shared origin, together with one measured wrist position. The right wrist of the worked-example frame of Section 3.5 reads (-0.20, 0.11, 1.06) in the camera frame and (-0.20, -0.11, 1.06) in person space: the same physical point, with one coordinate flipped. From here on, every landmark position in this chapter is a person-space value unless stated otherwise."),

(IMG, FIG / "ch3_fig_colocated.png", 5.6),
(CAP, "Figure 3.2. The camera frame C and person space P drawn from the same origin, each axis labelled with the frame it belongs to. Only the y axis differs: the camera reads y downward and person space reads y upward. The wrist landmark of the worked-example frame is shown with its coordinates in both frames."),

(P, "The handedness of a frame changes no physical result, so the left-handed choice is one of convenience. The angles this chapter produces drive the Unity animation system, and so the kinematics are computed in the convention Unity uses. Converting the points is also cheaper than converting the rotations: a point crosses a handedness change with one sign flip, while a rotation crosses by conjugation with every sign convention changing along the way. Each measured point is therefore flipped once at the entry and no solved rotation is converted at the exit. Chapter 4 makes the opposite choice for the object track, which stays in the desk-anchored frame of the rail it is compared against and converts only when its poses are exported."),

(P, "The relationship between two coordinate frames has two parts: how the child frame is rotated relative to the parent, and where the child's origin sits in the parent's coordinates. Together they form a rigid body transformation, an operation that moves and turns an object without deforming it [42]. The rotation part is a 3 by 3 matrix R whose three columns are the axis directions of the child frame written in the parent's coordinates. Because the columns are perpendicular unit vectors, the transpose of R equals its inverse and its determinant equals one. This property is used throughout: a vector expressed in the parent frame is brought into the child frame by multiplying with the transpose, and no matrix is ever inverted numerically. The translation part is a 3-vector t giving the position of the child's origin in the parent frame. The two combine into one representation, the 4 by 4 homogeneous transformation matrix T, written with R and t as blocks:"),

(EQ, r("T") + r(" = ") + blockT(r("R"), r("t")) + r(",        ") +
     mat([[sub(r("p"), nor("parent"))], [r("1")]]) + r(" = ") + r("T") + r(" ") +
     mat([[sub(r("p"), nor("child"))], [r("1")]]), "3.2"),

(P, "The bottom row is the constant (0, 0, 0, 1). Appending a 1 to a point turns the rotation and the shift into a single matrix multiplication. Written out, the product rotates a point known in the child frame by R and moves it by t to give the same point in the parent frame. A single matrix therefore holds the complete pose of a frame, and the chapter writes these matrices as the letter T with a subscript naming the frame."),

(P, "This representation pays off when transformations chain. If a transformation A describes the torso frame relative to person space and a transformation B describes a shoulder frame relative to the torso, the product AB describes the shoulder frame directly in person space. Rotations defined locally, each relative to its immediate parent, accumulate into one description of the whole arm. The same property runs in reverse when the angles are computed: given a measured segment direction v in person space and the known orientation of its parent frame, the direction of the segment in the parent frame is"),

(EQ, sub(r("v"), nor("local")) + r(" = ") + sup(sub(r("R"), nor("parent")), r("T")) + r(" ") + r("v"), "3.3"),

(P, "Here v is a direction vector between two landmarks, not a point. Throughout this chapter p marks a measured landmark point and v marks a segment vector formed from two points. Directions transform by rotation alone. Equation (3.3) is the rotation part of the transformation acting on its own, so its scope needs care. It applies to directions, which have no location, and to points only when the child and the parent frames share one origin. A measured landmark is a point, and the frames of the chain sit at different places on the body, so mapping a landmark between frames needs the full T of equation (3.2). Inverting the block form gives the mapping of a point from the parent frame into the child frame:"),

(EQ, sub(r("p"), nor("child")) + r(" = ") + sup(r("R"), r("T")) + r(" ") +
     d(sub(r("p"), nor("parent")) + r(" − ") + r("t")) + r(",        ") +
     sup(r("T"), r("−1")) + r(" = ") +
     blockT(sup(r("R"), r("T")), r("−") + sup(r("R"), r("T")) + r("t")), "3.4"),

(P, "The inverse follows from what is already stated: the rotation block inverts to its transpose, and the origin offset reverses. As operations on the point, the offset is removed first and the transposed rotation then describes the point along the axes of the child. Every derivation in Section 3.4 uses these two operations, one to compose transformations forward along the chain and one to pull measured points and vectors back into local frames. Figure 3.3 draws the chain on the worked-example frame of Section 3.5, a measured frame of the recording of Chapter 2, with the three frames of the right arm chain at their anatomical origins."),

(IMG, FIG / "ch3_fig_chain_photo.png", 6.0),
(CAP, "Figure 3.3. The kinematic chain drawn on the worked-example frame of the recording, front view. The root frame sits at the right hip L24, the shoulder frame at L12, and the elbow frame at L14. The x axis continues the upper-arm axis down the arm that holds the cube of the task of Chapter 2."),

(P, "Each neighbouring pair of frames in Figure 3.3 is related by its own homogeneous transformation. Written out, the three show that the frames differ in both their relative rotation and the position of their origin:"),

(EQ, Troot + r(" = ") + blockT(Rroot, sub(r("t"), nor("root"))) + r(",    ") +
     Tsh + r(" = ") + blockT(r("I"), sub(r("t"), nor("sh,r"))) + r(",    ") +
     Tel + r(" = ") + blockT(Rsh, sub(r("t"), nor("el,r"))), "3.5"),

(PM, [T("From here on, a frame that exists once per arm has its side in the subscript, r for the subject's right and l for the left, so "),
      X(Tsh), T(" is the right shoulder frame and "), X(Tshl),
      T(" the left. The chapter derives the right arm, and the left-arm transformations follow from the mirror construction of Section 3.4.2. Each transformation has its own rotation and its own origin. "),
      X(Troot),
      T(" is the pose of the root (torso) frame with respect to person space, built in Section 3.2. "),
      X(Tsh),
      T(" is the pose of the right shoulder frame with respect to the root, with the 3 by 3 identity I for its rotation block. "),
      X(Tel),
      T(" is the pose of the right elbow frame with respect to the shoulder frame, with the solved shoulder rotation "),
      X(Rsh),
      T(" for its rotation block. Section 3.3.3 places both origins. Chaining the three describes the right elbow frame directly in person space,")]),

(EQ, Tarm + r(" = ") + Troot + r(" ") + Tsh + r(" ") + Tel, "3.6"),

(P, "These relative transformations are the plan of the whole chapter. Every landmark is measured with respect to the sensor and converted to person space by equation (3.1), and the relative transformations then carry it into the frame where it is needed. Applying the inverse of the root transformation, by equation (3.4), expresses a measured landmark with respect to the torso. The shoulder landmark, for example, becomes the shoulder position in the root frame, and that position is the origin offset of the shoulder frame. Next, the inverse of the shoulder transformation puts a point in the shoulder frame, so the elbow landmark can drive the shoulder angles of Section 3.4.2. Last comes the elbow inverse, which expresses the wrist with respect to the elbow frame, where the elbow flexion of Section 3.4.3 is read. Section 3.5 prints all three transformations as numbers on a measured frame."),
(H2, "3.2 Torso Reference Frame"),

(H3, "3.2.1 Landmark Selection"),

(P, "The right hip L24, the left hip L23, and the right shoulder L12, three MediaPipe landmarks [43], define the torso root. Left and right always refer to the subject, who faces the sensor, so the right side appears on the left of the image."),

(P, "The choice rests on geometry and visibility. The hip and shoulder points move more slowly than the hands and forearms, and the object rarely hides them. A full orientation needs a plane, and three points not on one line are the minimum for a plane. These three landmarks also form a broad triangle across the trunk, so a small position error changes the angles only a little."),

(P, "With only three torso points, the model cannot separate the pelvis from the upper trunk, so it assumes no relative twist between the shoulders and the hips. The model treats the whole torso as one rigid plate, and the frame captures the orientation of that plate, so a forward lean of the trunk pitches the root frame with it. The present model accepts this simplification, and Chapter 9 revisits it in the limitations."),

(H3, "3.2.2 Derivation of the Torso Frame"),

(PM, [T("The three landmark positions arrive from Chapter 2 in the camera frame. The flip F of equation (3.1) converts them to person space, and the whole construction below happens there. Let "),
      X(p23), T(", "), X(p24), T(", and "), X(p12),
      T(" be the person-space positions of the left hip, the right hip, and the right shoulder. This section derives the orientation and the location of the torso plane, and the result is a rotation matrix and an origin. Figure 3.4(a) shows the two input vectors drawn on the image of the worked-example frame, and Figure 3.4(b) shows the finished frame projected back onto the same image.")]),

(IMG, FIG / "ch3_fig_torso_photo.png", 6.3),
(CAP, "Figure 3.4. The torso frame on the image of the worked-example frame. (a) The two input vectors. The hip line runs from L23 to L24 (red), and the spine-side vector s runs from L24 up to L12 (yellow). (b) The finished orthonormal frame at the L24 origin, projected through the camera intrinsics. The x axis points toward the subject's right, the y axis points up along the trunk, and the z axis points forward out of the chest. The y and z axes lean in the image because the measured frame is pitched, as Section 3.5 explains."),

(P, "The x axis comes first. It is the unit vector along the hip line, pointing toward the subject's right, and the hat marks a unit vector."),
(EQ, xhat + r(" = ") + frac(p24 + r(" − ") + p23,
     d(p24 + r(" − ") + p23, "|", "|")), "3.7"),
(P, "Subtracting the left-hip position from the right-hip position already gives a vector that points to the subject's right, so no sign correction is needed, and that vector becomes the +x axis of the torso frame. The axis is kept exactly as measured, because both of its endpoints are pelvis landmarks and the hip line is the one direction the three points define with no ambiguity."),

(P, "The second input is the spine-side vector from the right hip up to the right shoulder."),
(EQ, r("s") + r(" = ") + p12 + r(" − ") + p24, "3.8"),
(PM, [T("This vector is not used as an axis, because it is generally not perpendicular to the hip line. In the worked-example frame the angle between them is 83.81 degrees, not 90, and treating it as an axis would give a skewed frame with axes that are not at right angles. It only selects the torso plane: many planes contain the hip line, and the torso plane is the one that also contains "),
      X(r("s")), T(".")]),

(PM, [T("The z axis comes from the cross product. For two vectors "),
      X(r("a")), T(" and "), X(r("b")), T(", the cross product "),
      X(r("a") + r(" × ") + r("b")),
      T(" is perpendicular to both. Its components are")]),
(MATH, d(cs("a","y")+cs("b","z") + r(" − ") + cs("a","z")+cs("b","y") + r(",   ") +
         cs("a","z")+cs("b","x") + r(" − ") + cs("a","x")+cs("b","z") + r(",   ") +
         cs("a","x")+cs("b","y") + r(" − ") + cs("a","y")+cs("b","x"))),
(P, "Applying it to the two inputs and normalizing gives"),
(EQ, zhat + r(" = ") + frac(xhat + r(" × ") + r("s"),
     d(xhat + r(" × ") + r("s"), "|", "|")), "3.9"),
(PM, [T("The order of the two factors sets the sign. With "),
      X(xhat), T(" pointing to the subject's right and "), X(r("s")),
      T(" pointing up the trunk, the product points forward, out of the subject's chest toward the camera. Reversing the order would flip the axis into the subject's back. The cross product also discards the part of "),
      X(r("s")), T(" that is parallel to "), X(xhat),
      T(". The imperfect angle between the inputs therefore does no harm, because only the component of "),
      X(r("s")), T(" perpendicular to the hip line contributes.")]),

(P, "The y axis closes the frame with a second cross product."),
(EQ, yhat + r(" = ") + zhat + r(" × ") + xhat, "3.10"),
(PM, [T("The vectors "), X(zhat), T(" and "), X(xhat),
      T(" are already perpendicular unit vectors, so their product is exactly a unit vector and needs no normalization. This third step guarantees an orthonormal frame in every measured pose, and the result is the anatomical up direction along the trunk.")]),

(P, "The three axes assemble into the root rotation matrix. Its columns are the axes of the frame in the person-space order right, up, forward."),
(EQ, Rroot + r(" = ") + mat([[xhat, yhat, zhat]]), "3.11"),
(PM, [T("The right hip position "), X(p24),
      T(" is the origin. Together they fill in the first transformation announced in equation (3.5), the pose of the root frame with respect to person space.")]),

(EQ, Troot + r(" = ") + blockT(Rroot, p24), "3.12"),

(P, "Every arm frame in the following sections is expressed relative to this matrix. Its inverse, by equation (3.4), carries any measured landmark into the torso's own coordinates."),

(PM, [T("Figure 3.5 shows the reference configuration that fixes the meaning of the finished matrix. Panel (a) is the subject in the laboratory, standing upright, facing the sensor, with the arms straight out to the sides, and a frame is drawn at every landmark of the model at its zero configuration. The root frame sits at the right hip, and the left hip has the same orientation. The two shoulder frames share the orientation of the root, the two elbow frames have x along each upper arm, and the two wrists, the tracked points that end the chain, have x along each forearm. Panel (b) is the avatar of the reconstruction in the same pose. This is the T-pose, the zero of every arm angle in Section 3.3. An ideal upright subject facing the camera has the right side toward the camera's left and the chest toward the negative z of person space, and substituting these ideal directions gives exact values. The matrix "),
      X(Rroot), T(" then has the columns (-1, 0, 0), (0, 1, 0), (0, 0, -1). In the convention of Section 3.4 this decodes to the Euler angles (0, 180, 0), an avatar standing upright and turned 180 degrees to face the viewer. The check matters because a proper rotation matrix alone does not pin down a construction. The same axes can be assembled with the forward direction in the up column. That is still a proper rotation matrix, but its reference pose decodes to (90, 0, 0), a rig lying flat on its back, and the reference pose check catches that kind of error before it reaches the avatar.")]),

(IMG, FIG / "ch3_fig_tpose.png", 6.3),
(CAP, "Figure 3.5. The reference configuration. (a) The subject in the T-pose in the laboratory, with the RGB-D camera on its mount at the desk edge, the desk with the rail, and the wall marker behind. A frame is drawn at each of the eight landmarks the detector finds on this photograph, at its zero configuration. The x axis is red, the y axis is green, and the z axis is blue, with z drawn shorter because it points toward the viewer. (b) The Unity avatar upright and facing the viewer at root Euler angles (0, 180, 0), with the arms straight out in the T-pose, which is the zero of all shoulder and elbow angles. The eight streamed landmark points of one frame are drawn beside the rig."),
(H2, "3.3 The Arm Model"),

(H3, "3.3.1 Kinematic Schematic and Solved Angles"),

(P, "The arm model borrows its shape from robotics. A human arm is described in [42] with seven rotational degrees of freedom, three at the shoulder, one at the elbow, and three at the wrist, the same split as a seven-axis serial manipulator. Figure 3.6 draws the description in two ways: panel (a) shows the seven rotations q1 to q7 on the arm itself, and panel (b) shows the same rotations as a chain of revolute joints in the PUMA convention. The model of this thesis solves the first four. The three wrist rotations cannot be observed from the eight body landmarks, so the chain ends at the wrist as a tracked point."),

(IMG, FIG / "ch3_fig_dof.png", 6.3),
(CAP, "Figure 3.6. The seven-degree-of-freedom description of the human arm and its serial-chain equivalent in the PUMA convention [42]. (a) The seven rotations q1 to q7 drawn on the arm. (b) The same rotations as a chain of revolute joints. The four rotations solved in this thesis are drawn in colour. The grey wrist triple cannot be observed from the landmark set."),

(PM, [T("In the labels of Figure 3.6, the pair "),
      X(sub(r("q"), r("1")) + r(", ") + sub(r("q"), r("2"))),
      T(" is the shoulder swing "),
      X(d(t_("y") + r(", ") + t_("z"))),
      T(". The angle "), X(sub(r("q"), r("3"))),
      T(" is the shoulder twist "), X(t_("t")),
      T(", and "), X(sub(r("q"), r("4"))),
      T(" is the elbow flexion "), X(sub(r("e"), r("y"))),
      T(". Figure 3.7 places these four joints on the body in the same drawing convention. Each solved rotation is drawn as a revolute-joint cylinder whose axis is the rotation axis. The torso is one rigid plate that holds the root frame of Section 3.2. The shoulder at L12 is a cluster of three revolute joints with one shared centre, the way a manipulator diagram splits a spherical joint. A single hinge sits at the elbow L14, and the chain ends at the wrist L16 with no joint drawn there.")]),

(IMG, FIG / "ch3_fig_schematic.png", 6.3),
(CAP, "Figure 3.7. The kinematic schematic of the modelled right arm, drawn as a serial chain of revolute-joint cylinders in the PUMA style. The dash-dot line through each cylinder is its rotation axis. Every solved angle is labelled. The shoulder swing pair is the azimuth about y and the elevation about z. The elevation is drawn as a disc because its axis points out of the page. The shoulder twist turns about the upper-arm axis, and the elbow flexion completes the set. The straight-arm zero of the elbow is drawn dotted."),

(PM, [T("The rest of this chapter solves for these four labelled angles, and the labels stay the same from here on. The swing azimuth "),
      X(t_("y")), T(" turns the arm about the y axis of the torso, and the swing elevation "),
      X(t_("z")), T(" raises it about the z axis. The twist "),
      X(t_("t")), T(" rolls the upper arm about its own length, and the elbow flexion "),
      X(sub(r("e"), r("y"))),
      T(" bends the forearm relative to the upper arm.")]),

(H3, "3.3.2 Definition of Shoulder, Elbow, and Wrist"),

(P, "With the root in place, the model extends along each arm as a chain of two rigid segments. The right arm uses the right shoulder L12, the right elbow L14, and the right wrist L16, and the left arm uses L11, L13, and L15. The upper arm runs from the shoulder to the elbow and the forearm from the elbow to the wrist. Figure 3.8 shows the four segments drawn on the image of the worked-example frame."),

(IMG, FIG / "ch3_fig_arm_photo.png", 6.0),
(CAP, "Figure 3.8. The four arm segments of the worked-example frame drawn on the image. The upper arm L12 to L14 and the forearm L14 to L16 are on the subject's right, which is the left side of the image. The segments L11 to L13 and L13 to L15 are on the subject's left."),

(P, "The joints hold different information, as the schematic of Figure 3.7 shows. At the shoulder, two rotations aim the upper arm and a third rolls it about its length, the elbow mainly adds flexion, and Section 3.4.4 covers the role of the wrist."),

(H3, "3.3.3 Establishing Local Arm Frames"),

(P, "Every joint rotation in the chain is measured relative to its parent frame: the shoulder relative to the torso, and the elbow relative to the rotated upper arm. That is what makes the angles useful for driving an avatar, because an elbow angle then describes how far the forearm bends relative to the upper arm and not relative to the room."),

(PM, [T("The parent frame of the shoulder has the same orientation as the torso frame, and its origin sits at the shoulder landmark L12. The L12 frame is the root orientation "),
      X(Rroot),
      T(" moved up the trunk. No separate orientation is derived at the shoulder, because three torso landmarks define one rigid orientation. A second basis at the shoulder, built for example from the shoulder line and the upper arm, would add a shoulder-girdle degree of freedom that the data cannot support. With the shoulder angles at zero, the right upper arm points along the +x axis of the frame, straight out to the subject's right.")]),

(PM, [T("In the chain of Section 3.1, this fills in the second transformation of equation (3.5), the pose of the shoulder frame with respect to the root:")]),

(EQ, Tsh + r(" = ") + blockT(r("I"), RrootT + d(p12 + r(" − ") + p24)), "3.13"),

(PM, [T("The rotation block is the identity, and the origin "),
      X(RrootT + d(p12 + r(" − ") + p24)),
      T(" is the measured shoulder landmark expressed with respect to the torso, from the mapping of equation (3.4) applied to "),
      X(p12),
      T(" with the rotation and origin of the root.")]),

(P, "The parent of the elbow is the upper arm itself, so the elbow frame is the fully rotated arm frame: the root orientation composed with the solved shoulder rotation, with its origin at the elbow landmark L14. The PUMA robot model uses the same device, where several wrist frames share one origin and each new frame is the previous one turned by the joint rotation [42]. In the rest configuration the forearm continues the arm axis along the local +x of the elbow frame, so a straight arm is the zero of elbow flexion. The pose of the elbow frame with respect to the shoulder frame is the third transformation of equation (3.5),"),

(EQ, Tel + r(" = ") + blockT(Rsh, RrootT + d(p14 + r(" − ") + p12)), "3.14"),

(PM, [T("with the solved shoulder rotation "), X(Rsh),
      T(" of Section 3.4.2 in the rotation block. The origin is the elbow landmark expressed in the coordinates of the shoulder frame. The shoulder frame shares the orientation of the root, so the same "),
      X(RrootT),
      T(" maps it.")]),

(PM, [T("Expressing a measured segment in its parent frame always takes the same two steps. The segment is first formed as a vector between two landmarks, which for the right upper arm is "),
      X(r("v") + r(" = ") + p14 + r(" − ") + p12),
      T(". The vector is then pulled into the parent frame by equation (3.3), which gives "),
      X(sub(r("v"), nor("local")) + r(" = ") + RrootT + r(" ") + r("v")),
      T(". Each component of the local vector is the dot product of "),
      X(r("v")),
      T(" with one torso axis, so the operation describes the arm in the directions of the body itself. It says how much of the segment points to the subject's right, how much up, and how much forward. The joint angles come from this local vector: it says where the arm points, and Section 3.4 works backwards to the angles that put it there.")]),
(H2, "3.4 Joint Angle Computation"),

(P, "The angles sent to the reconstruction follow the Euler convention of the Unity animation system, which Chapter 6 describes. A bone has three Euler angles, and Unity applies them in a fixed order about the axes of the parent frame: z first, then x, then y. As a matrix product on column vectors, the rotation applied first sits nearest the vector, so the convention reads"),

(EQ, r("R") + r(" = ") + Rot("y", r("y")) + r(" ") + Rot("x", r("x")) + r(" ") + Rot("z", r("z")), "3.15"),
(PM, [T("where "), X(sub(r("R"), r("x"))), T(", "), X(sub(r("R"), r("y"))), T(", "), X(sub(r("R"), r("z"))),
      T(" are the elementary rotations about the coordinate axes. Figure 3.9 shows the order one elementary rotation at a time. The product is multiplied out in symbols in two stages, with c for cosine and s for sine. The inner pair combines first: each row of "),
      X(sub(r("R"), r("x")) + d(r("x"))),
      T(" multiplies each column of "),
      X(sub(r("R"), r("z")) + d(r("z"))),
      T(", and because the x rotation leaves the first row untouched, the first row of the product is the first row of the z rotation:")]),
(MATH, sub(r("R"), r("x")) + d(r("x")) + r(" ") + sub(r("R"), r("z")) + d(r("z")) + r(" = ") + mat([
    [cs("c","z"), r("−")+cs("s","z"), r("0")],
    [cs("c","x")+cs("s","z"), cs("c","x")+cs("c","z"), r("−")+cs("s","x")],
    [cs("s","x")+cs("s","z"), cs("s","x")+cs("c","z"), cs("c","x")]])),
(PM, [T("The next step multiplies this matrix by "),
      X(sub(r("R"), r("y")) + d(r("y"))),
      T(" on the left. The y rotation mixes the first and third rows and leaves the second row unchanged, and the result is the full matrix used throughout this section:")]),
(EQ, r("R") + r(" = ") + mat([
    [cs("c","y")+cs("c","z")+r(" + ")+cs("s","y")+cs("s","x")+cs("s","z"),
     r("−")+cs("c","y")+cs("s","z")+r(" + ")+cs("s","y")+cs("s","x")+cs("c","z"),
     cs("s","y")+cs("c","x")],
    [cs("c","x")+cs("s","z"), cs("c","x")+cs("c","z"), r("−")+cs("s","x")],
    [r("−")+cs("s","y")+cs("c","z")+r(" + ")+cs("c","y")+cs("s","x")+cs("s","z"),
     cs("s","y")+cs("s","z")+r(" + ")+cs("c","y")+cs("s","x")+cs("c","z"),
     cs("c","y")+cs("c","x")]]), "3.16"),

(IMG, FIG / "ch3_fig_zxy_order.png", 6.3),
(CAP, "Figure 3.9. The Euler convention built one elementary rotation at a time. The chain starts from the identity. The z angle is applied first, then x, then y, all about the parent axes. The result is R = Ry Rx Rz."),

(PM, [T("The structure of this matrix lets the angles be read back. Write "),
      X(sub(r("m"), r("ij"))),
      T(" for the entry of a measured numerical matrix "), X(r("m")),
      T(" in row i and column j. The entry "), X(sub(r("m"), r("23"))),
      T(" equals "), X(r("−") + cs("s", "x")),
      T(", which isolates the x angle. The third column of the matrix is "),
      X(d(cs("s","y")+cs("c","x") + r(", −") + cs("s","x") + r(", ") + cs("c","y")+cs("c","x"))),
      T(", and its first and third entries share the factor "), X(cs("c","x")),
      T(", which cancels in the two-argument arctangent and leaves the y angle. The first two entries of the second row share the same factor, which leaves the z angle in the same way:")]),
(EQ, r("x") + r("=") + nor("asin") + d(r("−")+sub(r("m"),r("23"))) + r(", ") +
     r("y") + r("=") + nor("atan2") + d(sub(r("m"),r("13"))+r(",")+sub(r("m"),r("33"))) + r(", ") +
     r("z") + r("=") + nor("atan2") + d(sub(r("m"),r("21"))+r(",")+sub(r("m"),r("22"))), "3.17"),
(PM, [T("The two-argument arctangent looks at the signs of both arguments, so it returns the angle in the correct quadrant over the full circle, where a plain arctangent covers only half of it. The arcsine restricts x to the range -90 to +90 degrees. When x reaches either end of that range ("),
      X(d(sub(r("m"), r("23")), "|", "|") + r(" = 1")),
      T("), the y and z rotations turn about the same effective axis, only their combined angle is defined, and the configuration is called gimbal lock. By convention the z angle is set to zero there and the y angle takes the whole combined rotation. The pose itself is still represented without ambiguity, and only the split of the combined rotation between the two angles is a choice.")]),

(H3, "3.4.1 Torso Pose"),

(PM, [T("The torso is not a joint, so it needs no solving. Its pose is the pair "),
      X(Rroot + r(", ") + p24),
      T(". Equation (3.17) applied to "), X(Rroot),
      T(" gives the three angles of the torso. The worked example of Section 3.5 does this on measured data.")]),


(H3, "3.4.2 Shoulder Orientation"),

(PM, [T("A shoulder pose must describe both the direction of the upper arm and its roll about its own axis, the three angles labelled at the shoulder of the schematic in Figure 3.7. They separate into swing and twist [44], with the twist innermost in the three-factor rotation:")]),
(EQ, Rsh + r(" = ") + Rot("y", t_("y")) + r(" ") + Rot("z", t_("z")) + r(" ") + Rot("x", t_("t")), "3.18"),
(PM, [T("where "), X(t_("y")), T(" and "), X(t_("z")),
      T(" are the swing angles and "), X(t_("t")),
      T(" is the twist about the arm axis +x of the rest configuration. The order is forced by one observation: a rotation about x leaves the x axis itself fixed, so with the twist innermost, applying "),
      X(Rsh), T(" to the rest direction of the arm "), X(xhat),
      T(" removes the twist factor at once,")]),
(EQ, ahat + r(" = ") + Rsh + r(" ") + xhat + r(" = ") +
     Rot("y", t_("y")) + r(" ") + Rot("z", t_("z")) + r(" ") + xhat + r(" = ") +
     d(cs("c","y")+cs("c","z") + r(",  ") + cs("s","z") + r(",  −") + cs("s","y")+cs("c","z")), "3.19"),
(P, "so the upper-arm direction depends on the swing alone, and the twist is exactly the roll about the arm that the elbow position cannot see. If the twist were outermost instead, the twist axis would leave the arm axis as soon as the arm swings, and the decomposition would lose its physical meaning. This has two consequences. The twist is invisible in the shoulder-to-elbow vector, so it must be measured from a second segment, the forearm. And this joint order is not an Euler order. The rig therefore cannot take the three angles as Euler angles, and Chapter 6 rebuilds the rotation from them as three factors in this order. Figure 3.10 shows both halves of the decomposition."),

(IMG, FIG / "ch3_fig_swing_twist.png", 6.3),
(CAP, "Figure 3.10. The swing-twist decomposition. (a) The swing aims the rest direction +x of the arm into the observed direction â. The direction drawn is the measured arm direction of the worked-example frame. (b) The twist rolls about the arm axis. It is measured in the plane perpendicular to that axis, after the swing has been undone."),

(PM, [T("The swing angles come straight from the components of "), X(ahat),
      T(". Its y component is "), X(cs("s", "z")), T(", so")]),
(EQ, t_("z") + r(" = ") + nor("asin") + d(sub(r("a"),r("y"))), "3.20"),
(PM, [T("the elevation of the arm, positive upward and restricted to -90 to +90 degrees. The x and z components share the factor "),
      X(cs("c", "z")), T(", which cancels in the two-argument arctangent:")]),
(EQ, t_("y") + r(" = ") + nor("atan2") + d(r("−")+sub(r("a"),r("z"))+r(", ")+sub(r("a"),r("x"))), "3.21"),
(PM, [T("the azimuth of the arm, positive when sweeping backward. Every direction of the arm is reached by some pair of swing angles, so there is no coverage gap. The one degenerate configuration is the arm pointing straight up or straight down ("),
      X(t_("z") + r(" = ±90°")),
      T("), where the x and z components both vanish and the azimuth is undefined. The convention "),
      X(t_("y") + r(" = 0")),
      T(" is applied there, and any axial rotation then folds into the twist on its own.")]),

(P, "Solving the twist means measuring the rotation about the arm axis. A rotation about an axis is only visible in the plane perpendicular to that axis, so the procedure undoes the swing first, which brings the arm axis back onto +x and makes the perpendicular plane exactly the local y-z plane:"),
(EQ, r("f′") + r(" = ") + Rot("z", r("−")+t_("z")) + r(" ") + Rot("y", r("−")+t_("y")) + r(" ") + r("f"), "3.22"),
(PM, [T("where "), X(r("f")),
      T(" is the forearm vector in the parent frame from Section 3.3.3. The zero convention follows the anatomy: at zero twist, the perpendicular component of the forearm points along local +z, so the elbow flexes forward. Under a twist "),
      X(t_("t")), T(", that component rotates to "),
      X(d(r("−") + nor("sin ") + t_("t") + r(", ") + nor("cos ") + t_("t"))),
      T(" in the (y, z) plane. The twist therefore reads")]),
(EQ, t_("t") + r(" = ") + nor("atan2") + d(r("−")+sub(r("f′"),r("y"))+r(", ")+sub(r("f′"),r("z"))), "3.23"),
(P, "positive for internal rotation, where the forearm rotates downward from forward."),

(PM, [T("The left arm needs no new derivation, because left angles are defined through the sagittal mirror. Both left segment vectors are expressed in the root basis, their x components are flipped with "),
      X(r("M") + r(" = ") + nor("diag") + d(r("−1, 1, 1"))),
      T(", and the same right-arm solver runs on the result. The mirror preserves the whole construction, so every property above holds unchanged, and a mirror-symmetric pose gives identical angle values on both sides with the same anatomical meaning. Positive "),
      X(t_("y")), T(" sweeps backward, positive "), X(t_("z")),
      T(" raises the arm, and positive "), X(t_("t")), T(" rotates internally.")]),

(H3, "3.4.3 Elbow Flexion and Extension"),

(PM, [T("The elbow is solved in the elbow frame of Section 3.3.3, at the landmark L14, whose rotation is "),
      X(Rarm + r(" = ") + Rroot + Rot("y", t_("y")) + Rot("z", t_("z")) + Rot("x", t_("t"))),
      T(", in which the forearm of the rest configuration continues the arm axis along +x. The forearm direction in this frame is "),
      X(ghat + r(" = ") + sup(Rarm, r("T")) + d(p16 + r(" − ") + p14)),
      T(", normalized, and its swing is read the same way as at the shoulder, as an elevation and an azimuth:")]),
(EQ, sub(r("e"),r("z")) + r(" = ") + nor("asin") + d(sub(r("g"),r("y"))) + r(",      ") +
     sub(r("e"),r("y")) + r(" = ") + nor("atan2") + d(r("−")+sub(r("g"),r("z"))+r(", ")+sub(r("g"),r("x"))), "3.24"),
(PM, [T("Here "), X(sub(r("e"), r("y")) + r(" = 0")), T(" is a straight arm and "),
      X(sub(r("e"), r("y")) + r(" = −90")), T(" is a right angle bend. This is the angle labelled at the elbow hinge of the schematic in Figure 3.7.")]),

(PM, [T("A structural fact makes the angles easier to extract: the angle "), X(sub(r("e"), r("z"))),
      T(" is always zero. The shoulder twist was defined as the rotation that aligns the perpendicular component of the forearm with local +z. By the time the elbow is solved, the flexion plane has therefore already been turned into the x-z plane of the elbow frame. The out-of-plane freedom of the elbow is the shoulder twist, solved one joint earlier. This closes the dimension count: the two measured segment directions give four observable degrees of freedom, and the model extracts four independent angles. The angle "),
      X(sub(r("e"), r("z"))),
      T(" stays in the streamed angle set for generality, but it holds no independent information.")]),

(PM, [T("The elbow also shows the one case where a three-landmark arm breaks down. When the arm is straight, the forearm is parallel to the upper arm, its perpendicular component vanishes, and the shoulder twist can no longer be observed. No algebra can recover a roll about an axis from two collinear segments. The solver detects this condition by a threshold on the perpendicular fraction of the forearm, applies the convention "),
      X(t_("t") + r(" = 0")),
      T(" so that the elbow frame stays defined, and flags the twist as unobservable. Later stages then hold the last valid value instead of trusting a numerical accident. A nearly straight elbow leaves the flexion angle well conditioned but makes the twist sensitive to noise, and Chapter 9 discusses this as a practical limitation.")]),

(H3, "3.4.4 The Wrist as a Tracked Point"),

(P, "The wrist is not a solved joint of this model. The wrist L16 enters as a tracked 3D point, as the schematic of Figure 3.7 draws it. That point does two jobs for the solver: it defines the forearm direction that the elbow flexion is read from, and it supplies the second segment that makes the shoulder twist observable."),

(P, "The model does not resolve a full three-degree-of-freedom wrist orientation, because that would need a landmark beyond the wrist. Forearm pronation, the roll of the forearm about its own axis, produces no motion of the wrist point at all, so no algebra over these landmarks can observe it. The tracked wrist position is still kept and transmitted, because it places the end point of each arm in the reconstructed scene. It is also the anchor that the pose recovery of Chapter 5 restores from the object pose when the landmark is lost during a grip. A hand model would attach at the same point. The hierarchical hand model of [41] solves finger joints from dedicated hand landmarks and could later extend the chain there without changing the arm solver."),
(H2, "3.5 Worked Example"),

(P, "A single measured frame now carries the whole chain from the raw landmark positions to the full angle set. The frame is taken part way through the task of Chapter 2, while the cube slides along the rail, and it is the frame shown in Figures 3.4 and 3.8. The subject stands at the desk with the right hand on the cube and the left arm at the side. The example uses this frame because all eight landmarks are measured on it: none was flagged by the despiking stage or filled by the gap-bridging stage of Section 2.5, and no failure detector of Chapter 5 fires on it. Each solved value below points back at its label in the schematic of Figure 3.7. Throughout, the values are computed from the unrounded landmark positions and printed rounded to two decimals, so a step recomputed by hand from the rounded inputs can differ from the printed result in the last digit."),

(P, "Table 3.1 lists the eight landmark positions in both coordinate frames. They are the positions after the filtering of Section 2.5, because the solver consumes the filtered stream. The same frame runs through the worked examples of Appendix C, Appendix D and Appendix E, where the landmark, depth and marker readings behind these positions can be followed."),

(TBL, [["Landmark", "Camera frame C (m)", "Person space P (m)"],
       ["L11 left shoulder", "(0.22, -0.34, 1.36)", "(0.22, 0.34, 1.36)"],
       ["L12 right shoulder", "(-0.16, -0.33, 1.31)", "(-0.16, 0.33, 1.31)"],
       ["L13 left elbow", "(0.28, -0.03, 1.38)", "(0.28, 0.03, 1.38)"],
       ["L14 right elbow", "(-0.20, -0.04, 1.19)", "(-0.20, 0.04, 1.19)"],
       ["L15 left wrist", "(0.24, 0.20, 1.25)", "(0.24, -0.20, 1.25)"],
       ["L16 right wrist", "(-0.20, 0.11, 1.06)", "(-0.20, -0.11, 1.06)"],
       ["L23 left hip", "(0.12, 0.18, 0.99)", "(0.12, -0.18, 0.99)"],
       ["L24 right hip", "(-0.06, 0.19, 0.99)", "(-0.06, -0.19, 0.99)"]]),
(CAP, "Table 3.1. The eight landmarks of the worked-example frame in the camera frame and in person space, printed to two decimals. The conversion flips only the sign of y. The hips have negative person-space y because they sit below the camera height. Their depth is the depth of the rail in front of them (see the torso angles below)."),

(P, "The torso construction of Section 3.2 needs three of these points, in person space:"),
(MATH, eqArr(
    p23 + r(" = (0.12, −0.18, 0.99)"),
    p24 + r(" = (−0.06, −0.19, 0.99)"),
    p12 + r(" = (−0.16, 0.33, 1.31)"))),

(P, "Following equation (3.7), the hip line is the difference of the two hip positions,"),
(MATH, p24 + r(" − ") + p23 + r(" = (−0.18, −0.01, −0.01)")),
(P, "with length 0.18 m. Dividing by the length:"),
(MATH, xhat + r(" = (−1.00, −0.05, −0.04)")),
(P, "The x component is close to -1, because the subject's right side points toward the camera's left. The spine-side vector of equation (3.8) is"),
(MATH, r("s") + r(" = ") + p12 + r(" − ") + p24 + r(" = (−0.11, 0.53, 0.33)")),
(P, "with length 0.63 m. Its upward y component dominates, and it also has a z component of 0.33 because the shoulder is measured farther from the camera than the hip. The cross product of equation (3.9) follows, each component written out and printed rounded:"),
(MATH, eqArr(
    d(xhat + r(" × ") + r("s"), "(", ")") + sub(r(""), r("x")) + r(" = (−0.05) · 0.33 − (−0.04) · 0.53 = 0.00"),
    d(xhat + r(" × ") + r("s"), "(", ")") + sub(r(""), r("y")) + r(" = (−0.04) · (−0.11) − (−1.00) · 0.33 = 0.33"),
    d(xhat + r(" × ") + r("s"), "(", ")") + sub(r(""), r("z")) + r(" = (−1.00) · 0.53 − (−0.05) · (−0.11) = −0.53"))),
(P, "with length 0.63 m. Normalizing gives"),
(MATH, zhat + r(" = (0.01, 0.53, −0.85)")),
(P, "a direction toward the camera, with negative z, tipped upward by the same hip-to-shoulder depth difference, so the chest faces the camera. The second cross product, equation (3.10), closes the frame:"),
(MATH, yhat + r(" = ") + zhat + r(" × ") + xhat + r(" = (−0.06, 0.85, 0.53)")),
(P, "a unit vector that needs no normalization. Equation (3.11) assembles the columns:"),
(MATH, Rroot + r(" = ") + mat([
    [r("−1.00"), r("−0.06"), r("0.01")],
    [r("−0.05"), r("0.85"), r("0.53")],
    [r("−0.04"), r("0.53"), r("−0.85")]])),
(PM, [T("Appending the origin "), X(p24),
      T(" gives the first of the three transformations of equation (3.5) as numbers, the root pose of equation (3.12):")]),
(MATH, Troot + r(" = ") + mat([
    [r("−1.00"), r("−0.06"), r("0.01"), r("−0.06")],
    [r("−0.05"), r("0.85"), r("0.53"), r("−0.19")],
    [r("−0.04"), r("0.53"), r("−0.85"), r("0.99")],
    [r("0"), r("0"), r("0"), r("1")]])),
(P, "The upper-left block is the rotation just assembled and the last column is the right hip position, so one matrix now says where the torso sits in person space and how it is turned. The shoulder transformation with respect to the root, equation (3.13), needs the shoulder landmark in the torso's own coordinates, which the point mapping of equation (3.4) gives:"),
(MATH, RrootT + d(p12 + r(" − ") + p24) + r(" = (0.07, 0.63, 0.00)")),
(P, "The spine-side vector lies in the torso plane by construction, so the third component is an exact zero. In the torso's own coordinates the shoulder sits straight up and slightly to the right of the hip, with no forward offset. The transformation is"),
(MATH, Tsh + r(" = ") + mat([
    [r("1"), r("0"), r("0"), r("0.07")],
    [r("0"), r("1"), r("0"), r("0.63")],
    [r("0"), r("0"), r("1"), r("0.00")],
    [r("0"), r("0"), r("0"), r("1")]])),
(P, "an identity rotation with a pure origin shift, as equation (3.13) prescribes. Equation (3.17) decodes the root matrix by reading one entry or one entry pair per angle. The entry in row 2, column 3 gives the x angle, the third column gives y, and the second row gives z:"),
(MATH, eqArr(
    r("x") + r(" = ") + nor("asin") + d(r("−0.53")) + r(" = −32.08°"),
    r("y") + r(" = ") + nor("atan2") + d(r("0.01, −0.85")) + r(" = 179.49°"),
    r("z") + r(" = ") + nor("atan2") + d(r("−0.05, 0.85")) + r(" = −3.26°"))),
(P, "Compared with the reference configuration (0, 180, 0), the subject faces almost straight at the sensor and the hip line is almost level. The frame is pitched by 32.08 degrees because the hips sit nearer the camera than the shoulders. The photograph in Figure 3.4 shows an upright trunk, so the pitch comes from the hip measurement. The two hip landmarks fall on the pixels where the pelvis meets the rail, and the depth sampled there is the depth of the rail. Table 3.1 shows 0.99 metres against 1.31 and 1.36 metres at the two shoulders. The root frame inherits that offset, and the arm angles below are read against this pitched frame. Chapter 5 describes this kind of failure, where a correct pixel sits over a depth sample taken on the surface in front of the body. Its torso repair puts the hips back on their own camera rays at a remembered trunk depth, and Chapter 7 reports the repaired root, while this chapter works on the measurement as it stands. These three values are the torso pose of Section 3.4.1."),

(P, "The right arm continues from the same frame. The person-space upper arm vector is"),
(MATH, r("v") + r(" = ") + p14 + r(" − ") + p12 + r(" = (−0.04, −0.29, −0.12)")),
(P, "with length 0.32 m, about the length of an upper arm. Equation (3.3) pulls the vector into the parent frame, and each component becomes a dot product with one column of the root matrix:"),
(MATH, sub(r("v"), nor("local")) + r(" = ") + RrootT + r(" ") + r("v") + r(" = (0.05, −0.31, −0.05)")),
(P, "The vector now reads anatomically: the upper arm points slightly across the body, since +x is the subject's right, strongly downward with negative y, and slightly behind the pitched torso plane with negative z. That is the visible pose in Figure 3.8, with the right arm reaching down to the cube on the rail. Equation (3.3) applies a rotation, so the length 0.32 is unchanged, and dividing by that length gives the local arm direction:"),
(MATH, ahat + r(" = (0.17, −0.97, −0.16)")),
(P, "The same two steps on the forearm give the forearm vector in the parent frame,"),
(MATH, r("f") + r(" = ") + RrootT + d(p16 + r(" − ") + p14) + r(" = (0.01, −0.20, 0.03)")),
(P, "with length 0.20 m. These two local vectors are the complete input to the right-arm angle computation, and nothing else about the pose is needed."),

(PM, [T("Equations (3.20) and (3.21) read the two swing angles (Figure 3.7):")]),
(MATH, eqArr(
    t_("z") + r(" = ") + nor("asin") + d(r("−0.97")) + r(" = −76.57°"),
    t_("y") + r(" = ") + nor("atan2") + d(r("0.16, 0.17")) + r(" = 43.03°"))),
(P, "The arm points 76.57 degrees below horizontal, and its small remaining horizontal component is swept toward the subject's back. Equation (3.22) undoes this swing on the forearm vector and gives"),
(MATH, r("f′") + r(" = ") + Rot("z", r("76.57°")) + r(" ") + Rot("y", r("−43.03°")) + r(" ") + r("f") + r(" = (0.19, −0.06, 0.03)")),
(PM, [T("Its perpendicular part points mostly along negative y (Figure 3.7). Equation (3.23) gives the twist:")]),
(MATH, t_("t") + r(" = ") + nor("atan2") + d(r("0.06, 0.03")) + r(" = 59.92°")),
(P, "This is an internal rotation: the forearm turns inward across the front of the body, so the hand rests on the cube in front of the trunk. In the elbow frame the forearm direction is"),
(MATH, ghat + r(" = (0.94, 0.00, 0.34)")),
(PM, [T("Its y component is zero, which is the "),
      X(sub(r("e"), r("z")) + r(" = 0")),
      T(" property of Section 3.4.3 holding on the measured frame. The flexion of equation (3.24), the hinge angle of Figure 3.7, is")]),
(MATH, sub(r("e"), r("y")) + r(" = ") + nor("atan2") + d(r("−0.34, 0.94")) + r(" = −19.81°")),
(PM, [T("This is a gentle bend. The solved shoulder rotation and the local upper-arm vector "),
      X(sub(r("v"), nor("local"))),
      T(" computed above also complete the last transformation of equation (3.5) as numbers, the elbow pose of equation (3.14):")]),
(MATH, Tel + r(" = ") + mat([
    [r("0.17"), r("0.95"), r("−0.27"), r("0.05")],
    [r("−0.97"), r("0.12"), r("−0.20"), r("−0.31")],
    [r("−0.16"), r("0.30"), r("0.94"), r("−0.05")],
    [r("0"), r("0"), r("0"), r("1")]])),
(PM, [T("Its rotation block is the composed swing and twist just solved, its first column is exactly "),
      X(ahat),
      T(", the local arm direction, and its last column is the elbow position in the shoulder frame. The numeric chain closes with two checks. In the first, the three matrices are composed as in equation (3.6) and the product is applied to the origin. The result lands on (-0.20, 0.04, 1.19), the measured elbow position of Table 3.1, to machine precision, so the relative transformations rebuild the measured chain. In the second, the measured wrist is carried through the inverse chain into the elbow frame by three applications of equation (3.4). The result is (0.19, 0.00, 0.07), its length is the forearm length 0.20, and its zero second component is the "),
      X(sub(r("e"), r("z")) + r(" = 0")),
      T(" property again. Dividing by the length reproduces the "),
      X(ghat),
      T(" used for the flexion.")]),
(P, "The left arm runs through the same mirrored solver and gives a shoulder azimuth of 76.07 degrees, an elevation of -53.52 degrees, a twist of 108.86 degrees, and an elbow flexion of -37.34 degrees. This is the arm hanging at the side in Figure 3.8, read against the same pitched root frame and bent more than the right. The whole measured pose of this frame is now described by thirteen numbers: the three root Euler angles, then swing, twist and flexion for each arm, with the zero elbow angle kept for generality."),

(P, "The same equations run on every frame of a recording and on both arms. Chapter 7 evaluates the accuracy of the angles the model produces."),
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
            for j, c in enumerate(row_):
                cell = t.cell(i, j)
                cell.text = c
                for par in cell.paragraphs:
                    for run in par.runs:
                        run.font.size = Pt(10)
                        if i == 0:
                            run.font.bold = True

out = REPO / "writing" / "v8" / "Chapter_3_Kinematic_Modeling.docx"
doc.save(out)
print("saved", out, "| items:", len(content))

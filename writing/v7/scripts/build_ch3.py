#!/usr/bin/env python3
"""Build writing/v7/Chapter_3_Kinematic_Modeling.docx (V7 rewrite round).

Chapter 3 against the V7 TOC: 3.1 Coordinate Systems and Transformations
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
Figures: writing/v7/figures/ (regenerated from the same frame; see
make_ch3_figs.py, make_ch3_chain_fig.py, make_ch3_fig2.py).
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches

from eqn import r, nor, sub, sup, hat, frac, mat, d, eqArr, \
    add_display_eq, add_display_math, add_inline_math

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v7" / "figures"

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

(P, "The previous chapter ended with eight body landmarks per frame, each lifted to a metric 3D position in the camera frame; Appendix C lists that landmark set and how it is read out of the detector, and Appendix D sets out the lifting itself. Those positions are labelled and arrive in a fixed order, but on their own they say nothing about how the body segments are oriented relative to one another, or about how each joint has rotated between one frame and the next. This chapter introduces the kinematic model that gives the points that meaning. The model is organized as a hierarchical chain of coordinate frames, rooted at the pelvis and extending outward through the shoulder and elbow of each arm, following the hierarchical modeling principle established for the hand by [41]. Once the chain is built, the pose of the body reduces to the orientation and position of the torso plus a small set of anatomical joint angles: a swing and twist for each shoulder, and a flexion angle for each elbow. Chapter 6 maps those angles onto the Unity avatar."),

(P, "The model developed here has three distinguishing properties. First, it is closed form: every angle is computed directly from the landmark geometry of the current frame, with no optimization and no temporal state. Second, it is invertible: composing the solved angles rebuilds the rotation they were read from, so the angle set describes the measured pose completely rather than approximating it. Third, one construction serves both arms. The left arm is solved by the right-arm equations applied to mirrored segment vectors. The chapter proceeds in the order of the chain itself: the mathematical tools first, then the torso root frame, then the arm model, then the joint angles. A worked example on one measured frame closes the chapter."),

(P, "Figure 3.1 draws the information flow of the whole chapter before any construction begins. The calibrated landmarks of Chapter 2 enter on the left, each box names the section that builds its contents, and the thirteen angles per frame leave on the right for the avatar of Chapter 6. The transformations written on the arrows are defined in Section 3.1, which also states, once, the logic they carry."),

(IMG, FIG / "ch3_fig_flow.png", 6.3),
(CAP, "Figure 3.1. The information flow of this chapter. Landmarks enter from the sensing stage of Chapter 2 (left). The torso landmarks establish the root frame and its transformation with respect to person space, and each arm landmark is then carried through the relative transformations into the frame where its joint is solved. The output is the thirteen-angle pose of one frame (right). Section numbers in the boxes locate each construction."),

(H2, "3.1 Coordinate Systems and Transformations"),

(P, "A coordinate frame is an origin point together with three mutually perpendicular unit vectors, labelled x, y, and z, that define the directions of the three axes. Any point in space is described by how far one must travel along each axis direction, starting from the origin, to reach it. The entire kinematic model is built from such frames: one is attached to each body segment. When a segment moves, its frame moves with it. The orientation of one segment relative to another is then captured entirely by the relationship between their two frames. Being precise about which frame a number lives in is the main bookkeeping rule of this chapter, so the two frames at the two ends of the system are defined first."),

(P, "Chapter 2 reports every sensing-stage measurement in RealSense camera coordinates, denoted C. This right-handed frame points x to image right, y downward, and z forward into the scene, defined from the perspective of a person standing behind the camera looking forward [10]. A point's z coordinate is its measured depth. Unity instead uses a left-handed frame with y upward. Figure 3.2 shows the camera frame on the sensor itself and, beside it, two frames of the reconstruction this chapter feeds: the measured root frame of the body and the Unity world frame."),

(IMG, FIG / "ch3_fig_sensor_unity.png", 6.3),
(CAP, "Figure 3.2. (a) The D435 camera frame C on a front photograph of the sensor (product photograph: Intel). The convention is defined from behind the camera, so on this front view the image-right x axis appears on the reader's left and z comes out of the page toward the reader; the module names mirror the same way, with the left imager on the reader's right. The origin is the colour camera's lens, the frame all measurements use after depth-to-colour alignment. (b) The Unity frame, captured in the Unity editor at the root node of the avatar rig: every scene element except the rig is hidden, the rig's top-most parent is selected, and its coordinate axes are drawn at its origin (x red, y green, z blue). The node is axis-aligned with the Unity world, and the avatar stands in the T-pose, the reference configuration of the model."),

(P, "Panel (b) of Figure 3.2 also fixes a distinction that matters for the whole chapter. The frame shown belongs to the avatar's root node, and it is axis-aligned with the Unity world. The body's measured root frame is a different frame: it rides the torso, and at the worked-example frame its yaw decodes to 179.49 degrees, because the participant faces the sensor (Section 3.5 prints that value). Person space itself is anchored at the camera, while the Unity world is anchored at the desk marker of Chapter 4. Three facts keep the reconstruction correct across these differences. First, every joint angle of this chapter is defined relative to its parent frame. The pose of the body is therefore carried by relative rotations, and no change of global frame can alter it. Second, the reconstruction places the person into the world through the calibrated camera pose, composed once per frame in Chapter 6, so the root lands in the right place without the frames ever being equated. Third, the system's two handedness conversions, the point flip introduced below as equation (3.1) and the axis swap where the object track of Chapter 4 is exported, are both reflections with determinant -1. Their composition through the calibrated pose therefore has determinant +1, and no net mirror reaches the rendered scene."),

(P, "A right-handed and a left-handed frame have opposite orientations, so the handedness itself must change during the conversion, not just the labels of the axes. The conversion used throughout this work is a single matrix multiplication applied to every measured point. If p is a landmark position in the camera frame, its position q in the person space P used by all the kinematic math is"),

(EQ, r("q") + r(" = ") + r("F") + r(" ") + r("p") + r(",        ") + r("F") + r(" = ") + nor("diag") + d(r("1, −1, 1")), "3.1"),

(P, "that is, the y coordinate flips sign and x and z pass through unchanged. Flipping exactly one axis converts a right-handed frame to a left-handed one: the determinant of F is -1, which marks a reflection. After the flip, x still points to the right in the image, y now points up, and z still points away from the camera, matching Unity's convention. Both frames keep the same origin at the optical centre of the camera; only the reading of the y axis changes. The flip applies to points only, never to rotation matrices: every rotation below is built from already flipped points, so every rotation in the pipeline comes out proper. Figure 3.3 shows the two frames drawn from that single shared origin, together with one measured wrist position: the right wrist of the worked-example frame of Section 3.5 reads (-0.20, 0.11, 1.06) in the camera frame and (-0.20, -0.11, 1.06) in person space. The physical point is the same; only one coordinate flips. From this point onward, every landmark position in this chapter is a person-space value unless stated otherwise."),

(IMG, FIG / "ch3_fig_colocated.png", 5.6),
(CAP, "Figure 3.3. The camera frame C and person space P drawn from the same origin, each axis labelled with the frame it belongs to. Only the y axis differs: the camera reads y downward, person space reads y upward. The wrist landmark of the worked-example frame is shown with its coordinates in both frames."),

(P, "No physical result depends on the handedness of a frame, so the left-handed choice is one of convenience. The angles this chapter produces drive the Unity animation system, and the kinematics are computed in the convention their consumer uses. Converting the points is also cheaper than converting the rotations: a point crosses a handedness change with one sign flip, while a rotation crosses by conjugation, with every sign convention changing along the way. Each measured point is therefore flipped once at the entry, and no solved rotation is converted at the exit. Chapter 4 makes the opposite placement for the object track, which stays in the desk-anchored frame its reference geometry lives in and converts only when its poses are exported."),

(P, "The relationship between two coordinate frames consists of two pieces of information: how the child frame is rotated relative to the parent, and where the child's origin sits in the parent's coordinates. Together they form a rigid body transformation, an operation that moves and turns an object without deforming it [42]. The rotation part is a 3 by 3 matrix R whose three columns are the child frame's axis directions written in the parent's coordinates. Because the columns are perpendicular unit vectors, R has a special property. Its transpose equals its inverse, and its determinant equals one. This property is used in what follows, because a vector expressed in the parent frame is brought into the child frame by multiplying with the transpose, and no matrix is ever inverted numerically. The translation part is a 3-vector t giving the position of the child's origin in the parent frame. The two combine into one representation, the 4 by 4 homogeneous transformation matrix T, written with R and t as blocks:"),

(EQ, r("T") + r(" = ") + blockT(r("R"), r("t")) + r(",        ") +
     mat([[sub(r("p"), nor("parent"))], [r("1")]]) + r(" = ") + r("T") + r(" ") +
     mat([[sub(r("p"), nor("child"))], [r("1")]]), "3.2"),

(P, "The bottom row is the constant (0, 0, 0, 1). Appending a 1 to a point turns the rotation and the shift into a single matrix multiplication: written out, the product says that a point known in the child frame is rotated by R and moved by t to give the same point in the parent frame. One matrix therefore carries the complete pose of a frame, and the letter T with a subscript naming the frame is used for these matrices throughout the chapter."),

(P, "The value of this representation appears when transformations chain. If a transformation A describes the torso frame relative to person space and a transformation B describes a shoulder frame relative to the torso, then the product AB describes the shoulder frame directly in person space. Rotations defined locally, each relative to its immediate parent, accumulate into a single description of the whole arm. The same property runs in reverse when the angles are computed: given a measured segment direction v in person space and the known orientation of its parent frame, the segment's direction in the parent frame is"),

(EQ, sub(r("v"), nor("local")) + r(" = ") + sup(sub(r("R"), nor("parent")), r("T")) + r(" ") + r("v"), "3.3"),

(P, "Here v is a direction vector between two landmarks rather than a point. The convention throughout this chapter is that p marks a measured landmark point and v marks a segment vector formed from two points, and directions transform by rotation alone. The scope of equation (3.3) must be stated precisely: it is the rotation part of the transformation acting on its own. It applies to directions, which have no location, and to points only in the special case where the child and the parent frames share one origin. A measured landmark is a point, and the frames of the chain sit at different body locations, so mapping a landmark between frames needs the full T of equation (3.2). Inverting the block form gives the mapping of a point from the parent frame into the child frame:"),

(EQ, sub(r("p"), nor("child")) + r(" = ") + sup(r("R"), r("T")) + r(" ") +
     d(sub(r("p"), nor("parent")) + r(" − ") + r("t")) + r(",        ") +
     sup(r("T"), r("−1")) + r(" = ") +
     blockT(sup(r("R"), r("T")), r("−") + sup(r("R"), r("T")) + r("t")), "3.4"),

(P, "No new algebra is needed for this inverse: the rotation block inverts to its transpose by the property already stated, and the origin offset reverses. Written as operations on the point, the offset is removed first and the transpose rotation then re-describes the point along the child's axes. Every derivation in Section 3.4 uses these two operations: composing transformations forward along the chain, and pulling measured points and vectors backward into local frames. Figure 3.4 draws the chain on the worked-example frame of Section 3.5, a measured frame of the recording of Chapter 2, with the three frames of the right arm chain at their anatomical origins."),

(IMG, FIG / "ch3_fig_chain_photo.png", 6.0),
(CAP, "Figure 3.4. The kinematic chain drawn on the worked-example frame of the recording, front view. The root frame sits at the right hip L24, the shoulder frame at L12, and the elbow frame at L14, with x continuing the upper-arm axis down the arm that holds the cube of the task of Chapter 2."),

(P, "Each neighbouring pair of frames in Figure 3.4 is related by its own homogeneous transformation, and writing the three out makes plain that the frames differ from one another in both their relative rotation and the position of their origin:"),

(EQ, Troot + r(" = ") + blockT(Rroot, sub(r("t"), nor("root"))) + r(",    ") +
     Tsh + r(" = ") + blockT(r("I"), sub(r("t"), nor("sh,r"))) + r(",    ") +
     Tel + r(" = ") + blockT(Rsh, sub(r("t"), nor("el,r"))), "3.5"),

(PM, [T("A notation rule applies from here on: a frame that exists once per arm carries its side in the subscript, r for the participant's right and l for the left, so "),
      X(Tsh), T(" is the right shoulder frame and "), X(Tshl),
      T(" the left. The chapter derives the right arm, and the left-arm transformations follow from the mirror construction of Section 3.4.2. Each transformation carries its own rotation and its own origin. "),
      X(Troot),
      T(" is the pose of the root (torso) frame with respect to person space, built in Section 3.2. "),
      X(Tsh),
      T(" is the pose of the right shoulder frame with respect to the root, with the 3 by 3 identity I for its rotation block. "),
      X(Tel),
      T(" is the pose of the right elbow frame with respect to the shoulder frame, with the solved shoulder rotation "),
      X(Rsh),
      T(" for its rotation block. Section 3.3.3 places both origins, and chaining the three describes the right elbow frame directly in person space,")]),

(EQ, Tarm + r(" = ") + Troot + r(" ") + Tsh + r(" ") + Tel, "3.6"),

(P, "These relative transformations are the plan of the whole chapter, and the logic should be clear before the constructions begin. Every landmark is measured with respect to the sensor and converted to person space by equation (3.1); the relative transformations then carry it into the frame where it is needed. Applying the inverse of the root transformation, by equation (3.4), expresses a measured landmark with respect to the torso: the shoulder landmark, for example, becomes the shoulder position in the root frame, and that position is the shoulder frame's origin offset. The shoulder inverse then puts a point in the shoulder frame, so the elbow landmark can drive the shoulder angles of Section 3.4.2. Applying the elbow inverse last expresses the wrist with respect to the elbow frame, and the elbow flexion of Section 3.4.3 is read there. The sections that follow build each transformation in this order, and Section 3.5 prints all three as numbers on a measured frame."),

(H2, "3.2 Torso Reference Frame"),

(H3, "3.2.1 Landmark Selection"),

(P, "The torso root is defined by three MediaPipe landmarks [43]: right hip L24, left hip L23, and right shoulder L12. Anatomical left and right always refer to the participant; because the participant faces the sensor, the right side appears on the image's left."),

(P, "This choice rests on geometry and visibility. The hip and shoulder points move more slowly than the hands and forearms, and the object rarely hides them. A full orientation requires a plane, for which three non-collinear points are the minimum. These landmarks also form a broad triangle across the trunk, reducing the angular effect of small position errors."),

(P, "A further assumption should be stated before the construction. With only three torso points, the model cannot separate the pelvis from the upper trunk. It therefore assumes that there is no relative twist between the shoulders and the hips: the whole torso is treated as one rigid plate whose orientation the frame captures. A consequence is that a forward lean of the trunk pitches the root frame with it. This simplification is accepted for the present model and is revisited in the limitations of Chapter 9."),

(H3, "3.2.2 Derivation of the Torso Frame"),

(PM, [T("The three landmark positions arrive from Chapter 2 in the camera frame and are converted to person space by the flip F of equation (3.1); the construction below happens entirely in person space. Let "),
      X(p23), T(", "), X(p24), T(", and "), X(p12),
      T(" denote the person-space positions of the left hip, right hip, and right shoulder. This section derives the orientation and location of the torso plane, described as a rotation matrix and an origin. Figure 3.5(a) shows the two input vectors drawn on the real image of the worked-example frame, and Figure 3.5(b) shows the finished frame projected back onto the same image.")]),

(IMG, FIG / "ch3_fig_torso_photo.png", 6.3),
(CAP, "Figure 3.5. The torso frame on the real image of the worked-example frame. (a) The two input vectors: the hip line from L23 to L24 (red) and the spine-side vector s from L24 up to L12 (yellow). (b) The finished orthonormal frame at the L24 origin, projected through the camera intrinsics: x toward the participant's right, y up along the trunk, z forward out of the chest. The y and z axes lean in the image because the measured frame is pitched, as Section 3.5 explains."),

(P, "The x axis is defined first. It is the unit vector along the hip line, pointing toward the participant's right (the hat marks a unit vector):"),
(EQ, xhat + r(" = ") + frac(p24 + r(" − ") + p23,
     d(p24 + r(" − ") + p23, "|", "|")), "3.7"),
(P, "No sign correction is needed: subtracting the left-hip position from the right-hip position already produces a vector that points to the participant's right, which becomes the +x axis of the torso frame being built. This axis is kept exactly as measured, because both of its endpoints are pelvis landmarks; the hip line is the one direction the three points define with no ambiguity."),

(P, "The second input is the spine-side vector from the right hip up to the right shoulder,"),
(EQ, r("s") + r(" = ") + p12 + r(" − ") + p24, "3.8"),
(PM, [T("This vector is not used as an axis. It is generally not perpendicular to the hip line (in the worked-example frame the angle between them is 83.81 degrees, not 90), and treating it as an axis would produce a skewed, non-orthogonal frame. Its only job is to select the torso plane: among all the planes that contain the hip line, the torso plane is the one that also contains "),
      X(r("s")), T(".")]),

(PM, [T("The z axis comes from the cross product. For two vectors "),
      X(r("a")), T(" and "), X(r("b")), T(", the cross product "),
      X(r("a") + r(" × ") + r("b")),
      T(" is perpendicular to both, with components")]),
(MATH, d(cs("a","y")+cs("b","z") + r(" − ") + cs("a","z")+cs("b","y") + r(",   ") +
         cs("a","z")+cs("b","x") + r(" − ") + cs("a","x")+cs("b","z") + r(",   ") +
         cs("a","x")+cs("b","y") + r(" − ") + cs("a","y")+cs("b","x"))),
(P, "Applying it to the two inputs and normalizing:"),
(EQ, zhat + r(" = ") + frac(xhat + r(" × ") + r("s"),
     d(xhat + r(" × ") + r("s"), "|", "|")), "3.9"),
(PM, [T("The ordering of the two factors sets the sign: with "),
      X(xhat), T(" pointing to the participant's right and "), X(r("s")),
      T(" pointing up the trunk, the product points forward, out of the participant's chest toward the camera. Reversing the order would flip the axis into the participant's back. The cross product also discards the part of "),
      X(r("s")), T(" that is parallel to "), X(xhat),
      T(" automatically, so the imperfect angle between the inputs does no harm: only the component of "),
      X(r("s")), T(" perpendicular to the hip line contributes.")]),

(P, "The y axis closes the frame with a second cross product:"),
(EQ, yhat + r(" = ") + zhat + r(" × ") + xhat, "3.10"),
(PM, [T("Because "), X(zhat), T(" and "), X(xhat),
      T(" are already perpendicular unit vectors, this product is exactly a unit vector, with no normalization needed. This third step guarantees an orthonormal frame in every measured pose. The result is the anatomical up direction along the trunk.")]),

(P, "The three axes assemble into the root rotation matrix, whose columns are the frame's axes in the person-space order right, up, forward:"),
(EQ, Rroot + r(" = ") + mat([[xhat, yhat, zhat]]), "3.11"),
(PM, [T("and the right hip position "), X(p24),
      T(" serves as the origin. Together they fill in the first transformation announced in equation (3.5), the pose of the root frame with respect to person space:")]),

(EQ, Troot + r(" = ") + blockT(Rroot, p24), "3.12"),

(P, "Every arm frame in the following sections is expressed relative to this matrix, and its inverse, by equation (3.4), carries any measured landmark into the torso's own coordinates."),

(PM, [T("Figure 3.6 shows the reference configuration that fixes the meaning of the finished matrix. Panel (a) is the participant in the laboratory, standing upright, facing the sensor, arms straight out to the sides, with a frame drawn at every landmark of the model at its zero configuration: the root frame at the right hip and the left hip in the same orientation, the two shoulder frames with the root's orientation, the two elbow frames with x along each upper arm, and the two wrists, the tracked points that end the chain, with x along each forearm. Panel (b) is the avatar of the reconstruction in the same pose. This is the T-pose: the zero of every arm angle in Section 3.3. An ideal upright person facing the sensor has their right side toward the camera's left and their chest toward the negative z of person space. Substituting these ideal directions gives exact values: "),
      X(Rroot), T(" with columns (-1, 0, 0), (0, 1, 0), (0, 0, -1), which decodes to the Euler angles (0, 180, 0) in the convention of Section 3.4: an avatar standing upright, turned 180 degrees to face the viewer. This reference test matters because a proper rotation matrix alone does not pin down a construction. Assembling the same axes with the forward direction placed in the up column still forms a proper rotation matrix, but its reference pose decodes to (90, 0, 0), a rig lying flat on its back. The reference pose check catches that kind of error before it reaches the avatar.")]),

(IMG, FIG / "ch3_fig_tpose.png", 6.3),
(CAP, "Figure 3.6. The reference configuration. (a) The participant in the T-pose in the laboratory, with the RGB-D camera on its mount at the desk edge, the desk with the rail, and the wall marker behind. A frame is drawn at each of the eight landmarks the detector finds on this photograph, at its zero configuration: x red, y green, z blue, with z drawn foreshortened toward the viewer. (b) The Unity avatar upright and facing the viewer at root Euler angles (0, 180, 0), arms straight out in the T-pose, the zero of all shoulder and elbow angles; the eight streamed landmark points of one frame are drawn beside the rig."),

(H2, "3.3 The Arm Model"),

(H3, "3.3.1 Kinematic Schematic and Solved Angles"),

(P, "The arm model borrows its shape from robotics. A human arm is conventionally described with seven rotational degrees of freedom: three at the shoulder, one at the elbow, and three at the wrist, the same decomposition used for seven-axis serial manipulators in the robotics literature [42]. Figure 3.7 draws the description both ways: the seven rotations q1 to q7 on the arm itself, and the equivalent chain of revolute joints in the PUMA convention. The model of this thesis solves the first four. The wrist triple is not observable from the eight body landmarks, so the chain ends at the wrist as a tracked point."),

(IMG, FIG / "ch3_fig_dof.png", 6.3),
(CAP, "Figure 3.7. The seven-degree-of-freedom description of the human arm and its serial-chain equivalent in the PUMA convention [42]: (a) the seven rotations q1 to q7 drawn on the arm; (b) the same rotations as a chain of revolute joints. The four rotations solved in this thesis are drawn in colour; the grey wrist triple is not observable from the landmark set."),

(PM, [T("In the labels of Figure 3.7, the pair "),
      X(sub(r("q"), r("1")) + r(", ") + sub(r("q"), r("2"))),
      T(" is the shoulder swing "),
      X(d(t_("y") + r(", ") + t_("z"))),
      T(", "), X(sub(r("q"), r("3"))),
      T(" is the shoulder twist "), X(t_("t")),
      T(", and "), X(sub(r("q"), r("4"))),
      T(" is the elbow flexion "), X(sub(r("e"), r("y"))),
      T(". Figure 3.8 lays out these four joints as this thesis places them on the body, in the same drawing convention: each solved rotation appears as a revolute-joint cylinder whose axis is the rotation axis. The torso is one rigid plate carrying the root frame of Section 3.2. The shoulder at L12 is a cluster of three revolute joints sharing one centre, the way a spherical joint is decomposed in a manipulator diagram. The elbow at L14 is a single hinge. The wrist at L16 ends the chain, with no joint drawn there.")]),

(IMG, FIG / "ch3_fig_schematic.png", 6.3),
(CAP, "Figure 3.8. The kinematic schematic of the modelled right arm, drawn as a serial chain of revolute-joint cylinders in the PUMA style; the dash-dot line through each cylinder is its rotation axis. Every solved angle is labelled: the shoulder swing pair (azimuth about y and elevation about z, the latter drawn as a disc because its axis points out of the page), the shoulder twist about the upper-arm axis, and the elbow flexion. The straight-arm zero of the elbow is drawn dotted."),

(PM, [T("The four labelled angles are the quantities the rest of this chapter solves for, and the labels are used consistently from here on. The swing azimuth "),
      X(t_("y")), T(" turns the arm about the torso's y axis, and the swing elevation "),
      X(t_("z")), T(" raises it about the z axis. The twist "),
      X(t_("t")), T(" rolls the upper arm about its own length, and the elbow flexion "),
      X(sub(r("e"), r("y"))),
      T(" bends the forearm relative to the upper arm.")]),

(H3, "3.3.2 Definition of Shoulder, Elbow, and Wrist"),

(P, "With the root established, the model extends outward along each arm as a chain of two rigid segments. For the right arm the landmarks are the right shoulder (L12), right elbow (L14), and right wrist (L16); for the left arm, L11, L13, and L15. The upper arm runs from shoulder to elbow, the forearm from elbow to wrist. Figure 3.9 shows the four segments drawn on the real image of the worked-example frame."),

(IMG, FIG / "ch3_fig_arm_photo.png", 6.0),
(CAP, "Figure 3.9. The four arm segments of the worked-example frame drawn on the real image: upper arm L12 to L14 and forearm L14 to L16 on the participant's right (left side of the image), and L11 to L13, L13 to L15 on the participant's left."),

(P, "The joints contribute different information, as the schematic of Figure 3.8 shows. At the shoulder, two rotational degrees of freedom aim the upper arm and a third rolls it about its length. The elbow mainly contributes flexion, and the wrist's role is the subject of Section 3.4.4."),

(H3, "3.3.3 Establishing Local Arm Frames"),

(P, "A principle of the chain is that no joint rotation is ever measured in isolation; each is measured relative to its parent frame. The shoulder is measured relative to the torso, and the elbow relative to the rotated upper arm. This makes the angles meaningful for driving an avatar: an elbow angle describes how the forearm is bent relative to the upper arm, not relative to the room."),

(PM, [T("The shoulder's parent frame is placed as follows: a frame with the same orientation as the torso frame, with its origin moved to the shoulder landmark L12. In other words, the L12 frame is the root orientation "),
      X(Rroot),
      T(" translated up the trunk. No separate orientation is derived at the shoulder. Three torso landmarks define one rigid orientation, and a second basis at the shoulder, built for example from the shoulder line and the upper arm, would add a shoulder-girdle degree of freedom that the data cannot support. With the shoulder angles at zero, the right upper arm extends along the frame's +x axis, straight out to the participant's right.")]),

(PM, [T("In the language of Section 3.1, this fills in the second transformation of equation (3.5), the pose of the shoulder frame with respect to the root:")]),

(EQ, Tsh + r(" = ") + blockT(r("I"), RrootT + d(p12 + r(" − ") + p24)), "3.13"),

(PM, [T("The rotation block is the identity, and the origin "),
      X(RrootT + d(p12 + r(" − ") + p24)),
      T(" is the measured shoulder landmark expressed with respect to the torso: the mapping of equation (3.4) applied to "),
      X(p12),
      T(" with the root's rotation and origin.")]),

(P, "The elbow's parent is the upper arm itself, so its frame is the fully rotated arm frame: the root orientation composed with the solved shoulder rotation, with its origin at the elbow landmark L14. This is the same device used in the PUMA robot model, where several wrist frames share one origin and each new frame is the previous one carried through the joint rotation [42]. In the rest configuration the forearm continues the arm axis, along the local +x of the elbow frame; a straight arm is the zero of elbow flexion. The elbow frame's pose with respect to the shoulder frame is the third transformation of equation (3.5),"),

(EQ, Tel + r(" = ") + blockT(Rsh, RrootT + d(p14 + r(" − ") + p12)), "3.14"),

(PM, [T("with the solved shoulder rotation "), X(Rsh),
      T(" of Section 3.4.2 in the rotation block and the elbow landmark expressed in the shoulder frame's coordinates as the origin (the shoulder frame shares the root's orientation, so the same "),
      X(RrootT),
      T(" performs the mapping).")]),

(PM, [T("Expressing a measured segment in its parent frame always follows the same two-step pattern. First the segment is formed as a vector between two landmarks; for the right upper arm, "),
      X(r("v") + r(" = ") + p14 + r(" − ") + p12),
      T(". Then the vector is pulled into the parent frame by equation (3.3): "),
      X(sub(r("v"), nor("local")) + r(" = ") + RrootT + r(" ") + r("v")),
      T(". Written out, each component of the local vector is the dot product of "),
      X(r("v")),
      T(" with one torso axis, so the operation re-describes the arm in the body's own directions: how much of the segment points to the participant's right, how much up, how much forward. The joint angles are extracted from this local vector. The shoulder behaves like a joystick: the measured local vector says where the stick points, and the solver works backwards to the angles that put it there. Section 3.4 extracts them.")]),

(H2, "3.4 Joint Angle Computation"),

(P, "The angles transmitted to the reconstruction follow the Euler convention of the Unity animation system, which Chapter 6 describes. A bone's three Euler angles are applied in a fixed order: first the z rotation, then the x rotation, then the y rotation, each about the parent frame's axes. As a matrix product acting on column vectors, the rotation applied first sits nearest the vector, so the convention reads"),

(EQ, r("R") + r(" = ") + Rot("y", r("y")) + r(" ") + Rot("x", r("x")) + r(" ") + Rot("z", r("z")), "3.15"),
(PM, [T("where "), X(sub(r("R"), r("x"))), T(", "), X(sub(r("R"), r("y"))), T(", "), X(sub(r("R"), r("z"))),
      T(" are the elementary rotations about the coordinate axes. Figure 3.10 shows the order applied one elementary rotation at a time. The product is multiplied out symbolically in two stages, writing c and s for cosine and sine. The inner pair combines first: each row of "),
      X(sub(r("R"), r("x")) + d(r("x"))),
      T(" multiplies each column of "),
      X(sub(r("R"), r("z")) + d(r("z"))),
      T(", and because the x rotation leaves the first row untouched, the first row of the product is the first row of the z rotation:")]),
(MATH, sub(r("R"), r("x")) + d(r("x")) + r(" ") + sub(r("R"), r("z")) + d(r("z")) + r(" = ") + mat([
    [cs("c","z"), r("−")+cs("s","z"), r("0")],
    [cs("c","x")+cs("s","z"), cs("c","x")+cs("c","z"), r("−")+cs("s","x")],
    [cs("s","x")+cs("s","z"), cs("s","x")+cs("c","z"), cs("c","x")]])),
(PM, [T("Multiplying this intermediate matrix by "),
      X(sub(r("R"), r("y")) + d(r("y"))),
      T(" on the left mixes its first and third rows through the y rotation and leaves its second row unchanged, giving the full matrix used throughout this section:")]),
(EQ, r("R") + r(" = ") + mat([
    [cs("c","y")+cs("c","z")+r(" + ")+cs("s","y")+cs("s","x")+cs("s","z"),
     r("−")+cs("c","y")+cs("s","z")+r(" + ")+cs("s","y")+cs("s","x")+cs("c","z"),
     cs("s","y")+cs("c","x")],
    [cs("c","x")+cs("s","z"), cs("c","x")+cs("c","z"), r("−")+cs("s","x")],
    [r("−")+cs("s","y")+cs("c","z")+r(" + ")+cs("c","y")+cs("s","x")+cs("s","z"),
     cs("s","y")+cs("s","z")+r(" + ")+cs("c","y")+cs("s","x")+cs("c","z"),
     cs("c","y")+cs("c","x")]]), "3.16"),

(IMG, FIG / "ch3_fig_zxy_order.png", 6.3),
(CAP, "Figure 3.10. The Euler convention built one elementary rotation at a time: starting from identity, the z angle is applied first, then x, then y, all about parent axes, giving R = Ry Rx Rz."),

(PM, [T("The structure of this matrix makes it possible to extract the angles. Write "),
      X(sub(r("m"), r("ij"))),
      T(" for the entry of a measured numerical matrix "), X(r("m")),
      T(" in row i, column j. The entry "), X(sub(r("m"), r("23"))),
      T(" is "), X(r("−") + cs("s", "x")),
      T(", isolating the x angle. The third column of the matrix is "),
      X(d(cs("s","y")+cs("c","x") + r(", −") + cs("s","x") + r(", ") + cs("c","y")+cs("c","x"))),
      T(", so its first and third entries share the factor "), X(cs("c","x")),
      T(", which cancels in the two-argument arctangent and leaves the y angle. The second row shares the same factor across its first two entries and leaves the z angle the same way:")]),
(EQ, r("x") + r("=") + nor("asin") + d(r("−")+sub(r("m"),r("23"))) + r(", ") +
     r("y") + r("=") + nor("atan2") + d(sub(r("m"),r("13"))+r(",")+sub(r("m"),r("33"))) + r(", ") +
     r("z") + r("=") + nor("atan2") + d(sub(r("m"),r("21"))+r(",")+sub(r("m"),r("22"))), "3.17"),
(PM, [T("The two-argument arctangent inspects the signs of both arguments and returns the angle in the correct quadrant over the full circle; a plain arctangent covers only half the circle. The arcsine restricts x to the range -90 to +90 degrees. When x reaches either end of that range ("),
      X(d(sub(r("m"), r("23")), "|", "|") + r(" = 1")),
      T("), the y and z rotations turn about the same effective axis and only their combined angle is defined; this configuration is called gimbal lock. The decoding stays well defined there by convention: z is set to zero and y carries the whole combined rotation. The pose itself is still represented without ambiguity; only the split of the combined rotation between the two angles is a choice.")]),

(H3, "3.4.1 Torso Pose"),

(PM, [T("The torso needs no solving, because it is not a joint. Its pose is the pair "),
      X(Rroot + r(", ") + p24),
      T(". Applying equation (3.17) to "), X(Rroot),
      T(" gives the three angles of the torso; the worked example of Section 3.5 carries this out on measured data.")]),


(H3, "3.4.2 Shoulder Orientation"),

(PM, [T("A shoulder pose must describe both the upper-arm direction and its axial roll, the three angles labelled at the shoulder of the schematic in Figure 3.8. These components separate into swing and twist [44], with the twist placed innermost in the three-factor rotation:")]),
(EQ, Rsh + r(" = ") + Rot("y", t_("y")) + r(" ") + Rot("z", t_("z")) + r(" ") + Rot("x", t_("t")), "3.18"),
(PM, [T("where "), X(t_("y")), T(" and "), X(t_("z")),
      T(" are the swing angles and "), X(t_("t")),
      T(" is the twist about the rest arm axis +x. The order is forced by a simple observation: a rotation about x leaves the x axis itself fixed. With the twist innermost, applying "),
      X(Rsh), T(" to the rest arm direction "), X(xhat),
      T(" removes the twist factor immediately,")]),
(EQ, ahat + r(" = ") + Rsh + r(" ") + xhat + r(" = ") +
     Rot("y", t_("y")) + r(" ") + Rot("z", t_("z")) + r(" ") + xhat + r(" = ") +
     d(cs("c","y")+cs("c","z") + r(",  ") + cs("s","z") + r(",  −") + cs("s","y")+cs("c","z")), "3.19"),
(P, "so the upper-arm direction depends on the swing alone, and the twist is exactly the roll about the arm that the elbow position cannot see. If the twist were outermost instead, the twist axis would stop being the arm axis as soon as the arm swings, and the decomposition would lose its physical meaning. Two consequences follow. First, the twist is invisible in the shoulder-to-elbow vector and must be measured from a second segment, the forearm. Second, this joint order is not the transmitted Euler order, so driving the rig requires composing the matrix and re-extracting angles with equation (3.17), carried out in Chapter 6. Figure 3.11 illustrates both halves of the decomposition."),

(IMG, FIG / "ch3_fig_swing_twist.png", 6.3),
(CAP, "Figure 3.11. The swing-twist decomposition. (a) The swing aims the rest arm +x into the observed direction â; the direction drawn is the measured arm direction of the worked-example frame. (b) The twist rolls about the arm axis; it is measured in the plane perpendicular to that axis, after the swing has been undone."),

(PM, [T("The swing angles read off the components of "), X(ahat),
      T(" directly. Its y component is "), X(cs("s", "z")), T(", so")]),
(EQ, t_("z") + r(" = ") + nor("asin") + d(sub(r("a"),r("y"))), "3.20"),
(PM, [T("the elevation of the arm, positive upward, restricted to -90 to +90 degrees. The x and z components share the factor "),
      X(cs("c", "z")), T(", which cancels in the two-argument arctangent:")]),
(EQ, t_("y") + r(" = ") + nor("atan2") + d(r("−")+sub(r("a"),r("z"))+r(", ")+sub(r("a"),r("x"))), "3.21"),
(PM, [T("the azimuth of the arm, positive sweeping backward. Every direction of the arm is reachable by some pair of swing angles, so there is no coverage gap. The one degenerate configuration is the arm pointing straight up or straight down ("),
      X(t_("z") + r(" = ±90°")),
      T("): there the x and z components both vanish and the azimuth is undefined. The convention "),
      X(t_("y") + r(" = 0")),
      T(" is applied, and any axial rotation folds into the twist automatically.")]),

(P, "Solving the twist means measuring rotation about the arm axis, and rotation about an axis is only visible in the plane perpendicular to that axis. The procedure therefore first undoes the swing, bringing the arm axis back onto +x, so that the perpendicular plane becomes exactly the local y-z plane:"),
(EQ, r("f′") + r(" = ") + Rot("z", r("−")+t_("z")) + r(" ") + Rot("y", r("−")+t_("y")) + r(" ") + r("f"), "3.22"),
(PM, [T("where "), X(r("f")),
      T(" is the forearm vector in the parent frame from Section 3.3.3. The zero convention is anatomical: at zero twist, the forearm's perpendicular component points along local +z, meaning the elbow flexes forward. Under a twist "),
      X(t_("t")), T(", that component rotates to "),
      X(d(r("−") + nor("sin ") + t_("t") + r(", ") + nor("cos ") + t_("t"))),
      T(" in the (y, z) plane, so the twist reads")]),
(EQ, t_("t") + r(" = ") + nor("atan2") + d(r("−")+sub(r("f′"),r("y"))+r(", ")+sub(r("f′"),r("z"))), "3.23"),
(P, "positive for internal rotation (the forearm rotating downward from forward)."),

(PM, [T("For the left arm no new derivation is needed. Left angles are defined through the sagittal mirror: both left segment vectors are expressed in the root basis, their x components are flipped with "),
      X(r("M") + r(" = ") + nor("diag") + d(r("−1, 1, 1"))),
      T(", and the identical right-arm solver runs on the result. Because the mirror preserves the whole construction, every property above carries over unchanged, and a mirror-symmetric pose produces identical angle values on both sides with the same anatomical meaning: positive "),
      X(t_("y")), T(" sweeps backward, positive "), X(t_("z")),
      T(" raises the arm, positive "), X(t_("t")), T(" rotates internally.")]),

(H3, "3.4.3 Elbow Flexion and Extension"),

(PM, [T("The elbow is solved in the L14 frame established in Section 3.3.3: the fully rotated arm frame "),
      X(Rarm + r(" = ") + Rroot + Rot("y", t_("y")) + Rot("z", t_("z")) + Rot("x", t_("t"))),
      T(", in which the rest forearm continues the arm axis along +x. The forearm direction in this frame is "),
      X(ghat + r(" = ") + sup(Rarm, r("T")) + d(p16 + r(" − ") + p14)),
      T(", normalized, and its swing is read the same way as at the shoulder, an elevation and an azimuth pair:")]),
(EQ, sub(r("e"),r("z")) + r(" = ") + nor("asin") + d(sub(r("g"),r("y"))) + r(",      ") +
     sub(r("e"),r("y")) + r(" = ") + nor("atan2") + d(r("−")+sub(r("g"),r("z"))+r(", ")+sub(r("g"),r("x"))), "3.24"),
(PM, [T("with "), X(sub(r("e"), r("y")) + r(" = 0")), T(" a straight arm and "),
      X(sub(r("e"), r("y")) + r(" = −90")), T(" a right angle bend. This is the angle labelled at the elbow hinge of the schematic in Figure 3.8.")]),

(PM, [T("A structural fact simplifies the extraction: "), X(sub(r("e"), r("z"))),
      T(" is identically zero. The shoulder twist was defined as exactly the rotation that aligns the forearm's perpendicular component with local +z, so by the time the elbow is solved, the flexion plane has already been rotated into the x-z plane of the elbow frame. The elbow's out-of-plane freedom is not lost; it is the shoulder twist, already accounted for one joint earlier. This closes the dimension count: the two measured segment directions carry four observable degrees of freedom, and the model extracts four independent angles. The angle "),
      X(sub(r("e"), r("z"))),
      T(" is kept in the data interface for generality but carries no independent information.")]),

(PM, [T("The elbow also exposes the one case where a three-landmark arm breaks down. When the arm is straight, the forearm is parallel to the upper arm, its perpendicular component vanishes, and the shoulder twist becomes unobservable; no algebra can recover a roll about an axis from two collinear segments. The solver detects the condition by thresholding the perpendicular fraction of the forearm, applies the convention "),
      X(t_("t") + r(" = 0")),
      T(" so the elbow frame stays defined, and flags the twist as unobservable so that downstream processing holds the last valid value instead of trusting a numerical accident. Near-straight elbows leave the flexion angle well conditioned but make the twist sensitive to noise; this is discussed as a practical limitation in Chapter 9.")]),

(H3, "3.4.4 The Wrist as a Tracked Point"),

(P, "The wrist is not a solved joint of this model. The chain solves for the shoulder and the elbow; the wrist L16 enters the model as a tracked 3D point, as the schematic of Figure 3.8 draws it. That point does two jobs for the solver. It defines the forearm direction that the elbow flexion is read from, and it supplies the second segment that makes the shoulder twist observable."),

(P, "A full three-degree-of-freedom wrist orientation is not resolved. The missing ingredient is a landmark beyond the wrist: forearm pronation, the roll of the forearm about its own axis, produces no motion of the wrist point at all, so no algebra over these landmarks can observe it. The tracked wrist position is retained and transmitted, for three reasons. It places the terminal point of each arm correctly in the reconstructed scene. It is the anchor that the pose recovery of Chapter 5 restores from the object pose when the landmark is lost during a grip. And it gives the attachment point where a hand-specific model such as the hierarchical hand model of [41], which solves finger joints from dedicated hand landmarks, could later extend the chain without changing the arm solver."),

(H2, "3.5 Worked Example"),

(P, "A single measured frame now carries the whole chain from raw landmark positions to the complete angle set. The frame is taken part way through the task of Chapter 2, while the cube slides along the rail. It is the frame shown in Figures 3.5 and 3.9: the participant stands at the desk with the right hand on the cube and the left arm at the side. It is chosen because all eight landmarks are measured on it, none of them was flagged by the despiking stage or filled by the gap stage of Section 2.4, and no failure detector of Chapter 5 fires on it. Each solved value below is pointed back at its label in the schematic of Figure 3.8. A convention applies throughout: values are computed from the unrounded landmark positions and printed rounded to two decimals, so recomputing a step by hand from the rounded printed inputs can differ from a printed result in the last digit."),

(P, "The eight landmark positions in both coordinate frames are listed in Table 3.1. These are the positions after the filtering of Section 2.4, since the solver consumes the filtered stream. The same frame is carried through the worked examples of Appendix C, Appendix D and Appendix E, so the landmark, depth and marker readings behind these positions can be followed there."),

(TBL, [["Landmark", "Camera frame C (m)", "Person space P (m)"],
       ["L11 left shoulder", "(0.22, -0.34, 1.36)", "(0.22, 0.34, 1.36)"],
       ["L12 right shoulder", "(-0.16, -0.33, 1.31)", "(-0.16, 0.33, 1.31)"],
       ["L13 left elbow", "(0.28, -0.03, 1.38)", "(0.28, 0.03, 1.38)"],
       ["L14 right elbow", "(-0.20, -0.04, 1.19)", "(-0.20, 0.04, 1.19)"],
       ["L15 left wrist", "(0.24, 0.20, 1.25)", "(0.24, -0.20, 1.25)"],
       ["L16 right wrist", "(-0.20, 0.11, 1.06)", "(-0.20, -0.11, 1.06)"],
       ["L23 left hip", "(0.12, 0.18, 0.99)", "(0.12, -0.18, 0.99)"],
       ["L24 right hip", "(-0.06, 0.19, 0.99)", "(-0.06, -0.19, 0.99)"]]),
(CAP, "Table 3.1. The eight landmarks of the worked-example frame in the camera frame and in person space, printed to two decimals. The conversion flips only the sign of y. The hips have negative person-space y because they sit below the camera height, and their depth is the depth of the rail in front of them (see the torso decode below)."),

(P, "The torso construction of Section 3.2 needs three of these points, in person space:"),
(MATH, eqArr(
    p23 + r(" = (0.12, −0.18, 0.99)"),
    p24 + r(" = (−0.06, −0.19, 0.99)"),
    p12 + r(" = (−0.16, 0.33, 1.31)"))),

(P, "Following equation (3.7), the hip line is the difference of the two hip positions,"),
(MATH, p24 + r(" − ") + p23 + r(" = (−0.18, −0.01, −0.01)")),
(P, "with length 0.18 m. Dividing by the length:"),
(MATH, xhat + r(" = (−1.00, −0.05, −0.04)")),
(P, "The x component is close to -1: the participant's right points toward the camera's left. The spine-side vector of equation (3.8) is"),
(MATH, r("s") + r(" = ") + p12 + r(" − ") + p24 + r(" = (−0.11, 0.53, 0.33)")),
(P, "with length 0.63 m. Its upward y component dominates, and it carries a z component of 0.33 because the shoulder is measured farther from the camera than the hip. The cross product of equation (3.9) follows, each component written out and printed rounded:"),
(MATH, eqArr(
    d(xhat + r(" × ") + r("s"), "(", ")") + sub(r(""), r("x")) + r(" = (−0.05) · 0.33 − (−0.04) · 0.53 = 0.00"),
    d(xhat + r(" × ") + r("s"), "(", ")") + sub(r(""), r("y")) + r(" = (−0.04) · (−0.11) − (−1.00) · 0.33 = 0.33"),
    d(xhat + r(" × ") + r("s"), "(", ")") + sub(r(""), r("z")) + r(" = (−1.00) · 0.53 − (−0.05) · (−0.11) = −0.53"))),
(P, "with length 0.63 m. Normalizing gives"),
(MATH, zhat + r(" = (0.01, 0.53, −0.85)")),
(P, "a direction toward the camera, negative z, tipped upward by the same hip-to-shoulder depth difference: the chest faces the camera. The second cross product, equation (3.10), closes the frame:"),
(MATH, yhat + r(" = ") + zhat + r(" × ") + xhat + r(" = (−0.06, 0.85, 0.53)")),
(P, "a unit vector with no normalization. Assembling the columns by equation (3.11):"),
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
(P, "The upper-left block is the rotation just assembled and the last column is the right hip position: one matrix now carries where the torso sits in person space and how it is turned. The shoulder's transformation with respect to the root, equation (3.13), needs the shoulder landmark expressed in the torso's coordinates, by the point mapping of equation (3.4):"),
(MATH, RrootT + d(p12 + r(" − ") + p24) + r(" = (0.07, 0.63, 0.00)")),
(P, "The spine-side vector lies in the torso plane by construction, so the third component is an algebraic zero: the shoulder sits straight up and slightly to the right of the hip in the torso's own coordinates, with no forward offset. The transformation is"),
(MATH, Tsh + r(" = ") + mat([
    [r("1"), r("0"), r("0"), r("0.07")],
    [r("0"), r("1"), r("0"), r("0.63")],
    [r("0"), r("0"), r("1"), r("0.00")],
    [r("0"), r("0"), r("0"), r("1")]])),
(P, "an identity rotation with a pure origin shift, as equation (3.13) prescribes. Decoding the root matrix with equation (3.17) reads one entry or entry pair per angle: the entry in row 2, column 3 gives the x angle, the third column gives y, and the second row gives z:"),
(MATH, eqArr(
    r("x") + r(" = ") + nor("asin") + d(r("−0.53")) + r(" = −32.08°"),
    r("y") + r(" = ") + nor("atan2") + d(r("0.01, −0.85")) + r(" = 179.49°"),
    r("z") + r(" = ") + nor("atan2") + d(r("−0.05, 0.85")) + r(" = −3.26°"))),
(P, "Compared with the reference configuration (0, 180, 0), the participant faces almost straight at the sensor, the hip line is almost level, and the frame is pitched by 32.08 degrees, because the hips sit nearer the camera than the shoulders. The photograph in Figure 3.5 shows an upright trunk. The pitch is a property of the hip measurement: the two hip landmarks fall on the pixels where the pelvis meets the rail, and the depth sampled there is the depth of the rail. Table 3.1 shows 0.99 metres against 1.31 and 1.36 metres at the two shoulders. The root frame carries that offset, and the arm angles below are read against this pitched frame. Chapter 5 describes this kind of failure, a correct pixel over a depth sample taken on the surface in front of the body, and its torso repair puts the hips back on their own camera rays at a remembered trunk depth; Chapter 7 reports the repaired root. This chapter works on the measurement as it stands. These three values are the torso pose of Section 3.4.1."),

(P, "The right arm continues from the same frame. The person-space upper arm vector is"),
(MATH, r("v") + r(" = ") + p14 + r(" − ") + p12 + r(" = (−0.04, −0.29, −0.12)")),
(P, "with length 0.32 m, about the length of an upper arm. Pulling the vector into the parent frame by equation (3.3), each component becomes a dot product with one column of the root matrix:"),
(MATH, sub(r("v"), nor("local")) + r(" = ") + RrootT + r(" ") + r("v") + r(" = (0.05, −0.31, −0.05)")),
(P, "The vector now reads anatomically: the upper arm points slightly across the body (+x is the participant's right), strongly downward (negative y), and slightly behind the pitched torso plane (negative z). That is the visible pose in Figure 3.9, the right arm reaching down to the cube on the rail. Equation (3.3) applies a rotation, so the length 0.32 is unchanged, and dividing by it gives the local arm direction:"),
(MATH, ahat + r(" = (0.17, −0.97, −0.16)")),
(P, "The same two steps applied to the forearm give the forearm vector in the parent frame,"),
(MATH, r("f") + r(" = ") + RrootT + d(p16 + r(" − ") + p14) + r(" = (0.01, −0.20, 0.03)")),
(P, "with length 0.20 m. These two local vectors are the complete input to the right-arm angle computation; nothing else about the pose is needed."),

(PM, [T("Equations (3.20) and (3.21) read the two swing angles (Figure 3.8):")]),
(MATH, eqArr(
    t_("z") + r(" = ") + nor("asin") + d(r("−0.97")) + r(" = −76.57°"),
    t_("y") + r(" = ") + nor("atan2") + d(r("0.16, 0.17")) + r(" = 43.03°"))),
(P, "the arm points 76.57 degrees below horizontal, and its small remaining horizontal component is swept toward the participant's back. Undoing this swing on the forearm vector by equation (3.22) gives"),
(MATH, r("f′") + r(" = ") + Rot("z", r("76.57°")) + r(" ") + Rot("y", r("−43.03°")) + r(" ") + r("f") + r(" = (0.19, −0.06, 0.03)")),
(PM, [T("its perpendicular part points mostly along negative y (Figure 3.8), and equation (3.23) gives the twist:")]),
(MATH, t_("t") + r(" = ") + nor("atan2") + d(r("0.06, 0.03")) + r(" = 59.92°")),
(P, "an internal rotation: the forearm turns inward across the front of the body, so the hand rests on the cube in front of the trunk. In the elbow frame the forearm direction is"),
(MATH, ghat + r(" = (0.94, 0.00, 0.34)")),
(PM, [T("Its y component is zero, the "),
      X(sub(r("e"), r("z")) + r(" = 0")),
      T(" property of Section 3.4.3 holding on the measured frame, and the flexion of equation (3.24), the hinge angle of Figure 3.8, is")]),
(MATH, sub(r("e"), r("y")) + r(" = ") + nor("atan2") + d(r("−0.34, 0.94")) + r(" = −19.81°")),
(PM, [T("a gentle bend. The solved shoulder rotation and the local upper-arm vector "),
      X(sub(r("v"), nor("local"))),
      T(" computed above also complete the last transformation of equation (3.5) as numbers, the elbow pose of equation (3.14):")]),
(MATH, Tel + r(" = ") + mat([
    [r("0.17"), r("0.95"), r("−0.27"), r("0.05")],
    [r("−0.97"), r("0.12"), r("−0.20"), r("−0.31")],
    [r("−0.16"), r("0.30"), r("0.94"), r("−0.05")],
    [r("0"), r("0"), r("0"), r("1")]])),
(PM, [T("Its rotation block is the composed swing and twist just solved (its first column is exactly "),
      X(ahat),
      T(", the local arm direction), and its last column is the elbow's position in the shoulder frame. Two checks close the numeric chain. First, composing the three matrices as in equation (3.6) and applying the product to the origin lands on (-0.20, 0.04, 1.19), the measured elbow position of Table 3.1, to machine precision: the relative transformations rebuild the measured chain. Second, carrying the measured wrist through the inverse chain into the elbow frame, three applications of equation (3.4), gives (0.19, 0.00, 0.07): its length is the forearm length 0.20, its zero second component is the "),
      X(sub(r("e"), r("z")) + r(" = 0")),
      T(" property again, and dividing by the length reproduces the "),
      X(ghat),
      T(" used for the flexion.")]),
(P, "The left arm runs through the identical mirrored solver and yields a shoulder azimuth of 76.07 degrees, an elevation of -53.52 degrees, a twist of 108.86 degrees, and an elbow flexion of -37.34 degrees: the arm hanging at the side in Figure 3.9, read against the same pitched root frame and bent more than the right. The entire measured pose of this frame is now described by thirteen numbers: three root Euler angles, then swing, twist, and flexion for each arm, with the zero elbow angle carried for generality."),

(P, "This worked example completes the model: the same equations run on every frame of a recording and on both arms. The accuracy of the angles the model produces is evaluated in Chapter 7."),

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

out = REPO / "writing" / "v7" / "Chapter_3_Kinematic_Modeling.docx"
doc.save(out)
print("saved", out, "| items:", len(content))

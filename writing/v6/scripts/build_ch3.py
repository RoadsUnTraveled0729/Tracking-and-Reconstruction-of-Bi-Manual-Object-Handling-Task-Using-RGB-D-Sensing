#!/usr/bin/env python3
"""Build writing/v4/Chapter_3_Kinematic_Modeling.docx.

Supervisor round of 2026-08-03: Section 3.4 renamed Joint Angle Computation
and restricted to the kinematic model and worked examples; new Section 3.5
collects all Unity material (root driving, bone composition, rig stills, rig
instrumentation) with the frame-100 numerical thread continued. Side
comparisons cut (rejected twist formula, forearm-vector equivalence, e_z
proof detail, Table 3.2 replaced by a summary paragraph). Worked-example
numbers printed to two decimals. Inline math (PM tag) added for symbols in
prose. New Figure 3.5 shows the reference configuration (T-pose).
Figure renumbering: old 3.5-3.7 -> 3.6-3.8 stay diagrams; rig stills move to
3.5 as Figures 3.9-3.12.

All numbers computed by running the implemented solver (kinematics/root_frame.py,
kinematics/shoulder.py) on pinned data (regenerated via ch3_numbers.py from
mediapipe/output/recording_20260224_083945_landmarks_filtered_v2.csv).
"""
from docx import Document
from docx.shared import Pt, Inches

from eqn import r, nor, sub, sup, hat, frac, mat, d, eqArr, \
    add_display_eq, add_display_math, add_inline_math

FIG = "/home/luo/Desktop/New_SandBox/writing/v2/figures/"
FIG4 = "/home/luo/Desktop/New_SandBox/writing/v6/figures/"
H1, H2, H3, P, IMG, CAP, TBL, EQ = "h1", "h2", "h3", "p", "img", "cap", "tbl", "eq"
MATH = "mth"  # displayed, unnumbered worked-example mathematics
PM = "pm"     # paragraph mixing text runs and inline math


def T(t):
    return ("t", t)


def X(f):
    return ("m", f)


# --- equation-fragment shorthands ---
def Rot(axis, arg=None):
    """R with axis subscript, optionally applied to an argument: R_y(t_y)."""
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
Rsh = sub(r("R"), nor("sh"))
xhat = hat(r("x"))
yhat = hat(r("y"))
zhat = hat(r("z"))
ahat = hat(r("a"))
ghat = hat(r("g"))

content = [
(H1, "Chapter 3: Kinematic Modeling"),

(P, "The previous chapter ended with eight body landmarks per frame, each lifted to a metric 3D position in the camera frame. Those positions are labelled and arrive in a fixed order, but on their own they say nothing about how the body segments are oriented relative to one another, or about how each joint has rotated between one frame and the next. This chapter introduces the kinematic model that gives the points that meaning. The model is organized as a hierarchical chain of coordinate frames, rooted at the pelvis and extending outward through the shoulder and elbow of each arm, following the hierarchical modeling principle established for the hand by [15]. Once the chain is built, the pose of the body reduces to a small set of anatomical joint angles: the orientation and position of the torso, a swing and twist for each shoulder, and a flexion angle for each elbow. Section 3.5 shows how these angles drive the Unity avatar."),

(P, "Three properties distinguish the model developed here. First, it is closed form: every angle is computed directly from the landmark geometry of the current frame, with no optimization and no temporal state. Second, it is an exact inverse: the solved angles reconstruct the measured segment directions to machine precision, so validation can demand exact agreement rather than a close fit. Third, every construction was first checked on synthetic recordings with known injected angles; the main results of those checks appear with the derivations. The chapter proceeds in the order of the chain itself: the mathematical tools first, then the torso root frame, then the arm frames, then the computation of the joint angles, and finally the mapping onto the Unity avatar. A numerical worked example on real data accompanies each stage."),

(H2, "3.1 Kinematic Foundations"),

(H3, "3.1.1 Coordinate Systems and Transformations"),

(P, "A coordinate frame is an origin point together with three mutually perpendicular unit vectors, labelled x, y, and z, that define the directions of the three axes. Any point in space is described by how far one must travel along each axis direction, starting from the origin, to reach it. The entire kinematic model is built from such frames: one is attached to each body segment, and when a segment moves, its frame moves with it. The orientation of one segment relative to another is then captured entirely by the relationship between their two frames. Being precise about which frame a number lives in is the single most important bookkeeping rule of this chapter, so the two frames that bracket the whole system are defined first."),

(P, "Every measurement produced by the sensing stage of Chapter 2 is expressed in the camera frame of the RealSense sensor, denoted C. This frame is right-handed: x points to the right in the image, y points downward, and z points forward from the sensor into the scene [9]. The z coordinate of a point in this frame is exactly the depth measured by the sensor. The reconstruction environment uses a different convention: Unity's frame is left-handed with y pointing up. Figure 3.1 shows the two conventions side by side, the camera frame drawn on the sensor and the Unity frame drawn on a screenshot of the Unity scene."),

(IMG, FIG + "ch3_fig1_sensor_unity.png", 6.3),
(CAP, "Figure 3.1. (a) The D435 camera frame C, drawn on the sensor: x right in the image, y down, z out of the sensor into the scene (the depth direction). (b) The Unity frame U, drawn on a screenshot of the reconstruction scene: x right, y up, z forward, left-handed."),

(PM, [T("A right-handed and a left-handed frame have opposite orientations, so the handedness itself must change during the conversion, not just the labels of the axes. The conversion used throughout this work is a single matrix multiplication applied to every measured point. If "),
      X(r("p")), T(" is a landmark position in the camera frame, its position "),
      X(r("q")), T(" in the person space P used by all the kinematic math is")]),
(EQ, r("q") + r(" = ") + r("F") + r(" ") + r("p") + r(",        ") + r("F") + r(" = ") + nor("diag") + d(r("1, −1, 1")), "3.1"),
(PM, [T("that is, the y coordinate flips sign and x and z pass through unchanged. Flipping exactly one axis converts a right-handed frame to a left-handed one: the determinant of "),
      X(r("F")), T(" is -1, the signature of a reflection. After the flip, x still points to the right in the image, y now points up, and z still points away from the camera, matching Unity's convention. Both frames keep the same origin at the optical centre of the camera; only the reading of the y axis changes. The flip applies to points only, never to rotation matrices: every rotation below is built from already flipped points, so every rotation in the pipeline comes out proper. Figure 3.2 shows the two frames drawn from that single shared origin, together with a real measurement: the right wrist of frame 100, the running example frame of Chapter 2, reads (-0.07, -0.16, 0.99) in the camera frame and (-0.07, +0.16, 0.99) in person space. Same physical point, one flipped coordinate. From this point onward, every landmark position in this chapter is a person-space value unless stated otherwise.")]),

(IMG, FIG4 + "ch3_fig2_colocated.png", 5.2),
(CAP, "Figure 3.2. The camera frame C and person space P drawn from the same origin, each axis labelled with the frame it belongs to. Only the y axis differs: the camera reads y downward, person space reads y upward. The wrist landmark of frame 100 is shown with its coordinates in both frames."),

(H3, "3.1.2 Homogeneous Transformation Matrices"),

(P, "The relationship between two coordinate frames consists of two pieces of information: how the child frame is rotated relative to the parent, and where the child's origin sits in the parent's coordinates. Together they form a rigid body transformation, an operation that moves and turns an object without deforming it [41]."),

(PM, [T("The rotation part is a 3 by 3 matrix "), X(r("R")),
      T(" whose three columns are the child frame's axis directions written in the parent's coordinates: the first column is the child's x axis as seen from the parent, the second its y axis, the third its z axis. Because the columns are perpendicular unit vectors, "),
      X(r("R")), T(" has a special property: its transpose equals its inverse, "),
      X(sup(r("R"), r("T")) + r("R") + r(" = ") + r("I")),
      T(", and its determinant equals one. This property is used constantly in what follows, because a vector expressed in the parent frame is brought into the child frame by multiplying with "),
      X(sup(r("R"), r("T"))), T(", with no numerical matrix inversion ever needed.")]),

(PM, [T("The translation part is a 3-vector "), X(r("t")),
      T(" giving the position of the child's origin in the parent frame. Rotation and translation combine into a single 4 by 4 homogeneous transformation matrix "),
      X(r("T")), T(" whose top-left 3 by 3 block is "), X(r("R")),
      T(", whose top-right column is "), X(r("t")),
      T(", and whose bottom row is (0, 0, 0, 1). A point is transformed by appending a 1 to its coordinates and multiplying: the result is "),
      X(r("R") + r(" ") + r("p") + r(" + ") + r("t")),
      T(", the point rotated and then shifted, a complete rigid body motion in one multiplication.")]),

(PM, [T("The value of this representation appears when transformations chain. If "),
      X(sub(r("T"), r("1"))), T(" describes the torso frame relative to person space and "),
      X(sub(r("T"), r("2"))), T(" describes a shoulder frame relative to the torso, then the product "),
      X(sub(r("T"), r("1")) + sub(r("T"), r("2"))),
      T(" describes the shoulder frame directly in person space. Rotations defined locally, each relative to its immediate parent, accumulate into a single description of the whole arm. The same property runs in reverse during angle computation: given a measured segment direction "),
      X(r("v")), T(" in person space and the known orientation "),
      X(sub(r("R"), nor("parent"))),
      T(" of its parent frame, the segment's direction in the parent frame is")]),
(EQ, sub(r("v"), nor("local")) + r(" = ") + sup(sub(r("R"), nor("parent")), r("T")) + r(" ") + r("v"), "3.2"),
(PM, [T("Here "), X(r("v")), T(" is a direction vector between two landmarks rather than a point; the convention throughout this chapter is that "),
      X(r("p")), T(" marks a measured landmark point and "), X(r("v")),
      T(" marks a segment vector formed from two points, and directions transform by rotation alone. That single operation, pulling a measured vector back into a local frame, is the heart of every derivation in Section 3.4. Figure 3.3 sketches the chain on a mannequin, with the three frames of the right arm chain drawn at their anatomical origins.")]),

(IMG, FIG + "ch3_fig3_chain_mannequin.png", 5.8),
(CAP, "Figure 3.3. The kinematic chain drawn on a mannequin, front view (the subject faces the sensor, so the subject's right side appears on the left of the image). The root frame sits at the right hip L24; the L12 shoulder frame has the same orientation as the root with its origin moved to L12; the L14 elbow frame is the fully rotated arm frame, with x continuing the upper-arm axis."),

(H2, "3.2 Torso Reference Frame"),

(H3, "3.2.1 Landmark Selection"),

(P, "The torso frame is the root of the entire upper-body chain: every other frame is expressed, directly or through the chain, in terms of this one. It is constructed from three MediaPipe landmarks [39]: the right hip (L24), the left hip (L23), and the right shoulder (L12). Throughout this thesis, left and right always mean the subject's own left and right; since the subject faces the sensor, the subject's right side appears on the left of the camera image."),

(P, "The selection rests on three assumptions. The hips and shoulders are the most stable landmarks during manipulation tasks: they move slowly and are rarely hidden by the manipulated object, unlike the hands and forearms. Three points are the minimum that defines a plane, and a plane is needed to fix a full three-axis orientation; two points would give only a single direction. And the three chosen landmarks span a broad triangle across the trunk, so a small measurement error in any one landmark has a proportionally small effect on the computed axes."),

(P, "One further assumption should be stated before the construction. With only three torso points, the model cannot separate the pelvis from the upper trunk. It therefore assumes that there is no relative twist between the shoulders and the hips: the whole torso is treated as one rigid plate whose orientation the frame captures. A consequence is that a forward lean of the trunk pitches the root frame with it. This simplification is accepted for the present model and is revisited in the limitations of Chapter 8."),

(H3, "3.2.2 Derivation of Torso Frame"),

(PM, [T("The three landmark positions arrive from Chapter 2 in the camera frame and are converted to person space by the flip F of Section 3.1.1; the construction below happens entirely in person space. Let "),
      X(p23), T(", "), X(p24), T(", and "), X(p12),
      T(" denote the person-space positions of the left hip, right hip, and right shoulder. The torso is not a joint and has no joint angles; what this section derives is the orientation and location of the torso plane, described as a rotation matrix and an origin. Figure 3.4(a) shows the two input vectors drawn on the real image of frame 100, and Figure 3.4(b) shows the finished frame projected back onto the same image.")]),

(IMG, FIG4 + "ch3_fig4_torso_photo.png", 6.3),
(CAP, "Figure 3.4. The torso frame on the real image of frame 100. (a) The two input vectors: the hip line from L23 to L24 (red) and the spine-side vector s from L24 up to L12 (yellow). (b) The finished orthonormal frame at the L24 origin, projected through the camera intrinsics: x toward the subject's right, y up along the trunk, z forward out of the chest (foreshortened because it points almost straight at the camera)."),

(P, "The x axis is defined first. It is the unit vector along the hip line, pointing toward the subject's right (the hat marks a unit vector):"),
(EQ, xhat + r(" = ") + frac(p24 + r(" − ") + p23,
     d(p24 + r(" − ") + p23, "|", "|")), "3.3"),
(P, "No sign correction is needed: subtracting the left-hip position from the right-hip position already produces a vector that points to the subject's right, the +x direction of person space. This axis is kept exactly as measured, because both of its endpoints are pelvis landmarks; the hip line is the one direction the three points define with no ambiguity."),

(P, "The second input is the spine-side vector from the right hip up to the right shoulder,"),
(EQ, r("s") + r(" = ") + p12 + r(" − ") + p24, "3.4"),
(PM, [T("This vector is deliberately not used as an axis. It is generally not perpendicular to the hip line (in frame 100 the angle between them is 85.4 degrees, not 90), and treating it as an axis would produce a skewed, non-orthogonal frame. Its only job is to select the torso plane: among all the planes that contain the hip line, the torso plane is the one that also contains "),
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
     d(xhat + r(" × ") + r("s"), "|", "|")), "3.5"),
(PM, [T("The ordering of the two factors is a deliberate choice of sign: with "),
      X(xhat), T(" pointing to the subject's right and "), X(r("s")),
      T(" pointing up the trunk, the product points forward, out of the subject's chest toward the camera. Reversing the order would flip the axis into the subject's back. The cross product also discards the part of "),
      X(r("s")), T(" that is parallel to "), X(xhat),
      T(" automatically, so the imperfect angle between the inputs does no harm: only the component of "),
      X(r("s")), T(" perpendicular to the hip line contributes.")]),

(P, "The y axis closes the frame with a second cross product:"),
(EQ, yhat + r(" = ") + zhat + r(" × ") + xhat, "3.6"),
(PM, [T("Because "), X(zhat), T(" and "), X(xhat),
      T(" are already perpendicular unit vectors, this product is exactly a unit vector, with no normalization needed. This third step guarantees a perfectly orthonormal frame in every measured pose, regardless of the angle between the original inputs. The result is the anatomical up direction along the trunk.")]),

(P, "The three axes assemble into the root rotation matrix, whose columns are the frame's axes in the person-space order right, up, forward:"),
(EQ, Rroot + r(" = ") + mat([[xhat, yhat, zhat]]), "3.7"),
(PM, [T("and the right hip position "), X(p24),
      T(" serves as the origin. Together they form the homogeneous transformation of the root, the anchor of the whole chain. Every arm frame in the following sections is expressed relative to this frame.")]),

(PM, [T("A reference configuration pins down what the finished matrix means, and Figure 3.5 shows it: the avatar standing upright, facing the viewer, arms straight out to the sides. This is the T-pose, and it serves as the reference configuration for the whole model: it is the zero of every arm angle in Section 3.3, and it fixes the meaning of the root matrix. An ideal upright person facing the sensor has their right side toward the camera's left and their chest toward the negative z of person space. Substituting these ideal directions gives "),
      X(Rroot), T(" with columns (-1, 0, 0), (0, 1, 0), (0, 0, -1), which decodes to the Euler angles (0, 180, 0) in the convention of Section 3.4: an avatar standing upright, turned 180 degrees to face the viewer. The 180 degree yaw is physically real, not an artifact. This reference test matters because properness alone does not pin down a construction: a wrong ordering of the same axes still forms a perfectly proper rotation matrix, but one whose reference pose decodes to (90, 0, 0), a rig lying flat on its back. The reference pose distinguishes correct anatomy from merely valid algebra.")]),

(IMG, FIG4 + "ch3_fig5_reference_pose.png", 5.6),
(CAP, "Figure 3.5. The reference configuration: the Unity avatar upright and facing the viewer at root Euler angles (0, 180, 0), arms straight out in the T-pose, the zero of all shoulder and elbow angles. The eight streamed landmark points of one frame are drawn beside the rig."),

(H3, "3.2.3 Worked Example"),

(P, "Frame 100 of the evaluation recording (the frame of Figure 3.4) carries the construction through real numbers. The eight landmark positions in both frames are listed in Table 3.1. These are the positions after the filtering of Section 2.1.5, since the filtered stream is what the solver consumes; the raw back-projection of the same frame, carried through for the right wrist in Appendix C, differs from them by a few millimetres, the displacement the filter introduces. One convention applies to this and every later worked example: values are computed at full precision and printed rounded to two decimals, so recomputing a step by hand from the rounded printed inputs can differ from a printed result in the last digit. The three landmarks the root frame needs are, in person space,"),
(MATH, eqArr(
    p23 + r(" = (0.06, −0.02, 1.26)"),
    p24 + r(" = (−0.12, −0.02, 1.27)"),
    p12 + r(" = (−0.16, 0.45, 1.28)"))),

(TBL, [["Landmark", "Camera frame C (m)", "Person space P (m)"],
       ["L11 left shoulder", "(0.16, -0.44, 1.32)", "(0.16, 0.44, 1.32)"],
       ["L12 right shoulder", "(-0.16, -0.45, 1.28)", "(-0.16, 0.45, 1.28)"],
       ["L13 left elbow", "(0.30, -0.29, 1.29)", "(0.30, 0.29, 1.29)"],
       ["L14 right elbow", "(-0.23, -0.23, 1.13)", "(-0.23, 0.23, 1.13)"],
       ["L15 left wrist", "(0.34, -0.19, 1.07)", "(0.34, 0.19, 1.07)"],
       ["L16 right wrist", "(-0.07, -0.16, 0.99)", "(-0.07, 0.16, 0.99)"],
       ["L23 left hip", "(0.06, 0.02, 1.26)", "(0.06, -0.02, 1.26)"],
       ["L24 right hip", "(-0.12, 0.02, 1.27)", "(-0.12, -0.02, 1.27)"]]),
(CAP, "Table 3.1. The eight landmarks of frame 100 in the camera frame and in person space, printed to two decimals. The conversion flips only the sign of y. The hips have small negative person-space y because the sensor sits slightly above hip height."),

(P, "The construction needs exactly two vectors from these three points, and both are computed first. Following equation (3.3), the hip line is the difference of the two hip positions,"),
(MATH, p24 + r(" − ") + p23 + r(" = (−0.18, 0.00, 0.02)")),
(P, "with length 0.18 m, a plausible half-pelvis width. Dividing by the length:"),
(MATH, xhat + r(" = ") + frac(r("(−0.18, 0.00, 0.02)"), r("0.18")) + r(" = (−0.99, 0.01, 0.10)")),
(P, "The x component is close to -1: the subject's right points toward the camera's left, as it must for a person facing the sensor. The spine-side vector of equation (3.4) is"),
(MATH, r("s") + r(" = ") + p12 + r(" − ") + p24 + r(" = (−0.03, 0.47, 0.01)")),
(P, "with length 0.48 m, dominated by its upward y component. The cross product of equation (3.5) follows, each component written out:"),
(MATH, eqArr(
    sub(d(xhat + r(" × ") + r("s")), r("x")) + r(" = 0.01 · 0.01 − 0.10 · 0.47 = −0.05"),
    sub(d(xhat + r(" × ") + r("s")), r("y")) + r(" = 0.10 · (−0.03) − (−0.99) · 0.01 = 0.01"),
    sub(d(xhat + r(" × ") + r("s")), r("z")) + r(" = (−0.99) · 0.47 − 0.01 · (−0.03) = −0.47"))),
(P, "with length 0.47. Normalizing gives"),
(MATH, zhat + r(" = (−0.10, 0.01, −0.99)")),
(P, "almost exactly the negative z direction, meaning the chest faces the camera. The second cross product, equation (3.6), closes the frame:"),
(MATH, yhat + r(" = ") + zhat + r(" × ") + xhat + r(" = (0.01, 1.00, 0.01)")),
(P, "a unit vector with no normalization, exactly as claimed. Assembling the columns by equation (3.7):"),
(MATH, Rroot + r(" = ") + mat([
    [r("−0.99"), r("0.01"), r("−0.10")],
    [r("0.01"), r("1.00"), r("0.01")],
    [r("0.10"), r("0.01"), r("−0.99")]])),
(P, "Decoding this matrix with equation (3.10) of Section 3.4, using its entries symbolically so the full-precision values carry through:"),
(MATH, eqArr(
    r("x") + r(" = ") + nor("asin") + d(r("−") + sub(r("m"), r("23"))) + r(" = −0.62°"),
    r("y") + r(" = ") + nor("atan2") + d(sub(r("m"), r("13")) + r(", ") + sub(r("m"), r("33"))) + r(" = −174.02°"),
    r("z") + r(" = ") + nor("atan2") + d(sub(r("m"), r("21")) + r(", ") + sub(r("m"), r("22"))) + r(" = 0.47°"))),
(P, "Compared with the reference configuration (0, 180, 0), the subject stands essentially upright, turned about 6 degrees away from dead-on, and that reading agrees with the photograph in Figure 3.4. Recomposing the matrix from the three decoded angles reproduces the assembled matrix to machine precision, confirming the decode is an exact inverse."),

(H2, "3.3 Arm Frames"),

(H3, "3.3.1 Definition of Shoulder, Elbow, and Wrist"),

(P, "With the root established, the model extends outward along each arm as a chain of two rigid segments. For the right arm the landmarks are the right shoulder (L12), right elbow (L14), and right wrist (L16); for the left arm, L11, L13, and L15. The upper arm runs from shoulder to elbow, the forearm from elbow to wrist. Figure 3.6 shows the four segments drawn on the real image of frame 100."),

(IMG, FIG4 + "ch3_fig5_arm_photo.png", 5.6),
(CAP, "Figure 3.6. The four arm segments of frame 100 drawn on the real image: upper arm L12 to L14 and forearm L14 to L16 on the subject's right (left side of the image), and L11 to L13, L13 to L15 on the subject's left."),

(P, "Each joint plays a distinct role. The shoulder connects the torso to the upper arm and carries three rotational degrees of freedom: two that aim the arm in a direction, like pointing a rod, and one that rolls the arm about its own length, like turning a screwdriver. The elbow connects the upper arm to the forearm and is dominated by a single degree of freedom, flexion. The wrist terminates the chain: it defines the direction of the forearm and supplies the reference that makes the shoulder roll observable, but no independent wrist orientation is resolved in this model."),

(P, "A dimension count explains why this set of angles is the natural target. Three landmarks per arm define two segment directions, and a direction contributes two degrees of freedom, so the landmarks of one arm carry exactly four observable rotational degrees of freedom. The model extracts exactly four independent angles per arm: two shoulder swing angles, one shoulder twist, and one elbow flexion. Nothing observable is discarded, and nothing unobservable is invented. The one unobservable motion is also worth naming: rotation of the forearm about its own axis (pronation) would need a hand landmark to detect, and is not modeled."),

(H3, "3.3.2 Establishing Local Arm Frames"),

(P, "A central principle of the chain is that no joint rotation is ever measured in isolation; each is measured relative to its parent frame. The shoulder is measured relative to the torso, and the elbow relative to the rotated upper arm. This makes the angles meaningful for driving an avatar: an elbow angle describes how the forearm is bent relative to the upper arm, not relative to the room."),

(PM, [T("The shoulder's parent frame is placed as follows: a frame with the same orientation as the torso frame, with its origin moved to the shoulder landmark L12. In other words, the L12 frame is the root orientation "),
      X(Rroot),
      T(" translated up the trunk. No separate orientation is derived at the shoulder, and deliberately so: three torso landmarks define one rigid orientation, and a second basis at the shoulder would add a shoulder-girdle degree of freedom that the data cannot support. The rest configuration is the T-pose of Figure 3.5, the reference configuration of this model: with the shoulder angles at zero, the right upper arm extends along the frame's +x axis, straight out to the subject's right.")]),

(PM, [T("The elbow's parent is the upper arm itself, so its frame is the fully rotated arm frame: orientation "),
      X(Rroot),
      T(" composed with the solved shoulder rotation, origin at the elbow landmark L14. This is the same device used in the classic Puma robot model, where several wrist frames share one origin and each new frame is the previous one carried through the joint rotation [41]. In the rest configuration the forearm continues the arm axis, along the local +x of the elbow frame; a straight arm is the zero of elbow flexion. Figure 3.3 showed all three frames in place on the mannequin.")]),

(PM, [T("Expressing a measured segment in its parent frame always follows the same two-step pattern. First the segment is formed as a vector between two landmarks; for the right upper arm, "),
      X(r("v") + r(" = ") + p14 + r(" − ") + p12),
      T(". Then the vector is pulled into the parent frame by the pullback of equation (3.2): "),
      X(sub(r("v"), nor("local")) + r(" = ") + RrootT + r(" ") + r("v")),
      T(". Written out, each component of "), X(sub(r("v"), nor("local"))),
      T(" is the dot product of "), X(r("v")),
      T(" with one torso axis, so the operation re-describes the arm in the body's own directions: how much of the segment points to the subject's right, how much up, how much forward. This local vector is what the joint angles are extracted from. The extraction itself is the subject of Section 3.4; the picture to hold is a ball joint like a joystick: the measured local vector says where the stick points, and the solver works backwards to the angles that put it there.")]),

(H3, "3.3.3 Worked Example"),

(P, "Continuing frame 100 on the right arm. The person-space upper arm vector is"),
(MATH, eqArr(
    r("v") + r(" = ") + p14 + r(" − ") + p12 +
    r(" = (−0.23, 0.23, 1.13) − (−0.16, 0.45, 1.28)"),
    r("= (−0.07, −0.22, −0.15)"))),
(P, "with length 0.28 m, a plausible upper-arm length. Its components say the elbow sits slightly toward the subject's left of the shoulder in camera terms, well below it, and closer to the camera. Pulling the vector into the parent frame by equation (3.2), each component becomes a dot product with one column of the root matrix:"),
(MATH, sub(r("v"), nor("local")) + r(" = ") + RrootT + r(" ") + r("v") + r(" = (0.05, −0.22, 0.16)")),
(PM, [T("The re-description is anatomical: the upper arm points slightly across the body (+x is the subject's right), strongly downward (negative y), and forward (positive z). That is exactly the visible pose in Figure 3.6, an arm hanging down and reaching forward to hold the object. The pullback is a rotation, so the length 0.28 is unchanged, and dividing by it gives the local arm direction "),
      X(ahat), T(":")]),
(MATH, ahat + r(" = ") + frac(sub(r("v"), nor("local")), r("0.28")) + r(" = (0.19, −0.81, 0.56)")),
(PM, [T("The same two steps applied to the forearm give the forearm vector "),
      X(r("f")), T(" in the parent frame,")]),
(MATH, r("f") + r(" = ") + RrootT + r(" ") + d(p16 + r(" − ") + p14) + r(" = (−0.17, −0.07, 0.12)")),
(P, "with length 0.22 m. These two local vectors are the complete input to the right-arm angle computation in the next section; nothing else about the pose is needed."),

(H2, "3.4 Joint Angle Computation"),

(P, "The angles transmitted to the reconstruction follow the Euler convention of the Unity animation system, the consumer described in Section 3.5. A bone's three Euler angles are applied in a fixed order: first the z rotation, then the x rotation, then the y rotation, each about the parent frame's axes. As a matrix product acting on column vectors, the rotation applied first sits nearest the vector, so the convention reads"),
(EQ, r("R") + r(" = ") + Rot("y", r("y")) + r(" ") + Rot("x", r("x")) + r(" ") + Rot("z", r("z")), "3.8"),
(PM, [T("where "), X(sub(r("R"), r("x"))), T(", "), X(sub(r("R"), r("y"))), T(", "), X(sub(r("R"), r("z"))),
      T(" are the elementary rotations about the coordinate axes. Figure 3.7 shows the order applied one elementary rotation at a time. Multiplying the three matrices symbolically (writing c and s for cosine and sine) gives the full matrix used throughout this section:")]),
(EQ, r("R") + r(" = ") + mat([
    [cs("c","y")+cs("c","z")+r(" + ")+cs("s","y")+cs("s","x")+cs("s","z"),
     r("−")+cs("c","y")+cs("s","z")+r(" + ")+cs("s","y")+cs("s","x")+cs("c","z"),
     cs("s","y")+cs("c","x")],
    [cs("c","x")+cs("s","z"), cs("c","x")+cs("c","z"), r("−")+cs("s","x")],
    [r("−")+cs("s","y")+cs("c","z")+r(" + ")+cs("c","y")+cs("s","x")+cs("s","z"),
     cs("s","y")+cs("s","z")+r(" + ")+cs("c","y")+cs("s","x")+cs("c","z"),
     cs("c","y")+cs("c","x")]]), "3.9"),

(IMG, FIG + "ch3_fig7_zxy_order.png", 6.3),
(CAP, "Figure 3.7. The Euler convention built one elementary rotation at a time: starting from identity, the z angle is applied first, then x, then y, all about parent axes, giving R = Ry Rx Rz."),

(PM, [T("The structure of this matrix makes angle extraction possible. Write "),
      X(sub(r("m"), r("ij"))),
      T(" for the entry of a measured numerical matrix "), X(r("m")),
      T(" in row i, column j. The entry "), X(sub(r("m"), r("23"))),
      T(" is simply "), X(r("−") + cs("s", "x")),
      T(", isolating the x angle. Once x is known, the third column isolates y, and the second row isolates z:")]),
(EQ, r("x") + r("=") + nor("asin") + d(r("−")+sub(r("m"),r("23"))) + r(", ") +
     r("y") + r("=") + nor("atan2") + d(sub(r("m"),r("13"))+r(",")+sub(r("m"),r("33"))) + r(", ") +
     r("z") + r("=") + nor("atan2") + d(sub(r("m"),r("21"))+r(",")+sub(r("m"),r("22"))), "3.10"),
(PM, [T("The two-argument arctangent inspects the signs of both arguments and returns the angle in the correct quadrant over the full circle; a plain arctangent covers only half the circle. The arcsine restricts x to the range -90 to +90 degrees. When x reaches either end of that range ("),
      X(d(sub(r("m"), r("23")), "|", "|") + r(" = 1")),
      T("), the y and z rotations turn about the same effective axis and only their combined angle is defined; this configuration is called gimbal lock. The decode stays well defined there by convention: z is set to zero and y carries the whole combined rotation. On the real recording the decode and recompose round trip agrees to machine precision, and it is exact at synthetic poses placed at the singularity itself.")]),

(H3, "3.4.1 Torso Pose"),

(PM, [T("The torso needs no solving at all, and the reason is worth stating. The torso is not a joint: it has no angles of its own. Its pose is completely described by the plane orientation and location already constructed in Section 3.2, the pair "),
      X(d(Rroot + r(", ") + p24)),
      T(". Applying the decode of equation (3.10) to "), X(Rroot),
      T(" gives the three angles of the torso; the frame 100 decode of (-0.62, -174.02, 0.47) degrees in Section 3.2.3 was computed exactly this way. How these angles drive the avatar root is shown numerically in Section 3.5.1.")]),

(P, "The decode was validated before any real data was used. A synthetic rigid body was swept through known yaw, pitch, roll, and combined rotations, exported in sensor space in the extractor's own output format, and pushed through the complete pipeline: the decoded angles match the injected truth to 1.1e-13 degrees over all 900 frames."),

(H3, "3.4.2 Shoulder Orientation"),

(P, "The shoulder must reproduce two different things at once: where the upper arm points, and how the arm is rolled about its own length. The physical split is swing (the aiming part) and twist (the roll part) [42]. The parameterization used here writes the shoulder rotation as three elementary rotations with the twist innermost:"),
(EQ, Rsh + r(" = ") + Rot("y", t_("y")) + r(" ") + Rot("z", t_("z")) + r(" ") + Rot("x", t_("t")), "3.11"),
(PM, [T("where "), X(t_("y")), T(" and "), X(t_("z")),
      T(" are the swing angles and "), X(t_("t")),
      T(" is the twist about the rest arm axis +x. The order is forced by a simple observation: a rotation about x leaves the x axis itself fixed. With the twist innermost, applying "),
      X(Rsh), T(" to the rest arm direction "), X(xhat),
      T(" removes the twist factor immediately,")]),
(EQ, ahat + r(" = ") + Rsh + r(" ") + xhat + r(" = ") +
     Rot("y", t_("y")) + r(" ") + Rot("z", t_("z")) + r(" ") + xhat + r(" = ") +
     d(cs("c","y")+cs("c","z") + r(",  ") + cs("s","z") + r(",  −") + cs("s","y")+cs("c","z")), "3.12"),
(P, "so the upper-arm direction depends on the swing alone, and the twist is exactly the roll about the arm that the elbow position cannot see. If the twist were outermost instead, the twist axis would stop being the arm axis as soon as the arm swings, and the decomposition would lose its physical meaning. Two consequences follow. First, the twist is invisible in the shoulder-to-elbow vector and must be measured from a second segment, the forearm. Second, this joint order is not the transmitted Euler order; driving the rig requires composing the matrix and re-extracting angles with equation (3.10), carried out in Section 3.5.2. Figure 3.8 illustrates both halves of the decomposition."),

(IMG, FIG4 + "ch3_fig6_swing_twist.png", 6.3),
(CAP, "Figure 3.8. The swing-twist decomposition. (a) The swing aims the rest arm +x into the observed direction a_hat; the direction drawn is the measured frame 100 arm direction. (b) The twist rolls about the arm axis; it is measured in the plane perpendicular to that axis, after the swing has been undone."),

(PM, [T("The swing solve reads the components of "), X(ahat),
      T(" directly. Its y component is "), X(cs("s", "z")), T(", so")]),
(EQ, t_("z") + r(" = ") + nor("asin") + d(sub(r("a"),r("y"))), "3.13"),
(PM, [T("the elevation of the arm, positive upward, restricted to -90 to +90 degrees. The x and z components share the factor "),
      X(cs("c", "z")), T(", which cancels in the two-argument arctangent:")]),
(EQ, t_("y") + r(" = ") + nor("atan2") + d(r("−")+sub(r("a"),r("z"))+r(", ")+sub(r("a"),r("x"))), "3.14"),
(PM, [T("the azimuth of the arm, positive sweeping backward. Every direction of the arm is reachable by some pair of swing angles, so there is no coverage gap. The one degenerate configuration is the arm pointing straight up or straight down ("),
      X(t_("z") + r(" = ±90°")),
      T("): there the x and z components both vanish and the azimuth is undefined. The convention "),
      X(t_("y") + r(" = 0")),
      T(" is applied, and any axial rotation folds into the twist automatically. A synthetic pose generated with swing (30, 90) decodes as (0, 90, 30), a different set of numbers describing the identical physical pose, and the recomposed arm direction confirms it.")]),

(P, "The twist solve must measure rotation about the arm axis, and rotation about an axis is only visible in the plane perpendicular to that axis. The procedure therefore first undoes the swing, bringing the arm axis back onto +x, so that the perpendicular plane becomes exactly the local y-z plane:"),
(EQ, r("f′") + r(" = ") + Rot("z", r("−")+t_("z")) + r(" ") + Rot("y", r("−")+t_("y")) + r(" ") + r("f"), "3.15"),
(PM, [T("where "), X(r("f")),
      T(" is the forearm vector in the parent frame from Section 3.3.2. The zero convention is anatomical: at zero twist, the forearm's perpendicular component points along local +z, meaning the elbow flexes forward. Under a twist "),
      X(t_("t")), T(", that component rotates to "),
      X(d(r("−") + nor("sin ") + t_("t") + r(", ") + nor("cos ") + t_("t"))),
      T(" in the (y, z) plane, so the twist reads")]),
(EQ, t_("t") + r(" = ") + nor("atan2") + d(r("−")+sub(r("f′"),r("y"))+r(", ")+sub(r("f′"),r("z"))), "3.16"),
(P, "positive for internal rotation (the forearm rotating downward from forward). The twist solve was validated against synthetic known twists of up to 80 degrees, with a maximum decode error of 8.5e-14 degrees over 900 frames, including trials where the torso rotates at the same time."),

(PM, [T("For the left arm no new derivation is needed. Left angles are defined through the sagittal mirror: both left segment vectors are expressed in the root basis, their x components are flipped with "),
      X(r("M") + r(" = ") + nor("diag") + d(r("−1, 1, 1"))),
      T(", and the identical right-arm solve runs on the result. Because the mirror preserves the whole construction, every property above carries over unchanged, and a mirror-symmetric pose produces identical angle values on both sides with the same anatomical meaning: positive "),
      X(t_("y")), T(" sweeps backward, positive "), X(t_("z")),
      T(" raises the arm, positive "), X(t_("t")), T(" rotates internally.")]),

(H3, "3.4.3 Elbow Flexion and Extension"),

(PM, [T("The elbow is solved in the L14 frame established in Section 3.3.2: the fully rotated arm frame "),
      X(sub(r("R"), nor("arm")) + r(" = ") + Rroot + Rot("y", t_("y")) + Rot("z", t_("z")) + Rot("x", t_("t"))),
      T(", in which the rest forearm continues the arm axis along +x. The forearm direction in this frame is "),
      X(ghat + r(" = ") + sup(sub(r("R"), nor("arm")), r("T")) + d(p16 + r(" − ") + p14)),
      T(", normalized, and the same swing parameterization as the shoulder applies:")]),
(EQ, sub(r("e"),r("z")) + r(" = ") + nor("asin") + d(sub(r("g"),r("y"))) + r(",      ") +
     sub(r("e"),r("y")) + r(" = ") + nor("atan2") + d(r("−")+sub(r("g"),r("z"))+r(", ")+sub(r("g"),r("x"))), "3.17"),
(PM, [T("with "), X(sub(r("e"), r("y")) + r(" = 0")), T(" a straight arm and "),
      X(sub(r("e"), r("y")) + r(" = −90")), T(" a right angle bend.")]),

(PM, [T("One structural fact simplifies the solve: "), X(sub(r("e"), r("z"))),
      T(" is identically zero. The shoulder twist was defined as exactly the rotation that aligns the forearm's perpendicular component with local +z, so by the time the elbow is solved, the flexion plane has already been rotated into the x-z plane of the elbow frame. The elbow's out-of-plane freedom is not lost; it is the shoulder twist, already accounted one joint earlier. This closes the dimension count of Section 3.3.1: four observable degrees of freedom, four independent angles. The angle "),
      X(sub(r("e"), r("z"))),
      T(" is kept in the data interface for generality but carries no independent information. Elbow flexion stays in the anatomical range "),
      X(sub(r("e"), r("y"))),
      T(" between -180 and 0 on all 899 real frames.")]),

(PM, [T("The elbow also exposes the one genuine degeneracy of a three-landmark arm. When the arm is perfectly straight, the forearm is parallel to the upper arm, its perpendicular component vanishes, and the shoulder twist becomes unobservable; no algebra can recover a roll about an axis from two collinear segments. The solver detects the condition by thresholding the perpendicular fraction of the forearm, applies the convention "),
      X(t_("t") + r(" = 0")),
      T(" so the elbow frame stays defined, and flags the twist as unobservable so that downstream processing holds the last valid value instead of trusting a numerical accident. Near-straight elbows leave the flexion angle well conditioned but make the twist sensitive to noise; this is quantified as a practical limitation in Chapter 8.")]),

(H3, "3.4.4 Wrist Rotation"),

(P, "The wrist is the terminal landmark of the chain. In this model it serves two purposes: it defines the forearm direction that the elbow flexion is read from, and it supplies the reference that makes the shoulder twist observable. A full three-degree-of-freedom wrist orientation is deliberately not resolved. The missing ingredient is a landmark beyond the wrist: forearm pronation, the roll of the forearm about its own axis, produces no motion of the wrist point at all, so no algebra over these landmarks can observe it. Resolving hand orientation is the province of hand-specific models such as [15], which this framework is structured to accept downstream without changing the arm chain: the wrist position is retained and transmitted so the terminal point of each arm is correctly placed in the reconstructed scene."),

(H3, "3.4.5 Worked Example"),

(PM, [T("The per-stage numbers of frame 100 now assemble into the complete solve. From Sections 3.2.3 and 3.3.3, the root decodes to Euler (-0.62, -174.02, 0.47) and the right-arm local vectors are "),
      X(ahat + r(" = (0.19, −0.81, 0.56)")), T(" and "),
      X(r("f") + r(" = (−0.17, −0.07, 0.12)")),
      T(". The swing solve of equations (3.13) and (3.14) reads")]),
(MATH, eqArr(
    t_("z") + r(" = ") + nor("asin") + d(r("−0.81")) + r(" = −53.72°"),
    t_("y") + r(" = ") + nor("atan2") + d(r("−0.56, 0.19")) + r(" = −71.12°"))),
(P, "the arm is dropped 54 degrees below horizontal and swung 71 degrees forward of the T-pose, which is exactly the reaching-down-and-forward pose visible in Figure 3.6. Undoing this swing on the forearm vector by equation (3.15) gives"),
(MATH, r("f′") + r(" = ") + Rot("z", r("53.72°")) + r(" ") + Rot("y", r("71.12°")) + r(" ") + r("f") + r(" = (0.09, 0.01, 0.20)")),
(P, "its perpendicular part is almost purely +z, so the twist of equation (3.16) is small:"),
(MATH, t_("t") + r(" = ") + nor("atan2") + d(r("−0.01, 0.20")) + r(" = −1.88°")),
(P, "In the elbow frame the forearm direction is"),
(MATH, ghat + r(" = (0.41, 0.00, 0.91)")),
(PM, [T("Its y component is zero, the "),
      X(sub(r("e"), r("z")) + r(" = 0")),
      T(" property arriving on real data, and the flexion of equation (3.17) is")]),
(MATH, sub(r("e"), r("y")) + r(" = ") + nor("atan2") + d(r("−0.91, 0.41")) + r(" = −65.68°")),
(P, "a comfortable working bend. The left arm runs through the identical mirrored solve and yields shoulder (-3.45, -44.57, 5.77) and elbow -59.85 degrees: raised less, swung forward barely, also bent to hold the object. Thirteen numbers (three root Euler angles, then swing, twist, and flexion for each arm, with the zero elbow angle carried for generality) now describe the entire measured pose of frame 100."),

(P, "Every solve in this chapter was validated against six synthetic ground-truth datasets with known injected angle trajectories: root sweeps, shoulder swings and twists with and without simultaneous torso motion, elbow flexion with a rotating flexion plane, the full arm, and both arms together with twelve angles nonzero. Each dataset synthesizes landmarks in sensor space through the extractor's exact data format and pushes them through the full pipeline; the worst decode error across all six is 2.8e-13 degrees, floating-point noise, so the solve is an exact inverse of the construction. Real recordings close the loop: with no injected truth available, correctness on real data means the frame invariants hold on every one of the 899 frames, the solved angles reconstruct both measured segment directions (worst frame 6.4e-14 degrees), and the numbers stay physically plausible, with elbow flexion never leaving its anatomical range."),

(H2, "3.5 Mapping to the Unity Avatar"),

(P, "The angles of Section 3.4 exist to drive a graphical avatar. This section collects the complete mapping from the solved kinematics to the Unity rig: first the torso, whose orientation and position anchor the whole character, then the arm chain. The numerical thread of frame 100 continues throughout, so every step of the mapping is shown on real data."),

(H3, "3.5.1 Torso: Driving the Avatar Root"),

(PM, [T("Unity's animation interface consumes Euler angles rather than matrices, in the z, x, y order of equation (3.8), so the root matrix is transmitted as its decode. For frame 100 the decode of "),
      X(Rroot),
      T(" gave (-0.62, -174.02, 0.47) degrees. Applied to the rig's hip bone, these three numbers reproduce the measured torso plane exactly: the avatar stands nearly upright, turned to face the viewer, matching the photograph of Figure 3.4. The root bone is additionally translated so the hip lands on the streamed pelvis point "),
      X(p24),
      T(", and a uniform scale sizes the character to the subject; the scale commutes with every rotation, so scaling never disturbs the angles.")]),

(P, "The full path from synthetic landmark input through the frame construction, the Euler decode, and the rig was validated end to end: the rig was driven with the decoded angles of the synthetic root datasets and captured at known poses. Figure 3.9 shows four of them, each reproducing the injected angles."),

(IMG, FIG + "ch3_fig8_root_stills.png", 6.0),
(CAP, "Figure 3.9. The Unity rig holding known root poses from the synthetic validation dataset: (a) the reference pose, Euler (0, 180, 0), upright facing the viewer; (b) yaw +30; (c) pitch +20, a bow; (d) roll +20, a sideways lean."),

(H3, "3.5.2 Arms: From Joint Angles to Bone Rotations"),

(P, "Driving the arm chain is one further composition per bone. The world rotation applied to a bone is"),
(EQ, sub(r("R"), nor("bone")) + r(" = ") + sub(r("q"), r("A")) + r(" ") +
     sub(r("R"), nor("chain")) + r(" ") + sub(r("C"), nor("rest")), "3.18"),
(PM, [T("where "), X(sub(r("R"), nor("chain"))),
      T(" is the solved chain up to that bone ("), X(Rroot),
      T(" for the hips, "), X(Rroot + r(" ") + Rsh),
      T(" for the upper arm, and the elbow rotation appended for the forearm), "),
      X(sub(r("C"), nor("rest"))),
      T(" is the bone's authored rest rotation captured once at startup (it absorbs the character model's own axis conventions, including the rig's built-in 8 degree arm droop, as a constant), and "),
      X(sub(r("q"), r("A"))),
      T(" is the world anchor of the integrated scene of Chapter 5 (identity in the standalone scene). The anchor multiplies from the left, outside the chain. On the left side, the mirror identities "),
      X(r("M") + Rot("y", r("t")) + r("M") + r(" = ") + Rot("y", r("−t"))),
      T(", "),
      X(r("M") + Rot("z", r("t")) + r("M") + r(" = ") + Rot("z", r("−t"))),
      T(", "),
      X(r("M") + Rot("x", r("t")) + r("M") + r(" = ") + Rot("x", r("t"))),
      T(" mean the left chain is the right chain with the y and z angle signs flipped and the twist sign kept, applied to a rest arm along -x.")]),

(PM, [T("The frame 100 thread completes here. The solved right-shoulder joint angles "),
      X(d(t_("y") + r(", ") + t_("z") + r(", ") + t_("t")) + r(" = ") + d(r("−71.12, −53.72, −1.88"))),
      T(" compose into "),
      X(Rsh + r(" = ") + Rot("y", r("−71.12°")) + Rot("z", r("−53.72°")) + Rot("x", r("−1.88°"))),
      T(" by equation (3.11), and re-extracting in the transmitted order by equation (3.10) gives the shoulder Euler angles (-1.11, -69.61, -53.73). The recomposed matrix maps the rest arm exactly onto the measured direction "),
      X(ahat),
      T(", and the elbow streams its flexion of -65.68 degrees directly. These are the numbers the packet of Chapter 5 carries for this frame.")]),

(P, "Figures 3.10 to 3.12 capture the rig at validated poses across the angle space: the shoulder twist extremes, the straight-elbow degeneracy, and the hardest single pose of the synthetic sets, with every right-side angle nonzero at once."),

(IMG, FIG + "ch3_fig9_twist_stills.png", 6.3),
(CAP, "Figure 3.10. The rig at known shoulder twists from the synthetic validation set. (a) Zero twist at the rest pose: elbow bent, forearm toward the camera. (b) Twist +90 (internal rotation): the forearm hangs straight down. (c) Twist -90 (external rotation): the forearm points straight up."),

(IMG, FIG + "ch3_fig10_elbow_straight.png", 4.6),
(CAP, "Figure 3.11. The rig holding the synthetic straight-elbow pose (e_y = 0): the forearm continues the upper-arm axis, reproduced to 0.02 degrees. At this configuration the shoulder twist is unobservable from landmarks and is held by convention."),

(IMG, FIG + "ch3_fig11_arm_full.png", 5.2),
(CAP, "Figure 3.12. The rig holding frame 742 of the full-arm validation dataset, with every right-side angle nonzero at once: root (8.0, -171.7, 5.8), shoulder swing-twist (27.8, 30.0, 32.4), elbow -100.4. Both displayed bone directions match the dataset's landmark directions to four decimal places."),

(P, "One further measurement pins the final step of the chain. The Unity rig itself was instrumented to log its four arm-segment directions on every displayed frame and compare them against independent predictions from the solved angles. Across 897 displayed frames the mean angular error is 0.0000 degrees and the maximum is 0.0001 degrees, the quantization floor of the 32-bit packet format. The chain from landmarks to angles to rendered bones is exact end to end; whatever error the reconstructed motion carries comes from the measurements, not from the model."),

]

references = {
9:  'L. Keselman, J. Iselin Woodfill, A. Grunnet-Jepsen, and A. Bhowmik, "Intel RealSense stereoscopic depth cameras," in Proc. IEEE Conf. Computer Vision and Pattern Recognition Workshops (CVPRW), 2017.',
15: 'Y. Dong and S. Payandeh, "Toward tracking and reconstruction of grasping hand kinematics: A framework based on RGB-D sensing," Applied Sciences, vol. 15, no. 16, art. 8737, 2025.',
39: 'V. Bazarevsky, I. Grishchenko, K. Raveendran, T. Zhu, F. Zhang, and M. Grundmann, "BlazePose: On-device real-time body pose tracking," arXiv:2006.10204, 2020.',
41: 'J. J. Craig, Introduction to Robotics: Mechanics and Control, 3rd ed. Upper Saddle River, NJ, USA: Pearson Prentice Hall, 2005.',
42: 'P. Dobrowolski, "Swing-twist decomposition in Clifford algebra," arXiv:1506.05481, 2015.',
}

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
        doc.add_picture(item[1], width=Inches(item[2]))
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

out = "/home/luo/Desktop/New_SandBox/writing/v6/Chapter_3_Kinematic_Modeling.docx"
doc.save(out)
print("saved", out)

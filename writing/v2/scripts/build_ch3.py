#!/usr/bin/env python3
"""Build writing/v2/Chapter_3_Kinematic_Modeling.docx.

All numbers computed by running the implemented solver (kinematics/root_frame.py,
kinematics/shoulder.py) on pinned data; see writing/v2/scripts/ch3_numbers.py.
"""
from docx import Document
from docx.shared import Pt, Inches

FIG = "/home/luo/Desktop/New_SandBox/writing/v2/figures/"
H1, H2, H3, P, IMG, CAP, TBL = "h1", "h2", "h3", "p", "img", "cap", "tbl"

content = [
(H1, "Chapter 3: Kinematic Modeling"),

(P, "The previous chapter ended with eight body landmarks per frame, each lifted to a metric 3D position in the camera frame. Those positions are an unstructured cloud of points. On their own they say nothing about how the body segments are oriented relative to one another, or about how each joint has rotated between one frame and the next. This chapter introduces the kinematic model that gives the points structure. The model is organised as a hierarchical chain of coordinate frames, rooted at the pelvis and extending outward through the shoulder and elbow of each arm, following the hierarchical modeling principle established for the hand by [15]. Once the chain is built, the pose of the body reduces to a small set of anatomical joint angles: the orientation and position of the torso, a swing and twist for each shoulder, and a flexion angle for each elbow. These angles are exactly what the Unity animation system consumes."),

(P, "Three properties distinguish the model developed here. First, it is closed form: every angle is computed directly from the landmark geometry of the current frame, with no optimisation and no temporal state. Second, it is an exact inverse: the solved angles reconstruct the measured segment directions to machine precision, which turns validation into a strict test rather than a curve fit. Third, every construction was verified against synthetic recordings with known injected angles before it was trusted on real data; those verification results appear alongside the derivations throughout the chapter. The chapter proceeds in the order of the chain itself: the mathematical tools first, then the torso root frame, then the arm frames, and finally the resolution of the joint angles, with a numerical work example closing each stage."),

(H2, "3.1 Kinematic Foundations"),

(H3, "3.1.1 Coordinate Systems and Transformations"),

(P, "A coordinate frame is an origin point together with three mutually perpendicular unit vectors, labelled x, y, and z, that define the directions of the three axes. Any point in space is described by how far one must travel along each axis direction, starting from the origin, to reach it. The entire kinematic model is built from such frames: one is attached to each body segment, and when a segment moves, its frame moves with it. The orientation of one segment relative to another is then captured entirely by the relationship between their two frames. Being precise about which frame a number lives in is the single most important bookkeeping rule of this chapter, so the two frames that bracket the whole system are defined first."),

(P, "Every measurement produced by the sensing stage of Chapter 2 is expressed in the camera frame of the RealSense sensor, denoted C. This frame is right-handed: x points to the right in the image, y points downward, and z points forward from the sensor into the scene [9]. The z coordinate of a point in this frame is exactly the depth measure reported by the sensor. The reconstruction environment uses a different convention: Unity's frame is left-handed with y pointing up. Figure 3.1 shows the two conventions side by side, the camera frame drawn on the sensor and the Unity frame drawn on a screenshot of the Unity scene."),

(IMG, FIG + "ch3_fig1_sensor_unity.png", 6.3),
(CAP, "Figure 3.1. (a) The D435 camera frame C, drawn on the sensor: x right in the image, y down, z out of the sensor into the scene (the depth direction). (b) The Unity frame U, drawn on a screenshot of the reconstruction scene: x right, y up, z forward, left-handed."),

(P, "A right-handed and a left-handed frame have opposite orientations, so the handedness itself must change during the conversion, not just the labels of the axes. The conversion used throughout this work is a single matrix multiplication applied to every measured point. If p is a landmark position in the camera frame, its position q in the person space P used by all the kinematic math is"),
(P, "q = F p,        F = diag(1, -1, 1),"),
(P, "that is, the y coordinate flips sign and x and z pass through unchanged. Flipping exactly one axis is precisely what converts a right-handed frame to a left-handed one: the determinant of F is -1, the signature of a reflection. After the flip, x still points to the right in the image, y now points up, and z still points away from the camera, which matches Unity's convention exactly. Both frames keep the same origin at the optical center of the camera; only the reading of the y axis changes. Figure 3.2 shows the two frames drawn from that single shared origin, together with a real measurement: the right wrist of frame 100, the running example frame of Chapter 2, reads (-0.072, -0.164, 0.994) in the camera frame and (-0.072, +0.164, 0.994) in person space. Same physical point, one flipped coordinate."),

(IMG, FIG + "ch3_fig2_colocated.png", 5.2),
(CAP, "Figure 3.2. The camera frame C and person space P drawn from the same origin. Only the y axis differs: the camera reads y downward, person space reads y upward. The wrist landmark of frame 100 is shown with its coordinates in both frames."),

(P, "One rule keeps the handedness bookkeeping trivial for the rest of the chapter: F is applied to points only, never to rotation matrices. Every rotation below is constructed from already flipped points, so no rotation matrix is ever multiplied by a reflection, and every rotation in the pipeline comes out proper, with determinant +1. This is not just a theoretical nicety; the determinant was checked on all 899 frames of the real evaluation recording and equals +1.000000 on every frame. From this point onward, every landmark position in this chapter is a person-space value unless stated otherwise."),

(H3, "3.1.2 Homogeneous Transformation Matrices"),

(P, "The relationship between two coordinate frames consists of two pieces of information: how the child frame is rotated relative to the parent, and where the child's origin sits in the parent's coordinates. Together they form a rigid body transformation, an operation that moves and turns an object without deforming it [41]."),

(P, "The rotation part is a 3 by 3 matrix R whose three columns are the child frame's axis directions written in the parent's coordinates: the first column is the child's x axis as seen from the parent, the second its y axis, the third its z axis. Because the columns are unit vectors that are mutually perpendicular, R has a special property: its transpose equals its inverse, R^T R = I, and its determinant equals one. This property is used constantly in what follows, because it means a vector expressed in the parent frame is brought into the child frame by multiplying with R^T, with no numerical matrix inversion ever needed."),

(P, "The translation part is a 3-vector t giving the position of the child's origin in the parent frame. Rotation and translation combine into a single 4 by 4 homogeneous transformation matrix T, whose top-left 3 by 3 block is R, whose top-right column is t, and whose bottom row is (0, 0, 0, 1). A point is transformed by appending a 1 to its coordinates and multiplying: the result is R p + t, the point rotated and then shifted, which is exactly a rigid body motion performed in one multiplication."),

(P, "The value of this representation appears when transformations chain. If T1 describes the torso frame relative to person space and T2 describes a shoulder frame relative to the torso, then the product T1 T2 describes the shoulder frame directly in person space. Rotations defined locally, each relative to its immediate parent, accumulate into a single description of the whole arm. The same property runs in reverse during angle resolution: given a measured segment direction in person space and the known orientation R_parent of its parent frame, the segment's direction in the parent frame is R_parent^T times the measured vector. That single operation, pulling a measured vector back into a local frame, is the heart of every derivation in Section 3.4. Figure 3.3 sketches the chain on a mannequin, with the three frames of the right arm chain drawn at their anatomical origins."),

(IMG, FIG + "ch3_fig3_chain_mannequin.png", 5.8),
(CAP, "Figure 3.3. The kinematic chain drawn on a mannequin, front view (the subject faces the sensor, so the subject's right side appears on the left of the image). The root frame sits at the right hip L24; the L12 shoulder frame has the same orientation as the root with its origin moved to L12; the L14 elbow frame is the fully rotated arm frame, with x continuing the upper-arm axis."),

(H2, "3.2 Torso Reference Frame"),

(H3, "3.2.1 Landmark Selection"),

(P, "The torso frame is the root of the entire upper-body chain: every other frame is expressed, directly or through the chain, in terms of this one. It is constructed from three MediaPipe landmarks [39]: the right hip (L24), the left hip (L23), and the right shoulder (L12). Throughout this thesis, left and right always mean the subject's own left and right; since the subject faces the sensor, the subject's right side appears on the left of the camera image."),

(P, "Three considerations drive this selection. The hips and shoulders are the most stable landmarks during manipulation tasks: they move slowly and are rarely hidden by the manipulated object, unlike the hands and forearms. Three points are also the minimum that defines a plane, and a plane is what is needed to fix a full three-axis orientation; two points would give only a single direction. And the three chosen landmarks span a broad triangle across the trunk, so small measurement errors in any one landmark have a proportionally small effect on the computed axes."),

(P, "One assumption should be stated explicitly before the construction. With only three torso points, the model cannot separate the pelvis from the upper trunk. It therefore assumes that there is no relative twist between the shoulders and the hips: the whole torso is treated as one rigid plate whose orientation is what the frame captures. A consequence is that a forward lean of the trunk pitches the root frame with it. This simplification is accepted for the present model and is revisited in the limitations of Chapter 8."),

(H3, "3.2.2 Derivation of Torso Frame"),

(P, "The three landmark positions arrive from Chapter 2 in the camera frame and are converted to person space by the flip F of Section 3.1.1; the construction below happens entirely in person space. Let p23, p24, and p12 denote the person-space positions of the left hip, right hip, and right shoulder. The torso is not a joint and has no joint angles; what this section derives is the orientation and location of the torso plane, packaged as a rotation matrix and an origin. Figure 3.4(a) shows the two input vectors drawn on the real image of frame 100, and Figure 3.4(b) shows the finished frame projected back onto the same image."),

(IMG, FIG + "ch3_fig4_torso_photo.png", 6.3),
(CAP, "Figure 3.4. The torso frame on the real image of frame 100. (a) The two input vectors: the hip line from L23 to L24 (red) and the spine-side vector s from L24 up to L12 (yellow). (b) The finished orthonormal frame at the L24 origin, projected through the camera intrinsics: x toward the subject's right, y up along the trunk, z forward out of the chest (foreshortened because it points almost straight at the camera)."),

(P, "The x axis is defined first. It is the unit vector along the hip line, pointing toward the subject's right:"),
(P, "x_hat = (p24 - p23) / |p24 - p23|."),
(P, "No sign correction is needed: subtracting the left-hip position from the right-hip position already produces a vector that points to the subject's right, which is the +x direction of the Unity convention adopted in Section 3.1.1. This axis is kept exactly as measured, because both of its endpoints are pelvis landmarks; the hip line is the one direction the three points define with no ambiguity."),

(P, "The second input is the spine-side vector from the right hip up to the right shoulder,"),
(P, "s = p12 - p24."),
(P, "This vector is deliberately not used as an axis. It is generally not perpendicular to the hip line (in frame 100 the angle between them is 85.4 degrees, not 90), and treating it as an axis would produce a skewed, non-orthogonal frame. Its only job is to select which of the infinitely many planes through the hip line is the torso plane."),

(P, "The z axis comes from the cross product. For two vectors a and b, the cross product a x b is perpendicular to both, with components (a_y b_z - a_z b_y, a_z b_x - a_x b_z, a_x b_y - a_y b_x). Applying it to the two inputs and normalising:"),
(P, "z_hat = (x_hat x s) / |x_hat x s|."),
(P, "The ordering of the two factors is a deliberate choice of sign: with x_hat pointing to the subject's right and s pointing up the trunk, the product x_hat x s points forward, out of the subject's chest toward the camera. Reversing the order would flip the axis into the subject's back. The cross product also automatically discards the part of s that is parallel to x_hat, which is exactly why the imperfect angle between the inputs does no harm: only the component of s perpendicular to the hip line contributes."),

(P, "The y axis closes the frame with a second cross product:"),
(P, "y_hat = z_hat x x_hat."),
(P, "Because z_hat and x_hat are already perpendicular unit vectors, this product is exactly a unit vector, with no normalisation needed. This third step is what guarantees a perfectly orthonormal frame in every measured pose, regardless of the angle between the original inputs: x_hat is exact by construction, z_hat is perpendicular to x_hat by the nature of the cross product, and y_hat is perpendicular to both. The result is the anatomical up direction along the trunk."),

(P, "The three axes assemble into the root rotation matrix, whose columns are the frame's axes in the person-space order right, up, forward:"),
(P, "R_root = [ x_hat | y_hat | z_hat ],"),
(P, "and the right hip position p24 serves as the origin. Together they form the homogeneous transformation of the root, the anchor of the whole chain. Every arm frame in the following sections is expressed relative to this frame."),

(P, "A reference pose pins down what the finished matrix means. An ideal upright person facing the sensor has their right side toward the camera's left and their chest toward the negative z of person space (toward the camera). Substituting these ideal directions gives R_root with columns (-1, 0, 0), (0, 1, 0), (0, 0, -1), which decodes to the Euler angles (0, 180, 0): an avatar standing upright, turned 180 degrees to face the viewer. The 180 degree yaw is physically real, not an artifact. This reference test matters because properness alone does not pin down a construction. An earlier sketch of this frame, which built the axes in a different order, also produced a perfectly proper rotation matrix, but its reference pose decoded to (90, 0, 0): a rig lying flat on its back. The reference pose is what distinguishes correct anatomy from merely valid algebra."),

(H3, "3.2.3 Work Example"),

(P, "Frame 100 of the evaluation recording (the frame of Figure 3.4) carries the construction through real numbers. The eight landmark positions in both frames are listed in Table 3.1; the three the root frame needs are, in person space,"),
(P, "p23 = (0.0593, -0.0222, 1.2549),    p24 = (-0.1225, -0.0207, 1.2745),    p12 = (-0.1560, 0.4538, 1.2831)."),

(TBL, [["Landmark", "Camera frame C (m)", "Person space P (m)"],
       ["L11 left shoulder", "(0.1614, -0.4392, 1.3195)", "(0.1614, 0.4392, 1.3195)"],
       ["L12 right shoulder", "(-0.1560, -0.4538, 1.2831)", "(-0.1560, 0.4538, 1.2831)"],
       ["L13 left elbow", "(0.3040, -0.2946, 1.2946)", "(0.3040, 0.2946, 1.2946)"],
       ["L14 right elbow", "(-0.2269, -0.2325, 1.1318)", "(-0.2269, 0.2325, 1.1318)"],
       ["L15 left wrist", "(0.3396, -0.1945, 1.0719)", "(0.3396, 0.1945, 1.0719)"],
       ["L16 right wrist", "(-0.0718, -0.1638, 0.9938)", "(-0.0718, 0.1638, 0.9938)"],
       ["L23 left hip", "(0.0593, 0.0222, 1.2549)", "(0.0593, -0.0222, 1.2549)"],
       ["L24 right hip", "(-0.1225, 0.0207, 1.2745)", "(-0.1225, -0.0207, 1.2745)"]]),
(CAP, "Table 3.1. The eight landmarks of frame 100 in the camera frame and in person space. The conversion flips only the sign of y. The hips have small negative person-space y because the sensor sits slightly above hip height."),

(P, "The hip line is p24 - p23 = (-0.1819, 0.0015, 0.0196), with length 0.1829 m, a plausible half-pelvis width. Dividing by the length:"),
(P, "x_hat = (-0.9942, 0.0082, 0.1071)."),
(P, "The x component is close to -1: the subject's right points toward the camera's left, as it must for a person facing the sensor. The spine-side vector is s = p12 - p24 = (-0.0334, 0.4745, 0.0086), length 0.4758 m, dominated by its upward y component. The cross product is"),
(P, "x_hat x s = (0.0082 * 0.0086 - 0.1071 * 0.4745,  0.1071 * (-0.0334) - (-0.9942) * 0.0086,  (-0.9942) * 0.4745 - 0.0082 * (-0.0334)) = (-0.0508, 0.0050, -0.4715),"),
(P, "with length 0.4742. Normalising gives z_hat = (-0.1070, 0.0105, -0.9942): almost exactly the negative z direction, meaning the chest faces the camera. The second cross product closes the frame with y_hat = z_hat x x_hat = (0.0093, 0.9999, 0.0095), which comes out a unit vector to ten decimal places with no normalisation, exactly as claimed. Assembling the columns:"),
(P, "R_root = [ -0.9942  0.0093  -0.1070 ;  0.0082  0.9999  0.0105 ;  0.1071  0.0095  -0.9942 ]."),
(P, "The determinant evaluates to 1.000000000000 and the orthonormality residual |R^T R - I| to 3.3e-16, machine precision. Decoding this matrix with the Euler extraction of Section 3.4 gives (x, y, z) = (-0.60, -173.86, 0.47) degrees. Compare the ideal reference pose (0, 180, 0): the subject stands essentially upright (pitch -0.6, roll 0.5) facing the sensor, turned about 6 degrees away from dead-on (yaw -173.9 instead of 180). That reading agrees with the photograph in Figure 3.4, and recomposing the matrix from these three angles reproduces R_root to 2.6e-16, confirming the decode is an exact inverse."),

(H2, "3.3 Arm Frames"),

(H3, "3.3.1 Definition of Shoulder, Elbow, and Wrist"),

(P, "With the root established, the model extends outward along each arm as a chain of two rigid segments. For the right arm the landmarks are the right shoulder (L12), right elbow (L14), and right wrist (L16); for the left arm, L11, L13, and L15. The upper arm runs from shoulder to elbow, the forearm from elbow to wrist. Figure 3.5 shows the four segments drawn on the real image of frame 100."),

(IMG, FIG + "ch3_fig5_arm_photo.png", 5.6),
(CAP, "Figure 3.5. The four arm segments of frame 100 drawn on the real image: upper arm L12 to L14 and forearm L14 to L16 on the subject's right (left side of the image), and L11 to L13, L13 to L15 on the subject's left."),

(P, "Each joint plays a distinct role. The shoulder connects the torso to the upper arm and carries three rotational degrees of freedom: two that aim the arm in a direction, like pointing a rod, and one that rolls the arm about its own length, like turning a screwdriver. The elbow connects the upper arm to the forearm and is dominated by a single degree of freedom, flexion. The wrist terminates the chain: it defines the direction of the forearm and supplies the reference that makes the shoulder roll observable, but no independent wrist orientation is resolved in this model."),

(P, "A dimension count explains why this set of angles is the natural target. Three landmarks per arm define two segment directions, and a direction contributes two degrees of freedom, so the landmarks of one arm carry exactly four observable rotational degrees of freedom. The model extracts exactly four independent angles per arm: two shoulder swing angles, one shoulder twist, and one elbow flexion. Nothing observable is discarded, and nothing unobservable is invented. What cannot be observed is also worth naming: rotation of the forearm about its own axis (pronation) would need a hand landmark to detect, and is not modeled."),

(H3, "3.3.2 Establishing Local Arm Frames"),

(P, "A central principle of the chain is that no joint rotation is ever measured in isolation; each is measured relative to its parent frame. The shoulder is measured relative to the torso, and the elbow relative to the rotated upper arm. This is what makes the angles meaningful for driving an avatar: an elbow angle describes how the forearm is bent relative to the upper arm, not relative to the room."),

(P, "The shoulder's parent frame is placed as follows: a frame with the same orientation as the torso frame, with its origin moved to the shoulder landmark L12. In other words, the L12 frame is the root orientation R_root translated up the trunk. No separate orientation is derived at the shoulder, and deliberately so: three torso landmarks define one rigid orientation, and inventing a second basis at the shoulder would silently introduce a shoulder-girdle degree of freedom that the data cannot support. The rest configuration is a T-pose: with the shoulder angles at zero, the right upper arm extends along the frame's +x axis, straight out to the subject's right."),

(P, "The elbow's parent is the upper arm itself, so its frame is the fully rotated arm frame: orientation R_root composed with the solved shoulder rotation, origin at the elbow landmark L14. This is the same device used in the classic Puma robot model, where several wrist frames share one origin and each new frame is the previous one carried through the joint rotation [41]. In the rest configuration the forearm continues the arm axis, along the local +x of the elbow frame; a straight arm is the zero of elbow flexion. Figure 3.3 showed all three frames in place on the mannequin."),

(P, "Expressing a measured segment in its parent frame always follows the same two-step pattern. First the segment is formed as a vector between two landmarks; for the right upper arm, u = p14 - p12. Then the vector is pulled into the parent frame by the transpose trick of Section 3.1.2: u_local = R_root^T u. Written out, each component of u_local is the dot product of u with one torso axis, so the operation re-describes the arm in the body's own directions: how much of the segment points to the subject's right, how much up, how much forward. This local vector is what the joint angles are extracted from. The extraction itself is the subject of Section 3.4; the picture to hold is a ball joint like a joystick: the measured local vector says where the stick points, and the solver works backwards to the angles that put it there."),

(H3, "3.3.3 Work Example"),

(P, "Continuing frame 100 on the right arm. The person-space upper arm vector is"),
(P, "u = p14 - p12 = (-0.2269, 0.2325, 1.1318) - (-0.1560, 0.4538, 1.2831) = (-0.0709, -0.2212, -0.1513),"),
(P, "with length 0.2773 m, a plausible upper-arm length. Its components say the elbow sits slightly toward the subject's left of the shoulder in camera terms, well below it, and closer to the camera. Pulling the vector into the parent frame, each component becomes a dot product with one column of R_root:"),
(P, "u_local = R_root^T u = (0.0525, -0.2233, 0.1557)."),
(P, "The re-description is anatomical: the upper arm points slightly across the body (+x is the subject's right), strongly downward (negative y), and forward (positive z). That is exactly the visible pose in Figure 3.5, an arm hanging down and reaching forward to hold the object. Normalising gives the local arm direction"),
(P, "a_hat = (0.1894, -0.8055, 0.5615)."),
(P, "The same two steps applied to the forearm give f = R_root^T (p16 - p14) = (-0.1696, -0.0687, 0.1199), length 0.2188 m. These two local vectors are the complete input to the right-arm angle resolution in the next section; nothing else about the pose is needed."),

(H2, "3.4 Joint Angle Resolution"),

(P, "Unity applies a bone's three Euler angles in a fixed order: first the z rotation, then the x rotation, then the y rotation, each about the parent frame's axes. As a matrix product acting on column vectors, the rotation applied first sits nearest the vector, so the convention reads"),
(P, "R = R_y(y) R_x(x) R_z(z),"),
(P, "where R_x, R_y, R_z are the elementary rotations about the coordinate axes. Figure 3.6 shows the order applied one elementary rotation at a time. Multiplying the three matrices symbolically (writing c and s for cosine and sine) gives the full matrix used throughout this section:"),
(P, "R = [ cy cz + sy sx sz,   -cy sz + sy sx cz,   sy cx ;   cx sz,   cx cz,   -sx ;   -sy cz + cy sx sz,   sy sz + cy sx cz,   cy cx ]."),

(IMG, FIG + "ch3_fig7_zxy_order.png", 6.3),
(CAP, "Figure 3.6. Unity's Euler convention built one elementary rotation at a time: starting from identity, the z angle is applied first, then x, then y, all about parent axes, giving R = Ry Rx Rz."),

(P, "The structure of this matrix is what makes angle extraction possible. The entry in row 2, column 3 is simply -sx, isolating the x angle. Once x is known, the third column (sy cx, -sx, cy cx) isolates y, and the second row (cx sz, cx cz, -sx) isolates z. Reading the entries of a measured numerical matrix m:"),
(P, "x = asin(-m23),    y = atan2(m13, m33),    z = atan2(m21, m22),"),
(P, "using 1-based row and column indices. The two-argument arctangent is used instead of a plain arctangent because it inspects the signs of both arguments and returns the angle in the correct quadrant over the full circle; a plain arctangent covers only half the circle and cannot tell an angle from its opposite. The arcsine branch restricts x to the range -90 to +90 degrees. At the edges of that range (when |m23| = 1) the y and z rotations align about the same effective axis and only their combination is observable; this is gimbal lock. The decode stays well defined there by convention: z is set to zero and y absorbs the combined rotation, read from the first row. On the real recording the decode and recompose round trip agrees to 3.6e-16, and it is exact at synthetic poses placed at the singularity itself."),

(H3, "3.4.1 Torso Pose Estimation"),

(P, "The torso needs no solving at all, and it is worth being precise about why. The torso is not a joint: it has no angles of its own. Its pose is completely described by the plane orientation and location already constructed in Section 3.2, the pair (R_root, p24). Euler angles enter only because Unity's animation interface consumes angles rather than matrices, so the matrix must be re-encoded. Applying the extraction formulas above to R_root gives the three angles that, applied in Unity's order, reproduce the torso orientation exactly; the frame 100 decode of (-0.60, -173.86, 0.47) degrees in Section 3.2.3 was computed exactly this way."),

(P, "The full path, from synthetic landmark input through the frame construction, the Euler decode, and the Unity rig, was validated end to end before any real data was trusted. A synthetic rigid body was swept through known yaw, pitch, roll, and combined rotations, exported in sensor space in the extractor's own CSV format, and pushed through the complete pipeline: the decoded angles match the injected truth to 1.1e-13 degrees over all 900 frames. Figure 3.7 shows the Unity rig holding four of those known poses, each with the angles that were sent."),

(IMG, FIG + "ch3_fig8_root_stills.png", 6.0),
(CAP, "Figure 3.7. The Unity rig holding known root poses from the synthetic validation dataset: (a) the reference pose, Euler (0, 180, 0), upright facing the viewer; (b) yaw +30; (c) pitch +20, a bow; (d) roll +20, a sideways lean."),

(H3, "3.4.2 Shoulder Orientation"),

(P, "The shoulder must reproduce two different things at once: where the upper arm points, and how the arm is rolled about its own length. The physical split is swing (the aiming part) and twist (the roll part) [42]. The parameterization used here writes the shoulder rotation as three elementary rotations with the twist innermost:"),
(P, "R_sh = R_y(ty) R_z(tz) R_x(tt),"),
(P, "where ty and tz are the swing angles and tt is the twist about the rest arm axis +x. The order is forced by a simple observation: a rotation about x leaves the x axis itself fixed. With the twist innermost, applying R_sh to the rest arm direction x_hat kills the twist factor immediately,"),
(P, "a_hat = R_sh x_hat = R_y(ty) R_z(tz) x_hat = (cy cz,  sz,  -sy cz),"),
(P, "so the upper-arm direction depends on the swing alone, and the twist is exactly the roll about the arm that the elbow position cannot see. If the twist were outermost instead, the twist axis would stop being the arm axis as soon as the arm swings, and the decomposition would lose its physical meaning. Two consequences follow. First, the twist is invisible in the shoulder-to-elbow vector and must be measured from a second segment, the forearm. Second, this joint order is not Unity's Euler order; driving the rig requires composing the matrix and re-extracting Unity angles with the formulas of the section introduction. Figure 3.8 illustrates both halves of the decomposition."),

(IMG, FIG + "ch3_fig6_swing_twist.png", 6.3),
(CAP, "Figure 3.8. The swing-twist decomposition. (a) The swing aims the rest arm +x into the observed direction a_hat; the direction drawn is the measured frame 100 arm direction. (b) The twist rolls about the arm axis; it is measured in the plane perpendicular to that axis, after the swing has been undone."),

(P, "The swing solve reads the components of a_hat directly. Its y component is sz, so"),
(P, "tz = asin(a_y),"),
(P, "the elevation of the arm, positive upward, restricted to -90 to +90 degrees. The x and z components share the factor cz, which cancels in the two-argument arctangent:"),
(P, "ty = atan2(-a_z, a_x),"),
(P, "the azimuth of the arm, positive sweeping backward. Every direction of the arm is reachable by some (ty, tz) pair, so there is no coverage gap. The one degenerate configuration is the arm pointing straight up or straight down (tz = +90 or -90): there a_x and a_z both vanish and the azimuth is undefined. The convention ty = 0 is applied, and any axial rotation folds into the twist automatically. This is not just asserted: a synthetic pose generated with swing (30, 90) decodes as (0, 90, 30), a different set of numbers describing the identical physical pose, and the recomposed arm direction confirms it."),

(P, "The twist solve must measure rotation about the arm axis, and rotation about an axis is only visible in the plane perpendicular to that axis. The procedure therefore first undoes the swing, bringing the arm axis back onto +x, so that the perpendicular plane becomes exactly the local y-z plane:"),
(P, "f' = R_z(-tz) R_y(-ty) f,"),
(P, "where f is the forearm vector in the parent frame from Section 3.3.2. The zero convention is anatomical: at zero twist, the forearm's perpendicular component points along local +z, meaning the elbow flexes forward. Under a twist tt, that component rotates to (-sin tt, cos tt) in the (y, z) plane, so the twist reads"),
(P, "tt = atan2(-f'_y, f'_z),"),
(P, "positive for internal rotation (the forearm rotating downward from forward). The choice of forearm vector does not matter: solving with the elbow-to-wrist vector or the shoulder-to-wrist vector gives identical twist, because after the un-swing the extra upper-arm contribution lies entirely along x and the y-z reading ignores it."),

(P, "The earlier draft of this thesis used a different twist formula, and its failure is instructive enough to keep. The draft projected the forearm onto the x-z plane, a plane that contains the rotation axis x. The x component of any vector is unchanged by a rotation about x, so that projection mixes a twist-independent quantity into the angle. The error is not subtle. At the rest pose, with the true twist equal to zero, the draft formula returns 47.9 degrees, a number that is pure segment-length geometry (it is atan of the upper arm length over the forearm length). Worse, it returns the same value for +90 and -90 degrees of true twist: the formula is blind to the sign of the roll. The large wrap-around twist values reported in the earlier draft's worked example were artifacts of this formulation, not properties of the motion. The corrected extraction above, measured in the plane perpendicular to the axis, was validated against synthetic known twists of up to 80 degrees with a maximum decode error of 8.5e-14 degrees over 900 frames, including trials where the torso rotates simultaneously. Figure 3.9 shows the Unity rig at known twist values."),

(IMG, FIG + "ch3_fig9_twist_stills.png", 6.3),
(CAP, "Figure 3.9. The rig at known shoulder twists from the synthetic validation set. (a) Zero twist at the rest pose: elbow bent, forearm toward the camera. (b) Twist +90 (internal rotation): the forearm hangs straight down. (c) Twist -90 (external rotation): the forearm points straight up."),

(P, "For the left arm no new derivation is needed. Left angles are defined through the sagittal mirror: both left segment vectors are expressed in the root basis, their x components are flipped with M = diag(-1, 1, 1), and the identical right-arm solve runs on the result. Because the mirror conjugation preserves the whole construction, every property above carries over unchanged, and a mirror-symmetric pose produces identical angle values on both sides with the same anatomical meaning: positive ty sweeps backward, positive tz raises the arm, positive tt rotates internally. When the left chain is reconstructed in world coordinates, the mirror identities M R_y(t) M = R_y(-t), M R_z(t) M = R_z(-t), M R_x(t) M = R_x(t) mean the left chain is the right chain with the y and z angle signs flipped and the twist sign kept, applied to a rest arm along -x."),

(H3, "3.4.3 Elbow Flexion and Extension"),

(P, "The elbow is solved in the L14 frame established in Section 3.3.2: the fully rotated arm frame R_arm = R_root R_y(ty) R_z(tz) R_x(tt), in which the rest forearm continues the arm axis along +x. The forearm direction in this frame is g_hat = R_arm^T (p16 - p14), normalised, and the same swing parameterization as the shoulder applies:"),
(P, "e_z = asin(g_y),        e_y = atan2(-g_z, g_x),"),
(P, "with e_y = 0 a straight arm and e_y = -90 a right angle bend."),

(P, "One structural fact about this solve was derived on paper and then confirmed numerically: e_z is identically zero. The reason sits in the definition of the shoulder twist. The twist was defined as exactly the rotation that aligns the forearm's perpendicular component with local +z, so by the time the elbow is solved, the flexion plane has already been rotated into the x-z plane of the elbow frame, leaving g_y = 0 on every frame. The elbow's out-of-plane freedom is not lost; it is the shoulder twist, already accounted one joint earlier. This closes the dimension count of Section 3.3.1: four observable degrees of freedom, four independent angles (ty, tz, tt, e_y). The confirmation is direct: a synthetic pose generated with e_z = 30 degrees at zero twist decodes as twist -30 and e_z = 0 with the same e_y, and the reconstructed forearm direction matches the input to 5.6e-17. The angle e_z is kept in the data interface for generality but carries no independent information. Elbow flexion stays in the anatomical range e_y between -180 and 0 on all 899 real frames."),

(P, "The elbow also exposes the one genuine degeneracy of a three-landmark arm. When the arm is perfectly straight, the forearm is parallel to the upper arm, its perpendicular component vanishes, and the shoulder twist becomes unobservable; no algebra can recover a roll about an axis from two collinear segments. The solver detects the condition by thresholding the perpendicular fraction of the forearm, applies the convention tt = 0 so the elbow frame stays defined (e_y then correctly decodes 0), and flags the twist as unobservable so that downstream processing holds the last valid value instead of trusting a numerical accident. Near-straight elbows leave the flexion angle well conditioned but make the twist sensitive to noise; this is quantified as a practical limitation in Chapter 8. Figure 3.10 shows the rig at a validated straight-elbow pose."),

(IMG, FIG + "ch3_fig10_elbow_straight.png", 4.6),
(CAP, "Figure 3.10. The rig holding the synthetic straight-elbow pose (e_y = 0): the forearm continues the upper-arm axis, reproduced to 0.02 degrees. At this configuration the shoulder twist is fundamentally unobservable from landmarks and is held by convention."),

(H3, "3.4.4 Wrist Rotation"),

(P, "The wrist is the terminal landmark of the chain. In this model it serves two purposes: it defines the forearm direction that the elbow flexion is read from, and it supplies the reference that makes the shoulder twist observable. A full three-degree-of-freedom wrist orientation is deliberately not resolved. The missing ingredient is a landmark beyond the wrist: forearm pronation, the roll of the forearm about its own axis, produces no motion of the wrist point at all, so no algebra over these landmarks can observe it. Resolving hand orientation is the province of hand-specific models such as [15], which this framework is structured to accept downstream without changing the arm chain: the wrist position is retained and transmitted so the terminal point of each arm is correctly placed in the reconstructed scene."),

(H3, "3.4.5 Work Example"),

(P, "The per-stage numbers of frame 100 now assemble into the complete chain. From Sections 3.2.3 and 3.3.3, the root decodes to Euler (-0.60, -173.86, 0.47) and the right-arm local vectors are a_hat = (0.1894, -0.8055, 0.5615) and f = (-0.1696, -0.0687, 0.1199). The swing solve reads"),
(P, "tz = asin(-0.8055) = -53.66 degrees,        ty = atan2(-0.5615, 0.1894) = -71.36 degrees:"),
(P, "the arm is dropped 54 degrees below horizontal and swung 71 degrees forward of the T-pose, which is exactly the reaching-down-and-forward pose visible in Figure 3.5. Undoing this swing on the forearm vector gives f' = (0.0905, 0.0072, 0.1990); its perpendicular part is almost purely +z, so the twist is small:"),
(P, "tt = atan2(-0.0072, 0.1990) = -2.07 degrees."),
(P, "Composing R_sh = R_y(-71.36) R_z(-53.66) R_x(-2.07) and re-extracting in Unity's convention gives the transmitted shoulder Euler angles (-1.23, -69.70, -53.68). The recomposed matrix maps the rest arm onto the measured a_hat with zero error at machine precision. In the elbow frame the forearm direction is g_hat = (0.4138, 0.0000, 0.9104); its y component is zero to ten decimal places, the e_z = 0 property arriving on real data, and the flexion is"),
(P, "e_y = atan2(-0.9104, 0.4138) = -65.56 degrees,"),
(P, "a comfortable working bend. The left arm runs through the identical mirrored solve and yields shoulder (-3.13, -44.54, 5.95) and elbow -60.20 degrees: raised less, swung forward barely, also bent to hold the object. Thirteen numbers (three root Euler angles, then swing, twist, and flexion for each arm, with e_z carried for generality) now describe the entire measured pose of frame 100."),

(P, "Driving the rig is one further composition per bone. The world rotation applied to a bone is"),
(P, "R_bone = q_A R_chain C_rest,"),
(P, "where R_chain is the solved chain up to that bone (R_root for the hips, R_root R_sh for the upper arm, R_root R_sh R_el for the forearm, and the sign-flipped mirror versions on the left), C_rest is the bone's authored rest rotation captured once at startup (it absorbs the character model's own axis conventions, including the rig's built-in 8 degree arm droop, as a constant), and q_A is the world anchor of the integrated scene of Chapter 5 (identity in the standalone scene). The anchor multiplies from the left, outside the chain. The root bone is additionally translated so the hip lands on the streamed pelvis point, and the uniform scale that sizes the character to the subject commutes with every rotation, so scaling never disturbs the angles."),

(P, "Table 3.2 summarises the synthetic ground-truth validation of every solve in this chapter: six datasets with known injected angle trajectories, exported in sensor space through the extractor's exact data format and pushed through the full pipeline. The worst decode error across all of them is 2.8e-13 degrees, which is floating-point noise; the solve is an exact inverse of the construction. Figure 3.11 shows the hardest single pose, frame 742 of the arm_full dataset, where all seven right-side angles are nonzero simultaneously."),

(TBL, [["Dataset", "Content", "Max decode error (deg)"],
       ["root motion", "yaw, pitch, roll sweeps and combined", "1.1e-13"],
       ["shoulder_only", "swings to 60, twist to 80, combinations", "8.5e-14"],
       ["shoulder_torso", "arm and root moving simultaneously", "2.0e-13"],
       ["elbow_only", "flexion -10 to -150, rotating flexion plane", "8.5e-14"],
       ["arm_full", "root, shoulder, elbow all moving", "2.8e-13"],
       ["arm_both", "both arms plus root, 12 angles nonzero", "2.6e-13"]]),
(CAP, "Table 3.2. Synthetic known-truth validation of the kinematic solve. Each dataset injects known angle trajectories, synthesises landmarks in sensor space, and compares the full-pipeline decode against the truth."),

(IMG, FIG + "ch3_fig11_arm_full.png", 5.2),
(CAP, "Figure 3.11. The rig holding frame 742 of the arm_full validation dataset, with every right-side angle nonzero at once: root (8.0, -171.7, 5.8), shoulder swing-twist (27.8, 30.0, 32.4), elbow -100.4. Both displayed bone directions match the dataset's landmark directions to four decimal places."),

(P, "Real recordings close the loop. With no injected truth available, correctness on real data means three things: the frame invariants hold (determinant, orthonormality, and Euler round trip all at machine precision on every one of the 899 frames), the solved angles reconstruct both measured segment directions (worst frame 6.4e-14 degrees), and the numbers are physically plausible (elbow flexion never leaves its anatomical range). One further measurement pins the final step: the Unity rig itself was instrumented to log its four arm-segment directions on every displayed frame and compare them against independent predictions from the solved angles. Across 897 displayed frames the mean angular error is 0.0000 degrees and the maximum is 0.0001 degrees, the quantisation floor of the 32-bit packet format. The chain from landmarks to angles to rendered bones is exact end to end; whatever error the reconstructed motion carries comes from the measurements, not from the model."),

(H2, "References"),
(P, "Reference numbering continues from the previous chapters; entries cited in this chapter:"),
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
        for i, r in enumerate(rows):
            for j, c in enumerate(r):
                cell = t.cell(i, j)
                cell.text = c
                for par in cell.paragraphs:
                    for run in par.runs:
                        run.font.size = Pt(10)
                        if i == 0:
                            run.font.bold = True

for n in sorted(references):
    doc.add_paragraph(f"[{n}] {references[n]}")

out = "/home/luo/Desktop/New_SandBox/writing/v2/Chapter_3_Kinematic_Modeling.docx"
doc.save(out)
print("saved", out)

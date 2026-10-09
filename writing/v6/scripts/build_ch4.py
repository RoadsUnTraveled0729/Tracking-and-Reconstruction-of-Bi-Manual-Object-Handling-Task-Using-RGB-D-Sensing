#!/usr/bin/env python3
"""Build writing/v4/Chapter_4_Offline_Processing_Pipeline.docx.

v3 restructuring per writing/v4/STRUCTURE.md: the detection and pose-recovery
subsections (v2 4.2.1 Detection and Subpixel Corners, 4.2.2 Planar Pose
Estimation and the Two-Solution Ambiguity, 4.2.5 Worked Example: Frame 100
Detections) move to Appendix D; a bridging paragraph summarizes what that
machinery delivers. Kept sections renumber: 4.2.3 -> 4.2.1, 4.2.4 -> 4.2.2.
Figures: v2 4.4 (lobes) moves to the Appendix; v2 4.5/4.6/4.7/4.8 ->
4.4/4.5/4.6/4.7. Tables: v2 4.2 moves; v2 4.3 -> 4.2. Rule-11 rewording:
bag file -> recording, raw CSV -> archived track/detections. Per-chapter
References section dropped (skill rule 12). All numbers unchanged from v2
(pinned Pipeline B artifacts).

v5 trim round (2026-08-03, supervisor directive): exactness numerology and
side asides cut (singular-value listing, 200-rotation self-test, R(4/8)
matrix display, machine-precision litanies, Recording 3 aside, closing
observations); worked examples kept in condensed form; all pinned headline
numbers and Eqs 4.1-4.4 unchanged.
"""
from docx import Document
from docx.shared import Pt, Inches

FIG = "/home/luo/Desktop/New_SandBox/writing/v2/figures/"
from eqn import r, nor, sub, sup, hat, frac, mat, d, eqArr, add_display_eq, add_display_math

H1, H2, H3, P, IMG, CAP, TBL, EQ = "h1", "h2", "h3", "p", "img", "cap", "tbl", "eq"
MATH = "mth"  # displayed, unnumbered worked-example mathematics

content = [
(H1, "Chapter 4: Offline Processing Pipeline System"),

(P, "Chapter 3 turned the measured landmarks into joint angles, so the reconstruction can now show what the arms are doing. What it cannot yet show is whether that reconstruction is right. The landmark chain has no witness: if the estimated wrist drifts five centimetres to the side, nothing in the chain itself would notice. Validating the reconstructed arm motion during a bimanual task therefore requires a second, independent source of measurements about where the arms are. The manipulated object provides one. A fiducial marker attached to the object can be tracked through the colour images alone, by geometry rather than by a learned detector, and whenever a hand carries the object, the tracked object position becomes an independent estimate of where that hand must be. Chapter 6 uses exactly this comparison to grade the landmark-based tracking. This chapter builds the machinery that makes the comparison possible: the marker-based branch of the offline pipeline, which reconstructs the fixed scene, tracks the object through it, and expresses everything in a single camera-independent world frame."),

(P, "The chapter follows the data. Section 4.1 lays out the architecture of the whole offline pipeline and shows where the two branches separate and rejoin. Section 4.2 states what the marker detections deliver and covers the calibration that freezes the static scene; the detection and pose recovery machinery itself, including the planar two-solution ambiguity and its resolution, is perception-layer material and is detailed in Appendix D. Section 4.3 develops the transformation chain that carries the moving object into the world frame and the filter that cleans its track. Section 4.4 describes how the two branches come together into one fused record per frame. The experimental setup and the marker preliminaries were established in Chapter 2 and the Appendix and are not repeated; this chapter concentrates on what is done with them and on the measured results."),

(H2, "4.1 System Architecture Overview"),

(P, "Everything the pipeline consumes is captured in a single recording session. During a session, the RealSense sensor writes one session recording, the container format of the RealSense software that stores the synchronized colour stream, the depth stream, their timestamps, and the calibration parameters of the sensor itself [9]. No data is collected separately for the two branches: the body landmarks and the marker detections that later chapters compare are extracted from the same recording, frame by frame, so the comparison in Chapter 6 is between two readings of the same physical event."),

(P, "The word offline in the chapter title means that this processing happens after the session has ended, not that the data is somehow different. The distinction matters for two reasons. There is no per-frame time budget, so every frame can be processed completely before the next one is read, and the whole pipeline can be re-run from the same recording whenever a stage changes, which makes every result in this thesis repeatable. The price of working offline, and what changes when the same task must run against a live sensor, is the subject of Chapter 7."),

(IMG, FIG + "ch4_fig1_pipeline.png", 6.3),
(CAP, "Figure 4.1. Dataflow of the offline pipeline. The recorded session is replayed into aligned colour and depth pairs, which feed two parallel branches: the landmark branch (MediaPipe Pose, depth lifting, smoothing, kinematic solve) and the marker branch (ArUco detection, planar pose estimation, world anchoring). The static scene calibration is computed once from the first frames and frozen; the two branches meet in the per-frame fused record."),

(P, "Figure 4.1 shows the flow. Replay opens the recording and produces, for every frame, the aligned colour and depth pair described in Chapter 2, with the depth image resampled into the colour camera's geometry and the colour intrinsics attached. The landmark branch runs MediaPipe Pose on the colour image, lifts the eight upper-body landmarks to metric 3D positions through the aligned depth, smooths the trajectories, and solves the kinematic chain of Chapter 3. Its output per frame is a set of joint angles together with the landmark positions they came from, terminating at the wrists. Calling this output the human pose deserves one qualification: it is the pose of the upper body and arms, and the wrist positions at the end of the chain are the quantities the object track will later be compared against."),

(P, "The marker branch is the subject of this chapter. It detects the three ArUco markers in each colour frame, estimates each marker's six degree of freedom pose relative to the camera, freezes the static scene from the first ten frames, and streams the object marker's pose, re-expressed in the world frame, for every frame. Its output is one world-frame object pose per frame plus the frozen scene description."),

(P, "The two branches are deliberately independent, and the independence is worth stating precisely because Chapter 6 leans on it. They read different channels of the recording: the landmark branch measures through the depth stream and a learned landmark detector, the marker branch through the colour stream and the projective geometry of a printed square. They share no code, and neither reads the other's output. The only quantities they share are the physical recording itself and, later, the single calibrated transform that places both in one frame. When the object track and the wrist track agree in Chapter 6, that agreement is evidence, because nothing in either chain was fitted to produce it. Figure 4.2 shows the idea."),

(IMG, FIG + "ch4_fig2_independence.png", 5.8),
(CAP, "Figure 4.2. The independence argument. One recording feeds two measurement chains that share no code and no data and rest on different physics; their outputs meet only in the common world frame, where Chapter 6 compares them."),

(H2, "4.2 Scene Calibration and Reconstruction"),

(P, "The marker branch rests on three printed markers whose roles were introduced in Chapter 2 and are summarized again in Table 4.1, now together with their measured detection statistics over the 899 frames of the evaluation recording. The desk marker, id 2, lies flat on the working table and anchors the world frame: the world is literally this marker's own coordinate frame, x and y in the printed plane and z out of the printed face. The wall marker, id 0, is mounted plumb on the wall behind the subject and serves as the gravity reference and as a long-range consistency check. The object marker, id 1, is centred on one face of the 70 mm cardboard cube that the subject carries. The subject's body crosses in front of the wall marker repeatedly, which accounts for its 58 missed frames; the two markers that matter for the object track are seen on every frame or nearly so."),

(TBL, [["id", "role", "size", "behaviour", "detections", "mean reprojection"],
       ["2", "desk, world anchor", "50 mm", "static, calibrated once", "899 / 899", "0.158 px"],
       ["0", "wall, gravity reference", "150 mm", "static, calibrated once", "841 / 899", "0.060 px"],
       ["1", "object, tracked", "50 mm", "carried, streamed per frame", "877 / 899", "0.183 px"]]),
(CAP, "Table 4.1. The three markers with their measured detection coverage and mean corner reprojection error over the 899-frame evaluation recording. Missed object frames are the carrying hand covering the marker; missed wall frames are the person crossing in front of it."),

(P, "How a detection turns into a pose is a perception-layer matter, and Appendix D develops it in full: the detection stages, the sub-pixel corner refinement that measurement forced, the planar pose recovery, and the two-solution ambiguity that a nearly face-on marker admits, together with the policy that resolves that ambiguity for each marker class. Two products of that machinery are all this chapter needs. Each detected marker yields a pose relative to the camera with sub-pixel reprojection error, far below one pixel on all three markers. And each frame also records an independent depth reading at the marker's centre that never enters the pose estimate; it is kept precisely because it is independent, and it serves as a range cross-check throughout. Frames on which a marker is not detected are written as empty records, never interpolated at this stage, the same data integrity convention as the landmark branch. Figure 4.3 shows the three markers as detected on frame 100, the running example frame of this thesis."),

(IMG, FIG + "ch4_fig3_markers_photo.png", 6.0),
(CAP, "Figure 4.3. The three markers on frame 100 of the evaluation recording. The outlines and corner points are drawn by projecting each marker's known corner geometry through its estimated pose and the real colour intrinsics; that the outlines land on the printed markers is itself a first sanity check of the poses."),

(H3, "4.2.1 Static Scene Calibration"),

(P, "The scene is fixed, so the pipeline does not track it. The first ten detections of each static marker are averaged into a single calibrated pose, and from then on the desk and wall poses are frozen constants; only the object is estimated per frame. Averaging the translations is an ordinary arithmetic mean. Averaging the rotations is not, because the element-wise mean of rotation matrices is in general not a rotation matrix at all. The pipeline uses the chordal mean: take the element-wise mean matrix anyway, then project it back onto the set of proper rotations by finding the rotation closest to it in the least-squares sense [45]. That projection has a closed form through the singular value decomposition of the mean matrix: with mean A = U S V^T, the projection is"),
(EQ, r("R") + r(" = ") + r("U") + r(" ") + nor("diag") + d(r("1, 1, ") + nor("det") + d(r("U") + sup(r("V"), r("T")))) + r(" ") + sup(r("V"), r("T")), "4.1"),
(P, "where the determinant factor guards against landing on a reflection. For spreads well under a degree, as here, the chordal mean coincides with the true geometric mean of the rotations far below measurement noise. Everything stays in matrix form, in keeping with the rotation policy of Chapter 3."),

(P, "The desk anchor of the evaluation recording makes the projection concrete. The required data are the ten desk rotation matrices of the calibration window, frames 0 through 9 of the archived detections; averaging them element by element gives"),
(MATH, r("A") + r(" = ") + mat([
    [r("0.9994"), r("0.0159"), r("−0.0318")],
    [r("−0.0305"), r("−0.0792"), r("−0.9964")],
    [r("−0.0183"), r("0.9967"), r("−0.0786")]])),
(P, "which is nearly but not exactly a rotation, because it averages ten matrices that disagree by fractions of a degree. Equation (4.1) projects it back onto the rotations; the correction is of order 1e-6, so at four printed decimals the projected rotation looks identical to A while now being exactly orthonormal. Together with the ordinary mean of the ten translations, (0.0117, 0.1220, 0.5786) m, this is the frozen anchor, and it reproduces the calibrated desk pose stored with the dataset to machine precision, because the calibration is exactly this computation."),

(P, "Over the ten-frame calibration window of the evaluation recording, the desk pose is stable to 0.40 mm and 0.13 degrees at worst, and the wall pose to 4.3 mm and 0.36 degrees, entirely consistent with the wall's 32 pixel image size. These numbers set the quality of the world frame itself: every world-frame quantity in this thesis is expressed relative to the calibrated desk pose."),

(P, "Freezing the anchor is not merely a resource saving. Over the 30 second session the desk marker's detected position stays static to 0.20 mm at the 95th percentile, but its detected orientation wanders by 0.088 degrees at the 95th percentile as the person moves through the scene and the lighting on the marker changes. An orientation error in the anchor displaces every reconstructed point in proportion to its distance from the anchor, so at the wall, 3.2 m away, 0.088 degrees is already 4.9 mm of apparent motion. Re-anchoring the world on every frame would inject this wobble into every point of the scene, including the object track; the frozen chordal-mean anchor makes the world frame immune to it. Figure 4.4 shows both sides of the argument on real data."),

(IMG, FIG + "ch4_fig5_anchor_drift.png", 6.3),
(CAP, "Figure 4.4. Why the anchor is frozen. (a) Orientation of the per-frame desk detection relative to the frozen calibrated pose over the recording. (b) The camera-invariance check: the wall's position recomputed in the desk frame independently at every frame, against the calibrated value; the 5.8 mm p95 at a 3.2 m range is the residual of the whole anchoring chain."),

(H3, "4.2.2 The Reconstructed Scene and Its Ground Truth Geometry"),

(P, "Calibration produces more than two frozen poses; it measures the scene geometry that Chapter 6 will treat as ground truth, and it does so with exactly one physical assumption. The assumption is that the wall is plumb. Everything else is measured. The calibrated wall marker's in-plane up axis therefore defines the direction of gravity, and by construction the reconstructed wall is exactly vertical and the reconstructed desk top exactly horizontal once the scene is levelled by that gravity."),

(P, "A second, independent gravity estimate is computed from the depth channel, and its role is deliberately limited: it breaks the sign and lobe ambiguities of the pose recovery (Appendix D), for which about 10 degrees of accuracy suffices. One plane is fitted robustly to rings of depth pixels around the desk marker, excluding the marker card itself, averaged over the first ten frames, and frozen. The fit needed one protective gate, added after a measured failure: the cube is hand-held from the first frame of this recording, and without the gate the fit swept across the person's body and bent the estimated gravity by more than 60 degrees, so the object marker's surroundings enter the fit only when their local depth plane agrees with the desk-only fit, that is, only when the cube is resting on the desk. Measured against the authoritative wall gravity the finished seed agrees to 5.03 degrees, comfortably inside its requirement, and the agreement of two gravity estimates from two different channels is itself a cross-check of the calibration."),

(P, "The remaining calibrated quantities, all from the frozen calibration of the evaluation recording: the desk marker card lies nearly flat, its normal 4.75 degrees from the measured gravity; the world origin, the marker's centre, sits 1.2 mm below the fitted tabletop plane, consistent with a card of negligible thickness lying on the surface; the sensor's field of view from the colour intrinsics is 55.6 by 43.1 degrees; and the object cube's edge length is 70 mm. The cube size was auto-calibrated on Recording 3, where the cube rests on the desk, as twice the height of the marker centre above the local tabletop, and supplied to this recording as a parameter, since a hand-held cube offers no resting reference. The camera's own pose in the world falls out of the anchoring for free, as the next section shows, and the Unity reconstruction of Chapter 5 receives exactly this full scene description, anchor, wall, camera, gravity, tabletop height, and cube size, once, before any per-frame streaming begins. Figure 4.5 shows the reconstructed scene assembled from nothing but the pipeline outputs described so far."),

(IMG, FIG + "ch4_fig8_scene_recon.png", 6.3),
(CAP, "Figure 4.5. The reconstructed scene, drawn purely from the pipeline outputs in the world frame of the desk marker. (a) Top view: origin, calibrated camera pose, calibrated wall pose with the wall line, and the filtered object path. (b) The carried object's trajectory above the fitted tabletop plane, coloured by time."),

(H2, "4.3 Object Tracking"),

(H3, "4.3.1 World Anchoring and Camera-Motion Invariance"),

(P, "Every pose the solver returns is expressed relative to the camera. For reconstruction this is the wrong frame: if the camera were nudged or placed differently between sessions, the camera-relative pose of a motionless object would change even though nothing in the scene moved. The object must instead be expressed relative to something fixed in the scene, and the fixed reference chosen is the desk marker, the world frame W. Three frames therefore participate, shown on the real image in Figure 4.6: the camera frame C, the world frame W at the desk marker, and the object frame O at the object marker, moving with the cube."),

(IMG, FIG + "ch4_fig6_frames_photo.png", 6.0),
(CAP, "Figure 4.6. The three coordinate frames of object tracking, drawn on frame 100 through the real intrinsics, with the two measured transformations and the derived one. The camera frame is the viewpoint of the image itself. The desk axes are the calibrated anchor; the object axes are the frame 100 detection."),

(P, "Each pose is packaged as the 4 by 4 homogeneous transformation of Chapter 3, the rotation in the top left block and the translation in the top right column [41]. Two such transformations are available: the calibrated desk pose T_cam_desk, mapping world points into camera coordinates, and the per-frame object pose T_cam_obj(t), mapping object points into camera coordinates. Wanted is T_desk_obj(t), the object as seen from the world, the quantity that does not care where the camera stands. It is assembled by walking the only available path between the two frames, from the object into the camera, then from the camera into the world:"),
(EQ, sub(r("T"), nor("desk,obj")) + d(r("t")) + r(" = ") +
     sup(d(sub(r("T"), nor("cam,desk"))), r("−1")) + r(" ") +
     sub(r("T"), nor("cam,obj")) + d(r("t")), "4.2"),

(P, "The first factor reverses the direction of the calibrated transformation, and inverting a homogeneous transformation is cheap enough to derive in two lines rather than treat as a generic matrix inverse. Suppose the inverse has the same rigid form, an unknown rotation followed by an unknown translation d. Multiplying the candidate against the original and demanding the identity gives two block conditions: the rotation blocks must multiply to the identity, which the transpose R^T achieves exactly because rotation matrices are orthonormal, and the translation blocks must satisfy R^T t + d = 0, which solves to d = -R^T t. The inverse is therefore built from a transpose and one matrix-vector product, no numerical inversion involved:"),
(EQ, sup(d(sub(r("T"), nor("cam,desk"))), r("−1")) + r(" = ") +
     mat([[sup(r("R"), r("T")), r("−") + sup(r("R"), r("T")) + r(" ") + r("t")],
          [r("0"), r("1")]]), "4.3"),

(P, "Applied to the calibrated anchor, this inverse has a pleasant physical reading: its translation column, -R^T t = (0.0026, -0.5673, 0.1675) m, is the camera's own position in the world, 57 cm behind the desk marker's y axis and 17 cm above the marker plane, at the desk's edge. The camera pose in the reconstructed scene comes for free; no extra calibration step ever measures it."),

(P, "The chain makes the reconstruction camera-independent. If the camera were moved, both measured transformations would change, because both are measured from the camera. But the camera frame appears in the chain twice, once as the destination of the object pose and once as the source of the inverted desk pose, and the two appearances cancel: whatever the camera's placement contributes to T_cam_obj is removed again by (T_cam_desk)^-1. What remains depends only on where the object is relative to the desk. The claim is not merely algebraic; it is checked on data. On every frame of the recording, the wall's pose was recomputed in the desk frame using only that frame's raw detections, no calibration involved, and compared against the frozen calibrated value. Across 841 frames the wall moved by 5.8 mm at the 95th percentile, at a lever arm of 3.2 m, and by 0.54 degrees in orientation, Figure 4.4(b). The residual is explained by known mechanisms: most of it lies along the camera-to-wall ray, where monocular range from a 32 pixel marker is weakest, and the lateral remainder is bounded by the measured desk-anchor drift multiplied by the lever arm."),

(P, "One subtlety in the implementation deserves emphasis because it is easy to get wrong: the desk transformation in the chain is always the frozen calibrated one, never the current frame's desk detection. Using the per-frame desk pose would re-anchor the world on every frame and leak the anchor's 0.088 degree orientation wobble, amplified by whatever lever arm applies, straight into the object track. With the frozen anchor, desk measurement noise cannot reach the object stream at all: frame to frame, the object's world pose inherits noise only from the object's own detection."),

(H3, "4.3.2 Conversion to the Unity Frame"),

(P, "The world frame W is right-handed with z pointing out of the desk marker's face, which is up for a marker lying on the table. Unity is left-handed with y up. The conversion swaps the roles of y and z, and one permutation matrix P, with rows (1,0,0), (0,0,1), (0,1,0), does the whole job: positions map as p_U = P p_W, and rotations map by conjugation, R_U = P R_W P. The same matrix appears on both sides because P is its own inverse. Two determinant facts make this conversion safe. P itself has determinant -1, a reflection, exactly as a change of handedness requires. And in the conjugation the two copies of P contribute (-1) times (-1), so det(R_U) = det(R_W) = +1: every converted rotation is still a proper rotation, verified numerically on every stored matrix of the recording. The converted rotation is finally encoded as Unity Euler angles in the ZXY-applied convention of Chapter 3; the marker branch carries its own copy of that small conversion, in keeping with the independence rule of Section 4.1."),

(H3, "4.3.3 Filtering the Object Track"),

(P, "The raw world-frame track upholds data integrity but is not smooth. Two defects need treatment before the track is fit to drive a reconstruction or grade another sensor. First, gaps: the carrying hand covers the marker on 22 of the 899 frames, in four gaps: ten frames in three interior gaps of one, two, and seven consecutive frames, plus a twelve-frame gap that runs to the end of the recording. Second, jitter: raw pose estimation noise moves the object by up to 19 mm between consecutive frames while the true motion is a smooth carry, and if gaps are simply held at the last pose, the track pops by up to 2.2 cm and 3.4 degrees on re-acquisition. The filter runs offline, between the extractor and any consumer, and never modifies the raw track; every stage below can be re-run or audited against the original."),

(P, "Positions in interior gaps are bridged linearly over time. Rotations cannot be interpolated element by element, for the same reason they cannot be averaged element by element, so gaps in orientation are bridged along the geodesic, the constant-angular-velocity path between the two endpoint rotations. With Delta = R_a^T R_b the relative rotation across the gap, the interpolant at fraction s is"),
(EQ, r("R") + d(r("s")) + r(" = ") + sub(r("R"), r("a")) + r(" ") + nor("exp") + d(r("s") + r(" ") + nor("log") + r(" Δ")), "4.4"),
(P, "The logarithm extracts Delta's rotation axis and angle, the angle is scaled by s, and the exponential, which is Rodrigues' rotation formula, rebuilds the partial rotation (the formula itself is equation (D.1) in Appendix D). This is the matrix-form equivalent of quaternion slerp, with no quaternions introduced. Gaps at the boundaries of the recording hold the nearest valid pose instead of extrapolating."),

(P, "The longest interior gap of the evaluation recording shows the bridge on real data. The hand covers the marker on frames 879 through 885, so the last measurement before the gap is frame 878 and the first after it is frame 886, and those two archived world poses are the only inputs the bridge uses. Their relative rotation has trace 2.99733, so its angle and axis are"),
(MATH, eqArr(
    r("θ") + r(" = ") + nor("acos") + d(frac(r("2.99733 − 1"), r("2"))) + r(" = 2.96°"),
    r("w") + r(" = (0.4130, 0.9042, 0.1092)"))),
(P, "a three-degree turn about an axis lying mostly along the world y axis. The middle of the gap, frame 882, sits at s = 4/8 of the way from one endpoint to the other, so equation (4.4) scales the angle to 1.48 degrees and the exponential rebuilds the partial rotation. The linearly bridged position at the same frame is the midpoint of the endpoint positions, (0.0169, 0.3234, 0.2143) m. The archived filtered track holds exactly this pose at frame 882 with its filled flag set, and across all seven bridged frames the archived track deviates from this hand computation by at most 0.4 mm and 0.08 degrees, the small residual of the smoothing stage described next."),

(P, "Jitter is treated after despiking with the same Hampel outlier statistic used for the landmarks in Chapter 2. Position is smoothed with a Savitzky-Golay filter of window 9 and order 2: each output sample is the value of the least-squares quadratic fitted to its nine-frame neighbourhood [44]. A quadratic fit was chosen over a plain moving average deliberately, because the object track's value lies in its kinematics; local polynomial smoothing preserves peaks and derivatives that a moving average flattens, and Chapter 6 differentiates this track to correlate object velocity with wrist velocity. Rotation is smoothed by the rolling version of the chordal mean of Section 4.2.1, a five-frame window projected back onto the rotations, the same mathematics reused as a moving filter."),

(P, "The filter operates under an explicit data integrity contract. The detected flag of every frame passes through unchanged, so a bridged frame is never disguised as a measurement; downstream, bridged frames stream with a live flag of zero and the reconstruction tints the cube red for exactly those frames. And the filter is asserted, inside the validation suite, to move genuinely measured frames by less than the raw estimation jitter itself: measured median displacement 1.2 mm, maximum 11.6 mm, against an asserted bound of 15 mm. Figure 4.7 shows the result. Frame-to-frame steps drop from 10.2 mm to 4.9 mm at the 95th percentile, the re-acquisition pops disappear, and the bridged samples are individually marked."),

(IMG, FIG + "ch4_fig7_filter_qc.png", 6.3),
(CAP, "Figure 4.7. Raw versus filtered object track over the full recording, in Unity axes: the three position components and the frame-to-frame step size. Orange dots mark bridged gap frames, which keep their live flag at zero downstream."),

(H3, "4.3.4 Worked Example: Frame 100 Through the Chain"),

(P, "The frame 100 object detection, recovered in Appendix D with camera-frame translation (0.0675, -0.1111, 0.9268) m, now runs the full path from camera measurement to Unity pose. The numbers below are produced by executing the pipeline's own functions on the archived raw detections and calibration data of the evaluation recording."),

(P, "Step one, the inverse anchor. The calibrated desk pose of Section 4.2.1 has rotation R and translation t = (0.0117, 0.1220, 0.5786) m. Its closed-form inverse of equation (4.3) carries rotation R^T and translation"),
(MATH, r("−") + sup(r("R"), r("T")) + r(" t = (0.0026, −0.5673, 0.1675)")),
(P, "the camera position in the world already met in Section 4.3.1."),

(P, "Step two, the chain. Multiplying the inverse anchor by the frame 100 object pose, exactly the product of equation (4.2), gives the object in the world; the translation column of the result is"),
(MATH, sub(r("t"), nor("desk,obj")) + r(" = (0.0564, 0.3663, 0.2031)")),
(P, "Read against the scene, each coordinate makes physical sense: the cube's marker is 5.6 cm along the desk marker's x axis, 36.6 cm along its y axis, which points away from the camera toward the person, and 20.3 cm along z, that is, held about 20 cm above the tabletop, matching the photograph in Figure 4.3, where the subject holds the cube at chest height above the desk."),

(P, "Step three, the Unity map. Applying P swaps the last two coordinates:"),
(MATH, r("P") + r(" ") + sub(r("t"), nor("desk,obj")) + r(" = (0.0564, 0.2031, 0.3663)")),
(P, "now x right, y up 20.3 cm, z forward. Conjugating the rotation and decoding in the ZXY convention gives Unity Euler angles (-86.5, -153.4, 134.9) degrees, and the conjugated matrix's determinant is again +1."),

(P, "Step four, the check against the archived data. The archived world-track entry for frame 100 agrees with the pose just computed to machine precision, and the same reproduction holds across the whole recording: the archived track is exactly the raw data pushed through exactly this chain. The filtered track of Section 4.3.3 moves this particular frame by 2.9 mm, within the raw jitter, and its bridged-frame flag is zero, as frame 100 is a genuine detection."),

(H2, "4.4 Data Fusion"),

(P, "After both branches have run, each frame of the recording owns two records. From the landmark branch: the eight upper-body landmark positions in person space, the joint angles of the kinematic chain, and the per-landmark visibility flags of Chapter 2. From the marker branch: the object's world-frame pose, its detected flag, and the frozen scene description shared by all frames. Fusion pairs them. Both branches processed the same sequence of frames from the same recording, so they share a frame index and the recording's time base, and the fused record for a frame is simply the pair of records carrying that index; no resampling and no timestamp matching is needed offline."),

(P, "One caveat defines what fusion does not do. The two records do not yet live in the same coordinate frame: the object pose is world-anchored, but the person-space landmarks are still expressed relative to the camera, only with the y axis flipped. The bridge is already present in this chapter's output, because the anchoring chain measured the camera's pose in the world, and a single constant transform built from that calibrated pose places every person-space point into the scene. Deriving that anchor transform, and verifying it, belongs to the integration layer and is done in Chapter 5. What fusion guarantees here is narrower and checkable: the two streams are temporally aligned by construction, each carries its own data integrity flags unchanged, and each is traceable to the same physical instant of the recording."),

(P, "The marker branch's outputs were validated as a whole before being frozen into the dataset that later chapters consume. The validation suite runs 21 checks over the recording, grouped in Table 4.2, and all 21 pass on both recorded sessions. The checks range from coverage and subpixel reprojection through the camera-invariance and depth cross-checks already discussed, to exact reproducibility of the stored world track from the raw detections plus the calibration data."),

(TBL, [["group", "checks", "headline result on the evaluation recording"],
       ["detection coverage", "4", "desk 899/899, object 877/899, wall 841/899, no unresolved lobes"],
       ["reprojection error", "3", "means 0.060 to 0.183 px, all far below 1 px"],
       ["camera invariance", "6", "wall stable in desk frame to p95 5.8 mm / 0.54 deg at 3.2 m"],
       ["depth cross-check", "3", "solver range vs depth median within 10 mm at all three markers"],
       ["calibration and world math", "5", "rotations SO(3) to 1e-9, Euler round-trip exact, world track reproduces to 1.1e-16 m"]]),
(CAP, "Table 4.2. The 21-check validation of the marker branch, all passing on both recordings. The full per-check output is archived with the frozen dataset."),

(P, "Chapter 5 streams this chapter's outputs into Unity and verifies that the transfer is exact to float precision, and Chapter 6 grades the two branches against each other, including a measured design lesson about camera placement relative to the anchor marker."),
]

references = {
9:  'L. Keselman, J. Iselin Woodfill, A. Grunnet-Jepsen, and A. Bhowmik, "Intel RealSense stereoscopic depth cameras," in Proc. IEEE Conf. Computer Vision and Pattern Recognition Workshops (CVPRW), 2017.',
41: 'J. J. Craig, Introduction to Robotics: Mechanics and Control, 3rd ed. Upper Saddle River, NJ, USA: Pearson Prentice Hall, 2005.',
44: 'A. Savitzky and M. J. E. Golay, "Smoothing and differentiation of data by simplified least squares procedures," Analytical Chemistry, vol. 36, no. 8, pp. 1627-1639, 1964.',
45: 'R. Hartley, J. Trumpf, Y. Dai, and H. Li, "Rotation averaging," International Journal of Computer Vision, vol. 103, no. 3, pp. 267-305, 2013.',
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
        for i, r in enumerate(rows):
            for j, c in enumerate(r):
                cell = t.cell(i, j)
                cell.text = c
                for par in cell.paragraphs:
                    for run in par.runs:
                        run.font.size = Pt(10)
                        if i == 0:
                            run.font.bold = True

out = "/home/luo/Desktop/New_SandBox/writing/v6/Chapter_4_Offline_Processing_Pipeline.docx"
doc.save(out)
print("saved", out)

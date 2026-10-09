#!/usr/bin/env python3
"""Build writing/v8/Chapter_2_Experimental_Setup.docx (V8 rewrite round).

Chapter 2 "Experimental Setup and Measurements" (title per user decision
2026-09-05, supervisor round 4): 2.1 The Recording Setup, 2.2 Coordinate
Frames and Scene Calibration (new; C45/C46: the frame list, Figure 2.4
camera frame moved from Chapter 3, Figure 2.5 scene frames with the T
arrows, Table 2.2 transformations, and the static scene calibration
moved from Chapter 4 Section 4.1 with equation (2.1), Table 2.3 and
Figure 2.6), 2.3 Pose Landmarks from MediaPipe, 2.4 Object Pose from
ArUco Markers, 2.5 Measurement Filtering (C43 rename). Sections 2.3-2.5
are the user's own text (commit 669cff0); every edit to them is logged in
CH2_CONCISION_LOG.md. Environment only (user
direction 2026-09-01): the reference paths and the waypoints of both
recordings live at the start of Chapter 7, and the rail dimension
figure (ch2_fig_rail_dims.png) moved there with them. The rail lies
FLAT (a 2-by-4: 3.8 cm tall, top face 8.8 cm wide; E-024). Marker size:
45 mm is the printed size (fact), 50 mm the size declared to the
detector. Rail-only round (2026-09-01, user direction): the thesis is
based on the rail recording recording_20260831_065553 (900 frames,
30 s) alone; the R5 loop recording appears only in Chapter 7's
occlusion evaluation and is not mentioned here. All example figures
(setup, MediaPipe, ArUco, filters) come from rail frame 533 and the
rail landmark CSVs. Filter parameters per the run metadata: hampel
window 7, k 3, floor 2 cm, gaps to 5 frames, Butterworth 3 Hz order 4
zero-phase; edge backfill disabled.
Supervisor comments addressed: C4 (setup photographs + user study
objective), C6 (filters named, justified, referenced, results shown),
C8 (filter panel split into separate larger figures), C43, C45, C46
(round 4, 2026-09-05; C44 keeps the user's sentences as they are).
Natural-voice pass 2026-09-05 (user: no 'participant', no 'X, the Y of
Z' appositives, active voice, natural joins): 2.1 and 2.2 redrafted,
2.3-2.5 touched only where the rule required; log entries 131-169.
Humanizer pass 2026-09-05 (writing/WRITING_SKILL.md = blader/humanizer):
2.1 and 2.2 redrafted again, 2.3-2.5 touched in four places; log
entries 170-173 and the 2.1/2.2 redraft block.
Figures: make_ch2_frames_fig.py (Figure 2.5), make_ch2_fig1.py (2.3).
Figures: writing/v8/figures/. Citations: writing/v7/references.md
numbering ([1]-[52] frozen, [53]-[57] appended).
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches

from eqn import r, nor, sub, sup, d, add_display_eq, add_inline_math

H1, H2, H3, P = "h1", "h2", "h3", "p"
CAP, TBL, LIN, IMG, EQ, PM = "cap", "tbl", "lin", "img", "eq", "pm"


def T(t):
    return ("t", t)


def X(f):
    return ("m", f)


def M(f):
    """A table cell holding inline math instead of text."""
    return ("m", f)


# --- equation-fragment shorthands (Table 2.2 and Section 2.2) ---
TCW = sub(r("T"), nor("CW"))
TCwall = sub(r("T"), nor("C,wall"))
TCO = sub(r("T"), nor("CO"))
TWO = sub(r("T"), nor("WO"))
TWC = sub(r("T"), nor("WC"))
TAB = sub(r("T"), nor("AB"))
Troot = sub(r("T"), nor("root"))
Tsh = sub(r("T"), nor("sh"))
Tel = sub(r("T"), nor("el"))
TCWinv = sup(TCW, r("−1"))


def bar(e):
    """Overbar accent (mean matrix); the shared equation helpers have none."""
    return ('<m:acc><m:accPr><m:chr m:val="\u0304"/></m:accPr>'
            f'<m:e>{e}</m:e></m:acc>')


Mbar = bar(r("M"))

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v8" / "figures"

# Rail-only round: the rail recording (ground truth by construction) is
# the only recording of the chapter. The loop recording belongs to
# Chapter 7's occlusion evaluation and is introduced there.
F_RAILS, F_SETUP, F_FLOW, F_CAM, F_FRAMES, F_CALIB = 1, 2, 3, 4, 5, 6
F_MP, F_ARUCO, F_DESP, F_GAP, F_SMOOTH = 7, 8, 9, 10, 11

content = [
(H1, "Chapter 2: Experimental Setup and Measurements"),

(P, f"This chapter describes the experiment and the measurements it produces. It covers the recording setup, the coordinate frames and the scene calibration, the body landmarks from MediaPipe, the object poses from the ArUco markers, and the filtering of those measurements. Later chapters build on these outputs."),

(H2, "2.1 The Recording Setup"),

# 2.1 rewritten on the user's outline (2026-09-02): controlled-lab
# opening, one table of the scene objects, the 2 m range argument from
# the Intel D400 tuning guide [58], no field-of-view sentence, and no
# Appendix D pointer here (appendix order = first appearance in body;
# Appendix D was first cited in the MediaPipe section, user decision
# 2026-09-02; since round 4 the moved calibration text of Section 2.2.2
# cites Appendix D and Appendix E before Section 2.3 cites Appendix C,
# which the appendix order rule must absorb - flagged to the main agent).
(P, f"The recording took place in a controlled lab, because uneven lighting and a busy background would make the ArUco markers harder to detect and the MediaPipe landmarks less reliable. The subject moves a cube along the desk and then along a wooden rail with one hand. Chapter 7 defines the reference path of this task and compares the tracked trajectory against it. Figure 2.{F_RAILS}(a) shows the layout in a photograph taken from above the desk. Panels (b) and (c) show the scene from behind the RGB-D camera and one colour frame of the recording. Table 2.1 lists the objects in the scene."),

(IMG, FIG / "ch2_fig_rail_setup.png", 6.3),
(CAP, f"Figure 2.{F_RAILS}. The recording setup. (a) The working area drawn on grid paper, with the rail, the cube at its start position, the desk marker, and the spirit level used to level the rail. (b) The scene from behind the RGB-D camera. (c) A colour frame of the recording, with the cube part way along the rail in the subject's right hand."),

# src: marker sizes and the 0.9 scale -> eval/common/marker_size.py, E-009a;
#      45 mm is the printed size (user measured, 2026-09-01), 50 mm the
#      declared size. Rail 38.7 x 8.8 x 3.8 cm lying flat (E-024).
(TBL, [["Object", "Role", "ArUco ID", "Dictionary", "Printed size (mm)", "Declared size (mm)", "Physical dimensions"],
       ["Wall marker", "Static; gravity reference", "0", "5 by 5", "150", "150", "-"],
       ["Desk marker", "Static; world origin", "2", "5 by 5", "45", "50", "-"],
       ["Object marker", "Dynamic; tracked cube", "1", "5 by 5", "45", "50", "Cube: 70 mm per side"],
       ["Wooden rail", "Reference object", "-", "-", "-", "-", "387 by 88 by 38 mm, lying flat"]]),
(CAP, f"Table 2.1. The objects in the scene. All markers are from the OpenCV 5 by 5 dictionary. The printed size is the measured black square, and the declared size is the value given to the detector. The distance the detector recovers scales with the size it is given. So the pipeline multiplies every translation from the desk and object markers by 45 divided by 50, which is 0.90, before it uses any object pose."),

(P, f"Figure 2.{F_SETUP} labels the parts of the scene in one colour frame from the sensor. The camera is an Intel RealSense D435. It sits on a fixed support at the edge of the desk and faces the subject from about 1.3 metres away. The subject stays within 2 metres of the camera for the whole experiment, because the depth error of the sensor grows with the square of the distance [37], [38], [58]."),

(IMG, FIG / "ch2_fig_setup.png", 6.3),
(CAP, f"Figure 2.{F_SETUP}. The experimental setup, seen from the RGB-D camera. It shows the subject at the desk, the rail on the drawn working area, the carried cube, and the three ArUco markers (wall, desk, and object)."),

(P, f"The recording is saved as a bag file, which is the recording format of the Intel RealSense software. Each frame holds a colour image and a depth image aligned to it, and a shared frame index says which person and object measurements belong to the same moment. Appendix A describes how the recording was made and how the file is organised."),

(P, f"Figure 2.{F_FLOW} shows how the data flows from the recording through two parallel pipelines. Pipeline A tracks the subject, and later chapters call it the landmark branch. It runs landmark detection, depth fusion and filtering, then the pose recovery of Chapter 5 on the frames where a landmark fails, and then the kinematic solver of Chapter 3. Pipeline B tracks the scene and the object, and later chapters call it the marker branch. It runs marker detection, the scene calibration of Section 2.2, and the world anchoring of Chapter 4. Pipeline B supplies the measurements that Chapter 5 recovers from and that Chapter 7 evaluates against. The two branches share no processing stage. Chapter 6 pairs the finished data at a common render time at the streaming stage and sends it to Unity. Both pipelines run on the one workstation listed in Appendix B."),

(IMG, FIG / "ch2_fig_flow.png", 6.3),
(CAP, f"Figure 2.{F_FLOW}. Overall data flow of the system. Pipeline A (top) tracks the person, Pipeline B (bottom) tracks the scene and object, and the two meet at the streaming stage. Each block names the chapter that develops it."),

(H2, "2.2 Coordinate Frames and Scene Calibration"),

(P, f"Every measurement in this thesis is a position or an orientation, and each one is given in a coordinate frame. A frame is an origin with three axes at right angles. This section names the frames of the thesis and the transformations between them, in standard robotics notation [42], and describes the calibration that fixes the static part of the scene. Chapter 3 and Chapter 4 derive the transformations in full."),

(H3, "2.2.1 The Frames"),

(P, f"The camera frame C belongs to the RGB-D sensor. Its origin is at the colour camera lens. The x axis points to the right of the image, the y axis points down, and the z axis points forward into the scene [10]. The depth of a point is its z coordinate in this frame. Every raw measurement of both pipelines starts out in C. Figure 2.{F_CAM}(a) shows this frame drawn on the sensor, and Figure 2.{F_CAM}(b) shows the Unity frame U defined at the end of this section."),

(IMG, FIG / "ch3_fig_sensor_unity.png", 6.3),
(CAP, f"Figure 2.{F_CAM}. (a) The camera frame C on a front photograph of the D435 sensor (product photograph: Intel). The convention is defined from behind the camera, so in this front view the x axis of the image appears on the reader's left and z comes out of the page toward the reader. The module names mirror the same way. The origin is at the colour camera lens, and every measurement uses this frame once the depth is aligned to the colour image. (b) The Unity frame U, captured in the Unity editor at the root of the avatar rig, with its axes drawn at the origin (x red, y green, z blue). The avatar stands in the T-pose, which is the reference configuration of the model."),

(P, f"The world frame W sits on the desk marker. Its x and y axes lie in the printed plane of the marker, and its z axis points out of the printed face. The desk marker sits on the desk inside the working area, so W is fixed to the desk. Every object pose ends up in W, and Chapter 6 brings the reconstructed body into W as well. The reconstruction then does not depend on where the camera stands."),

(P, f"The wall marker has a frame of its own. It is fixed on a plumb wall behind the working area, and this frame is never used as an origin. Because the wall is plumb, the up axis in the plane of the marker gives the direction of gravity, and the calibration of Section 2.2.2 uses it for that purpose only."),

(P, f"The object frame O is attached to the marker on the cube and moves with it. Its pose is measured on every frame where the marker is detected."),

(P, f"Person space P is the camera frame with the y axis flipped so that it points up. Chapter 3 uses it for the body model, so that heights read upward. The body model then attaches a frame to the torso, called the root frame, and one frame to each shoulder and each elbow. Chapter 3 defines all of them."),

(P, f"The Unity frame U is the frame that the reconstruction of Chapter 6 lives in. Unity uses a left-handed frame with y up, so Chapter 6 converts every pose into U before it draws anything."),

(PM, [T("A transformation carries a point from one frame into another. The pose of a frame B seen in a frame A is written "), X(TAB),
      T(". It is a 4 by 4 matrix that holds a rotation and a translation, and Chapter 3 gives its form in equation (3.2). A point given in B is multiplied by "), X(TAB),
      T(f" to get the same point in A. Figure 2.{F_FRAMES} draws the frames of the scene on one colour frame of the recording and on a top view, with an arrow for each transformation. Table 2.2 lists the transformations and says which ones are fixed by the calibration and which ones are measured on every frame.")]),

(IMG, FIG / "ch2_fig_frames.png", 6.3),
(CAP, f"Figure 2.{F_FRAMES}. The scene and its coordinate frames. (a) The colour frame of the recording used in the worked examples. The frame of the wall marker, the world frame W on the desk marker, and the object frame O on the cube are each drawn by projecting their pose through the colour intrinsics. The camera frame C is the viewpoint of the image itself. Each arrow is one transformation of Table 2.2. (b) The same frames in a top view of the scene, drawn from the calibrated poses, with the clean object path of Chapter 4 in grey and the subject shown at the working distance."),

(TBL, [["Symbol", "Carries a point from", "Into", "Fixed or measured", "Derived in"],
       [M(TCW), "the world frame W", "the camera frame C", "fixed by the calibration", "Section 2.2.2, Chapter 4"],
       [M(TCwall), "the wall marker frame", "the camera frame C", "fixed by the calibration", "Section 2.2.2"],
       [M(TCO), "the object frame O", "the camera frame C", "measured on every frame", "Section 2.4"],
       [M(TWO + r(" = ") + TCWinv + r(" ") + TCO), "the object frame O", "the world frame W", "computed on every frame", "Chapter 4"],
       [M(TWC + r(" = ") + TCWinv), "the camera frame C", "the world frame W", "fixed by the calibration", "Chapter 4"],
       [M(r("F")), "the camera frame C", "person space P", "fixed, the y flip", "Chapter 3, equation (3.1)"],
       [M(Troot), "the root frame", "person space P", "measured on every frame", "Chapter 3"],
       [M(Tsh + r(", ") + Tel), "the shoulder and elbow frames", "their parent frame", "measured on every frame", "Chapter 3"],
       [M(r("S")), "the world frame W", "the Unity frame U", "fixed, y and z swapped", "Chapter 6, equation (6.1)"]]),
(CAP, f"Table 2.2. The transformations between the frames of the thesis. A transformation written with two frame letters carries a point from the second frame into the first."),

(H3, "2.2.2 Scene Calibration"),

# Moved from Chapter 4 Section 4.1 (round 4, C46; build_ch4.py at commit
# d3561d2 lines 94-131). Long sentences re-patterned to the chapter's
# voice; each change is logged in CH2_CONCISION_LOG.md.
(P, f"The three printed markers of Table 2.1 define the scene. Neither the desk marker nor the wall marker moves. The desk marker anchors the world frame, and the wall marker is fixed on a plumb wall well behind the working area. The object marker moves with the cube. The pipeline assumes the scene stays fixed, so it does not track the two static markers. It measures their poses once, over a short window at the start of the recording, and then keeps them as frozen constants for the whole recording."),

(PM, [T("The calibration window is the first ten detections of each static marker. Averaging the ten translations is a plain arithmetic mean, but averaging the ten rotations needs more care. The element-wise mean of rotation matrices is in general not a rotation matrix, because its columns are no longer unit length and no longer at right angles. The pipeline takes that element-wise mean anyway and then projects it back onto the set of proper rotations, which gives the rotation nearest to the mean [45]. The rotation obtained that way is called the chordal mean, and the world anchor is the chordal mean of the calibration rotations. The singular value decomposition gives the projection in closed form. Writing "),  # src: eval/output/scene_calibration_r6bc.json (calib_frames = 10); default in v1/aruco/calibrate_scene.py
      X(Mbar), T(" for the element-wise mean of the calibration rotations, its decomposition is "),
      X(Mbar + r(" = ") + r("U") + r(" ") + r("Σ") + r(" ") + sup(r("V"), r("T"))),
      T(", where the middle factor is the diagonal matrix of singular values. The projection is")]),

(EQ, r("R") + r(" = ") + r("U") + r(" ") + nor("diag") +
     d(r("1, 1, ") + nor("det") + d(r("U") + sup(r("V"), r("T")))) + r(" ") +
     sup(r("V"), r("T")), "2.1"),

(P, f"where the determinant factor keeps the result a rotation instead of a reflection. For a marker that does not move, the ten rotations differ only by detection noise, so the projection barely moves the entries. It is there to make the frozen anchor exactly orthonormal, which every later transformation assumes. Every rotation stays a matrix, as in Chapter 3. The same computation comes back in Chapter 4 as a smoothing filter for the object track."),

(P, f"The anchor is frozen to keep the reconstruction stable. The desk marker keeps being detected after the calibration window, like any other marker. Its detected orientation wanders as the subject moves through the scene and the light on the card changes. An orientation error in the anchor turns the whole reconstructed scene about the anchor, so a point moves in proportion to its distance from the anchor. Re-anchoring the world on each frame would push that wobble into every reconstructed point, the object track included. With the anchor frozen, the world pose of the object on a frame carries only the noise of the object's own detection and nothing from the desk detection on that frame."),

(P, f"Calibration also measures the geometry of the scene around the markers. It rests on one physical assumption, that the wall carrying the wall marker is plumb, so the up axis in the plane of the calibrated wall marker is the direction of gravity. This step is needed because the axes of the world frame are not lined up with gravity. The desk marker card sits on a small stand that tilts it toward the camera so that the camera sees more of the card face. Because of that tilt, the axis out of the printed face is not the vertical."),

(P, f"A second and coarser estimate of the same direction comes from the depth stream. The pipeline fits a plane to the depth pixels in a ring around the desk marker card, after the deprojection of Section 2.3 has turned those pixels into metric points. The plane does not need to be accurate. It only has to fix the sign of the gravity direction and to settle the two-solution ambiguity of the planar pose estimation that Section 2.4 describes. The fitted plane is also the tabletop, so every later height reading has a physical reference surface."),

(P, f"The remaining calibrated quantities follow from those pieces. Table 2.3 lists the whole set with the measurement each one comes from. The height above the tabletop and the cube edge are less direct. The marker card sits at the table surface, so the height of the world origin above the fitted tabletop is the small offset between the two. That offset places the tabletop relative to the anchor. The marker is centred on one face of the cube, so the cube edge is twice the height of the marker centre above the tabletop point beside the resting cube. When the cube is carried from the first frame of a recording and never rests, the pipeline takes the measured edge instead."),

(TBL, [["Quantity", "How it is obtained"],
       ["World anchor pose", "mean translation and chordal-mean rotation of the desk marker over the calibration window"],
       ["Wall marker pose in the world", "calibrated wall pose carried through the inverse anchor"],
       ["Camera pose in the world", "the inverse of the anchor, the transformation from C into W of Table 2.2"],
       ["Gravity direction", "up axis in the plane of the calibrated wall marker, with the sign taken from the depth plane"],
       ["Tabletop plane", "plane fitted to the depth pixels in a ring around the desk marker card"],
       ["World origin height above the tabletop", "the origin's offset along gravity from the fitted plane"],
       ["Object cube edge", "twice the marker centre height above the local tabletop point while the cube rests, or the measured edge"],
       ["Sensor field of view", "the colour intrinsics of the recording"]]),
(CAP, f"Table 2.3. The frozen scene description produced by the static calibration."),

(P, f"The pipeline hands this description to the reconstruction once, before any per-frame streaming begins, and Chapter 6 builds the Unity scene from it. Figure 2.{F_CALIB} draws it, with the clean object path of Chapter 4 added for context."),

(IMG, FIG / "ch4_fig_scene.png", 6.2),
(CAP, f"Figure 2.{F_CALIB}. The calibrated scene of the recording, drawn from the pipeline outputs. It shows the world origin at the desk marker with its three axes, the measured gravity direction, the fitted tabletop plane, and the position of the camera in the world. The clean object track of Chapter 4 is overlaid and coloured by time. The vertical axis is height along the measured gravity. The two horizontal axes are the world x and z levelled against it, so they run flat rather than along the tilted axis arrows at the origin."),

(H2, "2.3 Pose Landmarks from MediaPipe"),

(P, f"Pipeline A starts with MediaPipe Pose. It is an open-source detector from the MediaPipe framework [28], and it runs in real time on ordinary hardware. For each colour frame, it first locates the person and then regresses 33 body landmarks from the face to the feet. Landmark indices are fixed. The pipeline can therefore select the eight required upper-body points directly: shoulders L11 and L12, elbows L13 and L14, wrists L15 and L16, and hips L23 and L24. Every result includes image coordinates, an appearance-derived depth estimate, and a visibility score between 0 and 1. Appendix C gives the detector architecture, the steps that extract the landmarks, and a numerical example."),

(P, f"The pipeline uses only a subset of MediaPipe's output. Because MediaPipe estimates depth from 2D appearance rather than physical sensor measurements, the pipeline discards those values and uses the depth readings from the aligned RealSense stream instead. It then uses the camera intrinsics to project each landmark pixel into metric 3D coordinates (Appendix D). These coordinates are given in the camera frame C of Section 2.2. The pipeline treats landmarks with visibility scores below 0.50 as missing data, so the system does not report coordinates for occluded points. Figure 2.{F_MP} illustrates the full detector output on a sample recording frame."),

(IMG, FIG / "ch2_fig_mediapipe.png", 6.3),
(CAP, f"Figure 2.{F_MP}. MediaPipe Pose output on a mid-task frame of the recording. The eight numbered landmarks (shoulders, elbows, wrists, hips) are the ones this system uses. The other 25 landmarks are drawn without numbers. The leg landmarks below the desk edge are detector guesses for body parts that the desk hides, and the visibility gate removes them."),

(H2, "2.4 Object Pose from ArUco Markers"),

(P, f"Pipeline B gets its measurements from ArUco fiducial markers [29], which have a black square border around a unique binary ID grid. The detector spots candidate square outlines, reads the embedded ID, and refines the four corners to sub-pixel precision. Once supplied with the marker's physical side length, it solves the planar Perspective-n-Point problem [52] to resolve both position and orientation in a single pass. The result is the pose of the marker in the camera frame C. For the object marker this pose is the transformation from O into C of Table 2.2, and it is measured on every frame."),

# The marker table lives in Section 2.1 (Table 2.1) since 2026-09-02;
# the old duplicate table here is removed.
(P, f"The markers that define the working area are listed in Table 2.1 and shown detected in Figure 2.{F_ARUCO}. The wall marker (ID 0, 150 mm) is mounted on a plumb wall and gives the vertical gravity reference. It is printed larger only because it sits farthest from the sensor. The object marker (ID 1, 45 mm) is attached to the front face of the cube. The desk marker (ID 2, 45 mm) is the world origin. The camera pose is expressed relative to it, so the 3D reconstruction does not depend on where the camera stands. Section 2.2.2 describes the static calibration step that averages and freezes the baseline poses of the stationary markers. Appendix E covers corner detection, planar ambiguity, and rotation matrix conversion."),

(IMG, FIG / "ch2_fig_aruco.png", 6.3),
(CAP, f"Figure 2.{F_ARUCO}. ArUco detections on a mid-task frame of the recording. (a) The three detected markers in the full frame. (b) to (d) Each marker enlarged, with its four detected corners drawn in detection order."),

(H2, "2.5 Measurement Filtering"),

(P, f"The raw 3D landmark trajectories carry three kinds of error:"),

(LIN, f"Case A, spikes: an isolated sample jumps far off the local trajectory for one frame, from a depth speckle or a momentary false detection."),
(LIN, f"Case B, gaps: a few consecutive samples are missing, because the visibility gate of Section 2.3 blocked them or the depth sample was invalid."),
(LIN, f"Case C, jitter: every sample carries small broadband noise from detection and depth measurement."),

(P, f"A single smoothing filter cannot solve all three kinds of errors. If a filter is strong enough to remove a sharp spike, it also distorts fast motion. No smoothing filter can fill in missing data gaps either. The pipeline therefore handles each case in a separate stage."),

(P, f"A rolling Hampel test handles case A. The Hampel identifier [53] spots outliers by checking how far a point drifts from the local median. It works well on time-series data because a sudden spike will not pull the median off track the way it pulls a mean [54]. The test looks across a 7-frame window with a threshold set to three robust standard deviations. That value is the window's median absolute deviation multiplied by 1.4826 (Appendix F). A baseline floor of 2 centimetres prevents small sensor noise from triggering the test when the subject is standing still. As movement speeds up, the threshold widens, so rapid hand motions are never flagged as errors. The pipeline discards any spike the test flags and marks it as missing data, which then passes into case B. Figure 2.{F_DESP} shows the test flagging a wrist spike that jumped 2.94 centimetres off track in a single frame."),

(IMG, FIG / "ch2_fig_filter_despike.png", 6.0),
(CAP, f"Figure 2.{F_DESP}. Despiking result on the right wrist of the recording: per-axis raw and filtered trajectories, with the sample flagged by the Hampel test marked."),

(P, f"Linear interpolation handles case B. The interpolation fills interior gaps no longer than 5 frames, a sixth of a second, along a straight line between the two valid endpoints. Longer gaps remain missing, and the pose recovery of Chapter 5 handles them. The recovery restores a joint from the object or from the rest of the arm where a measurement anchors it. Where nothing anchors it, the last angle is held. Figure 2.{F_GAP} shows bridged wrist dropouts from the recording."),

(IMG, FIG / "ch2_fig_filter_gap.png", 6.0),
(CAP, f"Figure 2.{F_GAP}. Gap-bridging result on the right wrist of the recording: short gaps are filled by interpolation, and the replaced samples are marked."),

(P, f"A zero-phase Butterworth low-pass filter then handles case C. The filter follows the design procedure of [55]. The Butterworth family has a flat passband, so it passes the motion without ripple [56]. A fourth-order filter with a 3 Hz cutoff runs forward and backward over the recording [57]. The two passes cancel the phase delay and preserve event timing. Deliberate upper-body motion lies below roughly 5 Hz, so the cutoff leaves the motion intact and removes the jitter. The backward pass needs the whole recording, so the filter can only run offline. The real-time alternative is the One Euro filter [40]. It is a causal low-pass filter that adapts its cutoff to how fast the signal is changing. Chapter 8 measures the lag and the angle cost of the causal filter against the offline one. Appendix F compares the candidate smoothers side by side. They are the Butterworth filter used here, the Savitzky-Golay filter, the rolling median, and the One Euro filter. The Savitzky-Golay filter fits a low-order polynomial over a sliding window [46], and the rolling median replaces each sample by the median of its neighbours. Figure 2.{F_SMOOTH} shows the raw jitter against the filtered track."),

(IMG, FIG / "ch2_fig_filter_smooth.png", 6.0),
(CAP, f"Figure 2.{F_SMOOTH}. Smoothing result on the right-wrist depth of the recording: the raw and filtered tracks over an eight-second span, with the shaded window enlarged below."),

(P, f"The preprocessing writes a separate output and never modifies the raw data, so the unfiltered baseline stays available for the evaluation of Chapter 7 to compare against. Every repaired sample keeps a flag, which separates measured data from filled-in data for later stages. Chapter 3 solves the joint angles from these filtered landmarks. Pipeline B cleans the object track in its own stage, described in Chapter 4, and Chapter 5 uses the cleaned object pose to recover a held wrist."),

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
                if isinstance(c, tuple):
                    add_inline_math(cell.paragraphs[0], c[1])
                    continue
                cell.text = c
                for par in cell.paragraphs:
                    for run in par.runs:
                        run.font.size = Pt(10)
                        if i == 0:
                            run.font.bold = True

out = REPO / "writing" / "v8" / "Chapter_2_Experimental_Setup.docx"
doc.save(out)
print("saved", out, "| items:", len(content))

#!/usr/bin/env python3
"""Build writing/v7/Chapter_6_System_Integration.docx (V7 rewrite round).

Chapter 6 "System Integration and Graphical Reconstruction" against the
V7 TOC: 6.1 Communication Architecture, 6.2 Coordinate System
Conversion, 6.3 Avatar Reconstruction in Unity, 6.4 Scene Reconstruction
in Unity.

METHOD ONLY (user rule 2026-08-28, skill_set/thesis-structure-rules.md):
no accuracy or error numbers (Chapter 7), no latency, cadence or frame
rate numbers (Chapter 8), no validation counts. The Unity-vs-video check
of eval/reports/r5_unity_check.md is internal and is not cited; only its
captured stills are reused as imagery.

Sources for every statement, in the order the sections use them:
  6.1  v2/V2.md, v2/reports/r5_realtime_probe.md,
       v2/integration/run_v2.py, v2/broker/capture_broker.py,
       v2/common/shm_ring.py, v2/person/v2_person.py,
       v2/object/v2_object.py, v2/common/person_shm_v2.py (PSR2),
       v2/common/object_link.py (B->A link), v2/integration/
       v2_integrate.py (merger, PSI2), v1/aruco/send_scene_poses.py
       (PSB2, PSB3).
  6.2  v1/KINEMATIC_MODEL.md sec 3 and v1/kinematics/root_frame.py
       (the y flip F), v1/ARUCO_MODEL.md sec 5 and v1/aruco/frames.py
       (the swap, written S here), v1/INTEGRATION.md sec 1 (the anchor, written A here),
       Unity/Assets/Scripts/IntegratedSceneReceiverV2.cs (anchor node),
       Unity/Assets/Scripts/ArucoSceneReceiver.cs (gravity levelling).
  6.3  Unity/Assets/Scripts/IntegratedSceneReceiver.cs (bone driving,
       AlignArm T-pose forcing, MatchArm subject proportions, uniform
       height scale), IntegratedSceneReceiverV2.cs (tags to colours),
       v2/common/display_lpf.py + eval/DECISIONS.md E-018 (display
       smoother), v1/kinematics/shoulder.py (the 13-angle layout),
       eval/reports/recording_20260825_222315_offset_fit.json (subject
       segment lengths).
  6.4  Unity/Assets/Scripts/ArucoSceneReceiver.cs (BuildStaticScene,
       BuildDeferredScene), v1/aruco/send_scene_poses.py (PSB3 fields).

Figures: writing/v7/figures/ch6_fig_arch.png (make_ch6_arch_fig.py),
ch6_fig_frames.png (make_ch6_frames_fig.py), ch6_fig_unity.png
(make_ch6_unity_fig.py, cropped from eval/output/unity_check_r5 stills).
Citations: writing/v7/references.md ([1]-[57] frozen numbering).
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches

from eqn import r, nor, sub, mat, d, eqArr, add_display_eq

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v7" / "figures"

H1, H2, P, IMG, CAP, TBL, EQ = "h1", "h2", "p", "img", "cap", "tbl", "eq"

F_ARCH, F_FRAMES, F_SCENE = 1, 2, 3

# --- equation-fragment shorthands -------------------------------------
Sm = r("S")
Fm = r("F")
Am = r("A")
Rcam = sub(r("R"), nor("cam"))
tcam = sub(r("t"), nor("cam"))
Rbone = sub(r("R"), nor("bone"))
Rchain = sub(r("R"), nor("chain"))
Rx90 = sub(r("R"), r("x")) + d(nor("-90 deg"))
Rrest = sub(r("R"), nor("rest"))

content = [
(H1, "Chapter 6: System Integration and Graphical Reconstruction"),

(P, "The two branches are complete at this point, and separate. The landmark branch of Chapters 3 and 5 delivers, for every frame, a pelvis position and thirteen joint angles that describe the upper body in person space, together with a statement of how each joint group was obtained. The marker branch of Chapter 4 delivers a frozen description of the room and a world-frame pose of the carried object for every frame, anchored at the desk marker. Neither output is a picture. Both are tables of numbers, and they live in different coordinate frames."),

(P, "This chapter joins them into one rendered scene: a Unity world holding the wall, the desk, the sensor, the moving object and an animated human figure, all in a single frame and all driven from the recorded or live data. Section 6.1 describes how the numbers travel from the processing side to the display side. Section 6.2 develops the coordinate conversions, including the anchor that places the person stream inside the marker world. Section 6.3 describes how the solved angles drive the avatar rig, and Section 6.4 how the measured room is rebuilt around it. The chapter describes the construction only. The accuracy of the reconstruction is measured in Chapter 7, and its cost to run in Chapter 8."),

(H2, "6.1 Communication Architecture"),

(P, "One design rule shapes the whole section. All mathematics stays on the processing side, and the display side, a receiver script running inside Unity, applies finished numbers without solving, filtering or converting anything beyond the fixed transforms of Section 6.2. The numerical code has one implementation and one set of tests. A second implementation inside the game engine would be a second version of the same mathematics, free to disagree with the first, and the disagreement would show up on the screen rather than in a test."),

(P, f"Figure 6.{F_ARCH} shows the running structure. The system runs as four processes: a capture process, one process for each branch, and a merging process that feeds the display. Rounded boxes in the figure are processes, square boxes are shared-memory records, and the box at the left is the source itself, either the sensor or a recorded session."),

(IMG, FIG / "ch6_fig_arch.png", 6.4),
(CAP, f"Figure 6.{F_ARCH}. The integration architecture: the capture process publishes aligned frames into the shared frame buffer, each branch reads the buffer and writes its own record, the landmark branch also reads the object record, and the merger combines both branches for the display."),

(P, "The capture process is the only one that opens the source. Two processes cannot both open one physical camera, so a single owner is required rather than convenient. That owner aligns the depth frame to the colour frame once, stamps each frame with a session clock derived from the sensor's own hardware timestamps, and publishes the pair into a shared frame buffer. The buffer is a fixed number of fixed-size slots in shared memory, with one writer and any number of readers. A reader always takes the newest published slot, under the sequence-counter protocol described below, so a reader that falls behind loses whole frames instead of reading a frame that is being overwritten underneath it. Losing frames is the correct behaviour for a slow consumer on a live stream, and each pipeline counts what it skipped."),

(P, "Aligning the frames inside the capture process has a second consequence that matters for the rest of the thesis. Both branches see the same aligned frame, carrying the same frame index and the same session timestamp, so a shared frame index denotes the same instant on both sides by construction rather than by agreement. It also puts the choice between a recording and a live camera entirely inside one process; everything downstream is written against the buffer and runs the same on either source."),

(P, "The two branches then run as independent processes. The landmark branch reads the shared frame buffer, detects and filters the landmarks, solves the chain of Chapter 3 with the recovery of Chapter 5, and writes one person record per frame. The marker branch reads the same buffer, detects the markers, computes the world pose of the object, applies the cleaning step of Chapter 4, and writes one object record per frame. Neither imports the other's code. The buffer sits below that boundary as shared transport, in the same way the operating system and the sensor library do."),

(P, "Every record is a small block of shared memory with a fixed layout: a four-character code naming the record type, a sequence counter, the frame or tick it describes, and then the payload, written in a fixed byte order. Table 6.1 lists the family. The four-character code lets a reader reject a stream it does not understand before interpreting a single field, and the sequence counter carries the consistency protocol. A writer raises the counter to an odd value before touching the payload and to the next even value after finishing. A reader copies the whole record and then checks that the counter is even and unchanged; if it is not, the reader discards the copy and retries. No locks are involved, the writer never waits for a reader, and a late reader never sees the values it missed."),

(TBL, [["Record", "Code", "Written by", "Rate", "Contents"],
       ["frame buffer", "PSF1", "capture process", "per frame",
        "aligned colour and depth images, frame index, session timestamp, and the sensor intrinsics in the buffer header"],
       ["person record", "PSR2", "landmark branch", "per frame",
        "pelvis position in person space, thirteen joint angles, a live bit for each of the seven joint groups, and a state tag for each group"],
       ["object record", "PSB2", "marker branch", "per frame",
        "object position and orientation in Unity axes, and a live flag lowered when the marker is not measured"],
       ["scene record", "PSB3", "merger", "once",
        "the static scene: desk, wall and camera poses, the gravity direction, the height of the world origin above the tabletop plane, the object cube edge, and the sensor field of view"],
       ["combined record", "PSI2", "merger", "per output tick",
        "tick index and render time, pelvis, the thirteen angles, the object position and orientation, both live fields, the interpolation flags, and the group tags"]]),
(CAP, "Table 6.1. The record family. Every record is fixed size, little-endian, and begins with its four-character code; the per-frame and per-tick records are protected by the sequence counter described in the text."),

(P, "The person record carries more than angles. A live bit per joint group states whether that group was measured on this frame, and a state tag per group states how its value was obtained: measured, held from the last valid value, or constrained, solved on this frame from a landmark the recovery of Chapter 5 rebuilt or limited in its per-frame change. The record describes seven groups this way: the torso root and, for each arm, the shoulder swing, the shoulder twist and the elbow. Carrying the state alongside the value costs two bytes, and it lets the display show where each value came from, which Section 6.3 turns into a visible distinction."),

(P, "One link crosses between the branches, and it runs in one direction only. The landmark branch reads the marker branch's object record, because the wrist recovery of Chapter 5 needs the object pose. The read takes whatever record is currently stable, through the same sequence-counter protocol. The object pose is then brought back into camera coordinates in three steps: the streamed Euler triple is recomposed into a rotation matrix, the axis swap that Section 6.2 defines is undone, which returns the pose to the desk world, and the world-to-camera transform of Chapter 4 places it in camera coordinates. Each step is the exact inverse of a fixed or calibrated transform, so the round trip returns the pose the marker branch measured. A skew guard rejects an object record whose frame index is more than a few frames away from the frame index the landmark branch is processing, so a stalled marker branch cannot feed a stale pose into the recovery. The link is optional: with it switched off the solver runs on landmarks alone."),

(P, "The merger is the only stage that reads both branches. It keeps a short buffer of recent samples from each and emits at a fixed output rate, rendering not the newest sample but the state of the world at a render time that trails capture by a fixed and declared delay. The delay makes the pairing possible: at the render time both branches usually already have a sample on each side, so the merger can place each stream at that one instant. Each stream leaves the merger in one of four states. A sample that lands on the render time is measured. A render time that falls between two samples close enough together is interpolated, on the angles component by component with wrap-around handled at the angle seam, and on the object pose by a straight line in position and a shortest-arc path in orientation. The merger holds the last value across a gap too long to bridge. When a stream returns from a long gap, the merger blends it back in over a few ticks rather than snapping to it."),

(P, "The record tells the receiver which of the four applies, so the display never has to guess whether a value is a measurement, a bridge across a dropout, or a hold. The joint-group tags travel through the same buffer, ordered measured, then held, then constrained. Across the interval between two interpolated samples each group takes the later of its two tags in that order, and on a held tick every group is raised to at least held, so a tag never reports a value as fresher than it is. Person and object ride in one record, so however slow either branch runs, the reconstruction can never show a person from one instant beside an object from another."),

(P, "Startup is arranged so that nothing observes a half-built system. Each process signals that it has finished initializing and then waits for a common start signal, and the capture process opens the source only once every consumer is attached. When the scene calibration of Chapter 4 is computed from the live stream rather than read from a frozen file, the capture process is released first, the calibration runs against the buffer, and the pipelines start against its result."),

(H2, "6.2 Coordinate System Conversion"),

(IMG, FIG / "ch6_fig_frames.png", 6.4),
(CAP, f"Figure 6.{F_FRAMES}. The four coordinate frames and the three maps between them. The landmark branch reaches the display through the flip and then the anchor; the marker branch reaches it through the swap."),

(P, f"Figure 6.{F_FRAMES} places the four frames of the system side by side with the maps between them. The landmark branch works in person space: the camera frame with the y axis flipped upward by the diagonal matrix F of Section 3.1. The marker branch works in the desk-anchored world of Chapter 4, whose third axis points out of the printed face of the desk marker. Unity draws in a left-handed frame with the second axis upward [47], so the world reaches it by the swap S that exchanges the second and third coordinates,"),

(EQ, sub(r("p"), r("U")) + r(" = ") + Sm + r(" ") + sub(r("p"), r("w")) + r(",        ") +
     sub(r("R"), r("U")) + r(" = ") + Sm + r(" ") + sub(r("R"), r("w")) + r(" ") + Sm + r(",        ") +
     Sm + r(" = ") + mat([[r("1"), r("0"), r("0")],
                          [r("0"), r("0"), r("1")],
                          [r("0"), r("1"), r("0")]]), "6.1"),

(P, "with the rotation conjugated rather than multiplied on one side, because a rotation is a map from the frame to itself and both its input and its output have to change basis. The swap is symmetric and equal to its own inverse, so Section 6.1 can undo it by applying it a second time. Its determinant is minus one, so it changes the handedness of the frame, and the flip F of Chapter 3 has determinant minus one for the same reason. Each map on its own is the single handedness change that a right-handed measurement frame needs to reach a left-handed display frame."),

(P, "The two results do not land in the same place, so one further transform is needed. A person-space point is still expressed relative to the camera, while a world point is expressed relative to the desk marker. Chapter 4 calibrated the camera's own pose in the world and froze it, so one more transform closes the gap. Take a person-space point q. Undoing the flip returns the point to raw camera coordinates, since F is its own inverse. The calibrated camera orientation then rotates it into the world. Applying the swap carries it into the display frame, and the calibrated camera position, mapped by the same swap, supplies the offset. Collecting the three rotations into one matrix,"),

(EQ, r("p") + r(" = ") + Am + r(" q") + r(" + ") + Sm + r(" ") + tcam + r(",        ") +
     Am + r(" = ") + Sm + r(" ") + Rcam + r(" ") + Fm, "6.2"),

(P, "where R with the camera subscript is the calibrated camera orientation in the world frame and t with the camera subscript the calibrated camera position. The determinant of A is the product of three determinants, minus one, plus one and minus one, so it is plus one. The two handedness changes cancel, A is a proper rotation, and the person arrives in the scene without a mirror image. The construction is a change of basis composed with a rigid motion, the standard chaining of homogeneous transformations [42]."),

(P, "The composition factorizes in a way that is simple to implement. Inserting the swap twice in the middle changes nothing, and regrouping gives A as the product of the calibrated camera orientation conjugated into display axes with the fixed matrix that the swap and the flip form together. That fixed pair is the swap of equation (6.1) times the flip of equation (3.1), and multiplying the two out negates the second column of the swap, which is the matrix of a rotation of minus ninety degrees about the x axis,"),

(EQ, eqArr(
    Am + r(" = ") + Sm + r(" ") + Rcam + r(" ") + Fm + r(" = ") + Sm + r(" ") + Rcam + r(" ") + d(Sm + r(" ") + Sm) + r(" ") + Fm + r(" = ") + d(Sm + r(" ") + Rcam + r(" ") + Sm) + r(" ") + d(Sm + r(" ") + Fm) + r(","),
    Sm + r(" ") + Fm + r(" = ") + mat([[r("1"), r("0"), r("0")],
                                        [r("0"), r("0"), r("1")],
                                        [r("0"), r("1"), r("0")]]) + r(" ") +
    mat([[r("1"), r("0"), r("0")],
         [r("0"), r("−1"), r("0")],
         [r("0"), r("0"), r("1")]]) + r(" = ") +
    mat([[r("1"), r("0"), r("0")],
         [r("0"), r("0"), r("1")],
         [r("0"), r("−1"), r("0")]]) + r(" = ") + Rx90), "6.3"),

(P, "The first factor is the orientation the display already uses to place the sensor body in the scene, so the receiver needs no new mathematics. It creates one static node, the person anchor, at the calibrated camera pose composed with that constant rotation, and every quantity that arrives from the person record is applied through this node. Positions pass through it as points. Rotations pass through it by multiplication on the left. That operation needs to be stated precisely, because a change of basis on a rotation is conjugation and conjugation is the wrong operation here. Conjugating a body rotation by the anchor and applying the result to the rig would cancel the camera orientation out of the pose, leaving the figure correctly placed at the desk but turned the wrong way, and no check on position would notice. The anchor is not changing the basis of the person's pose; it is stating where the person stands and which way person space itself is turned, so it pre-multiplies."),

(P, "The display frame the receiver draws in is levelled, and the world frame is not. Section 6.4 describes how the scene is levelled; the point for this section is that both branches inherit it the same way, as local poses beneath one levelled parent, so the data is never rewritten."),

(P, "Orientations travel as Euler angles rather than as matrices or quaternions, in the fixed order used by the animation system: the z rotation first, then x, then y, each about the parent frame's axes [47]. Chapter 3 defined the solved angles against this convention, so the receiver reassembles each rotation directly from the three numbers it receives. In the other direction, Section 3.4 decodes a rotation matrix into that Euler triple, and the same code runs on both branches."),

(H2, "6.3 Avatar Reconstruction in Unity"),

(P, "The avatar is a standard humanoid character with a full skeleton, of which the receiver drives five bones: the spine bone at the base of the trunk, which takes the root rotation and the per-frame placement, and the upper arm and forearm of each side, which take the arm chains. The bones are located by name when the scene starts. Everything else, the hands, the head, the spine segments above the root and the whole body below the hips, keeps its rest pose. The legs stay still by necessity: the system tracks eight upper-body landmarks, so no leg measurement exists, and posing the legs from imagination would put invented motion on the screen next to measured motion."),

(P, "The thirteen streamed angles reassemble five rotations. The first three angles are the root Euler triple and rebuild the trunk rotation directly. The next three angles are the shoulder swing pair and twist of Section 3.4, applied as three axis-angle factors about the up, forward and right axes in that order. The elbow follows as two angles applied the same way about up and forward. The last five angles repeat that pattern for the left arm, with every component except the twist reversed in sign, which is the sagittal mirror of Chapter 3 expressed on the display side. Writing the trunk rotation as R with subscript 0, the shoulder rotation as R with subscript 1 and the elbow rotation as R with subscript 2, each reconstructed joint rotation then enters the chain composition,"),

(EQ, eqArr(
    sub(Rchain, nor("spine")) + r(" = ") + sub(r("R"), r("0")) + r(",        ") +
    sub(Rchain, nor("upper arm")) + r(" = ") + sub(r("R"), r("0")) + r(" ") + sub(r("R"), r("1")) + r(",        ") +
    sub(Rchain, nor("forearm")) + r(" = ") + sub(r("R"), r("0")) + r(" ") + sub(r("R"), r("1")) + r(" ") + sub(r("R"), r("2")) + r(",")), "6.4"),

(P, "so the spine bone takes the trunk rotation alone, the upper arm takes the trunk rotation followed by the shoulder, and the forearm takes both followed by the elbow. Each product is the forward kinematics of Chapter 3 read from the root outward, one factor per joint."),

(P, "The composition needs three corrections before the figure looks like the recorded person. Two corrections belong to the avatar setup used for the reconstruction shown in Figure 6.3, and are applied once, when the scene starts. The third runs on every output tick, before the record leaves the processing side, so it reaches any setup that reads the record."),

(P, "The first correction sets the frame the composition is composed against. The world rotation written to a bone is"),

(EQ, Rbone + r(" = ") + Am + r(" ") + Rchain + r(" ") + Rrest, "6.5"),

(P, "where A is the anchor rotation of Section 6.2, the chain product of equation (6.4) sits in the middle, and R with the rest subscript is the bone's own rest rotation, captured when the scene starts. That last factor absorbs the rig's authored axis conventions as a constant. The composition is only correct if the captured rest pose is the pose Chapter 3 defines as the zero of every arm angle, namely the T-pose with the arms straight out along the model's own lateral axes. A character authored with a slight droop in the arms, or with a small bend at the elbow, would otherwise carry that droop into every rendered frame, added silently to every solved angle. That setup therefore forces the T-pose before it captures anything: it measures each arm segment's direction in the pose the character starts in and applies the minimal rotation that brings it onto the model's lateral axis, upper arm first and then forearm. A rig that already starts in the T-pose is left untouched. The five rest rotations are captured after the arms are aligned and after the rig is sized as described next."),

(P, "The second correction, in the same avatar setup, fixes proportions. The transfer sends joint angles and one point, so the rendered hand ends up wherever the rig's own bone lengths put it, and a rig whose forearm is longer than the participant's will reach past the object even when every angle is right. The character is first scaled uniformly, when the scene starts, to the height of an average adult, 1.70 metres. The trunk and the arms are then matched segment by segment against lengths measured from the participant's own landmark data: a hip-to-mid-shoulder length of 47.9 centimetres, a right upper arm of 25.6 centimetres and a left of 26.2 centimetres, a right forearm of 25.2 centimetres and a left of 24.7 centimetres. Each length is the median of that segment over the whole landmark track of the occlusion recording of Chapter 7, the same participant, and the reconstruction of the recording in Figure 6.3 uses those proportions. The rig reads them once, when the scene starts. Chapter 7 quotes clean-frame medians for two of these segments, taken over the frames its detectors accept; those differ from the whole-track values by at most 0.30 centimetres. The trunk is scaled first, because it moves the shoulder anchors, and the arms afterwards, so they are measured on the already-scaled rig. Each scale is uniform on its bone. A uniform scale is a scalar multiple of the identity, which commutes with every rotation, so resizing the character moves where its bones are without touching how the angle transfer composes. The hand is given back the forearm's factor and keeps the upper arm's, so a longer-armed subject also gets a proportionally larger hand at the object."),

(P, "The third correction is a display smoother, applied to the angles and the pelvis on their way into the output record. The solver of Chapters 3 and 5 changes state in short ramps rather than steps, because its own guards limit how far a joint may move between frames, and the eye reads those ramps as a jump. A plain low-pass filter cannot remove them. A linear filter with a gain of one passes a constant input unchanged, and a ramp is a constant slope, so once the transient has died out the filter's output climbs at the ramp's own slope, a fixed lag behind it; the filter rounds the corners of a transition without shortening it. The smoother therefore has two parts. A first-order low-pass with a fixed gain rounds corners and removes isolated single-frame spikes, and a cap on how far any angle may move in one output tick bounds what the ramp can do on screen. The smoother runs on the processing side but changes only the displayed values; the recorded tables that Chapters 7 and 8 analyse are written before it."),

(P, "The rig is placed by its hip. Each tick, the streamed pelvis point, the midpoint of the two hip landmarks, is mapped through the anchor, and the character's root is translated so that the spine bone lands on that point. The root rotation then orients the trunk about it. Position and orientation therefore come from two separate parts of the record, and neither is inferred from the other."),

(P, "The live reconstruction draws what the record says about the origin of each value. A joint group that is not measured on a tick carries a small sphere on its bone, at the hip for the torso root, on the upper arm for the shoulder swing and on the forearm for the elbow, coloured red where the value is held and blue where it is constrained, the tags of Section 6.1. The twist group carries no sphere of its own. A smaller amber sphere at the pelvis marks a pose that crossed a real dropout by interpolation or is ramping back after a long occlusion. The blue and the amber markers belong to that setup; the capture behind Figure 6.3 streams only the live mask, so there a group that carries a sphere is drawn red whether its value is held or constrained. Held values still pose the rig, because a held angle is a defined angle, but a viewer can tell a measured value from a held one and a held one from a rebuilt one."),

(H2, "6.4 Scene Reconstruction in Unity"),

(P, "The room is built from the static scene record, which arrives once before the stream begins and is never updated. It carries the calibrated desk, wall and camera poses, the measured gravity direction, the height of the world origin above the fitted tabletop plane, the measured cube edge and the sensor's vertical field of view, all already expressed in display axes by the swap of Section 6.2."),

(P, "Levelling comes first. The world frame's up direction is the desk marker's face normal, and the marker card sits on a leaning stand, so drawing the room in raw world axes would show a tilted wall and a tilted desk on a level screen. The receiver creates one parent node for the whole reconstruction and rotates it by the shortest rotation that carries the measured gravity direction onto the screen's vertical. Every streamed pose is then applied beneath that node as a local pose. The tilt lives in one transform, and because gravity was derived in Chapter 4 from the plumb wall marker, the displayed wall comes out vertical and the displayed desk top horizontal by construction."),

(P, "The wall is a thin slab coplanar with the calibrated wall marker, extended down to the floor level and a short distance above the marker. The desk is a horizontal slab whose top surface lies on the tabletop plane fitted from the depth data in Chapter 4. The slab runs from a margin behind the desk marker to just past the object's position on the first streamed frame, so it covers the working area the task uses. A fixed length centred on the marker would be simpler and wrong, because it would extend across the far edge into the space where the participant stands. The participant's legs are not tracked, so the figure would then appear to stand inside the table. The desk width, the extent of the wall slab, the slab thicknesses, the legs and the floor are fixed dimensions the recording never measures, and they only complete the room around the measured geometry."),

(P, "A marker plate sits at each calibrated marker pose, carrying the same printed pattern the physical marker carries, so the reconstruction and the colour frame can be compared by eye. The object is a cube of the measured edge length. Its marker is printed on one face, and the pose measurement locates the marker plate, so the cube body is placed half an edge behind the plate along the face normal. The cube is driven every tick from the combined record, and it changes colour with the record's own fields, red for a held pose and amber for an interpolated one, the same meanings the avatar's markers carry."),

(P, "The sensor is drawn as a small body at the calibrated camera pose, which is the same pose the person anchor of Section 6.2 is built from. A second view camera is attached to it, looking along the optical axis with the calibrated vertical field of view at the sensor's own aspect ratio, and its image is rendered as an inset over the main view. The inset shows the view the reconstruction assigns to the real camera, so it can be compared with the recorded colour frame of the same instant by eye."),

(P, f"Figure 6.{F_SCENE} shows the finished reconstruction on two frames of the recording, rendered from that virtual sensor rather than from a free camera, so the view matches the one the real sensor had. The rig is posed from the record the recovery layer of Chapter 5 emits. Under the live mask of Section 6.3 a red sphere therefore marks each of those groups the record does not carry as measured, held and constrained alike. The root carries one at the hip on both frames, because the depth samples at the hip pixels land on the rail in front of the body and the torso repair rebuilds the root from frame 5 onward. Chapter 3 states the size of that offset on frame 533. The idle left arm carries one on its upper arm and one on its forearm, since the detector does not measure that arm on either frame."),

(P, "On frame 114 the right arm reaches forward and down to the cube on the desk, foreshortened because it points at the sensor, and the rendered hand stops about 9 centimetres short of the measured wrist. The elbow is bent by only 14 degrees there, so the shoulder twist is held at its last observed value by the rule of Section 5.6, and a held twist swings a nearly straight forearm; the rig's own segment lengths carry the rest. No sphere marks the twist, by the rule of Section 6.3. Section 7.3.1 measures what a nearly straight arm costs the recovery. On frame 700 the elbow is bent by 31 degrees, the twist is measured, and the hand sits on the cube within 2 centimetres of the measured wrist."),
# frame 114: Rel_y -14.4 deg, tag_2 (R twist) held; rig-length FK wrist
# 9.9 cm from the measured wrist. frame 700: Rel_y -31.0, twist measured,
# 2.4 cm. eval/output/recovery_r6b/angles_recovery.csv +
# eval/inspect/check_v1_overlay.py fk_arm_dirs with rig lengths 0.256/0.252

(IMG, FIG / "ch6_fig_unity.png", 6.4),
(CAP, f"Figure 6.{F_SCENE}. The reconstruction as Unity draws it, seen from the virtual sensor at the calibrated camera pose, on two frames of the recording. (a) Frame 114, during the desk move: the right arm reaching forward and down to the cube on the desk, with the wall marker, the desk marker and the tracked cube in the measured room; the red spheres mark the groups the record does not carry as measured, the rebuilt root at the hip and the idle left arm's shoulder and elbow groups; the right shoulder's twist is held on this frame as well and is not drawn. (b) Frame 700, during the slide: the hand on the cube on the rail."),

(P, "The reconstruction is complete at this point. The landmark branch supplies the person, the marker branch supplies the object and the room, one levelled parent holds both, one record drives each tick, and every drawn value carries the tag that says how it was obtained."),

]

references = {
    42: "J. J. Craig, Introduction to Robotics: Mechanics and Control, 3rd ed. "
        "Upper Saddle River, NJ, USA: Pearson Prentice Hall, 2005.",
    47: 'Unity Technologies, "Unity scripting reference: Transform, '
        'Quaternion," Unity Documentation. [Online]. Available: '
        "https://docs.unity3d.com/ScriptReference/",
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
    elif kind == P:
        doc.add_paragraph(item[1])
    elif kind == EQ:
        add_display_eq(doc, item[1], item[2])
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
        for i, row_ in enumerate(rows):
            for j, c in enumerate(row_):
                cell = t.cell(i, j)
                cell.text = c
                for par in cell.paragraphs:
                    for run in par.runs:
                        run.font.size = Pt(10)
                        if i == 0:
                            run.font.bold = True

out = REPO / "writing" / "v7" / "Chapter_6_System_Integration.docx"
doc.save(out)
print("saved", out, "| items:", len(content))

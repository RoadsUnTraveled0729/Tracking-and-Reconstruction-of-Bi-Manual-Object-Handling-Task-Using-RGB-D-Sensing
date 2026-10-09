#!/usr/bin/env python3
"""Build writing/v4/Chapter_5_System_Integration.docx.

v3 port: content carried per the approved v2-to-v3 map; per-chapter References
section dropped (skill rule 12); references dict kept for build_thesis.py.

All numbers come from the pinned artifacts (integration/dataset/,
aruco/dataset/scene_calibration.json) via writing/v2/scripts/ch5_numbers.py
and validate_integration_output.txt; nothing is invented. Structure follows
ToC v3 sections 5.1-5.4.

v5 trim round (2026-08-03, supervisor directive): new Figure 5.2, the shared
memory block diagram (ch5_fig_shm.png from make_ch5_shm_fig.py, layout from
integration/send_integrated_scene.py); old Figures 5.2-5.6 renumbered to
5.3-5.7. Factorization and two-checks paragraphs of 5.2.1 tightened; the
5.2.2 bug story kept as an iteration record.

Figure caption numbers vs files: Figure 5.4 uses ch5_fig4_preview.png and
Figure 5.5 uses ch5_fig3_rig.png (the preview appears earlier in the text
than the rig diagram).
"""
from docx import Document
from docx.shared import Pt, Inches

FIG = "/home/luo/Desktop/New_SandBox/writing/v2/figures/"
from eqn import r, nor, sub, sup, hat, frac, mat, d, eqArr, add_display_eq, add_display_math

H1, H2, H3, P, IMG, CAP, TBL, EQ = "h1", "h2", "h3", "p", "img", "cap", "tbl", "eq"
MATH = "mth"  # displayed, unnumbered worked-example mathematics

content = [
(H1, "Chapter 5: System Integration and Graphical Reconstruction"),

(P, "The two pipelines are now complete but separate. The landmark branch of Chapters 2 and 3 produces, for every frame, a pelvis position and thirteen joint angles that describe the upper body in person space, the camera-aligned frame with the vertical axis flipped upward. The marker branch of Chapter 4 produces a frozen description of the room and a world-frame pose of the carried object for every frame, anchored to the desk marker. Neither output is an image; both are tables of numbers. This chapter turns those numbers into a single rendered scene: a Unity world containing the wall, the desk, the sensor, the moving object, and an animated human figure, all in the same coordinate frame and driven frame by frame from the recorded data."),

(P, "The chapter is organized around the three problems that integration poses. Section 5.1 describes how the numbers travel from Python, where everything is computed, into Unity, where everything is drawn. Section 5.2 develops the coordinate conversions, including the one genuinely new piece of mathematics in this chapter, the anchor transform that places the person stream inside the marker world. Section 5.3 describes how the solved joint angles drive the avatar rig, and Section 5.4 how the reconstructed scene is built and what the finished world looks like. Throughout, one distinction is kept sharp: this chapter verifies that the transfer into Unity is exact, meaning that Unity displays the same numbers the pipelines computed. Whether those numbers are accurate, meaning close to physical truth, is the separate question that Chapter 6 answers."),

(H2, "5.1 Communication Architecture"),

(P, "A design decision made early shapes everything in this section: all mathematics lives in Python, and Unity is a display and logging layer only. The pipelines' numerical code is validated by the test suites of the previous chapters, and re-implementing any of it in a second language would create a second copy that could silently disagree with the first. Unity therefore receives finished poses and applies them to scene objects; it never solves, filters, or converts anything beyond the fixed transforms described in Section 5.2."),

(P, "The two sides communicate through packets. Each stream is one small binary record of fixed size, little-endian, beginning with a four-byte magic code that names the packet type, so a receiver can immediately reject a stream it does not understand. The default transport is a shared memory file, a small memory-backed file provided by the operating system: the Python sender writes the record into the file, and the Unity receiver maps the same file and reads it every rendered frame. With one writer and one reader, consistency is guaranteed by a sequence counter rather than by locks. The writer increments the counter to an odd value before touching the payload and to the next even value after finishing, and the reader copies the record, then checks that the counter is even and unchanged; if not, the copy was torn by a concurrent write and is simply discarded and retried. Figure 5.2 draws the record as a block of memory with the two protocols beside it. Reads cost no system call and no copy on the sender side, which matters for the real-time variant of Chapter 7, where the same transport carries live data. The same packet can instead be sent over UDP to port 9750 on the local machine. Both transports were implemented and carry the identical packet; shared memory was chosen as the default over UDP because it is exactly the channel the live variant of Chapter 7 needs, and the UDP path is kept as a drop-in alternative for setups where the two processes cannot share a memory file."),

(IMG, FIG + "ch5_fig1_comm.png", 6.3),
(CAP, "Figure 5.1. The communication architecture. Python senders replay the pipelines' output tables into fixed-size shared memory packets; Unity receivers map the same files and apply the poses. The integrated configuration in the bottom lane carries the person and the object in one packet."),

(TBL, [["packet", "channel", "size", "cadence", "contents"],
       ["PSE1", "person landmark stream", "180 B", "per frame", "8 landmark positions in the camera frame, with per-landmark valid flags"],
       ["PSA5", "arm angle stream", "72 B", "per frame", "13 joint angles plus a per-joint live mask"],
       ["PSB3", "static scene stream", "100 B", "once", "static desk, wall, and camera poses, gravity direction, tabletop drop, cube edge, sensor field of view"],
       ["PSB2", "object stream", "44 B", "per frame", "object position and Euler angles plus a live flag"],
       ["PSI1", "integrated scene stream", "108 B", "per frame", "pelvis position, the 13 angles, the object pose, and both live masks in one record"]]),
(CAP, "Table 5.1. The packet family. Every packet is little-endian, fixed size, and begins with a four-byte magic code; per-frame packets are protected by the sequence counter described in the text."),

(IMG, "/home/luo/Desktop/New_SandBox/writing/v5/figures/ch5_fig_shm.png", 6.3),
(CAP, "Figure 5.2. The shared memory transport drawn as a memory block: the 108-byte integrated record with its byte offsets, the sender's write protocol on the left, and the receiver's read protocol on the right. The sequence counter is odd while a write is in progress and even when the record is stable, so a reader whose two counter readings disagree, or are odd, discards its copy and reads again."),

(P, "Figure 5.1 and Table 5.1 list the five packet types. The first two belong to the landmark branch alone: the landmark packet carries the eight raw upper-body points for the skeleton display, and the angle packet carries the thirteen solved angles that drive the rig. The next two belong to the marker branch: the scene packet is written once and describes everything static, and the object packet carries the moving object's pose every frame. The last packet exists for the integrated scene of this chapter. It carries the pelvis, the thirteen angles, and the object pose together in one 108-byte record, and this bundling is deliberate: if the person and the object travelled in separate streams, a slow frame on either side could present the reader with a person from one instant and an object from another. Inside a single packet they can never desynchronize. The two source tables come from the same recording, so their rows already align one to one by frame index; the packet simply preserves that alignment across the process boundary."),

(P, "The data integrity conventions of the earlier chapters travel with the data rather than being cleaned away before display. The angle packets carry a per-joint live mask, set by the occlusion fallback of Chapter 2 whenever a joint is holding its last valid angle instead of measuring a new one, and the object packets carry a live flag that is lowered on the frames where the carrying hand covers the marker. The receivers render held joints with a red marker sphere and the held object with a red tint, so a viewer of the reconstruction always sees which parts of the pose are measurement and which are memory. On the evaluation recording the integrated stream spans 899 frames with strictly increasing frame numbers; the person solves live on all 899 frames and the object is live on 877 of them."),

(H2, "5.2 Coordinate System Conversion"),

(H3, "5.2.1 Python to Unity Coordinate Mapping"),

(P, "Each pipeline already ends with its own conversion into Unity conventions, and the two conversions are different because the two pipelines live in different frames. The landmark branch works in person space: camera coordinates with the y axis flipped so that up is positive, obtained by the diagonal map F with entries one, minus one, one applied to every camera-frame point, as established in Chapter 3. The marker branch works in the desk-anchored world and reaches Unity through the axis swap P that exchanges the second and third coordinates, as established in Chapter 4. Each map has determinant minus one, which is exactly right for a single conversion between a right-handed measurement frame and Unity's left-handed frame. The problem this section must solve is that the two results do not land in the same place. A person-space point is still expressed relative to the camera; a world point is expressed relative to the desk marker. Rendering both in one scene requires one more transform, and only one, because the camera's pose in the world was calibrated once in Chapter 4 and is frozen."),

(P, "The derivation reads from right to left, composing three maps that are each already known [41]. Take a person-space point q. First undo the flip: F is its own inverse, so F applied to q recovers the point in raw camera coordinates. Second, rotate camera coordinates into the world with the calibrated camera orientation, the rotation part of the inverted anchor transform of Chapter 4. Third, swap the world result into Unity axes with P. Collecting the three rotations into a single matrix M, and adding the camera's world position mapped through the same swap, a person-space point q lands in the scene at"),
(EQ, r("p") + r(" = ") + r("M") + r(" ") + r("q") + r(" + ") + r("P") + r(" ") + r("t") + r(",        ") +
     r("M") + r(" = ") + r("P") + r(" ") + sub(r("R"), nor("cam")) + r(" ") + r("F"), "5.1"),
(P, "where R_cam is that calibrated camera orientation and t is the calibrated camera position in the world. The determinant of M is the product of the three determinants, minus one times plus one times minus one, which is plus one: the two handedness flips cancel, so M is a proper rotation and the person maps into the scene with no residual mirror image. Figure 5.3 summarizes the geometry."),

(IMG, FIG + "ch5_fig2_anchor.png", 6.1),
(CAP, "Figure 5.3. The coordinate spaces and the anchor. Both pipelines start at the camera frame; Pipeline A flips y into person space, Pipeline B rotates into the desk world and swaps into Unity. The anchor M joins the two paths, and its two handedness flips cancel to a proper rotation."),

(P, "The transform has a factorization that makes its implementation nearly free. Insert P twice in the middle of M, which changes nothing because P is its own inverse, and regroup: M equals P R P times P F. The first factor, P R P, is the calibrated camera orientation conjugated into Unity axes, which is precisely the rotation Unity already uses to render the sensor body in the scene. The second factor, P F, multiplies out to a single fixed matrix, and evaluating it shows that it is exactly a rotation of minus ninety degrees about the x axis. The receiver therefore creates one static node, called the person anchor, whose transform is the camera pose composed with that constant rotation, and parents nothing else to the mathematics: every per-frame quantity from the person stream is applied through this node unchanged. Computed from the pinned calibration, the anchor's own orientation comes out within a few degrees of the identity, Euler angles 4.5, minus 1.0, and minus 1.8 degrees, with the camera at Unity position 0.003, 0.168, minus 0.567 metres. The near-identity is not a coincidence but a statement about the physical setup: the camera sat almost level at the desk edge, so person space and the levelled scene were already nearly aligned."),

(P, "Two checks give confidence that M is the right matrix. The first is numerical: M is orthonormal and proper to machine precision. The second is physical and uses the one quantity both pipelines estimate independently, the direction of gravity: the landmark branch fits it from depth data, the marker branch derives it from the plumb wall marker. Mapping the depth-derived direction through M and comparing it with the scene gravity reproduces the calibrated disagreement between the two estimates, 5.03 degrees, exactly. A pure rotation must preserve that angle, and a wrong one would not."),

(P, "The running example continues, and because every factor of equation (5.1) is frozen calibration data, the anchor can be written out numerically. Composing the swap, the calibrated camera orientation, and the flip gives"),
(MATH, r("M") + r(" = ") + mat([
    [r("0.9994"), r("0.0305"), r("−0.0183")],
    [r("−0.0318"), r("0.9964"), r("−0.0786")],
    [r("0.0159"), r("0.0792"), r("0.9967")]])),
(P, "recognizably close to the identity, which is the numerical form of the near-level-camera observation above, and the camera's calibrated world position maps to P t = (0.0026, 0.1675, -0.5673) m. At frame 100 the streamed pelvis, the midpoint of the two hip landmarks in person space, is"),
(MATH, r("q") + r(" = (−0.0316, −0.0215, 1.2645)")),
(P, "a little over a metre in front of the camera. Equation (5.1) lands it in the scene in two steps, the rotation first and then the offset:"),
(MATH, eqArr(
    r("M") + r(" q") + r(" = (−0.0554, −0.1198, 1.2582)"),
    r("p") + r(" = ") + r("M") + r(" q") + r(" + ") + r("P") + r(" t") + r(" = (−0.0528, 0.0476, 0.6909)"))),
(P, "about five centimetres above the world origin, which Chapter 4 placed a millimetre below the tabletop surface, and 0.69 metres out from the desk marker on the far side of the table. That is a standing person at the desk with the pelvis just above tabletop height, matching the person in the video. The same frame's object pose arrives in the integrated packet verbatim from the filtered world track of Chapter 4, matching that table to the last digit."),

(H3, "5.2.2 Bone Rotation Mapping and Axis Correction"),

(P, "Positions transfer through the anchor as points; rotations need more care, for two reasons. The first is convention: Unity applies Euler angles in the fixed order z, then x, then y, and the solved angles of Chapter 3 were defined against exactly this convention [47], so the receiver reassembles each joint's rotation with three axis-angle factors in that order and no numerical conversion is needed. The second is the rig itself. The avatar is a standard humanoid FBX model whose bones carry their own authored local axes; the artist who built the rig chose rest orientations that do not coincide with the identity, including roughly eight degrees of built-in droop in the arms. Applying a solved rotation directly to such a bone would add the pose to those authored offsets and bend the figure wrong."),

(P, "The correction is calibrated rather than assumed. At spawn, before any packet is applied, the receiver records each driven bone's world rotation as its rest correction C. From then on, the world rotation applied to a bone is the product of three factors read right to left: first C, the authored rest pose, which absorbs the rig's own axis conventions as a constant; then the solved chain rotation for that bone, the root rotation alone for the hip, the root times the shoulder for the upper arm, and the root times the shoulder times the elbow for the forearm, exactly the compositions of Chapter 3; and finally the anchor rotation, which carries the whole person-space pose into the scene. In the standalone person scene the anchor factor is the identity and the formula reduces to the chain times the rest pose."),

(P, "The order of that last multiplication hides the one serious bug of the integration work, and the way the bug was found changed the project's methodology, so it is worth recording. The anchor must pre-multiply: anchor times chain times rest. The first implementation instead conjugated, anchor times chain times anchor inverse times rest, which looks equally plausible as a change of basis. The conjugation cancels the anchor's orientation out of the applied pose, so the rig rendered facing away from the desk with its legs inside the table, while every positional check still passed, because positions were mapped separately and correctly. The bug was localized by plotting the streamed data in Python before Unity ever saw it: the plotted person faced the sensor to a mean of 4.5 degrees, so the data was right and the fault had to be in the Unity composition. Figure 5.4 shows that pre-Unity plot for the evaluation recording. Two lessons became standing rules: validators must assert orientation-level facts, because positional checks are blind to an entire class of orientation errors, and every stream is now plotted in Python and checked against physical reality before it is sent to Unity."),

(IMG, FIG + "ch5_fig4_preview.png", 6.3),
(CAP, "Figure 5.4. The plot-first stage: the integrated stream rendered in Python in the levelled desk world before anything is sent to Unity, in perspective and from above. Wall and floor planes, the sensor, the object trajectory, both wrist trajectories, the pelvis path, and the person's root axes are all drawn from the streamed numbers; the person stands between the sensor and the wall, facing the sensor across the desk."),

(P, "One more property of the transfer deserves a sentence because it makes the display scaling of the next section safe. The rig is displayed at a uniform scale, every axis multiplied by the same factor, and a uniform scale is a scalar multiple of the identity matrix, which commutes with every rotation. Scaling the avatar therefore changes where its bones are but not how the angle transfer composes; none of the rotation mathematics above is affected."),

(H2, "5.3 Avatar Reconstruction in Unity"),

(H3, "5.3.1 Unity Joint Hierarchy and Motion Mapping"),

(P, "The avatar is a humanoid FBX character whose skeleton contains many bones, of which the receiver drives exactly five: the hip bone at the base of the spine, which receives the root rotation and the per-frame translation, and the right and left upper arm and forearm bones, which receive the arm chains. The bones are located by name at spawn, their rest rotations are captured as the corrections of the previous section, and the rest of the skeleton, fingers, head, spine segments, and everything below the hips, keeps its authored rest pose. The legs stay still by necessity rather than choice: the pipeline tracks the eight upper-body landmarks only, so no leg measurement exists, and posing legs from imagination would violate the data integrity rules the rest of the system follows. Figure 5.5 shows the driven hierarchy and the rotation composed for each bone."),

(IMG, FIG + "ch5_fig3_rig.png", 6.1),
(CAP, "Figure 5.5. The driven bones of the avatar rig and the world rotation applied to each. The rest corrections C are captured at spawn; the anchor pre-multiplies every bone; below the hips the rig keeps its rest pose because no leg landmarks are measured."),

(P, "The rig is placed in the scene by its hip. Each frame, the receiver maps the streamed pelvis point, the midpoint of the two hip landmarks, through the anchor and translates the rig's root so the hip bone lands exactly on that point; the root rotation then orients the trunk about it. Body size is handled at spawn: the FBX is authored about 3.25 metres tall, so the receiver applies a uniform display scale of 0.523 to present a 1.70 metre person, the height of the recorded subject. Because the scale is uniform it commutes with the rotation transfer, as noted above. What the scale does not fix is proportion: the avatar keeps the rig's own limb ratios, its forearm about 1.6 times the length of the subject's, because only the hip position and the joint angles are transferred, not the skeleton geometry. The consequences of that mismatch for hand placement are measured in Chapter 6 rather than hidden here."),

(P, "The live mask arrives with every angle packet, and the receiver turns it into the same visual language used throughout the project: a joint that is holding its last valid angle, because its landmarks were occluded on that frame, carries a small red marker sphere on the corresponding bone. The held joints still pose the rig, since a held angle is a defined angle, but the viewer can always distinguish measured motion from remembered motion."),

(H3, "5.3.2 Mapping Kinematic Model to Unity Avatar"),

(P, "The thirteen streamed angles reconstruct five rotations. The three root angles reassemble the trunk rotation in the z, x, y application order. The shoulder angles arrive as the swing-twist decomposition of Chapter 3, two swing angles and one twist, and are reassembled as three axis-angle rotations about the scene's up, forward, and right axes in that order; the elbow contributes its two angles the same way. The left arm uses the mirrored convention established in Chapter 3, flipping the signs of the two swing components and keeping the twist, so one code path serves both arms. Each reconstructed joint rotation then joins the chain composition and the rest correction of Section 5.2.2 and is written to its bone as a world rotation."),

(P, "The receiver logs what it applies, so the exactness of the transfer can be measured end to end. On the evaluation recording, the logged hip bone position reproduces the anchor applied to the streamed pelvis, recomputed offline from first principles, to 0.0007 millimetres across 899 frames, and the received pelvis matches the sent pelvis to 5 times 10 to the minus 7 metres, the quantization of a 32-bit float. In the standalone arm validation of Chapter 3's pipeline, the rig's four arm-segment directions, logged every displayed frame and compared against independent predictions from the solved angles, agree to a maximum of 0.0001 degrees over 897 frames. The applied object poses match the world table to 0.0006 millimetres. These numbers say one specific thing: between Python and the rendered bone there is no loss beyond float rounding. They deliberately say nothing about whether the solved angles describe the real person well; that is measurement accuracy, and it is the subject of Chapter 6."),

(H2, "5.4 Unity Scene Reconstruction"),

(H3, "5.4.1 Marker Coordinate System and World Frame"),

(P, "The scene side of the display starts from the world frame of Chapter 4: the desk marker's own coordinate frame, x and y in the printed plane, z out of the face, mapped into Unity by the swap P. Inside Unity the mapped frame reads naturally: the marker's x axis becomes scene right, the marker's face normal becomes scene up, and the marker's y axis becomes scene forward. The static scene description arrives once in the scene packet: the calibrated desk, wall, and camera poses already converted to Unity positions and Euler angles, the gravity direction, the height offset between the world origin and the fitted tabletop plane, the calibrated cube edge, and the sensor's vertical field of view."),

(P, "One subtlety separates the world frame from the displayed frame. The world's up axis is the desk marker's face normal, and the marker stand was measured in Chapter 4 to lean 4.75 degrees off gravity. Rendering the room in raw world axes would therefore draw a slightly tilted wall and a slightly tilted desk on a level screen. The receiver instead creates a parent node for the whole reconstruction and rotates it so that the streamed gravity direction, in Unity components minus 0.018, 0.997, minus 0.081, becomes the scene's vertical; all streamed poses are then applied as local poses under this parent. The measured tilt lives in the parent transform, the data is untouched, and the displayed wall is exactly vertical and the displayed desk top exactly horizontal by construction, because the wall marker is plumb and gravity was derived from it."),

(H3, "5.4.2 Wall, Table, and Object Pose Estimation"),

(P, "Every pose in the displayed room is a calibrated quantity from Chapter 4; nothing is placed by hand. The wall is a slab coplanar with the calibrated wall marker, extended down to the floor. The desk is a slab whose top surface lies on the depth-fitted tabletop plane and whose extent is data-driven, spanning the region between the desk marker and the object's travel, so the displayed table covers the physical table's working area rather than an assumed rectangle; its legs and the floor are decorative context at standard height. The object is a cube of the calibrated 70 millimetre edge with the marker drawn on its front face, driven every frame by the streamed pose and tinted red on the frames where the marker was hidden and the pose is held. The sensor is a small camera body at the calibrated camera pose, which is also the pose the person anchor of Section 5.2 composes with. Marker plates with identity labels sit at every calibrated marker pose as a visual cross-reference."),

(P, "The sensor body carries one more display device: a second Unity camera parented to it, looking along the sensor's optical axis with the calibrated vertical field of view of 43.1 degrees at the sensor's 4 by 3 aspect ratio. Its image is rendered as a picture-in-picture inset over the main view. This inset is the reconstruction's claim about what the real camera saw, and because the real camera's frames exist, the claim is checkable by eye frame by frame: the low desk-edge viewpoint of the evaluation recording puts the desk in the lower half of the inset with the person's torso above it and the carried cube at hand height, matching the real colour frames."),

(IMG, FIG + "ch5_fig5_scene_unity.png", 6.1),
(CAP, "Figure 5.6. The reconstructed scene from the marker branch alone, before the person is added: vertical wall slab with its marker, desk with the marker plates and the object cube on its top, sensor body at the calibrated camera pose, and the sensor's own view as the picture-in-picture inset at the upper right."),

(H3, "5.4.3 Scene Representation in Unity"),

(P, "Figure 5.6 shows the scene receiver's output for the evaluation recording with the person stream absent: the room as the marker branch measured it. The geometric assertions made in the running scene are exact where construction makes them exact, the wall 0.0000 degrees off vertical and the desk top 0.0000 degrees off horizontal under the gravity-aligned parent, and float-limited where data flows, the applied object poses matching the world table to 0.0006 millimetres. The logged display loop showed 898 of the 899 streamed frames, sampling the stream at its own rate. Of the 22 frames the stream marks as held rather than measured, the hand-covered frames of Chapter 4 in their short interior gaps and the trailing gap, the 21 that fell within the displayed set rendered with the red tint; the remaining one coincides with the single frame the display loop skipped."),

(P, "The integrated scene adds the person. Its receiver is a subclass of the scene receiver, so the room, the packet machinery, and the inset come along unchanged, and it adds the person anchor node, the rig driving of Section 5.3, the per-frame root translation, and the red held-joint markers. Startup is arranged so the configurations cannot conflict: the integrated receiver activates only when the integrated stream exists, the standalone scene receiver yields in that case, and the standalone person receivers are disabled at start so no two scripts fight over the same bones. A global monitor camera frames wall, desk, object, sensor, and person together. Figure 5.7 shows the result on the evaluation recording: the avatar stands at the desk in mid-transfer with the cube at its hand, and the inset reproduces the layout of the real sensor view."),

(IMG, FIG + "ch5_fig6_integrated.png", 6.3),
(CAP, "Figure 5.7. The integrated reconstruction: the avatar, driven by the landmark branch, carries the cube tracked by the marker branch, in the room reconstructed by the marker branch, all in one desk-anchored world. The inset at the upper right is the reconstruction's sensor point of view."),

(P, "The pinned validation of the integrated stream runs twenty automated checks and passes all of them on the evaluation recording. Beyond the anchor mathematics and the exactness results already quoted, the checks assert facts about physical plausibility that no stage of the system enforces by construction, which makes them informative: the pelvis stays at desk-working height, between 3 centimetres below and 32 centimetres above the tabletop plane, and between 0.35 and 0.60 metres from the object; the person faces the sensor across the desk with a mean facing error of 4.5 degrees and a 95th percentile of 13.0 degrees; and the pelvis clears the desk's far edge by at least 22.9 centimetres, so the avatar never stands inside the table. Each of these is a statement about two independent measurement chains landing in one world and still describing a physically coherent scene."),

(P, "One further number from that validation is quoted here only as a bridge. On the frames where the object is in motion, its trajectory stays within grasp of the nearest wrist, a median of 15.0 centimetres, and its velocity correlates with that wrist's at 0.843. Those numbers are the first quantitative contact between the two pipelines' measurements, and unpacking them, the geometry of the grip, the decomposition of the offset, and what the residuals say about the accuracy of the whole system, is the work of the next chapter."),

]

references = {
41: 'J. J. Craig, Introduction to Robotics: Mechanics and Control, 3rd ed. Upper Saddle River, NJ, USA: Pearson Prentice Hall, 2005.',
47: 'Unity Technologies, "Unity scripting reference: Transform, Quaternion," Unity Documentation. [Online]. Available: https://docs.unity3d.com/ScriptReference/',
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

out = "/home/luo/Desktop/New_SandBox/writing/v5/Chapter_5_System_Integration.docx"
doc.save(out)
print("saved", out)

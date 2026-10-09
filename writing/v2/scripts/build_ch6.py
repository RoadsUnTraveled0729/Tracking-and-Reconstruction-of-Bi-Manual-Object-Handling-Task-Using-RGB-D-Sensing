#!/usr/bin/env python3
"""Build writing/v2/Chapter_6_Experimental_Design_and_Evaluation.docx.

All numbers come from the pinned artifacts (validate_aruco_output.txt,
validate_aruco_328_output.txt, validate_integration_output.txt,
analyze_object_offset_output.txt, validate_occlusion_output.txt,
scene_calibration.json, thesis/A1+A3+B1+C1, OBJECT_OFFSET.md) plus the
scenario timeline computed by writing/v2/scripts/ch6_numbers.py; nothing is
invented. Structure follows ToC v3 sections 6.1-6.6.
"""
from docx import Document
from docx.shared import Pt, Inches

FIG = "/home/luo/Desktop/New_SandBox/writing/v2/figures/"
H1, H2, H3, P, IMG, CAP, TBL = "h1", "h2", "h3", "p", "img", "cap", "tbl"

content = [
(H1, "Chapter 6: Experimental Design and Evaluation"),

(P, "The previous chapters established that every stage of the system computes what it claims to compute: the solver reproduces synthetic joint angles to fractions of a microdegree, the scene calibration reproduces its own world table to machine precision, and Unity displays the streamed numbers exactly. None of that says how close the reconstruction is to the physical event in front of the sensor. This chapter asks that question, and it begins by being honest about what can and cannot be measured. No motion capture reference was available, so there is no external ground truth for the person's joints. The evaluation therefore rests on three layers of evidence, each weaker than a reference system but each independent of the others. The first layer is synthetic truth: the kinematic mathematics was graded against generated datasets with known answers in Chapter 3, and those results are only cited here. The second layer is constructional truth: the scene is built from markers of known printed size mounted on a plumb wall and a level desk, so lengths, verticals, and the tabletop plane are known by construction and every scene measurement can be checked against them. The third layer, and the centre of this chapter, is cross-pipeline agreement: the landmark branch and the marker branch observe the same carried object through two independent measurement chains, and the distance between their two accounts of the same motion is an in-situ measurement of the whole system's accuracy."),

(P, "The chapter follows the structure of the experiment itself. Section 6.1 describes the object handling scenarios that were recorded and what each phase of the motion stresses. Section 6.2 documents the sensor and marker placement, including a two-recording comparison that turned placement into a measured design lesson rather than an assumption. Sections 6.3 and 6.4 evaluate the two measurement branches separately, landmarks first and markers second. Section 6.5 brings them together into the reconstruction fidelity result, the headline accuracy of the integrated system. Section 6.6 closes with a qualitative reading of the rendered scene against the real video."),

(H2, "6.1 Object Handling Scenarios"),

(P, "The evaluation recording, recording 20260224_083945, is a single continuous take of 899 frames, 30.0 seconds at 30 frames per second, in which a person standing at the far side of the desk handles the 70 millimetre marker cube: lifting it off the desk, carrying and turning it, passing it between hands, parking it back on the desk for roughly ten seconds, and finally picking it up again with a changed grip. All three scenario types named below therefore occur inside one uninterrupted stream, which is deliberate. Transitions are where tracking systems fail, and a protocol of separate, carefully staged clips would have hidden exactly the events that matter: the moment a hand covers the marker, the moment the object leaves a hand, the moment a wrist disappears behind the carried box. Figure 6.1 shows the timeline of the take as measured by the marker branch itself: the marker's height above the tabletop, its speed, and its accumulated rotation. Two supporting recordings complement the main take: recording 20260225, used in Chapter 3 to validate simultaneous two-arm tracking, and recording 20260328, an alternative camera placement analysed in Section 6.2."),

(IMG, FIG + "ch6_fig1_timeline.png", 6.3),
(CAP, "Figure 6.1. The evaluation take as measured by the marker branch: marker height above the tabletop, marker speed, and cumulative rotation over the 30 second recording. The shaded band is the parked stretch, 13.4 to 23.5 seconds, during which the cube rests on the desk and no object-to-hand relationship exists."),

(H3, "6.1.1 Lifting"),

(P, "The lifting phases are visible in the top panel of Figure 6.1 as the transitions between two well-separated height bands. While the cube rests on the desk, the marker centre sits at a median 2.9 centimetres above the measured tabletop plane, against a nominal value of half a cube edge, 3.5 centimetres, for a marker centred on a face of a 70 millimetre cube. While carried, the marker rides between roughly 11 and 22 centimetres above the tabletop. The two bands never blur into each other, which makes height above the tabletop a clean classifier: a frame is treated as carried when the marker is more than 6 centimetres above the plane, and 586 of the 899 frames qualify. This classification matters for everything in Section 6.5, because a grip vector is only defined while a hand actually holds the box. Lifting also stresses the vertical geometry of the scene in a way level carrying does not: it checks that the tabletop plane, measured once during calibration, is where the object physics says it is. The parked cube rests on the reconstructed desk surface to within 4.2 millimetres, and the resting band of the height trace is flat to a few millimetres across the whole ten second parked stretch."),

(H3, "6.1.2 Rotating"),

(P, "The person does not carry the cube like a tray; they turn it continuously, and the bottom panel of Figure 6.1 quantifies how much. The orientation track sweeps a cumulative 511 degrees of rotation over the take, more than a full turn, while the net orientation change between the first and last frame is only 26 degrees: the box is rotated far and mostly rotated back. The largest single-frame orientation step in the filtered track is 2.7 degrees, consistent with hand motion at 30 frames per second rather than with estimation jumps. Rotation is the stress test for two specific parts of the system. For the marker branch it exercises pose estimation across a wide range of viewing angles, including the shallow angles where planar pose estimation is least stable, as discussed in Chapter 4. For the integration analysis of Section 6.5 it is what makes the grip question sharp: because the box turns, any offset between the marker and the holding hand rotates with it, and the horizontal direction of that offset sweeps essentially the full circle, plus and minus 178 degrees, over the video. A constant offset in the world frame could not survive that; a constant offset in the object's own frame is exactly what Section 6.5 finds."),

(H3, "6.1.3 Passing and Transferring"),

(P, "Across the carried portion of the take the box changes hands repeatedly: the nearest wrist is the left one on 72 percent of all frames and the right one on 28 percent, and after the parked stretch the person picks the cube back up with a visibly different grip than before. Passing is the scenario that couples the two pipelines' failure modes together. When a hand wraps around the cube it can cover the marker, which costs the marker branch its measurement: the object marker is undetected on 22 of the 899 frames, in short groups during regrips. Symmetrically, the carried box can occlude the wrist that holds it from the sensor's viewpoint, which degrades the landmark branch; Section 6.5 shows this asymmetry directly, with the fully visible right wrist tracked several times more tightly than the half-occluded left one. The transfer events also give the evaluation its per-hand structure: since each hand cups the box differently, the grip vector must be fitted separately per holding hand, and a regrip after parking shows up as a small shift within the left hand's fitted vector."),

(H2, "6.2 Sensor and Marker Placement"),

(P, "The physical instrumentation is deliberately minimal: one RGB-D sensor and three printed markers [9]. Table 6.1 lists the markers with their sizes and roles, and Figure 6.2 draws the measured geometry to scale, using only coordinates from the pinned scene calibrations. The desk marker, 50 millimetres, lies flat on the tabletop and defines the world frame; every other pose in the system is expressed relative to it. The wall marker, 150 millimetres, hangs plumb on the wall about 2.9 metres from the desk marker and 0.85 metres above the tabletop plane, and serves two purposes: it is the gravity reference from which the levelled scene is built, and it is the far-field probe used to measure how stable the world anchor really is, since any wobble in the desk anchor is amplified by the 3.2 metre lever arm to the wall. The object marker, 50 millimetres on a face of the 70 millimetre cube, is the only moving marker. The sensor sat at the near edge of the desk, 0.17 metres above the desk marker and 0.57 metres behind it, looking across the tabletop at the person; its field of view, 55.6 by 43.1 degrees, covers the working volume and the wall behind it."),

(TBL, [["element", "size", "placement", "role"],
       ["desk marker, id 2", "50 mm", "flat on the tabletop", "world frame origin; anchor for every pose in the system"],
       ["wall marker, id 0", "150 mm", "plumb on the wall, 2.9 m away, 0.85 m above the tabletop", "gravity reference; far-field stability probe"],
       ["object marker, id 1", "50 mm on the 70 mm cube", "one face of the carried cube", "the moving object; graded against the wrist track in Section 6.5"],
       ["RGB-D sensor", "", "desk edge, 0.17 m above and 0.57 m behind the desk marker", "sole camera; both pipelines read the same recording"]]),
(CAP, "Table 6.1. Markers and sensor of the evaluation setup. All placement numbers are read from the pinned scene calibration, not from design drawings."),

(IMG, FIG + "ch6_fig2_layout.png", 6.3),
(CAP, "Figure 6.2. The measured scene geometry, side and top view, drawn from the two pinned calibrations. Both camera placements are shown: the desk-edge camera of the evaluation recording (224) and the high camera of the comparison recording (328). The blue dots in the top view are the carried object's 1.94 metre path."),

(P, "Placement was not left as an assumption; it was measured as an experiment. The same scene, with identical markers, was recorded twice: once with the camera at the desk edge, recording 224, and once with the camera mounted high, 0.58 metres above the desk marker and looking down at the scene, recording 328. Both recordings pass the full validation of Section 6.4, 21 checks each, so the comparison in Table 6.2 is between two working configurations, not between success and failure. The desk-edge camera wins every metric, and not by a little. The per-frame drift of the world anchor is four times smaller in position and nine times smaller in orientation, and the wall's apparent motion in the desk frame, the end-to-end stability measure, is five times smaller in position and four times smaller in rotation. The mechanism is geometric: the anchoring marker lies flat on the desk, so a desk-edge camera sees it at a steep, information-rich angle at half a metre, while a high camera sees it foreshortened, and every fraction of a pixel of corner noise on the anchor multiplies across the whole scene. The practical lesson, which held everywhere it was tested, is that camera placement relative to the anchor marker matters more than marker size at these scales [27]. The high recording does contribute one clean result: with the cube resting on the desk throughout, its object marker is detected on all 899 frames, confirming that the 22 dropped object frames of the evaluation recording are caused by hands, not by the marker system."),

(TBL, [["measure", "desk-edge camera (224)", "high camera (328)"],
       ["camera position relative to the desk marker", "0.17 m up, 0.57 m back", "0.58 m up, 0.36 m back"],
       ["wall marker mean reprojection error", "0.060 px", "0.203 px"],
       ["desk anchor position drift, p95", "0.20 mm", "1.09 mm"],
       ["desk anchor orientation drift, p95", "0.088 deg", "0.815 deg"],
       ["wall position deviation in the desk frame, p95", "5.8 mm", "28.3 mm"],
       ["wall rotation deviation in the desk frame, p95", "0.54 deg", "2.38 deg"],
       ["validation result", "21 of 21 checks pass", "21 of 21 checks pass"]]),
(CAP, "Table 6.2. The placement experiment: the same scene and markers recorded from two camera positions, graded by the same validator. The desk-edge camera wins every stability metric; camera placement relative to the anchor marker matters more than marker size at these scales."),

(H2, "6.3 Accuracy of Landmark-Based Tracking"),

(P, "The landmark branch has no external reference to be graded against, so its evaluation is built from internal cross-checks, each of which would expose a different failure. The first check is that the detector's confidence signal actually separates measurement from guessing. MediaPipe always outputs a position for every landmark, visible or not [39]; an occluded wrist still gets coordinates, and the per-landmark visibility score is the only warning. The evaluation recording provides direct evidence that the gate is needed and works: during the model's warm-up on frames 0 to 9, the left elbow and wrist are reported up to about two metres from any plausible position while their visibility climbs from 0.001 toward 0.5, and the visibility gate removes exactly those 19 landmark cells and nothing else; on the rest of the recording the gated positions are unchanged. The second check is metric: the depth that turns a pixel into a 3-D point is cross-checked against an independent estimate wherever one exists. At the frame 100 wrist of the running example, the depth-derived range and the marker-derived range of the object held in that hand agree to about two millimetres, as computed in Chapter 2."),

(P, "The smoothing stage is evaluated by measurement rather than by choice of habit. Table 6.3 repeats the comparison from Chapter 4's filtering discussion, run on the evaluation recording: each candidate filter is scored on shake, the residual frame-to-frame jitter at rest, and on fidelity, the deviation from the despiked raw track during fast wrist motion. The chosen zero-phase Butterworth filter at 3 hertz reduces shake five-fold relative to raw, from 10.2 to 1.9 millimetres, at the same fast-motion fidelity as a Savitzky-Golay fit [44]. The One Euro filter [40] shows the smallest shake of all but pays 28.4 millimetres of deviation during fast motion, which is not smoothing error but causal lag; that disqualifies it offline, while leaving it the natural candidate for the real-time variant of Chapter 7, where zero-phase filtering is impossible. One repair outside the filter proper deserves its number: the edge backfill described in Chapter 2, which fills the warm-up gap at the start of the recording, reduces the largest single-frame angle step in the streamed output from 60.3 to 11.8 degrees, turning a visible snap of the avatar's arm into ordinary motion."),

(TBL, [["method", "shake at rest (mm)", "fast-motion deviation (mm)"],
       ["raw landmarks", "10.2", ""],
       ["Savitzky-Golay, window 9, order 2", "2.8", "4.8"],
       ["rolling median, window 9", "2.9", "3.9"],
       ["Butterworth 3 Hz, zero phase (chosen)", "1.9", "4.8"],
       ["Butterworth 2 Hz, zero phase", "1.5", "5.3"],
       ["One Euro (causal)", "1.1", "28.4"]]),
(CAP, "Table 6.3. Landmark smoothing alternatives measured on the evaluation recording. Shake is the residual frame-to-frame jitter at rest; deviation is measured against the despiked raw track during fast wrist motion. The One Euro filter's deviation is causal lag, which excludes it offline and reserves it for the real-time system."),

(P, "The occlusion behaviour is the one part of the landmark branch that can be graded against exact truth, because the truth can be manufactured. Starting from the fully verified recording, landmarks are masked over known frame ranges and the full pipeline is rerun; the unmasked solve is then exact ground truth for everything the fallback should reproduce. Table 6.4 summarises the six scenarios and the 33 automated checks, all of which pass. The pattern to read from the table is graceful degradation with honest bookkeeping: a blocked wrist freezes only the two angles it makes unobservable while everything else continues to solve exactly; a blocked shoulder is survived by rebuilding the torso frame from the opposite shoulder, at a measured cost of at most 1.53 degrees; even total pose loss holds every angle and recovers exactly. During a hold the frozen joint drifts from the truth by 1.4 to 7.8 degrees in these scenarios, which is simply the motion that occurred while the joint was blocked; the system's answer to that is not to hide it but to flag it, and every held joint is marked in the live mask that travels with the data and is rendered in red downstream. One in-situ noise indicator closes the section: the landmark-measured upper arm lengths differ between sides, 0.225 metres on the left against 0.279 on the right, though the person is symmetric. MediaPipe segment lengths are not constant, and this asymmetry, driven by depth noise and partial occlusion of whichever arm holds the box, previews the left-right accuracy asymmetry that the integrated evaluation measures precisely in Section 6.5. The definitive accuracy number for the landmark branch, one centimetre median against an independent chain when sight lines are clean, is deferred to that section, because it is a property of the two pipelines together."),

(TBL, [["blocked landmark (frames)", "expected behaviour", "measured result"],
       ["right wrist, 3 frames (300 to 302)", "the filter bridges it; nothing holds", "wrist within 0.30 mm, angles within 0.08 deg"],
       ["right wrist, 45 frames (400 to 444)", "elbow and twist hold; all else live", "live joints exact; hold constant; exact recovery"],
       ["right elbow, 45 frames (500 to 544)", "whole right arm holds; rest live", "exact"],
       ["left hip, 30 frames (600 to 629)", "root holds; arms solve against the held root", "arms match an independent recompute exactly"],
       ["right shoulder, 30 frames (750 to 779)", "root rebuilt from the left shoulder; right arm holds", "root within 1.53 deg; left arm exact"],
       ["whole pose, 10 frames (700 to 709)", "all 13 angles hold", "exact hold and exact recovery"]]),
(CAP, "Table 6.4. The synthetic occlusion scenarios and their outcomes, 33 automated checks in total, all passing. Truth is the unmasked solve of the same recording, so every comparison is exact. Every scenario outputs on all 899 frames."),

(H2, "6.4 ArUco Tracking Accuracy"),

(P, "The marker branch is graded by 21 automated checks on the evaluation recording, all passing, and the same suite passes on the comparison recording of Section 6.2. Coverage comes first: the desk anchor is detected on all 899 frames, the object marker on 877, missing only while a hand covers it, and the wall marker on 841, dropping out when the person walks in front of it, which costs nothing since the wall is calibrated once and used as a cross-check. Image-level precision is high: mean corner reprojection errors are 0.060 pixels for the wall, 0.158 for the desk, and 0.183 for the object, with the worst single frame at 0.47 pixels. The world anchor itself is effectively rigid: recomputed independently on every frame, the desk marker's pose moves with a 95th percentile of 0.20 millimetres and 0.088 degrees over the whole recording, and the ten-frame calibration snapshot that froze the world had already measured the same stability, a mean deviation of 0.13 millimetres and 0.06 degrees across its samples."),

(P, "The strongest test is camera invariance, because it checks the whole chain end to end: if the world is truly anchored to the desk, then the wall, recomputed through the camera on every frame, must not move in the desk frame even as detection noise moves the camera. Its measured apparent motion has a 95th percentile of 5.8 millimetres and 0.54 degrees, and the position part decomposes cleanly into two explained pieces: 5.3 millimetres along the camera-to-wall ray, the monocular range noise expected when a 150 millimetre marker is read at 3.4 metres, and 4.0 millimetres laterally, which is bounded by the measured desk-anchor drift multiplied by the 3.2 metre lever arm, a derived bound of 7.7 millimetres rather than a hard-coded tolerance. Range is also cross-checked against physics: the pose-estimated distance to each marker is compared with the median depth reading over the same pixels, an independent measurement chain inside the same camera, and the biases are 5.3 millimetres at 3.38 metres, 4.3 millimetres at 0.58 metres, and 0.6 millimetres at 0.91 metres. This check is designed to catch a specific silent failure: pose estimation infers range from apparent size, so a wrongly configured marker size would scale these distances proportionally and the depth comparison would expose it immediately."),

(P, "The moving object needs one more evaluation, of its filter. The object track is despiked, bridged across the short hand-cover gaps, and smoothed frame to frame, and the filter operates under an asserted honesty bound: it may not move any measured frame by more than the raw pose jitter itself, 15 millimetres. Measured, it moves them by a median of 1.2 millimetres with a maximum of 11.6, well inside the bound, while cutting the frame-to-frame step at the 95th percentile from 10 to 4.9 millimetres and eliminating the hold-and-reacquire pops, up to 2.2 centimetres and 3.4 degrees, that raw dropouts had caused. Interior gaps are bridged geometrically, but the trailing 12-frame gap at the end of the recording is held rather than extrapolated, and streams with its detected flag lowered, rendered as a red tint in the scene. The filtered track is what Section 6.5 grades against the wrists."),

(H2, "6.5 Reconstruction Fidelity"),

(P, "Everything before this section evaluated one pipeline at a time; this section grades them against each other, and the reason the comparison means something is independence. The two branches share no code, no model, and no measurement channel: the person track comes from a learned pose detector reading color images plus stereo depth, while the object track comes from classical corner geometry reading the color images alone. They meet only through the anchor transform of Chapter 5, which was calibrated once from static markers. Agreement between them therefore cannot be circular; it can only mean that two unrelated instruments measured the same physical motion. The instrument that links them is the carried cube, and the physical premise is elementary: the cube has no actuator, so whenever it moves, a hand is moving it, and its trajectory must shadow a wrist."),

(P, "The premise holds quantitatively. On the 46 frames where the object is genuinely in motion, displacement above 3 centimetres over a quarter-second window, the marker centre stays within a median 15.0 centimetres of the nearest wrist, 95th percentile 17.4, always within grasp; the pooled velocity correlation between object and wrist is 0.843, and their velocity directions agree to a mean cosine of 0.858. The 15 centimetre gap is not error, it is geometry: the marker sits on a face of the box while the landmark is the wrist joint, and the whole distance from marker face to far side of the box to palm to wrist joint intervenes. The question is whether that gap behaves like rigid geometry or like noise, and the frame in which one asks decides the answer. In the world frame the offset is anything but constant: its horizontal direction sweeps plus and minus 178 degrees as the box is carried and turned. Rotated into the object's own frame, it collapses into a single constant vector per holding hand, shown in Table 6.5. The right hand's grip vector is constant to better than 2 centimetres on every axis over 249 frames, direct evidence that a rigid physical relationship is being measured, not fitted. Each component has a physical reading: along the marker normal, both hands sit 8 to 11 centimetres behind the marker face, of which 3.5 centimetres is the half-cube from face to centre and the rest is the far half of the box plus the distance from palm to wrist joint; the in-plane components are where each hand happens to cup the box, different per hand, which is exactly why one constant per hand is the right model and one global constant is not."),

(TBL, [["holding hand", "frames", "grip vector (x, normal, z) cm", "per-axis std (cm)"],
       ["left", "314", "(+3.8, -8.2, +8.6)", "3.8, 2.8, 2.5"],
       ["right", "249", "(-11.0, -10.6, +5.3)", "1.8, 0.9, 0.8"]]),
(CAP, "Table 6.5. The fitted grip vectors: the wrist's position in the object marker's own frame, averaged over carried frames per holding hand. The right hand, whose wrist stays fully visible to the sensor, is constant to better than 2 cm on every axis."),

(P, "Subtracting the grip geometry leaves the measurement error of the whole system, and Table 6.6 states the result, computed on the 563 carried frames where both chains measure rather than interpolate. While the right hand holds the box, with its wrist fully visible, the two pipelines agree on the wrist's position to a median of 1.0 centimetre, 95th percentile 3.8; this is the accuracy floor of the integrated system. While the left hand holds it, the carried box itself half-occludes that wrist from the sensor, and the residual grows to a median of 4.6 centimetres, the same asymmetry the segment-length noise of Section 6.3 foreshadowed. Over all carried frames the median is 3.3 centimetres with a root mean square of 4.2. Velocity tells the same story from a second angle: the object-wrist velocity correlation is 0.842 over the carried frames, collapsing to 0.273 over the whole video only because the parked stretch contributes ten seconds in which both velocities are noise around zero. Figure 6.3 shows the full analysis. The reading of Table 6.6 is the central claim of the thesis evaluation: two fully independent measurement chains, linked only by a calibrated static transform, agree on a moving point to about one centimetre when sight lines are clean, and to four or five centimetres when the carried object occludes the view, and the degradation is attributable, frame by frame, to a named physical cause."),

(TBL, [["segment", "frames", "median residual", "p95", "note"],
       ["right hand holding", "249", "1.0 cm", "3.8 cm", "wrist fully visible; the two-pipeline floor"],
       ["left hand holding", "314", "4.6 cm", "8.9 cm", "wrist half-occluded by the carried box"],
       ["all carried frames", "563", "3.3 cm", "7.3 cm", "RMS 4.2 cm"]]),
(CAP, "Table 6.6. Reconstruction fidelity: the residual between the landmark-tracked wrist and the wrist predicted from the object pose plus the constant grip vector, on carried frames where both pipelines measure."),

(IMG, FIG + "ch6_fig3_offset.png", 6.3),
(CAP, "Figure 6.3. The pinned offset analysis. Top panels: the object-to-wrist offset in the world frame, whose direction sweeps the full circle as the box is carried and turned. Lower panels: the same offset expressed in the object's own frame, collapsing to one flat constant vector per holding hand, and the residual after removing it."),

(P, "One further audit belongs to fidelity because it concerns what the viewer sees rather than what the data says. The avatar is a stock humanoid model authored 3.25 metres tall, and early renders showed the cube floating far from its hand; measurement located the cause before any parameter was touched. At the original size the rig's forward-kinematics hand landed a median of 30 to 46 centimetres from the real wrist point. The receiver now measures the rig's rest height at spawn and scales it uniformly by 0.523 to a 1.70 metre person, which is safe because a uniform scale commutes with every rotation, leaving the angle transfer untouched; after the fix the rig hand lands a median of 7 to 13 centimetres from the wrist landmark. The remainder is the rig's own non-uniform proportions: its forearm is 1.59 times the person's measured forearm even at the correct overall height, and its right-arm reach exceeds the person's by 4.8 centimetres. Only per-bone retargeting onto a measured-proportions skeleton could remove this, and it is deliberately out of scope: the system transfers joint angles, not body surfaces, and the data-side accuracy of Table 6.6 is unaffected by how long the display rig's forearm is."),

(H2, "6.6 Qualitative Analysis"),

(P, "Figure 6.4 places the sensor's color image at frame 100 of the running example beside the integrated Unity reconstruction. The comparison is deliberately unglamorous: the reconstruction is not a photorealistic double but a geometric one, and the things worth checking are positions, directions, and relationships. They hold. The avatar stands where the person stands, on the far side of the desk facing the sensor; the streamed facing direction deviates from the sensor axis by a mean of 4.5 degrees over the recording. The cube sits at the avatar's hand, at the correct height above the desk. The desk, the wall, and the sensor body occupy their calibrated places, and the inset in the corner of the reconstruction renders the same scene from the sensor's own calibrated pose and field of view, so the correspondence with the real camera image can be judged directly by eye."),

(IMG, FIG + "ch6_fig4_compare.png", 6.5),
(CAP, "Figure 6.4. The real sensor image at frame 100 (left) and the integrated Unity reconstruction (right), with the sensor's own viewpoint rendered as the inset. The comparison to make is geometric: person position and facing, object position at the hand, and desk and wall placement."),

(P, "Some properties of the rendered scene are exact by construction, and the qualitative view is the right place to say so plainly. The wall slab stands at exactly zero degrees from vertical and the desk top at exactly zero degrees from horizontal, because the scene is built inside a parent node that absorbs the measured 4.75 degree tilt of the desk stand; the levelling is real measurement, but it lives in one transform, so the rendered surfaces are perfectly plumb and level by design, not as an accuracy claim. The accuracy claims live one level down: the cube resting on that perfect desk surface to within 4.2 millimetres, and the parked height trace of Figure 6.1 holding flat, are measurements."),

(P, "The reconstruction is also honest about what it does not know, and Figure 6.5 shows the vocabulary. In the synthetic occlusion scenarios of Section 6.3, every joint that is holding rather than measuring carries a red marker sphere: one sphere on a blocked wrist, a chain of spheres up the arm as more of it becomes unobservable, and the full set during total pose loss, while the rest of the body visibly keeps tracking. The same convention colors the object: during the trailing marker gap of the evaluation recording the cube renders with a red tint, announcing that its pose is held memory rather than measurement. In the full evaluation video the overall impression is of coherent, ordinary motion: the avatar walks the cube along the desk, turns it, parks it, and picks it up again, with the arm asymmetry of Section 6.5 visible on close inspection as a slightly noisier left arm, and the two artifact classes that earlier drafts of the pipeline showed, a start-up arm snap and freeze-and-pop object dropouts, absent after the edge backfill and the object-track filter. What the numbers of this chapter cannot show and the video can is the plausibility of the whole: that the reconstruction reads as one person doing one thing, rather than as two data streams that happen to share a screen. The residual limitations that remain, the display rig's proportions, the left-wrist occlusion sensitivity, and the single-viewpoint sensor geometry behind both, are taken up in the discussion of Chapter 8."),

(IMG, FIG + "ch6_fig5_occlusion.png", 6.3),
(CAP, "Figure 6.5. The honesty vocabulary of the reconstruction, from the synthetic occlusion scenarios: red marker spheres appear on exactly the joints that are holding their last measured angle, while the rest of the body keeps tracking live. Clockwise from top left: a blocked right wrist, a blocked right elbow, total pose loss, and a blocked left hip."),

(H2, "References"),
(P, "Reference numbering continues from the previous chapters; entries cited in this chapter:"),
]

references = {
9: 'L. Keselman, J. Iselin Woodfill, A. Grunnet-Jepsen, and A. Bhowmik, "Intel RealSense stereoscopic depth cameras," in Proc. IEEE Conf. Computer Vision and Pattern Recognition Workshops (CVPRW), 2017.',
27: 'M. Kalaitzakis, B. Cain, S. Carroll, A. Ambrosi, C. Whitehead, and N. Vitzilaios, "Fiducial markers for pose estimation: Overview, applications and experimental comparison," Journal of Intelligent and Robotic Systems, vol. 101, art. 71, 2021.',
39: 'V. Bazarevsky, I. Grishchenko, K. Raveendran, T. Zhu, F. Zhang, and M. Grundmann, "BlazePose: On-device real-time body pose tracking," arXiv:2006.10204, 2020.',
40: 'G. Casiez, N. Roussel, and D. Vogel, "1 euro filter: A simple speed-based low-pass filter for noisy input in interactive systems," in Proc. SIGCHI Conf. Human Factors in Computing Systems (CHI), 2012, pp. 2527-2530.',
44: 'A. Savitzky and M. J. E. Golay, "Smoothing and differentiation of data by simplified least squares procedures," Analytical Chemistry, vol. 36, no. 8, pp. 1627-1639, 1964.',
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

out = ("/home/luo/Desktop/New_SandBox/writing/v2/"
       "Chapter_6_Experimental_Design_and_Evaluation.docx")
doc.save(out)
print("saved", out)

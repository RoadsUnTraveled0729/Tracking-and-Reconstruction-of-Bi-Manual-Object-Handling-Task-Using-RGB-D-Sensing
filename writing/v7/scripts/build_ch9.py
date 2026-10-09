#!/usr/bin/env python3
"""Build writing/v7/Chapter_9_Discussion_Conclusion.docx (V7 rewrite round).

Chapter 9 "Discussion, Future Work, and Conclusion" against the V7 TOC:
9.1 Limitations, 9.2 Future Directions, 9.3 Conclusion.

Chapter 9 is the only chapter besides 7 and 8 allowed to restate result
numbers. Every number below carries a source comment; the sources are
the frozen R5 reports and decision logs:

  eval/reports/r5_failure_mask.md          failure detectors, windows
  eval/reports/r5_waypoint_eval.md         trajectory vs designed path
  eval/reports/r5_recovery_synthetic.md    synthetic-mask grading
  eval/reports/r5_recovery_moving.md       moving-outage grading
  eval/reports/r5_object_conditioned_recovery.md   recovery limitations
  eval/DECISIONS.md                        E-009a, E-011b, E-013, E-014a,
                                           E-014b, E-017a, E-019, E-021
  v2/reports/r5_realtime_probe.md          real-time measurements
  eval/output/recording_20260825_222315_scaled_object_world.csv
                                           object marker detection count
  eval/output/recovery_r5/failure_mask.csv against the phases of
                                           eval/reports/recording_20260825_222315_inspection.json
                                           (all-clear frames inside the
                                           manipulation phase)
  eval/output/recording_20260825_222315_scaled_object_world_filtered.csv
  eval/output/recording_20260825_222315_scaled_object_world_filtered_clean.csv
                                           the held pose through the
                                           handover gap and the cleaning
                                           stage dropping no detected row
  writing/v7/figures/src/r5_ch9_landmarks.json
                                           visibility scores of the two
                                           figure frames

Per E-021 the recovery and waypoint reports were regenerated on
2026-08-28 against the committed code, and per E-022 the whole R5 chain
from the object-track filter onward was re-run the same day after the
filter fix; this chapter quotes the regenerated values only, at the
precision Chapter 7 prints them.

Rule 3 of skill_set/thesis-structure-rules.md: the limitations section
carries the two failure-mode screenshots, built by
writing/v7/scripts/make_ch9_failure_figs.py.

Chapters 7 and 8 are referred to by section title, never by figure
number, because they are drafted in the same round.
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches

H1, H2, P = "h1", "h2", "p"
CAP, TBL, LIN, IMG = "cap", "tbl", "lin", "img"

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v7" / "figures"

F_LANDMARK, F_MARKER = 1, 2

content = [
(H1, "Chapter 9: Discussion, Future Work, and Conclusion"),

(P, "The preceding chapters built the system and reported what it measures. This chapter states where the system stops, what should be built next, and what the thesis as a whole established. Section 9.1 collects the limitations together with their causes. Section 9.2 lists the work that follows from what is already built, and Section 9.3 closes the thesis against the objectives of Chapter 1."),

(H2, "9.1 Limitations"),

(P, "The limitations fall into three groups: the failures of the sensing, the limits of two recordings of one participant, and what the model does not represent. The first group is the most visible on screen, so it comes first, with a pair of frames from the loop recording, the occlusion scenario of Chapter 7, for each of the two ways the sensing fails, since the rail recording shows neither."),

# Failure mode (a): MediaPipe skeleton off the body.
# Limb lengths and window: eval/reports/r5_failure_mask.md,
# confident-but-wrong table, arm_R window 1775-1825.
(P, f"MediaPipe returns a landmark for every frame, and it returns one whether or not the body part is where the landmark is placed. Figure 9.{F_LANDMARK} shows the difference on two frames of the loop recording, four seconds apart, the second taken while the hand holds the cube in front of the chest. On the second frame the elbow landmark has slid down the arm onto the hand. The reported skeleton no longer follows the arm in the picture. Measured limb lengths give the size of the error over that window: the upper arm reads 47.2 centimetres against a clean median of 25.8, and the forearm reads 3.0 centimetres against 25.5. A limb cannot change length, so the geometry alone identifies the frames as wrong."),

(IMG, FIG / "ch9_fig_landmark_failure.png", 6.3),
# Visibility values from writing/v7/figures/src/r5_ch9_landmarks.json
# (frame 1818: L14 = 0.566, L16 = 0.902), gate 0.50 from Section 2.2.
(CAP, f"Figure 9.{F_LANDMARK}. Landmark tracking failure on the loop recording. Panel (a), frame 1698: the right arm is tracked, with the right elbow and right wrist marked in red on the elbow and the wrist. Panel (b), frame 1818: the elbow landmark has moved onto the hand and lies on top of the wrist landmark. The detector reports the right elbow at a visibility of 0.57 and the right wrist at 0.90 on the failed frame, both above the 0.50 gate of Section 2.2."),

(P, "Nothing in the detector's own output announces the failure. Both landmarks stay above the visibility gate through the whole window. The failure detectors of Chapter 5 therefore test geometry instead of confidence. The recovery restores a holding arm from the object pose. An arm that fails this way while it holds nothing keeps its last valid angles, so the free-arm case stays a limitation rather than a solved problem."),

# Failure mode (b): object marker blocked.
# 2058 of 2099 detected, 41 misses at frames 1013 and 1067-1109 (the
# handover run carries brief reappearances at 1076, 1084 and 1105):
# eval/output/recording_20260825_222315_scaled_object_world.csv;
# the handover window is also named in eval/reports/r5_waypoint_eval.md
# and in E-019 of eval/DECISIONS.md. After the E-022 filter fix the
# filtered track holds tx -0.0660 flat across the gap and the cleaning
# stage blanks no detected row (2058 detected in both the scaled and the
# filtered_clean CSV), so the cleaning rule never fires on R5.
(P, f"The object marker fails in the opposite way, by returning nothing at all. Figure 9.{F_MARKER} shows a detected frame and a lost frame from the desk handover, just under half a second apart. On the frames inspected across the handover the square is never fully covered, so a hand crossing the marker border is enough to lose the pose. The object marker is present on 2058 of the loop recording's 2099 frames, and all but one of the 41 missing frames fall inside this handover. On the rail recording, where no hand crosses the marker, it is present on 899 of 900 frames."),

(IMG, FIG / "ch9_fig_marker_blocked.png", 6.3),
(CAP, f"Figure 9.{F_MARKER}. Object marker loss on the loop recording, cropped to the object marker and the desk marker; the wall marker lies outside the crop. Panel (a), frame 1060: both markers are detected, with their four detected corners outlined. Panel (b), frame 1073, inside the desk handover: a finger crosses the top-right corner of the printed square and the detector returns no object pose, while the desk marker on the tabletop is still found."),

(P, "A blocked marker costs more than a missing object sample. The recovery of Chapter 5 anchors a lost wrist on the measured object pose, so a marker gap that falls inside a landmark failure window leaves nothing to anchor on and the solver falls back on holding the last angles. The two failures did not overlap on the loop recording, because both wrists stayed tracked through the handover, but nothing in the design prevents the overlap. The gap itself is covered rather than repaired. The filtering stage of Chapter 4 holds the object at the last pose it measured for as long as the detector returns nothing. The track therefore runs flat across the handover, and the detections that reappear briefly inside the gap are kept as measured. The cleaning stage that follows blanks a detected sample only when the distance from its predecessor is too large to be physical. On neither recording does the offline rule blank a detected sample, and the rule stands as a safety net that neither recording sets off. The marker branch answers this failure mode with a held pose and one cleaning rule."),

# One subject, one recording. Span from skill_set/r5-experiment-state.md
# and v2/reports/r5_realtime_probe.md; the 154 eligible frames on the
# left and 304 on the right, carving one masked window on the left and
# two on the right (three in total), from
# eval/reports/r5_recovery_synthetic.md (E-021 regeneration).
(P, "The results rest on one participant and two recordings. The rail recording, 900 frames, about 30 seconds, of a one-handed slide along a straight rail, carries the object accuracy against the rail line, the solver check, the synthetic masking of Section 7.3.1, and the real-time run of Chapter 8. The loop recording, 2099 frames, about 70 seconds, supplies the occlusion scenario: the natural failure windows, its own trajectory evaluation, and the synthetic masking of Section 7.3.2. A third, shorter recording set the failure thresholds in Chapter 5; it tests the margin of those thresholds and is not an evaluation dataset. It does not clear every detector: the left-arm segment-length detector fires on 96 of its frames, because that recording carries an elbow defect of its own. Widening the tolerance until the detector stops firing there would calibrate it to a defect, so the threshold stays at the value the right arm and the torso support. Two takes support no statement about how the system behaves across body sizes, grips, or working habits. The synthetic-masking evaluation rests on less than either recording, because its eligibility rule admits only frames where the hand held the object and no detector fired on the evaluated arm or the torso. On the rail recording that rule leaves 342 eligible frames on the right side and five slow windows; on the loop recording it leaves 154 eligible frames on the left and 304 on the right, one window on the left and two on the right, so a single window moves the pooled result."),

# Labelled natural windows: protocol in place, labels not yet made
# (skill_set/r5-experiment-state.md, "Recovery verification by manual
# labels", status 2026-08-28). No number is quoted here.
(P, "The scope of that evaluation is itself a limitation. Synthetic masking grades the recovery on stand-in frames, chosen because they are clean enough for the unmasked solve to serve as the reference, and the frames that matter are the natural failure windows, where no reference exists in the recording. Chapter 7 sets out the protocol that closes this: the wrist is labelled by hand on failure-window frames inside a grip episode, the aligned depth map supplies the third coordinate, and the recovered wrist is compared with the labelled point. The labels for the loop recording are not yet made, so the accuracy of the recovery on natural failure windows is not a measured quantity in this thesis. At present the natural windows carry only the qualitative reading of Chapter 7. The two recordings do not close the gap between them: the rail recording carries the ground-truth line but no occlusion, and the loop recording carries the occlusion but no reference on the frames where it happens, so tracking accuracy under natural occlusion is not separately evaluated."),

# Desk occlusion of the hips: eval/reports/r5_failure_mask.md
# (fail_torso 625 frames, 30.7 percent of span; manipulation phase
# 43.2 percent). Pinned figure frames: D17 in writing/v7/DECISIONS.md
# (frame 270, pre-task, every detector clear, the Chapter 3 worked
# example; frame 1236, mid-task, torso detector firing with both arm
# flags clear, the Chapter 2 scene figures). 511 frames inside the
# manipulation phase 656-1983 carry no failure window
# (eval/output/recovery_r5/failure_mask.csv against the phases of
# eval/reports/recording_20260825_222315_inspection.json).
(P, "The desk edge is the largest single cause of failure in both recordings. A participant standing at a desk keeps both hips behind it. The hip landmarks are therefore inferred rather than seen, and their depth samples land on the desk, on the rail, or on a hand crossing the trunk. On the loop recording the torso detector fires on 625 frames of the evaluated span, 30.7 percent of it, and on 43.2 percent of the manipulation phase, since the hands spend most of that phase in front of the body. On the rail recording it fires on 31.3 percent of its evaluated span, nearly all of it in one window from frame 632 to the end, where one hip pixel reads the rail's depth and the other the body's. The steadier case is worse for the detectors: for most of the rail recording both hip pixels read the rail's depth together, 0.99 metres against 1.31 to 1.36 metres at the shoulders, so the root frame of Chapter 3 decodes to a pitch of about 32 degrees on an upright participant, and no failure detector fires before frame 632, because nothing jumps. The worked-example frame of Chapter 3, frame 533, carries that offset, and Section 3.5 gives its size. The torso repair of Chapter 5 puts a gated hip back on its own camera ray at a remembered depth, or where no memory can be trusted at the depth of the shoulders, so the reconstruction stays usable through these windows. On the rail recording it holds the trunk within 10 degrees of the true vertical where the measurement puts it 24 degrees off at the median, as Section 7.4 reports."),

(P, "A repair is not a measurement, and it carries its own cost. The direction memory it leans on lags a fast trunk rotation for as long as the gate stays closed, and its depth memory was seeded on the first frames of the take, so it holds the pelvis near the depth the take began with, 1.21 metres against the 1.22 of its first frames. The shoulder-depth gate of Section 5.5, which compares a hip with the shoulders instead of with its own past, is the cover for a take that begins with the pelvis already behind the rail. It fires on two frames of the rail recording. Over a whole take it would place both hips at the shoulder depth, giving a vertical trunk in place of a leaning one, and that behaviour is untested."),

(P, "The cause sits one step earlier, in a choice made in Chapter 2. The pipeline discards MediaPipe's own depth estimate and samples the registered depth stream at the landmark pixel instead, and the metric positions rest on that substitution. The sample belongs to the pixel, not to the body part. Any object that passes in front of a landmark therefore hands that landmark a wrong distance while its image position stays correct, and no visibility score reflects it. The hip corruption above is this failure, so the repair puts the joint back on its ray rather than trusting the depth value."),

# Marker size assumption: E-009a in eval/DECISIONS.md (45 mm working
# value, implied 43.5/43.7 mm from the depth cross-check).
(P, "The metric scale of the marker branch rests on one number, the printed black square of the desk and object markers, 45 millimetres. Planar pose recovery scales its translation linearly with the side length it is given, so any error in that number multiplies every object position by a fixed factor. A depth cross-check on the loop recording reads the square about three percent smaller: the object marker at 43.5 millimetres against the depth stream and the desk marker at 43.8. Comparisons made inside the object track absorb the factor, and both trajectory evaluations of Chapter 7 are of that kind: the loop's waypoints are detected on the track itself, and the rail line is fitted to the tracked slide. Any distance quoted as a physical length in the room does not absorb it."),

# Grip offset through a regrasp: eval/reports/
# r5_object_conditioned_recovery.md section 7, E-014a, and the E-021
# regeneration in eval/reports/r5_recovery_synthetic.md (offset 12.86 cm
# or more from the fitted value in the two windows leading into the wire
# handover, wrist estimate 13.98 cm median on the left; 1.18 cm on the
# rigid-grasp window).
(P, "The recovered wrist is the measured object pose plus the hand-object offset of Chapter 5, and that offset can only be fitted while the hand is visible. A regrasp inside a failure window has no clean frame to update it, so the estimate stays where the last visible grasp put it and the error grows with the displacement of the regrasp. The two windows leading into the wire handover, the second handover of the loop task, measure this directly: the offset there sits 12.86 centimetres or more from the value fitted over its episode, and the wrist estimate follows it out to a median of 13.98 centimetres on the left side. The one window where the grasp stays rigid puts the same estimate 1.18 centimetres from the reference. The torso cannot be recovered from a single rigid grasp at all."),

# Grip tracker rest warm-up: v2/reports/r5_realtime_probe.md,
# sensor-switch checklist item 2.
(P, "The online offset estimate of the real-time path needs a reference for where the object rests. It takes the median of the object's first samples as that rest pose and calls the object carried once it has moved away from it, so it assumes the object starts at rest and in view for about a second. The design of the task satisfies this. A session that begins with the object already moving, or out of view, has no rest reference, and the grip episodes would not open where they should."),

# Live-sensor round still open: v2/reports/r5_realtime_probe.md and
# skill_set/v2-r5-probe-state.md.
(P, "The real-time results come from the rail recording replayed at its own pace rather than from the camera. The capture stage owns the device, and both pipelines read the same stream of captured frames. Everything downstream of the capture stage is therefore independent of whether frames arrive from a file or from a sensor, and the source is a single switch. That switch has not yet been run against the camera; Section 9.2 states the two preconditions such a session needs. Long sessions, changing light, and a camera that is knocked during a take are untested as well."),

# Seven-rotation description and the four solved angles: Section 3.3.1
# of the built Chapter 3 (Craig [42]).
(P, "The last group of limitations concerns what the model does not represent. The human arm is conventionally described by seven rotations, and this model solves four of them. The three wrist rotations are not observable from the eight body landmarks: forearm pronation turns the forearm about its own axis and moves the wrist point not at all, so no algebra over these landmarks can see it. The reconstruction therefore places the hand without orienting it. Fingers, contact points, and grip force lie outside the landmark set, so the system records the position of a hand and not its grasp. The torso is one rigid plate for the same reason, and the legs below the desk are not tracked. Table 9.1 collects the limitations of this section with their causes."),

(TBL, [["Limitation", "Cause", "Where it shows on the recordings"],
       ["Landmark failure at high confidence",
        "MediaPipe places a landmark whether or not the body part is there",
        "Right arm, frames 1775 to 1825: upper arm 47.2 cm against a clean 25.8 cm"],
       ["Object marker blocked",
        "A hand crosses the border of the printed square during a handover",
        "Object pose missing on 41 of the loop recording's 2099 frames, 40 of them in the desk handover"],
       ["Hips behind the desk",
        "Hip landmarks are inferred and their depth samples land on the desk, the rail, or a crossing hand",
        "Torso detector fires on 30.7 percent of the loop recording and 31.3 percent of the rail recording"],
       ["Steady hip depth offset",
        "Both hip pixels take the depth of the rail in front of the body, so nothing jumps and no failure detector fires before frame 632; the repair depends on a depth memory seeded on the body",
        "Measured root frame pitched about 32 degrees on the worked-example frame, and the trunk 24.3 degrees from vertical at the median; repaired trunk within 10 degrees of vertical"],
       ["Metric scale of the marker branch",
        "The depth stream reads the 45 mm printed square about 3 percent smaller",
        "Every object translation scales linearly with the marker size"],
       ["Hand-object offset through a regrasp",
        "The offset can only be fitted while the hand is visible",
        "Wrist estimate 13.98 cm before the loop recording's wire handover against 1.18 cm on a rigid grasp"],
       ["One participant, two recordings",
        "A rail take of about 30 seconds and a loop take of about 70 seconds",
        "Synthetic masking gives five slow windows on the rail recording and three still windows on the loop recording"],
       ["No wrist or hand pose",
        "Pronation moves no landmark in the set",
        "Four of the arm's seven rotations are solved"],
       ["No live-sensor session",
        "The source switch has not been run against the camera",
        "Real-time results come from the recording replayed at its own pace"]]),
(CAP, "Table 9.1. The principal limitations of the system, their causes, and where each one shows on the recordings."),

(H2, "9.2 Future Directions"),

(P, "Each direction below follows from something this work already built or already measured. None of them asks for a different system."),

(P, "The live-sensor session is the first and the closest, since the sensor path is the same code with the capture source switched. The session needs the scene calibration run from the live stream with the true marker sizes. It also needs the object left at rest in view while the offset estimate warms up. Running it would close the one gap between the real-time results reported here and a working camera, and it would produce the first evidence on the untested questions Section 9.1 lists, the ones a replay cannot answer."),

# The two-minute on-site check is the R5 re-recording protocol of E-013
# in eval/DECISIONS.md ("a compliant take shows all-PASS in about two
# minutes; re-record until it does").
(P, "More participants and more sessions are the natural extension of the evaluation. The recording precondition of Chapter 7 runs on site in about two minutes, so a take can be confirmed compliant before the participant leaves the room, and a multi-participant round becomes a scheduling problem rather than a research one. Several participants would also supply arm proportions across body sizes and put the failure thresholds in front of more than the present pair of recordings."),

(P, "A hand model attached at the tracked wrist is the extension the arm model was left open for. The wrist is carried as a tracked point so that a hand-specific chain can begin there without changing the arm solver, and the laboratory's own hierarchical hand model [17], [41] solves finger joints from dedicated hand landmarks in that form. Adding it would supply the hand orientation, fingers, and contact points that Section 9.1 lists as unobservable. It would also give the hand-object offset a measured origin instead of a fitted one."),

(P, "Chain-level recovery by Bayesian estimation is the direction Chapter 1 named. The present solver holds a joint that loses its landmark, or restores it from the object when the hand is holding one, and both are point estimates without a stated spread. The Gaussian network formulation of [18] recovers anatomically consistent joint configurations for a hand chain by correcting each joint from the estimates of its neighbours, and the upper-body chain of Chapter 3 has the same structure. The pieces such an extension needs are already in place: the failure detectors mark which joints are unsupported, the solver already labels a recovered group as constrained rather than measured, and the synthetic-masking harness of Chapter 7 grades any replacement against the same reference, on the same windows, without modification. The labelled natural windows become the second benchmark for it as soon as the labels exist."),

(P, "Recovery that survives a regrasp and a marker gap is the last direction, and it addresses the largest errors measured in Section 9.1. Both failures point at one missing ingredient, a second observation of the hand that does not come from the body landmarks and does not come from the object marker. A hand model is one route to it and the Bayesian chain is another, so the three directions share one goal."),

(H2, "9.3 Conclusion"),

(P, "This thesis set out to track and graphically reconstruct an object-handling task from a single consumer-grade RGB-D sensor, and to keep the reconstruction physically consistent when the measurements are occluded or wrong. Chapter 1 stated five objectives for that goal. Each objective is delivered, one of them within a narrower scope than its wording suggests, and the outcome of each is stated below with the bound it carries."),

(LIN, "1. The calibrated sensing pipeline is built in Chapters 2 and 4. Depth and colour are registered on the device, the intrinsics come from the camera, and the desk marker fixes one world frame that the landmark branch, the marker branch, and the Unity scene all share, so the reconstruction does not depend on where the camera stands."),

(LIN, "2. The upper-body pose estimation module is built in Chapters 2 and 3. Eight landmarks per frame are back-projected through the registered depth into metric positions, the appearance-derived depth of the detector is discarded, and the kinematic model turns the positions into a torso pose and four joint angles per arm. This objective is delivered within a narrower scope than its wording: it names the hands, and the hand is delivered as a tracked wrist point rather than an oriented hand, for the reason Section 9.1 gives."),

# Object marker present on 2058 of 2099 frames:
# eval/output/recording_20260825_222315_scaled_object_world.csv.
# One cleaning filter: E-019 in eval/DECISIONS.md; after the E-022
# filter fix it blanks no detected row on this recording.
(LIN, "3. Concurrent object tracking is built in Chapter 4, within the bound the objective itself states. The marker is detected on 899 of the 900 frames of the rail recording, and on the loop recording on all but the 41 frames Section 9.1 counts, nearly all of them in the desk handover; the filter holds the last measured pose across the longer gaps and bridges the short ones, and the object's orientation is carried through filtering, streaming, and evaluation without a second measurement chain to check it."),

# Moving-outage numbers: eval/reports/r5_recovery_moving.md
# (recovered wrist 1.67 and 1.65 cm median over the two outages;
# hold-last 15.39 and 21.39 cm max) and E-014a. Quasi-static outcome:
# eval/reports/r5_recovery_synthetic.md.
(LIN, "4. Pose recovery of a holding hand is built in Chapter 5 and graded in Chapter 7 under synthetic masking, where the truth is known by construction. The grading splits by what the arm is doing. On a moving outage the recovered wrist of the loop recording stays a median of 1.67 and 1.65 centimetres from the reference over its two moving outages. Holding the last angles runs away with the motion instead, out to 15.39 and 21.39 centimetres, because the object anchor is a live measurement and a memory is not. On the still holding windows of the loop recording and the slow windows of the rail recording, both memory baselines beat the recovery by a few degrees of arm angle, since a hand resting on a box has a last measured pose that is nearly correct and the recovery inherits the drift of its hand-object offset instead. Both figures come from stand-in frames; accuracy on the natural failure windows waits on the manual wrist labels of Section 9.1."),

# Trajectory result: eval/reports/r5_waypoint_eval.md and E-017a
# (point-to-path median 0.79 cm, p95 9.32 cm over 1032 loop frames,
# regenerated under E-022).
# The two large per-segment errors, re-derived with
# path_metrics.point_to_path against eval/gt/labeled_path_r5.json over
# the loop span 858-1930 (1032 measured frames after the E-022 re-run):
# W8_wire_left -> W1_start, the closing descent, median 5.95 cm over 83
# frames; W1_start -> W2_back_end, median 0.66 cm over 136 frames, and
# those 136 frames are 45 of outward travel (858-902, median 0.68 cm,
# max 4.72 cm), 49 of back-end station dwell (903-954, median 0.05 cm,
# near zero because the cube is standing at the waypoint) and 42 of
# closing return (1889-1930, median 10.47 cm, max 13.11 cm), so every
# large value on the segment comes from the return and none of it makes
# the outward travel exceptional.
# The carried loop never reaches the parked start position: frame 858
# lies 26.7 cm from W1_start and frame 1930 lies 26.4 cm from it, with a
# closest approach of 24.8 cm, so the two segments meeting at W1_start
# are unmatched at that end. The un-paused corners are described in the
# limitations section of eval/reports/r5_waypoint_eval.md by approximate
# frame; no corner frame is measured here.
(LIN, "5. Integration and evaluation are built in Chapters 6 and 7. The person and object records are paired by frame index and streamed into the Unity reconstruction, and the tracked object trajectory sits a median of 0.97 centimetres from the rail line with a 95th percentile of 2.36 centimetres, and on the loop recording a median of 0.79 centimetres from its reference path with a 95th percentile of 9.32 centimetres. The two largest per-segment errors of the loop both sit at the end of the designed path. One is the closing descent from the wire, where the participant did not pause and the designed path has no waypoint to bend around. The other is the segment drawn from the parked start to the back-end station, whose measured frames fall at that station and on the closing return, and every large value it carries comes from the return. The carried cube never reaches the parked start position, passing about 26 centimetres from it at either end, so the two segments that meet there are unmatched at that end."),

# Real-time measurements: v2/reports/r5_realtime_probe.md.
(P, "Chapter 8 puts the same feature set on a real-time footing. The stack consumes every frame of the rail recording at 29.0 frames per second with none skipped, and the slower branch, the marker branch, spends 16.7 milliseconds at its 99th percentile against a 33.3 millisecond budget. The whole recovery layer adds about 0.23 milliseconds per frame, and the output carries a declared delay of two frames. The reconstruction the viewer sees is therefore the same reconstruction the offline chapters evaluate, produced at the pace the sensor delivers frames."),

# Torso repair result: E-011b in eval/DECISIONS.md.
(P, "The repairs matter most where the loop recording is hardest. On the window where both hips fail together the torso repair brings the root yaw spread down from 57.4 to 15.3 degrees, and it narrows the range of camera depth the hip midpoint wanders through from 21.9 to 0.5 centimetres. Without the repair the torso swings whenever a hand crosses it, and with the repair it stays put."),

(P, "Chapter 1 also opened with a working assumption about where capability comes from. With transistor scaling near its physical limits, further capability is expected to come from algorithms and system organization rather than from faster parts [16], and industry has said the same [49]. The parts of this system are ordinary: a depth camera sold as a consumer product [10], three markers printed on paper, an open-source landmark detector [28], an open-source computer vision library, and a game engine. None of them was built for manipulation capture. The instrumented route would have added hardware until the problem became easy, with inertial sensors on every segment [50] or a laboratory installation of synchronized cameras [8]. This work took the other route, and its contribution sits in the arrangement rather than in any part: two measurement chains that share only the recorded frames and one world frame, a kinematic model that fixes what the landmarks can and cannot reveal, and a recovery stage that uses one chain to stand in for the other when it fails."),

(P, "The measurements reported here belong to this sensor, this room, and these two recordings. Two things in the work are more portable. The first is the arrangement, because its two chains fail for different physical reasons, and any rigid marked object can play the second chain's role for the hand that holds it. The second is the labelling: every quantity the system reports is marked as measured, repaired, or held, and the label travels with it to the screen, so a reader of the reconstruction can tell which parts of the pose the sensor saw. Section 9.2 lists what follows, and the closest of those directions moves the system off the replayed recording and onto the camera itself."),

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
    elif kind == P:
        doc.add_paragraph(item[1])
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
                cell.text = c
                for par in cell.paragraphs:
                    for run in par.runs:
                        run.font.size = Pt(10)
                        if i == 0:
                            run.font.bold = True

out = REPO / "writing" / "v7" / "Chapter_9_Discussion_Conclusion.docx"
doc.save(out)
print("saved", out, "| items:", len(content))

#!/usr/bin/env python3
"""Build writing/v7/Chapter_7_Evaluation.docx (V7 rewrite round).

Chapter 7 "Evaluation" against the V7 TOC: 7.1 Evaluation Protocol and
the Recording, 7.2 Object Trajectory Against the Designed Path, 7.3
Recovery Accuracy Under Synthetic Masking, 7.4 Torso Stability, 7.5
Qualitative Results. Two subsections were added under 7.1 so that the
solver validation parked out of Chapter 3 (writing/v7/CH6_PARKED.md)
and the failure statistics that set up 7.3 to 7.5 have a home without
renumbering the fixed sections.

Every number in the prose carries a comment naming the frozen artifact
it comes from. Values re-verified for this build by rerunning
writing/v7/scripts/ch3_numbers.py (solver sweep on the primary
recording), writing/v7/scripts/make_ch7_figs.py (waypoint distances,
torso window spreads, moving-outage wrist errors) and
v1/kinematics/validate_occlusion_ext.py (41 checks, no failures).

Scenario-separation round (2026-08-31, E-023): Section 7.2 closes with
the no-occlusion rail evaluation (numbers from
eval/reports/r6b_rail_eval.json; figure make_ch7_rail_fig.py).

Style: build_ch2.py / build_ch3.py conventions (P/H/CAP/TBL/IMG items,
Times New Roman 12 pt, self-renumbering figure and table constants).
Figures: writing/v7/scripts/make_ch7_figs.py -> writing/v7/figures/.
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches

H1, H2, H3, P = "h1", "h2", "h3", "p"
CAP, TBL, LIN, IMG = "cap", "tbl", "lin", "img"

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v7" / "figures"

# 7.1.1 (rail-only round, 2026-09-01): the reference paths of both recordings
# open the chapter; rail trajectory (make_ch7_rail_traj_fig.py), rail tape
# photographs (moved from Chapter 2), loop path (make_ch2_path_fig.py output)
F_RTRAJ, F_RDIMS, F_LOOP = 1, 2, 3
F_FAILR, F_FAIL, F_RAIL, F_WAY, F_RECOV, F_TORSO, F_OVER = 4, 5, 6, 7, 8, 9, 10
T_SYNTH, T_DET, T_SEG, T_RMASK, T_MASK, T_MOVE = 1, 2, 3, 4, 5, 6
T_LABEL, T_TORSO = 7, 8

content = [
(H1, "Chapter 7: Evaluation"),

(P, "This chapter reports the accuracy of each stage of the system. The evaluation has four parts: the solver against synthetic ground truth, the object trajectory against the reference paths of Section 7.1.1, the pose recovery of Chapter 5 under synthetic masking and on labelled natural failures, and the torso repair over the windows where the hip depths are corrupted. Section 7.1.3 first records where the tracker fails on each recording, since that decides which frames can be scored. The rail recording of Chapter 2 carries every part, and the loop recording enters where occlusion is the subject."),

(H2, "7.1 Evaluation Protocol and the Recordings"),

# recording: 2099 frames / 69.98 s / 30 fps, eval/reports/r5_object_conditioned_recovery.md
(P, "The measured results come from two recordings. The first is the recording of Chapter 2, called the rail recording in this chapter: one participant, 900 frames, about 30 seconds at 30 frames per second, sliding the cube along the desk, onto the rail, and along the rail with one hand. Nothing covers the object marker or the working arm during that task, so it is the scenario without occlusion. The second, the loop recording, carries the scenario with occlusion: the same participant, desk, camera, and markers, 2099 frames, about 70 seconds, on the two-handed task that Section 7.1.1 describes together with both reference paths. These two takes are the only recordings used for accuracy numbers in this chapter. The reference recording that set the failure thresholds of Chapter 5 appears once, in Section 7.4, with synthetic corruption injected into it, and where a result comes from a synthetic dataset instead, the text says so."),

(P, "One rule governs every accuracy number. Accuracy is quoted only where the correct answer is known independently of the method being graded. Two situations satisfy that. In a synthetic dataset the angles are injected before the landmarks are generated, so the truth is exact. On a real frame that the failure detectors of Chapter 5 accept, the unmasked solve is a measurement, and landmarks can be removed afterwards, as Section 7.3 does. The frames where the tracker fails on its own satisfy neither situation: nothing there measures the arm apart from the recovery itself, so comparing the two would compare two guesses. The rule alone leaves the frames the recovery exists for unscored. A person looking at the colour image can see where the wrist is even when the tracker cannot, so the rule is complemented by a second reference: manual wrist labels placed on the natural failure windows of the loop recording, described in Section 7.3.3, whose labels are not yet made. Frames that carry neither an automatic nor a manual reference are reported qualitatively in Section 7.5 and are excluded from every accuracy table."),

# marker size 45 mm: USER ASSUMPTION E-009a, eval/DECISIONS.md; eval/reports/r5_marker_scale.json
(P, "The object scale follows from the printed marker. The black square of the object marker is 45 millimetres, the detector was configured with 50, and every recovered translation is scaled by 45 divided by 50 before use, as Table 2.1 states. Every distance derived from the marker carries that printed size: the object positions of Section 7.2, the path lengths compared against the designed moves, and the object-derived wrist estimate of Section 7.3. Distances measured on the person, such as the landmark positions and the joint angles, do not depend on it."),

(H3, "7.1.1 The Recordings and Their Reference Paths"),

# src: eval/reports/r6b_waypoints.json (make_ch7_rail_traj_fig.py, E-024):
#      start = parked mean, frames 0-91; W1/W2/W3 from the fitted rail line
#      (depth, height, far end); legs 25.48 / 3.61 / 37.44 cm; the track
#      begins the lift at frame 501 and reaches rail height at frame 529
(P, f"The task of the rail recording has three legs, and Figure 7.{F_RTRAJ} draws the tracked cube trajectory in the gravity-levelled world frame of Chapter 4 together with the reference path. The reference path is the path the participant was asked to follow, and it has one direction per leg. From the parked start on the desk the cube moves straight back, away from the camera, to W1, the foot of the lift. A straight lift takes it to W2, the start of the rail. It then moves straight along the rail to W3, the far end. The corners come from the physical geometry, not from the corners of the track. The start is the mean tracked position of the parked cube over frames 0 to 91, W1 lies straight behind it at the depth of the rail, W2 straight above W1 at the height of the rail, and W3 at the far end of the rail. The depth, the height, and the far end are read from the line fitted to the rail slide in Section 7.2. The three legs measure 25.48, 3.61, and 37.44 centimetres, the third being the distance along the line from the x position of the start to the far end of the fitted line."),

(P, f"Only the third leg has a physical ground truth. The rail is a straight wooden bar, 38.7 centimetres long and 3.8 centimetres tall, lying flat on the desk and set level with a spirit level. Figure 7.{F_RDIMS} shows the tape measurements. The cube can only slide along the top face of the rail, so the straight line of that face is the reference for the slide, and Section 7.2 compares the tracked slide against the line fitted to it. The first two legs are free-space legs, and the tracked trajectory departs from their straight lines where the hand does: the lift begins at frame 501, and the cube reaches rail height at frame 529."),

(IMG, FIG / "ch7_fig_rail_traj.png", 6.2),
(CAP, f"Figure 7.{F_RTRAJ}. The rail recording in the gravity-levelled world frame: the tracked cube centre, the reference path from the parked start straight back to W1, straight up to W2, and along the rail to W3, and the line fitted to the rail slide. The height axis is stretched two times relative to the horizontal axes."),

(IMG, FIG / "ch2_fig_rail_dims.png", 6.3),
(CAP, f"Figure 7.{F_RDIMS}. The rail measured with a tape: (a) along its length, 38.7 centimetres; (b) the tape upright beside the rail lying flat, with the top face 3.8 centimetres above the desk."),

# src: loop path spec eval/gt/labeled_path_r5.json (E-017a); figure
#      writing/v7/figures/ch2_fig_path.png from make_ch2_path_fig.py
(P, f"The loop recording keeps the same desk, camera, and markers and changes only the task. The participant moves the cube around a closed loop of eight stations with both hands, passing it from one hand to the other. The path is marked physically: stations on the desk surface and a wire stretched between two stands above it. From its start position on the desk the cube moves away from the camera about 30 centimetres, then to the participant's left about 45 centimetres, then toward the camera about 15 centimetres, with a two-hand handover at a marked stop on the leftward move. It is then lifted about 30 centimetres up to the wire, carried along the wire with a second handover, and returned to the start position. Figure 7.{F_LOOP} plots the designed loop. The eight stations are the start point, the endpoints of the three desk moves, the desk handover stop, and three elevated stations at the wire, the middle one being the wire handover stop. At every station the cube is held still for a moment, and the straight segments between stations form the ideal polyline of the loop recording. During a handover both hands close around the cube, the hands occlude each other and the marker, and the landmark detector loses the wrist landmarks. That makes the loop recording the scenario with occlusion."),

(IMG, FIG / "ch2_fig_path.png", 6.3),
(CAP, f"Figure 7.{F_LOOP}. The designed loop in the gravity-levelled world frame: the eight stations, the straight segments between them, the desk plane, and the wire level. The station positions are read from the frames where the cube is held still."),

(H3, "7.1.2 Solver Validation Against Synthetic Ground Truth"),

(P, "The kinematic solver of Chapter 3 was checked before any recording was processed with it. Six synthetic datasets carry known injected angle trajectories: a rigid body swept through yaw, pitch, and roll; shoulder swings and twists with the torso held still; the same shoulder motion with the torso rotating at the same time; elbow flexion with the flexion plane rotating under the shoulder twist; the whole right arm with root, shoulder, and elbow all moving; and both arms together with twelve angles nonzero at once. Each dataset synthesizes landmark positions in sensor space, in the same data format the sensing stage produces, and pushes them through the complete pipeline. The decoded angles are then compared with the injected ones."),

# per-dataset worst decode errors: v1/KINEMATIC_MODEL.md lines 225, 357, 358,
# 432, 433, 543 and v1/kinematics/dataset/README.md
(TBL, [["Synthetic dataset", "What moves", "Worst decoding error (deg)"],
       ["Root sweeps", "torso yaw, pitch, roll, then combined", "1.1e-13"],
       ["Shoulder only", "shoulder swing and twist, torso still", "8.5e-14"],
       ["Shoulder with torso", "the same shoulder motion, torso moving", "2.0e-13"],
       ["Elbow only", "flexion, then a rotating flexion plane, then both", "8.5e-14"],
       ["Full arm", "root, shoulder, and elbow together", "2.8e-13"],
       ["Both arms", "torso and both arms, twelve angles nonzero", "2.6e-13"]]),
(CAP, f"Table 7.{T_SYNTH}. Worst decoding error of the solver on the six synthetic datasets, taken over every frame and every angle of each dataset."),

# worst across all six 2.80e-13 deg: v1/KINEMATIC_MODEL.md, writing/v7/CH6_PARKED.md
(P, f"Table 7.{T_SYNTH} lists the worst error of each dataset. The largest value anywhere in the set is 2.8 times 10 to the power of minus 13 degrees, which is the size of floating-point rounding at these magnitudes. The solver therefore inverts the geometric construction exactly, and the gimbal-lock case behaves as derived: a pose placed at the singularity itself decodes without error, and a swing pair of 30 and 90 degrees decodes as 0, 90, and 30 degrees, a different set of numbers describing the identical physical pose. The consequence for the rest of the chapter is that any deviation measured later belongs to the landmark measurements or to the recovery, never to the algebra between them."),

# 1720 of 2099 frames, worst reconstruction 1.48e-06 deg, elbow ranges:
# writing/v7/scripts/ch3_numbers.py rerun 2026-08-28 (right arm) plus the
# same sweep extended to the left arm
# rail sweep: writing/v7/scripts/ch3_numbers.py on recording_20260831_065553
# (77 of 900 frames with all eight landmarks; worst reconstruction 1.21e-06
# deg both arms; elbow ranges right -30.83 to -14.75, left -40.40 to -15.54)
(P, "The rail recording closes the loop on real data, where no injected truth exists. Two properties can still be checked on every frame. The solver ran on the 77 frames of the 900 in which all eight landmarks are measured, all of them inside the slide, since the idle left arm is out of the detector's view for most of the take. On the worst of those frames, the angles it returns reconstruct the measured upper-arm direction to within 1.21 millionths of a degree on either arm, so the solve remains an exact inverse when the input is a measurement rather than a construction. Elbow flexion stays inside its anatomical range throughout, between -30.83 and -14.75 degrees on the right arm and between -40.40 and -15.54 degrees on the left. Neither check says anything about the landmark positions. They confirm that the model consumes the measured positions without adding error of its own."),

(H3, "7.1.3 Tracking Failures in the Recordings"),

# rail failure study: eval/reports/r6b_failure_mask.md (E-024 re-run):
# span 5-899 (895 frames); arm_L 93.6 %, arm_R 13.3 %, torso 31.3 %;
# d1_R 111 frames; torso window 632-899 (8.94 s), hip depth split 19.4 cm
# against 0.8 clean; right-wrist natural gap 550-639 (3.0 s)
(P, f"The failure detectors of Chapter 5 run over each recording and mark, per frame, whether each arm and the torso can be trusted. Figure 7.{F_FAILR} shows the rail recording as a timeline, over the 895 evaluated frames after a five-frame warm-up. The working right arm is rejected on 13.3 percent of the span, three quarters of it one gap of 3.0 seconds in the middle of the slide, frames 550 to 639, where the detector stops reporting the wrist while the hand pushes the cube along the rail. The idle left arm hangs at the participant's side, partly out of the frame, and the detector declines its wrist on 93.6 percent of the span; nothing in the task uses that arm. The torso is rejected on 31.3 percent of the span, nearly all of it one window from frame 632 to the end of the take. There the two hips read depths 19.40 centimetres apart, against 0.80 centimetres on clean frames, because one hip pixel takes its depth from the rail in front of the body while the other takes it from the body. The geometry detectors catch the split while the tracker reports both hips at full visibility."),

(IMG, FIG / "ch7_fig_failures_rail.png", 6.3),
(CAP, f"Figure 7.{F_FAILR}. Frames rejected by the failure detectors over the rail recording, one band per entity. The percentage at the right of each band is the share of the evaluated span the entity spends in a rejected state."),

(P, f"The loop recording, the scenario with occlusion, fails in a different pattern, and Figure 7.{F_FAIL} shows it over the same kind of timeline. The detectors examine the person-present span from frame 62 onward, after a five-frame warm-up."),

(IMG, FIG / "ch7_fig_failures.png", 6.3),
# fire percentages 30.7 / 17.2 / 9.0 and the annotated windows:
# eval/reports/r5_failure_mask.md, r5_failure_events.csv
(CAP, f"Figure 7.{F_FAIL}. Frames rejected by the failure detectors over the loop recording, one band per entity. The percentage at the right of each band is the share of the evaluated span the entity spends in a rejected state. The three longest windows are labelled with what happens in the scene at that moment."),

(P, "The torso is rejected on 30.7 percent of the span, the left arm on 17.2 percent, and the right arm on 9.0 percent, after the closing step that bridges gaps of up to five frames between fires. The bands are not spread evenly. The failures cluster in the manipulation phase, where the torso spends 43.2 percent of its frames rejected against 8.6 percent during the approach, and both arms carry their longest windows there as well. "),

# detector fire counts: eval/reports/r5_failure_mask.md, R5 detector fire table
(TBL, [["Detector", "What it rejects", "Frames", "Percent of span"],
       ["Acquisition, left arm", "the detector declines the sample", "218", "10.7"],
       ["Acquisition, right arm", "the detector declines the sample", "108", "5.3"],
       ["Acquisition, torso", "the detector declines the sample", "9", "0.4"],
       ["Segment length, left arm", "an arm segment changes length", "50", "2.5"],
       ["Segment length, right arm", "an arm segment changes length", "50", "2.5"],
       ["Torso line angle", "hip line and shoulder line disagree", "537", "26.4"],
       ["Torso width ratio", "shoulder width over hip width leaves its band", "439", "21.6"],
       ["Landmark step, left arm", "a landmark jumps between frames", "62", "3.0"],
       ["Landmark step, right arm", "a landmark jumps between frames", "22", "1.1"],
       ["Landmark step, torso", "a landmark jumps between frames", "46", "2.3"]]),
(CAP, f"Table 7.{T_DET}. How often each detector fires on the loop recording, over the 2037 evaluated frames. A frame can trip several detectors at once, so the counts overlap, and the closing step adds frames the entity masks carry that no detector fired on. The grip-plausibility detector of Chapter 5 acts inside the recovery and is not part of the mask."),

# two failure classes and their windows: eval/reports/r5_failure_mask.md
# (interpretation section) and r5_object_conditioned_recovery.md section 1
(P, f"Two kinds of failure sit behind the counts of Table 7.{T_DET}, and the distinction matters for what a recovery stage can do about them. The acquisition detector passes on the tracker's own flag that it cannot see a landmark, which happens when a hand wraps behind the carried cube. The geometry detectors catch something else: frames where the tracker reports full visibility while the depth sample lands on the wrong surface. The torso line-angle and width-ratio detectors carry most of the fires, 537 and 439 frames, and almost none of those frames are ones the tracker flagged itself. On the longest torso window, running from frame 1182 to frame 1544 over 12.1 seconds, one hip sits 31.30 centimetres deeper than the other while the clean split between them is 1.30 centimetres. Both arm blackouts are preceded by the same pattern. Before the left arm is lost at frame 1458, its apparent forearm measures 34.70 centimetres against a clean median of 24.70; before the right elbow is lost at frame 1826, the apparent upper arm reaches 47.20 centimetres against a clean median of 25.80. The geometry detectors therefore fire before the tracker declines the sample."),

# A6 precondition on R5: eval/reports/r5_tracking_precondition.json, E-013
(P, "Read against the accuracy rule of Section 7.1, the failure pattern of the loop recording decides which of its windows can be scored. The left elbow is covered on 89 percent of the span and the left wrist on 90 percent, each with a longest landmark gap of 7.0 seconds, and the right elbow on 96 percent with a longest gap of 2.3 seconds. Neither hand meets the coverage and gap conditions an accuracy window requires. The arm-level rejection window around the left gap runs longer, 8.1 seconds, since it also counts the frames the geometry detectors reject. The torso landmarks meet them. The recovery evaluation of Section 7.3 therefore builds its windows synthetically on both recordings, out of frames the detectors accept, and the natural blackouts of the loop recording appear in Sections 7.3.3 and 7.5 instead."),

(H2, "7.2 Object Trajectory Against the Reference Paths"),

(P, f"Section 7.1.1 gives the rail leg the one physical reference, and the rail recording is compared against it first. The reference is the straight line through the slide samples that makes their summed squared perpendicular distances smallest. The slide samples are found geometrically in the gravity-levelled frame. The heights of the tracked positions gather at two levels, the desk and the rail, and the rail level is the upper of the two; every sample within half a cube size of that level belongs to the slide, counted from where the cube first reaches the level and stays there. Figure 7.{F_RAIL} shows the track, the fitted line, and the deviation along the slide."),

(IMG, FIG / "ch7_fig_rail.png", 6.4),
(CAP, f"Figure 7.{F_RAIL}. The rail recording against the rail line. Left: the tracked cube trajectory in the gravity-levelled world frame, with the line fitted to the slide samples. Right: the vertical and depth components of the deviation from that line, over the position along the rail."),

# rail stats: eval/reports/r6b_rail_eval.md / .json (E-024, levelled
# frame): 407 slide frames over t 16.41-29.99 s, travel 40.9 cm, perp
# median 0.97 / p95 2.36 / max 3.08 cm, vertical median 0.32,
# horizontal 0.81, line tilt 0.05 deg; desk level 3.5 cm, rail level
# 7.4 cm; marker detections 899/900
# (eval/reports/recording_20260831_065553_inspection.md)
(P, "The marker is detected on 899 of the 900 frames of the recording. The slide samples extend 40.90 centimetres along the fitted line over 407 frames, 2.20 centimetres more than the tape length of the rail, since the cube reaches past both ends of the bar. The tracked centre sits a median of 0.97 centimetres from the fitted line, with a 95th percentile of 2.36 centimetres and a largest deviation of 3.08 centimetres. The vertical component of the deviation carries a median of 0.32 centimetres and the depth component 0.81. The fitted line lies 0.05 degrees from horizontal. The rail level sits 3.90 centimetres above the desk level of the parked cube, against the 3.8 centimetre tape measurement of Section 7.1.1. The deviation mixes the tracking error with how the cube rides against the rail, so it bounds the tracking error of the slide from above."),

(P, "The loop recording is compared against the designed loop of Section 7.1.1. Its eight waypoints are the start position and the seven stations where the cube is held still, and the straight lines between consecutive waypoints form the ideal path the participant was asked to follow. Seven of the eight waypoints are recovered from the object track itself by finding the stretches where the cube stops; the start point is taken from the parked rest position before the task begins, which the stopping criterion cannot see because it examines carried frames only."),

# loop traversal 858-1930, 28.62-64.38 s; 1032 measured frames:
# eval/reports/r5_waypoint_eval.md, regenerated under E-022 (the
# object-track filter fix of 2026-08-28; the loop gained one frame,
# 1031 -> 1032, because the cleaning rule no longer blanks frame 1066)
(P, f"The comparison runs over the single loop traversal, frames 858 to 1930, of which 1032 carry a measured marker. Each measured position is assigned the closest of the eight straight segments and the distance to that segment is recorded. Figure 7.{F_WAY} shows the trajectory, the waypoints, and the distance over time in one view."),

(IMG, FIG / "ch7_fig_waypoints.png", 6.4),
(CAP, f"Figure 7.{F_WAY}. The measured cube trajectory against the designed path. Left: the loop in the gravity-levelled world frame, with the eight waypoints and the straight lines between them. Right: the distance from each measured position to the nearest segment, over the traversal."),

# median 0.79 / p95 9.32 / max 13.11 / mean 1.66 cm over 1032 frames:
# eval/reports/r5_waypoint_eval.md (E-022 re-run; the median moved
# 0.80 -> 0.79, the other three are unchanged), E-017a in
# eval/DECISIONS.md; reproduced by make_ch7_figs.py
(P, "Over the traversal the trajectory sits a median of 0.79 centimetres from the designed path, with a 95th percentile of 9.32 centimetres, a mean of 1.66 centimetres, and a largest deviation of 13.11 centimetres. The median and the mean differ by a factor of two, which says the distribution is not symmetric: most of the traversal lies close to the line and a small part of it lies far away."),

# per-segment table: eval/reports/r5_waypoint_eval.md (E-022 re-run),
# reproduced cell for cell by make_ch7_figs.py. Three rows moved with
# the re-run: back to desk handover 8.8/80/0.76/1.92/2.26, desk
# handover to left 24.4/141/0.47/1.95/2.59 and left to forward
# 8.4/97/0.22/0.39/1.13 became the values below
(TBL, [["Segment", "Length (cm)", "Frames", "Median (cm)", "p95 (cm)", "Max (cm)"],
       ["Start to back", "28.7", "136", "0.66", "11.74", "13.11"],
       ["Back to desk handover", "8.9", "76", "0.75", "1.93", "2.27"],
       ["Desk handover to left", "24.4", "147", "0.45", "1.92", "2.59"],
       ["Left to forward", "8.4", "96", "0.22", "0.38", "1.13"],
       ["Forward to lift top", "31.2", "264", "1.22", "2.12", "2.41"],
       ["Lift top to wire handover", "20.0", "158", "1.09", "2.22", "2.35"],
       ["Wire handover to wire left", "11.1", "72", "0.36", "0.60", "0.70"],
       ["Wire left back to start", "38.4", "83", "5.95", "12.33", "13.07"]]),
(CAP, f"Table 7.{T_SEG}. Distance from the measured trajectory to each designed segment, over the frames assigned to that segment."),

# The two outliers re-derived with path_metrics.point_to_path against
# eval/gt/labeled_path_r5.json over the loop span 858-1930, on the track
# loaded as detect_waypoints.load_center_track loads it (re-run after
# E-022): the closing descent W8_wire_left -> W1_start, median 5.95 cm
# over 83 frames, and the start-to-back segment W1_start -> W2_back_end,
# median 0.66 cm over 136 frames. Those 136 frames sit in three places,
# not along the line: 45 outward-move frames 858-902 (median 0.68 cm,
# p95 3.98, max 4.72), 49 frames 903-954 inside the W2_back_end station
# dwell itself, where the waypoint is the dwell mean so the distance is
# near zero by construction (median 0.05 cm, max 0.38), and the closing
# return 1889-1930 (42 frames, median 10.47 cm, p95 12.62, max 13.11),
# which holds every large value. The 858-954 half therefore reads
# median 0.16 cm only because the dwell dominates it, and the segment
# is not evidence about the whole W1 -> W2 line: W1_start is the parked
# rest position, and the carried loop never comes closer to it than
# 24.78 cm (frame 869; 26.75 cm at frame 858, 26.38 cm at frame 1930),
# so both segments meeting at W1 are matched at one end only.
# All values above recomputed 2026-08-28 on the E-022 track. The
# un-paused corners named in r5_waypoint_eval.md ("around frame 767",
# "around frame 1842") are literal prose in detect_waypoints.py, not
# detected quantities, so no corner frame number is quoted here.
(P, f"Table 7.{T_SEG} locates the asymmetry. Six of the eight segments hold a median under 1.3 centimetres and a maximum under 2.6 centimetres. Both outliers meet at the start waypoint. The participant did not pause at the corner where the cube leaves the wire, so that corner is not a waypoint, and the straight line drawn between the waypoints on either side cuts across the route the cube travelled around. The closing descent carries a median of 5.95 centimetres because of it. The start-to-back segment is the second outlier, and the frames assigned to it fall in three places rather than along the line. The largest group sits inside the back-end station itself, 49 frames on which the distance is near zero because that waypoint is defined as the mean of the same dwell, and the outward move supplies 45 more at a median of 0.68 centimetres. The remaining 42 fall in the closing return after the descent, at a median of 10.47 centimetres, and they carry every large value the segment holds. The start waypoint is also the parked rest position, which the carried loop never reaches: the cube stays at least 24.8 centimetres away from it throughout, so both segments that meet there are matched at one end only. Both figures measure the polyline model, not the object tracker."),

# designed vs measured steps: eval/reports/r5_waypoint_eval.md, E-017a
(P, "The measured geometry of the loop recording can also be read against the designed moves. The backward move was specified at about 30 centimetres and measures 28.7. The upward lift was specified at about 30 centimetres and rises 30.8 over a 31.2 centimetre segment. The leftward move was specified at about 45 centimetres and measures 32.8 as the straight-line distance between its endpoints, where the two segments of Table 7.3 that span it sum to 33.3, and the forward push specified at about 15 centimetres measures 8.4. The two short desk moves were executed shorter than the design; the design figures are approximate and the evaluation compares the trajectory against the detected waypoints rather than against the nominal lengths, so the discrepancy affects the description of the task and not the error statistics."),

# loop closure 46.9 mm between the loop-span endpoints 858 and 1930:
# eval/reports/r5_waypoint_eval.md (E-022 re-run, unchanged). Those two
# frames are where the carried run starts and stops, NOT the start
# waypoint: measured on the E-022 track the cube sits 26.75 cm from
# W1_start at frame 858 and 26.38 cm from it at frame 1930.
(P, "One further property is visible in the measured track alone. The loop begins at frame 858, where the cube is taken up, and ends at frame 1930, where it is set down, and both positions lie about 26 centimetres from the parked rest position rather than on it. The two differ from each other by 4.69 centimetres. Nothing in the comparison forces that agreement, since the polyline is closed by construction while the trajectory is not, so the residual combines whatever the object track drifts over the 36-second traversal with however far from the pick-up point the cube was set down."),

(P, "Against the loop traversal, the two scenarios agree in the middle of the distribution and separate in the tail. The medians are 0.97 and 0.79 centimetres, while the 95th percentiles are 2.36 and 9.32. The polyline tail comes from the corner the polyline does not model and from the parked start discussed above, and the rail scenario has neither: its reference is a single physical line the cube is constrained to follow."),

(H2, "7.3 Pose Recovery Accuracy"),

(P, "The recovery is graded against the two references of Section 7.1: synthetic masking of frames the tracker handled correctly, reported in Section 7.3.1 for the rail recording and in Section 7.3.2 for the loop recording, and manual wrist labels on the natural failure windows of the loop recording, whose protocol Section 7.3.3 states and whose measurements are pending. Synthetic masking evaluates the recovery under an optimistic failure model, clean absence: the withheld landmarks are missing and nothing else is wrong. Natural occlusion can also produce corrupted presence, a partly covered marker that still decodes with a wrong pose or a landmark placed on the occluder, and only the natural handover windows of the loop recording show that behaviour."),

(H3, "7.3.1 Synthetic Masking on the Rail Recording"),

(P, "The recovery of Chapter 5 replaces a lost wrist with a position derived from the object and then solves the elbow from that wrist by two-link inverse kinematics. Grading it requires frames where the correct arm pose is already known, so the evaluation takes frames the failure detectors accept, records the unmasked solve as the reference, and then removes exactly the landmarks the detectors would have removed. The pose the recovery has to reproduce is fixed before the recovery runs. Three methods run on identical masked input: holding the last solved angles, recovering the arm from the direction memory the solver keeps, and the object-conditioned recovery. Three levels of loss are tested, removing the elbow and wrist alone, then the shoulder as well, then both hips on top of that."),

# rail windows and numbers: eval/reports/r6b_recovery_synthetic.md and
# r6b_recovery_moving.md (E-025): 342 eligible right frames, run 207-536,
# five 45-frame windows; pooled S1 angle medians hold 3.40 / EMA 0.60 /
# object 1.33 deg (after the E-027 hip gate); object wrist-estimate error
# median 1.02, p95 2.88 cm;
# reach ratio 0.99-1.00, elbow bend 14-17 deg; FK wrist per window below
(P, f"A frame is eligible only when the hand holds the object, no detector fires on that arm or on the torso, the wrist sample is a measurement rather than a filled-in value, and the object-derived estimate exists. Torso failures disqualify arm windows as well, because the arm angles are expressed in the torso frame. On the rail recording only the right hand holds the cube, so only the right arm can be graded. The state of the idle left arm is not a condition, since one arm's solve depends on the torso frame and that arm's own landmarks alone. The rule leaves 342 eligible frames, 330 of them in one run from frame 207 to frame 536, the desk move and the lift of Section 7.1.1. The run ends where the filter of Section 2.4 repairs a wrist sample, and the natural wrist gap of Section 7.1.3 follows at frame 550. Five masked windows of 45 frames are carved from the run. In every window the arm is nearly straight while it pushes the cube, with the wrist at 99 to 100 percent of the combined upper-arm and forearm length and the elbow bent by 14 to 17 degrees. The reference arm turns by 3.0 to 6.0 degrees over a window, so these are slow outages on an extended arm."),

(P, "Two of the reference's own groups are not measurements on these frames. The rule keeps the detectors quiet on the torso, and on this recording the root is still a repaired group throughout, as Section 7.4 sets out. Reference and recovery are read against the same repaired frame, so the comparison is unaffected, but the arm angles are expressed in a repaired torso frame rather than a measured one. The elbow bend also sits below the 15 degrees at which Section 5.6 holds the shoulder twist, so the reference twist is a held value and not a measured one. Holding the last angles inherits it; the two recovery methods do not, since the hold of Section 5.6 acts on a twist read from a measured forearm and each method instead solves the twist from the rebuilt elbow and the wrist, and Table 7.4 shows what that difference costs on the opening frames of an outage."),

(TBL, [["Window (frames)", "Arm travel (deg)", "Hold: median (cm)", "Hold: max (cm)", "Direction memory: median (cm)", "Direction memory: max (cm)", "Object recovery: median (cm)", "Object recovery: max (cm)"],
       ["212 to 256", "4.0", "1.68", "3.06", "0.83", "8.61", "0.57", "14.85"],
       ["272 to 316", "3.0", "2.83", "3.16", "1.16", "7.86", "1.13", "14.52"],
       ["332 to 376", "6.0", "2.47", "4.84", "1.64", "7.37", "1.02", "6.40"],
       ["392 to 436", "6.0", "1.33", "2.03", "1.77", "6.94", "2.68", "6.64"],
       ["452 to 496", "5.2", "0.83", "1.23", "0.48", "7.33", "0.96", "7.60"]]),
(CAP, f"Table 7.{T_RMASK}. Wrist position error of the three methods over the five synthetic outages of the rail recording, with the elbow and wrist removed. The arm travel is the angle the reference arm turns through during the outage."),

(P, f"Table 7.{T_RMASK} reports, for each window, the distance between the wrist that each method's angles place and the wrist the tracker measured on the same frame. All three methods keep the wrist between 0.48 and 2.83 centimetres from the truth at the median. Holding the last angles is bounded by how far the arm moves during the outage, and its largest deviation stays under 5 centimetres in every window. The two recovery methods reach medians as small or smaller than holding in four of the five windows for the direction memory and three for the object-conditioned recovery, but larger worst frames, up to 8.61 centimetres for the direction memory and 14.85 centimetres for the object-conditioned recovery. Those worst frames are the first frames of each outage, in every window and for both methods. The rebuilt arm starts from the last measured angles, and with the arm nearly straight the twist it needs differs from the held twist of the reference by about 80 degrees in a coordinate that hardly moves the hand once the arm has settled; the rate limit of Section 5.6 walks the twist and the flexion across at 15 degrees per frame, and while the two are on their way the hand is off. The error falls by about 2 centimetres a frame, and from the eighth masked frame onward no window exceeds 2.55 centimetres for the direction memory or 3.77 centimetres for the object-conditioned recovery. The object-derived wrist estimate itself sits a median of 1.02 centimetres from the measured wrist, with a 95th percentile of 2.88, which is the accuracy of the anchor the recovery rests on. Pooled over the five windows with the elbow and wrist removed, the arm angle error has a median of 3.40 degrees for holding, 0.60 degrees for the direction memory, and 1.33 degrees for the object-conditioned recovery."),

(P, "The rail recording therefore bounds the recovery from the slow side. On an outage in which the arm turns by less than 10 degrees, a held angle is nearly right, and the recovery has little to gain in the median and a straight-arm singularity to lose. The loop recording supplies the fast case."),

(H3, "7.3.2 Synthetic Masking on the Loop Recording"),

(P, "The same rule runs on the loop recording with one difference: both hands hold the cube in turn, so a frame is eligible only when no detector fires anywhere in the body. Those conditions leave 154 eligible frames on the left and 304 on the right, which carve one masked window of 45 frames on the left and two on the right."),

# S1 pooled angle errors: eval/reports/r5_recovery_synthetic.md, S1_arm
# table, regenerated against the committed code (E-021, re-run under
# E-022 in eval/DECISIONS.md; the grip episodes now end at 1066 instead
# of 1065, the windows and every cell below are unchanged).
# The left side pools one window, the right side two.
(TBL, [["Side", "Method", "Angle error median (deg)", "p95 (deg)", "Worst window median (deg)"],
       ["Left", "Hold the last angles", "1.40", "10.31", "1.40"],
       ["Left", "Direction memory", "2.29", "6.82", "2.29"],
       ["Left", "Object-conditioned recovery", "6.06", "15.10", "6.06"],
       ["Right", "Hold the last angles", "1.02", "7.32", "1.52"],
       ["Right", "Direction memory", "0.76", "4.77", "0.97"],
       ["Right", "Object-conditioned recovery", "3.06", "24.56", "8.95"]]),
(CAP, f"Table 7.{T_MASK}. Arm angle error against the unmasked reference, pooled over the masked frames of each side, with the elbow and wrist removed. The left side carries one window and the right side two, so the left rows repeat their worst window."),

# interpretation of the negative result: eval/reports/r5_recovery_synthetic.md
# (E-021 regeneration, re-verified after the E-022 re-run)
(P, f"Table 7.{T_MASK} reports a result that runs against the technique. In these windows the object-conditioned recovery is beaten by both baselines, on both sides. A duration sweep from half a second to three seconds finds no crossover either. The reason is visible in the two inputs the technique depends on."),

# grip drift 0.86 / 12.86 / 13.09 cm per window; reach ratio 0.847 to 1.024;
# elbow bend 21.57 deg: eval/reports/r5_recovery_synthetic.md (E-021
# regeneration, re-verified after the E-022 re-run: unchanged),
# "What the windows contain" table and the interpretation
(P, "The first input is the hand-object offset. The estimate places the wrist at the object pose plus an offset learned while the hand holds the cube, so the estimate is only as good as that offset is constant. On the loop recording the grip episodes are long, the longest running 24 seconds, and the participant regrasps inside them. The offset sits 12.86 centimetres or more away from the value fitted over its episode in two of the three windows, reaching 13.09 centimetres in the left one, while the remaining right window sits at 0.86 centimetres. The wrist estimate inherits that difference directly, so its error reaches a median of 13.98 centimetres on the left side, while the right side, pooled over its good window and its bad one, stays at 2.16."),

(P, "The second input is the arm configuration, and it fails independently of the first. In the right-side window running from frame 661 the object-derived wrist is accurate to 1.18 centimetres, and the recovered arm is still wrong. Holding a box in front of the body puts the wrist at 85 to 102 percent of the combined upper-arm and forearm length, so the straight-arm degeneracy of Section 7.3.1 applies here too, and the solve returns a straight arm where the participant's elbow is bent by 21.57 degrees. Every window the eligibility rule admits sits in that configuration, because carrying the cube in front of the body puts the arm there."),

(P, "The windows themselves explain why the baselines do so well. The eligibility rule admits only windows in which the hand holds the cube, and on this recording those windows fall at the stations, where the hand is still: the reference arm travels between 13.75 and 27.71 degrees across the whole masked stretch. The hold baseline barely moves over such a window, so it barely errs, and the direction memory is still fresh. The comparison is therefore narrow in its conditions: it measures the recovery where a memory is at its strongest."),

# moving outage: eval/reports/r5_recovery_moving.md, reproduced by make_ch7_figs.py
(P, f"The one tracked stretch of the loop recording where the masked arm keeps moving is a right-hand slide across the desk, frames 858 to 931, and it separates the methods in the opposite direction. Two overlapping outages are carved from it by hand, under the same holding and detector conditions but without the spacing the rule imposes, each covering about 50 degrees of arm travel. Figure 7.{F_RECOV} shows the wrist position error over them, and Table 7.{T_MOVE} gives the same result as numbers."),

(IMG, FIG / "ch7_fig_recovery.png", 6.3),
(CAP, f"Figure 7.{F_RECOV}. Wrist position error of the three methods over two synthetic outages on a moving arm. The error is the distance between the wrist the solved angles place and the wrist the tracker measured on the same frame."),

# moving-window table: eval/reports/r5_recovery_moving.{md,json}, regenerated
# against the committed code (E-021 in eval/DECISIONS.md; unchanged by the
# E-022 re-run). Every cell matches the FK wrist columns of that report and
# Figure 7.3 is drawn from the same code path.
(TBL, [["Outage", "Method", "Wrist error median (cm)", "p95 (cm)", "Max (cm)"],
       ["Outage 1, 31 frames", "Hold the last angles", "2.04", "10.71", "15.39"],
       ["Outage 1, 31 frames", "Direction memory", "2.99", "3.26", "3.28"],
       ["Outage 1, 31 frames", "Object-conditioned recovery", "1.67", "2.17", "2.80"],
       ["Outage 2, 33 frames", "Hold the last angles", "2.17", "21.00", "21.39"],
       ["Outage 2, 33 frames", "Direction memory", "2.32", "2.72", "4.79"],
       ["Outage 2, 33 frames", "Object-conditioned recovery", "1.65", "2.39", "2.99"]]),
(CAP, f"Table 7.{T_MOVE}. Wrist position error over the two moving outages, with about 50 degrees of true arm travel in each."),

(P, f"Holding the last angles tracks the truth for about two thirds of a second and then diverges as the arm moves, reaching 15.39 and 21.39 centimetres by the end of the two outages. The object-conditioned recovery stays between 1.65 and 2.99 centimetres throughout, and its error does not grow with time. The direction memory sits between the two, better than holding but drifting as its memory ages."),

(P, "The two results together describe the technique. The object anchor carries a bias, set by how far the current grip is from the fitted offset and by how well conditioned the elbow solve is, and that bias is flat in time. A memory carries no bias at the moment the landmarks vanish and accumulates error afterwards, at a rate set by how fast the arm is moving. The method with the smaller error at that moment is the better one. On a still arm the memory is smaller and the recovery is not worth using; on a moving arm the memory grows past the bias within a second. Since the failures this system faces occur while the cube is being carried, the moving case is the operating case, and the slow windows of the rail recording and the still windows of the loop recording stand as the boundary of the claim."),

(P, "Two further properties hold across every masked window. Removing the shoulder as well leaves the arm chain solving against a shoulder recovered from the opposite side, and the ordering of the methods is unchanged. Removing both hips leaves the root frame with no support, and it holds rather than inventing a pose. In every masked frame of every scenario, each joint group that consumed a removed landmark reported itself as recovered rather than measured, with no exceptions over the nine window and masking-level combinations of the loop recording and the fifteen of the rail recording, so a downstream consumer can tell the two apart."),

(H3, "7.3.3 Recovery Accuracy on Labelled Natural Failure Windows"),

(P, "The windows of Sections 7.3.1 and 7.3.2 are stand-ins, and the recovery never runs on them outside the evaluation. The frames the recovery exists for are the natural failure windows, where the tracker has lost the arm on its own and no automatic reference exists. Manual wrist labels, the second reference of Section 7.1, take that role here."),

# label set: failure-mask runs of at least 5 frames inside a grip episode,
# every 5th frame -> 78 frames (54 left, 24 right), frames 1427 to 1890.
# Source: eval/failure/extract_label_frames.py (committed 9af65b2) and its
# output meta.json in eval/output/label_frames_r5/ (generated 2026-08-28).
(P, "The label set is chosen by rule rather than by hand, so that the choice of frames cannot favour either method. The failure mask of the loop recording in Section 7.1.3 supplies the runs: every stretch of at least five consecutive frames on which it rejects an arm, so that isolated blips are ignored. Every fifth frame of each such run is taken, which spreads the labels across a window instead of concentrating them. Of those, the frames where the hand on that side is inside a grip episode are kept, since the recovery applies only to a hand that holds the object. On the loop recording the rule selects 78 frames lying between frames 1427 and 1890, asking for the left wrist on 54 of them and the right wrist on 24, so both natural blackouts of Section 7.1.3 are covered."),

(P, "Each selected frame is labelled in two steps. The wrist is clicked on the colour image, which fixes the pixel the hand occupies. The aligned depth image is then read at that pixel, and the depth sample is back-projected through the colour intrinsics by the deprojection of Appendix D, which fixes the third coordinate. The result is a metric 3D point in the same frame the solver works in, obtained from the same sensor as every other position in this thesis and independently of the landmark detector that failed."),

(P, "The comparison is per frame and direct. The wrist that the recovered angles place and the wrist that the hold baseline places are each compared with the labelled point. Reporting both against one reference separates what the recovery contributes from what the recording would have given without it. The statistics are the median, the 95th percentile, and the largest deviation, taken per side over the labelled frames of that side."),

(TBL, [["Side", "Recovered: median", "Recovered: p95", "Recovered: max",
        "Hold: median", "Hold: p95", "Hold: max"],
       ["[pending manual labels]", "[pending manual labels]",
        "[pending manual labels]", "[pending manual labels]",
        "[pending manual labels]", "[pending manual labels]",
        "[pending manual labels]"]]),
(CAP, f"Table 7.{T_LABEL}. Distance in centimetres between the labelled wrist and the wrist each method places, over the labelled frames of the natural failure windows. The labels for the loop recording are pending, and the table carries a placeholder in place of values."),

(P, f"Table 7.{T_LABEL} will hold the result. The labels are placed by hand, and no number from the table appears anywhere else in this thesis. The label set, the selection rule, the deprojection, and the two methods compared are fixed before any label is placed."),

(P, "Two limits apply to the labels once they exist. The label is only as good as the click and as the depth sample beneath it, so a wrist that the cube hides completely can be pointed at on the image while the depth at that pixel belongs to the cube rather than to the hand, and such frames measure the cube. Sampling every fifth frame also trades density for effort, so the statistics describe the windows rather than every frame in them. Both limits are properties of the reference, not of the methods being compared, and they affect the recovery and the baseline identically."),

(H2, "7.4 Torso Stability"),

(P, "The torso carries the reference frame that every arm angle is expressed in, so an error there moves both arms at once. Section 7.1.3 located the problem on both recordings: a hip with full reported visibility and a depth from the wrong surface. The repair described in Section 5.5 puts a hip whose depth is rejected back on its own camera ray at a remembered depth, since the pixel stays reliable when the depth does not."),

# torso window figure and spreads: writing/v7/scripts/make_ch7_figs.py rerun
# (window 956-1130), E-011b in eval/DECISIONS.md
(P, f"Figure 7.{F_TORSO} follows the torso of the loop recording through the longest window in which both hips are corrupted at once, frames 956 to 1130, a case the line-consistency check alone cannot see because the two hips agree with each other while both are wrong."),

(IMG, FIG / "ch7_fig_torso.png", 6.3),
(CAP, f"Figure 7.{F_TORSO}. Root yaw and pelvis depth of the loop recording through the longest window in which both hips are corrupted at once, shaded. Each quantity is drawn twice, once with the depth-jump gate disabled and once with the gate and the ray repair active."),

# window spreads: recomputed by make_ch7_figs.py fig_torso (prints the values);
# pinned in E-011b, eval/DECISIONS.md
(TBL, [["Window (frames)", "Duration (s)",
        "Root yaw spread, depth-jump gate disabled (deg)",
        "Root yaw spread, depth-jump gate enabled (deg)"],
       ["896 to 931", "1.2", "2.5", "2.5"],
       ["956 to 1130", "5.8", "57.4", "15.3"],
       ["1182 to 1544", "12.1", "13.2", "13.2"]]),
(CAP, f"Table 7.{T_TORSO}. Spread of the root yaw across each torso failure window of the loop recording's manipulation phase, with the depth-jump gate disabled and enabled."),

(P, "The disabled configuration of the figure and the table switches off the depth-jump gate alone. The line-consistency check and the ray repair stay active in both configurations, so the comparison isolates the depth-jump gate rather than setting the whole repair against no repair at all."),

(P, f"Table 7.{T_TORSO} shows the gate acting where it is needed and staying out of the way elsewhere. On two of the three windows the line-consistency check already caught the corruption and the depth-jump gate changes nothing. On the window from frame 956 to frame 1130 the two hips fail together, and there the root yaw swings across 57.4 degrees without the gate and across 15.3 degrees with it. The pelvis behaves the same way in the lower panel of Figure 7.{F_TORSO}: the midpoint of the measured hips wanders through 21.9 centimetres of camera depth during the window, and the midpoint of the repaired hips through 0.5 centimetres."),

(P, "The residual spread of 15.3 degrees is not noise removed and forgotten. During a window the repaired orientation passes through a memory, which lags a real torso rotation while it holds a false one still, and the remaining spread mixes the two. That trade is deliberate: a repair that followed the raw pixel directions would reintroduce the wobble of hands crossing in front of the torso."),

# validator synthetic corruption: v1/kinematics/validate_occlusion_ext.py run
# 2026-08-28, sections 5 and 5b; 41 checks, no failures
# rail torso: Chapter 3 worked example (frame 533) and CH3_RAIL_LOG.md; the
# hips read the rail's depth (0.99 m) on frames 518-549, 1.13 m on 732-756;
# torso detectors fire 632-899 (r6b_failure_mask.md)
(P, "The rail recording shows how far that repair reaches. Its hip landmarks fall on the pixels where the pelvis meets the rail for all but the opening frames of the take, so both hips take the rail's depth together and the chain of Chapter 3, run on the measurement as it stands, decodes a pitch of about 32 degrees on an upright participant, as the worked example states on frame 533. Against the true vertical of the calibrated world the measured hips put the trunk 24.3 degrees from upright at the median over the take, and 28.3 degrees over frames 12 to 631, from the first frame after the hip depth settles on the rail to the last frame before the split. Because the offset arrives on both hips at once, the line-consistency check sees two hips that agree with each other, and the failure detectors of Chapter 5 fire in earnest only from frame 632, as Section 7.1.3 reports, where one hip pixel returns to the body while the other stays on the rail, the 19.40 centimetre split."),

(P, "The repair catches it earlier, through its depth memory. The first frames of the take measure the hips on the body at 1.22 metres, and over frames 4 to 11 the hip depth slides down to the rail's 0.99 metres. The shoulder-depth gate of Section 5.5 takes the hips on frames 5 and 6, where they lie more than 15 centimetres nearer the sensor than the shoulders, and from frame 7 the depth-jump gate takes over, since the measured depth has left the remembered 1.21 metres by more than 10 centimetres. The hips are then placed on their rays at that remembered depth for the rest of the take."),

(P, "The recovered pelvis stays at 1.21 metres, and the recovered trunk leans toward the sensor by 8.0 degrees at the median, 9.6 at the 95th percentile, which is the lean of a participant working over a desk rather than the 24.3 degrees the measurement gives. The repair rests on the memory having been seeded on the body. Had the take begun with the pelvis already behind the rail, the depth-jump gate would have had nothing to trip on, and the shoulder-depth gate alone would carry the repair. Chapter 9 states what that would cost."),
# eval/output/recovery_r6b/angles_recovery.csv (pel_z, root_ex), raw hips
# from the filtered landmark CSV; trunk tilt = angle between hip-mid ->
# shoulder-mid and the wall marker's in-plane up (calib T_cam_wall col 1):
# measured median 24.3 (frames 12-631: 28.3, p95 30.7), recovered median 8.0 p95 9.6;
# E-027 gate frames 5 (right hip) and 6 (both); depth-jump gate from frame 7

(P, "The same repair was checked against synthetic corruption, where the truth is known. A clean span of the reference recording of Chapter 5, the take that set the failure thresholds, is corrupted by pushing torso points along their own camera rays, which reproduces a wrong depth sample while leaving the pixel in place. Trusting the corrupted hips leaves the root frame 53.92 degrees off at the 95th percentile. Repairing them on their rays leaves it 8.86 degrees off. The corresponding check on the shoulder side, where the shoulder line is the corrupt one and the hips are clean, fires on the shoulder line and leaves the hips alone, and the root error falls from 34.41 to 6.25 degrees."),

(H2, "7.5 Qualitative Results"),

(P, "Until the manual labels of Section 7.3.3 exist, nothing in the natural failure windows is scored. They can be looked at. The reconstruction is projected back onto the colour frames it was computed from, which puts the solved skeleton and the measured landmarks in the same picture as the person. A skeleton that sits on the body indicates that the measurement, the solve, and the model agree with the scene."),

(P, f"Figure 7.{F_OVER} shows one frame from the longest left-arm blackout of the loop recording, which runs 8.1 seconds while the left hand is wrapped behind the carried cube. The left panel takes the landmarks as the tracker reported them. The left forearm ends at the participant's chest, several tens of centimetres from the cube the hand is holding, at full reported visibility. The right panel removes the landmarks the detectors reject and recovers the arm from the object. The forearm reaches out to the cube, and the frame is marked as a tracking failure."),

(IMG, FIG / "ch7_fig_overlay.png", 6.4),
(CAP, f"Figure 7.{F_OVER}. The reconstruction projected back onto a frame inside the longest left-arm failure window. Left: the landmarks taken as reported. Right: the rejected landmarks removed and the arm recovered from the object pose. Green marks the measured landmarks and the torso, blue the left arm, red the right arm, and the yellow cross in the right panel marks the object-derived wrist estimate the recovery anchors to."),

(P, "The two panels also show the limit of what the picture proves. The recovered forearm reaches the cube because the recovery places the wrist at the cube, so the agreement between them is built in rather than observed. The frame does establish that the recovery keeps the arm attached to the object it is holding for the whole window, that the rest of the body keeps tracking while one arm is recovered, and that the failure is declared instead of hidden. The measured skeleton in the left panel establishes the opposite: the tracker reported a wrong pose at full visibility, which a viewer can see."),

(P, "The torso repair shows the same way. Through the loop recording's window of frames 956 to 1130 in Section 7.4 the reconstructed pelvis stays at a plausible standing depth while the participant works at the desk, and the unrepaired pelvis slides toward and away from the camera without the person moving. The slide follows from hip depth samples that land on the hands crossing in front of the trunk instead of on the person, and it is visible in the projection long before it is visible in a number."),

(P, "Taken together, the four measured parts and the frames above describe a system whose object track follows its reference path to within about a centimetre for most of a traversal, whose kinematic solve adds no error of its own, whose torso repair survives the depth jumps that the tracker cannot detect, and whose arm recovery holds the wrist within a few centimetres on synthetic outages of a moving arm. Chapter 8 examines whether the same pipeline runs inside a frame period, and Chapter 9 returns to what the failure windows and the assumptions of Section 7.1 mean for the conclusions."),

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

out = REPO / "writing" / "v7" / "Chapter_7_Evaluation.docx"
doc.save(out)
print("saved", out, "| items:", len(content))

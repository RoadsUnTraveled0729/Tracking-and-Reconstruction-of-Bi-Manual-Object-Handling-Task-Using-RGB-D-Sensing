# Chapter 7 parked material (condensed build, 2026-09-07)

Removed from writing/v8/condensed/scripts/build_ch7.py when Chapter 7 was
restructured on decision D-007 (writing/v8/condensed/DECISIONS.md; the
supervisor's round 4 comments C30 to C42 and CH7_RECOMMENDATIONS.md): the
chapter is led by the one-handed rail task, the loop recording stays only
for the compact manual-label study, and the torso diagnostics leave the
main chapter. Every paragraph, table and caption below is verbatim from the
build of commit 2bcaad6 (figure and table numbers are those of that build).
Source comments with the evidence paths stay in that builder's git history.
The evidence itself is unchanged: eval/reports/r5_waypoint_eval.md,
r5_failure_mask.md, r5_recovery_synthetic.md, r5_recovery_moving.md,
r5_recovery_eligible.md, r6b_recovery_eligible.md, the torso window figure
script writing/v7/scripts/make_ch7_figs.py and
v1/kinematics/validate_occlusion_ext.py.

## 7.1.1 loop paragraph and the designed-loop figure (old Figure 7.2)

The loop recording changes only the task. The subject moves the cube around a closed loop of seven stations with both hands, passing it from one hand to the other, along a path marked on the desk and by a wire stretched above it. Figure 7.2 plots the designed loop, whose straight segments between the start and the stations, where the cube is held still, form its polyline of eight waypoints. During a handover both hands close around the cube and the detector loses the wrist landmarks.

[figure: ch2_fig_path.png, width 6.3 in]

*Figure 7.2. The designed loop in the gravity-levelled world frame: the eight stations, the straight segments between them, the desk plane, and the wire level.*

## 7.1.3 loop failure pattern, old Table 7.2 and its readings

The loop recording fails in a different pattern, drawn in the lower panel over the person-present span from frame 62 onward. The torso is rejected on 30.7 percent of that span, the left arm on 17.2 percent, and the right arm on 9.0 percent, after the closing step that bridges gaps of up to five frames. The failures cluster in the manipulation phase, where the torso is rejected on 43.2 percent of its frames against 8.6 percent during the approach, and both arms have their longest windows there.

| Detector | What it rejects | Frames | Percent of span |
|---|---|---|---|
| Acquisition, left arm | the detector declines the sample | 218 | 10.7 |
| Acquisition, right arm | the detector declines the sample | 108 | 5.3 |
| Acquisition, torso | the detector declines the sample | 9 | 0.4 |
| Segment length, left arm | an arm segment changes length | 50 | 2.5 |
| Segment length, right arm | an arm segment changes length | 50 | 2.5 |
| Torso line angle | hip line and shoulder line disagree | 537 | 26.4 |
| Torso width ratio | shoulder width over hip width leaves its band | 439 | 21.6 |
| Landmark step, left arm | a landmark jumps between frames | 62 | 3.0 |
| Landmark step, right arm | a landmark jumps between frames | 22 | 1.1 |
| Landmark step, torso | a landmark jumps between frames | 46 | 2.3 |

*Table 7.2. How often each detector fires on the loop recording, over the 2037 evaluated frames. A frame can trip several detectors at once, so the counts overlap. The grip-plausibility detector acts inside the recovery.*

Table 7.2 mixes two kinds of failure, and the distinction matters for what a recovery stage can do. The torso line-angle and width-ratio detectors carry most of the fires, and almost none of those frames are ones the tracker flagged itself. On the longest torso window, frames 1182 to 1544 over 12.1 seconds, one hip sits 31.3 centimetres deeper than the other against a clean split of 1.3. Both arm blackouts show the same pattern beforehand. The left forearm measures 34.7 centimetres against a clean median of 24.7 before frame 1458, and the right upper arm 47.2 against 25.8 before frame 1826. The medians are those calibrated on the loop recording itself. The geometry detectors fire before the tracker declines the sample.

That pattern decides which windows of the loop recording can be scored under the rule of Section 7.1. The left elbow is covered on 89 percent of the span and the left wrist on 90 percent, each with a longest landmark gap of 7.0 seconds, and the right elbow on 96 percent with a longest gap of 2.3 seconds. The natural blackouts therefore hold no reference of their own, and the arm-level rejection window around the left gap runs longer still, 8.1 seconds. Shorter clean stretches remain, 154 eligible frames on the left and 304 on the right, from which Section 7.3 builds its synthetic windows. The natural blackouts are graded against the manual labels of Section 7.3.3 and shown in Section 7.5.

## 7.2 loop trajectory against the designed path (old Figure 7.5, old Table 7.3)

The loop recording is compared against the designed loop of Section 7.1.1, the parked start and the seven stations joined by straight lines, with the stations taken from the stretches of the object track where the cube stops.

The comparison runs over the single loop traversal, frames 858 to 1930, of which 1032 carry a measured marker. Each measured position is assigned the closest segment and its distance to that segment is recorded (Figure 7.5).

[figure: ch7_fig_waypoints.png, width 6.4 in]

*Figure 7.5. The measured cube trajectory against the designed path. Left: the loop with its eight waypoints. Right: the distance from each measured position to the nearest segment.*

Over the traversal the trajectory sits a median of 0.8 centimetres from the designed path, with a 95th percentile of 9.3 and a mean of 1.7.

| Segment | Length (cm) | Frames | Median (cm) | p95 (cm) | Max (cm) |
|---|---|---|---|---|---|
| Start to back | 28.7 | 136 | 0.7 | 11.7 | 13.1 |
| Back to desk handover | 8.9 | 76 | 0.8 | 1.9 | 2.3 |
| Desk handover to left | 24.4 | 147 | 0.5 | 1.9 | 2.6 |
| Left to forward | 8.4 | 96 | 0.2 | 0.4 | 1.1 |
| Forward to lift top | 31.2 | 264 | 1.2 | 2.1 | 2.4 |
| Lift top to wire handover | 20.0 | 158 | 1.1 | 2.2 | 2.4 |
| Wire handover to wire left | 11.1 | 72 | 0.4 | 0.6 | 0.7 |
| Wire left back to start | 38.4 | 83 | 6.0 | 12.3 | 13.1 |

*Table 7.3. Distance from the measured trajectory to each designed segment, over the frames assigned to that segment.*

Table 7.3 locates the asymmetry in the two segments that meet at the start waypoint; the other six have a median under 1.3 centimetres and a maximum under 2.6. The subject did not pause at the corner where the cube leaves the wire, so that corner is not a waypoint and the straight line between its neighbours cuts across the route the cube travelled. The start waypoint is the parked rest position, which the carried loop never reaches. Both outliers measure the polyline model rather than the object tracker.

The two scenarios agree in the middle of the distribution and separate in the tail: medians of 1.0 and 0.8 centimetres against 95th percentiles of 2.4 and 9.3. The polyline tail comes from the unmodelled corner and the parked start, while the rail is a single physical line the cube must follow.

## 7.3 opening sentence on the two synthetic sections

The recovery is graded by synthetic masking of frames the tracker handled correctly, in Sections 7.3.1 and 7.3.2, and against the manual wrist labels of Section 7.3.3. Synthetic masking assumes clean absence, the withheld landmarks missing and nothing else wrong. Natural occlusion can also produce corrupted presence, a partly covered marker that decodes with a wrong pose, which only the natural windows show.

## 7.3.2 Synthetic Masking on the Loop Recording (whole; old Table 7.5, old Figure 7.6, old Table 7.6)

### 7.3.2 Synthetic Masking on the Loop Recording

The same rule runs on the loop recording with one difference: both hands hold the cube in turn, so a frame is eligible only when no detector fires anywhere in the body. That leaves 154 eligible frames on the left and 304 on the right, which carve one masked window of 45 frames on the left, frames 1674 to 1718, and two on the right, frames 661 to 705 and 1674 to 1718. The two windows from frame 1674 cover the same recording frames, one per arm.

| Side | Method | Angle error median (deg) | p95 (deg) | Worst window median (deg) |
|---|---|---|---|---|
| Left | Hold the last angles | 1.4 | 10.3 | 1.4 |
| Left | Direction memory | 2.3 | 6.8 | 2.3 |
| Left | Object-conditioned recovery | 6.1 | 15.1 | 6.1 |
| Right | Hold the last angles | 1.0 | 7.3 | 1.5 |
| Right | Direction memory | 0.8 | 4.8 | 1.0 |
| Right | Object-conditioned recovery | 3.1 | 24.6 | 9.0 |

*Table 7.5. Arm angle error against the unmasked reference with the elbow and wrist removed, pooled over the masked frames of each side and over the five arm angle columns, including the elbow coordinate that Section 3.4 holds at zero. The comparison excludes the held reference twist. The left side carries one window, so its rows repeat their worst window.*

Table 7.5 runs against the recovery: in these windows both baselines beat the object-conditioned recovery on both sides, and a duration sweep from half a second to three seconds finds no crossover. The reason lies in the two inputs the recovery depends on.

The first input is the hand-object offset. The grip episodes are long here, the longest running 24 seconds, and the subject regrasps inside them. The offset therefore sits 12.9 centimetres or more from the value fitted over its episode in two of the three windows, 13.1 in the left one, against 0.9 in the remaining right window. The wrist estimate inherits that difference, so its error reaches a median of 14.0 centimetres on the left side while the right stays at 2.2.

The second input is the arm configuration, and it fails independently: in the right-side window from frame 661 the object-derived wrist is accurate to 1.2 centimetres and the recovered arm is still wrong. Holding a box in front of the body puts the wrist at 85 to 102 percent of the combined upper-arm and forearm length, the straight-arm degeneracy of Section 7.3.1, and the solve returns a straight arm where the elbow is bent by 21.6 degrees. Every window the rule admits sits in that configuration.

The baselines do so well because the eligibility rule admits only windows in which the hand holds the cube, and here those fall at the stations, where the hand is still. The reference arm travels between 13.8 and 27.7 degrees across the whole masked stretch, so the hold baseline is nearly right and the direction memory is fresh. The comparison measures the recovery where a memory is strongest.

The one tracked stretch where the masked arm keeps moving is a right-hand slide across the desk, frames 858 to 931. The evaluation carves two overlapping outages from it by hand, each covering about 50 degrees of arm travel, and scores every frame of each window without the eligibility rule of Section 7.3.1. The rule would exclude 2 frames of the first outage and 9 of the second, where a reference joint group is not measured and, on frames 896 to 902, the torso detectors fire. The two outages share 26 frames and cover 38 frames in all. Table 7.6 is therefore an exploratory wrist-only comparison under those conditions rather than a second run of the protocol, and Figure 7.6 draws it.

[figure: ch7_fig_recovery.png, width 6.3 in]

*Figure 7.6. Wrist position error of the three methods over two synthetic outages on a moving arm, against the wrist the tracker measured on the same frame.*

| Outage | Method | Wrist error median (cm) | p95 (cm) | Max (cm) |
|---|---|---|---|---|
| Outage 1, 31 frames | Hold the last angles | 2.0 | 10.7 | 15.4 |
| Outage 1, 31 frames | Direction memory | 3.0 | 3.3 | 3.3 |
| Outage 1, 31 frames | Object-conditioned recovery | 1.7 | 2.2 | 2.8 |
| Outage 2, 33 frames | Hold the last angles | 2.2 | 21.0 | 21.4 |
| Outage 2, 33 frames | Direction memory | 2.3 | 2.7 | 4.8 |
| Outage 2, 33 frames | Object-conditioned recovery | 1.7 | 2.4 | 3.0 |

*Table 7.6. Wrist position error over the two moving outages, with about 50 degrees of true arm travel in each.*

Holding the last angles tracks the truth for about two thirds of a second and then diverges as the arm moves, reaching the largest deviations of Table 7.6 by the end of the two outages. The object-conditioned recovery stays under 3 centimetres throughout, and the direction memory sits between the two, better than holding but drifting as its memory ages. Scoring only the frames the rule admits keeps the recovery at the smaller median in both outages, 1.7 centimetres in each against 2.0 and 2.1 for holding. The largest hold deviations then fall to 9.1 and 8.6, so the tails of Table 7.6 come partly from the excluded frames.

A rerun that applies the eligibility rule before any error is scored, at the 45-frame duration of Section 7.3.1, selects no windows other than those of Table 7.4 and Table 7.5, the five rail windows and the three loop windows. In none of them does the reference arm turn by more than about 15 degrees inside the window, so under the protocol there is no eligible moving outage to score, and the comparison of Table 7.6 stays exploratory. On the three loop windows the rerun also gives the wrist position error of all three methods. In the right window from frame 661 the object-conditioned recovery places the wrist 1.5 centimetres from the measured wrist at the median, against 2.2 for the direction memory and 2.4 for holding. In the two windows from frame 1674 it sits 14.0 centimetres off on the left and 6.9 on the right, the error of the object estimate itself. The direction memory sits 4.3 and 1.4 centimetres off there, and holding 4.3 and 2.2.

In the two exploratory outages of Table 7.6 the object anchor carried an error that did not grow with time, while the held pose and the direction memory drifted as the arm moved. That is what a rigid grip with a measured object pose and no regrasp predicts. It is an observation on two short overlapping outages rather than a general law, and Section 7.3.3 shows the other side, where the frozen offset itself is wrong.

Every masked window shows two further properties. Removing the shoulder leaves the arm chain solving against a shoulder recovered from the opposite side, with the ordering of the methods unchanged, and removing both hips leaves the root frame unsupported, so it holds rather than inventing a pose. Each joint group that consumed a removed landmark reported itself as constrained in every masked frame, so a later stage can tell the two apart.

## 7.4 Torso Stability (whole; old Figure 7.7)

### 7.4 Torso Stability

An error in the torso frame moves both arms at once. On the rail recording the hip landmarks fall on the pixels where the pelvis meets the rail for all but the opening frames, so both hips take the rail's depth together. The chain of Chapter 3 then decodes a pitch of about 32 degrees on an upright subject, as the worked example of Section 3.5 shows on frame 533. Because both hips agree with each other, the detectors of Chapter 5 fire only from frame 632, at the 19.4 centimetre split.

The pipeline corrects the hip depth from the memory of clean frames before the solve, the preparation of Section 2.6, outside the recovery layer of Chapter 5. Against the true vertical of the calibrated world the measured hips put the trunk 24.3 degrees from upright at the median over the take, and 28.3 over frames 12 to 631. The corrected trunk leans toward the sensor by 8.0 degrees at the median and 9.6 at the 95th percentile, the lean of a subject working over a desk. The correction rests on the memory having been seeded on the body. A take beginning with the pelvis behind the rail would fall to the shoulder-depth check of Appendix G, which no recording tests.

Figure 7.7 follows the torso of the loop recording through the longest window in which both hips are corrupted at once, frames 956 to 1130, a case the line-angle detector alone cannot see because the two hips agree while both are wrong. The root yaw swings across 57.4 degrees with the hip depth preparation disabled and across 15.3 degrees with it, and the midpoint of the hips wanders through 21.9 centimetres of camera depth against 0.5 corrected. On the two other torso windows the check had already caught the corruption and the correction changes nothing. The residual spread comes from a memory that lags a real rotation while it holds a false one still.

[figure: ch7_fig_torso.png, width 6.3 in]

*Figure 7.7. Root yaw and pelvis depth through the shaded window in which both hips are corrupted at once, each drawn once with the hip depth preparation disabled and once with it active.*

The same correction was checked against synthetic corruption. A clean span of the reference recording that set the failure thresholds of Chapter 5, frames 300 to 419, was corrupted by pushing the two hips 10 centimetres along their own camera rays in opposite directions. The depth sample is then wrong while the pixel stays in place. The measure is the 95th percentile of the absolute difference in each of the three root Euler angles against the same solver's output on the uncorrupted span, a per-component figure rather than a rotation distance. Trusting the corrupted hips leaves that measure at 53.9 degrees and correcting them leaves it at 8.9.

## 7.5 the loop overlay figure (old Figure 7.8) and its readings

The reconstruction is projected back onto the colour frames it was computed from, so a skeleton that sits on the body shows that the measurement, the solve and the model agree with the scene.

Figure 7.8 shows one frame from the longest left-arm blackout of the loop recording, 8.1 seconds with the left hand wrapped behind the carried cube. In the left panel the landmarks are taken as reported, and the left forearm ends at the subject's chest, several tens of centimetres from the cube, above the visibility gate. The right panel removes the rejected landmarks and recovers the arm from the object: the forearm reaches the cube, and the frame is marked as a tracking failure.

[figure: ch7_fig_overlay.png, width 6.4 in]

*Figure 7.8. The reconstruction projected back onto a frame inside the longest left-arm failure window. Left: the landmarks as reported. Right: the rejected landmarks removed and the arm recovered from the object pose, the yellow cross at the object-derived wrist estimate.*

The picture proves little on its own: the recovered forearm reaches the cube because the recovery places the wrist at the cube, so that agreement is built in. The frame does establish that the arm stays attached to the object for the whole window, that the rest of the body keeps tracking, and that the failure is declared.

#!/usr/bin/env python3
"""Build writing/v7/Chapter_8_Real_Time_Feasibility.docx (V7 rewrite round).

Chapter 8 against the V7 TOC: 8.1 Causality of the Pipeline, 8.2
Computational Cost and Latency, 8.3 Offline and Real-Time Comparison.

Every number in this chapter comes from the frozen real-time round of the
primary R5 recording; the source file is named in a comment beside each
value. The three sources are:

  v2/reports/r5_realtime_probe.md   feature-preservation matrix, the
                                    causal adaptations, the measured
                                    summary, the sensor-switch items
  v2/dataset/r5_probe_baseline.txt  per-stage profile blocks (person,
                                    object, capture broker), declared
                                    merger delay
  v2/dataset/r5_probe_validation.txt  the 13 live checks and the
                                    flags-off regression tail

Branch end-to-end percentiles were recomputed from the pinned run dumps
(v2/output/v2_person_dump.csv, v2_object_dump.csv, v2_integrate_dump.csv)
and agree with the validation file: person p50 9.0 / p95 22.8 / p99 25.1,
object p50 13.1 / p95 14.0 / p99 15.1, tick interval p50 33.3 / p95 34.8 /
p99 35.3 over 2129 ticks.

Style rules applied: skill_set/thesis-statement-style.md,
skill_set/thesis-structure-rules.md (no speed values for the movement;
software frame rates and latencies are fine), writing/WRITING_SKILL.md.
Figures: make_ch8_cost_fig.py, make_ch8_latency_fig.py.

Rail-only round (2026-09-01, E-026): every measured number now comes from
the live probe run on the RAIL recording (v2/dataset/r6b_probe_baseline.txt
full feature set, r6b_probe_baseline_off.txt recovery and gate off,
r6b_probe_validation.txt: 10 of 12 checks pass, the two angle-tracking
bounds fail on the near-vertical arm's azimuth and on a shallow lag
minimum; both reported in the text). The "# src:" comments that name the
r5 files describe the loop-recording run this chapter previously reported;
the loop numbers are kept only in the one comparison sentence of 8.3.
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v7" / "figures"

H1, H2, P, IMG, CAP, TBL = "h1", "h2", "p", "img", "cap", "tbl"

content = [
(H1, "Chapter 8: Real-Time Feasibility"),

(P, "Every result so far was computed with a whole recording in hand. The landmark smoother of Chapter 2 passes over each signal twice, the object track of Chapter 4 is cleaned as a complete time series, and the grip episodes of Chapter 5 are fitted over their full extent. A clinical or robotic use of the system needs the reconstruction while the motion is still happening, and that removes all three freedoms at once. This chapter reports the cost of the same reconstruction when each frame must be finished before the next one arrives."),

# src: 2099 frames / 70 s recording -> skill_set/r5-experiment-state.md
#      (R5 = recording_20260825_222315); opt-in flags -> v2/reports/r5_realtime_probe.md
#      section "Feature preservation"; the options themselves ->
#      v2/integration/run_v2.py (--object-recovery, --plausibility-gate,
#      --display-lpf; all three set by the --probe-r5 preset)
(P, "Real time here means the recording of Chapter 2, the rail recording, replayed at its recorded pacing in place of a live camera. Frames become available one at a time, each must be handled before its successor appears, and no stage may read a frame that has not been captured yet. The arrangement imposes the constraint a camera imposes, on data whose offline results are already established. The two versions can therefore be compared frame by frame on identical input. A capture process owns the source and publishes each aligned frame into a shared frame buffer that both branches read. Exchanging the recording for the sensor changes that one process and nothing downstream of it. The live features this chapter measures are selected by explicit options, so the streaming stack runs with or without them."),

(P, "Section 8.1 sorts the processing stages by whether they can run causally and states the replacement used where they cannot. Section 8.2 gives the measured cost of every stage and the end-to-end latency. Section 8.3 sets the offline and real-time versions side by side, feature by feature, and states the remaining requirements for a switch to a physical sensor."),

(H2, "8.1 Causality of the Pipeline"),

# no measured values in this paragraph
(P, "A stage is causal when its output for a frame depends only on that frame and the frames before it [55]. Offline processing is free of the restriction, and Chapters 2, 4, and 5 use that freedom. The pipeline's stages fall into three groups: the ones that are already causal, the ones that needed a causal replacement, and the ones that are analysis tools with no live counterpart."),

(P, "The largest group needs no change. The kinematic solve of Chapter 3 is closed form and holds no state across frames, so the eight landmark positions of one frame determine the thirteen angles of that frame and nothing else enters. The recovery machinery of Chapter 5 works the same way. It consists of the segment-length and torso-line gates, the repair of a gated hip along its camera ray with the depth-jump gate, the twist hold and the limit on how far an angle may move from one frame to the next, and the reconstruction of a wrist from the object pose followed by the two-link elbow solution. Each of these steps is closed form and reads no frame that has not yet arrived. Marker detection and planar pose estimation on the marker branch read a single image. None of these stages changes when the recording is replaced by a stream, and all of them run live through the same code."),

# src: trailing window and the three-rejection escape hatch ->
#      v1/realtime/person/realtime_person.py CausalLandmarkFilter
#      (MAX_REJECTS = 3), used unchanged by v2/person/v2_person.py
(P, "Three stages of the offline chain do read the future, and each needed a replacement. The first is the despiking test of Chapter 2, which centres its window on the sample being judged. Live, the window trails: a sample is compared against the median of the samples already accepted, and a rejected sample becomes a missing sample, handled by the same fallback that handles any other missing landmark. A trailing window that never accepts a rejection goes stale after genuine motion, because the window still describes where the hand used to be and every new sample then looks like a spike. The filter therefore accepts a sample after three consecutive rejections and rebuilds its window around it, because a spike which persists is not a spike."),

# src: delay of two frame intervals -> v2/dataset/r5_probe_baseline.txt
#      ("delay 2 frame(s) = 66.7 ms"); merger states MEASURED /
#      INTERP / HELD / BLEND -> v2/integration/v2_integrate.py header
(P, "Gap bridging is the second. Interpolating across an interior gap needs the sample on the far side of it, which does not exist yet. The live path keeps only the bounded form of the idea, and it lives in the merger. Output is rendered at a fixed delay of two frame intervals behind capture. The merger therefore interpolates between two samples it already holds, and it holds the last pose whenever the gap runs past the declared delay. Each rendered frame states which of those it is, whether measured, interpolated, held, or a ramp back into a measurement after a long dropout, so the display never shows an invented pose without saying so."),

# src: fourth-order Butterworth at 3 Hz zero-phase -> Chapter 2
#      (writing/v7/scripts/build_ch2.py, section 2.5); One Euro live
#      settings -> v2/person/v2_person.py (--min-cutoff 1.0 --beta 1.0)
(P, "The landmark smoother is the third, and the substitution is the one Chapter 2 anticipated. A fourth-order Butterworth filter run forward and backward has no phase delay because it is not causal [55], [57], and running it live is impossible. Its replacement is the One Euro filter applied to each landmark coordinate [40], a causal low-pass whose cutoff widens as the coordinate changes faster, so it smooths a still pose firmly and follows a moving one closely. Section 8.3 gives what the exchange costs in lag and in angle."),

# src: 27 live rejects -> v2/reports/r5_realtime_probe.md ("E-019 gate 27 rejects");
#      offline: 0 detected rows rejected, 41 never-detected rows blanked
#      (eval/output/recording_20260825_222315_scaled_object_world_filtered
#      _clean.csv against ..._filtered.csv; E-022 in eval/DECISIONS.md)
(P, "The marker branch needed no new mechanism, only a different position in the chain. The cleaning rule of Chapter 4 discards a sample that sits farther from the last kept sample than the slow task can physically produce. The live branch applies the same rule to the detected sample as it arrives, ahead of its causal filter, while the offline step applies it after the zero-phase filter, to rows the smoother has already been through. The two tests therefore judge different samples. The live one sees every raw detection, including the ones the offline smoother later pulls back toward their neighbours, and it rejected 19 detections over the recording. The offline rule rejected no detected row, and it removed only the one row on which the marker was never detected."),

# src: running mean then moving average, and the thirty-sample rest
#      reference -> v2/common/object_link.py (MU_WARMUP, MU_ALPHA,
#      REST_N = 30); offline forms -> eval/failure/grip_state.py
(P, "Two parts of the grip machinery of Chapter 5 take an online form in the live path. The hand-object offset is fitted offline once per episode, over the whole episode, in the gravity-levelled world coordinate frame. Live it is a running mean over the first clean frames of an episode and then a slowly updated moving average, fitted directly in the coordinate frame the solver works in. A rigid offset between a hand and a held object is constant in any fixed coordinate frame, so the detour through the levelled world adds nothing. The test for whether the object is being carried is referenced offline to a rest pose read from the whole recording; live the rest pose is the median of the first thirty object samples of the session. It gates entry into an episode only and never exit, so a pause with the object held does not split one episode into two."),

# src: five-frame bounded exit -> v2/reports/r5_realtime_probe.md ("ADAPTED FOR
#      CAUSALITY", episode EXIT) and eval/failure/grip_state.py
#      EXIT_FRAMES = 5
(P, "At episode exit, and only there, causality costs something that cannot be recovered. The offline state machine can clear the frames after a release once it sees the release. The live tracker confirms a release only after five consecutive frames of a cleanly measured wrist beyond the release radius, and until then the wrist stays anchored to the object. A genuine release therefore carries up to five frames of anchored wrist before the episode closes. The bound is fixed and known. Table 8.1 collects the replacements."),

# src: every row -> v2/reports/r5_realtime_probe.md section "Feature preservation";
#      constants (3 rejections, 30 samples, 5 frames) as cited above
(TBL, [["offline stage", "live form"],
       ["Despiking with a window centred on the sample",
        "Trailing window; a rejected sample becomes a missing sample; three rejections in a row are read as real motion and the window is rebuilt"],
       ["Interpolation across an interior gap",
        "No upstream equivalent; the merger interpolates only between samples it already holds and holds the last pose beyond the declared delay"],
       ["Fourth-order Butterworth smoothing run forward and backward",
        "One Euro filter on each landmark coordinate, with a cutoff that widens as the coordinate changes faster"],
       ["Cleaning of the object track, applied to the smoothed track",
        "The same cleaning rule, applied to the detected sample ahead of the causal filter"],
       ["Hand-object offset fitted per episode in the levelled world frame",
        "Running mean over the first clean frames, then a slowly updated moving average, fitted in the solver frame"],
       ["Carried test referenced to a rest pose from the whole recording",
        "Rest pose from the first thirty object samples of the session; gates episode entry only"],
       ["Episode exit, with the frames after a release cleared afterwards",
        "Exit confirmed after five consecutive clean frames beyond the release radius; the wrist stays anchored until then"]]),
(CAP, "Table 8.1. The offline stages that needed a causal replacement, and the live form of each."),

# src: offline-only list -> v2/reports/r5_realtime_probe.md ("OFFLINE-ONLY BY NATURE")
(P, "The last group has no live form and needs none, because its members are analysis tools rather than parts of the reconstruction. Comparing the object track with the reference path, the graded failure mask over the whole recording, the accuracy grading under synthetic masking, and the rendered overlay video all read a finished recording by construction. Live, the solver's own gates do the work the graded mask does in analysis. One detector belongs to the reconstruction rather than to the study, the test that rejects a measured wrist lying too far from the held object, and it runs inside the live grip tracker."),

# src: display smoother applied at packet write, dumps unfiltered ->
#      v2/common/display_lpf.py module docstring
(P, "One stage falls outside the three groups because it exists only in the live path. The streamed packet passes the display smoother of Chapter 6 on its way out. That smoother acts at the moment the packet is written, so the recorded output stays unfiltered and the evaluation of Chapter 7 is untouched by it."),

(H2, "8.2 Computational Cost and Latency"),

# src: Ryzen 9 7950X 16C/32T, 64 GB, RTX 3080 10 GB ->
#      v1/realtime/REALTIME.md "Hardware" note (2026-07-31), and
#      Appendix B of this thesis
(P, "Every timing in this section comes from the workstation described in Appendix B: an AMD Ryzen 9 7950X processor with 16 cores and 32 threads, 64 GB of memory, and an NVIDIA GeForce RTX 3080 graphics card with 10 GB of video memory. The work is divided the same way throughout. The pose detector's network runs on the graphics card, and everything else, including all of the kinematic mathematics, runs on the processor. Absolute values belong to that configuration; the shape of the budget, meaning which stage dominates and which are not worth accelerating, carries over to other machines."),

# src: the two runs -> v2/dataset/r5_probe_baseline.txt (per-stage profile, live options
#      off) and v2/dataset/r5_probe_validation.txt (full feature set)
(P, "Each stage times itself around its own call, while both branches run concurrently and the merger runs on its own output tick, so each stage is timed under load rather than in isolation. Two runs over the full rail recording are reported, and they are kept apart throughout. Table 8.2 and Figure 8.1 come from the run that carries a stage-by-stage profile; in that run the object-conditioned recovery and the live cleaning rule were switched off. Table 8.3 comes from the run with both enabled. Comparing the two gives the cost of the recovery layer. Apart from that comparison, every stage figure below belongs to the first run."),

# src: all rows -> v2/dataset/r5_probe_baseline.txt
#      capture      "[stage] align+publish ms"  2.36 / 2.54 / 2.67
#      landmark     person profile block: mediapipe 8.03/21.90/25.84,
#                   deproj+filt 0.40/0.52/0.60, solve 0.34/0.43/0.50,
#                   shm-write 0.00/0.01/0.01
#      marker       object profile block: detect 12.97/13.77/14.19,
#                   pnp 0.14/0.19/0.22, filter+map 0.16/0.19/0.21
(TBL, [["stage", "p50 (ms)", "p95 (ms)", "p99 (ms)"],
       ["capture: depth alignment and publication", "2.41", "2.66", "3.08"],
       ["landmark: pose detection", "7.42", "11.63", "12.00"],
       ["landmark: deprojection and causal filtering", "0.41", "0.51", "0.57"],
       ["landmark: kinematic solve", "0.18", "0.22", "0.25"],
       ["landmark: record write into shared memory", "0.00", "0.01", "0.01"],
       ["marker: detection", "13.79", "14.91", "16.03"],
       ["marker: planar pose estimation", "0.15", "0.22", "0.23"],
       ["marker: causal filtering and world mapping", "0.17", "0.20", "0.22"]]),
(CAP, "Table 8.2. Per-stage cost over the full rail recording, both branches running concurrently, from the run with the recovery layer and the live cleaning rule switched off. The frame budget at 30 frames per second is 33.3 ms."),

# src: drawn from the same v2/dataset/r5_probe_baseline.txt blocks; see
#      writing/v7/scripts/make_ch8_cost_fig.py
(IMG, FIG / "ch8_fig_cost.png", 6.4),
(CAP, "Figure 8.1. Per-stage and end-to-end cost against the frame budget, from the run of Table 8.2. Each bar is the median and each whisker reaches the 99th percentile."),

# src: 8.03 vs branch total 8.78, and 12.97 vs branch total 13.27,
#      both from the profile blocks of v2/dataset/r5_probe_baseline.txt;
#      0.40 + 0.34 and 0.14 + 0.16 = 0.30 from the same blocks
(P, "The cost in Table 8.2 is spread unevenly. Detection dominates on both sides: pose detection takes 7.42 ms at the median against 8.03 for the whole landmark branch in the same run, and marker detection takes 13.79 against 14.13 for the whole marker branch; the rows of each branch in Table 8.2 add up to its whole within rounding. Everything the thesis develops mathematically fits in the remainder. Deprojection with the causal filter costs 0.41 ms, the thirteen-angle solve 0.18, and the record write into shared memory rounds to zero at the precision of the table. On the marker branch, planar pose estimation and the mapping into the world frame together cost 0.32 ms against the detector's 13.79."),

# src: recovery off, solve 0.34 p50 / 0.50 p99 -> v2/dataset/r5_probe_baseline.txt
#      recovery on, solve 0.40 p50 / 0.56 p99 -> v2/reports/r5_realtime_probe.md
#      ("solve within it"); the ~0.06 ms/frame delta is that report's
#      own statement ("0.34 -> 0.40")
(P, "The cost of the recovery layer of Chapter 5 is the difference between two runs of the same stack on the same recording. With the recovery off the solve takes 0.18 ms at the median and 0.25 at the 99th percentile. With the object link, the grip tracker, and the recovery enabled it takes 0.41 and 0.58. The layer therefore costs about 0.23 ms per frame, less than one part in a hundred of the frame budget, and it is active on most frames of this recording, since the live grip episode runs from frame 199 to the end. The layer is that cheap because no step searches or iterates."),

# src: 2099/2099 frames, 29.6 fps, 71.0 s -> v2/dataset/r5_probe_baseline.txt
#      ("[done] consumed 2099 frames ... 29.6 fps sustained");
#      2129 ticks and person p99 25.1 -> v2/dataset/r5_probe_validation.txt
#      headroom 33.3 - 25.1 = about 8 ms
(P, "Table 8.3 gives the end-to-end picture of the full feature set. The stack consumed all 900 frames of the recording with none dropped, sustaining 29.0 frames per second over 31.0 seconds of playback, about one second of which is start-up before the first frame is consumed, and the merger emitted 929 output ticks at a steady interval. The marker branch carries the larger worst case on this recording, finishing within 16.7 ms at the 99th percentile, and so keeps 16.6 ms of headroom against the budget; the landmark branch finishes within 13.0 ms and keeps 20.3."),

# src: v2/dataset/r5_probe_validation.txt (person p99 25.1, object p99 15.1,
#      cadence p99 35.3 over 2129 ticks); p50/p95 recomputed from the
#      pinned dumps v2/output/v2_person_dump.csv, v2_object_dump.csv,
#      v2_integrate_dump.csv -> 9.0/22.8, 13.1/14.0, 33.3/34.8
(TBL, [["quantity", "p50", "p95", "p99"],
       ["landmark branch, end to end (ms)", "8.4", "12.5", "13.0"],
       ["marker branch, end to end (ms)", "14.0", "15.4", "16.7"],
       ["merger output tick interval (ms)", "33.2", "35.2", "35.3"]]),
(CAP, "Table 8.3. End-to-end cost of the live path with the full feature set enabled. The nominal output tick interval equals the frame budget."),

# src: declared delay 2 frames = 66.7 ms -> v2/dataset/r5_probe_baseline.txt;
#      branch-to-branch skew p50 -1 / p99 0 frames, 0 dropped as
#      stale -> v2/reports/r5_realtime_probe.md ("B-A frame skew")
(P, "The sustained rate does not settle the delay of a single frame. Figure 8.2 divides that delay between its stages. The merger renders at a fixed delay of two frame intervals, 66.7 ms, behind capture. The delay is set by design rather than produced by the computation, and it makes the bounded interpolation of Section 8.1 possible. Both branches finish inside the first of those two intervals at the 99th percentile, so a viewer waits for the declared delay rather than for the computation. The two branches are paired by frame index. Across the run the marker record paired with a landmark frame trails it by one frame at the median and at the 99th percentile, and no record was discarded as stale."),

# src: see writing/v7/scripts/make_ch8_latency_fig.py
(IMG, FIG / "ch8_fig_latency.png", 6.4),
(CAP, "Figure 8.2. The end-to-end delay of one captured frame, divided between its stages, for the full feature set of Table 8.3. The solid part of each branch bar is the median cost, the lighter extension reaches the 99th percentile, and the merger renders the frame at its declared delay of two frame intervals."),

# src: 8.03 / 0.34 = about 24, so "more than twenty times", from the
#      profile block of v2/dataset/r5_probe_baseline.txt
(P, "Two consequences follow for any later work on the system. Accelerating the kinematics saves no measurable time, because the solve is already about forty times cheaper than the detector that feeds it in the profiled run, and about eighteen times with the recovery enabled; the detector is the only stage worth reducing, and a lighter model variant is the documented way to reduce it [43]. The source sets the pace, and the stack kept up with it throughout, finishing every frame. The measurement bounds the cost per frame and the margin against the budget, not the maximum rate the machine could reach."),

(H2, "8.3 Offline and Real-Time Comparison"),

# no measured values in this paragraph
(P, "The live path is not a replacement for the offline pass. Its purpose is to carry as much of the offline feature set as causality allows, so that the reconstruction a viewer sees while the motion happens is the same reconstruction the evaluation of Chapter 7 grades afterwards. Table 8.4 sets the two side by side, capability by capability."),

# src: every row -> v2/reports/r5_realtime_probe.md section "Feature preservation";
#      the three-frame guard -> v2/common/object_link.py SKEW_MAX = 3
(TBL, [["capability", "offline form", "live form", "relation"],
       ["Segment-length and torso-line gates", "per frame", "same construction", "unchanged"],
       ["Torso repair along camera rays, with the depth-jump test", "per frame", "same construction", "unchanged"],
       ["Twist hold and the limit on angle change between frames", "per frame", "same construction", "unchanged"],
       ["Wrist from the object pose and two-link elbow solution", "per frame", "same construction", "unchanged"],
       ["Object pose available to the landmark branch", "read from the cleaned track as a table", "newest published marker record, object pose rebuilt in the camera frame, with a guard on how far apart the two frame indices may be", "new wiring"],
       ["Per-joint output states carried to the reconstruction", "written into the record", "packed into the streamed packet and carried through the delay buffer", "new wiring"],
       ["Hand-object offset and grip episodes", "fitted per episode over the recording", "online tracker that opens an episode only after several consecutive holding frames and closes it after a bounded delay", "adapted"],
       ["Cleaning rule on the object track", "applied to the smoothed track", "applied ahead of the causal filter", "adapted"],
       ["Landmark despiking and smoothing", "centred window, zero-phase filter", "trailing window, One Euro filter", "adapted"],
       ["Comparison with the reference path", "whole track against the ground truth", "no live counterpart", "offline only"],
       ["Graded failure mask over the recording", "detectors over the whole signal", "the solver's own gates; the wrong-measurement test runs live", "offline only, in part"],
       ["Accuracy grading under synthetic masking", "needs a reference pass", "no live counterpart", "offline only"]]),
(CAP, "Table 8.4. Feature preservation between the offline pipeline of Chapters 3 to 5 and the live path; the adapted rows are the replacements of Table 8.1."),

# src: exact reconstruction of the camera-frame object pose and the
#      three-frame guard -> v2/common/object_link.py docstring and
#      SKEW_MAX = 3; tags to Unity -> v2/reports/r5_realtime_probe.md
(P, "Most of the reconstruction transfers without alteration, and two capabilities needed new wiring rather than new mathematics. The first is the landmark branch's access to the object. Offline the recovery reads the cleaned object track as a table; live it reads the most recent record the marker branch has published and rebuilds the object pose in the camera coordinate frame from it, by inverting the mapping into the world frame of Chapter 4 and the handedness conversion of Chapter 6. Both mappings are fixed and invertible, one a rigid transformation and the other a reflection, so the rebuilt pose is exact rather than approximate. A guard rejects an object record whose frame index differs from the index of the frame being solved by more than three. The second is that the solver delivers its per-joint output state to the reconstruction, so that a group shown as constrained, solved on this frame from a landmark the recovery rebuilt, is distinguishable on screen from a group that is merely being held."),

# src: all of v2/dataset/r5_probe_validation.txt: 13/13 checks, person
#      coverage 2099/2099, object live 1978/2099, causal lag 3 frames,
#      worst group median 0.47 deg / p95 2.76 deg over 594 clean frames
(P, "An automated check suite grades the live run, and ten of its twelve checks pass, and the two that do not are the angle-tracking bounds. Coverage accounts for all 900 frames on the landmark branch, and the object is live on 829 of them; the 71 frames without a live object all fall in the manipulation phase, 19 of them the live gate's rejections and the rest frames on which the marker branch produced no usable record. Both branch budgets pass, as does the merger's tick interval. The live angles of the working arm are compared with the offline recovery solve on the 179 frames where that arm is cleanly measured on both sides. The comparison is restricted to the arm because the live torso repair gates the hips on almost every frame of this recording, for the reason Section 7.4 gives, so the root is rarely a measured group on both sides at once."),

(P, "The lag that minimises the difference is five frames, one more than the bound the suite sets, and the minimum is shallow: the median differs by 0.14 degrees between lags of three and seven, because the arm moves slowly. At that alignment the elbow flexion differs from the offline result by a median of 0.42 degrees and a 95th percentile of 1.33, the shoulder elevation by 1.44 and 2.30, and the shoulder twist by 7.28 and 15.68. The shoulder azimuth differs by 16.07 and 26.70 degrees, which fails the 20 degree bound, and it does so for the reason Section 3.4.2 states: the arm hangs within 15 degrees of straight down throughout the slide, where the azimuth is close to its undefined configuration and a small change in the filtered landmarks moves it a long way. On the loop recording, where the arms move through the working range, the same suite reported a lag of three frames and a worst-group median of 0.47 degrees. The exchange Chapter 2 left open therefore costs a filter lag of five frames, a fraction of a degree on the well-conditioned angles, and 16.07 degrees at the median on the azimuth, which is near its degenerate configuration throughout this recording."),

# src: v2/dataset/r5_probe_validation.txt: rec R 811 / L 692 frames,
#      CONSTRAINED inside offline failure windows L 255 / R 125,
#      episode coverage 90 percent right / 89 percent left,
#      1538 of 2129 ticks carry non-measured tags
# NOTE: v2/reports/r5_realtime_probe.md states "19 right" for the wrist-from-object count;
#       the validation file's 125 is used here (see the round report)
(P, "The recovery fires where the offline study says it should. Object-derived wrist estimates reached the solver on 625 frames of the right hand, the only hand that holds the cube, and the object placed the wrist on 147 of them. Output marked constrained falls inside the offline failure windows on 101 frames of the right arm and 112 of the left, the idle arm the solver holds. The live grip episode covers 90 percent of the 682 offline holding frames, frames 207 to 888. It enters a few frames later, because an episode opens only after several consecutive holding frames. The per-joint output states reached the reconstruction on every one of the 929 output ticks, since at least one group of the idle arm is held on each."),

# src: declared 50 mm vs true 45 mm marker size (50/45 = about 11
#      percent) and the live-session checklist -> v2/reports/r5_realtime_probe.md
#      ("The calibration trap", "Sensor-switch checklist");
#      marker size still an assumption -> eval/DECISIONS.md E-009a
(P, "The comparison above was produced from a recording, and the step to a physical sensor is a change of one option on the capture process. Three items remain open in that step. First, a scene calibration built from a live stream must be given the true printed size of each marker. The stored calibration of the recording declares a marker size of 50 millimetres against the 45 millimetres printed, as Chapter 2 states, about eleven percent larger, while its transformations carry the true scale. A planar pose estimate scales its translation in proportion to the marker size it is given, so passing the declared value to a live pose estimate would scale every translation by that factor. The correction is applied once, where the calibration is written. Second, the rest reference of the grip tracker assumes the object begins the session at rest and in view for about a second, which the designed task provides and a free-form session would not. Third, a session with the camera in place has not been recorded under this configuration."),

# src: 0.40 + 0.34 = 0.74 ms landmark branch and 0.14 + 0.16 = 0.30 ms
#      marker branch, so about 1 ms together, from v2/dataset/r5_probe_baseline.txt
(P, "The reconstruction keeps pace with the source on one workstation, at a declared delay of two frames, with the recovery layer costing a fraction of a millisecond per frame and the mathematics of Chapters 3 to 5 costing about one millisecond for both branches together. The offline pass keeps its role as the reference, and the live path is a lagged version of it whose differences sit in a small number of named places: a filter lag of a few frames, a bounded anchoring of the wrist at the end of a grip, and the analysis tools that belong to a finished recording."),

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
    elif kind == IMG:
        path = Path(item[1])
        assert path.exists(), f"missing figure: {path}"
        doc.add_picture(str(path), width=Inches(item[2]))
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

out = REPO / "writing" / "v7" / "Chapter_8_Real_Time_Feasibility.docx"
doc.save(out)
print("saved", out, "| items:", len(content))

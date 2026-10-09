# Chapter 8 parked material (condensed build, 2026-09-07)

Removed from writing/v8/condensed/scripts/build_ch8.py when Chapter 8 was
rewritten on the user's brief of 2026-09-07 (focus on how the offline pass
was transferred to the live structure, the proposed system structure, and
what was lost; few numbers, because accuracy measurement is Chapter 7's
scope). Verbatim from the build of commit 2bcaad6. The evidence is
unchanged: v2/dataset/r6b_probe_baseline.txt, r6b_probe_baseline_off.txt,
r6b_probe_validation.txt, v2/dataset/m03_rail_corrected.{json,txt},
v2/output/*_r6b_full.csv, writing/v7/scripts/make_ch8_latency_fig.py.

## 8.2 Computational Cost and Latency (whole section; Tables 8.2 and 8.3, Figure 8.1)

### 8.2 Computational Cost and Latency

Every timing comes from the workstation of Appendix B; the pose detector's network runs on its graphics card and everything else on the processor. Absolute values belong to that configuration; the shape of the budget carries over to other machines.

Each stage times itself around its own call while both branches run concurrently, so each is timed under load. Table 8.2 comes from the run with a stage-by-stage profile and the object-conditioned recovery and the live cleaning rule switched off; Table 8.3 from the run with both enabled.

| stage | p50 (ms) | p95 (ms) | p99 (ms) |
|---|---|---|---|
| capture: depth alignment and publication | 2.41 | 2.66 | 3.08 |
| landmark: pose detection | 7.42 | 11.63 | 12.00 |
| landmark: deprojection and causal filtering | 0.41 | 0.51 | 0.57 |
| landmark: kinematic solve | 0.18 | 0.22 | 0.25 |
| landmark: record write into shared memory | 0.00 | 0.01 | 0.01 |
| marker: detection | 13.79 | 14.91 | 16.03 |
| marker: planar pose estimation | 0.15 | 0.22 | 0.23 |
| marker: causal filtering and world mapping | 0.17 | 0.20 | 0.22 |

*Table 8.2. Per-stage cost over the full rail recording, from the run with the recovery layer and the live cleaning rule switched off. The frame budget at 30 frames per second is 33.3 ms.*

Detection dominates on both sides: pose detection takes 7.42 ms at the median against 8.03 for the whole landmark branch, and marker detection 13.79 against 14.13 for the marker branch. Everything the thesis develops fits in the remainder, and no such stage reaches half a millisecond.

The recovery layer of Chapter 5 costs the difference between the two runs. With the recovery off the solve takes 0.18 ms at the median and 0.25 at the 99th percentile; with the object link, the grip tracker and the recovery enabled it takes 0.41 and 0.58. The layer therefore costs about 0.23 ms per frame, less than one part in a hundred of the frame budget.

Table 8.3 gives the end-to-end cost of the full feature set. The stack consumed all 900 frames with none dropped, at 29.0 frames per second over 31.0 seconds of playback, and the merger emitted 929 output ticks at a steady interval. The marker branch has the larger worst case, 16.7 ms at the 99th percentile with 16.6 ms of headroom against the budget; the landmark branch finishes within 13.0 ms. The slowest landmark frame took 34.26 ms, just past one frame interval. The replay therefore meets the budget at the 99th percentile, while a few frames run past it.

| quantity | p50 | p95 | p99 |
|---|---|---|---|
| landmark branch, end to end (ms) | 8.4 | 12.5 | 13.0 |
| marker branch, end to end (ms) | 14.0 | 15.4 | 16.7 |
| merger output tick interval (ms) | 33.2 | 35.2 | 35.3 |

*Table 8.3. End-to-end cost of the live path with the full feature set enabled. The nominal output tick interval equals the frame budget.*

The sustained rate does not settle the delay of a single frame, which Figure 8.1 divides between its stages. The merger renders two frame intervals, 66.7 ms, behind capture, a delay set by design that makes the bounded interpolation of Section 8.1 possible. Both branches finish inside the first of the two intervals at the 99th percentile, so a viewer waits for the declared delay rather than for the computation. That delay is a buffering choice, distinct from the lag of the causal filter that Section 8.3 measures. The time from the sensor to the screen, which adds the display's own refresh, was not measured.

[figure: ch8_fig_latency.png, width 6.4 in]

*Figure 8.1. The end-to-end delay of one captured frame, divided between its stages, for the full feature set of Table 8.3. The solid part of each branch bar is the median cost and the lighter extension reaches the 99th percentile.*

Accelerating the kinematics saves no measurable time: the solve is already about forty times cheaper than the detector that feeds it, and about eighteen times with the recovery enabled. The detector is the only stage worth reducing, and a lighter model variant is the documented way [43]. The measurement bounds the cost per frame and the margin against the budget, not the maximum rate the machine could reach.

## 8.3 Offline and Real-Time Comparison: the check-suite paragraphs and the angle-difference numbers

An automated check suite grades the live run, and ten of its twelve checks pass. The landmark branch covers all 900 frames, and the object is live on 829 of them; the 71 frames without a live object all fall in the manipulation phase, 19 of them the live gate's rejections. Both branch budgets pass, as does the merger's tick interval. The live angles of the working arm are compared with the offline recovery solve on the frames where that arm is cleanly measured on both sides. The suite as first run tested that condition at the unshifted frame and then shifted the angle series, so a few of its 179 pairs carried a reference that was not clean at its own time. The figures below come from a rerun with the pairing corrected, on the archived live records of the same run. Each live frame is paired with the reference frame the lag places beside it, and both must be clean. The reference solve was rebuilt with the solver of that time and reproduces every historical angle to the printed precision. The corrected pairing keeps 174 frames and moves no figure by more than a degree. The comparison covers the arm only, because the live hip depth preparation acts on almost every frame of this recording (Section 7.4), so the root is rarely a measured group on both sides at once.

The two failures are the angle-tracking bounds. The lag that minimizes the difference is five frames, one more than the bound the suite sets. The minimum is shallow: the median differs by less than 0.2 degrees between lags of three and seven. At that alignment the elbow flexion differs from the offline result by a median of 0.4 degrees and a 95th percentile of 1.2, the shoulder elevation by 1.4 and 2.3, and the shoulder twist by 7.0 and 15.1. The shoulder azimuth differs by 16.4 and 26.9 degrees and carries the shoulder group's 95th percentile to 23.3 degrees, past the 20 degree bound. The reason is the one Section 3.4.2 states: the arm hangs within 15 degrees of straight down throughout the slide, near the azimuth's undefined configuration. On the loop recording, where the arms move through the working range, the same suite reported a lag of three frames and a worst-group median of 0.5 degrees. The live records of that run were not archived, so those figures stand with the first pairing. The exchange Chapter 2 left open therefore costs an estimated alignment of five frames between the live and the offline angle series, a median elbow flexion difference under half a degree, and a median shoulder elevation difference of about a degree and a half.

The recovery fires where the offline study says it should. Object-derived wrist estimates reached the solver on 625 frames of the right hand, the only hand that holds the cube, and the object placed the wrist on 147 of them. Output marked constrained falls inside the offline failure windows on 101 frames of the right arm and 112 of the left. The live grip episode covers 90 percent of the 682 offline holding frames, entering a few frames later because an episode opens only after several consecutive holding frames. The output states reached the reconstruction on all 929 ticks.

The reconstruction consumes every frame of the source at a declared delay of two frames, with the recovery layer costing a fraction of a millisecond per frame. The live path differs from the offline pass in an alignment lag of a few frames, a bounded anchoring of the wrist at the end of a grip, a display smoother on the output only, and the analysis tools that belong to a finished recording. The numbers come from a replay on one workstation, and the delay from the sensor to the screen was not measured.

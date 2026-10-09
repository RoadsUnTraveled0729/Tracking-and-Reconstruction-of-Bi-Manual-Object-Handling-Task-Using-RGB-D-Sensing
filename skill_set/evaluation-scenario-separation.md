# Evaluation scenario separation (E-023)

User direction 2026-08-31: the evaluation separates two scenarios,
WITHOUT occlusion and WITH occlusion, and the current focus is the
without-occlusion one.

State:
- WITH occlusion: R5 = recording_20260825_222315 stays the primary;
  all frozen R5 reports and thesis Chapter 7 numbers come from it.
- WITHOUT occlusion: R6B = recording_20260831_065553 (30 s, 900
  frames, recorded 2026-08-31), the revised setup with a straight
  horizontal raised rail: the cube is lifted from the desk onto the
  rail and slid to its far end, so the rail line physically
  constrains the slide and is the ground-truth path. Take 1
  (recording_20260831_065504, r6a) failed the A6 precondition on
  every landmark and is rejected (user confirmed: use the newest
  take). Both bags live in Video/ (gitignored) and in
  ~/Desktop/ENSC498/recordings/.
  The archive files were renamed to descriptive names on 2026-09-23; the
  old-to-new map is eval/recordings_archive/RENAME_MAP.tsv.
- Evaluator: eval/gt/eval_rail_scenario.py (rail height = upper mode
  of the height histogram, band = half a cube; total-least-squares
  line; perpendicular errors; since E-024 the track is levelled by
  the calibrated gravity first). R6B headline (levelled): travel 40.9
  cm, perpendicular median 0.97 cm, p95 2.36 cm, rail line 0.05 deg
  from horizontal (eval/reports/r6b_rail_eval.md). detect_waypoints.py stays pinned
  to the R5 seven-station plan and is not applied to rail recordings.
- R6B natural failures: one 3.0 s right-wrist gap mid-slide
  (MediaPipe visibility, not occlusion); the idle left arm is
  low-visibility most of the recording. Object-conditioned recovery
  fills the right-wrist gaps (101 frames). Overlay FK check on R6B:
  right wrist FK-vs-measured median 8.5 cm (open item, likely the
  long-grip wrist bias; not yet analyzed).

Why: the with-occlusion scenario mixes tracking error with occlusion
handling; the rail scenario isolates plain tracking accuracy with a
physically constrained ground truth.

Thesis integration (2026-08-31): the user supplied five laboratory
photographs of the rail setup (working area 45 by 30 cm drawn on grid
paper, rail 38.7 cm long, lying flat, 3.8 cm tall with an 8.8 cm
wide top face (corrected under E-024), spirit level used to level it; sources in
writing/v7/figures/src/rail_*.jpg, orientations corrected by
handwriting direction since top-down phone EXIF is unreliable).
Section 2.1 presents the setup (figures via make_ch2_rail_figs.py;
since 2026-09-01 Ch2 is environment only with figures 2.1-2.8),
Section 7.1.1 defines both reference paths, and Section 7.2 closes
with the rail-line evaluation and the scenario comparison
(make_ch7_rail_fig.py; Ch7 figures now 7.1-7.9).

Thesis focus (user direction 2026-09-01): the WHOLE thesis is based on
the rail recording (R6B). The loop recording (R5) is mentioned only in
Chapter 7's occlusion evaluation (introduced there as "a second
recording"). The internal names R5/R6B never appear in thesis prose; the
prose says "the recording". Round of 2026-09-01: Ch1 unchanged (user),
Ch2 rail-only, abstract rewritten, Ch3 worked example on rail frame 533,
Appendices A/C/D/E/F on the rail recording. Ch7 plan and the Ch4-9
adaptation list are logged in writing/v7/PROGRESS.md (Ch7 NOT written
yet, by user direction). Known data property: the rail recording's hip
landmarks take the rail's depth (0.99 m), so the MEASURED torso frame is
pitched about 32 degrees on every detector-clear frame (stated in Ch3).
The recovery layer repairs it (E-027, 2026-09-02): depth-jump gate from
frame 7 on a memory seeded on the body, plus the new memory-free
occluder gate (hip > 15 cm nearer than the shoulder midpoint -> placed
at the shoulder depth). Recovered trunk 8.0 deg median from vertical.
Unity captures must use eval/output/recovery_r6b/angles_recovery.csv
(--angles-csv), never the hold-last stream; clear /dev/shm/*_v2 and
stale senders first.

R6B fixes shipped 2026-09-01 (E-024 in eval/DECISIONS.md):
1. Wrong wall-marker lobe on R6B (the depth-annulus gravity seed was 59
   deg off because the desk marker sits at the desk's front edge) ->
   new seed estimate_tabletop_between() in extract_aruco_poses.py (plane
   on the desk surface between the desk card and the object card,
   preferred when both are detected; annulus fallback; R5 seed unchanged
   within 1 deg). R6B re-extracted and the chain re-run from
   scale_correction to run_recovery; object/desk poses bit-identical,
   only the wall pose and gravity changed (seed agreement now 6.2 deg).
2. eval_rail_scenario.py now levels the track by the calibrated gravity
   (carry.LeveledWorld) before the height segmentation. Levelled R6B
   headline (eval/reports/r6b_rail_eval.md): 407 slide frames, travel
   40.9 cm, perpendicular median 0.97 cm, p95 2.36 cm, max 3.08 cm,
   vertical median 0.32, horizontal 0.81, rail line 0.05 deg from
   horizontal, desk level 3.5 cm, rail level 7.4 cm. The old 1.01/2.58/
   2.92 deg numbers were taken in the tilted desk-marker frame.
3. The rail lies FLAT (2-by-4: 3.8 cm tall, top face 8.8 cm wide,
   38.7 cm long); "on edge, 8.8 cm high" was wrong and is corrected.
4. Reference path of R6B (user definition): axis-aligned, one direction
   per leg: straight back (z) from the parked start to W1 at the rail's
   depth, straight up (y) to W2 at rail height, along the rail (x) to
   W3 at the rail's far end; corners from the fitted rail line and the
   parked mean, NOT from the track's corners (legs 25.48 / 3.61 / 37.44
   cm; eval/reports/r6b_waypoints.json; figure make_ch7_rail_traj_fig.py
   -> ch7_fig_rail_traj.png, reference path drawn with the track).
5. Marker size. Printed marker: 45 mm (user, confirmed 2026-09-01 and
   2026-09-25). The pinned chain declares 0.050 m to the detector at
   PnP time (v1/aruco/frames.py MARKERS via extract_aruco_poses.py)
   and eval/gt/scale_correction.py rescales every desk and object
   translation by 0.9 (eval/common/marker_size.py) to the 45 mm print
   before calibration. All thesis numbers are on the 45 mm scale. Do
   not reopen.
   "Assumed" wording removed thesis-wide (Ch2, Ch7, Ch8, Ch9,
   Appendix E); E-009a's open item is closed.
Structure (user direction 2026-09-01): Chapter 2 is environment only
(2.1 setup, 2.2 MediaPipe, 2.3 ArUco, 2.4 filtering; no path section);
both recordings and their reference paths open Chapter 7 as Section
7.1.1 (rail trajectory + waypoints figure, rail tape photographs, loop
path figure). Chapter 7 is rail-led since the same day (E-025: synthetic masking on
R6B with harness --side-only; 7.3.1 rail, 7.3.2 loop, 7.3.3 labels).
Ch4/5/6/8/9 are on the rail recording (E-026: live probe re-run on R6B,
10/12 checks, azimuth of the near-vertical arm and a shallow lag minimum
fail the loop-era bounds and are reported as such). Every chapter except
Ch1 is now rail-based; the loop recording appears in Ch7's occlusion
parts, Ch9's failure illustrations, and one Ch8 comparison sentence.

How to apply: new rail recordings go through the pinned chain
(eval/README.md) with eval_rail_scenario.py as the ground-truth step;
scenario labels belong in report titles and any thesis text that uses
these numbers. See [[r5-experiment-state]] and [[marker-simplicity]].

Round 6 (2026-09-08, supervisor C50): a THIRD recording is planned, the
two-hand rail take R7 (right hand slides the cube to the middle of the
rail, the left hand takes over and slides it to the far end), recorded
by the user on eval/RECORDING_R7_HANDOVER.md. It enters Chapter 7 only,
as a second recording with its own section; R6B stays the thesis
recording everywhere else, and no worked example or figure of Chapters
2 to 6 changes. Register the stem as alias r7 in eval/common/paths.py
before running the pinned chain; the precondition checker's wrist lines
are expected to FAIL on coverage (each hand rests for half the take),
torso PASS is the acceptance criterion.

R7 RECORDED AND ACCEPTED (2026-09-09): recording_20260909_000024 (alias
r7, 1499 frames, 50 s; the last of eight takes that night, user: use the
latest only). Every landmark passes the precondition (right wrist 99.3
percent). The wall card had shifted (centre 7 cm nearer, plane tilted
44 deg, in-plane up 28 deg off), so calibrate_scene.py --gravity-from
scene_calibration_r6bc.json carries the r6b gravity (camera-to-desk
pose unchanged within 1 deg / 5.5 mm; E-034). Results: slide 1072
frames, 42.4 cm, perpendicular median 0.26 / p95 1.65 / max 3.44 cm;
handover frames 864-1022 (left hand arrives, right hand leaves; hold
radius 0.25 m) at 29 to 35 cm along the slide, cube within 1.7 cm of the
line; torso detector 326 frames, hips ray-repaired 644-1060; FK wrists
1.0 / 1.2 cm from the measured wrists. Thesis: Section 7.7 (D-021),
Figures 7.11-7.13, Table 7.1; the recovery section is now 7.8.
Tools: eval/gt/rail_waypoints.py, eval/failure/handover_analysis.py,
eval/failure/compare_hip_hold.py. The user's hip-freeze idea
("people won't move while handling the object; freeze L24 to its last
known value when the hand or object blocks the depth") is the opt-in
RobustChainSolver(hip_hold=True): on r7 root yaw spread 0.13 deg vs 4.59
with the ray repair over the covered window; on r6b it would change 895
of 900 frames. NOT adopted for the thesis (user decision 2026-09-09: keep the
preparation of Section 2.6 for this version, revisit after the weekly
usage limit resets only if the supervisor asks or the user still wants
it; the cheap first step is a numbers-only rerun); stated in Sections
7.7 and 9.2.


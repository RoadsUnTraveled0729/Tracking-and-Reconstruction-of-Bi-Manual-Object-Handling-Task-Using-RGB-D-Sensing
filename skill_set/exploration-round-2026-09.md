# Exploration round 2026-09: v2 and v3 plan while the thesis is under review

Written 2026-09-08 by Claude from three read-only explorations (v3 state,
v2 open items, thesis future work) and one design pass; the user chose
the four decisions below and asked for the plan to be kept in the repo
before any milestone starts. Status: NOT STARTED. Each milestone marks
itself DONE here (date, commit hash) when it finishes.

## Context

The thesis (Thesis_V8_Condensed, 161 pages, commit 5660113) is with the
supervisor and the user wants to keep exploring the two code tracks in
the meantime. Same-day update: supervisor round 6 arrived while this
plan was being written (C50, writing/v8/PROF_COMMENTS_ROUND6.md). A
separate thesis session (commit 3c70f01) planned a NEW two-hand
hand-over take on the rail (alias r7, protocol
eval/RECORDING_R7_HANDOVER.md) and waits for the user to record it. The
thesis track owns writing/, the r7 alias in eval/common/paths.py and the
pinned chain on that take; this exploration stays out of its way (see
Coordination below). The two tracks:

- v2: the live pipeline (capture broker, --source bag|live, pipelines A
  person / B object on a shared-memory frame ring, merger, Unity receiver
  IntegratedSceneReceiverV2). Its R5 probe round closed 2026-08-26 and
  the R6B replay ran 2026-09-01 (E-026). The physical camera session (M6)
  was never done as a documented round.
- v3: the RTMPose exploration track (rtmlib + ONNX Runtime GPU, env
  v3rt). One day of work on 2026-08-06: Phases 0-3 done, S2 quaternion
  prediction beats the hold-last baseline on all hard gates, end-to-end
  replay at 28.7 fps. It has only ever seen the February 2026 recording
  and has never been run on the two thesis recordings.

The exploration targets evidence the thesis itself says it lacks
(Chapter 10 future work and Table 9.1; Section 8.3 open items), usable
in the defense or a follow-up paper, without touching the thesis:

1. The live-sensor path (Table 9.1 last row; Section 8.3): prepared end
   to end, the session with the subject deferred.
2. An independent detector comparison: RTMPose versus MediaPipe on the
   same recordings and the same manual wrist labels (DEFENSE_QA.md
   names the RTMPose track as the baseline a journal version would add).
3. Pure-kinematic occlusion strategies (v3 S2 to S6) versus the
   object-conditioned recovery on identical inputs; the thesis says the
   free-arm failure has no object to rebuild from, which only a
   kinematic strategy addresses.

## User decisions (2026-09-08)

- Camera work: PREPARE ONLY. Everything possible without a person in
  frame is done; sessions with the subject are deferred milestones with
  a ready checklist.
- Priority: v3 leads, v2 interleaved.
- Autonomy: the v3 rule (never stop for approval; log every choice as
  SETTLED/UNCERTAIN/BLOCKED at the moment it is made; session review at
  the end) applies to BOTH tracks for this exploration, with a
  checkpoint report after every commit and a push after every milestone.
- S6 (object-conditioned recovery vendored into v3 as a strategy) is in
  scope.

## Verified facts the plan rests on

Hardware: RealSense D435 attached on USB now (lsusb 8086:0b07); RTX
3080 10 GB; env v3rt has onnxruntime 1.22.0 with TensorRT, CUDA and CPU
providers; pyrealsense2 imports in base python and in v3rt; thesis and
eval python is /home/luo/anaconda3/bin/python3. GPU runs need the five
CUDA-12 dirs from v3/configs/default.json model.cuda_lib_dirs on
LD_LIBRARY_PATH. Unity 6000.3.19f1 at ~/Unity/Hub/Editor.

Recordings: rail R6B Video/recording_20260831_065553.bag (900 frames),
loop R5 Video/recording_20260825_222315.bag (2099 frames), the February
bag v3 used, and v2/output/live_20260806.bag (2.5 GB, undocumented,
UNINDEXED so unreadable; a negative result, see V2-1).

Manual wrist labels (the only independent wrist measurement):
eval/labels/frames_r6b/labels.json (26 frames, right wrist: failure
550..684 step 5 plus clean 500/520/540/700/720) and
eval/labels/frames_r5/labels.json (20 failure labels left 1427-1492 step
5, 1777, 1787, right 1775, 1880, 1885, 1890, plus 7 clean). Format per
frame and side: u, v, depth_m, xyz_cam (colour optical frame, metres),
depth_valid_px. Intrinsics in meta.json equal the v3 extraction
intrinsics (fx 607.561, ppx 323.938), so the label deprojection equals
v3's depth_sampler. Grader: eval/failure/eval_labeled_recovery.py
(truth = unity_from_sensor(xyz_cam), distances in cm, median/p95/max).

Frame conventions: camera frame (labels, v1 raw CSV, v3 extraction)
-> solver/Unity space by (x, -y, z) (v1/kinematics/root_frame.py:12,
v3/replay/runner.py:27); levelled desk world only on the object path
(eval/offset/carry.py LeveledWorld; inverse recovery_core.py:65-72).
Frame indices differ between extractors (v1 counts every frame return,
v3 BagSource counts aligned pairs only; 899 vs 898 on the February
bag), so every cross-track join is on time_s (5 ms tolerance) and
prints the offset.

Unattended Unity: eval/unity_check/run_unity_capture.py launches the
editor (unity_binary, editor_pids refuses a running editor, DISPLAY)
and drives it by flag files: Unity/Assets/Editor/EvalPlayBootstrap.cs
(/tmp/r5_autoplay_on|stop|quit|state, ScenePath hard-coded to
rig.unity) and Unity/Assets/Scripts/EvalFrameDump.cs (/tmp/r5_capture_on,
one PNG per applied frame keyed on ArucoSceneReceiver.lastFrame).
render_ch7_trails.py adds -logFile, freshness acceptance and a SHA-256
manifest. IntegratedSceneReceiverV2 extends ArucoSceneReceiver and
self-spawns when /dev/shm/integrated_scene_v2 and /dev/shm/aruco_scene
exist, so the v2 stream works in rig.unity unchanged. V3Scene needs its
own bootstrap and dumper copies (v3 must not edit existing scripts).

v3 extraction CSV (tools/extract_bag_to_csv.py:72-77): frame, time_s,
per landmark _x _y _z _score _src _u _v, det_ran, det_reasons, box.
v1 raw CSV: frame, time_s, has_pose, per landmark _x _y _z _vis _src.
v3 consumers read only _x/_y/_z, so both feed run_csv and the offset
table; v1 raw CSVs exist for both thesis recordings under
v1/mediapipe/output/<stem>_landmarks_raw.csv.

Marker size defect: v2/calibration/live_calibrate.py:194 and 218-220
use MARKERS from v1/aruco/frames.py (0.050 for ids 1 and 2, 0.150 wall)
while the printed size is 0.045 (eval/common/marker_size.py
ASSUMED_BLACK_SQUARE_M; make_r5_calib.py:33,51-53 applies it for the bag
path). Grip tracker rest assumption: v2/common/object_link.py:83
REST_N = 30, 153-161.

validate_v2.py reference: dumps v2/output/v2_{person,object,integrate}
_dump.csv from run_v2.py --source bag --dump with the defaults (the
February bag, v1/aruco/output/scene_calibration.json) against
v1/mediapipe/output/recording_20260224_083945_landmarks_filtered_v2.csv
and v1/aruco/output/recording_20260224_083945_object_world_filtered.csv
(both exist). The current dumps are the R6B flags-on run; copy aside
before re-running.

S6 feasibility: the offline recovery (eval/failure/recovery_core.py
build_inputs) is whole-recording and not causal; the causal form exists
in v2/common/object_link.py (GripTracker 129-214, ObjectPoseReader
97-111). A bounded S6 vendors v1/aruco/frames.py verbatim, copy-adapts
GripTracker and the closed-form two-link elbow from
v1/kinematics/occlusion_ext.py:344-365 (without the capsule branch),
reads eval/output/<stem>_scaled_object_world_filtered_clean.csv and
the calibration JSON by absolute path, and needs a causal bone-length
calibrator (v3 has none; config bones.calibrate_frames is unused).
Not cheap: the offline per-episode mu with retro-clearing; a v3 object
branch of its own (S6 stays replay-only).

v3 live source: a LiveSource sibling of replay/bag_source.py copy-adapting
capture_broker.open_live and assert_profile (56-80), about 80 lines;
realtime.py gains --source and --record. The device is exclusive, so
v2 and v3 never run live together; the clean cross-track basis is one
recorded bag replayed by both stacks.

## Coordination with the thesis track (round 6, the r7 hand-over take)

- The D435 is one exclusive device. The r7 recording (the user runs
  ~/Desktop/ENSC498/record_realsense_bag.py) has priority. The camera
  milestones V2-2 and V3-6a run only when no recording session is
  scheduled, never leave the broker holding the device, and stop the
  pipeline before the session ends; if a recording session is
  imminent, log the milestone BLOCKED and take the next CPU milestone.
- Once r7 is accepted by the thesis track it becomes a shared basis for
  this exploration: replay it through v2 (--source bag, probe flags) and
  v3 (extraction, offset table, label compare when the thesis track
  labels it), and add its hand-over interval as a bimanual R-type
  scenario (V3-3). The exploration never registers r7 itself, never
  runs run_recovery or detect_failures on it before the thesis track
  has, and reads its eval outputs read-only.
- Any new alias this exploration needs for its own live recordings
  (V2-5) is registered only after the thesis track has finished r7, or
  kept v2-local (a --calib and --bag pair) until then.
- HANDOVER.md: while the thesis track waits for the recording, its
  section stays the "Latest task"; exploration milestones add their own
  dated section below it and never rewrite the thesis section.
- The thesis text stays untouched by this exploration even though the
  thesis track is editing it; a conflict-free commit needs git pull
  --rebase before every push and no edits under writing/.

## Binding rules

- writing/ untouched; v1 frozen (occlusion_ext.py the only additive
  exception); eval pinned numbers never change, new eval work is
  additive with ids from E-034; v3 copy-only isolation with the hash
  manifest; v3 may read eval/output, eval/labels and Video/ by absolute
  path but never imports eval or v1 at runtime.
- Delegation and model routing: AGENTS.md, Master workflow rules
  (user rules 2026-09-23), is authoritative. The master briefs and
  verifies; subagents do all work (worker Opus, code-reviewer Opus,
  checker Sonnet, scout Haiku, a Fable fork only when a task is too
  hard for Opus or needs the full session context).
- Checkpoint report after every commit; push after every finished
  milestone; HANDOVER.md rewritten in the same commit; decisions logged
  when made (v3/V3_DECISIONS.md D-023 onward, eval/DECISIONS.md E-034
  onward, .agent/DECISIONS.md for v2); evidence text files pinned under
  v3/dataset and v2/dataset; large outputs gitignored.
- GPU-timed runs (v2 validators with compute-budget checks, v3 latency)
  never overlap another GPU job or an editor capture (SERIAL below).
- Plain text, PASS/FAIL markers, cm and 0.1 deg precision, no
  number-led sentences in prose docs, marker side stays simple.

## Milestones

Order: SB0 -> SB2 -> SB1 -> V2-1 -> SB3 -> V3-1 -> V3-2 -> SB4 -> V2-2
-> V2-3 -> V2-4 -> V3-3 -> V3-4 -> V3-5 -> V3-6a -> (deferred: V2-5,
V3-6b, SB4 extension). P = may run alongside CPU or doc work; SERIAL =
exclusive GPU, device or editor.

### SB0 Staleness sweep and rule update (docs only). P. 2-3 h.

Goal: every status document says what is true on 2026-09-08 and the
project memory carries this plan's standing decisions.
- v3/README.md status block (Phase 4 item 1 done, S2 result, open
  queue); v3/SESSION_REVIEW.md new dated section (old kept).
- skill_set/v3-rtmpose-exploration-plan.md and
  skill_set/v2-r5-probe-state.md state lines corrected; new
  skill_set/exploration-round-2026-09.md (user decisions above, the
  autonomy rule extended to v2, the milestone order, the time_s join
  rule, the no-overlap rule) with one INDEX.md line.
- .agent/DECISIONS.md catch-up entry pointing at E-026..E-033 and M03
  (stale since 2026-08-26; still says 22 checks).
- v3/dataset/phase4_test_count.txt: pytest counts under base python and
  under v3rt (none recorded after S2).
- v3/dataset/phase3_v1_offset_table_20260908.txt: regenerated with the
  post-move v1 path, must equal the old numbers; old file stays.
- v3/dataset/phase4_d010_mean_vs_max.txt: grade.py with a
  --group-reduction mean option added to bench/metrics group error;
  closes the D-010 review (does MAX versus mean reorder S2 vs baseline).
Decision: D-023. Verify: both pytest suites; grade.py output for the
February manifest byte-identical to dataset/phase4_s2_vs_baseline.txt
under the default reduction.

### SB2 v3 extraction of both thesis recordings. GPU, SERIAL. 2 h.

Commands under v3rt: tools/extract_bag_to_csv.py on R6B and R5 ->
v3/output/extraction_<stem>.csv and .meta.json (meta gains
"color_format", additive); bench/v1_offset_table.py with --v1-csv
v1/mediapipe/output/<stem>_landmarks_raw.csv and --v3-csv for both;
bench/gate_weak_labels.py on the loop extraction (the recording with
real occlusion that D-017 asked for). Pin v3/dataset/phase5_extraction_
{r6b,r5}.txt, phase5_v1_offset_table_{r6b,r5}.txt,
phase5_gate_weak_labels_r5.txt, each with the frame-count and time_s
alignment line. Decision: D-024 (thesis recordings adopted as v3 base
recordings; time_s join rule; D-017 status from the loop result).

### SB1 v2 flags-off ALL PASS reproduced; probe re-run after E-027. SERIAL. 3 h.

Copy the current v2/output dumps aside (they are the R6B flags-on run,
also kept as *_r6b_full.csv). run_v2.py --source bag --dump with the
defaults, then validate_v2.py -> pin v2/dataset/m3_validate_output_
20260908.txt beside the 2026-08-06 original; zip the three dumps with a
SHA-256 manifest (pattern v2/dataset/m03_rail_manifest.json). Then
run_v2.py --source bag --probe-r5 --dump and validate_v2_r5.py
--report-json -> pin r5_probe_validation_20260908.txt; diff against
r5_probe_validation.txt (first probe since the third torso gate) and
state which counter the 255/19 and 255/125 figures are (wrist placed
from object per side versus CONSTRAINED tags including the IK elbow).
No code change; v2/reports/r5_realtime_probe.md gets a dated addendum.
Decision: .agent/DECISIONS.md; E-034 only if a pinned number is touched
(expected: none).

### V2-1 Marker-size fix and record-teardown hardening. P. 3 h.

- v2/calibration/live_calibrate.py: sizes from
  eval/common/marker_size.ASSUMED_BLACK_SQUARE_M through one
  MARKER_SIZES dict, --marker-size id=m override, meta records the
  source and the assumption (mirrors make_r5_calib.py:33,51-53; v2
  already imports eval modules, object_link.py:65-69).
- v2/broker/capture_broker.py: SIGTERM handled like SIGINT; log line
  after pipeline.stop() confirming the record closed.
- v2/integration/run_v2.py:196-201: with --record wait up to 120 s for
  the broker and never kill() it (the likely cause of the unindexed
  live_20260806.bag; stated as unverified).
- v2/tests/test_live_calibrate_sizes.py (new).
Rehearsal on the rail bag: run_v2.py --source bag --bag R6B --calibrate
--cube-size 0.07 --max-frames 300 with --compare against
eval/output/scene_calibration_r6bc.json -> pin
v2/dataset/m6a_calibration_rehearsal_45mm.txt (desk anchor within the
M4 envelope of dataset/m4_calibration_rehearsal.txt). Decision:
.agent/DECISIONS.md; the 45 mm stays the user's assumption until the
ruler measurement. Verify: python -m unittest discover -s v2/tests.

### SB3 Label basis for v3. P (CPU). 3-4 h. Depends on SB2.

- v3/core/fk.py: fk_arm_dirs and fk_wrist copy-adapted from
  eval/inspect/check_v1_overlay.py:47-66 and
  eval/failure/moving_window_check.py:54-60 on the vendored shoulder.py
  and root_frame.py; unit test against one pinned eval number.
- v3/replay/runner.py: run_csv(return_points=True), additive.
- v3/bench/label_compare.py (new): reads eval/labels/frames_<alias>/
  labels.json and meta.json read-only, the v3 extraction, joins on
  time_s; per labelled frame and side: raw RTMPose wrist error in cm
  and px, score, src; filtered wrist error; FK wrist of baseline_hold
  and s2_quat_prediction with bone lengths from
  eval/reports/<stem>_offset_fit.json read-only until V3-4's calibrator
  exists (D-018 caveat stated); failure and clean groups apart; stats as
  eval_labeled_recovery.py:62-69.
Output v3/output/label_compare_<alias>.csv; pin
v3/dataset/phase5_label_compare_{r6b,r5}.txt. Headline: on the 18 rail
failure frames where MediaPipe returned no wrist, does RTMPose return
one and how far from the label. Decision: D-025 (label-wrist metric;
COCO wrist versus BlazePose wrist definition stated).

### V3-1 V3Scene opened unattended. SERIAL (editor). 3 h.

The hand-built scene has never been opened; do this before any v3 live
work. Files: Unity/Assets/Editor/V3/V3PlayBootstrap.cs (flags
/tmp/v3_autoplay_*, ScenePath Assets/Scenes/V3Scene.unity) and
Unity/Assets/Scripts/V3/V3FrameDump.cs (flag /tmp/v3_capture_on, keyed on
V3PersonReceiver.lastFrameSeen at V3PersonReceiver.cs:86, Camera.main,
/tmp/v3_frames), both with pre-generated .meta files as D-013 did;
v3/tools/run_v3_unity_capture.py copy-adapted from
eval/unity_check/run_unity_capture.py (reuse unity_binary and
editor_pids by copy; -logFile; never touch /tmp/r5_* flags). Sender:
tools/psv3_demo_writer.py first, then replay/realtime.py --strategy
s2_quat_prediction --bag R6B. Pin v3/dataset/phase5_unity_v3scene.txt
(the "[V3Person] shared memory opened" line, frames seen, PNG count)
and a three-frame contact sheet (orange, amber, red). Decision: D-026
(closes the D-013 review). Needs: editor closed, DISPLAY.

### V3-2 Scenario manifests on the thesis recordings. P (CPU). 3 h.

bench/make_scenarios.py gains --anchors name=start and --alias naming
(default behaviour byte-identical; test_scenarios_schema unchanged).
v3/configs/scenarios_r6b.json and scenarios_r5.json: windows anchored
on the E-029 eligible windows (eval/reports/r6b_recovery_eligible.md,
r5_recovery_eligible_selection.json), shifted and logged where the v3
extraction has src != 0 inside a window; budgets derived per recording.
grade.py on both manifests for baseline_hold and s2_quat_prediction ->
pin phase5_grade_{r6b,r5}.txt. Decision: D-027 (placement rule; settles
D-019 for the thesis recordings; the user may overturn the placements).

### SB4 Cross-track comparison on the labelled frames. P. 3 h. Depends on SB1, SB3.

eval/failure/eval_labeled_crosstrack.py (new, additive): per recording
one table on the identical labelled frames: v1 offline columns read
from eval/reports/<alias>_recovery_labeled.json (never recomputed);
v2 live-probe replay FK wrist from the v2 person dump angles with the
raw shoulder of the frame (_ShoulderAt, eval_labeled_recovery.py:
211-218) and the offset-fit lengths, paired at the same frame and at
the validator's best lag (E-028 pairing rule); v3 columns from
v3/output/label_compare_<alias>.csv. Writes
eval/reports/<alias>_labeled_crosstrack.md and .json. Decision: E-034
(protocol: same labels, same stats, pairing rule, v3 exploratory).
Verify: the v1 columns equal the pinned report byte for byte.

### V2-2 Camera-alone round, documented (M6a). SERIAL (device). 2-3 h.

Nobody in frame. rs-enumerate-devices; capture_broker.py --source live
--max-frames 300 -> v2/dataset/m6a_broker_live.txt (negotiated profile,
USB3 check via assert_profile, fps, jitter); ring_viewer.py --snapshot
-> m6a_sensor_view.png; with the three markers placed: run_v2.py
--source live --calibrate --cube-size 0.07 --max-frames 300 --record
v2/output/live_<date>_calib.bag -> m6a_live_calibration.txt (static
stability, seed deviation, the --compare block against r6bc); re-open
the recorded bag to prove it is indexed and replay it with the live
calibration -> m6a_record_replay.txt. Start v2/reports/m6_camera_round.md;
V2.md status M6a. If the markers are not physically in place, do the
broker and viewer steps, log the calibration step BLOCKED, and leave
the checklist. Decision: .agent/DECISIONS.md.

### V2-3 Unity capture of the v2 probe stream, unattended. SERIAL (editor, shm). 3 h.

v2/integration/run_v2_unity_capture.py copy-adapted from
run_unity_capture.py: background run_v2.py --source bag with the E-026
flags, assert /dev/shm/integrated_scene is absent (E-027 caveat: both
receivers spawn otherwise), remove stale rt_* and integrated_scene_v2,
arm /tmp/r5_capture_on and /tmp/r5_autoplay_on, wait for PNG coverage
keyed on lastFrame, stop, quit, archive the receiver log. Runs: R6B
(--object-recovery --plausibility-gate --display-lpf) and R5
(--probe-r5). Evidence: eval/output/unity_check_v2_<alias>/ (gitignored)
and a four-frame contact sheet v2/dataset/m6b_unity_v2_<alias>.png
(rail frames 114, 505, 560, 700: amber bridge and blue constrained
spheres visible) with the frame-count line. This closes the "Unity
visual check of the probe stream" item open since 2026-08-26.

### V2-4 R6B and live-probe report. P. 2 h. Depends on SB1, V2-3.

v2/reports/r6b_realtime_probe.md (new): the E-026 numbers, the M03
corrected pairing, the azimuth-singularity reading of the two failing
checks, a fresh R6B run after E-027 (run_v2.py with the R6B calib and
flags, validate_v2_r5.py --alias r6b --one-handed --report-json; pin
r6b_probe_validation_20260908.txt; dumps archived with a manifest), the
twist-hold cost table pointer (E-027 addendum; user decision
unchanged), the contact sheet. v2/README.md status corrected (the
"ALL PASS on the 2026-08-26 dumps" claim replaced by SB1's evidence).

### V3-3 R-type label scenarios. P. 3 h. Depends on SB3, V3-2.

Manifests gain type-R entries: natural windows from
eval/reports/r6b_failure_events.csv (arm_R 550-639, 674-684) and the r5
equivalents (arm_L 1427-1668, arm_R 1775-1893, arm_L 1777-1798) with
truth only at the labelled frames. bench/grade.py gains a type-R branch
(continuity, teleport, honesty, and the label-wrist error from
label_compare; no e_occ). Pin phase5_grade_R_{r6b,r5}.txt. Decision:
D-028 (amendment to D-003 for R-type; S-type numbers unchanged;
regression: the February grade equals dataset/phase4_s2_vs_baseline.txt).

### V3-4 S6 object-conditioned strategy, replay only. P (CPU). 6-8 h.

- v3/vendor/v1/frames.py verbatim, MANIFEST.sha256 updated,
  test_vendor_integrity covers it.
- v3/core/bones.py: causal segment-length calibrator (config
  bones.calibrate_frames finally used).
- v3/core/ik.py: closed-form two-link elbow from occlusion_ext.py:
  344-365 with the 0.98 reach guard; synthetic unit tests.
- v3/replay/object_track.py: clean object CSV plus T_cam_desk from the
  calibration JSON -> per-frame camera-frame object pose, joined on
  time_s.
- v3/strategies/s6_object_conditioned.py: GripTracker copy-adapt
  (constants and their source lines from v2/common/object_link.py:
  74-83) wrapping S2; injected wrist and elbow reported ESTIMATED.
- v3/strategies/strategy_base.py: update(t, points, scores,
  context=None); v3/replay/runner.py: run_csv(..., object_track=None);
  v3/configs/default.json s6 block with every constant sourced.
Grade S6 versus S2 versus baseline on both manifests and the R-type
scenarios -> phase5_grade_s6_{r6b,r5}.txt. The question answered: where
does object conditioning beat pure prediction on identical inputs, and
does it lose on the free arm. Decisions: D-029 (design, constants),
D-030 (result). Verify: full pytest under both interpreters; the
February grade unchanged.

### V3-5 Open-constant sweeps and the detector under real occlusion. SERIAL for the GPU part. 3 h.

D-021: EMA alpha {0.3, 0.5, 0.7} x cap fraction {0.6, 0.8, 1.0} over
the three manifests (CPU) -> phase5_s2_sweep.txt. D-008/D-016 caveat:
bench/sweep_detector.py on the loop bag, YOLOX tiny versus m, det_freq
{5, 15, 30}, box-centre steps and person-found inside the failure
windows -> phase5_detector_sweep_r5.txt. Decisions: D-031, D-032.
Cheap follow-on if time allows: S3 chain-constrained partial IK from
V3-4's ik.py and bones.py, graded the same way. S5 stays blocked until
the D-017 path is decided from SB2's loop result (user item 5).

### V3-6a v3 live source, camera-alone smoke. SERIAL (device). 3 h.

v3/replay/live_source.py (copy-adapt of capture_broker.open_live and
assert_profile; query and record the colour format so live and bag
numbers stay comparable; close() stops the pipeline so a recording is
indexed); replay/realtime.py --source {bag,live} and --record. Smoke
with nobody in frame: person found 0, detect-stage latency measured,
PSV3 published -> phase5_live_smoke.txt. Decision: D-033.

### Deferred, need the subject (checklists ready, nothing else blocks)

- V2-5 Full live session (M6b), a separate session from the r7
  recording (the v2 broker and record_realsense_bag.py cannot share the
  device): V2.md steps 4 and 5 with the fixed
  calibrator; run_v2.py --source live --calibrate --record --dump with
  the probe flags; the rail task and the marker-cover test; replay the
  recorded bag through --source bag; a new validate_live_replay.py (live
  dumps versus replay dumps: coverage, per-frame angle and object
  differences, tag agreement); the pinned eval chain on the bag under a
  new alias in eval/common/paths.py (additive); extract_label_frames.py
  for its failure windows; the grip-tracker rest check from the dump.
  Evidence v2/dataset/m6b_*.txt, m6_camera_round.md, E-035.
- V3-6b: a 30 s S2 run into V3Scene with V3-1's capture, the bag
  recorded and re-extracted so the run is replayable ->
  phase5_live_session.txt.
- SB4 extension on the new recording once labelled.

## User-only items, in order

1. Subject in frame for V2-5 and V3-6b (the thesis-stated live session).
2. Confirm the wall, desk and cube markers are physically in place for
   V2-2, or place them; otherwise the calibration step is logged
   BLOCKED and the round covers the broker and viewer only.
3. Ruler measurement of the printed markers (E-009a); 45 mm remains an
   assumption until then.
4. Decision on D-017: manual gate labels on the loop recording (a
   tools/label_gate.py session of about 15 minutes) or none; unblocks S5.
5. Decision on the twist-hold threshold (E-027 addendum) for the live
   path.
6. Review of the V3-2 window placements and D-021's ESTIMATED-during-cap
   semantics from the logs.
7. Editor closed and DISPLAY available during V3-1 and V2-3.

## Risks, riskiest first

1. Contention corrupting timing evidence: v2 validators carry
   compute-budget checks and v3 pins latency; serialize every GPU-timed
   run and every editor capture.
2. Frame-index misalignment across extractors: every cross-track join
   is on time_s and prints the offset, or the label comparison silently
   compares neighbouring frames.
3. Unindexed recordings: V2-1's teardown hardening and V2-2's re-open
   check come before any recording that matters.
4. Marker size: a live calibration with the wrong size rescales the desk
   anchor by ten percent silently; only the ruler closes this.
5. V3Scene never opened: a malformed scene block surfaces on first open;
   V3-1 precedes any v3 live work.
6. The S6 interface change perturbing S2 and the baseline: guarded by
   regrading the February manifest byte-identical.
7. Thesis freeze: SB4 reads the pinned eval reports and writes only new
   files; run_recovery and detect_failures are never re-run on R5 or R6B.
8. The E-027 torso gate may change the R5 probe result in SB1; report
   as-is, the thesis already qualifies the loop numbers.
9. Colour-format mismatch between bags and a live stream: LiveSource
   queries and records the format.

## Verification

- v3: cd v3 and /home/luo/anaconda3/bin/python -m pytest -q; the full
  suite under /home/luo/anaconda3/envs/v3rt/bin/python with the five
  CUDA dirs on LD_LIBRARY_PATH; bench/grade.py on the February manifest
  byte-identical to dataset/phase4_s2_vs_baseline.txt after every
  interface change; every new number pinned in v3/dataset with the
  command that made it.
- v2: python -m unittest discover -s v2/tests; validate_v2.py 21 checks
  and validate_v2_r5.py 13 checks with their stdout pinned and the dumps
  archived with a SHA-256 manifest; unattended Unity captures verified
  by PNG coverage and the receiver log.
- eval: the pinned reports unchanged (git diff empty under eval/reports
  except new files); the cross-track table's v1 columns equal the pinned
  labelled report.
- Every milestone: Opus code review for meaningful code changes, tests
  and review in parallel, checkpoint report, HANDOVER.md, commit, push,
  pushed hash reported.

UPDATE 2026-09-09: the r7 hand-over take is recorded and accepted by the
thesis track (recording_20260909_000024, alias r7 registered in
eval/common/paths.py; chain outputs under eval/output/recovery_r7 and
eval/reports/r7_*; E-034/E-035). It is now available as the shared
replay basis this plan foresaw. Two things the exploration must know:
the wall card has shifted since 2026-08-31, so any new calibration of
this scene needs calibrate_scene.py --gravity-from
eval/output/scene_calibration_r6bc.json until the card is re-hung; and
the recovery layer has an opt-in hip hold (RobustChainSolver(hip_hold=
True), eval/reports/r7_hip_hold.md) that is NOT the thesis policy. The
thesis task still owns writing/ and the r7 reports.


# Task 2 report: provenance fact sheets for the nine Video/ bags (read-only research, 2026-09-23)

KEY FINDING: Seven stems have a role constant in eval/common/paths.py:15-28 (R5, R4, R4 backup, R1, R6a, R6b, R7). Two stems (20260225_230607, 20260328_021733) have none and are v1-era. .gitignore line 1 is `Video/`; a bare `!Video/README.md` negation will not work; the rule must become `Video/*` plus negations. No tracked code lists the contents of Video/. R7 has no v2 dump and no v2-specific calibration on disk. Only R6b has `*_r6b_full` v2 dumps.

ASSUMPTIONS-UNRESOLVED: R3 = 20260328_021733 is inferred, not stated. R2 = 20260225_230607 has no evidence at all. The scene of the R4 backup and of R6a is known only as "same session / take 1".

Counts are for tracked files: `git grep -l`. Untracked writing/v4..v7 hold further hits for R1, for example writing/v4/scripts/ch45_numbers.py:5.

What the codes mean: R1..R7 are the project's recording labels. eval/common/paths.py:33-35 gives them lowercase aliases ("r1","r4","r5","r6a","r6b","r7"), used in calibration filenames and report prefixes. R4 became the "PRIMARY evaluation recording" on 2026-08-25 (.agent/DECISIONS.md:533-537), and that rebase left the "R1/R2/R3" artifacts untouched (:537-539). R5 is the with-occlusion primary and R6B the without-occlusion primary (eval/README.md:3-15; skill_set/evaluation-scenario-separation.md:1-19; eval/DECISIONS.md:706-716). R7 is the handover-on-rail recording (eval/README.md:16-24). The thesis prose calls them "the rail recording", "the handover recording" and "the loop recording", and internal names never appear in prose (writing/v9/REVISION_2026-09-11_BRIEF.md:51-55).

All bags are 640x480 at 30 fps where stated. All calibration files listed below are gitignored and exist on local disk only: .gitignore:4 v1/aruco/output/, :24 v2/output/, :31 eval/output/.

--- 1 ---
Stem: recording_20260224_083945
Role: R1 (eval/common/paths.py:18 `R1_STEM = "recording_20260224_083945"`). It was the original v1 ACTIVE evaluation recording (thesis/00_notation.md:93-96). The eval track now uses it as the clean zero-fire reference: "Reference (zero-fire check): recording_20260224_083945." (eval/reports/r5_failure_mask.md:3, r6b_failure_mask.md:3, r7_failure_mask.md:3). Thresholds are set "plot-first from R1" (eval/DECISIONS.md:393).
Scene: the person stands at the desk and "carries the 70 mm cube (1.94 m of smoothed travel), parking it on the desk for t ~13.5-23 s. Camera at the desk edge" (thesis/00_notation.md:93-96). "object carried by the person, desk card flat, camera at the desk edge" (v1/ARUCO_MODEL.md:12-13). "one subject, cube with ArUco marker", 899 frames (v1/V1.md:49-50). "complex": yaw sweeps +-12 deg, both arms low and bent (v1/KINEMATIC_MODEL.md:473-474).
Status: good; kept. "KEEP Recording 1 as the regression-baseline / supplementary consistency dataset" (.agent/STATE.md:597-599). Superseded as primary by R4 (.agent/DECISIONS.md:533-537).
Calibration: v1/aruco/output/scene_calibration.json, whose line 2 source_csv is ..._20260224_083945_aruco_raw.csv. It is the default --calib of v2/integration/run_v2.py:58 and is built via thesis/B1_aruco_scene.md:304-305 (--cube-size 0.070).
Usage (tracked files 58): v1 29 (v1/V1.md:49, v1/KINEMATIC_MODEL.md:473, v1/realtime/person/realtime_person.py:167); v3 11 (v3/configs/default.json:4, v3/configs/scenarios_20260224.json:3); v2 5 (v2/integration/run_v2.py:57, v2/dataset/m1_ring_parity.txt:3); thesis 5 (thesis/00_notation.md:93, thesis/A1_acquisition_filtering.md:200, thesis/B1_aruco_scene.md:304); eval 4 (eval/common/paths.py:18, eval/reports/r5_failure_mask.md:3); .agent 2; skill_set 1; writing 1.
Pinned ranges: parked t ~13.5-23 s (thesis/00_notation.md:95); frames 0-1 lack left-arm landmarks (v1/KINEMATIC_MODEL.md:475-476).
Derived outputs: v1/aruco/output/recording_20260224_083945_{aruco_raw,object_world,object_world_filtered,object_world_filtered_clean}.* ; v1/mediapipe/output/recording_20260224_083945_landmarks_{raw,filtered}{,_v2}.* ; v1/aruco/dataset/recording_20260224_083945_* (committed copies); v1/kinematics/dataset/real_20260224/ ; v1/kinematics/output/{real_20260224_motion,unity_real_20260224}.mp4 ; v3/output/extraction_recording_20260224_083945.{csv,meta.json} ; eval/output/backup_20260825/realtime/ (R1 working dumps, per eval/reports/r4_stage6_ch7_rerun.md:8).
Defence relevance: MAYBE. It has a matching calibration and is run_v2.py's default bag (run_v2.py:57-58), which fits RECORDING_GUIDE.md:37. It is a one-person carry with no handover and no v2 dump retained under a named file.
Proposed alias: R1_desk_cube_carry_20260224_083945.bag
Uncertainties: none material.

--- 2 ---
Stem: recording_20260225_230607
Role: no role constant; v1-era (absent from eval/common/paths.py:15-28). R2 label UNCERTAIN: "R1/R2/R3" is mentioned (.agent/DECISIONS.md:537), but no file ties R2 to this stem.
Scene: "standing person, arms moving; used for the real-data kinematic validation (A2 s9)" (thesis/00_notation.md:100-101). "The person faces the camera throughout (yaw 180 +- 4.7 deg)" (v1/KINEMATIC_MODEL.md:459). 900/900 frames with pose (v1/KINEMATIC_MODEL.md:441-442).
Status: good; used for the kinematic validation only (thesis/A2_kinematic_model.md:397; .agent/FINDINGS.md:143-146).
Calibration: none found. The kinematic validation uses landmarks only.
Usage (tracked 5): thesis 2 (thesis/00_notation.md:100, thesis/A2_kinematic_model.md:397); v1 2 (v1/KINEMATIC_MODEL.md:441, v1/realtime/bench/shoulder_vec.py:179); .agent 1 (.agent/FINDINGS.md:143).
Pinned ranges: none found.
Derived outputs: v1/mediapipe/output/recording_20260225_230607_landmarks_{raw,filtered}.{csv,meta.json} ; v1/kinematics/dataset/real_20260225/ (raw and filtered CSVs) ; v1/kinematics/output/{real_20260225_motion,unity_real_20260225}.mp4.
Defence relevance: NO. There is no object or marker content and no calibration.
Proposed alias: v1era_standing_arms_moving_20260225_230607.bag
Uncertainties: the R2 label.

--- 3 ---
Stem: recording_20260328_021733
Role: no role constant; v1-era. It is probably the "R3" / "Recording 3" of the v1 thesis, but that is UNCERTAIN because it is inferred, not stated. Evidence: "R4 desk marker is on a ~32 deg tilted stand (like R3)" (.agent/FINDINGS.md:202), and this stem's stand is 31.8 deg (thesis/00_notation.md:97-98). Also, "scene_calibration_328.json ... Recording 3's means" (.agent/STATE.md:313-315).
Scene: "seated person, object untouched, camera high, desk marker on a 31.8 deg stand. Used for Pipeline B development and cross-validation" (thesis/00_notation.md:97-99; v1/ARUCO_MODEL.md:14-15). 899 frames, 30 s, 640x480 (.agent/STATE.md:269).
Status: good; a v1 development and cross-validation recording. It is the default stem of the v1 aruco tools (v1/aruco/validate_aruco.py:37, v1/aruco/calibrate_scene.py:91, v1/aruco/send_scene_poses.py:77).
Calibration: v1/aruco/output/scene_calibration_328.json, whose line 2 source_csv is ..._20260328_021733_aruco_raw.csv. The cube size was auto-calibrated on this recording (v1/ARUCO_MODEL.md:123).
Usage (tracked 18): v1 14 (v1/mediapipe/README.md:27, v1/ARUCO_MODEL.md:14, v1/aruco/calibrate_scene.py:20); .agent 3 (.agent/STATE.md:269, .agent/FINDINGS.md:161,177); thesis 1 (thesis/00_notation.md:97).
Pinned ranges: none found.
Derived outputs: v1/aruco/output/recording_20260328_021733_{aruco_raw,object_world,object_world_filtered}.* ; v1/mediapipe/output/recording_20260328_021733_landmarks_{raw,filtered}.* and _skeleton_{raw,filtered}.mp4 ; v1/aruco/dataset/recording_20260328_021733_* (committed).
Defence relevance: NO. The object is never handled.
Proposed alias: v1era_seated_cube_untouched_20260328_021733.bag
Uncertainties: the R3 label.

--- 4 ---
Stem: recording_20260825_070032
Role: R4 backup (eval/common/paths.py:17 `R4_BACKUP_STEM = "recording_20260825_070032"`).
Scene: UNCERTAIN. The only text is "Backup take recording_20260825_070032 (same session, also healthy) copied to Video/ alongside R4" (.agent/DECISIONS.md:541-543). It is presumably the same four-phase scenario as R4, but no file says so.
Status: backup take, unused ("also healthy", .agent/DECISIONS.md:542).
Calibration: none found.
Usage (tracked 2): eval 1 (eval/common/paths.py:17); .agent 1 (.agent/DECISIONS.md:542).
Pinned ranges: none. Derived outputs: none found (find by stem: no hits outside Video/).
Defence relevance: NO. There is no calibration and no extraction.
Proposed alias: R4backup_desk_cube_path_20260825_070032.bag (UNCERTAIN scene words)
Uncertainties: the scene content.

--- 5 ---
Stem: recording_20260825_070152
Role: R4 (eval/common/paths.py:16 `R4_STEM = "recording_20260825_070152"`). It was the PRIMARY evaluation recording from 2026-08-25 (.agent/DECISIONS.md:533-537) and was superseded by R5: "the R4 artifacts (the previous primary recording) remain for reproducibility" (eval/README.md:27-28).
Scene: 50 s, 1499 frames, "person enters -> walks to desk -> moves cube along the labeled path -> steps back" (.agent/DECISIONS.md:534-537). "four-phase scenario: entry / approach / manipulation / retreat" (.agent/STATE.md:573-574). The desk marker is on a ~32 deg stand (.agent/FINDINGS.md:202).
Status: superseded, with partial failure. "R4 disposition: torso PASS, right hand PASS, LEFT hand FAIL (wrist coverage 55.4 percent, longest gap 8.8 s)" (eval/DECISIONS.md:342-343). The left-carry phase (approx 28-36 s) is out of scope (eval/DECISIONS.md:345-346).
Calibration: v1/aruco/output/scene_calibration_r4.json (line 2 source_csv is ..._070152_aruco_raw.csv); eval/output/scene_calibration_r4c.json (marker-size corrected, eval/common/paths.py:52-57); eval/output/scene_calibration_r4c_live.json (eval/common/make_live_calib.py:17).
Usage (tracked 19): eval 17 (eval/common/paths.py:16, eval/DECISIONS.md:61, eval/reports/r4_stage6_ch7_rerun.md:6); .agent 2 (.agent/DECISIONS.md:534, .agent/STATE.md:573).
Pinned ranges: left-carry approx 28-36 s out of scope (eval/DECISIONS.md:345); f951 left-elbow visibility loss (eval/DECISIONS.md:337-338); frame 1225 candidate running example (.agent/STATE.md:596-597).
Derived outputs: v1/aruco/output/recording_20260825_070152_{aruco_raw,object_world,object_world_filtered}.* ; v1/mediapipe/output/recording_20260825_070152_landmarks_{raw,filtered}.* ; eval/output/recording_20260825_070152_{aruco_raw_scaled,landmarks_fusion_display,landmarks_raw_vis0,scaled_object_world,scaled_object_world_filtered}.* ; eval/output/occlusion_r4/ ; eval/output/v2_dump_baseline_r4/ (v2 dumps; eval/reports/r4_stage6b_robust_live.md:23) ; eval/reports: 12 files named by stem and 16 prefixed r4_.
Defence relevance: MAYBE, weak. It has a calibration and a v2 dump baseline, but it is a superseded primary with a failed left hand.
Proposed alias: R4_desk_cube_labeled_path_20260825_070152.bag
Uncertainties: none material.

--- 6 ---
Stem: recording_20260825_222315
Role: R5 (eval/common/paths.py:15 `R5_STEM = "recording_20260825_222315"   # primary, occlusion scenario (user-selected 2026-08-26)`). It is the WITH-occlusion primary (eval/README.md:5-9) and the thesis's "loop recording" (writing/v9/REVISION_2026-09-11_BRIEF.md:54).
Scene: 70 s, 2099 frames (eval/README.md:5-6). "The cube traverses a designed 8-waypoint loop (desk moves, 31 cm lift, wire traverse, two handovers)" (README.md:48-50). Back 30 cm, left 45 cm "with a two-hand handover", forward 15, up 30 cm to a wire, along the wire "with a second handover" (eval/gt/detect_waypoints.py:4-8). It was recorded under the re-recording protocol of E-013 (eval/DECISIONS.md:348-354).
Status: good; primary for the occlusion scenario. The round was frozen on 2026-08-26 and unfrozen on 2026-08-28 for E-022 (skill_set/r5-experiment-state.md:1,11-12).
Calibration: eval/output/scene_calibration_r5c.json and v2/output/scene_calibration_r5_v2.json (both line 2 source_csv ..._222315_aruco_raw_scaled.csv). The v2 flag --probe-r5 selects bag and calibration (v2/integration/run_v2.py:93,99-101).
Usage (tracked 84): writing 34 (writing/v9/notes_revision_ch6_ch7_v9.md:160, writing/v9/REVISION_2026-09-14_BRIEF.md:165); eval 28 (eval/README.md:5, eval/gt/detect_waypoints.py:4, eval/gt/labeled_path_r5.json:317); presentation 15 (presentation/defense_2026/anim/axes_extract.py:11, presentation/defense_2026/SPEAKER_NOTES.md:467); v2 3 (v2/integration/run_v2.py:100, v2/dataset/r5_probe_baseline.txt:18, v2/reports/r5_realtime_probe.md:6); skill_set 3 (skill_set/evaluation-scenario-separation.md:8, skill_set/r5-experiment-state.md:11, skill_set/exploration-round-2026-09.md:70); root 1 (README.md:48).
Pinned ranges: VIDEO-2 "R5 stream frames 900-1649", 25 s (presentation/defense_2026/committee_materials/baseline_75_docs/MEDIA_PROVENANCE.md:30).
Derived outputs: v1/aruco/output/recording_20260825_222315_aruco_raw.* ; v1/mediapipe/output/recording_20260825_222315_landmarks_{raw,filtered}.* ; eval/output/recording_20260825_222315_{aruco_raw_scaled,landmarks_raw_vis0,scaled_object_world,scaled_object_world_filtered,scaled_object_world_filtered_clean}.* ; eval/output/{recovery_r5,recovery_r5_overlay,unity_check_r5,v1_check_r5,label_frames_r5}/ ; eval/labels/frames_r5/ ; eval/reports (9 named by stem, 28 prefixed r5_) ; presentation/defense_2026/unity_capture/r5/Fresh_Unity_R5_Model_Axes.mp4 ; presentation/defense_2026/media/provenance/axes_r5_rgb.json.
Defence relevance: YES (candidate). A matching v2 calibration exists and has already been run through v2 (v2/dataset/r5_probe_baseline.txt:9,18), which fits RECORDING_GUIDE.md:37. It has two-hand handovers and natural occlusion, which suit slide 36's "real hold/recovery event" (talk_content.json, page 36 recording_instructions). No `*_r5_full` v2 dump is on disk.
Proposed alias: R5_occlusion_waypoint_loop_20260825_222315.bag
Uncertainties: none material.

--- 7 ---
Stem: recording_20260831_065504
Role: R6a (eval/common/paths.py:22 `R6A_STEM = "recording_20260831_065504"`). It is take 1 of the no-occlusion rail session. It has no entry in the ALIAS dict (paths.py:34-35), although the prose alias "r6a" appears at eval/DECISIONS.md:717.
Scene: "Take 1 of the same session" as R6B, the raised-rail setup (eval/DECISIONS.md:712-717). The hand usage is not described.
Status: failed precondition, rejected. It "failed the A6 precondition on every landmark (pose on 661/900 frames) and is kept only as a rejected take" (eval/DECISIONS.md:717-719; skill_set/evaluation-scenario-separation.md:15-17).
Calibration: none found.
Usage (tracked 3): eval 2 (eval/common/paths.py:22, eval/DECISIONS.md:717); skill_set 1 (skill_set/evaluation-scenario-separation.md:15).
Pinned ranges: none.
Derived outputs: v1/mediapipe/output/recording_20260831_065504_landmarks_raw.{csv,meta.json} only.
Defence relevance: NO. The take is rejected and has no calibration.
Proposed alias: R6a_rail_slide_rejected_20260831_065504.bag (scene words rest on "same session", so mildly UNCERTAIN)
Uncertainties: whether the take's motion matches R6b's.

--- 8 ---
Stem: recording_20260831_065553
Role: R6b (eval/common/paths.py:23 `R6B_STEM = "recording_20260831_065553"`). It is the WITHOUT-occlusion primary (eval/README.md:10-15) and the thesis's "rail recording", "the primary recording of Chapter 2" (writing/v9/REVISION_2026-09-11_BRIEF.md:51-52).
Scene: 30 s, 900 frames. "a straight horizontal wooden rail raised above the desk; the cube is lifted from the desk onto the rail and slid to its far end" (eval/DECISIONS.md:712-716). One hand: "Offset fit: right hand only"; "the idle left arm" (eval/DECISIONS.md:724-726).
Status: good; primary. Pose 900/900, torso PASS, object marker 899/900 (eval/DECISIONS.md:721-722). One natural 3.0 s right-wrist gap at frames 550-639 (eval/DECISIONS.md:725).
Calibration: eval/output/scene_calibration_r6bc.json and v2/output/scene_calibration_r6b_v2.json (both line 2 source_csv ..._065553_aruco_raw_scaled.csv). It was run through v2 (v2/dataset/r6b_probe_baseline.txt:18,43; r6b_probe_baseline_off.txt:17,37).
Usage (tracked 203): writing 150 (writing/v9/CH7_TRAILS_IMPLEMENTATION.md:161, writing/v9/scripts/make_ch5_fig_frames.py:39, writing/v9/REVISION_2026-09-11_BRIEF.md:52); eval 27 (eval/README.md:10, eval/DECISIONS.md:712, eval/common/paths.py:23); presentation 19 (presentation/defense_2026/anim/causal_replay.py:44, presentation/defense_2026/media/provenance/recorded_context_source.json:3, presentation/defense_2026/committee_materials/baseline_75_docs/RECORDING_GUIDE.md:30); v2 4 (v2/dataset/r6b_probe_baseline.txt:43, v2/dataset/m03_rail_manifest.json:43); skill_set 2 (skill_set/evaluation-scenario-separation.md:10, skill_set/exploration-round-2026-09.md:69); root 1.
Pinned ranges: causal replay frames 269-898 (MEDIA_PROVENANCE.md:116, baseline_75_docs); frame journey 383-533 with a hold at 533 (baseline_75_docs/MEDIA_PROVENANCE.md:29,47); filter clips 450-549, 650-749 and 25-179 (same file :20-22,28,31); thesis Figure 5.6 frames 549 and 560 (writing/v9/scripts/make_ch5_fig_frames.py:36-39); natural gap 550-639 (eval/DECISIONS.md:725).
Derived outputs: v1/aruco/output/recording_20260831_065553_aruco_raw.* ; v1/mediapipe/output/recording_20260831_065553_landmarks_{raw,filtered}.* ; eval/output/recording_20260831_065553_{aruco_raw_scaled,scaled_object_world,..._filtered,..._filtered_clean}.* ; eval/output/{recovery_r6b,unity_check_r6b,unity_check_r6b_trails,unity_check_r6b_v9,label_frames_r6b}/ ; eval/labels/frames_r6b/ ; v2/output/v2_{person,object,integrate}_dump_r6b_full.csv ; eval/reports (4 named by stem, 24 prefixed r6b_) ; presentation/defense_2026/media/matched/r6b_frame_533.jpg ; presentation/defense_2026/media/provenance/{v2_person_dump_r6b_full.csv,v2_integrate_dump_r6b_full.csv,filter_demo_raw_r6b.csv,filter_demo_saved_parameters_r6b.json} ; writing/v9/figures/src/r6b_frame00549.png, r6b_frame00560.png.
Defence relevance: YES, the strongest candidate. It is the only bag with both a matching v2 calibration and full v2 dumps on disk, and the defence already uses it for the frame-flow and causal-replay material. Its limit is one-hand content only.
Proposed alias: R6b_rail_slide_one_hand_20260831_065553.bag
Uncertainties: none material.

--- 9 ---
Stem: recording_20260909_000024
Role: R7 (eval/common/paths.py:28 `R7_STEM = "recording_20260909_000024"`, comment :24-27). It is the "handover recording" (writing/v9/REVISION_2026-09-11_BRIEF.md:53).
Scene: 50 s, 1499 frames. "the right hand slides the cube to about 30 cm along the rail, the left hand takes it over and slides it to the far end" (eval/README.md:16-19). The handover runs from frame 864 to frame 1022, 5.27 s (eval/reports/r7_handover.md:13).
Status: good; accepted. "RECORDED AND ACCEPTED ... named the last one ... as the one to use" (eval/RECORDING_R7_HANDOVER.md:3-8). "the seven earlier takes of that night are not used" (eval/DECISIONS.md:1066). Deviation: the wall card had shifted, so gravity is carried from R6b (eval/RECORDING_R7_HANDOVER.md:9-11).
Calibration: eval/output/scene_calibration_r7c.json (line 2 source_csv ..._000024_aruco_raw_scaled.csv; gravity via --gravity-from, E-034). There is NO v2-specific calibration and NO v2 dump for R7 on disk (ls v2/output; find *v2*dump*).
Usage (tracked 123): writing 57 (writing/v9/audit_evidence/figure_3_4_video/source.json:5, writing/v9/FIGURE_REPLACEMENTS_2026-09-13.md:16, writing/v8/PROF_COMMENTS_CHECKLIST.md:51); presentation 40 (presentation/defense_2026/talk_content.json:265, presentation/defense_2026/media/provenance/matched_evidence.json:5, presentation/defense_2026/DEMONSTRATION_MANIFEST.json:184); eval 21 (eval/README.md:16, eval/DECISIONS.md:1066, eval/RECORDING_R7_HANDOVER.md:7); skill_set 3 (skill_set/evaluation-scenario-separation.md:124, skill_set/exploration-round-2026-09.md:509); root 2 (README.md:53).
Pinned ranges: VIDEO-1 frames 600-1259 (presentation/defense_2026/review/MEDIA_AUDIT.md:57; baseline_75_docs/MEDIA_PROVENANCE.md:19); grasp and elbow 600-740 with holds at 705 and 740 (same file :24,26,43); grip context 600-779 (:23); pages 13-20 use frames 100-249 (presentation/defense_2026/MEDIA_PROVENANCE.md:9); slide 426-1498 (eval/reports/r7_handover.md:12); thesis Figure 3.4 frame 1400 at t=46.699725 s (writing/v9/audit_evidence/figure_3_4_video/source.json:5-7).
Derived outputs: v1/aruco/output/recording_20260909_000024_aruco_raw.* ; v1/mediapipe/output/recording_20260909_000024_landmarks_{raw,filtered}.* ; eval/output/recording_20260909_000024_{aruco_raw_scaled,scaled_object_world,..._filtered,..._filtered_clean}.* ; eval/output/{recovery_r7,unity_check_r7}/ ; eval/reports (4 named by stem, 17 prefixed r7_, plus unity_check_r7/) ; presentation/v9/videos/HANDOVER_UNITY_R7.mp4, embed/HANDOVER_UNITY_R7_15s.mp4, posters/handover_unity_r7.png ; presentation/defense_2026/unity_capture/r7/Fresh_Unity_R7_Model_Axes.mp4 ; presentation/defense_2026/media/matched/torso_r7_f00100.png ; presentation/defense_2026/media/provenance/axes_r7_{rgb,extraction}.json ; writing/v9/figures/ch7_*_r7.png and figures/src/r7_frame*.png.
Defence relevance: MAYBE. It has two-hand handover content and an eval calibration, but it has never been run through v2 and has no v2 dump. The guide requires "its matching calibration" (RECORDING_GUIDE.md:37), and r7c carries borrowed gravity (E-034). A first v2 run would be needed.
Proposed alias: R7_rail_handover_two_hand_20260909_000024.bag
Uncertainties: whether r7c.json is accepted as a v2 --calib; it is untested.

--- Once ---
.gitignore line 1, exact: `Video/`
`git check-ignore -v` result: `.gitignore:1:Video/	Video/README.md` and `.gitignore:1:Video/	Video/aliases/x.bag`. Both are ignored. The v1/Video symlink points to ../Video (ls -la v1/Video). The bags have a hard-link count of 2 (ls -la Video/), consistent with copies in ~/Desktop/ENSC498/recordings/ (skill_set/evaluation-scenario-separation.md:17-18; not independently verified).
Folder enumeration: none found. `git grep` for glob, listdir, iterdir, os.walk, scandir, rglob, Directory.GetFiles and EnumerateFiles in *.py, *.sh and *.cs found no match that combines these with Video. The only glob hits are presentation/v9/anim/video1_overlay.py:302,360 (frame_dir.glob("*.png"), not Video/). There are no "*.bag" or "Video/*" patterns in code. Every consumer builds explicit paths (eval/common/paths.py:30-32,64-65 `VIDEO / f"{stem}.bag"`; run_v2.py:57,100). A Video/aliases/ subfolder is therefore safe for code. Symlink aliases are safe for code, but the defence and writing provenance files record hashes and canonical paths (for example matched_evidence.json:5-9), so aliases must not replace the original names.

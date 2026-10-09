# Research report: provenance of the 34 bags in /home/luo/Desktop/ENSC498/recordings (read-only, 2026-09-23)

KEY FINDING: The 34 files fall into 13 sessions. 27 of them have no reference anywhere in the thesis repository: no tracked file, no untracked text file and no commit in its history. Only the seven known stems (R1, R4 backup, R4, R5, R6a, R6b, R7) are referenced there. On the ENSC498 side, 11 more files are referenced by scripts or by the `bag_file` field of tracking_data JSONs. 16 files have no reference in either repository:
- 13 earlier takes of the R4, R5 and R7 sessions.
- 3 January files: 20260121_180042, aruco_full_circle and 20260131_184322.

The R7 handover document confirms "eight takes" that night (eval/RECORDING_R7_HANDOVER.md:3-4). That matches exactly the eight 20260908_2354xx..20260909_000024 files. No text records what went wrong with any of the seven rejected takes.

VERIFIED:
- Every ENSC498 reference below comes from a grep of the working tree or a `git grep` on a named commit.
- The thesis-repo zero counts come from `git grep -l` on tracked files, `grep -r` on untracked text, and `git log --all -G` over the whole history.
- Each bag's duration and stream profile was measured by opening it read-only with pyrealsense2 playback (MEASURED). Every non-empty readable bag is a D435 with serial 215322078503, recording depth and colour at 640x480, 30 fps.
- 5 bags could not be read:
  - 3 are 27 KB with duration 0.0 and no sensors: 20260131_184322, 20260825_065736, 20260825_065900.
  - 3 report "Bag unindexed": 20260825_070016, 20260908_235818, 20260908_235947.

ASSUMPTIONS-UNRESOLVED:
- Why the earlier takes of R4, R5 and R7 were not used is never stated anywhere.
- Explanations for the empty and unindexed files are inferred from how the recorder scripts behave (see the recorder section). No text confirms them.
- The content of 20260121_180042, aruco_full_circle and Aruco_Only rests only on the filename or a commit message.
- ENSC498 labels 20260328_021733 "Right arm" and 20260328_021821 "Left arm". The thesis repo describes 021733 as "seated person, object untouched". These two sources do not agree.

---
SESSION GROUPING (by date/time and cited evidence)

S1 ENSC498_aruco_only (2025-12-15): Aruco_Only.
 - It is the bag named in e2debdb:run_pose_playback_class.py:33 (commit 2025-12-15, "aruco marker tracking but cannot track the pose at the same time").
S2 ENSC498_jan21 (2026-01-21 18:00): recording_20260121_180042. No reference anywhere.
S3 ENSC498_apriltag_and_arm_test (2026-01-22): recording_20260122_153720, recording_20260122_154958, arm_test.
 - The AprilTag "Set1"/"Set2" pair appears at 0798566:send_marker_to_unity.py:16-22, commit 2026-01-22 "Apriltag tracker along with testers".
 - arm_test has the same file date (ls mtime Jan 22).
S4 ENSC498_aruco_eval (2026-01-31): aruco_full_circle, recording_20260131_184322.
 - Same day as ENSC498/Aruco_Evaluation/recording_20260131_202911.bag, which ENSC498/Aruco_Evaluation/test.py:6 and arucoTmatrix.py:12 use. The session link is by date only (UNCERTAIN).
S5 ENSC498_arm_test (2026-02-11): right_arm_test, right_elbow, right_shoulder.
 - Their JSONs were committed together in 843816e (2026-02-16, "test elbow rotation"); see `git show 843816e --stat`.
S6 R1 session (2026-02-24 08:29-08:39): recording_20260224_082950, recording_20260224_083018, recording_20260224_083945.
 - ENSC498 commits 527fa9f "real scene data test" and 3c9ddab "elbow data in real scene" are both dated 2026-02-24.
S7 v1era_whole_body (2026-03-17): recording_20260317_200217. ENSC498 labels it "# Whole body" (d146583:run_offline_processing.py:17-18).
S8 v1era_arm_pair (2026-03-28 02:17-02:18): recording_20260328_021821.
 - Its neighbour 021733 is labelled "# # Right arm" and 021821 "# # Left arm" (d146583:run_offline_processing.py:20-24).
 - 021733 itself is not in ENSC498/recordings.
S9 R4 session (2026-08-25 06:57-07:02): 065736, 065900, 065917, 070016, 070032, 070152.
 - "The newest 50 s bag recording_20260825_070152 becomes the PRIMARY evaluation recording" (.agent/DECISIONS.md:533-535).
 - "Backup take recording_20260825_070032 (same session, also healthy)" (.agent/DECISIONS.md:541-543).
S10 R5 session (2026-08-25 22:20-22:24): 222024, 222149, 222315.
 - These were recorded under the E-013 re-recording protocol: "re-record until it does" (eval/DECISIONS.md:348-355).
 - "R5_STEM = recording_20260825_222315 # primary, occlusion scenario (user-selected 2026-08-26)" (eval/common/paths.py:15).
S11 R6 rail session (2026-08-31 06:55-06:56): 065504 (r6a), 065553 (r6b) (eval/DECISIONS.md:710-719).
S12 R7 handover night (2026-09-08/09 23:54-00:01): the eight files 235402 through 20260909_000024.
 - "The user recorded eight takes on the night of 2026-09-08/09 ... named the last one, recording_20260909_000024" (eval/RECORDING_R7_HANDOVER.md:3-7).
 - "the seven earlier takes of that night are not used, user direction" (eval/DECISIONS.md:1066; eval/common/paths.py:26-27; skill_set/evaluation-scenario-separation.md:125).

---
PER-FILE FACT BLOCKS
"Thesis refs" means the number of tracked files found by `git grep -l`. A count of 0 also means 0 untracked text hits and 0 hits in history (`git log --all -G`).

1. Original: Aruco_Only.bag
 Session: S1. Content: marker-only recording, going by the name (UNCERTAIN); 40.0 s (MEASURED).
 Status: test. Used by the pose-playback prototype: e2debdb:run_pose_playback_class.py:33 `BAG_FILE = "recordings/Aruco_Only.bag"`. Gone from that script from 5a93b16 (2026-01-01); the current file points at other bags (run_pose_playback_class.py:33-34).
 ENSC498 refs: history only (e2debdb, 5a93b16^). Thesis refs: 0.
 Uncertainty: the scene rests on the name alone.

2. Original: recording_20260121_180042.bag
 Session: S2. Content: UNCERTAIN; 35.0 s (MEASURED). Status: unknown.
 ENSC498 refs: none, in the working tree or in history. Thesis refs: 0.
 Uncertainty: content fully unknown.

3. Original: recording_20260122_153720.bag
 Session: S3. Content: AprilTag test "Set1", 15.0 s (MEASURED).
 - 0798566:send_marker_to_unity.py:16-18: `# Set1`, INPUT_FILE tracking_data_apriltag.json, BAG_FILE this bag.
 - tracking_data_apriltag.json:2-6 gives mode APRILTAG, wall tag id 0, object tag id 1.
 Status: test, used.
 ENSC498 refs: tracking_data_apriltag.json (it has no bag_file field; the pairing comes from the Set1 lines); history 0798566, 2aa7f9e^:send_marker_to_unity.py:19. Thesis refs: 0.

4. Original: recording_20260122_154958.bag
 Session: S3. Content: AprilTag test "Set2", 15.0 s (MEASURED).
 - 0798566:send_marker_to_unity.py:20-22 pairs it with tracking_data_apriltag_1.json.
 - The current ENSC498/test_markers.py:9 uses it (TRACKING_MODE "APRILTAG", :12).
 - b56e6f0:run_marker_processing.py:11-14 wrote tracking_data_apriltag_1.json from it.
 Status: test, used. ENSC498 refs: test_markers.py:9, tracking_data_apriltag_1.json. Thesis refs: 0.

5. Original: arm_test.bag
 Session: S3 (file date Jan 22). Content: first arm pose test, 30.0 s (MEASURED); MediaPipe heavy model on landmarks 11-14 onward (tracking_data_pose.json:3-9).
 Status: test, used.
 ENSC498 refs: tracking_data_pose.json:3; history 2a2a9d5:run_offline_processing.py:25 and send_to_unity.py:19 (2026-02-09, "pose smooth: one euro filter"). Thesis refs: 0.

6. Original: aruco_full_circle.bag
 Session: S4 (UNCERTAIN, same day as the Aruco_Evaluation bags). Content: by name, an ArUco marker taken around a full circle (UNCERTAIN); 50.0 s (MEASURED).
 Status: unknown. ENSC498 refs: none, in the working tree or history. Thesis refs: 0.
 Uncertainty: scene from the name only.

7. Original: recording_20260131_184322.bag
 Session: S4. Content: empty (27 076 bytes, duration 0.0, no sensors; MEASURED). Status: empty take (inferred cancel, see recorder section).
 ENSC498 refs: none. Thesis refs: 0.

8. Original: right_arm_test.bag
 Session: S5. Content: right-arm pose test, 30.0 s (MEASURED). Status: test, used.
 ENSC498 refs: tracking_data_right_arm.json:3 (added in 843816e, 2026-02-16); no script names it. Thesis refs: 0.

9. Original: right_elbow.bag
 Session: S5. Content: right-elbow test, 30.0 s (MEASURED). Status: test, used.
 ENSC498 refs: tracking_data_right_elbow.json:3; history 843816e:run_offline_processing.py:28-29 (output tracking_data_right_elbow.json), 843816e:send_to_unity.py:32, 9de262c^:send_to_unity.py:29. Thesis refs: 0.

10. Original: right_shoulder.bag
 Session: S5. Content: right-shoulder test, 30.0 s (MEASURED). Status: test, used.
 ENSC498 refs: tracking_data_right_shoulder.json:3; history 843816e:send_to_unity.py:29-30 (commented out), f14a86c^:send_to_unity.py:27. Thesis refs: 0.

11. Original: recording_20260224_082950.bag
 Session: S6 (R1 morning, 10 min before R1). Content: left-arm test, 15.0 s (MEASURED); input to run_offline_processing_left.py (94969fb:run_offline_processing_left.py:29, commit 2026-02-25 "starting test left shoulder"), which produced tracking_data_left_elbow.json.
 Status: earlier take, used in ENSC498 only. The current tracking_data_left_elbow.json:3 points at 20260225_230607 instead.
 ENSC498 refs: history only (94969fb, 9de262c^). Thesis refs: 0.
 Uncertainty: the scene is not described anywhere.

12. Original: recording_20260224_083018.bag
 Session: S6. Content: left-arm test, 15.0 s (MEASURED).
 - 9de262c:run_offline_processing_left.py:28-29 (output tracking_data_left_elbow.json) and 9de262c:send_to_unity.py:29; commit 2026-02-25 "left shoulder done".
 Status: earlier take, used in ENSC498 only. ENSC498 refs: history only (9de262c, 622fc60^). Thesis refs: 0.
 Uncertainty: scene not described.

13. Original: recording_20260224_083945.bag (Video/ R1; see task2_provenance.md sheet 1)
 Session: S6. Content, status and thesis refs (58 files): as in task2_provenance.md.
 ENSC498 additions:
 - tracking_data_right_elbow_real.json:3.
 - 527fa9f:run_offline_processing.py:28 (2026-02-24, "real scene data test").
 - 2aa7f9e^:run_offline_processing.py:20 and send_to_unity.py:20.

14. Original: recording_20260317_200217.bag
 Session: S7. Content: "# Whole body" (d146583:run_offline_processing.py:17-18; send_all_to_unity_replay.py:25-26); 40.0 s (MEASURED). It was also used for ArUco marker processing (run_marker_processing.py:24, commented out; tracking_data_markers_test_1.json:3).
 Status: v1-era test, heavily used in ENSC498.
 ENSC498 refs:
 - Scripts: demo_processing_and_plots.py:36, extract_mediapipe_landmarks.py:12, export_bag_to_mp4.py:10-11 (and recordings/recording_20260317_200217.mp4, named in send_all_to_replay_debug copy.py:15).
 - JSONs: tracking_data_demo.json:3, tracking_data_both_arms_test_rod.json:3, tracking_data_markers_test_1.json:3.
 Thesis refs: 0. File mtime 2026-04-14 (ls) matches ENSC498 commit d146583 of 2026-04-14.
 Uncertainty: "markers" rests on run_marker_processing.py:24 and the markers_test_1 JSON.

15. Original: recording_20260328_021821.bag
 Session: S8. Content: "# # Left arm" (d146583:run_offline_processing.py:23-24; send_all_to_unity_replay.py:31-32); 30.0 s (MEASURED). ArUco output in tracking_data_markers_test.json:3-9 (DICT_5X5_50, static ids 0 and 2).
 Status: v1-era test, used in ENSC498. ENSC498 refs: send_all_to_unity_replay.py:32 (commented out), tracking_data_markers_test.json:3. Thesis refs: 0.
 Uncertainty: this conflicts with how the thesis describes 021733 ("seated person, object untouched", thesis/00_notation.md:97-99), a minute earlier and labelled "Right arm" in ENSC498.

16. Original: recording_20260825_065736.bag
 Session: S9 (R4). Content: empty (27 076 bytes, 0.0 s; MEASURED). Status: empty take. ENSC498 refs: none. Thesis refs: 0.

17. Original: recording_20260825_065900.bag
 Session: S9. Content: empty (27 076 bytes, 0.0 s; MEASURED). Status: empty take. Refs: none, 0.

18. Original: recording_20260825_065917.bag
 Session: S9. Content: UNCERTAIN; 30.0 s (MEASURED), where R4 is 50 s. Status: earlier take, unused. The newest 50 s bag was chosen (.agent/DECISIONS.md:533-535). Refs: none, 0.
 Uncertainty: content unknown.

19. Original: recording_20260825_070016.bag
 Session: S9. Content: UNCERTAIN; 108 MB, "Bag unindexed" (MEASURED), so the recording was not finalized. Status: aborted take. Refs: none, 0.

20. Original: recording_20260825_070032.bag (Video/ R4 backup; task2_provenance.md sheet 4)
 Session: S9. Content: as in the earlier research (scene UNCERTAIN); 50.0 s (MEASURED). ENSC498 refs: none. Thesis refs: 2.

21. Original: recording_20260825_070152.bag (Video/ R4; task2_provenance.md sheet 5)
 Session: S9. Accepted as R4, later superseded by R5. ENSC498 refs: none. Thesis refs: 19.

22. Original: recording_20260825_222024.bag
 Session: S10 (R5). Content: UNCERTAIN; 70.0 s (MEASURED), the same length as R5, so presumably the same loop scenario.
 Status: earlier take, unused. There is no text on why; E-013 says "re-record until it does" (eval/DECISIONS.md:354-355). Refs: none, 0.

23. Original: recording_20260825_222149.bag
 Session: S10. Content: UNCERTAIN; 70.0 s (MEASURED). Status: earlier take, unused. Refs: none, 0.

24. Original: recording_20260825_222315.bag (Video/ R5; task2_provenance.md sheet 6)
 Session: S10. Accepted, "user-selected 2026-08-26" (eval/common/paths.py:15). Thesis refs: 84. ENSC498 refs: none.

25. Original: recording_20260831_065504.bag (Video/ R6a; task2_provenance.md sheet 7)
 Session: S11. Rejected take 1 (eval/DECISIONS.md:716-719). Thesis refs: 3. ENSC498 refs: none.

26. Original: recording_20260831_065553.bag (Video/ R6b; task2_provenance.md sheet 8)
 Session: S11. Accepted primary. Thesis refs: 203.
 ENSC498 additions:
 - run_offline_processing.py:19 (uncommitted working-tree change).
 - send_all_to_unity.py:36.
 - send_all_to_unity_replay.py:28-29, labelled "# Right arm".
 - tracking_data_both_arms_test.json:3.

27-33. The seven earlier R7-night takes (S12). For all seven:
 - Content: presumably attempts at the two-hand rail handover of eval/RECORDING_R7_HANDOVER.md:42-54 (UNCERTAIN).
 - Status: earlier take, not used (eval/DECISIONS.md:1066; eval/common/paths.py:26-27).
 - No per-take reason exists anywhere.
 - ENSC498 refs: none. Thesis refs: 0.
 27. recording_20260908_235402.bag: 30.0 s (MEASURED; shorter than the 50 s setting).
 28. recording_20260908_235500.bag: 50.0 s.
 29. recording_20260908_235605.bag: 50.0 s.
 30. recording_20260908_235712.bag: 50.0 s.
 31. recording_20260908_235818.bag: 268 MB, unindexed.
 32. recording_20260908_235840.bag: 50.0 s.
 33. recording_20260908_235947.bag: 669 MB, unindexed.
 The "rail_handover" scene words are UNCERTAIN for all seven.

34. Original: recording_20260909_000024.bag (Video/ R7; task2_provenance.md sheet 9)
 Session: S12. Accepted, the last of eight takes (eval/RECORDING_R7_HANDOVER.md:3-7). Thesis refs: 123. ENSC498 refs: none.

---
FILES WITH NO REFERENCE ANYWHERE (content UNCERTAIN) - 16 files
- recording_20260121_180042 and aruco_full_circle.
- The three empty 27 KB bags: 20260131_184322, 20260825_065736, 20260825_065900.
- 20260825_065917 and 20260825_070016.
- 20260825_222024 and 20260825_222149.
- The seven 20260908_2354xx..2359xx bags.
Aruco_Only, 082950, 083018, right_arm_test, right_elbow, right_shoulder, arm_test, 153720, 154958, 200217 and 021821 are referenced only in ENSC498, in its working tree or its history.

---
RECORDER SCRIPT FINDINGS (ENSC498)
- Naming: both recorders name the file from the start time, `datetime.now().strftime("%Y%m%d_%H%M%S")` then `recording_{timestamp}.bag`:
  - record_realsense_bag.py:36-38
  - record_realsense_bag_pose.py:140-141
  The timestamp is taken before the preview wait, so a stem marks when the script was launched, not when writing began (inferred from the order of the code).
- Stream configuration: depth z16 and colour bgr8, 640x480 at 30 fps (record_realsense_bag.py:23-24,56-57; record_realsense_bag_pose.py:18-19,147-148). The measured profiles of all readable bags match.
- Where they save: `OUTPUT_DIR = "recordings"`, relative to the directory the script runs from (record_realsense_bag.py:22; record_realsense_bag_pose.py:17). The thesis protocol then copies the bag to New_SandBox/Video/ (eval/RECORDING_R7_HANDOVER.md:69-72).
- Timing: the recorder is paused during a preview of WAIT_TIME, then resumed for RECORD_TIME (record_realsense_bag.py:68,116; record_realsense_bag_pose.py:169,180-186).
  - The working tree has WAIT_TIME 10 and RECORD_TIME 50 (record_realsense_bag.py:18-19; record_realsense_bag_pose.py:15-16).
  - The committed HEAD versions have RECORD_TIME 30.0, and WAIT_TIME 5.0 in record_realsense_bag.py (`git diff HEAD`). The change is uncommitted.
  - The measured 30 / 50 / 70 s durations suggest RECORD_TIME was edited from session to session (UNCERTAIN; no text records the 70 s setting used for R5).
- Empty and unindexed bags (inference, UNCERTAIN):
  - Pressing q during the paused preview returns before any frame is written (record_realsense_bag.py:109-111). This fits the 27 KB, 0 s files.
  - In the pose recorder, q during recording does `return` without `pipeline.stop()` (record_realsense_bag_pose.py:278-280). This fits the "Bag unindexed" files.
  - In record_realsense_bag.py, q during recording only `break`s (:157-159).
- Which recorder was used for R7 is inconsistent in the text:
  - eval/RECORDING_R7_HANDOVER.md:5 says record_realsense_bag_pose.py.
  - The protocol section of the same file (:58-64) says record_realsense_bag.py.
- Other ENSC498 notes:
  - ENSC498/.gitignore:2 ignores `recordings/`.
  - The `*.bag` rule on its last line is fused with the next entry as `*.bagAprilTag_Evaluation.7z`, so as written it does not ignore stray .bag files outside recordings/.
  - ENSC498/recordings also holds visualizer.py (6454 bytes, Dec 11 2025).

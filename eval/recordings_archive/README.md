Mirror of /home/luo/Desktop/ENSC498/recordings/README.md, copied 2026-09-23. The live copy is the one in the folder.

Location (2026-10-06, RA-001 in DECISIONS.md): the bank now lives inside the repository at recordings/ (/home/luo/Desktop/bimanual-tracking/recordings), git-ignored and never pushed. /home/luo/Desktop/ENSC498/recordings is a symlink to it, so every recorded path below and in index.json still resolves and stays as written.

# ENSC498 recordings archive

This folder holds the 34 Intel RealSense .bag recordings made with the D435 camera between December 2025 and September 2026: the ENSC498 course-project tests, the v1-era tests and every take of the thesis sessions R1, R4, R5, R6 and R7. On 2026-09-23 the files were given descriptive names of the form `<SESSION>_<scene words>_<status>_<original stem>.bag`; the old names and the rename actions are in RENAME_MAP.tsv, and the probe data (size, sha256, duration, frame counts, streams, device) are in index.json. The six unreadable bags are deleted (B-005); their size and sha256 stay in RENAME_MAP.tsv and in this README. The rename and the deletions were executed on 2026-09-23; the folder now holds 28 bags plus 3 legacy symlinks (B-004). The thesis repository's Video/ folder holds the canonical copies of the thesis recordings, seven of which also exist here as separate byte-identical files; Video/ is never touched by anything done in this folder.

Contact sheets: thumbnails/<new stem>_contact.png, where the new stem is the new name without .bag (6 or 12 tiles per readable bag). Sources quoted as file:line are in the thesis repository unless marked ENSC498; ensc_provenance.md and task2_provenance.md are the 2026-09-23 research sheets these citations were collected in, kept in the thesis repository at eval/recordings_archive/provenance/.

## Summary (capture order)

| new name | old name | session | date | duration s | frames | scene | status | referenced by |
|---|---|---|---|---|---|---|---|---|
| ENSC498_aruco_box_held_two_hands_test_Aruco_Only.bag | Aruco_Only.bag | ENSC498 | 2025-12-15 | 39.996 | 1200 | box marker held in hands | test | ENSC498 (history) |
| ENSC498_right_arm_raise_cube_untouched_test_20260121_180042.bag | recording_20260121_180042.bag | ENSC498 | 2026-01-21 | 34.993 | 1050 | right arm raise, cube idle | test | none |
| ENSC498_apriltag_set1_cube_push_test_20260122_153720.bag | recording_20260122_153720.bag | ENSC498 | 2026-01-22 | 14.978 | 450 | AprilTag Set1 cube push | test | ENSC498 |
| ENSC498_apriltag_set2_side_view_test_20260122_154958.bag | recording_20260122_154958.bag | ENSC498 | 2026-01-22 | 15.011 | 450 | AprilTag Set2 side view | test (legacy symlink) | ENSC498 |
| ENSC498_arms_outstretched_pose_test_arm_test.bag | arm_test.bag | ENSC498 | 2026-01-22 | 29.997 | 899 | arms outstretched pose test | test | ENSC498 |
| ENSC498_aruco_eval_unreadable_20260131_184322.bag | recording_20260131_184322.bag | ENSC498 | 2026-01-31 | - | - | empty stub (27076 bytes) | unreadable (DELETED, B-005) | none |
| ENSC498_aruco_cube_around_stick_test_aruco_full_circle.bag | aruco_full_circle.bag | ENSC498 | 2026-01-31 | 49.993 | 1499 | cube circled around stick | test | none |
| ENSC498_right_arm_landmark_test_right_arm_test.bag | right_arm_test.bag | ENSC498 | 2026-02-11 | 29.997 | 899 | right arm landmark test | test | ENSC498 |
| ENSC498_right_shoulder_arms_out_test_right_shoulder.bag | right_shoulder.bag | ENSC498 | 2026-02-11 | 29.998 | 899 | right shoulder, arms out | test | ENSC498 |
| ENSC498_right_elbow_bend_test_right_elbow.bag | right_elbow.bag | ENSC498 | 2026-02-11 | 29.998 | 899 | right elbow bend test | test | ENSC498 |
| R1_left_arm_raise_lower_test_20260224_082950.bag | recording_20260224_082950.bag | R1 | 2026-02-24 | 14.988 | 449 | left arm raise, cube idle | test | ENSC498 (history) |
| R1_left_arm_elbow_bend_test_20260224_083018.bag | recording_20260224_083018.bag | R1 | 2026-02-24 | 14.978 | 449 | left elbow bend, cube idle | test | ENSC498 (history) |
| R1_desk_cube_carry_accepted_20260224_083945.bag | recording_20260224_083945.bag | R1 | 2026-02-24 | 29.997 | 899 | desk cube carry | accepted | thesis, ENSC498 |
| v1era_whole_body_cube_handling_test_20260317_200217.bag | recording_20260317_200217.bag | v1era | 2026-03-17 | 40.03 | 1200 | whole body, cube handling | test (legacy symlink) | ENSC498 |
| v1era_left_arm_cube_untouched_test_20260328_021821.bag | recording_20260328_021821.bag | v1era | 2026-03-28 | 29.989 | 899 | left arm, cube untouched | test | ENSC498 |
| R4_desk_cube_labeled_path_unreadable_20260825_065736.bag | recording_20260825_065736.bag | R4 | 2026-08-25 | - | - | empty stub (27076 bytes) | unreadable (DELETED, B-005) | none |
| R4_desk_cube_labeled_path_unreadable_20260825_065900.bag | recording_20260825_065900.bag | R4 | 2026-08-25 | - | - | empty stub (27076 bytes) | unreadable (DELETED, B-005) | none |
| R4_desk_cube_labeled_path_earlier_take_20260825_065917.bag | recording_20260825_065917.bag | R4 | 2026-08-25 | 29.989 | 900 | desk cube labeled path | earlier_take | none |
| R4_desk_cube_labeled_path_unreadable_20260825_070016.bag | recording_20260825_070016.bag | R4 | 2026-08-25 | - | - | unindexed, not finalized | unreadable (DELETED, B-005) | none |
| R4_desk_cube_labeled_path_backup_20260825_070032.bag | recording_20260825_070032.bag | R4 | 2026-08-25 | 49.97 | 1499 | desk cube labeled path | backup | thesis |
| R4_desk_cube_labeled_path_accepted_20260825_070152.bag | recording_20260825_070152.bag | R4 | 2026-08-25 | 49.97 | 1499 | desk cube labeled path | accepted | thesis |
| R5_waypoint_loop_earlier_take_20260825_222024.bag | recording_20260825_222024.bag | R5 | 2026-08-25 | 69.973 | 2099 | waypoint loop attempt | earlier_take | none |
| R5_waypoint_loop_earlier_take_20260825_222149.bag | recording_20260825_222149.bag | R5 | 2026-08-25 | 69.982 | 2099 | waypoint loop attempt | earlier_take | none |
| R5_occlusion_waypoint_loop_primary_20260825_222315.bag | recording_20260825_222315.bag | R5 | 2026-08-25 | 69.982 | 2099 | occlusion waypoint loop | primary | thesis |
| R6_rail_cube_unmoved_rejected_20260831_065504.bag | recording_20260831_065504.bag | R6 | 2026-08-31 | 29.989 | 900 | rail, cube never moved | rejected | thesis |
| R6_rail_slide_one_hand_primary_20260831_065553.bag | recording_20260831_065553.bag | R6 | 2026-08-31 | 29.989 | 900 | rail slide, one hand | primary (legacy symlink) | thesis, ENSC498 |
| R7_rail_handover_earlier_take_20260908_235402.bag | recording_20260908_235402.bag | R7 | 2026-09-08 | 29.989 | 900 | rail handover attempt | earlier_take | none |
| R7_rail_handover_earlier_take_20260908_235500.bag | recording_20260908_235500.bag | R7 | 2026-09-08 | 49.97 | 1499 | rail handover attempt | earlier_take | none |
| R7_rail_handover_earlier_take_20260908_235605.bag | recording_20260908_235605.bag | R7 | 2026-09-08 | 49.97 | 1499 | rail handover attempt | earlier_take | none |
| R7_rail_handover_earlier_take_20260908_235712.bag | recording_20260908_235712.bag | R7 | 2026-09-08 | 49.97 | 1499 | rail handover attempt | earlier_take | none |
| R7_rail_handover_unreadable_20260908_235818.bag | recording_20260908_235818.bag | R7 | 2026-09-08 | - | - | unindexed, not finalized | unreadable (DELETED, B-005) | none |
| R7_rail_handover_earlier_take_20260908_235840.bag | recording_20260908_235840.bag | R7 | 2026-09-08 | 49.97 | 1499 | rail handover attempt | earlier_take | none |
| R7_rail_handover_unreadable_20260908_235947.bag | recording_20260908_235947.bag | R7 | 2026-09-08 | - | - | unindexed, not finalized | unreadable (DELETED, B-005) | none |
| R7_rail_handover_two_hand_accepted_20260909_000024.bag | recording_20260909_000024.bag | R7 | 2026-09-09 | 49.97 | 1499 | rail handover, two hands | accepted | thesis |

Date is the capture stamp in the original name, or the file modification date for hand-named bags (index.json fields capture_stamp_from_name, mtime_iso). Duration and frames are index.json duration_s and frame_count_color. 'thesis' means the stem is referenced in the thesis repository; 'ENSC498' means in the ENSC498 repository (working tree or history, see each detail block).

## Sessions

The research sheet speaks of 13 sessions (ensc_provenance.md:3) but lists twelve (ensc_provenance.md:26-51); the twelve listed are used here.

S1 - ENSC498, 2025-12-15, marker box. One bag, Aruco_Only.bag, named in the ENSC498 pose-playback prototype (e2debdb:run_pose_playback_class.py:33, commit 2025-12-15 "aruco marker tracking but cannot track the pose at the same time"; ensc_provenance.md:26-27). The tiles show a standing person holding a cardboard box with one large marker in both hands. Single take, used as a test.

S2 - ENSC498, 2026-01-21, arm raise. One bag, recording_20260121_180042, with no reference anywhere (ensc_provenance.md:28). The tiles show a standing person raising and lowering the right arm while a marker cube sits untouched on the desk.

S3 - ENSC498, 2026-01-22, AprilTag tests and first arm test. The AprilTag "Set1"/"Set2" pair, 153720 and 154958, appears at 0798566:send_marker_to_unity.py:16-22 (commit 2026-01-22 "Apriltag tracker along with testers"); arm_test shares the file date (ensc_provenance.md:29-31). Set1 is a front view and Set2 a side view of one hand pushing a tag cube; arm_test is a T-pose with no object. All three are tests, all used in ENSC498.

S4 - ENSC498, 2026-01-31, ArUco evaluation day. aruco_full_circle and the empty stub 184322, linked to the ENSC498 Aruco_Evaluation bags by date only (UNCERTAIN; ensc_provenance.md:32-33). aruco_full_circle shows a marker cube moved around a vertical stick; 184322 holds no frames and is deleted.

S5 - ENSC498, 2026-02-11, right-arm tests. right_arm_test, right_elbow and right_shoulder, whose JSONs were committed together in 843816e (2026-02-16, "test elbow rotation"; ensc_provenance.md:34-35). Same person and desk in all three; the cube is never touched.

S6 - R1, 2026-02-24 08:29-08:39. Two 15 s left-arm tests (082950, 083018) used by ENSC498's left-shoulder work, then R1 itself, 083945 (ensc_provenance.md:36-37; eval/common/paths.py:18). R1 is the accepted v1 recording and now the eval track's zero-fire reference (eval/reports/r5_failure_mask.md:3; task2_provenance.md:15). The two earlier bags show the same man with his left arm out and the cube untouched: they are separate tests, not attempts at R1.

S7 - v1era, 2026-03-17, whole body. One bag, 200217, labelled "# Whole body" in ENSC498 (d146583:run_offline_processing.py:17-18) and used heavily there (ensc_provenance.md:38,127-133). The tiles show a standing person handling the marker cube on the desk.

S8 - v1era, 2026-03-28, arm pair. 021821, labelled "# # Left arm" (d146583:run_offline_processing.py:23-24). Its neighbour 021733 ("# # Right arm") is not in this folder; the thesis holds it in Video/ (ensc_provenance.md:39-41; task2_provenance.md:39-50). The tiles of 021821 show a standing person moving the left arm, cube untouched.

S9 - R4, 2026-08-25 06:57-07:02. Six bags: two empty stubs (065736, 065900), a 30 s take (065917), an unindexed partial (070016), the backup (070032) and R4 (070152). "The newest 50 s bag recording_20260825_070152 becomes the PRIMARY evaluation recording" (.agent/DECISIONS.md:533-535); "Backup take recording_20260825_070032 (same session, also healthy)" (.agent/DECISIONS.md:541-543). The readable earlier take shows the same grey-jacket person moving the cube along the desk path under the wire rig.

S10 - R5, 2026-08-25 22:20-22:24. Three 70 s takes under the E-013 protocol, "re-record until it does" (eval/DECISIONS.md:348-355). "R5_STEM = recording_20260825_222315 # primary, occlusion scenario (user-selected 2026-08-26)" (eval/common/paths.py:15). In the tiles, 222024 shows the person leaving the lane from 44 s with the cube on the desk; 222149 shows a lift near the wire and a pass between hands.

S11 - R6 rail, 2026-08-31 06:55-06:56. Two takes on the raised wooden rail: R6a (065504, rejected, "failed the A6 precondition on every landmark (pose on 661/900 frames)") and R6b (065553, primary without occlusion) (eval/DECISIONS.md:710-719). In the tiles R6a shows the person walking in and standing with the cube never moved; R6b shows the right hand lifting the cube onto the rail and sliding it.

S12 - R7 handover night, 2026-09-08/09 23:54-00:01. "The user recorded eight takes on the night of 2026-09-08/09 ... named the last one, recording_20260909_000024" (eval/RECORDING_R7_HANDOVER.md:3-7); "the seven earlier takes of that night are not used" (eval/DECISIONS.md:1066). Of the seven earlier takes, two are unindexed partials (235818, 235947) and five are readable; all five readable ones show the same right-hand slide, two-hand handover and left-hand slide as R7 in their tiles. 235402 is 30 s, the others 50 s.

## Per-recording details

### ENSC498_aruco_box_held_two_hands_test_Aruco_Only.bag

- New name: ENSC498_aruco_box_held_two_hands_test_Aruco_Only.bag
- Old name: Aruco_Only.bag
- Session: ENSC498 (S1: ENSC498, 2025-12-15, marker box)
- Capture: 2025-12-15; 39.996 s; 1200 colour / 1200 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.16.0.1; sha256 c2aea9db23cd; full record in index.json.
- Tiles: 12 tiles. A standing man in a black Coca-Cola sweatshirt holds a cardboard box carrying one large marker in front of his chest and face with both hands for the whole 40 s, tilting and turning it. Office background; no desk scene, no cube, no rail or wire. (thumbnails/ENSC498_aruco_box_held_two_hands_test_Aruco_Only_contact.png)
- Content: No text describes the scene. The name suggests a marker-only recording (ensc_provenance.md:58, UNCERTAIN). The bag was used by the pose-playback prototype: `BAG_FILE = "recordings/Aruco_Only.bag"` (ENSC498 e2debdb:run_pose_playback_class.py:33; commit 2025-12-15 "aruco marker tracking but cannot track the pose at the same time", ensc_provenance.md:27).
- Status: test
- Referenced by: ENSC498: history only, e2debdb:run_pose_playback_class.py:33, removed from 5a93b16 (2026-01-01) (ensc_provenance.md:59-60). Thesis: none.
- Uncertainties: The name says marker only, but the tiles show a person holding the marker box; the scene words follow the tiles.

### ENSC498_right_arm_raise_cube_untouched_test_20260121_180042.bag

- New name: ENSC498_right_arm_raise_cube_untouched_test_20260121_180042.bag
- Old name: recording_20260121_180042.bag
- Session: ENSC498 (S2: ENSC498, 2026-01-21, arm raise)
- Capture: 2026-01-21; 34.993 s; 1050 colour / 1050 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.16.0.1; sha256 fe20810a831c; full record in index.json.
- Tiles: 12 tiles. A standing man in a yellow-green jacket and headphones repeatedly raises and lowers the arm on the image left (his right arm, if the image is unmirrored), from horizontal to above the shoulder; the other arm hangs. A marker cube sits on the desk untouched in every tile; two wall markers are visible; no rail or wire. (thumbnails/ENSC498_right_arm_raise_cube_untouched_test_20260121_180042_contact.png)
- Content: None. No reference in ENSC498 (working tree or history) or in the thesis repo (ensc_provenance.md:63-66).
- Status: test
- Referenced by: None found (ensc_provenance.md:65).
- Uncertainties: Content comes from the tiles only. Status 'test' is assigned from the content; the research records the status as unknown (ensc_provenance.md:64).

### ENSC498_apriltag_set1_cube_push_test_20260122_153720.bag

- New name: ENSC498_apriltag_set1_cube_push_test_20260122_153720.bag
- Old name: recording_20260122_153720.bag
- Session: ENSC498 (S3: ENSC498, 2026-01-22, AprilTag tests and first arm test)
- Capture: 2026-01-22; 14.978 s; 450 colour / 450 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.16.0.1; sha256 d514af73fd3a; full record in index.json.
- Tiles: 6 tiles. Front view with the face out of frame; a person in a dark hooded jacket stands behind the desk and pushes a tag cube along the desk with one hand (the image-right hand), the other hand in a pocket. Wall tags are visible behind; no rail or wire. (thumbnails/ENSC498_apriltag_set1_cube_push_test_20260122_153720_contact.png)
- Content: AprilTag test "Set1": `# Set1`, INPUT_FILE tracking_data_apriltag.json, BAG_FILE this bag (ENSC498 0798566:send_marker_to_unity.py:16-18). tracking_data_apriltag.json:2-6 gives mode APRILTAG, wall tag id 0, object tag id 1 (ensc_provenance.md:68-72).
- Status: test
- Referenced by: ENSC498: tracking_data_apriltag.json (paired through the Set1 lines); history 0798566:send_marker_to_unity.py:16-18, 2aa7f9e^:send_marker_to_unity.py:19 (ensc_provenance.md:73). Thesis: none.
- Uncertainties: None material.

### ENSC498_apriltag_set2_side_view_test_20260122_154958.bag

- New name: ENSC498_apriltag_set2_side_view_test_20260122_154958.bag
- Old name: recording_20260122_154958.bag
- Session: ENSC498 (S3: ENSC498, 2026-01-22, AprilTag tests and first arm test)
- Capture: 2026-01-22; 15.011 s; 450 colour / 450 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.16.0.1; sha256 493506352ec3; full record in index.json.
- Tiles: 6 tiles. Low side view along the desk; a person in a dark jacket leans in from the image left and slides a tag cube along the desk toward the camera with one hand. One wall tag is visible; the person is mostly out of frame. (thumbnails/ENSC498_apriltag_set2_side_view_test_20260122_154958_contact.png)
- Content: AprilTag test "Set2", paired with tracking_data_apriltag_1.json (ENSC498 0798566:send_marker_to_unity.py:20-22); b56e6f0:run_marker_processing.py:11-14 wrote tracking_data_apriltag_1.json from it (ensc_provenance.md:75-79).
- Status: test; legacy symlink recording_20260122_154958.bag -> ENSC498_apriltag_set2_side_view_test_20260122_154958.bag (B-004)
- Referenced by: ENSC498: test_markers.py:9 (TRACKING_MODE "APRILTAG", :12), tracking_data_apriltag_1.json (ensc_provenance.md:78,80). Legacy symlink kept for test_markers.py:9 (B-004). Thesis: none.
- Uncertainties: None material.

### ENSC498_arms_outstretched_pose_test_arm_test.bag

- New name: ENSC498_arms_outstretched_pose_test_arm_test.bag
- Old name: arm_test.bag
- Session: ENSC498 (S3: ENSC498, 2026-01-22, AprilTag tests and first arm test)
- Capture: 2026-01-22; 29.997 s; 899 colour / 899 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.16.0.1; sha256 5cb9e14cdc94; full record in index.json.
- Tiles: 6 tiles. A standing man in a dark jacket holds both arms straight out sideways (T pose) throughout, with small changes in arm height. No object is handled; wall markers are visible; desk in the foreground. (thumbnails/ENSC498_arms_outstretched_pose_test_arm_test_contact.png)
- Content: First arm pose test; MediaPipe heavy model on landmarks 11-14 onward (tracking_data_pose.json:3-9) (ensc_provenance.md:82-84).
- Status: test
- Referenced by: ENSC498: tracking_data_pose.json:3; history 2a2a9d5:run_offline_processing.py:25 and send_to_unity.py:19 (2026-02-09, "pose smooth: one euro filter") (ensc_provenance.md:85). Thesis: none.
- Uncertainties: Session S3 membership rests on the file date only (ensc_provenance.md:31).

### ENSC498_aruco_eval_unreadable_20260131_184322.bag

- New name: ENSC498_aruco_eval_unreadable_20260131_184322.bag
- Old name: recording_20260131_184322.bag
- Session: ENSC498 (S4: ENSC498, 2026-01-31, ArUco evaluation day)
- Capture: unreadable. Size 27076 bytes; sha256 ed6ef43102d60a0ee3df979a552de2ed401b8bbf6c733f1c215b41f381140fcb; capture stamp 2026-01-31T18:43:22. Probe error: `RuntimeError: No streams are selected!` (index.json).
- Tiles: none (the bag cannot be opened).
- Content: Empty: 27076 bytes, no sensors (ensc_provenance.md:92-93). Inferred cause: q pressed during the paused preview returns before any frame is written (record_realsense_bag.py:109-111; ensc_provenance.md:219-220, UNCERTAIN).
- Status: unreadable; deleted 2026-09-23 per B-005
- Referenced by: None (ensc_provenance.md:94).
- Uncertainties: The session link to the ArUco evaluation day is by date only (ensc_provenance.md:33).

### ENSC498_aruco_cube_around_stick_test_aruco_full_circle.bag

- New name: ENSC498_aruco_cube_around_stick_test_aruco_full_circle.bag
- Old name: aruco_full_circle.bag
- Session: ENSC498 (S4: ENSC498, 2026-01-31, ArUco evaluation day)
- Capture: 2026-01-31; 49.993 s; 1499 colour / 1499 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.16.0.1; sha256 f0d959d19657; full record in index.json.
- Tiles: 12 tiles. Close torso-only view (head out of frame), dark clothing. One hand holds a vertical wooden stick standing on the desk while the other hand moves a marker cube around the stick on a paper sheet, lifting it at about 36 s. A flat marker on the desk front and a wall marker are visible; no rail or wire. (thumbnails/ENSC498_aruco_cube_around_stick_test_aruco_full_circle_contact.png)
- Content: By name, an ArUco marker taken around a full circle (ensc_provenance.md:87-88, UNCERTAIN).
- Status: test
- Referenced by: None, in ENSC498 (working tree or history) or the thesis repo (ensc_provenance.md:89).
- Uncertainties: Session S4 membership is by date only (ensc_provenance.md:88). The tiles agree with the name: the cube is moved around the stick.

### ENSC498_right_arm_landmark_test_right_arm_test.bag

- New name: ENSC498_right_arm_landmark_test_right_arm_test.bag
- Old name: right_arm_test.bag
- Session: ENSC498 (S5: ENSC498, 2026-02-11, right-arm tests)
- Capture: 2026-02-11; 29.997 s; 899 colour / 899 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.16.0.1; sha256 332cb978bd75; full record in index.json.
- Tiles: 6 tiles. A man in a black "JUST DO IT" T-shirt, legs apart, head partly cut off at the top, holds both arms out and raised and waves them up and down; both arms move, not only the right. A marker cube, a loose wooden stick and a mouse lie on the desk untouched; a flat desk marker is visible. (thumbnails/ENSC498_right_arm_landmark_test_right_arm_test_contact.png)
- Content: Right-arm pose test (ensc_provenance.md:96-97).
- Status: test
- Referenced by: ENSC498: tracking_data_right_arm.json:3 (added in 843816e, 2026-02-16); no script names it (ensc_provenance.md:98). Thesis: none.
- Uncertainties: The filename says right arm; the tiles show both arms moving.

### ENSC498_right_shoulder_arms_out_test_right_shoulder.bag

- New name: ENSC498_right_shoulder_arms_out_test_right_shoulder.bag
- Old name: right_shoulder.bag
- Session: ENSC498 (S5: ENSC498, 2026-02-11, right-arm tests)
- Capture: 2026-02-11; 29.998 s; 899 colour / 899 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.16.0.1; sha256 27ffb9d2079b; full record in index.json.
- Tiles: 6 tiles. Same person, T-shirt and desk scene as right_arm_test; both arms are held out horizontally (T pose) in every tile, head cut off at the top. Objects on the desk are untouched. (thumbnails/ENSC498_right_shoulder_arms_out_test_right_shoulder_contact.png)
- Content: Right-shoulder test (ensc_provenance.md:104-105).
- Status: test
- Referenced by: ENSC498: tracking_data_right_shoulder.json:3; history 843816e:send_to_unity.py:29-30 (commented out), f14a86c^:send_to_unity.py:27 (ensc_provenance.md:106). Thesis: none.
- Uncertainties: None material.

### ENSC498_right_elbow_bend_test_right_elbow.bag

- New name: ENSC498_right_elbow_bend_test_right_elbow.bag
- Old name: right_elbow.bag
- Session: ENSC498 (S5: ENSC498, 2026-02-11, right-arm tests)
- Capture: 2026-02-11; 29.998 s; 899 colour / 899 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.16.0.1; sha256 5e3e29709a32; full record in index.json.
- Tiles: 6 tiles. The same man, now in a yellow-green jacket over the "JUST DO IT" T-shirt, standing with both arms out; the image-left arm (his right) bends at the elbow with the hand raised at 12, 24 and 30 s. The cube on the desk is untouched. (thumbnails/ENSC498_right_elbow_bend_test_right_elbow_contact.png)
- Content: Right-elbow test (ensc_provenance.md:100-101).
- Status: test
- Referenced by: ENSC498: tracking_data_right_elbow.json:3; history 843816e:run_offline_processing.py:28-29, 843816e:send_to_unity.py:32, 9de262c^:send_to_unity.py:29 (ensc_provenance.md:102). Thesis: none.
- Uncertainties: None material.

### R1_left_arm_raise_lower_test_20260224_082950.bag

- New name: R1_left_arm_raise_lower_test_20260224_082950.bag
- Old name: recording_20260224_082950.bag
- Session: R1 (S6: R1, 2026-02-24 08:29-08:39)
- Capture: 2026-02-24; 14.988 s; 449 colour / 449 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.16.0.1; sha256 ec86a0176292; full record in index.json.
- Tiles: 12 tiles. A standing man in a dark button shirt holds the image-right arm (his left) out horizontally, raises it above the shoulder at 9.5 s and lowers it toward the desk at 13.6 s; his right hand is in a pocket. The marker cube on the desk is untouched; a wall marker is visible. (thumbnails/R1_left_arm_raise_lower_test_20260224_082950_contact.png)
- Content: Left-arm test; input to run_offline_processing_left.py (ENSC498 94969fb:run_offline_processing_left.py:29, commit 2026-02-25 "starting test left shoulder"), which produced tracking_data_left_elbow.json (ensc_provenance.md:108-110).
- Status: test
- Referenced by: ENSC498: history only (94969fb, 9de262c^); the current tracking_data_left_elbow.json:3 points at 20260225_230607 instead (ensc_provenance.md:110-111). Thesis: none.
- Uncertainties: The research lists the status as an earlier take (ensc_provenance.md:110); the tiles show a separate left-arm test, not an attempt at the R1 cube carry, so the status here is 'test'.

### R1_left_arm_elbow_bend_test_20260224_083018.bag

- New name: R1_left_arm_elbow_bend_test_20260224_083018.bag
- Old name: recording_20260224_083018.bag
- Session: R1 (S6: R1, 2026-02-24 08:29-08:39)
- Capture: 2026-02-24; 14.978 s; 449 colour / 449 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.16.0.1; sha256 7cf2e67f5ec0; full record in index.json.
- Tiles: 12 tiles. Same man, clothing and scene as 082950; the left arm is held out, with the forearm raised (elbow bend) at 8.2 and 9.5 s. The cube on the desk is untouched. (thumbnails/R1_left_arm_elbow_bend_test_20260224_083018_contact.png)
- Content: Left-arm test (ENSC498 9de262c:run_offline_processing_left.py:28-29, output tracking_data_left_elbow.json; 9de262c:send_to_unity.py:29; commit 2026-02-25 "left shoulder done") (ensc_provenance.md:114-116).
- Status: test
- Referenced by: ENSC498: history only (9de262c, 622fc60^) (ensc_provenance.md:117). Thesis: none.
- Uncertainties: As for 082950: status 'test' instead of the research's 'earlier take', because the content is a separate left-arm test.

### R1_desk_cube_carry_accepted_20260224_083945.bag

- New name: R1_desk_cube_carry_accepted_20260224_083945.bag
- Old name: recording_20260224_083945.bag
- Session: R1 (S6: R1, 2026-02-24 08:29-08:39)
- Capture: 2026-02-24; 29.997 s; 899 colour / 899 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.16.0.1; sha256 5789a1b51b24; full record in index.json.
- Tiles: 6 tiles. Same dark shirt, head out of frame, standing at the desk. The cube is held between both hands, carried to the image-right side, set on the desk and pushed with the left hand (18-24 s), and held in both hands again at 30 s. A flat desk marker on the front edge and a wall marker are visible; no rail or wire. (thumbnails/R1_desk_cube_carry_accepted_20260224_083945_contact.png)
- Content: R1: `R1_STEM = "recording_20260224_083945"` (eval/common/paths.py:18). "carries the 70 mm cube (1.94 m of smoothed travel), parking it on the desk for t ~13.5-23 s. Camera at the desk edge" (thesis/00_notation.md:93-96). "object carried by the person, desk card flat, camera at the desk edge" (v1/ARUCO_MODEL.md:12-13). "KEEP Recording 1 as the regression-baseline / supplementary consistency dataset" (.agent/STATE.md:597-599). Superseded as primary by R4 (.agent/DECISIONS.md:533-537) (task2_provenance.md:13-24).
- Status: accepted
- Referenced by: Thesis: 58 tracked files, e.g. eval/common/paths.py:18, v2/integration/run_v2.py:57, thesis/00_notation.md:93 (task2_provenance.md:19). ENSC498: tracking_data_right_elbow_real.json:3; 527fa9f:run_offline_processing.py:28; 2aa7f9e^:run_offline_processing.py:20 and send_to_unity.py:20 (ensc_provenance.md:122-125). Canonical copy: thesis repo Video/.
- Uncertainties: None material.

### v1era_whole_body_cube_handling_test_20260317_200217.bag

- New name: v1era_whole_body_cube_handling_test_20260317_200217.bag
- Old name: recording_20260317_200217.bag
- Session: v1era (S7: v1era, 2026-03-17, whole body)
- Capture: 2026-03-17; 40.03 s; 1200 colour / 1200 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.17.0.10; sha256 86396b801bdf; full record in index.json.
- Tiles: 6 tiles. A standing person in a dark navy shirt, head out of frame, handles a marker cube over a gridded desk sheet: one hand sets it down, both hands hold it at 8 and 40 s, one hand holds it at 16, 24 and 32 s. A flat desk marker, a wall marker and a wooden stick on the desk are visible. Only the torso and arms are in frame. (thumbnails/v1era_whole_body_cube_handling_test_20260317_200217_contact.png)
- Content: "# Whole body" (ENSC498 d146583:run_offline_processing.py:17-18; send_all_to_unity_replay.py:25-26). Also used for ArUco marker processing (run_marker_processing.py:24, commented out; tracking_data_markers_test_1.json:3) (ensc_provenance.md:127-128).
- Status: test; legacy symlink recording_20260317_200217.bag -> v1era_whole_body_cube_handling_test_20260317_200217.bag (B-004)
- Referenced by: ENSC498 scripts: demo_processing_and_plots.py:36, extract_mediapipe_landmarks.py:12, export_bag_to_mp4.py:10-11; JSONs: tracking_data_demo.json:3, tracking_data_both_arms_test_rod.json:3, tracking_data_markers_test_1.json:3 (ensc_provenance.md:130-132). Legacy symlink kept for export_bag_to_mp4.py:10, extract_mediapipe_landmarks.py:12, demo_processing_and_plots.py:36 (B-004). Thesis: none.
- Uncertainties: The label "Whole body" does not match the framing: the tiles show the torso and arms only, handling the cube. The scene words keep the cited label and add what the tiles show.

### v1era_left_arm_cube_untouched_test_20260328_021821.bag

- New name: v1era_left_arm_cube_untouched_test_20260328_021821.bag
- Old name: recording_20260328_021821.bag
- Session: v1era (S8: v1era, 2026-03-28, arm pair)
- Capture: 2026-03-28; 29.989 s; 899 colour / 899 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.17.0.10; sha256 26c95e18332d; full record in index.json.
- Tiles: 12 tiles. A standing man in a black jacket holds the image-right arm (his left) out, lowers it (10.9 s) and raises the forearm vertically (27.3 s); the other arm hangs. The marker cube on the desk is untouched; a flat desk marker and a wall marker are visible. (thumbnails/v1era_left_arm_cube_untouched_test_20260328_021821_contact.png)
- Content: "# # Left arm" (ENSC498 d146583:run_offline_processing.py:23-24; send_all_to_unity_replay.py:31-32). ArUco output in tracking_data_markers_test.json:3-9 (DICT_5X5_50, static ids 0 and 2) (ensc_provenance.md:136-137).
- Status: test
- Referenced by: ENSC498: send_all_to_unity_replay.py:32 (commented out), tracking_data_markers_test.json:3 (ensc_provenance.md:138). Thesis: none.
- Uncertainties: Its neighbour recording_20260328_021733 (a minute earlier, not in this folder) is labelled "Right arm" in ENSC498 but described as "seated person, object untouched" in the thesis (thesis/00_notation.md:97-99; ensc_provenance.md:21,139). The tiles of 021821 show a standing person, consistent with its own "Left arm" label.

### R4_desk_cube_labeled_path_unreadable_20260825_065736.bag

- New name: R4_desk_cube_labeled_path_unreadable_20260825_065736.bag
- Old name: recording_20260825_065736.bag
- Session: R4 (S9: R4, 2026-08-25 06:57-07:02)
- Capture: unreadable. Size 27076 bytes; sha256 ed6ef43102d60a0ee3df979a552de2ed401b8bbf6c733f1c215b41f381140fcb; capture stamp 2026-08-25T06:57:36. Probe error: `RuntimeError: No streams are selected!` (index.json).
- Tiles: none (the bag cannot be opened).
- Content: Empty: 27076 bytes, 0.0 s (ensc_provenance.md:141-142). Inferred cause: q pressed during the paused preview (record_realsense_bag.py:109-111; ensc_provenance.md:219-220, UNCERTAIN).
- Status: unreadable; deleted 2026-09-23 per B-005
- Referenced by: None (ensc_provenance.md:142).
- Uncertainties: Scene words come from the session only; the file holds no frames.

### R4_desk_cube_labeled_path_unreadable_20260825_065900.bag

- New name: R4_desk_cube_labeled_path_unreadable_20260825_065900.bag
- Old name: recording_20260825_065900.bag
- Session: R4 (S9: R4, 2026-08-25 06:57-07:02)
- Capture: unreadable. Size 27076 bytes; sha256 ed6ef43102d60a0ee3df979a552de2ed401b8bbf6c733f1c215b41f381140fcb; capture stamp 2026-08-25T06:59:00. Probe error: `RuntimeError: No streams are selected!` (index.json).
- Tiles: none (the bag cannot be opened).
- Content: Empty: 27076 bytes, 0.0 s (ensc_provenance.md:144-145). Inferred cause as for 065736 (UNCERTAIN).
- Status: unreadable; deleted 2026-09-23 per B-005
- Referenced by: None (ensc_provenance.md:145).
- Uncertainties: Scene words come from the session only; the file holds no frames.

### R4_desk_cube_labeled_path_earlier_take_20260825_065917.bag

- New name: R4_desk_cube_labeled_path_earlier_take_20260825_065917.bag
- Old name: recording_20260825_065917.bag
- Session: R4 (S9: R4, 2026-08-25 06:57-07:02)
- Capture: 2026-08-25; 29.989 s; 900 colour / 900 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.17.0.10; sha256 22b9abb5755c; full record in index.json.
- Tiles: 12 tiles. A person in a grey jacket over the "JUST DO IT" T-shirt, head out of frame, stands at the desk. A horizontal wire runs between two thin posts with orange bases. The cube is pushed along the gridded sheet by one hand, then the other, and lifted toward the wire in the left hand at 27-30 s. Wall and desk markers are visible. (thumbnails/R4_desk_cube_labeled_path_earlier_take_20260825_065917_contact.png)
- Content: No text describes this take. The session's newest 50 s bag became R4: "The newest 50 s bag recording_20260825_070152 becomes the PRIMARY evaluation recording" (.agent/DECISIONS.md:533-535). This take is 30 s (ensc_provenance.md:147-148).
- Status: earlier_take
- Referenced by: None (ensc_provenance.md:148).
- Uncertainties: Why it was not used is not recorded. It is 30 s against 50 s for R4, so it may be cut short (UNCERTAIN).

### R4_desk_cube_labeled_path_unreadable_20260825_070016.bag

- New name: R4_desk_cube_labeled_path_unreadable_20260825_070016.bag
- Old name: recording_20260825_070016.bag
- Session: R4 (S9: R4, 2026-08-25 06:57-07:02)
- Capture: unreadable. Size 108457028 bytes; sha256 12fbfff28d5d532beae011a6bce9041bbde29523122507ffbb590e9a48b9268c; capture stamp 2026-08-25T07:00:16. Probe error: `RuntimeError: Failed to resolve request. Request to enable_device_from_file("/home/luo/Desktop/ENSC498/recordings/recording_20260825_070016.bag") was invalid, Reason: Failed to create ros reader: Bag unindexed` (index.json).
- Tiles: none (the bag cannot be opened).
- Content: 108 MB, "Bag unindexed", so the recording was not finalized (ensc_provenance.md:151-152). Inferred cause: q during recording in the pose recorder returns without pipeline.stop() (record_realsense_bag_pose.py:278-280; ensc_provenance.md:221, UNCERTAIN).
- Status: unreadable; deleted 2026-09-23 per B-005
- Referenced by: None (ensc_provenance.md:152).
- Uncertainties: Scene words come from the session only.

### R4_desk_cube_labeled_path_backup_20260825_070032.bag

- New name: R4_desk_cube_labeled_path_backup_20260825_070032.bag
- Old name: recording_20260825_070032.bag
- Session: R4 (S9: R4, 2026-08-25 06:57-07:02)
- Capture: 2026-08-25; 49.97 s; 1499 colour / 1499 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.17.0.10; sha256 f4742ce30f66; full record in index.json.
- Tiles: 6 tiles. Same clothing and wire rig as 065917. The cube is pushed along the desk, held up in the left hand at 30 s and in the right hand at 40 s; at 50 s the person has stepped back to the image left and the cube sits on the desk. (thumbnails/R4_desk_cube_labeled_path_backup_20260825_070032_contact.png)
- Content: `R4_BACKUP_STEM = "recording_20260825_070032"` (eval/common/paths.py:17). "Backup take recording_20260825_070032 (same session, also healthy) copied to Video/ alongside R4" (.agent/DECISIONS.md:541-543) (task2_provenance.md:52-62).
- Status: backup
- Referenced by: Thesis: 2 tracked files, eval/common/paths.py:17 and .agent/DECISIONS.md:542 (task2_provenance.md:58). ENSC498: none. Canonical copy: thesis repo Video/.
- Uncertainties: No text states its scene (task2_provenance.md:55); the tiles show the same desk-path task as R4.

### R4_desk_cube_labeled_path_accepted_20260825_070152.bag

- New name: R4_desk_cube_labeled_path_accepted_20260825_070152.bag
- Old name: recording_20260825_070152.bag
- Session: R4 (S9: R4, 2026-08-25 06:57-07:02)
- Capture: 2026-08-25; 49.97 s; 1499 colour / 1499 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.17.0.10; sha256 8e8df75edc38; full record in index.json.
- Tiles: 6 tiles. Frame 0 shows the scene nearly empty (a person at the image-left edge). The same person in the grey jacket then moves the cube along the desk, holds it up in the left hand (30 s) and the right hand (40 s) near the wire, and stands back at 50 s with the cube on the desk. (thumbnails/R4_desk_cube_labeled_path_accepted_20260825_070152_contact.png)
- Content: `R4_STEM = "recording_20260825_070152"` (eval/common/paths.py:16). "person enters -> walks to desk -> moves cube along the labeled path -> steps back" (.agent/DECISIONS.md:534-537). "four-phase scenario: entry / approach / manipulation / retreat" (.agent/STATE.md:573-574). Superseded by R5: "the R4 artifacts (the previous primary recording) remain for reproducibility" (eval/README.md:27-28). "R4 disposition: torso PASS, right hand PASS, LEFT hand FAIL" (eval/DECISIONS.md:342-343) (task2_provenance.md:64-75).
- Status: accepted
- Referenced by: Thesis: 19 tracked files, e.g. eval/common/paths.py:16, eval/DECISIONS.md:61, .agent/DECISIONS.md:534 (task2_provenance.md:70). ENSC498: none. Canonical copy: thesis repo Video/.
- Uncertainties: Status 'accepted' records that it was the primary evaluation recording from 2026-08-25 until R5 superseded it.

### R5_waypoint_loop_earlier_take_20260825_222024.bag

- New name: R5_waypoint_loop_earlier_take_20260825_222024.bag
- Old name: recording_20260825_222024.bag
- Session: R5 (S10: R5, 2026-08-25 22:20-22:24)
- Capture: 2026-08-25; 69.973 s; 2099 colour / 2099 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.17.0.10; sha256 a678e670662e; full record in index.json.
- Tiles: 12 tiles. The scene is empty at frame 0 apart from the image-left edge. A person in a black "JUST DO IT" T-shirt and grey shorts enters, moves the cube along the desk with one hand, raises both hands at 38 s, then leans far to the image right at 44-57 s. A yellow rod appears on the desk from 57 s. The cube is on the desk in every tile after 19 s; the wire rig is present. (thumbnails/R5_waypoint_loop_earlier_take_20260825_222024_contact.png)
- Content: No text describes this take; 70 s, the same length as R5 (ensc_provenance.md:160-162). R5 was recorded under the E-013 re-recording protocol, "re-record until it does" (eval/DECISIONS.md:348-355).
- Status: earlier_take
- Referenced by: None (ensc_provenance.md:162).
- Uncertainties: The tiles do not show the cube lifted to the wire, and the person leaves the lane from 44 s; the take may have been interrupted (UNCERTAIN). Why it was not used is not recorded.

### R5_waypoint_loop_earlier_take_20260825_222149.bag

- New name: R5_waypoint_loop_earlier_take_20260825_222149.bag
- Old name: recording_20260825_222149.bag
- Session: R5 (S10: R5, 2026-08-25 22:20-22:24)
- Capture: 2026-08-25; 69.982 s; 2099 colour / 2099 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.17.0.10; sha256 3316b7883929; full record in index.json.
- Tiles: 12 tiles. Same person and rig, the yellow rod on the desk from frame 0. The cube is moved along the desk, lifted in the image-right hand (his left) at 44.6 s, held near the wire at 50.9 s and in the other hand at 57.3 s, then set on the desk; the person stands back at 70 s. (thumbnails/R5_waypoint_loop_earlier_take_20260825_222149_contact.png)
- Content: No text describes this take; 70 s (ensc_provenance.md:164-165). Recorded under E-013 (eval/DECISIONS.md:348-355).
- Status: earlier_take
- Referenced by: None (ensc_provenance.md:165).
- Uncertainties: Why it was not used is not recorded (ensc_provenance.md:18).

### R5_occlusion_waypoint_loop_primary_20260825_222315.bag

- New name: R5_occlusion_waypoint_loop_primary_20260825_222315.bag
- Old name: recording_20260825_222315.bag
- Session: R5 (S10: R5, 2026-08-25 22:20-22:24)
- Capture: 2026-08-25; 69.982 s; 2099 colour / 2099 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.17.0.10; sha256 0c406cf38ec0; full record in index.json.
- Tiles: 6 tiles. Same person and rig with the yellow rod. The cube is moved along the desk with one hand, then with both hands (42 s), held up between the two hands at 56 s, and back on the desk at 70 s with the person standing back. (thumbnails/R5_occlusion_waypoint_loop_primary_20260825_222315_contact.png)
- Content: `R5_STEM = "recording_20260825_222315"   # primary, occlusion scenario (user-selected 2026-08-26)` (eval/common/paths.py:15). "The cube traverses a designed 8-waypoint loop (desk moves, 31 cm lift, wire traverse, two handovers)" (README.md:48-50). It is the WITH-occlusion primary (eval/README.md:5-9) (task2_provenance.md:77-88).
- Status: primary
- Referenced by: Thesis: 84 tracked files, e.g. eval/README.md:5, eval/gt/detect_waypoints.py:4, v2/integration/run_v2.py:100, presentation/defense_2026/SPEAKER_NOTES.md:467 (task2_provenance.md:83). ENSC498: none. Canonical copy: thesis repo Video/.
- Uncertainties: None material.

### R6_rail_cube_unmoved_rejected_20260831_065504.bag

- New name: R6_rail_cube_unmoved_rejected_20260831_065504.bag
- Old name: recording_20260831_065504.bag
- Session: R6 (S11: R6 rail, 2026-08-31 06:55-06:56)
- Capture: 2026-08-31; 29.989 s; 900 colour / 900 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.17.0.10; sha256 bde4fe58eea3; full record in index.json.
- Tiles: 6 tiles. A raised wooden rail on the desk. A person in a yellow-green jacket walks in from the image left over the first 12 s, then stands behind the rail with arms at his sides from 18 to 30 s. The cube stays at the near end of the rail and is not touched in any tile. (thumbnails/R6_rail_cube_unmoved_rejected_20260831_065504_contact.png)
- Content: R6a, `R6A_STEM = "recording_20260831_065504"` (eval/common/paths.py:22). "Take 1 of the same session" as R6B (eval/DECISIONS.md:712-717). It "failed the A6 precondition on every landmark (pose on 661/900 frames) and is kept only as a rejected take" (eval/DECISIONS.md:717-719) (task2_provenance.md:90-101).
- Status: rejected
- Referenced by: Thesis: 3 tracked files, eval/common/paths.py:22, eval/DECISIONS.md:717, skill_set/evaluation-scenario-separation.md:15 (task2_provenance.md:96). ENSC498: none. Canonical copy: thesis repo Video/.
- Uncertainties: Six tiles over 30 s; the cube could have moved between tiles, but it is at the same place in all six. The earlier proposed alias 'rail_slide' (task2_provenance.md:100) does not match the tiles.

### R6_rail_slide_one_hand_primary_20260831_065553.bag

- New name: R6_rail_slide_one_hand_primary_20260831_065553.bag
- Old name: recording_20260831_065553.bag
- Session: R6 (S11: R6 rail, 2026-08-31 06:55-06:56)
- Capture: 2026-08-31; 29.989 s; 900 colour / 900 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.17.0.10; sha256 c6e8a8919376; full record in index.json.
- Tiles: 6 tiles. Frame 0 carries a burned-in pose skeleton overlay; the later tiles are clean. A person in the yellow-green jacket, face out of frame, uses the image-left hand (his right) to lift the cube onto the rail and slide it to the far end; the other arm hangs idle. One hand only. (thumbnails/R6_rail_slide_one_hand_primary_20260831_065553_contact.png)
- Content: R6b, `R6B_STEM = "recording_20260831_065553"` (eval/common/paths.py:23). "a straight horizontal wooden rail raised above the desk; the cube is lifted from the desk onto the rail and slid to its far end" (eval/DECISIONS.md:712-716). "Offset fit: right hand only"; "the idle left arm" (eval/DECISIONS.md:724-726). WITHOUT-occlusion primary (eval/README.md:10-15) (task2_provenance.md:103-114).
- Status: primary; legacy symlink recording_20260831_065553.bag -> R6_rail_slide_one_hand_primary_20260831_065553.bag (B-004)
- Referenced by: Thesis: 203 tracked files, e.g. eval/README.md:10, eval/common/paths.py:23, writing/v9/scripts/make_ch5_fig_frames.py:39, presentation/defense_2026/anim/causal_replay.py:44 (task2_provenance.md:109). ENSC498: run_offline_processing.py:19 (uncommitted), send_all_to_unity.py:36, send_all_to_unity_replay.py:28-29 (labelled "# Right arm"), tracking_data_both_arms_test.json:3 (ensc_provenance.md:175-179). Legacy symlink kept for those scripts (B-004). Canonical copy: thesis repo Video/.
- Uncertainties: None material. The ENSC498 label "# Right arm" matches the one-hand content.

### R7_rail_handover_earlier_take_20260908_235402.bag

- New name: R7_rail_handover_earlier_take_20260908_235402.bag
- Old name: recording_20260908_235402.bag
- Session: R7 (S12: R7 handover night, 2026-09-08/09 23:54-00:01)
- Capture: 2026-09-08; 29.989 s; 900 colour / 900 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.17.0.10; sha256 e9bba349dc7e; full record in index.json.
- Tiles: 12 tiles. Frame 0 carries a burned-in pose skeleton overlay; the later tiles are clean. A person in a lime sweater under an open dark jacket, head out of frame; the right hand brings the cube onto the rail and slides it; both hands meet on the cube mid-rail at 24.6-27.3 s; at 30 s the cube is near the far end under the left hand. The take ends at 30 s. (thumbnails/R7_rail_handover_earlier_take_20260908_235402_contact.png)
- Content: No per-take text. The night had "eight takes" (eval/RECORDING_R7_HANDOVER.md:3-4); "the seven earlier takes of that night are not used, user direction" (eval/DECISIONS.md:1066; eval/common/paths.py:26-27) (ensc_provenance.md:181-193).
- Status: earlier_take
- Referenced by: None by name (ensc_provenance.md:185).
- Uncertainties: No reason for not using this take is recorded. It is 30 s, shorter than the 50 s of the other takes (ensc_provenance.md:186).

### R7_rail_handover_earlier_take_20260908_235500.bag

- New name: R7_rail_handover_earlier_take_20260908_235500.bag
- Old name: recording_20260908_235500.bag
- Session: R7 (S12: R7 handover night, 2026-09-08/09 23:54-00:01)
- Capture: 2026-09-08; 49.97 s; 1499 colour / 1499 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.17.0.10; sha256 1da78d3eab81; full record in index.json.
- Tiles: 12 tiles. Frame 0 overlay, later tiles clean. Same person; the right hand slides the cube along the rail, both hands meet on it at 31.8 s, and the left hand slides it to the far end (36-50 s). (thumbnails/R7_rail_handover_earlier_take_20260908_235500_contact.png)
- Content: No per-take text. The night had "eight takes" (eval/RECORDING_R7_HANDOVER.md:3-4); "the seven earlier takes of that night are not used, user direction" (eval/DECISIONS.md:1066; eval/common/paths.py:26-27) (ensc_provenance.md:181-193).
- Status: earlier_take
- Referenced by: None by name (ensc_provenance.md:185).
- Uncertainties: No reason for not using this take is recorded.

### R7_rail_handover_earlier_take_20260908_235605.bag

- New name: R7_rail_handover_earlier_take_20260908_235605.bag
- Old name: recording_20260908_235605.bag
- Session: R7 (S12: R7 handover night, 2026-09-08/09 23:54-00:01)
- Capture: 2026-09-08; 49.97 s; 1499 colour / 1499 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.17.0.10; sha256 09af620a098b; full record in index.json.
- Tiles: 12 tiles. Frame 0 overlay, later tiles clean. Same sequence: right-hand slide to mid-rail, two hands on the cube at 31.8 s, left hand at the far end by 36.4 s, cube at the far end to 50 s. (thumbnails/R7_rail_handover_earlier_take_20260908_235605_contact.png)
- Content: No per-take text. The night had "eight takes" (eval/RECORDING_R7_HANDOVER.md:3-4); "the seven earlier takes of that night are not used, user direction" (eval/DECISIONS.md:1066; eval/common/paths.py:26-27) (ensc_provenance.md:181-193).
- Status: earlier_take
- Referenced by: None by name (ensc_provenance.md:185).
- Uncertainties: No reason for not using this take is recorded.

### R7_rail_handover_earlier_take_20260908_235712.bag

- New name: R7_rail_handover_earlier_take_20260908_235712.bag
- Old name: recording_20260908_235712.bag
- Session: R7 (S12: R7 handover night, 2026-09-08/09 23:54-00:01)
- Capture: 2026-09-08; 49.97 s; 1499 colour / 1499 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.17.0.10; sha256 7ecc81da3eaa; full record in index.json.
- Tiles: 12 tiles. Frame 0 overlay, later tiles clean. Right-hand slide; two hands together on the cube at 36.4 s; left hand with the cube at the far end from 40.9 to 50 s. (thumbnails/R7_rail_handover_earlier_take_20260908_235712_contact.png)
- Content: No per-take text. The night had "eight takes" (eval/RECORDING_R7_HANDOVER.md:3-4); "the seven earlier takes of that night are not used, user direction" (eval/DECISIONS.md:1066; eval/common/paths.py:26-27) (ensc_provenance.md:181-193).
- Status: earlier_take
- Referenced by: None by name (ensc_provenance.md:185).
- Uncertainties: No reason for not using this take is recorded.

### R7_rail_handover_unreadable_20260908_235818.bag

- New name: R7_rail_handover_unreadable_20260908_235818.bag
- Old name: recording_20260908_235818.bag
- Session: R7 (S12: R7 handover night, 2026-09-08/09 23:54-00:01)
- Capture: unreadable. Size 267920248 bytes; sha256 881947db4924f11bbb1a79552a5238e8aa088e33b82b4c0ce175ec90d01e553b; capture stamp 2026-09-08T23:58:18. Probe error: `RuntimeError: Failed to resolve request. Request to enable_device_from_file("/home/luo/Desktop/ENSC498/recordings/recording_20260908_235818.bag") was invalid, Reason: Failed to create ros reader: Bag unindexed` (index.json).
- Tiles: none (the bag cannot be opened).
- Content: 268 MB, "Bag unindexed" (ensc_provenance.md:190-192). Inferred cause: q during recording in the pose recorder returns without pipeline.stop() (record_realsense_bag_pose.py:278-280; ensc_provenance.md:221, UNCERTAIN). One of the eight takes of the night (eval/RECORDING_R7_HANDOVER.md:3-4).
- Status: unreadable; deleted 2026-09-23 per B-005
- Referenced by: None by name (ensc_provenance.md:185).
- Uncertainties: Scene words come from the session only.

### R7_rail_handover_earlier_take_20260908_235840.bag

- New name: R7_rail_handover_earlier_take_20260908_235840.bag
- Old name: recording_20260908_235840.bag
- Session: R7 (S12: R7 handover night, 2026-09-08/09 23:54-00:01)
- Capture: 2026-09-08; 49.97 s; 1499 colour / 1499 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.17.0.10; sha256 eee55ca6361f; full record in index.json.
- Tiles: 12 tiles. Frame 0 overlay, later tiles clean. Right-hand slide; two hands on the cube at 31.8 s; the left hand moves it to the far end by 36.4 s and it stays there to 50 s. (thumbnails/R7_rail_handover_earlier_take_20260908_235840_contact.png)
- Content: No per-take text. The night had "eight takes" (eval/RECORDING_R7_HANDOVER.md:3-4); "the seven earlier takes of that night are not used, user direction" (eval/DECISIONS.md:1066; eval/common/paths.py:26-27) (ensc_provenance.md:181-193).
- Status: earlier_take
- Referenced by: None by name (ensc_provenance.md:185).
- Uncertainties: No reason for not using this take is recorded.

### R7_rail_handover_unreadable_20260908_235947.bag

- New name: R7_rail_handover_unreadable_20260908_235947.bag
- Old name: recording_20260908_235947.bag
- Session: R7 (S12: R7 handover night, 2026-09-08/09 23:54-00:01)
- Capture: unreadable. Size 669048599 bytes; sha256 b9bcc87e5f0d779279b3f22cf0174e467c8361b13505877ae8e8e45601a7a8b8; capture stamp 2026-09-08T23:59:47. Probe error: `RuntimeError: Failed to resolve request. Request to enable_device_from_file("/home/luo/Desktop/ENSC498/recordings/recording_20260908_235947.bag") was invalid, Reason: Failed to create ros reader: Bag unindexed` (index.json).
- Tiles: none (the bag cannot be opened).
- Content: 669 MB, "Bag unindexed" (ensc_provenance.md:190-192). Inferred cause: q during recording in the pose recorder returns without pipeline.stop() (record_realsense_bag_pose.py:278-280; ensc_provenance.md:221, UNCERTAIN). One of the eight takes of the night (eval/RECORDING_R7_HANDOVER.md:3-4).
- Status: unreadable; deleted 2026-09-23 per B-005
- Referenced by: None by name (ensc_provenance.md:185).
- Uncertainties: Scene words come from the session only.

### R7_rail_handover_two_hand_accepted_20260909_000024.bag

- New name: R7_rail_handover_two_hand_accepted_20260909_000024.bag
- Old name: recording_20260909_000024.bag
- Session: R7 (S12: R7 handover night, 2026-09-08/09 23:54-00:01)
- Capture: 2026-09-09; 49.97 s; 1499 colour / 1499 depth frames; depth z16 640x480 30 fps, color bgr8 640x480 30 fps; Intel RealSense D435 serial 215322078503, firmware 5.17.0.10; sha256 d0fd94121237; full record in index.json.
- Tiles: 6 tiles. Frame 0 carries a burned-in pose skeleton overlay; the later tiles are clean. The right hand lifts the cube onto the rail and slides it (10-20 s), both hands are on the cube at 30 s, and the cube is at the far end under the left hand at 40 and 50 s. (thumbnails/R7_rail_handover_two_hand_accepted_20260909_000024_contact.png)
- Content: `R7_STEM = "recording_20260909_000024"` (eval/common/paths.py:28). "the right hand slides the cube to about 30 cm along the rail, the left hand takes it over and slides it to the far end" (eval/README.md:16-19). The handover runs from frame 864 to frame 1022, 5.27 s (eval/reports/r7_handover.md:13). "RECORDED AND ACCEPTED ... named the last one ... as the one to use" (eval/RECORDING_R7_HANDOVER.md:3-8). The wall card had shifted, so gravity is carried from R6b (eval/RECORDING_R7_HANDOVER.md:9-11) (task2_provenance.md:116-127).
- Status: accepted
- Referenced by: Thesis: 123 tracked files, e.g. eval/README.md:16, eval/DECISIONS.md:1066, presentation/defense_2026/talk_content.json:265, writing/v9/audit_evidence/figure_3_4_video/source.json:5 (task2_provenance.md:122). ENSC498: none. Canonical copy: thesis repo Video/.
- Uncertainties: None material.

## Camera and common properties

- All 28 readable bags: Intel RealSense D435, serial 215322078503; depth z16 and colour bgr8, both 640x480 at 30 fps (index.json fields device_name, device_serial, streams). This matches the recorder configuration (ENSC498 record_realsense_bag.py:23-24,56-57; record_realsense_bag_pose.py:18-19,147-148; ensc_provenance.md:213).
- Firmware: firmware 5.16.0.1 on the 12 readable bags dated 2025-12-15 to 2026-02-24, and 5.17.0.10 on the 16 dated 2026-03-17 to 2026-09-09 (index.json field firmware; dates as in the summary table).
- In every readable bag the colour and depth frame counts are equal (index.json frame_count_color, frame_count_depth; counting method iterated_all_framesets_unique_frame_number).
- Tile labels on the contact sheets are the zero-based colour frame index in playback order, not the device frame number (index.json thumbnail_frames; the device numbers are color_frame_number_min/max).
- A stem `recording_YYYYMMDD_HHMMSS` marks the recorder's launch time, not the first written frame: both recorders take `datetime.now()` before the preview wait (ENSC498 record_realsense_bag.py:36-38; record_realsense_bag_pose.py:140-141; ensc_provenance.md:209-212).
- Image orientation: the cited left-arm tests (R1 session 082950, 083018; v1era 021821) move the arm on the image right, and the right-elbow test moves the arm on the image left, so the colour images are unmirrored; 'image-left arm' in the tiles notes is the person's right arm.
- Nine thesis stems live in the thesis repository's Video/; seven of them are also in this folder (083945, 070032, 070152, 222315, 065504, 065553, 000024). The copies here are separate files (different inode, link count 1, checked with stat on 2026-09-23) whose sha256 equals the Video/ sha256 recorded in the earlier Video/ probe index. The thesis code reads Video/ only (eval/common/paths.py:30-32,64-65; task2_provenance.md:132), so renaming the copies here affects no thesis code.

## Rules for this folder

- Never rename a file again without updating RENAME_MAP.tsv, index.json and this README in the same step.
- The legacy symlinks exist only for the three ENSC498 scripts named in B-004: recording_20260831_065553.bag, recording_20260317_200217.bag, recording_20260122_154958.bag. Do not add others; update the scripts instead.
- Never write to, move or delete a .bag file here as a side effect of other work. The thesis repository's Video/ copies are canonical and are never touched from here.
- Regenerate the probe data from the thesis repository root with:

      /home/luo/anaconda3/bin/python eval/inspect/probe_bags.py --dir /home/luo/Desktop/ENSC498/recordings --dense ENSC498_right_arm_raise_cube_untouched_test_20260121_180042,ENSC498_aruco_cube_around_stick_test_aruco_full_circle,ENSC498_aruco_box_held_two_hands_test_Aruco_Only,R1_left_arm_raise_lower_test_20260224_082950,R1_left_arm_elbow_bend_test_20260224_083018,v1era_left_arm_cube_untouched_test_20260328_021821,R4_desk_cube_labeled_path_earlier_take_20260825_065917,R5_waypoint_loop_earlier_take_20260825_222024,R5_waypoint_loop_earlier_take_20260825_222149,R7_rail_handover_earlier_take_20260908_235402,R7_rail_handover_earlier_take_20260908_235500,R7_rail_handover_earlier_take_20260908_235605,R7_rail_handover_earlier_take_20260908_235712,R7_rail_handover_earlier_take_20260908_235840

  The 14 dense (12-tile) bags are, by original stem: Aruco_Only, recording_20260121_180042, aruco_full_circle, recording_20260224_082950, recording_20260224_083018, recording_20260328_021821, recording_20260825_065917, recording_20260825_222024, recording_20260825_222149, recording_20260908_235402, recording_20260908_235500, recording_20260908_235605, recording_20260908_235712, recording_20260908_235840. The command above lists them under their new stems (the new names without .bag). The script skips the three legacy symlinks, so the index has one record per real file (eval/inspect/probe_bags.py:33-35,289-294). It copies the curated fields (new_name, old_name, session, take_status, scene_summary, provenance_note, renamed_on) from the existing index.json onto each new record, finding the old record by stem first and, failing that, by sha256, so curated fields survive a rename as long as the content is unchanged (eval/inspect/probe_bags.py:37-44,68-69,300-302,322-327). The header field curated_by is carried over from the old index when present (eval/inspect/probe_bags.py:252-261,350-351). A rerun writes the thumbnails named by the current stems.

## Decisions

ID: B-001

- Status: SETTLED
- Decision: Rename the originals in place; no aliases, no subfolders.
- Why: User decision 2026-09-23: one name per file keeps the folder listing self-describing and avoids a second name for scripts and people to track.
- Alternatives: Symlink aliases next to the old names; moving files into per-session subfolders. Both rejected by the user.
- Evidence: User decision 2026-09-23 (no measurement).
- Reversibility: Rename back using RENAME_MAP.tsv (old_name, new_name columns).
- Review: Check that the folder listing reads well and that no external tool depends on the old names beyond the B-004 scripts.

ID: B-002

- Status: SETTLED
- Decision: The index lives in this folder (README.md, index.json, RENAME_MAP.tsv, thumbnails/); a tracked copy of README.md and index.json goes to eval/recordings_archive/ in the thesis repository.
- Why: User decision 2026-09-23: this folder is not under version control (ENSC498/.gitignore:2 ignores recordings/, ensc_provenance.md:227), so a tracked copy is needed for history.
- Alternatives: Index only in the thesis repository; index only here. Rejected by the user.
- Evidence: User decision 2026-09-23; ENSC498/.gitignore:2.
- Reversibility: Delete the tracked copy or stop maintaining the local one.
- Review: Check the copy in eval/recordings_archive/ matches this README and index.json after it is made (another worker).

ID: B-003

- Status: SETTLED
- Decision: New name = <SESSION>_<scene words>_<status>_<original stem>.bag.
- Why: User chose the style 2026-09-23. SESSION is R1, R4, R5, R6, R7 for thesis sessions, v1era for the March 2026 bags, ENSC498 for the December 2025 to February 2026 bags. Scene words are two to five lowercase ASCII words from cited text first, then the tiles. Status is one of accepted, primary, backup, earlier_take, rejected, test, unreadable. No take numbers. The trailing stem drops the recording_ prefix; hand-named bags keep their full old name.
- Alternatives: Take numbers (rejected: order is already in the stem); dates as the leading field (rejected: session first groups the listing).
- Evidence: User decision 2026-09-23; scene words per file are cited in each detail block.
- Reversibility: Rename again from RENAME_MAP.tsv with a new scheme, updating index.json and this README in the same step.
- Review: Check the scene words of the files marked with tile-based content: 180042, aruco_full_circle, Aruco_Only, 200217, 065504, 222024, 222149, and the status 'test' (not 'earlier_take') for 082950 and 083018.

ID: B-004

- Status: SETTLED
- Decision: Create three relative legacy-name symlinks inside this folder after the rename.
- Why: ENSC498 scripts hard-code the old names: recording_20260831_065553.bag (send_all_to_unity.py:36, send_all_to_unity_replay.py:29, run_offline_processing.py:19), recording_20260317_200217.bag (export_bag_to_mp4.py:10, extract_mediapipe_landmarks.py:12, demo_processing_and_plots.py:36), recording_20260122_154958.bag (test_markers.py:9). Symlinks keep them working without editing ENSC498.
- Alternatives: Edit the ENSC498 scripts (rejected: ENSC498 is a read-only reference directory per the thesis repository AGENTS.md, standing constraints); no symlinks (rejected: the scripts would break).
- Evidence: The script lines above (ensc_provenance.md:78,130-131,175-178).
- Reversibility: Remove the symlinks once the scripts point at the new names.
- Review: Check the three symlinks resolve (ls -l) after the rename step.

ID: B-005

- Status: SETTLED
- Decision: Delete the six unreadable bags.
- Why: User decision 2026-09-23. Three are 27076-byte stubs with probe error "No streams are selected!" (recording_20260131_184322, recording_20260825_065736, recording_20260825_065900); three report "Bag unindexed" (recording_20260825_070016, recording_20260908_235818, recording_20260908_235947). None is referenced by any script or document (ensc_provenance.md:199-204).
- Alternatives: Keep them (rejected: they cannot be opened by the reader in use); repair the unindexed ones with a rosbag reindex (not chosen by the user).
- Evidence: The error strings in index.json (field error); probe log.
- Reversibility: Irreversible once deleted; the size and sha256 below and in RENAME_MAP.tsv identify what was removed.
- Review: Confirm the six files are gone and nothing else was removed.

Deleted files (B-005), for the record:

| old name | size bytes | sha256 | probe error |
|---|---|---|---|
| recording_20260131_184322.bag | 27076 | ed6ef43102d60a0ee3df979a552de2ed401b8bbf6c733f1c215b41f381140fcb | No streams are selected! |
| recording_20260825_065736.bag | 27076 | ed6ef43102d60a0ee3df979a552de2ed401b8bbf6c733f1c215b41f381140fcb | No streams are selected! |
| recording_20260825_065900.bag | 27076 | ed6ef43102d60a0ee3df979a552de2ed401b8bbf6c733f1c215b41f381140fcb | No streams are selected! |
| recording_20260825_070016.bag | 108457028 | 12fbfff28d5d532beae011a6bce9041bbde29523122507ffbb590e9a48b9268c | Bag unindexed |
| recording_20260908_235818.bag | 267920248 | 881947db4924f11bbb1a79552a5238e8aa088e33b82b4c0ce175ec90d01e553b | Bag unindexed |
| recording_20260908_235947.bag | 669048599 | b9bcc87e5f0d779279b3f22cf0174e467c8361b13505877ae8e8e45601a7a8b8 | Bag unindexed |

Facts recorded with the decisions (not decisions): the recorder scripts name a file from the launch time (ENSC498 record_realsense_bag.py:36-38, record_realsense_bag_pose.py:140-141); the copies here of the thesis stems are separate byte-identical files of the Video/ bags, and the thesis code reads Video/ only (see Camera and common properties).

## Which recording suits the pending defence replay (pages 34, 36, 38)

R6b (R6_rail_slide_one_hand_primary_20260831_065553) is the strongest candidate: it is the only bag with both a matching v2 calibration and full v2 dumps on disk, and the defence already uses it for the frame-flow and causal-replay material; its limit is one-hand content only (task2_provenance.md:112). R5 (R5_occlusion_waypoint_loop_primary_20260825_222315) is a candidate: a matching v2 calibration exists and it has already been run through v2 (v2/dataset/r5_probe_baseline.txt:9,18), its two-hand handovers and natural occlusion suit page 36's real hold/recovery event, but no *_r5_full v2 dump is on disk (task2_provenance.md:86). R7 (R7_rail_handover_two_hand_accepted_20260909_000024) is a maybe: it has two-hand handover content and an eval calibration, but it has never been run through v2, has no v2 dump, and its r7c calibration carries borrowed gravity (E-034), so a first v2 run would be needed (task2_provenance.md:125).

Listing check, 2026-09-23, `ls -la v2/output | grep -i r6b` in the thesis repository:

    -rw-rw-r--  1 luo luo       4617 Sep  1 23:25 scene_calibration_r6b_v2.json
    -rw-rw-r--  1 luo luo     263117 Sep  1 23:27 v2_integrate_dump_r6b_full.csv
    -rw-rw-r--  1 luo luo     144752 Sep  1 23:27 v2_object_dump_r6b_full.csv
    -rw-rw-r--  1 luo luo     314301 Sep  1 23:27 v2_person_dump_r6b_full.csv

The same folder holds, for R5 and R7, only: scene_calibration_r5_v2.json (no R5 or R7 dump, no R7 calibration).


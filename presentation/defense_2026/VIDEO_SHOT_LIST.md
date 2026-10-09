# Demonstration shot list

Currency note (2026-10-08): This is a retained shot list for the retired
39-main/14-hidden deck. Its committee movie/index/contract links and page
bindings describe that historical delivery, recoverable at commits
85078c9 and 87e87ae under D-385. Current deck/media facts and remaining
playback checks are in [README.md](README.md). Original source intervals
and recording proposals below are preserved.

The current presentation contains 39 main and 14 hidden topic pages (40-53, round 6, 2026-09-28), reached by typing the slide number; there is no index page (D-127, D-128). Recorded footage accompanies 17 of 20 main demonstrations (unchanged; the films kept their pages or moved with the round-5 renumbering). The three previously-proposed instrumented execution recordings below (image copying, stream resampling, Python/Unity read verification; thesis Sections 6.1.1-6.1.2 and 6.2) no longer have a hidden page (deleted in round 4, D-127); the recipes are kept for reference. The optional live-camera proposal is thesis Sections 8.4-8.5 and Appendix B (formerly Q&A page 48, deleted). The two supplemental technical animations (media/memory_records.gif/mp4 and media/frame_journey.gif/mp4; thesis Sections 6.1.1-6.1.2) are no longer linked from a deck page (formerly Q&A pages 46 and 51, deleted). Use the [current video index](committee_materials/unified_revision/VIDEO_INDEX.md) and [hash/source contract](committee_materials/unified_revision/media_contract.json); the earlier bank_revision and axes_revision collections and the 76-page and 75-page media remain preserved.

## Ready demonstrations

| Page | Movie | Duration | Evidence role |
|---:|---|---:|---|
| 8 | [p06-Accepted_Body_Landmarks_With_Axes.mp4](committee_materials/axes_revision/videos/p06-Accepted_Body_Landmarks_With_Axes.mp4) | 22.000 s | Recorded input overlay |
| 44 | [p07-Hampel_Spike_Removal.mp4](committee_materials/axes_revision/videos/p07-Hampel_Spike_Removal.mp4) | 18.700 s | Synchronized recorded RGB and calculation |
| 45 | [p08-Short_Gap_Interpolation.mp4](committee_materials/axes_revision/videos/p08-Short_Gap_Interpolation.mp4) | 18.700 s | Synchronized recorded RGB and calculation |
| 9 | [p09-Offline_Butterworth_Smoothing.mp4](committee_materials/axes_revision/videos/p09-Offline_Butterworth_Smoothing.mp4) | 18.367 s | Synchronized recorded RGB and calculation |
| 12 | [p13-Torso_Frame_From_Standing_T_Pose.mp4](committee_materials/unified_four/videos/p13-Torso_Frame_From_Standing_T_Pose.mp4) | 11.067 s | Recorded standing T-pose (arm_test bag, frames 780-885) and computed torso frame (L24 origin, hip-line X, root Euler angles) |
| none (D-130) | [p14-Shoulder_Swing_Rotates_Root_Frame_Onto_Upper_Arm.mp4](committee_materials/unified_four/videos/p14-Shoulder_Swing_Rotates_Root_Frame_Onto_Upper_Arm.mp4) | 11.133 s | Recorded arm raise (180042 bag, frames 3-109) and computed shoulder swing (L12 frame rotated onto the upper arm); retired in round 4 (thesis Section 3.3) |
| 13 | [p15-Shoulder_Twist_About_Upper_Arm_Axis.mp4](committee_materials/unified_four/videos/p15-Shoulder_Twist_About_Upper_Arm_Axis.mp4) | 18.733 s | Recorded arm movement (right_arm_test bag, frames 505-725) and computed shoulder twist, with the observability reading folded in |
| 14 | [p16-Elbow_Rotation_Onto_Forearm.mp4](committee_materials/unified_four/videos/p16-Elbow_Rotation_Onto_Forearm.mp4) | 28.067 s | Recorded elbow bending (right_elbow bag, frames 180-540) and computed elbow angles from the completed L14 frame |
| 18 | [p23-Holding_Input_And_Torso_Rejection_With_Axes.mp4](committee_materials/axes_revision/videos/p23-Holding_Input_And_Torso_Rejection_With_Axes.mp4) | 6.000 s | Recorded input overlay |
| 19 | [p25-Grasp_Offset_During_Wrist_Depth_Loss_With_Axes.mp4](committee_materials/axes_revision/videos/p25-Grasp_Offset_During_Wrist_Depth_Loss_With_Axes.mp4) | 15.400 s | Synchronized recorded RGB and derivation |
| none (D-127; thesis 6.1.2) | [p27-Fresh_Unity_Wrist_Loss_With_Model_Axes.mp4](committee_materials/axes_revision/videos/p27-Fresh_Unity_Wrist_Loss_With_Model_Axes.mp4) | 12.000 s | Recorded RGB and fresh Unity replay |
| 20 | [p29-Elbow_Endpoint_Constraint_Circle_With_Axes.mp4](committee_materials/axes_revision/videos/p29-Elbow_Endpoint_Constraint_Circle_With_Axes.mp4) | 15.400 s | Synchronized recorded RGB and endpoint constraints |
| 21 | [p32-Controlled_Held_Joint_Fallback.mp4](committee_materials/axes_revision/videos/p32-Controlled_Held_Joint_Fallback.mp4) | 8.000 s | Controlled masked-landmark recording |
| 23 | [p33-Single_Frame_Data_Flow.mp4](committee_materials/axes_revision/videos/p33-Single_Frame_Data_Flow.mp4) | 44.000 s | Recorded RGB and saved-data walkthrough |
| 25 | [p41-Archived_Pose_Replay_With_Model_Axes.mp4](committee_materials/bank_revision/videos/p41-Archived_Pose_Replay_With_Model_Axes.mp4) | 25.000 s | Recorded RGB and direct archived-packet Unity replay (file stem p41) |
| 31 | [p47-Fresh_Unity_Handover_With_Model_Axes.mp4](committee_materials/axes_revision/videos/p47-Fresh_Unity_Handover_With_Model_Axes.mp4) | 49.933 s | Recorded RGB and fresh Unity replay |
| 33 | [p49-Causal_One_Euro_Filtering.mp4](committee_materials/axes_revision/videos/p49-Causal_One_Euro_Filtering.mp4) | 18.367 s | Synchronized recorded RGB and causal calculation |
| 47 | [p67-Savitzky_Golay_Filtering.mp4](committee_materials/axes_revision/videos/p67-Savitzky_Golay_Filtering.mp4) | 18.367 s | Synchronized recorded RGB and calculation |
| 48 | [p68-Median_Filtering.mp4](committee_materials/axes_revision/videos/p68-Median_Filtering.mp4) | 18.367 s | Synchronized recorded RGB and calculation |

## Coordinate-frame evidence

All shared triads use X red (#FF4040), Y green (#40E070) and Z blue (#408CFF). Colors identify axes, not validity states. The shared renderer is anim/coordinate_axes.py. It consumes metric origins, basis columns and a calibrated camera or explicitly editorial orthographic projector.

- Pages 12, 13 and 14 (round 2 kinematics films, round 3 page numbers) use four new films with one unified layout in committee_materials/unified_four/{videos,posters,review,provenance} (author request, 2026-09-24, round 2): the recorded video with its overlay on top, the 3D model drawn with the recording's own pinhole projection at lower left showing the parent frame dim and the rotated frame bright with a grey arc labelled by the angle, and a small 2D plane panel with that page's quantity at lower right. File names: p13-Torso_Frame_From_Standing_T_Pose.mp4 (11.067 s, now page 12), p14-Shoulder_Swing_Rotates_Root_Frame_Onto_Upper_Arm.mp4 (11.133 s, retired in round 4, D-130; it was round 3's Q&A page 76), p15-Shoulder_Twist_About_Upper_Arm_Axis.mp4 (18.733 s, now page 13), p16-Elbow_Rotation_Onto_Forearm.mp4 (28.067 s, now page 14), all in committee_materials/unified_four/videos/. The lower-left model and the overlay share one projection; the producers record the L12 pixel of both on every source frame. Page 12 (Torso frame) uses ENSC498_arms_outstretched_pose_test_arm_test.bag frames 780-885: a standing T-pose facing the camera with a small lean; it does not show a torso rotation. The retired shoulder-swing film (thesis Section 3.3; formerly Q&A page 76, D-130) uses ENSC498_right_arm_raise_cube_untouched_test_20260121_180042 frames 3-109. Page 13 (Shoulder twist) uses ENSC498_right_arm_landmark_test_right_arm_test frames 505-725 and folds in the former observability reading (perpendicular fraction, Section 5.5). Page 14 (Elbow) uses ENSC498_right_elbow_bend_test_right_elbow frames 180-540, unchanged from the round-1 bank window. Playback is half speed with two-second endpoint holds. Root origin is the actual right hip L24, not the stored pelvis midpoint. The earlier R7 films for the old pages 13-16 (frames 100-249) remain preserved in committee_materials/axes_revision with their original review.
- The round-1 bank_axes_revision collection (old pages 13-16) and bank_revision_v2 collection (old pages 17-20) are superseded by the unified_four collection above and remain preserved on disk for history; they are no longer referenced by any current page. Their actual inference RGB hash, hardware frame ID and absolute timestamp bound each camera image to the filtered landmark calculation, and their reports remain valid only for those preserved films: page 17 (round 1) showed the unit upper arm in the L12 X-Z plane with the azimuth arc, with the camera-view model drawing the moving swing basis at the elbow, a dim L12 reference and the forearm in faded white; page 18 showed the swing-removed unit-forearm Y-Z components with the thesis L12 notation; page 19 showed the forearm X-Z components in completed L14; page 20 magnified the nonzero perpendicular component beside a separate ideal zero-component sketch. All selected round-1 samples retained twist_ok true; there was no observed singular or held state. CPU preparation supplies qualitative examples, not thesis accuracy or GPU timing results.
- Pages 8/18 retain the original input overlay and original Marker triads. Added L24/L14 axes are input-derived and omitted when required source geometry or saved state is not measured. The saved torso rejection remains visible even though original green torso dots are retained.
- Pages 19/20 add MappedMarker axes from saved calibrated object poses. The ideal-elbow view on 20 is endpoint-aligned; its points are computed in Camera-prime. It does not invent a saved prior or the runtime branch actually used.
- Thesis Section 6.1.2 (formerly Q&A page 66) and main page 31 retain source-matched R7 Unity replays with their own five effective lengths. Their saved measured/held/constrained tags precede display smoothing and are distinct from binary receiver status.
- Page 25 (file stem p41) instead applies the archived R5 integrated packets directly, with archived dimensions: right upper arm/forearm 0.256/0.252 m, left 0.262/0.247 m and torso 0.479 m. There is no additional solve or smoothing pass. Only archived binary live/non-live flags appear; newer recovery tags are not imported. In all three Unity views, the pelvis triad carries displayed L24 orientation at the rendered pelvis, not anatomical L24. Model frames precede authored bone rest offsets; no wrist orientation is measured.
- Page 21 retains a deliberately masked legacy recording without an experiment-frame map. No coordinate axes are fabricated on it.

Camera changes are limited to declared overlays and their pixel masks. The native camera is 640x480; a larger composite does not add camera resolution. Fresh Unity frames are 1440x1080, and the current paired canvas is 1440x1200. Axis lengths, model-panel scale and oblique-view scale are presentation choices, not measurements.

## Capture boundaries

The Unity pairs are qualitative application demonstrations. Thesis Section 6.1.2 (formerly Q&A page 66) and main page 31 retain R7-specific lengths; page 25 (file stem p41) uses its documented archived R5 dimensions. None inherits Table 7.4 accuracy numbers or establishes exact historical pixels. Offered wrist target and final chain endpoint are not separately instrumented by these captures. Every selected bank sample has observable twist; the exact zero-component limit is now presented on page 13, folded into the twist discussion, rather than as a separate schematic page.

## Three requested technical recordings still to make

These are proposals, not supplied evidence. Record the actual implementation in a debugger or an explicitly labelled copied instrumentation harness. Preserve uncut footage and logs. Do not modify the frozen source or count a visualization of saved fields as a recording of the original execution.

### Thesis Section 6.1.1: publication and private copies (formerly Q&A page 68, deleted, D-127)

- Editorial recording target: 35-45 s, silent H.264 MP4; `media/new_recordings/p30-Shared_Image_Copy_Execution.mp4` and PNG poster.
- Composition: camera/ring image at left; readable capture/consumer watch values at right.
- Show, one operation at a time: publication count and slot; odd/write/even sequence; colour and depth sizes; each branch's private copied arrays; final sequence and expected-frame validation.
- Required evidence: actual observed sequence and frame values, declared resolution, and enough code context to identify the copy from the memory map. A separate reader's buffer identity must not be presented as instrumentation of the person or object process.
- Narration: "This reader copies the image payload and accepts it only after the slot passes the consistency check."
- Acceptance: the shared image stays available while private arrays exist. A changed or overwritten slot is rejected rather than silently applied. Label paused or stepped execution; no latency claim.

### Thesis Section 6.1.2: two histories and a new output record (formerly Q&A page 70, deleted, D-127)

- Editorial recording target: 35-45 s; `media/new_recordings/p32-Temporal_Merger_Execution.mp4` and PNG poster.
- Composition: person history, object history and one selected render time; show the outgoing tick and resulting Unity update.
- Show: the actual person bracket and object bracket independently; the returned measured/interpolated/held/blended states; a new tick and render time in PSI2.
- Required evidence: selected source indices/times, output tick/time, source-state fields and packed payload. The source IDs do not become the combined tick.
- Narration: "Each stream is evaluated at the same render time, and the merger packs a fresh record."
- Acceptance: values come from the actual buffer/emit calls. Mark any debugger pauses; the configured delay is not measured end-to-end latency.

### Thesis Section 6.2: Python writer and Unity reader (formerly Q&A page 72, deleted, D-127)

- Editorial recording target: 45-55 s; `media/new_recordings/p34-Python_Unity_Concurrent_Access.mp4` and PNG poster.
- Composition: Python publication status, Unity's sequence checks/local variables, and Unity Game view.
- Show: one unchanged-even read accepted; one controlled overlapping write or odd-start read rejected; a later accepted new tick. For the all-retries-fail branch, show all three attempts and unchanged displayed transforms before claiming it happened.
- Required evidence: actual sequence values before/after typed reads, attempt counter, return result and output tick. Numbers need not be the illustrative 10/11/12.
- Narration: "The changed sequence invalidates these local values; Unity retries before applying a new pose."
- Acceptance: rejected values are not applied. Label a deliberately induced/debugger-controlled overlap. Do not claim a natural race frequency, a mutex or a formal cross-platform proof.

Concrete source locations and capture setup are in `RECORDING_GUIDE.md`. Retain the placeholders if the required trace is not available.


## Additional useful shots

- Page 18: instrument grip entry tests, five-frame confirmation, episode ID, clean count and reset; existing footage is holding context.
- Thesis Section 6.1.2 (formerly Q&A page 66): expose measured wrist, offered target and final reconstructed wrist as three distinct source-indexed values. Fresh Unity motion alone does not prove target use.
- Page 21: for a new natural-occlusion replacement, retain the camera frame, exact solver state and valid pose/projection logs. The current recording is deliberately masked.
- The optional live-camera validation (thesis Sections 8.4-8.5 and Appendix B; formerly Q&A page 48, deleted, D-127) remains unrecorded. Use a new checked physical calibration, unique bag/log paths and one capture broker.

Follow the detailed steps and acceptance conditions in [RECORDING_GUIDE.md](RECORDING_GUIDE.md). Preserve the uncut recordings, actual calibration, input type, source interval, frame map and hashes. Keep placeholders until the evidence exists.

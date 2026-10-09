# Media build and recording guide

Currency note (2026-10-08): This is a historical build and recording guide
for the retired presentation. In particular, build_deck.py,
anim/unified_revision_build.py and the committee collection/media-checker
paths below are not a current build route; the retired files are
recoverable at commits 85078c9 and 87e87ae (D-385). Current speaker-script
and PDF/package commands are in [README.md](README.md). Capture proposals,
source limitations and original page references below retain their old scope.

The current presentation contains 39 main and 14 hidden topic pages (40-53, round 6, 2026-09-28), reached by typing the slide number; there is no index page (D-127, D-128). Recorded footage accompanies 17 of 20 main demonstrations (unchanged; the main talk is untouched by round 4). The three previously-proposed instrumented execution recordings below (image copying, stream resampling, Python/Unity read verification; thesis Sections 6.1.1-6.1.2 and 6.2) no longer have a hidden page (deleted in round 4, D-127); the recipes are kept for reference. The optional live-camera proposal is thesis Sections 8.4-8.5 and Appendix B (formerly Q&A page 48, deleted). The two supplemental technical animations (media/memory_records.gif/mp4 and media/frame_journey.gif/mp4; thesis Sections 6.1.1-6.1.2) are no longer linked from a deck page (formerly Q&A pages 46 and 51, deleted). Use the [current video index](committee_materials/unified_revision/VIDEO_INDEX.md) and [hash/source contract](committee_materials/unified_revision/media_contract.json); the earlier bank_revision and axes_revision collections and the 76-page and 75-page media remain preserved.

## Rebuild current media

The supplied movies are sufficient to build the PowerPoint without Unity or camera hardware. The active collection references 20 unchanged earlier entries (including page 25, file stem p41) and four unified-layout entries for pages 12, 13 and 14 (the fourth, shoulder swing, was round 3's Q&A page 76 and is retired in round 4, D-130; replacing the round-1 eight-page unified layout for the old pages 13-20). Do not run the historical axes_revision_docs.py or bank_revision_build.py to overwrite the current guides or bindings: bank_revision_build.py rebinds the earlier bank_revision contract, whose producer hash no longer matches the version-2 bank_kinematics.py.

    /home/luo/anaconda3/bin/python presentation/defense_2026/anim/unified_revision_build.py
    /home/luo/anaconda3/bin/python presentation/defense_2026/build_deck.py

The assembler verifies the unified source audit, both media audits and every producer report before binding the current collection. It does not run inference, render Unity or encode movies.

Full regeneration of the eight bank lessons additionally needs the managed recordings, detector model and temporary RGB cache. Each command below writes presentation-only outputs; the bags and frozen methods remain read-only. Regeneration requires new report and visual acceptance bindings before replacing a delivered movie. Details are in [bank_processing/README.md](bank_processing/README.md).

    /home/luo/anaconda3/bin/python presentation/defense_2026/anim/bank_axes_kinematics.py --extract
    /home/luo/anaconda3/bin/python presentation/defense_2026/anim/bank_axes_kinematics.py --build
    /home/luo/anaconda3/bin/python presentation/defense_2026/anim/bank_kinematics.py --build
    /home/luo/anaconda3/bin/python presentation/defense_2026/bank_processing/check_unified_sources.py
    /home/luo/anaconda3/bin/python presentation/defense_2026/bank_processing/check_unified_media.py

The frozen overlay checker separately enumerates RGB and supplies a diagnostic visualization. Exact inference-frame correspondence instead comes from inference_frame_map.json. The full recording behind the old page 20 (observability, now folded into page 13) fails its hand-window precondition; the explicitly selected 28-208 interval passes and is carried into page 13. This is selection of an explanatory window, not repair of the full recording's failed result.

The corrected page 25 (file stem p41) capture is documented in [the capture guide](unity_capture/README.md). It replays archived packets and archived geometry and is unchanged by the unified revision. Thesis Section 6.1.2 (formerly Q&A page 66) and main page 31 and all earlier source media remain unchanged. HANDOVER.md asked to preserve the five films of the earlier bank revision; the four old page 17-20 films (bank_revision_v2) were superseded in round 1 because the author asked for the unified layout on 2026-09-24. In round 2 the old pages 13-16 (bank_axes_revision) and 17-20 (bank_revision_v2) are both superseded by the new unified_four pages 12, 13 and 14 (the fourth, page 76's shoulder swing, retired in round 4, D-130); their files remain preserved in committee_materials/bank_revision, bank_axes_revision and bank_revision_v2 respectively. Review reports bind final movies, clocks, numeric projections and preserved originals. PDF posters do not establish PowerPoint playback.

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

## Record the three technical placeholders

Use an existing recorded bag with its matching calibration for these implementation demonstrations. Label the input RECORDED BAG. Close other V2 sessions first: the launcher recreates shared-memory regions and uses fixed dump paths. Preserve existing `v2/output/v2_*_dump.csv` files before a new run. Save each new run under a unique presentation session directory. Do not modify frozen V1/V2/Unity files. A debugger can observe the original implementation; any copied instrumentation harness must live in the presentation track and be labelled as such.

A future launch template is shown below. Replace both angle-bracket paths before running it; this is not a command that was run for the delivered deck.

    /home/luo/anaconda3/bin/python v2/integration/run_v2.py \
        --source bag --bag <existing-recording.bag> \
        --calib <matching-scene-calibration.json> \
        --object-recovery --plausibility-gate --display-lpf --dump --profile

Open the intended Unity rig scene only after `/dev/shm/integrated_scene_v2` and `/dev/shm/aruco_scene` exist. If Play started too early, stop and restart it after the files exist. Use the shared ring viewer rather than opening the camera in another process:

    /home/luo/anaconda3/bin/python v2/common/ring_viewer.py

Arrange large, readable watch values, the camera view and Unity Game view. For a stepped/debugger capture, label it STEPPED EXECUTION; stopping a process changes the schedule and cannot support a throughput or latency claim.

### Thesis Section 6.1.1: image publication and copying (formerly Q&A page 68, deleted, D-127)

1. Open `v2/common/shm_ring.py` at `FrameRingWriter.write` and `FrameRingReader.fetch`. In the writer, watch publication count, slot, frame index and sequence. In the actual consumer, watch the requested publication `c`, slot, `s0`, `s1` and decoded frame index.
2. Show the global header separately from the selected slot. At 640x480, the slot has 32 header bytes, 921600 colour bytes and 614400 depth bytes. Capture the actual stream resolution rather than assuming it.
3. Step the writer through odd sequence, metadata/payload and even commit. A consumer that encounters odd or changing sequence retries. Avoid claiming that an uninstrumented other process read the same frame.
4. In `fetch`, show the colour/depth memory-map slices producing local bytes, then the sequence/frame verification. The arrays are constructed from those copied bytes. Show their shapes and local buffer ownership; the shared source remains present.
5. Record a successful accepted read. If a rejection is also demonstrated, show the actual changed/overwritten condition. Preserve the uncut trace and actual values.

Use an editorial recording target of 35-45 s and save the cut as `media/new_recordings/p30-Shared_Image_Copy_Execution.mp4` with a PNG poster. The recording must visibly expose real copy/verify state; a terminal containing only hand-typed byte counts is insufficient.

### Thesis Section 6.1.2: independent buffers and resampling (formerly Q&A page 70, deleted, D-127)

1. Open `v2/integration/v2_integrate.py` at the `pbuf.add`, `obuf.add`, `pbuf.emit(tau)` and `obuf.emit(tau)` calls. Watch each source frame/time and each buffer independently.
2. Choose one actual output tick. Show `tau`, then returned person indices `pf0/pf1` and object indices `of0/of1`, including the stream states. The two brackets need not have identical indices.
3. Show one actual output value after resampling. State whether the sample was exact/near, interpolated, held or blended. Positions, person angles and object rotations follow different interpolation rules.
4. Step to `out.write` and show the fresh tick/time, masks, flags and tags. The optional display smoother can change outgoing person values after the analysis dump, so distinguish `disp_pelvis/disp_angles` from dump values if that option is enabled.
5. Show the accepted new tick in Unity. A debugger pause may alter the current state; report what actually occurred rather than scripting an interpolation that was not observed.

Use an editorial recording target of 35-45 s; save `media/new_recordings/p32-Temporal_Merger_Execution.mp4` and poster. Keep the raw dumps and selected tick/indices. A visualization of old CSV fields is supplementary data replay, not a recording of the original memory operation.

### Thesis Section 6.2: an overlapping Python write and Unity read (formerly Q&A page 72, deleted, D-127)

1. In Python, identify `PSI2Writer.write` in `v2/integration/v2_integrate.py`: odd sequence, packed payload assignment, even sequence. In Unity, attach a C# debugger to `IntegratedSceneReceiverV2.ReadIntegrated` and watch `attempt`, `seq0`, the second sequence, tick and return result.
2. First record an ordinary unchanged-even read and a valid new tick reaching `Update`. This establishes the accepted path.
3. For a controlled overlap, pause Unity after its first even sequence read while the independent Python writer publishes another record. Resume to the final sequence check and record the mismatch/retry. Use the actual sequence values; they need not be 10/11/12. Mark the sequence as deliberately induced with debugger stepping.
4. If demonstrating an odd start, show that the reader skips payload reads. If claiming all retries failed, capture all three attempts and the false return, followed by unchanged displayed transforms. Otherwise narrate that branch as code behaviour, not an observed event.
5. Resume and show a later accepted new tick. The reader does not clear shared bytes, acknowledge the writer or zero the avatar on failure.

Use an editorial recording target of 45-55 s; save `media/new_recordings/p34-Python_Unity_Concurrent_Access.mp4` and poster. Keep the uncut screen capture and trace. A controlled interleaving illustrates the implemented consistency check; it does not establish natural race frequency or a formal guarantee under arbitrary CPU ordering.

## Optional instrumented replacements

The current grip/wrist/fallback recordings have useful but limited roles. To strengthen them later:

- For page 18, expose holding tests, five-frame confirmation, episode ID, clean-observation count and reset. Distinguish retrospective offline entry/exit from causal confirmation. Existing context is not that state trace.
- For the wrist-loss context material (thesis Section 6.1.2; formerly Q&A page 66), display measured wrist, offered object-derived target and final reconstructed wrist separately, with source frame/state. Do not infer target use solely from a moving avatar.
- For page 21, retain the deliberate-mask label unless a new natural-occlusion recording and per-frame states actually support a replacement.

## Optional live-camera demonstration (thesis Sections 8.4-8.5 and Appendix B; formerly Q&A page 48, deleted, D-127)

Prepare a checked calibration for the actual camera pose, physical marker sizes and scene. An old bag's calibration is not transferable after the rig moves. The existing calibrator imports marker dimensions; inspect them against the prints. Preserve previous fixed-name V2 dumps, and choose unique paths for the new bag, logs and capture.

A future live launch template is:

    /home/luo/anaconda3/bin/python v2/integration/run_v2.py \
        --source live --calib <checked-calibration-for-this-rig.json> \
        --record <new-session-source.bag> \
        --object-recovery --plausibility-gate --display-lpf --dump --profile

Only the capture broker should own the physical camera. Display its shared ring in the viewer. Start Unity after the combined and static scene records exist. Confirm both views update, then record 20-30 s of right-hand movement, handover and left-hand continuation. Keep source identifiers readable. If the two views are not exactly pairable by source index/time, label them simultaneous visual monitoring.

Stop the recorder, Unity and launcher cleanly, preserving the bag, actual calibration, logs, all dumps and uncut footage. Unity Stats is a render-rate readout, not camera rate or dropped frames. Leave the slide labelled UNRECORDED AND UNVALIDATED until the footage and every stated claim are reviewed. The current thesis does not establish a complete validated live-camera session.

## Screen recording and file checks

On X11, confirm display and monitor geometry. This example captures a 1920x1080 rectangle at the top-left of display `:0`; change it to the actual arrangement and use a new output path.

    ffmpeg -f x11grab -video_size 1920x1080 -framerate 30 -i :0.0+0,0 \
        -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p \
        -t 30 presentation/defense_2026/media/new_capture_raw.mp4

The command has no audio input. Preserve the uncut original before trimming. Export silent H.264 MP4 with yuv420p; its pixel dimensions must describe the actual captured area, not an invented resolution. Check a replacement before embedding:

    ffprobe -v error -show_entries stream=codec_name,width,height,pix_fmt,r_frame_rate \
        -show_entries format=duration,size -of default=noprint_wrappers=1 \
        presentation/defense_2026/media/new_capture_raw.mp4
    ffmpeg -v error -i presentation/defense_2026/media/new_capture_raw.mp4 -f null -

Save a PNG poster and provenance containing source date, input type, source interval, crop/retiming, calibration/rig conditions, hashes and supported claims. Update the content JSON media declaration and source notes only after review, then rebuild and validate the deck. Keep evidence boundaries on the slide or in the narration.

## PowerPoint rehearsal

Copy the PPTX alone to the defence computer. Play every embedded clip and GIF in slideshow mode, including the hidden topic-page material (typed by slide number, D-128). Check poster, startup, repeat behaviour, navigation and readable labels from an audience seat. A PDF and a successful media decode do not test the presentation host. Use an MP4 alternative or static poster if a GIF does not animate reliably.

The current fuller draft exceeds the initial 20-minute target by design. Use the current speaker notes for an aloud rehearsal, then select the shorter defence sequence using the latest cutting guide. Include real clip playback and pauses in that timing; the media durations alone do not prove the delivered talk length.

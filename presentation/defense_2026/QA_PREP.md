# Thesis defense: technical question preparation

Currency note (2026-10-08): This guide's 39-main/14-hidden slide numbering
belongs to a retired presentation. The answers and original source/page
references below are retained as historical preparation, without remapping
or a new source review. Current hidden-slide navigation is documented in
the English outline and QA guide listed in [README.md](README.md).

This guide is grounded in final Thesis V9 and accompanies the chapter-ordered defense presentation. Pages 1-39 form the main presentation. Pages 40-53 are 14 self-contained hidden topic pages and are excluded from its duration; there is no navigation index, and each is reached by typing the slide number (D-127, D-128). Metric back-projection is thesis Appendix D, Eq. D.2 (formerly page 53, deleted); the six recorded/reconstructed natural-failure pairs with visible discrepancies are thesis Figures 7.5-7.6 and Section 7.4 (formerly pages 55-60, deleted; the summary remains on main page 30). The full deck has 53 pages. The author requested fuller material first; timing is an editable rehearsal plan rather than a 20-minute limit. All presentation-page references below follow the round-6 revision (2026-09-28); thesis section and printed-page references remain separate.

Begin with the methodological definition or assumption, then give the evidence and its limit. If a question needs an experiment the thesis did not perform, say so and describe the experiment that would answer it.

Source: writing/v9/Thesis_V9.pdf. Main-text printed page p is PDF page p + 14. Appendix H is printed H1-H2, PDF pages 162-163. Final Chapter 9 has no numbered subsections.

## Navigation by question category

Category | Related presentation pages
--- | ---
Clarifications | Main 11, 18, 30-31; thesis Sections 7.1-7.4 (references), 5.3-5.5 (frames), Appendix D (back-projection), 2.3/2.6 (occluding surface), 5.3 (Camera')
Technical understanding | Main 12-14 derivations, 20-21 elbow, 24 scene/rig; thesis Sections 5.5 (elbow circle), 5.3 (grasp offset), 6.1.1-6.1.2 (record fields), Appendix H (verification), 3.2-3.3 (root angles), 5.5 (elbow circle derivation), 6.1.1-6.1.2/6.2 (memory execution), 3.3 (shoulder swing; film retired, D-130)
Validity of assumptions | Main 30; thesis Sections 7.2 (endpoint lengths), 7.4.2 (labels), 5.3 (grasp), 2.6 (hips), 2.6 (hip-depth ambiguity), 2.3/2.6 (occluding surface)
Why this approach | Main 33 causal processing, 38 contributions; thesis Sections 5.5 (geometry), 5.3-5.5 (calibration), Appendix H (verification)
What if something changes | Main 21 fallback, 38 future work; thesis Sections 5.3 (grasp), 5.3-5.5 (camera pose), 5.6 (guards), 8.1-8.2/8.4-8.5 (timing)
Possible extensions | Main 38 future work; thesis Sections 8.4-8.5 and Appendix B (proposed live validation)
Main contributions | Main 38; thesis Sections 7.1-7.4 (references), 7.3.2 (model versus rig), 7.4.1-7.4.2 (recovery), Figures 7.5-7.6 (visible discrepancies; also shown on main page 30)

## 1. Clarifications

Q1.1. Which quantities and coordinate-frame origins does the method reconstruct?

A. It reconstructs the torso, both arms, and a marked cube in one calibrated metric scene. The body branch stores three root angles and five joint coordinates per arm, for thirteen angles. The two segment directions determine four independent arm angles; the additional elbow coordinate is retained for generality. The torso frame L24 originates at the right hip. Shoulder frames L12/L11 inherit its orientation, while elbow frames L14/L13 carry the solved shoulder rotation. The saved pelvis position is the post-recovery hip midpoint, not the L24 origin; it must not be used to anchor an axis labelled L24. The wrist is a tracked point without an observed orientation. A separate marker branch tracks the cube. The recovery layer reads the object pose through a one-way link and labels outputs as measured, held, or constrained.

Source: Sections 3.2-3.4, Chapter 5 opening, Sections 6.1-6.3, and Section 10.1; eval/failure/recovery_core.py:214-221. Related pages: main 38; thesis Sections 5.3-5.5 and 6.1.1-6.1.2.

Q1.2. What does the 0.53-2.83 cm object result measure?

A. It is the range of absolute endpoint-length errors in the six object segment comparisons across the rail and handover recordings. The reference is tape-measured separation of marker-center positions. It is not a per-frame position error, a trajectory error bound, or an anatomical accuracy result. The physical route was not registered into the reconstruction frame.

Source: Tables 7.1-7.2, pp.88 and 91; Section 7.2, pp.86-87.

Q1.3. What do measured, held, and constrained mean?

A. Measured is the saved solver's accepted-input state after preparation; it is not proof that every required raw sensor measurement existed on that frame. Held means the previous value is retained. Constrained means the output uses a rebuilt landmark or a limited angular change. These are output provenance states, not confidence probabilities. A twist can be held even with visible landmarks because it is unobservable near a straight elbow; rate limiting can constrain an otherwise measured angle. Moving model axes inherit the saved group state rather than a visibility score. A short gap can be interpolated before solving: R7 frames 705-707 have missing raw right-wrist depth and a filtered missing-interpolated flag, while the saved right-arm groups remain measured. Those frames do not demonstrate that object-assisted recovery was invoked. Axes computed from input landmarks are labelled separately and cannot imply a valid solved pose during torso rejection. The merger also has separate stream statuses: measured, interpolated, held, or blended.

Source: Chapter 5 opening, p.48; Section 6.1.2, p.71; v1/kinematics/occlusion_ext.py:165-172 and :780-857; v1/mediapipe/filter_landmarks.py:31-32; saved R7 raw/filtered landmark CSVs and recovery_r7/angles_recovery.csv, frames 705-707. Related pages: main 18 and 31; thesis Sections 7.3.2, 6.1.1-6.1.2 and 6.1.2/6.2. Receiver spheres in the archived and fresh Unity replays mean non-measured and do not separate held from constrained. Thesis Section 6.1.2 (formerly Q&A page 66) and main page 31 additionally show saved recovery tags as pre-display provenance; the original display smoother acts on those shown angles. Page 25 (file stem p41) instead applies the archived integrated packets directly and exposes only their original binary validity; it does not import newer recovery tags.

Q1.4. Was this a complete live-camera demonstration?

A. No complete live-camera session was validated in the thesis. The causal architecture replayed all 900 rail frames at about 29 fps without drops on the documented workstation. That supports feasibility under causal processing. The recording source, start-state assumptions, and calibration still need a complete sensor session, and sensor-to-screen latency was not measured.

Source: Sections 8.4-8.5, pp.114-115; Appendix B. Related pages: thesis Sections 8.4-8.5 and 8.1-8.2.

Q1.5. Are the recording and the explanatory data actually synchronized?

A. On the current filter and grasp pages, both views use the same archived source frame and timestamp on every output frame, including shared pauses. That is display correspondence, not proof of online availability: offline filters can use future samples, and the wrist target is a derived input rather than anatomical ground truth. The frame-flow page instead visibly freezes source 533 while illustrating operations from saved records. Its merger also uses adjacent source 532 and emits a new render tick; the animation is not a captured scheduler or latency trace.

Source: media/provenance/filter_*_sync_frames.csv, media/provenance/matched_evidence.json, review/FILTER_SYNC_MAPPING_CHECK.json, unity_capture/r7/capture_manifest.json, unity_capture/r5_archived/capture_manifest.json, bank_processing/BANK_SOURCE_CHECK.json, and V9 Section 6.5/Table 6.2. Related pages: main 9, 19, 20, 23 and 33; hidden pages 44-45 and 47-48, and thesis Sections 6.1.1-6.1.2 (formerly the original frame overview page). Thesis Section 6.1.2 (formerly Q&A page 66) and main page 31 use explicit source-frame joins and R7-specific rig dimensions. Page 25 (file stem p41) uses the archived R5 packets and archived rig dimensions, without another solve or smoothing pass. Its binary validity comes from those packets. Their explanatory model axes are captured in the engine; historical raster identity and anatomical accuracy are not claimed. The required page 25 application checker retains 7 passing assertions and one failed historical error-concentration assertion; direct packet and rig application pass separately. Pages 12-14 are newly processed bank examples: logged actual inference-image hashes, hardware IDs and absolute times establish the shared source identity; the retired swing film (p14, thesis Section 3.3, D-130) shares the same provenance but is no longer embedded on any page. The lower views show local calculated quantities, with visible filter-repair flags. Page 21 retains the controlled fallback qualification. The preserved original record and overview animations (media/memory_records.gif/mp4, media/frame_journey.gif/mp4; thesis Sections 6.1.1-6.1.2) are no longer linked from a deck page.

Q1.6. Why are green hip points visible when the torso geometry is rejected?

A. The recording on page 18 is an input overlay, not a reconstructed pose. Its original drawing preserves returned torso points without applying the torso failure mask. A hidden joint can still receive a two-dimensional estimate, and an aligned depth sample can land on an occluding surface. The added status strip reports the saved torso rejection from frames 651-758. At frames 705-707 the right wrist has high visibility but no usable aligned depth. The short gap is interpolated before the offline solve, which explains why the later saved right-arm state can still read measured. Visible dots and that later state therefore do not establish a same-frame raw three-dimensional measurement. The torso rejection is a separate geometric test.

Source: presentation/v9/anim/video1_overlay.py; eval/output/recovery_r7/failure_mask.csv; v1/mediapipe/output/recording_20260909_000024_landmarks_raw.csv; Thesis Sections 2.3, 2.6 and 5.2. Related pages: main 8 and 18; thesis Sections 2.6 (hip-depth ambiguity and torso preparation), 2.3 (occluding surface) and Appendix D (back-projection).

Q1.7. What exactly is the approximately 5 cm recovery example?

A. At loop frame 1890, the final recovered forward-kinematic wrist is 5.01 cm from a manual right-watch feature; the plain-solve endpoint is 14.03 cm away. The raw wrist is still available. The elbow fails the input test, and the arm-level mask removes both elbow and wrist before recovery. In the picture, the white cross is the offered object-derived target, which differs from the final chain endpoint. The comparison concerns a manually labelled visible feature, not an independently measured anatomical wrist centre.

Source: Figure 7.9, Table 7.9 and Section 7.4.2; eval/reports/r5_recovery_labeled.json, frame 1890; eval/failure/recovery_core.py. Related pages: main 30; thesis Sections 7.1-7.4 and 7.4.2.

Q1.8. Did moving L23 and L24 upward correct the measured hip positions?

A. No. The upward points (thesis Section 2.6, hip-depth ambiguity; formerly Q&A page 64) are a manual anatomical-location illustration requested for explanation. The photograph is unchanged, and those new display positions have no assigned measured depth. The original projected detector points on the block (thesis Sections 2.3/2.6; formerly Q&A page 73) are preserved. The implemented preparation instead tests the saved three-dimensional inputs and uses accepted depth and direction memory when those inputs fail. The illustration must not be presented as recorded detector output or a measured correction.

Source: Thesis Section 2.6; media/provenance/matched_evidence.json, R6b frame 533; the hip-depth-ambiguity illustration's explicit display annotation (thesis Section 2.6; formerly Q&A page 64). Related pages: thesis Section 2.6 (torso preparation, hips) and 2.3/2.6 (occluding surface).

## 2. Technical understanding

Q2.1. Why can you not recover wrist orientation from these landmarks?

A. The landmark set supplies point positions, and forearm pronation can rotate the wrist without moving any point in that set. The two segment directions determine four observable arm degrees of freedom, not all seven anatomical rotations. Additional orientation information or landmarks beyond the wrist would be needed. A displayed model forearm frame at L16/L15 follows the reconstructed chain; its axes are not a measured anatomical wrist orientation. Near a straight elbow, the perpendicular component becomes small. The geometric solver marks twist unobservable when that component vanishes; the recovery layer also has a separate flexion-based hold. All selected samples on pages 13-14 still have twist_ok true; page 13 presents the exact zero-component limit as part of the twist discussion (the former observability page is folded in), not an observed hold. Page 13 rotates the forearm vector to undo swing while retaining the thesis L12 label; page 14 uses the completed L14 frame.

Source: Sections 3.3.1, 3.4.3-3.4.4, 5.5, and 6.3 (printed p.75); v1/kinematics/occlusion_ext.py:815-828 (15-degree hold and 25-degree release). Related pages: main 13; thesis Section 5.5.

Q2.2. If the wrist and shoulder are known, why is the elbow not unique?

A. The elbow must lie on a sphere around the shoulder and another around the wrist. Their intersection is generally a circle. One swivel angle remains unobserved, so the remembered upper-arm direction selects one point. In the thesis's worked example, the circle radius is 0.06 m; the free turn can move the elbow about 12 cm. That example is separate from the illustrative dimensions on the presentation's prior-selection page. This choice is inferred, not measured.

Source: Section 5.5, equations 5.8-5.12, pp.58-61; Section 5.6, p.64. Related pages: main 20-21; thesis Section 5.5.

Q2.3. How can the branches read memory while capture writes it?

A. Capture is the only writer of an eight-slot frame ring. A sequence counter distinguishes a stable slot from one being written, and readers copy the images into process-local storage and verify the counter and frame index. Capture does not wait for slow readers, so an overloaded reader can lose whole frames. The merger decodes new person and object records into separate timestamped buffers. It resamples their values and packs a new 112-byte record with a tick index, render time, poses and status fields; it does not concatenate the 84-byte and 44-byte input records.

Source: Sections 6.1.1-6.1.2, Figures 6.2-6.3, pp.67-71; v2/common/shm_ring.py:230; v2/integration/v2_integrate.py:322 and :410. Related pages: thesis Sections 6.1.1-6.1.2. The detailed memory animations (thesis Sections 6.1.1, 6.1.2 and 6.2; formerly Q&A pages 68, 70, 71 and 72) and the record-field reference (thesis Sections 6.1.1-6.1.2; formerly Q&A page 46) are schematic; their dwell times are not measured execution times. The full detailed master is supplied separately as [GIF](media/memory_records.gif) and [MP4](media/memory_records.mp4). The original frame overview is also retained as [GIF](media/frame_journey.gif) and [MP4](media/frame_journey.mp4). The global image header stores geometry and intrinsics separately from each image slot.

Q2.4. How were the kinematic equations verified?

A. Six synthetic datasets inject known angle trajectories, generate landmarks, and compare decoded angles with those injected values. Agreement is to arithmetic precision for the tested trajectories. A separate check uses 77 rail frames with all eight landmarks measured. These tests verify the geometric calculation, not the landmark detector, depth sensor, object pose, anatomical accuracy, or recovery during missing observations.

Source: Appendix H, Table H.1 and Sections H.1-H.3, PDF pp.162-163. Related pages: thesis Appendix H.

Q2.5. What happens if Python writes while Unity is reading the pose record?

A. Unity applies the pose only after its sequence check succeeds. Python marks a write with an odd counter and commits with the next even counter. If Unity starts with 10, reads fields while Python changes 11 to 12, and finishes with 12, it rejects those local values because the counters differ. It can retry immediately, up to three attempts in that Update. A stable 12-to-12 read is accepted if the magic is valid; a new tick is then applied. If all attempts fail, Update returns before either pose is applied, so the previous scene transforms remain until a later successful read. Unity does not clear or acknowledge the shared fields.

Source: v2/integration/v2_integrate.py:109-117; Unity/Assets/Scripts/IntegratedSceneReceiverV2.cs:187-228 and :348-368. Related pages: thesis Sections 6.1.1-6.1.2 and 6.2 (the dedicated read-verification and race animation, formerly Q&A page 72). This explains the implemented sequence-counter protocol; it is not a formal proof for arbitrary CPU memory ordering, nor a new concurrency stress-test result. Python's pose-record reader allows four attempts, while the image-slot reader and Unity receiver allow three.

Q2.6. How do the coordinate maps connect the object, body and scene?

A. The predicted wrist in equation 5.7 is expressed in Scene coordinates. Before the camera-frame elbow construction in equations 5.8-5.12, apply the fixed inverse scene-anchor transform to that target. Both shoulder and wrist must be in the same Camera' frame used by the arm geometry. A point transform includes translation; rotating the target alone would be incorrect. The slide equations retain the thesis frame labels so that this conversion is explicit. Camera is right-handed; Camera' flips only y at the same optical origin and is left-handed. The world-to-Unity swap S changes both bases of an object orientation, giving S R S; its marker axes become MappedMarker. The body anchor changes only the reference basis, so it left-multiplies the chain rotation. Conjugating that body chain would be incorrect. Gravity alignment and floor placement together define Scene, with no additional named intermediate frame. Red x, green y and blue z identify axes consistently; the frame label determines their physical meaning.

Source: Section 5.3, p.53 (fixed Scene/Camera' mapping); Sections 5.4-5.5, equations 5.7-5.12; Sections 6.2 and 6.4 (display-frame chain). Related pages: main 20-21 and 24; thesis Sections 5.5, 5.3-5.5 and 5.3.

Q2.7. What do the individual filters do, and why show them separately?

A. Hampel testing identifies unusually large local residuals and leaves missing values. Short-gap interpolation estimates only bounded interior gaps from their endpoints. Butterworth smoothing attenuates rapid variation; the offline forward-backward pass needs future data. Savitzky-Golay fits a local polynomial, while a median filter selects the middle value after sorting the window values. One Euro adapts its smoothing with estimated motion speed and can operate causally. These plots isolate one operation on recorded samples; they are not a comparison of complete pipelines or new accuracy measurements. Gap-filled and smoothed values remain estimates.

Source: Section 2.5, Appendix F, frozen v1/mediapipe/filter_landmarks.py and media/provenance/filter_demo_saved_parameters_r6b.json. Related pages: main 9 and 33; hidden pages 44-45 and 47-48. The Appendix-F One Euro setting shown here differs from the separate V2 command-line default; do not describe it as a universal runtime configuration.

Q2.8. What does deprojection add, and what can it get wrong?

A. The calibrated camera intrinsics and a pixel's metric depth convert an image landmark into a camera-frame point. The depth is from a visible surface near that pixel. It does not establish that the surface lies at the anatomical joint, which is why hip depth can be wrong even with a confident image landmark. The unshifted detector projections from source frame 533 show the measurement problem (thesis Sections 2.3/2.6; formerly Q&A page 73). The hip-depth-ambiguity illustration (thesis Section 2.6; formerly Q&A page 64) separately identifies a manual torso-location illustration. The exact back-projection equation is thesis Appendix D, Eq. D.2 (formerly the Q&A appendix, deleted in round 4, D-127).

Source: Sections 2.3 and 2.6; Section 3.5; Appendix D, Eq.D.2, printed D3/PDF 147. Related pages: thesis Sections 2.6, Appendix D and 2.3.

Q2.9. What defines the torso axes and the zero-angle T-pose?

A. Shoulders 11/12 and hips 23/24 bound the rigid torso representation. The coordinate basis itself uses the hip line 23-to-24 and the vector from right hip 24 to right shoulder 12, with origin at 24. The fourth corner helps identify the full torso in the recorded person; it is not an additional independent basis input. Landmark 13 is the left elbow, not a shoulder. In the sensor-facing T-pose, all arm angles are zero, but the root orientation in Camera' is diag(-1, 1, -1), with Euler angles (0, 180, 0). Root x points to the subject's right, y up the trunk and z out of the chest. The right arm lies along local +x and the left along local -x. Zero arm angles therefore do not mean an identity camera-to-root rotation.

Source: Section 2.3 and Sections 3.2-3.3, Eqs.3.7-3.14 and Figure 3.5 (printed pp.27-30); the R7 landmark metadata and matched_evidence.json. Related pages: main 11-12; thesis Section 5.3.

## 3. Validity of assumptions

Q3.1. Is a fixed hand-object offset realistic?

A. It is conditional on the grasp staying sufficiently rigid, and the loop recording shows violations. The left-hand offset observations have standard deviations of 7.0, 2.7, and 6.3 cm across the mapped marker axes. The recursive estimate also lags a changing grip and freezes during missing wrist observations. An accurate current object pose can therefore carry an inappropriate offset.

Source: Section 5.3, pp.55-56; Section 7.4.2.

Q3.2. Can you assume the torso is measured while the desk hides the hips?

A. That is a modeling assumption supported by a depth-preparation stage, not an independently measured anatomical fact. The preparation rejects a measured hip on 858 of 900 rail frames. A single rejected point retains its camera ray and uses remembered depth or the stated shoulder-depth fallback. Whole-pair repair restores calibrated width and can move the endpoints away from those rays. A lost root remains outside the recovery layer's scope, and its constrained state should remain visible.

Source: Section 2.6; Section 5.1, p.49; Section 8.3, p.113.

Q3.3. How trustworthy are the manually labeled wrists?

A. They are visible-feature references with important uncertainty. One annotator marked a bracelet on the left and a watch on the right; these features are not anatomical wrist centers. Clean-frame median label separations are 4.5 cm left and 2.1 cm right. Occlusion results use only 16 left and 4 right frames, excluding fully hidden features. Repeated-click and depth uncertainties were not quantified.

Source: Tables 7.8-7.9 and Section 7.4.2, pp.102-106.

Q3.4. Are your body lengths and gravity direction independently calibrated?

A. The segment lengths are effective medians of landmark tracks, not anatomical measurements used to fit the solver. The right arm splits into 31.7/20.5 cm on rail and 25.6/25.2 cm on loop, while a direct physical measurement is about 25 cm per segment. Gravity comes from the wall marker's printed up axis; its upright mounting was not measured. Both choices limit the physical interpretation.

Source: Sections 2.2.2 and 6.3; Table 9.1; Chapter 9. Related pages: thesis Sections 2.6 and 5.3-5.5.

Q3.5. Did the matched elbow animation show the solver choosing that circle?

A. No. It uses the same recorded shoulder and object-derived wrist target to show the ideal set allowed by two fixed lengths. The elbow remains measured in this interval, and the saved data do not contain the direction-memory value. Some endpoint pairs also exceed the runtime near-extension guard. The animation therefore shows endpoint ambiguity before safeguards, with no invented selected elbow or claim that an elbow-missing branch ran. Pages 26-27 derive the circle and separately show how a prior selects a point.

Source: Section 5.5, Eqs.5.8-5.12; eval/failure/recovery_core.py; pinned R7 segment lengths; media/provenance/matched_evidence.json. Related pages: main 20-21; thesis Section 5.5.

## 4. Why this approach

Q4.1. Why use one RGB-D camera with printed markers?

A. The research asks what person-object reconstruction and recovery are available from a single consumer-grade viewpoint. RGB-D supplies metric depth, and fiducials provide object identity and pose without an object-specific learned model. The tradeoff is direct: only marked objects are tracked, a visible marker is needed for the recovery constraint, and a single view cannot remove occlusion ambiguity.

Source: Sections 1.1-1.3, 2.3-2.4, and 5.1; Chapter 9. Related pages: main 38.

Q4.2. Why an explicit geometric model rather than a learned replacement?

A. The explicit chain makes the assumptions inspectable, produces a closed-form per-frame solve, and allows verification against injected exact geometry. It also records where measurements are replaced or held. The thesis did not compare this architecture with a learned replacement, so it does not establish that learned methods cannot provide those properties. Learned assistance to the chain is proposed future work.

Source: Chapter 3; Appendix H; Sections 8.2 and 10.2. Related pages: main 38; thesis Sections 5.5 and Appendix H.

Q4.3. Why freeze the scene calibration instead of updating it every frame?

A. A noisy anchor orientation would rotate every reconstructed point, with displacement growing farther from the anchor. The calibration averages the first ten static-marker detections and freezes them to avoid frame-to-frame anchor wobble. This does not remove a fixed calibration bias. It also means the camera must remain fixed after calibration or the transform must be recalibrated.

Source: Section 2.2.2 and equation 2.1; Section 4.1. Related pages: main 8 and 16; thesis Sections 5.3-5.5.

Q4.4. Why change filters for causal processing?

A. Forward-backward Butterworth smoothing and a centered despiking window use future samples. The causal path instead uses a trailing despiking window and a One Euro filter, and bridges only within the merger's available buffer. Causal filtering therefore introduces motion-dependent lag. The same closed-form geometric solve remains usable; the preparation and state updates change around it.

Source: Sections 2.5, 8.1-8.2; Table 8.1. Related pages: main 33; thesis Sections 8.1-8.2 and 8.4-8.5.

## 5. What if something changes

Q5.1. What happens if the hand also covers the object marker?

A. The object cannot supply a current geometric constraint when its marker is lost. The recovery must use available direction memory or hold the relevant angles. On the loop recording, the marker is detected on 2058 of 2099 frames; 40 of the 41 missing detections occur during the two-hand transfer. Every retained manual-label evaluation frame still has a detected object marker, so that evaluation does not establish recovery when both cues are lost.

Source: Sections 5.3-5.4 and 7.4.2, pp.102-103. Related pages: thesis Sections 7.4.2 and 5.3.

Q5.2. What happens if the subject moves faster?

A. That performance is not established by this thesis. Faster motion can challenge the fixed step threshold, the short direction memory, the angle rate limit, and the filtering assumptions. The tested task was deliberately slow. A useful next experiment would vary motion speed while holding the scene and independent reference fixed, then measure both tracking error and missing-data behavior.

Source: Sections 2.5, 4.2, 5.1-5.5, and 8.3. Related pages: main 38; thesis Sections 5.3 and 8.1-8.2/8.4-8.5.

Q5.3. What happens if the camera moves or the marker size is wrong?

A. Moving the camera after frozen calibration makes the old anchor transform inconsistent with new observations. Recalibration is required. An incorrect printed marker size scales the translation recovered by the planar pose solver, so it affects object distances and the object-derived recovery constraint. The thesis's calibrated invariance is not a claim of unrestricted moving-camera operation.

Source: Section 4.1; Section 2.4 and Appendix E; Table 2.1. Related pages: thesis Sections 5.3-5.5.

Q5.4. Would a better landmark detector solve all the remaining problems?

A. It could reduce wrong or missing landmarks, but the amount was not measured here. It would not create observations behind an occluder, observe wrist orientation absent from the landmark set, or make an old grasp offset current. Rendering differences and state initialization would still need their own tests. The appropriate comparison would keep the downstream architecture and reference protocol fixed while replacing the detector.

Source: Chapter 9; Sections 3.4.4, 8.3, and 10.2. Related pages: main 38; thesis Sections 7.3.2, 5.5 and 5.3.

## 6. Possible extensions

Q6.1. What would make the accuracy evaluation stronger?

A. Register the physical route into the calibrated world frame and acquire an independent reference for body and object motion. This would support physical trajectory and orientation comparisons instead of only endpoint lengths, detector agreement, and visible-feature distances. More subjects, grips, and repeated trials would address generalization. Those measurements are future work, not missing values that can be inferred from the current tables.

Source: Section 7.2; Section 7.4.2; Chapter 9 and Section 10.1. Related pages: main 38; thesis Sections 7.1-7.4 and 7.2.

Q6.2. What does a complete live validation need?

A. It needs a real sensor run with verified calibration, correct marker sizes known before detection, a defined initial rest state, and recorded capture-to-display behavior. Log frame IDs, timestamps, branch rates, drops, and joint states while retaining the raw source and uncut capture. Measure sensor-to-screen latency separately using a synchronized observable event. A short demonstration video alone is insufficient to establish these claims.

Source: Section 8.5, pp.114-115. The optional live-camera-validation proposal (thesis Sections 8.4-8.5; formerly Q&A page 48, deleted in round 4, D-127) specifies an optional 20-30 second recording; that duration is an editorial instruction, not an experimental result.

Q6.3. Why add multiple cameras?

A. A second calibrated viewpoint may retain a landmark or marker when the first loses it and can improve observability along a weak viewing direction. Both views could feed observations into the common metric scene developed here. The thesis proposes this extension but does not measure its gains, synchronization cost, or calibration robustness. A controlled occlusion experiment would test the benefit.

Source: Chapter 9; Section 10.2, first proposed direction. Related pages: main 38; thesis Sections 5.3-5.5.

Q6.4. Where could machine learning help without hiding the geometry?

A. A learned model could help judge which recent observations or recovery cues to trust while an explicit chain checks geometric consistency. The thesis proposes using landmark history, pose, confidence, failure flags, and object motion together. That model is not implemented or evaluated here. Its test should include held-out grips and subjects, and should report failure cases as well as average error.

Source: Section 10.2, third proposed direction. Related pages: main 38. Held-out evaluation is a proposed validation design, not a thesis finding.

## 7. Main contributions

Q7.1. What is the central contribution?

A. It is an integrated architecture that reconstructs the torso, both arms, and a tracked object together while exposing measured and inferred output. The object can provide an extra geometric constraint when a landmark fails, and a causal replay path preserves the overall architecture. The thesis characterizes geometric ambiguity and failure conditions under the tested conditions.

Source: Section 10.1; Chapter 9; Section 1.3. Related pages: main 38.

Q7.2. What did the object constraint actually improve?

A. It improved the right-wrist distance to the manual labels in the retained natural-failure set: median 5.2 cm versus 11.4 cm for plain solve and 17.6 cm for hold-last, on four frames. It did not improve the median of the sixteen-frame left-arm set. Synthetic removal also shows joint- and window-dependent tradeoffs. The evidence supports a conditional geometric constraint whose effect varies by arm, window, and evaluated joint.

Source: Tables 7.6-7.9 and Sections 7.4.1-7.4.2.

Q7.3. Which limitations are most consequential for the method?

A. A plausible displayed reconstruction can retain errors caused by measurement and remembered state. For example, offline and causal initialization froze twists about 40 degrees apart and placed the frame-18 wrists 12.0 cm apart. Separately, matched model-to-rig comparisons show additional downstream discrepancy without isolating its cause. Smooth output alone is therefore not evidence of physical accuracy.

Source: Section 8.3, pp.112-113; Section 7.3.2, pp.96-97. Related pages: thesis Sections 7.3.2 and 8.1-8.2/8.4-8.5.

Q7.4. What can you claim about novelty and practical use?

A. Relative to the reviewed systems, the thesis combines upper-body reconstruction, tracked object motion, and recovery from a single RGB-D viewpoint in one scene. That is a scoped literature claim, not proof that no other system exists. The evidence covers one subject and three controlled recordings. It supports feasibility and motivates further work; it does not establish clinical readiness or population-level accuracy.

Source: Section 1.2.4; Chapter 9; Sections 10.1-10.2. Related pages: main 38.

## Answers that must retain their limits

- The 6 mm worked-example elbow comparison uses frame 549 as the reference for frame 560. It is not same-frame accuracy.
- The 1.03 cm recording-wide model-wrist medians do not share the rendered capture's frame populations.
- The 0.4-degree offline-causal elbow difference follows a best five-frame alignment on 174 retained pairs. Neither path is ground truth.
- A two-frame render delay is not a measured end-to-end latency.
- An object-derived wrist target and the final wrist of the reconstructed chain can differ.
- Legacy red spheres mean non-measured. They cannot distinguish held from constrained.
- The archived full handover is Unity-only and qualitative. Its old sizing used a torso override and loop-arm constants. The fresh axes replay uses all five R7 dimensions; neither inherits the separate scored Table 7.4 results. Fresh capture provenance is in unity_capture/r7/capture_manifest.json.
- The matched frame journey uses actual frame/record values, but block order and travel time are explanatory. A saved value is not a captured scheduling event.
- R7 frames 705-707 have a missing-depth source flag. This does not identify a physical occlusion cause.
- The current filter/grasp composites share a source frame across their panels; the earlier separate-context assets remain unsynchronized supplementary material.
- A numerical axes companion is a reconstruction from saved values. Fresh Unity replays additionally log model bases, bone bases, rendered origins and camera matrices from the engine; these are distinct evidence sources. The explanatory axes remain visible through the rig mesh and do not imply anatomical visibility. Direct overlays require the matching frame, origin, orientation and camera projection.
- Axis colors identify x/y/z, not validity. Measured, held and constrained must remain separately labelled.
- The saved pelvis midpoint and the L24 right-hip frame origin are distinct quantities.

## Response when the thesis does not settle the question

"That was not established in this thesis. The result I do have is [the relevant comparison and its conditions]. To distinguish the proposed explanations, I would hold [the confounding factors] fixed and measure [the missing independent reference or controlled intervention]."

Do not invent a numerical prediction, attribute a cause to a stage the evaluation did not isolate, or treat a proposed future recording as completed evidence.

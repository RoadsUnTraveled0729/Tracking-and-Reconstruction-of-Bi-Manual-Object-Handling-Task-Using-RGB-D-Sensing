# Condensed thesis audit follow-up decisions

ID: D-001
Status: SETTLED
Decision: Complete the approved audit follow-up in the condensed thesis and additive evaluation reports.
Why: The user approved the proposed sequence and requested an updated handover; the current manuscript has qualified results but unresolved method and validation details.
Alternatives: Leaving the qualified results without attempting the approved checks would leave the requested work incomplete.
Evidence: User approval in this session; HANDOVER.md at 9fa9de4; MATH_LOGIC_REVIEW.md.
Reversibility: Revert the individual follow-up commits; historical reports and frozen v1/v7 remain available.
Review: Check the new report provenance and the final condensed manuscript.

ID: D-002
Status: SETTLED
Decision: Retain the measured-only twist hold and persistent two-link swivel prior; describe their actual scope.
Why: Changing either policy would change the method that produced the existing results and require a separate regenerated evaluation.
Alternatives: A universal twist hold or enforced swivel-memory horizon is deferred to a new implementation study.
Evidence: Approved recommendation; audit M05/M07 and source checks in audit_evidence/.
Reversibility: Implement and evaluate alternative policies in a separate study.
Review: Check that Chapter 5 distinguishes the bounded direction fallback from the persistent IK prior.

ID: D-003
Status: SETTLED
Decision: Add hip preparation after Chapter 2 filtering; apply the two approved verbatim corrections, sensor-scale display precision and scoped bimanual claims, then trim below 30,000 main-body words.
Why: These edits complete method disclosure while retaining the Chapter 5 arm-recovery focus and the evaluated implementation.
Alternatives: Restoring the full parked torso chapter adds unnecessary detail; removing the hip results would hide an implemented dependency.
Evidence: Approved recommendation; supervisor D2/D5/C38; CONDENSE_BRIEF.md target.
Reversibility: Rebuild from prior builders; exact verbatim replacements will be recorded.
Review: Check the new method subsection, scope language, precision and count report.

ID: D-004
Status: SETTLED
Decision: Report the two recordings' calibrated arm lengths as effective model lengths and leave their difference unexplained; no forced match and no elbow-localisation claim.
Why: The same-side, same-rule diagnostic (audit_evidence/followup/m17_segment_diagnostic.py) reproduces the gap (loop right 25.8/25.5 cm, rail right 32.1/19.9 cm) and rules out rounding and filtering, but no anatomical truth or matched pose exists to name the cause.
Alternatives: Forcing one calibration onto both recordings would change every solved angle of one of them; claiming elbow localisation as the cause would be unsupported.
Evidence: m17_segment_diagnostic.json; HANDOVER.md section 2 (M17).
Reversibility: A future measurement of the subject's arm would settle which calibration is anatomical.
Review: Chapter 6 states both sets beside each other; Chapters 3, 5 and 7 name the lengths as calibrated per recording.

ID: D-005
Status: SETTLED
Decision: The subject's direct arm measurement (user, 2026-09-07: upper arm and forearm both about 25 cm) is stated in the thesis beside the two calibrations; the rail recovery keeps its own calibrated lengths (31.7/20.5 cm) and the avatar keeps the loop lengths; no rerun.
Why: The measurement shows the loop calibration (25.6/25.2 cm rig, 25.8/25.5 cm clean medians) is close to the anatomy and the rail calibration splits the same total (52.2 against 50.8 cm) differently, which is consistent with the elbow landmark sitting farther along the arm on the rail recording. The calibrated lengths are effective lengths of the landmark track; the recovery's two-link construction must be consistent with where that recording's landmarks sit, so forcing anatomical lengths onto the rail solve would move the rebuilt elbow away from the measured one and change every Chapter 7 rail recovery number for no measured gain.
Alternatives: Rerun the rail recovery with 25/25 cm and regenerate Sections 5.6, 6.4, 7.3 and Chapter 9 (a separate study); leave the difference unexplained (superseded by the measurement).
Evidence: User message of 2026-09-07 ("both of my upper arm and lower arm are around 25cm"); audit_evidence/followup/m17_segment_diagnostic.json; the frame 114/700 forward-kinematics check in the Chapter 6 technical verification (rail lengths land 8.8 and 1.1 cm from the measured wrist, rig lengths 9.9 and 2.4 cm).
Reversibility: Rerun with anatomical lengths as a separate study; the pipeline reads the lengths from the offset-fit report.
Review: Chapter 6 Section 6.3 and Chapter 9 Section 9.1 and Table 9.1 state the measurement; D-004 is amended by this entry.

ID: D-006
Status: UNCERTAIN
Decision: Recommend a rail-led Chapter 7 with the loop retained only for a compact natural-failure label study, a short rail recovery result, and no standalone torso-results section; leave supervisor D7-D10 unapproved.
Why: The user requested suggestions after a handover review. Completed labels now support a small case study containing both favourable and adverse outcomes; removing all recovery results would leave Chapter 5 under-supported. The supervisor requests task illustrations, world-frame trajectories and Unity reconstruction as the main results.
Alternatives: Removing the loop completely is possible because rail labels are already complete, but loses the contrasting natural-failure cases. Keeping the full loop analysis conflicts with the requested focus. Treating the advice as approval to rewrite would exceed this turn's advisory scope.
Evidence: Current Chapter_7_Evaluation.docx; eval/reports/r5_recovery_labeled.md and r6b_recovery_labeled.md; eval/reports/r6b_recovery_eligible.md; writing/v7/PROF_COMMENTS_ROUND4.md C34-C42. Detail and proposed reply: CH7_RECOMMENDATIONS.md. Supervisor acceptance is unknown.
Reversibility: No manuscript or experiment changed. Revise the recommendation if the user or supervisor chooses complete loop removal or a new handover recording.
Review: Confirm the desired thesis scope and the meaning of "same Unity". The advice is not a settled D7-D10 decision and no supervisor message was sent.

Amendment: D-007 supersedes D-006's unapproved status after the user's approval.

ID: D-007
Status: SETTLED
Decision: Implement the Chapter 7 recommendations approved by the user, retain the one-handed rail task and compact label comparison, and mark supervisor D10/C42 DONE.
Why: The user said "ok do it based on your suggestion, for D10 mark as done", confirmed that the chapter follows the D10 reply, and then said "ok continue". This authorizes the planned restructuring, figures and captures without another approval round.
Alternatives: Leaving the recommendations advisory is superseded. A new two-handed recording and trails inside Unity are not part of the confirmed implementation; D9's trails interpretation remains unresolved.
Evidence: User instructions in this session; CH7_RECOMMENDATIONS.md; supervisor C30-C42 in writing/v8/PROF_COMMENTS_ROUND4.md.
Reversibility: Revert the implementation commits; park removed chapter content under V8 and retain frozen V7 and all evaluation evidence.
Review: Check the rail-led chapter, the retained positive and negative label results, and the C30-C42 checklist. D10 completion records the user's direction, not a claim that an agent sent a message.

ID: D-008
Status: SETTLED
Decision: Rewrite Chapter 8 around the transfer from the offline pass to the live structure (system design diagram, what changed, what was lost, offline-versus-live frames), with the frame rate and the declared delay as its only measured numbers; park the timing tables and the angle-difference figures.
Why: User direction 2026-09-07 ("chapter 8 should be focus how we transfer the offline to the realtime, and what is the proposed system structure. by doing this what we lost? you should have system design diagram, and give some of the screenshot of the realtime and offline where the accuracy drops clearly. dont mention too much numbers since this will lead to another discussion of how we measure the accuracy").
Alternatives: Keeping Tables 8.2 and 8.3 and the check-suite numbers would reopen the accuracy-measurement discussion the user wants out of scope.
Evidence: CH8_PARKED.md holds the removed material; ch8_compare.json records the chosen windows and frames and the differences behind the figures (twist about 42 degrees apart from frame 25 on; gap onset wrists 8.5 cm apart at frame 548).
Reversibility: Restore the parked sections from CH8_PARKED.md and the builder in git history (commit 2bcaad6).
Review: Check that Chapter 9 no longer quotes the parked Chapter 8 numbers and that the figures show the differences without stating them.

ID: D-009
Status: SETTLED
Decision: Recapture the Unity reconstruction of the rail recording after fixing two display defects in the receiver (held-group spheres placed for the rendering camera; trunk length set per recording from the record's pelvis to the measured mid-shoulder, 0.576 m on the rail recording), show four moments in Figure 7.9 (frames 95, 505, 700, 898) and the same two moments in Figure 6.3, and quote the rendered hand's distance to the measured wrist from the receiver's own log.
Why: The user reported that the red spheres of Figure 7.9 did not imply the pose correctly (2026-09-07). The spheres were pushed 20 cm toward the editor's main camera and so projected off the joints in the sensor view. The recapture then showed the rig's right arm hidden below the drawn desk top on every frame before about 540: the rig's shoulders sat 10 cm below the measured ones because the trunk used the loop recording's 47.9 cm while the rail record's pelvis is the hip-depth-corrected point. Supervisor C37 asked for captures at the task moments.
Alternatives: Painting the spheres out of the old captures (rejected: edits evidence); keeping the hidden arm and explaining it (rejected: the reconstruction is meant to place the shoulders on the measured shoulders, and the receiver already scales the trunk to a measured length); switching the avatar to the rail calibration's arm split (rejected: it moves the hand by about 1 cm only, and D-005 keeps the loop lengths as the anatomical ones).
Evidence: Unity/Assets/Scripts/HeldMarkers.cs, IntegratedSceneReceiver.cs (torsoM, rig joints logged); eval/unity_check/run_unity_capture.py run of 2026-09-07 (899 PNGs); eval/unity_check/check_unity_log.py on the run: right hand clean-frame median 41.1 px, de-biased 7.1 px (was 85.3 and 9.5 with the old trunk); rig upper arm within 0.1 deg of the measured direction, forearm 24.1 deg off on clean frames (held twist); rendered hand to measured wrist 15.2, 12.1, 6.4, 8.7 cm on frames 95, 505, 700, 898 and 14.1 on 114.
Reversibility: git history holds the old captures (writing/v7/figures/src before this commit) and the old receiver defaults; the capture reruns in about three minutes.
Review: Check that Chapter 6 Section 6.3 (proportions paragraph, sphere paragraph, Figure 6.3 text) and Chapter 7 Section 7.6 agree with the renders, and that the far-end frame is 898 in Figures 7.3 and 7.9 and the text.

Amendment to D-009 (2026-09-07, later): the user then reported that the desk marker card showed only half in Figures 6.3 and 7.9. Cause: the calibrated card centre lies 0.4 cm below the fitted tabletop plane (origin_above_tabletop_m -0.0038), so the desk slab cut the tilted 5 cm card at its middle. A depth-frame check (eval/labels/frames_r6b f00500 and f00700, along the calibrated gravity) puts the card centre 0.7 to 2.0 cm above the desk around it and the cube's resting centre 3.7 cm above the plane (3.5 expected), so the plane is right at the cube and the card pose is 1 to 2 cm low, within the pose error of a 5 cm marker at 0.55 m. Decision: draw the desk card over the desk slab (Unity/Assets/Shaders/PlateOverlay.shader, no depth test, assigned to marker id 2 only in ArucoSceneReceiver.MarkerPlate; nothing ever stands between the sensor and the desk card) rather than move the card off its calibrated pose or lower the desk (which would float the cube). Chapter 6 Section 6.4 states the overlay and the discrepancy. Captures redone from the same recovery stream.

ID: D-010
Status: SETTLED
Decision: Restore the shared-memory discussion of Chapter 6 in full, bring back the memory block figure (supervisor request of 2026-08-03, present in V5 and V6 as Figure 5.2, dropped in V7) as Figure 6.2 drawn from the live structure's records, and add a worked example that traces one real frame (548 of the rail recording) through the frame buffer, the two records and the merger.
Why: User direction 2026-09-07 ("why we lost our discussion about the shared memory and the memory block diagram? also we should have a example of how the data is managed"). The V8 condensation had cut the sequence-counter walkthrough to one sentence and V7 had dropped the figure. The user also said the 30,000 word goal may be exceeded a little.
Alternatives: Restoring the V6 figure as it was (rejected: it drew the v1 108 byte record; the thesis now describes the live structure's 112 byte combined record and the frame buffer).
Evidence: v2/common/shm_ring.py (frame buffer layout), v2/common/person_shm_v2.py, v1/aruco/send_scene_poses.py, v2/integration/v2_integrate.py (record layouts); v2/output/v2_person_dump_r6b_full.csv, v2_object_dump_r6b_full.csv, v2_integrate_dump_r6b_full.csv (frame 548, tick 548: person interpolated between 547 and 548, object between 546 and 548 with the bridge flag, tags root constrained and right twist held). Figure numbering in Chapter 6 shifts: 6.2 memory, 6.3 frames, 6.4 Unity.
Reversibility: Remove the two paragraphs, the figure and the example; git history holds the shorter section.
Review: Chapter_6_shm_round1.txt (fresh reviewer on the rebuilt chapter).

Amendment to D-010 (2026-09-07, later): at the user's direction the worked example moved out of Section 6.1 into a new closing Section 6.5, Worked Example: Frame 548, and now also applies the maps of Sections 6.2 to 6.4 to the record's numbers (pelvis through flip, anchor, swap and levelling: (0.2, -20.5, 38.9) cm in display axes, (0.0, 74.8, 43.8) cm in the scene; object pose back to the camera frame (-20.7, 15.1, 102.1) cm; right upper arm 0.2 deg and forearm 6.9 deg from the measured directions), with Table 6.2. Section 6.1 states the two uses of shared memory (frames from the capture process to the two branches, never read by Unity; records from the branches through the merger to Unity) after the user asked why frames are transferred at all. Figure 6.2's panel titles name the writer and the readers of each block. The V2 receiver's cube colour is corrected in 6.4: amber marks a pose interpolated across a dropout or blended back, not every interpolation.

Amendment to D-010 (2026-09-07, later still): at the user's direction ("we have 2 systems, should divide them and then explain them one by one clearly") Section 6.1 is split into 6.1.1 The Frame Buffer: Capture Process to the Branches and 6.1.2 The Records: Branches to the Merger and Unity, each with its own memory block figure (6.2 the frame buffer with one slot's byte layout; 6.3 the combined record with the write and read protocols). The chapter's figures are now 6.1 architecture, 6.2 frame buffer, 6.3 combined record, 6.4 coordinate frames, 6.5 Unity reconstruction; no other chapter cites a Chapter 6 figure by number. The builder gained subsection headings (H3).

ID: D-011
Status: SETTLED
Decision: Front matter completed at the user's direction (2026-09-07): the examining committee on the approval page (Dr. Shahram Payandeh, Chair and Supervisor, Professor; Dr. Jie Liang, Committee Member, Professor; Dr. Craig Scratchley, Committee Member, Senior Lecturer; all School of Engineering Science, Simon Fraser University), the abstract rewritten in plainer prose with the same facts and numbers (338 words), the acknowledgements written from the user's draft in the user's voice with the supervisor and committee named, and a Glossary table of 40 terms added as the last front-matter section and listed in the table of contents.
Why: User instructions of 2026-09-07 (committee block supplied verbatim; "make the expression more natural, and more fit to my mood"; "rewrite the abstract make it natural"; "we also should add a terminology word table").
Alternatives: Leaving the supervisor and committee unnamed in the acknowledgements, as the user's draft had them (the names are conventional; the user can strike them). The title stays as the user supplied it, with Bi-Manual, although the evaluated task is one-handed; changing a registered title is the user's call.
Evidence: writing/v8/condensed/scripts/build_frontmatter.py (COMMITTEE, ABSTRACT, ACKNOWLEDGMENTS, GLOSSARY); build_toc.py entries; check_style 0 hits on the front matter. The only placeholder left is the date approved.
Reversibility: git history holds the placeholder version.
Review: The user reads the acknowledgements and the abstract; the glossary definitions follow writing/GLOSSARY.md.

ID: D-012
Status: SETTLED
Decision: Supervisor round 5 (Chapter 4, 2026-09-07) applied to the whole thesis: (a) every printed number stops at two decimals, matrix entries and vector components included, with one set of conventions (rotation entries and unit vectors two decimals, near-zero 0.00; vectors in equations in metres with two decimals; prose distances in centimetres or millimetres with one decimal; session-clock times in seconds with two decimals and offsets in whole milliseconds; where rounded operands no longer give the printed result the intermediate is dropped or only the result stated); (b) Chapter 4 gains Figure 4.1, four camera frames of the task with the detected object marker outlined, its frame O and the world frame W drawn, and the track plot becomes Figure 4.2; (c) at the user's direction the Chapter 6 worked example shows the equation (6.2) calculation, the levelling and the object's inverse path with numbers from a new number source (ch6_numbers.py), which also corrected two double-rounded values (camera position y 43.1 cm, cube x −20.6 cm in the camera frame); (d) at the user's direction the Glossary is written for an engineering reader: p95 and median, the record codes PSF1/PSR2/PSB2/PSB3/PSI2, the landmark numbering, L1 and L2, the T subscript convention, the chordal mean, the hip depth preparation and the PUMA convention in; colour and depth frame, intrinsics, kinematic model, two-link inverse kinematics, rig and avatar, tabletop plane out.
Why: The supervisor's comment ("In the value of the matrices, do not go beyond two decimals ... Same comments for all the numerical values"; "show the images of the experiment") and the user's direction to apply it through the whole thesis; the user's questions of the same day on the Chapter 6 example and the glossary.
Alternatives: Keeping extra digits in the appendix worked examples as calculation displays (rejected: the supervisor's rule names all numerical values); centimetre vectors inside the equations (rejected: Chapters 3 and 5 print vectors in metres with two decimals, so metres keep one convention).
Evidence: writing/v8/PRECISION_ROUND5_CHANGES.md (every old -> new pair); condensed/scripts/check_style.py decimals check (0 hits on every part); writing/v7/scripts/ch4_numbers.py, condensed/scripts/appendix_numbers.py and condensed/scripts/ch6_numbers.py (full-precision sources, rounding checked from them); condensed/figures/ch4_fig_experiment.png; reviews writing/reviews/Chapter_4_round5_round1.txt, Chapter_6_round5_round1.txt, Appendices_C_F_round5_round1.txt.
Reversibility: git history holds the four-decimal builders; the full-precision values stay in the builder comments.
Review: The supervisor reads the rounded worked examples; the user reads the glossary.

ID: D-013
Status: SETTLED
Decision: User decisions of 2026-09-07 night: (a) D9 done as trails inside the Unity scene: make_ch7_trails.py writes the reference path, the tracked marker origin and the model right wrist in display axes, Unity/Assets/Scripts/TrajectoryTrails.cs draws them as LineRenderers under the levelled ArucoWorld node (the frame-indexed trails grow with the stream), the unattended capture eval/output/unity_check_r6b_trails (ignored by git; the record trails.txt and check_unity_log are copied to eval/reports/unity_check_r6b_trails) supplies frames 505 and 898, Figure 7.10 in Section 7.6, the label figures renumbered 7.11 and 7.12; (b) the "[UPDATE FIELDS IN WORD: F9]" note above the contents is dropped from build_frontmatter.py, and the repository PDF is rendered by condensed/scripts/render_pdf.py through LibreOffice's UNO bridge with every index and field updated, so the printed contents and lists carry page numbers; (c) the title stays as the user supplied it; (d) the date approved stays a placeholder.
Why: User message of 2026-09-07 night: "D9 well, do it if you can, the date i dont think i have the answer just leave it title should not changed just keep it, the TOC note should not appear in the formal printed one".
Alternatives: Trails of the rendered rig's hand and cube instead of the Figure 7.8 trajectories (rejected: the supervisor asked to compare the three plots, and the rendered hand differs from the model wrist by the rig lengths, Section 6.3); a plain soffice conversion for the PDF (rejected: it prints the cached field results without page numbers).
Evidence: eval/reports/unity_check_r6b_trails (trails.txt, frames, check_unity_log.txt: 7 pass, the pre-existing left-hand torso check fails as in E-031, right hand de-biased median 7.1 px unchanged), writing/v8/condensed/figures/ch7_fig_unity_trails.png, the field-updated render writing/v8/Thesis_V8_Condensed.pdf.
Reversibility: Remove the figure block from build_ch7.py and the trails file; the Unity script is inert without /tmp/r5_trails.txt.
Review: the fresh Opus reviewer for Section 7.6 was cut off by the session limit on 2026-09-07; the paragraph was checked by hand against the rules; rerun Chapter_7_trails_round1 when usage allows.

ID: D-014
Status: UNCERTAIN
Decision: Recommend a clearer Chapter 7 trajectory presentation with phase-specific Unity panels, a view centred on the task, consistent point definitions, and visible recovery transitions; record the review without rebuilding the manuscript.
Why: The user asked to check the newest Chapter 7 trail result and suggest improvements. The current figure obscures the green track, accumulates the wrist history, and changes the reference and point names between figures. A presentation revision must also disclose discontinuities already present in the saved trajectory.
Alternatives: Smoothing the wrist to make it look better would change the displayed result without explaining its discontinuities. A new tracking-method evaluation exceeds this review. Replacing Unity entirely with plots would omit the supervisor's requested Unity comparison.
Evidence: Reviewed revision d2b910a; Chapter_7_Evaluation.docx and Thesis_V8_Condensed.docx; figures/ch7_fig_unity_trails.png, ch7_fig_wrist_traj.png and ch7_fig_combined.png; scripts/make_ch7_trails.py and make_ch7_wrist_traj_fig.py; eval/gt/eval_rail_scenario.py load_track; committed eval/reports/unity_check_r6b_trails/trails.txt. Detailed findings and verification: CH7_TRAILS_REVIEW.md. The proposed layout has not been rendered or assessed by the user.
Reversibility: This is an advisory record. Revise the proposal after a new capture; current manuscript, figures and experiment outputs remain as reviewed.
Review: Check the proposed Unity layout, marker-origin terminology, reference-line distinction and treatment of real wrist jumps before adopting the revised figure.

Amendment: D-015 supersedes D-014's advisory status after the user's approval.

ID: D-015
Status: SETTLED
Decision: Implement the approved Chapter 7 trail redesign using the existing recording and saved results, without modifying the recorded video, source camera frames, tracking positions or measured results.
Why: The user asked "can you do that?" after the review and then explicitly required that the recorded video remain unchanged because it is the foundation of the thesis. New Unity stills and scientific plots are derivative presentation artifacts; no new recording, trajectory filtering or experiment rerun is needed.
Alternatives: Re-recording or altering the video violates the user's constraint. Changing the solver or smoothing its output would change the evaluated method and exceeds this presentation revision.
Evidence: User approval and recording-preservation instruction in this session; CH7_TRAILS_REVIEW.md; saved eval/reports/unity_check_r6b_trails/trails.txt and eval/output/recovery_r6b/angles_recovery.csv.
Reversibility: Revert the presentation changes; source hashes and the previous figures remain available in the implementation record and Git history.
Review: Compare source hashes before and after, review the new Unity stills at printed size, and confirm that the captions identify marker origin, model wrist, task phases and recovery states.

ID: D-016
Status: SETTLED
Decision: Use carry frames 92-500, lift frames 501-528 and slide frames 529-899 for the phase panels, retaining frames 0-899 in the coordinate history and full-track overview.
Why: These intervals partition the task after the recorded parked span and use the already pinned lift onset and rail arrival. They are presentation intervals, separate from the height-band sample selection used by the existing evaluation.
Alternatives: Reusing the evaluation band's first frame 492 as the lift or slide transition would mix two definitions; selecting quiet intervals would hide output behavior.
Evidence: eval/reports/r6b_waypoints.json track_turns: parked_frames 0-91, lift_begins_frame 501, rail_reached_frame 529, last_frame 899. Each phase ends immediately before the next begins; snapshots use each interval's final frame.
Reversibility: Change the phase metadata and recapture the figures, without changing the evaluation selection or its statistics.
Review: Check each frame interval against the documented task transitions and keep the startup and failure transitions visible in the full history.

ID: D-017
Status: UNCERTAIN
Decision: Use an orthographic oblique task camera, an outline avatar, a dashed dark reference and green/blue/orange trajectories for the new Unity stills; tune only display parameters through visual inspection.
Why: The previous sensor view compresses height and depth and gives the avatar most of the image. An outline preserves scene context without covering the result. Distinct styling separates the reference, object marker and wrist states.
Alternatives: Keeping the sensor view repeats Figure 7.9 and obscures the comparison; red waypoint spheres duplicate the held-group marker meaning.
Evidence: CH7_TRAILS_REVIEW.md and the existing Figure 7.10. Initial display settings are editorial choices, not measured quantities: camera offset direction (0.6, 1.2, -1.5), framing margin 1.2, reference width 0.002 m, trajectory width 0.003 m, waypoint size 0.01 m, dashed-line length 0.02 m and gap 0.012 m, avatar outline opacity 0.18, PNG target 1200 by 800. Colors use the existing Matplotlib tab palette; the reference is dark gray. Changes after inspection are recorded with the final capture configuration.
Reversibility: Adjust the display-only configuration and rebuild the derivative images; the saved coordinates are untouched.
Review: Check visibility, equal framing and readable labels at printed size; no display constant is an accuracy threshold.

Amendment to D-017: inspection replaced the unsupported Standard material with a dedicated URP transparent shader. The final avatar is translucent rather than an outline. The task camera frames the union of the displayed intervals (92-899), with the earlier startup retained in the full-history plot, and the dedicated stills hide the wall slab and use a neutral desk material (RGB 0.92, 0.92, 0.90). Original scene materials are restored after each still. These are display choices under the same UNCERTAIN decision. The saved-stream replayer holds each requested endpoint until its capture record exists, including frame 899; this addresses the observed skipped final frame at loop wrap without changing any saved pose or timestamp.

ID: D-018
Status: SETTLED
Decision: Correct the Chapter 7 object quantity to marker origin in the text and plot labels, place the schematic marker origin on the existing waypoints, preserve all numerical reports, and qualify consistency claims.
Why: The figure builders read marker-position columns without applying the separate cube-centre conversion. Renaming the plotted quantity describes the existing calculation; shifting its data to the cube centre would change the result. The schematic must locate the same point as the data plots.
Alternatives: Changing every trajectory to the physical cube centre would require a new evaluation and violate this presentation-only scope. Changing Chapter 5's valid cube-centre holding-gate terminology would introduce an error.
Evidence: CH7_TRAILS_REVIEW.md; eval/gt/eval_rail_scenario.py load_track; eval/offset/carry.py box_center; Unity/Assets/Scripts/ArucoSceneReceiver.cs object_cube offset. Figure 7.5 is rebuilt under condensed, preserving frozen V7. Legacy JSON keys stay byte-identical and their marker-origin meaning is documented in the generator.
Reversibility: Revert the labels and schematic changes without touching any source result.
Review: Check Figures 7.2, 7.5, 7.7, 7.8 and 7.10 and the Section 7.3-7.6 interpretation; all existing measured values must remain unchanged.

ID: D-019
Status: UNCERTAIN
Decision: Bound the presentation capture by observable endpoint acknowledgements and process readiness, with operational deadlines only; use the existing chapter figure typography and adjust panel dimensions for print readability.
Why: Capturing a still must join the requested saved frame, not depend on a guessed sleep. A deadline prevents an unattended editor failure from blocking the session. Figure sizing and label placement are editorial settings and never select or modify trajectory samples.
Alternatives: Continuous replay without acknowledgement missed the final frame; a fixed sleep before screenshots would not prove frame identity.
Evidence: Captures at frames 500 and 528 succeeded during the first test, while frame 899 was missed at loop wrap. The working acknowledgement loop subsequently captured all three. Operational limits in render_ch7_trails.py are 60 seconds for shared-memory readiness, 600 seconds for capture/acknowledgement, 120 seconds for editor stop and exit, and 30 seconds for terminating an owned process; these are unmeasured limits, not timing results. Poll intervals are 0.1 seconds for endpoint acknowledgement, 0.2 seconds for readiness, 1 second for shutdown and 5 seconds for progress. Plot sizes, font sizes, stroke widths, camera clipping bounds and raster resolution are display choices in the final scripts, carried under D-017/D-019 rather than experimental thresholds.
Reversibility: Change operational limits or figure typography without changing the recording, samples or reported results.
Review: Inspect the resulting figures at final page width and check capture records and source hashes. The timeout limits are not measurements of system performance.

Amendment to D-017: the close-view test clipped the rendered cube at the right edge on the slide endpoint. The framing margin is increased from 1.2 to 1.4 for the final stills. This includes the cube body as scene context while keeping the saved trajectories fixed.

Amendment to D-019: the frozen Unity receiver writes shared scratch diagnostics under v1/integration/output. The final launcher preserves those files before opening the editor, archives the capture's diagnostics beside the new stills, and restores their prior bytes after shutdown. Earlier test launches refreshed those shared scratch logs; they did not alter the recorded video, tracking inputs, saved capture stream or pinned evaluation reports.

Amendment to D-019 (2026-09-08, finishing pass): the composed Figure 7.10 cuts the same window (still pixels 110-1200 by 80-680) from every phase still, which removes the empty wall and desk bands and keeps the three panels comparable; the label positions come from the logged waypoint viewport coordinates shifted by the cut, and the scale bar from the logged orthographic size. Figures 7.5 and 7.7 have the white margin around the 3D axes box trimmed from the rendered image. Display choices only; the saved points, the capture records and every reported number are unchanged, and validate_ch7_trails_revision.py still passes. The printed pages were inspected at page width after the rebuild (CH7_TRAILS_IMPLEMENTATION.md).

Amendment to D-016 (2026-09-08, code review finding): panel (a) of Figure 7.7 draws the wrist over the task frames 92 to 899 (the carry, lift and slide intervals of this decision), so that the startup excursion of frames 0 to 25, which reaches 40 cm beyond the task, no longer sets the scale of the 3D view; panel (b) keeps every frame 0 to 899 with the rebuilt intervals shaded, and the caption states both ranges. The full-track overview of the recording therefore lives in panel (b); no sample is removed from any evaluation.

Amendment to D-019 (2026-09-08, code review findings): (1) the stills are bound to their capture. render_ch7_trails.py accepts a run only when every still, record and receiver log carries a modification time after the editor launch, then writes manifest.json (SHA-256 of every artefact and of the view config) and capture.txt (the editor's capture lines) beside the stills; validate_ch7_trails_revision.py checks the manifest, so a stale still or a leftover receiver log fails. The capture was rerun through this path. (2) The composed figure derives its crop window from the drawn pixels of the three stills instead of a fixed pixel rectangle, and asserts one camera and one still size across the records. (3) Figures 7.1 and 7.2: the rail bar moved half a cube edge away from the sensor with the cube, because the fitted depth is the marker origin's and the cube body sits behind it; the W3 label moved above the cube. (4) Figure 7.8 gives the two panels heights in the ratio of their data spans and adjusts the data limits, so both panels keep the full width under the shared x axis. (5) Figure 7.7 labels the vertical axis of the 3D panel "height y (cm)" and widens the gap to the coordinate strips.

Amendment to D-019 (2026-09-08, second code review pass): (6) the equal panel widths of Figure 7.8 come from the box aspect mode with span-proportional heights; the data-limit mode used briefly before it cut the trajectories at the panel edges. (7) Figure 7.5's x label padded clear of its tick labels. (8) The composed Figure 7.10 is bound to its capture: make_ch7_trails_fig.py writes figures/ch7_trails_compose.json (digest of the manifest it composed from, the crop, the digest of the figure) and the validator checks it. (9) The launcher takes its acceptance time right before the editor starts, requires all three receiver logs fresh, and never raises during shutdown. (10) The first frame of the task in Figure 7.7 (a) is read from the pinned waypoints, not a literal.

ID: D-020
Status: SETTLED
Decision: The rail height above the desk in Section 7.3 is printed as 4.0 centimetres (was 3.9).
Why: The pinned eval/reports/r6b_rail_eval.json gives rail_height_m 0.0743 and desk_height_m 0.0346, a difference of 3.97 cm; the earlier 3.9 subtracted the two levels after each had been rounded to 7.4 and 3.5. The two-decimal rule (C48, PRECISION_ROUND5_CHANGES.md) computes before rounding. The tape value 3.8 cm and every other number are unchanged.
Alternatives: Keep 3.9 (a rounding error a reader can reproduce from the pinned values); print 3.97 (a third decimal, against C48).
Evidence: Code review of 2026-09-08 (second pass, finding 11); eval/gt/eval_rail_scenario.py writes both levels to four decimals.
Reversibility: One number in build_ch7.py.
Review: None; the inspection markdown that printed the rounded levels is a report, not the thesis.

ID: D-021
Status: SETTLED
Decision: The handover recording of supervisor round 6 (C50; E-034, E-035) enters the condensed thesis as new Section 7.7 "Handover on the Rail" between the Unity section and the recovery section, with Figures 7.11 (colour frames), 7.12 (marker origin along the rail with the hand at the cube, its distance to the fitted line, and the slide from above and from the side with both model wrists) and 7.13 (the Unity trail stills with both wrists) and Table 7.1 (the rail error per part of the slide, cited before the rail masking table, which becomes 7.2); the recovery section becomes 7.8 and the solver check 7.9, the label figures 7.14 and 7.15 and the remaining tables 7.3 to 7.5. The recording of Chapter 2 stays the thesis recording everywhere else. The chapter now names the three recordings as "the recording" (Chapter 2), "the handover recording" and "the loop recording" (previously "the second recording"). Sentences that called the rail task one-handed changed in Chapter 1 (scope, 1.3, objective 5), Section 2.1, Chapter 9 (9.1, Table 9.1 hips row, 9.3, the objective 5 item) and the abstract; Chapter 5, 6 and 9 cross-references to the recovery section moved from 7.7 to 7.8. The section reports the errors as they came out of the pinned chain (the supervisor: "even if it is filled with error, you should show them"), states that the wall card had shifted and that the levelling carries the gravity of the first recording (E-034), and closes with the hip-hold assumption and its numbers; Section 9.2 gains one paragraph on that assumption. The hip hold itself is not adopted (E-034).
Why: The supervisor asked for the second arm on the rail task, with the errors shown. Replacing the primary recording would redo the worked examples and figures of Chapters 2 to 6 (round 6 plan); a separate section keeps them intact.
Alternatives: Replace the primary recording; report only the object track without the wrists and the torso; adopt the hip hold thesis-wide (every root number changes while the thesis is under review).
Evidence: writing/v8/PROF_COMMENTS_ROUND6.md; eval/reports/r7_handover.md and the E-034 evidence; the builder comments of build_ch7.py Section 7.7 name the source of every number; check_refs UNRESOLVED none; check_style no new hits.
Reversibility: Remove the Section 7.7 block and restore the constants in build_ch7.py; the other chapters' sentence changes are listed in Thesis_V8_Changes_Ch7.docx.
Review: Opus chapter reviews writing/reviews/Chapter_7_handover_round1-3.txt; code review r7_code_review_round1.txt.

ID: D-022
Status: SETTLED
Decision: Supervisor round 7 (2026-09-10, C51 to C53): the abstract is rewritten as four paragraphs in the supervisor's order (the problem and why, the challenges, how they were addressed, what was accomplished), 344 words, quoting only numbers printed in Chapters 7 and 8 and keeping the C2 ground-truth statement and the M01 and M08 wording; the old Chapter 9 "Discussion, Future Work, and Conclusion" is split into Chapter 9 "Discussion" (9.1 Object Tracking Against the Rail, 9.2 Arm Pose and the Recovery, 9.3 The Second Arm and the Handover, 9.4 Torso and the Hidden Hips, 9.5 Landmark Failures at High Confidence, 9.6 The Live Structure, 9.7 Limits of the Model and the Evaluation with Table 9.1) and Chapter 10 "Conclusions and Future Work" (10.1 Conclusions, the old 9.3; 10.2 Future Work, the old 9.2). The marker-loss figure becomes Figure 9.1 and the landmark-failure figure 9.2, because Section 9.1 cites the marker first; Table 9.1 is unchanged. The hip-hold numbers stay in Section 9.3 and Section 10.2 only points at them; the hold stays a documented option (E-034). Cross-references moved: Chapter 1 objective 4 cites Chapter 10 and the roadmap sentence names both chapters; Chapter 3 Section 3.2 cites Section 9.7; Section 7.7 cites Section 9.3; Section 8.4 cites Section 9.6; Appendix E cites Section 9.1 and Appendix G Section 9.4. Chapter 10 is registered in build_thesis.py PARTS, build_toc.py, build_frontmatter.py CHAPTER_FILES, check_refs.py, check_style.py and count_summary.py. The three parts are also delivered as separate files: Abstract_V8.docx (scripts/build_abstract.py, reading the same ABSTRACT list), Chapter_9_Discussion.docx and Chapter_10_Conclusions_Future_Work.docx. The old Chapter_9_Discussion_Conclusion.docx leaves the tree; its last build is commit de74302.
Why: The supervisor asked for the abstract in those four parts, for a discussion chapter because "there are a lot to discuss about all your results", and for a separate conclusions and future work chapter, sent separately. Ordering the discussion by result rather than by limitation is what makes it a discussion; no new evaluation was run because the round is the last comment and every needed number was already printed.
Alternatives: Keep one chapter with a renamed discussion section (does not answer C52 and C53); bring the parked loop-recording material of CH7_PARKED.md back into the discussion (new numbers under review, declined); relax the 350-word abstract gate (declined, the gate is the thesis format).
Evidence: writing/v8/PROF_COMMENTS_ROUND7.md; the builder comments of build_ch9.py and build_ch10.py name the source of every number; the number audit of the round (every numeric token of the three new texts found in the old Chapter 9, the old abstract or the built Chapters 7 and 8: none missing); check_refs UNRESOLVED none; check_style only the two pre-existing hits.
Reversibility: Restore build_ch9.py and build_frontmatter.py from de74302, delete build_ch10.py and the registry lines, and reverse the cross-reference pairs listed in CH9_SPLIT_TEXT_CHANGES.md.
Review: three fresh Opus rounds each on the abstract, Chapter 9 and Chapter 10 (writing/reviews/Abstract_round1-3.txt, Chapter_9_discussion_round1-3.txt, Chapter_10_round1-3.txt); every clear finding applied (active voice, sentence splits, glossary names for the two branches, the parked term torso repair, intensifiers, metaphors); the flags left after round 3 are marked uncertain by the reviewers or name the thesis's established evaluation terms (the slide, the unmasked solve, the reference floor, the marker origin, the object estimate, the manual labels) and the deliberate objective-by-objective parallel of Section 10.1, and are declined.

ID: D-023
Status: SETTLED
Decision: Thesis revision of 2026-09-11, Phase 1: Chapter 7 rebuilt as "Experimental Evaluation" (7.1 Evaluation Framework and References, 7.2 Object Reconstruction, 7.3 Human-Object Reconstruction and Handover, 7.4 Landmark Failure and Wrist Recovery with 7.4.1 Synthetic Masking and 7.4.2 Natural Failures, 7.5 Kinematic Solver Verification) and Chapter 8 kept as "Real-Time Feasibility" (8.1 From Offline to Causal Processing, 8.2 Causal and Real-Time Architecture, 8.3 Offline-Causal Comparison, 8.4 Runtime, Buffering, and Delay, 8.5 Feasibility and Remaining Validation Gap), under the author's locked facts recorded verbatim in REVISION_2026-09-11_BRIEF.md. The revision starts from commit 0006355; the attempt of 2026-09-11 that turned Chapter 8 into a discussion is discarded (its two pushed commits b8c51e1 and b6ba126 are kept under the tag archive/ch78-attempt-2026-09-11).
Why: The author fixed the chapter roles (Ch7 offline evaluation, Ch8 causal feasibility, Ch9 discussion, Ch10 conclusions) and nine experimental facts that the previous text contradicted: the physical route 25.5 / 3.5 / 37.5 cm is a tape measurement and not the tracked waypoints; a line fitted to the tracked samples is a within-recording description, not an accuracy reference; the approximately 16 cm wrist-to-marker distance of a single-hand grip is an approximate scalar physical reference; the four handover medians 15.77 / 17.91 / 15.85 / 14.08 cm are compared with it only for the single-hand parts; the 16 loop-left labels are 14 frames 1427 to 1492 at five-frame spacing plus 1777 and 1787; object information supplies an additional geometric constraint and does not recover the wrist by itself; the 29 fps result is a causal replay at recorded pace with a configured two-frame buffering delay and no live-camera validation; the desk and object markers are 45 mm.
Alternatives: Keep the tracking-derived leg lengths 25.5 / 3.6 / 37.4 cm as the route (rejected: they are outputs of the track); relabel the old Figure 7.2 as the physical route (rejected: the figure, now Figure 7.4, carries a bold placeholder until the route is registered into the world frame); keep the 45/50 mm correction narrative (rejected: the pinned chain implements 45 mm as the detector's 50 mm default times 0.9, which is exactly the 45 mm result, so the thesis states 45 mm and the builder comments keep the provenance).
Evidence: Author's message of 2026-09-11 (locked facts); eval/reports/r7_handover.json (the four medians); eval/reports/r5_recovery_labeled.md and r6b_recovery_labeled.json (label sets; the rail set is 18 frames 550 to 635 plus 674, 679, 684, corrected in the same pass); eval/reports/r6b_marker_scale.json and r7_marker_scale.json (assumed 45 mm, scale 0.9); v2/dataset/r6b_probe_baseline.txt (29.0 fps sustained, gated hips 858 of 900); v2/dataset/m03_rail_corrected.json (lag 5, 174 pairs, per-angle medians); figures/ch8_compare.json (12.0 cm at frame 18); review and fix records in notes_revision_ch7.md and notes_revision_ch8.md. One unsourced sentence (2.6 / 3.8 cm from the eighth masked frame) was deleted because no pinned report carries it.
Reversibility: git revert of the Phase 1 commit restores the 0006355 chapters; the tag keeps the discarded attempt.
Review: Confirm the 45 mm wording (the thesis no longer mentions the 50 mm detector default), the bold regeneration placeholder in Section 7.2, and the two-decimal medians against the one-decimal precision rule. Chapter 2 Table 2.1, Appendix E and Chapter 9 still carry the old wording until Phases 2 and 3.

ID: D-024
Status: SETTLED
Decision: Thesis revision of 2026-09-11, Phase 2: Chapter 9 rebuilt as the Discussion in seven sections (9.1 Object Reconstruction and Physical-Route Error Sources, 9.2 Human-Object Spatial Reconstruction, 9.3 Landmark Failure and Object-Assisted Recovery, 9.4 Torso and Root Failure and High-Confidence Landmark Errors, 9.5 Single-View Observability and Model Limits, 9.6 Real-Time and Causal Implications, 9.7 Scope of the Evaluation with Table 9.1); Chapter 1 reframed on the central question with the five objectives as stages of one investigation and the organization section on the final chapter roles; Chapter 10 rewritten as a concise answer to the central question (feasibility, the conditional value of object information, limits of two kinds) with future work following from the limits; the abstract reworded to the same vocabulary within the 350-word gate; the author's Chapter 7 defect list processed (Part A verified against the pipeline outputs, no printed number changed; Part B applied to the new numbering; record in audit_evidence/ch7_defects_2026-09-11/REPORT.md).
Why: The author's Phase 2 specification. The review of the phase found and the fix pass corrected: "the held wrist 17.6" in Chapter 10 (it is the hold-last solve; the held wrist is 15.6); the Chapter 9 claim that no torso detector fires before frame 632 (r6b_failure_events.csv has a torso event at frames 21 to 32; the 19.4 cm hip split is the mechanism of the window from 632); two citation targets (Section 6.4 for the three parts of the rendered-hand distance; Section 7.2 for the handover detection count); the Chapter 3 pointer to the rigid-torso limitation (9.5, was 9.7).
Alternatives: Keep the objective-by-objective recital in Chapter 10 (rejected by the author's specification); keep the abstract's "median of 1.0 centimetres from the rail" (rejected: it presents a fitted-line spread as accuracy against the rail, locked fact 3).
Evidence: notes_revision_ch9.md, notes_revision_ch1.md, notes_revision_ch10.md (each with section (h) review fixes); eval/reports/r5_recovery_labeled.md (hold 15.64, hold_fk 17.6); eval/reports/r6b_failure_events.csv; eval/reports/r6b_hip_hold.md (rail hip-hold values, printed in Chapter 9 only); eval/output/recording_20260825_222315_scaled_object_world.csv (loop detection counts 2058 of 2099, an output file rather than a pinned report, printed in Chapter 9 only; flagged for the author).
Reversibility: git revert of the Phase 2 commit.
Review: The abstract lost the explicit mention of the unmasked solve and of "reaching and handovers" to stay under 350 words; the rail hip-hold values and the loop detection counts appear only in Chapter 9; Chapter 9 sits about 5 percent above its word allowance.

Amended by: D-046. The loop detection coverage is now recomputed and pinned in audit_evidence/ch7_restructured/loop_detection.json, introduced in Chapter 7 Section 7.4.2. The evaluation output CSV is no longer its cited source and the flag for the author is closed.
ID: D-025
Status: SETTLED
Decision: Thesis revision of 2026-09-11, Phase 3: Chapters 2 to 6 revised for continuity only, under a shared chain contract (Chapter 2 the measurement layer; 3 the upper-body kinematic state; 4 the independent object observation branch; 5 object information as an additional geometric constraint under landmark failure; 6 the integration), each opening with what the previous stage provides and what remains unresolved and closing with what the chapter established and why the next is required. No method, experiment, parameter, equation, figure, table or number changed. Table 2.1 carries one marker size column (wall 150, desk 45, object 45 mm) and the 45/50 correction sentence is gone from Chapter 2, Chapter 4 and Appendix E (provenance kept in the builder comments: the pinned chain implements 45 mm as the detector's 50 mm default times 0.9). Cross-references into the new Chapters 7 and 8 repaired in Chapters 2 to 6 (old Section 7.8 to 7.4.1 or 7.4.2 by content; "declares" to "configures (Section 8.2)"; "the reference path of Section 7.1" to the measured route and the fitted line of Section 7.2). Chapter 3 states the model scope once in Section 3.3.1 in wording Section 9.5 cites. Chapter 5 says once, in Section 5.4, that equation (5.7) does not by itself recover the wrist. Chapter 6 lists five passages as candidates for relocation to Chapter 8 in notes_revision_ch6.md section (d) and leaves them in place.
Why: The author's Phase 3 specification.
Alternatives: Sequential writing of Chapters 2 to 6 (rejected for time; the chain contract fixed the seam formulations and the final review loop checks the seams).
Evidence: notes_revision_ch2.md to notes_revision_ch6.md; check_refs UNRESOLVED none over 609 references; check_style clean apart from the pre-existing acknowledgements line; count_summary main body 37,089 words.
Reversibility: git revert of the Phase 3 commit.
Review: One verbatim user sentence of Section 2.5 was deleted (logged in notes_revision_ch2.md section (f)); Chapters 2, 3, 5 and 6 each grew by 150 to 185 words; the "about 6 centimetres" offset scatter of Section 5.3 rests on a scratchpad diagnostic rather than a pinned report; Table 5.1 attributes the segment lengths to Chapter 3 (Chapter 3 writer proposes Section 5.1). Table 2.1 wording is subsequently clarified by D-026.

ID: D-026
Status: SETTLED
Decision: Use the author's supplied Table 2.1 with the heading "Printed size (mm)": wall marker ID 0, 150 mm; desk marker ID 2, 45 mm; object marker ID 1, 45 mm; all dictionaries "5 by 5"; cube 70 mm per side; wooden rail 387 by 88 by 38 mm, lying flat, with role "Reference object". The earlier "Declared size (mm)" values are legacy values and are not used as the marker dimensions in the current thesis.
Why: The author supplied the exact table and explicitly requested a permanent record that the declared values are legacy values, not values used in the current thesis.
Alternatives: Retain the generic "Size (mm)" heading or restore a declared-size column (rejected: neither matches the author's table and the latter would present obsolete dimensions as current).
Evidence: Author's Table 2.1 instruction in this conversation on 2026-09-11; eval/common/marker_size.py and eval/reports/r6b_marker_scale.json and r7_marker_scale.json preserve the historical calculation, where the legacy 50 mm detector default is scaled by 0.9 to obtain the effective 45 mm size. The requested dimensions are author-supplied setup values, not new experimental measurements by the agent.
Reversibility: Restore the two table labels in condensed/scripts/build_ch2.py and rebuild Chapter 2. Historical code, configurations and pinned reports retain their original values as provenance.
Review: Confirm that Table 2.1 matches all cells supplied by the author. "Not used in the current thesis" refers to the current stated and effective marker dimensions; it does not assert that the historical 50 mm default never appeared in an intermediate calculation.

ID: D-027
Status: SETTLED
Decision: Revise "7.3 Object Trajectory in the World Frame" at its current V8 location, Section 7.2, and provide replacement text under the author's requested heading. Separate physical rail measurements, the straight-line estimate of the filtered ArUco trajectory, and individual samples around that line. Use perpendicular deviation and tracking scatter; report only supported physical comparisons. The author's subsequent heading clarification narrows the scope to this object-trajectory section; the current Human-Object Reconstruction and Handover section is unchanged.
Why: The author's current instruction requires standard terminology and independent physical references for accuracy claims. The chapter numbering changed during D-023; changing only current Section 7.3 would leave the requested evaluation passage untouched.
Alternatives: Invent a registered 3D rail path or treat fitted-line distances as position errors (rejected: no independently surveyed world-frame rail coordinates); report the fitted direction's tilt as full object orientation error (rejected: only its elevation against the horizontal setup is available); treat the tracked extent as measured endpoint error (rejected: the height-selected samples are not matched physical endpoints).
Evidence: Author's instruction in this conversation; REVISION_2026-09-11_BRIEF.md section 3 facts 2 and 3; Table 2.1 and eval/DECISIONS.md E-024 for rail dimensions and the levelled setup; eval/reports/r6b_rail_eval.json, r7_rail_eval.json and r7_handover.json for height modes, fitted-line tilt, projected extent and perpendicular deviations; eval/gt/eval_rail_scenario.py uses filtered object samples and computes horizontal deviation from both horizontal coordinates.
Reversibility: Restore the affected paragraphs and captions in condensed/scripts/build_ch7.py and rebuild Chapter 7. Historical reports and their terminology remain unchanged as provenance.
Review: The height comparison assumes the marker retains its height relative to the cube base between desk and rail. The tilt comparison depends on calibrated gravity and the reported spirit-level setup, without a measured levelling uncertainty. Full 3D position, azimuth and object orientation accuracy remain unverified. A subagent must check the modified prose against the language rules after rebuilding.

ID: D-028
Status: SETTLED
Decision: Remove unnecessary personal self-reference from the current thesis prose by describing the procedure, data or analysis directly. State once in Section 7.4.2 that manual wrist labels were produced by a single annotator. Preserve legal/template wording, acknowledgments and unrelated uses of authored for the rig.
Why: The user requested objective academic phrasing throughout the thesis and explicitly excluded mechanical replacement with I or we, legal wording and asset-authoring descriptions.
Alternatives: Global text substitution including source comments and historical records (rejected: would alter provenance and protected wording); replace the author with first-person pronouns (explicitly prohibited); repeat annotator attribution across chapters (unnecessary repetition).
Evidence: User instruction of 2026-09-12; rendered-text audit of the current chapter documents and builder prose; existing Section 7.4.2 describes the labels as clicks by one person. Label counts, exclusions, depth checks and all measurement values remain unchanged.
Reversibility: Restore the affected builder sentences and rebuild the chapters and assembled thesis. Source comments, historical decision records and archived drafts retain their provenance.
Review: Independent subagents check coverage and language. Confirm no personal self-reference remains in technical prose, the annotation role appears once, and copyright/acknowledgments and rig-authoring wording are preserved.

ID: D-029
Status: SETTLED
Amended by: D-037. Solver verification was removed from Chapter 7 by this entry and now lives in Appendix H; it is not deleted from the thesis.
Decision: Reorganize condensed V8 Chapter 7 into the user's Evaluation Method, Object Reconstruction Accuracy, Human Reconstruction Accuracy under Valid Landmark Measurements, and Reconstruction during Landmark Failure structure. Remove solver verification and evaluate each result against its specified reference.
Why: The user's 2026-09-12 instruction supersedes the earlier fixed chapter structure and preservation of old figures, tables and numerical results. Independent audits must establish evidence before results enter the replacement.
Alternatives: Preserve the earlier mixed object/human section or reuse existing numerical tables without checking reference definitions (rejected by the user).
Evidence: Current user request; active builder condensed/scripts/build_ch7.py; three parallel read-only evidence audits. The initial DOCX and builder were preserved in /tmp/ch7_rewrite_baseline before edits; the repository contains pre-existing changes in other chapters and assembled documents.
Reversibility: Restore the initial Chapter 7 files from the baseline backup or the previous Git version, with the pre-existing uncommitted changes accounted for.
Review: Check requested section order, common definitions, traceable numerical sources, and explicit Data Required requests. Do not treat a partial chapter as a completed evaluation.

ID: D-030
Status: BLOCKED
Superseded by: D-035. The user supplied the missing physical reference and authorized independent motion-based frame identification.
Decision: Withhold the three segment-length error results for both recordings until physical waypoint identity, frame correspondence and measurement applicability are supplied.
Why: The stored route corners combine coordinates from the tracked parked mean and fitted slide line. They are not reconstructed observations at independently identified physical endpoints. Length accuracy does not itself require a surveyed world-frame route.
Alternatives: Relabel tracked synthetic corners or fitted min/max extents as physical endpoint measurements (rejected: the correspondence is unsupported); require a full 3D survey for scalar lengths (unnecessary).
Evidence: REVISION_2026-09-11_BRIEF.md fact 2 records tape lengths; eval/reports/r6b_waypoints.json and r7_waypoints.json construct route corners from the reconstruction. The object evidence subagent independently verified the mismatch. A specific data request was sent to the user before writing results.
Reversibility: Supply waypoint definitions, endpoint/movement frame ranges and applicable physical lengths for each take; calculate and pin the resulting measurements before completing Section 7.2. Registered figures additionally require physical geometry and its frame transform.
Review: Confirm which point on the object each tape endpoint measures, whether the same route lengths apply to the handover, and the endpoint-selection rule. No existing leg length or fitted extent is accepted as a substitute.

ID: D-031
Status: SETTLED
Decision: Calculate Section 7.3 errors from captured Unity elbow/wrist bone positions against same-frame raw MediaPipe plus aligned-depth positions, with explicit detector-accepted input validity and capture-subset scope.
Why: Saved rig positions exist for both tasks. Filtered model wrist errors and image reprojection distances measure different quantities. Measurement acceptance does not imply that every output group is measured; root/twist output states must be disclosed.
Alternatives: Require all output tags measured (would leave no single-hand observations and would change an input-validity condition into an output-state condition); publish whole-recording estimates from sparse captures (unsupported).
Evidence: figures/src/ch7_trails_revision/unity_person_log.csv and figures/src/ch7_handover_trails/unity_person_log.csv; raw/filtered landmark CSVs; failure masks and instantaneous detectors; eval/unity_check/check_unity_log.py defines the calibration mapping and receiver scene constants. Read-only human audit verified frame, timestamp and pelvis correspondence.
Reversibility: Replace subsets with complete synchronized captures, or restrict to wholly measured output if that is the intended experimental condition. Regenerate coordinate-pair evidence and all tables/figures together.
Review: Gate source code zero, finite positive depth, filtered flag zero, side and torso instantaneous/event acceptance within the existing evaluated span. Disclose constrained-root output. Existing checker tolerances are synchronization checks, not accuracy filters. Never reject large joint errors on magnitude alone.

ID: D-032
Status: SETTLED
Decision: Recalculate synthetic removal using the valid unmasked model reconstruction as reference, with 45-frame right-arm windows selected by reference wrist excursion before method scores.
Why: Existing positional tables use measured wrists as reference. Strictly observed reference inputs and live root/arm outputs exist in the handover recording. The existing harness WIN=45 is its established recovery-horizon experiment duration.
Alternatives: Reuse old positional errors (wrong reference); keep only stationary windows (misses available motion); use arbitrarily selected durations (unnecessary).
Evidence: eval/failure/harness_recovery.py WIN, grip_context and masked_inputs; recovery_core.py; strict read-only screening finds handover right-arm frames 433-643 before further source validation. Select minimum excursion, maximum among nonoverlapping remaining candidates, then nearest full-candidate median among remaining candidates, earliest-frame tie break. This is a descriptive selection rule, not a claimed representative sample or tuned performance threshold.
Reversibility: Change the explicitly documented selection and rerun all methods from fresh initial state; keep the complete candidate list and previous evidence.
Review: All relevant raw/filtered inputs observed and finite, positive raw depth, all instantaneous and event detectors accepted, reference root/swing/twist/elbow live, grip established before removal. Mask elbow and wrist only, keep the measured shoulder, compare elbow and wrist positions on identical frames. Exclude scored landmarks from grip fitting. Pin selection before recovery scores and disclose offline calibration.

ID: D-033
Status: SETTLED
Decision: Present natural physical occlusion on the loop recording with separate bracelet/watch wrist proxies, clean measured-to-proxy offsets first, and matched plain/hold/object-assisted model wrist distances second.
Why: These comparisons have reproducible pinned coordinates and identical proxy conventions on clean and occluded frames. Rail detector dropout does not establish physical occlusion and is omitted from this subsection.
Alternatives: Call clicks anatomical ground truth, subtract a scalar clean offset from reconstruction distances, or validate recovery against its own hand-object constraint (all unsupported).
Evidence: eval/labels/README.md, frames_r5/meta.json and labels.json; eval/reports/r5_recovery_labeled.json; independent audit reproduced all stored model distances from angle CSVs and filtered shoulder anchors. Clean wrist baselines use accepted filtered measurements, with raw observed source and valid depth, not raw-coordinate statistics.
Reversibility: Add repeated independent annotations or a better wrist reference and regenerate comparisons with that reference explicitly identified.
Review: Report median/p95/maximum and n by arm on the same retained failure labels. Clean samples quantify usual proxy separation, not anatomical calibration; annotation/depth uncertainty remains unmeasured. Small selectively visible samples cannot support a general method ranking.

ID: D-034
Status: UNCERTAIN
Decision: Use a 0.00001-second maximum same-frame timestamp discrepancy as a serialization sanity check on the captured Unity logs, alongside exact frame/mask correspondence and existing pelvis-mapping checks.
Why: Unity serializes single-precision timestamps to six decimal places; stored times differ slightly from the double-precision source. The chosen tolerance exceeds the observed discrepancies and remains far below one recorded frame interval. It does not choose an alignment lag or exclude frames from error statistics.
Alternatives: Require exact textual timestamp equality (fails harmless serialization differences); align by nearest timestamp (unnecessary and could conceal wrong frame identity).
Evidence: Unity/Assets/Scripts/IntegratedSceneReceiver.cs writes t with F6; independent audit found maximum discrepancies below 0.000006 seconds. The exact 0.00001 threshold is an analyst-selected numerical check, not a measured sensor accuracy or a formal bound on all runtime serialization.
Reversibility: Replace with an exact reproduction of the receiver serialization; per-frame joins and resulting coordinates are unchanged if it confirms the same frame identity.
Review: Check provenance and recorded maximum discrepancies. This threshold never appears as an experimental result or a landmark-validity gate.

ID: D-035
Status: SETTLED
Decision: Use the ArUco marker centre as the physical and reconstructed endpoint reference in both recordings, with physical lengths 25.5, 3.5 and 37.5 cm and measurement resolution 1 mm. Detect each recording's waypoint timing independently from its marker motion.
Why: The user explicitly supplied these measurement definitions and instructed the agent to find frame intervals rather than request frame numbers. This resolves D-030's data blocker.
Alternatives: Reuse old constructed waypoints or derive endpoints from fitted rail lines (explicitly prohibited); assume shared frame timing (explicitly prohibited).
Evidence: User's current instruction: W1 initial stationary; W2 stationary or near-stationary immediately before rise; W3 after rise before leftward rail translation; W4 final stationary. Use mean marker-centre positions over detected intervals; if no clear pause exists, identify and explain a motion-transition frame instead.
Reversibility: Re-evaluate only if the physical measurement definitions or waypoint-phase interpretation change. Keep raw trajectories, detector diagnostics and sensitivity results with the new output.
Review: Independently inspect both trajectories and task phases. Interval selection must use local motion, not physical-length agreement. Explicitly disclose any transition-frame estimator and detector-selection uncertainty.

ID: D-036
Status: SETTLED
Decision: Define W1 to W4 in Section 7.2 as physical task phase boundaries on the ArUco marker centre, not as arbitrary stationary points. W1 is the marker centre before the first translation begins; W2 is the marker centre at the end of the first translation, immediately before the vertical rise; W3 is the marker centre at the end of the vertical rise, immediately before the leftward rail translation; W4 is the final marker centre after the leftward translation ends. W2 and W3 are single transition frames and are not required to contain a stationary dwell. W1 and W4 may use the mean of a clear stationary interval. Physical segments are W1 to W2 equal to 25.5 cm, W2 to W3 equal to 3.5 cm, and W3 to W4 equal to 37.5 cm, at 1 mm resolution, applying to both recordings because the physical setup is identical. This replaces the earlier Start, W1, W2, W3 naming.
Why: The author restated the waypoint definitions after D-035 to remove a false requirement. Requiring a stationary dwell at W2 and W3 would have blocked both segments adjoining the vertical rise, because the object does not pause on either side of the lift. Phase boundary identification is well posed where dwell detection is not.
Alternatives: Keep the stationary dwell requirement at every waypoint (rejected by the author: the rise has no pause, so the requirement is unsatisfiable); reuse the constructed corners in eval/reports/r6b_waypoints.json and r7_waypoints.json or the fitted rail line to define the waypoints (explicitly prohibited); assume shared frame timing across the two recordings (explicitly prohibited).
Evidence: Author's binding correction of 2026-09-12, reproduced verbatim in the writer brief. Trajectory source eval/output/recording_20260831_065553_scaled_object_world_filtered_clean.csv and recording_20260909_000024_scaled_object_world_filtered_clean.csv. All physical measurements refer to the ArUco marker centre, not the cube centre and not an edge.
Reversibility: Re-evaluate only if the physical measurement definitions or the phase interpretation change. Keep raw trajectories, the detection rule, per waypoint phase confirmation and sensitivity results with the output.
Review: Report the selected W1 to W4 frames or intervals per recording and state how each motion transition was identified. Confirm each detected boundary sits in the intended task phase from the trajectory's own motion pattern. Where a boundary is genuinely ambiguous, run a sensitivity check around the candidate boundary and report whether the segment length changes materially. Fitted line scatter remains separate and is not the physical length accuracy metric.

ID: D-037
Status: SETTLED
Decision: Move solver verification, formerly Section 7.5 with its Table 7.5, into an appendix. Chapter 3 points to the appendix instead of Section 7.5, and the Chapter 1 roadmap is corrected so it does not advertise a verification the evaluation chapter no longer contains.
Why: D-029 removed solver verification from Chapter 7, leaving it with no home anywhere in the thesis while Chapter 3 still promised it. The author chose to keep the evidence available without letting it re-enter the evaluation narrative.
Alternatives: Delete the promise from Chapters 1 and 3 and drop the verification entirely (rejected: discards existing verified evidence); restore the section inside the restructured Chapter 7 (rejected: reopens what D-029 deliberately removed).
Evidence: CH7_INTEGRATION_FIXLIST.md records the single check_refs.py failure, Chapter_3_Kinematic_Modeling sec 7.5, and the Chapter 1 roadmap wording. The removed content is recovered from Git history of condensed/scripts/build_ch7.py with its pinned source comments unchanged.
Reversibility: Restore the appendix section to Chapter 7 or remove it, and revert the Chapter 1 and Chapter 3 pointers. No number changes, so no evidence is invalidated either way.
Review: Numbers and pinned source comments must move unaltered; only connective framing may change. Confirm the sec 7.5 cross-reference error is gone and report any pre-existing unrelated errors that remain rather than fixing them.

ID: D-038
Status: SETTLED
Decision: Retain the wrist to marker measurement in the restructured Chapter 7 as a short subsection, 7.3.3 Human-Object Spatial Check, placed after the valid landmark human reconstruction analysis, without restoring the old Section 7.3 structure. Report the physical wrist landmark to ArUco marker centre distance of about 16 cm, the reconstructed right hand alone median of 15.77 cm and the reconstructed left hand alone median of 14.08 cm, under normal single hand grip conditions only. Do not grade the handover values of 17.91 cm and 15.85 cm against the 16 cm reference. Revise Chapter 9 Section 9.2 and Chapter 10 Section 10.1 to match this limited interpretation.
Why: This is the only human-object quantity in the thesis with an external physical reference, and both Chapter 9 and Chapter 10 build on it, including Chapter 10's answer to the central question of Chapter 1. The restructure left those claims without a source. The author restricted its interpretation rather than discarding it.
Alternatives: Drop the measurement and rewrite Chapter 9 and Chapter 10 without it (rejected: removes the only external physical check of human-object separation); restore the previous Section 7.3 structure to carry it (explicitly rejected by the author); apply the 16 cm reference to the handover values as well (rejected: grip geometry changes during transfer, so the reference does not apply).
Evidence: Author's decision of 2026-09-12. REVISION_2026-09-11_BRIEF.md records the author's approximate 16 cm measurement for a normal single hand grip and the verified medians 15.77, 17.91, 15.85 and 14.08 cm. CH7_INTEGRATION_FIXLIST.md records the dependent claims at build_ch9.py line 140 and build_ch10.py line 72.
Reversibility: Remove the subsection and the dependent sentences in Chapters 9 and 10 together. The pinned medians and the author's physical measurement are unchanged by this decision.
Review: The subsection must describe an approximate external physical check that the reconstructed human-object separation is of the correct magnitude, and nothing stronger. It is not anatomical wrist ground truth and it does not validate the three dimensional hand-object offset used by the recovery algorithm. Confirm the handover values are not graded against the reference and that Chapters 9 and 10 carry no stronger accuracy claim.

ID: D-039
Status: SETTLED
Outcome: the bare model quantity was recomputed and is pinned in audit_evidence/ch7_restructured/bare_model.json. The fallback of removing the claim was not needed. Reporting conventions are settled in D-040, D-041, D-042 and D-043.
Decision: Distinguish two wrist quantities explicitly throughout the thesis. The bare model wrist error compares the measured MediaPipe and depth wrist with the wrist position produced directly by the kinematic model and forward kinematics, before Unity rig mapping and display filtering. The rendered rig wrist error compares the same measured wrist with the corresponding Unity rig joint after the complete rendering path, including coordinate and rig mapping and any display filtering. Recompute the bare model quantity against the current accepted valid landmark frame set and pin its source. Keep the rendered rig values in Table 7.2 as a separate end to end reconstruction and display metric. Never describe the two interchangeably.
Why: Chapter 9 claims the model wrist sits about a centimetre from the measured wrist, citing 0.96 cm and 1.17 cm, while the restructured Table 7.2 prints 5.7 cm and 6.9 cm on the same recording. Both can be correct because they measure different quantities, but the thesis nowhere defines the difference, and the older values no longer have a surviving pinned source.
Alternatives: Drop the one centimetre claim and let the rendered rig numbers stand alone (retained by the author only as a fallback); reuse the old values as they are (rejected: not reproduced from the current data or the current accepted frame definition).
Evidence: CH7_INTEGRATION_FIXLIST.md item at build_ch9.py line 150; audit_evidence/ch7_restructured/human.json and human_pairs.csv define the current accepted frame set and the rendered rig comparison; natural.json derives model distances from angle files and filtered shoulder anchors, indicating an existing forward kinematics path.
Reversibility: If the bare model quantity cannot be recomputed from available data, remove the one centimetre claim from Chapter 9 rather than preserving the old values unsupported. This decision closes as SETTLED once the recomputed values are pinned or the fallback is taken.
Review: Use the same accepted frame set as Section 7.3.2 so the two quantities are directly comparable. Do not tune anything to reproduce 0.96 and 1.17 cm; if the recomputed values differ, state what accounts for the difference. Do not invent a forward kinematics convention, a segment length calibration, a root anchor choice or a frame alignment.

ID: D-040
Status: SETTLED
Decision: The reference wrist for quantitative reconstruction error throughout the revised thesis is the accepted raw MediaPipe and depth three dimensional wrist measurement before temporal filtering. The same reference applies to the bare kinematic model wrist error, the rendered Unity rig wrist error, and any clean frame baseline intended to represent reconstruction error against a measured wrist. State the convention once in the evaluation method and apply it consistently. Where a filtered wrist is used elsewhere for an algorithmic purpose, distinguish that explicitly from the evaluation reference. Never mix raw reference and filtered reference errors in one comparison table.
Why: The author required a single evaluation convention rather than continuity with older reports. Two conventions were in use: the accepted raw landmark behind human_pairs.csv and the Section 7.3 rendered rig comparison, and the filtered landmark behind the older pinned reports and the clean baseline of natural.json. A thesis that mixes them invites a comparison that is not like for like.
Alternatives: Keep the filtered wrist for continuity with eval/reports/r7_handover.json and natural.json (rejected by the author: continuity is not a reason to preserve a second convention); leave the convention implicit per section (rejected: the difference is small but the ambiguity is not).
Evidence: Author's decision of 2026-09-12. audit_evidence/ch7_restructured/bare_model.json records both variants, raw 0.83 and 2.34 cm and filtered 0.73 and 2.30 cm on the capture subset, so the cost of the convention is measured rather than assumed.
Reversibility: Recompute against the filtered landmark and restate the convention once. Both variants are already pinned, so neither direction needs new data.
Review: Confirm the convention is stated in the evaluation method and that no comparison table mixes the two references. Older reports and derived prose are updated where they carry the superseded convention.

ID: D-041
Status: SETTLED
Numbering note: these entries were written before Section 7.2 gained its two object tables. Every reference to "Table 7.2" in this entry means the HANDOVER RENDERED RIG table, which is now Table 7.4. Table 7.2 is now the handover object segment length table. Table 7.1 of Section 7.3.1 is now Table 7.3.
Decision: Report the bare kinematic model wrist error at two scopes for two distinct purposes, never as interchangeable results. The Unity capture subset values, right 0.83 cm and left 2.34 cm with n of 650 and 589, are the values directly comparable with the rendered rig results of Table 7.2 and are used only when discussing the additional discrepancy introduced downstream in the Unity, rig and display path. The recording wide accepted frame values, right 1.03 cm and left 1.03 cm with n of 1156 and 1095, are the representative performance of the bare kinematic model and support any general statement that the bare model wrist lies about a centimetre from the measured wrist. State explicitly that the capture subset is not representative of the full accepted frame population, especially on the left arm, because it over represents held twist frames at 55 per cent against 41 per cent recording wide. Never compare the recording wide values directly against Table 7.2, because the frame sets differ.
Why: The bare model quantity does not require a Unity capture, so the capture subset restriction is an artefact of the rendered rig comparison rather than a property of the model. Frame matched comparison and representativeness are different needs and the single number that serves one misleads about the other. The left arm differs by more than a centimetre between the two scopes.
Alternatives: Print the capture subset alone (rejected: over represents held twist frames and misstates the model); print the recording wide values alone (rejected: not frame matched to Table 7.2, so the downstream contrast would not be like for like).
Evidence: Author's decision of 2026-09-12. audit_evidence/ch7_restructured/bare_model.json holds both scopes, the frame counts and the held twist composition of each.
Reversibility: Drop either scope and restate the dependent sentences in Chapter 7 and Chapter 9 together. Both are pinned.
Review: Each printed value must name its scope. Confirm Chapter 9 uses the recording wide values for intrinsic kinematic model accuracy and the capture subset values only for the downstream discrepancy.

ID: D-042
Status: SETTLED
Decision: Do not print the 6.78 cm bare model wrist value of the single hand rail recording as a reconstruction accuracy result, and omit it from the main accuracy table of Section 7.3.1. State explicitly in Section 7.3.1 that the right forearm twist is held on all accepted frames and the root is constrained on all accepted frames, so the distance is not an isolated kinematic model closure metric and includes the effects of the held twist and constrained root state. Do not compare the single hand rail recording numerically with the handover bare model results. The handover recording supplies the quantitative bare kinematic model accuracy. If the value is retained anywhere it may appear only in Chapter 9, as an operational consequence of the held and constrained state, never as intrinsic accuracy.
Why: A bare 6.78 cm printed beside the handover values would read as a model closure figure for a recording in which no frame has measured twist or free root. The output state, not the kinematic chain, dominates it.
Alternatives: Print it with disclosure (rejected: the number would still be read as closure accuracy); report it split by twist state (rejected: the rail recording has no measured twist frames to split against).
Evidence: Author's decision of 2026-09-12. bare_model.json records the rail right arm as 100 per cent held twist and 100 per cent constrained root over the accepted frames, and the twist split showing 0.6 to 0.9 cm where twist is measured against 2.3 to 2.8 cm where it is held.
Reversibility: Print the value if a rail frame set with measured twist and free root is ever established. None exists now.
Review: Confirm no numerical comparison is drawn between the rail and handover bare model results, and that Section 7.3.1 states the output state rather than simply omitting the number.

ID: D-043
Status: SETTLED
Numbering note: these entries were written before Section 7.2 gained its two object tables. Every reference to "Table 7.2" in this entry means the HANDOVER RENDERED RIG table, which is now Table 7.4. Table 7.2 is now the handover object segment length table. Table 7.1 of Section 7.3.1 is now Table 7.3.
Decision: State the Unity capture configuration explicitly, because it materially affects how Table 7.2 must be read. Both captures used the loop recording's arm segment lengths rather than each recording's calibrated lengths, and the rail capture additionally retained the receiver's default torso length. Describe Table 7.2 as an end to end rendered rig result under the actual capture configuration, not as a pure test of rig mapping and display filtering with matched body dimensions. Chapter 9 may state that part of the downstream discrepancy may arise from mismatched rig proportions, but must not quantify that contribution and must not attribute the entire rendered rig discrepancy to it, because display filtering, rig mapping and other downstream stages remain confounded. Keep the bare kinematic model error separate from the rendered rig error throughout.
Why: The reported rendered rig errors were produced with avatar proportions that do not match the recordings. A reader who takes Table 7.2 as a clean test of the display path would draw the wrong conclusion. The configuration is a fact about how the capture ran, which the evidence supports, unlike an apportionment of the error, which it does not.
Alternatives: Omit the configuration and report only that the discrepancy appears downstream (rejected: leaves a known and documented cause unstated); quantify the contribution of the proportion mismatch (rejected: would require a separate controlled rerun to isolate it).
Evidence: Author's decision of 2026-09-12. The rig_dimensions.csv file beside each capture and the receiver's serialized configuration fields record the avatar proportions; bare_model.json documents the calibrated lengths against the avatar lengths for both recordings and both arms.
Reversibility: Add a separate quantitative comparison if a controlled rerun with recording specific arm lengths and the correct torso length becomes available. The present statement needs no revision in that case, only extension.
Review: Confirm no fraction of the rendered rig error is attributed to the proportion mismatch, that Table 7.2 is described under the actual capture configuration, and that the bare model and rendered rig quantities are never described interchangeably.

ID: D-044
Status: SETTLED
Decision: Define the task phase vocabulary once, in Chapter 2 Section 2.1, where the experimental setup and task are introduced. For the rail task the sequence is grasp, where the hand acquires the cube at its initial position; carry, where the cube is translated from its initial position toward the rail; lift, where the cube is raised from desk level to rail level; slide, where the cube is translated along the rail; and release, where the hand leaves the cube at the far end. The handover recording uses the same physical phases, with the slide additionally containing a right hand segment, a handover interval and a left hand segment. Keep the passage concise: it is a task definition, not an evaluation result. Later chapters refer back to this definition rather than introducing the terms independently. Do not reintroduce the old Chapter 7 protocol figure unless the prose definition proves insufficient.
Why: D-029 removed the four step protocol drawing and the frame strip, leaving the task phases described nowhere. Chapters 6, 8 and 9 use terms such as the slide, the lift and the grasp with no defined referent. Section 7.2 names four waypoint roles, but those are measurement definitions and do not describe the task as performed.
Alternatives: Describe the phases in Section 7.1 (rejected: repeats setup material that belongs in Chapter 2); reinstate the deleted protocol figure (rejected unless the prose proves insufficient, and it would add to the renumbering); leave the terms undefined (rejected: an examiner would meet them with no referent).
Evidence: Author's decision of 2026-09-12. CH7_INTEGRATION_FIXLIST.md records the vocabulary in use across Chapters 6, 8 and 9; Chapter 2 Section 2.1 already describes the setup and the task in one sentence.
Reversibility: Remove the passage and the pointers together, or promote it to a figure if prose proves insufficient.
Review: Confirm the passage is a task definition carrying no evaluation result, that the five phases are named exactly as above, and that the handover segmentation of the slide is stated. Later chapters must point here rather than redefining a term.

ID: D-045
Status: SETTLED
Decision: The coarse rail height cross check is genuinely dropped. Do not restore the comparison between the reconstructed desk and rail height modes and the 3.8 cm physical rail height. Its removal from Chapter 8 Table 8.1 stands, and any remaining Chapter 9 or Chapter 10 claim resting on it is removed. The 3.8 cm rail height may remain in Chapter 2 as a physical dimension of the apparatus, but never as a Chapter 7 accuracy result.
Why: The restructured Section 7.2 now carries a more direct physical reference for vertical object motion, the W2 to W3 separation of 3.5 cm measured for the ArUco marker centre itself, which is the appropriate quantity to compare with the reconstructed marker centre displacement. The old check is an indirect apparatus geometry cross check that additionally assumes the marker keeps the same height relative to the cube base on the desk and on the rail. It is redundant under the new evaluation design.
Alternatives: Reinstate it in Section 7.2 as a second physical reference (rejected: indirect and resting on an extra assumption the direct measurement does not need); defer the decision until Section 7.2 was built (overtaken, since Section 7.2 now prints the direct comparison).
Evidence: Author's decision of 2026-09-12. D-029 removed the check from Chapter 7; the Chapter 2, 4, 6 and 8 repair pass found and removed the surviving assertion in Chapter 8 Table 8.1; the Chapter 9 revision removed the rail height histogram claim.
Reversibility: Recompute and pin the check under current conventions if a reason to prefer the indirect geometry ever arises. Nothing depends on it now.
Review: Confirm no accuracy claim anywhere rests on the 3.8 cm rail height, and that its surviving use in Chapter 2 is an apparatus dimension only.

ID: D-046
Status: SETTLED
Decision: Report the loop recording's object marker detection coverage as 2058 of 2099 frames under the criterion that the extractor returned a marker pose on that frame, and introduce the count in Chapter 7 Section 7.4.2, where the natural occlusion recording is characterized. Chapter 9 may discuss its implication but must not introduce it and must not cite an unpinned evaluation output. The count is pinned in audit_evidence/ch7_restructured/loop_detection.json. The stricter accepted sample count under the Section 7.2 rule, which additionally requires a finite position, no despiked rejection and no interpolated fill, is 2046 of 2099; it is recorded in the pinned file and in the builder source comment rather than in the prose.
Why: The author required the count to be kept only if it reproduces from current evaluation data, to be pinned, and to be introduced first where the recording is characterized, because object marker availability determines when object assisted recovery can have object information at all. Detection coverage and usable sample count answer different questions, so both are recorded and the one that answers the availability question is the one printed.
Alternatives: Print the accepted sample count of 2046 instead (rejected: it answers whether a sample survives filtering, not whether the detector saw the marker); keep the figure in Chapter 9 from the evaluation output CSV (rejected by the author: unpinned and introduced in the wrong chapter); drop the count (unnecessary, since it reproduces).
Evidence: Author's instruction of 2026-09-12. loop_detection.json records both criteria, the missing frame runs, the grip episode location and input SHA256 values. The count reproduces independently from the pre cleaning filtered track, the unfiltered world track and the extractor sidecar, which records 2058 detections of the object marker over 2099 frames. Of the 41 missing frames, 40 lie in the two hand transfer on the desk and the remaining frame sits at its near edge. All 27 manually labelled frames of Section 7.4.2 carry a detected marker, so the gap does not touch Tables 7.8 and 7.9.
Reversibility: Reprint under the accepted sample criterion if a single coverage convention is later preferred across the chapter. Both counts are pinned, so neither direction needs new data.
Review: A detected frame is not necessarily a usable frame. The pinned file records that a few detected frames at the edges of the gap carry an implausible pose, and the count does not exclude them. Confirm Chapter 9 cites Section 7.4.2 rather than introducing the count, and that the source comment names loop_detection.json.

ID: D-047
Status: SETTLED
Decision: Keep the 2058 of 2099 detection count in Section 7.4.2 and add one sentence clarifying that a detected pose is not necessarily an accepted or reliable trajectory sample, because detection coverage measures whether the extractor returned an object observation, not whether that observation survived later cleaning. Do not introduce the implied speed threshold of 50 centimetres per second into the thesis unless it becomes a formally defined evaluation rule. Do not harmonize detection coverage and accepted sample coverage into a single convention, because they answer different questions. Instead define both terms explicitly: a detected frame is one on which the ArUco extractor returned a pose; an accepted object sample is a returned pose that remained usable after the Section 7.2 cleaning rules. Use these terms consistently wherever 2058 of 2099, 889 of 900 or 1487 of 1499 is reported.
Why: The two counts answer different questions and collapsing them into one convention would lose information. Naming them removes the ambiguity without forcing a false equivalence. The clarifying sentence prevents a reader from treating detection coverage as a statement about sample quality. The speed diagnostic is an informal plausibility observation recorded in the evidence, not a defined evaluation rule, so printing it would introduce a threshold the thesis does not define.
Alternatives: Report only the accepted sample count everywhere (rejected: detection coverage is the quantity that governs whether object assisted recovery has object information at all); report only detection coverage everywhere (rejected: Section 7.2 needs the count of samples that survived cleaning); print the implied speed caveat with its numerical threshold (rejected: an undefined threshold in the prose invites a rule the thesis does not have).
Evidence: Author's ruling of 2026-09-12. audit_evidence/ch7_restructured/loop_detection.json records both criteria and the informal plausibility observation; object.json records the accepted sample counts of Section 7.2. The difference between the two loop counts is exactly the despiked and interpolated rows recorded in the track filter sidecar.
Reversibility: The definitions are prose only and can be restated without touching any evidence file or any number.
Review: Confirm both terms are defined once, that every reported coverage figure uses the matching term, and that no implied speed threshold appears anywhere in the thesis prose.

ID: D-048
Status: SETTLED
Reaffirmed 2026-09-12 by the author: keep this decision in force, do not alter [50] or renumber references during chapter level builds, and at full V7 assembly remove uncited [50], perform the planned global first appearance renumbering, and verify every in text citation against the final bibliography.
Decision: Do not renumber references at the chapter build stage. Leave reference [50] in place for the current chapter level builds, record it as uncited and scheduled for removal during the full V7 reference assembly pass, create no visible gap at [50] in intermediate builds, and do not shift [51] to [58] at this stage. During the full V7 assembly, remove uncited entries, perform the planned global first appearance renumbering, and then verify every in text citation against the final bibliography. Reference [49] is cited in the closing paragraph of Section 10.2, with the marker placed after the hardware scaling clause.
Why: references.md states that entries [1] to [52] carry the frozen V6 numbering and that renumbering by first appearance happens only at the full V7 assembly, not per chapter. Reference [50] sits inside the frozen range, and [53] to [57] form a deliberate per filter grouping appended for a supervisor comment, with [58] the Intel D400 tuning guide. A local renumber would break numbering the supervisor has already reviewed and disturb that grouping. This supersedes the earlier instruction to renumber [51] to [58] immediately, which was given before the frozen numbering policy in references.md was known.
Alternatives: Renumber [51] to [58] down by one and update the 27 citation occurrences across six builders (rejected: breaks the frozen V6 numbering and the per filter grouping); delete [50] and accept a printed gap (rejected: a visible hole reads as an error in an intermediate build); leave [50] uncited with no record (rejected: the entry would be forgotten at assembly).
Evidence: The header of writing/v8/condensed/references.md states the frozen numbering policy and the assembly time renumbering rule. A sweep of all built parts and all builders found [49] and [50] to be the only uncited entries of [1] to [58]; after [49] was cited, [50] is the only one remaining. Reference [18] was verified still cited twice in Chapter 1 and is not orphaned by the Chapter 1 roadmap correction.
Reversibility: The removal of [50] and the global renumber are deferred, not cancelled. Nothing needs undoing if the assembly pass proceeds as planned.
Review: At full V7 assembly, confirm [50] is removed, the first appearance renumbering is applied globally rather than per chapter, and every in text citation is verified against the final bibliography. Until then [50] stays in the list and the numbering is unchanged.

ID: D-049
Status: SETTLED
Decision: Name the human reconstruction acceptance concept a valid landmark frame, defined in Section 7.3 as a frame in which the shoulder, elbow, wrist and required torso inputs used by the Section 7.3 reconstruction satisfy the landmark validity checks. Use the term consistently for the counts of 650 and 589 and of 1156 and 1095. Do not call these frames simply accepted frames, because Chapter 7 already uses accepted object sample for a different object trajectory cleaning concept. Three terms remain distinct throughout the thesis: a detected frame is one on which the object extractor returned a pose; an accepted object sample is a returned object pose that survived the Section 7.2 cleaning; a valid landmark frame is one in which the human landmark inputs required by Section 7.3 passed the landmark validity checks.
Why: D-047 defined two object terms and left the human acceptance concept unnamed, so Chapter 7 carried three acceptance notions with only two names. The unnamed one sat close enough to accepted object sample that a reader could mistake a human landmark count for an object count. Naming it removes the ambiguity without merging concepts that answer different questions.
Alternatives: Leave the human concept unnamed and rely on context (rejected: the two surviving uses of accepted are then ambiguous); reuse accepted frame for it (rejected by the author: collides with accepted object sample); merge the object and human conventions (rejected under D-047, which keeps them separate by design).
Evidence: Author's ruling of 2026-09-12. The verification pass that produced scripts/verify_ch7_restructured.py identified the unnamed third concept. Section 7.3 already carries the phrase in its heading, Human Reconstruction Accuracy under Valid Landmark Measurements, so the term matches the existing structure. The counts are pinned in audit_evidence/ch7_restructured/human.json and bare_model.json.
Reversibility: The definitions are prose only and can be restated without touching any evidence file or any number.
Review: Confirm the term is defined once in Section 7.3, that every human count in that section uses it, that no human count is called an accepted frame, and that the three terms stay distinct wherever the thesis reports a coverage or sample figure.

ID: D-050
Status: SETTLED
Decision: Keep the depth patch field in Appendix E.1 as part of the recorded data description. Its status is documentary only: it was stored by the pipeline, no analysis or result in this thesis uses it, and it must not be cited as evidence for any claim in Chapters 7 to 10. Do not remove it merely because it has no downstream consumer, unless Appendix E is later redefined to document only analysed quantities.
Why: Appendix E documents what the recording pipeline stores, not only what the evaluation analyses. Removing a recorded field because the thesis stopped analysing it would misrepresent the recorded data. The removal of the depth implied marker size diagnostic under the author's instruction of 2026-09-12 left this field without a consumer, but that changes what the thesis claims from it, not what the pipeline recorded.
Alternatives: Remove the passage because nothing reads the field (rejected: the appendix would then describe the recorded data incompletely); keep the field and restore a use for it (rejected: that would reintroduce the diagnostic the author removed); leave the question open in the builder comment (overtaken by this ruling).
Evidence: Author's ruling of 2026-09-12. The field is the median of a 5 by 5 patch of aligned depth values at each marker's centre pixel, recorded at detection time. The pose recovery never reads it, and a grep of every builder confirms its only surviving appearance in the thesis is the depth sample column of Table E.1 in Appendix E.4. The printed Appendix E.1 passage already states that it is recorded, that the pose recovery never reads it and that no analysis of this thesis reads it, so the prose required no change; the prohibition on citing it as evidence is recorded in the builder source comment and here rather than printed, because it instructs writers rather than readers.
Reversibility: Remove the passage only if Appendix E is redefined to document analysed quantities only. Nothing in Chapters 7 to 10 depends on the field either way.
Review: Confirm no claim in Chapters 7 to 10 cites the depth patch as evidence, and that the appendix continues to describe it without asserting a use the thesis does not contain.

ID: D-051
Status: SETTLED
Decision: Rename the task phase formerly called the grasp to the object acquisition, throughout the task phase vocabulary of Chapter 2 Section 2.1 and every later phase reference. Do not rename Chapter 5's technical use of grasp, grasp state or the grasp offset h; those name the rigid hand object attachment model and are a different concept. The five task phases are therefore object acquisition, carry, lift, slide and release, with the handover recording's slide additionally containing a right hand segment, a handover interval and a left hand segment.
Why: D-044 introduced the grasp as the first task phase while Chapter 5 already used the grasp for the rigid hand object attachment that defines the offset the object assisted recovery depends on. A reader meeting the grasp in a later chapter had two live referents, one of them load bearing for the recovery method. Renaming the new phase rather than the established technical term leaves the mathematics and its vocabulary untouched.
Alternatives: Rename Chapter 5's technical usage (rejected: it is established, mathematically tied to the offset h and used across seven passages); keep both and distinguish them by context (rejected: the ambiguity is exactly what the phase vocabulary was introduced to remove).
Evidence: Author's ruling of 2026-09-12. A sweep of every builder found the phase term printed in exactly one place, the Section 2.1 definition, with Chapter 5 carrying seven occurrences of the technical sense and the remaining mentions confined to non printed docstrings. The replacement Chapter 10 uses no task phase term at all, so the author's verbatim text is unaffected.
Reversibility: The rename is prose only and touches no number and no evidence file.
Review: Confirm the phase is named object acquisition wherever the phase vocabulary is used, that Chapter 5's grasp, grasp state and offset h are unchanged, and that no later chapter reintroduces the grasp as a phase name. Note that Figure 4.1's caption uses grasped as an ordinary verb describing what a panel shows, which is closer to Chapter 5's sense than to the phase; it was left unchanged and is flagged for the author.

ID: D-052
Status: SETTLED
Decision: This work is an undergraduate bachelor's honours thesis. Do not describe the thesis, the committee, the examination, the submission process or the degree level as graduate level anywhere. Keep the bachelor's honours designation unless an authoritative institutional source specifies otherwise. Remove any note suggesting the degree level is uncertain. Treat confirmation of the degree, department and date lines against the current institutional template as a pre submission administrative verification item, not a content rewrite.
Why: The assembled thesis build printed a note inferring a graduate programme from the supervisor's request for an examining committee. The author confirmed that inference was wrong. A committee request does not establish a degree level, and an unresolved note in the build output invites a later writer to change the designation on the strength of the same wrong inference.
Alternatives: Infer the degree level from the supervisor's committee comment (rejected by the author as incorrect); leave the uncertainty note in place pending confirmation (rejected: it perpetuates the wrong inference).
Evidence: Author's correction of 2026-09-12. The stale note lived only in condensed/scripts/build_thesis.py, in the placeholders report it generates. A sweep of every built chapter, the front matter and the appendices found no occurrence of graduate anywhere in the thesis itself, so no printed prose required a change. The front matter records the degree as Bachelor of Applied Science in Systems Engineering.
Reversibility: Change the designation only on an authoritative institutional source, not on committee or examination wording.
Review: Confirm no part of the thesis or its build output describes the work, committee, examination, submission or degree level as graduate level, and that the remaining administrative item is a template check rather than a question about the degree.

ID: D-053
Status: SETTLED
Decision: The ArUco translation origin is geometrically located at the marker centre, so the object endpoint of Section 7.3.3 and the object endpoint of Section 7.2 are the same physical point. Use marker centre consistently in Chapters 7 and 9 for this quantity, and state the equivalence once in the thesis. The author's approximately 16 centimetre physical reference, which the brief records as measured to the object marker origin, therefore shares its object point with the reconstruction, and the external physical check of Section 7.3.3 is valid on point identity. Section 7.3.3 requires no evidential downgrading.
Why: The author ruled that the naming difference must not be resolved by editorial renaming, and that the external physical check is valid only if the reconstructed and physically measured wrist object quantities use the same object point. The point identity was therefore traced through the code rather than inferred from the symbol names.
Alternatives: Rename the prose for consistency without tracing the geometry (explicitly prohibited by the author); treat the numerical agreement between the medians and the 16 centimetre reference as evidence that the points coincide (rejected: on a 45 millimetre marker the candidate points differ by at most a few centimetres, so agreement is not evidence of point identity).
Evidence: The object point layout in v1/aruco/extract_aruco_poses.py places the PnP corners at plus and minus half the side about the origin, symmetric about it, so the translation origin is the centre of the printed square; the solve uses those points through solvePnPGeneric with IPPE_SQUARE. The 45 against 50 millimetre correction in eval/gt/scale_correction.py with eval/common/marker_size.py multiplies the translation by 0.9, and the layout stays symmetric at any declared side, so it rescales the distance to the centre and does not move the reference to another point on the marker. The chain continues through calibrate_scene, frames, filter_object_track, clean_object_track and eval_rail_scenario without changing the point estimated. The cube centre is a different point and appears only in the hold gate, never in a reported distance. Recorded in audit_evidence/ch7_restructured/spatial_check.json with the full traced chain.
Reversibility: The naming is prose only. The point identity is a property of the code and changes only if the object point layout changes.
Review: Confirm the equivalence is stated once, that marker centre is used consistently for this quantity in Chapters 7 and 9, and that the separate coordinate frame sense of origin in Chapters 5 and 6 is not swept into the rename. Do not accept numerical agreement as evidence of point identity in any future check.

ID: D-054
Status: SETTLED
Decision: Adopt a four class notation policy for coordinate frames, rotations and transforms, applied semantically rather than by symbol shape. Class 1, a frame relative proper rotation, is written with both frame labels as a left superscript reference frame and a left subscript described frame. Class 2, a homogeneous frame transform, likewise always carries both frames. Class 3, a rotation operator, follows Craig's operator form with an axis and an angle, carries no frame pair, and must be explicitly identifiable as an operator in the surrounding definition. Class 4, a handedness changing basis map such as S, F or M, is a separate symbol class and is never written in Craig rotation or transform notation, because doing so would be semantically incorrect. Craig style frame cancellation applies only to proper rotations and homogeneous transforms between right handed frames and must never be applied through a class 4 map. Where an orientation is expressed in a basis related by a handedness changing map, print the change of basis explicitly as a conjugation or similarity rather than a one sided multiplication, and if a proper re based body frame results, name and define that frame explicitly and resume Craig notation only once the orientation is again a proper rotation. Class 4 maps are declared once by source basis, destination basis, matrix form, determinant, and whether they are self inverse. Rodrigues' formula in equation E.1, the elementary joint rotations, and any other matrix whose role is to rotate a vector rather than to describe one frame relative to another are class 3 and are exempt from the two frame requirement.
Why: The author's earlier rule that every printed rotation and transform must carry both frame labels cannot be applied literally to two categories without asserting something false. An operator acts on a vector and has no source and destination frame pair, so inventing one would claim a relationship it does not have. A handedness changing map has determinant minus one and is not a proper rotation, so Craig notation would both misdescribe it and license frame cancellation across it. The notation audit established that cancellation genuinely fails there: the naive chain yields a matrix of determinant minus one that is not a valid rotation and is a physically wrong orientation, which is why the implementation conjugates instead.
Alternatives: Apply the two frame rule literally to every printed symbol including operators and improper maps (rejected: uniform on the page but semantically false, and it would lead a reader to apply an invalid chain rule); factor improper maps away wherever possible (useful in one equation where the improper factors pair off, but it does not cover every appearance).
Evidence: Author's ruling of 2026-09-12. Three independent read only audits recorded in CRAIG_NOTATION_AUDIT_ch2_ch4.md, CRAIG_NOTATION_AUDIT_ch3_ch5.md and CRAIG_NOTATION_AUDIT_ch6_ch8.md, covering 191 items. The camera to Unity linear map is exactly improper orthogonal, confirmed algebraically, numerically from the scene calibration, and from audit_evidence/ch7_restructured/human.json which records a determinant of minus one with an orthogonality error of about 1.9e-15. All three audits independently found no wrong transformation direction anywhere in the code.
Reversibility: The policy governs printed notation only. It requires no change to any number, any transformation direction or any code path.
Review: Confirm every printed proper rotation and homogeneous transform carries both frames, that every operator is identifiable as an operator, that no class 4 map carries Craig notation, and that no composition cancels frames across a class 4 map.

ID: D-055
Status: SUPERSEDED
Superseded by: D-056. The author replaced single letter frame labels with semantic frame names, which dissolves all four symbol collisions this entry was written to resolve. No letter is reassigned and no existing quantity is renamed.
Decision: Resolve the four notation symbol collisions individually rather than by a blanket rule. Keep U for the standard singular value decomposition factor and rename the Unity frame. Separate the two frames currently both called W, which differ by about 32 degrees, keeping W for the calibrated world frame and renaming the levelled or display frame to a distinct symbol such as L or D, subject to a collision check against the approved frame inventory. Reserve P for Craig style point and position notation and rename the person space frame. Keep t for time and never use a bare t for translation, using the Craig origin position form or a distinct position symbol where compact block notation is required. Produce the occurrence counts and affected equations for the concrete replacement letters before any edit is applied. No Craig style relabelling of any expression, including equation 3.22, may begin until the thesis wide frame inventory is approved by the author.
Why: A blanket rule in either direction would damage one convention to serve the other. The singular value decomposition and Craig's point notation are established outside this thesis and should keep their letters, while the frames that collide with them are local and can be renamed. The two frames sharing the letter W are 32 degrees apart and a reader cannot currently tell which is meant, which is how the Chapter 5 attribution error went unnoticed.
Alternatives: Frames win every collision (rejected: would rename the singular value decomposition factor and Craig's point symbol); mathematics wins every collision (rejected: would force frame relabelling across every chapter for no gain on the two collisions where the frame is the local symbol).
Evidence: Author's ruling of 2026-09-12. The collisions and their locations are recorded in the three notation audits: U as both the Unity frame and the singular value decomposition factor one page apart, W as two distinct frames, P as both person space and Craig's point symbol, and t as both translation and time one page apart.
Reversibility: Letters can be reassigned before the edits are applied. Nothing is applied until the inventory is approved.
Review: This entry closes as SETTLED once the frame inventory is approved and the concrete replacement letters are chosen with their collision checks and occurrence counts. Check each proposed letter against every symbol used anywhere in the thesis, not only against frames.

ID: D-056
Status: SETTLED
Decision: Use semantic frame names for system level frames where the names are short and unambiguous, for example Sensor, Camera, World, Unity, Display and LevelledWorld, and write Craig frame relations directly with those names rather than forcing single letters. Retain compact approved symbols only for local kinematic and link frames, where long semantic names would make equations unreadable, with every such symbol defined in the frame table. The requirement is semantic clarity and explicit parent and child frames, not single letter frame names. Keep existing uses of single letters for segment lengths, landmark identifiers, error quantities and other non frame quantities unchanged.
Why: The notation audit established that every candidate single letter was already carrying another meaning. U was both the Unity frame and the singular value decomposition factor, C both the sensor frame and the sample covariance matrix, W two distinct frames 32.04 degrees apart, P both person space and Craig's point symbol, L the most loaded letter in the thesis across segment lengths, landmark names, the levelling matrix and the marker side, and t had three meanings including a frame index. Semantic names remove every one of these collisions at once without renaming a single existing quantity, and they satisfy the binding requirement that both frames be identifiable in every printed rotation and transform.
Alternatives: Assign a free single letter to each frame (rejected: forces renaming of established quantities such as the singular value decomposition factor or the covariance matrix, and exhausts the available letters); keep the colliding letters and rely on context (rejected: the author's rule requires both frames to be identifiable, and two frames 32 degrees apart sharing a letter is how the Chapter 5 attribution error went unnoticed).
Evidence: Author's ruling of 2026-09-12. Occurrence counts from the corrected frame audit: Unity frame 14 printed occurrences against 3 for the singular value decomposition factor; sensor frame printed as C in 45 places against the swap matrix in 20 and the covariance matrix in 2; world frame 34 printed occurrences; the levelled world 3 lettered and 3 unlettered. FRAME_INVENTORY.md records the full inventory.
Reversibility: The naming is prose only and touches no number, no transformation direction and no code path.
Review: Confirm every printed frame relative rotation and homogeneous transform identifies both frames by name, that no existing non frame quantity was renamed, and that compact symbols appear only for local kinematic and link frames and are defined in the frame table.

ID: D-057
Status: SETTLED
Decision: Treat equation 3.22 as a class 3 rotation operator rather than a frame relative rotation. It is the system's existing un-swing step, which actively rotates the relevant vector to remove the swing component before the subsequent two argument arctangent evaluation. Write it in Craig operator form with the actual axis and angle the equation uses. Do not introduce a new intermediate frame for this operation. The surrounding prose must state explicitly that this rotation is an operator acting on the vector, that it is not a frame relative rotation, and that the components the arctangent subsequently reads are components of the operated vector in the already defined coordinate basis. This is an allowed exception to the two frame rule because that rule applies only to frame relative rotations and homogeneous transforms.
Why: The corrected frame audit found exactly one genuinely unnamed basis in the thesis, the one equation 3.22 maps into, and found that the system's own vocabulary calls the step un-swing in four places rather than naming a frame. An active rotation that removes a component is an operator, and classifying it as such unblocks the equation without adding a frame the system does not have.
Alternatives: Name it as a chain frame with origin, axes and parent (legal under D-054 but adds a frame the implementation never names and requires a new semantic definition from the author).
Evidence: Author's ruling of 2026-09-12. The un-swing vocabulary appears at shoulder.py line 65, in KINEMATIC_MODEL.md at lines 317 and 330, and in thesis Section 3.4.2. The basis is built at shoulder.py lines 79 to 82 and its components are read individually by the two argument arctangent.
Reversibility: Reclassify as a frame if the chain contract is later stated to include an explicit untwisted intermediate frame.
Review: The author's constraint is binding and must be verified before the prose is written: the operator classification is valid only because equation 3.22 performs an active un-swing rotation, not because it re-expresses the same vector in an unnamed coordinate frame. Confirm from the code that the components the arctangent reads are components of the operated vector in an already defined basis. The classification must never be used merely to avoid defining a frame.

ID: D-058
Status: SETTLED
Naming refinement: D-073 replaces Sensor/Person with Camera/Camera' on the author's later instruction; all geometric identities and other names remain.
Decision: Fix the semantic frame names as Sensor, Person, World, Wall, Object, Unity, Levelled, MappedMarker and MappedCamera, with the local kinematic and link frames named directly by their landmarks as L24, L12, L11, L14 and L13. The sensor optical frame is named Sensor rather than Camera, and the gravity levelled evaluation world is named Levelled rather than LevelledWorld. Declare the input of equation 4.3 to be the Unity frame, matching what the implementation actually reads, and correct the prose that calls it the world frame track. The E0 example given in D-056 is withdrawn: it was the earlier audit's label for the basis that D-057 reclassified as an operator, so no such frame is issued.
Why: Sensor is the system's own word in check_unity_log.py and KINEMATIC_MODEL.md, and it keeps a word's distance from MappedCamera and from the Unity point of view camera node, which Camera would sit adjacent to. Levelled is unambiguous because no other frame is levelled, and it is five characters shorter in every left superscript in Chapters 5 and 7. The landmark names are the system's own names for the link frames, are already printed in the thesis 53 times including the caption of Figure 3.3, carry the side without an r or l subscript, and introduce no new symbol. Equation 4.3 reads the Unity columns in clean_object_track.py, and although the swap is orthogonal so both readings give the same number, the thesis must declare the frame the implementation uses rather than the one its prose assumes.
Alternatives: Camera for the sensor frame (rejected: collides in reading with MappedCamera and the Unity camera node); LevelledWorld (rejected on length, since it appears in a superscript slot throughout two chapters); invented link symbols such as B, S_r and E_r (rejected: the system already names these frames by landmark); declaring equation 4.3 to be in the world frame (rejected: the code reads the Unity columns, and a declaration should follow the implementation).
Evidence: Author's rulings of 2026-09-12. Frame name sources are recorded per frame in FRAME_INVENTORY.md. The equation 4.3 input is read at eval/common/clean_object_track.py lines 59 to 61 from the unity_px, unity_py, unity_pz, unity_ex, unity_ey and unity_ez columns. The withdrawal of E0 follows from D-057 and from the verification that equation 3.22 performs an active un-swing rotation whose output components are read in the already defined L12 shoulder frame.
Reversibility: Names are prose only. One substitution reverses any of them.
Review: Confirm no frame label collides with an existing quantity, that every link frame label matches the landmark that defines its origin, and that the equation 4.3 prose no longer calls its input the world frame track.

ID: D-059
Status: SETTLED
Resolved by D-060. The trace established two bases and three origin and basis combinations; the author declared the third a frame and named it Scene.
Decision: Determine whether the Unity side of the system contains one coordinate frame or two, by tracing the rig side read sites from code and data rather than from prose, before any notation is applied. Establish the basis produced by equation 6.1, the basis in which the Unity person log positions are stored, the basis of the positions exported to the committed coordinate pairs, the basis plotted in Figures 7.3 and 7.4, and the transform if any between the equation 6.1 display axes and the avatar rig root and read sites. Do not infer a second frame merely from the Unity hierarchy, and do not collapse the two merely because both are informally called Unity. If all rig side read sites numerically use the same basis as equation 6.1, keep one Unity frame and correct the misleading caption of Figure 2.4(b). If a non identity transform separates the equation 6.1 basis from the rig side read basis used for reported positions, define two distinct frames and print that transform explicitly. Do not edit the thesis until this is resolved.
Why: This is a question of how many frames exist, not of what they are called, so D-056 does not settle it. The evidence is genuinely mixed. Nothing new is expressed beneath the levelling parent node, whose local system is the Unity frame and whose transform the code calls purely presentational, but positions are read above it in the Unity person log, in the committed coordinate pairs and in Figures 7.3 and 7.4, whose axes are labelled in Unity coordinates. The avatar rig is not parented to the levelling node, and the caption of Figure 2.4(b) places the frame at the avatar rig root while equation 6.1 produces the display axes.
Alternatives: Declare one frame and correct the caption without tracing (rejected: would collapse a possible distinction on the strength of a shared informal name); declare two frames because the rig sits outside the levelling parent (rejected: Unity hierarchy alone does not establish a coordinate frame, per the author's rule that a node transform changes a node's pose relative to its parent and not the parent frame itself).
Evidence: The node evidence is in ArucoSceneReceiver.cs at lines 114, 119 to 120, 208 to 211, 315 and 389 to 390, and in IntegratedSceneReceiver.cs at lines 126 and 180. The read sites are the Unity person logs beside the trail figures, audit_evidence/ch7_restructured/human_pairs.csv, and the axis labels written by scripts/make_ch7_valid_joint_figures.py. The calibration mapping used by the evaluation is in scripts/evaluate_ch7_restructured.py.
Reversibility: Either outcome is prose only and changes no error or distance, because the floor drop cancels from every reported error and distance. Correction of 2026-09-12: it does NOT cancel from plotted and printed coordinates. The vertical axis of Figure 7.3 reads 78 to 97 centimetres because of the drop and would read 6 to 16 centimetres without it, and one coordinate is printed in the scene in Table 6.2. The drop is therefore not invisible at those three sites.
Review: The operative test is the basis, not the origin. A pure translation does not change a basis; a rotation does. Two systems may share a basis and differ in origin, and that case must be stated precisely rather than forced into either branch. Three notation rows are blocked on this entry: the caption of Figure 2.4(b) and two Chapter 7 items.

ID: D-060
Status: SETTLED
Decision: The Unity side of the system contains three distinct coordinate frames, not one or two. A coordinate frame is defined by both basis and origin. Unity is the pre levelling display basis produced by equation 6.1. Levelled is the same system after the gravity levelling rotation and before the floor drop translation. Scene shares the basis of Levelled but carries the origin translated by the measured floor drop, and it is the system in which the Unity person log, the committed coordinate pairs and Figures 7.3 and 7.4 actually read and report positions. Scene is therefore not merely a presentational offset. Represent the Levelled to Scene relation as an explicit homogeneous transform with identity rotation and the measured floor drop translation. Do not change the numerical values printed in Figures 7.3 and 7.4 in order to eliminate this frame. Name the third frame Scene, from the system's own words, and keep Unity, Levelled and Scene distinct. Do not rename Scene merely to avoid visual similarity with Sensor, because the full semantic frame labels are unambiguous.
Why: The author's decision rule asked whether the rig side read sites use the same basis as equation 6.1. They do not. A basis test on difference vectors, which removes every origin and translation, gave a maximum discrepancy of 0.108 metres on the rail recording and 0.054 metres on the handover recording against the equation 6.1 basis, while the same comparison against the levelled basis gave 0.000002 metres. Lengths were preserved to 2 micrometres while directions differed by a median of about 30 degrees, which is an isometry that is not the identity, that is a rotation and not a translation. A blind least squares recovery of the map from the two logged coordinate sets alone returned a rotation of 32.0363 and 32.0394 degrees on the two recordings, matching the levelling rotation to about 1e-5. The second basis is not new: it equals the levelled basis exactly. The remaining distinction is the origin, which is read at four sites, three of them printed.
Alternatives: Keep two frames and record the floor drop as a presentational offset named at the three print sites (rejected: Figures 7.3 and 7.4 would then plot the levelled frame plus 71.6 centimetres on axes labelled in Unity coordinates); keep two frames and replot the figures in levelled coordinates (rejected by the author: the printed values must not change in order to remove a frame).
Evidence: Author's ruling of 2026-09-12 and the trace recorded in UNITY_FRAME_RESOLUTION.md. Equation 6.1 contains no levelling and no drop, at v1/aruco/frames.py lines 38 to 40 and 85 to 88. The rig is never parented and never read locally; the only parenting call in IntegratedSceneReceiver.cs is the anchor at line 160, and no bone is read with a local position or rotation. The levelled basis and the scene basis agree to 1.1e-16 on a shared 900 frame object track, with a constant offset of 0.716215 metres in the vertical axis. The name comes from ArucoSceneReceiver.cs line 308, check_unity_log.py line 148 and Table 6.2.
Reversibility: Prose only. No error, distance or printed coordinate changes.
Review: Confirm the three frames are never conflated, that the Levelled to Scene relation is printed as an explicit transform with identity rotation, and that the floor drop is stated rather than implied at the three sites where it is visible in printed or plotted coordinates. Note that the caption of Figure 2.4(b) is wrong in four separate ways and is corrected separately; the figure itself is an accurate picture of Scene.

ID: D-061
Status: SETTLED
Decision: Write the levelled to scene relation in Craig notation as a frame transform whose left superscript is Scene and whose left subscript is Levelled, so that a point expressed in Levelled maps to Scene by that transform. Do not write a concatenated symbol such as LevelledScene T, and do not parameterize the transform by the floor drop unless the text explicitly introduces it as a parameterized transform. Define the translation column explicitly. Where the vertical floor offset is denoted d, define d separately as the recording specific scalar used in that translation vector, rather than as a constant of the system. Introduce each Unity side frame where its defining transform is established: Unity in Chapter 2, where the display coordinate convention is first introduced; Levelled in Chapter 6 at the point where the gravity levelling rotation is defined; Scene immediately after, where the floor drop translation to the final scene coordinates is defined. Do not place Levelled or Scene in the Chapter 2 frame table merely for completeness. A thesis wide frame inventory retained for audit purposes may list all three, but the printed thesis introduces each frame where its defining transform is established.
Why: The author corrected a proposed concatenated notation and required the Craig form, so the mapping direction is readable from the symbol itself. The floor drop is recording dependent, measured as 0.716215 metres on the rail recording and 0.709312 metres on the handover recording, so printing a single value as though it were a property of the system would be a silent methodological choice. Introducing a frame before its defining transform exists would require a reader to accept a coordinate system whose construction has not yet been given.
Alternatives: Print one floor drop value as a system constant (rejected: it is recording dependent); define all three Unity side frames in the Chapter 2 frame table for completeness (rejected by the author: each frame is introduced where its defining transform is established).
Evidence: Author's rulings of 2026-09-12. The two floor drop values are recorded in FRAME_INVENTORY.md and in UNITY_FRAME_RESOLUTION.md, traced to ArucoSceneReceiver.cs and the two receivers. The levelled and scene bases agree to 1.1e-16 on a shared 900 frame track, so the rotation block of this transform is the identity.
Reversibility: Prose only. No number changes.
Review: Confirm the transform is printed in Craig form with an explicit translation column, that d is stated as a recording specific scalar, that no frame is named in the printed thesis before its defining transform is given, and that the audit inventory is not confused with the printed introduction.

ID: D-062
Status: SETTLED
Outcome: the frame branch fired for all four matrices, opposite to the D-057 precedent. Evidence in BONE_ROTATION_CLASSIFICATION.md. Consequences are recorded in D-064.
Decision: Classify R_rest and the bone rotations R_0, R_1 and R_2 of equations 6.4 and 6.5 by running the same active versus frame relation test that settled equation 3.22, rather than by analogy with the precedent that entry set. Establish from the implementation what physical or frame quantity R_rest stores at spawn, what frames R_0, R_1 and R_2 are expressed in, whether these matrices are actively applied to vectors and bones or represent passive frame orientations, whether the multiplication order matches operator semantics, and whether the T pose and spawn axis coincidence is required for the equations to be valid or merely true in practice. If they are genuine active rotation operators, use class 3 operator notation. If they represent bone, model or scene frame orientations, use Craig two frame notation and state the necessary spawn and T pose assumption explicitly. Do not edit equations 6.4 or 6.5 until the classification is established.
Why: The role of R_rest in the product is a bone axes to model frame rotation, but its value in the code is the bone's world rotation captured at spawn. These coincide only if the rig spawns with its body axes coincident with the scene axes, which is asserted in a code comment and nowhere in the thesis. A numerical coincidence is not evidence that the notation is correct, and the author has explicitly forbidden classifying these by analogy with the equation 3.22 precedent.
Alternatives: Classify as operators on the strength of D-057 (explicitly rejected by the author); declare the spawn assumption and use two frame notation without testing (rejected: would assert a frame relation that may not hold).
Evidence: The capture site is IntegratedSceneReceiver.cs lines 239 to 243, the spawn axis assertion is a code comment at lines 237 to 238, the chain is built at lines 358 to 374, and the rig is not parented at line 180. The audit recorded this as UNRESOLVED items U-1 and U-2 in CRAIG_NOTATION_AUDIT_ch6_ch8.md.
Reversibility: The classification is prose only and changes no number or code path.
Review: The test must find a discriminator of the same calibre as the one that settled equation 3.22, where a fixed constant of the frame was rotated and the documentation stated both readings side by side with the code taking the active one. A mixed answer is legitimate if R_rest and the chain rotations are of different classes. This entry closes as SETTLED once the classification is established with evidence.

ID: D-063
Status: SETTLED
Decision: Keep Figure 2.4(b) unchanged and do not re-render it. Rewrite its caption so it accurately describes the final Unity scene coordinate system the image shows, without introducing the formal frame symbol Scene in Chapter 2. Introduce and define Scene formally in Chapter 6, where the levelling rotation and the floor drop translation that produce it are established. At that point Chapter 6 may state explicitly that the final frame shown earlier in Figure 2.4(b) is denoted Scene. Do not forward declare Scene in Chapter 2.
Why: The image is an accurate picture of the final scene coordinate system, so a caption that described the Chapter 2 display axes instead would be false about its own figure. Naming the frame in Chapter 2 would introduce a coordinate system four chapters before the transform that defines it, against the placement rule of D-061. A caption that describes the system accurately without the formal symbol satisfies both, and a back reference from Chapter 6 to the figure closes the loop where the definition exists.
Alternatives: Name Scene in the caption with a forward pointer to Chapter 6 (rejected: forward declares a frame before its defining transform); re-render the figure to show the Chapter 2 display axes (rejected by the author: the figure is accurate and is not re-rendered merely to avoid the early appearance of that coordinate system); leave the caption as it is (rejected: it is wrong in four separate ways).
Evidence: Author's ruling of 2026-09-12. The four caption defects are recorded in UNITY_FRAME_RESOLUTION.md and FRAME_INVENTORY.md: the frame label is 32.04 degrees off, the origin is 71.6 centimetres off, the phrase placing the origin at the root of the avatar rig names an origin that moves every frame per IntegratedSceneReceiver.cs line 379, and the screenshot contains no levelling parent node at all. The figure itself is recorded as accurate.
Reversibility: Caption prose only. The figure file is untouched.
Review: Confirm the caption describes the system shown without using the formal symbol, that Scene is defined in Chapter 6 beside its transform, that Chapter 6 carries the back reference to Figure 2.4(b), and that no forward declaration appears in Chapter 2.

ID: D-064
Status: SETTLED
Decision: Classify R_0, R_1, R_2 and R_rest of equations 6.4 and 6.5 as class 1 frame relative rotations, each carrying both frames. R_0 is the L24 root frame described in person space, R_1 the L14 frame described in the L12 shoulder frame, R_2 the L16 frame described in the L14 frame, and R_rest the bone's authored axes described in its segment frame. The multiplication order is a Craig frame chain whose intermediate indices cancel to give the scene to bone rotation that the code assigns. Issue L16 and L15 for the distal wrist frames under the landmark naming rule of D-058, and issue Bone_k for the driven bone's authored axes as a declared exception to the usage test of the frame inventory, because D-054 forces it once equation 6.5 is printed in Craig form and it is the described frame of that equation's own left hand side. Distinguish the symbol A, which is the Unity frame described in person space in equation 6.2 and the Scene frame described in person space in equation 6.5. Print the spawn and T pose coincidence as a stated assumption and never as an established fact. Add one sentence where R_2 is introduced recording that the same physical rotation is a class 3 operator on the solver side of Chapter 3 and a class 1 frame relation on the Unity side of Chapter 6, because D-054 classifies semantically by use rather than by symbol shape.
Why: The author required the active versus frame relation test to be run rather than settled by analogy with D-057, and the test returned the opposite answer with two independently decisive discriminators. The first is that RootFrameAxes.cs takes the product of the anchor rotation and the root Euler, which is exactly the first two factors of equation 6.5, assigns it, gives it the origin at the hip position, names it the measured body root frame, and draws its three columns as that frame's axes for the Chapter 3 figure, while excluding the rest rotation by name. That is the same structural test that placed equation 3.22 on the operator side, landing here on the frame side. The second is that the reference frame of R_rest is an exposed code parameter whose misuse was observed during live verification, producing a rig that kept its authored facing while the person faced the sensor. An operator has no reference index to get wrong.
Alternatives: Classify as operators by analogy with D-057 (explicitly forbidden by the author, and falsified by the test); print R_rest as a constant re basing factor with no bone frame (rejected on its own terms: the indices then do not cancel, which hides the assumption rather than avoiding it).
Evidence: BONE_ROTATION_CLASSIFICATION.md records the five answers with citations. Nothing is ever transformed by these four matrices; they are assigned as and read as orientations, and on the solver side the same matrices appear transposed, re expressing measured vectors whose components are then read individually. The spawn coincidence is required structurally: a spawn rotation other than the identity produces a per bone error that differs between bones, so the arms would go wrong relative to the trunk. It is asserted in two code comments and bounded to about 8.2 degrees about only two of three axes by one capture log, so it is a bound and not a proof.
Reversibility: The classification is prose only and changes no number, no transformation direction and no code path.
Review: Confirm every one of the four carries both frames, that the chain indices cancel as printed, that the spawn and T pose assumption is stated as an assumption, that no bare A remains readable as either of its two meanings, and that the Chapter 3 and Chapter 6 classifications of the same physical rotation are reconciled in one sentence. Labelling R_rest does not fix the missing levelling factor of equation 6.5 or the two mutually exclusive re expression rules, which remain outstanding content defects.

ID: D-065
Status: SETTLED
Decision: Figure 2.4(b) must not remain in the final thesis with its baked in panel title naming the frame as U and placing its origin at the root node of the avatar rig. Both claims are false: the formal frame is the Unity scene frame introduced in Chapter 6, and its origin is on the drawn floor, not at the rig root. The no re-render constraint of D-063 is superseded for this figure alone. Recreate the figure with the minimum necessary change, preserving the screenshot content and the overall meaning of the figure while removing the incorrect title. Make no new frame claim inside the image; the corrected caption carries the coordinate system description.
Why: The corrected caption written under D-063 described the finished Unity scene coordinate system, while the image directly above it still asserted a different frame name and a different origin. A caption that contradicts its own figure is worse than either error alone, and an examiner reads the image before the caption. The earlier judgement that the figure was accurate rested on its screenshot content and did not account for the composed matplotlib panel title.
Alternatives: Leave the image and accept the contradiction (rejected by the author); retouch the pixels of the existing asset (unnecessary, since both source images and a generator were found); rewrite the caption to match the false title (rejected: the title is wrong, not the caption).
Evidence: Author's ruling of 2026-09-12. The generator is writing/v7/scripts/make_ch3_sensor_fig.py, which the earlier pass reported as absent because it searched only the v8 tree. Both source images, the sensor front photograph and the rig screenshot, are present under writing/v7/figures/src. The regenerated panel confirms the origin: the axis gizmo is drawn at the floor at the avatar's feet, not at the rig root, which corroborates the trace recorded in UNITY_FRAME_RESOLUTION.md and D-060.
Reversibility: The original assets are untouched. The corrected figure is a new file and the change is one line in the Chapter 2 builder.
Review: Confirm the image makes no frame claim, that panel (a) is unchanged, that the caption alone describes the coordinate system, and that the original assets under writing/v7 and the shared writing/v8 figure were not modified. The project rule against writing under writing/v7 or writing/v8/scripts was observed: the generator copy lives in the condensed scripts directory.

ID: D-066
Status: SETTLED
Decision: Keep the Craig relabelling of Figure 2.5's arrow labels inside the condensed thesis only. The shared generator under writing/v8/scripts and its asset are restored to their committed state, and the condensed thesis uses a labelled copy of the generator that writes a separate figure file. The non-condensed V8 thesis therefore keeps arrow labels that match its own prose.
Why: The notation pass relabelled the arrows of Figure 2.5 by editing the shared generator in place, which regenerated the shared asset. Both the condensed builder and the non-condensed V8 builder read that asset, so the change silently gave the non-condensed thesis Craig labelled arrows while its prose still used the old two letter subscripts. That is an inconsistency introduced into a document nobody asked to change, and it also breaks the project rule that nothing writes under writing/v7 or writing/v8/scripts.
Alternatives: Keep the in place edit (rejected: leaves the non-condensed thesis internally inconsistent and violates the write rule); drop the figure relabelling from the condensed thesis (rejected: the arrows would then disagree with the chapter's own equations and Table 2.2).
Evidence: The shared asset writing/v8/figures/ch2_fig_frames.png is read by writing/v8/scripts/build_ch2.py and by condensed/scripts/build_ch2.py. Both the generator and the asset were reverted to their committed state and verified unchanged. The condensed copy differs from the shared generator only in the four arrow label strings and its output filename; every arrow direction is unchanged.
Reversibility: Delete the condensed copy and repoint the condensed builder at the shared asset. Nothing under writing/v8/scripts or writing/v7 was modified.
Review: Confirm the shared generator and asset stay untouched, that the condensed figure differs only in its labels, and that the same pattern is used for any future figure the condensed thesis needs to relabel. The sensor and scene figure of D-065 follows the same pattern.


ID: D-067
Status: SETTLED
Decision: Complete the delivered condensed thesis in place, with supported content corrections, final assembly and auditable checks; make no commits.
Why: The author explicitly requests completion rather than a new redesign and overrides the repository commit rule. Preserve D-035 through D-066 and the approved Chapter 10 text.
Alternatives: Restart evaluation or revisit settled naming (outside scope); assume the delivery note describes current Git status (contradicted by inspection).
Evidence: Current request; baseline.json under audit_evidence/final_completion records clean Git status at ff3f078 and hashes of the delivered DOCX/PDF. The older delivery statement that nothing was committed is historical, not the current working-tree state.
Reversibility: All edits are confined to V8 thesis deliverables, condensed sources and audit records; previous artifacts remain recoverable from the baseline commit.
Review: Confirm no commit is created and old decisions remain intact.

ID: D-068
Status: SETTLED
Decision: Print the Chapter 4 to Chapter 5 object chain and the Levelled to Person conversion explicitly, without changing worked-example numbers.
Why: Table 5.1 omits the swap and levelling, and never defines the mapped marker basis. The Section 5.6 matrix is present but its derivation and homogeneous point multiplication are missing.
Alternatives: Relabel the Chapter 4 transform directly (wrong); invent a new frame (unnecessary); remove the example (loses reproducibility).
Evidence: v1/aruco/frames.py object transform and conjugation; eval/offset/carry.py LeveledWorld; eval/failure/recovery_core.py _leveled_to_solver_space; writing/v8/scripts/ch5_worked_example.py. MappedMarker swaps Object axes 2 and 3 at the same marker-centre origin; its handedness is left. The G S R S composition is proper; no Craig cancellation is applied through S or F.
Reversibility: Restore the previous explanatory text; no pipeline or experimental result changes.
Review: Check Table 5.1 and Sections 5.3/5.6 against the explicit implementation chain. Keep the full Levelled/Scene display construction in Section 6.4 per D-061, with a forward reference here.

ID: D-069
Status: SETTLED
Decision: Execute D-048's deferred global first-appearance citation renumber only in the assembled thesis, remove uncited bibliography entries there, and correct Craig's source entry to the requested fourth edition.
Why: Inspection establishes that final renumbering has not happened: the assembled bibliography still contains uncited [50] and the assembly script copies frozen numbers verbatim. check_refs checks internal document targets, not literature citations.
Alternatives: Renumber chapter sources (violates frozen chapter policy); retain uncited [50] indefinitely (fails the requested final assembly); treat 601 internal references as bibliography validation (wrong check).
Evidence: references.md header; build_thesis.py add_references; check_refs.py scope; actual baseline DOCX/PDF. Pearson's fourth-edition page identifies John J. Craig and copyright 2018: https://www.pearson.com/en-us/subject-catalog/p/Craig-Introduction-to-Robotics-Mechanics-and-Control-4th-Edition/P200000003304?view=educator (accessed 2026-09-12).
Reversibility: Remove the assembly-only mapping; frozen source citation identifiers remain unchanged. Bibliography metadata correction changes the edition, not the cited mathematical claims.
Review: Verify every final citation against its source entry, first-appearance order across chapters and appendices, contiguous final bibliography and unchanged chapter numbering. D-048 is fulfilled at assembly, not superseded for chapter sources.


ID: D-070
Status: SETTLED
Decision: Correct the surviving frame and evidential defects in Chapters 3, 4, 6, 7 and 9, and the condensed Figure 2.5 and Figure 6.4 assets.
Why: Read-only independent reviews confirmed the implementation chains but found misleading provenance, omitted mapping factors and unsupported causal interpretations. Several historical defect descriptions are now narrower than originally recorded.
Alternatives: Change Chapter 7 metrics (no numeric defect established); add eight boxes to Figure 6.4 (the actual figure shows four pre-levelling frames); undo D-064 (unnecessary).
Evidence: frames.py:85-88; carry.py:59-80; IntegratedSceneReceiver.cs:160-180,357-403; ArucoSceneReceiver.cs:114-120,208-214,389-397; evaluate_ch7_restructured.py:103-135; Figure 4.1 generator raw desk detections; scaled object CSV frame 533. Chapter 3 equation 3.3 maps parent A components to child B. Pinned natural.json does not measure a proxy uncertainty bound. Tape measurements do not enter PCA line residuals.
Reversibility: Thesis-source/figure-only edits, with historical assets and experiment data untouched.
Review: Equation 6.1 gets the approved two-frame symbols. Equation 6.5 retains its valid Scene factor and gains its explicit levelling expansion; the spawn assumption remains. Figure 6.4 remains four boxes, with the pre-levelling frame correctly identified. Remove Chapter 6's unsupported additive attribution and Chapter 9's proxy-resolution threshold and tape-to-scatter attribution. Scope the Chapter 5 grip bound to this task, not all hands and objects. No Chapter 7 number changes; only the Figure 2.5 glyph position changes numerically, using the scaled detection.

ID: D-071
Status: SETTLED
Decision: Correct the dimensional form of the Chapter 6 scene-point transformation, remove a duplicated Chapter 5 conversion, finish the concrete Appendix E rotation labels, and split equation 6.1 into display lines.
Why: A 4 by 4 homogeneous transform cannot multiply the printed three-component point directly. The repeated Chapter 5 equation adds no mathematical content. Appendix E's worked-example trace still uses an unlabelled frame-relative rotation despite the adjacent named matrix. Equation 6.1 now carries long semantic frame names and benefits from one relation per line.
Alternatives: Treat three-component homogeneous multiplication as implicit (rejected: the thesis explicitly distinguishes the matrix dimensions); leave bare R in the trace (violates D-054); shorten semantic frame names or change the equation renderer (unnecessary).
Evidence: build_ch6.py equation 6.6 defines a 4 by 4 transform and its Section 6.5 example supplies a three-component point. IntegratedSceneReceiver.cs:378 uses anchor.TransformPoint for the pelvis, including the parent levelling and floor translation. build_ch5.py repeats the identical homogeneous wrist conversion twice. build_appendix.py names RSO as the Object frame relative to Sensor, then omits those labels from its trace.
Reversibility: These are mathematical presentation, semantic and formatting corrections to the thesis builders; all example coordinates, experimental numbers and implementation remain unchanged.
Review: Confirm both sides of homogeneous point equations have four components, the pelvis paragraph names Scene, the Appendix E trace uses the same two-frame rotation as its matrix, and equation 6.1 remains complete in the rendered PDF. Preserve the stated spawn-axis assumption and the existing renderer fixes.

ID: D-072
Status: SETTLED
Decision: Verify the new frame chains with the existing 1e-9 full-precision diagnostic tolerance and a 2e-6 tolerance for serialized matrix/Euler comparisons, and retain obsolete trail-check failures as explicitly historical checks.
Why: Full-precision round trips and six-decimal stored representations have different numerical precision. Old trail embedding assertions target figures deliberately removed by D-029 and cannot validate the current chapter.
Alternatives: Demand exact equality after serialization (not numerically meaningful); restore removed figures to satisfy old assertions (violates the settled evaluation structure); silently call those checks passing (false).
Evidence: ch5_worked_example.py existing 1e-9 assertion; six-decimal stored rotation matrix and Euler fields. A row norm bounds three half-unit last-place matrix errors, with the angle rounding contribution also covered by 2e-6. verify_ch7_restructured.py independently checks the current coordinate pairs and metrics. Legacy checks pass source and capture preservation before failing obsolete embedding expectations.
Reversibility: Tighten serialization checks after preserving more input precision. No experiment acceptance rule or reported result changes.
Review: The new frame verifier must identify these as numerical representation checks, preserve the empty-slot/table-grid regression checks, and report all failures honestly. Legacy logs remain in audit_evidence/final_completion.

ID: D-073
Status: SETTLED
Decision: Rename the current thesis frame {Person} to {Camera'} and {Sensor} to {Camera}, keeping semantic {World}, {Object}, {Unity}, {Levelled} and {Scene}; preserve Craig's point symbol P and all non-frame code variables.
Why: The author first requested y-up camera C' and then explicitly preferred Camera' for specific equations. The former name could imply a person-centred origin, whereas this frame shares the raw camera optical origin and only flips y. Semantic Camera and Camera' make that relationship explicit without changing the geometry.
Alternatives: Blindly replace every P (would corrupt point symbols, swap matrices and paragraph tags); rename the moving torso frame (wrong, it is L24); use compact C/C' everywhere (refined by the author's preference for Camera').
Evidence: Author's latest messages; read-only review of Chapters 2, 3, 5 and 6 and the assembled DOCX; v1/kinematics/root_frame.py unity_from_sensor multiplies by [1,-1,1] without translation; recovery_core/carry and Unity receiver undo that same flip. Whole-repository scan found no alternative frame-P origin, but found non-frame P as swap matrix and position variables.
Reversibility: Terminology, frame labels and locally regenerated figures only. Existing matrices, data, numeric values and algorithms are unchanged.
Review: Camera' is explicitly not person-centred and only names the camera-coordinate convention used for body kinematics. Scan current thesis and figure generators for stale frame labels. Preserve frozen v1/Unity and superseded drafts, raw data and historical audit records, reporting their retained vocabulary rather than rewriting history. This supersedes only the Sensor/Person naming clauses of D-058, not its semantic notation policy or frame identities.

ID: D-074
Status: SETTLED
Decision: Round equation-grid twips consistently and exclude explicitly hidden n-ary limits from empty-script regression failures.
Why: int(5.6*1440) produced 8063 rather than the 8064 twips written to cells, a one-twip representation mismatch. Hidden summation upper limits are intentional OMML and do not render placeholder boxes.
Alternatives: Change the equation widths (unnecessary); ignore every empty script (would miss the actual prior renderer defect); call a one-twip discrepancy the old half-table clipping failure (unsupported).
Evidence: verify_final_frames.py run on rebuilt parts; table grids versus cell widths; m:naryPr/m:supHide=1 on four Chapter 5 summation limits. Shared eqn.py and build_ch4.fit_eq_table contain the floating-point truncation.
Reversibility: Restore truncation or overbroad checking; no mathematical or experimental value changes.
Review: Ordinary empty scripts remain failures; only explicitly hidden n-ary limits are exempt. Verify grid/cell consistency and visually inspect the final render.

ID: D-075
Status: SETTLED
Decision: Correct the remaining parent/local coordinate descriptions identified by independent review, without changing joint equations or numerical results.
Why: The author explicitly requested verification that the equations demonstrate their parent and local coordinates correctly. Correct frame labels alone do not fix prose that describes a different quantity or destination.
Alternatives: Leave the sentences as general descriptions (misleading); change the tested mathematics to match them (wrong).
Evidence: Chapter 3 equation 3.19 and Chapter 6's stream carry root Euler angles and distinct shoulder/elbow coordinates, not three Euler angles per driven bone. Chapter 3 root/shoulder bases inherit hip-line orientation; the elbow frame's first axis follows the upper arm. Appendix D.2 deprojects pixels to raw Camera, so its heading must say Pixel-to-Camera Mapping rather than Pixel-to-World Mapping. Detailed checks are recorded in final_completion/parent_local_review.md and figure_semantics.md.
Reversibility: Restore the prior descriptions; all underlying coordinates, tests and data remain unchanged.
Review: Verify reference frame in left superscript, described frame in left subscript, input components in the described frame and output components in the reference frame. Points between different origins require homogeneous transforms; direction vectors use rotation alone. Keep the active un-swing and improper basis maps distinct and preserve the spawn-axis assumption.

D-075 additional verified sites: Chapter 2's inline 4 by 4 transform originally multiplied three-component points without homogeneous coordinates; it now appends 1 on both sides, matching equation 3.2. Figure 2.5 arrows indicate the described pose relative to the reference origin, not coordinate conversion flow; the caption states the reverse direction of point conversion. Figure 6.4 anchor includes translation, so its image now describes a proper rotation block rather than calling the whole anchor a rotation. These refinements preserve the transformations and arrow geometry.

ID: D-076
Status: SETTLED
Decision: Repair the concrete formatting and embedded-frame defects found in final PDF visual inspection, then rebuild and inspect the affected pages again.
Why: XML checks cannot establish rendered visibility. Physical PDF pages 76 and 79 clip Table 5.1's first symbol cell and a long unnumbered least-squares derivation. Figure 5.3 retains World/Object labels where its mathematics and caption require Levelled/MappedMarker. Figure 7.4 has overlapping labels between plot rows.
Alternatives: Deliver XML-correct but clipped mathematics (unreadable); shorten or relabel frames to conceal width (violates semantic notation); change plotted quantities (unnecessary).
Evidence: Direct pdftoppm/view_image inspection of the 184-page intermediate final render, with reviewer records in audit_evidence/final_completion. The displayed object-pose conversion on page 78 is complete; the following three-term sum on page 79 crosses the page edge. Existing Figure 5.3 generator supplies the stale baked-in labels.
Reversibility: Restore original wrapping or figure typography; all numerical data, equations and geometric relationships remain unchanged.
Review: Split long derivations and multi-symbol cells across lines, regenerate only condensed-local figure copies where shared assets are frozen, and correct plot spacing without changing trajectories. Keep captions attached where a detached caption is confirmed. Re-run semantic/figure identity checks and inspect the final render.

D-076 additional visual findings: Figure 5.1's flow image also retained the superseded World/R_obj input description, so its condensed-local copy follows Section 5.3's Levelled/MappedMarker chain. Figure 7.4 row separation uses hspace=0.16, selected as a formatting allocation from the observed overlap, not an experimental constant; both joint-trajectory figures label their actual axes Scene. Figure 3.1's detached caption is kept with its image. All plotted coordinates, selections and measurement results remain fixed.

D-076 appendix visual finding: Table E.1's header was split across physical PDF pages 174/175, leaving 'frame (m)' isolated on the next page. Keep that header row intact with its first data row; no table value or caption changes.

D-076 renderer recheck: the new wrapped Chapter 5 derivation exposed LibreOffice's rejection of a leading binary '=' in equation-array continuation lines, rendered as red error glyphs. State in prose that the three displayed sums are equal forms of the same objective and display each complete sum on its own line. This retains all expressions and their equality without introducing a new symbol or changing the mathematics. Reinspect page 80 after rebuilding.

ID: D-077
Status: SETTLED
Decision: Deliver the completed DOCX and its 184-page PDF with final evidence and explicit remaining limitations; retain the successful document workflow rather than invoke the author's conditional LaTeX fallback.
Why: The final source state builds and the previously observed equation/figure defects are visually cleared. A format migration is unnecessary to complete the requested corrections and would create another assembly to validate.
Alternatives: Migrate to LaTeX despite the successful build (unnecessary); declare all old diagnostic scripts passing (false, because obsolete trail-embedding assertions remain); fabricate missing approval or spawn evidence (unsupported).
Evidence: Final PDF SHA256 08f85efbc57af62f9b5e2a26b5761cc6e513e8c747e0982167555e8109b1029e; final DOCX SHA256 00eb9037ca34c93838d1afa26c2ed196209cf7cdc2dc152b3595fe14999c6906. Final frame checks PASS 16, Chapter 7 PASS 1147 / SKIP 21 / FAIL 0, check_refs 607 with no unresolved target or numbering gap, assembly citations 132 occurrences / 57 entries. Final visual reviewers cleared the inspected mathematical, figure and appendix pages, including the last page 80 correction.
Reversibility: All current changes remain uncommitted in the V8 track; previous history and frozen inputs are preserved. A later format conversion can reuse these validated sources and evidence.
Review: Delivery addendum and SESSION_REVIEW.md distinguish current checks, historical diagnostic exceptions, assumptions and manual Word-only/institutional QA. The author authorized LaTeX if generation proved difficult, not a mandatory format change. Completion date: 2026-09-13. No commit or push is made.


ID: D-078
Status: SETTLED
Decision: Accept the author's new authorization to commit and push the completed thesis, then perform a fresh whole-thesis equation review, fix supported defects, rebuild as needed and push the reviewed result.
Why: The latest request explicitly overrides the earlier no-commit instruction. The first delivery is already verified; the second iteration must add an independent equation review and preserve explicit limitations rather than invent evidence.
Alternatives: Continue withholding commits (contradicts the latest request); rewrite all equations without a defect (unnecessary); force-push or replace history (not authorized or needed).
Evidence: Author's two explicit messages on 2026-09-13. git ls-remote identifies master as the remote default, with no main branch; origin/master is 347f873 and is an ancestor of the current ff3f078 thesis revision. The author was asked asynchronously whether main meant this default branch or a new branch.
Reversibility: Normal additive commits and fast-forward pushes preserve prior history. Any subsequent mathematical correction receives its own evidence and verification.
Review: Record the branch choice and actual pushed hashes. This supersedes only the no-commit/no-push clauses of D-067 and D-077 from the time of the new authorization; their earlier historical statements remain accurate. Word-only QA, missing physical evidence and approval-date limitations remain explicit.

D-078 branch resolution: the author explicitly selected "Push both deliveries to master". Both pushes target origin/master; no main branch is created. Use normal fast-forward pushes, preserving remote history.


ID: D-079
Status: SETTLED
Decision: Correct the concrete mathematical, numerical and supporting-description defects found by the fresh independent equation review after the first authorized push.
Why: Re-deriving the current printed formulas revealed omissions and overclaims that the first completion pass did not catch. The author explicitly requested that this iteration test logical expression and calculations, then fix supported errors.
Alternatives: Treat a prior PASS as proof of every expression (insufficient); alter the frozen implementations or experimental results to match inaccurate prose (wrong); preserve incorrect rounded values (not defensible).
Evidence: First delivery pushed to origin/master as e69dfa62eda80bc0ba5d0c4607a3a183a69f71fb. Independent reports and reproducible diagnostics under audit_evidence/equation_iteration2 cover all 56 numbered displays plus unnumbered calculations. Chapter 3's closing point transforms omit homogeneous components; its unit forearm vector omits normalization. The printed Chapter 5 elbow y rounds from 0.044979675 m to 0.04 m, not 0.05 m. Pinned Appendix D intrinsics give vertical field of view 43.145438 degrees, rounding to 43.1. Appendix H's both-arm synthetic row has eleven nonzero fields, not twelve. Appendix F's plotted curves are amplitude responses of the actual candidates, and the implemented robust scale uses rolling absolute residuals. Detailed supported prose corrections and calibration-plane distinctions are recorded in the reviewers' reports.
Reversibility: Thesis-source and derivative artifact edits only; independent diagnostics preserve before/after evidence. No input data, algorithms or experiment-selection rule changes.
Review: Verify the final per-equation dispositions and numerical rounding directly from full-precision inputs. Preserve the rig spawn assumption and previous evaluation constraints. Any additional exact sites are appended below as they are integrated; rebuild, rerender and recheck before the second push.

ID: D-080
Status: SETTLED
Later refinements: D-087/D-088 supersede the Chapter 3/6 picture choices. D-089/D-090 supersede the Chapter 7 gallery placement and coordinate-only human figures while preserving the paired capture provenance and quantitative evaluation.
Decision: Add paired video/Unity task illustrations to Chapter 7 and replace unclear Figure 6.4 and the photographic Figure 3.4 with clear, current mathematical diagrams.
Why: The author explicitly requested more Chapter 7 screenshots like the previous version, identified Figure 6.4 as unclear and clarified that Figure 3.4 serves a demonstration purpose and should simply be replaced with a clear picture.
Alternatives: Move the photographed hip detections onto an invented anatomical location (would fabricate measurements); restore obsolete evaluation metrics or trajectory plots (not requested); add a caveat-heavy photograph after the author chose an illustrative replacement (unnecessary).
Evidence: Existing saved video/Unity frames and their capture logs; make_ch3_figs.py shows that the old hip points project onto the rail. The replacement Figure 3.4 is a labelled schematic, not an altered measurement. Figure 6.4 will expose the same four pre-levelling frames and mapping directions. Camera and Camera' retain one optical origin; World and Unity retain the desk-marker origin.
Reversibility: Condensed-local figure generators/assets and Chapter 3/6/7 placement/captions only. Preserve all original assets and capture logs. Formatting sizes, line widths and selected example frames serve illustration, not sample selection for statistics.
Review: Check schematic landmark/origin/axis geometry, clear mapping arrows and labels, and matched frame identity for each video/Unity pair. Chapter 7 statistics, masks, validity definitions and existing section meanings remain unchanged. No new anatomical ground truth or capture is claimed.


ID: D-081
Status: BLOCKED
Decision: Pause the current correctness iteration and use only the author's newly named Thesis_V8_Condensed(7).docx for removal of the intermediate gravity-aligned frame; resume correctness review after that refactor is complete.
Why: The latest explicit instruction replaces the previous manuscript baseline and requires semantic elimination of the frame, not a label substitution. The named file is not available in the accessible repository, home folders, temporary files or connected Word sessions. Editing the older assembled thesis would not satisfy the source-of-truth requirement.
Alternatives: Assume that the (7) file is identical to the previously pushed thesis (unsupported); continue changing the older builders (would risk overwriting author changes); rename the removed frame mechanically (explicitly rejected).
Evidence: Author's 2026-09-13 instruction. File-name searches under the workspace, /home/luo and /tmp found only the existing unnumbered thesis artifacts and scratch chapter files. Codex Document Control reports no connected sessions. An asynchronous request for the exact accessible path is pending.
Reversibility: The first delivery remains pushed as e69dfa6 on origin/master. Second-iteration reports and pending findings remain under audit_evidence/equation_iteration2. The already applied but unbuilt Appendix source edits are preserved in pending_appendix_corrections.patch and removed from the active builder pending comparison with the new baseline. Both visual agents stopped without changing files.
Review: Supply the latest document or its accessible location. Then inventory its actual contents, preserve its independent author edits, remove the obsolete frame while retaining basis conversion, gravity alignment and floor translation, prove Chapter 5/7 distance invariance, rebuild DOCX/PDF, and perform the requested renewed correctness pass before the second push. Earlier figure requests remain pending: clear illustrative Figure 3.4, clearer Figure 6.4 and additional Chapter 7 video/Unity pairs.


D-081 resolution: D-082 records the author's clarification that the current assembled document is the intended source. The missing-file blocker is closed; the requested operation is proceeding from the pinned current hashes.


ID: D-082
Status: SETTLED
Decision: Use the current assembled thesis as the clarified baseline, eliminate the intermediate frame entirely, and express Chapter 5 geometry and Chapter 7 plotted positions directly in Scene.
Why: The author clarified that Thesis_V8_Condensed(7).docx means the current document. A direct Scene formulation preserves Craig frame pairs and avoids inventing a replacement intermediate frame. Gravity alignment remains the proper rotation operation G inside the full Unity-to-Scene transform; floor placement remains the recording-specific translation t_f=(0,d,0).
Alternatives: Mechanically rename intermediate coordinates Scene (wrong unless the floor translation is included); introduce another gravity-aligned frame name (explicitly forbidden); retain unlabelled frame-relative rotation matrices in Chapter 5 (unnecessary and less reproducible).
Evidence: Author's clarification; current DOCX SHA256 00eb9037ca34c93838d1afa26c2ed196209cf7cdc2dc152b3595fe14999c6906 and PDF SHA256 08f85efbc57af62f9b5e2a26b5761cc6e513e8c747e0982167555e8109b1029e, the first delivery at e69dfa6. Frozen mapping gives pScene=G*S*pWorld+t_f and R(Scene,MappedMarker)=G*S*R(World,Object)*S. In wrist-minus-marker displacements the same t_f cancels exactly, and proper G preserves Euclidean distances. The inverse full Scene/Camera' transform cancels the added floor placement before the unchanged kinematic solve.
Reversibility: Thesis sources, figures and derivatives only. Experimental data, input selection, pinned metrics and frozen implementation remain unchanged. Plotted absolute vertical coordinates and affected worked intermediate coordinates shift by the explicitly included recording-specific floor translation; geometric differences and recovered Camera' wrist remain unchanged.
Review: D-081's missing-file blocker is resolved. Remove the old frame from printed prose, scripts, tables, glossary and embedded figures; retain its name only in explicit historical change records. Prove distance/offset/recovery invariance, build and inspect DOCX/PDF, then resume the deferred correctness audit and finish the remaining author-requested figures before the second push to master. Earlier frame decisions are superseded only where they issued the removed intermediate frame; gravity alignment, floor placement and the spawn-axis assumption remain.


D-082 additional image dependency: Figure 2.5(b) contained the removed coordinate adjective in its raster axis labels. Its condensed generator now uses the full Scene mapping and labels Scene x/z. The added floor translation affects only the discarded y component, so every displayed point/axis and trajectory remains in the same x-z location. The caption states this projection property. No figure-source data or experimental statistic changes.


D-082 visual/build refinement: actual rendered removal-stage pages showed one frame-inventory row split across pages and the Figure 5.3 caption separated from its image. Keep Table 2.2 entries intact and keep that image with its caption. The new Chapter 5 floor scalar follows existing C48 display precision (71.62 cm), with full precision retained in the diagnostic. These are formatting-only refinements; neither the full-precision transform nor a numerical result changes.


ID: D-083
Status: SETTLED
Decision: Close the verified frame-removal milestone and resume the deferred whole-equation correctness review on the revised Scene formulation.
Why: The author explicitly required this order. The assembled DOCX/PDF now contain zero removed-frame terms, use the full Scene mapping and retain every physical evaluation statistic. The supported D-079 findings still need correction; a prior arithmetic PASS does not erase them.
Alternatives: Continue correctness changes before the removal is complete (contradicts the requested sequence); end after frame removal (leaves authorized work unfinished); discard old diagnostic evidence (loses the audit trail).
Evidence: remove_intermediate_frame/milestone_manifest.json pins DOCX a0125df75ed4e0d525ba9bec202235031f358f891b17c6fffcebeaacec8f2bfe and PDF aabb3c466f4b1d3e5edb25c2a5984f3fa2dda660e7174d67e7403f9f49cb43df. Assembled frame checks PASS 18, terminology checks PASS 16, Chapter 5 invariants PASS 79, Chapter 7 Scene invariants PASS 149, pinned Chapter 7 PASS 1147 / SKIP 21 / FAIL 0, 616 internal references resolve. All eleven substantive parts have zero style hits; the old front-matter false positive remains. Actual raster review cleared the inspected chains and figures, including the caption and table-row corrections. Historical trail embedding checks still fail their documented obsolete assertions.
Reversibility: Preserve removal-stage evidence separately from equation_iteration2 (pre-correction findings) and equation_iteration2_final (renewed checks). All corrections remain in V8 sources and derivatives; no frozen code/data changes.
Review: Complete the supported D-079 corrections and Figure 3.4 schematic, re-review all numbered and unnumbered mathematics, build and inspect final artifacts, append final dispositions and then perform the authorized second normal push to master. No new frame or experiment is introduced. Native Word typography, unknown approval date and physical assumptions remain explicit.


ID: D-084
Status: SETTLED
Decision: Qualify Appendix D's printed field of view as the nominal centred-principal-point approximation.
Why: The renewed calculation review found that the standard centred formula gives 55.5511797 by 43.1454381 degrees, but including the recorded off-centre principal point gives about 55.5496 by 43.1395 degrees. The small horizontal difference crosses the one-decimal rounding boundary. Calling the nominal number exact would therefore be misleading.
Alternatives: Treat both calculations as identical at printed precision (false horizontally); change an experimental result (these are explanatory intrinsics calculations, not results); add unnecessary optical theory (not needed).
Evidence: Table D.1 full-precision intrinsics and independent equation_iteration2_final/ch7_appendix_results.json calculation. Pixel-boundary conventions 0..size and -0.5..size-0.5 both give a horizontal span rounding to 55.5, while the centred approximation rounds to 55.6. The earlier audit report's contrary rounding statement is explicitly corrected in the final review, not erased.
Reversibility: One qualified Appendix D sentence, matching revision/evidence notes; no image, calibration, equation, recording or experimental result changes.
Review: Printed nominal values remain 55.6 by 43.1 degrees under the stated approximation. Rebuild the Appendix and assembled thesis and retain the earlier report as historical evidence.


D-083 final Chapter 5 review: scope the pose-introduction sentence to frames with a measured object pose. The previous universal every-frame wording contradicted the explicitly documented missed marker detections. No equation, sample mask or numerical value changes. The independent final Ch5 report records the correction.


ID: D-085
Status: SETTLED
Decision: Correct the stale Figure 5.5 memory-target statement and clear two label overlaps found by final actual-PDF inspection.
Why: The Figure 5.5 inset still claimed minimal displacement from the last measured elbow, contradicting the corrected Chapter 5 derivation. Raster inspection also found the x/z labels overlapping in Figure 2.4(a) and the lower plot edge crossing the Figure 3.7(b) legend. These are concrete figure defects, not a thesis redesign.
Alternatives: Rely only on XML and ignore raster text (would leave a mathematical contradiction); change the underlying plotted geometry or measurements (unnecessary); edit archived/shared drafts (avoid by using current condensed-local generator copies).
Evidence: Final-PDF reviewers inspected all Chapters 2-6 pages. Physical page 88 carries the stale Figure 5.5 inset; page 31 shows the camera-label overlap; page 57 shows the swing/twist legend intersection. The corrected minimum-distance target is current shoulder plus upper-arm length times the remembered unit direction, as independently established in CH5-4. The pre-correction PDF is pinned by SHA256 7f285378a027d6c99f1bd8d96e7aca25591630a48342c9ff6b2388630434f5f3.
Reversibility: Condensed-local figure copies/generators and builder routes; preserve original V7/V8 assets and all coordinates. Text placement and inset wording only, with no experimental result or equation change.
Review: Regenerate and inspect all three figures in the rebuilt PDF, confirm the rest of the reviewed mathematics remains identical, update final hashes and then complete the authorized second push.


D-085 Appendix pagination finding: final raster inspection also found Figure D.1 separated from its caption across physical pages 172/173. Keep that image paragraph with its caption; no image pixels, equations or numbers change. Reinspect affected Appendix pagination after rebuild.


D-085 scope note: ordinary continued long captions and table rows retain all text and are accepted as nonblocking pagination. No broader layout redesign is performed. The three corrected figure defects and the fully detached Appendix caption were reinspected in the final PDF.

ID: D-086
Status: SETTLED
Decision: Deliver and normally push the completed second thesis revision to origin/master, preserving all assumptions, pinned results and prior history.
Why: The author authorized both master deliveries and a fresh equation review after the first. Frame removal was completed first; the renewed review then corrected supported mathematical, numerical, evidential and embedded-figure defects. Current artifacts and final raster reviews agree.
Alternatives: Stop after recommendations or leave supported fixes unbuilt (would not complete the request); force-push or create main (not authorized or needed); fabricate physical evidence or hide legacy check failures (unsupported).
Evidence (reviewed preliminary build; final label-only artifact addendum below): DOCX ed6d4e339d3d4c32fa7f069920757396dc54b502d2bde28d750b15519df436a5; 189-page PDF 99367be8b27f6ab2463efe6c8c0efc652f01dde10b0c1c4d0b4c226f42ed44e5. All 56 numbered equations and supporting mathematics reviewed; Ch2-4 PASS80, Ch5 PASS16, Ch6 PASS42, current Chapter7 PASS1147/SKIP21/FAIL0. Frame checks PASS18, notation/image checks PASS22, 619 references resolve, 132 citations map to 57 bibliography entries. Eleven substantive parts have zero style hits. Final reviewers cleared the corrected images and complete equations; no page text exceeds page bounds. Two historical trail embedding checks retain their explained obsolete failures. First delivery is already origin/master commit e69dfa62eda80bc0ba5d0c4607a3a183a69f71fb.
Reversibility: Normal additive commit/push preserves the first delivery and the full decision chain. Frozen implementations, recordings, result tables and archived drafts remain unchanged. The exact changed-file list and SHA256 manifest identify this delivery.
Review: DELIVERY_2026-09-13.md, REMOVE_INTERMEDIATE_FRAME.md, DETERMINED_DEFECTS.md, UNRESOLVED_ITEMS.md and equation_iteration2_final evidence provide a cold handoff. Native Word typography, actual institutional approval date, physical/model assumptions and missing historical/local-data reproduction limits remain explicit. Identify the second delivery by the commit containing DELIVERY_2026-09-13.md; verify its hash equals origin/master after pushing. No further thesis source work remains.

D-086 final artifact addendum: the last two Figure 3.7 panel (a) label anchors
were cleared under D-085 before delivery. The delivered DOCX SHA256 is
d99335e683b9cf2cebcfdf424be495a9b1d9f9a52a4fbd30c6815036c4996b14; the final
189-page PDF SHA256 is
4e1e00cd0dd6c6c93a2b20d9f9abd6a2996c646e6aae3d38a35ee9ef2c727f9d. These supersede
only the preliminary artifact hashes above, whose earlier reviewed state is
preserved in the visual manifests. Final page 57 was inspected directly; all
other 44 reviewed Chapter 2-4 pages, all 34 Chapter 5/6 pages and all 30
Chapter 7/Appendix pages are byte-identical to the preceding reviewed PDF.
The complete current checks were rerun against these final artifacts. The
new verify_delivery_artifacts.py reproduces global PDF text-bound, numbered-
equation, protected-chapter and V8-only scope checks. No calculation or
experimental output changed during this last text-placement adjustment.

D-086 packaging note: the full staged Git whitespace check reports trailing
spaces and terminal blank lines only in eight preserved raw diagnostic or
patch-context files. Their exact bytes remain part of the audit history.
The check restricted to manuscript sources, scripts, figures and records
outside audit_evidence passes. This is recorded in command_results.json;
no manuscript, calculation or source whitespace defect is concealed.

ID: D-087
Status: SETTLED
Decision: Replace the Figure 3.4 schematic with a real recorded video frame carrying the corresponding measured torso landmarks and derived axes.
Why: The author clarified that the requested correction was a better video frame, not a drawing. The author also requested direct replacement without another inspection pass. This refines D-080 only for Figure 3.4; its schematic choice is superseded.
Alternatives: Keep the schematic (contradicts the clarification); reuse the frame with hip labels on the rail (retains the original problem); manually move measured points onto the body (would fabricate a measurement).
Evidence: Author's explicit Figure 3.4 clarification and instruction to replace directly. Starting delivery is commit 9a0d7ce0ca6a541961336400cde7576f6dde0a40, DOCX d99335e683b9cf2cebcfdf424be495a9b1d9f9a52a4fbd30c6815036c4996b14 and PDF 4e1e00cd0dd6c6c93a2b20d9f9abd6a2996c646e6aae3d38a35ee9ef2c727f9d. Selected frame and source-row provenance will be appended with the replacement.
Reversibility: Condensed-local image, generator, caption and directly associated prose only, followed by Chapter 3 and thesis rebuild. Existing figures, prior delivery evidence, equations, worked example and experimental results remain preserved.
Review: Record the actual frame and image source; use a concise photographic caption. Rebuild DOCX/PDF and deliver under the standing normal master-push authorization. No new whole-thesis or equation audit is performed.

ID: D-088
Status: SETTLED
Decision: Restore Figure 6.4 and its generator exactly from the preceding delivery e69dfa6, with a caption scoped to the conversion before gravity alignment.
Why: The author said the replacement was worse and explicitly requested the previous picture. The older picture shows Camera, Camera', World and Unity without the removed intermediate frame, so its restoration preserves the current coordinate-frame policy.
Alternatives: Keep or redesign the new diagram (contradicts the request); revert Chapter 6 mathematics (unrequested and would discard the completed Scene formulation).
Evidence: Author's direct request. Git e69dfa6 contains the previous ch6_fig_frames.png and make_ch6_frames_final_fig.py. That diagram ends at the pre-gravity Unity convention; Section 6.4 still provides the actual gravity rotation and floor translation into Scene.
Reversibility: Restore the prior PNG/generator byte-for-byte and narrow only the caption and its introductory sentence to what the picture shows. No equation, calibration, result or frame inventory changes.
Review: Rebuild Chapter 6 and the assembled DOCX/PDF together with the Figure 3.4 replacement. No additional inspection pass is requested. Preserve both earlier decisions and their artifact hashes as history.

D-087 selected-frame evidence: Figure 3.4 uses recorded two-hand rail frame
1400 (recording_20260909_000024), time 46.699725 s. Its RGB image is the
already tracked figures/src/r7_frame01400.png, SHA256
11ee86700ab6d468e1be7bd2bf594a47e4ed5c8a44d71af22796b23d0c4e3c80.
The corresponding filtered CSV row, physical line 1402, projects L12, L23
and L24 onto the visible shoulder and hips. A compact committed source.json
pins that row, the intrinsics, complete source hashes, derived axes and
projection. The generator needs only this record and the original PNG;
it does not require the ignored whole CSV or bag when rebuilding. The
0.30 m drawn axis length is inherited from the former photographic
illustration as a display choice, not a measured segment length. The final
figure SHA256 is 22c2454d07155eb98f9425f6e63e48b4b05b922566d8b2ff612787a8c9c25701.
Only illustration frame/prose/caption changes; the numeric frame-533 example
and every equation remain unchanged.

D-088 exact restoration evidence: restored Figure 6.4 SHA256
e820cc8c57a48c1b9f9ee7420a0bc9e318e9f2bbcad732301264868d40478249
and generator SHA256
5f8e78d9906cc9f28cab7fa793e72adb630abd9e01c16b451e9a52956df722ce
match their e69dfa6 bytes. The caption no longer describes the rejected
solid/dashed five-frame diagram. The full Scene equations are retained.

D-087/D-088 build completion: Chapters 3 and 6 and the complete DOCX build
passed; the PDF renderer refreshed four indexes and produced 189 pages.
Current DOCX SHA256 c9880631767aa12da818bc6896ba3ed7ef6182cdc21b6cc6ad26d3fb23d52d09;
PDF SHA256 8cfec25a5bc433beca1f349abee9b95f077d9883cea5022997fa38bad0c2a135.
Current files, source provenance and exact commands are recorded in
FIGURE_REPLACEMENTS_2026-09-13.md. The requested replacements were applied
without reopening the completed equation audit.

ID: D-089
Status: SETTLED
Decision: Restore substantial real-video and Unity imagery throughout Chapter 7, replacing Figures 7.3/7.4 with genuine saved Unity trajectory views while retaining the accepted evaluation.
Why: The author explicitly requested the missing earlier Chapter 7 images and Unity trajectories, with pictures beside the relevant discussion. Additional scene images should explain the task and failures, not form a detached gallery or silently redefine the numerical comparisons.
Alternatives: Keep the two coordinate-only human plots (does not meet the request); append all pictures at one location (does not explain the relevant passages); restore old metrics or describe full saved traces as the exact validity-gated table samples (would misstate the evidence).
Evidence: Author's direct request, existing recorded RGB frames, saved Unity trail captures and their source/compose manifests under condensed/figures/src. Current baseline is master 7243a2060df433a8ea6c3814ca7b594c8273618d. D-035 to D-053 and the completed equation review establish the fixed physical-reference, frame-selection and quantity distinctions.
Reversibility: Condensed-local presentation assets, directly associated captions/prose and the Chapter 7 builder, followed by assembly/render. Nine result tables, six equations, experimental inputs/results and the Chapter 7 evaluation structure remain fixed. No new recording or experiment is made.
Review: Preserve Figure 7.3/7.4 numbering; add real-video context to the existing object figures, restore failure/proxy examples beside their methods, and distribute the video/Unity pairs with the spatial discussion. Captions identify model-wrist versus rig-joint quantities and any schematic scene guides. Record source hashes and exact figure placements, run relevant existing build/consistency checks, then normally push the completed presentation revision to master.

ID: D-090
Status: SETTLED
Decision: Omit the earlier outer waypoint labels from the restored Unity trajectory figures, retain their real captured paths, and identify the dashed path as a schematic scene guide.
Why: The earlier visualization's Start/W1/W2/W3 roles predate D-035 and differ from the current W1-W4 measurement-waypoint roles. Reprinting those labels would create a terminology collision. The saved model-wrist trails also span presentation intervals rather than the valid-landmark subsets scored as rendered rig joints in Tables 7.3 and 7.4.
Alternatives: Keep the old labels with a long historical caption (requires readers to learn conflicting waypoint systems); relabel them to the current W1-W4 (would imply unsupported geometric correspondence); alter the captured trajectories (would change the evidence).
Evidence: The native composition script adds the labels outside the saved Unity PNGs using waypointViewport. The capture records and trail files identify rail frames 92-899 and handover frames 137-1498, whereas the current table evidence has 100 rail samples and 650 right/589 left handover samples. sources.json in audit_evidence/ch7_visual_restoration records the exact provenance.
Reversibility: Restore the outer annotation loop in the condensed-local composition script and regenerate Figures 7.3 and 7.4. Captured source images and quantitative evidence are untouched.
Review: Figures 7.3 and 7.4 retain genuine Unity imagery, state-coloured model-wrist paths and the projected scale bars. Their captions state the separate table scope. No new frame, physical path registration, elbow trail or experimental result is claimed.

ID: D-091
Status: SETTLED
Decision: Use two-line 50-pixel titles on the restored video strips and keep every Chapter 7 figure caption together with its image.
Why: The first PDF render showed that the original 25-pixel strip titles became approximately 4.2-point text at the 6.1-inch embedding width, and Figure 7.4's caption split across pages. The larger titles yield approximately 8.46-point text while retaining the compact four-frame sequence.
Alternatives: Leave small titles or split captions (poor readability); enlarge the photographs and plots together until the compound figure no longer fits a page (unnecessary); resize or crop the original video (not needed).
Evidence: First render physical pages 116, 118, 123 and 131; final strip geometry is 2596 by 594 pixels, including unchanged 640 by 480 image regions. integration_review.json verifies all twelve source-frame regions by exact decoded-pixel comparison. The figure helper sets caption keep_together and image keep_with_next.
Reversibility: Restore the earlier title-band settings and remove the caption paragraph property. Source frames, quantitative plots, tables and all equations are untouched.
Review: Inspect the regenerated figure pages for complete captions, legible titles and retained real-video content. This is formatting only; no experimental number changes.

ID: D-092
Status: SETTLED
Decision: Recompose Figures 7.1 and 7.2 with the x-y projection at upper left, x-z projection at lower left and a larger three-dimensional Scene view spanning the right column.
Why: The author finds the two existing projections unclear and explicitly requests this arrangement. A 3D overview adds spatial context while the x-y projection retains the detail of the short lift. The real-video strips remain above the plots under the same figure numbers.
Alternatives: Retain the two vertically stacked plots (does not meet the request); substitute Unity screenshot trajectories here (would replace the accepted-sample waypoint quantities in these object-evaluation figures); draw a surveyed physical path (no registered physical path exists).
Evidence: Author's direct layout instruction; existing make_ch7_object_waypoint_figures.py supplies the accepted marker-centre samples and pinned W1-W4 positions in final Scene coordinates. Baseline is master b52235513477f5d44a4b790d52858b12a934b4b9. D-035/D-036 fix waypoint and accepted-sample semantics, and D-082 fixes the final Scene formulation.
Reversibility: Restore only the prior plot layout and captions, then rebuild Chapter 7 and the thesis. All recorded source frames, sample selection, coordinates, waypoint means, experimental statistics, tables and equations remain unchanged.
Review: Verify the requested panel order, readable labels, correct y-up Scene axes and disclosed plot scaling. Compare plot inputs and waypoint coordinates directly with the baseline generator. Record final figure hashes, rebuild DOCX/PDF, inspect both complete figure pages and push the completed revision to master under the standing authorization.

D-092 rendered-size refinement: the first proof used a 10.2 by 4.8 inch
plot source and made the 3D panels too small at the thesis width. The final
source is 10.2 by 7.2 inches, displayed at 6.1 by 4.306 inches; its smallest
13.5-point source labels display at 8.07 points. The 3D W4 text offset is
moved away from the Scene y tick at 80 cm without moving its waypoint marker.
These are display choices established by inspection of the actual PDF pages.
The upper-left x-y view uses independent scales; the lower-left x-z view
uses equal data aspect; the right 3D view uses equal data-axis spans and a
cubic box, with Scene y vertical. Normal perspective foreshortening remains.
No source sample, coordinate, selected waypoint, result, table or equation
changes. Final provenance and the independent review are in
audit_evidence/ch7_object_3d.

ID: D-093
Status: SETTLED
Decision: Widen the displayed-equation spacing to 10 pt above and below, set on the paragraphs inside the equation table cells (eqn.EQ_SPACE_PT) and reapplied in build_thesis._normalize_table after the in-table branch zeroes every table paragraph.
Why: The author reported the spacing between equations as too small. Equation cell paragraphs carried line 1.0 and after 0, so an equation sat flush against the prose and against the next equation while body text ran at 1.5 lines with 6 pt after.
Alternatives: Spacing on the table itself is not available in Word; a blank paragraph between equations would add an empty item to the body flow.
Evidence: Rendered page comparison before and after on the Chapter 3 torso-frame page; page count 189 to 195.
Reversibility: Set eqn.EQ_SPACE_PT back to 0 and rebuild.
Review: Confirm the equation number stays vertically centred beside the expression.

ID: D-094
Status: SETTLED
Decision: Apply the round-1 language review as targeted rule fixes only: glossary-name consistency, humanizer lexical items, P3 credibility clauses, invented and above-C1 words, three sentences over the 45-word checker limit, and the rhetorical contrast frames. Reject the mass passive-voice and 28-to-44-word sentence-splitting flags.
Why: Twelve fresh Opus reviewers ran under .agent/CHAPTER_REVIEW.md with instructions to over-report, so most flags are marked uncertain. The passive-voice class contradicts D-028, which established objective agentless description and records that no first-person substitute was introduced. Splitting every flagged sentence would rewrite a large share of a delivered thesis for no rule the project checker enforces.
Alternatives: A full rewrite to about 30 words per sentence; the author chose targeted only.
Evidence: writing/reviews/*_lang_round1.txt (12 reports); check_style.py 1 hit, check_refs.py 626 references, UNRESOLVED none.
Reversibility: The builders are the source; each replacement is a single exact string.
Review: The number-precision flags were escalated, not applied, because the values are the author's locked facts.

ID: D-095
Status: SETTLED
Decision: Extend writing/GLOSSARY.md with the established technical terms the reviewers found in the thesis but not in the list, and replace the stale "person space" entry with the Craig frame names the thesis now uses.
Why: GLOSSARY.md admits terms that are established names a reader can look up. The thesis used about forty such terms that were absent, and the frame entry predated the Craig notation of D-035 to D-066 while the thesis uses {Camera'} 47 times.
Alternatives: Rewriting the prose to avoid the terms would blur standard terminology; the author chose to extend the list.
Evidence: The twelve review reports' TERMS NOT IN GLOSSARY sections, filtered against the built text.
Reversibility: Revert GLOSSARY.md.
Review: The project-invented labels were not added; they are listed for the author in LANGUAGE_REVIEW_2026-09-13.md.

ID: D-096
Status: SETTLED
Decision: Raise the displayed L24 axes by 55 source-image pixels and place their label beside the raised origin in Figure 3.3; retain the recorded frame and the numerical example.
Why: The author explicitly requested moving the L24 coordinate drawing above the rail and waived routine ground-truth checks. The composite still reads the older annotated source image. The 55-pixel offset is a visual layout choice accepted after inspection, not a measured anatomical correction.
Alternatives: Replace the worked-example frame (unrequested); retain the rail overlap (does not address the request); change recorded landmark coordinates (unnecessary for annotation placement).
Evidence: Author's instruction and visual inspection of ch3_fig_chain_segments.png; make_ch3_condensed_figs.py loads the older writing/v8/figures/ch3_fig_chain_photo.png.
Reversibility: Restore the previous figure input, local drawing offset and caption, then replace the figure in the chapter and assembled thesis.
Review: Inspect the rendered Figure 3.3 for rail clearance. Disclose the display shift in its caption. No routine ground-truth or experiment checks.

D-096 visual review: the parent and independent subagent inspected the new
composite. The L24 origin, axes and adjacent label clear the rail. The
generator translates drawing coordinates only; the caption and legend
disclose this. No ground-truth checks were run, as requested.

ID: D-097
Status: SETTLED
Decision: Review all twelve current thesis parts against the local writing and glossary rules, apply supported language corrections in their builders, and repeat independent review on revised text.
Why: The author explicitly requested checking the whole thesis and modifying it until its language follows the rules, authorized subagents and pushing, and asked to avoid routine ground-truth and Git-history checks. This authorizes direct language edits without another approval round.
Alternatives: Apply every old uncertain flag blindly (would replace valid academic phrasing and locked quantities); stop after the mechanical checker (misses contextual language violations); rewrite methods or rerun experiments (outside this request).
Evidence: Current user instructions; writing/WRITING_SKILL.md; writing/GLOSSARY.md; .agent/CHAPTER_REVIEW.md; skill_set/thesis-statement-style.md; D-028 objective voice and D-094/D-095 preceding language work. Complete initial texts and embedded-comment inventory are in audit_evidence/language_compliance_2026-09-13.
Reversibility: Restore individual builder replacements from the language change record, then rebuild affected parts and the thesis. Existing equation spacing and unrelated working edits are retained.
Review: Apply P1-P3, plain C1 vocabulary, Canadian spelling, standard terms, clear sentences and all humanizer patterns in context. Keep title-case headings, objective academic voice, scientific caveats, proper names, equations and pinned result values. Record uncertain or rejected flags with reasons; use the existing 45-word mechanical check without treating shorter convoluted sentences as automatically acceptable.

ID: D-098
Status: SETTLED
Decision: Include gigabyte (GB) and long-term support (LTS) in the glossary as established abbreviations used in Appendix B specification tables.
Why: The reviewer found both absent from the glossary. These are conventional storage-unit and software-support names, unlike project-invented labels. Keeping the table entries preserves the hardware and operating-system names.
Alternatives: Expand every table entry (unnecessary repetition); omit the abbreviations from the glossary (leaves a reported vocabulary gap); change the equipment or software version (outside a language edit).
Evidence: Appendix B uses GB for memory/storage capacity and LTS in Ubuntu 24.04 LTS. The glossary already includes megabyte and operating-system/product terminology.
Reversibility: Remove these two glossary entries and expand their specification-table abbreviations if preferred.
Review: No numeric table value, equipment specification or software version changes.

D-098 round-2 extension: include bus, metadata, mathematical/rotation
operator, amplitude and amplitude gain. The Appendix review identified
these conventional technical names as absent from the literal whitelist,
not as invented language. Appendix A uses hardware-bus and recording
metadata terminology; Appendix E distinguishes a rotation operator from
a frame relation; Appendix F discusses amplitude gains. Retaining these
names preserves technical precision. The alternative replacements
"signal size" and "gives a rotation" would obscure those distinctions.
No method, quantity or notation changes.

ID: D-099
Status: SETTLED
Decision: Reduce the printed thesis glossary to one page containing only T-pose, marker/fiducial marker, the PSF/PSR/PSB/PSI record codes and p95.
Why: The author explicitly replaced the earlier two-page limit with one page and identified the terms to explain for engineering students. Routine terms such as merger are unnecessary for that audience.
Alternatives: Retain coordinate frames, recovery rules and routine engineering terms (outside the revised selection); compress all old entries with smaller type (keeps the unwanted content).
Evidence: Author's latest instruction; the previous printed glossary has 43 entries in build_frontmatter.py. Definitions are shortened from those existing entries.
Reversibility: Restore selected entries in build_frontmatter.py and rebuild the front matter and assembled thesis.
Review: Verify that the complete glossary occupies one rendered PDF page. The internal writing/GLOSSARY.md vocabulary guide remains a separate authoring resource.

D-099 author addition: also retain RGB-D camera/sensor. The printed glossary now has five entries; the one-page limit remains.

D-099 further author additions: retain coordinate frames and PUMA convention. The final selection has twelve entries, including six coordinate frames; retain the one-page limit and existing table typography.

ID: D-100
Status: UNCERTAIN
Decision: Increase the existing displayed-equation spacing from 10 pt to 12 pt above and below each equation.
Why: The author again requested a small increase. Two additional points per side provide a modest increase without introducing blank paragraphs or changing equation content.
Alternatives: Keep 10 pt (does not implement the latest request); add blank paragraphs or a large gap (less controlled and more disruptive to pagination).
Evidence: Author's latest instruction; eqn.EQ_SPACE_PT and the assembler apply the spacing to numbered equation cells and unnumbered displays. The exact 12 pt choice is an editorial assumption pending rendered inspection.
Reversibility: Change EQ_SPACE_PT and rebuild the chapter documents and thesis.
Review: Inspect consecutive equations in the rendered PDF for separation and number alignment; retain all mathematical content.

D-100 review status: SETTLED after rendered and independent structural
inspection. All 56 numbered equations (including both cells) and 51
unnumbered displays have 12 pt above and below. Inline paragraphs and data
tables are unaffected. Physical pages 45 and 48 show clear separation and
aligned equation numbers. The original 12 pt choice was editorial; its
rendered result is now verified. Evidence: language_compliance_2026-09-13/
equation_spacing_review.txt and the saved page images under audit_evidence.

ID: D-101
Status: SETTLED
Decision: Complete the clean LaTeX edition under condensed/latex using the final assembled DOCX as the content source, native equations and tables, extracted original figures, and generated contents lists.
Why: The author's request for a clean LaTeX version after the language iteration is the unfinished item in Claude's handoff. The assembled DOCX contains final citation numbering, so exporting separate chapter drafts would silently restore older reference numbers.
Alternatives: Stop at the Word/PDF revision (leaves the handoff incomplete); use unprocessed Pandoc output (leaves equations in Word-layout tables and loses upright frame labels); copy the printed contents pages (produces stale pagination).
Evidence: Claude session 0ac37c1d-1f9c-4f54-8d07-196c7f02001b, final handoff; build_thesis.py performs assembly-only citation numbering; the independent conversion prototype preserves Chapter 3 and 7 prose, table data, math tokens and original images.
Reversibility: The LaTeX edition is a separate editable deliverable. Remove or regenerate its files without changing the accepted Word edition.
Review: Verify all ten chapters, appendices, front matter and references; native math and image preservation; complete captions; successful compilation; one-page glossary and equation spacing. Exact Word pagination is not a conversion requirement. Tool downloads and build caches stay under /tmp, outside the submitted sources.

D-101 is superseded by D-102 before any LaTeX deliverable was completed.

ID: D-102
Status: SETTLED
Decision: Cancel the LaTeX edition and finish with the verified Word and PDF thesis.
Why: The author explicitly stated "no need for latex, that it" after the Word/PDF revision was pushed to master.
Alternatives: Continue the earlier handoff request (contradicts the latest instruction).
Evidence: Author's latest message; thesis revision e934e29 is pushed to master. The LaTeX investigation produced only temporary prototypes; the repository scaffold was empty and has been removed.
Reversibility: Resume the LaTeX edition only on a new author request.
Review: No LaTeX task remains. Retain the completed language revision, one-page glossary, raised L24 drawing and increased equation spacing.

ID: D-103
Status: SETTLED
Decision: Apply the remaining ENSC 498/499 Checklist 2.8 editorial and formatting corrections to the active V8 builders and deliver a rebuilt Word/PDF pair with populated navigation lists.
Why: The author supplied the review and explicitly requested all remaining fixes. Items 01 and 02 are confirmed by the author. The current builders reproduce the reported missing Word field caches, oversized equation tables, small captions and unsorted glossary.
Alternatives: Edit only the assembled binary (lost on rebuild); mark unverified items complete (unsupported); rerun experiments (unrelated to formatting and prose).
Evidence: User checklist and instructions; clean starting commit 5e0403d; baseline.json in audit_evidence/submission_checklist_2026-09-13; build_frontmatter.py, eqn.py and render_pdf.py. No embedded comment part exists in the assembled DOCX.
Reversibility: Revert this revision and rebuild the active V8 sources.
Review: Compare native math and all result tables with the baseline; inspect all final pages, numbered pre-mentions, field results and links. Preserve the author-selected glossary terms and verbatim acknowledgements.

ID: D-104
Status: SETTLED
Decision: Defer the actual approval date and submission term, retaining the existing placeholder and Summer 2026 until the author supplies those facts.
Why: The author explicitly answered the clarification with 'not right now just forget that first'. Neither the checklist nor repository establishes an actual approved date.
Alternatives: Guess the current date or current academic term (could misstate the approval/submission record); stop all other corrections (contrary to the author's direction).
Evidence: Author's reply in this session and existing front-matter constants.
Reversibility: Update the front-matter values when supplied and regenerate the documents.
Review: These two facts are deferred, not certified complete; no further request is needed in this session.

ID: D-105
Status: UNCERTAIN
Decision: Use 12-point Times New Roman, a six-inch text area, symmetric 0.45/5.10/0.45-inch equation columns with zero cell side padding, and right-aligned dot-leader tabs for navigation lists.
Why: Checklist items 41, 42, 50 and 51 require the equation centred over the full text area, the label within the right margin and at least 12-point Times New Roman. Equal outer columns centre the equation exactly. The outer width reserves room for the existing parenthesized labels at 12 point.
Alternatives: Keep the 6.5-inch two-column tables (violates margins and centring); reduce font size (violates the checklist); add manual spaces (unstable alignment).
Evidence: Letter page width minus two 1.25-inch margins gives six inches. Existing numbered labels are at most six characters. The exact outer-column allocation remains an editorial layout assumption until rendered verification.
Reversibility: Adjust the symmetric outer width or split an overwide equation across native mathematical lines, then rebuild and inspect.
Review: Check every display for overlap/clipping, every caption and data-table size, the one-page glossary, and final right-margin bounds.

ID: D-106
Status: SETTLED
Decision: Add sentence punctuation to all 56 numbered displays, split long explanatory paragraphs, repair first-use abbreviations and preceding figure/table introductions, and put References after Appendix H.
Why: The checklist requires these editorial fixes, and the author separately specified that References must follow the appendices. An independent full-text review found only three missing numbered figure/table introductions and identified twelve equations that continue into a lower-case clause.
Alternatives: Add a period to every equation (breaks continuing sentences); count necessary technical-list conjunctions as compound-clause defects (would distort clear lists); preserve References before appendices (contradicts the latest instruction).
Evidence: Independent editorial and equation reviews in this session; equation comma tags 2.1, 3.14, 3.15, 3.18-3.22, 5.1, 5.2, 5.5 and 6.2; Figure 6.4, Figure 7.3 and Table F.1 need earlier introductions. Current proportions are in Section 6.3, so the Section 9.2 cross-reference is corrected. User direction on reference placement.
Reversibility: Restore individual wording or paragraph boundaries in the builders. Reposition References in build_thesis.py/build_toc.py without changing citation source identifiers.
Review: Retain all measurement values, caveats, native equations and author-verbatim acknowledgements. Punctuation in a multiline equation belongs at the end of its final line. The list procedure starts each item with a verb and retains every acquisition condition.

D-106 unnumbered-display completion: independent review covered all 51
unnumbered mathematical paragraphs as well. Eleven displays continue a
sentence and take commas; forty take periods. The builder ordinal maps
record those continuations. The native mathematical tokens are preserved;
a single punctuation run is appended, on the final line for an array.

ID: D-107
Status: SETTLED
Decision: Cache the actual converged page-numbered navigation results in the original Word package and verify the cached document reproduces the PDF when reopened without index updates.
Why: The prior PDF updater did not save results into Word. Saving the entire manuscript through another word processor could rewrite native mathematical objects. Updating just the four field-result ranges preserves the original body and media.
Alternatives: Leave Word caches empty (reported defect); require the reader to press F9 (does not deliver completed navigation); round-trip all Word content through LibreOffice (unnecessary transformation).
Evidence: Existing render_pdf.py updated only PDF. Initial review found that cached list indents must match actual LibreOffice Contents styles; cache_navigation.py now uses those levels. Native package and mathematics comparisons are recorded in the final validation report.
Reversibility: Rebuild the assembly and regenerate caches from the current page layout. The cached lists remain Word TOC fields.
Review: Verify four populated fields, dot leaders, correct exclusion of Title Page/Table of Contents, final bibliography position, and page-for-page cached/recomputed rendering. The eight-update limit detects non-converging pagination and fails explicitly; 60 seconds is a maximum readiness timeout, not a fixed wait.

ID: D-108
Status: SETTLED
Decision: Correct verified reference metadata, cite the exact Intel product photograph, and align the unsigned approval-page layout with the public ENSC 499 approval form.
Why: The checklist identifies incomplete sources and requests the approval-page format check. Primary sources supply the missing bibliographic details and signature-line structure. The actual approval date and term remain deferred under D-104.
Alternatives: Invent an original publication year for the Intel guide (unsupported); cite a similar product photo (wrong source); use the graduate-thesis template (wrong course).
Evidence: Source verification report in audit_evidence/submission_checklist_2026-09-13; official approval form https://www.sfu.ca/content/dam/sfu/fas/study/current-students/ensc/undergraduates/ENSC_499_APPROVAL_Page.pdf. The exact D435 photograph has SHA256 dbd2de81399e0ce6dcd926cc8942619201ce0afeac19c220b12cb16f487a01da. The guide's 2019 date is expressly its verified online posting date.
Reversibility: Edit reference entries under their frozen source IDs, then rebuild. Signature lines remain unsigned; no personal authorization is asserted.
Review: Retain the author's committee names and roles. The Canvas-only title-page template and the deferred date/term cannot be certified from public sources. Glossary wording is shortened with all twelve author-selected terms retained; single-spaced 12-point cells preserve the one-page limit.

D-107 review clarification: the cached re-open check retains every page
and line boundary while ignoring the count of dot-leader glyphs and PDF
extraction whitespace. The first strict byte comparison found only these
extraction differences, with no substantive text or pagination difference.
Both cache indents and schema property order were independently corrected
before the final check. The citation audit is rewritten after caching so
its SHA256 identifies the actual delivered DOCX.

D-106 final editorial review: 33 additional exact replacements resolve
compound-clause chains and one ambiguous pronoun introduced by the RGB-D
expansion. Ten more topic boundaries and the worked capture example are
split into separate paragraphs. Every replacement retains its numeric
token sequence. The case convention capitalizes content words and words
of four or more letters, including During and From, while retaining short
articles/prepositions/conjunctions in lower case except at a title start.

ID: D-109
Status: UNCERTAIN
Decision: Keep the existing avatar illustrations while flagging the imported avatar's original creator/source as unverified; request the original download page without blocking other corrections.
Why: The exact camera-photo credit is verified, but the repository does not identify the creator of female-character-rig-unity.fbx. The user explicitly retained existing Unity figures in the preceding revision. Removing or replacing the avatar would change those figures and is not a supported source-credit correction.
Alternatives: Attribute the model to Blender from exporter metadata (wrong inference); infer a creator from the filename (unsupported); certify all borrowed material as fully credited (unsupported).
Evidence: Targeted read-only asset, importer, documentation and original commit checks in checklist_source_review.txt. The FBX exporter name identifies software, not an artist. No original creator/source evidence was found.
Reversibility: Add the supplied creator/download citation to the avatar description and affected captions when the original source is available.
Review: Only this discovered provenance gap prevents certifying checklist item 54 in full. The camera photograph itself is now traced exactly. No signature, date or asset attribution is invented.

D-109 is superseded by D-110 following the author's provenance confirmation.

ID: D-110
Status: SETTLED
Decision: Record the humanoid avatar as supplied by the laboratory and close the external-source query.
Why: The author explicitly confirmed that the model came from the lab and instructed that no external credit is needed. This supplies provenance without inventing a web source or artist.
Alternatives: Keep requesting a download page (contradicts the author's instruction); invent an outside attribution (unsupported).
Evidence: Author's current reply: 'that is from the lab, so no need for that'. Section 6.3 now describes the avatar as laboratory-supplied.
Reversibility: Add a more specific laboratory/creator acknowledgement if the author later requests one.
Review: No further avatar-source action remains. D-104's approval-date and term deferral still applies.

D-105 review status: SETTLED. Final Word grids use symmetric 648/7344/648
twip columns. All 56 equation numbers are unwrapped at the right text
boundary. The final PDF has zero horizontal margin violations; the
Chapter 4 builder's obsolete two-column grid override was removed.
Schema property ordering is normalized for native Word. Independent
review confirmed layout and complete mathematical content. Small labels
inside the author-retained Figure 6.4 remain a physical-print QA limit.

D-103 final checkpoint: the 200-page Word/PDF pair passes all artifact
checks and independent review. Every one of 251 navigation entries was
checked against the rendered page. All 77 figure/table groups have prior
numbered mentions; all 50 figure captions share an image page. The two
initial general confirmations are recorded as Done from the author's
instruction. Date and term are Deferred, not checked. The checklist and
SESSION_REVIEW.md contain exact reproduction commands and final hashes.
No experiment was rerun. No work outside writing/v8 was modified.

ID: D-111
Status: SETTLED
Decision: Commit and push this completed checklist revision on the existing thesis-revision-2026-09-12 branch to its configured origin branch.
Why: The workspace is already on that branch with its upstream configured. The standing project rule authorizes committing/pushing completed work; changing branches or rewriting another branch is unnecessary.
Alternatives: Force-update master (unnecessary); leave the finished work only on disk (contradicts standing delivery instruction).
Evidence: git status -sb and git for-each-ref identify origin/thesis-revision-2026-09-12 as the current upstream. All final validation and independent review pass; the diff is confined to writing/v8.
Reversibility: An ordinary subsequent commit can revert this revision; no history is rewritten.
Review: The final user report names the pushed commit and branch. Earlier SESSION_REVIEW master-delivery notes are historical.

D-111 delivery target superseded by D-112 at the author's request on
2026-09-14. The completed revision commit remains preserved.

ID: D-112
Status: SETTLED
Decision: Fast-forward master to the completed thesis revision, push master, and delete the local and remote thesis-revision-2026-09-12 branch after verifying its commit is on remote master.
Why: The author explicitly requested this integration and branch cleanup. The fetched remote master is an ancestor of the revision, so all history can be preserved without a merge commit or force push.
Alternatives: Keep the revision branch (contradicts the cleanup request); rewrite history (unnecessary).
Evidence: On 2026-09-14, git fetch origin succeeded; origin/master is 5e0403d56ca30cc9fd6b65d2159fa7bae9c36b2b and the revision tip is 156011f318cc770307100d2113819b6dffb0b6f9. git rev-list --left-right --count reports 0 and 1. The working tree is clean and only this worktree exists. Both thesis artifact hashes match the completed handoff.
Reversibility: Recreate the revision branch at 156011f318cc770307100d2113819b6dffb0b6f9 if needed; revert changes with ordinary commits.
Review: Verify remote master contains the revision tip before deleting either branch reference. The final user report records the pushed master hash and confirms deletion.

# Supervisor comments checklist

Each comment from the supervisor's messages, with where it is answered
in the built V7 chapters and its status. Comment numbering follows
PROF_COMMENTS_ROUND2.md (C1-C14) and PROF_COMMENTS_ROUND3.md (C15-C21,
the Chapter 3 T-matrix round of 2026-08-31; his verdict there:
"Other than this, the content looks okay"), and PROF_COMMENTS_ROUND4.md (C22-C47,
the 2026-09-05 round on Chapters 5, 7 and 2; verdicts "a good chapter",
"Good start", "Good job"), and PROF_COMMENTS_ROUND5.md (C48-C49, the
2026-09-07 comments on Chapter 4, applied to the whole thesis), and
PROF_COMMENTS_ROUND6.md (C50, the 2026-09-08 comment on Chapter 7: the
second arm in the rail experiment), and PROF_COMMENTS_ROUND7.md (C51-C53,
the 2026-09-10 comments on the abstract and the last chapter; his
verdict "Everything looks good"). Round 7 is listed first, then round 6,
then round 5, then round 4. Its Chapter 5 items (C22-C28)
are DONE in v8 since 2026-09-06 on the user's plan; the Chapter 7 items
wait on the user's decisions D6-D10 in that file.

# Round 7 (2026-09-10): the abstract and the last chapter

## C51. Rewrite the abstract: the problem and why, the challenges, how addressed, what accomplished (round 7, front matter)
- Where: the Abstract page (condensed/scripts/build_frontmatter.py,
  ABSTRACT), four paragraphs in his order; the same text as
  writing/v8/Abstract_V8.docx (scripts/build_abstract.py). Supersedes
  the C2 rewrite of 2026-08-28.
- Status: DONE (2026-09-10). 344 words; every number printed in
  Chapters 7 and 8; the C2 ground-truth statement kept.

## C52. A Discussion chapter (round 7, Ch9)
- Where: condensed/Chapter_9_Discussion.docx (condensed/scripts/
  build_ch9.py), Sections 9.1 to 9.7 by result, Figures 9.1 and 9.2,
  Table 9.1.
- Status: DONE (2026-09-10). D-022; number audit none missing;
  check_refs UNRESOLVED none.

## C53. A Conclusions and Future Work chapter (round 7, Ch10)
- Where: condensed/Chapter_10_Conclusions_Future_Work.docx
  (condensed/scripts/build_ch10.py), Sections 10.1 and 10.2.
- Status: DONE (2026-09-10). Registered in every builder and checker;
  cross-references in Chapters 1, 3, 7, 8 and Appendices E and G moved.

# Round 6 (2026-09-08): Chapter 7, the second arm in the rail experiment

## C50. Add the second arm to the rail experiment: one hand slides halfway, the other takes over (round 6, Ch7)
- Where: a new Chapter 7 section "Hand-over on the Rail" on a new
  recording of the whole rail task with the hand-over midway along the
  rail (the plan in PROF_COMMENTS_ROUND6.md; the recording steps in
  eval/RECORDING_R7_HANDOVER.md). The one-hand recording stays the
  thesis recording everywhere else; Chapters 1, 2, 7 and 9 and the
  abstract lose the sentences that say the rail task is one-handed.
- Status: DONE (2026-09-09). Recording recording_20260909_000024 (r7)
  accepted; Section 7.7 "Handover on the Rail" with Figures 7.11 to
  7.13 and Table 7.1 built from eval/reports/r7_handover.md,
  r7_rail_eval.md, r7_failure_mask.md, r7_hip_hold.md and the Unity
  capture eval/reports/unity_check_r7 (E-034, E-035, D-021); the
  recovery section is 7.8 and the solver check 7.9; Chapters 1, 2, 5,
  6, 9 and the abstract updated. User decision 2026-09-09: the hip hold (the
  user's freeze idea) stays a documented option and is not adopted for
  this version (E-034); revisit after the usage limit resets if the
  supervisor asks.

# Round 5 (2026-09-07): Chapter 4, applied to the whole thesis

## C48. Two decimals at most, in the matrices and in every number (round 5, Ch4)
- Where: every part of writing/v8/Thesis_V8_Condensed.docx. Chapter 4
  Section 4.3 (the two matrices, the seven vectors, the frame 786
  numbers), Chapter 5 Section 5.6 (arm lengths in centimetres),
  Chapter 6 Section 6.5 and Table 6.2 (session-clock times), Chapter 2
  Section 2.5 and Appendix F (the Hampel factor), Appendices C, D and
  E (the landmark, deprojection and marker worked examples, Tables
  C.2, D.1 and E.1). The other chapters were already at two decimals.
  Every old -> new pair: writing/v8/PRECISION_ROUND5_CHANGES.md.
  check_style.py now flags any three decimals; rule in
  skill_set/measurement-precision-reporting.md.
- Status: DONE (2026-09-07).

## C49. Show images of the experiment (round 5, Ch4)
- Where: new Figure 4.1 in Section 4.1, the four colour frames of the
  task (frames 95, 505, 700, 898) with the detected object marker
  outlined, its frame O and the world frame W drawn from the detected
  and calibrated poses, and a cube inset per panel
  (condensed/figures/ch4_fig_experiment.png,
  condensed/scripts/make_ch4_experiment_fig.py). The track plot is
  Figure 4.2.
- Status: DONE (2026-09-07).

# Round 4 (2026-09-05): Chapters 5, 7, 2

## C22. General readability in the user's voice (round 4, Ch5)
- Where: the whole of Chapter 5, rebuilt by v8/scripts/build_ch5.py.
- Status: DONE (2026-09-06). Whole chapter redrafted in shorter plainer
  sentences on the Chapter 2 sample and the humanizer rules; Opus
  review loop in writing/reviews/Chapter_5_v8_round*.txt; the user's
  own flattening pass still to come (plan item 6).

## C23. Schematic for equations 5.1 and 5.2 (round 4, Ch5)
- Where: Figure 5.3 (figures/ch5_fig_offset.png), directly under
  equation (5.2): (a) the read-off of the offset on a clean frame in
  world and object axes, (b) the same offset carried to a later frame.
- Status: DONE (2026-09-06).

## C24. Define every variable (round 4, Ch5)
- Where: Table 5.1 at the head of Section 5.3 (symbol, meaning, frame,
  where it comes from) plus first-use definitions. Collisions removed
  with Section 5.5 (torso repair) parked: h_k is the offset observation
  (was d), alpha is defined at equation (5.5), s is the circle turn only.
- Status: DONE (2026-09-06).

## C25. Ground-truth framing, offset h unknown in general (round 4, Ch5)
- Where: Section 5.3, the paragraph "While a hand grips the cube ...
  That offset is not known in general ..." with the forward pointer to
  the Chapter 7 wrist-versus-reference-path comparison (C35-C36 open).
- Status: DONE for Chapter 5 (2026-09-06); Chapter 7 side DONE (C35 and
  C36, 2026-09-07; Sections 7.4 and 7.5 read the wrist comparison as
  consistency because the offset is not known independently; figures
  redesigned 2026-09-08).

## C26. Fit with Chapters 3-4: wrist from the shoulder and elbow (round 4, Ch5)
- Where: the case list at the chapter opening (Case A wrist from the
  elbow along the forearm memory, Case B wrist from the object, Case C
  elbow by two-link IK), equation (5.6) for Case A, and the rebuild
  boxes of Figure 5.1.
- Status: DONE (2026-09-06).

## C27. Pipeline flow diagram at the chapter opening (round 4, Ch5)
- Where: Figure 5.1 (figures/ch5_fig_flow.png, make_ch5_flow_fig.py) in
  the style of Figure 3.1: inputs from Chapters 2-4, detectors, the
  three rebuild cases, the unchanged solve, the joint groups to
  Chapters 6 and 7, and the state carried between frames. The old
  pipeline figure is reduced to the three-state strip (Figure 5.6).
- Status: DONE (2026-09-06).

## C28. Assumptions and parameters, and how each is obtained (round 4, Ch5)
- Where: new Section 5.1 Assumptions and Parameters: six assumptions in
  plain sentences and a parameters paragraph in three kinds (no table since 2026-09-06; was Table 5.1: parameter, symbol, value, how it is
  obtained, section).
- Status: DONE (2026-09-06).

## C29. Verdict "it is a good chapter" (round 4, Ch5)
- Where: none.
- Status: DONE (no action).

## Chapter 5 decisions (round 4)
- D1 Section 5.5 torso repair: PARKED on the user's plan item 3 (torso
  assumed measured); verbatim in v8/CH5_PARKED.md. Sections 7.4, 8.1
  Table 8.1 and Chapter 9 still refer to it in v7 and change when those
  chapters enter v8.
- D2 rail hip-depth offset (E-027): CLOSED 2026-09-07 (user approved the
  Chapter 2 route). Section 2.6 states the preparation's checks, order,
  depth memory and replacement; Appendix G gives the exact branching,
  fallbacks and output tags of the frozen occlusion_ext.py; Chapter 5
  and Section 7.4 point at Section 2.6; Chapter 9 names the untested
  occluded start and the live pelvis translation that still uses the
  original hips. No Chapter 7 number changed (the results were already
  computed with the preparation).
- D3 manual labels: CLOSED 2026-09-06. The user placed every label on
  both recordings (rail 21 failure frames plus 5 clean, loop 20 failure
  frames plus 7 clean, 58 skipped), graded into
  eval/reports/r6b_recovery_labeled.md and r5_recovery_labeled.md, and
  the condensed thesis reports them: Section 7.3.3 (Tables 7.7 and
  7.8), Section 7.5 (Figures 7.9 and 7.10, frames 1462 and 1890), the
  Chapter 5 closing and Section 5.3 limit, Chapter 9 (9.1, Table 9.1,
  9.3). No number from the labels appears before Chapter 7.
- D4 torso detectors: KEPT as a report on the torso assumption (Table
  5.2, Figure 5.2 unchanged); the torso mask is reported, not acted on.
  Reversible.
- D5 bimanual wording: CLOSED 2026-09-07 (user approved the scoped
  wording, no re-recording). Chapter 1 (opening, 1.2.4, 1.3, Objective 5)
  and Section 9.3 state that the system covers both arms, that the
  primary rail evaluation is one-handed, and that the loop recording adds
  secondary bimanual evidence in the occlusion evaluation; neither
  recording establishes accuracy for general bimanual manipulation. The
  Chapter 5 opening no longer mentions a handover; Section 5.3 keeps the
  general statement that a handover is two overlapping episodes.

## C30. Object-station schematic with the marker origin (round 4, Ch7)
- Where: Section 7.1.1, new drawn figure (none exists; Figure 7.1 is a
  data plot, Figure 7.2 tape photographs).
- Status: DONE (2026-09-07, D-007). Figure 7.2 (ch7_fig_stations.png, make_ch7_task_schematic.py): the cube at the parked start, W1, W2 and W3 in the levelled world frame with the marker origin O and its axes on the face turned to the sensor and the world frame W at the desk marker; Section 7.1 says the reported pose is the pose of O and the cube centre lies half an edge behind it.
## C31. Protocol schematic; Figure 7.2 before 7.1 (round 4, Ch7)
- Where: Section 7.1.1, new opening figure and reorder of Figures 7.1
  and 7.2 in build_ch7.py.
- Status: DONE (2026-09-07, D-007). Figure 7.1 (ch7_fig_protocol.png): the one-handed task in four steps seen from the sensor with a top view; it opens Section 7.1 ahead of the station schematic, the rail dimensions and the colour-frame strip, and the data plots follow in 7.3. No handover: the recorded task is one-handed (D5) and the text says so.
## C32. Marker origin mapped to the world frame (round 4, Ch7)
- Where: Section 7.2, a mapping paragraph before Figure 7.6 (the
  mapping lives in Chapter 4 4.1-4.2 and Chapter 6 6.4; the plots
  exist).
- Status: DONE (2026-09-07). Section 7.3 opens with the mapping paragraph: the marker origin O measured in the camera frame, carried into W by the calibrated camera-to-world transformation of Table 2.2 (Section 4.1), the cube centre half an edge behind O, and the levelling of Section 6.4.
## C33. Colour frames of grasp, handover, release (round 4, Ch7)
- Where: Section 7.1.1 or 7.5, a new frame strip from the rail
  recording (extract_r6b_frames.py); no handover frame exists on the
  one-handed recording.
- Status: DONE for the one-handed task (2026-09-07). Figure 7.3 (ch7_fig_frames_strip.png, frames 95, 505, 700, 899): grasp on the desk, lift onto the rail, slide, far end with the hand withdrawn; the text says the release falls in the last frames. No handover frame exists (D5, one-handed recording).
## C34. Figure 7.3 and the wire removed (round 4, Ch7)
- Where: Figure 7.3 in 7.1.1; by extension every loop-recording item
  (Figure 7.5, Table 7.2, Figure 7.7, Table 7.3, 7.3.2, 7.3.3, loop part
  of 7.4, Figure 7.10), to be parked in CH7_PARKED.md.
- Status: DONE (2026-09-07, D-007). Figure 7.3 of V7 (the wire loop) and every loop trajectory and loop synthetic-masking item left Chapter 7 (parked verbatim in writing/v8/CH7_PARKED.md). The loop recording stays only as the second recording of the label study in Section 7.7 and as the lower panel of the failure figure (C39).
## C35. Wrist trajectory from the kinematic model vs ground truth (round 4, Ch7)
- Where: new section between 7.2 and the combined plot; script to
  write (fk_wrist in eval/failure/moving_window_check.py and
  LeveledWorld in eval/offset/carry.py exist; angles in
  eval/output/recovery_r6b/angles_recovery.csv).
- Status: DONE (2026-09-07). Section 7.4 and Figure 7.7 (ch7_fig_wrist_traj.png, make_ch7_wrist_traj_fig.py): the right wrist placed by forward kinematics from the recovery angles, the measured shoulder and the calibrated lengths, in the levelled world frame with the reference path and the rail line, coloured by state; read as consistency (median 6.5 cm from the line, the grip offset), because the wrist's ground truth is the line shifted by the unknown hand-object offset (C25).
## C36. Three plots in one frame and one unit (round 4, Ch7)
- Where: new combined figure after C35, levelled world frame,
  millimetres. "In the same Unity" also read as trails inside the
  Unity scene; ask him.
- Status: DONE, both readings (2026-09-07; presentation revised
  2026-09-08). Reading (a): Section 7.5 and Figure 7.8 (ch7_fig_combined.png),
  the fitted rail line, the object marker origin and the model right wrist
  over the slide samples, seen from above and from the side, one unit.
  Reading (b): Figure 7.10 (ch7_fig_unity_trails.png), the trajectories
  drawn inside the Unity scene. The first version (sensor pose, trails at
  frames 505 and 898, TrajectoryTrails.cs) was reviewed as unclear
  (condensed/CH7_TRAILS_REVIEW.md); the user approved the redesign
  (D-015 to D-019): one panel per task interval (carry 92-500, lift
  501-528, slide 529-899) from a fixed oblique presentation camera,
  translucent avatar, dashed waypoint reference, green marker origin,
  blue/orange model wrist by state; Chapter7TrailView.cs renders the stills
  while render_ch7_trails.py replays the saved E-032 stream; the recording
  and every reported number are unchanged (validate_ch7_trails_revision.py;
  condensed/CH7_TRAILS_IMPLEMENTATION.md). The user settled D9 ("do it if
  you can").

## C39. Figures 7.4 and 7.5 kept (round 4, Ch7)
- Where: 7.1.3, Figure 7.4 (rail) and Figure 7.5 (loop). Figure 7.5
  leaves with the loop recording if C34 drops it.
- Status: DONE (no change).

## C40. Earlier block experiments not needed (round 4, Ch7)
- Where: none present in Chapter 7; the earlier experiment still
  present is the loop recording, handled under C34.
- Status: DONE (nothing to remove beyond C34).

## C41. Per-part calculations and error sources elsewhere (round 4, Ch7)
- Where: Chapter 7 trimmed to overall results; 7.4 torso stability and
  the per-method tables of 7.3 parked; sources-of-error passages added
  to Chapter 3 (3.2, 3.4 or 3.5).
- Status: DONE (2026-09-07, D-007/D8). Chapter 7 keeps one short rail masking result (Table 7.1 and one reading paragraph) and the compact label study with both outcomes (Tables 7.2 and 7.3, Figures 7.10 and 7.11); the loop synthetic masking (old 7.3.2) and the torso stability section (old 7.4) are parked in CH7_PARKED.md, and Chapter 9 discusses their implications without the numbers. The solver check closes the chapter (7.8).
## C42. His closing question (round 4, Ch7)
- Where: the user's reply (suggested text in the round file).
- Status: DONE (2026-09-07, D-007). The user replied on the lines of CH7_RECOMMENDATIONS.md (D10); the chapter follows that reply.
## C43. Rename 2.4 and state where the filtering goes next (round 4, Ch2)
- Where: writing/v8 Section 2.5 Measurement Filtering (renamed from Signal Filtering); its closing sentences say the filtered landmarks feed the Chapter 3 solve and the object track is cleaned in Chapter 4 and used by Chapter 5.
- Status: DONE (2026-09-05, v8).

## C44. Clarity pass keeping the user's English level (round 4, Ch2)
- Where: writing/v8/CH2_CONCISION_LOG.md entries 106-130: the user's own sentences kept; 7 small edits (cross-references and single inserted sentences) and 17 re-patterned sentences of the moved calibration text, each listed before/after for the user to accept or reject.
- Status: DONE (2026-09-05, v8), pending the user's read of the log.

## C45. Scene picture with the coordinate frames drawn (round 4, Ch2)
- Where: writing/v8 Figure 2.5 (make_ch2_frames_fig.py): the colour frame with the wall marker frame, the world frame W on the desk marker, the object frame O, the camera frame C and arrows T_C,wall, T_CW, T_CO, T_WO, plus a top-view panel. World frame kept on the desk marker (user decision); the reply to the supervisor says why.
- Status: DONE (2026-09-05, v8).

## C46. Frames, T-matrix notation and calibration in Chapter 2 (round 4, Ch2)
- Where: writing/v8 Section 2.2 Coordinate Frames and Scene Calibration: 2.2.1 names every frame (C, W, wall, O, P, body frames, U) and the T notation with Table 2.2; 2.2.2 is the static calibration moved from Chapter 4 (equation (2.1), Table 2.3, Figure 2.6). Chapter 3 Section 3.1 and Chapter 4 Section 4.1 refer back. Chapter retitled Experimental Setup and Measurements.
- Status: DONE (2026-09-05, v8). Follow-up 2026-09-07 (Chapter 6 review):
  Table 2.2 now gives the world-to-Unity swap its symbol S with a pointer
  to Chapter 6 equation (6.1), and Chapter 6 equation (6.2) writes the
  person-to-display map also as the homogeneous matrix T_UP, with R_cam
  and t_cam named as the blocks of T_WC of Table 2.2, so no transformation
  after Chapter 2 is left in bare R and t form (C15).

## C47. Verdict "Good job" (round 4, Ch2)
- Where: none needed.
- Status: DONE (no action).

# Rounds 2 and 3

## C15. Show the homogeneous T matrix combining R and t (round 3)
- Where: Section 3.1. Equation (3.2) displays T as the 2 by 2 block
  matrix [[R, t], [0, 1]] with its action on a homogeneous point;
  the rotation-only mapping (now equation (3.3)) is explicitly scoped
  to directions and shared-origin frames, and equation (3.4) shows
  the inverse T that maps a point into the child frame.
- Status: DONE (2026-08-31). Chapter 6 equation (6.2) follows the same
  form since 2026-09-07 (T_UP beside A and S t_cam).

## C16. Define the T matrices between the frames of Figure 3.3 (round 3)
- Where: after the chain photograph (now Figure 3.4), equation (3.5)
  defines T_root, T_sh, T_el as block matrices, each with its own
  rotation and origin, and equation (3.6) composes them.
- Status: DONE.

## C17. Mapping logic stated before the details (round 3)
- Where: the paragraph after equation (3.6): every landmark is measured
  with respect to the sensor; the inverse transformations carry it into
  the frame where its joint is solved (shoulder into root, elbow into
  shoulder, wrist into elbow), before any construction begins.
- Status: DONE.

## C18. T matrix at the root assembly (round 3)
- Where: Section 3.2.2, equation (3.12): T_root = [[R_root, p24],
  [0, 1]] immediately after the root rotation and origin are built.
- Status: DONE.

## C19. Shoulder (and elbow) T with respect to the root (round 3)
- Where: Section 3.3.3, equations (3.13) and (3.14): the shoulder
  frame's T (identity rotation, origin R_root^T(p12 - p24)) and the
  elbow frame's T (solved shoulder rotation, origin in shoulder
  coordinates).
- Status: DONE.

## C20. Numeric T matrices in the worked example (round 3)
- Where: Section 3.5 prints T_root, T_sh, T_el as 4 by 4 numbers on
  the worked-example frame (values from ch3_numbers.py), and closes
  the chain with two checks: the composed product lands on the
  measured elbow to machine precision, and the wrist carried through
  the inverse chain reproduces the forearm length, the e_z = 0
  property, and the flexion input direction.
- Status: DONE.

## C21. Information-flow diagram at the chapter start (round 3)
- Where: new Figure 3.1 (make_ch3_flow_fig.py), drawn in the Chapter
  2/6 flow-figure family style, with an introduction paragraph; all
  other Chapter 3 figures shifted by one (now 3.2-3.11) and equations
  renumbered to 3.1-3.24.
- Status: DONE.

## C4. Whole-setup phone photo first in Chapter 2 + user-study objective
- Where: Chapter 2 opens Section 2.1 with the objective prose (task,
  wire, markers, sensor, ground truth) and Figure 2.1 before every
  other figure.
- Status: DONE with one caveat. The photos are in the build
  (2026-08-27): the wide shot is Figure 2.1 (first figure of the
  chapter) and the top-down drawn-path shot is Figure 2.4 in Section
  2.2; the later figures renumbered to 2.5-2.10 automatically. The
  supervisor's reference schematics are kept in figures/src as
  ref_prof_*.png.
- Caveat for the supervisor's exact wording: the wide shot does not
  show the RGB-D sensor on its mount or the participant. A retake
  with both in frame would satisfy C4 fully; overwrite
  writing/v7/figures/src/setup_phone.jpg and rerun build_ch2.py.

## C5. Equations broken in the Word file
- Where: all Chapter 3 equations, native Word math (OMML) from the same
  generator as before (user decision D14).
- Status: OPEN - cannot be verified on this machine. Check 3.1-3.5 in
  the supervisor's Word; if still broken, the fallback is rendering
  every equation to an image (one build-script switch).

## C6. Filtering: which filter, why, reference, results
- Where: Section 2.5 names the chain actually run on the primary
  recording (Hampel despike, 7-frame window, with references [53],
  [54]; linear gap bridging to 5 frames; zero-phase fourth-order
  Butterworth at 3 Hz with references [55], [56], [57]), states why
  each stage is chosen, and shows results in Figures 2.7-2.9
  (before/after despike, gap bridging, smoothing). One Euro [40] and
  Savitzky-Golay [46] are defined as the alternatives.
- Status: DONE.

## C7. Optional appendix on filter features
- Where: Appendix F "Characteristics of the Candidate Filters" in the
  TOC; Section 2.5 points to it and names the candidates.
- Status: DONE (2026-08-28): Appendix F is written in Appendices.docx
  (two fixed stages, then Butterworth, Savitzky-Golay, rolling median,
  One Euro, with Figure F.1 and a comparison table). If the supervisor
  declines the appendix, delete it from build_appendix.py and the
  pointer in Section 2.5.

## C8. Figure 2.5 unclear - break up, enlarge, label, caption
- Where: the old combined filter panel is now three separate figures
  (despike, gap bridging, smoothing), each with per-axis panels,
  larger fonts, legends, and its own caption.
- Status: DONE.

## C9. Kinematic arm schematic, PUMA style, before the joint-angle sections
- Where: new Section 3.3.1, placed before all of 3.4, now with two
  figures. Figure 3.6 states where the idea comes from: the standard
  seven-degree-of-freedom description of the human arm (q1 to q7) and
  its serial-chain equivalent in the PUMA convention, drawn after the
  supervisor's reference figures and cited to the robotics text [42],
  with the four solved rotations in colour and the unobservable wrist
  triple in grey; a mapping paragraph ties q1 to q4 to the thesis
  symbols. Figure 3.7 is the thesis's own schematic of those four
  joints on the body.
  Drawn as a serial chain of revolute-joint cylinders with dash-dot
  rotation axes, matching the robotics-course reference images the
  user supplied: three cylinders clustered at the shoulder (swing
  azimuth about y, swing elevation about z, twist about the arm axis),
  one hinge cylinder at the elbow, the wrist as a tracked point.
  Every solved angle is labelled with its symbol.
- Status: DONE.

## C10. Wrist is not a solved joint
- Where: Section 3.4.4 "The Wrist as a Tracked Point": the chain
  solves shoulder and elbow; the wrist is a tracked 3D point (with its
  roles: forearm direction, twist observability, recovery anchor,
  future hand-model attachment).
- Status: DONE.

## C11. Worked example must reference the kinematic diagram
- Where: Section 3.5 states up front that every solved value is
  pointed at its label in Figure 3.6, and each angle (swing azimuth,
  swing elevation, twist, elbow flexion) is read against the schematic
  at the step where it is solved.
- Status: DONE.

## C1. Title page format and committee members
- Where: the front matter of the assembled thesis (title page and
  Approval page), built by scripts/build_frontmatter.py.
- Status: BUILT WITH PLACEHOLDERS (2026-08-28). The title page follows
  the Eng.Sci. format order (title, author, degree statement, school,
  faculty, university, date, copyright) and the Approval page carries
  the committee block: a chair row, the supervisor row, and three
  member rows. The names and roles of the chair and the three members
  are bold placeholders, since the repository holds none; they are
  listed in Thesis_V7_Placeholders.md for the user to fill.

## C2. Abstract rewrite
- Where: the Abstract page of the assembled thesis. Superseded by the
  round 7 rewrite (C51, 2026-09-10), which keeps the ground-truth
  statement asked for here.
- Status: DONE (2026-08-28). Rewritten in the student's voice from the
  built Chapters 1, 7, 8 and 9, 319 words. It states that the drawn
  path in the laboratory is the ground truth and that the tracked
  object trajectory is compared with it, and it quotes only numbers
  printed in Chapters 7 and 8 (median 0.79 cm and 95th percentile
  9.32 cm to the designed path, 29.6 frames per second).

## C3. Chapter page breaks and format compliance
- Where: the assembled Thesis_V7.docx, built by scripts/build_thesis.py.
- Status: DONE (2026-08-28). Heading 1 carries a page break before it
  in the house style, so every chapter, the references, and each
  appendix begin on a new page. The whole document runs on one style
  set: Times New Roman, black, no theme fonts and no theme colours.

## Comments outside the Chapters 1-3 scope
- C12 (chordal-mean anchor definition): handed to the Chapter 4 writer
  2026-08-28 - plain definition at first use or shorthand removed.

# V7 supervisor comments, round of 2026-09-05 (Chapters 5, 7 and 2)

Every comment from the supervisor's three messages of 2026-09-05 on
the assembled V7, mapped to its target, what the current build holds
(verified against the built chapter files and their build scripts),
the planned action, and the decisions only the user can make.
Numbering continues from PROF_COMMENTS_ROUND3.md (C15-C21):

- C22-C29: Chapter 5 (Pose Recovery), with the user's own plan for the
  chapter as sent to the supervisor the same day.
- C30-C42: Chapter 7 (Evaluation), verdict "Good start."
- C43-C47: Chapter 2 (Experimental Setup), verdict "Good job."

Two directions in these messages apply to every chapter and are
recorded as standing rules: AI revision must keep the user's level of
English (skill_set/user-voice-drafting.md), and reported errors stop
at the sensor's precision, millimetres, never e-13
(skill_set/measurement-precision-reporting.md).

The Chapter 2 items (C43-C46) are implemented in writing/v8 (2026-09-05). The change work waits on the user's decisions listed at
the end.

# Chapter 5 block (C22-C29)

Supervisor's message on Chapter 5 of V7, received 2026-09-05, with the
user's reply to him restated as the plan. Numbering continues from
PROF_COMMENTS_ROUND3.md (C15-C21). Overall verdict in the same
message: "Other than this, it is a good chapter." Every "Current"
line below is checked against writing/v7/Chapter_5_Pose_Recovery.docx
and its source writing/v7/scripts/build_ch5.py (the equations are Word
math built from that script).

## C22. General readability: revise with AI, keep the style and the English
"One general comment. You can ask AI tool to revise it but keep the
style and English similar. The write-up does not read smooth."
- Target: the whole chapter, every section.
- Current: Chapter 5 is the AI draft after the review loops of
  2026-08-28 to 2026-09-02 (sentence splits, statement style). It has
  not had the user's flattening pass that Chapter 2 sections 2.2-2.4
  received (commit 669cff0, the user's own text kept verbatim).
  Sentences such as "The object cannot do more than this" and
  "Continuity settles it" are the drafting voice, not the user's.
- Action: a prose pass in the user's voice: shorter sentences, plain
  words, the user's vocabulary level, no change of content. The
  reference for the target style is Chapter 2 sections 2.2-2.4. Per
  the user's workflow, AI drafts the pass and the user reads it and
  flattens it further by hand.
- Status: OPEN.

## C23. A simple schematic for equations 5.1 and 5.2
"Also, add a simple schematic when you are explaining equations 5.1
and 5.2"
- Target: Section 5.2, at equations (5.1) and (5.2).
- Current: Figure 5.2(a) (figures/ch5_fig_grip.png) already draws the
  object axes R_obj, the origin o, the offset h, the measured wrist and
  the recovered wrist. It is placed after equation (5.4) and the
  holding-state paragraphs (build_ch5.py line 224), beside the
  state-machine panel (b), so it is four equations and five paragraphs
  away from equations (5.1) and (5.2). It does not draw the read-off
  of equation (5.2): the world-frame displacement p_wr - o and its
  expression d in the object's axes.
- Action: a dedicated one-panel schematic placed directly under
  equation (5.2): the object with its axes R_obj at origin o, the
  wrist p_wr, the displacement p_wr - o drawn in the world axes, and
  the same vector read in the object axes as d (equal to h while the
  grasp is rigid). Panel (a) of Figure 5.2 then either moves up to
  become that schematic (with d added) or is left as is and the new
  figure becomes Figure 5.2 with the state machine renumbered 5.3.
- Status: PARTIAL (figure exists, wrong place, missing the vector of
  equation (5.2)).

## C24. Define every variable used in the chapter
"You should also define all the variables which you used in this
chapter if they are not defined before."
- Target: the whole chapter; a notation paragraph at the start of
  Section 5.2 and first-use definitions elsewhere.
- Current: audit of every symbol in equations (5.1)-(5.23) and the
  prose around them, from build_ch5.py.

  Defined at first use in this chapter:
  p_sh, p_el, p_wr (5.2, tied to p12, p14, p16 of Chapter 3); o and
  R_obj (5.2, "origin" and "orientation" of the object from Chapter
  4); h (5.2, wrist position in the object's axes); d and d_k (5.2,
  the per-frame read-off, frame k); N (number of clean frames); c
  (gain of (5.4), 0.02); w (5.3, the wrist estimate); L1, L2 (5.3 and
  5.4, calibrated upper-arm and forearm lengths); b, r, b_hat (5.4,
  shoulder-to-wrist vector, its length, its unit vector); j (5.4,
  angle at the shoulder); p_c, r_c (5.4, circle centre and radius);
  n1, n2 (5.4, two unit vectors spanning the circle plane); s (5.4,
  the turn angle about the shoulder-to-wrist line); u_hat (5.4,
  remembered upper-arm direction); u_perp (5.4); (u, v), d, K, p
  (5.5.1, pixel, depth sample, colour intrinsics, lifted point);
  p', d' (5.5.1, corrupt point and occluder depth); delta, L_t
  (5.5.1, common hip depth error, trunk height); p_z, z* (5.5.2,
  depth coordinate, chosen depth); z_mem (5.5.2); theta (5.5.3);
  Delta_h, Delta_s (5.5.3); s_mid, s_mid,z (5.5.5); phi, Delta z
  (5.5.5); q_a, q_b, m, u_hat_pair, w (5.5.6, endpoints, midpoint,
  pair direction memory, calibrated width).

  Used without a definition in this chapter:
  alpha, the gain 0.30 of equation (5.16): the sentence after (5.16)
  says "the same gain alpha = 0.30 as the direction memories of
  equation (5.4)", but equation (5.4) is written with the gain c =
  0.02 and the direction memories of Section 5.2 are described in
  prose only ("a gain of 0.30"); alpha appears nowhere before (5.16).
  h_hat_mem and s_hat_mem in equation (5.18): the prose says "its own
  direction memory" but never names these two symbols. f and c in the
  projection "u = f x / z + c" of Section 5.5.2: focal length and
  principal point are not defined, and this c is not the gain c of
  (5.4). x, z in the same expression. p_a, p_b in (5.23) are only
  implied by q_a, q_b. p12, p14, p16, R^T, equation (3.1) and (3.3)
  rely on Chapter 3; K and the deprojection rely on Appendix D.

  Symbol collisions inside the chapter (confirmed in the script):
  h = hand-object offset (5.1)-(5.5) AND h = hip midpoint (prose of
  5.5.1: "hip midpoint h and the shoulder midpoint s") AND h = hip
  line from left hip to right hip (5.17)-(5.18).
  s = shoulder midpoint (5.5.1 prose) AND s = turn angle about the
  shoulder-to-wrist line (5.10)-(5.11) AND s = shoulder line
  (5.17)-(5.18).
  w = wrist estimate from the object (5.5)-(5.6) AND w = calibrated
  pair width (5.23).
  d = read-off offset observation (5.2), (5.4) AND d = depth sample
  behind a pixel (5.12)-(5.13).
  c = offset gain 0.02 (5.4) AND c = principal point in "u = f x / z
  + c" (5.5.2 prose).
  u_hat = remembered upper-arm direction (5.11) AND u = pixel column
  (5.12) AND u_hat_pair = pair direction memory (5.23); the
  shoulder-to-wrist vector itself is b, not u.
  p = generic lifted point (5.12)-(5.15) alongside p_sh, p_el, p_wr,
  p_a, p_b.
- Action: a notation paragraph at the head of Section 5.2 (or a short
  table) listing every symbol, its meaning, its frame, and where it
  comes from (Chapter 3 landmark numbers, Chapter 4 object pose,
  Appendix D intrinsics). Rename the colliding symbols so each letter
  has one meaning: for example the hip and shoulder lines as l_hip
  and l_sh with midpoints m_hip and m_sh; the pair width as w_pair or
  W; the depth sample as z_d or keep d for depth and rename the offset
  observation to h_k; the circle turn angle as psi; the pixel
  coordinates kept as (u, v) with the direction memories as e_hat. Define
  alpha where the direction memory is introduced in Section 5.2, and
  state there that (5.4) is the same update with gain c. Define f and
  c_x or drop the projection formula and cite Appendix D.
- Status: OPEN.

## C25. Ground-truth comparison: marker trajectory and both wrists, offset h unknown in general
"Remember, when we comparing the track data with the ground truth, we
compare the trajectory of the Aruco marker on the object which is
being handled and the position of the writs points of the two hands
(knowing there will be an offset of where the object aruco marker is
and where the writs point is. Although for example you can assume
some h, but in general, we will not know. Hence, by comparing with
the ground truth, we can have some sense of how far away tracked and
reconstructed data are with respect to the ground truth."
- Target: Section 5.2 (what h is and that it is not known in advance)
  and Chapter 7 (the wrist trajectory against the reference path, see
  the Chapter 7 block C35-C36).
- Current: Section 5.2 defines h as the wrist position in the
  object's axes and fits it from clean frames by equations (5.2)-(5.4).
  It never says in one sentence that h is unknown a priori, differs
  per grasp, and is estimated only from frames where both the wrist
  and the marker are measured. Chapter 7 compares the object
  trajectory with the rail line (Section 7.2, Figure 7.6) and grades
  the recovered wrist only against the tracker's own wrist on masked
  frames (Table 7.4); no wrist trajectory is compared with the
  reference path.
- Action: in Section 5.2, one plain paragraph: the wrist is not on the
  marker; the offset h between the marker origin and the wrist is not
  known in general; in this work it is estimated from the clean frames
  of each grasp; the accuracy of the reconstructed wrist is therefore
  read against the ground-truth path in Chapter 7 together with the
  marker trajectory, and the comparison shows how far the tracked and
  reconstructed data sit from the ground truth. The Chapter 7 side is
  C35-C36.
- Status: OPEN.

## C26. How the chapter fits Chapters 3-4: a missing wrist from the shoulder and elbow
"Also, I am not sure how this chapter (beside saying that you have
various missing data cases) will fit previous chapters. For example,
in previous chapters we track the Aruco marker on the object and we
can compare it with the ground truth. Then, we use the kinematic
model of the arms based on the measured landmarks to compute the
position of the wrist. It is not clear for example, if the writs
landmark is missing, can we estimate where the writs can be using the
kinematic model of the elbow and shoulder."
- Target: the chapter opening (before Section 5.1) and Section 5.2.
- Current: the opening three paragraphs say the layer decides,
  rebuilds and labels, without listing the missing-data cases. The
  case the supervisor asks about (wrist missing, shoulder and elbow
  measured) is answered only inside the direction-memory paragraph at
  the end of Section 5.2: "A missing landmark is then rebuilt by
  stepping the segment's calibrated length from its measured
  neighbour along that direction", with a 45-frame staleness horizon
  after which the arm holds its last angles. It is not stated as a
  case, and the rebuild box of Figure 5.5 lists four rebuilds (torso
  point on its ray, shoulder or hip from its partner, wrist from the
  object, elbow by two-link IK) and omits this one. The elbow case is
  Section 5.4; the holding-hand wrist case is Section 5.3.
- Action: a case list at the start of the chapter, in the words of
  the Chapter 3 chain: (a) wrist missing, shoulder and elbow measured:
  the wrist is placed at the calibrated forearm length L2 from the
  elbow along the remembered forearm direction (forward kinematics on
  the memory), Section 5.2; (b) wrist missing while the hand holds the
  object: the wrist is placed from the marker pose and the offset h,
  Section 5.3; (c) elbow missing, shoulder and wrist known: two-link
  inverse kinematics, Section 5.4; (d) a torso point corrupt in depth:
  Section 5.5 (or, under the user's plan, out of scope). Each case
  names the Chapter 3 quantities it uses (L1, L2, the root frame) and
  the Chapter 4 quantity (o, R_obj). Add the case (a) rebuild to the
  pipeline figure of C27.
- Status: PARTIAL (mechanisms exist; the case list does not).

## C27. Information pipeline flow diagram at the beginning of the chapter
"Perhapse you want to add some sort of information pipeline flow
diagram at the begineeing of how the estimation part of this chapter
is used within the models presented in the previous chapter."
- Target: a new Figure 5.1 at the chapter opening.
- Current: Figure 5.5 (figures/ch5_fig_states.png, build_ch5.py line
  502) is a pipeline figure, landmarks to detectors to rebuild to the
  Chapter 3 solve to the seven joint groups, with the three output
  states. It sits at the end of the chapter in Section 5.6. It does
  not show the inputs from the earlier chapters (filtered landmarks
  of Chapter 2, calibrated lengths L1, L2 and pair widths of Chapter
  3, object pose o and R_obj of Chapter 4) nor the outputs (Chapter 6
  reconstruction, Chapter 7 evaluation). The precedent is Chapter 3
  Figure 3.1 (comment C21, make_ch3_flow_fig.py), which opens that
  chapter with the flow from Chapter 2 landmarks to the solved angles.
- Action: a flow figure as the new Figure 5.1, drawn in the style of
  Figure 3.1: left, the inputs by chapter (landmarks with source
  flags, Chapter 2; chain and calibrated lengths, Chapter 3; marker
  pose, Chapter 4); centre, the detectors, the rebuild cases of C26,
  and the unchanged Chapter 3 solve; right, the joint groups with
  their states to Chapter 6 and Chapter 7. Figure 5.5 then either
  becomes this figure or is reduced to the three-state strip. Figures
  renumber 5.1-5.6.
- Status: PARTIAL (figure exists at the end, without the cross-chapter
  inputs and outputs).

## C28. State the assumptions and the parameters needed, and how each is obtained
"Also state a clear assumptions about what parameters you need (e.g.
h) in order for this estimation to work properly and how in collected
data experiments, this parameters is obtained."
- Target: a new subsection at the start of the chapter, "Assumptions
  and Parameters", with one table.
- Current: no consolidated statement. The values are scattered
  through the prose and the source comments of build_ch5.py:
  Hand-object offset h: fitted per grip episode by the mean of
  equation (5.3), then tracked by the recursive update (5.4) with
  gain c = 0.02 (about the last fifty frames); warm-up of five clean
  frames uses the episode mean; an episode with fewer than fifteen
  clean frames falls back to the whole-recording fit; discarded above
  0.30 m (Section 5.3). Source: clean frames of the recording itself.
  Upper-arm and forearm lengths L1, L2: median of the measured segment
  over the first sixty clean frames of the recording, or supplied from
  an earlier calibration (Section 5.4; Chapter 3 calibration).
  Torso pair widths and four diagonals: median over the first sixty
  frames with both endpoints measured, or supplied (Section 5.5.3).
  Trunk length L_t: about 0.48 m, quoted from Section 6.3 (5.5.5).
  Direction memories: recursive update with gain 0.30, unit
  renormalised, stale after 45 frames without an update (Section 5.2).
  Depth memories: same gain 0.30, no staleness horizon, seeded on the
  first measured depth (5.16).
  Holding state: hold radius 0.25 m, release radius 0.35 m, entry and
  exit after five consecutive frames, forearm within 30 percent of its
  median (Section 5.2).
  Detector thresholds (Table 5.1): segment length 35 percent, torso
  line angle 22 degrees, width ratio 20 percent, landmark step 5 cm
  per frame, grip plausibility 0.35 m; set at the 99th percentile of a
  separate reference recording's clean frames plus a margin.
  Mask cleaning: gaps of at most five frames closed, runs shorter than
  five frames dropped (Section 5.1).
  Torso gates: width and diagonal tolerance 30 percent; line
  disagreement trips at 20 degrees, releases under 10 degrees; depth
  jump 0.10 m; shoulder-depth gate 0.15 m (18 degrees of lean at L_t =
  0.48 m); two-link reach guard at 98 percent of L1 + L2; twist hold
  below 15 degrees of elbow flexion, released above 25; rate limit 15
  degrees per frame (Sections 5.4-5.6).
  Frames and maps: object pose in the gravity-levelled world frame of
  Chapter 4; the fixed rigid map from the scene calibration carries the
  wrist estimate into person space (Section 5.3).
- Action: a subsection before Section 5.1 with (1) the assumptions in
  plain sentences (the recording is mostly clean; failures are short
  windows; the torso is measured on every frame under the user's plan;
  the grasp is rigid within an episode; the marker stays visible while
  the hand is hidden; bone lengths are constant), and (2) a table
  "Parameter, value, how it is obtained in the recorded data" built
  from the list above. Everything that Section 5.5 owns drops out of
  the table if Section 5.5 leaves the chapter (see the plan below).
- Status: OPEN.

## C29. Verdict
"Other than this, it is a good chapter."
- Action: none.
- Status: DONE (no action).

## User's plan for Chapter 5 (2026-09-05)

The user's reply to the supervisor, restated as the planned scope of
the rewrite:

1. Chapter 5 is the occlusion-handling chapter and it carries stated
   limitations (assumptions). Having limitations is a strength: it
   shows the method is understood.
2. Occlusion means some missing data points in an otherwise clean
   recording. Most frames have every landmark detected; the missing
   points are isolated windows.
3. The torso, and landmark 24 in particular, is assumed measured on
   every frame. Loss of the root frame is out of scope of this thesis.
4. Chapter 7 gets a matching evaluation case: withhold some measured
   data, apply the Chapter 5 mathematics, and compare the result with
   the recorded data. Where MediaPipe drifts because the pose is
   unclear, the reference is the wrist pixel labelled by hand, lifted
   through the depth image, and compared with the computed value.
5. The thesis is too long (the user counts 169 pages) and must keep
   its focus; Chapter 5 stays simple.
6. Workflow: AI drafts, the user reviews, flattens the sentence
   structure and replaces complex words. Chapter 2 sections 2.2-2.4
   (commit 669cff0) are the style reference.
7. The newer Chapter 3 (24 pages) arrives from the user next.

Tensions between that plan and the current build, listed as decisions
for the user:

- D1. Section 5.5 versus "torso always good". Section 5.5 (torso
  repair on camera rays) is seven subsections, equations (5.12)-(5.23),
  Figure 5.4, and about a third of the chapter's text; Chapter 7
  Section 7.4 (Figure 7.9, Table 7.8) evaluates it, and Chapter 9 has a
  limitation row for it. Under assumption 3 this material either moves
  out of the thesis (parked, the CH6_PARKED.md precedent) or shrinks to
  a short note stating the assumption and pointing to future work.
  Either way Sections 5.1 (torso detectors), 5.6 (root group states),
  7.4 and 9 must lose their torso-repair references, and the depth
  memories drop out of C28.
- D2. The rail recording's hip depth. E-027 (PROGRESS.md round 4;
  build_ch7.py Section 7.4, the paragraph beginning "The rail recording
  shows how far that repair reaches") found that on the rail recording
  both hip landmarks take the rail's depth (0.99 m against 1.22 m on
  the body) on all but the opening frames, so the measured trunk reads
  about 24-32 degrees from upright on an upright participant. Today
  Section 5.5 repairs that (recovered trunk 8 degrees from vertical),
  and Chapter 3's worked example on frame 533 states the pitched root.
  If the torso is assumed measured and Section 5.5 goes, the
  assumption is false on this recording as it stands, so the offset
  must be absorbed elsewhere: as a Chapter 2 measurement-filtering
  step (hip depth taken from the body, or the hips levelled by the
  calibrated vertical), or as a stated Chapter 9 limitation with the
  arm angles read against the pitched root. The choice also changes
  every arm-angle number in Chapter 7.
- D3. Section 7.3.3 manual labels. The manual-label protocol is
  defined on the loop recording (78 frames between frames 1427 and
  1890, both natural blackouts), while the thesis has been rail-only
  since 2026-09-01 and the supervisor's Chapter 7 round drops the loop
  material (see the Chapter 7 block, C34). Plan item 4 needs the label
  set redefined on the rail recording's own drift frames, with the
  selection rule restated, before any labels are placed.
- D4. Detector scope under assumption 2. Table 5.1 keeps six
  detectors, two of them torso detectors (line angle, width ratio),
  plus the three-mask cleaning. With the torso assumed measured, the
  arm-side detectors (acquisition, segment length, landmark step, grip
  plausibility) are the ones that remain; the user decides whether the
  torso detectors stay as a consistency check or go with Section 5.5.
- D5. Chapter 1 still calls the task bimanual (PROGRESS.md notes 14
  occurrences) while the rail recording is one-handed; the opening
  paragraph of Chapter 5 ("in a two-handed task the two hands meet
  during a handover") inherits the same mismatch. Same decision as the
  Chapter 7 block's C31.

# Chapter 7 block (C30-C42)

Every comment from the supervisor's Chapter 7 message ("Good start."),
mapped to its target and action. Numbering continues from the Chapter 5
block of this round (C22-C29). Every "Current" line was checked against
writing/v7/Chapter_7_Evaluation.docx, its source
writing/v7/scripts/build_ch7.py, and writing/v7/figures/.

Facts that several comments depend on:

- The thesis task is one-handed. Chapter 2 (build_ch2.py, 2.1): "One
  participant moves a cube along the desk and then along a wooden rail
  with one hand." Chapter 7 (7.1 opening): "sliding the cube along the
  desk, onto the rail, and along the rail with one hand." PROGRESS.md
  and skill_set/evaluation-scenario-separation.md record the rail
  recording as a one-handed slide (900 frames, 29.99 s). The supervisor
  describes a grasp, a slide along the wood, a handover to the other
  hand, and a placement at the end, and closes with "the overall results
  of bi-manual operation." Chapter 1 still calls the task bimanual
  (14 occurrences noted in PROGRESS.md; goal statement "bimanual object
  manipulation", objective 5 "a designed bimanual object-handling
  task"). Only the loop recording has handovers, and that is the
  recording he wants removed (C34, C40).
- Loop-recording blast radius in Chapter 7 (verified by section):
  7.1.1 loop paragraph and Figure 7.3; 7.1.3 Figure 7.5 and Table 7.2
  (the 2037-frame detector counts); 7.2 second half: Figure 7.7,
  Table 7.3 and the loop-vs-rail comparison paragraphs; 7.3 opening
  paragraph (mentions the loop and manual labels); 7.3.2 whole
  (Table 7.5, Figure 7.8, Table 7.6); 7.3.3 whole (Table 7.7, the
  pending manual labels are defined on loop frames 1427-1890); 7.4
  first part (Figure 7.9, Table 7.8 on loop windows); 7.5 (Figure 7.10
  is a loop frame). Rail-only content that survives untouched: 7.1.1
  rail paragraphs with Figures 7.1 and 7.2; 7.1.2 (Table 7.1 and the
  rail solver check); Figure 7.4; 7.2 first half (Figure 7.6); 7.3.1
  (Table 7.4); 7.4 rail paragraphs and the synthetic-corruption check.

## C30. Schematics of the object at its stations, with the marker origin
"Draw some schematics showing how the object suppose to be at
different locations along the experiments and where the origin of its
aruco marker suppose to be."
- Target: Section 7.1.1, a new drawn figure before the measured
  trajectory plot.
- Current (verified): no drawn schematic exists. Figure 7.1
  (ch7_fig_rail_traj.png, make_ch7_rail_traj_fig.py) is a data plot of
  the tracked cube centre with the reference path and waypoints W1, W2,
  W3. Figure 7.2 (ch2_fig_rail_dims.png, make_ch2_rail_figs.py) is two
  tape-measure photographs. Chapter 2 Figure 2.1 is a photograph
  composite (ch2_fig_rail_setup.png) and Figure 2.2 a labelled colour
  frame (ch2_fig_setup.png); neither draws the object stations or the
  marker origin.
- Action: a new drawn figure (make_ch7_task_schematic.py): the desk,
  the rail, and the cube drawn at its stations (parked start, W1 end of
  the desk move, W2 top of the lift, W3 rail end) with the marker
  origin (marker centre, world-frame axes of Chapter 4) drawn on the
  cube at each station, and the world frame drawn once at the desk
  marker. Same frame and axis labels as Figure 7.1 so the data plot
  reads against it.
- Status: OPEN.

## C31. Schematics of how the subject performs the task; Figure 7.2 first
"Draw some schematics on how the subject suppose to preform the
experiments. For example, how to subject suppose to grasp the object
and move it along the wood and how the object is the grasped by the
other hand and finally placed at the end point. Figure 7.2 should come
before 7.1"
- Target: Section 7.1.1, opening figure of the chapter.
- Current (verified): no protocol schematic exists. 7.1.1 opens with
  Figure 7.1 (data plot) and then Figure 7.2 (rail tape photos). The
  task described in 7.1 and in Chapter 2 is a one-handed slide with no
  handover; the supervisor describes a handover to the other hand.
- Action: a drawn step schematic (grasp on the desk, carry to the
  rail, slide along the rail, release at the end; a handover panel only
  if the task is re-recorded two-handed), placed first in 7.1.1,
  followed by the object-station schematic of C30 and the rail
  dimensions (current Figure 7.2), then the measured trajectory
  (current Figure 7.1). Reorder the IMG/CAP items in build_ch7.py and
  renumber F_RTRAJ, F_RDIMS.
- Decision needed (user): re-record the rail task two-handed (grasp,
  slide, hand over to the other hand mid-rail, place at the end) so
  that the thesis matches the supervisor's description and Chapter 1's
  "bimanual" wording; or keep the one-handed recording and tell the
  supervisor plainly that the recorded task is one-handed. Every
  number in 7.2, 7.3.1, 7.4 and the abstract would change with a new
  recording.
- Status: OPEN (blocked on the decision for the handover panel; the
  reorder and the one-handed schematic can be done now).

## C32. How the computed marker origin is mapped to the world frame
"Then, talk about how the computed origin of the object aruco marker
is mapped to the World frame and the associated plots."
- Target: Section 7.2, opening paragraph.
- Current (verified): 7.2 opens directly with the rail-line fit and
  Figure 7.6 ("the tracked cube trajectory in the gravity-levelled
  world frame"). The mapping itself is in Chapter 4 (4.1 Static Scene
  Calibration, 4.2 World Anchoring) and the levelling in Chapter 6
  (6.4). Chapter 7 does not restate it.
- Action: one short paragraph before Figure 7.6: the marker pose is
  measured in the camera frame, carried into the world frame by the
  calibrated camera-to-world transformation of Chapter 4 (name the T
  matrix in the notation the Chapter 2 frame figure of this round will
  fix, C45/C46), and levelled by the calibrated gravity; then the
  plots. Keep the ArUco-centre-to-cube-centre step explicit, since the
  marker origin is what he asks about.
- Status: PARTIAL (plots exist; the mapping paragraph is missing).

## C33. Images of the grasp, the handover, and the release
"Show images of how the hand grasp the object at the beginning, then
pass it to the other hand and how it is released at the end."
- Target: Section 7.1.1 (beside the protocol schematic) or 7.5.
- Current (verified): no colour-frame strip of the task exists in
  Chapter 7. The only colour frames are Figure 7.10 (one loop frame
  with the reprojected skeleton, ch7_fig_overlay.png) and, in Chapter 2,
  Figure 2.1(c) (one mid-rail frame). Frame extraction for the rail
  recording exists (scripts/extract_r6b_frames.py).
- Action: a strip of three or four colour frames of the rail
  recording: the grasp at the parked start, the lift onto the rail,
  mid-slide, the release at the rail end. A handover frame exists only
  if the task is re-recorded (C31 decision).
- Status: OPEN.

## C34. Figure 7.3 and the wire are no longer needed
"I do not understand Figure 7.3 it is talking about the wire and we do
not need this any more."
- Target: Figure 7.3 and everything in Chapter 7 that rests on the
  loop recording (list above).
- Current (verified): Figure 7.3 (ch2_fig_path.png) is the designed
  loop with eight stations and the wire level, introduced in 7.1.1 as
  "the second recording ... the scenario with occlusion".
- Action: remove Figure 7.3 and the loop paragraph of 7.1.1. Removing
  the loop recording altogether (his "we do not need this any more"
  read together with C40) also removes Figure 7.5, Table 7.2, Figure
  7.7, Table 7.3, Section 7.3.2, Section 7.3.3, the loop part of 7.4
  and Figure 7.10. The occlusion evaluation then rests on the rail
  recording alone: synthetic masking (7.3.1) plus manual wrist labels
  on rail frames where MediaPipe drifts (the user's Chapter 5 plan).
  Park the removed material verbatim in writing/v7/CH7_PARKED.md
  (precedent CH6_PARKED.md).
- Decision needed (user): drop the loop recording from the thesis
  entirely, or keep it only for the natural-occlusion labels of
  7.3.3. The user's own Chapter 5 plan (occlusion limited to some
  missing points in an otherwise clean recording) points to dropping
  it.
- Status: OPEN.

## C35. Wrist position through the kinematic model against ground truth
"The next plot you need is to show the position of the wrist
computation through your kinematic model against the ground truth.
This should be in the World frame as well."
- Target: new Section 7.3 (wrist trajectory), between the object
  trajectory and the combined plot.
- Current (verified): no such plot exists. The wrist appears only in
  Table 7.4 (7.3.1) as a distance between the wrist the solved angles
  place and the wrist the tracker measured, on five masked windows, in
  the solver's point space. Nothing in Chapter 7 plots a wrist
  trajectory, and nothing compares a wrist with the rail line.
- What exists in code: forward kinematics from angles to a wrist
  position, eval/failure/moving_window_check.py fk_wrist(angles, i, sh,
  Lu, Lf, side), used for Table 7.4; the camera-to-levelled-world map
  for landmarks, eval/offset/carry.py LeveledWorld.wrist_world; the
  inverse map from levelled world to solver space,
  eval/failure/recovery_core.py _leveled_to_solver_space; the solved
  angles per frame with pelvis position,
  eval/output/recovery_r6b/angles_recovery.csv (root, shoulder, elbow
  angles of both arms, live mask, tags, pel_x/y/z); the rail line and
  its frame, eval/gt/eval_rail_scenario.py and
  eval/reports/r6b_waypoints.json.
- What has to be written: one script (make_ch7_wrist_traj_fig.py) that
  runs fk_wrist over all 900 frames for both arms from
  angles_recovery.csv with the calibrated L1, L2, maps the result into
  the levelled world frame of Figure 7.6, and plots both wrists against
  the rail line and the cube centre; plus the numbers (perpendicular
  distance of the holding wrist to the rail line, its median and p95,
  and its spread, in millimetres per C38). The ground truth of the
  wrist is the rail line shifted by the hand-object offset h, which is
  not known in general (his Chapter 5 comment, C25), so the plot is
  read as: the wrist runs parallel to the rail line at a near-constant
  offset, and the spread of that offset is the accuracy figure.
- Status: OPEN.

## C36. The three plots in one frame and one unit
"Then, compare these three plots in the same coordinate frame and in
the same Unity."
- Target: new combined figure after C35.
- Current (verified): the cube trajectory (Figure 7.6) and the
  reference path (Figure 7.1) are already in the gravity-levelled world
  frame; the wrist plot does not exist. No combined figure exists.
- Action: one figure, one axis set, one unit (centimetres or
  millimetres, C38): the rail line (ground truth), the cube centre, and
  the two wrists, all in the levelled world frame. Two readings of "in
  the same Unity": (a) "the same units", which the combined figure
  satisfies; (b) the same Unity scene, which means drawing the three
  trajectories inside the Unity reconstruction of C37 as trails. Do
  (a) as the figure and ask him in the reply whether he also wants
  (b); (b) is a Unity-side change (trail renderers on the cube and the
  wrist joints).
- Status: DONE, both readings (2026-09-07): (a) Figure 7.8; (b) Figure
  7.10, the trajectories drawn inside the Unity scene, at the user's
  direction "do it if you can" (D9 settled by the user, not by the
  supervisor). Figure 7.10 redesigned 2026-09-08 after the clarity review
  (one panel per task interval from a fixed presentation camera,
  Chapter7TrailView.cs, D-015 to D-019); Figures 7.5, 7.7 and 7.8 and the
  text of 7.3 to 7.6 now name the plotted object point as the marker
  origin. Record: condensed/CH7_TRAILS_IMPLEMENTATION.md.

## C37. Show the Unity reconstruction
"Then, show the Unity reconstruction."
- Target: Section 7.5 (or a new 7.4 after the combined plot).
- Current (verified): Chapter 7 contains no Unity figure and no
  mention of Unity. The Unity reconstruction exists in Chapter 6 as
  Figure 6.3 (ch6_fig_unity.png): frames 114 and 700 of the rail
  recording seen from the virtual sensor, recaptured from the recovery
  stream (commit b63b262). Chapter 7's only qualitative figure is the
  reprojected skeleton on a loop frame (Figure 7.10).
- Action: a Unity strip at the stations of C30 (grasp, top of the
  lift, mid-slide, release), each beside the colour frame of C33, so
  the reader sees the scene and the reconstruction of the same moment.
  Either move Figure 6.3 here and leave Chapter 6 with the
  architecture and frame figures, or add new captures (Unity captures
  must use eval/output/recovery_r6b/angles_recovery.csv per
  skill_set/evaluation-scenario-separation.md). The UnityMCP server
  was not reachable this session, so new captures are a user step.
- Status: PARTIAL (captures exist in Chapter 6, none in Chapter 7).

## C38. Error precision: no e-13, millimetres are enough
"Also, if you want to talk about the error, you doing need to go
e-13. In engineering or in our case of precision, if you have units in
mm, that should be fine since the system can not measure that
precise."
- Target: 7.1.2 and every number finer than the sensor.
- Current (verified, build_ch7.py): Table 7.1 lists six worst
  decoding errors as 1.1e-13, 8.5e-14, 2.0e-13, 8.5e-14, 2.8e-13,
  2.6e-13 degrees; the prose says "2.8 times 10 to the power of minus
  13 degrees, which is the size of floating-point rounding"; the rail
  solver check says "to within 1.21 millionths of a degree". Beyond
  7.1.2, position errors are quoted in centimetres with two decimals
  (52 occurrences, e.g. 0.79, 9.32, 13.11, 0.48, 2.83 cm), which is
  0.1 mm precision, and angles with two decimals (11 occurrences, e.g.
  -30.83, 53.92, 8.86 degrees). The chapter also states, in 7.1.3 and
  the Table 7.3 prose, several sub-centimetre comparisons.
- Action: in 7.1.2 replace Table 7.1 and the exponent prose with one
  statement: the solver reproduces the injected angles exactly to
  floating-point precision (below 0.001 degree) on all six synthetic
  sets, and on the rail recording below 0.001 degree; keep the
  anatomical-range check. Elsewhere round every position to
  millimetres (one decimal in centimetres, or whole millimetres) and
  every angle to 0.1 degree, in tables and prose alike; the abstract
  and Chapter 9 quote the same numbers and follow. Candidate rule for
  skill_set: report no finer than the sensor resolves (mm, 0.1 deg).
- Status: OPEN.

## C39. Figures 7.4 and 7.5 are good
"I like figure 7.4 and 7.5. it also relates to the previous chapters
of your estimation."
- Target: none.
- Current (verified): Figure 7.4 (ch7_fig_failures_rail.png,
  make_ch7_rail_failures_fig.py) is the detector failure timeline of
  the rail recording; Figure 7.5 (ch7_fig_failures.png,
  make_ch7_figs.py) is the same for the loop recording.
- Action: keep both in the trimmed chapter. Note that Figure 7.5 is on
  the loop recording; if the loop is dropped (C34) it goes with it,
  and only Figure 7.4 remains. Tell him this in the reply so his "keep"
  and his "drop the wire" do not collide silently.
- Status: DONE (no change needed; dependency on C34 flagged).

## C40. Earlier block experiments not needed
"Is not needed if you show the earlier experiments of moving the
object along the block."
- Target: any earlier-experiment material in Chapter 7.
- Current (verified): Chapter 7 contains no block-sliding experiment
  from earlier versions. The earlier experiment it still carries is the
  loop recording (wire, eight stations). Read with C34, the loop is
  what he means by earlier experiments.
- Action: same as C34; nothing further.
- Status: DONE for earlier-version material (none present); OPEN as
  part of C34.

## C41. Sample calculations and error sources elsewhere; overall results here
"when you show the trajectory of the wrist through your kinematic
model, this will capture the overall accuracy. But, when you talk about
the kinematic of torso individually and then the arms, you should show
some sample calculation and talk about the sources of error. In this
chapter, just show the overall results of bi-manual operation."
- Target: Chapter 7 structure; Chapters 3 and 9 for the per-part
  material.
- Current (verified): Chapter 7 has per-part sections: 7.1.2 solver
  check, 7.3 pose recovery by method and window (Tables 7.4-7.7), 7.4
  torso stability (Figure 7.9, Tables 7.8, the rail trunk-pitch
  paragraphs and the synthetic-corruption check). Chapter 3 already has
  a worked example (3.5) on frame 533 with the numeric T matrices
  (C20), and the torso frame derivation (3.2). No section of Chapter 3
  or Chapter 9 lists the sources of error per part; Chapter 9 has a
  limitations table.
- Action: trim Chapter 7 to the overall results (outline below). Move
  the torso-stability material (7.4) and the per-method recovery
  tables (7.3.1 and, if kept, 7.3.2) to a parked file, and add to
  Chapter 3 (end of 3.2 and 3.4, or the worked example) a short
  sources-of-error passage per part: torso (hip depth taken at the
  desk or rail edge, the 24 vs 8 degree trunk figures now in 7.4),
  shoulder and elbow (landmark depth noise, the near-straight-arm
  conditioning already stated in Chapter 5 5.4). Whether the
  recovery-under-masking numbers (Table 7.4) survive as a short
  paragraph is for the user to decide, since they are the only
  quantitative evidence for Chapter 5.
- Decision needed (user): how much of 7.3 and 7.4 to keep. The
  supervisor's "just show the main experimental results" argues for a
  short 7.3 paragraph with the Table 7.4 headline and no 7.4.
- Status: OPEN.

## C42. His closing question
"I think jus show the main experimental results I have talked about in
the above combined with the Unity reconstruction. That should be
enough I think. What do you think?"
- Target: the user's reply.
- Action: the user answers. Suggested reply, in the user's voice, a
  suggestion only:
  "I agree. I will cut Chapter 7 down to the task schematics, the
  object trajectory against the rail line, the wrist trajectory from
  the kinematic model in the same world frame, the combined plot, and
  the Unity reconstruction at the same moments, and drop the wire
  experiment. One thing to confirm: the recording I have is
  one-handed (the cube goes along the desk and the rail in one hand,
  no handover). If you want the handover in the results I need to
  record the task again with both hands, which I can do this week."
- Status: user reply needed.

## Proposed Chapter 7 outline under the supervisor's direction

1. 7.1 The Task and the Recording. (a) Protocol schematic: grasp,
   carry to the rail, slide, release (C31), drawn first. (b) Object
   stations with the marker origin and the world frame (C30). (c) Rail
   dimensions (current Figure 7.2). (d) Colour-frame strip of the
   grasp, lift, slide, release (C33). Handover panels only after the
   C31 decision. Keep the marker-scale paragraph (45 mm).
2. 7.2 Detector Failures on the Recording. Figure 7.4 kept (C39), with
   the two or three sentences that read it. Figure 7.5 and Table 7.2 go
   with the loop (C34).
3. 7.3 Object Trajectory in the World Frame. The mapping paragraph
   (C32), then current Figure 7.6 and its numbers rounded to
   millimetres (C38). Figure 7.7, Table 7.3 and the loop comparison
   are cut (C34).
4. 7.4 Wrist Trajectory Through the Kinematic Model. New figure and
   numbers (C35), both wrists, same frame as 7.3, offset to the rail
   line read against the hand-object offset of Chapter 5.
5. 7.5 Combined View. Rail line, cube centre, both wrists on one axis
   set in one unit (C36).
6. 7.6 Unity Reconstruction. Colour frame beside the Unity view at the
   stations of 7.1 (C37); the trails-in-Unity variant if he confirms
   reading (b) of C36.
7. 7.7 Solver Check, short. One statement that the solver is exact to
   floating-point precision on the synthetic sets and the rail frames,
   plus the anatomical-range check (C38); Table 7.1 removed.

Cut or parked (to writing/v7/CH7_PARKED.md, verbatim, with the source
section, precedent CH6_PARKED.md): Figure 7.3 and the loop paragraph
of 7.1.1; Figure 7.5, Table 7.2 and the loop failure prose; Figure 7.7,
Table 7.3 and the loop trajectory prose; 7.3.2 whole (Table 7.5,
Figure 7.8, Table 7.6); 7.3.3 whole (Table 7.7 and the label
protocol); 7.4 whole (Figure 7.9, Table 7.8, the rail trunk paragraphs,
the synthetic-corruption check); Figure 7.10. Of these, the rail parts
of 7.3.1 (Table 7.4) and 7.4 are candidates to return as one short
paragraph each if the user wants Chapter 5's evidence to stay in the
thesis (C41 decision). The sources-of-error passages move to Chapter 3.

Possible now, before any user decision: the reorder of 7.1.1 (C31,
second half), the one-handed protocol schematic and the station
schematic (C30, C31), the colour-frame strip without a handover panel
(C33), the mapping paragraph (C32), the wrist trajectory script and
figure (C35), the combined figure (C36 reading a), the precision pass
(C38), the Chapter 6 Unity captures reused in Chapter 7 (C37, partial).
Blocked on decisions: the handover panels and any re-recording (C31,
C33), dropping the loop (C34, C40, and with it Figure 7.5 of C39), how
much of 7.3 and 7.4 survives (C41), the Unity trails variant (C36
reading b), new Unity captures (C37, server unreachable).

# Chapter 2 block (C43-C47)

## C43. Rename Section 2.4 and say where the filtering goes next
"You should mention how the signal filtering of this chapter (section
2.4 (I think you should call it measurement filtering or something
like this)."
(The sentence is cut off in his message. The intent is inferred: most
plausibly, say how the filtered signals of Section 2.4 feed the later
chapters, and rename the section.)
- Target: Section 2.4 heading and its closing paragraph.
- Current (verified in build_ch2.py, "2.4 Signal Filtering"): the
  heading is "Signal Filtering". The section already carries three
  onward links, but scattered: the gap paragraph says gaps longer than
  five frames go to the pose recovery of Chapter 5; the smoothing
  paragraph says Chapter 8 measures the causal One Euro filter against
  the offline Butterworth; the closing paragraph says the unfiltered
  baseline is kept for Chapter 7 and that the object track is cleaned
  by its own stage in Chapter 4. Nothing says that the filtered
  landmarks are the input of the Chapter 3 solve, and no single
  sentence states the onward path in one place.
- Action: (1) retitle the section "2.4 Measurement Filtering" (and
  update the two references to it in the chapter opening and the
  Figure 2.3 data-flow caption if they name it); (2) add one closing
  sentence pair: the filtered landmarks are the measurements Chapter 3
  solves the joint angles from, and the filtered object track of
  Chapter 4 is the object pose Chapter 5 recovers a held wrist from;
  (3) keep the existing Chapter 5/7/8 links as they are. This section
  is the user's own verbatim text (commit 669cff0), so the edit is a
  find/replace list, not a rewrite.
- Status: DONE (2026-09-05, in writing/v8; see PROF_COMMENTS_CHECKLIST.md).

## C44. AI for clarity, but the user's level of English and vocabulary
"I also think you should use AI again for clarity BUT keeping your
level of English and vocabulary."
- Target: the whole of Chapter 2.
- Current (verified: git log on scripts/build_ch2.py; commit 669cff0
  "Ch2 rewritten on the user's text: 2.1 on the user's outline,
  2.2-2.4 verbatim"): Sections 2.2-2.4 are the user's own sentences;
  2.1 was drafted on the user's outline. So the comment is on the
  user's own prose, and it matches the user's stated workflow (AI
  drafts, the user flattens sentence structure and replaces complex
  words).
- Action: a light clarity pass delivered as a find/replace edit list
  (skill_set/manual-edit-change-lists.md): split run-on sentences,
  fix connectives, no new vocabulary above the user's level, no new
  terms, no paragraph rewrites. The same instruction applies to
  Chapters 5 and 7 (C22) and becomes a standing rule for every
  chapter.
- Status: DONE (2026-09-05, in writing/v8; see PROF_COMMENTS_CHECKLIST.md).

## C45. Overall picture of the scene with the coordinate frames drawn
"Also, what is missing is the overall picture of the subject, the
table, the markers and the wall. You need to draw the main coordinates
involves in your setup. ... For example, draw a frame on each of the
Aruco markers. Draw the World frame on the wall aruco marker. Show the
sensor frame. Then draw arrows between the frame corresponding the T
matrices and so on."
- Target: Section 2.1, a new figure right after the setup photographs
  (Figures 2.1 and 2.2), before the data-flow figure.
- Current (verified): Chapter 2 has no frame drawing. Figure 2.1 is
  the working area on grid paper plus the scene from behind the
  camera; Figure 2.2 labels the parts of the scene in a colour frame
  (participant, rail, cube, wall/desk/object markers) with no axes
  drawn (make_ch2_setup_fig.py labels the markers, and its label for
  the desk marker already reads "world anchor"). The frames exist only
  later: Chapter 3 Figure 3.2 draws the camera frame C on a photo of
  the sensor and Figure 3.3 draws C against person space P; Chapter 4
  Figure 4.2 (make_ch4_figs.py, draw_axes projects a T through the
  colour intrinsics onto the worked-example frame) draws camera C,
  world W and object O, and no figure anywhere draws the wall marker's
  frame or the arrows for the T matrices.
- World-frame anchor, verified: in the current thesis the WORLD ORIGIN
  IS THE DESK MARKER (ID 2), not the wall marker. Table 2.1 lists the
  desk marker as "Static; world origin" and the wall marker (ID 0,
  150 mm) as "Static; gravity reference"; Section 4.1 says the desk
  marker anchors the world frame and the wall marker, on a plumb wall
  behind the working area, supplies the gravity direction (its in-plane
  up axis), with the sign fixed by the depth plane; Table 4.1 lists the
  wall marker pose "in the world" as a derived quantity carried through
  the inverse anchor; Section 4.2 names the desk marker's frame as the
  world frame W. The supervisor's instruction "Draw the World frame on
  the wall aruco marker" contradicts this.
- Decision needed (user): either (a) keep the desk marker as the world
  origin and say so plainly to the supervisor in the reply and in the
  new figure (the desk marker sits on the tabletop at the working
  area, so heights and the object path read directly against it; the
  wall marker is far behind the area and only levels the frame), or
  (b) move the world origin to the wall marker as he expects, which
  changes the calibration of Section 4.1, every world-frame plot in
  Chapters 4 and 7, the Unity scene of Chapter 6 and the headline
  numbers. Recommendation: (a); the figure can then draw both static
  markers with their frames and label which one is the world origin.
- Action: new figure "The scene and its coordinate frames" on the
  colour frame of Figure 2.2 (natural base: the draw_axes/project
  helpers of make_ch4_figs.py applied to the calibrated poses, moved
  or copied into a new make_ch2_frames_fig.py): the sensor frame C at
  the camera, a frame on each of the three markers (wall, desk = world
  frame W, object O), the participant's root frame optional, and
  arrows between the frames labelled with the T matrices of C46. The
  photo view cannot show the camera's own axes in the image, so a
  schematic top view (camera, desk, wall, participant) as panel (b)
  may be the clearer form; both panels from one script.
- Status: DONE (2026-09-05, in writing/v8; see PROF_COMMENTS_CHECKLIST.md).

## C46. Calibration section and the frame/T-matrix notation in Chapter 2
"Also, include the calibration section here as well. Define the
coordinate frames here and the overall T matrices between the frame
(just the notation). Just like Chapter 2 of your robotics book."
- Target: a new section in Chapter 2 (proposed "2.5 Coordinate Frames
  and Scene Calibration", or placed as 2.2 before the sensing sections
  so the frames are defined before any measurement is reported).
- Current (verified): Chapter 2 contains no calibration and no frame
  definitions; the word "calibration" does not occur in build_ch2.py.
  The material lives in three places: Chapter 3 Section 3.1 defines
  the camera frame C, person space P (the y flip, equation (3.1)), the
  homogeneous T (equation (3.2)) and the body chain T_root, T_sh, T_el
  (equations (3.5)-(3.6), added for C15-C17 of round 3); Chapter 4
  Section 4.1 is the static scene calibration (chordal-mean anchor of
  the desk marker, wall marker gravity direction, tabletop plane,
  Table 4.1 of the frozen quantities, Figure 4.1) and Section 4.2
  defines the scene frames C, W, O with T_CW, T_CO and the chain
  T_WO = T_CW^-1 T_CO (equation (4.2), Figure 4.2).
- Action (notation only in Chapter 2, derivations stay where they
  are): the new section names every frame of the thesis in one list
  with one symbol each (sensor/camera C, world W at the desk marker,
  wall marker frame, object frame O, person space P, root/torso frame
  and the arm frames of Chapter 3, Unity frame of Chapter 6), writes
  the T matrices between them as symbols only (T_CW, T_C,wall, T_CO,
  T_WO, T_PC or the flip F, T_root, T_sh, T_el) with one sentence each
  on what is fixed by calibration and what is measured per frame, and
  states the calibration in two or three sentences (static markers
  measured over the first ten detections and frozen; wall marker gives
  gravity; tabletop plane from depth) with a forward reference to
  Section 4.1 for the method. Chapter 3 Section 3.1 and Chapter 4
  Sections 4.1-4.2 then open with a back-reference to the Chapter 2
  notation instead of re-introducing the frames; equations (3.2) and
  (4.2) stay. Precedent: round 3 C15-C19 (T matrices shown wherever R
  and t appear) and C21 (Figure 3.1 information flow at the chapter
  start); the supervisor's "Chapter 2 of your robotics book" is the
  standard frames-and-transformations chapter, so the section is a
  frame list plus a figure, not a derivation. Figure 2.3 (data flow)
  should gain the calibration block if the section is placed after it.
- Status: DONE (2026-09-05, in writing/v8; see PROF_COMMENTS_CHECKLIST.md).

## C47. Verdict
"Good job"
- Action: none.
- Status: DONE (no action).

# Decisions for the user (round 4)

Only the user can settle these; each blocks the items named.

Chapter 5
- D1. Section 5.5 torso repair versus the planned "torso always
  measured" assumption: park it (CH6_PARKED.md precedent) or shrink it
  to a note. Touches 5.1, 5.6, 7.4 and the Chapter 9 row.
- D2. If 5.5 goes, where the rail recording's hip-depth offset (E-027:
  hips at the rail's depth, trunk 24-32 deg from upright) is absorbed:
  a Chapter 2 filtering step, or a Chapter 9 limitation. Changes the
  Chapter 7 arm-angle numbers.
- D3. The manual-label set (7.3.3) is defined on the loop recording;
  it must be redefined on the rail recording's own drift frames.
- D4. Whether the two torso detectors of Table 5.1 stay.
- D5. One-handed rail task versus the bimanual wording of Chapter 1
  and the Chapter 5 opening (same as C31).

Chapter 7
- D6. Re-record the rail task two-handed with a handover as the
  supervisor describes, or keep the one-handed recording and tell him
  (C31, C33, and the Chapter 1 wording).
- D7. Drop the loop recording entirely, or keep it only for the
  manual-label occlusion evaluation (C34, C40; Figure 7.5 of C39 goes
  with it).
- D8. How much of 7.3 (Table 7.4) and 7.4 survives as short paragraphs
  versus parked (C41).
- D9. "In the same Unity": same units in one combined figure, or the
  trails drawn inside the Unity scene (C36). SETTLED 2026-09-07 by the
  user ("do it if you can"): both, Figures 7.8 and 7.10.
- D10. His closing question needs a reply; a suggested two-sentence
  reply is under C42.

Chapter 2
- D11. World-frame anchor: the thesis puts the world origin on the
  desk marker and uses the wall marker only for gravity; the
  supervisor expects the world frame on the wall marker. Recommended:
  keep the desk marker and say so in the reply and the new figure,
  since moving it recalibrates Section 4.1, every world-frame plot in
  Chapters 4 and 7, the Unity scene and the headline numbers.
- D12. Where the new frames-and-calibration section sits in Chapter 2:
  before the sensing sections (recommended, so the frames exist when
  the measurements are named) or after them as 2.5.

Possible before any decision: the Chapter 5 variable audit and
parameters table (C24, C28), the eq. 5.1/5.2 schematic (C23), the
Chapter 5 opening pipeline figure (C27), the Chapter 7 reorder and
one-handed schematics (C30, C31), the mapping paragraph (C32), the
wrist-trajectory script and figure (C35), the combined figure (C36a),
the precision pass (C38), the Chapter 2 rename and link sentences
(C43), and the Chapter 2 frames figure drafted on the desk-marker
origin (C45, C46).

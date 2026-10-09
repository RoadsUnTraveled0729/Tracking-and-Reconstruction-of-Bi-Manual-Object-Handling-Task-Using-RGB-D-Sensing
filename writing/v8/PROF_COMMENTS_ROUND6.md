# V8 supervisor comments, round of 2026-09-08 (Chapter 7)

Relayed by the user on 2026-09-08 after the trajectory-figure revision
("It looks good. Just one comment."). Numbering continues from
PROF_COMMENTS_ROUND5.md (C48-C49).

## C50. Add the second arm to the wooden block (rail) experiment
"Can you add the second arm in the wooden block experiment. I mean,
one arm slide the object half way and then the other arm grasp the
object half way and continue. Even if it is filled with error, you
should show them. If it can not be done, then forget it. We use the
later results you have presented. I just want to show the results as
closely related to the theme of your thesis and its title."
- Target: Chapter 7. The title is "Tracking and Reconstruction of
  Bi-Manual Object Handling Task ..."; the rail recording is
  one-handed, and the only two-hand evidence is the loop recording in
  Section 7.7.
- Current (verified 2026-09-08): no existing take has a two-hand
  slide on the rail. The two rail takes of 2026-08-31 are one-handed
  (recording_20260831_065553 is the thesis recording; 065504 was
  rejected on the A6 precondition). The loop recording
  (recording_20260825_222315) has a hand-to-hand pass but no rail.
  The pipeline already handles both arms: detect_failures, grip_state
  (hand-over as two overlapping holding states), fit_offset per hand,
  run_recovery and the Unity rig all ran per side on the loop
  recording; eval_rail_scenario.py scores the object marker against
  the rail line and does not depend on the hand. The D435 is attached
  to the workstation and responds (rs-enumerate-devices).
- Decision (user, 2026-09-08): record a NEW take of the whole rail
  task with the hand-over midway along the rail, and add it to
  Chapter 7 as a second recording. The one-hand recording stays the
  thesis recording in every other chapter; the other chapters change
  only where they say the rail task is one-handed (Chapter 1 scope
  sentence and objective 5, Chapter 2 Section 2.1, Chapter 7 opening
  and Section 7.1, one sentence in Chapter 9, and the abstract if
  wanted). Replacing the primary recording was offered and advised
  against (it would redo the worked examples and figures of Chapters
  2 to 6).
- Plan: (1) the user records the take at the workstation on the
  protocol in eval/RECORDING_R7_HANDOVER.md and runs the precondition
  check; (2) register the stem (alias r7) in eval/common/paths.py and
  run the pinned chain of eval/README.md; (3) hand-over analysis:
  which hand holds on each frame from the grip state machine, the
  hand-over interval, object-to-rail error per half, both wrists
  through the kinematic model, the failure mask; (4) figures: frames
  around the hand-over, the object track along the rail coloured by
  hand, both wrist trajectories, one Unity still at the hand-over
  (trail view extended to the left wrist); (5) new Section "Hand-over
  on the Rail" between the Unity section and the recovery section,
  errors reported as they come out; (6) review loop, code review,
  validation, rebuild, change log, checklist, decisions, handover,
  commit and push.
- Status: DONE (2026-09-09). The user recorded eight takes on the
  night of 2026-09-08/09 and named the last, recording_20260909_000024
  (alias r7, 1499 frames, 50 s), as the one to use. Every landmark
  passes the precondition check (right wrist 99.3 percent, the rest
  100). The wall card had shifted, so the calibration carries the
  gravity of the Chapter 2 recording (E-034). New Section 7.7 "Handover
  on the Rail" (Figures 7.11 to 7.13, Table 7.1; D-021): the right
  hand slides the cube 29.7 cm, both hands hold it for 5.3 s at 29 to
  35 cm along the slide, the left hand slides the last 7.8 cm; the
  marker origin stays within 1.7 cm of the fitted line during the
  handover (whole slide median 0.3, p95 1.6, max 3.4 cm); the torso
  detector fires on 326 frames while the hands cover the hips and the
  preparation of Section 2.6 replaces both hips on 417 frames; both
  arms measured through the handover; the model wrist jumps by up to
  23 cm at the three torso transitions (reported as they are). The
  sentences calling the rail task one-handed changed in Chapters 1, 2,
  7 and 9 and the abstract. The user's hip-freeze idea of the same
  message is implemented as an opt-in and measured (E-034), not
  adopted; Section 7.7 and Section 9.2 state it.

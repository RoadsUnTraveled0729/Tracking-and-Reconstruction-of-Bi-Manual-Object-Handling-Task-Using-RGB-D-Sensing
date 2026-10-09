# Current pointer (2026-10-08)

The R5 round and its dated results below are historical. V9 is delivered
and defended, with post-defence revisions in
[writing/v9](../writing/v9/README.md). The printed desk/object black
squares are confirmed 45 mm; the frozen detector declares 0.050 m and
the thesis chain applies a 0.9 translation scale before calibration
([AGENTS.md](../AGENTS.md)). E-009a ruler measurement is closed. The
V7 rewrite and measurement tasks described below are superseded; the
completed manual-label results remain the recorded evidence.

## Historical R5 state
# R5 experiment round: FROZEN 2026-08-26, UNFROZEN 2026-08-28 for E-022 (object-track filter gap hold fixed; chain re-run)

User decision 2026-08-26: "the experiment is good for now, freeze
it." The R5 evaluation round is complete and committed; the next
round is the thesis rewrite, starting from the TOC (free
restructure allowed; only after this freeze, per the user's
staging).

## What is frozen (all committed on master, pushed)

- Primary recording: R5 = recording_20260825_222315 (70 s, 2099
  frames; Video/, gitignored). R4/R1 artifacts remain for
  reproducibility and threshold cross-checks.
- Failure study (E-015): detectors D1-D6, events, thresholds
  plot-first with R1 zero-fire; reports r5_failure_mask.md,
  r5_failure_events.csv.
- Object-conditioned pose recovery (E-014/a/b; reports REGENERATED 2026-08-28 against committed code, E-021: 3 synthetic windows not 4): solver-layer wrist
  from object + two-link IK elbow, time-local grip offsets, grip
  state machine, plausibility bounds; the mathematics deliverable is
  eval/reports/r5_object_conditioned_recovery.md; synthetic
  evaluation r5_recovery_synthetic.md + r5_recovery_moving.md
  (moving outage: recovered wrist 1.6 cm median vs hold 21 cm max).
- Torso ray repair + consensus depth-jump gate (E-011b): worst
  window root yaw 49 -> 15 deg, pelvis depth wander 22 -> 0.5 cm.
  validate_occlusion_ext.py: 39 checks all passing.
- Object track cleaning (E-019, the ONLY marker-side mechanism per marker-simplicity.md; CAUSE CORRECTED 2026-08-28, see E-022: the handover swing is the filter gap hold, not a bad decode; filter fix is an open user decision) (per
  marker-simplicity.md): eval/common/clean_object_track.py.
- 8-waypoint trajectory evaluation (E-017a): point-to-path median
  0.80 cm / p95 9.32 cm; one-glance 3D figure r5_waypoints.png;
  spec eval/gt/labeled_path_r5.json.
- Unity-vs-video check (internal, NOT thesis): autonomous editor
  capture, exact frame pairing, display smoother (E-018), rig
  corrections (spawn T-pose alignment, subject proportions); wrist
  within 4.3 cm at a raised-hold pose; r5_unity_check.md.
- All decisions logged E-001..E-019 in eval/DECISIONS.md; per-track
  commands in eval/README.md (stem-generic chain for any new
  recording).

## Open items carried into the thesis round

- Marker size 45 mm is still a USER ASSUMPTION (E-009a); a ruler
  measurement of the printed black squares would settle it.
- A6 precondition on R5: torso PASS, left hand FAIL (7.0 s gap),
  right elbow gap 2.3 s - the failure windows are the recovery's
  subject, but accuracy-evaluation windows must respect E-013
  (synthetic masking only).
- Thesis: writing/v7 has only the English TOC (sent for sign-off,
  now superseded by the user's free-restructure decision) and a
  Chinese Chapter 1. The rewrite drops the "Data Integrity"
  organizing rule entirely (plain statement style, simple words,
  values + analysis; see readability-first.md and
  thesis-statement-style.md), and all evaluation numbers come from
  the frozen R5 reports above.

## Recovery verification by manual labels (user direction 2026-08-26, restated 2026-08-28)

The synthetic-masking evaluation (E-013) grades the recovery on stand-in
frames. The frames that matter are the NATURAL failure windows, so the
recovered wrist is verified against manual labels there: the user clicks
the wrist on failure-window frames that fall inside a grip episode
(every 5th frame), the aligned depth map gives the third coordinate,
and the recovered wrist is compared with the deprojected label.
Pipeline: eval/failure/extract_label_frames.py [--stem] (selects and extracts
frames + depth + intrinsics to eval/output/label_frames_<alias>/; copies
tracked in eval/labels/frames_r5 and frames_r6b since 2026-09-06 so the
labelling can happen on the user's Mac) ->
eval/failure/label_wrists.py (click tool, writes labels json) ->
eval/failure/eval_labeled_recovery.py (error per frame, report
eval/reports/r5_recovery_labeled.md). Thesis home: Chapter 7, a
subsection "Recovery Accuracy on Labeled Natural Failure Windows"
next to the synthetic-masking section. E-013 is amended: natural
windows are evaluated quantitatively where labels exist.

Status 2026-09-06: DONE. The user placed every label (rail: 21 failure
frames plus 5 clean, cuff-seam convention; loop: 20 failure frames plus
7 clean, wrist-jewellery convention, 58 skipped where the cube hides
the mark). Graded by eval_labeled_recovery.py into
eval/reports/r6b_recovery_labeled.md and r5_recovery_labeled.md. The
condensed thesis reports them in Section 7.3.3 (Tables 7.7 and 7.8),
Section 7.5 (frames 1462 and 1890), the Chapter 5 closing and Chapter 9
(decision D3 closed). Reading: rail gap at the reference floor for every
method; loop right window recovery 5.22 cm against 11.38 plain; loop
left window no better than the baselines because the frozen grip offset
was already off (estimator lag, non-rigid grip).

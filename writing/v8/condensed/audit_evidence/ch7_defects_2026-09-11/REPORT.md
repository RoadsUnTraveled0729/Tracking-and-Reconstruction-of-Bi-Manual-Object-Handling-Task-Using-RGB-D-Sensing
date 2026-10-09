# Chapter 7 defect list of 2026-09-11: verification and change log

Scope. The author's Chapter 7 defect list, Parts A and B, processed
against the rebuilt chapter of this morning (the structure of
REVISION_2026-09-11_BRIEF.md section 4, the rebuild recorded in
writing/v8/condensed/notes_revision_ch7.md). Edited file:
writing/v8/condensed/scripts/build_ch7.py only. Outputs:
writing/v8/condensed/Chapter_7_Evaluation.docx (the tracked chapter,
rebuilt) and Chapter_7_Evaluation_revised.docx in this folder. Nothing
was committed. No number printed in the chapter was changed by this
pass.

Section mapping used throughout (the author's list was written against
the previous numbering):

| author's section | current section |
|---|---|
| 7.2 tracking failures | closing passage of 7.1 |
| 7.4 wrist trajectory, 7.5 object/wrist/rail | first half of 7.3 |
| 7.7 handover | second half of 7.3 |
| 7.8 recovery on the failure windows | 7.4, split into 7.4.1 and 7.4.2 |
| 7.9 solver check | 7.5 |

## 1. Part A verification

| item | conflicting values | source-data value | recommended fix | confidence |
|---|---|---|---|---|
| A1 right-wrist gap extent | 7.1 (old 7.2): frames 550 to 639, 3.0 s. Old 7.8: "the 21 frames from 550 to 684". Chapter 5: "about three seconds" from frame 550. 684 would imply 134 frames, 4.5 s | Two separate right-arm rejected runs, both acquisition (d1_R): 550 to 639, 90 frames, 3.002 s; and 674 to 684, 11 frames, 0.367 s. A third run, 7 to 24, 18 frames, 0.601 s, sits at the start of the recording. The three sum to 119 frames, the 13.3 percent of the 895-frame span. The label rule selected 21 frames: 550, 555, ... 635 (18 samples at five-frame spacing, inside the 550 to 639 run) plus 674, 679 and 684 (inside the 674 to 684 run) | No number is wrong. The chapter's numbers already agree with the data after this morning's rebuild replaced the "550 to 684" sentence. Both windows are now named in 7.1 as well, so the label set of 7.4.2 can be reconciled from 7.1. Chapter 5's "about three seconds" describes the 550 to 639 run and is correct. The stale wording lives on in eval/labels/README.md ("21 frames, right wrist only: frames 550 to 684 every fifth frame", which would be 27 frames): a data file, not edited here, reported for the author | High |
| A2 hip repair frame count | 7.3 (old 7.7): "those 417 frames" for frames 644 to 1060. A passage elsewhere gave 419 | 644 to 1060 inclusive is 417 frames. eval/reports/r7_hip_hold.md states both counts and they describe different sets: "frames with a replaced hip: 417; frames where any of the thirteen angles differs by more than 0.05 deg between the policies: 419". The same file lists "root tagged constrained: ray 417, hold 417 frames" and the replaced run [[644, 1060]] | 7.3 is right and needs no change. The 419 was the Chapter 9 sentence "it would change the root on 419 of the 1499 frames of the handover recording" (writing/v8/CH9_SPLIT_TEXT_CHANGES.md item 18, writing/v8/CH7_HANDOVER_TEXT_CHANGES.md item 6), and the Chapter 9 revision already cut it: no built chapter now prints 419 (dump of all 13 docx files, no hit). If any writer restores that sentence, it must say what the 419 counts, the frames on which the two policies differ by more than 0.05 degrees in any of the thirteen angles, not the repaired frames | High |
| A3 handover slide distances | Prose of old 7.7: right hand to 29.7 cm, both hands to 34.5, left hand to 42.4. Table 7.1 Travel column: 29.7, 5.3, 7.8. 29.7 + 5.3 = 35.0, not 34.5; the three sum to 42.8, not 42.4 | Travel is a per-part EXTENT along the fitted line, not a cumulative increment. Recomputed over the along_cm column of eval/reports/r7_handover.csv: right part 0.00 to 29.65 cm (extent 29.65), handover part 29.23 to 34.48 (5.25), left part 34.58 to 42.41 (7.83), all slide samples 0.00 to 42.41 (42.41). The parts overlap by 0.43 cm, because the cube slides back at the transfer, and there is a 0.10 cm gap between the handover and the left part, so the three extents sum to 42.74 and not 42.41. The report's own per-part table gives the same spans, 0.0 to 29.7, 29.2 to 34.5, 34.6 to 42.4 | Fix the column definition, not the numbers. The Table 7.1 caption now says that Travel is that part's own extent and not a cumulative position, and that the cube slides back 0.4 centimetres at the transfer, so the parts overlap and the three extents do not sum to the 42.4 centimetre slide. The prose the author quoted no longer exists: the rebuild replaced it with "the transfer takes place 29 to 35 centimetres along the 42.4 centimetre slide", which are along-line positions and are consistent with the CSV | High |
| A4 label counts 78 to 20 | 7.4.2 (old 7.8): the rule yields 78 candidate frames on the loop recording, 54 left and 24 right. Table 7.3: 16 left and 4 right, 20 failure labels. 58 candidates unreconciled | Counted from eval/labels/frames_r5/meta.json against frames_r5/labels.json: 78 non-clean candidates, 54 left and 24 right; 20 carry a label, left 1427 to 1492 at five-frame spacing plus 1777 and 1787 (16), right 1775, 1880, 1885, 1890 (4); 58 carry none, left 1497 to 1667 at five-frame spacing plus 1782, 1792 and 1797 (38), right 1780 to 1875 at five-frame spacing (20). The rail set has no discard: all 21 failure frames and all 5 clean frames are labelled. Discard reason: the tool writes a skip as a null entry with no reason field (eval/failure/label_wrists.py, key "s"), so no per-frame reason exists in the data. The only documented reason is full occlusion of the mark: eval/labels/README.md, "Skip (s) only where the cube hides the jewellery completely", and HANDOVER.md, "58 skips where the cube hides the jewellery" | Counts confirmed, no number changed. 7.4.2 now states the discard explicitly, 58 of the 78 loop candidates, 38 left and 20 right, and names the selection effect as a third limit of the reference (B6). That occlusion was the sole reason is supported by the labelling protocol and the handover note but is not recorded frame by frame, so the report states it as the documented reason rather than as a verified per-frame fact | High on the counts, medium on "occlusion was the sole reason" |

Evidence files and lines.

- A1: eval/reports/r6b_failure_mask.md, the "Event table" section, rows
  "7 | 24 | 0.601 | 18 | arm_R", "550 | 639 | 3.002 | 90 | arm_R" and
  "674 | 684 | 0.367 | 11 | arm_R"; the same three rows in
  eval/reports/r6b_failure_events.csv lines 3, 6 and 9; the
  "Acquisition-only events" list of the same report ("arm_R 550-639
  (3.00 s)", "arm_R 674-684 (0.37 s)"); the detector fire counts table
  ("d1_R | 111 | 12.4") and the combined mask table ("fail_arm_R | 119 |
  13.3 | 3 events"). Label frames: eval/reports/r6b_recovery_labeled.json,
  the 21 rows with group "failure" (550 to 635 at five-frame spacing,
  674, 679, 684) and the 5 rows with group "clean" (500, 520, 540, 700,
  720); eval/labels/frames_r6b/meta.json "frames" and "clean_frames".
  Chapter 5: writing/v8/condensed/scripts/build_ch5.py line 462, "From
  frame 550 the landmark detector stops reporting a usable right wrist
  for about three seconds". Stale wording: eval/labels/README.md, the
  frames_r6b bullet.
- A2: eval/reports/r7_hip_hold.md line 24 (both counts in one line) and
  the section heading "## Frames 644-1060 (417 frames)"; the same file's
  "root tagged constrained: ray 417, hold 417 frames";
  eval/reports/r7_handover.md, "torso replaced (root constrained) runs:
  [[644, 1060]]"; eval/DECISIONS.md E-034 ("the ray repair holds both
  hips through 1060 ... root constrained 417 frames"). The 419 in the
  drafts: writing/v8/CH9_SPLIT_TEXT_CHANGES.md line 96,
  writing/v8/CH7_HANDOVER_TEXT_CHANGES.md line 191,
  writing/v8/condensed/notes_revision_ch9.md lines 136 and 294. No hit
  for 419 in any built chapter or in any builder.
- A3: eval/reports/r7_handover.csv, the along_cm and perp_cm columns
  over the rows whose part column is right, handover or left (1073 rows,
  frames 426 to 1498; frame 741 has no along_cm, the one undetected
  object frame); eval/reports/r7_handover.md, the per-part table rows
  "right | 426-863 | 438 | 0.0 to 29.7 | 29.7", "handover | 864-1022 |
  159 | 29.2 to 34.5 | 5.3", "left | 1023-1498 | 476 | 34.6 to 42.4 |
  7.8" and the headline "slide frames 426-1498 (1072 frames), extent
  42.4 cm"; eval/DECISIONS.md E-034, "parts: right 426-863 travel 29.7
  cm ... handover 864-1022 5.3 cm ... left 1023-1498 7.8 cm".
- A4: eval/labels/frames_r5/meta.json ("frames", 85 entries, and
  "clean_frames", 7 entries) against eval/labels/frames_r5/labels.json
  (85 entries, 27 with a point and 58 with a null side);
  eval/reports/r5_recovery_labeled.md, the line "Labels: 20 wrists
  clicked by the user on natural failure-window frames inside grip
  episodes and 7 on clean frames"; eval/labels/README.md, the frames_r5
  bullet and the "Where to click" paragraph; HANDOVER.md, the "LABELS
  DONE and GRADED" paragraph ("58 skips where the cube hides the
  jewellery"); eval/failure/label_wrists.py lines 220 to 224 (the skip
  key writes {side: None}) and line 233 (the skip counter).

## 2. Change log

Every line is one edit in build_ch7.py. No printed number changed.

- 7.1 - named the other two rejected right-arm runs, frames 7 to 24 and
  frames 674 to 684, after the 3.0 second gap of frames 550 to 639 (A1),
  with the event-table provenance in the source comment.
- 7.1 - extended the recordings source comment with the second and third
  pinned source for the loop recording's 2099 frames and 69.98 seconds
  and with the pinned source of its task (B2). The prose already gave
  the frame count, the duration and the task of all three recordings, so
  no prose changed.
- 7.2 - rewrote the Table 7.1 caption: Travel is that part's own extent
  along the line and not a cumulative position, and the cube slides back
  0.4 centimetres at the transfer, so the parts overlap and the three
  extents do not sum to the 42.4 centimetre slide (A3).
- 7.2 - recorded the recomputation of the per-part extents from
  eval/reports/r7_handover.csv in the source comment above Table 7.1
  (A3).
- 7.2 - added the provenance clause to the Figure 7.5 caption: the
  dashed polyline through the drawn waypoints is constructed from the
  recording and is not an independent survey of the route (B4).
- 7.3 - added the segment-length cross-reference to Section 6.3: the
  calibrated lengths are medians of each recording's own landmark track
  and not measurements taken on the subject (B3). The lengths are not
  reprinted; the provenance, eval/offset/carry.py seg_lengths and the
  per-recording offset_fit.json, is in the source comment.
- 7.3 - added the provenance clause to the Figure 7.7 caption (B4).
- 7.3 - added the provenance clause to the Figure 7.10 caption and
  reworded its "not the fitted rail line" clause so the sentence carries
  both facts (B4).
- 7.3 - added the provenance clause to the Figure 7.13 caption, naming
  the handover recording as the source of its waypoints (B4).
- 7.4.2 - named the second window of the rail label set, frames 674 to
  684, in place of "a later rejected run" (A1).
- 7.4.2 - stated the discard: the skipped frames are 58 of the 78 loop
  candidates, 38 on the left side and 20 on the right, and the rail set
  has no skip (A4), with the frame-by-frame count and the skip mechanism
  in the source comment.
- 7.4.2 - added the selection effect as the third limit of the closing
  paragraph, with the verified discard count and without asserting a
  magnitude: the 58 skipped frames are the most heavily occluded frames
  of each window, they were never scored, and how far they would move
  any column is not measured (B6).
- Module docstring - recorded the defect pass and pointed at this report.

Passage removed under B7: none. The paragraph that begins "The covered
hips allow a within-recording comparison of two torso rules" was read
sentence by sentence. It reports the two policies, the two pairs of
numbers, the fact that the hold freezes the yaw by construction, the
fact that nothing in the recording measures which is nearer the truth,
and the forward reference to Section 9.4. No sentence argues which
policy is better, so nothing was cut. The interpretation the author
objected to was removed by this morning's rebuild and is quoted in
writing/v8/condensed/notes_revision_ch7.md section (b) under "Old 7.7,
the hip-hold paragraph".

## 3. Not done, with the reason

- A1, A2, A3, A4: no value in Chapter 7 was wrong, so no number was
  corrected. Every A item resolved as a wording or a definition problem,
  and the fixes above are wording only.
- A2, the 419: nothing was changed outside Chapter 7. The count no
  longer appears in any built chapter. If the Chapter 9 writer restores
  the hip-hold option sentence, that writer must state which set the 419
  counts (see A2 above). Reported, not edited.
- A1, eval/labels/README.md: its frames_r6b bullet still describes the
  rail label set as "frames 550 to 684 every fifth frame", which would
  be 27 frames and not the 21 the set holds, and it cites the old
  Section 7.3.3 numbering. It is a data file outside the permitted edit
  scope. For the author to correct in the trace.
- A4, "occlusion was the sole discard reason": confirmed as the only
  documented reason, not verifiable per frame. The labelling tool stores
  a skip as a null entry with no reason field, so the 58 discards carry
  no recorded cause in the data. The chapter therefore states the rule
  the author followed and does not claim a verified per-frame cause.
- B1: already done by the rebuild. The old Section 7.5 is folded into
  the current Section 7.3, its figure is the current Figure 7.8, and the
  median of 6.5 centimetres with the 95th percentile of 9.6 is stated
  once, in the paragraph before that figure. The old 7.6 to 7.9 are the
  current 7.3 to 7.5. Confirmed, nothing to do.
- B1, the cross-reference repairs in the other chapters: not done here,
  by instruction. check_refs.py still reports two unresolved references
  into the old numbering, both outside Chapter 7:
  Chapter_5_Pose_Recovery "sec 7.8" (build_ch5.py, the short-memory
  paragraph; target Section 7.4.2) and Chapter_6_System_Integration
  "sec 7.8" (build_ch6.py line 303, "Section 7.8 measures what a nearly
  straight arm costs"; target Section 7.4.1). The Chapter 9 entries that
  notes_revision_ch7.md section (c) listed have already been repaired by
  the Chapter 9 writer. Chapters 8, 9 and 10 are being rewritten by
  other writers and were not opened for editing.
- B2: no prose edit was needed. Section 7.1 already specifies all three
  recordings in one paragraph: rail 900 frames and about 30 seconds at
  30 frames per second with the one-handed rail task; handover 1499
  frames and 50 seconds with the second arm on the same task; loop 2099
  frames and about 70 seconds with the two-hand carry around a loop and
  the pass from hand to hand. Only the source comment was extended.
- B4, the figure legends themselves: not changed. The plots still print
  the dashed polyline as "Waypoint reference" (make_ch7_object_trajectory.py,
  draw_ch7_trajectories.py, make_ch7_trails_fig.py) and as "reference
  path" (make_ch7_task_schematic.py). This task does not regenerate
  figures, and locked fact 3 holds Figure 7.4 for regeneration from an
  independently registered physical route; the legends change with that
  regeneration. The captions now carry the provenance. Full list of
  affected figures confirmed by reading the four figure scripts: 7.4
  (already carried the provenance after the rebuild), 7.5, 7.7, 7.10 and
  7.13. Figure 7.8 draws the fitted rail line and not the waypoints, so
  it is not affected, and Figure 7.12 draws the fitted line only.
- B5: no edit needed. The phrase "5.3 seconds" appears nowhere in the
  chapter after this morning's review fix. The only remaining 5.3 near
  Table 7.1 is the table's own travel of 5.3 centimetres, and the same
  paragraph gives the transfer as frames 864 to 1022 and as 159 frames,
  so the reader has its length without a duration. The other "5.3" on
  that page is the cross-reference to Section 5.3.
- B7: nothing removed, see the change log. The rebuild had already cut
  the interpretation.
- Figure 7.4 itself remains flagged for regeneration from the
  independently registered physical route, as locked fact 3 requires.
  Unchanged by this pass.

## 4. Check outputs

Before this pass (the morning rebuild, after its review fixes):

    prose 5136, captions 1168, headings 33, tables 147

After this pass:

    python3 build_ch7.py
    saved .../Chapter_7_Evaluation.docx | items: 92

    python3 check_style.py Chapter_7_Evaluation
    == Chapter_7_Evaluation: 0 hits

    python3 check_refs.py
    defined: figures 56, tables 22, equations 45, sections 67,
    appendices ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    references checked: 569
    UNRESOLVED (2):
      Chapter_5_Pose_Recovery: sec 7.8
      Chapter_6_System_Integration: sec 7.8
    never referenced eq: ['3.15', '3.16', '3.18', '3.19', '4.3', '6.3']

    python3 count_words.py ../Chapter_7_Evaluation.docx
    Chapter_7_Evaluation.docx  prose=5298  captions=1269  headings=33
    tables=147  eqs=0

Total including captions, headings and tables: 6747, within the budget
the rebuild worked to. No Chapter 7 entry appears under UNRESOLVED; the
two entries belong to the Chapter 5 and Chapter 6 builders and are
listed in section 3 with their proposed targets. The rebuilt chapter was
copied to Chapter_7_Evaluation_revised.docx in this folder, and the
tracked writing/v8/condensed/Chapter_7_Evaluation.docx carries the same
build.

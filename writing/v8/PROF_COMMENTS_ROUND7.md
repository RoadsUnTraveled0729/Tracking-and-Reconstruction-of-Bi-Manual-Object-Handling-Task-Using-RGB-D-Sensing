# V8 supervisor comments, round of 2026-09-10 (abstract and the last chapter)

Relayed by the user on 2026-09-10 after the handover round ("Everything
looks good."). Numbering continues from PROF_COMMENTS_ROUND6.md (C50).
The user's note with the comments: this should be the last comment.

## C51. Rewrite the abstract in four parts
"However, rewrite the abstract. Basically abstract wants to state a)
what is the problem and why doing it; b) what are the challenges; d)
how you have addressed them and e) how you solve it and what you have
accomplished."
- Target: the Abstract page of the front matter (condensed/scripts/
  build_frontmatter.py, ABSTRACT).
- Current (verified 2026-09-10): three paragraphs, 349 words: the
  system and its sensors, the two measurement chains and the recovery,
  the rail reference and the results. The problem and why it matters,
  and the challenges, are implied rather than stated.
- Decision (user, 2026-09-10, plan approved): rewrite as four
  paragraphs in his order, one per point, inside the 250 to 350 word
  gate, keeping the ground-truth statement of C2 (the tracked object
  trajectory compared with the straight rail defined in the laboratory)
  and the audit wording of M01 and M08, and quoting only numbers printed
  in Chapters 7 and 8.
- Plan: (1) draft the four paragraphs from Section 1.1 (why), Chapters
  2, 3, 5 and 8 and the old Chapter 9 (challenges), the old abstract
  (how) and Chapters 7 and 8 (accomplished); (2) build the standalone
  Abstract_V8.docx from the same ABSTRACT list (scripts/
  build_abstract.py); (3) review loop; (4) change log, text-change list,
  checklist, decisions, handover, commit and push.
- Status: DONE (2026-09-10). Four paragraphs, 344 words: the problem
  and why (two-handed handling, its uses, the cost of capture arrays and
  wearables, one camera and three markers), the challenges (a landmark
  returned whether or not the body part is there, hidden wrists and
  hips, no wrist orientation, causal operation), how they were addressed
  (the two chains that stand in for each other, the rebuilt wrist and
  elbow, the detectors, the remembered hip depth, the labels) and what
  was accomplished (1.0 / 2.4 cm and 0.3 / 1.6 cm against the rail, the
  two gradings of the recovery, 29.0 frames per second). Sent separately
  as writing/v8/Abstract_V8.docx.

## C52. A Discussion chapter
"Also, I think it is better to have a chapter called discussions since
there are a lot to discuss about all your results."
- Target: the old Chapter 9 "Discussion, Future Work, and Conclusion"
  (condensed/scripts/build_ch9.py): 9.1 Limitations, 9.2 Future Work,
  9.3 Conclusion.
- Current (verified 2026-09-10): the discussion was one section of
  limitations listed one after another, with Figures 9.1 and 9.2 and
  Table 9.1; the results of Chapters 7 and 8 were not read against each
  other anywhere.
- Decision (user, 2026-09-10, plan approved): Chapter 9 becomes
  "Discussion", ordered by result: 9.1 Object Tracking Against the Rail,
  9.2 Arm Pose and the Recovery, 9.3 The Second Arm and the Handover,
  9.4 Torso and the Hidden Hips, 9.5 Landmark Failures at High
  Confidence, 9.6 The Live Structure, 9.7 Limits of the Model and the
  Evaluation (Table 9.1). Only numbers already printed in Chapters 7 and
  8 or in the old Chapter 9; no parked material re-enters; the hip hold
  stays a documented option (user decision of 2026-09-09).
- Status: DONE (2026-09-10). condensed/Chapter_9_Discussion.docx, seven
  sections, 2,814 words (the old chapter 2,239 including the conclusion
  and future work). The marker figure is now Figure 9.1 (Section 9.1
  cites it first) and the landmark figure 9.2; Table 9.1 unchanged. The
  number audit (every numeric token in the chapter found in the old
  Chapter 9, the old abstract or the built Chapters 7 and 8) reports
  none missing. Sent separately.

## C53. A Conclusions and Future Work chapter
"Add another chapter called, Conclusions and Future work."
- Target: new Chapter 10 (condensed/scripts/build_ch10.py).
- Decision (user, 2026-09-10, plan approved): 10.1 Conclusions carries
  the old Section 9.3 (the five objectives of Chapter 1 answered in
  order, the real-time result, the torso caveat, the systems framing,
  the scope statement); 10.2 Future Work carries the old Section 9.2,
  with the hip-hold numbers left in Section 9.3 and only pointed at.
- Status: DONE (2026-09-10). condensed/
  Chapter_10_Conclusions_Future_Work.docx, 762 words, no figures or
  tables. Registered in build_thesis.py, build_toc.py,
  build_frontmatter.py (CHAPTER_FILES), check_refs.py, check_style.py
  and count_summary.py. Cross-references moved: Chapter 1 (objective 4
  now cites Chapter 10; the roadmap sentence names both chapters),
  Chapter 3 (Section 9.7), Section 7.7 (Section 9.3), Section 8.4
  (Section 9.6), Appendix E (Section 9.1) and Appendix G (Section 9.4).
  check_refs UNRESOLVED none. Sent separately.

## Delivery
"Please revise the abstract and there last two chapters and send them
separately."
- Files: writing/v8/Abstract_V8.docx, writing/v8/condensed/
  Chapter_9_Discussion.docx, writing/v8/condensed/
  Chapter_10_Conclusions_Future_Work.docx; the change log
  writing/v8/Thesis_V8_Changes_Abstract_Ch9_Ch10.docx; the rebuilt
  writing/v8/Thesis_V8_Condensed.docx and .pdf (ten chapters).

# Condensation round 2 and language check, 2026-09-15

Author request: "condense all the possible places then do the language
check", then "one more round". Brief: CONDENSE2_BRIEF.md. Per-chapter
logs: notes_condense2_chN.md. Baseline commit a95b31e.

## Result

Thesis_V9.pdf 172 pages (was 176). Chapters 1 to 10: 126 pages (was 130).
Front matter 14, appendices and references 32, both unchanged.

Prose words per chapter (count_words.py), before -> after:
Ch1 1399 -> 1399 (untouched), Ch2 2641 -> 2560, Ch3 3812 -> 3606,
Ch4 2018 -> 1964, Ch5 4952 -> 4879, Ch6 4927 -> 4767, Ch7 3820 -> 3820
(untouched, evidence chapter), Ch8 2324 -> 2268, Ch9 3234 -> 3006,
Ch10 1342 -> 848. Total 30469 -> 29117.

Cut: chapter previews and recaps; rationale owned by another chapter
(rigid-body notation in 3.1, Euler extraction steps in 3.4, equation
(4.2) which re-derived (3.4), the Scene chain in 5.3, byte-level transport
in 6.1, table narration in 9.2 and 9.3, re-argument of Chapter 9 in 10.1).
Chapter 10 is the author's verbatim text and was cut by whole-sentence
deletion, plus logged single-word connective edits (notes_condense2_ch10.md
lists each for revert). Nothing moved into an appendix. No printed number
retyped; the one unit change (Section 5.6 reach printed as 50.7 cm of
52.2 cm instead of 0.51 m of 0.52 m) was verified against
ch5_worked_example.py, values unchanged.

## Language check

Three rounds under .agent/CHAPTER_REVIEW.md with fresh Opus reviewers:
round 1 whole chapters (Chapter_N_condense2_round1.txt), round 2 changed
paragraphs only (condense2_round2_changed_paragraphs.txt; 22 defects, 21
fixed and confirmed in condense2_round3_check.txt, 1 declined), round 3
whole chapters with CERTAIN/UNCERTAIN marking (Chapter_N_condense2_round3.txt).
Every CERTAIN flag was fixed unless it required retyping a number, a new
fact, a heading change, a locked table or caption, or rewording the
author's verbatim sentences; those are listed per chapter in the notes.
Arithmetic "does not recompute" flags in Chapters 3, 4, 5 and 6 were
checked against the generating scripts (ch3_numbers.py, ch4_numbers.py,
ch5_worked_example.py, ch6_numbers.py): all are two-decimal rounding
artefacts, no printed value is wrong.

Checks at delivery: build_thesis PASS; render_pdf three indexes converged;
verify_submission 22 of 22 PASS (baseline regenerated; display count 103
and equation-table count 55 updated in verify_submission.py); check_style
0 hits on all twelve parts; check_refs UNRESOLVED none;
test_assembly_citations OK.

## Left to the author

Condensation candidates not taken (professor comments or evidence):
merging Figures 7.8 and 7.9; trimming Table 9.1 rows (C52); shortening
the Section 5.2 threshold read-out (C24); dropping adapted rows of Table 8.1.

Author decisions applied later on 2026-09-15:
- Section 5.6 shows frames 549 and 560 side by side as the new Figure 5.6
  (make_ch5_fig_frames.py, 5.0 in wide; points from the verified frame-560
  run, no number recomputed) and the heading names both frames.
- Section 3.4.3 no longer names a threshold; the twist-unobservable test is
  described from the code as the perpendicular part of the forearm vanishing
  against its length. The Figure 3.1 caption says "stored thirteen-angle";
  Section 3.5 already states that eleven are independent.
- Figure 4.2 caption and text agree on the verified counts: 899 of 900
  frames detected, eleven bridged rows, ten despiked and one undetected
  (frame 786); sources tabulated in notes_condense2_ch4.md.
- Chapter 10 is excluded from language iterations; every word-level edit
  was reverted, so each surviving author sentence is byte-identical to
  commit a95b31e except the one pointer sentence naming Sections 9.3 to 9.6.

Final check of 2026-09-15 (Sonnet, three reports in writing/reviews/
final_check_*_2026-09-15.txt): evidence audits 0 real failures
(verify_ch7_restructured 1157 PASS); layout clean apart from two half-empty
appendix pages (C2, E1) and the date placeholder; consistency found three
items: the Section 5.6 pointer to Section 5.3 (fixed to Sections 6.2 and
6.4), d printed 71.62 vs 71.6 cm (Chapter 5 now 71.6, verified from the
calibration JSON), and the abstract clause "differ by 0.53 to 2.83 cm
depending on detection settings", which attributes the Table 7.1/7.2 point
errors to detection settings; the abstract is the professor's text and was
not changed.

Closed by the author on 2026-09-15: the glossary stays as it is, and the
abstract clause stays as it is. No open decision remains from this round.

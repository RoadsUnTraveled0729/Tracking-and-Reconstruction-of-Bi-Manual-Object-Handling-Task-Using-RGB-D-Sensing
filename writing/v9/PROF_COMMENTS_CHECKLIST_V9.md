# Supervisor comments checklist, V9

Each comment from the supervisor's messages on the V9 round, with where
it is answered in the built V9 chapters and its status. Comment
numbering continues from writing/v8/PROF_COMMENTS_CHECKLIST.md (C1 to
C53, closed with the V8 delivery of 2026-09-10). C54 is supplied by
writing/v9/PROF_COMMENTS_2026-09-16.md, the round of 2026-09-16 on
Chapter 9 and Chapter 10 bullets and the chapter transitions. The
supervisor's comments of 2026-09-14 (the general Chapter 9 opening and
Section 9.1, shorter subsections, the table of contents reference pages,
the list of equations, and the avatar sizing) were relayed by the author
that day and recorded in writing/v9/REVISION_2026-09-14_BRIEF.md Section
2 ("Round scope"); they were not given comment numbers and are not
repeated here.

# Round of 2026-09-16: Chapter 9 and Chapter 10 bullets, chapter transitions

## C54. Bullet format for Chapter 9 and Chapter 10, and condensed chapter transitions (round of 2026-09-16)
- Where: Chapter 9 "Discussion" (writing/v9/scripts/build_ch9.py) and
  Chapter 10 "Conclusions and Future Work" (writing/v9/scripts/
  build_ch10.py), Sections 9.1 to 9.7 renumbered from 9.2 to 9.8 with
  the former 9.1 folded into the chapter opening, prose shortened to
  lead sentence plus bullets; the opening and closing transition
  paragraphs of every chapter (writing/v9/scripts/build_ch1.py through
  build_ch10.py). Full comment, target, current state and plan in
  writing/v9/PROF_COMMENTS_2026-09-16.md; author decisions and the
  override of the no-bullet rule in writing/v9/DECISIONS.md D-128;
  worker briefing in writing/v9/C54_BRIEF.md.
- Status: DONE (2026-09-16), second pass after the author's review.
  Chapters 9 and 10 went back to prose with a few short lists after the
  author found the all-bullet form unclear; the Chapter 1 and Chapter 9
  openers and Section 10.2 were shortened and reworded off their
  AI-sounding phrasing; bullets and numbers are now used sparingly,
  confined to Section 1.4, the Chapter 5 opening, Sections 9.5, 9.7,
  10.1 and 10.2, and the pre-existing Appendix A.1 steps. Evidence:
  Chapter 9 3,006 to 1,699 prose words (one numbered list of three
  limitation groups in 9.5, one bulleted list in 9.7), Chapter 10 857 to
  457 (two numbered lists of three items each, in 10.1 and 10.2);
  verify_submission 22 of 22 PASS, check_style 0 hits, check_refs
  UNRESOLVED none, citations OK, 170 pages; first-pass commits 1d5521a,
  2c8665e, 6416f9f, d342d1b, 8434f29, 894f373; second-pass commits
  06af1da, f0b5170, a625123. Full record in DECISIONS.md D-128 and
  D-129.
- Status: DONE (2026-09-16), third pass, the final state. The author
  re-read the supervisor's wording ("Make them all in a bullet format
  ... IN chapter 10, also introduce bullets") and asked to follow it
  after all. Chapter 9 Sections 9.1 to 9.7 are each a lead sentence plus
  labelled bullets again, restored under the two-paragraph opener kept
  from the second pass; the former Section 9.1 overview stays as the
  unnumbered chapter opening, since the supervisor's "you do not need to
  add subsection" is read as objecting to the numbered heading, not to
  the opening text. Chapter 10's two lists (three conclusions, three
  future-work directions) are bullets instead of numbers; their text is
  unchanged. Kept from the second pass: the Chapter 1 opener at 70
  words, the Chapter 7 opener, Chapter 5 Cases A to C as labelled
  bullets with the states in prose, the sentence-keeps-with-its-list
  rule, the NUM item kind (now unused in content). Lists thesis-wide:
  Section 1.4 (four bullets), Chapter 5 opening (three case bullets),
  Chapter 9 (lead sentence plus bullets in every section, about 33
  bullets), Section 10.1 (three bullets), Section 10.2 (three bullets),
  Appendix A.1 (eight numbered steps, pre-existing). Evidence: Chapter 9
  1,757 prose words, Chapter 10 457 (unchanged); verify_submission 22 of
  22 PASS, check_style 0 hits, check_refs UNRESOLVED none, citations OK,
  170 pages; commits cc51e0d (Chapter 9 and Chapter 10 bullet content,
  subject names only the docstring fix the commit also carries), 3f2bf55
  (notes). Full record in DECISIONS.md D-128, D-129 and D-130.

## C55. Plain-language single bullets in Chapter 9 and Chapter 10 (round of 2026-09-16)
- Where: Chapter 9 "Discussion" (writing/v9/scripts/build_ch9.py), the
  seven sections 9.1 to 9.7 losing their numbered headings and bold
  run-in labels and becoming one plain-language bullet each; Chapter 10
  "Conclusions and Future Work" (writing/v9/scripts/build_ch10.py), its
  six bullets (three conclusions, three future-work directions) rewritten
  in layman's terms. Full comment, target, current state and plan in
  writing/v9/PROF_COMMENTS_2026-09-16.md C55; author decision in
  writing/v9/DECISIONS.md D-131.
- Status: DONE (2026-09-16). Chapter 9 has no Sections 9.1 to 9.7 left;
  it has an H1, two opening paragraphs, and seven bullets with no
  headings and no bold, one per former section in the former order, the
  first built from the supervisor's own example rewrite made impersonal.
  Figure 9.1 sits after the first bullet, Figure 9.2 after the fourth,
  Table 9.1 unchanged with every number, then a plain closing paragraph.
  Only one number remains in the Chapter 9 bullets (about 12 centimetres
  between the offline and live wrist chains); every other number stays in
  Table 9.1 or a figure caption. Every "Section 9.x" pointer in Chapters
  3, 4, 5, 8, 10 and Appendix G now reads "Chapter 9". Chapter 10 keeps
  its lead paragraph and "10.1"/"10.2" headings, with three conclusion
  bullets and three future-work bullets rewritten in layman's terms and
  no bold, and the contribution and scope paragraph simplified; the
  author's closing sentence is unchanged. Section 1.4 and the Chapter 5
  case bullets also lose their bold labels (wording unchanged), so no
  bullet anywhere in the thesis carries a bold label. Evidence: Chapter 9
  1,757 to 1,072 prose words, Chapter 10 457 to 566, total body 32,276 to
  31,750; verify_submission 22 of 22 PASS, check_style 0 hits, check_refs
  UNRESOLVED none, citations OK, 168 pages (legitimate: Chapter 9 lost
  seven headings and about 750 words); commits 0b8e992 (the "Section
  9.x" pointers repointed to "Chapter 9"), 7ca4ab0 (the Chapter 9 and
  Chapter 10 rewrite), 7112bfe (fix: Chapter 9 bullets name Figures 9.1
  and 9.2 and Table 9.1 before they appear, render_pdf's footer check
  skips contents pages), d4008ef (Section 1.4 and Chapter 5 case bullets
  lose their bold labels). The supervisor closed the round: "We are Done
  for now." Full record in DECISIONS.md D-131.

# V9 supervisor comments, round of 2026-09-16 (Chapters 9 and 10 bullets, transitions)

Relayed by the user on 2026-09-16, after the condensation round and its
three language rounds ("It reads much better."). Numbering continues
from PROF_COMMENTS_ROUND7.md (C53).

## C54. Bullet format for Chapter 9 and Chapter 10, and condensed chapter transitions
"Hi, It reads much better. One last comment, in chapter 9, you do not need
to add subsection. Make them all in a bullet format. Also, ask AI to
shorten each of the descriptions in subsections. IN chapter 10, also
introduce bullets and ask to see if you can shorten the descriptions."

The author's own addition, verbatim: "so bassically condense the
beginning and end transition parageraph for each chapter and to those
areas we are allowed to use bullet points. make the layout nice please."

- Target: Chapter 9 "Discussion" (writing/v9/scripts/build_ch9.py) and
  Chapter 10 "Conclusions and Future Work" (writing/v9/scripts/
  build_ch10.py); the opening and closing transition paragraphs of every
  chapter (writing/v9/scripts/build_ch1.py through build_ch10.py).
- Current (verified 2026-09-16, count_words.py and a section-by-section
  read of the built Chapter_9_Discussion.docx and
  Chapter_10_Conclusions_Future_Work.docx): Chapter 9 opens with a
  63-word unnumbered paragraph, then Section 9.1 "The Integrated
  Reconstruction and Its Evaluation" (the general overview added by
  D-119, 215 prose words, no number of its own in the supervisor's
  reading), then seven numbered sections 9.2 to 9.8, each ordinary
  prose: 9.2 Object Reconstruction and Physical-Route Error Sources (486
  words, Figure 9.1 caption 30 words), 9.3 Human-Object Spatial
  Reconstruction (655 words), 9.4 Landmark Failure and Object-Assisted
  Recovery (509 words), 9.5 Torso and Root Failure and High-Confidence
  Landmark Errors (316 words, Figure 9.2 caption 27 words), 9.6
  Single-View Observability and Model Limits (288 words), 9.7 Real-Time
  and Causal Implications (242 words), 9.8 Scope of the Evaluation (232
  words, Table 9.1 caption 19 words). Chapter 9 prose totals 3,006
  words. Chapter 10 has 10.1 Conclusions (437 prose words) and 10.2
  Future Work (420 prose words), 857 words total, no figures or tables.
  No paragraph in either chapter, and no chapter opener or closer
  anywhere in the ten chapters, uses a bullet list; check_style.py and
  every builder currently print running prose only.
- Decision (author, 2026-09-16, settled as D-128):
  1. Chapter 10 may be rewritten by the AI; the verbatim-text rule of
     2026-09-12 (Chapter 10 cut only by whole-sentence deletion,
     excluded from language passes) is lifted for this round. The
     author reviews the result.
  2. Cut depth about half: Chapter 9 from 3,006 prose words to about
     1,500; Chapter 10 from 857 to about 450. Every number, figure,
     table, caption, citation and locked statement stays.
  3. The standing rule "no bullet lists in the thesis prose"
     (REVISION_2026-09-14_BRIEF.md line 54, CONDENSE2_BRIEF.md lines 62
     to 63) is overridden for Chapter 9, Chapter 10 and the opening and
     closing transition paragraphs of every chapter, and nowhere else.
     Bullets use the native Word "List Bullet" style with a hanging
     indent; a complete sentence introduces each list (SUBMISSION_
     CHECKLIST_2026-09-13.md row 48 precedent, "A complete sentence
     introduces the numbered procedure").
  4. Workers are Sonnet subagents in small scoped tasks; the
     orchestrator briefs and verifies.
- Plan: Chapter 9 opener merges the former opening paragraph and the
  former Section 9.1 into unnumbered chapter-opening text; the former
  9.2 to 9.8 become 9.1 to 9.7, each a lead sentence plus three to six
  bullets with a bold run-in label; Figures 9.1, 9.2 and Table 9.1 keep
  their numbers and places. Chapter 10: 10.1 a lead paragraph plus
  bullets; 10.2 a lead sentence plus three future-work bullets and the
  hardware-scaling closing sentence with citation [49]. Every "Section
  9.x" cross-reference in the other chapters follows the renumbering.
  Transitions in Chapters 1 to 8 condensed from about 1,770 to about
  1,000 words; Section 1.4 and the Chapter 5 cases and states become
  bullets; Chapter 7 (no opener or closer today) is not touched; Section
  2.5's last paragraph is the author's verbatim text and is not touched.
  Mechanics and per-chapter briefing: writing/v9/C54_BRIEF.md.
- Status: DONE (2026-09-16), second pass after the author's review of
  the first-pass delivery above. The author found the all-bullet
  Chapters 9 and 10 unclear and strange, the Chapter 1 and Chapter 9
  openers still too long and AI-sounding, Section 10.2 AI-sounding, and
  asked that bullets and numbers be used sparingly throughout, not as
  the default format for whole chapters. Delivered: Chapter 9 is prose
  in Sections 9.1 to 9.7 (the former Section 9.1 still merged into the
  unnumbered chapter opening), with one numbered list of the three
  limitation groups in Section 9.5 and one bulleted list of missing
  references in Section 9.7, 3,006 to 1,699 prose words; Chapter 10 is a
  lead paragraph, a numbered list of three conclusions, a numbered list
  of three future-work directions and the author's own closing
  sentence, 857 to 457 prose words; Chapter 1 opener cut to 70 words;
  Chapter 7 opener restored; Chapter 5 keeps Cases A to C as bullets and
  now defines the three states in one prose sentence; native "List
  Number 2" style added for numbered lists, restarting per list. Lists
  thesis-wide: Section 1.4 (four bullets), Chapter 5 opening (three case
  bullets), Section 9.5 (numbered, three), Section 9.7 (bulleted,
  three), Section 10.1 (numbered, three), Section 10.2 (numbered,
  three), Appendix A.1 (eight numbered steps, pre-existing). Commits:
  06af1da (List Number 2 mechanics), f0b5170 (Chapter 1 and 7 openers),
  a625123 (Chapters 9 and 10 back to prose). Checks: verify_submission
  22 of 22 PASS, check_style 0 hits, check_refs UNRESOLVED none,
  citations OK, 170 pages. Full record in DECISIONS.md D-128 and D-129.
- Status: DONE (2026-09-16), third pass, the final state. The author
  re-read the supervisor's comment in full and asked to follow it after
  all: "we should follow his advise, sorry for the misleading." Chapter 9
  Sections 9.1 to 9.7 are each a lead sentence plus labelled bullets
  again, restored under the two-paragraph opener kept from the second
  pass; the former Section 9.1 overview stays as the unnumbered chapter
  opening (only the numbered "9.1" heading goes, per the author's
  reading of "you do not need to add subsection"). Chapter 10's two
  lists (three conclusions, three future-work directions) are bullets
  instead of numbers; their text is unchanged from the second pass. Kept
  from the second pass: the Chapter 1 opener at 70 words, the Chapter 7
  opener, Chapter 5 Cases A to C as labelled bullets with the states in
  prose, the sentence-keeps-with-its-list rule, the NUM item kind (now
  unused in content). Lists thesis-wide: Section 1.4 (four bullets),
  Chapter 5 opening (three case bullets), Chapter 9 (lead sentence plus
  bullets in every section, about 33 bullets), Section 10.1 (three
  bullets), Section 10.2 (three bullets), Appendix A.1 (eight numbered
  steps, pre-existing). Commits: cc51e0d (the Chapter 9 and Chapter 10
  bullet content, subject names only the docstring fix that the commit
  also carries), 3f2bf55 (notes). Checks: verify_submission 22 of 22
  PASS, check_style 0 hits, check_refs UNRESOLVED none, citations OK,
  170 pages (Table 9.1 shares its page with the closing paragraph). Full record in DECISIONS.md D-128, D-129 and D-130.

## C55. Plain-language single bullets in Chapter 9 and Chapter 10
"Hi, I think you should use normal explanation to discuss each bullet. It
is rather vague what you are discussing. Try to rewrite them in a
layman's terms and explanations. It is better that you don't give the
bullets a headings in bold. Just explain what you are discussing. You may
want to group the main points that you want to discuss together under a
common theme. You want the ready to understand the main points you are
discussing about your methods and results in relation to the propose
theme/title of the thesis. So for example, do not have subsections such
as 9.1, to 9.7. Instead have a single bullet each. Then combined all of
the bullets that you have now for each of these subsections into one
short/clear explanations. For example, here is a rewrite of the first
subsection (9.1): Comparing the reconstructed object path with simple
tape-measure distances shows a clear pattern in the errors: carry
segments come out a bit shorter than they really are, while lift and
slide segments come out a bit longer. Changing the detector settings
changes how large the errors are, not their direction. Lift points are
the least reliable because each one depends on depth from a single video
frame. Some extra uncertainty also comes from how much the object wobbles
or rotates, since those checks rely only on the recording itself, not an
external reference. When the system loses the marker, it simply gives no
position rather than a wrong one, and these losses happen only outside
the labelled parts of the data, so the labelled comparisons remain
unaffected. Figure 9.1 shows one such loss. So do the same thing for the
all the discussion part. Same for the bullets in the Conclusion and
Future work. Try to use layman's term to explain each of the bullets.
Other than these. We are Done for now."

- Target: Chapter 9 "Discussion" (writing/v9/scripts/build_ch9.py) and
  Chapter 10 "Conclusions and Future Work" (writing/v9/scripts/
  build_ch10.py).
- Current (verified 2026-09-16, count_words.py and a section-by-section
  read of the built Chapter_9_Discussion.docx and
  Chapter_10_Conclusions_Future_Work.docx, the third C54 pass state):
  Chapter 9 opens with the two-paragraph unnumbered opener kept from the
  second C54 pass (about 120 words), then Sections 9.1 to 9.7, each a
  lead sentence plus three to six bullets with a bold run-in label, about
  33 labelled bullets in all, several of them stating centimetre and
  degree figures inline (segment-length differences, wrist separations,
  the elbow shift) alongside Table 9.1's identical numbers; Figure 9.1
  sits inside Section 9.1's bullet group, Figure 9.2 inside Section 9.4's,
  Table 9.1 and its caption close Section 9.7, and the chapter's closing
  paragraph follows the table; 1,757 prose words. Chapter 10 has a lead
  paragraph, a "10.1 Conclusions" heading with three labelled-in-substance
  bullets, a "10.2 Future Work" heading with three bullets naming
  RTMPose-m, COCO-17 and ONNX Runtime, the contribution-and-scope
  paragraph, and the author's own closing sentence; 457 prose words. No
  chapter uses a single combined bullet per former section; check_style.py
  and verify_submission.py both pass on this state. 170 pages.
- Decision (author, 2026-09-16): follow the comment as written; settled
  as D-131.
- Plan: Chapter 9's seven sections (9.1 to 9.7) lose their numbered
  headings and their bold run-in labels; each section's several bullets
  are combined into a single plain-language bullet, one per former
  section, in the former order, with no jargon term left unexplained. The
  first bullet is built from the supervisor's own example, made
  impersonal (the thesis never uses "we"). Figure 9.1 stays after the
  first bullet, Figure 9.2 after the fourth, Table 9.1 and its caption
  keep every number and close the sequence, and the chapter's closing
  paragraph is kept, in plain language, after the table. Numbers move out
  of the bullets into Table 9.1 and the two figure captions wherever the
  table or caption already carries the same figure; the one exception is
  the roughly 12 centimetre gap between the offline and live wrist
  chains, kept in its bullet because no table row carries it. Chapter 10
  keeps its "10.1 Conclusions" and "10.2 Future Work" headings and its
  three-plus-three bullet structure (the supervisor's rewrite instruction
  was illustrated on Chapter 9's numbered subsections, not on Chapter 10's
  already-unheaded bullets), but every bullet, and the contribution and
  scope paragraph, is rewritten in layman's terms with no bold. Every
  "Section 9.x" pointer elsewhere in the thesis is repointed to "Chapter
  9". Work done by a Fable fork, the author's voice preference for these
  chapters.
- Status: DONE (2026-09-16). Delivered: Chapter 9 has an H1, the same two
  opening paragraphs, and seven bullets with no headings and no bold, one
  per former section in the former order, each built to plain language
  (the first from the supervisor's example); Figure 9.1 after the first
  bullet, Figure 9.2 after the fourth, Table 9.1 unchanged with every
  number, then the plain closing paragraph; only one number remains in
  the bullets themselves (about 12 centimetres between the offline and
  live wrist chains). Every "Section 9.x" pointer in Chapters 3, 4, 5, 8,
  10 and Appendix G now reads "Chapter 9". Chapter 10 keeps its lead
  paragraph and its "10.1"/"10.2" headings, with three conclusion bullets
  and three future-work bullets rewritten in layman's terms and no bold,
  and the contribution and scope paragraph simplified; the author's
  closing sentence is unchanged. Commits: 0b8e992 (the "Section 9.x"
  pointers repointed to "Chapter 9" in Chapters 3, 4, 5, 8 and Appendix
  G), 7ca4ab0 (the Chapter 9 seven-bullet rewrite and the Chapter 10
  layman's-terms rewrite), 7112bfe (fix: the Chapter 9 bullets now name
  Figure 9.1, Figure 9.2 and Table 9.1 before each appears, and
  render_pdf's footer part-label check skips contents pages, since a
  dot-leader contents page had started matching the check after Chapter
  9's subsections went), d4008ef (Section 1.4 and the Chapter 5 case
  bullets lose their bold labels too, matching the same preference;
  wording unchanged; no bullet anywhere in the thesis now carries a bold
  label). Checks (chain10.log, complete, rerun after each fix and again
  after d4008ef): verify_submission
  22 of 22 PASS, check_style 0 hits, check_refs UNRESOLVED none, citations
  OK, 168 pages (down from 170, legitimate: Chapter 9 lost its seven
  numbered headings and about 750 prose words). Word counts
  (count_words.py): Chapter 9 1,072 prose words (was 1,757), Chapter 10
  566 (was 457), total body 31,750 (was 32,276). Full record in
  DECISIONS.md D-131.

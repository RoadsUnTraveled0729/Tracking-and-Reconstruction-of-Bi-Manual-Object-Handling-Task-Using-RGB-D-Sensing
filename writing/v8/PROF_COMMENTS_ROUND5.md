# V8 supervisor comments, round of 2026-09-07 (Chapter 4)

The supervisor's message on Chapter 4, relayed by the user on
2026-09-07 with the direction "i think you need to change through the
whole thesis". Numbering continues from PROF_COMMENTS_ROUND4.md
(C22-C47). The same day the user gave three directions of their own
that are handled in the same pass and listed at the end (U1-U3).

Every "Current" line is checked against the built condensed parts in
writing/v8/condensed and their builders in
writing/v8/condensed/scripts; the deliverable is
writing/v8/Thesis_V8_Condensed.docx.

## C48. Two decimals at most, in the matrices and in every number
"In the value of the matrices, do not go beyond two decimals. For
example, if it is 0.0014 just write 0.0. Same comments for all the
numerical values."
- Target: every number in the thesis, the appendices included (user:
  "change through the whole thesis").
- Current (verified by dumping every built part and searching for
  numbers with three or more decimals, 2026-09-07 before the edits):
  Chapter 4 worked example (two 4-decimal matrices, seven 4-decimal
  vectors, 0.000002, 1.18 degrees, world x 0.0304 and 0.0341 m);
  Chapter 5 worked example (L1 0.317 m, L2 0.205 m, 0.507 in the
  cosine law); Chapter 6 worked example (session-clock times 18.280,
  18.318, 18.251, 18.247 s in two paragraphs and Table 6.2); Chapter 2
  Section 2.5 and Appendix F (the Hampel factor 1.4826); Appendices C,
  D, E (visibility 0.5778, normalized-coordinate intervals, depths and
  positions to the millimetre in metres, the intrinsics to five
  decimals, Table E.1 to three decimals, the Rodrigues example to six
  decimals). Chapters 1, 3, 7, 8, 9 and the front matter were already
  at two decimals (Chapter 3's T matrices since round 3, Chapters 7 to
  9 since C38).
- Action: round every printed number to at most two decimals from its
  full-precision source (not from the printed value), with one set of
  conventions across the parts: rotation entries and unit vectors to
  two decimals, near-zero written 0.00; vectors inside equations in
  metres with two decimals; prose distances in centimetres or
  millimetres with one decimal (C38); session-clock times in seconds
  with two decimals and offsets in whole milliseconds; where rounded
  operands no longer give the printed result, drop the intermediate
  value or state the result only (the Chapter 4 intermediate product,
  the Appendix E trace arithmetic, the Appendix C normalized
  intervals). Builder comments keep the full-precision values. Add
  the check to check_style.py so that it cannot regress, and the rule
  to skill_set/measurement-precision-reporting.md and the reviewer
  brief.
- Where: Chapter 4 Section 4.3; Chapter 5 Section 5.6; Chapter 6
  Section 6.5 and Table 6.2; Chapter 2 Section 2.5 (the user's own
  sentence, recorded as a find/replace pair in
  condensed/notes_followup_ch2.md); Appendices C.3, Table C.2, Table
  D.1, D.4, Table E.1, E.4, F. Every old -> new pair is listed in
  writing/v8/PRECISION_ROUND5_CHANGES.md.
- Status: DONE (2026-09-07).

## C49. Show images of the experiment
"It would be nice if you can show the images of the experiment."
- Target: Chapter 4 (the chapter he was reading). Chapter 2 opens
  with the setup photograph (Figure 2.1) and the scene frame with the
  coordinate frames drawn (Figure 2.5); Chapter 7 carries the
  colour-frame strip of the task (C33). Chapter 4 itself had no
  image of the experiment, only the filtered track plot.
- Action: new Figure 4.1 in Section 4.1: the four colour frames of
  the task (grasp on the desk, frame 95; lift onto the rail, 505;
  slide along the rail, 700; far end of the rail, 898, the moments of
  the Chapter 7 strip) with the detector's output drawn on each: the
  yellow outline of the object marker and the object frame O from the
  detected pose, the world frame W on the desk marker, and a
  magnified inset of the cube per panel. Script
  condensed/scripts/make_ch4_experiment_fig.py, poses from the
  unscaled raw detections (the scaled ones project axis tips off the
  printed marker), intrinsics from the recording. The track plot
  becomes Figure 4.2. One introducing paragraph before the figure.
- Status: DONE (2026-09-07).

# User directions of the same day (not supervisor comments)

- U1. Glossary for an engineering reader: define p95 and the record
  codes PSF1, PSR2, PSB2, PSB3, PSI2; drop entries a colleague would
  know. Done in build_frontmatter.py: six entries out (colour and
  depth frame, intrinsics, kinematic model, two-link inverse
  kinematics, rig and avatar, tabletop plane), eight in (the landmark
  numbering L11 to L24, the T subscript convention, the chordal mean,
  the hip depth preparation, L1 and L2, the PUMA convention, the
  record codes, median and p95), and the RGB-D entry now spells out
  the abbreviation and names the D435.
- U2. Chapter 6 worked example: show the coordinate transformation
  calculation, not only its results. Done in Section 6.5: the person
  path of equation (6.2) with A = S R_cam F, S t_cam and p_U printed at
  two decimals, the levelling rotation and the raise to the floor, and
  the object's inverse path through the link; numbers from the new
  condensed/scripts/ch6_numbers.py.
- U3. The user asked what "[UPDATE FIELDS IN WORD: F9]" at the table
  of contents is: it is a note the front matter builder writes above
  the contents field, because the builder cannot compute page numbers;
  Word fills the contents and the three lists when the fields are
  updated (the file also asks Word to update them on opening), after
  which the note is deleted by hand. Later the same night the user
  said the note must not appear in the printed thesis: the builder no
  longer writes it (build_frontmatter.py), the file still asks Word to
  update its fields on opening, and the repository PDF is now rendered
  by condensed/scripts/render_pdf.py, which fills the contents and the
  three lists through LibreOffice before exporting.
- U4. D9 ("do it if you can"): the trajectories drawn inside the Unity
  scene, Figure 7.10 (see C36 in the checklist; redesigned 2026-09-08 as
  one panel per task interval after the clarity review, D-015 to D-019). The user also decided: the title stays as supplied
  (Bi-Manual), and the date approved stays a placeholder.

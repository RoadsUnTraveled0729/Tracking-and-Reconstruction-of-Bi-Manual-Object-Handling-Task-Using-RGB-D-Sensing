# V7 supervisor comments, round of 2026-08-11

Every comment from the supervisor's message, mapped to its target and action.
Status: EXECUTED (this round) or DEFERRED (a later V7 round). This round
delivers only the finalized table of contents (English) and Chapter 1
(Chinese); the thesis body moves to Chinese from V7 on.

## C1. Title page format and committee members
"The title page should follow the format of the thesis template. There should
be other members listed. I do not see the name of other committee members."
- Target: front matter (title page + approval page).
- Action: rebuild the title and approval pages against the Eng.Sci. thesis
  format template; add the other examining committee members. BLOCKER: the
  other committee members' names and roles are not in the repo; they must
  come from the user before the front matter can be built.
- Status: DEFERRED.

## C2. Abstract rewrite
"The abstract needs to be rewritten more aligned with your language. Also,
make sure you mention that the tracking results are compared with the ground
truth which is the actual path you define in the lab."
- Target: Abstract.
- Action: rewrite in the student's own voice; state explicitly that tracking
  results are compared against ground truth, the actual path defined in the
  lab (the wire the person follows).
- Status: DEFERRED.

## C3. Chapter page breaks and format compliance
"Make each chapter starts on a new page. Make sure you follow the eng. Sci
thesis format template."
- Target: full build (build_thesis equivalent).
- Action: insert a page break before every chapter heading; audit the build
  against the Eng.Sci. format template.
- Status: DEFERRED for the full build. The standalone Chapter 1 docx starts
  on its own first page by construction.

## C4. Chapter 2 whole-setup photo first
"In chapter 2, first show the image of the whole setup using your phone. This
should include the ground truth wire that the person need to follow, the
Aruco markers, the RGB-D sensor and you. This should come first before other
images and explain the overall objective of the user study."
- Target: Chapter 2, before all other figures.
- Action: new phone photograph of the complete setup (ground-truth wire,
  ArUco markers, RGB-D sensor, the participant); place it as the first figure
  of Chapter 2 with prose explaining the overall objective of the user study.
  BLOCKER: the photo must be taken by the user in the lab.
- Status: DEFERRED.

## C5. Equations broken in the Word file
"Somehow the equations in the Word file is messed up." /
"Equations in section 4.2.1 are not showing correctly."
- Target: all OMML equations (eqn.py output), 4.2.1 explicitly.
- Action: reproduce the corruption (likely a Word version or docx merge
  issue), fix the OMML generation or embed equations differently, verify in
  the same Word environment the supervisor uses.
- Status: DEFERRED.

## C6. Data filtering: which, why, reference, results
"When you talk about data filtering, you need to mention which one you have
used and why. Then, refer the reader to a reference textbook (or wherever you
have borrowed them from). You should also show the results after filtering."
- Target: 2.1.5 Signal Smoothing and 4.3.3 Filtering the Object Track.
- Action: name each filter actually used (Hampel despike, gap bridging,
  Butterworth 3 Hz zero-phase; Savitzky-Golay window 9 order 2, rolling
  chordal mean), state why each was chosen, cite a reference textbook for
  each, and add before/after filtering result figures.
- Status: DEFERRED.

## C7. Optional filter-features appendix
"Not sure if we should add an appendix highlighting the features of each
filter."
- Target: appendix list.
- Action: Appendix F "Characteristics of the Candidate Filters" added to the
  finalized TOC (one line to delete if the supervisor decides against it).
  Content written in a later round.
- Status: EXECUTED in the TOC; content DEFERRED.

## C8. Figure 2.5 clarity
"Figure 2.5 is not clear. You may want to break it down to make a bigger.
Also label the Figures and add captions for each set."
- Target: Figure 2.5 (filtering overview panel).
- Action: split into larger individual figures, label each, caption each set.
- Status: DEFERRED.

## C9. Kinematic model figure before 3.4.1
"In the joint angle calculation section, show a kinematic model of an arm
(similar to what we draw in robotics course) and the label which joint angle
is which. This clear figure should come before section 3.4.1. For example,
draw some schematic similar to PUMA robot for the shoulder joint and
connected elbow joint and the wrist point. In there, label the joints which
you are solving for."
- Target: Chapter 3, opening of 3.4 (before 3.4.1).
- Action: PUMA-style schematic of the arm: shoulder joint, connected elbow
  joint, wrist as a point; label every solved joint angle.
- Status: DEFERRED.

## C10. Wrist is not a solved joint
"Section 3.4.4, we do not solve for wrist joints. We are solving for the
shoulder and elbow joints. The wrist would be just a 3D point which we can
then track."
- Target: 3.4.4 and the TOC.
- Action: TOC retitled 3.4.4 to "The Wrist as a Tracked Point"; the 3.4.4
  prose is rewritten in the Chapter 3 round to present the wrist as a tracked
  3D point, not a solved joint.
- Status: EXECUTED in the TOC; prose DEFERRED.

## C11. Worked example must reference the kinematic diagram
"In the example you are solving, you need to directly refer to the kinematic
diagram of PUMA type model which I mention above and show the corresponding
angles that you are solving for."
- Target: 3.4.5 Worked Example.
- Action: reference the C9 schematic directly and point each solved angle at
  its label in the diagram.
- Status: DEFERRED (depends on C9).

## C12. Chordal-mean anchor question
"What is chordal-mean anchor?"
- Target: 4.2.1 / 4.3.1 terminology.
- Action: the term is defined in 4.2.1 (element-wise mean of the first ten
  marker rotations projected back onto the rotation group via SVD, then
  frozen as the world anchor). The Chapter 4 round adds a plain definition at
  first use, or replaces the shorthand "chordal-mean anchor" with a spelled
  out phrase, so the term never appears before its definition.
- Status: DEFERRED.

## C13. Finalized table of contents
"Prepare the table of content of the thesis as we have agreed and based on
the thesis format. Sent it to me so we can call it finalized."
- Target: TOC.
- Action: Thesis_V7_TOC.docx built (English): V6 structure with the C10
  retitle and the C7 Appendix F line; front matter list in the Eng.Sci.
  format order.
- Status: EXECUTED.

## C14. Language change
"next version, i want you to write in chinese, instead of english ... toc in
english, chapter 1 in chinese" (user directive, same round).
- Target: whole V7 body.
- Action: Chapter_1_Introduction_CN.docx delivered in simplified Chinese;
  later chapters follow in Chinese; the TOC stays English.
- Status: EXECUTED for Chapter 1; remaining chapters DEFERRED.

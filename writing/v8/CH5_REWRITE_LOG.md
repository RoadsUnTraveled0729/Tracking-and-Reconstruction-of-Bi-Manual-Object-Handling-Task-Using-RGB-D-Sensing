# Chapter 5 rewrite log (2026-09-06, v8)

Chapter 5 (Pose Recovery During Tracking Failure) rebuilt by
scripts/build_ch5.py for supervisor round 4 (comments C22-C28 in
PROF_COMMENTS_ROUND4.md) on the user's plan sent to the supervisor the
same day. Baseline: writing/v7/scripts/build_ch5.py at commit b59af8e.
Review reports: writing/reviews/Chapter_5_v8_round*.txt.

## Comment mapping

- C22 readability in the user's voice: every paragraph redrafted; the
  drafting-voice sentences of V7 ("The object cannot do more than
  this", "Continuity settles it", "One bookkeeping step separates the
  frames involved") are gone or rewritten. Sample: Chapter 2 sections
  2.3-2.5; rules: writing/WRITING_SKILL.md plus P1-P3.
- C23 schematic for (5.1) and (5.2): Figure 5.3 directly under equation
  (5.2), two panels (read-off on a clean frame in world and object axes;
  the offset carried to a later frame). The old two-panel grip figure is
  split: its state machine is Figure 5.4 alone.
- C24 define every variable: Table 5.1 (Table 5.3, then 5.2, until 2026-09-06) at the head of Section 5.3 and
  first-use definitions. The direction memory is now written as
  equation (5.5) with its gain alpha, which V7 only mentioned in prose.
- C25 offset unknown in general: one paragraph in Section 5.3 before
  equation (5.1), with the pointer to the Chapter 7 comparison.
- C26 fit with Chapters 3-4: the case list at the chapter opening (Case
  A, B, C in the words of the Chapter 3 chain, with L1, L2, o, R_obj),
  equation (5.6) for Case A, and the rebuild boxes of Figure 5.1.
- C27 flow diagram: Figure 5.1 (make_ch5_flow_fig.py) in the style of
  Figure 3.1. The V7 pipeline figure (old Figure 5.5) is reduced to
  the three-state strip, Figure 5.6.
- C28 assumptions and parameters: Section 5.1 with six assumptions and
  Table 5.1 (parameter, symbol, value, how obtained, section). Every
  value is the one printed in V7 or in the source comments of the V7
  build script; the code sources are named in comments beside the
  table.

## Decisions taken (round 4 D1-D5)

- D1: Section 5.5 torso repair PARKED (CH5_PARKED.md, verbatim) on the
  user's plan item 3. With it: equations (5.12)-(5.23) and Figure 5.4
  of V7, the reach inequality (5.6) of V7 and its paragraph, and every
  torso-repair sentence in the opening, 5.2 and 5.6.
- D2: not a Chapter 5 matter; open for the user (Chapter 2 filtering
  step or Chapter 9 limitation).
- D4: the two torso detectors stay in the Section 5.2 prose and Figure 5.2 as a
  report on the torso assumption; Section 5.2 says the torso mask is
  reported and not acted on. Reversible in one paragraph.
- D5: the opening no longer says "in a two-handed task the two hands
  meet during a handover"; Section 5.3 keeps "a handover is two grip
  episodes that overlap" as a general statement of the method.

## Transition from Chapter 4 (user direction 2026-09-06)

The opening paragraph starts from the two products Chapter 4 ends with
(the cleaned object track: a measured world pose of the cube or a
marked gap) and from the Chapter 3 assumption of eight measured
landmarks, and places the chapter between the filtering of Chapter 2
and the solve of Chapter 3.

## Symbols (one meaning per letter)

- d (offset observation, V7 5.2) -> h_k, the observation of h on frame k.
- alpha: defined at equation (5.5); V7 used it at (5.16) only.
- u-hat: the upper-arm direction memory (kept, Figure 5.5 draws it);
  f-hat: the forearm direction memory (new, equation 5.6).
- s: the turn about the shoulder-to-wrist line (kept; the shoulder
  midpoint and shoulder line that also used s left with Section 5.5).
- w: the wrist estimate from the object (kept; the pair width w left
  with Section 5.5).
- c: the offset gain (kept; the principal point c left with 5.5).

## Equation and figure numbering, V7 -> V8

Equations: 5.1-5.4 unchanged; 5.5 direction memory (new); 5.6 Case A
wrist (new); 5.7 = V7 5.5; 5.8-5.12 = V7 5.7-5.11; V7 5.6 and
5.12-5.23 parked. Figures: 5.1 flow (new); 5.2 detectors = V7 5.1;
5.3 offset schematic (new); 5.4 holding state = V7 5.2(b); 5.5 IK =
V7 5.3; 5.6 states strip = V7 5.5 reduced; V7 5.4 parked. Tables: 5.1
parameters (new); 5.2 detectors = V7 5.1; 5.3 notation (new); 5.4
joint groups = V7 5.2.

## Content checks

- Every design value in Table 5.1 and the prose matches the V7 build
  script and its named code sources (grip_state.py, carry.py,
  recovery_core.py, occlusion_ext.py, detect_failures.py).
- Equation (5.5) matches _learn_dir (exponential average, gain 0.3,
  renormalised); equation (5.6) matches _try_recover over ARM_SEGS
  (child = anchor + L * memory, horizon 45 frames); the Case B before
  Case A priority matches the solve order in occlusion_ext.py.
- Method only: no accuracy numbers, fire counts or frame numbers.
- Banned-pattern sweep (writing/v7/scripts/style_sweep.py patterns)
  over the build script: no hits in prose (headings and table cells
  excepted).

## Review rounds

(appended below as each round closes)

### Round 1 (writing/reviews/Chapter_5_v8_round1.txt, 56 findings)

Applied: the unnamed-tolerances clause dropped (5); "serves as" -> "is"
(8); the rigidity statements matched to the four detectors (10); the
detector paragraph and the Figure 5.1 paragraph reshaped, five short
paragraph openers varied (11); four passive sentences made active (13);
the conditioning note stated directly (28); "starting material" saying
replaced by the claim (32); nine long sentences split (captions of
Figures 5.2 and 5.5, the five holding conditions, the minimiser
argument, the constrained-state list, the degenerate case, the
carried-state paragraph); "entry back-dating" -> a verb; "Two limits"
and "The fourth" (P2); the duplicated "no fit on recovered frames" rule
kept once, as the rule of the fits in Section 5.6 (P3); vocabulary:
proximal/distal, limiter/clamping, accumulator/moving average, person
tracker, indivisible, orphaned, bookkeeping, "in force" replaced.
GLOSSARY.md gains hand-object offset, failure mask, mask cleaning,
source flag, least squares, law of cosines, clip.

Declined (thesis conventions, unchanged across chapters): title-case
headings (17; the TOC and every chapter use them); "the solve of
Chapter 3" as a noun (Chapters 2 and 3 in v8 use it; the glossary
"kinematic solver" names the component); Canadian -ise spellings
(minimising, recognised, minimiser: the user's own Chapter 2 text
spells organised, levelled).

### Round 2 (writing/reviews/Chapter_5_v8_round2.txt, 22 findings)

Applied: the two torso detectors back in one sentence each with the
detector as subject; the Figure 5.2 caption, the law-of-cosines
sentence and the circle-basis sentence split (V6); "rigid map" ->
"rigid body transformation" / "fixed transformation" (V1); the
"not invented", "invented position" and "not of the data" clauses cut
(P3). GLOSSARY.md gains gain (filter sense), first-order recursive
update, ill conditioned, depth window.

Declined: title-case headings (17, convention); "the solve", "the fit"
and "the hold" as nouns (standard usage; the glossary names the
component kinematic solver and the state held).

### Round 3 (writing/reviews/Chapter_5_v8_round3.txt, 16 findings; loop closed)

Applied: the three "It is ..." sentences merged into one list (11);
"the tracker" -> "the landmark detector" (11); the Section 5.1 opener
no longer restates the heading (29); "the four" -> "the four inputs"
(P2); "closed-form minimiser" -> "minimises, in closed form"; three
sentences split (the torso assumption, the episode restart, the
episode ends); "grip machinery" -> "the holding state". GLOSSARY.md
gains recovery layer.

Declined after round 3 (recorded for the author): title-case headings
(17, thesis convention); "the solve of Chapter 3" as a noun (Chapters 2
and 3 use it); the three parallel "A group is measured / held /
constrained" definitions kept as deliberate parallel definitions.

Final verdict after three rounds: FAIL by the reviewer's count, with
the remaining flags all in the declined list above. Sentence mean about
18 words (the user's Chapter 2 sample: 16.4); no number-led sentence;
no dash.

Lists and tables pass (2026-09-06, user's plan, draft for the user's
preview, no reviewer round): the chapter had four tables and two lists
against three tables and three lists in Chapter 2, one table in Chapter
3 and none in Chapter 4. Kept: Table 5.1 parameters (C28) and the
notation table (C24), renumbered Table 5.3 -> 5.2. Cut: the detector
table (V7 carry-over; its five thresholds now sit in the Section 5.2
prose and in the Table 5.1 thresholds row) and the joint-group table
(V7 carry-over; now three sentences of Section 5.6). The Case A-C list
became prose in the opening paragraph and the six assumptions became
two paragraphs of Section 5.1. C26 anchor changed from "three cases:"
to "three cases."; the C24 anchor now names Table 5.2. Every reference
resolves; 87 build items.

Second pass on the user's plan (2026-09-06, after the preview): the
parameter table became one paragraph in 5.1 (calibrated constants,
design values, fitted states; every value stays where its equation is
introduced); the three output states are defined in the chapter
opening; the twist hold and the rate limit close Section 5.5; Section
5.6 Output States, Figure 5.6 and the two closing paragraphs on offline
inputs were removed (evaluation matter, Chapters 7 and 8); the notation
table is now Table 5.1, the chapter's only table, as in Chapter 3. New
Section 5.6 Worked Example in the form of Section 3.5: rail recording
frame 560, ten frames into the right-wrist window that starts at 550,
Case B wrist by (5.7) and Case C elbow by (5.8)-(5.12), numbers from
writing/v8/scripts/ch5_worked_example.py, which re-runs the pipeline
and re-derives every value by hand (agreement below a millimetre; no
Case A frame exists in either recording). Figures 2.3 and 3.1 were
made consistent with the chapter (recovery between filter and solve).

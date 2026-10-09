# Defence deck: why the 2026-09-29 Codex decks were discarded, and the restored-deck review

Verified: 2026-09-29. Status 2026-10-06: history; both decks discussed here were replaced by the
author's final deck (deck_inventory.md); the generator files it names (talk_content.json and the rest) were deleted in 3dbd345, recover at 85078c9.
Sources: the master's session scratchpad files DEFECT_REGISTER.md (defect
register of the discarded 105-page deck, rendered 2026-09-29 16:51; three
independent page-by-page reviews of preview/slide-001..105.png) and
RESTORED_DECK_REVIEW.md (three independent page-by-page reviews of the
restored 53-page deck plus the master's reading of pages 2, 3, 35, 37, 39);
presentation/defense_2026/review/RESTORE_2026-09-29.md; D-244 in
presentation/defense_2026/DECISIONS.md. The two scratchpad files are
temporary; this file is their durable copy. The restored-deck part (b) is
copied unchanged from RESTORED_DECK_REVIEW.md; the numbers in it are not
re-derived here.
Answers: why the argument-led and 66+39 decks were dropped, which defects the
discarded 105-page deck had and what caused them, and what a review of the
restored c5440c4 deck (39 main + 14 hidden, 1785 s = 29:45) found.

Context: D-244 restored the deck to c5440c4 because the author judged 66 main
pages far too many and the professor's structure feedback was already applied
there. The discarded work is in git history a202509..ddfdf40 and is not
repaired. Severity in the register: HIGH = unpresentable, MEDIUM = noticeable,
LOW = cosmetic. Category numbers: 1 overflow/clipped, 2 overlap, 3 media size or
placement, 4 placeholder or internal identifiers, 5 unreadable size, 6
heading/wrap, 7 table, 8 footer/page number, 9 process wording, 10 other.
Slide numbers in (a) refer to the discarded 105-page numbering, not to the
current deck.

## (a) Discarded 105-page deck: shared causes and per-slide defects

Result of the three reviews: five HIGH (unpresentable) pages, 28, 35, 43 and
53 among the main slides and 79 among the hidden ones, plus the MEDIUM and LOW
defects listed below. presentation/defense_2026/README.md records that the
discarded deck "renders broken on about 64 pages"; that count is the
author's and master's, not recomputed here.

### Shared causes (from restoration_layout.py and build_deck.py of the discarded deck, read in full)

- caption() line 193 and rows() caption at fixed y=6.29: two-line
  18 pt captions end at about 6.88, on the rule at 6.94.
- movie() line 197: label "Recorded camera / Unity replay" at y=1.05
  over media at y=1.22 for ids 28, 43, 53 with viewport
  [336,64,1104,1188]; filter_page and [26,30] branches mask the poster
  sidebar with black boxes and hand-place labels.
- page() schematic branch line 249: fixed band height (80 or 100 px)
  does not cover the title band on 35; caption plus the hard-coded
  "Logical operation; animation timing is illustrative." label.
- B.restrained_equations(slide,s,equation_start_y default 4.55): fixed
  start under three bullets on 17-20.
- context() line 162: 4.13 x 0.99 in black boxes over the photo.
- pipeline() line 100: last label at bottom+1.27 lands on the rule on 55;
  return connector at x=12.91 outside the 6.22..12.83 column.
- rows() line 68: column widths for the 4-column case wrap "Model cm".
- build_deck.py restrained_page recording_plan branch (about line 2207):
  hard-coded "Recording needed: complete live session".
- Footer text from talk_content.json source_label fields (for example
  line 1736 "Section 5.2; ", line 3584 "Final V9 Tables 7.1-7.2",
  lines 2779-3122 "source-verified schematic").

### Per-slide defects (every slide number and defect kept)

#### Main slides 1-66 (discarded numbering)

- 2 Presentation outline: outline numbering (1-8) differs from the divider
  chapter numbers (2, 3, 5, 6, 7, 8, 9, 10). AUTHOR CALL, not changed.
- 3 Motivation: caption under the table sits on the footer rule (2, LOW);
  caption larger than table text.
- 5 Research question: right column repeats "Research question" as a
  sub-label (6, LOW); two unconnected boxes with large empty bands above
  and below (4/10, LOW).
- 6 Offline pipeline: footer "Adapted from final V9 Figure 8.1" (4/9,
  MEDIUM); "Object support" label floats close to connectors (2, LOW).
- 8 Calibration: equation smaller and isolated (5, LOW).
- 9 Landmark acceptance: status lines under the video and landmark labels
  in the frame unreadable (5, MEDIUM); video small and off-centre with
  empty space, orphan "X Y Z" legend (3, LOW); caption touches footer
  rule (2, LOW).
- 10 Hampel: footer "synchronized recorded-data illustration" (9,
  MEDIUM); floating "Cross: rejected" / "Shared pauses" labels left of the
  thumbnail over a black mask (10, MEDIUM); small "Frame 549 / 18.313 s"
  and "Right wrist; offline output" (5, LOW); caption touches rule (2, LOW).
- 11 Short-gap filling: same footer and floating labels as 10 (MEDIUM);
  caption says "Recorded wrist depth" but the chart axis is "Camera x (m)"
  (10, MEDIUM).
- 12 Butterworth: same footer wording; floating "Recorded camera / Shared
  pauses" labels (MEDIUM); small frame/time text (5, LOW).
- 13 Hip-depth ambiguity: footer "raw R6b frame 533" (4, MEDIUM; R6b is a
  recording name, AUTHOR CALL); caption cross-reference "raw observations
  on slide 52" (9, LOW).
- 15 Camera and Camera-prime: axis diagrams small with large empty column
  (3, LOW); equation font differs (5, LOW).
- 16 T-pose reference: embedded "Thesis Figure 3.5" thumbnail tiny and
  unreadable (3/5, MEDIUM); schematic annotations small (5, MEDIUM).
- 17 Torso frame: equation block starts directly under the third bullet
  with no gap and runs to the footer area (2, MEDIUM); right-column panel
  text about 8 pt (5, MEDIUM); caption touches rule (2, LOW).
- 18 Shoulder swing: equations butt against last bullet (2, MEDIUM); panel
  text tiny (5, MEDIUM); skeleton lines run off the bottom of the camera
  panel (3, LOW).
- 19 Shoulder twist: same as 18 (equations, tiny panel text).
- 20 Elbow: same as 18.
- 21 Object pose: equation small, different font (5, LOW).
- 23 Output states: footer "Section 5.2; " with a stray semicolon (8,
  MEDIUM; talk_content.json source_label); headerless table with very
  tall rows and a large empty bottom (7, LOW).
- 24 Holding context: status lines and overlay labels too small (5,
  MEDIUM); same frame as 9 (LOW).
- 25 Grasp offset: code-style names "MappedMarker coordinates",
  "p_wr - o_k", "h_k (object-local)" visible (4, MEDIUM; AUTHOR CALL for
  MappedMarker); "Measured on R7 frame 630, illustrative", "Single-frame
  values; not a thesis result" (4/9, MEDIUM); small grey notes (5, LOW).
- 26 Offset retention: floating "Input axes / Object axes / X Y Z" legend
  left of the video over a black mask (10, MEDIUM); x/z plot small and
  cramped (3, LOW); caption touches rule (2, LOW).
- 27 Object-derived wrist target: "MappedMarker" in equation (AUTHOR
  CALL); small annotation text (5, LOW).
- 28 Wrist-loss context: HIGH. "Recorded camera / Unity replay" label
  drawn over the top of the RGB image (2); stray "r" glyph left of the
  image at about x=705, y=200 of 1200 (10, MEDIUM); the two stacked images
  have different widths, misaligned, unused space (3, MEDIUM); footer
  "Fresh same-frame RGB/Unity replay" (9, MEDIUM).
- 30 Circle of possible elbows: floating "Input axes / Object axes / X Y Z"
  legend as on 26 (10, MEDIUM); caption breaks "Camera-" / "prime" (6,
  LOW); "Endpoint constraints alone" line and its sub-line misaligned
  (2, LOW); footer "| schematic".
- 32 Selecting one elbow: first bullet breaks "Camera-" / "prime" (6, LOW).
- 33 Direction-memory fallback: notes "Deliberately masked legacy
  recording", "No experiment-frame map; no inferred axes added" (9/4,
  MEDIUM); orphan "X Y Z" legend (10, LOW); notes tiny (5, LOW).
- 35 One frame through the system: HIGH. A row of stray tick marks and
  fragments above the video at about y=130 of 675 (incompletely masked
  title band) (4/10); "Shared RAM" box empty and "RGB-D" sub-box with an
  empty second cell (3, MEDIUM); "timing is not a latency measurement"
  and footer "| schematic timing" (9, LOW).
- 36 One capture, two readers: right caption wraps to two lines close to
  the footer rule and sits lower than the left caption (2, MEDIUM);
  "Shared source retained", footer "source-verified schematic", caption
  "Logical operation; animation timing is illustrative." (9, MEDIUM);
  "Person"/"Object" labels sit on the bottom border of their boxes with
  the top half empty (10, LOW).
- 37 Derived pose records: box text pinned to the top of each box, lower
  half empty; "New output time and publication sequence" floats between
  boxes (10, LOW); footer "source-verified schematic" (9, LOW).
- 38 A common render time: right caption second line nearly touches the
  rule; left and right captions at different heights (2, MEDIUM);
  process wording as on 36 (9, LOW).
- 39 Python publication: box labels pinned to top (10, LOW); footer
  wording (9, LOW).
- 40 Unity read verification: "If retries fail" floats above two boxes
  with no link; no arrows; "Old Pose" wraps (10, MEDIUM); captions
  crowd the rule and are misaligned (2, MEDIUM); process wording (9, LOW).
- 41 Mapping into Scene: three large black label boxes cover about half
  the photo including the person and a marker; text at the top of each
  box with the rest empty (3, MEDIUM); equation noticeably smaller than
  body (5, LOW).
- 42 Rig application: equation sub/superscripts very small (5, MEDIUM);
  label boxes cover the model's torso and part of the object, same empty
  lower half (3, MEDIUM).
- 43 Integrated reconstruction: HIGH. "Recorded camera / Unity replay"
  drawn over the top edge of the camera photo (2); "Same recorded source
  frame" caption much smaller than other text (5, MEDIUM); two images of
  different widths stacked with no gap, lower caption nearly touches the
  rule, lower-left half of the slide empty (3, MEDIUM).
- 44, 54, 59, 63 dividers: no page number (consistent, probably intended).
- 45 Object reconstruction: chart axis has only a "0" tick (3, LOW);
  "Tape: 3.5-37.5 cm" sits in the legend row like a third entry (10, LOW).
- 46 Endpoint reference table: footer "Final V9 Tables 7.1-7.2" (4/8,
  MEDIUM); header "Model cm" wraps to two lines (7, LOW).
- 47 Model and rendered rig: legend "Model" / "Rendered rig" has no colour
  swatches while 45 has them; grey and white bars distinguished only by
  text colour (3, MEDIUM); axis only "0" tick; "Reference: accepted raw 3D
  wrists" crowded against the rule (LOW).
- 48 Joint-results table: large empty gap between table and caption (LOW).
- 49 Controlled landmark removal: caption runs to the right margin close
  to the rule (2, LOW); "R7 right arm" (AUTHOR CALL).
- 50, 51 Right/Left-arm recovery: bottom-right caption indented
  differently from the caption above it (10, LOW).
- 52 Landmarks on an occluding surface: L11/L12/L23/L24 tags (probably
  intended, LOW).
- 53 Imperfect handover replay: HIGH. "Recorded camera / Unity replay"
  overlaps the top edge of the photo (2); stray lone "r" glyph left of the
  upper photo at about x=705, y=200 of 1200 (4); small "Same source frame
  in both views" (5, MEDIUM); "separate accuracy evidence", "remains
  qualitative evidence", footer "Fresh same-frame RGB/Unity replay" (9,
  MEDIUM).
- 55 Real-time pipeline: final label "Unity: mapped scene and rig" sits on
  the footer rule (2, MEDIUM); footer "Final V9 Figure 8.1; Sections 6.1,
  8.2" (4/8, MEDIUM); "Object support" floats; right return connector runs
  outside the box column near the margin (10, LOW).
- 56 Causal processing: "Forward/backward filter" row taller than the
  others (7, LOW).
- 57 One Euro: floating "Recorded camera" / "Shared pauses" labels beside
  the photo (10, MEDIUM); "Frame 179 / 5.972 s" and "Right wrist; causal
  output" much smaller (5, MEDIUM); footer "| causal reprocessing" (9, LOW).
- 58 Replay timing: caption "900-frame rail replay; Appendix B
  workstation." sits against and overlaps the table's bottom rule (2,
  MEDIUM); no footer source label (8, LOW).
- 60, 61, 62 results and limits: footers "Final V9 Sections 7.2, 9.1",
  "Final V9 Section 7.3; Table 7.4", "Final V9 Section 7.4; Tables
  7.5-7.9" (4/8, MEDIUM); heading "Where the evidence stops" (9, LOW);
  62 awkward wraps "11.4 / -> 5.2 cm" and "13.1 / cm, n=16" (6, LOW);
  bottom 40 percent of 60 empty (LOW).
- 66 Question: singular (AUTHOR CALL).

#### Hidden slides 67-105 (discarded numbering)

- 67 Technical appendix: "Type a slide number to open it." shown to the
  audience (9, LOW).
- 69, 70: "Model cm" header wraps (7, LOW); 70 bottom half empty (LOW).
- 71 Controlled removal: caption "cm; higher-motion window 557-601; n=45."
  starts lowercase with raw frame numbers (4, LOW); left column empty
  below the bullets (LOW).
- 73 Two-link reconstruction: top equation shows "cos j" where an angle
  symbol is expected, apparent font fallback (10, MEDIUM); "Camera'"
  superscript prefix on every symbol clutters (5, MEDIUM); "Shoulder" and
  "Wrist target" labels well below their points (3, LOW); caption second
  line just above the rule (1, LOW).
- 74 Grasp-offset update: MappedMarker, "p_wr - o_k", "h_k", "Measured on
  R7 frame 630" (4/9, MEDIUM; AUTHOR CALL on the names); second equation
  breaks leaving "+c ..." alone on a line (10, MEDIUM); inset text small
  (5, LOW); caption tight against the rule (1, LOW).
- 75 Torso preparation: first column header repeats the slide title (6,
  LOW); large empty area between table and caption (LOW).
- 76 Coordinate transforms: MappedMarker/MappedCamera names (AUTHOR CALL);
  equation block very dense, bottom matrix reaches about y=597 of 675
  close to the footer (5, LOW); caption wraps down to the rule (1, LOW).
- 77 Record fields: box text pinned to the top of each box; floating "New
  output time and publication sequence"; thin bracket connector (3, LOW).
- 78 Solver verification: no source footer unlike neighbours (LOW).
- 79 Live-camera validation: HIGH. Placeholder "Recording needed:
  complete live session" bottom left (4); caption "Proposed complete
  live-camera session; not yet validated." reads as a process note (9,
  MEDIUM); the two captions sit at different heights (6, LOW).
- 80 Savitzky-Golay, 81 Median: floating "Recorded camera" / "Shared
  pauses" labels (4/9, MEDIUM); Input and Output lines lie on top of each
  other so the filter effect is invisible; identical poster and chart on
  80, 81, 98, 99, 100 (3, MEDIUM); 80 duplicates 99 and 81 duplicates 100
  by title (AUTHOR CALL).
- 82 Original frame overview: tiny burned-in label "R6b rail task:
  recorded RGB, no overlays" (4/5, MEDIUM); caption "Original task
  recording; later supporting film." (9, LOW); large empty band above the
  footer (LOW).
- 83 Recovery guards: caption "see the source notes" (9, LOW); caption
  second line touches the rule (1, LOW).
- 84 RGB-D back-projection: labels placed loosely, "Calibrated viewing
  ray" floats below the ray, "Image pixel" at the bottom of the
  image-plane line (3, LOW).
- 85 Root-angle derivation: caption white where others are grey (LOW).
- 86-91 Rail/Handover frames: caption second line touches the footer rule
  on 86, 88, 89, 90 (1/2, MEDIUM); both images small with the left column
  empty below the bullets on all six (3, LOW); identical bullets on all
  six (6, LOW).
- 92-105 later backups: repository or code paths in every footer
  ("knowledge/marker_literature.md", "experiments/marker_bench/
  summary.csv", "experiments/transport_bench/results.csv",
  "results_package.csv", "v1/mediapipe/filter_landmarks.py",
  "knowledge/references.md"; on 102 and 103 two paths run almost into the
  page number) (4, MEDIUM; AUTHOR CALL, present since round 4).
- 93: chart legend and annotation box too small (5, MEDIUM).
- 94: "No (v1 fallback)" (9, LOW); UDP loss 4.55 percent versus "lost 528
  of 1000" on 95 (UNCERTAIN, AUTHOR CALL).
- 96-101 filter pages: "Shared pauses" label (9, LOW); 96 and 98 caption
  wraps to the rule (1, LOW); 97 and 100 caption centred while
  neighbours are left-aligned (6, LOW); 98-100 identical chart (3,
  MEDIUM); 99 duplicates 80, 100 duplicates 81 (AUTHOR CALL).
- 102, 103: chart tick labels, legend, bar values and scatter annotations
  small (5, MEDIUM); 103 "85 ms" and "142 ms" labels sit on the curves
  (2, LOW); "R6b" in captions (AUTHOR CALL).
- 104, 105 References: citation text about half the size of the key
  column, too small for a projector (5, MEDIUM).

## (b) Review of the restored 53-page deck (c5440c4 bytes), 2026-09-29

Three independent page-by-page reviews of preview/slide-01..53.png plus the
master's own reading of pages 2, 3, 35, 37 and 39.

Result: 0 HIGH (unpresentable) pages. Professor's instructions (relayed
2026-09-29) all MET: page 2 "Presentation outline" describes the logic of
the talk, not thesis chapters; page 3 "Motivation" opens the Introduction;
no thesis-structure map exists; page 34 divider "Chapter 9 / Discussions",
page 35 "Discussions"; page 36 divider "Chapter 10 / Conclusions" over
Limitations (37) and Contributions (38); Questions (39).

MEDIUM findings (all present in the accepted round-6 deck; none changed;
optional follow-ups for the author):
- Producer labels burned into the films and their side columns: "p06 |",
  "p09 - Smoothing", "p13 |", "p15 |", "p16 |", "p23 |", "p25 |", "p29 |",
  "p32 |", "p33 |", "p41 |", "p47 |", "p49 -", "p07/p08/p67/p68" on the
  hidden filter pages, "Shared pause", "L24: omitted", "Object:
  MappedMarker", "R6b rail task" on page 5. Changing them means
  regenerating the films (media bytes are pinned by the media contract).
- Side-label text inside the analysis panels on pages 12-14, 19-20, 24,
  25, 31, 35 is about 9-10 px at 1200 px width; unreadable on a projector,
  but the spoken numbers are repeated in the bullets.
- Page 8 header "Accepted body landmarks" over a frame whose status lines
  say "Torso geometry: rejected"; the same frame 705 appears on page 18.
- Page 23: the frame diagram is a mid-animation frame with an empty
  "Shared RAM" box (static poster of an animated film).
- Page 27 bar categories Carry/Lift/Slide versus page 28 rows W1-W2/W2-W3/
  W3-W4 for the same numbers.
- Page 30 title "Right-arm tracking failure" while the page also shows the
  left-wrist case.
- Page 35 reuses the page-31 handover film (D-209, deliberate).
- Page 39 closing page: first bullet repeats the heading "Questions", and
  "Questions and discussion" floats mid-right.
- Hidden pages 41, 50, 51: chart legends and annotations about 10-11 px.
- Filter plots on 44-48: the Input line is hidden under the Output line.

LOW findings: two-line captions close to the footer rule (3, 12, 16, 19,
21, 23, 24, 29, 31, 35, 44, 46, 47, 50, 51); divider titles in sentence
case versus Title Case chapter labels; dividers carry no page number;
footer paths on hidden pages 40-41, 50-53 (round-4 design); "n 45 frames"
on page 29; "->" arrows and "33.3 / ms" wraps.

## (c) Lessons

1. Fixed-type layouts with no fit check: text, equations and captions were
   placed at fixed sizes and positions (equation start y, fixed column
   widths, fixed caption y) and nothing tested whether they fit, so text
   overflowed, wrapped or collided on many pages.
2. Black mask boxes over media with hand-placed labels: the film sidebars and
   photo areas were hidden with black boxes and re-labelled by hand, which left
   stray glyphs, floating legends, half-covered photos and label text drawn over
   the media.
3. Fixed caption y hit the footer rule: caption() and the table-rows caption
   placed two-line 18 pt captions at a fixed y=6.29 in, which end at about
   6.88 in against the footer rule at 6.94 in (the register's shared cause);
   the restored deck shows the same near-rule captions on 15 pages, rated LOW
   in (b).

## Open items

- The 134-question committee bank kept from the discarded work still points to
  the discarded slide numbering (COMMITTEE_QUESTIONS.md line 20 says the numbers refer to
  the 66-main/39-hidden deck; review/qa_revision/slide_rebinding_audit.json
  and slide_rebinding_audit_m3.json also record bindings to discarded decks,
  the first to a 38+14 deck). See thesis_outline.md.
- The register's AUTHOR CALL items (MappedMarker names, R6b recording names,
  outline numbering, duplicated filter pages, footer paths, UDP loss 4.55
  percent versus "lost 528 of 1000") were not decided; they concern content the
  restored deck also carries in part (hidden pages 40-41, 50-53 footer paths
  and the MEDIUM list in (b)).
- PowerPoint playback on the defence machine, projector legibility and an
  aloud rehearsal are unverified (D-244).

# RETIRED (history): FOCUSED revision inventory, files deleted 2026-10-06

Status 2026-10-06 (Verified 2026-10-06): the FOCUSED pptx and script, the build
chain they were back-ported into (build 77) and review/round11_focused/ were
deleted in 3dbd345 (D-382); recover at 85078c9. The author's later deck
(Thesis_Defence_2026.pptx, D-381, adopted 2026-10-06) replaced all of it, so none of
the counts below describes a current file. The current deck is described in
deck_inventory.md. Kept as the record of the round-11 comparison.

## FOCUSED defence deck revision: inventory against build 74 (round 11, M1; retired)

Verified: 2026-10-01 (repository master 0e9fe81 for the M1 measurements; the
Outcome section below at master 88878cd, build 77).

Sources: presentation/defense_2026/Thesis_Defence_2026_FOCUSED.pptx (sha256
703545b5c781cd8a0fb36e6466c8b5405ee686e1fc53daca1a16ac114b5114dd),
presentation/defense_2026/DEFENSE_SCRIPT_FOCUSED.md (git blob 80777293db3c...),
build 74 = presentation/defense_2026/Thesis_Defence_2026.pptx at 0e9fe81 (sha256
bd4ed712...), talk_content.json, backup_content.json, validate_deck.py and
set_page_budgets.py at 0e9fe81; outputs in
presentation/defense_2026/review/round11_focused/.

## What the FOCUSED pair is

The author's hand edit of the build-74 deck and script (D-340). Same 76 slides,
order, media, masters and theme. The author decided the content is back-ported
into talk_content.json / backup_content.json and the deck rebuilt (round 11);
that was done in build 77, see Outcome.

## Outcome: back-ported in build 77 (verified 2026-10-01, master 88878cd)

Sources: presentation/defense_2026/review/round11_focused/{EQUIVALENCE.md,
RENDER_COMPARE.md, RULE_FIXES.md, rule_fixes.json, build_rule_fixes.py},
review/ARTIFACT_CHECK.json, DECISIONS.md D-359 to D-369, PROJECT_STATUS.md row 77.

- Back-port: titles, visible text, cues, narration and the hidden set were
  written verbatim into talk_content.json, backup_content.json and the new
  script_document.json by review/round11_focused/apply_backport.py (D-359),
  including the caveats the author removed and the four claims marked STRONGER
  THAN SOURCE or NOT SUPPORTED (pages 33, 35, 36, 41), which are neither
  softened nor restored. Build 77 pptx sha256 8481390b...; the FOCUSED pair is
  unchanged (pptx 703545b5..., md de3e7a77...).
- Equivalence gate (EQUIVALENCE.md, result PASS, compare_decks.py exit 0): 76 of
  76 pages EQUAL against the FOCUSED pptx after 74 allow entries (73 text
  substitutions and 1 geometry tolerance of 1 EMU on page 41, G-01, D-368), 0
  differences outside the allow-list; DEFENSE_SCRIPT.md against
  DEFENSE_SCRIPT_FOCUSED.md: 58 lines differ, 58 explained by listed fixes, 0
  unexplained, plus 5 script-document fixes (F-73 to F-76, F-78).
- Rendered comparison (RENDER_COMPARE.md, 90 dpi pdftoppm rasters): 68 of 76
  pages pixel-identical to the FOCUSED render; the 8 that differ (3, 23, 28, 32,
  35, 36, 39, 41) differ only in the rows of strings changed by F-22, F-29 to
  F-32, F-70 to F-72 and F-77. Page 2 is identical.
- Validator: 2092 checks, 0 package failures, status PARTIAL only for D-058 and
  D-066; total 1895 s = 31:35, 100 s over the 1795 s cap (recorded override,
  D-364); 3943 script words (FOCUSED 3941).
- Rule fixes applied: the 69 minimal fixes F-01 to F-69 (D-360), plus the
  following four wordings, which replace the author's own text and are all
  NEEDS AUTHOR (RULE_FIXES.md, "Round 11 M3 additions"):

  | ID | Page | Old (FOCUSED) | New (build 77) | Why |
  | --- | --- | --- | --- | --- |
  | F-70 | 41 title | What the evaluation establishes | Findings established by the evaluation | what-clause title (D-263), D-361 |
  | F-71 | 3 bullet | Applications need body and object positions in one metric scene | Body and object positions in one metric scene | over 8 words, D-361 |
  | F-72 | 39 bullet | Replay: each branch under 33.3 ms in 99% of frames | Replay branches under 33.3 ms, 99% of frames | over 8 words, D-361 |
  | F-77 | 32 bullet | Absolute length errors: 0.53 to 2.83 cm | Length errors: 0.53 to 2.83 cm | wrapped to two lines and met the equation strip (D-276 guard), D-362 |

- Caveat on regenerating the fix list: review/round11_focused/build_rule_fixes.py
  (unchanged since M1 commit 15e77b5; grep finds no "F-7", "G-01" or
  "script_document" in it) numbers only its in-script FIXES list as F-01 to F-69
  and writes rule_fixes.json with the keys about, allow, needs_author,
  check_problems and residual_hits_after_fixes, plus RULE_FIXES.md. Rerunning it
  would therefore drop the later entries F-70 to F-72, F-77 and G-01 from "allow"
  (74 entries -> 69), the "script_document" part (F-73 to F-76, F-78) and the
  "Round 11 M3 additions" section of RULE_FIXES.md, and the equivalence gate and
  apply_backport.py would then fail on those strings and on the 1 EMU
  tolerance. It also needs a scratch directory holding the 0e9fe81 validator
  tree (vd/) and rule_screen.json written by make_inventory.py. Treat
  rule_fixes.json as hand-extended; do not rerun build_rule_fixes.py without
  porting the M3 entries into it first.

## Headline counts (measured by compare_decks.py and make_inventory.py)

- Package: no part added or removed; 108 parts differ. Slide XML: 44 identical,
  11 differ only by a dropped empty r:id attribute (pages 8-11, 16-18, 30,
  53-55), 21 differ otherwise; all 76 notes XML differ. So 44 of the 152
  slide and notes parts are identical. Correction: the D-340 statement "55 of
  152 parts identical" does not match this measurement (44).
- Hidden: pages 2 and 3 newly hidden (plus 49-76 as before); their narration is empty.
- Titles changed on 18 pages (3, 4, 5, 22, 23, 25, 27-29, 32-36, 39, 41, 43, 48).
  Visible text changed on 21 pages by shape (2, 3, 4, 5, 22-25, 27-29, 32-36, 39,
  41, 43, 44, 48; titles included): 18 of them with changes other than the title
  (97 item lines in FOCUSED_CHANGES.md) and 3 (5, 43, 48) with a title change
  only (the FOCUSED_CHANGES.md summary line said 18 for the whole class and was
  corrected in the round-11 close-out). Page 2 rebuilt (three 24/18 pt heading and
  grey subline pairs, unnamed shapes); page 41 lost six dash shapes, boxes moved,
  17 pt sublines. Media unchanged on every page (part hashes and geometry).
- Notes pane on all 76 pages: cue line(s), say lines, one Sources line; pages 17,
  23, 44 carry a second cue inside the narration; the builder's other lines are
  gone. Narration changed on 75 pages, cue on all 76 (build-74 cue = presenter_cue).
- Spoken words, visible main pages (1, 4-48): 3941 (build 74: 3647).
- Rule screen with the 0e9fe81 validator functions: 69 minimal fixes proposed
  (15 semicolons, 1 number opening plus '?', 6 en dashes, 5 "Camera prime"
  retired-term hits, 1 page-49 Sources renumbering, 4 bullets over 8 words, 37
  question clauses under D-263), 3 NEEDS AUTHOR (page 41 title "What the
  evaluation establishes", page 3 and page 39 bullets over 8 words).
- Numbers: 0 MISMATCH, 0 NOT FOUND, 4 DERIVED; claims: 3 STRONGER THAN SOURCE
  (pages 33, 35, 41), 1 NOT SUPPORTED (page 36 "hand-cube alignment" bullet).
- Citation first-use order unchanged: [1] p7 ... [8]-[11] p49, [12] p53; rule 6 holds.
- Time (set_page_budgets.py rule, read-only): 1815 s at 140 wpm and 1790 s at
  144 with dividers at 5 s; 1890 s and 1865 s with dividers by words; cap 1795 s.
  The first 11 of 18 ranked cut candidates reach the cap from 1890 s. Dated
  note 2026-10-01 (TIME_ESTIMATE.md): build 77 is 1895 s (pages 17, 22, 25 are
  60, 70, 60 s against 55, 65, 65 s in the estimate), the first 11 cuts save
  95 s (1800 s, still 5 s over the cap), all 18 save 130 s, so a 12th cut
  (page 9, 5 s) is needed.
- Caveats removed: 29 rows on 12 pages. 12 rows have an Elsewhere entry that
  begins with "no" (counted by reading the table; the file said 11): 10 are not
  restated anywhere in the deck and 2 (page 35, left arm) say "no sentence"
  while the numbers stay visible. 5 left-arm rows keep only the numbers (two of
  them are those two).

## Files (presentation/defense_2026/review/round11_focused/)

- compare_decks.py: read-only per-slide comparison and the M3 equivalence gate;
  allow-list format and exit codes (0 / 1 / 2) in its docstring; --self-test.
- dump_b74.json, dump_focused.json: per-slide extraction of both decks.
- FOCUSED_CHANGES.md: all 76 pages old -> new; focused_content.json: target content
  per page with the build-74 field of each visible string (text before fixes).
- rule_fixes.json (allow-list + edit list), RULE_FIXES.md (also md vs pptx).
- CITATIONS.md, NUMBER_CHECK.md, CAVEATS_REMOVED.md, TIME_ESTIMATE.md.
- Generators: make_inventory.py, build_rule_fixes.py, analyze_m1.py,
  write_reports.py (each takes a scratch directory; they read 0e9fe81 blobs).

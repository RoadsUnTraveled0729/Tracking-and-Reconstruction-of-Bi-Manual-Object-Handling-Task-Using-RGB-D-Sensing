## Defence deck checkers after 2026-10-06 (Verified 2026-10-06; totals refreshed 2026-10-08)

Sources: presentation/defense_2026/{build_speaker_script.py, make_package.py,
export_committee_questions.py}, DECISIONS.md D-382, D-383, D-385, D-386,
review/RENDER_RECORD.json. Thesis Python: /home/luo/anaconda3/bin/python -B.

The build, render, validation, budget and effective-text checkers
(build_deck.py, render_deck.py, validate_deck.py, set_page_budgets.py,
report_effective_text.py, export_defense_script.py and the compare_decks.py gate)
were deleted in 3dbd345 with the pipeline (D-382, D-385); the author's files can only
be checked as files (D-383). What exists now, run from presentation/defense_2026:

- `build_speaker_script.py --check`: lints speaker_script.json; expected "total words
  (slides 1-46): 2657", "total seconds: 1620, cap 1620: PASS", "hits: 0"; exit 0
  (checked 2026-10-08).
  Default mode builds the docx; --extract rebuilds the JSON from the docx.
- `make_package.py --render`: LibreOffice (soffice) PDFs of the pptx and the two
  docx files and review/RENDER_RECORD.json (recorded 2026-10-06 pdf_pages:
  deck 77, speaker script 23, outline/Q&A index 2; no new render).
- `make_package.py` and `make_package.py --require-clean`: copy the six files and
  README.txt into package/Thesis_Defence_2026 and write package/MANIFEST.json;
  --require-clean refuses a dirty or untracked input (the six deliverables,
  PACKAGE_README.txt, make_package.py, the render record). It refuses a PDF the
  render record does not describe and a pptx with an external relationship.
- `make_package.py --self-test`: six clean-tree cases, expected PASS.
- `export_committee_questions.py --pdf`: COMMITTEE_QUESTIONS.docx and .pdf from
  review/question_index.json (D-385).
- Still present and unchanged by the retirement: anim/validate_media.py,
  anim/validate_filter_sync.py, anim/validate_matched_sources.py (they read
  review/ and media/ records; validate_media.py was not run on 2026-10-06; some
  provenance paths they read are broken, D-385), the thesis checkers and the
  Unity and recording checkers sections below.

## RETIRED (history): checker commands of builds up to 77

The sections down to "Checker inventory" below describe the retired pipeline
(builds 73-77, deleted in 3dbd345; recover at 85078c9). The "Presentation
checkers" table and the "Package commit metadata" notes are partly retired too:
validate_deck.py and export_defense_script.py no longer exist, and
--require-clean no longer checks build_deck.py or talk_content.json (inputs are
listed above). The D-058/D-066 "accepted findings" belonged to the retired
validator. The /tmp cache notes at the end stay valid for anim/causal_replay.py and
anim/matched_evidence.py.

## Round-11 deck and checker commands (build 77, verified 2026-10-01; retired in 3dbd345)

Verified: 2026-10-01 at master 88878cd. Sources:
presentation/defense_2026/{validate_deck.py, set_page_budgets.py,
build_deck.py, make_package.py, render_deck.py, export_defense_script.py,
report_effective_text.py, equations/derivation_leads.py,
review/round11_focused/{compare_decks.py, equivalence_report.py},
review/ARTIFACT_CHECK.json, review/SCRIPT_EXPORT_CHECK.json,
budget_override.json, DECISIONS.md D-341 to D-369}, PROJECT_STATUS.md row 77,
git log and git diff of validate_deck.py (f5634de, 0e9fe81..HEAD). The
current deck is 46 shown + 2 hidden main pages + 28 hidden topic pages, 1895 s
= 31:35, 3943 script words (deck_inventory.md, round-11 section).

Command sequence of build 77 (thesis Python /home/luo/anaconda3/bin/python,
from the repository root; PY below stands for that interpreter). The order
matters: the budgets must be written before the build (the D-356 check fails
on stale durations), the validator needs the rendered PDF, and the package
needs every report.

1. `PY presentation/defense_2026/set_page_budgets.py --allow-over-cap --write`
   -- rewrites the `duration` of every main page of talk_content.json from the
   narration word counts. --allow-over-cap (D-349) keeps the start rate of 140
   words per minute instead of rising to 144, prints the total and the
   overage, and with --write also writes budget_override.json {decision D-349,
   cap_s 1795, total_s 1895, overage_s 100, rate_wpm 140}. Without the flag a
   total above the cap at 144 words per minute prints FAIL, writes nothing and
   exits 1; with --write and a total within the cap the tool deletes a stale
   budget_override.json (D-352). Without --write it only prints the table.
2. `PY presentation/defense_2026/equations/derivation_leads.py --check`
   -- regenerates the derivation leads in memory and compares them byte for
   byte with equations/derivation_leads.json (validate_deck.py also runs it,
   D-289); PASS at build 77 (PROJECT_STATUS.md row 77).
3. `PY presentation/defense_2026/build_deck.py` -- builds the pptx, SPEAKER_NOTES.md
   (76 sections, D-344), DEFENSE_SCRIPT.md (from script_document.json, D-346)
   and the layout reports; raises on a layout option outside the two author
   layouts (check_layout_options, D-355) and on a hidden flag that is not a
   boolean on a main page (D-341).
4. `TMPDIR=<absolute directory inside the repository> PY presentation/defense_2026/render_deck.py`
   -- PDF and preview PNGs (76 pages, review/RENDER_CHECK.json). The
   repository-contained TMPDIR is the round-9 and round-10 practice; whether
   render_deck.py needs it was not tested (it uses tempfile.TemporaryDirectory
   with prefix defense-render-, so TMPDIR is honoured).
5. `PY presentation/defense_2026/validate_deck.py --pdf presentation/defense_2026/Thesis_Defence_2026.pdf`
   -- 2092 checks, all PASS, overall PARTIAL only for D-058/D-066, package
   PASS (review/ARTIFACT_CHECK.json, read 2026-10-01); prints a "Time cap:" line.
6. `PY presentation/defense_2026/report_effective_text.py` -- writes
   review/EFFECTIVE_TEXT.md (80 rows; deck_fonts.md).
7. `TMPDIR=<absolute directory inside the repository> PY presentation/defense_2026/export_defense_script.py --pdf`
   -- DEFENSE_SCRIPT.docx and .pdf, 387 paragraphs and 23 PDF pages at build
   77 (review/SCRIPT_EXPORT_CHECK.json). TMPDIR practice as in the round-10
   note below (the script uses tempfile.TemporaryDirectory, prefix
   defense-script-, and an isolated LibreOffice profile).
8. Equivalence gate against the author's FOCUSED pair (round 11 only, not a
   standing checker): `PY presentation/defense_2026/review/round11_focused/equivalence_report.py`
   writes review/round11_focused/EQUIVALENCE.md and exits 0 when the deck and
   the script show no difference outside rule_fixes.json (result PASS, 76 of 76
   pages EQUAL); the deck half alone is `PY .../compare_decks.py
   presentation/defense_2026/Thesis_Defence_2026_FOCUSED.pptx
   presentation/defense_2026/Thesis_Defence_2026.pptx --allow
   presentation/defense_2026/review/round11_focused/rule_fixes.json` (exit 0
   none, 1 uncovered difference, 2 usage error or an allow entry that does not
   apply); `compare_decks.py --self-test` runs its own cases. Rendered
   comparison: review/round11_focused/render_compare.py (informational).
9. `PY presentation/defense_2026/make_package.py --self-test` (six cases in a
   throwaway git repository, D-351) and, after the content is committed,
   `PY presentation/defense_2026/make_package.py --require-clean`. Run for
   build 77 on 2026-10-01: the manifest pins git_commit 7173058 (the round-11
   records commit; 46 shown + 2 hidden main + 28 hidden topic pages, 76 PDF
   pages, 19 embedded MP4, 2092 checks, pptx sha256 8481390b..., total_bytes
   124859377); the manifest is committed as 487e468 and these statements in
   the following commit (the round-10 pattern); do not rerun packaging to
   chase the hash. --require-clean now treats the inputs build_deck.py,
   talk_content.json, backup_content.json, PACKAGE_README.txt and
   script_document.json (and budget_override.json when present, which must be
   tracked) as dirty when `git status --porcelain --untracked-files=all` lists
   them, staged or untracked included (D-351; make_package.py line 211).
   The package README states "<shown> shown main pages, <hidden> hidden main
   pages and <topic> hidden topic pages" and the hidden set from the data
   (D-341, D-353); MANIFEST.json adds shown_main_pages and hidden_main_pages.

Check count: 2092 at build 77 (ARTIFACT_CHECK.json: 2092 entries, all PASS).
History: 2063 (build 68), 2068, 2073 (builds 70 and 71), 2078, 2081 (builds 73
and 74; the round-10 note below), 2085 at commit f5634de (round-11 M2, +4 by
the commit message and the check() diff against 0e9fe81: the D-349 cap check,
the two D-346 script-document checks and the round-11 self-test; the
"complete script", "planned duration" and font-role or palette checks were
renamed or re-pointed, not added), 2092 at build 77 (+7 by the check() diff
f5634de..HEAD: D-354 two, D-355 one, D-356 one, D-357 one, D-358 one and the
review-fix self-test).

New and re-pointed validate_deck.py checks (exact names; D-IDs in
DECISIONS.md):
- D-341 "Slide NN visibility" expects hidden == page_hidden(spec, i, len(talk))
  (flag or position); "Full draft has explicit positive slide budgets" reads
  the shown main pages and requires duration 0 on every hidden main page.
- D-343 "Slide NN notes pane equals its cue and narration blocks and one
  Sources line (D-343)" replaces "Slide NN contains the complete script": it
  rebuilds the pane independently and compares it exactly.
- D-344 re-pointed to the page's SPEAKER_NOTES.md section (the check text
  scans themselves read pane + section, validate_deck.py line 2676): "Slide NN
  speaker notes record the planned duration (D-344)" (replaces "Slide NN notes
  match the planned duration"; the lead line "MAIN TALK | Slide NN | Budget: N
  s", or "HIDDEN MAIN PAGE | Slide NN | Not in main-talk timing" for a hidden
  main page), "Slide NN speaker notes state the overlay mode of every drawn
  frame (D-344)", "Slide NN speaker notes give every lead source and name the
  main slide supported (D-281, D-344)", "Slide NN speaker notes keep the export
  text of every lead shown with [...] (D-286, D-344)", "Every main page with a
  thesis equation strip names its derivation pages in its speaker notes
  (D-281, D-344)", "Closing page speaker notes list every hidden page by slide
  number (D-128, D-344)". So the notes pane no longer carries the "Budget" lead
  (nor Role, Provenance, media lines); it carries cues, narration and one
  Sources line only.
- D-346 "DEFENSE_SCRIPT.md equals script_document.json and the cue and
  narration blocks (D-346)" and "DEFENSE_SCRIPT.md and SPEAKER_NOTES.md are
  ASCII (D-346)"; D-347 "The discussion, limitations and contributions pages
  (legacy keys discussion, 38, 55) cite Chapter 9, Table 9.1 and Section 10.1
  (D-279, D-347)" (found by legacy key, titles free).
- D-349 "Main talk is within the 1795 s cap or a recorded override names its
  total (D-349)" (cap_problem(): over the cap needs an override with the same
  total and cap; an override for an in-cap talk fails, D-352); ARTIFACT_CHECK.json
  main_time_cap {cap_s 1795, planned_s 1895, over_cap true, overage_s 100,
  override_recorded true}.
- D-350 "Slide NN actual XML uses only the fixed font roles (variants: D-350)"
  and "Slide NN native text uses the white monochrome palette (variants:
  D-350)" (variant sizes and colours: deck_fonts.md).
- D-354 "No '**' emphasis marker is left in any notes pane or in SPEAKER_NOTES.md
  (D-354)" and "Every '**' in DEFENSE_SCRIPT.md is a balanced word-boundary
  emphasis pair within its paragraph (D-354)".
- D-355 "title_box, footer and box_style appear only on the heading-pairs outline
  or a bullet_boxes page, and every declared author-layout box is drawn as
  declared (D-355)" (BOX_TOLERANCE_IN 0.005 in).
- D-356 "Every shown main page budget equals the set_page_budgets.py rule applied
  to its narration (D-356)" (plan() imported from set_page_budgets.py, applied
  to the validator's own word count; at the start rate when an override is
  recorded; the override's rate_wpm must equal it).
- D-357 "script_document.json header, Q&A introduction and appendix carry no
  semicolon, retired term, internal recording name or repository path (D-357)".
- D-358 "Every hidden page, hidden main and topic pages alike, has its
  SPEAKER_NOTES.md section and unspoken record (D-358)".
- Self-tests: "The round-11 hidden-flag, pane, pointer, script-document, D-279,
  font-role and cap rules report every bad sample and pass every good sample
  (self-test)" and "The round-11 review-fix rules (D-352 to D-358) report every
  bad sample and pass every good sample (self-test)".
- D-337 (build 74, still current) "No semicolon anywhere in DEFENSE_SCRIPT.md
  (D-332, D-337)": script_doc_semicolons(text) (validate_deck.py line 688) takes
  no exemption; every line of the generated document is scanned, appendix
  included. The D-326 (g) path exemption for derivation lead sources is a real
  one and stays.

Budget rule as it is now (set_page_budgets.py; D-327, D-333, D-348, D-349,
D-356): cover 20 s, each References page 5 s, Thank you 5 s, Question page 10 s;
a chapter divider with narration is budgeted by its words exactly like a content
page (words / rate * 60, rounded up to a multiple of ROUND_S = 5 s, no film
lead; D-348), a divider without narration keeps 5 s; every other page words /
rate * 60 plus FILM_LEAD_S = 5 s on a film page, floored at the embedded film's
ffprobe duration, rounded up to 5 s; hidden main pages get 0 s and stay out of
the total (D-341); hidden topic pages 0. Words are build_deck.narration() (the
tool imports it, D-356): narration blocks only, cues excluded, "**" removed.
Rate RATE_START_WPM 140 (within 131-144 of D-095), rising one word per minute
to RATE_MAX_WPM 144 only while the total exceeds TOTAL_CAP_S 1795 s (the
round-9 total, the author's ceiling) and --allow-over-cap is not given. Result
at build 77 (D-364): 1895 s at 140, 100 s over the cap, recorded override; the
exercise dry run of D-348 gave 1790 s at 141 on the round-10 content. All budgets
are word-rate estimates until an aloud rehearsal (D-348 and D-364 UNCERTAIN).

## Round-10 deck and checker commands (builds 73-74, history, verified 2026-09-30; superseded by the round-11 section above)

At builds 73 and 74 the deck was 48 main + 28 hidden pages, 1755 s = 29:15, 3647
script words (see deck_inventory.md, round-10 history section); the counts,
notes-pane statements and check names below are those builds, not build 77.
Round-10 notes (sources:
review/ARTIFACT_CHECK.json, validate_deck.py, set_page_budgets.py,
PROJECT_STATUS.md rows 68-73, DECISIONS.md D-308, D-311, D-316, D-320 to
D-322, D-326 to D-333):

- validate_deck.py --pdf: 2081 package checks, 0 package failures, overall
  PARTIAL for D-058/D-066 at build 73 (review/ARTIFACT_CHECK.json: 2081
  PASS, none other). Build history of the count (PROJECT_STATUS.md rows
  68-73): 2063 at build 68 (down from 2100 at build 67 after the page
  restructure; the sources do not itemise the difference), 2068 at build 69 (+5: the
  four D-311 wording checks and their self-test), 2073 at builds 70 and 71
  (+5 at build 70; the sources do not itemise them, D-316 changed the overlay
  photo-hash check and D-318 added a seventh overlay, which is the likely
  source, not verified; build 71 left the count unchanged), 2078 at build 72
  (+5: the four D-326 notes checks and their self-test), 2081 at build 73
  (+3: the D-332 self-test, cue check and script-document check).
- D-308 (build 68): CITATION_REQUIRED keys are static_marker_calibration,
  filter_hampel and filter_butterworth, signal_conditioning and
  calibration_landmarks no longer exist (five required pages 7, 9, 11, 32,
  39); the filter-page geometry check reads the film from the page with
  legacy key filter_hampel and also covers the three main filter pages; check
  "The static marker calibration page labels Eq. 2.1 with one line directly
  above it (D-308)"; FILM_MASKS_PX and FILM_GEOMETRY_PX lost p05 and p43 and
  gained p04.
- D-311 wording checks (build 69): (a) no semicolon, (b) no bullet full
  stop, (c) no retired term, (d) no internal recording name or file path,
  on every native text frame, table cell and note, with a self-test check
  "The D-311 wording rules report every bad sample and pass every good
  sample (self-test)".
- D-316 plain-panel overlay check: a coordinate overlay panel with
  background "plain" carries no photo fields and only illustrative frames
  ("Coordinate overlay <name> declares the committed photo hash (plain
  panels: no photo, illustrative frames only)").
- D-320: the page-4 film p04 has no mask; FILM_GEOMETRY_PX keeps it with
  the measured full-frame content [0, 0, 640, 480] and no label, so the
  D-262 binding still covers it; measure_film_geometry.py has no strip
  branch any more.
- D-321: report_effective_text.py selects the exception pages from the deck.
- D-326 notes checks (build 72; the `notes` field only, not the unspoken
  Budget, Sources and provenance lines the builder added to the pane then;
  since build 77 the pane holds no such lines and the scans read the pane plus
  the SPEAKER_NOTES.md record, D-344). Check names:
  "The D-326 notes rules report every bad sample and pass every good sample
  (self-test)"; "No semicolon in the notes of any page (D-326 e)"; "No notes
  contain the tag 'Thesis:' (D-326 f)"; "No notes contain an internal
  recording name (R5, R6, R6a, R6b, R7) or a repository path; derivation lead
  sources exempt (D-326 g)"; "No sentence in the notes of a main page opens
  with a digit or a number word (D-326 h)". NUMWORDS is copied from
  writing/v9/scripts/check_style.py (writing/ is frozen and is not
  imported); sentence splitting at "." or "!" plus white space except after
  Eq., Eqs., al., e.g., i.e., Fig., vs., No., cf.
- D-332 cue and script-document checks (build 73): "The D-332 cue and
  script-document semicolon rules report every bad sample and pass every good
  sample (self-test)"; "No semicolon in the presenter cue of any page
  (D-332)"; "No semicolon anywhere in DEFENSE_SCRIPT.md outside the
  derivation lead sources (D-332)" (every line of the generated document at
  build 73). CORRECTED 2026-10-01: the "outside the derivation lead sources"
  exemption removed only strings that contain no ";", so it was a no-op; D-337
  (build 74) removed it and the check is named "No semicolon anywhere in
  DEFENSE_SCRIPT.md (D-332, D-337)" with script_doc_semicolons(text) taking no
  exemption (validate_deck.py line 688 and line 3782, read 2026-10-01).
  SPEAKER_NOTES.md is not scanned for semicolons (its Sources, Provenance and
  media lines keep ";").
- Existing duration and word checks at build 73 (ARTIFACT_CHECK.json; build 74
  history, build 77 is 1895 s, 3943 words, 64.9 percent and the D-344 name
  "Slide NN speaker notes record the planned duration"): main
  talk 1755 s and 3647 script words, every "Slide NN notes match the planned
  duration" check, and "At least 55 percent of main time explains methodology"
  (63.0 percent, floor 55 percent, D-211).
- set_page_budgets.py (build 72, D-327, D-333): not a checker; it writes the
  `duration` field of the main pages of talk_content.json from the notes
  word counts. Rule: dividers 5 s, cover 20 s, References pages 5 s each,
  Thank you 5 s, Question 10 s; every other page words / rate * 60 (words =
  len(notes.split())), plus 5 s (FILM_LEAD_S) on a film page, floored at the
  embedded committee film's ffprobe duration, rounded up to a multiple of 5 s
  (ROUND_S). Rate starts at 140 words per minute (RATE_START_WPM, within the
  131-144 of D-095) and rises one word per minute up to 144 (RATE_MAX_WPM)
  only while the total exceeds 1795 s (TOTAL_CAP_S, the round-9 total);
  exit status 1 without writing if it still exceeds it at 144. Hidden pages
  stay 0. Command, from the repository root:
  `/home/luo/anaconda3/bin/python presentation/defense_2026/set_page_budgets.py`
  prints the table and `... set_page_budgets.py --write` also writes the
  durations; then run build_deck.py and validate_deck.py. Result at build 73
  (D-333): 1755 s at 140 words per minute. All budgets are untimed until an
  aloud rehearsal.
- export_defense_script.py --pdf: 308 paragraphs, 20 PDF pages at build 73
  (387 and 23 at build 77, above)
  (review/SCRIPT_EXPORT_CHECK.json). Round 10 runs it with TMPDIR set to an
  absolute directory inside the repository and removes that directory
  afterwards (brief requirement). The script has no TMPDIR handling of its
  own (grep, 2026-09-30); a run without TMPDIR was not tested.
- make_package.py --require-clean (round 10, build 74, 2026-09-30): run on
  records commit 8ec851f; package/MANIFEST.json pins git_commit 8ec851f,
  working_tree_differs_from_commit false, 48 main + 28 hidden pages, 76 PDF
  pages, 19 embedded MP4, validator PARTIAL with package PASS, 2081 checks,
  total_bytes 124843391 (pptx sha256 bd4ed712..., pdf 72fb9dbc...). The
  manifest was committed in 6b0ab0e and the pin statements in the commit after
  it (rounds 8 and 9 pattern); do not rerun packaging to chase the hash.
- anim/validate_media.py needs the /tmp/defense_2026_causal cache, which
  is outside the repository; writing it needs the author's approval, so it
  was not run to completion in round 10 (PROJECT_STATUS.md rows 69 and 72).

Round-9 state (history): Commands (thesis Python /home/luo/anaconda3/bin/python,
from presentation/defense_2026/ unless a path is given):

1. `build_deck.py`, then `render_deck.py` (short repository-contained TMPDIR).
2. `validate_deck.py --pdf Thesis_Defence_2026.pdf` -- 2100 package checks,
   0 package failures, overall PARTIAL for D-058/D-066 (review/ARTIFACT_CHECK.json,
   read 2026-09-30). Counts per build: 63 1439, 64 1539, 65 2081, 66 2092,
   67 2100 (three round-8 citation checks removed, nine numeric-citation
   checks added, net +6, 2098; then two D-303 drawn-table checks from the
   code review, 2100).
3. `equations/derivation_leads.py --check` -- regenerates the derivation leads
   in memory and compares byte for byte (validate_deck.py runs it, D-289).
4. `report_effective_text.py` -- writes review/EFFECTIVE_TEXT.md.
5. `export_defense_script.py --pdf` -- 312 paragraphs, 77 slide headings,
   19 PDF pages.
6. `make_package.py --require-clean` -- last run for build 66 in commit 3afc1c3; the
   tracked package/MANIFEST.json then pinned content commit b406ea3 (46 main + 31
   hidden pages). Build 67 was packaged later (manifest pinned a8eb5fe, commit
   0a58a09); build 77 is the latest package (manifest 487e468, pin 7173058; see the round-11 section and the round-10 note above).

New validate_deck.py check families in round 8:

- No question clause or embedded question clause in any visible string,
  table cell, caption, title or note (D-263, D-287); the two verbatim
  derivation leads of Eqs. 3.21 and 5.12 are the only exemption, with a
  staleness check (D-283).
- Thesis-figure binding: pages 4 and 36 equal figures/thesis/manifest.json and
  the thesis source bytes (D-264).
- Overlay manifest binding (build 67: overlay manifest sha256 73e7300f... after D-303, abd988f1... before,
  page 18 has a Wall frame, D-302): generator and input hashes, per-overlay hash and
  photo hash, per-slide placement, notes that state the overlay mode of every
  frame, visual.overlay_manifest_sha256 equal to the manifest hash, no
  anchored_photos page (D-273, D-290).
- Footer audit against the numbered lists of knowledge/thesis_outline.md
  (counts 74/51/24/55; 149 references, 0 problems) with a parser self-test of
  twelve negative and five positive labels (D-278, D-295), and the footer
  pins of pages 39, 41, 42 (D-279).
- Footer-equation presence: every thesis equation strip is cited by its
  footer and every cited equation is on the page (D-278, D-292).
- Derivation checks for pages 59-77 (family order, crops bound by catalog and
  white_manifest.json, scale 1.4, verbatim leads, "[...]" export text in the
  notes, supports pointers; D-281, D-286) and derivation_leads.py --check plus
  the independent source-line check against writing/v9/zh/src (D-289).
- Chained-contract byte comparison: every bound file key of a row equals its
  base row; rerendered_rows must be empty (D-288).
- citation_required and the citation family (rewritten in round 9; the
  round-8 author-year checks "Every References key appears in the visible
  text of a hidden page", "Every author-year key on any main or hidden page
  is in a References table (D-277)" and "Every citation_required page carries
  a References key (D-277, D-291)" no longer exist, D-301). Nine numeric
  rules over the deck's own list [1]..[12]: 1 every [n] on any page is a
  References row number; 2 every row number is cited on a main or hidden
  page; 3 no author-year string (regex plus the "et al." variant; D-303 adds
  ", " or " (" before the year, and exempts the IEEE "City: Publisher, year"
  shape in the visible References rows only) in the visible text or notes of
  any page; 4 one number per bracket, no list, range or "[a; b]", and (D-303)
  no two adjacent bracket citations on a line separated by anything but
  exactly ", " ("[2],[3]", "[2] [3]"); 5 row numbers contiguous [1]..[N] over pages 43-44; 6 first
  citations in order 1..N (main pages, then hidden); 7 the four
  CITATION_REQUIRED pages (8, 9, 30, 37; legacy keys in D-291) each carry a
  row number; 8 every [n] in notes is a row number; 9 each [n] in a
  compiled_text derivation lead is printed on its compiled PDF page via
  pdftotext (eq_3_18 -> PDF page 46, [52]). Derivation lead strings and quoted
  source_text are excluded from the scans. The checks are labelled D-297
  (rules 4, 5, 6), D-300 (rule 9), D-301 (rules 1, 2, 3, 8) and D-277/D-291
  (rule 7). Negative probes in
  a shadow copy (a leftover "Hampel 1974", "[13]", "[2, 3]", swapped
  first-citation order, "[45]" in notes) each failed the intended rule
  (worker report, build 67; re-run in the D-303 fix task, still FAIL).
- D-303 (build 67, code review I1): every full_table page (41, 42, 43, 44,
  47, 49) draws each display_table cell, header and rows, as exactly one text
  box of its slide; the References pages draw their (number, entry) pairs in
  reading order equal to the JSON rows. Probes: deleting or altering row [12]
  of page 44 in the PPTX alone now fails both checks (0 failures before).
  Builder guard (M1): build_deck.py raises when a page has more bullets than
  bullet slots or a bullet_y list of another length. Generator bound (M4):
  make_frame_overlay_figures.py raises above a 1.0 px World/Object/Wall
  reprojection residual (manifest.json reprojection_checks.residual_bound_px;
  overlay manifest sha256 73e7300f...).
- Also new: References pages visible after Contributions (D-267), the
  page-39 one-line caption (D-269), evaluation pages found by legacy key
  (D-274).

Environment note: the footer audit needs knowledge/thesis_outline.md lists a-d
with its Counts paragraph (a missing paragraph fails the check).

## Restored round-6 checker notes (2026-09-29; history for the commands above)

The current defence deck is the compact round-6 deck: 39 main + 14 hidden
pages, 1785 s = 29:45, bytes restored from commit c5440c4 on 2026-09-29 (D-244;
see deck_inventory.md). The checkers below are those of that deck. Current
commands (thesis Python /home/luo/anaconda3/bin/python, from
presentation/defense_2026/):

1. `render_deck.py` -- only when the PPTX is rebuilt (build_deck.py).
2. `validate_deck.py --pdf Thesis_Defence_2026.pdf` -- 1331 package checks,
   0 package failures, overall PARTIAL for D-058/D-066 (master run 2026-09-29).
3. `export_defense_script.py --pdf` -- script DOCX/PDF export and check.
4. `make_package.py --require-clean` -- copies the deck into package/.

Verified: 2026-09-29. Re-checked in this task: the three commands' argparse
options in the scripts (validate_deck.py takes --deck/--pdf PATH/--out;
export_defense_script.py and export_committee_questions.py take --pdf;
make_package.py takes --require-clean, no --check-only); the reports
review/ARTIFACT_CHECK.json (PARTIAL, package PASS), RENDER_CHECK.json (53
preview pages, PPTX sha256 1096465b...) and SCRIPT_EXPORT_CHECK.json (216
paragraphs, 14 pages); package/MANIFEST.json (commit f6e2ec4, 4 files, 39 main,
14 hidden, 18 embedded MP4); that every checker script named below exists.
The validators were not rerun in this task, to avoid rewriting review/*.json.

Discarded tooling (D-244 removed these from the tree; they exist only in git
history a202509..ddfdf40): check_targeted_revision.py, check_speech_exports.py,
check_restored_numbers.py, restoration_delivery.py, validate_restoration.py,
restoration_inventory.py, restoration_layout.py and restoration_timing.py
(absent from the working tree, re-checked 2026-09-29). Do not follow older
notes that name them. anim/unified_revision_build.py is back at its c5440c4
version (restored), but the schema 10/11 and M2/M3/M4 workflows built on it
are discarded.

## Checker inventory

Verified: 2026-09-28 (round-6 update; command list and purposes carried over)
Sources: presentation/defense_2026/{validate_deck.py,export_defense_script.py,make_package.py,anim/validate_media.py,anim/validate_filter_sync.py,anim/validate_matched_sources.py}, writing/v9/scripts/{check_style.py,check_refs.py,verify_submission.py}, eval/unity_check/{check_unity_log.py,check_rig_sizing.py}, eval/inspect/{check_v1_overlay.py,check_tracking_precondition.py}, thesis/check_limits.py, presentation/defense_2026/DECISIONS.md
Answers: the exact command and one-line purpose of every project checker, the review/*.json file each rewrites, and the regeneration commands for the two out-of-repository caches the defence-deck checkers depend on.

## Round-6 additions (verified 2026-09-28)

- validate_deck.py new checks (DECISIONS.md D-207, D-213, D-214):
  "Slide NN divider draws only its chapter label and title" replaces
  the round-5 outline-column divider check; it requires exactly two
  text-frame shapes on each of the nine divider slides (7, 10, 15,
  17, 22, 26, 32, 34, 36) -- one chapter_label run (22 pt, BBBBBB)
  and one title run (28 pt, FFFFFF) -- and checks their band moved to
  (0.50, 3.15, 12.83, 4.45) in, the vertical-middle geometry of
  D-213. The round-5 thesis_map typography allowance and "Exactly
  one thesis_map page" check are removed (page deleted, D-205).
- "Committee copy X is byte-identical to Y" now also covers page 35
  (p35-Fresh_Unity_Handover_Discussion, copy of p47), alongside the
  existing p43/p46 filter-copy checks; the Unity-composite audit
  skips copy rows on its first pass and then audits each against its
  original (hash-bound byte_identical_copy_of, film/poster bytes,
  provenance) rather than reading a copy report as a capture report.
- The methodology-time check is renamed "At least 55 percent of main
  time explains methodology" (floor 0.60 -> 0.55, D-211).
- revision_id_map.json schema 9 (D-214): main 39, backup 14, total
  53; old_to_new maps round-5 ids to round-6 pages, with round-5
  pages 3 and 4 (thesis map, Introduction divider) marked "deleted".
- Round-6 result: validate_deck.py 1331 checks, 0 package failures
  (overall PARTIAL, same two retained D-058/D-066 findings as every
  earlier round).

## Round-5 additions (verified 2026-09-28)

- `python equations/typeset_filters.py --check` (presentation/
  defense_2026): re-renders the nine typeset filter equations and
  exits 1 if any PNG or the catalogue differs. validate_deck.py also
  runs it when the installed matplotlib equals the catalogue's 3.9.2.
- validate_deck.py new checks: typeset catalogue pins
  v1/mediapipe/filter_landmarks.py and realtime_person.py; each ts_ key
  cites existing lines of the pinned file and its PNG matches hash,
  size and white colour; pages 42-49 (round-5 numbering; round 6 shifts hidden pages by +2) are exactly the ts_ pages and use
  page 9's geometry (EMU-exact boxes; film equal to page 9's); pages
  48-49 panel chart embedded uncropped; every References key visible
  on a hidden page and every visible author-year key in a References
  table. Round-5 result: 1282 checks, 0 package failures.

## Presentation checkers (presentation/defense_2026/)

Run with the thesis Python unless noted: `/home/luo/anaconda3/bin/python`.

| Checker | Command | Validates | Rewrites |
|---|---|---|---|
| validate_deck.py | `python validate_deck.py --pdf Thesis_Defence_2026.pdf` | Delivered PowerPoint package, timing, notes and media against the content files and the typography grid | review/FILTER_SYNCHRONIZED_CHECK.json, review/MATCHED_EVIDENCE_CHECK.json (reads); overall PASS/FAIL/PARTIAL report |
| export_defense_script.py | `python export_defense_script.py --pdf` | Makes the printable speaking script from the generated Markdown, verbatim | review/SCRIPT_EXPORT_CHECK.json |
| anim/validate_media.py | `python anim/validate_media.py` | Decodes all fresh presentation media and preserves technical metadata | review/MATCHED_EVIDENCE_CHECK.json, review/MATCHED_INDEPENDENT_REVIEW.json, review/<stem>_checks.json per asset |
| anim/validate_filter_sync.py | `python anim/validate_filter_sync.py` | Independently checks synchronized filter maps against recorded sources | review/FILTER_SYNC_MAPPING_CHECK.json (reads review/media_validation.json) |
| anim/validate_matched_sources.py | `python anim/validate_matched_sources.py` | Independently checks recorded matched-media transforms and frame maps | review/MATCHED_INDEPENDENT_REVIEW.json (reads media/provenance/matched_evidence.json and review/MATCHED_EVIDENCE_CHECK.json) |
| make_package.py | `python make_package.py --require-clean` | Copies the finished defence deck into a shareable folder, gated on the other checks | reads review/ARTIFACT_CHECK.json, review/RENDER_CHECK.json, review/SCRIPT_EXPORT_CHECK.json |
| export_committee_questions.py | `python export_committee_questions.py --pdf` | Makes COMMITTEE_QUESTIONS.docx/.pdf from the reviewed Markdown and question index and verifies them (kept from the discarded work) | review/COMMITTEE_EXPORT_CHECK.json |

## Package commit metadata (verified 2026-09-29)

Source: presentation/defense_2026/make_package.py (main(): dirty check and manifest write);
`git ls-files presentation/defense_2026/package/MANIFEST.json` and
`git check-ignore presentation/defense_2026/package/Thesis_Defence_2026/README.txt`.

The manifest is tracked; the share folder is ignored. Every package run
writes the current HEAD into the manifest and share-folder README.
`--require-clean` checks the three copied artifacts plus build_deck.py,
talk_content.json, backup_content.json and PACKAGE_README.txt against
HEAD. It does not include the manifest itself in that dirty check.

To close a delivery without chasing a self-referential commit hash:
commit the accepted content, run make_package.py --require-clean once,
then commit the manifest and any package-audit/handoff metadata updates.
The package remains pinned to the content commit, whose artifact bytes
are also present in the following metadata-only commit. Do not rerun
packaging just to replace that content hash with the metadata commit.
The artifact, render and script-export report hashes stay unchanged;
the manifest's README hash/size, total bytes, git_commit and dirty flag
change. A follow-up audit that records the old package commit/dirty flag
must refresh that detail against the regenerated manifest.

## Thesis checkers (writing/v9/scripts/, thesis Python)

| Checker | Command | Validates |
|---|---|---|
| check_style.py | `python writing/v9/scripts/check_style.py` | Style sweep over the condensed thesis parts (prose paragraphs only) |
| check_refs.py | `python writing/v9/scripts/check_refs.py` | Cross-reference check across every chapter/appendix docx in writing/v9 |
| verify_submission.py | `python writing/v9/scripts/verify_submission.py` | Actual V9 submission artifacts against Checklist 2.8 and baseline (document structure and rendered geometry, not experiment results) |

Rerun `python writing/v9/scripts/make_submission_baseline.py` whenever an image or the
citation numbering legitimately changes; verify_submission.py's "Embedded image bytes
preserved" check compares against audit_evidence/submission_checklist_v9/baseline.json.
Done 2026-10-06 for the signed Approval page (54 images against a baseline of 53;
D-395) (verified 2026-10-06).

## Unity and recording checkers (eval/, thesis Python unless noted)

| Checker | Command | Validates |
|---|---|---|
| eval/unity_check/check_unity_log.py | `python eval/unity_check/check_unity_log.py` | Numeric backstop for the R5 Unity pose check |
| eval/unity_check/check_rig_sizing.py | `python eval/unity_check/check_rig_sizing.py` | Rig sizing for a Unity capture (avatar sizing from IntegratedSceneReceiver) |
| eval/inspect/check_v1_overlay.py | `python eval/inspect/check_v1_overlay.py` | v1 reconstruction correctness by reprojecting onto the colour video (camera frame only, no calibration, no Unity) |
| eval/inspect/check_tracking_precondition.py | `python eval/inspect/check_tracking_precondition.py` | Recording validity: whether MediaPipe is actually tracking the body |
| thesis/check_limits.py | `python thesis/check_limits.py` | Numerical checks behind the D1_limitations.md derivations |

## Documentation-only checks

- ASCII check: `grep -nP '[^\x00-\x7F]' <files>` -- must return nothing.
- `git diff --check` -- flags whitespace errors (trailing whitespace, CRLF-in-LF-file conflicts) in the diff.

## Known accepted findings (do not re-litigate without new evidence)

- `validate_deck.py` overall status is PARTIAL, not PASS, because of
  2 retained historical source findings tied to decisions D-058 and
  D-066 (confirmed by DECISIONS.md D-120/D-125 evidence lines, which
  both cite "overall PARTIAL only for the two retained historical
  Unity-checker findings of D-058/D-066").
- Historical source CSVs retain CRLF bytes (the two committee_materials
  VIDEO_INDEX.csv files keep the c5440c4 endings that git diff --check flags
  if they are ever edited; D-244 open item). The D-222 gzip snapshot of the
  discarded deck was removed with that deck.

## Caches outside the repository

Both live under /tmp and are not tracked by git. Neither directory below, nor /tmp/defense_bank_rgb or /tmp/defense_axes_rgb_r7, existed on 2026-09-29 (checked with ls); the committed media are bound by hash and are not regenerated from them. Writing to them
needs the author's approval each time (per Standing project
constraints, /tmp is outside the repository).

### /tmp/defense_2026_causal/camera

899 JPEGs (R6b arm-outstretched trial colour frames). Regenerate:

```
/home/luo/anaconda3/envs/v3rt/bin/python presentation/defense_2026/anim/causal_replay.py extract --start-frame 0 --duration 30
presentation/defense_2026/anim/recorded_context.py audit-source
```

(`causal_replay.py` argparse: stage `extract`, `--start-frame`,
`--duration`(via count)/`--force-extract`; the extract stage runs
under v3rt, confirmed in causal_replay.py: "Run with base Python:
causal_replay.py all. The extract stage uses v3rt.")

### /tmp/defense_matched_r7

182 frames (R7 handover trial). Regenerate:

```
/home/luo/anaconda3/envs/v3rt/bin/python presentation/defense_2026/anim/matched_evidence.py extract
```

Confirmed in DECISIONS.md D-121: this command extracted 182 frames
into /tmp/defense_matched_r7, then validate_matched_sources.py PASS
(141 matched frames); the only file it rewrote,
review/MATCHED_INDEPENDENT_REVIEW.json, was restored to HEAD bytes
after the check (differed only in reviewed_at_utc).

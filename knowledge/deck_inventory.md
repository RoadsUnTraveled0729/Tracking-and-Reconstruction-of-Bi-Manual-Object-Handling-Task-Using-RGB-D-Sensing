## Final deck (Verified 2026-10-06; commits 3dbd345 and 2d9db7e)

Sources: presentation/defense_2026/Thesis_Defence_2026.pptx (python-pptx and zipfile
read on 2026-10-06), review/RENDER_RECORD.json, package/MANIFEST.json,
speaker_script.json, DECISIONS.md D-381 to D-393, README.md of that folder.

The deck is the author's reviewed file, adopted byte for byte (sha256
da94af7c11b30defdc5de453b0014c5f2b396bc99740293e188770d766a0a749, 102,708,312 B;
D-381), with one later edit (Verified 2026-10-06, D-387): the slide 12 picture
is replaced by the chain-growth film p12_chain_growth.mp4 (8.0 s), giving sha256
3dcaf1068b5e7668e8b8ed325e2145027d7bb91566e89ea31ee3cc581d43dff1, 103,078,203 B;
only slide12.xml and its rels changed (review/slide12_patch.json). Second edit
(Verified 2026-10-06, D-389): results slides 33-35 reduced to the spoken script
by anim/patch_results_slides.py (slide 33 model and avatar without the grasp
distance; slide 34 six rows with the intermediate window 445-489 amber bold, the
rest grey; slide 35 right wrist only, image50.png removed), giving sha256
4e158522cf007fe6f06f69dd2770b442913cc9fa00ee9f2af3c34551994d9a37, 102,013,918 B;
only slide33-35.xml and the slide 35 rels changed
(review/results_slides_patch.json). Third edit (Verified 2026-10-06, D-390):
the slide 33 Python FK still and the slide 34 masked-comparison figure added by
anim/patch_results_pictures.py (slide 34 Frames column removed, grid 14 pt from
x 0.5 to 7.6 in), giving sha256
13f3f74b63a7cc7fc91779c4c478b8b32852bd63851a7f0f1961c66ef56278f6, 103,088,310 B;
only slide33-34.xml, their rels and two PNG parts changed
(review/results_pictures_patch.json). Fourth edit (Verified 2026-10-06, D-391):
slide 39 "Limitations" lists the system assumptions (static scene, uncertain
inputs, object size, rigid torso) and their consequences, row 5 and its divider
deleted, caption and footer citing Chapter 9 and Sections 2.2.2, 3.2.1, 4.1, by
anim/patch_slide39_limitations.py, giving sha256
a27dc653d3860e8076622e1923894c49a2c03e148551f06d1739eebdb15f2a80, 103,088,322 B;
only slide39.xml changed (review/slide39_patch.json). Fifth edit (Verified
2026-10-06, D-392): slide 34 rows relabelled by wrist travel ("Wrist travel
0.6 | 2.8 | 5.1 cm, wrist | elbow", thesis Table 7.5), header "Window / joint",
tiles "45-frame windows, slow motion" (later "45-frame slow windows") and "Three recovery cases", a new caption and a
three-case figure (frame 489, wrist 1.2 / 1.9 / 1.2 cm) in place of the error-curve
figure, by anim/patch_slide34_wording.py, giving sha256
0800111c3300c454c636f58450e7b74e42b392e14888c70d17756142ee1cc7cd, 102,961,028 B;
only slide34.xml and the figure part changed (review/slide34_wording_patch.json).
The slide 34 script edit, first blocked by the 1620 s cap, was applied after the
master decisions (D-392 Final state). Sixth edit (Verified 2026-10-06, D-393):
slide 33 shows the three-panel film media/p33_three_panel.mp4 (recorded RGB, Python
FK skeleton, Unity avatar; 1440 x 640, 1498 frames) instead of the FK still, by
anim/patch_slide33_film.py, giving sha256
f1b146219bb10b04565f2f0ae3dc95fc8c78b4ea8179f9b5838044a3ea31be00, 98,268,933 B;
slide33.xml and its rels changed, two media parts added and three removed
(review/slide33_film_patch.json). Seventh edit (Verified 2026-10-06, D-392 Final state): tile 1002
"45-frame slow windows" by anim/patch_slide34_tile.py, giving the current sha256
b3b6a8f0d650888db8f13f8536c787f90cb5b16a1d1860683d46af11fe129cb7, 98,268,928 B;
only slide34.xml changed (review/slide34_tile_patch.json). 77 slides:
1-46 shown, 47-77 hidden backup (31 hidden); 149 media files in ppt/media (123
PNG, 26 MP4), 0 external relationships. The slide-number and
title map of all 77 slides is in presentation/defense_2026/README.md (page map).
Structure: three blocks. Block 1 motivation and goal, slides 1-4. Block 2 the
offline reconstruction system, slides 5-30 (architecture 5; data preprocessing
6-10; kinematic model 11-15; object tracking 16-18; partial occlusion 19-24;
modules to one system 25-30). Block 3 results and next steps, slides 31-46
(results 31-38; limitations, future directions, summary 39-41; references
42-44; Thank you 45; Questions 46). Hidden backup: 47 coordinate
transformations, 48 left-handed and right-handed body-model workflows (the
two approved LH/RH workflows with derived matrix-form operation counts: eight
input matrix-vector products versus five output rotation conversions of two
matrix-matrix products each; representation counts, not a runtime
measurement), 49-50 ArUco versus AprilTag, 51-52 transport, 53-57 filter
alternatives, 58-76 derivations (Eqs. 3.1 to 7.6), 77 the causal run from its
process logs. Page 20 has three main points with six nested detector items; page
23 has RGB above synchronized flat-circle geometry in one automatically started
film; page 38 is a native Unity recording with corrected table display bounds and
wall span. All 23 references appear on pages 42-44 (1 of 3 to 3 of 3).

Script: Thesis_Defence_2026_Speaker_Script.docx covers slides 1-46 with 2,657
spoken words, 1620 s = 27:00 at 110 words per minute (D-388; 2,660 after the slide 39 text, D-391; 2,657 after the slide 34 text, D-392; D-393 changed a cue only; docx sha256 f0fdb49146374ce0f86f58ad44ee741c7d0900e46be0f49aa76e2f05068f28ab) (the 2026-10-05 version had
2,540 words; rewritten in 2d9db7e, D-386; see speaker_script.md). Guide:
Thesis_Defence_2026_Outline_and_QA_Index.docx, two Letter landscape pages,
English. PDFs: LibreOffice renders of all three (77, 23 and 2 pages).

Not verified: PowerPoint playback of the embedded videos, a timed aloud
rehearsal, a cold read of the rewritten script (D-383, D-386). The 2026-10-05
author checks recorded in review/personal_review_20261005/VISUAL_REVIEW.json
cover the adopted D-381 baseline (sha256 da94af7c...), before the later
D-387..D-393 edits. They do not certify playback or layout of those edits
in the current pptx (sha256 b3b6a8f0...). This review boundary was rechecked
2026-10-08 against presentation/defense_2026/README.md and DECISIONS.md D-381.

## RETIRED (history): everything below describes generated decks that no longer exist

The generated decks of builds 24-77, their build_deck.py / validate_deck.py
pipeline and talk_content.json were deleted in 3dbd345 (D-382, D-385). Recover at
85078c9 (round-11 state) or 87e87ae. Nothing below is the current deck; the page
numbers, hashes and file names are those of the round named in each heading.

## Round-11 deck (build 77, 2026-10-01; history, retired in 3dbd345)

Verified: 2026-10-01 at master 88878cd (build 77 generated outputs from
commit ac80447; round-11 commits 06121e1..943e4d7 are the chain changes,
d449830..88878cd the back-port and build 77).
Sources: presentation/defense_2026/{talk_content.json, backup_content.json,
script_document.json, budget_override.json, review/ARTIFACT_CHECK.json,
review/RENDER_CHECK.json, review/SCRIPT_EXPORT_CHECK.json,
review/EFFECTIVE_TEXT.md, SPEAKER_NOTES.md, DEFENSE_SCRIPT.md,
review/round11_focused/{FOCUSED_CHANGES.md, EQUIVALENCE.md, RENDER_COMPARE.md,
RULE_FIXES.md}, build_deck.py, validate_deck.py, set_page_budgets.py,
make_package.py, DECISIONS.md D-340 to D-369}, PROJECT_STATUS.md row 77,
README.md subsection "Content fields added in round 11".
Answers: the page-by-page contents of the current defence deck, what the
round-11 build chain added, and how the author's FOCUSED pair relates to it.
Reproduced by the master and re-read in this task (numbers below were read
from the named files, not copied from a report).

Counts (review/ARTIFACT_CHECK.json, pdfinfo, zip listing of the pptx):
76 slides = 48 main pages in talk_content.json (46 shown, 2 hidden: pages 2
and 3) + 28 hidden topic pages (49-76 in backup_content.json); 30 hidden
pages in all (ARTIFACT_CHECK.json hidden_pages = [2, 3, 49..76]); 76 PDF
pages (pdfinfo Thesis_Defence_2026.pdf); 136 media files of which 19 MP4
(zip listing), 0 external relationships. PPTX sha256
8481390b80050620c549edcf5125b7762cc01aa99514ae5ff89dc440641a767d.
Validator: validate_deck.py --pdf 2092 checks, all PASS (counted in
ARTIFACT_CHECK.json), status PARTIAL only for the retained D-058/D-066
source findings (historical Unity outcome checker, page 30 r5_archived; pages
36 and 41 r7), package_status PASS. The package was rebuilt for build 77
(2026-10-01): package/MANIFEST.json pins git_commit 7173058, the round-11
records commit (48 main, of which 46 shown and 2 hidden, + 28 hidden topic
pages, 76 PDF pages, 2092 checks, pptx sha256 8481390b...); the manifest is
committed as 487e468 and these statements are in the following commit.

Time and words (planned_main_seconds, main_script_words, focus_seconds in
ARTIFACT_CHECK.json; SPEAKER_NOTES.md header): 1895 s = 31:35 at 140 words
per minute (RATE_START_WPM) over the 46 shown main pages; 100 s over the
1795 s cap (TOTAL_CAP_S), recorded as an override in budget_override.json
{decision D-349, cap_s 1795, total_s 1895, overage_s 100, rate_wpm 140}
(D-364, UNCERTAIN: the author accepts 31:35 or chooses cuts); 3943 script
words on shown main pages (SPEAKER_NOTES.md: 124.8 words per minute across
the media-inclusive plan; FOCUSED 3941, build 74 3647); focus_seconds context
75, methodology 1230, evaluation 350, conclusion 230, questions 10;
methodology 1230 of 1895 s = 64.9 percent (floor 55 percent, D-211).
Budgets are word-rate estimates, not a timed rehearsal. Dividers with
narration are budgeted by words (D-348): pages 6, 12, 19, 21, 37 and 42 are
10 s, 26 and 40 are 15 s, 31 is 30 s (nine dividers, same set as before).

Hidden mechanism (D-341, supersedes the "hidden = after the talk" part of
D-128): a main page of talk_content.json may carry "hidden": true (boolean,
main pages only, duration 0). build_deck.py is_hidden() at lines 1124-1126
(`s['id']>main_count or s.get('hidden') is True`) and the slide is drawn with
show="0" at line 1486; the load checks at lines 1453-1462 raise unless hidden
is boolean on main pages only, a shown main page has a positive duration and a
hidden or backup page has duration 0. validate_deck.py page_hidden() at lines
777-779 and the check "Slide NN visibility" at line 2659
(`hidden == page_hidden(spec, i, len(talk))`). set_page_budgets.py gives a
hidden main page 0 s and leaves it out of the total (line 102);
make_package.py hidden_ranges() (line 92) writes "2-3 and 49-76" into the
package README; shown counts everywhere else exclude hidden main pages (D-353).
Pages 2 and 3 have empty narration (notes "" on pages 2, 3 and 46, D-367) and
their records stay as they were (D-365).

Notes pane and unspoken record (D-343, D-344): the PowerPoint notes pane holds
only the author's layout, one line "[cue]" per cue, one line per narration
paragraph in block order, then one line "Sources: <source>" (a list source
joined with " | "), no blank lines. Pages 17, 23 and 44 declare script_blocks
(two cues, D-342, D-367); the other 73 pages keep presenter_cue and notes. The
builder lines that used to sit in the pane (the "Budget: N s" lead, Role,
Provenance, media and recording lines, Slide purpose, the [...] lead export
text, the main-page derivation pointer, the closing-page hidden-topic list)
now live in the "Unspoken record (not spoken)" block of every page section of
SPEAKER_NOTES.md (76 "## Slide NN: title (state)" sections, verified by grep
2026-10-01); derivation pages also get the lead-source line and "This page
supports main slide N". The closing list names every hidden page. DEFENSE_SCRIPT.md
keeps the "**...**" emphasis pairs (page 22 only), the pane and counts drop
them (D-354, D-366).

Layout variants (data fields, no page-number special case): page 2 is the
outline kind with visual.variant "heading_pairs" (three heading and grey
subline pairs at 24 pt FFFFFF and 18 pt BFBFBF, footer B0B0B0 with no rule,
plain box style, D-345); page 41 is a composite with bullet_boxes, six
boxes alternating 22 pt headline and 17 pt detail lines at 22 pt leading
(no dash marks), the caption under the bullets kept (D-345, D-350). The
options title_box, footer and box_style are admitted only on these two
author layouts (D-355); font roles and colours: knowledge/deck_fonts.md.
Gate geometry tolerance: 1 EMU on page 41 only (D-368, G-01). Rendered
comparison: page 2 raster identical to the FOCUSED render, page 41 differs
only in the title rows and the F-32 line (D-345 annotation, RENDER_COMPARE.md).

script_document.json (D-346, D-363): the DEFENSE_SCRIPT.md document text
(header, main_heading, qa_heading, qa_intro, section_lines false, appendix with
the author's "Additional questions to rehearse" and "Rehearsal and revision
notes" sections, final_blank_line false); the file DEFENSE_SCRIPT.md has 76
"### Slide NN:" headings (grep) and the export has 387 paragraphs and 23 PDF
pages (SCRIPT_EXPORT_CHECK.json).

Back-port (D-359 to D-369): the FOCUSED titles, text, cues, narration and
hidden set were written verbatim into the content files by
review/round11_focused/apply_backport.py, with 69 minimal rule fixes F-01 to
F-69 (D-360), four wordings by the master (F-70, F-71, F-72, F-77, NEEDS
AUTHOR, D-361, D-362), four script-document semicolon fixes F-73 to F-76 and
the end-of-file fix F-78 (D-363). Removed caveats and the four flagged claims
(pages 33, 35, 36, 41) are kept as the author wrote them (D-359). Outcome and
gate numbers: knowledge/focused_revision.md.

Decision range: D-109..D-369 (round 11 is D-340 to D-369: D-340 the FOCUSED
files, D-341 to D-350 chain support, D-351 to D-358 code-review fixes, D-359
to D-369 back-port and build 77).

### Round-11 pages (read from talk_content.json and backup_content.json)

Kind is visual.kind. "Hidden" is the per-page flag or position (pages 49-76).
The last column gives the build-74 title where the title changed (18 pages,
the same 18 as FOCUSED_CHANGES.md; page 41 reads "What the evaluation
establishes" in the FOCUSED deck and "Findings established by the evaluation"
here, F-70). Media, legacy keys and the derivation supports map are unchanged
from the round-10 tables below (git diff of committee_materials/, media/,
figures/, provenance/ from 0e9fe81 to 88878cd is empty; supports map equal to
0e9fe81). Duration column sums to 1895 s over pages 1-48.

| # | Title | Kind | Dur (s) | Hidden | Build-74 title (only where retitled) |
|---:|---|---|---:|---|---|
| 1 | Tracking and Reconstruction of Bi-Manual Object Handling Task Using RGB-D Sensing | cover | 20 | no |  |
| 2 | Presentation outline | outline | 0 | yes |  |
| 3 | Human-object interaction with one camera | table | 0 | yes | was "Motivation" |
| 4 | Introduction: the handover task | task_video | 55 | no | was "The task: bimanual object handling under one RGB-D camera" |
| 5 | Body and object reconstruction | full_image | 30 | no | was "Information flow through the system" |
| 6 | Experimental setup and measurements | divider | 10 | no |  |
| 7 | Static marker calibration | frame_figure | 55 | no |  |
| 8 | Landmark acceptance | landmark_video | 55 | no |  |
| 9 | Hampel spike removal | composite | 45 | no |  |
| 10 | Short-gap interpolation | composite | 40 | no |  |
| 11 | Butterworth smoothing | composite | 50 | no |  |
| 12 | Kinematic modelling | divider | 10 | no |  |
| 13 | Camera and Camera' frames | frame_figure | 45 | no |  |
| 14 | Landmark frames and the T-pose reference | frame_figure | 40 | no |  |
| 15 | Torso and root frame | frame_figure | 45 | no |  |
| 16 | Recorded torso frame | composite | 45 | no |  |
| 17 | Shoulder swing and twist | composite | 60 | no |  |
| 18 | Elbow | composite | 50 | no |  |
| 19 | Object tracking and scene reconstruction | divider | 10 | no |  |
| 20 | Object pose in the World frame | frame_figure | 50 | no |  |
| 21 | Pose recovery during tracking failure | divider | 10 | no |  |
| 22 | Failure detection and output states | grip_video | 70 | no | was "Output states and holding context" |
| 23 | The object provides a wrist target | composite | 65 | no | was "Grasp offset held through tracking loss" |
| 24 | The circle of possible elbows | composite | 60 | no |  |
| 25 | Elbow selection and fallback | fallback_video | 60 | no | was "Selecting one elbow and the direction-memory fallback" |
| 26 | System integration and graphical reconstruction | divider | 15 | no |  |
| 27 | Matching the body and object in time | composite | 50 | no | was "One frame through the system" |
| 28 | A common frame for the Unity scene | frame_figure | 45 | no | was "Mapping into the scene" |
| 29 | Mapping model rotations onto the avatar | frame_figure | 45 | no | was "Applying the rig" |
| 30 | Integrated reconstruction | composite | 45 | no |  |
| 31 | Experimental evaluation | divider | 30 | no |  |
| 32 | Object movement compared with physical measurements | evaluation_figures | 70 | no | was "Object reconstruction accuracy" |
| 33 | Body reconstruction at model and avatar stages | evaluation_figures | 60 | no | was "Human reconstruction accuracy" |
| 34 | Arm recovery with missing elbow and wrist inputs | table | 75 | no | was "Recovery under landmark failure: synthetic removal" |
| 35 | Object assistance during natural tracking failures | evaluation_figures | 65 | no | was "Recovery under natural occlusion" |
| 36 | Integrated replay of the handover | composite | 50 | no | was "Imperfect handover replay" |
| 37 | Real-time feasibility | divider | 10 | no |  |
| 38 | Offline pass and causal structure | full_image | 50 | no |  |
| 39 | Causal processing and timing limits | composite | 65 | no | was "Causal processing and adaptive smoothing" |
| 40 | Discussions | divider | 15 | no |  |
| 41 | Findings established by the evaluation | composite | 80 | no | was "Discussions" |
| 42 | Conclusions | divider | 10 | no |  |
| 43 | Further validation and development | full_table | 40 | no | was "Limitations" |
| 44 | Contributions | full_table | 70 | no |  |
| 45 | References (1 of 2) | full_table | 5 | no |  |
| 46 | References (2 of 2) | full_table | 5 | no |  |
| 47 | Thank you | thanks | 5 | no |  |
| 48 | Questions | closing | 10 | no | was "Question" |
| 49 | ArUco vs AprilTag in the published literature | full_table | 0 | yes |  |
| 50 | AprilTag 3 faster, corner errors converge at 96 px | full_image | 0 | yes |  |
| 51 | Transport candidates | full_table | 0 | yes |  |
| 52 | Moving one frame package from Python to Unity | full_image | 0 | yes |  |
| 53 | Savitzky-Golay filtering | composite | 0 | yes |  |
| 54 | Median filtering | composite | 0 | yes |  |
| 55 | One Euro filtering | composite | 0 | yes |  |
| 56 | Butterworth for offline smoothing | panel_chart | 0 | yes |  |
| 57 | One Euro for real-time smoothing | panel_chart | 0 | yes |  |
| 58 | Derivation: Camera' and the chain (Eqs. 3.1-3.3) (1 of 2) | derivation | 0 | yes |  |
| 59 | Derivation: Camera' and the chain (Eqs. 3.4-3.6) (2 of 2) | derivation | 0 | yes |  |
| 60 | Derivation: Torso and root frame (Eqs. 3.7-3.9) (1 of 2) | derivation | 0 | yes |  |
| 61 | Derivation: Torso and root frame (Eqs. 3.10-3.12) (2 of 2) | derivation | 0 | yes |  |
| 62 | Derivation: Shoulder and elbow frames (Eqs. 3.13-3.14) | derivation | 0 | yes |  |
| 63 | Derivation: Root Euler angles (Eqs. 3.15-3.17) | derivation | 0 | yes |  |
| 64 | Derivation: Shoulder swing and twist (Eqs. 3.18-3.23) | derivation | 0 | yes |  |
| 65 | Derivation: Elbow coordinates (Eq. 3.24) | derivation | 0 | yes |  |
| 66 | Derivation: Object pose in World (Eqs. 4.1-4.2) | derivation | 0 | yes |  |
| 67 | Derivation: Grasp offset (Eqs. 5.1-5.4) | derivation | 0 | yes |  |
| 68 | Derivation: Direction memory and wrist target (Eqs. 5.5-5.7) | derivation | 0 | yes |  |
| 69 | Derivation: Elbow circle and prior (Eqs. 5.8-5.10) (1 of 2) | derivation | 0 | yes |  |
| 70 | Derivation: Elbow circle and prior (Eqs. 5.11-5.12) (2 of 2) | derivation | 0 | yes |  |
| 71 | Derivation: Mapping into Scene (Eq. 6.1) (1 of 2) | derivation | 0 | yes |  |
| 72 | Derivation: Mapping into Scene (Eqs. 6.2-6.3) (2 of 2) | derivation | 0 | yes |  |
| 73 | Derivation: Rig chain and rest axes (Eqs. 6.4-6.5) | derivation | 0 | yes |  |
| 74 | Derivation: Gravity and floor (Eq. 6.6) | derivation | 0 | yes |  |
| 75 | Derivation: Evaluation measures (Eqs. 7.1-7.2) (1 of 2) | derivation | 0 | yes |  |
| 76 | Derivation: Evaluation measures (Eqs. 7.3-7.6) (2 of 2) | derivation | 0 | yes |  |

## Author's focused revision (verified 2026-10-01; back-ported in build 77)

presentation/defense_2026/Thesis_Defence_2026_FOCUSED.pptx and
presentation/defense_2026/DEFENSE_SCRIPT_FOCUSED.md: the round-10 generated
deck and script (build 73 or build 74; the two differ only in the page-49
notes, which this revision rewrote) re-edited by the author outside
build_deck.py, 2026-09-30. 76 slides, 76 notes slides, 136 media files, 0
external relationships (same counts as the tracked Thesis_Defence_2026.pptx);
hidden set {2, 3, 49-76} (the build-74 deck hides only 49-76). Change counts
(44 of 152 slide and notes parts identical, not the 55 that D-340 states),
the 18 retitled pages and the notes-pane format are in knowledge/focused_revision.md,
measured by compare_decks.py; they are not repeated here. The script keeps
the same 76 "### Slide NN:" headings with rewritten narration; its non-ASCII
dashes and quotes on 16 lines were normalised to ASCII when the file was added
to the repository. The pair stays unchanged beside the generated outputs as the
reference of the round-11 gate (D-340 annotation); build_deck.py does not
produce them and validate_deck.py does not read them, and since build 77 their
content is back-ported into the content files (see the round-11 section above).
Decision: DECISIONS.md D-340.

## Round-10 deck (builds 68-74, 2026-09-30; history, superseded by build 77 above)

History: the text below is the state verified on 2026-09-30 at build 73 and was
not rewritten. Build 74 (D-334 to D-338) hardened the wording checks, the
page-4 clip and overlay generator checks and corrected content leftovers (the
page-49 Source field, unrendered data fields), with no deck-text change beyond
the page-49 notes; the numbers below (48 main + 28 hidden counted without the
hidden flag, 1755 s, 3647 words, 2081 checks, durations, the titles of the 18
pages listed above, a notes pane with the Budget lead) are not those of build 77.

Verified: 2026-09-30 at build 73 (HEAD 9e0ebec).
Re-read this task: talk_content.json (48 pages, durations sum
1755 s), backup_content.json (28 pages, ids 49-76,
all duration 0), review/ARTIFACT_CHECK.json (status PARTIAL, package_status
PASS, 2081 checks all PASS, main_slides 48, backup_slides 28,
planned_main_seconds 1755, main_script_words 3647, focus_seconds
{"context": 140, "methodology": 1105, "evaluation": 280, "conclusion": 220, "questions": 10}). PPTX sha256 a335a3a2...;
the PDF has 76 pages (pdfinfo). The two retained source findings are the
historical Unity outcome checker on page 30 (r5_archived) and on pages 36 and
41 (r7), D-058/D-066.
Sources: presentation/defense_2026/{talk_content.json,backup_content.json,
review/ARTIFACT_CHECK.json,DECISIONS.md D-304 to D-333}, PROJECT_STATUS.md rows 68-73.
Answers: the page-by-page contents of the current defence deck.

48 main pages (1755 s = 29:15, 3647 script words, methodology 1105 s = 63.0
percent) and 28 hidden pages (49-76, show="0").
Build history: 68 (M1a structure: task video page 4 before information flow
page 5, research-question page deleted, old page 8 split into pages 7-8, the
filter page split into pages 9-11, hidden filter pages 51-53 removed; 2063
checks; D-304 to D-309), 69 (M1b wording, D-311 checks; 2068; D-310 to
D-315), 70 (M2a figures on pages 7, 13, 15, root angles once; 2073; D-316
to D-319), 71 (M2b page-4 clip without a caption, no mask; 2073; D-320,
D-321), 72 (M3 script version 2 in all 76 notes, page 16 retitled "Recorded
torso frame", derivation page 63 supports page 15, notes checks (e)-(h),
budgets from set_page_budgets.py, 1735 s; 2078; D-322 to D-328), 73 (M3
script version 3 in the 48 main notes, v3 presenter cues on all 76 pages,
page-33 bullet, semicolon rule on cues and DEFENSE_SCRIPT.md, budgets reset to
1755 s; 2081; D-329 to D-333). Durations are computed from the word counts
at 140 words per minute (D-327, D-333) and stay untimed until an aloud
rehearsal.
Nine dividers: 6, 12, 19, 21, 26, 31, 37, 40, 42. References are main pages 45-46; Thank you
47; Question 48. The page-41 caption sits under the bullets (caption_under_bullets).
Derivation pages (supports field of backup_content.json): 58,59 page(s) 13; 60,61 page(s) 15; 62 page(s) 14; 63 page(s) 15 (D-325; 16 at build 71); 64 page(s) 17; 65 page(s) 18; 66 page(s) 20; 67 page(s) 23; 68 page(s) 25; 69,70 page(s) 24, 25; 71,72,74 page(s) 28; 73 page(s) 29; 75,76 page(s) 32.
Decision range: D-109..D-333 (round 10 is D-304..D-333).

### Main pages (legacy key = the key the validator uses to find the page)

| # | Title | Dur (s) | Kind | Media and figures | Legacy key |
|---:|---|---:|---|---|---|
| 1 | Tracking and Reconstruction of Bi-Manual Object Handling Task Using RGB-D Sensing | 20 | cover | - | 1 |
| 2 | Presentation outline | 30 | outline | - | presentation_outline |
| 3 | Motivation | 55 | table | - | motivation |
| 4 | The task: bimanual object handling under one RGB-D camera | 35 | task_video | p04-Raw_Handover_Task.mp4 | 2 |
| 5 | Information flow through the system | 40 | full_image | ch2_fig_flow.png | information_flow |
| 6 | Experimental setup and measurements | 5 | divider | - | divider_2 |
| 7 | Static marker calibration | 40 | frame_figure | overlay_static_markers.png | static_marker_calibration |
| 8 | Landmark acceptance | 40 | landmark_video | p06-Accepted_Body_Landmarks_With_Axes.mp4; viewport [160, 104, 1120, 824] | landmark_acceptance |
| 9 | Hampel spike removal | 40 | composite | p07-Hampel_Spike_Removal.mp4; masks [[32, 145, 365, 202], [32, 215, 365, 270]] | filter_hampel |
| 10 | Short-gap interpolation | 30 | composite | p08-Short_Gap_Interpolation.mp4; masks [[32, 145, 365, 202], [32, 215, 365, 270]] | filter_short_gap |
| 11 | Butterworth smoothing | 30 | composite | p09-Offline_Butterworth_Smoothing.mp4; masks [[32, 145, 365, 202], [32, 215, 365, 270]] | filter_butterworth |
| 12 | Kinematic modelling | 5 | divider | - | divider_3 |
| 13 | Camera and Camera' frames | 40 | frame_figure | overlay_camera_frames.png | camera_frames_overlay |
| 14 | Landmark frames and the T-pose reference | 30 | frame_figure | overlay_landmark_frames.png | frames_tpose |
| 15 | Torso and root frame | 60 | frame_figure | overlay_torso_root.png | torso_root_overlay |
| 16 | Recorded torso frame | 35 | composite | p13-Torso_Frame_From_Standing_T_Pose.mp4; masks [[34, 14, 380, 61], [38, 128, 276, 172]] | torso_frame |
| 17 | Shoulder swing and twist | 55 | composite | p15-Shoulder_Twist_About_Upper_Arm_Axis.mp4; masks [[34, 14, 432, 61], [38, 128, 276, 172], [1230, 1074, 1413, 1113]] | shoulder_swing_twist |
| 18 | Elbow | 35 | composite | p16-Elbow_Rotation_Onto_Forearm.mp4; masks [[34, 14, 266, 61], [38, 128, 276, 172]] | elbow |
| 19 | Object tracking and scene reconstruction | 5 | divider | - | divider_4 |
| 20 | Object pose in the World frame | 50 | frame_figure | overlay_object_world.png | 6 |
| 21 | Pose recovery during tracking failure | 5 | divider | - | divider_5 |
| 22 | Output states and holding context | 70 | grip_video | p23-Holding_Input_And_Torso_Rejection_With_Axes.mp4; viewport [0, 78, 960, 970] | states_holding |
| 23 | Grasp offset held through tracking loss | 60 | composite | p25-Grasp_Offset_During_Wrist_Depth_Loss_With_Axes.mp4; masks [[44, 22, 1167, 80], [20, 240, 242, 662]] | grasp_offset_retention |
| 24 | The circle of possible elbows | 45 | composite | p29-Elbow_Endpoint_Constraint_Circle_With_Axes.mp4; masks [[44, 22, 1167, 80], [20, 240, 242, 662]] | elbow_circle |
| 25 | Selecting one elbow and the direction-memory fallback | 70 | fallback_video | p32-Controlled_Held_Joint_Fallback.mp4; viewport [0, 78, 960, 798] | elbow_selection_fallback |
| 26 | System integration and graphical reconstruction | 5 | divider | - | divider_6 |
| 27 | One frame through the system | 45 | composite | p33-Single_Frame_Data_Flow.mp4; masks [[44, 22, 1015, 80]] | 28 |
| 28 | Mapping into the scene | 50 | frame_figure | overlay_scene_mapping.png | scene_rig |
| 29 | Applying the rig | 60 | frame_figure | overlay_rig_frames.png | rig_frames_overlay |
| 30 | Integrated reconstruction | 35 | composite | p41-Archived_Pose_Replay_With_Model_Axes.mp4; viewport [336, 64, 1104, 1188] | 35 |
| 31 | Experimental evaluation | 5 | divider | - | divider_7 |
| 32 | Object reconstruction accuracy | 45 | evaluation_figures | ch7_video_context_r6b.png; ch7_object_waypoints_r6b.png; ch7_object_waypoints_r6b.png | object_rig_accuracy |
| 33 | Human reconstruction accuracy | 65 | evaluation_figures | ch7_visual_examples_r7.png | ch7_results_table |
| 34 | Recovery under landmark failure: synthetic removal | 55 | table | - | synthetic_removal |
| 35 | Recovery under natural occlusion | 60 | evaluation_figures | r5_label_compare_f1890.png; r5_label_compare_f1462.png | right_failure |
| 36 | Imperfect handover replay | 50 | composite | p47-Fresh_Unity_Handover_With_Model_Axes.mp4; viewport [345, 64, 1104, 1188] | 53 |
| 37 | Real-time feasibility | 5 | divider | - | divider_8 |
| 38 | Offline pass and causal structure | 45 | full_image | ch8_fig_system.png | offline_causal_structure |
| 39 | Causal processing and adaptive smoothing | 70 | composite | p49-Causal_One_Euro_Filtering.mp4; masks [[32, 145, 365, 202], [32, 215, 365, 270]] | causal_smoothing |
| 40 | Discussions | 5 | divider | - | divider_9 |
| 41 | Discussions | 65 | composite | p27-Fresh_Unity_Wrist_Loss_With_Model_Axes.mp4; viewport [345, 64, 1104, 1188] | discussion |
| 42 | Conclusions | 5 | divider | - | divider_10 |
| 43 | Limitations | 65 | full_table | - | 38 |
| 44 | Contributions | 65 | full_table | - | 55 |
| 45 | References (1 of 2) | 5 | full_table | - | references |
| 46 | References (2 of 2) | 5 | full_table | - | references_2 |
| 47 | Thank you | 5 | thanks | - | thanks |
| 48 | Question | 10 | closing | - | 39 |

### Hidden pages 49-76

| # | Title | Dur (s) | Kind | Media and figures | Legacy key |
|---:|---|---:|---|---|---|
| 49 | ArUco vs AprilTag in the published literature | 0 | full_table | - | qa_marker_literature |
| 50 | AprilTag 3 faster, corner errors converge at 96 px | 0 | full_image | chart_marker_bench.png | qa_marker_bench |
| 51 | Transport candidates | 0 | full_table | - | qa_transport_candidates |
| 52 | Moving one frame package from Python to Unity | 0 | full_image | chart_transport_package.png | qa_transport_package |
| 53 | Savitzky-Golay filtering | 0 | composite | p67-Savitzky_Golay_Filtering.mp4; masks [[32, 145, 365, 202], [32, 215, 365, 270]] | qa_filter_savgol |
| 54 | Median filtering | 0 | composite | p68-Median_Filtering.mp4; masks [[32, 145, 365, 202], [32, 215, 365, 270]] | qa_filter_median |
| 55 | One Euro filtering | 0 | composite | p46-Causal_One_Euro_Filtering.mp4; masks [[32, 145, 365, 202], [32, 215, 365, 270]] | qa_filter_one_euro |
| 56 | Butterworth for offline smoothing | 0 | panel_chart | chart_filter_offline_panel.png | qa_filter_offline_choice |
| 57 | One Euro for real-time smoothing | 0 | panel_chart | chart_filter_realtime_panel.png | qa_filter_realtime_choice |
| 58 | Derivation: Camera' and the chain (Eqs. 3.1-3.3) (1 of 2) | 0 | derivation | - | qa_derivation_3_1_part1 |
| 59 | Derivation: Camera' and the chain (Eqs. 3.4-3.6) (2 of 2) | 0 | derivation | - | qa_derivation_3_1_part2 |
| 60 | Derivation: Torso and root frame (Eqs. 3.7-3.9) (1 of 2) | 0 | derivation | - | qa_derivation_3_7_part1 |
| 61 | Derivation: Torso and root frame (Eqs. 3.10-3.12) (2 of 2) | 0 | derivation | - | qa_derivation_3_7_part2 |
| 62 | Derivation: Shoulder and elbow frames (Eqs. 3.13-3.14) | 0 | derivation | - | qa_derivation_3_13 |
| 63 | Derivation: Root Euler angles (Eqs. 3.15-3.17) | 0 | derivation | - | qa_derivation_3_15 |
| 64 | Derivation: Shoulder swing and twist (Eqs. 3.18-3.23) | 0 | derivation | - | qa_derivation_3_18 |
| 65 | Derivation: Elbow coordinates (Eq. 3.24) | 0 | derivation | - | qa_derivation_3_24 |
| 66 | Derivation: Object pose in World (Eqs. 4.1-4.2) | 0 | derivation | - | qa_derivation_4_1 |
| 67 | Derivation: Grasp offset (Eqs. 5.1-5.4) | 0 | derivation | - | qa_derivation_5_1 |
| 68 | Derivation: Direction memory and wrist target (Eqs. 5.5-5.7) | 0 | derivation | - | qa_derivation_5_5 |
| 69 | Derivation: Elbow circle and prior (Eqs. 5.8-5.10) (1 of 2) | 0 | derivation | - | qa_derivation_5_8_part1 |
| 70 | Derivation: Elbow circle and prior (Eqs. 5.11-5.12) (2 of 2) | 0 | derivation | - | qa_derivation_5_8_part2 |
| 71 | Derivation: Mapping into Scene (Eq. 6.1) (1 of 2) | 0 | derivation | - | qa_derivation_6_1_part1 |
| 72 | Derivation: Mapping into Scene (Eqs. 6.2-6.3) (2 of 2) | 0 | derivation | - | qa_derivation_6_1_part2 |
| 73 | Derivation: Rig chain and rest axes (Eqs. 6.4-6.5) | 0 | derivation | - | qa_derivation_6_4 |
| 74 | Derivation: Gravity and floor (Eq. 6.6) | 0 | derivation | - | qa_derivation_6_6 |
| 75 | Derivation: Evaluation measures (Eqs. 7.1-7.2) (1 of 2) | 0 | derivation | - | qa_derivation_7_1_part1 |
| 76 | Derivation: Evaluation measures (Eqs. 7.3-7.6) (2 of 2) | 0 | derivation | - | qa_derivation_7_1_part2 |

## Round-9 deck (build 67, 2026-09-30; history under the round-10 section above)

Verified: 2026-09-30, working tree on HEAD ceb67d4 (uncommitted at the time of
writing). Re-read this task: review/ARTIFACT_CHECK.json (status PARTIAL,
package_status PASS, 2100 checks all PASS, main_slides 46, backup_slides 31,
planned_main_seconds 1795, main_script_words 3395), talk_content.json pages 8,
9, 18, 30, 37, 43, 44, backup_content.json pages 47-48, 51-58,
equations/derivation_leads.json eq_3_18, figures/coordinate_frames/overlay/
{manifest.json,NOTES.md}. PPTX sha256 2d5747d7..., PDF 21994d79... (d22bb0c3...
before the D-303 re-render; the PPTX bytes did not change).
Sources: presentation/defense_2026/{talk_content.json,backup_content.json,
build_deck.py,validate_deck.py,DECISIONS.md D-297 to D-303}.
Answers: what changed in the deck from round 8 (build 66) to build 67.

Page count, order, durations (1795 s = 29:55) and media bytes are those of
the round-8 deck below. Changes:

- References pages 43 and 44 are the deck's own IEEE list [1]..[12]
  (columns "No." and "Reference", widths 0.06 / 0.94, six rows each), in
  order of first citation; eight rows are verbatim from the thesis
  reference list (D-297, D-298). Details: knowledge/references.md.
- In-text citations are numbers: pages 8, 30 ([1]), 9 ([2], [3]), 37 ([4]);
  hidden pages 47, 48, 51, 53, 54, 56, 57, 58 (D-297). No author-year string
  remains in any visible text or note.
- build_deck.py restrained_full_table draws three-line rows 0.30 in taller
  (D-299); only page 43 changes geometry among the full_table pages.
- Hidden page 65 (Eq. 3.18) quotes the compiled thesis "[52]" (D-300).
- Page 18 (Object pose in the World frame) has a fourth frame, Wall, in
  projected mode from T_cam_wall (eval/output/scene_calibration_r6bc.json),
  reprojection residual 0.08 px against the detected marker ID 0; World:
  fixed desk marker; Wall: gravity reference; caption "World, Object and
  Wall projected from calibration."; footer "Sections 2.2.2, 4.1; Eq. 4.1";
  the Camera legend moved to the upper-right corner (D-302). Frames on the
  overlay: World projected, Object projected, Wall projected, Camera
  illustrative.
- validate_deck.py: 2100 checks (2098 before the D-303 code-review fixes,
  2092 at build 66); the author-year checks are replaced by numeric-citation
  rules 1-9 (D-297, D-300, D-301); D-303 adds the drawn-table binding of
  every full_table page and widens rules 3 and 4.
- Decision range: D-109..D-303 (round 9 is D-297..D-303). The round-5
  files references/KEY_USAGE.md and references/page50_snippet.json were
  deleted (D-301).

## Round-8 deck (builds 63-66, 2026-09-30; history under the round-9 section above)

Verified: 2026-09-30 at HEAD aed90fe (build 66). Re-read this task:
talk_content.json (46 pages, durations sum 1795 s), backup_content.json
(31 pages, ids 47-77, all duration 0), review/ARTIFACT_CHECK.json (status
PARTIAL, package_status PASS, 2092 checks all PASS, main_slides 46,
backup_slides 31, planned_main_seconds 1795, main_script_words 3357,
focus_seconds context 225 / methodology 1030 / evaluation 350 /
conclusion 180 / questions 10), review/RENDER_CHECK.json (77 preview
pages), review/SCRIPT_EXPORT_CHECK.json (312 paragraphs, 77 slide
headings, 19 PDF pages), pdfinfo (deck PDF 77 pages). PPTX sha256
e1189479..., PDF 1aa1a4b9.... Decisions D-109..D-295.
Sources: presentation/defense_2026/{talk_content.json,backup_content.json,
build_deck.py,DECISIONS.md,review/ARTIFACT_CHECK.json,
committee_materials/unified_revision/media_contract.json}.
Answers: the page-by-page contents of the current defence deck, the build
mechanism, the hidden pages and the decisions that cover them.

46 main pages (1795 s = 29:55) and 31 hidden pages (47-77, show="0",
reached by typed slide number). Built from round 7 (39 + 14, 1785 s) by
four builds: 63 (43 + 12, 1790 s, 1439 checks), 64 (46 + 12, 1795 s, 1539),
65 (46 + 31, 2081), 66 (2092). Nine dividers: 7, 10, 17, 19, 24, 29, 35, 38,
40. References are main pages 43-44 (D-267); Thank you is 45 (kind thanks,
one centred 60 pt word); Question is 46 (kind closing). The hidden
filter, marker and transport pages keep their round-7 content at pages
47-58; derivation pages 59-77 are new.

### Main pages (legacy key = the key the validator uses to find the page)

| # | Title | Dur (s) | Kind | Media and figures | Legacy key |
|---:|---|---:|---|---|---|
| 1 | Tracking and Reconstruction of Bi-Manual Object Handling Task Using RGB-D Sensing | 20 | cover | - | 1 |
| 2 | Presentation outline | 30 | outline | - | presentation_outline |
| 3 | Motivation | 50 | table | - | motivation |
| 4 | Information flow through the system | 45 | full_image | ch2_fig_flow.png | information_flow |
| 5 | The task: bimanual object handling under one RGB-D camera | 75 | task_video | p05-Raw_Task_Context.mp4; masks [[0, 458, 276, 480]] | 2 |
| 6 | Research question and assumptions | 50 | scope | - | 3 |
| 7 | Experimental setup and measurements | 5 | divider | - | divider_2 |
| 8 | Camera, calibration and landmark acceptance | 55 | landmark_video | p06-Accepted_Body_Landmarks_With_Axes.mp4; viewport [160, 104, 1120, 824] | calibration_landmarks |
| 9 | Signal conditioning: spikes, gaps, smoothing | 60 | composite | p09-Offline_Butterworth_Smoothing.mp4; masks [[32, 145, 365, 202], [32, 215, 365, 270]] | signal_conditioning |
| 10 | Kinematic modelling | 5 | divider | - | divider_3 |
| 11 | Camera and Camera-prime frames | 30 | frame_figure | overlay_camera_frames.png | camera_frames_overlay |
| 12 | Landmark frames and the T-pose reference | 50 | frame_figure | overlay_landmark_frames.png | frames_tpose |
| 13 | Torso and root frame | 30 | frame_figure | overlay_torso_root.png | torso_root_overlay |
| 14 | Torso frame | 50 | composite | p13-Torso_Frame_From_Standing_T_Pose.mp4; masks [[34, 14, 380, 61], [38, 128, 276, 172]] | torso_frame |
| 15 | Shoulder swing and twist | 50 | composite | p15-Shoulder_Twist_About_Upper_Arm_Axis.mp4; masks [[34, 14, 432, 61], [38, 128, 276, 172], [1230, 1074, 1413, 1113]] | shoulder_swing_twist |
| 16 | Elbow | 45 | composite | p16-Elbow_Rotation_Onto_Forearm.mp4; masks [[34, 14, 266, 61], [38, 128, 276, 172]] | elbow |
| 17 | Object tracking and scene reconstruction | 5 | divider | - | divider_4 |
| 18 | Object pose in the World frame | 45 | frame_figure | overlay_object_world.png (World, Object, Wall projected; Camera illustrative since build 67) | 6 |
| 19 | Pose recovery during tracking failure | 5 | divider | - | divider_5 |
| 20 | Output states and holding context | 65 | grip_video | p23-Holding_Input_And_Torso_Rejection_With_Axes.mp4; viewport [0, 78, 960, 970] | states_holding |
| 21 | Grasp offset held through tracking loss | 60 | composite | p25-Grasp_Offset_During_Wrist_Depth_Loss_With_Axes.mp4; masks [[44, 22, 1167, 80], [20, 240, 242, 662]] | grasp_offset_retention |
| 22 | The circle of possible elbows | 60 | composite | p29-Elbow_Endpoint_Constraint_Circle_With_Axes.mp4; masks [[44, 22, 1167, 80], [20, 240, 242, 662]] | elbow_circle |
| 23 | Selecting one elbow and the direction-memory fallback | 70 | fallback_video | p32-Controlled_Held_Joint_Fallback.mp4; viewport [0, 78, 960, 798] | elbow_selection_fallback |
| 24 | System integration and graphical reconstruction | 5 | divider | - | divider_6 |
| 25 | One frame through the system | 65 | composite | p33-Single_Frame_Data_Flow.mp4; masks [[44, 22, 1015, 80]] | 28 |
| 26 | Mapping into the scene | 45 | frame_figure | overlay_scene_mapping.png | scene_rig |
| 27 | Applying the rig | 30 | frame_figure | overlay_rig_frames.png | rig_frames_overlay |
| 28 | Integrated reconstruction | 60 | composite | p41-Archived_Pose_Replay_With_Model_Axes.mp4; viewport [336, 64, 1104, 1188] | 35 |
| 29 | Experimental evaluation | 5 | divider | - | divider_7 |
| 30 | Object reconstruction accuracy | 70 | evaluation_figures | ch7_video_context_r6b.png; ch7_object_waypoints_r6b.png | object_rig_accuracy |
| 31 | Human reconstruction accuracy | 70 | evaluation_figures | ch7_visual_examples_r7.png | ch7_results_table |
| 32 | Recovery under landmark failure: synthetic removal | 60 | table | - | synthetic_removal |
| 33 | Recovery under natural occlusion | 75 | evaluation_figures | r5_label_compare_f1890.png; r5_label_compare_f1462.png | right_failure |
| 34 | Imperfect handover replay | 70 | composite | p47-Fresh_Unity_Handover_With_Model_Axes.mp4; viewport [345, 64, 1104, 1188] | 53 |
| 35 | Real-time feasibility | 5 | divider | - | divider_8 |
| 36 | Offline pass and causal structure | 30 | full_image | ch8_fig_system.png | offline_causal_structure |
| 37 | Causal processing and adaptive smoothing | 55 | composite | p49-Causal_One_Euro_Filtering.mp4; masks [[32, 145, 365, 202], [32, 215, 365, 270]] | causal_smoothing |
| 38 | Discussions | 5 | divider | - | divider_9 |
| 39 | Discussions | 45 | composite | p27-Fresh_Unity_Wrist_Loss_With_Model_Axes.mp4; viewport [345, 64, 1104, 1188] | discussion |
| 40 | Conclusions | 5 | divider | - | divider_10 |
| 41 | Limitations | 55 | full_table | - | 38 |
| 42 | Contributions | 55 | full_table | - | 55 |
| 43 | References (1 of 2) | 5 | full_table | - (rows [1]-[6], D-298) | references |
| 44 | References (2 of 2) | 5 | full_table | - (rows [7]-[12], D-298) | references_2 |
| 45 | Thank you | 5 | thanks | - | thanks |
| 46 | Question | 10 | closing | - | 39 |

### Hidden pages 47-77

| # | Title | Dur (s) | Kind | Media and figures | Legacy key |
|---:|---|---:|---|---|---|
| 47 | ArUco vs AprilTag in the published literature | 0 | full_table | - | qa_marker_literature |
| 48 | AprilTag 3 faster; corner errors converge at 96 px | 0 | full_image | chart_marker_bench.png | qa_marker_bench |
| 49 | Transport candidates | 0 | full_table | - | qa_transport_candidates |
| 50 | Moving one frame package from Python to Unity | 0 | full_image | chart_transport_package.png | qa_transport_package |
| 51 | Hampel spike removal | 0 | composite | p07-Hampel_Spike_Removal.mp4; masks [[32, 145, 365, 202], [32, 215, 365, 270]] | qa_filter_hampel |
| 52 | Short-gap interpolation | 0 | composite | p08-Short_Gap_Interpolation.mp4; masks [[32, 145, 365, 202], [32, 215, 365, 270]] | qa_filter_gap |
| 53 | Butterworth smoothing | 0 | composite | p43-Offline_Butterworth_Smoothing.mp4; masks [[32, 145, 365, 202], [32, 215, 365, 270]] | qa_filter_butterworth |
| 54 | Savitzky-Golay filtering | 0 | composite | p67-Savitzky_Golay_Filtering.mp4; masks [[32, 145, 365, 202], [32, 215, 365, 270]] | qa_filter_savgol |
| 55 | Median filtering | 0 | composite | p68-Median_Filtering.mp4; masks [[32, 145, 365, 202], [32, 215, 365, 270]] | qa_filter_median |
| 56 | One Euro filtering | 0 | composite | p46-Causal_One_Euro_Filtering.mp4; masks [[32, 145, 365, 202], [32, 215, 365, 270]] | qa_filter_one_euro |
| 57 | Butterworth for offline smoothing | 0 | panel_chart | chart_filter_offline_panel.png | qa_filter_offline_choice |
| 58 | One Euro for real-time smoothing | 0 | panel_chart | chart_filter_realtime_panel.png | qa_filter_realtime_choice |
| 59 | Derivation: Camera-prime and the chain (Eqs. 3.1-3.3) (1 of 2) | 0 | derivation | - | qa_derivation_3_1_part1 |
| 60 | Derivation: Camera-prime and the chain (Eqs. 3.4-3.6) (2 of 2) | 0 | derivation | - | qa_derivation_3_1_part2 |
| 61 | Derivation: Torso and root frame (Eqs. 3.7-3.9) (1 of 2) | 0 | derivation | - | qa_derivation_3_7_part1 |
| 62 | Derivation: Torso and root frame (Eqs. 3.10-3.12) (2 of 2) | 0 | derivation | - | qa_derivation_3_7_part2 |
| 63 | Derivation: Shoulder and elbow frames (Eqs. 3.13-3.14) | 0 | derivation | - | qa_derivation_3_13 |
| 64 | Derivation: Root Euler angles (Eqs. 3.15-3.17) | 0 | derivation | - | qa_derivation_3_15 |
| 65 | Derivation: Shoulder swing and twist (Eqs. 3.18-3.23) | 0 | derivation | - | qa_derivation_3_18 |
| 66 | Derivation: Elbow coordinates (Eq. 3.24) | 0 | derivation | - | qa_derivation_3_24 |
| 67 | Derivation: Object pose in World (Eqs. 4.1-4.2) | 0 | derivation | - | qa_derivation_4_1 |
| 68 | Derivation: Grasp offset (Eqs. 5.1-5.4) | 0 | derivation | - | qa_derivation_5_1 |
| 69 | Derivation: Direction memory and wrist target (Eqs. 5.5-5.7) | 0 | derivation | - | qa_derivation_5_5 |
| 70 | Derivation: Elbow circle and prior (Eqs. 5.8-5.10) (1 of 2) | 0 | derivation | - | qa_derivation_5_8_part1 |
| 71 | Derivation: Elbow circle and prior (Eqs. 5.11-5.12) (2 of 2) | 0 | derivation | - | qa_derivation_5_8_part2 |
| 72 | Derivation: Mapping into Scene (Eq. 6.1) (1 of 2) | 0 | derivation | - | qa_derivation_6_1_part1 |
| 73 | Derivation: Mapping into Scene (Eqs. 6.2-6.3) (2 of 2) | 0 | derivation | - | qa_derivation_6_1_part2 |
| 74 | Derivation: Rig chain and rest axes (Eqs. 6.4-6.5) | 0 | derivation | - | qa_derivation_6_4 |
| 75 | Derivation: Gravity and floor (Eq. 6.6) | 0 | derivation | - | qa_derivation_6_6 |
| 76 | Derivation: Evaluation measures (Eqs. 7.1-7.2) (1 of 2) | 0 | derivation | - | qa_derivation_7_1_part1 |
| 77 | Derivation: Evaluation measures (Eqs. 7.3-7.6) (2 of 2) | 0 | derivation | - | qa_derivation_7_1_part2 |

Derivation pages (kind derivation, D-281): each stacks full width one 16 pt
verbatim lead line from equations/derivation_leads.json above the white
numbered thesis crop of each equation at source scale 1.4; 50 crops in all.
Supported main pages: 59-60 page 11; 61-62 page 13; 63 page 12; 64 page 14;
65 page 15; 66 page 16; 67 page 18; 68 page 21; 69 page 23; 70-71 pages 22
and 23; 72-73 and 75 page 26; 74 page 27; 76-77 page 30.

### Build mechanism

build_deck.py reads talk_content.json (46 page dicts) and backup_content.json
(31 page dicts). Hidden mechanism: build_deck.py line 1316
`if s['id']>main_count:slide._element.set('show','0')` (re-read 2026-09-30),
so every slide with id greater than 46 is hidden. validate_deck.py finds
pages by legacy key (for example EVALUATION_KEYS, the References pages and
the closing pages), not by fixed page number (D-274, D-267).

### Visual kinds added or changed in round 8

- frame_figure with `visual.overlay`: pages 11, 12, 13, 18, 26, 27 place an
  overlay PNG of figures/coordinate_frames/overlay/ (6.61 x 5.00 in box,
  one-line caption) bound by overlay/manifest.json and the
  visual.overlay_manifest_sha256 field (D-270, D-273, D-290).
- full_image thesis figures: page 4 (Figure 2.3) and page 36 (Figure 8.1),
  byte-identical copies in figures/thesis/ bound by figures/thesis/manifest.json,
  placed 5.00 in tall and centred (D-264).
- thanks: page 45, closing layout (D-267).
- derivation: hidden pages 59-77 (D-281).
- composite with `caption_under_bullets`: page 39 (D-269).
- The round-7 kinds information_flow, anchored_photos and the page-33
  left_diagram were removed (D-264, D-273).
- Decision range: D-109..D-295 (round 8 is D-263..D-295).

### Round-7 deck (history; superseded by the round-8 deck above)

Round-7 deck (builds 57-60, 2026-09-29):

Same 39 main + 14 hidden pages, order and 1785 s budget as the restored
deck below; content, layouts and some figures changed by the author's
slide-change list (plan items 1-11; DECISIONS.md D-245 to D-260).
Kinds now in use: cover, outline, table, information_flow, task_video, scope,
divider, landmark_video, composite, frame_figure, grip_video, fallback_video,
anchored_photos (page 24), evaluation_figures (27, 28, 30), full_table (37,
38, hidden 40, 42, 52, 53), closing (39, only "Question" at 60 pt),
full_image (41, 43), panel_chart (50, 51). The kinds figure_pair,
object_chart and human_chart were deleted from build_deck.py in build 60
(D-260). Content pages draw no 11 pt chapter kicker (D-245).

Verified: 2026-09-29. Table generated from talk_content.json and
backup_content.json at commit c394fde (build 60); validate_deck.py --pdf
1372 checks, 0 package failures; pdfinfo 53 pages.
Sources: presentation/defense_2026/{talk_content.json,backup_content.json,
build_deck.py,DECISIONS.md,review/ARTIFACT_CHECK.json}.

| # | Title | Dur (s) | Kind | Media and figures |
|---:|---|---:|---|---|
| 1 | Tracking and Reconstruction of Bi-Manual Object Handling Task Using RGB-D Sensing | 20 | cover | - |
| 2 | Presentation outline | 30 | outline | - |
| 3 | Motivation | 50 | table | - |
| 4 | Information flow through the system | 60 | information_flow | native diagram |
| 5 | The task: bimanual object handling under one RGB-D camera | 75 | task_video | p05-Raw_Task_Context.mp4 |
| 6 | Research question and assumptions | 50 | scope | - |
| 7 | Experimental setup and measurements | 5 | divider | - |
| 8 | Camera, calibration and landmark acceptance | 55 | landmark_video | p06-Accepted_Body_Landmarks_With_Axes.mp4 |
| 9 | Signal conditioning: spikes, gaps, smoothing | 70 | composite | p09-Offline_Butterworth_Smoothing.mp4 |
| 10 | Kinematic modelling | 5 | divider | - |
| 11 | Frames and the T-pose reference | 70 | frame_figure | thesis_fig3_5_reference_pose.png |
| 12 | Torso frame | 65 | composite | p13-Torso_Frame_From_Standing_T_Pose.mp4 |
| 13 | Shoulder swing and twist | 60 | composite | p15-Shoulder_Twist_About_Upper_Arm_Axis.mp4 |
| 14 | Elbow | 50 | composite | p16-Elbow_Rotation_Onto_Forearm.mp4 |
| 15 | Object tracking and scene reconstruction | 5 | divider | - |
| 16 | Object pose in the world frame | 50 | frame_figure | object_frames.png |
| 17 | Pose recovery during tracking failure | 5 | divider | - |
| 18 | Output states and holding context | 65 | grip_video | p23-Holding_Input_And_Torso_Rejection_With_Axes.mp4 |
| 19 | Grasp offset held through tracking loss | 60 | composite | p25-Grasp_Offset_During_Wrist_Depth_Loss_With_Axes.mp4 |
| 20 | The circle of possible elbows | 60 | composite | p29-Elbow_Endpoint_Constraint_Circle_With_Axes.mp4 |
| 21 | Selecting one elbow and the direction-memory fallback | 70 | fallback_video | p32-Controlled_Held_Joint_Fallback.mp4 |
| 22 | System integration and graphical reconstruction | 5 | divider | - |
| 23 | One frame through the system | 65 | composite | p33-Single_Frame_Data_Flow.mp4 |
| 24 | Mapping into the scene and applying the rig | 65 | anchored_photos | r6b_frame00505.png; r6b_unity_f00505.png |
| 25 | Integrated reconstruction | 60 | composite | p41-Archived_Pose_Replay_With_Model_Axes.mp4; crop [336, 64, 1104, 1188] |
| 26 | Experimental evaluation | 5 | divider | - |
| 27 | 7.2 Object reconstruction accuracy | 70 | evaluation_figures | ch7_video_context_r6b.png; ch7_object_waypoints_r6b.png |
| 28 | 7.3 Human reconstruction accuracy | 70 | evaluation_figures | ch7_visual_examples_r7.png |
| 29 | 7.4 Recovery under landmark failure: synthetic removal | 60 | table | - |
| 30 | 7.4 Recovery under natural occlusion | 75 | evaluation_figures | r5_label_compare_f1890.png; r5_label_compare_f1462.png |
| 31 | Imperfect handover replay | 70 | composite | p47-Fresh_Unity_Handover_With_Model_Axes.mp4; crop [345, 64, 1104, 1188] |
| 32 | Real-time feasibility | 5 | divider | - |
| 33 | Causal processing and adaptive smoothing | 70 | composite | p49-Causal_One_Euro_Filtering.mp4; masks [[32, 145, 365, 202], [32, 215, 365, 270]]; native diagram |
| 34 | Discussions | 5 | divider | - |
| 35 | Discussions | 55 | composite | p35-Fresh_Unity_Handover_Discussion.mp4; crop [345, 64, 1104, 1188] |
| 36 | Conclusions | 5 | divider | - |
| 37 | Limitations | 55 | full_table | - |
| 38 | Contributions | 55 | full_table | - |
| 39 | Question | 10 | closing | - |
| 40 | ArUco vs AprilTag: what the literature reports | 0 | full_table | - |
| 41 | AprilTag 3 faster; corner errors converge at 96 px | 0 | full_image | chart_marker_bench.png |
| 42 | Transport candidates | 0 | full_table | - |
| 43 | Moving one frame package from Python to Unity | 0 | full_image | chart_transport_package.png |
| 44 | Hampel spike removal | 0 | composite | p07-Hampel_Spike_Removal.mp4 |
| 45 | Short-gap interpolation | 0 | composite | p08-Short_Gap_Interpolation.mp4 |
| 46 | Butterworth smoothing | 0 | composite | p43-Offline_Butterworth_Smoothing.mp4 |
| 47 | Savitzky-Golay filtering | 0 | composite | p67-Savitzky_Golay_Filtering.mp4 |
| 48 | Median filtering | 0 | composite | p68-Median_Filtering.mp4 |
| 49 | One Euro filtering | 0 | composite | p46-Causal_One_Euro_Filtering.mp4 |
| 50 | Why Butterworth offline | 0 | panel_chart | chart_filter_offline_panel.png |
| 51 | Why One Euro in real time | 0 | panel_chart | chart_filter_realtime_panel.png |
| 52 | References (1 of 2) | 0 | full_table | - |
| 53 | References (2 of 2) | 0 | full_table | - |

The round-6 table further below is the pre-round-7 state (titles on pages
19, 27-30, 37-39 changed since).

## Restored round-6 deck (2026-09-29, D-244; history)

The current defence deck is the compact round-6 deck: 39 main pages plus 14
hidden pages, 1785 s = 29:45. Its bytes (Thesis_Defence_2026.pptx, .pdf,
talk_content.json, build_deck.py) were restored on 2026-09-29 from commit
c5440c4 by commits f6e2ec4, 788beab and 237fdef (decision D-244 in
presentation/defense_2026/DECISIONS.md; restore table in
presentation/defense_2026/review/RESTORE_2026-09-29.md). The later Codex decks
(a202509..ddfdf40: an argument-led 38+14 deck, then a 66-main/39-hidden
restoration) are discarded and exist only in git history; D-218 to D-243 are
superseded. Why they were discarded and the review of the restored deck:
deck_defects_2026-09-29.md.

Current checker commands (thesis Python /home/luo/anaconda3/bin/python, from
presentation/defense_2026/): `validate_deck.py --pdf Thesis_Defence_2026.pdf`,
`export_defense_script.py --pdf`, `make_package.py --require-clean`;
`render_deck.py` only when the PPTX is rebuilt. See checkers_and_caches.md.

Verified: 2026-09-29. Re-checked against the files in this task: page ids,
titles and durations of talk_content.json (39 pages, sum 1785 s) and
backup_content.json (14 pages, ids 40-53, kinds); sha1 of the working-tree
Thesis_Defence_2026.pptx equal to the c5440c4 blob; pdfinfo (deck PDF 53
pages, DEFENSE_SCRIPT.pdf 14 pages); review/ARTIFACT_CHECK.json (status
PARTIAL, package_status PASS, main 39, backup 14, 1785 s);
review/SCRIPT_EXPORT_CHECK.json (216 paragraphs); package/MANIFEST.json
(commit f6e2ec4, 39 main, 14 hidden, 18 embedded MP4, 1331 checks).
Not re-checked: the round-6 prose below (checks, decisions D-205 to D-217)
was carried over from the build-45 verification; validate_deck.py was not
rerun in this task (the master ran it: 1331 checks, 0 package failures).
Sources: presentation/defense_2026/{talk_content.json,backup_content.json,
build_deck.py,DECISIONS.md,revision_id_map.json,review/ARTIFACT_CHECK.json,
review/SCRIPT_EXPORT_CHECK.json,package/MANIFEST.json}.
Answers: the page-by-page contents of the restored round-6 deck, its build
mechanism, the hidden topic pages and the decisions that cover them.

## Round-6 deck and feedback follow-up (build 45; history)

53 pages: main 1-39 (1785 s = 29:45; focus seconds context 225,
methodology 1025 (57.4 percent), evaluation 350, conclusion 175,
questions 10), hidden 40-53 (untimed, duration 0, show="0", reached by typed
slide number). Professor's round-6 feedback (relayed by the author):
slide 2 must be a table of contents of the presentation, right after
the title; the first Introduction slide must motivate the work; the
outline is about the logic of the defence, not the thesis map; the
Introduction chapter divider is not needed; Discussions and
Conclusions each need a heading, with Limitations and Contributions
under Conclusions. The 2026-09-29 review of the restored deck found all
of these met (deck_defects_2026-09-29.md).

The 2026-09-29 follow-up swaps Motivation and information flow to pages
3 and 4, and uses "Discussions" in the outline and pages 34-35 (D-216).
D-217 replaces the unfinished first Motivation bullet with "Robot
learning, VR avatars and potential clinical assessment". The original round-5
page 3 was the thesis map, as confirmed at commit 7614fd2; that removed
page is distinct from today's preserved system diagram.

Recorded at build 45 (review/FEEDBACK_FOLLOWUP_CHECK.json): 1331 package
checks pass, zero package failures; 24 follow-up checks pass on
source/artifact order, unchanged media and share copies. Script export
preserves 216 paragraphs and 53 slide sections in 14 PDF pages (216
paragraphs and 14 pages re-checked 2026-09-29). Overall source validation
remains PARTIAL for D-058/D-066.

| # | Title | Dur (s) | Kind |
|---:|---|---:|---|
| 1 | Tracking and Reconstruction of Bi-Manual Object Handling Task Using RGB-D Sensing | 20 | cover |
| 2 | Presentation outline | 30 | outline (D-205, ten rows on the logic of the talk, not chapter titles) |
| 3 | Motivation | 50 | table (D-206/D-208/D-216/D-217; Table 1.1, custom column widths) |
| 4 | Information flow through the system | 60 | information_flow (round-5 page 2; D-216) |
| 5 | The task: bimanual object handling under one RGB-D camera | 75 | task_video |
| 6 | Research question and assumptions | 50 | scope |
| 7 | Experimental setup and measurements | 5 | divider |
| 8 | Camera, calibration and landmark acceptance | 55 | landmark_video (trimmed from 70 s, D-211) |
| 9 | Signal conditioning: spikes, gaps, smoothing | 70 | composite |
| 10 | Kinematic modelling | 5 | divider |
| 11 | Frames and the T-pose reference | 70 | frame_figure |
| 12 | Torso frame | 65 | composite |
| 13 | Shoulder swing and twist | 60 | composite (trimmed from 75 s, D-211) |
| 14 | Elbow | 50 | composite |
| 15 | Object tracking and scene reconstruction | 5 | divider |
| 16 | Object pose in the world frame | 50 | frame_figure |
| 17 | Pose recovery during tracking failure | 5 | divider |
| 18 | Output states and holding context | 65 | grip_video |
| 19 | Grasp offset and its retention through loss | 60 | composite (trimmed from 75 s, D-211) |
| 20 | The circle of possible elbows | 60 | composite (trimmed from 75 s, D-211) |
| 21 | Selecting one elbow and the direction-memory fallback | 70 | fallback_video |
| 22 | System integration and graphical reconstruction | 5 | divider |
| 23 | One frame through the system | 65 | composite (trimmed from 80 s, D-211) |
| 24 | Mapping into the scene and applying the rig | 65 | figure_pair |
| 25 | Integrated reconstruction | 60 | composite |
| 26 | Experimental evaluation | 5 | divider |
| 27 | Object and rig reconstruction accuracy | 70 | evaluation_charts |
| 28 | Chapter 7 results: object and body | 70 | full_table (Tables 7.1-7.4, D-175) |
| 29 | Synthetic landmark removal | 60 | table (Tables 7.6-7.7, D-175) |
| 30 | Right-arm tracking failure and the limited improvement | 75 | figure_pair |
| 31 | Imperfect handover replay | 70 | composite |
| 32 | Real-time feasibility | 5 | divider |
| 33 | Causal processing and adaptive smoothing | 70 | composite |
| 34 | Discussions | 5 | divider (D-207; plural heading D-216) |
| 35 | Discussions | 55 | composite (D-209/D-216; four bullets, page-31 handover film copied to the right) |
| 36 | Conclusions | 5 | divider (new, D-207/D-210) |
| 37 | Limitations | 55 | limits (old 35) |
| 38 | Contributions | 55 | contribution_table (old 36) |
| 39 | Questions | 10 | closing (old 37) |

The table was re-read from talk_content.json on 2026-09-29 (titles,
durations and kinds match). The nine dividers are 7, 10, 15, 17, 22, 26, 32,
34 and 36.

Hidden pages 40-53 (backup_content.json, re-read 2026-09-29): 40 ArUco vs
AprilTag literature (full_table), 41 AprilTag 3 faster; corner errors
converge at 96 px (full_image, chart_marker_bench.png), 42 transport
candidates (full_table), 43 Moving one frame package from Python to Unity
(full_image, chart_transport_package.png), 44-49 the six filter composite
pages (Hampel, short gaps, Butterworth, Savitzky-Golay, median, One Euro),
50-51 the two why-charts (panel_chart, chart_filter_offline_panel.png and
chart_filter_realtime_panel.png), 52-53 References (full_table). Their films
and committee copies are listed in media_inventory.md. No index page and no
internal link exists; a hidden page is reached only by typing its slide
number (D-128).

Media contract round 6, schema 9 (media_contract.json and
revision_id_map.json, schema_version 9 re-checked 2026-09-29): the round-5
contract, map and both VIDEO_INDEX levels are byte-copied to
committee_materials/unified_revision/history/round5_equations/; a committee
copy p35-Fresh_Unity_Handover_Discussion is bound to page 35 (byte-identical
to p47, keeps its burned-in "p47" label, D-132 precedent). validate_deck.py:
1331 checks, 0 package failures, overall PARTIAL (D-058/D-066 findings, pages
25 and 31 unchanged). Decisions D-205 to D-217 (D-172, D-173, D-174 annotated
as superseded by D-207/D-213, D-205/D-207 and D-211 respectively).

## Build (round-6 state, history; the round-8 mechanism is in the round-8 section above)

Built by `presentation/defense_2026/build_deck.py` from two content
files:
- `talk_content.json` -- the 39-page main talk (list of page dicts).
- `backup_content.json` -- the hidden pages (list of page dicts,
  14 entries, ids 40-53).

Outputs: `Thesis_Defence_2026.pptx`, `Thesis_Defence_2026.pdf`,
`DEFENSE_SCRIPT.md`/`.pdf`/`.docx`, `SPEAKER_NOTES.md`,
`preview/slide-NN.png`.

Hidden mechanism: build_deck.py line 1247
`if s['id']>main_count:slide._element.set('show','0')` marks any slide with id
greater than main_count (39) with PowerPoint's `show="0"` attribute, which
hides it from normal playback while keeping it navigable in the file (line
re-checked 2026-09-29). The closing page 39's speaker notes list every hidden
page's number and title (derived from backup_content.json, D-128).

## Visual kinds (dispatch table in build_deck.py; read 2026-09-28, round-8 kinds are listed above)

Carried over from the 2026-09-28 read; the dispatch table was not re-read
after the restore.

One line each, in dispatch order:
- `cover` -- title/author page, centered text only.
- `divider` -- black chapter-divider page (label + title, no footer).
- `composite` -- generic left-text/right-exhibit restrained page.
- `schematic` -- schematic diagram page.
- `setup` / `calibration` -- photo pages with a caption.
- `outline` -- section-name list page.
- `information_flow` -- six-node system diagram.
- `figure_pair` -- two images side by side or stacked.
- `evaluation_charts` -- object chart plus wrist-median chart from Ch7 tables.
- `hip_depth_manual` / `hip_depth_raw` -- hip-depth illustration photos.
- `frame_figure` -- a single coordinate-frame figure with caption.
- `evidence_image` / `evidence_pair` -- natural-failure evidence figures.
- `elbow_constraints` -- elbow endpoint-constraint visual.
- `torso` -- torso-frame visual.
- `arm_swing` / `arm_twist` / `arm_elbow` -- restrained arm photo variants.
- `elbow_prior` -- elbow prior visual.
- `offset_axes` / `offset_update` -- grasp-offset visuals.
- `observability` -- twist-observability visual.
- `landmark_video` / `grip_video` / `target_video` / `fallback_video` / `integrated_video` / `video` / `task_video` -- video-backed pages (restrained_video).
- `architecture` / `scope` / `object_frames` / `wrist_frames` / `records` / `record_fields` / `publication` / `preserved_overview` / `back_projection` -- restrained_flow diagram variants.
- `states` -- state-machine visual.
- `causal_table` -- causal-vs-offline comparison table.
- `rig` -- rig visual.
- `object_chart` / `human_chart` -- standalone chart pages.
- `limits` -- limitations list page.
- `table` -- generic table page.
- `depth_rules` -- depth-rule visual.
- `anchor_factorization` -- anchor-factorization visual.
- `recording_plan` -- recording-plan page (excluded from the main talk).
- `contribution_table` -- contributions table page.
- `closing` -- the Questions page.
- `full_image` -- hidden-page kind (round 4): a PNG scaled to fit and centred across the full slide region (x 0.50-12.83 in, y 1.20-6.75 in), no left bullets, optional one-line caption (D-129).
- `full_video` -- round-4 hidden-page kind: a film and poster filling the same full-region height above the caption, no left bullets except a 22 pt claim panel (D-129).
- `full_table` -- round-4 hidden-page kind: a restrained table spanning the full region width, same header band as other tables, no left bullets (D-129).
- `panel_chart` -- round-5 kind used by hidden 50-51 (D-203; present in build_deck.py). The round-5 `thesis_map` kind is no longer in build_deck.py (page deleted, D-205).

`index` (the Q&A index page) is a round-3 kind, retired in round 4 (D-128);
no page uses it.

## Decision log

`presentation/defense_2026/DECISIONS.md`:
- D-109 to D-126: round 3 (27:00 restructure, media contract rebind D-119 to
  D-121, information_flow and outline typography exceptions D-122/D-126,
  page-11 T-pose figure D-123, two pages moved to Q&A D-124, code-review
  fixes D-125).
- D-127 to D-171: round 4 (2026-09-28): deletion of the 41 round-3 hidden
  pages and the self-containment rule (D-127, D-128); three full-width visual
  kinds (D-129, UNCERTAIN); retired checks (D-130); media contract schema 7
  (D-131) and byte-identical committee copies for the filter films (D-132);
  stand-ins closed by D-169; the three experiments (D-134 to D-148
  marker_bench, D-149 to D-159 transport_bench, D-160 to D-168
  filter_metrics); stale previews and render_deck.py fix (D-170); wording
  pass (D-171). The 41 round-3 hidden pages are recoverable at commit 41d94a7.
- D-172 to D-204: round 5 (dividers, thesis map, Chapter 7 results pages,
  typeset equations, References, panel charts).
- D-205 to D-217: round 6 and its follow-up (the current deck).
- D-218 to D-243: the discarded Codex decks (argument-led M2/M3/M4, targeted
  revision, 66+39 restoration); all superseded by D-244.
- D-244 (2026-09-29): restore the deck and build sources to c5440c4; keep the
  134-question committee bank (slide pointers still use the discarded
  numbering, an open item).

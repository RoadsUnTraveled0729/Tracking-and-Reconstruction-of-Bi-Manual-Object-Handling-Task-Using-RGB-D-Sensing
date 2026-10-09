# Thesis defence presentation

## Final deck (2026-10-06, commits 3dbd345 and 2d9db7e)

The deliverable is the author's reviewed deck, adopted byte for byte and then
given two author-requested edits (the slide 12 film, D-387; results slides
33-35 reduced to the spoken script, D-389), with its
English speaker script and English outline and QA guide:

- [Thesis_Defence_2026.pptx](Thesis_Defence_2026.pptx): the presentation.
- [Thesis_Defence_2026_Speaker_Script.docx](Thesis_Defence_2026_Speaker_Script.docx):
  the spoken script, rewritten general-then-specific on 2026-10-06 (D-386).
- [Thesis_Defence_2026_Outline_and_QA_Index.docx](Thesis_Defence_2026_Outline_and_QA_Index.docx):
  a two-page Letter landscape guide, a three-block tree and then the question
  ranges that name the hidden page for each topic.

The deck has 77 slides: slides 1-46 are the talk and slides 47-77 are hidden
backup (question and derivation pages), reached by typing the slide number.
The three blocks are motivation and goal, the offline reconstruction system,
and results and next steps. The script covers slides 1-46 with 2,657 spoken
words (D-392), planned at 1620 s = 27:00 (110 words per minute), using the full
27-minute limit with no reserve (D-388). The 27:00 is arithmetic from word counts, not a measured
delivery time.

### Deliverables (read from the files on 2026-10-06)

| File | Bytes | Pages | sha256 |
|---|---:|---|---|
| Thesis_Defence_2026.pptx | 98,268,928 | 77 slides (46 shown, 31 hidden) | b3b6a8f0d650888db8f13f8536c787f90cb5b16a1d1860683d46af11fe129cb7 |
| Thesis_Defence_2026.pdf | 69,706,833 | 77 | 110326a24de3613c6116b58ddc02076d9d9b9ec44be3de7ae650ad0472727c44 |
| Thesis_Defence_2026_Speaker_Script.docx | 54,318 | 23 (PDF) | f0fdb49146374ce0f86f58ad44ee741c7d0900e46be0f49aa76e2f05068f28ab |
| Thesis_Defence_2026_Speaker_Script.pdf | 199,693 | 23 | 11ccc9f27bf137d2eb9d61f8650cf7e82dd991353309fb6de1805fc369f67495 |
| Thesis_Defence_2026_Outline_and_QA_Index.docx | 209,782 | 2 (PDF) | a266ffe5ab3e014eac12ec17792cec96e08f4c7cbfae0e91ce9522ffdd9add4b |
| Thesis_Defence_2026_Outline_and_QA_Index.pdf | 236,152 | 2 | c4c6924a3765f8fc6f85c34d9081d92b06b6142e69a00af09e66fb634a3d9a7c |

The outline docx is the author's file, unchanged. The pptx is the author's file
(D-381; author sha256 da94af7c...) with two edits and four later ones (below). First, the slide 12 picture is
replaced by the chain-growth film media/p12_chain_growth.mp4 (8.0 s, made by
anim/chain_growth.py and embedded by anim/patch_slide12_video.py; every other
zip entry unchanged, review/slide12_patch.json; D-387). Second, slides 33-35 are
reduced to what the script says: slide 33 shows model elbow, model wrist and
rig values without the grasp distance, slide 34 keeps its six rows with the
spoken intermediate window (445-489) in amber bold and the rest grey, slide 35
shows the right wrist only (anim/patch_results_slides.py; only slide33-35.xml
and the slide 35 rels changed, image50.png removed;
review/results_slides_patch.json; D-389).
Four later edits followed on 2026-10-06 (D-390 to D-393, all UNCERTAIN until the
author views them): the slide 33 and 34 pictures (D-390); slide 39 as system
assumptions (D-391); slide 34 rows relabelled by wrist travel (0.6, 2.8 and 5.1 cm,
thesis Table 7.5), "cases" wording and a three-case figure in place of the
error-curve figure (anim/patch_slide34_wording.py, review/slide34_wording_patch.json;
D-392; its speaker-script edit and shorter tile wording were applied in
D-392's Final state, within the 1620 s cap); and slide 33
replaced its FK still by the three-panel film media/p33_three_panel.mp4 (recorded RGB,
Python FK skeleton, Unity avatar, 1498 frames, frame map identity;
anim/three_panel_fk.py, anim/patch_slide33_film.py,
review/slide33_film_patch.json; D-393; playback in PowerPoint not verified).
The speaker script docx is a build output of speaker_script.json
(D-386). The PDFs are LibreOffice stills (soffice 24.2.7.2) with every video as
one still image; they are written by make_package.py --render and described in
[review/RENDER_RECORD.json](review/RENDER_RECORD.json), which carries each source
and PDF hash. [package/MANIFEST.json](package/MANIFEST.json) pins the git commit
and the hash of each packaged file; the package folder holds the six files above
plus README.txt, 168,676,728 bytes in all (package/MANIFEST.json, 2026-10-06).

The pptx has 149 media files in ppt/media (123 PNG, 26 MP4; zip listing
2026-10-06, after the D-392 and D-393 edits) and no external relationships (make_package.py deck_facts();
package/MANIFEST.json embedded_mp4_videos 26). All text on slides 1-46 is set in DejaVu Sans at
the sizes 60, 28, 22, 16, 11 and 10.5 pt (explicit run sizes read with
python-pptx on 2026-10-06; inherited sizes were not read).

### The author's delivery notes (2026-10-05, commit 87e87ae)

Page 20 has three main points with six nested detector items. Page 23 puts
RGB above synchronized flat-circle geometry in one automatically started
film. Page 38 uses a new native Unity recording with corrected table display
bounds and wall span. Its left RGB and right Unity panels use corresponding
causal states. QA47 covers coordinate transforms; QA48 keeps the two approved
LH/RH body workflows and derived matrix-form operation counts. Formulas and
other original movies are preserved. IEEE citations use the deck's own
numbering; all 23 entries are on the three visible reference pages 42-44.

[Delivery details and hashes](review/personal_review_20261005/DELIVERY.json)
include 1,585 preservation checks, 5 Unity log checks and 12 rig checks, all
passing. All pages were visually reviewed as renders, and main pages 1-40
were checked in PowerPoint before the final p23/text refinements. The repaired
file opened directly without a Repair prompt, and page 23 played with
synchronized geometry. The final bibliography refinement was reopened without
Repair and page 44 was checked in native slideshow; see
[native review coverage](review/personal_review_20261005/VISUAL_REVIEW.json).
The official package helper's unchanged 24 empty-media-action compatibility
findings remain recorded; separate layout/font/chart/table checks passed. The
final three reference pages (42-44) were checked in native PowerPoint and
approved by the author; see
[final reference audit](review/personal_review_20261005/reference_consolidation_audit.json).

These author notes and native PowerPoint checks describe the adoption
baseline, before the later D-387..D-393 edits; they do not certify playback
or layout of those edits in the current pptx. The script they mention
(2,540 words) was replaced on 2026-10-06 by the rewrite below (2,532 words,
then 2,659 in D-388 and 2,657 in D-392). The native checks were made on the
author's machine and are not repeated here. review/restructured_fixed_20261005/DELIVERY.json
pins an earlier pptx (sha256 1d646c2b..., D-385) and is superseded by the
personal_review_20261005 record.

## Speaker script: how it is built and checked

The source of truth is [speaker_script.json](speaker_script.json) (the text of
slides 1-46, the header lines, the block and section map and the timing
constants). [build_speaker_script.py](build_speaker_script.py) has three modes
(enter the directory shown below and use the thesis Python):

```bash
cd /home/luo/Desktop/bimanual-tracking/presentation/defense_2026
/home/luo/anaconda3/bin/python -B build_speaker_script.py --extract   # docx -> JSON (seeding only; overwrites the JSON)
/home/luo/anaconda3/bin/python -B build_speaker_script.py             # JSON -> Thesis_Defence_2026_Speaker_Script.docx
/home/luo/anaconda3/bin/python -B build_speaker_script.py --check     # lint: exit 0 on pass
```

The build keeps the author's Word styles (the current docx is the template, its
body is cleared), adds a Heading 3 per section (ten sections in three blocks) and
recomputes the timing lines from the constants: 110 words per minute, 2 s per
slide, a per-slide viewing pause, the remainder to the cap (timing.cap_s of the JSON, 1620 s) assigned to
slide 38 (constants from review/personal_review_20261005/build_documents.py
lines 41-44). The check prints words and seconds per slide, requires the total
to be at most the JSON cap, and reports hits for semicolons, filler words, internal
recording names, sentences opening on a number word, repeated sentences, and a
header that states a different word count or checkpoint than the computed one.
Result on 2026-10-06 after D-392: 2,657 words, 1620 s, cap 1620 PASS, 0 hits (D-391 had 2,660 words; D-388 had 2,659 words; D-386 had 2,532 words, 1560 s).

Section map (script headings, slides): Motivation and goal 1-4; System
architecture 5; Data preprocessing 6-10; Kinematic model 11-15; Object tracking
16-18; Partial occlusion 19-24; From modules to one system 25-30; Results
31-38; Limitations, future directions and summary 39-41; References and close
42-46. Each block opens with a question and each section and slide paragraph
states its point first (D-386). Slides 2, 5, 20, 25 and 26 were trimmed by one
sentence or clause each to meet the cap.

After editing speaker_script.json, rebuild the docx, run --check, then render and
package as below.

## PDFs and package

```bash
cd /home/luo/Desktop/bimanual-tracking/presentation/defense_2026
/home/luo/anaconda3/bin/python -B make_package.py --render        # three PDFs and review/RENDER_RECORD.json
/home/luo/anaconda3/bin/python -B make_package.py                 # package/Thesis_Defence_2026 and package/MANIFEST.json
/home/luo/anaconda3/bin/python -B make_package.py --require-clean # same, after the inputs are committed
/home/luo/anaconda3/bin/python -B make_package.py --self-test     # six clean-tree cases
```

--render needs soffice (LibreOffice) and writes the PDFs with the Impress option
ExportHiddenSlides, so the deck PDF has all 77 slides. It is idempotent: a PDF whose
source sha256 and PDF sha256 match review/RENDER_RECORD.json is skipped ("unchanged,
skipped") and only the others are re-rendered (D-388). make_package.py refuses a
PDF that RENDER_RECORD.json does not describe for the current source hash, refuses
a pptx with an external relationship, and with --require-clean refuses a dirty or
untracked input (the six deliverables, PACKAGE_README.txt, make_package.py and the
render record). Commit the rebuilt files first, then run --require-clean, so that
package/MANIFEST.json pins the commit that holds them. The folder
package/Thesis_Defence_2026 is git-ignored (it duplicates tracked files) and is
shared by link, because the pptx and the deck PDF exceed an e-mail attachment
limit (D-108, D-383). The generated package README.txt is filled from
[PACKAGE_README.txt](PACKAGE_README.txt).

share/ (2026-10-07, D-396) holds a shown-only copy for sending to another
professor: share/Thesis_Defence_2026_shown_only.pptx is a copy of
Thesis_Defence_2026.pptx with the 31 hidden backup slides (47-77) removed by
python-pptx (sldId and presentation relationship dropped, 46 slides left), and
share/Thesis_Defence_2026_shown_only.pdf is its 46-page LibreOffice render with
the same soffice command and Impress export option as make_package.py --render
(videos as poster frames). The original pptx is unchanged (sha256 b3b6a8f0...).
share/Thesis_Defence_2026_shown_only_email.pdf (2026-10-07) is a reduced copy of that PDF for email (Ghostscript 10.02.1 pdfwrite, -dCompatibilityLevel=1.5 -dPDFSETTINGS=/prepress, 300 dpi image limit, 4,724,538 B against 45,896,443 B, 46 pages, same two embedded fonts).
On pages 7, 20, 24, 30 and 41 the copy carries a plain picture of the film frame that the author's poster shows, cropped to the poster's own crop and placed in the same box, instead of the film, because LibreOffice ignored or misapplied that crop and drew a distorted poster (D-396 follow-up (b)); `/home/luo/anaconda3/bin/python presentation/defense_2026/share/fix_video_posters.py` regenerates the copy and both PDFs (trim, fix, render).
share/ is not a make_package.py input and is not in the package manifest.

## Verification basis and limits

Adoption verification (D-383) established equality with the author's three
pinned source hashes, PDF page counts of 77, 24 and 2, a rendered-page spot
check and refusal of external relationships. That was the adoption baseline;
the script's 24-page count and author-source equality do not describe the
later patched deck and rewritten script.

Current artifact hashes agree with [RENDER_RECORD.json](review/RENDER_RECORD.json)
and [MANIFEST.json](package/MANIFEST.json), checked locally on 2026-10-08.
Their recorded PDF page counts are 77, 23 and 2. The manifest pins cdfbaa4
and records working_tree_differs_from_commit as false for its packaged input
state; this is an artifact pin, not a certification of subsequent repository
changes. Its total_bytes is 168,676,728.

Not verified: PowerPoint playback of the later embedded films and edits on
the defence machine; a timed aloud rehearsal against the 27:00 schedule; a
cold read of the rewritten script against the slides; whether the LibreOffice
PDF matches PowerPoint layout. No rendering or playback was rerun for this
currency update. The current corrections and ranked historical author checks
are in [SESSION_REVIEW.md](SESSION_REVIEW.md).

## Page map (slides 1-77, read from Thesis_Defence_2026.pptx with python-pptx on 2026-10-06)

Slides 1-46 are shown; slides 47-77 are hidden backup. The title is the first
text on the slide (slides 1 and 2 are the cover and the outline).

| # | Title | State |
|---:|---|---|
| 1 | Tracking and Reconstruction of Bi-Manual Object Handling Task Using RGB-D Sensing (cover) | shown |
| 2 | Outline | shown |
| 3 | Capturing bimanual handling today | shown |
| 4 | Goal: one RGB-D camera, one metric scene | shown |
| 5 | Offline system architecture | shown |
| 6 | Data preprocessing | shown |
| 7 | Raw observations: detector and sensor | shown |
| 8 | Spikes: Hampel rejection | shown |
| 9 | Short gaps: linear interpolation | shown |
| 10 | Jitter: Butterworth smoothing | shown |
| 11 | Kinematic model | shown |
| 12 | Linked landmarks and constraints (chain-growth film from L24, 8.0 s, D-387) | shown |
| 13 | Level 1: the root frame at L24 | shown |
| 14 | Level 2: the shoulder, swing and twist | shown |
| 15 | Level 3: the elbow | shown |
| 16 | Object tracking | shown |
| 17 | Static markers: desk and wall | shown |
| 18 | Moving marker: the cube | shown |
| 19 | Partial occlusion | shown |
| 20 | Landmark validity overlay | shown |
| 21 | Case A: the wrist from the elbow and direction memory | shown |
| 22 | Case B: the wrist from the object | shown |
| 23 | Case C: the elbow from two lengths | shown |
| 24 | No support: hold the last valid angles | shown |
| 25 | From modules to one system | shown |
| 26 | Shared memory: frame access and dropped frames | shown |
| 27 | Shared records and time alignment | shown |
| 28 | Mapping the body into Unity | shown |
| 29 | Mapping the ArUco frames into Unity | shown |
| 30 | Integrated reconstruction | shown |
| 31 | Results | shown |
| 32 | Object: reconstructed lengths against the tape | shown |
| 33 | Body, unoccluded: model and avatar (three-panel film: recorded RGB, Python FK, Unity avatar, D-393) | shown |
| 34 | Body, occluded: controlled removal (rows by wrist travel, "cases", three-case figure, D-392; script edit blocked) | shown |
| 35 | Body, occluded: natural failures | shown |
| 36 | Offline pass and causal structure | shown |
| 37 | Causal replay within the frame budget | shown |
| 38 | Recorded RGB and causal Unity reconstruction | shown |
| 39 | Limitations (system assumptions and their consequences, D-391) | shown |
| 40 | Future directions | shown |
| 41 | Summary | shown |
| 42 | References (1 of 3) | shown |
| 43 | References (2 of 3) | shown |
| 44 | References (3 of 3) | shown |
| 45 | Thank you | shown |
| 46 | Questions | shown |
| 47 | Backup: coordinate transformations between frames | hidden backup |
| 48 | Left-handed and right-handed body-model workflows | hidden backup |
| 49 | ArUco vs AprilTag in the published literature | hidden backup |
| 50 | AprilTag 3 faster, corner errors converge at 96 px | hidden backup |
| 51 | Transport candidates | hidden backup |
| 52 | Moving one frame package from Python to Unity | hidden backup |
| 53 | Savitzky-Golay filtering | hidden backup |
| 54 | Median filtering | hidden backup |
| 55 | One Euro filtering | hidden backup |
| 56 | Butterworth for offline smoothing | hidden backup |
| 57 | One Euro for real-time smoothing | hidden backup |
| 58 | Derivation: Camera' and the chain (Eqs. 3.1-3.3) (1 of 2) | hidden backup |
| 59 | Derivation: Camera' and the chain (Eqs. 3.4-3.6) (2 of 2) | hidden backup |
| 60 | Derivation: Torso and root frame (Eqs. 3.7-3.9) (1 of 2) | hidden backup |
| 61 | Derivation: Torso and root frame (Eqs. 3.10-3.12) (2 of 2) | hidden backup |
| 62 | Derivation: Shoulder and elbow frames (Eqs. 3.13-3.14) | hidden backup |
| 63 | Derivation: Root Euler angles (Eqs. 3.15-3.17) | hidden backup |
| 64 | Derivation: Shoulder swing and twist (Eqs. 3.18-3.23) | hidden backup |
| 65 | Derivation: Elbow coordinates (Eq. 3.24) | hidden backup |
| 66 | Derivation: Object pose in World (Eqs. 4.1-4.2) | hidden backup |
| 67 | Derivation: Grasp offset (Eqs. 5.1-5.4) | hidden backup |
| 68 | Derivation: Direction memory and wrist target (Eqs. 5.5-5.7) | hidden backup |
| 69 | Derivation: Elbow circle and prior (Eqs. 5.8-5.10) (1 of 2) | hidden backup |
| 70 | Derivation: Elbow circle and prior (Eqs. 5.11-5.12) (2 of 2) | hidden backup |
| 71 | Derivation: Mapping into Scene (Eq. 6.1) (1 of 2) | hidden backup |
| 72 | Derivation: Mapping into Scene (Eqs. 6.2-6.3) (2 of 2) | hidden backup |
| 73 | Derivation: Rig chain and rest axes (Eqs. 6.4-6.5) | hidden backup |
| 74 | Derivation: Gravity and floor (Eq. 6.6) | hidden backup |
| 75 | Derivation: Evaluation measures (Eqs. 7.1-7.2) (1 of 2) | hidden backup |
| 76 | Derivation: Evaluation measures (Eqs. 7.3-7.6) (2 of 2) | hidden backup |
| 77 | Backup: the causal run from its process logs | hidden backup |

## Kept supporting material

These folders stay because the deck's media, figures and the evaluation code
read them; some of their README sections describe earlier builds.

- media/ (masters and generators of the film and chart assets), anim/ (the
  generators that remain), figures/, equations/ (equation crops and
  derivation_leads.py), experiments/ (marker_bench, transport_bench,
  filter_metrics), bank_processing/ (processed recording data and its source
  checks), unity_capture/ (Unity capture scripts and records).
- The unified_four provenance folder under committee_materials is the only part of
  that tree that remains (four JSON files read by
  eval/pipeline_smoothness/compare_film_vs_live.py).
- COMMITTEE_QUESTIONS.md, .docx and .pdf (134 questions) with
  export_committee_questions.py and review/question_index.json; QA_PREP.md,
  RECORDING_GUIDE.md, VIDEO_SHOT_LIST.md, MEDIA_PROVENANCE.md. Their slide
  pointers use earlier numberings; use the outline and QA guide for the final
  numbering.
- review/ holds the audit records of earlier rounds and the author's
  personal_review_20261005/ delivery record (builder scripts, DELIVERY.json,
  VISUAL_REVIEW.json).
- [DECISIONS.md](DECISIONS.md) (the log, adoption and follow-up entries D-381 to D-396) and
  [SESSION_REVIEW.md](SESSION_REVIEW.md) (ranked author checks, history below the
  final section).

## Retired material (history, not current)

On 2026-10-06 the author's files became the delivery and the generated deck
and its pipeline were retired (D-382, D-385). Nothing below exists in the
working tree; each item is recoverable from git:

- At commit 85078c9 (the round-11 records state, 2026-10-01): the generated
  Thesis_Defence_2026.pptx of build 77 and its PDF, the FOCUSED pptx and script,
  DEFENSE_SCRIPT.md, the build_deck.py, render_deck.py, validate_deck.py,
  set_page_budgets.py and report_effective_text.py pipeline with its inputs
  (talk_content.json, backup_content.json, script_document.json,
  budget_override.json) and reports, the round-10 and round-11 review folders and
  the earlier version of this README (rounds 3 to 11, page maps, per-round
  validator counts). Recover with git show 85078c9:presentation/defense_2026/README.md.
- At commit 87e87ae (the state just before the deletion in 3dbd345): everything
  else deleted on 2026-10-06 (818 tracked files), among them the round-8 to
  round-11 committee_materials trees, presentation/v9, presentation/assets,
  presentation/out, slides.md, build.sh, review/qa_revision, 16 anim/ scripts and
  the media checkers (D-385). Recover with git checkout 87e87ae -- <path>. The
  author's upload under its original name Thesis_Defence_2026_RESTRUCTURED_FIXED.pptx
  is also in 87e87ae (D-381).
- Records that still cite a retired path (anim/recorded_context.py, the
  media/provenance JSON files, older DECISIONS.md entries) are provenance and are
  not rewritten (D-385 lists the broken ones).

## Evidence and limits

All headline numbers shown on the slides come from the thesis and the pinned
validators and benchmarks cited on each slide; this README restates none of
them. Presentation timing and media pauses are editorial, not performance
measurements. The complete live-camera pipeline and sensor-to-screen latency
remain unvalidated; recordings keep their actual calibration, sizing and display
limitations.

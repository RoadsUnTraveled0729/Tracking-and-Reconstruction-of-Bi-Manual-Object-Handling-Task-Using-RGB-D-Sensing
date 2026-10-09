Note (Verified 2026-10-06, post-defence revision 1, D-394): the page-2 revision
added reference entries [60]-[62] (compiled [19], [28], [29]), shifted later
compiled citation numbers by +1/+2, and kept 168 pages. Figures below were not
re-read after that revision except where stated.

Verified: 2026-09-29 (compiled PDF/DOCX and submission-record cross-check)
Sources: writing/v9/Thesis_V9.pdf; writing/v9/Thesis_V9.docx;
writing/v9/README.md; writing/v9/audit_evidence/submission_checklist_v9/validation.json;
writing/v9/zh/src/*.txt (reading aids only, version limits below).
Answers: the final V9 outline and the difference between physical PDF pages,
printed thesis page labels and source-export line numbers.

Verified 2026-09-29 for the committee-bank facts (last section): 134 "###"
question headings in COMMITTEE_QUESTIONS.md, 16 Basic questions per
review/COMMITTEE_EXPORT_CHECK.json (134 questions, 61-page PDF, status PASS),
and the listed review/qa_revision files exist. The outline tables above were
not re-read in this task.

Historical defence deck context (2026-09-29): 39 main + 14 hidden pages, 1785 s = 29:45,
c5440c4 bytes restored 2026-09-29 (D-244; deck_inventory.md). The
committee bank below was kept from the discarded Codex decks and its slide
pointers refer to the discarded 66-main/39-hidden numbering, not to the
current deck.

Current defence deck (Verified 2026-10-08 against
presentation/defense_2026/README.md and build_speaker_script.py --check):
77 slides, 46 shown and 31 hidden; the script is planned at 1620 s = 27:00.
See [deck_inventory.md](deck_inventory.md) for current files and review limits.
This planned duration is not a measured rehearsal.

## Citation authority and version limits

The final compiled thesis has 168 physical PDF pages. PDF page means the
1-based physical page, not a source line or printed footer. Printed main
pages 1-122 are PDF pages 15-136. Appendix footers restart by letter;
References use R1-R5. The front matter has roman-numbered footers.
The compiled PDF and compiled DOCX are primary. V9 was final and frozen
at the 2026-09-29 outline check. The current V9 post-defence revision round
opened on 2026-10-06 under [D-394](../writing/v9/DECISIONS.md), lifting that
freeze for this round only (Verified 2026-10-08). Current version and build
pointers are [writing/v9/README.md](../writing/v9/README.md) and AGENTS.md;
the dated outline tables below retain their stated verification limits.

The prior version of this note incorrectly described export line indices
as section and appendix pages. In particular, appendix numbers 1, 33,
49, 76, 105, 145, 161 and 181 were line positions, not pages. Do not use
them for citations. English exports under zh/src do not uniformly mirror
the final assembly: compiled Chapter 9 has no 9.1-9.8 section headings;
Chapter 4 has numbering/opening-text differences. Use exports to find a
passage, then check its wording and equations in the final compiled PDF.
No claim is made that every export difference has been inventoried.

## Files and reading tools

Primary outputs are Thesis_V9.pdf and Thesis_V9.docx. Thesis_V9_TOC.docx,
per-chapter DOCX files, FrontMatter_V9.docx and Appendices.docx are also
present, but this outline cites the final assembly. pdftotext -layout
reads PDF text; python-docx reads DOCX prose and tables. PDF page images
are needed to inspect equations and figures that text extraction omits.

## Front matter

| Content | Printed label | PDF page |
|---|---|---|
| Title | none | 1 |
| Approval | ii | 2 |
| Abstract | iii-iv | 3-4 |
| Acknowledgements | v | 5 |
| Table of Contents | vi-viii | 6-8 |
| List of Figures | ix-xi | 9-11 |
| List of Tables | xii-xiii | 12-13 |
| Glossary | xiv | 14 |

## Chapters and sections

All starts below were checked against actual compiled page headings and
printed footers, not inferred from export line numbers. Table-of-contents
entries agree with these starts. Main-page printed labels equal PDF page
minus 14; this offset does not apply to appendices or front matter.

| Heading | Printed page | PDF page |
|---|---:|---:|
| Chapter 1: Introduction | 1 | 15 |
| 1.1 Motivation | 1 | 15 |
| 1.2 Problem Statement and Literature Review | 2 | 16 |
| 1.2.1 Hand and Object Tracking Approaches | 2 | 16 |
| 1.2.2 Bimanual Manipulation in Motion Analysis | 2 | 16 |
| 1.2.3 Graphical Reconstruction in Robotics and VR | 3 | 17 |
| 1.2.4 Gap Analysis and Motivation for This Work | 4 | 18 |
| 1.3 Research Objectives | 5 | 19 |
| 1.4 Organization of the Thesis | 6 | 20 |
| Chapter 2: Experimental Setup and Measurements | 7 | 21 |
| 2.1 The Recording Setup | 7 | 21 |
| 2.2 Coordinate Frames and Scene Calibration | 10 | 24 |
| 2.2.1 The Frames | 10 | 24 |
| 2.2.2 Scene Calibration | 13 | 27 |
| 2.3 Pose Landmarks From MediaPipe | 14 | 28 |
| 2.4 Object Pose From ArUco Markers | 15 | 29 |
| 2.5 Measurement Filtering | 16 | 30 |
| 2.6 Hip Depth Preparation | 19 | 33 |
| Chapter 3: Kinematic Modelling | 21 | 35 |
| 3.1 Coordinate Systems and Transformations | 21 | 35 |
| 3.2 Torso Reference Frame | 25 | 39 |
| 3.2.1 Landmark Selection | 25 | 39 |
| 3.2.2 Derivation of the Torso Frame | 25 | 39 |
| 3.3 The Arm Model | 28 | 42 |
| 3.3.1 Kinematic Schematic and Solved Angles | 28 | 42 |
| 3.3.2 Definition of Shoulder, Elbow, and Wrist | 29 | 43 |
| 3.3.3 Establishing Local Arm Frames | 30 | 44 |
| 3.4 Joint Angle Computation | 31 | 45 |
| 3.4.1 Torso Pose | 32 | 46 |
| 3.4.2 Shoulder Orientation | 32 | 46 |
| 3.4.3 Elbow Flexion and Extension | 34 | 48 |
| 3.4.4 The Wrist as a Tracked Point | 35 | 49 |
| 3.5 Worked Example | 35 | 49 |
| Chapter 4: Object Tracking and Scene Reconstruction | 40 | 54 |
| 4.1 World Anchoring and Camera Placement Invariance | 40 | 54 |
| 4.2 Filtering and Cleaning the Object Track | 42 | 56 |
| 4.3 Worked Example | 45 | 59 |
| Chapter 5: Pose Recovery During Tracking Failure | 48 | 62 |
| 5.1 Assumptions and Parameters | 49 | 63 |
| 5.2 Landmark Tracking Failures | 50 | 64 |
| 5.3 Grip Episodes and the Hand-Object Offset | 52 | 66 |
| 5.4 Wrist Recovery From the Object Pose | 57 | 71 |
| 5.5 Elbow Recovery by Two-Link Inverse Kinematics | 58 | 72 |
| 5.6 Worked Example: Frames 549 and 560 | 61 | 75 |
| Chapter 6: System Integration and Graphical Reconstruction | 66 | 80 |
| 6.1 Communication Architecture | 66 | 80 |
| 6.1.1 The Frame Buffer: Capture Process to the Branches | 67 | 81 |
| 6.1.2 The Records: Branches to the Merger and Unity | 68 | 82 |
| 6.2 Coordinate System Conversion | 71 | 85 |
| 6.3 Avatar Reconstruction in Unity | 74 | 88 |
| 6.4 Scene Reconstruction in Unity | 78 | 92 |
| 6.5 Worked Example | 80 | 94 |
| Chapter 7: Experimental Evaluation | 85 | 99 |
| 7.1 Evaluation Method | 85 | 99 |
| 7.2 Object Reconstruction Accuracy | 86 | 100 |
| 7.2.1 Single-Hand Rail Task | 87 | 101 |
| 7.2.2 Handover Task | 90 | 104 |
| 7.3 Human Reconstruction Accuracy under Valid Landmark Measurements | 92 | 106 |
| 7.3.1 Single-Hand Rail Task | 94 | 108 |
| 7.3.2 Handover Task | 95 | 109 |
| 7.3.3 Human-Object Spatial Check | 97 | 111 |
| 7.4 Reconstruction During Landmark Failure | 100 | 114 |
| 7.4.1 Synthetic Landmark Removal | 100 | 114 |
| 7.4.2 Natural Occlusion | 102 | 116 |
| Chapter 8: Real-Time Feasibility | 107 | 121 |
| 8.1 From Offline to Causal Processing | 107 | 121 |
| 8.2 Causal and Real-Time Architecture | 108 | 122 |
| 8.3 Offline-Causal Comparison | 111 | 125 |
| 8.4 Runtime, Buffering, and Delay | 114 | 128 |
| 8.5 Feasibility and Remaining Validation Gap | 114 | 128 |
| Chapter 9: Discussion | 116 | 130 |
| Chapter 10: Conclusions and Future Work | 121 | 135 |
| 10.1 Conclusions | 121 | 135 |
| 10.2 Future Work | 122 | 136 |

Chapter 9 is a single Discussion chapter, with no numbered subsections.

## Appendices and References

| Appendix | Title | Printed pages | PDF pages | Section starts: printed label (PDF page) |
|---|---|---|---|---|
| A | RGB-D Data Acquisition | A1-A3 | 137-139 | A.1 A1 (137); A.2 A1 (137); A.3 A2 (138) |
| B | Hardware and Software Platform | B1 | 140 | No numbered subsections |
| C | Pose Landmark Detection | C1-C4 | 141-144 | C.1 C1 (141); C.2 C1 (141); C.3 C4 (144) |
| D | Depth Sensing and Deprojection | D1-D4 | 145-148 | D.1 D1 (145); D.2 D2 (146); D.3 D3 (147); D.4 D4 (148) |
| E | Fiducial Marker Detection and Pose Recovery | E1-E7 | 149-155 | E.1 E1 (149); E.2 E3 (151); E.3 E5 (153); E.4 E5 (153) |
| F | Characteristics of the Candidate Filters | F1-F3 | 156-158 | No numbered subsections |
| G | Hip Depth Preparation | G1-G3 | 159-161 | G.1 G1 (159); G.2 G1 (159); G.3 G2 (160); G.4 G3 (161) |
| H | Kinematic Solver Verification | H1-H2 | 162-163 | H.1 H1 (162); H.2 H1 (162); H.3 H2 (163) |
| References | Compiled bibliography, entries [1]-[58] | R1-R5 | 164-168 | Assembly numbering is authoritative |

Verification scope: all front matter, appendices A-H and compiled
References were read end-to-end in the final PDF; DOCX prose/tables were
cross-checked. All appendix figures, tables and numbered equations were
visually inspected in PDF page renders. Main-chapter heading starts were
checked; this outline check is not a claim to have read every main-chapter
paragraph or original cited paper. Scoped evidence/answer coverage is in
presentation/defense_2026/review/qa_revision/coverage_basics_appendices.md.

## Whole-thesis committee-answer coverage

The three source-reader lanes now report end-to-end compiled-PDF reading
covering all 168 physical pages: front/abstract (1-14), methods Chapters
1-5 (15-79), evaluation/integration Chapters 6-10 (80-136), appendices
A-H (137-163) and References (164-168). DOCX coherence and named exhibits
are documented in the lane coverage records; this statement combines
their recorded scopes rather than attributing all reading to one agent.

The integrated rehearsal bank is presentation/defense_2026/COMMITTEE_QUESTIONS.md:
134 questions, including 16 separate Basic questions, all 105 original
IDs and 13 specialist additions. Each has two answer levels, sources,
limits and a supporting-slide/thesis-exhibit reference. The supporting-slide
numbers are stale: COMMITTEE_QUESTIONS.md line 20 states they refer to the
restored 66-main/39-hidden deck, which was discarded on 2026-09-29 (D-244),
so they do not match the current 39+14 deck. Rebinding them to the current
page numbers is an open item (D-244, review/RESTORE_2026-09-29.md); the
thesis-exhibit references and the answers themselves are unaffected.
All 134 answers have independent source acceptance after three correctness
fixes and two clarity edits; master/checker final integration is accepted
at build 46 (six independent checker criteria PASS; recorded in the
build log, not re-run).
Sources and hashes, author/reviewer assignments, group membership and
original-ID coverage are in review/qa_revision/question_index.json; the
consolidated record is review/qa_revision/coverage_consolidated.md, both
under presentation/defense_2026/. No thesis rebuild, new experiment, full
video playback or live/clinical validation is implied by answer coverage.

Source-status boundary from Q3.2 review: final PDF 51 (printed 37) identifies
Chapter 3 frame-533 values as before hip replacement, whereas PDF 95
(printed 81) says the hip midpoint was left unchanged. Sections 2.6/G.4
and the two code paths distinguish published causal translation from
prepared solver inputs. The pinned causal frame-533 dump is not the exact
offline post-preparation pose and does not resolve every intermediate in
Chapter 6's prose. Preserve this distinction in later presentation/script
work; do not silently amend the frozen V9 thesis. Sources and exact review
correction are in review/qa_revision/integration_notes.json.

## Numbered lists for the footer audit (round 8)

Verified: 2026-09-30. Correction made the same day: the 7.3 row of the
chapters table above read "under Valid Landmark Tracking"; the compiled
table of contents (PDF page 7) and the body heading (PDF page 106) both
read "under Valid Landmark Measurements".

Sources. Numbers, titles and caption wording are the compiled numbering of
writing/v9/Thesis_V9.pdf: the table of contents (PDF pages 6-8) for list a,
the List of Figures (PDF pages 9-11) for list b, the List of Tables (PDF
pages 12-13) for list c, and the equation-number positions in the body
(pdftotext -layout, PDF pages 21-163) for list d, each equation assigned to
the last numbered heading printed before it. Every item also names the
matching paragraph of writing/v9/zh/src as file:line (the 1-based file line,
equal to the export's own paragraph number); "none" means the export has no
such item. Printed page to PDF page: main pages add 14; appendix pages count
from the appendix starts of the table above (A 137, B 140, C 141, D 145,
E 149, F 156, G 159, H 162).

Parse rule. Each list starts at a line "LIST <letter> <name> | <columns>"
and ends at the line "END". Every line between is one item, fields
separated by " | ", first field the number. Chapter rows in list a carry
the bare chapter number. A "caption first clause" is the compiled caption
up to its first sentence end, colon or semicolon outside parentheses.

Stale-export effects on these lists (checked item by item against the
compiled PDF; no other difference was found in the items listed):

- List a: the export has sections 9.1-9.8 in Chapter 9; the compiled
  thesis has none, so they are omitted. The export titles them 9.1 The
  Integrated Reconstruction and Its Evaluation; 9.2 Object Reconstruction
  and Physical-Route Error Sources; 9.3 Human-Object Spatial
  Reconstruction; 9.4 Landmark Failure and Object-Assisted Recovery;
  9.5 Torso and Root Failure and High-Confidence Landmark Errors;
  9.6 Single-View Observability and Model Limits; 9.7 Real-Time and Causal
  Implications; 9.8 Scope of the Evaluation. A footer citing "Section 9.x"
  cites a heading the committee copy does not have; the compiled text
  itself contains no "Section 9." reference, while the export has eleven.
  The export also titles 5.6 "Worked Example: Frame 549" (compiled:
  "Frames 549 and 560").
- List b: compiled Figure 5.6 (PDF page 76) has no caption in the export.
  Figure 2.4 cites Intel as [42] in the compiled caption and [59] in the
  export.
- List c: Table 9.1 ends "and the evidence for each on the recordings" in
  the compiled caption and "and where each one shows on the recordings" in
  the export.
- List d: the export numbers the Chapter 4 cleaning rule (4.3) and gives
  the inverse anchor its own number (4.2); in the compiled thesis the
  inverse anchor is unnumbered inline text and the cleaning rule is
  Eq. 4.2. There is no compiled Eq. 4.3. All other equation numbers agree.

Where the thesis states limitations and contributions. Limitations:
Chapter 9 Discussion (PDF pages 130-134, printed 116-120), which has no
numbered sections; its Table 9.1 (PDF page 134) lists "The six principal
limitations of the system". Contributions: Section 10.1 Conclusions (PDF
page 135, printed 121): "The contribution is a working integrated system
together with a full account, in Chapter 9, of the motion it can and cannot
recover from one camera." Section 10.2 Future Work is PDF page 136.

Counts: list a 74 headings (10 chapters, 40 sections a.b, 24 sections
a.b.c); list b 51 figures (43 in Chapters 2-9, 8 in appendices); list c
24 tables (16 in Chapters 1-9, 8 in appendices); list d 55 equations
(51 in Chapters 2-7, 4 in appendices).

```text
LIST a headings | number | title | export source file:line | printed page | PDF page
1 | Introduction | Chapter_1_Introduction.txt:1 | 1 | 15
1.1 | Motivation | Chapter_1_Introduction.txt:3 | 1 | 15
1.2 | Problem Statement and Literature Review | Chapter_1_Introduction.txt:9 | 2 | 16
1.2.1 | Hand and Object Tracking Approaches | Chapter_1_Introduction.txt:11 | 2 | 16
1.2.2 | Bimanual Manipulation in Motion Analysis | Chapter_1_Introduction.txt:15 | 2 | 16
1.2.3 | Graphical Reconstruction in Robotics and VR | Chapter_1_Introduction.txt:17 | 3 | 17
1.2.4 | Gap Analysis and Motivation for This Work | Chapter_1_Introduction.txt:31 | 4 | 18
1.3 | Research Objectives | Chapter_1_Introduction.txt:33 | 5 | 19
1.4 | Organization of the Thesis | Chapter_1_Introduction.txt:40 | 6 | 20
2 | Experimental Setup and Measurements | Chapter_2_Experimental_Setup.txt:1 | 7 | 21
2.1 | The Recording Setup | Chapter_2_Experimental_Setup.txt:3 | 7 | 21
2.2 | Coordinate Frames and Scene Calibration | Chapter_2_Experimental_Setup.txt:21 | 10 | 24
2.2.1 | The Frames | Chapter_2_Experimental_Setup.txt:23 | 10 | 24
2.2.2 | Scene Calibration | Chapter_2_Experimental_Setup.txt:34 | 13 | 27
2.3 | Pose Landmarks From MediaPipe | Chapter_2_Experimental_Setup.txt:44 | 14 | 28
2.4 | Object Pose From ArUco Markers | Chapter_2_Experimental_Setup.txt:49 | 15 | 29
2.5 | Measurement Filtering | Chapter_2_Experimental_Setup.txt:52 | 16 | 30
2.6 | Hip Depth Preparation | Chapter_2_Experimental_Setup.txt:68 | 19 | 33
3 | Kinematic Modelling | Chapter_3_Kinematic_Modeling.txt:1 | 21 | 35
3.1 | Coordinate Systems and Transformations | Chapter_3_Kinematic_Modeling.txt:6 | 21 | 35
3.2 | Torso Reference Frame | Chapter_3_Kinematic_Modeling.txt:29 | 25 | 39
3.2.1 | Landmark Selection | Chapter_3_Kinematic_Modeling.txt:30 | 25 | 39
3.2.2 | Derivation of the Torso Frame | Chapter_3_Kinematic_Modeling.txt:34 | 25 | 39
3.3 | The Arm Model | Chapter_3_Kinematic_Modeling.txt:56 | 28 | 42
3.3.1 | Kinematic Schematic and Solved Angles | Chapter_3_Kinematic_Modeling.txt:57 | 28 | 42
3.3.2 | Definition of Shoulder, Elbow, and Wrist | Chapter_3_Kinematic_Modeling.txt:64 | 29 | 43
3.3.3 | Establishing Local Arm Frames | Chapter_3_Kinematic_Modeling.txt:66 | 30 | 44
3.4 | Joint Angle Computation | Chapter_3_Kinematic_Modeling.txt:75 | 31 | 45
3.4.1 | Torso Pose | Chapter_3_Kinematic_Modeling.txt:84 | 32 | 46
3.4.2 | Shoulder Orientation | Chapter_3_Kinematic_Modeling.txt:86 | 32 | 46
3.4.3 | Elbow Flexion and Extension | Chapter_3_Kinematic_Modeling.txt:105 | 34 | 48
3.4.4 | The Wrist as a Tracked Point | Chapter_3_Kinematic_Modeling.txt:111 | 35 | 49
3.5 | Worked Example | Chapter_3_Kinematic_Modeling.txt:114 | 35 | 49
4 | Object Tracking and Scene Reconstruction | Chapter_4_Object_Tracking.txt:1 | 40 | 54
4.1 | World Anchoring and Camera Placement Invariance | Chapter_4_Object_Tracking.txt:3 | 40 | 54
4.2 | Filtering and Cleaning the Object Track | Chapter_4_Object_Tracking.txt:14 | 42 | 56
4.3 | Worked Example | Chapter_4_Object_Tracking.txt:29 | 45 | 59
5 | Pose Recovery During Tracking Failure | Chapter_5_Pose_Recovery.txt:1 | 48 | 62
5.1 | Assumptions and Parameters | Chapter_5_Pose_Recovery.txt:9 | 49 | 63
5.2 | Landmark Tracking Failures | Chapter_5_Pose_Recovery.txt:14 | 50 | 64
5.3 | Grip Episodes and the Hand-Object Offset | Chapter_5_Pose_Recovery.txt:23 | 52 | 66
5.4 | Wrist Recovery From the Object Pose | Chapter_5_Pose_Recovery.txt:60 | 57 | 71
5.5 | Elbow Recovery by Two-Link Inverse Kinematics | Chapter_5_Pose_Recovery.txt:67 | 58 | 72
5.6 | Worked Example: Frames 549 and 560 | Chapter_5_Pose_Recovery.txt:89 (export title differs: "Worked Example: Frame 549") | 61 | 75
6 | System Integration and Graphical Reconstruction | Chapter_6_System_Integration.txt:1 | 66 | 80
6.1 | Communication Architecture | Chapter_6_System_Integration.txt:3 | 66 | 80
6.1.1 | The Frame Buffer: Capture Process to the Branches | Chapter_6_System_Integration.txt:10 | 67 | 81
6.1.2 | The Records: Branches to the Merger and Unity | Chapter_6_System_Integration.txt:17 | 68 | 82
6.2 | Coordinate System Conversion | Chapter_6_System_Integration.txt:33 | 71 | 85
6.3 | Avatar Reconstruction in Unity | Chapter_6_System_Integration.txt:47 | 74 | 88
6.4 | Scene Reconstruction in Unity | Chapter_6_System_Integration.txt:70 | 78 | 92
6.5 | Worked Example | Chapter_6_System_Integration.txt:83 | 80 | 94
7 | Experimental Evaluation | Chapter_7_Evaluation.txt:1 | 85 | 99
7.1 | Evaluation Method | Chapter_7_Evaluation.txt:2 | 85 | 99
7.2 | Object Reconstruction Accuracy | Chapter_7_Evaluation.txt:7 | 86 | 100
7.2.1 | Single-Hand Rail Task | Chapter_7_Evaluation.txt:20 | 87 | 101
7.2.2 | Handover Task | Chapter_7_Evaluation.txt:36 | 90 | 104
7.3 | Human Reconstruction Accuracy under Valid Landmark Measurements | Chapter_7_Evaluation.txt:51 | 92 | 106
7.3.1 | Single-Hand Rail Task | Chapter_7_Evaluation.txt:58 | 94 | 108
7.3.2 | Handover Task | Chapter_7_Evaluation.txt:68 | 95 | 109
7.3.3 | Human-Object Spatial Check | Chapter_7_Evaluation.txt:81 | 97 | 111
7.4 | Reconstruction During Landmark Failure | Chapter_7_Evaluation.txt:92 | 100 | 114
7.4.1 | Synthetic Landmark Removal | Chapter_7_Evaluation.txt:93 | 100 | 114
7.4.2 | Natural Occlusion | Chapter_7_Evaluation.txt:127 | 102 | 116
8 | Real-Time Feasibility | Chapter_8_Real_Time_Feasibility.txt:1 | 107 | 121
8.1 | From Offline to Causal Processing | Chapter_8_Real_Time_Feasibility.txt:3 | 107 | 121
8.2 | Causal and Real-Time Architecture | Chapter_8_Real_Time_Feasibility.txt:7 | 108 | 122
8.3 | Offline-Causal Comparison | Chapter_8_Real_Time_Feasibility.txt:30 | 111 | 125
8.4 | Runtime, Buffering, and Delay | Chapter_8_Real_Time_Feasibility.txt:43 | 114 | 128
8.5 | Feasibility and Remaining Validation Gap | Chapter_8_Real_Time_Feasibility.txt:46 | 114 | 128
9 | Discussion | Chapter_9_Discussion.txt:1 | 116 | 130
10 | Conclusions and Future Work | Chapter_10_Conclusions_Future_Work.txt:1 | 121 | 135
10.1 | Conclusions | Chapter_10_Conclusions_Future_Work.txt:3 | 121 | 135
10.2 | Future Work | Chapter_10_Conclusions_Future_Work.txt:11 | 122 | 136
END
LIST b figures | number | caption first clause (compiled) | export source file:line | printed page | PDF page
2.1 | The recording setup | Chapter_2_Experimental_Setup.txt:7 | 7 | 21
2.2 | The experimental setup seen from the RGB-D camera, with the subject, the rail, the carried cube, and the three ArUco markers labelled | Chapter_2_Experimental_Setup.txt:16 | 9 | 23
2.3 | Overall data flow | Chapter_2_Experimental_Setup.txt:20 | 10 | 24
2.4 | (a) The sensor frame C on a D435 photograph (Intel [42]; axes added) | Chapter_2_Experimental_Setup.txt:26 (export first clause differs: "(a) The sensor frame C on a D435 photograph (Intel [59]; axes added)") | 11 | 25
2.5 | The scene frames | Chapter_2_Experimental_Setup.txt:32 | 12 | 26
2.6 | MediaPipe Pose output on a mid-task frame | Chapter_2_Experimental_Setup.txt:48 | 15 | 29
2.7 | Despiking on the right wrist of the recording | Chapter_2_Experimental_Setup.txt:60 | 17 | 31
2.8 | Gap bridging on the right wrist of the recording | Chapter_2_Experimental_Setup.txt:63 | 18 | 32
2.9 | Smoothing on the right-wrist depth of the recording | Chapter_2_Experimental_Setup.txt:66 | 19 | 33
3.1 | The chapter's information flow | Chapter_3_Kinematic_Modeling.txt:5 | 21 | 35
3.2 | The raw camera frame {Camera} and y-up camera frame {Camera'} drawn from one optical centre | Chapter_3_Kinematic_Modeling.txt:13 | 22 | 36
3.3 | The worked-example frame, front view | Chapter_3_Kinematic_Modeling.txt:23 | 24 | 38
3.4 | Torso-frame construction | Chapter_3_Kinematic_Modeling.txt:37 | 26 | 40
3.5 | The reference configuration | Chapter_3_Kinematic_Modeling.txt:55 | 28 | 42
3.6 | The kinematic schematic of the right arm, a chain of revolute-joint cylinders in the Programmable Universal Machine for Assembly (PUMA) style | Chapter_3_Kinematic_Modeling.txt:62 | 29 | 43
3.7 | The swing-twist decomposition | Chapter_3_Kinematic_Modeling.txt:93 | 33 | 47
4.1 | The object marker | Chapter_4_Object_Tracking.txt:7 | 41 | 55
4.2 | The object marker origin in the world frame, one panel per axis | Chapter_4_Object_Tracking.txt:20 | 43 | 57
5.1 | Information flow of the recovery layer in the Scene formulation of Section 5.3 | Chapter_5_Pose_Recovery.txt:8 | 49 | 63
5.2 | The six failure detectors, one panel each | Chapter_5_Pose_Recovery.txt:18 | 51 | 65
5.3 | The hand-object offset | Chapter_5_Pose_Recovery.txt:39 | 54 | 68
5.4 | The holding state of one hand | Chapter_5_Pose_Recovery.txt:53 | 56 | 70
5.5 | The elbow reconstruction | Chapter_5_Pose_Recovery.txt:83 | 60 | 74
5.6 | (a) Frame 549, the last clean frame of the right arm | none | 62 | 76
6.1 | The integration architecture | Chapter_6_System_Integration.txt:7 | 66 | 80
6.2 | The frame buffer | Chapter_6_System_Integration.txt:15 | 68 | 82
6.3 | The combined record as a memory block | Chapter_6_System_Integration.txt:20 | 69 | 83
6.4 | The four frames of the coordinate conversion before gravity alignment, with the path of each branch to the display | Chapter_6_System_Integration.txt:36 | 72 | 86
6.5 | The reconstruction from the virtual sensor | Chapter_6_System_Integration.txt:82 | 80 | 94
7.1 | Rail recording | Chapter_7_Evaluation.txt:31 | 89 | 103
7.2 | Handover recording | Chapter_7_Evaluation.txt:46 | 91 | 105
7.3 | Single-hand rail task in Unity | Chapter_7_Evaluation.txt:67 | 95 | 109
7.4 | Handover task in Unity | Chapter_7_Evaluation.txt:77 | 96 | 110
7.5 | Rail recording | Chapter_7_Evaluation.txt:85 | 98 | 112
7.6 | Handover recording | Chapter_7_Evaluation.txt:90 | 99 | 113
7.7 | Loop recording | Chapter_7_Evaluation.txt:132 | 103 | 117
7.8 | Loop frame 1462, left wrist | Chapter_7_Evaluation.txt:141 | 104 | 118
7.9 | Loop frame 1890, right wrist, with the symbols of Figure 7.8 | Chapter_7_Evaluation.txt:152 | 105 | 119
8.1 | The offline pass (above) and the causal structure (below), each causal stage under the offline stage it replaces | Chapter_8_Real_Time_Feasibility.txt:11 | 108 | 122
8.2 | The two paths | Chapter_8_Real_Time_Feasibility.txt:34 | 112 | 126
8.3 | The offline chain (blue) and the causal chain (orange) drawn on the colour image at frames 18, 548 and 595, one moment from each window of Figure 8.2 | Chapter_8_Real_Time_Feasibility.txt:39 | 113 | 127
9.1 | Object marker loss on the loop recording | Chapter_9_Discussion.txt:15 | 117 | 131
9.2 | Landmark tracking failure on the loop recording | Chapter_9_Discussion.txt:39 | 118 | 132
A.1 | Structure of the recorded session file | Appendices.txt:15 | A2 | 138
A.2 | (a) The recorded colour frame of the worked-example moment | Appendices.txt:31 | A3 | 139
C.1 | The eight upper-body landmarks on the worked-example frame, drawn at the pixels the extractor sampled, with the segments between them | Appendices.txt:62 | C2 | 142
C.2 | The same eight landmarks as metric position vectors from the sensor origin, with the camera axes drawn at the origin | Appendices.txt:64 | C3 | 143
D.1 | (a) The pinhole geometry the intrinsics describe | Appendices.txt:94 | D3 | 147
E.1 | Marker detection on the worked-example frame | Appendices.txt:110 | E2 | 150
E.2 | (a) A nearly face-on plane admits two pose readings, tilted toward the camera or away from it, that are mirror images about the camera ray | Appendices.txt:117 | E4 | 152
F.1 | (a) The four candidates on one constructed test signal, not recorded data | Appendices.txt:153 | F2 | 157
END
LIST c tables | number | caption first clause (compiled) | export source file:line | printed page | PDF page
1.1 | Summary of the reviewed literature | Chapter_1_Introduction.txt:30 | 4 | 18
2.1 | The objects in the scene | Chapter_2_Experimental_Setup.txt:13 | 8 | 22
3.1 | The eight landmarks of the worked-example frame in the sensor frame and in the y-up camera frame, printed to two decimals | Chapter_3_Kinematic_Modeling.txt:126 | 36 | 50
6.1 | The shared memory blocks | Chapter_6_System_Integration.txt:27 | 70 | 84
6.2 | Frame 533 of the rail recording through the causal structure and the receiver | Chapter_6_System_Integration.txt:114 | 84 | 98
7.1 | Rail recording | Chapter_7_Evaluation.txt:28 | 88 | 102
7.2 | Handover recording | Chapter_7_Evaluation.txt:43 | 91 | 105
7.3 | Single-hand task | Chapter_7_Evaluation.txt:64 | 94 | 108
7.4 | Handover task | Chapter_7_Evaluation.txt:75 | 96 | 110
7.5 | Synthetic removal windows selected using valid unmasked wrist motion before method errors were calculated | Chapter_7_Evaluation.txt:100 | 100 | 114
7.6 | Synthetic elbow reconstruction error relative to the valid unmasked model reconstruction | Chapter_7_Evaluation.txt:114 | 101 | 115
7.7 | Synthetic wrist reconstruction error relative to the valid unmasked model reconstruction | Chapter_7_Evaluation.txt:125 | 102 | 116
7.8 | Clean-frame distance between the manual wrist label and an accepted filtered wrist measurement | Chapter_7_Evaluation.txt:137 | 103 | 117
7.9 | Reconstructed wrist distance to the same manual wrist label on retained natural-occlusion frames, separately for each arm | Chapter_7_Evaluation.txt:149 | 105 | 119
8.1 | The parts of the offline pass of Chapters 2 to 5 that the causal structure keeps | Chapter_8_Real_Time_Feasibility.txt:28 | 110 | 124
9.1 | The six principal limitations of the system, their causes, and the evidence for each on the recordings | Chapter_9_Discussion.txt:63 (export first clause differs: "The six principal limitations of the system, their causes, and where each one shows on the recordings") | 120 | 134
A.1 | Contents of the recording's session file | Appendices.txt:27 | A2 | 138
B.1 | The workstation and the software versions behind every result in this thesis | Appendices.txt:48 | B1 | 140
C.1 | The eight MediaPipe landmarks used in this work, with the model's indices | Appendices.txt:59 | C1 | 141
C.2 | The right-arm landmarks of the worked-example frame, from the visibility score through the sampled pixel and depth to the back-projected position | Appendices.txt:75 | C4 | 144
D.1 | Factory colour-camera intrinsics, read from the calibration topic of the recording | Appendices.txt:89 | D2 | 146
E.1 | The three marker detections of the worked-example frame, in the order of the panels of Figure E.1 | Appendices.txt:131 | E6 | 154
F.1 | The four candidate smoothers, with the parameters used in Figure F.1(a) | Appendices.txt:160 | F3 | 158
H.1 | The six synthetic datasets | Appendices.txt:192 | H1 | 162
END
LIST d equations | number | section number | section title | PDF page | export source file:line
2.1 | 2.2.2 | Scene Calibration | 27 | Chapter_2_Experimental_Setup.txt:37
3.1 | 3.1 | Coordinate Systems and Transformations | 35 | Chapter_3_Kinematic_Modeling.txt:10
3.2 | 3.1 | Coordinate Systems and Transformations | 37 | Chapter_3_Kinematic_Modeling.txt:16
3.3 | 3.1 | Coordinate Systems and Transformations | 37 | Chapter_3_Kinematic_Modeling.txt:18
3.4 | 3.1 | Coordinate Systems and Transformations | 37 | Chapter_3_Kinematic_Modeling.txt:20
3.5 | 3.1 | Coordinate Systems and Transformations | 38 | Chapter_3_Kinematic_Modeling.txt:25
3.6 | 3.1 | Coordinate Systems and Transformations | 38 | Chapter_3_Kinematic_Modeling.txt:27
3.7 | 3.2.2 | Derivation of the Torso Frame | 40 | Chapter_3_Kinematic_Modeling.txt:39
3.8 | 3.2.2 | Derivation of the Torso Frame | 40 | Chapter_3_Kinematic_Modeling.txt:41
3.9 | 3.2.2 | Derivation of the Torso Frame | 40 | Chapter_3_Kinematic_Modeling.txt:44
3.10 | 3.2.2 | Derivation of the Torso Frame | 41 | Chapter_3_Kinematic_Modeling.txt:47
3.11 | 3.2.2 | Derivation of the Torso Frame | 41 | Chapter_3_Kinematic_Modeling.txt:50
3.12 | 3.2.2 | Derivation of the Torso Frame | 41 | Chapter_3_Kinematic_Modeling.txt:52
3.13 | 3.3.3 | Establishing Local Arm Frames | 44 | Chapter_3_Kinematic_Modeling.txt:69
3.14 | 3.3.3 | Establishing Local Arm Frames | 44 | Chapter_3_Kinematic_Modeling.txt:72
3.15 | 3.4 | Joint Angle Computation | 45 | Chapter_3_Kinematic_Modeling.txt:77
3.16 | 3.4 | Joint Angle Computation | 45 | Chapter_3_Kinematic_Modeling.txt:79
3.17 | 3.4 | Joint Angle Computation | 45 | Chapter_3_Kinematic_Modeling.txt:81
3.18 | 3.4.2 | Shoulder Orientation | 46 | Chapter_3_Kinematic_Modeling.txt:88
3.19 | 3.4.2 | Shoulder Orientation | 46 | Chapter_3_Kinematic_Modeling.txt:90
3.20 | 3.4.2 | Shoulder Orientation | 47 | Chapter_3_Kinematic_Modeling.txt:95
3.21 | 3.4.2 | Shoulder Orientation | 47 | Chapter_3_Kinematic_Modeling.txt:97
3.22 | 3.4.2 | Shoulder Orientation | 47 | Chapter_3_Kinematic_Modeling.txt:100
3.23 | 3.4.2 | Shoulder Orientation | 48 | Chapter_3_Kinematic_Modeling.txt:102
3.24 | 3.4.3 | Elbow Flexion and Extension | 48 | Chapter_3_Kinematic_Modeling.txt:107
4.1 | 4.1 | World Anchoring and Camera Placement Invariance | 55 | Chapter_4_Object_Tracking.txt:9
4.2 | 4.2 | Filtering and Cleaning the Object Track | 58 | Chapter_4_Object_Tracking.txt:25 (export numbers it 4.3)
5.1 | 5.3 | Grip Episodes and the Hand-Object Offset | 67 | Chapter_5_Pose_Recovery.txt:33
5.2 | 5.3 | Grip Episodes and the Hand-Object Offset | 67 | Chapter_5_Pose_Recovery.txt:36
5.3 | 5.3 | Grip Episodes and the Hand-Object Offset | 68 | Chapter_5_Pose_Recovery.txt:43
5.4 | 5.3 | Grip Episodes and the Hand-Object Offset | 69 | Chapter_5_Pose_Recovery.txt:45
5.5 | 5.3 | Grip Episodes and the Hand-Object Offset | 71 | Chapter_5_Pose_Recovery.txt:55
5.6 | 5.3 | Grip Episodes and the Hand-Object Offset | 71 | Chapter_5_Pose_Recovery.txt:58
5.7 | 5.4 | Wrist Recovery From the Object Pose | 72 | Chapter_5_Pose_Recovery.txt:62
5.8 | 5.5 | Elbow Recovery by Two-Link Inverse Kinematics | 73 | Chapter_5_Pose_Recovery.txt:69
5.9 | 5.5 | Elbow Recovery by Two-Link Inverse Kinematics | 73 | Chapter_5_Pose_Recovery.txt:72
5.10 | 5.5 | Elbow Recovery by Two-Link Inverse Kinematics | 73 | Chapter_5_Pose_Recovery.txt:74
5.11 | 5.5 | Elbow Recovery by Two-Link Inverse Kinematics | 73 | Chapter_5_Pose_Recovery.txt:76
5.12 | 5.5 | Elbow Recovery by Two-Link Inverse Kinematics | 74 | Chapter_5_Pose_Recovery.txt:79
6.1 | 6.2 | Coordinate System Conversion | 86 | Chapter_6_System_Integration.txt:38
6.2 | 6.2 | Coordinate System Conversion | 87 | Chapter_6_System_Integration.txt:41
6.3 | 6.2 | Coordinate System Conversion | 88 | Chapter_6_System_Integration.txt:44
6.4 | 6.3 | Avatar Reconstruction in Unity | 89 | Chapter_6_System_Integration.txt:51
6.5 | 6.3 | Avatar Reconstruction in Unity | 89 | Chapter_6_System_Integration.txt:54
6.6 | 6.4 | Scene Reconstruction in Unity | 92 | Chapter_6_System_Integration.txt:75
7.1 | 7.2 | Object Reconstruction Accuracy | 100 | Chapter_7_Evaluation.txt:10
7.2 | 7.2 | Object Reconstruction Accuracy | 100 | Chapter_7_Evaluation.txt:13
7.3 | 7.2 | Object Reconstruction Accuracy | 101 | Chapter_7_Evaluation.txt:15
7.4 | 7.2 | Object Reconstruction Accuracy | 101 | Chapter_7_Evaluation.txt:17
7.5 | 7.3 | Human Reconstruction Accuracy under Valid Landmark Measurements | 107 | Chapter_7_Evaluation.txt:54
7.6 | 7.4.1 | Synthetic Landmark Removal | 115 | Chapter_7_Evaluation.txt:102
D.1 | D.1 | RGB Camera Calibration | 145 | Appendices.txt:80
D.2 | D.3 | Pixel-to-Camera Mapping | 147 | Appendices.txt:98
E.1 | E.3 | From the Rodrigues Form to a Rotation Matrix | 153 | Appendices.txt:123
G.1 | G.1 | Inputs and Initial State | 159 | Appendices.txt:166
END
```

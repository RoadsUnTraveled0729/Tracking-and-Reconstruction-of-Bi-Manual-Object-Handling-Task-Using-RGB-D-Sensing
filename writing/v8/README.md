# V8 final thesis

Delivery branch: master, under the author's 2026-09-14 integration request
recorded in [D-112](condensed/DECISIONS.md). The completed checklist revision
is 156011f; the integration preserves the thesis artifact hashes below.

Current submission-checklist revision, 2026-09-13: the complete Word and
PDF thesis now include paginated contents, figure/table/equation lists,
12-point captions and table text, centred equations within the margins,
a sorted one-page glossary and a numbered acquisition procedure.
References follows Appendix H, as the author requested. The editorial
passes, verified source corrections and all 56 checklist dispositions are
in [SUBMISSION_CHECKLIST_2026-09-13.md](condensed/SUBMISSION_CHECKLIST_2026-09-13.md).

Status: the 200-page PDF and saved Word navigation pass the artifact checks
in [validation.json](condensed/audit_evidence/submission_checklist_2026-09-13/validation.json).
All 339 native mathematical objects retain their content, with punctuation
added to 107 displays. All 52 embedded images and the 27 result tables are
preserved, apart from documented abbreviation and citation updates. No
experiment was rerun. D-103 to D-110 record the changes and verification.
The approval date and submission term remain deferred by the author. The
avatar is laboratory-supplied; no external source credit is requested.
The Linux PDF uses metric-compatible font substitutes; Word specifies
Times New Roman. The checklist record describes the rendering limits.

Reproduction commands and final hashes are in
[SESSION_REVIEW.md](condensed/SESSION_REVIEW.md). Word and PDF remain the
requested deliverables; the LaTeX edition remains cancelled under D-102.
Earlier language and figure reports below are historical.

Figure 3.3 update, 2026-09-13: the L24 coordinate drawing and label are
raised above the rail under [D-096](condensed/DECISIONS.md). This is a
display offset, stated in the caption. Regenerate its local source with
condensed/scripts/make_ch3_chain_final_fig.py before running
condensed/scripts/make_ch3_condensed_figs.py.

Latest figure update, 2026-09-13: Figures 7.1 and 7.2 now have x-y at upper
left, x-z at lower left and a larger 3D Scene view on the right. Their real
video strips remain. D-092, exact unchanged-data comparisons and inspected
PDF pages are recorded in condensed/CH7_OBJECT_3D_2026-09-13.md. Tables,
equations and experimental results are unchanged.

Previous Chapter 7 update, 2026-09-13: Figures 7.3 and 7.4 now show genuine
saved Unity trajectories. Twelve real-video panels and two paired recovery
diagnostics are restored beside the relevant discussion, with the existing
video/Unity pairs placed in the grip and transfer section. D-089 to D-091,
source provenance, final page checks and artifact hashes are recorded in
condensed/CH7_VISUAL_RESTORATION_2026-09-13.md. Equations and experimental
results are unchanged.

Latest figure update, 2026-09-13: Figure 3.4 uses an actual two-hand rail
video frame with its recorded torso landmarks under D-087, and Figure 6.4
is restored to the previous picture under D-088. The earlier
replacement hashes and details are in
condensed/FIGURE_REPLACEMENTS_2026-09-13.md. Equations and experimental results
retain the completed review described below.

V8 is the final undergraduate honours thesis. The complete current manuscript is
Thesis_V8_Condensed.docx and its rendered PDF. All active chapter builders,
source figures, evidence and decision records are under condensed/.

Status: final Scene formulation and renewed equation review completed on
2026-09-13; final delivery evidence is in condensed/DELIVERY_2026-09-13.md.
The earlier delivery had 192 physical PDF pages; the current page count is given above. Mathematical checks cover all
56 numbered equations and supporting calculations; 626 current internal
references resolve. Chapter 7 passes 1147 checks with 21 disclosed skips and no failures.
These are verification counts, not new experimental outcomes.

The final frame structure uses Camera, Camera' (same optical origin, y flipped,
not person-centred), calibrated World and final Scene. Unity remains where
needed to explain the handedness swap. Gravity alignment and floor placement
are operations inside the mapping to Scene, without another named frame.

Design decisions:
- Add three-view object plots while preserving their data: D-092.
- Restore recorded Chapter 7 context with accurate scope: D-089 to D-091.
- Preserve the accepted Chapter 7 evaluation and approved Chapter 10: D-035
  through D-053 and D-067 in condensed/DECISIONS.md.
- Use semantic Craig frames and separate proper rotations from improper maps:
  D-054 through D-064, D-073 and the D-082 frame reduction.
- Print a reproducible common-Scene object/wrist chain: D-068 refined by D-082.
- Retain assembly-only citation numbering: D-069.
- Correct supported equation and rendered-figure defects while preserving
  experimental results: D-079 and D-083 through D-085.

Results and limitations: condensed/DELIVERY_2026-09-13.md links every final
check, defect disposition, figure change and artifact hash. The spawn-axis
and mounting assumptions, visible-proxy reference limits, approximately
16 cm normal-grip check and missing historical loop inputs remain explicit.
Native Word upright equation appearance and the actual approval date remain
manual checks. Local archival assets and recording data are dependencies;
a clean checkout without those inputs has not been demonstrated.

Reproduction: use the exact current commands in condensed/SESSION_REVIEW.md,
with /home/luo/anaconda3/bin/python for builders and /usr/bin/python3 for the
LibreOffice PDF renderer. Source citation identifiers stay frozen. The first
and second deliveries target origin/master under the author's D-078 approval.
The files and hashes for the second delivery are in condensed/audit_evidence/
equation_iteration2_final/changed_files_second_delivery.txt and
delivery_manifest.json. Earlier V8 notes below remain historical.

## Historical V8 progress notes

The current chapters and assembled DOCX/PDF use objective descriptions of
measurement, annotation and validation under [D-028](condensed/DECISIONS.md).
The manual-label methodology names a single annotator once; copyright,
acknowledgments and rig-authoring wording are preserved. The
[revision record](condensed/SELF_REFERENCE_REVISION.md) links the independent
coverage and language checks.

The object-trajectory evaluation separates physical rail measurements,
the fitted ArUco trajectory and sample scatter under
[D-027](condensed/DECISIONS.md). The edited condensed chapter places this
material in Section 7.2; [replacement text](condensed/SECTION_7_3_REVISED.md)
preserves the author's heading "7.3 Object Trajectory in the World Frame".
The available measurements support relative-height and horizontal-direction
checks; full 3D path registration remains unavailable.

Table 2.1 in condensed Chapter 2 uses the author's printed marker sizes
and object dimensions, recorded in [D-026](condensed/DECISIONS.md).
The earlier 50 mm declarations for the desk and object markers are legacy
values, not the 45 mm dimensions used in the current thesis. The wall
marker remains 150 mm. Historical calculation records retain their
original values as provenance.

The finished condensed thesis has a mathematical and logical review in
[condensed/MATH_LOGIC_REVIEW.md](condensed/MATH_LOGIC_REVIEW.md).
Chapter 5's reachable equations and worked example reproduce; the report
identifies an unreachable-target explanation error, recovery-policy
mismatches, and remaining evaluation and exposition corrections. It
includes source locations, independent numerical checks, and evidence in
condensed/audit_evidence/. The reviewed thesis is unchanged by the audit.

V8 holds only what changed since V7 was sent to the supervisor
(2026-09-05 onward). Everything else, including the assembled thesis,
the front matter, Chapters 1 and 6-9 and the appendices, stays in
writing/v7 and is not copied here. A chapter enters V8 when it is
rewritten; when every chapter is here, the three-file delivery of
skill_set/thesis-delivery-protocol.md is assembled from V8.

Contents:
- Round 7 (2026-09-10, supervisor: "Everything looks good", C51-C53;
  D-022): the abstract rewritten in his four parts (the problem and why,
  the challenges, how they were addressed, what was accomplished; 344
  words, condensed/scripts/build_frontmatter.py ABSTRACT), the old
  Chapter 9 split into Chapter 9 "Discussion" (condensed/scripts/
  build_ch9.py: 9.1 Object Tracking Against the Rail, 9.2 Arm Pose and
  the Recovery, 9.3 The Second Arm and the Handover, 9.4 Torso and the
  Hidden Hips, 9.5 Landmark Failures at High Confidence, 9.6 The Live
  Structure, 9.7 Limits of the Model and the Evaluation with Table 9.1)
  and Chapter 10 "Conclusions and Future Work" (build_ch10.py). Sent
  separately as Abstract_V8.docx (scripts/build_abstract.py, the same
  ABSTRACT list), condensed/Chapter_9_Discussion.docx and
  condensed/Chapter_10_Conclusions_Future_Work.docx, with the change log
  Thesis_V8_Changes_Abstract_Ch9_Ch10.docx (scripts/
  make_ch9_ch10_changes.py) and the hand-sync list
  CH9_SPLIT_TEXT_CHANGES.md (scripts/make_ch9_split_text_changes.py).
  PROF_COMMENTS_ROUND7.md holds the comments and their mapping. The old
  Chapter_9_Discussion_Conclusion.docx left the tree; its last build is
  commit de74302.
- condensed/CH7_TRAILS_IMPLEMENTATION.md: the implemented Chapter 7
  presentation revision (D-015 to D-019), with phase-specific Unity
  stills, full wrist coordinate histories and corrected marker-origin
  labels. The original recording and protected inputs retain their
  hashes; condensed/CH7_TRAILS_VALIDATION.txt records the checks.
  condensed/CH7_TRAILS_TEXT_CHANGES.md gives the exact text changes.
- condensed/CH7_TRAILS_REVIEW.md: review of the latest Chapter 7 Unity
  trajectories, with a proposed clearer layout, verified marker-origin
  naming issues and saved wrist discontinuities. The read-only audit
  output is condensed/CH7_TRAILS_AUDIT.txt; the recommendations remain
  advisory under condensed/DECISIONS.md D-014.
- condensed/CH7_RECOMMENDATIONS.md: advisory recommendations for supervisor
  D7-D10, a proposed reply and the verified Unity capture status (2026-09-07).
  These are not approved manuscript changes; condensed/DECISIONS.md D-006.
- Section 7.7 "Handover on the Rail" (2026-09-09, supervisor round 6, C50;
  D-021): the two-hand rail recording (recording_20260909_000024, E-034)
  reported as it came out of the pinned chain. Figures 7.11 to 7.13 and
  Table 7.1 come from condensed/scripts/make_ch7_handover_frames.py (colour
  frames), make_ch7_handover_fig.py (marker origin along the rail with the
  hand at the cube, both model wrists; reads eval/reports/r7_handover.csv/
  json) and make_ch7_handover_trails.py plus render_ch7_trails.py --alias r7
  and make_ch7_trails_fig.py r7 (the Unity trail stills with both wrists,
  E-035; stills and manifest in figures/src/ch7_handover_trails/). The
  recovery section is now 7.8 and the solver check 7.9. PROF_COMMENTS_ROUND6.md
  holds the comment and its mapping; the hip-hold study the section and
  Section 9.2 cite is eval/reports/r7_hip_hold.md.
- CH7_HANDOVER_TEXT_CHANGES.md: the exact old -> new text pairs of the
  handover round (2026-09-09; abstract, Chapters 1, 2, 5, 6, 7 and 9),
  with the new Section 7.7 in full, for hand-syncing an online copy;
  the supervisor-facing summary is Thesis_V8_Changes_Ch7.docx, which since
  2026-09-09 compares this version with the one he last saw (8 September).
- Thesis_V8_Condensed.docx: the condensed thesis (user request 2026-09-06;
  main body cut from about 43,300 to about 29,400 words), assembled by
  condensed/scripts/build_thesis.py from the condensed chapter builders
  in condensed/scripts/ (copies of the v8 builders for Chapters 2-5 and
  of the v7 builders for the rest, cut on the plan of
  condensed/REPEATED_MATERIAL_MAP.md and condensed/CONDENSE_EDITOR_RULES.md).
  The account of what was cut, with before and after counts, is
  condensed/CONDENSE_SUMMARY.md; per-chapter detail in condensed/notes_*.md.
  The originals (v7 as sent, the v8 chapter builds) are untouched.
- Chapter_2_Experimental_Setup.docx: restructured for supervisor round 4
  (C43-C46); built by scripts/build_ch2.py.
- Chapter_3_Kinematic_Modeling.docx, Chapter_4_Object_Tracking.docx:
  only the changes that Chapter 2 forced (Figure 3.2 and Section 4.1
  moved into Chapter 2, figures and sections renumbered); built by
  scripts/build_ch3.py and build_ch4.py. Chapter 3's prose is also
  rewritten in the user's sentence pattern (2026-09-05): every equation,
  figure, number, citation and supervisor anchor kept, sentences
  shortened to the Chapter 2 norm. Both Chapter 2 and Chapter 3 were
  then redrafted against the humanizer prose rules (writing/WRITING_SKILL.md,
  2026-09-06) with an Opus review loop per chapter (writing/reviews/
  Chapter_2_humanizer_round1-3.txt, Chapter_3_humanizer_round*.txt).
- Chapter_5_Pose_Recovery.docx: rewritten for supervisor round 4
  (C22-C28) on the user's plan (occlusion as missing data in a clean
  recording, torso assumed measured, chapter kept simple); built by
  scripts/build_ch5.py. New: the missing-data cases A-C and Figure 5.1
  information flow at the opening, Section 5.1 Assumptions and
  Parameters as prose, Table 5.1 notation, Figure 5.3 schematic for
  equations (5.1)-(5.2), equations (5.5)-(5.6) for the direction memory
  and the wrist-from-elbow case. The V7 torso repair (Section 5.5) is
  parked verbatim in CH5_PARKED.md. Change record: CH5_REWRITE_LOG.md.
- scripts/: the build scripts of the chapters above, eqn.py (Word math),
  frame_draw.py and make_ch2_frames_fig.py (Figure 2.5), make_ch2_fig1.py
  (Figure 2.3), make_ch4_figs.py (imports frame_draw.py), the Chapter 5
  figure scripts make_ch5_flow_fig.py, make_ch5_offset_fig.py,
  make_ch5_holding_fig.py and make_ch5_states_fig.py (Figures 5.1, 5.3,
  5.4, 5.6; Figures 5.2 and 5.5 are copied from v7), and
  add_prof_comments.py (comment sites C1-C21, C22-C28 and C43-C46; it
  runs once a Thesis_V8.docx exists). Unchanged helper scripts and number sources
  are referenced at their writing/v7 paths.
- figures/: only the figures the chapters here use, plus figures/src
  inputs of the figure scripts here.
- PROF_COMMENTS_ROUND2/3/4/5/6/7.md, PROF_COMMENTS_CHECKLIST.md,
  PROF_REPLIES_V8.md: the supervisor comment trace, continued here. Round 5
  (2026-09-07, Chapter 4: two decimals at most everywhere, images of the
  experiment) is applied to the whole condensed thesis; PRECISION_ROUND5_CHANGES.md
  lists every old -> new number pair, condensed/scripts/make_ch4_experiment_fig.py
  draws the new Figure 4.1 and condensed/scripts/ch6_numbers.py is the number
  source of the Chapter 6 worked example's transformation calculation.
  Same night (D-013): condensed/scripts/make_ch7_trails.py and
  make_ch7_trails_fig.py (Figure 7.10, the three trajectories as trails inside
  the Unity scene, with Unity/Assets/Scripts/TrajectoryTrails.cs), and
  condensed/scripts/render_pdf.py, which renders Thesis_V8_Condensed.pdf with
  the contents and the three lists filled through LibreOffice.
- CH2_CONCISION_LOG.md: every edit to the user's own Chapter 2 sentences.
- CH3_HUMANIZER_LOG.md: the Chapter 3 humanizer pass, per section, with the
  review-round dispositions.
- CH7_PARKED.md, CH8_PARKED.md: material that left Chapters 7 and 8 on 2026-09-07 (D-007 rail-led Chapter 7: loop trajectory, loop synthetic masking, torso stability, the loop overlay figure; D-008 Chapter 8 rewrite: the timing tables, the latency figure and the check-suite and angle-difference paragraphs), verbatim from the build of commit 2bcaad6.
- CH5_REWRITE_LOG.md, CH5_PARKED.md: the Chapter 5 rewrite record (comment
  mapping, decisions, symbol renames, review rounds) and the parked V7
  torso-repair material.
- Thesis_V8_Changes_Ch2_Ch3.docx: the concise change log for the supervisor,
  V7 to V8 for Chapters 2 and 3 by his round 4 comments (scripts/
  make_ch2_ch3_changes.py).
- Thesis_V8_Changes_Ch4.docx and Thesis_V8_Changes_Ch5.docx: the same kind of change log for Chapters 4 and 5, one file per chapter, V7 as sent (2026-09-05) to the condensed V8 of 2026-09-07, by his round 4 comments C22 to C29 (Chapter 5) and C46/C38 plus the condensation (Chapter 4); built by scripts/make_ch4_ch5_changes.py (2026-09-07).
- Thesis_V8_Changes_Ch6.docx: the same kind of change log for Chapter 6, V7 as sent to the condensed V8 of 2026-09-07, by C46/C15 (frames and T notation), C38 (precision), the condensation and the Chapter 6 review pass (technical verification against the code, cross-reference check, three Opus prose rounds: writing/reviews/Chapter_6_v8_round1-3.txt; account in condensed/notes_ch6.md section (h)); built by scripts/make_ch6_changes.py (2026-09-07).
- CHANGELOG_CH2_CH3_humanizer.md: sentence-level old -> new list for both
  chapters, c38750c to the current build (for hand-syncing an online copy).
- PROGRESS.md: V8 progress; earlier history in writing/v7/PROGRESS.md.

The condensed thesis PDF is rendered with refreshed contents and lists
under the later user direction recorded in condensed/DECISIONS.md D-013.

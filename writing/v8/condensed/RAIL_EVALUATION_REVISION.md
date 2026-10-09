# Object trajectory evaluation revision

Decision: D-027, completed 2026-09-12.

The author identified the target as "7.3 Object Trajectory in the World
Frame". The section map in notes_revision_ch7.md places that former
section in current Section 7.2, "Object Reconstruction". The builder and
rebuilt Chapter_7_Evaluation.docx are corrected there. SECTION_7_3_REVISED.md
provides concise replacement prose under the author's requested heading.
The current Section 7.3, "Human-Object Reconstruction and Handover", is
unchanged. Section, figure and table numbers are unchanged.

Changes:
- Separate independent physical measurements, the fitted trajectory and
  individual filtered ArUco samples.
- Describe the line as an estimate of the observed trajectory that reduces
  the influence of frame-to-frame tracking noise.
- Compare fitted direction with the horizontal rail setup, and tracked
  height-mode separation with the physical rail height.
- Describe sample-to-line distances as perpendicular deviations and
  tracking scatter. The prohibited term is absent from the rebuilt chapter
  and replacement prose. Historical change records retain their original text.
- Correct the 0.8 cm statistic from depth component to horizontal component:
  the evaluator uses the norm of the x and z deviations together.
- Remove repetitive explanations of why the fit is not a physical reference.

Evidence:
- REVISION_2026-09-11_BRIEF.md section 3 facts 2 and 3: physical route
  lengths and rail dimensions; no independent world-frame registration.
- eval/reports/r6b_rail_eval.json and r7_rail_eval.json: line fits,
  sample spans, tilt and scatter.
- eval/reports/r7_handover.json: handover height modes and per-part scatter.
- eval/gt/eval_rail_scenario.py: filtered sample selection, line fitting,
  vertical and horizontal components.
- Independent subagent factual review: PASS, no blocking corrections.

Limits retained:
- No absolute 3D path, azimuth or cube-orientation accuracy is claimed.
- The horizontal comparison depends on calibrated gravity; the setup has
  no quantified spirit-level uncertainty.
- The height check assumes the marker retains its height above the cube
  base on the two support surfaces. Its inputs are histogram modes, not
  a fitted-line intercept.
- Sample extrema are not independently matched physical endpoints, so the
  tracked extent is not reported as a length error.
- Scatter includes motion away from a straight path and noise remaining
  after filtering; it does not isolate raw sensor noise.
- Existing figures and pinned reports were not regenerated or rewritten.
  The physical-route figure still awaits independent registration.

Validation:
- Chapter 7 automated style check: PASS, zero hits.
- Chapter cross-reference check: PASS, 624 references, none unresolved.
- Prohibited-term check in chapter prose and replacement: PASS.
- Current human-object section preserved verbatim: PASS.
- Isolated commit build: PASS; chapter XML outside the object-trajectory
  section is unchanged from the committed base. Existing unrelated thesis
  revisions remain in the working tree.
- Chapter counts: prose 5381 -> 5318 words; captions 1269 -> 1242;
  headings 33 and table words 147 unchanged.
- Language subagent: PASS, zero violations after removing the redundant
  final clause of the relative-height paragraph. All seven changed
  manuscript paragraphs/captions and five standalone paragraphs passed.
  Report: audit_evidence/rail_evaluation_language_2026-09-12.txt.

Reproduce from the repository root:

    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/build_ch7.py
    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/check_style.py Chapter_7_Evaluation
    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/check_refs.py
    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/count_words.py writing/v8/condensed/Chapter_7_Evaluation.docx

Delivery is the revised chapter and standalone replacement text. The full
assembled thesis was not rebuilt during this section edit.

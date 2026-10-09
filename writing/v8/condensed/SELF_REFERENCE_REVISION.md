# Objective descriptions of experimental procedures

Decision: D-028, 2026-09-12.

Scope: technical prose in Chapters 2, 4, 5, 7, 9 and 10. The remaining
chapters, appendices and abstract required no sentence edits. Section,
figure, table and equation numbering is unchanged.

The changes describe measurements, recording collection, manual pixel
selection, exclusions and depth validation directly. No first-person
substitute was introduced. Section 7.4.2 states once that all manual wrist
labels were produced by a single annotator. The existing label counts,
clean-frame selection, occlusion exclusion criterion and comparison with
the adjacent cube-face depth are retained.

Protected content: copyright permission wording, acknowledgments and the
description of the rig as authored are unchanged. Builder comments and
historical records retain their provenance wording.

Artifacts:
- The six chapter DOCX files were rebuilt from their edited builders.
- Thesis_V8_Condensed.docx was reassembled from the chapter files; its old
  copy predated recent chapter revisions. Front matter, contents and the
  placeholder report were refreshed by the existing assembly script.
- The existing Thesis_V8_Condensed.pdf was refreshed using LibreOffice.
- The local working documents retain the pre-existing uncommitted thesis
  revisions. The commit uses builds from the committed base with only this
  task's wording edits, preserving those unrelated revisions separately.

Validation:
- Independent coverage audit: PASS, 54 checks. All 1,253 numeric tokens
  and 135 equation elements in the six edited working chapters match the
  pre-edit snapshots. Copyright, all seven acknowledgment paragraphs and
  the rig-authoring paragraph are preserved verbatim.
- Independent language review: PASS for all 16 changed paragraph/caption
  definitions. Automated style checks report zero hits in all six chapters.
- Chapter cross-reference check: PASS, 624 references, none unresolved.
- Assembly checks: PASS for element counts, heading order and uniqueness,
  image relationships and placeholder formatting. The existing approval
  date and physical-route figure placeholders remain.
- PDF text check: the only occurrence of the personal author phrase is
  the protected copyright wording. The annotation-role statement appears
  once, and the rig-authoring wording remains present.

Reports:
- audit_evidence/self_reference_coverage_2026-09-12.txt
- audit_evidence/self_reference_language_2026-09-12.txt

Reproduce from the repository root:

    for chapter in 2 4 5 7 9 10; do /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/build_ch${chapter}.py; done
    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/build_thesis.py
    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/check_style.py Chapter_2_Experimental_Setup Chapter_4_Object_Tracking Chapter_5_Pose_Recovery Chapter_7_Evaluation Chapter_9_Discussion Chapter_10_Conclusions_Future_Work
    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/check_refs.py
    libreoffice --headless --convert-to pdf --outdir writing/v8 writing/v8/Thesis_V8_Condensed.docx

The PDF text was checked after export; a full page-by-page typographic
review was not performed.

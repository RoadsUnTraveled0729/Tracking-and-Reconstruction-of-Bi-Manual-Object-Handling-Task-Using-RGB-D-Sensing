# Thesis V9

V9 is the revision round that follows the delivered V8 thesis
(`writing/v8/Thesis_V8_Condensed.docx` and `.pdf`, master commit 12a0553).
It answers the supervisor's comments of 2026-09-14 and the author's task of
the same day (per-recording avatar dimensions in the Unity replay).

Rule for this version (author, 2026-09-14): `writing/v8/` is frozen as the
delivered record and is never edited. `writing/v9/` is a flat copy of
`writing/v8/condensed/` (the live builders, figures, notes, decision log and
the evidence folders the build chain reads), repointed so that it is
self-contained. Everything the V9 round changes happens here.

## Layout

- `scripts/` the builders (`build_ch1.py` to `build_ch10.py`,
  `build_appendix.py`, `build_frontmatter.py`, `build_toc.py`,
  `build_thesis.py`), the Approval scan cropper (`crop_approval_scan.py`,
  `/usr/bin/python3` with PIL; run before `build_frontmatter.py` when
  `figures/src/IMG_2688.jpeg` changes), the PDF renderer (`render_pdf.py`, run with
  `/usr/bin/python3`), the checkers (`check_refs.py`, `check_style.py`,
  `count_words.py`, `verify_submission.py`, `verify_ch7_restructured.py`,
  `validate_ch7_trails_revision.py`, `test_assembly_citations.py`), the
  figure generators and the Chapter 7 evaluation scripts. The three helpers
  that lived in `writing/v8/scripts/` (`build_abstract.py`, `frame_draw.py`,
  `ch5_worked_example.py`) and the Figure 6.5 generator that lived in
  `writing/v7/scripts/` (`make_ch6_unity_fig.py`) are vendored here.
- `figures/` every image a builder reads, including the ones V8 still read
  from the untracked `writing/v7/figures/` and from `writing/v8/figures/`.
  `figures/src/` holds the capture archives of the Chapter 7 Unity runs.
- `audit_evidence/` only the folders the build and verification chain reads
  (`ch7_restructured`, `followup`, `final_completion`,
  `ch7_visual_restoration`, `remove_intermediate_frame`, `figure_3_4_video`,
  `ch7_object_3d`) plus the new `submission_checklist_v9`. The one-off audit
  folders of V8 stay in `writing/v8/condensed/audit_evidence/`.
- `DECISIONS.md` continues the V8 log from D-113. `references.md`, the
  `notes_*.md` files and the V8 briefs are carried over as history.
- Outputs: `Chapter_N_*.docx`, `Appendices.docx`, `FrontMatter_V9.docx`,
  `Thesis_V9_TOC.docx`, `Thesis_V9.docx`, `Thesis_V9.pdf`.

## Build

From the repository root, thesis Python `/home/luo/anaconda3/bin/python`:

```
for n in 1 2 3 4 5 6 7 8 9 10; do python writing/v9/scripts/build_ch$n.py; done
python writing/v9/scripts/build_appendix.py
python writing/v9/scripts/build_thesis.py
/usr/bin/python3 writing/v9/scripts/render_pdf.py
python writing/v9/scripts/check_refs.py
python writing/v9/scripts/check_style.py
python writing/v9/scripts/test_assembly_citations.py
python writing/v9/scripts/verify_submission.py
```

## Status

2026-10-06: V9 was delivered and defended (defence of 2026-10-06). A
post-defence revision round opened the same day on the author's
instruction (writing/ is no longer frozen for this round); change 1 is the
Introduction page 2 citations and transitions (Google MediaPipe
documentation [60], [61], Unity User Manual [62], transition sentences in
Section 1.2; DECISIONS.md D-394). The build chain and checker results hold:
verify_submission 22 of 22 PASS, check_style 0 hits, check_refs UNRESOLVED
none, 168 pages. Change 2 is the signed Approval page: page ii is built
from figures/src/IMG_2688.jpeg (cropped by scripts/crop_approval_scan.py,
run with /usr/bin/python3 and PIL) with Date Approved October 6, 2026
(DECISIONS.md D-395).

2026-09-16: C54 round delivered, 170 pages (was 172); after the author's
review, Chapter 9 and Chapter 10 first went back to prose with at most
two short lists each (D-129), then, on the author's re-reading of the
supervisor's wording, forward again to bullet format in every Chapter 9
section and in both Chapter 10 lists (D-130). A further comment, C55,
asked for plain-language explanation with no bold headings, so Chapter 9
lost Sections 9.1 to 9.7 for seven unlabelled plain-language bullets,
Chapter 10's bullets and the Section 1.4 and Chapter 5 case bullets lost
their bold labels (D-131), and the supervisor closed the round: "We are
Done for now." Final state: verify_submission 22 of 22 PASS, check_style
0 hits, check_refs UNRESOLVED none, citations OK, 168 pages, 31,750 body
prose words; see DELIVERY_2026-09-16.md and DECISIONS.md D-128 to D-131.

2026-09-14 (later): V9 delivered, 192 pages; see DELIVERY_2026-09-14.md and
DECISIONS.md D-113 to D-120. Remaining condensation of Chapters 5 and 6 is
recorded in ../../PROJECT_STATUS.md.

2026-09-14: V9 started. The baseline build of the repointed copy is
identical to the delivered V8: `pdftotext` of `Thesis_V9.pdf` against
`Thesis_V8_Condensed.pdf` differs by zero lines, and every zip member of all
fourteen docx pairs (chapters, appendices, front matter, TOC, assembled
thesis) is byte-identical. Built outputs are committed at delivery, not at
every phase.

Round content (see `../../.claude` plan and `DECISIONS.md` D-113 onward):
per-part page labels for the appendices and references (A1, B1, R1) in the
footers and the navigation lists; List of Equations removed; Chapter 9
opened by a general overview with the specific discussions renumbered 9.2
to 9.8 and condensed; the abstract replaced by the supervisor's text
verbatim; avatar sized per recording (E-036) with the rail and handover
captures re-run and Tables 7.3 and 7.4 regenerated; Sections 6.3 and 7.3
and Chapter 9 revised accordingly.

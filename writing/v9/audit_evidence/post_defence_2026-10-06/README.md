# Post-defence revision 2026-10-06: annotated pages

These five PNG images show, for the supervisor, where writing/v9/Thesis_V9.pdf
(as committed at 55a847b) changed in the post-defence revision of 2026-10-06.
Each image is one PDF page rendered at 150 dpi with a title band on top, red
boxes with lettered tags around the changed text, and a legend below that
explains each tag: page_ii_approval.png (signed Approval page and its date),
page_2_introduction.png and page_3_introduction.png (new citations [19], [28]
and [29] and the new transition sentences in Sections 1.1 to 1.2.3), and
page_R2_references.png and page_R3_references.png (the new References entries
[19], [28] and [29]). Box positions come from the PDF itself, word boxes from
`pdftotext -bbox-layout` and the scanned approval block from the image
placement reported by `pdftohtml -xml`; the images are regenerated
deterministically from the repository root with
`/usr/bin/python3 writing/v9/audit_evidence/post_defence_2026-10-06/annotate_revision.py`
(needs poppler-utils, Pillow, and the DejaVu and Liberation fonts).

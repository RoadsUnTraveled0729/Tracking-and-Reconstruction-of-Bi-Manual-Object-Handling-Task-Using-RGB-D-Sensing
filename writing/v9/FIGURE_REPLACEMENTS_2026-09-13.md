STATUS: COMPLETE
GOAL: Apply the author's two requested figure changes directly.
KEY FINDING: Figure 3.4 uses real recorded video; Figure 6.4 is restored to its previous picture.
VERIFIED: Chapters 3 and 6 and the assembled DOCX built successfully; the PDF renderer refreshed four indexes and produced 189 pages.
ASSUMPTIONS-UNRESOLVED: Prior physical assumptions and native Word/approval-date items remain. No renewed whole-thesis, equation or rendered-PDF inspection pass was performed, as requested.
DECISION: D-087 and D-088 supersede only the previous figure choices.
NEXT: Author review of the replacement images.

Delivered files
- ../Thesis_V8_Condensed.docx
  SHA256 c9880631767aa12da818bc6896ba3ed7ef6182cdc21b6cc6ad26d3fb23d52d09
- ../Thesis_V8_Condensed.pdf (189 physical pages)
  SHA256 8cfec25a5bc433beca1f349abee9b95f077d9883cea5022997fa38bad0c2a135

Figure 3.4
The replacement is actual frame 1400 of recording_20260909_000024, the
two-hand rail recording, at 46.699725 seconds. The original tracked RGB
image is figures/src/r7_frame01400.png. Labels L12, L23 and L24 and their
vectors use the corresponding filtered landmark measurements, with the
recorded intrinsics. No image content or measured landmark is relocated.
Panel (a) shows the two torso input vectors; panel (b) projects the derived
axes from the right-hip origin. Section 3.2.2 and the caption identify this
illustration. The frame-533 worked example and all equations/results remain
unchanged. The compact audit_evidence/figure_3_4_video/source.json pins the
source image, row, original CSV/meta hashes and derived geometry. Regeneration
requires only that committed record and the tracked image.

Figure 6.4
The PNG and generator are restored byte-for-byte from e69dfa6. The caption
and first introductory sentence now describe the four-frame conversion
before gravity alignment. Section 6.4 retains gravity alignment, floor
translation and the full Scene transform. No removed frame is restored.
No Chapter 6 equation, calibration or experimental result changes.
Restored PNG SHA256:
e820cc8c57a48c1b9f9ee7420a0bc9e318e9f2bbcad732301264868d40478249

Reproduction from the repository root
/home/luo/anaconda3/bin/python writing/v8/condensed/scripts/make_ch3_torso_video_fig.py
/home/luo/anaconda3/bin/python writing/v8/condensed/scripts/build_ch3.py
/home/luo/anaconda3/bin/python writing/v8/condensed/scripts/build_ch6.py
/home/luo/anaconda3/bin/python writing/v8/condensed/scripts/build_thesis.py
/usr/bin/python3 writing/v8/condensed/scripts/render_pdf.py
The restored Figure 6.4 generator is make_ch6_frames_final_fig.py; this
revision restores the exact previous PNG instead of regenerating it.

Audit and Git
The before-build baseline is master commit
9a0d7ce0ca6a541961336400cde7576f6dde0a40. Its complete numerical and visual
review remains preserved in equation_iteration2_final and the earlier
DELIVERY_2026-09-13.md text. Current build logs and the replacement manifest
are in audit_evidence/figure_3_4_video. The frame/notation asset verifier now
expects the photographic Figure 3.4. No new broad correctness audit is claimed.
The current commit is identified by git log -1 --format=%H --
writing/v8/condensed/FIGURE_REPLACEMENTS_2026-09-13.md and is delivered to
origin/master using the author's standing normal-push authorization.

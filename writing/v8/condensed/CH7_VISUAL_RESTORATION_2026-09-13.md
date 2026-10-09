STATUS: COMPLETE
GOAL: Restore substantial real-video context in Chapter 7 and use Unity trajectories for Figures 7.3 and 7.4.
KEY FINDING: Chapter 7 now contains nine figure groups, distributed beside the relevant object, human-object and natural-occlusion discussion.
VERIFIED: DOCX/PDF rebuilt; all nine figure pages inspected; 626 internal references resolve; Chapter 7 PASS 1147 / SKIP 21 / FAIL 0. Its nine result tables and six equation displays remain unchanged.
ASSUMPTIONS-UNRESOLVED: No new unresolved image or content issue. Existing U-1 to U-5 and manual Word/approval-date items Q-1/Q-2 remain applicable.
DECISION: D-089 to D-091 restore recorded evidence and correct its presentation without changing experimental results.
NEXT: Author review of the updated manuscript; normal delivery to origin/master under the standing authorization.

Reason:
The author requested more of the earlier real-video and Unity imagery in its
relevant Chapter 7 locations. The current manuscript at master 7243a20 is the
baseline. Existing captures provide the requested illustrations, with their
original data and visual discrepancies preserved.

Delivered files:
- ../Thesis_V8_Condensed.docx
  SHA256 04066056b0382906474d56d33af7de9cf854afc494079c849068a910b96de279
- ../Thesis_V8_Condensed.pdf, 193 physical pages
  SHA256 93016e067fb5c7299ebd2327d9660c06920185adb0895cf10575fe95f6bf065a

Exact changes and placement:
- Section 7.2: scope the statement about physical paths to the reconstructed
  trajectory plots. The Unity views have an explicitly schematic scene guide;
  no surveyed physical path or registered physical waypoint is claimed.
- Section 7.2.1, Figure 7.1, PDF page 116: add four real rail-video frames
  (95, 505, 700, 898) above the unchanged Scene waypoint plots. The selected
  pictures illustrate acquisition, lift, slide and the far end. They do not
  define the quantitative waypoint estimates.
- Section 7.2.2, Figure 7.2, PDF page 119: add four real handover-video frames
  (700, 950, 1042, 1200) above the unchanged Scene waypoint plots. Caption the
  last still as arrival at the far end; it does not depict the release event.
- Section 7.3.1, Figure 7.3, PDF page 123: replace the coordinate-only human
  plot with three genuine saved Unity trajectory views, covering carry
  (92-500), lift (501-528) and slide (529-899).
- Section 7.3.2, Figure 7.4, PDF page 125: replace the coordinate-only human
  plot with three genuine saved Unity trajectory views, covering the right
  hand (137-863), transfer (864-1022) and left hand (1023-1498).
- Both Unity figures show marker-centre and model-wrist trails, with the
  avatar/cube posed at the final frame of each presentation interval. They
  do not show elbow trails or the exact table subsets of rendered rig joints.
  Captions preserve that distinction. Omit the old outer Start/W1/W2/W3
  annotations, whose roles conflict with the current W1-W4 measurement
  waypoints. Label the retained dashed line Schematic scene guide. Captured
  Unity rasters, trajectory samples and scale bars are retained.
- Section 7.3.3, Figures 7.5 and 7.6, PDF pages 127 and 129: move the existing
  six video/Unity pairs into the single-hand grip and transfer discussion.
  The images and capture-configuration disclosures remain unchanged. This
  supersedes D-080's separate Section 7.3.4 gallery placement.
- Section 7.4.2, Figure 7.7, PDF page 133: add four real natural-failure frames
  (1427, 1462, 1777, 1890) after the loop-recording context and before Table
  7.8. The first three concern the left arm; the fourth concerns the right.
- Section 7.4.2, Figure 7.8, PDF page 134: restore the paired frame-1462
  left-wrist diagnostic beside the recovery-method explanation and before
  Table 7.9. The manual proxy, object-derived estimate and reconstructed arm
  are identified separately.
- Section 7.4.2, Figure 7.9, PDF page 135: restore the paired frame-1890
  right-wrist diagnostic after Table 7.9. Its caption distinguishes the
  object-derived estimate from the final wrist placed by the recovered arm.
- Front matter: regenerate the contents and figure list. The PDF renderer
  refreshes four indexes. Figure numbering is contiguous, 7.1 through 7.9.
- Formatting: enlarge the three video-strip headers to 50 pixels, about
  8.46 points at 6.1-inch width. Preserve all twelve source-frame regions
  pixel-for-pixel. Keep figure captions together to prevent the first
  render's split Figure 7.4 caption.

Numbers, equations and tables:
No experimental result changes. The six equations (7.1-7.6), all nine result
tables, computational builder statements and pinned numeric inputs are
unchanged. Canonical XML comparison against 7243a20 confirms exact equality
of all fifteen Chapter 7 tables, including the six display-equation tables,
and all six OMML displays. The new diagnostic captions repeat existing
per-frame results: 14.0/13.7 cm for frame 1462 and 14.0/5.0 cm for frame 1890.
These are individual examples, not additional population statistics.

Evidence:
audit_evidence/ch7_visual_restoration contains:
- sources.json and compose_unity_trajectories.py: saved Unity capture,
  interval, trail, legend and output provenance. Regeneration no longer
  requires ignored recovery-angle CSVs; their hashes remain optional
  historical provenance. Both outputs are identical with those inputs absent.
- supporting_manifest.json, supporting_PROVENANCE.md and supporting_compose.py:
  the twelve real-video panels and two unchanged diagnostic PNGs, with source
  hashes and pixel-identity checks. The manifest's proposed captions are
  source notes; the exact delivered captions are in pdf_layout.json.
- integration_review.json: independent source/arm/point/caption checks and
  computational AST, equation and table equality. The far-end caption finding
  is resolved.
- document_preservation.json: exact canonical DOCX table/equation equality.
- pdf_layout.json and page_*.png: final nine figure pages and complete
  captions. initial_layout preserves the first render's formatting evidence.
- build and consistency logs; delivery_manifest.json and changed_files.txt
  identify the final artifacts and complete change set.

Validation:
- Chapter 7 and full assembly: PASS; 52 embedded images resolve; 339 OMML
  objects and 84 tables in the assembly match the sum of its parts.
- Literature mapping: PASS, 132 citation occurrences and 57 contiguous cited
  bibliography entries. Assembly-only renumbering remains unchanged.
- check_refs: PASS, 626 references, 50 figures, 27 detected tables, 52 numbered
  chapter equations, 71 sections; no unresolved reference or numbering gap.
- check_style: zero hits in all ten chapters and appendices. The sole
  front-matter acknowledgment false positive remains; the script therefore
  exits 1 for that pre-existing item.
- verify_ch7_restructured: PASS 1147 / SKIP 21 / FAIL 0. The disclosed skips
  concern existing missing inputs or physical-reference limits.
- verify_final_frames: PASS 18 / FAIL 0, including display-equation grid and
  script-slot checks.
- verify_camera_frame_terminology: PASS 27 / FAIL 0. All current images are
  embedded; printed Word parts contain no removed or replacement frame name.
  Repository historical terminology remains classified as provenance.
- All nine final figure pages visually inspected: complete image groups,
  readable labels/legends and intact captions. The first-render small titles
  and split caption are corrected. No new full mathematical audit is claimed.

Reproduction from the repository root:
/home/luo/anaconda3/bin/python writing/v8/condensed/audit_evidence/ch7_visual_restoration/supporting_compose.py
/home/luo/anaconda3/bin/python writing/v8/condensed/audit_evidence/ch7_visual_restoration/compose_unity_trajectories.py
/home/luo/anaconda3/bin/python writing/v8/condensed/scripts/build_ch7.py
/home/luo/anaconda3/bin/python writing/v8/condensed/scripts/build_thesis.py
/usr/bin/python3 writing/v8/condensed/scripts/render_pdf.py
/home/luo/anaconda3/bin/python writing/v8/condensed/scripts/check_style.py
/home/luo/anaconda3/bin/python writing/v8/condensed/scripts/check_refs.py
/home/luo/anaconda3/bin/python writing/v8/condensed/scripts/verify_ch7_restructured.py
/home/luo/anaconda3/bin/python writing/v8/condensed/scripts/verify_final_frames.py --docx writing/v8/Thesis_V8_Condensed.docx
/home/luo/anaconda3/bin/python writing/v8/condensed/scripts/verify_camera_frame_terminology.py --docx writing/v8/Thesis_V8_Condensed.docx --evidence-dir /tmp/ch7-notation-recheck

Git:
Baseline: 7243a2060df433a8ea6c3814ca7b594c8273618d.
Delivery target: origin/master, normal push with no history rewrite.
Identify this delivery's commit with:
git log -1 --format=%H -- writing/v8/condensed/CH7_VISUAL_RESTORATION_2026-09-13.md
The prior figure replacement and complete equation-review records are retained.

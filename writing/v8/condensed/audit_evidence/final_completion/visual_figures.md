# Rendered figure QA, 2026-09-12

This report records actual pdftoppm image inspection, not XML-only validation.
First inspected PDF SHA256: e06bdb982863b16980440a80f5ae1fd3adabe67a04d11a4bb50d0e5e48073f56
First inspected PDF: 184 physical pages. Page numbers below are physical
PDF pages, followed by the printed thesis page where useful.

- Page 31 (11), Figure 2.4: both panels and caption visible. The scene origin
  is correctly named as the drawn floor, not the body root. Panel (a)'s C
  label is explicitly identified by its caption. Camera' body-kinematics
  prose below explicitly states the common optical origin and no person centre.
- Page 32 (12), Figure 2.5: all four Craig transform labels and semantic frame
  labels fit. Caption explicitly distinguishes reference-to-described arrows
  from the opposite direction of point-coordinate conversion. The inline
  homogeneous coordinate equation above is complete, including both trailing
  homogeneous ones.
- Pages 43/44 (23/24), Figure 3.1: diagram labels are visible and frame pairs
  correct. Initial rendering places the figure on page 43 and its caption at
  the top of page 44. Reported to parent for a keep-with-caption correction.
  Equation 3.1 on page 44 has complete Camera/Camera' point labels and F.
- Page 45 (25), Figure 3.2: Camera/Camera' axes, same optical origin,
  unchanged wrist values and non-person-centred title are visible without
  the earlier right-side clipping. Figure and caption agree.
- Page 98 (78), Figure 6.4 and equation 6.1: four pre-levelling frames,
  inverse flip, calibrated rotation/translation and swap are visible.
  Equation 6.1's Levelled-related discussion does not rename Unity as Scene;
  the matrix and all long frame labels are complete. No placeholder boxes.
- Page 119 (99), Table 7.3 and Figure 7.3: table columns, plot axes, n=100
  titles and legend entries are visible. Caption correctly identifies Scene
  coordinates and the floor-origin difference from Levelled.
- Page 120 (100), Table 7.4: all four rows and numeric columns visible,
  right n=650 and left n=589. Large white space below reflects the next
  full-height figure; no content is cut off.
- Page 121 (101), Figure 7.4: right/left sample counts match Table 7.4;
  caption identifies the upper/right and lower/left rows correctly. Initial
  rendering overlaps the upper-row Unity x labels with lower-row titles.
  Reported to parent for a figure spacing correction before final export.

These are visual layout checks, not new experimental measurements.
Word-only native OMML upright rendering remains outside this PDF check.
The two reported formatting defects require final re-render confirmation;
this first-pass record does not claim that confirmation in advance.

## Chapter 5 source-figure follow-up

The parent's rendered-page review found stale world-frame/R_obj labels in
Figure 5.3. Direct image inspection additionally found the same stale
world-frame input in Figure 5.1. Condensed-local generators and assets now
correct both, under D-076:

- scripts/make_ch5_flow_final_fig.py -> figures/ch5_fig_flow.png: names the
  Levelled pose after the swap and levelling of Section 5.3; uses the equation
  5.7 reference instead of the old bare R_obj formula.
- scripts/make_ch5_offset_final_fig.py -> figures/ch5_fig_offset.png: prints
  the full Levelled/MappedMarker rotation relation, Levelled positions,
  MappedMarker offset, and the transposed rotation for reading the offset.
  The reference axes are Levelled and the cube axes are MappedMarker.

Both final generated PNGs were opened and visually inspected. Added
annotation space and moved text prevent the longer semantic expressions
from overlapping the unchanged illustrative wrist/cube geometry. All
illustrative point coordinates, angles and offset values are unchanged.
The builder owner was informed when both images were final and ready.

The remaining Chapter 5 source PNGs were also opened: detector schematic,
holding-state diagram and two-link IK schematic. None contains a
contradictory Person/Camera frame or World/Levelled transform label. Their
local point/vector names are diagram labels, not missing Craig R/T frame pairs.

## Final render confirmation

Final PDF SHA256: b8bc42ee392f50cc7df626c704964ca254bd4ba9d9a70ca8aae78b82ebda1938
Final document: 184 physical pages.

The replacement PDF was rasterized with pdftoppm and the actual page PNGs
were opened with view_image. Physical pages 44, 72, 79 and 121 were checked
after the final build.

- PASS page 44 (24): Figure 3.1 and its caption are now together on the
  same page. All root/shoulder/elbow frame labels are visible. The initial
  detached-caption finding is closed.
- PASS page 72 (52): Figure 5.1 shows the Levelled object-pose input after
  swap and levelling, and refers to equation 5.7 for wrist recovery.
  Diagram and caption are attached; no stale world-frame input remains.
- PASS page 79 (59): Figure 5.3 contains both full Craig expressions,
  Levelled reference axes and MappedMarker axes. Text is clear of the
  unchanged wrist/cube geometry. The displayed equation 5.2 above and
  caption below agree with the image; neither equation is clipped.
- PASS page 121 (101): Figure 7.4 now has separated rows and Scene-labelled
  axes. The upper x-axis labels no longer collide with the lower titles.
  Right n=650 and left n=589 remain visible and agree with the caption
  and Table 7.4. The first-render overlap finding is closed.

No unresolved defect remains from this delegated figure inspection.
Native Microsoft Word rendering of upright OMML labels remains a separate
manual QA item; this report verifies the delivered LibreOffice PDF.

## Final artifact provenance after the Chapter 5 equality clarification

Current delivery PDF SHA256:
08f85efbc57af62f9b5e2a26b5761cc6e513e8c747e0982167555e8109b1029e

All four pages were rasterized again with the same pdftoppm settings
(-scale-to 1900, PNG, single page) and compared with the previously opened
page images. Pages 44, 72 and 121 are byte-identical to the visually verified
PNGs. Page 79 differs in the explanatory prose below the figure; its new
PNG was opened and visually rechecked. Figure 5.3, its full Craig equations,
caption and the page's text remain complete and unobscured. PASS.

Current page PNG SHA256 values:

- Physical page 44: 85e9a811d1c217d08715e5413470c40e04b1a3e38fe925c71c24955b835b928b
- Physical page 72: 05ecc2cd0d9a5649265520d2da907379c770852e44a0e62d3e6d4951d80c64f3
- Physical page 79: 896ade14ee87e8a101277ca2c0791e00f69a6c8c9cea1f72ae6ab1ad5da7fab6
- Physical page 121: a233a5c9d841d6bda3a16c127fc45dd9799e7f26e18c7328c1a66f2c3f5fb8b1

Final inventory review found no remaining nomenclature defect among the
inspected current figure dependencies. A source scan of the six corrected
condensed figure generators finds no person-space/Person frame, Sensor
Craig label or stale root/shoulder/elbow/object R/T shorthand. Historical
shared figures are preserved and the current builders select the corrected
local assets. Generic diagram-local point/vector names and Figure 2.4's
caption-declared raw-camera C label are not conflicting frame definitions.
No source changes were made during this provenance confirmation.

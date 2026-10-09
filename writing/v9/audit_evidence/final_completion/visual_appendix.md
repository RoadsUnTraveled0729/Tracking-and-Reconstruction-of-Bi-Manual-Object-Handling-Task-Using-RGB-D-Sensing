# Appendix and evaluation-table rendered review

STATUS: COMPLETE
GOAL: Inspect actual rendered appendix equations and representative Chapter 7 tables.
KEY FINDING: Equation displays are complete; one table-header pagination defect and one Chapter 7 figure-label overlap were found and corrected in sources.
VERIFIED: The pages below were rasterized with pdftoppm and visually opened using view_image, rather than checked only through PDF text or DOCX XML.
ASSUMPTIONS/UNRESOLVED: Native Microsoft Word upright OMML appearance remains manual QA.
DECISION: Preserve the mathematics and data; apply the narrow D-076 formatting corrections.
NEXT: Native Microsoft Word appearance check remains manual; no rendered-PDF defect remains in this review scope.

Initial inspected PDF SHA256: e06bdb982863b16980440a80f5ae1fd3adabe67a04d11a4bb50d0e5e48073f56
Page numbering below is physical PDF page numbering; printed body-page numbers are 20 lower in this render.

## Pages visually inspected

- Physical 113: Table 7.1. All five headers and all three waypoint rows are complete; physical versus reconstructed lengths and absolute/relative error labels are distinct.
- Physical 115: Table 7.2. All cells and caption are complete; the caption correctly identifies handover marker-centre segment lengths.
- Physical 162: Appendix C introduction and Table C.1. Complete table, caption and landmark-extraction text.
- Physical 165: Appendix C worked deprojection and Table C.2. Both x/y calculations and all raw camera-coordinate rows are complete; raw versus filtered distinction remains explicit.
- Physical 166 (additional page): Equation D.1 and Table D.1. Projection fractions, equation number and calibration table are complete.
- Physical 167: Figure D.1 and alignment description. Figure labels and caption are legible and complete.
- Physical 168: Equation D.2, corrected Pixel-to-Camera heading, Camera/Camera' definition and numeric deprojection. No clipping or visible OMML placeholders.
- Physical 174: Equation E.1. The operator and its number are complete. Table E.1 begins at the bottom; its header splits across the page break.
- Physical 175 (additional page): Table E.1 continued with the isolated header remainder 'frame (m)'. The concrete Camera/Object matrix, trace equation, Camera axis and skew matrix are all complete.
- Physical 176: Squared skew matrix and recomposed Camera/Object rotation. Both frame labels and all matrix entries are visible; no equation clipping or visible placeholder boxes.
- Physical 121: Figure 7.4. Upper x-axis labels intersect lower panel titles; axis labels say Unity although the stored comparison coordinates are in Scene.

## Supported corrections

Table E.1: build_appendix.py now sets cantSplit and tblHeader on that table's header row and keep_with_next on its header paragraphs. Only pagination properties changed. Appendix rebuilt; check_style reports zero hits.

Figures 7.3/7.4: make_ch7_valid_joint_figures.py now allocates constrained-layout hspace=0.16 and labels axes Scene x, Scene z and Scene y. The generator's CSV input, sample selections, plotted coordinates, centimetre conversion, axis limits, view and data series are unchanged. Both assets were regenerated. The new Figure 7.4 PNG was visually opened and its upper axis labels are now clearly separated from lower titles. Final assembled-PDF appearance still requires the recheck below.

## Reproduction

Render the current assembled thesis with the repository's render_pdf.py and the system Python/UNO environment. Rasterize any inspected physical page, for example:

    pdftoppm -f 168 -l 168 -scale-to 1600 -png -singlefile writing/v8/Thesis_V8_Condensed.pdf /tmp/thesis-page168

Open the generated PNG for actual visual inspection. These checks do not establish Microsoft Word's native upright handling of semantic frame labels.

## Final rendered recheck

STATUS: PASS
Final PDF SHA256: b8bc42ee392f50cc7df626c704964ca254bd4ba9d9a70ca8aae78b82ebda1938
Final DOCX SHA256: ca3faf2767cba1fa652f11a8ce71bad982f58ca31a2eb9e9c974e477c4cb93a2

- Physical 121 was rasterized anew and visually opened. Figure 7.4 now has a clear gap between upper axis labels and lower panel titles. All axes name Scene; panel titles, counts, legends, points and caption are complete.
- Physical 174 was rasterized anew and visually opened. Equation E.1 remains complete, and the split table header no longer appears at the bottom.
- Physical 175 was rasterized anew and visually opened. Table E.1 now has its complete header and all three rows together at the top, followed by its complete caption. The Camera/Object matrix and trace equation remain complete and legible.
- Final physical pages 113, 115, 162, 165, 166, 167, 168 and 176 were each rasterized anew. Their PNG hashes exactly match the corresponding images visually inspected in the initial review, so those page appearances are unchanged in the final PDF.
- figure7_data_preservation.json independently compares actual plotted coordinates, axis limits, view and titles between the HEAD and current generators with saving disabled: all 12 data series across six panels are identical.
- verify_camera_frame_terminology.py passes all 12 checks on the final DOCX, including exact embedded-image identity for all eight corrected figures. The final bibliography was independently rescanned: 132 citations and 57 contiguous, cited entries remain.

Only native Microsoft Word's semantic-frame upright rendering remains outside this visual verification. All defects found within the pages reviewed here are fixed in the final PDF.

## Latest assembly confirmation

Final PDF SHA256: 08f85efbc57af62f9b5e2a26b5761cc6e513e8c747e0982167555e8109b1029e
Final DOCX SHA256: 00eb9037ca34c93838d1afa26c2ed196209cf7cdc2dc152b3595fe14999c6906

After the final Chapter 5 equation presentation fix, physical pages 113, 115, 121, 162, 165, 166, 167, 168, 174, 175, 176 were rasterized again. Every PNG exactly matches the corresponding page already visually inspected above. No repeated visual inference is needed: visual_appendix_final_equivalence.json records the matching image hashes. Terminology verification remains PASS 12 and the independent bibliography scan remains PASS with 132 citations and 57 contiguous cited entries. The updated PDF retains every appendix/table/figure correction verified here.

STATUS: COMPLETE
GOAL: Correct the supported Chapter 2-4 findings after the D-082 removal milestone, then review every numbered and unnumbered mathematical item in the delivered chapters.
KEY FINDING: C234-01 through C234-09 are resolved without changing pinned experimental results or frozen implementation. The final assembled DOCX passes 80 of 80 independent/source-identity checks.
VERIFIED: All 28 numbered equations, 21 unnumbered display items, 48 inline-math paragraphs and two math-bearing tables were re-read and matched to the final DOCX. All 45 rendered Chapter 2-4 pages were inspected; both identified figure-label overlaps were corrected under D-085.
ASSUMPTIONS-UNRESOLVED: Native Microsoft Word rendering remains manual QA. This work does not establish physical uncertainty bounds or verify every invalid-input/near-singular runtime branch.
DECISION: D-080 supplies the illustrative torso schematic; D-083 resumes supported correctness fixes after D-082; D-085 authorizes the two observed figure-label corrections. The original equation_iteration2 evidence is preserved.
NEXT: Parent-owned global delivery checks and Git integration. No Chapter 2-4 source change remains pending.

Reason:
The first audit correctly identified defects in the surrounding mathematical definitions, dimensions, captions and implementation description even though its 54 independent numerical checks passed. The final diagnostic retains those counterexamples as historical evidence and adds assertions for the corrected delivered text and formulas. Its 80/80 result now covers the supported corrections as well as the original numerical checks.

Evidence:
Final assembled DOCX: writing/v8/Thesis_V8_Condensed.docx
SHA256: d99335e683b9cf2cebcfdf424be495a9b1d9f9a52a4fbd30c6815036c4996b14
Final PDF: writing/v8/Thesis_V8_Condensed.pdf, 189 pages
SHA256: 4e1e00cd0dd6c6c93a2b20d9f9abd6a2996c646e6aae3d38a35ee9ef2c727f9d

ch2_ch4_input_hashes.json pins the final document, chapter builders, figure assets/generators, diagnostic and relevant implementation/data files. ch2_ch4_math_inventory.json records each mathematical item and confirms its presence. The check uses a per-chapter multiset, so a matching expression elsewhere in the thesis cannot satisfy a missing chapter expression. The final heading parser requires a chapter number immediately followed by a colon; a prose sentence such as "Chapter 2 ends ..." is not a heading.

Supported-finding dispositions:

- C234-01 RESOLVED: both closing Section 3.5 point-transform relations include the final homogeneous 1 on each point. Their 4 by 4 products are dimensionally valid, and the three-coordinate results retain the original values.
- C234-02 RESOLVED: the inline g-hat definition before equation 3.24 divides the rotated forearm vector by its length and is explicitly a unit direction. The independently reconstructed norm is one.
- C234-03 RESOLVED: the false alternative reference-pose example is removed. The valid diagonal (-1,1,-1) reference matrix and its (0,180,0) Euler result remain.
- C234-04 RESOLVED: the zero-twist sentence names f-prime after un-swinging. Its nonzero perpendicular component has unit direction (-sin(t_t),cos(t_t)) in the shoulder y-z plane. Equation 3.22 remains an active operator with both vectors expressed in L12.
- C234-05 RESOLVED: Figure 3.5's caption states that zero-pose frames share the root orientation; the right arm extends along +x and the left along -x. The correct photograph overlay is unchanged.
- C234-06 RESOLVED: the stored-state enumeration includes two redundant elbow elevation fields: thirteen stored values and eleven independent angular quantities. The actual interface is unchanged.
- C234-07 RESOLVED: Chapter 2 defines the implemented horizontal tabletop model through a depth-derived point, with calibrated gravity as normal. Table 2.3 and Chapter 4 consistently describe heights above that model. The pinned 3.8 mm origin offset, 15.4 cm camera height and 6.3 cm marker height remain.
- C234-08 RESOLVED: Chapter 4 retains the 6.3 cm and 7.3 cm comparison, identifies the marker centre as a cube-centre height proxy for the mounting/orientation, and states that the discrepancy's sources have not been separated. The unsupported resolution/uncertainty assurance is removed.
- C234-09 RESOLVED: Chapter 2 describes absolute residuals from each sample's own centred rolling median, followed by a second centred seven-frame median and the scale factor. Appendix F carries the exact implementation factor 1.4826. Independent ramp and spike/missing-value masks match the frozen implementation. The window, three-scale threshold, 2 cm floor and filtered data are unchanged.

Numbered-equation review after correction:

2.1 PASS: SVD projection, determinant correction and Frobenius minimum; reproduces the ten-detection calibration.
3.1 PASS: F is an involutory reflection with the shared optical origin, not a proper frame rotation.
3.2 PASS: homogeneous point relation and pose block have four-dimensional points and the stated bottom row.
3.3 PASS: parent-to-child direction conversion uses the transpose without translation.
3.4 PASS: inverse point translation has the correct subtraction and -R-transpose times origin order.
3.5 PASS: root, shoulder and elbow pose blocks use their respective origins and parent coordinates.
3.6 PASS: the three factors compose from L14 to Camera'; the corrected closing point check reconstructs the measured elbow.
3.7 PASS: normalized L23-to-L24 hip direction points toward the subject's right.
3.8 PASS: L24-to-L12 spine-side vector has the correct endpoints and metric units.
3.9 PASS: cross-product order gives forward in the declared Camera' convention for non-collinear inputs.
3.10 PASS: the second cross product closes the proper orthonormal basis from exact unit/perpendicular inputs.
3.11 PASS: [right,up,forward] columns map root components into Camera', with determinant +1.
3.12 PASS: translation is the L24 Camera' point; the adjacent reference example is now correct after C234-03.
3.13 PASS: shoulder origin subtracts L24 before rotation into the root; its zero forward coordinate follows from the constructed plane.
3.14 PASS: elbow origin subtracts the shoulder and rotates into the coincident shoulder/root basis.
3.15 PASS: fixed parent-axis applied order z,x,y gives Ry*Rx*Rz on column vectors.
3.16 PASS: every expanded entry agrees with independent Rodrigues multiplication over 60 generic angle cases.
3.17 PASS: regular extraction and both exact gimbal branches recompose correctly, including 18 singular reference cases.
3.18 PASS: right shoulder composition Ry*Rz*Rx places twist innermost and matches the frozen convention.
3.19 PASS: its first column is the stated arm direction and is independent of twist.
3.20 PASS: asin extracts restricted elevation from a unit direction.
3.21 PASS: atan2 sign/order extracts azimuth, with the stated exact vertical convention.
3.22 PASS: un-swing order Rz(-z)*Ry(-y) is correct, both vectors retain L12, and the corrected adjacent text refers to the operated vector.
3.23 PASS: atan2(-f-prime_y,f-prime_z) extracts observable twist; magnitude cancels.
3.24 PASS: the corrected unit g-hat supplies the required input; exact observable geometry reconstructs both segments and gives zero elbow elevation.
4.1 PASS: inverse anchor times camera/object pose gives world/object pose; common camera-transform invariance requires a correspondingly updated calibration, as the text states.
4.2 PASS: rigid inverse has the transposed rotation and -R-transpose times translation.
4.3 PASS: norm and relative-angle bounds use elapsed time from the last kept sample. Unity/MappedMarker labels match the implementation; orthogonal conjugation preserves the relevant distances and relative angle. Independent cleaning agrees for all 900 rows.

Unnumbered, inline, table and numerical review:

- Chapter 2: five inline-math paragraphs and two math-bearing tables were reviewed with the homogeneous relation, frame-chain order, S/F declarations, SVD relation and wall/gravity semantics. The D-082 Scene inventory and full Scene/Unity transform are retained. The exact rolling-residual description agrees with the implementation and Appendix F.
- Chapter 3: all 16 unnumbered display items and 35 inline-math paragraphs were reviewed, including both singular root branches, root/shoulder/elbow chains, all worked vectors/matrices/angles, unit-direction definitions and both corrected homogeneous closing checks. Table 3.1's sixteen triples retain their values. Independent root Euler cases, both arms and their mirrored segment reconstruction pass. The illustrative Figure 3.4 now has no photographic measurement claims.
- Chapter 4: all five unnumbered display items and eight inline-math paragraphs were reviewed. The ten-pose calibration, inverse camera placement, frame-533 object pose and model-relative heights reproduce. The missing-frame example retains its interpolation and cleaning results: 899 detected rows of 900, frame 786 blanked, no detected-sample rejection. Figure 4.1 keeps its per-frame estimate versus frozen-anchor distinction.

ch2_ch4_scope_comparison.json confirms that all 28 numbered and all 21 unnumbered display mathematical expressions match the original audit. The revised mathematical definitions are inline. Its four complete worked-value groups are equal to the baseline, and all 17 common frozen implementation/data hashes match. The removed false reference-pose example is not an experimental result. No inference, raw measurement extraction or experiment was rerun.

Visual changes and final verification:

D-080 Figure 3.4 is a front-view schematic with L24 on the viewer's left, L23 on the right and L12 at the right shoulder. The hip vector points L23 to L24, the spine-side vector L24 to L12, and the root frame is at L24 with forward shown toward the viewer. It changes no measured coordinates.

D-085 fixes the observed PDF overlaps using condensed-local generators and assets. Figure 2.4(a)'s z annotation is raised; its sensor origin, arrows and complete Unity-panel pixels are unchanged. Figure 3.7(b)'s lower legend moves below the plot, and two panel (a) text anchors move inside the right plot border. Data, vector calculations, plotted geometry and view angles are preserved. The entire final Figure 3.7 was inspected at full resolution and at 6.3-inch print width before rebuilding. Shared V7/V8 originals retain their hashes. Across these figure-only rebuilds all 32 Chapter 2 and 129 Chapter 3 OMML expressions and all chapter text runs are unchanged. ch2_ch3_layout_fix.json records the old/new asset hashes, source hashes, pixel bounds and exact annotation changes.

The final PDF review is recorded separately in visual_ch2_ch4.md and ch2_ch4_visual_manifest.json. Physical pages 27-71 cover the complete three chapters. The two revised pages were inspected again in the final PDF; the other 43 page rasters are byte-identical to the already inspected PDF. No clipping, empty math boxes or remaining figure-label overlap was found. Caption continuations for Figures 2.5 and 3.2 are complete and remain ordinary pagination observations.

After the final panel (a) label-anchor adjustment, delivered page 57 was
inspected again at 145 dpi. All other 44 Chapter 2-4 page rasters match
the preceding reviewed PDF (99367be8...) byte-for-byte at 90 dpi. The
original pre-D-085 hash and that intermediate PDF hash are retained in
the visual evidence; the delivered hash above identifies the final PDF.

Validation:
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/ch234_final_matplotlib /home/luo/anaconda3/bin/python writing/v8/condensed/audit_evidence/equation_iteration2_final/ch2_ch4_verify.py --docx writing/v8/Thesis_V8_Condensed.docx
Result: 80 checks, 80 PASS, zero FAIL.

PYTHONDONTWRITEBYTECODE=1 /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/check_style.py Chapter_2_Experimental_Setup Chapter_3_Kinematic_Modeling Chapter_4_Object_Tracking
Result: zero hits in all three chapters.

The final diagnostic writes only ch2_ch4-prefixed files in this sibling directory. The original equation_iteration2 baseline was not rerun or edited. The worker rebuilt only chapter parts and generated the scoped figures; assembly, PDF generation, global checks and Git remain parent-owned.

Therefore:
The supported Chapter 2-4 corrections and requested schematic are complete, traceable and numerically consistent with the pinned implementation/data. The final DOCX and inspected PDF include the corrected formulas and figures. Remaining native Word QA is a renderer check, not an unresolved Chapter 2-4 mathematical finding.

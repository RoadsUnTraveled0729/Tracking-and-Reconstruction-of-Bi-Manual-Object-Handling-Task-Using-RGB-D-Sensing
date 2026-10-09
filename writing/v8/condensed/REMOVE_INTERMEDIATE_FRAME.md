Later figure-only refinement, D-087/D-088: the frame removal and all
mathematics recorded below remain in effect. Figure 6.4 now restores the
prior four-frame conversion picture, ending at pre-gravity Unity, while
Section 6.4 still supplies the full Scene mapping. Figure 3.4 now uses a
real video frame. See FIGURE_REPLACEMENTS_2026-09-13.md. The original
removal-stage figure and verification descriptions below are preserved.

STATUS: COMPLETE (D-082; renewed correctness review follows under D-083)
GOAL: Remove the named intermediate frame while preserving the complete mapping.
KEY FINDING: The thesis uses final Scene coordinates; no replacement frame was introduced.
VERIFIED: DOCX and PDF text contain zero removed-frame terms. Chapter 5 invariants pass 79 checks; Chapter 6 passes 71; Chapter 7 passes 149. The separate pinned Chapter 7 verifier passes 1147, skips 21 and fails zero.
ASSUMPTIONS-UNRESOLVED: Existing spawn-axis, physical-mounting and evaluation limitations remain. Native Word typography requires manual QA.
DECISION: Use the full Scene mapping and preserve all input data and result statistics.
NEXT: D-083 completes the deferred equation review and final rebuilt delivery.

Reason:
The author clarified that Thesis_V8_Condensed(7).docx means the current assembled manuscript. The first pushed delivery e69dfa6 and its D-082 hashes are the source baseline. The explicit change recorded here removes Levelled as a named or conceptual coordinate frame. It is not renamed. The proper rotation G and the floor translation remain operations.

Evidence:
The complete Word-package occurrence inventory is audit_evidence/remove_intermediate_frame/baseline_occurrences.json (49 matching paragraphs/cells, including repeated contents/list entries). All changed Chapter 5 display texts are in ch5_document_changes.json. Detailed Chapter 6/7 derivations and changed sites are in ch6_report.md and ch7_changes.md. milestone_manifest.json pins the built DOCX/PDF before the renewed correctness corrections. Historical decision quotations, older drafts and frozen helper names remain explicitly classified in stale_repository_terms.txt; they are not part of the current thesis notation.

Therefore:
A reader encounters Camera, Camera', World, Unity where needed for the swap, and final Scene, together with genuinely local marker and joint frames. Gravity alignment does not create another frame.

Mapping and quantities
- S exchanges World axes 2/3 and reverses handedness; F reverses the camera y convention. Neither is a Craig proper rotation.
- pScene = G S pWorld + t_f, where t_f=(0,d,0) is recording-specific.
- R(Scene,MappedMarker) = G S R(World,Object) S. MappedMarker retains the marker-centre origin and Object axes x,z,y.
- T(Scene,Unity) = [G,t_f;0,1]. T(Scene,Camera') also includes the calibrated camera origin; its inverse subtracts floor placement before returning a wrist to Camera'.
- Wrist-minus-object displacement cancels the common t_f. G is proper orthogonal, so it preserves lengths and fitted-line distances. The implementation may compute those differences before the common floor translation without changing the geometry.

Every section/table/figure affected by frame removal
- Front matter: glossary distinguishes the Unity convention and final Scene. Contents, list entries and page numbers rebuild automatically.
- Section 2.2.1: final Scene introduced in the frame inventory; Unity's second axis follows the desk-marker normal and is not asserted to align with gravity. Table 2.2 gains the Scene row and full Scene/Unity transform. Inventory rows are kept intact after an actual split was observed.
- Figure 2.5(b) and caption: full Scene point mapping; axis labels Scene x/z. Floor translation has no x/z component, so every displayed point, direction glyph and trajectory remains at its original projected location. Generator regenerated. Figure 2.4(b) already depicts final floor-based Scene and requires no pixel change.
- Chapter 5 parameter overview and Section 5.3: Table 5.1, pose/offset definitions, object-chain and camera-chain displays, local fitting derivation and prose all use common Scene coordinates with explicit floor placement. Equations 5.1, 5.2 and 5.7 change their common frame; eight unnumbered displays change. Equations 5.3-5.6 and 5.8-5.12 remain identical during this refactor.
- Chapter 5 Section 5.6: absolute Scene object/wrist values and the full inverse translation are recomputed, with identical recovered Camera' wrist and model solve. Figures 5.1 and 5.3 regenerated; Figure 5.3 now draws absolute Scene position vectors from the floor origin and keeps its caption on the same page.
- Section 6.2 and Figure 6.4: clear five-frame diagram distinguishes solid frame boxes from dashed operation boxes, includes the calibrated translation, and ends at Scene. Camera/Camera' share one optical origin; World/Unity share the marker origin.
- Section 6.3: equation 6.5 itself is unchanged; its adjacent leading-factor expansion is now G R(Unity,Camera'). Floor placement affects positions, not orientations. The spawn/authored-axis assumption is preserved.
- Section 6.4: Scene is the only named post-Unity frame. Equation 6.6 is the full Scene/Unity homogeneous transform and direct World-to-Scene point mapping. No intermediate frame inventory or transform chain remains.
- Section 6.5 worked example: G is an operation, and the augmented Scene/Unity transform is printed in the scene-point calculation. The numerical G, pelvis, camera, object and floor values are unchanged. ch6_numbers.py uses matching labels.
- Section 7.2: fitted-line coordinate declaration and route-registration explanation; Figures 7.1/7.2 captions and generators use the final Scene point coordinates. Section 7.2.2 states rotation/translation invariance precisely.
- Section 7.3: measured landmarks already use final Scene, so no second floor translation is applied. Figure 7.3 caption now matches its existing Scene axis labels; Figure 7.4 image and caption are unchanged. Section 7.3.3 explains the common-frame spatial separation.
- Chapter 9 Table 9.1: gravity-referenced heights and tilts remain conditional on the wall-marker mounting assumption, without issuing a frame.
- Chapters 1, 3, 4, 8, 10 and the appendices: searched; no printed dependency on the removed frame. No frame-removal text edits needed. Later D-079/D-080 corrections are separately logged.

Numerical changes and invariance
Rail floor translation: (0,0.7162149392973363,0) m. Handover floor translation: (0,0.7093121647102482,0) m. All marker plot y values increase by the corresponding amount; x/z and plotted segment/scatter geometry are unchanged. Pinned coordinate-pair files keep their historical conventions and hashes, and the plotting conversion is explicit in the generator.

The Chapter 5 example object position becomes (-0.2245135269,0.7926310228,0.4457637618) m; predicted wrist becomes (-0.2122313195,0.8479321341,0.4819418431) m. The inverse translation is (0.0539180852,-0.9018703466,0.5133133731) m. At printed precision the object y is 0.79, wrist y is 0.85, and inverse translation is (0.05,-0.90,0.51). The recovered Camera' wrist remains (-0.1855927004,-0.0912133372,1.0441323384) m. The diagnostic checks 681 finite rail recovered wrists with maximum difference 4.44e-16 m.

Chapter 7 checks all 1,499,557 unique marker-sample pairs, all waypoint samples/means, six segment/error sets, all available fitted-line summaries, 2,146 spatial rows and the existing human/bare/synthetic pairs. Numerical results, all nine result tables, all six numbered equations and 18 pinned evidence/human-figure hashes are unchanged. Maximum difference among 1e-9-tolerance checks is 1.28e-13. This is floating-point arithmetic, not a measurement uncertainty claim.

Related author-requested illustrations (D-080)
New Section 7.3.4 and Figures 7.5/7.6 show three full video/Unity pairs per recording. Rail frames 95/505/700 and handover frames 700/950/1042 are qualitative examples. Full source images, capture distinctions and SHA256 values are recorded in ch7_visual_examples_sources.json and ch7_visual_examples_provenance.json. No metric sample or statistical result is selected or changed by these examples. Figure 3.4's separate schematic replacement is recorded in the final equation/illustration delivery log.

Rendered validation and remaining issues
Actual raster inspection covered the inventory, full Chapter 5 chains and inverse, equations 6.4/6.5/6.6, the clear Figure 6.4, the waypoint figures and the new video/Unity pages. The split Figure 5.3 caption and split inventory row were corrected and re-inspected. All affected images have reproducible generators; no unresolved image contradiction remains. No new coordinate ambiguity was left unresolved. Native Word upright OMML appearance remains a manual check; the missing approval date and physical assumptions are unchanged.

The final delivery report records the subsequent equation corrections, refreshed hashes, final rendering and second push. This milestone record remains preserved.

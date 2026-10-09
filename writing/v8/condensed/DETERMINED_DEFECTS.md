OBJECT FIGURE READABILITY, 2026-09-13, D-092
CORRECTED: Figures 7.1 and 7.2 now use the requested x-y upper-left, x-z
lower-left and larger 3D right arrangement. Their real-video strips remain.
CORRECTED DURING PAGE PROOF: Enlarge the plot height and move the W4 text
away from an axis tick. These are presentation changes; exact accepted-data,
waypoint, equation and result-table comparisons show no numerical changes.
Both complete final pages pass visual review. See CH7_OBJECT_3D_2026-09-13.md.
The prior determined mathematical corrections below remain unchanged.

CHAPTER 7 VISUAL RESTORATION, 2026-09-13, D-089 TO D-091
CORRECTED: Missing recorded-video context is restored around the object and
natural-occlusion evaluation. Figures 7.3/7.4 now use genuine saved Unity
trajectories, as requested. The old outer waypoint labels are omitted and
the dashed scene guide is explicitly schematic; model-wrist trails are not
identified as the validity-gated rendered-rig table samples.
CORRECTED DURING INTEGRATION: Frame 1200 depicts the settled far end rather
than the release event. Small video-strip titles are enlarged; the split
Figure 7.4 caption is kept together. These are presentation/evidence-scope
corrections. No result table, equation or experimental number changes.
See CH7_VISUAL_RESTORATION_2026-09-13.md and its source/visual evidence.
The earlier determined mathematical corrections below remain unchanged.

CURRENT FIGURE UPDATE, 2026-09-13, D-087/D-088
Figure 3.4's schematic did not meet the author's clarified request for real
video. It is replaced by the two-hand rail recording's frame 1400 with its
corresponding measured torso landmarks and derived axes. No measurement is
manually relocated. Section 3.2.2 and the caption follow the selected frame;
the frame-533 worked example, equations and results remain unchanged.
Figure 6.4 is also restored to the prior picture under D-088, following the
author's preference; its caption is scoped to the conversion it depicts.
See FIGURE_REPLACEMENTS_2026-09-13.md for the current artifacts and provenance.

CURRENT DISPOSITION ADDENDUM, 2026-09-13 (D-079 to D-084)

The original twelve-item history below is preserved. Its former coordinate
names describe the earlier corrections, not the current frame inventory.
REMOVE_INTERMEDIATE_FRAME.md records the later author-requested semantic
elimination, including every affected section, display, table and figure.
The supported defects from the renewed equation audit are corrected in the
current sources and rebuilt parts. No experimental result or frozen
implementation is changed. Final render evidence and delivery hashes are in
DELIVERY_2026-09-13.md and audit_evidence/equation_iteration2_final/.

New determined defects and dispositions
- C234-01: CORRECTED. Chapter 3 Section 3.5 closing point-transform checks
  omitted homogeneous components. Both sides now contain the fourth
  component where a 4 by 4 transform acts. Evidence: independent point
  composition/inverse diagnostics and dimensions. Mathematical; no numbers
  or numbered equation changes.
- C234-02: CORRECTED. The unit forearm vector before equation 3.24 lacked
  division by its norm. The full normalization is now printed. Evidence:
  frozen elbow solve and frame-533 metric vector. Mathematical; the input
  formula changes, while the calculated angles and equation 3.24 remain.
- C234-03: CORRECTED. The alternate T-pose paragraph claimed that merely
  swapping axes retained a proper rotation and gave the wrong Euler triple.
  That unnecessary false alternative is removed. The valid (0,180,0)
  reference construction remains. Mathematical; no experiment changes.
- C234-04: CORRECTED. The zero-twist explanation after equation 3.22 now
  refers to the actively un-swung forearm and its L12 y-z components.
  Evidence: shoulder.py and independent forward/inverse directions.
  Semantic/mathematical; equations 3.22/3.23 and numbers unchanged.
- C234-05: CORRECTED. Figure 3.5 caption now respects the mirrored left-arm
  reference directions. All reference frames share the root orientation;
  right arm lies along +x, left along -x. Caption only; image unchanged.
- C234-06: CORRECTED. Chapter 3 distinguishes thirteen stored angle fields
  from eleven independent angles, including the two redundant elbow-z
  fields. Evidence: serialized interface and pure solver. Interface and
  data unchanged; counting/explanation corrected.
- C234-07: CORRECTED. Sections 2.2.2 and 4.3, Table 2.3 and matching Chapter
  6 prose named the depth-fitted tabletop plane as the height reference.
  The implementation instead uses a horizontal model through a depth-derived
  tabletop point with calibrated gravity as normal. That model is now
  explicit. Existing heights remain identical. Evidential/reproducibility.
- C234-08: CORRECTED. Chapter 4's assurance that a height discrepancy lay
  within an unmeasured uncertainty bound is removed. The 6.3 cm model-relative
  and 7.3 cm physical/proxy comparison remains descriptive with its conditions.
  Evidential scope; no replacement uncertainty or causal attribution.
- C234-09 / CA-04: CORRECTED. Chapter 2 and Appendix F described a standard
  window MAD, but the implemented scale takes a rolling median of residuals
  from each sample's own rolling median. Both operations are now stated.
  Evidence: filter_landmarks.py and a counterexample distinguishing the
  definitions. Reproducibility; all gains, windows, masks and data unchanged.
- CH5-1: CORRECTED. Failure-mask exclusion is scoped to local updates and
  episode means. The earlier recording-wide fallback uses holding and
  plausibility gates rather than the later cleaned arm mask. Actual evaluated
  episodes have sufficient clean samples; no contamination claim is invented.
- CH5-2: CORRECTED. The forty-five-frame counter tracks consecutive missing
  distal landmarks, not every segment direction's age. The separate IK memory
  use without that counter check remains explicit. Implementation unchanged.
- CH5-3: CORRECTED. The episode/global fallback supplies values before local
  warm-up; a finite local estimate takes precedence after five clean samples.
  The fifteen-sample episode criterion is no longer stated as overriding it.
- CH5-4: CORRECTED. Equation 5.12 minimizes displacement from the point predicted
  by the remembered direction at the current shoulder, rather than literally
  from the last measured elbow. Formula unchanged.
- CH5-5: CORRECTED. The worked elbow y is 0.044979675 m and rounds to 0.04 m,
  not 0.05 m. This is a worked-example display correction; output CSVs and
  experimental results are unchanged.
- CH5 supporting scope: CORRECTED. The object-pose introduction is conditional
  on a measured pose, since detections can be absent. A unit-vector blend is
  no longer than its unit inputs; the 0.120674 m elbow-circle diameter is about
  twelve centimetres, rather than bounded by the rounded twelve-centimetre
  value. No formula or result changes.
- CA-01: CORRECTED. Appendix H Table H.1's both-arm dataset has eleven nonzero
  angle fields, not twelve. Six pinned 900-frame datasets retain their results.
- CA-02 / D-084: CORRECTED. Appendix D's nominal vertical field of view rounds
  to 43.1 degrees. Its 55.6 by 43.1 pair is now explicitly the centred-principal-
  point approximation. Principal-point-aware horizontal bounds round to 55.5;
  the earlier audit's contrary rounding statement is corrected in the final
  report while preserving that baseline report.
- CA-03: CORRECTED. Figure F.1 plots amplitude gain, including both Butterworth
  passes. The caption and prose now say so and explain that those gains
  multiply. The existing plot and filter results were already correct.
- Chapter 6 directional example: CORRECTED. The 6.9-degree discrepancy is
  reported while twist is held; the prose no longer claims a quantified causal
  cost without isolating other contributors. Numerical comparison unchanged.

Author-requested illustrations, completed
D-080 replaces the misleading photographic Figure 3.4 with a clear torso
schematic, replaces Figure 6.4 with a readable full Scene mapping, and adds
Figures 7.5/7.6 with paired video/Unity examples. No photo landmark is moved
onto invented anatomy; no new metric is inferred from the qualitative frames.
Every new or affected image has a generator and pinned/reproducible inputs.

No determined source defect remains open. Existing physical assumptions,
missing historical loop inputs and Word-only/institutional QA are retained
in UNRESOLVED_ITEMS.md. Actual final PDF inspection is recorded separately.

HISTORICAL COMPLETION DISPOSITIONS, PRESERVED

# Determined content defects: final completion disposition, 2026-09-12

This is the current disposition of the twelve items in the original delivery
note. That note and FRAME_INVENTORY.md preserve the historical findings. Later
evidence narrowed items 5, 7 and 8; their original descriptions must not be used
as instructions to change already correct mathematics or evaluation data.

Source corrections are recorded below. Final build, automated checks and
rendered-page evidence belong to DELIVERY_2026-09-12.md and
audit_evidence/final_completion. This list does not substitute for those checks.
No experimental result has been recalculated for these corrections.

## Initial twelve items

1. Table 5.1 object-pose provenance. CORRECTED, D-068.
   Wrong: the table attributed Levelled object coordinates directly to the
   Chapter 4 World pose. Evidence: v1/aruco/frames.py, eval/offset/carry.py
   LeveledWorld and eval/failure/recovery_core.py _leveled_to_solver_space.
   Change: Table 5.1 and Section 5.3 now print the origin chain as levelling
   times S times the World origin, and the orientation chain as levelling times
   (S times the World/Object rotation times S). The cleaned display-coordinate
   track is identified as the recovery input. Section 5.6 points to that chain.
   Classification: mathematical and reproducibility clarification. Numbers:
   worked-example coordinates and experimental results unchanged.

2. MappedMarker definition and conjugation. CORRECTED, D-068.
   Wrong: Chapter 5 used the frame without defining its construction.
   Evidence: frames.py and carry.py use the same two-sided swap.
   Change: Section 5.3 defines the marker-centre origin, Object axes x,z,y,
   left handedness and positive second-axis marker normal. Both changed bases
   appear in the conjugation; S remains an improper map, not a Craig rotation.
   Classification: semantic and mathematical. Numbers: unchanged.

3. Section 5.6 wrist conversion. CORRECTED, D-068 and D-071.
   Wrong: the two coordinate values referred to one wrist without a printed
   derivation connecting the Levelled and Person coordinates.
   Evidence: recovery_core.py and writing/v8/scripts/ch5_worked_example.py.
   Change: Section 5.3 derives the complete fixed mapping from calibration,
   inverse flip, swap and levelling. Section 5.6 applies its inverse using
   homogeneous point coordinates; the duplicate conversion is removed.
   Classification: mathematical presentation and reproducibility. Numbers:
   unchanged.

4. Chapter 6 one-sided and two-sided rotation rules. CORRECTED, D-070.
   Wrong: the text gave contradictory general rules with no selection rule.
   Evidence: frames.py conjugates the marker pose; IntegratedSceneReceiver.cs
   assigns the anchor times the segment and bone orientation chain.
   Change: Section 6.2 explains that changing reference and marker bases needs
   conjugation; changing only the reference basis needs left multiplication.
   Equation 6.1 now uses the explicit Unity/MappedMarker and World/Object
   relations. Classification: mathematical and semantic. Numbers: unchanged.

5. Equation 6.5 alleged missing levelling. RECONCILED AND CLARIFIED, D-070.
   The delivered equation already contained the correct Scene/Person leading
   factor after D-064. Adding a second levelling factor to it would be wrong.
   Evidence: IntegratedSceneReceiver.cs reads anchor.rotation after the scene
   parent has applied gravity levelling; the D-064 equation names Scene.
   Change: an adjacent equality expands Scene/Person into Scene/Levelled,
   Levelled/Unity and Unity/Person. The first rotation is identity; floor
   translation does not affect orientation. The spawn-axis assumption remains.
   Classification: semantic and reproducibility clarification. Numbers:
   unchanged. This refines the earlier delivery item, not D-064's classification.

6. F direction in equations 6.2 and 6.3. CORRECTED, D-070.
   Wrong: a bare F obscured that this path undoes Sensor-to-Person mapping.
   Evidence: equation 3.1 and the implementation's diagonal involution.
   Change: print F inverse and state that it equals F. The prose names linear
   basis maps rather than calling all individual factors proper rotations or
   ordinary Craig transforms. Classification: semantic. Numbers: unchanged.

7. Section 7.3 shared comparison frame. RECONCILED AND CLARIFIED, D-070.
   Wrong: the prose did not explain floor placement and could be read as using
   pre-placement coordinates for the measured landmarks.
   Evidence: evaluate_ch7_restructured.py already includes levelling and the
   recording-specific floor translation before comparing with rig logs.
   Change: Section 7.3 explicitly names Scene and distinguishes it from
   Levelled, which shares its basis but has a different origin. Equation 7.5,
   Figures 7.3/7.4 and the coordinate-pair results retain their existing values.
   Classification: semantic and reproducibility clarification. Numbers:
   unchanged; no erroneous metric recomputation was needed.

8. Figure 6.4 frame-count claim. RECONCILED AND CORRECTED, D-070.
   The actual figure contains four boxes, not eight. Its defect is the baked-in
   frame identification and the lack of a pre-levelling scope, not a need to
   draw every frame used in Chapter 6.
   Evidence: the original figure/generator and the receiver conversion path.
   Change: a condensed-only figure names the pre-levelling frames and inverse
   flip; the caption says four frames before gravity levelling. It does not
   introduce extra frames. Classification: semantic figure/caption correction.
   Numbers: no measurement changes.

9. Shared-parent claim in Chapter 6. CORRECTED, D-070.
   Wrong: the text claimed both output branches were local poses under one
   parent. Evidence: ArucoSceneReceiver.cs assigns local object poses;
   IntegratedSceneReceiver.cs keeps the rig outside that hierarchy and assigns
   global bone poses through its parented anchor.
   Change: Sections 6.2 and 6.4 describe those two implementation paths and the
   common levelling/floor mapping explicitly. Classification: factual and
   reproducibility. Numbers: unchanged.

10. Figure 4.1 desk-axis provenance. CORRECTED, D-070.
    Wrong: the caption called the drawn axes the frozen calibrated anchor.
    Evidence: make_ch4_experiment_fig.py draws the per-frame raw desk detection.
    Change: the caption distinguishes that estimate of World from the frozen
    anchor used by reconstruction. Classification: evidential. Numbers and
    figure pixels: unchanged.

11. Figure 2.5(b) object scale. CORRECTED IN GENERATOR, D-070.
    Wrong: the metric top view combined a scaled calibration with an unscaled
    object detection. Evidence: make_ch2_frames_craig_fig.py and the frame 533
    scaled object CSV. Change: only the metric panel uses the scaled object
    detection; the image overlay keeps its raw pose for reprojection. The
    condensed asset remains separate from the shared non-condensed figure.
    Classification: numerical figure geometry and reproducibility. Numbers:
    the cube glyph position changes; no thesis experiment statistic changes.

12. Chapter 3 numerical-inverse claim. CORRECTED, D-070.
    Wrong: an unrestricted claim that no matrix is ever numerically inverted
    also covered Chapter 5, which uses a numerical inverse.
    Evidence: carry.py and recovery_core.py. Change: Section 3.1 confines the
    transpose statement to its kinematic transformations. Classification:
    factual scope. Numbers: unchanged.

## Additional supported findings in the final pass

- Equation 3.3's prose named the wrong destination. It now says child frame B,
  matching the printed B/A relation (D-070). Mathematical direction correction;
  equation and numbers unchanged.
- Chapter 5's 35 cm grip bound was claimed to apply to any object and recording.
  It is now a task-specific design choice with unestablished generality
  (D-070). Evidential scope correction; bound unchanged.
- Chapter 6's displayed joint discrepancy had an unsupported additive causal
  decomposition. It now reports the measured discrepancy and names confounded
  contributors without apportioning them; capture proportions are stated as
  configuration facts (D-070, preserving D-043). Removed causal attribution,
  not recalculated error statistics.
- Chapter 9 treated clean proxy separation as a method-resolution threshold.
  It now distinguishes separation from unmeasured annotation/depth uncertainty,
  including the Table 9.1 row label. Its fitted-line discussion no longer lists
  tape precision as a source of PCA residual spread (D-070). Evidential
  corrections; reported values unchanged.
- Chapter 6's scene-point example applied a 4 by 4 transform to a printed
  three-component point. Homogeneous components are now explicit, and the
  pelvis paragraph names Scene. Appendix E's concrete trace expression now
  retains both frames of its Object-relative-to-Sensor rotation. Equation 6.1
  is split over display lines for long frame names (D-071). Mathematical,
  notation and formatting corrections; numbers unchanged.
- The deferred literature assembly stage had not occurred. D-069 performs
  first-appearance renumbering in the assembled thesis only, omits uncited
  entries there and corrects Craig's entry to the fourth edition. Frozen
  chapter citation identifiers stay intact. Internal-target check_refs output
  was never sufficient evidence of correct bibliography numbering.

## Historical items that are not new defects

- FRAME_INVENTORY S-6/S-11 predate D-064. Distal wrist and driven bone frames
  were explicitly issued there; Figure 3.5 no longer lacks a defined wrist
  frame. The operator classification of equation 3.22 stays intact.
- Chapter 7 remains the restructured evaluation settled by D-035 to D-053.
  Solver verification belongs in Appendix H, and the approximate 16 cm
  single-grip check remains Section 7.3.3. Deleted metrics are not restored.
- Table 3.1 headers use words with a caption correspondence. This is a valid
  table representation, not a mathematical defect.

Remaining evidence limitations and manual checks are in UNRESOLVED_ITEMS.md.


## Author-directed naming and final semantic/visual review

D-073: the current frame names are Camera and Camera', replacing only the
historical Sensor/Person names. Camera' shares the optical origin and flips
only y; it is not person-centred. All affected prose, frame scripts, origin
labels, tables, glossary and current figures were rebuilt consistently.
Craig position P and unrelated implementation variables remain unchanged.

D-075: the independent parent/local audit corrected Chapter 2's unaugmented
4 by 4 point multiplication, Chapter 3's mistaken generalization of every
arm parameter as an Euler triple, and the Figure 3.3 axis description.
Appendix D.3 now names its actual destination Camera. Figure 2.5's caption
clarifies pose-arrow direction versus point-coordinate conversion. Figure
6.4 identifies only the anchor rotation block as proper and names its
translation. See parent_local_review.md under the final completion evidence.

D-074/D-076: numerical table-grid widths now round consistently; hidden
summation limits are intentionally exempt from the empty-script check.
Rendered-page review fixed Table 5.1's clipped first symbol cell, split the
long unnumbered least-squares derivation, corrected Figure 5.1/5.3's old
World/Object frame claims in condensed-local copies, retained Figure 3.1's
caption with its image, separated Figure 7.4 plot rows, labelled the actual
Scene plot axes, and kept Appendix Table E.1's header intact. These are
mathematical presentation, semantic or formatting corrections only. No
experimental statistic changed.

The final visual records carry the reviewed PDF hash and page numbers. They
must be read with the current delivery addendum rather than the intermediate
184-page render in which the defects were first identified.


## Final disposition, 2026-09-13

All determined items above are corrected or reconciled against later evidence.
The final DOCX/PDF and final page-80 visual recheck pass the applicable checks;
no supported content correction or identified PDF defect is left pending.
Remaining assumptions, unavailable historical inputs and manual Word/institutional
QA are explicitly listed in UNRESOLVED_ITEMS.md. D-077 and the current delivery
addendum close this pass without commits or an unnecessary format migration.


Final raster follow-up, D-085 (current addendum to the history above): Figure 5.5
contained the same incorrect last-measured-elbow target as CH5-4 inside the
image. It is corrected in a condensed-local generator and asset. Figure
2.4(a) x/z label overlap and Figure 3.7(b) legend intersection are cleared
without changing geometry. Figure D.1 is kept with its caption. These
changes affect figure text/layout only and are rechecked in the final PDF.

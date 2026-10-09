STATUS: COMPLETE

GOAL:
Re-review Chapter 6 mathematics after frame removal and correct the
supported tabletop-model and held-twist descriptions.

KEY FINDING:
The current Scene equations reproduce the source calculations. The
tabletop model was misdescribed, and the forearm discrepancy did not by
itself isolate a held-twist cause. Both descriptions are corrected.

VERIFIED:
Fresh ch6_numeric.json: PASS 42, FAIL 0. The rebuilt Chapter 6 style check
has zero findings. All six numbered equations, seven unnumbered display
groups and nine inline OMML expressions were inspected. Every recorded
numeric value is retained.

ASSUMPTIONS/UNRESOLVED:
The exact authored bone-axis and spawn alignment required by equation 6.5
remains explicitly assumed. These calculations do not establish physical
sensor accuracy, wall mounting or anatomical ground truth.

DECISION:
Use the horizontal tabletop model through the depth-derived point with
normal set by calibrated gravity. Describe the 6.9-degree forearm
discrepancy while twist is held, without allocating its entire cause.

NEXT:
Parent final handoff. Final assembled mathematics and targeted rendered
pages pass; see visual_ch5_ch6.md for the final hashes and page coverage.

Reason:
calibrate_scene.py:146-150 selects gravity from the calibrated wall marker
with the depth normal as a sign check. Line 198 maps the depth-derived
tabletop point into World, and line 234 projects that point onto gravity.
The stored height therefore refers to the horizontal model through that
point. The independent frame-548 calculation gives a forearm discrepancy
of 6.928139231895637 degrees, which rounds to 6.9; this comparison alone
does not isolate a counterfactual pose with measured twist.

Evidence and dispositions:

6.1 PASS. S swaps the second and third position coordinates. The marker
orientation changes both reference and described bases by S R S. S is
orthogonal, self-inverse and improper; the resulting orientation matrix
is proper. Proper R carries both frame labels, while S remains an operation.

6.2 PASS. The inverse flip returns Camera' components to Camera. The full
calibrated Camera-to-World pose supplies its rotation and translated
origin. Premultiplication by S yields Unity coordinates. Both homogeneous
point operands are augmented, and the translation block is the camera
origin in Unity. The two improper factors produce a proper net rotation.

6.3 PASS. Inserting S S=I leaves the map unchanged. Regrouping yields
(S R S)(S F^-1), and the constant second factor is exactly Rx(-90 degrees).
MappedCamera labels cancel in the corresponding frame-chain product.
This factorization is also the parent-local anchor construction in the
receiver source.

6.4 PASS. The root, upper-arm and forearm orientation products have
matching intermediate frame labels. The shoulder frame inherits the root
orientation, so the L24/L14 rotation can be used in this orientation-only
chain without an origin translation. The wrist-frame origin does not
enter a rotation product. The source-function comparison of the removal
stage additionally covers right and left arm directions over 900 recorded
angle rows.

6.5 PASS WITH STATED ASSUMPTION. The leading Scene/Camera' orientation is
G times Unity/Camera', including gravity once and omitting floor
translation because this is an orientation. The middle chain ends in
Segment; the trailing rest orientation relates Bone to that Segment.
The receiver assigns global bone rotations through its global anchor
rotation. Interpreting the captured authored rest rotation this way
requires the unchanged spawn-axis assumption printed beside the equation.
The current evidence does not promote that assumption to a verified fact.

6.6 PASS. T(Scene,Unity) has a 3-by-3 G block, 3-by-1 t_f block and
homogeneous bottom row. Its direct World-point expression is G S P+t_f.
G is a proper shortest gravity alignment operation, t_f=(0,d,0)^T uses
the recording-specific floor offset, and the full inverse restores Unity
coordinates. The copied diagnostic now uses this full transform rather
than the superseded translation-only relation.

Unnumbered displays, all PASS:
- The Scene/Camera' leading-factor expansion has G once.
- The inverse calibration rotation and camera-origin vector reproduce.
- The anchor matrix and swapped camera-origin vector reproduce.
- Camera' and Unity pelvis coordinates reproduce at the printed precision.
- The G matrix, unnamed G P(Unity) value, full homogeneous Scene product
  and final pelvis coordinates reproduce. Both sides of the homogeneous
  product have four components.
- The inverse Camera/World rotation and world-origin vector reproduce.
- The object return point path reproduces and completes its round trip.

Inline OMML expressions identify already declared frame rotations,
transforms, points or the G/t_f operations. No inline expression introduces
a removed frame or an unlabelled frame-relative R/T.

The source-hashed diagnostic also verifies the printed gravity/floor
values, sample times, interpolation endpoints, object Euler fields,
camera/object point coordinates, right-arm joint coordinates and the
0.2/6.9-degree directional comparisons. Rounded operands are not treated
as the computational source; Chapter 6 explicitly computes before rounding.
The frame-548 branch-record example is not claimed to equal the merger's
interpolated output pose.

Therefore:
No additional numeric or matrix correction is supported. The current
descriptions match the implemented tabletop model and the demonstrated
forearm comparison while retaining the stated rig assumption.

Validation:
- ch6_check.py -> ch6_numeric.json: 42 PASS, 0 FAIL.
- ch6_math_inventory.json: 22 OMML expressions, including six numbered
  displays, seven unnumbered display groups and nine inline expressions.
- ch6_style.log: zero findings.
- ch6_docx.txt: rebuilt output used for the renewed review.
- Removal-stage evidence remains separate and unchanged.

Reproduction:
/home/luo/anaconda3/bin/python writing/v8/condensed/scripts/build_ch6.py
/home/luo/anaconda3/bin/python writing/v8/condensed/audit_evidence/equation_iteration2_final/ch6_check.py
/home/luo/anaconda3/bin/python writing/v8/condensed/scripts/check_style.py Chapter_6_System_Integration

Git:
No Git or assembly action was performed by this chapter worker.

Final assembly and visual addendum:
Fresh numerical replay remains 42 PASS / 0 FAIL. The final assembled DOCX
preserves all 22 Chapter 6 mathematical objects in order and structure,
including equation (6.6), the leading G factor beside (6.5) and every
worked homogeneous point. Physical PDF pages 100-112 were inspected;
Figure 6.4 and equations (6.1)-(6.6) are clear and complete. The corrected
final PDF renders all 13 of these pages byte-identically to the inspected
first pass. Table 6.2's visible continuation is recorded as nonblocking
pagination in visual_ch5_ch6.md. No additional correction is required.

Final artifact refresh after the Chapter 3 label adjustment:
The parent's new final DOCX (SHA256 d99335e683b9...) again preserves all
22 Chapter 6 mathematical objects. Fresh numerical replay remains
42 PASS / 0 FAIL. All 13 reviewed Chapter 6 page rasters are identical to
the accepted PDF review. ch5_ch6_ch3_label_equivalence.json and
visual_ch5_ch6.md pin the current and prior artifact hashes and this
equivalence. No Chapter 6 source changed in the refresh.

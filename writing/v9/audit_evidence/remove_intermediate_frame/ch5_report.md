STATUS: COMPLETE

GOAL:
Remove the intermediate frame from Chapter 5 and express its shared geometry
directly in Scene, including the recording-specific floor translation.

KEY FINDING:
The full Scene formulation preserves the hand-object offset and every
recovered Camera' wrist. The worked Scene positions and inverse translation
column change because they now include the drawn floor placement.

VERIFIED:
79 checks pass. The diagnostic covers all 899 finite rail object poses and
2058 finite loop object poses, both hands' finite offset observations, all
681 finite rail wrist predictions, and the rebuilt Chapter 5 DOCX.

ASSUMPTIONS/UNRESOLVED:
Final assembled DOCX/PDF layout remains an integration check. The earlier
equation_iteration2 correctness findings remain deferred by author order.

DECISION:
Apply D-082 with G as the proper gravity-alignment operator and
t_f = (0,d,0)^T as the Scene floor translation. Preserve the frozen pipeline
and all experimental data, masks, constants and output statistics.

NEXT:
Integrate the completed chapter with the other frame-removal work, inspect
the assembled document, and then resume the deferred correctness audit.

Reason:
The same t_f appears in the Scene wrist and marker positions. It cancels
from their difference in equation (5.2), so rotating that difference into
MappedMarker gives the same observations and offsets. The inverse complete
Scene/Camera' transform removes the added floor translation from equation
(5.7). Gravity alignment remains an operation within these complete maps;
there is no replacement intermediate frame.

Evidence:
- ch5_invariance.py is the reproducible diagnostic. ch5_invariance.json
  records its checks, full-precision matrices and points, finite sample
  counts, tolerances and SHA256 hashes of every relevant source/input.
- ch5_document_changes.json compares the current chapter with the chapter
  committed at e69dfa62eda80bc0ba5d0c4607a3a183a69f71fb. It lists every
  numbered equation and every changed unnumbered display.
- No removed frame name remains in printed Chapter 5 prose or OMML, or in
  the active parts of its builder and two figure generators. The builder's
  explicitly labelled historical changelog preserves the earlier naming.
- Both regenerated figure assets are embedded byte-for-byte in the chapter.
  Their final PNGs were visually inspected after regeneration. Figure 5.1
  names Scene floor placement and the Camera' conversion; Figure 5.3 draws
  both absolute positions from the same Scene origin on the drawn floor.

Therefore:
This is a complete change of the chapter's common reference coordinates,
with the required translation applied. It preserves the recovery geometry
and does not reinterpret existing experiment results.

Affected sites:

| Site | Change and numerical disposition |
| --- | --- |
| Equation (5.1) | Wrist and marker positions, and the rotation reference, are Scene. Both absolute positions include t_f. The MappedMarker offset is unchanged. |
| Equation (5.2) | Both positions are Scene; their common floor translation cancels. Offset observations are unchanged. |
| Equation (5.3) | OMML unchanged. The mean is unchanged because every contributing observation is unchanged. |
| Equation (5.4) | OMML unchanged. Re-running the recursive estimator on Scene observations preserves all finite rail estimates and the fallback mask. |
| Equations (5.5), (5.6) | OMML unchanged; these directions and points are already Camera'. |
| Equation (5.7) | The predicted wrist is Scene and includes floor placement; the full inverse maps it to the unchanged Camera' wrist. |
| Equations (5.8)-(5.12) | OMML unchanged; earlier correctness-audit findings are not applied in this pass. |
| Table 5.1 | Shared positions and rotation references become Scene. Object-position provenance now includes floor placement. G and t_f receive explicit entries; MappedMarker, Camera', lengths and gains retain their meanings. |
| Figure 5.1 and caption | The object input includes swap, gravity alignment and floor placement. Case B explicitly returns its Scene wrist to Camera' before the Chapter 3 solve. The caption identifies the Scene formulation. |
| Figure 5.3 and caption | Scene origin is on the drawn floor; grey absolute position vectors share that origin and the purple difference is the offset displacement. Equations and captions use Scene. Illustration coordinates and line layout are schematic, not new measurements. |
| Sections 5.1, 5.3, 5.4 and 5.6 prose | Full mapping provenance, MappedMarker handedness/origin, common-translation cancellation, actual pre-floor implementation equivalence, and the inverse translation-column meaning are explicit. |

All changed unnumbered displays, in document order:

1. Object origin/orientation chain: oScene = G S PWorld,ObjectORG + t_f;
   R(Scene,MappedMarker) = G(S R(World,Object) S).
2. Camera' orientation/origin chain: rotation G S R(World,Camera) F^-1;
   translation G S PWorld,CameraORG + t_f.
3. Complete Scene/Camera' homogeneous transform and its inverse: updated
   frame slots and the newly defined full translation column.
4. Three equivalent least-squares objectives: Scene labels; the residuals
   and objective values are unchanged by the common translation.
5. Worked input array: object y changes from 0.08 to 0.79 m. The shoulder,
   calibrated lengths and nine printed orientation entries are unchanged.
6. Worked rotated offset and predicted wrist: the offset displacement is
   unchanged; wrist y changes from 0.13 to 0.85 m.
7. Worked inverse matrix: rotation unchanged; the last column changes from
   (0.02,-0.19,0.55) to (0.05,-0.90,0.51) m at printed precision.
8. Homogeneous inverse wrist multiplication: the input is the full Scene
   point and the transform maps Scene to Camera'. The next display, the
   Camera' wrist (-0.19,-0.09,1.04) m, is unchanged.

These are unnumbered display indices 1, 2, 3, 4, 5, 7, 8 and 9 in
ch5_document_changes.json; display 6 is the unchanged local offset.

Worked numerical changes:

The source calibration gives origin_above_tabletop_m = -0.003785060702663684.
ArucoSceneReceiver.cs gives DeskThick = 0.03 m and LegH = 0.69 m. Their sum
gives d = 0.7162149392973363 m, printed as 71.62 cm under the existing
two-decimal prose rule. Calculations use the full value and full calibration
matrices before rounding. The Figure 5.3 image paragraph is kept with its
caption after integration exposed a page break between them.

| Quantity | Before floor placement | Scene formulation |
| --- | --- | --- |
| Object position, m | (-0.224513526929,0.076416083507,0.445763761839) | (-0.224513526929,0.792631022805,0.445763761839) |
| Wrist position, m | (-0.212231319522,0.131717194806,0.481941843063) | (-0.212231319522,0.847932134103,0.481941843063) |
| Inverse translation column, m | (0.023457900000,-0.187376800000,0.552492300000) | (0.053918085225,-0.901870346561,0.513313373113) |

The two absolute y coordinates gain d. Absolute x and z coordinates do
not move. The inverse column does not simply gain d: its change is
-R(Camera',Scene) t_f, which has three components because the two frames'
axes are only nearly parallel. The worked MappedMarker offset remains
(0.011270449141,-0.040850036232,0.052174424834) m, its rotated displacement
remains (0.012282207406,0.055301111298,0.036178081225) m, and the resulting
Camera' wrist remains (-0.185592700427,-0.091213337247,1.044132338424) m.

Validation:
- Chapter 5 rebuilt with the thesis Python; 113 builder items.
- 79/79 arithmetic, source-scope, equation-scope and embedded-asset checks.
- Rail: 900 rows; 899 finite object poses; 124 finite left and 795 finite
  right wrist/object pairs; 681 finite accepted right-wrist predictions.
- Loop: 2099 rows; 2058 finite object poses; 1790 finite left and 1976
  finite right wrist/object pairs. These are diagnostic availability counts,
  not newly selected experimental populations.
- Existing D-072 representation tolerances are retained: 1e-9 for arithmetic,
  2e-6 for comparison with six-decimal stored pose representations.
- No assembly, PDF export, commit or push was performed by this worker.

Reproduction, from the repository root:

    MPLCONFIGDIR=/tmp/ch5_scene_matplotlib /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/make_ch5_flow_final_fig.py
    MPLCONFIGDIR=/tmp/ch5_scene_matplotlib /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/make_ch5_offset_final_fig.py
    MPLCONFIGDIR=/tmp/ch5_scene_matplotlib /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/build_ch5.py
    MPLCONFIGDIR=/tmp/ch5_scene_matplotlib /home/luo/anaconda3/bin/python writing/v8/condensed/audit_evidence/remove_intermediate_frame/ch5_invariance.py

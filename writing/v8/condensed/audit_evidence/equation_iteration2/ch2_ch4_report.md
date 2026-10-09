STATUS: COMPLETE

GOAL:
Independently audit every mathematical relation and numerical worked calculation in current Chapters 2, 3 and 4.

KEY FINDING:
The numbered derivations and worked-example values reproduce, but the delivered document still has concrete dimensional and explanatory errors. The most important are two malformed homogeneous point products, a missing unit-vector normalization, and a tabletop reference described as the fitted depth plane when its normal actually comes from wall-derived gravity.

VERIFIED:
54 independent numerical/source-identity checks pass. All 28 numbered equations, 21 unnumbered display items, 48 paragraphs containing inline mathematics, and two tables containing mathematical frame relations were inventoried and matched to the assembled DOCX. Full-precision Chapter 3/4 examples and the complete 900-row cleaning mask reproduce. Supported defects below are separate from those computational pass checks.

ASSUMPTIONS-UNRESOLVED:
No anatomical ground truth for the hidden hips is available. The latest author instruction makes Figure 3.4 a pure schematic, removing the need to imply that its photographic samples are anatomical hip measurements. Physical wall mounting, tabletop geometry and sensor uncertainty are not independently measured by this audit. Near-singular implementation tolerances and generic invalid-input policy were read but are not newly validated as experimental guarantees.

DECISION:
Recommend narrow thesis corrections below, preserving frozen implementation and experimental values. The parent owns source changes, decision logging, assembly and Git operations.

NEXT:
Apply accepted corrections, replace Figure 3.4 with the user-requested schematic, rebuild, inspect the changed mathematical displays, and verify the revised artifacts.

Reason:
The core frame chains are correct and numerical replay agrees with the pinned inputs. Several nearby formulas/prose statements describe different dimensions, bases, sample counts or reference planes. Passing arithmetic alone cannot clear those statements.

Evidence:
- ch2_ch4_input_hashes.json pins the audited assembled DOCX/PDF, all three builders, implementation, source data and inspected figures.
- ch2_ch4_results.json records derivation tests, all worked intermediates, counterexamples, numeric rounding checks and a complete cleaning-mask comparison.
- ch2_ch4_math_inventory.json locates every numbered/unnumbered/inline builder expression and confirms its presence in the assembled document.
- ch2_ch4_assembled_extract.txt is a paragraph/table transcript of the actual delivered Chapters 2-4, with document-body indices. Escaped Unicode retains the underlying text without decorative characters.

Therefore:
Correct the demonstrated semantic defects without changing the successfully reproduced calculations.

Supported defects and exact narrow fixes:

C234-01. Two dimensionally invalid homogeneous point equalities.
Source: build_ch3.py, final mixed paragraph of Section 3.5, beginning 'Its rotation block is the composed swing and twist'; assembled BODY 573.
The elbow-origin equality has a three-component origin position on the left but T*[0,0,0,1]^T on the right, which has four components. The following wrist conversion applies inverse(T), a 4 by 4 matrix, to a three-component Camera' wrist point. The independent test raises NumPy's size 3 versus 4 matmul error on the printed second expression.
Fix: print [P(Camera',L14ORG);1] = T(Camera',L14)*[0,0,0,1]^T and [P(L14,16);1] = inverse(T(Camera',L14))*[P(Camera',16);1]. Both sides must have four components. The corrected products reproduce the measured elbow and local wrist values to floating-point precision; no number changes.

C234-02. A unit direction is equated to a dimensional segment vector.
Source: build_ch3.py Section 3.4.3, inline definition immediately before equation 3.24; assembled BODY 529.
The displayed g-hat equals R(Camera',L14)^T*(P16-P14), followed by prose 'normalized'. The right side has units of metres, whereas g-hat and the arcsine argument in 3.24 are dimensionless. On frame 533 its norm is 0.2017854184449412 m, not one. Frozen shoulder.py normalizes this expression before extracting elbow angles.
Fix: include division by norm(P16-P14) in the displayed equality. The resulting vector is (0.9408121411, approximately 0, 0.3389284808), matching the worked example and frozen implementation.

C234-03. The alternative reference-pose calculation is false.
Source: build_ch3.py Section 3.2.2, paragraph immediately after equation 3.12; assembled BODY 476.
The correct reference matrix is diag(-1,1,-1), decoding to (0,180,0). The next sentence says the 'same axes with the forward direction in the up column' remain proper and decode to (90,0,0). Simply swapping the up and forward columns has determinant -1. The proper signed permutation [right,forward,-up] has determinant +1 and decodes to (90,180,0). The claimed (90,0,0) matrix has first column (1,0,0), contradicting the retained right axis (-1,0,0).
Fix: remove this unnecessary alternative example, or explicitly state [right,forward,-up] and the corrected (90,180,0) result. The valid T-pose calibration remains unchanged.

C234-04. The zero-twist description drops the un-swing qualification.
Source: build_ch3.py paragraph after equation 3.22; assembled BODY 524.
The paragraph first defines raw forearm f in L12, then says its perpendicular component points along L12 +z at zero twist. For nonzero swing that is not true: it is the operated vector f-prime after un-swinging whose perpendicular direction lies along +z. The printed equation 3.22 and implementation correctly perform the un-swing.
Fix: say 'After un-swinging, the perpendicular direction of f-prime points along +z at zero twist', and describe (-sin(t_t),cos(t_t)) as its unit direction in the y-z plane. This retains the operator interpretation and frame L12.

C234-05. Figure 3.5 caption incorrectly applies the right-arm axis direction to the left arm.
Source: build_ch3.py Figure 3.5 caption; assembled BODY 478; inspected current ch3_fig_tpose_a.png.
The caption says the elbow x axes follow each upper arm and the wrist x axes follow each forearm. The image actually draws every x axis toward the subject's right, including L13 and L15. This agrees with the frozen mirror implementation: M*I*M=I at zero pose, so left +x remains (1,0,0) while the left segment extends (-1,0,0). More generally the mirrored reconstruction begins with -x. The figure itself is consistent; the caption is wrong on the left.
Fix: 'At zero pose all the frames share the root orientation. The right arm extends along +x and the left arm along -x.' This resolves the contradiction without redrawing a correct image.

C234-06. Thirteen reported numbers are described as a set containing eleven.
Source: build_ch3.py final left-arm paragraph of Section 3.5; assembled BODY 574.
Three root angles plus two swing, one twist and one flexion per arm gives 3+2*4=11. The actual interface has 13 fields because it retains the redundant e_z field for each elbow, as Section 3.4.3 and Chapter 6 already explain. The image/stream may correctly say thirteen; the final enumeration omits two fields.
Fix: explicitly include the two redundant elbow e_z fields, distinguishing the thirteen stored values from eleven independent angular quantities. Keep the current stream unchanged.

C234-07. The tabletop normal used for reported heights is misidentified.
Sources: build_ch2.py Section 2.2.2 and Table 2.3; build_ch4.py Section 4.3's 'fitted tabletop plane' statements; assembled BODY 389, 608, 610 and 616. Implementation: v1/aruco/calibrate_scene.py:143-150,198,234. Pinned scene_calibration_r6bc.json and aruco_raw_scaled.meta.json.
The stored tabletop point comes from the depth fit, but origin/camera/object heights are projections onto wall-derived gravity. The depth-fit normal and gravity differ by 6.2052001386 degrees. Current printed values reproduce as heights above the horizontal model through that tabletop point: origin -3.7850607 mm, camera 15.3916189 cm, object marker 6.3197832 cm. They are not distances to the original fitted plane. For example, the camera's signed distance to that fitted plane is 4.7758903 cm, and the origin's is -49.1388989 mm. These audit counterexamples are not proposed replacement experimental results.
Fix: state once in Section 2.2.2 that the tabletop used for heights is a horizontal model through the depth-derived tabletop point, with normal set by calibrated gravity. Update Table 2.3 and Chapter 4 to call these model-relative heights. Keep all current numeric values. Chapter 6 has analogous 'fitted tabletop plane' wording and should use the same definition.

C234-08. The height discrepancy is asserted to lie within an unmeasured uncertainty bound.
Source: build_ch4.py Section 4.3, sentence after 6.3 cm and 7.3 cm; assembled BODY 616.
The arithmetic reproduces: marker-model height 6.3197832 cm and tape rail height plus half cube edge 3.8+3.5=7.3 cm. No pinned uncertainty interval establishes that their difference is 'within what the coarse fitted plane resolves', and C234-07 further shows the prose names the wrong plane. Plane-normal disagreement alone does not establish a confidence bound on this comparison.
Fix: retain both quantities and, if needed, call their approximately 1.0 cm difference a discrepancy; delete the unsupported assurance or state that its sources were not separated. Do not replace it with a newly invented uncertainty number. The comparison additionally assumes that the marker centre is representative of the cube centre's height, appropriate only to the marker mounting and object orientation used here.

C234-09. The named Hampel scale differs from the implemented scale.
Source: build_ch2.py Section 2.5; assembled BODY 407. v1/mediapipe/filter_landmarks.py:54-61. Appendix F reviewer independently confirmed the same prose there.
The text names a window median absolute deviation. The code takes the rolling median of absolute residuals from each sample's own rolling median, then multiplies by 1.4826. Those operations differ from taking each sample's deviation from the current window's single median. Counterexample in results.facts.hampel_definition_counterexample: fifteen samples [0,.01,...,.14] m, seven-frame window centred at index 7. Conventional MAD is .02 m; the implemented rolling-residual median is 0 m.
Fix: describe the implementation-specific rolling scale exactly in Chapter 2 and Appendix F. Preserve the 7-frame window, 3 multiplier, 1.4826 scale and 2 cm floor, and preserve all filtered results. The Appendix reviewer owns the matching Appendix F recommendation.

Figure 3.4, latest author instruction:
The inspected photograph and generator show L23/L24 dots on the rail because they project the before-preparation frame-533 points, not because of an arbitrary label-position error. The generator uses px(P_cam) and (+10,-8) pixel label offsets; root origin is that same L24 point. The user subsequently clarified that Figure 3.4 is purely illustrative and requested a schematic. Replace it with a clear schematic labelled as such; no photographic failure caveat is needed in the thesis. Do not invent corrected measured hip positions. This supersedes the earlier audit suggestion to retain the photo with an explicit caveat.

Numbered-equation dispositions:
2.1 PASS. Orthogonal Procrustes/chordal projection, including determinant-negative SVD branch; singular values use the conventional descending order. Independently attains the Frobenius minimum and reproduces the first-ten-detections calibration.
3.1 PASS. F flips y only, keeps origin, is orthogonal/involutory with determinant -1. It is not a proper frame rotation.
3.2 PASS. Four-dimensional homogeneous point relation and 4 by 4 pose block. The printed zero block is explained by the explicit bottom row.
3.3 PASS. Parent A directions map to child B via transpose, with no translation for directions.
3.4 PASS. Inverse point subtraction and inverse homogeneous translation -R^T*p have correct order and dimensions.
3.5 PASS. Root origin at L24, shoulder shift in root coordinates with identity orientation, elbow shift in shoulder coordinates with solved shoulder orientation.
3.6 PASS. Three frame-chain factors compose in the correct source/destination order; frame 533 origin check passes when points are homogeneous.
3.7 PASS. Hip-line normalization and sign point toward the subject's right for distinct hips.
3.8 PASS. Spine-side vector has the correct endpoints and metric units.
3.9 PASS. Componentwise cross product order produces the intended forward direction in the declared Camera' convention for non-collinear inputs.
3.10 PASS. Second cross product closes a proper orthonormal numeric basis, without a further normalization for exact unit/perpendicular inputs.
3.11 PASS. Columns [right,up,forward] map root components into Camera'; determinant +1 between the two left-handed frames.
3.12 PASS. Root transform translation equals the L24 Camera' point. The adjacent alternative reference-pose explanation fails C234-03.
3.13 PASS. Shoulder origin subtracts L24 before rotation into root; zero forward offset follows the constructed plane.
3.14 PASS. Elbow origin subtracts shoulder and is rotated by root transpose because shoulder/root bases coincide.
3.15 PASS. Fixed parent-axis applied order z,x,y gives product Ry*Rx*Rz on columns.
3.16 PASS. All nine expanded entries agree with independent Rodrigues multiplication over 60 generic angle cases.
3.17 PASS. Regular extraction and both separately displayed exact gimbal-lock branches recompose correctly. Numerical branches near singularity are implementation tolerance conventions, not new exact-angle guarantees.
3.18 PASS. Right shoulder product Ry*Rz*Rx places twist innermost and matches the frozen joint convention.
3.19 PASS. First column is (cos(y)cos(z),sin(z),-sin(y)cos(z)); independent of twist.
3.20 PASS. Asin extracts elevation in the restricted interval for normalized input.
3.21 PASS. Atan2 extracts azimuth with the stated sign; exact vertical branch folds azimuth into twist.
3.22 PASS. Active un-swing operator order Rz(-z)*Ry(-y) is correct and keeps both vector expressions in L12. Adjacent raw-versus-operated prose fails C234-04.
3.23 PASS. Atan2(-f-prime_y,f-prime_z) extracts twist where the perpendicular component is observable; magnitude cancels.
3.24 PASS WITH REQUIRED INPUT-FORMULA FIX. Formula is correct for unit g; its preceding displayed definition needs C234-02. For observable exact geometry the solved twist makes e_z zero and the two measured segment directions reconstruct. At singular/near-collinear inputs, finite precision and fallback policy qualify any literal 'always zero' implementation claim.
4.1 PASS. Inverse anchor times Camera-object pose gives World-object pose; independently invariant under a common camera transform when calibration is updated. Moving the camera after freezing the anchor does not cancel, as the prose correctly states.
4.2 PASS. Inverse pose block has transposed rotation and -R^T*p translation.
4.3 PASS. Linear norm and relative angular bound use elapsed time from the last kept sample; Unity/MappedMarker labels match the implemented fields. Orthogonal swap preserves norms and conjugation preserves the relative rotation trace. Independent cleaning of all 900 rows keeps 899 and blanks only frame 786, exactly matching the pinned cleaned file.

Unnumbered/inline and numerical coverage:
- Chapter 2: homogeneous point relation, frame-chain table, S/F declarations, SVD mean relation, wall-frame chain and gravity-table semantics inspected. Marker-size linear scaling is dimensionally correct; 45/50=.9 is the pinned historical scale, not a change to current dimensions. Seven/five-frame filtering windows, 1.4826 scale, 2 cm floor, 3 Hz filter, 10/15 cm depth gates and .7/.3 memory weights were traced to implementation or the existing appendix delegation. These constants were not newly tuned or treated as measured accuracy guarantees.
- Chapter 3: all 16 unnumbered display items and 35 inline-math paragraphs were read, including the two singular root branches; Table 3.1's sixteen coordinate triples; root axes/matrix and all three transforms; local arm/forearm vectors, swing/twist/flexion on both arms; rounded-angle caveat; and both closing reconstruction checks. The full-precision frame 533 values round to every printed matrix/vector/angle. The only revised numeric statement recommended is the demonstrably wrong alternative (90,0,0) reference calculation, not an experimental result.
- Chapter 4: all five unnumbered display items and eight inline-math paragraphs were read. First-ten calibration mean has determinant .9999960728 and max projection change 1.43836e-6. Inverse camera range is 58.3873342 cm. Object Camera range is 105.5703550 cm, rounding to 106 cm. World object pose, gravity 32.0367654 degrees and the model-relative heights reproduce. At missing frame 786 the filtered position is 1.0202988 mm from the raw endpoint mean; candidate step is 3.2927143 mm and 1.1836101 degrees; frame 787 is 4.9476673 mm from 785. Counts are 899 detections/900 rows, 10 despikes, 11 bridges, zero held rows and zero detected-sample rejections. These conditions are retained.
- Captions/tables: frame identity, origin and handedness declarations in Tables 2.2/2.3, Table 3.1 numeric positions, Figures 3.3/3.4/3.5 axis meanings and Figure 4.1 per-frame versus frozen anchor were inspected. Figure 3.5 caption fails C234-05; Figure 3.4 follows the latest explicit schematic request.
- Glossary/frame meanings relevant to these chapters agree with the main Camera/Camera'/World/Object/Unity inventory: Camera' has the optical origin, not a person origin. Levelled and Scene remain Chapter 6 frames; no new frame is introduced by this audit.

Limits:
The source-dimension observations, counterexamples and uncertainty deficiencies are not encoded as failing assertions because they are deliberately recorded defects in the current thesis, not failures of the corrected independent mathematics. A 54/54 diagnostic result must not be reported as 'no equation defects'. The audit did not rerun inference, marker extraction, rendering, or raw experiments. It did not validate all possible invalid-input or near-singular runtime branches. No Git operations or thesis-source changes were performed.

Reproduce:
PYTHONDONTWRITEBYTECODE=1 /home/luo/anaconda3/bin/python writing/v8/condensed/audit_evidence/equation_iteration2/ch2_ch4_verify.py

The script writes only files prefixed ch2_ch4 under this audit directory. Rerunning after source corrections records the new inputs and changes the identity manifest; preserve this baseline evidence in Git before treating a later run as the same audit.

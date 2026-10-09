STATUS: PASS WITH PRESERVED ASSUMPTIONS
GOAL: Independently verify reference-frame versus local-frame semantics after D-073.
KEY FINDING: Proper R/T formulas preserve their actual source and destination frames. Three presentation defects were corrected under D-075; no experimental number changed.
VERIFIED: Chapters 2, 3, 5 and 6 formulas and implementation; existing frame verifier PASS 22 / FAIL 0; Chapter 3 pinned worked-example chain reproduced.
ASSUMPTIONS-UNRESOLVED: Equation 6.5 spawn/rest-axis identification remains an explicit assumption; optical model, rigid torso, rigid grip and fixed calibration limitations remain.
DECISION: Retain the mathematics and correct the determined dimensional and explanatory defects.
NEXT: Parent performs final assembly and visual QA.

Reason
A frame requires an orientation and an origin. Camera' is camera-origin, whereas the root L24 and arm frames originate at landmarks. Equal orientations do not authorize omitting translations in point transforms. Rotation-only mappings remain sufficient for displacement vectors.

Evidence and scope
Read current condensed build_ch2.py, build_ch3.py, build_ch5.py and build_ch6.py and the following implementation: v1/kinematics/root_frame.py, v1/kinematics/shoulder.py, v1/aruco/frames.py, eval/offset/carry.py, eval/failure/recovery_core.py, Unity/Assets/Scripts/IntegratedSceneReceiver.cs. The frozen implementation was not modified. Historical source terminology "Unity-space" in root_frame.py means Camera' here: unity_from_sensor multiplies by [1,-1,1] and performs no translation.
Notation in this audit: R(A,B) describes B in A and maps B components to A; T(A,B) additionally contains B's origin expressed in A. This audit shorthand does not replace printed Craig notation.

Chapter 2
- Section 2.2.1 generic T(A,B): direction B -> A verified. Determined defect: a stated 4 by 4 matrix previously multiplied an unaugmented point. Corrected both sides to homogeneous columns [P;1], matching equation 3.2.
- Table 2.2: T(Camera,World), T(Camera,Wall), T(Camera,Object) are marker poses read in the camera frame. T(World,Camera) is the inverse static anchor. T(World,Object)=T(World,Camera)T(Camera,Object) has the required cancelling Camera index. World/Object origins remain desk-marker/object-marker centres.
- Table 2.2 chain frames: T(Camera',L24), T(L24,L12/L11), T(L12/L11,L14/L13) match the ordered root/shoulder/elbow origins of Chapter 3. Only shoulder/root orientation is shared; their origins differ.
- Equation 2.1: SVD projection of the mean of R(A,B) samples produces another R(A,B). U and V are SVD factors, not frame labels. The determinant correction removes an improper result.
- F and S declarations: F maps Camera coordinates to Camera' and is self-inverse; S exchanges World axes 2 and 3 into Unity. Both have determinant -1 and remain distinct from proper frame rotations.
- Figure 2.5 caption now distinguishes pose arrows (reference origin -> described origin) from the opposite point-coordinate mapping direction. Labels were not reversed. Table aliases now match the semantic figure labels; Camera's C label remains only for Figure 2.4(a).

Chapter 3
- Equation 3.1: Camera' q = F Camera p. Same optical origin, y-only reflection, no person-centering. F remains a class-4 basis map.
- Equation 3.2: T(A,B)=[R(A,B), A P_BORG;0,1]; multiplying [B P;1] yields [A P;1]. Columns of R(A,B) are B axes in A.
- Equation 3.3: B v=R(B,A) A v with R(B,A)=R(A,B)^T. Correct for directions; adjacent prose explicitly excludes points with different origins.
- Equation 3.4: inverse point mapping first removes A P_BORG then applies R(A,B)^T. Inverse transform translation has the required minus sign and reference basis.
- Equation 3.5: T(Camera',L24), T(L24,L12), T(L12,L14) have rotation/translation blocks in their respective reference frames. The middle rotation is identity but its shoulder displacement is nonzero.
- Equation 3.6: all three homogeneous transforms compose with cancelling adjacent indices into T(Camera',L14).
- Equations 3.7-3.10: Camera' landmark differences build axes of L24 expressed in Camera'. Cross products use the implemented component convention, not an extra spatial transformation.
- Equations 3.11-3.12: axis columns give R(Camera',L24), and Camera' P24 supplies the root origin. Root remains person-attached and Camera' remains camera-attached.
- Equation 3.13: T(L24,L12) has identity rotation and R(Camera',L24)^T (Camera' P12 - Camera' P24) for translation. Identity rotation does not imply coincident origins.
- Equation 3.14: T(L12,L14) uses the solved R(L12,L14) and elbow offset R(Camera',L24)^T (Camera' P14 - Camera' P12). This root transpose is correct because L12 and L24 have equal orientations. The adjacent displacement-vector mapping uses the same fact without translating a vector.
- Equations 3.15-3.17: generic Euler operator decomposition and its numerical extraction, not a new unnamed frame. Corrected the introductory claim: only root orientation here is encoded as the Euler triple; arm angles are separately composed joint coordinates.
- Equation 3.18: R(L12,L14)=Ry(ty)Rz(tz)Rx(tt). Rightmost twist acts first in the zero configuration; the product maps elbow-frame components into shoulder-frame components. These factors are elementary operators and need no invented intermediate frames.
- Equation 3.19: applying R(L12,L14) to its local unit x gives the L14 x-axis expressed in L12. The twist leaves local x unchanged; the stated swing expression follows. The operator factors express the same component construction from zero-configuration x, not a translation.
- Equations 3.20-3.21: shoulder swing is extracted from the arm unit vector already expressed in L12; scalar x/y/z subscripts denote components, not new frame names.
- Equation 3.22: verified active un-swing product Rz(-tz)Ry(-ty), inverse of the swing product, acting on the forearm vector in L12. Input and operated output remain expressed in L12; the operator exception of D-057 is preserved.
- Equation 3.23: atan2 reads the operated vector's y/z components in L12. It does not silently read Camera' components.
- Equation 3.24 and its preceding chain: R(Camera',L14)=R(Camera',L24)R(L24,L12)R(L12,L14); its transpose maps the wrist-minus-elbow vector into L14. Flexion is extracted in L14, not Camera'.
- Left-side construction: shoulder.py:130-151 mirrors already-root-expressed segment vectors with diag(-1,1,1); reconstruction reverses y/z operator signs and retains twist. This improper mirror remains separate from Craig rotations.
- Worked example: writing/v7/scripts/ch3_numbers.py reproduces frame 533. The composed transform origin differs from the measured elbow by 5.59e-17 m. The wrist in the elbow frame is obtained by the inverse full chain. The accompanying report is preserved as parent_local_ch3_numbers.txt; its 77/900 full-solve count is a source-script condition, not a new thesis result.
- Figure 3.3 caption corrected: root and shoulder share orientation; only elbow x follows the upper arm. Previous "each x axis continuing down the arm" contradicted the defined root and shoulder axes.

Chapter 5
- Table 5.1 / Section 5.3 object chain: Levelled o=R(Levelled,Unity) S World P_ObjectORG. R(Levelled,MappedMarker)=R(Levelled,Unity)[S R(World,Object) S]. Conjugation changes both marker and reference bases; levelling changes only reference coordinates. MappedMarker retains the object-marker centre with swapped local axes.
- Section 5.3 wrist chain: R(Levelled,Camera')=R(Levelled,Unity)[S R(World,Camera) F^-1], with Levelled P_Camera'ORG=R(Levelled,Unity)S World P_CameraORG. Camera and Camera' share their origin, justifying that translation. The inverse T(Camera',Levelled) matches recovery_core._leveled_to_solver_space.
- Equations 5.1 and 5.7: marker-local wrist offset in MappedMarker is rotated into Levelled and added to the Levelled marker-origin position. They compare/add quantities only after expressing them in the same frame.
- Equation 5.2: subtract marker origin first in Levelled, then transpose R(Levelled,MappedMarker) to recover local offset. Translation is not omitted.
- Equations 5.3-5.4 and the intervening least-squares identity: all offsets are MappedMarker coordinates; orthonormality permits removing R from the norm. No averaging across incompatible reference frames.
- Equations 5.5-5.6: direction memory and the held-direction wrist estimate remain wholly in Camera'.
- Equations 5.8-5.12: shoulder/wrist positions, circle centre, direction memories and basis vectors are consistently Camera' quantities. The inverse-kinematics construction introduces no extra frame transform.
- Section 5.6: the printed inverse matrix is T(Camera',Levelled). Its final column is Levelled's desk origin expressed in Camera'. Both wrist vectors are augmented for the 4 by 4 multiplication. Distinct printed wrist coordinates before/after conversion remain intentional.
- Floor translation into Scene is not part of this Chapter 5 chain. The new chain preserves D-068's supported correction rather than conflating Levelled and Scene.

Chapter 6
- Equation 6.1 positions: Unity P=S World P with coincident desk-marker origins. Orientations: R(Unity,MappedMarker)=S R(World,Object) S, changing both reference and object axes. A single left multiplication by S would be improper and is not used.
- Equation 6.2: R(Unity,Camera')=S R(World,Camera) F^-1; Unity P_CameraORG=S World P_CameraORG. The homogeneous T(Unity,Camera') therefore maps the camera-origin pelvis point correctly. Two improper factors yield a proper net rotation between left-handed bases.
- Equation 6.3: insert S S=I, then factor into R(Unity,MappedCamera) and R(MappedCamera,Camera'). S F^-1 has the numerical Rx(-90 degrees) form. This is an operator-form identification of that constant; no improper factor is cancelled as a Craig rotation.
- Equation 6.4: R(Camera',L14)=R(Camera',L24)R(L24,L14), and forearm composition adds R(L14,L16). R(L24,L14) equals the Chapter 3 shoulder rotation numerically because L24 and L12 share orientation; no equivalence of their origins is claimed or needed for a rotation-only product.
- Equation 6.5: R(Scene,Bone)=R(Scene,Camera')R(Camera',Segment)R(Segment,Bone). Leading factor expands through Scene/Levelled/Unity/Camera' with adjacent indices cancelling. The floor shift does not alter orientation. Receiver writes anchor.rotation * root * shoulder * elbow * rest, matching this product order.
- Equation 6.5 limitation: identifying the captured rest matrix with R(Segment,Bone) depends on the stated authored/spawn-axis coincidence. It is not established from committed data and remains an assumption, not a verified claim.
- Equation 6.6: T(Scene,Levelled)=[I,(0,d,0);0,1]. Scene's origin is below Levelled's origin, so Levelled coordinates gain positive d when expressed in Scene. d remains recording-specific. The worked example augments both points correctly.
- Section 6.5 object return: Camera P=R(Camera,World) S Unity P + Camera P_WorldORG; static camera anchor direction is the inverse of the World-from-Camera map. Intermediate origins and coordinates are consistent.
- Chapter 6 opening now locates the pelvis, rather than all relative joint angles, in Camera'. The concluding held-twist explanation points to Section 5.5.

Validation
The existing verify_final_frames.py ran with its existing D-072 tolerances, PASS 22 / FAIL 0. See parent_local_numeric.json for exact numerical errors and source hashes. It checks handedness determinants, orthogonality, stored object-track conversions, inverse recovery mapping, absence of a Scene shift in the Levelled mapping, equation presence and retained OMML regressions. Numerical tolerance is not an experimental-accuracy threshold.
The four edited chapter parts rebuilt after figure routing and check_style returned zero hits for each. These checks do not prove Word-specific upright glyph rendering or the stated rig spawn assumption.

Therefore
The root, shoulder and elbow transformations are not reinterpreted as camera-centred frames. Camera' remains camera-origin; full homogeneous translations are used whenever landmark origins differ. No equation-number, experimental-number, filter, threshold, source/destination direction or implementation change was needed.

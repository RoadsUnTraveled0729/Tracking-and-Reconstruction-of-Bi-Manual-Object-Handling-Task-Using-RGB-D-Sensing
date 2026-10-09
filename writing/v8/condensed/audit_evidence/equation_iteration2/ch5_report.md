STATUS: COMPLETE
GOAL: Independently audit all Chapter 5 mathematics and worked calculations in the first pushed delivery.
KEY FINDING: Equations 5.1-5.12 and the corrected frame transformations are sound. One worked coordinate rounds incorrectly, and four surrounding statements overstate the implemented estimator or memory guarantees.
VERIFIED: Fresh diagnostics PASS 15 / FAIL 1. The failure is the displayed elbow y coordinate. All 114 mathematical objects in the chapter DOCX match the assembled DOCX in order. Coverage includes 12 numbered equations, 15 unnumbered display blocks, 70 inline insertions, Table 5.1 and all six captions.
ASSUMPTIONS/UNRESOLVED: Rigid grip, measured/prepared torso, effective calibrated lengths and the existing unclamped forearm fallback remain assumptions or limitations. No experimental result is changed by this audit. Native Word rendering is not checked.
DECISION: Recommend the narrow source corrections below; retain all numbered formulas and recorded data.
NEXT: Parent integrates supported wording/rounding corrections and rebuilds. This investigator changed only sibling ch5 evidence files.

Reason:
The corrected Camera'/World/Unity/Levelled/MappedMarker chain agrees with the frozen implementation, and independent sphere subtraction and least-squares normal equations reproduce its results. Several prose claims go beyond what those equations or state counters establish.

Evidence:
- ch5_diagnostic.py and ch5_diagnostic.json contain the independent derivations, complete ordered content inventory, worked values, synthetic counterexamples, pinned-report comparisons and SHA256 input manifest.
- ch5_docmath.json confirms equality of all 114 chapter and assembled-document mathematical objects, selecting the body heading rather than its front-matter contents entry.
- Fresh frame-560 replay matches the independent wrist and elbow construction. Its maximum stored-angle difference is 0.000046912580936 degrees, within half of the four-decimal CSV unit. Root and all three right-arm groups have constrained tag 2.
- Analytical tests use the existing D-072 1e-9 full-precision and 2e-6 serialized-rotation tolerances. The angle comparison uses 0.00005 degrees, derived directly from the stored CSV precision. These are diagnostic precision tolerances, not experimental accuracy claims.

Therefore:
Correct presentation and scope; do not change the reconstruction method or infer a new failure of the reported evaluation.

Actionable findings, ranked by semantic importance

CH5-1. Local/episode fitting excludes arm failures; the global fallback fit does not.
Source: writing/v8/condensed/scripts/build_ch5.py:415, final sentence, and the broad final sentence at line 296.
Current text: "No frame that a detector has flagged enters any fit." This is false for the recording-wide fallback read from the offset-fit report. fit_offset.py:80-94 applies holding_mask, but does not apply the cleaned arm failure mask. recovery_core.py:110-147 excludes those masks from hold_clean for the local/episode fit, then reads the pre-existing global fit.
Independent observations: the global rail right-hand hold set contains five cleaned-arm-mask frames, 675, 676, 677, 679 and 680. The global loop right-hand set contains six, 1775, 1806, 1807, 1808, 1811 and 1812. These are diagnostic counts, not new experiment results. Both left-hand overlap counts are zero. All actual rail/loop episode fits have at least fifteen clean samples and source "episode", so this check does not establish that a global fallback affected their reported recovery.
Narrow correction: "Flagged arm frames do not enter the local updates or episode means. The recording-wide fallback uses the earlier holding fit, which applies acquisition and forearm-plausibility checks rather than the later cleaned arm failure mask." At line 296, replace "No parameter is fitted on a flagged frame" with a statement scoped to these local updates and episode means, or point to Section 5.3 for the fallback qualification.
Do not claim that a synthetic masked target contaminated a scored output: that was not demonstrated.

CH5-2. The horizon counts missing child observations, rather than every segment memory's age.
Source: build_ch5.py:464, with implementation v1/kinematics/occlusion_ext.py:391-401 and the counter update immediately before the recovery stage.
Current text says a memory with no update for forty-five frames is unused, and a rebuild never outlives its measurement. _try_recover instead permits child k <= 45 and rejects k > 45. k is reset when that child is measured even when the proximal endpoint is absent and the segment direction cannot update. A wrist can remain measured while its elbow is absent; the forearm direction can therefore be older than its wrist counter. The diagnostic gives the helper an old direction and a child counter of one and confirms recovery. It also confirms that k=45 remains accepted and k=46 is rejected.
This is an implementation-contract counterexample, not a claim that such a sequence occurred in the reported recordings. The arm-mask policy normally removes both elbow and wrist together, in which case the ages agree. The existing separate exception for an unbounded IK swivel prior remains correct.
Narrow correction: "Direct memory rebuilds and the reach guard are allowed for at most forty-five consecutive frames on which the affected distal landmark is unmeasured. The counter tracks that landmark, rather than the age of every segment-direction update. The two-link solve uses the remembered upper-arm direction without that counter check."
If the parent chooses to limit the sentence to the simultaneous elbow/wrist-removal case, state that condition explicitly; do not change the frozen counter implementation.

CH5-3. Fifteen-sample episode/global selection only fills slots before local warm-up.
Source: build_ch5.py:415, and grip_state.py:84-156 / recovery_core.py:134-147.
Current text says an episode that never gathers fifteen clean frames falls back to the global offset. In the implementation the per-episode fallback array is overwritten wherever the time-local estimate is finite, beginning at the fifth clean observation. A ten-clean-frame synthetic episode uses the global fallback on indices 0-3 and its own initialized/recursive local estimate on indices 4-9.
Narrow correction: "Before the local estimate has accumulated five clean observations, the episode mean stands in. That fallback mean uses the recording-wide fit if the episode has fewer than fifteen clean observations; once the local estimate is available, it takes priority."
The existing retrospective/offline explanation is correct and must remain: the pre-warm-up episode mean may use later observations in that episode.

CH5-4. Equation 5.12 minimizes displacement from the current memory target, not literally the last measured elbow.
Source: build_ch5.py:566, sentence "The elbow therefore moves as little as possible from where it was last measured."
The preceding derivation correctly minimizes ||p_el - (p_sh + L1 u_hat)||. Its shoulder is current and u_hat is an exponentially averaged direction. Neither generally equals the last measured elbow position. A synthetic example in the diagnostic gives a 0.448306 m distance from the equation's choice to the old elbow, while another feasible point is 0.314505 m away. This disproves the literal old-position guarantee without challenging the formula.
Narrow correction: "The elbow therefore moves as little as possible from the position predicted by the remembered direction at the current shoulder."
The worked-example comparison to the actual last elbow remains correct: it is a measured diagnostic distance, not the minimized objective.

CH5-5. The displayed elbow y coordinate is incorrectly rounded from full precision.
Source: build_ch5.py:651, final unnumbered example result.
Fresh independent result: (-0.20103969640479846, 0.04497967507953052, 1.1965720107818492) m.
Current printed result: (-0.20, 0.05, 1.20).
Narrow correction at the existing two-decimal precision: (-0.20, 0.04, 1.20). All other printed two-decimal quantities pass their half-unit rounding checks. The existing worked script prints intermediate values to four decimals; this audit does not assert why the wrong final rounding was introduced.
Do not change the six-millimetre old-elbow comparison, the 31.7/20.5 cm lengths, the 0.7-degree direction comparison or -28.1-degree flexion. Those match full-precision reconstruction.

Optional precision wording, not a separate method defect

At line 453, the weighted sum of two unit vectors is "no longer than either", rather than strictly "shorter than either": equal inputs preserve length. With alpha=0.30 its norm is at least |1-2 alpha|=0.40, so normalization is well-defined even for opposite inputs.
At line 644, the calculated diameter is 0.1206742839 m. "About twelve centimetres" is more precise than the strict bound "at most twelve centimetres" when rounded quantities are being described. Both are low-impact wording refinements; neither affects the method.

Numbered equation dispositions

5.1, source line 367: PASS. A 3-vector point in Levelled equals the mapped-marker origin in Levelled plus R(Levelled,MappedMarker) times the wrist displacement in MappedMarker. Translation is necessary for the point; the offset is relative to the marker centre.
5.2, line 378: PASS. R_k transpose maps the Levelled displacement back to MappedMarker. Reference/represented frames and subtraction origin match. Numerical forward/inverse tests pass.
5.3, line 405: PASS for N>0 and equal unweighted observations. Stacking all rotation blocks gives A transpose A = N I, hence h = mean(h_k). The independent least-squares solve, zero gradient and equality of both objectives agree. The N=0 fit is undefined and is handled by the stated unavailable/fallback logic, not by this equation.
5.4, line 411: PASS. The convex update acts on vectors in the same MappedMarker basis, c=0.02. Temporal warm-up, fallback precedence and masking need CH5-1/CH5-3; the formula does not.
5.5, line 446: PASS. The normalized 0.70/0.30 blend stays in Camera' and has unit length; its denominator is bounded below by 0.40 for unit inputs. See optional strict-inequality wording above.
5.6, line 458: PASS. Current elbow plus L2 times a Camera' unit direction preserves the forearm length. Its allowable memory age is a policy issue covered by CH5-2.
5.7, line 471: PASS. The same geometry as 5.1 provides the Levelled wrist estimate. The frame conversion before IK is correct and includes inverse translation.
5.8, line 496: PASS. Both sphere distances have units of length and common Camera' coordinates. Simultaneous feasibility requires |L1-L2| <= r <= L1+L2 for positive links. Coincident equal-radius spheres have infinitely many geometric solutions; the implemented algorithm declines coincident endpoints because it needs their direction.
5.9, line 513: PASS for positive L1 and r. Direct sphere subtraction gives the same cosine. The derivative is -(1-(L1^2-L2^2)/r^2)/(2 L1 sqrt(1-cos(j)^2)); its magnitude diverges near outer tangency. The 98-percent guard is a chosen implementation parameter, not a derived numerical certainty.
5.10, line 525: PASS in the reachable domain. Independent subtraction gives axial displacement a=(L1^2-L2^2+r^2)/(2r), centre p_sh+a b_hat and radius sqrt(L1^2-a^2). Positive current calibrated upper arms exceed forearms in both reports, supporting the chapter's inner-clipping discussion. General L2>L1 may instead clip cosine at -1; the code does so, and the equation itself remains general.
5.11, line 536: PASS. Orthonormal n1/n2 perpendicular to b_hat span the circle. s is a freely parameterized swivel; no handedness-sensitive cross-product identity is asserted in the thesis equation.
5.12, line 549: PASS for nonzero projection and positive-radius circle. Maximizing the target/projection dot product gives the closest memory-target point. Parallel/no-memory fallback supplies down or depth; at zero radius the implementation returns the centre directly. The target is not necessarily the last measured elbow: CH5-4.

The 200 deterministic random reachable tests include varied positive unequal link lengths and endpoint orientations. Maximum errors and objective margins are in ch5_diagnostic.json. Explicit tests cover outer and inner tangency, beyond reach, over-folding with either link longer, parallel memory and coincident endpoints. These are mathematical diagnostics, not measurements of human performance.

Unnumbered and inline coverage

Source line 354, object origin/orientation chain: PASS. Origin o=G S P(World,ObjectORG); R(Levelled,MappedMarker)=G(S R(World,Object) S). S changes both right-handed bases to their left-handed mapped bases. G rotates only the reference basis. The marker origin is unchanged and no Scene floor translation enters.
Line 359, Camera' rotation/origin: PASS. R(Levelled,Camera')=G S R(World,Camera) F^-1 and P(Levelled,Camera'ORG)=G S P(World,CameraORG). F is self-inverse; Camera' has the raw optical origin.
Line 362, homogeneous mapping and inverse: PASS. The block is 4 by 4 with 3 by 3 rotation and 3 by 1 translation. Its inverse rotation and translation agree with recovery_core._leveled_to_solver_space. Proper block determinant is +1 for the supplied calibrations.
Line 398, three least-squares objectives: PASS. Substitution and orthogonality preserve the sum of squared residuals. Stating equality in prose while displaying three complete objectives avoids the earlier rendering issue without changing algebra.
Line 599, shoulder, calibrated lengths, object origin and rotation: PASS. Units are metres for points and explicitly centimetres for lengths. The matrix is the rounded proper rotation used by the pipeline, not an exactly orthogonal rounded matrix.
Line 609, offset and norm: PASS, norm 0.0672154676 m rounds to 0.07 m.
Line 611, rotated offset and Levelled wrist: PASS, both independently rounded from full precision. Adding already-rounded printed inputs can differ in the last printed digit; this alone is not a defect.
Line 619, inverse transform: PASS. Translation is the desk/Levelled origin in Camera', (0.0234579,-0.1873768,0.5524923) m before rounding. No person-centred origin or Scene floor shift is introduced.
Line 628, homogeneous wrist multiplication: PASS, both point columns have four components.
Line 629, Camera' wrist: PASS, (-0.1855927004,-0.0912133372,1.0441323384) m.
Line 633, shoulder-wrist difference, r and unit vector: PASS. r=0.5071242488 m and reach ratio=0.9715023923; 97 percent is below the 98-percent guard.
Line 637, centimetre cosine calculation: PASS. All three lengths use centimetres; the ratio is dimensionless. Full-precision j=10.9725093944 degrees rounds to 11.0 degrees.
Line 641, centre and radius: PASS, radius 0.0603371419 m. The diameter statement benefits from the optional approximate wording above.
Line 647, memory, dot product and projection: PASS. Dot=0.9840956963, projection norm=0.1776391298.
Line 651, recovered elbow: formula PASS; printed y rounding FAIL, CH5-5.

All seventy inline-math insertions are enumerated with their enclosing paragraph in the diagnostic inventory. They define or reuse the twelve equations' vectors, scalars, frames and intermediate quantities. No additional conflicting frame, dimensional or operator-order defect was found. Table 5.1 correctly identifies Camera', Levelled and MappedMarker, the converted object origin and orientation, unit directions, lengths, circle basis and swivel angle. Radius entries carry physical length rather than an origin-dependent vector interpretation. The six captions were checked against the defining equations: Figures 5.1/5.3 use the corrected Levelled/MappedMarker inputs, Figure 5.5 depicts the same sphere/circle/prior geometry, and the detector/holding captions introduce no competing mathematical definition.

Limits retained

- Out-of-reach and near-full-extension substitutions preserve only the upper-arm length in general; the thesis already discloses this correctly.
- The measured-only twist hold and unrestricted-age IK prior remain as implemented and already disclosed; no policy rewrite is recommended.
- The general levelling helper returns -I for exactly antiparallel inputs, which is improper. Both recording calibrations used here are in the non-antiparallel branch. This is not evidence of a current frame-chain defect; a general implementation guarantee would require separate boundary handling.
- Calibration lengths are effective model lengths, not established anatomical truth. The approximately rigid grip and old-offset lag remain limitations.
- This audit establishes mathematical content equality in DOCX, not native Word typography or a fresh visual inspection of every PDF page.

Reproduction

/home/luo/anaconda3/bin/python -B writing/v8/condensed/audit_evidence/equation_iteration2/ch5_diagnostic.py

Baseline expected result: PASS 15 / FAIL 1, where the single failure identifies the existing worked elbow rounding. The report intentionally does not call that baseline fully passing. The parent can rerun after correcting the printed value and updating the corresponding expected display in the diagnostic. No raw data, frozen code, thesis source or Git state was changed by this investigator.

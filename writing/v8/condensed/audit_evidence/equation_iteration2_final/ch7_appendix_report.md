STATUS: PASS

SUMMARY:
All six Chapter 7 equations and all four numbered Appendix equations remain
mathematically sound. The four earlier Appendix presentation defects are
corrected, and D-084 explicitly identifies the nominal field-of-view formula's
principal-point assumption. The current parts preserve all 18 mathematical
objects and all Chapter 7 result-table contents from e69dfa6.

BLOCKERS:
None in the current Chapter 7 and Appendix mathematical content.

IMPORTANT:
None unresolved. The field-of-view qualification reported during this final
review was incorporated by the parent under D-084 and independently checked.

MINOR:
None requiring another manuscript edit. The earlier audit's statement that
principal-point-aware and nominal FOV values round to the same pair was wrong;
the correction and full-precision boundary calculations are recorded below.

NEEDS VERIFICATION:
None within this Chapter 7 and Appendix scope. The final assembled PDF has
been checked against the reviewed parts and visually inspected; the evidence
is in visual_ch7_appendix.md. The first-pass Figure D.1 pagination finding
was resolved under D-085 and its three affected pages were reinspected.

TEST QUALITY:
The new diagnostic copies the earlier read-only calculation script into this
separate directory, preserving the original evidence. It imports no builder
or evaluator. It reconstructs distances directly from coordinate columns,
computes fresh covariance eigenvectors in final Scene coordinates, and replays
the existing six synthetic inputs through frozen pure solvers. Source hashes,
actual DOCX equation inventories and numeric residuals are retained. The
separate artifact check compares canonical OMML as well as visible table text,
avoiding the loss of math runs in python-docx cell.text.

RECOMMENDATION:
ACCEPT. The final assembled-page inspection and mathematical identity pass.

Resolved findings:

CA-01, Appendix H Table H.1: PASS. The Both arms row now says eleven nonzero
angles. The actual frame-742 truth row has 13 stored angle fields and 11
nonzero fields; elbow_z and l_elbow_z are zero. No frame has more than 11.
All six existing 900-frame synthetic datasets still decode with a maximum
wrapped angular residual of 1.1368683772161603e-13 degrees. No dataset,
solver, threshold or validation result changed.

CA-02, Appendix D.1: PASS with the explicit D-084 assumption. The nominal
centred-principal-point formula produces 55.55117970492011 by
43.14543806115066 degrees, so its rounded pair is 55.6 by 43.1. The former
43.2 is corrected. The current sentence begins, "Ignoring the small
principal-point offset", and identifies a nominal field of view.

The recorded principal point is (323.93756103515625, 248.0174102783203)
pixels and the focal lengths are (607.561279296875, 607.0150756835938)
pixels. Boundary-ray spans that include that offset are:
- Boundaries 0 to image size: 55.54962617632427 by 43.139527518603586 degrees.
- Pixel edges -0.5 to size minus 0.5: 55.54920659558418 by
  43.138767411716174 degrees.
Both round to 55.5 by 43.1, not the nominal pair's 55.6 by 43.1. The tiny
horizontal difference crosses a rounding boundary. This corrects the prior
equation_iteration2/ch7_appendix_report.md assertion that the exact spans
round to the same pair. That archived report is preserved. The final text
states the approximation explicitly and does not present the nominal pair
as a principal-point-aware angular extent.

CA-03, Appendix F Figure F.1 and attenuation prose: PASS. The caption now
describes amplitude gain, including both Butterworth passes. At the pinned
3 Hz cutoff, one-pass Butterworth amplitude is 0.7071067811865434 and the
forward/backward amplitude is 0.4999999999999941. The plotted Savitzky-Golay
amplitude is 0.8472657862552273, whose square would be 0.7178593125586885.
The actual plot uses the former. The adjacent prose states that the two
passes multiply their amplitude gains. The original figure remains valid.

CA-04, Appendix F robust scale: PASS. The final text describes each sample's
own seven-frame median, followed by a rolling median of absolute residuals
and the scale factor. This matches frozen filter_landmarks.py. A conventional
single-window MAD and the implementation's two rolling medians are distinct:
an interior steady ramp gives 2.0 for the former and 0.0 for the latter in
the seven-sample counterexample. All filtering parameters and outputs remain
unchanged; the correction describes the implemented statistic accurately.

Every numbered equation:

7.1: PASS. Reconstructed endpoint separation is a norm, absolute error is
the absolute difference from the positive physical reference, and relative
error is 100 times that error divided by the reference. Units are length,
length and percent. All six segment/error triples were recomputed after the
Scene floor translation and agree with the pinned values. Physical marker
centres and the author-supplied endpoint definitions are preserved.

7.2: PASS. The sample mean has length units and the 1/n covariance has
squared-length units. This normalization defines the geometric least-squares
objective; it is not an unbiased covariance-estimation claim. Translation
cancels from centred coordinates. Orthogonal basis changes carry covariance
by G C G^T and preserve its eigenvalues.

7.3: PASS. With unit u, I - u u^T is the orthogonal complement projector.
A line through the centroid in a largest-eigenvalue direction minimizes the
sum of squared perpendicular distances. The centre parameter's along-line
redundancy does not invalidate the minimization. The prose discloses the
case of a nonunique principal direction for degenerate samples.

7.4: PASS. The projector norm is distance to the fitted line. Independent
covariance-eigenvector fits to final Scene samples agree with the reported
rail-scatter summaries to at most 3.574918139293004e-14 cm. Tilt residuals
are at most 2.4424906541753444e-15 degrees. Scalar distance and scatter
remain rigid-motion invariants; coordinate components and tilt depend on
axis orientation. The current text makes that distinction.

7.5: PASS. Both reconstructed and measured operands explicitly carry Scene.
Their difference is a Scene vector and its norm is a length. The raw landmark
reference, rendered-rig capture subset and bare-model scopes remain separate.
Every stored human and bare-model distance and each grouped summary were
independently recomputed from coordinates. These positions already include
the floor placement and receive no additional translation.

7.6: PASS. Both masked and unmasked model points explicitly carry Camera'.
The norm compares the same joint at the same frame in the same coordinate
frame. The fixed orthogonal camera y flip preserves this distance. All
synthetic groups are recomputed from the same retained coordinate pairs and
remain equal to the pinned summaries. The synthetic error remains a deviation
from the unmasked model, not anatomical accuracy.

D.1: PASS. Pinhole projection uses dimensionless x/z and y/z with pixel-unit
intrinsics. Its domain requires nonzero optical depth, and the evaluated
examples use positive-depth samples. Recorded distortion coefficients are
zero, consistent with the stated simplified projection.

D.2: PASS. Deprojection multiplies optical depth by normalized pixel offsets
to produce metric x and y. It is the inverse of D.1 before display rounding.
Camera is the raw optical frame; Camera' retains its optical origin and flips
only y. The wrist example gives (-0.2005292615722035,
0.10474458980014248, 1.06) m; the depth example gives
(-0.2011359830601578, 0.15103551318281386, 0.986) m. They round to the
printed values and reproject to their input pixels at full precision.

E.1: PASS. Rodrigues' formula has the correct I, sin(theta)K and
(1-cos(theta))K^2 terms for a unit axis. K's signs give the declared cross
product. The generic expression is a rotation operator; the worked use
explicitly names Object relative to Camera. The worked inverse is evaluated
away from zero and pi and is not claimed to be globally nonsingular.

G.1: PASS. p_star = z_star p/p_z has length units and sets its optical-depth
component to z_star while retaining its camera ray. The prose restricts the
input to p_z greater than 5 cm. The y-only Camera-to-Camera' flip leaves z
unchanged. Whole-pair width reconstruction is separately described and is
correctly allowed to leave the original individual rays.

Unnumbered mathematics and numerical prose:
- Appendix A: 900 * 640 * 480 * (2 + 3) = 1,382,400,000 bytes, supporting
  the displayed 1.38 decimal GB payload. Acquisition counts and formats are
  recorded metadata, not newly inferred performance.
- Appendix C: its one equation array is the wrist deprojection worked
  example above. The truncated pixel and median depth inputs are distinct
  from an anatomical or ground-truth wrist position.
- Appendix D: its unnumbered array is the object-depth example above.
  The focal-length difference is 0.08990099137215696 percent, supporting
  less than 0.1 percent. Display-rounded point tuples are not expected to
  reproject exactly; the underlying full-precision points do.
- Appendix E: six unnumbered objects cover R, trace angle, axis, K, K^2
  and the recomposition. The full raw stored rotation yields the displayed
  177.7-degree angle and two-decimal matrices. Its recomposition residual
  is approximately 2.27e-7, while six-decimal scaled-CSV serialization
  amplifies near-pi extraction error to approximately 9.16e-4. The current
  thesis claims agreement to displayed rounding and does not restore the
  old 1e-5 claim. Table E.1 ranges remain Euclidean norms distinct from
  optical depth. Four corners supply eight image coordinates for six pose
  unknowns; the heuristic lobe policy remains disclosed as a heuristic.
- Appendix F: there is no OMML object. The corrected scale and amplitude
  definitions match the frozen source and plotted candidates. The centred
  median's ramp behavior, spike-rank effect, polynomial fit, and causal
  smoothing/lag descriptions remain supported.
- Appendix G: all preparation thresholds, normalized 70/30 direction
  updates, remembered depths, width reconstruction and the distinct
  45-frame missing-point horizon match the frozen update rules. The
  non-expiring depth memory and fallback's unchanged midpoint are disclosed.
- Appendix H: the only numeric correction is the authorized eleven-field
  count. All six frozen synthetic trajectories retain machine-precision
  closure. Measured-input and anatomical-accuracy limitations remain.
- Chapter 7: all nine result tables, their physical conditions and the
  normal-grip-only approximate 16 cm interpretation remain unchanged.
  Differences of 0.23 and 1.92 cm from that reference support "within about
  two centimetres". Neither transfer median is graded against it. The
  object detection and accepted-sample counts remain separate criteria.
  The new paired-image figures carry qualitative capture provenance and
  define no new evaluation sample or numerical validation.

Artifact identity and source integrity:
- ch7_appendix_artifact_checks.json proves six Chapter 7 and twelve Appendix
  canonical OMML objects match e69dfa6 byte-for-byte after canonicalization.
- All Chapter 7 tables remain identical. The Appendix tables differ in
  exactly one cell: the authorized Table H.1 change from twelve to eleven.
- ch7_appendix_results.json pins all read inputs, including current chapter
  DOCXs, builders, calibration, metadata and the frozen mathematical sources.
- ch7_appendix_existing_verifier.txt: 1,147 PASS, 21 SKIP, 0 FAIL. Its
  selection/provenance/physical-reference limitations remain limitations.
- No chapter, appendix, implementation, dataset, filter, capture or result
  was edited by this review. The parent applied the manuscript corrections.

Reproduction from the repository root:
/home/luo/anaconda3/bin/python writing/v8/condensed/audit_evidence/equation_iteration2_final/ch7_appendix_checks.py
/home/luo/anaconda3/bin/python writing/v8/condensed/audit_evidence/equation_iteration2_final/ch7_appendix_artifact_checks.py
/home/luo/anaconda3/bin/python writing/v8/condensed/scripts/verify_ch7_restructured.py

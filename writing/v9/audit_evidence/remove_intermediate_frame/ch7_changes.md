STATUS: COMPLETE

GOAL:
Express Chapter 7 directly in Scene and add the separately authorized paired
video/Unity illustrations while preserving the current evaluation.

KEY FINDING:
Final Scene marker coordinates require one recording-specific vertical
translation. All reported distances, errors, selections and line tilts remain
unchanged. Figures 7.5 and 7.6 add qualitative task views in new Section 7.3.4.

VERIFIED:
149 numerical checks pass. All 1,499,557 unique accepted-marker pairs retain
their distances. All nine result tables and six equation displays retain their
baseline contents. The existing independent evidence verifier reports 1,147
PASS, 21 SKIP and 0 FAIL. Original experimental evidence and human trajectory
figures remain byte-identical to e69dfa6.

ASSUMPTIONS/UNRESOLVED:
Existing physical-reference and capture limitations remain. The new images
have their own saved capture provenance; the handover screenshot run is not
identified with the later trajectory-table run. Assembled PDF inspection and
Git integration belong to the parent task.

DECISION:
Apply D-082 to coordinates and exposition, preserving pinned measurements.
Apply D-080 to illustrations only, retaining complete original sensor views.

NEXT:
Integrate Chapter 7, update automatic contents/figure lists, and inspect the
assembled PDF. No additional Chapter 7 implementation is pending.

Reason:
The stored marker unity_p* columns contain S times the World position. The
previous figures applied the proper gravity alignment G. Final Scene requires
pScene = G*pStored + (0,d,0). A common translation cancels from displacements,
and a proper rotation preserves Euclidean norms. It does not justify treating
absolute coordinates, axis components or orientations as frame independent.

Evidence:
- ch7_scene_invariance.json records the exact input hashes, transformations,
  before/after waypoint coordinates, segment lengths/errors and scatter fits.
- The receiver projection and existing human evaluator independently confirm
  d = 0.7162149392973363 m for r6b and 0.7093121647102482 m for r7. Each is the
  calibrated origin_above_tabletop_m plus 0.03 m desk thickness and 0.69 m leg
  height, imported from the existing receiver checker.
- Every plotted x and z component is preserved; y increases by
  71.62149392973363 cm for the rail recording and 70.93121647102482 cm for the
  handover recording. The complete eight waypoint positions are in the JSON.
- The sample populations remain 889 and 1,487. The unique-pair checks cover
  394,716 and 1,104,841 pairs respectively. Detected waypoint boundaries are
  unchanged at rail frames 92, 493, 617, 875 and handover frames 138, 430,
  534, 1083, with the original W1/W4 averaging intervals retained.
- All six segment lengths, absolute/relative errors, displacement components
  and dominant axes agree with object.json. All six available scatter fits
  preserve every perpendicular distance, median, p95, maximum, PCA spread,
  direction, vertical residual component and tilt. The largest residual
  among checks using the existing 1e-9 tolerance is 1.28e-13.
- All 2,146 spatial rows are retained, with 2,144 available coordinate pairs
  and two unavailable ones. The original hold gate uses a substituted model
  wrist on three rows. Replaying it before and after translation preserves
  every inclusion decision and all 813 included rows. All four medians retain
  their pinned values and restricted physical-reference interpretation.
- The 2,678 human pairs and both reference variants of 8,208 bare-model pairs
  already use Scene and receive no extra floor placement. All 810 synthetic
  pairs retain Camera' coordinates. Their per-row errors remain unchanged.
- The 16 files under ch7_restructured and both human trajectory PNGs match
  e69dfa6 byte-for-byte. All 15 DOCX tables, including six equation layout
  tables, retain their contents; all six canonical OMML displays also match.

Therefore:
The coordinate presentation is consistent with final Scene placement while
the accepted evaluation and all of its physical interpretations stay intact.

Changed printed sites:
1. Section 7.2: the sample coordinates in the line-fit method now name Scene.
2. Section 7.2: the physical-route statement names World and Scene, preserving
   the lack of physical route registration.
3. Figure 7.1 caption: identifies final Scene coordinates, Scene y in the
   elevation panel and the recording-specific floor translation.
4. Figure 7.2 caption: identifies Scene with that recording's translation and
   keeps the existing panel conventions.
5. Section 7.2.2, closing paragraph: states invariance of Euclidean distances
   and scalar line scatter under proper G and common translation; distinguishes
   absolute coordinates, orientation-dependent components and line tilt.
6. Section 7.3, mapping paragraph before equation 7.5: describes the calibrated
   camera mapping, gravity alignment and floor translation directly into Scene.
7. Figure 7.3 caption: matches the existing Scene x, Scene y and Scene z axis
   labels. The image and coordinates receive no new translation.
8. Section 7.3.3, reconstructed separation paragraph: expresses both positions
   in Scene and explains translation cancellation and norm preservation.
9. New Section 7.3.4 Visual Examples: adds paired sensor views with brief
   qualitative framing and a correct explanation of red status spheres.
10. New Figure 7.5 caption: rail acquisition/lift/slide from the saved
    7 September 2026 visualization capture.
11. New Figure 7.6 caption: right-hand slide/transfer/left-hand slide from the
    saved 9 September 2026 sensor capture, with a torso override and separate
    provenance from Table 7.4.

Figure 7.4, equations 7.1 through 7.6, Tables 7.1 through 7.9, Sections 7.1,
7.4.1 and 7.4.2 and the rest of Section 7.3 retain their accepted contents.
The old notes and pinned evidence retain historical naming as provenance.

Illustration provenance:
- ch7_visual_examples_sources.json pins all 12 selected 640 by 480 inputs and
  the capture/extraction/frame-naming sources. Rail frames are 95, 505 and
  700; handover frames are 700, 950 and 1042.
- Three handover Unity PNGs were copied byte-for-byte from the ignored
  eval/output/unity_check_r7/frames directory into
  figures/src/ch7_visual_examples. The other nine input PNGs already exist
  under figures/src. No original source is edited or deleted.
- make_ch7_visual_examples.py checks the source hashes and composes three
  rows by two columns without cropping, warping, recolouring, shifting, or
  adding overlays within the source images. Both complete figures were
  visually inspected. Row labels and source views are unobscured.
- EvalFrameDump names PNGs from the applied stream frame in LateUpdate. The
  manifest preserves this frame-index pairing basis without claiming a new
  timing or anatomical-accuracy validation.
- The handover sensor capture ran 00:48:56 to 00:50:32 on 9 September 2026
  with a 0.517 m torso override. The later trajectory-table editor log begins
  at 00:52:16 local. These runs are not identified as the same capture or
  assumed to share their complete configuration.
- The old handover capture check retains 7 PASS and 1 FAIL. The failed
  hypothesis concerns concentration of left-hand disagreement on torso-failure
  frames; the saved frame-identifier and applied-frame checks passed. The
  new figures are not presented as an experimental validation.
- ch7_visual_examples_provenance.json pins the current generator and output
  images. Selection is illustrative and changes no statistic or validity rule.

Validation:
- ch7_scene_invariance.py: PASS, 149 numeric comparisons plus selection,
  source-identity, equation-identity and table-identity assertions.
- verify_ch7_restructured.py: 1,147 PASS, 21 SKIP, 0 FAIL. The 21 documented
  limits remain; this change makes no stronger physical-reference claim.
- check_style.py Chapter_7_Evaluation: zero hits.
- The current Chapter 7 DOCX has six images and Figures 7.1 through 7.6 in
  order. Section 7.3.4 follows 7.3.3 and precedes 7.4.
- Word count: 3,568 prose, 444 caption, 52 heading and 100 table words under
  the existing counting script. Its zero equation count reflects equation
  placement in layout tables; six OMML displays are independently verified.

Reproduction from the repository root:
MPLCONFIGDIR=/tmp/ch7_restructured_mpl XDG_CACHE_HOME=/tmp/ch7_restructured_cache /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/make_ch7_object_waypoint_figures.py
MPLCONFIGDIR=/tmp/ch7_restructured_mpl XDG_CACHE_HOME=/tmp/ch7_restructured_cache /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/make_ch7_visual_examples.py
/home/luo/anaconda3/bin/python writing/v8/condensed/scripts/build_ch7.py
MPLCONFIGDIR=/tmp/ch7_restructured_mpl XDG_CACHE_HOME=/tmp/ch7_restructured_cache /home/luo/anaconda3/bin/python writing/v8/condensed/audit_evidence/remove_intermediate_frame/ch7_scene_invariance.py
/home/luo/anaconda3/bin/python writing/v8/condensed/scripts/verify_ch7_restructured.py
/home/luo/anaconda3/bin/python writing/v8/condensed/scripts/check_style.py Chapter_7_Evaluation

Git:
No assembly, PDF generation, commit or push was performed by this delegated
writer. The parent integration task owns final rendering and delivery.

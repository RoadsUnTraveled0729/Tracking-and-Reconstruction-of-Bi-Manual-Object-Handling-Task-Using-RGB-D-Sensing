# Chapter 7 reconstruction evidence

Status: supported comparisons computed and independently reviewed.
The object endpoint accuracy that D-030 blocked is now computed under
D-035 and D-036, which supply the physical reference and the phase
boundary waypoint definitions. These files support the replacement
standalone Chapter_7_Evaluation.docx.

The paired coordinates are the reproducible numerical record:

- human_pairs.csv: raw accepted measured 3D landmarks transformed to
  Unity world coordinates, actual captured rig joints, frame, output
  root tag, and Euclidean error in cm. human.json records selection,
  transforms, capture coverage, synchronization checks and statistics.
- synthetic_selection.json: complete eligible candidate list and the
  motion-based selections, written before masked methods are scored.
- synthetic_pairs.csv: reconstructed model joints for each method and
  valid unmasked reference joints. synthetic.json records all results.
- natural.json: explicitly named wrist-proxy reference and pinned
  summary values from eval/reports/r5_recovery_labeled.json. Clean
  baseline values use accepted filtered wrist measurements, unlike
  the raw measured-landmark reference of human_pairs.csv.
- object.json: the Section 7.2 object result. It records the detection
  rule and its parameters, the identified W1 to W4 frames or intervals,
  the per waypoint phase confirmation, excluded sample counts, the
  waypoint positions with their sample counts and spreads, the three
  segment lengths with absolute and relative error, the rigid invariance
  check, the detector selection sensitivity, the fitted line scatter and
  the caveats the prose must disclose. object_pairs.csv holds every
  accepted sample behind each waypoint position: the W1 opening interval,
  the two single transition samples W2 and W3, and the W4 closing
  interval, in the gravity-levelled desk world in metres. It does not
  hold the samples between waypoints, so the detector, the sensitivity
  block and the fitted line scatter cannot be rebuilt from it.
- bare_model.json: the bare kinematic-model result of D-039 to D-043. It
  separates the two wrist quantities the thesis must keep apart, records
  the forward kinematics, the anchor, the frame alignment and the
  selection it reuses from evaluate_ch7_restructured.py, and for each
  recording holds the calibrated segment lengths, the avatar segment
  lengths actually used by the capture, the display filter reproduction,
  and per joint the errors at both scopes: section_7_3_frame_set, the
  accepted frames of the Unity capture subset, and
  recording_wide_accepted, the accepted frames of the whole recording.
  Each scope carries n, the statistics against both the raw and the
  filtered measured landmark, the frame list, the root, swing, twist and
  elbow output tag counts, the twist measured and twist held split, and
  the rendered rig values of human.json on the identical frames. The
  chapter_9_previous_values block preserves the superseded whole
  recording filtered-reference values and states their old definition; it
  is kept for traceability and is not reused. bare_model_pairs.csv holds
  one row per scored frame per scope: the model wrist or elbow, the raw
  measured landmark, the filtered measured landmark, both error columns,
  and the root and twist output tags. A frame accepted at both scopes
  appears twice, once per scope.
- loop_detection.json: object-marker detection coverage on the loop
  recording, pinned for Section 7.4.2 by the separate harness
  scripts/evaluate_ch7_loop_detection.py. It holds frame counts rather
  than coordinate pairs: the detected and accepted coverage with their
  missing frames and runs, the despiked and bridged rows, the two-hand
  grip intervals and the desk handover span the missing frames fall in,
  and the object-marker status of the labelled frames of natural.json.
- spatial_check.json: the Section 7.3.3 human-object spatial check of D-038,
  pinned by scripts/evaluate_ch7_spatial_check.py. It records the four
  reconstructed wrist to marker-centre medians with their n, the definition
  of every endpoint with the file it comes from, the traced chain that
  establishes the object point, the inclusion rule with its hold radius, the
  delimitation of the three intervals, which medians D-038 grades against the
  author's approximate 16 cm physical reference and which it does not, the
  agreement with the pinned eval/reports/r7_handover.json, a diagnostic that
  reruns the at-the-cube test with the alternative cube-centre convention,
  and its own source SHA256 values. spatial_check_pairs.csv holds one row per
  frame of the rail span for each hand, included and excluded alike: the
  model wrist, the marker centre, the measured wrist and the cube centre, the
  carried and detected states, the extractor source code and the substitution
  flag, the hold distance, the inclusion status with its reason, and the
  wrist to marker distance in centimetres. Because the excluded rows are
  there too, the inclusion rule is rebuildable from the file rather than
  asserted by it. Nothing is excluded for the size of a distance.
- provenance.json and object_provenance.json: input/source SHA256 values
  and numerical-library versions. bare_model.json, loop_detection.json and
  spatial_check.json carry the same fields and their own source lists. Local
  gitignored inputs are not copied or rewritten.

Selection is specified in scripts/evaluate_ch7_restructured.py, in
scripts/evaluate_ch7_object.py for the object result, in
scripts/evaluate_ch7_spatial_check.py for the Section 7.3.3 check, and in
DECISIONS.md D-031/D-032/D-035/D-036/D-038. scripts/evaluate_ch7_bare_model.py
reuses that same gate rather than re-implementing it, and asserts that
the frames it scores on the capture subset are exactly the frames
human.json reports. Filter source and flag must both
pass; raw and filtered relevant arm and torso coordinates must be
finite with positive sensor depth. Both instantaneous detector and event
mask acceptance are required. Existing person-present span and detector
warmup apply. No rejection threshold uses the size of reconstruction error.

Human scope: captured subsets, not complete recordings. All selected
single-hand frames have constrained-root output. Handover subsets also
include constrained roots. Rendered-rig errors include display filtering
and rig mapping; they are not bare-model closure errors or anatomical
accuracy. Receiver capture order is nonchronological, so figures use
unconnected samples and cannot imply continuity through absent frames.

Synthetic scope: right elbow/wrist removal after offline filtering,
with retained measured shoulder and torso; fixed existing calibration.
Root and all evaluated arm groups are measured in the unmasked
reference. Separate fresh full replays start each method. All methods
match reference immediately before each mask. The mature time-local
grip offset stays constant through each mask without masked-sample
updates. Source files retain their original algorithms unchanged.
The windows contrast observed motion and are not independent trials.

Natural scope: left bracelet and right watch; identical points for all
three model methods on each side. Clean proxy separation is not an
anatomical calibration or a scalar correction. Entirely hidden proxies
were excluded. Repeated annotation/depth uncertainty is unmeasured.

Bare model scope: the reference is the accepted raw measured landmark
of D-040, and the filtered variant is recorded beside it so the cost of
that convention is measured rather than assumed. The two scopes answer
different questions and are never interchangeable: the capture subset is
frame matched to the rendered rig table and is used only for the
downstream contrast, while the recording wide accepted frames are the
representative bare model performance. The capture subset is not
representative of the accepted frame population, especially on the left
arm, where held twist frames are 55 per cent of the subset against 41
per cent recording wide. Constrained twist frames belong to neither side
of the twist split, so the measured and held counts need not add to n.
On the single-hand rail recording the right forearm twist is held and
the root is constrained on every accepted frame, so that value is not an
isolated kinematic model closure metric and D-042 keeps it out of the
Section 7.3.1 accuracy table. Both captures ran with the loop
recording's arm segment lengths rather than each recording's calibrated
lengths, and the rail capture kept the receiver's default torso length;
the difference is recorded here but no fraction of the rendered rig
discrepancy is attributed to it.

Object scope: the physical reference is the author tape measurement of
25.5, 3.5 and 37.5 cm between ArUco marker centre positions, at 1 mm
resolution, applying to both recordings. Waypoint frames come only from
each recording own marker centre motion; the stored route corners of
eval/reports/*_waypoints.json and the fitted rail line are never used to
place a waypoint. W2 and W3 are single transition samples and carry the
instantaneous depth error of one sample. Segment lengths are invariant
under the levelling rotation, verified in object.json; the scatter
components, the line tilt and the axis dominance used for the phase
checks are not. The fitted line distances are a within-recording
comparison and never a physical accuracy. Every reported length carries
the detector selection band recorded in the caveats block.

Spatial check scope: the reported endpoint is the ArUco marker centre, the
pose translation of the object marker. The pose solve places its four object
points symmetrically about the origin, so that translation is the centre of
the printed black square, and the marker origin of the Section 7.3.3 prose
and the marker centre of Section 7.2 and D-036 are the same physical point.
The 45 mm size enters as a scalar rescale of the translation, which changes
the distance to that centre and not which point it is. The wrist is the bare
kinematic-model wrist of D-039: the solved recovery angles anchored at the
same-frame filtered measured shoulder with the calibrated segment lengths,
not the rendered rig wrist of Table 7.4 and not a measured wrist. The cube
centre appears only in the at-the-cube gate and never in a reported distance.
The medians are reconstructed geometry over the frames on which that hand is
at the cube; the two hand-alone intervals are the only ones D-038 compares
with the author's approximate 16 cm physical reference, and the two transfer
values are descriptive because the grip geometry changes while both hands
hold the cube. The left-hand-alone interval contributes 58 frames, because
the cube stops being carried once it is parked at the far end.

Reproduce from the repository root using existing local inputs:

    MPLCONFIGDIR=/tmp/ch7_restructured_mpl XDG_CACHE_HOME=/tmp/ch7_restructured_cache /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/evaluate_ch7_restructured.py
    MPLCONFIGDIR=/tmp/ch7_restructured_mpl XDG_CACHE_HOME=/tmp/ch7_restructured_cache /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/make_ch7_valid_joint_figures.py
    MPLCONFIGDIR=/tmp/ch7_restructured_mpl XDG_CACHE_HOME=/tmp/ch7_restructured_cache /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/evaluate_ch7_object.py
    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/evaluate_ch7_bare_model.py
    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/evaluate_ch7_spatial_check.py
    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/build_ch7.py

evaluate_ch7_bare_model.py reads human.json, so it runs after
evaluate_ch7_restructured.py. build_ch7.py reads these JSON files
directly and formats them, so the chapter cannot drift from the evidence
and anything verified here is what the chapter prints.

Standalone verification from committed coordinate pairs:

    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/verify_ch7_restructured.py

That script needs no arguments, no recordings and no third-party
package. It reads the *_pairs.csv and *.json files here, recomputes
every published statistic they carry, and exits non-zero if anything
disagrees. It writes nothing. It is independent of the three evaluation
harnesses above: it imports none of them, uses neither numpy nor pandas,
and implements the
distance, the median, the 95th percentile and the maximum itself, so
the percentile definition Section 7.1 states, linear interpolation
between ordered observations, is under test rather than assumed. Every
distance is recomputed from the stored coordinate columns; the stored
per-row error column is checked against that recomputation and is never
trusted in its place. The tolerance is 1e-9 cm on re-derived arithmetic,
a numerical-noise allowance stated in the output; where a file stores
values already rounded to two decimals the line says so and uses a 0.01
cm display allowance instead.

It covers the human rendered-rig errors, the bare model errors at both
scopes, the synthetic per window per method errors, the object waypoint
positions, segment lengths and errors, the natural summary, and the four
Section 7.3.3 wrist to marker medians. Beyond
the statistics it checks frame sets against the stated n, scope nesting,
relative error against absolute over physical, the derived phase
quantities against the waypoint coordinates, that no accepted frame is
missing from a waypoint interval, and that the synthetic window
selection rule of D-032 reproduces the three selected windows from the
committed candidate list. For Section 7.3.3 it recomputes every wrist to
marker distance and every hold distance from the stored coordinates,
replays the inclusion rule on the stored carried and detected states and
checks the result against the stored inclusion column, re-derives the
transfer boundaries and the three intervals from the frames at which each
hand is at the cube, rebuilds the four medians from the included rows and
checks that they round to the values the chapter prints, and checks that
exactly the two hand-alone medians are marked as graded against the
physical reference and that both lie within the two centimetres the
chapter claims of it. It also checks identities across files: the
measured landmark of human_pairs.csv against the same landmark in
bare_model_pairs.csv, the rendered rig block of bare_model.json against
human.json on the identical frames, and the labelled frames of
loop_detection.json against the rows of natural.json. loop_detection.json
carries counts rather than pairs, so what is checked there is its own
arithmetic: the two coverage criteria against their missing frame lists,
runs and percentages, the despiked and bridged accounting, the handover
span and its intervals, the two-hand intervals re-derived from the grip
episodes, and both gap durations. Where a committed file outside this
directory exists it is used as well: the Unity capture
logs, the calibrated segment lengths, the avatar rig dimensions, the
manual label file, the loop and handover reports, and the SHA256 of
every recorded provenance source still present.

What it must skip is printed as an explicit SKIP line with the reason,
never passed silently. Without the gitignored recordings it cannot
recheck the acceptance gate itself, the synchronization and display
filter reproductions, the forward kinematics behind the model column,
the measured landmark behind the measured column, the object waypoint
detector with its sensitivity block and fitted line scatter, the object
rigid invariance check, any per-row distance of natural.json, the
coverage counts of loop_detection.json, or the carried and detected
states, the rail span endpoints and the coordinate columns behind the
Section 7.3.3 pairs. One published quantity has no coordinate pairs here
at all: the approximately 16 cm physical wrist to marker reference, which
is an author tape measurement and not a computed quantity.
On this machine the run reports 1147 checks passed, 21 skipped and none
failed; with the committed files present but none of the gitignored local
inputs it reports 1147 passed, 26 skipped and none failed, the five extra
skips being the source-hash lists it can no longer complete.

Full-thesis integration is in progress. Chapter 3 and Chapter 1 now
point to Appendix H, which holds the solver verification formerly in
Section 7.5 (D-037), and check_refs.py exits 0 with no unresolved
reference anywhere in the thesis. Other chapters are still being
revised for references that resolve but now point at different
content; CH7_INTEGRATION_FIXLIST.md tracks them. The standalone
chapter contains no reference to Section 7.5 and no old evaluation
figures or tables. CH7_DATA_REQUIRED.md states the remaining optional
author input; the object blocker it recorded is resolved.

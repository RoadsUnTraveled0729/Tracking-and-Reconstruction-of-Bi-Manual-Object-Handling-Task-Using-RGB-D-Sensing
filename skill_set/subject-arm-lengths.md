# Subject arm lengths (user measurement, 2026-09-07)

The subject's upper arm and forearm are both about 25 cm (user: "both of
my upper arm and lower arm are around 25cm"). This is an independent
anatomical comparison and nothing else. It is never the source of any
solver length, any avatar length or any rig length, and the pipeline has
never read it.

Against it, the loop recording's calibrated right arm (25.8/25.5 cm clean
medians, 25.6/25.2 cm at three decimals) is close to the anatomy, and the
rail recording's calibration (31.7/20.5 cm) splits about the same total
differently, consistent with the elbow landmark sitting farther along the
arm on that recording. The size of that shift is a computed number, not a
typed one: comparison.right.elbow_shift_along_shoulder_wrist_line_m of
writing/v9/audit_evidence/followup/m17_segment_diagnostic.json. It is a
landmark-placement observation, never anatomy and never an anatomical
error.

Decision D-005 (writing/v9/DECISIONS.md) stands for the solver: each
recording's recovery keeps its
own calibrated lengths because they describe where that recording's
landmarks sit. The "no rerun" half of D-005, which also kept the avatar on
the loop lengths, is SUPERSEDED by E-036 (eval/DECISIONS.md, 2026-09-14):
the Unity avatar is now sized per replayed recording from that recording's
own landmark geometry, through eval/reports/<alias>_rig_sizing.json, so
the three thesis captures are re-run. The avatar is still not sized from
the anatomical 25 cm: the solver never saw those numbers. The thesis
states the per-recording sizing in Sections 6.3 and 7.3 and in Chapter 9,
whose section numbers move with the v9 restructure, so follow
writing/v9/DECISIONS.md D-113 onward rather than a section number typed
here.

**Why:** the calibrated lengths are effective lengths of the landmark
track, and the two-link recovery must be consistent with the landmarks it
is fed; forcing anatomical lengths onto the rail solve would move the
rebuilt elbow away from the measured one and change every Chapter 7 rail
recovery number. The avatar has to reproduce the geometry the solver used
for the same reason, which is what E-036 corrects.

**How to apply:** never describe the rail lengths as anatomical; never
describe the old 25.6/25.2 cm avatar lengths as measured on the subject,
because they are the loop recording's landmark medians; quote "about 25
centimetres" for the subject's arm, never a finer figure; read the elbow
shift from the diagnostic JSON instead of typing it. A rerun with
anatomical lengths would be a separate study (reversible through the
offset-fit report the pipeline reads the lengths from). Related:
[[unity-capture-checks]], [[evaluation-scenario-separation]],
[[measurement-precision-reporting]].

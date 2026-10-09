#!/usr/bin/env python3
"""Build writing/v8/Chapter_4_Object_Tracking.docx (V8 rewrite round).

Chapter 4 as built: 4.1 World Anchoring and Camera Placement
Invariance, 4.2 Filtering and Cleaning the Object Track, 4.3 Worked
Example.  The section numbering is fixed, since other chapters cite
Section 4.1 and equation (4.x).

Method only (skill_set/thesis-structure-rules.md): no validation
results, no accuracy or error numbers, no coverage counts.  Detection
and planar pose recovery point to Appendix E, deprojection of depth
pixels to Appendix D, the Unity axis conversion to Chapter 6, and the
trajectory evaluation to Chapter 7.

Every printed number comes from writing/v7/scripts/ch4_numbers.py,
which recomputes it from the rail-recording artifacts (raw scaled ArUco
detections, scene_calibration_r6bc.json after the E-024 wall-lobe fix,
the filtered and the cleaned object track). Rail-only round 2026-09-01:
the worked example uses the scene frame of Figure 2.5 (frame 533, the
Chapter 3 worked-example frame) for the transformation chain and the
one undetected frame of the recording (frame 786, bridged by the filter
and blanked by the cleaning rule; frame 779 a despiked-and-bridged
detection kept with its flag) for the filtering and the cleaning step.
The rule of E-019 rejects no detected sample on this recording; the
held case (a run longer than the bridging limit) does not occur here
and is described as the case Section 9.2 shows on the loop recording
(the object marker lost when a finger crosses the printed square).
The old loop-recording example (frame 1236, handover frames 1065-1105)
is in git history before this round.

Figures: writing/v8/scripts/make_ch4_figs.py (Figure 4.2, the track) and
writing/v9/scripts/make_ch4_experiment_fig.py (Figure 4.1).

Supervisor round 5 (2026-09-07, on Chapter 4): C48, no number carries
more than two decimals, matrix entries included (translation vectors
in metres with two decimals, distances in prose in centimetres or
millimetres with one decimal, angles to 0.1 degree; the intermediate
product of the worked example is no longer printed, since its rounded
operands would not add up to the printed result); C49, the new Figure
4.1 shows the object marker as the camera sees it at the four moments
of the task with the detected pose drawn on it, and the track figure
becomes Figure 4.2. The source comments below keep the full-precision
values as the trace.

Revision of 2026-09-11 (Phase 3, continuity only; no method, parameter,
equation, figure, table or number changed):
 - Locked fact 1 (REVISION_2026-09-11_BRIEF.md section 3). The desk and
   object markers are 45 mm and the pipeline uses that size. Provenance,
   for this comment only and never for the prose: the pinned chain
   implements the size as the detector's 50 mm default multiplied by 0.9
   (eval/common/marker_size.py, E-009a; eval/reports/r6b_marker_scale.json
   and r7_marker_scale.json record assumed_black_square_mm 45,
   scale_applied 0.9). For a planar pose solver the translation scales
   linearly with the declared size, so this is exactly the 45 mm result.
   No sentence of this chapter presents a 45/50 correction; the chapter
   prints no marker size at all. Table 2.1 of Chapter 2 states it; the
   rebuilt Section 7.1 (D-029) states no marker size.
 - Locked facts 2 and 3. The physical route (25.5, 3.5 and 37.5 cm) and
   the rail (38.7 cm long, 3.8 cm tall) are the author's tape
   measurements. Under D-035 and D-036 the ArUco marker centre is the
   physical and reconstructed endpoint, so Section 7.2 compares endpoint
   segment lengths with those tape lengths; the line Chapter 7 fits to
   the slide samples stays a within-recording comparison that describes
   the spread of the reconstructed trajectory and not its accuracy. The
   chapter therefore promises no comparison against a reference path.
 - Chapter 7 restructure of 2026-09-12 (D-029, fix list item 4-1): the
   closing sentence no longer says that Chapter 7 reports the physically
   measured route. Sections 7.2.1 and 7.2.2 were Data Required when that
   edit was made; they now print the D-036 waypoint results, so the
   sentence is accurate as written and still names no printed value.
 - Cross-references checked against the rebuilt Chapter 7: the evaluation
   of the object track is Section 7.2, the live order of the cleaning
   rule is Section 8.2, and object marker loss is Section 9.2.

Table removal pass of 2026-09-14 (Chapter 2 companion edit, author
decision): Chapter 2's Table 2.3 is removed, so the two prose sentences
that pointed at it now point at Section 2.2.2, the scene calibration,
instead. No number, figure, table or equation of this chapter changes.

Notation pass of 2026-09-12 (D-054, D-056, D-058 and D-061; the 20 rows of
FRAME_INVENTORY.md section 8.9.4). Every frame-relative rotation and every
homogeneous transform of this chapter now carries both frames as Craig left
scripts under the semantic frame names, positions are written as Craig origin
vectors, and the flat subscripts T_CW, T_CO, T_WO, T_WC, t_CO, t_WC, t_WO,
R_CO, R_WO and the bare transposed rotation of the worked example retire. No
number, no transformation direction, no figure and no equation count changes.
The frame of equation (4.2), renumbered from (4.3) in the condensation
of 2026-09-15, is declared Unity (D-058), which is the copy the
implementation reads. Figure 4.1's caption is left untouched: its provenance
claim is the substantive defect S-8 of FRAME_INVENTORY.md section 9, which a
notation pass must not paint over, and the letters C, W and O of Section 4.1's
prose stay with it until the letter retirement of Chapter 2 is applied.

Prose condensation of 2026-09-14 (body toward 100 pages; readers are
systems engineers). Chapter 4 prose 2133 -> 2018 words, captions 168 ->
59. Cut: the Section 4.1, 4.2 and 4.3 roadmap sentences of the chapter
opening, and its Section 2.2.2 clause, which the first paragraph of 4.1
states in full; the camera-corner illustration reduced to one clause;
"but it is not yet fit to drive a reconstruction", a transition; and the
closing summary merged into fewer sentences. Everything else is wording
compression. No number, equation, figure, cross-reference or method step
was dropped.

Figure 4.1's caption is now 30 words and Figure 4.2's 29 (author's
caption limit of this round). The S-8 provenance claim of Figure 4.1,
that the desk-marker axes are the per-frame detected estimate while the
reconstruction uses the frozen calibrated anchor, moved into the
paragraph above the figure, where it replaces the looser sentence "The
axes on the desk marker are the world frame W"; it is not lost. Dropped
from the captions, and recorded here because no caption can hold them
inside 30 words: the sentence naming the yellow outline and the cube
axes as the object frame O (the paragraph above the figure states it),
the note that each panel repeats the cube at a larger scale in its upper
right corner, the phrase "before and after the signal filter" (the panel
key now says grey detected and blue filtered), and "so no row is held"
(the paragraph below Figure 4.2 states the held case does not occur on
this recording). Frames 95, 505, 700 and 898, the eleven bridged rows,
899 of 900 frames and the omitted wall marker are all kept.

Chapter 4 stopped at 2018 words in that round rather than the 1800 of the
brief. What remains is method definition, the worked example and its
pinned numbers, and cross-references; a further cut would remove a rule
of the filter or of the cleaning step, a caveat of the invariance
argument, or a printed value.
Figure 4.2 caption and text reconciled, 2026-09-15 (author decision). The
caption said "the eleven bridged rows. Detected on 899 of 900 frames."
while the paragraph below it said the recording has one undetected frame,
and nothing said that despiked rows are bridged too. Counts verified three
ways: writing/v7/scripts/ch4_numbers.py prints "whole-recording counts:
despiked 10, bridged 11, held 0";
eval/output/recording_20260831_065553_scaled_object_world_filtered.meta.json
records frames 900, detected 899, despiked 10, bridged 11, held_boundary 0;
and counting the CSVs directly gives 900 rows, one row with detected 0
(frame 786) and eleven rows with filled 1 (frames 676, 704, 707, 726, 754,
779, 786, 808, 809, 840 and 852), of which the ten other than 786 were
detected and despiked. The caption now reads "orange the eleven bridged
rows, ten despiked and one undetected" (28 words, inside the 30-word
limit) and carries no coverage count; the paragraph below carries the
coverage and the split. No value was invented or re-rounded.

Condensation round 2 of 2026-09-15 (CONDENSE2_BRIEF.md). Prose 2018 ->
1984, after three language-review rounds added back what the cuts had
made ambiguous. The old equation (4.2), which reprinted the homogeneous transform
and its inverse, is deleted: equation (3.4) of Chapter 3 already gives
that inverse, and Section 4.1 and the worked example now cite (3.4).
The old equation (4.3), the cleaning rule, is therefore equation (4.2);
no other script referred to a Chapter 4 equation number, so the
renumbering is contained in this file. The chapter opening loses the
sentence that recapped Chapter 3, and the closing paragraph loses its
"two products" announcement while keeping both products, both caveats
and every cross-reference. Section 4.2 keeps its pointer to the three
stages of Section 2.5 and now states only what Chapter 4 adds to them:
the straight-line bridging of position, which Section 2.5 owns, is
dropped, while the rotation handling of all three stages, the bridging
limit of eight frames and the hold behaviour, which Section 2.5 does not
have because it leaves long gaps missing, stay. No number, figure, table,
section number or method step changed.
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches
from docx.oxml.ns import qn

from eqn import r, nor, sub, sup, hat, frac, mat, d, eqArr, \
    add_display_eq, add_display_math, add_inline_math

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v9" / "figures"
FIGC = REPO / "writing" / "v9" / "figures"

H1, H2, H3, P, IMG, CAP, TBL, EQ = "h1", "h2", "h3", "p", "img", "cap", "tbl", "eq"
MATH = "mth"  # displayed, unnumbered worked-example mathematics
PM = "pm"     # paragraph mixing text runs and inline math
BUL = "bul"   # bullet item (supervisor comment C54, 2026-09-16)
NUM = "num"  # numbered item (C54 mechanics follow-up, 2026-09-16; see list_numbering.py)


def T(t):
    return ("t", t)


def X(f):
    return ("m", f)


# --- equation-fragment shorthands ---
# Craig notation, applied under D-054, D-056 and D-058: a frame-relative
# rotation (class 1) and a homogeneous frame transform (class 2) carry the
# reference frame as a left superscript and the described frame as a left
# subscript, written with the semantic frame names of the thesis frame table
# (Sensor, World, Object, Unity, MappedMarker).  Cancellation applies to those
# two classes only and never across the class-4 axis swap of Section 2.2.1,
# which this chapter neither prints nor cancels through.


SPACE = '<m:r><m:t xml:space="preserve"> </m:t></m:r>'


def pre(base, sup_, sub_=SPACE):
    """Craig left scripts; the shared equation helpers have no pre-script.
    An empty script slot renders as a placeholder box, so the unused slot of a
    position vector carries a space run instead."""
    return ('<m:sPre><m:sPrePr/>'
            f'<m:sub>{sub_ or SPACE}</m:sub><m:sup>{sup_}</m:sup>'
            f'<m:e>{base}</m:e></m:sPre>')


def Tf(a, b):
    """^A_B T, the pose of frame B described in frame A."""
    return pre(r("T"), a, b)


def Rf(a, b):
    """^A_B R, the orientation of frame B described in frame A."""
    return pre(r("R"), a, b)


def Porg(a, b):
    """^A P_BORG, the origin of frame B expressed in frame A."""
    return pre(sub(r("P"), b + nor("ORG")), a)


def bar(e):
    """Overbar accent (mean matrix); the shared equation helpers have none."""
    return ('<m:acc><m:accPr><m:chr m:val="\u0304"/></m:accPr>'
            f'<m:e>{e}</m:e></m:acc>')


SENS, WRLD, OBJ, UNI = nor("Camera"), nor("World"), nor("Object"), nor("Unity")
MM_i = nor("MappedMarker(") + r("i") + nor(")")
MM_l = nor("MappedMarker(last)")
A_, B_ = r("A"), r("B")

T_SW = Tf(SENS, WRLD)     # the calibrated anchor
T_SO = Tf(SENS, OBJ)      # the per-frame object pose
T_WO = Tf(WRLD, OBJ)      # the anchored object pose, equation (4.1)
T_WS = Tf(WRLD, SENS)     # the inverse anchor, the camera pose in the world
T_AB = Tf(A_, B_)
T_BA = Tf(B_, A_)
R_AB = Rf(A_, B_)
R_ABt = sup(R_AB, r("T"))
P_ABorg = Porg(A_, B_)
R_WS = Rf(WRLD, SENS)
R_SO = Rf(SENS, OBJ)
R_WO = Rf(WRLD, OBJ)
P_SW = Porg(SENS, WRLD)   # the desk marker origin seen from the camera
P_SO = Porg(SENS, OBJ)    # the object marker origin seen from the camera
P_WS = Porg(WRLD, SENS)   # the camera's own position in the world frame
P_WO = Porg(WRLD, OBJ)    # the anchored object position
g_W = pre(hat(r("g")), WRLD)
P_Ui = Porg(UNI, OBJ) + d(r("i"))
P_Ul = Porg(UNI, OBJ) + d(nor("last"))
R_Ui = Rf(UNI, MM_i)
R_Ul = Rf(UNI, MM_l)
R_rel = pre(r("R"), MM_l, MM_i)

t_i = sub(r("t"), r("i"))
t_l = sub(r("t"), nor("last"))
v_max = sub(r("v"), nor("max"))
w_max = sub(r("w"), nor("max"))
zeroT = sup(r("0"), r("T"))


Mbar = bar(r("M"))


def num_mat(rows):
    return mat([[r(c) for c in row] for row in rows])


content = [
(H1, "Chapter 4: Object Tracking and Scene Reconstruction"),

(P, "Chapter 2 left the marker branch at its raw product: each detected marker's pose relative to the camera. This chapter builds that pose into an independent branch that describes the carried object in the same calibrated metric scene. Appendix E covers the conversion of a detection into a pose."),

(H2, "4.1 World Anchoring and Camera Placement Invariance"),

(P, "The static calibration of Section 2.2.2 fixed the world frame at the desk marker and the other quantities of the scene. Every pose the detector returns is expressed relative to the camera, which is the wrong frame for a reconstruction: the same cube on the same spot gives a different camera-relative pose when the camera moves to another corner of the room. The object must instead be expressed relative to the desk marker's own frame, the world frame W. Figure 2.5 draws the three frames of the chain: the camera frame C, the world frame W at the desk marker, and the object frame O, which moves with the cube."),

(P, "Figure 4.1 shows the object marker as the camera sees it at four moments of the task. On each frame the outline and the axes drawn on the cube are the pose the detector returns for its marker in the camera frame. The axes on the desk marker show the per-frame detected estimate of the world frame W, while the reconstruction uses the frozen calibrated anchor."),
(IMG, FIGC / "ch4_fig_experiment.png", 6.3),
(CAP, "Figure 4.1. The object marker: (a) on the desk, frame 95; (b) lifted, frame 505; (c) sliding, frame 700; (d) the rail end, frame 898. The wall marker is omitted."),

(PM, [T("The marker branch writes each pose as the 4 by 4 homogeneous transformation of Chapter 3. The calibrated anchor "),
      X(T_SW), T(" maps a point of the world frame into camera coordinates, and the per-frame object pose "),
      X(T_SO), T(" maps a point of the object frame into camera coordinates. Both are available on any frame on which the cube is seen. The chain must deliver "),
      X(T_WO), T(", the object as seen from the world, and only one path connects the two frames:")]),

(EQ, T_WO + r(" = ") + T_WS + r(" ") + T_SO, "4.1"),

(PM, [T("The first factor is the inverse of the calibrated anchor, "),
      X(T_WS + r(" = ") + sup(d(T_SW), r("−1"))),
      T(", which equation (3.4) gives as a transpose and one matrix-vector product. Its translation column is the camera's own position in the world frame, so the camera pose in the reconstructed scene comes from the anchoring without a separate measurement. Chapter 6 places the sensor in the Unity scene at that pose.")]),

(P, "The chain makes the reconstruction independent of the location where the camera is set up. Both measured transformations change when the camera moves, but the camera frame enters equation (4.1) twice, as the described frame of the inverted anchor and as the reference frame of the object pose. Those two labels are adjacent in the product and cancel, so the remainder depends only on the cube's position relative to the desk. They cancel only if the anchor and the object pose are measured from the same camera position. On a recording the anchor is the frozen one of Section 2.2.2. The reconstruction is therefore invariant to a camera placed differently before the calibration window. A camera moved after that window breaks the invariance. The camera stands on a fixed support at the desk edge for the whole session. The world frame and the Unity frame are defined in Section 2.2.1, and Chapter 6 converts between them before anything is drawn."),

(H2, "4.2 Filtering and Cleaning the Object Track"),

(P, "The track that Section 4.1 delivers holds one entry per frame in the world frame, with a flag that records the marker's detection status. It passes a signal filter, the Pipeline B counterpart of the landmark filtering of Section 2.5, and then a single cleaning step against marker failure."),

(P, 'The filter runs the three stages of Section 2.5 over the track, with rotation added to each and with its own parameters, among them a bridging limit of eight frames rather than five. A spiked pose solution is wrong as a whole, so the despike test on position drops its rotation along with its position. Bridging turns along the shortest path between the endpoint rotations. A run at either end of the recording holds the first or the last valid pose, and an interior run longer than the bridging limit holds the valid pose before it. The smoothing stage runs a Savitzky-Golay filter on position [46]. On rotation the filter takes a rolling chordal mean, equation (2.1) applied to the world-frame object rotations over a short window.'),

(P, 'The detection flag passes through every stage unchanged. A row the marker was never seen on stays marked as not detected, and a despiked sample keeps its incoming flag while carrying the bridged pose. The raw track is kept unmodified in its own output. Figure 4.2 shows the track before and after the filter.'),  # src: v1/aruco/filter_object_track.py defaults (max_gap 8 frames, Savitzky-Golay window 9, polynomial order 2,
     #      rotation window 5) against the landmark filter of Section 2.5 (interior gaps no longer than 5 frames)

(IMG, FIG / "ch4_fig_track.png", 6.3),
(CAP, "Figure 4.2. The object marker origin in the world frame, one panel per axis: grey detected, blue filtered, orange the eleven bridged rows, ten despiked and one undetected."),

(P, "On the recording the hand never covers the marker, and the detector returns a pose on 899 of the 900 frames. The filter bridges that one undetected row along with the ten the despike test emptied. The held case of the filter, which the recording does not show, has a physical cause. A hand closing over the marker leaves the detector with nothing for longer than the bridging limit, so the track stays where the cube was last seen. Chapter 9 shows such a loss on the loop recording."),

(P, "The branch ends with two cases, and neither clears the detection flag. A detected row beside a held run is smoothed together with that run, so its pose can drift from the detection on its own frame while it still carries the detected flag. A partly covered marker, which the recording does not show either, may decode into a pose that is not right."),

(P, "The cleaning step at the end of the branch answers both cases. No later stage carries marker logic of its own: the recovery of Chapter 5, the streaming of Chapter 6, and the evaluation of Chapter 7 read the same cleaned track, and Section 8.2 gives the timing of the cleaning step in the live path."),

(P, "The rule is physical, carries no tuning to a particular recording, and walks the track forward. It keeps a sample only if the marker was detected, the pose is finite, and the step from the last kept sample is no larger than the task's slow movement can produce in the time between the two:"),

(EQ, eqArr(
    d(P_Ui + r(" − ") + P_Ul, "‖", "‖") + r(" ≤ ") + v_max + r(" ") +
    d(t_i + r(" − ") + t_l),
    nor("angle") + d(R_rel) + r(" ≤ ") + w_max +
    r(" ") + d(t_i + r(" − ") + t_l)), "4.2"),

# src: eval/common/clean_object_track.py, V_MAX = 1.0 and W_MAX_DEG = 400.0;
#      the numeric rates and their per-frame allowances are not printed
#      (skill_set/thesis-structure-rules.md rule 1)
# src: the frame of equation (4.2) is declared Unity by D-058, matching
#      eval/common/clean_object_track.py:59-61, which reads unity_px, unity_py
#      and unity_pz and rebuilds the rotation from unity_ex, unity_ey and
#      unity_ez.  The swap of Section 2.2.1 is orthogonal, so the norm and the
#      relative angle are identical in the world frame and no printed number
#      changes.  The child frame of the rotation is MappedMarker, not Object,
#      because the axes the Unity copy carries are the swapped ones
#      (v1/aruco/frames.py:88, R_U = S R_W S); the two frames share the marker
#      centre as their origin, which is why the position keeps Object.
(PM, [T("Equation (4.2) uses the Unity frame of Section 2.2.1, because the rule reads the Unity copy of each row. That frame exchanges two coordinates of the world frame, which changes no distance and no relative angle, so the rule bounds the same two quantities in either frame. In that frame the object's own axes are the mapped marker axes, which Chapter 6 obtains by applying that exchange to both sides of the object rotation. The rule forms the second bound from the two orientations of the Unity copy, "), X(sup(d(R_Ul), r('T')) + r(' ') + R_Ui), T(', in which the reference frame cancels and leaves the relative rotation between the two samples.')]),

(PM, [T('The two bounds are rates rather than fixed steps: '), X(v_max), T(' bounds the linear step and '), X(w_max), T(' the angular step, each an allowance per unit of elapsed time between the candidate and the last kept sample. A real occlusion, during which the cube does travel, therefore leaves the rule ready to accept the marker when it is detected again. Measuring against the last kept sample rather than the previous row keeps one bad pose from dragging the track behind it. Both bounds carry a margin of about a factor of two over the largest step the clean parts of the recording show, so the rule is a guard.')]),

(P, "A sample that fails the test has its pose columns blanked and its detection flag cleared, and so does every row the marker was never detected on. A later stage reads filtered poses on the kept rows and blanks elsewhere, and on a blanked row it holds the last kept pose and flags it as held."),

(H2, "4.3 Worked Example"),

(P, "The transformation chain runs on frame 533 in the scene image of Figure 2.5, the worked-example frame of Chapter 3, where the subject holds the cube against the rail and its marker is cleanly detected. The cleaning step runs on frame 786, the one frame of the recording on which the marker is not detected."),  # src: writing/v7/scripts/ch4_numbers.py (rail recording, frames 533 and 786)

(P, "Vectors and matrices are printed to two decimals. Averaging the ten desk rotations of the calibration window element by element gives"),
(MATH, pre(Mbar, SENS, WRLD) + r(" = ") + num_mat([  # src: writing/v7/scripts/ch4_numbers.py, element-wise mean over eval/output/recording_20260831_065553_aruco_raw_scaled.csv
    ["1.00", "0.00", "−0.02"],
    ["−0.02", "−0.48", "−0.88"],
    ["−0.01", "0.88", "−0.48"]])),
    # full precision (round 5, C48: two decimals in print): 0.999704, -0.001401,
    # -0.024251 / -0.021907, -0.483249, -0.875208 / -0.010492, 0.875481, -0.483136
(PM, [T("which is not a rotation matrix, since its determinant is not exactly one and its columns are only nearly perpendicular. Equation (2.1) projects it back onto the nearest rotation, and at the precision printed here no entry changes, because the ten input rotations disagree so little. With the mean of the ten translations, the projected rotation forms the frozen anchor "),  # src: writing/v7/scripts/ch4_numbers.py (det A = 0.999996; |R - A| max 1.44e-06); mean of the ten desk translations (0.023458, 0.187377, 0.552492) m matches T_cam_desk in eval/output/scene_calibration_r6bc.json
      X(T_SW), T(". That anchor puts the calibrated desk marker 55.3 cm in front of the camera and 18.7 cm below it.")]),

(PM, [T("The same calibration gives the scene description of Section 2.2.2. Gravity, taken from the wall marker, is the unit direction "),
      X(g_W + r(" = (−0.02, 0.53, 0.85)")),
      T(", at 32.0 degrees to the world z axis, which is the tilt of the desk marker card on its stand. The world origin sits 3.8 mm below the horizontal tabletop model of Section 2.2.2.")]),  # src: eval/output/scene_calibration_r6bc.json scene_geometry (gravity_up_world (-0.0212, 0.5300, 0.8477), desk_stand_tilt_deg 32.04, origin_above_tabletop_m -0.0038, object_cube_size_m 0.07 supplied via --cube-size)

(PM, [T("Transposing the anchor rotation gives "), X(R_WS),
      T(", and applying it to the negated translation gives the inverted anchoring transformation of equation (3.4),")]),
(MATH, P_WS + r(" = −") + R_WS + r(" ") + P_SW + r(" = (−0.01, −0.39, 0.43) m")),  # src: writing/v7/scripts/ch4_numbers.py, inverse of T_cam_desk in eval/output/scene_calibration_r6bc.json: (-0.013549, -0.393115, 0.431492) m
(P, "which puts the camera 58.4 cm from the world origin and 15.4 cm above the same tabletop model."),  # src: writing/v7/scripts/ch4_numbers.py (58.4 cm from the world origin, 15.4 cm above the gravity-normal tabletop model)

(P, "The chain of equation (4.1) runs on the scene image. The object marker is detected there, and its origin in the camera frame is"),
(MATH, P_SO + r(" = (−0.21, 0.16, 1.02) m")),  # src: writing/v7/scripts/ch4_numbers.py, frame 533 of eval/output/recording_20260831_065553_aruco_raw_scaled.csv: (-0.209474, 0.155957, 1.022892) m
(P, "The cube is therefore 106 cm from the camera, on the rail in front of the subject. Multiplying the inverted anchoring transformation by that object transformation gives one expression for each block: the transposed anchor rotation multiplies the object rotation and the object translation, and the translation block also includes the camera position:"),  # src: writing/v7/scripts/ch4_numbers.py (range from the camera 1.06 m)

(MATH, eqArr(
    R_WO + r(" = ") + R_WS + r(" ") + R_SO,
    P_WO + r(" = ") + R_WS + r(" ") + P_SO + r(" + ") + P_WS)),

(P, "Adding the camera position to the transformed object translation gives the world translation, with the rotation product beside it:"),  # src: R^T t_CO = (-0.223562, 0.820451, -0.625612) m, no longer printed (round 5, C48: at two decimals the rounded operands would not add up to the printed result)
(MATH, eqArr(  # src: writing/v7/scripts/ch4_numbers.py, world object pose on frame 533
    P_WO + r(" = (−0.24, 0.43, −0.19) m"),
    R_WO + r(" = ") + num_mat([
        ["1.00", "0.01", "0.07"],
        ["0.05", "0.52", "−0.85"],
        ["−0.05", "0.86", "0.52"]]))),
    # full precision: t_WO (-0.237111, 0.427336, -0.194120) m; R_WO 0.997476,
    # 0.013288, 0.069747 / 0.052808, 0.517788, -0.853877 / -0.047462,
    # 0.855405, 0.515780
(PM, [T("Projected onto "), X(g_W),
      T(", the marker centre is 6.3 cm above the tabletop model. The cube is held against the rail at that instant, and the rail height measured with a tape puts the cube centre 7.3 cm above the tabletop. The comparison uses marker-centre height in place of cube-centre height for this mounting and orientation. The sources of the discrepancy have not been separated.")]),  # src: writing/v7/scripts/ch4_numbers.py (6.3 cm above the gravity-normal tabletop model; rail height 3.8 cm, the author's tape measurement of REVISION_2026-09-11_BRIEF.md section 3 fact 2, plus half the 7 cm cube)

(P, "For the cleaning step, the object marker is seen on frames 785 and 787, at world x 3.0 cm and 3.4 cm, and the detector returns nothing on frame 786 between them. The gap is one frame, inside the bridging limit of eight, so the filter bridges it. The bridged position sits 1.0 mm from the mean of the two detections beside it."),  # src: writing/v7/scripts/ch4_numbers.py, frames 783-789 of eval/output/recording_20260831_065553_scaled_object_world.csv against ..._filtered.csv and ..._filtered_clean.csv; frame 779 dev 20.6 mm

(P, "The rule then walks the filtered track. Frame 786 is 3.3 mm and 1.2 degrees from the last kept sample, frame 785, well inside the allowance. The marker was never seen on it, so the row is blanked. Frame 787, two frame intervals later, is 4.9 mm from frame 785 and is kept. The rule rejects no detected sample anywhere in the recording."),  # src: writing/v7/scripts/ch4_numbers.py (cleaning decision around frame 786; rejected: none; blanked: [786])

(P, "The frozen scene fixes the desk, gravity, tabletop, camera and cube edge of Table 2.1 in one frame. The cleaned track gives a measured cube pose, a marked gap where the marker was missed, and the marker identity on each row. A grip ties the branches together in Chapter 5, constraining the carrying arm. Chapter 6 streams the position and orientation. Section 7.2 evaluates the track against the physical route; a line fit to the slide samples describes spread, not accuracy. No second measurement chain checks the streamed orientation."),

]

doc = Document()
style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(12)

# D-106: unnumbered display ordinals continuing into the following clause.
DISPLAY_COMMAS = {1, 2}
math_display_index = 0

for item in content:
    kind = item[0]
    if kind == H1:
        doc.add_heading(item[1], level=1)
    elif kind == H2:
        doc.add_heading(item[1], level=2)
    elif kind == H3:
        doc.add_heading(item[1], level=3)
    elif kind == P:
        doc.add_paragraph(item[1])
    elif kind == PM:
        p = doc.add_paragraph()
        for typ, val in item[1]:
            if typ == "t":
                p.add_run(val)
            else:
                add_inline_math(p, val)
    elif kind == EQ:
        add_display_eq(doc, item[1], item[2])
    elif kind == MATH:
        math_display_index += 1
        add_display_math(doc, item[1],
                         punctuation="," if math_display_index in DISPLAY_COMMAS else ".")
    elif kind == IMG:
        path = Path(item[1])
        assert path.exists(), f"missing figure: {path}"
        doc.add_picture(str(path), width=Inches(item[2]))
    elif kind == BUL:
        # bullet item (supervisor comment C54, 2026-09-16)
        p = doc.add_paragraph(style="List Bullet")
        if item[1]:
            p.add_run(item[1]).font.bold = True
            p.add_run(" " + item[2])
        else:
            p.add_run(item[2])
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        p.paragraph_format.space_after = Pt(4)
    elif kind == NUM:
        # numbered item, restarted per contiguous run (C54 mechanics
        # follow-up, 2026-09-16; see list_numbering.py)
        p = doc.add_paragraph(style="List Number 2")
        if item[1]:
            p.add_run(item[1]).font.bold = True
            p.add_run(" " + item[2])
        else:
            p.add_run(item[2])
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        p.paragraph_format.space_after = Pt(4)
    elif kind == CAP:
        p = doc.add_paragraph(item[1])
        p.runs[0].font.size = Pt(10)
        p.runs[0].font.italic = True
    elif kind == TBL:
        rows = item[1]
        t = doc.add_table(rows=len(rows), cols=len(rows[0]))
        t.style = "Table Grid"
        for i, row_ in enumerate(rows):
            for j, c in enumerate(row_):
                cell = t.cell(i, j)
                cell.text = c
                for par in cell.paragraphs:
                    for run in par.runs:
                        run.font.size = Pt(10)
                        if i == 0:
                            run.font.bold = True

out = REPO / "writing" / "v9" / "Chapter_4_Object_Tracking.docx"
from list_numbering import restart_numbered_lists
restart_numbered_lists(doc)

doc.save(out)
print("saved", out, "| items:", len(content))

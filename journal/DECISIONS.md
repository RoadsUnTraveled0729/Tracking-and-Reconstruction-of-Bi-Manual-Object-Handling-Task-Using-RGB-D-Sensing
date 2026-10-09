# journal decisions

Format follows AGENTS.md (ID, Status, Decision, Why, Alternatives,
Evidence, Reversibility, Review). This track derives a journal paper
from the thesis (writing/v9). Its first part is a self-contained
derivation of the step "kinematic model -> joint angles", written for
two frame conventions: Method A (what v1/kinematics does today) and
Method B (a right-handed convention requested by the author for the
paper). Plan: /home/luo/.claude/plans/cozy-honking-origami.md
(milestone 1). Thesis values cited here are SETTLED with the thesis or
the code as evidence; every choice the author has not confirmed is
UNCERTAIN.

ID: J-001
Status: SETTLED
Decision: The journal track lives in journal/ only; nothing outside
journal/ is edited; v1/ is imported (sys.path insert of
v1/kinematics), never edited or copied.
Why: the same self-contained rule as eval/akc_comparison/ (AKC-001)
keeps the paper work separate from the frozen pipeline and the thesis;
importing v1/kinematics/root_frame.py instead of copying it means
Method A in the paper is, by construction, the code that produced the
thesis numbers.
Alternatives: copying root_frame.py into journal/ (rejected: a copy can
drift from the frozen original); placing the work under writing/v9
(rejected: V9 is the delivered thesis, post-defence revisions there
are logged separately from D-394 onward).
Evidence: AGENTS.md, Standing project constraints (v1 frozen, import
or copy only); approved plan, "Deliverables of milestone 1". The
script sets sys.dont_write_bytecode = True so the import writes no
.pyc into v1/kinematics.
Reversibility: folder move.
Review: git status shows no path outside journal/.

ID: J-002
Status: SETTLED
Decision: Method B root frame at L24, in the right-handed {Camera}
(x right, y down, z forward, subject facing the camera):
x_B = normalize(L23 - L24) (subject's left), s = L12 - L24,
z_B = normalize(x_B x s) (subject's forward, toward the camera),
y_B = z_B x x_B (subject's up), R_B = [x_B | y_B | z_B].
Why: the master's reading of the author's instruction "keep it
right-handed, frame at L24, x from 24 to 23". With x reversed relative
to Method A and the same cross-product order as build_root_frame, z
and y come out forward and up, so B differs from A only in the x
column and remains a proper rotation (det +1) in a right-handed frame,
without the F = diag(1, -1, 1) flip.
Alternatives: the rejected v1 sketch (X = 24->23, Y = X x (24->12),
Z = X x Y; v1/KINEMATIC_MODEL.md section 3.3), which makes Y the
anterior-posterior axis and Z point down; keeping Method A's x
direction in {Camera} (gives a left-handed triad, det -1 as a
{Camera} matrix).
Evidence: computed by journal/scripts/make_tpose_frames_fig.py on the
ideal T-pose: R_B = diag(1, -1, -1), det(R_B) = +1; F R_A =
diag(-1, -1, -1) (A's columns in physical {Camera}, det -1);
R_B^T (F R_A) = diag(-1, 1, 1), so x opposite, y same, z same
(script prints "PASS"). The axis choice itself is an interpretation of
the author's words, not measured. Author confirmed Figure 1 panel (b) on 2026-10-07.
Reversibility: change method_b_root() in the script and regenerate
the figure.
Review: the author confirms on Figure 1 (journal/figures/
fig1_tpose_frames.png, panel b) that x_B = subject's left, y_B = up,
z_B = forward is the intended convention.
Annotation 2026-10-08 (J-018): the construction is unchanged and is derived in
KINEMATIC_ANGLES.md Section 3.2 under the name "right-handed convention"; the
name "Method B" and the matrix names R_A, R_B no longer appear in the document.

ID: J-003
Status: UNCERTAIN
Decision: Schematic proportions from thesis Table 3.1 (frame 533 of
recording_20260831_065553, {Camera} column, two-decimal values):
shoulder width |L11-L12| = 0.3834 m, hip width |L23-L24| = 0.1803 m,
upper arm = mean(|L12-L14|, |L11-L13|) = 0.3164 m, forearm =
mean(|L14-L16|, |L13-L15|) = 0.2329 m, hip-to-shoulder height =
mean vertical separation |y24-y12|, |y23-y11| = 0.5200 m, hip row at
the mean hip y = 0.1850 m; subject depth z = 2.0 m.
Why: the plan asks for the author's own proportions when the table
gives them; it does. Segment lengths are pose-independent, so frame
533 (arms not in a T-pose) still yields them. The torso height uses
only the vertical separation because Table 3.1 is printed before the
hip depth preparation of thesis Section 2.6 (table caption and text),
so the hip z, and with it the 3D hip-shoulder length (0.6187 m right,
0.6460 m left), is not trusted. z = 2.0 m is the brief's value; it
only places the schematic and does not enter R_A or R_B.
Alternatives: nominal values (shoulder 0.40, hip 0.30, upper arm 0.30,
forearm 0.26, torso 0.50 m; the brief's fallback, not needed since the
table gives coordinates); the 3D torso length (rejected for the
reason above); the per-side forearm (0.1985 right, 0.2672 left;
averaged for a symmetric schematic).
Evidence: writing/v9/scripts/build_ch3.py, Section 3.5, Table 3.1
(values and caption); lengths printed by the script. UNCERTAIN
because the inputs are rounded to two decimals, come from one frame,
the forearms differ by 0.07 m between sides, and the torso-height
choice is a judgement.
Reversibility: edit TABLE_3_1_CAMERA or proportions_from_table() and
regenerate. The frames do not depend on these values.
Review: whether the schematic should instead use the M2 perfect frame
or the subject's measured segment lengths (thesis Section 6.3).

ID: J-004
Status: UNCERTAIN
Decision: Figure 1 conventions: image-plane view (page right = camera
+x, page down = camera +y, as the camera image shows it, so the
subject's left is on the page's right); x red #FF4040, y green
#40E070, z blue #408CFF; in-plane axes as arrows of fixed drawn length
0.110 m (image-plane metres); z, which points toward the viewer in
both methods, as a blue circled dot at the landmark (ring radius
0.020 m) plus a short diagonal arrow (0.065 m, page up-right) labelled
"z"; circled cross for an axis into the page (the camera z axis in
the corner glyphs); connections grey #9a9a9a, landmark dots white with
a dark edge (covered by the z symbol at each landmark); landmark
labels "Lnn" plus anatomical name 0.055 m below the dot (hip labels
pushed outward); panel titles "(a) Method A: left-handed {Camera'},
root x = L23 -> L24" and "(b) Method B: right-handed {Camera}, root
x = L24 -> L23"; corner axes {Camera'} (x right, y up, z into page)
and {Camera} (x right, y down, z into page); a legend box under the
panels; 200 dpi, 12 x 4.7 in, Agg backend.
Why: the axis colours are the deck's (presentation/defense_2026/anim/
coordinate_axes.py AXIS_COLORS), so the paper matches the defence
figures; the image-plane view is what the camera and MediaPipe see;
fixed arrow lengths show directions only, since the frames are
rotations. The pixel-level sizes (arrow, ring, offsets, figure size)
were chosen by viewing the rendered PNG until no arrow overlaps a
landmark label; they have no source beyond that visual check.
Alternatives: a dark MediaPipe-style background (the plan allowed it;
white chosen for a journal page); an oblique 3D view (rejected: the
out-of-page axis is clearer as a circled dot in the image plane);
the panel titles without "(a)"/"(b)" as written in the brief (prefix
added for referencing in the text).
Evidence: brief and plan, Step 1; visual check of
journal/figures/fig1_tpose_frames.png. The light green #40E070 was
picked for a dark background and has lower contrast on white; kept to
match the deck.
Reversibility: constants at the top of the drawing section of
journal/scripts/make_tpose_frames_fig.py.
Review: legibility of the green labels and the hip triads (hip width
0.18 m is narrow against 0.11 m arrows) at the journal's column width.
Annotation 2026-10-08 (J-018): the panel titles are now "(a) implemented
convention" and "(b) right-handed convention" (labels only, make_tpose_frames_fig.py);
the constants of this entry are unchanged.

ID: J-005
Status: UNCERTAIN
Decision: Perfect-frame selection criteria
(journal/scripts/select_perfect_frame.py). All 28 bags in recordings/
(sorted, the 3 legacy symlinks skipped); MediaPipe PoseLandmarker heavy
(v1/mediapipe/models/pose_landmarker_heavy.task), VIDEO mode,
num_poses 1, confidences 0.3, CPU delegate; coarse pass every
STRIDE = 5 colour frames. Scores: vis_min8 = min visibility over L11-L16,
L23, L24; margin_ok = the 8 and L0 inside the image with
MARGIN_FRAC = 0.03 of width/height on each side; depth_ok = aligned
single-pixel depth > 0 at the 8; sharpness = variance of
cv2.Laplacian (CV_64F) of the grey image; tpose = max arm segment
|dv| / shoulder pixel width. Gates: vis_min8 >= VIS_GATE = 0.9,
margin_ok, depth_ok; ranking vis_min8 desc, then sharpness desc.
T-pose pick: gated and tpose <= TPOSE_GATE = 0.15. Refinement at
stride 1 in +-WINDOW = 25 frames around the top REFINE_TOP = 3 distinct
(non-overlapping) overall windows, the top 3 distinct T-pose windows and
the best head-in window; final picks from the refined rows. Contact
sheet: best frame of each of the top CONTACT_TILES = 12 distinct
windows.
Why: the brief's definition of "perfect" for the worked example
(highest 8-landmark visibility, head in the image, sharp, valid depth).
Constants and their sources: STRIDE 5, VIS_GATE 0.9, MARGIN_FRAC 0.03,
TPOSE_GATE 0.15, WINDOW 25 and REFINE_TOP 3 are the M2 brief's choice,
with no measurement behind them. The MediaPipe settings and the model
file are the frozen extractor's (v1/mediapipe/
extract_landmarks_to_csv.py lines 85-89, --model default heavy). The
following are the worker's judgement, each logged here: (1) "distinct"
windows (a later candidate must be more than 2 x WINDOW frames from an
earlier one in the same bag), because the top coarse frames are
neighbours and three overlapping windows would refine one stretch of
video; (2) the fine pass runs MediaPipe at stride 1 from frame 0 of the
bag, not from the window start, so a refined frame carries the
landmarks the frozen extractor (stride 1 from the bag start) would
produce: a fresh tracker started at the window start gave visibilities
up to 0.13 lower at the same frames (arm_test frames 10-60, smoke run),
because VIDEO-mode results depend on the tracking history; (3) three
T-pose windows instead of one, because the single best coarse T-pose
window (arm_test #35, stride-5 history) lost its gate at stride 1 and
left no T-pose pick in the first full run; (4) CPU delegate for
determinism (two runs gave byte-identical coarse rows); (5) two
informational scores that do not gate the main pick: head_in = all
face landmarks L0..L10 inside the same 3 % margin (the brief's L0-only
test passes frames whose forehead is cut off), and
hip_minus_shoulder_depth_m = mean hip depth minus mean shoulder depth
(5x5 median), which flags hip pixels that see something in front of
the body; a third pick (best gated head_in frame) is written beside
the brief's two; (6) contact sheet with one tile per distinct window,
so 12 tiles show 12 alternatives instead of 12 neighbouring frames.
Depth is recorded twice for each of the 8 landmarks: single pixel at
(int(x*w), int(y*h)) and the 5x5 median of nonzero returns (the frozen
extractor's --depth-window 5 default); xyz is deprojected with
rs2_deproject_pixel_to_point for both.
Alternatives: gating on head_in (not done: it changes the brief's
gate and is the author's call, see J-006); full stride 1 over all bags
(about 5 times the MediaPipe work of the coarse pass, which took
6.7 min at stride 5); a
learned or face-detector head test (no source in the repository).
Evidence: brief M2 (master, 2026-10-07); run log of 2026-10-07: 28 bags,
none failed, 6192 coarse frames scored, 720 gated, 306 fine frames
scored, 208 gated, 0 hardware frame number mismatches between the two
playbacks, 523.9 s; coarse rows identical across two full runs; a
two-bag smoke run reproduced byte-identical CSV and JSON (except the
run time). UNCERTAIN because every gate value is a choice without a
measurement behind it.
Reversibility: constants at the top of select_perfect_frame.py; rerun
(about 9 min).
Review: whether 0.9, 3 %, 0.15 and the L0-only head test express what
"perfect" should mean for the paper's worked example.

ID: J-006
Status: SETTLED
Decision: The worked-example frame under the brief's criteria is
R7_rail_handover_earlier_take_20260908_235402.bag, frame index 662
(0-based count of colour+depth framesets, as the frozen extractor's
"frame" column), hardware colour frame number 952, t = 22.083 s from
the bag start: vis_min8 0.97300, vis_min_face 0.99609, sharpness
460.73, tpose 0.642, margin_ok and depth_ok true. T-pose pick:
ENSC498_arms_outstretched_pose_test_arm_test.bag frame 167 (hw 605,
t 5.571 s): vis_min8 0.92426, sharpness 245.85, tpose 0.1365.
Head-in alternative: R5_occlusion_waypoint_loop_primary_20260825_222315.bag
frame 202 (hw 492, t 6.738 s): vis_min8 0.95690, sharpness 553.79,
face_top_y 0.0311, all face landmarks inside the 3 % margin.
Why: highest vis_min8 among the 208 gated refined frames (J-005
ranking); records in journal/data/perfect_frame.json,
perfect_frame_tpose.json and perfect_frame_headin.json.
Alternatives: the next refined frames differ by less than 0.0005 in
vis_min8 (frame 663 of the same bag 0.97284; 235500 frame 1234
0.97250), so the ranking among the top R7 frames is a near tie.
Evidence: run log 2026-10-07 (journal/data/perfect_frame.json
"selection" block); journal/figures/perfect_frame_overlay.png and
candidates_contact.png viewed. SETTLED by measurement for the
criteria as given; two observations from the same measurement qualify
it: (a) the pick's top face landmark has y = -0.011 (above the image):
the forehead is cut off, so "head inside the image" holds only for the
nose; (b) the hip depths (L23 1.221 m, L24 1.169 m) are 0.114 m (mean)
nearer than the shoulders (L11 1.320 m, L12 1.298 m), consistent with
the hip pixels seeing the hands, the cube or the rail in front of the
body rather than the body (not verified pixel by pixel). The head-in
alternative has the same sign (-0.067 m) and a horizontal stick crosses
the image at shoulder height there.
Reversibility: choose another record from perfect_frame_candidates.csv
or change J-005 and rerun; the derivation reads the JSON.
Review: the author looks at journal/figures/perfect_frame_overlay.png
and candidates_contact.png (and perfect_frame_headin_overlay.png,
perfect_frame_tpose_overlay.png) and confirms which frame the paper's
worked example uses, given the cut forehead and the hip depth
observation above.
Amendment 2026-10-07 (superseded by J-010 for the picks): the overall
pick R7_235402 frame 662 is rejected by the author's check that all 8
landmarks be correctly measured. Its L24 (right hip) pixel (294, 316)
lies on the occlusion edge between the trousers and the right hand: the
depth there, 1.169 m single pixel and also 1.169 m as the 5x5 median,
is a ramp value between the trousers (1.207 m, clean 9x9 patch beside
the landmark) and the hand (1.08 m); the 9x9 window at L24 has valid
fraction 0.802, std 35.8 mm, max-min 131 mm. L23 (1.221 m, std 6.4 mm)
is clean. The record is kept as
journal/data/perfect_frame_rejected_r7_662.json (field rejected_reason;
figure journal/figures/perfect_frame_l24_depth_check.png). The head-in
alternative R5_222315 frame 202 also fails the J-010 gate (L11 std
9.0 mm, L16 8.3 mm). New picks under J-010 (J-005 gates plus
depth_clean8, ranking unchanged): overall
R7_rail_handover_earlier_take_20260908_235500.bag frame 1174 (fine row,
hw 1463, t 39.163 s), vis_min8 0.96697, vis_min_face 0.99792,
sharpness 453.81, tpose 0.620, depth_std_max8 7.8 mm (L15), every
window 100 % valid, face_top_y -0.0008 (top of the head at the image
edge); head-in R5_occlusion_waypoint_loop_primary_20260825_222315.bag
frame 204 (fine, hw 494, t 6.805 s), vis_min8 0.95553, sharpness 554.34,
depth_std_max8 7.999 mm (L23, 0.001 mm under the threshold). T-pose:
none; every one of the 22 T-pose rows (all in the arms_outstretched
bag) fails at L15 and the earlier T-pose record carries a
depth_clean_stage note saying so.

ID: J-007
Status: UNCERTAIN
Decision: Every formula in KINEMATIC_ANGLES.md uses Craig notation
exactly as printed in thesis Chapter 3 (eqs. 3.1-3.14): rotation
^{A}_{B}R, position ^{A}P_{k} (or ^{A}q, ^{A}p, ^{A}s), axis columns
^{A}\hat{X}_{B}, flip ^{Camera'}q = F ^{Camera}p. The shorthands R_A, R_B,
\hat{X}_B and the abbreviations C and C' are removed. Method A's root
rotation is ^{Camera'}_{L24}R. Method B's frames at the same five
landmarks are named {L24*}, {L12*}, {L11*}, {L14*}, {L13*} (a star marks
the right-handed variant), so Method B's root rotation is
^{Camera}_{L24*}R with columns ^{Camera}\hat{X}_{L24*} and so on. The
comparison matrix of Section 0.6 is
(^{Camera}_{L24*}R)^T F ^{Camera'}_{L24}R.
Why: author instruction 2026-10-07 (formulas in the thesis's notation).
Method B's root is a different frame from {L24} at the same landmark, so
it needs its own label; a frame label may appear only in the frame slot
of a Craig symbol (writing/v9/FRAME_INVENTORY.md section 2.3), and a
star in that slot cannot be confused with the prime of {Camera'}, which
already marks the y-flip.
Alternatives: {L24B} or {L24^B} (rejected: B reads as a frame letter and
collides with the generic frame B of the thesis); a prime {L24'}
(rejected: {Camera'} already uses the prime for the y-flip, so a prime on
L24 would read as a flipped frame); keeping R_A and R_B (rejected by the
author's instruction).
Evidence: writing/v9/zh/src/Chapter_3_Kinematic_Modeling.txt lines 1-115;
writing/v9/scripts/build_ch3.py (Ppt, Ax, pre and the eq. 3.1-3.14
entries); writing/v9/FRAME_INVENTORY.md; the star name itself is the
master's instruction, with no source beyond it, hence UNCERTAIN. The
thesis equations were copied; the numbers in section 0 are unchanged.
Reversibility: rename the star label throughout KINEMATIC_ANGLES.md
(search for L24*, L12*, L11*, L14*, L13*) and update this entry. The
figure script prints R_A and R_B and is unchanged.
Review: whether the star label is acceptable for the paper, and whether
F ^{Camera'}_{L24}R may be printed as a bare product of an improper map
and a rotation in Section 0.6 (it is used there only as a comparison
device).
Annotation 2026-10-08 (J-018): the star labels {L24*}, {L12*}, {L11*}, {L14*},
{L13*} are still used, and Craig notation is unchanged. The Section 0 and 0.6
references above describe the superseded document; the comparison now sits in
Section 3.3 of the rewritten note. Convention marks lh and rh replace the
shorthands (J-018).

ID: J-008
Status: UNCERTAIN (master decision, author to confirm)
Decision: Method B applies no y-flip; all points stay in {Camera}
(x right, y down, z forward, right-handed); only the hip axis is
reversed (x = L24 -> L23, J-002).
Why: F = diag(1,-1,1) has det -1 and is exactly the improper map that
makes {Camera'} left-handed; Method B exists to keep a right-handed
chain end to end, so no improper map may enter. A y-up right-handed
frame, if ever wanted for display, is reached by the proper rotation
R_x(180 deg) = diag(1,-1,-1), det +1, applied to the final result, and
it does not change any joint angle. Method B's forward kinematics then
lands directly in {Camera} and projects onto the image with the
recorded intrinsics without any un-flip.
Alternatives: y-flip as in Method A (rejected: det -1); proper rotation
diag(1,-1,-1) before building frames (rejected for now: adds a step
that the angle derivation does not need; may be revisited for
figures).
Evidence: det F = -1 (KINEMATIC_ANGLES.md eq. 0.2); the author's
instruction of 2026-10-07 that the master decides this; no
measurement.
Reversibility: if overturned, Method B's input becomes R_x(180)
{Camera}P and section 0.5 is recomputed; the physical axes in Figure 1
do not change.
Review: the author reads section 0.5 and this entry.
Annotation 2026-10-08 (J-018): the decision stands (the right-handed convention
applies no flip and stays in {Camera}); the references to section 0.5 and to
"Method B" describe the superseded document (now Sections 2.2 and 3.2).

ID: J-009
Status: SETTLED (author instruction 2026-10-07)
Decision: Milestone plan after M2. M3: Method A angles (root ZXY Euler,
shoulder swing-twist, elbow, left-arm mirror; thesis eqs 3.15-3.24)
computed with the chosen frame's numbers. M4: Method B angles with the
sign changes derived, and an A-versus-B table. M5: forward kinematics
in Python for both methods from segment lengths and angles,
reconstructing the 8-point skeleton and reporting the per-landmark
position error versus the measured landmarks, plus an overlay on the
RGB frame (Method A reconstructed in {Camera'} then un-flipped by F
before projection; Method B projected directly, J-008).
Why: the author asked that the final angles of both methods be run
through forward kinematics and the reconstructed skeleton compared
with the input landmarks, which closes the loop on the derivation.
Alternatives: none considered; the author specified the step.
Evidence: the author's messages of 2026-10-07. The main worked-example
frame is still the author's choice (J-006 Review).
Reversibility: the plan is a sequence only; reorder or drop M5 by
editing this entry.
Review: the author confirms the worked-example frame (J-006) before M3
starts.
Annotation 2026-10-08 (J-018): the plan M3 to M5 was carried out; its content now
sits in Sections 5 and 6 of the rewritten note, under the names "implemented
convention" and "right-handed convention". The RGB overlay of M5 is not part of
the note.

ID: J-010
Status: UNCERTAIN
Decision: Depth-clean gate on top of the J-005 gates
(select_perfect_frame.py --depth-clean). At each of the 8 landmark
pixels (u_int, v_int, from the scoring pass in the candidates CSV) of
every gated row, the aligned depth is sampled in a DC_WINDOW = 9 pixel
square window; per landmark: valid fraction (nonzero pixels / 81,
pixels outside the image count as invalid), median, population std and
max - min of the valid depths (metres). depth_clean8 = every window has
valid fraction >= DC_VALID_FRAC = 0.95 and std <= DC_STD_MAX_M =
0.008 m; depth_std_max8 and depth_valid_min8 are the frame-level max
std and min valid fraction. Ranking unchanged (vis_min8 desc, sharpness
desc); coarse rows are ranked too, and the best coarse-only clean
candidates get a stride-1 'fine2' pass with the default fine pass's
procedure (MediaPipe from frame 0 of the bag, +-WINDOW = 25 frames):
the literal top DC_REFINE_TOP = 5, the top 5 distinct windows, the top
REFINE_TOP = 3 distinct T-pose windows and the best head-in window.
Picks come from the fine and fine2 rows.
Why: the author's criterion that all 8 landmarks be correctly
measured: the depth at each landmark pixel must come from a clean body
surface, not an occlusion edge. The J-005 depth_ok gate (single pixel >
0) and the pipeline's 5x5 median both passed the R7_235402 frame 662
L24 edge-ramp value (J-006 amendment).
Constants and their sources: 9, 0.95, 0.008 m and 5 are the depth-clean
brief's (master, 2026-10-07). 0.008 m comes from the clean-patch stds
measured at R7_235402 frame 662: 2.2 mm on the body, 6.4 mm at L23,
against 35.8 mm at the contaminated L24 (reproduced by this stage: L23
6.362 mm, L24 35.827 mm, valid 0.802). The worker's judgement, logged
here: (1) "top 5 coarse-only" is read as the literal top 5 plus the top
5 distinct windows, because the literal top 5 were neighbours in one
window (R7_235712 #820-#840) and would refine a single stretch;
(2) coarse-only = no default fine row at the same bag and frame index;
(3) T-pose and head-in windows are added as in J-005 (3) and (5), so
those picks are not decided by the overall ranking alone; (4) the fine2
rows go to a separate file, journal/data/perfect_frame_candidates_fine2.csv
(same columns, pass = fine2), so the default run's CSV is never
modified and the stage is repeatable; (5) records are rebuilt from the
CSV rows (6 decimals) for every pass, so all picks carry the same
rounding; (6) when no row passes for a pick, its earlier JSON is kept
with a depth_clean_stage note and its own window values.
Alternatives: a depth-gradient or plane-fit residual test (not done:
no source threshold); a larger window (would reach the body outline at
the shoulders and wrists more often); exempting the wrists (not done:
the author's criterion covers all 8 landmarks).
Evidence: run of 2026-10-07 (two runs, the depth and fine2 CSVs
byte-identical, the pick JSONs identical except run time and date):
928 gated rows walked in 11.7 s, 0 hardware frame number mismatches, 0
gated rows unreached; fine2 315 rows over 4 bags (75.0 s); gated / clean
per pass: coarse 720 / 172, fine 208 / 17, fine2 278 / 102; total 90.1 s.
Overall pick R7_235500 frame 1174 (J-006 amendment), all 8 windows 100 %
valid, std 1.6 to 7.8 mm; journal/figures/perfect_frame_depth_check8.png
viewed: L11-L14 and L24 on the jacket, L23 on the shirt, L15 on a bead
bracelet at the wrist, L16 on a wristwatch face, no window on an
occlusion edge. UNCERTAIN because the thresholds are the brief's
choice, and both remaining picks pass by a small margin (overall L15
7.81 mm, head-in L23 7.999 mm against 8 mm): a threshold change of a
fraction of a millimetre changes the picks. The T-pose bag fails at
every frame (L15 window straddles the hand and the background, median
std 157 mm over the 22 rows), so no T-pose pick exists under this gate.
Reversibility: constants DC_* at the top of select_perfect_frame.py;
rerun --depth-clean (about 1.5 min).
Review: whether a bracelet (L15) and a watch face (L16) count as a
correctly measured wrist (they sit about 5 to 10 mm proud of the skin,
not measured); whether the paper needs a T-pose frame, which this gate
removes; whether 8 mm should have a margin given the two near-threshold
picks.

ID: J-011
Status: UNCERTAIN
Decision: The worked-example frame for the paper is
R7_rail_handover_earlier_take_20260908_235500.bag frame 1174 (hw 1463,
t 39.163 s): vis_min8 0.96697, sharpness 453.81, depth_std_max8 7.8 mm,
all 8 depth windows on the body (L11-L14 and L24 on the jacket, L23 on
the shirt, L15 on a bracelet, L16 on a watch face). Master adoption;
the author confirms.
Why: highest 8-landmark visibility among the frames whose 8 depth
windows are flat and on the body (J-010), and the author's criterion of
2026-10-07 that the hip depth must be correct, which this frame meets.
Alternatives: (1) R7_235402 frame 662: rejected, its L24 depth is an
edge-ramp value (1.169 m against 1.207 m on the trousers, 3.8 cm error;
J-006 amendment); (2) R5_222315 frame 204: head fully in, arms hanging,
degenerate shoulder swing of about -90 deg, kept as a second example
candidate; (3) arm_test frame 167 (T-pose): rejected, its wrist depth
windows fail J-010 (the L15 window straddles the hand and the
background).
Evidence: journal/figures/perfect_frame_depth_check8.png,
journal/figures/perfect_frame_l24_depth_check.png,
journal/data/perfect_frame.json, journal/data/perfect_frame_rejected_r7_662.json.
UNCERTAIN until the author confirms; the J-010 thresholds are the
brief's choice and this pick passes L15 by a small margin (7.81 mm
against 8 mm).
Reversibility: rerun journal/scripts/compute_angles.py on another
pick's JSON (for example perfect_frame_headin.json).
Review: the author views journal/figures/perfect_frame_overlay.png and
perfect_frame_depth_check8.png and confirms or names another frame.

ID: J-012
Status: UNCERTAIN
Decision: Method B arm convention (journal/scripts/compute_angles.py,
method_b). In the Method B root {L24*} the x axis is the subject's left,
so at rest the right upper arm points along local -x and the left upper
arm along local +x. Right arm: both segment vectors are expressed in the
Method B root basis, R_B^T (p14 - p12) and R_B^T (p16 - p14), their x
components are negated by M = diag(-1, 1, 1) (the frozen MIRROR of
v1/kinematics/shoulder.py), and the frozen right-arm solve runs on the
mirrored vectors with an identity root, solve_right_arm(0, u, u + f, I),
the call pattern of the frozen solve_left_arm. Left arm: the frozen
right-arm formulas apply directly, solve_right_arm(p11, p13, p15, R_B).
World reconstruction: right arm R_B M R_sh M with rest -x, left arm
R_B R_sh with rest +x. Root Euler: the same ZXY formulas
(euler_unity_zxy) applied to R_B, read relative to the {Camera} axes
(y down), not Unity Euler angles.
Why: the frozen swing-twist formulas (thesis eqs. 3.15-3.24,
KINEMATIC_MODEL.md sections 6, 7 and 9) assume a rest direction of local
+x, with the twist innermost about that axis and the zero-twist forearm
along local +z. Mirroring x moves the Method B right arm's rest onto +x,
so the thesis formulas, their gimbal and straight-elbow conventions and
their validation carry over unchanged and are reused by import; the only
new element is one sign flip that the thesis already uses for the left
arm. Consequence, derived and measured: since F R_A = R_B M for any
frame (shown in Section 0.6 for the T-pose, measured here as
max |R_B^T F R_A - M| = 1.1e-16 on frame #1174), the Method B root-basis
vectors equal M times the Method A root-basis vectors, so all ten arm
angles of Method B equal those of Method A (max difference 1.4e-14 deg
on frame #1174). Only the root Euler differs: x_B = -x_A, y_B = y_A,
z_B = 180 deg - z_A (wrapped).
Alternatives: (1) define Method B's own swing-twist with the right arm's
rest at -x without mirroring, R_sh = Ry Rz Rx about -x (or with Rx
replaced by a rotation about -x): rejected for now because the swing
formulas (th_z = asin(a_y), th_y = atan2(-a_z, a_x)), the twist
atan2 arguments and the anatomical signs (th_y+ backward, th_z+ up,
th_t+ internal) would all have to be re-derived and re-validated, the
thesis formulas could not be cited as they stand, and the left and right
arms would no longer share one solver; the resulting angles would differ
from the mirrored ones only by sign conventions that the paper would then
have to tabulate. (2) Mirror the left arm instead and solve the right arm
directly against -x: rejected, it needs the same re-derivation as (1)
for the right arm. (3) Solve both arms directly in R_B with rest +x:
wrong for the right arm, whose rest pose would then read th_y = 180 deg.
Evidence: journal/scripts/compute_angles.py run of 2026-10-07 on
journal/data/perfect_frame.json (21 PASS / 0 FAIL): det R_A = det R_B =
1; recompose_zxy reproduces R_A and R_B to 2.6e-16; the forward chains
above reproduce the measured upper-arm and forearm directions of both
arms in both methods (unit dot product 1 to 15 decimals); the replicated
intermediates equal the frozen solve_right_arm and solve_left_arm
outputs to 0 deg. Output: journal/data/angles_method_a.json and
angles_method_b.json. UNCERTAIN because the choice of mirroring over a
native -x parameterisation is the M3 brief's (master) and has not been
confirmed by the author; the paper's A-versus-B comparison of the arm
angles depends on it (with the mirror the arm angles are identical by
construction).
Reversibility: replace the mirrored right-arm call in method_b() of
compute_angles.py with a native -x solve and rerun (under 1 s).
Review: the author confirms that Method B's arm angles should keep the
thesis's anatomical meaning (and hence equal Method A's), rather than
carry signs native to the right-handed frame.
Annotation 2026-10-08 (J-018): the arm construction is derived in Section 5 of the
rewritten note with the rest-direction sign h of each arm (Table 4 of the note).
The section references above describe the superseded document.

ID: J-013
Status: UNCERTAIN (master decision, author to confirm)
Decision: Method B native arm solve (journal/scripts/compute_angles.py,
native_arm and method_b_native; output
journal/data/angles_method_b_native.json; the J-012 mirrored output is
kept unchanged). Root R_B and root Euler as Method B (J-002, J-008).
Rest (T-pose in {L24*}): right upper arm and forearm along local -x,
left along local +x. Swing Ry(th_y) Rz(th_z), with the frozen
_ry/_rz/_rx matrices (standard right-handed rotations). Twist th_t is
the right-handed rotation about the arm's own outward rest axis: left
+x, R_tw = Rx(th_t); right -x, R_tw = R_{-x}(th_t) = Rx(-th_t).
R_sh = Ry(th_y) Rz(th_z) R_tw, R_arm = R_B R_sh, elbow R_elb = Ry(ey)
Rz(ez) applied to the same rest direction. Zero twist: the forearm's
component perpendicular to the arm axis on local +z (thesis convention).
Right arm closed forms, a = normalize(R_B^T (p14 - p12)):
a = Ry Rz (-1,0,0)^T = (-cos th_z cos th_y, -sin th_z, cos th_z sin th_y)^T,
th_z = -asin(a_y), th_y = atan2(a_z, -a_x);
f' = Rz(-th_z) Ry(-th_y) R_B^T (p16 - p14) = Rx(-th_t) (f_par, 0, |f_perp|)^T,
so (f'_y, f'_z) = |f_perp| (sin th_t, cos th_t), th_t = atan2(f'_y, f'_z);
g = normalize(R_arm^T (p16 - p14)) = Ry(ey) Rz(ez) (-1,0,0)^T,
ez = -asin(g_y), ey = atan2(g_z, -g_x).
Left arm: the thesis formulas unchanged in R_B: th_z = asin(a_y),
th_y = atan2(-a_z, a_x), th_t = atan2(-f'_y, f'_z), ez = asin(g_y),
ey = atan2(-g_z, g_x). Gimbal (th_y := 0) and straight-elbow
(th_t := 0) conventions use the frozen GIMBAL_EPS = 1e-8 and
TWIST_EPS = 1e-6 (v1/kinematics/shoulder.py).
Why: the paper presents Method B in its own right-handed frames {L24*},
{L12*}, {L11*}, {L14*}, {L13*} so that the sign conventions of a
right-handed swing-twist appear explicitly; the J-012 mirror identity
then serves as the proof that the two methods describe the same pose.
Derived relation (u_B = M u_A in the root bases, M Ry(t) M = Ry(-t),
M Rz(t) M = Rz(-t), M Rx(t) M = Rx(t)): right arm, every native-B
angle is the negative of Method A's (th_y, th_z, th_t, ey, ez); left
arm, every angle equal. Anatomical reading on the right arm in native
B: th_z+ = down, th_y+ = forward sweep, th_t+ = external rotation,
ey in [0, 180] deg for flexion; the left arm keeps the thesis reading
(th_z+ up, th_y+ backward, th_t+ internal, ey in [-180, 0]). The
rotation matrices themselves agree: R_arm,Bn = F R_arm,A M =
R_B M R_sh,B(J-012) M.
Judgement made by the worker, logged here: the brief states both
"R_sh = Ry Rz Rx(th_t)" and "the rotation about the arm axis by th_t
equals Rx(-th_t)". The second reading (th_t about the arm's own axis)
was implemented; the JSON also records the Rx argument of R_tw (=
-th_t on the right arm, 52.745615730 deg on frame #1174). Under the
first reading (th_t = the Rx argument, th_t = atan2(-f'_y, f'_z) on
both arms) the right-arm th_t would equal Method A's instead of
changing sign; R_sh, the forward chains and the other four angles are
identical under both readings.
Alternatives: (1) the J-012 mirror (right arm mirrored to rest +x and
solved with the thesis formulas), kept as the default Method B output
and as the equivalence proof; (2) the literal Rx(th_t) twist on the
right arm (see the judgement above); (3) solving the right arm against
+x directly (wrong: rest pose reads th_y = 180 deg, J-012 (3)).
Evidence: journal/scripts/compute_angles.py run of 2026-10-07 on
journal/data/perfect_frame.json (R7_235500 frame 1174), native section
11 PASS / 0 FAIL: forward upper-arm and forearm directions of both arms
reproduced (dot = 1.000000000000000 for all four); un-twisted forearm
perpendicular part on local +z (y = -1.7e-17 right, 1.7e-18 left);
mirror identities R_arm,Bn = F R_arm,A M (2.2e-16), R_arm,Bn R_elb,Bn =
F R_arm,A R_elb,A M (2.2e-16), R_arm,Bn = R_B M R_sh,B(J-012) M (0),
left R_arm,Bn = R_arm,B (0); relation table, native B minus A (deg):
R th_y -7.914758328 -> +7.914758328 (sign), R th_z -59.223955601 ->
+59.223955601 (sign), R th_t 52.745615730 -> -52.745615730 (sign),
R ey -48.433795454 -> +48.433795454 (sign), R ez 0 -> 0 (zero, same and
sign), L th_y -45.758254667, L th_z -66.319192588, L th_t 30.376591699,
L ey -29.720937812 (all same), L ez 0 (zero). A synthetic round trip
(4000 random poses and random roots, both arms, in the worker's
scratchpad, not committed) recovered the generating angles to
4.3e-13 deg. The default run leaves angles_method_a.json and
angles_method_b.json byte-identical (md5 f26e0557b240c47b3aea7ae5cdda4579 and
a9bac779cebe87b5ae3245c1cde9213c, md5 after the 12-digit serialisation
change of build 103).
UNCERTAIN because the native parameterisation and the twist-axis
reading are the master's and the worker's choices, not confirmed by
the author.
Reversibility: the native solve is additive (native_arm,
method_b_native, NATIVE_CHECKS); dropping it or changing the twist
reading is local to those functions; rerun under 1 s.
Review: the author confirms (1) that the paper shows Method B with
native right-arm signs (th_z+ down, th_y+ forward, th_t+ external,
flexion positive) and (2) the twist reading: right-handed about the
arm's outward axis (implemented) or the literal Rx(th_t) argument.
Master decision 2026-10-07: the twist is read right-handed about the
outward arm axis (-x for the right arm), so the right-arm th_t changes
sign; author to confirm.
Annotation 2026-10-08 (J-018): the twist reading is carried into Section 5.3 of the
rewritten note unchanged; the author confirmation requested above is still
open. The section references describe the superseded document.

ID: J-014
Status: UNCERTAIN (master decision, author to confirm)
Decision: the worked example (compute_angles.py, KINEMATIC_ANGLES.md
sections 1-3) uses the raw single-frame landmarks of
journal/data/perfect_frame.json (R7_235500 #1174). The thesis Section 2.6
hip-depth preparation and the filtering are not applied.
Why: this frame's 8 depth windows were verified clean (J-010, J-011), so
the landmarks carry no depth artefact that the preparation would repair,
and the paper derivation is about the angle computation, not the
preprocessing; applying Section 2.6 would add steps that the worked
example does not need and would change the printed landmark numbers.
Alternatives: apply Section 2.6 (and the filtering) to the frame and
report both sets of angles: rejected for now to keep the derivation
short; it stays available as a follow-up.
Evidence: journal/KINEMATIC_ANGLES.md section 1.3 and
journal/figures/perfect_frame_depth_check8.png (all 8 windows 100 %
valid, std <= 8 mm, on the body).
Reversibility: rerun journal/scripts/compute_angles.py on a prepared
JSON (same schema as perfect_frame.json); the output files and the
section numbers are then regenerated.
Review: the author confirms that the raw landmarks are the right input
for the worked example, or asks for the Section 2.6 variant.
Annotation 2026-10-08 (J-018): the worked example still uses the raw single-frame
landmarks; the rewritten note states "no filtering" in Section 4.1 and gives the
frame selection no provenance (the selection record stays here and in J-005 to J-011).

ID: J-015
Status: UNCERTAIN (worker choices under the M5 brief, author to confirm)
Decision: M5 forward kinematics (journal/scripts/fk_reconstruct.py;
outputs journal/data/fk_reconstruction.json and
journal/figures/fk_reconstruction.png). Chain parameters, all measured
on the same frame (R7_235500 #1174) and held constant as a retarget
would hold them: root origin P24 ({Camera'}P24 = F {Camera}P24 for A,
{Camera}P24 for B); root rotation recompose_zxy(root Euler) (frozen,
R = Ry Rx Rz), A in {Camera'}, B in {Camera}; link offsets
{L24}P_kORG = R_meas^T (P_k - P24) for k = 23, 12, 11, with R_meas the
root built from the measured points (build_root_frame for A, the J-002
construction for B); segment lengths |P14 - P12| = 0.231026 m,
|P16 - P14| = 0.208174 m, |P13 - P11| = 0.248201 m,
|P15 - P13| = 0.232748 m; rest directions A right +x, A left -x with
local rotations M R M (the inverse of solve_left_arm), B native right
-x with R_sh = Ry Rz Rx(-t_t) (J-013), B native left +x. The chain is
the thesis homogeneous form (eqs. 3.2, 3.5, 3.6): T(frame->L24) =
[R_root | P24], T(L24->L12) = [I | offset], T(L12->L14) =
[R_sh | L_ua R_sh e], wrist at L_fa R_elb e in {L14}; Method A is
un-flipped by F before comparison and projection. Tolerances: 3D error
<= 1e-9 m per landmark and pixel error <= 1e-6 px (source: the M5
brief, float64 round-off; no measurement); sensitivity tables of A and
B native agree to <= 1e-9 m (worker's choice, the 3D tolerance reused);
sensitivity step +1 deg on one angle at a time (source: the M5 brief);
TOL_EXACT = 1e-12 for identities that hold exactly in real arithmetic (the
exact-identity tolerance reused from compute_angles.py, float64 round-off
with margin; no measurement).
Why: the offsets and lengths are the quantities a retarget fixes per
subject; taking them from the same frame isolates the angle chain, so
any residual is an error of the angles or of the FK, not of the body
model. The offsets in the measured root are (-0.199952, 0, 0) for L23
and (0.045322, 0.506635, 0) for L12 in A (x components negated in B),
exactly as the root construction implies (L23 on the root x axis, L12
in the root x-y plane).
Alternatives: (1) offsets in the Euler-recomposed root instead of the
measured root: differs by the JSON angle rounding only (recompose vs
measured root 7.5e-12 A, 9.8e-12 B); (2) Table 3.1 anthropometric
proportions or the Unity avatar's bone lengths: rejected for M5,
because they would not reproduce the measured points and the
comparison would then mix a body-model error into the angle check;
(3) the 4x4 chain only: a vector-sum form is computed as well and
agrees to 1.1e-16 m.
Evidence: fk_reconstruct.py run of 2026-10-07 on
journal/data/perfect_frame.json with angles_method_a.json and
angles_method_b_native.json, 44 PASS / 0 FAIL, 0.31 s, output
md5-identical on a second run. Reconstruction error versus the
measured {Camera} points: A max 2.98e-12 m (RMS 1.87e-12 m), max
6.4e-10 px; B native max 5.95e-12 m (RMS 3.85e-12 m), max 2.6e-9 px;
all 8 landmarks of both methods reproduced. The 1e-12 m floor is the
12-significant-digit rounding of the angle JSONs (up to 4.7e-10 deg):
the same FK on the in-memory float64 angles of compute_angles.py gives
1.4e-16 m (A) and 2.7e-16 m (B native). Sensitivity, +1 deg: the two
13 x 8 displacement tables agree to 6.8e-14 m; e.g. right wrist L16
moves 2.19 mm (th_y), 6.80 mm (th_z), 2.72 mm (th_t), 3.63 mm (ey and
ez, = 2 sin(0.5 deg) x 0.208174 m), left wrist L15 2.82, 7.93, 2.01,
4.06, 4.06 mm, root_z moves L11 by 10.12 mm. Agreement is exact in
real arithmetic: a one-angle step is a rotation about a fixed line,
the A and B native lines coincide in {Camera}, and a +-h rotation
moves a point by 2 sin(h/2) times its distance to the line.
UNCERTAIN because the tolerance values and the same-frame parameter
choice have no source beyond the brief and round-off estimates.
Reversibility: chain_params() in fk_reconstruct.py holds the
parameters; swapping in a body model or other tolerances is local;
rerun under 1 s.
Review: the author confirms that the paper reports the FK closure with
same-frame link parameters (and the 1e-12 m JSON-rounding floor, or
the 1e-16 m float64 floor), and whether the sensitivity table belongs
in the paper.
Annotation 2026-10-08 (J-018): the FK check is Section 6 of the rewritten note; the
+1 deg sensitivity tables, the tolerances and the 44 script checks are not in the
note (they stay in fk_reconstruct.py and data/fk_reconstruction.json, which is
byte-identical). Only labels of fk_reconstruct.py and its figure changed (J-018).

ID: J-016
Status: SETTLED (author instruction 2026-10-07, "I want Word")
Decision: the deliverable format of the derivation is Word,
journal/KINEMATIC_ANGLES.docx, built by journal/scripts/build_docx.py with
python-docx and writing/v9/scripts/eqn.py the way the thesis chapters are
built (build_ch3.py mechanics, build_frontmatter.py house style: Times New
Roman, black Heading 1/2/3, Letter page, 1.25 in side margins). The .md
stays the source; the .docx is regenerated from it.
Why: native Word equations (OMML) and the thesis's numbered three-column
equation table, figure and table captions, Table Grid tables and List Bullet
items give the author an editable Word file that matches the thesis.
Alternatives: pandoc route (J-017, a separate parallel track, not decided
here); hand-typed Word equations (not reproducible).
Evidence: build_docx.py run of 2026-10-07: 149 numbered + 10 unnumbered
displays, 1349 inline spans (1764 inline equation objects), 10 tables, 4
figures, 41 headings, 288 bullets, 1 code block; 1923 m:oMath = 159 + 1764;
no run contains LaTeX source; LibreOffice render 83 pages, 0 missing-operand
marks.
Translator subset and fail-loud rule: the LaTeX subset listed in the
build_docx.py docstring (Craig left indices as m:sPre, scripts, primes,
hat, frac, sqrt, norms, \left( \right), pmatrix, aligned, gathered,
mathrm/text, the symbols and spacing used by the .md); any other command,
environment, character or Markdown block raises NotImplementedError or
ValueError, nothing is dropped. Layout choices (UNCERTAIN, worker, no
source beyond the render): a display wider than the 5.1 in equation column
(estimated at 0.5 em per character) is stacked at its top-level relations,
then before a top-level matrix (55 displays), with no symbol added; an
inline span wider than 22 em is emitted as adjacent inline equations cut at
relations then operators, and table-cell math at 8 em, also after commas,
because LibreOffice cannot wrap inside an equation object; a zero-width
space opens a line or piece that starts with an operator and follows the
star of L24* etc., and bars are m:d delimiters or U+2223, because
LibreOffice's formula import otherwise draws missing-operand marks or reads
| as a logical or; figure widths 6.3 / 5.0 / 5.5 / 6.3 in; table text 10 pt
(build_ch3.py), column widths from estimated text widths.
Reversibility: rerun build_docx.py after any .md change; the constants are
at the top of the script.
Review: the author opens the .docx in Word and checks the broken displays
and the split inline equations read naturally.
Annotation 2026-10-08 (J-018, J-019): the Word toolchain of this entry is still the
deliverable route. The counts in the Evidence paragraph (83 pages, 159 displays,
10 tables, 4 figures) describe the superseded document; the rewritten document is
28 pages, 78 displays, 403 inline spans, 6 tables and 3 figures. Builder format
changes are logged in J-019.

ID: J-017
Status: SETTLED (master decision on evidence, author informed; install by
author permission 2026-10-07; the build is an alternative route, not the
deliverable)
Decision: pandoc 3.12 from the conda-forge channel lives in its own conda
env "pandoc" (/home/luo/anaconda3/envs/pandoc/bin/pandoc; installed by the
master), and journal/scripts/build_docx_pandoc.py builds
journal/KINEMATIC_ANGLES_pandoc.docx from the .md as the alternative to the
python-docx route of J-016.
Why: a separate env leaves anaconda3 base untouched; installing into base
would have upgraded conda, openssl and libgcc there (the thesis python).
The author first allowed a user-space tarball in ~/.local/bin, then asked
for anaconda instead so the local environment is not polluted; the tarball
copy (pandoc-3.12-linux-amd64.tar.gz, sha256
67d7d011fed8c8543306022b985b9b2499ab9b74818df91d8727c7e9ebc5ba06) was
removed from ~/.local/bin. The pandoc route reuses the thesis code without
copying it: build_frontmatter.apply_house_style restyles pandoc's
reference.docx, eqn.add_display_eq places each numbered display in the
three-column equation table, submission_layout.apply runs last.
Post-processing of pandoc's OMML (fix_math): Craig left indices, which
texmath writes as a script on a zero-width-space base, become m:sPre as in
build_ch3.py pre() (607); the superscript prime of Camera' becomes the run
Camera' (257); per-letter \mathrm runs are merged; 3 trailing scripts
texmath could not attach are given the element before them as base, and
"\ {}^\circ" becomes a degree sign. Reader
markdown+tex_math_dollars-smart-implicit_figures (ASCII prime kept, no
duplicate figure captions); the copy trims whitespace inside inline $..$
spans (2 spans; source line "$180^\circ - $ Method A" is otherwise
rejected by pandoc). Code-block text 9 pt: the longest code line is 73
characters, 73 x 0.6 em x 9 pt = 394 pt inside the 432 pt text width;
everything else keeps the thesis 12 pt floor.
Env reason (conda dry run): installing pandoc into base would have upgraded
conda, openssl, libgcc-ng and libgomp, so it lives in its own env. The stray
~/.local/bin/pandoc that a worker placed was removed (checked absent
2026-10-07).
Not shipped (master decision 2026-10-07): build_docx_pandoc.py stays as the
documented alternative to J-016 (m:sPre post-fix, 607 leading scripts, 0
empty bases, CODE_PT 9), but its output is not delivered because of the
three known defects above (stray "&" in aligned blocks, long math past the
margin, equal-width table columns that break words). KINEMATIC_ANGLES_pandoc.docx
is git-ignored (journal/.gitignore); the deliverable is
KINEMATIC_ANGLES.docx (J-016).
Alternatives: python-docx route (J-016, the deliverable); tarball in
~/.local/bin (withdrawn by the author); conda install into base (rejected,
upgrades base packages).
Evidence: build run 2026-10-07: 159 displays (149 numbered, 10
unnumbered), 1508 m:oMath (159 display + 1349 inline), 607 m:sPre, 0 empty
math bases, 10 data tables, 13 captions, 4 media = 4 image references; no
"$", "\tag" or "pmatrix" in run text (asserted by the script). LibreOffice
render 83 pages; pages 1, 5, 6, 14, 17, 20 and 80 viewed at 100 dpi.
Known defects (not fixed, route stopped by the master): aligned blocks keep
texmath's "&" markers, which LibreOffice draws as stray symbols (28
markers, e.g. equation (1.3)); long inline math and long displays run past
the margin or under the number column (LibreOffice cannot wrap an equation
object; J-016 splits them, this route does not); data tables use equal
column widths, so narrow columns break words (Tables 1 and 8). Upright
\mathrm text renders italic in LibreOffice in both routes (same OMML as
eqn.nor); not checked in Word.
Reversibility: delete build_docx_pandoc.py and the _pandoc.docx; remove
the env with conda env remove -n pandoc.
Review: whether the pandoc route is kept at all, given J-016 is the
deliverable.
Annotation 2026-10-08 (J-018): the pandoc route was not run on the rewritten note
in this round and is not verified on it; the deliverable is built by build_docx.py (J-016,
J-019).

ID: J-018
Status: UNCERTAIN (four open author items, listed under Review)
Decision: journal/KINEMATIC_ANGLES.md was rewritten on 2026-10-08 from
2,631 lines to 871 lines as a concise, self-contained derivation for the
supervisor, and journal/KINEMATIC_ANGLES.docx was rebuilt from it (28 pages).
Structure: 1 Purpose, 2 Landmarks, camera frame and notation, 3 The two
conventions, 4 The worked-example frame, 5 From landmarks to joint angles,
6 Forward-kinematics check, 7 Conclusion, References (Table 6 maps the
equations of the note to equations 3.1 to 3.24 of the thesis). The two
conventions are named "implemented convention" (left-handed {Camera'}, mark lh)
and "right-handed convention" (starred frames {L24*} and so on, mark rh);
Method A and Method B no longer appear in the document or in the two
figures. Dropped from the document: the status preamble, decision IDs,
checkpoint text, the frame-selection provenance and the rejected frame,
verification logs, sensitivity tables, code names and line numbers.
Figure scripts changed in labels only (make_tpose_frames_fig.py,
fk_reconstruct.py); data/fk_reconstruction.json is byte-identical.
Why: the author rejected the previous version for internal labels, repeated
material, bad format and non-derivation content (it was written by a Sonnet
worker). The new text was written by a Fable fork, built by an Opus worker,
reviewed by an Opus code-reviewer (about 330 numbers checked, 0 differing;
11 findings fixed) and an Opus cold reader (repeats, notation collisions,
undefined terms, format; fixed except the scope suggestion below), and
checked by a Sonnet checker. The note is scoped as derivation plus the
relation between the two conventions plus a short forward-kinematics check.
Alternatives: patching the 2,631-line version (rejected: the defects were
structural); a decision-first layout (open item a); keeping the Method A and
B names (replaced, open item b).
Evidence: build_docx.py run of 2026-10-08: 28 pages, 78 displays (61 numbered,
17 unnumbered), 403 inline spans, 6 tables, 3 figures, 482 m:oMath elements,
7 of 7 self-checks PASS, deterministic (sha256 of KINEMATIC_ANGLES.docx
da7cb4e9d1aec291e5e4513f577a1784f4df7b4d5bc3df946f5ad5c6ef041aa7 on two
builds). The reviewer count (about 330 numbers, 0 differing) is the reviewer's
report, not re-run by the author of this entry. Not verified: rendering in
Word; only LibreOffice was checked, and LibreOffice draws upright names
(\text, m:nor) italic where Word does not.
Reversibility: git revert of the rewrite commit restores the 2,631-line
version and its 83-page document; the figure scripts regenerate the figures.
Review (open items, all UNCERTAIN):
(a) The cold reader proposed a decision-first layout that names the downstream
consumers and moves the numeric worked example and the forward-kinematics check
to appendices. Not applied, because the author scoped the document as
derivation plus relation plus a short forward-kinematics check. The author
decides whether to restructure.
(b) The marks lh and rh and the names "implemented convention" and
"right-handed convention" were chosen by the master to replace Method A and
Method B; no source beyond that choice.
(c) Section 5.4 explains the elbow angle e_z by saying that the pipeline emits it
as a placeholder slot of the swing form R_y(e_y) R_z(e_z), always zero once the
twist is defined from the forearm. That reason is the writer's reading of the
mathematics, not a quotation from the earlier document or the thesis.
(d) References entry [1] cites the thesis without the degree name.
Annotation 2026-10-08 (J-020): the structure above (Sections 1 to 7 and the
rest-sign h) is superseded by the restructure of J-020: 1104 lines, 36 pages. The
decisions to leave out provenance, decision IDs and code names stand. Open items
(a) to (d) are not re-decided by J-020; item (a) is moot as a layout question
(the author fixed the structure) but the proposal to name downstream consumers
sits in Section 4.4 of the new text; (c) and (d) were not re-checked against the
new text by the author of this annotation.

ID: J-019
Status: UNCERTAIN (worker choices under the rewrite brief; Word rendering not
verified)
Decision: format changes to journal/scripts/build_docx.py for the rewrite:
captions above tables (below figures) with the caption kept on the same page as
its table; true minus (U+2212) in numeric table cells; a page-number footer;
core properties set (title, author Lanqing Luo, fixed dates); the real page
count written into app.xml from a LibreOffice render (needs soffice and pdfinfo
on PATH); deterministic zip timestamps; punctuation that follows an inline
equation attached to the equation so that it does not start a line; \text
emitted as m:nor; better line breaking of long displays.
Why: the author rejected the format of the previous version; the thesis puts
table captions above tables; a fixed build makes the sha256 comparable between
runs; the real page count lets Word show the right value before it repaginates.
Alternatives: leaving the previous layout (rejected by the author); building
the page count from an estimate (rejected: LibreOffice gives a measured count).
Evidence: the 2026-10-08 build (J-018): 7 of 7 self-checks PASS, same sha256
on two builds, 28 pages from pdfinfo. The 7 checks are the builder's own
(display count, tags, m:oMath count, inline pairs, no LaTeX source in runs,
figures embedded, ASCII source). Constants introduced in the builder and their sources: CELL_SCALE = 1.0 (three
variants rendered in LibreOffice on 2026-10-08, which draws cell equations at
12 pt whatever the size set; source: that test, no Word check); caption
space_before 12 pt (one text line; no source beyond the render); a space run of
at least 8 characters taken to be a \qquad gap, where the display line may be cut
(worker's choice, no source, UNRESOLVED). The rest are logic changes without new thresholds.
Not verified: Word rendering, in particular how the m:nor names and the
attached punctuation look, and whether Word paginates to 28 pages.
Reversibility: git revert of build_docx.py; the .md source is untouched by the
builder.
Review: the author opens KINEMATIC_ANGLES.docx in Word and checks the
equation lines, the table captions and the page count.
Annotation 2026-10-08 (J-021): the builder changes were extended in the
restructure round (figure widths, caption keep_together, lead-in keep with table,
header wrapping). Current build: 36 pages, 97 displays (84 tagged, 13 untagged),
548 inline spans, 9 tables, 3 figures, 646 m:oMath elements, 7 of 7 self-checks
PASS, sha256 69822f796befe448a79d41de110b5fdc5c39b91c366171aedb289767029e7ac0.
The 28-page figures in J-018 and above describe the first rewrite.

ID: J-020
Status: SETTLED (author direction 2026-10-08)
Decision: journal/KINEMATIC_ANGLES.md is restructured into two self-contained
convention sections followed by a conclusion: 1 Introduction (shared: purpose,
landmarks and {Camera} with Figure 1, notation and the thirteen angles, the
worked-example frame with Figure 2 and Table 1); 2 The left-handed convention as
implemented (2.1 flipped frame, 2.2 torso frame, 2.3 torso angles, 2.4 right
shoulder, 2.5 right elbow, 2.6 left arm through the mirror, 2.7 thirteen angles,
Table 2, 2.8 forward-kinematics check, Tables 3 and 4); 3 The right-handed
convention (3.1 to 3.8 mirroring 2.x with explicit signs, Tables 5 to 7); 4
Conclusion and comparison (4.1 side-by-side Table 8, 4.2 the F R M identity and
the angle relations, 4.3 forward-kinematics result for both with Figure 3, 4.4 what
the choice depends on); References with the correspondence Table 9. The rest sign
h is gone: each section writes its own signs, and cross-convention remarks live
only in Section 4. The text is 1104 lines and the document 36 pages, 97 displays
(84 tagged), 9 tables, 3 figures.
Why: the author directed it. The general derivation of J-018 (one construction with
the rest sign h and the mirror) made the reader hold two conventions at once and was
confusing; separate sections let each convention be read and checked alone, and the
comparison is made once, after both.
Alternatives: the general derivation with h of J-018 (rejected by the author as
confusing); a decision-first layout with appendices (J-018 item a, not chosen).
Evidence: the author's direction of 2026-10-08. Written by a Fable fork, built by Opus
workers, reviewed by an Opus code-reviewer: 962 numbers checked, 0 differing, 36
equations correct, 218 cross-references with 0 broken, 7 wording items fixed (the
reviewer's report, not re-run in this entry). Build 2026-10-08: 36 pages, 7 of 7
self-checks PASS, sha256 69822f796befe448a79d41de110b5fdc5c39b91c366171aedb289767029e7ac0.
Known minor: "180 deg minus, wrapped" wraps at a space in Table 8. Not verified:
rendering in Word.
Reversibility: git revert of the restructure commit restores the 871-line version
of J-018.
Review: the author reads Sections 2 to 4 and confirms the order and the sign
conventions written out per section.

ID: J-021
Status: UNCERTAIN (builder layout constants of the restructure round; measured in
LibreOffice only)
Decision: journal/scripts/build_docx.py FIG_WIDTH sets Figure 1
(fig1_tpose_frames.png) to 5.75 in and Figure 3 (fk_reconstruction.png) to 5.1 in;
Figure 2 stays 5.0 in; caption paragraphs get keep_together; a paragraph that ends in
":" or "as follows." keeps with the table that follows; header cells may wrap between
words, so body rows alone set the column widths.
Why: sources are the measurements recorded in the code comments. 5.75 in: LibreOffice
centres an inline picture in this column only up to 5.75 in (picture left edge by
pdftohtml: 5.5 in at 1.50 in, 5.75 in at 1.38 in, 5.9 and 6.0 in still at 1.38 in, so
a wider picture runs past the right margin at 7.25 in); the previous 6.3 in ran 0.3 in
into the margin (pdfimages: 1891 px at 300 ppi on page 2). 5.1 in: with the 1430 x 1166
px figure and its seven-line caption (13.8 pt per line) it fits on the page below the
opening of Section 4.3 with about 20 pt to spare; at 6.3 in the caption ran from page
34 onto page 35 and at 6.0 in the figure and caption moved to page 35 together. The
lead-in rule: Table 9's lead-in "... as follows." was left alone at the foot of page 35.
Header rule: with headers counted, Table 8's "Implemented (deg)" and "Right-handed
(deg)" took the width that "right shoulder elevation" and "180 deg minus, wrapped"
needed, and "out-of-plane" broke at its hyphen.
Alternatives: keeping 6.3 in (runs into the margin); the 6.0 in width for Figure 3
(moves figure and caption to the next page).
Evidence: the code comments above the FIG_WIDTH table and in the table builder; the
LibreOffice render of 2026-10-08. The margins and page breaks were not checked in
Word, where picture centring and pagination may differ.
Reversibility: edit the FIG_WIDTH constants and rerun the builder; the .md is
untouched.
Review: the author opens the .docx in Word and checks the two figure widths, the
page breaks around Figure 3 and Table 9, and the Table 8 column widths.

ID: J-022
Status: SETTLED (author instruction 2026-10-08); sub-items UNCERTAIN
Decision: a second, concise document is added beside the full note:
journal/KINEMATIC_ANGLES_SHORT.md (178 lines) built to
journal/KINEMATIC_ANGLES_SHORT.docx (5 pages). The full 36-page note
(KINEMATIC_ANGLES.md, J-020) stays unchanged. The short document is
kinematics only: numbers rounded to three decimals, degrees only, no pinhole
model, no analysis of the relation between the conventions, no forward
kinematics (one closing sentence cites the full note for it). Structure: 1 Data
(Table 1, the eight landmark positions), 2 The left-handed convention, as
implemented (equations (2.1) to (2.8), Table 2), 3 The right-handed convention
((3.1) to (3.7), Table 3), 4 Results (Table 4, the thirteen angles side by
side), References ([1] the thesis, [2] the full note).
Why: the author asked for a five-page summary of the angle computation that a
reader can follow without the proofs and checks of the full note.
Alternatives: shortening the full note in place (rejected: the author asked to keep
it unchanged); a summary that includes the relation between conventions and the
forward-kinematics check (excluded by the instruction).
Evidence: author instruction 2026-10-08. Written by the Fable fork; Opus
code-reviewer: 148 numbers checked against the full note, 0 differing, all
equations identical to the full note (the reviewer's report, not re-run in this
entry). Built by an Opus worker, then two doubled commas fixed and rebuilt by the
master. Build of 2026-10-08: 5 pages, 15 displays (all tagged), 124 inline spans,
4 tables, 0 figures, 139 m:oMath elements, 7 of 7 self-checks PASS, two builds
identical, sha256
6893a295548126c37a3e58e5247254daf707865c31a84c8eed7ca0e0ebddfbfe.
Sub-items (UNCERTAIN):
(a) Rounding rule: the three-decimal numbers are rounded half away from zero from
the six-decimal values of the full note; this is the rule the reviewer applied and
is not Python's default rounding of ties to even. The source is the reviewer's
check, not an author statement.
(b) Reference [1] is given as "Thesis, Simon Fraser University, 2026" without the
school name "School of Engineering Science" that the full note's reference [1]
carries and without the degree name (J-018 Review d is the same question for the
full note).
Not verified: rendering in Word; only LibreOffice was checked.
Reversibility: delete the two files; the full note is unaffected.
Review: the author reads the five pages and confirms the content, the rounding rule
and the form of reference [1].
Annotation 2026-10-08 (author direction): the summary must carry pictures and six
pages are acceptable. Figure 1 (figures/fig1_tpose_frames.png, Section 1) and
Figure 2 (figures/perfect_frame_overlay.png, above Table 1) are restored, so the
text above ("5 pages", "0 figures", 178 lines, the three-decimal sha256 6893a295...)
describes the first build. Current state: 188 lines, 2 figures, 4 tables, 6 pages,
7 of 7 self-checks PASS, 146 m:oMath elements, sha256
c6f3d181079139c7b976b21e5ddd23314d0466d1800606705b750f51e76e093a. The
forward-kinematics figure stays out of the summary on purpose. The 148-number
review covered the first build; the figures add no numbers to the text. Word
rendering is unverified.
Annotation 2026-10-08 (author direction, second): the summary must also show the
forward-kinematics reconstruction and compare the two results. Figure 3
(figures/fk_reconstruction.png) is added after Table 4, with a comparison paragraph
giving the maximum reconstruction errors taken from the full note: 2.98e-12 m
(left-handed) and 5.95e-12 m (right-handed). This overrides the exclusion of the
forward-kinematics check in the decision above and the previous annotation's "stays
out". Current state: 192 lines, 3 figures, 4 tables, 7 pages (six pages were not
reachable, the figure takes half a page), 7 of 7 self-checks PASS, 148 m:oMath
elements, sha256 50f87bb9b79863def5bd8bb658e3b4873dd1d25387a3ca3659341cf8c29ce63b.
The two error values were not re-checked against the full note by the author of this
annotation. Word rendering is unverified.

ID: J-023
Status: UNCERTAIN (builder changes; checked in LibreOffice only)
Decision: journal/scripts/build_docx.py builds either document: new arguments
--src and --out (defaults unchanged, so the full note still builds to sha256
69822f796befe448a79d41de110b5fdc5c39b91c366171aedb289767029e7ac0); image paths in
the source resolve relative to the source's folder; a row of a gathered or aligned
display that is wider than the display limit is flattened into its items so that it
breaks at its relations like any other line; the core-property title is the first
"# " heading of the source; it refuses --src equal to --out. Build command for the
short note:
/home/luo/anaconda3/bin/python -B journal/scripts/build_docx.py --src journal/KINEMATIC_ANGLES_SHORT.md --out journal/KINEMATIC_ANGLES_SHORT.docx
Why: the same parser, styles, self-checks, page count and deterministic zip serve
both documents, with no second builder to maintain; without the flattening, rows of
(2.2) and (3.1) of the short note ran past the right margin in the render of
2026-10-08.
Alternatives: a separate builder (rejected: duplicates the toolchain); breaking the
two displays by hand in the source (not chosen: the builder rule applies to any
note).
Evidence: both builds of 2026-10-08 print 7 of 7 PASS (full note: 36 pages, sha256
unchanged; short note: 5 pages). No new numeric constant was introduced: the
flattening reuses the existing DISPLAY_LIMIT_EM of J-016. Not verified: Word
rendering of the flattened rows, and any other note than these two.
Reversibility: git revert of the builder change; defaults restore the single-note
behaviour.
Review: the author opens both .docx files in Word and checks that the equation lines
(2.2) and (3.1) of the short note break at relations and stay inside the margins.

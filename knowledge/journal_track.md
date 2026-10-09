# Current journal notes (verified 2026-10-08)

Sources: [journal/README.md](../journal/README.md),
[journal/DECISIONS.md](../journal/DECISIONS.md), J-018 through J-023,
[journal/scripts/build_docx.py](../journal/scripts/build_docx.py).

The current full derivation is journal/KINEMATIC_ANGLES.md, restructured
into two self-contained convention sections and a comparison (J-020).
Its current Word artifact is journal/KINEMATIC_ANGLES.docx; the recorded
2026-10-08 LibreOffice build is 36 pages, superseding the 83-page build
described below. The short summary is journal/KINEMATIC_ANGLES_SHORT.md
and .docx (J-022); consult the journal README and decision annotations
for the latest short-note build and remaining author choices.

One builder serves both notes (J-023). Defaults build the full note;
explicit --src and --out select the short note:

    /home/luo/anaconda3/bin/python -B journal/scripts/build_docx.py
    /home/luo/anaconda3/bin/python -B journal/scripts/build_docx.py --src journal/KINEMATIC_ANGLES_SHORT.md --out journal/KINEMATIC_ANGLES_SHORT.docx

The recorded builds pass seven builder self-checks and were checked in
LibreOffice only. Native Word layout remains unverified. These notes
leave the thesis and frozen pipeline unchanged. The October 7 milestones
and original numerical results below are historical evidence.

## Historical journal milestones
# journal/ paper track: two root-frame conventions

Verified: 2026-10-07 (milestone 1, build 100; checker 6/6 PASS); see the end for M2 and M2b.

Sources (all opened and recomputed):
- journal/KINEMATIC_ANGLES.md (section 0, frame conventions)
- journal/scripts/make_tpose_frames_fig.py (ideal T-pose, R_A, R_B, Figure 1)
- journal/DECISIONS.md (J-001..J-004)
- v1/kinematics/root_frame.py lines 9-32 (flip F, normalize, build_root_frame)

Purpose: a paper derivation, with no step skipped, of how the 8 model
landmarks (L11-L16, L23, L24) become joint angles. The thesis and the
pipeline are not changed by this track. Figure 1: journal/figures/fig1_tpose_frames.png.

## The two constructions

F = diag(1, -1, 1) (SENSOR_TO_UNITY, the y flip of root_frame.py).

Method A (current code, thesis Chapter 3): points are flipped into the
left-handed {Camera'} (p' = F p), then
  r = normalize(p24 - p23)  (root x = L23 -> L24, subject's right)
  s = p12 - p24
  f = normalize(r x s)
  u = f x r
  R_A = [r | u | f]

Method B (J-002, SETTLED, author confirmed 2026-10-07): points stay in
the right-handed {Camera} (x right, y down, z forward), then
  x_B = normalize(p23 - p24)  (root x = L24 -> L23, subject's left)
  s = p12 - p24
  z_B = normalize(x_B x s)
  y_B = z_B x x_B
  R_B = [x_B | y_B | z_B]
Only the x column differs from A in physical {Camera}; y (subject up)
and z (subject forward, toward the camera) are the same.

## T-pose matrices (subject facing the camera)

- R_A = diag(-1, 1, -1), a proper rotation in {Camera'}.
- R_B = diag(1, -1, -1), det +1 in {Camera}.
- F R_A = diag(-1, -1, -1): A's columns in physical {Camera}, det -1
  (left-handed there).
- R_B^T F R_A = diag(-1, 1, 1): x opposite, y same, z same.
The script prints "Expectation 'same y, same z, opposite x': PASS".

## Shared-orientation rule (section 0.7)

At rest (all joint angles zero) every frame k in {11, 12, 13, 14} has
the root orientation (R_A in Method A, R_B in Method B); only the
origin moves to its landmark. So Figure 1 shows eight identical triads
per panel (the wrists L15, L16 are points; the triad there shows the
continuing arm axis). The sign of local x is what the angle sections
carry through: the right arm is along local +x in A and local -x in B.

## Perfect frame (verified 2026-10-07, milestones 2 and 2b, builds 101-102)
Source: journal/scripts/select_perfect_frame.py, journal/data/*.json,
J-005..J-011. Scan: 28 bags, 6192 frames at stride 5, 306 at stride 1,
8 min 44 s. hw = hardware colour frame number.
Rejected first pick: R7_235402 #662 (hw 952, vis_min8 0.9730). Its L24
pixel sits on the depth ramp between the trousers (1.207 m) and the right
hand (1.08 m) and reads 1.169 m, a 3.8 cm error (9x9 valid 0.802, std 35.8
mm). Kept as perfect_frame_rejected_r7_662.json; figure
perfect_frame_l24_depth_check.png.
Depth-clean gate (J-010, --depth-clean): 9x9 window at each of the 8 landmark
pixels, valid >= 0.95, std <= 8 mm (brief's choices, not measured), added to
the J-005 gates (vis_min8 >= 0.9, 3 % margin, depth > 0, ranking vis_min8
then sharpness, T-pose tpose <= 0.15). Stage 90 s, deterministic over two runs; gated/clean per pass: coarse 720/172, fine
208/17, fine2 278/102.

| Pick | Bag | Frame | hw | vis_min8 | sharpness | depth_std_max8 |
|---|---|---|---|---|---|---|
| overall (J-011) | R7_..._20260908_235500 | 1174 | 1463 | 0.96697 | 453.81 | 7.8 mm (L15) |
| head in | R5_..._20260825_222315 | 204 | 494 | 0.95553 | 554.34 | 7.999 mm (L23) |
| T-pose | none | - | - | - | - | all 22 rows fail at L15 |

Overall pick: t 39.163 s, all 8 windows 100 % valid and on the body
(L11-L14, L24 jacket; L23 shirt; L15 bracelet; L16 watch face); top of head
at the image edge. Head-in R5 #204: arms hanging, degenerate shoulder swing
of about -90 deg, second example candidate. T-pose bag fails everywhere (L15
window straddles hand and background). Both picks pass by a small margin.
J-011 is UNCERTAIN until the author confirms.
Files: journal/data/perfect_frame{,_headin,_tpose,_rejected_r7_662}.json,
perfect_frame_candidates_{depth,fine2}.csv, perfect_frame_candidates.csv
(18 MB, local only, git-ignored); journal/figures/perfect_frame_{,headin_}
rgb.png, _overlay.png, perfect_frame_depth_check8.png, candidates_contact.png.
J-008 (UNCERTAIN, master): Method B applies no y-flip, stays in {Camera}
(F has det -1; a y-up frame is diag(1,-1,-1) applied to the result).
J-009 plan: M3 Method A angles, M4 Method B angles and A-vs-B table, M5
forward kinematics for both, 8-point reconstruction, per-landmark error.

## Angles (verified 2026-10-07)

Milestone 3 (build 103): journal/scripts/compute_angles.py runs the
frozen v1 solvers on R7_235500 #1174 (journal/data/perfect_frame.json,
raw landmarks, J-014); 21 PASS / 0 FAIL, native Method B 11 PASS / 0 FAIL.
Method A angles (deg):
- root Euler (x, y, z): -12.168671, 174.290572, 1.212494
- right shoulder (th_y, th_z, th_t): -7.914758, -59.223956, 52.745616
- right elbow (ey, ez): -48.433795, 0
- left shoulder (th_y, th_z, th_t): -45.758255, -66.319193, 30.376592
- left elbow (ey, ez): -29.720938, 0
Method B, J-012 mirror: all ten arm angles equal Method A; root x
negated, root y equal, root z = 180 - A.
Method B, J-013 native (right arm rest along -x, twist right-handed
about the outward axis, master decision, author to confirm): the five
right-arm angles are the negatives of A, the left arm equals A, root as
in J-012 (x negated, z = 180 - A).
Mirror identity: R_arm,B = F R_arm,A M, M = diag(-1,1,1), holds to 2.2e-16.
Files: journal/data/angles_method_a.json, angles_method_b.json,
angles_method_b_native.json; journal/KINEMATIC_ANGLES.md sections 1-2
(sections 3-5 follow, see FK below); decisions J-012, J-013, J-014.

## FK (verified 2026-10-07)

Milestone 5 (build 104): journal/scripts/fk_reconstruct.py rebuilds the 8
landmarks of R7_235500 #1174 from the angle files with the thesis
homogeneous chain (J-015); 44 PASS / 0 FAIL, 0.31 s, deterministic.
Errors versus the measured {Camera} points: Method A max 2.98e-12 m, B
native max 5.95e-12 m (floor = 12-significant-digit angle JSONs); with the
in-memory float64 angles 1.4e-16 m (A) and 2.7e-16 m (B native). The +1
deg sensitivity tables (13 angles x 8 landmarks) of A and B agree to
6.8e-14 m (exact in real arithmetic: the rotation lines coincide in
{Camera}); e.g. right wrist L16 moves 6.80 mm per +1 deg of th_z.
Sections 3-5 of KINEMATIC_ANGLES.md written; checker found 13 angles
matching to 4.6e-7 deg and FK to 5e-12 m; all R_A/R_B shorthand replaced
by Craig symbols (only the Figure 1 caption sentence and JSON key names
keep the script names).
Files: journal/scripts/fk_reconstruct.py, journal/data/fk_reconstruction.json,
journal/figures/fk_reconstruction.png; decisions J-015 (TOL_EXACT = 1e-12).

## Word build (verified 2026-10-07)

The deliverable is journal/KINEMATIC_ANGLES.docx, built from
KINEMATIC_ANGLES.md by journal/scripts/build_docx.py (python-docx plus
writing/v9/scripts/eqn.py, thesis house style; J-016). Counts: 159 display
equations (149 numbered, 10 unnumbered), 1349 inline spans, 4 figures, 10
tables, 7 builder self-checks PASS; LibreOffice render 83 pages (pages 66
and 81 viewed: table headers do not split words). Not yet opened in Word by
the author. Run: python -B journal/scripts/build_docx.py (thesis python).
Alternative (J-017, not shipped): journal/scripts/build_docx_pandoc.py, pandoc 3.12 in conda env "pandoc"
(/home/luo/anaconda3/envs/pandoc/bin/pandoc, separate env so base conda is
not upgraded); output KINEMATIC_ANGLES_pandoc.docx is git-ignored. Defects:
stray "&" in aligned blocks, long math past the margin, equal-width table
columns that break words.

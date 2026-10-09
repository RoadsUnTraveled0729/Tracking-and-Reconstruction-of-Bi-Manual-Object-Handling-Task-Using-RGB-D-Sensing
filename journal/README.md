# Journal paper track (journal/)

## Purpose

This folder prepares a journal paper derived from the thesis
(writing/v9). Its first part is KINEMATIC_ANGLES.md, a concise,
self-contained note for the supervisor that derives how the kinematic
model turns the eight body landmarks (L11-L16, L23, L24) into the
thirteen joint angles of the torso-and-arms skeleton. The derivation is
carried out twice from the same recorded frame: in the implemented
convention (the thesis Chapter 3 pipeline: points flipped into the
left-handed {Camera'}, torso x axis along L23 -> L24, mark lh) and in a
right-handed convention (no flip, starred frames {L24*} and so on, torso
x axis along L24 -> L23, mark rh). The note proves how the two sets of
angles are related and closes with a short forward-kinematics check. It
supports a decision on which convention the pipeline should use when its
angles feed right-handed tools. The thesis and the pipeline are not
changed by this track.

Two documents come from this work, both on the same eight landmarks and
the same worked-example frame (J-022):

- KINEMATIC_ANGLES.docx, the full note (36 pages, from KINEMATIC_ANGLES.md,
  1104 lines): the complete derivation with every intermediate quantity, the
  relation between the two conventions and a forward-kinematics check.
- KINEMATIC_ANGLES_SHORT.docx, the summary (7 pages, from
  KINEMATIC_ANGLES_SHORT.md, 192 lines): kinematics only, three figures (the
  T-pose frames, the worked-example frame with its landmarks and the
  forward-kinematics reconstruction), numbers rounded
  to three decimals, degrees only, with no pinhole model and no analysis of the
  relation between the conventions; it shows the forward-kinematics
  reconstruction (Figure 3) and compares the maximum errors of the two
  conventions, and cites the full note for the derivation of the check. Structure: 1 Data (Table 1, the landmark positions);
  2 The left-handed convention, as implemented (equations (2.1) to (2.8),
  Table 2); 3 The right-handed convention ((3.1) to (3.7), Table 3);
  4 Results (Table 4, the thirteen angles side by side); References ([1]
  the thesis, [2] the full note).

The full note was rewritten on 2026-10-08 (J-018): the previous version ran
to 2,631 lines with internal labels, repeated material and a status
preamble, and was rejected by the author. It was then restructured on the
author's direction into two self-contained convention sections and a
comparison (J-020). The current text is 1104 lines.

## Status

Exploratory. The short summary KINEMATIC_ANGLES_SHORT.docx (7 pages, 15
numbered displays, 4 tables, 3 figures) passed the builder's 7 self-checks, and its
build is deterministic (sha256
50f87bb9b79863def5bd8bb658e3b4873dd1d25387a3ca3659341cf8c29ce63b); its
numbers were checked against the full note (148 numbers, 0 differing,
reviewer's report) and its rounding rule and reference [1] await the
author (J-022). The full Word deliverable KINEMATIC_ANGLES.docx (36 pages) is
built from KINEMATIC_ANGLES.md (36 pages, 97 displays of which 84 are
numbered, 9 tables, 3 figures) and has passed the builder's 7 self-checks;
its build is deterministic (sha256
69822f796befe448a79d41de110b5fdc5c39b91c366171aedb289767029e7ac0 on
the 2026-10-08 build). Rendering was checked in LibreOffice only. The
author has not yet opened the document in Word, so equation line
breaks, table captions and the page count are not verified there
(J-019, J-021, J-023). Four items from the first rewrite await the author's decision (J-018
Review a to d): a decision-first layout with appendices (moot as a layout
question since the author fixed the structure, J-020), the convention
names and marks, the stated reason for the always-zero elbow angle e_z,
and the form of reference [1]. Earlier open calls remain as logged in
DECISIONS.md (for example J-013 twist reading, J-014 raw landmarks,
J-015 same-frame link data), each marked UNCERTAIN there.

Document structure (J-020): 1 Introduction, shared (purpose, landmarks
and the sensor frame {Camera} with Figure 1, notation and the thirteen
angles, the worked-example frame with Figure 2 and Table 1); 2 The
left-handed convention as implemented (flipped frame, torso frame, torso
angles, right shoulder, right elbow, left arm through the mirror, the
thirteen angles in Table 2, forward-kinematics check in Tables 3 and 4);
3 The right-handed convention (Sections 3.1 to 3.8 mirror Section 2 with
the signs written out, Tables 5 to 7); 4 Conclusion and comparison
(4.1 the angles side by side in Table 8, 4.2 the relation between the
two torso frames, equation (4.4), and between the angle sets, 4.3 the
forward-kinematics result for both with Figure 3, 4.4 what the choice
depends on); References, with Table 9 mapping the equations of the note
to the thesis equations 3.1 to 3.24. Each convention section writes its own
signs; cross-convention remarks appear only in Section 4. All formulas use
Craig notation as printed in thesis Chapter 3.

## Design decisions

- The track stays inside journal/ and imports the frozen v1/kinematics
  code instead of copying it (J-001).
- The right-handed convention applies no y-flip and keeps all points in
  the sensor frame {Camera}; only the hip axis is reversed (J-002, J-008).
- Frames of the right-handed convention carry a star and all formulas use
  the thesis Craig notation (J-007); the conventions are named
  "implemented" and "right-handed" with marks lh and rh (J-018).
- The worked example is one frame, R7_235500 #1174, chosen with a depth-clean
  gate and used with raw single-frame landmarks (J-005, J-006, J-010,
  J-011, J-014).
- Forward kinematics uses link offsets and lengths measured on the same
  frame, so the check isolates the angle chain (J-015).
- The note has two self-contained convention sections followed by a
  comparison, at the author's direction; the general derivation with a rest
  sign h was rejected as confusing (J-020).
- The summary is a separate seven-page document, with three figures (Figure 1 in Section 1, Figure 2 above Table 1, Figure 3 after Table 4), that leaves the full note
  unchanged (J-022).
- The deliverable is Word, built from the Markdown source with python-docx
  and the thesis equation module (J-016, J-019); figure widths and table
  layout rules are measured in LibreOffice (J-021); the pandoc route is an
  unshipped alternative (J-017).

## Results

Conditions: one frame, R7_235500 #1174, raw landmarks; numbers from journal/data/*.json via
scripts/compute_angles.py and scripts/fk_reconstruct.py.

- The two torso frames are related in every pose (Section 4.2 of the
  note, equation (4.4)); the thirteen angles of the two conventions are
  related as in Table 8 of the note.
- Implemented convention: torso (pitch, yaw, roll) = (-12.168671,
  174.290572, 1.212494) deg; right shoulder (azimuth, elevation, twist) =
  (-7.914758, -59.223956, 52.745616), right elbow flexion -48.433795;
  left shoulder (-45.758255, -66.319193, 30.376592), left elbow flexion
  -29.720938 (data/angles_method_a.json). Right-handed convention: the
  torso pitch and the four nonzero right-arm angles change sign, the torso yaw and
  the left arm are equal, and the torso roll is 180 deg minus the
  implemented value, wrapped (data/angles_method_b_native.json; the
  file names keep the earlier Method A/B labels).
- Each set of angles rebuilds the eight landmarks to within 6e-12 m (the
  rounding floor of the 12-digit angle files; 1.4e-16 m and 2.7e-16 m with
  in-memory float64 angles, data/fk_reconstruction.json).
- What did not work: the first worked-example pick R7_235402 #662 was
  rejected because L24 depth lay on a hand edge ramp (3.8 cm error, J-006
  amendment, J-010); no T-pose frame passes the depth-clean gate.
- Not verified: Word rendering; the pandoc route on the rewritten note.

## Limitations

- One frame of one recording; the check does not validate the landmarks
  or the body model, because the link data come from the same frame.
- The note does not apply the thesis Section 2.6 hip-depth preparation or
  any filtering (J-014).
- Both torso readings pass through the arctangent discontinuity at +-180
  deg in normal use; the right-handed roll of an upright torso sits near
  180 deg, so the angles are not zero at the rest pose.
- The summary leaves out the relation between the conventions and the
  details of the forward-kinematics check (chain, link data, Tables 3 and
  4 of the full note); read the full note for them.
- Word rendering is unverified; LibreOffice draws upright names italic.
- The author has not yet chosen between the two conventions; the note
  states that the choice is one of downstream, not of accuracy.

## Layout

- DECISIONS.md: decision log, prefix J-001 (J-018 to J-023 for the
  2026-10-08 rewrite, builder changes, restructure, layout constants, short
  summary and the two-document builder).
- KINEMATIC_ANGLES.md: the source of the full note (1104 lines).
- KINEMATIC_ANGLES_SHORT.md: the source of the summary (192 lines);
  KINEMATIC_ANGLES_SHORT.docx: the summary, 7 pages (J-022).
- KINEMATIC_ANGLES.docx: the deliverable (Word, native equations, 36
  pages), built from the .md by scripts/build_docx.py (J-016, J-019, J-021).
- scripts/build_docx.py: Markdown and LaTeX-subset reader that emits the
  .docx with python-docx and writing/v9/scripts/eqn.py in the thesis house
  style; fails loudly on any construct outside its subset; needs soffice
  and pdfinfo on PATH to write the page count.
- scripts/build_docx_pandoc.py: the alternative builder (J-017), pandoc
  from /home/luo/anaconda3/envs/pandoc/bin/pandoc plus python-docx
  post-processing; writes KINEMATIC_ANGLES_pandoc.docx (git-ignored, not
  shipped, not run on the rewritten note).
- scripts/make_tpose_frames_fig.py: builds the ideal T-pose from the thesis
  Table 3.1 proportions, computes both root matrices (the implemented one
  imported from v1/kinematics/root_frame.py), prints them and their
  relation, and draws Figure 1 (figures/fig1_tpose_frames.png).
- scripts/compute_angles.py: solves the thirteen angles for both
  conventions (J-012, J-013, J-014); data/angles_method_a.json (implemented
  convention), angles_method_b.json (J-012 mirror) and
  angles_method_b_native.json (right-handed convention, J-013).
- scripts/fk_reconstruct.py: forward kinematics of both conventions from
  the angle files, 8-landmark reconstruction and +1 deg sensitivity tables
  (J-015); data/fk_reconstruction.json: its numbers (the note uses the
  reconstruction error only); figures/fk_reconstruction.png: Figure 3.
- scripts/select_perfect_frame.py: selects the worked-example frame from the
  28 recordings (J-005, J-006, J-010): MediaPipe on every 5th frame, gates
  and ranking, a stride-1 refinement pass and the depth-clean stage.
- data/perfect_frame.json: the pick R7_235500 #1174 (bag, frame index,
  hardware frame number, timestamp, colour intrinsics and depth scale, all
  33 landmarks, the 8 model landmarks' depth and xyz, scores, run
  settings). figures/perfect_frame_overlay.png: Figure 2 of the note, the
  8 landmarks on the colour frame; figures/perfect_frame_rgb.png: the
  untouched colour frame; figures/perfect_frame_depth_check8.png: the 8
  depth windows.
- Selection records, not used in the note: data/perfect_frame_tpose.json
  and data/perfect_frame_headin.json (alternatives found by the scan, with
  their _rgb and _overlay figures), data/perfect_frame_rejected_r7_662.json
  and figures/perfect_frame_l24_depth_check.png (the rejected pick),
  data/perfect_frame_candidates_depth.csv and _fine2.csv (depth-window
  values of the gated rows and the stride-1 pass),
  figures/candidates_contact.png (best frame of the top 12 candidate
  windows). data/perfect_frame_candidates.csv (every scored frame, about
  18 MB) is local only: git-ignored through journal/.gitignore,
  regenerated by select_perfect_frame.py.

## How to run

Word document (deliverable; prints the counts, the page count (36) and 7 PASS
lines; requires soffice and pdfinfo on PATH; deterministic, so the sha256
of the output above reproduces):

    /home/luo/anaconda3/bin/python -B journal/scripts/build_docx.py

It reads KINEMATIC_ANGLES.md and writes KINEMATIC_ANGLES.docx. The Word
rendering has not yet been verified by the author.

The seven-page summary (prints 7 pages and 7 PASS lines; sha256 above):

    /home/luo/anaconda3/bin/python -B journal/scripts/build_docx.py --src journal/KINEMATIC_ANGLES_SHORT.md --out journal/KINEMATIC_ANGLES_SHORT.docx

Both builds are deterministic. Word rendering of either document has not
yet been verified by the author.

The alternative pandoc build (not shipped, J-017):

    /home/luo/anaconda3/bin/python journal/scripts/build_docx_pandoc.py

Forward-kinematics reconstruction (milestone 5, needs only the committed
angle files and perfect_frame.json; under 1 s, prints 44 PASS lines):

    /home/luo/anaconda3/bin/python journal/scripts/fk_reconstruct.py

It writes journal/data/fk_reconstruction.json and
journal/figures/fk_reconstruction.png deterministically.

From the repository root, with the thesis interpreter (numpy,
matplotlib):

    /home/luo/anaconda3/bin/python journal/scripts/make_tpose_frames_fig.py

It prints the landmark positions, R_A, R_B, their determinants and
the column-by-column comparison, ends with
"Expectation 'same y, same z, opposite x': PASS", exits 0, and writes
journal/figures/fig1_tpose_frames.png. It is deterministic and reads
no recording.

Perfect-frame selection (needs the local recordings/ bank, mediapipe
0.10.15 and pyrealsense2 2.55.1 in the same interpreter; about 9 min,
CPU):

    /home/luo/anaconda3/bin/python journal/scripts/select_perfect_frame.py

It logs one [BAG] line per recording, the refinement windows, the
[PICK], [TPOSE] and [HEADIN] frames and the run time, and writes the
journal/data/ and journal/figures/ files listed above. Adding
--figures-only redraws the overlay PNGs from the saved JSON and RGB
files without reading the bags.
Adding --depth-clean (after the default run, about 1.5 min) applies the J-010 9x9 depth-window gate (data/perfect_frame_candidates_depth.csv, a stride-1 fine2 pass in data/perfect_frame_candidates_fine2.csv) and rewrites the picks, figures/perfect_frame_depth_check8.png and candidates_contact.png; the rejected R7 #662 record is data/perfect_frame_rejected_r7_662.json.

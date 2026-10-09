# Frame overlays on faded photographs (round 8, M2a, build 64 part 1)

Producer: presentation/defense_2026/make_frame_overlay_figures.py.
Run from the repository root with /home/luo/anaconda3/bin/python:
`--measure-tpose` (writes tpose_landmarks_mediapipe.json), then no
arguments (renders the six PNGs and manifest.json). Specs:
spec_<name>.json in this folder. Not committed; decisions below are
for the master to move into DECISIONS.md.

## Overlay mode per frame

| Figure | Frame | Mode | Pose / anchor source |
|---|---|---|---|
| overlay_camera_frames | Camera, Camera-prime | illustrative | corner legend; directions are the image axes by definition (Eq. 3.1) |
| overlay_landmark_frames | L11-L16, L23, L24 | measured points (no triads) | tpose_landmarks_mediapipe.json (MediaPipe heavy model on tpose_source.jpg) |
| overlay_torso_root | root L24 | illustrative (anchor measured) | anchor = MediaPipe L24; X, Y built in the image plane from L23, L24, L12 (Eqs. 3.7-3.10); Z drawn as a toward-viewer ring |
| overlay_object_world | World | projected | eval/output/scene_calibration_r6bc.json T_cam_desk; intrinsics eval/output/recording_20260831_065553_aruco_raw_scaled.meta.json |
| overlay_object_world | Object | projected | eval/output/recording_20260831_065553_aruco_raw_scaled.csv frame 505, marker 1 |
| overlay_object_world | Wall | projected | eval/output/scene_calibration_r6bc.json T_cam_wall (wall marker id 0, 150 mm; thesis WallCameraR, Section 2.2.2) |
| overlay_object_world | Camera | illustrative | corner legend (upper right since round 9) |
| overlay_scene_mapping | World | projected | as above |
| overlay_scene_mapping | Scene | projected directions, translated anchor | G from scene_calibration_r6bc.json gravity_up_unity, S of Eq. 6.1, tf from eval/output/unity_check_r6b_v9/unity_person_log.csv frame 505; drawn at the desk-marker origin |
| overlay_rig_frames | L24 root, L14, L16 | projected | angles eval/output/unity_check_r6b_v9/integrated_stream.csv frame 505; origins = rig joints in unity_person_log.csv frame 505; camera pose scene_calibration_r6bc.json |

The unity_check_r6b_v9 logs are byte-identical to
writing/v9/figures/src/r6b_unity_sensor/ (same capture as
r6b_unity_f00505.png, commit 00ae8f4).

## Checks (manifest.json reprojection_checks)

- World origin vs desk marker detected on the deck copy of frame 505: 0.72 px.
- Object origin vs cube marker detected: 0.02 px.
- Wall origin (T_cam_wall) vs wall marker (id 0) detected: 0.08 px.
- Unity camera model, World origin vs page-24 desk anchor (345.5, 443.0): 2.88 px.
- Unity camera model, rig hip vs page-24 pelvis sphere (340.0, 347.7): 3.61 px.
- Bound (D-303, round-9 code review M4): the generator raises when the World,
  Object or Wall residual exceeds 1.0 px (manifest.json
  reprojection_checks.residual_bound_px; the value was set by the review brief).
  The two Unity checks compare with hand-measured anchors and carry no bound.
- tf from the log = (0, 0.716215, 0) m; thesis Section 6.4 gives d = 71.6 cm.
- L14 and L16 first axes vs the rendered bone direction: 0.000 deg.
- Fade: base maximum 128 on every photo panel (255 x 0.5 rounded).

## Decisions

N-1 (SETTLED) Canvas 1440 x 1200 px, the size of the existing schematics
in figures/coordinate_frames/, so the PNGs drop into the frame_figure box
of build_deck.py (6.61 x 5.00 in, or 6.61 x 4.75 in with a three-line
caption). Single photographs (640 x 480) fill 1440 x 1080 at the top with
a 120 px black band below for one legend line.

N-2 (SETTLED) Label size 57 px, DejaVu Sans (build_deck.py TYPEFACE):
ceil(16 / 72 x 1200 / 4.75) = 57, the worst of the two boxes. Effective
17.1 pt in the 5.00 in box and 16.25 pt in the 4.75 in box
(knowledge/deck_fonts.md rule). Every text uses this size; the producer
fails when two labels overlap or a label leaves the canvas.

N-3 (SETTLED) Fade = rint(resized photo x 0.5), overlays drawn afterwards,
as eval/failure/make_label_compare_fig.py render_panel with --fade 0.5.
Resampling cv2.INTER_CUBIC when enlarging (as page 30), INTER_AREA when
shrinking (T-pose photo).

N-4 (UNCERTAIN) The T-pose landmark anchors are measured with MediaPipe
PoseLandmarker (v1 heavy model, IMAGE mode, CPU, confidences 0.3 as in
v1/mediapipe/extract_landmarks_to_csv.py) because no manifest records
landmark pixels for tpose_source.jpg: the coordinate_frames manifest has
schematic-canvas pixels only, and the 01d023a manifest had one manual
pointer. The measurement is deterministic across two runs. Review: that
the L14 elbow (about 25 source px below the L12-L16 line) and L16 wrist
positions look right to the author.

N-5 (SETTLED) Projected axis lengths are display choices, not
measurements: 0.09 m for World and Object on overlay_object_world (twice the 45 mm print),
0.30 m for Wall (twice the 150 mm wall print, the same rule),
0.12 m on overlay_scene_mapping and for the rig root, 0.09 m for L14 and
L16. Illustrative legends: 230 px (camera), 200 px (torso root).

N-6 (UNCERTAIN) Unity view camera model: pinhole with f = 240 /
tan(fov_y / 2) from sensor_fov_y_deg of scene_calibration_r6bc.json,
principal point (320, 240), square pixels, at the calibrated camera pose
(ArucoSceneReceiver.cs pov.fieldOfView, thesis Section 6.4). Supported by
the 2.88 px and 3.61 px checks above; the Unity sub-pixel convention was
not read from Unity itself.

N-7 (SETTLED) Scene axes on overlay_scene_mapping are drawn at the
desk-marker origin; the true Scene origin (0.716 m below along gravity)
projects to about v = 1306 px, outside the 480 px view. The figure text
says so.

N-8 (UNCERTAIN) Rig segment rotations are rebuilt from the streamed
angles exactly as IntegratedSceneReceiver.cs does (root Ry Rx Rz; right
shoulder Ry Rz Rx; right elbow Ry Rz) and carried to the camera by F; only
the right arm chain (L14, L16) is drawn, as in Eq. 6.4. The Y and Z axes
of L14 and L16 depend on the held twist and are not checked against any
rendered geometry; only the first axes are (0.000 deg).

N-9 (SETTLED) Camera and Camera-prime legends share the optical origin but
are drawn apart at the upper-left corner for legibility; Z into the
scene is a ring with a cross, Z toward the viewer a ring with a dot.

## Known visual limits

- overlay_object_world and overlay_scene_mapping: the World Y and Z axes
  project almost onto the same upward image line (the desk card leans back
  on its stand and the camera looks down on it); this is the true
  projection, labels are separated left and right.
- overlay_rig_frames: the root Z axis points almost along the line of
  sight and projects to about 13 px.

## Round 9: Wall frame on overlay_object_world (page 18)

N-10 (SETTLED) Author request 2026-09-30: page 18 labels the wall
marker. The Wall frame is projected from the calibrated pose T_cam_wall
of eval/output/scene_calibration_r6bc.json (pose type
calibration_marker, key T_cam_wall), the same calibration that gives
World; no per-frame detection was needed. The pinned detector (as in
reprojection_checks) finds id 0 on the deck copy of frame 505 at corner
mean (118.79, 154.56) px; T_cam_wall projects to (118.72, 154.52) px,
0.08 px apart. Its Y axis is the in-plane up axis that the calibration
takes as gravity (Section 2.2.2). Z points almost at the camera, so it
projects to a short arrow up and to the left.

N-11 (SETTLED) The Camera legend moved from the upper-left to the
upper-right image corner because the wall marker sits under the old
legend. The legend is illustrative (directions are the image axes), so
its anchor carries no measurement.

## Round 10 (build 70): plain diagram panels and the page-7 static markers

Overlay modes of the changed and new figures:

| Figure | Frame | Mode | Pose / anchor source |
|---|---|---|---|
| overlay_camera_frames | Camera, Camera' | illustrative | plain panel, one shared origin as thesis Figure 3.2; directions by definition (Eq. 3.1) |
| overlay_torso_root | root L24 | illustrative (anchor measured) | unchanged left panel, crop [1540, 600, 2490, 2100] at the same 0.8 scale |
| overlay_torso_root | Camera' (top view), root L24 (top view) | illustrative | plain right panel, nominal geometry of Section 3.2.2 (R = diag(-1, 1, -1)), not a measurement |
| overlay_static_markers | World, Wall | projected | T_cam_desk and T_cam_wall of eval/output/scene_calibration_r6bc.json on media/matched/r6b_frame_533.jpg, recording intrinsics |

N-12 (UNCERTAIN, D-316) Plain panels: "background": "plain" in a panel spec draws
no photograph (black, the deck background 000000); only illustrative frames,
outline shapes and texts may sit on it, and each of their labels must stay in
the panel. The manifest panel row says background plain and has no photo
fields; validate_deck.py checks exactly that.

N-13 (SETTLED, D-317) A spec may set canvas_px. overlay_torso_root uses
1586 x 1200 px (the 6.61 x 5.00 in box aspect), so the 57 px label is 17.1 pt;
the generator raises when a canvas would put labels below 16 pt.

N-14 (UNCERTAIN, D-317) Top view: Y (up) points at the viewer and is drawn as
the ring with a dot (z_symbol_axis Y); arrows 230 px (Camera') and 200 px
(torso), the N-5 legend lengths. Outlines are display constants.

N-15 (UNCERTAIN, D-318) Frame-533 checks: World origin vs desk marker 0.71 px,
Wall origin vs wall marker 0.03 px (pinned detector on the JPEG still), both
under the D-303 1.0 px bound, which now applies to them.

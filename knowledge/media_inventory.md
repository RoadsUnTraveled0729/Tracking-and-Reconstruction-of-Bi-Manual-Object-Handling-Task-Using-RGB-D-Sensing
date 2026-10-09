## Final deck media (Verified 2026-10-06)

Sources: presentation/defense_2026/Thesis_Defence_2026.pptx (zipfile scan of ppt/media
and of the slide relationship files), package/MANIFEST.json, DECISIONS.md D-381,
D-383, D-385, D-387, D-389, D-390, D-392, D-393.

Slide 12 film (Verified 2026-10-06, D-387): media/p12_chain_growth.mp4 (1440 x
1200, h264 yuv420p, 30 fps, 240 frames = 8.0 s, sha256 c3c72c7c...; generator
anim/chain_growth.py, poster media/p12_chain_growth_poster.png = last frame,
provenance media/provenance/p12_chain_growth.json) is embedded on slide 12 as
ppt/media/p12_chain_growth.mp4 with poster ppt/media/p12_chain_growth.png by
anim/patch_slide12_video.py, in slide 13's movie convention; image10.png (the
old static figure) was removed. validate_media.py EXPECTED_SECONDS lists it at
240/30; only its inspect() was run on it (PASS), the full run still needs the
/tmp/defense_2026_causal cache.

The author's pptx had 148 media files in ppt/media (123 PNG, 25 MP4); with the
slide 12 film it had 149 (123 PNG, 26 MP4); after D-389 removed the slide 35
left-wrist picture ppt/media/image50.png (r5_label_compare_f1462.png) it has 148
(122 PNG, 26 MP4); D-390 added ppt/media/p33_fk_overlay.png (sha256 8f34fb02...)
and ppt/media/p34_masked_comparison.png (sha256 2181352b...), so it had 150 (124
PNG, 26 MP4). D-392 replaced the part p34_masked_comparison.png by the three-case
figure (sha256 32c88095..., 1500 x 1155, media/provenance/p34_masked_comparison.json).
D-393 added ppt/media/p33_three_panel.mp4 (sha256 5057b413..., 1440 x 640, 30 fps,
1498 frames, 49.93 s, 8,044,512 B; generator anim/three_panel_fk.py, provenance
media/provenance/p33_three_panel.json) and ppt/media/p33_three_panel.png (poster =
frame 630, sha256 dc091a6c...), and removed media15.mp4, image48.png and
p33_fk_overlay.png. It now has 149 (123 PNG, 26 MP4), 0 external relationships (zip listing 2026-10-06;
package/MANIFEST.json embedded_mp4_videos 26). A name scan
of the author's slide relationship files found MP4 links on 24 slides (shown: 4,
7, 8, 9, 10, 13, 14, 15, 20, 22, 23, 24, 25, 26, 27, 30, 33, 37, 38, 41; hidden:
51, 52, 53, 75; slide 12 is now added) with 23 distinct MP4 names, so two MP4 files of the 25 are not linked by name
from a slide relationship (not investigated). Slide 23 carries the synchronized
flat-circle film and slide 38 the native Unity recording (author, 2026-10-05).
The deck has no GIF. Playback was not verified outside the author's PowerPoint
review (D-383).

The media_contract.json, the round-3 to round-11 committee_materials trees (all
except unified_four/provenance, four JSON files) and presentation/v9/videos were
deleted in 3dbd345 (D-385), so the contract chain below no longer exists. The media/
folder (117 files, 45 MP4 masters), anim/ generators and unity_capture/ remain;
anim/recorded_context.py and media/provenance/recorded_context.json still cite
deleted presentation/v9 paths (D-385).

## RETIRED (history): media of the generated decks, rounds 4 to 11

Every section below describes media bound by the retired media contract of the
generated decks (builds up to 77; recover at 85078c9 or 87e87ae). Page numbers
are those of the round named in each heading, not of the final deck.

## Round-10 media (builds 68-73, verified 2026-09-30; history, retired)

Re-verified 2026-10-01 at build 77 (master 88878cd), no rewrite of the text
below: media statements still hold. media_contract.json schema_version 9,
main_count 48, backup_count 28, total_count 76, 20 asset rows (read);
Thesis_Defence_2026.pptx has 136 media files, 19 of them MP4, 0 external
relationships (zip listing); git diff --name-only 0e9fe81 HEAD over
committee_materials/, media/, figures/ and provenance/ is empty; the page-4
clip media/raw_handover_task.mp4 is 17.0 s (ARTIFACT_CHECK.json media1.mp4)
and its sha256 is
d2da9480efb883ff11efed9835babb6cfc9efa675d6d79d413741ffd19bd1997 (sha256sum;
the hash typed in the page-4 bullet below omits "c9e" after "babb6cf" and is
corrected here); media_contract.json sha256 d2709f78... unchanged. Round 11
changed no media; of the 48 main pages in the contract two (pages 2 and 3) are
now hidden by the per-page flag, so 46 are shown (deck_inventory.md, round-11
section).

Sources: presentation/defense_2026/{committee_materials/unified_revision/
media_contract.json, provenance/p04-Raw_Handover_Task.json and
provenance/p04-Raw_Handover_Task_source_frames.csv, figures/coordinate_frames/
overlay/manifest.json, review/film_geometry.json, talk_content.json,
anim/raw_handover_task.py}, DECISIONS.md D-304, D-307, D-308, D-312, D-316
to D-320.

- Page-4 clip (D-304, D-320): media/raw_handover_task.mp4 and its committee
  copy committee_materials/unified_revision/videos/p04-Raw_Handover_Task.mp4
  are byte-identical (sha256sum, 2026-09-30:
  d2da9480efb883ff11efed9835babb6cfa675d6d79d413741ffd19bd1997). Generator
  presentation/defense_2026/anim/raw_handover_task.py (sha256 c0a8dd67... at build 74,
  4a68bbaf... at build 73, provenance JSON), a wrapper over anim/raw_task_context.py (sha256 c2db5c21...,
  unchanged). Content: R7 (Video/recording_20260909_000024.bag) frames
  690-1199 inclusive, 510 frames at the native 30 fps = 17.000 s, 640 x 480,
  h264 yuv420p, libx264 CRF 18; poster at R7 frame 950 (eeead4dfc2fc2816...,
  committee posters/p04-Raw_Handover_Task.png and media/raw_handover_task.png);
  frame map p04-Raw_Handover_Task_source_frames.csv sha256 219522b2.... No
  caption and no mask since build 71 (D-320): the encoder input is the decoded
  source frames by construction, not by a measured check (D-335, build 74:
  the build-71 self-comparison was removed; source rgb sha256 976433b3...), review/
  film_geometry.json lists it with content [[0, 0, 640, 480]], no labels, so
  the D-262 binding rule still covers it. Sha256 of the provenance JSON
  412933875f3ea074fb77bbc232925ba31002869f1251d050df71a00c7f729be6 (build 74, D-335;
  71fa9c79... at build 73) and of
  media_contract.json d2709f78e99d48e4aec10e40b1865176422e600f20bc0e7fbd015be04fcc2a7c (build 74; b1446870... at build 73)
  (computed 2026-09-30). The contract row p04 has page 4, previous_page null,
  kind recording, source_key raw_handover_task.
- Contract at build 73: media_contract.json schema_version 9, 48 main / 28
  backup / 76 total, 20 asset rows, binding_status PASS, status PARTIAL,
  revision_id_map.json schema 12 (D-307). History snapshot of build 67:
  committee_materials/unified_revision/history/round10_b68/ (byte copies of
  the build-67 contract and map). dropped_rows: p05-Raw_Task_Context (previous
  page 5; the page shows the p04 clip) and p43-Offline_Butterworth_Smoothing
  (previous page 53; hidden page 53 deleted, p09 shown on main page 11);
  added_pages [4]. Both dropped films stay on disk: media/raw_task_context.mp4
  (5,399,817 bytes, sha256 a0e82d4e...) and its committee copy
  p05-Raw_Task_Context.mp4; neither is placed on any page.
- Films now on main pages 9-11 (moved from hidden pages, D-307): p07-Hampel_
  Spike_Removal.mp4 on page 9 (previous page 51, 18.7 s), p08-Short_Gap_
  Interpolation.mp4 on page 10 (previous page 52, 18.7 s) and
  p09-Offline_Butterworth_Smoothing.mp4 on page 11 (previous page 9, 18.367
  s). The film bytes are unchanged; durations are read from the contract rows.
  Other films keep their files at new pages: p06 page 8, p13 page 16, p15 page
  17, p16 page 18, p23 page 22, p25 page 23, p29 page 24, p32 page 25, p33 page
  27, p41 page 30, p47 page 36, p49 page 39, p27 page 41, hidden p67 page 53,
  p68 page 54, p46 page 55 (page column of media_contract.json).
- Overlay PNGs (figures/coordinate_frames/overlay/, producer
  make_frame_overlay_figures.py, manifest.json whole-file sha256
  b7a96ffdfe18d16225fcd2e20e363a71af97a4591ae0c9ed388e73fc2db07b3c (build 74), computed
  2026-09-30 and equal to visual.overlay_manifest_sha256 on pages 7, 13, 14,
  15, 20, 28, 29). Seven outputs: overlay_static_markers.png is new
  (D-318), overlay_camera_frames.png and overlay_torso_root.png were redrawn
  (D-312, D-316, D-317); the older sections below describe the six outputs of
  rounds 8-9:

  | Overlay | Page | Size px | sha256 (first 12) | Background and modes (manifest.json) |
  | --- | ---: | --- | --- | --- |
  | overlay_static_markers.png (new, D-318) | 7 | 1440 x 1200 | 31334b203f4d | R6b frame 533 (media/matched/r6b_frame_533.jpg), faded; World projected, Wall projected (reprojection residuals 0.71 and 0.03 px, bound 1.0 px) |
  | overlay_camera_frames.png (D-316) | 13 | 1440 x 1200 | c6bac5eb5f67 | plain panel, no photograph; Camera illustrative, Camera' illustrative |
  | overlay_landmark_frames.png | 14 | 1440 x 1200 | e44cdf1fa8c3 | T-pose photograph, faded; landmark points measured (MediaPipe), no triads |
  | overlay_torso_root.png (D-317) | 15 | 1586 x 1200 | 725591eae790 | T-pose photograph panel plus a plain top view; root L24 illustrative, Camera' (top view) illustrative, root L24 (top view) illustrative, points L23 and L12 measured |
  | overlay_object_world.png | 20 | 1440 x 1200 | fec0d67dbdd6 | R6b frame 505, faded; World, Object, Wall projected, Camera illustrative |
  | overlay_scene_mapping.png | 28 | 1440 x 1200 | 9d000712b523 | frame 505 and the Unity view; World, Scene projected |
  | overlay_rig_frames.png | 29 | 1440 x 1200 | 02cb8ddf0257 | Unity view of frame 505; L24 root, L14, L16 projected |

  The 1586 px canvas of page 15 keeps the 57 px labels at 17.1 pt effective
  in the 6.61 in box (D-317). Page numbers of the older overlays moved:
  camera_frames 11 -> 13, landmark_frames 12 -> 14, torso_root 13 -> 15,
  object_world 18 -> 20, scene_mapping 26 -> 28, rig_frames 27 -> 29.
  Manifest whole-file hash: 73e7300f... (build 67), 54c1e95f... (build 69,
  D-312), 648eab94... (build 73, after D-316 to D-318), b7a96ffd... (build 74,
  generator_sha256 only, PNGs unchanged, D-336).
- Not verified in this task: the 483-file media reference list of round 8
  and anim/validate_media.py (needs the cache /tmp/defense_2026_causal outside
  the repository, PROJECT_STATUS.md rows 69 and 72); the hashes above were
  computed or read from the files named, the other media bytes were not
  re-hashed.

## Round-8 media (history; builds 63-66, verified 2026-09-30; round-9 addition at the end of this section; page numbers are those of build 67, the round-10 numbering is above)

Sources: presentation/defense_2026/{committee_materials/unified_revision/
media_contract.json and history/, revision_id_map.json,
figures/thesis/manifest.json, figures/coordinate_frames/overlay/
{manifest.json,NOTES.md}, equations/white_manifest.json,
equation_catalog.json, review/{film_geometry.json,EFFECTIVE_TEXT.md}},
DECISIONS.md D-264 to D-295.

- Media bytes: the 483 media files are reported hash-identical before and
  after builds 63-66 (PROJECT_STATUS.md rows 63-65; D-266, D-275, D-284). The
  reference list is not in the repository and was not regenerated on
  2026-09-30. Films are unchanged; the page numbers of every film shifted
  (+2 from old page 12, +3 from old page 25, hidden pages 47-58).
- Page-39 film p27: p27-Fresh_Unity_Wrist_Loss_With_Model_Axes.mp4
  (committee_materials/axes_revision/videos/), R7 frames 660-1019, 360
  frames at 30 fps = 12 s, 1440 x 1200, source
  unity_capture/r7/Fresh_Unity_R7_Model_Axes.mp4. Viewport
  [345, 64, 1104, 1188] (FILM_VIEWPORT_PX, VIEWPORT_LEFT_LIMIT 345), box
  5.55 in tall. Measured content rectangles [400,64,1040,544] and
  [336,565,1104,1188] (review/film_geometry.json); the 9 px between x 336
  and 345 is the allowed Unity loss (D-268, D-293). The p35 committee copy
  (videos/p35-Fresh_Unity_Handover_Discussion.mp4) stays on disk but is no
  longer a contract row.
- Film centring rule (D-265): a cropped film box is placed at
  x + (w - pw) / 2 in the 6.61 in column from x 6.22 in, with
  pw = h * (x1 - x0) / (y1 - y0); the validator requires the left edge at
  6.22 + (6.61 - width) / 2 within 0.01 in (page 39: x 7.651, width 3.748).
- Contract chain (media_contract.json schema 9, 21 rows; revision_id_map.json
  schema 11): current 46 main / 31 hidden / 77 total. History snapshots in
  committee_materials/unified_revision/history/: round7_compact (39/14/53,
  map schema 9), round8_b63 (43/12/55, map schema 9, contract sha256
  cfac3502...), round8_b65 (46/12/58, map schema 10, contract sha256
  9fa7802a...); older rounds round1_8film to round5_equations remain.
  base_contract and previous_page_map point at round8_b65; every row carries
  previous_page. The p27 row names its source contract in readded_from
  (axes_revision/media_contract.json, sha256 95d1446c...; D-266 correction),
  and the chained branch compares every bound file key with the base row
  (D-288).
- Thesis figure copies (figures/thesis/manifest.json, D-264): Figure 2.3
  ch2_fig_flow.png (1575 x 840 px, from writing/v9/figures/, page 4) and
  Figure 8.1 ch8_fig_system.png (1920 x 1360 px, page 36), byte-identical to
  the sources. The manifest purpose text still says "page 33" for Figure 8.1
  (stale since build 64; the page is 36).
- Overlay PNGs (figures/coordinate_frames/overlay/, 1440 x 1200 px, fade
  0.5, producer make_frame_overlay_figures.py, manifest.json):
  overlay_camera_frames (page 11; R6b frame 505 photo; Camera and
  Camera-prime illustrative), overlay_landmark_frames (12; tpose_source.jpg,
  4032 x 3024, landmarks measured with MediaPipe, points only),
  overlay_torso_root (13; tpose_source.jpg; root L24 illustrative with a
  measured anchor), overlay_object_world (18; frame 505; World and Object
  projected, Camera illustrative; since build 67 also a projected Wall frame
  and the Camera legend in the upper-right corner, see the round-9 note
  below), overlay_scene_mapping (26; frame 505 and
  r6b_unity_f00505.png; World and Scene projected),
  overlay_rig_frames (27; r6b_unity_f00505.png; L24, L14, L16 projected).
  Photo sources are writing/v9/figures/src/r6b_frame00505.png and
  r6b_unity_f00505.png copies in figures/coordinate_frames/. Specs
  spec_<name>.json and tpose_landmarks_mediapipe.json sit beside them.
- Equation crops: equation_catalog.json has 53 entries (11 added in round 8:
  Eqs. 3.5, 3.6, 3.13, 3.14, 4.2 and 7.1-7.6, each with a plain and a
  _numbered crop; contact-05.png). equations/white_manifest.json lists 71
  white keys: 21 plain keys placed on main pages and 50 _numbered keys
  (Eqs. 3.1-3.24, 4.1-4.2, 5.1-5.12, 6.1-6.6, 7.1-7.6) placed on derivation
  pages 59-77. The compiled thesis has no Eq. 4.3 (the export numbering
  differs).

- Round 9 (build 67, verified 2026-09-30): overlay_object_world.png changed
  (sha256 9362931e... -> fec0d67d..., 1096744 bytes, still 1440 x 1200 px) and
  is not a media_contract.json row (grep of the contract finds no
  overlay_object_world), so the contract chain is untouched. New frame Wall:
  projected from T_cam_wall of eval/output/scene_calibration_r6bc.json (wall
  marker ID 0, 150 mm, thesis WallCameraR, Section 2.2.2), generator pose
  type "calibration_marker"; axis length 0.30 m (twice the 150 mm print, rule
  N-5); reprojection check wall_origin_vs_wall_marker in manifest.json:
  detector finds ID 0 on the deck copy of frame 505 at corner mean (118.79,
  154.56) px, T_cam_wall projects to (118.72, 154.52) px, residual 0.08 px.
  The Camera legend moved to the upper-right corner (anchor 1100, 110) because
  the wall marker sits under the old legend (NOTES.md N-10, N-11; D-302).
  overlay/manifest.json sha256 84a2c6fb... -> abd988f11981d9b3e87bef1b4bfd6768
  d2b4689b4f37503bd4c73cdac4e90440 -> 73e7300fd9f565f05c4b2698e93ccf781a25075b
  639bfa599cb2e3ac89582bd6 (whole-file hash; the last step is D-303: the
  generator records and enforces a 1.0 px World/Object/Wall reprojection bound,
  reprojection_checks.residual_bound_px, and the six PNGs regenerated
  byte-identically); talk_content.json
  visual.overlay_manifest_sha256 of pages 11, 12, 13, 18, 26, 27 carry the new
  value (D-290); the other five overlay PNGs are byte-identical. The 483-file
  media reference list (/home/luo/.claude/jobs/dd6e65ba/tmp/r8/media_before.txt,
  outside the repository) passes per the build-67 worker and master; not
  re-run in the documentation task.

## Round-7 viewports, masks and figure manifests (verified 2026-09-29)

Sources: presentation/defense_2026/{validate_deck.py (FILM_VIEWS,
VIEWPORT_LEFT_LIMIT, FILM_MASKS_PX), talk_content.json, render_deck.py,
figures/evaluation/manifest.json, figures/recovery/manifest.json,
figures/coordinate_frames/anchored_photos.json, effective_text_table.json},
DECISIONS.md D-251 to D-260.

- 1440x1200 composite films: camera view [400,64,1040,544], Unity view
  [336,612,1104,1188] px (every 1 fps frame). Right state-code column starts
  at x 1131; p47 has a stray glyph at x 336-344.
- Presentation crops (a:srcRect, MP4 bytes unchanged): page 25
  p41-Archived_Pose_Replay_With_Model_Axes.mp4 [336,64,1104,1188]; page 31
  p47-Fresh_Unity_Handover_With_Model_Axes.mp4 and page 35
  p35-Fresh_Unity_Handover_Discussion.mp4 [345,64,1104,1188]. Film box at x
  6.22 in, 5.00 in tall (25, 31) or 5.55 in (35). VIEWPORT_LEFT_LIMIT is keyed
  by these file names since build 60 (D-260).
- Page 33 p49-Causal_One_Euro_Filtering.mp4: uncropped 6.00 x 5.00 in, two
  black masks at film px [32,145,365,202] and [32,215,365,270]
  (FILM_MASKS_PX, keyed by file name).
- Build 61 (D-261): every other film hides its burned-in producer labels the
  same way, keyed by file name in validate_deck.py (FILM_VIEWPORT_PX,
  FILM_MASKS_PX, FILM_GEOMETRY_PX with the measured content and label
  rectangles, every 1 fps frame). Viewports (recorded-video kinds, box 4.92 in
  tall at x 6.22): page 8 p06 [160,104,1120,824]; page 18 p23
  [0,78,960,970] (header only; status strip kept, its caption cites it);
  page 21 p32 [0,78,960,798]. Masks: filter family p09/p07/p08/p43/p67/p68/p46
  (pages 9, 44-49) = the p49 boxes; p13/p16 (12, 14) header box plus
  [38,128,276,172] ("0.5x playback"); p15 (13) also [1230,1074,1413,1113]
  ("(Section 5.5)"); p25/p29 (19, 20) [44,22,1167,80] and [20,240,242,662];
  p33 (23) [44,22,1015,80]; p05 (5) [0,458,276,480] over the caption strip
  (build 62; build 61 had [0,457,278,480], 1 px into the camera).
  Film sizes: p05 640x480, p06 1280x1054, p23/p32 960x970, others 1440x1200.
- Build 62 (D-262): the measured label and content rectangles are in
  presentation/defense_2026/review/film_geometry.json (every 30 fps frame,
  film sha256 per entry), written by
  presentation/defense_2026/measure_film_geometry.py; validate_deck.py
  FILM_GEOMETRY_PX must equal it, and every non-full MP4 on any page must be
  in it or be a D-255 viewport film (p41, p47, p35). Rerun the script after
  any film change. Verified 2026-09-29.
- LibreOffice does not honour a:srcRect on a movie (tested 2026-09-29: wrong,
  distorted region); render_deck.py turns cropped movies into cropped poster
  pictures in the PDF export copy only (D-255, D-260).
- Figure manifests: figures/evaluation/manifest.json (byte copies of thesis
  ch7_video_context_r6b.png, ch7_object_waypoints_r6b.png,
  ch7_visual_examples_r7.png for pages 27-28); figures/recovery/manifest.json
  (page-30 r5_label_compare_f1890.png / f1462.png, generator
  eval/failure/make_label_compare_fig.py with --fade 0.5, input hashes);
  figures/coordinate_frames/anchored_photos.json (page-24 r6b_frame00505.png,
  r6b_unity_f00505.png, 640x480, anchors).
- Charts: chart_transport_package.png regenerated in build 60 with every text
  at 16 pt (transport_bench.py --package-chart-only, PKG_TEXT_PT); marker and
  filter panel charts unchanged (D-259). Baked text sizes: deck_fonts.md.

Verified: 2026-09-28 (round-6 update)
Sources: presentation/defense_2026/committee_materials/ (axes_revision, unified_four, bank_revision, unified_revision/VIDEO_INDEX.md, unified_revision/history/round5_equations/), presentation/defense_2026/media/, presentation/defense_2026/anim/, presentation/defense_2026/FILTER_SYNC_BRIEF.json, v1/mediapipe/filter_landmarks.py, presentation/defense_2026/backup_content.json, presentation/defense_2026/experiments/{marker_bench,transport_bench,filter_metrics}/, presentation/defense_2026/DECISIONS.md D-209/D-214
Answers: where every committee film, GIF and master media asset lives, which script generated it, the filter settings baked into the synchronized demo clips, and the round-4/round-6 hidden-page chart and committee-copy media.

## Round-6 update (verified 2026-09-28)

- Media contract round 6, schema 9 (D-214): the round-5
  media_contract.json, revision_id_map.json, both VIDEO_INDEX levels
  (md, csv) and provenance/SOURCE_PRESERVATION_CHECK.json are
  byte-copied to
  committee_materials/unified_revision/history/round5_equations/
  before the rebase, preserving the round-5 state the same way
  history/round4_topics/ and history/round3_27min/ preserve their
  rounds.
- New committee copy for page 35 "Discussion": a byte-identical copy
  of p47-Fresh_Unity_Handover_With_Model_Axes.mp4 (main page 31,
  "Imperfect handover replay"), bound at
  committee_materials/unified_revision/{videos,posters,provenance}/
  p35-Fresh_Unity_Handover_Discussion.{mp4,png,json} (D-132 style,
  same mechanism as the p43/p46 filter-film copies below). The copy
  keeps the "p47" label burned into its frames (D-209).
- The six committee filter-film copies (p43, p46) and the round-5
  hidden pages all shift +2 to hidden 44-49 (filters), 50-51
  (why-charts), 52-53 (References); the underlying files and their
  hashes are unchanged, only the deck page each is bound to.
- Round-5's chart_transport_package.png and the two filter panel
  charts (chart_filter_offline_panel.png,
  chart_filter_realtime_panel.png) are unchanged in content and now
  sit on hidden pages 43 and 50-51 respectively (was 41 and 48-49).

## Round-5 update (verified 2026-09-28)

- The six filter films (p07, p08, p09 copy p43, p67, p68, p49 copy p46)
  are on hidden pages 42-47 in the composite layout (media contract
  schema 8, D-178).
- Charts: experiments/transport_bench/chart_transport_package.png
  (2466 x 1110 px, 200 dpi, page 41, idle rerun); experiments/
  filter_metrics/chart_filter_offline_panel.png and
  chart_filter_realtime_panel.png (1322 x 1000 px = 6.61 x 5.00 in at
  200 dpi, pages 48-49, charts.py --panel). The round-4 transport
  latency and throughput charts and the full-width filter charts stay
  on disk but no page uses them.
- Typeset equations: equations/typeset/ts_*.png (nine keys, white on
  transparent, 600 dpi), catalogue equations/typeset_catalog.json.

## Committee films (presentation/defense_2026/committee_materials/)

Current index: `unified_revision/VIDEO_INDEX.md` (round 3, 2026-09-27).
It lists 25 rows: page (current deck page), stem page (file-name
number), previous page (round-2 slide), movie, duration, evidence
role. Full table is in that file; selected rows:

| Page | Movie | Duration | Role |
|---:|---|---:|---|
| 5 | p05-Raw_Task_Context.mp4 | 46.533 s | Recorded task context, no overlays |
| 8 | p06-Accepted_Body_Landmarks_With_Axes.mp4 | 22.000 s | Recorded input overlay |
| 9 | p09-Offline_Butterworth_Smoothing.mp4 | 18.367 s | Synchronized recorded RGB and calculation |
| 12 | p13-Torso_Frame_From_Standing_T_Pose.mp4 | 11.067 s | T-pose torso frame and root angles |
| 13 | p15-Shoulder_Twist_About_Upper_Arm_Axis.mp4 | 18.733 s | Shoulder twist |
| 14 | p16-Elbow_Rotation_Onto_Forearm.mp4 | 28.067 s | Elbow angles |
| 18 | p23-Holding_Input_And_Torso_Rejection_With_Axes.mp4 | 6.000 s | Holding context |
| 19 | p25-Grasp_Offset_During_Wrist_Depth_Loss_With_Axes.mp4 | 15.400 s | Grasp offset through wrist-depth loss |
| 20 | p29-Elbow_Endpoint_Constraint_Circle_With_Axes.mp4 | 15.400 s | Elbow endpoint constraints |
| 21 | p32-Controlled_Held_Joint_Fallback.mp4 | 8.000 s | Masked-landmark fallback replay |
| 23 | p33-Single_Frame_Data_Flow.mp4 | 44.000 s | Single-frame data flow |
| 25 | p41-Archived_Pose_Replay_With_Model_Axes.mp4 | 25.000 s | Archived-packet Unity replay |
| 29 | p47-Fresh_Unity_Handover_With_Model_Axes.mp4 | 49.933 s | Fresh Unity handover replay |
| 31 | p49-Causal_One_Euro_Filtering.mp4 | 18.367 s | Causal One Euro filtering |
| 46,49,50,51 | p64/p67/p68/p69 | 44.0/18.367/18.367/36.0 s | Q&A schematic/filter demos |
| 62,63 | p07-Hampel_Spike_Removal.mp4, p08-Short_Gap_Interpolation.mp4 | 18.700 s each | Hampel despike / gap interpolation |
| 66 | p27-Fresh_Unity_Wrist_Loss_With_Model_Axes.mp4 | 12.000 s | Fresh Unity wrist-loss replay |
| 68,70,72 | p34/p36/p38 | 40.0/40.0/48.0 s | Schematics, execution recording pending (round 3; retired in round 4, D-127) |
| 76 | p14-Shoulder_Swing_Rotates_Root_Frame_Onto_Upper_Arm.mp4 | 11.133 s | Shoulder swing (round 3; retired in round 4, D-130 -- no current page shows this film) |

Historical files keep their pNN- stem names, so for 23 entries the
stem number differs from the current page. This table describes the
round-3 committee set (still on disk); round 4 (2026-09-28) deleted
pages 36-76 (index and Q&A) and replaced them with 13 topic pages
36-48 -- see the round-4 committee media below.

Video source folders:
- `axes_revision/videos/` -- current-round films with overlay axes (p06-p38 series listed above).
- `unified_four/videos/` -- p13, p14, p15, p16 (torso/swing/twist/elbow unified-layout films; producer pages keep their stems: p13 on page 12, p14 retired in round 4 (D-130, was page 76), p15 on page 13, p16 on page 14).
- `bank_revision/videos/` -- p17-Shoulder_Swing_From_Arm_Raise.mp4, p18-Shoulder_Twist_From_Forearm_Plane.mp4, p19-Elbow_Angles_From_Bending_Trial.mp4, p20-Straight_Arm_Twist_Observability.mp4, p41-Archived_Pose_Replay_With_Model_Axes.mp4 (earlier bank demonstrations).
- `axes_revision/animations/` -- GIF versions of five round-3 Q&A-only films: p34-Shared_Image_Private_Copies.gif, p36-Temporal_Stream_Combination.gif, p38-Python_Unity_Read_Write_Validation.gif, p64-Derived_Memory_Records.gif, p69-Single_Frame_Overview.gif. All five files are unchanged on disk, but every page that showed them (Q&A 68, 70, 72, 46, 51) was deleted in round 4 (D-127); no current deck page embeds any of these five GIFs.

## Round-4 hidden-page committee media (2026-09-28, backup_content.json pages 36-48)

Six of the 13 round-4 hidden pages are `full_video` filter demonstrations, each a byte-checked committee copy of the corresponding `media/filter_*_sync.mp4` master (confirmed by reading backup_content.json `committee_media` blocks directly):

| Page | Committee file | Source master | Note |
|---:|---|---|---|
| 41 | p07-Hampel_Spike_Removal.mp4 | media/filter_hampel_sync.mp4 | unchanged stem from round 3 (was Q&A 62) |
| 42 | p08-Short_Gap_Interpolation.mp4 | media/filter_gap_sync.mp4 | unchanged stem from round 3 (was Q&A 63) |
| 43 | p43-Offline_Butterworth_Smoothing.mp4 | media/filter_butterworth_sync.mp4 | new stem, byte-identical copy of p09 (main page 9); added in round 4 because one film cannot bind to two contract pages (D-132) |
| 44 | p67-Savitzky_Golay_Filtering.mp4 | media/filter_savgol_sync.mp4 | unchanged stem from round 3 (was Q&A 49) |
| 45 | p68-Median_Filtering.mp4 | media/filter_median_sync.mp4 | unchanged stem from round 3 (was Q&A 50) |
| 46 | p46-Causal_One_Euro_Filtering.mp4 | media/filter_one_euro_sync.mp4 | new stem, byte-identical copy of p49 (main page 31); added in round 4 (D-132) |

The other seven round-4 hidden pages are `full_image`/`full_table`
with no committee video: 36 and 38 are `full_table` (no media file,
table rows only); 37, 39, 40, 47 and 48 are `full_image` pages
showing one of five new PNG charts, one per experiment folder except
transport_bench which contributes two:
- `experiments/marker_bench/chart_marker_bench.png` (page 37)
- `experiments/transport_bench/chart_transport_latency.png` (page 39)
- `experiments/transport_bench/chart_transport_throughput.png` (page 40)
- `experiments/filter_metrics/chart_filter_offline.png` (page 47)
- `experiments/filter_metrics/chart_filter_realtime.png` (page 48)

All paths are relative to `presentation/defense_2026/`. See
experiments.md for how each chart was produced.

## media/ masters (presentation/defense_2026/media/)

Six synchronized filter demo masters, 1440x1200, confirmed by
ffprobe 2026-09-28:
- filter_hampel_sync.mp4 -- 18.700 s
- filter_gap_sync.mp4 -- 18.700 s
- filter_butterworth_sync.mp4 -- 18.367 s
- filter_one_euro_sync.mp4 -- 18.367 s
- filter_savgol_sync.mp4 -- 18.367 s
- filter_median_sync.mp4 -- 18.367 s

Each has a matching `.png` poster frame. These are the source for
the committee p07/p08/p09/p49/p67/p68 films above.

Older, unsynchronized teaching clips (also present): filter_hampel,
filter_gap, filter_butterworth, filter_one_euro, filter_savgol,
filter_median, each as `.mp4` and `.gif`, 1440x1080, 36.000 s
(confirmed by ffprobe 2026-09-28).

Camera-only context clips: filter_*_context.mp4 (e.g.
filter_hampel_context.mp4, confirmed 640x480, 12.0 s) --
camera pixels only, no overlay.

Raw task context master: raw_task_context.mp4, 640x480, 46.533 s
(confirmed by ffprobe 2026-09-28; this is the file copied
byte-identically into the committee p05 slot per DECISIONS.md D-120).

Other masters present: causal_replay.mp4/.png, frame_journey,
grasp_offset, memory_combine/flow/layout/race/records, recovery_geometry,
teaching_elbow, teaching_frame_journey, teaching_memory_copy(_restrained),
teaching_merge(_restrained), teaching_read_write(_restrained),
matched_elbow_constraints, matched_frame_journey, matched_grasp,
method_grasp_context, method_occlusion_context, wrist_prediction_context,
grip_episode_context, held_fallback_context -- each with a matching
`.png` poster and some with `.gif` variants; not individually timed
in this inventory.

## Generators (presentation/defense_2026/anim/)

- `filter_synchronized.py` -> `filter_demos.py` -> frozen
  `v1/mediapipe/filter_landmarks.py`, driven by
  `media/provenance/filter_demo_raw_r6b.csv`. Produces the six
  filter_*_sync masters above.
- `committee_media.py` -- black-background re-renders for the
  committee packet.
- `recorded_context.py` and `raw_task_context.py` -- build the
  camera-only and raw-task context clips from the R6b bag
  (Video/recording_20260831_065553.bag) and the R7 bag
  (Video/recording_20260909_000024.bag).
- `causal_replay.py` -- the causal (online) replay generator; stages
  extract/render/encode/all, extract stage uses the v3rt Python.
- `recorded_context.py audit-source` -- checks the existing R6b
  colour cache against source (v3rt Python).
- `matched_evidence.py` -- source-matched R7 extraction (stages
  extract/derive/preview/build/elbow).

## Unity captures

`presentation/defense_2026/unity_capture/` -- capture and validation
scripts for Unity replay footage: run_capture.py, prepare_project.py,
capture_archived_r5.py, replay_archived_packets.py,
finalize_archived_capture.py, finalize_manifest.py, finish_capture.py,
compare_archived_views.py, validate_archived_media.py,
check_rig_sizing_isolated.py, plus AxesOverlay.shader and
DefenseAxes.cs (Unity-side), and capture output folders r5,
r5_archived, r7.

## Filter settings (confirmed in both FILTER_SYNC_BRIEF.json
## "parameters" block and v1/mediapipe/filter_landmarks.py argparse
## defaults)

| Filter | Setting | Value |
|---|---|---|
| Hampel | window / k / floor | 7 frames / 3.0 / 0.02 m |
| Gap interpolation | max_gap | 5 frames |
| Butterworth | order / cutoff | 4 / 3.0 Hz |
| Savitzky-Golay | window / order | 9 / 2 |
| One Euro (offline default in filter_landmarks.py) | min cutoff / beta | 0.05 Hz / 1.0 |

Note: the live/causal One Euro filter used in
`eval/pipeline_smoothness/` (CausalLandmarkFilter,
v1/realtime/person/realtime_person.py) uses different defaults --
min_cutoff 1.0 Hz, beta 1.0, freq 30 -- confirmed in
eval/pipeline_smoothness/DECISIONS.md line 55 and README.md line 68.
Do not conflate the two One Euro parameter sets; see
filter_facts.md.

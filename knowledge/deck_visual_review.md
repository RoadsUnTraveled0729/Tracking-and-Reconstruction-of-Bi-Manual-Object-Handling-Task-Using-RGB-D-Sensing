# Defence deck visual review

Status 2026-10-06: history. The deck reviewed here (2026-09-29, D-244: 39 main + 14 hidden pages,
1785 s = 29:45, bytes restored from commit c5440c4) is no longer the deck; its generated files and the paths named below
(talk_content.json, build_deck.py, validate_deck.py, committee_materials) were deleted in 3dbd345
(recover at 85078c9); the final deck is in deck_inventory.md. This file holds the
read-only visual audit of that deck made at commit 26e954a, whose
talk_content.json, build_deck.py and Thesis_Defence_2026.pptx are identical to
c5440c4 (git diff --quiet, checked 2026-09-29), so the findings below apply to
the restored deck. Their proposed presentation-only changes were prototyped and
built only in the discarded Codex decks (a202509..ddfdf40, git history); they
are NOT in the restored deck and remain optional. The 2026-09-29 three-reviewer
page review of the restored deck (0 unpresentable pages, list of MEDIUM and
LOW findings) is in deck_defects_2026-09-29.md. The M3 prototype and
integrated-implementation sections of the earlier version of this file are
removed (they described the discarded deck).

Verified: 2026-09-29. Re-checked in this task: the git identity of the reviewed
and restored files; that the listed preview PNG/JPG files and the p35 poster
exist; the ffprobe metadata table below (H.264 High, yuv420p, 30 fps, sizes and
durations all match). Not re-checked: the slide-by-slide reading of the five
findings, the point conversions, and the "Polish feasibility follow-up" code
statements (only the missing /tmp caches and the existence of the named input
files were re-checked).
Sources: presentation/defense_2026/preview/{overview-01.jpg,overview-02.jpg,
overview-03.jpg,overview-04.jpg,slide-03.png,slide-09.png,slide-13.png,
slide-24.png,slide-28.png,slide-29.png,slide-30.png,slide-35.png};
presentation/defense_2026/committee_materials/unified_revision/posters/
p35-Fresh_Unity_Handover_Discussion.png;
presentation/defense_2026/{talk_content.json,build_deck.py,
make_coordinate_figures.py}; presentation/defense_2026/anim/
{axes_unity_composite.py,unified_panels.py,bank_axes_kinematics.py}.

The audit viewed all 39 main slides through overview sheets and the selected
full-size previews above. Native PowerPoint playback and projector readability
were not tested. See deck_inventory.md, media_inventory.md and
checkers_and_caches.md for the existing inventory, provenance and checks.

## Five findings and proposed presentation-only changes

1. Slides 31/35: observed small recovery/live labels in the handover
   composite, shown directly on slide 35 and its original poster. Source
   labels of 25-32 pixels on a 1200-pixel-high canvas displayed at 5 inches
   correspond to approximately 7.5-9.6 points. Reflow larger labels in a
   presentation-specific copy using axes_unity_composite.py:draw. Preserve
   both complete views, source clock, and recovery/live distinctions.
2. Slides 12-14: observed dense kinematic panel labels; slide 13 was
   inspected at full size. unified_panels.py defines 28/30-pixel small
   labels/headings, approximately 8.4/9 points at the same display height.
   Reflow headings, legends and angle readouts through compose_four and
   bank_axes_kinematics.py:render/build while preserving camera/model/plane
   views, frames, arcs and the observability warning.
3. Slide 24: observed small internal captions in six schematic rows.
   Enlarge labels/axis glyphs and improve column spacing using
   make_coordinate_figures.py:scene_mapping/rig_frames and
   build_deck.py:restrained_figure_pair. Preserve frame conventions and
   the illustrative-geometry caveat.
4. Slides 3/29/35: captions sit close to the footer rule. More separation
   is subjective spacing polish; no overlap was established. Reserve a
   consistent caption band and redistribute wrapping/row heights through
   build_deck.py:restrained_rows/restrained_page/restrained_figure_pair.
   Retain all wording, values and existing caption typography.
5. Slide 30: figure-internal legends and adjacent repeated numeric labels
   compete for space. Improving hierarchy is subjective polish. Enlarge
   both complete comparison figures and align their native labels through
   build_deck.py:restrained_figure_pair. Preserve figure pixels, frame
   numbers, values and the manual-label caveat.

## Representative video metadata

Read-only ffprobe inspection of the current clips found H.264 High,
yuv420p and 30 fps for every sample below. Paths are relative to
presentation/defense_2026/committee_materials/.

| Slide | Path | Pixels | Duration (s) |
|---|---|---|---|
| 5 | unified_revision/videos/p05-Raw_Task_Context.mp4 | 640x480 | 46.533333 |
| 9 | axes_revision/videos/p09-Offline_Butterworth_Smoothing.mp4 | 1440x1200 | 18.366667 |
| 13 | unified_four/videos/p15-Shoulder_Twist_About_Upper_Arm_Axis.mp4 | 1440x1200 | 18.733333 |
| 25 | bank_revision/videos/p41-Archived_Pose_Replay_With_Model_Axes.mp4 | 1440x1200 | 25.000000 |
| 35 | unified_revision/videos/p35-Fresh_Unity_Handover_Discussion.mp4 | 1440x1200 | 49.933333 |

build_deck.py:movie fits posters/videos proportionally and requests
playback on entry. No aspect distortion was found. Metadata does not
verify player compatibility; blanket transcoding or raw-video enlargement
has no demonstrated benefit from this audit.

## Polish feasibility follow-up

Verified: 2026-09-29 (read-only input/path and code inspection).
Additional sources: bank_processing/{p13,p18,p19}/
{inference_frame_map.json,source_manifest.json};
bank_processing/unified_four/{p13,p15,p16}/kinematic_source.json;
media/provenance/axes_r7_rgb.json; unity_capture/r7/
{capture_manifest.json,integrated_stream.csv,source_group_states.csv};
anim/axes_inputs.py; bank_processing/check_unified_four_media.py;
validate_deck.py. Paths in this section are relative to
presentation/defense_2026/ unless stated otherwise.

- Each bank inference manifest references 899 missing images under
  /tmp/defense_bank_rgb/p13, p18 or p19. The R7 RGB manifest references
  1498 missing images under /tmp/defense_axes_rgb_r7. Existing bank raw/
  filtered tables, derived kinematics, source references and manifests
  are present; path existence does not establish current hash freshness.
- Existing encoded kinematic/handover films, posters, source-frame maps
  and axis audits are present. The fresh R7 Unity capture MP4, driver/
  state CSVs and all R7 inputs named by axes_inputs.py are also present.
  Copies could use these sources without new camera or Unity capture.
- The proposed video generators and make_coordinate_figures.py have
  fixed output directories and no output-directory argument; rerunning
  them unchanged overwrites original assets/reports. The video generators
  also require the missing RGB caches. Inspected provenance records
  contain film duration, not generator elapsed runtime.
- Proposed alternative: a separate presentation derivative writer with
  repository-local outputs, preserving originals and complete scientific
  views. Bind parent film/provenance, saved data and frame maps by hash;
  retain frame order, fps, duration, holds and motion states. Decoded
  encoded-exhibit pixels must not be claimed as fresh raw-camera pixels.
- New derivatives require content/contract bindings and a dedicated
  validate_deck.py audit route, while retaining original audit routes.
  check_unified_four_media.py calls renderer.prepare and needs the missing
  RGB caches; a derivative check must instead compare the preserved
  encoded baseline and inherited audit. Page 35's byte-identical-copy
  binding would need to refer to the new handover derivative.

These derivative/code/contract changes remain proposed, unapproved and
unimplemented. No renderer, extractor or report-writing checker was run
for this feasibility follow-up. Playback/projector testing remains open.

Note (2026-09-29): the discarded decks implemented derivatives of this kind
(and the M3 prototypes for pages 24 and 31/35); none of that work is in the
restored deck. If the author wants these polishes, they are new work on the
restored deck and the discarded implementations in git history are the
reference.

# Chapter 7 trajectory figures: implementation record

Decisions D-015 to D-019 in DECISIONS.md, applied 2026-09-08 after the
review in CH7_TRAILS_REVIEW.md (D-014). The user approved the redesign
and required that the recorded video stay unchanged. Codex implemented
the revision; the Claude session of 2026-09-08 finished it (fixed crop
and margins of the figures, the review loop, the tracking files, the
build, the commit). Baseline: commit 7373441 (the review), whose figures
came from d2b910a.

## What the reader sees

- Figure 7.10 (ch7_fig_unity_trails.png): three Unity stills from one
  fixed orthographic oblique presentation camera, one per task interval:
  carry frames 92 to 500, lift 501 to 528, slide 529 to 899. Each still
  shows the pose at the interval's last frame. Dashed waypoint reference
  with cube-shaped waypoint marks, green object marker origin, blue model
  wrist where the shoulder swing and elbow groups were measured, orange
  where they were rebuilt, translucent avatar, labelled waypoints, a
  10 cm scale bar from the logged orthographic size (a length in the
  image plane). Every panel is the same window cut from the same fixed
  view: the union of the drawn pixels over the three stills plus a
  margin, measured by the composer (112-1200 by 78-679 of 1200 x 800 for
  this capture), so the panels share one framing and one world scale;
  panel (c) is printed at about twice the magnification of (a) and (b),
  and each panel carries its own bar.
- Figure 7.5 (ch7_fig_rail_traj.png): the object marker origin track in
  the levelled world frame with the waypoint reference and the fitted
  rail line, labelled as the marker origin.
- Figure 7.7 (ch7_fig_wrist_traj.png): (a) the model wrist path in 3D
  by state over the task frames 92 to 899 (the startup excursion of
  frames 0 to 25 would otherwise set the scale); (b) x, y, z of the wrist
  over every frame 0 to 899 with the rebuilt intervals shaded: 5-25,
  550-640, 674-684, 821-822. No display smoothing; the startup and
  recovery jumps stay visible in (b).
- Figure 7.8 (ch7_fig_combined.png): the slide samples of Section 7.3
  seen from above (x against z) and from the side (x against y), with
  the fitted rail line, the marker origin and the wrist by state; legend
  outside the data; panel heights in the ratio of the data spans so both
  panels keep the full width under the shared x axis at equal aspect.
- Figures 7.1 and 7.2: the cube rectangles and bodies are placed so the
  pinned waypoints locate the marker origin (the drawn cube centre sits
  half an edge behind it), which is what the data plots use; the rail
  bar moved with the cube, because the fitted depth is the marker
  origin's and the cube body sits behind it.
- Text: Sections 7.3 to 7.6 and the captions name the plotted object
  point as the marker origin, distinguish the waypoint reference from the
  fitted rail line, state that the model wrist is not the rendered hand,
  and read the wrist comparison as consistency. Exact old -> new pairs:
  CH7_TRAILS_TEXT_CHANGES.md. Chapter 9 now cites Section 7.7 for frame
  1462 (was 7.5).

## Data path (nothing recomputed, nothing filtered)

- Points: eval/reports/unity_check_r6b_trails/trails.txt (committed in
  d2b910a, display axes under the levelled ArucoWorld node): the
  reference (start, W1, W2, W3), the marker origin per frame (899 frames,
  786 missing) and the model right wrist per frame (900 frames).
- Wrist state: eval/output/recovery_r6b/angles_recovery.csv columns
  tag_1 (right shoulder swing) and tag_3 (right elbow); 2 = rebuilt,
  1 = held, 0 = measured (eval/occlusion/solvers.py group order). The
  same rule as make_ch7_wrist_traj_fig.py. No held frame occurs in those
  two groups; the twist (tag_2) is held on 528 frames and is not drawn.
- Intervals: eval/reports/r6b_waypoints.json track_turns (parked 0-91,
  lift begins 501, rail reached 529, last 899). They are presentation
  intervals; the evaluation's height-band sample set (Section 7.3) is
  unchanged.
- Stream: eval/output/unity_check_r6b_trails/integrated_stream.csv (the
  E-032 capture, ignored by git) replayed into shared memory.

Scripts (writing/v8/condensed/scripts/):

- ch7_trail_data.py: reads the three inputs above; write_view_config
  writes figures/ch7_trails_view.json and its copy /tmp/ch7_trails_view.json.
- render_ch7_trails.py: refuses if an editor is open or another capture
  mode is armed; starts the replay (--replay, send_scene_r5.ShmWriter),
  waits for both shared-memory mappings, arms the autoplay flag, launches
  the editor, waits until the three phase records exist, then stops and
  quits the editor, archives the receiver's scratch logs beside the stills
  and restores their previous bytes, and removes the view config. The
  replay holds each interval's last frame until its record exists (the
  last frame was skipped at loop wrap without this). A run is accepted
  only when every still, record and the two receiver logs were written
  after the editor launch (the three receiver logs included); it then
  writes manifest.json (SHA-256 of each artefact and of the view config)
  and capture.txt (the editor's capture lines), which
  validate_ch7_trails_revision.py checks, so a stale still or a leftover
  log cannot pass. Shutdown never raises, so the log restore and the flag
  removal always run.
- Unity/Assets/Scripts/Chapter7TrailView.cs (opt-in, bootstraps only when
  /tmp/ch7_trails_view.json exists): builds the orthographic camera
  around the union of the drawn points (direction (0.6, 1.2, -1.5),
  margin 1.4), draws the reference dashes and waypoint cubes and the two
  frame-indexed paths for the interval (a missing frame is a gap), swaps
  the avatar materials for Chapter7Ghost.shader (alpha 0.18), neutralises
  the desk top and hides the text meshes, held markers, occlusion markers
  and wall slab for the render, then writes <phase>.png (1200 x 800) and
  <phase>.json (applied frame, camera pose, orthographic size, waypoint
  viewport coordinates) and restores the scene.
- make_ch7_trails_fig.py: composes the stills; asserts one camera and
  one still size across the records; the crop window is measured from
  the drawn pixels; labels from the logged viewport coordinates; fonts
  and label offsets are display choices. It writes
  figures/ch7_trails_compose.json (the digest of the manifest it composed
  from, the crop, the digest of the figure), which the validator checks,
  so a figure composed from an earlier capture fails.
- make_ch7_object_trajectory.py: Figure 7.5 from eval_rail_scenario
  load_track (the marker origin), r6b_waypoints.json and the same line
  fit as Section 7.3.
- make_ch7_wrist_traj_fig.py: unchanged computation (forward kinematics
  from the recovery angles, levelled by LeveledWorld); it now asserts that
  its numbers equal the pinned figures/ch7_wrist_traj.json and hands the
  arrays to draw_ch7_trajectories.py, which draws Figures 7.7 and 7.8 and
  carries the two display helpers (settle_3d centres the projected 3D
  content in its slot, trim cuts the white margin).
- validate_ch7_trails_revision.py: the 40 protected files of
  ch7_trails_source_hashes.json at their recorded size and SHA-256 (the
  .bag, the filtered track, the recovery angles, the calibration, the
  stream, trails.txt, the pinned numbers, the source frames), the
  exported points equal to trails.txt, no held tag in the right swing
  and elbow groups, the capture manifest (every artefact at its digest,
  the view config unchanged since the capture), the three records at the
  interval endpoints with one camera, the receiver's object and pelvis
  logs equal to the stream at those frames, the four figure files
  embedded byte for byte in Chapter_7_Evaluation.docx and
  Thesis_V8_Condensed.docx. Output pinned in CH7_TRAILS_VALIDATION.txt.

Capture record (figures/src/ch7_trails_revision/): carry.png/json (frame
500), lift.png/json (528), slide.png/json (899), unity_object_log.csv,
unity_person_log.csv, rig_dimensions.csv, manifest.json, capture.txt;
editor.log and sender.log are kept locally and ignored. The accepted run
launched 2026-09-08 08:25:13 (Codex's first render of 07:37 had the same
camera and frames; it was rerun through the hardened launcher so that the
manifest binds the stills). Camera: position (0.42, 1.73, -0.77) m,
target (-0.04, 0.80, 0.39) m, orthographic half-height 0.22 m, identical
in the three records. eval/DECISIONS.md E-033 records the render.

## Reproduce

    cd /home/luo/Desktop/New_SandBox
    PY=/home/luo/anaconda3/bin/python
    # stills (Unity editor closed; a few minutes; MCP not needed)
    $PY writing/v8/condensed/scripts/render_ch7_trails.py
    # figures
    cd writing/v8/condensed/scripts
    $PY make_ch7_task_schematic.py; $PY make_ch7_object_trajectory.py
    $PY make_ch7_wrist_traj_fig.py; $PY make_ch7_trails_fig.py
    # chapter, thesis, PDF, checks
    cd /home/luo/Desktop/New_SandBox
    $PY writing/v8/condensed/scripts/build_ch7.py
    $PY writing/v8/condensed/scripts/build_ch9.py
    $PY writing/v8/condensed/scripts/build_thesis.py
    /usr/bin/python3 writing/v8/condensed/scripts/render_pdf.py
    $PY writing/v8/condensed/scripts/check_refs.py
    $PY writing/v8/condensed/scripts/check_style.py
    (cd writing/v8/condensed/scripts && $PY validate_ch7_trails_revision.py)
    $PY writing/v8/scripts/make_ch7_ch8_changes.py --chapter7-only

## Not changed

The recording (Video/recording_20260831_065553.bag), the tracking
outputs, the recovery angles, the trails file, every reported number
(the 6.5 cm median wrist distance, the 407 slide frames, the 899 of 900
detections, the line residuals). The earlier capture path
(make_ch7_trails.py, TrajectoryTrails.cs, /tmp/r5_trails.txt) is kept and
inert; render_ch7_trails.py refuses to run while it is armed.

## Review and build (finishing pass, 2026-09-08)

Chapter review loop (skill_set/thesis-revision-workflow.md): three fresh
Opus reviewers on the whole chapter, reports in writing/reviews/
Chapter_7_trails_revision_round1.txt (31 flags), round2 (24), round3 (14).
Every certain flag in the revised text of Sections 7.3 to 7.6 was applied:
one name, "the marker origin", in prose, captions and legends; the passives
named their actor; the change-log and provenance sentences left the
captions; the nominalisations and the terms outside the glossary ("trail",
"stills", "presentation camera", "oblique", "translucent") were replaced;
"visible deviations" became the median 6.5 cm and 95th percentile 9.6 cm;
the Section 7.5 opening no longer restates its heading. Round 3 left only
uncertain flags in the revised text and pre-existing flags in Sections
7.1, 7.2 and 7.7 (listed in the reports for the author; those sections
passed the earlier Chapters_7_8_9 rounds and are outside this revision),
so the loop stopped at its three-round limit.

Code review (.claude/agents/code-reviewer.md, Opus, two passes). First
pass, applied: the schematic rail bar moved with the cube and the W3 label
above it (Figures 7.1 and 7.2); Figure 7.8 panels equally wide under the
shared x axis; Figure 7.7's 3D axis labelled "height y (cm)" with a wider
gap and drawn over the task frames 92 to 899; the held-tag check made on
the raw tag columns; the stills bound to the capture (manifest,
freshness, capture.txt) and the capture rerun through that path; the crop
measured from the pixels; the scale bar stated as an image-plane length.
Second pass, applied: the equal widths are now obtained with the box
aspect mode and span-proportional heights (the data-limit mode had cut
the trajectories at the panel edges); Figure 7.5's x label padded clear
of its ticks; the launch time taken right before the editor starts; all
three receiver logs required fresh; the composition bound to the manifest
(ch7_trails_compose.json); the shutdown made non-raising; the unused
import removed; the task-first frame read from the pinned waypoints. Also
found there: the pre-existing "3.9 centimetres" rail height was the
difference of two rounded levels (7.4 and 3.5); the pinned r6b_rail_eval
values give 7.43 - 3.46 = 3.97 cm, printed as 4.0. Left by decision:
build_ch7.py keep_with_next after every picture (Chapter 7 only; a
candidate for the other builders); *.log ignored in the capture folder
(capture.txt carries the capture lines); the "Marker-centre track"
docstring in the frozen eval/gt/eval_rail_scenario.py (it returns the
marker origin, as this record states); Chapter7TrailView.cs draws a held
group in the measured colour (no held frame exists in the drawn groups;
the validator asserts it); the unused left-wrist forward kinematics in
make_ch7_wrist_traj_fig.py (pre-existing); check_unity_log.py not rerun
for the presentation render (E-033 states why).

Build: build_ch7.py, build_thesis.py all PASS; render_pdf.py 161 PDF
pages; check_refs UNRESOLVED none; check_style only the two pre-existing
hits (the 94-word Chapter 3 sentence, the user's first acknowledgement
sentence); validate_ch7_trails_revision.py PASS (CH7_TRAILS_VALIDATION.txt);
the Chapter 7 change log Thesis_V8_Changes_Ch7.docx rebuilt. The figure
pages (83, 84, 87, 89, 90 and 92 of the PDF) were inspected at page
width.

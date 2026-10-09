STATUS: COMPLETE
GOAL: Check the newest Chapter 7 trail result and recommend clearer presentation.
KEY FINDING: The figure combines avoidable visual clutter with real discontinuities in the saved wrist trajectory; its terminology also needs correction.
VERIFIED: The current trail image is embedded in both delivered Word documents. The saved wrist path contains consecutive frames with abrupt position changes. Both green plots use the object marker origin.
ASSUMPTIONS/UNRESOLVED: The user's "trail" is interpreted as Figure 7.10, with Figures 7.7 and 7.8 as context. The cause of each wrist discontinuity is unverified. The proposed layout has not been rendered.
DECISION: Recommend the changes below. This review does not rebuild the manuscript or change experiment outputs; D-014 records the advisory scope.
NEXT: Apply the figure redesign and terminology corrections in a subsequent manuscript revision, then inspect the new capture at printed size.

Reason:

The camera view prioritizes the avatar while the comparison takes place
in a small region near the desk. The reference path dominates the object
track, and accumulated wrist history is difficult to read. Simply drawing
a smoother line would leave the incorrect names and the real output
discontinuities unexplained.

Evidence:

- Reviewed baseline: d2b910a, the latest chapter change at review time.
  The files are writing/v8/condensed/Chapter_7_Evaluation.docx and
  writing/v8/Thesis_V8_Condensed.docx. The PDF Figure 7.10 is on printed
  page 92, PDF page 111. Its small trail region and legend were checked
  in a rendered page, as well as in the original PNG.
- The matching image hashes and saved-path checks are recorded in
  CH7_TRAILS_AUDIT.txt, produced by scripts/audit_ch7_trails.py.
- An independent read-only agent reviewed the data, figure builders,
  Unity renderer and captions and confirmed the findings below.

Priority 1: Give the trajectories the main area of the figure.

Use a close elevated oblique Unity camera aimed at the object workspace,
with identical framing across panels. Reduce the avatar's visual weight
using an outline or translucent presentation in this dedicated trajectory
view. Keep the matched sensor-camera evidence in Figure 7.9. Label the
new Figure 7.10 view as a presentation camera. Add a top or side projection
where it helps distinguish depth and height, with equal spatial scale.

The current Figure 7.10 spends most of its area on the torso and background.
Its green line is difficult to distinguish from the red reference, and
the opaque avatar can occlude the trails. Higher image resolution alone
will not solve these problems. Figure 7.8 also places its top-view legend
over part of the plotted wrist data.

Priority 2: Separate motion phases and make time explicit.

Use panels for carry, lift and rail slide. Draw the current phase clearly
and put earlier history in a subdued style, or show only the named interval
and retain a separate full-recording overview. Print frame intervals and
mark the start, end and direction of motion. Use documented task boundaries
and disclose the selection; do not select intervals to remove failures.

The current panels show accumulated history through frames 505 and 898.
The second therefore repeats all earlier wrist movement. TrajectoryTrails.cs
Apply selects every sample up to the current frame and joins it into one
line. The static reference is drawn whole, including future waypoints.
The two panels do not isolate the lift and slide behavior.

Boundary caution: r6b_waypoints.json identifies lift onset and rail arrival,
whereas the height-band sample set in ch7_wrist_traj.json starts earlier.
Those definitions serve different purposes. A phase-specific illustration
must name its rule rather than silently treating the evaluation band as
the physical task transition.

Priority 3: Give different meanings different visual styles.

Use a thin dashed reference and labelled waypoint symbols, green for the
object marker track, and blue/orange wrist segments for the input/recovery
states already distinguished in Figure 7.7. Use a separate shape or neutral
annotation for the avatar's non-measured groups. Keep a compact legend
outside the plotted region and readable at the final page width.

The current red spheres mean both reference waypoints and non-measured
avatar groups. The reference line is wider than either trajectory
(make_ch7_trails.py STYLE), and the Unity wrist has one color for every
frame. These choices obscure both overlap and recovery behavior.
The measured-input/rebuilt categories do not certify that every angle was
measured: the right-arm twist has its own held state. Name this scope in
the legend or caption.

Priority 4: Preserve and explain the discontinuities.

Keep the saved trajectory unchanged. Mark recovery entry and return where
they coincide with abrupt changes. A wrist-coordinate-versus-frame strip,
with recovery intervals shown, would distinguish a position jump from
repeated movement in the same place. Break the object line at a missing
detection or identify the connecting interval as a gap.

The wrist section of eval/reports/unity_check_r6b_trails/trails.txt contains
every frame from 0 through 899. Abrupt segments are therefore present in
the stored wrist output, rather than being created by joining omitted
wrist frames. Examples occur at startup and around frames 550 and 640.
Several coincide with state changes in angles_recovery.csv; this association
does not establish the full cause. The cube path skips frame 786, but
TrajectoryTrails.cs joins frames 785 and 787 without marking that gap.
The gap is a separate disclosure issue, not an explanation of the blue
tangle. The existing Unity-log checks validate pose application and rig
placement; they do not establish trail readability or the cause of jumps.

Priority 5: Correct the point names and the result statement.

Both green plots contain the tracked object marker origin. Figure 7.8
calls it the cube centre. Its builder takes xyz from
eval/gt/eval_rail_scenario.py load_track, which levels the unity position
columns without applying the separate box_center transform in
eval/offset/carry.py. Figure 7.10 reads the same columns directly.
Unity/Assets/Scripts/ArucoSceneReceiver.cs places the cube body half an
edge behind the object node, confirming that the marker origin and body
centre are distinct. Use "object marker origin" consistently for the
existing plots and associated distances. Changing to a physical cube-centre
trajectory would require recalculating the affected figures and statistics.

Figure 7.8 uses the fitted rail line; Figure 7.10 uses the waypoint reference
path. The paragraph and caption currently call them the same three
trajectories. Name the distinction, or use the same reference in both.
The reference and fitted line are derived from the track; they do not
independently establish wrist accuracy.

The blue path is the model wrist computed using the measured shoulder and
the recording's calibrated arm lengths. It is not the rendered avatar hand
trajectory, as D-013 explicitly records. Put that distinction beside the
figure so a reader does not assume the blue endpoint must coincide with
the visible hand. Do not translate the trail to the hand for appearance.

Replace the claims that the green line "lies on" the reference and that
blue density is explained by a hand that "moved little" with a qualified
description of the visible agreement and deviations. Some of the density
can be accumulated movement; source discontinuities also contribute. The
independent wrist comparison remains the manual-label results in Section 7.7.

Therefore:

The preferred redesign is a task-centred Unity view divided by phase,
with labelled waypoints, distinct reference styling and visible recovery
states. Keep the full saved output trace without additional display smoothing and correct the
marker-origin/model-wrist definitions before interpreting the separation
between the curves. Reassess the chapter at actual printed size.

Validation and reproduction:

Run from /home/luo/Desktop/New_SandBox:

    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/audit_ch7_trails.py
    pdftoppm -f 111 -l 111 -scale-to 1250 -png -singlefile writing/v8/Thesis_V8_Condensed.pdf /tmp/ch7_trails_page

The first command reads the committed trails and current DOCX images.
Its output is pinned in CH7_TRAILS_AUDIT.txt. The second produces a page
preview for this reviewed PDF; pagination may change after later edits.
No Unity recapture, filtering change or tracking-method rerun was performed.
Acceptance of a replacement figure would require new capture inspection,
verification of its frame intervals and point definitions, preservation
of failure behavior, and a rebuilt DOCX/PDF layout check.

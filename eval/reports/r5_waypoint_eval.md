# R5 waypoint evaluation: recording_20260825_222315

Eight waypoints along the designed loop (operator's specification, 2026-08-26: start, back ~30 cm, left ~45 cm with a handover, forward ~15 cm, up ~30 cm, along the wire with a second handover, back to start). Seven pause stations are detected from the ArUco box-centre track alone; the start point is the parked rest position. The measured trajectory is compared with the ideal polyline through the eight waypoints. Stored frame: desk-marker world (unleveled), metres; geometric reasoning and the figure use the gravity-leveled frame (the marker stand is tilted 31.7 deg). Driver: eval/gt/detect_waypoints.py.

Detected station count: 7 of 7 expected - PASS. Waypoints total: 8 (start added from the rest position).

## Constants and their origin

| constant | value | origin |
|---|---|---|
| SMOOTH_WIN | 5 frames | position moving average, 0.17 s; same window as the existing dwell detector (path_metrics.detect_dwells, E-008) |
| SPEED_WIN | +-5 frames | secant speed over 0.33 s. The 1-frame gradient speed histogram of the carried track is flat from 0 to 10 cm/s (jitter and slow motion are the same order), so it separates nothing; the secant does |
| V_STATION | 4.0 cm/s | centre of the plateau 3.00-4.75 cm/s over which the detected station count is invariantly 7 (sweep table below, sweep panel of the figure). The carried-speed histogram of this recording has no low-speed gap to cut at, so the plateau is the derivation |
| MIN_DUR_S | 0.30 s | 9 frames, just under the 0.33 s span of the speed secant: shorter runs are not resolved by that estimator |
| MERGE_RADIUS | 6 cm | full 3D distance. The closest genuinely distinct pair (left-move end vs forward-push end) is 8.0 cm apart in 3D; the widest same-station sub-run spread (lift-top regrips) is under 3 cm; 6 cm sits between them. The first version of this detector merged in the marker-frame x-y projection, which the 31.7 deg stand tilt compresses - that wrongly fused those two waypoints (3.7 cm apparent) and is why the merge is 3D now |
| MIN_STATION_DWELL_S | 0.50 s | jitter guard only. At V_STATION nothing lies between it and the weakest real station (0.80 s at W8_wire_left), so the station count is not produced by this cut |
| APPROACH_WIN | 15 frames | 0.5 s before the first dwell frame, for the reported approach speed |

## Trajectory span

Manipulation envelope: frames 656-1983. Carried frames: 1136.

Loop traversal: frames 858-1930 (28.62-64.38 s, 1073 frames), of which 1032 have a measured marker and are used for every number below.

The loop is the longest contiguous carried run after bridging carried-mask gaps that contain no detected marker sample - a gap with no measurement is no evidence of a stop. On R5 exactly one gap qualifies (frames 1089-1098, the occluded two-hand handover). The pick-up and set-down excursions at the parked spot fall outside this run and are excluded, which is what keeps the parked spot from being reported as a seventh station.

## Threshold sweep

| threshold (cm/s) | stations |
|---|---|
| 1.50 | 3 |
| 1.75 | 4 |
| 2.00 | 5 |
| 2.25 | 5 |
| 2.50 | 5 |
| 2.75 | 6 |
| 3.00 | 7 |
| 3.25 | 7 |
| 3.50 | 7 |
| 3.75 | 7 |
| 4.00 | 7 |
| 4.25 | 7 |
| 4.50 | 7 |
| 4.75 | 7 |
| 5.00 | 8 |
| 5.25 | 8 |
| 5.50 | 8 |
| 5.75 | 8 |
| 6.00 | 8 |
| 6.25 | 9 |
| 6.50 | 9 |
| 6.75 | 10 |
| 7.00 | 10 |

7 stations are detected for every threshold from 3.00 to 4.75 cm/s. Moving V_STATION anywhere inside that plateau moves the detected waypoint positions by at most 6.8 mm, so the choice of threshold inside the plateau does not change the geometry:

| threshold (cm/s) | max waypoint shift vs V_STATION (mm) |
|---|---|
| 3.00 | 6.8 |
| 3.25 | 1.1 |
| 3.50 | 1.2 |
| 3.75 | 0.6 |
| 4.00 | 0.1 |
| 4.25 | 2.7 |
| 4.50 | 2.9 |
| 4.75 | 2.9 |

## Detected stations

Position is the dwell-duration-weighted mean of the merged cluster (W1_start: median of the parked rest frames); std is the per-axis spread of the raw track over the dwell frames. Leveled coordinates: gravity = up, height above the tabletop.

| # | id | frames | dwell (s) | marker xyz (m) | leveled xyz (m) | height (m) | std (mm) | note |
|---|---|---|---|---|---|---|---|---|
| 1 | W1_start | 0-655 | parked | -0.255, -0.107, 0.192 | -0.257, 0.015, 0.218 | 0.022 | - | start point (parked rest position on the desk) |
| 2 | W2_back_end | 903-955 | 1.73 | -0.163, -0.240, 0.430 | -0.165, 0.025, 0.491 | 0.032 | 1.5 | end of the back move, on the desk |
| 3 | W3_desk_handover | 984-994, 1025-1059 | 1.47 | -0.077, -0.226, 0.411 | -0.080, 0.025, 0.469 | 0.032 | 13.4 | desk, two-hand handover |
| 4 | W4_left_end | 1195-1234 | 1.30 | 0.165, -0.235, 0.439 | 0.163, 0.027, 0.498 | 0.034 | 4.9 | end of the left move, on the desk |
| 5 | W5_forward_end | 1274-1306, 1313-1336 | 1.83 | 0.178, -0.195, 0.366 | 0.176, 0.022, 0.415 | 0.029 | 6.6 | end of the forward push, on the desk (lift starts here) |
| 6 | W6_lift_top | 1475-1632 | 5.24 | 0.131, 0.047, 0.558 | 0.136, 0.330, 0.451 | 0.337 | 13.9 | top of the lift, on the wire |
| 7 | W7_wire_handover | 1713-1754 | 1.37 | -0.069, 0.045, 0.562 | -0.064, 0.335, 0.454 | 0.342 | 9.7 | on the wire, second handover |
| 8 | W8_wire_left | 1790-1814 | 0.80 | -0.178, 0.038, 0.539 | -0.173, 0.320, 0.438 | 0.326 | 4.9 | wire, left end, before the descent |

No cluster was rejected by the dwell-duration cut: the detected stations are all that the detector produced.

## Designed vs measured steps

The operator's designed moves (nominal, approximate) against the measured waypoint geometry in the leveled frame (horizontal length for desk moves, height change for the lift). The left move is measured sequentially from the back-move endpoint; measured execution can differ from the nominal figure without affecting the evaluation, which compares the trajectory against the DETECTED waypoints.

| step | move | nominal (cm) | measured (cm) | delta (cm) |
|---|---|---|---|---|
| W1_start -> W2_back_end | back | 30 | 28.7 | -1.3 |
| W2_back_end -> W4_left_end | left | 45 | 32.8 | -12.2 |
| W4_left_end -> W5_forward_end | forward | 15 | 8.4 | -6.6 |
| W5_forward_end -> W6_lift_top | up | 30 | 30.8 | +0.8 |

## Trajectory vs the ideal polyline

The ideal path is the closed polyline through the eight waypoints in traversal order, including the closing segment W8 -> W1. Distances are 3-D point-to-segment, nearest segment wins.

Overall over 1032 loop frames: median 0.79 cm, p95 9.32 cm, max 13.11 cm, mean 1.66 cm.

| segment | length (cm) | frames | median (cm) | p95 (cm) | max (cm) |
|---|---|---|---|---|---|
| W1_start -> W2_back_end | 28.7 | 136 | 0.66 | 11.74 | 13.11 |
| W2_back_end -> W3_desk_handover | 8.9 | 76 | 0.75 | 1.93 | 2.27 |
| W3_desk_handover -> W4_left_end | 24.4 | 147 | 0.45 | 1.92 | 2.59 |
| W4_left_end -> W5_forward_end | 8.4 | 96 | 0.22 | 0.38 | 1.13 |
| W5_forward_end -> W6_lift_top | 31.2 | 264 | 1.22 | 2.12 | 2.41 |
| W6_lift_top -> W7_wire_handover | 20.0 | 158 | 1.09 | 2.22 | 2.35 |
| W7_wire_handover -> W8_wire_left | 11.1 | 72 | 0.36 | 0.6 | 0.7 |
| W8_wire_left -> W1_start | 38.4 | 83 | 5.95 | 12.33 | 13.07 |

Loop closure (measured, carried frames only): the cube leaves the loop at frame 858 and returns at frame 1930; the two positions differ by 46.9 mm ([-27.7, 34.7, 15.1] mm per axis). This is a property of the measured trajectory, not of the polyline, which is closed by construction.

## Limitations

- The eight waypoints are the designed stations. The un-paused corners (the far-left desk corner around frame 767 and the wire's left descent corner around frame 1842) are not waypoints, so the segments crossing them - especially the closing W8 -> W1 descent - carry the largest per-segment error; that number measures the polyline model, not the tracker.
- W1_start is the parked rest position, not a detected dwell: the speed criterion runs on carried frames only, so the start is added from the pre-manipulation rest frames and its position has no dwell statistics.
- The measured forward push (W4 -> W5) is shorter than the nominal 15 cm; the designed figures are approximate and the evaluation compares against the DETECTED geometry.
- Coordinates are detected, not surveyed. They inherit whatever bias the scene calibration and the marker-size correction carry; the numbers here are self-consistent, not traceable to a ruler.
- The first two-hand handover (frames 1067-1109) loses the marker. Those frames are bridged for the loop-span decision but excluded from every statistic, so the desk edge is sampled with a gap. The few frames on either side of that gap are flagged detected but carry an implausible pose (an implied speed above 50 cm/s); they are left in the statistics rather than removed by a hand-set plausibility cut, and they are the samples clipped off the top of the speed panel.

## Outputs

- /home/luo/Desktop/New_SandBox/eval/gt/labeled_path_r5.json
- /home/luo/Desktop/New_SandBox/eval/reports/r5_waypoint_eval.md
- /home/luo/Desktop/New_SandBox/eval/reports/r5_waypoint_eval.json
- /home/luo/Desktop/New_SandBox/eval/reports/r5_waypoints.png


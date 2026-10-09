# Stage 4: ground-truth evaluation (geometry-pending run)

REVISED 2026-08-25 (third pass): numbers computed under the 45 mm
black-square USER ASSUMPTION, traceable solely to
eval/common/marker_size.py (E-009). The survey has not been delivered, so stage
1 ran in geometry-pending mode; path-error tables and the wall
closure fill in by editing eval/gt/labeled_path.json and rerunning
two scripts.

## Path interface

- Schema: eval/gt/path_schema.md; placeholder: eval/gt/labeled_path.json
  (4 waypoints on the wire rectangle, 4 line segments, wall closure
  slot; coordinates null until surveyed).
- Metrics: eval/gt/path_metrics.py (point-to-path with constrained
  axes, automatic dwell detection, dwell-waypoint matching); 14 unit
  checks ALL PASS.

## Measured now, for the survey to close against (corrected scale)

- Path physically identified from the user's photos: a goal-post
  frame on the desk (posts 45 cm apart per the drawn plan; box slides
  along the desk between the posts, up one post, across the crossbar,
  down the other). Tracked at the 45 mm assumption: bottom traverse
  span ~46 cm, top edge at ~39 cm height. (At the depth-implied 43.6
  mm the span is 44.7 cm - the drawn 45 cm slightly favors the
  smaller size; the ruler will settle it.)
- Two dwells (E-008 thresholds, 45 mm assumption):
  - frames 648-742, 3.14 s, at (0.1525, -0.2815, 0.5024) m, cluster
    std under 1 mm (bottom-right corner, hand-over pause);
  - frames 840-861, 0.70 s, at (0.1679, -0.2071, 0.3735) m.
- Calibrated wall marker: unity (-1.242, -0.540, +2.388) m.
- MARKER SIZE to settle with the ruler (E-009): the BLACK SQUARE side
  of desk and object markers; working assumption 45 mm, depth
  diagnostic says 43.6 mm.

## Stage-2 constancy (kinematic wrist vs calibrated ArUco), corrected

| hand | held | median (cm) | p95 (cm) | whole-span drift (cm/min) |
|---|---|---|---|---|
| left | 158 | 13.4 | 17.3 | -21.0 |
| right | 494 | 14.6 | 17.9 | +4.44 (CI +3.52..+5.33) |

Per contiguous grip episode:

| hand | episode (frames) | n | median (cm) | std (cm) |
|---|---|---|---|---|
| right | 254-388 | 134 | 14.3 | 0.64 |
| right | 478-713 | 235 | 14.6 | 1.54 |
| right | 1028-1112 | 85 | 17.0 | 2.04 |
| left | 674-832 | 158 | 13.4 | 1.87 |

Interpretation: within a grip episode the magnitude is constant to
0.6-2.0 cm std; episode medians agree within 2.7 cm across regrips.
Diagnostic note: at the depth-implied scale (43.6 mm) the right-hand
whole-span drift is -0.01 cm/min vs +4.4 at the assumed 45 mm - the
small residual range-dependence is itself evidence the true black
square is nearer 43.6; recorded for the ruler check to settle. The error budget and
near-path consistency check remain PENDING SURVEY.

## To finish stage 4 when the survey arrives

1. Fill xyz/sigma in eval/gt/labeled_path.json; measure the three
   printed markers and settle E-009.
2. python eval/gt/analyze_gt_path.py
3. python eval/offset/analyze_offset_constancy.py

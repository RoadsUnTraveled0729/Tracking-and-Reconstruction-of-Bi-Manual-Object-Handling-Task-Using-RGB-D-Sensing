# Labeled-path description file (labeled_path.json)

The surveyed geometry of the labeled path the box follows on the
testbed. Read by eval/gt/analyze_gt_path.py. Until the physical
survey is delivered, coordinate fields are null and the analysis runs
in geometry-pending mode (dwell detection, trajectory plots, and
dwell-cluster positions are still produced; path-error tables print
PENDING SURVEY).

Frame and units: all coordinates are in the desk ArUco world frame
(marker id 2 = origin, the frame scene_calibration_r4.json's
object_world unity columns live in), meters. This is the same frame
the steel-ruler survey is performed in, per the professor's
definition; the survey-vs-calibration closure check (wall marker)
demonstrates the two frames coincide.

Fields:

- frame: fixed string "desk_marker_world".
- units: fixed string "m".
- survey: method (string), date (ISO date or null),
  default_sigma_m (number or null) - the stated measurement
  uncertainty used for any waypoint without its own sigma_m.
- waypoints: ordered list. Each: id (unique string), xyz ([x, y, z]
  or null while pending), sigma_m (number or null -> default),
  dwell_expected (bool: the protocol asked the carrier to pause
  here).
- segments: list. Each: from/to (waypoint ids), type ("line" is the
  only type implemented), constrained_axes (subset of ["x","y","z"]):
  the axes the segment actually pins down. A straight segment does
  not constrain the coordinate along its own direction; per-axis
  error is only reported for constrained axes, the along-segment
  axis is reported as unconstrained.
- wall_marker_surveyed: xyz + sigma_m of the wall marker center in
  the same frame, for the closure check against the calibrated wall
  pose. Null while pending.

Editing rule: when the survey arrives, fill the null xyz/sigma
values IN PLACE (git records the change); do not restructure.

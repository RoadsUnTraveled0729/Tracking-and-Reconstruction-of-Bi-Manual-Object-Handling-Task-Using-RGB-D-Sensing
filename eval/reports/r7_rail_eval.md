# Rail-path evaluation: recording_20260909_000024 (r7)

Scenario: no occlusion. The cube is lifted from the desk onto a
straight horizontal rail and slid to its far end; the rail is the
physical ground-truth path of the slide. Errors are perpendicular
distances of the tracked cube centre to the total-least-squares
line through the rail-segment samples. Offline geometry, no
causality claimed. Segmentation: rail height is the upper mode of
the height histogram, band = half a cube (3.5 cm). Frame: the
gravity-levelled desk world (y = true vertical from the calibrated
wall marker), not the tilted desk-marker frame the track is stored in.

- frames: 1498/1499 tracked
- desk level 3.4 cm, rail level 7.8 cm above the desk-marker origin
- parked 137 frames; lift 289 frames, travel 23.6 cm, tilt from vertical 88.2 deg
- rail segment: 1072 frames over t = 14.21 to 49.97 s, travel 42.4 cm, line tilt from horizontal 0.09 deg

Rail-line error of the tracked centre:

| statistic | value |
|---|---|
| perpendicular median | 0.26 cm |
| perpendicular p95 | 1.65 cm |
| perpendicular max | 3.44 cm |
| vertical component median | 0.11 cm |
| horizontal component median | 0.2 cm |
| direction reversals while moving | 6 |

The perpendicular error mixes tracking error with how the cube
rides against the rail; the rail constrains the hand, so this is
the tightest ground truth the setup provides.

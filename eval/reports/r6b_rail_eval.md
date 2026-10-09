# Rail-path evaluation: recording_20260831_065553 (r6b)

Scenario: no occlusion. The cube is lifted from the desk onto a
straight horizontal rail and slid to its far end; the rail is the
physical ground-truth path of the slide. Errors are perpendicular
distances of the tracked cube centre to the total-least-squares
line through the rail-segment samples. Offline geometry, no
causality claimed. Segmentation: rail height is the upper mode of
the height histogram, band = half a cube (3.5 cm). Frame: the
gravity-levelled desk world (y = true vertical from the calibrated
wall marker), not the tilted desk-marker frame the track is stored in.

- frames: 899/900 tracked
- desk level 3.5 cm, rail level 7.4 cm above the desk-marker origin
- parked 92 frames; lift 400 frames, travel 25.0 cm, tilt from vertical 88.5 deg
- rail segment: 407 frames over t = 16.41 to 29.99 s, travel 40.9 cm, line tilt from horizontal 0.05 deg

Rail-line error of the tracked centre:

| statistic | value |
|---|---|
| perpendicular median | 0.97 cm |
| perpendicular p95 | 2.36 cm |
| perpendicular max | 3.08 cm |
| vertical component median | 0.32 cm |
| horizontal component median | 0.81 cm |
| direction reversals while moving | 3 |

The perpendicular error mixes tracking error with how the cube
rides against the rail; the rail constrains the hand, so this is
the tightest ground truth the setup provides.

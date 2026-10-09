# Stage 3: recalibration scrutiny + R4 grip fit

REVISED 2026-08-25 (third pass): all numbers below are computed
under the USER-SET ASSUMPTION that the desk and object markers'
black squares are 45 mm (declared 50 mm in frozen frames.py). The
single traceable source of this number is eval/common/marker_size.py;
change it there and rerun the command list in its docstring to
regenerate every dependent number. Context: the markers' cards are
unchanged from R1, but the depth cross-check measured a constant
PnP/depth ratio ~1.145 (depth-implied black square ~43.6 mm, exactly
50 x 7/8 - consistent with prints that render the nominal size
including a quiet-zone module). Uncorrected artifacts kept for
comparison.

## Calibration (eval/output/scene_calibration_r4c.json)

- World origin: desk marker id 2 on a ~32.2 deg tilted stand (R3
  style). All height logic uses the leveled (gravity = +y) frame.
- Gravity: wall in-plane up; depth-seed agreement 4.40 deg. Desk
  anchor stability: pos p95 ~1.3 mm, rot p95 0.245 deg. Calibration
  window (frames 0-9) person-clear.
- origin_above_tabletop +6.8 mm under the 45 mm assumption (was
  -9.7 mm uncorrected).
- Calibrated wall marker (closure target for the survey):
  unity (-1.242, -0.540, +2.388) m in the desk-marker frame (wall
  kept at its declared 150 mm).

## Grip fit (eval/reports/recording_20260825_070152_offset_fit.json)

Carry story: right hand 7.5-19.5 s, both hands 19.5-23.5 s, left
23.5-27.5 s, left with wrist OCCLUDED 27.5-35.5 s (no measurable
holder), right 35.5-43.8 s.

Per-hand fit on held frames (E-005..E-007 classifiers), corrected:

| hand | frames | object-frame mu (cm) | std (cm) | resid med/p95 (cm) | |wrist-center| med/p95 (cm) |
|---|---|---|---|---|---|
| left | 157 | (+0.9, -5.7, +14.2) | (3.2, 1.0, 1.2) | 2.6 / 6.1 | 14.5 / 16.8 |
| right | 493 | (-3.8, -5.4, +8.3) | (7.3, 3.8, 9.5) | 10.2 / 21.7 | 15.6 / 17.9 |

Findings:

1. After the scale correction the left-hand grip is R1-tight (std
   1.0-3.2 cm, residual median 2.6 cm). The right-hand full VECTOR
   still varies (std up to 9.5 cm) because the right hand genuinely
   regrips while tracing the wire; its MAGNITUDE is tight per episode
   (std 0.7-2.0 cm, see stage 4). Magnitude as the primary metric is
   validated twice over.
2. The R1 carried/nearest-wrist classifiers fail on R4 (E-005/E-006
   evidence); eval-side classifiers replace them. Frozen v1 untouched.
3. R4 limb lengths are left-right symmetric (forearms 0.228 / 0.221
   m, upper arms 0.272 / 0.273 m) where R1 measured a 4.7 cm forearm
   asymmetry; the R4 set is the more self-consistent one and feeds
   the sphere fallback.
4. Depth-collapse specimen: right forearm apparent length falls to
   3-10 cm around 38-41 s with visibility high (gate-miss specimen,
   quantified in stage 5).
5. Object-marker planar ambiguity: 1308/1495 object detections
   gravity-resolved (near-frontal views) - object ROTATION is noisy
   on R4; magnitude uses rotation only through the 3.5 cm half-cube
   lever.

## Validation

eval/validate/validate_eval.py ALL PASS (16 checks) on the corrected
outputs, including the vendored-core regression against the pinned R1
numbers (0.05 cm) and the fusion-display firewall.

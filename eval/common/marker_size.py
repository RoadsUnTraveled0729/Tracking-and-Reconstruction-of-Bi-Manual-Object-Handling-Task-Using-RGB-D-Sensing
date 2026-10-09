"""THE marker-size assumption for R4 (single source of truth).

USER-SET ASSUMPTION (2026-08-25): the detected black-square side of
the R4 desk and object markers is 45 mm, pending a definitive ruler
measurement. The wall marker stays at its declared 150 mm.

Every R4 number that depends on marker size traces back to THIS
table and nowhere else:

  marker_size.py (here)
    -> eval/gt/scale_correction.py (rescales the raw ArUco CSV)
      -> eval/output/<stem>_aruco_raw_scaled.csv (+ meta with the
         assumption recorded)
        -> eval/output/scene_calibration_r4c.json (calibrate_scene)
        -> eval/output/<stem>_scaled_object_world_filtered.csv
          -> every eval analysis via paths.r4_calib() /
             paths.object_world_filtered()

To change the number: edit ASSUMED_BLACK_SQUARE_M below, then rerun
  python eval/gt/scale_correction.py
  python v1/aruco/calibrate_scene.py --csv eval/output/<stem>_aruco_raw_scaled.csv \
      --cube-size 0.07 --calib-frames 10 --out eval/output/scene_calibration_r4c.json
  python v1/aruco/filter_object_track.py --csv eval/output/<stem>_scaled_object_world.csv
  python eval/offset/fit_offset.py
  python eval/offset/analyze_offset_constancy.py
  python eval/gt/analyze_gt_path.py && python eval/gt/plot_path.py
  python eval/occlusion/gate_sweep.py && python eval/occlusion/harness.py
  python eval/occlusion/events.py && python eval/occlusion/fusion_display.py
  python eval/validate/validate_eval.py

Context (E-009): the frozen v1/aruco/frames.py declares 50 mm; the
depth cross-check measured a constant PnP/depth ratio of ~1.145,
implying ~43.6 mm; the drawn-path spans support ~44-45 mm. The user
chose 45 mm as the working assumption. Reference diagnostics stay in
eval/reports/r4_marker_scale.json.
"""

# Detected black-square side length, meters, per marker id.
ASSUMED_BLACK_SQUARE_M = {
    0: 0.150,   # wall  - unchanged print
    1: 0.045,   # object - USER ASSUMPTION 2026-08-25 (E-009)
    2: 0.045,   # desk   - USER ASSUMPTION 2026-08-25 (E-009)
}

# What the frozen extractor believed at PnP time (v1/aruco/frames.py).
DECLARED_M = {0: 0.150, 1: 0.050, 2: 0.050}

# Exact per-marker translation rescale: actual / declared.
SCALE = {mid: ASSUMED_BLACK_SQUARE_M[mid] / DECLARED_M[mid]
         for mid in DECLARED_M}

# eval/ - ground-truth evaluation track

Purpose: the evaluation of the offline v1 pipeline, separated into two
scenarios (E-023):
- WITH occlusion: primary recording R5 (recording_20260825_222315,
  70 s, 2099 frames, 30 fps): where MediaPipe fails and why, the
  object-conditioned pose recovery that answers those failures, the
  8-waypoint trajectory evaluation of the tracked box, and the
  Unity-vs-video fidelity check.
- WITHOUT occlusion: primary recording R6B (recording_20260831_065553,
  30 s, 900 frames): the revised setup with a straight
  raised rail as the physical ground-truth path; evaluated by
  eval/gt/eval_rail_scenario.py (rail-line fit, perpendicular errors;
  report reports/r6b_rail_eval.md). detect_waypoints.py stays pinned
  to the R5 step plan and is not applied here.
- HANDOVER on the rail: R7 (recording_20260909_000024, 50 s, 1499
  frames, recorded 2026-09-09 for supervisor round 6): the right hand
  slides the cube to about 30 cm along the rail, the left hand takes it
  over and slides it to the far end. Same chain, with the gravity
  carried over from the R6B calibration because the wall card had
  shifted (E-034); reports r7_rail_eval.md, r7_failure_mask.md,
  r7_handover.md (handover_analysis.py), r7_hip_hold.md
  (compare_hip_hold.py, the opt-in hip hold of E-034), r7_waypoints.json
  (rail_waypoints.py), unity_check_r7/ (E-035).

Status: the R5 experiment round was frozen on 2026-08-26 (user
decision: "the experiment is good for now", E-001..E-019). Later
corrections and rail/handover work are recorded separately in
[DECISIONS.md](DECISIONS.md), E-020 onward; their pinned reports remain
part of the evaluation record. The R4 artifacts remain for reproducibility.
The v1 tree is frozen: eval code imports v1 modules read-only via
sys.path or vendors small pure functions with provenance headers;
the one sanctioned exception is the additive robust layer
v1/kinematics/occlusion_ext.py (E-011/E-011b/E-012/E-014).

Layout:
- common/: paths.py (all stems and file locations, one place),
  marker_size.py (confirmed 45 mm desk/object black squares;
  frozen 0.050 m PnP declaration, 0.9 translation rescale before
  calibration; [standing rule](../AGENTS.md)),
  clean_object_track.py (the one-pass object-track cleaning filter,
  E-019 - the only marker-side mechanism, per
  skill_set/marker-simplicity.md).
- inspect/: recording inspection (coverage, phases, occlusion event
  inventory, anchor hard-check), the A6 tracking-precondition
  checker (E-013), plot renderings, and check_v1_overlay.py (FK
  reprojection onto the color video; --recovery renders the E-014
  solve with failure banners).
- failure/: the R5 failure study and the recovery pipeline -
  detect_failures.py (detectors D1-D5, E-015), grip_state.py
  (grip episodes + time-local mu, E-016/E-014a), recovery_core.py
  (solve variants, D6 grip bound, E-014b), run_recovery.py (angle
  track CSVs incl. the repaired pelvis), harness_recovery.py +
  moving_window_check.py (the E-013-compliant synthetic evaluation).
- gt/: labeled-path interface, path metrics, detect_waypoints.py
  (the 8-waypoint evaluation, E-017a), scale correction.
- offset/: carry/grip classification and offset-constancy analysis.
- occlusion/: gate sweep, fallback solvers, comparison harness (R4).
- unity_check/: Unity-vs-video verification (internal, not thesis) -
  vendored sender with display smoother (E-018), autonomous editor
  capture, side-by-side builder, marker textures.
- validate/: assertions over eval outputs (validate_eval.py).
- output/: large regenerable files (gitignored).
- reports/: small pinned summaries and plots (committed). Key R5
  reports: r5_object_conditioned_recovery.md (the mathematics
  deliverable), r5_failure_mask.md, r5_recovery_synthetic.md,
  r5_recovery_moving.md, r5_waypoint_eval.md, r5_unity_check.md.
- akc_comparison/: exploratory sub-study, outside the FROZEN
  E-001..E-019 evaluation - a from-the-paper re-implementation of
  Kwok, Koenig and Hu's Arm Kinematic Correction (arXiv 2606.19240,
  no code released) run against our occlusion recovery on r5, r6b
  and r7 under shared masks; own README.md and DECISIONS.md
  (AKC-001 onward).

Pinned chain for a NEW recording (stem <s>):
    python v1/mediapipe/extract_landmarks_to_csv.py --bag Video/<s>.bag
    python eval/inspect/check_tracking_precondition.py --stem <s>
    python v1/mediapipe/filter_landmarks.py --csv v1/mediapipe/output/<s>_landmarks_raw.csv
    python v1/aruco/extract_aruco_poses.py --bag Video/<s>.bag
    python eval/gt/scale_correction.py --stem <s>
    python v1/aruco/calibrate_scene.py --csv eval/output/<s>_aruco_raw_scaled.csv \
        --cube-size 0.07 --calib-frames 10 --out eval/output/scene_calibration_<alias>c.json
    python v1/aruco/filter_object_track.py --csv eval/output/<s>_scaled_object_world.csv
    python eval/common/clean_object_track.py --stem <s>
    python eval/inspect/inspect_recording.py --stem <s>
    python eval/offset/fit_offset.py --stem <s> --calib <calib>
    python eval/failure/detect_failures.py --stem <s>
    python eval/failure/run_recovery.py --stem <s>
    python eval/gt/detect_waypoints.py --stem <s>   # waypoint-scenario recordings only
    python eval/gt/eval_rail_scenario.py --stem <s> # rail-scenario recordings only
    python eval/inspect/check_v1_overlay.py --stem <s> --recovery
(register the stem in eval/common/paths.py ALIAS first; thresholds
are physical or derived plot-first with an R1 zero-fire requirement,
so the chain adapts to new recordings without retuning)
    # rail takes only, after eval_rail_scenario.py:
    python eval/gt/rail_waypoints.py --stem <s>        # <alias>_waypoints.json
    python eval/failure/handover_analysis.py --stem <s> # two-hand takes
    python eval/failure/compare_hip_hold.py --stem <s>  # hip hold study (E-034)
If the wall card has moved since an earlier take of the same scene
(check: the depth-seed agreement printed by calibrate_scene.py jumps
from about 6 to 30 deg while the camera-to-desk pose is unchanged),
add --gravity-from eval/output/scene_calibration_<earlier alias>c.json
to the calibrate_scene.py step; it refuses when the camera-to-desk
poses differ by more than 3 deg or 3 cm, or when this take's depth-fitted
tabletop normal is farther from the carried gravity than the source
take's own seed agreement plus 5 deg (E-034).

All offline analysis feeds frames strictly in order with no lookahead
where a causal variant is intended; deviations are stated per tool.
Plain text output only; "deg" not degree signs.

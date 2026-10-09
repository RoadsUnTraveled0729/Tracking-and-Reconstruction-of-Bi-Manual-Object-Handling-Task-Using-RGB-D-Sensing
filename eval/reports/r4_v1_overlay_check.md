# v1 correctness check: reconstruction reprojected onto the video

## What the check is

eval/inspect/check_v1_overlay.py verifies the v1 chain with zero
Unity and zero calibration involvement: filtered landmarks (sensor
frame) -> unity_from_sensor flip -> ChainFallbackSolver /
RobustChainSolver -> 13 angles -> forward kinematics
(KINEMATIC_MODEL conventions, fixed segment lengths = median of
clean frames) -> flip back to sensor frame -> pinhole projection ->
overlay on the real color frames of the bag. If the drawn skeleton
sits on the real person, the v1 measurement + solve + model are
correct; any Unity mismatch is then downstream (merger / receiver
composition - both of which were separately verified exact: anchor
rotation composition error 0.00 deg, position error 0.00 cm on both
the R1 and R4 calibrations).

Overlay legend: green = measured landmarks, red = FK right arm,
blue = FK left arm, magenta = root forward arrow.

## Key numbers (R4, robust solver)

- FK wrist vs measured wrist residual: right median 1.5 cm,
  p95 8.7 cm; left median 2.0 cm, p95 4.7 cm.
- Fixed segment lengths (median over frames with both endpoints
  measured, src == 0): upper arm R 0.273 / L 0.272 m, forearm
  R 0.221 / L 0.228 m.

## Findings

1. The arm chain is correct whenever MediaPipe measures correctly:
   at t = 15 s and t = 45 s both FK arms sit exactly on the real
   arms in the overlay.
2. Right-arm MediaPipe failure at 36-41 s: with the cube held
   against the chest, the measured wrist lands on the jacket at
   visibility 0.98 and the measured forearm collapses to 0.076 m
   against the 0.221 m calibrated length; 75 percent of the window's
   frames violate the 30 percent segment gate. This is a measurement
   fault, not a solver fault; the robust layer gates most of it
   (the "hand inside body" symptom in the first Unity render).
3. Root direction corruption windows (hip line 18-24 s, shoulder
   line 34.5-36 s) drove the "body changes direction suddenly"
   symptom; fixed by the E-011 torso line-consistency gate
   (eval/DECISIONS.md E-011, r4_stage6b_robust_live.md).
4. f951 (user-flagged, t ~ 31.7 s): MediaPipe is not following the
   raised left hand at all - the left elbow/wrist report visibility
   0.06-0.22 for ~8 s while the hand wraps behind the carried cube,
   so the landmarks are honestly missing (src = 1) and the solver
   correctly holds. The heavy model (pose_landmarker_heavy.task, GPU
   delegate) is confirmed in use for both recordings and the live
   pipelines, so this is not a model-tier issue: no landmark model
   can see through the cube. This is a scenario-protocol problem.

## A6 tracking precondition (from finding 4)

USER-SET precondition (ASSUMPTIONS.md A6, eval/DECISIONS.md E-013):
an accuracy-evaluation window is valid only where the landmarks it
grades are tracked - coverage >= 95 percent and no continuous gap
longer than 0.5 s over the person-present span. Enforced by
eval/inspect/check_tracking_precondition.py (run after every new
extraction). Occlusion robustness is evaluated by synthetically
masking tracked segments (truth known by construction), never on
naturally occluded stretches.

R4 verdicts (eval/reports/r4_tracking_precondition.json): torso
PASS, right hand PASS, LEFT hand FAIL - wrist coverage 55.4
percent, longest gap 8.8 s. The left-carry phase (~28-36 s) is out
of evaluation scope in R4. R1 passes everything, so the checker
discriminates correctly.

## Artifacts

eval/output/v1_check/ (gitignored, regenerate with the script):
- v1_overlay_robust.mp4 - the overlay video (robust solver FK; earlier iterations wrote v1_overlay_baseline.mp4)
- v1_check_plots.png - root yaw baseline vs robust, pelvis
  top-down track, FK wrist residuals
- root_lines.png - hip-line vs shoulder-line yaw deviations and
  their 3D disagreement against the 20 deg gate

Regenerate:
    /home/luo/anaconda3/bin/python eval/inspect/check_v1_overlay.py \
        --stem recording_20260825_070152 --solver both \
        --video-solver robust

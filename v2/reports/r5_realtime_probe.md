# R5 real-time probe: the v1 feature set running live

Date: 2026-08-26. Purpose: proof of concept that the rig model runs in
real time in a lightweight way while preserving as much of the frozen
R5 evaluation round's feature set as possible (user direction). The v2
stack executes the R5 recording (recording_20260825_222315, 2099
frames, 70 s) at recorded pacing and streams to Unity; the same code
path runs against the physical sensor by switching the capture broker's
source (`--source live`), because every ported feature sits downstream
of the shared-memory frame ring.

Command:

    python v2/calibration/make_r5_calib.py          # once
    python v2/integration/run_v2.py --source bag --probe-r5 --dump
    python v2/integration/validate_v2_r5.py         # 13 checks

All probe features are opt-in flags (`--probe-r5` enables the set);
with the flags off the stack is the pinned validated v2 behavior.

## Feature preservation

PRESERVED UNCHANGED - these live inside RobustChainSolver
(v1/kinematics/occlusion_ext.py), are causal by construction, and run
live via the existing `--robust-occlusion` flag:
- E-011 gates (segment length, torso line consistency)
- E-011b torso ray repair + 10 cm consensus depth-jump gate
- E-012 twist hold + 15 deg/frame slew limit
- E-014 wrist-from-object + two-link IK elbow mathematics

PRESERVED WITH NEW WIRING (this probe's work):
- E-014 object conditioning: Pipeline A reads Pipeline B's PSB2 pose
  (latest-wins seqlock), reconstructs the camera-frame object exactly
  (the unity/world maps are involutions, T_cam_desk from the scene
  calibration), and an online grip tracker feeds the solver's obj
  input (v2/common/object_link.py).
- E-019 plausibility gate: Pipeline B rejects a detected sample
  farther than the physical bounds allow from the last kept sample,
  ahead of its causal filter (`--plausibility-gate`).
- E-018 display smoother: the merger (v2's Unity sender) shapes the
  output packet with the low-pass + rate cap (`--display-lpf`); every
  dump CSV stays unfiltered.
- Solver tags to Unity: PSR2 carries the 7 group tags in PSR1's former
  pad bytes (same 84 B layout, new magic); the merger routes them
  through the delay buffer (elementwise max across interpolation
  brackets, floored to HELD on merger holds) into the PSI2 pad. The
  Unity receiver turns a red (held) joint sphere BLUE when its group
  is CONSTRAINED - recovered geometry, not a hold.

ADAPTED FOR CAUSALITY (same math, online form):
- The grip offset mu: offline fitted per episode in the leveled desk
  world; live it is the time-local EMA (alpha 0.02, warmup 5) fitted
  directly in solver space - a rigid grip offset is constant in any
  fixed frame, so the leveled-world detour adds nothing.
- "Carried": offline used the rest-referenced envelope (needs the
  whole recording); live the rest pose is the median of the first 30
  live object samples and carried = displaced from it. It gates
  episode ENTER only, so waypoint dwells do not churn episodes.
- Episode EXIT cannot retro-clear release frames the way the offline
  state machine does: a true release keeps the wrist box-anchored for
  up to EXIT_FRAMES (5) frames before the episode closes. This is the
  one bounded causality cost of the port.

OFFLINE-ONLY BY NATURE (analysis tools, not runtime features):
waypoint evaluation, the D1-D5 failure study as a graded mask (live,
the solver's own gates play that role; D6 runs live in the tracker),
synthetic-masking accuracy evaluation, the overlay video.

## Measured results (full R5 run, all features on)

Real time, sustained:

    frames consumed        2099/2099 (0 skipped by latest-wins), 29.6 fps
    person compute         p50 9.0 ms   p99 25.1 ms   (budget 33.3 ms)
    solve within it        p50 0.40 ms  p99 0.56 ms
    object compute         p50 13.1 ms  p99 15.1 ms
    merger tick cadence    p50 33.3 ms  p99 35.3 ms  (steady 30 Hz)
    output delay           2 frames (66.7 ms), declared

The whole recovery layer costs ~0.06 ms per frame on top of the
robust solve (0.34 -> 0.40 ms p99): the report's "closed-form O(1)"
claim, measured.

The features fired where the offline study says they should:

    grip episodes (live)   right 598-1188, 1669-2013; left 1037-1807
                           (the overlaps ARE the two handovers; live
                           estimates cover 90 / 89 percent of the
                           offline holding frames, entering a few
                           frames later by causal hysteresis and not
                           sub-segmenting where offline retro-cleared)
    wrist from object      255 frames left, 19 right (obj_recovered)
    elbow two-link IK      227 left, 145 right
    D6 wrong-measurement   17 left, 8 right
    E-019 gate             27 rejects (offline cleaner: 42; the live
                           gate acts BEFORE the One-Euro filter, the
                           offline cleaner after it - same order, same
                           windows)
    torso ray repair       hips gated ~540/544 frames, recovered on
                           rays (the R5 depth-corruption stretches)
    B-A frame skew         p50 -1, p99 0 frames; 0 dropped as stale

Validation: `validate_v2_r5.py` 13 checks ALL PASS - real-time budget,
causal lag 3 frames vs the offline reference (v1's documented lag),
worst joint-group median 0.47 deg / p95 2.76 deg on clean frames,
recovery firing inside the offline failure windows, tags present in
the merger output. Old-recording regression (all flags off):
validate_v2.py 21 checks (count corrected 2026-08-28; the script emits 21) - see v2/dataset/r5_probe_validation.txt.

## The calibration trap (one-time setup fix)

eval's scene_calibration_r5c.json records the DECLARED 50 mm marker
size while its transforms are true-scale (built from the
scale-corrected track, E-009). Live PnP feeds that size field
directly, which would overscale translations ~11 percent against the
desk anchor. make_r5_calib.py writes the v2 copy with the true 45 mm
sizes; the live path needs no scale layer at all.

## Sensor-switch checklist (--source live)

The switch already exists: the capture broker owns the device and both
pipelines read the same frame ring, so the probe behavior carries to
the camera unchanged. What a live session needs:
1. `--calibrate` reruns the scene calibration from the stream;
   live_calibrate.py must be given the TRUE marker sizes (same E-009
   fix as make_r5_calib.py applies to the bag path) - or the markers
   reprinted at declared size and measured with a ruler (E-009a, still
   open).
2. The initial-rest warmup of the grip tracker assumes the object
   starts at rest in view for ~1 s (true of the task design).
3. Everything else is source-independent by construction.

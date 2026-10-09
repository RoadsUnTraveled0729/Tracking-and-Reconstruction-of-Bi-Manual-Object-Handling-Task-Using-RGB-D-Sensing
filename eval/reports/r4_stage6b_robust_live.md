# Stage 6b: robust occlusion solver wired into the live pipelines

## What changed (and what did not)

The KINEMATIC MODEL IS UNCHANGED: root-frame construction, the
swing-twist shoulder decomposition, the elbow solve, and the
hold-last fallback (root_frame.py, shoulder.py, occlusion.py) are
untouched. The robust layer (v1/kinematics/occlusion_ext.py) only
decides which wrist MEASUREMENTS to trust before the identical solver
runs: implausible-forearm-length wrists become missing (gate), and a
missing wrist with a live elbow gets a constrained sphere estimate.
Angle definitions, packet formats, and all default behavior are
identical; the feature is opt-in:

    v2/integration/run_v2.py --robust-occlusion ...   (passes through)
    v2/person/v2_person.py --robust-occlusion
    (v1 realtime wiring: same flag pattern, pending)

With the flag off, output is bit-identical to the baseline
(validate_occlusion_ext.py check 1).

## R4 live A/B (v2 stack, identical bag replay; baseline dumps kept
## in eval/output/v2_dump_baseline_r4/)

- Throughput unchanged: 29.4 fps sustained, person p99 23.9 ms vs
  23.8 baseline - the robust layer costs nothing measurable.
- Live-mask changes: 148 frames DEMOTED (bits cleared), 0 frames
  gained - the solver only ever became more honest, never claimed
  more. All demotions are right-side and concentrated in the
  depth-collapse regions (frames ~1116-1289 = the 37-43 s stretch
  where the wrist depth lands on the wrong surface with high
  visibility). Left side: 0 demotions - its failure mode is
  missingness, which the causal filter already converts correctly.
- UPDATE (universal chain layer, same day): the layer now applies
  the same gate + recovery at every chain link (hips, shoulders,
  elbows, wrists), so both failure regions improve. Against the
  offline universal-layer reference:

  | window | stack | median (deg) | p95 (deg) |
  |---|---|---|---|
  | R depth collapse 1110-1300 | baseline live | 7.37 | 161.55 |
  | R depth collapse 1110-1300 | robust live | 1.52 | 25.06 |
  | L real occlusion 833-1096 | baseline live | 1.20 | 17.63 |
  | L real occlusion 833-1096 | robust live | 0.55 | 7.68 |

  Live counters on R4: gated right_wrist 99 / right_elbow 49 /
  left_shoulder 10 (the stage-2 background-bleed specimen, caught by
  the torso diagonal); recovered left_wrist 256 / left_elbow 173
  (the long real occlusion, chained shoulder -> elbow -> wrist) plus
  shoulder/hip recoveries. Mask changes vs baseline: 179 demotions,
  0 gains; p99 compute 24.3 vs 23.8 ms.

## E-011: torso line-consistency gate (root direction stability)

Added after user review of the first R4 Unity reconstruction
rejected the body's direction behavior ("changes direction
suddenly"). Diagnosis: hands/cube crossing in front of the torso
poison the hip/shoulder landmark DEPTH samples while 2D visibility
stays ~0.98 (so the visibility gate B1 cannot fire) and the pair
width stretches less than 11 percent (so the width gate B2 cannot
fire). The corrupted line rotates 25-40 deg and drags the root frame
with it. R4 shows both variants: hip-line corruption at 18-24 s,
shoulder-line corruption at 34.5-36 s.

The gate (occlusion_ext.py, full rationale and thresholds in
eval/DECISIONS.md E-011): when the hip line and shoulder line
disagree by more than 20 deg (rigid torso, ASSUMPTIONS.md A2;
R1-clean maximum is 18.9 deg), the pair whose direction deviates
more from its own EMA memory is the corrupt one - symmetric
attribution. A single endpoint blamed by its torso diagonal is gated
normally; otherwise the whole line is rebuilt around its measured
midpoint along its memory, steered toward the surviving line.
Hysteresis (release at 10 deg) holds the constraint through R4's
just-under-threshold plateaus. Dependent groups are demoted to
CONSTRAINED.

Measured on R4 (person-present window 4-46 s):

- root yaw deviation p95 31.6 -> 17.1 deg, max 39.2 -> 21.3 deg
- 18-24 s corruption window p95 36.6 -> 18.8 deg
- gate counters (final run): gated left_hip 199 / right_hip 199 /
  left_shoulder 36 / right_shoulder 15 / right_wrist 108 /
  right_elbow 51
- validate_occlusion_ext.py grows to 28 checks (synthetic hip- and
  shoulder-side corruption scenarios), all passing; clean-R1
  behavior bit-identical outside gated frames (zero gate fires on
  all of R1).

Residual limitation: at 24-31 s both lines agree at -10..-23 deg
deviation - consensus corruption is indistinguishable from a real
lean using rigidity alone, so the root there is trusted as
measured.

## Angle-parameter stabilization (E-012 / E-012a)

Second user-review round: "even the video overlay is not stable".
The instability is arm-level parameter noise at the model's two
smooth singularities plus transition snaps, not root wander. Final
stabilization set in the robust layer (eval/DECISIONS.md E-012 and
E-012a):

- Twist observability hold: shoulder twist is HELD (bit clear, tag
  HELD) while elbow flexion is below 15 deg, released above 25 deg
  (hysteresis) - the same unobservability semantics the model
  applies at exact singularity (1/sin(flexion) amplification,
  ASSUMPTIONS.md A4), widened to the noise-aware threshold. R1
  right-arm flexion never drops below 30 deg, so clean data never
  engages it.
- Wrap-aware slew limit of 15 deg/frame (450 deg/s) on every arm
  parameter (theta_y, theta_z, tau, ey), with honest demotion: while
  the limiter actively clamps, the group bit is cleared and tagged
  CONSTRAINED - the output is not the measurement until it
  converges. R1's fastest clean right-side step is 11.4 deg/frame,
  so the limiter never engages on clean data. The root is excluded
  (E-011 owns root robustness).
- A vertical-arm swing-yaw hold was tried and REJECTED (E-012a): it
  kept the swing bit LIVE while the output diverged from the
  measurement, producing 27.4 cm p95 FK-wrist error on nominally
  live frames - a stabilizer must never make a live claim diverge
  from the measurement. The slew limit bounds the vertical-arm
  azimuth flips (94 -> 15 deg/frame) honestly instead.

Measured on R4 (person-present window 4-46 s):

- max per-frame arm step 149.4 -> exactly 15.0 deg, zero violations
- FK wrist residual on fully-live frames: right median 1.3 / p95
  4.4 cm, left median 3.5 / p95 4.9 cm - accurate where claimed
  live; larger deviations only on demoted frames (right 4.7/13.6,
  left 3.9/11.2 cm)
- validate_occlusion_ext.py now 32 checks (section 6: flexion hold,
  honest slewed re-lock, vertical-arm slew bound, clamp+demote),
  all passing
- solve cost p99 0.34 ms - no measurable budget impact

## Provenance

Marker sizes do not enter Pipeline A, so these numbers are
independent of the 45 mm assumption (E-009a). Baseline-vs-robust ran
on the same bag with the same calibration argument.

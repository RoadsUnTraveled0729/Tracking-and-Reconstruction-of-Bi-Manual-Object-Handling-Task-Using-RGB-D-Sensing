# E-020: joint-limited elbow IK (the manipulator idea, tested)

Date: 2026-08-26. User idea: treat the arm as a robot manipulator
(DH-style serial chain) and add joint limits to the occlusion
recovery, e.g. an elbow hidden between a known shoulder and wrist.
Directive: implement it and test whether it works, do not assume.
Raw numbers: r5_joint_limit_ik.json (harness_limits.py, regenerates
the table below), r5_limit_bounds.json (derive_limit_bounds.py).

## 1. The manipulator formalization (liftable to thesis ch. 3/5)

The arm is a serial chain: a 3-DOF shoulder (swing y/z + twist), a
1-DOF elbow (flexion), the wrist as the tracked end point; link
lengths are the calibrated upper-arm and forearm segments. The E-014
elbow recovery IS the inverse kinematics of this chain: given the
shoulder S and wrist W, the elbow lies on the circle where the
spheres |E-S| = L1 and |E-W| = L2 intersect; flexion follows in
closed form from the cosine law. The chain is redundant for a
position target - the elbow may orbit the S-W axis (the swivel, the
chain's self-motion DOF) - and the solver resolves the redundancy by
continuity (the upper-arm EMA direction projected onto the circle)
with a gravity-down prior when no memory exists. Joint limits, in
this formulation, prune the swivel circle to its feasible arc.

## 2. Which limits survive derivation (r5_limit_bounds.md)

- Elbow flexion: identical at EVERY point of the swivel circle (the
  cosine law fixes it from the triangle's side lengths), so it cannot
  discriminate candidates; the IK's cosine clip already bounds it by
  construction. Not a usable swivel limit.
- Shoulder-twist box: REJECTED by the data. R5's clean left arm
  carries real mass at -150..-120 deg of the swing-twist tau
  (241 frames) - tau does not map one-to-one onto humeral rotation,
  so an anatomical +-120 box would reject genuinely measured poses.
- Torso-capsule clearance: the one implementable limit. On clean
  frames of both recordings the elbow never comes closer to the
  pelvis -> shoulder-mid axis than 0.42 shoulder widths (R5) / 0.73
  (R1); the limit is pinned at TORSO_RADIUS_FRAC = 0.334 (strictest
  clean p1 with 20 percent slack), subject-scaled by the measured
  shoulder width.

## 3. Mechanism (implemented, opt-in, validated)

RobustChainSolver(elbow_limits=True): if the prior's swivel point
penetrates the capsule, the feasible circle point angularly nearest
the prior is used instead; an all-infeasible circle falls back to
the prior unchanged (the limit never reduces availability); flag off
is bit-identical. validate_occlusion_ext.py grew 39 -> 42 checks,
ALL PASS - including a constructed cross-body reach where the
gravity prior lands inside the torso and the limit moves the elbow
11.6 cm out to the feasible arc.

## 4. The experiment (E-013 synthetic masking, both recordings)

Elbow masks inside clean tracked stretches; truth = the hidden
measurement; short = 15 frames (fresh memory), long = 75 frames
(prior frozen while the arm moves), object = elbow+wrist masked with
the wrist recovered from the cube (full E-014 path). off = existing
prior, on = + capsule pruning:

    r5/left/short   45 f   off 4.91/5.44 cm (med/p95)  on identical  0 interventions
    r5/left/long   150 f   off 4.64/8.38 cm            on identical  0
    r5/left/object 150 f   off 3.78/5.94 cm            on identical  0
    r5/right/short  30 f   off 1.55/2.15 cm            on identical  0
    r5/right/long   75 f   off 1.37/2.05 cm            on identical  0
    r5/right/object 74 f   off 1.33/1.97 cm            on identical  0
    r1/left/short  135 f   off 3.77/16.11 cm           on identical  0
    r1/left/long   375 f   off 5.02/9.77 cm            on identical  0
    r1/right/short 135 f   off 2.30/6.07 cm            on identical  0
    r1/right/long  375 f   off 2.34/4.63 cm            on identical  0

Natural failure windows (the real E-014 recovery over the full R5
failure masks, 383 IK elbow placements): 0 interventions - outputs
bit-identical with limits on.

## 5. Verdict

The idea is geometrically sound and the mechanism provably works,
but on this task's data it never fires: across ~1500 synthetically
masked frames on two recordings and all 383 natural IK recoveries,
the continuity prior never once proposed a torso-penetrating elbow,
so the limit changed nothing (all error numbers identical to the
fourth digit). The reason is visible in section 2's numbers: this
task keeps the elbows far lateral of the torso axis, and the EMA
prior inherits that feasibility from the frames before the loss.

Disposition: kept as an opt-in safety guard (elbow_limits=True) - it
costs nothing when inactive, and the validator proves it catches the
cross-body case this task never produces. For the thesis, the
manipulator formulation of section 1 is the right presentation of
the recovery (it matches the supervisor's requested robot-style
schematic), the feasibility constraint is stated as part of that
formulation, and the honest evaluation sentence is: on the recorded
tasks the continuity prior alone already kept every recovered elbow
inside the feasible arc, so the limit acted as a verified invariant
rather than a correction.

## 6. What would make the limits earn their keep

A task with cross-body reaches or object transfers in front of the
chest (the constructed validator case) is where the gravity/stale
prior can propose infeasible elbows. If a future recording includes
such motion, rerun harness_limits.py - the interventions counter and
the off/on error split answer the question for that data
automatically.

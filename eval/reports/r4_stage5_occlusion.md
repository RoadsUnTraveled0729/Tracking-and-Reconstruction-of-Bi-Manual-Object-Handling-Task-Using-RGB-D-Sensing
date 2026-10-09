# Stage 5: occlusion analysis on R4

## Real-occlusion inventory

44 events total; 37 in scene; 25 overlap carry segments
(r4_occlusion_events.csv). Dominant causes: the carried box blocking
the left arm (left wrist 264 + 207 frame events, left elbow 189 +
122), the person crossing the wall marker during approach (52
frames), and 4 short object-marker view losses. Entry/retreat
out-of-scene runs are inventoried but excluded from all robustness
statistics.

## Visibility-gate miss rate and threshold sensitivity

(r4_gate_sweep.md, permissive --min-vis 0 extraction, two independent
wrongness tests)

- Offset test (vs box + fitted grip, > 3 std, inside grip episodes;
  scale-corrected track): 0 wrong right-wrist cells and 3 wrong
  left-wrist cells kept at every threshold - the gate passes
  essentially no gross position errors during holds.
- Segment test (forearm length off > 30 percent, manipulation
  frames): the right wrist has 167 demonstrably wrong cells KEPT at
  every threshold 0.3-0.6; even 0.7 keeps 148 while discarding 7
  percent of good data. These are depth-collapse frames (elbow and
  wrist landing on the same surface, 6-8 s and 37-41 s) whose 2D
  visibility stays high: THE GATE CANNOT SEE DEPTH ERRORS. At the
  current 0.5 gate the kept-but-wrong rate is 15.3 percent of
  manipulation-phase right-wrist cells.
- Threshold sensitivity: right-wrist retention is flat (96 percent)
  from 0.3-0.6 - the 0.5 choice is not load-bearing there. Left-wrist
  retention falls 80 -> 19 percent across the sweep; lowering the
  gate to 0.3 would recover 394 left-wrist cells, none of which the
  offset test flags as wrong (verifiable only inside grip episodes).
- Conclusion for the thesis: the 0.5 gate handles the missingness
  failure mode (left arm) but a visibility threshold at ANY level
  cannot catch the depth-substitution failure mode; a segment-length
  gate is the complementary check.

## Fallback comparison (Table 6.3 equivalent: r4_table63_equiv.md)

Synthetic (six R1 scenario designs regenerated at the same run
fractions inside R4's person-present span, all zero shift; truth =
unmasked solve; regression guard on the pinned R1 masked data passes
with exact zeros):

- Sphere-constrained wrist recovery wins both wrist scenarios:
  wrist_long p95 38.2 deg vs hold 66.0 vs cv-extrap 93.7; recovery
  step 32.9 vs 61.8 vs 89.5 deg. It cannot help (= hold) when the
  elbow or more is gone.
- Constant-velocity extrapolation in angle space HURTS in most
  scenarios (wrist_long p95 93.7 vs hold 66.0; root_ref 24.8 vs
  11.5); it helps marginally only for whole-pose loss (p95 21.7 vs
  30.4). Ten frames of carried-arm motion are not constant-velocity
  in Euler space. Honest verdict: not recommended as the default.
- Real event (long left-wrist occlusion, frames 833-1096, box in the
  left hand), graded against box_center + fitted grip offset
  (evaluation reference only; scale-corrected track, E-009): the
  sphere method applies on just 47 of 264 frames (the left ELBOW is
  co-occluded for the rest) and on those frames does not beat the
  hold-point baseline (median 7.2 vs 5.6 cm); over the whole event
  the stale hold-point runs at 36.7 cm median. R4's real occlusion
  blocks elbow+wrist together, which caps what any wrist-only
  recovery can do.

## Display-only fusion

fusion_display.py fills 445 left-wrist frames (the occluded carry
stretch) from box + offset with flag 9 for the Unity display.
validate_eval.py now asserts the firewall: no reports artifact
derives from the fusion CSV and no flag-9 sample exists in analysis
inputs. ALL PASS.

## Causality

All three solvers are causal by construction (EMA state, last-valid
holds, no lookahead); the harness feeds frames strictly in order. A
real-time variant is the same class fed by the live stream.

## Recommendation forming for the thesis

Hold-last remains the right default; add the segment-length gate as a
depth-error catch (it is also what the fit already uses via E-007);
present sphere recovery as the bounded-gap wrist option with its
live-elbow precondition stated; report cv-extrap as evaluated and
rejected with the numbers above.

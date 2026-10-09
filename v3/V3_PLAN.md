# V3: RTMPose real-time occlusion exploration (isolated worktree track)

## Context

V3 answers one research question: the most ROBUST way to handle
occlusion in real time -- explicitly not v1's freeze/hold and not a
Bayesian-network recovery. It modernizes the detector (RTMPose-m,
COCO-17, via rtmlib + ONNX Runtime) while keeping the SAME kinematic
model semantics as the thesis, so V1-vs-V3 comparison stays possible.
It is an exploration track: nothing from it may reach the thesis except
by an explicit later promotion decision by the user.

Timing: originally scheduled after the mid-September thesis freeze; on
2026-08-06 the user directed implementation to start immediately, with
isolation from the thesis (v1/v2) as the binding requirement. The
defense retains absolute priority in the main tree.

## Isolation guarantees (hard, user's top requirement)

Redefined by the user on 2026-08-06 (V3_DECISIONS.md D-007): isolation
does NOT mean git separation -- V3 lives in `v3/` on master and is
pushed normally. What must stay isolated:

1. Thesis code and content: no file in the v1/v2 trees (kinematics/,
   mediapipe/, aruco/, realtime/, integration/, unity_bridge/, v2/,
   writing/, thesis/) is ever edited for V3. Reuse is copy-only:
   `v3/vendor/v1/` holds VERBATIM copies used as numerical oracles
   (never edited, hash-checked by a test); other copies are adapted
   freely inside V3 modules. No imports from thesis/v2 trees at
   runtime, no sys.path into them. Nothing from V3 enters the thesis
   text except by an explicit user promotion decision.
2. Unity: V3 gets its OWN scene and its OWN scripts.
   `Unity/Assets/Scenes/V3Scene.unity` + `Unity/Assets/Scripts/V3/`;
   V3 scripts read V3-only shared memory names (/dev/shm/v3_*), so the
   v1/v2 receivers stay dormant in the V3 scene and vice versa. No
   existing scene or script is modified.
3. Environment: dedicated conda env `v3rt` (clone of env `RealSense`),
   base anaconda env and its mediapipe pins untouched. USER-APPROVED
   installs into v3rt only: `onnxruntime-gpu >= 1.19` (~280 MB, reuses
   torch's vendored cuDNN 9.5.1 via LD_LIBRARY_PATH or ort preload)
   plus `rtmlib --no-deps`. RTMPose ONNX weights (RTMDet-nano ~12 MB +
   RTMPose-m ~50 MB, one-time network download) are pinned into
   `v3/models/` (gitignored) and referenced by local path.
4. Data: the .bag recordings are read by absolute path and never
   modified. ~/Desktop/ENSC498 recordings stay read-only.

## Layout and copy map

```
v3-realtime/v3/
  V3_PLAN.md  V3_DECISIONS.md  V3_FINDINGS.md  .gitignore  pytest.ini
  configs/    default.json, scenarios_20260224.json, bench.json
  vendor/v1/  root_frame.py, shoulder.py, occlusion.py   (verbatim oracles)
  detector/   rtmpose_detector.py, box_tracker.py, overlay.py
  core/       representation.py, skeleton.py, convert.py, solver_q.py
  replay/     bag_source.py, depth_sampler.py, causal_filter.py, runner.py
  occlusion/  strategy_base.py, gate.py, baseline_hold.py, s1..s5_*.py
  bench/      latency.py, metrics.py, make_scenarios.py, grade.py
  tools/      extract_bag_to_csv.py, make_synthetic.py, label_gate.py
  tests/      (pytest; default run needs NO onnxruntime)
```

Copies: kinematics/{root_frame,shoulder,occlusion}.py -> vendor/v1
(verbatim); realtime_person.py open_bag_realtime -> replay/bag_source,
CausalLandmarkFilter -> replay/causal_filter, Stopwatch ->
bench/latency (adapted); extract_landmarks_to_csv.py sample_depth +
deproject + CSV/meta pattern -> replay/depth_sampler +
tools/extract_bag_to_csv (adapted, scores instead of visibility);
filter_landmarks.py OneEuro (verbatim class); make_masked_dataset.py ->
bench/make_scenarios (adapted, COCO columns, windows re-derived);
make_synthetic_*.py -> tools/make_synthetic; validate_occlusion.py's
33-check structure -> tests/test_baseline_scenarios.py.

Landmark mapping fixed in core/skeleton.py (the ONLY place indices
appear): v1 names -> COCO-17 5/6 shoulders, 7/8 elbows, 9/10 wrists,
11/12 hips; root frame from COCO 11, 12, 6. The detector emits a dict
keyed by the eight v1 names; everything downstream speaks v1
vocabulary.

## Phase 0 -- metrics defined before building (STOP for user review)

Scenario taxonomy: G-type (synthetic, analytic truth), S-type (masked
windows over the real V3 extraction; truth = the unmasked causal solve
of the identical CSV through the identical stateful pipeline, derived
at grade time, never stored), R-type (real occlusions, no truth: proxy
metrics only).

Metrics (bench/metrics.py, pure functions; e_j(t) = |wrap_deg(out -
truth)| per angle, grouped by the seven v1 mask groups):
- E_occ mean/max over the occlusion window (G/S).
- E_reacq: mean error over the first K=5 frames after the window.
- Recovery time: frames until e < 5 deg sustained 3 frames; inf = fail.
- Teleport: per-joint step budget delta_j = 1.5 x p99.9 of clean-run
  steps (derived, recorded in the manifest, not hardcoded); hard gate
  teleport_count == 0, report worst step.
- Continuity: p95 |per-frame step| over the FULL run (R-type too).
- Plausibility: joint-limit violation fraction; bone-length deviation.
- Latency: per-stage p50/p95/p99/max at recorded pacing, warmup split
  out; PASS iff total p99 <= 33.3 ms; plus occlusion-conditional p99
  (a strategy that only blows budget while active still fails).
- Honesty: status per joint-group in {MEASURED, ESTIMATED, LOST} every
  frame; confusion matrix vs manifest windows; false-measured < 1%
  (2-frame boundary slop); estimated-coverage reported.
Ranking rule fixed now: hard gates (latency, teleport 0, honesty)
disqualify; survivors ranked by mean rank across metrics x scenarios;
ties broken on the long-wrist scenario.

Deliverables: config drafts, metrics.py + tests, V3_DECISIONS.md
entries (env decision above, metric definitions, ranking rule). STOP.

## Phase 1 -- detector module (needs v3rt env + one-time download)

rtmlib explicit RTMDet + RTMPose classes (not the Body wrapper -- V3
controls scheduling). box_tracker: pose box from previous keypoints
(score >= 0.3) + 25% margin; scheduled re-detect N=15 plus triggers
(mean score < 0.35 for 2 frames, box area jump > 2x, border contact,
no-person). N validated by a {5,15,30} sweep. Overlay writer + latency
harness (runner --mode latency). Acceptance: CUDAExecutionProvider
active, pose p99 measured, sweep table, extractor CSV
({name}_x/_y/_z/_score/_src + meta.json mirroring the v1 format).

## Phase 2 -- math core (no onnxruntime needed; synthetic before real)

Representation decision: UNIT QUATERNIONS internally, v1 angle
definitions at the interface. Rationale: native SLERP/log-map
prediction and filtering without +-180 or gimbal pathology, well-posed
hypothesis blending, two-line swing-twist about the arm axis; all v1
singular branches live only in convert.py, which calls the VERBATIM
vendored trig on matrix_from_quat(q) -- the comparability contract.
Modules: representation.py (qmul/qexp/qlog/slerp/swing_twist/
hemisphere continuity/QuatOneEuro), skeleton.py, solver_q.py,
convert.py. Tests: oracle identity vs vendored v1 solvers to 1e-9 deg
on all G datasets + 10k random poses; injected-truth match; +-180
crossing; gimbal and straight-elbow branch parity.

## Phase 3 -- integration, gate recalibration, BASELINE

Loop: paced bag -> align -> detector -> depth (5x5 median +
rs2_deproject) -> gate -> causal filter (gated samples only) -> y-flip
-> strategy -> outputs. Runner has --mode realtime (paced, latency) and
--mode csv (deterministic replay of the extraction; grading and most
tests run here, no onnxruntime).

Gate recalibration (v1's 0.5 visibility threshold is INVALID: RTMPose
score is localization confidence; occluded joints return as confident
hallucinations): automatic weak labels (depth-front check: joint depth
nearer than torso median - 0.25 m means the sample is the occluder;
no-depth; velocity jump), plus ~15 min of manual labeling
(tools/label_gate.py, ~150 keystrokes across score deciles); fit
per-joint-class thresholds, record ROC in V3_FINDINGS.md, thresholds
live in config only. Gate emits pass/fail + reason codes.

BASELINE (the bar Phase 4 must beat): recalibrated gate -> NaN ->
vendored ChainFallbackSolver hold-last; status: live = MEASURED, held
<= 30 frames = ESTIMATED, longer = LOST. Ported 33-check suite must
pass. S-type scenarios regenerated on the V3 extraction (same design
as v1: wrist short/long, elbow long, hip, root ref, pose loss; windows
auto-proposed in clean spans, human-confirmed; modes nan and low_conf).

## Phase 4 -- strategy bake-off behind one interface

OcclusionStrategy.update(t, kp3d, conf, gate_mask) -> StrategyOutput
(angles13 v1 order, status (7,) in {0,1,2}, diagnostics dict);
registry by name; reset() between runs; every strategy causal and
stateful. Candidates, cheapest first: S2 quaternion prediction with
damped decay (q propagated by tangent velocity, lambda ~ 0.8/frame,
SLERP-capped reacquisition blend -- structurally teleport-proof); S3
chain-constrained partial IK (two-bone IK from visible
shoulder+wrist with calibrated bone lengths; root from shoulder line
when a hip drops -- recovers exactly what hold-last throws away); S5
confidence-weighted blending (slerp(pred, meas, w(score)), hard-zeroed
by depth-front); S1 constraint-projection solve (<= 5 Gauss-Newton
iters on the 13-dim state: match visible landmarks through FK, joint
limits, nearest to prediction -- budget risk, measured day one); S4
multi-hypothesis late commitment (3-5 hypotheses per arm scored
against arriving evidence, commit on reacquire). grade.py runs
manifest x strategies (accuracy in csv mode, latency in realtime
mode) and emits ranked tables; verdicts to V3_DECISIONS.md.

## Phase 5 -- full combined runs

All three local bags + one held-out ENSC498 bag (absolute path,
read-only), baseline + top-2 strategies, combined all-windows mask +
natural occlusions. Report: config hash, git commit, env, model files,
latency tables, all metrics per scenario per joint-group, honesty
matrix, hard-gate verdicts, ranked recommendation with failure cases.
Curated into V3_FINDINGS.md with a "promotion candidate" section that
states what WOULD move to the thesis if the user ever decides; nothing
moves otherwise.

## Testing

pytest markers: ort / net / bag / gpu; the DEFAULT run needs none --
metrics, config guards, representation, oracle identity, singularities,
causal filter, gate logic, baseline scenarios, strategy contracts
(including a causality check), synthetic-gap strategy tests, and
grading all run on numpy + CSVs. Only detector tests and paced-bag
smoke tests need the install.

## Config schema (all tunables in JSON, no hardcoding)

configs/default.json: paths {bag (absolute), models_dir, output_dir,
scenario_manifest}; model {variant, det_onnx, pose_onnx, input sizes,
providers}; detect {det_freq 15, margin 0.25, kpt_min_score 0.3,
reacquire_score 0.35, reacquire_frames 2, box_area_jump 2.0}; depth
{window 5}; gate {score_thresholds per joint class, depth_front_margin
0.25, velocity_max 4.0}; filter {v1 constants}; strategy {name +
per-strategy blocks}; status {lost_after_frames 30}; budget {frame_ms
33.3, recovery_deg 5.0, reacq_k 5, teleport_safety 1.5}; joint_limits;
bones {calibrate_frames 60}. Scenario manifest carries derived teleport
budgets per the no-hardcoding rule. Null config values are deliberate
placeholders (fitted or pinned in their phase); code must fail loudly
on a null, never default silently.

## Risks

CPU fallback misses budget (GPU is plan of record; variant=rtmpose-s/t
is a config-only escape); model CDN unreachable (weights fetchable
anywhere, dropped into v3/models/); confident hallucination (layered:
depth-front gate + velocity + honesty matrix as guardrail; S5
down-weights instead of trusting); wrist redefinition (COCO wrist
crease vs BlazePose wrist joint shifts the twist angle definition --
measure the per-angle offset V3-vs-v1 on the same recording in Phase 3,
report offset-corrected comparisons, never reuse v1's calibrated grip
offset); scenario windows never reuse v1 frame indices; S-type truth
must run the identical stateful pipeline with masking disabled (one
code path, mask=None switch).

## Execution order

Phase 0 (worktree + docs + configs + metrics + tests) -> STOP for user
review -> Phase 1 (env v3rt + installs + detector) and Phase 2 (math
core, independent of the install) -> Phase 3 -> Phase 4 (S2, S3, S5,
S1, S4) -> Phase 5. V3_DECISIONS.md and V3_FINDINGS.md are running
logs from Phase 0 onward. Plain-text professional output everywhere,
per the standing style rule.

# V3 decisions log

Running log. Newest at the bottom. Numbers cited here must come from a
pinned run or the approved plan; none are invented.

FORMAT NOTE (2026-08-06, appended per RULES.md, log is never
rewritten): entries D-001 through D-008 predate the structured format
and use date/decision/why/consequences. From D-009 onward every entry
carries ID / Status (SETTLED | UNCERTAIN | BLOCKED) / Decision / Why /
Alternatives / Evidence / Reversibility / Review, per v3/RULES.md.
Retroactive statuses for the early entries:
  D-001 SETTLED (user-directed), D-002 SETTLED (env survey + install
  verified), D-003 SETTLED (approved plan), D-004 UNCERTAIN (design
  judgment, no measurement -- see its Review note in D-009),
  D-005 SETTLED (approved plan + oracle tests), D-006 SETTLED
  (policy), D-007 SETTLED (user-directed), D-008 SETTLED for the ORT
  1.22.0 pin (measured) but UNCERTAIN for YOLOX-tiny vs yolox-m until
  box stability is measured on the pinned recording. ANNOTATION
  2026-08-06 later: the detector-choice half is resolved by the sweep
  in D-016 (tiny + det_freq 15 kept, clean-scene evidence); the
  occlusion-reacquisition caveat stays open until Phase 4.

---

## D-001 2026-08-06 Track bootstrap and isolation

Decision: V3 lives in git worktree /home/luo/Desktop/v3-realtime on
branch v3-explore, created from master ee7079f. All V3 material under
v3/; no file outside v3/ changes on this branch; the branch is never
merged to master. Reuse from the thesis tree is copy-only.

Why: the user's binding requirement is that V3 cannot affect the v1/v2
thesis context. A worktree on a never-merged branch plus copy-only
reuse makes cross-contamination structurally impossible rather than a
matter of discipline.

Consequences: vendor/v1/ holds verbatim oracle copies (hash-checked by
tests/test_vendor_integrity.py); V3 sessions run rooted at the
worktree; bags are read by absolute path from the main tree's
gitignored Video/ directory.

Timing note: the original plan deferred implementation to after the
mid-September thesis freeze. On 2026-08-06 the user directed the start
immediately ("ignore the timing"), keeping isolation as the hard
requirement. The defense retains absolute priority in the main tree.

## D-002 2026-08-06 Environment: conda env v3rt, GPU ONNX Runtime

Decision: dedicated conda env v3rt (clone of env RealSense).
User-approved installs into v3rt ONLY: onnxruntime-gpu >= 1.19 and
rtmlib --no-deps. RTMPose ONNX weights (RTMDet-nano ~12 MB +
RTMPose-m ~50 MB) are downloaded once and pinned into v3/models/
(gitignored), referenced by local path in configs/default.json.

Why: the environment survey (2026-08-06, thesis session) found
onnxruntime and rtmlib absent from every env and no ONNX weights on
disk; base python 3.11.9 carries torch 2.7.1+cu126 with working CUDA
(RTX 3080) and vendored cuDNN 9.5.1, which onnxruntime-gpu can reuse.
rtmlib without --no-deps would clobber the GPU ORT with the CPU wheel.
GPU inference gives real headroom against the 33.3 ms p99 budget that
CPU-only RTMPose-m would threaten.

Consequences: the base anaconda env and its mediapipe pins are never
touched. The install happens at Phase 1 start, not Phase 0; until then
the default pytest run must need no onnxruntime.

## D-003 2026-08-06 Metrics and ranking rule fixed before building

Annotation 2026-09-25: the budget derivation (clean-run steps) is superseded for the oracle_union manifests by D-033 (oracle steps over the union, twist gated by elbow bend); the gate and ranking rule are unchanged.


Decision: the metric set and the ranking rule are frozen now, before
any detector or strategy code exists, in bench/metrics.py (pure
functions) and configs/bench.json:

- E_occ mean/max over the occlusion window (G/S scenarios).
- E_reacq: mean error over the first K=5 frames after the window.
- Recovery time: frames until error < 5 deg sustained 3 frames;
  inf = fail.
- Teleport: per-angle step budget = 1.5 x p99.9 of clean-run steps
  (derived at manifest build time, recorded in the manifest, never
  hardcoded); hard gate teleport_count == 0.
- Continuity: p95 |per-frame step| over the full run.
- Plausibility: joint-limit violation fraction; bone-length deviation.
- Latency: per-stage p50/p95/p99/max at recorded pacing, warmup split
  out; PASS iff total p99 <= 33.3 ms; plus occlusion-conditional p99.
- Honesty: per-group status in {MEASURED, ESTIMATED, LOST}; confusion
  matrix vs manifest windows with 2-frame boundary slop;
  false-measured < 1 percent; estimated-coverage reported.

Ranking: hard gates (latency p99, teleport 0, honesty false-measured)
disqualify; survivors ranked by mean rank across metrics x scenarios;
ties broken on the wrist_long scenario.

Why: fixing the grading before the contestants exist is the only way
the Phase 4 bake-off cannot be gamed, consciously or not.

Consequences: changing any metric or the ranking rule after Phase 4
starts requires a new decision entry with justification, and re-grading
of everything already graded.

## D-004 2026-08-06 Group error reduction = max over member angles

Decision: per-group error at frame t is the MAX over that group's
member angles' errors (groups = the seven v1 live-mask bits: root,
R_swing, R_twist, R_elbow, L_swing, L_twist, L_elbow, over the
13-angle PSA order defined in vendor/v1/occlusion.py).

Why: a joint group is only as correct as its worst degree of freedom;
averaging would let one badly wrong angle hide behind its siblings.
Conservative reduction also matches how the hard teleport gate treats
any single exceeding angle as a failure.

Consequences: reported group errors are upper bounds on per-angle
errors; per-angle detail stays available from the same functions for
diagnosis.

## D-005 2026-08-06 Representation: unit quaternions internally

Decision (implemented in Phase 2): internal orientation state is unit
quaternions; v1 angle definitions exist only at the interface, in
core/convert.py, which calls the VERBATIM vendored v1 trig on
matrix_from_quat(q). Oracle identity to 1e-9 deg is the acceptance
test.

Why: native SLERP/log-map prediction and filtering without +-180 or
gimbal pathology, well-posed hypothesis blending for S4, two-line
swing-twist about the arm axis; and the comparability contract with v1
stays exact because the final trig is v1's own code.

Consequences: every strategy operates on quaternions; any angle-space
logic outside convert.py is a design error.

## D-006 2026-08-06 Null config values are deliberate placeholders

Decision: configs/default.json ships with nulls where the value is
fitted or pinned in a later phase: gate score thresholds (fitted in
Phase 3 from ROC on labeled data), model onnx paths (pinned in Phase 1
after download), joint limits (reviewed in Phase 2 against the v1
KINEMATIC_MODEL conventions), scenario windows and teleport budgets
(derived in Phase 3 on the V3 extraction). Code encountering a null it
needs must fail loudly, never substitute a silent default.

Why: inventing placeholder numbers now would violate the no-invented-
numbers rule and could silently survive into graded runs.

Consequences: tests/test_configs.py asserts the nulls stay null until
their phase replaces them with sourced values.

## D-007 2026-08-06 Isolation redefined: Unity-level, not git-level

Decision: per the user's clarification, V3 does not need git
separation: v3/ lives on master in the main tree and is pushed
normally (the bootstrap worktree and branch v3-explore are retired;
commit 9f79876 there carries the identical Phase 0 content). The
binding isolation is:

1. No v1/v2 file is ever edited for V3 (copy-only reuse, unchanged).
2. Unity: V3 gets its OWN scene (Unity/Assets/Scenes/V3Scene.unity)
   and OWN scripts (Unity/Assets/Scripts/V3/), reading V3-only shared
   memory names (/dev/shm/v3_*). Existing scenes and scripts are never
   modified; the v1/v2 receivers stay dormant in the V3 scene because
   their shm names are never created by the V3 stack.
3. Dedicated conda env v3rt (unchanged).
4. Nothing enters the thesis text without an explicit user decision
   (unchanged).

Why: the user directed "the meaning of isolate is not isolate the git,
you can push to the git as well; for v3 create separate scene at the
unity, and use separate code in unity". Same-branch cohabitation is
also what lets the V3 Unity scene coexist with the thesis scenes in
the one Unity project the user opens.

Consequences: the Phase 0 stop-for-review was waived by the user
("no need for stop continue the work"); Phases 1 and 2 proceed
immediately. The plan's isolation section is rewritten to match.

## D-008 2026-08-06 Phase 1 environment: ORT 1.22.0 (CUDA 12), YOLOX-tiny detector

Decision: onnxruntime-gpu is pinned to 1.22.0, not the latest 1.28.0.
Person detection uses rtmlib's YOLOX-tiny (HumanArt, 416x416), not the
RTMDet-nano the plan sketched; pose is RTMPose-m body7 256x192 exactly
as planned. Both ONNX zips are pinned in v3/models/ with sha256 in
MODELS.sha256. The CUDA execution provider loads the five CUDA-12
library dirs vendored by base torch (cudnn 9, cublas 12, cudart 12,
cufft, curand), preloaded by absolute path; the CUDA-13 copies under
nvidia/cu13 must never be on the search path.

Why: measured, not assumed. ORT 1.28.0 is built against CUDA 13 and
refused the CUDA EP on this machine (driver 575.57.08 = CUDA 12.9;
CUDA 13 needs >= 580): "Require cuDNN 9.* and CUDA 13.*". ORT 1.22.0
is the CUDA-12 build line and activates CUDAExecutionProvider cleanly.
rtmlib has no RTMDet person model; its body solutions ship YOLOX
variants. YOLOX-tiny over yolox-m: detection runs on 1-in-15 frames,
which lands det latency inside the p95..p99 window of the per-frame
distribution, so the detector must be cheap too; yolox-m stays a
config-only escape if tiny's boxes prove unstable.

Consequences: measured pose forward on the RTX 3080 (200 runs after
warmup): p50 1.58 ms, p95 1.72 ms, p99 2.00 ms -- the 33.3 ms budget
has an order of magnitude of headroom. CPU fallback measured p50
6.05 ms / p99 11.50 ms, so even provider loss keeps the budget
feasible. Version constraint "onnxruntime-gpu >= 1.19" is satisfied.

ANNOTATION 2026-09-25: the pose half of this entry (RTMPose-m body7
256x192 as the default) is superseded by D-028 (M3 pose sweep): the
default variant is now rtmpose-x_yolox-m. The ORT 1.22.0 pin and the
CUDA library setup stand. rtmpose-m stays in configs/model_variants.json
under its original name (tests/test_configs.py PINNED_VARIANTS).

## D-009

ID: D-009
Status: SETTLED
Decision: Adopt v3/RULES.md (user-set 2026-08-06): run continuously
without approval stops, log every decision at the moment it is made in
this structured format, one decision per commit where possible, write
v3/SESSION_REVIEW.md before the session limit.
Why: user instruction; a logged assumption the user can overturn later
beats an idle session.
Alternatives: none considered; this is a direct user directive.
Evidence: the user's message of 2026-08-06 (verbatim rule text in
v3/RULES.md).
Reversibility: user edits or replaces v3/RULES.md.
Review: confirm the rule text in v3/RULES.md matches your intent,
including that its scope is the V3 track.

## D-010

ID: D-010
Status: UNCERTAIN
Decision: Retroactive status D-004 (group error = MAX over member
angles) stays UNCERTAIN; kept as the grading reduction.
Why: it is a design judgment with a coherent rationale (a group is as
wrong as its worst DOF; matches the any-angle teleport gate) but no
measurement demonstrates it ranks strategies better than mean
reduction.
Alternatives: mean over members (hides one bad DOF behind siblings);
reporting both (doubles every table for little decision value since
per-angle detail stays available).
Evidence: none (design argument only).
Reversibility: one-line change in bench/metrics.py group_error plus
re-grading; per-angle errors are unaffected.
Review: after Phase 4's first graded runs, check whether MAX vs mean
would reorder any strategy ranking; if not, this is harmless.

## D-011

ID: D-011
Status: UNCERTAIN
Decision: pip install pytest (dev-only) into env v3rt, beyond the two
explicitly approved packages (onnxruntime-gpu, rtmlib).
Why: the ort/gpu/bag-marked tests can only execute inside v3rt; an
environment that cannot run its own test suite defeats the testing
plan. pytest is a development tool with no runtime footprint in the
pipeline.
Alternatives: running ort tests with base python (impossible: ort is
not installed there, by design); vendoring a test runner (absurd
overhead).
Evidence: none for the approval itself; the approved-installs list
(D-002) named only onnxruntime-gpu and rtmlib.
Reversibility: pip uninstall pytest inside v3rt; nothing else changes.
Review: confirm dev tools in v3rt are acceptable, or say so and it
gets removed.

## D-012

ID: D-012
Status: SETTLED
Decision: The box tracker's border trigger is rising-edge (a NEWLY
touched image edge), not level-triggered; and note_detection resets
the area-jump baseline instead of seeding it with the detector box.
Why: measured on the pinned recording, the subject's head touches the
top image edge in every frame, so level-triggered border contact
degenerated to detect-every-frame (60/60 frames ran detection; box
reuse never engaged). Separately, the pose box is tighter than the
detector's loose box by construction, so comparing their areas refired
area_jump after every detection.
Alternatives: dropping the border trigger entirely (loses the genuine
person-leaving-frame signal); requiring score degradation alongside
border contact (conflates two independent signals; low_score already
exists).
Evidence: per-frame trigger trace on the pinned bag, frames 0-11: all
fired 'border' with the box top at y ~= 2 px; after the fix the bag
smoke test shows detection amortized (see test_bag_smoke_detection_and
_shapes). Rising-edge and baseline-reset behavior pinned by
test_border_contact_triggers_on_rising_edge_only and
test_detector_box_does_not_seed_area_jump.
Reversibility: two small blocks in detector/box_tracker.py; triggers
are independent, removing one does not affect the others.
Review: on live camera night-style footage where the person walks out
of frame, confirm a border re-detect fires on the way out.

## D-013

ID: D-013
Status: SETTLED
Decision: V3's Unity isolation (the user's binding requirement) is
implemented as: scene Unity/Assets/Scenes/V3Scene.unity + script
folder Unity/Assets/Scripts/V3/ (V3PersonReceiver.cs, self-contained,
no inheritance from any existing receiver), reading only
/dev/shm/v3_person in the new PSV3 format (172 B seqlock: 8 landmark
positions + 13 angles + 7 per-group statuses). Unity applies numbers
and never creates them: landmark positions are FK-reconstructed on
the python side; the canonical writer is v3/replay/psv3.py. Color
vocabulary: side colors = MEASURED, amber = ESTIMATED, red = LOST
(amber/red meanings consistent with the v2 scene). The scene file was
built from SampleScene's settings blocks (camera, light, volume; no
receiver objects exist in that scene) plus one V3Person GameObject;
meta GUIDs were pre-generated so nothing needs Unity open to commit.
Why: positions-in-packet keeps all math in python (single source of
truth, matches the v1/v2 receiver philosophy) and makes the Unity
side dumb enough to be provably isolated; per-group statuses carry
the honesty signal the whole track is about.
Alternatives: inheriting ArucoSceneReceiver like the v2 receiver
(couples V3 to v1 Unity code, violating separate-code); sending only
angles and doing FK in C# (duplicates the kinematic conventions in a
second language, a drift risk the oracle tests cannot see).
Evidence: PSV3 round-trip and validation tests (tests/test_psv3.py);
demo writer publishes and the shm file has the exact packet size;
the demo pattern solves finite angles through solver_q + convert at
25 sampled times. NOT yet verified inside the Unity editor (no
editor in this session); first Play run pending, user step.
Reversibility: delete Scripts/V3/, V3Scene.unity, replay/psv3.py,
tools/psv3_demo_writer.py; nothing else references them.
Review: open V3Scene in Unity, run
/home/luo/anaconda3/bin/python v3/tools/psv3_demo_writer.py, press
Play: a swinging-arm figure whose right arm cycles orange -> amber ->
red every 4 s. Existing scenes must behave exactly as before.

## D-014

ID: D-014
Status: UNCERTAIN
Decision: README structure per the user's README rules: root
README.md (7 sections, under two pages); V1.md at the repository root
serves as v1's per-version README because v1 has no single folder;
v2/README.md added alongside the existing V2.md phase doc (README =
five-minute view, V2.md = full phase detail); v3/README.md links the
plan, decisions, and findings.
Why: the rules require a README per version folder; v1 IS the root
tree, so its README needs a root-level home that the versions table
can link. Splitting v2's README from V2.md keeps the five-minute view
short without deleting the working phase document.
Alternatives: renaming V2.md to README.md (loses the distinction
between overview and working doc); creating a v1/ folder (would move
frozen v1 files, forbidden).
Evidence: none for the placement choices themselves; the section
structure follows the user's rule text in AGENTS.md verbatim.
Reversibility: files can be renamed or merged freely; only links in
README.md would need updating.
Review: confirm V1.md at root is acceptable as v1's README home, and
that keeping V2.md separate from v2/README.md is wanted rather than
merged.

## D-015

ID: D-015
Status: SETTLED
Decision: The config filter block carries v1's CAUSAL live tuning, not
the offline values: min_cutoff 1.0 Hz (beta 1.0, d_cutoff 1.0) plus
the trailing-Hampel despike constants window 11 / k 3.0 / abs floor
0.035 m / max rejects 3.
Why: V3's loop is causal; v1 measured that the offline 0.05 Hz
min_cutoff costs about 9 frames of lag in the causal setting and
re-tuned to 1.0 Hz, and widened the despike floor from 20 mm to 35 mm
because a trailing window has MAD ~ 0 at motion onset. Copying the
offline constants (as the config drafted in Phase 0 did) would have
rebuilt v1's known mistake.
Alternatives: keeping 0.05 Hz (known 9-frame lag); re-tuning from
scratch on V3 data (possible later; starting from v1's measured
values keeps V1-vs-V3 comparability and is the documented baseline).
Evidence: realtime/person/realtime_person.py docstring and
CausalLandmarkFilter defaults (v1 measurements recorded there);
replay/causal_filter.py copies the class; tests/test_replay_units.py
pins the behavior; tests/test_configs.py pins the constants.
Reversibility: config values only; the filter reads everything from
the config block.
Review: none needed beyond confirming the constants match
realtime_person.py.

## D-016

ID: D-016
Status: SETTLED
Decision: Keep YOLOX-tiny and det_freq 15 as the defaults. This
closes D-008's UNCERTAIN detector-choice half FOR CLEAN-SCENE
OPERATION; reacquisition behavior under occlusion remains open until
the S-type runs (Phase 4) and is noted in D-008 as the remaining
caveat.
Why: the sweep (det_freq {5,15,30} x variant {tiny,m}, full pinned
bag, non-paced, warmup 60 excluded, GPU) shows identical coverage
(898/898 every combo) and identical pose quality (median eight-
landmark score 0.753-0.758 everywhere), while tiny's stage p99 is
8.5 ms vs m's 17.5 ms -- m spends half the 33.3 ms budget on det
frames for zero measurable quality gain here. m's detector boxes do
agree better with the pose-derived crop (box-center step p95 8-20 px
vs 40-54 px for tiny), but the disagreement does not propagate into
scores, confirming RTMPose's crop robustness with the 25 percent
margin. det_freq makes no difference on this clean recording except
detection cost (5.1 to 21.7 percent of frames); 15 stays as the
middle value pending occlusion data.
Alternatives: yolox-m default (rejected: 2x stage p99 for nothing
measurable on this data); det_freq 30 (kept available; rejected as
default because slower reacquisition after occlusion is the expected
failure mode, untested yet).
Evidence: v3/dataset/phase3_detector_sweep.txt (table), produced by
bench/sweep_detector.py at commit HEAD.
Reversibility: config-only (model.det_onnx + det_input_size_wh,
detect.det_freq); yolox-m is downloaded and pinned in v3/models/.
Review: after Phase 4 S-type runs, check reacquisition error and
recovery time per det_freq and variant; if tiny reacquires worse,
this entry gets superseded.

ANNOTATION 2026-09-25: the detector half (YOLOX-tiny as the default)
is superseded by D-028 for the pinned variant, which pairs RTMPose-x
with YOLOX-m 640x640. det_freq 15 stands. The tiny-vs-m finding of
this entry still holds for RTMPose-m.

## D-017

ID: D-017
Status: SETTLED (the finding); UNCERTAIN (the path forward)
Decision: The plan's depth-front weak label (joint depth nearer than
torso median minus 0.25 m implies the sample lies on the occluder) is
REJECTED as an occlusion signal for wrists on this task; no
provisional score thresholds are proposed, and the config gate
thresholds stay null.
Why: measured on the pinned-bag extraction, the rule flags the right
wrist on 889 of 898 frames and the left on 363 -- the subject reaches
forward for the entire task, so wrists are legitimately far in front
of the torso; and the flagged samples score HIGHER (median 0.818)
than the unflagged ones (0.789), so the labels anti-correlate with
any plausible occlusion truth. The Youden fit degenerates (tpr 0.00,
fpr 0.00). Shoulders, elbows, and hips get zero hits, which is
geometrically sensible; the velocity rule fires zero times.
Alternatives (for Phase 3 continuation, all unmeasured, hence
UNCERTAIN): depth-front relative to the joint's own predicted depth
(kinematic prediction or last accepted sample) instead of the torso;
restricting depth-front to non-wrist joints; leaning on the manual
labeling pass (tools/label_gate.py, user step) as the primary label
source with automatic labels as a cross-check only.
Evidence: v3/dataset/phase3_gate_weak_labels.txt, produced by
bench/gate_weak_labels.py on the pinned extraction.
Reversibility: analysis-only; nothing was applied to the config.
Review: decide whether the manual labeling session happens on this
recording or on a new recording with deliberate occlusions (the
pinned bag may simply contain too few true occlusion frames to fit
wrist thresholds at all).

## D-018

ID: D-018
Status: SETTLED
Decision: The V3-vs-v1 per-angle offset table is measured and pinned
(dataset/phase3_v1_offset_table.txt): both raw extractions solved
through the identical vendored ChainFallbackSolver, no smoothing.
Headline offsets: root_y -7.61 deg, r_swing_y +9.03, l_swing_y -9.45;
twist spread (cstd) ~6.3-6.6 deg -- the predicted wrist-redefinition
effect; elbow_z exactly 0.00/0.00 on BOTH sides, an independent
confirmation that v1's ez == 0 construction carries over to the V3
solve. Any quoted V3-vs-v1 angle comparison must subtract these
offsets and state the spread.
Why: the plan's standing risk: the COCO wrist (crease) is not the
BlazePose wrist (joint), and shoulder/hip placements differ too;
assuming comparability would fabricate agreement or disagreement.
Alternatives: reusing v1's calibrated grip offset (forbidden by the
plan); comparing filtered outputs (would entangle filter tuning with
the definitional offset).
Evidence: bench/v1_offset_table.py on 898 common frames of the pinned
recording.
Reversibility: analysis-only.
Review: the r_swing_y cstd of 9.62 deg means the two detectors
disagree beyond a constant shift for that angle; decide whether
swing_y comparisons are quotable at all.

ANNOTATION 2026-09-25: these offsets hold for rtmpose-m only and are
kept for it (dataset/phase3_v1_offset_table.txt). The pinned variant
rtmpose-x_yolox-m has its own table, dataset/phase5_v1_offset_table.txt
(D-028); bench/grade_clean.py V1_OFFSET_TABLES maps variant -> table.

## D-019

ID: D-019
Status: UNCERTAIN
Decision: S-type scenario windows auto-proposed at fixed run
fractions (0.30/0.45/0.60/0.70/0.79/0.88 of 898 frames -> wrist_short
269-271, wrist_long 404-448, elbow_long 539-583, hip 629-658,
pose_loss 709-718, root_ref 790-819), disjoint, past warmup; v1
durations and landmark choices kept, v1 frame indices not reused.
Why: the plan calls for auto-proposed windows in clean spans with
human confirmation; the entire V3 extraction is landmark-complete so
every span is clean, and the autonomy rule says proceed and log
rather than stop. The fractions spread windows across task phases.
Alternatives: reusing v1's window indices (forbidden); choosing
windows at high-motion moments (more stressful, but would need a
motion criterion that itself would be a fresh unvalidated choice).
Evidence: none for the specific placements (that is the uncertainty);
the masked CSVs and manifest derive deterministically from them.
Reversibility: rerun bench/make_scenarios.py with different anchors;
grading derives truth at grade time, nothing else caches.
Review: confirm the windows cover task moments you consider
representative (especially whether any window should sit on a
high-motion reach).

## D-020

Annotation 2026-09-25: budgets re-derived by D-033; see D-033 for the re-grade.


ID: D-020
Status: SETTLED
Decision: Three implementation rulings from the baseline build:
(1) the v3 strategy package is strategies/, not the plan's
occlusion/, because a package named occlusion shadows the vendored
occlusion.py module in imports; (2) derived teleport budgets carry a
1e-9 deg floor because identically-zero angles (elbow ez) have clean
p99.9 exactly 0 and float64 noise (measured 2.8e-14 deg) would count
as teleports; (3) grading excludes the 60 warmup frames from teleport
and continuity, matching the budget derivation and v1's warm-up
exclusions (the rest-pose snap is a start-of-stream artifact).
Why: (1) import collision produced ImportError order-dependently;
(2)(3) first grade run showed ~45 identical "teleports" in every
scenario, all traced to noise on ez and warmup snaps, drowning the
real signal.
Alternatives: importlib-by-path aliasing for (1) (fragile);
excluding ez from the gate for (2) (hides a real failure mode a
strategy could introduce).
Evidence: dataset/phase3_baseline_grade.txt (final table);
test_teleport_budget_floor_for_identically_zero_angles;
tests/test_baseline_scenarios.py.
Reversibility: (1) rename back if the vendored module is aliased;
(2)(3) parameters in metrics.py/grade.py.
Review: the baseline verdict: honest everywhere (false_measured 0),
wrist gaps repaired or absorbed, but HARD GATE FAIL on teleport for
elbow_long (1) and root_ref (2) -- the reacquisition snap. This is
the measured bar Phase 4 strategies must clear.

## D-021

Annotation 2026-09-25: the cap values now follow D-032 (0.8 x the smallest budget per side and track) on the D-033 budgets; the fixed step_caps_deg table is the legacy source.


ID: D-021
Status: SETTLED (design); UNCERTAIN (two constants)
Decision: S2 implementation: independent quaternion tracks per STATUS
GROUP (root, swing, twist, elbow per arm), velocity from the log map
with EMA alpha 0.5, damped decay lambda 0.8/frame while unobservable,
and UNCONDITIONAL per-track geodesic step caps (config step_caps_deg,
~0.8 x the smallest driven teleport budget) applied to every output
step -- reacquisition, prediction, and measurement discontinuities
alike (a capped frame reports ESTIMATED). Swing tracks live on v1's
OWN factorization manifold Ry(ty)Rz(tz) (projector re-derives ty,tz
from the arm axis); the measurement split uses convert.shoulder_angles
so the extracted twist depends on the twist track alone.
Why: three grade-measured failures forced each element: (1) a
composite shoulder track snapped the twist on wrist return (1
teleport, wrist_long); (2) the geometric swing-twist decomposition
about x is NOT the v1 factorization (Ry*Rz has an x quat component),
so capped tracks still leaked 2.83 deg into r_twist vs its 2.49
budget; (3) the v1 root reference switch (occluded right shoulder ->
left shoulder) steps the MEASURED root by 2.29 deg, identically under
hold-last, so only output-side continuity can pass the gate.
Alternatives: uncapped snap-to-measured (the baseline's documented
failure); per-angle caps in angle space (reintroduces the +-180 and
gimbal pathologies quaternions were chosen to avoid).
Evidence: dataset/phase4_s2_vs_baseline.txt and the intermediate
grade tables in the session log; UNCERTAIN constants: velocity EMA
alpha 0.5 and the 0.8 budget fraction in the caps (both unmeasured
sweeps).
Reversibility: all constants in config s2_quat_prediction; the
projector is one function.
Review: whether ESTIMATED-during-cap is acceptable honesty semantics
for measurement-side discontinuities (2-3 frames after a root
reference switch).

## D-022

ID: D-022
Status: SETTLED
Decision: The whole-design verification the user asked for is done
and PASSES on the pinned recording: (a) same video + new tool, end to
end at recorded pacing: 883/883 frames found, 28.7 fps sustained,
total per-frame latency p50 3.95 / p99 10.65 ms vs the 33.3 ms budget
(detector 9.74 p99 dominates; depth 0.14, filter 0.35, strategy 0.54,
publish 0.02), PSV3 published for the isolated V3Scene; (b) advanced
math improves robustness: S2 passes the teleport hard gate on all six
scenarios while the baseline fails two, halves the worst output step
(1.90 vs 3.81 deg), cuts reacquisition error 38 percent on elbow_long
and short-gap error 38 percent, honesty perfect on both. Per the
frozen D-003 ranking rule the baseline is disqualified and S2
survives.
Why: the user's direction: verify the design works before adding
complexity. Tradeoffs stay visible: S2's bounded prediction drift
makes e_occ worse than hold on near-static holds (root_ref 2.73 vs
1.11, pose_loss 2.35 vs 1.96) while winning on moving joints.
Alternatives: none -- this is the measurement record.
Evidence: dataset/phase4_realtime_e2e.txt,
dataset/phase4_s2_vs_baseline.txt.
Reversibility: not applicable (recorded results).
Review: the next complexity step per the user's plan: a recording
with real, deliberate occlusions (also unblocks D-017 gate fitting).

## D-023

ID: D-023
Status: UNCERTAIN (the rtmpose path is SETTLED by the v3rt suite;
the rtmw and rtmo paths are UNEXERCISED on real models)
Decision: Detector construction goes through
detector/factory.py build_detector(cfg, repo_root, img_wh, device,
key_indices), keyed on a new config field model.backend in {rtmpose,
rtmw, rtmo}; model combinations are named in
configs/model_variants.json with every end2end.onnx pinned by sha256
and size, repeated in configs/models.sha256 and checked by
tests/test_models_sha256.py.
Why: the V3 plan (2026-09-25, milestone M1) sweeps stronger pose
models in M3; a named, hash-pinned table lets the extractor and the
sweep select a model by name and record exactly which files ran,
instead of editing default.json or the local VARIANTS dict that
bench/sweep_detector.py carried. The detector call contract
(frame_bgr -> kp17 (17, 2) px COCO order, scores17 (17,), diag
{det_ran, det_reasons, box, frame}) is unchanged, so every caller,
BoxTracker and core/skeleton.py COCO_IDX stay as they were.
Design: RTMPoseDetector keeps the BoxTracker scheduling and delegates
to a pose backend object (__call__(img, box) -> (kp17, sc17),
needs_box, n_kpts). rtmpose = rtmlib RTMPose on a 17-keypoint model;
rtmw = rtmlib RTMPose on a 133-keypoint COCO-WholeBody model, sliced
to the first 17 (the COCO body block, same order); rtmo = rtmlib RTMO
(verified in the installed rtmlib 0.0.16: RTMO(onnx_model,
model_input_size (h, w)-indexed, nms_thr 0.45, score_thr 0.7)(image)
-> keypoints (N, 17, 2), scores (N, 17), one all-zero person when
nothing passes) on the whole frame, keeping the person with the
largest confident-keypoint extent; its diag box is the tracker's own
box_from_keypoints of this frame (detect.kpt_min_score 0.3,
detect.margin 0.25, both existing config values), det_ran is True on
every frame with reason bottom_up, and no YOLOX is loaded. A backend
whose model emits a keypoint count other than its n_kpts raises.
Constants: n_kpts 17 (COCO body) and 133 (COCO-WholeBody) are the
dataset definitions; the rtmo input size is read from the variant
table, none is defaulted in code; RTMO's nms_thr 0.45 and score_thr
0.7 are rtmlib 0.0.16 defaults, left unchanged and UNCERTAIN until an
RTMO model is swept. yolox-m 640x640 in the table comes from the
local VARIANTS dict of bench/sweep_detector.py (commit f28ee84, the
D-016 sweep); rtmpose-m 192x256 and yolox-tiny 416x416 from D-008.
The bottom-up diag box is built from the current frame's keypoints,
whereas the top-down diag box is the crop used this frame (previous
frame's keypoints or a detection), so box_step_p95 is not strictly
comparable across the two families.
Alternatives: a subclass per backend of RTMPoseDetector (rejected:
duplicates the scheduling that every backend shares); a
backend-specific keypoint mapping in core/skeleton.py (rejected: all
three backends return COCO-17 order, so COCO_IDX stays the only
index mapping); keeping --variants tiny,m in the sweep (rejected: it
required the local dict; the new default --pose-variants
rtmpose-m,rtmpose-m_yolox-m runs the same two combinations).
Evidence: behaviour preserved on the rtmpose path: re-extracting
the pinned 2026-02-24 bag through build_detector (variant rtmpose-m,
v3rt, CUDA) gives a CSV byte-identical (cmp) to
v3/output/extraction_recording_20260224_083945.csv written at commit
54bde7e; sweep_detector.py --det-freqs 15 with the default
--pose-variants reproduces the D-016 row values (898/898 found,
score 0.757 both, stage p99 8.41 ms tiny vs 16.30 ms yolox-m); v3rt
full suite with the ort, gpu and bag tests (the detector fixture now
builds through build_detector) and the default suite pass (M1 report
2026-09-25). Stub-model tests in
tests/test_detector_ort.py cover the rtmw slice, the keypoint-count
check, RTMO largest-person selection, the synthesised box and the
empty-frame case. No RTMW or RTMO model is on disk, so neither path
has run on a real model or a real frame: UNEXERCISED.
Reversibility: callers go back to RTMPoseDetector(cfg, ...) directly
(the class still loads rtmpose from the config when no backend is
injected); delete configs/model_variants.json and the three onnx
lines of models.sha256.
Review: when M3 downloads an RTMW or RTMO model, check that its
first 17 keypoints match the rtmpose-m keypoints on the same frames
(slice order) and that the RTMO score_thr 0.7 does not drop the
person on low-contrast frames.

## D-025

ID: D-025
Status: UNCERTAIN
Decision: The V3 clean-window set is the four source windows of the
unified defence films, recorded in configs/clean_windows.json:
right_elbow 180-540 (page 16), 180042 3-109 (page 14), right_arm_test
505-725 (page 15), arms_outstretched 780-885 (page 13); 0-based
colour-frame indices, stop inclusive, bags under
/home/luo/Desktop/ENSC498/recordings pinned by sha256; baseline
extractions with rtmpose-m in v3/output/clean/. (D-024 is left to the
M2 oracle entry named in the plan.)
Why: chosen for availability: these are the only windows in the
repository already reviewed as clean (every v1 landmark raw-accepted
except two right-wrist frames on page 14) and already carrying v1
angle series (eval/pipeline_smoothness), so the M2 smoothness and
v1-agreement scores need no new review. They were selected for the
defence films, not for coverage: one subject, one session setup, no
occlusion, four motions (elbow bend, straight-arm raise, bent-arm
twist, static T-pose).
Frame alignment: the V3 BagSource yields 898 frames (1049 for 180042)
where the defence MediaPipe extractions have 899 (1050); the last
V3 time_s is one frame period shorter (29.9219 vs 29.9552 s), so the
dropped frame is the last one and window indices agree. Checked by
frame-offset scan -2..+2 of right wrist and elbow xyz velocities
against bank_processing/p13, p17, p18, p19 landmarks_raw.csv: offset
0 is the peak on all four (velocity correlation 0.41 / 0.60 / 0.63 /
0.65 at 0, at most 0.25 elsewhere).
Alternatives: windows picked on the pinned 2026-02-24 bag (rejected:
no reviewed clean span with v1 series exists there); whole
recordings (rejected: include entry and exit motion and tracking
losses the reviewed windows exclude); waiting for the author's
known-angle protocol recording (deferred in the plan; it will be
added as a fifth window, not a replacement).
Evidence: presentation/defense_2026/DECISIONS.md D-088 (windows) and
D-089 (page 14 wrist exception); eval/recordings_archive/index.json
sha256 values, re-hashed on 2026-09-25 with sha256sum (all four
match). Baseline extraction 2026-09-25, rtmpose-m, v3rt, CUDA: person
found on every frame of all four bags; inside the windows all eight
landmarks have depth src 0 on every frame (361/361, 107/107,
221/221, 106/106); whole-bag no-depth samples: 35 on 180042 (outside
its window), 0 on the other three. Source: the .meta.json files next
to the CSVs (v3/output is gitignored, so these are not pinned yet).
Reversibility: edit configs/clean_windows.json; M2 graders read the
set from that file only.
Review: whether four clean, occlusion-free windows of one subject are
enough to rank smoothers, and whether page 14 (short, near T-pose,
107 frames) should count equally with the others.

## D-024

ID: D-024
Status: UNCERTAIN (the reimplementation is SETTLED by test; the
choice of the film settings as the oracle is a judgment)
Decision: The clean-window accuracy reference ("oracle") is the
defence films' offline filter reimplemented in bench/oracle.py and
run on the V3 extraction of the WHOLE recording: centered Hampel
(window 7, k 3, floor 0.02 m, min_periods 3, MAD scale 1.4826) per
landmark, spikes to NaN, linear interpolation over time_s of interior
NaN runs up to 5 frames (edge_fill 0), Butterworth order 4 at 3 Hz
applied with scipy filtfilt per axis on each contiguous finite
segment (segments not longer than scipy's default padlen stay
unfiltered), fs = 1 / median(diff(time_s)); then the Unity flip
[1, -1, 1], core.solver_q.solve_frame_q and core.convert.angles13,
stateless per frame (NaN angles where a group is unsolvable). The
constants live in the new configs/default.json "oracle" block. A raw
reference (the same stateless solve of the unfiltered landmarks) is
exposed as oracle.raw_angles.
Why: the plan (2026-09-25, author decision 2) names an offline
zero-phase oracle on clean frames as the accuracy reference. Using
the film's exact settings keeps the V3 numbers comparable with the
2026-09-24 smoothness study (eval/pipeline_smoothness), whose film
series are this filter on MediaPipe landmarks, and with what the
author saw in the defence films. Reimplemented, not imported, because
V3 reuse is copy-only (D-007) and the v1 script is a CLI.
Constants and sources: hampel window 7, k 3, floor 0.02 m, max_gap 5,
edge_fill 0, butter order 4, cutoff 3 Hz: the command line in
presentation/defense_2026/anim/bank_axes_kinematics.py lines 217-220;
min_periods 3 and MAD scale 1.4826 are hardcoded in
v1/mediapipe/filter_landmarks.py hampel_mask; fs from the median time
step and the padlen rule are that script's smooth_segment and main.
None of these was tuned for RTMPose keypoints: UNCERTAIN whether 3 Hz
is the right bandwidth for V3 (the right_elbow and 180042 motions
reach 4.95 deg/frame in the oracle's r_swing_y on 180042).
Alternatives: a lower cutoff or a Savitzky-Golay oracle (rejected
for now: breaks comparability with the film series and the pinned
smoothness table); the v1 film angles themselves as the reference
(rejected: different detector, carries the D-018 definitional
offsets); importing the v1 script (rejected: D-007).
Evidence: tests/test_oracle.py. On the film's own raw MediaPipe
landmarks (bank_processing/p19 = page 16 and p17 = page 14) the
reimplementation reproduces landmarks_filtered.csv to 4.9999e-7 m
(the %.6f rounding of that file) with identical provenance flags on
every frame of both recordings; a one-time measurement on
2026-09-25 (not a test: a test loading live v1 code would cross
D-007) found the reimplementation agrees with the v1 filter functions
on the p19 input to under 1e-9 m at full precision; its angles reproduce the film's derived right-arm and root
angles (unified_four/p16 and p14 derived_kinematics.csv) to 0.0041
deg max in the film windows, and solving the film's filtered file
directly reproduces them to 5e-10 deg. Synthetic tests: constant
input is returned unchanged (1e-12 m), a 3 Hz sinusoid is attenuated
to 0.50 (filtfilt squares |H| = 1/sqrt(2)), 0.5 Hz passes above 0.99,
8 Hz below 0.01, best lag of a 1 Hz sinusoid is 0 and the centroid of
an asymmetric bump moves by under 1e-3 frames. grade_clean.py output
is identical under base scipy 1.13.1 and v3rt scipy 1.14.1.
Reversibility: edit the oracle block (and the pinned values in
tests/test_oracle.py test_oracle_block_matches_film_settings), re-run
bench/grade_clean.py; nothing live depends on the oracle.
Review: the oracle is not external truth. It is the same RTMPose
keypoints smoothed with look-ahead, so it shares every detector and
depth error of the causal path (for example the right upper-arm
length varies by 31 percent p95 around its window median on
right_elbow even after the oracle filter,
dataset/phase5_clean_baseline.txt). "RMS vs oracle" measures how far
the causal path is from the best zero-lag smoothing of the same
measurement, not accuracy. Check whether 3 Hz suits these motions.

## D-026

ID: D-026
Status: UNCERTAIN
Decision: D-003 is extended, not changed: clean-window metrics from
bench/grade_clean.py (second_diff_rms, rms_vs_oracle_lag0, best_lag
as |lag|; configs/bench.json ranking.clean_metrics) RANK strategies
and smoothers; they never disqualify. The three hard gates
(latency_p99, teleport_zero, honesty_false_measured) and grade.py's
verdict logic are unchanged. Per D-003's consequence clause,
everything already graded (baseline_hold, S2 on the six S-type
scenarios) is re-graded in M3 together with the new clean metrics.
Per window x strategy grade_clean.py also reports, as information:
RMS at the best lag, second-difference RMS of the oracle and of the
raw solve, teleport frames against the S-type manifest budgets,
joint-limit fraction (n/a while every limit is null), non-MEASURED
frames per group, causal-filter reject frames, bone-length p95
deviation (filtered landmarks the strategy received, against the
oracle's median bone length in the window), and for right_elbow and
180042 the right-arm agreement with the v1 series of
eval/pipeline_smoothness after subtracting the D-018 offsets, at the
best lag (circular mean and circular std of the residual).
Why: the plan's goal is smooth and accurate; D-003's frozen set has
continuity p95 but no jitter, lag or reference-agreement score, so
the smoothers of M4 and M5 could not be compared. Ranking-only keeps
the occlusion bar (D-020, D-022) exactly where it was.
Constants and sources: max lag 10 frames (bench.json
ranking.clean_max_lag_frames) = MAX_LAG of
eval/pipeline_smoothness/compare_film_vs_live.py (its PS-004: covers
the 3-frame live lag and the 9-frame earlier tuning); best-lag tie
tolerance 1e-9 deg = the teleport_budget noise floor (metrics.py), so
the identically-zero elbow_z reports lag 0; second_diff_rms and the
mean_abs best-lag criterion are ports of that script, and
tests/test_metrics.py reproduces its pinned metrics.csv (page 16,
el_y / sh_y / sh_z / sh_twist, film / raw_gated / live_cpu) to 6e-5.
The V3 score uses the RMS criterion instead of mean_abs (UNCERTAIN,
chosen so lag and rms_vs_oracle use one norm). Bone reference = the
oracle's window median (UNCERTAIN: bones.calibrate_frames 60 is not
used because the clean windows do not start at a calibration pose).
Alternatives: new hard gates for smoothness or lag (rejected: no
agreed threshold and it would change D-003's disqualification rule
mid-bake-off); ranking on right-arm angles only (rejected: the
mean rank uses all 13 angles so a smoother cannot trade left-arm
quality for right-arm scores; the right-arm summary is printed
separately).
Evidence: dataset/phase5_clean_baseline.txt (grade_clean.py
--strategies baseline_hold,s2_quat_prediction --smoothers none,
rtmpose-m, four windows). Headline, right_elbow r_elbow_y: second-
diff RMS 0.602 (baseline_hold) / 0.513 (S2) vs oracle 0.175 and raw
4.921 deg/frame^2; best lag 3 / 5 frames. On 180042 S2's best lag
reaches the 10-frame bound on r_swing_y and on the left arm because
S2 starts from the rest pose and approaches the first measurements
along the geodesic at its step caps (swing 1.0 deg/frame; l_swing_z
error vs oracle 67 deg at frame 3, still 16 deg at frame 70, measured
2026-09-25), and because fast motion exceeds the caps (oracle
r_swing_y steps up to 4.95 deg/frame there). baseline_hold ranks
ahead on the clean mean rank (1.385 vs 1.615), S2 has the lower
jitter. Teleport counts on clean windows are informational: the
budgets were derived on the slower 2026-02-24 recording.
Reversibility: delete ranking.clean_metrics and
ranking.clean_max_lag_frames from bench.json and bench/grade_clean.py;
grade.py never read them.
Review: (1) whether RMS against the oracle plus lag is the accuracy
score the author wants until the known-angle recording exists;
(2) the v1 agreement shows that the D-018 offsets, measured on the
2026-02-24 recording, do not transfer: after subtracting +9.03 deg
the right_elbow r_swing_y residual is -13.2 deg (oracle vs v1 film,
cstd 2.8) and on 180042 -11.9 deg, so the recording-specific V3-vs-v1
swing_y offset is about -4 / -3 deg there; quote v1 agreement as
residual spread (cstd), not as a mean; (3) whether the 180042 window,
which starts at bag frame 3, should be graded from a warmed-up state
(it currently includes start-of-stream convergence for every
strategy).

## D-028

Annotation 2026-09-25 (M4 recap, review item 2): re-run on the D-033 manifests with D-032 caps and D-031 warm start, every variant passes the S2 hard gates with smoother none and quat_one_euro, and the unchanged selection rule picks rtmpose-l (d2_raw ratio 0.909, mean bone 0.0606, total p99 12.44 ms) over rtmpose-x_yolox-m for both smoothers (dataset/phase5_pose_sweep_recapped.txt, section [F]). The pinned variant is NOT changed here; the re-pin is a master decision.

Annotation 2026-09-25: REVERSED by D-034 (author decision) under this entry's Reversibility clause. The default variant is now rtmpose-l with its own D-033 manifest; the rtmpose-x_yolox-m manifests, pins and offset table stay as history.

ID: D-028
Status: UNCERTAIN
Decision: Pin model variant rtmpose-x_yolox-m (RTMPose-x body7
384x288 + YOLOX-m humanart 640x640, det_freq 15) as the V3 default,
chosen by a selection rule stated before the sweep numbers were read
(M3 of the approved plan). It supersedes the pose half of D-008 and
the detector half of D-016; the D-018 offsets stay for rtmpose-m and
the new variant gets its own table.
Selection rule (written into bench/sweep_pose.py before its first
table run): (1) disqualify a variant whose s2_quat_prediction fails
any D-003 hard gate (latency_p99, teleport_zero,
honesty_false_measured) on the six S-type scenarios, graded on that
variant's own pinned-bag extraction and its own make_scenarios
manifest; (2) a candidate beats rtmpose-m only if its raw-angle
second-difference RMS ratio (geometric mean over the four clean
windows x 11 non-degenerate angles of variant / rtmpose-m, 44 pairs)
is below 1 AND its mean oracle-side bone-length p95 deviation (four
bones x four windows) is not above rtmpose-m's; (3) among those, the
lowest d2_raw ratio wins; (4) if none beats rtmpose-m, keep rtmpose-m.
Numbers (dataset/phase5_pose_sweep.txt; d2_raw ratio, mean bone p95,
s2 teleport-gate scenario failures, realtime total p99 ms paced on
the pinned bag):
  rtmpose-m          1.000  0.0799  0/6   9.68  reference
  rtmpose-x          0.951  0.0632  1/6  15.14  disqualified (gate)
  rtmpose-x_yolox-m  0.937  0.0640  0/6  24.08  beats reference -> WINNER
  rtmpose-l          0.909  0.0606  2/6  12.44  disqualified (gate)
  rtmpose-l_yolox-m  0.936  0.0592  2/6  21.41  disqualified (gate)
  rtmw-dw-l-m        1.111  0.0976  0/6  11.81  does not beat reference
Honesty: 0 failures for every variant and both strategies. All
latency_p99 PASS (budget 33.3 ms). The winner's right upper-arm
oracle bone p95 (the M2 31 percent right_elbow signal) is 0.113 mean
over windows vs 0.140 for rtmpose-m; pinned-bag mean eight-landmark
score 0.885 vs 0.751; S2 causal d2 ratio 0.948; but its mean RMS vs
its own oracle is not better (s2 6.556 vs 6.470 deg, baseline_hold
3.873 vs 3.640 deg), and its latency p99 rises from 9.68 to 24.08 ms
(detect stage 23.16 ms, YOLOX-m runs on scheduled frames).
Why: the clean-window keypoint and smoothness signals are the brief's
criterion; rtmpose-x_yolox-m is the only candidate that improves both
the raw-angle jitter and the bone-length consistency while passing
every hard gate. The yolox-m pairing was swept because the crop is
box-sensitive in the 2D step (clean-window mean step p95 3.23 px with
YOLOX-m vs 4.07 px with YOLOX-tiny for RTMPose-x) and in the gates
(1/6 vs 0/6), although found count and score did not drop with tiny
(the brief's trigger); rtmpose-l_yolox-m was added after the first
table for parity with the x pairing, under the same rule.
Alternatives: rtmpose-l_yolox-m and rtmpose-l have the lowest bone
deviation, a d2_raw ratio equal or lower (0.936, 0.909) and lower
latency, but fail the teleport gate with S2 on 2/6 scenarios;
rtmpose-x fails 1/6; rtmw-dw-l-m is rougher than rtmpose-m on both
clean aggregates; keeping rtmpose-m was the fallback of rule (4).
Evidence: dataset/phase5_pose_sweep.txt (bench/sweep_pose.py run +
table), dataset/phase5_s_grade__rtmpose-x_yolox-m.txt (bench/grade.py,
all three gates), dataset/phase5_realtime__rtmpose-x_yolox-m.txt
(replay/realtime.py), dataset/phase5_clean__rtmpose-x_yolox-m.txt
(bench/grade_clean.py), dataset/phase5_v1_offset_table.txt
(bench/v1_offset_table.py on the winner's extraction). One recording
for the gates and four clean windows for the ranking.
Known confound (why UNCERTAIN): the S2 per-track step caps (D-021)
were set at about 0.8 x the smallest rtmpose-m manifest budget. Each
variant derives its own, smaller budgets (smoother keypoints give
smaller clean steps; e.g. r_elbow_y 1.392 deg for rtmpose-m, 1.004 for
rtmpose-x, 1.032 for rtmpose-l, 1.192 for the winner), while S2's
worst step is 1.90 deg on every variant. The gate failures of
rtmpose-x and rtmpose-l are therefore plausibly a cap-vs-budget
mismatch rather than worse keypoints; which angle tripped was not
isolated. Under the winner's manifest D-021's derivation rule no
longer holds for the swing cap (1.0 deg vs r_swing_z budget 0.779),
although every gate still passes. baseline_hold's teleport failures
rise from 2/6 to 4/6 scenarios for the same reason (tighter budgets);
baseline_hold is the reference behaviour and is not gated.
Constants: none new. Input sizes 288x384 (x, l) and 192x256 (rtmw)
from each zip's pipeline.json; YOLOX-m 640x640 from D-016; det_freq
15 from D-008/D-016; the 44-pair geometric mean excludes r_elbow_z and
l_elbow_z because they are identically zero (ratio undefined).
Reversibility: config-only: default.json model block and
paths.scenario_manifest back to rtmpose-m and
configs/scenarios_20260224.json; tests/test_configs.py DEFAULT_VARIANT.
The old manifest, masked CSVs and extraction are untouched.
Review: (1) whether a 24 ms p99 (vs 9.7 ms) is acceptable headroom
for the smoothers of M4/M5; (2) re-run the selection after the S2 caps
are re-derived per variant (M4 re-grade), since rtmpose-l_yolox-m
(lower latency, equal d2_raw, lower bone deviation) lost only on the
teleport gate; (3) the ranking rests on self-consistency against each
variant's own oracle, not on external truth.

## D-027

ID: D-027
Status: SETTLED (principle); UNCERTAIN (no smoother beyond One-Euro measured yet)
Decision: smoothers inside the S2 tracks may keep tangent-space or scalar internal state (log-map velocity, a scalar twist angle); the track output is always a unit quaternion on the track's manifold. Extension of D-005, not a change.
Why: the M4 One-Euro filter keeps an angular speed, and the twist smoother is a scalar One-Euro on the angle about +x, unwrapped against the previous raw sample. The M5 Kalman filter needs a tangent-space state [r, w]. D-005 only forbids angle-space OUTPUT state, because of the +-180 and gimbal problems. The output stays quaternion and is re-projected onto v1's Ry*Rz manifold for swing and elbow.
Alternatives: quaternion-only state, i.e. slerp chains with no velocity. Rejected because it cannot express the One-Euro speed term or the M5 Kalman state.
Evidence: strategies/smoother_base.py; tests/test_smoother.py (on-manifold output, twist about x only, ramp lag equal to the first-order EMA value).
Reversibility: smoother_base.py only; smoother "none" is the identity.
Review: whether a scalar twist state is acceptable for twist near +-180 deg (unwrap covered by test_twist_output_is_rotation_about_x).

## D-030

ID: D-030
Status: UNCERTAIN
Decision: bone-length projection along the camera ray (replay/bone_projection.py, config bones.project) is implemented and OFF by default.
Why: the projection moves a distal landmark along its own pixel ray to the calibrated bone length. It would remove depth-bleed length errors. But the clean-window oracle is computed from the UNPROJECTED landmarks, so switching the projection on scores S2 against a different reference. The previous worker measured swing rms0 3.73 -> 6.28 deg and 6 teleport failures with bones on (scratchpad fix.txt, warm_capman_innov_bones). That comparison is confounded, not a measured loss. It stays off until the oracle is computed from the same projected landmarks.
Constants: calibrate_frames 60 (the pre-M4 placeholder; median over the first 60 frames with both ends lifted); tolerance 0.064 = the mean oracle-side bone p95 fractional deviation for rtmpose-x_yolox-m, 4 bones x 4 clean windows (0.0640 of dataset/phase5_pose_sweep.txt). Both UNCERTAIN. depth.min_score is present and null (D-017 stands).
Alternatives: projection on by default (rejected: the confound above); a joint least-squares chain fit (more code; not needed until the confound is resolved).
Evidence: tests/test_bone_projection.py (ray geometry, calibration median, tolerance, infeasible case); no clean accuracy number, because of the confound.
Reversibility: config bones.project.
Review: compute the oracle from projected landmarks, then re-grade with project true.

## D-031

ID: D-031
Status: SETTLED (measured); UNCERTAIN (only one recording plus four windows)
Decision: S2 warm start: a track's FIRST measurement is taken as the output directly. The step caps apply from the second measurement on (config warm_start true).
Why: cold start approaches the first measurement from the rest pose along the geodesic at the cap (D-026: l_swing_z 67 deg off at frame 3, still 16 deg at frame 70 on 180042). Warm start alone cut S2's swing rms0 from 6.07 to 3.73 deg with 0 gate failures (scratchpad grid of the previous worker, rows legacy vs warm). The first frame is not a teleport in the D-003 sense, because the gate excludes 60 warmup frames.
Alternatives: faster caps during warmup (a second constant with no source).
Evidence: tests/test_smoother.py::test_warm_start_snaps_first_measurement; previous worker's fix.txt; dataset/phase5_s_grade__rtmpose-x_yolox-m.txt.
Reversibility: config warm_start false (the legacy regression test runs this way).
Review: whether a mid-stream first detection (person enters late) should also snap; currently yes.

## D-032

ID: D-032
Status: UNCERTAIN
Decision: S2 step caps are derived per track AND per side from the ACTIVE manifest: cap = step_cap_budget_fraction 0.8 (the D-021 rule) x the smallest non-degenerate budget among the angles the track drives (config step_cap_source manifest, step_cap_track_angles). The fixed table step_caps_deg stays as the legacy source.
Why: D-028 found the fixed caps inconsistent with each variant's own budgets (swing cap 1.0 vs r_swing_z budget 0.779). Deriving the caps makes D-021's rule hold by construction on every manifest. On the D-033 manifest the caps are root 0.692, r_swing 3.997, r_twist 4.345, r_elbow 4.082, l_swing 1.513, l_twist 2.789, l_elbow 3.814 deg/frame. The caps now bind on 2-24 percent of clean-window frames per arm track, down from 11-36 percent under the fixed caps (root 36 percent vs 59 percent; dataset/phase5_teleport_rule_check.txt section 4).
Constants: 0.8 from D-021 (UNCERTAIN there). Identically-zero angles are skipped at the 1e-6 threshold, well above the 1e-9 floor of teleport_budget.
Alternatives: caps on the innovation instead of the absolute output step (previous worker's warm_capman_innov; no gain in rms0, scratchpad fix.txt).
Evidence: dataset/phase5_teleport_rule_check.txt; tests/test_smoother.py derive_step_caps tests.
Reversibility: config step_cap_source fixed.
Review: the root cap stays tight (root_z budget 0.865) and still binds on 36 percent of clean frames; root_z is the limiting angle.

## D-033

ID: D-033
Status: UNCERTAIN
Decision: teleport budgets = 1.5 x p99.9 of the OFFLINE ORACLE's per-frame steps over the pinned bag (post-warmup) UNION the four clean windows, per angle and per variant (make_scenarios.py --budget-source oracle_union). Twist steps enter the derivation AND the teleport count only when the oracle solve has the twist observable on BOTH frames of the step: solver twist_ok (vacuous, v1 TWIST_EPS 1e-6) AND an elbow bend >= budget.twist_min_bend_deg = 30 deg (sin(bend) = |forearm perpendicular to the upper-arm axis| / |forearm| >= 0.5). Supersedes the budget half of D-003's derivation (clean-run steps of the causal baseline); the gate itself (teleport_count == 0) is unchanged. Author decision (budgets from real motion over the union), with master refinements (twist gating by bend; mask from the oracle; injection acceptance).
Why: the D-003 budgets came from the slow pinned recording (0.5-3.5 deg/frame). The S2 caps derived from them bound on 26-61 percent of clean-window frames where real motion reaches 5 deg/frame, which caused about half of S2's error against the oracle. The union rule as first stated let twist budgets explode (r_twist 2.29 -> 28.35, l_twist 4.81 -> 36.72 deg). Twist is ill-conditioned near a straight arm: the largest oracle twist steps sit at bends of 1-19 deg (49.7 deg at 1 deg bend). With those budgets baseline_hold passed with a 14.61 deg step. The solver's twist_ok excludes nothing, being true on 1628/1628 steps. Gated budgets per variant at 30 deg: r_twist 4.43-6.28, l_twist 3.11-5.10 deg. 25 deg leaves r_twist 11.68 (rtmpose-x_yolox-m) and 15.70 (rtmpose-m).
Mask source: the oracle's twist observability on the UNMASKED base CSV (and on each clean window's own oracle in grade_clean.py). The causal flag is false inside every occlusion window, so a causal mask would exempt the reacquisition twist snaps D-021 was built to prevent. The oracle mask is scenario-independent and is the condition the budgets were derived under.
Acceptance (replaces "warm, no caps must fail": with warm start and no caps the largest non-twist step in pose_loss is 0.99 deg, so that configuration has no real teleport). Inject a single step of 1.5 x the angle's budget into r_swing_z, and separately into r_elbow_y, on the first MEASURED frame after the pose_loss window. Both must FAIL and the un-injected S2 default must PASS. Result: r_swing_z +7.494 deg (step 7.413) FAIL, r_elbow_y +7.653 deg (step 7.739) FAIL, S2 default 0 teleports, worst step 2.79 deg, PASS.
Constants: 1.5 and p99.9 from D-003. twist_min_bend_deg 30 = the smallest 5-deg grid value giving single-digit twist budgets on all six variants. It was CHOSEN AFTER SEEING THE DATA, hence UNCERTAIN. Injection factor 1.5 x budget: master decision.
Alternatives: the union rule without gating (twist budgets 22.6-62.0 deg, gate vacuous for twist); solver twist_ok alone (vacuous); a fixed twist budget (no source); a causal-flag mask (exempts reacquisition snaps).
Evidence: dataset/phase5_teleport_rule_check.txt (budgets D-003 vs D-033, caps, injection, cap activity); configs/scenarios_20260224__rtmpose-x_yolox-m__oracle_union.json and output/pose_sweep/scenarios__<variant>__oracle_union.json; tests/test_teleport_gate.py; the per-variant bend-threshold tables (worker scratchpad twist_thr__<variant>.txt, 2026-09-25; not committed).
Consequence: per D-003's clause, S2 and baseline_hold are re-graded on the new manifests (dataset/phase5_s_grade__rtmpose-x_yolox-m*.txt, dataset/phase5_pose_sweep_recapped.txt). The pre-D-033 grade is kept as dataset/phase5_s_grade__rtmpose-x_yolox-m__pre_d033.txt and is reproduced by tests/test_smoother.py with the legacy overrides.
Reversibility: config paths.scenario_manifest back to scenarios_20260224__rtmpose-x_yolox-m.json (teleport_twist_gate none, ungated count); the old manifests are untouched.
Review: (1) the l_twist budget (3.49) is now BELOW its D-003 value (4.81), because the oracle is smoother than the causal pipeline; S2 passes, but any causal strategy with twist jitter at bent-elbow frames will be judged more strictly than before; (2) 30 deg was picked after seeing the data; (3) whether twist steps at straight-arm frames should be bounded by some other rule rather than exempted.
Annotations: D-003 (budget derivation superseded for the oracle_union manifests), D-020 and D-021 (the caps now follow D-032 on the D-033 budgets).

## D-029

Annotation 2026-09-25 (M5, finalisation; design and constants of the winner in D-038): the default smoother is decided. Rule, stated in the M5 brief before the comparison was run: among smoothers passing all three D-003 hard gates, pick the one with the lowest mean rms0 over the four clean windows x the 13 angles (elbow_z excluded, identically zero in the oracle) among those with mean d2/o <= 1.5 (d2/o = geometric mean of causal / oracle second-diff RMS); tie-break lower mean |lag|; if none meets the bound, the lowest d2/o. Inputs (dataset/phase5_smoother_compare__rtmpose-l.txt, 13-angle means; gates from dataset/phase5_s_grade__rtmpose-l.txt, __quat_one_euro.txt, __tangent_kf.txt, all PASS on teleport, honesty and latency): none rms0 3.925 / d2/o 3.142 (infeasible); quat_one_euro 4.188 / 1.456, |lag| 4.91; tangent_kf 4.171 / 1.467, |lag| 4.48. Result: tangent_kf; configs/default.json strategy.s2_quat_prediction.smoother = "tangent_kf". The rms0 margin is 0.017 deg (0.4 percent), small enough that another window set could reverse it; the tie-break metric (lag) and rmsL (2.387 vs 2.467) point the same way. Smoothest (lowest mean d2 causal): tangent_kf 0.631 deg/frame^2 (quat_one_euro 0.633, none 1.092); its accuracy price against "none" is +0.246 deg rms0 and +0.71 frames of lag. The quat_one_euro parameters above stay in smoother_params.quat_one_euro (smoother_params is now keyed by smoother name; a flat per-kind dict still works for sweep overrides). Status: the default is SETTLED by the stated rule; the rule's 1.5 bound and the four-window evidence stay UNCERTAIN.

Annotation 2026-09-25 (D-034): known limits (1) and (2) are addressed for rtmpose-l. The grid was re-run on rtmpose-l with beta extended to 64 and 128 under the same rule; winners root 2 / 8, swing 1 / 8, twist 4 / 8, elbow 2 / 2 (min_cutoff Hz / beta), none on a grid edge (dataset/phase5_smoother_grid__rtmpose-l.txt). default.json smoother_params now carry these rtmpose-l constants; the rtmpose-x_yolox-m values below stay as the record for that variant. The default smoother stays "none".

ID: D-029
Status: UNCERTAIN (provisional until M5)
Decision: smoother (i) quat_one_euro parameters per track kind = root min_cutoff 4 Hz / beta 8, swing 2 / 8, twist 4 / 32, elbow 2 / 2 (d_cutoff 1.0 Hz everywhere), picked from the pinned grid by a fixed rule; configs/default.json carries them in strategy.s2_quat_prediction.smoother_params but keeps smoother "none" as the default until the M5 comparison.
Selection rule (bench/sweep_smoother.py docstring, per kind): (1) feasible = d2/o <= 1.5, where d2/o is the geometric mean over clean windows x the kind's angles of second-diff RMS causal / oracle; pick the feasible point with the lowest rms0 (RMS vs the oracle at lag 0); (2) if none is feasible, the lowest d2/o among points whose rms0 is not above smoother "none"; (3) otherwise the lowest-rms0 point, flagged. All four kinds were decided by rule 1.
Grid: min_cutoff {0.5, 1, 2, 4, 8, 16, 32} Hz x beta {0, 0.5, 2, 8, 32} per rad/s, every kind at the same point per run (tracks of different kinds are independent state machines), on rtmpose-x_yolox-m, the four clean windows, the D-033 manifest, D-032 caps and D-031 warm start.
Trade-off at the chosen points (dataset/phase5_smoother_grid__rtmpose-x_yolox-m.txt; none -> quat_one_euro; rms0 deg, d2/o, mean |lag| frames):
  root   rms0 1.533 -> 1.576   d2/o 2.225 -> 1.403   |lag| 4.08 -> 4.33
  swing  rms0 2.850 -> 3.029   d2/o 3.062 -> 1.409   |lag| 3.12 -> 4.31
  twist  rms0 13.134 -> 13.146 d2/o 1.888 -> 1.452   |lag| 4.38 -> 4.62
  elbow  rms0 2.504 -> 2.953   d2/o 4.136 -> 1.448   |lag| 3.00 -> 4.75
The smoother lowers d2/o by 23-65 percent per kind and costs 0.01-0.45 deg of lag-0 RMS and 0.2-1.8 frames of lag. On the 13-angle clean mean rank (informational, D-026) none ranks 1.474 and quat_one_euro 1.526 (dataset/phase5_smoother_i__rtmpose-x_yolox-m.txt). S-type hard gates on rtmpose-x_yolox-m: 0/6 teleport and 0/6 honesty failures with both smoothers, worst S2 step 3.51 deg (none) and 2.79 deg (quat_one_euro) (dataset/phase5_s_grade__rtmpose-x_yolox-m.txt and __quat_one_euro.txt). Latency: strategy stage p99 0.55 -> 0.76 ms, total p99 24.08 -> 24.40 ms vs the 33.3 ms budget (dataset/phase5_realtime__rtmpose-x_yolox-m.txt and __quat_one_euro.txt). With the same parameters on all six variants every variant passes the gates with both smoothers (dataset/phase5_pose_sweep_recapped.txt).
Why: rule 1 keeps the output within 1.5 x the oracle's own roughness and then maximises accuracy, which is the plan's "smooth and accurate" goal expressed as a constraint plus an objective. The default stays "none" because neither setting dominates: quat_one_euro is smoother, "none" is more accurate at lag 0 and lags less. The author wants both, and the M5 tangent-space Kalman (designed for zero lag) is the comparison that decides the default; the parameters are in the config so the switch is one field.
Alternatives: switching the default to quat_one_euro now (rejected: it costs accuracy and lag and M5 may beat it on both axes); a single (min_cutoff, beta) for all kinds (rejected: the kinds' feasible optima differ, e.g. elbow needs beta 2, twist beta 32); a weighted sum of rms0 and d2/o (rejected: the weight would be a constant with no source).
Constants and sources: d_cutoff 1.0 Hz = config filter.d_cutoff (the v1 landmark One-Euro value); grid values = a log-spaced range, no source (UNCERTAIN); feasibility bound d2/o <= 1.5 has no recorded source (UNCERTAIN; it is not the D-003 1.5 x budget factor, although numerically equal).
Known limits: (1) the twist beta 32 sits at the grid edge (the next grid point in min_cutoff, 8 / 32, is infeasible at d2/o 1.542, but larger beta at min_cutoff 4 was not tried), so the twist optimum may lie outside the grid; (2) the grid was run on rtmpose-x_yolox-m only; the recapped pose selection now prefers rtmpose-l (dataset/phase5_pose_sweep_recapped.txt, D-028 annotation), for which the parameters were not re-swept; (3) the twist rms0 of about 13 deg is plausibly dominated by straight-arm frames where twist is ill-conditioned (D-033), because the clean-window metrics do not apply the bend mask; not isolated; (4) one recording for the gates, four clean windows for the ranking, self-consistency against the oracle only (D-024).
Evidence: dataset/phase5_smoother_grid__rtmpose-x_yolox-m.txt (bench/sweep_smoother.py grid), dataset/phase5_smoother_i__rtmpose-x_yolox-m.txt (bench/grade_clean.py --smoothers none,quat_one_euro), dataset/phase5_s_grade__rtmpose-x_yolox-m__quat_one_euro.txt, dataset/phase5_realtime__rtmpose-x_yolox-m__quat_one_euro.txt, dataset/phase5_pose_sweep_recapped.txt; tests/test_smoother.py.
Reversibility: config strategy.s2_quat_prediction.smoother and smoother_params; "none" is the identity (tests/test_smoother.py::test_none_is_identity; test_legacy_overrides_reproduce_pre_d033_grade reproduces the pre-D-033 grade).
Review: (1) whether the 1.5 feasibility bound expresses the jitter the author accepts; (2) extend the twist beta range before finalising; (3) re-sweep on the variant the master pins if it changes; (4) the M5 comparison (i) vs (ii) vs S2 decides the default smoother.

## D-034

ID: D-034
Status: UNCERTAIN (the re-pin is SETTLED as an author decision; every number behind it is a single run on one recording plus four clean windows)
Decision: Re-pin the V3 default model variant to rtmpose-l (RTMPose-l body7 384x288 + YOLOX-tiny humanart 416x416, det_freq 15), reversing D-028 under its Reversibility clause, with its own D-033 manifest configs/scenarios_20260224__rtmpose-l__oracle_union.json and the D-029 smoother parameters re-swept on rtmpose-l. Author decision 2026-09-25.
Rule: unchanged D-028 selection rule (stated before the M3 numbers), re-run in the M4 recap on each variant's own D-033 manifest with D-032 derived caps and D-031 warm start (dataset/phase5_pose_sweep_recapped.txt): every variant passes the S2 hard gates with smoother none and quat_one_euro, and rtmpose-l has the lowest d2_raw ratio (0.909 vs rtmpose-m; rtmpose-x_yolox-m 0.937) with mean oracle bone p95 0.0606 (reference 0.0799). The smoother parameters follow the D-029 rule (feasible d2/o <= 1.5, lowest rms0).
Re-measured for rtmpose-l (all on the pinned bag recording_20260224_083945 and the four clean windows of configs/clean_windows.json):
  manifest: make_scenarios.py --budget-source oracle_union --variant rtmpose-l, tracked copy with repo-relative paths; budgets and masked CSVs identical to the recap's output/pose_sweep/scenarios__rtmpose-l__oracle_union.json (compared before writing; cmp on all six masked CSVs). D-033 budgets e.g. r_swing_z 5.113, r_elbow_y 6.486, r_twist 4.791, l_twist 4.041, root_z 0.772 deg/frame; D-032 caps root 0.618, r_swing 4.090, r_twist 3.833, r_elbow 5.189, l_swing 1.633, l_twist 3.233, l_elbow 3.756 deg/frame.
  smoother grid (bench/sweep_smoother.py, min_cutoff {0.5,1,2,4,8,16,32} Hz x beta {0,0.5,2,8,32,64,128}, d_cutoff 1.0 Hz; dataset/phase5_smoother_grid__rtmpose-l.txt): winners by rule 1 for all four kinds, root 2 / 8, swing 1 / 8, twist 4 / 8, elbow 2 / 2. None -> quat_one_euro (rms0 deg, d2/o, |lag| frames): root 1.107 -> 1.178, 2.720 -> 1.467, 3.75 -> 4.33; swing 2.500 -> 2.765, 3.620 -> 1.448, 3.56 -> 4.69; twist 12.112 -> 12.469, 2.182 -> 1.434, 4.50 -> 5.12; elbow 2.817 -> 3.280, 4.230 -> 1.444, 3.50 -> 5.88. The twist winner moved from beta 32 (rtmpose-x_yolox-m, on the old grid edge) to beta 8; at min_cutoff 4 beta 32, 64 and 128 are infeasible (d2/o 1.644, 1.772, 1.890).
  clean bench (bench/grade_clean.py, dataset/phase5_smoother_i__rtmpose-l.txt): 13-angle clean mean rank none 1.452, quat_one_euro 1.548 (informational, D-026).
  S-type hard gates (bench/grade.py, dataset/phase5_s_grade__rtmpose-l.txt and __quat_one_euro.txt): S2 teleport 0/6 and honesty 0/6 failures with both smoothers, worst S2 step 3.34 deg (none) and 3.23 deg (quat_one_euro); baseline_hold fails teleport on 1/6 (pose_loss, 13.34 deg step; reference behaviour, not gated).
  teleport rule check (bench/teleport_rule_check.py --old-manifest output/pose_sweep/scenarios__rtmpose-l.json, dataset/phase5_teleport_rule_check__rtmpose-l.txt): injection of 1.5 x budget FAILS on r_swing_z (+7.669 deg) and r_elbow_y (+9.729 deg), un-injected S2 PASSES (worst step 3.23 deg); caps bind on 1-21 percent of clean-window frames per arm track and 32.5 percent for root.
  latency (replay/realtime.py, paced, no shm, env v3rt, RTX 3080, GPU idle by nvidia-smi before each run): total p99 12.14 ms (none) and 12.59 ms (quat_one_euro) vs the 33.3 ms budget (dataset/phase5_realtime__rtmpose-l.txt and __quat_one_euro.txt); M3 measured 12.44 ms.
  v1 offsets (bench/v1_offset_table.py, 898 common frames, dataset/phase5_v1_offset_table__rtmpose-l.txt): root_y -7.06, r_swing_y +8.18 (cstd 8.44), l_swing_y -9.66, r_twist +2.42 (cstd 5.92), l_twist -0.90 (cstd 5.66); elbow_z 0.00 both sides; grade_clean.py V1_OFFSET_TABLES gains the entry.
Why: with the D-028 confound removed by M4 (per-variant caps, warm start, D-033 budgets), the same rule that picked rtmpose-x_yolox-m now picks rtmpose-l for both smoothers, and rtmpose-l also halves the latency p99 (12.1 vs 24.1 ms) against the 33.3 ms budget. Re-sweeping the smoother on the pinned variant removes D-029's limits (1) and (2) for this variant.
Alternatives: keep rtmpose-x_yolox-m (rejected by the author; it loses on the unchanged rule and costs 12 ms more p99); rtmpose-l_yolox-m (lower bone deviation 0.0592 but d2_raw ratio 0.936 and total p99 21.41 ms; the rule ranks by d2_raw); keep the x-tuned smoother parameters on rtmpose-l (rejected: tuned on another variant, twist at the grid edge).
Evidence: the pinned files named above; dataset/phase5_pose_sweep_recapped.txt for the selection; tests/test_configs.py::test_default_variant_is_d034_pin; tests/test_baseline_scenarios.py evidence row for the new manifest (baseline_hold teleports per scenario, twist-gated as in grade.py).
Constants: none new. Grid values 64 and 128 extend D-029's log-spaced beta range (master brief 2026-09-25; no other source, UNCERTAIN as D-029's grid is); the 1.5 feasibility bound, d_cutoff 1.0 and the 1.5 x budget injection factor are inherited from D-029 and D-033.
Known limits: (1) single run per latency setting, measured on a shared machine (GPU idle confirmed only by nvidia-smi compute processes before and after each run); (2) the S-type gates rest on one recording and the smoother ranking on four clean windows, self-consistency against each variant's own oracle only (D-024); (3) the D-003 column of the teleport rule check comes from the gitignored output/pose_sweep/scenarios__rtmpose-l.json (recap artefact, not re-derived here); (4) the l_twist D-033 budget (4.041) is again slightly below its D-003 value (4.129); (5) the three M4 changes that flipped the ranking were not isolated (D-028 annotation).
Reversibility: config-only: default.json model block, paths.scenario_manifest and smoother_params back to the D-028 / D-029 values (rtmpose-x_yolox-m, configs/scenarios_20260224__rtmpose-x_yolox-m__oracle_union.json, root 4/8 swing 2/8 twist 4/32 elbow 2/2); tests/test_configs.py DEFAULT_VARIANT. All older manifests, pins and offset tables are kept.
Review: (1) whether the latency gain and the rule's verdict outweigh rtmpose-x's higher keypoint scores (pinned-bag mean 0.885 vs 0.780); (2) the smoother default stays "none" until M5; (3) re-run the latency on an unshared machine before quoting it outside V3.

## D-035

ID: D-035
Status: SETTLED (transform and frame alignment, by test and measurement); UNCERTAIN (grading against the raw rather than the filtered ArUco track is a judgment)
Decision: the wrist-to-object bench (M7) takes the object pose from the thesis's marker-size-corrected ArUco CSVs eval/output/<stem>_aruco_raw_scaled.csv (object id 1, camera-optical metres, 45 mm scale) and the scene calibrations eval/output/scene_calibration_{r4c,r5c,r6bc,r7c}.json, transformed into the levelled desk world by bench/aruco_source.py (a reimplementation of eval/offset/carry.py LeveledWorld plus the v1/aruco/calibrate_scene.py per-frame loop and v1/aruco/frames.py unity_from_world); V3 extraction row i is ArUco row i (frame-index equality, offset 0), and undetected marker frames are NaN (no filtering, no gap fill).
Why: the CSVs and calibrations already exist for R4-R7, so no v1 extractor copy is needed (plan A3 fallback not triggered). Frame-index equality was the explorer's finding (both count colour+depth framesets, non-real-time; offset 0 on R5 by eval/unity_check/side_by_side.py --lag-scan); here it is checked on every frame of all four recordings: after index alignment |time_s(ArUco) - time_s(V3)| is at most 0.001 ms against a half-frame tolerance of 16.68 ms (half the median V3 frame period), n = 1498 / 2098 / 899 / 1498 frames for R4 / R5 / R6b / R7 (V3 drops the last frame). The raw per-frame pose keeps the reference independent of any smoothing choice.
Alternatives: the thesis's filtered world track (<stem>_scaled_object_world_filtered[_clean].csv, v1/aruco/filter_object_track.py and eval clean_object_track.py): smoother and gap-filled, but it bakes a second filter into the reference; kept as the input of the thesis reproduction test only. Copying extract_aruco_poses.py into v3/vendor/v1: unnecessary while the CSVs exist.
Evidence: tests/test_aruco_source.py (R4 raw ArUco -> levelled world equals the thesis's <stem>_scaled_object_world.csv through carry.py's object_world path: position max diff 6e-16 m, rotation max diff 4.1e-6, the latter from the 6-decimal rotation columns of the ArUco CSV; alignment test on R4-R7); dataset/phase5_wrist_object__rtmpose-l.txt (alignment lines per recording).
Constants: object id 1 (v1/aruco/frames.py MARKERS); box centre = marker origin + R (0, -cube/2, 0) with cube 0.07 m from each calibration's scene_geometry.object_cube_size_m (carry.py box_center); half-frame tolerance = 0.5 x median V3 frame period (brief acceptance rule).
Reversibility: bench/aruco_source.py read_object is the single entry point; swapping to the filtered track means reading unity_p*/unity_e* through LeveledWorld.object_world (already implemented for the reproduction test).
Review: (1) whether the V3 numbers should also be reported against the filtered track, as the thesis did; (2) raw-marker jitter enters |v_rec - v_real| only through the box centre and R_obj (grip constancy, |wrist - centre|), not through err = |FK wrist - measured wrist|, where the object cancels.

## D-036

ID: D-036
Status: UNCERTAIN (constants SETTLED by source and reproduction test; applying the rule to the V3 wrist with src == 0 as the "clean" flag is a judgment)
Decision: holding frames per hand = the thesis geometry rule reimplemented in bench/holding.py: marker detected AND carried (rest_referenced_carried with the stage-1 manipulation envelope from eval/reports/<stem>_inspection.json: inside the envelope and farther than 0.04 m from both rest positions, or moving 0.03 m over 7 frames, or more than 0.06 m above the table) AND |measured wrist - box centre| < 0.25 m AND wrist clean AND forearm length within 30 percent of its recording median; evaluation episodes = hold_runs (gap > 15 frames splits, runs under 30 held frames dropped); grip_episodes (the causal state machine, ENTER 5 / EXIT 5 / RELEASE 0.35 m) is reported beside them. V3's wrist is the raw extraction wrist; clean = right/left_wrist_src == 0 (depth present, in frame) and finite.
Why: the author asked for "while the hand holds the object"; the thesis rule is the one the R4 numbers were produced with, so reusing it keeps V3 comparable. Finding: the thesis R4 episodes 254-388, 478-713, 1028-1112 (right) and 674-832 (left) come from the hold_runs split in eval/offset/analyze_offset_constancy.py, NOT from grip_state.grip_episodes; tests/test_holding.py reproduces all four runs, their n (134, 235, 85, 158), medians (14.3, 14.6, 17.0, 13.4 cm), stds (0.64, 1.54, 2.04, 1.87 cm), and the per-hand held counts (494, 158) and |wrist - centre| median/p95 (14.6/17.9, 13.4/17.3 cm) exactly from the MediaPipe-era inputs (v1/mediapipe/output/<stem>_landmarks_filtered.csv, eval/output/<stem>_scaled_object_world_filtered.csv, scene_calibration_r4c.json).
V3 on R4 (rtmpose-l): right held 596, runs 253-403 (139), 476-712 (235), 1027-1183 (148), 1258-1311 (46); left held 298, run 673-984 (294); grip_episodes right (257, 395), (444, 458), (478, 719), (1027, 1301), left (673, 1099). R5 / R6b / R7 in dataset/phase5_wrist_object__rtmpose-l.txt.
Alternatives: grip_episodes as the evaluation set (it holds through wrist failures, so v_real would be undefined on some of its frames); a new rule (no source).
Evidence: tests/test_holding.py (constants parsed from eval/offset/carry.py and eval/failure/grip_state.py; exact reproduction of the thesis R4 runs); dataset/phase5_wrist_object__rtmpose-l.txt.
Constants and sources: HOLD_RADIUS 0.25, FOREARM_TOL 0.30, REST_DIST 0.04, K 7, MOVE_DIST 0.03, CARRY_HEIGHT 0.06 (eval/offset/carry.py, eval E-005/E-006); ENTER_FRAMES 5, EXIT_FRAMES 5, RELEASE_RADIUS 0.35 (eval/failure/grip_state.py); gap 15 and minimum 30 frames (eval/offset/analyze_offset_constancy.py main); cube 0.07 m (calibration scene_geometry).
Reversibility: bench/holding.py CONFIG and the wrist_clean argument of holding_mask.
Review: (1) V3 classifies more frames as held than the thesis (R4 left 298 vs 158): the left run extends to 984 through the span the thesis calls "left with wrist OCCLUDED 27.5-35.5 s" (eval/reports/r4_stage3_offset_fit.md), because src == 0 only says depth was sampled, not that the wrist was visible; the measured-wrist floor may therefore contain occluded-wrist guesses (a score gate would be the next step; not tried here); (2) whether the thesis's run split should be replaced by grip_episodes for V3.

## D-037

ID: D-037
Status: UNCERTAIN (FK conventions SETTLED by closure and round-trip tests; the anchor-(b) construction and the median bone lengths are judgments)
Decision: core/fk.py fk_arm(angles13, side, Lu, Lf, anchor) built on the vendored v1 modules (root_frame.recompose_zxy, shoulder.recompose_shoulder, shoulder._ry/_rz, shoulder.MIRROR; right up = R_sh x, fore = R_sh R_elb x, left = MIRROR * the same, i.e. the vendored solve_left_arm docstring's M R M with rest arm -x), in solver (Unity) space. Two anchors, both reported: (a) the measured raw shoulder landmark of that side; (b) the measured raw right hip L24 + R_root @ offset, offset = component-wise median over the recording of R_root^T (shoulder - L24) on the oracle's filtered landmarks and angles. Bone lengths Lu, Lf = median over the whole recording of the oracle-filtered |shoulder - elbow| and |elbow - wrist| per side.
Why: anchor (a) is the thesis precedent (eval/failure/moving_window_check.py fk_wrist) and isolates the arm chain; anchor (b) also exercises the root, as plan A3 requires. The oracle (D-024) is the offline reference already used for the angles, so its medians are the calibration least tied to any causal strategy.
Results (dataset/phase5_wrist_object__rtmpose-l.txt, holding frames, cm, err = |v_rec - v_real| median/p95): anchor (a) is 0.8-3.4 cm median for every recording, hand, strategy and smoother (S2 none: R4 R 1.3/5.0, R4 L 3.3/15.1, R5 R 1.2/6.2, R5 L 3.1/11.6, R6b R 1.3/2.6, R7 R 1.0/2.4, R7 L 1.1/3.3); anchor (b) has p95 8.6-38 cm everywhere and a median of 10-30 cm for R5 left and R7 left. On R5's left run 1105-1451 the raw right-hip depth median is 1.084 m against 1.372 m over the whole recording while the left hip stays at 1.396 m, and the oracle root_x median moves from 0.4 to -22.0 deg: consistent with a corrupted right-hip depth tilting the root, NOT established as the cause.
Alternatives: anchoring at the hip midpoint or at a filtered hip (would hide the root error anchor (b) is meant to expose); per-frame bone lengths (make FK equal the measurement by construction); v1's calibrated segment lengths (MediaPipe-era, different landmark definitions, D-018).
Evidence: tests/test_fk.py: closure on the oracle's filtered landmarks of the right_elbow clean window (frames 180-540, both arms, per-frame bone lengths, anchor = filtered shoulder): FK elbow and wrist equal the landmarks to 1e-6 m on every frame; round trip of 10k random poses (root random, |tz| < 80 deg, ey in -170..-10 deg, ez = 0) through convert.angles13 -> FK -> solver_q.solve_frame_q -> angles13: angles within 1e-6 deg and positions within 1e-9 m; rigid-torso hip-anchor test; left-right mirror test.
Constants: bone lengths and offsets per recording are printed in the pinned text (R4 right Lu 0.2513 / Lf 0.2184 m, left 0.2690 / 0.2191 m; R5 0.2605 / 0.2301, 0.2654 / 0.2367; R6b 0.2760 / 0.2154, 0.2826 / 0.2567; R7 0.2305 / 0.2370, 0.2375 / 0.2309); test ranges |tz| < 80 deg and ey in -170..-10 deg keep the random poses away from the solver's gimbal and straight-elbow branches (no other source; test-only).
Reversibility: core/fk.py is new and only used by bench/grade_wrist_object.py.
Review: (1) anchor (b) is not usable as a reconstruction anchor on these recordings without a hip-depth check; (2) the right-hand R5 and left-hand R4 S2 p95 (6.2 and 15.1 cm) are larger than baseline_hold's (4.3 and 7.0 cm) at similar medians (1.2 vs 1.2, 3.3 vs 2.7 cm), so S2 has tail errors on held frames that the clean-window bench does not see; (3) FK(a) cannot be better than the measured-wrist noise: the grip-vector std of the measured wrist alone (the depth-side floor) is 3.0-7.1 cm per hand, and the oracle FK(a)'s is within 0.2 cm of it except R4 left (7.8 vs 7.1), R5 right (3.4 vs 3.0) and R5 left (5.6 vs 6.3).
Annotation 2026-09-25 (bench re-run with tangent_kf, D-038 review item 3): dataset/phase5_wrist_object__rtmpose-l.txt regenerated with --smoothers none,quat_one_euro,tangent_kf; the none and quat_one_euro rows are byte-for-byte unchanged (diff against the git history version at 06d0b3b). Anchor-a tangent_kf median/p95 (cm) sit inside the same 0.8-3.4 cm median band as none and quat_one_euro, close to quat_one_euro throughout: R4 right 1.3/4.9, R4 left 3.4/15.3, R5 right 1.3/6.5, R5 left 3.1/12.1, R6b right 1.3/2.7, R7 right 1.0/2.5, R7 left 1.1/3.2.

## D-038

ID: D-038
Status: UNCERTAIN (design SETTLED by tests; the q_w and r_v values come from one grid on four clean windows under D-029's rule, whose 1.5 bound is UNCERTAIN)
Decision: smoother (ii) "tangent_kf" (strategies/smoother_kalman.py): per S2 track a causal constant-velocity Kalman filter in the tangent space: state [r (3), w (3)], r = qlog(q_ref^-1 q), w body-frame angular velocity, re-linearised every frame (q_ref <- q_ref qexp(r), r <- 0); twist is the scalar 1-DOF version [theta, omega] on the unwrapped angle about +x; swing and elbow outputs (and state) re-projected onto v1's Ry*Rz by project_v1_swing. Process noise = continuous white-noise acceleration q_w plus a position random walk q_r; measurement variance r_v; Joseph-form update. Per kind: root q_w 1000 / r_v 1, swing 100 / 0.3, twist 1000 / 0.3, elbow 100 / 1 (q_w deg^2/s^3, r_v deg^2), q_r 1 deg^2/s everywhere; decay_lambda null = S2's 0.8; lag_frames 0. Chosen as the default smoother by the D-029 finalisation rule (annotation there).
Design: (1) the covariance is P2 (x) I3 exactly because Q, R and H are isotropic and the initial P is isotropic, so it is carried as one symmetric 2x2 block (three floats); symmetric by construction, Joseph form keeps it positive definite (test: 10k mixed updates); equality with a textbook matrix Kalman filter is a test. (2) The covariance passes through the re-linearisation unchanged (first order; the exact reset Jacobian I - [r/2]x differs at second order in r). (3) Unmeasured frames: S2 calls update(q_track, measured=False); the filter runs the predict with the velocity multiplied by decay_lambda (so it dies out at S2's rate), inflates P, then re-synchronises its orientation to the track output; update(None) is predict-only (per-frame increments shrink by exactly 0.8, test). (4) Initialisation by two-point differencing (Bar-Shalom, Li and Kirubarajan 2001, sec. 5.5.3): first sample -> output; second -> w = difference / dt, P0 = r_v [[1, 1/dt], [1/dt, 2/dt^2]]; no extra constant. (5) lag_frames > 0 enables a fixed-lag RTS smoother that outputs frame t - lag_frames; off because the PSV3 packet has no lag field (replay/psv3.py), so Unity could not know the pose is late (plan "Deferred: declared smoothing lag").
Constants and sources: dt = 1 / config filter.freq_hz (30 Hz). q_r = 1 deg^2/s is a normalisation, not a tuned value: with P0 proportional to r_v the output depends only on q_w / q_r and r_v / q_r; the same grid with q_r = 10 reproduces every one of the 63 scaled (10 q_w, 10 r_v) points to the printed precision (dataset/phase5_smoother_ii_grid__rtmpose-l.txt, sensitivity section). q_r = 0 (the pure CWNA model, a one-parameter family in q_w / r_v) is worse (rule-1 rms0 root 1.184, swing 2.835, twist 12.444, elbow 3.266 vs 1.179, 2.766, 12.418, 3.232) and three of its four winners sit on the grid edge (q_w 10). q_w, r_v per kind = rule-1 winners of q_w {10 .. 1e6} x r_v {0.01 .. 100} in half-decade steps, every kind at the same point per run as in D-029; none on a grid edge; the grid range itself has no source (UNCERTAIN). decay_lambda 0.8 = S2's (D-021, UNCERTAIN there). The 13-angle mean exclusion threshold in bench/grade_clean.py angle_means (oracle second-diff RMS <= 1e-6 deg/frame^2) = the D-032 degenerate threshold. LAG_WEIGHT_DEG 0.5 in bench/sweep_smoother.py = master brief value for the informational lag-weighted rule, no measured source (UNCERTAIN). The 50 us update budget = master brief (measured median 5 us twist, 21 us root, 33 us swing and elbow).
Results (rtmpose-l; four clean windows; D-033 manifest, D-032 caps, D-031 warm start). Per kind at the rule-1 points, tangent_kf vs quat_one_euro (rms0 deg, |lag| frames, rmsL deg, d2/o): root 1.179 vs 1.178, 3.83 vs 4.33, 0.680 vs 0.750, 1.472 vs 1.467; swing 2.766 vs 2.765, 4.44 vs 4.69, 1.439 vs 1.554, 1.450 vs 1.448; twist 12.418 vs 12.469, 5.12 vs 5.12, 7.576 vs 7.644, 1.479 vs 1.434; elbow 3.232 vs 3.280, 4.88 vs 5.88, 1.699 vs 1.711, 1.462 vs 1.444. Lag-weighted rule (min rms0 + 0.5 deg x |lag| under d2/o <= 1.5, informational): the Kalman's pick equals its rule-1 pick for every kind and scores 3.096 / 4.985 / 14.980 / 5.670 against quat_one_euro's best 3.343 / 5.090 / 15.029 / 6.220 (quat_one_euro's lag-weighted swing pick moves to 4 / 0). So the Kalman's advantage is lag and rmsL, not lag-0 RMS. 13-angle means, S-type gates and latency: D-029 finalisation annotation and README M5 table; worst S2 step 3.52 deg (elbow_long) vs 3.23 with quat_one_euro, strategy p99 0.76 ms, total p99 12.65 ms. Synthetic (tests/test_smoother_kalman.py, default params, 1 deg/frame ramp with N(0, 0.5 deg) noise): lag 0.039-0.042 frames vs quat_one_euro 0.61-1.57; a 20 deg step overshoots by 2.4-3.0 deg and settles within 0.1 deg in 9-23 frames (quat_one_euro 3-8 frames, no overshoot).
Why: the plan's M5 hypothesis was that the measured losses are filter lag and jitter; a velocity state removes the ramp lag that a first-order filter cannot (type-2 tracking loop), at the same jitter level. On real motion the gain is smaller (0.43 frames mean) because about 3.8 frames of lag come from the upstream landmark filter (D-015), which smoother "none" already shows, and because arm motion is not constant-velocity.
Alternatives: a full 6x6 numpy covariance (identical for isotropic noise, slower); q_r tied to q_w (the whole Q scales with q_w, so only q_w / r_v matters: the one-parameter family that tested worse as q_r = 0); q_r = 0 (worse, grid edge); the exact reset Jacobian (second-order effect, more code); a lagged RTS default (needs a PSV3 lag field); an adaptive (innovation-scaled) Q to cut the step overshoot (a new constant with no source; not tried).
Evidence: tests/test_smoother_kalman.py (identity, manifold, twist unwrap, ramp lag vs quat_one_euro, step convergence, lambda decay, S2 re-sync, SPD over 10k updates, equality with a matrix Kalman filter, fixed-lag option, speed, registration and config plumbing); dataset/phase5_smoother_ii_grid__rtmpose-l.txt; dataset/phase5_smoother_compare__rtmpose-l.txt; dataset/phase5_s_grade__rtmpose-l__tangent_kf.txt; dataset/phase5_realtime__rtmpose-l__tangent_kf.txt.
Reversibility: config strategy.s2_quat_prediction.smoother ("none" or "quat_one_euro") and smoother_params.tangent_kf; smoother "none" still reproduces the pinned S2 grade (dataset/phase5_s_grade__rtmpose-l.txt S2 section re-run identical).
Review: (1) the step overshoot on fast stops (2.4-3.0 deg on a 20 deg synthetic step), to be judged by eye in the M8 side-by-side; (2) whether a 0.017 deg rms0 margin should decide the default, or the lag and rmsL advantage should be the stated reason; (3) the wrist-to-object bench (M7, D-035..D-037) was graded with none and quat_one_euro only; re-run it with tangent_kf before quoting the default stack there.
Annotation 2026-09-25 (review item 3 closed): bench/grade_wrist_object.py re-run with --smoothers none,quat_one_euro,tangent_kf (rtmpose-l, r4/r5/r6b/r7); the script accepted tangent_kf and the nested smoother_params.tangent_kf without changes; none and quat_one_euro rows are unchanged from the pre-M5 pin. tangent_kf's anchor-a wrist-to-object error is statistically indistinguishable from quat_one_euro's (both within the 0.8-3.4 cm median band reported under D-037; see that decision's annotation for the per-recording numbers) -- the default stack (S2 + tangent_kf) is now quoted with wrist-to-object evidence, not just the clean-window angle grades.

## D-039

ID: D-039
Status: UNCERTAIN (projection, cube geometry and frame alignment SETTLED by tests and per-frame checks; the anchor choice, the colour-to-bone mapping and the editorial film constants are judgments; the films are judged by the author's eye, plan A4)
Decision: M8a side-by-side film contract (tools/side_by_side.py, tools/render_rig.py). One 1536x576 film per recording = two 768x576 panels of the SAME bag frame (CSV frame index = BagSource index; the bag timestamp is checked against the CSV time_s on every frame, tolerance half a frame period as in D-035). Left: the bag colour frame (BGR -> RGB, LANCZOS 640x480 -> 768x576) with the RTMPose pixels of the eight v1 landmarks from the extraction CSV (<name>_u/_v; filled = depth sampled, ring = depth hole) and the eight-landmark skeleton drawn thin. Right, on a dark background, in the same camera view (extraction .meta.json intrinsics, pinhole; the colour streams carry zero distortion): torso = hip-shoulder quadrilateral of the causally filtered landmarks the strategy received (replay/runner.py <name>_f*, held at the last valid value while missing); upper arm and forearm = core/fk.py fk_arm from the 13 output angles, anchored at that filtered shoulder, bone lengths = per-recording medians of the oracle-filtered landmarks (D-037); ArUco object cube from bench/aruco_source.py (camera optical, 45 mm scale, cube 0.07 m, centre = marker origin + R (0, 0, -cube/2), the OpenCV-axis form of carry.py box_center) on detected frames (R4-R7 only); the measured (raw CSV) wrist as a faint grey ring; per-group status chips and a whole-film status timeline with a cursor. Colours: white MEASURED, amber ESTIMATED, red LOST; torso = root, upper arm = swing, forearm = the worse of twist and elbow. The stack is the default config run on the whole extraction CSV from frame 0 (S2 s2_quat_prediction, warm start D-031, D-032 caps on the D-033 rtmpose-l manifest, smoother tangent_kf D-038), then sliced.
Why: the author's acceptance is by eye (plan "Deliverable and acceptance"), so both panels must share geometry: the rig is projected through the same pinhole as the photo, so a correct reconstruction lies on the person. The filtered landmarks are the anchor rather than D-037's raw measured shoulder because they are what the live pipeline publishes (replay/realtime.py writes them into PSV3) and they carry the same filter lag as the angles; a raw anchor would mix a lag-free shoulder with lagged angles. Holding the last valid value keeps the rig drawn through landmark dropouts, which is where the occlusion criterion is judged.
Alternatives: the raw measured shoulder of D-037 anchor (a) (lag mismatch, missing on depth holes); the hip anchor (b) (unusable, D-037); running the detector again to draw all 17 COCO keypoints (needs the GPU env and re-inference; the extraction CSV stores only the eight v1 landmarks, so only those are drawn); plan A4's extra 3D view (the M8a brief specified the camera view only; not built); writing PNG frames then encoding (disk heavy; frames are piped as rawvideo into ffmpeg instead).
Constants and sources: panel 768x576, scale 1.2 and the LANCZOS resize = presentation/defense_2026/anim/unified_panels.py CAMERA_RECT / CAMERA_SCALE / compose; pinhole and Camera-prime flip = coordinate_axes.py project_pinhole / CAMERA_TO_CAMERA_PRIME (copied, not imported); amber (230, 166, 26) and red (217, 26, 26) = round(255 x) of Unity/Assets/Scripts/V3/V3PersonReceiver.cs estimatedColor (0.9, 0.65, 0.1) and lostColor (0.85, 0.1, 0.1); white measured = M8a brief; encoder libx264 preset slow crf 20 yuv420p +faststart = presentation/defense_2026/anim/causal_replay.py stage_encode (master film), system /usr/bin/ffmpeg 6.1.1 (imageio-ffmpeg is not installed in either env); 30 fps = brief, equal to the measured median frame period of every CSV (33.3 ms); half speed = input rate 15 fps re-timed to 30 fps output; clean-window lead-in 1 s = 30 frames (brief); start-of-stream warmup 60 frames excluded from the summary step statistics = configs/bench.json latency.warmup_frames; twist steps exempt at a bend < 30 deg = the manifest's twist_min_bend_deg (D-033), here computed from the causal output angles instead of the oracle; contact sheet cap 1.5 MB (brief), tiles 768x288, 256-colour PNG. No source (editorial or chosen after viewing, UNCERTAIN): the second "reacquiring" contact frame 10 frames after reacquisition; the 30-frame (1 s) post-reacquisition window of the summary; bone 6 px, torso 4 px, joint radius 6 px, keypoint radius 4 px, thin skeleton 2 px, background (16, 16, 16), cube blue = AXIS_COLORS Z, keypoint green = AXIS_COLORS Y.
Contact-frame rule: occlusion = any group not MEASURED; the episode = the longest occlusion run with a clean frame on both sides inside the film (else the longest); clean = 1/3 and 2/3 of the longest all-measured run; entering = the last clean frame and the onset; during = 1/3 and 2/3 into the episode; reacquiring = the first measured frame after it and 10 frames later.
Evidence: tests/test_side_by_side.py (known-point projection; equality with rs2_project_point_to_pixel on the bag intrinsics; camera-frame cube centre -> levelled world equals aruco_source box_center on R4 to 1e-9 m; contact-frame picking; occlusion-summary steps, twist exemption and warmup; 20-frame smoke film: 20 frames, 1536x576, h264 yuv420p 30/1; manifest schema); the per-frame bag-vs-CSV time check in every film (max |dt| in the manifest); dataset/phase5_side_by_side_manifest.json, dataset/phase5_side_by_side_summary.txt, dataset/phase5_side_by_side_<name>.png; frames viewed by the worker (report of 2026-09-25).
Observations (dataset/phase5_side_by_side_summary.txt; worker viewed R4 frames 293, 688, 1090, R5 frame 2062 and the R4 and right_elbow contact sheets): the rig lies on the person in the camera view on measured frames (shoulders on the keypoints by construction of the anchor; FK elbows and wrists within about 2-15 px of the RTMPose keypoints on the frames viewed, estimated by eye), the cube sits on the marker, and the status colours turn amber through occlusions. At every reacquisition frame of all eight films the largest step is within the D-033 budget (0.58-0.80 x). Over budget elsewhere: R4 10 frames (l_twist 17.8 deg step at frame 1090 while L_twist is ESTIMATED, 4.39 x), R5 46 frames (38 root, root_x up to 1.59 x while root is ESTIMATED; l_twist 1.94 x at frame 85), R6b 1 frame (r_twist 1.03 x on the last frame), R7 and the clean windows 0. ESTIMATED also marks frames where S2's step cap binds (strategies/s2_quat_prediction.py: a capped frame is non-converged), so amber appears on fully visible frames (e.g. R5 2062: every landmark depth-sampled, scores 0.54-0.80, root and right arm amber). Not investigated: why an Euler step can exceed its budget while the geodesic step is capped.
Reversibility: tools/side_by_side.py and tools/render_rig.py are new and used by nothing else; films are gitignored and re-rendered with one command.
Review: (1) watch the films against the two acceptance criteria; the summary lists every reacquisition step against the D-033 budget; (2) whether the filtered-landmark anchor should be replaced by the raw measured shoulder; (3) the right panel is a Python stand-in for the Unity rig of M8b.

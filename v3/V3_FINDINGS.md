# V3 findings log

Running log of measured results. Every number here must come from a
pinned run (command + config hash + git commit recorded alongside).
Newest at the bottom of each section.

## Phase 0 (setup, metrics)

2026-08-06: Phase 0 delivered: worktree + docs + configs +
bench/metrics.py + tests (default pytest run, no onnxruntime needed).
No measured findings yet; metric definitions and the ranking rule are
recorded in V3_DECISIONS.md D-003/D-004.

## Phase 1 (detector)

2026-08-06 env v3rt: onnxruntime-gpu 1.22.0 (CUDA 12 build; see
D-008), rtmlib 0.0.16 (--no-deps). Models pinned to v3/models/
(MODELS.sha256): YOLOX-tiny HumanArt 416x416 det, RTMPose-m body7
256x192 pose. CUDAExecutionProvider active with base-torch CUDA-12
libs preloaded. RTMPose-m raw forward, RTX 3080, 200 runs after 20
warmup: p50 1.58 ms / p95 1.72 ms / p99 2.00 ms. CPU fallback: p50
6.05 ms / p99 11.50 ms. Both fit the 33.3 ms budget with margin.

2026-08-06 detector module acceptance on the FULL pinned bag (897
aligned frames, non-realtime playback, GPU, evidence:
dataset/phase1_detector_smoke.txt): person found on 897/897 frames
(100.0 pct); detection ran on 73 frames (8.1 pct; scheduled 1-in-15 =
6.7 pct plus triggers) so box reuse engages; detector-stage per-frame
latency excluding 60 warmup frames p50 2.72 / p95 8.37 / p99 8.96 /
max 9.78 ms (warmup max 324 ms, EP initialization); v1-landmark
(COCO 5-12) mean score median 0.757, p5 0.716. Trigger fix D-012:
level-triggered border contact had degenerated to detect-every-frame
because the head touches the top edge throughout this recording.
NOTE the {5,15,30} det_freq sweep from the plan has NOT run yet;
det_freq 15 is inherited from the plan, not yet validated (UNCERTAIN
until the sweep runs in Phase 3's runner).

## Phase 2 (math core)

2026-08-06 oracle identity PASS: quaternion path (solver_q + convert)
reproduces the verbatim vendored v1 solvers to < 1e-9 deg on 10000
random poses and all singular branches (shoulder gimbal, straight
elbow, +-180 seam, root euler lock at 1e-6). Suite: 61 tests passing
in 3.6 s with numpy + pytest only.

## Phase 3 (integration, gate, baseline)

2026-08-06 V3 extraction of the pinned bag (tools/extract_bag_to_csv
.py, non-paced, GPU; evidence: dataset/phase3_extraction.txt): 898
frames in 5.3 s wall, person found on all 898, detection ran on 8.1
percent; ZERO no-depth and ZERO out-of-frame samples across all 7184
landmark samples. Contrast with v1's MediaPipe extraction, which had
visibility- and depth-blocked cells: RTMPose abstains from nothing --
every occluded joint arrives as a confidently-placed point. The gate
recalibration is therefore not optional; until it exists, the
extraction carries scores and src codes only (no gating applied).
Output: v3/output/extraction_recording_20260224_083945.csv + meta.

2026-08-06 detector sweep (bench/sweep_detector.py, det_freq {5,15,
30} x YOLOX {tiny,m}, full bag, non-paced, warmup 60 excluded, GPU;
evidence: dataset/phase3_detector_sweep.txt): coverage 898/898 and
median eight-landmark score 0.753-0.758 in EVERY combination; stage
p99 8.5-8.6 ms (tiny) vs 16.8-17.8 ms (m); box-center step p95
40-54 px (tiny) vs 8-20 px (m) -- m's boxes agree better with the
pose crop but the difference does not reach the scores. Verdict in
D-016: keep tiny + det_freq 15; revisit after occlusion runs.

2026-08-06 gate weak labels (bench/gate_weak_labels.py on the pinned
extraction; evidence: dataset/phase3_gate_weak_labels.txt): the
plan's depth-front rule is INVALID for wrists on this task -- right
wrist flagged on 889/898 frames, left on 363, because the subject
reaches forward throughout; flagged wrist samples score HIGHER
(median 0.818) than unflagged (0.789), so the weak labels
anti-correlate with occlusion truth and the Youden fit degenerates.
Shoulders/elbows/hips: zero depth-front hits; velocity rule: zero
hits everywhere. Verdict in D-017: no thresholds proposed, config
nulls stay; the gate needs prediction-relative depth or manual
labels, and possibly a recording with more true occlusion frames.

2026-08-06 V3-vs-v1 offset table (bench/v1_offset_table.py, both
raw extractions through the identical vendored solver, 898 common
frames, no smoothing; evidence: dataset/phase3_v1_offset_table.txt):
root_y offset -7.61 deg (cstd 4.65), r_swing_y +9.03 (9.62),
l_swing_y -9.45 (6.35), twists +1.83/-0.92 (cstd 6.61/6.34, the
wrist-redefinition spread), elbows +0.68/+1.54 (cstd 3.3); elbow_z
exactly zero on both sides (v1's ez == 0 construction confirmed for
V3). Subtract offsets and state cstd before quoting any comparison.

2026-08-06 S-type scenarios + derived teleport budgets
(bench/make_scenarios.py; windows in D-019, budgets in the manifest,
1.5 x p99.9 of the clean causal run, warmup 60 excluded, 1e-9 deg
floor per D-020). BASELINE GRADE (bench/grade.py, evidence:
dataset/phase3_baseline_grade.txt): honesty perfect in every scenario
(false_measured 0.000); wrist_short fully repaired (E_occ max 0.91
deg, 0 teleports); wrist_long held at E_occ 0.69/max 1.51, reacq
1.38, 0 teleports; elbow_long E_occ 2.87/max 3.89, reacq 2.63 and 1
TELEPORT; root_ref 2 TELEPORTS; hip and pose_loss small and clean.
Estimated-coverage 0.68 on 45-frame windows (ESTIMATED 30 then LOST
15, the lost_after boundary working as specified). VERDICT: the
baseline fails the teleport hard gate on elbow_long and root_ref via
the reacquisition snap -- the measured bar for Phase 4.

(gate ROC tables land here after the manual labeling pass)

## Phase 4 (strategy bake-off)

2026-08-06 S2 vs baseline on the six S-type scenarios (evidence:
dataset/phase4_s2_vs_baseline.txt): S2 passes ALL hard gates
(baseline fails teleport on elbow_long and root_ref); worst step 1.90
vs 3.81 deg; elbow_long reacq 1.63 vs 2.63; wrist_short e_occ 0.46 vs
0.74; honesty perfect on both. S2's drift costs it on near-static
holds (root_ref e_occ 2.73 vs 1.11, pose_loss 2.35 vs 1.96). Three
S2 bugs were found BY the grade and fixed (D-021): composite-track
twist snap, wrong decomposition manifold, uncapped measurement
discontinuities.

2026-08-06 END-TO-END realtime verification (paced bag, GPU, S2,
PSV3 on; evidence: dataset/phase4_realtime_e2e.txt): 883/883 frames
found at 28.7 fps sustained; per-frame total p50 3.95 / p95 9.65 /
p99 10.65 / max 11.25 ms vs the 33.3 ms budget -> PASS with 3x
headroom. Stage p99: detect 9.74, depth 0.14, filter 0.35, strategy
0.54, publish 0.02 ms.

## Phase 5 (full runs)

(none yet)

## 2026-09-25 Pose prediction models: assessed, not adopted

Survey (scratchpad pose_prediction_survey.md, this worker session);
condensed per the plan's addendum A2. Question: for V3's measured
losses, does a learned or model-based temporal predictor beat the
planned M5 tangent-space Kalman (D-038)? Plug-in points: P1 2D infill
before the depth lift; P2 3D landmarks after the lift, feeding the
existing solver; P3 a smoother or strategy on the quaternion tracks;
all keep D-005 and the 13-angle packet if they output landmarks or
quaternions and leave convert.py untouched.

Key finding: V3's measured losses (lag 3-5 frames, second-diff RMS
0.51 vs oracle 0.18 deg/frame^2 on r_elbow_y, D-026) come from the
causal landmark filter, not from missing foresight; a tangent-space
Kalman (M5) is the cheap fix, and no paper found compares a tuned
Kalman against a learned forecaster on noisy detector input at 1-3
frame horizons. Learned models help only for multi-frame occlusion
infill, and V3 cannot yet tell when a joint is occluded (RTMPose never
abstains, D-017 thresholds unfitted); any learned infill is blocked on
that gate.

A. Learned motion forecasting (P2 during ESTIMATED frames, replacing
S2's decayed velocity; needs retraining on the eight V3 landmarks --
no legs/spine in this lift):

| Model | Year, licence | Data, joints, fps | Causal | Note |
|---|---|---|---|---|
| siMLPe (github.com/dulucas/siMLPe) | 2023, MIT | H3.6M/AMASS/3DPW, 22/18 jt, 25 fps, 50-frame input | yes | 0.14M params; best fit |
| AuxFormer (github.com/MediaBrain-SJTU/AuxFormer) | 2023, no licence | H3.6M etc. | yes | trained to recover masked/noisy joints |
| EqMotion (github.com/MediaBrain-SJTU/EqMotion) | 2023, MIT | H3.6M | yes | equivariant |
| HisRepItself, PGBIG, MotionMixer; HumanMAC | 2020-23; no licence; MIT | H3.6M, 25 fps | yes | superseded; HumanMAC is stochastic diffusion |

siMLPe H3.6M MPJPE at 80 ms: 9.6 mm vs 23.8 mm for repeating the last
frame (paper Table 1; no constant-velocity baseline reported).
Martinez et al. (CVPR 2017): a zero-velocity baseline beat earlier
RNN predictors. High domain-shift risk (25 fps noise-free mocap vs 30
fps noisy RTMPose-plus-depth); output must stay ESTIMATED and never
feed back as a measurement; needs self-training (seeds, split and
weight hash pinned).

B. Temporal 2D-to-3D lifting and refinement (P1/P2 infill: lift a
window, align to the measured depth landmarks by a similarity
transform):

| Model | Year, licence | Window | Causal | Note |
|---|---|---|---|---|
| MotionBERT-lite (github.com/Walter0807/MotionBERT) | 2023, Apache-2.0 | up to 243 | no (last-frame use possible) | confidence input, masking pretrain, 61 MB |
| MotionAGFormer-XS (github.com/TaatiTeam/MotionAGFormer) | 2024, Apache-2.0 | 27 | no | 2.2M params, 1.0 GMACs |
| VideoPose3D (github.com/facebookresearch/VideoPose3D) | 2019, CC BY-NC | 27-243 | --causal flag | non-commercial |
| SmoothNet | 2022, Apache-2.0 | 32 | no | authors state it is not real time |

Trained on H3.6M studio poses, root-relative; desk occluders unseen.
Checkpoints 61 MB or less; needs a COCO-to-H36M joint map with spine
and thorax synthesised. Highest risk: can place a hidden wrist
confidently and must never feed back as measured.

C. Online SMPL mesh with motion context: not a near-term candidate
(the author deferred it). WHAM (2024, MIT code; SMPL/AMASS weights
non-commercial) is a unidirectional RNN "suitable for online
inference," but the full pipeline runs about 9 fps, not 33 fps. GVHMR
(ZJU licence, non-commercial, offline), CoMotion (Apple
research-only), OnlineHMR (2026, no licence file, needs MASt3R-SLAM
plus Detectron2 plus PyTorch3D) were ruled out on licence or latency.
Mapping SMPL rotations to v1 swing/twist is not direct (the collar and
spine share the shoulder motion); positions would be the safer path,
adding a new D-018-style definitional offset.

D. Classical, no training (P3, native to D-005 and D-027):

| Method | Evidence | Fit |
|---|---|---|
| Tangent-space constant-velocity/acceleration Kalman (M5) | CV/DES equals KF (LaViola 2003); last-frame is a strong short-term baseline (Martinez 2017) | well under 1 ms (UNVERIFIED), no installs |
| IMM (CV plus CA plus near-static) | no joint-level comparison found | addresses S2 drift on static holds (D-022) |
| LSTM-KF hybrid (Coskun et al., ICCV 2017) | beat KF and LSTM alone (search summary, paper not read) | later option |
| Joint-limit and bone-length priors | bench already measures them | constraint step |

Honest answer: on clean 30 fps motion with a 33-100 ms horizon, a
well-tuned Kalman should match a learned predictor; siMLPe's 80 ms
advantage is over last-frame repetition on noise-free mocap, not over
a velocity model on noisy detector joints. Learned models may add
value only for long occlusions (a 10-frame threshold used in the
survey is a judgement, unsourced) and joint infill, once the D-017
occlusion gate works.

Ranked shortlist:
1. Tangent-space Kalman with an IMM (CV/CA/static) mode set on the S2
   tracks (P3; M5 plus IMM). M5's single-mode CV version shipped as
   D-038; the IMM extension was not built this round. Stop if any
   D-003 gate fails, or if the lag gain costs more than it saves in
   second-diff RMS on the clean bench.
2. The D-017 occlusion gate plus siMLPe retrained on the 8-landmark
   upper body at 30 fps, used only for ESTIMATED frames (P2). Stop if
   it does not beat #1 on E_occ at 10 or more masked frames, if the
   p99 budget fails, or if the licence is unacceptable.
3. MotionBERT-lite asynchronous infill aligned to depth (P1/P2), as an
   offline spike first. Stop if the last-frame error beats neither S2
   nor #2, or if it cannot run outside the frame path.

Licence caveats: dataset licences (H3.6M, AMASS, SMPL: registration,
non-commercial) are from memory, not re-fetched this round; whether
model weights inherit those terms is legally unresolved. Desktop GPU
latency for siMLPe, MotionAGFormer-XS and MotionBERT-lite is not
reported anywhere found; any millisecond figure for them is a
parameter/MAC-count estimate, UNVERIFIED. No paper found compares an
IMM or CA Kalman with a learned forecaster on noisy detector joints
under 300 ms; "a learned predictor will not beat the Kalman there" is
a judgement, not a citation.

Conclusion (plan addendum A2): the measured losses are filter lag and
jitter, fixed cheaply by M5's tangent-space Kalman (now D-038, the
default smoother); learned forecasters help only for long occlusions
and infill, and are blocked until the D-017 gate is fitted. Mesh
models (family C) are ruled out for now. No implementation work
started on A, B or C; item 2 of the shortlist is a candidate M9 the
author decides on after seeing M8a and M8b.

## 2026-09-25 Smooth-and-accurate round: results

M1 to M8a of the 2026-09-25 plan
(/home/luo/.claude/plans/virtual-wiggling-globe.md). Conditions and a
dataset citation accompany every number; full reasoning is in
V3_DECISIONS.md D-023 to D-039.

Oracle and clean-window bench (M2, D-024/D-026; rtmpose-m, the four
clean windows of configs/clean_windows.json; oracle = offline
zero-phase filter of the same RTMPose keypoints, self-consistency not
external truth): the causal baseline_hold/S2 paths leave second-diff
RMS 0.60/0.51 deg/frame^2 against oracle 0.18 and raw 4.92 on
right_elbow r_elbow_y, lagging 3/5 frames
(dataset/phase5_clean_baseline.txt).

Pose-model sweep and re-pin (M3 D-028, M4 recap, author decision
D-034; pinned bag recording_20260224_083945 plus the four clean
windows, RTX 3080): M3 picked rtmpose-x + yolox-m (d2 ratio 0.937 vs
rtmpose-m, dataset/phase5_pose_sweep.txt), but that ranking was
confounded by fixed step caps and cold start; the M4 recap on each
variant's own D-033 manifest (D-032 derived caps, D-031 warm start)
flips the SAME unchanged rule to rtmpose-l (d2 ratio 0.909, mean bone
p95 0.061, total p99 12.44 ms, dataset/phase5_pose_sweep_recapped.txt).
D-034 re-pins the default to rtmpose-l 384x288 + YOLOX-tiny 416x416:
S2 passes teleport/honesty 6/6, worst step 3.34/3.23 deg
(none/quat_one_euro), latency p99 12.14/12.59 ms vs the 33.3 ms budget
(dataset/phase5_s_grade__rtmpose-l*.txt,
dataset/phase5_realtime__rtmpose-l*.txt).

D-033 teleport-budget rule (M4, budgets from real motion instead of
the slow pinned recording): budgets rise 1.4-6.4x (e.g. r_swing_z
0.78 -> 5.00 deg/frame) except l_twist, which gets stricter (4.81 ->
3.49); a 1.5x-budget step injected on r_swing_z or r_elbow_y still
FAILS the gate, and the un-injected S2 default PASSES at worst step
2.79 deg (dataset/phase5_teleport_rule_check.txt); the derived caps
(D-032) bind on 2-24 percent of clean-window frames per arm track,
down from 11-36 percent under the old fixed caps (same file, section
4).

Smoother comparison and the default (M5, D-029 finalised, D-038;
rtmpose-l, pinned bag for the gates plus four clean windows for the
ranking, 44 window-angle pairs, elbow_z excluded): none rms0 3.925
deg / d2-vs-oracle ratio 3.142 (fails the d2/o <= 1.5 feasibility
bound); quat_one_euro 4.188 / 1.456, mean |lag| 4.91 frames;
tangent_kf 4.171 / 1.467, mean |lag| 4.48 frames, lowest rmsL 2.387
deg and lowest causal second-diff RMS 0.631 deg/frame^2
(dataset/phase5_smoother_compare__rtmpose-l.txt). tangent_kf wins the
rule stated before the run by a 0.017 deg rms0 margin over
quat_one_euro (D-029 annotation) and becomes the default smoother
(configs/default.json); S-type gates PASS 6/6 teleport and honesty,
worst S2 step 3.52 deg, total p99 12.65 ms
(dataset/phase5_s_grade__rtmpose-l__tangent_kf.txt,
dataset/phase5_realtime__rtmpose-l__tangent_kf.txt).

Wrist-to-object evaluation (M7, D-035-D-037; R4-R7, holding frames
only, anchor (a) = measured shoulder, re-run with S2+tangent_kf under
D-038 review item 3): |v_rec - v_real| median 0.8-3.4 cm and p95 up
to 15.3 cm across every recording, hand, strategy and smoother; the
causal strategies add at most 0.7 cm to the oracle's median
(dataset/phase5_wrist_object__rtmpose-l.txt). Anchor (b) (hip-based)
is unusable: p95 8.6-38 cm, median 10-30 cm on R5/R7 left, consistent
with (not established as caused by) a corrupted right-hip depth on
R5's left run, where the root tilts about 22 deg (same file; D-037
review item 1).

Side-by-side films (M8a, D-039; eight films, rtmpose-l + S2 +
tangent_kf, whole R4-R7 recordings plus the four clean windows): the
reconstructed rig's largest per-frame step at every reacquisition
stays within its D-033 budget on all eight films (0.58-0.80x); frames
with any group over budget away from reacquisition: R4 10, R5 46, R6b
1, R7 0, clean windows 0 (dataset/phase5_side_by_side_summary.txt,
dataset/phase5_side_by_side_manifest.json). ESTIMATED also flags
cap-bound frames with full landmark visibility (e.g. r5 frame 2062),
so amber is not synonymous with occlusion in these films (D-039).

## Promotion candidate

Empty by design. Nothing moves to the thesis unless the user explicitly
decides; if that ever happens, this section states exactly what would
move and why.

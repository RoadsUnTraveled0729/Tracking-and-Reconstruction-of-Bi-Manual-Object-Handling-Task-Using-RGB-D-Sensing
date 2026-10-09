# v3: real-time occlusion exploration (RTMPose)

## Purpose

v1 and v2 freeze a joint when its landmarks vanish: honest, but the
arm stops moving. v3 asks one question: what is the most ROBUST way to
keep estimating through an occlusion in real time -- explicitly not
hold-last and not the laboratory's Bayesian recovery. To ask it
fairly, v3 also modernizes the detector (currently RTMPose-l, COCO-17,
ONNX Runtime on GPU) while keeping the SAME kinematic model semantics as
the thesis, so V1-vs-V3 comparisons stay meaningful. It is an
exploration track: nothing here reaches the thesis without an
explicit user decision.

## Status

EXPLORATORY; development is paused. Phases 0-3 have recorded outputs,
and Phase 4 implemented S2 quaternion prediction
([V3_FINDINGS.md](V3_FINDINGS.md)). The September smooth-and-accurate
round completed M1-M8a, including pose sweeps, two smoothers,
wrist-to-object evaluation and side-by-side films
([SESSION_REVIEW.md](SESSION_REVIEW.md)). Current defaults are RTMPose-l
with YOLOX-tiny and tangent_kf smoothing
([config](configs/default.json), D-034, D-038 and D-029). Gate threshold
fitting remains open under D-017; hardware and broader recording
validation remain limited. Results below are pinned to their stated
models and conditions, including older RTMPose-m runs. Nothing in this
track is validated for thesis use or promoted to the frozen reference.

## Design decisions

Full structured log with statuses in [V3_DECISIONS.md](V3_DECISIONS.md);
the shaping five:

- D-003: metrics and the ranking rule were frozen before any strategy
  existed, so the bake-off cannot be gamed.
- D-005: unit quaternions internally, v1 angle definitions only at
  the interface via the verbatim vendored v1 trig; oracle identity to
  1e-9 deg is enforced by tests.
- D-007: isolation is Unity-level and code-level, not git-level: own
  scene, own scripts, own shared-memory names, copy-only reuse of v1.
- D-008: onnxruntime-gpu pinned to 1.22.0 (CUDA 12 build; this
  machine's driver is CUDA 12.9, ORT 1.28 needs CUDA 13), person
  detection amortized to 1-in-15 frames. D-028 (M3 pose sweep)
  replaced the RTMPose-m + YOLOX-tiny default with RTMPose-x 384x288
  + YOLOX-m; D-034 (author decision 2026-09-25) reversed that and
  pins RTMPose-l 384x288 + YOLOX-tiny, the winner of the same rule
  after M4 (UNCERTAIN, see Results).
- D-012: re-detect triggers are edge-triggered, not level-triggered;
  the level version degenerated to detect-every-frame on the pinned
  recording because the head touches the top image edge throughout.

M4 (smoother (i) and the teleport rule), one line each:

- D-027: smoothers may keep tangent-space or scalar state; every S2
  track still outputs a unit quaternion on its v1 manifold.
- D-029 (provisional until M5): quat_one_euro parameters per track
  kind from a fixed rule on the clean windows; the default stays
  smoother "none" until the M5 comparison. Re-swept on RTMPose-l for
  D-034 (beta range extended to 128; no winner on a grid edge).
- D-030: bone-length projection along the camera ray exists and is
  OFF by default (the oracle is computed from unprojected landmarks).
- D-031: warm start; a track's first measurement is taken directly.
- D-032: S2 step caps derived per track and side from the active
  manifest (0.8 x the smallest budget, the D-021 rule).
- D-033: teleport budgets = 1.5 x p99.9 of the offline oracle's steps
  over the pinned bag plus the four clean windows; twist steps count
  only where the oracle elbow bend is >= 30 deg.

M5 (smoother (ii) and the default smoother), one line each:

- D-038: smoother (ii) tangent_kf, a causal constant-velocity Kalman
  filter per S2 track in the tangent (log-map) space, re-linearised
  every frame, scalar for twist, Ry*Rz re-projection for swing and
  elbow, velocity damped by S2's lambda 0.8 while unmeasured, zero
  declared lag; q_w and r_v per kind from a grid under the D-029 rule,
  q_r fixed at 1 deg^2/s as a normalisation (shown to be one).
- D-029 finalised (annotation): the default smoother is chosen by a
  rule stated before it was applied (lowest 13-angle mean rms0 among
  gate-passing smoothers with mean d2/o <= 1.5); it picks tangent_kf,
  now the default in configs/default.json.

## Results (so far)

Conditions per result; evidence in [V3_FINDINGS.md](V3_FINDINGS.md)
and v3/dataset/.

- Oracle identity: the quaternion path reproduces the vendored v1
  solvers to under 1e-9 deg on 10000 random poses and every singular
  branch (test_oracle_identity.py, runs in the default suite).
- RTMPose-m raw forward, RTX 3080, 200 runs after warmup: p50
  1.58 ms / p99 2.00 ms; CPU fallback p50 6.05 / p99 11.50 ms.
- Full detector stage on the pinned bag (897 frames, non-realtime
  playback, 60 warmup frames excluded): person found 897/897,
  detection ran on 8.1 percent of frames, p50 2.72 / p99 8.96 ms
  (dataset/phase1_detector_smoke.txt).
- Detector sweep, det_freq {5,15,30} x YOLOX {tiny,m} on the same
  bag: identical coverage and pose scores everywhere; tiny stage p99
  8.5 ms vs m 17.5 ms; verdict keep tiny + det_freq 15 for clean
  scenes, revisit under occlusion (D-016,
  dataset/phase3_detector_sweep.txt).
- V3 extraction of the pinned bag: 898/898 frames, zero depth holes
  and zero abstentions across all 7184 landmark samples -- RTMPose
  never declines to answer, which is exactly why the gate must be
  recalibrated before any occlusion claim
  (dataset/phase3_extraction.txt).
- V3-vs-v1 per-angle offsets measured (both raw extractions through
  the identical vendored solver): root_y -7.6 deg, swing_y about
  +-9 deg, twist spread ~6.5 deg cstd -- subtract before any
  comparison; elbow_z exactly zero on both sides (D-018,
  dataset/phase3_v1_offset_table.txt).
- BASELINE graded on six S-type scenarios (derived teleport budgets,
  honesty perfect): fails the teleport hard gate on elbow_long and
  root_ref via the reacquisition snap -- the measured bar Phase 4
  strategies must clear (D-020, dataset/phase3_baseline_grade.txt).
- S2 (quaternion prediction, damped decay, per-track step caps)
  BEATS that bar: all hard gates pass on all six scenarios, worst
  step halved (1.90 vs 3.81 deg), elbow_long reacquisition error down
  38 percent; drift costs it on near-static holds (D-021/D-022,
  dataset/phase4_s2_vs_baseline.txt).
- END-TO-END realtime PASS on the same video: paced playback through
  detector -> depth -> filter -> S2 -> PSV3, 883/883 frames at 28.7
  fps sustained, total p99 10.65 ms vs the 33.3 ms budget
  (dataset/phase4_realtime_e2e.txt).
- Clean-window bench (four occlusion-free windows of the defence
  films, D-025; rtmpose-m; reference = offline zero-phase oracle,
  D-024, which is the same keypoints smoothed with look-ahead, not
  external truth): on right_elbow r_elbow_y the causal
  baseline_hold / S2 paths leave second-difference RMS 0.60 / 0.51
  deg/frame^2 against 0.18 for the oracle and 4.92 raw, lagging it by
  3 / 5 frames. S2 is smoother everywhere but lags up to the 10-frame
  search bound where motion exceeds its step caps or the window starts
  near the stream start (180042); baseline_hold ranks ahead on the
  clean mean rank. The D-018 V3-vs-v1 offsets do not transfer to these
  recordings (r_swing_y residual about -12 to -13 deg after
  subtraction) (D-026, dataset/phase5_clean_baseline.txt).
- Pose-model sweep (M3, D-028, UNCERTAIN; dataset/phase5_pose_sweep.txt):
  six variants (RTMPose-m / -l / -x body7, RTMW-dw-l-m wholebody sliced
  to 17, YOLOX-tiny or -m) on the pinned bag and the four clean
  windows, RTX 3080, det_freq 15. Rule fixed before the numbers:
  S2 must pass every D-003 gate on its own S-type manifest, then lower
  raw-angle second-difference RMS (geometric-mean ratio vs RTMPose-m
  over 44 window-angle pairs) and no worse bone-length p95. Winner
  RTMPose-x + YOLOX-m: ratio 0.937, mean oracle bone p95 0.064 vs
  0.080 (right upper arm 0.113 vs 0.140), pinned-bag keypoint score
  0.885 vs 0.751; S2 passes all gates on the regenerated manifest
  (dataset/phase5_s_grade__rtmpose-x_yolox-m.txt). Costs: realtime
  total p99 24.08 ms vs 9.68 ms (budget 33.3,
  dataset/phase5_realtime__rtmpose-x_yolox-m.txt); RMS against its own
  oracle is not lower (S2 6.56 vs 6.47 deg mean). RTMPose-l (with
  either detector) was as smooth or smoother, faster and more
  bone-consistent but failed the S2 teleport gate on 2/6 scenarios;
  the S2 step caps were tuned to the RTMPose-m budgets (D-021), so
  that verdict is confounded until the caps are re-derived (M4).
  RTMW-dw-l-m was rougher than RTMPose-m. All solver-side numbers are
  self-consistency, not external truth. New V3-vs-v1 offsets for the
  winner: dataset/phase5_v1_offset_table.txt.
- Teleport rule re-derived (M4, D-033, UNCERTAIN;
  dataset/phase5_teleport_rule_check.txt; rtmpose-x_yolox-m, pinned
  bag post-warmup plus four clean windows, 1628 oracle steps): budgets
  rise 1.4-6.4 x (e.g. r_swing_z 0.78 -> 5.00, r_elbow_y 1.19 -> 5.10
  deg/frame) except l_twist (4.81 -> 3.49), which is now stricter.
  The rule still catches real jumps: a single injected step of 1.5 x
  budget on r_swing_z or r_elbow_y after the pose_loss window FAILS the
  gate, and un-injected S2 PASSES (worst step 2.79 deg). The 30 deg
  bend threshold for twist was chosen after seeing the data.
- Cap activity (D-032, same file, 795 clean-window frames): the
  derived caps bind on 2-24 percent of frames per arm track (root 36
  percent), down from 11-36 percent (root 59 percent) under the fixed
  D-021 caps.
- Smoother (i) trade-off (D-029, UNCERTAIN;
  dataset/phase5_smoother_grid__rtmpose-x_yolox-m.txt and
  phase5_smoother_i__rtmpose-x_yolox-m.txt; rtmpose-x_yolox-m, four
  clean windows, D-033 manifest, warm start): quat_one_euro lowers the
  jitter ratio d2/o (causal vs oracle second-difference RMS) by 23-65
  percent per track kind (elbow 4.14 -> 1.45, swing 3.06 -> 1.41) and
  costs 0.01-0.45 deg of RMS vs the oracle at lag 0 and 0.2-1.8 frames
  of lag. Neither dominates; the default stays "none" until M5.
- S-type hard gates after M4 (dataset/phase5_s_grade__rtmpose-x_yolox-m.txt
  and __quat_one_euro.txt; six scenarios, D-033 manifest): S2 passes
  teleport and honesty on 6/6 with both smoothers; baseline_hold fails
  teleport on 6/6 (reference behaviour, not gated). Latency on the
  pinned bag, paced: total p99 24.08 ms (none) and 24.40 ms
  (quat_one_euro) vs the 33.3 ms budget
  (dataset/phase5_realtime__rtmpose-x_yolox-m*.txt). The pre-D-033
  grade is kept as phase5_s_grade__rtmpose-x_yolox-m__pre_d033.txt.
- Pose sweep recapped under M4 (dataset/phase5_pose_sweep_recapped.txt;
  same six variants, each on its own D-033 manifest with derived caps
  and warm start, both smoothers): every variant now passes the S2
  gates, so the unchanged D-028 rule selects RTMPose-l (raw d2 ratio
  0.909, mean bone p95 0.061, total p99 12.44 ms) instead of the pinned
  RTMPose-x + YOLOX-m, for both smoothers. This is consistent with
  the cap-vs-budget confound D-028 named for the M3 gate failures; the
  three M4 changes (budgets, caps, warm start) were not isolated.
  Latency for the non-pinned variants is the M3 measurement (S2
  without smoother).
- Re-pin to RTMPose-l (D-034, UNCERTAIN; author decision reversing
  D-028; pinned bag plus four clean windows, RTX 3080, own D-033
  manifest configs/scenarios_20260224__rtmpose-l__oracle_union.json):
  smoother grid re-run with beta up to 128
  (dataset/phase5_smoother_grid__rtmpose-l.txt), winners root 2 / 8,
  swing 1 / 8, twist 4 / 8, elbow 2 / 2 (min_cutoff Hz / beta);
  quat_one_euro lowers d2/o by 34-66 percent per kind and costs
  0.07-0.46 deg rms0 and 0.6-2.4 frames of lag
  (dataset/phase5_smoother_i__rtmpose-l.txt). S2 passes teleport and
  honesty on 6/6 with both smoothers, worst step 3.34 / 3.23 deg;
  baseline_hold fails teleport on 1/6
  (dataset/phase5_s_grade__rtmpose-l*.txt). A 1.5 x budget injection
  still FAILS and un-injected S2 PASSES
  (dataset/phase5_teleport_rule_check__rtmpose-l.txt). Latency total
  p99 12.14 ms (none) and 12.59 ms (quat_one_euro), single runs with
  the GPU idle (dataset/phase5_realtime__rtmpose-l*.txt). V3-vs-v1
  offsets for RTMPose-l: dataset/phase5_v1_offset_table__rtmpose-l.txt
  (root_y -7.06, r_swing_y +8.18 with cstd 8.44 deg).
- Smoother (ii) and the default (D-038, D-029 finalised; UNCERTAIN;
  rtmpose-l, pinned bag for the gates plus the four clean windows of
  configs/clean_windows.json for the ranking, D-033 manifest, D-032
  caps, D-031 warm start; accuracy is agreement with the offline
  zero-phase oracle, self-consistency and not external truth, D-024).
  Grid (dataset/phase5_smoother_ii_grid__rtmpose-l.txt): winners root
  q_w 1000 / r_v 1, swing 100 / 0.3, twist 1000 / 0.3, elbow 100 / 1
  (deg^2/s^3, deg^2), none on a grid edge. Clean-window 13-angle means
  (dataset/phase5_smoother_compare__rtmpose-l.txt; elbow_z excluded as
  identically zero; 44 window-angle pairs):

  | S2 smoother | rms0 deg | mean abs lag, frames | rmsL deg | d2 causal deg/frame^2 | d2/o | S-type gates | total p99 ms |
  |---|---|---|---|---|---|---|---|
  | none | 3.925 | 3.77 | 2.499 | 1.092 | 3.142 | PASS | 12.14 |
  | quat_one_euro | 4.188 | 4.91 | 2.467 | 0.633 | 1.456 | PASS | 12.59 |
  | tangent_kf | 4.171 | 4.48 | 2.387 | 0.631 | 1.467 | PASS | 12.65 |

  The rule excludes "none" (d2/o 3.14 > 1.5) and picks tangent_kf by
  0.017 deg of rms0 over quat_one_euro, a margin a different window
  set could reverse; tangent_kf also lags 0.43 frames less and has the
  lowest rmsL and d2 causal. Against "none" the smoothing costs 0.25
  deg of rms0 and 0.7 frames of lag for 42 percent less
  second-difference RMS. Per kind the Kalman matches quat_one_euro's
  rms0 (within 0.05 deg) and lags less (root 3.83 vs 4.33, elbow 4.88
  vs 5.88 frames); under a lag-weighted score (rms0 + 0.5 deg per
  frame of lag, informational) it wins every kind, so its advantage
  is lag, not lag-0 accuracy. About 3.8 frames of the lag are upstream
  of the smoother (smoother "none" already shows them: the landmark
  Hampel plus One-Euro, D-015). On right_elbow r_elbow_y the second
  difference is 0.161 deg/frame^2 at lag 4 frames (live pipeline
  0.47, eval/pipeline_smoothness/metrics.csv). S-type gates
  (dataset/phase5_s_grade__rtmpose-l__tangent_kf.txt): teleport 0/6
  and honesty 0/6 failures, worst S2 step 3.52 deg (quat_one_euro
  3.23). Latency (dataset/phase5_realtime__rtmpose-l__tangent_kf.txt,
  single paced run, GPU idle by nvidia-smi, RTX 3080): strategy p99
  0.76 ms, total p99 12.65 ms vs the 33.3 ms budget. Synthetic tests
  (tests/test_smoother_kalman.py): ramp lag 0.04 frames vs
  quat_one_euro 0.61-1.57 frames; but a 20 deg step overshoots by
  2.4-3.0 deg and settles to 0.1 deg in 9-23 frames (quat_one_euro 3-8
  frames, no overshoot).
- Negative result: the planned depth-front weak label is invalid for
  wrists on this reaching task (right wrist flagged on 889/898
  frames; flagged samples score HIGHER than clean ones); gate
  thresholds remain unfitted (D-017,
  dataset/phase3_gate_weak_labels.txt).
- Failure found and fixed: level-triggered border contact caused
  detect-every-frame (D-012). Not yet validated: the gate thresholds
  (manual labeling or prediction-relative depth needed, D-017),
  reacquisition behavior per det_freq and detector variant under
  occlusion, automatic occlusion detection and broader occlusion
  robustness.

## Limitations

- S2's S-type comparisons use masked replay on the pinned bag; they
  do not establish reliable recovery through automatically detected
  occlusions ([grade](dataset/phase5_s_grade__rtmpose-l__tangent_kf.txt),
  [D-017](V3_DECISIONS.md#d-017)).
- The COCO wrist is not the BlazePose wrist. Model-specific V1-vs-V3
  offsets have been measured, but the RTMPose-m offsets do not transfer
  to the clean windows. Angle comparisons must state their model,
  offset table and recording conditions
  ([D-018](V3_DECISIONS.md#d-018),
  [clean-window bench](dataset/phase5_clean_baseline.txt)).
- RTMPose scores are localization confidence, not visibility;
  high confidence does not establish that a joint is visible. Gate
  threshold fitting remains open after the rejected depth-front weak
  label ([D-017](V3_DECISIONS.md#d-017)).
- Needs conda env v3rt and the CUDA-12 library path for GPU runs.
- The default smoother (tangent_kf, D-038) overshoots sharp stops: a
  20 deg synthetic step overshoots by 2.4-3.0 deg before settling; its
  margin over quat_one_euro on lag-0 RMS is 0.017 deg on four clean
  windows. Declared smoothing lag (lag_frames) is off because PSV3 has
  no lag field.

## How to run and reproduce

Run from the repository root.

    # default test suite: numpy + pytest only, no onnxruntime needed
    (cd v3 && /home/luo/anaconda3/bin/python -m pytest)

    # full suite including detector tests (env v3rt, CUDA-12 libs)
    NV=/home/luo/anaconda3/lib/python3.11/site-packages/nvidia
    (cd v3 && LD_LIBRARY_PATH=$NV/cudnn/lib:$NV/cublas/lib:$NV/cuda_runtime/lib:$NV/cufft/lib:$NV/curand/lib \
      /home/luo/anaconda3/envs/v3rt/bin/python -m pytest)

    # model variants (configs/model_variants.json, D-023): every onnx
    # is hash-checked before a run; default = config model.variant
    NVLIB=$NV/cudnn/lib:$NV/cublas/lib:$NV/cuda_runtime/lib:$NV/cufft/lib:$NV/curand/lib
    LD_LIBRARY_PATH=$NVLIB /home/luo/anaconda3/envs/v3rt/bin/python \
      v3/tools/extract_bag_to_csv.py --bag BAG --variant rtmpose-m
    #   -> v3/output/extraction_<bagstem>__<variant>.csv + .meta.json
    #      (meta records variant, backend and the onnx sha256 values)
    LD_LIBRARY_PATH=$NVLIB /home/luo/anaconda3/envs/v3rt/bin/python \
      v3/bench/sweep_detector.py --pose-variants rtmpose-m,rtmpose-m_yolox-m
    #   det_freq {5,15,30} x variants; the default pair reproduces the
    #   D-016 YOLOX tiny-vs-m sweep

    # clean-window baselines (configs/clean_windows.json, D-025)
    for BAG in $(/home/luo/anaconda3/bin/python -c "import json; \
        [print(w['bag']) for w in json.load(open( \
        'v3/configs/clean_windows.json'))['windows']]"); do
      LD_LIBRARY_PATH=$NVLIB /home/luo/anaconda3/envs/v3rt/bin/python \
        v3/tools/extract_bag_to_csv.py --bag $BAG --variant rtmpose-m \
        --out-csv v3/output/clean/extraction_$(basename $BAG .bag)__rtmpose-m.csv
    done

    # clean-window bench (D-024 oracle, D-026 clean metrics): replays
    # each clean extraction through the causal path and the offline
    # zero-phase oracle; rtmpose-m CSVs from the loop above; no GPU
    /home/luo/anaconda3/bin/python v3/bench/grade_clean.py \
      --strategies baseline_hold,s2_quat_prediction --smoothers none \
      --windows all --variant rtmpose-m \
      --manifest v3/configs/scenarios_20260224.json \
      --out-txt v3/dataset/phase5_clean_baseline.txt
    #   -> table on stdout, pinned text v3/dataset/phase5_clean_baseline.txt
    #      (--out-txt), per-angle CSV v3/output/clean/clean_grade__<variant>.csv

    # pose-model sweep (M3, D-028): detector runs per variant x bag
    # (pinned + clean windows), then extraction, realtime, S-type grade
    # and clean grade per variant, then the table and the selection
    VS=rtmpose-m,rtmpose-x,rtmpose-x_yolox-m,rtmpose-l,rtmpose-l_yolox-m,rtmw-dw-l-m
    LD_LIBRARY_PATH=$NVLIB /home/luo/anaconda3/envs/v3rt/bin/python \
      v3/bench/sweep_pose.py run --variants $VS
    #   -> v3/output/pose_sweep/<variant>__<bagstem>.npz
    # per variant V (not rtmpose-m, whose manifest is
    # configs/scenarios_20260224.json): extract the pinned bag and the
    # clean bags with --variant V (commands above), then
    LD_LIBRARY_PATH=$NVLIB /home/luo/anaconda3/envs/v3rt/bin/python \
      v3/replay/realtime.py --config CFG_V --no-shm \
      > v3/output/pose_sweep/realtime__V.txt   # CFG_V = default.json
    #   with apply_variant(cfg, V) overlaid (detector/factory.py)
    /home/luo/anaconda3/bin/python v3/bench/make_scenarios.py \
      --base-csv v3/output/extraction_recording_20260224_083945__V.csv \
      --manifest v3/configs/scenarios_20260224.json \
      --out-manifest v3/output/pose_sweep/scenarios__V.json \
      --out-dir v3/output/pose_sweep/scenarios__V
    /home/luo/anaconda3/bin/python v3/bench/grade.py \
      --manifest v3/output/pose_sweep/scenarios__V.json \
      --strategies baseline_hold,s2_quat_prediction \
      --realtime-txt v3/output/pose_sweep/realtime__V.txt \
      > v3/output/pose_sweep/s_grade__V.txt
    /home/luo/anaconda3/bin/python v3/bench/grade_clean.py --variant V \
      --manifest v3/output/pose_sweep/scenarios__V.json \
      --out-txt v3/output/pose_sweep/clean__V.txt
    /home/luo/anaconda3/bin/python v3/bench/sweep_pose.py table \
      --variants $VS --out-txt v3/dataset/phase5_pose_sweep.txt

    # M3 pin (D-028, now history): S-type grade on
    # configs/scenarios_20260224__rtmpose-x_yolox-m.json; since D-034
    # the default manifest is rtmpose-l's, so pass it explicitly
    /home/luo/anaconda3/bin/python v3/bench/grade.py \
      --manifest v3/configs/scenarios_20260224__rtmpose-x_yolox-m.json \
      --strategies baseline_hold,s2_quat_prediction \
      --realtime-txt v3/dataset/phase5_realtime__rtmpose-x_yolox-m.txt
    /home/luo/anaconda3/bin/python v3/bench/grade_clean.py \
      --variant rtmpose-x_yolox-m \
      --manifest v3/configs/scenarios_20260224__rtmpose-x_yolox-m.json \
      --strategies baseline_hold,s2_quat_prediction
    #   -> v3/dataset/phase5_clean__rtmpose-x_yolox-m.txt

    # NOTE (D-034): the M4 commands below reproduce the rtmpose-x_yolox-m
    # pins only with the pre-D-034 config (model block, scenario_manifest
    # and smoother_params of D-028 / D-029), e.g. --config with
    # `git show 2b718aa:v3/configs/default.json` saved to a file;
    # sweep_smoother.py always reads configs/default.json
    # M4 teleport rule (D-033): regenerate the oracle_union manifests
    # (per variant V; rtmpose-m uses the un-suffixed base CSV and the
    # pinned variant writes configs/scenarios_20260224__V__oracle_union.json)
    /home/luo/anaconda3/bin/python v3/bench/make_scenarios.py \
      --base-csv v3/output/extraction_recording_20260224_083945__V.csv \
      --manifest v3/configs/scenarios_20260224.json \
      --out-manifest v3/output/pose_sweep/scenarios__V__oracle_union.json \
      --out-dir v3/output/pose_sweep/scen_ou__V \
      --budget-source oracle_union --variant V
    # budgets D-003 vs D-033, caps, injection check, cap activity
    /home/luo/anaconda3/bin/python v3/bench/teleport_rule_check.py \
      --out-txt v3/dataset/phase5_teleport_rule_check.txt

    # M4 smoother (i) (D-029): grid on the clean windows, then the
    # clean bench and S-type grade with both smoothers
    /home/luo/anaconda3/bin/python v3/bench/sweep_smoother.py grid \
      --min-cutoffs 0.5,1,2,4,8,16,32 --betas 0,0.5,2,8,32 \
      --out-txt v3/dataset/phase5_smoother_grid__rtmpose-x_yolox-m.txt
    /home/luo/anaconda3/bin/python v3/bench/grade_clean.py \
      --strategies s2_quat_prediction --smoothers none,quat_one_euro \
      --out-txt v3/dataset/phase5_smoother_i__rtmpose-x_yolox-m.txt \
      --out-csv v3/output/recap/smoother_i.csv
    #   (--out-csv keeps the M3 CSVs in v3/output/clean untouched)
    S2=strategy.s2_quat_prediction
    /home/luo/anaconda3/bin/python v3/bench/grade.py \
      --strategies s2_quat_prediction --set "$S2.smoother=\"quat_one_euro\"" \
      --realtime-txt v3/dataset/phase5_realtime__rtmpose-x_yolox-m__quat_one_euro.txt
    #   (the realtime text comes from replay/realtime.py with the
    #   smoother set to quat_one_euro in a copy of default.json)

    # M4 pose-sweep recap: per variant V, grade.py with --manifest the
    # V oracle_union manifest and --set "$S2.smoother=..." into
    # v3/output/recap/s_grade__V[__quat_one_euro].txt, grade_clean.py
    # --variant V --manifest ... --smoothers none,quat_one_euro
    # --out-csv v3/output/recap/clean_grade__V.csv, then (from v3/)
    /home/luo/anaconda3/bin/python bench/sweep_pose.py table \
      --variants $VS --smoothers none,quat_one_euro \
      --csv-dir output/recap --grade-dir output/recap \
      --realtime-dir output/pose_sweep \
      --realtime-override rtmpose-x_yolox-m:quat_one_euro=dataset/phase5_realtime__rtmpose-x_yolox-m__quat_one_euro.txt \
      --m3-table dataset/phase5_pose_sweep.txt \
      --out-txt dataset/phase5_pose_sweep_recapped.txt

    # D-034 re-pin (rtmpose-l, default.json): tracked manifest, smoother
    # grid, clean bench, S-type grades, teleport rule, latency, offsets
    /home/luo/anaconda3/bin/python v3/bench/make_scenarios.py \
      --base-csv v3/output/extraction_recording_20260224_083945__rtmpose-l.csv \
      --manifest v3/configs/scenarios_20260224.json \
      --out-manifest v3/configs/scenarios_20260224__rtmpose-l__oracle_union.json \
      --out-dir v3/output/pose_sweep/scen_ou__rtmpose-l \
      --budget-source oracle_union --variant rtmpose-l
    /home/luo/anaconda3/bin/python v3/bench/sweep_smoother.py grid \
      --min-cutoffs 0.5,1,2,4,8,16,32 --betas 0,0.5,2,8,32,64,128 \
      --work v3/output/smoother_sweep_d034_rtmpose-l \
      --out-txt v3/dataset/phase5_smoother_grid__rtmpose-l.txt
    /home/luo/anaconda3/bin/python v3/bench/grade_clean.py \
      --strategies s2_quat_prediction --smoothers none,quat_one_euro \
      --out-txt v3/dataset/phase5_smoother_i__rtmpose-l.txt \
      --out-csv v3/output/recap/smoother_i__rtmpose-l.csv
    # latency: check nvidia-smi shows no other compute process first
    LD_LIBRARY_PATH=$NVLIB /home/luo/anaconda3/envs/v3rt/bin/python \
      v3/replay/realtime.py --config v3/configs/default.json --no-shm \
      > v3/dataset/phase5_realtime__rtmpose-l.txt
    #   (and with a default.json copy whose smoother is quat_one_euro
    #   -> phase5_realtime__rtmpose-l__quat_one_euro.txt; the pinned
    #   files carry a GPU-idle header line above the realtime output)
    /home/luo/anaconda3/bin/python v3/bench/grade.py \
      --strategies baseline_hold,s2_quat_prediction \
      --set "$S2.smoother=\"none\"" \
      --realtime-txt v3/dataset/phase5_realtime__rtmpose-l.txt \
      > v3/dataset/phase5_s_grade__rtmpose-l.txt
    /home/luo/anaconda3/bin/python v3/bench/grade.py \
      --strategies s2_quat_prediction \
      --set "$S2.smoother=\"quat_one_euro\"" \
      --realtime-txt v3/dataset/phase5_realtime__rtmpose-l__quat_one_euro.txt \
      > v3/dataset/phase5_s_grade__rtmpose-l__quat_one_euro.txt
    /home/luo/anaconda3/bin/python v3/bench/teleport_rule_check.py \
      --old-manifest v3/output/pose_sweep/scenarios__rtmpose-l.json \
      --out-txt v3/dataset/phase5_teleport_rule_check__rtmpose-l.txt
    /home/luo/anaconda3/bin/python v3/bench/v1_offset_table.py \
      --v3-csv v3/output/extraction_recording_20260224_083945__rtmpose-l.csv \
      > v3/dataset/phase5_v1_offset_table__rtmpose-l.txt

    # M5 smoother (ii) (D-038) and the default smoother (D-029
    # finalised). NOTE: default.json now selects tangent_kf, so the
    # D-034 commands above reproduce their "none" pins only with
    # --set "$S2.smoother=\"none\"" (grade.py) or a default.json copy
    # whose smoother is "none" (realtime.py).
    /home/luo/anaconda3/bin/python v3/bench/sweep_smoother.py grid \
      --smoother tangent_kf --fixed '{"q_r": 1.0}' --jobs 16 \
      --grid '{"q_w": [10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000, 300000, 1000000], "r_v": [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100]}' \
      --work v3/output/smoother_sweep_kf --out-txt GRID.txt
    #   pinned file = GRID.txt plus the same grid with --fixed q_r 10
    #   and 0 (sensitivity), in dataset/phase5_smoother_ii_grid__rtmpose-l.txt
    /home/luo/anaconda3/bin/python v3/bench/grade_clean.py \
      --strategies baseline_hold,s2_quat_prediction \
      --smoothers none,quat_one_euro,tangent_kf \
      --out-txt v3/dataset/phase5_smoother_compare__rtmpose-l.txt \
      --out-csv v3/output/m5/smoother_compare__rtmpose-l.csv
    # latency: nvidia-smi shows no other compute process first
    LD_LIBRARY_PATH=$NVLIB /home/luo/anaconda3/envs/v3rt/bin/python \
      v3/replay/realtime.py --config v3/configs/default.json --no-shm \
      > v3/dataset/phase5_realtime__rtmpose-l__tangent_kf.txt
    #   (pinned file: GPU-idle header lines above the output, onnxruntime
    #   node-assignment warnings removed)
    /home/luo/anaconda3/bin/python v3/bench/grade.py \
      --strategies s2_quat_prediction \
      --set "$S2.smoother=\"tangent_kf\"" \
      --realtime-txt v3/dataset/phase5_realtime__rtmpose-l__tangent_kf.txt \
      > v3/dataset/phase5_s_grade__rtmpose-l__tangent_kf.txt
    /home/luo/anaconda3/bin/python -m pytest v3/tests/test_smoother_kalman.py

    # Unity demo: synthetic swinging-arm through the real math core
    /home/luo/anaconda3/bin/python v3/tools/psv3_demo_writer.py
    # then open Unity/, scene V3Scene, press Play: right arm cycles
    # orange (measured) -> amber (estimated) -> red (lost)

Plan: [V3_PLAN.md](V3_PLAN.md). Working rules: [RULES.md](RULES.md).

## Wrist-to-object evaluation

Question: does the reconstructed arm put the wrist where the RGB-D
wrist is, relative to the object the hand holds? Author definitions
(2026-09-25): real vector = measured RGB-D wrist landmark minus the
ArUco object marker position, per frame while the hand holds the
object; reconstructed vector = forward-kinematics wrist from the 13
solved angles and calibrated bone lengths minus the same marker
position. Since the object position cancels, |v_rec - v_real| =
|FK wrist - measured wrist|.

Design:

- Object pose: the thesis's 45 mm-scaled ArUco CSVs and scene
  calibrations under eval/output/, transformed into the levelled desk
  world by bench/aruco_source.py; V3 frame i = ArUco row i, checked on
  every frame of R4-R7 (max |dt| 0.001 ms, tolerance half a frame)
  (D-035).
- Holding frames: the thesis geometry rule in bench/holding.py (hold
  radius 0.25 m, carried with the inspection envelope, forearm within
  30 percent of its median), which reproduces the thesis R4 episodes
  exactly from the MediaPipe-era inputs (D-036).
- FK: core/fk.py on the vendored v1 rotation code; anchor (a) = the
  measured shoulder, anchor (b) = the measured right hip plus a
  per-recording hip-to-shoulder offset in the root frame; bone lengths
  = oracle medians per recording (D-037). Closure on the oracle's own
  landmarks to 1e-6 m and a 10k-pose round trip through the solver
  are tests.

Results (dataset/phase5_wrist_object__rtmpose-l.txt; rtmpose-l
extraction of the canonical bags, whole recordings replayed causally,
D-033 manifest caps, D-029 smoother parameters; holding frames only;
cm). Cells are |v_rec - v_real| median / p95. "measured" gives the
median |wrist - box centre| and the grip-vector 3D std (std of
R_obj^T (wrist - centre) within each hold run, frame-weighted), which
is the depth-side floor: no reconstruction can be more constant than
the wrist it is compared with. "1euro" = smoother quat_one_euro,
"KF" = smoother tangent_kf (D-038, the configs/default.json default
since M5). Re-run 2026-09-25 with --smoothers none,quat_one_euro,
tangent_kf to add the KF column; the none and quat_one_euro columns
are unchanged from the pre-M5 pin (D-037 annotation, D-038 review
item 3).

| rec | hand | held | measured: dist med, grip std | oracle a | S2 none a | S2 1euro a | S2 KF a | oracle b | S2 none b | S2 1euro b | S2 none a: dist med, grip std |
|---|---|---|---|---|---|---|---|---|---|---|---|
| r4 | right | 596 | 15.0, 4.9 | 1.1 / 4.3 | 1.3 / 5.0 | 1.3 / 5.0 | 1.3 / 4.9 | 2.6 / 8.6 | 3.1 / 10.2 | 3.1 / 10.4 | 15.0, 5.0 |
| r4 | left | 298 | 13.0, 7.1 | 2.8 / 6.5 | 3.3 / 15.1 | 3.4 / 15.4 | 3.4 / 15.3 | 5.0 / 30.1 | 5.5 / 23.5 | 5.5 / 23.5 | 10.8, 10.2 |
| r5 | right | 506 | 15.1, 3.0 | 1.1 / 4.4 | 1.2 / 6.2 | 1.3 / 6.8 | 1.3 / 6.5 | 3.5 / 23.7 | 4.1 / 25.3 | 4.2 / 25.5 | 15.1, 4.8 |
| r5 | left | 561 | 14.9, 6.3 | 2.5 / 8.7 | 3.1 / 11.6 | 3.2 / 12.0 | 3.1 / 12.1 | 29.9 / 32.6 | 19.6 / 38.0 | 19.6 / 38.2 | 13.0, 6.6 |
| r6b | right | 681 | 10.8, 5.5 | 1.2 / 2.6 | 1.3 / 2.6 | 1.3 / 2.6 | 1.3 / 2.7 | 2.6 / 22.4 | 2.6 / 20.2 | 2.6 / 20.2 | 10.8, 5.8 |
| r7 | right | 728 | 15.6, 7.0 | 0.9 / 2.3 | 1.0 / 2.4 | 1.0 / 2.6 | 1.0 / 2.5 | 2.1 / 23.6 | 2.1 / 21.6 | 2.1 / 21.6 | 15.6, 6.8 |
| r7 | left | 219 | 14.3, 4.0 | 0.8 / 1.5 | 1.1 / 3.3 | 1.1 / 3.2 | 1.1 / 3.2 | 11.0 / 27.5 | 10.5 / 36.1 | 10.7 / 36.5 | 13.9, 4.7 |

What it means:

- With the measured shoulder as anchor (a), the reconstructed wrist
  sits 0.8-3.4 cm (median) from the measured wrist on held frames in
  every recording, hand, strategy and smoother. The oracle row is the
  zero-phase reference; the causal strategies add at most 0.7 cm
  to its median (-0.04 to +0.70 cm). tangent_kf (KF), the default
  smoother since D-038, falls in the same band and tracks 1euro
  closely (median within 0.06 cm and p95 within 0.4 cm at every
  recording and hand): the wrist-to-object evidence does not
  distinguish the two smoothers.
- S2 has heavier tails than its median suggests on two hands: R4 left
  p95 15.1 cm and R5 right 6.2 cm, against 7.0 and 4.3 cm for
  baseline_hold. The clean-window bench does not contain these
  held-object frames.
- Anchor (b) (hip-based) fails: p95 8.6-38 cm everywhere, median
  10-30 cm on R5 left and R7 left. On R5's left run the right-hip depth
  reads 29 cm nearer than its recording median while the left hip does
  not move, and the root tilts by about 22 deg; this is consistent
  with a corrupted hip depth, not an established cause.
- The measured wrist itself is not constant in the object frame
  (3.0-7.1 cm grip std), so FK(a)'s grip std (4.8-10.2 cm for S2 without smoothing) is
  bounded by the measurement, not only by the solver.

Thesis comparison (R4, CAVEAT: the thesis used MediaPipe landmarks,
BlazePose wrist joint versus the COCO wrist crease, D-018, and the
filtered object track): thesis |wrist - centre| median/p95 right
14.6/17.9, left 13.4/17.3 cm; V3 measured right 15.0/17.5, left
13.0/15.0 cm. Thesis stage-3 residual median right 10.2, left 2.6 cm;
V3 11.4 and 5.1 cm. V3 classifies more frames as held (right 596 vs
494, left 298 vs 158); the left excess lies in the span the thesis
excluded as wrist-occluded, because the V3 "clean" flag only checks
that depth was sampled (D-036 review item).

Not verified: whether the V3 held frames on R4 left 833-984 show a
visible wrist (needs a look at the frames); the anchor (b) root cause.

How to run (env v3rt; bags under Video/ are read-only; about 1 min of
GPU for the four extractions, 20 s for the bench):

    cd v3
    for s in recording_20260825_070152 recording_20260825_222315 \
             recording_20260831_065553 recording_20260909_000024; do
      python tools/extract_bag_to_csv.py --bag ../Video/$s.bag \
        --variant rtmpose-l \
        --out-csv output/objects/extraction_${s}__rtmpose-l.csv
    done
    python bench/grade_wrist_object.py --recordings r4,r5,r6b,r7 \
      --strategies baseline_hold,s2_quat_prediction \
      --smoothers none,quat_one_euro --variant rtmpose-l
    python -m pytest tests/test_aruco_source.py tests/test_holding.py \
      tests/test_fk.py tests/test_grade_wrist_object.py

## Side-by-side films (M8a)

Purpose: a per-recording video that lets the author judge, by eye, the
plan's two acceptance criteria (with no occlusion the reconstruction
looks almost the same as the real person; through an occlusion it
transitions smoothly, no jump) before the Unity-rendered version
(M8b) exists. Built by tools/side_by_side.py and tools/render_rig.py;
full design in D-039.

Panel contract: each film is 1536x576, two 768x576 panels of the SAME
bag frame side by side. Left panel: the bag colour frame with the
RTMPose pixel locations of the eight v1 landmarks (filled = depth
sampled, hollow = depth hole) and the eight-landmark skeleton drawn
thin. Right panel, dark background, same camera projection: the torso
is the hip-shoulder quadrilateral of the causally filtered landmarks
the strategy received (held at the last valid value while missing);
the upper arm and forearm are core/fk.py fk_arm from the 13 output
angles, anchored at that filtered shoulder, with per-recording median
bone lengths from the oracle (D-037); the ArUco object cube
(bench/aruco_source.py, 45 mm scale, 0.07 m) is drawn on R4-R7 when
the marker is detected; the measured (raw CSV) wrist is a faint grey
ring. Colours follow the D-013 vocabulary (white MEASURED, amber
ESTIMATED, red LOST; torso = root status, upper arm = swing, forearm
= the worse of twist and elbow), plus a status strip and a whole-film
status timeline with a cursor. The stack rendered is the default
config from frame 0 (S2 s2_quat_prediction, D-031 warm start, D-032
caps on the D-033 rtmpose-l manifest, smoother tangent_kf D-038, the
default since M5).

Films (v3/output/side_by_side/, gitignored; sha256 and byte counts
pinned in the manifest):

| Film | Source | Frames | Duration |
|---|---|---|---|
| r4 | recording_20260825_070152, whole recording | 1498 | 49.93 s |
| r5 | recording_20260825_222315, whole recording | 2098 | 69.93 s |
| r6b | recording_20260831_065553, whole recording | 899 | 29.97 s |
| r7 | recording_20260909_000024, whole recording | 1498 | 49.93 s |
| right_elbow | clean window 180-540 plus 1 s lead-in | 391 | 13.03 s |
| 180042 | clean window 3-109 plus 1 s lead-in | 110 | 3.67 s |
| right_arm_test | clean window 505-725 plus 1 s lead-in | 251 | 8.37 s |
| arms_outstretched | clean window 780-885 plus 1 s lead-in | 136 | 4.53 s |

Contact sheets (v3/dataset/phase5_side_by_side_<name>.png, tiles
768x288, at most eight tagged frames per film: clean, entering,
during, reacquiring) and the manifest
(v3/dataset/phase5_side_by_side_manifest.json: per film sha256, byte
count, probe, status fractions, bones, contact-sheet frame tags,
config and render-constants sha256) are pinned and committed; the
occlusion summary is v3/dataset/phase5_side_by_side_summary.txt.

Occlusion summary headline (largest per-frame angle step at each
reacquisition, as a fraction of its D-033 teleport budget; twist steps
at a causal elbow bend under 30 deg exempt, as in D-033):

| Recording | Largest reacquisition step | Frames over budget (any group) |
|---|---|---|
| r4 | 0.80x budget (L_twist, frame 978) | 10 |
| r5 | 0.78x budget (L_twist, frame 1484) | 46 |
| r6b | 0.58x budget (root, frame 828) | 1 |
| r7 | 0.75x budget (L_elbow, frame 1141) | 0 |
| clean windows (all four) | 0.65-0.77x budget | 0 |

Every reacquisition across all eight films stays within its D-033
budget (0.58-0.80x); the "over budget" frames occur away from
reacquisition, largest at r4 frame 1090 (l_twist 4.39x) and r5 frame
85 (l_twist 1.94x), both while that track is ESTIMATED.

Caveats (D-039):

- The right-panel rig is anchored on the causally filtered landmarks
  the live pipeline actually publishes (replay/realtime.py writes
  these into PSV3), not on D-037's raw measured-shoulder anchor: a raw
  anchor would mix a lag-free shoulder with lagged angles. This means
  the panel shows what the live system would draw, not the most
  accurate possible reconstruction.
- ESTIMATED also fires when S2's per-frame step cap binds
  (strategies/s2_quat_prediction.py: a capped frame is non-converged),
  not only when a landmark is missing, so amber can appear on a fully
  visible frame: e.g. r5 frame 2062 (every landmark depth-sampled,
  scores 0.54-0.80; root and the right arm amber) and r4's root track
  at frame 554 (all eight landmarks depth-sampled, scores 0.69-0.85).
  Why an Euler-angle step can exceed its budget while the underlying
  geodesic step stayed capped is not investigated.
- No 3D view: plan A4 asked for the camera view only; the extra 3D
  panel it also mentions was not built.
- --half-speed exists (input rate 15 fps re-timed to 30 fps output)
  but is untested: no half-speed film was rendered or viewed this
  round.

How to run (base anaconda python; pyrealsense2 needed for BagSource):

    cd v3
    /home/luo/anaconda3/bin/python tools/side_by_side.py --recording all
    /home/luo/anaconda3/bin/python tools/side_by_side.py --recording r4 --half-speed
    /home/luo/anaconda3/bin/python tools/side_by_side.py --recording all --summary-only

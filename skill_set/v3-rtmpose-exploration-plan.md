# Current exploration pointer (2026-10-08)

The original Phase 3 next-work list and 78-test snapshot below are
historical. V3 has implemented S2 prediction and completed the September
M1-M8a smooth-and-accurate round. Current defaults are RTMPose-l with
YOLOX-tiny and tangent_kf; development is paused. See
[v3/README.md](../v3/README.md), [config](../v3/configs/default.json) and
[SESSION_REVIEW.md](../v3/SESSION_REVIEW.md) for results, unresolved
D-017 gate fitting, verification limits and reproduction commands.

## Historical exploration plan
# V3 RTMPose exploration plan

The V3 exploration track (RTMPose-m/COCO-17 via rtmlib + ONNX Runtime; research question: most robust real-time occlusion handling, not hold-last, not Bayesian) is on master under `v3/` through commit 90d8d66 (2026-08-06). Isolation per D-007 is Unity-level and code-level, NOT git-level: no v1/v2 file is ever edited, reuse is copy-only (hash-checked vendored oracles), V3 has its own Unity scene `V3Scene.unity` + `Unity/Assets/Scripts/V3/` reading only `/dev/shm/v3_person` (PSV3, canonical writer `v3/replay/psv3.py`). Done as of 2026-08-06: frozen metrics + ranking (D-003), quaternion core with 1e-9 deg oracle identity, env `v3rt` (onnxruntime-gpu 1.22.0 CUDA-12 pin per D-008 + rtmlib + pytest), models pinned in `v3/models/`, detector with amortized detection (bag acceptance: 897/897 found, 8.1 pct det frames, stage p99 8.96 ms), READMEs, AGENTS.md.

Why: the user directed immediate start ("ignore the timing") and continuous autonomous work per v3-autonomy-decision-logging.md; every choice is in `v3/V3_DECISIONS.md` with statuses, handoff in `v3/SESSION_REVIEW.md`.

How to apply: next work is Phase 3 in `v3/SESSION_REVIEW.md` order:
replay runner, V3 bag extraction, det_freq sweep (closes D-008
UNCERTAIN), gate ROC to fill config nulls, baseline + 33-check port.
Paused as of 2026-09; resumes after the thesis phase closes. GPU runs
need env v3rt plus the five CUDA-12 lib dirs from
`configs/default.json` on LD_LIBRARY_PATH before python starts. Full
suite: pytest under v3rt (78 tests); default suite runs on base
python. Unity verification pending: demo writer + Play in V3Scene.
project-readme-rules.md and plain-text-output-style.md apply.

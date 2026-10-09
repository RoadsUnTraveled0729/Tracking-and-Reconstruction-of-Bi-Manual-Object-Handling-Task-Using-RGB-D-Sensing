Current layout verification: 2026-10-08
Sources: ../../workspace_support/migration/baseline.json;
../../knowledge/workspace_migration.md.
The complete thesis tree is now under ug_thesis_2026/, including Video/
and recordings/. The dated paths and inventories below describe their
recorded baseline; temporary root links preserve them during internal
validation. After the final outer rename, the canonical thesis path is
/home/luo/Desktop/AI_WorkSpace/ug_thesis_2026 and bimanual-tracking will
resolve to that subtree. External old-name symlink text stays unchanged.

Verified: 2026-10-06
Sources: git grep over tracked files at bc715ea plus the M5 working-tree edits; v3/configs/{default.json,clean_windows.json}, v3/bench/{paths.py,sweep_pose.py}, presentation/defense_2026/anim/{bank_kinematics.py,bank_axes_kinematics.py,causal_replay.py}, presentation/defense_2026/{make_package.py,export_committee_questions.py}, presentation/defense_2026/unity_capture/{run_capture.py,capture_archived_r5.py}, eval/unity_check/run_unity_capture.py, scripts/{start_unity_mcp.py,claude_usage_profile.py}, eval/recordings_archive/DECISIONS.md RA-001/RA-002
Answers: which paths outside the repository folder tracked files still name, which of them are needed at run time, and what a new machine must provide.

# External references (outside the repository folder)

Counts are `git grep -l -e <pattern> | wc -l` (files) on 2026-10-06,
working tree after M5. Patterns are unanchored, so "~/" and
"/home/luo/" forms are both counted. "Provenance" means a recorded
path in a log, manifest, meta file, report or doc: it is never
rewritten (AGENTS.md, Standing project constraints) and needs
nothing at run time.

| Path pattern | Files | Kind | Run-time users | A new machine must provide |
| --- | --- | --- | --- | --- |
| /home/luo/anaconda3 (bin/python, lib/python3.11/site-packages/nvidia) | 197 | run time + provenance | presentation/defense_2026/anim/bank_kinematics.py:41 and bank_axes_kinematics.py:44 (PYTHON = Path('/home/luo/anaconda3/bin/python'), subprocess interpreter); v3/configs/default.json model.cuda_lib_dirs (CUDA, cuDNN, cuBLAS, cuFFT libs of the base anaconda, read by v3/detector/rtmpose_detector.py ensure_cuda_env); writing/v9/scripts/render_pdf.py:30 (frozen). Docstring run lines in eval/akc_comparison/*, eval/pipeline_smoothness/*, v3/* name it but do not hard-code it. Rest (md 92, json 20, txt 11, log 11 of the 197) provenance. | anaconda python 3.11 at /home/luo/anaconda3 with pyrealsense2, mediapipe, opencv and the nvidia CUDA wheels, or a symlink at that path |
| /home/luo/anaconda3/envs/v3rt | 15 | run time + docs | presentation/defense_2026/anim/causal_replay.py:54 (V3RT_PYTHON); all V3 commands in v3/README.md and docstrings | conda env v3rt (onnxruntime-gpu stack, v3/README.md) |
| symlink presentation/defense_2026/experiments/.venv/bin/python -> /home/luo/anaconda3/bin/python | 1 link, git-ignored (experiments/.gitignore), not tracked | run time | experiments/marker_bench/marker_bench.py run as ../.venv/bin/python (marker_bench/README.md lines 27-32) | recreate the venv from the anaconda python: `python -m venv .venv` plus marker_bench/requirements.txt |
| ~/Unity/Hub/Editor/6000.3.19f1 | 11 | run time + logs | eval/unity_check/run_unity_capture.py:65, presentation/defense_2026/unity_capture/run_capture.py:37, capture_archived_r5.py:26, scripts/start_unity_mcp.py:40; review/personal_review_20261005/{capture_scene.py:53,scene_view.py:26} (one-off review scripts) | Unity Editor 6000.3.19f1 installed by Unity Hub at ~/Unity/Hub/Editor (Unity captures only) |
| soffice on PATH (not a path string) | 2 | run time | presentation/defense_2026/make_package.py:116,126, export_committee_questions.py:257 | LibreOffice (soffice), deck and document PDFs only |
| ~/Desktop/ENSC498/recordings | 66 | provenance only | none since RA-002 (v3/configs/clean_windows.json now repository-relative). The two bank_*kinematics.py hits are a comment; BANK = ROOT / 'recordings'. | nothing; on this workstation the old path is a symlink to recordings/ (RA-001) |
| ~/Desktop/ENSC498/record_realsense_bag*.py | 3 | provenance | none | nothing |
| ~/Desktop/ENSC498 (other; all Desktop/ENSC498 = 69 files, overlapping the two rows above) | 5 | docs | none (read-only reference statements) | nothing |
| /home/luo/Desktop/New_SandBox | 65 | run time + provenance | v3/configs/default.json paths.bag and v3/configs/scenarios_20260224*.json; the frozen v1 Unity scripts (Unity/Assets/Scripts/{ArmAngleLogger,ArucoSceneReceiver,IntegratedSceneReceiver,IntegratedSceneReceiverV2}.cs log paths); unity_capture/prepare_project.py rewrites them for captures | the old-name symlink /home/luo/Desktop/New_SandBox -> repository (standing rule), or the repository checked out under that name |
| /home/luo/Desktop/Tracking-and-Reconstruction-of-Bi-Manual-... | 207 | provenance | none found in code outside writing/ and personal_review | nothing; old-name symlink kept on this workstation |
| /Users/luolanqing (macOS working copy) | 9 | provenance + one-off scripts | presentation/defense_2026/review/personal_review_20261005/{animate_p23.py,consolidate_references.py,english_outline.py} (macOS review scripts, not part of any build) | nothing for the Linux pipeline |
| ~/.config/matplotlib | 16 | logs (writing/ audit evidence) | none | nothing |
| ~/.config/unity3d, ~/.cache/unity3d | 4, 2 | logs | none (Unity writes there itself) | nothing |
| ~/.claude/ | 20 | provenance + one tool | scripts/claude_usage_profile.py:17 DEFAULT_DIR (agent cost audit; not part of the project pipeline) | nothing for the project |
| ~/Desktop/v3-realtime | 2 | docs only | none; the folder does not exist | nothing |

Absolute paths to the repository itself (/home/luo/Desktop/bimanual-tracking,
80 occurrences) are inside the folder and not listed.

Data that is inside the folder but not in git: Video/ (9 .bag, 9.3 GiB,
canonical thesis copies incl. the pinned bag) and recordings/ (the bank,
28 .bag, 27 GiB); both git-ignored and local to the Linux workstation
(knowledge/recordings_bank.md).

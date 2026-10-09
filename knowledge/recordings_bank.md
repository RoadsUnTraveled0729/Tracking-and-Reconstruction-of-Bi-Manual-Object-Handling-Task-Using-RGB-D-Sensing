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
Sources: .gitignore, recordings/ (local), eval/recordings_archive/{README.md,DECISIONS.md,index.json,RENAME_MAP.tsv}, presentation/defense_2026/anim/{bank_kinematics.py,bank_axes_kinematics.py,raw_task_context.py}, v3/configs/clean_windows.json, v3/bench/sweep_pose.py, v3/bench/paths.py, v3/tools/side_by_side.py, v3/dataset/phase5_side_by_side_manifest.json
Answers: where the recordings bank (all RealSense .bag recordings) lives, how the old path still works, which code reads it at run time, and which path mentions are provenance only.

# Recordings bank

## Location

- New path: /home/luo/Desktop/bimanual-tracking/recordings (repository
  folder recordings/), moved there on 2026-10-06 (eval/recordings_archive/DECISIONS.md RA-001).
- Old path: /home/luo/Desktop/ENSC498/recordings is now a symlink to the
  new path. Never delete it: 68 tracked files mention Desktop/ENSC498 (git grep -l, 2026-10-06), many of them paths under the bank.
- Git: ignored by .gitignore line "/recordings/"; never pushed, no LFS.
  It is local to the Linux workstation only.
- Contents: 28 .bag files (317 MB to 1.87 GB, 27 GB total), 3 legacy
  symlinks (recording_20260122_154958.bag, recording_20260317_200217.bag,
  recording_20260831_065553.bag) pointing at bags in the same folder,
  thumbnails/ (28 contact-sheet .png), index.json, README.md,
  RENAME_MAP.tsv, visualizer.py.
- Mirror: eval/recordings_archive/ holds tracked copies of index.json,
  README.md and RENAME_MAP.tsv (index.json byte-identical to the live
  one on 2026-10-06).
- Video/ (also git-ignored) is separate: it holds the canonical thesis
  copies under their original recording_<stamp>.bag names; seven of
  them are byte-identical to bank files. Never touched by bank work.

## Run-time readers

- presentation/defense_2026/anim/bank_kinematics.py and
  bank_axes_kinematics.py: BANK = ROOT / 'recordings' (ROOT derived from
  __file__); repository-relative since 2026-10-06.
- presentation/defense_2026/anim/raw_task_context.py: does not read the
  bank; reads Video/recording_20260909_000024.bag and the mirror
  eval/recordings_archive/index.json (sha lookup).
- v3/configs/clean_windows.json: four repository-relative bag paths
  (recordings/<name>.bag) since 2026-10-06 (RA-002); v3/bench/sweep_pose.py
  bag_list resolves them against the repository root with
  bench/paths.py repo_path (absolute paths used as written). The
  other loaders (bench/grade_clean.py, make_scenarios.py,
  teleport_rule_check.py, tools/side_by_side.py, tests/test_grade_clean.py)
  use only the bag stem.

## Provenance only (never rewritten)

- v3/dataset/phase5_side_by_side_manifest.json: written by
  v3/tools/side_by_side.py (write_manifest), not read; its "bag" values
  copy the extraction meta.
- v3/output/clean/*.meta.json "bag" fields, eval/recordings_archive/index.json
  "dir", the probe commands and errors in the archive README, logs,
  manifests and docs: recorded absolute paths, resolved through the
  symlink.

## Known side effect

The ENSC498 repository's .gitignore entry "recordings/" matches
directories only, so its git status shows "?? recordings" for the
symlink (before the move: "!! recordings/"). Not changed, since
~/Desktop/ENSC498 is read-only apart from the bank (RA-001 Review).

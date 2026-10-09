# Release selection and provenance

This private repository is a fresh snapshot, not a rewrite of the workspace
history. source_summary.json pins the source commit and tree;
source_tree.jsonl independently lists every tracked workspace path/mode/blob.
source_manifest.jsonl accounts for each with include/exclude reasons, size
and SHA-256. Included thesis paths lose only the ug_thesis_2026/ prefix.
Frozen scientific files are copied verbatim.

The snapshot retains scientific implementation and validation code across
v1/v2/v3, Unity Assets/Packages/ProjectSettings, evaluation/calibration/labels,
fixtures, numerical and measurement logs, final V9 assembly/checker inputs,
final defence deliverables, presentation sources/assets, manuscript scripts,
scientific decisions, and third-party provenance. Generic directory names
such as logs and .agent are not sufficient reasons to discard evidence.

Workspace instructions, private agent configuration, usage profiling,
orchestration/handoffs and editorial agent task logs are omitted. Raw bags,
weights and generated Unity/environment caches are not copied. Obsolete
manuscript binaries, translated prose/binaries, duplicate delivery packs and
unrequested admissions/career/cloud notes are omitted. The root README and
release notes are new navigation rather than frozen source material.

Local ignored writing/v1-v7 scripts and their script-referenced figure
inputs/citation tables are optional historical supplements, not current
V9 dependencies. Supplemental rows also record unselected candidate assets. Every row records its local SHA-256 and whether
its Git blob matches archive/writing-v1-v7; source workspace Git remains
unchanged. Historical manuscript binaries remain excluded. The supplemental
rows distinguish local archive recovery from the pinned tracked snapshot.

Historical documentation and scientific decision records preserve their
original claims, names and provenance. They may link to omitted editorial
work, manuscript binaries, historical Git commits/tags, or external data.
Those links provide context and are not release reproduction promises.
Current reviewer entrypoints are the root README, final artifacts and
REPRODUCTION.md. Source accounting is checked separately from scientific
correctness. No AI co-author trailer is to be added to the fresh commit;
existing truthful technical provenance and upstream credits remain intact.

To reproduce selection from the source workspace, using an empty/new
release destination and the commit recorded in source_summary.json:

```bash
python3 -B release/prepare_snapshot.py --source SOURCE_WORKSPACE --commit SOURCE_COMMIT --destination NEW_RELEASE_DIRECTORY --copy
```

This exports immutable tracked Git blobs and supplements the verified local
archive sources. It does not copy .git or publish a remote. Release-authored
README/notes and the empty Video placeholder must be supplied separately.

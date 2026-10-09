# thesis/ — thesis material for the offline phase

Currency note (2026-10-08): This folder preserves early offline-phase
mathematical write-ups. The final thesis and its post-defence revision
status are documented in [writing/v9/README.md](../writing/v9/README.md).
The chapters' original marker settings, recording labels, measurements and
unprefixed implementation/reproduction paths belong to that earlier stage;
they are not current thesis results or current run instructions. The v1
implementation now lives under v1/ and is frozen. This notice preserves the
chapter text and its original evidence rather than rebinding old numbers.

Self-contained, thesis-grade write-ups of the math behind the offline
system: every procedure derived (not just cited), every claim tied to a
pinned validation artifact in the repo. The working engineering notes
(`v1/KINEMATIC_MODEL.md`, `v1/ARUCO_MODEL.md`, `v1/INTEGRATION.md`,
`v1/OBJECT_OFFSET.md`, `.agent/FINDINGS.md`) remain the canonical repo
record; this folder is the write-up layer on top of them, with one
consistent notation defined once in `00_notation.md`.

## Chapter map

| file | content | suggested thesis chapter |
|---|---|---|
| `00_notation.md` | frames, symbols, conventions, recordings | Preliminaries / Notation |
| `A1_acquisition_filtering.md` | sensor model, deprojection, landmark extraction, glitch filtering | Methods — data acquisition |
| `A2_kinematic_model.md` | root frame, Euler convention, shoulder swing–twist, elbow, left arm, rig transfer | Methods — kinematic model (core) |
| `A3_occlusion.md` | blocked-landmark detection + chain fallback | Methods — robustness |
| `B1_aruco_scene.md` | marker pose, ambiguity policy, scene calibration, object track | Methods — ground-truth pipeline |
| `C1_integration_evaluation.md` | anchor transform, independence argument, accuracy evaluation | Evaluation |
| `D1_limitations.md` | limitations with mathematical justification | Limitations / Discussion |

Reading order = table order. Equations are GitHub-flavored LaTeX
(`$inline$`, `$$display$$`).

## Converting to Word for review

```bash
pandoc thesis/A2_kinematic_model.md -o A2_kinematic_model.docx
# all chapters into one document:
pandoc thesis/00_notation.md thesis/A*.md thesis/B*.md thesis/C*.md \
       thesis/D1_limitations.md -o offline_phase.docx
```

(If `pandoc` is missing: `conda install -c conda-forge pandoc` or
`sudo apt install pandoc`.)

## Provenance rule

Every number quoted in these chapters comes from a pinned artifact
(`v1/kinematics/dataset/`, `v1/aruco/dataset/`, `v1/integration/dataset/`,
`v1/mediapipe/output/*.meta.json`) or a validator output committed to the
repo — nothing is asserted from memory. Each chapter ends with a
"Reproduce" note naming the scripts that regenerate its numbers.

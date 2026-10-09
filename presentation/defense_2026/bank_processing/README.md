# Recording-bank kinematics lessons

Currency note (2026-10-08): The data and source checks described here are
retained evidence from earlier bank demonstrations. All page numbers and
claims of an active collection below belong to those earlier decks; use
[the presentation README](../README.md) for the final delivery. The source
checkers check_bank_sources.py, check_unified_sources.py and
check_unified_four_sources.py remain, but check_bank_media.py,
check_unified_media.py, check_unified_four_media.py,
anim/unified_revision_build.py, build_deck.py and validate_deck.py were
retired (D-385; original paths at 87e87ae). Thus the historical full media
build/validation sequences below are not complete current commands.
Original hashes, counts, frame intervals and findings are preserved.

These are newly processed qualitative demonstrations for presentation pages
13-20. They show the recorded camera image and a calculation from the same
inference frame. Pages 17-20 were processed first (sections below); pages
13-16 and the unified re-rendering of all eight pages were added on
2026-09-24 (section "Unified layout, pages 13-20"). They do not add an accuracy experiment or reuse the legacy
ENSC498 angle JSON files. Original bags, frozen methods and earlier media
remain unchanged.

## Sources and selection

All bags are read from `/home/luo/Desktop/ENSC498/recordings`.

| Page | Bag | Selected color-frame indices | Movie |
| --- | --- | --- | --- |
| 13-15 | ENSC498_arms_outstretched_pose_test_arm_test.bag | 780-885 | 11.067 s each |
| 16 | ENSC498_right_arm_raise_cube_untouched_test_20260121_180042.bag (p17 extraction) | 798-947 | 14.000 s |
| 17 | ENSC498_right_arm_raise_cube_untouched_test_20260121_180042.bag | 798-947 | 14.000 s |
| 18 | ENSC498_right_arm_landmark_test_right_arm_test.bag | 360-720 | 28.067 s |
| 19 | ENSC498_right_elbow_bend_test_right_elbow.bag | 180-540 | 28.067 s |
| 20 | ENSC498_right_shoulder_arms_out_test_right_shoulder.bag | 28-208 | 16.067 s |

The first p17 candidate, frames 0-191, had 31 rejected right-wrist samples.
The later selected interval retains useful lowering/raising motion with all
eight raw landmarks accepted. The first p20 candidate, frames 0-180,
contained detector warm-up; the selected interval starts at frame 28.
The original full-recording eligibility failure for p20 is retained.

All four selected windows pass the unchanged repository tracking
precondition checker, with coverage at least 0.95 and maximum gap at most
0.5 s for every required landmark. Accepted pixels are estimates; the
visibility/depth gate does not establish anatomical ground truth. No hip
point was manually moved. Camera photos were reviewed to check that the
displayed torso points do not simply trace the desk.

## Processing and identity

The frozen heavy MediaPipe model runs on the CPU over each complete bag.
The unchanged extractor uses visibility 0.5 and a 5 by 5 median nonzero
depth window. The frozen offline filter uses a 7-frame Hampel window,
multiplier 3, 0.02 m floor, interior gaps at most 5 frames, no edge fill,
and fourth-order 3 Hz forward/backward Butterworth smoothing.

`extract_logged.py` executes a copy of the frozen extractor with one added
logging call immediately before the RGB image enters MediaPipe. The exact
copy and one-line diff are under `sources/`. Each `pNN/inference_frame_map.json`
records the color hardware frame ID, absolute timestamps, relative clock,
exact RGB-array SHA-256 and cached PNG hash. Filtering preserves `_src`
and adds `_flag`; both are retained in the delivered source records.

The current frozen `root_frame.py` and `shoulder.py` supply the torso,
swing, twist and elbow calculations. The four lower panels differ:

- Page 17: upper-arm vector in the shoulder-origin, torso-oriented L12
  frame, with a fixed reference and moving swing basis.
- Page 18: unit forearm after undoing swing, projected onto its Y-Z plane;
  the signed arc is the shoulder twist coordinate.
- Page 19: unit forearm in the fully rotated L14 frame, projected onto
  X-Z; the signed arc is the elbow y coordinate.
- Page 20: the actual small perpendicular component, shown beside a
  separate exact-zero schematic. All recorded frames retain `twist_ok`.
  No observed frame is called singular or held.

Camera triads use each bag's own intrinsics and the Camera/Camera-prime
point reflection. No wrist orientation is inferred. Page 17/18/20 camera
triads show the swing basis; page 19 shows the fully rotated elbow parent.
Every camera/model pair uses a single explicit source-frame map. Source
frames are repeated twice at 30 fps, with 2 s endpoint holds.

## Reproduction

Run from the repository root using the thesis Python. RealSense playback
requires a normal host process with udev available; a restricted sandbox
may fail before opening a bag.

```bash
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/defense_bank_mpl /home/luo/anaconda3/bin/python presentation/defense_2026/anim/bank_kinematics.py --extract
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/defense_bank_mpl /home/luo/anaconda3/bin/python presentation/defense_2026/anim/bank_kinematics.py --preview
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/defense_bank_mpl /home/luo/anaconda3/bin/python presentation/defense_2026/anim/bank_kinematics.py --build
```

An intact completed cache reuses extraction only after validating all
bound source/model/adapter/CSV/meta hashes, frame counts and clocks.
It does not silently regenerate missing PNGs. The RGB cache is under
`/tmp/defense_bank_rgb/pNN`; it is not part of the slide-delivery package.
If this cache has been cleared, the following runs exact-frame extraction
into a new isolated output directory while rebuilding the RGB cache.
The canonical CSVs/maps remain untouched. Subsequent rendering verifies
the rebuilt pixels against the existing inference RGB and PNG hashes.

```bash
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/defense_bank_mpl /home/luo/anaconda3/bin/python - <<'PY'
import json
import pathlib
import subprocess
import tempfile

work = pathlib.Path('presentation/defense_2026/bank_processing').resolve()
fresh = pathlib.Path(tempfile.mkdtemp(prefix='cache_rebuild_', dir=work))
for page in range(17, 21):
    manifest = json.loads((work / f'p{page}/source_manifest.json').read_text())
    command = manifest['commands']['extract'][:]
    command[command.index('--out') + 1] = str(fresh / f'p{page}/landmarks_raw.csv')
    subprocess.run(command, check=True)
print('Fresh extraction outputs:', fresh)
PY
```

## Unified layout, pages 13-20

On 2026-09-24 the author asked for one right-column layout on pages 13-20:
the recorded video with its overlay on top, the 3D model drawn with the
recording's own pinhole projection at lower left, and a small 2D plane
panel with that page's quantity at lower right. `../anim/unified_panels.py`
draws it for every page; its hash is bound in every producer report as
`layout_renderer_sha256`. Decisions D-071 to D-078 in `../DECISIONS.md`.

- Pages 13-15: `../anim/bank_axes_kinematics.py` reads one extraction of
  the arms-outstretched trial (`p13/`; pages 14 and 15 bind it through
  `p14/source_reference.json` and `p15/source_reference.json`). The window
  is a standing T-pose facing the camera with a small lean; it shows no
  torso rotation. Measured root angles stay near x -12..-8, y 171..180 and
  z -13..-6 deg (NEW_BINDINGS.md in committee_materials/bank_axes_revision).
- Page 16: the same producer reads the page 17 extraction through
  `p16/source_reference.json`, so its arm direction is the motion whose
  swing page 17 reads.
- Pages 17-20: version 2 of `../anim/bank_kinematics.py` reads the existing
  `p17/`-`p20/` extractions without rewriting them; its derived files go to
  `unified_v2/pNN/` and its films to
  `../committee_materials/bank_revision_v2/`. The first collection,
  `../committee_materials/bank_revision/`, is left unchanged.
- The new extraction uses `extract_logged_v2.py`, identical to
  `extract_logged.py` except that its instrumented copy and diff are written
  to `sources_v2/`, so the hash-bound `sources/` files stay unchanged.

```bash
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/defense_bank_mpl /home/luo/anaconda3/bin/python presentation/defense_2026/anim/bank_axes_kinematics.py --extract
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/defense_bank_mpl /home/luo/anaconda3/bin/python presentation/defense_2026/anim/bank_axes_kinematics.py --build
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/defense_bank_mpl /home/luo/anaconda3/bin/python presentation/defense_2026/anim/bank_kinematics.py --build
PYTHONDONTWRITEBYTECODE=1 /home/luo/anaconda3/bin/python presentation/defense_2026/bank_processing/check_unified_sources.py
PYTHONDONTWRITEBYTECODE=1 /home/luo/anaconda3/bin/python presentation/defense_2026/bank_processing/check_unified_media.py
/home/luo/anaconda3/bin/python presentation/defense_2026/anim/unified_revision_build.py
```

`UNIFIED_SOURCE_CHECK.json` records 10846 PASS / 0 FAIL: source clocks,
exact inference pixels, raw/filter flags, independent angle and matrix
recomputation, reprojection, the model-panel projection and fail-closed
negative cache cases. The media audits record 203 PASS / 0 FAIL
(`../committee_materials/bank_axes_revision/review/BANK_AXES_MEDIA_CHECK.json`)
and 213 PASS / 0 FAIL
(`../committee_materials/bank_revision_v2/review/BANK_V2_MEDIA_CHECK.json`),
including full decode counts and the overlay/model congruence at L12.
Whole-recording tracking preconditions pass for pages 13-19; page 20's
whole recording still fails its hand windows while the selected window
passes. `../anim/unified_revision_build.py` binds the eight films into
`../committee_materials/unified_revision/media_contract.json`, which
`../validate_deck.py` checks against these three reports. The older
`BANK_SOURCE_CHECK.json`, `check_bank_sources.py`, `check_bank_media.py`
and their reports remain history for the first collection; the producer
hash in `BANK_SOURCE_CHECK.json` no longer matches the version-2
`bank_kinematics.py`, and that report is not re-run.

## Checks and limitations

```bash
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/defense_bank_mpl /home/luo/anaconda3/bin/python presentation/defense_2026/anim/bank_kinematics.py --check-overlay
PYTHONDONTWRITEBYTECODE=1 /home/luo/anaconda3/bin/python presentation/defense_2026/bank_processing/check_bank_sources.py
PYTHONDONTWRITEBYTECODE=1 /home/luo/anaconda3/bin/python presentation/defense_2026/bank_processing/check_bank_media.py
```

`BANK_SOURCE_CHECK.json` checks source clocks, exact inference pixels,
raw/filter flags, independent vector/SciPy angle calculations, OpenCV
reprojection and ten negative cache/verdict cases. The final media report
is `../committee_materials/bank_revision/review/BANK_MEDIA_CHECK.json`.
Individual movie reports contain the full decode/count checks and exact
output-to-source frame maps.

`run_overlay_checker.py` is a path-only adapter for the unchanged repository
`eval/inspect/check_v1_overlay.py`. Its separate replay pairs rows by
enumeration and produces diagnostic fixed-length FK overlays. It does not
independently certify exact inference-frame pairing; the same-pass RGB
and hardware-clock records provide that evidence. Its residuals are
internal consistency diagnostics, not external accuracy measurements.

The p20 whole-bag checker fails hand eligibility because of warm-up, while
its selected interval passes. CPU processing timings are not comparable
to the thesis runtime benchmark. Desktop PowerPoint playback of these
four new movies still needs a host rehearsal.

## Merged pages 13-16 (unified_four, 2026-09-24 round 2)

The eight unified pages were merged into four (plan virtual-wiggling-globe.md,
M1). `anim/bank_axes_kinematics.py` now produces only these four films; its
earlier pages 13-16 (bank_axes_revision) and all older folders stay unchanged.
Each page reads a whole-bag extraction by hash (`unified_four/pNN/source_reference.json`);
MediaPipe was not re-run.

| Page | Topic | Bag (extraction) | Source frames | Movie |
| --- | --- | --- | --- | --- |
| 13 | Torso frame | arms_outstretched arm_test (p13) | 780-885 | 11.067 s |
| 14 | Shoulder swing | 180042 arm raise (p17) | 3-109 | 11.133 s |
| 15 | Shoulder twist | right_arm_test (p18) | 505-725 | 18.733 s |
| 16 | Elbow | right_elbow (p19) | 180-540 | 28.067 s |

The camera-view model draws the parent frame dim and the rotated frame bright
at the page's joint, with a grey 3D arc from the parent axis to the rotated
axis (DECISIONS.md D-088 to D-093). On pages 14 and 16 the bright X axis has
the bone length, so it ends on the bone end. Page 14 accepts two
filter-interpolated right-wrist frames (25, 53; D-089). On page 15 the twist
plane is nearly edge-on to this camera, so the 2D panel carries the twist.

`check_unified_four_sources.py` (UNIFIED_FOUR_SOURCE_CHECK.json) asserts on
every selected frame of pages 14-16 that the rotated X axis lies on the bone
within 1e-3 deg, from the stored and from independently recomputed frames.
`check_unified_four_media.py` (committee_materials/unified_four/review/UNIFIED_FOUR_MEDIA_CHECK.json)
checks decode counts, holds, constant panel geometry, X tip against bone end
within 2 px in both panels, and printed arc values against derived_kinematics.csv.

```bash
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/defense_bank_mpl /home/luo/anaconda3/bin/python presentation/defense_2026/anim/bank_axes_kinematics.py --extract --build
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/defense_bank_mpl /home/luo/anaconda3/bin/python presentation/defense_2026/bank_processing/check_unified_four_sources.py
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/defense_bank_mpl /home/luo/anaconda3/bin/python presentation/defense_2026/bank_processing/check_unified_four_media.py
```

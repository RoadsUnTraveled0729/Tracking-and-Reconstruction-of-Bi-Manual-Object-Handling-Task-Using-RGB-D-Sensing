# Chapter 7 evidence regeneration on the E-037 captures, 2026-09-14

Every number and figure below was produced by re-running a script on the
archived captures of E-037. No evidence value, pinned constant or figure was
hand-edited. Where a pin had to move, it was recomputed from the file it
protects by a script that prints the old and new value; where a guard failed,
the step was stopped and reported instead of loosened.

Interpreter: `/home/luo/anaconda3/bin/python`, run from the repository root
with `MPLCONFIGDIR` and `XDG_CACHE_HOME` pointed at a session scratch
directory. Repository at commit 64467ea (E-037), branch master.

Capture archives read (E-036, E-037):

| presentation | archive | unique frames |
| --- | --- | --- |
| rail sensor view | `writing/v9/figures/src/r6b_unity_sensor/` plus `figures/src/r6b_unity_f000{95,114,505,700,898}.png` | 899 PNGs of 900 streamed |
| rail presentation | `writing/v9/figures/src/ch7_trails_revision/` | 487 |
| handover presentation | `writing/v9/figures/src/ch7_handover_trails/` | 938 |

## 1. Commands and exit codes, in the order they were run

| # | command | exit |
| --- | --- | --- |
| 1 | `writing/v9/scripts/evaluate_ch7_restructured.py` | 0 |
| 2 | `writing/v9/scripts/evaluate_ch7_bare_model.py` | 0 |
| 3 | `writing/v9/scripts/evaluate_ch7_object.py` | 0 |
| 4 | `writing/v9/scripts/evaluate_ch7_spatial_check.py` | 0 |
| 5 | `writing/v9/scripts/compare_captures_v8_v9.py` | 0 |
| 6 | `writing/v9/scripts/make_ch7_handover_trails.py` | 0 |
| 7 | `writing/v9/scripts/make_ch7_trails_fig.py` (r6b) | 0 |
| 8 | `writing/v9/scripts/make_ch7_trails_fig.py r7` | 0 |
| 9 | `writing/v9/scripts/make_ch7_unity_pairs.py` | 0 |
| 10 | `writing/v9/scripts/make_ch7_task_schematic.py` | 0 |
| 11 | `writing/v9/scripts/make_ch7_object_trajectory.py` | 0 |
| 12 | `writing/v9/scripts/make_ch7_wrist_traj_fig.py` | 0 |
| 13 | `writing/v9/scripts/make_ch7_handover_fig.py` | 0 |
| 14 | `writing/v9/scripts/make_ch7_frame_strip.py` | 0 |
| 15 | `writing/v9/audit_evidence/ch7_visual_restoration/compose_unity_trajectories.py` | **1** (pin mismatch on `human.json`, before re-pinning) |
| 16 | `writing/v9/scripts/repin_compose_unity_trajectories.py` (written for this step) | 0 |
| 17 | `writing/v9/audit_evidence/ch7_visual_restoration/compose_unity_trajectories.py` | 0 |
| 18 | `writing/v9/scripts/repin_ch7_visual_examples.py` (written for this step) | 0 |
| 19 | `writing/v9/scripts/make_ch7_visual_examples.py` | 0 |
| 20 | `writing/v9/audit_evidence/followup/m17_segment_diagnostic.py` | 0 |
| 21 | `writing/v9/scripts/verify_ch7_restructured.py --print-pins` | 0 |
| 22 | `writing/v9/scripts/verify_ch7_restructured.py` | **1** (1 FAIL: stale self-hash in `loop_detection.json`) |
| 23 | `writing/v9/scripts/evaluate_ch7_loop_detection.py` | 0 |
| 24 | `writing/v9/scripts/verify_ch7_restructured.py` | 0 (PASS 1157, FAIL 0, SKIP 21) |
| 25 | `writing/v9/scripts/validate_ch7_trails_revision.py` | **1** (stale `ch7_trails_source_hashes.json`) |
| 26 | `writing/v9/scripts/repin_ch7_trails_sources.py` (written for this step) | 0 |
| 27 | `writing/v9/scripts/validate_ch7_trails_revision.py` | **1** (pre-existing legacy docx-embedding assertion; see escalations) |
| 28 | `writing/v9/scripts/build_ch7.py` | 0 (D-042 guard held) |
| 29 | `writing/v9/scripts/build_ch6.py` | 0 |
| 30 | `writing/v9/scripts/check_style.py Chapter_6_System_Integration Chapter_7_Evaluation` | 0 (0 hits each) |
| 31 | `writing/v9/scripts/check_refs.py` | 0 (615 references, UNRESOLVED none) |
| 32 | `writing/v9/scripts/test_assembly_citations.py` | 0 (2 tests OK) |
| 33 | `writing/v9/scripts/dump_docx.py writing/v9/Chapter_7_Evaluation.docx` | 0 |
| 34 | `writing/v9/scripts/validate_ch7_trails_revision.py` (after the rebuild) | **1** (same pre-existing assertion) |

## 2. Matched-dimensions guard, `rig_sizing()`

`evaluate_ch7_restructured.rig_sizing()` passed for both recordings at
`RIG_TOL_M = 1e-3`, with a maximum absolute difference of **0.0 m** on each:
every requested length appears in the rendered rig exactly.

| recording | upper_arm_R | forearm_R | upper_arm_L | forearm_L | torso |
| --- | --- | --- | --- | --- | --- |
| r6b requested and rendered | 0.3170 | 0.2050 | 0.3100 | 0.2570 | 0.5745 |
| r7 requested and rendered | 0.2410 | 0.2330 | 0.2520 | 0.2230 | 0.5166 |

The V8 captures rendered the loop constants 0.256 / 0.252 / 0.262 / 0.247 m
with trunk 0.576 m (r6b) and 0.517 m (r7) for both recordings, which is the
configuration mismatch E-036 removes.

## 3. Tables 7.3 and 7.4, old against new

Old: `writing/v8/condensed/audit_evidence/ch7_restructured/human.json`.
New: `writing/v9/audit_evidence/ch7_restructured/human.json`.
Errors are centimetres between the captured rig joint and the accepted
measured landmark, on the accepted frames of each capture.

Captured frames: r6b 485 old, **487** new; r7 934 old, **938** new.

| table | recording | side and joint | n old | n new | median old | median new | p95 old | p95 new | max old | max new |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 7.3 | r6b | right elbow | 100 | 102 | 10.66 | **6.41** | 12.31 | **7.46** | 24.34 | **19.46** |
| 7.3 | r6b | right wrist | 100 | 102 | 11.95 | **11.36** | 16.79 | **15.38** | 23.38 | **22.95** |
| 7.4 | r7 | right elbow | 650 | 650 | 5.70 | **5.31** | 6.33 | **6.68** | 8.17 | **9.35** |
| 7.4 | r7 | right wrist | 650 | 650 | 5.71 | **5.46** | 6.55 | **6.84** | 15.93 | **15.04** |
| 7.4 | r7 | left elbow | 589 | 589 | 6.33 | **6.14** | 11.57 | **11.89** | 17.33 | **17.74** |
| 7.4 | r7 | left wrist | 589 | 589 | 6.87 | **6.75** | 11.06 | **12.26** | 16.37 | **17.75** |

`compare_captures_v8_v9.py` reports 20 of 24 statistics changed in
`human.json`. The comparison is a summary one, not frame matched: each
capture writes one row per Unity Update of a wall-clock sender, so the two
runs accept different frame subsets of the same recording and a changed n is
expected. The largest movement is the r6b elbow median, 10.66 to 6.41 cm.

Table rows dumped from `writing/v9/Chapter_7_Evaluation.docx` after the
rebuild, each equal to `human.json` at the printed precision:

| table | row | n | median | p95 | maximum |
| --- | --- | --- | --- | --- | --- |
| 7.3 | Right Elbow | 102 | 6.4 | 7.5 | 19.5 |
| 7.3 | Right Wrist | 102 | 11.4 | 15.4 | 22.9 |
| 7.4 | Right Elbow | 650 | 5.3 | 6.7 | 9.4 |
| 7.4 | Right Wrist | 650 | 5.5 | 6.8 | 15.0 |
| 7.4 | Left Elbow | 589 | 6.1 | 11.9 | 17.7 |
| 7.4 | Left Wrist | 589 | 6.8 | 12.3 | 17.7 |

All six rows verified equal to `human.json` programmatically.

## 4. Scripts with no capture dependence

Re-run and confirmed to reproduce their outputs byte-identically:

- `evaluate_ch7_object.py`: `object.json` and `object_pairs.csv` unchanged.
  `object_provenance.json` changed in exactly one field, the script's own
  sha256, which was stale against the committed script; every number and
  every other source hash is byte-identical.
- `evaluate_ch7_spatial_check.py`: `spatial_check_pairs.csv` unchanged.
  `spatial_check.json` changed in exactly one field, the script's own
  sha256, same stale-self-hash cause; every number identical (right 15.77,
  handover left 15.85 and right 17.91, left 14.08 cm).
- `evaluate_ch7_loop_detection.py`: only its own self-hash changed; every
  count identical (detected 2058 of 2099, accepted 2046, 41 missing).
- Figure scripts reproducing byte-identical PNGs: `make_ch7_task_schematic.py`,
  `make_ch7_object_trajectory.py`, `make_ch7_wrist_traj_fig.py`,
  `make_ch7_handover_fig.py`, `make_ch7_frame_strip.py`.
  `make_ch7_frame_strip.py` was checked against `figures/ch7_frames_strip.json`
  first: its four panels are colour frames extracted from the bag
  (`figures/src/r6b_frame000{95,505,700,898}.png`), not sensor-view stills, so
  it has no capture dependence. `make_ch7_handover_trails.py` also reproduced
  `eval/reports/unity_check_r7/trails.txt` byte-identically; it derives the
  trails from the recovery angles, not from a capture.

`evaluate_ch7_bare_model.py` IS capture dependent: it takes its accepted
frame set from `evaluate_ch7_restructured.accepted`, so the r6b frame count
moved from 100 to 102 and the rendered rig block now records the per-recording
lengths.

## 5. Pins changed

### `writing/v9/scripts/verify_ch7_restructured.py`

Regenerated from `--print-pins`, which reported 18 of 21 pinned values equal
to the evidence and 3 changed. Pasted verbatim; no pin became a tolerance, a
range or an inequality.

| constant | old | new |
| --- | --- | --- |
| `PIN_RAIL_SUBSET_MEDIAN` | 6.78 | 6.77 |
| `PIN_HUMAN_R7_WRIST` | `{'right': 5.71, 'left': 6.87}` | `{'right': 5.46, 'left': 6.75}` |

`PIN_BARE_SUBSET`, `PIN_BARE_WIDE`, `PIN_TWIST_SHARE`,
`PIN_REFERENCE_CONVENTION`, `PIN_TWIST_MEASURED_SPAN` and
`PIN_TWIST_HELD_SPAN` were unchanged. The two stated prose spans are
unchanged (twist measured 0.6 to 0.9 cm, twist held 2.3 to 2.8 cm), with
observed extremes 0.57 to 0.94 cm and 2.34 to 2.79 cm inside them.

### `writing/v9/audit_evidence/ch7_visual_restoration/compose_unity_trajectories.py`

Ten pins regenerated by the new `repin_compose_unity_trajectories.py`:
`TABLE_SCOPE_SHA256` (human.json), and per alias
`layout_reference_sha256`, `compose_sha256`, `capture_sha256` and
`view_sha256` for r6b and r7; plus `r6b.table_samples` from
`{right_elbow: 100, right_wrist: 100}` to `{right_elbow: 102, right_wrist: 102}`.
Unchanged and left alone: `NATIVE_COMPOSER_SHA256`, both `trails_sha256`,
both `intervals_sha256`, both `historical_states_sha256`,
`r7.handover_intervals_sha256`, `r7.table_samples`, and both
`expected_dimensions_px` (r6b 1565x1468, r7 1511x1468, re-measured by the
composer's own `compose()` and found unchanged).

### `writing/v9/audit_evidence/remove_intermediate_frame/ch7_visual_examples_sources.json`

Nine r6b pins regenerated by the new `repin_ch7_visual_examples.py`.
Figure 7.6 (r7) keeps its old sources and pins by author decision, and all
six r7 row images were confirmed to still hash as pinned.

| entry | old | new |
| --- | --- | --- |
| `r6b_unity_f00095.png` (and its `original_sha256`) | 51fe0390... | d11e6892... |
| `r6b_unity_f00505.png` (and its `original_sha256`) | 39e70ff7... | 227290d5... |
| `r6b_unity_f00700.png` (and its `original_sha256`) | c904028c... | 2bbb0ecf... |
| evidence `make_ch7_unity_pairs.py` | 02b8737e... | dc378019... |
| evidence `make_ch7_frame_strip.py` | cb69b5d1... | 091fc780... |
| `r6b.capture_context` | "Saved 2026-09-07 sensor-view capture..." | rewritten from `figures/src/r6b_unity_sensor/rig_sizing_used.txt` and E-037 |

The three r6b colour frames, `figures/ch7_frames_strip.json`, all image
dimensions (640x480) and `shared_evidence` `EvalFrameDump.cs` were unchanged.

### `writing/v9/ch7_trails_source_hashes.json`

Five of forty keys re-pinned by the new `repin_ch7_trails_sources.py`; the
key list is unchanged and no protected file was added or dropped.

| key | old sha256 and bytes | new sha256 and bytes |
| --- | --- | --- |
| `figures/src/r6b_unity_f00095.png` | 51fe0390... 206854 | d11e6892... 207079 |
| `figures/src/r6b_unity_f00114.png` | d583f020... 206248 | b1e378fe... 206792 |
| `figures/src/r6b_unity_f00505.png` | 39e70ff7... 197332 | 227290d5... 197987 |
| `figures/src/r6b_unity_f00700.png` | c904028c... 198468 | 2bbb0ecf... 199614 |
| `figures/src/r6b_unity_f00898.png` | 68759f1a... 203498 | 3521270e... 205356 |

The old values in this table were read back from `git show HEAD:` because
the first version of the re-pin script printed the mutated record and so
displayed the new value in its "old" column. The script was corrected to
copy each record before updating it; re-running it after the fix reports
"all 40 protected sources already match; file untouched", which confirms the
written file was correct and the defect was in the printing only.

The other thirty-five keys still hash as recorded, including the bag, the
filtered landmarks, the cleaned object track, the scene calibration, the
recovery angles, `trails.txt`, `integrated_stream.csv`, the waypoints, the
wrist trajectory record, every colour frame and the three
`r6b_unity_trails_f*.png` stills of E-032.

## 6. Figures regenerated, with new sha256

| figure | new sha256 |
| --- | --- |
| `figures/ch7_unity_trajectories_r6b.png` (Figure 7.3) | `bb73ff8e267448c5d3414f29b8c6143c987e2e6d05259fd50dcd32e7fbed005f` |
| `figures/ch7_unity_trajectories_r7.png` (Figure 7.4) | `07c65e297e249438e24d9695ac246f0760295b361c30b04f635eeb0181f20c85` |
| `figures/ch7_visual_examples_r6b.png` (Figure 7.5) | `309dadf901e962d54be0d1fd935b57ac02e14d8b2c725168eae12ef5b14dc15e` |
| `figures/ch7_fig_unity_trails.png` (native r6b composition) | `26075ee8090b4ebe9174d3cca34f7f0259d281ef60e41a521336e76243e080e0` |
| `figures/ch7_fig_handover_trails.png` (native r7 composition) | `58917dce92479e4678b466e25e5830b11531f1a6a0661090d49a0829d3594e99` |
| `figures/ch7_fig_unity_pairs.png` | `ca37114fd6ef70ff064af1f9528ce5c564572431f64c6cba0b4e5355d97c8135` |
| `figures/ch7_trails_compose.json` | `5794dbc60c212583c08d8208a4110b7045336a670a1412b1f98e1da81102b3d1` |
| `figures/ch7_handover_compose.json` | `b4048cab276670979d89a2eca850ad71c4288e6f73d1a05526854eca6cb1ca5a` |

`figures/ch7_visual_examples_r7.png` (Figure 7.6) is byte-identical to before,
as the author's decision requires. Eighty-seven of the ninety-eight hashed
figure and manifest files under `writing/v9/figures` and the two evidence
folders are unchanged.

## 7. Guards and checks

- `rig_sizing()` in `evaluate_ch7_restructured.py`: PASS for r6b and r7,
  worst difference 0.0 m against a 1 mm tolerance.
- D-042 in `build_ch7.py`: PASS. `bare_model.json` r6b right wrist reports
  `twist_held_frames == n` at both scopes, 102 == 102 on
  `section_7_3_frame_set` and 514 == 514 on `recording_wide_accepted`, and
  `output_tags.root['2'] == n` at both. `build_ch7.py` exited 0, so both
  assertions held, and the stale-evidence warning at line 358 did not fire
  because `human.json` now carries `rig_sizing` for both recordings.
- D-043, inverted per E-036: PASS. `verify_ch7_restructured.py` section [3]
  reports "bare model r6b avatar sizing (E-036): 6 checks ... avatar segment
  lengths equal the calibrated lengths", and the same for r7.
- `check_rig_sizing`-equivalent agreement is also visible in
  `m17_segment_diagnostic.json`: rendered rail r6b 0.317 / 0.205 / 0.310 /
  0.257 / 0.5745 and rendered handover r7 0.241 / 0.233 / 0.252 / 0.223 /
  0.5166, each equal to its sizing JSON.

`verify_ch7_restructured.py`, final run, PASS/FAIL/SKIP by group:

| section | PASS groups | FAIL | SKIP |
| --- | --- | --- | --- |
| [1] Human rendered-rig errors (D-031, D-040, D-043) | 11 | 0 | 3 |
| [2] Synthetic removal windows (D-032) | 28 | 0 | 3 |
| [3] Bare kinematic-model wrist and elbow errors (D-039 to D-043) | 32 | 0 | 4 |
| [4] Object segment lengths (D-035, D-036) | 23 | 0 | 5 |
| [5] Natural occlusion wrist proxies (D-033) | 12 | 0 | 1 |
| [6] Loop-recording object-marker coverage | 5 | 0 | 1 |
| [7] Human-object spatial check (D-038) | 11 | 0 | 3 |
| [8] Provenance of the recorded inputs | 6 | 0 | 0 |
| [9] Published values, recomputed from the pairs | 6 | 0 | 1 |
| total individual checks | 1157 | 0 | 21 |

Every SKIP is a pre-existing one: the skipped quantities need gitignored
inputs under `eval/output` (landmark CSVs, failure masks, scene calibrations,
object tracks) or are author tape measurements, and none was introduced here.

Document checks: `check_style.py` 0 hits on Chapter 6 and Chapter 7;
`check_refs.py` 615 references, UNRESOLVED none, never-referenced equations
3.15, 3.16, 3.19, 6.3 and 7.3 (pre-existing); `test_assembly_citations.py`
2 tests OK.

`validate_ch7_trails_revision.py` after re-pinning: PASS on all forty
protected sources, PASS on every exported point, frame and wrist state, PASS
on the capture manifest of 2026-09-14 18:05:38 against 10 files and the view
config, PASS on Figure 7.10 composed from this capture, and PASS on the
carry, lift and slide endpoint poses (frames 92-500, 501-528, 529-899). It
then stops on a pre-existing assertion described under escalations.

## 8. Choices made

1. Ran the five figure scripts with no Unity-capture dependence rather than
   only asserting they had none, and verified byte-identical output. This is
   stronger evidence than a claim and cost nothing.
2. Determined `make_ch7_frame_strip.py`'s capture dependence by reading
   `figures/ch7_frames_strip.json` first: its four panels are bag-extracted
   colour frames, so it is not a sensor-view consumer.
3. Wrote `writing/v9/scripts/repin_compose_unity_trajectories.py` because
   `compose_unity_trajectories.py` carries its pins as inline constants and
   ships neither a re-pin option nor a companion script. The re-pin script
   recomputes each value from the file the composer itself names, measures
   the output dimensions by calling the composer's own `compose()`, refuses
   to rewrite a literal it cannot locate uniquely, and prints old and new.
4. Wrote `writing/v9/scripts/repin_ch7_visual_examples.py` for the same
   reason: nothing in the repository writes
   `ch7_visual_examples_sources.json`. It is scoped to the r6b entry only,
   re-measures every image's dimensions, and rewrites `capture_context` from
   the capture's own `rig_sizing_used.txt` plus the E-037 identifier rather
   than from prose. It reports, without touching, any out-of-scope pin that
   no longer matches.
5. Wrote `writing/v9/scripts/repin_ch7_trails_sources.py` for
   `ch7_trails_source_hashes.json`, with the key list fixed to the keys
   already present and a refusal to write if any protected file is missing.
6. Re-ran `evaluate_ch7_loop_detection.py` to clear the single verifier FAIL.
   The FAIL was the script's own stale self-hash inside
   `loop_detection.json`; re-running regenerated the file with every count
   identical and only that hash changed. Nothing was relaxed.
7. Ran `compose_unity_trajectories.py` and `validate_ch7_trails_revision.py`
   before re-pinning, so the failures and their exact mismatches are on the
   record above rather than being pre-empted.
8. Left `figures/ch7_trails_view.json` and `figures/ch7_handover_view.json`
   untouched. The captures were rendered from them and their manifests pin
   `view_config_sha256`; regenerating them would invalidate the archives.

## 9. Escalations

1. **`validate_ch7_trails_revision.py` still exits 1, on a pre-existing check
   unrelated to the re-run.** After all hash, manifest and phase checks pass,
   it asserts that `ch7_fig_rail_traj.png`, `ch7_fig_wrist_traj.png`,
   `ch7_fig_combined.png` and `ch7_fig_unity_trails.png` are embedded
   byte-for-byte in `Chapter_7_Evaluation.docx` and `Thesis_V9.docx`. The
   restructured Chapter 7 embeds none of them: `build_ch7.py` uses
   `ch7_failure_context.png`, `ch7_natural_proxy_left/right.png`,
   `ch7_object_waypoints_r6b/r7.png`, `ch7_unity_trajectories_r6b/r7.png`,
   `ch7_video_context_r6b/r7.png` and `ch7_visual_examples_r6b/r7.png`. The
   identical failure on the identical figure is already recorded for V8 in
   `writing/v9/audit_evidence/remove_intermediate_frame/legacy_validate_trails.txt`,
   and `ch7_fig_rail_traj.png` is byte-identical to its committed version, so
   this is a stale assertion against a superseded figure set, not a
   consequence of E-037. It was not loosened, and the assertion list was not
   edited. Deciding whether the validator's docx-embedding check should name
   the restructured figures, or be retired, is an author decision.
2. **Figure 7.5's caption states a capture date that no longer matches its
   sources.** `build_ch7.py` line 407 reads "The visualization capture was
   made on 7 September 2026", but Figure 7.5's three r6b stills are now the
   E-037 capture of 14 September 2026, as
   `ch7_visual_examples_sources.json` and
   `figures/src/r6b_unity_sensor/rig_sizing_used.txt` record. The builder's
   own header note covers Figure 7.6's caption ("Figure 7.6 keeps its caption
   by the author's decision") but says nothing about Figure 7.5's date. Ch7
   prose is out of scope for this regeneration, so nothing was changed. The
   author must decide the wording.
3. **Two r7 evidence pins in `ch7_visual_examples_sources.json` are stale and
   were deliberately left stale.** `writing/v9/scripts/make_ch7_handover_frames.py`
   (pinned d6cbd031..., actual 3048e58f...) and
   `writing/v9/figures/src/ch7_handover_trails/editor.log`
   (pinned 9959377c..., actual 3c73edfb...). The second is the direct
   consequence of E-037: the handover presentation re-run overwrote that
   editor log, so the r7 provenance now names a file whose content has
   changed. Because Figure 7.6 keeps its old sources and pins by author
   decision, and because the generator asserts only the row images (never the
   evidence list), both were reported rather than re-pinned. All six r7 row
   images do still hash as pinned, so Figure 7.6 itself is intact.
4. **Three evidence files carried stale self-hashes before this regeneration.**
   `object_provenance.json`, `spatial_check.json` and `loop_detection.json`
   each recorded an older sha256 of their own generating script while the
   committed scripts had moved on, so the committed evidence did not match the
   committed code. Re-running fixed all three with no numeric change, but the
   gap means those three files were committed without a matching re-run at
   some earlier point.
5. **No frame-matched control exists for the old-against-new comparison.**
   `compare_captures_v8_v9.py` states this itself: the V8 and V9 captures
   accept different frame subsets (r6b 485 against 487, r7 934 against 938),
   so each changed statistic mixes the corrected rig with a different subset.
   The r6b elbow median improvement from 10.66 to 6.41 cm is large enough
   that the rig change plainly dominates, but the individual r7 changes of a
   few tenths of a centimetre cannot be attributed to the rig alone. E-037
   records that a matched-frame control re-run of the old configuration was
   not requested. No causal claim was written into any evidence file here.

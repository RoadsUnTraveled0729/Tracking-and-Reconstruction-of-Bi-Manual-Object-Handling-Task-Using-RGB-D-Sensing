# mediapipe/ — Pipeline A, stage 1+2 (bag → landmarks CSV)

Reads a RealSense `.bag` recording offline and exports MediaPipe pose
landmark positions (camera-frame XYZ, meters) to one CSV row per frame.

## How it works
1. `pyrealsense2` plays the bag back as a device (`set_real_time(False)`,
   so it runs as fast as possible, not paced to 30 fps).
2. Every frameset is aligned depth→color; color intrinsics are read once.
3. MediaPipe **PoseLandmarker** (tasks API, VIDEO running mode) detects the
   person on each color frame.
4. Each in-scope landmark's normalized (x, y) is scaled to pixels, depth is
   sampled at that pixel from the aligned depth frame, and the point is
   deprojected through the color intrinsics
   (`rs2_deproject_pixel_to_point`, handles the distortion model) into
   camera-frame XYZ in meters (X right, Y down, Z forward).

**No smoothing/filtering** — base variant exports raw values only.
(The ENSC498 reference applied a One-Euro filter here; deliberately omitted.)

Inference runs on the **GPU delegate by default on Linux** (falls back to CPU
if GPU init fails; `--delegate cpu|gpu|auto` to override). Measured on the
RTX 3080: ~112 fps with the heavy model vs ~27 fps on CPU.

## Usage
```bash
python extract_landmarks_to_csv.py --bag ../Video/recording_20260328_021733.bag
# options:
#   --model lite|full|heavy|<path.task>   default: heavy
#   --delegate cpu|gpu                    default: cpu
#   --landmarks 11 12 ...                 default: 11 12 13 14 15 16 23 24
#   --max-frames N                        smoke tests
#   --out <path.csv>                      default: output/<bag-stem>_landmarks.csv
```

## Output
- `output/<bag-stem>_landmarks_raw.csv` — columns: `frame`, `time_s` (relative,
  from bag timestamps), `has_pose`, then per landmark
  `<name>_x/_y/_z` (meters, camera frame) and `<name>_vis` (MediaPipe
  visibility 0–1). XYZ cells are **empty** when the pixel had no valid depth
  or fell outside the image; every frame gets a row regardless, so frame
  indexing stays aligned across pipeline stages.
- `output/<bag-stem>_landmarks_raw.meta.json` — source bag, model, landmark
  map, color intrinsics (needed later for coordinate conversion), frame counts.

## Glitch filtering (separate stage, separate CSV)
`filter_landmarks.py` reads the raw CSV and writes
`<bag-stem>_landmarks_filtered.csv` — the raw file is never modified, so the
strict baseline stays available. Three configurable steps per landmark:
1. **Despike (Hampel)** — deviation from the centered rolling median beyond
   `max(0.02 m, 3 × 1.4826 × MAD)` on any axis is a glitch (MAD term adapts
   to genuine motion speed, so fast movement isn't flagged).
2. **Gap fill** — NaN runs ≤ `--max-gap` frames (default 5) linearly
   interpolated over time; longer gaps stay empty.
3. **Smooth** — method selectable via `--smooth butter|savgol|median|oneeuro|none`,
   applied per contiguous valid segment. Default is a **zero-phase Butterworth
   low-pass, 3 Hz cutoff, order 4** (`--cutoff-hz` to adjust).

   Measured on recording_20260328_021733 (shake = mean RMS frame-to-frame
   displacement; fidelity = mean deviation from despiked raw during fast
   wrist motion):

   | method        | shake (mm) | fast-motion deviation (mm) |
   |---------------|-----------:|---------------------------:|
   | raw           | 10.2       | —                           |
   | savgol 9/2    | 2.8        | 4.8                         |
   | median 9      | 2.9        | 3.9                         |
   | butter 3 Hz   | 1.9        | 4.8                         |
   | butter 2 Hz   | 1.5        | 5.3                         |
   | one-euro      | 1.1        | 28.4 (causal lag)           |

   Butterworth at 3 Hz was chosen: ~5x less shake than raw at the same
   motion fidelity as SavGol. One-Euro looks smoothest but trails genuine
   motion by ~28 mm — it stays available (`--smooth oneeuro`) as the
   real-time preview since causal filtering is what variant 3 will require.
   Zero-phase methods are valid only because this stage is offline.

Each landmark gets a `_flag` column (0 raw, 1 glitch-interpolated,
2 missing-interpolated, 3 missing) and per-landmark stats land in the meta
JSON. `--plot` writes a raw-vs-filtered QC PNG.
```bash
python filter_landmarks.py --plot            # newest *_raw.csv in output/
```

## Performance / real-time readiness (profiled 2026-07-12, RTX 3080)
Median per-frame cost with the heavy model: **8.8 ms total → 113 fps ceiling**
(MediaPipe GPU inference 6.5 ms / 73%, depth-to-color align 2.2 ms / 25%
CPU-bound in librealsense, everything else < 0.2 ms). A 30 fps real-time loop
has a 33 ms budget, so compute already fits with ~4x headroom; the extractor
also streams rows straight to disk (O(1) memory in recording length). If the
budget ever tightens: a CUDA-built librealsense offloads align, and the lite
model cuts inference ~3x. No further GPU offload is worthwhile now — the
remaining CPU work is smaller than the GPU transfer overhead it would incur.

## Skeleton animation viewer
`plot_skeleton.py` plays the CSV back as a 3D matplotlib skeleton
(blue = left side, red = right side, grey = torso). It consumes the CSV,
not the bag, so it stays decoupled from extraction.
```bash
python plot_skeleton.py                                  # newest CSV, interactive window
python plot_skeleton.py --csv output/foo_landmarks.csv --save output/foo.mp4
python plot_skeleton.py --step 3 --speed 2               # lighter playback
```
Camera-frame coords are remapped for viewing (plot up = −Y) so the person
stands upright; axis limits are fixed over the clip with equal aspect.

## Notes
- Do **not** add an `__init__.py` to this directory — as a plain directory it
  cannot shadow the installed `mediapipe` package, but making it a regular
  package would.
- `models/` (gitignored) holds the `.task` files; they are auto-downloaded
  if missing.

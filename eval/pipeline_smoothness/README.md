# Film vs live path: where the roughness comes from

Investigation, 2026-09-24. Question from the author: the defence films on
pages 13-16 of presentation/defense_2026 look smooth, but the live v1
pipeline (MediaPipe -> filter -> shared memory -> Unity avatar) looks
rougher. Which stage introduces the roughness? Right arm only; pages 16
(right_elbow, source frames 180-540) and 14 (180042, frames 3-109).

STATUS: done (offline stages measured; the Unity render stage was not measured)

GOAL: Compare the film angle series with the live-path angle series on the
same source frames and locate the stage where they diverge.

KEY FINDING: The per-frame landmarks (MediaPipe plus depth lookup and
visibility gate) are identical in the film and the live path, and they are
rough. The two paths diverge only at the filter: the film's offline
zero-phase Butterworth leaves 2.5 to 4.9 times less frame-to-frame jitter
(second-difference RMS) than the live causal filter, and the film is then
played at half speed. Shared memory and the merger add nothing measurable.

VERIFIED:
- No live log covers either recording. The only ArmAngleLogger output
  (v1/kinematics/output/unity_frame_log.csv, copy in
  v1/kinematics/dataset/real_20260224/) is recording_20260224_083945, and
  the pinned live dumps in v1/realtime/dataset/ are the same recording.
- The replay reproduces the film's input: replay raw landmarks vs the film's
  landmarks_raw.csv differ by at most 5.0e-7 m (CSV rounding), 0 gating
  mismatches, both pages (checks.json). Bag sha256 equals the film's
  source_manifest.json binding for both bags.
- The live solver reproduces the film angles from the film's filtered
  landmarks to 5e-10 deg (checks.json), so both paths use one convention.
- realtime_person.py run unmodified (paced, GPU) wrote the same right-arm
  angles as the GPU replay to 4.9e-7 deg, with 0 dropped frames on both
  bags (checks.json).
- The paced loop delivers frames at 30.00 fps, interval standard deviation
  2.1 ms, maximum 47.6 ms (timing_paced.csv).

ASSUMPTIONS-UNRESOLVED:
- Unity rendering: IntegratedSceneReceiver.Update applies the latest packet
  with no interpolation or smoothing (code read, lines 545-553); the merger
  passes the 13 angles through unchanged (realtime_integrate.py). The Unity
  frame rate and its beat against the 30 Hz packets were not measured.
- Whether the second-difference metric matches what the author perceives
  has not been checked (DECISIONS.md PS-003).
- The live run the author watched is assumed to be v1/realtime with the
  default GPU delegate. The V3 track has its own live path; it was not
  examined.

DECISION: Replay offline with the frozen v1 live objects imported
unchanged, CPU delegate as the primary series so MediaPipe output equals
the film's (PS-001); GPU, paced GPU and the unmodified dump reported beside
it. Alignment choices and metrics: DECISIONS.md PS-002 to PS-007.

NEXT: If the author wants the live avatar closer to the films, the lever is
the live filter (One-Euro min_cutoff and beta, and the causal Hampel
floor), not transport or Unity. Measuring the Unity render cadence would
need a capture with a frame-time log.

## Reason

The film producer (presentation/defense_2026/anim/bank_axes_kinematics.py)
reads landmarks from an offline extraction that ran MediaPipe on every bag
frame, then applies v1/mediapipe/filter_landmarks.py: centered Hampel,
gap interpolation and a 3 Hz Butterworth run forwards and backwards
(zero-phase). The live loop (v1/realtime/person/realtime_person.py) runs the
same MediaPipe call and the same deproject_landmarks gate, then a causal
filter (trailing Hampel whose rejections become missing samples that the
solver holds, then One-Euro min_cutoff 1 Hz, beta 1), then
ChainFallbackSolver, then shared memory. A causal filter cannot look ahead,
so it removes less jitter and adds delay; the offline filter can do both
without delay.

## Evidence

Stages of the live-side series (all right arm, degrees):

| series | stages included |
| --- | --- |
| film | offline extraction, centered Hampel, interpolation, Butterworth 3 Hz zero-phase, solver |
| raw_gated | MediaPipe CPU, visibility gate, 5x5 median depth, solver (no filter) |
| despiked | raw_gated after the live causal Hampel (rejects held) |
| live_cpu | full live CausalLandmarkFilter and ChainFallbackSolver, MediaPipe CPU: the values that would be written to PSR1 |
| live_gpu | same with the GPU delegate (live default); equal to the unmodified realtime_person.py dump |
| oneeuro_only | diagnostic, not a live stage: One-Euro without the Hampel |

Not included: the merger (pass-through by code read), Unity receive timing,
retargeting and rendering.

Alignment: replays by bag frame index (every frame processed once);
unmodified dump by bag timestamp within half a frame (PS-002). Page 16:
361 frames (180-540). Page 14: 107 frames (3-109).

Page 16, right_elbow, frames 180-540 (metrics.csv):

| angle | series | mean abs diff to film | max abs diff | best lag (frames) | delta std | 2nd-diff RMS | held (live) / repaired (film) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| el_y | film | - | - | - | 0.734 | 0.162 | 20 |
| el_y | raw_gated | 1.080 | 4.556 | 0 | 2.210 | 3.517 | 0 |
| el_y | live_cpu | 1.471 | 13.250 | 3 | 0.789 | 0.470 | 7 |
| el_y | live_gpu | 2.177 | 11.009 | 3 | 0.867 | 0.741 | 9 |
| el_y | oneeuro_only | 1.321 | 7.070 | 3 | 0.733 | 0.441 | 0 |
| sh_y | film | - | - | - | 0.725 | 0.333 | 20 |
| sh_y | raw_gated | 3.311 | 14.526 | 0 | 6.579 | 11.373 | 0 |
| sh_y | live_cpu | 1.472 | 6.338 | 2 | 0.913 | 1.333 | 0 |
| sh_y | live_gpu | 2.738 | 7.850 | 3 | 0.914 | 1.324 | 3 |
| sh_z | film | - | - | - | 0.211 | 0.072 | 20 |
| sh_z | raw_gated | 0.488 | 2.499 | 0 | 0.948 | 1.530 | 0 |
| sh_z | live_cpu | 0.452 | 2.202 | 3 | 0.193 | 0.180 | 0 |
| sh_z | live_gpu | 0.827 | 2.917 | 4 | 0.209 | 0.223 | 3 |
| sh_twist | film | - | - | - | 2.659 | 1.447 | 20 |
| sh_twist | raw_gated | 4.830 | 50.956 | 0 | 15.569 | 25.725 | 0 |
| sh_twist | live_cpu | 2.498 | 27.899 | 2 | 2.684 | 3.624 | 7 |
| sh_twist | live_gpu | 4.159 | 40.509 | 1 | 2.404 | 3.138 | 9 |

el_z is 0 in every series (the solver sets ez to 0 by construction,
v1/kinematics/shoulder.py), so it is in metrics.csv but not plotted.

Page 14, 180042, frames 3-109:

| angle | series | mean abs diff to film | max abs diff | best lag | delta std | 2nd-diff RMS | held / repaired |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| sh_y | film | - | - | - | 2.610 | 1.174 | 40 |
| sh_y | raw_gated | 11.974 | 43.457 | 1 | 24.416 | 42.188 | 0 |
| sh_y | live_cpu | 6.257 | 21.167 | 3 | 3.333 | 4.874 | 26 |
| sh_y | live_gpu | 5.995 | 20.572 | 3 | 3.433 | 5.188 | 18 |
| sh_z | film | - | - | - | 1.747 | 0.365 | 40 |
| sh_z | raw_gated | 3.061 | 11.514 | 0 | 6.304 | 10.761 | 0 |
| sh_z | live_cpu | 5.004 | 19.358 | 4 | 1.993 | 1.606 | 26 |
| sh_z | live_gpu | 4.480 | 13.923 | 3 | 1.957 | 1.478 | 18 |
| sh_twist | film | - | - | - | 9.087 | 4.736 | 40 |
| sh_twist | raw_gated | 34.232 | 136.483 | 1 | 62.869 | 105.979 | 2 |
| sh_twist | live_cpu | 23.302 | 75.998 | 3 | 15.073 | 23.285 | 47 |
| sh_twist | live_gpu | 17.861 | 61.943 | 2 | 13.684 | 20.246 | 40 |
| el_y | film | - | - | - | 1.534 | 0.958 | 40 |
| el_y | raw_gated | 8.995 | 45.416 | -1 | 15.474 | 26.627 | 2 |
| el_y | live_cpu | 4.038 | 13.572 | 3 | 3.341 | 4.680 | 47 |
| el_y | live_gpu | 5.533 | 22.786 | 5 | 3.467 | 5.032 | 40 |

Dropouts and rejections inside the windows (checks.json): page 16, no
gated right-chain landmark; the live causal Hampel rejected right_wrist on
7 frames (187, 189-191, 463-465) and left_hip on 2; the film's offline
filter repaired at least one required landmark on 20 frames. Page 14:
right_wrist gated on 2 frames; the live Hampel rejected right_wrist 26,
right_elbow 22, right_shoulder 7, left_hip 9, right_hip 4 frames; the film
repaired 40 frames. Each live rejection becomes a hold, then a jump when
the landmark is accepted again: page 16 el_y reaches 13.3 deg from the
film around frames 187-197 against 7.1 deg without the Hampel
(oneeuro_only); plots/p16_el_y.png and plots/p14_sh_y.png show the steps.

MediaPipe delegate: GPU vs CPU raw landmarks of the right chain differ by
up to 0.039 m on page 16 and 0.174 m on page 14. The GPU series is further
from the film but not rougher (delta std and second-difference RMS within
the same range as live_cpu).

Frame delivery of the paced loop (timing_paced.csv): 899 and 1050 frames,
0 dropped; mean interval 33.33 ms against 33.36 ms in the bag; standard
deviation 2.12 and 2.10 ms; 5th-95th percentile 32.4-34.3 and 31.8-35.1
ms; maximum 47.6 and 46.9 ms; delivered span 29.93 s for a 29.96 s
recording. realtime_person.py prints "899 frames in 35.0 s (25.7 fps
sustained)" (data/p16_right_elbow_live_paced.log; 1050 in 40.0 s on page
14); the extra 5.0 s matches the 5000 ms wait_for_frames timeout at the
end of the bag, so the 25.7 fps figure in v1/realtime/REALTIME.md is most
likely that timeout, not playback pacing. This explanation is inferred
from the timing, not traced in librealsense.

Half speed (half_speed.csv; film mapping from the provenance JSON, 2 s
holds removed): each source frame is shown on two screen frames, so half
the screen frames carry no change (361 of 721 on page 16, 107 of 213 on
page 14) and the mean change per screen frame is half the source-rate
value; the largest single step is unchanged.

| page | angle | source deg per frame (mean abs) | film deg per screen frame (mean abs) | source deg/s at 30 fps | film deg/s on screen | largest step (both) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 16 | el_y | 0.478 | 0.239 | 14.35 | 7.16 | 2.666 |
| 16 | sh_y | 0.573 | 0.286 | 17.20 | 8.59 | 2.075 |
| 16 | sh_twist | 1.153 | 0.576 | 34.59 | 17.27 | 16.928 |
| 14 | sh_y | 2.181 | 1.086 | 65.44 | 32.57 | 6.558 |
| 14 | el_y | 1.212 | 0.603 | 36.37 | 18.10 | 5.176 |

The live avatar runs at source rate, so with the live path's own series it
shows 0.473 deg per screen frame on page 16 el_y (live_cpu) against the
film's 0.239.

## Therefore

The roughness is introduced by the landmark stage (MediaPipe per-frame
output with the depth lookup) and is present in both paths: before any
filter, the angle series are 3 to 16 times rougher than the film by
second-difference RMS (e.g. page 16 sh_y 11.37 vs 0.33 deg). The film and
the live path diverge at the filter. The live causal filter removes most
of it but leaves 2.5 to 4.9 times the film's second-difference RMS (page
16: el_y 0.47 vs 0.16, sh_y 1.33 vs 0.33, sh_z 0.18 vs 0.07, sh_twist 3.62
vs 1.45; page 14: 4.2 to 4.9 times), adds a 2 to 4 frame lag, and its
causal Hampel turns rejected samples into hold-then-jump steps. Almost all
of the residual jitter comes from the One-Euro half (oneeuro_only is within
10 percent of live_cpu on second-difference RMS on page 16 and 3 to 20
percent on page 14); the Hampel half adds the steps. On the brief's delta
standard deviation the gap is smaller (page 16 ratios 0.91 to 1.26, page 14
1.14 to 2.18), because that metric is dominated by real motion. Half-speed
playback then halves the film's per-screen-frame change. Transport adds
nothing (the unmodified dump equals the replay, 0 dropped frames, 2.1 ms
interval jitter). Confidence: high that the divergence is at the filter
and that transport is clean, since both are measured on identical inputs;
the Unity render stage was not measured and could add judder on top.

## Files

- replay_live_person.py: deterministic (or --paced) replay of the v1 live
  person objects, logging raw and filtered landmarks and the 13 angles.
- compare_film_vs_live.py: builds all series, metrics and plots.
- series_p16.csv, series_p14.csv: per-frame angle series, every stage.
- metrics.csv, half_speed.csv, timing_paced.csv, checks.json: results.
- plots/pNN_<angle>.png: film, live and raw series, and differences.
- data/: replay CSVs with .meta.json, unmodified live dumps and logs.
- DECISIONS.md: PS-001 to PS-007.

## Reproduce

```bash
cd eval/pipeline_smoothness
B=/home/luo/Desktop/ENSC498/recordings
PY=/home/luo/anaconda3/bin/python
E=$B/ENSC498_right_elbow_bend_test_right_elbow.bag
R=$B/ENSC498_right_arm_raise_cube_untouched_test_20260121_180042.bag
$PY replay_live_person.py --bag $E --out data/p16_right_elbow_replay_cpu.csv --delegate cpu
$PY replay_live_person.py --bag $E --out data/p16_right_elbow_replay_gpu.csv --delegate gpu
$PY replay_live_person.py --bag $E --out data/p16_right_elbow_replay_gpu_paced.csv --delegate gpu --paced
$PY replay_live_person.py --bag $R --out data/p14_180042_replay_cpu.csv --delegate cpu
$PY replay_live_person.py --bag $R --out data/p14_180042_replay_gpu.csv --delegate gpu
$PY replay_live_person.py --bag $R --out data/p14_180042_replay_gpu_paced.csv --delegate gpu --paced
# unmodified live loop; shared memory goes to a scratch path, not /dev/shm
PYTHONDONTWRITEBYTECODE=1 $PY ../../v1/realtime/person/realtime_person.py --bag $E \
    --shm /tmp/rt_person_p16 --dump-csv data/p16_right_elbow_live_paced_dump.csv --profile
PYTHONDONTWRITEBYTECODE=1 $PY ../../v1/realtime/person/realtime_person.py --bag $R \
    --shm /tmp/rt_person_p14 --dump-csv data/p14_180042_live_paced_dump.csv --profile
$PY compare_film_vs_live.py
```

Run time on this machine: about 40 s per CPU replay, 14 s per GPU replay,
30-40 s per paced run.

# Filter metrics: offline and causal smoothers on the R6b right wrist

Currency note (2026-10-08): This is a retained benchmark with pinned
recording inputs, settings and result files. Page numbers 47 and 48 refer
to its original 2026-09-28 deck, not the final delivery. Measurements and
reproduction commands below keep their original conditions; no benchmark
was rerun for this currency update. Current slide navigation is in
[the presentation README](../../README.md).

Decisions: presentation/defense_2026/DECISIONS.md D-160 to D-168

## Purpose

Measured backing for two Q&A slides, "Why Butterworth offline" (page 47)
and "Why One Euro in real time" (page 48). The thesis (Section 2.5,
Appendix F, Chapter 8) defines the filters; this folder measures how they
behave on one pinned recording, so every number on those slides comes from
a committed script run on committed data.

## Command

    /home/luo/anaconda3/bin/python presentation/defense_2026/experiments/filter_metrics/filter_metrics.py

Runtime is a few seconds. `--no-charts` writes the tables only. Two
consecutive runs give byte-identical results.csv, summary.csv,
run_info.json and PNG files (sha256 checked on 2026-09-28).

## Inputs (read only, sha256-checked against FILTER_DEMO_BRIEF.json)

- `presentation/defense_2026/media/provenance/filter_demo_raw_r6b.csv`
  (R6b, 900 frames, 29.979 Hz from the median time step).
- `v1/mediapipe/filter_landmarks.py` (frozen V1 functions: hampel_mask,
  fill_gaps, smooth_landmark, OneEuro), loaded by path, never edited.
- The script also imports `presentation/defense_2026/anim/filter_demos.py`
  and asserts that the frozen smoothers, applied to the raw valid runs,
  reproduce the film data exactly (max error 0.0 m), so the settings match
  the filter films.

## Method

1. Despiked baseline, common to all candidates: Hampel (window 7, k 3,
   floor 0.02 m; flags frames 36, 537, 760), then linear gap fill up to 5
   frames. This is "despiked raw" below.
2. Each candidate runs per contiguous valid segment of that baseline.
3. Metrics use the two segments longer than 15 frames (frames 25-549 and
   640-899, 785 frames, 783 frame-to-frame steps). Definitions are in
   presentation/defense_2026/DECISIONS.md D-160 to D-163:
   - shake: RMS frame-to-frame displacement of the filtered signal;
   - fast-motion deviation: RMS of filtered minus despiked raw on the 157
     frames whose despiked-raw 3-D speed is at or above the 80th percentile
     (0.138 m/s);
   - lag: the shift in -15..15 frames that maximises the normalised
     cross-correlation with despiked raw (positive = filtered output late),
     integer and parabola-refined; ms = frames x 33.357 ms.

Candidates: despiked raw; Savitzky-Golay 9/2; median 9; Butterworth 4th
order 3 Hz filtfilt (chosen offline); Butterworth 4th order 2 Hz filtfilt;
Butterworth 4th order 3 Hz forward only (causal); One Euro min cutoff
0.05 Hz, beta 1 (Appendix F, the films); One Euro min cutoff 1 Hz, beta 1
(the live filter measured in eval/pipeline_smoothness); EMA alpha 0.3.

## Outputs

| File | Content |
| --- | --- |
| results.csv | one row per candidate x axis (x, y, z, norm): mode, shake_mm, fast_deviation_mm, lag_frames, lag_frames_subframe, lag_ms and lag_ms_subframe (causal only), xcorr_peak |
| summary.csv | the norm rows of results.csv (3-D displacement for shake and deviation, all three axes pooled for lag) |
| run_info.json | input hashes, flagged and filled frames, evaluated segments, speed threshold, excerpt window, film-replay check |
| chart_filter_offline.png | page 47 chart, 2466x1110 px |
| chart_filter_realtime.png | page 48 chart, 2466x1110 px |
| filter_metrics.py, charts.py | the computation and the plotting |
| SLIDE_TEXT.md | titles, claims, source lines and speaker notes for pages 47 and 48 |

## Results (summary.csv, 3-D norm, R6b right wrist, 785 frames)

- Despiked raw: shake 6.38 mm.
- Offline, all lag 0 frames: Butterworth 3 Hz shake 2.86 mm, deviation 6.53 mm; Savitzky-Golay 9/2 3.29 / 5.64 mm; median 9 3.51 / 7.49 mm; Butterworth 2 Hz 2.54 / 7.73 mm.
- Butterworth 3 Hz has the lowest shake of the 9-frame and 3 Hz candidates; Savitzky-Golay stays closest to fast motion; median is worse than Butterworth 3 Hz on both metrics.
- Causal, shake / lag: Butterworth 3 Hz forward 2.88 mm / 142.28 ms; One Euro 1 Hz 2.48 mm / 85.39 ms; One Euro 0.05 Hz 2.08 mm / 186.79 ms; EMA 0.3 2.86 mm / 54.89 ms.
- Causal fast-motion deviation grows with lag: EMA 11.68, One Euro 1 Hz 14.68, Butterworth forward 20.50, One Euro 0.05 Hz 23.77 mm.
- One Euro 1 Hz and EMA 0.3 both beat the causal Butterworth on shake and lag; One Euro 1 Hz has the lower shake of the two (2.48 against 2.86 mm), EMA the lower lag.

Comparison with the prose table in thesis/A1_acquisition_filtering.md
(lines 169-176, no script): the values DIFFER. Shake, prose vs here: raw
10.2 vs 6.38, Savitzky-Golay 2.8 vs 3.29, median 2.9 vs 3.51, Butterworth
3 Hz 1.9 vs 2.86, Butterworth 2 Hz 1.5 vs 2.54, One Euro 1.1 vs 2.08
(0.05 Hz setting). Deviation, prose vs here: Savitzky-Golay 4.8 vs 5.64,
median 3.9 vs 7.49, Butterworth 3 Hz 4.8 vs 6.53, Butterworth 2 Hz 5.3 vs
7.73, One Euro 28.4 vs 23.77. The shake ranking agrees (raw > median >
Savitzky-Golay > Butterworth 3 Hz > Butterworth 2 Hz > One Euro); the
deviation ranking does not (prose: median lowest; here: median highest of
the 9-frame and 3 Hz candidates). The prose data set, landmarks, speed
threshold and averaging are not recorded, so the cause of the difference
is not established. Do not quote the prose numbers.

Cross-check: eval/pipeline_smoothness/metrics.csv gives best lags of 2-3
frames for its One Euro 1 Hz series on joint angles; the 1 Hz candidate
here has an integer best lag of 3 frames on wrist position. Different
signals, same order of magnitude.

## Caveats

- One recording, one landmark, 26 s of evaluated data. Not a population
  result and not an accuracy result (there is no ground truth for the
  wrist here).
- Shake counts genuine motion as well as noise; a filter that lags or
  flattens motion lowers shake. Read shake together with deviation and lag.
- Causal deviation is dominated by lag, not by noise.
- Lag in ms is the parabola-refined cross-correlation peak; the integer
  lag column is the unrefined peak.
- The causal Butterworth is seeded at steady state on the first sample of
  each segment (scipy lfilter_zi), not with the filtfilt padding used in
  the films' forward-pass animation.

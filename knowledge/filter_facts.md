Current scope note (verified 2026-10-08): the benchmark scripts and
pinned outputs described below remain in the repository. Defence page
numbers in the round-4/round-5 descriptions refer to the retired
generated deck, not the final author deck adopted on 2026-10-06. Use
[deck_inventory.md](deck_inventory.md) and the
[presentation README](../presentation/defense_2026/README.md) for current
slide pointers. Benchmark measurements and their original conditions
are preserved; they were not rerun for this documentation correction.

Verified: 2026-09-28 (round-4 update)
Sources: v1/mediapipe/filter_landmarks.py, presentation/defense_2026/FILTER_SYNC_BRIEF.json, thesis/A1_acquisition_filtering.md, eval/pipeline_smoothness/metrics.csv, eval/pipeline_smoothness/DECISIONS.md, eval/pipeline_smoothness/README.md, writing/v9/zh/src/Chapter_8_Real_Time_Feasibility.txt, writing/v9/figures/appF_fig_filters.png, writing/v7/scripts/make_appF_fig.py, presentation/defense_2026/experiments/filter_metrics/{README.md,summary.csv,results.csv}
Answers: the filter chain and its frozen settings, where each numeric filter comparison actually lives, and which of those comparisons is NOT reproducible from a script.

## Round-5 update (verified 2026-09-28)

The deck now shows each filter's equation, typeset from the frozen
code (equations/typeset_catalog.json cites function and line per key):
Hampel threshold max(0.02 m, 3 x 1.4826 MAD) over a centred 7-frame
window, the MAD being the rolling median of each sample's own residual
(line 60); gap fill linear in time, interior gaps <= 5 frames;
Butterworth analog magnitude, order 4, 3 Hz, applied by filtfilt;
Savitzky-Golay 9-tap quadratic; median 9; One Euro with the speed
taken against the previous filtered value (line 117), f_min 0.05 Hz
offline and 1 Hz live, beta 1. Pages 42-49; D-190 to D-198.

## Round-4 update: a reproducible comparison now exists (2026-09-28)

`presentation/defense_2026/experiments/filter_metrics/` (D-160 to
D-168) is a committed script (`filter_metrics.py`) that measures
shake, fast-motion deviation and lag for nine candidate
filters/smoothers (despiked raw, Savitzky-Golay 9/2, median 9,
offline Butterworth 3 Hz and 2 Hz filtfilt, causal Butterworth 3 Hz
forward-only, One Euro at two parameter sets, EMA 0.3) on the R6b
right wrist, 785 evaluated frames. Its `summary.csv` (norm/3-D rows)
and `results.csv` (per-axis rows) are the new reproducible numbers;
see the Results table in experiments/filter_metrics/README.md and
knowledge/experiments.md. These numbers DIFFER from the item 1 prose
table below (for example shake: raw 6.38 mm here vs 10.2 mm in the
prose table; Butterworth 3 Hz 2.86 mm here vs 1.9 mm in the prose
table) and the ranking of deviation does not agree between the two.
The prose table's data set, landmarks, speed threshold and averaging
are not recorded, so the cause of the difference is not established
(filter_metrics/README.md, "Comparison with the prose table").
**The prose table (item 1 below) is superseded for any claim that
needs a reproducible number; cite experiments/filter_metrics/
instead. The prose table remains the citable source only for the
thesis-published Chapter 8 offline-vs-causal alignment number (item
3 below), which the new script does not measure.**

## Chain

Offline pipeline: Hampel despike -> gap interpolation -> Butterworth
forward-backward smoothing (zero-phase, `filtfilt`). Real-time
pipeline: causal One Euro filter. Both implemented in the frozen
`v1/mediapipe/filter_landmarks.py` (smoothing options `butter`,
`savgol`, `median`, `oneeuro` and `none`; `hampel_mask` despiking and
gap handling are separate stages before smoothing, not selectable
smoothers).

## Settings (confirmed identically in FILTER_SYNC_BRIEF.json
## "parameters" and filter_landmarks.py argparse defaults)

| Stage | Setting | Value |
|---|---|---|
| Hampel | window / k / abs floor | 7 / 3.0 / 0.02 m |
| Gap interpolation | max_gap | 5 frames |
| Butterworth | order / cutoff | 4 / 3.0 Hz |
| Savitzky-Golay | window / order | 9 / 2 |
| One Euro (offline default, this file) | min cutoff / beta | 0.05 Hz / 1.0 |

See media_inventory.md for the six synchronized demo films these
settings drive (filter_*_sync.mp4).

Caution: the real-time/causal pipeline used for the Chapter 8
live-vs-offline comparison (`eval/pipeline_smoothness/`,
`CausalLandmarkFilter` in v1/realtime/person/realtime_person.py) uses
a DIFFERENT One Euro parameter set: min_cutoff 1.0 Hz, beta 1.0,
freq 30 (eval/pipeline_smoothness/DECISIONS.md line 55,
README.md line 68). Do not conflate this with the offline default of
0.05 Hz above; they are two different filter instances for two
different purposes (offline batch smoothing vs. live/causal
smoothing).

## Numeric comparisons and where they live

1. `thesis/A1_acquisition_filtering.md` lines 165-181: a shake and
   fast-motion-deviation table for raw / Savitzky-Golay 9,2 /
   rolling median 9 / Butterworth 3 Hz (chosen) / Butterworth 2 Hz /
   One-Euro. Example values: raw shake 10.2 mm; Butterworth 3 Hz
   shake 1.9 mm, fast-motion deviation 4.8 mm; One-Euro shake 1.1 mm
   but 28.4 mm fast-motion deviation (pure causal lag). THIS TABLE
   EXISTS ONLY AS PROSE IN THAT FILE -- there is no script that
   reproduces it. Do not quote it as a result from a runnable
   pipeline; it is a stated finding, not a re-derivable one. As of
   round 4 (2026-09-28), a reproducible comparison exists and gives
   DIFFERENT numbers -- see "Round-4 update" above and
   presentation/defense_2026/experiments/filter_metrics/.

2. `eval/pipeline_smoothness/metrics.csv`: the real numeric
   comparison of offline vs. live jitter and best lag, per page,
   angle and series (film / raw_gated / despiked / live_cpu /
   live_gpu / live_dump / oneeuro_only), with columns
   delta_std_deg, delta_mean_abs_deg, d2_rms_deg,
   held_or_repaired_frames, mean_abs_diff_vs_film_deg,
   max_abs_diff_vs_film_deg, best_lag_frames,
   mean_abs_diff_at_best_lag_deg. This one IS backed by a script
   (`eval/pipeline_smoothness/replay_live_person.py`) and is the
   live One Euro min cutoff 1 Hz, beta 1 instance described above.

3. Chapter 8 offline-vs-causal comparison (thesis-published number,
   confirmed at writing/v9/zh/src/Chapter_8_Real_Time_Feasibility.txt
   line 40): best alignment 5 frames, 174 paired frames retained
   after the arm-clean gate; at that alignment the median difference
   between the causal and offline angle series is 0.4 deg elbow
   flexion, 1.4 deg shoulder elevation, 7.0 deg shoulder twist.

4. Appendix F figure: `writing/v9/figures/appF_fig_filters.png`,
   generated by `writing/v7/scripts/make_appF_fig.py` (both files
   confirmed to exist; the figure is carried forward from v7 into
   the v9 figures directory, not regenerated by a v9-tree script).

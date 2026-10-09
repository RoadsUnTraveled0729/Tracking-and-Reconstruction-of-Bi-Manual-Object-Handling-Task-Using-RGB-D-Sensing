# Decisions: film vs live-path smoothness (eval/pipeline_smoothness)

Log format per AGENTS.md. IDs are local to this folder (PS-nnn).

ID: PS-001
Status: SETTLED
Decision: The primary live-path series is an offline replay of the frozen v1 live person objects (replay_live_person.py) with playback set_real_time(False) and the MediaPipe CPU delegate; the GPU delegate, a paced GPU replay and the unmodified realtime_person.py dump are reported beside it.
Why: No live log exists for either recording (see README). A non-paced replay processes every bag frame once, so its frame index equals the film's source frame index, and the CPU delegate gives the same MediaPipe output as the film extraction (which ran on CPU), so any difference is downstream of MediaPipe.
Alternatives: Only the unmodified paced run (rejected as sole source: it logs no intermediate landmarks); GPU only (rejected as primary: its landmarks differ from the film's by up to 3.9 cm on page 16, which would confound the filter comparison).
Evidence: checks.json: replay raw landmarks vs film landmarks_raw.csv max 5.0e-7 m (CSV rounding), 0 missing-mask mismatches, both pages; unmodified dump vs GPU replay max 4.9e-7 deg on the right arm, 0 dropped frames; bag sha256 equal to the film source_manifest.json bindings.
Reversibility: Additive; all series are in series_p14.csv and series_p16.csv, so another series can be chosen as primary without re-running.
Review: Confirm that realtime_person.py with the GPU delegate is the configuration the author watched live.

ID: PS-002
Status: SETTLED
Decision: The unmodified live dump is aligned to bag frames by nearest bag timestamp, accepted when within half a frame (0.5/30 s).
Why: The dump numbers frames by processing count, not bag index; its time_s is computed from the bag timestamps exactly as the extractor computes them.
Alternatives: Align by processing count (rejected: would silently shift after any dropped frame).
Evidence: Measured bag interval 33.36 ms (timing_paced.csv); all 899 and 1050 dump rows aligned, 0 duplicates (checks.json).
Reversibility: One constant in compare_film_vs_live.py.
Review: None needed unless a run with dropped frames is analysed.

ID: PS-003
Status: UNCERTAIN
Decision: Roughness is reported with two metrics: the standard deviation of the frame-to-frame delta (asked for in the brief) and the RMS of the second difference (added).
Why: The delta standard deviation includes the real motion (a fast clean swing scores high), so on page 16 it barely separates a smooth from a jittery series; the second difference is near zero for smooth motion and grows with frame-to-frame jitter.
Alternatives: High-pass residual power (rejected: needs a cutoff choice with no source).
Evidence: metrics.csv; e.g. page 16 el_y: film vs live_cpu delta std 0.734 vs 0.789 deg, second-difference RMS 0.162 vs 0.470 deg; the plots show the jitter the second metric picks up.
Reversibility: Both are in metrics.csv.
Review: Whether the second-difference RMS matches what the author perceives as rough in the avatar has not been checked against a viewer judgement.

ID: PS-004
Status: SETTLED
Decision: The best-lag search covers integer shifts of -10..+10 source frames.
Why: The lag is reported to separate difference caused by causal delay from difference caused by noise.
Alternatives: None considered.
Evidence: v1/realtime/REALTIME.md reports a 3-frame live lag with the deployed One-Euro tuning and 9 frames with the earlier tuning; 10 covers both. Measured best lags here are -1..5 frames (metrics.csv), inside the range.
Reversibility: MAX_LAG in compare_film_vs_live.py.
Review: None.

ID: PS-005
Status: SETTLED
Decision: The half-speed numbers use the built film's own mapping (output_source_frames in committee_materials/unified_four/provenance/<stem>.json) with the first and last 60 screen frames removed.
Why: The 60 frames are the 2 s start and end holds at 30 fps, during which nothing moves.
Alternatives: Synthesise the 2x repetition (rejected: the provenance mapping is the ground truth of what was encoded).
Evidence: provenance JSON editorial fields playback_speed 0.5, start_hold_s 2, end_hold_s 2, fps 30; bank_axes_kinematics.py line 368 builds the mapping.
Reversibility: One slice in compare_film_vs_live.py.
Review: None.

ID: PS-006
Status: SETTLED
Decision: A diagnostic series oneeuro_only (raw landmarks through the live One-Euro settings, causal Hampel removed) is reported and labelled as not a live-path stage.
Why: It separates the two halves of CausalLandmarkFilter: whether the residual jitter comes from the One-Euro smoothing or from the Hampel hold-then-jump behaviour.
Alternatives: None.
Evidence: One-Euro parameters freq 30, min_cutoff 1.0, beta 1.0 are the CausalLandmarkFilter defaults in v1/realtime/person/realtime_person.py line 98.
Reversibility: Delete the series; nothing depends on it.
Review: None.

ID: PS-007
Status: SETTLED
Decision: Frame delivery timing of the paced live loop is measured with a monotonic wall clock in replay_live_person.py --paced, not in realtime_person.py.
Why: The unmodified script does not log wall time per frame and v1 is frozen; the paced replay uses the same set_real_time(True) playback and produces identical angles.
Alternatives: Patch realtime_person.py (forbidden: v1 frozen).
Evidence: checks.json paced_replay_vs_gpu_replay_max_abs_deg_right_arm 0.0 for both pages.
Reversibility: Additive.
Review: The timing is at the Python producer; Unity's own frame cadence was not measured.

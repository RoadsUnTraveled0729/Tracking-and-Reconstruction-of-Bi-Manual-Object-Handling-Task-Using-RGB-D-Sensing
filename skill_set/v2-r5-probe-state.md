# Current probe limits (2026-10-08)

The marker print is confirmed 45 mm, not awaiting a ruler measurement.
The offline chain retains the 0.050 m PnP declaration and applies a 0.9
translation scale before calibration ([AGENTS.md](../AGENTS.md)). The
known live-calibration mismatch, stale probe after E-027, missing loop
dumps and pending Unity visual check remain open
([v2 README](../v2/README.md)). V9 has been delivered and defended;
the V7 rewrite noted below is historical
([V9 README](../writing/v9/README.md)).

All following sections are dated probe records, including superseded
measurement and thesis tasks. Preserve their original outcomes and
report counts; the current flags-off validator emits 21 checks.

## Historical probe state
# v2 R5 real-time probe round: COMPLETE 2026-08-26

User pivot after the R5 freeze and the V7 TOC build: "more interested
in the v2 real-time probe" - a proof of concept that the rig model
runs in real time in a lightweight way, preserving as much of the
frozen R5 feature set as possible. Requirements honored: recording
first with the broker's `--source bag|live` switch keeping the sensor
path identical downstream of the frame ring; more permission than the
v1 freeze (not bound to the exact v1 transform chain) but MediaPipe +
ArUco pipeline kept; all new behavior opt-in (`--probe-r5` preset).

State: COMPLETE and committed. Every ported feature runs live on the
full R5 recording at 29.6 fps sustained (person p99 25.1 ms, recovery
cost ~0.06 ms/frame): E-011/E-011b/E-012 in the solver, E-014
object-conditioned recovery (B->A shm link + online grip tracker in
solver space, D6 live), E-019 plausibility gate in Pipeline B, E-018
smoother in the merger, solver tags through PSR2/PSI2 to Unity (blue
sphere = recovered). validate_v2_r5.py 13 checks ALL PASS; flags-off
regression validate_v2.py 22 checks ALL PASS.

Key docs: v2/reports/r5_realtime_probe.md (feature-preservation
matrix, measurements, sensor-switch checklist), .agent/DECISIONS.md
2026-08-26 section, evidence in v2/dataset/r5_probe_baseline.txt +
r5_probe_validation.txt.

Open items for the sensor round (--source live): live_calibrate.py
needs the true 45 mm marker sizes (same E-009 fix make_r5_calib.py
applies for the bag); marker ruler measurement still pending (E-009a);
grip tracker assumes the object starts at rest in view ~1 s.

Not yet done: Unity visual check of the probe stream (press Play
during a probe run) and the optional capture video; the thesis
rewrite round (V7 TOC built and committed, chapters not started - see
[[r5-experiment-state]] and [[thesis-structure-rules]]).

## Regression-count defect (found 2026-08-28 by the Ch8 review)

validate_v2.py emits 21 checks, not 22; docs corrected. Re-running it
on the dumps currently in v2/output (the --probe-r5 run, recovery on)
gives 15 PASS / 6 FAIL - the offline-agreement checks fail because
those dumps are not the flags-off run the ALL PASS claim was made on.
The flags-off ALL PASS is therefore NOT reproducible from disk today;
reproduce it with `python run_v2.py --source bag --dump` with all
probe flags off, then `validate_v2.py`, before anyone cites it. The
thesis (Ch8) no longer cites the regression suite. Second open
defect: r5_realtime_probe.md says "wrist from object 255 left, 19
right" while r5_probe_validation.txt says CONSTRAINED L 255 / R 125;
the thesis uses the validation-file numbers; settle by re-running
validate_v2_r5.py.

## Validity pairing corrected (2026-09-07, M03, E-028/E-030)

validate_v2_r5.py now pairs live frame f with reference frame f-lag and
requires both samples clean (the old code shifted rows under an
unshifted mask); v2/tests/test_validator_pairing.py holds six
regression tests. The corrected rerun on the archived original rail
dumps (v2/dataset/m03_rail_inputs.zip, rerun_m03_archive.py, report
m03_rail_corrected.json) gives lag 5, 174 pairs, worst group 3.90/23.25
degrees; the same two checks fail as before. The loop run's live dumps
were never archived, so its numbers cannot be corrected; Chapter 8 says
so. Any future live or replay run must archive its dumps beside the
report.

STALE NOTE (2026-09-08): still open as listed above plus: the v2 probe was never re-run after the E-027 torso gate; live_calibrate.py is hard-wired to the 50 mm declared marker size (v2/calibration/live_calibrate.py:194,218-220) while the printed size is 45 mm; the Unity visual check of the probe stream was never done; the undocumented v2/output/live_20260806.bag is unindexed and unreadable; .agent/DECISIONS.md is stale since 2026-08-26. Current plan: [[exploration-round-2026-09]] (milestones SB1, V2-1 to V2-4; the camera session with the subject is deferred by user decision).

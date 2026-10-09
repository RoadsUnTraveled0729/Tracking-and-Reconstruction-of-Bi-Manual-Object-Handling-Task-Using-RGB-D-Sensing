# v2: the genuinely live pipeline

## Purpose

v1 proves the method on a recording played at recorded pacing. v2
makes the same chain live end to end: a capture broker owns the one
physical device and publishes aligned frames to a shared-memory ring;
the person and object pipelines consume it concurrently; a
timestamp-paired delay buffer merges their outputs at a fixed,
declared latency, bridging short dropouts by interpolation between
measured samples and flagging everything it does. v1 code is imported
in place, never edited, so v2 inherits v1's validated math unchanged.

## Status

ACTIVE code track; development is paused. M0-M5 recording results are
pinned in v2/dataset/; physical-camera bring-up (M6, checklist in
[V2.md](V2.md)) remains unverified. The original recording validation
does not establish that later probe changes or live calibration are
correct on hardware. The corrected rail probe and remaining defects
are described under Limitations below.

R5 REAL-TIME PROBE (2026-08-26): the frozen R5 evaluation round's
feature set now runs live behind opt-in flags - object-conditioned
wrist recovery (E-014) via a B->A shared-memory link and an online
grip tracker, the E-019 object plausibility gate, the E-018 display
smoother in the merger, and the solver tags through to Unity (blue
sphere = recovered-from-object). Full R5 recording at recorded pacing:
29.6 fps sustained, person p99 25.1 ms, recovery cost ~0.06 ms/frame;
validate_v2_r5.py 13 checks ALL PASS, flags-off regression
validate_v2.py 21 checks ALL PASS on the flags-off dumps of 2026-08-26. Report:
v2/reports/r5_realtime_probe.md.

## Design decisions

Full reasoning in .agent/DECISIONS.md (thesis-track log):

- One capture broker + PSF1 frame ring, because two processes cannot
  open one camera; the ring sits below the A/B independence boundary
  like /dev/shm itself.
- Delay buffer at a declared 2-frame (66.7 ms) delay: measured at 1
  frame, about 7 percent of ticks missed their future bracket; at 2,
  mid-run holds vanish. Thesis section 8.3.3 sanctions 1-2 frames.
- Interpolation only between MEASURED samples, wrap-aware for angles
  and geodesic for object rotation; long gaps hold-last exactly like
  v1; reacquisition blends instead of snapping. Every non-measured
  tick is flagged in the packet.
- Held-object honesty: the "is the object live" judgment reads the
  newest packet at or before render time, so a future reacquisition
  can never claim liveness early.
- Prompt end-of-source detection (1 s timeout + playback status +
  miss counter): the earlier 5 s blocking wait inflated every
  sustained-fps figure.

## Results

Conditions: pinned recording (899 frames, 640x480 at 30 fps), full v2
stack (broker + A + B + merger), development machine. Evidence files
in v2/dataset/.

- Frame ring parity: 899/899 frames, probe checksums identical to a
  direct bag read, zero laps (m1_ring_parity.txt).
- Pipeline parity: v2 outputs equal the pinned v1 dumps exactly, zero
  angle or pose diffs (m2_pipeline_parity.txt).
- Merger: 22 validation checks ALL PASS; steady 30 Hz; v1's causal
  bounds reproduced exactly; 777 person + 740 object interpolated
  ticks recomputed exactly from their brackets; short dropouts
  bridged and flagged, long occlusions held with the object marked
  not-live (m3_validate_output.txt, m3_interp_plot.png).
- Live calibration dress rehearsal: reproduces the frozen offline
  calibration to 0.98 mm / 0.32 deg (m4_calibration_rehearsal.txt).
- What failed and was fixed en route (exit-tail artifact, epsilon in
  the olive rule, delay-1 held fraction) is recorded per decision in
  .agent/DECISIONS.md.

## Limitations

- The physical-camera path (M6) is untested against hardware; USB2
  downgrade is detected loudly but has never been provoked for real.
- [live_calibrate.py](calibration/live_calibrate.py) still uses the frozen
  0.050 m desk/object PnP declaration. The confirmed print is 45 mm;
  the offline thesis chain rescales translations by 0.9 before
  calibration ([standing rule](../AGENTS.md)). The live path has not
  received that correction, so its scale is not validated.
- The probe was not rerun after the E-027 torso gate. The corrected
  archived rail validation is 10/12 PASS, with two reported failures
  ([report](dataset/m03_rail_corrected.json)); the original loop live
  dumps were not archived, so their numbers cannot be corrected.
  [Probe state](../skill_set/v2-r5-probe-state.md) records these limits
  and the pending Unity visual check.
- The declared 66.7 ms output delay is a floor for interactive use.
- Default occlusion behavior is v1's hold-last plus honesty and
  bridging; the R5 probe flags add object-conditioned recovery for a
  holding hand (free-arm and torso failures still hold/repair).
- A true release keeps the wrist box-anchored for up to 5 frames
  before the grip episode closes (the online state machine cannot
  retro-clear release frames the way the offline one does).

## How to run and reproduce

    python v2/integration/run_v2.py --source bag --dump
    python v2/integration/validate_v2.py     # 21 checks; needs flags-off dumps in v2/output
    python v2/integration/plot_v2.py

    # R5 real-time probe (full live feature set):
    python v2/calibration/make_r5_calib.py   # once (true marker sizes)
    python v2/integration/run_v2.py --source bag --probe-r5 --dump
    python v2/integration/validate_v2_r5.py  # 13 checks, ALL PASS

    # live session (camera connected; recalibrates the scene first)
    python v2/integration/run_v2.py --source live --calibrate \
        --cube-size 0.07 --record v2/output/live.bag --dump

Unity: start a stack, open Unity/, press Play (SampleScene); the v2
receiver bootstraps from /dev/shm/integrated_scene_v2. Colors: red =
held (v1 meaning), amber = bridged or blending. Full phase details
and the camera-night checklist: V2.md.

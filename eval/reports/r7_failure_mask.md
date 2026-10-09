# R7 MediaPipe failure mask: recording_20260909_000024

Reference (zero-fire check): recording_20260224_083945.
Evaluated span: frames 5-1498 (1494 frames), i.e. the person-present span minus a 5-frame warmup.

Source: the RAW landmark CSV, so the detector sees what MediaPipe actually produced. All statistics are invariant under the camera -> leveled-desk map (a rigid isometry), so no scene calibration is needed.

## Constants

| constant | value | meaning |
|---|---|---|
| SEG_TOL | 0.35 | D2 fractional deviation from the clean segment median |
| TORSO_LINE_TOL_DEG | 22.0 | D3 hip line vs shoulder line angle, degrees |
| WIDTH_RATIO_BAND | 0.2 | D4 fractional deviation of shoulder/hip width ratio |
| STEP_TOL_M | 0.05 | D5 per-landmark step over one frame, meters |
| WARMUP_FRAMES | 5 | frames dropped after the person-present start |
| BRIDGE_GAP | 5 | morphological closing: gaps of at most this many frames |
| MIN_EVENT | 5 | morphological opening: events shorter than this are dropped |

## Threshold derivation and reference headroom

Thresholds were derived plot-first from the statistic distributions of the reference recording and R5 (eval/reports/r5_failure_thresholds.png), each set at the reference clean p99 plus a safety margin and cross-checked against the project precedents (E-011 torso line trip 20 deg; FOREARM_TOL / gate_tol 0.30 fractional).

| statistic | unit | threshold | max on 083945 | headroom | zero-fire |
|---|---|---|---|---|---|
| D2 forearm_L | frac dev | 0.35 | 0.626 | -0.276 | FAIL |
| D2 forearm_R | frac dev | 0.35 | 0.298 | +0.0525 | PASS |
| D2 upper_arm_L | frac dev | 0.35 | 0.558 | -0.208 | FAIL |
| D2 upper_arm_R | frac dev | 0.35 | 0.0782 | +0.272 | PASS |
| D3 torso line angle | deg | 22 | 20.1 | +1.85 | PASS |
| D4 width ratio dev | frac dev | 0.2 | 0.155 | +0.0452 | PASS |
| D5 landmark step | m | 0.05 | 0.0457 | +0.00431 | PASS |

Reference per-frame fire counts (D2-D5 must be 0):

| detector | frames fired on reference |
|---|---|
| d1_L | 5 |
| d1_R | 0 |
| d2_L | 96 |
| d2_R | 0 |
| d1_torso | 0 |
| d3 | 0 |
| d4 | 0 |
| d5_L | 0 |
| d5_R | 0 |
| d5_torso | 0 |

D1 is an acquisition detector, not a threshold detector: it reports MediaPipe's own src codes, so it is expected to fire wherever the reference has low-visibility samples and is exempt from the zero-fire rule.

Zero-fire check: FAIL for d2_L. This is a finding about the reference recording, not a mis-set threshold - see the next section.

### Reference residual events (the reference is not defect-free)

Only events that survive morphological closing and are not pure acquisition gaps are listed. The evidence column reports the median upper-arm and forearm length inside the event against their clean medians.

| entity | start_frame | stop_frame | frames | detectors | evidence (m) |
|---|---|---|---|---|---|
| arm_L | 297 | 317 | 21 | d2_L | upper 0.180 (clean 0.223), forearm 0.320 (clean 0.233), sum 0.500 (clean 0.456) |
| arm_L | 758 | 769 | 12 | d2_L | upper 0.193 (clean 0.223), forearm 0.318 (clean 0.233), sum 0.511 (clean 0.456) |
| arm_L | 811 | 882 | 72 | d2_L | upper 0.316 (clean 0.223), forearm 0.173 (clean 0.233), sum 0.492 (clean 0.456) |

Interpretation: in each of these windows the reference left elbow slides ALONG the arm - upper-arm and forearm move in opposite directions and their sum changes far less than either part does. That is a physically impossible limb, so the detector is right and the material assumption "the reference recording is clean" holds only for the right arm and the torso, not for the reference left arm. The same plateau is present in the reference FILTERED track, so it is not a raw-vs-filtered artifact.

### SEG_TOL sensitivity (what forcing zero fires costs)

| SEG_TOL | reference d2_L | reference d2_R | R5 d2_L | R5 d2_R |
|---|---|---|---|---|
| 0.35 | 96 | 0 | 62 | 0 |
| 0.65 | 0 | 0 | 62 | 0 |

Widening SEG_TOL to 0.65 silences the reference but loses these R5 D2 windows: none. DECISION: keep SEG_TOL = 0.35 (derived from the reference RIGHT arm, max frac dev 0.298, and consistent with the 0.30 project precedent). Calibrating the tolerance to a defect would blind the detector to the moderate R5 corruption windows the recovery stage needs.

## R7 detector fire counts

| detector | frames | percent of span |
|---|---|---|
| d1_L | 0 | 0.0 |
| d1_R | 5 | 0.3 |
| d2_L | 62 | 4.1 |
| d2_R | 0 | 0.0 |
| d1_torso | 0 | 0.0 |
| d3 | 289 | 19.3 |
| d4 | 118 | 7.9 |
| d5_L | 2 | 0.1 |
| d5_R | 2 | 0.1 |
| d5_torso | 4 | 0.3 |

Combined masks after closing (bridge <= 5, drop < 5):

| mask | frames | percent of span | events |
|---|---|---|---|
| fail_arm_L | 63 | 4.2 | 1 |
| fail_arm_R | 0 | 0.0 | 0 |
| fail_torso | 326 | 21.8 | 3 |

## Sanity check: known natural occlusions

Not applicable: the known occlusion windows are R5's frame numbers; no such list exists for this recording.

| entity | known window | source event | D1 coverage percent | overlapping mask events | verdict |
|---|---|---|---|---|---|

Sanity verdict: n/a

## Per-phase failure coverage (percent of phase frames)

| phase | frames | arm_L | arm_R | torso |
|---|---|---|---|---|
| approach | 285 | 0.0 | 0.0 | 0.0 |
| manipulation | 791 | 0.0 | 0.0 | 41.2 |
| retreat | 418 | 15.1 | 0.0 | 0.0 |

## Confident-but-wrong windows (D2-D5 firing without D1)

### arm_L: 63 frames, 1 windows after closing

| start_frame | stop_frame | seconds | detectors | mechanism |
|---|---|---|---|---|
| 1156 | 1218 | 2.1 | d2_L;d5_L | upper arm 27.5 cm (clean 25.2), forearm 43.2 cm (clean 22.2) |

### arm_R: 2 frames, 0 windows after closing

none

### torso: 291 frames, 3 windows after closing

| start_frame | stop_frame | seconds | detectors | mechanism |
|---|---|---|---|---|
| 651 | 758 | 3.6 | d3;d4;d5_torso | hip depth split 23.0 cm (clean 3.4), shoulder 5.0 cm (clean 3.4) |
| 809 | 965 | 5.24 | d3;d4;d5_torso | hip depth split 13.9 cm (clean 3.4), shoulder 0.8 cm (clean 3.4) |
| 994 | 1054 | 2.03 | d3;d5_torso | hip depth split 7.5 cm (clean 3.4), shoulder 0.8 cm (clean 3.4) |

A person facing the desk keeps both hips and both shoulders at nearly the same camera depth, so a torso window is read by which of the two splits blows up: a large HIP split with a clean shoulder split means one hip landmark took its depth off the wrong surface, and a large SHOULDER split with a clean hip split means the shoulder line is the corrupt one. Both variants appear above, matching the two E-011 corruption modes. MediaPipe reports all of these landmarks at full visibility, which is why D1 never fires and only the geometry detectors catch them. For the arm windows the mechanism column reports the measured limb lengths against their clean medians: a limb cannot change length, and upper arm and forearm moving in opposite directions is the elbow-slide signature.

## Interpretation

Known natural occlusions recovered by D1 (the sanity windows):

- none

Acquisition-only events (MediaPipe declined the sample, geometry never became implausible):

- none

Mixed events (an acquisition gap with implausible geometry in the same window - the tracker degrades before and after it gives up):

- none

NEW confident-but-wrong events (D2-D5 only, MediaPipe reported these samples as good):

- torso 651-758 (3.60 s) [d3;d4;d5_torso]
- torso 809-965 (5.24 s) [d3;d4;d5_torso]
- torso 994-1054 (2.04 s) [d3;d5_torso]
- arm_L 1156-1218 (2.10 s) [d2_L;d5_L]

## Event table

| start_frame | stop_frame | duration_s | frames | entity | detectors | phase |
|---|---|---|---|---|---|---|
| 651 | 758 | 3.603 | 108 | torso | d3;d4;d5_torso | manipulation |
| 809 | 965 | 5.237 | 157 | torso | d3;d4;d5_torso | manipulation |
| 994 | 1054 | 2.035 | 61 | torso | d3;d5_torso | manipulation |
| 1156 | 1218 | 2.101 | 63 | arm_L | d2_L;d5_L | retreat |

## Files

- eval/output/recovery_r7/failure_mask.csv
- eval/reports/r7_failure_events.csv
- eval/reports/r7_failure_mask.png
- eval/reports/r7_failure_thresholds.png
- eval/reports/r7_failure_mask.md


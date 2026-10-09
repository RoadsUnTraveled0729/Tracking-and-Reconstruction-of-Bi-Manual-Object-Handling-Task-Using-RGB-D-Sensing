# R5 MediaPipe failure mask: recording_20260825_222315

Reference (zero-fire check): recording_20260224_083945.
Evaluated span: frames 62-2098 (2037 frames), i.e. the person-present span minus a 5-frame warmup.

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
| 0.35 | 96 | 0 | 50 | 50 |
| 0.65 | 0 | 0 | 9 | 39 |

Widening SEG_TOL to 0.65 silences the reference but loses these R5 D2 windows: 1427-1457, 1807-1812. DECISION: keep SEG_TOL = 0.35 (derived from the reference RIGHT arm, max frac dev 0.298, and consistent with the 0.30 project precedent). Calibrating the tolerance to a defect would blind the detector to the moderate R5 corruption windows the recovery stage needs.

## R5 detector fire counts

| detector | frames | percent of span |
|---|---|---|
| d1_L | 218 | 10.7 |
| d1_R | 108 | 5.3 |
| d2_L | 50 | 2.5 |
| d2_R | 50 | 2.5 |
| d1_torso | 9 | 0.4 |
| d3 | 537 | 26.4 |
| d4 | 439 | 21.6 |
| d5_L | 62 | 3.0 |
| d5_R | 22 | 1.1 |
| d5_torso | 46 | 2.3 |

Combined masks after closing (bridge <= 5, drop < 5):

| mask | frames | percent of span | events |
|---|---|---|---|
| fail_arm_L | 350 | 17.2 | 5 |
| fail_arm_R | 183 | 9.0 | 5 |
| fail_torso | 625 | 30.7 | 5 |

## Sanity check: known natural occlusions

| entity | known window | source event | D1 coverage percent | overlapping mask events | verdict |
|---|---|---|---|---|---|
| arm_L | 1458-1668 | left elbow+wrist blocked | 100.0 | 1427-1668 | PASS |
| arm_R | 1826-1893 | right elbow blocked | 100.0 | 1775-1893 | PASS |

Sanity verdict: PASS

## Per-phase failure coverage (percent of phase frames)

| phase | frames | arm_L | arm_R | torso |
|---|---|---|---|---|
| entry | 0 | 0.0 | 0.0 | 0.0 |
| approach | 594 | 13.1 | 9.1 | 8.6 |
| manipulation | 1328 | 20.5 | 9.7 | 43.2 |
| retreat | 115 | 0.0 | 0.0 | 0.0 |

## Confident-but-wrong windows (D2-D5 firing without D1)

### arm_L: 98 frames, 5 windows after closing

| start_frame | stop_frame | seconds | detectors | mechanism |
|---|---|---|---|---|
| 65 | 76 | 0.4 | d2_L;d5_L | upper arm 28.4 cm (clean 26.6), forearm 26.7 cm (clean 24.7) |
| 85 | 150 | 2.2 | d2_L;d5_L | upper arm 28.3 cm (clean 26.6), forearm 27.9 cm (clean 24.7) |
| 1427 | 1457 | 1.03 | d2_L;d5_L | upper arm 22.5 cm (clean 26.6), forearm 34.7 cm (clean 24.7) |
| 1777 | 1798 | 0.73 | d2_L;d5_L | upper arm 22.5 cm (clean 26.6), forearm 14.9 cm (clean 24.7) |
| 1853 | 1860 | 0.27 | d2_L;d5_L | upper arm 21.0 cm (clean 26.6), forearm 19.5 cm (clean 24.7) |

### arm_R: 66 frames, 2 windows after closing

| start_frame | stop_frame | seconds | detectors | mechanism |
|---|---|---|---|---|
| 74 | 87 | 0.47 | d5_R | upper arm 27.1 cm (clean 25.8), forearm 24.2 cm (clean 25.5) |
| 1775 | 1825 | 1.7 | d2_R;d5_R | upper arm 47.2 cm (clean 25.8), forearm 3.0 cm (clean 25.5) |

### torso: 571 frames, 5 windows after closing

| start_frame | stop_frame | seconds | detectors | mechanism |
|---|---|---|---|---|
| 85 | 117 | 1.1 | d3;d4;d5_torso | hip depth split 4.1 cm (clean 1.3), shoulder 14.9 cm (clean 4.3) |
| 135 | 145 | 0.37 | d3;d4;d5_torso | hip depth split 8.6 cm (clean 1.3), shoulder 17.9 cm (clean 4.3) |
| 896 | 931 | 1.2 | d3;d4;d5_torso | hip depth split 11.8 cm (clean 1.3), shoulder 6.1 cm (clean 4.3) |
| 956 | 1130 | 5.84 | d3;d4;d5_torso | hip depth split 13.8 cm (clean 1.3), shoulder 1.6 cm (clean 4.3) |
| 1182 | 1544 | 12.11 | d3;d4;d5_torso | hip depth split 31.3 cm (clean 1.3), shoulder 0.9 cm (clean 4.3) |

A person facing the desk keeps both hips and both shoulders at nearly the same camera depth, so a torso window is read by which of the two splits blows up: a large HIP split with a clean shoulder split means one hip landmark took its depth off the wrong surface, and a large SHOULDER split with a clean hip split means the shoulder line is the corrupt one. Both variants appear above, matching the two E-011 corruption modes. MediaPipe reports all of these landmarks at full visibility, which is why D1 never fires and only the geometry detectors catch them. For the arm windows the mechanism column reports the measured limb lengths against their clean medians: a limb cannot change length, and upper arm and forearm moving in opposite directions is the elbow-slide signature.

## Interpretation

Known natural occlusions recovered by D1 (the sanity windows):

- arm_L 1427-1668 (8.07 s): left elbow+wrist blocked
- arm_R 1775-1893 (3.97 s): right elbow blocked

Acquisition-only events (MediaPipe declined the sample, geometry never became implausible):

- arm_R 1395-1404 (0.33 s)

Mixed events (an acquisition gap with implausible geometry in the same window - the tracker degrades before and after it gives up):

- arm_R 62-87 (0.87 s)
- arm_L 65-76 (0.40 s)
- arm_L 85-150 (2.20 s)
- torso 85-117 (1.10 s)
- arm_R 114-133 (0.67 s)
- torso 133-150 (0.60 s)
- arm_R 147-154 (0.27 s)

NEW confident-but-wrong events (D2-D5 only, MediaPipe reported these samples as good):

- torso 896-931 (1.20 s) [d3;d4;d5_torso]
- torso 956-1130 (5.84 s) [d3;d4;d5_torso]
- torso 1182-1544 (12.11 s) [d3;d4;d5_torso]
- arm_L 1777-1798 (0.73 s) [d2_L;d5_L]
- arm_L 1853-1860 (0.27 s) [d2_L;d5_L]

## Event table

| start_frame | stop_frame | duration_s | frames | entity | detectors | phase |
|---|---|---|---|---|---|---|
| 62 | 87 | 0.867 | 26 | arm_R | d1_R;d5_R | approach |
| 65 | 76 | 0.4 | 12 | arm_L | d1_L;d2_L;d5_L | approach |
| 85 | 150 | 2.202 | 66 | arm_L | d1_L;d2_L;d5_L | approach |
| 85 | 117 | 1.101 | 33 | torso | d1_torso;d3;d4;d5_torso | approach |
| 114 | 133 | 0.667 | 20 | arm_R | d1_R;d5_R | approach |
| 133 | 150 | 0.6 | 18 | torso | d1_torso;d3;d4;d5_torso | approach |
| 147 | 154 | 0.267 | 8 | arm_R | d1_R;d5_R | approach |
| 896 | 931 | 1.201 | 36 | torso | d3;d4;d5_torso | manipulation |
| 956 | 1130 | 5.838 | 175 | torso | d3;d4;d5_torso | manipulation |
| 1182 | 1544 | 12.109 | 363 | torso | d3;d4;d5_torso | manipulation |
| 1395 | 1404 | 0.334 | 10 | arm_R | d1_R | manipulation |
| 1427 | 1668 | 8.072 | 242 | arm_L | d1_L;d2_L;d5_L | manipulation |
| 1775 | 1893 | 3.969 | 119 | arm_R | d1_R;d2_R;d5_R | manipulation |
| 1777 | 1798 | 0.734 | 22 | arm_L | d2_L;d5_L | manipulation |
| 1853 | 1860 | 0.267 | 8 | arm_L | d2_L;d5_L | manipulation |

## Files

- eval/output/recovery_r5/failure_mask.csv
- eval/reports/r5_failure_events.csv
- eval/reports/r5_failure_mask.png
- eval/reports/r5_failure_thresholds.png
- eval/reports/r5_failure_mask.md


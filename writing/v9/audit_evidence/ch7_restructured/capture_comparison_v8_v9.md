# Chapter 7 capture evidence: V8 against V9 (E-036)

Old: `writing/v8/condensed`  
New: `writing/v9`  
Written: 2026-09-15T01:11:35Z

## What this comparison is

The two captures do not share a frame set. The dumper writes one row per Unity Update while the sender streams on the wall clock, so each run keeps a different subset of the recording and the accepted frames differ. Read this as a comparison of reported summaries, not as a per-frame difference: a change in n is expected, and a change in a statistic carries both the new rig sizing and the new frame subset.

All error statistics are centimetres; rig dimensions are metres. Deltas are new minus old.

## Rendered rig errors against the measured landmark (human.json, Tables 7.3 and 7.4)

### r6b

Captured frames 485 to 487 of 900 recorded frames.

| joint | n old | n new | median old | median new | median delta | p95 old | p95 new | p95 delta | max old | max new | max delta |
|---|---|---|---|---|---|---|---|---|---|---|---|
| right_elbow | 100 | 102 | 10.66 | 6.41 | -4.25 | 12.31 | 7.46 | -4.86 | 24.34 | 19.46 | -4.88 |
| right_wrist | 100 | 102 | 11.95 | 11.36 | -0.59 | 16.79 | 15.38 | -1.41 | 23.38 | 22.95 | -0.44 |

### r7

Captured frames 934 to 938 of 1499 recorded frames.

| joint | n old | n new | median old | median new | median delta | p95 old | p95 new | p95 delta | max old | max new | max delta |
|---|---|---|---|---|---|---|---|---|---|---|---|
| left_elbow | 589 | 589 | 6.33 | 6.14 | -0.19 | 11.57 | 11.89 | 0.32 | 17.33 | 17.74 | 0.41 |
| left_wrist | 589 | 589 | 6.87 | 6.75 | -0.12 | 11.06 | 12.26 | 1.19 | 16.37 | 17.75 | 1.38 |
| right_elbow | 650 | 650 | 5.70 | 5.31 | -0.38 | 6.33 | 6.68 | 0.35 | 8.17 | 9.35 | 1.19 |
| right_wrist | 650 | 650 | 5.71 | 5.46 | -0.25 | 6.55 | 6.84 | 0.29 | 15.93 | 15.04 | -0.88 |

## Bare model errors (bare_model.json)

### r6b

| joint | scope | reference | n old | n new | median old | median new | median delta | p95 old | p95 new | p95 delta | max old | max new | max delta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| right_elbow | section_7_3_frame_set | vs_raw_measured | 100 | 102 | 0.88 | 0.85 | -0.03 | 2.12 | 2.10 | -0.02 | 17.45 | 17.45 | 0.00 |
| right_elbow | section_7_3_frame_set | vs_filtered_measured | 100 | 102 | 0.91 | 0.89 | -0.02 | 2.10 | 2.09 | -0.01 | 17.50 | 17.50 | 0.00 |
| right_elbow | recording_wide_accepted | vs_raw_measured | 514 | 514 | 0.59 | 0.59 | 0.00 | 1.71 | 1.71 | 0.00 | 17.45 | 17.45 | 0.00 |
| right_elbow | recording_wide_accepted | vs_filtered_measured | 514 | 514 | 0.55 | 0.55 | 0.00 | 1.66 | 1.66 | 0.00 | 17.50 | 17.50 | 0.00 |
| right_elbow | rendered rig, same frames | vs_raw_measured | 100 | 102 | 10.66 | 6.41 | -4.25 | 12.31 | 7.46 | -4.86 | 24.34 | 19.46 | -4.88 |
| right_wrist | section_7_3_frame_set | vs_raw_measured | 100 | 102 | 6.78 | 6.77 | -0.01 | 10.89 | 10.86 | -0.04 | 27.95 | 27.95 | 0.00 |
| right_wrist | section_7_3_frame_set | vs_filtered_measured | 100 | 102 | 6.80 | 6.80 | 0.00 | 10.80 | 10.78 | -0.02 | 27.95 | 27.95 | 0.00 |
| right_wrist | recording_wide_accepted | vs_raw_measured | 514 | 514 | 8.52 | 8.52 | 0.00 | 9.75 | 9.75 | 0.00 | 27.95 | 27.95 | 0.00 |
| right_wrist | recording_wide_accepted | vs_filtered_measured | 514 | 514 | 8.54 | 8.54 | 0.00 | 9.71 | 9.71 | 0.00 | 27.95 | 27.95 | 0.00 |
| right_wrist | rendered rig, same frames | vs_raw_measured | 100 | 102 | 11.95 | 11.36 | -0.59 | 16.79 | 15.38 | -1.41 | 23.38 | 22.95 | -0.44 |

### r7

| joint | scope | reference | n old | n new | median old | median new | median delta | p95 old | p95 new | p95 delta | max old | max new | max delta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| left_elbow | section_7_3_frame_set | vs_raw_measured | 589 | 589 | 1.08 | 1.08 | 0.00 | 1.86 | 1.86 | 0.00 | 3.99 | 3.99 | 0.00 |
| left_elbow | section_7_3_frame_set | vs_filtered_measured | 589 | 589 | 1.12 | 1.12 | 0.00 | 1.84 | 1.84 | 0.00 | 3.46 | 3.46 | 0.00 |
| left_elbow | recording_wide_accepted | vs_raw_measured | 1095 | 1095 | 0.45 | 0.45 | 0.00 | 1.74 | 1.74 | 0.00 | 3.99 | 3.99 | 0.00 |
| left_elbow | recording_wide_accepted | vs_filtered_measured | 1095 | 1095 | 0.29 | 0.29 | 0.00 | 1.70 | 1.70 | 0.00 | 3.46 | 3.46 | 0.00 |
| left_elbow | rendered rig, same frames | vs_raw_measured | 589 | 589 | 6.33 | 6.14 | -0.19 | 11.57 | 11.89 | 0.32 | 17.33 | 17.74 | 0.41 |
| left_wrist | section_7_3_frame_set | vs_raw_measured | 589 | 589 | 2.34 | 2.34 | 0.00 | 3.85 | 3.85 | 0.00 | 11.14 | 11.14 | 0.00 |
| left_wrist | section_7_3_frame_set | vs_filtered_measured | 589 | 589 | 2.30 | 2.30 | 0.00 | 3.77 | 3.77 | 0.00 | 6.11 | 6.11 | 0.00 |
| left_wrist | recording_wide_accepted | vs_raw_measured | 1095 | 1095 | 1.03 | 1.03 | 0.00 | 3.58 | 3.58 | 0.00 | 11.14 | 11.14 | 0.00 |
| left_wrist | recording_wide_accepted | vs_filtered_measured | 1095 | 1095 | 0.93 | 0.93 | 0.00 | 3.54 | 3.54 | 0.00 | 6.11 | 6.11 | 0.00 |
| left_wrist | rendered rig, same frames | vs_raw_measured | 589 | 589 | 6.87 | 6.75 | -0.12 | 11.06 | 12.26 | 1.19 | 16.37 | 17.75 | 1.38 |
| right_elbow | section_7_3_frame_set | vs_raw_measured | 650 | 650 | 0.36 | 0.36 | 0.00 | 1.55 | 1.55 | 0.00 | 8.85 | 8.85 | 0.00 |
| right_elbow | section_7_3_frame_set | vs_filtered_measured | 650 | 650 | 0.20 | 0.20 | 0.00 | 1.57 | 1.57 | 0.00 | 8.76 | 8.76 | 0.00 |
| right_elbow | recording_wide_accepted | vs_raw_measured | 1156 | 1156 | 0.68 | 0.68 | 0.00 | 3.24 | 3.24 | 0.00 | 12.39 | 12.39 | 0.00 |
| right_elbow | recording_wide_accepted | vs_filtered_measured | 1156 | 1156 | 0.62 | 0.62 | 0.00 | 3.19 | 3.19 | 0.00 | 12.46 | 12.46 | 0.00 |
| right_elbow | rendered rig, same frames | vs_raw_measured | 650 | 650 | 5.70 | 5.31 | -0.38 | 6.33 | 6.68 | 0.35 | 8.17 | 9.35 | 1.19 |
| right_wrist | section_7_3_frame_set | vs_raw_measured | 650 | 650 | 0.83 | 0.83 | 0.00 | 2.03 | 2.03 | 0.00 | 13.46 | 13.46 | 0.00 |
| right_wrist | section_7_3_frame_set | vs_filtered_measured | 650 | 650 | 0.73 | 0.73 | 0.00 | 1.81 | 1.81 | 0.00 | 13.27 | 13.27 | 0.00 |
| right_wrist | recording_wide_accepted | vs_raw_measured | 1156 | 1156 | 1.03 | 1.03 | 0.00 | 2.87 | 2.87 | 0.00 | 22.78 | 22.78 | 0.00 |
| right_wrist | recording_wide_accepted | vs_filtered_measured | 1156 | 1156 | 0.97 | 0.97 | 0.00 | 2.75 | 2.75 | 0.00 | 23.07 | 23.07 | 0.00 |
| right_wrist | rendered rig, same frames | vs_raw_measured | 650 | 650 | 5.71 | 5.46 | -0.25 | 6.55 | 6.84 | 0.29 | 15.93 | 15.04 | -0.88 |

## Rendered rig dimensions

The sizing column is the length `eval/reports/<alias>_rig_sizing.json` asks the receiver for (E-036). The V8 captures were made before that rule, so their arm rows carry the loop recording constants.

### r6b (ch7_trails_revision)

| segment | old m | new m | delta m | sizing m |
|---|---|---|---|---|
| applied_scale | 0.522735 | 0.522735 | 0.000000 |  |
| forearm_L | 0.247000 | 0.257000 | 0.010000 | 0.2570 |
| forearm_R | 0.252000 | 0.205000 | -0.047000 | 0.2050 |
| hip_height_rest | 0.824127 | 0.824127 | 0.000000 |  |
| rig_rest_height_raw | 3.252124 | 3.252124 | 0.000000 |  |
| shoulder_width | 0.361215 | 0.360275 | -0.000940 |  |
| torso_hip_to_midshoulder | 0.576000 | 0.574500 | -0.001500 | 0.5745 |
| upper_arm_L | 0.262000 | 0.310000 | 0.048000 | 0.3100 |
| upper_arm_R | 0.256000 | 0.317000 | 0.061000 | 0.3170 |

### r7 (ch7_handover_trails)

| segment | old m | new m | delta m | sizing m |
|---|---|---|---|---|
| applied_scale | 0.522735 | 0.522735 | 0.000000 |  |
| forearm_L | 0.247000 | 0.223000 | -0.024000 | 0.2230 |
| forearm_R | 0.252000 | 0.233000 | -0.019000 | 0.2330 |
| hip_height_rest | 0.824127 | 0.824127 | 0.000000 |  |
| rig_rest_height_raw | 3.252124 | 3.252124 | 0.000000 |  |
| shoulder_width | 0.324216 | 0.323965 | -0.000251 |  |
| torso_hip_to_midshoulder | 0.517000 | 0.516600 | -0.000400 | 0.5166 |
| upper_arm_L | 0.262000 | 0.252000 | -0.010000 | 0.2520 |
| upper_arm_R | 0.256000 | 0.241000 | -0.015000 | 0.2410 |

## Sources

| file | sha256 |
|---|---|
| eval/reports/r6b_rig_sizing.json | 87e8fc3e8e6717f7ffe6224294a87023528204e6d6fb59299c8a4696826c57f5 |
| eval/reports/r7_rig_sizing.json | bb320f58c8e42411779505ee4e0ff9c1de7adf55474fc9d171ef8c611b6d5dfc |
| writing/v8/condensed/audit_evidence/ch7_restructured/bare_model.json | 64ac31dcbd8ffd4da69ea09e611bb73dc4894f535e54df03006f9b148d8b342e |
| writing/v8/condensed/audit_evidence/ch7_restructured/human.json | 1b03df1ee415f80dc1fd6c360caec32685d47fd00e8aea7b0fa4ae526a97d8d1 |
| writing/v8/condensed/figures/src/ch7_handover_trails/rig_dimensions.csv | 32d04a78de289c468e43dca03ebbed6ce78203531b3d601d7f0e29a06ee413d9 |
| writing/v8/condensed/figures/src/ch7_trails_revision/rig_dimensions.csv | 25c8beec24b946a4f69f20afad8aac0bd82784178b5c01e57b9cc0ef4091eace |
| writing/v9/audit_evidence/ch7_restructured/bare_model.json | 933c9f8cf775585d47f25513d53b1582188431736a44d9e4762feba3eef68980 |
| writing/v9/audit_evidence/ch7_restructured/human.json | 50735fe852f47a5c40a4e467da741b1359855382adb4b43b5955be2d0f3ef90b |
| writing/v9/figures/src/ch7_handover_trails/rig_dimensions.csv | 019053b23f7753501222974ab89a6505ff21313d83f27a292691cb9a0f3f402d |
| writing/v9/figures/src/ch7_trails_revision/rig_dimensions.csv | d03f6670affcb0f224b21212f1681b34744899e2ba03a55dfd2b75007587a736 |
| writing/v9/scripts/compare_captures_v8_v9.py | 9a4e2e45f5cc2609246a7a2dfb34b4c6e1934fe01f352659f83cef7940bf8280 |


STATUS: REQUIRED CHECKER FAIL; APPLICATION CHECKS PASS
GOAL: Identify the failed original Unity check without changing the archived pose or its threshold.
KEY FINDING: The failed predicate demands that left-hand disagreement on torso-failure frames exceed three times clean-frame disagreement. The archived-packet replay does not reproduce that historical error pattern.
VERIFIED: Original checker 7 PASS / 1 FAIL; separate sizing 12 PASS; independent archived packet/model checks 11 PASS; sampled raster 131 PASS / 0 FAIL, 4 skipped.
ASSUMPTIONS-UNRESOLVED: No exact final archived R5 joint log or renderer hash bundle is available. Historical pixel equivalence and the full cause of changed image residuals are not established.
DECISION: Preserve the failing result unchanged. Do not call the full required checker passing or change the pose to manufacture the historical error pattern.
NEXT: Root review determines activation; exact historical appearance remains unproven.

The predicate is eval/unity_check/check_unity_log.py:246-250. It is a greater-than error-concentration expectation, not an upper bound on error or a packet-integrity test. The new left-hand medians are 10.508664412402037 pixels clean and 15.072833335446552 pixels torso-only; 15.0728 is not greater than three times 10.5087. The other seven checks, including packet application, anchor, coverage and clean-frame following, pass.

The old eval/output/unity_check_r5/check_unity_log.json reports 23.910474751588723 pixels clean and 155.85097142797673 pixels torso-only. These are the values printed in the original section of eval/reports/r5_unity_check.md:95-100. That document later records spawn-pose alignment and segment/torso sizing corrections in its 2026-08-26 update. This establishes that the old report reflects the earlier documented measurement state. It does not establish the exact renderer/stream combination behind the currently available archived movie.

No corresponding final original R5 joint log is present in the archived capture directory. The older eval/output/backup_20260825/unity_person_log.csv contains only 896 unique matching source IDs; its pelvis differs from the archived input stream by a median maximum-coordinate difference of 0.13847244211014043 m. It is not a valid substitute for the missing matching log. Current global v1 runtime logs belong to another recording.

The current independent check verifies direct archived packets, constant bone-rest offsets for all 13 angles, rendered triad origins, source clock, and that the copied receiver differs only by private paths and a post-pose axis hook. These facts locate the failed requirement in the historical outcome comparison; they do not prove anatomical accuracy or exact historical renderer reproduction.

Reproduction, from repository root:

    /home/luo/anaconda3/bin/python eval/unity_check/check_unity_log.py --stem recording_20260825_222315 --out presentation/defense_2026/unity_capture/r5_archived --person-log presentation/defense_2026/unity_capture/r5_archived/unity_person_log.csv --object-log presentation/defense_2026/unity_capture/r5_archived/unity_object_log.csv --frames-dir /tmp/defense_axes_capture/r5_frames
    /home/luo/anaconda3/bin/python presentation/defense_2026/unity_capture/check_rig_sizing_isolated.py --sizing presentation/defense_2026/unity_capture/r5_archived/archived_rig_sizing.json --rig-dimensions presentation/defense_2026/unity_capture/r5_archived/rig_dimensions.csv --used presentation/defense_2026/unity_capture/r5_archived/rig_sizing_used.txt
    /home/luo/anaconda3/bin/python presentation/defense_2026/unity_capture/validate_archived_replay.py
    /home/luo/anaconda3/bin/python presentation/defense_2026/unity_capture/validate_render_projection.py presentation/defense_2026/unity_capture/r5_archived

The first command exits 1 by design for the preserved failed assertion; do not suppress that exit or present it as a pass. The full PNG sequence is local under /tmp and must be regenerated if removed.

Root disposition: accepted for the presentation as a source-preserving replay, conditional on complete final MP4 decoding. The legacy required checker remains FAIL. Neither its threshold nor the pose has been changed. This limited presentation acceptance is not a passing scientific benchmark or a historical pixel-equivalence claim.

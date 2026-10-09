"""Reproduce Table 7.6 and inspect its scores on harness-eligible frames.

Run from the repository root with /home/luo/anaconda3/bin/python.
Reads current local CSV inputs, computes only in memory, and writes the
result beside this script. The eligible-only result filters scoring after
running the original masks; it is not a newly designed outage experiment.
"""
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import numpy as np

sys.path[:0] = ['eval/failure', 'eval/common']
import recovery_core as rc
import paths
import harness_recovery as hr
import moving_window_check as mw

inp = rc.build_inputs(paths.R5_STEM)
truth = rc.run_variant(inp, 'plain')
eligible = hr.select_windows(
    inp, truth, hr.grip_context(paths.R5_STEM, inp), 'right')['ok']
lm = inp['lm_df']
shoulder = lm[['right_shoulder_' + a for a in 'xyz']].to_numpy() * [1, -1, 1]
wrist = lm[['right_wrist_' + a for a in 'xyz']].to_numpy() * [1, -1, 1]
lengths = inp['seg_len']
lines = []
for start, stop in [(865, 895), (870, 902)]:
    mask = np.zeros(inp['n'], bool)
    mask[start:stop + 1] = True
    masked = rc.build_inputs(paths.R5_STEM, extra_fail={'right': mask})
    for method in ['hold', 'masked', 'recovery']:
        result = (rc.run_hold_baseline(masked) if method == 'hold'
                  else rc.run_variant(masked, method))
        errors = np.array([
            np.linalg.norm(mw.fk_wrist(
                result['angles'], i, shoulder,
                lengths['upper_arm_R'], lengths['forearm_R'], 'right')
                - wrist[i]) * 100
            for i in range(start, stop + 1)])
        good = errors[eligible[start:stop + 1]]
        lines.append(
            f'{start}-{stop} {method}: all n={len(errors)} '
            f'median/p95/max={np.percentile(errors, [50, 95, 100]).round(3).tolist()}, '
            f'eligible-only n={len(good)} '
            f'median/p95/max={np.percentile(good, [50, 95, 100]).round(3).tolist()}')
text = '\n'.join(lines)
print(text)
(Path(__file__).parent / 'moving_eligible_check.txt').write_text(
    text + '\nNOTE: post hoc eligibility filtering of existing masks, '
    'not new eligible-only window design. Uses current local CSV inputs; '
    'all-frame values reproduce pinned Table7.6.\n')

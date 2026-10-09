"""Read-only thesis evaluation audit. Run from repository root with thesis Python.
Prints diagnostic JSON; reads current CSV inputs, not pinned
historical replay data. Does not rerun hardware or mutate repository outputs.
"""
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import numpy as np
import pandas as pd

sys.path[:0] = ['eval/failure', 'eval/common']
import recovery_core as rc
import paths
import harness_recovery as hr

inp = rc.build_inputs(paths.R5_STEM)
truth = rc.run_variant(inp, 'plain')
ctx = hr.grip_context(paths.R5_STEM, inp)
sel = hr.select_windows(inp, truth, ctx, 'right')
out = {'warning': 'Current local CSV inputs; shifted replay numbers are not corrected historical pinned results.', 'moving_windows': []}
for a, b in [(865, 895), (870, 902)]:
    out['moving_windows'].append({
        'start': a, 'stop': b, 'eligible_count': int(sel['ok'][a:b+1].sum()),
        'ineligible_frames': (np.flatnonzero(~sel['ok'][a:b+1]) + a).tolist(),
        'torso_failure_frames': (np.flatnonzero(inp['fail']['torso'][a:b+1]) + a).tolist(),
        'root_live_count': int(((truth['mask'][a:b+1] & 1) > 0).sum()),
        'reference_masks': np.asarray(truth['mask'][a:b+1], int).tolist(),
        'raw_wrist_count': int(ctx['right']['wrist_flag0'][a:b+1].sum()),
    })
files = ['v2/output/v2_person_dump.csv', 'eval/output/recovery_r6b/angles_recovery.csv', 'eval/output/recovery_r5/failure_mask.csv']
out['input_sha256'] = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in files}
live = pd.read_csv(files[0])
ref = pd.read_csv(files[1])
m = live.merge(ref, on='frame', suffixes=('_l', '_r'))
la = m[[f'a{i}' for i in range(13)]].to_numpy(float)
ra = m[hr.ANGLE_COLS].to_numpy(float)
lv = ((m['mask'].to_numpy(int) & 14) == 14)
rv = ((m['live_mask'].to_numpy(int) & 14) == 14)
for i in range(1, 4):
    lv &= m[f'tag_{i}_l'].to_numpy(int) == 0
    rv &= m[f'tag_{i}_r'].to_numpy(int) == 0
clean = lv & rv
out['shifted_validity'] = []
for k in [0, 3, 4, 5, 6, 7]:
    a, b = (la[k:], ra[:-k]) if k else (la, ra)
    old = clean[k:] if k else clean
    corrected = (lv[k:] & rv[:-k]) if k else clean
    e = np.abs(hr.wrap(a - b))
    out['shifted_validity'].append({
        'lag_frames': k, 'old_count': int(old.sum()),
        'corrected_count': int(corrected.sum()),
        'old_invalid_reference_count': int(np.sum(old & ~corrected)),
        'old_median_deg': float(np.median(e[old, 3:8])),
        'corrected_median_deg': float(np.median(e[corrected, 3:8])),
        'old_per_angle_median_p95_deg': [np.percentile(e[old, i], [50, 95]).tolist() for i in range(3, 8)],
    })
print(json.dumps(out, indent=2))

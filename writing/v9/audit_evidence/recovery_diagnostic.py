"""Read-only reproduction of recovery audit checks; prints diagnostics only.

Run from repository root with the thesis Python:
PYTHONDONTWRITEBYTECODE=1 /home/luo/anaconda3/bin/python writing/v9/audit_evidence/recovery_diagnostic.py

The code below reproduces the exact numerical diagnostic run used for
recovery_review.txt. sys.dont_write_bytecode additionally suppresses import
cache writes even when the environment variable is omitted.
"""
import sys
sys.dont_write_bytecode = True
import numpy as np
sys.path[:0] = ['writing/v9/scripts', 'eval/failure', 'eval/common',
               'eval/offset', 'v1/kinematics']
import ch5_worked_example as ex
import paths
import recovery_core as rc
from occlusion_ext import RobustChainSolver

s = RobustChainSolver()
for L1, L2, r in [(.317, .205, .05), (.205, .317, .05), (.317, .205, .6)]:
    S = np.zeros(3)
    W = np.array([r, 0, 0])
    E = s._ik_elbow(S, W, L1, L2, None)
    print('UNREACHABLE', L1, L2, r, 'rawcos',
          (L1 * L1 + r * r - L2 * L2) / (2 * L1 * r),
          'E', E.tolist(), 'actual_lengths',
          np.linalg.norm(E - S), np.linalg.norm(E - W))

inp, _ = ex.build(paths.R6B_STEM)
s = RobustChainSolver(seg_len=dict(inp['seg_len']))
low = []
stale = []
orig = s._ik_elbow
current_i = -1


def wrapped(S, W, L1, L2, mem_dir, p=None):
    if (mem_dir is not None and s.k.get('right_elbow', 0) > s.H
            and L1 == s.L['upper_arm_R']):
        stale.append((current_i, s.k['right_elbow']))
    return orig(S, W, L1, L2, mem_dir, p)


s._ik_elbow = wrapped
prev = None
for i, (_, row) in enumerate(inp['lm_df'].iterrows()):
    current_i = i
    pts = rc.solver_points(
        row, {a: bool(inp['fail'][a][i]) for a in rc.SIDES})
    obs = {
        a: inp['w_hat_solver'][a][i]
        if np.isfinite(inp['w_hat_solver'][a][i]).all() else None
        for a in rc.SIDES
    }
    angles, mask, tags = s.solve(pts, obj=obs)
    if prev is not None and abs(angles[6]) < 15 and tags[2] == 2:
        delta = (angles[5] - prev[5] + 180) % 360 - 180
        if abs(delta) > 1e-8:
            low.append((i, float(angles[6]), float(delta), int(tags[2])))
    prev = angles.copy()
print('STALE_RIGHT_IK_count', len(stale),
      'first_last', stale[:3], stale[-3:])
print('CONSTRAINED_LOW_FLEX_TWIST_CHANGES_count', len(low),
      'examples', low[:8])

import grip_state as g
h = np.r_[np.ones(5, bool), np.zeros(5, bool)]
carried = np.ones(10, bool)
wc = np.ones(10, bool)
dist = np.r_[np.zeros(5), np.full(5, .4)]
a = g.grip_episodes(h[:8], carried[:8], dist[:8], wc[:8])[0]
b = g.grip_episodes(h, carried, dist, wc)[0]
print('PREFIX holding first8', a.tolist(), 'full first8', b[:8].tolist())

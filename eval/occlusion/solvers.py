"""Occlusion fallback solvers (stage 5), wrapping the frozen v1
ChainFallbackSolver.

Three methods, all causal (state from past frames only, no lookahead):

- HoldLast: the v1 baseline, unchanged (imported), tags derived from
  its live mask.
- CVAngleFallback: constant-velocity extrapolation in the 13-angle
  space with a bounded horizon (H frames, then freeze at the
  extrapolated pose). Velocity is a shortest-arc EMA updated only on
  consecutive live frames, reset on reacquisition.
- SphereWristFallback: segment-length-constrained wrist recovery -
  when shoulder+elbow are live and the wrist is blocked, a wrist
  estimate is injected upstream of the solver on the sphere of the
  measured forearm length around the elbow, in the EMA'd last-valid
  forearm direction. The affected joint bits are cleared from the
  reported live mask (the estimate is constrained, not measured) and
  tagged.

Method tags per joint group and frame:
  0 MEASURED, 1 HELD, 2 EXTRAPOLATED, 3 CONSTRAINED
(9 = fusion-display-only exists only in fusion_display.py output and
never enters error statistics.)

Group order (mask bit i = group i): root, R_swing, R_twist, R_elbow,
L_swing, L_twist, L_elbow.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]
                       / "v1" / "kinematics"))
from occlusion import (BIT_NAMES, LANDMARKS, MASK_ALL,  # noqa: E402,F401
                       ChainFallbackSolver, points_from_row)

MEASURED, HELD, EXTRAPOLATED, CONSTRAINED = 0, 1, 2, 3

# angle indices per mask-bit group
GROUP_IDX = ((0, 1, 2), (3, 4), (5,), (6, 7), (8, 9), (10,), (11, 12))
N_GROUPS = 7


def wrap_deg(a):
    return (np.asarray(a, float) + 180.0) % 360.0 - 180.0


class HoldLast:
    """v1 baseline: ChainFallbackSolver verbatim, tags from the mask."""

    def __init__(self):
        self.inner = ChainFallbackSolver()

    def solve(self, points):
        angles, mask = self.inner.solve(points)
        tags = np.array([MEASURED if mask & (1 << g) else HELD
                         for g in range(N_GROUPS)])
        return angles, mask, tags


class CVAngleFallback:
    """Constant-velocity extrapolation in angle space, horizon H."""

    def __init__(self, horizon=10, vel_alpha=0.5):
        self.inner = ChainFallbackSolver()
        self.H = horizon
        self.alpha = vel_alpha
        self.a_last = None            # last live output per group (13,)
        self.v = np.zeros(13)         # deg/frame EMA
        self.k = np.zeros(N_GROUPS, int)      # frames since live
        self.was_live = np.zeros(N_GROUPS, bool)

    def solve(self, points):
        angles, mask = self.inner.solve(points)
        out = angles.copy()
        tags = np.zeros(N_GROUPS, int)
        if self.a_last is None:
            self.a_last = angles.copy()
        for g in range(N_GROUPS):
            idx = list(GROUP_IDX[g])
            live = bool(mask & (1 << g))
            if live:
                if self.was_live[g]:
                    d = wrap_deg(angles[idx] - self.a_last[idx])
                    self.v[idx] = (self.alpha * d
                                   + (1 - self.alpha) * self.v[idx])
                else:
                    self.v[idx] = 0.0   # reacquisition: no velocity claim
                self.a_last[idx] = angles[idx]
                self.k[g] = 0
                tags[g] = MEASURED
            else:
                self.k[g] += 1
                k_eff = min(self.k[g], self.H)
                out[idx] = wrap_deg(self.a_last[idx]
                                    + k_eff * self.v[idx])
                tags[g] = EXTRAPOLATED if self.k[g] <= self.H else HELD
            self.was_live[g] = live
        return out, mask, tags


class SphereWristFallback:
    """Segment-length-constrained wrist recovery upstream of the solver."""

    ARMS = {
        "right": {"sh": "right_shoulder", "el": "right_elbow",
                  "wr": "right_wrist", "twist_bit": 2, "elbow_bit": 3},
        "left": {"sh": "left_shoulder", "el": "left_elbow",
                 "wr": "left_wrist", "twist_bit": 5, "elbow_bit": 6},
    }

    def __init__(self, forearm_len, dir_alpha=0.3, horizon=None):
        """forearm_len: dict side -> measured forearm length (m),
        in the same (Unity) space the points arrive in."""
        self.inner = ChainFallbackSolver()
        self.L = forearm_len
        self.alpha = dir_alpha
        self.H = horizon            # None = unbounded
        self.u = {"right": None, "left": None}   # EMA forearm direction
        self.k = {"right": 0, "left": 0}
        self.last_injection = {"right": None, "left": None}

    @staticmethod
    def _ok(p, k):
        v = p.get(k)
        return v is not None and bool(np.all(np.isfinite(v)))

    def solve(self, points):
        p = {k: (np.asarray(v, float) if v is not None else None)
             for k, v in points.items()}
        constrained = {"right": False, "left": False}
        self.last_injection = {"right": None, "left": None}
        for side, names in self.ARMS.items():
            sh, el, wr = names["sh"], names["el"], names["wr"]
            if self._ok(p, el) and self._ok(p, wr):
                d = p[wr] - p[el]
                nd = np.linalg.norm(d)
                if nd > 1e-9:
                    u = d / nd
                    if self.u[side] is None:
                        self.u[side] = u
                    else:
                        m = (1 - self.alpha) * self.u[side] + self.alpha * u
                        self.u[side] = m / np.linalg.norm(m)
                self.k[side] = 0
            elif (self._ok(p, sh) and self._ok(p, el)
                  and self.u[side] is not None):
                self.k[side] += 1
                if self.H is None or self.k[side] <= self.H:
                    p = dict(p)
                    p[wr] = p[el] + self.L[side] * self.u[side]
                    constrained[side] = True
                    self.last_injection[side] = p[wr]
        angles, mask = self.inner.solve(p)
        tags = np.array([MEASURED if mask & (1 << g) else HELD
                         for g in range(N_GROUPS)])
        for side, names in self.ARMS.items():
            if constrained[side]:
                for bit in (names["twist_bit"], names["elbow_bit"]):
                    # solver saw the injected wrist and set these bits
                    # live; the estimate is constrained, not measured
                    if mask & (1 << bit):
                        mask &= ~(1 << bit)
                        tags[bit] = CONSTRAINED
        return angles, mask, tags

    def wrist_estimate(self, side):
        """The injected point for the last constrained frame, if any -
        native point-space output for the real-event evaluation."""
        return self.u[side]

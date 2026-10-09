"""BASELINE: the bar every Phase 4 strategy must beat.

Recalibrated gate (upstream) -> NaN -> the VERBATIM vendored v1
ChainFallbackSolver (hold-last per joint group, in angle space).
Status per group: solved live this frame = MEASURED; held for up to
status.lost_after_frames = ESTIMATED; longer = LOST. This is exactly
v1's behavior plus the honesty statuses -- if a strategy cannot beat
this, it has no reason to exist.
"""
import sys
from pathlib import Path

import numpy as np

_VENDOR = Path(__file__).resolve().parents[1] / "vendor" / "v1"
if str(_VENDOR) not in sys.path:
    sys.path.insert(0, str(_VENDOR))

from occlusion import ChainFallbackSolver  # noqa: E402  vendored

from bench.metrics import ESTIMATED, GROUP_NAMES, LOST, MEASURED  # noqa: E402
from strategies.strategy_base import (OcclusionStrategy, StrategyOutput,  # noqa: E402
                                     register)


@register
class BaselineHold(OcclusionStrategy):
    name = "baseline_hold"

    def __init__(self, cfg):
        self.lost_after = int(cfg["status"]["lost_after_frames"])
        self.reset()

    def reset(self):
        self.solver = ChainFallbackSolver()
        self.held = np.zeros(len(GROUP_NAMES), dtype=int)

    def update(self, t, points, scores):
        angles, mask = self.solver.solve(points)
        status = np.empty(len(GROUP_NAMES), dtype=int)
        for g in range(len(GROUP_NAMES)):
            if (mask >> g) & 1:
                self.held[g] = 0
                status[g] = MEASURED
            else:
                self.held[g] += 1
                status[g] = (ESTIMATED if self.held[g] <= self.lost_after
                             else LOST)
        return StrategyOutput(angles, status, {"live_mask": mask})

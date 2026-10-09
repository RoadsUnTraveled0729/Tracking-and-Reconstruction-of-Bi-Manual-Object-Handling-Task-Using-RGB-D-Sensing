"""The common interface every occlusion strategy competes behind
(V3_PLAN.md Phase 4). Registered by name; grade.py runs manifest x
strategies with no strategy-specific code anywhere else.

Contract:
- update() is called once per frame, in order, and must be CAUSAL:
  this frame and its own state only.
- points are the eight v1 landmarks in UNITY space (already filtered
  and flipped by the runner); a blocked landmark is absent, None, or
  NaN. scores carry the detector confidence per landmark (may be
  empty for CSV replay of nan-masked data).
- The output must ALWAYS contain 13 finite angles and an honest
  status per group: MEASURED only when the group was solved from this
  frame's landmarks.
"""
import numpy as np

from bench.metrics import ESTIMATED, GROUP_NAMES, LOST, MEASURED  # noqa: F401


class StrategyOutput:
    __slots__ = ("angles13", "status", "diagnostics")

    def __init__(self, angles13, status, diagnostics=None):
        self.angles13 = np.asarray(angles13, dtype=float)
        self.status = np.asarray(status, dtype=int)
        if self.angles13.shape != (13,):
            raise ValueError(f"angles13 shape {self.angles13.shape}")
        if self.status.shape != (len(GROUP_NAMES),):
            raise ValueError(f"status shape {self.status.shape}")
        if not np.all(np.isfinite(self.angles13)):
            raise ValueError("non-finite angle in strategy output")
        self.diagnostics = diagnostics or {}


class OcclusionStrategy:
    name = None

    def update(self, t, points, scores):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError


REGISTRY = {}


def register(cls):
    if not cls.name:
        raise ValueError("strategy needs a name")
    REGISTRY[cls.name] = cls
    return cls


def build(name, cfg):
    if name not in REGISTRY:
        raise KeyError(f"unknown strategy '{name}'; have "
                       f"{sorted(REGISTRY)}")
    return REGISTRY[name](cfg)

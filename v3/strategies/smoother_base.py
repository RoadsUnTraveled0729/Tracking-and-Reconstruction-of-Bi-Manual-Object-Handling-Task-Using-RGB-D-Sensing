"""Causal smoothers for the S2 quaternion tracks (plan M4/M5).

A QuatSmoother sits inside one S2 _JointTrack, after the
measure/blend step and before the per-frame step caps:

    q_target = smoother.update(q_meas, measured=True)   # measured frame
    smoother.update(q_pred, measured=False)             # predicted frame

On a measured frame it returns the smoothed target the step caps then
approach; on a predicted (unobservable) frame it receives the track's
own predicted output and only re-synchronizes its state to it (the
return value is ignored by the track), so after an occlusion the
smoother restarts from what was on screen instead of from a stale
pre-occlusion state. reset() returns to the empty state; the first
measured sample initializes it (output = that sample).

Smoothers are registered by name; "none" is the identity and leaves
S2 bit-for-bit unchanged (tests/test_smoother.py). Each track kind
(root, swing, twist, elbow) gets its own instance and its own
parameters from config strategy.s2_quat_prediction.smoother_params.

Causality: update() sees this frame and the smoother's own state only.
Internal tangent-space or Rodrigues state is allowed (D-027, an
extension of D-005); the output is always a unit quaternion.
"""
import numpy as np

from core.representation import (QuatOneEuro, hemisphere, qnormalize,
                                 quat_about)

_X = np.array([1.0, 0.0, 0.0])
TRACK_KINDS = ("root", "swing", "twist", "elbow")


class QuatSmoother:
    name = None

    def update(self, q_meas, measured):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError


SMOOTHERS = {}


def register_smoother(cls):
    if not cls.name:
        raise ValueError("smoother needs a name")
    SMOOTHERS[cls.name] = cls
    return cls


def build_smoother(name, kind, params, freq_hz, projector=None):
    """name: registry key; kind: one of TRACK_KINDS; params: that
    kind's parameter dict (may be None for 'none'); projector: the
    track's manifold projector (swing, elbow) or None."""
    if name not in SMOOTHERS:
        raise KeyError(f"unknown smoother '{name}'; have "
                       f"{sorted(SMOOTHERS)}")
    if kind not in TRACK_KINDS:
        raise KeyError(f"unknown track kind '{kind}'")
    return SMOOTHERS[name](kind, params, freq_hz, projector)


@register_smoother
class NoSmoother(QuatSmoother):
    """Identity: returns the input object unchanged."""
    name = "none"

    def __init__(self, kind=None, params=None, freq_hz=None,
                 projector=None):
        pass

    def update(self, q_meas, measured):
        return q_meas

    def reset(self):
        pass


class _ScalarOneEuro:
    """1-D One-Euro (v1 OneEuro semantics: derivative of the raw
    samples, EMA at d_cutoff, cutoff = min_cutoff + beta * |dx|)."""

    def __init__(self, freq, min_cutoff, beta, d_cutoff):
        self.freq = float(freq)
        self.min_cutoff = float(min_cutoff)
        self.beta = float(beta)
        self.d_cutoff = float(d_cutoff)
        self.reset()

    @staticmethod
    def _alpha(cutoff, freq):
        tau = 1.0 / (2.0 * np.pi * cutoff)
        return 1.0 / (1.0 + tau * freq)

    def reset(self):
        self.x = None
        self.raw = None
        self.dx = 0.0

    def sync(self, x):
        self.x = float(x)
        self.raw = float(x)
        self.dx = 0.0

    def __call__(self, x):
        x = float(x)
        if self.x is None:
            self.sync(x)
            return x
        d = (x - self.raw) * self.freq
        self.dx += self._alpha(self.d_cutoff, self.freq) * (d - self.dx)
        cutoff = self.min_cutoff + self.beta * abs(self.dx)
        self.x += self._alpha(cutoff, self.freq) * (x - self.x)
        self.raw = x
        return self.x


def _twist_angle(q):
    """Signed angle of a rotation about +x (q = [cos(a/2), sin(a/2), 0,
    0] up to sign)."""
    q = q if q[0] >= 0 else -q
    return 2.0 * float(np.arctan2(q[1], q[0]))


@register_smoother
class QuatOneEuroSmoother(QuatSmoother):
    """One-Euro on the rotation manifold (core.representation
    .QuatOneEuro) for root, swing and elbow; swing and elbow are
    re-projected onto v1's Ry*Rz manifold after smoothing (the slerp
    of two Ry*Rz points leaves the manifold); the twist track is a
    scalar One-Euro on its angle about +x, unwrapped against the
    previous raw sample so it never crosses +-180 by a jump.
    params: {"min_cutoff": Hz, "beta": 1/rad (on rad/s speed),
    "d_cutoff": Hz}."""
    name = "quat_one_euro"

    def __init__(self, kind, params, freq_hz, projector=None):
        if params is None:
            raise ValueError(f"quat_one_euro needs smoother_params.{kind}")
        for k in ("min_cutoff", "beta", "d_cutoff"):
            if params.get(k) is None:
                raise ValueError(f"smoother_params.{kind}.{k} is null "
                                 "(D-006)")
        self.kind = kind
        self.projector = projector
        mc, b, dc = (float(params["min_cutoff"]), float(params["beta"]),
                     float(params["d_cutoff"]))
        if kind == "twist":
            self.f = _ScalarOneEuro(freq_hz, mc, b, dc)
        else:
            self.f = QuatOneEuro(freq_hz, mc, b, dc)
        self._last_raw_angle = None

    def reset(self):
        self.f.reset()
        self._last_raw_angle = None

    def _unwrap(self, a):
        if self._last_raw_angle is not None:
            a = self._last_raw_angle + float(
                np.angle(np.exp(1j * (a - self._last_raw_angle))))
        self._last_raw_angle = a
        return a

    def update(self, q_meas, measured):
        if q_meas is None:
            return None
        if self.kind == "twist":
            a = self._unwrap(_twist_angle(qnormalize(q_meas)))
            if not measured:
                self.f.sync(a)
                return q_meas
            return quat_about(_X, self.f(a))
        if not measured:
            q = qnormalize(q_meas)
            if self.f._q is not None:
                q = hemisphere(q, self.f._q)
            self.f._q = q.copy()
            self.f._raw = q.copy()
            self.f._speed = 0.0
            return q_meas
        q = self.f(q_meas)
        return q if self.projector is None else self.projector(q)


# smoother (ii), registered on import (kept last: it imports this module)
from strategies import smoother_kalman  # noqa: E402,F401

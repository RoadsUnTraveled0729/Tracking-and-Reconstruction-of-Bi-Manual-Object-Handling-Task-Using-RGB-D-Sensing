"""Smoother (ii): causal constant-velocity Kalman filter in the tangent
space of a quaternion track (plan M5, D-038; state allowed by D-027).

State per track: an orientation estimate q_ref plus a tangent-space
state [r (3), w (3)], r = qlog(q_ref^-1 q) (the Rodrigues / log-map
offset, rad) and w the body-frame angular velocity (rad/s). After every
step the filter re-linearises: q_ref <- q_ref * qexp(r), r <- 0, so r
stays small and the linear model holds (the multiplicative
error-state form). The twist track uses the scalar 1-DOF version, state
[theta, omega] on the unwrapped angle about +x.

Model (per tangent axis, the three axes independent and identical):

    predict   r' = r + w dt,   w' = f w          (f = 1 measured frame,
                                                  f = decay_lambda when
                                                  no measurement)
              P' = F P F^T + Q,  F = [[1, dt], [0, f]]
              Q  = q_w [[dt^3/3, dt^2/2], [dt^2/2, dt]]   (continuous
                   white-noise acceleration, CWNA)
                 + q_r [[dt, 0], [0, 0]]                   (position
                   random walk)
    update    z = qlog(q_pred^-1 q_meas),  H = [1, 0],  R = r_v
              Joseph form P+ = (I - K H) P (I - K H)^T + K R K^T

Because Q, R and H are the same on every axis and the initial P is
isotropic, the 6x6 covariance is P2 (x) I3 exactly; the filter carries
the 2x2 block as three Python floats (a, b, c), symmetric by
construction, which keeps an update well under 50 us in pure numpy.
The covariance is carried through the re-linearisation unchanged (the
first-order transport; the exact reset Jacobian I - [r/2]x differs at
second order in r, and r is one frame's innovation times the gain).

Initialisation (two-point differencing, Bar-Shalom, Li and
Kirubarajan, Estimation with Applications to Tracking and Navigation,
2001, sec. 5.5.3): the first measurement sets q_ref, w = 0; the second
sets w = z / (n dt) over the n frames between them and
P = R [[1, 1/(n dt)], [1/(n dt), 2/(n dt)^2]]. Output on both = the
measurement.

S2 contract (strategies/smoother_base.py): update(q, measured=True)
returns the filtered target; update(q, measured=False) is S2's
predicted frame: the filter runs the damped predict (velocity x
decay_lambda, the S2 lambda, so the velocity dies out at S2's rate)
and then re-synchronises its orientation to the track's output q; the
return value is ignored by the track. update(None, ...) is a
predict-only frame (standalone use): damped predict, return the
prediction. Swing and elbow outputs (and the internal q_ref) are
re-projected onto v1's Ry*Rz manifold after every update, sync and
predict-only output; the intermediate prior of a measured frame is not
projected (it only serves as the linearisation point of that frame's
innovation), which saves one projection per update.

lag_frames (default 0, off): a fixed-lag Rauch-Tung-Striebel smoother
over the last lag_frames measured frames, returning the smoothed
estimate of frame t - lag_frames. It is off because the PSV3 packet has
no lag field (replay/psv3.py), so Unity could not know that the pose it
draws is lag_frames old (plan: "Deferred: declared smoothing lag").
The option exists so the lagged variant can be measured without a code
change.

Parameters (config strategy.s2_quat_prediction.smoother_params
.tangent_kf.<kind>; degrees for readability, converted to radians):
    q_w         deg^2/s^3  CWNA spectral density (acceleration noise)
    q_r         deg^2/s    position random-walk spectral density
    r_v         deg^2      measurement noise variance per tangent axis
    decay_lambda           velocity damping per unmeasured frame;
                           null = S2's decay_lambda (filled by S2)
    lag_frames  int        0 (off)
"""
import math

import numpy as np

from core.representation import qexp, qlog, qmul, qconj, qnormalize, \
    quat_about
from strategies.smoother_base import (QuatSmoother, _twist_angle,
                                      register_smoother)

_X = np.array([1.0, 0.0, 0.0])
_D2R2 = (math.pi / 180.0) ** 2


def _wrap(a):
    return (a + math.pi) % (2.0 * math.pi) - math.pi


class _Cov2:
    """Symmetric 2x2 covariance [[a, b], [b, c]] of one tangent axis."""
    __slots__ = ("a", "b", "c")

    def __init__(self, a=0.0, b=0.0, c=0.0):
        self.a, self.b, self.c = float(a), float(b), float(c)

    def copy(self):
        return _Cov2(self.a, self.b, self.c)

    def predict(self, dt, f, q_w, q_r):
        a, b, c = self.a, self.b, self.c
        dt2 = dt * dt
        self.a = a + 2.0 * dt * b + dt2 * c + q_w * dt2 * dt / 3.0 \
            + q_r * dt
        self.b = f * (b + dt * c) + q_w * dt2 / 2.0
        self.c = f * f * c + q_w * dt

    def update(self, r_v):
        """Joseph-form measurement update with H = [1, 0]; returns the
        gain (k1, k2)."""
        a, b, c = self.a, self.b, self.c
        s = a + r_v
        k1, k2 = a / s, b / s
        m = 1.0 - k1
        self.a = m * m * a + k1 * k1 * r_v
        self.b = m * (b - k2 * a) + k1 * k2 * r_v
        self.c = k2 * k2 * a - 2.0 * k2 * b + c + k2 * k2 * r_v
        return k1, k2

    def matrix(self):
        return np.array([[self.a, self.b], [self.b, self.c]])


class _QuatSpace:
    """Tangent-space operations for a 3-DOF quaternion track."""
    zero = staticmethod(lambda: np.zeros(3))

    def __init__(self, projector=None):
        self.projector = projector

    def from_quat(self, q, ref):
        return qnormalize(q)

    def to_quat(self, x):
        return x.copy()

    def project(self, x):
        return x if self.projector is None else self.projector(x)

    def minus(self, x, ref):        # x boxminus ref, tangent at ref
        return qlog(qmul(qconj(ref), x))

    def plus(self, ref, v):         # ref boxplus v
        return qmul(ref, qexp(v))


class _TwistSpace:
    """Scalar angle about +x (unwrapped) for the 1-DOF twist track."""
    zero = staticmethod(lambda: 0.0)
    projector = None

    def from_quat(self, q, ref):
        a = _twist_angle(qnormalize(q))
        return a if ref is None else ref + _wrap(a - ref)

    def to_quat(self, x):
        return quat_about(_X, x)

    def project(self, x):
        return x

    def minus(self, x, ref):
        return _wrap(x - ref)

    def plus(self, ref, v):
        return ref + v


@register_smoother
class TangentKalmanSmoother(QuatSmoother):
    """Constant-velocity Kalman filter in the tangent space (module
    docstring). params per kind: q_w, q_r, r_v (degrees), decay_lambda
    (null -> S2's), lag_frames (0)."""
    name = "tangent_kf"

    def __init__(self, kind, params, freq_hz, projector=None):
        if params is None:
            raise ValueError(f"tangent_kf needs smoother_params.{kind}")
        for k in ("q_w", "q_r", "r_v", "decay_lambda"):
            if params.get(k) is None:
                raise ValueError(f"smoother_params.{kind}.{k} is null "
                                 "(D-006)")
        self.kind = kind
        self.dt = 1.0 / float(freq_hz)
        self.q_w = float(params["q_w"]) * _D2R2
        self.q_r = float(params["q_r"]) * _D2R2
        self.r_v = float(params["r_v"]) * _D2R2
        if self.r_v <= 0.0 or self.q_w < 0.0 or self.q_r < 0.0:
            raise ValueError("tangent_kf needs r_v > 0, q_w >= 0, q_r >= 0")
        self.decay = float(params["decay_lambda"])
        self.lag = int(params.get("lag_frames", 0) or 0)
        if self.lag < 0:
            raise ValueError("lag_frames must be >= 0")
        self.sp = (_TwistSpace() if kind == "twist"
                   else _QuatSpace(projector))
        self.reset()

    # -- state -----------------------------------------------------
    def reset(self):
        self.x = None               # orientation (quat) or angle
        self.w = None               # velocity, rad/s (3-vec or float)
        self.P = None               # _Cov2
        self.n_since = 0            # frames since x was last set
        self.vel_init = False
        self._hist = []             # fixed-lag RTS buffer

    def covariance(self):
        """The 2x2 per-axis covariance block (diagnostics, tests)."""
        return None if self.P is None else self.P.matrix()

    def _out(self, x):
        return self.sp.to_quat(x)

    def _predict(self, f):
        """Damped constant-velocity predict (f = velocity factor)."""
        self.x = self.sp.plus(self.x, self.w * self.dt)
        self.w = self.w * f
        if self.P is not None:
            self.P.predict(self.dt, f, self.q_w, self.q_r)
        self.n_since += 1

    # -- contract --------------------------------------------------
    def update(self, q_meas, measured):
        """q_meas: unit quat or None; measured: False on S2's predicted
        frames (module docstring). Returns a unit quaternion (None only
        before the first sample with q_meas None)."""
        if q_meas is None or not measured:
            if self.x is None:
                return q_meas
            self._predict(self.decay)
            self._hist = []
            if q_meas is None:
                self.x = self.sp.project(self.x)
                return self._out(self.x)
            # S2 predicted frame: re-synchronise to the track output
            self.x = self.sp.project(self.sp.from_quat(q_meas, self.x))
            self.n_since = 0
            return q_meas

        if self.x is None:                          # first sample
            self.x = self.sp.project(self.sp.from_quat(q_meas, None))
            self.w = self.sp.zero()
            self.n_since = 0
            self.vel_init = False
            self._hist = []
            return self._out(self.x)
        z = self.sp.from_quat(q_meas, self.x)
        if not self.vel_init:                       # two-point init
            # n_since unmeasured frames lie between the two samples, so
            # they are n_since + 1 frame intervals apart
            T = (self.n_since + 1) * self.dt
            self.w = self.sp.minus(z, self.x) / T
            self.x = self.sp.project(z)
            R = self.r_v
            self.P = _Cov2(R, R / T, 2.0 * R / (T * T))
            self.vel_init = True
            self.n_since = 0
            self._hist = []
            return self._out(self.x)

        # predict
        self._predict(1.0)
        x_pr, w_pr, P_pr = self.x, self.w, self.P.copy()
        # update in the tangent space at the prior, then re-linearise
        y = self.sp.minus(z, self.x)
        k1, k2 = self.P.update(self.r_v)
        self.x = self.sp.project(self.sp.plus(self.x, k1 * y))
        self.w = self.w + k2 * y
        self.n_since = 0
        if self.lag == 0:
            return self._out(self.x)
        return self._out(self._fixed_lag(x_pr, w_pr, P_pr))

    # -- optional fixed-lag RTS (off by default) --------------------
    def _fixed_lag(self, x_pr, w_pr, P_pr):
        """Append this frame and return the RTS-smoothed estimate of
        frame t - lag (the oldest buffered frame while the buffer
        fills). Each entry: filtered (x, w, P) and the prior of the
        NEXT frame, which is filled when that frame arrives."""
        if self._hist:
            self._hist[-1]["next_prior"] = (x_pr, w_pr, P_pr)
        self._hist.append({"x": self.x, "w": self.w,
                           "P": self.P.copy(), "next_prior": None})
        if len(self._hist) > self.lag + 1:
            self._hist.pop(0)
        xs, ws = self._hist[-1]["x"], self._hist[-1]["w"]
        dt = self.dt
        for e in reversed(self._hist[:-1]):
            xp, wp, Pp = e["next_prior"]
            Pk = e["P"]
            # C = Pk F^T Pp^-1, F = [[1, dt], [0, 1]]
            fa = Pk.a + dt * Pk.b
            fb = Pk.b
            fc = Pk.b + dt * Pk.c
            fd = Pk.c
            det = Pp.a * Pp.c - Pp.b * Pp.b
            ia, ib, ic = Pp.c / det, -Pp.b / det, Pp.a / det
            c11 = fa * ia + fb * ib
            c12 = fa * ib + fb * ic
            c21 = fc * ia + fd * ib
            c22 = fc * ib + fd * ic
            dr = self.sp.minus(xs, xp)
            dw = ws - wp
            xs = self.sp.project(
                self.sp.plus(e["x"], c11 * dr + c12 * dw))
            ws = e["w"] + c21 * dr + c22 * dw
        return xs

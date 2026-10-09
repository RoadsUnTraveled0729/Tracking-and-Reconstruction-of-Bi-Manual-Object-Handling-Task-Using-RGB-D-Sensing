"""Quaternion toolbox for V3's internal orientation state (D-005).

Convention: q = [w, x, y, z], unit norm, scalar first. matrix_from_quat
follows the standard formula, so a quaternion about +x by angle a
reproduces exactly the Rx(a) matrix used by the vendored v1 solvers
(and likewise y/z); handedness questions live entirely in the vectors,
not here. Rotation vectors ("rotvec") are axis * angle in radians.

Everything is float64 and pure numpy. Strategies (Phase 4) operate on
these primitives; v1 angle definitions exist only in core/convert.py.
"""
import numpy as np

_EPS = 1e-12

QUAT_ID = np.array([1.0, 0.0, 0.0, 0.0])


def qnormalize(q):
    q = np.asarray(q, dtype=float)
    n = np.linalg.norm(q)
    if n < _EPS:
        raise ValueError("cannot normalize a near-zero quaternion")
    return q / n


def qmul(a, b):
    """Hamilton product a*b (apply b first, then a, like matrix product)."""
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return np.array([
        aw * bw - ax * bx - ay * by - az * bz,
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
    ])


def qconj(q):
    return np.array([q[0], -q[1], -q[2], -q[3]])


def qrotate(q, v):
    """Rotate vector v by unit quaternion q."""
    qv = np.array([0.0, v[0], v[1], v[2]])
    return qmul(qmul(q, qv), qconj(q))[1:]


def quat_about(axis, angle_rad):
    """Unit quaternion rotating by angle_rad about a unit axis."""
    axis = np.asarray(axis, dtype=float)
    half = 0.5 * angle_rad
    return np.concatenate([[np.cos(half)], np.sin(half) * axis])


def matrix_from_quat(q):
    """Unit quaternion -> 3x3 rotation matrix (standard formula)."""
    w, x, y, z = qnormalize(q)
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
        [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
        [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
    ])


def quat_from_matrix(R):
    """3x3 rotation matrix -> unit quaternion, w >= 0 (Shepperd)."""
    R = np.asarray(R, dtype=float)
    t = np.trace(R)
    if t > 0:
        s = np.sqrt(t + 1.0) * 2.0
        q = np.array([0.25 * s,
                      (R[2, 1] - R[1, 2]) / s,
                      (R[0, 2] - R[2, 0]) / s,
                      (R[1, 0] - R[0, 1]) / s])
    else:
        i = int(np.argmax(np.diag(R)))
        j, k = (i + 1) % 3, (i + 2) % 3
        s = np.sqrt(max(_EPS, 1.0 + R[i, i] - R[j, j] - R[k, k])) * 2.0
        q = np.empty(4)
        q[0] = (R[k, j] - R[j, k]) / s
        q[1 + i] = 0.25 * s
        q[1 + j] = (R[j, i] + R[i, j]) / s
        q[1 + k] = (R[k, i] + R[i, k]) / s
    if q[0] < 0:
        q = -q
    return qnormalize(q)


def qexp(rotvec):
    """Rotation vector (axis * angle, rad) -> unit quaternion."""
    rotvec = np.asarray(rotvec, dtype=float)
    angle = np.linalg.norm(rotvec)
    if angle < _EPS:
        return np.concatenate([[1.0], 0.5 * rotvec])  # first-order
    return quat_about(rotvec / angle, angle)


def qlog(q):
    """Unit quaternion -> rotation vector (axis * angle, rad), the
    inverse of qexp on the w >= 0 hemisphere; |result| <= pi."""
    q = qnormalize(q)
    if q[0] < 0:
        q = -q
    vn = np.linalg.norm(q[1:])
    if vn < _EPS:
        return 2.0 * q[1:]  # first-order
    angle = 2.0 * np.arctan2(vn, q[0])
    return angle * q[1:] / vn


def hemisphere(q, q_ref):
    """Flip q's sign if needed so dot(q, q_ref) >= 0 (same-hemisphere
    continuity for filtering and blending)."""
    q = np.asarray(q, dtype=float)
    return -q if float(np.dot(q, np.asarray(q_ref, dtype=float))) < 0 else q


def slerp(q0, q1, s):
    """Geodesic interpolation from q0 (s=0) to q1 (s=1), shortest arc."""
    q0 = qnormalize(q0)
    q1 = hemisphere(qnormalize(q1), q0)
    d = float(np.clip(np.dot(q0, q1), -1.0, 1.0))
    if d > 1.0 - 1e-9:
        return qnormalize(q0 + s * (q1 - q0))
    ang = np.arccos(d)
    return qnormalize((np.sin((1.0 - s) * ang) * q0 + np.sin(s * ang) * q1)
                      / np.sin(ang))


def angle_between(q0, q1):
    """Geodesic angle (rad) between two orientations."""
    return float(np.linalg.norm(qlog(qmul(qconj(qnormalize(q0)),
                                          qnormalize(q1)))))


def swing_twist(q, axis):
    """Decompose q = q_swing * q_twist with q_twist a rotation about
    `axis` (unit) and q_swing moving the axis itself.

    Projection method: twist = normalize([w, (v . axis) axis]); a 180
    degree swing (projection ~ 0) yields identity twist by convention.
    """
    q = qnormalize(q)
    axis = np.asarray(axis, dtype=float)
    proj = float(np.dot(q[1:], axis))
    tw = np.concatenate([[q[0]], proj * axis])
    n = np.linalg.norm(tw)
    if n < _EPS:
        twist = QUAT_ID.copy()
    else:
        twist = tw / n
        if twist[0] < 0:
            twist = -twist
    swing = qmul(q, qconj(twist))
    return qnormalize(swing), twist


class QuatOneEuro:
    """One Euro filter on the rotation manifold.

    Same parameter semantics as the v1 landmark OneEuro (freq in Hz,
    min_cutoff, beta, d_cutoff): the angular speed (rad/s, from the
    log-map between consecutive raw samples, EMA-smoothed at d_cutoff)
    raises the cutoff via beta, and the state slerps toward the sample
    with the resulting alpha. First sample initializes the state.
    """

    def __init__(self, freq, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        if freq <= 0:
            raise ValueError("freq must be positive")
        self.freq = float(freq)
        self.min_cutoff = float(min_cutoff)
        self.beta = float(beta)
        self.d_cutoff = float(d_cutoff)
        self._q = None        # filtered state
        self._raw = None      # previous raw sample (for the derivative)
        self._speed = 0.0     # filtered angular speed, rad/s

    @staticmethod
    def _alpha(cutoff, freq):
        tau = 1.0 / (2.0 * np.pi * cutoff)
        return 1.0 / (1.0 + tau * freq)

    def reset(self):
        self._q = None
        self._raw = None
        self._speed = 0.0

    def __call__(self, q):
        q = qnormalize(q)
        if self._q is None:
            self._q = q
            self._raw = q
            return q.copy()
        q = hemisphere(q, self._q)
        speed = np.linalg.norm(
            qlog(qmul(qconj(self._raw), q))) * self.freq
        a_d = self._alpha(self.d_cutoff, self.freq)
        self._speed += a_d * (speed - self._speed)
        cutoff = self.min_cutoff + self.beta * self._speed
        self._q = slerp(self._q, q, self._alpha(cutoff, self.freq))
        self._raw = q
        return self._q.copy()

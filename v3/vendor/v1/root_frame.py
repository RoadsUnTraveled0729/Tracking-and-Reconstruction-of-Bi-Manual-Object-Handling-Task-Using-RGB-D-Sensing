"""Root-frame construction and Unity Euler conversion (KINEMATIC_MODEL.md §3-4).

All functions operate on Unity-space points (left-handed, X right, Y up,
Z forward). Rotation representation: matrices + Unity ZXY-applied Euler
(R = Ry·Rx·Rz), per the base-variant policy.
"""
import numpy as np

SENSOR_TO_UNITY = np.array([1.0, -1.0, 1.0])


def unity_from_sensor(p):
    """RealSense optical frame -> Unity frame: (x, y, z) -> (x, -y, z)."""
    return np.asarray(p, dtype=float) * SENSOR_TO_UNITY


def normalize(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def build_root_frame(p23, p24, p12):
    """L24 root frame from Unity-space left hip, right hip, right shoulder.

    Columns of R are the person's [right | up | forward] in Unity world.
    The hip line is the trusted primary axis; the spine-ish vector 24->12
    only selects the coronal plane; up is recovered by the final cross.
    """
    r = normalize(p24 - p23)                # person's anatomical right
    s = p12 - p24                           # spine-ish, roughly up
    f = normalize(np.cross(r, s))           # person's forward (out of chest)
    u = np.cross(f, r)                      # exact up, unit by construction
    return np.stack([r, u, f], axis=-1)


def euler_unity_zxy(R):
    """Matrix -> Unity Euler degrees (applied order Z, then X, then Y).

    x = asin(-m12); y = atan2(m02, m22); z = atan2(m10, m11).
    Gimbal lock at x = +/-90 deg: z := 0, y from row 0.
    """
    m12 = np.clip(R[..., 1, 2], -1.0, 1.0)
    x = -np.arcsin(m12)
    y = np.arctan2(R[..., 0, 2], R[..., 2, 2])
    z = np.arctan2(R[..., 1, 0], R[..., 1, 1])
    lock = np.abs(m12) > 1.0 - 1e-8
    if np.any(lock):
        y_lock = np.where(
            m12 < 0,  # x = +90
            np.arctan2(R[..., 0, 1], R[..., 0, 0]),
            np.arctan2(-R[..., 0, 1], R[..., 0, 0]),
        )
        y = np.where(lock, y_lock, y)
        z = np.where(lock, 0.0, z)
    return np.degrees(np.stack([x, y, z], axis=-1))


def recompose_zxy(deg):
    """Euler degrees (x, y, z) -> R = Ry·Rx·Rz (Unity convention)."""
    x, y, z = np.radians(np.asarray(deg, dtype=float))
    cx, sx, cy, sy, cz, sz = np.cos(x), np.sin(x), np.cos(y), np.sin(y), np.cos(z), np.sin(z)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Ry @ Rx @ Rz


def wrap_deg(a):
    """Wrap angle degrees to (-180, 180]."""
    return -((-np.asarray(a) + 180.0) % 360.0 - 180.0)

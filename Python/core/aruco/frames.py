"""Pipeline B (ArUco) shared frame math — ARUCO_MODEL.md.

Deliberately self-contained: Pipeline B imports nothing from kinematics/ or
mediapipe/ (Pipelines A and B stay independent until evaluation), so
euler_unity_zxy / recompose_zxy are intentional small duplicates of the
Pipeline A versions — same Unity ZXY-applied convention (KINEMATIC_MODEL.md
§4), byte-for-byte identical math.

Frames:
  camera  — RealSense color optical: X right, Y down, Z forward, meters.
            A marker's (R, t) maps marker-frame points into the camera frame.
  world   — the DESK marker's own frame (id 2, user-chosen anchor): x/y in
            the printed plane, z out of the printed face. Everything —
            wall, object, and the camera itself — is expressed here, which
            is what makes the reconstruction camera-placement invariant.
  Unity   — left-handed, Y up. world -> Unity is the axis swap y<->z
            (marker z, out of the face, becomes Unity up), which also
            converts right- to left-handed.

Rotation representation: matrices + Unity ZXY-applied Euler only (project
policy). No quaternions anywhere.
"""
import numpy as np

# id -> (role, printed side length in meters); user-confirmed 2026-07-19.
MARKERS = {
    0: ("wall", 0.150),
    2: ("desk", 0.050),
    1: ("object", 0.050),
}
MARKER_IDS = sorted(MARKERS)
STATIC_IDS = (0, 2)
OBJECT_ID = 1
WORLD_ID = 2  # desk marker anchors the world frame

# world (right-handed, z out of the desk marker face) -> Unity (left-handed,
# y up): swap y and z. P is symmetric and its own inverse.
WORLD_TO_UNITY = np.array([[1.0, 0.0, 0.0],
                           [0.0, 0.0, 1.0],
                           [0.0, 1.0, 0.0]])

R_COLS = [f"r{i}{j}" for i in (1, 2, 3) for j in (1, 2, 3)]


def rt_from_row(row, mid):
    """(R, t) of marker `mid` from one raw-CSV row, or None if not detected."""
    p = f"m{mid}"
    if not row[f"{p}_detected"]:
        return None
    R = np.array([row[f"{p}_{c}"] for c in R_COLS], dtype=float).reshape(3, 3)
    t = np.array([row[f"{p}_tx"], row[f"{p}_ty"], row[f"{p}_tz"]], dtype=float)
    return R, t


def make_T(R, t):
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t
    return T


def inv_T(T):
    R, t = T[:3, :3], T[:3, 3]
    return make_T(R.T, -R.T @ t)


def chordal_mean(Rs):
    """Chordal mean of rotation matrices: element-wise mean projected back
    onto SO(3) via SVD (UVᵀ, det=+1 enforced). Matrices only — no
    quaternion detour."""
    M = np.mean(np.asarray(Rs, dtype=float), axis=0)
    U, _, Vt = np.linalg.svd(M)
    R = U @ np.diag([1.0, 1.0, np.linalg.det(U @ Vt)]) @ Vt
    return R


def geodesic_deg(Ra, Rb):
    """Rotation angle between Ra and Rb in degrees, well-conditioned near 0
    (atan2 of the skew part, not arccos of the trace — FINDINGS 2026-07-17)."""
    D = Ra.T @ Rb
    v = 0.5 * np.array([D[2, 1] - D[1, 2], D[0, 2] - D[2, 0], D[1, 0] - D[0, 1]])
    return float(np.degrees(np.arctan2(np.linalg.norm(v), 0.5 * (np.trace(D) - 1.0))))


def unity_from_world(R_w, t_w):
    """Pose in the world (desk) frame -> Unity position + rotation matrix."""
    return WORLD_TO_UNITY @ np.asarray(t_w, float), \
        WORLD_TO_UNITY @ np.asarray(R_w, float) @ WORLD_TO_UNITY


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

"""Right-shoulder swing-twist solve (KINEMATIC_MODEL.md §6).

Joint parameterization (derived, not Unity's Euler order):

    R_sh = Ry(θy) · Rz(θz) · Rx(θτ)

with the twist θτ INNERMOST, about the rest arm axis +x (the person's
right). The two outer angles are the swing (they alone determine where the
upper arm points, since Rx(θτ)·x̂ = x̂). All vectors are expressed in the
torso basis: the L12 shoulder frame inherits the L24 root orientation with
its origin moved to landmark 12.

Zero conventions:
- rest upper arm: local +x (T-pose, arm straight out to the person's right)
- zero twist: the forearm's component perpendicular to the arm axis points
  along local +z (elbow flexes forward). Positive twist = internal rotation
  (forearm-forward rotates toward -y / downward).

To drive a Unity bone, convert the resulting matrix through the §4 ZXY
extraction — (θy, θz, θτ) are joint coordinates, NOT Unity Euler angles.
"""
import numpy as np

from root_frame import normalize

GIMBAL_EPS = 1e-8   # |sin θz| within this of 1 -> arm vertical, θy := 0
TWIST_EPS = 1e-6    # forearm ⊥-fraction below this -> twist unobservable


def _rx(rad):
    c, s = np.cos(rad), np.sin(rad)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def _ry(rad):
    c, s = np.cos(rad), np.sin(rad)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def _rz(rad):
    c, s = np.cos(rad), np.sin(rad)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def recompose_shoulder(deg):
    """(θy, θz, θτ) degrees -> R_sh = Ry·Rz·Rx (validation round-trip)."""
    y, z, t = np.radians(np.asarray(deg, dtype=float))
    return _ry(y) @ _rz(z) @ _rx(t)


def solve_right_shoulder(p12, p14, p16, R_root):
    """Swing-twist angles of the right shoulder from Unity-space landmarks.

    p12/p14/p16: right shoulder / elbow / wrist in Unity space.
    R_root: L24 root frame (columns [right|up|forward], KINEMATIC_MODEL §3).

    Returns (angles_deg, twist_ok):
      angles_deg = (θy, θz, θτ); θτ is NaN when the elbow is straight
      (forearm parallel to the arm axis -> twist unobservable from
      landmarks alone), twist_ok False in that case.

    Swing: â = R_rootᵀ(p14-p12)/|·| = Ry·Rz·x̂ = (cy·cz, sz, -sy·cz)
      -> θz = asin(ây), θy = atan2(-âz, âx); gimbal at θz = ±90°: θy := 0
         (axial rotation then folds into θτ by construction).
    Twist: un-swing the forearem f = R_rootᵀ(p16-p14) with R_swingᵀ, then
      f' = Rx(θτ)·(rest forearm ∝ ẑ) ⊥-part = (-sinθτ, cosθτ)·|f⊥| in (y,z)
      -> θτ = atan2(-f'y, f'z), measured in the y-z plane (the plane
      perpendicular to the rotation axis x).
    """
    a = normalize(np.asarray(R_root).T @ (np.asarray(p14) - np.asarray(p12)))
    sz = np.clip(a[1], -1.0, 1.0)
    th_z = np.arcsin(sz)
    if 1.0 - abs(sz) < GIMBAL_EPS:
        th_y = 0.0
    else:
        th_y = np.arctan2(-a[2], a[0])

    f = np.asarray(R_root).T @ (np.asarray(p16) - np.asarray(p14))
    fp = _rz(-th_z) @ (_ry(-th_y) @ f)
    perp = np.hypot(fp[1], fp[2])
    twist_ok = perp >= TWIST_EPS * np.linalg.norm(f)
    th_t = np.arctan2(-fp[1], fp[2]) if twist_ok else np.nan

    return np.degrees(np.array([th_y, th_z, th_t])), twist_ok


def solve_right_arm(p12, p14, p16, R_root):
    """Full right-arm solve: shoulder swing-twist + elbow swing (§6-7).

    The elbow parent frame (L14) is the fully-rotated upper-arm frame
    R_arm = R_root · Ry(θy)·Rz(θz)·Rx(θτ), origin at landmark 14; the rest
    forearm continues the arm axis (local +x, straight elbow). The forearm
    is expressed there and its two swing angles solved with the SAME
    parameterization as the shoulder swing (R_elbow = Ry(ey)·Rz(ez),
    twist ignored - forearm pronation is unobservable from landmarks):

        ĝ = R_armᵀ (p16-p14)/|·| = (cy·cz, sz, -sy·cz)
        ez = asin(ĝy)          ("up/down" swing out of the flexion plane)
        ey = atan2(-ĝz, ĝx)    (flexion; 0 = straight, -90 = right angle)

    NOTE (derived, validated): because the shoulder twist θτ is itself
    measured from the forearm - it is DEFINED as the rotation aligning the
    forearm's perpendicular component with local +z - the flexion plane is
    already rotated into x-z when the elbow is solved, so ez ≡ 0
    identically and ey ≤ 0. The elbow's "up/down" DOF is not lost: it IS
    the shoulder twist. 3 landmarks give 4 observable rotational DOF
    (2 swing + 1 twist + 1 flexion); ez is kept in the interface for
    generality but carries no independent information.

    When the elbow is straight (twist unobservable) the convention
    θτ := 0 is applied so the arm frame stays defined; ey then decodes 0.

    Returns (shoulder_deg (θy, θz, θτ), elbow_deg (ey, ez), twist_ok).
    """
    sh, twist_ok = solve_right_shoulder(p12, p14, p16, R_root)
    if not twist_ok:
        sh = sh.copy()
        sh[2] = 0.0
    y, z, t = np.radians(sh)
    R_arm = np.asarray(R_root) @ (_ry(y) @ _rz(z) @ _rx(t))
    g = normalize(R_arm.T @ (np.asarray(p16) - np.asarray(p14)))
    ez = np.arcsin(np.clip(g[1], -1.0, 1.0))
    ey = np.arctan2(-g[2], g[0])
    return sh, np.degrees(np.array([ey, ez])), twist_ok


MIRROR = np.array([-1.0, 1.0, 1.0])  # sagittal reflection in the root basis


def solve_left_arm(p11, p13, p15, R_root):
    """LEFT arm (L11 shoulder / L13 elbow / L15 wrist) via mirroring (§9).

    Left angles are DEFINED as the right-solver angles of the sagittally
    mirrored pose: express both segment vectors in the root basis, flip
    their x components (M = diag(-1,1,1)), and run the identical right-arm
    solve. Consequences (derived, not re-implemented):
      - a mirror-symmetric pose yields IDENTICAL angle values on both sides
        (θy+ = backward sweep, θz+ = up, θτ+ = internal rotation,
        ey = flexion in [-180, 0] - same anatomical meaning);
      - every §6-7 property (twist plane, ez ≡ 0, singularities) carries
        over verbatim, since M conjugation preserves the construction.
    Reconstruction in world coords uses M·R·M, i.e. flip the SIGNS of the
    y- and z-axis angles and keep the twist sign:
      chain_L = Ry(-θy)·Rz(-θz)·Rx(θτ)·Ry(-ey)·Rz(-ez), rest arm = -x̂.

    Returns (shoulder_deg (θy, θz, θτ), elbow_deg (ey, ez), twist_ok).
    """
    R_root = np.asarray(R_root)
    u = MIRROR * (R_root.T @ (np.asarray(p13) - np.asarray(p11)))
    f = MIRROR * (R_root.T @ (np.asarray(p15) - np.asarray(p13)))
    zero = np.zeros(3)
    return solve_right_arm(zero, u, u + f, np.eye(3))

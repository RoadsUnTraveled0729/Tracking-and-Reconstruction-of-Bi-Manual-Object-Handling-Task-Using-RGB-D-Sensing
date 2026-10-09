# 0. Notation, frames, and conventions

All chapters use the symbols defined here. The governing representation
rule of the project: **rotations are $3\times3$ matrices $R \in SO(3)$
and Unity ZXY-applied Euler angles only.** Quaternions never appear in
the mathematics; they occur solely as opaque intermediates inside Unity's
API (`Quaternion.Euler`, bone `rotation` properties), which this text
treats as matrix operations.

## 0.1 Coordinate frames

| symbol | frame | axes | handedness |
|---|---|---|---|
| $\mathcal{C}$ | camera (RealSense optical) | $x$ right, $y$ **down**, $z$ forward (into scene), meters | right |
| $\mathcal{P}$ | person space ("Unity-from-sensor") | $\mathcal{C}$ with $y$ flipped: $x$ right, $y$ up, $z$ forward | left |
| $\mathcal{W}$ | world = desk-marker frame | marker $x,y$ in the marker plane, $z$ out of the face | right |
| $\mathcal{U}$ | Unity scene | $x$ right, $y$ up, $z$ forward | left |
| $\mathcal{L}$ | leveled world | $\mathcal{U}$ re-oriented so measured gravity is exactly $-y$ | left |

Two fixed change-of-basis maps connect them:

$$
F = \mathrm{diag}(1,-1,1) \quad (\mathcal{C}\to\mathcal{P}), \qquad
P = \begin{bmatrix}1&0&0\\0&0&1\\0&1&0\end{bmatrix} \quad (\mathcal{W}\to\mathcal{U}).
$$

Both are reflections ($\det = -1$), which is exactly what a change of
handedness requires; each is its own inverse. $F$ is applied to **points
only** — all Pipeline A rotations are constructed *after* the flip from
already-flipped points, so no rotation is ever conjugated by $F$
(A2 §1). $P$ conjugates Pipeline B rotations: $R_\mathcal{U} = P R_\mathcal{W} P$
(B1 §7).

## 0.2 Rotation conventions

Column-vector convention throughout: $p' = R\,p$, and composition reads
right-to-left. The elementary rotations (Unity's numeric convention,
valid as written in its left-handed basis — see A2 §2):

$$
R_x(\theta)=\begin{bmatrix}1&0&0\\0&c&-s\\0&s&c\end{bmatrix},\quad
R_y(\theta)=\begin{bmatrix}c&0&s\\0&1&0\\-s&0&c\end{bmatrix},\quad
R_z(\theta)=\begin{bmatrix}c&-s&0\\s&c&0\\0&0&1\end{bmatrix}
$$

with $c=\cos\theta$, $s=\sin\theta$. **Unity Euler** $(x,y,z)$ means the
ZXY-applied product

$$
R = R_y(y)\,R_x(x)\,R_z(z),
$$

i.e. Unity rotates about $z$ first, then $x$, then $y$, all about parent
axes (derived and validated in A2 §3). Angles are degrees in prose,
radians in derivations where noted; ranges $(-180°, 180°]$ unless stated.

## 0.3 Points and landmarks

$p_i \in \mathbb{R}^3$ is the 3-D position of MediaPipe landmark $i$;
"L$i$" names the landmark. Landmarks in scope (all of Pipeline A):

| id | name | id | name |
|---|---|---|---|
| 11 | left shoulder | 12 | right shoulder |
| 13 | left elbow | 14 | right elbow |
| 15 | left wrist | 16 | right wrist |
| 23 | left hip | 24 | right hip |

Unit vectors wear hats ($\hat r$); $\times$ is the numeric cross
product; $\|\cdot\|$ the Euclidean norm. Time series are indexed by
frame $t$ (30 fps, $\Delta t \approx 33.3$ ms).

## 0.4 ArUco markers (Pipeline B)

DICT_5X5_50, sizes user-confirmed (same prints as the reference
project):

| id | role | side length | behavior |
|---|---|---|---|
| 0 | wall | 150 mm | static; **plumb** — defines gravity |
| 2 | desk | 50 mm | static; **world anchor** (origin of $\mathcal{W}$) |
| 1 | object | 50 mm | on one face of a 70 mm cube, carried |

Rigid transforms are written $T^{a}_{b} = (R^{a}_{b}, t^{a}_{b})$,
mapping frame-$b$ coordinates into frame $a$:
$p_a = R^{a}_{b}\,p_b + t^{a}_{b}$.

## 0.5 Recordings

Both 899 frames, 640×480 @ 30 fps, Intel RealSense (aligned depth +
color), ~30 s:

- **`recording_20260224_083945`** — the ACTIVE evaluation recording: the
  person stands at the desk and **carries the 70 mm cube** (1.94 m of
  smoothed travel), parking it on the desk for $t \approx$ 13.5–23 s.
  Camera at the desk edge. Used for the integrated evaluation (C1).
- **`recording_20260328_021733`** — seated person, object untouched,
  camera high, desk marker on a 31.8° stand. Used for Pipeline B
  development and cross-validation.
- **`recording_20260225_230607`** — standing person, arms moving; used
  for the real-data kinematic validation (A2 §9).

Synthetic known-truth datasets (`kinematics/make_synthetic_*.py`)
provide exact ground truth for solver validation; the real recordings
validate invariants and plausibility (no external truth exists for the
person's joints — that gap is precisely what Pipeline B fills at the
object level, C1).

## 0.6 Statistical conventions

- Angle between unit vectors: $\theta = \mathrm{atan2}(\|a \times b\|,\ a\cdot b)$
  — never $\arccos(a \cdot b)$, which is ill-conditioned near 0° (D1 §9).
- Yaw statistics near ±180° use circular statistics (D1 §9).
- "p95" = 95th percentile; "RMS" = root mean square; errors are reported
  per frame over all frames unless stated.

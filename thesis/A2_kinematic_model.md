# A2. Pipeline A — the kinematic model

From filtered 3-D landmarks to a minimal set of anatomical joint angles
(pelvis orientation + per-arm shoulder swing–twist + elbow flexion), and
from those angles back to segment directions (the solve is an exact
inverse) and onto a Unity rig. Everything is matrices and Unity
ZXY-applied Euler (§0.2); the solve is closed-form on every frame — no
optimization, no temporal state (except the declared occlusion holds,
A3).

Implementation: `kinematics/shoulder.py`, `kinematics/occlusion.py`,
`kinematics/validate_root_frame.py`, `kinematics/validate_shoulder.py`.

## 1. Sensor space → person space

The RealSense optical frame $\mathcal{C}$ is right-handed with $y$
down; person space $\mathcal{P}$ (the frame all Pipeline A math lives
in) flips one axis:

$$
q = F\,p_\mathcal{C}, \qquad F = \mathrm{diag}(1,-1,1).
$$

$F$ is a reflection ($\det F = -1$): flipping exactly one axis is what
converts right-handed to left-handed. The rule that keeps handedness
bookkeeping trivial for the rest of the pipeline: **$F$ is applied to
points only, never to rotations.** Every rotation below is *constructed*
from already-flipped points, so no rotation matrix is ever conjugated by
a reflection, and all of them come out proper ($\det = +1$) by
construction — verified to $+1.000000$ on all 899 frames of real data.

## 2. The root frame at L24 (right hip)

### 2.1 Construction

With $p_{23}, p_{24}, p_{12}$ the person-space positions of the hips and
right shoulder:

$$
\hat r = \frac{p_{24} - p_{23}}{\|p_{24} - p_{23}\|}
\quad\text{(anatomical right)},\qquad
s = p_{12} - p_{24} \quad\text{("spine-ish", selects the coronal plane)},
$$

$$
\hat f = \frac{\hat r \times s}{\|\hat r \times s\|}
\quad\text{(forward, out of the chest)},\qquad
\hat u = \hat f \times \hat r \quad\text{(up; exactly unit by construction)}.
$$

This is Gram–Schmidt with a deliberate trust ordering: the hip line
$23\to24$ is kept **exactly** (both endpoints are pelvis landmarks — it
*is* the segment being posed), while $s$ contributes only its component
perpendicular to $\hat r$ (the parallel part is annihilated by the cross
product). $\hat u$ is the unique third axis. The root rotation is the
matrix whose columns are the frame axes in Unity's
right/up/forward order:

$$
R_{root} = \bigl[\, \hat r \;\big|\; \hat u \;\big|\; \hat f \,\bigr].
$$

### 2.2 Why no handedness correction is needed

The numeric cross-product formula is basis-independent algebra, and
Unity's own basis satisfies the cyclic identities
$\hat x \times \hat y = \hat z$, etc., *numerically* — the "left-hand
rule" is only the geometric visualization. A triad built as
$\hat r,\ \hat f = \hat r \times s,\ \hat u = \hat f \times \hat r$
therefore satisfies the same cyclic identities as Unity's world axes,
and $\det R_{root} = +1$ with no sign flip anywhere. Properness alone
does not pin the *assignment* (an axis-permuted variant is also proper);
the assignment is pinned by the reference-pose test below.

### 2.3 Reference pose and rig alignment

Adopted alignment: *a Unity humanoid with identity hip rotation stands
upright facing world $+z$, right side toward $+x$.* An ideal upright
person facing the sensor (which looks along $+z$) has their right toward
the camera's left and their chest toward $-z$:

$$
R_{root}^{ref} = \begin{bmatrix} -1&0&0 \\ 0&1&0 \\ 0&0&-1 \end{bmatrix}
\;\;\Rightarrow\;\; \text{Euler } (0°, 180°, 0°).
$$

The 180° yaw is physically real (the avatar faces the viewer), not an
artifact. The construction reproduces this exactly on a synthetic
reference pose; a plausible-looking alternative construction (the
initial sketch, $X = 24{\to}23$, $Y = X \times (24{\to}12)$,
$Z = X \times Y$) is *also* proper but decodes to $(90°, 0°, 0°)$ — a
rig pitched flat on its back — which is how the reference-pose test
distinguishes correct anatomy from mere properness.

Known simplification: with only 3 points, pelvis and trunk are not
separable, so trunk lean pitches this frame (accepted for the base
variant; D1 §8).

## 3. The Unity Euler convention (ZXY-applied)

Unity applies Euler angles $z$ first, then $x$, then $y$, about parent
axes. As a matrix product (column vectors):

$$
R = R_y(y)\,R_x(x)\,R_z(z).
$$

### 3.1 Composition

$$
R_x R_z =
\begin{bmatrix}
c_z & -s_z & 0\\
c_x s_z & c_x c_z & -s_x\\
s_x s_z & s_x c_z & c_x
\end{bmatrix},
$$

$$
R = R_y (R_x R_z) =
\begin{bmatrix}
c_y c_z + s_y s_x s_z & -c_y s_z + s_y s_x c_z & s_y c_x\\
c_x s_z & c_x c_z & -s_x\\
-s_y c_z + c_y s_x s_z & s_y s_z + c_y s_x c_z & c_y c_x
\end{bmatrix}.
$$

### 3.2 Extraction (matrix → Euler)

Reading elements $m_{ij}$ (0-indexed):

$$
x = \arcsin(-m_{12}) \in [-90°, 90°], \qquad
y = \mathrm{atan2}(m_{02},\, m_{22}), \qquad
z = \mathrm{atan2}(m_{10},\, m_{11}),
$$

valid on the $\cos x > 0$ branch. **Gimbal lock** at $|m_{12}| = 1$
($x = \pm 90°$, $c_x = 0$): $y$ and $z$ rotate about the same effective
axis and only their combination is observable. Substituting
$s_x = \pm1,\ c_x = 0$, row 0 becomes $[\cos(y \mp z),\ \pm\sin(y \mp z),\ 0]$;
convention $z := 0$ and

$$
x = +90°:\; y = \mathrm{atan2}(m_{01}, m_{00}), \qquad
x = -90°:\; y = \mathrm{atan2}(-m_{01}, m_{00}).
$$

The decode stays well-defined at the singularity, but its conditioning
degrades in a neighborhood of it (quantified in D1 §3). Round-trip
(decode → recompose) is exact to $3.6\times10^{-16}$ on real data, and
exact at synthetic $x = \pm 90°$ poses.

## 4. Right shoulder — swing–twist decomposition

### 4.1 Parent frame

The shoulder's parent segment is the torso; its only constructed
orientation is $R_{root}$. The L12 shoulder frame therefore has origin
$p_{12}$ and orientation $R_{root}$ — deriving a separate basis at the
shoulder would silently introduce a shoulder-girdle DOF that 3 torso
landmarks cannot support. Direction vectors are expressed in the parent
frame as $v_{local} = R_{root}^{\mathsf T} v$.

Rest configuration (T-pose): right upper arm along the person's right
⇒ **rest arm axis $= +\hat x$** (local). Zero-twist reference: with the
elbow flexed, the forearm's perpendicular component points along local
$+\hat z$ (elbow flexes forward).

### 4.2 Parameterization — why twist must be innermost

The physical split is *swing* (where the arm points) vs *twist* (roll
about the arm's own long axis). Since a rotation about $\hat x$ leaves
$\hat x$ fixed, writing the joint rotation with twist **innermost**,

$$
R_{sh} = R_y(\theta_y)\,R_z(\theta_z)\,R_x(\theta_\tau),
$$

makes the upper-arm direction depend on swing alone:

$$
\hat a = R_{sh}\,\hat x = R_y(\theta_y) R_z(\theta_z)\,\hat x
= \bigl(c_y c_z,\; s_z,\; -s_y c_z\bigr).
$$

If twist were outermost, the "twist axis" would no longer be the arm
axis after any swing — the decomposition would not be the physical one.
Two consequences: (i) twist is **invisible** in the shoulder→elbow
vector and must be measured from a second, non-collinear segment (the
forearm); (ii) this joint order is *not* Unity's ZXY — driving a bone
requires composing the full matrix and extracting Unity Euler via §3.

### 4.3 Swing extraction

From $\hat a = (c_y c_z,\ s_z,\ -s_y c_z)$ with $c_z \ge 0$ on
$\theta_z \in [-90°, 90°]$:

$$
\theta_z = \arcsin(\hat a_y) \quad\text{(elevation; $+$ = up)},\qquad
\theta_y = \mathrm{atan2}(-\hat a_z,\ \hat a_x) \quad\text{(azimuth; $+$ = backward sweep)}.
$$

Every direction is reachable — no coverage gap. Gimbal lock at
$\theta_z = \pm90°$ (arm vertical): $\hat a_x = \hat a_z = 0$, so
$\theta_y$ is undefined; convention $\theta_y := 0$, and any axial
rotation folds into $\theta_\tau$ automatically (validated: a pose
generated as $(\theta_y, \theta_z) = (30°, 90°)$ decodes to
$(0°, 90°, 30°)$ — the same physical pose).

### 4.4 Twist extraction

Twist is rotation **about** the arm axis, so it must be measured in the
plane **perpendicular to** that axis. Procedure: express the forearm in
the parent basis, remove the swing (bringing the arm axis back to
$\hat x$, so the perpendicular plane is exactly local $y$–$z$), then
read the angle:

$$
f = R_{root}^{\mathsf T}(p_{16} - p_{14}), \qquad
f' = R_z(-\theta_z)\,R_y(-\theta_y)\,f = R_{swing}^{\mathsf T} f,
$$

$$
\theta_\tau = \mathrm{atan2}(-f'_y,\ f'_z).
$$

Derivation of the arguments: at zero twist the un-swung forearm's
perpendicular component is $\propto \hat z$; under $R_x(\theta_\tau)$,
$\hat z \mapsto (0, -\sin\theta_\tau, \cos\theta_\tau)$, so
$(-f'_y, f'_z) \propto (\sin\theta_\tau, \cos\theta_\tau)$.

**Equivalence of 14→16 and 12→16.** Since $p_{14} - p_{12} \parallel \hat a$,
un-swinging $w = p_{16} - p_{12}$ gives $w' = \|ua\|\,\hat x + f'$, and
the projection onto $y$–$z$ annihilates the $\hat x$ term — with the
*correct* projection plane the two choices give identical twist. (The
draft formulation that projected onto a plane *containing* the axis is
analyzed as an error case in §4.5.)

### 4.5 Audit of the earlier draft formulation

Two genuine errors were found in the pre-existing draft of this solve
and are documented because the numeric refutation is instructive:

1. **Projection onto the ZX plane** (a plane containing the rotation
   axis $\hat x$): the $x$-component of any vector is invariant under
   $R_x$ and carries zero twist information. At the rest pose the draft
   formula reads $\arctan(L_{ua}/L_{fa}) = 47.9°$ at true twist 0 —
   pure segment-length geometry — and returns the **same value for
   $+90°$ and $-90°$** twist (sign-blind).
2. **No un-swing**: twist is about the *current* arm axis; fixed
   coordinate planes are perpendicular to it only at zero swing.

The generic swing solution in the draft was confirmed correct
(identical to §4.3).

## 5. Right elbow — swing in the fully-rotated arm frame

### 5.1 Frame and solve

The elbow's parent segment is the upper arm, so the L14 frame is the
fully-rotated arm frame $R_{arm} = R_{root}\,R_y(\theta_y) R_z(\theta_z) R_x(\theta_\tau)$
with origin $p_{14}$ and rest forearm $= +\hat x$ (continuing the arm
axis). With $\hat g = R_{arm}^{\mathsf T}(p_{16}-p_{14})/\|\cdot\|$, the same
swing parameterization as §4.3 gives

$$
R_{el} = R_y(e_y)\,R_z(e_z) \;\Rightarrow\; \hat g = (c_y c_z,\ s_z,\ -s_y c_z),
\qquad
e_z = \arcsin(\hat g_y), \quad e_y = \mathrm{atan2}(-\hat g_z,\ \hat g_x),
$$

with $e_y = 0$ a straight elbow and $e_y = -90°$ a right angle.
Forearm pronation/supination is unobservable without hand landmarks and
is not modeled.

### 5.2 DOF accounting: $e_z \equiv 0$ (derived, not a bug)

The shoulder twist $\theta_\tau$ is *defined* (§4.4) as the rotation
about the arm axis that aligns the forearm's perpendicular component
with local $+\hat z$. Therefore, by the time the elbow is solved in the
L14 frame, the flexion plane has already been rotated into $x$–$z$:

$$
\hat g_y \equiv 0 \;\Rightarrow\; e_z \equiv 0, \qquad e_y \in [-180°, 0].
$$

The elbow's out-of-plane swing is not lost — **it is the shoulder
twist**. Dimension count: 3 landmarks per arm give two segment
directions = 4 observable rotational DOF, and the solve extracts
exactly 4 non-redundant angles $(\theta_y, \theta_z, \theta_\tau, e_y)$.
Empirical confirmation: a pose *generated* with $e_z = 30°$ at zero
twist decodes as $\theta_\tau = -30°$, $e_z = 0$, same $e_y$ — and the
recomposed forearm direction matches to $5.6\times10^{-17}$. The angle
$e_z$ is kept in the packet interface for generality but carries no
independent information under this convention.

### 5.3 Degeneracy

At a straight elbow ($p_{16}-p_{14} \parallel \hat a$) the perpendicular
component vanishes and twist is unobservable — fundamental to a
3-landmark arm, not fixable by algebra. The solver thresholds
$\|f'_\perp\| < 10^{-6}\|f\|$ and flags twist unobservable (downstream:
hold last valid, A3). Near-straight elbows leave $e_y$ well-conditioned
but make $\theta_\tau$ noise-sensitive — quantified as the leading
practical limitation in D1 §1.

## 6. Left arm — sagittal mirror, not re-derivation

Landmarks 11/13/15, same parent root, rest arm $= -\hat x$. Left angles
are **defined** through the sagittal reflection in the root basis,

$$
M = \mathrm{diag}(-1, 1, 1):
$$

express both left segment vectors in root coordinates, flip $x$, run the
**identical** right-arm solve. Because conjugation by $M$ preserves the
whole construction, every result above (twist plane, $e_z \equiv 0$,
gimbal and straight-elbow behavior) carries over verbatim, and a
mirror-symmetric pose yields identical angle values on both sides with
side-independent anatomical meaning ($\theta_y+$ backward, $\theta_z+$
up, $\theta_\tau+$ internal, $e_y \in [-180°,0]$ flexion).

Reconstruction uses $M R M$ term-wise; with these elementary matrices

$$
M R_y(\theta) M = R_y(-\theta), \quad
M R_z(\theta) M = R_z(-\theta), \quad
M R_x(\theta) M = R_x(\theta),
$$

so the left chain is the right chain with **$y$- and $z$-angle signs
flipped, twist sign kept**:

$$
\text{chain}_L = R_y(-\theta_y) R_z(-\theta_z) R_x(\theta_\tau) R_y(-e_y) R_z(-e_z),
\qquad \text{rest arm} = -\hat x.
$$

(Twist keeping its sign states that "internal rotation moves the
forearm-forward vector downward" holds on both sides.)

## 7. Driving the rig (angle transfer)

Per bone, the applied world rotation composes three factors:

$$
R_{bone} = q_A \; R_{chain} \; C_{rest},
$$

- $C_{rest}$: the bone's authored rest world rotation, captured once at
  spawn (absorbs the FBX's local axis conventions, e.g. the rig's ~8°
  authored arm droop, as a constant);
- $R_{chain}$: the solved kinematic chain up to that bone
  ($R_{root}$, $R_{root}R_{sh}$, $R_{root}R_{sh}R_{el}$, or the
  mirrored left versions);
- $q_A$: the world anchor (identity for the standalone Pipeline A
  scene; the person-anchor rotation in the integrated scene, C1 §1).

The anchor **pre-multiplies**. The conjugation
$q_A R_{chain} q_A^{-1} C_{rest}$ — superficially plausible as a "change
of basis" — actually cancels the anchor out of the applied pose and is
invisible to positional validation; it was caught by plotting the data
(C1 §3). The root bone is additionally translated each frame so the hip
lands on the streamed pelvis point; a **uniform** root scale $s$ (used
to display-scale the 3.25 m FBX to a 1.70 m person) commutes with all
rotations ($sI\,R = R\,sI$), so the angle transfer is unaffected by
scaling.

## 8. Validation on synthetic known truth

Synthetic rigid-body datasets with known injected angle trajectories,
exported in sensor space through the extractor's exact CSV layout, then
pushed through the full pipeline:

| dataset | content | max decode error |
|---|---|---|
| root motion | yaw ±30°, pitch ±20°, roll ±20°, combined | $1.1\times10^{-13}$° |
| `shoulder_only` | swings ±60°, twist ±80°, combos (900 fr) | $8.5\times10^{-14}$° |
| `shoulder_torso` | arm + root simultaneously | $2.0\times10^{-13}$° |
| `elbow_only` | flexion −10..−150°, rotating flexion plane | $8.5\times10^{-14}$° |
| `arm_full` | all seven right-side angles nonzero | $2.8\times10^{-13}$° |
| `arm_both` | 12 angles nonzero (both arms + root) | $2.6\times10^{-13}$° |

Held-pose and live-motion Unity checks match the derivations to 0.02°
(float32 packet quantization); videos and per-frame logs are pinned in
`kinematics/dataset/`.

## 9. Validation on real recordings (no external truth)

With no injected truth, correctness means: (a) frame invariants hold,
(b) the solve is an exact inverse — the solved angles must reconstruct
both measured segment directions — and (c) the numbers are physically
plausible.

On `recording_20260225_230607` (900/900 frames) and
`recording_20260224_083945` (899 frames):

| check | result |
|---|---|
| $\det R = 1$, $\|R^{\mathsf T}R - I\|$, Euler round-trip | $\le 6.7\times10^{-16}$ every frame |
| worst-frame reconstruction angle (all 4 segments) | $\le 6.4\times10^{-14}$° |
| elbow range | $e_y \in [-180°, 0]$ all frames |
| raw → filtered frame-to-frame jumps | 65° → 5.8° (shoulder), 20 → 2.2° (root) |

Reconstruction stays at machine precision on **both** raw and filtered
data — the solve inverts whatever geometry it is given — so the large
raw jumps are input noise, not solver artifacts; their 10–30× collapse
under the 3 Hz filter attributes them to depth noise. The largest raw
jumps occur in shoulder twist at near-straight elbows — the §5.3
conditioning prediction appearing in practice (D1 §1).

**Per-frame Unity mapping error**, measured (not assumed) by logging the
rig's four arm-segment directions every displayed frame and comparing
against independent predictions from the solved angles: 897/897 frames
displayed, angular error mean 0.0000°, **max 0.0001°**, zero frames off
by more than 0.1°. The ceiling is float32 packet quantization; the
mapping chain itself is exact.

## 10. Reproduce

```bash
cd kinematics
python validate_root_frame.py
python validate_shoulder.py          # parts A-E: shoulder, elbow, left arm
python validate_real_recording.py
```

Pinned artifacts: `kinematics/dataset/` (synthetic datasets, Unity
videos, per-frame logs, real-recording snapshots).

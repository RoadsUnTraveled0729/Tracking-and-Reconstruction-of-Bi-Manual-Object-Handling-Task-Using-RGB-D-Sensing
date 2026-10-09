# Kinematic Model — Conventions and Derivations

Base variant (offline, matrices + Euler only). This document is the canonical
reference for coordinate frames, the root-frame construction, and the Euler
convention used everywhere downstream (logs, CSVs, Unity handoff).

## 1. Landmarks in scope

MediaPipe pose indices, positions in meters:

| id | name           | role in root frame        |
|----|----------------|---------------------------|
| 24 | right hip      | root origin (L24)         |
| 23 | left hip       | lateral axis endpoint     |
| 12 | right shoulder | plane (up) disambiguation |

## 2. Sensor space → Unity space (established earlier, restated)

RealSense optical frame: X right, Y **down**, Z forward (into the scene),
meters, right-handed. Unity: X right, Y **up**, Z forward, meters,
left-handed. The mapping is a single axis flip:

```
p_unity = (x, -y, z)
```

This is a reflection (det = −1 as a linear map), which is exactly what
converts a right-handed frame to a left-handed one. It is applied to **points
only**; it never touches rotation matrices directly. All rotations below are
constructed *after* the flip, from already-Unity-space points, so no further
handedness correction is ever applied to them.

## 3. Root frame at L24 (right hip)

### 3.1 Anatomical direction vectors (Unity space)

With `p23, p24, p12` the Unity-space landmark positions:

```
r̂ = normalize(p24 − p23)          # person's anatomical RIGHT (left hip → right hip)
s  = p12 − p24                     # "spine-ish": roughly up, not trusted as an axis
f̂ = normalize(r̂ × s)             # person's FORWARD (out of the chest)
û = f̂ × r̂                        # person's UP (exact unit vector by construction)
```

Cross products use the standard component formula
`(a×b) = (a_y b_z − a_z b_y, a_z b_x − a_x b_z, a_x b_y − a_y b_x)` —
i.e. `numpy.cross` / `Vector3.Cross`.

**Trusted primary axis** (Gram-Schmidt ordering): the hip line 23→24 is kept
exactly — both endpoints are pelvis landmarks, so it *is* the segment being
posed. The spine-ish vector `s` only selects the coronal plane; its component
along `r̂` is discarded implicitly by the cross product. `û` is then recovered
as the unique third axis. Consequence: trunk lean does pitch this frame (with
only 3 points, pelvis and trunk are not separable) — accepted simplification
for the base variant; noted as a refinement candidate (use shoulder/hip
midpoints) for later.

### 3.2 Handedness resolution (open question 1)

The numeric cross-product formula is basis-independent algebra. Unity's own
basis satisfies it cyclically: `x̂×ŷ = ẑ`, `ŷ×ẑ = x̂`, `ẑ×x̂ = ŷ`
*numerically*, even though Unity is left-handed (the "left-hand rule" is only
the geometric visualization). Therefore a triad built as
`r̂, f̂ = r̂×s, û = f̂×r̂` satisfies the same cyclic identities as Unity's
world axes, and

```
R = [ r̂ | û | f̂ ]     (columns: right, up, forward)
```

has **det(R) = +1** — a proper rotation, no sign flip needed anywhere.
This was verified numerically: det = +1.000000 on all 899 frames of the real
recording (§5). The sign correctness (as opposed to mere properness) is pinned
by the reference-pose check in §5, which distinguishes the correct frame from
any axis-permuted/flipped variant.

Column order matters: Unity's `Transform` exposes `right`, `up`, `forward` as
the 1st, 2nd, 3rd columns of its rotation matrix. Assembling `[r̂|û|f̂]` in
that order means "hip bone with rotation R has its local X along the person's
right, local Y along the person's up, local Z out of the chest" — matching a
Unity humanoid at rest (identity rotation = facing world +Z, right = +X).

### 3.3 Corrections to the initial sketch

The sketch (`X = 24→23`, `Y = X × (24→12)`, `Z = X × Y`) is a valid proper
rotation (det +1) but assigns axes to the wrong anatomy:

- Its **X** = 24→23 is the person's **left**, but the rig convention needs
  +X = person's right → direction reversed to 23→24.
- Its **Y** = lateral × spine is the normal of the coronal plane — the
  **anterior–posterior** axis (person's *back*), not up.
- Its **Z** = X × Y then comes out pointing **down**.

Decoded at the upright reference pose, the sketch yields Euler
**(90, 0, 0)** — a rig pitched flat on its back — instead of (0, 180, 0).
Verified numerically in §5.

### 3.4 Rig alignment assumption (open question 3)

Reference alignment adopted: *a Unity humanoid with identity hip rotation
stands upright facing world +Z with its right side toward +X.* Under the base
variant's simplifying assumption, `R_hip = R` directly. A person standing
upright facing the sensor therefore decodes to **(0, 180, 0)** — the person
faces the camera, i.e. world **−Z**, because the sensor looks along +Z.
The 180° yaw is physically real, not an artifact: the avatar must face the
opposite direction of the camera's viewing axis to face "toward the viewer".
If a specific FBX's hip rest rotation is not identity, a constant calibration
`C = R_charrest⁻¹ · R_hip_rest` gets composed at retarget time
(`R_hip = R · C`), where `R_charrest` is the CHARACTER's authored rest facing
expressed as a world rotation — (0,0,0) for a rig authored facing +Z. With the
stated assumption, `C = R_hip_rest` (only the bone's local axis convention).

**Pitfall found during live verification**: anchoring the calibration to the
*person's* reference pose instead (`C = Euler(0,180,0)⁻¹ · R_hip_rest`)
discards the absolute yaw — the rig then stays at its authored facing (+Z,
back to the camera) while the person faces the sensor. The correct anchor is
the character convention, which lets the streamed y = 180 physically turn the
rig around to face the viewer, matching the person. Implemented in
`Unity/Assets/Scripts/RootAngleReceiver.cs` (`referenceEuler = (0,0,0)`).

## 4. Euler decomposition — Unity's actual order (open question 4)

**Unity applies Z, then X, then Y** (about the parent's fixed axes). From the
Unity documentation for `Quaternion.Euler` / `Transform.eulerAngles`: rotation
of `euler.z` degrees around z, `euler.x` around x, `euler.y` around y, *in
that order*. The initial guess of "YZX" was incorrect. As a matrix product
(column-vector convention, world-fixed axes):

```
R = Ry(y) · Rx(x) · Rz(z)
```

The individual axis matrices in Unity's convention are the standard forms
(verified against Unity behavior, e.g. `Euler(0,90,0)·forward = right`):

```
Rx(x) = [1   0    0 ]    Ry(y) = [ cy  0  sy]    Rz(z) = [cz  -sz  0]
        [0  cx  -sx]             [  0  1   0]            [sz   cz  0]
        [0  sx   cx]             [-sy  0  cy]            [ 0    0  1]
```

### 4.1 Derivation of the composed matrix

First `Rx·Rz`:

```
Rx·Rz = [ cz        -sz        0  ]
        [ cx·sz      cx·cz    -sx ]
        [ sx·sz      sx·cz     cx ]
```

Then `R = Ry·(Rx·Rz)`:

```
R = [ cy·cz + sy·sx·sz    -cy·sz + sy·sx·cz    sy·cx ]
    [ cx·sz                cx·cz              -sx    ]
    [-sy·cz + cy·sx·sz     sy·sz + cy·sx·cz    cy·cx ]
```

### 4.2 Extraction (matrix → Euler)

Reading off elements (m[row][col], 0-indexed):

```
m12 = -sin(x)              →  x = asin(-m12)            (x ∈ [-90°, +90°])
m02 =  sy·cx,  m22 = cy·cx →  y = atan2(m02, m22)       (cx > 0 branch)
m10 =  cx·sz,  m11 = cx·cz →  z = atan2(m10, m11)
```

**Gimbal lock** (`|m12| = 1`, i.e. x = ±90°, cx = 0): y and z rotate about the
same effective axis and only their combination is observable. Substituting
sx = ±1, cx = 0 into R:

- x = +90°: row 0 becomes `[cos(y−z), sin(y−z), 0]` → set z = 0,
  `y = atan2(m01, m00)`.
- x = −90°: row 0 becomes `[cos(y+z), −sin(y+z), 0]` → set z = 0,
  `y = atan2(−m01, m00)`.

For this application x = ±90° means the torso pitched to horizontal —
outside the expected workspace, but the decode stays well-defined.

## 5. Validation (open question resolution by test, not assumption)

Implementation: `kinematics/validate_root_frame.py`. Two levels:

**(a) Synthetic reference pose** — ideal upright person facing the sensor
(hips level at equal Z, right shoulder above right hip):

```
expected  R = [ -1  0   0 ]   (r̂ = -X: person's right is camera's left;
                [  0  1   0 ]    û = +Y: up;  f̂ = -Z: facing the camera)
                [  0  0  -1 ]
measured  R = exactly that;  Euler = (0, 180, 0) ✓
sketch construction on the same pose: Euler = (90, 0, 0) ✗ (rig on its back)
```

**(b) Real recording** (899 frames, filtered CSV of the person standing in
front of the sensor):

| check | result |
|---|---|
| det(R) | +1.000000 on every frame |
| max \|RᵀR − I\| | 6.7e-16 (orthonormal to machine precision) |
| Euler mean (x, y, z) | (−0.7°, −168.8°, +1.7°) |
| Euler std | (0.9°, 2.0°, 0.6°) |
| decode→recompose round-trip | max error 3.6e-16 |
| gimbal decode (x = ±90° synthetic) | round-trip exact |

Interpretation: y ≈ −168.8° ≡ 191.2° = 180° + 11°, i.e. the subject/camera
were ~11° off square-on during the recording; x ≈ −0.7°, z ≈ +1.7° say the
camera was nearly level. These small constant offsets are **extrinsic** (the
camera's pose in the room), which the later camera→world coordinate-conversion
stage will absorb; the frame construction itself is confirmed by the exact
synthetic check plus the tight, near-constant angles on real data.

**(c) End-to-end synthetic motion test** (`kinematics/make_synthetic_motion.py`
→ `kinematics/send_root_angles.py` → Unity `RootAngleReceiver`): a rigid
8-landmark body was animated by known injected Euler trajectories
(yaw ±30°, pitch ±20°, roll ±20°, then combined), exported in SENSOR space
with the extractor's exact CSV layout, and pushed through the full pipeline.

| check | result |
|---|---|
| pipeline decode vs injected truth | max error 1.1e-13 deg (900 frames × 3 axes) |
| Unity receiver, frame-matched | sent Euler = truth at sampled frames; bone world rotation = Euler(sent)·C exactly |
| held poses (ref / yaw+30 / pitch+20 / roll+20) | screenshots match expectation, incl. facing the camera at reference |
| visual A/B | `kinematics/output/synthetic_motion.mp4` (matplotlib ground truth) vs `kinematics/output/unity_rig_root_rotation.mp4` (rig + raw-landmark markers moving in sync) |

## 6. Right shoulder — swing–twist decomposition

Implementation: `kinematics/shoulder.py`; validation:
`kinematics/validate_shoulder.py` on datasets from
`kinematics/make_synthetic_shoulder_motion.py`.

### 6.1 Parent frame and rest configuration

The L12 shoulder frame has its **origin at landmark 12** and **inherits the
L24 root orientation** (§3). Joint angles must be measured relative to the
parent segment; the torso's only constructed orientation is R_root, and
re-deriving a separate basis at L12 would silently introduce a shoulder-girdle
DOF the landmark set cannot support. "Express a vector in L12 coordinates"
therefore means `v_local = R_rootᵀ · v_unity` (direction vectors ignore the
origin shift).

Rest configuration (T-pose): the right upper arm points along the person's
right ⇒ **rest arm axis = local +x**. Zero-twist reference: with the elbow
flexed, the forearm's component perpendicular to the arm axis points along
**local +z** (elbow flexes forward). Positive twist = internal rotation
(forearm-forward rotates toward −y, i.e. downward), which follows from the
numeric Rx below.

### 6.2 Parameterization: why twist must be innermost

The physical split is: swing = where the arm points, twist = roll about the
arm's own long axis. A rotation about the rest axis x̂ leaves x̂ fixed
(`Rx(θτ)·x̂ = x̂`), so writing

```
R_sh = Ry(θy) · Rz(θz) · Rx(θτ)        (joint order, NOT Unity's ZXY)
```

with the twist **innermost** makes the upper-arm direction depend on swing
alone:

```
â = R_sh · x̂ = Ry(θy)·Rz(θz)·x̂ = ( cy·cz,  sz,  −sy·cz )
```

If twist were outermost (R = Rx·Ry·Rz), the "twist" axis would no longer be
the arm axis after any swing — the split would not be the physical one.
Consequence: **twist is invisible in the 12→14 vector**; it must be measured
from a second, non-collinear segment (the forearm, §6.4).

The matrices are the same numeric Rx/Ry/Rz as §4 (valid in Unity's
left-handed basis per §3.2). Since this joint order differs from Unity's
ZXY-applied convention, driving a Unity bone requires composing the matrix
`R_root·R_sh·(rest correction)` and extracting Unity Euler via §4 — the
joint angles themselves are anatomical coordinates, not Unity Euler input.

### 6.3 Swing extraction

From â = (cy·cz, sz, −sy·cz) with cz ≥ 0 on θz ∈ [−90°, +90°]:

```
θz = asin(ây)                 (elevation; + = arm up)
θy = atan2(−âz, âx)           (azimuth;   + = arm sweeps backward)
```

Every direction â is reachable with θz ∈ [−90, 90], θy ∈ (−180, 180] — no
coverage gap. Gimbal lock at θz = ±90° (arm straight up/down): âx = âz = 0
and θy is undefined; convention **θy := 0**, and any axial rotation folds
into θτ automatically (validated: a pose generated with θy=30°, θz=90°
decodes to (0, 90, 30) — same physical pose, twist absorbs the yaw).

### 6.4 Twist extraction

Twist is a rotation **about** the arm axis, so it must be measured in the
plane **perpendicular to** that axis — a projection onto any plane
*containing* the axis (e.g. ZX when the axis is x) destroys the sign and
mixes in segment-length geometry (§6.5, draft audit).

Procedure (measure AFTER removing swing, so the arm axis is back at x̂ and
the perpendicular plane is exactly the local y–z plane):

```
f  = R_rootᵀ (p16 − p14)                  forearm in the torso basis
f′ = Rz(−θz) · Ry(−θy) · f                un-swing: R_swingᵀ · f
θτ = atan2(−f′y, f′z)
```

Derivation of the atan2 arguments: with zero twist the un-swung forearm's
⊥-component is ∝ ẑ; under Rx(θτ), ẑ ↦ (0, −sinθτ, cosθτ), so
(−f′y, f′z) ∝ (sinθτ, cosθτ).

**12→16 vs 14→16:** because p14 − p12 ∥ â, un-swinging w = p16 − p12 gives
w′ = |ua|·x̂ + f′, and the projection onto y–z kills the x̂ term — with the
*correct* plane, shoulder→wrist and the forearm give **identical** twist.
The forearm 14→16 is adopted as it states directly where the twist
information lives; 12→16 is only "contaminated by elbow flexion" when
combined with a wrong projection plane.

### 6.5 Thesis-draft audit (errors found and confirmations)

| # | draft says | correct is | because |
|---|---|---|---|
| 1 | twist from 12→16 | 14→16 (but see §6.4) | equivalent under the correct ⊥ projection (parallel part is annihilated); inequivalent and flexion-contaminated under the draft's plane |
| 2 | project onto the **ZX plane** | the **y–z plane** (after un-swing) | ZX *contains* the rotation axis x; the x-component of any vector is invariant under Rx and carries zero twist information. Numeric refutation at rest pose: draft reads **47.9°** at true twist 0 (= atan(L_ua/L_fa), pure geometry), and returns the **same value for +90° and −90°** twist |
| 3 | θτ = atan2(projected x, projected z) | θτ = atan2(−f′y, f′z) | follows from Rx(θτ)·ẑ = (0, −sθτ, cθτ) |
| 4 | (implicit) project the raw vector in the L12 frame | **un-swing first** (f′ = R_swingᵀ f), or equivalently project onto the plane ⊥ current â with a swung reference | twist is about the *current* arm axis; fixed coordinate planes are only ⊥ to it at zero swing |
| 5 | L12 basis unspecified | inherit R_root (torso), origin at p12 | joint angles are relative to the parent segment; no extra landmarks / DOF invented |
| 6 | generic swing θz = asin(vy/L), θy = atan2(−vz, vx), rest (L,0,0) | **confirmed correct** | identical to §6.3; corresponds exactly to R_swing = Ry·Rz with rest +x |
| 7 | (unstated) angle order vs Unity | joint order Ry·Rz·Rx ≠ Unity ZXY | feeding (θτ, θy, θz) into Quaternion.Euler would be wrong; convert the matrix via §4 |

### 6.6 Singularities and limitations (for the thesis)

- **Swing gimbal lock** at θz = ±90° (arm vertical): azimuth θy undefined;
  convention θy := 0 with axial rotation reassigned to θτ. Near-vertical
  poses make θy noise-sensitive (atan2 of two →0 quantities).
- **Straight elbow ⇒ twist unobservable.** With 14→16 ∥ â the perpendicular
  component vanishes; no landmark carries axial information (fundamental to
  a 3-landmark arm, not fixable by math). Solver thresholds
  |f′⊥| < 1e-6·|f| and returns NaN + flag; downstream may hold the last
  valid twist.
- **atan2 wraparound** at θτ = ±180°; per-frame values are reported in
  (−180°, 180°], temporal unwrapping is a downstream choice.
- asin argument clamped to [−1, 1] against numeric noise.

### 6.7 Validation results (2026-07-14, `validate_shoulder.py`, ALL PASS)

| check | result |
|---|---|
| 6 known poses (rest / forward / elevated / int+ext rotation / combined) | exact (0 err) |
| gimbal pose (θy=30, θz=90) | decodes (0, 90, 30) — axial folds into twist as derived |
| straight elbow | twist flagged unobservable; swing still exact |
| draft ZX formula at true twist 0 / +90 / −90 | 47.9° / 90.0° / 90.0° (wrong value; sign-blind) |
| dataset `shoulder_only` (900 fr, arm sweeps θy±60, θz±60, θτ±80 + combo) | max shoulder err 8.5e-14 deg |
| dataset `shoulder_torso` (same arm motion + root yaw/pitch/roll sweeps) | max root err 1.1e-13, max shoulder err 2.0e-13 deg |

**Unity verification (2026-07-17, `kinematics/send_arm_angles.py` →
`ArmAngleReceiver.cs` driving DEF-spine + DEF-upper_arm.R + DEF-forearm.R;
elbow driven by a provisional hinge angle measured between segments):**

| check | result |
|---|---|
| held poses: rest / arm forward (θy=−90) / twist ±90 | screenshots match derivation exactly (forearm toward camera / folded across at shoulder height / hanging down / pointing up) |
| arm-forward numeric | rest bone dirs rotate by exactly Ry(−90): ua (−0.990,−0.142,0.017)→(−0.017,−0.142,−0.990) |
| complex pose, ALL SIX angles nonzero (frame 742: root (8.0, −171.7, 5.8), shoulder (27.8, 30.0, 32.4)) | measured bone dirs vs predicted chain: 0.02° / 0.00° (float32); delta chain maps frame-0 landmark dirs onto frame-742 landmark dirs to 4 decimals |
| videos | `kinematics/dataset/unity_arm_shoulder_only.mp4`, `unity_arm_shoulder_torso.mp4` (rig reproduces both datasets live, incl. torso+arm simultaneous) |

The rig's authored rest arm has a small droop (≈8°) relative to a perfect
T-pose; the calibration (C = rest world rotation per bone, §3.4 convention)
preserves it as a constant visual offset — the *rotation deltas* match the
math exactly, which is what the checks above measure.

## 7. Right elbow — swing in the L14 frame

Implementation: `solve_right_arm` in `kinematics/shoulder.py`; validation
parts C/D of `kinematics/validate_shoulder.py`.

### 7.1 Frame and parameterization

The elbow's parent segment is the upper arm, so the L14 frame is the
**fully-rotated arm frame** `R_arm = R_root · Ry(θy)·Rz(θz)·Rx(θτ)` with
origin at landmark 14. Rest forearm = local **+x** (straight elbow,
continuing the arm axis). The forearm 14→16 is expressed there,
`ĝ = R_armᵀ(p16−p14)/|·|`, and its two swing angles are solved with the
SAME parameterization as the shoulder swing (§6.3):

```
R_elbow = Ry(ey)·Rz(ez)   ⇒   ĝ = (cy·cz, sz, −sy·cz)
ez = asin(ĝy)             ("up/down" swing out of the flexion plane)
ey = atan2(−ĝz, ĝx)       (flexion: 0 = straight, −90 = right angle)
```

Forearm twist (pronation/supination) is ignored — with no hand landmarks it
is unobservable, exactly like shoulder twist at a straight elbow.

### 7.2 DOF accounting: ez ≡ 0 (derived, not a bug)

The shoulder twist θτ is *measured from the forearm*: it is defined (§6.4)
as the rotation about the arm axis that aligns the forearm's perpendicular
component with local +z. Therefore, by the time the elbow is solved in the
L14 frame, the flexion plane has already been rotated into x–z, and

```
ĝy ≡ 0  ⇒  ez ≡ 0,   ey ∈ [−180°, 0]
```

identically. The elbow's "up/down" swing is not lost — **it IS the shoulder
twist**. Angle count: 3 landmarks give two segment directions = 4
observable rotational DOF, and the solve extracts exactly 4 nonredundant
angles (θy, θz, θτ, ey). Validated numerically: a pose generated with
ez = 30° at zero twist decodes as twist −30°, ey unchanged, ez = 0 — the
recomposed forearm direction is identical to 5.6e-17. ez is kept in the
interface/packet for generality but carries no independent information
under this convention.

### 7.3 Degenerate case

At a straight elbow the twist is unobservable (§6.6); convention θτ := 0
keeps the L14 frame defined and ey decodes 0 exactly. Near-straight elbows
make θτ (and hence the flexion-plane orientation) noise-sensitive while ey
itself stays well-conditioned.

### 7.4 Validation (2026-07-17, ALL PASS)

| check | result |
|---|---|
| known poses (straight / −90 rest / −45 with twist 30 / full combo with elbow −120) | exact |
| ez=30 injection re-attributed to twist −30, same forearm direction | exact (5.6e-17) |
| dataset `elbow_only` (flexion sweep −10..−150, then twist rotating the flexion plane, then both) | max elbow err 8.5e-14 deg |
| dataset `arm_full` (root + shoulder + elbow all moving; 24–30 s all seven angles nonzero) | max err root 1.1e-13 / shoulder 2.0e-13 / elbow 2.8e-13 deg |
| Unity, straight-arm held pose (ey=0) | forearm continues the arm axis, err 0.02° |
| Unity, arm_full frame 742 held (root (8.0,−171.7,5.8), shoulder (27.8,30.0,32.4), elbow −100.4) | both bone dirs match predictions to 0.02°; delta chain reproduces the dataset's landmark dirs to 4 decimals |
| videos | `kinematics/dataset/unity_arm_elbow_only.mp4`, `unity_arm_full.mp4` |

## 8. Validation on a real recording (no ground truth)

Implementation: `kinematics/validate_real_recording.py`; data:
`Video/recording_20260225_230607.bag` → MediaPipe extractor → 900/900
frames with pose (raw + Butterworth-filtered CSVs snapshotted in
`kinematics/dataset/real_20260225/`).

On real data there is no injected truth, so correctness means: (a) the
frame invariants hold, (b) the solve is an exact inverse — the 4 solved
right-arm angles must reconstruct both measured segment directions — and
(c) the numbers are physically plausible.

| check | raw CSV | filtered CSV |
|---|---|---|
| max \|det(R)−1\| / \|RᵀR−I\| / Euler round-trip | 6.7e-16 / 6.7e-16 / 5.4e-16 | same |
| worst-frame reconstruction angle (upper arm / forearm) | 2.9e-14 / 2.7e-14 deg | 2.9e-14 / 3.7e-14 deg |
| elbow ey within [−180, 0] | all 900 frames (−42.5..−13.9) | all 900 (−38.1..−19.6) |
| max frame-to-frame jump (root / shoulder / elbow) | 20.2 / 65.2 / 21.2 deg | 2.2 / 5.8 / 2.1 deg |

The person faces the camera throughout (yaw 180° ± 4.7° circular; the
naive yaw std of ~176° is a ±180° wraparound artifact — use circular
stats). Reconstruction stays at machine precision on BOTH raw and filtered
data (the solve inverts whatever geometry it is given); the large raw
jumps collapse ~10–30× under the 3 Hz filter, attributing them to sensor
depth noise (hips worst: 12.4 mm rms correction), not solver artifacts.
The largest raw jumps are in shoulder twist — the §7.3 conditioning
prediction (near-straight elbow, ey up to −14°) showing up in practice.
Visual A/B: `kinematics/dataset/real_20260225/real_20260225_motion.mp4`
(matplotlib) vs `unity_real_20260225.mp4` (rig + markers, live), plus a
live in-Unity check: measured bone directions vs the solved chain 0.02°.
Note the `arccos` of a dot product is ill-conditioned near 0°
(~1e-6 deg floor); reconstruction angles use atan2(|a×b|, a·b).

### 8.1 Second real recording + per-frame Unity mapping error (2026-07-17)

`Video/recording_20260224_083945.bag` ("complex": yaw sweeps ±12°, both
arms low and bent, deep asymmetric elbow flexion): 899 frames extracted,
897 usable — frames 0–1 lack left-arm landmarks (MediaPipe warm-up);
`compute_angles` drops rows with missing cells rather than emitting NaN.
Same ALL PASS as §8: invariants 1e-16, all four segment reconstructions
≤6.4e-14 deg, both elbows in range, raw jumps (up to 114° in L shoulder
θy at near-vertical arm — the §6.3 gimbal conditioning) collapse under the
3 Hz filter to ≤6.6°.

**"How far off is the rig, and on how many frames?"** — measured directly,
not assumed: `ArmAngleLogger.cs` samples the rig's four arm segment
directions every displayed frame; `analyze_unity_frame_log.py` predicts
each from the solved angles independently and compares:

| metric | result |
|---|---|
| frames sent → displayed | 897 → 897 (0 missed) |
| angular error, all 4 segments | mean 0.0000°, p99 0.0001°, **max 0.0001°** |
| frames off by >0.1° | **0** |
| frames off by >1° | **0** |

The 0.0001° ceiling is float32 packet quantization — the mapping chain
itself is exact. Artifacts in `kinematics/dataset/real_20260224/`
(CSVs, matplotlib + Unity videos, the per-frame log).

## 9. Left arm — sagittal mirror of the right-arm solve

Implementation: `solve_left_arm` in `kinematics/shoulder.py`;
validation part E of `validate_shoulder.py` + dataset `arm_both` + §8's
real-recording checks (both arms).

### 9.1 Definition by reflection, not re-derivation

Landmarks: 11 = left shoulder (origin), 13 = left elbow, 15 = left wrist;
parent basis = the same L24 root; rest left arm = local **−x**.

Left joint angles are DEFINED through the sagittal reflection
M = diag(−1, 1, 1) in the root basis: express both left segment vectors in
root coordinates, flip their x components, and run the **identical**
right-arm solve. Because M-conjugation preserves the whole construction,
every §6–7 result (twist plane, ez ≡ 0, gimbal and straight-elbow
behavior) carries over verbatim, and:

- a mirror-symmetric pose yields **identical angle values** on both sides
  (validated: a mirrored (25, −40, 35, −75) pose decodes to the same
  numbers left and right);
- the anatomical meaning is side-independent: θy+ = backward sweep,
  θz+ = elevation, θτ+ = internal rotation, ey = flexion ∈ [−180°, 0].

### 9.2 Reconstruction / rig driving

World reconstruction uses M·R·M, which for our matrices means **flip the
signs of every y- and z-axis angle, keep the twist sign** (M·Ry(θ)·M =
Ry(−θ), M·Rz(θ)·M = Rz(−θ), M·Rx(θ)·M = Rx(θ)):

```
chain_L = Ry(−θy)·Rz(−θz)·Rx(θτ)·Ry(−ey)·Rz(−ez),   rest arm = −x̂
```

(Twist keeping its sign is the statement that "internal rotation moves the
forearm-forward vector downward" holds on both sides.) The Unity receiver
composes exactly this chain for DEF-upper_arm.L / DEF-forearm.L; packet
bumped to 'PSA4' (72 B, root + both arms).

### 9.3 Validation (2026-07-17, ALL PASS)

| check | result |
|---|---|
| left known poses (rest / forward / elevated / int. rotation / straight / asymmetric combo) | exact |
| mirror pair decodes identically (L vs R) | exact |
| dataset `arm_both` (torso + both arms, left on distinct phases; frame 742 has all 12 angles nonzero) | max left err 2.6e-13 deg (right + root unchanged) |
| left on the other four datasets (static straight left arm) | exact 0 |
| real recording (§8, both arms) | left reconstruction ≤3.1e-14 deg; left ey ∈ (−76.7, −9.5) |
| Unity, arm_both frame 742 held | left chain reproduces the dataset's landmark directions to 4 decimals |
| video | `kinematics/dataset/unity_arm_both.mp4`, `real_20260225/unity_real_both_arms.mp4` |

## 10. Blocked landmarks — chain fallback (occlusion handling)

Implementation: extractor gate in `mediapipe/extract_landmarks_to_csv.py`,
chain fallback in `kinematics/occlusion.py` (PSA5 in `send_arm_angles.py`
/ `ArmAngleReceiver.cs`); validation `kinematics/validate_occlusion.py`
on masked copies of the verified §8.1 recording.

### 10.1 The three failure modes of a blocked landmark

1. **Hallucination** — MediaPipe always outputs a position for all 33
   landmarks, occluded or not; the per-landmark `visibility` score is the
   only signal that the position is a guess. Before this stage the score
   was written to the CSV and never read: a blocked wrist silently fed a
   wrong point into the solve.
2. **Depth holes** — the depth image returns 0 at the sampled pixel
   (occluder edges, dark/specular surfaces), killing an otherwise good
   landmark.
3. **Whole-frame loss** — the old policy dropped the ENTIRE frame when any
   of the 8 landmarks was missing: a blocked left wrist killed the root
   and the right arm too.

### 10.2 Detection: turn "wrong" into "missing" (extractor)

- **Visibility gate** `--min-vis` (default 0.5): a landmark below the
  threshold writes empty xyz cells. On the §8.1 recording this exposed
  frames 0–9: left elbow/wrist visibility ramps 0.001 → 0.5 while
  MediaPipe warms up, and the old extractor emitted those hallucinated
  positions as data.
- **Depth neighborhood median** `--depth-window` (default 5): depth is the
  median of nonzero returns in a 5×5 window instead of a single
  `get_distance` pixel. Regression on §8.1: median position change 0.00 mm
  (p99 ≤ 7.5 mm, within depth noise), and one wrist frame previously lost
  to a single-pixel hole is recovered.
- Every landmark gets a `{name}_src` reason column: 0 ok / 1 low_vis
  (blocked) / 2 no_depth. The filter carries it through and splits its
  missing-cell stats by reason.

The 3-stage filter (§ Hampel + bounded linear gap fill + zero-phase
smooth) is unchanged: gaps ≤ 5 frames (~167 ms) are repaired offline with
both endpoints known; longer gaps deliberately stay NaN — they are the
fallback's job, not data to invent.

### 10.3 Chain fallback: hold the ANGLE, not the point (solver)

The chain is traceable — every landmark has a parent:

```
L23/L24 hips ──► root frame ──► shoulders (11/12) ──► elbows ──► wrists
```

so the fallback rule is: **a joint whose landmarks are blocked holds its
last valid angle; every joint whose landmarks survive keeps solving
live** (children of a held joint are then implicitly reconstructed by the
parent chain's forward kinematics × fixed bone length). Holding in angle
space dominates guessing the 3D point: the reconstruction is always
bone-length consistent and on the reachable manifold.

Observability table — what each blocked landmark costs (and nothing
more):

| blocked landmark | joints that hold | joints that stay live |
|---|---|---|
| wrist (15/16)    | that arm's twist + elbow (3 DOF) | root, both swings, other arm |
| elbow (13/14)    | that whole arm (5 DOF) | root, other arm |
| one shoulder     | that arm; root switches to the OTHER shoulder as tilt reference | root (see below), other arm |
| one hip          | root (3 DOF) | both arms, solved against the held root |
| everything       | all 13 angles hold | — |

Root with either shoulder: `build_root_frame` only uses the reference
shoulder to select the coronal plane — its component along the hip line
is discarded by the cross product — so the left shoulder substitutes for
the right with a measured deviation of ≤1.53° on real data (shoulder-line
asymmetry, not a construction error).

Straight-elbow twist unobservability (§6.3) unifies with occlusion:
unobservable ⇒ hold last valid twist (this supersedes the θτ := 0
streaming convention of §7; the pure solvers in `shoulder.py` are
unchanged — the wrapper substitutes the held value).

The PSA5 packet (72 B, magic 0x35415350) adds a u16 per-joint live mask
(root, R swing, R twist, R elbow, L swing, L twist, L elbow); the Unity
receiver keeps posing held joints from the (held) angles and shows a red
marker sphere on held bones.

### 10.4 Validation (2026-07-18, ALL PASS — 33 checks)

Masked copies of the verified §8.1 recording; truth = the unmasked solve,
so every check is exact (`make_masked_dataset.py` + `validate_occlusion.py`):

| scenario (frames) | expected behavior | result |
|---|---|---|
| R wrist 3-frame gap in RAW (300–302) | filter repairs (flag 2), nothing holds | wrist within 0.30 mm, angles within 0.08° of truth |
| R wrist 45 frames (400–444) | twist+elbow hold, swing/root/left LIVE | live joints exact (0.0), hold constant, recovery exact |
| R elbow 45 frames (500–544) | whole R arm holds, rest live | same — exact |
| L hip 30 frames (600–629) | root holds; arms live AGAINST THE HELD ROOT | arms match independent recompute with held root exactly |
| R shoulder 30 frames (750–779) | root live via LEFT shoulder; R arm holds | root deviation ≤1.53°, left arm exact against the alt root |
| whole pose 10 frames (700–709) | all 13 angles hold | exact hold + exact recovery |
| low-vis gate consistency (v2 raw) | _src=1 ⟺ empty xyz ∧ vis<0.5 | 19/19 cells consistent |

Coverage: every scenario outputs on **899/899 frames** (the old policy
dropped frames); held-joint "drift" during gaps (1.4–7.8°) equals the
true motion that occurred while blocked — the price of holding, not an
error. On the unmasked recording the fallback changes nothing: frames
0–8 hold the left arm at rest (the warm-up hallucinations §10.2 removed),
frame 9 recovers swing, frames 10+ are fully live.

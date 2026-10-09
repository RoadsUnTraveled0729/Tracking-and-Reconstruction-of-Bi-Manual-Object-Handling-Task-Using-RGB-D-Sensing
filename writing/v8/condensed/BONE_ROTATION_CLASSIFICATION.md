# Classification of `R_rest`, `R_0`, `R_1`, `R_2` in equations (6.4) and (6.5)

Read-only. **Nothing in the repository was changed to produce this file. The only
file written is this one.** Equations (6.4) and (6.5) are untouched, as the
author's instruction requires. No builder, no `.docx`, no code file, and neither
`DECISIONS.md`, `FRAME_INVENTORY.md`, `CRAIG_NOTATION_AUDIT_ch6_ch8.md` nor
`UNITY_FRAME_RESOLUTION.md` was edited.

This answers the ch6/ch8 audit's **U-1** and **U-2**, `FRAME_INVENTORY.md` §4.9,
and §9 **S-11**. It does **not** answer **S-4** (equation (6.5)'s missing
levelling factor), which is a separate defect; see §10.

**The classification was NOT made by analogy with D-057.** D-057's precedent is
used in exactly one way, which the author's instruction permits: the *test* that
settled equation (3.22) is re-run here from scratch, and it is allowed to return
the opposite answer. It does. Section 6 states the discriminators found, in the
same terms §0 of `FRAME_INVENTORY.md` states (3.22)'s, so the two can be compared
line for line.

---

## 0. Verdict, stated first

**All four matrices are frame-relative rotations (D-054 class 1). None is an
operator.** The answer is **not mixed in class**, but `R_rest` is distinguished
from the other three in one respect that matters and must be printed: the other
three are class-1 unconditionally, while `R_rest`'s *captured value* equals the
frame relation its role requires **only under a spawn/T-pose assumption that the
thesis does not currently state**.

| symbol | class | Craig form | conditional on the spawn/T-pose assumption? |
|---|---|---|---|
| `R_0` | **1** | `^{Person}_{L24} R` | no |
| `R_1` | **1** | `^{L12}_{L14} R` (right), `^{L11}_{L13} R` (left); `= ^{L24}_{L14} R`, since `^{L24}_{L12} R = I₃` | no |
| `R_2` | **1** | `^{L14}_{L16} R` (right), `^{L13}_{L15} R` (left) — **the distal frame is not in the inventory**; see §9.2 | no |
| `R_rest,k` | **1** | `^{Seg_k}_{Bone_k} R`, a constant of the rig, `Seg_k ∈ {L24, L14, L16}` (and `{L13}, {L15}` left) | **YES** |
| `R_chain` | **1** | `^{Person}_{L24} R`, `^{Person}_{L14} R`, `^{Person}_{L16} R` | no |
| `R_bone` | **1** | `^{Scene}_{Bone_k} R` | no |
| `A` **as it is used in (6.5)** | **1** | `^{Scene}_{Person} R` — **not** `^{Unity}_{Person} R`; see §10 (S-4) | no |

**The frame branch of the author's decision rule therefore fires.** Craig
two-frame notation is required, and the spawn/T-pose assumption must be stated
explicitly. Its exact wording and its location are in §8; what it costs in new
frame labels is in §9, and two consequences are escalated rather than decided.

---

## 1. Question 1 — what physical or frame quantity does `R_rest` store at spawn?

**It stores the driven bone's own axes expressed in the Unity scene axes, read at
start-up: `^{Scene}_{Bone_k} R` at spawn.** It is a rotation **of the bone's
authored local axes**, **relative to Unity's global (scene) axes**. Its intended
content — what it is there to carry — is the bone's authored axis convention
relative to the character's model frame.

**The capture site.** `Unity/Assets/Scripts/IntegratedSceneReceiver.cs:237-243`:

```
// Authored rest, captured with the rig spawned unrotated (body
// axes = scene axes) — the anchor is PRE-multiplied per frame.
cHip = hip.rotation;
cUpperArm = upperArm.rotation;
cForearm = forearm.rotation;
cLUpperArm = lUpperArm.rotation;
cLForearm = lForearm.rotation;
```

**What `Transform.rotation` is.** Unity's `Transform.rotation` is the transform's
rotation *in world space*: it is the map that carries a direction written in the
transform's own local axes to the same direction written in world axes
(`TransformDirection(v) == rotation * v`). That is, by definition, the
orientation of one frame relative to another — the bone's local axes relative to
Unity's global axes. It is **not** a rotation applied to anything.

The repository uses that API meaning explicitly, on a node of the same kind:
`Unity/Assets/Scripts/RootFrameAxes.cs:85-87` draws a coordinate triad as
`o + q * Vector3.right`, `o + q * Vector3.up`, `o + q * Vector3.forward` — i.e.
it reads the three **columns** of a `Quaternion` as the three axes of a frame,
in scene components. That is the Craig read of a class-1 rotation and it is
performed in this repository, on the product of this very equation (see §6, D-1).

**What the bone frame is not.** The inventory's usage test finding is confirmed
independently here: a grep of `IntegratedSceneReceiver.cs` for `localPosition`,
`localRotation`, `InverseTransformPoint`, `TransformDirection` and
`InverseTransformDirection` returns **only** `:161`, `:162` (the *anchor* node)
and `:378`, `:419`, `:420` (`TransformPoint` on the *anchor* and the *world*
node). **No bone is ever read or written in its own local axes**, and
`HeldMarkers.cs:38-43`, the only other consumer of a bone, reads `bone.position`
alone. So the bone axes have exactly one appearance in the whole system: as the
described frame of `R_rest` and of `R_bone`.

**What the stored value is *meant* to be, in the system's own words.** Both are
stated, and the system states the general form before it states the shortcut.
`v1/KINEMATIC_MODEL.md:108-112`:

> "If a specific FBX's hip rest rotation is not identity, a constant calibration
> **`C = R_charrest⁻¹ · R_hip_rest`** gets composed at retarget time
> (`R_hip = R · C`), where **`R_charrest` is the CHARACTER's authored rest facing
> expressed as a world rotation** — (0,0,0) for a rig authored facing +Z. **With
> the stated assumption, `C = R_hip_rest`** (only the bone's local axis
> convention)."

`R_hip_rest` is the captured world rotation; `R_charrest` is the character's
model frame in world axes. So `C = (^{Scene}_{Model} R)⁻¹ · ^{Scene}_{Bone} R =
^{Model}_{Bone} R`. The system writes the **change of reference frame explicitly**
and then says the condition under which it collapses to the raw capture.

`Unity/Assets/Scripts/ArmAngleReceiver.cs:21-22` says the same in one line: "where
each C is **the bone's authored rest world rotation** (calibration **anchored to
the character's authored facing** — see §3.4 pitfall)."

**And the collapse is a code parameter, not an inference.**
`Unity/Assets/Scripts/RootAngleReceiver.cs:61`:

```
calibration = Quaternion.Inverse(Quaternion.Euler(referenceEuler)) * targetBone.rotation;
```

with `:37-38`:

```
[Tooltip("The character's authored rest facing: (0,0,0) for a rig authored facing world +Z.")]
public Vector3 referenceEuler = Vector3.zero;
```

`referenceEuler` **is the left reference frame of `R_rest`, exposed as an editable
field, with a tooltip that names the frame it stands for.**
`IntegratedSceneReceiver.cs:239-243` is that same computation with the field
inlined at identity.

**Answer.** `R_rest,k` stores `^{Scene}_{Bone_k} R` at spawn. Its role, and the
quantity it is built to carry, is `^{Model}_{Bone_k} R` — equivalently the
constant `^{Seg_k}_{Bone_k} R`, since `{Bone_k}` is rigid on segment `k` and
`{Seg_k}` coincides with `{Model}` at the model's zero configuration. The two are
the same number **iff** `^{Scene}_{Model} R = I₃` at spawn (Question 5).

---

## 2. Question 2 — what frames are `R_0`, `R_1`, `R_2` expressed in?

Each is traced to where it is built, and to what its factors are. The Unity
receiver does not build them; it **re-assembles** them from the thirteen streamed
angles, so the build sites are on the solver side and the frames are the solver's.

### `R_0` — the root/trunk rotation. `^{Person}_{L24} R`, components in {Person}.

- Built at `v1/kinematics/occlusion.py:80-81`:
  `self.R_root = build_root_frame(p["left_hip"], p["right_hip"], ref)` then
  `self.root = euler_unity_zxy(self.R_root)`. The three numbers `v[0..2]` the
  receiver reads are the Euler form of `R_root` and of nothing else
  (`occlusion.py:90-92` concatenates `self.root` first).
- `v1/kinematics/root_frame.py:21-32`, `build_root_frame`, docstring `:22-24`:
  "**L24 root frame** from Unity-space left hip, right hip, right shoulder.
  **Columns of R are the person's [right | up | forward]** in Unity world." The
  code's "Unity world" here is **{Person}**, per `FRAME_INVENTORY.md` §2.5.
- **A matrix whose columns are declared to be the axes of one named frame written
  in another frame's components is the definition of a class-1 frame-relative
  rotation.** Nothing is applied to anything at the build site: the three columns
  `r`, `u`, `f` are stacked (`:32` `np.stack([r, u, f], axis=-1)`).
- Rebuilt in Unity at `IntegratedSceneReceiver.cs:358`
  `Quaternion qRoot = Quaternion.Euler(v[0], v[1], v[2])`. Unity's
  `Quaternion.Euler` applies Z, then X, then Y, i.e. `R = Ry·Rx·Rz`, which is
  exactly `root_frame.recompose_zxy` (`root_frame.py:57-58`) and the inverse of
  `euler_unity_zxy` (`:35-54`). The round trip is exact.

### `R_1` — the shoulder swing-twist. `^{L12}_{L14} R`, components in {L24}/{L12}.

- Solved at `v1/kinematics/shoulder.py:70-82`; parameterised at `:1-11`:
  "`R_sh = Ry(θy) · Rz(θz) · Rx(θτ)` … **All vectors are expressed in the torso
  basis: the L12 shoulder frame inherits the L24 root orientation with its origin
  moved to landmark 12.**"
- The frame it produces is **named, given an origin, and assigned**,
  `shoulder.py:90-93`: "**The elbow parent frame (L14) is the fully-rotated
  upper-arm frame `R_arm = R_root · Ry(θy)·Rz(θz)·Rx(θτ)`, origin at landmark
  14**; … **The forearm is expressed there**", implemented at `:120`
  `R_arm = np.asarray(R_root) @ (_ry(y) @ _rz(z) @ _rx(t))`.
- It has a **read site**: `shoulder.py:121-123`
  `g = normalize(R_arm.T @ (p16 - p14))`, then `ez = arcsin(g[1])`,
  `ey = arctan2(-g[2], g[0])` — the forearm is re-expressed in {L14} and its
  components are read one by one. Likewise `:70` `a = R_root.T @ (p14 - p12)`
  with `a[0]`, `a[1]`, `a[2]` read individually at `:71-76`. These are passive
  changes of basis, and they are the exact evidence on which
  `FRAME_INVENTORY.md` entries 11 and 12 already rest.
- Rebuilt in Unity at `IntegratedSceneReceiver.cs:359-361`:
  `AngleAxis(v[3], Vector3.up) * AngleAxis(v[4], Vector3.forward) *
  AngleAxis(v[5], Vector3.right)` — y, then z, then x, i.e. `Ry(θy)Rz(θz)Rx(θτ)`,
  the same product in the same order.

### `R_2` — the elbow swing. `^{L14}_{L16} R`, components in {L14}.

- Solved at `shoulder.py:120-123`, parameterised at `:94-99`: "`R_elbow =
  Ry(ey)·Rz(ez)` … `ĝ = R_armᵀ (p16-p14)/|·|`", with the rest forearm declared as
  "**local +x**" of {L14} (`:91-92`, and `v1/KINEMATIC_MODEL.md:385-386`).
- Its components are therefore **{L14} components**, and its left frame is {L14},
  which is established. **Its right (described) frame is the forearm segment
  frame, and the system never names it.** On the solver side nothing needs it:
  `solve_right_arm` returns `(ey, ez)` and never assembles `R_elbow`.
  `eval/inspect/check_v1_overlay.py:47-66` builds the forearm *direction* as
  `Rarm @ (_ry(ey) @ _rz(ez) @ [1,0,0])` — the first column of the same matrix.
- **On the Unity side it is needed**, because `R_2` is followed by a rest rotation:
  `IntegratedSceneReceiver.cs:372`
  `forearm.rotation = qA * qRoot * qSh * qElb * cForearm`. The product
  `qA·qRoot·qSh·qElb` is the orientation of the forearm *segment* frame in
  {Scene}, and `cForearm` re-bases from it to the bone's axes. §9.2 records this
  as the one real cost of the frame branch, and escalates it.

### The left side

`IntegratedSceneReceiver.cs:364-368` negates `v[8], v[9], v[11], v[12]` and keeps
the twist `v[10]`, matching `shoulder.py:127` `MIRROR` and
`v1/KINEMATIC_MODEL.md` §9. The frames are the left-side instances {L11}, {L13},
{L15}. This changes no part of the classification.

---

## 3. Question 3 — actively applied to vectors and bones, or passive frame orientations? (the crux)

**Passive frame orientations, all four.** The test is the one used for (3.22): is
something *transformed by* the matrix, with the operand changed and its image read
in the same basis, or is the matrix *assigned as*, *read as*, or *decomposed into*
an orientation?

### 3.1 Nothing is ever transformed by any of them

- `R_rest,k` is never applied to anything. It is *read* out of the API
  (`:239-243`) and later *appears as a right factor*. There is no operand.
- `R_0`, `R_1`, `R_2` are never applied to a vector in Unity. The only vector
  operation in the whole person path is `anchor.TransformPoint(pelvis)` at `:378`,
  which is a change of basis on a {Person} point, not a joint rotation.
- On the solver side the corresponding matrices are used **transposed**, to
  re-express measured vectors: `shoulder.py:70` `R_root.T @ (p14 - p12)`, `:78`
  `R_root.T @ (p16 - p14)`, `:121` `R_arm.T @ (p16 - p14)`, and their components
  are then read individually. That is the passive use, and it is exactly the read
  evidence on which {L24}, {L12} and {L14} are already inventory entries.

### 3.2 They are assigned as orientations, and read as orientations

- `bone.rotation = …` (`:370-374`) **assigns an orientation** — the left-hand side
  is `^{Scene}_{Bone_k} R`, by the API definition in §1.
- `RootFrameAxes.cs:75-77, 85-87` **reads the columns** of `anchor.rotation *
  Quaternion.Euler(lastRootEuler)` — that is `A·R_0` — as the x, y and z axes of a
  frame, gives it the origin `hip.position`, and calls it "**the measured body
  root frame**" / "**the measured torso frame**" (`:1-12`, `:73`). See §6, D-1.
- `shoulder.py:90-93` **assigns the product to a frame variable, gives it an
  origin, and names it** ("the elbow parent frame (L14) … origin at landmark 14").

### 3.3 The one place the code *does* use the operator idiom on a bone — and how it differs

This objection has to be met, because the syntax is identical.
`IntegratedSceneReceiver.cs:261-273`, `AlignArm`:

```
Vector3 d1 = (fore.position - up.position).normalized;
up.rotation = Quaternion.FromToRotation(d1, axis) * up.rotation;
```

This **is** an operator, and the ch6/ch8 audit's C6-18 already classifies it as
one. The distinction is not the shape of the product; it is how the factor is
*defined*:

- `Quaternion.FromToRotation(d1, axis)` is defined as **the rotation that carries
  one measured direction onto another**. Its operand is the bone's current
  orientation and its output is the same bone's changed orientation. Active, by
  construction.
- `qA` is defined as a node's orientation and is independently used as a change of
  basis on a point (`:378`). `qRoot` is defined by its **columns**
  (`root_frame.py:22-32`). `qSh` is defined as the matrix that makes {L14} the
  frame the forearm is expressed in (`shoulder.py:90-93`). `c_rest` is defined as
  a reference-relative rest (`KINEMATIC_MODEL.md:108-112`). **None of the four is
  defined as "the rotation that carries X onto Y".**

So the same file contains both idioms and the code's own definitions separate
them. That separation is the answer to the crux, and §6 gives the two
discriminators that make it decisive rather than merely plausible.

---

## 4. Question 4 — does the multiplication order match operator semantics or a frame chain?

**A frame chain, and only a frame chain.**

**What the Unity product means.** For unit quaternions `(q1 * q2) * v = q1 * (q2 * v)`.
Read actively in one fixed basis, the right factor acts first. Read as frames,
`q1 * q2` is the composition `^{A}_{B} · ^{B}_{C}`. The numbers are the same; the
index bookkeeping is not.

**The chain closes, index for index.** With the four identifications of §§1-2:

```
^{Scene}_{Bone_k} R  =  ^{Scene}_{Person} R  ·  ^{Person}_{Seg_k} R  ·  ^{Seg_k}_{Bone_k} R
   bone.rotation              qA                      qChain                  c_rest
```

`Scene ← Person ← Seg_k ← Bone_k`. **Every intermediate index cancels, and the
composite is exactly the quantity assigned.** Three of the four factors are
established as frame relations at read sites *outside* this equation — `qA` at
`:378` and by `FRAME_INVENTORY.md` §4.4; `qRoot` by its columns
(`root_frame.py:22-24`); `qSh` by `shoulder.py:90-93` and its read site at `:121`.
Once three factors and the assigned composite are class 1, the fourth cannot be
anything else.

**The operator reading does not close.** Under it, `R_chain`'s components are
{Person}-axis components of a physical joint rotation (that is what
`shoulder.py:9-11` and `root_frame.py:24` say they are). To apply the same
physical rotation to an orientation written in {Scene} components you must
conjugate: `qA · qChain · qA⁻¹`. That form is **written out in the code, as the
alternative, and rejected on data** — `IntegratedSceneReceiver.cs:30-34`. See §6,
D-4.

**The alternative operator reading, that `qChain` is already in scene components,
is excluded by the build sites.** `v[0..2]` is the Euler of a matrix whose columns
are the person's axes (`root_frame.py:22-24`); `v[3..7]` are angles about "the
torso basis" axes with "rest upper arm: local +x" (`shoulder.py:9-17`). They are
not scene-axis components of anything. Independently, `RootFrameAxes.cs:75`
composes `anchor.rotation * Quaternion.Euler(lastRootEuler)` and only then draws
the triad in scene axes — i.e. the anchor is what puts `R_0` into scene
components, which it would not need to do if `R_0` were already there.

**The presence of `qA` at all is itself the evidence.** `IntegratedSceneReceiver.cs:19-25`:
"Pipeline A solves in 'Unity-from-sensor' space (camera frame with y flipped);
Pipeline B's world is the desk frame mapped by the y/z swap P… so a 'PersonAnchor'
node at the calibrated camera pose composed with Rx(-90) **turns person-space
coordinates into scene coordinates directly**." A coordinate map is inserted
precisely because the chain rotations are in person coordinates.
`ArmAngleReceiver.cs:14-20`, the receiver with **no** anchor, writes the same
product without it — `hip = R_root · C_hip` — and calls the factors
"**person-basis joint matrices**" while calling the result "**Bone world
rotations**". That receiver is correct only because it identifies the person basis
with Unity's world; the integrated receiver inserts `qA` to break that
identification. Both facts point the same way: `R_chain`'s left index is {Person}.

**Order verification.** Unchanged from the ch6/ch8 audit and re-checked here:
`R_0 = qRoot`, `R_1 = qSh`, `R_2 = qElb`; spine `= R_0`, upper arm `= R_0 R_1`,
forearm `= R_0 R_1 R_2` (`:370-372` against `build_ch6.py:318-321`); axis order
y, z, x and y, z (`:359-363` against `shoulder.py:1-5, 94-99`); Euler convention
ZXY (`root_frame.py:35-58` against `Quaternion.Euler`). **AGREES.**

---

## 5. Question 5 — is the spawn/T-pose coincidence REQUIRED, or merely true in practice?

**Required. It is load-bearing in the structure of the assignment, and it is not
repaired by anything the setup does.** Answered from the code's structure, then
corroborated — not established — by what the system measured when part of it was
violated.

### 5.1 The structural argument

Suppose the rig spawned with its model axes rotated by `Q = ^{Scene}_{Model} R ≠ I₃`.
Every bone's captured rest becomes

```
c_rest_k'  =  ^{Scene}_{Bone_k,0} R  =  Q · ^{Model}_{Bone_k} R  =  Q · c_rest_k
```

and `:370-374` then writes `^{Scene}_{Seg_k} R · Q · ^{Seg_k}_{Bone_k} R` in place
of `^{Scene}_{Seg_k} R · ^{Seg_k}_{Bone_k} R`. The stray `Q` sits **inside** the
chain, between the segment frame and the bone, so in world terms bone `k` is
wrong by `(A·R_chain,k) Q (A·R_chain,k)⁻¹` — **an error that depends on `R_chain,k`
and therefore differs from bone to bone.** The figure is not merely misoriented as
a whole; the arms are wrong relative to the trunk. Equation (6.5) is therefore
**false for `Q ≠ I₃`**, not merely imprecise.

### 5.2 The forced T-pose does not rescue it — it presupposes it

`AlignArm` (`:217-218`, `:261-273`) is called with `Vector3.right` and
`Vector3.left` — **scene**-axis constants. The condition it is enforcing is
defined in the **model** frame: `:213` "the spawn arms lie along **the model's
rest axes (+x right arm, -x left)**", and `shoulder.py:14-15` "rest upper arm:
**local +x**" of {L12}. Enforcing a model-frame condition against scene axes is
correct only under the same coincidence. On a rig spawned with `Q ≠ I₃`, `AlignArm`
would swing the arms onto the scene's ±x while the trunk stayed at `Q` — an
internally inconsistent pose, worse than the one it started from.

### 5.3 Three further sites in the same file depend on it

- `:186-187` `rigRestHeightRaw = headEnd.position.y` — the rig's height read as a
  **scene y** component, with `:184` "rig spawns standing at the origin, feet at
  y=0". Under `Q ≠ I₃` this is a foreshortened height and `appliedScale` (`:195`)
  is wrong.
- `:311` `hip_height_rest,{hip.position.y}` — same component read, written to
  `rig_dimensions.csv`.
- `:222-223` and `:279-280` use distances only and are invariant; recorded so the
  line between the dependent and the invariant sites is visible.

So the coincidence is used **four times** in `IntegratedSceneReceiver.cs` alone,
not once.

### 5.4 The T-pose half was violated in practice, and the system measured the predicted error

`v1/KINEMATIC_MODEL.md:371-374`:

> "The rig's authored rest arm has a **small droop (≈8°) relative to a perfect
> T-pose**; the calibration (C = rest world rotation per bone, §3.4 convention)
> **preserves it as a constant visual offset** — the *rotation deltas* match the
> math exactly, which is what the checks above measure."

That is precisely the constant per-bone error §5.1 predicts when the captured rest
is not the model zero, measured rather than argued. It is the reason `AlignArm`
exists in `IntegratedSceneReceiver` at all, and the thesis records the contrast
itself: the other receiver "applies the uniform height scale but neither the
forced T-pose nor the measured segment lengths, and it **captures the rest
rotations of equation (6.5) from the rig as authored**" (`build_ch6.py:339`;
`IntegratedSceneReceiverV2.cs:166-170, 259-263` composes the identical product
with **no** `AlignArm` call). The two receivers are the same equation with the
assumption held and released.

### 5.5 What the committed evidence does and does not show about the spawn axes

`AlignArm` logs the spawn deviation it measures, `:270-272`. The committed capture
log `writing/v8/condensed/figures/src/ch7_handover_trails/editor.log:929, 941`
reads:

```
[IntegratedSceneReceiver] DEF-upper_arm.R spawn pose vs T-pose: upper 8.2 deg, forearm 5.7 deg (aligned)
[IntegratedSceneReceiver] DEF-upper_arm.L spawn pose vs T-pose: upper 8.2 deg, forearm 5.7 deg (aligned)
```

Both arms lie within **8.2°** of the scene's ±x, symmetrically, and the figure
matches `KINEMATIC_MODEL.md:371`'s ≈8° droop. **This bounds a spawn misalignment
about scene y or z at ≤ 8.2°; it bounds nothing about scene x**, which leaves the
arm axis fixed. It is a bound, not a proof of exact coincidence — which is the
whole point: the exact coincidence is asserted only in a code comment
(`:28-29`, `:237-238`) and cannot be established from committed data. **That is
why it must be printed as a stated assumption rather than relied on silently.**

### 5.6 Answer

**Required.** Under the code's structure equation (6.5) is false when the rig's
model axes do not coincide with the scene axes at spawn, or when the captured rest
is not the model's zero configuration. The T-pose half is *enforced* for the four
arm bones (against scene axes, hence still on the same assumption) and is
**not enforced at all for the spine bone**, whose `cHip` is the rig's authored
spine rest read directly in scene axes.

---

## 6. The discriminators

The author asked for evidence of the calibre that settled (3.22): a genuine
discriminator, not a plausibility argument. Four were found, and **D-1 and D-2 are
each individually decisive**. They are stated in the same form as
`FRAME_INVENTORY.md` §0's items so the two can be compared directly.

### D-1 (primary, for `R_0`, `R_1`, `A`). The system draws `A·R_0` as a frame: origin, name, and columns read as axes — with the rest rotation explicitly excluded.

`Unity/Assets/Scripts/RootFrameAxes.cs:73-77`:

```
// the measured root frame, composed exactly as the receiver
// composes it for the hip bone (before the rig rest rotation)
Quaternion q = anchor.rotation * Quaternion.Euler(receiver.lastRootEuler);
Vector3 o = hip.position;
SetTriad(rootAxes, o, q, RootLen);
```

with `:85-87`:

```
axes[0].SetPosition(1, o + q * Vector3.right * len);
axes[1].SetPosition(1, o + q * Vector3.up    * len);
axes[2].SetPosition(1, o + q * Vector3.forward * len);
```

and the file header `:1-12`: "Draws **the measured body root frame** on the driven
rig, plus the **Unity world frame** at the scene origin, **for the Chapter 3 frame
figure**… The **ROOT frame** (thick lines, at the hip bone) is **the measured torso
frame** as the solver streams it, **placed in the scene exactly as the receiver
places it: PersonAnchor.rotation \* Euler(root angles)**."

Four things at once, and each is the thing §0 of `FRAME_INVENTORY.md` looked for:

1. The product `A·R_0` — the first two factors of (6.5), and nothing else — is
   **assigned to a variable, given an origin (`hip.position`), and named a frame**,
   three times over. That is the exact structural test §0 observation (6) used to
   separate (3.22)'s operator from {L14}: "when the implementation wants a frame,
   it builds the factors together, assigns them, gives them an origin and names
   it." Here it does all three, **inside Unity**, on this equation's own product.
2. Its **columns are extracted and drawn as the frame's x, y and z axes in scene
   components**. Reading a matrix's columns as the described frame's axes in the
   reference frame is the definition of `^{Scene}_{L24} R`. An operator has no
   axes to draw.
3. The comment **excludes the rest rotation by name** — "(before the rig rest
   rotation)". The system itself draws the line this classification has to draw,
   and puts the frame on the `A·R_chain` side and the rig's axis convention on the
   `R_rest` side.
4. It is the **thesis's own Chapter 3 frame figure** that is drawn this way, and
   the same file draws the world frame beside it from `world.rotation` (`:79-80`) —
   a frame nobody disputes, by the identical call.

### D-2 (primary, for `R_rest`). The reference frame of `R_rest` is an exposed code parameter, the system states both readings, and filling it with the wrong frame was falsified live.

The general form, `v1/KINEMATIC_MODEL.md:108-112`, is a change of reference frame
written out in full: `C = R_charrest⁻¹ · R_hip_rest`, with `R_charrest` defined as
"the CHARACTER's authored rest facing **expressed as a world rotation**". The
collapsed form used in the code is named as such: "**With the stated assumption**,
`C = R_hip_rest` (only the bone's local axis convention)."

`Unity/Assets/Scripts/RootAngleReceiver.cs:61` implements the general form
literally, and `:37-38` exposes the reference frame as a public field with a
tooltip naming it: "The character's authored rest facing: (0,0,0) for a rig
authored facing world +Z."

And `KINEMATIC_MODEL.md:114-120` records what happens when that field is filled
with a **different frame**:

> "**Pitfall found during live verification**: anchoring the calibration to the
> *person's* reference pose instead (`C = Euler(0,180,0)⁻¹ · R_hip_rest`)
> **discards the absolute yaw** — the rig then stays at its authored facing (+Z,
> back to the camera) while the person faces the sensor. The correct anchor is the
> character convention… Implemented in `RootAngleReceiver.cs`
> (`referenceEuler = (0,0,0)`)."

**An operator has no reference-frame index to get wrong.** This failure mode is
entirely about which frame `R_rest`'s left index names; it was observable (a 180°
facing error), it was observed, and the system chose between two *named frames* to
fix it. That is a frame-relation discriminator, and it is of the same calibre as
(3.22)'s item (4) — both readings stated side by side, the system saying which it
implements — with the addition that here the choice is a parameter in the code.

### D-3 (corroborating, for the T-pose half of the assumption). The predicted violation was measured.

`KINEMATIC_MODEL.md:371-374` (§5.4 above) records the ≈8° authored droop being
preserved "as a constant visual offset" with "the rotation deltas match the math
exactly" — exactly the per-bone constant error that §5.1's algebra predicts when
the captured rest is not the model zero. Corroboration, not proof; listed as such.

### D-4 (corroborating, for the multiplication order). The operator form was implemented and falsified against data.

`IntegratedSceneReceiver.cs:26-34`:

> "Bones are driven like ArmAngleReceiver with the anchor PRE-multiplied:
> `bone.rotation = qA * qChain * C_rest` … **NOT the conjugation
> `qA*qChain*qA^-1*C_rest`** — that cancels the camera orientation out of the pose
> and **faced the rig the wrong way**; caught by
> `integration/plot_integrated_scene.py`, where **the DATA showed the person facing
> the sensor to 4.5 deg while the rendered rig did not**."

`qA·qChain·qA⁻¹` is precisely the similarity that re-expresses an **operator**
whose components are given in {Person} axes into {Scene} axes. It is the operator
reading of (6.5), it was implemented, and it was falsified against an observable
physical fact. The form kept is Craig's frame-chain left composition. The system
states both readings and says which one it implements — with the added weight that
it says how it found out.

### What was looked for and not found

No site was found where any of the four matrices is applied to a vector or to a
bone with the operand changed and the image read in the same basis; no
documentation was found offering the operator reading as the intended one; and no
axis-and-angle form exists for `R_rest`, which class 3 under D-054 would require
(D-057's (3.22) could be written `R_Z(−t_z) R_Y(−t_y)`; `R_rest` is an arbitrary
authored rig constant with no meaningful axis or angle). **The evidence is
one-directional.**

---

## 7. The classification, under the author's decision rule

> "if they are genuine active rotation operators, use class-3 operator notation;
> if they represent bone/model/scene frame orientations, use Craig two-frame
> notation and state the necessary spawn/T-pose assumption explicitly."

**The second branch fires, for all four.** They represent bone, model and scene
frame orientations. Craig two-frame notation, and the assumption stated.

**Equation (6.4), fully labelled:**

```
^{Person}_{L24} R = R_0
^{Person}_{L14} R = ^{Person}_{L24} R · ^{L12}_{L14} R
^{Person}_{L16} R = ^{Person}_{L24} R · ^{L12}_{L14} R · ^{L14}_{L16} R
```

with `^{L24}_{L12} R = I₃` stated once (the shoulder frame inherits the root
orientation, `shoulder.py:9-11`), and the left-side instances {L11}, {L13}, {L15}
by the mirror of Chapter 3.

**Equation (6.5), fully labelled:**

```
^{Scene}_{Bone_k} R = ^{Scene}_{Person} R · ^{Person}_{Seg_k} R · ^{Seg_k}_{Bone_k} R
```

`Seg_k ∈ {L24, L14, L16}` right and `{L24, L13, L15}` left, one per driven bone;
`^{Seg_k}_{Bone_k} R` is a constant of the rig; and `^{Scene}_{Person} R` — not
`^{Unity}_{Person} R` — is what the code's `qA` is (§10).

**This is not a mixed classification by class.** It is mixed in one respect only,
and that respect must be printed: `R_0`, `R_1`, `R_2` are class 1
unconditionally, while `R_rest`'s printed label is correct only under §8's
assumption, because the code obtains it by a shortcut (`^{Scene}_{Bone_k} R` at
spawn) rather than by the general two-frame form `^{Model}_{Scene} R ·
^{Scene}_{Bone_k} R` that `RootAngleReceiver.cs:61` implements.

**Why route (ii) of `FRAME_INVENTORY.md` §9 S-11 — "a fixed constant re-basing
factor, no bone frame named" — is rejected on its own terms.** Printed that way,
equation (6.5) reads

```
^{Scene}_{Bone_k} R = ^{Scene}_{Person} R · ^{Person}_{Seg_k} R · ^{Scene}_{Bone_k,0} R
```

whose indices **do not cancel**: `Seg_k` on the right of the middle factor against
`Scene` on the left of the last. The equation would be correct only through the
unstated assumption, and a reader checking it by Craig's rule would find it
malformed. Route (ii) does not avoid the assumption; it hides it. That is the
opposite of what D-054 is for.

---

## 8. The assumption that must be stated, and where

### 8.1 The assumption, in the system's own words

> **The rig's reference alignment.** The avatar is authored so that, with every
> driven bone at its identity rotation, it stands upright with its right side
> toward the scene's +x and its chest toward the scene's +z, and it is placed in
> the scene unrotated, so that **the model's axes coincide with the scene axes at
> start-up**. The model's zero configuration is then **the reference configuration
> of Section 3.2.2** — the T-pose that is the zero of every arm angle — and the
> setup **forces each arm onto the model's rest axes before the rest rotations are
> captured**. Under this assumption, and only under it, the orientation read from
> the scene at start-up is the constant `^{Seg_k}_{Bone_k} R` that equation (6.5)
> requires.

Sources, none of them invented: `v1/KINEMATIC_MODEL.md:101-102` ("a Unity humanoid
with identity hip rotation stands upright facing world +Z with its right side
toward +X"), `:110-112` ("(0,0,0) for a rig authored facing +Z"),
`RootAngleReceiver.cs:37-38`, `IntegratedSceneReceiver.cs:28-29` and `:237-238`
("the rig spawns unrotated (body axes = scene axes)"), `:210-218` (the forced
model T-pose), `build_ch3.py:290-291` (Section 3.2.2's reference configuration).

### 8.2 Where in the thesis it must be stated

1. **§6.3, in the paragraph immediately after equation (6.5)** —
   `scripts/build_ch6.py:331`. This paragraph already states **half** of the
   assumption: "The composition is correct only if that rest pose is the T-pose
   Chapter 3 defines as the zero of every arm angle (Section 3.2.2)." The missing
   half is the avatar's own reference alignment — that the rig is placed
   unrotated so that its model axes are the scene axes, which is what makes the
   orientation captured from the scene the constant the equation needs. **This is
   the one place the assumption must appear; without it (6.5) cannot be labelled.**
2. **The frame table**, wherever D-058's semantic frame names are tabulated
   (Chapter 2, beside Tables 2.2 and 2.3). It must gain the bone frame
   `{Bone_k}` — and `{L16}`/`{L15}` if `R_2` is labelled per §9.2 — with the
   note that `{Bone_k}` is the only frame in the inventory in which nothing is
   ever expressed, and that it exists because equations (6.4) and (6.5) relate it.
3. **§3.2.2, one cross-reference sentence** — `scripts/build_ch3.py:290-291`. That
   paragraph fixes the **subject's** reference configuration and its decode to
   (0, 180, 0); it is silent on the **avatar's**, which is the other half of the
   same statement and is what §6.3 will rely on. One clause pointing forward to
   §6.3 closes the gap without duplicating the content.

---

## 9. What the frame branch costs, and the two conflicts it creates

### 9.1 `{Bone_k}` — a frame with no read site

`{Bone_k}` fails `FRAME_INVENTORY.md` §4's usage test: nothing is ever expressed
in a bone's own axes (§1 above re-verifies the grep). It is nevertheless **forced**
by D-054 class 1, because equation (6.5)'s left-hand side *is* `^{Scene}_{Bone_k} R`
and its right factor *is* `^{Seg_k}_{Bone_k} R`. There is no way to print (6.5)
with both frames and not name it. **Recommendation:** issue it as a per-bone family
under §2.4's existing rule (the rig's own names are `DEF-spine`,
`DEF-upper_arm.R/L`, `DEF-forearm.R/L`), with one sentence in the frame table
saying it is the only entry justified by an equation rather than by a read site.
**Escalated**, because it is a genuine exception to a test the inventory applies
everywhere else.

### 9.2 `R_2`'s distal frame — this contradicts §4.7 and S-6, and must be ruled on

`FRAME_INVENTORY.md` §4.7 demotes "the forearm/wrist frame of Figure 3.5's
caption" on the ground that no read site exists, and §8.2 classifies the unprinted
elbow rotation (**C3-39**) as a **class-3 operator** acting on {L14}'s rest
direction. §9 **S-6** then records Figure 3.5's caption ("the wrists x along each
forearm") as a **caption defect**.

**That analysis is sound for Chapter 3 and does not reach Chapter 6.** §4.7 tested
the solver side only, where `R_elbow` is never assembled and only its first column
is used (`check_v1_overlay.py:47-66`). On the Unity side the matrix **is**
assembled (`IntegratedSceneReceiver.cs:362-363`) and **is** followed by a rest
rotation (`:372`), so the product `A·R_0·R_1·R_2` is the orientation of a forearm
segment frame and `cForearm` re-bases out of it. Printing `R_2` as a class-1
factor in (6.4) therefore requires the frame — and, under §2.3's landmark rule, its
name is already available: **{L16}** (right) / **{L15}** (left), origin at the
wrist landmark, {L14}'s basis turned by the elbow rotation, x along the forearm.

Three consequences follow and none of them is mine to decide:

- The **same symbol would be class 3 in Chapter 3 (C3-39) and class 1 in Chapter 6
  (6.4)**. D-054 is explicitly semantic rather than symbol-shaped, so this is legal
  — but it needs one sentence saying so, or one of the two must move.
- **Figure 3.5's caption would become correct**, since {L16}/{L15} is exactly the
  frame it draws. **S-6 would have to be revisited**, not applied.
- Alternatively the author may choose to **label only the three chain products** of
  (6.4) (`^{Person}_{L24} R`, `^{Person}_{L14} R`, `^{Person}_{L16} R`) and print
  `R_2` without a pair — but that leaves a bare factor in a class-1 equation, which
  is what D-054 forbids.

**Escalated.** It is the only part of the answer that changes a finding recorded
elsewhere.

---

## 10. What this does NOT settle

- **S-4 / X-3 — equation (6.5)'s missing levelling factor — is untouched and
  remains open.** Labelling makes it *harder to miss*, not fixed: `qA =
  anchor.rotation` at `:357` is the anchor's **global** rotation, and the anchor is
  parented to the levelled node (`:159-160`, `ArucoSceneReceiver.cs:212`), so the
  factor in (6.5) is `^{Scene}_{Person} R = ^{Scene}_{Unity} R · ^{Unity}_{Person} R`,
  while the `A` of equation (6.2) is `^{Unity}_{Person} R` alone. **Under Craig
  labelling the two cannot share a symbol**, so applying this classification
  forces S-4 to be confronted rather than allowing it to stay hidden. No edit is
  proposed here.
- **S-12** (`build_ch6.py:308`, "both branches inherit the levelled frame as local
  poses beneath one parent") is unaffected and still stands as recorded.
- **No number, no transformation direction and no code path is questioned
  anywhere in this file.** Every order and every factor checked against the
  implementation AGREES, as all three earlier audits found.

---

## 11. Choices I made

1. **I re-ran the (3.22) test rather than reasoning from D-057, and let it return
   the opposite answer.** The two structural tests §0 of `FRAME_INVENTORY.md` used
   — "is a constant of the frame rotated?" and "does the implementation assign the
   product to a frame variable, give it an origin and name it?" — are applied here
   unchanged. The first finds no rotated operand; the second finds an origin, a
   name and a drawn triad (D-1).
2. **I treated Unity's `Transform.rotation` API semantics as a premise and then
   corroborated it from inside the repository** (`RootFrameAxes.cs:85-87` reads a
   quaternion's columns as a frame's axes), rather than asserting it from
   documentation alone.
3. **I gave the operator reading its strongest form before rejecting it**, including
   the objection that `AlignArm` uses the identical syntax on the identical
   left-hand side (§3.3) and the objection that `Vector3.up/forward/right` are
   scene-axis constants (§4). Both are answered from build sites, not by analogy.
4. **I treated the 8.2° spawn log as a bound, not as proof.** It bounds a
   misalignment about scene y and z and says nothing about scene x, and I say so
   (§5.5). A numerical coincidence is not evidence.
5. **I did not name the new frames.** `{Bone_k}`, `{L16}` and `{L15}` are proposed
   from the system's own vocabulary and §2.3's existing rule, and escalated for a
   D-058-style ruling rather than issued.
6. **I recorded the conflict with §4.7/S-6 rather than resolving it** (§9.2), and
   I did not touch S-4 even though labelling (6.5) makes it unavoidable (§10).
7. **I did not edit equations (6.4) or (6.5), or any other file.**

---

## 12. Escalations for the author

1. **`{Bone_k}` is a frame with no read site (§9.1).** Forced by D-054 once (6.5)
   is printed in Craig form. It is a genuine exception to the inventory's usage
   test and should be declared as one in the frame table.
2. **`R_2`'s distal frame contradicts §4.7, S-6 and C3-39's class-3 classification
   (§9.2).** Issuing {L16}/{L15} makes Figure 3.5's caption correct and requires
   S-6 to be revisited; not issuing it leaves a bare factor in (6.4). This is the
   only finding elsewhere in the corpus that this classification disturbs.
3. **Labelling (6.5) forces S-4 (§10).** `A` in (6.5) is `^{Scene}_{Person} R`;
   `A` in (6.2) is `^{Unity}_{Person} R`. They cannot keep one symbol under Craig
   notation. S-4's content fix and this notation pass now have to be sequenced.
4. **The spawn-axis coincidence cannot be verified from committed data (§5.5).**
   It is asserted in two code comments and bounded to ≤ 8.2° about two of three
   axes by one capture log. It must be printed as a stated assumption of the
   reconstruction, not as an established fact — which is what §8 proposes.

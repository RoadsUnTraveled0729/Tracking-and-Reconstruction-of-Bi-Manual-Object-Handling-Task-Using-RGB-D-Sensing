# Does the Unity side contain ONE coordinate frame or TWO? — resolution by code and data

Status 2026-09-12. Read-only investigation. **Nothing in the thesis, the builders,
the figure scripts, the code, `DECISIONS.md`, `FRAME_INVENTORY.md` or the three
audit reports was changed to produce it. This file is the only write.** Nothing is
applied; the author's instruction that the thesis must not be edited until this is
resolved is observed.

This settles `FRAME_INVENTORY.md` §4.3, the one candidate the inventory reported
without resolving, and it unblocks the three table rows blocked on it (F2.4b,
C7-04, C7-07).

---

## 0. Verdict, stated first

**TWO bases, not one.** The rig-side read sites do **not** use the basis of
equation (6.1). A **proper rotation of 32.04°** separates them. This was
established from the data alone, by a translation-free test that recovered the
matrix without being told what to look for (§6).

The author's decision rule therefore fires on its **second branch**: *"If a
non-identity transform separates the Equation (6.1) basis from the rig-side read
basis used for reported positions, define two distinct frames and print that
transform explicitly."*

**But the second basis is not new.** It is the basis of **{Levelled}**, which
`FRAME_INVENTORY.md` already carries as entry 7. The rig-side read sites share
{Levelled}'s basis **exactly** (max difference 0.0 — §7) and differ from
{Levelled} only in **origin**, by a pure translation of 71.6 cm. That is the trap
the author flagged, and it appears here — just not between the pair the rule
names.

So the Unity side contains:

| | basis | origin | already named? |
|---|---|---|---|
| **{Unity}** | `S ·` {World} — eq (6.1) | desk-marker centre | yes, entry 6 |
| **{Levelled}** | `G · S ·` {World} | desk-marker centre | yes, entry 7 |
| **{Scene}** (the name the system uses) | `G · S ·` {World} — **identical to {Levelled}** | the drawn floor, 71.6 cm below | **no — this is the gap** |

Two bases. Three (origin, basis) frames. Figure 2.4(b) draws the third and labels
it with the first.

---

## 1. Question 1 — What coordinate basis is produced by Equation (6.1)?

**{Unity}: the desk-marker world basis with the second and third coordinates
exchanged. Origin at the desk-marker centre. Left-handed. No levelling, no drop.**

From code, not prose:

- `v1/aruco/frames.py:38-40` — the matrix itself:
  ```
  WORLD_TO_UNITY = np.array([[1.0, 0.0, 0.0],
                             [0.0, 0.0, 1.0],
                             [0.0, 1.0, 0.0]])
  ```
  with `:36-37` "world (right-handed, z out of the desk marker face) -> Unity
  (left-handed, y up): swap y and z."
- `v1/aruco/frames.py:85-88` — the map applied: `unity_from_world` returns
  `WORLD_TO_UNITY @ t_w` for a point and `WORLD_TO_UNITY @ R_w @ WORLD_TO_UNITY`
  for an orientation. This function *is* equation (6.1).
- `frames.py:12-15` fixes the origin: "world — the **DESK marker's own frame** (id
  2) … Everything — wall, object, and the camera itself — is expressed here."
  `S` is linear, so the origin is unmoved: eq (6.1)'s origin is the desk-marker
  centre.
- The thesis prints it at `build_ch6.py:271-275` as `p_U = S p_w`, `R_U = S R_w S`,
  and Table 2.2 row 9 (`build_ch2.py:234`) declares `S` to map "the world frame W"
  → "the Unity frame U", citing "Chapter 6, equation (6.1)".

`det S = −1` (verified). **No rotation and no translation of any kind is in
equation (6.1)** — in particular neither the levelling nor the floor drop.

This basis has genuine read sites and is not being emptied by anything below:
`ArucoSceneReceiver.cs:114` ("A pose node in ArucoWorld-local coordinates"),
`:119-120`, `:389-390` (`objectNode.localPosition = pos`), and the object log
written at `:392-397`, which logs the **local** `pos`/`euler`, not a global
position.

---

## 2. Question 2 — In what basis are the Unity person-log positions stored?

**The CSV holds two different frames in one row, and they must not be conflated.**

`unity_person_log.csv` is written at `IntegratedSceneReceiver.cs:393-405`, header
at `:252-255`.

**(a) `pel_x, pel_y, pel_z` — {Person}, not any Unity basis.** They are the
streamed record value written back unchanged (`:399`, the variable `pelvis`),
documented at `:13` ("f32 pelvis xyz (**Pipeline-A Unity space = camera frame, y
flipped**)") and at `:78` (`public Vector3 lastPelvis; // person space, as
received`). This is the `FRAME_INVENTORY.md` §2.5 trap — "Unity space" in v1 means
{Person}. Confirmed numerically: `evaluate_ch7_restructured.py:116-117` asserts
`log.pel == stream.pel` to `1e-5` m, i.e. the column is the **un-mapped input**.

**(b) `hip_*, rh_*, lh_*, rsh_*, lsh_*, rel_*, lel_*` — the Unity global scene
basis, i.e. {Scene}.** They are `Transform.position` reads
(`:395-398`: `hip.position`, `rHand.position`, `lHand.position`,
`upperArm.position`, `lUpperArm.position`, `forearm.position`,
`lForearm.position`). `Transform.position` is Unity's **world-space** property.

That these are global and not {Unity}-local is forced by the hierarchy plus the
absence of any local read, both checked directly:

- `IntegratedSceneReceiver.cs:180` `rigRoot = hip.root;` — the rig is *found*
  (`FindBone`, `:128-133`), never re-parented. A grep for `SetParent` in the whole
  file returns exactly one hit, `:160` `anchor.SetParent(world, false)` — the
  **anchor** is parented to ArucoWorld; **the rig is not**.
- A grep for `localPosition` / `localRotation` / `InverseTransformPoint` /
  `TransformDirection` on any bone returns **nothing**. The only local writes in
  the file are `anchor.localPosition` (`:161`) and `anchor.localRotation`
  (`:162-163`). Nothing is ever expressed in a bone's own axes or in ArucoWorld's
  local axes.
- The values get there through `:378` `Vector3 target = anchor.TransformPoint(pelvis);`
  and `:379` `rigRoot.position += target - hip.position;`. `TransformPoint` on a
  node parented to `world` returns a **global** point.

So the seven joint triples are written in whatever basis Unity's scene root has,
which §5 identifies and §6 measures.

---

## 3. Question 3 — In what basis are the positions exported to `human_pairs.csv`?

**Both column families — `measured_*` and `rig_*` — are in {Scene}. The `rig_*`
columns are the person-log global positions copied verbatim.**

`writing/v8/condensed/scripts/evaluate_ch7_restructured.py`:

- `:139` `rig = xyz(log, prefix)` — taken straight from `unity_person_log.csv`,
  no transform applied.
- `:136-138`
  ```
  measured = (G @ (P @ T[:3, :3] @ xyz(raw, side + '_' + joint).T
                    + cp[:, None])).T + offset
  ```
  where `P` is eq (6.1)'s swap `S` (`:91`), `T = inv(T_cam_desk)` (`:106`),
  `cp = P @ T[:3,3]` = `S t_cam` (`:107`), `G` is the levelling rotation
  (`:110`), and `offset` is the floor drop (`:114`).

**Verified, not assumed** — the `rig_*` columns and the log columns are
bit-identical:

```
human_pairs rig_* (right elbow) vs unity_person_log rel_* : max diff = 0.0 m  (n = 100, r6b; 650, r7)
human_pairs rig_* (right wrist) vs unity_person_log rh_*  : max diff = 0.0 m  (n = 100, r6b; 650, r7)
```

Spot check, r6b right elbow frame 500: `human_pairs.csv` row 2 gives
`rig = (-0.224183, 1.040151, 0.693136)`; `unity_person_log.csv` frame 500 gives
`rel = (-0.224183, 1.040151, 0.693136)`.

The harness **asserts** the two families land in one frame, at `:119-120`:

```
expected_hip = (G @ (M @ xyz(log, 'pel').T + cp[:, None])).T + offset
hip_delta = float(abs(xyz(log, 'hip') - expected_hip).max())
assert time_delta <= 1e-5 and pelvis_delta < 1e-5 and hip_delta < 1e-3
```

`M @ pel + cp` is exactly equation (6.2), i.e. a point **in the eq (6.1) basis**.
The assertion says the rig's global read equals `G · (that point) + offset`. **The
pipeline's own passing assertion is the statement that the rig-side read basis is
the eq (6.1) basis turned by `G`.**

The same assertion exists independently in the pre-thesis tool,
`eval/unity_check/check_unity_log.py:138-142`, and its inverse is written out at
`:147-149`:

```
def to_pixels(p_unity):
    """Unity scene world -> person space -> sensor frame -> pixels."""
    p_person = (M.T @ (G.T @ (p_unity - world_pos).T - cam_pos_u[:, None]))
```

To leave the rig-side read frame the code must undo **`G.T` (a rotation)** and
**`world_pos` (a translation)**. If the rig-side basis were eq (6.1)'s, `G.T`
would not be there.

---

## 4. Question 4 — In what basis are Figures 7.3 and 7.4 plotted?

**{Scene}. The script plots `human_pairs.csv` columns directly, in centimetres,
with no transform.**

`writing/v8/condensed/scripts/make_ch7_valid_joint_figures.py`:

- `:12` reads `audit_evidence/ch7_restructured/human_pairs.csv`.
- `:25` `p = samples[[prefix + '_' + a for a in 'xyz']].to_numpy() * 100` — the
  only operation applied to the coordinates is a metre→centimetre scale.
- `:28-29` `ax.scatter(p[:, 0], p[:, 2], p[:, 1], ...)`, with `:37-39`
  `ax.set_xlabel('Unity x (cm)')`, `ax.set_ylabel('Unity z (cm)')`,
  `ax.set_zlabel('Unity y (cm)')`. The vertical plot axis carries the data's
  second component, consistent with the caption at `build_ch7.py:320` ("the
  vertical plot axis is Unity y").

So the three axis labels that say **"Unity"** are labels on {Scene} components,
not on equation (6.1)'s. The captions at `build_ch7.py:320` and `:325` add "in the
same Unity world frame".

**The origin matters here, not only the basis.** The plotted numbers carry the
floor drop:

```
Figure 7.3, right wrist, r6b:  measured_y  77.96 .. 87.48 cm
                               rig_y       79.08 .. 96.58 cm
without the 71.62 cm floor drop they would read   6.34 .. 15.86 cm
error_cm                        7.259 .. 23.385    <- the drop cancels here
```

This qualifies one of the facts supplied with this task. The floor drop **does**
cancel from every reported *error and distance* (`:141`
`error = np.linalg.norm(rig - measured, axis=1) * 100`, common `offset`). It does
**not** cancel from the *coordinates plotted on the axes of Figures 7.3 and 7.4*,
nor from the triple printed in Chapter 6 §6.5, nor from Table 6.2. Those are
absolute component reads and they depend on the origin.

---

## 5. Question 5 — What transform lies between the eq (6.1) display axes and the avatar-rig root / read sites?

**`^{Scene} P = G · ^{Unity} P + (0, d, 0)`** — a proper rotation of 32.04°
followed by a pure vertical translation. Built by two lines of Unity code on one
node, and reproduced exactly outside Unity.

**The rotation.** `Unity/Assets/Scripts/ArucoSceneReceiver.cs:212`:
```
world.rotation = Quaternion.FromToRotation(gravityUpLocal, Vector3.up);
```
`world` is the `ArucoWorld` node (`:206`) and has **no parent**, so
`world.rotation` *is* its global rotation. `gravityUpLocal` is read from the scene
record (`:190-192`) and is written by
`v1/aruco/calibrate_scene.py:279`:
```
"gravity_up_unity": [float(x) for x in (unity_from_world(np.eye(3), up_w)[0])],
```
— the calibrated gravity direction expressed **in the eq (6.1) basis** (hence
"Local"), which is why the levelling is a map *out of* that basis.

**The translation.** `ArucoSceneReceiver.cs:213` `world.position = WorldOffset();`
and `:308-310`:
```
// Drop the whole reconstruction so the floor sits at scene y = 0.
float floorY = world.TransformPoint(center - g * (DeskThick + LegH)).y;
world.position += Vector3.down * floorY;
```
`WorldOffset()` is `(2.5, 0, 0)` in the standalone receiver (`:315`) and
`Vector3.zero` in the integrated one (`IntegratedSceneReceiver.cs:126`), so for
every recording in the thesis the whole translation is the floor drop.

**Why this reaches the rig even though the rig is not parented to ArucoWorld.**
The rig's position is set at `IntegratedSceneReceiver.cs:378-379` from
`anchor.TransformPoint(pelvis)`, and `anchor` **is** parented to `world`
(`:160`). `TransformPoint` composes the parent's global transform, so the rig is
placed at `G · (p in eq-6.1 basis) + world.position` and then stays in Unity's
global frame, which is where `hip.position` reads it back. **The non-parenting of
the rig is what makes the read global rather than local; it is not itself the
argument that a second basis exists.** The argument is §6.

**The constants**, recomputed from the committed calibrations:

| | r6b (`scene_calibration_r6bc.json`) | r7 (`scene_calibration_r7c.json`) |
|---|---|---|
| gravity in eq (6.1) basis | `(−0.021236, 0.847708, 0.530038)` | identical |
| `G` | `[[0.999756, 0.021236, 0.006092], [−0.021236, 0.847708, 0.530038], [0.006092, −0.530038, 0.847952]]` | identical |
| `det G` | `1.000000` | `1.000000` |
| orthogonality error | `2.2e−16` | `2.2e−16` |
| angle | **32.0368°** | 32.0368° |
| `max |G − I|` | **0.530038** | 0.530038 |
| floor drop `d` | **0.716215 m** | **0.709312 m** |

`d = origin_above_tabletop_m + DeskThick + LegH` exactly (residual `0.00e+00`;
`DeskThick + LegH = 0.72` at `check_unity_log.py:41`). The drop is **recording-
dependent** (0.716215 against 0.709312 m), which is independent confirmation that
the {Scene} *origin* is a presentational constant and not a measurement.

---

## 6. The decisive numerical check — is the transform identity, a pure translation, or a rotation?

The author's operative test is "numerically use the same basis". A translation
cannot change a basis; a rotation can. So the check is run on **difference
vectors**, which kill every translation and every origin, leaving only the basis.

Take a point that exists in both representations: the pelvis. `pel_*` gives it in
{Person}; equation (6.2) puts it in the eq (6.1) basis as `p_U = M·pel + cp`;
`hip_*` gives the same physical point at the rig-side read site. Then form
consecutive-frame displacements `d_U` and `d_rig` and compare.

```
================ r6b ================                    ================ r7 ================
hypothesis A: rig read = eq(6.1) basis + pure translation  hypothesis A
   max residual = 0.393232 m                                  max residual = 0.413688 m
hypothesis B: rig read = G · eq(6.1) basis + translation   hypothesis B
   max residual = 0.000001 m                                  max residual = 0.000001 m

translation-free test, n = 145 displacements > 1 mm       n = 263 displacements > 1 mm
   max |d_rig − d_U|    = 0.107750 m   <- 0 iff same basis    = 0.054265 m
   max |d_rig − G d_U|  = 0.000002 m                          = 0.000002 m
   max ||d_rig|| − ||d_U||  = 0.000002 m  (isometry)          = 0.000002 m
   median angle(d_rig, d_U) = 28.564 deg                      = 31.125 deg
```

Then, discarding every prior, the basis map was **recovered from the two logged
coordinate sets by least squares on the displacements alone**:

```
r6b:  [[ 0.999750  0.021243  0.006081]          r7:  [[ 0.999713  0.021231  0.006101]
       [-0.021241  0.847710  0.530035]                [-0.021229  0.847706  0.530025]
       [ 0.006091 -0.530043  0.847964]]               [ 0.006066 -0.530032  0.847947]]
  max|Rest − I| = 0.530043                        max|Rest − I| = 0.530032
  max|Rest − G| = 0.000012                        max|Rest − G| = 0.000043
  recovered angle = 32.0363 deg                   recovered angle = 32.0394 deg
```

(The residual 1e−5 is the float32 precision of the Unity log, not a modelling
error.)

**Result, in the terms the author set out:**

- **Not the identity.** `max|Rest − I| = 0.53`; corresponding displacement vectors
  differ in direction by a median of 28.6° / 31.1°.
- **Not a pure translation.** A translation leaves every difference vector
  unchanged; these change by up to 10.8 cm, while their lengths are preserved to
  2 µm. The map is an **isometry that is not the identity** — a rotation.
- **It is exactly `G`**, the levelling rotation, recovered blind from the data to
  1.2e−5 / 4.3e−5.

**The levelling is a rotation and it stands between equation (6.1) and every
rig-side read site. A second basis therefore exists.**

---

## 7. The trap the author flagged — where it actually occurs

The author warned that two systems can share a basis and differ in origin, and
asked for that to be stated precisely rather than forced into a branch. It does
not occur between eq (6.1) and the rig-side read sites (§6 settles those as
different bases). **It occurs between {Levelled} and the rig-side read sites.**

`eval/offset/carry.py:64` builds {Levelled}'s map as
`self.G = from_to_rotation(self.g, np.array([0.0, 1.0, 0.0]))` from the same
`gravity_up_unity` (`:62-63`), and `:68-69` `level(p) = (G @ p.T).T` applies **no
translation**. Checked against the matrix Unity's ArucoWorld applies:

```
carry.LeveledWorld.G  ==  ArucoWorld levelling G :  max diff = 0.0
```

Then, on one shared object track (900 frames, r6b):

```
{Levelled} vs Unity scene root
  scene − levelled : constant over all frames?  max spread = 0.0   value = (0, 0.716215, 0)
  translation-free test:  max |d_scene − d_levelled| = 1.1e−16   <- IDENTICAL BASIS

{Unity} (eq 6.1) vs {Levelled}
  max |d_levelled − d_unity|   = 0.005484 m   <- DIFFERENT BASIS
  max |d_levelled − G d_unity| = 0.000000 m
```

**So {Levelled} and the rig-side read frame share a basis exactly and differ only
by a pure vertical translation of 71.6 cm.** The second basis the decision rule
demands is therefore **not a new basis at all** — it is {Levelled}'s, which
`FRAME_INVENTORY.md` entry 7 already defines and names from the system's own
vocabulary.

---

## 8. Applying the author's decision rule, explicitly

> *"If all rig-side read sites numerically use the same basis as Equation (6.1),
> keep one {Unity} frame and correct the misleading Figure 2.4(b) caption."*

**Does not apply.** §6 shows the rig-side read sites numerically use a basis
32.04° away from equation (6.1)'s, recovered from the data without prior
knowledge.

> *"If a non-identity transform separates the Equation (6.1) basis from the
> rig-side read basis used for reported positions, define two distinct frames and
> print that transform explicitly."*

**This branch applies.** The separating transform is `G`, a proper rotation
(`det +1`, orthogonality error 2.2e−16) of 32.0368°, plus a pure translation of
`(0, 0.716215, 0)` m (r6b) / `(0, 0.709312, 0)` m (r7).

**Two distinct frames are therefore required — and there is a third, because the
origin is read too.** The full, minimal declaration:

| frame | basis | origin | status |
|---|---|---|---|
| **{Unity}** | `S ·` {World}, left-handed, y up | desk-marker centre | **already defined**, entry 6 |
| **{Levelled}** | `G S ·` {World} | desk-marker centre | **already defined**, entry 7 |
| **{Scene}** | `G S ·` {World} — *the same basis as {Levelled}* | the drawn floor, `d` below the desk marker along levelled y | **NEW — this is the gap §4.3 left open** |

### 8.1 The transforms, ready to be printed (D-054 / D-056 forms)

```
^{Levelled}_{Unity} R = G                                  class 1, det +1, 32.04 deg
^{Scene}_{Unity}    R = G                                  class 1, det +1 — same rotation
^{Scene} P_{Levelled}ORG = (0, d, 0)                       pure translation; identity rotation
^{Scene} P = G · ^{Unity} P + (0, d, 0)
d = origin_above_tabletop_m + DeskThick + LegH  = 0.716215 m (r6b), 0.709312 m (r7)
```

`^{Levelled}_{Unity} R = G` is already the form `FRAME_INVENTORY.md` §4.1
prescribes; nothing there changes. The two additions are the row for {Scene} and
the one-line statement that `^{Scene}_{Levelled} R = I` — that {Levelled} and
{Scene} are **the same axes with different origins**, so every distance, every
scatter shape and every direction agrees between them and only absolute component
values differ.

### 8.2 Why {Scene} passes the inventory's own usage test

The inventory demotes a candidate unless a position or an orientation is
*expressed* in it, component by component. {Scene} passes on its **origin**, at
four independent sites, three of them in the printed thesis:

- `make_ch7_valid_joint_figures.py:25, 28-29, 37-39` — Figures 7.3 and 7.4 plot
  absolute coordinates, axis by axis, and label them; the numbers are 71.6 cm
  different from {Levelled}'s (§4).
- `build_ch6.py:434` — `p_scene = L p_U + (0, 0.72, 0) = (0.00, 0.75, 0.44) m`,
  a coordinate triple printed in {Scene}.
- `build_ch6.py:435, 475` — "The spine bone lands at (0.0, 74.8, 43.8) centimetres,
  2.8 centimetres above the drawn desk top at 72.0", and Table 6.2 prints **both**
  triples for one point: "pelvis (0.2, −20.5, 38.9) cm **in display axes**;
  (0.0, 74.8, 43.8) cm **in the scene**". *The thesis already prints one physical
  point in two frames and gives them two different names.* That is the strongest
  single piece of evidence that the thesis needs two, and it is in the thesis
  today.
- `IntegratedSceneReceiver.cs:395-403` — seven joint triples per frame, logged as
  global positions.

### 8.3 The name {Scene} is the system's own

Required by D-056. The system says it, unprompted, in five places:

- `ArucoSceneReceiver.cs:308` "Drop the whole reconstruction so the floor sits at
  **scene y = 0**."
- `ArucoSceneReceiver.cs:209-210` "the depth-fit gravity direction becomes
  **scene up**."
- `IntegratedSceneReceiver.cs:24` "turns person-space coordinates into **scene
  coordinates** directly"; `:238` "body axes = **scene axes**".
- `check_unity_log.py:148` docstring: "**Unity scene world** -> person space ->
  sensor frame -> pixels."
- `build_ch6.py:475`, Table 6.2: "(0.0, 74.8, 43.8) cm **in the scene**".

The ch6/ch8 audit's provisional label for it was `{S}`; under D-056 no letter is
issued and the semantic name is **{Scene}**. Note the adjacency with **{Sensor}**
— escalated in §11.

---

## 9. What is wrong with Figure 2.4(b)'s caption, and what it should say

The caption (`build_ch2.py:213`) reads:

> "(b) The Unity frame **U** at the root of the avatar rig, with its axes drawn at
> the origin. The avatar stands in the T-pose, the reference configuration of the
> model."

and the body text repeats it (`build_ch2.py:217`): "Figure 2.4(b) shows **U** at
the root of the avatar rig."

The figure itself (`writing/v8/figures/ch3_fig_sensor_unity.png`) is a Unity
editor screenshot: the avatar standing on a ground plane in the T-pose with the
red/green/blue transform gizmo at its feet, y up, x and z in the ground plane.

**Four defects, in order of seriousness.**

1. **The label is wrong by 32.04°.** Table 2.2 row 9 (`build_ch2.py:234`) defines
   `U` as the output of `S`, citing equation (6.1). The axes in the screenshot are
   Unity's **scene** axes, which §6 measures to be `G` — 32.04° — away from that.
   The figure is the reader's *first* sight of the Unity frame, in Chapter 2, and
   it shows the wrong one.
2. **The origin is wrong by 71.6 cm.** Equation (6.1)'s `U` has its origin at the
   desk-marker centre. The drawn origin is the Unity scene origin, which in the
   reconstruction sits `d = 0.716` m below the desk marker along levelled y.
3. **"At the root of the avatar rig" names a moving origin.** The rig root is
   re-translated on every frame — `IntegratedSceneReceiver.cs:379`
   `rigRoot.position += target - hip.position;`. It coincides with the scene
   origin only at spawn, before any data arrives (`:186-187`, "rig spawns standing
   at the origin, feet at y=0"). A frame origin cannot be attached to a node that
   moves with the measurement.
4. **The screenshot does not contain the frame it is captioned with.** There is no
   desk, no wall, no marker and no ArucoWorld node in the image — it is the bare
   rig scene. Equation (6.1)'s basis is not present in the picture at all.

**The figure is not wrong; only the caption is.** It is an accurate picture of
{Scene}, and {Scene} is the frame Chapter 7's own Figures 7.3 and 7.4 plot in — so
the figure earns its place once it is named correctly, and it becomes the reader's
introduction to the frame Chapter 7 reports in.

**Proposed replacement caption and sentence** (for the author to accept, amend or
overrule — *not applied*):

> "(b) The Unity **scene** frame, left-handed with y up, drawn at the origin of the
> Unity scene, where the avatar rig spawns in the reference T-pose. The
> reconstruction reaches this frame from the display axes of equation (6.1) by the
> levelling rotation of Section 6.4; Figures 7.3 and 7.4 report in it."

and, for `build_ch2.py:217`, replace "Figure 2.4(b) shows U at the root of the
avatar rig" with a sentence that separates the two: the display axes `U` of
equation (6.1) are anchored on the desk marker and are **not** levelled; the Unity
scene frame of Figure 2.4(b) is those axes turned upright by the calibrated
gravity and dropped so the drawn floor is at zero height.

---

## 10. What this unblocks

The three rows `FRAME_INVENTORY.md` §8 marked BLOCKED on §4.3 are now determinate.

- **F2.4b** — caption relabelled to {Scene}; §9 above.
- **C7-04** (Figures 7.3/7.4, "the same Unity world frame", `build_ch7.py:320,
  325`) — the frame is **{Scene}**. Figures 7.1/7.2 and Sections 7.2/7.3.3 are in
  **{Levelled}**. The audit's X-4 said these "differ by the levelling and the
  placement"; **they differ by the placement only** (§7): same basis, origins 71.6 cm
  apart. So the defect is narrower than X-4 recorded — the scatter shapes,
  directions, tilts and distances are identical between the two; only absolute
  component values differ. The fix is to name both frames and say they share axes.
- **C7-07** (equations (7.5)/(7.6)) — both operands of (7.5) are in **{Scene}**,
  verified: `evaluate_ch7_restructured.py:133` and `:139` add the identical
  `offset` before `:141` differences them. Craig form `^{Scene} p^{rig}`,
  `^{Scene} p^{meas}`.

One further consequence, **not** in scope but visible from here and recorded so it
is not lost: the ch6/ch8 audit's **X-3** (equation (6.5) omits the levelling
factor) is confirmed by the same evidence — `IntegratedSceneReceiver.cs:357`
`qA = anchor.rotation` is a **global** rotation, and `anchor` is parented to
`world` (`:160`), so `anchor.rotation = G · A`. With {Scene} named, X-3's fix
becomes a labelling statement rather than an open question: equation (6.5) as
printed is `^{Unity}`-relative, and the rotation actually written to the bone is
`^{Scene}`-relative.

---

## 11. Escalations for the author

1. **{Scene} against {Sensor} — a readability adjacency, not a collision.** Both
   are the system's own names and both begin "Se". They never appear in the same
   equation (the {Sensor}→{Scene} composite of §7.3 is the one place they would
   meet). Alternatives from the system's own vocabulary: **{UnityScene}**
   (`check_unity_log.py:148` "Unity scene world"), or **{Drawn}**. Recommendation:
   keep **{Scene}**, because it is what the code and Table 6.2 already say.
   *Author's to overrule in one substitution.*

2. **Three frames or two?** The strict reading of the usage test gives three
   ({Unity}, {Levelled}, {Scene}), because both origins are read component-wise.
   The alternative is to declare **two** — {Unity} and {Levelled} — and treat the
   floor drop as a stated presentational offset applied at the three print sites
   (Figures 7.3/7.4, §6.5, Table 6.2) rather than as a frame. That is defensible
   and is closer to the inventory's §4.2 demotion of the drop. **Its cost is
   explicit:** Figures 7.3 and 7.4 would then be plotting "{Levelled} plus 71.6 cm"
   on axes labelled "Unity y", and Table 6.2's two triples for one point would lose
   one of their two names. My recommendation is three, on the same usage test the
   inventory applies everywhere else. *Author's call.*

3. **The fact supplied with this task needs one qualification.** "The floor drop
   cancels from every reported number" is true of every reported **error and
   distance** and false of the **plotted and printed coordinates** (§4): Figure
   7.3's vertical axis reads 78–97 cm because of it, and would read 6–16 cm
   without it. Nothing numerical is wrong anywhere; the qualification matters only
   for whether the drop can be treated as invisible, and it cannot be at the three
   sites where absolute components are shown.

4. **Two prose sentences in Chapter 6 become checkable.** `build_ch6.py:308` ("both
   branches inherit the levelled frame as local poses beneath one parent, so
   nothing rewrites the data") is true of the **object** branch, whose node is
   parented to ArucoWorld and whose log is local. It is **not** true of the
   **rig**, which is not parented to ArucoWorld (`IntegratedSceneReceiver.cs:180`;
   only `anchor` is, `:160`) and whose logged positions are global. Flagged as a
   prose item for the revision pass, outside this file's scope.

---

## 12. Choices I made

1. **I ran the basis test on difference vectors, not on positions.** The decision
   rule asks about the basis; differencing removes every origin and every
   translation, so the test cannot be confounded by the floor drop. Positions were
   used only as a secondary confirmation (hypotheses A and B in §6).
2. **I recovered the basis map blind, by least squares, in addition to testing the
   two named hypotheses.** Testing `G` alone would have been a confirmation; the
   least-squares recovery is independent of what the code says the answer is, and
   it returns 32.04° with no prior.
3. **I ran everything on both recordings (r6b and r7)** rather than one, so that a
   per-recording artefact could not pass as a frame property. The rotation is
   identical in both; only the drop differs, which is itself informative.
4. **I treated the non-parenting of the rig as a mechanism, not as evidence.** The
   author forbade inferring a second frame from Unity hierarchy. The hierarchy
   appears in §5 only to explain *how* the transform reaches the rig; the existence
   of the second basis rests entirely on §6.
5. **I named the new frame {Scene} from the code and Table 6.2 rather than adopting
   the ch6/ch8 audit's `{S}`**, because D-056 replaced letters with semantic names
   and `S` is the swap matrix.
6. **I did not treat {Levelled} and {Scene} as one frame**, even though they share
   a basis exactly, because the usage test the inventory applies is passed on both
   origins. The alternative is escalated as item 2 rather than decided.
7. **I stated the qualification to a fact I was given** (§4, escalation 3) rather
   than working around it, because it changes what may be said about Figures 7.3
   and 7.4.
8. **I proposed caption wording but applied nothing.** Every file in the repository
   is unchanged except this one.

---

## Appendix — reproducing the checks

Three scripts were written under the session scratchpad (not in the repository)
and run with `/home/luo/anaconda3/bin/python`:

- `check.py` — hypotheses A/B on the pelvis, the translation-free displacement
  test, the blind least-squares basis recovery, and the `human_pairs.csv` /
  `unity_person_log.csv` identity check, for r6b and r7.
- `check2.py` — `carry.LeveledWorld.G` against the ArucoWorld levelling matrix;
  {Levelled} against the scene root on the object track; {Unity} against
  {Levelled}.
- `check3.py` — the floor-drop constants and their decomposition, and the
  magnitude of the drop in the Figure 7.3 axis values.

Inputs, all committed or present in the working tree:
`eval/output/scene_calibration_r6bc.json`, `eval/output/scene_calibration_r7c.json`,
`writing/v8/condensed/figures/src/ch7_trails_revision/unity_person_log.csv`,
`writing/v8/condensed/figures/src/ch7_handover_trails/unity_person_log.csv`,
`writing/v8/condensed/audit_evidence/ch7_restructured/human_pairs.csv`,
`eval/output/unity_check_r6b_trails/integrated_stream.csv`,
`eval/output/unity_check_r7/integrated_stream.csv`.

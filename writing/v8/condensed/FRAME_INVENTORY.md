CURRENT INVENTORY: 2026-09-13, D-082

The reader-facing frames are Camera (raw optical), Camera' (same origin,
y flipped, body kinematics), World (calibrated desk marker), Unity (basis
conversion convention before gravity alignment), and Scene (final display
coordinates after gravity alignment and floor placement). Local marker and
body frames remain: Wall, Object, MappedMarker, L24, L12/L11 and L14/L13.
Camera and World are right-handed. Camera', Unity, Scene, MappedMarker and
the body joint frames use the left-handed convention specified in the thesis.

F and S are improper orthogonal basis maps with determinant -1. G is a
proper gravity-alignment rotation operation; it does not establish another
coordinate frame. With the recording-specific t_f=(0,d,0), the mapping is
pScene = G S pWorld + t_f. The complete T(Scene,Unity) has rotation G and
translation t_f. The full T(Scene,Camera') includes the calibrated camera
origin and this floor translation. Its inverse returns Chapter 5 points to
Camera'. A common translation cancels from relative displacements; G and S
preserve Euclidean distances. Table 2.2 and Section 6.4 define this inventory.

Explicit change record: the named frame Levelled is removed, not renamed.
D-082 supersedes the parts of D-060/D-061/D-068/D-070/D-076 that issued it.
The mathematical operations and recording-specific floor distance remain.
All inventory text below is a preserved historical change record, not the
current frame system. Historical names and quoted code identifiers must not
be copied back into the thesis. See REMOVE_INTERMEDIATE_FRAME.md for the
per-section change and invariant checks.

HISTORICAL INVENTORY AND DECISION EVIDENCE, PRESERVED

Current naming refinement: D-073 uses {Camera} and {Camera'} for the frames historically called {Sensor} and {Person} below. Camera' shares the optical origin with Camera and flips only y; it is not person-centred. The remaining semantic names and every frame identity are unchanged. The historical inventory and its decisions are preserved. See CAMERA_FRAME_RENAME.md for the repository-wide scan and final notation checks.

# Thesis-wide coordinate frame inventory — semantic naming (D-058), the D-057 verification, and the {Scene} resolution (D-060)

Status 2026-09-12, fourth pass. **Nothing in the thesis, the builders, the figure
scripts, the code, DECISIONS.md, the three audit reports or
`UNITY_FRAME_RESOLUTION.md` was changed to produce it.** The only file written is
this one. No relabelling has been applied.

This pass **keeps every finding of the third pass** — the usage test, the
demotions, the frames that survived, the read-site evidence, the class-4
declarations, the code-to-thesis naming warning, the disagreements with the three
earlier audits and every substantive defect — and **folds in the two author
rulings made after that pass was written**:

- **D-058** fixes the semantic names, declares equation (4.3)'s input to be
  {Unity}, and withdraws {E0}. This closes what section 10 of the third pass
  carried as open items 1, 2, 4 and 5, and unblocks table rows **C4-08** and
  **C4-09**.
- **D-060** settles the question section 4.3 left open. **The Unity side has three
  frames, not one or two.** {Unity} is equation (6.1)'s pre-levelling display
  basis; {Levelled} is that system after the gravity levelling rotation and before
  the floor drop; **{Scene}** shares {Levelled}'s basis exactly and carries the
  origin translated by the measured floor drop, and it is where the Unity person
  log, the committed coordinate pairs and Figures 7.3 and 7.4 actually report.
  {Scene} is **entry 13** of the inventory. This unblocks **F2.4b**, **C7-04** and
  **C7-07**.

The evidence for D-060 is the read-only trace in `UNITY_FRAME_RESOLUTION.md`; it
is summarised with its numbers in section 4.3 below and is not re-derived here.

D-054's four-class policy stands unchanged and is applied throughout. The item
lists and transformation directions of the three read-only audits
(`CRAIG_NOTATION_AUDIT_ch2_ch4.md`, `_ch3_ch5.md`, `_ch6_ch8.md`, 191 items) are
reused, not re-derived.

---

## 0. TASK 1 — the D-057 verification. **VERDICT: PASSES.**

> **D-057's binding caveat:** *"Do not use the operator classification merely to
> avoid defining a frame: it is valid here only because Equation (3.22) performs
> an active 'un-swing' rotation rather than re-expressing the same vector in an
> unnamed coordinate frame."*

**Equation (3.22) is an ACTIVE rotation of a vector.** The operand is changed;
the components equation (3.23)'s two-argument arctangent then reads are
components of the **operated** vector in an **already-defined** basis — **the L12
shoulder frame, {L12}** (entry 11 of the inventory: the L24 root orientation with
its origin moved to landmark L12). D-057's premise holds and the classification
is not being used to avoid defining a frame.

Five independent pieces of evidence, from the code and from the thesis's own
prose. Any one of them would be suggestive; together they are decisive, and
**item (4) is the discriminator**, because it is the one place where the system
states both readings side by side and says which one it implements.

**(1) The code defines `f′` as the image of an active rotation applied to a
constant of {L12}.** `v1/kinematics/shoulder.py:65-68`:

```
Twist: un-swing the forearem f = R_rootᵀ(p16-p14) with R_swingᵀ, then
  f' = Rx(θτ)·(rest forearm ∝ ẑ) ⊥-part = (-sinθτ, cosθτ)·|f⊥| in (y,z)
  -> θτ = atan2(-f'y, f'z), measured in the y-z plane (the plane
  perpendicular to the rotation axis x).
```

`f′` is *defined* as `Rx(θτ)` applied to the **rest forearm**. The rest forearm
is a fixed constant of {L12} — `shoulder.py:14-17` declares the zero conventions
in {L12}'s own axes ("rest upper arm: local +x"; "zero twist: the forearm's
component perpendicular to the arm axis points along **local +z**"), and
`shoulder.py:9-11` declares the basis once for the whole module ("All vectors are
expressed in the torso basis: **the L12 shoulder frame** inherits the L24 root
orientation with its origin moved to landmark 12"). A passive change of basis
does not rotate a constant; `Rx(θτ)` here is the joint's physical twist. The
measurement plane is named as "the plane perpendicular to **the rotation axis
x**" — the *rest* arm axis, i.e. {L12}'s own +x — not the plane perpendicular to
the *current* arm direction.

**(2) The derivation reads a mapped vector against {L12}'s own basis vector.**
`v1/KINEMATIC_MODEL.md:312-314`, and verbatim in the thesis at
`build_ch3.py:426-428`:

> "with zero twist the un-swung forearm's ⊥-component is ∝ ẑ; **under Rx(θτ), ẑ ↦
> (0, −sinθτ, cosθτ)**, so (−f′y, f′z) ∝ (sinθτ, cosθτ)."

`ẑ ↦ (0, −sinθτ, cosθτ)` is an active statement: the **vector ẑ is carried to
another vector**, and the triple given is that image's components **in the same
basis ẑ itself belongs to**. Under a passive reading ẑ would have to be
re-expressed rather than mapped, and the sentence would not parse. The reference
direction against which θτ is measured is therefore **{L12}'s third basis
vector**, which is what makes {L12} the basis the arctangent's components live
in.

**(3) The forward model uses the same matrix as an operator on {L12} constants
and declares its output to be in the root basis.**
`eval/inspect/check_v1_overlay.py:47-66`, `fk_arm_dirs`, docstring at `:48`
"**Model-space (root basis) unit directions** of upper arm and forearm":

```
Rsw = _ry(ty) @ _rz(tz)
Rarm = Rsw @ _rx(tau)
upper = Rsw @ np.array([1.0, 0, 0])
fore  = Rarm @ (_ry(ey) @ _rz(ez) @ np.array([1.0, 0, 0]))
```

`R_swing` is applied to the constant rest direction `(1,0,0)` and the result is
declared a root-basis direction. `shoulder.py:79`'s `Rz(−θz)Ry(−θy)` is the exact
algebraic inverse of that construction, so it takes a root/{L12}-basis vector to
a root/{L12}-basis vector. Input and output are in one basis.

**(4) THE DISCRIMINATOR. The system names both readings and says it implements
the active one.** `v1/KINEMATIC_MODEL.md:330` (row 4 of its draft audit):

> "| 4 | (implicit) project the raw vector in the L12 frame | **un-swing first**
> (f′ = R_swingᵀ f), **or equivalently project onto the plane ⊥ current â with a
> swung reference** | twist is about the *current* arm axis; fixed coordinate
> planes are only ⊥ to it at zero swing |"

"Project onto the plane ⊥ current â **with a swung reference**" **is** the
passive/frame reading — measure the forearm against the axes of a basis that has
been swung. The document offers it as the **equivalent alternative** to what is
implemented. If `f′ = R_swingᵀ f` were itself that passive re-expression, the two
clauses would be one procedure and the word "equivalently" would be empty. They
are stated as two routes to one number, and the code takes the first.
`v1/KINEMATIC_MODEL.md:303-304` says what the first route does to the geometry:

> "Procedure (measure AFTER removing swing, so **the arm axis is back at x̂** and
> the perpendicular plane **is exactly the local y–z plane**)"

"the arm axis is back at x̂" and "is exactly the local y–z plane" assert a
coincidence between a **moved** geometric plane and a **pre-existing** frame's
coordinate plane. Under a passive reading no plane moves and the assertion is
vacuous, because every basis's y–z plane is trivially the y–z plane in its own
coordinates. It carries content only if the plane has been carried into
coincidence with {L12}'s.

**(5) The operator is reusable on a second, different vector, and its output is
decomposed against {L12}'s axes.** `v1/KINEMATIC_MODEL.md:316-318` (and
`thesis/A2_kinematic_model.md:234`):

> "because p14 − p12 ∥ â, **un-swinging w = p16 − p12 gives w′ = ‖ua‖·x̂ + f′**,
> and the projection onto y–z kills the x̂ term"

The shoulder-to-wrist vector is passed through the same operation and the result
is decomposed into **{L12}'s x̂** plus `f′`. The upper-arm part is actively
carried back onto {L12}'s +x, the rest direction. Applying one matrix to several
different vectors and decomposing the results in one fixed basis is what an
operator does.

**A sixth, structural observation, recorded because it shows the system drawing
this exact line itself.** When the implementation wants a *frame*, it builds the
swing **and** twist together, assigns it to a variable, gives it an origin and
names it: `shoulder.py:120` `R_arm = R_root @ (_ry(y) @ _rz(z) @ _rx(t))`, with
`:90-91` "**The elbow parent frame (L14)** is the fully-rotated upper-arm frame …
origin at landmark 14". The swing-only product `Ry(θy)Rz(θz)` is **never**
assigned to a frame variable, never given an origin, never composed into
`R_root`, and nothing is ever expressed in it: it appears twice in the whole
repository, at `shoulder.py:79` (inverted, on the forearm) and
`check_v1_overlay.py:57, 62` (forward, on the rest direction), and both uses are
operator uses.

**The thesis's own prose already says what D-057 requires it to say**, and needs
strengthening rather than correcting. `build_ch3.py:423`: "the procedure **undoes
the swing first, which makes that plane the local y-z plane**"; `:426-428`:
"where **f is the forearm vector in the parent frame of Section 3.3.3**. At zero
twist the perpendicular component of the forearm points along **local +z**, and
under a twist t_t **it rotates to** (−sin t_t, cos t_t) in the (y, z) plane";
`:531` "Equation (3.22) **undoes this swing on the forearm vector**". The subject
of "it rotates to" is the forearm's perpendicular component — a vector that moves
— and its destination components are given in the (y, z) plane of the
already-named parent frame of §3.3.3, which is {L12}.

**Consequences, all of which this file applies:**

- Equation (3.22) is **class 3** and carries **no frame pair**. Its Craig
  operator form is `R_Z(−t_z) R_Y(−t_y)`, with both operands labelled in the one
  frame they share: `^{L12} f′ = R_Z(−t_z) R_Y(−t_y) · ^{L12} f`.
- The candidate the corrected inventory listed as "the basis equation (3.22) maps
  into" is **resolved and is not a frame**. Section 4.8 keeps the evidence and
  records the resolution; no finding is deleted.
- Section 4.8's option (a), naming the basis, is **closed**, and the ch3/ch5
  audit's label `{E0_r}` / `{E0_l}` is **withdrawn**. **D-058 confirms the
  withdrawal**: "The E0 example given in D-056 is withdrawn: it was the earlier
  audit's label for the basis that D-057 reclassified as an operator, so no such
  frame is issued." The third pass escalated this for confirmation; it is now
  settled and is no longer an open item.
- The removal of this candidate is **independent of** the addition of {Scene}
  (section 4.3). The two are different questions about different parts of the
  system, and the inventory's total of **13 frames** already reflects both.

---

## 1. Summary

**The system has 13 coordinate frames. It already names all 13 of them itself.**
Under D-056 and D-058 each keeps the system's own name, written out; no frame is
renamed and no non-frame quantity is touched.

| | count |
|---|---|
| System-level frames, **semantic names** | 10 |
| Local kinematic / link frames, **compact landmark symbols** | 3 (5 with the left-side instances) |
| **Total real frames** | **13** (15 counting the left-side link instances) |
| Candidates **demoted** from frame to transform or operation (section 4) | 5 |
| The candidate **resolved as an operator** by D-057 and verified in section 0 | 1 |
| The one genuinely close call of the third pass, **resolved as a frame** by D-060 on the trace of `UNITY_FRAME_RESOLUTION.md` (section 4.3) | 1 — **{Scene}, entry 13** |

**The Unity side, stated once so it is never conflated again** (D-060):

| frame | basis | origin | entry |
|---|---|---|---|
| **{Unity}** | `S ·` {World} — equation (6.1); no levelling, no drop | desk-marker centre | 6 |
| **{Levelled}** | `G S ·` {World} | desk-marker centre | 7 |
| **{Scene}** | `G S ·` {World} — **the same basis as {Levelled}**, agreeing to 1.1e−16 | the drawn floor, `d` below the desk marker along levelled +y | **13** |

`^{Scene}_{Levelled} R = I₃` and `^{Scene} P_{Levelled}ORG = (0, d, 0)` with
`d = 0.716215 m` (r6b) / `0.709312 m` (r7). {Unity} and {Levelled} differ by a
proper rotation of **32.0368°**.

**All three audits independently found no wrong transformation direction anywhere
in the code, and no pass of this inventory has found any.** This remains a
notation and documentation exercise, with the substantive defects of section 9
kept strictly separate from it.

---

## 2. Where the names come from

D-056 requires the names to be the system's own. They are. The system names its
frames in four places and they agree with one another:

1. **`thesis/00_notation.md`** — the project's own notation chapter. Section 0.1
   is a five-row frame table with symbols, axes and handedness: `𝒞` camera, `𝒫`
   person space, `𝒲` world = desk-marker frame, `𝒰` Unity scene, `ℒ` levelled
   world (`thesis/00_notation.md:14-18`).
2. **Module docstrings and header comments** — `v1/aruco/frames.py:9-18`
   ("Frames: camera … world … Unity"), `v1/KINEMATIC_MODEL.md:17` ("Sensor space
   → Unity space"), `:33` ("Root frame at L24"), `v1/kinematics/shoulder.py:10-11`
   ("the L12 shoulder frame"), `:90` ("The elbow parent frame (L14)"),
   `v1/aruco/calibrate_scene.py:9` ("The desk marker's own frame is the WORLD
   frame"), `eval/offset/carry.py:54-56` ("the leveled desk world").
3. **Unity source comments** — `Unity/Assets/Scripts/ArucoSceneReceiver.cs:12`
   ("mapped marker frame: x = right, normal = up, y = forward"), `:114` ("a pose
   node in ArucoWorld-local coordinates"), `:224-225` and `:235` ("Mapped camera
   frame: optical axis = local up, image-down = local forward").
4. **The thesis itself** — §2.2.1 and Table 2.2 give C, W, O, P, U; the landmark
   vocabulary L11…L24 is printed **53 times** across Chapters 2, 3, 5 and the
   appendices, including Figure 3.3's caption (`build_ch3.py:217`), "the root at
   the right hip **L24**, the shoulder at **L12** and the elbow at **L14**".

### 2.1 The names chosen, and where each comes from

Shortest unambiguous form of the system's own name, as D-056 requires. Nothing
below is an invented word.

| # | Name | Source of the name | Shorter or alternative form, and why it was not taken |
|---|---|---|---|
| 1 | **{Sensor}** | `eval/unity_check/check_unity_log.py:147` "person space -> **sensor frame** -> pixels"; `v1/KINEMATIC_MODEL.md:17` "**Sensor space**"; `v1/kinematics/root_frame.py:9,12` `SENSOR_TO_UNITY`, `unity_from_sensor`; D-056 lists "Sensor" first | **{Camera}** is equally the system's word (`frames.py:10-11`; the thesis's "camera frame C") and equally short, but it sits one word from **{MappedCamera}** (frame 9) and from the Unity POV camera node (`ArucoSceneReceiver.cs:241-242`). {Sensor} is the name the system reaches for precisely when it must distinguish this frame from other camera-like things. **CONFIRMED by D-058**, which names the frame Sensor rather than Camera on exactly this ground; §10.1 records the closure |
| 2 | **{Person}** | `thesis/00_notation.md:15`; thesis §2.2.1 "person space P"; `v2/common/object_link.py:23,84` | — |
| 3 | **{World}** | `v1/aruco/calibrate_scene.py:9` "The desk marker's own frame is the **WORLD** frame"; `frames.py:12-15, 34`; `thesis/00_notation.md:16` | — |
| 4 | **{Wall}** | `frames.py:27`; `calibrate_scene.py:133, 301`; thesis §2.2.1 in words ("wall marker frame") | The full "{WallMarker}" is unnecessary: there is exactly one wall marker |
| 5 | **{Object}** | `frames.py:29, 33`; thesis §2.2.1 "object frame O" | — |
| 6 | **{Unity}** | thesis §2.2.1, Figure 2.4(b), Table 2.2 row 9; `thesis/00_notation.md:17` `𝒰`; `frames.py:16-18, 38-40` `WORLD_TO_UNITY`; `ArucoSceneReceiver.cs:114` "ArucoWorld-local coordinates" | D-056 also offers "{Display}"; see the two-names note in §2.2 |
| 7 | **{Levelled}** | `thesis/00_notation.md:18` `ℒ`; `eval/offset/carry.py:54-56` "the **leveled desk world**"; `eval/gt/eval_rail_scenario.py:51-58` "the **GRAVITY-LEVELLED desk world**"; `evaluate_ch7_object.py:514`; `evaluate_ch7_spatial_check.py:338` | D-056's own example spells it **{LevelledWorld}**. {Levelled} is its shortest unambiguous form and is 8 characters against 13 in every left superscript. **CONFIRMED by D-058**, which fixes the name as Levelled on exactly this ground; §10.1 records the closure |
| 8 | **{MappedMarker}** | `ArucoSceneReceiver.cs:12` "**mapped marker frame**: x = right, normal = up, y = forward"; `:13`, `:114`, `:131` | Instantiated per marker by the same family rule as §2.4; **every printed instance is the object marker's**, so no per-instance label is issued |
| 9 | **{MappedCamera}** | `ArucoSceneReceiver.cs:224-225` and `:235` "**Mapped camera frame**: optical axis = local up, image-down = local forward" | — |
| 10 | **{L24}** | `v1/kinematics/root_frame.py:22` "**L24 root frame**"; `shoulder.py:55` "R_root: **L24 root frame**"; `v1/KINEMATIC_MODEL.md:13, 33`; thesis Figure 3.3 caption | see §2.3 |
| 11 | **{L12}**, **{L11}** | `shoulder.py:10-11` "the **L12** shoulder frame"; `KINEMATIC_MODEL.md:238-243`; thesis Figure 3.3 caption | see §2.3 |
| 12 | **{L14}**, **{L13}** | `shoulder.py:90-91` "The elbow parent frame (**L14**)"; `KINEMATIC_MODEL.md:376, 383-384`; thesis Figure 3.3 caption | see §2.3 |
| 13 | **{Scene}** *(belongs logically beside {Levelled}, row 7; numbered 13 so that every "entry N" reference elsewhere in this file keeps its referent)* | `ArucoSceneReceiver.cs:308` "Drop the whole reconstruction so the floor sits at **scene y = 0**"; `:209-210` "the depth-fit gravity direction becomes **scene up**"; `IntegratedSceneReceiver.cs:24` "turns person-space coordinates into **scene coordinates** directly"; `:238` "body axes = **scene axes**"; `check_unity_log.py:148` "**Unity scene world** -> person space -> sensor frame -> pixels"; the thesis itself at `build_ch6.py:475`, Table 6.2, "(0.0, 74.8, 43.8) cm **in the scene**" | The ch6/ch8 audit's provisional `{S}` is **not** issued: `S` is the swap matrix (20 printed occurrences) and D-056 replaced letters with names. **{UnityScene}** and **{Drawn}** are the other forms the system's vocabulary supports; **D-060 fixes {Scene}** and rules explicitly that it is **not** to be renamed to avoid the visual adjacency with {Sensor}, because the full semantic labels are unambiguous |

### 2.2 Where the system uses two names for one frame — stated explicitly

D-056's requirement is semantic clarity. Six frames carry more than one name in
the sources, and a reader who moves between the thesis and the code will be
misled unless the thesis says so once. Each of these belongs in the frame table's
"also called" cell, not in a footnote.

- **{Sensor}** is also **the camera frame** (the thesis's 45 printed `C`s), the
  **RealSense colour optical frame**, **sensor space** (`KINEMATIC_MODEL.md:17`)
  and **camera space** (`object_link.py:84`). One frame, four names.
- **{Person}** is also **Unity space** in v1 (`KINEMATIC_MODEL.md:17, 35`;
  `shoulder.py:54`; `IntegratedSceneReceiver.cs:13` "Pipeline-A Unity space =
  camera frame, y flipped") and **solver space** in v2 and eval
  (`object_link.py:23, 84`). **"Unity space" in the v1 code is {Person}, not
  {Unity}.** This is the single most dangerous name in the system and the thesis
  must state it once, in the frame table.
- **{Unity}** is also **the display axes** — the thesis's own phrase, printed ten
  times in Chapter 6 — and **ArucoWorld-local coordinates**
  (`ArucoSceneReceiver.cs:114`). D-056 offers "{Display}" as an alternative label
  for exactly this reason. **{Unity} is adopted** because the thesis prints the
  Unity frame 14 times and `00_notation.md:17` already carries `𝒰`, with "display
  axes" recorded as the same frame. **D-060 settles what §4.3 left open:**
  {Unity} is the display axes of equation (6.1) and nothing more — it is *not*
  Unity's scene root, which is entry 13, {Scene}.
- **{Levelled}** is also **the leveled desk world**, the **gravity-levelled desk
  world** and `ℒ`.
- **{Scene}** is also **Unity's scene root**, **Unity scene world**
  (`check_unity_log.py:148`), **scene coordinates** / **scene axes**
  (`IntegratedSceneReceiver.cs:24, 238`), **the scene** (Table 6.2,
  `build_ch6.py:475`) and, informally and dangerously, **"Unity"** — the axis
  labels of Figures 7.3 and 7.4 say `Unity x (cm)`, `Unity z (cm)`, `Unity y (cm)`
  (`make_ch7_valid_joint_figures.py:37-39`) while plotting {Scene} components.
  **This is the second most dangerous name in the system**, after "Unity space"
  for {Person}, and the thesis must state it once in the frame table: the word
  "Unity" on those axes means **{Scene}**, not equation (6.1)'s {Unity}.
- **{L14}** is addressed by **three** names in Chapter 3 alone — the subscripts
  "el,r" (relative to {L12}) and "arm,r" (relative to {Person}), plus "the
  fully-rotated upper-arm frame" in the code. The Craig rewrite collapses all
  three into `^{L12}_{L14} T` and `^{Person}_{L14} T`, which is audit item C3-11
  and C3-13's fix.

### 2.3 The link-frame symbols — decision and justification

**Decision: the landmark names are used directly as the compact symbols —
{L24}, {L12}, {L11}, {L14}, {L13}.** No per-link symbol is invented.

D-056 allows "compact approved symbols such as {E0}, {E1}, {B}" for local
kinematic and link frames, and the brief asks whether to use the landmark names
directly or a short symbol per link. Seven reasons decide it for the landmark
names:

1. **They are the system's own names**, in exactly the form D-056's first clause
   demands: `root_frame.py:22` "L24 root frame", `shoulder.py:10-11` "the L12
   shoulder frame", `shoulder.py:90` "The elbow parent frame (L14)",
   `KINEMATIC_MODEL.md:13, 33`. `{B}`, `{S_r}`, `{E_r}` are the ch3/ch5 audit's
   inventions; the system uses none of them.
2. **The thesis already prints them 53 times**, including Figure 3.3's caption,
   which names the whole chain in landmark vocabulary: "the root at the right hip
   L24, the shoulder at L12 and the elbow at L14" (`build_ch3.py:217`). The frame
   table therefore lands on vocabulary the reader has already been given, and
   Figure 3.3 becomes the picture of the chain contract at no cost.
3. **They are as compact as the alternatives** — three characters, the same as
   `{E0}`, shorter than any semantic spelling of "shoulder".
4. **They carry the side for free.** {L12}/{L11} and {L14}/{L13} are right/left
   by construction, which retires the "r"/"l" subscripts and settles the ch2/ch4
   audit's complaint that the thesis's `T_sh`, `T_el` never distinguish the sides.
5. **They introduce no new symbol at all**, which is the strongest possible
   compliance with D-056's "keep existing uses of L for segment lengths, landmark
   identifiers, and other quantities unchanged": nothing is renamed; a name the
   thesis already prints is promoted into the frame slot of a Craig symbol.
6. **Every short single letter is already taken.** `S` is the swap matrix (20
   printed occurrences), `B` and `E` are invented, `R` is a rotation, `L` is the
   most heavily loaded letter in the thesis.
7. **The chain contract becomes self-documenting**: `^{Person}_{L24} T
   ^{L24}_{L12} T ^{L12}_{L14} T = ^{Person}_{L14} T` names the landmarks the
   transform is built from, which is exactly how §3.3 constructs it
   (`build_ch3.py:327, 337`).

**The one cost, recorded rather than resolved.** Chapter 5 prints the calibrated
segment lengths `L_1` and `L_2` 29 times, and the landmark names appear in the
same chapter; the two differ by one character. This is a **pre-existing**
adjacency that the corrected inventory already flagged, not one this choice
creates, and D-056 forbids renaming the lengths. The mitigation is positional and
needs no edit to either: a frame label only ever appears in the
superscript/subscript **frame slot** of a Craig symbol (`^{L24}`, `_{L12}`),
while the lengths only ever appear as bare multiplicands (`L_2 f̂`). The frame
table should say so in one sentence.

### 2.4 One naming rule the system already has, that removes an invented label

`v1/aruco/extract_aruco_poses.py:64-72` defines *the marker's own frame* once:

```
"""Corner order must match cv2.aruco detections (TL, TR, BR, BL in the
marker's own frame: x right, y up, z out of the plane toward the viewer)"""
```

— and the thesis states the same in Appendix E.2 ("The printed marker gives the
same four corners **in its own frame**, at plus and minus half the printed side
length L in the marker plane where the third coordinate is zero"). That is a
**family rule**, not a frame. Its three instances are already named: **{World}**
(the desk marker's, `calibrate_scene.py:9`), **{Wall}** and **{Object}**. No
generic marker frame is needed; the appendix's "its own frame" should simply be
stated as the rule that generates the three. The same rule generates
{MappedMarker}'s instances inside Unity.

### 2.5 Code names that must never be used to infer a frame

Recorded once so a later pass does not trip on them. These are naming collisions
**inside the code**, first flagged by the ch2/ch4 audit (S4). **Retained in
substance from the corrected inventory; D-056 does not touch it, because it is
about the code's names, not the thesis's.**

- `v1/kinematics/root_frame.py:9,12` calls the sensor→person-space flip
  `SENSOR_TO_UNITY` / `unity_from_sensor`, and `:24` says the root columns are
  the person's axes "in Unity world". Its destination is **{Person}**, not
  {Unity}.
- `v1/KINEMATIC_MODEL.md:17,35` and `v1/kinematics/shoulder.py:54` call {Person}
  "**Unity space**"; `IntegratedSceneReceiver.cs:13` says "Pipeline-A Unity space
  = camera frame, y flipped".
- `eval/offset/carry.py:24` names the world→Unity swap `P`, and `:25` names the
  sensor→person flip `D`. **The code's `P` is the thesis's `S`, and the code's
  `D` is the thesis's `F`** (`check_unity_log.py:88-89` likewise). Any
  cross-reference from the thesis to the code must say this once.
- `eval/offset/carry.py:61` `cam_pos = P @ T_dc[:3,3]` is in **{Unity}** axes
  despite the name.

---

## 3. The inventory

Handedness: R = right-handed, L = left-handed. "Printed today" is what the **v8
thesis** prints now; the Name column is what D-056 puts in its place.

| # | Name | Also called | Printed today | Origin | Axes | Handed | Parent | Fixed / time-varying | First in the thesis | What uses it |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **{Sensor}** | camera frame, RealSense colour optical frame, sensor space, camera space | **C** (45 occurrences) | colour camera optical centre | x image right, y down, z forward | R | — | fixed | §2.2.1, Figure 2.4(a) | every raw measurement; eq (3.1); Appendices C, D, E |
| 2 | **{Person}** | *Unity space* in v1, *solver space* in v2/eval | **P** (17) | shared with {Sensor} | x right, y up, z forward | L | {Sensor} via **F** | fixed | §2.2.1, §3.1 | all of Chapters 3 and 5; the PersonAnchor node's local system (`IntegratedSceneReceiver.cs:159-163, 378`) |
| 3 | **{World}** | the desk marker's own frame | **W** (34) | desk marker centre | x, y in the printed plane, z out of the printed face | R | {Sensor} via calibration | fixed | §2.2.1 | eqs (4.1), (4.2); Table 2.2; Chapter 6 |
| 4 | **{Wall}** | wall marker frame | *(none — subscript "wall")* | wall marker centre | the marker's own frame (§2.4 rule) | R | {Sensor} | fixed | §2.2.1; Table 2.2 row 2 | gravity: `calibrate_scene.py:148` takes **column 2** of `T_desk_wall` |
| 5 | **{Object}** | object marker frame | **O** | ArUco translation origin = geometric centre of the printed square (D-053) | the marker's own frame (§2.4 rule) | R | {Sensor} per frame | time-varying | §2.2.1 | eq (4.1); Table 5.1; Appendix E |
| 6 | **{Unity}** | *display axes* (×10 in Ch 6), ArucoWorld-local coordinates | **U** (14) | desk marker centre | {World} with the 2nd and 3rd coordinates exchanged; y up | L | {World} via **S** | fixed | §2.2.1, Fig 2.4(b); eq (6.1) | eq (6.1); every streamed record; the ArucoWorld node's local system |
| 7 | **{Levelled}** | leveled desk world, gravity-levelled desk world, `ℒ` | printed as **W** in Ch 5 (3 lettered, 3 unlettered) | desk marker centre (no floor drop) | {Unity} rotated so calibrated gravity is +y | L | {Unity} via **G** | fixed | §5.3 | Chapter 5 `o`, `R_obj`; Chapter 7 §7.2, §7.3.3, Figures 7.1, 7.2 |
| 8 | **{MappedMarker}** (instantiated per marker; every printed instance is the object's) | mapped marker frame | *(none)* | marker centre | marker plane = local x/z, **normal = local up**, y = forward | L | {Unity} | fixed or time-varying per marker | never named | `carry.py:83` cube centre; `carry.py:117` / `recovery_core.py:111` the grip offset `h`; the Unity object node |
| 9 | **{MappedCamera}** | mapped camera frame | *(none)* | camera optical centre | optical axis = local up, image-down = local forward | L | {Unity} | fixed | never named | eq (6.3)'s first factor `S R_cam S`; the Unity sensor node |
| 10 | **{L24}** | the root frame, the torso frame, the L24 root frame | *(none — subscript "root")* | landmark L24, the right hip | x subject's right along the hip line, y up the trunk, z out of the chest | L | {Person} | time-varying | §2.2.1 in words; eq (3.5) | eqs (3.5), (3.11)-(3.14), (3.18); the left-arm mirror |
| 11 | **{L12}** (right), **{L11}** (left) | the L12 shoulder frame | *(none — subscript "sh,r"/"sh,l")* | landmark L12 / L11 | inherits {L24}'s orientation | L | {L24} | time-varying | eqs (3.5), (3.13) | eqs (3.13), (3.19)-(3.23); `shoulder.py:70, 78, 79-82` |
| 12 | **{L14}** (right), **{L13}** (left) | the elbow parent frame, the fully-rotated upper-arm frame | *(none — two subscripts, "el,r" and "arm,r")* | landmark L14 / L13 | {L24}'s basis turned by the solved shoulder rotation | L | {L12} / {L11} | time-varying | eqs (3.5), (3.14) | eqs (3.14), (3.24); `shoulder.py:120-123` |
| 13 | **{Scene}** | Unity's scene root, Unity scene world, scene coordinates / scene axes, "the scene", and — misleadingly — "Unity" on the axes of Figures 7.3/7.4 | *(none; the thesis says "in the scene" once, at `build_ch6.py:475`, and "Unity x/y/z" on two figures)* | **the drawn floor**: `d` below the desk-marker centre along {Levelled}'s +y, where `d = origin_above_tabletop_m + DeskThick + LegH` = **0.716215 m** (r6b) / 0.709312 m (r7) | **exactly {Levelled}'s axes** — x, z in the levelled horizontal plane, y up along calibrated gravity | L | **{Levelled}**, by a pure translation: `^{Scene}_{Levelled} R = I₃`, `^{Scene} P_{Levelled}ORG = (0, d, 0)` | fixed within a recording; `d` is a **recording-dependent** presentational constant, which is why the *origin* is not a measurement even though the frame is real | the picture is Figure 2.4(b) (whose caption misnames it — §4.3, §8.1); the first **printed coordinate** is §6.5, `build_ch6.py:434`, and Table 6.2, `:475` | the seven joint triples of `unity_person_log.csv` (`IntegratedSceneReceiver.cs:395-403`); both column families of `audit_evidence/ch7_restructured/human_pairs.csv` (`evaluate_ch7_restructured.py:133`, `:136-139`); **Figures 7.3 and 7.4** (`make_ch7_valid_joint_figures.py:25, 28-29, 37-39`); equation (7.5); §6.5's `p_scene`; Table 6.2's second triple |

**On the thirteenth row.** Two different candidates have competed for it across
the passes, and they must not be confused. The candidate that stood here in the
corrected inventory — "the basis equation (3.22) maps into" — is **resolved by
D-057 and is not a frame**; the evidence and the resolution are in section 4.8,
and the verification is in section 0. The thirteenth row is instead **{Scene}**,
added by **D-060** on the trace in `UNITY_FRAME_RESOLUTION.md`, which closes what
section 4.3 carried as the one genuinely close call. **D-058 withdraws {E0}**, so
no link-frame symbol of that shape is issued anywhere in this file.

### 3.1 Notes on four entries

**Frame 8, {MappedMarker}, is the one entry a reader may doubt, so its read sites
are given in full.** It is not an artefact of describing a conjugation; positions
are expressed in it, inside Unity and outside it:

- `ArucoSceneReceiver.cs:131-132` states the axes ("marker plane = local x/z,
  normal = local up"), and `:137-138` builds the plate at local offset
  `Vector3.up * 0.002f` with extents `(sizeM, 0.003f, sizeM)`: thin along local
  **y** (the marker normal), square in local **x/z** (the marker plane).
- `ArucoSceneReceiver.cs:253-254` — the object cube's centre is placed at
  `Vector3.down * (cubeSize / 2f)`, i.e. `(0, −cube/2, 0)` in the node's local
  axes, "half an edge behind the marker along its normal" (`:24-25`).
- `eval/offset/carry.py:83` — **the same vector, outside Unity**:
  `box_center = obj + R_obj @ np.array([0.0, -self.cube / 2.0, 0.0])`.
- `eval/offset/carry.py:117` — `d_loc = np.einsum("nij,ni->nj", R_obj, wr - obj)`
  = `R_objᵀ(wr − o)`, which is **Chapter 5's `h`**. Same at
  `eval/failure/recovery_core.py:111`.

Since `R_obj = G · S · (^{World}_{Object} R) · S` (`carry.py:79` composed with
`frames.py:85-88`; verified entry-by-entry by the ch3/ch5 audit at C5-03), the
columns of `R_obj` are the **mapped** object axes. **Chapter 5's `h` is therefore
expressed in {MappedMarker}, not in {Object}.** Table 5.1 currently declares `h`
in "object frame O", which is right-handed with the normal on +z; {MappedMarker}
is left-handed with the normal on +y. This is a **substantive defect**, listed in
section 9, and it is the reason D-054 requires the re-based body frame to be
named: without frame 8 there is no legal way to write equations (5.1)-(5.3).

**Frame 9, {MappedCamera}.** Read sites: `ArucoSceneReceiver.cs:229-231` places
the sensor lens at local `(0.018, 0.0125, 0)`, and `:241-242` parents the POV
camera to the sensor node with
`localRotation = Quaternion.LookRotation(Vector3.up, -Vector3.forward)` — an
orientation expressed in the node's local axes, and exactly the axis convention
the comment at `:235` states. This is the frame `S R_cam S` maps out of, so it is
what makes equation (6.3)'s factorisation Craig-legal.

**Frame 4, {Wall}, appears in exactly two places** — the printed symbol
`T_C,wall` (Table 2.2 row 2) and the unprinted gravity column extraction at
`calibrate_scene.py:148`. Under D-056 it gets its name rather than a letter,
which removes the ch2/ch4 audit's `{Wl}` proposal and the question of whether it
needed a letter at all.

**Frame 13, {Scene}, is the entry added by D-060, and the one a reader is most
likely to want to collapse into {Levelled}, so its separation is given here in one
place.** The two **share a basis exactly** — on a shared 900-frame object track a
translation-free test gives `max |d_scene − d_levelled| = 1.1e−16` — and differ
**only in origin**, by a translation that is constant over every frame with **zero
spread**: `(0, 0.716215, 0)` m on the rail recording. What keeps them apart is the
inventory's own usage test, which {Scene} passes **on its origin**, at four sites:
`IntegratedSceneReceiver.cs:395-403` (seven joint triples per frame, logged as
global `Transform.position` reads), `evaluate_ch7_restructured.py:133, 139` (both
column families of `human_pairs.csv`), `make_ch7_valid_joint_figures.py:25, 28-29,
37-39` (Figures 7.3 and 7.4, plotted axis by axis and labelled), and
`build_ch6.py:434, 475` (§6.5's `p_scene` and **Table 6.2, which prints one
physical point in both frames under both names**). The consequence to carry into
every caption: because the axes are identical, **every distance, every scatter
shape, every direction and every line tilt agrees between {Levelled} and {Scene}**,
and only absolute components differ. `^{Scene}_{Levelled} R = I₃` is therefore not
a formality — it is the statement that makes Chapter 7's two figure pairs
comparable. The separating transform from equation (6.1) is
`^{Scene} P = G · ^{Unity} P + (0, d, 0)`, with `G` a proper rotation of
**32.0368°** (`det +1`, orthogonality error `2.2e−16`), recovered blind from the
logged data to `1.2e−5`. Full evidence at §4.3; the trace is
`UNITY_FRAME_RESOLUTION.md`.

---

## 4. What is a frame and what is a transform — the demotions (4.1, 4.2, 4.6, 4.7), the frames that passed (4.3, 4.4, 4.5), and the resolved operator (4.8)

**Every finding in this section is carried over unchanged.** The test applied
throughout is **usage, not motion**: *is there a site in the implementation or the
thesis where a position or an orientation is expressed in this system?* A write
site (something being rotated or translated) is not evidence. A read site — a
component read, a local coordinate assigned, a corner list, an axis label on a
plotted coordinate — is. Absence of a read site is reported explicitly.

Eight candidates were tested. **Four fail and are demoted** (4.1, 4.2, 4.6, 4.7,
and the PersonAnchor node in 4.4); **three pass** and are kept under the system's
own names (4.3, 4.4, 4.5). Section 4.8 records the eighth, resolved by D-057 as
an operator rather than a frame. **Section 4.3 is the one that changed**: the
third pass reported it as an unresolved close call, and D-060 has now resolved it
**as a frame**, {Scene}, on evidence that did not exist when the third pass was
written.

### 4.1 The gravity levelling carried by the ArucoWorld parent node — NOT a frame

- **Write site.** `Unity/Assets/Scripts/ArucoSceneReceiver.cs:206`
  `world = new GameObject("ArucoWorld").transform;` and `:212`
  `world.rotation = Quaternion.FromToRotation(gravityUpLocal, Vector3.up);`
- **The code states its own status at `:208-211`:** *"Level the reconstruction:
  rotate the parent so the depth-fit gravity direction becomes scene up. Poses
  are applied as LOCAL pose, so **the parent transform is purely
  presentational**."*
- **Read sites for the node's local coordinate system:** `:114` ("A pose node in
  **ArucoWorld-local coordinates** (mapped marker frame)"), `:119-120`
  (`t.localPosition = pos; t.localRotation = Quaternion.Euler(euler)`),
  `:389-390` (the streamed object pose), `IntegratedSceneReceiver.cs:161-163`
  (the PersonAnchor's local pose). **Every one of these expresses a pose in
  {Unity}** — the values arrive from `frames.unity_from_world`
  (`frames.py:85-88`), which is eq (6.1).
- **Verdict.** The node's local coordinate system **is {Unity}, a frame that
  already exists and already has a name**. Rotating the node changes the node's
  pose relative to Unity's scene root; it creates nothing beneath it. There is
  **no read site in any new system introduced by this rotation**. Record the
  levelling as a **class-1 proper rotation between two named frames**
  (`^{Levelled}_{Unity} R = G`) wherever the thesis prints it — it is `G` in the
  code (`carry.py:64`) and `L` in Chapter 6's worked example — never as a new
  frame.
- The thesis already says this correctly, twice: §6.2's closing sentence ("both
  branches inherit the levelled frame **as local poses beneath one parent**, so
  nothing rewrites the data") and §6.4 ("It rotates that node … Every streamed
  pose is applied beneath it **as a local pose**").

### 4.2 The floor drop and the scene offset — the TRANSLATION is not a frame (with the D-060 correction at the end of this section)

- **Write sites.** `ArucoSceneReceiver.cs:213` `world.position = WorldOffset();`
  with `:315` `protected virtual Vector3 WorldOffset() { return new Vector3(2.5f, 0f, 0f); }`;
  and `:308-310` *"Drop the whole reconstruction so the floor sits at scene
  y = 0"*, `float floorY = world.TransformPoint(...).y; world.position += Vector3.down * floorY;`
- **These are translations of the same node**, so the read sites are those of 4.1
  and they are all in {Unity}. **No position or orientation is expressed in any
  new system introduced by the drop.**
- **Positive evidence that the placement is presentational, not measured.** The
  lateral component is 2.5 m in the standalone receiver and **zero** in the
  integrated one (`IntegratedSceneReceiver.cs:126`
  `protected override Vector3 WorldOffset() { return Vector3.zero; }`). A
  quantity that changes with which receiver is running is not a measurement
  frame.
- **Where it does appear downstream, it cancels.**
  `evaluate_ch7_restructured.py:114` builds `offset`; `:118` adds it to
  `expected_hip` and `:133` adds it to `measured`; `:137` reports
  `error = np.linalg.norm(rig - measured)`, in which the common `offset` cancels
  exactly. Same at `check_unity_log.py:106, 138-139`. **No reported number in the
  thesis depends on the drop.**
- **Verdict: the drop is a transform, not a frame.** *A translation cannot create
  a basis, and this section's argument on that point stands unchanged.*
- **CORRECTION required by D-060, recorded here so §4.2 is never read against
  §4.3.** Two claims above are narrower than they were written.
  - *"No position or orientation is expressed in any new system introduced by the
    drop"* is **false of the origin**. Positions are read absolutely, component by
    component, at four sites — `IntegratedSceneReceiver.cs:395-403`,
    `evaluate_ch7_restructured.py:133, 139`,
    `make_ch7_valid_joint_figures.py:25, 28-29, 37-39`, and `build_ch6.py:434,
    475` — and those reads carry the drop. A frame is a **basis and an origin**;
    the drop supplies the origin of {Scene}, which is entry 13.
  - *"No reported number in the thesis depends on the drop"* is true of every
    reported **error and distance** — the common `offset` cancels at
    `evaluate_ch7_restructured.py:137` and `:141` exactly as this section shows —
    and **false of the plotted and printed coordinates**. Figure 7.3's vertical
    axis reads 78–97 cm because of the drop and would read 6–16 cm without it;
    §6.5 and Table 6.2 print one triple that carries it. D-059's own
    reversibility clause was corrected on the same ground.
  - The two facts that *are* unchanged, and that still matter: the lateral offset
    is receiver-dependent (2.5 m standalone, zero integrated) and the drop is
    recording-dependent (0.716215 m against 0.709312 m). **This makes {Scene}'s
    origin presentational without making {Scene} unreal** — the thesis reports in
    it, so it must be named and its transform printed. That is exactly what D-060
    directs, and D-060 also forbids changing the printed values of Figures 7.3 and
    7.4 in order to remove the frame.

### 4.3 The far side of that node — Unity's own scene root. **RESOLVED by D-060: it IS a frame, and it is {Scene}, entry 13**

The node argument disposes of 4.1 and 4.2 *beneath* the node. It does not say
what lies *above* it. Unity's scene root is not created by the ArucoWorld
transform; it pre-exists it. **The third pass reported this as the one genuinely
close call and escalated it rather than deciding it. D-059 commissioned a
code-and-data trace; `UNITY_FRAME_RESOLUTION.md` produced it; D-060 decided it.
The open framing below is replaced by the resolution.**

#### 4.3.1 The verdict

**The Unity side contains three frames, not one and not two.** A coordinate frame
is a **basis and an origin**. The Unity side has **two bases** and **three
(origin, basis) pairs**:

| frame | basis | origin | status |
|---|---|---|---|
| **{Unity}** | `S ·` {World} — equation (6.1), left-handed, y up. No levelling, no drop | desk-marker centre | entry 6, unchanged |
| **{Levelled}** | `G S ·` {World} | desk-marker centre | entry 7, unchanged |
| **{Scene}** | `G S ·` {World} — **identical to {Levelled}'s** | the drawn floor, `d` below the desk marker along levelled +y | **entry 13, added by D-060** |

**Figure 2.4(b) draws the third and labels it with the first.** That is the whole
defect, and it is a caption defect, not a figure defect (§4.3.4).

#### 4.3.2 The evidence, in the terms the author's decision rule set

The rule had two branches. The trace ran the operative test — **the basis, not the
origin** — on **difference vectors**, which annihilate every translation and every
origin and therefore cannot be confounded by the floor drop.

- **Branch 1 does not apply.** The rig-side read sites do **not** numerically use
  equation (6.1)'s basis. On consecutive-frame displacements larger than 1 mm:
  `max |d_rig − d_U| = 0.107750 m` (r6b, n = 145) and `0.054265 m` (r7, n = 263),
  against `max |d_rig − G d_U| = 0.000002 m` in both. Lengths are preserved to
  **2 µm** while directions differ by a median of **28.6°** / **31.1°** — an
  isometry that is not the identity, i.e. a **rotation**, not a translation.
- **The map was recovered blind.** Discarding every prior, a least-squares fit of
  the basis map from the two logged coordinate sets alone returned
  **32.0363°** (r6b) and **32.0394°** (r7), matching the levelling rotation `G` to
  `1.2e−5` / `4.3e−5`. `det G = +1.000000`, orthogonality error `2.2e−16`.
- **Branch 2 therefore applies**, and the separating transform is
  `^{Scene} P = G · ^{Unity} P + (0, d, 0)`, built by two lines on one Unity node:
  `ArucoSceneReceiver.cs:212` (`world.rotation = Quaternion.FromToRotation(gravityUpLocal, Vector3.up)`)
  and `:213` with `:308-310` (`world.position += Vector3.down * floorY`).
- **The second basis is not new.** It is **{Levelled}'s**, which this inventory
  already carries as entry 7. On a shared 900-frame object track the two agree to
  `max |d_scene − d_levelled| = 1.1e−16` and differ by a constant
  `(0, 0.716215, 0)` m with **zero spread over all frames**. The trap the author
  flagged — two systems sharing a basis and differing only in origin — occurs
  here, between {Levelled} and {Scene}, and not between the pair the rule names.
- **The pipeline asserts the relation itself.**
  `evaluate_ch7_restructured.py:119-120` asserts
  `xyz(log,'hip') == (G @ (M @ pel + cp)) + offset` to 1e−3 m, and
  `check_unity_log.py:147-149` writes the inverse, undoing **`G.T` (a rotation)**
  and `world_pos` (a translation) to leave the rig-side frame. If the rig-side
  basis were equation (6.1)'s, `G.T` would not be there.

#### 4.3.3 Why {Scene} passes this section's own usage test

The test is **usage, not motion**: is there a site where a position or an
orientation is *expressed* in this system, component by component? {Scene} passes
on its **origin**, at four independent sites, three of them printed in the thesis:

- `IntegratedSceneReceiver.cs:395-403` — seven joint triples per frame, written as
  `Transform.position` reads, which is Unity's **world-space** property. The rig
  is never parented (`:180` `rigRoot = hip.root;`; the file's only `SetParent` is
  `:160`, the **anchor**) and no bone is ever read with a local position or
  rotation, so these are global by construction. *The non-parenting is the
  mechanism by which the read is global; it is not the argument that a second
  basis exists. That argument is §4.3.2 alone.*
- `evaluate_ch7_restructured.py:139` — `human_pairs.csv`'s `rig_*` columns are
  those log values copied verbatim (verified bit-identical, max difference
  **0.0 m**), and `:136-138` puts `measured_*` in the same frame by applying `G`
  and `offset`.
- `make_ch7_valid_joint_figures.py:25, 28-29, 37-39` — **Figures 7.3 and 7.4**
  plot those columns with only a metre-to-centimetre scale, axis by axis, and
  label them. The plotted numbers carry the drop: Figure 7.3's right-wrist
  vertical range is 77.96–96.58 cm and would be 6.34–15.86 cm without it.
- `build_ch6.py:434`, `:435`, `:475` — §6.5 prints
  `p_scene = L p_U + (0, 0.72, 0) = (0.00, 0.75, 0.44) m`, and **Table 6.2 prints
  one physical point in two frames under two different names**: "pelvis
  (0.2, −20.5, 38.9) cm **in display axes**; (0.0, 74.8, 43.8) cm **in the
  scene**". *The thesis already needs two names here, and already uses them.*

#### 4.3.4 What this unblocks, and what it narrows

- **F2.4b** — the frame is **{Scene}**. The figure is an accurate picture of it;
  only the caption is wrong, in four ways. §8.1 carries the corrected wording,
  **proposed, not applied**.
- **C7-04** — Figures 7.3/7.4 report in **{Scene}**; Figures 7.1/7.2 and §§7.2,
  7.3.3 report in **{Levelled}**.
- **C7-07** — equation (7.5)'s two operands are both **{Scene}**, verified at
  `evaluate_ch7_restructured.py:133` and `:139`, which add the identical `offset`
  before `:141` differences them. Equation (7.6) is a separate matter and is
  traced at §8.6.
- **X-4 is narrowed, and the narrowing must be carried into the fix.** The ch6/ch8
  audit recorded that Figures 7.1/7.2 and Figures 7.3/7.4 "differ by the levelling
  **and** the placement". **They differ by the placement only.** {Levelled} and
  {Scene} share a basis to 1.1e−16, so between those two figure pairs **the
  scatter shapes, the directions, the line tilts and every distance are
  identical**, and only the absolute components differ, by the constant
  `(0, 0.716215, 0)` m. The defect is therefore narrower than X-4 recorded: the
  fix is to **name both frames and state that they share axes**, not to warn that
  the two pictures are differently oriented. *(The separate half of X-4 — §7.3's
  `det −1` map called a rotation and its false frame-identity claim — is
  untouched by this and remains substantive: §9, S-5.)*
- **X-3 is confirmed by the same evidence**, and becomes a labelling statement
  rather than an open question: `IntegratedSceneReceiver.cs:357` `qA = anchor.rotation`
  is a **global** rotation and the anchor is parented to the levelling node
  (`:160`), so `anchor.rotation = G · A`. Equation (6.5) as printed is
  `^{Unity}`-relative; the rotation actually written to the bone is
  `^{Scene}`-relative. It stays a **substantive defect** (§9, S-4) because the
  missing factor is content, not a label.

#### 4.3.5 The two alternatives the author considered, and why they were not taken

Recorded because they were live and may be revisited.

- **Two frames, with the drop as a stated presentational offset** at the three
  print sites. Defensible, and closer to §4.2's demotion of the drop. **Rejected
  by D-060**, and its cost is explicit: Figures 7.3 and 7.4 would plot "{Levelled}
  plus 71.6 cm" on axes labelled `Unity y`, and Table 6.2's two triples for one
  point would lose one of their two names.
- **Two frames, with Figures 7.3 and 7.4 replotted in {Levelled}.** **Rejected by
  D-060 on a binding ground: the printed values must not change in order to remove
  a frame.**

### 4.4 The Unity sensor node and object node — these ARE frames (see 3.1)

Tested under the same rule and they **pass**, so they are not demoted. Their
local axes are read, not merely written: `ArucoSceneReceiver.cs:137-138`,
`:229-231`, `:241-242`, `:253-254`, and outside Unity at
`eval/offset/carry.py:83, 117` and `eval/failure/recovery_core.py:111`. They are
entries 8 and 9 and they carry the system's own names, from
`ArucoSceneReceiver.cs:12-13` and `:224-225, 235`. They are not an artefact of
describing the conjugation; the conjugation exists *because* they do.

For contrast, the **PersonAnchor** node, transformed in exactly the same way,
introduces no frame at all: `IntegratedSceneReceiver.cs:378`
`anchor.TransformPoint(pelvis)` feeds it a **person-space** point (the record
field is documented at `:13`), so the anchor node's local coordinate system **is
{Person}**, an existing frame. That is the cleanest demonstration that the test
discriminates: the same kind of node yields a new frame in one case and not in
the other, depending on what is expressed in it.

### 4.5 The analysis-side levelling — this IS a frame, {Levelled}

Tested separately, on its own evidence, because it is not a Unity node.

- **Write sites.** `eval/offset/carry.py:64` `self.G = from_to_rotation(self.g,
  np.array([0.0, 1.0, 0.0]))`; `:68-69` `level(p) = (G @ p.T).T`. No translation.
- **Read sites where positions are expressed in it, component by component:**
  - `eval/gt/eval_rail_scenario.py:66-70` stores the levelled track as `"xyz"`;
    the docstring at `:51-58` declares the frame — *"Marker-centre track in the
    GRAVITY-LEVELLED desk world (x, y up, z), metres, origin at the desk marker …
    Same frame as detect_waypoints.py's leveled_xyz."*
  - `eval/gt/eval_rail_scenario.py:79-85` reads `y = xyz[idx, 1]` and builds the
    **height histogram** from it; the two height modes, the rail band and the
    parked/lift/rail segmentation are all properties of that y axis.
  - `eval/offset/carry.py:85-86` `height_above_table(obj) = obj[:, 1] + drop`.
  - `evaluate_ch7_object.py:76` and `:514`
    `frame='gravity-levelled desk world (x, y up, z away from the camera)'` — a
    **declared frame convention written into the committed evidence**.
  - `evaluate_ch7_spatial_check.py:338`
    `frame_convention='Gravity-levelled desk world: x along the rail, y up, …'`.
  - `make_ch7_object_waypoint_figures.py:87` labels Figure 7.1's axis
    `'Lateral x (cm)'`; `make_ch7_object_trajectory.py:34` labels x, y, z.
  - Chapter 5 §5.6 prints a coordinate triple in it, `o = (−0.22, 0.08, 0.45)`.
- **The thesis states the dependence itself.** Chapter 7 §7.2
  (`build_ch7.py:286`): *"Segment lengths are invariant under the levelling
  rotation applied to the stored track, so the choice of world frame cannot
  change Tables 7.1 and 7.2. **The fitted-line scatter components, the line tilt
  and the axis-dominance checks** … **are properties of that frame and are not
  invariant**."*
- **Verdict: a real frame,** entry 7, with the system's own name. **It is not a
  levelling transform applied to {World}; it is a system in which the thesis
  reports non-invariant results.** Under D-056 the old W/W collision is gone —
  {World} and {Levelled} are different words — but the *finding* that these are
  two frames 32.04° apart is unchanged and is what made the collision real.
- *Close-call note, now narrower.* This frame and the demoted Unity parent node
  carry **the same rotation** — verified numerically:
  `carry.LeveledWorld.G == ArucoWorld levelling G`, max difference **0.0**. What
  separates them is that the analysis expresses and reports coordinates in the
  levelled system while the Unity parent only places what is already expressed in
  {Unity}. If the author prefers to treat them as one thing, the cost is that
  Chapter 7 §7.2's own sentence about non-invariant quantities loses its
  referent.
- *Relation to {Scene} (entry 13), stated so the two are never merged.*
  {Levelled} and {Scene} **share this basis exactly** — a translation-free test on
  a shared 900-frame object track gives `max |d_scene − d_levelled| = 1.1e−16` —
  and differ **only** in origin, by the constant `(0, 0.716215, 0)` m. They are
  therefore the same axes at two origins, which is why every distance, every
  scatter shape, every direction and every tilt agrees between them and only
  absolute component values differ. **Chapter 7 reports in both**: Figures 7.1/7.2
  and §§7.2, 7.3.3 in {Levelled}, Figures 7.3/7.4 and equation (7.5) in {Scene}.

### 4.6 The sagittally mirrored root basis — NOT a frame

- **Write site.** `shoulder.py:127` `MIRROR = np.array([-1.0, 1.0, 1.0])  #
  sagittal reflection in the root basis`, applied at `:149-150` to
  `R_root.T @ (p13 − p11)` and `R_root.T @ (p15 − p13)` — vectors **already
  expressed in {L24}**.
- **The system's own words deny a second basis.** `shoulder.py:127` "sagittal
  reflection **in the root basis**"; `:133-135` "express both segment vectors
  **in the root basis**, flip their x components (M = diag(-1,1,1)), and run the
  identical right-arm solve"; `KINEMATIC_MODEL.md:507-512` "parent basis = **the
  same L24 root** … Left joint angles are DEFINED through the sagittal reflection
  M = diag(−1, 1, 1) **in the root basis**". The thesis says the same at §3.4.2
  (`build_ch3.py:433-435`).
- **Read sites.** The components read are `u[0], u[1], u[2]` of a reflected
  vector; the reflection changes the numbers, not the basis they are numbers in.
  `shoulder.py:152` passes `np.eye(3)` as `R_root` — **code reuse, not a frame
  declaration**: the solver's first act is `R_root.T @ v` (`shoulder.py:70`), so
  the identity means "these vectors are already expressed", nothing more.
- **The reconstruction confirms it.** `shoulder.py:142-144` reconstructs with
  `M·R·M` — a **conjugation back into {L24}** — and `check_v1_overlay.py:61-65`
  implements the left chain directly in the root basis with the signs of the y-
  and z-angles flipped and rest arm −x. **No second basis is ever the reference
  frame of anything.**
- **Verdict: a class-4 improper basis map under D-054 (section 6), used by
  conjugation.** Not a frame. D-054's clause "if a proper re-based body frame
  results, name and define that frame explicitly" is **not triggered**, because
  `M·R·M` lands back in {L24} — which is why `KINEMATIC_MODEL.md:511` can say "M
  conjugation preserves the construction".

### 4.7 The forearm / wrist frame of Figure 3.5's caption — NOT a frame

- Figure 3.5's caption (`build_ch3.py:294`; the ch3/ch5 audit cites `:305-306`,
  which the builder has since moved) says "the wrists x along each forearm", so
  the thesis **draws** a frame at each wrist.
- **No read site exists anywhere.** `shoulder.py:92-99` expresses the forearm
  **in {L14}** (`ĝ = R_armᵀ(p16−p14)`) and reads *its* components;
  `check_v1_overlay.py:47-66` `fk_arm_dirs` returns "Model-space (root basis)
  unit directions" and builds the forearm as
  `fore = Rarm @ (Ry(ey) @ Rz(ez) @ [1,0,0])` — the rest forearm `(1,0,0)` is a
  vector **in {L14}**, and the product lands in {L24}. **At no point is any
  position or orientation expressed in a forearm or wrist frame.** Chapter 3
  §3.3.1 says why: "The three wrist rotations cannot be observed from the eight
  body landmarks, so the chain ends at the wrist **as a tracked point**."
- **Verdict: not a frame.** C3-22 and C3-39 are therefore **not a missing frame
  definition**. C3-22 is a **figure caption that draws something the model does
  not have** (section 9). C3-39, the unprinted elbow rotation, has no second
  frame and is therefore a **class-3 operator** acting on {L14}'s rest direction
  — see section 8.2, and the note in section 11.

### 4.8 The eighth candidate — RESOLVED by D-057, verified in section 0

**The basis equation (3.22) would map into, if it were a passive re-expression:
the upper arm with the swing applied and the twist not.** The corrected inventory
found this to be the one candidate that is genuinely distinct **and** genuinely
unnamed, and put two routes to the author. **D-057 took route (b) — declare it a
class-3 operator — and section 0 of this file verifies the premise that route (b)
depends on.** No label is issued and no frame is added. The evidence is kept here
because the *finding* is unchanged; only its disposal is new.

**What the code establishes (unchanged).**

- `shoulder.py:79` `fp = _rz(-th_z) @ (_ry(-th_y) @ f)`, where
  `f = R_rootᵀ(p16 − p14)` (`:78`) is the forearm vector expressed in **{L12}**.
  The product `Rz(−θz) Ry(−θy)` is `(Ry(θy) Rz(θz))⁻¹`, the inverse of the
  **swing**, with the twist factor `Rx(θτ)` absent.
- `shoulder.py:82` `th_t = np.arctan2(-fp[1], fp[2])` — the y and z components of
  `fp` are read individually.
- The thesis does the same at equations (3.22) and (3.23) (`build_ch3.py:424,
  430`).
- `KINEMATIC_MODEL.md:315-318` states the geometric consequence — "measure AFTER
  removing swing, so the arm axis is back at x̂ and the perpendicular plane is
  exactly the local y–z plane".

**What the system does NOT do: give it a name.** Both the code and the thesis
describe the step as an **operation on a vector**: `shoulder.py:65` "**un-swing**
the forearm"; `KINEMATIC_MODEL.md:317` "un-swing: `R_swingᵀ · f`"; `:330`
"**un-swing first**"; thesis §3.4.2 "**the procedure undoes the swing first**".

**Resolution (D-057 + section 0).** The operation is **active**. The components
equation (3.23) reads are components of the **operated** vector in **{L12}**, an
already-defined frame (entry 11). Equation (3.22) is **class 3**, carries no
frame pair, and is written `^{L12} f′ = R_Z(−t_z) R_Y(−t_y) · ^{L12} f`, with the
surrounding sentence stating that the matrix is an operator, that it is not a
frame-relative rotation, and that `f` and `f′` are both {L12} vectors. **The
equation is unblocked.** The ch3/ch5 audit's `{E0_r}` / `{E0_l}` are withdrawn.

### 4.9 A related declaration the author must still make: `R_rest` in equation (6.5)

Not an unnamed frame, but the same kind of gap, and it is the last thing blocking
equations (6.4) and (6.5). **Unchanged by D-056 and D-057.**

- **The usage test says the avatar bone axes are not a frame.** A grep of
  `IntegratedSceneReceiver.cs` finds **no** `localPosition`, `localRotation`,
  `InverseTransformPoint` or `TransformDirection` on any bone: only global
  `.rotation` (`:239-243` at spawn, `:370-374` per frame), global `.position`
  (`:378-379`, `:395-398`, `:304-311`) and `.localScale` (`:196, 227`). **Nothing
  is ever expressed in a bone's own axes.** The five `c_rest` values are the
  bones' **spawn orientations expressed in the scene axes** (`:237-238` "the rig
  spawns unrotated (body axes = scene axes)").
- **But Craig's notation for a right-multiplied factor wants a frame anyway.**
  `R_bone = A R_chain R_rest` right-multiplies `R_rest`, whose Craig role is
  `^{model}_{bone} R`.
- **What the author must state**, as the ch6/ch8 audit's U-1 asked: (i) the frame
  in which the rest rotations are captured, (ii) the frame the streamed chain
  rotations `R_0, R_1, R_2` are expressed in, and (iii) the assumption linking
  them (rig spawns unrotated, body axes = scene axes, arms forced to the T-pose
  before capture — `:217-218, 261-273`). The alternative, consistent with the
  usage test and with D-057's precedent, is to declare `R_rest` a **fixed constant
  re-basing factor** defined as the bone's spawn orientation in the scene axes and
  **not** to name a bone frame. Either settles (6.4) and (6.5).

---

## 5. The symbol collisions — DISSOLVED by D-056

The corrected inventory's section 5 was a six-part analysis of the letter
collisions (U, W, P, t, S, and a list of minor ones) written to give the author
the counts he needed to reassign letters under D-055. **D-055 is SUPERSEDED and
that analysis is obsolete. It is deleted, not carried forward.** Under D-056
there are no letter collisions left to resolve, because frames no longer compete
for letters at all.

**What replaced them.** Every frame that previously carried a letter now carries
its name, so the letter is released and immediately falls to the non-frame
quantity that was already using it:

| former collision | how D-056 dissolves it |
|---|---|
| `U` = Unity frame (14) vs `U` = the SVD left-singular factor (3) | the frame becomes **{Unity}**; `U` means only the SVD factor |
| `C` = sensor frame (45) vs `C` = the Chapter 7 sample covariance (2) | the frame becomes **{Sensor}**; `C` means only the covariance |
| `W` = world frame (34) vs `W` = levelled world (3 lettered) | two names, **{World}** and **{Levelled}**; the letter `W` is released entirely |
| `P` = person space (17) vs `P` = Craig's point symbol (prospective, on every position vector) | the frame becomes **{Person}**; `P` is free for `^A P` and `^A P_BORG`, which D-054 needs |
| `t` = translation (8 subscripted + bare) vs `t` = time (3) vs `t` = frame index (6) | translations become `^A P_BORG` under D-054, so the translation meaning retires on its own; `t` keeps **time** and **frame index** |
| `S` = the swap matrix (20) vs `{S}` once proposed for the sensor frame | no `{S}` is issued; the frame is **{Sensor}** and `S` remains the class-4 swap |
| `A` = the anchor rotation (4) vs `A_j` = absolute error in cm | the anchor rotation becomes `^{Unity}_{Person} R` under D-054 class 1, so the bare `A` retires; `A_j` keeps its letter |
| `L` = the levelling rotation in §6.5 (2) vs `L_1`, `L_2`, `L_j`, `L_rec,j`, the marker side `L`, and `L11…L24` | the levelling rotation becomes `^{Levelled}_{Unity} R` under D-054 class 1, so the bare `L` retires; every other `L` keeps its letter |

**No existing non-frame quantity is renamed. Explicitly, and for the record:**

| quantity | keeps | where |
|---|---|---|
| `U`, `Σ`, `V` — the singular value decomposition factors | **unchanged** | Ch 2 §2.2.2, eq (2.1); `build_ch2.py:246, 249, 250` |
| `C` — the sample covariance matrix, and `u` its unit eigenvector | **unchanged** | Ch 7 eq (7.2); `build_ch7.py:233-236` |
| `A_j` — absolute error in centimetres | **unchanged** | Ch 7 eq (7.1); `build_ch7.py:74, 228-231` |
| `R_j` — relative error in percent | **unchanged** | Ch 7 eq (7.1) |
| `L_1`, `L_2` — calibrated arm segment lengths (29 occurrences) | **unchanged** | Ch 5, Table 5.1, eqs (5.6), (5.8)-(5.10) |
| `L_j`, `L_rec,j` — measured and reconstructed segment lengths | **unchanged** | Ch 7 eq (7.1) |
| `L` — the printed marker side length | **unchanged** | Appendix E.2 |
| `L11 … L24` — the MediaPipe landmark names (53 occurrences) | **unchanged**, and now also serve as the link-frame labels (§2.3) | Ch 2, 3, 5, appendices |
| `t` — time (eq 4.3) and frame index (eqs 7.5, 7.6) | **unchanged**, both meanings | Ch 4, Ch 7 |
| `S`, `F`, `M` — the class-4 maps | **unchanged**, and never given Craig notation (section 6) | Ch 2, 3, 6 |
| `G` — the levelling rotation in the code | **unchanged** in the code; printed as `^{Levelled}_{Unity} R` | `carry.py:64` |
| `w` — the Rodrigues axis; `w_max` — the angular rate bound | **unchanged** | Appendix E.3/E.4; eq (4.3) |
| `M̄` — the element-wise mean; `M` — the sagittal mirror | **unchanged**, case- and accent-separated as they already are | Ch 2 §2.2.2, Ch 4 §4.3; Ch 3 §3.4.2 |

**Two typographic near-misses that survive D-056, recorded not ruled on:** `L_1` /
`L_2` against `L11`…`L24` in Chapter 5 (§2.3 gives the positional mitigation), and
`p_w` against `p_W` in equation (6.1) versus §6.5's worked example
(`build_ch6.py:272` and `:453`) — a lowercase/uppercase subscript inconsistency in
one symbol, which the relabelling pass fixes for free by writing `^{World} P`.

---

## 6. Class-4 improper basis map declarations (D-054)

Each requires source basis, destination basis, matrix form, determinant and
whether self-inverse. **None may carry Craig `R` or `T` notation, and frame
cancellation must never be applied through one.** Verified in code and
numerically on `eval/output/scene_calibration_r6bc.json` by the ch6/ch8 audit.
**Unchanged; only the frame names are rewritten.**

| map | source | destination | form | det | self-inverse? | code |
|---|---|---|---|---|---|---|
| **F** | {Sensor} (right-handed) | {Person} (left-handed) | `diag(1, −1, 1)` | **−1** | **Yes** — true and **not currently stated in the thesis**; the thesis says it only of the swap (`build_ch6.py:277`). Audit item X-1. | `root_frame.py:9, 12-14`; `carry.py:25`; `check_unity_log.py:89` |
| **S** | {World} (right-handed) | {Unity} (left-handed) | exchanges the 2nd and 3rd coordinates | **−1** | Yes (an exchange of two coordinates) | `frames.py:38-40`; applied to points at `:87`, by **conjugation** to rotations at `:88`; `carry.py:24` (named `P` in the code) |
| **M** | {L24} | **{L24}** (a reflected vector, *not* a new basis — §4.6) | `diag(−1, 1, 1)` | **−1** | Yes | `shoulder.py:127`, applied `:149-150`, reconstructed by conjugation `:142-144` |

Numerically confirmed on the rail calibration: `det S = −1`, `det F = −1`,
`det R_cam = +1`, `det A = det(S R_cam F) = +1`, `det G = +1`,
`det(S R_cam) = −1`. The camera-to-Unity composite `S R_cam` is improper and is
recorded as `det = −1.000000` with orthogonality error ≈ 1.9e−15 in
`writing/v8/condensed/audit_evidence/ch7_restructured/human.json`.

**Two Craig-legal forms follow, and both are already in the code.**

- `A = S R_cam F = (S R_cam S)(S F)` — the two improper factors pair off inside
  it, `S R_cam S` is `^{Unity}_{MappedCamera} R` (class 1) and `S F = R_x(−90°)`
  is `^{MappedCamera}_{Person} R` (class 1). This is exactly what
  `IntegratedSceneReceiver.cs:161-163` composes.
- A **pose** crossing `S` is a similarity, not a left composition:
  `^{Unity}_{MappedMarker} R = S · ^{World}_{Object} R · S` (`frames.py:88`), and
  the live link un-does it the same way (`v2/common/object_link.py:109-111`
  `T = T_cam_desk @ make_T(W @ R_u @ W, W @ t_u)`). Naming **{MappedMarker}** is
  what makes this statement legal, and it resolves the ch6/ch8 audit's X-2 at the
  same time: the criterion the thesis is missing is *conjugate when the body's
  own frame is re-based by the same map, left-multiply when it is not*, and
  {MappedMarker} / {MappedCamera} are the frames that make "re-based" a thing one
  can point at.

**Not class 4, recorded to keep the contrast visible:** the levelling rotation `G`
(code) / `L` (Chapter 6) is a **proper** rotation, `det +1`, between two
left-handed frames, so it is left-multiplied, not conjugated (`carry.py:79`
`R_obj = G @ recompose_zxy(e)`). The code's difference in treatment between `S`
and `G` is the empirical proof of the missing criterion.

**Also not class 4, and not a rotation at all:** the floor drop. `^{Scene}_{Levelled} T`
is a **class-2 homogeneous transform with identity rotation** —
`^{Scene}_{Levelled} R = I₃`, `^{Scene} P_{Levelled}ORG = (0, d, 0)`,
`d = 0.716215 m` (r6b). D-060 requires it to be printed in exactly that explicit
form rather than implied. It cancels freely under Craig's rule, because both
frames are the same left-handed axes; nothing about it is improper.

### 6.1 Appendix D.2's depth-imager transform — no label, and none is needed

**Recorded as required, and closed.** Appendix D.2 says the depth point is "moved
into the colour camera's frame through the known transformation between the two
imagers" (`build_appendix.py:237`). That transform **appears nowhere in this
repository**. The alignment is performed by a single vendor call,
`rs.align(rs.stream.color)`, at `v1/realtime/person/realtime_person.py:79` (used
at `:226`), `v1/realtime/object/realtime_object.py`,
`v2/broker/capture_broker.py:160` and `v3/replay/bag_source.py:30`; a grep across
every `.py` and `.cs` for a depth-to-colour extrinsic, a `T_depth`, or a
depth-imager frame returns nothing.

**Therefore: the depth imager frame is not a frame of this system, no label is
issued for it, and the inter-imager transform gets no symbol.** What the thesis
should state instead, once, in Appendix D.2: only the **aligned colour-optical
frame** — {Sensor} — is ever used downstream, and the inter-imager transform is
internal to the vendor library and is never printed. This is the ch2/ch4 audit's
A-D03 option (b), and it is the true description of the pipeline.

---

## 7. How to read the label table

Labels use the names of section 2. Craig's conventions, unchanged:

- `^{A}_{B} R` — orientation of {B} relative to {A}; **columns are {B}'s axes
  expressed in {A}**.
- `^{A} P_{B}ORG` — position of {B}'s origin expressed in {A}.
- `^{A}_{B} T = [ ^{A}_{B} R , ^{A} P_{B}ORG ; 0 0 0 , 1 ]`, and
  `^{A} P = ^{A}_{B} T ^{B} P`.
- Cancellation `^{A}_{B} T ^{B}_{C} T = ^{A}_{C} T` applies to class 1 and class 2
  only, and **never across a class-4 map**.

Status marks:

- **APPLY** — ready for the relabelling pass. Direction established by the audits
  from the code; both frames named; nothing further required.
- **OPERATOR** — class 3 per D-054 / D-057. Acts on a vector inside one frame;
  carries **no frame pair**. The operand and the result each carry the one frame
  they share. The surrounding sentence must identify it as an operator.
- **IMPROPER** — class 4 per D-054. `det = −1`. **Never** Craig notation, never
  cancelled through. Declared once in section 6.
- **BLOCKED** — not applicable by a relabelling pass, with the reason given. Two
  kinds: an author declaration is missing, or the row is a **substantive defect**
  and belongs to section 9.

**Directions were established by the three audits from the code and are reused,
not re-derived.** Builder line numbers are the audits' and were spot-checked
against the current builders; the one drift found is noted at C3-22.

---

## 8. TASK 3 — the complete A/B label assignment table

### 8.1 Chapter 2 — `build_ch2.py`

| item | location | present notation | assigned Craig form | status |
|---|---|---|---|---|
| C2-01 | `:219-220`, §2.2.1 definition sentence | `T_AB` | `^{A}_{B} T`, with `^{A} P = ^{A}_{B} T ^{B} P` | **APPLY** |
| C2-02 | Table 2.2 row 1 | `T_CW` | `^{Sensor}_{World} T` | **APPLY** |
| C2-03 | Table 2.2 row 2 | `T_C,wall` | `^{Sensor}_{Wall} T` | **APPLY** |
| C2-04 | Table 2.2 row 3 | `T_CO` | `^{Sensor}_{Object} T` | **APPLY** |
| C2-05 | Table 2.2 row 4 | `T_WO = T_CW⁻¹ T_CO` | `^{World}_{Object} T = ^{World}_{Sensor} T · ^{Sensor}_{Object} T`, with `^{World}_{Sensor} T = (^{Sensor}_{World} T)⁻¹` stated separately — the cancellation Chapter 4 §4.1 argues from becomes visible | **APPLY** |
| C2-06 | Table 2.2 row 5 | `T_WC = T_CW⁻¹` | `^{World}_{Sensor} T` | **APPLY** |
| C2-07 | Table 2.2 row 6 | `F` | none — class 4, section 6 | **IMPROPER** |
| C2-08 | Table 2.2 row 7 | `T_root` | `^{Person}_{L24} T` | **APPLY** |
| C2-09 | Table 2.2 row 8 | `T_sh`, `T_el` | `^{L24}_{L12} T`, `^{L12}_{L14} T`; left pair `^{L24}_{L11} T`, `^{L11}_{L13} T` — the sides, never distinguished today, come for free | **APPLY** |
| C2-10 | Table 2.2 row 9 | `S` | none — class 4, section 6 | **IMPROPER** |
| C2-11 | `:244-247` | `M̄ = U Σ Vᵀ` | keep `M̄`, `U`, `Σ`, `V` generic; label the instantiation `^{Sensor}_{World} M̄` | **APPLY** |
| C2-12 | `:249-251`, eq (2.1) | `R = U diag(1,1,det(UVᵀ)) Vᵀ` | stays generic `^{A}_{B} R`; instantiated on `^{Sensor}_{World} R`, `^{Sensor}_{Wall} R`, `^{World}_{Object} R`. `U` keeps its letter | **APPLY** |
| C2-13 | `:285`, prose | "the pose of the marker in the camera frame C" | `^{Sensor}_{Object} T` | **APPLY** |
| C2-14 | `make_ch2_frames_fig.py:103-107` (panel a), `:205-208` (panel b), Figure 2.5 arrows | `T_{C,wall}`, `T_{CO}`, `T_{CW}`, `T_{WO}` | the four semantic forms above; arrow directions already correct | **APPLY** |
| C2-15 | Table 2.2 caption | "A transformation written with two frame letters carries a point from the second frame into the first" | restate with names, and exclude `F` and `S` explicitly (class 4, not transformations) | **APPLY** |
| C2-16 | Table 2.3, wall pose in the world | prose | `^{World}_{Wall} T = ^{World}_{Sensor} T · ^{Sensor}_{Wall} T` (frames cancel) | **APPLY** |
| C2-17 | Table 2.3, camera pose in the world | prose | `^{World}_{Sensor} T` | **APPLY** |
| C2-18 | Table 2.3, gravity direction | no symbol | `^{World} ĝ` — column 2 of `^{World}_{Wall} R` (`calibrate_scene.py:148`) | **APPLY** |
| **F2.4b** | `build_ch2.py:213` (Figure 2.4(b) caption) and `:217` (the body sentence that repeats it) | "The Unity frame **U** at the root of the avatar rig, with its axes drawn at the origin." / "Figure 2.{F_CAM}(b) shows **U** at the root of the avatar rig." | **The frame drawn is {Scene}** (D-060, §4.3). No rotation or transform symbol appears in the caption, so what this row carries is the **corrected wording**, not a Craig label. See the four defects and the proposed replacement immediately below the table | **APPLY** — determinate under D-060. *The replacement wording is **proposed, not applied**; the author accepts, amends or overrules it* |

#### 8.1.1 F2.4b — the four defects, and the corrected wording (**proposed, not applied**)

Carried forward from `UNITY_FRAME_RESOLUTION.md` §9 and recorded here because §8.1
is where the relabelling pass will look. **The figure itself is accurate.** It is a
Unity editor screenshot (`writing/v8/figures/ch3_fig_sensor_unity.png`) of the
avatar standing on a ground plane in the T-pose with the transform gizmo at its
feet, y up, x and z in the ground plane — **a correct picture of {Scene}**, which
is the frame Chapter 7's own Figures 7.3 and 7.4 report in. Only the caption is
wrong, in four independent ways, in order of seriousness:

1. **The label is wrong by 32.04°.** Table 2.2 row 9 (`build_ch2.py:234`) defines
   `U` as the output of `S`, citing equation (6.1). The axes in the screenshot are
   Unity's **scene** axes, which §4.3 measures to be `G` — 32.0368° — away from
   that. This is the reader's *first* sight of the Unity frame, in Chapter 2, and
   it shows the wrong one.
2. **The origin is wrong by 71.6 cm.** Equation (6.1)'s `U` has its origin at the
   desk-marker centre. The drawn origin is the Unity scene origin, which sits
   `d = 0.716215 m` below the desk marker along levelled y.
3. **"At the root of the avatar rig" names an origin that moves every frame.** The
   rig root is re-translated on every frame —
   `IntegratedSceneReceiver.cs:379` `rigRoot.position += target - hip.position;`.
   It coincides with the scene origin only at spawn, before any data arrives
   (`:186-187`). A frame origin cannot be attached to a node that moves with the
   measurement.
4. **The screenshot does not contain the frame it is captioned with.** There is no
   desk, no wall, no marker and **no ArucoWorld node** in the image — it is the
   bare rig scene. Equation (6.1)'s basis is not present in the picture at all.

**Proposed replacement caption** for `build_ch2.py:213` — for the author to
accept, amend or overrule; **nothing is applied**:

> "(b) The Unity **scene** frame, left-handed with y up, drawn at the origin of the
> Unity scene, where the avatar rig spawns in the reference T-pose. The
> reconstruction reaches this frame from the display axes of equation (6.1) by the
> levelling rotation of Section 6.4; Figures 7.3 and 7.4 report in it."

**Proposed replacement for the body sentence** at `build_ch2.py:217`, which today
reads "Figure 2.4(b) shows **U** at the root of the avatar rig": a sentence that
separates the two frames — the display axes `U` of equation (6.1) are anchored on
the desk marker and are **not** levelled; the Unity scene frame of Figure 2.4(b) is
those axes turned upright by the calibrated gravity and dropped so the drawn floor
is at zero height.

*Note for the pass: correcting this caption introduces {Scene} in Chapter 2, which
is where Table 2.2 and the frame table live, so the {Unity} / {Levelled} / {Scene}
distinction should be stated once there rather than first in Chapter 6.*

### 8.2 Chapter 3 — `build_ch3.py`

| item | location | present notation | assigned Craig form | status |
|---|---|---|---|---|
| C3-01 | `:188`, eq (3.1) | `q = F p`, `F = diag(1,−1,1)` | `^{Person} p = F · ^{Sensor} p`, `F` declared improper; **never** `^{Person}_{Sensor} R` | **IMPROPER** |
| C3-02 | `:197`, prose | "columns are the child's axes in the parent's coordinates" | `^{A}_{B} R = [ ^{A} X̂_B  ^{A} Ŷ_B  ^{A} Ẑ_B ]` | **APPLY** |
| C3-03 | `:197`, prose | "the translation part is a 3-vector t" | `^{A} P_{B}ORG`, "expressed in {A}" | **APPLY** |
| C3-04 | `:199-201`, eq (3.2) | `T = [R t; 0 1]` | `^{A} P = ^{A}_{B} T ^{B} P` | **APPLY** |
| C3-05 | `:205`, eq (3.3) | `v_local = R_parentᵀ v` | `^{B} v = ^{B}_{A} R ^{A} v`, `^{B}_{A} R = (^{A}_{B} R)ᵀ` | **APPLY** |
| C3-06 | `:209-212`, eq (3.4) | `p_child = Rᵀ(p_parent − t)` | `^{B} P = (^{A}_{B} R)ᵀ(^{A} P − ^{A} P_{B}ORG)`; `^{B}_{A} T = (^{A}_{B} T)⁻¹` | **APPLY** |
| C3-07 | `:221`, eq (3.5) | `T_root` | `^{Person}_{L24} T` | **APPLY** |
| C3-08 | `:222`, eq (3.5) | `T_sh,r` (and `T_sh,l`) | `^{L24}_{L12} T` (and `^{L24}_{L11} T`) | **APPLY** |
| C3-09 | `:223`, eq (3.5) | `T_el,r` (and `T_el,l`) | `^{L12}_{L14} T` (and `^{L11}_{L13} T`) | **APPLY** |
| C3-10 | `:225-236`, eq (3.5) + prose | `R_sh,r` | `^{L12}_{L14} R` — today the subscript names the **reference** frame while `R_root`'s names the **described** frame; the Craig form removes the contradiction | **APPLY** |
| C3-11 | `:237`, eq (3.6) | `T_arm,r = T_root T_sh,r T_el,r` | `^{Person}_{L14} T = ^{Person}_{L24} T · ^{L24}_{L12} T · ^{L12}_{L14} T` — cancellation visible, and the third name "arm,r" for {L14} disappears | **APPLY** |
| C3-12 | `:239`, prose | "the inverse transformations … carry it into the frame where its joint is solved" | `^{L24}_{Person} T`, `^{L12}_{Person} T`, `^{L14}_{Person} T` | **APPLY** |
| C3-13 | chapter-wide | the self-inconsistent subscript convention | resolved wholesale by C3-07…C3-11 | **APPLY** |
| C3-14 | `:260`, eq (3.7) | `x̂ = (p24−p23)/‖·‖` | `^{Person} X̂_{L24}`, from `^{Person} P_{23}`, `^{Person} P_{24}` | **APPLY** |
| C3-15 | `:265`, eq (3.8) | `s = p12 − p24` | `^{Person} s` | **APPLY** |
| C3-16 | `:270`, eq (3.9) | `ẑ = (x̂ × s)/‖·‖` | `^{Person} Ẑ_{L24}` | **APPLY** |
| C3-17 | `:279`, eq (3.10) | `ŷ = ẑ × x̂` | `^{Person} Ŷ_{L24}` | **APPLY** |
| C3-18 | `:284`, eq (3.11) | `R_root = [x̂ ŷ ẑ]` | `^{Person}_{L24} R` | **APPLY** |
| C3-19 | `:288`, eq (3.12) | `T_root = [R_root, p24; 0 1]` | `^{Person}_{L24} T`, `^{Person} P_{L24}ORG = ^{Person} P_{24}` | **APPLY** |
| C3-20 | `:290`, prose | the T-pose reference columns | `^{Person}_{L24} R` at the reference configuration | **APPLY** |
| C3-21 | `:257-258`, Figure 3.4 caption | "the finished frame at the L24 origin" | name {L24} in the caption | **APPLY** |
| C3-22 | `:294`, Figure 3.5 caption (audit cites `:305-306`; the builder has moved it) | "the wrists x along each forearm" | — | **BLOCKED** — substantive: the caption draws a frame the mathematics never defines (§4.7, §9 S-6) |
| C3-23 | `:327`, eq (3.13) | `T_sh,r = [I, R_rootᵀ(p12−p24); 0 1]` | `^{L24}_{L12} T`, with `^{L24}_{L12} R = I₃` and `^{L24} P_{L12}ORG` | **APPLY** |
| C3-24 | `:337`, eq (3.14) | `T_el,r = [R_sh,r, R_rootᵀ(p14−p12); 0 1]` | `^{L12}_{L14} T`, `^{L12} P_{L14}ORG` | **APPLY** |
| C3-25 | `:344-348`, inline | `v = p14 − p12`, `v_local = R_rootᵀ v` | `^{Person} v`, `^{L24} v` | **APPLY** |
| C3-26 | `:353`, eq (3.15) | `R = Ry(y) Rx(x) Rz(z)` | class 3, Craig's `R_K(θ)` about the parent's axes; the decoded `m` is whichever `^{A}_{B} R` is being read. Craig calls the printed rule a **fixed-angle** (Z-X-Y) set, not Euler — a prose correction that rides along | **OPERATOR** |
| C3-27 | `:356-363`, eq (3.16) | the multiplied-out 3×3 | as C3-26 | **OPERATOR** |
| C3-28 | `:374-386`, eq (3.17) + the gimbal-lock display | `R_x, R_y, R_z` | as C3-26 | **OPERATOR** |
| C3-29 | `:388-391`, §3.4.1 | "Its pose is the pair (R_root, p24)" | `( ^{Person}_{L24} R , ^{Person} P_{L24}ORG )` | **APPLY** |
| C3-30 | `:397`, eq (3.18) | `R_sh,r = Ry(t_y) Rz(t_z) Rx(t_t)` | `^{L12}_{L14} R` | **APPLY** |
| C3-31 | `:403-405`, eq (3.19) | `â = R_sh,r x̂` | `^{L12} â` = **the first column of** `^{L12}_{L14} R`. Writing it as a column removes the operator-versus-description ambiguity. Glyph note: `x̂` is `(1,0,0)` here and `^{Person} X̂_{L24}` eleven equations earlier | **APPLY** |
| C3-32 | `:413, :416`, eqs (3.20)-(3.21) | `t_z = asin(a_y)`, `t_y = atan2(−a_z, a_x)` | scalars read from `^{L12} â`'s components | **APPLY** |
| **C3-33** | `:424`, **eq (3.22)** | `f′ = Rz(−t_z) Ry(−t_y) f` | `^{L12} f′ = R_Z(−t_z) R_Y(−t_y) · ^{L12} f` — **no frame pair**; both operands are {L12} vectors. Prose must state that the matrix is an operator, that it is not a frame-relative rotation, and that (3.23) reads components of the **operated** vector in {L12} | **OPERATOR** (D-057; premise verified in section 0) |
| C3-34 | `:430`, eq (3.23) | `t_t = atan2(−f′_y, f′_z)` | scalar read from `^{L12} f′`'s components | **APPLY** |
| C3-35 | `:433-435`, §3.4.2 | `M = diag(−1,1,1)` | none — class 4; the vectors stay in {L24} (§4.6) | **IMPROPER** |
| C3-36 | `:439-440`, §3.4.3 | `R_arm,r = R_root Ry Rz Rx` | `^{Person}_{L14} R = ^{Person}_{L24} R · ^{L24}_{L12} R · ^{L12}_{L14} R` (the middle factor is I₃) | **APPLY** |
| C3-37 | `:441-442`, §3.4.3 | `ĝ = R_arm,rᵀ(p16−p14)` | `^{L14} ĝ = (^{Person}_{L14} R)ᵀ(^{Person} P_{16} − ^{Person} P_{14})/‖·‖` | **APPLY** |
| C3-38 | `:444-445`, eq (3.24) | `e_z = asin(g_y)`, `e_y = atan2(−g_z, g_x)` | scalars read from `^{L14} ĝ`'s components | **APPLY** |
| C3-39 | §3.4.3, the unprinted elbow rotation | `Ry(e_y) Rz(e_z)` (`shoulder.py:94`; `check_v1_overlay.py:60`) | class 3: `^{L14} ĝ = R_Y(e_y) R_Z(e_z) · ^{L14} x̂`. **Not** `^{L14}_{F} R`: §4.7 demotes the forearm frame on read-site evidence, so there is no second frame for it to relate to | **OPERATOR** |
| C3-40 | `:468-478`, Table 3.1 | columns "Camera frame C (m)", "Person space P (m)" | `^{Sensor} P_i`, `^{Person} P_i` — the one place in Chapter 3 that already carries its frame | **APPLY** |
| C3-41 | `:481-485` | `p23, p24, p12` numeric | `^{Person} P_{23}`, `^{Person} P_{24}`, `^{Person} P_{12}` | **APPLY** |
| C3-42 | `:487-490` | `x̂, ẑ, ŷ` numeric | `^{Person} X̂_{L24}`, `^{Person} Ẑ_{L24}`, `^{Person} Ŷ_{L24}` | **APPLY** |
| C3-43 | `:495-498` | `R_root` 3×3 numeric | `^{Person}_{L24} R` | **APPLY** |
| C3-44 | `:501-506` | `T_root` 4×4 numeric | `^{Person}_{L24} T` | **APPLY** |
| C3-45 | `:507-512` | `T_sh,r` 4×4 numeric | `^{L24}_{L12} T` | **APPLY** |
| C3-46 | `:520-525` | `v`, `v_local`, `â` | `^{Person} v`, `^{L24} v`, `^{L12} â` | **APPLY** |
| C3-47 | `:526` | `f = R_rootᵀ(p16−p14)` | `^{L12} f` | **APPLY** |
| C3-48 | `:532` | `f′ = Rz(76.6°) Ry(−43.0°) f` | the numeric instance of C3-33: `^{L12} f′ = R_Z(76.6°) R_Y(−43.0°) · ^{L12} f`. Signs verified consistent with eq (3.22) at `t_z = −76.6°`, `t_y = 43.0°` | **OPERATOR** |
| C3-49 | `:536` | `ĝ = (0.94, 0.00, 0.34)` | `^{L14} ĝ` | **APPLY** |
| C3-50 | `:544-548` | `T_el,r` 4×4 numeric | `^{L12}_{L14} T`; last column verified equal to `v_local` | **APPLY** |
| C3-51 | `:549-556` | the closing check | `^{Person} P_{L14}ORG = ^{Person}_{L14} T (0,0,0,1)ᵀ`; `^{L14} P_{16} = (^{Person}_{L14} T)⁻¹ ^{Person} P_{16}` | **APPLY** |
| C3-52 | `:197`, prose | "no matrix is ever inverted numerically" | — | **BLOCKED** — true of Chapter 3's chain, **false of the path Chapter 5 depends on** (`carry.py:59`, `recovery_core.py:69`). Qualify or drop; a claim, not a label (§9 S-10) |

### 8.3 Chapter 4 — `build_ch4.py`

| item | location | present notation | assigned Craig form | status |
|---|---|---|---|---|
| C4-01 | `:145-146` | `T_CW` | `^{Sensor}_{World} T` | **APPLY** |
| C4-02 | `:146-147` | `T_CO` | `^{Sensor}_{Object} T` | **APPLY** |
| C4-03 | `:147-148` | `T_WO` | `^{World}_{Object} T` | **APPLY** |
| C4-04 | `:150`, eq (4.1) | `T_WO = T_CW⁻¹ T_CO` | `^{World}_{Object} T = ^{World}_{Sensor} T · ^{Sensor}_{Object} T` | **APPLY** |
| C4-05 | `:154-156`, eq (4.2) | bare `T`, `R`, `t`; `T⁻¹ = [Rᵀ, −Rᵀt; 0 1]` | `^{B}_{A} T = (^{A}_{B} T)⁻¹`; instantiated `^{World}_{Sensor} T` | **APPLY** |
| C4-06 | `:158-159` | `T_WC` | `^{World}_{Sensor} T` | **APPLY** |
| C4-07 | `:161`, prose | "the camera frame enters the chain twice … the two contributions cancel" | now visible in C4-04's form | **APPLY** |
| C4-08 | `:181-185`, eq (4.3) | `p_i`, `p_last` | `^{Unity} P_{Object}ORG(i)`, `^{Unity} P_{Object}ORG(last)` | **APPLY** — **unblocked by D-058**, which declares equation (4.3)'s input to be the {Unity} frame "matching what the implementation actually reads", and directs that "the prose that calls it the world frame track" be corrected. The read is at `eval/common/clean_object_track.py:59-61`, from the `unity_px, unity_py, unity_pz, unity_ex, unity_ey, unity_ez` columns. `S` is orthogonal, so **no number changes**; this is a declaration, not a correction, and not a code change |
| C4-09 | `:184`, eq (4.3) | `angle(R_lastᵀ R_i)` | `angle((^{Unity}_{MappedMarker(last)} R)ᵀ · ^{Unity}_{MappedMarker(i)} R) = angle(^{MappedMarker(last)}_{MappedMarker(i)} R)`; **the reference frame cancels out of the result** and the thesis should say so | **APPLY** — unblocked with C4-08 by D-058. *Note the child frame: in the {Unity} basis the object's own axes are the **mapped** ones (§6, `frames.py:88`), so the child is {MappedMarker}, not {Object}. The cancellation is legal because both factors are class-1 proper rotations between the same two frames; it does **not** cross `S`* |
| C4-10 | `:167`, prose | "a rolling chordal mean, which is equation (2.1) over a short window" | cross-reference to C2-12's generic form | **APPLY** |
| C4-11 | `:201-204` | `M̄` numeric | `^{Sensor}_{World} M̄` | **APPLY** |
| C4-12 | `:207-208` | `T_CW` numeric | `^{Sensor}_{World} T` | **APPLY** |
| C4-13 | `:210` | gravity, no symbol at all | `^{World} ĝ` | **APPLY** |
| C4-14 | `:213` | `−Rᵀ t`, bare `R`, bare `t` | `^{World} P_{Sensor}ORG = − ^{World}_{Sensor} R · ^{Sensor} P_{World}ORG` | **APPLY** |
| C4-15 | `:217` | `t_CO` | `^{Sensor} P_{Object}ORG` | **APPLY** |
| C4-16 | `:220-222` | `R_WO = Rᵀ R_CO`; `t_WO = Rᵀ t_CO + t_WC` (bare `Rᵀ` beside a labelled `R_CO`) | `^{World}_{Object} R = ^{World}_{Sensor} R · ^{Sensor}_{Object} R`; `^{World} P_{Object}ORG = ^{World}_{Sensor} R · ^{Sensor} P_{Object}ORG + ^{World} P_{Sensor}ORG` | **APPLY** |
| C4-17 | `:225-230` | `t_WO`, `R_WO` numerics | `^{World} P_{Object}ORG`, `^{World}_{Object} R` | **APPLY** |
| C4-18 | `:234`, prose | "projected onto the measured gravity direction" | `^{World} ĝ` | **APPLY** |
| C4-19 | `:190-192` | `v_max`, `w_max` | scalars; no frame of their own — the vectors they bound carry the label, so they follow C4-08 | **APPLY** |
| C4-20 | `:143`, Figure 4.1 caption | "the world frame W **of the calibration**" | — | **BLOCKED** — substantive: the figure code draws the **per-frame** desk detection, not the calibrated anchor (§9 S-8) |
| C4-21 | Figure 4.2 caption | "the object track in the world frame … one panel per world axis" | `^{World} P_{Object}ORG` per axis | **APPLY** |

### 8.4 Chapter 5 — `build_ch5.py`

Every Chapter 5 transform is labellable, because the frames it needs —
**{Levelled}** and **{MappedMarker}** — are named in section 3.

| item | location | present notation | assigned Craig form | status |
|---|---|---|---|---|
| C5-01 | `:253-256`, Table 5.1 row 1 | `p_sh, p_el, p_wr`, declared "person space P" | `^{Person} P_{L12}`, `^{Person} P_{L14}`, `^{Person} P_{WR}` — **and** `^{Levelled} P_{WR}` where eqs (5.1)/(5.2) use it. The two superscripts are what disambiguate the one glyph | **APPLY** |
| C5-02 | `:253-256` + `:564-570`, Table 5.1 row `o` | `o`, "levelled world frame W … Chapter 4, translation column of `T_WO`" | `^{Levelled} P_{MappedMarker}ORG` | **APPLY** for the label. **The "comes from" cell is a substantive defect — §9 S-1** |
| C5-03 | Table 5.1 row `R_obj` | `R_obj`, "… rotation block of `T_WO`" | `^{Levelled}_{MappedMarker} R = G · S · (^{World}_{Object} R) · S`, `det +1` | **APPLY** for the label. **Provenance cell substantive — §9 S-1** |
| C5-04 | Table 5.1 row `w` | `w`, frame cell "levelled world frame W, **then P**" | `^{Levelled} P_{ŴR}` and `^{Person} P_{ŴR}` | **APPLY** |
| C5-05 | Table 5.1, two cells | `T_WO` | `^{World}_{Object} T` | **APPLY** |
| C5-06 | Table 5.1 caption | "after levelling by the calibrated gravity direction" | `^{Levelled}_{Unity} R = G`, **class 1, det +1**, left-multiplied — and the `S` swap, which the caption does not mention at all | **APPLY** |
| C5-07 | Table 5.1 rows `h`, `h_k` | declared "object frame O" | `^{MappedMarker} P_{WR}` | **APPLY** for the label. **The declared frame is wrong — §9 S-2 and §3.1** |
| C5-08 | Table 5.1 | `û, f̂, b, r, b̂, p_c, r_c, n₁, n₂, u⊥` | all `^{Person}` | **APPLY** |
| C5-09 | `:281`, eq (5.1) | `p_wr = o + R_obj h` | `^{Levelled} P_{WR} = ^{Levelled}_{MappedMarker} T · ^{MappedMarker} P_{WR}` | **APPLY** |
| C5-10 | `:288`, eq (5.2) | `h_k = R_obj,kᵀ(p_wr,k − o_k)` | `^{MappedMarker} P_{WR,k} = ^{MappedMarker}_{Levelled} T · ^{Levelled} P_{WR,k}` | **APPLY** |
| C5-11 | `:306-311`, the least-squares display | unlabelled | `Σ‖ ^{Levelled} P_{WR,k} − ^{Levelled}_{MappedMarker} T · ^{MappedMarker} P_{WR} ‖²` — the labels show why the rotation drops out | **APPLY** |
| C5-12 | `:314-315`, eq (5.3) | `h = (1/N) Σ h_k` | `^{MappedMarker} P_{WR}` | **APPLY** |
| C5-13 | `:320-321`, eq (5.4) | `h_new = (1−c) h_old + c h_k` | `^{MappedMarker}` | **APPLY** |
| C5-14 | `:355-356`, eq (5.5) | `û_new = …` | `^{Person}` | **APPLY** |
| C5-15 | `:367`, eq (5.6) | `p_wr = p_el + L2 f̂` | `^{Person} P_{WR} = ^{Person} P_{L14} + L_2 · ^{Person} f̂`; `L_2` keeps its letter | **APPLY** |
| C5-16 | `:380`, eq (5.7) | `w = o + R_obj h` | `^{Levelled} P_{ŴR}` | **APPLY** |
| C5-17 | `:390` (§5.4) and `:220` (§5.1) | "the fixed rigid body transformation of the scene calibration" — **no symbol at all** | `^{Person}_{Levelled} T`; establish it once in §2.2.2 and cite it in §5.1, §5.4, §5.6. *Note:* the audits did not separate {Levelled} from {Unity} at this site; C5-06's missing levelling/swap statement is what fixes the source frame, and `:529-530`'s "rotation block close to the identity … last column is the desk origin in person space" is consistent with {Levelled} | **APPLY** |
| C5-18 | `:403-404`, eq (5.8) | `‖p_el − p_sh‖ = L1` etc. | `^{Person}`; `L_1`, `L_2` keep their letters | **APPLY** |
| C5-19 | `:420-422`, eq (5.9) | `cos j = …` | `^{Person}` | **APPLY** |
| C5-20 | `:432-434`, eq (5.10) | `p_c = p_sh + L1 cos j b̂`, `r_c` | `^{Person}` | **APPLY** |
| C5-21 | `:443-445`, eq (5.11) | `p_el = p_c + r_c(cos s n₁ + sin s n₂)` | `^{Person}` | **APPLY** |
| C5-22 | `:456-458`, eq (5.12) | `u⊥ = û − (û·b̂)b̂`, `p_el` | `^{Person}` | **APPLY** |
| C5-23 | `:297`, Figure 5.3 caption | "the displacement from the object origin o to the measured wrist is read in the object axes" | name {MappedMarker} and {Levelled}; the direction described in words is already right | **APPLY** |
| C5-24 | `:477`, Figure 5.5 caption | no transforms | no label needed — AGREES as printed | **APPLY** |
| C5-25 | `:507` | `p_sh = (−0.16, 0.34, 1.32)` | `^{Person} P_{L12}` | **APPLY** |
| C5-26 | `:509` | `o = (−0.22, 0.08, 0.45)` | `^{Levelled} P_{MappedMarker}ORG` | **APPLY** |
| C5-27 | `:510-513` | `R_obj` 3×3 | `^{Levelled}_{MappedMarker} R` | **APPLY** |
| C5-28 | `:516` | `h = (0.01, −0.04, 0.05)` | `^{MappedMarker} P_{WR}` | **APPLY** |
| C5-29 | `:518-520` | `R_obj h = (0.01, 0.06, 0.04)` | `^{Levelled}_{MappedMarker} R · ^{MappedMarker} P_{WR}` | **APPLY** |
| C5-30 | `:520` | `w = o + R_obj h = (−0.21, 0.13, 0.48)` | `^{Levelled} P_{ŴR}` | **APPLY** |
| C5-31 | `:524-528` | the 4×4 scene-calibration matrix | `^{Person}_{Levelled} T` (see C5-17) | **APPLY** |
| C5-32 | `:531` | `w = (−0.19, −0.09, 1.04)`, four lines after C5-30, y sign changed | `^{Person} P_{ŴR}` — the two superscripts are what tell the reader these are one point in two frames | **APPLY** |
| C5-33 | `:535-553` | `b, r, b̂`; `cos j`; `p_c, r_c`; `û, u⊥`; `p_el` | all `^{Person}` | **APPLY** |
| C5-34 | `:529-530` | "its rotation block is close to the identity … its last column is the desk origin in person space" | `^{Person} P_{Levelled}ORG` | **APPLY** |
| C5-36 | `:207`, §5.1 | "while a hand holds the cube the wrist keeps a fixed position in **the object's frame**" | `^{MappedMarker} P_{WR}` | **APPLY** for the label; the phrase "the object's frame" is the prose face of §9 S-2 |
| C5-37 | Table 5.1 vs Chapter 4 §4.1 | `W` used for two frames 32.04° apart | **{World}** and **{Levelled}** | **APPLY** — dissolved by D-056 (§5) |
| C5-38 | §5.4 vs Chapter 6 eq (6.1) | the swap Chapter 5 silently depends on | the same matrix `S` (`carry.py:24` = the thesis's `S`; confirmed by the ch6/ch8 audit) — print the dependence | **APPLY** |

### 8.5 Chapter 6 — `build_ch6.py`

| item | location | present notation | assigned Craig form | status |
|---|---|---|---|---|
| C6-01 | `:271-275`, eq (6.1) | `p_U = S p_w` | `^{Unity} p = S · ^{World} p`, `det S = −1`, **no cancellation across it** | **IMPROPER** |
| C6-02 | `:271-275`, eq (6.1) | `R_U = S R_w S` | `^{Unity}_{MappedMarker} R = S · ^{World}_{Object} R · S` — a **similarity**; naming {MappedMarker} is what makes it statable, and the result is class 1 | **IMPROPER** (the map; the result is class 1) |
| C6-03 | `:273-275` | the printed numeric `S` | class 4; declared once in section 6 | **IMPROPER** |
| C6-04 | `:277`, and eqs (6.2)/(6.3) | `F` printed bare while acting **person→sensor**, the inverse of eq (3.1)'s definition | declare `F`'s direction at every appearance | **IMPROPER** — and X-1 is substantive: harmless only because `F` is an involution, which the thesis never states (§9 S-9) |
| C6-05 | `:191`, used `:283, 287` | `R_cam` | `^{World}_{Sensor} R` | **APPLY** |
| C6-06 | `:192`, used `:282, 287` | `t_cam` | `^{World} P_{Sensor}ORG` | **APPLY** |
| C6-07 | `:282`, `:410` | `S t_cam` | `^{Unity} P_{Sensor}ORG` | **APPLY** |
| C6-08 | `:282-283` | `A = S R_cam F` | `^{Unity}_{Person} R`, `det +1` — **both frames left-handed**; state that Craig's algebra carries over but his right-handed assumption does not | **APPLY** |
| C6-09 | `:198`, prose `:287, 289` | `T_WC` | `^{World}_{Sensor} T` | **APPLY** |
| C6-10 | `:199`, eq (6.2) at `:284-285` | `T_UP` | `^{Unity}_{Person} T`, with `^{Unity} P = ^{Unity}_{Person} T · ^{Person} P` | **APPLY** |
| C6-11 | `:287-290`, prose after (6.2) | "the standard chaining of homogeneous transformations" | — | **BLOCKED** — two of the three factors have `det −1` rotation blocks and are not homogeneous transforms in Craig's sense. Needs a corrected characterisation sentence, not a label |
| C6-12 | `:294-304`, eq (6.3) | `(S R_cam S)(S F)` | `^{Unity}_{Person} R = ^{Unity}_{MappedCamera} R · ^{MappedCamera}_{Person} R`, with `^{MappedCamera}_{Person} R = R_x(−90°)`, `det +1`. **The one honest way to write (6.2)/(6.3)**; matches `IntegratedSceneReceiver.cs:161-163` factor for factor | **APPLY** |
| C6-13 | `:277` vs `:306` | the two conjugation rules | — | **BLOCKED** — substantive (X-2): two mutually exclusive rules. Needs a new sentence of content (§9 S-3) |
| C6-14 | `:318-321`, eq (6.4) | `R_0, R_1, R_2, R_chain` | class-3 operators composed along the chain; order verified against `IntegratedSceneReceiver.cs:358-374` | **BLOCKED** — the operator reading is consistent, but U-2 (the frames of `R_0…R_2`) is not settled until §4.9's declaration is made |
| C6-15 | `:329, :331`, eq (6.5) | `R_bone = A R_chain R_rest` | — | **BLOCKED** — substantive (X-3): the written rotation carries the levelling and the printed equation does not (§9 S-4) |
| C6-16 | `:329, :331` | `R_rest` | either `^{model}_{bone} R` or a declared constant re-basing factor | **BLOCKED** — U-1, §4.9; author declaration |
| C6-17 | `:337` | "the receiver maps the streamed pelvis …" | AGREES; name the frames in words | **APPLY** |
| C6-18 | `:333` | the avatar proportion scaling | a scale, not a frame relation; no label | **APPLY** |
| C6-19 | `:345` | "It rotates that node by the shortest …" | `^{Levelled}_{Unity} R = G`, class 1, `det +1`, 32.0368°. The accompanying **floor drop is the translation that carries {Levelled}'s origin to {Scene}'s**: `^{Scene}_{Levelled} T`, identity rotation, `^{Scene} P_{Levelled}ORG = (0, d, 0)`, `d = 0.716215 m` (r6b). Print the node placement as that explicit transform (D-060), not as an unnamed presentational nudge | **APPLY** — *text changed by D-060: the third pass called the drop "a presentational translation, not a frame". The **translation** is still not a frame; its **destination** is, and it is {Scene}* |
| C6-20 | `:429-434`, worked example | `L` (the levelling rotation), then `p_scene = L p_U + (0, 0.72, 0)` | `^{Levelled} P = ^{Levelled}_{Unity} R · ^{Unity} P`, then `^{Scene} P = ^{Scene}_{Levelled} T · ^{Levelled} P`; the bare `L` retires. The printed `(0, 0.72, 0)` is `^{Scene} P_{Levelled}ORG` rounded from `d = 0.716215 m` | **APPLY** |
| C6-21 | `:397-402` | `R_cam`, `t_cam` numerics | `^{World}_{Sensor} R`, `^{World} P_{Sensor}ORG` | **APPLY** |
| C6-22 | `:405-410` | `A` numeric, `S t_cam` numeric | `^{Unity}_{Person} R`, `^{Unity} P_{Sensor}ORG` | **APPLY** |
| C6-23 | `:412-416` | `q = (0.03, −0.18, 0.99) m`; `p_U = A q + S t_cam` | `^{Person} q`; `^{Unity} P = ^{Unity}_{Person} R · ^{Person} q + ^{Unity} P_{Sensor}ORG` | **APPLY** |
| C6-24 | `:417` | "Undoing the flip gives …", the three-step narration | name the frames at each step | **APPLY** |
| C6-25 | `:442-448` | `R = R_camᵀ`, `t = (0.02, 0.19, 0.55)` | `^{Sensor}_{World} R`, `^{Sensor} P_{World}ORG`; the step is `^{Sensor}_{Object} T = ^{Sensor}_{World} T · ^{World}_{Object} T` | **APPLY** |
| C6-26 | `:452-456` | `p_W = S p_U` | the **same bare `S` used in the opposite direction from eq (6.1)** — banned under D-054; write the direction explicitly | **IMPROPER** |
| C6-27 | `:258` | "bringing that pose back into camera coordinates undoes the axis swap … and applies the calibrated anchor" | `^{Sensor}_{Object} T = ^{Sensor}_{World} T · ^{World}_{Object} T`, with `^{World}_{Object} R = S · ^{Unity}_{MappedMarker} R · S`; order verified at `v2/common/object_link.py:109-111` | **APPLY** |
| C6-28 | `:251`, Table 6.1 | "pelvis position in person space" etc. | `^{Person} P` | **APPLY** |
| C6-29 | `:260` | "the object pose by a straight line …" | name the frame | **APPLY** |
| C6-30 | `:306` | "the first factor is the orientation the display already uses to place the sensor body" | `^{Unity}_{MappedCamera} R`; AGREES as written | **APPLY** |
| C6-31 | `:452-456` | `p_C = R p_W + t` | `^{Sensor} P = ^{Sensor}_{World} R · ^{World} P + ^{Sensor} P_{World}ORG` | **APPLY** |
| C6-32 | `:474-476`, Table 6.2 | "Link \| swap undone, …" rows; and `:475`, "pelvis (0.2, −20.5, 38.9) cm **in display axes**; (0.0, 74.8, 43.8) cm **in the scene**" | the frame at each row: the Link row is `^{Sensor}`, "display axes" is **{Unity}**, "in the scene" is **{Scene}**. **This row is the thesis's own proof that it needs both frames** — one physical point, two triples, two names, already printed | **APPLY** |
| C6-33 | `:267`, Figure 6.4 caption | "**the four** coordinate frames" | — | **BLOCKED** — the definite article asserts a completeness the chapter does not keep: **eight** of the thirteen frames appear in Chapter 6 ({Sensor}, {World}, {Unity}, {Person}, {MappedMarker}, {MappedCamera}, {Levelled}, **{Scene}**). A caption claim, not a label. *Count updated by D-060* |
| **C6-34** | **not printed today.** Anchor it at `:345` (§6.4, where the levelling and the drop are described) and cite it from `:434` and `:475` | — (the drop appears only as the literal `(0, 0.72, 0)` inside the §6.5 worked example, with no symbol and no frame pair) | `^{Scene}_{Levelled} T = [ I₃ , (0, d, 0) ; 0 0 0 , 1 ]`, `d = 0.716215 m` (r6b) / `0.709312 m` (r7), with `d = origin_above_tabletop_m + DeskThick + LegH` exactly (residual 0.00e+00; `DeskThick + LegH = 0.72` at `check_unity_log.py:41`) | **APPLY** — **a new printed transform required by D-060**: "Represent the Levelled to Scene relation as an explicit homogeneous transform with identity rotation and the measured floor drop translation." This is the only row in the table that adds a transform rather than relabelling one. **Escalated**: which `d` the thesis prints — see §10 item 3 |

### 8.6 Chapters 7 and 8 — `build_ch7.py`, `build_ch8.py`

Neither chapter prints a rotation-matrix or homogeneous-transform symbol. Every
transform is invoked in prose or a caption, so what these rows need is frame
**names**, not new symbols.

| item | location | present notation | assigned form | status |
|---|---|---|---|---|
| C7-01 | `build_ch7.py:293`, §7.3 | "the calibrated camera-to-scene mapping"; "the same Unity world frame" | — | **BLOCKED** — substantive (X-4): the map is orthogonal with `det = −1` and is **not a rotation**, and the frame-identity claim is false (§9 S-5) |
| C7-02 | `:286`, §7.2 | "invariant under the levelling rotation" | `^{Levelled}_{Unity} R = G`, `det +1` — so the invariance claim about Tables 7.1 and 7.2 **is correct**; and the next sentence about non-invariant quantities is what makes {Levelled} a frame (§4.5) | **APPLY** |
| C7-03 | `:251`, `:274`, Figures 7.1/7.2 captions | "this frame" | **{Levelled}**: origin at the desk marker, +y calibrated gravity up, left-handed (`eval_rail_scenario.py:51-58`) | **APPLY** |
| C7-04 | `:320`, `:325`, Figures 7.3/7.4 captions | "the same Unity world frame" | **{Scene}** — origin at the drawn floor, axes exactly {Levelled}'s, left-handed, y up along calibrated gravity. The captions must (i) name {Scene}, (ii) say it shares {Levelled}'s axes and differs only by the floor drop, and (iii) reconcile the figure axis labels, which read `Unity x/y/z` (`make_ch7_valid_joint_figures.py:37-39`) while plotting {Scene} components. *Figures 7.1/7.2 are in {Levelled} (C7-03), so the two figure pairs are the **same axes at two origins**: identical shapes, directions, tilts and distances; only absolute components differ, by `(0, 0.716215, 0)` m* | **APPLY** — unblocked by D-060 |
| C7-05 | `:377` | "the proxy and reconstructed wrist are …" | Table 7.8 is computed in **{Sensor}** (`evaluate_ch7_restructured.py:265-271`), Table 7.9 in **{Person}** (`eval_labeled_recovery.py:122`). `F` is an isometry so every distance agrees; name both frames instead of asserting one | **APPLY** |
| C7-06 | `:353-372`, §7.3.3 | the wrist-to-marker separations | **{Levelled}** | **APPLY** |
| C7-07a | `build_ch7.py:294`, eq (7.5) | `e_{k,t} = ‖p_{k,t}^Unity − p_{k,t}^measured‖` | `e_{k,t} = ‖ ^{Scene} P_{k,t}^{rig} − ^{Scene} P_{k,t}^{meas} ‖`. **Both operands are in {Scene}**, verified: `evaluate_ch7_restructured.py:133` and `:139` add the identical `offset` before `:141` differences them, so the drop cancels from `e` even though it does not cancel from the plotted coordinates. The printed right superscripts name **provenance**, not frame; the word "Unity" in `p^Unity` must become a provenance word (`rig`, or `rendered`) with the frame moved to the left superscript, or the reader will read it as equation (6.1)'s {Unity} | **APPLY** — unblocked by D-060 |
| C7-07b | `build_ch7.py:366`, eq (7.6) | `e_{m,k,t} = ‖p_{m,k,t}^masked − p_{k,t}^unmasked‖` | `e_{m,k,t} = ‖ ^{Person} P_{m,k,t}^{masked} − ^{Person} P_{k,t}^{unmasked} ‖`. **This is a different frame from (7.5) and was never covered by the Unity trace.** Traced here: `evaluate_ch7_restructured.py:184` builds `shoulders` by applying the y-flip `[1, −1, 1]` (= `F`) to the filtered landmark CSV, putting them in **{Person}**; `:153-162` `fk` composes `shoulders[i] + L · (root @ dir)` with `root = recompose_zxy(a[:3]) = ^{Person}_{L24} R`, so both `reference` (`:185`) and `points` (`:226`) are {Person} positions; `:231` differences them. **Nothing in §7.4 enters any Unity frame** | **APPLY** — *newly split out of the old single C7-07 row; see §8.8's reconciliation* |
| C7-08 | `:233-239`, eqs (7.2)-(7.4) | the PCA line fit; `c`, `C`, `u` | **{Levelled}**; `C` and `u` keep their letters | **APPLY** |
| C7-09 | `:240` | "the physical route is not registered into the …" | AGREES; name the frame | **APPLY** |
| C8-01 | `build_ch8.py:164` | "live it reads the newest …" | `^{Sensor}_{Object} T = ^{Sensor}_{World} T · ^{World}_{Object} T` after the conjugation un-swap (`object_link.py:109-111`) | **APPLY** |
| C8-02 | `:148`, Table 8.1 row | "newest published marker …" | name the frame | **APPLY** |
| C8-03 | `:174` and Figure 8.3 caption `:206` | the chain and the projection | the chain is built in **{Person}**, the projection is in **{Sensor}** | **APPLY** |
| C8-04 | `:164` | "the two capabilities marked as a new data path" | AGREES | **APPLY** |

### 8.7 Appendices — `build_appendix.py`

| item | location | present notation | assigned form | status |
|---|---|---|---|---|
| A-D01 | Appendix D.1, before eq (D.1) | bare `p` | `^{Sensor} P` | **APPLY** |
| A-D02 | Appendix D.3, eq (D.2) | bare `p` | `^{Sensor} P` | **APPLY** |
| A-D03 | Appendix D.2, `:237` | "the known transformation between the two imagers" — no symbol, frame unnamed | **no label, and none needed** — the transform exists only inside the vendor library (`rs.align(rs.stream.color)`, `realtime_person.py:79`; see §6.1). State that only the aligned colour-optical frame {Sensor} is used downstream | **APPLY** |
| A-D04 | Appendix D.3, prose | "a separate fixed axis flip, developed in Section 3.1" | `F`, class 4 — name its direction | **IMPROPER** |
| A-E01 | Appendix E.2 | bare `R`, bare `t` | `^{Sensor}_{World} R`, `^{Sensor}_{Wall} R`, `^{Sensor}_{Object} R`; `^{Sensor} P_{marker}ORG` — the three instances of §2.4's "marker's own frame" rule | **APPLY** |
| A-E02 | Appendix E.3, eq (E.1) | `R = I + sinθ[w]× + (1−cosθ)[w]×²` | Rodrigues: Craig's `R_K(θ)`, written `R(ŵ, θ)`, **no frame pair**; the *instance* in E.4 is `^{Sensor}_{Object} R` | **OPERATOR** |
| A-E03 | Appendix E.4, Table E.1 header | "Translation `t` (m)" | `^{Sensor} P_{marker}ORG` | **APPLY** |
| A-E04 | Appendix E.4 | bare `R` (twice) | `^{Sensor}_{Object} R` | **APPLY** |
| A-E05 | Appendix E.4 | `w = (1.00, 0.00, 0.03)` | `^{Sensor} ŵ`; `w` keeps its letter | **APPLY** |
| A-E06 | Appendix E.4 | "the third column is the marker's own outward normal in the camera frame" | `^{Sensor} Ẑ_{Object}` | **APPLY** |
| A-E07 | Appendix E.2 | "the lobe whose in-plane up axis better agrees with an estimate of the gravity direction" | `^{Sensor} ĝ` | **APPLY** |
| A-G01 | Appendix G.1, eq (G.1) | `p* = z* p / p_z` | `^{Person} P`, `^{Person} P*`; **the rescaling is a class-3 operator**. Frame confirmed at `build_appendix.py:393`: "The rules operate in person space P" | **OPERATOR** |

### 8.8 Counts

| status | rows | which |
|---|---|---|
| **APPLY** | **161** | ready for the relabelling pass; grouped by builder file in §8.9 |
| **OPERATOR** | **8** | C3-26, C3-27, C3-28, C3-33, C3-39, C3-48, A-E02, A-G01 |
| **IMPROPER** | **10** | C2-07, C2-10, C3-01, C3-35, C6-01, C6-02, C6-03, C6-04, C6-26, A-D04 (three distinct maps — `F`, `S`, `M` — at ten printed sites) |
| **BLOCKED** | **10** | C3-22, C3-52, C4-20, C6-11, C6-13, C6-14, C6-15, C6-16, C6-33, C7-01 |
| **total rows** | **189** | |

**Reconciliation against the third pass**, so the movement is auditable rather
than asserted. The third pass reported APPLY 154, OPERATOR 8, IMPROPER 10,
BLOCKED 15, total 187.

| change | rows | effect |
|---|---|---|
| **D-060** unblocks the three rows §4.3 was blocking | F2.4b, C7-04, C7-07 | BLOCKED 15 → 12, APPLY +3 |
| **D-058** declares equation (4.3)'s input to be {Unity}, which was the fourth and fifth blocked author declaration | C4-08, C4-09 | BLOCKED 12 → 10, APPLY +2 |
| **D-060** requires a transform to be printed that the thesis does not print today: `^{Scene}_{Levelled} T`, identity rotation, floor-drop translation | **C6-34, new row** | APPLY +1, total 187 → 188 |
| The old single row C7-07 covered two equations in two different sections and **two different frames**; it is split, and equation (7.6) is traced here for the first time | **C7-07a** (eq 7.5, {Scene}) and **C7-07b** (eq 7.6, {Person}) | APPLY +1, total 188 → 189 |
| | **net** | **APPLY 154 → 161, OPERATOR 8, IMPROPER 10, BLOCKED 15 → 10, total 187 → 189** |

*If the author prefers to count only the three rows the Unity question was
blocking and to leave C4-08 / C4-09 blocked pending a separate confirmation, the
counts are **APPLY 157, BLOCKED 12** on 187 rows. This file takes D-058 at its
word, because D-058 is SETTLED and says the declaration explicitly. Listed in
§10 as a choice, not hidden in the arithmetic.*

Per section: §8.1 Chapter 2, 19 rows; §8.2 Chapter 3, 52; §8.3 Chapter 4, 21;
§8.4 Chapter 5, 37; §8.5 Chapter 6, 34; §8.6 Chapters 7 and 8, 14; §8.7 the
appendices, 12. Total 189.

**Of the 10 BLOCKED rows: six are substantive defects** (C3-22, C3-52, C4-20,
C6-13, C6-15, C7-01) and belong to section 9; **three await an author
declaration** (C6-11's corrected characterisation sentence, C6-14 and C6-16 — the
frames of `R_0…R_2` and `R_rest`, section 4.9); and **one is a caption
completeness claim** (C6-33). **No row is blocked on a frame question any more.**

### 8.9 THE DELIVERABLE — the 161 APPLY rows grouped by builder file, in line order

This is the grouping the relabelling pass consumes. One group per file, rows in
**line order**, so a pass can open one builder and work top to bottom. The
"assigned" column is the Craig form to write; the full present-notation, evidence
and reasoning for every row are in §8.1-§8.7 under the same item id.

**Read §7 first** (Craig's conventions and the four status marks) and **§9 last**
(the substantive defects, which this pass must not touch). **OPERATOR, IMPROPER
and BLOCKED rows are deliberately absent from these groups**; they are listed per
file at the end of each group so that a pass working through a file knows what to
step over and why.

**Line-number drift found and corrected in this pass** (the third pass reused the
audits' numbers; these five had moved): **C5-36** is `build_ch5.py:218`, not
`:207`; **C5-23** is `:298`, not `:297` (`:297` is the image, `:298` the caption);
**C5-24** is `:478`, not `:477`; **C5-17**'s sites are `:286`, `:390` and `:523`,
not `:220` and `:390`; **C4-21** is `build_ch4.py:171`. Table 5.1's rows are given
individually below (`:254`-`:270`, caption `:271`) instead of as the block
`:253-256`. Everything else was spot-checked and stands.

#### 8.9.1 `build_ch2.py` — 16 APPLY rows

| # | item | line | present | assigned |
|---|---|---|---|---|
| 1 | F2.4b | `:213`, `:217` | "The Unity frame **U** at the root of the avatar rig" | name **{Scene}**; corrected wording in §8.1.1, **proposed not applied** |
| 2 | C2-01 | `:219-220` | `T_AB` | `^{A}_{B} T`, with `^{A} P = ^{A}_{B} T ^{B} P` |
| 3 | C2-02 | `:226` | `T_CW` (Table 2.2 row 1) | `^{Sensor}_{World} T` |
| 4 | C2-03 | `:227` | `T_C,wall` (row 2) | `^{Sensor}_{Wall} T` |
| 5 | C2-04 | `:228` | `T_CO` (row 3) | `^{Sensor}_{Object} T` |
| 6 | C2-05 | `:229` | `T_WO = T_CW⁻¹ T_CO` (row 4) | `^{World}_{Object} T = ^{World}_{Sensor} T · ^{Sensor}_{Object} T`, with `^{World}_{Sensor} T = (^{Sensor}_{World} T)⁻¹` stated separately |
| 7 | C2-06 | `:230` | `T_WC = T_CW⁻¹` (row 5) | `^{World}_{Sensor} T` |
| 8 | C2-08 | `:232` | `T_root` (row 7) | `^{Person}_{L24} T` |
| 9 | C2-09 | `:233` | `T_sh`, `T_el` (row 8) | `^{L24}_{L12} T`, `^{L12}_{L14} T`; left pair `^{L24}_{L11} T`, `^{L11}_{L13} T` |
| 10 | C2-15 | `:235` | Table 2.2 caption | restate with names; **exclude `F` and `S` explicitly** (class 4, not transformations) |
| 11 | C2-11 | `:244-247` | `M̄ = U Σ Vᵀ` | keep `M̄`, `U`, `Σ`, `V` generic; label the instantiation `^{Sensor}_{World} M̄` |
| 12 | C2-12 | `:249-251` | eq (2.1) | stays generic `^{A}_{B} R`; instantiated on `^{Sensor}_{World} R`, `^{Sensor}_{Wall} R`, `^{World}_{Object} R`. `U` keeps its letter |
| 13 | C2-16 | `:263` | Table 2.3, wall pose in the world | `^{World}_{Wall} T = ^{World}_{Sensor} T · ^{Sensor}_{Wall} T` (frames cancel) |
| 14 | C2-17 | `:264` | Table 2.3, camera pose in the world | `^{World}_{Sensor} T` |
| 15 | C2-18 | `:265` | Table 2.3, gravity direction — no symbol | `^{World} ĝ` — column 2 of `^{World}_{Wall} R` (`calibrate_scene.py:148`) |
| 16 | C2-13 | `:285` | "the pose of the marker in the camera frame C" | `^{Sensor}_{Object} T` |

*Step over in this file:* **IMPROPER** C2-07 (`:231`, `F`) and C2-10 (`:234`, `S`)
— class 4, declared once in §6, never Craig notation.

#### 8.9.2 `make_ch2_frames_fig.py` — 1 APPLY row

| # | item | line | present | assigned |
|---|---|---|---|---|
| 1 | C2-14 | `:103-107` (panel a), `:205-208` (panel b) | `T_{C,wall}`, `T_{CO}`, `T_{CW}`, `T_{WO}` on the Figure 2.5 arrows | `^{Sensor}_{Wall} T`, `^{Sensor}_{Object} T`, `^{Sensor}_{World} T`, `^{World}_{Object} T`; **arrow directions are already correct** |

*Also in this file, and NOT a relabelling item:* **§9 S-7**, the 45 mm / 50 mm
scale mismatch in panel (b) (`:116-120`, with `:56, 62`, `:137, 164`, `:140-142`).
A relabelling pass must not touch it.

#### 8.9.3 `build_ch3.py` — 42 APPLY rows

| # | item | line | present | assigned |
|---|---|---|---|---|
| 1 | C3-02 | `:197` | "columns are the child's axes in the parent's coordinates" | `^{A}_{B} R = [ ^{A} X̂_B  ^{A} Ŷ_B  ^{A} Ẑ_B ]` |
| 2 | C3-03 | `:197` | "the translation part is a 3-vector t" | `^{A} P_{B}ORG`, "expressed in {A}" |
| 3 | C3-04 | `:199-201` eq (3.2) | `T = [R t; 0 1]` | `^{A} P = ^{A}_{B} T ^{B} P` |
| 4 | C3-05 | `:205` eq (3.3) | `v_local = R_parentᵀ v` | `^{B} v = ^{B}_{A} R ^{A} v`, `^{B}_{A} R = (^{A}_{B} R)ᵀ` |
| 5 | C3-06 | `:209-212` eq (3.4) | `p_child = Rᵀ(p_parent − t)` | `^{B} P = (^{A}_{B} R)ᵀ(^{A} P − ^{A} P_{B}ORG)`; `^{B}_{A} T = (^{A}_{B} T)⁻¹` |
| 6 | C3-07 | `:221` eq (3.5) | `T_root` | `^{Person}_{L24} T` |
| 7 | C3-08 | `:222` eq (3.5) | `T_sh,r` / `T_sh,l` | `^{L24}_{L12} T` / `^{L24}_{L11} T` |
| 8 | C3-09 | `:223` eq (3.5) | `T_el,r` / `T_el,l` | `^{L12}_{L14} T` / `^{L11}_{L13} T` |
| 9 | C3-10 | `:225-236` | `R_sh,r` | `^{L12}_{L14} R` — today the subscript names the **reference** frame while `R_root`'s names the **described** frame; the Craig form removes the contradiction |
| 10 | C3-11 | `:237` eq (3.6) | `T_arm,r = T_root T_sh,r T_el,r` | `^{Person}_{L14} T = ^{Person}_{L24} T · ^{L24}_{L12} T · ^{L12}_{L14} T` — cancellation visible; the third name "arm,r" for {L14} disappears |
| 11 | C3-12 | `:239` | "the inverse transformations … carry it into the frame where its joint is solved" | `^{L24}_{Person} T`, `^{L12}_{Person} T`, `^{L14}_{Person} T` |
| 12 | C3-21 | `:257-258` Figure 3.4 caption | "the finished frame at the L24 origin" | name **{L24}** in the caption |
| 13 | C3-14 | `:260` eq (3.7) | `x̂ = (p24−p23)/‖·‖` | `^{Person} X̂_{L24}`, from `^{Person} P_{23}`, `^{Person} P_{24}` |
| 14 | C3-15 | `:265` eq (3.8) | `s = p12 − p24` | `^{Person} s` |
| 15 | C3-16 | `:270` eq (3.9) | `ẑ = (x̂ × s)/‖·‖` | `^{Person} Ẑ_{L24}` |
| 16 | C3-17 | `:279` eq (3.10) | `ŷ = ẑ × x̂` | `^{Person} Ŷ_{L24}` |
| 17 | C3-18 | `:284` eq (3.11) | `R_root = [x̂ ŷ ẑ]` | `^{Person}_{L24} R` |
| 18 | C3-19 | `:288` eq (3.12) | `T_root = [R_root, p24; 0 1]` | `^{Person}_{L24} T`, `^{Person} P_{L24}ORG = ^{Person} P_{24}` |
| 19 | C3-20 | `:290` | the T-pose reference columns | `^{Person}_{L24} R` at the reference configuration |
| 20 | C3-23 | `:327` eq (3.13) | `T_sh,r = [I, R_rootᵀ(p12−p24); 0 1]` | `^{L24}_{L12} T`, with `^{L24}_{L12} R = I₃` and `^{L24} P_{L12}ORG` |
| 21 | C3-24 | `:337` eq (3.14) | `T_el,r = [R_sh,r, R_rootᵀ(p14−p12); 0 1]` | `^{L12}_{L14} T`, `^{L12} P_{L14}ORG` |
| 22 | C3-25 | `:344-348` | `v = p14 − p12`, `v_local = R_rootᵀ v` | `^{Person} v`, `^{L24} v` |
| 23 | C3-29 | `:388-391` §3.4.1 | "Its pose is the pair (R_root, p24)" | `( ^{Person}_{L24} R , ^{Person} P_{L24}ORG )` |
| 24 | C3-30 | `:397` eq (3.18) | `R_sh,r = Ry(t_y) Rz(t_z) Rx(t_t)` | `^{L12}_{L14} R` |
| 25 | C3-31 | `:403-405` eq (3.19) | `â = R_sh,r x̂` | `^{L12} â` = **the first column of** `^{L12}_{L14} R`. Glyph note: `x̂` is `(1,0,0)` here and `^{Person} X̂_{L24}` eleven equations earlier |
| 26 | C3-32 | `:413`, `:416` eqs (3.20)-(3.21) | `t_z = asin(a_y)`, `t_y = atan2(−a_z, a_x)` | scalars read from `^{L12} â`'s components |
| 27 | C3-34 | `:430` eq (3.23) | `t_t = atan2(−f′_y, f′_z)` | scalar read from `^{L12} f′`'s components |
| 28 | C3-36 | `:439-440` §3.4.3 | `R_arm,r = R_root Ry Rz Rx` | `^{Person}_{L14} R = ^{Person}_{L24} R · ^{L24}_{L12} R · ^{L12}_{L14} R` (the middle factor is I₃) |
| 29 | C3-37 | `:441-442` §3.4.3 | `ĝ = R_arm,rᵀ(p16−p14)` | `^{L14} ĝ = (^{Person}_{L14} R)ᵀ(^{Person} P_{16} − ^{Person} P_{14})/‖·‖` |
| 30 | C3-38 | `:444-445` eq (3.24) | `e_z = asin(g_y)`, `e_y = atan2(−g_z, g_x)` | scalars read from `^{L14} ĝ`'s components |
| 31 | C3-40 | `:468-478` Table 3.1 | columns "Camera frame C (m)", "Person space P (m)" | `^{Sensor} P_i`, `^{Person} P_i` — the one place in Chapter 3 that already carries its frame |
| 32 | C3-41 | `:481-485` | `p23, p24, p12` numeric | `^{Person} P_{23}`, `^{Person} P_{24}`, `^{Person} P_{12}` |
| 33 | C3-42 | `:487-490` | `x̂, ẑ, ŷ` numeric | `^{Person} X̂_{L24}`, `^{Person} Ẑ_{L24}`, `^{Person} Ŷ_{L24}` |
| 34 | C3-43 | `:495-498` | `R_root` 3×3 numeric | `^{Person}_{L24} R` |
| 35 | C3-44 | `:501-506` | `T_root` 4×4 numeric | `^{Person}_{L24} T` |
| 36 | C3-45 | `:507-512` | `T_sh,r` 4×4 numeric | `^{L24}_{L12} T` |
| 37 | C3-46 | `:520-525` | `v`, `v_local`, `â` | `^{Person} v`, `^{L24} v`, `^{L12} â` |
| 38 | C3-47 | `:526` | `f = R_rootᵀ(p16−p14)` | `^{L12} f` |
| 39 | C3-49 | `:536` | `ĝ = (0.94, 0.00, 0.34)` | `^{L14} ĝ` |
| 40 | C3-50 | `:544-548` | `T_el,r` 4×4 numeric | `^{L12}_{L14} T`; last column verified equal to `v_local` |
| 41 | C3-51 | `:549-556` | the closing check | `^{Person} P_{L14}ORG = ^{Person}_{L14} T (0,0,0,1)ᵀ`; `^{L14} P_{16} = (^{Person}_{L14} T)⁻¹ ^{Person} P_{16}` |
| 42 | C3-13 | chapter-wide | the self-inconsistent subscript convention | resolved wholesale by rows 6-10 above; **verify at the end of the file, not at a line** |

*Step over in this file:* **OPERATOR** C3-26 (`:353`), C3-27 (`:356-363`), C3-28
(`:374-386`), **C3-33 (`:424`, eq 3.22 — D-057, verified in §0)**, C3-39 (§3.4.3,
unprinted), C3-48 (`:532`) — each carries **no frame pair**, and the surrounding
prose must say so. **IMPROPER** C3-01 (`:188`, `F`), C3-35 (`:433-435`, `M`).
**BLOCKED** C3-22 (`:294`, Figure 3.5's caption — §9 S-6) and C3-52 (`:197`, "no
matrix is ever inverted numerically" — §9 S-10). *C3-52 sits in the same source
line as rows 1 and 2 of this group: relabel the frame notation there, and leave
the inversion claim alone.*

#### 8.9.4 `build_ch4.py` — 20 APPLY rows

| # | item | line | present | assigned |
|---|---|---|---|---|
| 1 | C4-01 | `:145-146` | `T_CW` | `^{Sensor}_{World} T` |
| 2 | C4-02 | `:146-147` | `T_CO` | `^{Sensor}_{Object} T` |
| 3 | C4-03 | `:147-148` | `T_WO` | `^{World}_{Object} T` |
| 4 | C4-04 | `:150` eq (4.1) | `T_WO = T_CW⁻¹ T_CO` | `^{World}_{Object} T = ^{World}_{Sensor} T · ^{Sensor}_{Object} T` |
| 5 | C4-05 | `:154-156` eq (4.2) | bare `T`, `R`, `t`; `T⁻¹ = [Rᵀ, −Rᵀt; 0 1]` | `^{B}_{A} T = (^{A}_{B} T)⁻¹`; instantiated `^{World}_{Sensor} T` |
| 6 | C4-06 | `:158-159` | `T_WC` | `^{World}_{Sensor} T` |
| 7 | C4-07 | `:161` | "the camera frame enters the chain twice … the two contributions cancel" | now visible in row 4's form |
| 8 | C4-10 | `:167` | "a rolling chordal mean, which is equation (2.1) over a short window" | cross-reference to C2-12's generic form |
| 9 | C4-21 | `:171` Figure 4.2 caption | "the object track in the world frame … one panel per world axis" | `^{World} P_{Object}ORG` per axis |
| 10 | **C4-08** | `:181-185` eq (4.3) | `p_i`, `p_last` | **`^{Unity} P_{Object}ORG(i)`** — **D-058**; also correct the prose that calls it "the world-frame track". No number changes (`S` is orthogonal) |
| 11 | **C4-09** | `:184` eq (4.3) | `angle(R_lastᵀ R_i)` | **`angle(^{MappedMarker(last)}_{MappedMarker(i)} R)`** — D-058; state that the reference frame cancels out of the result |
| 12 | C4-19 | `:190-192` | `v_max`, `w_max` | scalars; no frame of their own — the vectors they bound carry the label, so they follow rows 10-11 into **{Unity}** |
| 13 | C4-11 | `:201-204` | `M̄` numeric | `^{Sensor}_{World} M̄` |
| 14 | C4-12 | `:207-208` | `T_CW` numeric | `^{Sensor}_{World} T` |
| 15 | C4-13 | `:210` | gravity, **no symbol at all** | `^{World} ĝ` |
| 16 | C4-14 | `:213` | `−Rᵀ t`, bare `R`, bare `t` | `^{World} P_{Sensor}ORG = − ^{World}_{Sensor} R · ^{Sensor} P_{World}ORG` |
| 17 | C4-15 | `:217` | `t_CO` | `^{Sensor} P_{Object}ORG` |
| 18 | C4-16 | `:220-222` | `R_WO = Rᵀ R_CO`; `t_WO = Rᵀ t_CO + t_WC` (bare `Rᵀ` beside a labelled `R_CO`) | `^{World}_{Object} R = ^{World}_{Sensor} R · ^{Sensor}_{Object} R`; `^{World} P_{Object}ORG = ^{World}_{Sensor} R · ^{Sensor} P_{Object}ORG + ^{World} P_{Sensor}ORG` |
| 19 | C4-17 | `:225-230` | `t_WO`, `R_WO` numerics | `^{World} P_{Object}ORG`, `^{World}_{Object} R` |
| 20 | C4-18 | `:234` | "projected onto the measured gravity direction" | `^{World} ĝ` |

*Step over in this file:* **BLOCKED** C4-20 (`:143`, Figure 4.1's caption — §9
S-8: the caption claims the calibrated anchor, the figure code
`make_ch4_experiment_fig.py:72, 87` draws the per-frame detection).

#### 8.9.5 `build_ch5.py` — 37 APPLY rows

Every Chapter 5 transform is labellable, because the frames it needs —
**{Levelled}** and **{MappedMarker}** — are named in §3. **Two of these rows carry
substantive defects in their "frame" or "comes from" cell (§9 S-1, S-2): relabel
the symbol, and leave the defect for the content pass.**

| # | item | line | present | assigned |
|---|---|---|---|---|
| 1 | C5-36 | `:218` §5.1 | "while a hand holds the cube the wrist keeps a fixed position in **the object's frame**" | `^{MappedMarker} P_{WR}`; the phrase is the prose face of §9 S-2 |
| 2 | C5-01 | `:254` Table 5.1 row 1 | `p_sh, p_el, p_wr`, declared "person space P" | `^{Person} P_{L12}`, `^{Person} P_{L14}`, `^{Person} P_{WR}` — **and** `^{Levelled} P_{WR}` where eqs (5.1)/(5.2) use it |
| 3 | C5-02 | `:255` Table 5.1 row `o` (+ `:564-570`) | `o`, "levelled world frame W … Chapter 4, translation column of `T_WO`" | `^{Levelled} P_{MappedMarker}ORG`. **The "comes from" cell is §9 S-1** |
| 4 | C5-03 | `:256` Table 5.1 row `R_obj` (+ `:564-570`) | `R_obj`, "… rotation block of `T_WO`" | `^{Levelled}_{MappedMarker} R = G · S · (^{World}_{Object} R) · S`, `det +1`. **Provenance cell is §9 S-1** |
| 5 | C5-07 | `:257`, `:258` Table 5.1 rows `h`, `h_k` | declared "object frame O" | `^{MappedMarker} P_{WR}`. **The declared frame is wrong — §9 S-2 and §3.1** |
| 6 | C5-08 | `:261`, `:265`, `:267`, `:268`, `:270` | `û, f̂, b, r, b̂, p_c, r_c, n₁, n₂, u⊥` | all `^{Person}` |
| 7 | C5-04 | `:264` Table 5.1 row `w` | `w`, frame cell "levelled world frame W, **then P**" | `^{Levelled} P_{ŴR}` and `^{Person} P_{ŴR}` |
| 8 | C5-06 | `:271` Table 5.1 caption | "after levelling by the calibrated gravity direction" | `^{Levelled}_{Unity} R = G`, **class 1, det +1**, left-multiplied — and the `S` swap, which the caption does not mention at all |
| 9 | C5-09 | `:281` eq (5.1) | `p_wr = o + R_obj h` | `^{Levelled} P_{WR} = ^{Levelled}_{MappedMarker} T · ^{MappedMarker} P_{WR}` |
| 10 | C5-17 | `:286` §5.2 (also `:390`, `:523`) | "the fixed transformation of the scene calibration" — **no symbol at all** | `^{Person}_{Levelled} T`; establish it once and cite it at all three sites |
| 11 | C5-10 | `:288` eq (5.2) | `h_k = R_obj,kᵀ(p_wr,k − o_k)` | `^{MappedMarker} P_{WR,k} = ^{MappedMarker}_{Levelled} T · ^{Levelled} P_{WR,k}` |
| 12 | C5-23 | `:298` Figure 5.3 caption | "the displacement from the object origin o to the measured wrist is read in the object axes" | name **{MappedMarker}** and **{Levelled}**; the direction described in words is already right |
| 13 | C5-11 | `:306-311` least-squares display | unlabelled | `Σ‖ ^{Levelled} P_{WR,k} − ^{Levelled}_{MappedMarker} T · ^{MappedMarker} P_{WR} ‖²` — the labels show why the rotation drops out |
| 14 | C5-12 | `:314-315` eq (5.3) | `h = (1/N) Σ h_k` | `^{MappedMarker} P_{WR}` |
| 15 | C5-13 | `:320-321` eq (5.4) | `h_new = (1−c) h_old + c h_k` | `^{MappedMarker}` |
| 16 | C5-14 | `:355-356` eq (5.5) | `û_new = …` | `^{Person}` |
| 17 | C5-15 | `:367` eq (5.6) | `p_wr = p_el + L2 f̂` | `^{Person} P_{WR} = ^{Person} P_{L14} + L_2 · ^{Person} f̂`; `L_2` keeps its letter |
| 18 | C5-16 | `:380` eq (5.7) | `w = o + R_obj h` | `^{Levelled} P_{ŴR}` |
| 19 | C5-18 | `:403-404` eq (5.8) | `‖p_el − p_sh‖ = L1` etc. | `^{Person}`; `L_1`, `L_2` keep their letters |
| 20 | C5-19 | `:420-422` eq (5.9) | `cos j = …` | `^{Person}` |
| 21 | C5-20 | `:432-434` eq (5.10) | `p_c = p_sh + L1 cos j b̂`, `r_c` | `^{Person}` |
| 22 | C5-21 | `:443-445` eq (5.11) | `p_el = p_c + r_c(cos s n₁ + sin s n₂)` | `^{Person}` |
| 23 | C5-22 | `:456-458` eq (5.12) | `u⊥ = û − (û·b̂)b̂`, `p_el` | `^{Person}` |
| 24 | C5-24 | `:478` Figure 5.5 caption | no transforms | **no label needed — AGREES as printed** |
| 25 | C5-25 | `:507` | `p_sh = (−0.16, 0.34, 1.32)` | `^{Person} P_{L12}` |
| 26 | C5-26 | `:509` | `o = (−0.22, 0.08, 0.45)` | `^{Levelled} P_{MappedMarker}ORG` |
| 27 | C5-27 | `:510-513` | `R_obj` 3×3 | `^{Levelled}_{MappedMarker} R` |
| 28 | C5-28 | `:516` | `h = (0.01, −0.04, 0.05)` | `^{MappedMarker} P_{WR}` |
| 29 | C5-29 | `:518-520` | `R_obj h = (0.01, 0.06, 0.04)` | `^{Levelled}_{MappedMarker} R · ^{MappedMarker} P_{WR}` |
| 30 | C5-30 | `:520` | `w = o + R_obj h = (−0.21, 0.13, 0.48)` | `^{Levelled} P_{ŴR}` |
| 31 | C5-31 | `:524-528` | the 4×4 scene-calibration matrix | `^{Person}_{Levelled} T` (see row 10) |
| 32 | C5-34 | `:529-530` | "its rotation block is close to the identity … its last column is the desk origin in person space" | `^{Person} P_{Levelled}ORG` |
| 33 | C5-32 | `:531` | `w = (−0.19, −0.09, 1.04)`, four lines after row 30, **y sign changed** | `^{Person} P_{ŴR}` — the two superscripts are what tell the reader these are one point in two frames |
| 34 | C5-33 | `:535-553` | `b, r, b̂`; `cos j`; `p_c, r_c`; `û, u⊥`; `p_el` | all `^{Person}` |
| 35 | C5-05 | `:564-570` | the two Table 5.1 cells naming `T_WO` | `^{World}_{Object} T` |
| 36 | C5-37 | chapter-wide (Table 5.1 vs Chapter 4 §4.1) | `W` used for two frames 32.04° apart | **{World}** and **{Levelled}** — dissolved by D-056 (§5) |
| 37 | C5-38 | chapter-wide (§5.4 vs Chapter 6 eq (6.1)) | the swap Chapter 5 silently depends on | the same matrix `S` (`carry.py:24` = the thesis's `S`) — **print the dependence** |

*Nothing to step over in this file: Chapter 5 has no OPERATOR, IMPROPER or BLOCKED
row.* **But §9 S-1 and S-2 both live in Table 5.1** (rows 3, 4, 5 above) and must
not be closed by the relabelling.

#### 8.9.6 `build_ch6.py` — 23 APPLY rows

The chapter with the most IMPROPER and BLOCKED rows. **Work the APPLY rows and
leave the other eleven strictly alone**; four of them are substantive defects.

| # | item | line | present | assigned |
|---|---|---|---|---|
| 1 | C6-05 | `:191` (definition), used `:283`, `:287` | `R_cam` | `^{World}_{Sensor} R` |
| 2 | C6-06 | `:192` (definition), used `:282`, `:287` | `t_cam` | `^{World} P_{Sensor}ORG` |
| 3 | C6-09 | `:198` (definition), used `:287`, `:289` | `T_WC` | `^{World}_{Sensor} T` |
| 4 | C6-10 | `:199` (definition), eq (6.2) at `:284-285` | `T_UP` | `^{Unity}_{Person} T`, with `^{Unity} P = ^{Unity}_{Person} T · ^{Person} P` |
| 5 | C6-28 | `:251` Table 6.1 | "pelvis position in person space" etc. | `^{Person} P` |
| 6 | C6-27 | `:258` | "bringing that pose back into camera coordinates undoes the axis swap … and applies the calibrated anchor" | `^{Sensor}_{Object} T = ^{Sensor}_{World} T · ^{World}_{Object} T`, with `^{World}_{Object} R = S · ^{Unity}_{MappedMarker} R · S`; order verified at `v2/common/object_link.py:109-111` |
| 7 | C6-29 | `:260` | "the object pose by a straight line …" | name the frame |
| 8 | C6-07 | `:282` | `S t_cam` | `^{Unity} P_{Sensor}ORG` |
| 9 | C6-08 | `:282-283` | `A = S R_cam F` | `^{Unity}_{Person} R`, `det +1` — **both frames left-handed**; state that Craig's algebra carries over but his right-handed assumption does not |
| 10 | C6-12 | `:294-304` eq (6.3) | `(S R_cam S)(S F)` | `^{Unity}_{Person} R = ^{Unity}_{MappedCamera} R · ^{MappedCamera}_{Person} R`, with `^{MappedCamera}_{Person} R = R_x(−90°)`, `det +1`. **The one honest way to write (6.2)/(6.3)**; matches `IntegratedSceneReceiver.cs:161-163` factor for factor |
| 11 | C6-30 | `:306` | "the first factor is the orientation the display already uses to place the sensor body" | `^{Unity}_{MappedCamera} R`; **AGREES as written** |
| 12 | C6-18 | `:333` | the avatar proportion scaling | a **scale**, not a frame relation; no label |
| 13 | C6-17 | `:337` | "the receiver maps the streamed pelvis …" | **AGREES**; name the frames in words |
| 14 | C6-19 | `:345` §6.4 | "It rotates that node by the shortest …" | `^{Levelled}_{Unity} R = G`, class 1, `det +1`, 32.0368° |
| 15 | **C6-34** | `:345` (anchor), cited from `:434` and `:475` | **not printed today** | **`^{Scene}_{Levelled} T = [ I₃ , (0, d, 0) ; 0 0 0 , 1 ]`**, `d = 0.716215 m` (r6b). **A new printed transform required by D-060**, with identity rotation stated explicitly |
| 16 | C6-21 | `:397-402` | `R_cam`, `t_cam` numerics | `^{World}_{Sensor} R`, `^{World} P_{Sensor}ORG` |
| 17 | C6-22 | `:405-410` | `A` numeric, `S t_cam` numeric | `^{Unity}_{Person} R`, `^{Unity} P_{Sensor}ORG` |
| 18 | C6-23 | `:412-416` | `q = (0.03, −0.18, 0.99) m`; `p_U = A q + S t_cam` | `^{Person} q`; `^{Unity} P = ^{Unity}_{Person} R · ^{Person} q + ^{Unity} P_{Sensor}ORG` |
| 19 | C6-24 | `:417` | "Undoing the flip gives …", the three-step narration | name the frames at each step |
| 20 | C6-20 | `:429-434` worked example | `L` (the levelling rotation); `p_scene = L p_U + (0, 0.72, 0)` | `^{Levelled} P = ^{Levelled}_{Unity} R · ^{Unity} P`, then `^{Scene} P = ^{Scene}_{Levelled} T · ^{Levelled} P`; the bare `L` retires; `(0, 0.72, 0)` is `^{Scene} P_{Levelled}ORG` |
| 21 | C6-25 | `:442-448` | `R = R_camᵀ`, `t = (0.02, 0.19, 0.55)` | `^{Sensor}_{World} R`, `^{Sensor} P_{World}ORG`; the step is `^{Sensor}_{Object} T = ^{Sensor}_{World} T · ^{World}_{Object} T` |
| 22 | C6-31 | `:452-456` | `p_C = R p_W + t` | `^{Sensor} P = ^{Sensor}_{World} R · ^{World} P + ^{Sensor} P_{World}ORG` |
| 23 | C6-32 | `:474-476` Table 6.2 | "in display axes" / "in the scene" on one point | **{Unity}** and **{Scene}**; the Link row is `^{Sensor}`. *The thesis's own proof that it needs both frames* |

*Step over in this file:* **IMPROPER** C6-01, C6-02, C6-03 (`:271-275`, eq 6.1),
C6-04 (`:277`, `F` — and §9 S-9), C6-26 (`:452-456`, bare `S` used in the opposite
direction from eq (6.1)). **BLOCKED** C6-11 (`:287-290`, the "standard chaining"
sentence — needs a corrected characterisation, author declaration), C6-13 (`:277`
vs `:306` — §9 S-3), C6-14 (`:318-321`, eq (6.4), awaits §4.9), C6-15 (`:329`,
`:331`, eq (6.5) — §9 S-4), C6-16 (`R_rest` — §4.9, author declaration), C6-33
(`:267`, Figure 6.4's caption). **And §9 S-12 is at `:308`**, a prose sentence in
this same file that is false of the rig; it is content, not a label.

#### 8.9.7 `build_ch7.py` — 9 APPLY rows

Chapter 7 prints no rotation-matrix or homogeneous-transform symbol. Every
transform is invoked in prose or a caption, so what these rows need is frame
**names**, not new symbols.

| # | item | line | present | assigned |
|---|---|---|---|---|
| 1 | C7-08 | `:233-239` eqs (7.2)-(7.4) | the PCA line fit; `c`, `C`, `u` | **{Levelled}**; `C` and `u` keep their letters |
| 2 | C7-09 | `:240` | "the physical route is not registered into the …" | **AGREES**; name the frame |
| 3 | C7-03 | `:251`, `:274` Figures 7.1/7.2 captions | "this frame" | **{Levelled}**: origin at the desk marker, +y calibrated gravity up, left-handed (`eval_rail_scenario.py:51-58`) |
| 4 | C7-02 | `:286` §7.2 | "invariant under the levelling rotation" | `^{Levelled}_{Unity} R = G`, `det +1` — so the invariance claim about Tables 7.1 and 7.2 **is correct**; the next sentence about non-invariant quantities is what makes {Levelled} a frame (§4.5) |
| 5 | **C7-07a** | `:294` eq (7.5) | `e_{k,t} = ‖p^Unity − p^measured‖` | `‖ ^{Scene} P^{rig} − ^{Scene} P^{meas} ‖`. **Both operands {Scene}**; the right superscripts are **provenance**, and `p^Unity` must be renamed (`rig` / `rendered`) so the word "Unity" stops naming a frame it is not |
| 6 | **C7-04** | `:320`, `:325` Figures 7.3/7.4 captions | "the same Unity world frame" | **{Scene}**, and say it **shares {Levelled}'s axes** and differs only by the floor drop; reconcile the `Unity x/y/z` axis labels of `make_ch7_valid_joint_figures.py:37-39` |
| 7 | C7-06 | `:353-372` §7.3.3 | the wrist-to-marker separations | **{Levelled}** |
| 8 | **C7-07b** | `:366` eq (7.6) | `e_{m,k,t} = ‖p^masked − p^unmasked‖` | **`^{Person}`** both operands — traced at `evaluate_ch7_restructured.py:184` (the `[1,−1,1]` flip), `:153-162` (`fk`), `:185`, `:226`, `:231`. **§7.4 enters no Unity frame at all** |
| 9 | C7-05 | `:377` | "the proxy and reconstructed wrist are …" | Table 7.8 is computed in **{Sensor}** (`evaluate_ch7_restructured.py:265-271`), Table 7.9 in **{Person}** (`eval_labeled_recovery.py:122`). `F` is an isometry so every distance agrees; **name both frames instead of asserting one** |

*Step over in this file:* **BLOCKED** C7-01 (`:293`, §7.3 — §9 S-5: a `det −1` map
called a rotation, and a false frame-identity claim). *Note that C7-01 sits in the
same paragraph that introduces equation (7.5): relabel row 5, and leave the
sentence at `:293` for the content pass.*

#### 8.9.8 `build_ch8.py` — 4 APPLY rows

| # | item | line | present | assigned |
|---|---|---|---|---|
| 1 | C8-02 | `:148` Table 8.1 row | "newest published marker …" | name the frame |
| 2 | C8-01 | `:164` | "live it reads the newest …" | `^{Sensor}_{Object} T = ^{Sensor}_{World} T · ^{World}_{Object} T` after the conjugation un-swap (`object_link.py:109-111`) |
| 3 | C8-04 | `:164` | "the two capabilities marked as a new data path" | **AGREES** |
| 4 | C8-03 | `:174` and Figure 8.3 caption `:206` | the chain and the projection | the chain is built in **{Person}**, the projection is in **{Sensor}** |

*Nothing to step over in this file.*

#### 8.9.9 `build_appendix.py` — 9 APPLY rows

| # | item | line | present | assigned |
|---|---|---|---|---|
| 1 | A-D01 | `:216-219`, D.1, at eq (D.1) | bare `p` | `^{Sensor} P` |
| 2 | A-D03 | `:237`, D.2 | "the known transformation between the two imagers" — no symbol, frame unnamed | **no label, and none needed** — the transform exists only inside the vendor library (`rs.align(rs.stream.color)`, `realtime_person.py:79`; §6.1). State that only the aligned colour-optical frame **{Sensor}** is used downstream |
| 3 | A-D02 | `:246-249`, D.3, eq (D.2) | bare `p` | `^{Sensor} P` |
| 4 | A-E01 | `:293`, E.2 | bare `R`, bare `t` | `^{Sensor}_{World} R`, `^{Sensor}_{Wall} R`, `^{Sensor}_{Object} R`; `^{Sensor} P_{marker}ORG` — the three instances of §2.4's "marker's own frame" rule |
| 5 | A-E07 | `:302`, E.2 | "the lobe whose in-plane up axis better agrees with an estimate of the gravity direction" | `^{Sensor} ĝ` |
| 6 | A-E03 | `:320`, Table E.1 header | "Translation `t` (m)" | `^{Sensor} P_{marker}ORG` |
| 7 | A-E04 | `:333` and `:352`, E.4 | bare `R` (twice) | `^{Sensor}_{Object} R` |
| 8 | A-E05 | `:340`, E.4 | `w = (1.00, 0.00, 0.03)` | `^{Sensor} ŵ`; `w` keeps its letter |
| 9 | A-E06 | `:356`, E.4 | "the third column is the marker's own outward normal in the camera frame" | `^{Sensor} Ẑ_{Object}` |

*Step over in this file:* **OPERATOR** A-E02 (`:306-310`, eq (E.1), Rodrigues —
`R(ŵ, θ)`, **no frame pair**; the *instance* in E.4 is `^{Sensor}_{Object} R`) and
A-G01 (`:393`, eq (G.1), the depth rescaling — a class-3 operator in **{Person}**,
frame confirmed by the builder's own sentence at `:393`). **IMPROPER** A-D04
(`:250`, "a separate fixed axis flip, developed in Section 3.1" — `F`, class 4;
name its direction, never Craig notation).

#### 8.9.10 Per-builder totals

| builder file | APPLY | also present (not for this pass) |
|---|---|---|
| `build_ch2.py` | **16** | 2 IMPROPER |
| `make_ch2_frames_fig.py` | **1** | §9 S-7 (substantive) |
| `build_ch3.py` | **42** | 6 OPERATOR, 2 IMPROPER, 2 BLOCKED |
| `build_ch4.py` | **20** | 1 BLOCKED |
| `build_ch5.py` | **37** | §9 S-1, S-2 (substantive, inside Table 5.1) |
| `build_ch6.py` | **23** | 5 IMPROPER, 6 BLOCKED, §9 S-12 at `:308` |
| `build_ch7.py` | **9** | 1 BLOCKED |
| `build_ch8.py` | **4** | — |
| `build_appendix.py` | **9** | 2 OPERATOR, 1 IMPROPER |
| **total** | **161** | 8 OPERATOR, 10 IMPROPER, 10 BLOCKED |

**Suggested execution order**, because the frame table must exist before anything
cites it: `build_ch2.py` (which carries Table 2.2, Table 2.3 and Figure 2.4(b),
and where the {Unity} / {Levelled} / {Scene} distinction should first be stated) →
`make_ch2_frames_fig.py` → `build_ch3.py` → `build_ch4.py` → `build_ch5.py` →
`build_ch6.py` → `build_ch7.py` → `build_ch8.py` → `build_appendix.py`.

---

## 9. SUBSTANTIVE DEFECTS — these are NOT notation and must NOT be swept into a relabelling pass

**Listed separately and prominently, as required.** Each of these is a claim the
thesis makes that the code does not support, or a figure that draws something the
mathematics does not have. **A relabelling pass would paint over every one of
them.** None is a numerical error, and none requires a change to any
transformation direction in the code. They need author decisions and new
sentences, not labels.

**Twelve rows.** S-1 through S-10 are carried forward unchanged from the third
pass. **S-11** collects the author declarations that are still open after D-058
and D-060, which belong here because each is a missing piece of *content* that a
relabelling pass would silently paper over. **S-12 is new**, found by the trace in
`UNITY_FRAME_RESOLUTION.md` §11 item 4 and recorded here for the first time.

**Each row is written so it can be actioned as a content fix on its own**: where
it is, what the thesis says, what is actually the case, and the code that
establishes it.

| # | defect | where | what is actually the case | evidence |
|---|---|---|---|---|
| **S-1** | **Table 5.1 attributes `o` and `R_obj` to Chapter 4's `T_WO`.** They are not its translation column and rotation block. | `build_ch5.py:253-256`, `:564-570` (C5-02, C5-03) | `o` and `R_obj` are that transform carried through the swap `S` **and** the 32.04° levelling `G`. Chapter 4's `T_WO` translation column at frame 560 is (−0.2234, 0.4171, −0.1763); Chapter 5 prints `o = (−0.22, 0.08, 0.45)`. | `carry.py:79` composed with `frames.py:85-88`; `R_obj = G · S · (^{World}_{Object} R) · S` reproduces the printed matrix to two decimals, the bare rotation block does not (verified entry-by-entry, ch3/ch5 audit C5-03) |
| **S-2** | **Chapter 5's `h` is declared in the object frame; it lives in the mapped marker frame.** | Table 5.1 rows `h`, `h_k` (C5-07); prose at `build_ch5.py:207` (C5-36) | {Object} is right-handed with the marker normal on **+z**; {MappedMarker} is left-handed with the normal on **+y**. Equations (5.1)-(5.3) are only legal once {MappedMarker} exists. | `carry.py:117` `d_loc = R_objᵀ(wr − o)` **is** Chapter 5's `h`; same at `recovery_core.py:111`; the frame's axes at `ArucoSceneReceiver.cs:12-13, 131-132`; §3.1 of this file |
| **S-3** | **Chapter 6 states two mutually exclusive rules for re-expressing a rotation.** | `build_ch6.py:277` against `:306` (X-2, C6-13) | One passage says a rotation must be **conjugated** because "both its input and its output change basis"; the other left-multiplies. Both appear in the same chapter. The missing criterion: **conjugate when the body's own frame is re-based by the same map** ({MappedMarker}, {MappedCamera}), **left-multiply when it is not** (the rig bones). | The code's own difference in treatment: `frames.py:88` conjugates through `S`; `carry.py:79` left-multiplies `G`. Requires a new sentence of content, not a relabel |
| **S-4** | **Equation (6.5) omits the levelling factor that the code applies.** | `build_ch6.py:329, :331` (X-3, C6-15) | The code writes `bone.rotation = qA * qChain * c_rest` with `qA = anchor.rotation`, the anchor's **global** rotation; the anchor **is** parented to the levelling node while **the rig is not**. So the written rotation carries the levelling and the printed equation does not. §6.2's "both branches inherit the levelled frame as local poses beneath one parent" is **false for the rig**. | `IntegratedSceneReceiver.cs:357, 370-374`; `:160` (anchor parented) against `:180` `rigRoot = hip.root;` |
| **S-5** | **Section 7.3 asserts a frame identity that does not hold, and calls a `det −1` map a rotation.** | `build_ch7.py:293` (X-4, C7-01) | "The calibrated camera-to-scene mapping" is orthogonal with `det = −1` and is **not** a rotation; and "the same Unity world frame" asserts an identity between two frames that differ by the levelling and the placement. | `det(S R_cam) = −1.000000`, orthogonality error ≈ 1.9e−15, recorded in `audit_evidence/ch7_restructured/human.json`; §4.3 |
| **S-6** | **Figure 3.5's caption draws a frame the mathematics never defines.** | `build_ch3.py:294` ("the wrists x along each forearm") (C3-22) | Chapter 3 defines no wrist or forearm frame, and §3.3.1 says the chain "ends at the wrist **as a tracked point**". **No position or orientation is ever expressed in a forearm or wrist frame** (§4.7). The fix is in the caption, not in the frame inventory. | `shoulder.py:92-99` expresses the forearm in **{L14}** and reads its components; `check_v1_overlay.py:47-66` builds the forearm as an {L14} vector carried into {L24} |
| **S-7** | **Figure 2.5(b) mixes the 45 mm-scaled calibration with the unscaled (50 mm) object detection.** | `make_ch2_frames_fig.py:116-120`, with `:56, 62`, `:137, 164`, `:140-142` | `T_cam_desk` comes from the **scaled** `scene_calibration_r6bc.json`; `T_cam_obj_raw` is read from the **unscaled** raw CSV. Panel (a) is right to use the unscaled pose (the image overlay must reproject correctly, `:18-21`), but panel (b) is a **metric top view**: the cube glyph sits at roughly 50/45 of its true range along the camera ray (~0.11 m at 1.02 m), beside a grey object path drawn from the **scaled** clean track. | ch2/ch4 audit S2. **A figure-owner check, not a value change** |
| **S-8** | **Figure 4.1's caption claims the calibrated anchor; the figure code draws the per-frame detection.** | `build_ch4.py:143` ("the world frame W **of the calibration**") (C4-20) | `make_ch4_experiment_fig.py:72, 87` draws them from `make_T(*rt_from_row(row, DESK_ID))` — the raw per-frame desk detection on that panel's frame, not `calib["T_cam_desk"]`. Both are `^{Sensor}_{World} T`, so the **direction** is right and no value is wrong; the caption's **provenance** claim is not what the figure code does. For a static marker the two are close, which is exactly why looking at the picture would not catch it. | ch2/ch4 audit S1 |
| **S-9** | **The `F` direction reversal.** Equations (6.2)/(6.3) print a bare `F` while it acts **person→sensor**, the inverse of eq (3.1)'s definition. | `build_ch6.py` eqs (6.2)/(6.3) (X-1, C6-04) | Harmless **only** because `F` is an involution — which the thesis states of the swap (`build_ch6.py:277`) but never of `F`. Declaring `F`'s direction at every appearance is a label fix; **stating the involution is content**. | `root_frame.py:9, 12-14`; section 6 |
| **S-10** | **Chapter 3's "no matrix is ever inverted numerically".** | `build_ch3.py:197` (C3-52) | True of Chapter 3's chain; **false of the path Chapter 5 depends on**. Qualify or drop the claim. | `carry.py:59`, `recovery_core.py:69` |
| **S-11** | **Two author declarations are still open, and equations (6.4) and (6.5) cannot be finished without them.** | `build_ch6.py:318-321` eq (6.4) (C6-14 / U-2) and `:329, :331` eq (6.5) (C6-16 / U-1); analysis in §4.9 | **(a) `R_rest`.** The usage test says the avatar bone axes are **not** a frame: a grep of `IntegratedSceneReceiver.cs` finds **no** `localPosition`, `localRotation`, `InverseTransformPoint` or `TransformDirection` on any bone — only global `.rotation` (`:239-243`, `:370-374`), global `.position` (`:378-379`, `:395-398`) and `.localScale`. Nothing is ever expressed in a bone's own axes. But Craig's notation for the right-multiplied factor in `R_bone = A R_chain R_rest` wants a frame anyway, as `^{model}_{bone} R`. The author must state either **(i)** the frame the rest rotations are captured in, the frame `R_0, R_1, R_2` are expressed in, and the assumption linking them, **or (ii)** that `R_rest` is a **fixed constant re-basing factor**, defined as the bone's spawn orientation in the scene axes, with **no bone frame named** — which is consistent with the usage test and follows D-057's precedent. **(b) `R_0, R_1, R_2`.** Equation (6.4)'s operator reading is consistent and its order is verified against `IntegratedSceneReceiver.cs:358-374`, but it is not settled until (a) is. *One short declaration settles both equations.* | `IntegratedSceneReceiver.cs:237-238` "the rig spawns unrotated (**body axes = scene axes**)"; `:217-218, 261-273` (arms forced to the T-pose before capture); `:357` `qA = anchor.rotation`; ch6/ch8 audit U-1, U-2 |
| **S-12** | **`build_ch6.py:308` states something that is true of one branch and false of the other.** §6.2 closes: *"Section 6.4 levels the display frame, and both branches inherit the levelled frame **as local poses beneath one parent**, so nothing rewrites the data."* | `build_ch6.py:308` | **True of the object branch**, whose node *is* parented to ArucoWorld and whose log is local: `ArucoSceneReceiver.cs:114` ("a pose node in **ArucoWorld-local coordinates**"), `:119-120` (`t.localPosition = pos; t.localRotation = …`), `:389-390` (`objectNode.localPosition = pos`), and the object log at `:392-397`, which writes the **local** `pos`/`euler`. **False of the rig.** The rig is never parented — `IntegratedSceneReceiver.cs:180` `rigRoot = hip.root;` and the file's **only** `SetParent` call is `:160`, the *anchor* — and nothing is ever read in a bone's local axes, so its logged positions at `:395-403` are **global**, i.e. in **{Scene}**. The sentence therefore asserts a uniformity the implementation does not have, and it is the same fact that makes S-4 (equation (6.5)'s missing levelling factor) a defect rather than a rounding of language. **The fix is one sentence of content**: say that the object branch is applied as a local pose beneath the levelled parent while the rig is driven globally through the anchor, and that this is *why* the bone rotation carries `G` and the printed equation does not. | `IntegratedSceneReceiver.cs:160`, `:180`, `:378-379`, `:395-403`; `ArucoSceneReceiver.cs:114`, `:119-120`, `:389-397`; `UNITY_FRAME_RESOLUTION.md` §11 item 4 |

**One correction to S-5's scope, from D-060** — recorded here rather than rewritten
into the row, so nothing is lost. The ch6/ch8 audit's **X-4** had two halves.
*Half one*, the `det −1` map called a rotation and the false frame-identity claim
at `build_ch7.py:293`, is **unchanged and still substantive**. *Half two*, the
claim that Figures 7.1/7.2 and Figures 7.3/7.4 "differ by the levelling **and** the
placement", is **narrower than recorded**: they differ **by the placement only**.
{Levelled} and {Scene} share a basis to `1.1e−16`, so the two figure pairs have
**identical shapes, directions, tilts and distances**, and only absolute component
values differ, by the constant `(0, 0.716215, 0)` m. §4.3.4 carries the evidence.
The fix for that half is to **name both frames and state that they share axes**.

---

## 10. Open items for the author

**Four of the third pass's six items are now CLOSED.** Recorded with their
dispositions so nothing is silently dropped, followed by what is actually still
open.

### 10.1 Closed since the third pass

| third-pass item | disposition |
|---|---|
| 1. **{Sensor} or {Camera}** | **CLOSED by D-058**: "The sensor optical frame is named **Sensor** rather than Camera", because Camera "collides in reading with MappedCamera and the Unity camera node". The thesis's prose phrase "the camera frame" and Figure 2.4(a) stay, with the identity stated once |
| 2. **{Levelled} or {LevelledWorld}** | **CLOSED by D-058**: **{Levelled}**, "unambiguous because no other frame is levelled, and five characters shorter in every left superscript in Chapters 5 and 7" |
| 3. **Unity's scene root (§4.3)** | **CLOSED by D-059 → D-060**: three frames, {Unity}, {Levelled} and **{Scene}**. F2.4b, C7-04 and C7-07 are unblocked; §4.3 carries the resolution and its evidence |
| 4. **The frame of equation (4.3) (C4-08 / C4-09)** | **CLOSED by D-058**: the input is declared **{Unity}**, matching `clean_object_track.py:59-61`, and the prose that calls it "the world frame track" is to be corrected. No number changes |
| 5. **The {E0} example in D-056** | **CLOSED by D-058**: "The E0 example given in D-056 is withdrawn … so no such frame is issued." The third pass escalated this for confirmation; the confirmation is explicit |
| 6. **`R_rest` in equation (6.5)** | **STILL OPEN** — carried below, and promoted into §9 as **S-11** so it is visible where the content fixes are listed |

### 10.2 Still open

1. **The two declarations of §4.9 — `R_rest`, and the frames of `R_0, R_1, R_2`.**
   This is the **only** thing still blocking equations (6.4) and (6.5), and it is
   the last of the third pass's six items. The usage test says the avatar bone axes
   are **not** a frame; Craig's notation for a right-multiplied factor wants a
   label anyway. **One short declaration settles both equations**, and D-057 sets
   the precedent for the operator/constant-factor route. Written up in full, with
   the code evidence and the two routes, at **§9 S-11**. *Note that this is a
   separate question from S-4: naming `R_rest` does not supply equation (6.5)'s
   missing levelling factor.*

2. **C6-11's characterisation sentence.** `build_ch6.py:287-290` calls equation
   (6.2)'s composition "the standard chaining of homogeneous transformations".
   Two of the three factors have `det −1` rotation blocks and are **not**
   homogeneous transforms in Craig's sense. This needs a corrected sentence of
   content, not a label. It is not a numerical error: the composition the code
   performs is correct, and C6-12 gives the Craig-legal factorisation that makes it
   sayable.

3. **Which floor drop `d` the thesis prints (new, raised by C6-34).** D-060
   requires `^{Scene}_{Levelled} T` to be printed with "the measured floor-drop
   translation", and the drop is **recording-dependent**: `d = 0.716215 m` on the
   rail recording (r6b, `scene_calibration_r6bc.json`) and `0.709312 m` on the
   handover recording (r7, `scene_calibration_r7c.json`). Chapter 6's worked
   example is the rail recording and already prints `(0, 0.72, 0)` rounded, so
   **printing `d = 0.716215 m` there is consistent with everything else in §6.5**.
   *Recommended*: print the rail value at the worked example, and state once — in
   the frame table or at C6-34's anchor — that `d` is a per-recording calibration
   constant equal to `origin_above_tabletop_m + DeskThick + LegH`, with the r7
   value given. **Escalated rather than decided, because printing a single `d` as
   if it were a constant of the system would be a silent methodological choice.**

4. **Whether {Scene} should appear in Chapter 2 (new, raised by F2.4b).**
   Correcting Figure 2.4(b)'s caption introduces {Scene} in Chapter 2, several
   chapters before the levelling of §6.4 that produces it. The alternative is a
   forward reference. *Recommended*: state the three Unity-side frames once in the
   Chapter 2 frame table, where Table 2.2 and Table 2.3 already live, and let
   §6.4 build the transform. **The author's call; the caption wording at §8.1.1 is
   proposed on that assumption.**

**Nothing in the label table is blocked on any of these four.** Items 1 and 2 hold
three rows (C6-11, C6-14, C6-16) that are already counted as BLOCKED; items 3 and
4 are wording choices inside APPLY rows.

---

## 11. Where this pass disagrees with the three earlier audits

Carried forward unchanged in substance, with the names updated. Stated
explicitly, with the evidence.

1. **The forearm/wrist frame is not a missing frame (contra C3-22 and C3-39).**
   The ch3/ch5 audit listed `{F_r}, {F_l}` as frames the chapter needs. **No
   position or orientation is ever expressed in them** — `shoulder.py:92-99`
   expresses the forearm in **{L14}** and reads *its* components, and
   `check_v1_overlay.py:47-66` builds the forearm direction as an {L14} vector
   carried into {L24}. Chapter 3 §3.3.1 already says the chain "ends at the wrist
   **as a tracked point**". C3-22 is a **caption defect** (§9 S-6); **C3-39 is a
   class-3 operator**, which is this pass's one new classification and follows
   directly from the demotion.

2. **The mirrored root basis is not a frame (contra C3-35 and `{B'}`).**
   `shoulder.py:127` calls `M` a "sagittal reflection **in the root basis**";
   `KINEMATIC_MODEL.md:507-512` and thesis §3.4.2 say the vectors are
   "**expressed in the root basis** and their x components flipped"; the
   reconstruction conjugates back into the same basis (`shoulder.py:142-144`,
   `check_v1_overlay.py:61-65`). The `np.eye(3)` at `shoulder.py:152` is code
   reuse, not a frame declaration. It is a **class-4 map**, which D-054 covers.

3. **There is no second Unity frame *beneath* the levelling parent (contra the
   ch6/ch8 audit's `{S}` and `{L}`-as-Unity-frames) — but there is one *above* it,
   and D-060 has now named it.** The node's local coordinate system **is {Unity}**
   (`ArucoSceneReceiver.cs:114, 119-120, 389-390`), and the code calls the parent
   transform "purely presentational" (`:208-211`); that part of the finding stands
   unchanged. What lies *above* the node is Unity's pre-existing scene root, which
   the third pass escalated rather than folding either way. **The escalation was
   right and the answer is that it is a frame**: `UNITY_FRAME_RESOLUTION.md`
   measured a proper rotation of 32.0368° between equation (6.1)'s basis and every
   rig-side read site, recovered blind from the data, and found the second basis to
   be **{Levelled}'s exactly** (agreement 1.1e−16), leaving only the origin — the
   floor drop — to separate {Levelled} from {Scene}. So the audits' instinct that
   something was missing was correct; their label `{S}` was not, both because `S`
   is the swap matrix and because the thing that was missing is a **third**
   (origin, basis) pair, not a second basis. It is **entry 13, {Scene}** (§4.3).

4. **{Levelled} is a real frame and keeps its own name.**
   `thesis/00_notation.md:18` already gives it `ℒ`; `carry.py:54-56` and
   `eval_rail_scenario.py:51-58` name it; Chapter 7 §7.2 states in the thesis's
   own words that quantities reported from it are not invariant. One frame, not
   two, and not a transform.

5. **{MappedMarker} and {MappedCamera} are the system's names, not new labels
   (contra the ch6/ch8 audit's `{M'}`, `{C'}`).** `ArucoSceneReceiver.cs:12-13`
   and `:224-225, 235` name them; `:131-132, 137-138`, `:229-231`, `:241-242`,
   `:253-254` and — decisively, outside Unity — `carry.py:83, 117` express
   positions in them.

6. **No generic marker frame is needed (contra the ch2/ch4 audit's `{M}`).**
   Appendix E.2's "its own frame" is a **family rule**
   (`extract_aruco_poses.py:64-72`) whose three instances are {World}, {Wall} and
   {Object} — all already named (§2.4).

7. **The kinematic frames already have names (contra `{Rt}`, `{B}`, `{Sh}`,
   `{El}`, `{S_r}`, `{E_r}`).** The system calls them the **L24 root frame**, the
   **L12 shoulder frame** and the **L14 frame**, in module docstrings, in
   `KINEMATIC_MODEL.md` and in Figure 3.3's own caption. §2.3 adopts them as the
   compact symbols.

8. **Every letter collision the three audits recorded is dissolved rather than
   resolved (contra all three audits' rename proposals, and D-055's).** D-056
   removes frames from the letter economy entirely; §5 records what each letter
   now means and what keeps it.

9. **`{E0_r}` / `{E0_l}` are withdrawn (contra the ch3/ch5 audit's frame 6 and
   its C3-33 verdict).** D-057 classifies equation (3.22) as a class-3 operator
   and section 0 verifies the active-rotation premise that classification rests
   on. The ch3/ch5 audit's "MISLEADING, plus a blocking gap" verdict on C3-33 is
   superseded: there is no gap, because there is no frame.

---

## 12. What remains blocked

Sections 8.1-8.7 are **directly executable now**, in the per-builder grouping of
**§8.9**, **except** for the 10 BLOCKED rows, which §8.8 itemises. **No row is
blocked on a frame question any more.**

- **Six substantive defects** — C3-22, C3-52, C4-20, C6-13, C6-15, C7-01, written
  up as **S-1 through S-12** in section 9 — which must be handled as content,
  before or separately from any relabelling pass, and **never inside one**. Note
  that section 9 carries twelve rows against six blocked table rows: the extra
  rows are defects that live in cells the table marks APPLY (S-1 and S-2 inside
  Table 5.1), in a file the table does not otherwise touch (S-7 in
  `make_ch2_frames_fig.py`), in an IMPROPER row (S-9), in the open declarations
  (S-11), or in prose the table has no row for at all (**S-12**,
  `build_ch6.py:308`).
- **Three author declarations** — C6-11's corrected characterisation sentence, and
  C6-14 / C6-16, the frames of `R_0…R_2` and `R_rest` (§4.9, §9 S-11).
- **One caption completeness claim** — C6-33, Figure 6.4's "the four coordinate
  frames", against the **eight** of thirteen that appear in Chapter 6.

**Three classes of blockage have been cleared since the third pass.**

- **Equation (3.22) is not blocked.** D-057 classifies it as a class-3 operator,
  section 0 verifies the active-rotation premise the classification depends on,
  and §8.2 gives its form. No frame is issued for it, and **D-058 withdraws
  {E0}**.
- **The frame of equation (4.3) is not blocked.** D-058 declares it **{Unity}**,
  matching `clean_object_track.py:59-61`. C4-08 and C4-09 are APPLY.
- **The Unity question is not blocked.** D-059 commissioned the trace, D-060
  decided it, and the three rows that waited on it — **F2.4b, C7-04, C7-07** — are
  APPLY. F2.4b carries corrected caption wording rather than a Craig label, marked
  **proposed, not applied**, at §8.1.1.

**Where this pass changes the third pass, and where it does not.**

*Changed:* the frame count (**12 → 13**, by D-060 adding {Scene}); section 4.3,
which becomes a resolution instead of an open question; section 4.2, which gains
the correction D-060 forces on two of its claims; the naming layer's confirmations
under D-058; the label table's five moved rows, its one new row (**C6-34**) and
its one split row (**C7-07 → C7-07a / C7-07b**); the counts (§8.8); five corrected
line anchors (§8.9); and section 9, which gains **S-11** and **S-12**.

*Unchanged:* **every finding.** The usage test and the four demotions; the frames
that survived and the read-site evidence for each; D-054's four classes and the
class-4 declarations of section 6; the code-to-thesis naming warning of §2.5; the
disagreements with the three earlier audits in section 11; the finding that **all
three audits independently found no wrong transformation direction anywhere in the
code, and no pass of this inventory has found any**; and every substantive defect
S-1 through S-10.

*Applied to the thesis:* **nothing.** The only file written by this pass is this
one.


## 13. Final completion disposition, 2026-09-12

This inventory preserves the pre-implementation findings above. Their current
status is in DETERMINED_DEFECTS.md and UNRESOLVED_ITEMS.md; D-064 and D-067 to
D-071 govern the completed source corrections. The historical "nothing
applied", BLOCKED and author-question labels above are not the current queue.

- S-1/S-2: Table 5.1 and Section 5.3 now derive the cleaned World-to-Unity-to-
  Levelled object path, define MappedMarker and its handedness, and print the
  two-sided swap. Section 5.6 explicitly converts homogeneous wrist coordinates
  back to Person (D-068/D-071).
- S-3/S-9 and C6-11: Chapter 6 distinguishes changing both bases from changing
  only the reference basis. Equations 6.2/6.3 show F inverse; two improper maps
  and the calibrated transform give the proper net relation (D-070).
- S-4: D-064 already made equation 6.5's leading factor Scene/Person. D-070
  expands that valid factor to expose levelling; it does not multiply levelling
  into an equation that already includes it.
- S-5: the Chapter 7 evaluator already floor-maps both sides into Scene. The
  prose now names that operation and distinguishes Levelled by origin. Existing
  rig errors and Figures 7.3/7.4 coordinates remain unchanged (D-070).
- S-6/S-11 and Sections 4.9/10.2 item 1: D-064 issued the distal wrist and bone
  frames and settled the classification of equations 6.4/6.5. Figure 3.5 has a
  defined wrist frame. Equation 3.22 remains an operator. Spawn coincidence is
  still an assumption, not a newly verified fact.
- S-7/S-8/S-10/S-12: the metric Figure 2.5 object glyph uses scaled detection;
  Figure 4.1 identifies raw per-frame desk-axis provenance; Chapter 3 confines
  its inverse claim to its own chain; Chapter 6 distinguishes local object and
  globally driven rig paths (D-070).
- C6-33: the actual Figure 6.4 contains four boxes. Its correction identifies
  those as pre-levelling frames, rather than expanding the picture to eight.
- Section 10.2 items 3/4: D-061 makes d recording-specific and introduces the
  frames at their construction; D-063/D-065 settle Figure 2.4(b)'s caption and
  image treatment. These are not author decisions still outstanding.

No transformation direction in the implementation is changed. Only the
Figure 2.5 metric glyph moves numerically; the experimental results remain
unchanged. Consult the final delivery evidence for rebuilt artifacts and
rendered-page checks; this reconciliation itself claims no test execution.

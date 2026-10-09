# Craig-convention notation audit — Chapters 6, 7, 8 (+ Appendices A–H sweep)

Working document. Read-only audit; no thesis file, build script, figure or code was
modified. Scope: Chapter 6 (System Integration), Chapter 7 (Evaluation), Chapter 8
(Real-Time Feasibility), plus a sweep of Appendices A–H for transforms belonging to
those chapters.

Reference convention (Craig, *Introduction to Robotics*, 4th ed., Ch. 2):
`^A_B R` = orientation of {B} relative to {A} (columns = axes of {B} in {A});
`^A P_BORG` = origin of {B} in {A}; `^A_B T = [^A_B R, ^A P_BORG; 0 0 0, 1]`;
`^A P = ^A_B T ^B P`; chain `^A_B T ^B_C T = ^A_C T`. A Craig rotation matrix is
orthonormal with **determinant +1**.

Every direction below was established from the equations *and* the implementing code
and re-derived numerically from the committed calibration
(`eval/output/scene_calibration_r6bc.json`, the rail recording used by the Section 6.5
worked example). No direction was inferred from a symbol name.

---

## 1. Summary

### Counts by verdict

| Verdict | Ch 6 | Ch 7 | Ch 8 | Total |
|---|---|---|---|---|
| AGREES | 3 | 1 | 1 | **5** |
| UNLABELLED | 22 | 5 | 3 | **30** |
| MISLEADING | 3 | 2 | 0 | **5** |
| CONTRADICTS | 3 | 1 | 0 | **4** |
| UNRESOLVED | 2 | 0 | 0 | **2** |
| **Total items** | **33** | **9** | **4** | **46** |

AGREES is reserved for an item whose mathematics is right *and* whose frames are already
identifiable; UNLABELLED marks an item whose direction I could establish but which is
printed without both frame labels. Appendices: no appendix section carries a transform
belonging to Chapters 6–8 (Section 7).

Item ids: Ch 6 = C6-01 to C6-33, Ch 7 = C7-01 to C7-09, Ch 8 = C8-01 to C8-04.

### CONTRADICTS — all four, in full

**X-1 (C6-04). Equation (6.2)/(6.3) uses `F` in the direction opposite to its own
definition in equation (3.1).**
`build_ch6.py:281-285` and `:294-304`; definition at `build_ch3.py:188-190`.
Chapter 3 prints `q = F p, F = diag(1, −1, 1)` and its following sentence says the
result `q` is the person-space value and `p` the camera-frame value — so (3.1) defines
`F : {C} → {P}`. Chapter 6 equation (6.2) prints `p_U = A q + S t_cam`,
`A = S R_cam F`, where `q` is the person-space pelvis. `F` is therefore applied to a
person-space vector and must produce camera coordinates: in (6.2)/(6.3) `F` acts
`{P} → {C}`, the inverse of its Chapter 3 definition. The Chapter 6 prose
(`build_ch6.py:279`) says this correctly in words — "Undoing the flip returns a
person-space point q to raw camera coordinates" — but the equation prints plain `F`,
not `F^-1`. It is numerically harmless only because `F` is an involution, and the
thesis never says so (it says the *swap* is its own inverse, `build_ch6.py:277`, and
says nothing of the kind about `F`). Verified in code: `M = P @ R_dc @ D` with
`D = diag(1,−1,1)` applied on the right, i.e. to the person-space vector
(`eval/unity_check/check_unity_log.py:89,92`; `eval/offset/carry.py:25,60`;
`root_frame.unity_from_sensor` maps `{C} → {P}`, `v1/kinematics/root_frame.py:9-14`).
Honest fix: `F` is not a rotation (det −1) and cannot be `^C_P R`; it must be named as
a handedness-changing basis map with an explicit direction in each place it appears.

**X-2 (C6-13). Chapter 6 states two mutually exclusive rules for re-expressing a
rotation across a frame change, for the same class of object, with no criterion.**
Rule A, `build_ch6.py:277` (after eq. 6.1): "with the rotation conjugated rather than
multiplied on one side, because a rotation is a map from the frame to itself and both
its input and its output change basis." Rule B, `build_ch6.py:306` (after eq. 6.3):
"Every quantity from the person record passes through this node, positions as points
and rotations by multiplying on the left. Conjugating a body rotation by the anchor
would cancel the camera orientation out of the pose and turn the figure the wrong
way." Both rules are applied to rigid-body orientations, and both match the code
(`v1/aruco/frames.py:85-87` conjugates; `IntegratedSceneReceiver.cs:370-374`
left-multiplies). The real criterion, established from the code and absent from the
thesis, is: **conjugate when the body's own local frame is re-based by the same map,
left-multiply when it is not.** The Unity object node's local axes *are* the swapped
marker axes ("marker plane = local x/z, normal = local up",
`ArucoSceneReceiver.cs:135-136`), and the sensor node's likewise ("optical axis =
local up, image-down = local forward", `ArucoSceneReceiver.cs:283-284`); the rig bones'
axes are **not** re-based, they are the scene axes at spawn
(`IntegratedSceneReceiver.cs:237-238`). As printed, a reader given Rule A would
conjugate the body rotation and get the figure facing the wrong way — the exact defect
the code comment at `IntegratedSceneReceiver.cs:29-34` records as having occurred.

**X-3 (C6-15). Equation (6.5) is called "the world rotation written to a bone" but omits
the levelling factor; under the Section 6.4 parent it is the *unlevelled* local
rotation.**
Sentence at `build_ch6.py:327`; equation at `build_ch6.py:329`
(`R_bone = A R_chain R_rest`). The code writes
`bone.rotation = qA * qChain * c_rest` where `qA = anchor.rotation`
(`IntegratedSceneReceiver.cs:357, 370-374`) — the anchor's **world** rotation. The
anchor is parented to the levelled node (`IntegratedSceneReceiver.cs:159-163`,
`anchor.SetParent(world,false)`, `anchor.localRotation = Euler(camera)*Euler(-90,0,0)`)
and that node carries `world.rotation = FromToRotation(gravityUpLocal, up)`
(`ArucoSceneReceiver.cs:212`). So `anchor.rotation = L · A`, and the Unity world bone
rotation is `L A R_chain R_rest`, not `A R_chain R_rest`. The printed equation is the
rotation relative to the **unlevelled display frame {U}**. Section 6.2's closing
sentence (`build_ch6.py:308`) — "both branches inherit the levelled frame as local
poses beneath one parent" — is consistent with the *equation* but contradicts the
*sentence that introduces it*. Compounding it, "world" here is ambiguous between the
thesis's desk world {W} (Section 2.2.1) and Unity's scene world. The worked example
(`build_ch6.py:462`) is correct: "After the anchor **and the levelling**…".

**X-4 (C7-01 wording half). Section 7.3 calls a determinant −1 map "the calibrated
camera-to-scene mapping" and asserts it carries the landmarks into "the same Unity
world frame" as the rig.**
`build_ch7.py:293`. Two separate defects in one sentence: (a) the map is orthogonal
with **det = −1** (Section 3 below) and so is not a rotation in Craig's sense; (b)
"the same Unity world frame" is the floor-dropped levelled scene {S}, while Section 7.2
and Section 7.3.3 report in a *different* frame {L} (same rotation, origin still at the
desk marker, no floor drop) — `eval/gt/eval_rail_scenario.py:51-70`,
`eval/offset/carry.py:68-69` vs `evaluate_ch7_restructured.py:113,118,133`. Both are
called only "world frame"/"this frame"/"the same Unity world frame" in the chapter.
The numbers are unaffected (all three tables report distances, which are invariant),
but the printed claim of frame identity is false as written.

### UNRESOLVED — both, with what is needed

**U-1 (C6-16). `R_rest` in equation (6.5): its two frames cannot be assigned from the
thesis as written.**
`build_ch6.py:329, 331`. It is right-multiplied, so its *role* in the product is
`^{T}_{Bk} R` — from the rig bone's own authored axes {B_k} to the T-pose model frame
{T} in which the streamed chain rotations are expressed. Its *value* in code is the
bone's Unity **world** rotation captured at spawn,
`cHip = hip.rotation` etc. (`IntegratedSceneReceiver.cs:239-243`), i.e. `^{S}_{Bk,0} R`.
Those two readings coincide only if the rig spawns with its body axes coincident with
the scene axes — asserted, but only in a code comment
(`IntegratedSceneReceiver.cs:237-238`), never in the thesis — and only after the forced
T-pose (`AlignArm`, `IntegratedSceneReceiver.cs:217-218, 261-273`). A numerical
coincidence is not evidence the notation is right, so this is not resolvable from the
printed mathematics.
*Needed from the author:* an explicit statement of (i) the frame in which the rest
rotations are captured, (ii) the frame the streamed chain rotations `R_0, R_1, R_2` are
expressed in, and (iii) the assumption that links them (rig spawns unrotated, body axes
= scene axes, arms forced to the T-pose before capture). With those three, `R_rest`
becomes `^{T}_{Bk} R` and the whole of (6.5) can be labelled.

**U-2 (C6-14/C6-28). The frames of `R_0`, `R_1`, `R_2` and of `R_chain` in equation
(6.4) cannot be assigned without the same statement.**
`build_ch6.py:316, 318-321`. Multiplication order is verified against
`IntegratedSceneReceiver.cs:358-374` and AGREES (`R_0 = qRoot`, `R_1 = qSh`,
`R_2 = qElb`; spine = `R_0`, upper arm = `R_0 R_1`, forearm = `R_0 R_1 R_2`; left arm
with `v[8], v[9], v[11], v[12]` negated and the twist `v[10]` kept, matching "every
component except the twist reversed in sign"). What is undetermined is the *frame pair*
each factor relates: the natural Craig reading is `R_1 = ^{trunk}_{upper arm} R` and
`R_2 = ^{upper arm}_{forearm} R`, giving `R_chain^{forearm} = ^{T}_{forearm} R`, but the
chapter never names the trunk or model frame, and the identification of {T} with the
frame `A` maps *out of* is exactly what U-1 leaves open.
*Needed:* the same declaration as U-1, plus a name for the trunk frame that `R_0`
produces.

---

## 2. Frame inventory for Chapters 6–8

Every frame these chapters actually need, with the short label I would use. The thesis
names four of them (in Figure 6.4) and uses at least nine.

| Label | Name in the thesis | Definition | Handed | Where established |
|---|---|---|---|---|
| {C} | "camera frame" | RealSense colour optical: x right, y down, z forward, origin at the optical centre | **right** | Appendix D.3 (`appx` text, D.3); `v1/aruco/frames.py:10-12` |
| {P} | "person space" | {C} with the second axis negated: x right, y up, z forward, same origin | **left** | Ch 3 eq. (3.1); `v1/kinematics/root_frame.py:9-14`; Fig. 6.4 box "Person space — left-handed" |
| {W} | "the world frame", "desk world" | the desk marker's own frame: x, y in the printed plane, z out of the printed face | **right** | Ch 2 §2.2.1; `v1/aruco/frames.py:12-16`; Fig. 6.4 box "Desk world — right-handed" |
| {U} | "display axes", "the display frame" | {W} with the 2nd and 3rd coordinates exchanged; y up | **left** | Ch 6 eq. (6.1); `frames.WORLD_TO_UNITY` (`v1/aruco/frames.py:37-40`); Fig. 6.4 box "Unity scene — left-handed" |
| {S} | (unnamed) "the scene" | {U} rotated by `L` so calibrated gravity → +y, then translated so the drawn floor is at y = 0 | left | Ch 6 §6.4; `ArucoSceneReceiver.cs:212, 308-310`; `check_unity_log.py:97,106` |
| {L} | (unnamed) the evaluation "levelled world" | {U} rotated by the same `L`, **origin left at the desk marker** (no floor drop) | left | `eval/offset/carry.py:54-69`; `eval/gt/eval_rail_scenario.py:51-70` |
| {C'} | (unnamed) | {C}'s own axes re-based by the swap: optical axis = up, image-down = forward — the frame of the Unity sensor node, and the frame `S R_cam S` maps out of | left | `ArucoSceneReceiver.cs:283-284`; implied by Ch 6 eq. (6.3) |
| {M} / {M'} | (unnamed) | the marker/object body frame in the world convention (normal = +z) and its swap-re-based form (normal = up) — the frame of the Unity object node | right / left | `ArucoSceneReceiver.cs:135-136`; `frames.unity_from_world` |
| {B_k}, {T} | "the bone's rest rotation", "the T-pose" | each driven bone's authored axes; the model frame at zero arm angles | left | `IntegratedSceneReceiver.cs:217-218, 237-243` — see U-1 |

**Where the handedness changes.** Exactly twice on each measurement branch, and the two
changes cancel on the landmark branch:

- landmark branch: `{C} --F(det −1)--> {P} --A(det +1)--> {U} --L(det +1)--> {S}`
- marker branch: `{W} --S(det −1)--> {U} --L(det +1)--> {S}` (and `{L}` instead of `{S}` in Ch 7)
- direct camera→scene (the map Section 7.3 uses): `{C} --(S R_cam)(det −1)--> {U} --L--> {S}`

Everything from {U} onward ({U}, {S}, {L}) is left-handed and related by proper
rotations. {C} and {W} are right-handed. The two improper factors in the thesis are
`F` and `S`; `A = S R_cam F` is proper because it contains both.

Numerically confirmed on `scene_calibration_r6bc.json` (the rail recording):
`det S = −1`, `det F = −1`, `det R_cam = +1`, `det A = det(S R_cam F) = +1`,
`det L = +1`, `det(S R_cam) = −1`.

---

## 3. THE DETERMINANT −1 MAP — central finding

### 3.1 What the object actually is

The map from the camera frame {C} to the Unity display/scene frame is

```
p_U   = (S R_cam) p_C + S t_cam                     (unlevelled display, {C} -> {U})
p_S   = (L S R_cam) p_C + (L S t_cam + floor_drop)  (levelled scene,    {C} -> {S})
```

Its linear part is **orthogonal with determinant exactly −1**. Verified three ways:

1. Algebraically: `det(S R_cam) = det(S)·det(R_cam) = (−1)(+1) = −1`; `L` is a proper
   rotation so levelling does not change the sign.
2. Numerically from the calibration (r6b): `S R_cam =`
   `[[0.9997, −0.0219, −0.0105], [−0.0243, −0.8752, −0.4831], [−0.0014, −0.4832, 0.8755]]`,
   `det = −1.0000`.
3. From the committed evidence file the Chapter 7 pipeline itself writes. The variable
   is literally named `camera_to_unity_linear`
   (`writing/v8/condensed/scripts/evaluate_ch7_restructured.py:125`,
   `camera_to_unity_linear = (G @ P @ T[:3,:3])`), and
   `writing/v8/condensed/audit_evidence/ch7_restructured/human.json` holds it for both
   recordings:
   - r6b: `[[0.998937, −0.043432, −0.015417], [−0.042529, −0.997597, 0.054703], [0.017755, 0.053989, 0.998384]]`, **det = −1.000000**, translation `(−0.006777, 0.873916, −0.562132)` m
   - r7: `[[0.999262, −0.037224, −0.009451], [−0.036475, −0.996888, 0.069891], [0.012023, 0.069495, 0.997510]]`, **det = −1.000000**, translation `(−0.011389, 0.856303, −0.559333)` m

   Orthogonality error `max|MMᵀ − I| ≈ 1.9e−15`. It is an exact improper orthogonal
   map (a rotation composed with a reflection), not a rotation.

It is used in the {C}→{S} direction at `evaluate_ch7_restructured.py:133` (measured
landmarks into the rig's frame), and in the inverse direction {S}→{C} at
`eval/unity_check/check_unity_log.py:147-153` (`to_pixels`: `M.T`, then `* [1,−1,1]`,
which reduces to `R_camᵀ S`, likewise det −1) and at
`eval/occlusion/fusion_display.py:42-45, 62-63` (`Ginv = world.G.T`,
`Minv = inv(world.M)`, then `* [1,−1,1]`). Both inverses are correct for the stated
direction: `(S R_cam)^{-1} = R_camᵀ S`, and the transposes present are required.

### 3.2 How the thesis currently describes it

- Chapter 6 never prints it as a named symbol. It appears only factorised inside
  `A = S R_cam F`, and Chapter 6 is **honest about the pieces**: "Its determinant is
  minus one, as is that of the flip F, so each changes the handedness of the frame"
  (`build_ch6.py:277`) and "The determinant of A is minus one times plus one times
  minus one, so the two handedness changes cancel. A is a proper rotation"
  (`build_ch6.py:290`). Both statements are correct. Figure 6.4 labels every frame's
  handedness and its banner says "Each single map reverses handedness once; the anchor
  composes two of them, so it is a plain rotation and the person is not mirrored"
  (`writing/v7/scripts/make_ch6_frames_fig.py:120-122`). Chapter 6 therefore does not
  currently assert anything false about determinants.
- Chapter 7 §7.3 names the composite in prose as "**The calibrated camera-to-scene
  mapping**" (`build_ch7.py:293`) with no determinant, no handedness note, no symbol
  and no frames. This is the one place the det −1 object is invoked as a single entity,
  and it is the place where Craig labelling would be applied.

### 3.3 The collision, stated for the author to decide

The new rule says *every printed R and T must carry both frames*. Craig's `^A_B R`
denotes an orthonormal matrix with **det +1**. The camera-to-scene map has det −1.
Giving it `^S_C R` would satisfy the letter of the rule while asserting something false
about the matrix — and worse, it would license Craig's frame-cancellation rule
`^A_B R ^B_C R = ^A_C R` across it, which **does not hold here**. Concretely:

- For the object pose the code computes `R_U = S R_w S` (`v1/aruco/frames.py:85-87`),
  a *conjugation*. The naive Craig chain `^U_W R · ^W_M R = S R_w` gives a det −1
  matrix, which is not a valid Unity rotation at all and is a physically wrong
  orientation. Craig cancellation fails precisely because `S` is not a rotation.
- Equivalently, the {W}→{U} step on a full pose is a **similarity**
  `^U_{M'} T = Σ · ^W_M T · Σ^{-1}` (Σ the affine map built from `S`), not a Craig left
  composition. It re-bases the body frame at the same time as the reference frame.
  This is why the live link at `v2/common/object_link.py:109-111` writes
  `T = T_cam_desk @ make_T(W @ R_u @ W, W @ t_u)` — the un-swap is done blockwise by
  conjugation *first*, and only the resulting genuine `^C_W T` is composed by the Craig
  rule.

**Recommendation (for the author to accept or overrule; I have not applied it).**
Do not give any det −1 matrix Craig rotation notation. Instead:

1. Declare `S` and `F` once, explicitly, as **handedness-changing basis maps, not
   rotations**, each with an explicit direction, in a distinct typeface or with a
   distinct letter class from `R`. A form that carries both frames without claiming
   rotation-hood, e.g. `^U_W S` with a one-line definition "`^U_W S` re-expresses a
   {W}-vector in {U}; `det ^U_W S = −1`, so it is not a rotation and the chain rule of
   Craig §2 does not apply across it", satisfies the semantic requirement honestly.
2. Where a *pose* crosses such a map, print the similarity explicitly
   (`^U_{M'} R = ^U_W S · ^W_M R · ^W_U S`) and **name the re-based body frame {M'}**.
   That single addition converts the conjugation from an unexplained rule into a
   Craig-legal statement and resolves CONTRADICTS X-2 at the same time.
3. Give the Chapter 7 §7.3 composite a symbol with both frames and an explicit
   determinant statement, e.g. `^S_C X` with "`X` is orthogonal with `det X = −1`: it
   changes handedness, because {C} is right-handed and {S} is left-handed. It is not a
   rotation." Then replace "the same Unity world frame" with the actual frame name and
   distinguish {S} from the {L} of §7.2/§7.3.3.
4. Keep `A` as a genuine rotation, but state that both {P} and {U} are left-handed, so
   `^U_P R = A` is orthonormal with det +1 while relating two left-handed frames —
   Craig's algebra carries over, Craig's right-handed assumption does not.

---

## 4. Chapter 6 — item inventory

Location column: `build_ch6.py` line, then the equation number or the sentence.
Every item's direction was checked against the code cited.

### 4.1 Section 6.1.2 — the branch link

**C6-27 · UNLABELLED.**
`build_ch6.py:258`, sentence: "Bringing that pose back into camera coordinates undoes
the axis swap of Section 6.2 and applies the calibrated anchor of Section 2.2.2, so the
round trip returns the measured pose."
*Maps:* object pose from {U} to {C}. *Translation frame:* the composite translation is
the desk-marker origin expressed in {C}. *Order verified:*
`v2/common/object_link.py:109-111` — `T = T_cam_desk @ make_T(W R_u W, W t_u)`, i.e.
the un-swap (conjugation on the rotation block, single multiplication on the
translation) produces `^W_M T`, and `^C_W T` is composed on the **left**. Craig chain
`^C_W T ^W_M T = ^C_M T` holds for that second step. *Transpose/inverse:* none present
in the code; `T_cam_desk` is already `^C_W T` and needs no inversion. **AGREES on
direction and order; no symbol and no frames printed.** Craig form: `^C_M T = ^C_W T
^W_M T`, with the un-swap shown as the similarity of §3.3.

**C6-28 · UNLABELLED.** `build_ch6.py:251` Table 6.1 rows: "pelvis position in person
space", "object position and orientation in display axes", "the frozen scene
description of Table 2.3, already in display axes". Frames are named in words but never
as labels, so nothing in an equation can refer to them.

**C6-29 · UNLABELLED.** `build_ch6.py:260`, "the object pose by a straight line in
position with a shortest-arc path in orientation". A rotation interpolation; the frame
it is performed in ({U}) is not stated. No symbol printed.

### 4.2 Section 6.2, equation (6.1)

**C6-01 · UNLABELLED.** `build_ch6.py:271-275`, eq. (6.1), `p_U = S p_w`.
*Maps:* {W} → {U}. *Translation:* none (pure linear map).
*Order verified:* `frames.unity_from_world` returns `WORLD_TO_UNITY @ t_w`
(`v1/aruco/frames.py:85-87`). *Inverse present:* none; `S = S^{-1}`.
*Operator or frame-relative:* a **basis change** (frame-relative), not an operator on a
vector — it re-expresses one physical point.
Craig form: `^U P = ^U_W S ^W P`, with `^U_W S` declared as a det −1 basis map (§3.3).
`p_U` and `p_w` do carry their frame as a subscript; Craig writes it as a leading
superscript.

**C6-02 · UNLABELLED.** `build_ch6.py:271-275`, eq. (6.1), `R_U = S R_w S`.
*Maps:* re-expresses the object/marker orientation from the {W} representation to the
{U} representation. Established from `v1/aruco/frames.py:85-87`
(`WORLD_TO_UNITY @ R_w @ WORLD_TO_UNITY`) and from what the consumer does with it: the
Unity node's local axes are the swap-re-based marker axes
(`ArucoSceneReceiver.cs:135-136`, plate plane = local x/z, normal = local up; sensor
node `:283-284`, optical axis = local up). *Order verified:* conjugation, both sides.
*Transpose/inverse:* `S` appears twice; since `S = S^{-1}` the second factor **is** the
required `S^{-1}` and is necessary. *Determinant:* `det R_U = det R_w = +1`, so `R_U`
is a valid rotation in the {U} representation.
Craig form: `^U_{M'} R = ^U_W S · ^W_M R · ^W_U S`, where {M'} is the re-based marker
frame — this is **not** `^U_W R ^W_M R` and must not be written as one.
**The formula AGREES with the code; its stated justification does not (see X-2).**

**C6-03 · UNLABELLED (honesty flag).** `build_ch6.py:273-275`, the printed numeric `S`,
and `:277` "Its determinant is minus one, as is that of the flip F, so each changes the
handedness of the frame." The determinant statement is **correct and verified**
(`det S = −1`, `det F = −1`). The symbol carries no frames. Cannot take `^U_W R`.

**C6-13 · CONTRADICTS.** `build_ch6.py:277` vs `:306`. Full statement in X-2 above.

### 4.3 Section 6.2, equation (6.2)

**C6-05 · UNLABELLED.** `R_cam` (`build_ch6.py:191`, used at `:283, 287`).
*Is:* the calibrated camera orientation **relative to the world**, `det = +1`, verified
as `inv(calib["T_cam_desk"])[:3,:3]` (`check_unity_log.py:90-91`,
`carry.py:59-60`; numerically `[[0.9997,−0.0219,−0.0105],[−0.0014,−0.4832,0.8755],
[−0.0243,−0.8752,−0.4831]]`, matching the printed matrix at `build_ch6.py:398-401`).
*Frame-relative*, not an operator. Craig form: **`^W_C R`**.

**C6-06 · UNLABELLED.** `t_cam` (`build_ch6.py:192`, used at `:282, 287`).
*Is:* the camera origin **expressed in {W}** — verified numerically,
`t_dc = (−0.0135, −0.3931, 0.4315)` m, matching the printed `(−0.01, −0.39, 0.43)`.
Craig form: **`^W P_CORG`**.

**C6-07 · UNLABELLED.** `S t_cam` (`build_ch6.py:282`, `:410`).
*Is:* the same camera origin **expressed in {U}**, `(−0.0135, 0.4315, −0.3931)` m,
matching the printed `(−0.01, 0.43, −0.39)`. Craig form: **`^U P_CORG`**.

**C6-08 · UNLABELLED.** `A = S R_cam F` (`build_ch6.py:282-283`).
*Maps:* {P} → {U}. *Determinant:* `+1` (verified: `det M = 1.0000`,
`check_unity_log.py:92`, `carry.py:60` — the code's own comment on that line is
"person space -> local"). *Translation:* none; `A` is the rotation block only, the
translation is the separate `S t_cam` term. *Order verified:* `P @ R_dc @ D` applied as
`M @ q` in `check_unity_log.py:138-139` and `evaluate_ch7_restructured.py:118`.
*Transpose/inverse:* none present; the inverse used elsewhere is `M.T`
(`check_unity_log.py:149`), correct because `M` is orthogonal.
*Frame-relative*, not an operator. Craig form: **`^U_P R`**, with the declaration that
{P} and {U} are both left-handed. The thesis's "A is a proper rotation" is true as a
statement about the matrix.

**C6-09 · UNLABELLED.** `T_WC` (`build_ch6.py:198`, used in prose at `:287, 289`).
*Is:* the calibrated camera pose in the world, verified as `inv(T_cam_desk)`; the
thesis's letter order already matches Craig. The form `T_WC` is explicitly banned by the
new rule. Craig form: **`^W_C T`**.

**C6-10 · UNLABELLED.** `T_UP` (`build_ch6.py:199`, eq. (6.2) at `:284-285`).
*Maps:* {P} → {U}; rotation block `A` (det +1), translation column `S t_cam` expressed
in {U}. Verified: `p_U = M q + cam_pos_u`, `check_unity_log.py:138-139`. This **is** a
legitimate Craig homogeneous transform (both frames left-handed, rotation block proper).
Craig form: **`^U_P T`**, and `^U P = ^U_P T ^P P`.

**C6-11 · MISLEADING.** `build_ch6.py:287-290`, the prose after (6.2):
"`T_UP` is the same map as one homogeneous transformation matrix, the product of the
4 by 4 forms of the swap, `T_WC` and the flip… by the standard chaining of homogeneous
transformations [42]."
*Verified:* the factorisation is arithmetically exact —
`S₄ · T_WC · F₄ = [[S R_cam F, S t_cam],[0,1]] = T_UP`, and the frame order
{U}←{W}←{C}←{P} does cancel correctly. **But** two of the three factors (`S₄` and `F₄`)
have det −1 rotation blocks and are therefore **not homogeneous transformations in
Craig's sense at all**. Calling this "the standard chaining of homogeneous
transformations" invites the reader to apply frame cancellation across `S`, which fails
for rotations (C6-02). The order and direction AGREE; the *characterisation* misleads.

### 4.4 Section 6.2, equation (6.3)

**C6-12 · UNLABELLED.** `build_ch6.py:294-304`, eq. (6.3):
`A = S R_cam F = S R_cam (S S) F = (S R_cam S)(S F)`, `S F = R_x(−90°)`.
*Verified numerically:* `S F = [[1,0,0],[0,0,1],[0,−1,0]] = R_x(−90°)`, det +1.
*Verified in code:* `anchor.localRotation = Quaternion.Euler(posesEuler[2]) *
Quaternion.Euler(−90,0,0)` (`IntegratedSceneReceiver.cs:161-163`), with
`posesEuler[2]` the camera's Unity ZXY Euler, i.e. the Euler of `S R_cam S`
(`calibrate_scene.py` → `frames.unity_from_world`). So the two printed factors are
exactly the two the receiver composes. **AGREES on order and value.**
*Frames:* `S R_cam S` is the camera orientation re-based into display axes, i.e.
`^U_{C'} R` with {C'} the swap-re-based camera frame (`ArucoSceneReceiver.cs:283-284`).
`S F = R_x(−90°)` is then **`^{C'}_P R`** — a genuine det +1 rotation. Proposed:
`^U_P R = ^U_{C'} R · ^{C'}_P R`. This factorisation is Craig-legal and is the one
honest way to write (6.3), because the two improper factors pair off inside it.
*Note:* `R_x(−90°)` is here a frame-relative transform, not "a rotation of minus ninety
degrees" applied to anything — the thesis's phrasing ("the matrix of a rotation of minus
ninety degrees about the x axis") is operator language for a frame-relative object.

**C6-30 · AGREES.** `build_ch6.py:306`, "The first factor is the orientation the display
already uses to place the sensor body in the scene, so the receiver needs no new
mathematics. It creates one static anchor node at the calibrated camera pose composed
with that constant rotation." Verified exactly against
`IntegratedSceneReceiver.cs:159-163`. Substance correct; no symbol printed.

### 4.5 Section 6.3 — the rig

**C6-14 · UNRESOLVED (U-2).** eq. (6.4), `build_ch6.py:318-321`. Order AGREES with
`IntegratedSceneReceiver.cs:358-374`; frames undeterminable — see U-2.

**C6-15 · CONTRADICTS (X-3).** eq. (6.5) and its introducing sentence,
`build_ch6.py:327, 329`.

**C6-16 · UNRESOLVED (U-1).** `R_rest` in eq. (6.5), `build_ch6.py:329, 331`.

**C6-17 · AGREES.** `build_ch6.py:337`: "Each tick the receiver maps the streamed pelvis
point through the anchor. It translates the root so that the spine bone lands on that
point, and the root rotation orients the trunk about it."
This sentence **does** make Craig's Chapter-2 distinction correctly, and it is the one
place in the chapter that does. Verified in `IntegratedSceneReceiver.cs:378-379`:
`Vector3 target = anchor.TransformPoint(pelvis); rigRoot.position += target -
hip.position;`. `anchor.TransformPoint` is a **frame transform** (`^S_P T`, the anchor's
world matrix); `rigRoot.position += …` is a **re-anchoring translation operator**
applied to the whole rig, which changes no bone rotation. The thesis's two clauses map
onto exactly those two things. Frames still unnamed.

**C6-18 · AGREES.** `build_ch6.py:333`, proportions: "the avatar setup scales the
character uniformly to 170 centimetres… a uniform scale leaves every rotation
unchanged." Verified: `rigRoot.localScale *= appliedScale`
(`IntegratedSceneReceiver.cs:195-196`), per-bone `hip.localScale *= st` and
`MatchArm` (`:220-233, 275-290`). These are **similarity scalings, not transforms and
not operators on orientation** — correctly described, and correctly identified as the
reason the rendered hand misses the measured wrist (`build_ch6.py:363` note; Ch 6
worked frame-114 discussion). Also verified: the T-pose forcing `AlignArm`
(`:217-218, 261-273`) is a **pre-multiplied operator** on each bone's current
orientation (`up.rotation = FromToRotation(d1, axis) * up.rotation`), and the thesis
calls it "rotating each arm segment so that it points straight out to the side" —
operator language for an operator. Correct.
*The brief's rig question is therefore answered:* the anchor is a frame transform, the
pelvis pinning is a re-anchoring translation, the proportion matching is a scaling, and
the T-pose forcing is an operator. **The thesis's language distinguishes all four**;
only `R_rest` (U-1) and the "world rotation" label (X-3) are defective.

### 4.6 Section 6.4 — levelling

**C6-19 · UNLABELLED.** `build_ch6.py:345`: "It rotates that node by the shortest
rotation that carries the gravity direction of Section 2.2.2 onto the screen's
vertical, then raises it so that the floor sits at zero height."
*Verified:* `world.rotation = Quaternion.FromToRotation(gravityUpLocal, Vector3.up)`
(`ArucoSceneReceiver.cs:212`) and `world.position += Vector3.down * floorY` with
`floorY = world.TransformPoint(floor_pt).y` (`:308-310`); reproduced independently as
`G = from_to_rotation(g, [0,1,0])`, `world_pos = [0, −(G @ floor_pt)[1], 0]`
(`check_unity_log.py:97, 106`) and asserted against the receiver's own log to
`< 1e−3` m (`check_unity_log.py:138-142`; `evaluate_ch7_restructured.py:118-120`).
*Direction:* {U} → {S}. *Determinant:* +1. **AGREES on direction and order; unnamed.**
*Operator vs frame-relative:* the sentence describes it as an **operator** ("rotates
that node"), and the worked example then uses it as a **frame map** (`p_scene = L p_U +
…`). Both are true here because the node's local coordinates are {U} coordinates, but
Craig requires the thesis to say which.

**C6-20 · UNLABELLED.** Worked example, `build_ch6.py:429-434`:
`L = [[1.00,0.02,0.01],[−0.02,0.85,0.53],[0.01,−0.53,0.85]]`,
`p_scene = L p_U + (0, 0.72, 0) = (0.00, 0.75, 0.44)` m.
*Reproduced exactly:* `G` from the r6b calibration is
`[[0.9998,0.0212,0.0061],[−0.0212,0.8477,0.5300],[0.0061,−0.5300,0.8480]]`; the
levelling angle is 32.04°; `L p_U = (0.0003, 0.0320, 0.4381)`, raise `0.716215` m,
`p_scene = (0.0003, 0.7482, 0.4381)` m. All printed values check out.
*Translation frame:* `(0, 0.716, 0)` is expressed in **{S}** (added after the rotation)
— correct. Craig form: **`^S_U R = L`, `^S P_UORG = (0, 0.716, 0)`**, so
`^S P = ^S_U T ^U P`.
*Symbol collision:* `L` here is also `L_j`, the physical segment length, in Chapter 7
eq. (7.1) (`build_ch7.py:228-231`). Flagged in §6.

### 4.7 Section 6.5 — worked example

**C6-21 · UNLABELLED.** `build_ch6.py:397-402`, printed `R_cam` and `t_cam` numerics.
Values verified against `T_cam_desk` of `scene_calibration_r6bc.json` — exact.
Craig: `^W_C R`, `^W P_CORG`.

**C6-22 · UNLABELLED.** `build_ch6.py:405-410`, `A = S R_cam F` numeric and `S t_cam`.
Verified exact (`M` above). Craig: `^U_P R`, `^U P_CORG`.

**C6-23 · UNLABELLED.** `build_ch6.py:412-416`, `q = (0.03, −0.18, 0.99)` m,
`p_U = A q + S t_cam = (0.00, −0.21, 0.39)` m. Reproduced exactly
(`A q + S t_cam = (0.0021, −0.2052, 0.3888)`). `q` carries **no frame label** at all
(it is the person-space pelvis). Craig: `^P P`, `^U P`.

**C6-24 · UNLABELLED.** `build_ch6.py:417`, the three-step narration: "Undoing the flip
gives the raw camera point (3.0, 17.9, 99.2)… The calibrated camera orientation and
position carry it into the world frame, (0.2, 38.9, −20.5), and the swap exchanges the
last two coordinates." Reproduced exactly (`F q = (0.0302, 0.1791, 0.9917)`;
`R_cam F q + t_cam = (0.0023, 0.3885, −0.2051)`; `S` of that `= p_U`). Every frame is
named in words ({P}, {C}, {W}, {U}) and none as a label. **AGREES on substance.**

**C6-25 · UNLABELLED.** `build_ch6.py:442-448`, `R = R_cam^T`, `t = (0.02, 0.19, 0.55)`.
*Is:* the rotation block and translation column of `^C_W T` = `calib["T_cam_desk"]`
(verified exactly: translation `(0.023458, 0.187377, 0.552492)`). *Transpose:* present
and **required** — `^C_W R = (^W_C R)ᵀ`. *Translation frame:* {C} — the desk-marker
origin seen from the camera, correct. Craig: `^C_W R`, `^C P_WORG`; and the whole step
`^C_M T = ^C_W T ^W_M T`. **AGREES on direction, transpose and order.** The bare `R`
and `t` here also collide with `R_cam`, `R_bone`, `R_chain`, `R_0..R_2` and with
Appendix E's bare `R`.

**C6-26 · MISLEADING.** `build_ch6.py:452-456`, `p_W = S p_U = S(−0.23,−0.19,0.43) =
(−0.23,0.43,−0.19)`. The **same bare symbol `S`** that equation (6.1) defines as
{W}→{U} is here used {U}→{W}. Numerically harmless (`S = S^{-1}`, and the chapter does
say so once at `:277`), but the printed notation gives the reader no way to tell which
direction any given `S` is acting in. Under the new rule this is the banned ambiguity.
Craig: `^W P = ^W_U S ^U P`.

**C6-31 · UNLABELLED.** `build_ch6.py:452-456`, `p_C = R p_W + t = (−0.21, 0.15, 1.02)`
m. Reproduced exactly (`(−0.206489, 0.150504, 1.020790)`). `p_W` and `p_C` do carry
their frames as subscripts; note the case inconsistency with eq. (6.1)'s `p_w`.

**C6-32 · UNLABELLED.** `build_ch6.py:474-476`, Table 6.2 rows "Link | swap undone,
anchor applied | cube marker origin … in the camera frame" and "Receiver, position |
equation (6.2) and the levelling | … in display axes; … in the scene". Frames in words
only.

**C6-33 · MISLEADING.** Figure 6.4 caption, `build_ch6.py:267`: "The **four** coordinate
frames and the three maps between them."
The figure itself is good — it names four frames and, uniquely in the thesis, states
each one's handedness (`make_ch6_frames_fig.py:85-99`: Camera frame right-handed,
Person space left-handed, Desk world right-handed, Unity scene left-handed). But the
chapter needs at least the nine frames of §2: the levelled scene {S} appears two
sections later and in the worked example, the re-based {C'} is implicit in eq. (6.3),
{M'} is implicit in eq. (6.1), and the rig frames appear in (6.4)/(6.5). The definite
article "the four coordinate frames" asserts completeness the chapter does not keep.

---

## 5. Chapter 7 — item inventory

Chapter 7 prints **no rotation-matrix or homogeneous-transform symbol anywhere** —
equations (7.1) to (7.6) contain only `L_j`, `q_j`, `A_j`, `R_j`, `p_i`, `c`, `C`, `u`,
`I`, `d_i`, `e_{k,t}`, `e_{m,k,t}`. Every transform in this chapter is invoked in prose
or in a caption. That is itself the chapter's principal notation defect under the new
rule: the frames in which its numbers live are never named.

**C7-01 · CONTRADICTS (X-4).** `build_ch7.py:293`, "The calibrated camera-to-scene
mapping carries the measured landmarks into the same Unity world frame."
*Is:* `p_S = (L S R_cam) p_C + (L S t_cam + floor_drop)`, linear part **det −1**
(§3). *Established from:* `evaluate_ch7_restructured.py:125` (`camera_to_unity_linear`)
and `:133` (`measured = (G @ (P @ T[:3,:3] @ raw + cp)) + offset`), with `raw` the
**raw camera-frame** MediaPipe+depth landmark. *Translation frame:* {S}.
*Order verified:* rotate then translate then level then drop, as written.
*Transpose/inverse:* none in this direction; the inverse used for reprojection
(`check_unity_log.py:149`) uses `M.T`, valid because `M` is orthogonal.
Craig form: `^S P = ^S_C X ^C P` with `^S_C X` declared improper (det −1).
Two defects, both in §1 X-4: det −1 not stated, and the frame identity claim is wrong
({S} vs {L}).
*Note on the pelvis path in the same function:* `expected_hip` at
`evaluate_ch7_restructured.py:118` uses `M = P @ T[:3,:3] @ D` (det **+1**) because its
input is the **person-space** pelvis, while `measured` at `:133` uses
`P @ T[:3,:3]` (det **−1**) because its input is a **camera-frame** landmark. Both are
correct for their inputs. The thesis names neither input frame.

**C7-02 · UNLABELLED.** `build_ch7.py:286`: "Segment lengths are invariant under the
levelling rotation applied to the stored track, so the choice of world frame cannot
change Tables 7.1 and 7.2."
*Is:* `L` (= `G`) applied as `world.level(p) = G p` (`eval/offset/carry.py:64, 68-69`),
called from `eval/gt/eval_rail_scenario.py:64-66`. *Direction:* {U} → {L}.
*Determinant:* +1, so it is an isometry and the invariance claim is **correct**.
*Translation:* none — `LeveledWorld.level` applies no offset, and heights are taken as
`obj[:,1] + drop` (`carry.py:85-86`). **AGREES on substance.** No symbol, no frames.
Craig: `^L_U R`. The second half of the sentence ("the fitted-line scatter components,
the line tilt and the axis-dominance checks … are properties of that frame and are not
invariant") is also correct — components and tilt-from-horizontal are frame-dependent,
though the scalar perpendicular distances `d_i` of eq. (7.4) are in fact invariant.

**C7-03 · UNLABELLED.** Figure 7.1 and 7.2 captions, `build_ch7.py:251` and `:274`:
"The physical route is not registered into **this frame** and is not drawn."
*The frame is:* {L} — "Marker-centre track in the GRAVITY-LEVELLED desk world (x, y up,
z), metres, **origin at the desk marker**" (`eval/gt/eval_rail_scenario.py:51-58`).
Craig-style naming needed: {L}, origin = desk-marker origin, +y = calibrated gravity up,
left-handed.

**C7-04 · MISLEADING.** Figures 7.3 and 7.4 captions, `build_ch7.py:320, 325`:
"in **the same Unity world frame**", "the vertical plot axis is Unity y".
*The frame is:* {S} (with the floor drop), `evaluate_ch7_restructured.py:113, 133`.
This is **not** the frame of Figures 7.1/7.2 and Section 7.3.3; they differ by the
floor-drop translation. Calling both "the … world frame"/"this frame" asserts an
identity that does not hold. Numbers unaffected (distances only), notation wrong.

**C7-05 · MISLEADING.** `build_ch7.py:377`: "The proxy and reconstructed wrist are
compared in **the same camera-derived coordinate frame**."
*Established:* Table 7.8 (clean-frame proxy separation) is computed in the **camera
frame {C}** — `evaluate_ch7_restructured.py:265-271` compares the filtered landmark
(camera-frame CSV columns) against `label['xyz_cam']` (camera-frame click deprojection,
`eval/failure/label_wrists.py:93`). Table 7.9 (occluded-frame method comparison) is
computed in **person space {P}** — `eval/failure/eval_labeled_recovery.py:122` maps the
proxy by `unity_from_sensor(L["xyz_cam"])` before comparing it with the forward-kinematic
wrists. Two different frames, related by the det −1 flip `F`. Because `F` is an isometry
every reported distance is identical either way, so **no number is wrong**; the sentence
asserting a single frame is. Needs: name {C} for Table 7.8 and {P} for Table 7.9, or say
that the two are isometric so the distances agree.

**C7-06 · UNLABELLED.** §7.3.3, `build_ch7.py:353-372`: the wrist-to-marker separations.
*Frame:* {L} — `evaluate_ch7_spatial_check.py:160-163` uses
`world.wrist_world(cam)` (= `G(S R_cam p_C + S t_cam)`, `carry.py:71-73`) and
`ers.load_track(stem)['xyz']` (= `G p_U`). Both in {L}; distances are frame-invariant.
The chapter never names the frame.

**C7-07 · UNLABELLED.** Equation (7.5), `build_ch7.py:294-299`:
`e_{k,t} = ||p^{Unity}_{k,t} − p^{measured}_{k,t}||`. The superscripts name the
**provenance** of each number, not the **frame** it is expressed in. Craig requires a
difference of two position vectors to show a common frame: both are in {S}
(`evaluate_ch7_restructured.py:133-137`). Proposed: `^S p^{rig}` and `^S p^{meas}`.
Same for equation (7.6), `build_ch7.py:415-419` (`masked`/`unmasked`, both in {P}
via `rc.run_variant`).

**C7-08 · UNLABELLED.** Equations (7.2)–(7.4), `build_ch7.py:233-239`: the PCA line fit
is performed in {L} (the samples `p_i` come from `ers.load_track`). Frame never stated,
although §7.2's own closing sentence (C7-02) turns on which frame it is.

**C7-09 · AGREES.** `build_ch7.py:240`: "The physical route is not registered into the
calibrated world frame, so no physical path or physical waypoint coordinate is drawn or
reported." Correct and consistent with the absence of any tape-measure→{W} transform in
the code.

---

## 6. Chapter 8 — item inventory

Chapter 8 prints **no rotation or transform symbol** either.

**C8-01 · UNLABELLED (direction AGREES).** `build_ch8.py:164`: "Live it reads the newest
record the marker branch published and rebuilds the object pose by undoing the axis swap
of Section 6.2 and the calibrated anchor of Section 2.2.2."
Verified line by line against `v2/common/object_link.py:104-111`:
skew guard `abs(skew) > SKEW_MAX` (=3, `:82`) matching "more than three frames";
`t_u`, `R_u = recompose_zxy(euler)`; `T = self.T_cam_desk @ make_T(W @ R_u @ W, W @ t_u)`;
returns `(T[:3,3], T[:3,:3])`. Direction {U} → {W} → {C}, order and conjugation exactly
as Chapter 6 describes. Craig: `^C_M T = ^C_W T ^W_M T`.

**C8-02 · UNLABELLED.** Table 8.1 row, `build_ch8.py:148`: "newest published marker
record, **rebuilt in camera coordinates**". Frame named in words ({C}); no label.

**C8-03 · UNLABELLED.** `build_ch8.py:174` and Figure 8.3 caption `:206`: "Figure 8.3
draws both chains on the colour frame… both on the measured shoulder of the frame."
*Established:* `make_ch8_compare_figs.py:167-183` — the shoulder is taken in the camera
frame, mapped to {P} by `unity_from_sensor`, the chain is built in {P} with
`R_root @ up`, `R_root @ fore`, then `project()` applies `P_sol * FLIP` ("back to the
camera frame") and the colour intrinsics. Direction and order correct; the two frames
({P} for the chain, {C} for the projection) are not named in the caption.

**C8-04 · AGREES.** `build_ch8.py:164`, "The two capabilities marked as a new data path
needed no new mathematics." Correct: the live link reuses `frames.WORLD_TO_UNITY` and
`recompose_zxy` unchanged (`object_link.py:71`).

---

## 7. Appendices A–H — what I covered

All eight were dumped and swept for rotation matrices, homogeneous transforms, position
vectors and transform compositions.

| Appendix | Transforms present | Belongs to | Action |
|---|---|---|---|
| A — RGB-D acquisition | none | Ch 2 | nothing to audit |
| B — hardware/software | none | — | nothing to audit |
| C — landmark detection | camera-frame positions only, no transform | Ch 2/3 | nothing in my scope |
| D — depth and deprojection | eq. (D.1), (D.2) projection/deprojection (not frame transforms); one transform in prose, D.2 "moved into the colour camera's frame through the known transformation between the two imagers" — unnamed, no symbol | Ch 2 (other agent) | **noted, not mine**; but see the naming clash below |
| E — marker detection | bare `R` and `t` (E.2, E.4), eq. (E.1) Rodrigues, worked `R`, `w`, `w×` | Ch 2 / Ch 4 (other agent) | **noted, not mine**: `R` and `t` are `^C_M R` and `^C P_MORG` (verified: the printed `t = (0.02, 0.19, 0.55)` for the desk marker is identical to `T_cam_desk[:3,3]`, and Chapter 6's worked example reuses that same column) |
| F — candidate filters | none | Ch 2 | nothing to audit |
| G — hip depth preparation | eq. (G.1) is a scalar ray rescaling, not a transform; **person space is labelled "P"** in G's opening sentence | Ch 2 §2.6 / Ch 5 | **noted**: this is the only place the thesis gives a frame a letter label, and it is "P" for person space — consistent with my proposed {P} |
| H — kinematic solver verification | none | Ch 3 | nothing to audit |

**Conclusion: no appendix section carries a transform that belongs to Chapter 6, 7 or 8.**

One cross-appendix naming clash that bears directly on my chapters:
**Appendix D.3 calls person space "the left-handed convention Unity uses"**
("Converting the camera-frame point into the left-handed convention Unity uses is a
separate fixed axis flip, developed in Section 3.1"), while Chapter 6 uses "Unity" /
"display axes" for a *different* frame, {U} = swapped desk world. The code has the same
collision (`IntegratedSceneReceiver.cs:14`: "Pipeline-A Unity space = camera frame, y
flipped"). Two distinct frames are both called "Unity". Recommend {P} and {U} with
distinct prose names.

---

## 8. Cross-cutting symbol collisions (all chapters in scope)

1. **`L`** — the levelling rotation (Ch 6 worked example, `build_ch6.py:430`) vs `L_j`,
   the physically measured segment length (Ch 7 eq. 7.1, `build_ch7.py:228-231`) vs the
   printed marker side length `L` (Appendix E.2).
2. **`C`** — if the camera frame is labelled {C}, it collides with the sample covariance
   matrix `C` in Chapter 7 eq. (7.2) (`build_ch7.py:233-236`).
3. **`P`** — Appendix G labels person space "P"; Chapter 7 uses `p_i` for points; the
   code uses `P` for the swap matrix (`carry.py:24`, `check_unity_log.py:88`) and `D`
   for the flip — i.e. the code's `P` is the thesis's `S` and the code's `D` is the
   thesis's `F`. Any cross-reference from thesis to code will mislead unless stated.
4. **bare `R`** — Chapter 6 worked example (`^C_W R`), Appendix E (`^C_M R`),
   Chapter 6 eq. (6.4) (`R_0, R_1, R_2`), and `R_j` = relative error (%) in Chapter 7
   eq. (7.1). Four distinct meanings of `R`.
5. **`S`** — Chapter 6's swap; also the natural label for the scene frame. If {S} is
   adopted for the levelled scene, the swap needs a different letter.
6. **`p_w` vs `p_W`** — eq. (6.1) prints the world point with a lowercase subscript
   (`build_ch6.py:272`), the worked example with an uppercase one (`build_ch6.py:453`).
7. **`A`** — the anchor rotation (Ch 6 eq. 6.2) vs `A_j` = absolute error in cm
   (Ch 7 eq. 7.1).

---

## 9. Suspected wrong directions in the CODE — reported separately

**None found.** Every transformation direction I checked in the code for these three
chapters is correct for what it is used for:

- `frames.unity_from_world` conjugates the rotation and single-multiplies the
  translation — correct for a pose crossing a handedness change where the body frame is
  re-based (`v1/aruco/frames.py:85-87`, consumed by `ArucoSceneReceiver` nodes whose
  local axes are the re-based ones).
- `IntegratedSceneReceiver` pre-multiplies the anchor onto bone rotations and does not
  conjugate — correct, and the code comment records the failure mode of the alternative
  (`:29-34`).
- `check_unity_log.to_pixels` and `fusion_display` both use the exact inverse of the
  forward map, with transposes that are required and valid (orthogonal matrices).
- `object_link` composes `^C_W T` on the left of `^W_M T` — correct Craig order.
- `evaluate_ch7_restructured` uses the det +1 map for the person-space pelvis and the
  det −1 map for camera-frame landmarks — correct for each input.
- `carry.LeveledWorld.object_world` left-multiplies `G` onto the object rotation
  (`carry.py:79`) rather than conjugating — **correct**, because `G` is a proper
  rotation between two left-handed frames, so the Craig chain `^L_M R = ^L_U R ^U_M R`
  does hold there. (This is the contrast that makes X-2's missing criterion visible: the
  code conjugates across `S` and left-multiplies across `G`, and the difference is
  exactly whether the map is improper and re-bases the body frame.)

No numerical value and no transformation direction is proposed for change anywhere in
this report.

---

## 10. How much of this is notation and how much is substance

**Substance — the mathematics and the code are right.** I reproduced every printed
number in the Section 6.5 worked example from the committed calibration and they are
exact: `R_cam`, `t_cam`, `A`, `S t_cam`, `p_U`, `L`, the 32.0° levelling angle, the
0.716 m raise, `p_scene`, `R_cam^T`, `t`, `p_W`, `p_C`. Every multiplication order in
Chapters 6–8 that I could check against the implementation matches it. Every transpose
and inverse that is present is required for the direction stated. Chapter 6's
determinant bookkeeping (`det S = det F = −1`, `det A = +1`) is correct, and Figure 6.4
already carries the handedness of all four frames it draws. I found **no wrong
direction and no wrong composition order** in the thesis or in the code.

**Notation — nearly everything, and it is systematic rather than incidental.** 30 of
46 items are UNLABELLED: Chapters 7 and 8 print no `R` or `T` at all and refer to five
different frames only as "this frame", "the same Unity world frame", "camera-derived",
"camera coordinates" and "display axes"; Chapter 6 prints eleven distinct matrix symbols
(`S`, `F`, `A`, `R_cam`, `R_x(−90°)`, `R_0..R_2`, `R_chain`, `R_bone`, `R_rest`, `L`,
bare `R`) of which none carries a frame pair, plus two banned flat-subscript transforms
(`T_WC`, `T_UP`) whose letter order happens to match Craig already. Bringing these to
Craig form is mechanical once the frame inventory of §2 is declared — with two
exceptions.

**Three items are genuinely substantive and cannot be fixed by relabelling.**

1. **The determinant −1 map (§3).** This is not cosmetic. Under the new rule the honest
   label and the required label pull in opposite directions, and a naive Craig label
   would license a chain rule that produces a *physically wrong object orientation*.
   The author has to choose a notation class for improper maps. My recommendation is in
   §3.3.
2. **CONTRADICTS X-2, the two incompatible conjugation rules.** The chapter states one
   rule, then its negation, for the same class of object, and gives no criterion. The
   criterion exists and is recoverable from the code (re-based body frame or not) but is
   nowhere in the thesis. Fixing this requires a new sentence of *content*, not a
   relabelling.
3. **CONTRADICTS X-3, "the world rotation written to a bone".** Equation (6.5) is a
   local rotation under the levelling parent; the sentence calls it a world rotation.
   That is a false statement about what the code writes, not a missing subscript.

X-1 (the `F` direction reversal) and X-4 (the Chapter 7 frame-identity claim) sit in
between: both are notational in origin, both are numerically harmless because `F` is an
involution and because the affected quantities are distances, but both are *false as
printed* and a reader following the notation rather than the prose would be led wrong.

The two UNRESOLVED items (`R_rest`, and the frames of `R_0..R_2`) need one short
declaration from the author — what frame the rest rotations are captured in, what frame
the streamed chain rotations live in, and the T-pose/spawn assumption that links them.
With that declaration, equations (6.4) and (6.5) become fully labellable and X-3's fix
becomes unambiguous as well.

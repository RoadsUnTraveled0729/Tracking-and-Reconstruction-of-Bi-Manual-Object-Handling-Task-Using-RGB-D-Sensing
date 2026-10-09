# Craig notation audit — Chapter 3 (Kinematic Modeling) and Chapter 5 (Pose Recovery)

Read-only audit. Nothing in the thesis, the builders or the code was edited.
Scope: Chapter 3, Chapter 5, Appendix G (hip depth preparation, feeds the Ch3 solve
and is relied on by Ch5 §5.1) and Appendix H (kinematic solver verification).
Appendices D and E are listed only where they define a frame or a matrix that
Chapter 3 or Chapter 5 consumes; Chapters 2, 4, 6, 7, 8 belong to other agents.

Reference convention (author's instruction, Craig 4th ed. Ch. 2):

    ^A_B R   orientation of {B} relative to {A}; columns are {B}'s axes expressed in {A}
    ^A P_BORG  origin of {B} expressed in {A}
    ^A_B T = [ ^A_B R   ^A P_BORG ; 0 0 0   1 ],   ^A P = ^A_B T ^B P
    ^A_B T ^B_C T = ^A_C T

Verdicts used:

- **AGREES** — direction correct AND both frames already identifiable as printed.
- **UNLABELLED** — direction establishable from the equations/code, but the printed
  symbol omits one or both frames. A defect under the author's second rule.
- **MISLEADING** — the printed notation invites a reading that differs from the
  actual mapping, or conflates two things Craig separates, without flatly
  contradicting a stated fact.
- **CONTRADICTS** — a printed statement is incompatible with the mapping the
  equations and code actually perform.
- **UNRESOLVED** — direction or frame cannot be fixed from the available evidence,
  or the frame needed to write the label does not exist in the thesis.

---

## 0. Summary

| Verdict | Ch 3 | Ch 5 | Appendices | Total |
|---|---|---|---|---|
| AGREES | 1 | 4 | 3 | **8** |
| UNLABELLED | 40 | 22 | 2 | **64** |
| MISLEADING | 6 | 1 | 0 | **7** |
| CONTRADICTS | 2 | 8 | 0 | **10** |
| UNRESOLVED | 3 | 2 | 0 | **5** |
| **Total items** | **52** | **37** | **5** | **94** |

### Every CONTRADICTS item (full list, details in the body)

| ID | Location | What is wrong |
|---|---|---|
| C3-10 | build_ch3.py:221-236, eq (3.5) + the prose after it | `R_sh,r` is the rotation block of `T_el,r`, i.e. it describes the **elbow** frame relative to the **shoulder** frame. Its subscript names the *reference* frame. `R_root` in the same equation names the *described* frame. One subscript slot, two opposite meanings. |
| C3-13 | Chapter 3 as a whole (`R_root`, `R_parent`, `R_sh,r`, `R_arm,r`, `T_root`, `T_sh,r`, `T_el,r`, `T_arm,r`) | The subscript convention is self-inconsistent. `T_*` subscripts consistently name the described frame; `R_sh,r` names the reference frame; `R_arm,r` names neither (a third name for the elbow frame). A reader applying the `R_root` rule to `R_sh,r` concludes `R_sh,r` = shoulder-relative-to-root, which eq (3.13) states is the identity. |
| C5-01 | build_ch5.py:253-256, Table 5.1 row 1 | `p_sh, p_el, p_wr` declared "person space P". Equations (5.1) and (5.2) require `p_wr` in the levelled world frame. |
| C5-02 | build_ch5.py:253-256 + :564-570, Table 5.1 row `o` | "levelled world frame W … Chapter 4, translation column of `T_WO`". Chapter 4's `T_WO` translation column at frame 560 is **(−0.2234, 0.4171, −0.1763)**; Chapter 5 prints **o = (−0.22, 0.08, 0.45)**. The two differ by the Unity y/z swap *and* a 32.04° levelling rotation, neither of which appears in the thesis notation. |
| C5-03 | Table 5.1 row `R_obj` | Same claim for the rotation block. Verified: `R_obj = G · P · (^W_O R) · P` exactly reproduces the printed matrix to two decimals; the bare rotation block of `T_WO` does not. |
| C5-04 | Table 5.1 row `w` | Frame column reads "levelled world frame W, **then P**". One symbol declared to carry two frames, and both are used in printed equations. |
| C5-09 | build_ch5.py:281, eq (5.1) | `p_wr = o + R_obj h` is correct as `^W P_WR = ^W_O T ^O P_WR`, but `p_wr` is the symbol Table 5.1 places in person space. |
| C5-15 | build_ch5.py:367, eq (5.6) | `p_wr = p_el + L2 f̂` is a person-space equation using the same `p_wr` that eq (5.1) uses as a world-frame quantity, five equations earlier. |
| C5-16 | build_ch5.py:380, eq (5.7) | `w` is formed in W, then §5.4's last paragraph carries it into P and §5.5 uses it in P, all under the same glyph. |
| C5-32 | build_ch5.py:524-531, §5.6 | `w = (−0.21, 0.13, 0.48)` and `w = (−0.19, −0.09, 1.04)` are printed within four lines of each other under the same symbol. They are the same physical point in two frames; the y component even changes sign. |

### Every UNRESOLVED item, with what is needed

| ID | Location | What is missing |
|---|---|---|
| C3-22 | build_ch3.py:305-306, Figure 3.5 caption | The caption draws a frame at each wrist ("the wrists x along each forearm"), but Chapter 3 defines no wrist or forearm frame. **Needed:** an author decision on whether {F_r}/{F_l} are part of the chain contract. If yes, they need a definition and a printed transform; if no, the caption must stop drawing them. |
| C3-35 | build_ch3.py:433-435, §3.4.2 | `M = diag(−1, 1, 1)`. det M = −1, so it is **not** a rotation and cannot carry `^A_B R` labels. It produces a mirrored root basis that the thesis never names, and `shoulder.py:152` then passes `np.eye(3)` as the root frame to the right-arm solver, i.e. the mirrored vectors are treated as living in a frame of their own. **Needed:** an author decision on whether to name that mirrored basis (e.g. {B′}) and a statement that M is a reflection operator outside the Craig transform family. |
| C3-39 | Chapter 3 §3.4.3 (no printed equation) | The elbow rotation `^{E_r}_{F_r} R = Ry(e_y) Rz(e_z)` exists in the implementation (`v1/kinematics/shoulder.py:94` docstring; `eval/inspect/check_v1_overlay.py:47-66` `fk_arm_dirs`) and is required for the chain to close at the forearm, but is never printed. **Needed:** an author decision on whether the chain contract ends at {E_r}. If it extends to the forearm, the rotation must be printed and labelled. |
| C5-37 | Chapter 5 Table 5.1 and Chapter 4 §4.1 | The letter **W** denotes two different frames. Chapter 4: the desk-marker frame, right-handed, z out of the card, in which gravity reads (−0.02, 0.53, 0.85), 32.04° from the world z axis (`build_ch4.py:210`). Chapter 5: a left-handed, y-up, gravity-levelled frame. **Needed:** an author decision — give Chapter 5's frame its own letter, or redefine Chapter 4's W (which would falsify Chapter 4's own gravity sentence). I cannot assign `^A_B` labels to Chapter 5's transforms until the letter is decided. |
| C5-38 | Chapter 5 §5.4 vs Chapter 6 eq (6.1) | Chapter 3 §3.1 says "Chapter 6 converts it for Unity with the axis swap of equation (6.1)". The code's swap is `P = [[1,0,0],[0,0,1],[0,1,0]]` (`eval/offset/carry.py:24`), applied to points as `p_U = P p_w` and to rotations as `R_U = P R_w P` (`v1/ARUCO_MODEL.md` §5). **Needed:** Chapter 6's eq (6.1) read against `carry.py:24` by the Chapter 6 auditor, to confirm the swap Chapter 5 silently depends on is the same matrix Chapter 6 prints. Outside my scope to verify. |

---

## 1. Frame inventory

These are the frames Chapters 3 and 5 actually need. Only four of the thirteen
currently have a letter in the thesis.

| # | Proposed label | Frame | Defined where? | Handedness / axes |
|---|---|---|---|---|
| 1 | {C} | camera (sensor optical) | §2.2, Appendix D.3 — **labelled C** | right-handed; x image right, y down, z forward |
| 2 | {P} | person space | §3.1 — **labelled P** | left-handed; x right, y up, z forward; origin shared with {C} |
| 3 | {B} | root / torso | §3.2.2 — **no letter**, only the subscript "root" | origin L24; x̂ subject's right along the hip line, ŷ up the trunk, ẑ out of the chest |
| 4 | {S_r}, {S_l} | shoulder | §3.3.3 — **no letter**, subscript "sh,r"/"sh,l" | origin L12/L11; orientation identical to {B} |
| 5 | {E_r}, {E_l} | elbow / rotated upper arm | §3.3.3 — **no letter**, and addressed by **two** subscripts, "el,r" (relative to {S_r}) and "arm,r" (relative to {P}) | origin L14/L13; {B} turned by the shoulder swing and twist |
| 6 | {E0_r}, {E0_l} | untwisted upper arm (swing applied, twist not) | **nowhere** — required by eq (3.22), which expresses the forearm in it | {B} turned by the swing only |
| 7 | {F_r}, {F_l} | forearm / wrist | **nowhere in the mathematics**; drawn in Figure 3.5's caption and implemented in the code | {E_r} turned by (e_y, e_z) |
| 8 | {B′} | sagittally mirrored root basis (left-arm solve) | **nowhere** — implied by M = diag(−1,1,1) and `shoulder.py:152` | mirror of {B} in the sagittal plane |
| 9 | {W} | desk-marker world frame | §2.2.2, Chapter 4 §4.1 — **labelled W** | right-handed; z out of the marker card, tilted 32.04° from gravity |
| 10 | {Wu} | Unity-axis world (after the y/z swap, before levelling) | **nowhere** — `carry.py:24,60` | left-handed, y up, not levelled |
| 11 | {Wl} | gravity-levelled Unity-axis world | Chapter 5 calls this **W as well** (collision, item C5-37) | left-handed, y up along gravity |
| 12 | {O} | object frame | Chapter 4, Table 5.1 — **labelled O** | moves with the cube |
| 13 | {M0},{M1},{M2} | the three marker frames | Appendix E — **no letters**, bare `R` and `t` | marker plane, z the outward normal |

**Blocking gap for the labelling rule.** Frames 3–8 have no letters, and frames
6, 7, 8, 10 have no definition at all. Under the author's rule, every printed
`R` and `T` in Chapter 3 must carry two of these labels. Six of the thirteen
frames the chapter's own mathematics uses cannot be named until the author
defines them. This is not an observation about tidiness: eq (3.22) maps into
frame 6, and neither its source nor its destination can currently be written.

---

## 2. Chapter 3 — Kinematic Modeling

Code cross-references used throughout this section:
`v1/kinematics/root_frame.py` (`unity_from_sensor` :12, `build_root_frame` :21,
`euler_unity_zxy` :35, `recompose_zxy` :57),
`v1/kinematics/shoulder.py` (`solve_right_shoulder` :51, `solve_right_arm` :87,
`solve_left_arm` :130, `MIRROR` :127),
`v1/kinematics/occlusion.py` (`ChainFallbackSolver` :57-114),
`eval/inspect/check_v1_overlay.py` (`fk_arm_dirs` :47, FK chain :167-176).

### 2.1 Section 3.1 — Coordinate Systems and Transformations

**C3-01 · eq (3.1) · build_ch3.py:188 · `q = F p, F = diag(1, −1, 1)`**
- Actually maps: a point described in {C} to the same point described in {P}. Verified at `root_frame.py:12-14` (`unity_from_sensor(p) = p * [1,−1,1]`, element-wise, identical to `diag(1,−1,1) @ p`).
- Translation vector: none (the two frames share an origin; the thesis says so).
- Multiplication order: single left multiplication on a column vector.
- Transpose/inverse: none present; F is its own inverse, so none is needed.
- Craig: `^P_C F`. **It is not a rotation matrix** — det F = −1, as the thesis itself states — so `^P_C R` would be wrong.
- Frame-relative vs operator: a **mapping** (change of description). The physical point does not move.
- **VERDICT: UNLABELLED.** Propose `^P p = ^P_C F ^C p` with `^P_C F = diag(1,−1,1)`, and an explicit note that F ∉ SO(3) so the Craig `R` algebra does not apply to it. The thesis's own guard — "The flip applies to points only, never to rotation matrices" — is the right rule and should stay.

**C3-02 · prose · build_ch3.py:197 · "a 3 by 3 matrix R whose columns are the axis directions of the child frame in the parent's coordinates"**
- This is Craig's definition verbatim. Direction correct.
- **VERDICT: UNLABELLED.** Propose `^A_B R = [ ^A X̂_B  ^A Ŷ_B  ^A Ẑ_B ]`.

**C3-03 · prose · build_ch3.py:197 · "The translation part is a 3-vector t, the position of the child's origin"**
- The frame in which t is expressed is never stated. From eq (3.2) and every numerical instance it is the **parent**.
- **VERDICT: MISLEADING.** "The position of the child's origin" is exactly the sentence Craig's `^A P_BORG` exists to disambiguate. Propose `^A P_BORG`, with the words "expressed in {A}" added.

**C3-04 · eq (3.2) · build_ch3.py:199-201 · `T = [R t; 0 1]`, `[p_parent; 1] = T [p_child; 1]`**
- Actually maps: child-frame coordinates to parent-frame coordinates. Direction stated correctly by the equation itself.
- Transpose/inverse: none, none needed.
- Frame-relative vs operator: **mapping**.
- **VERDICT: UNLABELLED.** Propose `^A P = ^A_B T ^B P`, `^A_B T = [ ^A_B R  ^A P_BORG ; 0 0 0  1 ]`.

**C3-05 · eq (3.3) · build_ch3.py:205 · `v_local = R_parent^T v`**
- Actually maps: a free vector expressed in {P} into the parent frame's coordinates. Verified at `shoulder.py:70` (`a = R_root.T @ (p14 − p12)`) and `:78` (`f = R_root.T @ (p16 − p14)`).
- Translation vector: none — this is the rotation block acting alone, and the thesis says so correctly ("applies to directions, and to points only when the two frames share one origin").
- Transpose: present and **required**. `R_parent` describes the parent frame in {P}; its transpose is the mapping into the parent.
- Frame-relative vs operator: **mapping**, not an operator. The vector does not move.
- Craig: `^B v = ^B_P R ^P v` with `^B_P R = (^P_B R)^T`.
- **VERDICT: UNLABELLED.** Note the subscript hazard: `R_parent` is subscripted by the *destination* of the transposed map, which is the *described* frame of the untransposed matrix. That reading is consistent on its own but collides with `R_sh,r` (C3-10).

**C3-06 · eq (3.4) · build_ch3.py:209-212 · `p_child = R^T (p_parent − t)`, `T^{-1} = [R^T, −R^T t; 0 1]`**
- Correct Craig inverse. "The offset is removed first, and the transposed rotation then describes the point along the axes of the child" — direction stated correctly.
- Transpose/inverse: present and **required**.
- Frame-relative vs operator: **mapping**.
- **VERDICT: UNLABELLED.** Propose `^B P = ^A_B R^T ( ^A P − ^A P_BORG )` and `^B_A T = (^A_B T)^{-1}`.

**C3-07 · eq (3.5) · build_ch3.py:221 · `T_root = [R_root, t_root; 0 1]`**
- Prose establishes it: "the pose of the root (torso) frame with respect to person space". Verified: `R_root` is `build_root_frame`'s `np.stack([r,u,f], axis=-1)` (`root_frame.py:32`), columns = {B}'s axes in {P}; the origin is `p24` (eq 3.12).
- Frame-relative vs operator: **frame description**.
- **VERDICT: UNLABELLED.** Propose `^P_B T`, `^P_B R`, `^P P_BORG`.

**C3-08 · eq (3.5) · build_ch3.py:222 · `T_sh,r = [I, t_sh,r; 0 1]`** (and `T_sh,l`)
- Prose establishes it: "the pose of the right shoulder frame with respect to the root". The identity rotation block is confirmed by the code, which never materialises a shoulder rotation and uses `R_root.T` directly for shoulder-frame quantities (`shoulder.py:70,78`).
- **VERDICT: UNLABELLED.** Propose `^B_{S_r} T`, with `^B_{S_r} R = I₃` and `^B P_{S_r}ORG = t_sh,r`.

**C3-09 · eq (3.5) · build_ch3.py:223 · `T_el,r = [R_sh,r, t_el,r; 0 1]`** (and `T_el,l`)
- Prose establishes it: "the pose of the right elbow frame with respect to the shoulder frame".
- **VERDICT: UNLABELLED.** Propose `^{S_r}_{E_r} T`, `^{S_r} P_{E_r}ORG = t_el,r`.

**C3-10 · eq (3.5) and the prose at build_ch3.py:225-236 · the symbol `R_sh,r`**
- Actually is: the orientation of the **elbow** frame relative to the **shoulder** frame. Verified two ways: the prose ("with the solved shoulder rotation `R_sh,r` for its rotation block" of the elbow transformation), and `shoulder.py:120` (`R_arm = R_root @ (_ry(y) @ _rz(z) @ _rx(t))`, so `Ry·Rz·Rx` sits between the root and the elbow).
- Craig: `^{S_r}_{E_r} R`.
- **VERDICT: CONTRADICTS.** In `R_root` the subscript names the frame being *described*. In `R_sh,r` it names the frame the description is *relative to*. A reader who carries the `R_root` rule across gets "the shoulder frame relative to the root", which eq (3.13) declares to be the identity. The two symbols cannot be read under one rule as printed.
- *Separate from the notation recommendation:* the mathematics is right. No transformation direction in the code needs changing.

**C3-11 · eq (3.6) · build_ch3.py:237 · `T_arm,r = T_root T_sh,r T_el,r`**
- The composition is correct and obeys frame cancellation: `^P_B T ^B_{S_r} T ^{S_r}_{E_r} T = ^P_{E_r} T`. Verified numerically in §3.5 (applying the product to the origin returns the measured elbow position; reproduced here from the printed matrices to the printed rounding).
- **VERDICT: MISLEADING.** The product's subscript "arm,r" is a **third** name for the elbow frame, already carried by "el,r" in the same equation. Nothing in the symbols says that `T_el,r` and `T_arm,r` describe the same frame against different references. Propose writing the equation as `^P_{E_r} T = ^P_B T ^B_{S_r} T ^{S_r}_{E_r} T`, at which point the frame cancellation is visible on the page.

**C3-12 · prose · build_ch3.py:239 · "the inverse transformations of equation (3.4) carry it into the frame where its joint is solved … shoulder landmark into the root frame, elbow landmark into the shoulder frame, wrist into the elbow frame"**
- Direction correct and matches the code.
- **VERDICT: UNLABELLED** (no symbols at all; the three inward maps are `^B_P T`, `^{S_r}_P T`, `^{E_r}_P T`).

**C3-13 · Chapter 3 as a whole — the subscript convention**
- `T_root`, `T_sh,r`, `T_el,r` : subscript = described frame. `R_root` : subscript = described frame. `R_parent` : subscript = described frame. `R_sh,r` : subscript = reference frame. `R_arm,r` : subscript = neither (the elbow frame under a third name).
- **VERDICT: CONTRADICTS.** There is no single reading of the subscript slot that is true of all five. This is the headline Chapter 3 finding, and it is the reason the author's rule is not cosmetic here: the current notation is not merely incomplete, it is ambiguous in a way that changes the meaning of eq (3.5).

### 2.2 Section 3.2 — Torso Reference Frame

All quantities below are expressed in {P} (the thesis says so once, in prose:
"Every landmark position in this chapter is a person-space value unless stated
otherwise"). Verified against `root_frame.py:21-32`.

| ID | Location | Printed | Actually is | Craig | Verdict |
|---|---|---|---|---|---|
| C3-14 | eq (3.7), build_ch3.py:260 | `x̂ = (p24 − p23)/‖p24 − p23‖` | {B}'s x axis expressed in {P}; `p23`, `p24` are {P} positions | `^P X̂_B`, `^P P_23`, `^P P_24` | UNLABELLED |
| C3-15 | eq (3.8), :265 | `s = p12 − p24` | free vector in {P} | `^P s` | UNLABELLED |
| C3-16 | eq (3.9), :270 | `ẑ = (x̂ × s)/‖x̂ × s‖` | {B}'s z axis in {P}; sign claim ("out of the chest toward the camera") confirmed by the worked example's `ẑ = (0.01, 0.53, −0.85)`, negative z = toward the camera | `^P Ẑ_B` | UNLABELLED |
| C3-17 | eq (3.10), :279 | `ŷ = ẑ × x̂` | {B}'s y axis in {P} | `^P Ŷ_B` | UNLABELLED |

**C3-18 · eq (3.11) · build_ch3.py:284 · `R_root = [x̂ ŷ ẑ]`**
- Actually is: the orientation of {B} relative to {P}; columns are {B}'s axes in {P}. Verified at `root_frame.py:32` (`np.stack([r, u, f], axis=-1)`, "Columns of R are the person's [right | up | forward] in Unity world") and independently at `check_v1_overlay.py:174-175`, where `R_root @ up` converts a root-basis direction into person space for forward kinematics.
- det = +1 (proved from the construction: u = f × r, so r·(u × f) = r·r = 1).
- Frame-relative vs operator: **frame description**.
- **VERDICT: UNLABELLED.** Propose `^P_B R = [ ^P X̂_B  ^P Ŷ_B  ^P Ẑ_B ]`.

**C3-19 · eq (3.12) · build_ch3.py:288 · `T_root = [R_root, p24; 0 1]`**
- `^P P_BORG = ^P P_24`. Direction stated correctly in the prose.
- **VERDICT: UNLABELLED.** Propose `^P_B T`.

**C3-20 · prose · build_ch3.py:290 · the T-pose reference, `R_root` columns (−1,0,0),(0,1,0),(0,0,−1)**
- Corroborated by `occlusion.py:40,64`: `ROOT_REST_DEG = (0, 180, 0)` and `recompose_zxy((0,180,0)) = Ry(180°) = diag(−1, 1, −1)`, whose columns are exactly those three.
- Decode verified against `euler_unity_zxy`: x = −asin(0) = 0, y = atan2(0, −1) = 180°, z = atan2(0, 1) = 0 → (0, 180, 0). ✓
- **VERDICT: UNLABELLED** (`^P_B R`).

**C3-21 · Figure 3.4 caption · build_ch3.py:257-258**
- "The finished frame at the L24 origin, x toward the subject's right, y up the trunk and z out of the chest." The axes are described but the frame is not named, so a reader cannot connect the picture to `R_root`.
- **VERDICT: UNLABELLED.** Name the frame {B} in the caption.

**C3-22 · Figure 3.5 caption · build_ch3.py:305-306** — **UNRESOLVED**, see §0.

### 2.3 Section 3.3 — The Arm Model

**C3-23 · eq (3.13) · build_ch3.py:327 · `T_sh,r = [I, R_root^T(p12 − p24); 0 1]`**
- Actually maps: {S_r} coordinates to {B} coordinates. The translation `R_root^T(p12 − p24)` is the shoulder landmark expressed **in {B}** — the thesis says exactly this ("expressed with respect to the torso, by the mapping of equation (3.4) applied to p12").
- Transpose: present and **required**.
- **VERDICT: UNLABELLED.** Propose `^B_{S_r} T` with `^B P_{S_r}ORG = ^P_B R^T ( ^P P_12 − ^P P_24 )`.

**C3-24 · eq (3.14) · build_ch3.py:337 · `T_el,r = [R_sh,r, R_root^T(p14 − p12); 0 1]`**
- Actually maps: {E_r} coordinates to {S_r} coordinates. The translation is the elbow landmark in {S_r}. The use of `R_root^T` (rather than a shoulder-specific matrix) is valid **because** `^B_{S_r} R = I`, and the thesis states the reason correctly ("That frame shares the orientation of the root, so the same `R_root^T` maps it").
- Transpose: present and **required**.
- Verified: the worked example's printed `T_el,r` last column (0.05, −0.31, −0.05) equals the printed `v_local`, which is exactly `R_root^T (p14 − p12)`.
- **VERDICT: UNLABELLED.** Propose `^{S_r}_{E_r} T` with `^{S_r} P_{E_r}ORG = ^P_B R^T ( ^P P_14 − ^P P_12 )`.

**C3-25 · inline · build_ch3.py:344-348 · `v = p14 − p12`, `v_local = R_root^T v`**
- Verified at `shoulder.py:70`.
- **VERDICT: UNLABELLED.** Propose `^P v` and `^B v = ^P_B R^T ^P v`.

### 2.4 Section 3.4 — Joint Angle Computation

**C3-26 · eq (3.15) · build_ch3.py:353 · `R = Ry(y) Rx(x) Rz(z)`, with the prose "applied about the axes of the parent frame in the order z, then x, then y"**
- Mathematics verified: symbolically identical to `recompose_zxy` (`root_frame.py:57-64`, `Ry @ Rx @ Rz`), and eq (3.16) multiplies out to exactly this product (checked symbolically with sympy; difference is the zero matrix).
- **VERDICT: MISLEADING on Craig's terminology.** The prose describes rotations about the **fixed** axes of the parent frame, pre-multiplied — Craig §2.7 calls that a *fixed-angle* set (here Z-X-Y fixed angles), and proves it equals the Y-X-Z **Euler** set about moving axes. The thesis calls them "Euler angles" throughout while giving the fixed-axis rule. The author's instruction asks for Craig's distinctions to be applied; this is one of them. The numbers are right; only the name and the accompanying sentence are at odds. It is also **UNLABELLED** (bare `R`): propose stating it as the parameterisation of a general `^A_B R`, with `Rx, Ry, Rz` explicitly *operators* about {A}'s axes.
- Secondary note, not a verdict: `Rx, Ry, Rz` as written are the standard right-handed-sense matrices, but {P} and {B} are left-handed, so a positive angle turns in the opposite geometric sense from Craig's figures. The algebra (RᵀR = I, composition, frame cancellation) is unaffected because every matrix in the chain has det +1. Worth one sentence in §3.1 so a reader coming from Craig is not misled about the sense of a positive angle.

**C3-27 · eq (3.16) · build_ch3.py:356-363 · the multiplied-out 3×3**
- Verified symbolically against `Ry(y) Rx(x) Rz(z)`. Exact.
- **VERDICT: UNLABELLED** (bare `R`).

**C3-28 · eq (3.17) and the unnumbered gimbal-lock display · build_ch3.py:374-386**
- `x = asin(−m23), y = atan2(m13, m33), z = atan2(m21, m22)`. Verified against `euler_unity_zxy` (`root_frame.py:41-44`) with 1-indexed ↔ 0-indexed mapping: `m23 → R[1,2]`, `m13 → R[0,2]`, `m33 → R[2,2]`, `m21 → R[1,0]`, `m22 → R[1,1]`. Exact.
- Lock branch verified too: code `np.where(m12 < 0, atan2(R[0,1], R[0,0]), atan2(−R[0,1], R[0,0]))`; since `x = −asin(m12)`, `m12 < 0` is `x = +90°`, matching the thesis's `x = +90°: y = atan2(m12, m11)` (1-indexed `m12` = `R[0,1]`). Exact, including the sign.
- **VERDICT: UNLABELLED.** `m` is whichever `^A_B R` is being decoded; the pair {A},{B} is never stated, and §3.4.1 applies it to `R_root` while Chapter 6 applies it to bone rotations.

**C3-29 · §3.4.1 · build_ch3.py:388-391 · "Its pose is the pair (R_root, p24)"**
- **VERDICT: UNLABELLED.** Propose `( ^P_B R, ^P P_BORG )`, i.e. `^P_B T`.

**C3-30 · eq (3.18) · build_ch3.py:397 · `R_sh,r = Ry(t_y) Rz(t_z) Rx(t_t)`**
- Verified at `shoulder.py:45-48` (`recompose_shoulder`) and `:120` (`R_arm = R_root @ (_ry(y) @ _rz(z) @ _rx(t))`), and independently at `check_v1_overlay.py:57-60`.
- Actually is: `^{S_r}_{E_r} R`.
- **VERDICT: UNLABELLED**, and see C3-10 for the subscript contradiction.

**C3-31 · eq (3.19) · build_ch3.py:403-405 · `â = R_sh,r x̂ = Ry(t_y) Rz(t_z) x̂ = (c_y c_z, s_z, −s_y c_z)`**
- Verified symbolically: `Ry(ty) Rz(tz) Rx(tt) · (1,0,0)ᵀ = (cos ty cos tz, sin tz, −sin ty cos tz)ᵀ`. Exact.
- **VERDICT: MISLEADING on two counts.**
  1. **Glyph collision.** `x̂` here is (1, 0, 0), the rest arm axis expressed in {S_r}. In §3.2 and §3.5 the same glyph `x̂` is {B}'s x axis expressed in {P}, printed numerically as (−1.00, −0.05, −0.04). One symbol, two frames, two values, eleven equations apart.
  2. **Operator vs description.** Here `R_sh,r` is applied to a vector to produce a new vector — Craig's *operator* use. In eq (3.14) the identical symbol is the rotation block of a transform — Craig's *description* use. Craig Ch. 2 separates these explicitly and the thesis does not.
- Craig: `^{S_r} â = ^{S_r}_{E_r} R · ^{E_r} X̂_{E_r}`, i.e. the first column of `^{S_r}_{E_r} R`. Writing it that way makes the operator/description question disappear, because it becomes a statement about a column of a description.

| ID | Location | Printed | Actually is | Verified against | Verdict |
|---|---|---|---|---|---|
| C3-32 | eqs (3.20)-(3.21), :413,416 | `t_z = asin(a_y)`, `t_y = atan2(−a_z, a_x)` | scalars read from `^{S_r} â`'s components | `shoulder.py:71-76` | UNLABELLED (the vector whose components they are is unlabelled) |
| C3-34 | eq (3.23), :430 | `t_t = atan2(−f′_y, f′_z)` | scalar read from `^{E0_r} f`'s components | `shoulder.py:82` | UNLABELLED |
| C3-38 | eq (3.24), :444-445 | `e_z = asin(g_y)`, `e_y = atan2(−g_z, g_x)` | scalars read from `^{E_r} ĝ`'s components | `shoulder.py:122-123` | UNLABELLED |

**C3-33 · eq (3.22) · build_ch3.py:424 · `f′ = Rz(−t_z) Ry(−t_y) f`**
- Verified at `shoulder.py:79`: `fp = _rz(-th_z) @ (_ry(-th_y) @ f)`. Exact, including the order.
- Actually is: `Rz(−t_z) Ry(−t_y) = ( Ry(t_y) Rz(t_z) )^{-1} = ^{E0_r}_{S_r} R`, the mapping of the forearm vector from {S_r} coordinates into the **untwisted upper-arm frame** {E0_r}. `f` is `^{S_r} f`; `f′` is `^{E0_r} f`.
- Transpose/inverse: the negated angles *are* the inverse; it is required for the stated purpose.
- **VERDICT: MISLEADING, plus a blocking gap.** The prose ("the procedure undoes the swing first, which makes that plane the local y-z plane") reads as an operator rotating a vector; the mathematics is a change of description into a frame the thesis never names. Craig requires a choice between the two readings, and the frame-description reading needs frame 6 of the inventory to exist. Propose `^{E0_r} f = ^{E0_r}_{S_r} R ^{S_r} f` with `^{E0_r}_{S_r} R = ( ^{S_r}_{E0_r} R )^T` and `^{S_r}_{E0_r} R = Ry(t_y) Rz(t_z)`.

**C3-35 · §3.4.2 · build_ch3.py:433-435 · `M = diag(−1, 1, 1)`** — **UNRESOLVED**, see §0.
- Evidence gathered: `shoulder.py:127` `MIRROR = np.array([-1.0, 1.0, 1.0])`, applied at `:149-150` to `R_root.T @ (p13 − p11)` and `R_root.T @ (p15 − p13)` — so M acts on vectors already expressed in {B}. `:152` then calls `solve_right_arm(zero, u, u+f, np.eye(3))`, i.e. the mirrored vectors are handed to the solver as if they lived in a frame whose orientation relative to itself is the identity. det M = −1.

**C3-36 · §3.4.3 inline · build_ch3.py:439-440 · `R_arm,r = R_root Ry(t_y) Rz(t_z) Rx(t_t)`**
- Verified at `shoulder.py:120`. Exact.
- Actually is: `^P_{E_r} R = ^P_B R · ^B_{S_r} R · ^{S_r}_{E_r} R` (the middle factor being I). Frame cancellation holds.
- Consistency check: `R_arm,r` is the rotation block of `T_arm,r` of eq (3.6). Confirmed: `T_root T_sh,r T_el,r` has rotation block `R_root · I · R_sh,r`. ✓
- **VERDICT: UNLABELLED.** Propose `^P_{E_r} R`, and drop the "arm" name in favour of the frame label (see C3-11).

**C3-37 · §3.4.3 inline · build_ch3.py:441-442 · `ĝ = R_arm,r^T (p16 − p14)`**
- Verified at `shoulder.py:121`: `g = normalize(R_arm.T @ (p16 − p14))`. Exact.
- Transpose: present and **required** — the target is the forearm direction expressed in {E_r}.
- Frame-relative vs operator: **mapping**.
- **VERDICT: UNLABELLED.** Propose `^{E_r} ĝ = ^P_{E_r} R^T ( ^P P_16 − ^P P_14 ) / ‖·‖`.

**C3-39 · the missing elbow rotation** — **UNRESOLVED**, see §0.

### 2.5 Section 3.5 — Worked Example

Every displayed quantity in §3.5 is a numerical instance of an item above. They
are listed separately because the author's rule covers displayed mathematics as
well as numbered equations.

| ID | build_ch3.py | Printed | Craig label once direction is fixed | Verdict |
|---|---|---|---|---|
| C3-40 | :468-478 | Table 3.1, columns "Camera frame C (m)" and "Person space P (m)" | `^C P_i`, `^P P_i` | **AGREES** — the one place in Chapter 3 where a quantity carries its frame |
| C3-41 | :481-485 | `p23, p24, p12` numeric | `^P P_23`, `^P P_24`, `^P P_12` | UNLABELLED |
| C3-42 | :487-490 | `x̂, ẑ, ŷ` numeric | `^P X̂_B`, `^P Ẑ_B`, `^P Ŷ_B` | UNLABELLED |
| C3-43 | :495-498 | `R_root` 3×3 numeric | `^P_B R` | UNLABELLED |
| C3-44 | :501-506 | `T_root` 4×4 numeric | `^P_B T` | UNLABELLED |
| C3-45 | :507-512 | `T_sh,r` 4×4 numeric | `^B_{S_r} T` (prose states the direction: "the shoulder landmark in the torso's own coordinates") | UNLABELLED |
| C3-46 | :520-525 | `v`, `v_local = R_root^T v`, `â` | `^P v`, `^B v`, `^{S_r} â` | UNLABELLED |
| C3-47 | :526 | `f = R_root^T (p16 − p14)` | `^{S_r} f` | UNLABELLED |
| C3-48 | :532 | `f′ = Rz(76.6°) Ry(−43.0°) f` | `^{E0_r} f`; signs verified consistent with eq (3.22) given `t_z = −76.6°`, `t_y = 43.0°` | UNLABELLED |
| C3-49 | :536 | `ĝ = (0.94, 0.00, 0.34)` | `^{E_r} ĝ` | UNLABELLED |
| C3-50 | :544-548 | `T_el,r` 4×4 numeric | `^{S_r}_{E_r} T`; last column verified equal to `v_local` | UNLABELLED |
| C3-51 | :549-556 | closing check prose: compose eq (3.6) and apply to the origin → (−0.20, 0.04, 1.19); carry the wrist through the inverse chain → (0.19, 0.00, 0.07) | `^P P_{E_r}ORG = ^P_{E_r} T · (0,0,0,1)ᵀ` and `^{E_r} P_16 = ( ^P_{E_r} T )^{-1} ^P P_16` | UNLABELLED — direction stated correctly in words, no symbols carry it. I reproduced the forward check from the printed matrices: (−0.20, 0.05, 1.20) against the stated (−0.20, 0.04, 1.19), the difference being the two-decimal rounding the section itself warns about |

**C3-52 · §3.1 prose · build_ch3.py:197 · "the transpose of R is its inverse and no matrix is ever inverted numerically"**
- True inside Chapter 3's own chain: the code uses `R_root.T` (`shoulder.py:70,78`) and `R_arm.T` (`:121`) and never calls an inverse.
- False for the path Chapter 5 depends on: `eval/offset/carry.py:59` `np.linalg.inv(calib["T_cam_desk"])` and `eval/failure/recovery_core.py:69` `np.linalg.inv(world.M)`.
- **VERDICT: MISLEADING.** The sentence is stated without qualification and the thesis's own recovery layer breaks it. Either qualify it to the kinematic chain or drop it.

---

## 3. Chapter 5 — Pose Recovery During Tracking Failure

Code cross-references: `eval/offset/carry.py` (`LeveledWorld` :54-87,
`fit_grip` :111-130), `eval/failure/recovery_core.py`
(`_leveled_to_solver_space` :65-72, `build_inputs` :75-165),
`eval/failure/grip_state.py`, `v1/kinematics/occlusion_ext.py`
(`_learn_dir` :301, `_ik_elbow` :334, `_try_recover` :391).

### 3.1 The frame chain, established from the code

```
{C}  camera
  │ ×[1,−1,1]                       root_frame.py:12
{P}  person space
  │ M = P_swap · R_dc · D , + cam_pos        carry.py:60-61
{Wu} Unity-axis world (unlevelled)
  │ G = from_to_rotation(g_unity, +y)        carry.py:64
{Wl} gravity-levelled world  ← Chapter 5 calls this "W"
```
with `T_dc = inv(T_cam_desk)` and `T_cam_desk = ^C_W T` (the desk marker's pose
in the camera frame; `v1/aruco/calibrate_scene.py:8-12`, `v1/ARUCO_MODEL.md` §4).

**Numerical confirmation, frame 560 of the rail recording** (this is how I fixed
the frames, not by trusting the names):

- Chapter 4's world-frame object translation, from
  `eval/output/recording_20260831_065553_scaled_object_world_filtered.csv`:
  `(tx, ty, tz) = (−0.223366, 0.417122, −0.176261)`.
- The same row's Unity columns: `(−0.223366, −0.176261, 0.417122)` — the y/z swap.
- Applying `G` from `eval/output/scene_calibration_r6bc.json`:
  `G · (−0.2234, −0.1763, 0.4171) = (−0.2246, 0.0764, 0.4458)`, which is the
  `o = (−0.22, 0.08, 0.45)` printed at build_ch5.py:509.
- Applying `G · P · R_w · P` to the same row's rotation reproduces the printed
  `R_obj` at build_ch5.py:510-513 entry by entry to two decimals.
- The 4×4 printed at build_ch5.py:524-528 equals `[ M⁻¹G⁻¹ | −M⁻¹ cam_pos ]`
  computed from the same calibration (0.9989/−0.0425/0.0178/0.0235 …), and does
  **not** equal the unlevelled variant (whose (2,2) entry is 0.8752, not 1.00).
  Applying it to `(−0.21, 0.13, 0.48)` returns `(−0.186, −0.092, 1.041)`, the
  printed `(−0.19, −0.09, 1.04)`. Direction: **{Wl} → {P}**, i.e. `^P_{Wl} T`.

### 3.2 Table 5.1 (build_ch5.py:253-272, caption at :273, patch at :564-570)

| ID | Row | Printed frame | Actual frame | Verdict |
|---|---|---|---|---|
| C5-01 | `p_sh, p_el, p_wr` | "person space P" | `p_sh`, `p_el` yes; `p_wr` is {P} in eqs (5.6), (5.8), (5.12) but **{Wl}** in eqs (5.1), (5.2) | **CONTRADICTS** |
| C5-02 | `o` | "levelled world frame W … translation column of `T_WO`" | `^{Wl} P_OORG`; **not** the translation column of `^W_O T` (see the frame-560 numbers above) | **CONTRADICTS** |
| C5-03 | `R_obj` | "levelled world frame W … rotation block of `T_WO`" | `^{Wl}_O R = G · P · ( ^W_O R ) · P`; **not** the rotation block of `^W_O T` | **CONTRADICTS** |
| C5-04 | `w` | "levelled world frame W, **then P**" | two frames, one glyph, both used in equations | **CONTRADICTS** |
| C5-05 | `T_WO` (two cells) | subscript form | `^W_O T`; direction verified from Chapter 4 eq (4.1) `T_WO = T_CW^{-1} T_CO` (frame cancellation `^W_C T ^C_O T = ^W_O T` ✓) and `v1/ARUCO_MODEL.md` §4 | **UNLABELLED** (the form the rule forbids) |
| C5-06 | caption, "after levelling by the calibrated gravity direction" | — | the levelling is a transform between two frames (`G`, `carry.py:64`) with no symbol anywhere in the thesis; the y/z swap is not mentioned at all | **UNLABELLED** — propose naming `^{Wl}_{Wu} R` (or folding both into a printed definition of {Wl}) |
| C5-07 | `h`, `h_k` | "object frame O" | correct: `^O P_WR`, `^O P_{WR,k}` | **UNLABELLED** (bare `h`) |
| C5-08 | `û, f̂` / `b, r, b̂` / `p_c, r_c` / `n₁, n₂` / `u⊥` | "person space P" | correct — verified at `occlusion_ext.py:301-310` (`_learn_dir` differences person-space landmarks) and `:334-390` (`_ik_elbow` takes person-space `S`, `W`, `mem_dir`) | **AGREES** on the frame column |

### 3.3 Section 5.3 — Grip Episodes and the Hand-Object Offset

**C5-09 · eq (5.1) · build_ch5.py:281 · `p_wr = o + R_obj h`**
- Actually maps: `^{Wl} P_WR = ^{Wl}_O R · ^O P_WR + ^{Wl} P_OORG`, i.e. `^{Wl} P_WR = ^{Wl}_O T ^O P_WR`.
- Verified in code twice: `carry.py:126` `pred = obj + np.einsum("nij,j->ni", R_obj, mu)` (= `R_obj @ mu`, no transpose) and `recovery_core.py:147` `w_lev = obj_lev + np.einsum("nij,nj->ni", R_lev, mu)`. The `wr` these are compared against is `LeveledWorld.wrist_world` output (`carry.py:71-73`), which is a **{Wl}** quantity.
- Translation vector: `o` is expressed in {Wl}.
- Transpose/inverse: none present, none needed for this direction.
- Frame-relative vs operator: `R_obj` is a **frame description** used as a **mapping** of `^O h` into {Wl}.
- **VERDICT: CONTRADICTS** on `p_wr`'s declared frame (Table 5.1 says {P}). The mapping direction itself **AGREES**.
- Craig: `^{Wl} P_WR = ^{Wl}_O T ^O P_WR`.

**C5-10 · eq (5.2) · build_ch5.py:288 · `h_k = R_obj,k^T (p_wr,k − o_k)`**
- Verified: `carry.py:117` `d_loc = np.einsum("nij,ni->nj", R_obj, wr[side] − obj)`. The index pattern `nij,ni->nj` contracts over the matrix's **row** index, which is `R_objᵀ v`. Same at `recovery_core.py:111`.
- Transpose: present and **required** for the stated direction ({Wl} → {O}).
- Frame-relative vs operator: **mapping**.
- The prose "pulled into the object's axes by the transpose, the operation of equation (3.3)" is a correct cross-reference: eq (3.3) is the same `Rᵀ` mapping.
- **VERDICT: UNLABELLED** on the symbols; **CONTRADICTS** carried over from C5-01 for `p_wr,k`.
- Craig: `^O P_{WR,k} = ^O_{Wl} T ^{Wl} P_{WR,k}`, whose rotation part is `( ^{Wl}_O R )^T`.

**C5-11 · unnumbered least-squares display · build_ch5.py:306-311**
- `Σ‖p_wr,k − o_k − R_obj,k h‖² = Σ‖R_obj,k(h_k − h)‖² = Σ‖h_k − h‖²`.
- Mathematically correct (orthonormality of `R_obj`). But the first two sums are over {Wl}-expressed vectors and the third over {O}-expressed vectors, and `R_obj,k(h_k − h)` is a {Wl} vector built from an {O} difference. The frame changes twice inside one display with no notation.
- **VERDICT: MISLEADING.** Propose writing it as `Σ‖ ^{Wl} P_{WR,k} − ^{Wl}_O T ^O P_WR ‖²` and letting the labels show why the rotation drops out.

| ID | Location | Printed | Frames | Verified against | Verdict |
|---|---|---|---|---|---|
| C5-12 | eq (5.3), :314-315 | `h = (1/N) Σ h_k` | all {O} | `carry.py:124` `mu = d_loc[hold].mean(axis=0)` | UNLABELLED |
| C5-13 | eq (5.4), :320-321 | `h_new = (1−c) h_old + c h_k` | all {O} | `grip_state.py` `MU_ALPHA = 0.02` | UNLABELLED |
| C5-14 | eq (5.5), :355-356 | `û_new = ((1−α)û_old + α û_meas)/‖·‖` | all {P} | `occlusion_ext.py:301-310` `_learn_dir`, `dir_alpha = 0.3`, renormalised | UNLABELLED |
| C5-15 | eq (5.6), :367 | `p_wr = p_el + L2 f̂` | all {P} | `occlusion_ext.py:391-405` `_try_recover`: `p[child] = anchor_pt + sign * L[seg] * u[dir_key]` | **CONTRADICTS** — same `p_wr` glyph as eq (5.1)'s {Wl} quantity |

### 3.4 Section 5.4 — Wrist Recovery from the Object Pose

**C5-16 · eq (5.7) · build_ch5.py:380 · `w = o + R_obj h`**
- Identical mapping to eq (5.1); verified at `recovery_core.py:147`.
- **VERDICT: CONTRADICTS.** The direction **AGREES**, but `w` is formed in {Wl} and then, four paragraphs later, used in {P} without a change of symbol. §5.5 (`b = w − p_sh`) requires the {P} value; §5.6 prints both under the same glyph.
- Craig: `^{Wl} P_ŴR = ^{Wl}_O T ^O P_WR` for the estimate in the world, and a **different symbol** for `^P P_ŴR = ^P_{Wl} T ^{Wl} P_ŴR`.

**C5-17 · §5.4 last paragraph (build_ch5.py:390) and §5.1 (build_ch5.py:220) · "the fixed rigid body transformation of the scene calibration (Section 2.2.2) therefore carries the estimate into person space"**
- Actually maps: **{Wl} → {P}**. Verified at `recovery_core.py:65-72`
  (`_leveled_to_solver_space`: `Ginv = world.G.T`, `Minv = np.linalg.inv(world.M)`,
  `w_cam = (Minv @ (Ginv @ w_lev.T − cam_pos[:,None])).T * [1,−1,1]`, then
  `unity_from_sensor` applies `[1,−1,1]` a second time, so the two flips cancel and
  the net result is `M⁻¹(G⁻¹ p_{Wl} − cam_pos)`, a person-space point), and
  numerically against the printed 4×4 (§3.1 above).
- Translation vector: `−M⁻¹ cam_pos`, expressed in {P}; it is the world origin in person space, which is what the §5.6 prose says.
- Transpose/inverse: `G.T` is used as `G⁻¹` (valid, G ∈ SO(3)); `M` is inverted **numerically** — see C3-52.
- "It changes no length and no angle" — correct; I computed det of the rotation block = 1.000000.
- Frame-relative vs operator: **mapping**.
- **VERDICT: UNLABELLED.** The transform has **no symbol at all** in the thesis. Propose `^P_{Wl} T`, defined once in §2.2.2 and cited by name in §5.1, §5.4 and §5.6.

### 3.5 Section 5.5 — Elbow Recovery by Two-Link Inverse Kinematics

All quantities are {P}. Verified against `occlusion_ext.py:334-390` (`_ik_elbow`).

| ID | Location | Printed | Code | Verdict |
|---|---|---|---|---|
| C5-18 | eq (5.8), :403-404 | `‖p_el − p_sh‖ = L1`, `‖p_el − p_wr‖ = L2` | the two spheres `_ik_elbow` intersects | UNLABELLED (the points need `^P` prefixes) |
| C5-19 | eq (5.9), :420-422 | `cos j = (L1² + r² − L2²)/(2 L1 r)` | `ca = np.clip((L1*L1 + r*r − L2*L2)/(2.0*L1*r), −1, 1)` | **AGREES** — scalars, no frame needed |
| C5-20 | eq (5.10), :432-434 | `p_c = p_sh + L1 cos j b̂`, `r_c = L1 sin j` | `c = S + L1*ca*dh`; `rho = L1*sqrt(1 − ca²)` | UNLABELLED |
| C5-21 | eq (5.11), :443-445 | `p_el = p_c + r_c(cos s n₁ + sin s n₂)` | the swivel circle; `u1`,`u2` in the limits branch | UNLABELLED |
| C5-22 | eq (5.12), :456-458 | `u⊥ = û − (û·b̂) b̂`, `p_el = p_c + r_c u⊥/‖u⊥‖` | `perp = n − (n @ dh)*dh`; `prior = c + rho*perp/m` | UNLABELLED |

Note on the fallbacks: the thesis's "A downward direction then takes its place …
with the depth axis of person space as the third candidate" matches
`occlusion_ext.py:365-367` exactly (`[0,−1,0]` then `[0,0,1]`), and both are
{P} directions, so the prose's "of person space" is correct.

### 3.6 Captions

| ID | Location | Verdict |
|---|---|---|
| C5-23 | Figure 5.3 caption, build_ch5.py:297 — "the displacement from the object origin o to the measured wrist is read in the object axes, equation (5.2)" | **UNLABELLED** — the direction is described correctly in words, but `o` and "the object axes"/"the world axes" carry no labels |
| C5-24 | Figure 5.5 caption, build_ch5.py:477 | **AGREES** — no transforms; all quantities are named {P} objects described in words |

### 3.7 Section 5.6 — Worked Example

| ID | build_ch5.py | Printed | Craig label | Verdict |
|---|---|---|---|---|
| C5-25 | :507 | `p_sh = (−0.16, 0.34, 1.32)` | `^P P_SH` (consistent with Ch3 Table 3.1's person-space L12) | UNLABELLED |
| C5-26 | :509 | `o = (−0.22, 0.08, 0.45)` | `^{Wl} P_OORG` | UNLABELLED |
| C5-27 | :510-513 | `R_obj` 3×3 | `^{Wl}_O R` | UNLABELLED |
| C5-28 | :516 | `h = (0.01, −0.04, 0.05)` | `^O P_WR` | UNLABELLED |
| C5-29 | :518-520 | `R_obj h = (0.01, 0.06, 0.04)` | a {Wl}-expressed displacement; the prose "turns it into the levelled world axes" states the direction correctly | UNLABELLED |
| C5-30 | :520 | `w = o + R_obj h = (−0.21, 0.13, 0.48)` | `^{Wl} P_ŴR` | UNLABELLED |
| C5-31 | :524-528 | the 4×4 scene-calibration matrix | `^P_{Wl} T` — established both from `recovery_core.py:65-72` and numerically (§3.1) | **UNLABELLED, most severe form: printed with no symbol whatsoever** |
| C5-32 | :531 | `w = (−0.19, −0.09, 1.04)` | `^P P_ŴR` | **CONTRADICTS** — same glyph as C5-30, different frame, y even changes sign |
| C5-33 | :535-553 | `b, r, b̂`; `cos j`; `p_c, r_c`; `û, u⊥`; `p_el` | all `^P` | UNLABELLED |
| C5-34 | :529-530 | "Its rotation block is close to the identity … its last column is the desk origin in person space" | direction and identification both correct — (0.02, −0.19, 0.55) is the Appendix E / Chapter 4 desk-marker translation with the person-space y flip | UNLABELLED (describes a transform that has no symbol) |
| C5-36 | :207 (§5.1) | "while a hand holds the cube the wrist keeps a fixed position in the object's frame" | **AGREES** — this statement is `h = ^O P_WR`, and every equation that uses `h` (5.1, 5.2, 5.3, 5.4, 5.7) applies the transform in the direction it implies. Verified in `carry.py:117,126` and `recovery_core.py:111,147`. The author's specific worry about `h` is unfounded: the direction is right everywhere. | **AGREES** |

---

## 4. Appendices in scope

**Appendix H — Kinematic Solver Verification.** Contains **no** rotation matrix,
homogeneous transform or position-vector symbol. Nothing to label.
**VERDICT: AGREES (nothing in scope).**
One caution for the author: H's evidence is that the decoder inverts the encoder
on injected angle trajectories ("the decoded angles agree with the injected ones
… to the precision of the arithmetic"). That is a self-consistency result about
the forward/inverse pair. It says nothing about whether the printed frame labels
name the right frames — exactly the case the audit brief warns about.

**Appendix G — Hip Depth Preparation.**
- **A-G1 · eq (G.1) · `p* = z* · p/p_z`** — a ray rescaling of a {P} point using its
  camera-depth coordinate. The appendix states the justification explicitly
  ("The rules operate in person space P; flipping the camera y axis leaves the
  camera-depth coordinate z unchanged"), which is exactly the identity `^C z = ^P z`
  implied by eq (3.1)'s `F = diag(1,−1,1)`. **VERDICT: AGREES** on that reasoning;
  the symbols `p`, `p*` should carry `^P`.
- **A-G2 · §G.1-G.3 prose** — remembered pair directions, calibrated widths, the
  rebuilt midpoint, the blended direction. All {P} vectors; no `R` or `T` is
  printed anywhere in the appendix. **VERDICT: UNLABELLED** (light: position and
  direction vectors only).

**Appendix D — Depth Sensing and Deprojection (listed because §3.1 rests on it).**
- **A-D · §D.3** defines {C}: "right-handed, with x to image right, y downward and
  z forward along the optical axis". This is the fact eq (3.1) converts away from,
  and it is stated correctly and with the frame named. **VERDICT: AGREES.**

**Appendix E — Marker Pose Recovery (Chapter 4's territory; listed because it is
the upstream of Chapter 5's `R_obj`).**
- **A-E · eq (E.1), the surrounding prose, and Table E.1's "Translation t (m)" column** —
  bare `R`, bare `t`, bare `w`, bare `[w]×`, all describing marker-frame poses in
  the camera frame. Direction is establishable: the prose "The third column is the
  marker's own outward normal in the camera frame" fixes `R`'s columns as the
  marker axes in {C}, i.e. `^C_M R`, and `t` is `^C P_MORG`.
  **VERDICT: UNLABELLED.** Flagged for the Chapter 4 auditor; the labels
  `^C_{M0} T`, `^C_{M1} T`, `^C_{M2} T` follow once the marker frames are named.

---

## 5. Suspected wrong transformation directions in the code

**None found.** Reported separately, as instructed, and the finding is negative:

- `carry.py:117` and `recovery_core.py:111` use `Rᵀ` for world→object; required.
- `carry.py:126` and `recovery_core.py:147` use `R` for object→world; required.
- `shoulder.py:70,78,121` use `Rᵀ` for person-space→local; required.
- `shoulder.py:120` composes `R_root @ Ry @ Rz @ Rx` left-to-right along the chain; frame cancellation holds.
- `carry.py:60,73,79` build `{P}→{Wu}→{Wl}` with `G` on the left for both points and rotations; correct.
- `recovery_core.py:65-72` inverts that chain; the apparent double `[1,−1,1]` flip at lines 71 and 72 is deliberate (invert to camera, then re-apply the solver's flip) and nets to the identity, leaving a person-space point. Correct.
- `check_v1_overlay.py:174-175` uses `R_root @ up` for local→person-space in forward kinematics; correct and the mirror image of the solve.

Every direction I could check is right. The defects are in the printed notation.

---

## 6. Assessment: how much of this is notation and how much is substance

**Notation only (about 64 of 94 items, all the UNLABELLED ones).** These are real
defects under the author's rule, but the underlying mathematics and the code are
correct. Fixing them is mechanical **once the frames exist** — which is the catch
below.

**Substance (about 20 items).**

1. **The frame inventory is incomplete, and that blocks the rule.** Six of the
   thirteen frames Chapters 3 and 5 actually use have no letter, and four have no
   definition at all: the untwisted upper-arm frame that eq (3.22) maps into, the
   forearm/wrist frames Figure 3.5 draws, the mirrored root basis the left-arm
   solver works in, and the unlevelled Unity world that sits between Chapter 4's
   W and Chapter 5's W. The author cannot write `^A_B T` for eq (3.22) today
   because neither A nor B has a name. This is a modelling gap that the notation
   rule has exposed, not a typography problem.

2. **Chapter 3's subscript convention is ambiguous, not merely incomplete
   (C3-10, C3-13).** `R_root` and `R_sh,r` use the same subscript slot for
   opposite roles, and a consistent reading of `R_sh,r` contradicts eq (3.13).
   That is a genuine reading error waiting to happen in the chapter that
   defines the chain.

3. **Chapter 5's Table 5.1 makes a factually wrong attribution (C5-02, C5-03).**
   `o` and `R_obj` are *not* the translation column and rotation block of
   Chapter 4's `T_WO`. At frame 560, Chapter 4's translation column is
   (−0.2234, 0.4171, −0.1763) and Chapter 5 prints (−0.22, 0.08, 0.45). Two
   transforms sit between them — the Unity y/z swap and a 32.04° gravity
   levelling — and neither appears anywhere in the thesis's notation. A reader
   trying to reproduce Chapter 5 from Chapter 4 cannot. This is the most
   substantive defect I found and it is independent of Craig: the sentence is
   simply not true as written.

4. **The letter W denotes two frames 32° apart (C5-37).** Chapter 4 states
   gravity reads (−0.02, 0.53, 0.85) in world coordinates, 32° off the world z
   axis; Chapter 5 calls its frame "the levelled world frame W". Both cannot be W.

5. **One symbol carrying two frames is printed as a declared convention
   (C5-04, C5-16, C5-32).** Table 5.1's frame column literally reads
   "levelled world frame W, then P" for `w`, and §5.6 prints two numerically
   different `w` vectors four lines apart. This is the exact practice Craig's
   notation exists to eliminate, and it is currently documented as intentional.

6. **Two Craig distinctions are not made anywhere (C3-26, C3-31, C3-33).**
   Fixed angles versus Euler angles, and matrix-as-description versus
   matrix-as-operator. Both are corrigible in prose; neither changes a number.

7. **Two glyph collisions (C3-31 `x̂`, C5-01/C5-15 `p_wr`).** `x̂` is the root
   frame's x axis in §3.2/§3.5 and the rest arm axis in §3.4.2; `p_wr` is a
   person-space point in eqs (5.6)/(5.8)/(5.12) and a world-frame point in
   eqs (5.1)/(5.2). Both are substantive because both appear in numbered
   equations with printed numerical values.

**Bottom line.** Roughly two thirds of the work is mechanical relabelling that
cannot start until the author names six frames. The remaining third — items 1
to 5 above — are real defects in what the thesis asserts, and three of them
(C5-02, C5-03, C5-37) are wrong statements about the pipeline rather than
notation preferences. None of them implies a change to any number or to any
transformation direction in the code.

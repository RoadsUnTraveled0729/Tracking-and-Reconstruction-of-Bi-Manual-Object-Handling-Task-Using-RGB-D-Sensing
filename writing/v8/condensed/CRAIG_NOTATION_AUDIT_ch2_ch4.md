# Craig notation audit — Chapter 2 (Experimental Setup) and Chapter 4 (Object Tracking)

Working document, not thesis prose. Read-only audit: nothing in the repository was
modified to produce it, and it proposes no change to any numerical value and no change
to any transformation direction.

Convention used throughout (Craig, *Introduction to Robotics*, 4th ed., ch. 2):

- `^A_B R` — orientation of {B} relative to {A}; **columns of `^A_B R` are the axes of {B} expressed in {A}**.
- `^A P_BORG` — position of the origin of {B} expressed in {A}.
- `^A_B T = [ ^A_B R  ^A P_BORG ; 0 0 0  1 ]`, and `^A P = ^A_B T ^B P`.
- Cancellation: `^A_B T ^B_C T = ^A_C T`.
- A *frame-relative transform* describes one frame in another. An *operator* acts on a
  vector inside one frame. Craig separates them; this audit says which each instance is.

Scope covered: Chapter 2 (all sections), Chapter 4 (all sections), and the appendix
sections that carry transforms belonging to those chapters — **Appendix C** (landmark
extraction, ch. 2 §2.3), **Appendix D** (deprojection, ch. 2 §2.3 / §2.2.2), **Appendix E**
(marker detection and pose recovery, ch. 2 §2.4 and ch. 4), **Appendix G** (hip depth
preparation, ch. 2 §2.6). **Appendix A** (recording), **Appendix B** (workstation) and
**Appendix F** (filter characteristics) were read and contain no rotation matrix,
homogeneous transform, position vector or composition. **Appendix H** belongs to
Chapter 3 and was not audited.

---

## 1. Summary — counts by verdict

| Verdict | Count |
|---|---|
| AGREES (correct direction **and** both frames identifiable as printed) | 12 |
| UNLABELLED (direction established, but printed without both Craig frame labels) | 32 |
| MISLEADING (direction right, notation or presentation ambiguous / non-Craig) | 3 |
| **CONTRADICTS** | **0** |
| **UNRESOLVED** | **4** |
| **Total inventory items** | **51** |

**No item CONTRADICTS.** Every transform direction stated in Chapters 2 and 4 that could
be checked against the implementing code is the direction the code implements. The defect
in these two chapters is notational density, not wrong geometry. See §7 for the
notation-versus-substance assessment.

### 1a. The four UNRESOLVED items (what is needed for each)

| ID | Item | Why unresolved | What is needed |
|---|---|---|---|
| **C4-08** | `p_i`, `p_last` in equation (4.3) | The chapter calls the input "the world-frame track", but the implementing script `eval/common/clean_object_track.py:59` reads the **Unity** columns (`unity_px/py/pz`), not the world columns (`tx/ty/tz`). Both give the identical number because `S` is orthogonal, so `‖S x‖ = ‖x‖`. The frame therefore cannot be settled from the code. | An author ruling: declare equation (4.3) in **{W}** (`^W P_OORG(i)`) or in **{U}** (`^U P_OORG(i)`). If {W} is declared, record in the builder comment that the script evaluates it on the Unity copy of the same row and that `S` being orthogonal makes the two identical. **This is a declaration, not a correction — do not change the code.** |
| **C4-09** | `R_i`, `R_last` in equation (4.3) | Same cause: `clean_object_track.py:60-61` rebuilds `R` from the **Unity** Euler columns. The reference frame cancels out of `angle(R_lastᵀ R_i)` entirely (trace is similarity-invariant under `R_U = S R_W S`), so no evidence in the code can distinguish {W} from {U}. | Same ruling as C4-08. Once the frame X is declared: `angle( (^X_{O(last)} R)ᵀ ^X_{O(i)} R ) = angle( ^{O(last)}_{O(i)} R )`. Worth stating in the thesis that the reference frame cancels. |
| **A-D03** | Appendix D.2, "moved into the colour camera's frame through the known transformation between the two imagers" | The **depth imager frame has no label anywhere in the thesis** — it is absent from §2.2.1 and from Table 2.2 — and the inter-imager transform has no symbol. A frame label cannot be assigned to a frame that does not exist in the frame inventory. | The author must either (a) add the depth imager frame to §2.2.1 with a label, and give the transform its Craig form `^{C}_{D} T`, or (b) state explicitly that only the aligned colour-optical frame is ever used downstream and that the inter-imager transform is internal to the vendor library and is never printed. Option (b) is the smaller change and is true of the pipeline. |
| **A-E02** | Appendix E.3, equation (E.1), `R = I + sinθ [w]× + (1−cosθ)[w]×²` | Rodrigues' formula builds a rotation **operator** from an axis and an angle. It has no source/destination pair of its own. Craig's own ch. 2 writes an operator as `R_K(θ)` with no leading frame superscript, which is in direct tension with the new rule that every printed `R` carry both frames. | An author ruling on how the operator case is written under the new rule. Recommended: print it as `R(ŵ, θ)` (Craig's `R_K(θ)`), state in the sentence that it is an operator and not a frame relationship, then label the *instance* in E.4 as `^C_O R`. **I have not guessed a frame pair for (E.1).** |

### 1b. Type mismatches — flagged with the same prominence

These are not direction errors, so they are not CONTRADICTS; but they are substantive
notation defects that block a naive Craig relabelling, and the author must see them.

| ID | Item | Problem |
|---|---|---|
| **C2-07** | `F` in Table 2.2 | `F = diag(1, −1, 1)`, `det F = −1` (`v1/kinematics/root_frame.py:9`; Chapter 3 §3.1 states the determinant explicitly). It is an improper matrix — a handedness-changing reflection — so it is **not** a member of SO(3) and **cannot** be written `^P_C R` or `^P_C T` without misrepresenting it. Table 2.2 nevertheless lists it under "The transformations between the frames of the thesis". |
| **C2-10** | `S` in Table 2.2 | `S = [[1,0,0],[0,0,1],[0,1,0]]`, `det S = −1` (`v1/aruco/frames.py:38-40`). Same problem as `F`. It is also applied by *conjugation* for rotations (`R_U = S R_W S`, `frames.py:85-88`), which is a change of basis for an operator, not a Craig transform chain. Also 3×3, placed beside 4×4 `T`s. |
| **C2-15** | Table 2.2 caption | "A transformation written with two frame letters carries a point from the second frame into the first." Correct and Craig-compatible — but it covers only five of the nine symbols in the table it captions (it says nothing about `F`, `S`, `T_root`, `T_sh`, `T_el`), and it does not cover translation **vectors**, which Chapter 4 then writes with the same two-letter pattern under a *different* semantics. |

### 1c. Symbol collisions that block the new rule

| ID | Collision | Consequence |
|---|---|---|
| **X1** | `U` = the **Unity frame** (§2.2.1, Table 2.2 row 9, Figure 2.4(b)) **and** `U` = the left singular-vector matrix in equation (2.1) (§2.2.2, reused by reference in ch. 4 §4.3). | `^U_W T` is unreadable one page after `M̄ = U Σ Vᵀ`. **Blocking for the new rule.** Rename one of them before any Craig relabelling. |
| **X2** | `t` = **translation vector** (equation (4.2); `t_CO`, `t_WO`, `t_WC` in §4.3; the "Translation t (m)" column of Table E.1) **and** `t` = **time** (equation (4.3), `t_i`, `t_last`; `clean_object_track.py:62` reads `time_s` into `t`). | Two incompatible meanings one page apart inside Chapter 4. Rename the time variable (e.g. `τ`) or the translation. |
| **X3** | `P` = **person space** (§2.2.1) **and** `P` = Craig's symbol for a position vector (`^A P`), which the new rule imports. | `^P P` (a point in person space) is unreadable. Needs an author ruling: rename person space, or use a lower-case point symbol. Note `eval/offset/carry.py:24` already uses `P` for the world→Unity swap matrix — a third meaning in the code. |
| **X4** | `W` = **world frame** and `w` = the Rodrigues axis (Appendix E.3/E.4), `w_max` = the angular rate bound (equation 4.3). | Case-separated, so tolerable, but `^W` beside `[w]×` in adjacent material is worth a deliberate check. Minor. |

### 1d. Compositions that do not cancel as printed

| ID | Composition | Status |
|---|---|---|
| **C2-05 / C4-04** | `T_WO = T_CW⁻¹ T_CO` (Table 2.2 row 4 and equation (4.1)) | Mathematically correct and matches the code exactly. But **the frames do not cancel as printed**: the adjacent indices read `…W` then `C…`, not `C` against `C`. The cancellation appears only after the reader silently rewrites `T_CW⁻¹` as `T_WC`. Craig form that does cancel: `^W_O T = ^W_C T ^C_O T`, with `^W_C T = (^C_W T)⁻¹` stated separately. This matters because Chapter 4 §4.1 spends a whole paragraph *arguing* from the cancellation ("The camera frame enters the chain twice… The two contributions cancel") while the printed equation never shows it. |
| **C4-16** | `R_WO = Rᵀ R_CO` ; `t_WO = Rᵀ t_CO + t_WC` | Same problem in its block form, made worse by a **bare `Rᵀ`** sitting beside a labelled `R_CO` in the same displayed equation. In Craig form, `^W_O R = ^W_C R ^C_O R` and `^W P_OORG = ^W_C R ^C P_OORG + ^W P_CORG` cancel visibly. |
| **C4-09** | `R_lastᵀ R_i` (equation 4.3) | **This one does cancel** once the transpose is named: `(^X_{O(last)} R)ᵀ ^X_{O(i)} R = ^{O(last)}_X R ^X_{O(i)} R = ^{O(last)}_{O(i)} R`. It is the only composition in these two chapters whose Craig cancellation is already visible in structure. Worth saying so in the thesis. |

---

## 2. Frame inventory

**Does the thesis define its frames in one place?** Partly, and this is the best part of
the present notation. Section 2.2.1 ("The Frames") plus Table 2.2 *is* a frame inventory,
and it is the right idea. It is however **incomplete in five ways**, and under the new rule
the gaps are blocking, because a subscript that names an undefined frame cannot be read.

| Frame | Label the thesis gives it | Where defined | Status |
|---|---|---|---|
| Camera (colour optical) | **C** | §2.2.1, Figure 2.4(a) | Defined. Matches `v1/aruco/frames.py:10-11` ("X right, Y down, Z forward, meters"). |
| Depth imager | *(none)* | Appendix D.2 only, in words | **MISSING from the inventory.** Needed by A-D03. Suggested label `{D}`. |
| World (desk marker) | **W** | §2.2.1 | Defined. Matches `WORLD_ID = 2`, `frames.py:34`. |
| Wall marker | *(none — subscripted "wall")* | §2.2.1 in words; Table 2.2 row 2 as `T_C,wall` | **NO SYMBOL.** Suggested label `{Wl}` (avoid `W`). |
| Object marker | **O** | §2.2.1 | Defined. Matches `OBJECT_ID = 1`. |
| Generic marker frame | *(none)* | Appendix E.2, "the printed marker gives the same four corners in its own frame" | **NO SYMBOL.** Suggested `{M}`, instantiated per marker. |
| Person space | **P** | §2.2.1, ch. 3 §3.1 | Defined, but collides with Craig's point symbol (X3). |
| Unity | **U** | §2.2.1, Figure 2.4(b) | Defined, but collides with the SVD `U` (X1). |
| Root (torso) | *(subscript only: `T_root`)* | §2.2.1 in words ("a frame on the torso, called the root frame") | Named, no formal label. Suggested `{Rt}`. |
| Shoulder, elbow (×2 sides) | *(subscripts `T_sh`, `T_el`)* | §2.2.1 in words | **Parents never named** ("their parent frame"), **sides never distinguished**. From the code the parents are: shoulder → root; elbow → upper-arm (shoulder) frame. Suggested `{ShR} {ShL} {ElR} {ElL}`. |
| Gravity-levelled world | *(none)* | Never defined. Appears as the printed axis labels "levelled x (m)" / "levelled z (m), away from the camera" in Figure 2.5(b) (`make_ch2_frames_fig.py:212-213`) and implicitly in ch. 4 §4.3 ("projected onto the measured gravity direction") | **MISSING from the inventory.** Built in `eval/offset/carry.py:54-69` as `G = from_to_rotation(g, [0,1,0])` applied to Unity-axis points. Suggested `{L}`. |
| Avatar rig root | *(none)* | Figure 2.4(b) caption; ch. 3 §3.1 explicitly says the measured root frame "is not the avatar root frame of Figure 2.4(b)" | **MISSING from the inventory**, and explicitly distinguished from a frame that *is* in the inventory. |

**Complete list of frames Chapters 2 and 4 actually need**, with the short label I would give
each: `{C}` camera colour-optical; `{D}` depth imager; `{W}` world / desk marker; `{Wl}` wall
marker; `{O}` object marker; `{M}` generic marker (Appendix E); `{P}` person space; `{U}` Unity;
`{L}` gravity-levelled world. (`{Rt}`, `{ShR/L}`, `{ElR/L}` are needed by Table 2.2 rows 7 and 8,
but they belong to Chapter 3's audit for their definitions.)

---

## 3. Chapter 2 inventory

Builder: `writing/v8/condensed/scripts/build_ch2.py`. Line numbers are builder lines;
the rendered location is given alongside.

### 3.1 Section 2.2.1 — The Frames

| ID | Location | Present notation | Actually maps | Translation expressed in | Mult. order (code) | Transpose / inverse | Craig form | Frame-relative or operator | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **C2-01** | `build_ch2.py:219-220`; §2.2.1 sentence "The pose of a frame B seen in a frame A is written `T_AB`" | `T_AB` | Generic definition. Frame-relative reading here; Table 2.2's caption gives it the point-carrying reading. Both are Craig-legitimate for the same matrix. | {A} | n/a | none | `^A_B T` | **Both readings, never reconciled.** §2.2.1 introduces it as a description of {B} in {A}; ch. 4 §4.1 then says it "maps a point of the world frame into camera coordinates". The thesis never states these are the same object. | **UNLABELLED** (flat subscript; the author's rule names `T_AB` explicitly as a forbidden form) |

### 3.2 Table 2.2 (`build_ch2.py:225-235`)

Code evidence common to rows 1–5: `v1/aruco/frames.py:10-13` — *"A marker's (R, t) maps
marker-frame points into the camera frame"*; `frames.py:45-52` `rt_from_row`;
`frames.py:55-59` `make_T`; `frames.py:62-64` `inv_T`;
`v1/aruco/calibrate_scene.py:36-68` `calibrate_static`, `:123-134` the anchor block,
`:249-266` the per-frame object loop, `:300-306` the JSON keys.

| ID | Row | Present | Actually maps | Translation in | Mult. order verified in code | Transpose / inverse | Craig form | Type | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **C2-02** | 1 | `T_CW` — "from the world frame W into the camera frame C" | {W} → {C} | {C}: `^C P_WORG` | `calibrate_scene.py:125` builds it; used at `:132` (`inv_T`), `:133`, `:251` | none in the symbol | `^C_W T` | frame-relative (the calibrated pose of {W} in {C}); becomes an operator when inverted | **UNLABELLED** (direction AGREES) |
| **C2-03** | 2 | `T_C,wall` — "from the wall marker frame into the camera frame C" | {Wl} → {C} | {C}: `^C P_{Wl}ORG` | `calibrate_scene.py:125` (`STATIC_IDS` includes 0); `:301` `T_cam_wall`; consumed at `:133` | none | `^C_{Wl} T` | frame-relative | **UNLABELLED** + source frame has no declared label (direction AGREES) |
| **C2-04** | 3 | `T_CO` — "from the object frame O into the camera frame C" | {O} → {C} | {C}: `^C P_OORG` | `calibrate_scene.py:213-214`, `:249-251`; also `writing/v8/condensed/scripts/make_ch4_experiment_fig.py:76-78` maps marker-frame corners into {C} with it | none | `^C_O T` | frame-relative; used as an operator on the corner points in the figure code | **UNLABELLED** (direction AGREES) |
| **C2-05** | 4 | `T_WO = T_CW⁻¹ T_CO` — "from the object frame O into the world frame W" | {O} → {W} | {W}: `^W P_OORG` | `calibrate_scene.py:132` + `:251` `T_w = T_desk_cam @ make_T(*rt)`; live path `v2/object/v2_object.py:73,137` identical | inverse present; **required** | `^W_O T = ^W_C T ^C_O T` | frame-relative | **UNLABELLED** + composition does not cancel as printed (§1d) (direction AGREES) |
| **C2-06** | 5 | `T_WC = T_CW⁻¹` — "from the camera frame C into the world frame W" | {C} → {W} | {W}: `^W P_CORG` | `calibrate_scene.py:132` `T_desk_cam = inv_T(T_cam[WORLD_ID])`; reported at `:305` as `poses_world.camera` | inverse present; **required** | `^W_C T` | frame-relative | **UNLABELLED** (direction AGREES) |
| **C2-07** | 6 | `F` — "from the camera frame C into person space P, fixed, the y flip" | {C} → {P}, points only | n/a (no translation) | `v1/kinematics/root_frame.py:9,12-14`; `v3/replay/runner.py:27,56`; `eval/offset/carry.py:25` (`D`) | none; `det F = −1` | **none available.** An improper matrix is not a Craig `^P_C R`. | **OPERATOR on points only** — ch. 3 §3.1 says so ("The flip applies to points only, never to rotation matrices") | **UNLABELLED** + **type mismatch** (§1b). Direction AGREES with the code. |
| **C2-08** | 7 | `T_root` — "the root frame into person space P" | {Rt} → {P} | {P}: `^P P_{Rt}ORG`, the L24 hip landmark | `v1/kinematics/root_frame.py:21-32` `build_root_frame` — *"Columns of R are the person's [right \| up \| forward]"*, i.e. Craig's column semantics; `shoulder.py:70,78` consume it as `R_root.T @ v` | none | `^P_{Rt} T` | frame-relative | **UNLABELLED** (single subscript names only the child). Direction AGREES. |
| **C2-09** | 8 | `T_sh, T_el` — "the shoulder and elbow frames into their parent frame" | shoulder: {Sh} → {Rt}. elbow: {El} → {Sh}. | in the respective parent | `v1/kinematics/shoulder.py:5` `R_sh = Ry·Rz·Rx`, `:70,78` `a = R_root.T @ (p14−p12)` → parent is the root; `:120-123` `R_arm = R_root @ (Ry Rz Rx)`, `g = R_arm.T @ (p16−p14)` → elbow's parent is the upper-arm frame. Left side via `MIRROR = diag(−1,1,1)` at `:127`. | transposes used to express vectors in the parent basis; required | `^{Rt}_{ShR} T`, `^{ShR}_{ElR} T` (and the L pair) | frame-relative | **UNLABELLED** — the destination "their parent frame" is not a frame label and the two sides are not distinguished. Direction AGREES. |
| **C2-10** | 9 | `S` — "from the world frame W into the Unity frame U, fixed, y and z swapped" | {W} → {U} for points; conjugation `R_U = S R_W S` for rotations | n/a | `v1/aruco/frames.py:38-40, 85-88`; `eval/offset/carry.py:24` | none; `det S = −1`; `S = S⁻¹ = Sᵀ` | **none available.** Improper, so not a Craig `^U_W R`. | **OPERATOR** (coordinate-convention change) | **UNLABELLED** + **type mismatch** (§1b). Direction AGREES. |
| **C2-15** | caption | "A transformation written with two frame letters carries a point from the second frame into the first." | n/a | n/a | n/a | n/a | Correct statement of Craig's `^A P = ^A_B T ^B P` | rule statement | **MISLEADING** — covers 5 of the 9 symbols in its own table and says nothing about vectors (see §1b) |
| **C2-14** | Figure 2.5 arrow labels, `make_ch2_frames_fig.py:103-107` (panel a) and `:205-208` (panel b) | `T_{C,wall}`, `T_{CO}`, `T_{CW}` drawn as arrows **from C to the target**, and `T_{WO}` drawn **from W to O** | The matrices map the **opposite** way (Wl→C, O→C, W→C, O→W) | as above | arrow endpoints: `tarrow(ax, c_anchor, uv_W, "$T_{CW}$")` etc. | none | `^C_{Wl} T`, `^C_O T`, `^C_W T`, `^W_O T` | The arrows read as **frame-relative** ("{W} described in {C}"); the table's caption reads the same symbols as **operators** ("carries a point from W into C"). | **MISLEADING** — both readings are Craig-valid for the same matrix, but the thesis states only the operator reading and neither the caption nor the figure says how an arrow is to be read. The arrows therefore read *against* the table's own stated direction. |

### 3.3 Section 2.2.2 — Scene Calibration

| ID | Location | Present | Actually is | Frame | Code evidence | Transpose / inverse | Craig form | Type | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **C2-11** | `build_ch2.py:244-247`; "Writing `M̄` for that element-wise mean, its singular value decomposition is `M̄ = U Σ Vᵀ`" | `M̄`, `U`, `Σ`, `Vᵀ` | `M̄` is the element-wise arithmetic mean of the ten calibration-window samples of `^C_W R` (desk) or `^C_{Wl} R` (wall). Not orthonormal — correctly **not** written `R`. | expressed in {C} | `v1/aruco/frames.py:71` `M = np.mean(Rs, axis=0)`; `calibrate_scene.py:56` | none | e.g. `^C_W M̄` (or `M̄` with its instantiation named) | intermediate matrix, becomes a frame-relative rotation after projection | **UNLABELLED**. `U` collides with the Unity frame (X1). |
| **C2-12** | `build_ch2.py:249-251`; **equation (2.1)** `R = U diag(1, 1, det(U Vᵀ)) Vᵀ` | bare `R` | the projected chordal-mean rotation. **Instantiated three different ways**: `^C_W R` and `^C_{Wl} R` in the calibration, and `^W_O R` in Chapter 4's rotation smoother. | {C} for the first two, {W} for the third | `frames.py:71-74` `chordal_mean`; `calibrate_scene.py:56`; `v1/aruco/filter_object_track.py:174-178` (the ch. 4 use, on `R_COLS`, i.e. world rotations) | `Vᵀ` is an SVD factor, not a frame inverse; no frame inverse present | **must stay generic**: `^A_B R = U diag(1,1,det(UVᵀ)) Vᵀ`, with the instantiations named in prose | operator (a projection onto SO(3)) whose *output* is a frame-relative rotation | **UNLABELLED**. **Do not label it `^C_W R`** — that would be wrong for the Chapter 4 use. |
| **C2-16** | Table 2.3, "Wall marker pose in the world \| calibrated wall pose carried through the inverse anchor" | prose, no symbol | `^W_{Wl} T` | {W} | `calibrate_scene.py:133` `T_desk_wall = T_desk_cam @ T_cam[0]` = `^W_C T ^C_{Wl} T`; **frames cancel** | inverse present in "inverse anchor"; required | `^W_{Wl} T = ^W_C T ^C_{Wl} T` | frame-relative | **AGREES** (prose is correct and unambiguous). Propose printing the symbol. |
| **C2-17** | Table 2.3, "Camera pose in the world \| the inverse of the anchor, from C into W of Table 2.2" | prose, no symbol | `^W_C T` | {W} | `calibrate_scene.py:132`, `:305` | inverse; required | `^W_C T` | frame-relative | **AGREES** |
| **C2-18** | Table 2.3, "Gravity direction \| up axis in the plane of the calibrated wall marker, signed by the depth plane" | prose, no symbol | the **second column** of `^W_{Wl} R`, i.e. the wall frame's ŷ axis expressed in {W} | {W} | `calibrate_scene.py:148` `up_w = T_desk_wall[:3,:3][:,1]`; sign fixed at `:146,149-150` against `seed_w = R_dc @ up_cam` (= `^W_C R ^C û`, rotation only, correctly no translation for a free vector) | none | `^W ĝ` (a free direction vector, not a point) | The column extraction is **exactly Craig's column semantics** and the code uses it correctly. The `R_dc @ up_cam` step is a correct rotation-as-operator on a direction. | **AGREES** on substance; no symbol printed. Propose `^W ĝ`. |

### 3.4 Section 2.4 — Object Pose from ArUco Markers

| ID | Location | Present | Actually | Verdict |
|---|---|---|---|---|
| **C2-13** | `build_ch2.py:285` — "The result is the pose of the marker in the camera frame C. For the object marker this pose is the transformation from O into C of Table 2.2" | prose, no symbol | `^C_O T`. Confirmed by `v1/aruco/frames.py:10-13` and `calibrate_scene.py:251`. Frame-relative. | **AGREES**. Adding `^C_O T` here would help but the prose is not ambiguous. |

---

## 4. Chapter 4 inventory

Builder: `writing/v8/condensed/scripts/build_ch4.py`.

### 4.1 Section 4.1 — World Anchoring and Camera Placement Invariance

| ID | Location | Present | Actually maps | Translation in | Mult. order (code) | Transpose / inverse | Craig form | Type | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **C4-01** | `build_ch4.py:145-146`; "The calibrated anchor `T_CW` maps a point of the world frame into camera coordinates" | `T_CW` | {W} → {C} | {C}: `^C P_WORG` | as C2-02 | none | `^C_W T` | Given the **operator** reading here, where §2.2.1 introduced `T_AB` as a **frame-relative** pose. Same matrix, two readings, never reconciled. | **UNLABELLED** (direction AGREES) |
| **C4-02** | `build_ch4.py:146-147`; "the per-frame object pose `T_CO` maps a point of the object frame into camera coordinates" | `T_CO` | {O} → {C} | {C}: `^C P_OORG` | as C2-04 | none | `^C_O T` | operator reading | **UNLABELLED** (direction AGREES) |
| **C4-03** | `build_ch4.py:147-148`; "The chain must deliver `T_WO`, the object as seen from the world" | `T_WO` | {O} → {W} | {W}: `^W P_OORG` | as C2-05 | none | `^W_O T` | frame-relative reading ("as seen from") — two sentences after the operator reading of C4-01/02 | **UNLABELLED** (direction AGREES) |
| **C4-04** | `build_ch4.py:150`; **equation (4.1)** `T_WO = T_CW⁻¹ T_CO` | `T_WO`, `T_CW⁻¹`, `T_CO` | {O} → {W} via {C} | {W} | `v1/aruco/calibrate_scene.py:132` + `:251`; live path `v2/object/v2_object.py:73,137` — **byte-for-byte the same chain** | inverse present; **required** (the calibration produces `^C_W T`, the chain needs `^W_C T`) | `^W_O T = ^W_C T ^C_O T`, with `^W_C T = (^C_W T)⁻¹` stated separately | frame-relative | **UNLABELLED** + composition does not cancel as printed (§1d). Direction AGREES. |
| **C4-05** | `build_ch4.py:154-156`; **equation (4.2)** `T = [R t; 0ᵀ 1]`, `T⁻¹ = [Rᵀ −Rᵀt; 0ᵀ 1]` | **bare `T`, `R`, `t` — no frames at all** | a generic rigid-transform identity; in this chapter it is instantiated only on the anchor, `T = ^C_W T` | {A} for the forward form | `v1/aruco/frames.py:55-64` `make_T` / `inv_T` (`return make_T(R.T, -R.T @ t)`) | transpose present and **required** (`R` orthonormal ⇒ `R⁻¹ = Rᵀ`); the code never inverts numerically | `^B_A T = (^A_B T)⁻¹ = [ ^A_B Rᵀ  −^A_B Rᵀ ^A P_BORG ; 0 0 0 1 ]` (Craig eq. 2.45). Instantiated: `^W_C T = [ ^C_W Rᵀ  −^C_W Rᵀ ^C P_WORG ; 0 0 0 1 ]`. | frame-relative identity | **UNLABELLED** (worst case: nothing carries a frame). Mathematics AGREES. |
| **C4-06** | `build_ch4.py:158-159`; "its translation column is the camera's own position in the world frame, so the camera pose in the reconstructed scene, `T_WC`, comes out of the anchoring" | `T_WC` | {C} → {W} | {W}: `^W P_CORG` — and the prose describes exactly Craig's `^W P_CORG`, correctly | `calibrate_scene.py:132`, `:305`; consumed by Unity at `Unity/Assets/Scripts/IntegratedSceneReceiverV2.cs:132` (`anchor.localPosition = posesPos[2]; // camera pose`) | inverse; required | `^W_C T` | frame-relative | **UNLABELLED** (direction AGREES) |
| **C4-07** | `build_ch4.py:161`; "The camera frame enters the chain twice, once as the destination of the object pose and once as the source of the inverted anchor. The two contributions cancel" | prose | a correct statement of Craig's cancellation rule | — | — | — | — | — | **AGREES** on substance. But the argument is made in prose while equation (4.1) does not display the cancellation — the strongest single case for rewriting (4.1) in Craig form. |

### 4.2 Section 4.2 — Filtering and Cleaning the Object Track

| ID | Location | Present | Actually | Frame | Code evidence | Transpose / inverse | Craig form | Type | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **C4-08** | `build_ch4.py:181-185`; **equation (4.3)**, first line `‖p_i − p_last‖ ≤ v_max \|t_i − t_last\|` | `p_i`, `p_last` (bare); `t_i`, `t_last` | `p` is the object-marker origin position at two samples. The step is a difference of two position vectors. | **{W} or {U} — unsettled.** | `eval/common/clean_object_track.py:59` `pos = df[["unity_px","unity_py","unity_pz"]]`; `:78` `np.linalg.norm(pos[i]-pos[last])/dt`. Upstream the track and filter are in {W} (`v1/aruco/filter_object_track.py:10,124,196`), Unity columns derived at `:198-205` via `unity_from_world`. `‖S x‖ = ‖x‖` because `S` is orthogonal, so both frames give the same number. | none | `^W P_OORG(i)` **or** `^U P_OORG(i)` — see §1a | position vectors, not transforms; the subtraction is an operator | **UNRESOLVED** (frame label). **Symbol collision X2**: `t` is **time** here (`clean_object_track.py:62`) and a translation vector in (4.2). Also: the vector norm is printed with single bars (`build_ch4.py:182`, `d(..., "\|", "\|")`), the same delimiter as the scalar `\|t_i − t_last\|` — use `‖·‖`. |
| **C4-09** | `build_ch4.py:184`; **equation (4.3)**, second line `angle(R_lastᵀ R_i) ≤ w_max \|t_i − t_last\|` | `R_last`, `R_i` (bare) | `R_lastᵀ R_i` is the relative rotation of the object frame between the two samples, expressed at the earlier sample | **{W} or {U} — unsettled**, and the reference frame **cancels out of the result** | `clean_object_track.py:60-61` `R = recompose_zxy(unity_ex/ey/ez)`; `:79` `cosang = (trace(R[last].T @ R[i]) - 1)/2`. Under `R_U = S R_W S`, `R_U(last)ᵀ R_U(i) = S (R_W(last)ᵀ R_W(i)) S`, and the trace is invariant. | transpose present and **required** — it inverts `^X_{O(last)} R` | `angle( (^X_{O(last)} R)ᵀ ^X_{O(i)} R ) = angle( ^{O(last)}_{O(i)} R )` | the product is a **frame-relative rotation** between two instants of {O}; `angle()` then reads its magnitude (operator on it) | **UNRESOLVED** (frame label, same cause as C4-08). **Frames do cancel** here (§1d). `angle()` is not defined in Chapter 4; Appendix E.4 gives `θ = acos((tr R − 1)/2)`. |
| **C4-10** | `build_ch4.py:167`; "on rotation, with a rolling chordal mean, which is equation (2.1) over a short window" | prose | equation (2.1) applied to `^W_O R` | {W} | `v1/aruco/filter_object_track.py:174-178` `chordal_mean(Rs[lo:hi])`, `Rs` from `R_COLS` (world rotations, `:125,197`) | none | `^W_O R` | operator producing a frame-relative rotation | **AGREES**. Confirms C2-12: equation (2.1) must stay generic, because it is instantiated on `^C_W R`, `^C_{Wl} R` **and** `^W_O R`. |
| **C4-19** | `build_ch4.py:190-192`; "`v_max` bounds the linear step and `w_max` the angular step" | `v_max`, `w_max` | scalar rate bounds | dimensionless of frame | `clean_object_track.py:44-45` `V_MAX = 1.0`, `W_MAX_DEG = 400.0` | none | n/a — scalars carry no frames | scalars | **AGREES** |
| **C4-21** | Figure 4.2 caption, "The object track in the world frame before and after the signal filter, one panel per world axis" | prose | {W} | {W} | `writing/v8/scripts/make_ch4_figs.py:172-174` reads `tx,ty,tz` — the world columns | — | — | — | **AGREES** |

### 4.3 Section 4.3 — Worked Example

| ID | Location | Present | Actually | Frame | Code / data evidence | Transpose / inverse | Craig form | Type | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **C4-11** | `build_ch4.py:201-204`; `M̄ = [3×3 numeric]`, "Averaging the ten desk rotations of the calibration window element by element gives" | `M̄` | element-wise mean of the ten `^C_W R` samples | {C} | `calibrate_scene.py:56`; `frames.py:71` | none | `^C_W M̄` | intermediate matrix | **UNLABELLED** |
| **C4-12** | `build_ch4.py:207-208`; "the projected rotation forms the frozen anchor `T_CW`. That anchor puts the calibrated desk marker 55.3 cm in front of the camera and 18.7 cm below it." | `T_CW` | {W} → {C} | {C} — the two distances are read straight off `^C P_WORG`, and the sentence's "in front of / below the camera" is the {C} reading | `eval/output/scene_calibration_r6bc.json` `T_cam_desk`; builder comment at `:207` records `(0.023458, 0.187377, 0.552492) m` | none | `^C_W T` | frame-relative | **UNLABELLED** (direction AGREES) |
| **C4-13** | `build_ch4.py:210`; "Gravity, taken from the wall marker, reads (−0.02, 0.53, 0.85) in world coordinates" | **no symbol at all** | a free unit direction vector | {W} (given in words) | `calibrate_scene.py:148-151, 278` `gravity_up_world` | none | `^W ĝ` | direction vector, not a point — Craig's leading superscript still applies | **UNLABELLED** |
| **C4-14** | `build_ch4.py:213`; `−Rᵀ t = (−0.01, −0.39, 0.43) m`, with "Transposing that rotation and applying it to the negated translation gives the inverse anchor" and "which is the camera's own position in the world frame" | **bare `R`, bare `t`** | `R = ^C_W R`, `t = ^C P_WORG`; result is `^W P_CORG` | result in {W}, operands in {C} | `frames.py:62-64` `inv_T`; `calibrate_scene.py:132` | transpose present and **required** | `^W P_CORG = − ^C_W Rᵀ ^C P_WORG = − ^W_C R ^C P_WORG` | **Both at once**, unmarked: `Rᵀ` acts as an **operator** on a position vector, and it *is* `^W_C R`, a **frame-relative rotation**. Craig separates these; the thesis prints neither label. | **UNLABELLED** (direction AGREES) |
| **C4-15** | `build_ch4.py:217`; `t_CO = (−0.21, 0.16, 1.02) m`, "camera-frame translation" | `t_CO` | position of {O}'s origin expressed in {C} | {C} | `eval/output/recording_20260831_065553_aruco_raw_scaled.csv` frame 533; corroborated by Appendix E Table E.1 row "id 1" | none | `^C P_OORG` | position vector | **UNLABELLED**, and a **semantics gap**: for `T`, "CO" means "from O into C" (Table 2.2 caption); for `t`, "CO" means "the position of O's origin in C". Both are Craig-consistent, but the thesis states only the first rule. |
| **C4-16** | `build_ch4.py:220-222`; `R_WO = Rᵀ R_CO` ; `t_WO = Rᵀ t_CO + t_WC` | `R_WO`, **bare `Rᵀ`**, `R_CO`, `t_WO`, `t_CO`, `t_WC` | `^W_O R = ^W_C R ^C_O R` and `^W P_OORG = ^W_C R ^C P_OORG + ^W P_CORG` | {W} for the results, {C} for `t_CO` | `calibrate_scene.py:251-252` — `T_w = T_desk_cam @ make_T(*rt)` then `R_w, t_w = T_w[:3,:3], T_w[:3,3]`; this block expansion is exactly that product | transpose present and **required**; `Rᵀ = ^W_C R` | `^W_O R = ^W_C R ^C_O R`; `^W P_OORG = ^W_C R ^C P_OORG + ^W P_CORG` | frame-relative rotation composition + operator action on a point | **UNLABELLED** — **the worst notation defect in Chapter 4**: one displayed equation prints a bare `Rᵀ` beside a labelled `R_CO` and a labelled `t_WC`. In Craig form the `C`-against-`C` cancellation becomes visible. Direction AGREES. |
| **C4-17** | `build_ch4.py:225-230`; `t_WO = (−0.24, 0.43, −0.19) m` ; `R_WO = [3×3 numeric]` | `t_WO`, `R_WO` | `^W P_OORG` and `^W_O R` on frame 533 | {W} | `calibrate_scene.py:251-259` writes exactly these as `tx,ty,tz` and `r11…r33`; builder comment at `:231-233` records the full-precision values | none | `^W P_OORG`, `^W_O R` | position vector; frame-relative rotation | **UNLABELLED** (direction AGREES) |
| **C4-18** | `build_ch4.py:234`; "Projected onto the measured gravity direction, the marker centre is 6.3 cm above the fitted tabletop plane" | prose | `^W ĝ · (^W P_OORG − ^W P_tabletop)` | {W} | `calibrate_scene.py:198,235` `table_pt_w = R_dc @ point_desk_cam + t_dc` (a correct Craig point map) | none | — | operator (a projection) | **AGREES**. But it implicitly invokes the gravity-levelled reading that Figure 2.5(b) labels "levelled x / levelled z" without ever defining that frame (§2). |
| **C4-20** | Figure 4.1 caption, "the axes on the cube are the object frame O from the pose the detector returns on that frame. The axes on the desk marker are the world frame W of the calibration." | prose, frame names only | The drawn axes are the **columns** of `^C_O R` and `^C_W R` — Craig's column semantics, implemented correctly | {C} | `writing/v8/scripts/frame_draw.py:31-33` `tips = o + T[:3, i] * length` (the i-th column of the rotation block) | none | `^C_O T`, `^C_W T` | frame-relative, drawn as axes | **AGREES** on notation. **Separate provenance finding — see §6, S1.** |

---

## 5. Appendix inventory (sections belonging to Chapters 2 and 4)

Appendix C (landmark extraction) prints camera-frame positions in Table C.2 under the
header "Camera-frame position (m)" and states the frame in every sentence; it prints no
`R`, `T` or bare vector symbol, so it raises no item under the new rule.

| ID | Location | Present | Actually | Frame | Code evidence | Transpose / inverse | Craig form | Type | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **A-D01** | Appendix D.1, "A point `p` with coordinates x, y and z in the camera frame projects … to the pixel" (before equation D.1) | bare `p` | a measured scene point | {C} (in words) | `writing/v8/scripts/frame_draw.py:12-22` `project` | none | `^C P` | position vector | **UNLABELLED** |
| **A-D02** | Appendix D.3, **equation (D.2)** `x = z(u−cx)/fx`, `y = z(v−cy)/fy`, `p = (x, y, z)` | bare `p` | the deprojected point | {C} | the inverse of `frame_draw.py:12-22`; consumed by the extractors and by `eval/` throughout | none | `^C P` | position vector | **UNLABELLED** |
| **A-D03** | Appendix D.2, "moved into the colour camera's frame through the known transformation between the two imagers" | no symbol; frame unnamed | `^{C}_{D} T` for an undeclared depth frame {D} | — | vendor library; not implemented in this repository | — | cannot be assigned — the frame does not exist in the inventory | frame-relative | **UNRESOLVED** (see §1a) |
| **A-D04** | Appendix D.3, "Converting the camera-frame point into the left-handed convention Unity uses is a separate fixed axis flip, developed in Section 3.1." | prose | Section 3.1's `F` maps {C} into **person space {P}**, not into the Unity frame {U}. Table 2.2 row 9 puts W→U under `S` (eq. 6.1). | — | the same slippage exists in the code: `v1/kinematics/root_frame.py:9,12` names the C→P flip `SENSOR_TO_UNITY` / `unity_from_sensor` | — | — | — | **MISLEADING** — calls `F`'s destination "Unity" where the thesis's own frame list calls it {P}. Direction is right. |
| **A-E01** | Appendix E.2, "finding the rotation `R` and the translation `t` that carry these four known points onto the four detected pixels" | **bare `R`, bare `t`** | `^C_M R` and `^C P_MORG` for a marker frame {M} | {C} | `v1/aruco/frames.py:10-13`; the mapping is exercised at `writing/v8/condensed/scripts/make_ch4_experiment_fig.py:76-78` `cam = (T_obj[:3,:3] @ corners.T).T + T_obj[:3,3]`, i.e. `^C P = ^C_O R ^O P + ^C P_OORG` — a textbook-correct Craig operator use | none | `^C_M R`, `^C P_MORG` | The sentence gives them the **operator** reading ("carry these four known points"), which is correct; they are simultaneously the frame-relative pose of {M} in {C}. | **UNLABELLED**. {M} also has no declared label (§2). |
| **A-E02** | Appendix E.3, **equation (E.1)** `R = I + sinθ [w]× + (1−cosθ)[w]×²` | bare `R` | Rodrigues' formula: builds a rotation **operator** from an axis and an angle | the output in E.4 is in {C}; the formula itself is frameless | `v1/aruco/filter_object_track.py:73-80` `exp_so3` | none | `R(ŵ, θ)` / Craig's `R_K(θ)` — **not** a frame pair | **OPERATOR**, explicitly | **UNRESOLVED** (see §1a — needs an author ruling on the operator case) |
| **A-E03** | Appendix E.4, Table E.1 column header "Translation `t` (m)", rows id 0 / id 2 / id 1 | bare `t` as a column header | `^C P_{Wl}ORG`, `^C P_WORG`, `^C P_OORG` | {C}; confirmed by the adjacent "Range (m)" column being their lengths, and by `calibrate_scene.py` reading the same CSV | `eval/output/…_aruco_raw_scaled.csv` | none | `^C P_{marker}ORG` | position vectors | **UNLABELLED** |
| **A-E04** | Appendix E.4, "The pose recovery returns the rotation `R = [3×3]`" and "`R = I + 0.04[w]× + 2.00[w]×² = [3×3]`" | bare `R` (twice) | `^C_O R` on frame 533 | {C} | `v1/aruco/frames.py:45-52` `rt_from_row`; the same matrix feeds `calibrate_scene.py:251` | none | `^C_O R` | frame-relative | **UNLABELLED** |
| **A-E05** | Appendix E.4, "`w = (1.00, 0.00, 0.03)`", "an axis close to the camera's x axis" | bare `w` | the rotation axis, a unit direction | {C} (given in words) | `filter_object_track.py:63-70` `log_so3` | none | `^C ŵ` | direction vector | **UNLABELLED** |
| **A-E06** | Appendix E.4, "The third column is the marker's own outward normal in the camera frame, (0.06, −0.04, −1.00)" | prose | the third column of `^C_O R` is `^C ẑ_O` | {C} | matches the printed matrix exactly | none | `^C ẑ_O` | **This is Craig's column semantics stated correctly in prose** — the clearest correct use of the convention in the appendices | **AGREES** (the symbol it refers to is the unlabelled `R` of A-E04) |
| **A-E07** | Appendix E.2, "the lobe whose in-plane up axis better agrees with an estimate of the gravity direction" | prose | column 1 of `^C_M R` compared against a `^C ĝ` seeded from the depth plane | {C} | `calibrate_scene.py:146-151` does the world-frame counterpart of the same comparison | none | — | column-of-rotation reading, correct | **AGREES** |
| **A-G01** | Appendix G.1, **equation (G.1)** `p* = z* p / p_z`, with "For a point `p` with camera-depth coordinate `p_z` greater than 5 centimetres, its retained ray is `p` divided by `p_z`" | bare `p`, `p*`, `p_z` | a landmark point and its depth-replaced repair | **person space {P}** — stated at the head of Appendix G ("The rules operate in person space P") | `v1/kinematics/occlusion_ext.py:418-419` `_ray(pt) = pt / pt[2] if pt[2] > 0.05`; the points arrive flipped (`v3/replay/runner.py:56` `points[name] = f * SENSOR_TO_UNITY`) | none | `^P P`, `^P P*` | **OPERATOR** on a position vector (a rescaling along the camera ray), not a frame relation | **UNLABELLED**. Note the appendix calls `p_z` the "camera-depth coordinate" while `p` is in {P}; it correctly explains that the y flip leaves z unchanged, but the two frames sit in one sentence. |

---

## 6. Reported separately: suspected substance, not notation

Per the brief, these are reported **prominently and separately** and are **not folded into any
notation recommendation**. I propose no change to any numerical value or transformation
direction on the basis of any of them.

**S1 — Figure 4.1 caption claims the calibrated anchor; the figure draws the per-frame
detection.** The caption (`build_ch4.py:143`) says "The axes on the desk marker are the world
frame W **of the calibration**". `writing/v8/condensed/scripts/make_ch4_experiment_fig.py:72,87`
draws them from `make_T(*rt_from_row(row, DESK_ID))` — the raw per-frame desk detection on
that panel's frame, not `calib["T_cam_desk"]`. Both are `^C_W T`, so the *direction* is right
and no value is wrong; the caption's *provenance* claim is not what the figure code does.
For a static marker the two are close, which is exactly why this would not be caught by
looking at the picture.

**S2 — Figure 2.5(b) mixes the 45 mm-scaled calibration with the unscaled (50 mm) object
detection.** `make_ch2_frames_fig.py:116-120` takes `T_cam_desk` from the **scaled**
`scene_calibration_r6bc.json` and composes it with `T_cam_obj_raw`, read at `:56,62` from the
**unscaled** `v1/aruco/output/…_aruco_raw.csv`. The header comment at `:18-21` explains that
the unscaled detections are used so that the *image overlay* in panel (a) reprojects
correctly — which is right for panel (a). Panel (b), however, is a metric top view: the cube
glyph at `:137,164` is placed from that unscaled pose, so it sits at roughly 50/45 of its true
range along the camera ray (~0.11 m at 1.02 m), while the grey object path beside it at
`:140-142` comes from the **scaled** clean track. Flagged for the figure owner to check; I am
not proposing a value change.

**S3 — `clean_object_track.py` reads the Unity columns where Chapter 4 describes a
world-frame track.** Detailed at C4-08/C4-09. **There is no numerical consequence** (`S` is
orthogonal, so the norm and the relative-rotation angle are identical in both frames), and
the code comment at `writing/v8/scripts/make_ch4_figs.py:212-214` shows the author already
knew this. It is a declaration the thesis must make, not a defect to fix in code.

**S4 — Code names that must not be used to infer frames.** `v1/kinematics/root_frame.py:9,12`
calls the C→P flip `SENSOR_TO_UNITY` / `unity_from_sensor`, and `build_root_frame`'s docstring
at `:24` says the columns are the person's axes "in Unity world" — but the thesis's frame list
reserves {U} for the desk-anchored Unity frame and calls this one {P}. The mathematics is
right in both; only the name is misleading. Similarly `eval/offset/carry.py:61`
`cam_pos = P @ T_dc[:3,3]` is in **Unity** axes despite the name. These are exactly the
name-based inferences this audit was told not to make, and they are recorded here so that a
later pass does not make them.

**S5 — Out of my scope, noticed in passing.** Chapter 4's closing sentence still reads
"Section 7.2 evaluates the object track **against the physically measured route**", while
`build_ch4.py:66-70` documents that the 2026-09-12 revision removed exactly that promise.
This is a Chapter 7 cross-reference matter, not a notation matter; passing it to the
coordinator only.

---

## 7. Assessment: how much of this is notation versus substance

**Substance: close to none.** Zero CONTRADICTS across 51 items. Every direction I could test
against the implementing code — the anchor `^C_W T`, the object pose `^C_O T`, the inversion,
the chain `^W_C T ^C_O T`, the wall-in-world composition, the gravity column extraction, the
root and shoulder and elbow parents, the block expansion in the worked example, the cleaning
rule's relative rotation — is the direction the code implements, in both the offline chain
(`v1/aruco/calibrate_scene.py`) and the live chain (`v2/object/v2_object.py`). The code's own
column semantics (`frame_draw.py:31-33`, `root_frame.py:24`, `calibrate_scene.py:148`) are
Craig's column semantics, used correctly. Nobody has mislabelled a camera-to-world transform
here.

**Notation: nearly all of it, and it is a large job.** 32 of 51 items are UNLABELLED. They
split into three kinds, in increasing order of effort:

1. *Flat two-letter subscripts* (`T_CW`, `T_CO`, `T_WO`, `T_WC`, `t_CO`, `t_WO`, `t_WC`,
   `R_CO`, `R_WO`, `T_AB`). Direction already correct and already recoverable from the
   symbol. These are a mechanical lift into `^A_B T`, *provided* X1 (the `U` collision) is
   settled first. Roughly 15 items.
2. *Bare symbols with the frame only in the surrounding words* (equation (4.2)'s `T`, `R`,
   `t`; equation (4.3)'s `p` and `R`; `−Rᵀ t`; `Rᵀ` inside `R_WO = Rᵀ R_CO`; Appendix E's
   `R` and `t` and `w`; Appendix D's `p`; Appendix G's `p`). These need the direction
   *established* before a label can be written, which this audit has now done for all of
   them except the four UNRESOLVED. Roughly 13 items.
3. *Symbols that cannot take a Craig label at all* — `F`, `S` (improper, `det = −1`), and
   equation (E.1) (an operator). These are the genuinely interesting ones: a cosmetic
   relabelling would put `^P_C R` on a reflection and `^U_W R` on a handedness swap, which
   would be worse than the present notation, not better. They need a stated exception, not
   a label.

**The three things that would change the thesis rather than its typography:**

- Rewriting equation (4.1) as `^W_O T = ^W_C T ^C_O T` with the inverse stated separately.
  Chapter 4 §4.1 argues its central claim — camera-placement invariance — *from* frame
  cancellation, and the present equation is the one place where the cancellation is invisible.
  This is the single highest-value change in the two chapters.
- Rewriting the `R_WO = Rᵀ R_CO` / `t_WO = Rᵀ t_CO + t_WC` pair (C4-16). A bare `Rᵀ` beside a
  labelled `R_CO` in one displayed equation is the clearest defect in the chapter, and the
  Craig form makes the same cancellation visible in the worked example.
- Completing the frame inventory (§2) and resolving X1 and X2. Without these the new rule
  cannot be applied at all: `^U_W T` cannot be written while `U` is also the SVD factor, and
  `^A P` cannot be adopted while `P` is also person space.

**The two things that would be wrong to do:** hard-labelling equation (2.1) as `^C_W R` (it is
instantiated on three different frame pairs, including `^W_O R` in Chapter 4), and giving
`F`, `S` or equation (E.1) a frame pair they do not have.

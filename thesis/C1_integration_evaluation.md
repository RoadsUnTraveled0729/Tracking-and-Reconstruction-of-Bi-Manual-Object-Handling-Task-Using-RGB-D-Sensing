# C1. Integration and accuracy evaluation

The evaluation layer: the MediaPipe-driven person (Pipeline A) and the
ArUco-reconstructed scene (Pipeline B) placed in ONE desk-anchored
world, so that B's independently measured object trajectory can grade
A's independently measured wrist trajectory. This chapter derives the
single new piece of math (the person→scene anchor), states the
independence argument that makes the comparison meaningful, and
presents the accuracy results.

Implementation: `integration/send_integrated_scene.py`,
`Unity/Assets/Scripts/IntegratedSceneReceiver.cs`,
`integration/plot_integrated_scene.py`,
`integration/validate_integration.py`,
`integration/analyze_object_offset.py`.

## 1. The anchor transform

Pipeline A solves in person space $\mathcal{P}$ (camera frame, $y$
flipped: $q = F p_\mathcal{C}$, $F = \mathrm{diag}(1,-1,1)$).
Pipeline B's world is the desk frame $\mathcal{W}$, mapped to Unity by
the swap $P$ (B1 §7). A person-space point lands in the scene as

$$
p_{scene} = M\,q + P\,t^{desk}_{cam}, \qquad
M = P\,R^{desk}_{cam}\,F .
$$

Derivation: undo the flip ($F^{-1} = F$) to reach camera coordinates,
apply the calibrated camera-to-desk rotation, then map into Unity —
$M = P\,R^{desk}_{cam}\,F$ read right-to-left.

**$M$ is a proper rotation.** $\det P = \det F = -1$ and
$\det R^{desk}_{cam} = +1$, so $\det M = (-1)(+1)(-1) = +1$: the two
handedness flips cancel, and the left-handed person space maps into the
left-handed scene with no residual reflection.

**Factorization into transforms Unity already has:**

$$
M = R_\mathcal{U}(cam)\; R_x(-90°),
$$

where $R_\mathcal{U}(cam) = P R^{desk}_{cam} P$ is the calibrated
camera pose as Unity already renders it (the sensor body in the scene)
and $R_x(-90°)$ is constant. Therefore the receiver only creates a
static **PersonAnchor** node — the camera's transform composed with
$R_x(-90°)$ — and every per-frame Pipeline A quantity passes through
untouched. Correctness check: $M$ maps the person-space depth-gravity
seed onto scene gravity at exactly the calibrated seed-vs-wall angle
(5.03°) — two *independent* gravity estimates (Pipeline A's depth
plane, Pipeline B's plumb wall) agreeing through the anchor.

Joint angles transfer with the anchor **pre-multiplied**
(A2 §7): $R_{bone} = q_A\,R_{chain}\,C_{rest}$, and the rig root is
translated each frame so the hip bone lands on the anchored pelvis
point.

## 2. Independence — why agreement is evidence, not tautology

$$
\begin{array}{ccc}
\text{recording.bag} & \longrightarrow &
\underbrace{\text{depth + MediaPipe} \to \text{landmarks} \to \text{angles}}_{\text{Pipeline A}}\\[2pt]
& \longrightarrow &
\underbrace{\text{RGB + ArUco PnP} \to \text{marker poses} \to \text{world}}_{\text{Pipeline B}}\\[6pt]
& & \text{integration/ (read-only): compares and renders both}
\end{array}
$$

- **Different measurement physics**: A uses the stereo depth channel +
  a learned landmark detector; B uses the RGB channel + fiducial
  geometry. Their error mechanisms are unrelated.
- **No shared code, no shared data**: neither pipeline reads the
  other's outputs; even trivial helpers are duplicated rather than
  shared. The integration layer only *reads* both finished outputs;
  nothing flows back.
- **The only shared quantities** are the physical recording itself and
  the calibrated anchor $(M, t)$ used to express both in one frame —
  the minimum required for any comparison to exist.

Consequently, when the object track shadows the wrist track (§4), that
agreement is a genuine two-chain cross-validation: the probability that
two unrelated error mechanisms produce matching trajectories through a
fixed rigid transform is negligible. Nothing in either pipeline was
fitted to make them agree.

One caveat is inherited by every accuracy number: the anchor itself is
part of the measurement chain, so a calibration error appears as a
common-mode offset in the residuals. The independent-gravity check
(§1) bounds the anchor's orientation consistency at the ~5° seed
agreement level, and the residual floor (§6) bounds the combined
effect at ~1 cm.

## 3. Verification methodology (plot-first)

Standing process rule, earned the hard way: **always render the
computed data in Python and check it against physical reality before
streaming to Unity.** The incident that created the rule: the first
receiver implementation composed the anchor as the conjugation
$q_A R q_A^{-1} C_{rest}$ instead of the pre-multiplication
$q_A R C_{rest}$. Conjugation cancels the anchor's orientation out of
the applied pose — the rig rendered facing *away* from the desk with
its legs in the table — while **every positional check still passed**
(positions were mapped separately and correctly). The Python plot of
the raw data showed the person facing the sensor to a mean 4.5°, which
localized the bug to the Unity composition. Two structural lessons,
both now institutionalized:

1. Positional validation is blind to an entire class of orientation
   errors; validators must assert orientation-level facts (facing
   direction, verticality), not just positions.
2. The pre-Unity plot stage (`plot_integrated_scene.py`) is a
   permanent part of the pipeline, and Pipeline B's wrong-lobe episode
   (B1 §4) independently confirms the pattern: rendering physical
   consistency finds what per-column statistics miss.

The validator (`validate_integration.py`, 20 checks) covers: anchor
math ($M \in SO(3)$, factorization, gravity agreement), stream
integrity (899 frames, filtered-object honesty < 15 mm from raw
detections), physical plausibility (pelvis at desk-working height,
0.34–0.60 m from the object; person faces the sensor mean 4.5°, p95
13°; pelvis clears the desk's data-driven far edge by ≥ 22.9 cm),
Unity application exactness (received pelvis = sent to float32;
logged hip = anchor·pelvis recomputed offline to **0.0007 mm**;
object log = world CSV to 0.0006 mm), and the carried-object
consistency below. The exactness chain verifies the *implementation*;
it is deliberately distinct from measurement accuracy (§6) — 0.0007 mm
says the transform is applied correctly, not that the person is
measured that well.

## 4. Carried-object consistency

Physical premise: the cube has no actuator — it moves only when a hand
moves it. So on every frame where the object is in motion, its
trajectory must shadow a wrist. Motion gate: displacement > 3 cm over
a 7-frame (0.23 s) window. On in-motion frames:

- median distance from marker center to the **nearest wrist**:
  **15.0 cm** (p95 17.4 cm) — within grasp; the offset is real
  geometry, not error (the marker sits on the box face, the landmark
  is the wrist joint — decomposed in §5);
- pooled velocity Pearson correlation with that wrist: **r = 0.842**;
- mean velocity direction cosine: **0.86**.

This ties B's object track to A's wrist track through the calibrated
anchor alone.

## 5. Offset decoupling — the grip vector

"Is the object–wrist offset constant?" is a **frame question**. In the
world frame, no: the offset's horizontal direction sweeps ±178° as the
person walks and turns the box — only its length is roughly constant.
In the object's own frame, yes: expressing the wrist as seen from the
marker's axes,

$$
d(t) = R_{obj}(t)^{\mathsf T}\bigl(w(t) - m(t)\bigr),
$$

($w$ = wrist, $m$ = marker center, $R_{obj}$ = object orientation) is
constant per **holding hand** — the world-frame "wandering" is exactly
one fixed vector co-rotating with the box.

Frames are conditioned before fitting: the box is parked on the desk
for $t \approx$ 13.5–23 s (no object–hand relationship exists), and
carried vs resting is unambiguous in the object's height above the
tabletop (resting: marker at half a cube edge, 3.5 cm; carried:
15–25 cm). On carried frames the nearest wrist defines the holding
hand, and each hand's grip vector is fitted separately as
$\bar d_{hand} = \operatorname{mean}\, d(t)$:

| holding hand | frames | $\bar d$ (x, normal, z) cm | std (cm) |
|---|---|---|---|
| left | 314 | (+3.8, −8.2, +8.6) | 3.8, 2.8, 2.5 |
| right | 249 | (−11.0, −10.6, +5.3) | **1.8, 0.9, 0.8** |

Each component has direct physical meaning: along the marker normal,
−3.5 cm is marker face → cube center (half the 70 mm edge) and the
rest is the far half of the box plus palm-to-wrist-joint (MediaPipe's
wrist is the joint, centimeters behind the palm); the in-plane
components are where each hand cups the box — different per hand,
which is why the model is one constant per holding hand, not one
global constant. The right-hand grip (wrist fully visible) is constant
to better than 2 cm per axis over 249 frames — direct evidence the
underlying rigid relationship is being measured, not fitted noise.

## 6. System accuracy (the headline result)

Decoupling = predicting the wrist from the object pose plus the
constant grip vector. The residual

$$
\varepsilon(t) = \bigl\| w(t) - \bigl(m(t) + R_{obj}(t)\,\bar d_{hand}\bigr) \bigr\|
$$

on carried, *measured* frames (marker detected, wrist raw; 563 frames):

| segment | median | p95 | note |
|---|---|---|---|
| right-holding | **1.0 cm** | 3.8 cm | wrist fully visible — the two-pipeline floor |
| left-holding | 4.6 cm | 8.9 cm | wrist half-occluded by the carried box |
| all carried | 3.3 cm | 7.3 cm | RMS 4.2 cm |

Velocity agreement: Pearson r = **0.842** while carried (0.273 over
the whole video — diluted by the resting stretch, where both
velocities are noise around zero).

Interpretation: two fully independent measurement chains, linked only
through the calibrated anchor, agree on a moving point's trajectory to
**~1 cm when sight lines are clean** and ~4–5 cm when the carried box
occludes the wrist. That is the ground-truth quality of the integrated
reconstruction — and simultaneously an in-situ accuracy statement for
Pipeline A's wrist track, graded against Pipeline B.

## 7. Reproduce

```bash
cd integration
python plot_integrated_scene.py            # ALWAYS first (plot-first rule)
python send_integrated_scene.py --dump-csv output/integrated_stream.csv
python validate_integration.py --stem recording_20260224_083945   # 20/20
python analyze_object_offset.py            # §5-§6 numbers + figure
```

Pinned artifacts: `integration/dataset/` (stream CSV, Unity logs,
validator output, offset analysis figure + stats, demo video).

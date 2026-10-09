# D1. Limitations — with mathematical justification

Every limitation below follows the same schema: **statement → why
(math) → measured evidence → mitigation and residual impact.** The
derivations marked ✓ were verified numerically
(scratchpad script; the amplification laws reproduce to 3 significant
figures).

## 1. Shoulder twist is ill-conditioned near a straight elbow

**Statement.** The dominant per-frame noise in the solved angles is
shoulder twist $\theta_\tau$, and it degrades as the elbow straightens.

**Math.** Twist is observable only through the forearm's component
perpendicular to the arm axis (A2 §4.4). At elbow flexion $e_y$, a
unit forearm's perpendicular component has magnitude $|\sin e_y|$.
Transverse angular noise $\delta$ on the measured forearm direction
(i.e. wrist position noise $\approx \delta \cdot L_{fa}$) perturbs the
decoded twist by

$$
\delta_\tau \;\approx\; \frac{\delta}{|\sin e_y|},
$$

since the noise displaces the tip of a lever whose twist-sensitive
radius is $|\sin e_y|$. ✓ Verified numerically: amplification 1.41× at
$e_y = 45°$, 4.13× at 14°, 11.3× at 5° — matching $1/|\sin e_y|$ to
three figures. At $e_y = 0$ (straight elbow) twist is exactly
unobservable — a property of any 3-landmark arm, not of this solver.

**Evidence.** The real recording shows raw twist jumps up to 65° at
$e_y \approx -14°$. Inverting the law: $65° \times \sin 14° \approx
16°$ of implied forearm-direction noise, which the measured raw wrist
spikes (up to 54 mm on a 0.23 m forearm ≈ 13°) account for. The 3 Hz
filter collapses these jumps 10–30×, confirming they are input noise
amplified by the conditioning, not solver error.

**Mitigation / residual.** The filter (A1 §3.3) removes the broadband
part; the solver flags exact unobservability
($\|f'_\perp\| < 10^{-6}\|f\|$) and holds the last valid twist (A3 §2).
Residual: twist quality is intrinsically posture-dependent; any
downstream use of $\theta_\tau$ near-straight elbows inherits the
amplification.

## 2. Only 4 rotational DOF per arm are observable ($e_z \equiv 0$)

**Statement.** The model cannot separate elbow out-of-plane swing from
shoulder twist, and cannot see forearm pronation or any hand DOF.

**Math.** Three landmarks per arm give two segment directions; each
unit direction carries 2 DOF, so the arm contributes exactly **4**
observable rotational DOF beyond the parent frame. The solve extracts
exactly 4 non-redundant angles $(\theta_y, \theta_z, \theta_\tau, e_y)$,
and $e_z \equiv 0$ *identically* because the twist definition already
rotates the flexion plane into $x$–$z$ (A2 §5.2). Anything beyond 4
DOF (pronation, wrist, fingers) is invisible in principle, not merely
noisy.

**Evidence.** A pose synthesized with $e_z = 30°$ decodes as
$\theta_\tau = -30°, e_z = 0$ with the recomposed forearm direction
identical to $5.6 \times 10^{-17}$ — the same physical geometry, one
convention of attribution.

**Mitigation / residual.** None needed for reconstruction — segment
directions are reproduced exactly. The residual is *interpretive*: the
"elbow carry angle" of clinical terminology is absorbed into shoulder
twist, so angle values are convention-dependent even though the
geometry is not. More landmarks (hand) would be required to extend the
DOF count.

## 3. Euler extraction degrades near gimbal lock ($x \to \pm 90°$)

**Statement.** ZXY Euler angles (the project's interchange format)
lose precision when the pitch approaches ±90°.

**Math.** The extraction $y = \mathrm{atan2}(m_{02}, m_{22})$,
$z = \mathrm{atan2}(m_{10}, m_{11})$ divides through $\cos x$
(A2 §3.2): each argument is a product with $c_x$, so the sensitivity
of $y$ and $z$ to matrix perturbations grows as $1/\cos x$, diverging
at the lock, where only $y \mp z$ is observable. ✓ Verified: perturbing
$R$ by $10^{-9}$ rad multiplies the extracted-angle error by ~34 at
$x = 89°$ and ~345 at $x = 89.9°$ ($\propto 1/\cos x$).

**Evidence.** The carried box reaches $x = -89.9°$; its Euler
round-trip error there is $1.3\times10^{-6}$° while the underlying
matrices still match to $10^{-14}$.

**Mitigation / residual.** All computation and validation are done on
matrices (machine precision throughout); Euler appears only at the
Unity interface, and exactness checks on Euler use a $10^{-5}$°
tolerance near the lock. Residual: none in practice — the torso
never approaches $x = \pm90°$ in the workspace, and the object's Euler
is display-only.

## 4. Depth noise sets the landmark noise floor

**Statement.** Pipeline A's per-frame precision is limited by the
depth sensor, not by MediaPipe tracking or by the solver.

**Math.** Stereo depth error grows quadratically with range,
$\sigma_z = \frac{z^2}{f\,b}\,\sigma_d$ (focal length $f$, baseline
$b$, disparity precision $\sigma_d$) — at $z \approx 1$–2 m this is
millimeters. Position noise maps to segment-direction noise as

$$
\sigma_\theta \approx \frac{\sigma_{pos}}{L}
$$

for segment length $L$: ✓ 5–10 mm on a 0.23 m forearm ≈ 1.2–2.5°, on a
0.28 m upper arm ≈ 1.0–2.0° — before the conditioning amplifications
of §1 and §3 apply on top.

**Evidence.** Measured raw landmark jitter is 5–10 mm median
frame-to-frame with hip spikes to 54 mm; hips and shoulders (bulky,
low-contrast, often near clutter) are noisier than wrists — the
signature of depth noise, not tracking noise. The solver reconstructs
raw and filtered data equally exactly ($10^{-14}$°), isolating all
jitter to the input. (A reference implementation storing landmarks as
float16 adds a ~1 mm quantization floor at 1.7 m; this pipeline stores
float64, so quantization is negligible.)

**Mitigation / residual.** 5×5 median depth sampling (A1 §1.1), the
3 Hz zero-phase filter (shake 10.2 → 1.9 mm). Residual: the ~1–2 mm
smoothed noise floor propagates to ~0.5° segment noise and contributes
to the 1 cm clean-visibility residual of the system evaluation (C1 §6).

## 5. Small-fiducial pose limits (Pipeline B)

Three distinct mechanisms, all functions of marker subtended size:

**(a) Lever-arm amplification of anchor orientation error.** A world
anchored to a marker inherits its orientation error $\delta\theta$
amplified by distance: a point at range $d$ from the anchor moves by
$d\,\delta\theta$. ✓ The measured desk-marker orientation drift
(0.07° → 0.69° over 30 s as lighting changes; position static to
1.1 mm) maps through the 2.8 m wall lever arm to ≈ 34 mm. *Mitigation:*
calibrate-once — the anchor is frozen as the chordal mean of the first
10 frames, making the world frame immune to session drift (B1 §5).
*Residual:* the frozen anchor is only as good as its calibration
window (0.19° desk spread ⇒ ≲ 9 mm at the wall).

**(b) Two-lobe degeneracy at small subtended angle.** The planar-pose
lobes (B1 §3) are mirror interpretations of the plane's tilt about the
viewing ray; their separation is $\approx 2\times$ the effective tilt,
and their reprojection difference shrinks with the perspective signal
— i.e. with subtended size. At 32 px (150 mm at 3.07 m) the wall's
lobes sit only ~23° apart, and reprojection error becomes a **biased**
discriminator: it chose the anti-plumb lobe on 815/837 frames, with
error ratios up to 2.18 — overlapping the 2.15–3.9 range where
well-conditioned markers are *genuinely* decisive. **Consequence
(proved by that overlap): no reprojection-ratio threshold can separate
the reliable from the unreliable case; the discriminator itself must
switch on lobe separation.** *Mitigation:* the ≥ 40° separation policy
with outlier-gated continuity + gravity seeding for the degenerate
case (B1 §4). *Residual:* wall pose is cross-check grade (p95 2.4°
orientation at the high camera), never used as ground truth — ground
truth lives near the desk (sub-mm, sub-0.2°) where the object moves.

**(c) Monocular range noise.** PnP infers range from apparent size:
$\sigma_z \approx z\,\frac{\sigma_{px}}{px_{marker}}$ — ≈ 28 mm for
0.3 px corner noise on a 32 px marker at 3 m. Confirmed by the
independent depth cross-check (PnP vs depth-median z within 5% of
range at all three markers).

## 6. Occlusion holds trade error for honesty

**Statement.** During a blocked-landmark interval, held joints carry a
bounded, *declared* error.

**Math.** A held angle differs from truth by the integral of the true
joint velocity over the hold:
$|\Delta\theta| \le \int_{t_0}^{t_0+T} |\dot\theta(t)|\,dt \le
\dot\theta_{max} T$. Holding in angle space keeps bone lengths exact
and the pose on the reachable manifold, so this motion term is the
*entire* error — a held 3-D point would add geometric inconsistency on
top (A3 §2).

**Evidence.** In the masked-data validation, held-joint deviation
during 30–45-frame gaps was 1.4–7.8°, exactly equal to the true motion
that occurred while blocked; live joints stayed exact (0.0°) through
every scenario.

**Mitigation / residual.** Per-joint live masks propagate to the
stream, the renderer (red bones), and every analysis, so no consumer
can mistake held for measured. Residual: long occlusions of a fast
joint are simply lost motion — no algorithm can recover unobserved
DOF; the honest bound is the declared price.

## 7. The evaluation's own floor: marker-vs-grip offset

**Statement.** The object-based accuracy evaluation (C1) measures the
wrist *through* a grip model, whose stability bounds what the
evaluation can resolve.

**Math.** The residual $\varepsilon = \|w - (m + R_{obj}\bar d)\|$
(C1 §6) contains the true pipeline disagreement *plus* any violation
of the rigid-grip assumption $d(t) = \bar d$. The evaluation's floor
is therefore $\mathrm{std}(d)$ per holding hand.

**Evidence.** Right hand (wrist fully visible): $\mathrm{std}(\bar d)
< 2$ cm/axis, residual median 1.0 cm — the assumption holds and the
floor is low. Left hand: std 2.5–3.8 cm/axis (regrips at
$t \approx 23$ s plus the box occluding the wrist), residual median
4.6 cm. The left-hand number is thus an upper bound on pipeline error,
not a measurement of it.

**Mitigation / residual.** Per-hand fitting, carried-only frames,
conditioning on measured frames. Residual: a true per-frame
ground-truth of the wrist (e.g. a marker on the hand) would be needed
to push the evaluation below ~1 cm.

## 8. Workspace and model-scope limits

- **Self-occlusion asymmetry**: the person must face the sensor; the
  arm on the far side of a carried object is systematically
  half-occluded — visible directly in the left/right residual split
  (4.6 vs 1.0 cm, §7) and in MediaPipe's inconstant left-arm segment
  lengths.
- **Rigid-torso assumption**: with 3 torso landmarks, pelvis and trunk
  are inseparable (A2 §2.3); trunk lean pitches the root frame. A
  shoulder-midpoint refinement is possible but was out of scope.
- **Untracked DOF**: legs, forearm pronation, wrist and finger pose
  (§2's DOF bound); the rig below the hips stays at rest.
- **Arm-vertical gimbal**: at $\theta_z = \pm90°$ the swing azimuth is
  undefined (A2 §4.3); the convention $\theta_y := 0$ keeps the decode
  well-defined, but near-vertical arms make $\theta_y$ noisy (atan2 of
  two vanishing quantities) — same structure as §3.
- **Single sensor**: FOV 55.6° × 43.1° and usable depth range bound
  the workspace; the person, desk, and wall must share one view.
- **Display rig proportions**: the FBX rig is display-scaled to
  1.70 m, but its bone ratios differ from the person's (forearm 1.6×);
  the FK hand lands a median 7–13 cm from the wrist landmark. This is
  a *rendering* limitation only — all quantitative results use raw
  landmark tracks, never the rig (OBJECT_OFFSET.md §6).

## 9. Methodological pitfalls (numerical statistics)

Documented because each silently corrupts an evaluation if ignored —
all three occurred and were caught in this project:

- **$\arccos$ near 0°**: $\frac{d}{du}\arccos u = -1/\sqrt{1-u^2}$
  diverges as $u \to 1$; in float64 the dot product's rounding
  ($u = 1 - \epsilon$) puts a resolution floor of
  $\sqrt{2\varepsilon_{mach}} \approx 2\times10^{-8}$ rad
  ($\approx 10^{-6}$°) under the result. ✓ Verified: at a true
  $5.7\times10^{-7}$° angle, arccos returns exactly 0 while
  $\mathrm{atan2}(\|a\times b\|, a\cdot b)$ is exact. All
  angle-between-vector checks use the atan2 form — otherwise
  machine-precision agreement *looks like* a $10^{-6}$° failure.
- **Yaw statistics at ±180°**: the person faces the camera, so yaw
  sits at the wrap point; the naive standard deviation explodes to
  ~176° when the true circular spread is ~5°. Yaw statistics are
  computed circularly (or on the unwrapped $y - 180°$).
- **Path length on unsmoothed tracks**: summed frame-to-frame distance
  integrates jitter into fake travel — 3.35 m raw vs 1.94 m smoothed
  for the carried cube (jitter of amplitude $\sigma$ per frame adds
  $\mathcal{O}(N\sigma)$ of spurious length). Travel is quoted from
  the smoothed track.

## 10. Offline scope

The profiled compute cost — 8.8 ms/frame end-to-end (MediaPipe GPU
inference 6.5 ms, depth-to-color align 2.2 ms) = a 113 fps ceiling —
shows a 30 fps real-time budget is met with ~4× headroom. But the
zero-phase filter (A1 §3.3) and the Savitzky–Golay object smoothing
(B1 §8) are non-causal by construction: a real-time variant must
substitute causal filters and accept their lag (the One-Euro
candidate trails genuine motion by ~28 mm at these speeds). Latency,
synchronization, and drop handling are untested. All claims in this
work are therefore **offline** claims; real-time is feasibility-shown,
not demonstrated.

## Reproduce

```bash
python thesis/check_limits.py   # twist amplification, gimbal conditioning,
                                # lever arm, angle-noise propagation, arccos floor
```

All measured numbers trace to the pinned artifacts named in chapters
A1–C1.

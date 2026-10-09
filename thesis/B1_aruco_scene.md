# B1. Pipeline B — ArUco scene reconstruction (ground truth)

Marker-based reconstruction of the fixed scene (wall, desk, camera) and
the moving object, anchored to the desk marker so the result is
identical wherever the camera stands. Fully independent of Pipeline A:
no shared code (the small Unity-Euler helpers are deliberately
duplicated in `aruco/frames.py`), no shared data — the two pipelines
meet only in the read-only integration layer (C1 §2). Rotations are
matrices + Unity ZXY Euler throughout; OpenCV's Rodrigues vector is
converted to a matrix immediately on receipt.

Implementation: `aruco/extract_aruco_poses.py`,
`aruco/calibrate_scene.py`, `aruco/filter_object_track.py`,
`aruco/send_scene_poses.py`, `aruco/validate_aruco.py`.

## 1. Scene design

| id | role | size | behavior |
|---|---|---|---|
| 0 | wall | 150 mm | static, **plumb** → gravity reference |
| 2 | desk | 50 mm | static, **world anchor** |
| 1 | object | 50 mm | on one face of a 70 mm cube, carried |

Three design decisions exploit the scene's structure:

1. **Calibrate-once**: the scene is fixed, so the static markers are
   averaged over the first 10 detections and frozen; only the object is
   streamed per frame. This is not merely a resource saving — it is
   what immunizes the world frame against the desk marker's session
   drift (§5.1).
2. **Desk anchoring**: everything (wall, object, and the camera itself)
   is expressed in the desk marker's frame $\mathcal{W}$, so the
   reconstruction is invariant to camera placement; the camera pose
   falls out for free as $T^{desk}_{cam} = (T^{cam}_{desk})^{-1}$.
3. **One physical assumption**: the wall is plumb. Everything else is
   measured. The wall marker's in-plane up axis defines gravity (§6),
   making the reconstructed wall exactly vertical and the desk top
   exactly horizontal *by construction*.

## 2. Detection and subpixel corners

`cv2.aruco.ArucoDetector` on DICT_5X5_50 with
**CORNER_REFINE_APRILTAG**. With the default (no refinement) corner
coordinates lock to integer pixels, which produces a diagnostic trap:
the close desk marker showed **0.00 mm frame-to-frame scatter** — false
stability (the detector re-snapping to identical pixels), not accuracy.
AprilTag subpixel refinement reveals the true scatter (desk 0.4 mm /
0.17°) and improves the far wall's position from 37 to 7 mm. Missing
markers write empty CSV cells (honest gaps, as in Pipeline A), and
`m{id}_depth_z` records a 5×5 median depth at the marker center as an
independent cross-check of the PnP range (§8).

## 3. Planar pose (IPPE) and the two-lobe ambiguity

For a marker of side $L$, the four object-frame corners
$X_i = (\pm L/2, \pm L/2, 0)$ and their detected pixels $x_i$ define
the planar PnP problem

$$
(R, t) = \arg\min_{R \in SO(3),\, t} \sum_{i=1}^{4}
\bigl\| \pi\!\left(K (R X_i + t)\right) - x_i \bigr\|^2,
\qquad \pi([a,b,c]^{\mathsf T}) = [a/c,\ b/c]^{\mathsf T},
$$

solved by `solvePnPGeneric(IPPE_SQUARE)`.

**Why there are two solutions.** All four $X_i$ lie in the plane
$z = 0$, so the image observation constrains only the homography
$H \simeq K [r_1\ r_2\ t]$ (first two columns of $R$ and $t$, up to
scale). Under perspective projection a planar patch viewed near
fronto-parallel admits two pose interpretations — tilted "toward" or
"away" by the same amount, the plane normal mirrored about the viewing
ray — that reproject almost identically; the finite difference between
them shrinks as the perspective cues shrink (small subtended angle,
small tilt). IPPE returns both local minima ("lobes") with their
reprojection errors. The angular separation between the lobes is the
conditioning signal: well-separated lobes mean the perspective
information is strong; near-coincident lobes mean the data genuinely
almost cannot tell the two apart.

## 4. Lobe disambiguation — the separation policy

Measured lobe separations: desk 64°, object 62° (50 mm markers at
close range) — but wall only ~23° (150 mm at 3.07 m ≈ 32 px). The
policy switches on separation, not on reprojection ratio:

- **Separation ≥ 40°** (desk, object): geometry is well-conditioned and
  the reprojection ratio is decisive (measured ratios 2.15–3.9) → take
  the lower-error lobe.
- **Separation < 40°** (wall): reprojection error is not merely noisy
  but **systematically biased** — on 815 of 837 wall detections it
  preferred the anti-plumb (physically wrong) lobe, with ratios up to
  2.18, *overlapping* the range where well-conditioned markers are
  genuinely decisive. Hence no ratio threshold can separate the cases;
  the discriminator must change, not the threshold. Here the lobe is
  chosen by **outlier-gated temporal continuity** (`LobeTracker`: the
  reference updates only when the new pose is within 30°, so one
  corrupted detection — e.g. the person clipping the marker edge —
  cannot poison subsequent frames; re-acquire after 5 consecutive
  misses), seeded on the first frame by plumbness against the
  depth-fit gravity seed (§6).

Result: wall orientation in the desk frame stable to p95 0.54°
(20260224) / 2.4° (20260328), and the chosen lobe agrees with the
independent depth-gravity seed to 4–5° — the wrong lobe would sit ~23°
away. A per-frame `m{id}_ambig` flag records how each pose was
resolved.

A rejected alternative is itself instructive: a depth-plane tiebreak
(compare each lobe's normal against the depth image's local plane) is
>30° biased for a 32 px quad at 3 m and *consistently* picked the same
wrong lobe — and it passed all per-column statistical validation. What
exposed it was building the real geometry from the poses: the wall
landed in the desk plane. Physical-consistency rendering finds bug
classes that per-column statistics miss (C1 §3).

## 5. Static calibration

### 5.1 Averaging rotations: the chordal mean

The first 10 detections of each static marker are averaged —
translation by the arithmetic mean, rotation by the **chordal mean**:
the element-wise mean matrix $\bar A = \frac{1}{N}\sum_i R_i$ is
generally not a rotation, so it is projected back onto $SO(3)$:

$$
R^* = \arg\min_{R \in SO(3)} \sum_{i=1}^{N} \|R - R_i\|_F^2
    = \arg\max_{R \in SO(3)} \operatorname{tr}(R^{\mathsf T} \bar A).
$$

(The expansion $\|R - R_i\|_F^2 = 6 - 2\operatorname{tr}(R^{\mathsf T} R_i)$
turns the sum of squared Frobenius distances into a single trace
against $\bar A$.) With the SVD $\bar A = U \Sigma V^{\mathsf T}$, the
maximizer over $SO(3)$ is the orthogonal Procrustes solution

$$
R^* = U\,\mathrm{diag}\bigl(1, 1, \det(UV^{\mathsf T})\bigr)\,V^{\mathsf T},
$$

the determinant correction guarding against a reflection. For the
sub-degree spreads involved the chordal mean coincides with the
geodesic mean far below measurement noise (validated: 200 samples with
2° noise recover a known rotation to 0.09°) — and it never leaves
matrix representation, in keeping with the project's rotation policy.

Measured stability over the calibration window: desk 0.43 mm / 0.19°;
wall 6.7 mm / 1.5° (32 px marker).

**Why freeze the anchor at all**: over the 30 s session the desk
marker's *position* is static to p95 1.1 mm but its *orientation*
drifts 0.07° → 0.69° (illumination changes as the person moves).
Through a lever arm $d$, an anchor orientation error $\delta\theta$
displaces reconstructed points by $d\,\delta\theta$ — at the wall
($d = 2.8$ m), 0.7° ≈ 34 mm. The frozen chordal-mean anchor keeps the
world frame and the object stream immune to that drift (D1 §5).

### 5.2 Derived scene quantities

The calibration also measures: the desk-stand tilt vs gravity (31.8°
tilted stand / 4.75° flat card), the world origin's height above the
depth-fit tabletop plane (32 mm / −1 mm), the sensor FOV from the color
intrinsics (55.6° × 43.1°), and the **object cube size**: the marker is
centered on the cube's face and (in 20260328) the cube rests on the
desk, so

$$
\text{edge} = 2 \times (\text{marker-center height above the local tabletop}) = 70\ \text{mm},
$$

auto-calibrated once and passed to the carried-cube recording via
`--cube-size` (no resting reference exists there).

## 6. Gravity: wall-referenced, depth-seeded

The authoritative gravity is the calibrated wall marker's in-plane up
axis (the wall is plumb — the one asserted scene property; the averaged
wall orientation is good to ~1°). A depth-based tabletop plane fit
serves only as a **seed** (sign/lobe disambiguation, needs ~10°
accuracy): one plane robustly fitted to depth annuli around the desk
marker — inner exclusion 2.2× the marker edge, outer 4×, ±5 cm median
gate, iterative 15 mm → 8 mm refit — averaged over the first 10 frames
and frozen. The object marker's annulus joins the fit **only** when its
local plane agrees with the desk-only fit within 15°, i.e. when the box
actually rests on the desk; without that gate, the hand-held box's
annulus swept the person's body and bent "gravity" more than 60° toward
horizontal. Measured seed-vs-wall agreement: 4.11° / 5.03° on the two
recordings — comfortably inside the ~11° needed to pick the correct
wall lobe.

## 7. World anchoring and the Unity map

With $T^{cam}_{m}$ the pose of marker $m$ in the camera frame:

$$
T^{desk}_{cam} = (T^{cam}_{desk})^{-1}, \qquad
T^{desk}_{wall} = T^{desk}_{cam}\, T^{cam}_{wall}, \qquad
T^{desk}_{obj}(t) = T^{desk}_{cam}\, T^{cam}_{obj}(t),
$$

where $T^{cam}_{desk}$ is the *calibrated* (frozen) desk pose — desk
measurement noise never leaks into the object stream. World
$\mathcal{W}$ is right-handed with $z$ out of the desk marker's face;
Unity is left-handed $y$-up. The single swap

$$
P = \begin{bmatrix}1&0&0\\0&0&1\\0&1&0\end{bmatrix}, \qquad
p_\mathcal{U} = P\,p_\mathcal{W}, \qquad
R_\mathcal{U} = P\,R_\mathcal{W}\,P
$$

handles both the axis relabeling ($y \leftrightarrow z$) and the
handedness change at once: $P$ is a reflection ($\det P = -1$) and its
own inverse, and the conjugation $P R P$ keeps $\det(PRP) = +1$, so
$R_\mathcal{U} \in SO(3)$ (validated numerically on every stored
matrix). Unity Euler extraction then follows the ZXY convention
(A2 §3; identical math duplicated into `aruco/frames.py` — pipeline
independence forbids importing it). For display, the whole world is
re-leveled by $G$ = FromToRotation(gravity, $+y$) so measured gravity
is exactly scene-down.

## 8. The object-track filter

Offline stage between the extractor and any consumer; the raw CSV is
never modified. The object marker is hand-covered on 22 frames of the
evaluation recording (4 gaps, longest interior gap 7 frames), and raw
PnP jitter runs to 19 mm frame-to-frame. Steps:

1. **Hampel despike** on position (same statistic as A1 §3.1).
2. **Interior gap bridging** — position linearly over time; rotation
   along the $SO(3)$ **geodesic**. With
   $\Delta = R_a^{\mathsf T} R_b$ the relative rotation across the gap,
   the interpolant at fraction $s \in [0,1]$ is

   $$
   R(s) = R_a \exp\!\bigl(s \log \Delta\bigr),
   $$

   where $\log$ maps a rotation to its axis–angle matrix
   $[\omega]_\times$ (angle $\theta = \arccos\frac{\operatorname{tr}\Delta - 1}{2}$,
   axis from the skew part $\frac{\Delta - \Delta^{\mathsf T}}{2\sin\theta}$)
   and $\exp$ is the Rodrigues formula

   $$
   \exp([\omega]_\times) = I + \sin\theta\, [\hat\omega]_\times
   + (1 - \cos\theta)\, [\hat\omega]_\times^2 .
   $$

   This is constant-angular-velocity interpolation — the matrix
   equivalent of slerp, with no quaternions involved. Boundary gaps
   hold the nearest valid pose.
3. **Smoothing** — Savitzky–Golay on position (window 9, order 2): each
   output sample is the value of the least-squares quadratic fitted to
   its 9-frame neighborhood, $\min_c \sum_{j=-4}^{4} (x_{i+j} - \sum_k c_k j^k)^2$
   — polynomial smoothing that preserves peaks and derivatives better
   than a moving average. Rotation: rolling **chordal mean** (window 5,
   §5.1) — the same $SO(3)$ projection applied as a moving filter.

Honesty contract: the `detected` flag is preserved unchanged (bridged
frames stream with `live=0`, red-tinted downstream), and the filter is
asserted to move *measured* frames by less than raw PnP jitter —
measured median 1.2 mm, max 11.6 mm, asserted < 15 mm in the
integration validator. Effect on the evaluation recording: frame-step
p95 10 → 4.9 mm, and the hold-last re-acquire pops (up to 2.2 cm /
3.4°) are gone.

## 9. Validation — 21/21 on both recordings

1. **Coverage**: desk 899/899 (both recordings); object 899/899 /
   877/899 (carried — hand covers the marker); wall 837/899 with 834
   near-degenerate frames continuity-resolved, 3 clear, 0 unresolved.
2. **Reprojection**: mean 0.20 px (wall), 0.42 px (desk), 0.08 px
   (object).
3. **Camera invariance** (the anchoring test): the wall's pose
   recomputed in the desk frame independently at every frame vs the
   frozen calibration — rotation p95 2.4°, position p95 28 mm,
   decomposed into ~11 mm along the camera→wall ray (monocular scale
   noise $\approx z\,\Delta px / px_{marker}$) and ~27 mm lateral,
   the lateral part explained by the measured desk-anchor drift times
   the 2.8 m lever arm — the bound is *derived* from the measured
   drift, not hard-coded.
4. **Depth cross-check**: PnP range vs the independent 5×5 depth
   median: +9 mm @ 3.07 m, +13 mm @ 0.65 m, −4 mm @ 1.02 m — all
   within 5% of range, confirming the marker size configuration (a
   wrong size would scale $z$ proportionally, since PnP range is
   inferred from apparent size).
5. **Math checks**: chordal mean recovers known rotations; every stored
   matrix is $SO(3)$ to $10^{-9}$ with exact Euler round-trip; the
   world CSV reproduces from raw + calibration to $10^{-16}$ m.

Unity end-to-end: applied poses match the world CSV to 0.0006 mm
(float32); wall slab 0.0000° off vertical and desk top 0.0000° off
horizontal (by construction under wall-referenced gravity); the cube
rests on the measured desk surface within 4.2 mm.

A cross-recording observation with design value: the desk-edge camera
(20260224) beats the high camera (20260328) everywhere — wall
invariance rot p95 0.54° vs 2.4°, desk drift p95 0.088° vs 0.82° —
**camera placement matters more than marker size** at these scales.

## 10. Reproduce

```bash
cd aruco
python extract_aruco_poses.py --bag ../Video/recording_20260224_083945.bag
python calibrate_scene.py --stem recording_20260224_083945 --cube-size 0.070
python filter_object_track.py --csv output/recording_20260224_083945_object_world.csv --plot
python validate_aruco.py --stem recording_20260224_083945   # 21/21
```

Pinned artifacts: `aruco/dataset/` (CSVs, filter QC, validator output,
Unity video/still).

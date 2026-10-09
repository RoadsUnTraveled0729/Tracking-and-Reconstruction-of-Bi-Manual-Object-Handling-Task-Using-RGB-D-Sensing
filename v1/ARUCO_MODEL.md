# Pipeline B — ArUco scene reconstruction (ground truth)

Marker-based reconstruction of the fixed scene (wall + desk) and the moving
object, anchored to the desk marker so the result is identical wherever the
depth camera is placed. Fully independent of Pipeline A (no shared code;
`aruco/frames.py` deliberately duplicates the tiny Unity-Euler helpers).
Rotation representation: matrices + Unity ZXY-applied Euler only —
quaternions appear nowhere (rotation averaging uses the chordal matrix
mean, §3; OpenCV's Rodrigues rvec is converted to a matrix immediately).

Verified on two recordings (899 frames, 640x480 each):
`recording_20260224_083945.bag` (ACTIVE calibration — object carried by
the person, desk card flat, camera at the desk edge) and
`recording_20260328_021733.bag` (object untouched, desk card on its
tilted stand, camera high). The evaluation-stage integration with
Pipeline A (person + real scene in one Unity world) is documented
separately in `INTEGRATION.md`.

## 1. Scene and design

| id | role | size (user-confirmed) | behavior | detections |
|---|---|---|---|---|
| 0 | wall | 150 mm | static | 837/899 (dropouts: person crossing) |
| 2 | desk | 50 mm | static, **world anchor** | 899/899 |
| 1 | object | 50 mm | moving | 899/899 |

Design (user's, 2026-07-19):
1. The scene is fixed → the static markers are calibrated ONCE from the
   first 10 detections and sent to Unity once (resource saving).
2. The object moves → its pose is streamed every frame.
3. Camera-placement invariance: everything (wall, object, and the camera
   itself) is expressed in the desk marker's own frame, so the
   reconstruction does not depend on where the camera stands. The camera's
   pose falls out for free as `T_desk_cam = T_cam_desk⁻¹`.

Physical scene properties (user-asserted, exploited by the pipeline):
the WALL is plumb — its marker's in-plane up axis defines gravity (§2.1)
and makes the reconstructed wall exactly vertical by construction. The
desk marker may sit on a stand tilted toward the camera (intentional:
less foreshortening = more precise corners; 31.8° in 20260328, flat
4.75° in 20260224). World "up" (desk z) is therefore NOT gravity; the
Unity build re-levels the whole world from the wall-referenced gravity.
The object is a cardboard cube (edge 70 mm, §3): carried by the person
in 20260224 (3.35 m of travel), untouched in 20260328 (~6 mm range).

## 2. Detection and per-marker pose (`aruco/extract_aruco_poses.py`)

- `cv2.aruco.ArucoDetector`, DICT_5X5_50, **CORNER_REFINE_APRILTAG**.
  With the default (no refinement) corners lock to integer pixels: the
  close desk marker showed 0.00 mm scatter over 10 frames — *false*
  stability. AprilTag refinement reveals the true subpixel scatter
  (desk 0.4 mm / 0.17°) and improves the wall position 37 → 7 mm.
- Pose per marker: `solvePnPGeneric(IPPE_SQUARE)` on the 4 corners with
  the known side length → full 6-DOF `(R, t)` in the camera frame.
- **Planar two-solution ambiguity — lobe-separation policy**: a square
  seen near fronto-parallel has two IPPE solutions ("lobes"). The
  *separation between the lobes* decides which signal is trustworthy:
  - lobes ≥ 40° apart (desk 64°, object 62°): the geometry is
    well-conditioned and reprojection error is decisive (ratios 2.15–3.9)
    → take the best-reprojection solution.
  - lobes < 40° apart (wall: ~23°, 150 mm at 3 m ≈ 32 px): reprojection
    is not just noisy but **systematically biased** — it preferred the
    anti-plumb (physically wrong) lobe on 815/837 frames with ratios up
    to 2.18, overlapping the range where well-conditioned markers are
    genuinely decisive, so NO ratio threshold separates the cases. Here
    the pose is chosen by continuity against an outlier-gated reference
    (`LobeTracker`: reference updates only within 30°, so one corrupted
    detection cannot poison the following frames; re-acquire after 5
    consecutive misses), seeded on the first frame by plumbness of the
    marker's y axis against the depth-fit gravity seed (§2.1).
  Result: the wall's orientation in the desk frame is stable to p95 2.4°
  (20260328) / 0.54° (20260224), and the chosen lobe agrees with the
  independent depth-gravity seed to 4–5° (the wrong lobe would sit ~23°
  away). Recorded per frame in `m{id}_ambig` (0 clear /
  1 gravity+continuity / 2 unresolved).
- Missing marker → empty CSV cells (honest gap, as in Pipeline A);
  `m{id}_depth_z` records the 5×5 median depth at the marker center as an
  independent cross-check of the PnP translation (§6.4).

### 2.1 Gravity: wall-referenced, depth-seeded

The AUTHORITATIVE gravity is the calibrated wall marker's in-plane up
axis: the wall is physically plumb (asserted scene property), and the
averaged wall orientation is good to ~1°. Consequence: the reconstructed
wall is exactly vertical and the desk top exactly horizontal by
construction (verified 0.0000° in the running scene).

The depth-based tabletop fit is demoted to a SEED (sign + lobe
disambiguation, needs only ~10° accuracy): ONE plane robustly fitted to
depth annuli around the desk marker (inner exclusion 2.2× the marker
edge, outer 4×, ±5 cm median gate, iterative 15 mm → 8 mm refit),
averaged over the first 10 frames and frozen. The object's annulus joins
the fit ONLY when its plane agrees with the desk-only fit within 15° —
i.e. when the box actually rests on the desk; in 20260224 the box is
hand-held from frame 0 and a naive two-annuli fit swept the person's
body, bending "gravity" 60°+ toward horizontal. Measured seed-vs-wall
agreement: 4.11° (20260328) / 5.03° (20260224), both comfortably inside
the 11° needed to pick the right wall lobe. The fit also yields the
tabletop points used for the desk height and the cube-size calibration
(§3).

## 3. Static calibration (`aruco/calibrate_scene.py`)

The first `--calib-frames 10` detections of each static marker are
averaged: translation by the mean, rotation by the **chordal mean** —
element-wise mean of the rotation matrices projected back onto SO(3) via
SVD, `R = U·diag(1,1,det(UVᵀ))·Vᵀ`. This is the rotation minimizing the
sum of squared Frobenius distances to the samples; for the sub-degree
spreads here it coincides with the geodesic mean to well below measurement
noise (validated: 200 samples of 2° noise recover a known rotation to
0.09°), and it never leaves matrix representation.

Measured stability over the calibration window: desk 0.43 mm / 0.19° max,
wall 6.7 mm / 1.5° max (150 mm marker at 3.07 m ≈ 32 px).

The calibration also derives the real-scene geometry streamed to Unity:
wall-referenced gravity (§2.1) with its depth-seed agreement, the desk
stand tilt (31.8° / 4.75°), the world origin's height above the tabletop
plane (32 mm / −1 mm — the flat card lies ON the surface), the sensor
FOV from the color intrinsics (55.6° × 43.1°), and the **object cube
size**: the marker is centered on the cube's front face and the cube
rests on the desk, so edge = 2 × (marker-center height above the local
tabletop point) = **70 mm**, auto-calibrated on 20260328 and passed to
20260224 via `--cube-size` (same physical box, hand-held from frame 0
there so no resting reference exists).

## 4. World anchoring

With `T_cam_m` mapping marker-m points into the camera frame:

    T_desk_cam  = T_cam_desk⁻¹              (camera pose in the world)
    T_desk_wall = T_desk_cam · T_cam_wall   (wall, fixed, sent once)
    T_desk_obj(t) = T_desk_cam · T_cam_obj(t)   (object, per frame)

The object uses the *calibrated* `T_cam_desk`, not the per-frame desk
detection, so desk measurement noise/drift does not leak into the object
stream and the world frame stays truly fixed.

## 5. World → Unity mapping

World is right-handed with z out of the desk marker's face ("up"); Unity
is left-handed y-up. The swap `P = [[1,0,0],[0,0,1],[0,1,0]]` (its own
inverse) converts both at once:

    p_U = P · p_w        R_U = P · R_w · P

`R_U` stays SO(3) (validated), and Unity Euler follows the project's
ZXY-applied convention (KINEMATIC_MODEL.md §4, identical math duplicated
into `aruco/frames.py`).

## 6. Unity bridge (`aruco/send_scene_poses.py` → `ArucoSceneReceiver.cs`)

- **PSB3** `/dev/shm/aruco_scene`, 100 B `<I24f`, written ONCE: magic
  'PSB3' + desk/wall/camera × (Unity position xyz + Euler xyz) + gravity
  up (Unity axes, world-local) + origin height above the tabletop + object
  cube edge + sensor vertical FOV. (Supersedes the 76 B PSB1 of the
  axis-triad-only build.)
- **PSB2** `/dev/shm/aruco_object`, 44 B `<IIif3f3fH2x` seqlock: magic
  'PSB2', seq, frame, time, position, Euler, live flag. Frames without an
  object detection hold the last pose with live=0 (red-tinted cube) —
  the same held convention as Pipeline A's PSA5 mask.
- **Object-track filter** (`aruco/filter_object_track.py`, offline stage
  between the extractor and the senders; raw CSV never modified):
  Hampel despike → interior detection gaps bridged (position linearly,
  rotation along the SO(3) geodesic — matrices/axis-angle only) →
  Savitzky-Golay polynomial smoothing on position + rolling chordal-mean
  smoothing on rotation; boundary gaps hold the nearest pose. Writes
  `*_object_world_filtered.csv` with `detected` kept as the original
  honesty flag (bridged frames carry a usable pose but stay live=0
  downstream). On 20260224: frame-step p95 10 → 4.9 mm, measured frames
  moved a median 1.2 mm (max 11.6 mm, within PnP jitter); on 20260328:
  0.4 mm median. The senders default to the filtered CSV — hold-last
  re-acquire pops (up to 2.2 cm / 3.4°) are gone (OBJECT_OFFSET.md §0).
- The receiver self-bootstraps on play mode when `/dev/shm/aruco_scene`
  exists (no scene edit needed) and builds the REAL scene under a
  gravity-aligned `ArucoWorld` parent (rotated so the streamed gravity
  becomes scene up; stream poses are applied as local pose): a wall slab
  coplanar with the wall marker extended down to the floor, a horizontal
  desk top whose top surface is the depth-fit tabletop plane (sized
  between the desk marker and the object; legs + floor are decorative
  standard-height), the object as a cube of the calibrated edge with the
  marker plate on its front face, a small RealSense-like sensor body at
  the calibrated camera pose, and marker plates + labels at every marker
  pose. A second camera parented to the sensor renders the **sensor POV**
  (optical axis = mapped marker "up", calibrated vertical FOV, 4:3) as a
  picture-in-picture inset over the global view. Every applied stream
  frame is appended to `aruco/output/unity_aruco_log.csv`.
  Mapped marker-frame identities used throughout: marker x = `Vector3.right`,
  marker normal (z) = `Vector3.up`, marker y = `Vector3.forward`.

## 7. Validation (`aruco/validate_aruco.py --stem <recording>` — 21/21 PASS on BOTH recordings, pinned in `aruco/dataset/`)

Numbers below are 20260328 unless noted (20260224 is uniformly tighter —
see §8).

1. Coverage: desk 899/899 on both; object 899/899 (20260328) / 877/899
   (20260224 — the carrying hand covers the marker, held with live=0);
   wall 837/899 with 834 near-degenerate frames gravity/continuity-
   resolved, 3 clear, none unresolved.
2. Reprojection: mean 0.20 px (wall) / 0.42 px (desk) / 0.08 px (object).
3. **Camera-invariance**: the wall's pose recomputed in the desk frame
   independently at every frame (no calibration involved) vs the
   calibrated `T_desk_wall`: rotation p95 2.4°; position p95 28 mm,
   decomposed into 11 mm along the camera→wall ray (monocular scale noise
   ≈ z·Δpx/marker_px ≈ 28 mm at 3 m for 0.3 px) and 27 mm lateral. The
   lateral part is explained by the desk anchor's own orientation drift
   (below) times the 2.8 m lever arm, and is asserted against a bound
   *derived* from that measured drift, not hard-coded. The lobe choice is
   guarded by the seed-agreement check (< 11°, measured 4–5°): the wrong
   lobe would sit ~23° from the independent depth-gravity seed.
4. Depth cross-check: PnP z vs depth-median z bias +9 mm @ 3.07 m (wall),
   +13 mm @ 0.65 m (desk), −4 mm @ 1.02 m (object) — all within 5% of
   range, confirming the 150/50 mm size configuration (a wrong size would
   scale z proportionally).
5. Math: chordal mean recovers a known rotation (0.09° from 2° noise);
   every stored matrix SO(3) to 1e-9 with exact Euler round-trip; the
   object_world CSV reproduces from raw + calibration to 1e-16 m / 1e-14°.

Unity end-to-end (from `unity_aruco_log.csv`, 20260224 run): 898 unique
frames displayed per loop; applied position/Euler match the object_world
CSV to 0.0006 mm (float32 quantization), 21 hand-covered frames held
with the red tint. Real-scene geometry verified in the running scene:
wall slab 0.0000° off vertical and desk top 0.0000° off horizontal (both
by construction under the wall-referenced gravity), cube resting on the
desk surface. Demo video + still:
`aruco/dataset/unity_real_scene_224.mp4`, `real_scene_224_still.png`.

## 8. Measured scene properties (thesis-relevant)

- **Desk anchor drift**: position static to p95 1.1 mm over the full 30 s,
  but orientation drifts 0.07° → 0.69° (p95 0.82°) as the person moves and
  lighting changes — a single 50 mm marker's orientation is only good to
  ~0.8° over a session. Amplified by a lever arm (×2.8 m = 40 mm at the
  wall), this dominates far-point reconstruction error and justifies the
  calibrate-once design: the frozen anchor keeps the world frame and the
  object stream immune to that drift.
- **Wall marker at 3 m** (32 px): orientation noise p95 2.4°, range noise
  ~11 mm — monocular pose at this pixel size is cross-check grade, not
  ground-truth grade; ground truth quality lives near the desk (sub-mm /
  sub-0.2°) where the object actually moves. Its IPPE lobes are only 23°
  apart there, which makes reprojection error a *biased* discriminator
  (§2) — the single most instructive failure of this pipeline.
- **Scene geometry** (one assumption — the wall is plumb — everything
  else measured): desk marker stand tilt vs gravity 31.8° (20260328
  stand) / 4.75° (20260224 flat); depth-gravity seed agrees with the
  wall to 4–5°; world origin 32 mm / −1 mm above the tabletop plane;
  object cube edge 70 mm; sensor FOV 55.6° × 43.1°.
- **Camera placement matters more than marker size**: the same scene at
  the desk-edge camera position (20260224) beats the high camera
  (20260328) across the board — wall invariance rot p95 0.54° vs 2.4°,
  desk anchor drift p95 0.088° vs 0.82°, wall position spread p95 5.8 mm
  vs 28 mm.

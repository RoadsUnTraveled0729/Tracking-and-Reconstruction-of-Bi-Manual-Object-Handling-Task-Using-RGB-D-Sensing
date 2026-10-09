# System integration — person (Pipeline A) + scene (Pipeline B) in one world

Evaluation-stage integration: the MediaPipe-driven person and the
ArUco-anchored real scene (wall, desk, object cube, sensor) rendered in the
SAME desk-anchored Unity world, from the same recording. Pipelines A and B
stay fully independent; only this layer (`integration/`) reads both their
outputs. Rotation representation: matrices + Unity ZXY Euler throughout
(quaternions only as Unity-API intermediates).

Verified on `recording_20260224_083945.bag` (ACTIVE: the person CARRIES
the object cube — 1.94 m of smoothed object travel — which lets the
carried-object consistency check tie the two pipelines together, §4.6) and
previously on `recording_20260328_021733.bag` (seated person, object
untouched). The object-vs-hand offset, its decoupling, the resulting
system accuracy, and the rig proportion audit live in **OBJECT_OFFSET.md**.

## 1. The person→scene anchor (the only new math)

Pipeline A solves everything in "Unity-from-sensor" space: the camera
frame with y flipped, `q = diag(1,−1,1)·p_cam` (KINEMATIC_MODEL.md §3).
Pipeline B's world is the desk-marker frame, mapped to Unity by the y/z
swap `P` (ARUCO_MODEL.md §5). A person-space point therefore lands in the
scene as

    p_scene = M·q + P·t_desk_cam,     M = P·R_desk_cam·diag(1,−1,1)

`M` is a proper rotation (det = +1: the two axis flips cancel), and it
factors into transforms Unity already has:

    M = R_unity(camera) · Rx(−90°)

so the receiver just creates a **PersonAnchor** node at the calibrated
camera pose composed with a fixed `Rx(−90°)` — no per-frame re-mapping of
any Pipeline A quantity. Correctness check (validate_integration.py):
`M` maps the person-space depth-gravity seed to exactly the calibrated
seed-vs-wall angle from scene gravity (5.03° — two independent gravity
sources agreeing through the anchor).

Joint angles transfer untouched: bones are driven exactly like
`ArmAngleReceiver` with the anchor PRE-multiplied,

    R_bone = qA · R_chain · C_rest

where `C_rest` is the authored rest rotation captured at spawn (the rig
spawns unrotated, so its body axes coincide with scene axes; `qA` then
carries the whole person-space pose — including which way the person
faces — into the scene). The first implementation used the conjugation
`qA·R_chain·qA⁻¹·C_rest`, which cancels the camera orientation out of
the pose: the rig rendered NOT facing the desk while every positional
check still passed. It was caught by plotting the data in Python first
(`integration/plot_integrated_scene.py`): the raw data showed the person
facing the sensor to a mean 4.5°, so the bug had to be in the Unity
composition. That plot is now a standing pipeline stage — **always draw
the data in Python and check it against reality before sending it to
Unity** — and the facing + desk-clearance assertions moved into
`validate_integration.py` so the mistake cannot recur silently. The rig
root is translated each frame so the hip bone lands on the streamed
pelvis point (midpoint of the two hip landmarks) mapped through the
anchor.

## 2. Stream (`integration/send_integrated_scene.py`)

- `/dev/shm/aruco_scene` — **PSB3** (100 B), written once, reused verbatim
  from Pipeline B's sender: static poses + gravity + tabletop drop + cube
  size + sensor FOV.
- `/dev/shm/integrated_scene` — **PSI1** (108 B `<IIif3f13f3f3fHH`,
  seqlock): frame, time, pelvis (person space), the 13 PSA5 angles (root
  Euler + R/L shoulder swing-twist + R/L elbow), object position + Euler
  (PSB2 pose), person live mask (PSA5 bits), object live flag. Person and
  object ride in ONE packet, so they can never desynchronize.

Person angles come from the real Pipeline A chain
(`kinematics/occlusion.py` ChainFallbackSolver on the filtered landmark
CSV, regenerated with `--edge-fill 12` so warm-up-blocked joints don't
snap — OBJECT_OFFSET.md §0); object poses come verbatim from Pipeline B's
FILTERED world CSV (`aruco/filter_object_track.py`: gaps bridged,
Savitzky-Golay smoothed; `obj_live` = the original detection flag). Both
CSVs are from the same bag, so frames align 1:1 by construction.

## 3. Unity (`IntegratedSceneReceiver.cs`)

Subclasses `ArucoSceneReceiver` (same real-scene geometry, same PSB3/log
machinery) and adds: the PersonAnchor, rig bone driving with the
anchor-relative calibration, per-frame rig translation, PSA5-style red
held-joint markers, and a global "monitor" camera framing that keeps
wall + desk + object + sensor + person in view. The sensor-POV
picture-in-picture inset (calibrated FOV, 4:3) comes from the base class.
Bootstraps only when `/dev/shm/integrated_scene` exists (the standalone
Pipeline B receiver yields in that case); the standalone Pipeline A
receivers (PoseStream/RootAngle/ArmAngle) are disabled at start so nothing
fights over the bones.

## 4. Validation

Stage order: `plot_integrated_scene.py` FIRST (renders desk/wall/floor,
sensor pose, object + wrist + pelvis trajectories and the person's root
axes in the leveled desk world, and prints the sanity numbers — facing
angle, desk-edge clearance, wall verticality); only when the picture
matches reality does anything get streamed to Unity. Then
`validate_integration.py --stem <recording>` — 20/20 PASS:

1. Anchor math: `M` proper rotation; equals `R_unity(camera)·Rx(−90°)`;
   maps the person-space depth-gravity seed to the exact calibrated
   angle from scene gravity (5.03°, two independent gravity sources).
2. Stream integrity: 899 frames, strictly increasing, live object poses
   verbatim from the FILTERED world CSV (877 live, 22 hand-covered frames
   bridged/held with live=0), and the filter stage stays within raw PnP
   jitter on measured frames (< 15 mm — smoothing must not invent
   geometry).
3. Physical plausibility (nothing here is enforced by construction —
   the person and the scene come from different sensors/algorithms):
   pelvis at desk-working height (−3 cm..+32 cm of the tabletop plane,
   standing), 0.34–0.60 m from the object; the person FACES the sensor
   across the desk (root forward vs pelvis→sensor mean 4.5°, p95 13°);
   the pelvis clears the desk's data-driven far edge by ≥ +22.9 cm (no
   legs inside the table — the desk slab spans marker→object projection,
   not a fixed centered box).
4. Unity application: received pelvis = sent pelvis (float32, 5e−7 m);
   logged hip bone position reproduces `anchor.TransformPoint(pelvis)`
   recomputed offline from first principles (gravity alignment + floor
   drop + anchor pose) to **0.0007 mm** over 898/899 frames.
5. Unity object log matches the world CSV (0.0006 mm).
6. **Carried-object consistency** (the user's requirement that the
   object's trajectory match the wrists'): the object only moves because
   a hand moves it, so on every in-motion frame (displacement > 3 cm per
   0.23 s window) the object must shadow a wrist. Measured: median
   distance to the nearest wrist **15.0 cm** (p95 17.4 cm — within
   grasp; the marker sits on the box face, not in the palm — the full
   decomposition of this offset is OBJECT_OFFSET.md), pooled velocity
   Pearson correlation with that wrist **r = 0.84**, mean direction
   cosine **0.86**. This ties Pipeline B's object track to
   Pipeline A's wrist track — different sensors and algorithms, no
   shared code — through the calibrated anchor alone.

Visual cross-check: the PiP sensor view reproduces the real color
frame's layout (low desk-edge camera: desk in the lower half, the
person's torso above it, the carried cube at hand height)
(`integration/dataset/`).

## 5. Known limitations (by design, for the thesis)

- Legs are not tracked (MediaPipe landmarks 11–16, 23, 24 only): the rig
  below the hips stays in its rest pose; the decorative floor/desk legs
  exist for spatial context only. The desk slab's data-driven extent
  keeps it out of the standing spot (clearance asserted in validation).
- The character's proportions are the FBX rig's, not the person's; only
  the hip position and the solved joint angles are transferred. The FBX
  is authored ~2.2× human size, so the receiver display-scales it to a
  1.70 m person at spawn (uniform root scale — rotations and the angle
  transfer untouched; OBJECT_OFFSET.md §6). Post-scale the FK hands land
  a median 7–13 cm from the real wrist points; the remainder is the
  rig's non-uniform bone proportions (forearm 1.6× the person's). The
  wrist correlation check in §4.6 is computed on the raw landmark
  tracks, not the rig.
- The object cube's edge (70 mm) is calibrated on a recording where the
  box rests on the desk; a hand-held-only recording needs `--cube-size`.

# R5: does the Unity pose match the recorded video?

Internal verification, NOT thesis material. Recording R5
(recording_20260825_222315), offline v1 pipeline only.

## What the check is

The Unity scene already contains a virtual replica of the recording
camera: ArucoSceneReceiver builds a "SensorPOVCamera" at the
calibrated sensor pose with the calibrated vertical FOV (43.1 deg,
matching fy = 607.0 over 480 rows). Rendering that camera and putting
its output beside the bag's own color frame for the SAME stream frame
turns "does the reconstruction match reality" into a direct visual
question, with the calibration and the receiver composition in the
loop (unlike eval/inspect/check_v1_overlay.py, which deliberately
leaves Unity out).

Streamed data: the true v1 offline pipeline - filtered landmarks
-> unity_from_sensor -> ChainFallbackSolver -> 13 angles, pelvis from
the hip midpoint, object pose from the marker-size-corrected filtered
track, calibration scene_calibration_r5c.json. 2099 frames, 70 s.

## Unity ran unattended: PASS

No human pressed Play. Unity/Assets/Editor/EvalPlayBootstrap.cs (new)
enters play mode, opens Assets/Scenes/rig.unity, leaves play mode and
quits the editor on flag files under /tmp, and publishes the editor's
live state to /tmp/r5_autoplay_state so the driver waits on facts
rather than on sleeps. eval/unity_check/run_unity_capture.py starts
the sender first (IntegratedSceneReceiver self-spawns only if both
/dev/shm files exist at Play start and never re-maps), then launches
the editor and tears everything down. The MCP bridge was not needed.

Run: editor up at 20 s, play mode at ~25 s, 2098 of 2099 frames
captured in a single 70 s replay pass, editor quit clean. The one
missing frame is the last frame of the pass (2098), which the looping
sender wrapped past before the capture stopped.

## Pairing method and its exactness: PASS

Each PNG is named by the STREAM frame number, not by wall time.
EvalFrameDump.cs (edited) reads ArucoSceneReceiver.lastFrame - the
frame the receivers applied in Update - from LateUpdate, and writes
one PNG per distinct value. All Update()s run before any LateUpdate(),
so the rendered pose is exactly the pose that frame carried. On the
video side the bag's i-th color frame is row i of the landmark CSV,
whose `frame` column is that same number.

Independent confirmation that this is not an off-by-N (nothing in it
trusts the statement above): compare the orange object cube's centroid
in each Unity render against the cube centre projected from the pose
that frame streamed, using frame-to-frame displacements so the
standing bias between the two cancels.

    offset  n     median |dUnity - dStreamed| (px)
      -3    445      0.68
      -2    445      0.60
      -1    445      0.49
      +0    445      0.39   <-- minimum
      +1    445      0.46
      +2    444      0.56
      +3    443      0.68

Sharp, symmetric minimum at offset 0 over 445 frames of object motion.
A first attempt compared the cube centroid against the ArUco
detector's own marker pixel (m1_u/m1_v) and put the minimum at -2;
that was an artefact of the reference, not a lag - the cube centre
sits half an edge behind the marker, so the image offset between them
swings with the object's rotation. Projecting the MARKER centre from
the same streamed pose reproduces m1_u/m1_v to a median 0.15 px
(p95 0.74 px), so the projection chain itself is sound.

Frame numbers are HUD-stamped on both halves of every pair, and the
still at f01869 - the recording's fastest object motion, 5.0 px/frame,
where any lag would be visible - shows the Unity cube and the real box
in the same place.

## Numeric log check: 8 PASS, 0 FAIL

eval/unity_check/check_unity_log.py (full output in
eval/output/unity_check_r5/check_unity_log.txt).

Application is exact:
- logged pelvis == streamed pelvis, max 5.0e-07 m over 2098 frames
- logged object pose == streamed pose, max 5.6e-07 m / 8.7e-06 deg
- 2098/2099 frames applied; every PNG frame number is a frame Unity
  actually applied (0 orphans)
- hip bone lands on anchor.TransformPoint(pelvis) recomputed from the
  calibration alone: max 0.0007 mm

Rendered hands vs measured wrists, mapped back out of Unity's world
into the sensor frame and projected with the recording's own
intrinsics (640x480 image), bucketed by the E-014 failure mask:

    right hand / clean          median  48.5 px, p95  83.4 px (n=1250)
    right hand / arm_only       median  29.6 px, p95 100.1 px (n= 151)
    right hand / torso_only     median  44.5 px, p95  91.5 px (n= 603)
    left  hand / clean          median  23.9 px, p95  85.0 px (n=1234)
    left  hand / arm_only       median  31.9 px, p95  58.4 px (n=  57)
    left  hand / torso_only     median 155.9 px, p95 202.0 px (n= 456)

The rig is a fixed-proportion avatar scaled to 1.70 m and its hand
bone is not MediaPipe's wrist point, so a standing offset is expected
and says nothing about whether the render FOLLOWS the video. Removing
each hand's own median offset (right +31.4, -35.2 px; left -17.4,
-14.3 px) leaves the frame-to-frame disagreement: right median
19.6 px (p95 42.8), left median 10.0 px (p95 63.0). That is the
tracking quality; the rest is avatar geometry.

## Side-by-side verdict

The Unity pose matches the video pose outside the E-014 failure
windows, and departs from it inside them - the departures line up with
the mask windows frame for frame, not with the pairing.

Object: matches everywhere, in every still and across the whole video.
This is the strongest single result: the box in the render sits on the
box in the video at the pixel level, through calibration, world
mapping and the receiver.

Person, per still (eval/output/unity_check_r5/still_f*.png). E-014
failure windows of 15 frames or more, from
eval/output/recovery_r5/failure_mask.csv: torso 85-117, 133-150,
896-931, 956-1130, 1182-1544; arm_L 85-150, 1427-1668, 1777-1798;
arm_R 62-87, 114-133, 1775-1893.

Frames the failure detector calls clean:
- f01740 - the best case. The video has the box gripped in both hands
  at chest height; the rig has both hands together at chest height
  with the rendered cube between them, torso square to the sensor.
- f00300, f02020 - rig stands behind the desk facing the sensor with
  arms at its sides, as in the video; torso orientation and body
  placement agree.
- f00700, f01150 - torso and body placement agree and the rendered
  cube is on the real box, but the reaching hand stops 40-90 px short
  of the video's hand, i.e. the p95 tail of the clean-frame numbers
  above (avatar arm proportions plus solve error, not a lag).

Frames the detector flags:
- f00900, f01200 (torso): the reaching arm points the right way, but
  the torso is rolled well past the video's lean, so the rig is
  rendered in three-quarter view where the person faces the sensor.
- f01450 (torso + arm_L): torso rotated, and the arm that holds the
  box in the video is folded at the rig's belly instead.
- f01600 (arm_L): the box is correct in the air at image right; the
  rig's left arm never goes there.
- f01830 (arm_R, stream mask 113 - right arm held): the right arm
  hangs while the video's right hand holds the box up.
- f01869 (arm_R, fastest object motion): the held right-arm pose
  happens to coincide again - rig hand and rendered cube both on the
  real box.

Numerically the same story: the one large bucket is the left hand on
torso-failure frames, 155.9 px against 23.9 px on clean frames.

This is the known v1 baseline failure (E-011/E-014), reproduced end to
end in Unity rather than a new Unity-side defect - application is
exact to float32 and rig placement to 0.0007 mm, so nothing between
the solved angles and the screen is losing the pose.

## Limits

- v1/integration/validate_integration.py could not be run for R5: it
  is pinned to R1 (899 frames, v1/aruco/output/scene_calibration.json)
  and requires v1/aruco/output/<stem>_object_world_filtered.csv, while
  R5's authoritative object track is the marker-size-corrected one
  under eval/output/. It aborts on the missing file. v1/ is frozen and
  was not edited; check_unity_log.py covers that validator's checks 1,
  4 and 5 for R5. The R1 baseline
  v1/integration/output/integrated_stream.csv was temporarily swapped
  for the attempt and restored byte-identical (md5 verified); a copy
  is kept at eval/output/unity_check_r5/v1_output_backup/.
- The recording's principal point is 4 px right and 8 px below centre;
  the Unity camera is centred. Not corrected, and below the effects
  measured here.
- Held-joint markers (red spheres) are offset toward Camera.main, not
  toward the POV camera, so their position in the render is indicative
  only. The scene's TextMesh labels are hidden for the duration of the
  capture render (they sit on the marker nodes, and the desk node is a
  few cm from the sensor, so one label otherwise fills the frame).
- This run streamed the v1 solve (ChainFallbackSolver, no failure
  masking), which is what "offline v1 pipeline" means. The variants in
  eval/output/recovery_r5/ come off the same landmark CSV but a
  different solver - eval/failure/recovery_core.py runs
  RobustChainSolver, with failure-mask removal and object-derived
  wrists in the recovery variant - so they are not interchangeable
  with the v1 solve (their live masks agree with it on only 47 percent
  of frames). send_scene_r5.py --angles-csv streams them verbatim
  (verified byte-exact against the CSV) when that comparison is
  wanted; it was not run here.

## Artifacts

eval/output/unity_check_r5/ (gitignored, regenerable):
- side_by_side.mp4 - 2098 pairs, 1280x506, Unity POV left, bag color
  right, both halves HUD-stamped with the frame number
- still_f00300 / f00700 / f00900 / f01150 / f01200 / f01450 / f01600 /
  f01740 / f01830 / f01869 / f02020.png
- pairing_lag_scan.txt / .json - the off-by-N evidence
- check_unity_log.txt / .json - the numeric check
- integrated_stream.csv - exactly what was streamed
Raw Unity PNGs: /tmp/r5_frames (2098 x 640x480, 368 MB).

Code (all new except the first):
- Unity/Assets/Scripts/EvalFrameDump.cs - edited: SensorPOVCamera,
  stream-frame naming, /tmp/r5_* flags, label hiding
- Unity/Assets/Editor/EvalPlayBootstrap.cs - unattended play mode
- eval/unity_check/send_scene_r5.py - vendored copy of
  v1/integration/send_integrated_scene.py, stem-driven inputs plus
  --angles-csv
- eval/unity_check/run_unity_capture.py - the whole run, unattended
- eval/unity_check/side_by_side.py - pairing, video, stills, lag scan
- eval/unity_check/check_unity_log.py - numeric backstop

Regenerate:
    /home/luo/anaconda3/bin/python eval/unity_check/run_unity_capture.py
    /home/luo/anaconda3/bin/python eval/unity_check/side_by_side.py
    /home/luo/anaconda3/bin/python eval/unity_check/check_unity_log.py

## Update 2026-08-26 (later): rig fidelity fixes

User review of the side-by-side ("the rig's hand is not touching the
cube") led to three rig corrections in
Unity/Assets/Scripts/IntegratedSceneReceiver.cs, verified against the
streamed FK wrist through the reconstructed anchor transform:

1. Spawn-pose alignment: the rig spawns 8.2 deg (upper arms) /
   5.7 deg (forearms) away from the model T-pose, and the angle
   transfer composes streamed rotations with the spawn pose, so that
   deviation rode into every frame (it is the "standing avatar
   offset" the first version of this check subtracted). The arms are
   now rotated onto the exact rest axes at spawn before the rest
   capture.
2. Segment proportions: rig arms rescaled per bone to the subject's
   calibrated lengths (rig upper arm 15 percent short, forearm 17
   percent long), torso to the calibrated hip-to-mid-shoulder length
   (rig 5.6 cm long, which raised the shoulder anchors).
3. Held-joint spheres reduced 12 -> 4.5 cm; marker plates textured
   with the real DICT_5X5_50 patterns.

Result at the raised-hold pose f1620: rendered left hand vs the
streamed FK wrist 11.6 cm before, 4.3 cm after (within the hand
mesh's own span); at f700 the rendered fingers rest on the cube as
in the video. The sender additionally streams the display smoother
(E-018) and the repaired pelvis (E-011b).

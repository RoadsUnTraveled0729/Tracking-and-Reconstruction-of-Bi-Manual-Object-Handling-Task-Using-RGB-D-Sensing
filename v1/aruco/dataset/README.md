# Pipeline B verified dataset (2026-07-19, wall-referenced gravity)

ArUco scene reconstruction, desk-anchored, gravity = the plumb wall
marker's in-plane up (ARUCO_MODEL.md §2.1). TWO recordings are pinned,
both 899 frames, both `validate_aruco.py` 21/21 PASS:

- **recording_20260224_083945** (ACTIVE, `scene_calibration.json`):
  desk marker flat on the desk (stand tilt 4.75°), object cube CARRIED by
  the person (47 cm motion range, 877/899 detections — hand covers it on
  22 frames), camera at the desk edge. Best-conditioned camera position:
  wall camera-invariance rot p95 0.54°, desk anchor drift p95 0.088°.
- **recording_20260328_021733** (`scene_calibration_328.json`): desk
  marker on its intentionally tilted stand (31.8° — less foreshortening
  for the camera), object resting untouched, camera high looking down.
  Wall invariance rot p95 2.4° (150 mm marker at 3 m ≈ 32 px).

| File | What it is |
|---|---|
| `<stem>_aruco_raw.csv` / `.meta.json` | per-frame 6-DOF camera-frame poses (R + t + reproj + ambig + depth cross-check); meta carries the tabletop depth fit (gravity SEED + tabletop points). |
| `scene_calibration.json` / `scene_calibration_328.json` | chordal-mean static calibration + world/Unity poses + scene_geometry: gravity (wall-referenced), tabletop, stand tilt, seed agreement (5.03° / 4.11°), cube 70 mm, sensor FOV 55.6°×43.1°. |
| `<stem>_object_world.csv` | object per frame in the desk (world) frame + Unity position/Euler; reproduces from raw + calibration to 1e-16 m. |
| `recording_20260224..._object_world_filtered.csv` / `.meta.json` / `.qc.png` | filter_object_track.py stage (2026-07-23): detection gaps bridged (geodesic rotation), Savitzky-Golay smoothed (step p95 10→4.9 mm, measured frames moved ≤ 11.6 mm); the senders' default input (OBJECT_OFFSET.md §0). |
| `validate_aruco_output.txt` (224) / `validate_aruco_328_output.txt` | the 21 checks per recording. |
| `unity_aruco_log.csv` | Unity-side log of the 224 standalone run: 898 unique frames, match to 0.0006 mm (float32), 21 held (live=0) frames. |
| `unity_real_scene_224.mp4` / `real_scene_224_still.png` | Unity real-scene reconstruction of 224: wall slab EXACTLY vertical (0.0000° by construction), desk top exactly horizontal on the measured tabletop plane, 70 mm cube streaming live (carried), sensor body + calibrated-FOV sensor-POV PiP. |

Cube edge 70 mm: auto-calibrated on 328 (marker height above the local
tabletop point under wall-referenced gravity) and supplied to 224 via
`--cube-size 0.070` (same physical box, hand-held from frame 0 there).

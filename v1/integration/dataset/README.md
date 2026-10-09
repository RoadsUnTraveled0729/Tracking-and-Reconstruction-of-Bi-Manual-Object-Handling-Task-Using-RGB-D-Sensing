# Integration verified dataset (2026-07-23, recording 20260224)

Person (Pipeline A) + real ArUco scene (Pipeline B) in one desk-anchored
Unity world, from recording_20260224_083945.bag — the recording where the
person CARRIES the object cube. INTEGRATION.md; offset/accuracy analysis in
OBJECT_OFFSET.md. Regenerate with `../send_integrated_scene.py --dump-csv
output/integrated_stream.csv` (reads the FILTERED landmark + object CSVs —
edge-fill + Savitzky-Golay stages, OBJECT_OFFSET.md §0), preview with
`../plot_integrated_scene.py` (ALWAYS check the Python picture against
reality before Unity — pinned as `scene_preview.png`), then a Unity play
pass; re-check with `../validate_integration.py` (20/20 PASS pinned in
`validate_integration_output.txt`).

| File | What it is |
|---|---|
| `integrated_stream.csv` | the 899 streamed PSI1 records: pelvis (person space), 13 PSA5 angles (all 899 frames solve live after `--edge-fill 12` killed the warm-up snap), object world pose from the filtered track (22 undetected frames bridged/held with live=0). |
| `unity_person_log.csv` | Unity log: received pelvis + applied hip world position (reproduces anchor·pelvis to 0.0007 mm) + the rig's DEF-hand.R/L world positions for the offset analysis. |
| `unity_object_log.csv` | Unity object log; matches the filtered world CSV to 0.0006 mm. |
| `rig_dimensions.csv` | rest-pose FBX bone lengths at spawn, POST display-scaling to a 1.70 m person (raw 3.25 m height + the ×0.523 factor recorded as rows; OBJECT_OFFSET.md §6). |
| `validate_integration_output.txt` | the 20 checks: anchor math, stream integrity + smoothing honesty (< 15 mm from raw detections), plausibility, Unity exactness, carried-object consistency (moving object median 15.0 cm from the nearest wrist, velocity r = 0.84, cos 0.86). |
| `object_offset_analysis.png` / `analyze_object_offset_output.txt` | whole-video offset decoupling (`../analyze_object_offset.py`): world-frame offset rotates, object-frame grip vector constant per holding hand (right-hand std < 2 cm), decoupled residual median 3.3 cm / RMS 4.2 cm — the two-pipeline accuracy. |
| `unity_integrated_224.mp4` / `integrated_still.png` | the demo: jump-free (no left-arm snap, no cube pops, motion from the first second), smooth cube trajectory, rig scaled to a 1.70 m person with the cube at its hand, global view + sensor-POV picture-in-picture. |
| `real_color_frame100.png` | the recording's actual color frame 100 for visual comparison with the PiP inset. |

Real-time phase artifacts live in `../../realtime/dataset/` (the phase has
its own folder — this offline dataset is thesis material and stays as-is).

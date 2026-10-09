# unity_bridge/ — Python → Unity landmark streaming

Streams landmark CSVs (from `mediapipe/output/`) into Unity in real time.

## Transports
- **Shared memory (default)** — Python writes a fixed 180-byte record to
  `/dev/shm/pose_stream`; Unity's `PoseStreamReceiver` maps the same file and
  reads it every frame. A seqlock (sequence counter odd while writing, even
  when stable, checked before/after the copy) makes reads tear-free without
  locks. Zero-copy, zero-syscall on the read path — this is the transport the
  future real-time variant will use.
- **UDP fallback** — the same packet sent to `127.0.0.1:9750`
  (`--transport udp`; set the receiver's Transport to Udp in the Inspector).

## Packet layout (little-endian, 180 bytes)
| offset | type | field |
|---|---|---|
| 0 | u32 | magic `'PSE1'` |
| 4 | u32 | seq (shm seqlock; unused for udp) |
| 8 | i32 | frame index |
| 12 | f32 | time_s |
| 16 | i32 | landmark count (8) |
| 20 | 8 × {i32 id, f32 x, f32 y, f32 z, i32 valid} | landmarks, camera frame, meters |

Kept in sync with `Unity/Assets/Scripts/PoseStreamReceiver.cs` — change both
or neither.

## Usage
```bash
# Unity: Thesis > Setup Pose Scene (once), then press Play
python send_landmarks.py                 # newest filtered CSV, loops at true speed
python send_landmarks.py --csv <path> --speed 2 --no-loop
python send_landmarks.py --transport udp
```

## Unity side
- `Assets/Scripts/PoseStreamReceiver.cs` — reads packets, converts camera
  frame (X right, Y down, Z forward) to Unity (x, −y, z), draws 8 sphere
  markers + LineRenderer bones (blue left / red-orange right / grey torso).
  Auto-centers on the first frame's hip midpoint; `displayOffset` places the
  skeleton beside the character model.
- `Assets/Scripts/Editor/PoseSceneSetup.cs` — menu item **Thesis > Setup Pose
  Scene**: places the first model in `Assets/Models` at the origin and adds a
  `PoseStreamReceiver` object.

Note: the character FBX is not yet driven by the stream — retargeting joints
onto the rig requires the kinematic solve stage (joint angles), which is a
later step. This bridge displays the raw landmark skeleton alongside it.

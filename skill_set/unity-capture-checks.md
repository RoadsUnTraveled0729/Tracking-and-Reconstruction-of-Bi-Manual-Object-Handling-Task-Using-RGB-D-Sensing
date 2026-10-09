# Unity capture checks (thesis renders)

Rule: after any Unity capture used in the thesis, run
eval/unity_check/check_unity_log.py --stem <stem> --out <capture dir> and
compare the rig joints logged in v1/integration/output/unity_person_log.csv
(hip, hands, shoulders, elbows) against the landmarks before choosing the
figure frames. Do not choose frames from the renders alone.

Why: On 2026-09-07 the committed renders of frames 114 and 700 carried two
display defects that a look at the picture did not reveal as defects: the
held-group spheres were pushed toward the editor's main camera and floated
off the joints in the sensor view, and the rig's trunk used the loop
recording's length, which placed the shoulders 10 cm low and hid the
reaching right arm under the drawn desk top on every frame before 540. The
numeric check showed a constant 85 px hand offset; the log showed the hand
below the desk top (world y 0.72).

How to apply:
- Capture: eval/unity_check/run_unity_capture.py --stem <stem>
  --angles-csv <recovery angles> --out eval/output/unity_check_<alias>
  [--sizing <json>]; the run aborts before arming anything if the sizing
  json is missing, and aborts if editor.log reports error CS;
  about three minutes unattended on this machine (Unity 6000.3.19f1 at
  ~/Unity/Hub/Editor); no editor may be running; remove stale
  /dev/shm/integrated_scene_v2 and rt_* files and send_scene processes.
- The dumper never writes the recording's last frame (899 of 900 on the rail
  recording); the final-station panel uses frame 898.
- Avatar sizing is per replayed recording (E-036, 2026-09-14): the avatar
  must reproduce the geometry the solver ran on, which is the landmark
  geometry of the recording being replayed, not the subject's anatomy and
  not another recording's lengths. eval/unity_check/make_rig_sizing.py
  writes eval/reports/<alias>_rig_sizing.json with five lengths, the four
  offset-fit arm medians of eval/reports/<stem>_offset_fit.json and the
  trunk as the median distance from the recovery pelvis to the measured
  mid-shoulder on frames with fail_torso == 0. run_unity_capture.py --sizing
  <json> (default eval/reports/<alias>_rig_sizing.json) writes the side
  channel /tmp/r5_rig_sizing just before the editor starts and removes it
  afterwards; the receiver reads it in Awake, rejects a file older than
  3600 s or missing a key, and writes rig_sizing_used.txt beside
  rig_dimensions.csv. The receiver's own arm and trunk defaults are 0,
  meaning no scaling, so a capture without the side channel leaves the rig
  as authored and says so in editor.log.
- After every capture run eval/unity_check/check_rig_sizing.py --sizing
  <json> --rig-dimensions <out>/rig_dimensions.csv --used
  <out>/rig_sizing_used.txt as well as check_unity_log.py. It requires each
  of the five requested lengths in the measured rig to 1e-3 m, rows
  upper_arm_R, upper_arm_L, forearm_R, forearm_L and
  torso_hip_to_midshoulder. It fails on every capture made before E-036 by
  construction, because those carry the loop recording's arm constants.
- Sphere placement is HeldMarkers.cs; EvalFrameDump re-places the spheres for
  the sensor-view camera before each render.
- The desk marker card is drawn over the desk slab (PlateOverlay.shader on
  marker id 2 only) because its calibrated centre is 0.4 cm below the fitted
  tabletop plane; do not move the card or lower the desk to fix the picture.
- Record the run in eval/DECISIONS.md (E-031 is the first) and the numbers in
  the chapter builder comments.
- Trails (D9, 2026-09-07): writing/v9/scripts/make_ch7_trails.py
  writes /tmp/r5_trails.txt (reference path, tracked marker origin, model
  right wrist, in display axes); Unity/Assets/Scripts/TrajectoryTrails.cs
  draws it under the levelled ArucoWorld node when the file exists, and the
  frame-indexed trails grow with the stream. Delete the file before a capture
  that must not show trails. Never shell out with pkill -f on a pattern that
  appears in your own command line; it kills the launching shell.
- History of the sizing rule: the trunk length was a receiver constant
  (E-031, 0.576 m rail against 0.479 m loop), then a single opt-in file
  /tmp/r5_torso_m written by --torso-m (E-035, 0.517 m on the handover take
  r7), with the arm lengths left at the loop values throughout (D-005).
  E-036 superseded both. --torso-m and /tmp/r5_torso_m no longer exist and
  no capture may reintroduce them; /tmp/r5_rig_sizing carries all five
  lengths instead. Captures E-031 to E-035 applied the loop arm medians to
  replays of other recordings, so their rendered-joint errors measured a
  configuration mismatch on top of the display path.
- The presentation render takes --alias r7 (render_ch7_trails.py) and
  Chapter7TrailView.cs draws the left wrist when the view json carries
  wristLeft.


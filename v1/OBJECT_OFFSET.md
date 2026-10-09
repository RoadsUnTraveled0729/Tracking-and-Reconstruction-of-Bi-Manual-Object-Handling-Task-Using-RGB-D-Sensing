# Why the object does not sit in the rig's hand — offset analysis & system accuracy

Whole-video analysis (all 899 frames of `recording_20260224_083945`, the
person carrying the 70 mm cube) of the gap between Pipeline B's tracked
object and the hand, answering four questions: is the offset constant,
how to decouple it, why it exists, and what the accuracy of the whole
system is once it is accounted for. Also: whether the rig's proportions
are consistent with the scene.

Everything below is reproduced by
`integration/analyze_object_offset.py` (figure:
`integration/output/object_offset_analysis.png`, stats:
`analyze_object_offset_output.txt`, both pinned in
`integration/dataset/`). Per the project rule, every number was plotted
and checked in Python before being written here.

## 0. First, the jumps that were in the video (fixed)

Two artifacts made the previous video look discontinuous, and both were
fill gaps in existing machinery — not new phenomena:

- **The person's left arm snapped ~60° at frame ≈9.** MediaPipe's first
  10 frames carry hallucinated left elbow/wrist points that the
  visibility gate correctly removes (FINDINGS 2026-07-18), but
  `filter_landmarks.py` only interpolated INTERIOR gaps — a missing run
  at the very start of the recording stayed empty, the solver held the
  rest pose, then snapped to the first live pose. Fix: `--edge-fill N`
  backfills leading/trailing runs (≤ N frames) with the nearest valid
  sample before smoothing. Max per-frame angle step in the stream:
  **60.3° → 11.8°**, all 899 frames now solve fully live.
- **The cube froze and popped during marker dropouts.** The object
  marker is hand-covered on 22 frames (4 gaps, the longest interior one
  7 frames); hold-last + re-acquire produced 0.4–2.2 cm / 1.6–3.4°
  pops, and raw PnP jitter ran to 19 mm between frames. Fix: a Pipeline
  B filtering stage, `aruco/filter_object_track.py` — Hampel despike,
  interior gaps bridged (position linearly, rotation along the SO(3)
  geodesic — matrices/axis-angle only), then **frame-to-frame
  polynomial smoothing** (Savitzky-Golay, window 9, order 2; rotation
  via a rolling chordal mean). Smoothing moves measured frames by a
  median **1.2 mm** (max 11.6 mm, within PnP jitter — asserted < 15 mm
  in `validate_integration.py`); frame-step p95 **10 → 4.9 mm**. The
  trailing 12-frame gap is held with `detected=0` (honest red tint).

## 1. The offset, whole video

Distance from the tracked object (ArUco marker center) to the nearest
wrist landmark, all 899 frames: **median 16.6 cm** (p95 22.0); to the
cube's geometric center: median 14.5 cm. The person cups the box with
either hand (nearest wrist: left 72% / right 28% of frames), and parks
it on the desk for t ≈ 13.5–23 s — during that stretch the hands leave
and there is no object–hand relationship to measure (distance runs to
24 cm). "Carried" frames (586/899) are unambiguous in the object's own
height: resting, the marker center sits half a cube edge (3.5 cm) above
the tabletop; carried, it rides 15–25 cm above it.

## 2. Is it a constant offset? Frame choice decides

- **In the world frame: no.** The per-axis offset components swing over
  the video (x: +1.7 ± 8.0 cm, z: −11.2 ± 4.8 cm) and the horizontal
  direction of the offset vector sweeps essentially the full circle
  (±178°) as the person walks the box 3.35 m and turns it. Only the
  offset's LENGTH is roughly constant.
- **In the object's own frame: yes, one constant vector per holding
  hand.** Expressing the same offset as `d = R_objᵀ (wrist − marker)`
  (the wrist seen from the marker's axes):

  | holding hand | frames | mean [x, normal, z] (cm) | std (cm) |
  |---|---|---|---|
  | left  | 314 | (+3.8, −8.2, +8.6) | 3.8, 2.8, 2.5 |
  | right | 249 | (−11.0, −10.6, +5.3) | **1.8, 0.9, 0.8** |

  Flat lines in the figure's panels 3–4: each grip is rigid. The
  world-frame "wandering offset" is exactly this fixed vector rotating
  with the box. The right-hand grip (held while that wrist was fully
  visible to the sensor) is constant to better than 2 cm on every axis.

## 3. Decoupling, and where the vector physically comes from

Decoupling = predicting the wrist from the object pose plus that hand's
constant grip vector: `wrist ≈ marker + R_obj · d̄_hand`. The
components of `d̄` have direct physical meaning:

- **Along the marker normal (−8 to −11 cm):** the marker is printed on
  ONE FACE of the cube, not at the grip point. Face → cube center is
  −3.5 cm (half the 70 mm edge); the rest is the far half of the box
  plus the palm — MediaPipe's wrist is the wrist JOINT, several
  centimeters behind the palm that actually touches the box.
- **In-plane (x, z up to ~9 cm):** where on the box face the hand cups
  it (underneath/beside, not centered), different for each hand — which
  is why one constant per holding hand, not one global constant.

## 4. Root causes of the offset (why it exists at all)

1. **Marker placement**: Pipeline B tracks the marker center on the
   box's face — by construction offset from any grip point.
2. **Landmark definition**: Pipeline A tracks the wrist joint, not the
   palm/fingers that hold the box.
3. **Per-hand grip geometry + regrips**: two different cupping
   positions (and a slightly different grip after the box is picked
   back up at t ≈ 23 s) — visible as the 2–4 cm std on the left hand.
4. **The rig's proportions (the reason it looked large on screen)**: see
   §6 — the FBX is authored ~2.2× human size; it is now display-scaled
   to a 1.70 m person at spawn, which brings the FK hand from 30–46 cm
   down to 7–13 cm (median) of the real wrist point; the remainder is
   the rig's non-uniform proportions. The DATA offset (§2) is 14–17 cm;
   everything beyond that in the rendered scene is the rig.
5. **Measurement noise floor**: what remains after decoupling (§5).

## 5. Accuracy of the whole system (after decoupling)

Residual `|wrist − (marker + R_obj·d̄)|` on carried, measured frames
(marker detected, wrist raw — 563 frames):

| segment | median | p95 | note |
|---|---|---|---|
| right-holding | **1.0 cm** | 3.8 cm | wrist fully visible — the two-pipeline floor |
| left-holding | 4.6 cm | 8.9 cm | wrist half-occluded by the carried box |
| all carried | 3.3 cm | 7.3 cm | RMS 4.2 cm |

Velocity agreement (object vs nearest wrist, pooled axes): Pearson
**r = 0.842** while carried (0.273 over the whole video — diluted by
the resting stretch, where both velocities are just noise around zero).

Read: two fully independent measurement chains (RealSense depth +
MediaPipe landmarks vs RGB ArUco PnP), linked only through the
calibrated desk-anchor transform, agree on a moving point's trajectory
to ~1 cm when sight lines are clean, ~4–5 cm when the carried box
occludes the wrist. That is the ground-truth quality of the integrated
reconstruction.

## 6. Is the rig proportioned consistently with the scene? It wasn't — measured, then fixed

The FBX is authored **3.25 m tall** (rest hip height 1.58 m, ~2.2×
human) in a scene where the desk top is at 0.72 m — the audit that
exposed why the cube appeared to float near the rig's hip: the FK
hands reached a median 30–46 cm past the real wrist points.

Fix: `IntegratedSceneReceiver` now measures the rig's rest height at
spawn (`DEF-head_end`) and uniformly scales the root to a **1.70 m
person** (factor 0.523). Uniform scaling leaves the bone rotations —
and therefore the whole angle transfer — untouched; the per-frame root
translation still pins the hip to the mapped pelvis. Post-scale
bone lengths (`integration/output/rig_dimensions.csv`, which also
records `rig_rest_height_raw` and `applied_scale`) against the
person's landmark medians:

| segment | rig (m) | person (m) | ratio |
|---|---|---|---|
| shoulder width | 0.336 | 0.316 | 1.06 |
| upper arm R / L | 0.217 / 0.217 | 0.279 / 0.225 | 0.78 / 0.96 |
| forearm R / L | 0.295 / 0.295 | 0.185 / 0.232 | 1.59 / 1.27 |
| hip → mid-shoulder | 0.535 | 0.456 | 1.17 |

Result: the rig hand now lands a median **7–13 cm** from the wrist
landmark (was 31–41 cm) and 20 cm from the marker (was 40 cm) — the
cube visibly sits at the hand in the video. What remains is the rig's
NON-uniform proportions (its forearm is 1.6× the person's even at the
correct overall height); only per-bone retargeting onto a
measured-proportions skeleton could remove that, and it is out of
scope because the thesis transfers angles, not surfaces.

Person-side note: the landmark-measured L/R arm asymmetry (upper arm
0.225 vs 0.279 m) is depth-noise + occlusion in the landmarks
themselves — MediaPipe segment lengths are not constant, which also
feeds the left-hand residual in §5.

## 7. Reproduce

```bash
# jump fixes (writes the *_filtered CSVs the senders now use)
cd mediapipe && python filter_landmarks.py \
    --csv output/recording_20260224_083945_landmarks_raw_v2.csv \
    --out output/recording_20260224_083945_landmarks_filtered_v2.csv \
    --edge-fill 12
cd ../aruco && python filter_object_track.py \
    --csv output/recording_20260224_083945_object_world.csv --plot

# stream + Unity play pass (logs rig hands + rig_dimensions.csv), then:
cd ../integration && python send_integrated_scene.py --dump-csv output/integrated_stream.csv
python analyze_object_offset.py     # prints §1–§6, writes the figure
```

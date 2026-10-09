# Defense Presentation Outline (from Thesis V6)

Currency note (2026-10-08): This is the historical Thesis V6 outline for
the original 20-minute, 19-content-slide presentation. Its slide references
and claims retain that scope. The current V9-based delivery, English
outline and QA guide are listed in
[the final presentation README](defense_2026/README.md).

20-minute talk, 19 content slides, ~1 minute each; videos count toward the
budget. Committee assumed NOT to have read the thesis. Every number below is
quoted from Thesis V6 with its section named; nothing is invented. Figure
paths refer to the main thesis tree (read-only); at build time each is
copied into `presentation/assets/`.

Notation for this outline: each slide lists its on-slide text (max 5 short
lines), its figure with exact source path, the numbers used with their
thesis source, and open TODOs.

---

## Slide 1 — Title (inverted, black background)

- TRACKING AND RECONSTRUCTION OF BI-MANUAL OBJECT HANDLING TASK USING
  RGB-D SENSING
- Lanqing Luo
- Supervisor: Dr. Shahram Payandeh
- Department of Engineering Science, Simon Fraser University
- TODO: defense date (user to confirm)

No figure. Source: thesis title page.

## Slide 2 — The problem (plain language, no jargon)

Text (5 lines max):
- One depth camera watches a person handling a box with both hands.
- Goal: rebuild the whole event in 3D: body, both arms, the box.
- Uses: clinical motion assessment, robot learning by watching; an avatar
  protects privacy where video would not.
- No suits, no gloves, no camera array: one commodity sensor, paper markers.
- The hard part: knowing how far to trust the reconstruction.

Figure: the real camera frame beside the finished Unity reconstruction,
`writing/v2/figures/ch6_fig4_compare.png` (thesis Figure 6.4). This is the
"what we built" picture and needs no vocabulary to read.
Source: Ch1 1.1 (motivation), Ch6 6.6.

## Slide 3 — Contributions (3 bullets)

- A closed-form upper-body kinematic model from eight RGB-D landmarks,
  validated as an exact inverse on synthetic ground truth.
- Two fully independent measurement pipelines joined in one calibrated
  world frame, so the system grades its own accuracy without any motion
  capture equipment: about 1 cm agreement where sight lines are clean.
- A real-time variant of the same mathematics inside the 33.3 ms frame
  budget, with the cost of causality measured, not guessed.

No figure (text slide). Source: Ch9; the 1.0 cm figure is Table 6.5,
budget 33.3 ms is Ch7 7.2.

## Slide 4 — System overview (one diagram)

Text (2 lines):
- One recording feeds two pipelines that share no code and no data.
- They meet only in a calibrated world frame; B is the witness that grades A.

Figure: `writing/v6/figures/fig1_system_flow.png` (thesis Figure 2.1:
Pipeline A landmark branch, Pipeline B marker branch, fusion, Unity).
Source: Ch2 Figure 2.1, Ch4 4.1 (independence argument).

## Slide 5 — Kinematic model I: the root frame (intuition first)

Text:
- Three stable landmarks: both hips and the right shoulder.
- The hip line is one axis; the three points fix the torso plane.
- Two cross products complete a perfectly orthonormal frame at the right
  hip (L24), the root of every other frame.
- Sanity anchor: an upright person facing the camera decodes to Euler
  (0, 180, 0), the T-pose reference.

Figure: `writing/v6/figures/ch3_fig4_torso_photo.png` (thesis Figure 3.4:
input vectors and finished frame drawn on the real frame-100 image).
Source: Ch3 3.2.1-3.2.2, reference configuration in 3.2.2.

## Slide 6 — Kinematic model II: shoulder swing and twist

Text:
- The shoulder does two things: aims the arm (swing, 2 angles) and rolls
  it about its own axis (twist, 1 angle).
- Twist is innermost: rotation about the arm axis leaves the arm direction
  unchanged, so swing is read from the elbow, twist from the forearm.
- Elbow flexion closes the chain: 3 landmarks per arm carry exactly 4
  observable rotational DOF, and exactly 4 angles are extracted.

Figure: `writing/v6/figures/ch3_fig6_swing_twist.png` (thesis Figure 3.8,
drawn with the measured frame-100 arm direction).
Source: Ch3 3.3.1 (dimension count), 3.4.2.

## Slide 7 — Kinematic model III: the twist solve (the derivation that matters)

Text:
- Roll about an axis is only visible in the plane perpendicular to it.
- So first undo the swing, bringing the arm axis onto local x; the
  forearm's perpendicular part then lives in the y-z plane, and
  twist = atan2(-f'_y, f'_z).
- Projecting onto a plane that contains the axis reads pure segment
  geometry as twist; the correct projection was validated against
  synthetic truth to 8.5e-14 degrees over 900 frames.

Displayed math (LaTeX in Marp): f' = R_z^T R_y^T v_fa, then the atan2 line;
full derivation chain deferred to backup section 4.
Figure: none, or reuse panel (b) of ch3_fig6_swing_twist.png cropped.
Source: Ch3 3.4.2 (equations 3.15-3.16, validation number).

## Slide 8 — Pipeline A: the estimation path

Text:
- MediaPipe Pose finds 33 landmarks; the eight upper-body ones are used.
- Its appearance-based depth is discarded; the RealSense depth image is
  sampled at each landmark pixel and deprojected into metric 3D.
- Visibility below 0.5 becomes missing data, never a guess (Data
  Integrity rule).
- Despike, bridge short gaps, zero-phase Butterworth at 3 Hz, then solve.

Figure: `writing/v6/figures/ch2_fig_mediapipe.png` (thesis Figure 2.3:
detector output on the real frame, numbered upper-body landmarks).
Source: Ch2 2.1.2, 2.1.5.

## Slide 9 — Pipeline B: the witness path

Text:
- Three printed markers: desk anchors the world frame, wall gives gravity
  (it is plumb), a 50 mm marker rides the 70 mm cube.
- Poses from square corners by planar geometry; mean reprojection error
  0.06 to 0.18 px over 899 frames.
- Static poses calibrated once (chordal mean of 10 frames) and frozen;
  re-anchoring per frame would inject the anchor's wobble everywhere.
- The result is camera-independent: the wall stays put in the desk frame
  to 5.8 mm (p95) at 3.2 m.

Figure: `writing/v2/figures/ch4_fig3_markers_photo.png` (thesis Figure 4.3:
the three detected markers on frame 100, real image).
Source: Ch4 Table 4.1 (reprojection, coverage), 4.2.1 (calibration), 4.3.1
(camera invariance).

## Slide 10 — Experimental setup (real photos) + [VIDEO 1]

Text:
- Desk against a wall; subject stands opposite, carrying a 70 mm cube.
- Camera at the desk edge: 0.17 m above and 0.57 m behind the desk marker.
- Evaluation recording: 899 frames, 30 fps, 30.0 s, 640 by 480.

Figures: `writing/v6/figures/ch2_fig_setup.png` (thesis Figure 2.2, the
annotated real camera view) and, small, `writing/v2/figures/ch6_fig2_layout.png`
(thesis Figure 6.2, measured geometry to scale, labelled as a drawing).
TODO: a photograph of the physical rig taken from outside the camera
(sensor on its mount at the desk edge). No such photo exists in the repo;
user to take one. Until then the slide carries the camera-view photo only.
[VIDEO 1: the recorded session, raw camera view] full-slide placeholder
comes immediately after this slide's content (same slide, video fills it).
Source: Ch2 2.1.1, Ch6 6.2 Table 6.1.

## Slide 11 — Results I: accuracy against the independent witness

Text:
- The carried cube must shadow the hand that carries it; the grip is a
  constant vector in the cube's own frame (right hand: stable to under
  2 cm per axis over 249 frames).
- Removing the grip leaves pure measurement disagreement between the two
  pipelines:
- right hand holding: median 1.0 cm (p95 3.8); left hand holding: median
  4.6 cm (p95 8.9); all carried frames: median 3.3 cm, RMS 4.2 cm.
- Velocity correlation while carried: 0.84.

Figure: `writing/v2/figures/ch6_fig3_offset.png` (thesis Figure 6.3: world
frame offset sweeping the circle vs collapsing to constants in the object
frame, plus residuals).
Source: Ch6 Tables 6.4 and 6.5, 6.5 prose (0.842 carried / 0.843 in-motion;
slide quotes 0.84 at 2 dp).

## Slide 12 — Results II: the bimanual task + [VIDEO 2]

Text:
- One continuous 30 s take: lift, carry, turn, pass between hands, park,
  regrip; transitions deliberately kept in.
- The cube turns through 511 degrees cumulative (net 26), so a fake
  constant-offset fit cannot survive; the real grip constant does.
- Hand-overs appear as clean switches between two per-hand grip vectors;
  left hand is the nearer wrist on 72 percent of frames, right on 28.
- Parked stretch: cube rests on the reconstructed desk to 4.2 mm.

Figure: `writing/v2/figures/ch6_fig1_timeline.png` (thesis Figure 6.1:
height, speed, cumulative rotation timeline with the parked band).
[VIDEO 2: real video beside the Unity reconstruction, in sync]
Source: Ch6 6.1, 6.1.1-6.1.3, 8.2.

## Slide 13 — Results III: where the error comes from

Text (small table on slide):
- Depth noise floor: 5 to 10 mm raw landmark jitter, 1 to 2 mm after
  filtering, about 0.5 degrees of segment direction noise.
- Self-occlusion is the dominant term: 4.6 cm (occluded left wrist)
  against 1.0 cm (visible right wrist).
- Anchor lever arm: 0.69 degrees of session drift would move the wall
  34 mm; the frozen anchor bounds it below 9 mm.
- Going real-time adds: worst joint group median 0.64 degrees, object
  6.2 mm median vs the offline solve.

Figure: none (the four-row table IS the slide).
Source: Ch8 8.1 and Table 8.1 (depth floor, lever arm), Ch6 Table 6.5
(asymmetry), Ch7 Table 7.3 (causality cost).

## Slide 14 — Failure cases I: what breaks + [VIDEO 3]

Text:
- A hand covering the marker costs the object track 22 of 899 frames;
  the pose is held and the cube renders red: declared, not hidden.
- The carried box half-occludes the wrist behind it: the left-holding
  residual is 4.6 cm against the 1.0 cm floor.
- MediaPipe hallucinates occluded landmarks: warm-up frames put the left
  arm up to 2 m off until the visibility gate removes them.
- A held joint drifts 1.4 to 7.8 degrees over 30-45 frame holds: the
  motion that happened while blocked is simply lost.

Figure: `writing/v2/figures/ch6_fig5_occlusion.png` (thesis Figure 6.5:
red held-joint spheres in four synthetic occlusion scenarios).
[VIDEO 3: occlusion in action: red flags on held joints, red-tinted cube]
Source: Ch4 4.3.3 (22 frames), Ch6 6.3 (gate, drift), Table 6.5.

## Slide 15 — Failure cases II: why it breaks (root causes)

Text:
- Twist is observable only through sin(elbow flexion): noise amplification
  1.41x at 45 degrees, 11.3x at 5, unobservable at a straight arm.
- Euler extraction divides by cos(pitch): 345x sensitivity at 89.9
  degrees, and the carried box reaches exactly that pitch.
- Both are derived laws verified numerically, not bugs; mitigation is
  filtering, flagging, and keeping matrices everywhere but the display.

Figure: `writing/v2/figures/ch8_fig1_conditioning.png` (thesis Figure 8.1:
the two conditioning curves with verified points).
Source: Ch8 8.1 and Figure 8.1.

## Slide 16 — Limitations (honest list)

- No external motion capture: the evaluation floor is the grip vector's
  own stability, so 4.6 cm (left) is an upper bound, not a measurement.
- Three landmarks per arm see 4 DOF: no forearm pronation, no wrist pose,
  no fingers; legs untracked.
- Single subject, single session, 30 seconds; real-time tested on a
  replayed recording, not a live camera.
- Display rig proportions: the avatar hand lands 7 to 13 cm from the
  wrist landmark (rendering only; no result is computed on the rig).

No figure. Source: Ch6 6.5, Ch8 8.1 Table 8.1, 8.1 closing.

## Slide 17 — Future work

- Model-based recovery of occluded joints: the laboratory's Gaussian
  Bayesian Network framework, with the synthetic occlusion scenarios as a
  ready-made benchmark.
- Hand landmarks for grasp, not just wrist position.
- Hardware timestamps end to end; 60/90 fps sensor modes.
- Marker bump detection and automatic re-calibration.

No figure. Source: Ch8 8.3.1-8.3.5.

## Slide 18 — Conclusion

- Two independent measurement chains, joined only by a calibrated static
  transform, agree on a moving hand to about 1 cm when sight lines are
  clean, and every degradation has a named, measured cause.
- The same mathematics runs live at camera rate, 100 ms behind the motion.
- Capability came from the arrangement of commodity parts, not from
  better parts: one depth camera, paper markers, open-source software.

No figure. Source: Ch9, Ch6 Table 6.5, Ch7 7.3 (100 ms).

## Slide 19 — Thank you / questions

- Thank you. Questions welcome.
- One line: "All numbers in this talk trace to the pinned artifacts of the
  thesis; backup slides follow."

---

# Backup slides (Q&A period; one section per question category)

## B1. Assumptions (each: what, justification, what breaks if it fails)
- Rigid torso plate (no hip-shoulder twist separation) - 3 torso landmarks
  cannot separate them; trunk lean pitches the root frame (Ch3 3.2.1).
- Wall is plumb (the single physical assumption) - gravity derives from
  it; the depth-fitted gravity cross-check agrees to 5.03 degrees (Ch4
  4.2.2).
- Camera fixed for the session; anchor calibrated once - measured session
  drift 0.20 mm / 0.088 deg p95 justifies freezing (Ch4 4.2.1, 6.4).
- Rigid grip while carried - right hand std under 2 cm/axis validates;
  left regrip inflates it (Ch6 6.5).
- Marker roles are configuration, not inference (Ch8 8.1).
- Subject faces the sensor; workspace is one field of view, 55.6 by 43.1
  degrees (Ch8 8.1).

## B2. Why this approach (design decisions and rejected alternatives, DECISIONS.md)
- Shared memory over UDP as default transport (both built; seqlock; the
  live variant needs it; UDP kept as drop-in).
- Deployed per-frame solver over vectorized/numba/GPU variants live (99 us
  vs 33.3 ms budget; vectorization pays only offline, 170x in batch).
- Zero-phase Butterworth 3 Hz offline over One Euro (measured shake 1.9 vs
  10.2 mm raw; One Euro returns as the causal live filter, retuned
  0.05 to 1 Hz cutting lag 9 to 3 frames).
- ArUco over learned detectors for the witness pipeline (independence of physics).
- Chordal matrix mean over quaternion averaging (matrix-only policy).
- Hold-last + flag over inventing poses (data integrity; Bayesian recovery
  deferred as future work).
- Desk marker as world frame over camera frame (camera-placement
  invariance, measured).

## B3. What if changed (sensitivity; untested = say untested)
- Camera placement: measured two-position experiment, desk edge beats high
  camera on every metric (Table 6.2: wall p95 5.8 vs 28.3 mm).
- Marker size vs distance: wall at 32 px is the measured worst case; lobe
  discrimination fails below 40 degrees separation (Ch4/App D, Ch8).
- Filter cutoff: the one latency dial live; 0.05 Hz gave 300 ms lag, 1 Hz
  gives 100 ms at correlation 0.998 (Ch7 7.3).
- Different subject/body: untested (single subject); angles transfer by
  design, rig proportions do not (Ch5 5.3.1).
- Higher frame rate: untested; budget shows headroom, detector inference
  is the stage to re-validate (Ch8 8.3.1).

## B4. Full derivations (behind slides 5-7)
- Root frame construction with the two cross products and the reference
  decode (Ch3 3.2.2, worked example 3.2.3 numbers).
- ZXY Euler composition and extraction, gimbal convention (3.4, eq 3.8-3.10).
- Swing solve, twist solve with the un-swing step, elbow, e_z = 0 DOF
  accounting, left-arm mirror (3.4.2-3.4.3, eq 3.11-3.17).
- The anchor transform M = P R F and its two cancelling handedness flips
  (Ch5 5.2.1, eq 5.1).
- Chordal mean and geodesic bridge (Ch4 eq 4.1, 4.4).

## B5. Extensions (deeper than slide 17)
- Bayesian occlusion recovery: what exists already (solver isolates
  unobservable angles, live mask, amplification weights) and the exact
  benchmark (Ch8 8.3.5).
- Multi-person passing scenario: what carries over, what does not (Ch8 8.2).
- Timestamped playback buffer as the declared-interpolation display path
  (Ch8 8.3.3).

## B6. Extra results (did not make the main deck)
- Placement experiment full table (Table 6.2).
- Per-stage latency table (Table 7.1) and solver benchmark
  (Table 7.2 + `writing/v6/figures/ch7_fig2_bench_v4.png`).
- Occlusion scenario table (Table 6.3, 33 checks).
- Offline vs real-time full comparison (Table 7.5).
- Packet family and the shared memory block diagram
  (`writing/v6/figures/ch5_fig_shm.png`, Table 5.1).
- Viewer 3D views of the raw recording
  (`writing/v6/figures/appD_fig_viewer.png`).
- Real-time failure modes: rejection lockout (877 to 541 frames, fixed to
  863) and motion-onset false rejection (92.4 to 97.3 percent live)
  (Ch7 7.4).

---

# Video shot list (summary; full video-shot-list.md at build)

- VIDEO 1 (slide 10): raw camera view of the evaluation session. Screen
  recording of playback (or bag export). Under 25 s. Must show: person,
  desk, cube with marker, both hands, wall marker.
- VIDEO 2 (slide 12): real video and Unity reconstruction side by side,
  in sync, covering lift, carry, a hand-over, parking. Screen recording.
  Under 30 s.
- VIDEO 3 (slide 14): failure vocabulary: red held-joint spheres during an
  occlusion, red-tinted cube while the marker is covered. Screen recording
  of the Unity scene. Under 20 s.

# TODO markers carried into the build

- TODO: defense date for the title slide.
- TODO: photograph of the physical rig (camera on its mount) taken from
  outside the camera view; nothing in the repo shows the rig itself.
- Videos 1-3 to be recorded separately (placeholders in the deck).

# Findings

Known issues and sensor/calibration gotchas discovered during the project.
One-liners, most recent first.

- 2026-07-24: a TRAILING-window causal despike has two failure modes a
  centered offline Hampel never shows: (1) rejected samples that don't
  update the window make it stale, so sustained real motion is rejected
  FOREVER (object live 877->541 until a 3-reject accept+re-seed cap);
  (2) at motion onset the trailing MAD is ~0, so genuine acceleration
  trips the absolute floor (raise it: 20->35 mm).
- 2026-07-24: two processes each opening the same bag with
  set_real_time(True) start playback at different wall times (model-load
  asymmetry) — measured 567 ms A-vs-B skew; a ready-file start barrier
  reduces it to <= 1 frame. Also: this bag plays 899 frames in 35.0 s
  (25.7 fps, identical in both processes) — librealsense playback pacing,
  not compute (p99 compute < 33 ms).
- 2026-07-24: pip-installing cupy/torch silently UPGRADES numpy to 2.x,
  which breaks mediapipe 0.10 and anaconda's scipy at import time —
  pin numpy==1.26.4 back and use cupy-cuda12x<14 (cupy 14 requires
  numpy>=2); torch must match the DRIVER's CUDA (2.13+cu130 refused to
  run on the 575/CUDA-12.9 driver; 2.7.1+cu126 works).
- 2026-07-23: starting a screen capture and the streamed playback in TWO
  separate harness Bash calls records the model round-trip (~5 s) as
  frozen video — the receiver just holds its last frame. Launch ffmpeg
  (background) and the sender in ONE shell invocation with a fixed sleep
  lead, then trim exactly that lead (ffmpeg -ss). Also: shell precedence
  — `cd X && nohup ffmpeg ... & sleep 2 && sender` backgrounds the whole
  `cd && nohup` compound, so the sender runs in the OLD cwd; use
  absolute paths.

- 2026-07-23: "is the offset constant?" is a FRAME question: object−wrist
  ran ±178° of azimuth swing in the world frame yet was constant to
  < 2 cm/axis per holding hand in the object's own frame — express a
  suspected rigid offset in the co-rotating frame before judging, and fit
  it only while the relationship physically exists (the object's height
  above the tabletop cleanly separates carried from parked).
- 2026-07-23: summed frame-to-frame path length on a raw PnP track
  overstates travel — 3.35 m raw vs 1.94 m after Savitzky-Golay on
  20260224 (jitter integrates into fake distance). Quote travel from the
  smoothed track.
- 2026-07-23: the demo FBX rig is ~2.2x human scale and NON-uniformly so
  (forearm 3.0x, upper arm 1.5x; rest hip height 1.58 m) — angles-only
  retargeting hides this until you measure bone lengths at spawn
  (rig_dimensions.csv) against landmark segment medians; the rendered
  hand then misses the object by the accumulated arm surplus (~50 cm).
- 2026-07-23: gap-fill that interpolates only INTERIOR runs silently
  leaves warm-up (leading-edge) landmark dropouts empty — the solver
  holds rest and SNAPS (60° in one frame here) when data starts; edge
  runs need constant backfill (filter_landmarks.py --edge-fill).

- 2026-07-19: cv2.aruco with default CORNER_REFINE_NONE returns integer
  -pixel corners — a close static marker then shows 0.00 mm frame-to-frame
  scatter, which is FALSE stability (detector re-snapping to identical
  pixels), not accuracy. CORNER_REFINE_APRILTAG reveals the true subpixel
  scatter (desk 0.4 mm/0.17 deg) and improves the far wall 37 -> 7 mm.
- 2026-07-19: a single 50 mm ArUco marker's ORIENTATION drifts ~0.07 ->
  0.7 deg over a 30 s session (illumination change as the person moves)
  while its position stays static to ~1 mm; through a 2.8 m lever arm that
  drift moves far points ~40 mm — average early frames once and freeze the
  anchor, and never chain far points through a small marker's rotation.
- 2026-07-19: conjugating a frame-mapping rotation (qA·R·qA⁻¹·C) instead
  of pre-multiplying it (qA·R·C) silently cancels the mapping out of the
  applied pose — every POSITION check still passes (positions were mapped
  separately and correctly), so orientation errors of this class are
  invisible to positional validation. Guard rails: plot the data (person
  axes arrows) in Python first, and assert orientation-level facts
  (facing direction) in the validator, not just positions.
- 2026-07-19: a steeply pitched LookAt camera keystones vertical edges —
  a perfectly plumb wall reads as "tilted" on video. Keep the demo
  camera pitch shallow (raise the look-at point) before concluding the
  geometry is wrong — and conversely, verify plumbness numerically, not
  from the rendered image.
- 2026-07-19: a depth-plane "tabletop" fit that includes an annulus
  around a HAND-HELD marker sweeps the person's body instead of the desk
  — in 20260224 it bent the gravity estimate 60+ deg toward horizontal.
  Never assume a movable marker rests on a surface; gate its annulus on
  plane agreement with an always-valid reference (the desk marker's).
- 2026-07-19: Unity ZXY Euler round-trips lose a digit near gimbal lock
  (x -> +/-90): a hand-carried box reaching x = -89.9 deg produced
  1.3e-6 deg euler round-trip error while the matrices still matched to
  1e-14 — exactness checks on Euler need ~1e-5 deg tolerance, matrix
  checks stay at machine precision.
- 2026-07-19: for near-degenerate IPPE lobes (~23 deg apart at 32 px),
  reprojection error is a BIASED lobe discriminator, not a noisy one: it
  preferred the anti-plumb (wrong) lobe on 815/837 wall frames with
  ratios up to 2.18 — overlapping the 2.15+ range where well-separated
  markers are genuinely decisive, so no ratio threshold can separate the
  cases. Lobe SEPARATION is the reliable signal for when to trust
  reprojection (>= 40 deg here).
- 2026-07-19: the in-quad depth-plane tiebreak was also wrong at range —
  the depth normal over a 32 px quad at 3 m is >30 deg biased and
  CONSISTENTLY picked the same wrong lobe (it shipped in commit 8978aed
  and passed 20/20 validation!). What exposed it was building REAL
  geometry from the poses: the wall landed in the desk plane and the
  object cube came out negative — physical-consistency rendering is a
  bug-finder that per-column statistics miss.
- 2026-07-19: depth-plane fits near desk clutter need aggressive gating:
  a naive annulus around the markers swept paper stacks and the box top
  and bent the gravity fit by 20 deg; inner exclusion 2.2x marker edge +
  outer 4x + per-annulus ±5 cm median gate + iterative 15->8 mm refit
  brings it to ~6 deg of a clean-region reference. Also: seed lobe choice
  by gravity ONLY for near-degenerate lobes — the tilted desk card's
  mirror lobe is MORE plumb than the true one, so a global gravity seed
  flips well-conditioned markers.
- 2026-07-19: 3 corrupted wall detections (person clipping the marker
  edge) produced wild poses whose lobes were well-separated, which reset
  a naive last-pose continuity reference to the mirror lobe for whole
  runs of frames — continuity references must be outlier-gated (update
  only within 30 deg, re-acquire after N misses), not overwritten every
  frame.
- 2026-07-19: Unity editor without xdotool/MCP-CLI can still be driven:
  the MCP-for-Unity HTTP server on 127.0.0.1:8080 answers raw JSON-RPC
  (initialize -> notifications/initialized -> tools/call) from curl or
  python urllib — used for play/stop/execute_code after the harness-side
  MCP connection was gone.

- 2026-07-18: MediaPipe emits POSITIONS for occluded/warm-up landmarks
  (visibility is the only tell): recording_20260224 frames 0-9 carry
  hallucinated left elbow/wrist points at visibility 0.001-0.5 that the
  old extractor exported as data. Gate on visibility (>= 0.5), don't
  trust presence of coordinates.
- 2026-07-18: 5x5 nonzero-median depth sampling changes valid landmarks
  by 0.00 mm median / <= 14 mm max (within depth noise) and recovers
  landmarks lost to single-pixel depth holes — strictly better than
  get_distance at one pixel (the FINDINGS 2026-07-12 hook, now done).
- 2026-07-18: the bracket trick (pkill -f "[s]end_arm") does NOT save a
  compound command that LAUNCHES the same script later in the line — the
  wrapper's cmdline contains the literal script name and still matches.
  pkill must be a fully separate Bash call from the relaunch.
- 2026-07-17: `pkill -f <pattern>` inside a compound background command
  kills the command's OWN wrapper shell if the pattern appears in its
  command line (exit 144) — run the pkill as a separate Bash call first.
- 2026-07-17: MediaPipe's first 1-2 frames of a recording can lack
  landmarks (warm-up) -> empty CSV cells -> NaN angles that poison a
  stream; senders must drop rows with missing cells, not propagate NaN.
- 2026-07-17: arccos(dot) is ill-conditioned near 0 deg (~1e-6 deg floor at
  float64) — angle-between-vectors checks must use atan2(|cross|, dot), or
  machine-precision agreement looks like a 1e-6 "failure".
- 2026-07-17: naive mean/std of yaw near ±180 deg is meaningless (wraps
  make std explode to ~176 deg while the true spread is ~5 deg) — compute
  stats on wrap_deg(y - 180) or circularly.
- 2026-07-17: recording_20260225_230607 (900/900 frames): raw frame-to-frame
  angle jumps up to 65 deg (shoulder twist, near-straight elbow ey ~ -14 deg
  = the predicted §7.3 conditioning); 3 Hz filter collapses jumps 10-30x,
  so they are depth noise (hip rms correction 12.4 mm), not solver issues.

- 2026-07-13: Unity editor silently stops the play-mode loop when it loses
  window focus AND can enter a paused state without an error — recordings
  or streams then freeze while everything else looks alive. Before any
  screen capture: check EditorApplication.isPaused, set
  Application.runInBackground = true, EditorPrefs InteractionMode = 1
  (No Throttling), and focus the Unity window (wmctrl -ia <id>).
- 2026-07-13: killing a nohup'd sender by its shell wrapper PID leaves the
  python child alive — a stale sender kept overwriting /dev/shm packets and
  masked held test poses. Use pkill -f <script> and verify with pgrep.
- 2026-07-13: real recording decodes to mean Euler (-0.7, -168.8, +1.7) —
  the ~11 deg yaw offset from 180 and small pitch/roll are camera extrinsics
  (sensor not square to the subject), to be absorbed by the camera->world
  conversion stage, not a bug in the frame construction.
- 2026-07-12: raw landmark jitter on recording_20260328_021733 is ~5-10 mm
  median frame-to-frame, hips noisiest (max 54 mm jumps, 12-13 Hampel
  glitches each); shoulders/hips glitchier than wrists — depth noise, not
  MediaPipe tracking noise, dominates.
- 2026-07-12: per-frame cost profile (heavy model, GPU, 640x480): inference
  6.5 ms, depth-to-color align 2.2 ms, everything else <0.2 ms — align is
  the only CPU-bound stage worth offloading if real-time ever needs it
  (CUDA-built librealsense supports GPU align; pip pyrealsense2 does not).
- 2026-07-12: ENSC498 reference pipeline stores landmark XYZ as float16
  (pose_toolkit/utils_fast.py) — ~1 mm quantization at 1.7 m range; any
  accuracy numbers derived from it inherit that floor. Ours uses float64.
- 2026-07-12: MediaPipe VIDEO mode requires strictly increasing integer-ms
  timestamps; bag playback timestamps can repeat/jitter, so the extractor
  clamps each timestamp to (last + 1) ms minimum.
- 2026-07-12: Depth is sampled at a single pixel per landmark
  (get_distance) — zero-depth returns are dropped as empty cells. Fine on
  recording_20260328_021733.bag (0 missing / 21,576 cells) but may need a
  neighborhood median on noisier recordings.

## 2026-07-28 — Writing v3
- v2 reference lists contained a genuine collision: [15] meant a different
  Dong & Payandeh paper in Chapter 1 (Appl. Sci. 8921) than in Chapter 3
  (Appl. Sci. 8737). Found mechanically while seeding references.md;
  resolved in the v3 renumbering pass (ch3 paper is now [39]).
- The v2 prose was already almost free of internal file names; the sweep
  found only /dev/shm (ch2, ch5), recording IDs (ch2, ch6), "bag"/"CSV"
  phrasing (ch2/3/4), synthetic dataset names in ch3's validation table,
  and shm channel names in ch5's packet table.
- The validator headline counts (21/21, 33/33, 20/20) all already existed in
  main-body prose (ch4, ch6, ch5 respectively), so shortening the Conclusion
  lost no numbers.

## R4 stage 2 (2026-08-25)
- ArUco PnP-vs-depth cross-check fails systematically on R4 desk
  (+80 mm) and object (+144 mm) markers; passed on R1/R3; cause open.
  Details: eval/reports/r4_stage2_validation.md finding 1.
- v1/integration/output unity logs were overwritten by the 07-24
  realtime session; pinned dataset/ copies are the matching pair
  (validator 20/20 after restore; backup in eval/output/backup_20260825).
- Gate-miss specimen on R4: left shoulder ~34-36 s keeps vis above 0.5
  while depth lands on background (z 1.3 -> 3.4 m).
- R4 desk marker is on a ~32 deg tilted stand (like R3); world frame
  is the tilted marker frame, gravity_up from calibration must be used
  for any height-above-table logic.

## R4 stages 3-5 (2026-08-25)
- The visibility gate cannot catch depth-substitution errors: 167
  right-wrist cells (15 percent of manipulation frames) are
  demonstrably wrong by segment length yet keep visibility above 0.7.
  Complementary segment-length gate needed (eval E-007).
- R4 grip is piecewise-rigid: within an episode |wrist-box-center|
  std 0.8-3.4 cm; regrips step the median 14.3 -> 17.8 -> 22.9 cm.
  Magnitude is the robust stage-2 metric (object rotation is 87
  percent ambiguity-resolved on R4).
- cv-extrap in angle space evaluated and REJECTED (worse than hold in
  most scenarios); sphere wrist recovery strong for bounded wrist-only
  gaps (p95 38 vs 66 deg) but needs a live elbow - R4's real occlusion
  blocks elbow+wrist together.
- R4 limb lengths are left-right symmetric, unlike R1's 4.7 cm forearm
  asymmetry; R1 right-forearm 0.185 m was likely camera-geometry bias.
- ROOT CAUSE of the R4 PnP-vs-depth failure (settled): the new desk
  and object marker prints are ~43.6 mm, not 50 mm (constant 1.145
  PnP/depth ratio; R1 ratio ~1.00). Exact post-hoc rescale applied
  (eval E-009, UNCERTAIN until ruler-confirmed); stages 3-5 numbers
  recomputed - right-hand drift collapsed to -0.01 cm/min.

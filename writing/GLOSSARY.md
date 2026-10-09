# Glossary

The only technical terms and abbreviations allowed in the thesis prose.
The chapter review loop (skill_set/thesis-revision-workflow.md) checks
every technical term and abbreviation in a chapter against this list,
alongside the rules in writing/WRITING_SKILL.md (blader/humanizer prose
skill since 2026-09-05). Terms are added here only when
they are established names a reader can look up; project-invented labels do
not belong in the thesis or in this list.

Conventions covered by this list:
- Hyphenated compounds formed from listed terms or from ordinary English
  words are allowed (marker-based, single-camera, Unity-based, end-to-end,
  per-user, two-stage, avatar-driven, object-conditioned, and the like);
  each part must be either a listed term or plain English.
- The thesis body uses Canadian spelling (colour, metre in prose); glossary
  entries written with American spelling (color frame) name the same terms.

## Fields, applications, and clinical terms

- bimanual
- imitation learning
- virtual reality (VR), augmented reality (AR)
- 2D, 3D
- Parkinson's disease
- amyotrophic lateral sclerosis (ALS)
- rehabilitation
- motion capture, markerless, marker-based
- consumer-grade (sensor class)
- vibrotactile glove

## Methods and models from the literature

- heavy variant, video mode (the BlazePose model size and its tracking mode)
- deep learning
- transistor scaling
- stroke (clinical), deficit (clinical)
- wearable sensor, wearables
- inertial sensor (a worn accelerometer and gyroscope unit)
- articulation (joint sense)
- parameterized model
- regress, regression (statistical sense)
- hierarchical
- camera ray
- motion replay
- occluded, unoccluded
- over-smooth, under-smooth
- instrumented glove
- Particle Swarm Optimization
- Iterative Closest Point (ICP)
- Gaussian, Gaussian Bayesian Network
- convolutional network
- transformer (neural architecture)
- state space model
- mesh recovery
- monocular
- keypoint
- inpainting
- mutual attention
- kinematic retargeting
- biomechanical constraint
- back-projection / back-projecting
- depth fusion
- landmark dropout
- synthetic masking
- causal (causal pipeline)
- InterHand2.6M, OakInk2, RGB2Hands, RePose (named systems/datasets)

## Systems, products, libraries

- bus (the hardware data connection used by a device)
- metadata (information describing a recording or an individual frame)

- gigabyte (GB), the storage and memory unit used in the hardware tables
- long-term support (LTS), the support designation used in the operating-system table

- MediaPipe (and MediaPipe Pose)
- BlazePose
- ArUco
- OpenCV
- Unity
- RealSense (Intel RealSense D435)
- RealSense Viewer
- FreeMoCap
- Kinect
- Python
- NumPy
- SciPy

## Sensing and imaging

- RGB, RGB-D
- depth frame, color frame, depth-to-color alignment
- depth window (the small pixel window around a landmark from which its depth sample is taken)
- point cloud
- intrinsics, extrinsics
- focal length, principal point (the pinhole intrinsics)
- imager (the left and right imager modules of the stereo camera)
- metric (measured in physical units: metric depth, metric 3D)
- registered (streams aligned pixel-to-pixel; same concept as depth-to-color alignment)
- deprojection
- pinhole camera model
- lens distortion
- inverse Brown-Conrady (the distortion model the colour stream declares)
- frame rate, fps
- field of view
- colour image / color image (same as color frame), depth image (same as depth frame)
- contour (image processing)
- binary grid (marker pattern)
- speckle (depth speckle)
- plumb (vertical by gravity)
- gravity-levelled, levelled (frame aligned with gravity; "leveled" in figure labels)
- invariant (unchanged under a transformation)
- bag file (recorded sensor session container)
- rosbag (the container format a bag file uses)
- z16 (16-bit depth pixel format), bgr8 (8-bit-per-channel colour pixel format)
- LZ4 (the chunk compression of the recorded session file)
- pixel, sub-pixel
- stereo matching, baseline, infrared projector, triangulation (how the stereo depth camera measures depth)
- calibration topic (the stream of the recorded session file that carries the sensor's factory calibration)
- region of interest (the image region a detector works on)

## Fiducial markers and object tracking

- fiducial marker
- marker ID (the identifier number encoded in a fiducial marker)
- marker dictionary (DICT_5X5_50)
- AprilTag (the fiducial system whose corner refinement the detector uses)
- IPPE (Infinitesimal Plane-based Pose Estimation)
- PnP (Perspective-n-Point)
- Rodrigues vector / Rodrigues form
- pose ambiguity (two-solution / two-lobe ambiguity); lobe (one of the two candidate poses of that ambiguity); discriminator (the rule that chooses between the two lobes)
- reprojection, reproject (projecting a recovered pose back into the image to compare with the detection)
- range (the length of a marker's translation vector, its straight-line distance from the camera)
- quadrilateral
- skew-symmetric matrix, matrix logarithm, trace (of a matrix), arc cosine (acos), affine (the standard matrix terms of the Rodrigues conversion)
- world anchor, world anchoring
- world origin, world frame (the desk-marker-anchored frame of Chapter 4)
- gravity reference (the wall marker's in-plane up axis, taken as the gravity direction)
- translation (the position part of a marker pose)
- chordal mean
- ground truth, ground-truth (not used in the thesis prose: the phrase
  appears only in the pinned evaluation reports under eval/reports. Every
  comparison names its kind of reference instead: physical reference,
  manual wrist label, synthetic exact reference, within-recording
  comparison)
- physical reference (a length the author measured with a tape or a ruler,
  such as the legs of the route the cube travels, the rail, and the
  wrist-to-marker distance of a normal single-hand grip)
- physical route (the author's tape measurement of the three legs the cube
  travels, 25.5, 3.5 and 37.5 centimetres; a physical reference, and not
  taken from the tracked trajectory)
- manual wrist label, the label (a point the author clicked on the colour
  image and deprojected with the aligned depth of the same frame; the only
  reference on the natural failure windows, and not exact anatomical truth)
- synthetic exact reference (an angle trajectory injected into a generator
  before the landmarks were produced, so the value the solver must return
  is known in advance)
- within-recording comparison (one output of the pipeline placed beside
  another output of the same recording: the unmasked solve, a line fitted
  to the tracked samples, or the offline pass against the causal path. It
  describes how consistent the reconstruction is with itself, and it is
  never called an accuracy or an error against physical truth)
- reference path (the phrase the plot legend of the Figure 7.4 schematic
  prints for the dashed polyline. That polyline is drawn from the tracked
  recording, the start from the parked mean and the rail corners from the
  line fitted to the slide, so the prose calls it "the drawn waypoints".
  The figure is pending regeneration from the physically measured route,
  which is the author's tape measurement of the physical route)
- track (a per-frame sequence of tracked positions; object track, landmark track)
- in-plane up axis (the up axis of a marker's own frame, lying in the marker plane)
- waypoint, the drawn waypoints (a point of the polyline the Chapter 7
  figures draw: the parked start of the rail recording and the depth,
  height and far end of the line fitted to the slide, or a held-still stop
  of the loop path. The drawn waypoints come from the tracked recording
  and are pending regeneration from the physically measured route, so the
  prose calls them the drawn waypoints and never a physical reference; the
  physical route is the author's tape measurement); station (a held-still
  stop of the loop path)
- polyline
- dwell
- handover (passing the object between hands)
- reconstruction (the rendered person-and-scene output)

## Human pose and kinematics

- joint coordinates (the joint angles as the coordinates of the kinematic model)
- landmark (pose landmark); L11 to L33 (MediaPipe landmark index notation, e.g. L16 = right wrist)
- visibility score
- visibility gate (the 0.50 threshold on the visibility score below which a landmark is written as missing)
- appearance-derived depth (the detector's own depth estimate, not used)
- kinematic solver (the angle computation of Chapter 3)
- kinematic model (the chain of Chapter 3 with its segment lengths, as the solver and the recovery use it)
- virtual sensor (the Unity camera placed at the calibrated sensor pose, Section 6.4)
- y-up camera frame {Camera'} (the camera frame with its y axis flipped
  upward, defined in Chapter 3; it keeps the optical centre of {Camera}
  and is not person-centred. It replaces the earlier name person space)
- sensor space (the camera frame, same as camera coordinates)
- {Camera} (the raw camera frame of Section 2.2.1)
- {World} (the desk-marker world frame fixed by the calibration of Section 2.2.2)
- {Unity} (the swapped-axis frame the receiver works in, Chapter 6)
- {Scene} (the gravity-levelled, floor-placed display frame of Chapter 6)
- {MappedMarker} (the object marker frame with the mapped axes of Chapter 5)
- observability (how far the available measurements determine a quantity)
- pose ambiguity, single-view ambiguity
- state estimation, estimator (the stage that carries state between frames)
- registration (bringing a measurement into a common frame; distinct from
  the depth-to-colour registration of the aligned streams)
- annotator (the person who clicks the manual wrist labels)
- excursion (how far a landmark travels from its first position in a window)
- forearm twist (the twist angle about the upper-arm axis, Chapter 3)
- bone head (the origin end of a bone in the humanoid rig)
- spine-side vector (the L24-to-L12 input vector of the torso frame, defined in Chapter 3)
- failure detector (the tracking-failure detectors of Chapter 5)
- closing step (the morphological closing that bridges gaps of up to five frames between detector fires when the per-entity failure masks are formed)
- entity mask (the per-frame rejected/accepted mask of one entity: an arm or the torso)
- line-consistency check (the torso line-angle detector applied inside the torso repair)
- outage (a stretch of frames over which a landmark is missing; a masked window in the synthetic evaluation)
- skeleton
- torso frame, root frame, reference frame, local frame
- coordinate system, coordinate frame
- handedness (left-handed, right-handed)
- change of basis
- homogeneous transformation matrix
- rotation matrix, SO(3)
- proper rotation (determinant +1)
- determinant, transpose
- reflection (geometric sense)
- orthonormal, orthogonal (non-orthogonal)
- invertible
- conjugation (of a rotation, mapping it across a change of frame)
- normalize, normalization (of a vector)
- arctangent, arcsine
- quadrant
- Euler angles (ZXY order)
- gimbal lock, singularity
- yaw, pitch, roll
- azimuth, elevation (angle names)
- degeneracy, degenerate (of a configuration)
- collinear, non-collinear
- closed form
- least squares
- law of cosines
- clip, clipped (a value limited to its valid range)
- well conditioned, ill conditioned
- machine precision, floating point
- threshold, thresholding
- quaternion
- swing-twist decomposition
- degree of freedom (DOF)
- forward kinematics, inverse kinematics (IK)
- two-link inverse kinematics
- swivel (the rotation of the arm about the line from the shoulder to the wrist, which the landmarks do not fix)
- kinematic chain
- PUMA robot (PUMA-style schematic, PUMA convention)
- revolute joint (revolute-joint cylinder in schematics)
- spherical joint
- shoulder, elbow, wrist, hip, pelvis, shoulder girdle (anatomical names)
- flexion, extension
- pronation
- internal rotation, external rotation
- forearm, upper arm, trunk, chest, spine, thigh (ordinary anatomical words)
- mannequin
- sagittal (mirror plane)
- ball joint, hinge joint
- joint group (the root, a shoulder swing, a shoulder twist or an elbow: the angles that share one live bit and one state)
- quasi-static
- regrasp
- spirit level (the levelling instrument)
- rigid body transformation
- manipulator (robot arm)
- optical centre
- Pipeline A / the landmark branch, Pipeline B / the marker branch (the two processing pipelines, named in Chapter 2)
- T-pose
- avatar, humanoid rig, bone

## Pose recovery (the names Chapter 5 establishes)

- holding state (the per-hand state that says whether that hand is holding the object)
- grip episode (the run of consecutive frames over which one hand holds the object, from entry into the holding state to exit from it)
- recovery layer, the layer (the pose recovery stage of Chapter 5 around the kinematic solver)
- hand-object offset (the position of the wrist in the object's own axes while the hand holds it; h in Chapter 5)
- failure mask (the per-frame mask of one arm or of the torso set by the failure detectors; same thing as an entity mask)
- mask cleaning (the two passes over a failure mask: gaps of up to five frames closed, runs shorter than five frames dropped)
- source flag (the flag a landmark sample carries from Chapter 2: measured, filled in, or missing)
- hold radius (the wrist-to-object distance inside which a hand counts as holding)
- release radius (the wider wrist-to-object distance beyond which a cleanly measured wrist counts as released)
- acquisition (the detector that reports the landmark detector's own flag on a sample)
- segment length (the detector that tests an upper arm or a forearm against its calibrated length)
- torso line angle (the detector that tests the hip line against the shoulder line)
- torso width ratio (the detector that tests shoulder width against hip width)
- grip plausibility (the detector that tests a measured wrist against the object its hand holds)
- landmark step (the distance a landmark moved between two consecutive frames)
- direction memory (the running average of the direction of a body segment, carried between frames)
- depth memory (the running average of the depth of a torso landmark, carried between frames; unlike the direction memories it has no staleness limit)
- depth-jump gate (the test that sends a torso landmark into the ray repair when its measured depth leaves the depth memory by more than 10 centimetres)
- shoulder-depth gate (the test that sends a hip into the ray repair when it sits more than 15 centimetres nearer the camera than the shoulder midpoint; applied only to a hip the first two gates passed)
- hip depth preparation (the condensed thesis's name for the torso preprocessing of Section 2.6 and Appendix G: the four checks in order, the depth memory, the replacement of a rejected point on its retained camera ray, and the whole-pair repair)
- shoulder-depth check (the name Section 2.6, Appendix G and Chapter 9 give the shoulder-depth gate and its replacement at the shoulder-midpoint depth)
- live bit (the per-group flag in the person record that says whether the group was measured on this frame, Section 6.1)
- hold-last solve (Chapter 7's name for the baseline that holds the last solved angles through a failure window; the plain solve applies no failure mask, the masked solve removes the flagged arm without the object, the recovery solve removes it and uses the object)
- retained ray (the camera ray through a landmark pixel, kept when the depth sample is rejected; a point is p divided by its camera depth)
- whole-pair repair (Appendix G: both endpoints of a hip or shoulder pair rebuilt around the midpoint of their remembered-depth ray points with the calibrated width)
- ray repair (sliding a torso landmark along its camera ray to a chosen depth, keeping its pixel)
- width test (the torso-repair test that compares a hip-to-hip or shoulder-to-shoulder width with its calibrated median)
- torso diagonal (the distance from one hip or shoulder to the midpoint of the opposite pair, calibrated per recording and used to decide which endpoint of a suspect pair to gate)
- pair rebuild (the repair that places both landmarks of a gated pair symmetrically about the midpoint of their ray-repaired positions, at the calibrated width, along the pair's direction memory)
- calibrated width (the median hip-to-hip or shoulder-to-shoulder separation of a recording over its calibration frames)
- occluder (the surface between the camera and the body whose depth the sensor returns instead of the body's)
- hysteresis (a test with separate trip and release thresholds, so that a condition just under the trip level does not release it)
- gate, gated (to reject a measured landmark as wrong and replace it; distinct from the visibility gate, which rejects on the detector's own score)
- torso repair (the whole of Section 5.5: the three gates and the ray repair)
- evaluated span (the frames of a recording after the warm-up, over which failure percentages are quoted)
- eligibility rule (the conditions a frame must meet before a synthetic outage may be placed on it)
- arm travel (the angle the reference arm turns through during a synthetic outage)
- full reach (the combined upper-arm and forearm length; a wrist distance is quoted as a fraction of it)
- clean frame (a frame no failure detector rejects; a clean median is a median over such frames)
- twist hold (the Section 5.5 rule that holds the shoulder twist while the elbow is nearly straight)
- cleaning rule (the Chapter 4 rule that discards an object sample the slow task cannot produce)
- grip tracker (the online form of the grip-episode logic in the live path, Chapter 8)
- live structure, live path (the real-time system of Chapter 8: the structure is its arrangement of processes, the path the route a frame takes through them)
- causal structure, causal path (the same real-time system and its output,
  read as the arrangement that uses no future sample: the causal structure
  is the arrangement of processes of Chapter 8 and the causal path is what
  it produces. Synonyms of live structure and live path)
- cleaning step (Chapter 4's name for the cleaning rule)
- rest reference (the resting object pose the carried test compares against)
- measured (output state: every landmark the joint group needs was measured on this frame)
- held (output state: the joint group keeps the value it last had)
- constrained (output state: the joint group was solved with a rebuilt landmark, or its output was rate limited)

## Signal processing and statistics

- mathematical operator, rotation operator (an operation applied to a vector)
- amplitude, amplitude gain (signal size and the output-to-input amplitude ratio)

- moving average, monotone (monotone response), attenuate, attenuation, backfill (filling a leading gap backward in time)
- Hampel filter (Hampel identifier / Hampel test / despike)
- Butterworth filter
- zero-phase filtering (forward-backward)
- cutoff frequency, Hz
- Savitzky-Golay filter
- One Euro filter
- low-pass filter
- gain (of a recursive update: the weight of the new sample)
- first-order recursive update (the exponential average of equation (5.4))
- passband, phase delay, broadband noise
- median absolute deviation (MAD)
- robust standard deviation (the MAD scaled by 1.4826)
- rolling median (median of a sliding window)
- outlier, despiking
- pose recovery (this thesis's recovery stage)
- gap bridging / gap filling, interpolation
- median, mean, standard deviation
- histogram mode (the level at which the tracked heights gather: one peak
  of the histogram of a tracked coordinate, as the desk level and the rail
  level of Section 7.2)
- time series
- trajectory
- polynomial
- planar
- ripple (filter response)
- smoother (a smoothing filter)
- preprocessing
- percentile, p95
- residual (the difference that remains after a fit or a round trip)
- point estimate (a single value reported without an uncertainty)
- Bayesian (in the sense of Bayesian inference; see also Gaussian Bayesian Network)
- RMS (root mean square)
- jitter
- atan2
- cross product, dot product, unit vector, Euclidean norm
- SVD (singular value decomposition)
- principal component analysis (PCA), eigenvector, eigenvalue
- covariance, covariance matrix
- identity matrix
- scalar
- centred difference (a derivative taken from samples on both sides)
- transverse (across the fitted line, as opposed to along it)
- rank (the position of a value in a sorted sample)
- robust scale (the robust standard deviation computed over a rolling window)

## Systems and integration

- UDP (User Datagram Protocol)
- packet
- latency
- pipeline
- streaming stage, the merger (the stage of Chapter 6 that pairs the two output streams at a common render time and sends them to Unity)
- live validator (the tool that pairs the frames of the causal path with
  the frames of the offline pass and reports their differences, Section 8.3)
- capture process (the one process of Chapter 6 that opens the sensor or the recording and publishes aligned frames)
- shared memory, frame buffer (the shared-memory ring of captured frames with one writer and many readers, Section 6.1)
- GPU (graphics processing unit), GPU delegate
- neural network
- thread, single thread
- throughput
- megabyte (MB)
- stream profile (the resolution, format and rate a sensor stream is opened with)
- topic (a named stream inside a bag file), message
- segmentation (the detector's person mask)
- zero return (a depth pixel the sensor reports with no range)
- decode (recovering a marker's identity from its printed pattern)
- heuristic
- fallback (the path taken when the preferred estimate is unavailable)
- expiry (the age at which a remembered value stops being used)
- tolerance, trigger (the threshold at which a check fires)
- systems engineering
- interpretable, interpretability
- ONNX Runtime, RTMPose-m, COCO-17 (the future-work detector of Chapter 10)
- record (a fixed-layout block of shared memory: person record, object record, scene record, combined record)
- sequence counter, lock-free (the odd/even counter protocol that protects a record while it is written)
- byte order, payload (the fixed layout of a record)
- slot (one fixed-size cell of the frame buffer holding one aligned colour and depth pair; frame n goes to slot n modulo 8)
- arrival time (the time a frame reached the computer, on the computer's clock, stored beside the hardware timestamp in a slot)
- frame index (the publication number of a captured frame, shared by every record that describes it)
- optical axis (the line through the camera centre along which depth is measured)
- mesh (the avatar's skin surface in Unity)
- contended (a counter is contended when a reader may catch it mid-write)
- tabletop plane (the plane fitted to the desk top in the calibration of Section 2.2.2)
- tabletop model (the horizontal plane through the tabletop point that the
  implementation uses for height measurements, with its normal set by the
  calibrated gravity direction; distinct from the fitted tabletop plane)
- card, desk card, plate (a marker card of the scene and the plate that draws it in Unity)
- inset (the picture-in-picture view of the virtual sensor camera in the Unity scene)
- mid-shoulder (variant of shoulder midpoint in the trunk length of Section 6.3)
- header (the fixed block at the start of the frame buffer that carries the image size, the intrinsics, the clock origin and the count of frames published)
- byte offset, memory block (the position of a field inside a record, and a record drawn as a block of memory)
- modulo (the remainder rule that assigns frame n to slot n modulo 8)
- dropout (a frame on which a stream has no usable sample, as distinct from the landmark dropout of Chapter 5)
- resampling (the merger's interpolation between two adjacent samples when the render time falls between them)
- display frame, display axes (the Unity frame of Section 6.2)
- parent node (the one node under which the receiver places the whole reconstruction, Section 6.4)
- lapped (a reader that falls more than eight frames behind the writer of the frame buffer)
- torn copy (a record copied while a write was in progress, detected by the sequence counter and discarded)
- bridge flag (the merger's flag that an interpolation crossed a real dropout rather than routine resampling)
- render time, tick (the fixed-rate output step of the merger and the instant it renders)
- session clock, session timestamp, hardware timestamp (the sensor's own time base and the per-frame time derived from it)
- blended (merger state: a stream ramping back over a few ticks after a long gap)
- shortest arc (interpolation of an orientation along the shortest rotation between two samples)
- receiver, receiver script (the Unity-side script of Chapter 6 that reads the records and drives the scene)
- the swap S, the flip F (the world-to-Unity axis exchange of equation (6.1) and the y flip of equation (3.1))
- anchor node (the static Unity node at the calibrated camera pose through which every person-record value passes, Section 6.2)
- display smoother (the output-only low-pass and rate cap of Section 6.3)
- rest pose, rest rotation (of a rig bone, captured when the scene starts)
- axis-angle (a rotation about a named axis by an angle)
- face normal (the direction perpendicular to a marker's printed face)
- real time, offline
- occlusion
- calibration

## Document and citation

- IEEE (citation style)
- CEFR C1 (vocabulary level, used by the review loop only)


## Parked terms (2026-09-06)

The torso repair of V7 Chapter 5 Section 5.5 is parked in
writing/v8/CH5_PARKED.md on the user's plan (the torso is assumed
measured on every frame). Its terms stay defined here for the V7 text
but do not appear in the v8 chapters or in the condensed thesis: torso
repair, ray repair, depth memory, depth-jump gate, shoulder-depth gate,
line-consistency check (the v8 name for the test is the line-angle
detector of Section 5.2), width test, torso diagonal, pair rebuild,
calibrated width, occluder. Decision D2 (2026-09-07): the condensed
thesis describes the hip-depth step as "the hip depth preparation" in
Section 2.6 and Appendix G (effect reported in Section 7.4), and those
texts use depth memory, calibrated width, shoulder-depth check, retained
ray and whole-pair repair as defined above; torso repair, ray repair,
depth-jump gate, line-consistency check, width test, torso diagonal,
pair rebuild and occluder stay parked.

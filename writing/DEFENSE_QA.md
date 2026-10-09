# Defense preparation: coordinate conventions and implementation questions

Prepared 2026-08-31 from the discussion of the V7 round. Each entry is
a question the committee may ask, a short answer to speak, and backup
layers for follow-ups.

## Q1. Why does the system work in a left-handed coordinate frame? Is that necessary?

The 20-second answer:
"The handedness of a coordinate frame is a convention, and no physical
result depends on it. We chose the left-handed, y-up frame because that
is the native convention of the animation system that consumes our
output, Unity. Solving the kinematics directly in the consumer's frame
means the thirteen angles we compute per frame are exactly the angles
the avatar applies, with no conversion layer at the boundary. The cost
of entering that frame is one sign flip on each measured point."

If they push, "why not just convert at the end?":
"Because points and rotations convert differently. A point crosses a
handedness change with a single sign flip, which is trivial. A rotation
crosses it by conjugation, and every Euler angle's sign convention
changes with it; that conversion layer is exactly where sign errors
hide. So we placed the cheap conversion (points, at the entry) and
eliminated the risky one (angles, at the exit). All rotation matrices
are then built from already-converted points, so every matrix in the
pipeline is proper and directly usable."

If they push further, "so the model depends on Unity?":
"Only the frame convention does, not the model. The angles themselves
are defined anatomically: swing azimuth, elevation, twist, elbow
flexion, each with a physical zero at the T-pose. The closed-form
solver would be identical in structure in a right-handed frame; only
sign conventions would differ. If the renderer were replaced by a
right-handed one, the change would be the entry flip and the export,
not the kinematic model."

Supporting fact to volunteer (shows the choice is principled): the
object-tracking branch of the same system does the opposite. It stays
in the right-handed desk-marker frame through all of its calibration,
tracking, and ground-truth evaluation, because its consumers are
physical desk geometry (the drawn path, the rail), and it converts to
the rendering frame only at the export point. Both branches follow one
rule: do the math in the frame your output lives in, and cross
handedness at the boundary where the crossing is cheapest.

Closing one-liner: "Handedness is like choosing the sign convention
for current in a circuit. Nothing measurable depends on it, but
picking the one your instruments use and staying consistent removes a
whole class of bookkeeping errors."

## Q2. How do the two branches handle coordinates differently?

Person branch (Pipeline A): landmarks arrive in the RealSense camera
frame (right-handed, x image-right, y down, z forward). Immediately
after the depth lifting, each point is mapped by q = F p with
F = diag(1, -1, 1); only y flips sign. That single reflection
(det F = -1) gives the left-handed, y-up person space matching Unity.
All kinematics run there. The flip applies to points only, never to
rotation matrices: rotations are built from already-flipped points, so
they come out proper. Implementation: unity_from_sensor() in
v1/kinematics/root_frame.py; thesis Section 3.1, equation (3.1).

Object branch (Pipeline B): ArUco planar PnP gives marker poses in the
camera frame; everything is re-expressed relative to the frozen desk
marker pose by T-matrix composition and STAYS right-handed through
filtering, cleaning, offset fitting, and all ground-truth evaluation.
Conversion to Unity happens only at the export: WORLD_TO_UNITY swaps
the y and z axes (det -1, marker z out of the desk face becomes Unity
up); points map as p' = P p, rotations by conjugation R' = P R P.
Implementation: v1/aruco/frames.py.

Where the branches meet (object-conditioned wrist recovery, grip
offset fit), the object pose is mapped into the person/solver space
first, so the solver only ever sees one convention.

## Q3. Would converting the person branch to work right-handed be a big change?

Yes, and it buys nothing. The equations themselves change, not just
plumbing: under conjugation by diag(1, -1, 1) the x- and z-rotation
angles flip sign, so every hand-tuned sign in Chapter 3 moves (the
cross-product orderings of the torso frame, elevation as asin of the
y component, the twist zero convention, the left-arm mirror, the
T-pose reference decode, the gimbal-lock conventions). Code blast
radius: root_frame.py, shoulder.py, the occlusion_ext.py robust layer,
their validators with hardcoded expected angles, recovery_core,
the offset fit, the v2 real-time path, the Unity sender, thesis
Chapter 3 end to end, Appendices C and D, and re-verification of every
Chapter 7 number. The physical output would be identical. The current
asymmetry is principled (see Q1), so the recommendation is to keep it.

Journal plan (decided 2026-08-31, recorded as D21 in
writing/v7/DECISIONS.md): a journal version of this work presents the
model in the conventional right-handed frame. That is a
presentation-level change only: the equations are re-derived on paper
with the right-handed sign conventions and the rendering conversion is
stated once at the boundary, while the implementation, its validators,
and every measured number stay as they are.

## Q5. The camera-frame figure was drawn wrong for months. Why were the reconstructions still almost correct?

What was wrong, precisely: two things, both documentation, neither
code. (1) The old figure drew the camera frame on a front view of the
sensor with x to the reader's right; the librealsense convention is
defined from behind the camera, so a front view must show image-right
on the reader's left, and the module labels mirror as well. (2) The
figure implied that the flipped person space IS the Unity frame; in
the running system person space is anchored at the camera while the
Unity world is anchored at the desk marker, and the body root frame is
a third, measured frame that rides the torso (about 180 degrees of yaw
from the world, since the subject faces the sensor).

Why nothing broke: the code never read the figure. The pipeline's
camera frame comes from the pinhole projection equations (x from
image column, y from image row, z from depth), so every computed
number used the correct convention even while the drawing of it was
mirrored. A figure error has no execution path into the solve.

Why the frame differences do not hurt the reconstruction (the honest
answer to "how does the experiment look so good"):
1. Joint angles are relative. Every angle is defined child-to-parent,
   so the pose shape is invariant under any global rotation or
   translation of the whole person. A global frame mismatch could
   only misplace or tilt the WHOLE body, never bend an elbow wrongly.
2. The root is placed through the calibrated camera pose. The
   reconstruction maps the camera-anchored person into the
   desk-anchored world with the calibration of Chapter 4, composed
   once per frame; the frames are related, not equated.
3. The two handedness conversions cancel. The person branch's point
   flip (det -1) and the object branch's axis swap (det -1) are both
   reflections; composed through the calibrated pose they form a
   proper rotation, so no net mirror reaches the rendered scene.

The evidence is on record. Figure 3.2(b) is a real Unity editor
capture of the rig's root node with its axes drawn, axis-aligned with
the world in the reference T-pose, and the chapter paragraph beside it
states the contrast with the measured root frame (yaw 178.13 degrees
at the worked-example frame, printed in Section 3.5). A capture of the
running reconstruction with the measured root frame and the world
frame drawn together is kept in the figure sources
(writing/v7/figures/src/r5_unity_rootframe_f270.png).

## Q4. Is the kinematic model our own code? Does a journal publication force redefining it?

Own code: yes. The kinematic solver (v1/kinematics: root_frame.py,
shoulder.py, occlusion_ext.py) is pure NumPy, written closed form; no
scipy.spatial.transform, no quaternion library (project policy:
matrices plus Unity ZXY Euler only). scipy appears in exactly one
place: the standard signal filters (Butterworth, Savitzky-Golay,
rolling median) in the filtering stage, which are textbook methods and
cited as such. MediaPipe is a third-party input (landmark detector);
Unity is the output (renderer).

Journal answer: no redefinition. The model is defined by the equations
(Chapter 3, equations 3.1-3.24 including the homogeneous T
formulation, plus the recovery mathematics of Chapter 5), not by the
code; the code implements them and the validators prove the two agree
(round-trip identity at 1e-9 degrees, synthetic oracles, the occlusion
check suite). A paper presents the same equations compressed. What a
journal would add is repackaging and stronger evidence, not new
mathematics: condensed notation (the T-matrix formulation aligns with
standard robotics notation), positioning against related work and
baselines (raw MediaPipe world landmarks; possibly the RTMPose
exploration track), and broader evaluation (more participants and
trials; the occlusion / no-occlusion scenario separation is exactly
the controlled-evaluation shape journals expect).

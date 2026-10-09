# V7 supervisor comments, round of 2026-08-31 (Chapter 3)

Every comment from the supervisor's message on the assembled V7,
mapped to its target and action. Numbering continues from
PROF_COMMENTS_ROUND2.md (C1-C14). Scope: all comments target Chapter 3
(Kinematic Modeling). Overall verdict in the same message: "Other than
this, the content looks okay." Per the user's direction, the fixes go
into V7 in place; no V8 is opened.

## C15. Show the homogeneous T matrix combining R and t
"You should also show the T matrix which combines both R and t in one
representation. For example, equation 3.2 is valid when the origin of
both child and parent are the same location. You should show the
corresponding T matrix here as well."
- Target: Section 3.1, the rigid-transformation paragraph and equation
  (3.2) (the rotation-only mapping v_local = R^T v).
- Action: display the 4x4 block matrix T = [[R, t],[0, 1]] and its
  action on a homogeneous point where R and t are introduced; at
  equation (3.2), state explicitly that the rotation-only form applies
  to directions (and to points only when child and parent share an
  origin), and display the corresponding inverse-T form
  p_child = R^T (p - t) for points.
- Status: EXECUTED (build_ch3.py; equations renumbered).

## C16. Define the T matrices between the frames of Figure 3.3
"Referring to Figure 3.3, you should also define the T matrices between
the various frames. For example, T of the shoulder about the root
(torso) frame, elbow with respect to the shoulder and .. This makes it
clear that each frame is different from the other in terms of relative
rotation and position of their origin."
- Target: end of Section 3.1, at the chain figure (chain photo).
- Action: define the three relative transformations of the right-arm
  chain as block matrices - root w.r.t. person space, shoulder w.r.t.
  root, elbow w.r.t. shoulder - each with its own rotation and origin
  offset, and show the chain composition product.
- Status: EXECUTED.

## C17. State the mapping logic before the details
"Then it is clear when you mention that when you measure the landmark
position of say the shoulder with respect to the sensor frame, you can
use these relative T matrices to obtain for example, the position of
the shoulder landmark with respect to the torso (root frame). As you
have it, you do not make this clear in explaining the logic before you
go over the details."
- Target: Section 3.1, immediately after the chain T definitions.
- Action: a logic paragraph before any derivation: every landmark is
  measured in the sensor frame; the relative T matrices carry it into
  the frame where its joint is solved (shoulder landmark into the root
  frame, elbow landmark into the shoulder frame, wrist landmark into
  the elbow frame), with the inverse-T mapping displayed.
- Status: EXECUTED.

## C18. T matrix at equation (3.7) - root w.r.t. sensor
"Same for equation 3.7. You should define the T matrix here as well
which defines the relative position and orientation of the root frame
with respect to the sensor frame."
- Target: Section 3.2.2, the assembled root matrix (old equation 3.7).
- Action: immediately after the root rotation and origin are named,
  display T_root = [[R_root, p24],[0, 1]], the pose of the root frame
  with respect to person space (the sensor frame with y flipped).
- Status: EXECUTED.

## C19. T matrix of the shoulder frame w.r.t. the root
"Same goes in the section about the shoulder T matrix with respect to
the root."
- Target: Section 3.3.3 (Establishing Local Arm Frames).
- Action: display the shoulder frame's transformation w.r.t. the root
  (identity rotation, origin offset R_root^T (p12 - p24)) and the
  elbow frame's transformation w.r.t. the shoulder frame (solved
  shoulder rotation, origin offset R_root^T (p14 - p12)), completing
  the chain of C16.
- Status: EXECUTED.

## C20. Show each T matrix numerically in the worked example
"Then in the numerical section, you should show how each of these T
matrices look like."
- Target: Section 3.5 Worked Example.
- Action: print the numeric 4x4 T of the root (from R_root and p24),
  of the shoulder w.r.t. the root, and of the elbow w.r.t. the
  shoulder, on the worked-example frame; numbers produced by
  ch3_numbers.py (extended to print the block matrices).
- Status: EXECUTED.

## C21. Information-flow diagram at the start of the chapter
"I also think that at the beginning of this chapter, you should draw a
visual information flow diagram. This way, the reader can clearly see
how each sections come together. For example, you have raw/calibrated
information from the landmarks of torso and arms coming in. The torso
landmark are used to establish the T matrix of the torso frame with
respect to the sensor frame. The shoulder landmarks + T of the root is
used to map the shoulder landmark with respect to the root ... So use
AI tools to create this visual data flow where the reader can then get
a better idea of the process."
- Target: opening of Chapter 3, before Section 3.1.
- Action: new first figure of the chapter (make_ch3_flow_fig.py ->
  ch3_fig_flow.png): landmarks enter from the sensing stage; torso
  landmarks build T of the root w.r.t. the sensor frame; the elbow
  landmark plus the root T resolves the shoulder angles in the root
  frame; the wrist landmark plus the shoulder chain resolves the
  elbow angle in the elbow frame; the wrist stays a tracked point;
  outputs are the thirteen angles of Section 3.5. Figure numbers in
  the chapter shift by one.
- Status: EXECUTED.

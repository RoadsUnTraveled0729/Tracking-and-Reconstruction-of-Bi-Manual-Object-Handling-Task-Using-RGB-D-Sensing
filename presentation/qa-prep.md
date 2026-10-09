# Q&A preparation

Currency note (2026-10-08): These answers and backup references belong to
the original V6-era presentation. They are preserved without rebinding old
slide or thesis-page pointers. Use
[the final presentation README](defense_2026/README.md) for the current
English outline and QA guide; the current compiled thesis is documented in
[writing/v9/README.md](../writing/v9/README.md).

One section per backup category. Each question: an honest 2-3 sentence
answer, then where the full answer lives (thesis section and backup slide).
Honesty rule: if the thesis does not support an answer, the response is
"we did not test that" plus what we would expect, never a bluff.

## 1. Assumptions

**Q: You treat the torso as rigid. How wrong is that, and what does it cost?**
Three torso landmarks cannot separate the pelvis from the upper trunk, so
the model treats the trunk as one plate and a forward lean pitches the root
frame with it. We did not measure the error against an articulated-spine
reference because no such reference exists in the data; the limitation is
declared and the fix is more torso landmarks.
Full answer: thesis 3.2.1, 8.1; backup "Assumptions I".

**Q: What if the wall is not actually plumb?**
The wall's plumbness is the single physical assumption of the setup, and
gravity is derived from it. The depth channel supplies a deliberately
coarse seed whose calibrated angle to the wall gravity is measured at
5.03 degrees, well inside the seed's 10 degree requirement; a grossly
tilted wall would have pushed that measured angle far outside it.
Full answer: thesis 4.2.2; backup "Assumptions I".

**Q: Why is calibrating the anchor once enough? Cameras and desks move.**
Measured over the session, the desk marker's detected pose drifts only
0.20 mm and 0.088 degrees at the 95th percentile, so freezing is justified
for a session. A bumped marker would currently be handled by convention,
not detected; automatic detection is future work with a wide measured
margin to threshold against.
Full answer: thesis 4.2.1, 8.3.4; backup "Assumptions I/II".

**Q: The rigid-grip assumption drives your headline number. How valid is it?**
For the fully visible right hand the grip vector is constant to under 2 cm
per axis over 249 frames, which validates the model where sight lines are
clean. For the left hand the spread is 2.5 to 3.8 cm, inflated by a
mid-recording regrip and occlusion, so the left-hand 4.6 cm figure is an
upper bound on pipeline error, not a measurement of it.
Full answer: thesis 6.5, 8.1; backup "Assumptions II"; Table 6.4.

## 2. Why this approach

**Q: Why not just use a motion capture system as ground truth?**
The goal was a system requiring no laboratory: one commodity camera and
paper markers. That removed external ground truth, so the evaluation was
designed around independence instead: two chains resting on different
physics, whose agreement cannot be circular.
Full answer: thesis Ch1, 6.5; backup "Design decisions I".

**Q: Why ArUco markers and not a learned object detector?**
The witness pipeline must be independent of the estimation pipeline, and a
second learned detector would share failure modes with the first. Corner
geometry on a printed square is a different physical measurement principle,
which is exactly what makes the cross-pipeline agreement evidence.
Full answer: thesis 4.1; backup "Design decisions II".

**Q: Why shared memory instead of something standard like ROS or gRPC?**
The requirement is one machine, one writer, one reader, newest frame wins.
A seqlock-protected shared memory file does that with a ten microsecond
write and no dependencies, and the identical packet also runs over UDP as
the drop-in for cross-machine setups.
Full answer: thesis 5.1, 8.3.2; backup "Design decisions I" and the
transport diagram.

**Q: Why didn't you GPU-accelerate or vectorize the live solver?**
The deployed solver costs 99 microseconds against a 33.3 ms budget, under
one percent, so no implementation choice can be visible live. Vectorization
pays only in offline batch, where it delivers about 170 times the
throughput, and that variant exists for reprocessing.
Full answer: thesis 7.2, Table 7.2; backup "Solver benchmark".

**Q: Why a zero-phase filter offline if it cannot run live?**
Offline, filtering forward and backward gives zero net phase shift, so
motion peaks stay where they happened; the measured resting shake drops
from 10.2 to 1.9 mm with fast wrist motion left in place. Live, causality
forbids it, so the One Euro filter substitutes at a measured cost.
Full answer: thesis 2.1.5, 6.3, 7.4; backup "Design decisions I/II".

## 3. What if changed

**Q: What happens with a different camera position?**
That was measured, not assumed: the same scene was recorded from the desk
edge and from a high mount, and the desk-edge camera wins every stability
metric (wall stability 5.8 vs 28.3 mm p95). The mechanism is the viewing
angle onto the flat anchor marker, so placement relative to the anchor
matters more than marker size.
Full answer: thesis 6.2, Table 6.2; backup "Camera placement experiment".

**Q: Would this work on a different person?**
We did not test other subjects; the evaluation is a single subject and
session, and that is declared as a limitation. Joint angles transfer across
body proportions by design, so we would expect the pipeline to work, but
per-subject accuracy numbers would need new recordings.
Full answer: thesis 8.1; backup "Sensitivity: what was not tested".

**Q: What if the object were smaller, or the marker partly covered?**
Marker pose quality is a function of subtended image size: at 32 pixels the
wall marker is the measured worst case, where the two pose lobes stop being
separable by reprojection error and a gravity-seeded continuity policy is
needed. A smaller carried marker would move toward that regime; we did not
test one.
Full answer: thesis 4.2, 8.1, Appendix D; backup "Sensitivity".

**Q: Could it run at 60 or 90 fps?**
Untested. The sensor offers those modes at reduced resolution, and the
latency budget shows the mathematics would follow easily; the pose
detector's inference time is the one stage that would need re-validation.
Full answer: thesis 8.3.1; backup "Sensitivity: what was not tested".

## 4. Full derivations

**Q: Walk me through the root frame. Why the second cross product?**
The hip line is the one direction the three points define unambiguously,
and the spine-side vector is generally not perpendicular to it (85.4
degrees at frame 100), so using it as an axis would skew the frame. The
first cross product discards its parallel component; the second guarantees
an exactly orthonormal frame in every measured pose.
Full answer: thesis 3.2.2; backup "Root frame construction".

**Q: Why must the twist be innermost in the shoulder decomposition?**
A rotation about x leaves the x axis fixed, so with twist innermost the
arm direction depends on swing alone and the twist is exactly the roll the
elbow position cannot see. Outermost, the twist axis would stop being the
arm axis as soon as the arm swings.
Full answer: thesis 3.4.2; backup "Swing, twist, elbow".

**Q: How do you know the solver is correct?**
Every construction was validated against six synthetic datasets with known
injected angles pushed through the full pipeline in the extractor's own
format; the worst decode error is 2.8e-13 degrees. On real data the solved
angles reconstruct both measured segment directions to 6.4e-14 degrees at
worst, so the solve is an exact inverse; accuracy against reality is the
separate cross-pipeline result.
Full answer: thesis 3.4.5; backup section 4.

**Q: Why does det(M) = +1 matter for the anchor transform?**
The person-space flip and the Unity swap each have determinant minus one,
and the calibrated camera rotation has plus one, so the composition is a
proper rotation: the person maps into the scene with no residual mirror
image. The physical check is that M reproduces exactly the calibrated
5.03 degree angle measured between the depth-fitted seed and the wall
gravity, as a pure rotation must.
Full answer: thesis 5.2.1; backup "The anchor transform".

## 5. Extensions

**Q: What is the concrete next step for occlusion?**
Replace hold-last with model-based estimation: the laboratory's Gaussian
Bayesian Network framework already recovers occluded hand configurations,
and the upper-body extension has its hooks in place (the solver isolates
unobservable angles, the live mask marks them). The synthetic occlusion
scenarios come with exact ground truth and are the ready benchmark.
Full answer: thesis 8.3.5; backup "Bayesian recovery of occluded joints".

**Q: Could this scale to two people passing an object?**
The object instrument and the evaluation logic carry over: one marked
object could grade two people's hands in turn. The current pose detector
is single-person, so multi-person detection, identity association, and one
anchor per person would be needed; we did not build that.
Full answer: thesis 8.2; backup "Multi-person and display-path extensions".

**Q: When does the hand model come in?**
The system sees wrists, not grasps: finger configuration, contact points,
and grip force are invisible today. The laboratory's hand framework is the
natural next instrument, and the arm chain is structured to accept it
downstream without changing the arm mathematics.
Full answer: thesis 3.4.4, 8.2.

## 6. Extra results

**Q: How much does real-time cost exactly?**
Median differences against the offline solve of the same frames: worst
joint group 0.64 degrees (p95 3.24), pelvis 2.4 mm, object 6.2 mm, with a
three-frame (100 ms) filter lag and coverage 863 against 877 object
frames. Every difference is attributable to causality because everything
else is shared.
Full answer: thesis Tables 7.3/7.5; backup "Offline versus real-time".

**Q: What is the actual frame budget usage?**
Person pipeline p99 is 30.7 ms against the 33.3 ms budget, dominated by
pose inference at 27.6 ms p99; the entire kinematic mathematics costs
under one millisecond. The object pipeline sits at 14.9 ms p99.
Full answer: thesis Table 7.1; backup "Per-stage latency".

**Q: Those two real-time filter failures, how were they found?**
Both surfaced as measured coverage collapses on the pinned recording:
rejection lockout dropped object coverage from 877 to 541 frames before
the three-reject reseed fixed it (863), and motion-onset false rejection
held all-joints-live at 92.4 percent until the floor was raised (97.3).
Both are generic to causal robust filtering, which is why they are
reported.
Full answer: thesis 7.4; backup "Real-time failure modes".

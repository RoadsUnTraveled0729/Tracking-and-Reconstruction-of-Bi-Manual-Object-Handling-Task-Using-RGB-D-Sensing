#!/usr/bin/env python3
"""Build writing/v4/Chapter_8_Discussion_and_Future_Work.docx.

v3 port: content carried per the approved v2-to-v3 map; per-chapter References
section dropped (skill rule 12); references dict kept for build_thesis.py.

All numbers come from thesis/D1_limitations.md (whose amplification laws
are numerically verified by thesis/check_limits.py) and the pinned results
already quoted in Chapters 6 and 7; nothing is invented. Structure follows
ToC v4 sections 8.1-8.3 (8.3.1-8.3.5; 8.3.5 added in the v4 review round). The 8.3.2 heading uses a hyphen in
"Python-Unity" (the ToC prints an en dash; the no-dash style rule wins).

v5 trim round (2026-08-03, supervisor directive): 8.1 paragraphs and the
pitfalls paragraph compressed, 8.3.1/8.3.3/8.3.4 tightened, 8.3.2 kept whole
with a pointer to the new Figure 5.2; Table 8.1 and all pinned numbers
unchanged.
"""
from docx import Document
from docx.shared import Pt, Inches

FIG = "/home/luo/Desktop/New_SandBox/writing/v2/figures/"
H1, H2, H3, P, IMG, CAP, TBL = "h1", "h2", "h3", "p", "img", "cap", "tbl"

content = [
(H1, "Chapter 8: Discussion and Future Work"),

(P, "The preceding chapters reported the system's capabilities and their measured accuracy; this chapter discusses its limits, their causes, and the work that should follow. The discussion follows a discipline established early in the project: every limitation is stated with its mathematical cause, its measured size on the evaluation data, and its mitigation, so that the boundary of the system's validity is as quantified as its performance. Section 8.1 organizes those limitations by cause. Section 8.2 reads the evaluation data for what it says about two-handed object manipulation, the behaviour the system was built to capture. Section 8.3 lays out five concrete future directions: three named in the thesis proposal, one of them, the shared memory transport, already delivered during the work itself, and a fifth, model-based recovery of occluded joints, opened by the laboratory's prior work."),

(H2, "8.1 System Limitations"),

(P, "The deepest limitations are not implementation flaws but observability limits, properties of what three landmarks per arm can ever reveal. Two segment directions carry exactly four rotational degrees of freedom, so the solver extracts exactly four angles per arm and the elbow's out-of-plane component is identically zero by construction; forearm pronation, wrist pose, and the fingers are invisible in principle, not merely noisy. A pose synthesized with a 30 degree out-of-plane elbow component decodes as 30 degrees of additional shoulder twist with the identical forearm direction: the same physical geometry under a different attribution. This has an interpretive consequence: the clinical elbow carry angle is absorbed into shoulder twist, so individual angle values are convention-dependent even though the reconstructed geometry is not. Within the four observable angles, quality is posture-dependent in a way that follows a derived law, shown in the left panel of Figure 8.1. Shoulder twist is observable only through the forearm's component perpendicular to the upper arm axis, whose magnitude is the sine of the elbow flexion; transverse noise on the measured forearm direction is therefore amplified in the decoded twist by one over that sine. The law was verified numerically: amplification 1.41 times at 45 degrees of flexion, 4.13 at 14 degrees, 11.3 at 5 degrees, and exact unobservability at a straight elbow, a property of any three-landmark arm. The evaluation recording confirms it in the wild, with raw twist jumps of up to 65 degrees at 14 degrees of flexion fully accounted for by the measured raw wrist spikes. The filter collapses these jumps ten- to thirty-fold, and the solver flags exact unobservability and holds the last valid twist; the residual is that any downstream use of twist near a straight elbow inherits the amplification."),

(IMG, FIG + "ch8_fig1_conditioning.png", 6.3),
(CAP, "Figure 8.1. The two verified conditioning laws. Left: shoulder-twist noise amplification as a function of elbow flexion, one over the sine of the flexion, with the numerically verified points marked. Right: the sensitivity of ZXY Euler extraction as pitch approaches 90 degrees, one over the cosine of the pitch. Curves are the derived laws; marked points are the verified values."),

(P, "A second conditioning law governs the interchange format rather than the measurement, shown in the right panel of Figure 8.1. Extracting ZXY Euler angles divides through the cosine of the pitch, so sensitivity to matrix perturbation grows without bound as pitch approaches 90 degrees, reaching an amplification of 345 at 89.9 degrees. The carried box reaches exactly that pitch in the recording, and its Euler round-trip error there rises to a millionth of a degree while the underlying matrices still agree to machine precision. The mitigation is architectural: every computation and every validation in the system operates on rotation matrices at machine precision, and Euler angles appear only at the Unity display interface. A cousin of the same structure appears at the arm-vertical pose, where the swing azimuth becomes the angle of two vanishing quantities; a fixed convention keeps the decode well-defined, at the cost of a noisy azimuth near vertical arms."),

(P, "The second family of limits comes from the sensor. Stereo depth error grows with the square of range, and position noise maps into segment-direction noise inversely with segment length, so the measured 5 to 10 millimetres of raw landmark jitter corresponds to roughly 1 to 2.5 degrees of raw direction noise on the forearm and upper arm, before the conditioning laws above act on top of it. The evidence that this is a depth-noise floor is internal: hips and shoulders are noisier than wrists, and the solver reconstructs raw and filtered data equally exactly, isolating all jitter to the input. After filtering, the residual 1 to 2 millimetre floor propagates to about half a degree of segment noise and is a visible contributor to the one centimetre clean-visibility result of Chapter 6. The single-sensor geometry imposes two further bounds: the workspace is one camera's field of view, 55.6 by 43.1 degrees, within usable depth range; and the person must face the sensor, so the arm on the far side of a carried object is systematically half-occluded. That asymmetry is not hypothetical; it is the measured factor of four between the left-holding and right-holding residuals of Chapter 6."),

(P, "The marker branch has its own limit family, each mechanism a function of how large a marker appears in the image. An anchored world inherits the anchor's orientation error amplified by distance, so the system calibrates once and freezes the anchor: the measured session drift of the desk marker under changing lighting, up to 0.69 degrees, would otherwise move the wall by some 34 millimetres, while the frozen anchor's calibration window bounds the wall to below 9 millimetres. The planar-pose two-lobe degeneracy of Chapter 4 becomes dangerous only at small subtended size, and the measured result there is a negative one worth stating: at 32 pixels no threshold on reprojection error can separate the reliable lobe from the unreliable one, so the discriminator must switch on lobe separation, which the gravity-seeded policy does. Monocular range noise, finally, scales with range over marker pixels, about 28 millimetres for the wall marker at 3 metres, confirmed by the independent depth cross-check. One structural gap belongs on this list even though it never failed in the recordings: marker roles are configuration, not inference, so a marker bumped mid-session would be handled by convention rather than detected. Section 8.3.4 takes this up as future work."),

(P, "Two limitations concern what the evaluation itself can resolve. Occlusion holds trade error for data integrity by design: a held angle differs from truth by the integral of the true joint velocity over the hold, and the masked-data validation measured exactly that, 1.4 to 7.8 degrees of drift over 30 to 45 frame holds, with live joints exact throughout. No algorithm recovers unobserved motion; the system's position is that the bound must be declared, and the live mask carries the declaration to every consumer. Second, the accuracy evaluation of Chapter 6 measures the wrist through a rigid-grip model, so its resolution floor is the stability of the grip vector itself. The right hand's standard deviation under 2 centimetres per axis validates the assumption and yields the 1.0 centimetre result; the left hand's 2.5 to 3.8 centimetres, inflated by a mid-recording regrip and the occluded wrist, means the left-holding 4.6 centimetre figure is an upper bound on pipeline error, not a measurement of it. Pushing the evaluation below one centimetre would require true per-frame wrist ground truth, such as a marker on the hand."),

(P, "The display layer contributes limitations of its own. The stock rig's proportions are not the person's: even display-scaled to the correct height, its forearm is 1.59 times the measured forearm, and the forward-kinematics hand lands a median 7 to 13 centimetres from the wrist landmark. This is a rendering limitation only; every quantitative result in this thesis is computed on landmark tracks, never on the rig. The rigid-torso assumption makes pelvis and trunk inseparable with three torso landmarks, so trunk lean pitches the root frame; legs are untracked and the rig below the hips stays at rest. And the one serious integration bug of the project, the anchor conjugation of Chapter 5 that cancelled itself out of the pose while every positional check passed, is recorded as a limitation of a class of tests rather than of the system: validators that check only positions are blind to orientation errors, so the project's validators now assert orientation-level facts."),

(TBL, [["limitation", "root cause", "measured size", "mitigation and residual"],
       ["twist ill-conditioning near straight elbow", "observability: 1 / sin(elbow flexion)", "11.3x amplification at 5 deg; 65 deg raw jumps", "filter, flag, hold; posture-dependent quality remains"],
       ["4 rotational DOF per arm", "3 landmarks give 2 directions", "out-of-plane elbow decodes as twist, geometry exact", "none needed for geometry; angle attribution is convention"],
       ["Euler gimbal sensitivity", "1 / cos(pitch) in ZXY extraction", "345x at 89.9 deg pitch", "matrices everywhere; Euler display-only"],
       ["depth noise floor", "stereo error grows as range squared", "5-10 mm raw, 1-2 mm filtered, ~0.5 deg segment noise", "median depth window, 3 Hz filter; feeds the 1 cm result"],
       ["self-occlusion asymmetry", "single viewpoint, carried object", "4.6 vs 1.0 cm left/right residual", "declared; second viewpoint is future work"],
       ["anchor lever arm", "orientation error x distance", "session drift 0.69 deg would move the wall 34 mm", "calibrate once and freeze; <= 9 mm residual at the wall"],
       ["two-lobe wall degeneracy", "planar pose at small subtended angle", "wrong lobe on 815/837 frames by reprojection alone", "lobe-separation-switched, gravity-seeded policy; wall is cross-check grade"],
       ["occlusion hold error", "integral of true velocity over the hold", "1.4-7.8 deg over 30-45 frame holds", "declared via live mask; long fast holds are lost motion"],
       ["evaluation grip floor", "rigid-grip assumption", "right std < 2 cm validates; left 2.5-3.8 cm inflates", "per-hand fit; hand marker needed to go below ~1 cm"],
       ["display rig proportions", "stock FBX bone ratios", "hand 7-13 cm from wrist landmark", "rendering-only; per-bone retargeting out of scope"]]),
(CAP, "Table 8.1. The principal limitations with their causes, measured sizes, and mitigations. Every number traces to the pinned artifacts of Chapters 4 through 7; the amplification laws are verified numerically."),

(P, "Three methodological pitfalls close the section, documented because each silently corrupts an evaluation and all three occurred in this project before being caught. The derivative of the arccosine diverges at zero angle, so tiny angles computed by arccosine collapse to zero in double precision; all angle comparisons in the validators use the two-argument arctangent form instead. Yaw statistics for a person facing the camera sit exactly at the 180 degree wrap, where a naive standard deviation reports 176 degrees for a true circular spread of about 5; circular statistics are used throughout. And path length summed over unsmoothed frames integrates jitter into fictitious travel: the carried cube's raw track sums to 3.35 metres against the smoothed track's 1.94, and the thesis quotes the latter. Finally, one limitation recorded early in the project has been overtaken by the work itself: the limitations document declared all claims offline, and Chapter 7 subsequently built and validated the causal stack. What remains true is narrower: the real-time results come from a recording replayed at recorded pacing on a single 30 second take, and long-run behaviour, lighting drift, and true camera jitter remain untested."),

(H2, "8.2 Insights into Bimanual Coordination"),

(P, "The system was built to capture object handling, and the evaluation recording, although only 30 seconds long, is dense enough in events to support some observations about two-handed coordination, offered here with the caution a single-subject, single-session recording deserves. The clearest finding is that grips are rigid and hand-specific. Expressed in the object's own frame, the wrist-to-marker offset is constant per holding hand, to better than 2 centimetres per axis for the fully visible hand, and the two hands' vectors differ substantially, by about 15 centimetres in the marker plane, because each hand cups the box in its own place. Hand-overs are therefore visible in the data as clean switches between two constant vectors rather than as gradual drift, and the one regrip that follows the parked stretch appears as a small but resolvable shift within the left hand's vector. The division of labour is asymmetric: the left hand is the nearer wrist on 72 percent of frames against 28 for the right, with the right hand engaged for the deliberate turning phases. Velocity coupling while carried is strong, a correlation of 0.842 between object and nearest-wrist velocity, and its collapse to 0.273 over the whole video is itself informative: coordination measures are only meaningful conditioned on contact, and the resting phase must be segmented out, which the object's height above the tabletop does cleanly."),

(P, "Two boundaries limit how far these observations reach, and both point at instrumentation rather than analysis. The system sees wrists, not grasps: with no hand landmarks, finger configuration, contact points, and grip force are all invisible, so the grip vector summarizes where a hand is, not how it holds; extending the landmark set with a hand model [26] is the natural next instrument. And the self-occlusion asymmetry means the coordination data is systematically better for whichever hand faces the sensor, a bias any single-viewpoint bimanual study inherits. The methodological contribution that does generalize is the instrument itself: a rigid object with a known marker grades the hand that holds it, through an independent measurement chain, without any wearable on the person. Anything rigid and marked, a tool, a box, a handle, can serve as ground truth for manipulation studies at the one-centimetre level measured here. The same logic extends to more than one person: passing an object between two people would let one marker grade two people's hands in turn. The present pose detector is single-person [39], so a multibody version needs multi-person detection, identity association across frames, and one anchor per person, but the scene side, the object instrument, and the evaluation logic carry over unchanged, and this is the extension the passing scenario of Chapter 6 most directly invites."),

(H2, "8.3 Future Directions"),

(H3, "8.3.1 Sampling Rate Limitations and Temporal Alignment Issues"),

(P, "Everything in the system ticks at the sensor's 30 frames per second, and several observed effects trace directly to that quantum. The pairing of person and object streams is aligned to one frame at best, the measured 33.4 millisecond worst-case skew of Chapter 7, and the sharpest carried-object motion approaches 26 centimetres per second, nearly a centimetre per frame, so a one-frame misalignment between the streams costs about as much as the entire clean-sight accuracy budget of the system. Three upgrades would relieve this in order of increasing effort: carry the sensor's hardware timestamps end to end and pair on stamps rather than arrival order; resample both streams onto a common clock in the merger, which removes the residual sub-frame offset at a known, bounded cost; and raise the rate itself, since the depth sensor offers 60 and 90 frame-per-second modes at reduced resolution and Chapter 7's budget shows the mathematics would follow easily, with the pose detector's inference time the only stage that must be re-validated."),

(H3, "8.3.2 Shared Memory Communication for Python-Unity Integration"),

(P, "This direction was listed in the thesis proposal as an aspiration, with uncertainty about whether it was achievable; it was subsequently built, validated, and used for every result in Chapters 5 through 7, so it is reported here as delivered future work rather than proposed. The delivered design is the seqlock-protected shared memory file of Chapter 5, drawn as a memory block in Figure 5.2: fixed-size little-endian packets, a writer that makes the sequence counter odd while writing and even when stable, a reader that copies and re-checks, no locks, no system calls on the read path, and a measured write cost of ten microseconds. The same packet contract runs unchanged over UDP for setups where a memory file cannot be shared. The engineering around the channel, rather than the channel itself, remains future work. The transport is single-host by construction; a cross-machine deployment, sensor computer separate from render computer, would promote the UDP path to primary and need sequence-gap handling, which the seqlock currently makes unnecessary. The channel set is fixed by convention, one file name per stream; a registry with discovery would let receivers enumerate what is being published. And the packet schemas are frozen structs identified by a magic code; versioning those codes explicitly would let old receivers reject new senders gracefully rather than by size mismatch. None of these change the core result: the mathematics stays in Python, the display stays in Unity, and the boundary between them is a page of shared memory that costs effectively nothing."),

(H3, "8.3.3 Robust Output Rate Handling (replacing upsampling workaround)"),

(P, "A tempting workaround exists: smooth playback by upsampling, with cubic interpolation generating intermediate poses between received frames. The system deliberately does not do this, for two reasons that this thesis's methodology makes plain: interpolation inside the display layer invents poses that no pipeline computed, which breaks the rule that Unity applies numbers and never creates them, and interpolated frames are indistinguishable on screen from measured ones, which breaks the convention that everything not measured must be declared. The receiver instead applies the newest packet each rendered frame, which is visually acceptable at 30 frames per second, as the delivered demonstrations show. The robust replacement, if display smoothness at higher rates becomes a requirement, belongs on the Python side of the boundary: a timestamped playback buffer that renders the pose at display time minus one frame interval, interpolating between the two bracketing measured packets, at a fixed, declared 33 milliseconds of additional latency and with a per-frame flag distinguishing measured from interpolated poses, rendered the same way the live mask already renders held joints. Prediction schemes that extrapolate ahead of the newest packet reintroduce invented poses and are worth their complexity only if end-to-end latency, not smoothness, becomes the binding constraint."),

(H3, "8.3.4 Improved Static vs. Dynamic Marker Differentiation"),

(P, "The system currently knows which markers are static and which are dynamic because a configuration file says so, and Section 8.1 identified the gap this leaves: the classification is trusted, not verified, for the lifetime of a session. The measured numbers give verification a wide margin to work with, since a genuinely bumped marker would move far outside the frozen anchor's measured noise envelope of 0.20 millimetres and 0.088 degrees. Three improvements follow in order of effort. The first is cheap: monitor each static marker's per-frame pose against its calibration with a windowed test thresholded by the measured noise model, and raise a scene-invalid flag when the envelope is left. The second is recovery: on a detected displacement, re-run the calibration automatically over the next stable window and mark the world discontinuity in the stream the way the live mask marks held joints. The third is role fluidity: an object that has rested motionless through a long window could serve as a secondary anchor, and a static marker that begins moving should be demoted to a tracked object rather than corrupting the world frame. Each builds on machinery that already exists, which makes this the most tractable of these directions."),

(H3, "8.3.5 Model-Based Recovery of Occluded Joints"),

(P, "The recovery behaviour of the present system is deliberately conservative. An occluded joint holds its last measured angle under a lowered live flag, and Chapter 6 measured what that costs: over the synthetic occlusion scenarios the held joint drifts from the truth by 1.4 to 7.8 degrees, which is simply the motion that occurred while the joint was blocked. Holding is the right floor for a system whose first duty is data integrity, but it is a floor. The prior work of this laboratory already demonstrates the next step at the scale of a single hand: the Bayesian framework of [16] formulates joint estimation as a Gaussian Bayesian Network over the hierarchical kinematic chain and recovers anatomically consistent configurations by Maximum Likelihood Estimation when landmarks are occluded or corrupted by noise. Extending that framework from the hand to the upper-body chain of Chapter 3 would replace held angles with estimated ones, and the pieces such an extension needs already exist here. The solver isolates exactly which angles an occlusion makes unobservable, the live mask already marks them, and the observability analysis of Section 8.1 supplies the per-joint noise amplification that a probabilistic model would weight by. The data integrity machinery would remain unchanged: an estimated angle would be flagged as an estimate rather than a measurement, exactly as held angles are flagged today. The occlusion scenarios of Chapter 6, which come with exact synthetic ground truth, are the ready-made benchmark for grading such an extension."),

(P, "Each of the five directions above extends machinery the system already has rather than replacing it, which is the practical test of whether a limitation was understood or merely encountered. Chapter 9 steps back from individual limitations and directions to conclude the thesis as a whole."),

]

references = {
16: 'Y. Dong and S. Payandeh, "Bayesian estimation of hand kinematics from spatially tracked landmarks," Journal of Intelligent Systems and Control, vol. 4, no. 2, pp. 105-124, 2025, doi: 10.56578/jisc040203.',
26:'F. Zhang, V. Bazarevsky, A. Vakunov, A. Tkachenka, G. Sung, C.-L. Chang, and M. Grundmann, "MediaPipe Hands: On-device real-time hand tracking," arXiv:2006.10214, 2020.',
39: 'V. Bazarevsky, I. Grishchenko, K. Raveendran, T. Zhu, F. Zhang, and M. Grundmann, "BlazePose: On-device real-time body pose tracking," arXiv:2006.10204, 2020.',
}

doc = Document()
style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(12)

for item in content:
    kind = item[0]
    if kind == H1:
        doc.add_heading(item[1], level=1)
    elif kind == H2:
        doc.add_heading(item[1], level=2)
    elif kind == H3:
        doc.add_heading(item[1], level=3)
    elif kind == P:
        doc.add_paragraph(item[1])
    elif kind == IMG:
        doc.add_picture(item[1], width=Inches(item[2]))
    elif kind == CAP:
        p = doc.add_paragraph(item[1])
        p.runs[0].font.size = Pt(10)
        p.runs[0].font.italic = True
    elif kind == TBL:
        rows = item[1]
        t = doc.add_table(rows=len(rows), cols=len(rows[0]))
        t.style = "Table Grid"
        for i, r in enumerate(rows):
            for j, c in enumerate(r):
                cell = t.cell(i, j)
                cell.text = c
                for par in cell.paragraphs:
                    for run in par.runs:
                        run.font.size = Pt(10)
                        if i == 0:
                            run.font.bold = True

out = ("/home/luo/Desktop/New_SandBox/writing/v5/"
       "Chapter_8_Discussion_and_Future_Work.docx")
doc.save(out)
print("saved", out)

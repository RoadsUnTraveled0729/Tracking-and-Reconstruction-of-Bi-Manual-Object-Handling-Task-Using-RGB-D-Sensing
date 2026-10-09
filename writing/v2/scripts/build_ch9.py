#!/usr/bin/env python3
"""Build writing/v2/Chapter_9_Conclusion.docx.

New chapter extending ToC v3 (which ended at Chapter 8): a Conclusion
requested by the user on 2026-07-28. All experiment numbers are pinned
values already quoted in Chapters 6 and 7 (see PROGRESS.md); nothing is
invented. The chapter absorbs the "closing word" paragraph that previously
ended Chapter 8 (build_ch8.py was trimmed accordingly). New global
references [51]-[53]: Leiserson et al. Science 2020, Takahashi GamesBeat
2022 (the NVIDIA "Moore's law is dead" statement), Lopez-Nava and
Munoz-Melendez IEEE Sensors J. 2016 (wearable inertial sensing review).
"""
from docx import Document
from docx.shared import Pt, Inches

H1, H2, H3, P = "h1", "h2", "h3", "p"

content = [
(H1, "Chapter 9: Conclusion"),

(P, "This chapter closes the thesis. Section 9.1 summarizes what was built and what was measured. Section 9.2 places the work in a wider context: the slowing of hardware scaling, and the systems engineering view that follows from it, which is the view this project was built under. Section 9.3 offers closing remarks."),

(H2, "9.1 Summary of the Thesis"),

(P, "The problem posed in Chapter 1 was to reconstruct, in a metric virtual scene, a person's upper body together with the object their two hands manipulate, and to know how far the reconstruction can be trusted. The constraint was deliberate: one commodity depth camera [9] and three printed paper markers, with no worn instrumentation of any kind. Everything else is software."),

(P, "Chapters 2 and 3 built the measurement foundation. The kinematic model works entirely in rotation matrices; a torso reference frame is constructed from three landmarks, each arm contributes two segment directions, and a swing and twist decomposition extracts the four rotational degrees of freedom per arm that those directions can support. Euler angles appear only at the display boundary, in Unity's ZXY convention, because extracting them any earlier would import their singularities into the computation. Every derivation was carried through a worked example on a pinned frame of the evaluation recording, so each equation in the text is attached to numbers that the pipeline code reproduces."),

(P, "Chapter 4 built two processing pipelines and kept them strictly separate. Pipeline A turns depth-aligned video into person landmarks and joint angles; pipeline B turns the same recording into a calibrated scene and a tracked object pose. They share no code and no intermediate data. That separation was an architectural decision made early, and it repaid itself at evaluation time, as Section 9.2 discusses. Chapter 5 integrated the two streams into one desk-anchored world in Unity, established the coordinate conversions exactly, and set the honesty conventions that run through the whole system: every held, bridged, or unmeasured quantity is declared as such all the way to the screen."),

(P, "Chapter 6 measured the system. The scene calibration validators pass 21 of 21 checks on both recordings; the occlusion machinery passes 33 of 33 on masked data with known truth; the integration validator passes 20 of 20. The headline result comes from the two pipelines grading each other: while the object is carried, the person chain and the object chain agree on its position with a median residual of 3.3 centimetres overall and 1.0 centimetre where sight lines are clean, with a correlation of 0.84 between the two independently measured trajectories. Chapter 7 then showed the same system running causally at the recording's own pace: three cooperating processes sustain 25.7 frames per second with a 99th percentile compute time of 30.7 milliseconds against a 33.3 millisecond budget, and the price of causality is measured rather than assumed, a median 0.64 degrees on the worst joint and about a tenth of a second of filter lag. Chapter 8 stated the limits with their causes and sizes, from observability laws to sensor noise floors, and laid out four concrete directions for future work."),

(H2, "9.2 A Systems Engineering Perspective"),

(P, "For half a century, computing improved mainly because the hardware underneath it improved. Transistor miniaturization delivered predictable gains, and system designers could treat next year's hardware as a free performance upgrade. That era is ending. As miniaturization approaches its physical limits, the consensus in the architecture community is that future performance must come from the top of the computing stack, from software, algorithms, and system architecture, rather than from the bottom [51]. Industry has said the same thing more bluntly: NVIDIA's chief executive declared in 2022 that Moore's law is dead, and that the expectation of twice the performance at the same cost on a fixed cadence is over [52]."),

(P, "The consequence for anyone building a measurement system is simple to state. Performance and capability are no longer delivered automatically by better components; they have to be engineered out of the components already available. This is the core concern of systems engineering: under a fixed resource budget, find the arrangement of parts whose whole exceeds the sum of the parts, the arrangement that makes one plus one larger than two. Given components A, B, and C, the design question is no longer which more powerful component D to add. It is which arrangement of A, B, and C exposes a capability that none of them has alone."),

(P, "Human motion tracking offers a clear instance of the two competing philosophies. The instrumentation route adds hardware until the problem becomes easy: inertial sensors strapped to every body segment [53], instrumented gloves on the hands [18], or multi-sensor laboratory installations [19]. These systems are robust precisely because each added sensor measures directly what would otherwise have to be inferred. But each added sensor also adds cost, setup time, and intrusion on the movement being studied, and the resulting system is only as available as its most specialized part. This thesis took the other route. Every component is a commodity or free: a depth camera sold for a few hundred dollars [9], markers printed on paper, an open source pose estimation network [39], an open source computer vision library, and a game engine. None of these tools was designed for the task at hand. The engineering effort of the thesis went not into acquiring stronger components but into the arrangement: independent pipelines, a calibrated common frame, causal variants of every filter, and explicit declaration of everything not measured."),

(P, "The claim that the whole exceeded the sum of its parts is not rhetorical; the thesis contains at least two measured instances of it. The first is the evaluation itself. Because pipelines A and B were kept strictly independent, their agreement on the carried object is a genuine measurement that neither pipeline could make alone. The system graded its own accuracy, to the centimetre level reported in Chapter 6, without any ground truth equipment. A fused design that let the person pipeline borrow the object pipeline's depth estimates, or vice versa, would have been marginally more accurate and entirely unable to say how accurate. The second instance is the real-time study of Chapter 7, which tested the instrumentation reflex directly, in miniature: does adding more parallel hardware to the computation make it faster? Measured at single frame granularity, it does not. The GPU solve is three to four orders of magnitude slower than plain serial code at one frame, 885 to 1511 microseconds against 91, because launch and transfer overhead dominates; even two CPU threads lose to one, 151 microseconds against 91, because the work being split is smaller than the cost of splitting it. What met the real-time budget was structure: three processes at the ten millisecond scale, the GPU reserved for the one stage where it pays, and serial code everywhere else. Performance came from the architecture, not from the silicon."),

(P, "The trade this system makes is stated in its numbers. It does not reach the millimetre accuracy of a marker-based capture studio, and it does not need to: it reaches centimetre agreement where sight lines are clean, degrades in ways whose laws are derived and whose sizes are measured, and announces its own failures. Low cost with acceptable, quantified accuracy is not a lesser version of the instrumented approach. It is a different point on the design curve, and as hardware improvement slows, it is the point that careful arrangement of available tools can keep pushing forward."),

(H2, "9.3 Closing Remarks"),

(P, "The system set out to reconstruct a person handling an object, using one commodity depth camera and three printed markers, and to know how much to trust the result. It ends with a levelled, metrically calibrated virtual scene in which an avatar tracks the person's upper body and a carried object follows its measured trajectory; with an integrated accuracy of one centimetre where sight lines are clean, established by two independent measurement chains grading each other; with a real-time variant a tenth of a second behind the motion at a measured fraction of a degree of cost; and with every held, bridged, or interpolated quantity declared as such all the way to the screen."),

(P, "The specific numbers belong to this sensor, this room, and this recording. Two things in the work are more portable. The first is the method: derive each error's law, measure its size on real data, and make the system announce what it does not know. The second is the design stance argued in Section 9.2: when better hardware can no longer be assumed, capability must be composed from what is available, and the composition itself, done carefully, is where the capability comes from. This thesis is one worked example of that stance, and the part this work would most hope to see reused."),

(H2, "References"),
(P, "Reference numbering continues from the previous chapters; entries cited in this chapter:"),
]

references = {
9:  'L. Keselman, J. Iselin Woodfill, A. Grunnet-Jepsen, and A. Bhowmik, "Intel RealSense stereoscopic depth cameras," in Proc. IEEE Conf. Computer Vision and Pattern Recognition Workshops (CVPRW), 2017.',
18: 'R. Y. Wang and J. Popovic, "Real-time hand-tracking with a color glove," ACM Transactions on Graphics, vol. 28, no. 3, pp. 1-8, 2009.',
19: 'C. Diaz and S. Payandeh, "Multimodal sensing interface for haptic interaction," Journal of Sensors, vol. 2017, art. 2072951, pp. 1-24, 2017, doi: 10.1155/2017/2072951.',
39: 'V. Bazarevsky, I. Grishchenko, K. Raveendran, T. Zhu, F. Zhang, and M. Grundmann, "BlazePose: On-device real-time body pose tracking," arXiv:2006.10204, 2020.',
51: 'C. E. Leiserson, N. C. Thompson, J. S. Emer, B. C. Kuszmaul, B. W. Lampson, D. Sanchez, and T. B. Schardl, "There\'s plenty of room at the Top: What will drive computer performance after Moore\'s law?," Science, vol. 368, no. 6495, art. eaam9744, 2020.',
52: 'D. Takahashi, "Jensen Huang Q&A: Why Moore\'s Law is dead, and smart design is replacing it," GamesBeat/VentureBeat, Sep. 21, 2022. [Online]. Available: https://gamesbeat.com/jensen-huang-qa-why-moores-law-is-dead-and-smart-design-is-replacing-it/',
53: 'I. H. Lopez-Nava and A. Munoz-Melendez, "Wearable inertial sensors for human motion analysis: A review," IEEE Sensors Journal, vol. 16, no. 22, pp. 7821-7834, 2016.',
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

for n in sorted(references):
    doc.add_paragraph(f"[{n}] {references[n]}")

out = "/home/luo/Desktop/New_SandBox/writing/v2/Chapter_9_Conclusion.docx"
doc.save(out)
print("saved", out)

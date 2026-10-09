#!/usr/bin/env python3
"""Build writing/v8/condensed/Chapter_1_Introduction.docx (condensed build).

Baseline: the V7 Chapter 1 builder, with the consolidated citation numbers
[1]-[39] preserved. Condensing pass of 2026-09-06 (CONDENSE_BRIEF.md,
REPEATED_MATERIAL_MAP.md section 5, CONDENSE_EDITOR_RULES.md):
  - 1.1 tightened; the depth-noise-with-distance clause dropped (map 1.23,
    Appendix D is its primary location) and the depth-fusion mechanism
    reduced to a clause (map 1.3).
  - 1.2.4: the five numbered gaps become one paragraph, since the five
    objectives of 1.3 state the same content a second time (map section 5).
    Every citation of the gap list is kept.
  - 1.3: the five objectives stay, one per item, tightened. They are the
    list Chapter 10 answers one by one, so all five survive.
  - 1.4 rewritten against the condensed build: Chapter 2 carries the frames
    and the scene calibration, the reference path is defined in Chapter 7,
    and the torso repair is not promised (parked, writing/v8/CH5_PARKED.md).
    The appendix roll-call stays, because appendix lettering follows first
    reference and this is the first reference.
  - D5 follow-up: bimanual system scope is distinguished from the
    one-handed primary rail evaluation and secondary occlusion evidence.
  - 2026-09-06 (MATH_LOGIC_REVIEW.md smaller corrections): the avatar
    privacy sentence is a deployment property, and the novelty claim is
    limited to the reviewed systems.

Revision of 2026-09-11, Phase 2B (REVISION_2026-09-11_BRIEF.md sections 2
and 4). The chapter now points at one central question instead of five
separate engineering aims:
  - The opening paragraph states the central question of brief section 2
    in the author's terms and the scope of the work: one consumer-grade
    RGB-D camera, the torso and both arms as an upper-body kinematic
    model, a marked object, a controlled desk task by one subject, and
    the three recordings. The D5 wording survives: the system covers
    both arms and no recording establishes accuracy for general bimanual
    manipulation.
  - 1.1 is unchanged in content and trimmed where it repeated itself.
    The laboratory prior-work paragraph stays.
  - 1.2.1 to 1.2.3 and Table 1.1 are untouched; every citation number is
    unchanged. 1.2.4 now ends at the central question instead of at
    "combines these components".
  - 1.3 keeps five objectives and presents them as the five stages of
    one investigation: measurement layer, human reconstruction,
    independent object observation, object-assisted constraint under
    landmark failure, integration and evaluation. All five survive
    because they are referred to elsewhere: Section 10.1 names them in
    one sentence as the stages of this investigation, and
    build_appendix.py line 239 refers to "the objectives of Chapter 1".
    Chapter 10 no longer answers them one by one. Objective 4 names the actual
    references of Chapter 7 (the unmasked solve under synthetic masking
    and the manual wrist labels on the natural failures) in place of
    "reference data".
  - 1.4 carries the final chapter roles: Chapters 2 to 6 methods,
    Chapter 7 the offline experimental evaluation, Chapter 8 real-time
    feasibility as a causal replay, Chapter 9 discussion, Chapter 10
    conclusions and future work. Chapter 7 no longer defines the
    reference paths; the chapter states that the physical route is not
    yet registered into the world frame.
  - Vocabulary follows the brief: no generic "ground truth", object
    information supplies an additional geometric constraint, and the
    real-time result is a causal replay at the recorded pace with no
    live-camera validation.
No number is printed in this chapter, so no pinned source is needed.

Round 1 fix pass of 2026-09-11 (writing/reviews/final_2026-09-11/round1/
Chapter_1.txt and Thesis_wide.txt, under FIX_DECISIONS.md; log in
FIXES_ch1-3.md). Objective 3 names the world frame on the desk marker that
the scene calibration of Chapter 2 fixes for both branches, in place of
"the skeletal stream's world frame", and states the missing second
measurement chain in the active voice. Table 1.1 carries the limitation of
the depth-fusion row that is true of [13] as well, and splits the camera
count of [32] from the wearable rig of [8]. Section 1.2.4 reorders the two
prepositional phrases and names [39] as the hand-object annotation method.
Objective 5 names the loop recording among Chapter 7's coverage. Section
1.4 lists the scene calibration as what puts both branches in one
calibrated metric scene, adds the filtering of the landmark signals and
the hip depth preparation, and describes Appendix A by what it covers (the
recording procedure of A.1, the session file of A.2 and the replay check
of A.3) rather than as "the RGB-D recordings", since Appendix A carries the
rail recording only.

Author-approved edit of 2026-09-12. Objective 4 of Section 1.3 promised
that "Chapter 10 discusses chain-level Bayesian recovery following [18] as
future work". The author's replacement Chapter 10 of 2026-09-12 proposes
no such thing and cites [18] nowhere; its third future direction is
lightweight learned estimation in the recovery layer, a compact temporal
model operating alongside the explicit kinematic chain rather than
replacing it. The clause is corrected to that, and the rest of the
roadmap is untouched. [18] is still cited in Section 1.2.1 and in Section
1.2.4, so it is not orphaned and stays in the reference list.
"""
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches

H1, H2, H3, P = "h1", "h2", "h3", "p"
CAP, TBL, LIN = "cap", "tbl", "lin"

content = [
(H1, "Chapter 1: Introduction"),

(P, 'This thesis asks what can be reconstructed of a person and a manipulated object from a single consumer-grade camera viewpoint. The camera captures red, green and blue colour plus depth (RGB-D). The thesis also asks what additional geometric constraint object tracking supplies when the body landmarks fail, and what limitations remain because of the sensing, the retained state and the single viewpoint. A single consumer-grade RGB-D sensor at a fixed viewpoint observes the torso and both arms, taken as an upper-body kinematic model, and a cube carrying a printed marker. A single subject performs a controlled desk task in three recordings: the primary rail recording is one-handed, the handover recording adds the second arm, and the loop recording adds secondary two-hand evidence. The system covers both arms, and none of the recordings establishes accuracy for general bimanual manipulation.'),

(H2, "1.1 Motivation"),

(P, 'Coordinated two-handed tasks such as lifting, rotating and transferring objects are common in daily life. Imitation learning in robotics uses recorded human demonstrations [1], [2]. Virtual reality (VR) and augmented reality animate avatars from skeletal pose data together with object poses [3], [4].'),

(P, "An avatar replay of a patient's upper-body motion could help a physician assess reaching and hand transfers in Parkinson's disease, stroke, or age-related loss of coordination [5], [6]. A deployment can keep colour and depth frames on the capture device and share only the reconstructed motion."),

(P, 'Metric three-dimensional (3D) measurement requires depth sensing or synchronized camera viewpoints [7]. Multi-camera motion capture needs calibrated arrays with expert operation [8]. Wearables need per-user attachment and calibration. They also raise movement and hygiene concerns [9]. A consumer-grade RGB-D camera captures registered colour and metric depth without hardware on the subject [10].'),

(P, 'Hands can occlude each other or the object, disrupting landmark detection [11], [12] and depth readings [13]. Calibration must place every segment and object in one frame [14], and torso and hand motion call for different filtering [15]. With limits on transistor scaling [16], this systems engineering thesis examines what algorithm design and system organization can achieve on existing hardware.'),

(P, 'Earlier work in the Networked Robotics and Sensing Laboratory at Simon Fraser University developed a hierarchical hand model from RGB-D landmarks [17] and Gaussian Bayesian Network joint estimation for noisy or occluded measurements [18]. This thesis extends the tracked anatomy to the torso and both arms, with concurrent object tracking and Unity visualization.'),

(H2, "1.2 Problem Statement and Literature Review"),

(P, "Table 1.1 summarizes the limitation each reviewed approach family carries in this setting."),

(H3, "1.2.1 Hand and Object Tracking Approaches"),

(P, "Early hand tracking systems encoded finger configuration in the sensor signal itself, through instrumented colour gloves [20] and, in earlier laboratory work, marker-based visual tracking with a vibrotactile glove [21]. Consumer depth cameras then shifted the field toward markerless tracking, with Particle Swarm Optimization over a geometric hand model [22], an articulated Iterative Closest Point solver [23], and a sphere-based model fitted to depth point clouds [24]."),

(P, 'Deep learning approaches include multi-view convolutional networks over depth images [25], transformer-based mesh recovery from monocular RGB [26], and graph-guided state space models [27]. MediaPipe provides lightweight landmark detection [28], but its appearance-derived depth is uncertain during motion, contact, and occlusion [3]. This thesis instead back-projects the landmarks using calibrated sensor depth [17], [13].'),

(P, "For object tracking, fiducial markers give reliable pose estimation without appearance models or training data. ArUco markers balance robustness and efficiency well for single-camera setups [29]. Marker size and viewing distance set the pose error [30]. Each marker encodes an integer identity, so one detection gives both the object identity and its pose. Occlusion between the hand and the object remains the most persistent failure mode, met either by inpainting the occluded hand before pose estimation [11] or by modelling hand and object jointly through mutual attention [12]."),

(H3, "1.2.2 Bimanual Manipulation in Motion Analysis"),

(P, 'Bimanual manipulation goes beyond running two hand trackers in parallel. The hands overlap in the image and are kinematically coupled through the object they hold, so an error in one hand spreads into the reconstructed scene [19]. Symmetric and asymmetric coordination give different patterns of landmark dropout [31]. Large bimanual datasets show how demanding the capture problem is: InterHand2.6M used between 80 and 140 synchronized cameras [32]; OakInk2 used multi-camera rigs with wearable sensors [8]. RGB2Hands recovers two interacting hands from a single RGB video [33] using a learned model that is hard to interpret physically.'),

(H3, "1.2.3 Graphical Reconstruction in Robotics and VR"),

(P, 'Unity has been used for monocular motion replay through kinematic retargeting [34] and Kinect-based rehabilitation feedback [35]. RePose streams MediaPipe-derived joint angles to a Unity avatar [36], the architecture adopted here. RealSense and Unity use different handedness and vertical axes, so the streamed poses need an explicit coordinate conversion [14].'),

(P, "A single fixed change of coordinates moves landmark positions between the two environments. The avatar, however, is driven joint by joint through rotations, so the rotation angles of the body segments must be resolved from the measured landmark positions. The depth noise underlying those positions is characterized as Gaussian, consistent with [37], [38]."),

(TBL, [["Approach family", "Representative work", "Sensing", "Limitation for this setting"],
       ["Instrumented gloves and wearables", "[20], [21]", "worn sensors", "hardware on the user; per-user calibration; hygiene"],
       ["Model-based depth tracking", "[22], [23], [24]", "one depth camera", "single hand; explicit geometric models; per-user initialization"],
       ["Learning-based pose estimation", "[25], [26], [27]", "depth or RGB", "large training sets; no biomechanical constraints"],
       ["Landmark detection with depth fusion", "[28], [3], [13], [17]", "RGB-D", "single hand, or body landmarks without a manipulated object in the same frame"],
       ["Fiducial object tracking", "[29], [30]", "RGB", "tracks marked objects only; no body tracking"],
       ["Hand-object occlusion handling", "[11], [12]", "RGB, depth", "single hand and object; learned models"],
       ["Bimanual capture datasets", "[32], [8]", "80 to 140 synchronized cameras [32]; multi-camera rig with wearables [8]", "laboratory infrastructure far beyond clinical settings"],
       ["Two-hand reconstruction", "[33]", "monocular RGB", "no object tracking; no metric depth"],
       ["Avatar replay in Unity", "[34], [35], [36]", "monocular or Kinect", "single tracked stream; no concurrent object in a shared frame"]]),
(CAP, "Table 1.1. Summary of the reviewed literature: each approach family, its representative work, its sensing arrangement, and its limitation for single-sensor bimanual capture."),

(H3, "1.2.4 Gap Analysis and Motivation for This Work"),

(P, 'The reviewed approaches address parts of the required system. Recovery must account for the different kinematics of the torso and arm segments [19]. The reviewed bimanual method omits object tracking [33], and the hand-object annotation method of [39] covers one hand. The sensor-to-Unity conversion is documented for a single hand [14]. No reviewed system reconstructs the upper body together with a tracked object from a single RGB-D viewpoint, or reports what that viewpoint recovers when the landmarks fail. This thesis investigates that question in the stages of Section 1.3, building on the laboratory work of [17] and [18].'),

(H2, "1.3 Research Objectives"),

(P, 'The central question divides into five stages, and the objectives below are those stages in the order the thesis builds them. Each stage supplies what the next one needs, and the last returns to the question.'),

(LIN, "Objective 1 is the measurement layer: a calibrated RGB-D pipeline on the Intel RealSense D435 that aligns the depth and colour streams, establishes the camera intrinsics, and places the body landmarks and the marked-object poses in one metric world frame."),
(LIN, 'Objective 2 reconstructs the person from that layer. Metric 3D positions for the torso, shoulders, elbows, and wrists come from MediaPipe Pose detections fused with registered depth, and they give the selected degrees of freedom of the upper body. The wrist stays a tracked point.'),
(LIN, "Objective 3 observes the object independently in the same scene. The scene calibration in Chapter 2 fixes the world frame on the desk marker for both branches. The ArUco-marked object is tracked in this frame, and the two records are synchronized by frame index. The branch filters and streams the object orientation, and no second measurement chain checks it."),
(LIN, 'Objective 4 uses that observation as an additional geometric constraint where the landmarks fail. The holding wrist comes from the tracked object pose and the hand-object offset. Its elbow comes from two-link inverse kinematics. The recovered positions are compared with the unmasked solve under synthetic masking and with manual wrist labels on the natural failures. Chapter 10 discusses lightweight learned estimation in the recovery layer as future work. The proposed compact temporal model operates alongside the explicit kinematic chain rather than replacing it.'),
(LIN, 'Objective 5 integrates the stages and evaluates the result. The person and object records drive one Unity reconstruction. Chapter 7 evaluates it offline. Chapter 8 tests whether the same architecture runs causally, and Chapter 9 discusses the limitations shown by the results. Chapter 7 covers the rail task one-handed and with a handover. It also takes natural failure windows from the two-hand loop recording. No recording establishes accuracy for general bimanual manipulation.'),

(H2, "1.4 Organization of the Thesis"),

(P, 'Chapters 2 to 6 build the system one stage at a time. Chapter 2 defines the coordinate frames and calibrates the shared metric scene. It describes the landmark and object measurements, landmark filtering and hip depth preparation. Chapter 3 reconstructs the upper body from those landmarks, and Chapter 4 observes the marked object independently in the same scene. Chapter 5 uses the object as an additional geometric constraint where landmarks fail, and Chapter 6 joins both records into the Unity reconstruction.'),

(P, 'Chapter 7 reports the offline experimental evaluation against physical references, manual wrist labels and within-recording comparisons. It also states that the physical route is not yet registered into the world frame. Chapter 8 examines real-time feasibility as a causal replay of a recording at its recorded pace, with no live-camera session validated. Chapter 9 discusses the results and their limitations. Chapter 10 concludes and outlines future work.'),

(P, 'The appendices hold the supporting internals. Appendix A covers the recording procedure, the session file and the replay check. Appendix B covers the hardware and software platform, Appendix C pose landmark detection, Appendix D depth sensing and deprojection, Appendix E fiducial marker detection and pose recovery, Appendix F the candidate filters, and Appendix G the hip depth preparation. Appendix H records the verification of the kinematic solver of Chapter 3 against synthetic exact references.'),

]

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
    elif kind == LIN:
        p = doc.add_paragraph(item[1])
        p.paragraph_format.left_indent = Inches(0.3)
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

out = str(Path(__file__).resolve().parents[4] / "writing" / "v8" / "condensed" / "Chapter_1_Introduction.docx")
doc.save(out)
print("saved", out, "| items:", len(content))

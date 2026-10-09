#!/usr/bin/env python3
"""Build writing/v9/Chapter_1_Introduction.docx (condensed build).

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

Prose condensation of 2026-09-14 (body toward 100 pages; readers are
systems engineers). Chapter 1 prose 1468 -> 1399 words. Cut: the
daily-life opener of 1.1, whose motivation the abstract carries, with
"coordinated two-handed tasks" folded into the sentence that keeps [1]
and [2]; the framing sentence of 1.2.4, restated concretely by the
sentences that follow it; the second lead sentence of 1.3, a transition;
and the "Chapters 2 to 6 build the system one stage at a time" lead of
1.4, a roadmap sentence. Everything else is wording compression: merged
sentences and shorter noun phrases. No citation, cross-reference,
heading, table or claim was dropped, and Table 1.1 and its caption are
untouched. The chapter stops short of the 1250-word target because every
remaining sentence of 1.1 and 1.2 anchors a citation number ([9] and
[16] are cited nowhere else), and 1.3 and 1.4 are cross-references to
chapters and appendices that the brief requires to stay.
"""
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches

H1, H2, H3, P = "h1", "h2", "h3", "p"
CAP, TBL, LIN = "cap", "tbl", "lin"
BUL = "bul"  # bullet item (supervisor comment C54, 2026-09-16)
NUM = "num"  # numbered item (C54 mechanics follow-up, 2026-09-16; see list_numbering.py)

content = [
(H1, "Chapter 1: Introduction"),

(P, 'This thesis examines the extent to which a person and a manipulated object can be reconstructed from one consumer-grade colour and depth (RGB-D) camera. It also examines the contribution of object tracking when the body landmarks fail, and the limits that remain from the sensing, the carried state and the single viewpoint. A fixed sensor observes the torso, both arms and a marked cube while a single subject performs a desk task in three recordings. None of the recordings establishes accuracy for general bimanual manipulation.'),

(H2, "1.1 Motivation"),

(P, 'Imitation learning in robotics uses recorded human demonstrations of coordinated two-handed tasks [1], [2]. Virtual reality (VR) and augmented reality animate avatars from skeletal pose data together with object poses [3], [4].'),

(P, "An avatar replay of a patient's upper-body motion could help a physician assess reaching and hand transfers in Parkinson's disease, stroke, or age-related loss of coordination [5], [6]. A deployment can keep colour and depth frames on the capture device and share only the reconstructed motion."),

(P, 'Metric three-dimensional (3D) measurement requires depth sensing or synchronized camera viewpoints [7]. Multi-camera motion capture needs calibrated arrays with expert operation [8]. Wearables need per-user attachment and calibration, and they raise movement and hygiene concerns [9]. A consumer-grade RGB-D camera captures registered colour and metric depth without hardware on the subject [10].'),

(P, 'Hands can occlude each other or the object, disrupting landmark detection [11], [12] and depth readings [13]. Calibration must place every segment and object in one frame [14], and torso and hand motion call for different filtering [15]. With limits on transistor scaling [16], this systems engineering thesis examines the capabilities that algorithm design and system organization can achieve on existing hardware.'),

(P, 'Earlier work in the Networked Robotics and Sensing Laboratory at Simon Fraser University developed a hierarchical hand model from RGB-D landmarks [17] and Gaussian Bayesian Network joint estimation for noisy or occluded measurements [18]. This thesis extends the tracked anatomy to the torso and both arms, with concurrent object tracking and Unity visualization [62].'),

(H2, "1.2 Problem Statement and Literature Review"),

(P, "That laboratory work covers the hand, but not the torso, the arms or a held object, so the review below follows the three problems that remain. Section 1.2.1 covers tracking the hands and the object, Section 1.2.2 the coupling of two hands on one object, and Section 1.2.3 the replay of the motion graphically. Table 1.1 summarizes the limitation each reviewed approach family carries in this setting."),

(H3, "1.2.1 Hand and Object Tracking Approaches"),

(P, "Early hand tracking systems encoded finger configuration in the sensor signal, through instrumented colour gloves [20] and, in earlier laboratory work, marker-based visual tracking with a vibrotactile glove [21]. Consumer depth cameras then shifted the field to markerless tracking: Particle Swarm Optimization over a geometric hand model [22], an articulated Iterative Closest Point solver [23], and a sphere-based model fitted to depth point clouds [24]."),

(P, 'Deep learning approaches followed the model-fitting trackers and include multi-view convolutional networks over depth images [25], transformer-based mesh recovery from monocular RGB [26], and graph-guided state space models [27]. Google\'s MediaPipe framework [60], [61] provides lightweight landmark detection [28], but its appearance-derived depth is uncertain during motion, contact, and occlusion [3]. This thesis instead back-projects the landmarks using calibrated sensor depth [17], [13].'),

(P, "A held object carries no landmarks, so its pose needs a different signal. For object tracking, fiducial markers give reliable pose estimation without appearance models or training data. ArUco markers balance robustness and efficiency for single-camera setups [29], and marker size and viewing distance set the pose error [30]. Each marker encodes an integer identity, so one detection gives both the object identity and its pose. Occlusion between the hand and the object remains the most persistent failure mode, met either by inpainting the occluded hand before pose estimation [11] or by modelling hand and object jointly through mutual attention [12]."),

(H3, "1.2.2 Bimanual Manipulation in Motion Analysis"),

(P, 'Occlusion between one hand and the object carries over to the two-handed case, where each hand can also hide the other. Bimanual manipulation goes beyond two hand trackers in parallel. The hands overlap in the image and are kinematically coupled through the object they hold, so an error in one hand spreads into the reconstructed scene [19]. Symmetric and asymmetric coordination give different patterns of landmark dropout [31]. Bimanual datasets show the difficulty of the capture problem: InterHand2.6M used between 80 and 140 synchronized cameras [32]; OakInk2 used multi-camera rigs with wearable sensors [8]. RGB2Hands recovers two interacting hands from a single RGB video [33] with a learned model that is hard to interpret physically.'),

(H3, "1.2.3 Graphical Reconstruction in Robotics and VR"),

(P, 'Unity [62] has been used for monocular motion replay through kinematic retargeting [34] and Kinect-based rehabilitation feedback [35]. RePose streams MediaPipe-derived joint angles to a Unity avatar [36], the architecture adopted here. RealSense and Unity use different handedness and vertical axes, so the streamed poses need an explicit coordinate conversion [14].'),

(P, "A single fixed change of coordinates moves landmark positions between the two environments. The avatar, however, is driven joint by joint, so the segment rotation angles must be resolved from the measured landmark positions. The depth noise underlying those positions is characterized as Gaussian, consistent with [37], [38]."),

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

(P, 'Recovery must account for the different kinematics of the torso and arm segments [19]. The reviewed bimanual method omits object tracking [33], the hand-object annotation method of [39] covers one hand, and the sensor-to-Unity conversion is documented for a single hand [14]. No reviewed system reconstructs the upper body together with a tracked object from a single RGB-D viewpoint, or reports the recovery from that viewpoint when the landmarks fail. This thesis investigates that question in the stages of Section 1.3, building on the laboratory work of [17] and [18].'),

(H2, "1.3 Research Objectives"),

(P, 'The central question divides into five stages, and the objectives below are those stages in the order the thesis builds them.'),

(LIN, "Objective 1 is the measurement layer: a calibrated RGB-D pipeline on the Intel RealSense D435 that aligns the depth and colour streams, establishes the camera intrinsics, and places the body landmarks and the marked-object poses in one metric world frame."),
(LIN, 'Objective 2 reconstructs the person from that layer. Metric 3D positions for the torso, shoulders, elbows and wrists come from MediaPipe Pose detections fused with registered depth, and give the selected degrees of freedom of the upper body. The wrist stays a tracked point.'),
(LIN, "Objective 3 observes the object independently in the same scene. The scene calibration of Chapter 2 fixes the world frame on the desk marker for both branches. The ArUco-marked object is tracked there, and the two records are synchronized by frame index. The branch filters and streams the object orientation, and no second measurement chain checks it."),
(LIN, 'Objective 4 uses that observation as an additional geometric constraint where the landmarks fail. The holding wrist comes from the tracked object pose and the hand-object offset, and its elbow from two-link inverse kinematics. The recovered positions are compared with the unmasked reconstruction under synthetic masking and with manual wrist labels on the natural failures. Chapter 10 discusses lightweight learned estimation in the recovery layer as future work, a compact temporal model that operates alongside the explicit kinematic chain rather than replacing it.'),
(LIN, 'Objective 5 integrates the stages and evaluates the result. The person and object records drive one Unity reconstruction. Chapter 7 evaluates it offline on the rail task one-handed and with a handover, and on natural failure windows from the two-hand loop recording. Chapter 8 tests the same architecture for causal operation, and Chapter 9 discusses the limitations shown by the results. No recording establishes accuracy for general bimanual manipulation.'),

(H2, "1.4 Organization of the Thesis"),

(P, 'The remaining chapters build the system, evaluate it, and discuss the results; the appendices support the chapters with detail.'),

(BUL, "", "Chapter 2 builds the measurement layer, Chapter 3 the kinematic model, Chapter 4 the object branch, Chapter 5 the recovery layer and Chapter 6 the Unity integration."),
(BUL, "", "Chapter 7 evaluates the system offline against a physical route not yet registered into the world frame. Chapter 8 tests real-time feasibility as a causal replay, with no live-camera session validated."),
(BUL, "", "Chapter 9 discusses the results and their limitations. Chapter 10 concludes and outlines future work."),
(BUL, "", "Appendix A covers the recording procedure, B the hardware and software platform, C pose landmark detection, D depth sensing, E fiducial marker detection, F candidate filters, G hip depth preparation, and H solver verification."),

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
    elif kind == BUL:
        # bullet item (supervisor comment C54, 2026-09-16)
        p = doc.add_paragraph(style="List Bullet")
        if item[1]:
            p.add_run(item[1]).font.bold = True
            p.add_run(" " + item[2])
        else:
            p.add_run(item[2])
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        p.paragraph_format.space_after = Pt(4)
    elif kind == NUM:
        # numbered item, restarted per contiguous run (C54 mechanics
        # follow-up, 2026-09-16; see list_numbering.py)
        p = doc.add_paragraph(style="List Number 2")
        if item[1]:
            p.add_run(item[1]).font.bold = True
            p.add_run(" " + item[2])
        else:
            p.add_run(item[2])
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        p.paragraph_format.space_after = Pt(4)
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

out = str(Path(__file__).resolve().parents[3] / "writing" / "v9" / "Chapter_1_Introduction.docx")
from list_numbering import restart_numbered_lists
restart_numbered_lists(doc)

doc.save(out)
print("saved", out, "| items:", len(content))

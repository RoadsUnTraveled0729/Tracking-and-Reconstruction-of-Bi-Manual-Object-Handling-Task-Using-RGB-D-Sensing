#!/usr/bin/env python3
"""Build writing/v8/condensed/Chapter_10_Conclusions_Future_Work.docx.

Supervisor round 7 (2026-09-10, C53; D-022): the conclusions and the
future work of the old Chapter 9 became their own chapter.

Author's replacement of 2026-09-12. The author supplied a complete
rewritten Chapter 10 and instructed that it replace the previous one
outright. The `content` list below is that text, installed verbatim and
mapped into the builder's (H1/H2/P) tuples. It is not a revision of the
earlier chapter and must not be merged with it. The only departures from
the author's characters are three sentence splits made to satisfy the
45-word gate of check_style.py; each split is made at a punctuation mark
the author already wrote, no word is changed, added or removed, and each
is recorded in the comment above the paragraph it affects.

Author-approved edits of 2026-09-12, applied after that installation and
recorded here so the verbatim statement above stays accurate:

- Section 10.2, second future direction: "One practical example is" ->
  "A practical example is". One word, approved by the author to clear the
  number-led sentence gate of check_style.py. Nothing else in the
  sentence or the paragraph was touched.
- Section 10.2, closing argument: the citation marker [49] (Takahashi,
  "Jensen Huang Q&A: Why Moore's Law is dead, and smart design is
  replacing it") was added to the hardware-scaling sentence, approved by
  the author. No word was changed. The marker sits after the
  hardware-scaling clause, matching the only other place the thesis makes
  this claim, Section 1.1 of build_ch1.py ("With limits on transistor
  scaling [16], ...").

Reference [50] (Lopez-Nava and Munoz-Melendez) remains uncited. The
author approved removing it from writing/v8/condensed/references.md, but
it is not the last entry ([51] to [58] follow it), so removal was
withheld and escalated rather than performed.

What the replacement means for the open Chapter 7 integration items
(CH7_INTEGRATION_FIXLIST.md, section build_ch10.py):

- 10-1, 10-2: the object detection count and the wrist-to-marker
  comparison are simply absent from the author's text, so the D-038
  reading of the wrist-to-marker check has no Chapter 10 element to
  limit. Section 7.3.3 and Section 9.2 carry it.
- 10-3, 10-4: the manual label counts and the "only slow windows"
  description of Section 7.4.1 are absent. The author's recovery
  paragraph states the loop right-hand and left-hand outcomes
  qualitatively and prints no label counts.
- 10-5: the unregistered physical route survives as a scope statement in
  the closing paragraph of Section 10.1, with no point-to-path distance
  claimed, which is what Sections 7.2 and 9.7 state.
- 10-6: no hip-hold future-work item remains, so the withdrawal of the
  hip-hold comparison from Section 9.4 leaves nothing here to support.
- D-045: no claim here rests on the dropped 3.8 cm rail-height
  cross-check; the chapter prints no height quantity at all.
- D-044/D-051: the chapter uses no task-phase term (object acquisition, carry, lift, slide,
  release), so the Section 2.1 vocabulary needs no pointer from here.

The 23 cm wrist steps at the hip-repair edges and their 417 repaired
frames, withdrawn from Chapter 9 on 2026-09-12, do not appear in the
replacement either.

Verified against the rebuilt Chapter 7 before installing (both checks
passed; evidence in the source comments below): the loop right-hand
recovery outcome and the absence of a left-hand improvement against
Section 7.4.2 and its Table 7.9; and "one subject and three controlled
recordings" and the causal replay at approximately the recorded frame
rate against Section 9.7, Section 8.4 and locked fact 9 of
REVISION_2026-09-11_BRIEF.md.
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches

H1, H2, P = "h1", "h2", "p"
CAP, TBL, LIN, IMG = "cap", "tbl", "lin", "img"

REPO = Path(__file__).resolve().parents[4]

content = [
(H1, "Chapter 10: Conclusions and Future Work"),

(P, 'This chapter summarizes the principal findings of the thesis and identifies the directions that follow from the limitations observed in the experimental evaluation. Section 10.1 presents the conclusions of the work, with particular emphasis on the role of kinematic reconstruction and object information in a single-view RGB-D system. Section 10.2 outlines future extensions in sensing, pose estimation, and lightweight learning, and considers their implications for system-level design.'),

(H2, "10.1 Conclusions"),

# Causal operation at approximately the recorded frame rate: locked fact 9
# of REVISION_2026-09-11_BRIEF.md and v2/dataset/r6b_probe_baseline.txt
# (E-026), printed in Section 8.4 as "about 29 frames per second". The
# replay is a causal pass over the recorded sequence at its recorded pace,
# which the closing paragraph of this section states.
(P, 'This thesis develops and evaluates a single-view RGB-D framework for reconstructing upper-body motion together with the motion of a manipulated object in a shared metric scene. The framework combines RGB-D body landmarks, fiducial object tracking, an explicit upper-body kinematic model, failure detection, object-assisted pose recovery, and graphical reconstruction in Unity. Body motion and object motion are expressed in the same calibrated world frame, allowing the person and the manipulated object to be reconstructed as one scene rather than as two independent outputs. Under the tested conditions, the system reconstructed the torso, both arms, and the tracked object from one consumer-grade RGB-D camera, while the same architecture also operated causally at approximately the recorded frame rate.'),

(P, 'The experiments also show that single-view human-object reconstruction is limited by occlusion and incomplete observability. During manipulation, the object can hide the hand and wrist. The hands and object can cover the hips. Motion along the viewing direction is only weakly constrained. Some failures therefore remain even if the landmark detector itself is improved. Once the only camera can no longer observe the body part needed by the kinematic chain, its motion must be inferred from information that remains available. In this system, that inference comes from the kinematic model, previously observed state, calibrated segment lengths, and, when available, the tracked object. The recovery layer therefore does more than correct noisy landmarks. It is a necessary part of a single-view reconstruction system whenever interaction removes the measurements required by direct pose estimation.'),

# Natural failure outcomes: Section 7.4.2 and its Table 7.9, from
# eval/reports/r5_recovery_labeled.md and audit_evidence/ch7_restructured/
# natural.json. On the retained right-arm frames of the loop recording the
# object-assisted solve is a median of 5.2 cm from the manual wrist label,
# against 11.4 for the plain solve and 17.6 for hold-last, so the author's
# right-hand statement holds. On the retained left-arm frames the same
# layer is 13.1 cm against 12.3 for the plain solve and 12.7 for
# hold-last, so it does not improve on either baseline there; the plain
# solve ranks nearest on that arm. Section 7.4.2 also notes that the clean
# frames put the proxy 2.1 to 4.5 cm from the wrist the landmark defines,
# so the left-arm spread of under a centimetre carries no ranking.
# Recovery interpretation: locked fact 8 of the brief.
# Sentence split for the 45-word gate (author's wording unchanged): the
# author wrote "... in some cases: on the labelled right-hand failure
# frames ..." as one 46-word sentence; the colon is raised to a full stop
# and "on" capitalized.
(P, 'Object tracking provides an additional source of geometric information during these failures. When a hand is holding the object and its wrist is rejected, the object pose and the previously estimated hand-object offset can constrain the missing wrist position, while the arm is reconstructed through the kinematic chain. The natural failure experiments show that this additional constraint can improve the reconstructed wrist in some cases. On the labelled right-hand failure frames of the loop recording, the recovery result was closer to the manual wrist labels than either the plain solve or the hold-last baseline. The same method, however, did not improve the corresponding left-hand failure window.'),

(P, 'Object-assisted recovery is therefore conditional rather than universally reliable. It depends on the object remaining visible, the stored hand-object offset continuing to represent the current grip, and the state carried by the kinematic model remaining compatible with the actual motion. A reconstruction that is closer to one labelled wrist point also does not by itself prove that the complete arm configuration is correct.'),

# Error sources: the landmark at a usable reported visibility is Section
# 9.4 with Figure 9.2 (loop recording, upper arm 47.2 cm against a clean
# 25.8 cm); the depth taken from an occluding surface and the effective
# segment lengths are Sections 9.2 and 9.5; the root frame changing at the
# hip repair is Section 9.4 with Section 2.6; the held states and the rate
# limit are Sections 5.5 and 9.5. The three-group sorting of the limits is
# Section 9.5.
# Sentence split for the 45-word gate (author's wording unchanged): the
# author wrote the five-item semicolon list as one 57-word sentence; the
# semicolon after "occluding surface" is raised to a full stop and
# "effective" capitalized.
(P, 'The evaluation further shows that reconstruction error is produced by the interaction of several parts of the system rather than by a single source. MediaPipe can return a landmark at an incorrect physical location with an apparently usable confidence score; depth sampled at a landmark pixel can belong to an occluding surface. Effective segment lengths depend on the detected landmark trajectories; the root frame changes when the hips are repaired; and temporal rules such as held states and rate limits carry earlier estimates into later frames. Errors in the final reconstruction therefore reflect sensing, calibration, model assumptions, and state estimation together. Improvements to the landmark detector alone cannot resolve errors caused by single-view ambiguity, and additional viewpoints alone would not remove state-estimation errors. The two classes of limitation require different remedies.'),

# Scope: one subject in one controlled setup recorded three times is
# Section 9.7. The physically measured route is a set of tape measurements
# between marker-centre waypoints and is not registered into the
# calibrated world frame, so no distance from the reconstructed track to
# the physical path exists (Section 7.2, D-035 and D-036). The causal
# result is a replay of the recorded sequence at its recorded pace with no
# complete live-camera session validated (locked fact 9; Section 8.5).
# Sentence split for the 45-word gate (author's wording unchanged): the
# author wrote "... three controlled recordings; the physically measured
# object route ..." as one 46-word sentence; the semicolon is raised to a
# full stop and "the" capitalized.
(P, 'The contribution of this thesis is therefore both an integrated reconstruction system and an experimental characterization of what such a system can and cannot recover from one RGB-D viewpoint. The results demonstrate the feasibility of combining upper-body kinematics, independently tracked object motion, landmark-failure detection, object-assisted recovery, and causal graphical reconstruction within one architecture. They also identify the conditions under which that architecture loses observability and must rely on inference rather than direct measurement.'),

(P, 'The evaluation remains limited to one subject and three controlled recordings. The physically measured object route was not registered into the calibrated world frame, so no direct point-to-path accuracy was established. The causal implementation was evaluated through recorded replay rather than a complete live-camera session. The results should therefore be interpreted as evidence of system feasibility and of the value and limits of object-assisted kinematic reconstruction, rather than as a general accuracy claim across subjects, tasks, and environments.'),

(H2, "10.2 Future Work"),

(P, 'The first direction for future work is to extend the system from a single RGB-D viewpoint to a network of multiple calibrated sensors. The experiments in this thesis show that many of the remaining failures arise from occlusion and weak observability along the viewing direction, both of which are fundamental limitations of a single viewpoint. A multi-view system could place observations from several sensors into a common world coordinate frame and estimate the same anatomical or object point from more than one direction. When one sensor loses a wrist, elbow, hip, or object marker, another viewpoint may still retain a valid observation. Such a networked architecture would therefore reduce the dependence on reconstruction from a single incomplete image while preserving the metric scene representation developed in this work.'),

(P, 'A second direction is to modernize the human-pose detector. MediaPipe provides a lightweight landmark source, but the experiments show that it can return incorrect landmarks with apparently usable confidence, particularly during occlusion and complex human-object interaction. Future implementations could replace or supplement it with a more capable pose-estimation model designed for faster and more difficult motion.'),

(P, 'A practical example is the medium RTMPose model for real-time multi-person pose estimation. It could use the 17-keypoint layout of Common Objects in Context (COCO), with inference on a graphics processing unit (GPU) through Open Neural Network Exchange (ONNX) Runtime. Such a detector could be integrated without changing the overall system architecture: the detected image points would still be fused with RGB-D depth and passed to the same kinematic reconstruction layer. The main question would therefore become whether a stronger detector reduces the frequency and severity of the failures observed in this thesis while maintaining the throughput required for causal operation.'),

(P, 'A third direction is to introduce lightweight learned estimation into the recovery layer. The present system relies primarily on explicit geometric rules, remembered state, segment lengths, and the tracked object. These components are interpretable, but their performance degrades when the stored hand-object offset becomes outdated or when several measurements fail at the same time. A compact temporal model could use recent landmark history, detector confidence, object pose, kinematic state, and failure flags to estimate which measurements should be trusted and how missing states should be reconstructed. Rather than replacing the kinematic model, such a model could operate together with it, using learned temporal information to propose or weight estimates while the explicit kinematic chain continues to enforce geometric consistency. This would preserve the interpretability of the current system while allowing it to adapt to motion patterns that are difficult to capture with fixed thresholds and hand-designed state rules.'),

(P, "More broadly, the results of this thesis suggest that future progress should not be judged only by the performance of an individual detector, sensor, or algorithm. As continued improvements from hardware scaling become increasingly difficult and costly [49], system architecture and integration become more important. A simple pose detector, a depth sensor, a fiducial tracker, a kinematic model, and a temporal recovery mechanism each have clear limitations when used alone. When they are placed in a common coordinate system and designed to compensate for one another's failure modes, however, the resulting system can provide capabilities that no single component provides by itself."),

(P, 'This kind of complementary integration is one of the central goals of systems engineering. The objective is to improve each component and design the overall architecture so that the technologies compensate for limitations in other components and provide capabilities they lack individually.'),

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
    elif kind == P:
        doc.add_paragraph(item[1])
    elif kind == LIN:
        p = doc.add_paragraph(item[1])
        p.paragraph_format.left_indent = Inches(0.3)
    elif kind == CAP:
        p = doc.add_paragraph(item[1])
        p.runs[0].font.size = Pt(10)
        p.runs[0].font.italic = True
    elif kind == IMG:
        path = Path(item[1])
        assert path.exists(), f"missing figure: {path}"
        doc.add_picture(str(path), width=Inches(item[2]))
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

out = REPO / "writing" / "v8" / "condensed" / "Chapter_10_Conclusions_Future_Work.docx"
doc.save(out)
print("saved", out, "| items:", len(content))

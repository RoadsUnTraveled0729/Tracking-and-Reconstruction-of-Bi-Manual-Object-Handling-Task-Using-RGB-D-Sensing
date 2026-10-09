#!/usr/bin/env python3
"""Build the two concise change logs for the supervisor, one per chapter:
writing/v8/Thesis_V8_Changes_Ch4.docx and Thesis_V8_Changes_Ch5.docx.
Both cover V7 (as sent, the version he commented on 2026-09-05) to the
condensed V8 chapters of 2026-09-07, organised by his round 4 comments
(C22 to C29 for Chapter 5; Chapter 4 changed through his Chapter 2 comment
C46, the precision direction C38 and the condensation). Counts come from
the built chapter files (count_summary.py: prose plus captions plus
tables) and the builders (figures, tables, numbered equations). Same
format as make_ch2_ch3_changes.py."""
from pathlib import Path
from docx import Document
from docx.shared import Pt

REPO = Path(__file__).resolve().parents[3]
OUT4 = REPO / "writing" / "v8" / "Thesis_V8_Changes_Ch4.docx"
OUT5 = REPO / "writing" / "v8" / "Thesis_V8_Changes_Ch5.docx"


def new_doc(title, intro):
    doc = Document()
    st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11)
    doc.add_heading(title, level=1)
    doc.add_paragraph(intro)
    return doc


def table(doc, rows):
    t = doc.add_table(rows=len(rows), cols=len(rows[0])); t.style = "Table Grid"
    for i, r in enumerate(rows):
        for j, c in enumerate(r):
            cell = t.cell(i, j); cell.text = c
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(10); run.font.bold = (i == 0)


def numbered(doc, items):
    for head, body in items:
        p = doc.add_paragraph(style="List Number"); r = p.add_run(head + " "); r.bold = True; p.add_run(body)


def bullets(doc, items):
    for b in items:
        doc.add_paragraph(b, style="List Bullet")


# ------------------------------------------------------------------ Chapter 4
doc = new_doc(
    "Changes from V7 to V8: Chapter 4",
    "V7 is the version you have (sent 2026-09-05). Your Chapter 4 comments of 2026-09-07 are answered first. Before them the chapter had changed for three reasons: your Chapter 2 comment that the frames, the T notation and the calibration belong in Chapter 2; your direction that reported values stop at the sensor's precision; and the shortening of the whole thesis. No result or equation changed in content.")

doc.add_heading("How much changed", level=2)
table(doc, [["", "Chapter 4 (V7)", "Chapter 4 (V8)"],
            ["Words", "4059", "2034"],
            ["Sections", "4", "3 (old 4.1 moved to Chapter 2)"],
            ["Figures", "4", "2 (the new experiment figure and the track plot)"],
            ["Tables", "1", "0 (moved to Chapter 2 as Table 2.3)"],
            ["Numbered equations", "4", "3 (old (4.1) is now (2.1) in Chapter 2)"]])

doc.add_heading("Your comments of 2026-09-07 on Chapter 4", level=2)
numbered(doc, [
 ("Two decimals at most, in the matrices and in every number (your comment).",
  "Every printed number in the thesis now stops at two decimals: the two rotation matrices and the seven vectors of the worked example (Section 4.3), and beyond this chapter the arm lengths of the Chapter 5 example (31.7 and 20.5 centimetres, they were 0.317 and 0.205 metres), the session-clock times of the Chapter 6 example, the Hampel factor in Section 2.5 and Appendix F (about 1.48), and the worked examples and tables of Appendices C, D and E (visibility scores, depths, positions, the intrinsics, the marker table and the Rodrigues example, which was printed to six decimals). Rotation entries and unit vectors are rounded to two decimals, a near-zero entry is written 0.00, vectors in the equations are in metres with two decimals, and distances in the text stay in centimetres or millimetres with one decimal as you asked before. Where rounding would break a displayed calculation, the intermediate step is dropped and the result kept: the intermediate product of the world translation here, the trace arithmetic of the Rodrigues example, and the normalized-coordinate intervals of Appendix C. Every value is rounded from its full-precision source, not from the printed value. Chapters 1, 3, 7, 8 and 9 already met the rule."),
 ("Images of the experiment (your comment).",
  "New Figure 4.1 at the start of Section 4.1: four camera frames of the task, the grasp on the desk (frame 95), the lift onto the rail (505), the slide along the rail (700) and the far end of the rail (898), the same moments as the frame strip of Chapter 7. On each frame the detected object marker is outlined and its frame O is drawn from the pose the detector returns, the world frame W is drawn on the desk marker, and a magnified inset shows the cube. A short paragraph introduces the figure and says that the chain of Section 4.1 turns each such camera-relative pose into a world-frame pose. The track plot is now Figure 4.2."),
])

doc.add_heading("Chapter 4: Object Tracking and Scene Reconstruction (earlier changes, V7 to V8)", level=2)
numbered(doc, [
 ("Calibration moved to Chapter 2 (your comment on Chapter 2: define the frames and the T matrices there and include the calibration section).",
  "Old Section 4.1 Static Scene Calibration is now Section 2.2.2. The chordal-mean projection that was equation (4.1) is equation (2.1), and the frozen scene description that was Table 4.1 is Table 2.3. Chapter 4 now opens with the world anchoring and refers back to Section 2.2 for the frames and the calibrated anchor instead of defining them again. The remaining sections are renumbered: 4.1 World Anchoring and Camera Placement Invariance, 4.2 Filtering and Cleaning the Object Track, 4.3 Worked Example. The three remaining equations keep their content and are numbered (4.1) to (4.3)."),
 ("Duplicate figures removed (follows from your comment asking for one scene picture with the frames drawn).",
  "Old Figure 4.1 (the calibrated scene) and old Figure 4.2 (the three frames C, W and O drawn on the worked-example frame) are gone, because Figure 2.5 now draws the camera, world, wall and object frames on the recording with an arrow for each transformation. Old Figure 4.4 (the cleaning step around the one undetected frame) is also gone: the recording has a single undetected frame and the worked example states that row in numbers. The filter figure stays, as Figure 4.2 since the new experiment figure took the first place."),
 ("Shorter text, same content (the thesis was too long).",
  "The re-explanation of the Chapter 2 filter is one sentence pointing at Section 2.5, followed only by the rules that are specific to a pose track: a spiked pose is dropped whole, rotation is bridged along the shortest turn, a run at either end holds a fixed pose, an interior run longer than the bridging limit holds the previous valid pose, and rotation smoothing is the rolling chordal mean of equation (2.1). The block-by-block derivation of the inverse transformation is one sentence pointing at Section 3.1; equation (4.2) itself stays because the worked example prints it. The worked example is about half its old length and keeps every frame and every result: the anchor from the ten calibration detections, the gravity direction, the camera position in the world, the object pose of frame 533 through the chain, the height check, the one-frame bridge at frame 786 and the cleaning decision. Two unnumbered display matrices were dropped."),
 ("Precision (your direction: no finer than the sensor).",
  "The tilt of the desk marker card is printed as 32.0 degrees (it was 32.04). The matrix entries, which kept four decimals at that point, are at two decimals since your comment of 2026-09-07 above."),
])
doc.add_paragraph("Unchanged: the world anchoring chain and the invariance argument, the object frame, the cleaning rule of equation (4.3) with its two rate bounds, every printed value of the worked example, and the closing sentence that Chapter 5 starts from (the cleaned track gives, for every frame, either a measured pose of the cube in the world frame or a marked gap).")
doc.save(OUT4); print("saved", OUT4)

# ------------------------------------------------------------------ Chapter 5
doc = new_doc(
    "Changes from V7 to V8: Chapter 5",
    "V7 is the version you commented on (2026-09-05). The chapter was rewritten on the plan I sent you the same day: occlusion is missing data in an otherwise clean recording, the torso is assumed measured on every frame, and the chapter stays simple. This note lists what changed and which of your comments each change answers.")

doc.add_heading("How much changed", level=2)
table(doc, [["", "Chapter 5 (V7)", "Chapter 5 (V8)"],
            ["Words", "8225", "5925"],
            ["Sections", "6 (5.5 with seven subsections)", "6 (no subsections)"],
            ["Figures", "5", "5 (two new, two removed)"],
            ["Tables", "2", "1 (the notation table)"],
            ["Numbered equations", "23", "12"]])

doc.add_heading("Chapter 5: Pose Recovery During Tracking Failure", level=2)
doc.add_paragraph("The section order is now 5.1 Assumptions and Parameters, 5.2 Landmark Tracking Failures, 5.3 Grip Episodes and the Hand-Object Offset, 5.4 Wrist Recovery from the Object Pose, 5.5 Elbow Recovery by Two-Link Inverse Kinematics, 5.6 Worked Example.")
numbered(doc, [
 ("Readability (your comment: revise with AI but keep the style and the English).",
  "Every paragraph was redrafted in shorter and plainer sentences in the same style as Chapter 2. The method, the equations, the thresholds and the figures did not change in content."),
 ("Schematic for equations 5.1 and 5.2 (your comment).",
  "New Figure 5.3 sits directly under equation (5.2). Panel (a) shows the offset read off on a clean frame: the object axes at the marker origin, the measured wrist, and the displacement from the origin to the wrist expressed in the object's axes. Panel (b) shows the same offset carried to a later frame to place the wrist. The holding-state diagram that shared a figure with it is now Figure 5.4 on its own."),
 ("Define every variable (your comment).",
  "Table 5.1 at the head of Section 5.3 lists every symbol of the chapter with its meaning, the frame it lives in and where it comes from (the landmark numbers of Chapter 3, the object pose of Chapter 4). Each symbol is also defined at first use, and every letter now has one meaning: the offset observation on frame k is h_k (it was d, which also meant a depth sample), the gain of the direction memory is defined where that memory is introduced, at equation (5.5), and s is only the turn about the shoulder-to-wrist line."),
 ("The offset h is not known in general (your comment on comparing with the ground truth).",
  "A paragraph in Section 5.3, before equation (5.1), says it plainly: the wrist is not on the marker, the offset between the marker origin and the wrist is not known in advance and differs from grasp to grasp, in this work it is estimated from the frames of each grasp on which both the wrist and the marker are measured, and the reconstructed wrist is therefore read against the references of Chapter 7, the unmasked solve on withheld frames and the manual wrist labels on the natural failure windows."),
 ("How the chapter fits Chapters 3 and 4: a missing wrist from the shoulder and elbow (your comment).",
  "The opening now starts from the two products of Chapter 4 (a measured cube pose or a marked gap on every frame) and the Chapter 3 assumption of eight measured landmarks, places the chapter between the filtering of Chapter 2 and the solve of Chapter 3, and lists the missing-data cases in the words of the Chapter 3 chain. Case A: the wrist is missing while the shoulder and elbow are measured, so the wrist is placed at the calibrated forearm length from the elbow along the remembered forearm direction, equation (5.6). Case B: the wrist is missing while the hand holds the object, so the wrist is placed from the marker pose and the offset, equation (5.7). Case C: the elbow is missing while the shoulder and wrist are known, so the elbow follows by two-link inverse kinematics, equations (5.8) to (5.12). Each case names the Chapter 3 lengths and the Chapter 4 pose it uses."),
 ("Information flow diagram at the start of the chapter (your comment).",
  "New Figure 5.1 at the opening, drawn like Figure 3.1: on the left the inputs by chapter (filtered landmarks with their flags from Chapter 2, the chain and calibrated lengths from Chapter 3, the marker pose from Chapter 4); in the middle the failure detectors, the three rebuild cases and the unchanged Chapter 3 solve; on the right the joint groups with their states going to Chapters 6 and 7, and the state carried between frames. The old pipeline figure at the end of the chapter is gone."),
 ("Assumptions and parameters, and how each is obtained (your comment).",
  "New Section 5.1. Six assumptions in plain sentences: the recording is mostly clean, a failure is a short window, the torso is measured on every frame, the grasp is rigid within a grip episode, the marker stays visible while the hand is hidden, and the bone lengths are constant. Then the parameters in three kinds, calibrated constants, design values and carried states, each with how it is obtained from the recorded data and the section that states its value (the offset from the clean frames of each grasp, the arm lengths from the clean frames of the recording, the detector thresholds from a separate reference recording)."),
 ("Torso repair taken out (my plan: the torso is assumed measured).",
  "Section 5.5 of V7, the torso repair on camera rays with its seven subsections, equations (5.12) to (5.23) and Figure 5.4, is out of the chapter. The two torso detectors stay in Section 5.2 as a check on the assumption; their mask is reported, not acted on. The rail recording's hip depth, which that section used to repair, is now handled before the solve by the hip depth preparation described in Chapter 2 Section 2.6 (with the exact rules in Appendix G); Section 5.1 says so and Section 7.4 reports its effect."),
 ("Output states folded into the opening.",
  "The old Section 5.6 Output States of the Solver is gone. The three states, measured, held and constrained, are defined once in the opening, and the twist hold and the angle rate limit moved to the end of Section 5.5, where the elbow solve that needs them is."),
 ("New Section 5.6 Worked Example.",
  "One failure frame of the recording (frame 560, inside the natural wrist gap of the rail slide) is carried through equations (5.7) to (5.12) with every number printed: the wrist from the object pose (Case B), then the elbow by two-link inverse kinematics (Case C), in the same form as the worked example of Chapter 3."),
 ("Two decimals at most (your comment of 2026-09-07 on Chapter 4, applied to every chapter).",
  "The worked example states the two calibrated arm lengths as 31.7 and 20.5 centimetres, and the law of cosines is written with the lengths in centimetres (31.7, 50.7 and 20.5); they were printed as 0.317, 0.507 and 0.205 metres. The result, 0.98 and 11.0 degrees, is unchanged. No other number in the chapter had more than two decimals."),
 ("Two-handed wording.",
  "The opening no longer describes a handover in a two-handed task; Section 5.3 keeps only the general statement that a handover is two grip episodes that overlap."),
 ("Limits stated after the evaluation.",
  "Section 5.3 states a limit of the offset estimate: it follows a change of grip with a lag, so the value frozen at a failure can already be off. Section 5.5 states where the two-link construction is exact and what the clipping does outside that range, that the twist hold applies to a twist solved from measured landmarks, and what the 45-frame memory horizon does and does not bound. The closing paragraph points to the results against the manual wrist labels in Section 7.3.3. No equation changed."),
])

doc.add_heading("Equation and figure numbering, V7 to V8", level=2)
table(doc, [["V7", "V8", "What it is"],
            ["(5.1) to (5.4)", "(5.1) to (5.4)", "offset read-off, mean, recursive update (unchanged)"],
            ["prose only", "(5.5)", "direction memory with its gain (new as an equation)"],
            ["none", "(5.6)", "Case A wrist from the elbow along the forearm memory (new)"],
            ["(5.5)", "(5.7)", "Case B wrist from the object pose"],
            ["(5.7) to (5.11)", "(5.8) to (5.12)", "Case C two-link elbow"],
            ["(5.6), (5.12) to (5.23)", "removed", "reach inequality and the torso repair"],
            ["Figure 5.1", "Figure 5.2", "the failure detectors"],
            ["none", "Figure 5.1", "information flow (new)"],
            ["Figure 5.2 (a)", "Figure 5.3", "offset schematic, redrawn under equation (5.2)"],
            ["Figure 5.2 (b)", "Figure 5.4", "the holding state"],
            ["Figure 5.3", "Figure 5.5", "two-link elbow geometry"],
            ["Figures 5.4, 5.5", "removed", "torso repair; the old pipeline figure"],
            ["Tables 5.1, 5.2", "prose", "detector thresholds and joint groups, now in Section 5.2"],
            ["none", "Table 5.1", "notation (new)"]])
doc.save(OUT5); print("saved", OUT5)

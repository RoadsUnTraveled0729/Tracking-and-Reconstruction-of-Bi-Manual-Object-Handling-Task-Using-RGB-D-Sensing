#!/usr/bin/env python3
"""Build the concise change log for the supervisor for Chapter 6:
writing/v8/Thesis_V8_Changes_Ch6.docx. Covers V7 (as sent, the version he
commented on 2026-09-05) to the condensed V8 chapter of 2026-09-07. He made
no comment on Chapter 6; the chapter changed through his Chapter 2 comment
C46 (frames, T notation and calibration in Chapter 2) and the round 3 T
direction C15, the precision direction C38, the condensation, and a review
of every statement against the code (writing/reviews/Chapter_6_v8_round*.txt,
writing/v8/condensed/notes_ch6.md section (h)). The V8 word count is read
from the built chapter (count_words.py: prose plus captions plus tables);
the V7 count is the one CONDENSE_SUMMARY.md records for V7 as sent.
Same format as make_ch4_ch5_changes.py."""
import sys
from pathlib import Path
from docx import Document
from docx.shared import Pt

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "writing" / "v8" / "condensed" / "scripts"))
from count_words import count  # noqa: E402

OUT = REPO / "writing" / "v8" / "Thesis_V8_Changes_Ch6.docx"
CH6 = REPO / "writing" / "v8" / "condensed" / "Chapter_6_System_Integration.docx"
V7_WORDS = 4760
c = count(str(CH6)); V8_WORDS = c[0] + c[1] + c[3]


def new_doc(title, intro):
    doc = Document()
    st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11)
    doc.add_heading(title, level=1)
    doc.add_paragraph(intro)
    return doc


def table(doc, rows):
    t = doc.add_table(rows=len(rows), cols=len(rows[0])); t.style = "Table Grid"
    for i, r in enumerate(rows):
        for j, cell_text in enumerate(r):
            cell = t.cell(i, j); cell.text = cell_text
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(10); run.font.bold = (i == 0)


def numbered(doc, items):
    for head, body in items:
        p = doc.add_paragraph(style="List Number"); r = p.add_run(head + " "); r.bold = True; p.add_run(body)


doc = new_doc(
    "Changes from V7 to V8: Chapter 6",
    "V7 is the version you have (sent 2026-09-05). Your comment of 2026-09-07 on Chapter 4 (two decimals at most) is applied here too, and the worked example now shows the coordinate transformation with its numbers; both are listed first. Before them the chapter had changed for four reasons: your Chapter 2 comment that the frames, the T notation and the calibration belong in Chapter 2; your direction that reported values stop at the sensor's precision; the shortening of the whole thesis; and a check of every statement of the chapter against the code, which corrected a few descriptions. The shared-memory discussion and its memory block figures, which V7 had dropped, are back as Figures 6.2 and 6.3 with a worked example, and the Unity figure, now Figure 6.5, was recaptured after two display defects in the receiver were fixed; no table changed, and no equation changed in content; equation (6.2) gained a second line.")

doc.add_heading("How much changed", level=2)
table(doc, [["", "Chapter 6 (V7)", "Chapter 6 (V8)"],
            ["Words", str(V7_WORDS), str(V8_WORDS)],
            ["Sections", "4", "5, and 6.1 now has two subsections (a closing worked example, Section 6.5)"],
            ["Figures", "3", "5 (the frame buffer, Figure 6.2, and the combined record, Figure 6.3, one memory block each)"],
            ["Tables", "1", "2 (Table 6.2 collects the worked example)"],
            ["Numbered equations", "5", "5 (equation (6.2) now also in homogeneous form)"]])

doc.add_heading("Changes of 2026-09-07 (your Chapter 4 comments, applied to every chapter)", level=2)
numbered(doc, [
 ("Two decimals at most (your comment on the matrices and all numerical values).",
  "The session-clock times of the worked example are printed to two decimals (the frame published at 18.28 seconds, the merger's tick at 18.32 seconds, the render time 18.25 seconds; they were 18.280, 18.318 and 18.251). Where two times would then read the same, the text gives the offsets in whole milliseconds instead: the person samples of frames 547 and 548 lay 4 milliseconds before and 29 milliseconds after the render time. Table 6.2 follows. Every matrix and vector in the new calculation below is printed to two decimals; the numbers are computed at full precision from the calibration file and the frame 548 records by a small number source script, and the text says that a product formed from the printed entries can differ from the printed result in the last digit. That recomputation also corrected two values that V7 had rounded twice: the camera position in display axes is (−1.4, 43.1, −39.3) centimetres (was 43.2) and the cube's marker origin in the camera frame is (−20.6, 15.1, 102.1) centimetres (was −20.7)."),
 ("The coordinate transformation calculated in the worked example (my own follow-up: Section 6.2 gave the equation but Section 6.5 only quoted its results).",
  "Section 6.5 now runs equation (6.2) on the pelvis of frame 548 with its numbers: the rotation block and translation column of the calibrated camera pose, the anchor rotation A = S R_cam F and the swapped camera position S t_cam, the pelvis point q and the display point p_U = A q + S t_cam = (0.00, −0.21, 0.39) metres. It then shows the levelling of Section 6.4 as a matrix, the 32.0 degree turn that carries the calibrated gravity direction onto the screen's vertical, applied to p_U with the 71.6 centimetre raise to the floor, giving the scene point (0.00, 0.75, 0.44) metres where the spine bone lands. The object's path back through the link is shown the same way: the swap undone, then the anchor's rotation (the transpose of R_cam) and its translation, returning the cube's marker origin to the camera frame, (−0.21, 0.15, 1.02) metres. The results are the ones V7 quoted in prose."),
])

doc.add_heading("Chapter 6: System Integration and Graphical Reconstruction (earlier changes, V7 to V8)", level=2)
numbered(doc, [
 ("Frames and calibration now cited from Chapter 2 (your comment on Chapter 2).",
  "Where V7 said the calibration was in Chapter 4, the chapter now points at Section 2.2.2 for the calibrated anchor, the camera pose in the world, the gravity direction and the fitted tabletop plane, at Section 2.2.1 for the world frame, and at Table 2.3 for the frozen scene description the scene record carries. The twist hold is cited as Section 5.5 and the three output states as the opening of Chapter 5, following the Chapter 5 rewrite."),
 ("Homogeneous T matrix (your round 3 direction, and the T notation of Chapter 2).",
  "Equation (6.2), which maps a person-space point into the display frame, kept its rotation-and-translation line and gained a second line that writes the same map as one homogeneous matrix T_UP, with the block form [A, S t_cam; 0, 1]. The text names R_cam and t_cam as the rotation block and translation column of T_WC in Table 2.2, and the display point is written p_U as in equation (6.1). Table 2.2 in Chapter 2 now gives the world-to-Unity axis swap its symbol S with a pointer to equation (6.1)."),
 ("Precision (your direction: no finer than the sensor).",
  "The two frame readings under Figure 6.3 are printed at the sensor's precision: on frame 114 the elbow is bent by 14.4 degrees and on frame 700 by 31.0 (V7 said 14 and 31). The avatar height is 170 centimetres and the rig segment lengths are given to 0.1 centimetre. The hand distances under the figure are now measured on the rendered rig itself, see the next item."),
 ("Shared memory discussion and memory block figure restored (your request of 2026-08-03; dropped between V6 and V7).",
  "Section 6.1 again explains the transport in full, and it is now split into two subsections so that the two uses of shared memory are explained one after the other: 6.1.1 the frame buffer, which carries the images from the capture process to the two branches and is never read by Unity, and 6.1.2 the records, which carry the computed numbers from the branches through the merger to Unity. A new paragraph gives the frame buffer's geometry: eight fixed-size slots of about 1.5 megabytes, one aligned colour and depth pair each, behind a 128 byte header with the intrinsics, the clock origin and the count of published frames; frame n lands in slot n modulo 8, so a slow reader has eight frames before it is lapped. The sequence-counter protocol is written out again step by step (odd while writing, even when stable; the reader copies, re-reads the counter, and discards a torn copy), with the sizes of the four records. New Figure 6.2 draws the frame buffer as a memory block with the byte layout of one slot, and new Figure 6.3 the 112 byte combined record with its byte offsets and the write and read protocols beside it. Section 6.1 also says plainly that shared memory is used in two places: the frame buffer carries the images from the capture process to the two branches and never reaches Unity, and the records carry the computed numbers from the branches through the merger to Unity."),
 ("Worked example on one real frame (new Section 6.5, at your request for an example of how the data is managed).",
  "The chapter now closes, as Chapter 5 does, on one real frame: frame 548 of the rail recording replayed through the live structure of Chapter 8. The section follows the frame through the frame buffer (slot 4, session time 18.28 seconds), the person record (8.4 milliseconds; live bits down for the root and the right shoulder twist; root constrained, twist held), the object record (13.7 milliseconds; frame 547 not detected) and the merger's tick (render time 18.251 seconds; person interpolated between frames 547 and 548, object between 546 and 548 with the dropout flag). It then applies the maps of Sections 6.2 to 6.4 to the record's numbers: the pelvis from person space through the flip, the calibrated camera pose, the swap and the 32.0 degree levelling to its place in the scene, 2.8 centimetres above the drawn desk top; the object pose back from display axes to the camera frame; the right upper arm's rotation from the streamed angles, 0.2 degrees from the measured direction, and the forearm 6.9 degrees off through the held twist; and what the receiver draws for the states and flags. Table 6.2 collects the values."),
 ("Figure 6.5 (the Unity reconstruction, Figure 6.3 in V7) recaptured (two display defects fixed).",
  "The two frames are the same, 114 and 700, rendered again from the sensor's pose. The red spheres that mark a group the record does not carry as measured were drawn 20 centimetres toward the editor's monitor camera, so in the sensor view they floated beside the head and the hips instead of sitting on the joints; they now sit at the pelvis, the shoulder and the elbow of the group they mark. The rig's trunk length was the loop recording's 47.9 centimetres; on the rail recording the pelvis point the record carries is the corrected one and sits deeper than the raw hips, so that length placed the rig's shoulders about 10 centimetres below the measured ones and the hand reaching for the cube fell below the drawn desk top and was invisible. The trunk is now set per recording (57.6 centimetres on the rail recording) and the arm reaches for the cube on both frames. The desk marker card, whose calibrated centre lies 0.4 centimetres below the fitted tabletop plane, was cut in half by the drawn desk; it is now drawn over the desk slab and the text says why. The text under the figure gives the distance from the rendered hand to the measured wrist as logged by the receiver, 14.1 centimetres on frame 114 and 6.4 on frame 700, and splits the 14.1 into the held twist on a nearly straight elbow (8.9), the rig's shoulder joint sitting 5.7 centimetres deeper than the measured shoulder landmark (4) and the loop arm lengths (1). V7 quoted 9 and 2 centimetres from a forward-kinematics calculation with the rig's lengths, not from the rendered rig."),
 ("Descriptions corrected against the code.",
  "Every statement was checked against the capture, branch, merger and Unity code. Four descriptions changed. The merger's record flags mark an interpolated or blended stream; a held person shows in its group states and a held object lowers its live bit after a fixed staleness limit (V7 said the record states which of four states applies). Only the root orientation and the object pose travel as Euler angles; the ten arm angles travel as the joint angles of Section 3.4 and the receiver rebuilds each rotation from them as equation (6.4) states (V7 said every orientation travels as Euler angles; the matching sentence in Chapter 3 Section 3.4 was corrected with it). The landmark branch reuses the marker branch's swap and Euler routines through the one link between them (V7 said neither branch imports the other's code). The captures of Figure 6.3 come from the receiver that applies the T-pose and proportion corrections and reads only the live bits; the receiver on the merger's record draws the blue and amber markers but applies the height scale only. The receiver is also described as composing the transforms of Sections 6.2 to 6.4, not of 6.2 alone."),
 ("Arm segment lengths.",
  "The proportions paragraph now states the two calibrations side by side: the loop recording's lengths fixed in the rig (right upper arm 25.6 and forearm 25.2 centimetres) and the rail recording's calibrated lengths that its recovery ran on (31.7 and 20.5 centimetres, described in Section 5.1; V7 attributed them to Chapter 3). A direct measurement of the subject gives about 25 centimetres for both segments, so the loop values are close to the anatomy and the rail split is consistent with the elbow landmark sitting farther along the arm on that recording. Chapter 9 Table 9.1 carries the same limitation."),
 ("Shorter text, same content (the thesis was too long).",
  "The sequence-counter walkthrough is one sentence naming the lock-free protocol; the cross-branch object-pose inversion is one sentence pointing at the swap and the calibrated anchor; the startup ordering paragraph is gone; the person-record paragraph no longer re-defines the joint groups and states that Chapter 5 defines; the argument that an authored arm droop would be added to every angle is a pointer to Section 3.2.2; the ramp analysis of the display smoother is two sentences; and the wall, desk and marker-plate paragraphs of Section 6.4 are two paragraphs that cite Table 2.3 instead of relisting it. Kept in full: the four processes and the shared frame index, Table 6.1, the merger's four states, all of Section 6.2 with equations (6.1) to (6.3), the five driven bones with equations (6.4) and (6.5), the display smoother, the levelling, and Figures 6.1 to 6.3."),
 ("Readability (your general direction: keep the style and the English).",
  "Long sentences were split, passive sentences name who acts (the receiver, the merger, the avatar setup), and the internal labels of V7 (skew guard, person anchor, state tag, live mask) are plain words: the link rejects a late record, the anchor node, the state of a joint group, the live bits."),
])
doc.add_paragraph("Unchanged: the four-process architecture and Figure 6.1, the record family of Table 6.1 and its codes, the swap and the flip with their determinants, the anchor factorization of equation (6.3), the chain composition of equations (6.4) and (6.5), the T-pose requirement, the display smoother, the levelling under one parent node, and the two moments of the Unity figure.")
doc.save(OUT); print("saved", OUT, "| V8 words", V8_WORDS)

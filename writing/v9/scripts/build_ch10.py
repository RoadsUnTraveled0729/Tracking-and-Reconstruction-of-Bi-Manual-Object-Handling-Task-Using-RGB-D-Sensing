#!/usr/bin/env python3

"""Build writing/v9/Chapter_10_Conclusions_Future_Work.docx.

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

Condensation round 2 of 2026-09-15 (CONDENSE2_BRIEF.md, Chapter 10
items). The chapter was cut by deleting whole sentences of the author's
text, so every surviving sentence is still his wording, with two
exceptions recorded here and four new pointer sentences that send the
reader to Chapter 9 for the reasoning:

- The chapter opener that previewed Sections 10.1 and 10.2 was deleted
  in full, and the closing sentence of Section 10.2 that restated the
  systems-engineering objective with it.
- Section 10.1: the occlusion list, the inference-source list, the grip
  mechanism sentence, the dependency list of the conditional recovery,
  the five-item error-source list and the two-classes closing sentence
  were deleted; Sections 9.4 and 9.6 and Sections 9.3, 9.5 and 9.6 are
  now named in their place. The reasoning lives there.
- Section 10.1, contribution paragraph: the sentence listing the five
  combined components was deleted because the opening paragraph of the
  section already lists them, and "They also identify" became "The
  results also identify" so the pronoun keeps an antecedent. Two words,
  no other change to the sentence.
- Section 10.2: every future-work item is untouched. The coda that
  repeated Section 1.1 keeps its first two sentences, including the
  citation [49], and the closing sentence of the systems-engineering
  paragraph; the component-list sentence and the compensation sentence
  that followed it were deleted together, since the second depends on
  the first for its subject.

No number, equation or citation was retyped, and no sentence carrying a
number was altered. Details and escalations in
writing/v9/notes_condense2_ch10.md.

Language fix pass of 2026-09-15 (writing/reviews/
Chapter_10_condense2_round1.txt), inside the same deletion-only rule:

- The three pointer sentences moved to the end of their paragraphs, so a
  claim and its consequence stay adjacent, and were reworded to carry
  the antecedents the cut removed (the landmark failures, the grip
  mechanism and the conditions the recovery depends on). Pointer wording
  is mine, not the author's.
- Section 10.1, contribution paragraph: the sentence beginning "The
  results also identify the conditions under which that architecture
  loses observability" was deleted, because the cut had left "that
  architecture" without an antecedent and the second paragraph of the
  section already states the same limit. The two-word pronoun repair
  recorded above is withdrawn with it, so every surviving sentence of
  Section 10.1 is again the author's exact wording.
- Section 10.2: the closing sentence "This kind of complementary
  integration is one of the central goals of systems engineering" was
  deleted, because "this kind" and "complementary" referred to the
  component list deleted before it. The chapter now ends on the
  architecture and integration sentence with its citation [49].

Round 3 language fix pass of 2026-09-15 (writing/reviews/
Chapter_10_condense2_round3.txt, 7 certain flags). Word-level edits are
confined to the certain repeated-connective and repeated-phrase flags,
as the round-3 instruction allows for this chapter, and each is listed
in writing/v9/notes_condense2_ch10.md so the author can revert it:
"therefore" dropped in four places (Sections 10.1 and 10.2, two kept);
"rather than" replaced by "and not" twice and by "Instead of" once
(three kept); the reporting frame "The experiments also show that"
dropped from the second paragraph of Section 10.1; and "such a model"
became "such a temporal model" in the learned-estimation paragraph,
where two different models were called "model" in one clause.

Two of the author's sentences deleted in the condensation are restored
to the second paragraph of Section 10.1, because the reviewer asks for
the full statement of the single-view limit to sit in the conclusions:
"Motion along the viewing direction is only weakly constrained." and
"Some failures therefore remain even if the landmark detector itself is
improved.", the latter without its "therefore" under the connective
edit above. The duplicate of that finding in the first future-work
paragraph was deleted in exchange.

The three pointer sentences became one, at the end of that same
paragraph, naming Sections 9.3 to 9.6. The bare pointer of the
error-source paragraph and the pointer of the recovery paragraph are
gone.

The opening sentence of the closing paragraph of Section 10.2 was
deleted, so the chapter ends on the hardware-scaling sentence and its
citation [49].

Author decision of 2026-09-15: Chapter 10 is excluded from the language
iterations. Every word-level edit of the round-3 pass is reverted, so
the author's exact wording of a95b31e is back: the four dropped
"therefore", the three "rather than" replacements, the dropped reporting
frame "The experiments also show that" and "such a temporal model". The
whole-sentence deletions and restorations of the condensation stand, and
so does the one pointer sentence naming Sections 9.3 to 9.6. Verified
sentence by sentence: every sentence of the chapter except that pointer
is byte-identical to the same sentence in a95b31e.

Reference [50] (Lopez-Nava and Munoz-Melendez) remains uncited. The
author approved removing it from writing/v9/references.md, but
it is not the last entry ([51] to [58] follow it), so removal was
withheld and escalated rather than performed.

What the replacement means for the open Chapter 7 integration items
(CH7_INTEGRATION_FIXLIST.md, section build_ch10.py):

- 10-1, 10-2: the object detection count and the wrist-to-marker
  comparison are simply absent from the author's text, so the D-038
  reading of the wrist-to-marker check has no Chapter 10 element to
  limit. Section 7.3.3 and Section 9.3 carry it.
- 10-3, 10-4: the manual label counts and the "only slow windows"
  description of Section 7.4.1 are absent. The author's recovery
  paragraph states the loop right-hand and left-hand outcomes
  qualitatively and prints no label counts.
- 10-5: the unregistered physical route survives as a scope statement in
  the closing paragraph of Section 10.1, with no point-to-path distance
  claimed, which is what Sections 7.2 and 9.8 state.
- 10-6: no hip-hold future-work item remains, so the withdrawal of the
  hip-hold comparison from Section 9.5 leaves nothing here to support.
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
rate against Section 9.8, Section 8.4 and locked fact 9 of
REVISION_2026-09-11_BRIEF.md.

2026-09-16, C54 (D-128): the verbatim rule of 2026-09-12 is lifted by
the author; chapter rewritten into lead paragraphs plus bullets. The
supervisor's C54 comment asks Chapter 10 to introduce bullets and
shorten its descriptions; author decision D-128 lifts the 2026-09-12
verbatim-text rule for this round only (C54_BRIEF.md). Every surviving
sentence below is a rewrite, not a deletion-only cut of the author's own
wording as in the earlier rounds, and the author will read the result
before it is treated as final.

count_words: prose 857 before this pass, 426 after. Section 10.1 (lead
paragraph plus five bullets) 282 words; Section 10.2 (lead sentence,
three bullets, closing sentence) 144 words. check_style.py: 0 hits.
dump_docx.py: "17-keypoint" and "[49]" present; the only other digits in
the text are the section numbers of the headings and the "Sections 9.2
to 9.5" pointer.

What is kept unchanged in content, because other material depends on it:
- The opening paragraph's six-item component list (RGB-D body landmarks,
  fiducial object tracking, an explicit upper-body kinematic model,
  failure detection, object-assisted pose recovery, graphical
  reconstruction in Unity) keeps its order and its content, because
  build_ch1.py's docstring records that Section 1.3 depends on this
  sentence naming the five stages of the investigation (measurement,
  human reconstruction, independent object observation, object-assisted
  constraint, integration).
- "17-keypoint" is still the only number in the chapter besides the
  citation marker [49].
- The pointer sentence is renumbered from "Sections 9.3 to 9.6" to
  "Sections 9.2 to 9.5" under the C54_BRIEF.md Chapter 9 renumbering map
  (former 9.3 -> 9.2, 9.6 -> 9.5), and now sits inside the first bullet
  of Section 10.1 instead of at the end of a paragraph.
- The hardware-scaling sentence and its citation [49] close the chapter,
  unchanged in meaning, as prose rather than as a bullet.
- The loop right-hand recovery outcome, the absence of a left-hand
  improvement, "one subject and three controlled recordings", the
  unregistered physical route and the causal-replay-not-live-camera
  distinction all survive as bullet content; no fact, number or citation
  from the previous round is dropped.

Two glossary corrections, made now that the verbatim lock is lifted
(escalated but withheld in condensation round 2 under that lock; see
notes_condense2_ch10.md item 4 and this round's notes_c54_ch10.md):
"hold-last baseline" -> "hold-last solve", and "the medium RTMPose
model" -> "RTMPose-m", both matching GLOSSARY.md exactly. "Common
Objects in Context (COCO)" is shortened to "COCO 17-keypoint layout",
which keeps the literal "17-keypoint" substring while folding the worked
example into one bullet with the pose-detector future-work item.

Full sentence-by-sentence map from the previous text to the new lead
paragraphs and bullets, the word counts, and the checker output are in
writing/v9/notes_c54_ch10.md.

2026-09-16, third pass (author): the supervisor asked for bullets in
Chapter 10, so the two numbered lists of the prose pass (three
conclusions, three future-work directions) are emitted as bullets; text
unchanged.

2026-09-16, C55 (supervisor): the three conclusion bullets and the three
future-work bullets are rewritten in layman's terms with no bold labels;
the lead paragraph of 10.1 and the author's closing sentence with [49]
are unchanged; the contribution and scope paragraph points at Chapter 9
instead of Sections 9.2 to 9.5, which no longer exist.
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches

H1, H2, P = "h1", "h2", "p"
CAP, TBL, LIN, IMG = "cap", "tbl", "lin", "img"
BUL = "bul"  # bullet item (supervisor comment C54, 2026-09-16)
NUM = "num"  # numbered item (C54 mechanics follow-up, 2026-09-16; see list_numbering.py)

REPO = Path(__file__).resolve().parents[3]

# Second pass of the C54 round (2026-09-16, author's feedback on the first
# delivery: "10.2 sounds like ai", too many bullets): lead paragraphs in
# the author's plain voice, one numbered list of three conclusions in
# 10.1 and one numbered list of three directions in 10.2, no bold labels.
# The component list of the first paragraph keeps its order (Section 1.3
# relies on it). Word target 420 to 480.
content = [
(H1, "Chapter 10: Conclusions and Future Work"),

(H2, "10.1 Conclusions"),

# Causal operation at approximately the recorded frame rate: locked fact 9
# of REVISION_2026-09-11_BRIEF.md (E-026), printed in Section 8.4 as
# "about 29 frames per second".
(P, 'This thesis develops and evaluates a single-view RGB-D framework for reconstructing upper-body motion together with the motion of a manipulated object in a shared metric scene. The framework combines RGB-D body landmarks, fiducial object tracking, an explicit upper-body kinematic model, failure detection, object-assisted pose recovery, and graphical reconstruction in Unity, with body and object motion expressed in one calibrated world frame. Under the tested conditions, the system reconstructed the torso, both arms, and the tracked object from one consumer-grade RGB-D camera, and the same architecture also operated causally at approximately the recorded frame rate.'),

(P, 'The results support the following points.'),

# Observability: the author's paragraph of 2026-09-12, condensed.
(BUL, "", "A single camera cannot see everything. Hands disappear behind the object or the desk, and distance along the line of sight is hard to judge, so some joints are hidden or poorly placed with any detector. The recovery layer that fills those gaps is therefore a needed part of the system, not a cosmetic filter."),

# Natural failure outcomes: Section 7.4.2, Table 7.9 (5.2 cm against 11.4
# and 17.6 on the right; 13.1 against 12.3 and 12.7 on the left). Glossary
# term "hold-last solve".
(BUL, "", "Using the object's position to place a hidden hand helped on one hand in one recording and did not help on the other hand. It works only under the right conditions: the stored hand-to-object distance must still be current and the arm must not point straight at the camera, and even then the evidence is a handful of frames rather than a general rule. A good wrist position on its own also does not prove that the whole arm is right."),

(BUL, "", "The errors come from the parts interacting, not from one weak part. A better detector alone would still leave the parts of the scene hidden from a single camera, and more cameras alone would still leave the errors that come from carrying old values forward, so no single upgrade removes them."),

# Contribution and scope. Pointer renumbered to Sections 9.2 to 9.5 under
# the C54 map. Scope: Section 9.7; route not registered (Section 7.2);
# replay, no live session (locked fact 9, Section 8.5).
(P, 'The contribution is a working integrated system together with a full account, in Chapter 9, of the motion it can and cannot recover from one camera. The evaluation covers one person and three controlled recordings. The physical route was never lined up in the same frame of reference as the reconstruction, so no point-to-path accuracy was established, and the live version was tested by replaying a recording rather than with a camera in the room. The results show that the approach works; they are not a general accuracy claim.'),

(H2, "10.2 Future Work"),

(P, 'The current system struggles when the stored hand-to-object distance goes out of date or when several measurements fail at the same time. Future work can take three directions.'),

(BUL, "", "The first is more cameras looking from different sides. Several cameras placed around the scene could see the parts hidden from one alone, so calibrated cameras watching the same wrist, elbow, hip or marker would leave far fewer gaps to fill, while everything would still be measured in the same shared scene."),

# RTMPose-m / COCO-17 / ONNX Runtime (GLOSSARY.md); "17" is the only
# numeral besides [49].
(BUL, "", "The second is a newer, more reliable pose detector. The current detector, MediaPipe, sometimes places a landmark on the wrong body part with high confidence. A stronger model such as RTMPose-m, using the COCO-17 keypoint layout and running on a graphics card through ONNX Runtime, could make such mistakes rarer without changing the rest of the system, provided the detector stays fast enough for live use."),

(BUL, "", "The third is a small learned model that judges which measurements to trust. It would look at the recent landmark history, the current pose, the detector's confidence, the failure flags and the object's position, and weigh them. The kinematic chain would keep the geometry consistent so that the arm can never take an impossible shape."),

# Hardware-scaling closing sentence, the author's own, unchanged;
# citation [49] kept exactly, as approved 2026-09-12.
(P, 'As continued improvements from hardware scaling become increasingly difficult and costly [49], system architecture and integration become more important.'),

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

out = REPO / "writing" / "v9" / "Chapter_10_Conclusions_Future_Work.docx"
from list_numbering import restart_numbered_lists
restart_numbered_lists(doc)

doc.save(out)
print("saved", out, "| items:", len(content))

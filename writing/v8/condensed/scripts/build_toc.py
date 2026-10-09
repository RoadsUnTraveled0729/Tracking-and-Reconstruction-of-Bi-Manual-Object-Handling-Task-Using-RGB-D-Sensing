#!/usr/bin/env python3
"""Build writing/v8/condensed/Thesis_V8_Condensed_TOC.docx: the condensed
thesis table of contents (copy of writing/v7/scripts/build_toc.py,
repointed 2026-09-06).

Rewrite round of 2026-08-26 (after the R5 experiment freeze). Structure:
the supervisor-shaped Chapters 1-3 and the appendix set are kept; the
middle and back are restructured around the completed R5 work:
  - New Chapter 5 "Pose Recovery During Tracking Failure" (the
    contribution; was only future-work item 8.3.5 in the old TOC).
  - Evaluation rebuilt around the designed 8-waypoint path (replaces
    the Lifting/Rotating/Passing scenario sections).
  - Old Ch 8 + 9 merged into one closing chapter; "Data Fusion" and all
    honesty-framed sections dropped; old 2.2 comms preliminaries moved
    into the integration chapter.
  - Appendices reordered by first appearance in the body (provisional
    lettering, verified against the built text before shipping - see
    skill_set/thesis-structure-rules.md).
  - No question-style titles; no speed information anywhere (the task
    is defined as slow movement).
"""
import pathlib
from docx import Document
from docx.shared import Pt, Inches

TITLE = "TRACKING AND RECONSTRUCTION OF BI-MANUAL OBJECT HANDLING TASK USING RGB-D SENSING"

# (level, text): 0 = top-level line (bold), 1 = section, 2 = subsection
# The body entries are read from the built condensed chapter and appendix
# documents (Heading 1, 2 and 3 paragraphs, in order), so the contents
# list and the assembly's heading-order check always match what was
# built. The front-matter lines are fixed.
from docx import Document as _Doc
from docx.oxml.ns import qn as _qn

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_BODY = ["Chapter_1_Introduction.docx", "Chapter_2_Experimental_Setup.docx",
         "Chapter_3_Kinematic_Modeling.docx", "Chapter_4_Object_Tracking.docx",
         "Chapter_5_Pose_Recovery.docx", "Chapter_6_System_Integration.docx",
         "Chapter_7_Evaluation.docx", "Chapter_8_Real_Time_Feasibility.docx",
         "Chapter_9_Discussion.docx", "Chapter_10_Conclusions_Future_Work.docx",
         "Appendices.docx"]


def _body_entries():
    out = []
    for name in _BODY:
        path = _ROOT / name
        if not path.exists():
            continue
        for para in _Doc(path).element.body.iter(_qn("w:p")):
            st = para.find(".//" + _qn("w:pStyle"))
            style = st.get(_qn("w:val")) if st is not None else ""
            text = "".join(t.text or "" for t in para.iter(_qn("w:t"))).strip()
            if not text:
                continue
            if style in ("Heading1", "Heading 1"):
                out.append((0, text))
            elif style in ("Heading2", "Heading 2"):
                out.append((1, text))
            elif style in ("Heading3", "Heading 3"):
                out.append((2, text))
    out.append((0, "References"))
    return out


entries = [
(0, "Approval"),
(0, "Abstract"),
(0, "Acknowledgements"),
(0, "List of Figures"),
(0, "List of Tables"),
(0, "List of Equations"),
(0, "Glossary"),
] + _body_entries()

doc = Document()
style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(12)

t = doc.add_paragraph()
r = t.add_run(TITLE)
r.font.bold = True
t.alignment = 1

s = doc.add_paragraph()
r = s.add_run("Table of Contents (V7 rewrite)")
r.font.italic = True
s.alignment = 1

doc.add_paragraph()

for level, text in entries:
    p = doc.add_paragraph()
    run = p.add_run(text)
    if level == 0:
        run.font.bold = True
        p.paragraph_format.space_before = Pt(10)
    else:
        p.paragraph_format.left_indent = Inches(0.3 * level)
    p.paragraph_format.space_after = Pt(2)

out = str(pathlib.Path(__file__).resolve().parents[1] / "Thesis_V8_Condensed_TOC.docx")
doc.save(out)
print("saved", out, "| entries:", len(entries))

#!/usr/bin/env python3
"""Build writing/v4/Thesis_V4.docx: the merged full thesis.

Order per writing/v4/STRUCTURE.md: Chapters 1-9, then one consolidated
References section, then the Appendix. This script performs the single
citation renumbering pass decided on 2026-07-28:
  - citations are renumbered by order of first appearance in the final text;
  - the meaning of an old number is chapter-local (each chapter script's
    references dict), which resolves the old [15] collision: the Chapter 1
    paper and the Chapter 3 paper are different entries and end up with
    different final numbers;
  - the two author-list variants of the old [26] (MediaPipe Hands) are
    unified to the full-author form.
It also prints the old-to-new mapping used to update references.md.

Chapter content is imported from the sibling build_chN.py / build_appendix.py
scripts (importing them rebuilds the per-chapter docx as a side effect, which
is harmless and keeps everything in sync).
"""
import importlib.util
import os
import re
import sys

from docx import Document
from docx.shared import Pt, Inches

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eqn import add_display_eq, add_display_math, add_inline_math

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "/home/luo/Desktop/New_SandBox/writing/v6/Thesis_V6.docx"
OUT_P1 = "/home/luo/Desktop/New_SandBox/writing/v6/Thesis_V6_Part1_Ch1-3.docx"
OUT_P2 = "/home/luo/Desktop/New_SandBox/writing/v6/Thesis_V6_Part2_Ch4-9_App.docx"

H1, H2, H3, P, IMG, CAP, TBL, EQ = "h1", "h2", "h3", "p", "img", "cap", "tbl", "eq"
MATH = "mth"  # displayed, unnumbered worked-example mathematics
CODE = "code"  # monospace code listing (Appendix D capture snippet)
LIN = "lin"   # numbered/itemized list entry (indented paragraph)
PM = "pm"     # paragraph mixing text runs and inline math

MODULES = [f"build_ch{n}" for n in range(1, 10)] + ["build_appendix"]

# The old [26] appears in two author-list variants; canonicalize to the full form.
MP_HANDS_SHORT = 'F. Zhang et al., "MediaPipe Hands: On-device real-time hand tracking," arXiv:2006.10214, 2020.'
MP_HANDS_FULL = ('F. Zhang, V. Bazarevsky, A. Vakunov, A. Tkachenka, G. Sung, C.-L. Chang, '
                 'and M. Grundmann, "MediaPipe Hands: On-device real-time hand tracking," '
                 'arXiv:2006.10214, 2020.')


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def canonical(ref):
    return MP_HANDS_FULL if ref == MP_HANDS_SHORT else ref


CITE = re.compile(r"\[(\d+)\]")

chapters = [load(m) for m in MODULES]

new_num = {}      # canonical ref string -> final number
final_refs = {}   # final number -> ref string
old_to_new = []   # (module, old, new) for the report

merged = []
for mod in chapters:
    refs = {n: canonical(s) for n, s in mod.references.items()}
    remap = {}

    def sub(match):
        old = int(match.group(1))
        assert old in refs, f"{mod.__name__}: cites [{old}] but its references dict has no entry"
        key = refs[old]
        if key not in new_num:
            new_num[key] = len(new_num) + 1
            final_refs[new_num[key]] = key
        if old not in remap:
            remap[old] = new_num[key]
            old_to_new.append((mod.__name__, old, new_num[key]))
        return f"[{remap[old]}]"

    for item in mod.content:
        kind = item[0]
        if kind in (P, CAP, H1, H2, H3, LIN):
            merged.append((kind, CITE.sub(sub, item[1])))
        elif kind == PM:
            merged.append((PM, [(t, CITE.sub(sub, v) if t == "t" else v)
                                for t, v in item[1]]))
        elif kind == TBL:
            merged.append((TBL, [[CITE.sub(sub, c) for c in row] for row in item[1]]))
        else:
            merged.append(item)
    if mod.__name__ == "build_ch9":
        merged.append((H1, "References"))
        # placeholder; the reference paragraphs are inserted after the scan of
        # the appendix module completes (its first-appearance numbers must be
        # known), so remember the insertion point.
        merged.append(("REFS_HERE",))

# splice the finished reference list into the placeholder position
idx = merged.index(("REFS_HERE",))
ref_items = [(P, f"[{n}] {final_refs[n]}") for n in sorted(final_refs)]
merged[idx:idx + 1] = ref_items

# ---------------------------------------------------------------------------
# Front matter (user request 2026-08-03, format of the supplied SFU thesis
# model PDF): title page, Approval, Abstract, Acknowledgments, Contents,
# List of Figures, List of Tables, all before Chapter 1. Front matter pages
# are numbered i, ii, iii, ... (title page unnumbered); the body restarts at
# arabic 1. Contents and the two lists are real Word TOC fields (headings
# 1-2 and the FigureCaption / TableCaption paragraph styles), updated by
# Word on open via the updateFields setting.

from docx.enum.style import WD_STYLE_TYPE
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

TITLE_LINES = ["TRACKING AND RECONSTRUCTION OF",
               "BI-MANUAL OBJECT HANDLING TASK USING RGB-D",
               "SENSING"]
TITLE_ONELINE = ("Tracking and Reconstruction of Bi-Manual Object Handling "
                 "Task Using RGB-D Sensing")
AUTHOR = "Lanqing Luo"
SUPERVISOR = "Dr. Shahram Payandeh"
DEPT = "Department of Engineering Science"

ABSTRACT = ("This thesis develops a system that tracks a person's upper body "
    "and a hand-held object during two-handed object handling, using one "
    "RGB-D camera and three printed fiducial markers, and reconstructs the "
    "motion in a metric virtual scene. Two independent processing pipelines "
    "are built. A landmark pipeline lifts pose landmarks from the colour and "
    "depth streams to metric 3D positions and solves thirteen joint angles "
    "through a kinematic model built entirely in rotation matrices. A marker "
    "pipeline tracks printed fiducial markers to calibrate the room and to "
    "follow the carried object in a world frame anchored to the desk. The "
    "two pipelines share no code and no data and meet only through one "
    "calibrated transform, so their agreement on the carried object measures "
    "the accuracy of the whole system: on the evaluation recording the "
    "landmark-tracked wrist and the wrist predicted from the object pose "
    "agree to a median of 1.0 centimetre while the wrist is fully visible, "
    "and to 4.6 centimetres while the carried box occludes it. A causal "
    "real-time variant of the same system runs inside the 33.3 millisecond "
    "frame budget at about 100 milliseconds of latency, with a measured "
    "median joint-angle cost below one degree relative to the offline "
    "output. Every quantity that is held or bridged rather than measured is "
    "flagged, and the flags travel with the data to the rendered scene.")

ACKNOWLEDGMENTS = ("I would like to thank my supervisor, Dr. Shahram "
    "Payandeh, for the guidance and support given throughout this work.")

# Short titles for the List of Equations (user request 2026-08-04). Each
# numbered equation gets an invisible Word TC entry field ({ TC "..." \f E })
# in its tag cell; the List of Equations page is { TOC \f E }, so Word
# computes the page numbers itself, exactly like the other lists.
EQ_TITLES = {
    "3.1":  "Person space from camera coordinates, the y-axis flip",
    "3.2":  "Change of basis into a parent frame",
    "3.3":  "Torso right axis from the hip line",
    "3.4":  "Spine-side vector",
    "3.5":  "Torso forward axis",
    "3.6":  "Torso up axis closing the frame",
    "3.7":  "Root rotation matrix from the frame axes",
    "3.8":  "ZXY Euler convention as a matrix product",
    "3.9":  "The composed ZXY rotation matrix",
    "3.10": "Euler angle extraction from the rotation matrix",
    "3.11": "Swing-twist shoulder parameterization",
    "3.12": "Upper-arm direction under the swing alone",
    "3.13": "Swing elevation from the arm direction",
    "3.14": "Swing azimuth from the arm direction",
    "3.15": "Forearm mapped back by undoing the swing",
    "3.16": "Shoulder twist from the de-swung forearm",
    "3.17": "Elbow angles from the forearm direction",
    "3.18": "World rotation applied to an avatar bone",
    "4.1":  "Projection of the mean matrix onto the rotations",
    "4.2":  "Object pose in the world frame",
    "4.3":  "Closed-form inverse of a rigid transformation",
    "4.4":  "Geodesic interpolation across a gap",
    "5.1":  "The person anchor into the scene",
    "B.1":  "Pinhole projection of a camera-frame point",
    "B.2":  "Deprojection of a pixel with depth",
    "D.1":  "Rodrigues' rotation formula",
}


def _center(doc, text, size=12, bold=False):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    return p


def _blank(doc, n=1):
    for _ in range(n):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)


def _add_field(p, instr):
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    begin.set(qn("w:dirty"), "true")
    r = p.add_run(); r._r.append(begin)
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = instr
    r = p.add_run(); r._r.append(it)
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    r = p.add_run(); r._r.append(end)


def _footer_page_number(section):
    section.footer.is_linked_to_previous = False
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _add_field(p, "PAGE")


def _set_page_number_format(section, fmt, start=None):
    sectPr = section._sectPr
    pgNumType = sectPr.find(qn("w:pgNumType"))
    if pgNumType is None:
        pgNumType = OxmlElement("w:pgNumType")
        sectPr.append(pgNumType)
    pgNumType.set(qn("w:fmt"), fmt)
    if start is not None:
        pgNumType.set(qn("w:start"), str(start))


def add_front_matter(doc):
    # --- title page (unnumbered) ------------------------------------------
    sec = doc.sections[0]
    sec.different_first_page_header_footer = True
    _set_page_number_format(sec, "lowerRoman", start=1)
    _footer_page_number(sec)

    _blank(doc, 3)
    for line in TITLE_LINES:
        _center(doc, line, size=14)
    _blank(doc)
    _center(doc, "by")
    _blank(doc)
    _center(doc, AUTHOR)
    _blank(doc, 2)
    _center(doc, "An honours thesis submitted in partial fulfillment", size=11)
    _center(doc, "of the requirements for the degree of", size=11)
    _center(doc, "Bachelor of Applied Science", size=11)
    _center(doc, "in Systems Engineering", size=11)
    _blank(doc)
    _center(doc, "Supervisor:", size=11)
    _center(doc, SUPERVISOR, size=11)
    _blank(doc)
    _center(doc, DEPT, size=11)
    _center(doc, "Simon Fraser University", size=11)
    _center(doc, "Burnaby, British Columbia", size=11)
    _blank(doc)
    _center(doc, f"© {AUTHOR} 2026", size=11)
    _center(doc, "Summer 2026", size=11)
    _blank(doc)
    _center(doc, "All rights reserved. This work may not be", size=11)
    _center(doc, "reproduced in whole or in part, by photocopy", size=11)
    _center(doc, "or other means, without the permission of the author.", size=11)
    doc.add_page_break()

    # --- approval page -----------------------------------------------------
    _center(doc, "APPROVAL", size=13, bold=True)
    doc.add_paragraph()
    from docx.enum.text import WD_TAB_ALIGNMENT
    for label, value in [("Name:", AUTHOR),
                         ("Degree:", "Bachelor of Applied Science "
                                     "in Systems Engineering"),
                         ("Title of Thesis:", TITLE_ONELINE)]:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(1.8),
                                                  WD_TAB_ALIGNMENT.LEFT)
        run = p.add_run(label + "\t")
        run.font.bold = True
        p.add_run(value)
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run("Examining Committee:").font.bold = True
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run("Supervisor:").font.bold = True
    p = doc.add_paragraph("\t\t\t_________________________________________")
    doc.add_paragraph("\t\t\t" + SUPERVISOR)
    doc.add_paragraph("\t\t\t" + DEPT + ", Simon Fraser University")
    for _ in range(3):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run("\t\t\tDate Approved: ").font.bold = True
    p.add_run("_______________________")
    doc.add_page_break()

    # --- abstract ----------------------------------------------------------
    doc.add_heading("Abstract", level=1)
    doc.add_paragraph(ABSTRACT)
    doc.add_page_break()

    # --- acknowledgments ---------------------------------------------------
    doc.add_heading("Acknowledgments", level=1)
    doc.add_paragraph(ACKNOWLEDGMENTS)
    doc.add_page_break()

    # --- contents and lists (Word fields, updated on open) -----------------
    doc.add_heading("Contents", level=1)
    _add_field(doc.add_paragraph(), r'TOC \o "1-2" \h \z')
    doc.add_page_break()
    doc.add_heading("List of Figures", level=1)
    _add_field(doc.add_paragraph(), r'TOC \h \z \t "FigureCaption,1"')
    doc.add_page_break()
    doc.add_heading("List of Tables", level=1)
    _add_field(doc.add_paragraph(), r'TOC \h \z \t "TableCaption,1"')
    doc.add_page_break()
    doc.add_heading("List of Equations", level=1)
    _add_field(doc.add_paragraph(), r'TOC \f E \h \z')

    # body starts in a new section with arabic numbering from 1
    body = doc.add_section(WD_SECTION.NEW_PAGE)
    body.different_first_page_header_footer = False
    _set_page_number_format(body, "decimal", start=1)
    _footer_page_number(body)

    # ask Word to refresh all fields (TOC, lists, page numbers) on open
    settings = doc.settings.element
    upd = OxmlElement("w:updateFields")
    upd.set(qn("w:val"), "true")
    settings.append(upd)


def _caption_styles(doc):
    for name in ("FigureCaption", "TableCaption"):
        if name not in [s.name for s in doc.styles]:
            st = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
            st.base_style = doc.styles["Normal"]
            st.font.size = Pt(10)
            st.font.italic = True


def render(items, out, front_matter=False):
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    _caption_styles(doc)
    if front_matter:
        add_front_matter(doc)

    for item in items:
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
        elif kind == PM:
            p = doc.add_paragraph()
            for typ, val in item[1]:
                if typ == "t":
                    p.add_run(val)
                else:
                    add_inline_math(p, val)
        elif kind == EQ:
            add_display_eq(doc, item[1], item[2])
            # invisible TC entry in the tag cell for the List of Equations
            tag = item[2]
            assert tag in EQ_TITLES, f"no List of Equations title for ({tag})"
            cell_p = doc.tables[-1].rows[0].cells[1].paragraphs[0]
            _add_field(cell_p, f'TC "{tag}  {EQ_TITLES[tag]}" \\f E')
        elif kind == MATH:
            add_display_math(doc, item[1])
        elif kind == CODE:
            for line in item[1].split("\n"):
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.3)
                p.paragraph_format.space_after = Pt(0)
                run = p.add_run(line if line else " ")
                run.font.name = "Courier New"
                run.font.size = Pt(9)
        elif kind == IMG:
            doc.add_picture(item[1], width=Inches(item[2]))
        elif kind == CAP:
            p = doc.add_paragraph(item[1])
            if item[1].startswith("Figure"):
                p.style = doc.styles["FigureCaption"]
            elif item[1].startswith("Table"):
                p.style = doc.styles["TableCaption"]
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

    doc.save(out)
    print("saved", out)


render(merged, OUT, front_matter=True)

# Two-part delivery split (user request, 2026-07-28): Part 1 is Chapters 1-3,
# Part 2 is Chapters 4-9 with References and the Appendix. Citation numbers
# stay global (first appearance over the whole thesis), so the parts read
# identically to the merged document. Part 1 gets its own copy of the full
# consolidated References so its citations resolve.
ch4_idx = next(i for i, it in enumerate(merged)
               if it[0] == H1 and it[1].startswith("Chapter 4"))
part1 = merged[:ch4_idx] + [(H1, "References")] + ref_items
part2 = merged[ch4_idx:]
render(part1, OUT_P1)
render(part2, OUT_P2)
print("final reference count:", len(final_refs))
print("\nold-to-new map (first use per module):")
for name, old, new in old_to_new:
    print(f"  {name}: [{old}] -> [{new}]")

#!/usr/bin/env python3
"""Build writing/v7/FrontMatter_V7.docx: the V7 thesis front matter.

Answers supervisor comments C1 (title page in the Eng.Sci. thesis format,
with the other examining committee members listed) and C2 (abstract in the
student's own voice, stating that the tracked object trajectory is compared
with the ground truth, the path defined in the laboratory that the person
follows).

Contents, in order: title page, approval page, abstract, acknowledgments,
table of contents, list of figures, list of tables, list of equations.

The contents and the three lists are self-paginating Word fields. Each
field carries a generated result, so the entries are visible before the
document is ever opened in Word and the page numbers appear as soon as the
fields are updated. The contents field reads headings 1 to 3; the two
caption lists read the FigureCaption and TableCaption paragraph styles that
the assembler puts on every caption; the equation list reads the TC entries
the assembler puts in each equation number cell. The generated results come
from the entry list of build_toc.py, which stays the single source for the
finalized structure, and from a scan of the built chapter documents, so
neither can drift from the text. Importing build_toc also rebuilds
Thesis_V7_TOC.docx.

This module also owns the house style used by the assembled thesis
(apply_house_style), so the front matter and every merged chapter share one
look: Times New Roman throughout, black, no theme fonts and no theme
colours anywhere.

PLACEHOLDER LIST
----------------
Every value below is printed in the document as bold text inside square
brackets, so it cannot be missed on a read-through. The same list is
written to Thesis_V7_Placeholders.md by build_thesis.py.

  [CHAIR NAME], [CHAIR AFFILIATION]
      Approval page, examining committee, chair row. Unknown.
  [COMMITTEE MEMBER NAME], [ROLE], [AFFILIATION]   (three rows)
      Approval page, examining committee. Unknown: the supervisor asked
      for the other members and the repository holds no names (C1).
  [DATE APPROVED]
      Approval page, signature block. Unknown.
  [ACKNOWLEDGEMENTS]
      Acknowledgments page, whole body. To be written by the author.
  [UPDATE FIELDS IN WORD: F9]
      Top of the contents page. Not a value to supply: the contents and
      the three lists are Word fields carrying a generated result, so
      they show their entries straight away and pick up page numbers
      when the fields are updated (in Word select all and press F9, in
      LibreOffice use Tools, Update, Update All). Delete the note once
      the fields are updated.

Values taken from the repository rather than placed as placeholders (they
are recorded in writing/v6/scripts/build_thesis.py and should still be
confirmed by the author): author name, supervisor name, degree,
department, university, and the date on the title page.

Run: python writing/v7/scripts/build_frontmatter.py
"""
import importlib.util
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

HERE = Path(__file__).resolve().parent
V7 = HERE.parent
REPO = V7.parent.parent
OUT = V7 / "FrontMatter_V7.docx"

# ---------------------------------------------------------------------------
# Identity block. Recorded values come from the V6 front matter builder
# (writing/v6/scripts/build_thesis.py); unknown values are bold placeholders.
# ---------------------------------------------------------------------------
AUTHOR = "Lanqing Luo"
SUPERVISOR = "Dr. Shahram Payandeh"
DEGREE = "Bachelor of Applied Science in Systems Engineering"
DEGREE_SHORT = "Bachelor of Applied Science"
DEPARTMENT = "School of Engineering Science"
UNIVERSITY = "Simon Fraser University"
UNIVERSITY_PLACE = "Burnaby, British Columbia, Canada"
TITLE_MIXED = ("Tracking and Reconstruction of Bi-Manual Object Handling Task "
               "Using RGB-D Sensing")
DATE = "Summer 2026"
COPYRIGHT_YEAR = "2026"

PH_CHAIR = "[CHAIR NAME]"
PH_CHAIR_AFF = "[CHAIR AFFILIATION]"
PH_MEMBER = "[COMMITTEE MEMBER NAME]"
PH_ROLE = "[ROLE]"
PH_AFFIL = "[AFFILIATION]"
PH_DATE_APPROVED = "[DATE APPROVED]"
PH_ACK = "[ACKNOWLEDGEMENTS]"
PH_UPDATE = "[UPDATE FIELDS IN WORD: F9]"

# Placeholder registry: (token, where it appears). Written out by
# build_thesis.py as Thesis_V7_Placeholders.md.
PLACEHOLDERS = [
    (PH_CHAIR, "Approval page, examining committee, chair row"),
    (PH_CHAIR_AFF, "Approval page, examining committee, chair row"),
    (PH_MEMBER, "Approval page, examining committee, three member rows"),
    (PH_ROLE, "Approval page, examining committee, three member rows"),
    (PH_AFFIL, "Approval page, examining committee, three member rows"),
    (PH_DATE_APPROVED, "Approval page, signature block"),
    (PH_ACK, "Acknowledgments page, whole body"),
    (PH_UPDATE, "Top of the contents page"),
]

ABSTRACT = [
    "This thesis develops a system that tracks a person's upper body and a "
    "hand-held object during an object-handling task at a desk, using one "
    "consumer-grade RGB-D camera and three printed fiducial markers, and "
    "reconstructs the motion in a metric virtual scene.",

    "The system runs two measurement chains over the same recording. The "
    "first lifts pose landmarks from the registered colour and depth "
    "streams into metric three-dimensional positions, and a kinematic model "
    "written in rotation matrices turns those positions into a torso pose "
    "and four joint angles per arm. The second reads the printed markers, "
    "fixes one world frame on the desk, and follows the carried cube in "
    "that frame. The two chains share only the recorded frames and the "
    "world frame, so one of them can stand in for the other when it fails. "
    "When the landmark detector loses a wrist behind the object or behind "
    "the other hand, the wrist is restored from the object pose and the "
    "elbow from two-link inverse kinematics, and the torso is repaired on "
    "camera rays when the hip depth is corrupt.",

    "The task slides the cube along a straight wooden rail set level on "
    "the desk, so the straight line of the rail is the ground truth of "
    "this work. The tracked object trajectory is compared with that line, "
    "and over the slide the trajectory sits a median of 0.97 centimetres "
    "from it, with a 95th percentile of 2.36 centimetres. The recovery is "
    "graded against known truth by removing landmarks from frames the "
    "tracker handled correctly. A causal version of the same feature set "
    "runs at 29.6 frames per second, so the reconstruction a viewer sees "
    "is the reconstruction the offline chapters evaluate. Every reported "
    "quantity is labelled as measured, repaired, or held, and the label "
    "travels with the data to the rendered scene.",
]

CHAPTER_FILES = [
    "Chapter_1_Introduction.docx",
    "Chapter_2_Experimental_Setup.docx",
    "Chapter_3_Kinematic_Modeling.docx",
    "Chapter_4_Object_Tracking.docx",
    "Chapter_5_Pose_Recovery.docx",
    "Chapter_6_System_Integration.docx",
    "Chapter_7_Evaluation.docx",
    "Chapter_8_Real_Time_Feasibility.docx",
    "Chapter_9_Discussion_Conclusion.docx",
    "Appendices.docx",
]

def xml_text(el):
    """Plain text of an element.

    lxml's itertext cannot be used here: python-docx gives w:p, w:r and w:t
    their own text properties, so itertext returns the same string once per
    level. Reading the w:t nodes directly gives each character once.
    """
    return "".join(t.text or "" for t in el.findall(".//" + qn("w:t")))


CAPTION_RE = re.compile(r"^(Figure|Table)\s+([A-F]|\d+)\.(\d+)\.\s*(.*)$")
EQTAG_RE = re.compile(r"^\((\d+|[A-F])\.(\d+)\)$")


# ---------------------------------------------------------------------------
# House style
# ---------------------------------------------------------------------------
BODY_FONT = "Times New Roman"
PPR_ORDER = ["w:pStyle", "w:keepNext", "w:keepLines", "w:pageBreakBefore",
             "w:numPr", "w:spacing", "w:ind", "w:jc", "w:outlineLvl"]
RPR_ORDER = ["w:rStyle", "w:rFonts", "w:b", "w:bCs", "w:i", "w:iCs",
             "w:caps", "w:smallCaps", "w:strike", "w:dstrike", "w:outline",
             "w:shadow", "w:emboss", "w:imprint", "w:noProof", "w:snapToGrid",
             "w:vanish", "w:webHidden", "w:color", "w:spacing", "w:w",
             "w:kern", "w:position", "w:sz", "w:szCs", "w:highlight", "w:u",
             "w:effect", "w:bdr", "w:shd", "w:fitText", "w:vertAlign",
             "w:rtl", "w:cs", "w:em", "w:lang", "w:eastAsianLayout",
             "w:specVanish", "w:oMath"]
STYLE_ORDER = ["w:name", "w:aliases", "w:basedOn", "w:next", "w:link",
               "w:autoRedefine", "w:hidden", "w:uiPriority", "w:semiHidden",
               "w:unhideWhenUsed", "w:qFormat", "w:locked", "w:personal",
               "w:personalCompose", "w:personalReply", "w:rsid", "w:pPr",
               "w:rPr"]


def _child(parent, tag, order):
    """Find or create a direct child, keeping the schema's element order."""
    el = parent.find(qn(tag))
    if el is not None:
        return el
    el = OxmlElement(tag)
    idx = order.index(tag)
    for sib in parent:
        name = sib.tag.split("}")[-1]
        sib_tag = "w:" + name
        if sib_tag in order and order.index(sib_tag) > idx:
            sib.addprevious(el)
            return el
    parent.append(el)
    return el


def _set_rfonts(rPr):
    rf = _child(rPr, "w:rFonts", RPR_ORDER)
    for attr in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
        if rf.get(qn("w:" + attr)) is not None:
            del rf.attrib[qn("w:" + attr)]
    for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
        rf.set(qn("w:" + attr), BODY_FONT)


def _set_color_black(rPr):
    col = _child(rPr, "w:color", RPR_ORDER)
    for attr in ("themeColor", "themeTint", "themeShade"):
        if col.get(qn("w:" + attr)) is not None:
            del col.attrib[qn("w:" + attr)]
    col.set(qn("w:val"), "000000")


def _set_size(rPr, pt):
    for tag in ("w:sz", "w:szCs"):
        el = _child(rPr, tag, RPR_ORDER)
        el.set(qn("w:val"), str(int(pt * 2)))


def _set_toggle(rPr, tag, on):
    el = rPr.find(qn(tag))
    if on:
        el = _child(rPr, tag, RPR_ORDER)
        el.set(qn("w:val"), "1")
    elif el is not None:
        el.set(qn("w:val"), "0")


def style_paragraph(pPr, *, line=None, before=None, after=None,
                    keep_next=False, page_break=False):
    if line is not None or before is not None or after is not None:
        sp = _child(pPr, "w:spacing", PPR_ORDER)
        if line is not None:
            sp.set(qn("w:line"), str(int(line * 240)))
            sp.set(qn("w:lineRule"), "auto")
        if before is not None:
            sp.set(qn("w:before"), str(int(before * 20)))
        if after is not None:
            sp.set(qn("w:after"), str(int(after * 20)))
    if keep_next:
        _child(pPr, "w:keepNext", PPR_ORDER)
        _child(pPr, "w:keepLines", PPR_ORDER)
    if page_break:
        _child(pPr, "w:pageBreakBefore", PPR_ORDER)


def define_style(doc, name, *, size, bold=False, italic=False, line=None,
                 before=None, after=None, keep_next=False, page_break=False):
    define_style_element(doc.styles[name].element, size=size, bold=bold,
                         italic=italic, line=line, before=before, after=after,
                         keep_next=keep_next, page_break=page_break)


def define_style_element(el, *, size, bold=False, italic=False, line=None,
                         before=None, after=None, keep_next=False,
                         page_break=False):
    pPr = _child(el, "w:pPr", STYLE_ORDER)
    style_paragraph(pPr, line=line, before=before, after=after,
                    keep_next=keep_next, page_break=page_break)
    rPr = _child(el, "w:rPr", STYLE_ORDER)
    _set_rfonts(rPr)
    _set_color_black(rPr)
    _set_size(rPr, size)
    _set_toggle(rPr, "w:b", bold)
    _set_toggle(rPr, "w:bCs", bold)
    _set_toggle(rPr, "w:i", italic)
    _set_toggle(rPr, "w:iCs", italic)


LIST_STYLES = [
    ("TOC1", "toc 1", 0.0),
    ("TOC2", "toc 2", 0.25),
    ("TOC3", "toc 3", 0.5),
    ("TableofFigures", "table of figures", 0.25),
]
CAPTION_STYLES = [("FigureCaption", "Figure Caption"),
                  ("TableCaption", "Table Caption")]


def add_generated_styles(doc):
    """Entry styles for the four lists and the two caption styles.

    The caption styles are what the two caption lists key on, so every
    figure caption and every table caption in the assembled thesis carries
    one of them. The entry styles carry the names Word expects, so an
    update of the fields keeps the indents built here.
    """
    from docx.enum.style import WD_STYLE_TYPE
    existing = {st.style_id for st in doc.styles}
    for style_id, word_name, indent in LIST_STYLES:
        if style_id in existing:
            continue
        st = doc.styles.add_style(style_id, WD_STYLE_TYPE.PARAGRAPH)
        st.element.set(qn("w:styleId"), style_id)
        st.element.find(qn("w:name")).set(qn("w:val"), word_name)
        st.base_style = doc.styles["Normal"]
        define_style_element(st.element, size=12, line=1.0, after=2)
        st.paragraph_format.left_indent = Inches(indent)
    for style_id, word_name in CAPTION_STYLES:
        if style_id in existing:
            continue
        st = doc.styles.add_style(style_id, WD_STYLE_TYPE.PARAGRAPH)
        st.element.set(qn("w:styleId"), style_id)
        st.element.find(qn("w:name")).set(qn("w:val"), word_name)
        st.base_style = doc.styles["Normal"]
        define_style_element(st.element, size=11, line=1.0, before=4,
                             after=14)


def _fix_doc_defaults(doc):
    root = doc.styles.element
    defaults = root.find(qn("w:docDefaults"))
    if defaults is None:
        return
    rpr_default = defaults.find(qn("w:rPrDefault"))
    if rpr_default is not None:
        rPr = _child(rpr_default, "w:rPr", ["w:rPr"])
        _set_rfonts(rPr)
        _set_size(rPr, 12)
    ppr_default = defaults.find(qn("w:pPrDefault"))
    if ppr_default is not None:
        pPr = _child(ppr_default, "w:pPr", PPR_ORDER)
        style_paragraph(pPr, line=1.5, after=6)


def _fix_theme(doc):
    """Point the theme's major/minor fonts at the body font.

    Nothing in the built document references a theme font once the styles
    are redefined, but rewriting the theme removes the last Calibri and
    Cambria strings from the package.
    """
    for part in doc.part.package.iter_parts():
        if part.partname.endswith("theme1.xml"):
            blob = part.blob.decode("utf-8")
            new = re.sub(r'typeface="(?:Calibri|Cambria)[^"]*"',
                         f'typeface="{BODY_FONT}"', blob)
            part._blob = new.encode("utf-8")
            return


def apply_house_style(doc):
    """One look for the whole thesis: Times New Roman, black, no theme."""
    define_style(doc, "Normal", size=12, line=1.5, after=6)
    define_style(doc, "Heading 1", size=16, bold=True, line=1.0,
                 before=0, after=14, keep_next=True, page_break=True)
    define_style(doc, "Heading 2", size=14, bold=True, line=1.0,
                 before=14, after=8, keep_next=True)
    define_style(doc, "Heading 3", size=12, bold=True, line=1.0,
                 before=12, after=6, keep_next=True)
    define_style(doc, "Caption", size=11, line=1.0, before=4, after=14)
    add_generated_styles(doc)
    _fix_doc_defaults(doc)
    _fix_theme(doc)


def scrub_runs(paragraph_el, drop=("w:rFonts", "w:color", "w:sz", "w:szCs",
                                   "w:i", "w:iCs", "w:b", "w:bCs")):
    """Remove run-level overrides so the paragraph style governs the look."""
    for rPr in paragraph_el.iter(qn("w:rPr")):
        if rPr.getparent().tag != qn("w:r"):
            continue
        for tag in drop:
            for el in rPr.findall(qn(tag)):
                rPr.remove(el)


# ---------------------------------------------------------------------------
# Front matter content helpers
# ---------------------------------------------------------------------------
def _centered(doc, text, size=12, bold=False, space_after=4):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    style_paragraph(p._p.get_or_add_pPr(), line=1.0, after=space_after)
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    return p


def _centered_placeholder(doc, text, size=12, space_after=4):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    style_paragraph(p._p.get_or_add_pPr(), line=1.0, after=space_after)
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0, 0, 0)
    return p


def _blank(doc, n=1):
    for _ in range(n):
        p = doc.add_paragraph()
        style_paragraph(p._p.get_or_add_pPr(), line=1.0, after=0)


def _plain(doc, text, *, line=1.0, after=6, indent=None, bold=False):
    p = doc.add_paragraph()
    style_paragraph(p._p.get_or_add_pPr(), line=line, after=after)
    if indent is not None:
        p.paragraph_format.left_indent = Inches(indent)
    run = p.add_run(text)
    run.font.bold = bold
    return p


def _mixed(doc, parts, *, line=1.0, after=6, indent=None):
    """Paragraph of (text, is_placeholder) runs; placeholders are bold."""
    p = doc.add_paragraph()
    style_paragraph(p._p.get_or_add_pPr(), line=line, after=after)
    if indent is not None:
        p.paragraph_format.left_indent = Inches(indent)
    for text, is_ph in parts:
        run = p.add_run(text)
        run.font.bold = bool(is_ph)
    return p


def _set_page_number_format(section, fmt, start=None):
    sectPr = section._sectPr
    pg = sectPr.find(qn("w:pgNumType"))
    if pg is None:
        pg = OxmlElement("w:pgNumType")
        sectPr.append(pg)
    pg.set(qn("w:fmt"), fmt)
    if start is not None:
        pg.set(qn("w:start"), str(start))


def field_run(kind, dirty=False):
    el = OxmlElement("w:fldChar")
    el.set(qn("w:fldCharType"), kind)
    if dirty:
        el.set(qn("w:dirty"), "true")
    r = OxmlElement("w:r")
    r.append(el)
    return r


def instr_run(text):
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = text
    r = OxmlElement("w:r")
    r.append(it)
    return r


def text_run(text):
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    r = OxmlElement("w:r")
    r.append(t)
    return r


def add_tc_field(paragraph_el, entry):
    """Hidden table-of-contents entry, the source of the equation list."""
    paragraph_el.append(field_run("begin"))
    paragraph_el.append(instr_run(f'TC "{entry}" \\f E'))
    paragraph_el.append(field_run("end"))


def add_field_list(doc, instr, lines, empty_style):
    """A Word list field carrying a generated result.

    The result paragraphs sit between the separate and end field
    characters, which is how Word stores a table of contents it has
    already built. Word and LibreOffice both show the generated entries on
    open and both replace them, page numbers included, when the fields are
    updated.
    """
    rows = lines or [(empty_style, "")]
    paragraphs = []
    for style_id, text in rows:
        p = doc.add_paragraph()
        pPr = p._p.get_or_add_pPr()
        ps = OxmlElement("w:pStyle")
        ps.set(qn("w:val"), style_id)
        pPr.insert(0, ps)
        p._p.append(text_run(text))
        paragraphs.append(p._p)
    first, last = paragraphs[0], paragraphs[-1]
    first.insert(1, field_run("separate"))
    first.insert(1, instr_run(instr))
    first.insert(1, field_run("begin", dirty=True))
    last.append(field_run("end"))
    return paragraphs


def _add_field(paragraph, instr):
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    r = paragraph.add_run()
    r._r.append(begin)
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = instr
    r = paragraph.add_run()
    r._r.append(it)
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    r = paragraph.add_run()
    r._r.append(end)


def _footer_page_number(section):
    section.footer.is_linked_to_previous = False
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _add_field(p, "PAGE")


# ---------------------------------------------------------------------------
# Scans of the built chapters
# ---------------------------------------------------------------------------
def _load_toc():
    spec = importlib.util.spec_from_file_location("build_toc",
                                                  HERE / "build_toc.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def scan_captions():
    """Return (figures, tables) as lists of (label, first sentence)."""
    figures, tables = [], []
    for name in CHAPTER_FILES:
        path = V7 / name
        if not path.exists():
            print(f"WARNING: {name} is missing, its captions are not listed")
            continue
        doc = Document(str(path))
        for para in doc.paragraphs:
            m = CAPTION_RE.match(para.text.strip())
            if not m:
                continue
            kind, major, minor, rest = m.groups()
            label = f"{kind} {major}.{minor}"
            first = rest.split(". ")[0].rstrip(".")
            entry = (label, first)
            (figures if kind == "Figure" else tables).append(entry)
    return figures, tables


def scan_equations():
    """Return (tag, owning section heading) for every numbered equation."""
    out = []
    for name in CHAPTER_FILES:
        path = V7 / name
        if not path.exists():
            continue
        doc = Document(str(path))
        section = ""
        for el in doc.element.body:
            tag = el.tag.split("}")[-1]
            if tag == "p":
                text = xml_text(el).strip()
                pstyle = el.find(qn("w:pPr"))
                sname = None
                if pstyle is not None:
                    st = pstyle.find(qn("w:pStyle"))
                    if st is not None:
                        sname = st.get(qn("w:val"))
                if sname in ("Heading1", "Heading2", "Heading3") and text:
                    section = text
            elif tag == "tbl":
                if el.find(".//" + qn("m:oMath")) is None:
                    continue
                texts = [xml_text(c).strip() for c in el.iter(qn("w:tc"))]
                for t in texts:
                    m = EQTAG_RE.match(t)
                    if m:
                        out.append((t, section))
                        break
    return out


def parse_references():
    """Reference entries from the tracked list, numbering unchanged."""
    path = V7 / "references.md"
    entries = []
    for line in path.read_text().splitlines():
        m = re.match(r"^-\s*\[(\d+)\]\s+(.*)$", line.strip())
        if m:
            entries.append((int(m.group(1)), m.group(2)))
    entries.sort(key=lambda e: e[0])
    return entries


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def add_title_page(doc, title):
    _blank(doc, 3)
    for line in _wrap_title(title):
        _centered(doc, line, size=15, bold=True, space_after=2)
    _blank(doc, 2)
    _centered(doc, "by")
    _blank(doc)
    _centered(doc, AUTHOR, size=13)
    _blank(doc, 2)
    _centered(doc, "A thesis submitted in partial fulfillment", size=11)
    _centered(doc, "of the requirements for the degree of", size=11)
    _centered(doc, DEGREE_SHORT, size=11)
    _centered(doc, "in Systems Engineering", size=11)
    _blank(doc, 2)
    _centered(doc, "in the", size=11)
    _centered(doc, DEPARTMENT, size=11)
    _centered(doc, "Faculty of Applied Sciences", size=11)
    _blank(doc, 2)
    _centered(doc, UNIVERSITY, size=11)
    _centered(doc, UNIVERSITY_PLACE, size=11)
    _blank(doc, 2)
    _centered(doc, DATE, size=11)
    _blank(doc, 2)
    _centered(doc, f"Copyright {AUTHOR} {COPYRIGHT_YEAR}", size=11)
    _centered(doc, "All rights reserved. This work may not be reproduced in "
                   "whole or in part,", size=10, space_after=0)
    _centered(doc, "by photocopy or other means, without the permission of "
                   "the author.", size=10)


def _wrap_title(title, width=46):
    words, lines, cur = title.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def add_approval_page(doc, title):
    doc.add_heading("Approval", level=1)
    for label, value in [("Name:", AUTHOR),
                         ("Degree:", DEGREE),
                         ("Title:", TITLE_MIXED)]:
        p = doc.add_paragraph()
        style_paragraph(p._p.get_or_add_pPr(), line=1.0, after=10)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(1.6),
                                                  WD_TAB_ALIGNMENT.LEFT)
        p.add_run(label + "\t").font.bold = True
        p.add_run(value)
    _blank(doc)
    _plain(doc, "Examining Committee:", bold=True, after=10)

    _mixed(doc, [(PH_CHAIR, True), (", Chair", False)], indent=0.3, after=0)
    _mixed(doc, [(PH_CHAIR_AFF, True)], indent=0.3, after=12)

    _mixed(doc, [(SUPERVISOR, False), (", Supervisor", False)],
           indent=0.3, after=0)
    _plain(doc, f"{DEPARTMENT}, {UNIVERSITY}", indent=0.3, after=12)

    for _ in range(3):
        _mixed(doc, [(PH_MEMBER, True), (", ", False), (PH_ROLE, True)],
               indent=0.3, after=0)
        _mixed(doc, [(PH_AFFIL, True)], indent=0.3, after=12)

    _blank(doc, 2)
    _mixed(doc, [("Date Approved: ", False), (PH_DATE_APPROVED, True)],
           indent=0.3, after=6)


def add_abstract(doc):
    doc.add_heading("Abstract", level=1)
    for para in ABSTRACT:
        _plain(doc, para, line=1.5, after=8)


def add_acknowledgments(doc):
    doc.add_heading("Acknowledgments", level=1)
    _mixed(doc, [(PH_ACK, True)], line=1.5, after=8)


def _heading(doc, text, style_id="Heading1"):
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    ps = OxmlElement("w:pStyle")
    ps.set(qn("w:val"), style_id)
    pPr.insert(0, ps)
    p.add_run(text)
    return p


def add_contents(doc, entries):
    # TOC Heading keeps the contents page out of its own list; it inherits
    # the look and the page break from Heading 1.
    _heading(doc, "Table of Contents", style_id="TOCHeading")
    _mixed(doc, [(PH_UPDATE, True)], after=10)
    rows = [(f"TOC{min(level + 1, 3)}", text) for level, text in entries]
    add_field_list(doc, r'TOC \o "1-3" \h \z \u', rows, "TOC1")


def add_list_of(doc, heading, rows, style_id):
    doc.add_heading(heading, level=1)
    lines = [("TableofFigures", f"{label}. {text}.") for label, text in rows]
    add_field_list(doc, f'TOC \\h \\z \\t "{style_id},1"', lines,
                   "TableofFigures")


def equation_entry(tag, section):
    return f"Equation {tag} in {section}"


def add_list_of_equations(doc, rows):
    doc.add_heading("List of Equations", level=1)
    lines = [("TableofFigures", equation_entry(tag, section))
             for tag, section in rows]
    add_field_list(doc, r"TOC \f E \h \z", lines, "TableofFigures")


# ---------------------------------------------------------------------------
def build():
    toc = _load_toc()
    doc = Document()
    apply_house_style(doc)

    sec = doc.sections[0]
    sec.different_first_page_header_footer = True
    _set_page_number_format(sec, "lowerRoman", start=1)
    _footer_page_number(sec)

    add_title_page(doc, toc.TITLE)
    add_approval_page(doc, toc.TITLE)
    add_abstract(doc)
    add_acknowledgments(doc)
    add_contents(doc, toc.entries)

    figures, tables = scan_captions()
    add_list_of(doc, "List of Figures", figures, "FigureCaption")
    add_list_of(doc, "List of Tables", tables, "TableCaption")
    add_list_of_equations(doc, scan_equations())

    body = doc.add_section(WD_SECTION.NEW_PAGE)
    body.different_first_page_header_footer = False
    _set_page_number_format(body, "decimal", start=1)
    _footer_page_number(body)

    doc.save(str(OUT))
    words = sum(len(p.split()) for p in ABSTRACT)
    print(f"saved {OUT}")
    print(f"abstract words: {words} | figures listed: {len(figures)} | "
          f"tables listed: {len(tables)} | toc entries: {len(toc.entries)}")
    assert 250 <= words <= 350, f"abstract is {words} words, wanted 250 to 350"
    return doc


if __name__ == "__main__":
    build()

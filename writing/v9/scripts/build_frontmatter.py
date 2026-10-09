#!/usr/bin/env python3
"""Build writing/v9/FrontMatter_V9.docx: the front matter of
the condensed thesis (copy of writing/v7/scripts/build_frontmatter.py,
repointed 2026-09-06).
Audit pass (2026-09-06, MATH_LOGIC_REVIEW.md M01, M08): the abstract
separates the live path from the display smoother. Its treatment of the
rail and of the wrist labels was replaced on 2026-09-12 by the Chapter 7
integration pass recorded above the ABSTRACT list: the object result is
now the physical tape comparison of Section 7.2, and the natural
occlusion outcome is the loop recording alone (D-033).

Answers supervisor comments C1 (title page in the Eng.Sci. thesis format,
with the other examining committee members listed) and C2 (abstract in the
student's own voice, stating that the tracked object trajectory is compared
with the ground truth, the path defined in the laboratory that the person
follows).

Contents, in order: title page, approval page, abstract, acknowledgments,
table of contents, list of figures, list of tables, glossary (added
2026-09-07 at the user's request; the list of equations was dropped on
2026-09-14 at the supervisor's request).

The contents and the two lists are self-paginating Word fields. Each
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
      Retired 2026-10-06 (post-defence revision): the approval date is
      now the real value DATE_APPROVED, and the Approval page carries the
      signed scan (see add_approval_page).
  [ACKNOWLEDGEMENTS]
      Acknowledgements page, whole body. To be written by the author.
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

Run: python writing/v9/scripts/build_frontmatter.py
"""
import hashlib
import importlib.util
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent          # writing/v9
REPO = ROOT.parent.parent
OUT = ROOT / "FrontMatter_V9.docx"

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

# Examining committee (user, 2026-09-07; chair and supervisor merged into one
# row by the user's own edit of the built document, commit ab41da9).
COMMITTEE = [
    ("Dr. Shahram Payandeh", "Chair and Supervisor", "Professor, School of Engineering Science"),
    ("Dr. Jie Liang", "Committee Member", "Professor, School of Engineering Science"),
    ("Dr. Craig Scratchley", "Committee Member", "Senior Lecturer, School of Engineering Science"),
]
# Approval date (author, 2026-10-06, after the defence of the same day);
# replaces the former bold placeholder "[DATE APPROVED]".
DATE_APPROVED = "October 6, 2026"
# Signed Approval page: the author's scan writing/v9/figures/src/IMG_2688.jpeg
# cropped to the block between the heading and the date line by
# crop_approval_scan.py. Printed at the text width, 6.0 in = the 8.5 in page
# width less the two 1.25 in margins set in apply_house_style.
APPROVAL_SCAN = ROOT / "figures" / "approval_signed_block.png"
APPROVAL_SCAN_WIDTH_IN = 6.0
PH_ACK = "[ACKNOWLEDGEMENTS]"
PH_UPDATE = "[UPDATE FIELDS IN WORD: F9]"

# Placeholder registry: (token, where it appears). Written out by
# build_thesis.py as Thesis_V7_Placeholders.md.
PLACEHOLDERS = [
    (PH_UPDATE, "Top of the contents page"),
]

ABSTRACT = [
    # Supervisor round 7 (2026-09-10, C51): four paragraphs in his order,
    # the problem and why, the challenges, how they were addressed, what
    # was accomplished. Every number is printed in Chapters 7 and 8.
    #
    # Revision of 2026-09-11 (review items 22 to 24). Paragraph 1 names
    # what camera arrays cost; paragraph 3 uses the recovery vocabulary of
    # the brief (object information supplies an additional geometric
    # constraint); paragraph 4 states the causal result as a replay at the
    # recorded pace with no live-camera validation (brief section 3, fact
    # 9; Sections 8.4 and 8.5). No claim was dropped except the clause "of
    # reaching and handovers" in paragraph 1 and the sentence "The system
    # runs two branches" in paragraph 3.
    #
    # Chapter 7 integration pass of 2026-09-12 (CH7_INTEGRATION_FIXLIST.md
    # item FM-1; D-033, D-035, D-036, D-038). Two claims of paragraph 4
    # were withdrawn because the rebuilt Chapter 7 prints neither:
    #   - the four fitted-line spread values, a median of 1.0 cm and a p95
    #     of 2.4 on the rail slide and 0.3 and 1.6 on the handover slide.
    #     Section 7.2 now reports the scatter of a different sample set,
    #     0.83 / 2.12 / 2.92 cm on the rail recording and 0.39 / 1.44 /
    #     2.82 cm on the handover recording, and states in terms that a
    #     line fitted to the tracked samples is not a physical reference.
    #     An abstract does not carry a within-recording description, so
    #     the physical comparison replaces it rather than the new values.
    #   - "through the rail wrist gap every method stays at about the
    #     uncertainty of the hand-placed wrist labels". That was the rail
    #     cuff-seam label set, which D-033 excludes; Section 7.4.2 is now
    #     the loop recording alone.
    # Paragraph 4 now carries the object result Section 7.2 prints:
    # physical segments of 3.5, 25.5 and 37.5 cm measured by tape between
    # marker-centre positions (locked fact 2, user measurement of
    # 2026-09-11; waypoint roles D-036) against reconstructed lengths
    # differing by 0.53 to 2.83 cm (Tables 7.1 and 7.2, pinned in
    # audit_evidence/ch7_restructured/object.json: rail 1.14, 0.53 and
    # 1.09 cm, handover 2.82, 0.85 and 2.83 cm). The detector-selection
    # band is named beside them because the point estimates alone
    # overstate the precision, and only the sign pattern, which holds
    # across that whole family, is stated as a finding. The relative
    # errors of the 3.5 cm segment are not quoted, their band being about
    # 14 per cent of the reference. The wrist-to-marker sentence carries
    # the D-038 strength and nothing more: Section 7.3.3 reports that both
    # single-hand medians, 15.77 and 14.08 cm, sit within about two
    # centimetres of the author's approximate 16 cm physical reference
    # (locked facts 4 and 5). The transfer medians are not graded against
    # it and do not appear. The closing natural-occlusion clause was
    # re-verified against Table 7.9: on the loop recording's right arm the
    # object-assisted solve is 5.2 cm from the manual proxy against 11.4
    # for the plain solve and 17.6 for hold-last, and on the left arm it
    # is 13.1 against 12.3 and 12.7, so the constraint helped on one
    # window and not on the other.
    # Supervisor-supplied 2026-09-14, verbatim, do not edit. The four
    # paragraphs below are the supervisor's own text, character for
    # character: the compound words carry U+2011 non-breaking hyphens, the
    # possessive carries U+2019, the branch names carry straight quotes.
    # ABSTRACT_SHA256 pins the joined text and build() refuses any change.
    # The paragraphs replace the 2026-09-12 wording described above; the
    # numbers they state (3.5 to 37.5 cm, 0.53 to 2.83 cm, about 2 cm,
    # about 29 fps) are the ones Chapters 7 and 8 print. This text is
    # exempt from check_style.py and from the language review.
    "Bimanual object handling is a fundamental human skill, and replaying such motions supports imitation learning, avatar animation, and clinical assessment. Conventional motion‑capture systems rely on multi‑camera rigs that require careful calibration and expert operation, while wearable systems impose hardware on the subject. This thesis demonstrates that a single consumer‑grade RGB‑D camera, combined with three printed ArUco markers, can track a person’s upper body and a hand‑held object during a desk‑based task and reconstruct both within a metric scene suitable for digital‑twin playback.",

    "The core challenge lies in sensing reliability. The landmark detector may output points even when the corresponding body part is occluded or absent. The object and the opposite hand frequently hide the wrist; the hands themselves obscure the hips, causing the depth map to default to the desk surface. The landmark set does not uniquely determine wrist orientation, and each frame must be solved independently as it arrives.",

    "The proposed pipeline contains two branches. The \"landmark branch\" converts RGB‑D body landmarks into a torso pose and four joint angles per arm. The \"marker branch\" establishes a world coordinate frame on the desk and tracks the object within it. The branches share only the captured frames and the world frame. Object pose information provides an additional geometric constraint when a wrist is lost, and the elbow pose follows from two‑link inverse kinematics. Outlier landmarks are rejected, remembered depth substitutes for occluded hips, and all reconstructed quantities are labelled as measured, held, or constrained before entering the rendered scene.",

    "The evaluation tracks a cube moving across a desk and along a rail, both single‑handed and during a handover. Tape‑measured distances between marker‑defined waypoints range from 3.5 to 37.5 cm, while reconstructed lengths differ by 0.53 to 2.83 cm depending on detection settings. Desk‑level segments reconstruct slightly short, whereas later segments reconstruct long. Because the route is not registered into the world frame, point‑to‑path distances are unavailable. Under single‑hand grip, the reconstructed wrist‑to‑marker separation remains within roughly 2 cm of its tape measurement. Object constraints assist recovery during one natural occlusion interval but not another. The causal pipeline replays the motion at the recorded rate of approximately 29 fps, producing smooth output playback; however, a full live‑camera session was not validated.",
]
# sha256 of "\n".join(ABSTRACT); build() asserts it so the supervisor's text
# cannot drift (2026-09-14).
ABSTRACT_SHA256 = "dbab949ea26cfe7c692deab1f97295efd040708bedcb9debc523f88c61fcd21b"

CHAPTER_FILES = [
    "Chapter_1_Introduction.docx",
    "Chapter_2_Experimental_Setup.docx",
    "Chapter_3_Kinematic_Modeling.docx",
    "Chapter_4_Object_Tracking.docx",
    "Chapter_5_Pose_Recovery.docx",
    "Chapter_6_System_Integration.docx",
    "Chapter_7_Evaluation.docx",
    "Chapter_8_Real_Time_Feasibility.docx",
    "Chapter_9_Discussion.docx",
    "Chapter_10_Conclusions_Future_Work.docx",
    "Appendices.docx",
]

def xml_text(el):
    """Plain text of an element.

    lxml's itertext cannot be used here: python-docx gives w:p, w:r and w:t
    their own text properties, so itertext returns the same string once per
    level. Reading the w:t nodes directly gives each character once.
    """
    return "".join(t.text or "" for t in el.findall(".//" + qn("w:t")))


CAPTION_RE = re.compile(r"^(Figure|Table)\s+([A-H]|\d+)\.(\d+)\.\s*(.*)$")
EQTAG_RE = re.compile(r"^\((\d+|[A-H])\.(\d+)\)$")


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
        st.paragraph_format.tab_stops.add_tab_stop(
            Inches(6), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    for style_id, word_name in CAPTION_STYLES:
        if style_id in existing:
            continue
        st = doc.styles.add_style(style_id, WD_STYLE_TYPE.PARAGRAPH)
        st.element.set(qn("w:styleId"), style_id)
        st.element.find(qn("w:name")).set(qn("w:val"), word_name)
        st.base_style = doc.styles["Normal"]
        define_style_element(st.element, size=12, line=1.0, before=4,
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
    for section in doc.sections:
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)
        section.top_margin = section.bottom_margin = Inches(1)
        section.left_margin = section.right_margin = Inches(1.25)
    define_style(doc, "Normal", size=12, line=1.5, after=6)
    define_style(doc, "Heading 1", size=16, bold=True, line=1.0,
                 before=0, after=14, keep_next=True, page_break=True)
    define_style(doc, "Heading 2", size=14, bold=True, line=1.0,
                 before=14, after=8, keep_next=True)
    define_style(doc, "Heading 3", size=12, bold=True, line=1.0,
                 before=12, after=6, keep_next=True)
    define_style(doc, "Caption", size=12, line=1.0, before=4, after=14)
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


def _footer_page_number(section, prefix=""):
    """Centred page number in the section's own footer.

    A prefix is printed as literal text ahead of the PAGE field, which is
    how the appendices and the references carry the labels A1, B1, R1
    (supervisor, 2026-09-14): each of those parts is its own section that
    restarts at 1 (build_thesis.insert_part_sections).
    """
    section.footer.is_linked_to_previous = False
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if prefix:
        p.add_run(prefix)
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
        path = ROOT / name
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
        path = ROOT / name
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
    path = ROOT / "references.md"
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
    heading = doc.add_heading("Approval", level=1)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if APPROVAL_SCAN.exists():
        # Post-defence revision (2026-10-06): the signed page replaces the
        # typed block. The heading stays text so the contents entry keeps
        # it; the scan supplies everything from "Name:" to the last
        # committee row; the date line below stays text.
        p = doc.add_paragraph()
        style_paragraph(p._p.get_or_add_pPr(), line=1.0, after=0)
        p.add_run().add_picture(str(APPROVAL_SCAN),
                                width=Inches(APPROVAL_SCAN_WIDTH_IN))
        _blank(doc, 2)   # same gap before the date as the text layout
        _mixed(doc, [("Date Approved: ", False), (DATE_APPROVED, False)],
               indent=0.3, after=6)
        return
    print(f"WARNING: {APPROVAL_SCAN} is missing; the Approval page is "
          f"printed as the unsigned text block")
    for label, value in [("Name:", AUTHOR),
                         ("Degree:", DEGREE),
                         ("Title of Thesis:", TITLE_MIXED)]:
        p = doc.add_paragraph()
        style_paragraph(p._p.get_or_add_pPr(), line=1.0, after=10)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(1.6),
                                                  WD_TAB_ALIGNMENT.LEFT)
        p.add_run(label + "\t").font.bold = True
        p.add_run(value)
    _blank(doc)
    _signature_line(doc)
    _plain(doc, "Director, School of Engineering Science", indent=1.6, after=18)
    _plain(doc, "Examining Committee:", bold=True, after=10)

    for name, role, position in COMMITTEE:
        _signature_line(doc)
        _plain(doc, f"{name}, {role}", indent=1.6, after=0)
        _plain(doc, position, indent=1.6, after=0)
        _plain(doc, UNIVERSITY, indent=1.6, after=12)

    _blank(doc, 2)
    _mixed(doc, [("Date Approved: ", False), (DATE_APPROVED, False)],
           indent=0.3, after=6)


def _signature_line(doc):
    """Unsigned line in the official ENSC 499 approval-form arrangement."""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(1.6)
    style_paragraph(p._p.get_or_add_pPr(), line=1.0, before=12, after=4,
                    keep_next=True)
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    for name, value in (("val", "single"), ("sz", "4"), ("color", "000000")):
        bottom.set(qn("w:" + name), value)
    borders.append(bottom)
    p._p.get_or_add_pPr().append(borders)


def add_abstract(doc):
    doc.add_heading("Abstract", level=1)
    for para in ABSTRACT:
        _plain(doc, para, line=1.5, after=8)


ACKNOWLEDGMENTS = [
    # The user's own wording (2026-09-07), kept verbatim at the user's request;
    # only the doubled full stop at the end was removed.
    "Writing the acknowledgements has, unexpectedly, been one of the hardest "
    "parts of finishing this thesis.",

    "The results of an experiment may be reproduced, but the uncertainty and "
    "frustration behind them cannot. Looking back, I still remember the nights "
    "I spent alone working through derivations by hand, again and again. "
    "Those difficult moments eventually became part of the work presented "
    "here.",

    "I used to think that growing meant becoming better at solving problems "
    "on my own. Only now do I realize how many people supported me along the "
    "way.",

    "I would like to thank my supervisor for his patience and guidance. "
    "He often reminded me not to rush and to take things one step at a time. "
    "When I was under too much pressure, he would tell me that it was okay to "
    "slow down and that my well-being mattered more. I am very grateful for "
    "that. I would also like to thank my committee for their patience and for "
    "giving me the time to complete this thesis.",

    "I am especially grateful to my friends. When I was struggling "
    "financially, one of you lent me an entire month's salary without "
    "hesitation. During the most difficult period of the pandemic in China, "
    "while I was far from home, another helped my family and told me not to "
    "worry too much and to focus on my studies. I will always remember your "
    "kindness and support.",

    "Finally, I want to thank my mother and my sister. When others questioned "
    "my choices, you continued to support me and simply told me, "
    "\u201cKeep going. Don\u2019t be afraid.\u201d",

    "I feel very fortunate to have had so much support throughout this "
    "journey. As my undergraduate years come to an end, I am glad to leave "
    "with a piece of work that I am genuinely proud of.",
]


# Closing quotation of the acknowledgements page (user, 2026-09-07, verbatim):
# centred, italic, set half-way between the end of the last paragraph and
# the foot of the page. QUOTE_SPACE_BEFORE_PT was measured on the rendered
# page (LibreOffice, pdftotext -bbox-layout) and is re-measured by
# measure_ack_quote.py whenever the acknowledgements change.
ACK_QUOTE = "\u201cSometimes life knows what is best for us better than we ourselves know or think.\u201d"
QUOTE_SPACE_BEFORE_PT = 35


def add_acknowledgments(doc):
    doc.add_heading("Acknowledgements", level=1)
    for para in ACKNOWLEDGMENTS:
        _plain(doc, para, line=1.5, after=8)
    q = doc.add_paragraph()
    style_paragraph(q._p.get_or_add_pPr(), line=1.0, before=QUOTE_SPACE_BEFORE_PT, after=0)
    q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = q.add_run(ACK_QUOTE)
    r.font.italic = True


GLOSSARY = [
    ('RGB-D camera, sensor', 'captures red, green and blue colour (RGB) plus depth (D); the sensor here is the Intel RealSense D435'),
    ('marker, fiducial marker', 'a printed square pattern for measuring pose; ArUco markers are fixed to the wall, desk and object'),
    ('camera frame {Camera}, C', 'the aligned colour optical frame: x right, y down, z forward'),
    ("y-up camera frame {Camera'}, C'", '{Camera} with y flipped upward; the optical origin is unchanged'),
    ('world frame {World}, W', 'fixed to the desk marker during calibration; the reference for object pose'),
    ('object frame {Object}, O', 'centred on the object marker; its third axis is normal to the marker plane'),
    ('display frame {Unity}, U', 'left-handed axes formed by swapping the second and third world axes; the desk-marker origin is retained'),
    ('scene frame {Scene}', 'the final Unity frame after gravity alignment and floor placement; y is vertical, with the origin on the drawn floor'),
    ('T-pose', 'arms extended horizontally to the sides; all arm angles are zero'),
    ('PUMA convention', 'Programmable Universal Machine for Assembly: the robot drawing convention with revolute joints shown as cylinders'),
    ('PSF1, PSR2, PSB2, PSB3, PSI2', 'pose-stream record identifiers: colour/depth frames (PSF1), person (PSR2), object (PSB2), calibration (PSB3), combined pose (PSI2); digits identify layout versions'),
    ('p95', '95th percentile: the value at or below which 95 percent of samples fall'),
]


def add_glossary(doc):
    doc.add_heading("Glossary", level=1)
    _plain(doc, "Selected terms and abbreviations used in this thesis.", after=8)
    t = doc.add_table(rows=len(GLOSSARY) + 1, cols=2)
    t.style = "Table Grid"
    t.cell(0, 0).text = "Term"
    t.cell(0, 1).text = "Meaning"
    for i, (term, meaning) in enumerate(sorted(GLOSSARY, key=lambda row: row[0].casefold()), start=1):
        t.cell(i, 0).text = term
        t.cell(i, 1).text = meaning
    for i, row in enumerate(t.rows):
        for j, cell in enumerate(row.cells):
            for par in cell.paragraphs:
                par.paragraph_format.line_spacing = 1.0
                par.paragraph_format.space_after = Pt(0)
                for run in par.runs:
                    run.font.size = Pt(12)
                    if i == 0:
                        run.font.bold = True
    t.columns[0].width = Inches(1.8)
    t.columns[1].width = Inches(4.2)
    for row in t.rows:
        row.cells[0].width = Inches(1.8)
        row.cells[1].width = Inches(4.2)


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
    # The "[UPDATE FIELDS IN WORD: F9]" note above the contents is gone since
    # 2026-09-07 (user: it must not appear in the printed thesis); the
    # document asks Word to update its fields on opening (build_thesis.py).
    rows = [(f"TOC{min(level + 1, 3)}", text) for level, text in entries]
    add_field_list(doc, r'TOC \o "1-3" \h \z \u', rows, "TOC1")


def add_list_of(doc, heading, rows, style_name):
    # Word's \t switch takes the style's display name ("Figure Caption"),
    # not its id ("FigureCaption"); with the id Word reports "No table of
    # contents entries found" when the field is updated (seen in the user's
    # edited build, commit ab41da9).
    doc.add_heading(heading, level=1)
    lines = [("TableofFigures", f"{label}. {text}.") for label, text in rows]
    add_field_list(doc, f'TOC \\h \\z \\t "{style_name},1"', lines,
                   "TableofFigures")


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
    add_list_of(doc, "List of Figures", figures, "Figure Caption")
    add_list_of(doc, "List of Tables", tables, "Table Caption")
    # The List of Equations was dropped at the supervisor's request
    # (2026-09-14); scan_equations() stays for the checkers.
    add_glossary(doc)

    body = doc.add_section(WD_SECTION.NEW_PAGE)
    body.different_first_page_header_footer = False
    _set_page_number_format(body, "decimal", start=1)
    _footer_page_number(body)

    doc.save(str(OUT))
    words = sum(len(p.split()) for p in ABSTRACT)
    print(f"saved {OUT}")
    print(f"abstract words: {words} | figures listed: {len(figures)} | "
          f"tables listed: {len(tables)} | toc entries: {len(toc.entries)}")
    # The supervisor's abstract of 2026-09-14 is 370 words; the earlier
    # 350-word ceiling was the project's own, not a regulation.
    assert 250 <= words <= 400, f"abstract is {words} words, wanted 250 to 400"
    digest = hashlib.sha256("\n".join(ABSTRACT).encode("utf-8")).hexdigest()
    assert digest == ABSTRACT_SHA256, (
        "ABSTRACT was edited; it is the supervisor's verbatim text (2026-09-14)")
    return doc


if __name__ == "__main__":
    build()

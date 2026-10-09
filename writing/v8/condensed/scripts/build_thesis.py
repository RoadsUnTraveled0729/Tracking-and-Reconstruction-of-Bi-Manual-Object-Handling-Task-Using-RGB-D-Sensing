#!/usr/bin/env python3
"""Build writing/v8/Thesis_V8_Condensed.docx: the assembled condensed thesis
(copy of writing/v7/scripts/build_thesis.py, repointed 2026-09-06; parts are
read from writing/v8/condensed/).

Order: front matter, Chapters 1 to 10, Appendices A to H, References.
Every chapter, the references, and each appendix start on a new page, which
answers supervisor comment C3.

The chapters are merged from the documents already built in writing/v7 by
the per-chapter scripts. Those scripts are not imported: rebuilding them
takes minutes and regenerates figures. Body elements are copied element by
element with python-docx, image relationships are remapped into the merged
package, and native Word mathematics (OMML) and tables are carried across
untouched. The merge is verified by counting paragraphs, tables, images and
OMML elements in every part before the copy and in the assembled document
after it; the sums have to match exactly.

One house style governs the whole document (defined in build_frontmatter.py
and applied to the master here): Times New Roman everywhere, black, no
theme fonts and no theme colours, Heading 1 at 16 pt bold with a page break
before it, Heading 2 at 14 pt bold, Heading 3 at 12 pt bold, captions at
11 pt plain, table text at 11 pt. Run level font, colour and size overrides
carried in from the chapter documents are stripped on headings, captions
and table cells so the style governs the look. Equation number tables keep
their own layout.

All chapter and appendix documents must exist so the global citation plan
can be validated before assembly. Missing inputs fail the build.

Outputs:
  writing/v8/Thesis_V8_Condensed.docx
  writing/v8/condensed/Thesis_V8_Condensed_Placeholders.md

Run: python writing/v8/condensed/scripts/build_thesis.py
"""
import copy
import io
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_frontmatter as fm  # noqa: E402
import assembly_citations as citations  # noqa: E402
import eqn  # noqa: E402  (EQ_SPACE_PT, the displayed-equation spacing)
import submission_layout  # noqa: E402

V7 = HERE.parent          # writing/v8/condensed
OUT = V7.parent / "Thesis_V8_Condensed.docx"
OUT_PLACEHOLDERS = V7 / "Thesis_V8_Condensed_Placeholders.md"
OUT_CITATIONS = V7 / "audit_evidence" / "final_completion" / "citation_mapping.json"

PARTS = [
    ("Chapter 1", "Chapter_1_Introduction.docx"),
    ("Chapter 2", "Chapter_2_Experimental_Setup.docx"),
    ("Chapter 3", "Chapter_3_Kinematic_Modeling.docx"),
    ("Chapter 4", "Chapter_4_Object_Tracking.docx"),
    ("Chapter 5", "Chapter_5_Pose_Recovery.docx"),
    ("Chapter 6", "Chapter_6_System_Integration.docx"),
    ("Chapter 7", "Chapter_7_Evaluation.docx"),
    ("Chapter 8", "Chapter_8_Real_Time_Feasibility.docx"),
    ("Chapter 9", "Chapter_9_Discussion.docx"),
    ("Chapter 10", "Chapter_10_Conclusions_Future_Work.docx"),
]
APPENDIX_PART = ("Appendices", "Appendices.docx")

HEADING_STYLES = {"Heading1", "Heading2", "Heading3", "TOCHeading"}
PLACEHOLDER_RE = re.compile(r"\[[A-Za-z][^\[\]]{2,}\]")
CODE_FONT = "Courier New"
# Bracketed strings that belong to the prose, not to the placeholder set.
NOT_PLACEHOLDERS = {"[Online]"}


def is_code(p):
    """Code listing paragraphs carry bracketed log tags, not placeholders."""
    for rf in p.findall(".//" + qn("w:rFonts")):
        if rf.get(qn("w:ascii")) == CODE_FONT:
            return True
    return False


# ---------------------------------------------------------------------------
# counting
# ---------------------------------------------------------------------------
def _n(el, tag):
    """Count descendants with this tag, plus the element itself."""
    return len(el.findall(".//" + qn(tag))) + (1 if el.tag == qn(tag) else 0)


def count(el):
    return {
        "paragraphs": _n(el, "w:p"),
        "tables": _n(el, "w:tbl"),
        "images": _n(el, "a:blip"),
        "equations": _n(el, "m:oMath"),
    }


def add_counts(a, b):
    return {k: a[k] + b[k] for k in a}


ZERO = {"paragraphs": 0, "tables": 0, "images": 0, "equations": 0}


def fmt_counts(c):
    return (f"paragraphs {c['paragraphs']:4d} | tables {c['tables']:3d} | "
            f"images {c['images']:3d} | equations {c['equations']:4d}")


# ---------------------------------------------------------------------------
# merging
# ---------------------------------------------------------------------------
class Merger:
    def __init__(self, master, citation_mapping=None):
        self.master = master
        self.citation_mapping = citation_mapping
        self.body = master.element.body
        self.sectPr = self.body.find(qn("w:sectPr"))
        assert self.sectPr is not None, "master document has no final sectPr"
        self.shape_id = 0

    def append(self, element):
        """Insert a body element ahead of the document's final sectPr."""
        self.sectPr.addprevious(element)

    def next_shape_id(self):
        self.shape_id += 1
        return self.shape_id

    def copy_part(self, src_path):
        src = Document(str(src_path))
        src_body = src.element.body
        before = count(src_body)
        section = ""
        for el in list(src_body):
            if el.tag == qn("w:sectPr"):
                continue
            new = copy.deepcopy(el)
            if self.citation_mapping is not None:
                citations.rewrite_element(new, self.citation_mapping)
            self._remap_images(new, src.part)
            self._renumber_shapes(new)
            normalize(new, section)
            if new.tag == qn("w:p") and _style_of(new) in HEADING_STYLES:
                text = fm.xml_text(new).strip()
                if text:
                    section = text
            self.append(new)
        return before

    def _remap_images(self, element, src_part):
        """Re-add each referenced image to the merged package.

        The image bytes are handed to the master package rather than the
        source part being related to directly: two chapters both carry a
        part named word/media/image1.png, and relating to the source parts
        would write two entries under one name. Going through the package
        gives every image a fresh name and folds identical images together.
        """
        cache = {}
        for attr in (qn("r:embed"), qn("r:link")):
            for node in element.iter():
                rid = node.get(attr)
                if rid is None:
                    continue
                if rid not in cache:
                    blob = src_part.related_parts[rid].blob
                    new_rid, _ = self.master.part.get_or_add_image(
                        io.BytesIO(blob))
                    cache[rid] = new_rid
                node.set(attr, cache[rid])

    def _renumber_shapes(self, element):
        for node in element.iter(qn("wp:docPr")):
            node.set("id", str(self.next_shape_id()))


def normalize(element, section=""):
    """Force the house look on one copied body element."""
    if element.tag == qn("w:tbl"):
        _normalize_table(element, section)
        return
    if element.tag == qn("w:p"):
        _normalize_paragraph(element, in_table=False)


def _style_of(p):
    pPr = p.find(qn("w:pPr"))
    if pPr is None:
        return None
    st = pPr.find(qn("w:pStyle"))
    return None if st is None else st.get(qn("w:val"))


def _set_style(p, name):
    pPr = p.get_or_add_pPr()
    st = pPr.find(qn("w:pStyle"))
    if st is None:
        st = OxmlElement("w:pStyle")
        pPr.insert(0, st)
    st.set(qn("w:val"), name)


def _normalize_paragraph(p, in_table):
    style = _style_of(p)
    text = fm.xml_text(p).strip()
    has_image = p.find(".//" + qn("a:blip")) is not None

    if style in HEADING_STYLES:
        fm.scrub_runs(p)
        return

    m = fm.CAPTION_RE.match(text)
    if m:
        # The two caption styles are what the list fields key on.
        _set_style(p, "FigureCaption" if m.group(1) == "Figure"
                   else "TableCaption")
        fm.scrub_runs(p)
        return

    if PLACEHOLDER_RE.search(text) and not is_code(p):
        _bold_placeholder_runs(p)

    if in_table:
        fm.style_paragraph(p.get_or_add_pPr(), line=1.0, after=0)
        return

    if not text and p.find(".//" + qn("m:oMath")) is not None:
        # Unnumbered displayed mathematics (eqn.add_display_math). It carries
        # the same space as a numbered equation.
        fm.style_paragraph(p.get_or_add_pPr(), line=1.0,
                           before=eqn.EQ_SPACE_PT, after=eqn.EQ_SPACE_PT)
        return

    if has_image and not text:
        pPr = p.get_or_add_pPr()
        jc = pPr.find(qn("w:jc"))
        if jc is None:
            jc = OxmlElement("w:jc")
            pPr.append(jc)
        jc.set(qn("w:val"), "center")
        fm.style_paragraph(pPr, line=1.0, after=4)


def _tag_equation(tbl, section):
    if tbl.find(".//" + qn("m:oMath")) is None:
        return
    for p in tbl.findall(".//" + qn("w:p")):
        tag = fm.xml_text(p).strip()
        if fm.EQTAG_RE.match(tag):
            fm.add_tc_field(p, fm.equation_entry(tag, section))
            return


def _bold_placeholder_runs(p):
    for r in p.findall(".//" + qn("w:r")):
        run_text = "".join(t.text or "" for t in r.findall(qn("w:t")))
        hits = [m.group(0) for m in PLACEHOLDER_RE.finditer(run_text)]
        if not [h for h in hits if h not in NOT_PLACEHOLDERS]:
            continue
        rPr = r.find(qn("w:rPr"))
        if rPr is None:
            rPr = OxmlElement("w:rPr")
            r.insert(0, rPr)
        for tag in ("w:b", "w:bCs"):
            for el in rPr.findall(qn(tag)):
                rPr.remove(el)
            el = OxmlElement(tag)
            el.set(qn("w:val"), "1")
            rPr.append(el)


def _normalize_table(tbl, section=""):
    tblPr = tbl.find(qn("w:tblPr"))
    style = None
    if tblPr is not None:
        st = tblPr.find(qn("w:tblStyle"))
        if st is not None:
            style = st.get(qn("w:val"))
    is_grid = style == "TableGrid"
    for p in tbl.findall(".//" + qn("w:p")):
        _normalize_paragraph(p, in_table=True)
    if not is_grid:
        # Equation number tables keep their layout; they gain the hidden
        # entry the list of equations is built from, and the space that
        # separates the equation from the prose and from the next equation.
        # The in_table branch above zeroes every table paragraph, so the
        # spacing is written here, after it.
        if tbl.find(".//" + qn("m:oMath")) is not None:
            for p in tbl.findall(".//" + qn("w:p")):
                fm.style_paragraph(p.get_or_add_pPr(), line=1.0,
                                   before=eqn.EQ_SPACE_PT,
                                   after=eqn.EQ_SPACE_PT)
        _tag_equation(tbl, section)
        return
    for r in tbl.findall(".//" + qn("w:r")):
        rPr = r.find(qn("w:rPr"))
        if rPr is None:
            rPr = OxmlElement("w:rPr")
            r.insert(0, rPr)
        for tag in ("w:color", "w:sz", "w:szCs"):
            for el in rPr.findall(qn(tag)):
                rPr.remove(el)
        fm._set_size(rPr, 12)


# ---------------------------------------------------------------------------
# generated sections
# ---------------------------------------------------------------------------
def add_missing_chapter(merger, name):
    p = OxmlElement("w:p")
    merger.append(p)
    fm._child(p.get_or_add_pPr(), "w:pageBreakBefore", fm.PPR_ORDER)
    jc = OxmlElement("w:jc")
    jc.set(qn("w:val"), "center")
    p.get_or_add_pPr().append(jc)
    r = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    b = OxmlElement("w:b")
    rPr.append(b)
    r.append(rPr)
    t = OxmlElement("w:t")
    t.text = f"[{name.upper()} NOT YET BUILT]"
    r.append(t)
    p.append(r)
    return count(p)


def add_references(merger, entries):
    total = dict(ZERO)
    h = OxmlElement("w:p")
    merger.append(h)
    _set_style(h, "Heading1")
    r = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = "References"
    r.append(t)
    h.append(r)
    total = add_counts(total, count(h))
    for number, text in entries:
        p = OxmlElement("w:p")
        merger.append(p)
        pPr = p.get_or_add_pPr()
        fm.style_paragraph(pPr, line=1.0, after=6)
        ind = OxmlElement("w:ind")
        ind.set(qn("w:left"), "720")
        ind.set(qn("w:hanging"), "720")
        pPr.append(ind)
        r = OxmlElement("w:r")
        t = OxmlElement("w:t")
        t.set(qn("xml:space"), "preserve")
        t.text = f"[{number}] {text}"
        r.append(t)
        p.append(r)
        total = add_counts(total, count(p))
    return total


# ---------------------------------------------------------------------------
# verification
# ---------------------------------------------------------------------------
def assembled_headings(doc):
    out = []
    for p in doc.element.body.findall(".//" + qn("w:p")):
        style = _style_of(p)
        if style in HEADING_STYLES:
            text = fm.xml_text(p).strip()
            if text:
                out.append((style, text))
    return out


def check_order(doc, entries):
    """Every build_toc entry that names a body heading appears once, in order."""
    headings = [t for _, t in assembled_headings(doc)]
    front = {"Front Matter", "Title Page", "Approval", "Abstract",
             "Acknowledgements", "Table of Contents", "List of Figures",
             "List of Tables", "List of Equations"}
    wanted = [t for _, t in entries if t not in front]
    problems = []
    cursor = 0
    for text in wanted:
        occurrences = [i for i, h in enumerate(headings) if h == text]
        if len(occurrences) != 1:
            problems.append(f"{text!r} appears {len(occurrences)} times "
                            f"as a heading")
            continue
        idx = occurrences[0]
        if idx < cursor:
            problems.append(f"{text!r} is out of order")
        cursor = idx
    return wanted, headings, problems


def placeholder_report(doc):
    """Every bracketed placeholder in the assembled body, with its section."""
    found = []
    section = "Front matter"
    for p in doc.element.body.findall(".//" + qn("w:p")):
        style = _style_of(p)
        text = fm.xml_text(p).strip()
        if style in HEADING_STYLES and text:
            section = text
            continue
        if is_code(p):
            continue
        for m in PLACEHOLDER_RE.finditer(text):
            token = m.group(0)
            if token in NOT_PLACEHOLDERS:
                continue
            bold = _token_is_bold(p, token)
            found.append((token, section, bold))
    return found


def _token_is_bold(p, token):
    for r in p.findall(".//" + qn("w:r")):
        run_text = "".join(t.text or "" for t in r.findall(qn("w:t")))
        if token not in run_text:
            continue
        rPr = r.find(qn("w:rPr"))
        if rPr is None:
            return False
        b = rPr.find(qn("w:b"))
        return b is not None and b.get(qn("w:val")) not in ("0", "false")
    return False


def image_check(doc):
    """Every image reference in the body resolves to a part in the package."""
    rels = doc.part.rels
    missing, parts = [], set()
    for node in doc.element.body.iter():
        for attr in (qn("r:embed"), qn("r:link")):
            rid = node.get(attr)
            if rid is None:
                continue
            if rid not in rels:
                missing.append(rid)
            else:
                parts.add(str(rels[rid].target_part.partname))
    return missing, parts


def font_report(doc):
    xml = doc.element.body.xml
    fonts = sorted(set(re.findall(r'w:ascii="([^"]+)"', xml)))
    colours = sorted(set(re.findall(r'<w:color w:val="([^"]+)"', xml)))
    themed = len(re.findall(r'w:(?:ascii|hAnsi|eastAsia|cs)Theme=', xml))
    theme_colour = len(re.findall(r"w:themeColor=", xml))
    return fonts, colours, themed, theme_colour


# ---------------------------------------------------------------------------
def main():
    doc = fm.build()
    fm.apply_house_style(doc)
    source_paths = [V7 / filename for _, filename in PARTS + [APPENDIX_PART]]
    # D-048/D-069: never rewrite the frozen-number chapter files. Plan the
    # order across all chapter and appendix inputs before adding References.
    citation_plan = citations.make_plan(source_paths, fm.parse_references())
    # Generated caption-list caches can contain literature credits too.
    citations.rewrite_element(doc.element.body, citation_plan["mapping"])
    merger = Merger(doc, citation_plan["mapping"])

    per_part = []
    front = count(doc.element.body)
    per_part.append(("Front matter", front))
    expected = dict(front)
    warnings = []

    for name, filename in PARTS:
        path = V7 / filename
        if path.exists():
            got = merger.copy_part(path)
        else:
            warnings.append(f"WARNING: {filename} is missing, a placeholder "
                            f"page stands in its place")
            got = add_missing_chapter(merger, name)
        per_part.append((name, got))
        expected = add_counts(expected, got)

    name, filename = APPENDIX_PART
    path = V7 / filename
    if path.exists():
        got = merger.copy_part(path)
    else:
        warnings.append(f"WARNING: {filename} is missing, a placeholder page "
                        f"stands in its place")
        got = add_missing_chapter(merger, "Appendices")
    per_part.append((name, got))
    expected = add_counts(expected, got)

    refs = citations.final_entries(citation_plan)
    got = add_references(merger, refs)
    per_part.append((f"References ({len(refs)} entries)", got))
    expected = add_counts(expected, got)

    settings = doc.settings.element
    if settings.find(qn("w:updateFields")) is None:
        upd = OxmlElement("w:updateFields")
        upd.set(qn("w:val"), "true")
        settings.append(upd)

    submission_layout.apply(doc)
    doc.save(str(OUT))

    # ---------------- verification ----------------
    check = Document(str(OUT))
    after = count(check.element.body)
    citation_result = citations.verify_assembly(check, citation_plan)
    citations.write_audit(OUT_CITATIONS, citation_plan, citation_result, OUT)
    print(f"literature citations: {citation_result}")

    print()
    print("counts per part, before the merge")
    for name, c in per_part:
        print(f"  {name:34s} {fmt_counts(c)}")
    print(f"  {'SUM':34s} {fmt_counts(expected)}")
    print(f"  {'ASSEMBLED DOCUMENT':34s} {fmt_counts(after)}")
    ok = expected == after
    print("  counts: PASS" if ok else "  counts: FAIL")

    toc = fm._load_toc()
    wanted, headings, problems = check_order(check, toc.entries)
    print()
    print(f"headings: {len(wanted)} body entries in the table of contents, "
          f"{len(headings)} headings in the document")
    if problems:
        for p in problems:
            print("  FAIL", p)
    else:
        print("  order and uniqueness: PASS")

    chapters = [h for h in headings if h.startswith(("Chapter ", "Appendix "))
                or h == "References"]
    print("  sequence:", " | ".join(h.split(":")[0] for h in chapters))

    found = placeholder_report(check)
    print()
    print(f"placeholders in the assembled document: {len(found)}")
    not_bold = [f for f in found if not f[2]]
    for token, section, bold in found:
        shown = token if len(token) <= 52 else token[:49] + "..."
        print(f"  {'bold' if bold else 'PLAIN'}  {shown:52s} {section}")
    print("  all bold: PASS" if not not_bold else
          f"  all bold: FAIL ({len(not_bold)} plain)")

    missing_images, image_parts = image_check(check)
    print()
    print(f"image parts in the package: {len(image_parts)} | unresolved "
          f"image references: {len(missing_images)}")
    print("  images: PASS" if not missing_images else "  images: FAIL")

    fonts, colours, themed, theme_colour = font_report(check)
    print()
    print(f"fonts in the body (w:ascii values): {fonts}")
    print(f"colours in the body (w:color values): {colours}")
    print(f"theme font references: {themed} | theme colour references: "
          f"{theme_colour}")

    write_placeholder_file(found, warnings)
    print()
    print(f"saved {OUT}")
    print(f"saved {OUT_PLACEHOLDERS}")
    for w in warnings:
        print(w)
    return 0 if (ok and not problems and not not_bold
                 and not missing_images) else 1


def write_placeholder_file(found, warnings):
    seen = {}
    for token, section, bold in found:
        seen.setdefault(token, []).append(section)
    lines = [
        "# Thesis V7 placeholders",
        "",
        "Every value the assembled thesis does not yet know, printed in "
        "Thesis_V8_Condensed.docx as bold text inside square brackets. Replace the "
        "bracketed text, keep the surrounding wording.",
        "",
        "| Placeholder | Where it appears | Count | What is needed |",
        "| --- | --- | --- | --- |",
    ]
    needs = {
        "[CHAIR NAME]": "Name of the chair of the examining committee.",
        "[CHAIR AFFILIATION]": "Department and university of the chair.",
        "[COMMITTEE MEMBER NAME]": "Names of the other examining committee "
                                   "members (supervisor comment C1).",
        "[ROLE]": "Role of each committee member, for example Internal "
                  "Examiner or External Examiner.",
        "[AFFILIATION]": "Department and university of each committee "
                         "member.",
        "[DATE APPROVED]": "Date of the defence.",
        "[ACKNOWLEDGEMENTS]": "The acknowledgements text, written by the "
                              "author.",
        "[UPDATE FIELDS IN WORD: F9]":
            "Not a value to supply. The contents and the three lists are "
            "Word fields that already carry their entries; select all and "
            "press F9 in Word, or use Tools, Update, Update All in "
            "LibreOffice, to bring in the page numbers, then delete the "
            "note.",
        "[pending manual labels]":
            "Wrist labels on the natural failure windows, Table 7.7. "
            "Waiting on the manual labelling that Section 7.3.3 describes.",
        "[PLACEHOLDER:":
            "The whole-setup photograph the supervisor asked for in comment "
            "C4, with the camera on its mount and the participant in frame. "
            "Owned by the Chapter 2 build.",
    }
    for token in sorted(seen):
        where = sorted(set(seen[token]))
        label = "; ".join(where[:3]) + (" and more" if len(where) > 3 else "")
        need = needs.get(token)
        if need is None:
            for key, value in needs.items():
                if token.startswith(key):
                    need = value
                    break
        need = need or "Supplied by the chapter that prints it."
        shown = token if len(token) <= 90 else token[:87] + "..."
        lines.append(f"| `{shown}` | {label} | {len(seen[token])} | {need} |")
    lines += [
        "",
        "## Values taken from the repository",
        "",
        "These are printed as real values rather than placeholders, from the "
        "V6 front matter builder. Confirm them before the thesis is sent.",
        "",
        f"- Author: {fm.AUTHOR}",
        f"- Supervisor: {fm.SUPERVISOR}",
        f"- Degree: {fm.DEGREE}",
        f"- Department: {fm.DEPARTMENT}",
        f"- University: {fm.UNIVERSITY}, {fm.UNIVERSITY_PLACE}",
        f"- Date on the title page: {fm.DATE}",
        "",
        # D-052: the author confirmed on 2026-09-12 that this is an
        # undergraduate bachelor's honours thesis. The earlier note here
        # inferred a graduate programme from the supervisor's committee
        # comment; that inference was wrong and is removed. Nothing in the
        # thesis may describe the work, committee, examination, submission
        # process or degree level as graduate-level.
        "The degree designation is an undergraduate bachelor's honours "
        "thesis. Confirm the wording of the degree, department and date "
        "lines against the current institutional template before submission.",
    ]
    if warnings:
        lines += ["", "## Build warnings", ""]
        lines += [f"- {w}" for w in warnings]
    lines.append("")
    OUT_PLACEHOLDERS.write_text("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())

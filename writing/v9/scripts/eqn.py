"""OMML (Word native math) builder for the v4 equation round.

No external converters: equations are assembled from a small set of builder
functions that emit OMML XML strings, inserted into python-docx paragraphs.
Displayed equations use a borderless three-column table within the text
width. Equal outer columns centre the native equation over the text area;
the right column places its number on the right margin.

Builder vocabulary (returns XML string fragments inside <m:oMath>):
  r(text)          math run (Word renders letters italic automatically)
  nor(text)        upright ("normal") run, for function names: asin, atan2, diag
  sub(base, s)     subscript      sup(base, s)  superscript
  hat(e)           circumflex accent (unit vectors)
  frac(num, den)   fraction
  mat(rows)        bracketed matrix; rows = list of lists of fragments
  d(e, l="(",r=")") delimiter (parenthesised expression)
  eqArr(*lines)    stacked multi-line display (worked-example step lists)

All fragments concatenate with +.

Displayed equations carry EQ_SPACE_PT of vertical space above and below, set
on the paragraphs inside the equation table cells. A table has no space of
its own in Word, so the cell paragraphs are what separates an equation from
the prose around it and from the next equation.
"""
from docx.oxml import parse_xml
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH

M = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" ' \
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'

# Vertical space above and below a displayed equation, in points. Body text
# runs at 1.5 lines with 6 pt after a paragraph, so an equation needs its own
# space to separate from the prose and from a following equation.
EQ_SPACE_PT = 12
EQ_SIDE_INCHES = 0.45  # D-105: room for the existing 12-point number labels.
# D-106: these displays continue into a lower-case explanatory clause.
CONTINUED_EQUATIONS = {"2.1", "3.14", "3.15", "3.18", "3.19", "3.20",
                       "3.21", "3.22", "5.1", "5.2", "5.5", "6.2"}


def _space(paragraph):
    """Put the displayed-equation space above and below one paragraph."""
    paragraph.paragraph_format.space_before = Pt(EQ_SPACE_PT)
    paragraph.paragraph_format.space_after = Pt(EQ_SPACE_PT)


def _esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def r(text):
    return f'<m:r><m:t xml:space="preserve">{_esc(text)}</m:t></m:r>'


def nor(text):
    return (f'<m:r><m:rPr><m:sty m:val="p"/></m:rPr>'
            f'<m:t xml:space="preserve">{_esc(text)}</m:t></m:r>')


def sub(base, s):
    return (f'<m:sSub><m:e>{base}</m:e><m:sub>{s}</m:sub></m:sSub>')


def sup(base, s):
    return (f'<m:sSup><m:e>{base}</m:e><m:sup>{s}</m:sup></m:sSup>')


def hat(e):
    return (f'<m:acc><m:accPr><m:chr m:val="̂"/></m:accPr>'
            f'<m:e>{e}</m:e></m:acc>')


def frac(num, den):
    return f'<m:f><m:num>{num}</m:num><m:den>{den}</m:den></m:f>'


def d(e, l="(", rr=")"):
    return (f'<m:d><m:dPr><m:begChr m:val="{l}"/><m:endChr m:val="{rr}"/></m:dPr>'
            f'<m:e>{e}</m:e></m:d>')


def eqArr(*lines):
    """Multi-line equation array: each argument is one stacked line."""
    body = "".join(f"<m:e>{ln}</m:e>" for ln in lines)
    return f"<m:eqArr>{body}</m:eqArr>"


def mat(rows, l="[", rr="]"):
    ncols = len(rows[0])
    body = "".join(
        "<m:mr>" + "".join(f"<m:e>{c}</m:e>" for c in row) + "</m:mr>"
        for row in rows)
    mpr = (f'<m:mPr><m:mcs><m:mc><m:mcPr><m:count m:val="{ncols}"/>'
           f'<m:mcJc m:val="center"/></m:mcPr></m:mc></m:mcs></m:mPr>')
    return d(f'<m:m>{mpr}{body}</m:m>', l, rr)


def _omath(fragments):
    return parse_xml(f'<m:oMath {M}>{fragments}</m:oMath>')


def _punctuate(math, punctuation):
    # A multiline expression is punctuated on its final baseline.
    target = math
    if len(math) and math[-1].tag == qn("m:eqArr"):
        target = math[-1].findall(qn("m:e"))[-1]
    target.append(parse_xml(f'<m:r {M}><m:t>{punctuation}</m:t></m:r>'))


def add_display_eq(doc, fragments, number, punctuation=None):
    """Add a displayed numbered equation: centred math, right-aligned (number)."""
    t = doc.add_table(rows=1, cols=3)
    t.autofit = False
    c_blank, c_eq, c_no = t.rows[0].cells
    widths = (EQ_SIDE_INCHES, 6 - 2 * EQ_SIDE_INCHES, EQ_SIDE_INCHES)
    for c, width in zip((c_blank, c_eq, c_no), widths):
        c.width = Inches(width)
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = c_eq.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _space(p)
    math = _omath(fragments)
    if punctuation is None:
        punctuation = "," if number in CONTINUED_EQUATIONS else "."
    if punctuation:
        _punctuate(math, punctuation)
    p._p.append(math)
    pn = c_no.paragraphs[0]
    pn.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    _space(pn)
    run = pn.add_run(f"({number})")
    run.font.size = Pt(12)
    # Both Word's cell widths and LibreOffice's grid must agree.
    tblPr = t._tbl.tblPr
    for tag in ("w:tblW", "w:tblLayout"):
        for el in tblPr.findall(qn(tag)):
            tblPr.remove(el)
    tblPr.append(t._tbl.makeelement(
        qn("w:tblW"), {qn("w:w"): str(6 * 1440), qn("w:type"): "dxa"}))
    tblPr.append(t._tbl.makeelement(
        qn("w:tblLayout"), {qn("w:type"): "fixed"}))
    for col, width in zip(t._tbl.find(qn("w:tblGrid")).findall(qn("w:gridCol")),
                          widths):
        col.set(qn("w:w"), str(round(width * 1440)))
    margins = t._tbl.makeelement(qn("w:tblCellMar"))
    for side in ("top", "left", "bottom", "right"):
        margins.append(t._tbl.makeelement(qn("w:" + side),
            {qn("w:w"): "0", qn("w:type"): "dxa"}))
    tblPr.append(margins)
    t.rows[0]._tr.get_or_add_trPr().append(t._tbl.makeelement(qn("w:cantSplit")))
    from submission_layout import order_properties
    order_properties(t._tbl)
    return t


def add_display_math(doc, fragments, punctuation="."):
    """Displayed but unnumbered mathematics: a centred paragraph of native math.

    Used for the numeric lines of worked examples; numbered equations are
    reserved for the symbolic formulas (add_display_eq)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _space(p)
    math = _omath(fragments)
    if punctuation:
        _punctuate(math, punctuation)
    p._p.append(math)
    return p


def add_inline_math(paragraph, fragments):
    """Append an inline OMML expression to an existing paragraph."""
    paragraph._p.append(_omath(fragments))

"""OMML (Word native math) builder for the v4 equation round.

No external converters: equations are assembled from a small set of builder
functions that emit OMML XML strings, inserted into python-docx paragraphs.
Displayed equations use the standard layout: a borderless two-column table,
equation centred in the wide cell, "(3.n)" right-aligned in the narrow cell.

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
"""
from docx.oxml import parse_xml
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH

M = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" ' \
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


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


def add_display_eq(doc, fragments, number):
    """Add a displayed numbered equation: centred math, right-aligned (number)."""
    t = doc.add_table(rows=1, cols=2)
    t.autofit = False
    c_eq, c_no = t.rows[0].cells
    c_eq.width = Inches(5.6)
    c_no.width = Inches(0.9)
    for c in (c_eq, c_no):
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = c_eq.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p._p.append(_omath(fragments))
    pn = c_no.paragraphs[0]
    pn.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = pn.add_run(f"({number})")
    run.font.size = Pt(12)
    return t


def add_display_math(doc, fragments):
    """Displayed but unnumbered mathematics: a centred paragraph of native math.

    Used for the numeric lines of worked examples; numbered equations are
    reserved for the symbolic formulas (add_display_eq)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p._p.append(_omath(fragments))
    return p


def add_inline_math(paragraph, fragments):
    """Append an inline OMML expression to an existing paragraph."""
    paragraph._p.append(_omath(fragments))

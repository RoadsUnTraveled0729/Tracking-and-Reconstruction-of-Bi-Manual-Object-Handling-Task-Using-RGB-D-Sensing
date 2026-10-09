"""Apply the submission checklist's typography, margins and keep rules.

Formatting only: native mathematical expressions, image bytes and data-cell
text are retained. D-105 records the dimensional choices.
"""
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches

from list_numbering import restart_numbered_lists

TEXT_TWIPS = 8640  # Letter width less two 1.25-inch margins.
TEXT_EMU = Inches(6)
KEEP_ROWS = 12  # tables up to this many rows are kept on one page
PROPERTY_ORDER = {
    'pPr': 'pStyle keepNext keepLines pageBreakBefore framePr widowControl numPr suppressLineNumbers pBdr shd tabs suppressAutoHyphens kinsoku wordWrap overflowPunct topLinePunct autoSpaceDE autoSpaceDN bidi adjustRightInd snapToGrid spacing ind contextualSpacing mirrorIndents suppressOverlap jc textDirection textAlignment textboxTightWrap outlineLvl divId cnfStyle rPr sectPr pPrChange',
    'tblPr': 'tblStyle tblpPr tblOverlap bidiVisual tblStyleRowBandSize tblStyleColBandSize tblW jc tblCellSpacing tblInd tblBorders shd tblLayout tblCellMar tblLook tblCaption tblDescription tblPrChange',
    'tcPr': 'cnfStyle tcW gridSpan hMerge vMerge tcBorders shd noWrap tcMar textDirection tcFitText vAlign hideMark headers cellIns cellDel cellMerge tcPrChange',
    'trPr': 'cnfStyle divId gridBefore gridAfter wBefore wAfter cantSplit trHeight tblHeader tblCellSpacing jc hidden ins del trPrChange',
    'numPr': 'ilvl numId numberingChange ins',
}


def order_properties(root):
    """Keep WordprocessingML properties in schema sequence for native Word."""
    for local, names in PROPERTY_ORDER.items():
        order = names.split()
        ranks = {qn('w:' + name): i for i, name in enumerate(order)}
        for properties in root.iter(qn('w:' + local)):
            properties[:] = sorted(properties, key=lambda child: ranks.get(child.tag, len(ranks)))


def element(parent, name, **attrs):
    child = parent.find(qn(name))
    if child is None:
        child = OxmlElement(name)
        parent.append(child)
    for key, value in attrs.items():
        child.set(qn("w:" + key), str(value))
    return child


def keep(paragraph, following=False):
    props = paragraph.get_or_add_pPr()
    element(props, "w:keepLines", val="1")
    if following:
        element(props, "w:keepNext", val="1")


def apply(doc):
    # Raise direct overrides as well as inherited sizes. Mathematical
    # subscripts still use the equation editor's natural script scaling.
    for root in (doc.element, doc.styles.element):
        for name in ("w:sz", "w:szCs"):
            for size in root.iter(qn(name)):
                if int(size.get(qn("w:val"))) < 24:
                    size.set(qn("w:val"), "24")
    for part in doc.part.package.iter_parts():
        if str(part.partname).startswith("/word/footer"):
            for name in ("w:sz", "w:szCs"):
                for size in part.element.iter(qn(name)):
                    if int(size.get(qn("w:val"))) < 24:
                        size.set(qn("w:val"), "24")

    for extent in doc.element.iter(qn("wp:extent")):
        width = int(extent.get("cx"))
        if width > TEXT_EMU:
            ratio = TEXT_EMU / width
            extent.set("cx", str(TEXT_EMU))
            extent.set("cy", str(round(int(extent.get("cy")) * ratio)))
            drawing = extent.getparent()
            for inner in drawing.findall(".//" + qn("a:ext")):
                if inner.get("cx") and inner.get("cy"):
                    inner.set("cx", str(round(int(inner.get("cx")) * ratio)))
                    inner.set("cy", str(round(int(inner.get("cy")) * ratio)))

    for table in doc.element.body.iter(qn("w:tbl")):
        props = table.find(qn("w:tblPr"))
        grid = table.find(qn("w:tblGrid"))
        columns = list(grid)
        widths = [int(c.get(qn("w:w"))) for c in columns]
        if sum(widths) > TEXT_TWIPS:
            scaled = [round(w * TEXT_TWIPS / sum(widths)) for w in widths]
            scaled[-1] += TEXT_TWIPS - sum(scaled)
            for col, width in zip(columns, scaled):
                col.set(qn("w:w"), str(width))
            for row in table.findall(qn("w:tr")):
                cursor = 0
                for cell in row.findall(qn("w:tc")):
                    cp = cell.get_or_add_tcPr()
                    span = cp.find(qn("w:gridSpan"))
                    n = int(span.get(qn("w:val"))) if span is not None else 1
                    element(cp, "w:tcW", w=sum(scaled[cursor:cursor+n]), type="dxa")
                    cursor += n
        element(props, "w:tblW", w=min(sum(widths), TEXT_TWIPS), type="dxa")
        element(props, "w:tblLayout", type="fixed")
        element(props, "w:tblInd", w=0, type="dxa")
        element(props, "w:jc", val="center")
        rows = table.findall(qn("w:tr"))
        for row in rows:
            element(row.get_or_add_trPr(), "w:cantSplit")
        # A short table stays on one page: every paragraph of every row but
        # the last keeps with the next, so the block moves to the next page
        # whole instead of breaking after a few rows (author, 2026-09-15,
        # for Tables 6.1, 8.1 and 9.1; the rule covers every table of at
        # most KEEP_ROWS rows).
        if len(rows) <= KEEP_ROWS:
            for row in rows[:-1]:
                for p in row.iter(qn("w:p")):
                    keep(p, following=True)
        is_grid = props.find(qn("w:tblStyle"))
        if is_grid is not None and is_grid.get(qn("w:val")) == "TableGrid":
            element(rows[0].get_or_add_trPr(), "w:tblHeader")
            for p in rows[0].iter(qn("w:p")):
                keep(p, following=True)
        after = table.getnext()
        if after is not None and after.tag == qn("w:p"):
            text = "".join(t.text or '' for t in after.iter(qn('w:t')))
            if text.startswith("Table "):
                for p in rows[-1].iter(qn("w:p")):
                    keep(p, following=True)
                keep(after)

    for paragraph in doc.element.body.iter(qn("w:p")):
        if paragraph.find(".//" + qn("a:blip")) is not None:
            keep(paragraph, following=True)
        style = paragraph.find("./" + qn("w:pPr") + "/" + qn("w:pStyle"))
        name = style.get(qn("w:val")) if style is not None else ""
        if name in ("FigureCaption", "TableCaption"):
            keep(paragraph)
        if name == "ListNumber":
            props = paragraph.get_or_add_pPr()
            element(props, "w:ind", left=360, hanging=360)
            # python-docx's built-in List Number style uses decimal numId 7.
            num = element(props, "w:numPr")
            element(num, "w:ilvl", val=0)
            element(num, "w:numId", val=7)
        if name == "ListBullet":
            # Bullet items (supervisor comment C54, 2026-09-16): enforce the
            # same indent hygiene as ListNumber above, scaled to the 0.25 in
            # / 0.25 in hanging indent the chapter builders set (504/360
            # twips). The paragraph itself carries no explicit w:numPr; the
            # built-in List Bullet style supplies numId 1 through styles.xml,
            # so it is left alone rather than re-pinned to the ListNumber
            # numId 7 verify_submission.py counts for the appendix.
            props = paragraph.get_or_add_pPr()
            element(props, "w:ind", left=360, hanging=360)
        if name == "ListNumber2":
            # Numbered items (NUM item kind, C54 mechanics follow-up,
            # 2026-09-16): same indent hygiene as ListBullet above, since
            # the chapter builders set the same 0.25 in / 0.25 in hanging
            # indent for NUM as for BUL. Unlike ListBullet, ListNumber2
            # paragraphs do carry an explicit numId (from
            # list_numbering.restart_numbered_lists), but that numId was
            # assigned against the per-chapter document's own numbering
            # part and does not resolve in the assembled master (see
            # list_numbering.py); restart_numbered_lists(doc) below
            # re-assigns every one against the master's own numbering part.
            props = paragraph.get_or_add_pPr()
            element(props, "w:ind", left=360, hanging=360)
    # A sentence that introduces a list stays on the page with the list's
    # first item (author, 2026-09-16: no introducing sentence stranded at a
    # page foot). Any non-list paragraph directly followed by a List Bullet
    # or List Number 2 paragraph keeps with next.
    paragraphs = doc.paragraphs
    list_styles = {"ListBullet", "ListNumber2", "ListNumber"}
    for current, following in zip(paragraphs, paragraphs[1:]):
        cur_style = (current.style.style_id if current.style is not None else "")
        nxt_style = (following.style.style_id if following.style is not None else "")
        if nxt_style in list_styles and cur_style not in list_styles and current.text.strip():
            keep(current._p, following=True)
    order_properties(doc.element)
    restart_numbered_lists(doc)

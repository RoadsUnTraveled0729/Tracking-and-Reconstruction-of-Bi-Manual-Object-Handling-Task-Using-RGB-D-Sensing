"""Apply the submission checklist's typography, margins and keep rules.

Formatting only: native mathematical expressions, image bytes and data-cell
text are retained. D-105 records the dimensional choices.
"""
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches

TEXT_TWIPS = 8640  # Letter width less two 1.25-inch margins.
TEXT_EMU = Inches(6)
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
    order_properties(doc.element)

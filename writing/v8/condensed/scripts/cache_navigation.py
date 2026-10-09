"""Save paginated index results without round-tripping native Word content.

The LibreOffice renderer supplies the displayed rows and their levels. Only
the four TOC field result ranges in document.xml are replaced. Other ZIP
members and body XML remain unchanged, preserving native Word mathematics.
"""
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

from lxml import etree as E

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
NS = {"w": W[1:-1]}


def node(name, **attrs):
    return E.Element(W + name, {W + k: str(v) for k, v in attrs.items()})


def run_text(text):
    run = node("r")
    t = E.SubElement(run, W + "t")
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return run


def cache(docx, manifest):
    results = json.loads(manifest.read_text())
    with ZipFile(docx) as source:
        entries = [(info, source.read(info.filename)) for info in source.infolist()]
    xml = E.fromstring(dict((i.filename, b) for i, b in entries)["word/document.xml"])
    body = xml.find(W + "body")
    fields = []
    for first in list(body):
        instructions = first.xpath(".//w:instrText/text()", namespaces=NS)
        toc = next((s for s in instructions if s.strip().startswith("TOC ")), None)
        if toc is None:
            continue
        last = first
        while not last.xpath('.//w:fldChar[@w:fldCharType="end"]', namespaces=NS):
            last = last.getnext()
            if last is None:
                raise ValueError("Unterminated contents field")
        fields.append((first, last, toc))
    assert len(fields) == len(results["indexes"]) == 4
    for index, (first, last, instruction) in zip(results["indexes"], fields):
        rows = index["rows"]
        assert rows, "Empty navigation index"
        paragraphs = []
        for row in rows:
            text = row["text"]
            assert re.search(r"\t(?:[ivxlcdm]+|\d+)$", text), text
            p = node("p")
            pp = E.SubElement(p, W + "pPr")
            # Match the actual rendered index style. LibreOffice also uses
            # Contents 1 for the three lists; TableofFigures would add an
            # indent and change wrapping when Word opens the cached file.
            level = re.search(r"([123])$", row["style"])
            style = "TOC" + (level.group(1) if level else "1")
            pp.append(node("pStyle", val=style))
            tabs = E.SubElement(pp, W + "tabs")
            tabs.append(node("tab", val="right", leader="dot", pos="8640"))
            label, page = text.rsplit("\t", 1)
            p.append(run_text(label))
            tabrun = E.SubElement(p, W + "r")
            E.SubElement(tabrun, W + "tab")
            p.append(run_text(page))
            paragraphs.append(p)
        begin = node("r")
        begin.append(node("fldChar", fldCharType="begin", dirty="false"))
        instr = node("r")
        ins = E.SubElement(instr, W + "instrText")
        ins.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        ins.text = instruction
        separate = node("r")
        separate.append(node("fldChar", fldCharType="separate"))
        for offset, run in enumerate((begin, instr, separate), 1):
            paragraphs[0].insert(offset, run)
        end = node("r")
        end.append(node("fldChar", fldCharType="end"))
        paragraphs[-1].append(end)
        old = first
        for p in paragraphs:
            first.addprevious(p)
        while True:
            following = old.getnext()
            body.remove(old)
            if old is last:
                break
            old = following
    data = E.tostring(xml, xml_declaration=True, encoding="UTF-8", standalone=True)
    temporary = docx.with_suffix(".navigation.tmp")
    with ZipFile(temporary, "w") as target:
        for info, blob in entries:
            target.writestr(info, data if info.filename == "word/document.xml" else blob)
    temporary.replace(docx)
    print("cached four paginated navigation fields in", docx)


if __name__ == "__main__":
    cache(Path(sys.argv[1]), Path(sys.argv[2]))

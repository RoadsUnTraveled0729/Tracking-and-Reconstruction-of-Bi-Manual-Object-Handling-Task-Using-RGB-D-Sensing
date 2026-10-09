#!/usr/bin/env python3
"""Compare Chapter 5/6 part mathematics with the final assembled DOCX.

All mathematical nodes, dimensions, arguments, script positions and
operator properties are compared. Run-font properties are excluded because
the assembler can apply the thesis typography without changing mathematics.
This does not substitute for visual PDF or native Word inspection.
"""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

from lxml import etree

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
CONDENSED = REPO / "writing/v8/condensed"
ASSEMBLED = REPO / "writing/v8/Thesis_V8_Condensed.docx"
NS = {"m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
      "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def xml(path):
    with ZipFile(path) as archive:
        return etree.fromstring(archive.read("word/document.xml"))


def words(node):
    return "".join(node.xpath(".//w:t/text()", namespaces=NS))


def mathematical_structure(node):
    tag = etree.QName(node)
    if tag.localname in ("rPr", "ctrlPr"):
        return None
    children = [mathematical_structure(child) for child in node]
    return {
        "tag": tag.namespace + ":" + tag.localname,
        "attributes": sorted(node.attrib.items()),
        "text": node.text if tag.localname == "t" else None,
        "children": [child for child in children if child is not None],
    }


def math_objects(nodes):
    objects = []
    for node in nodes:
        for math in node.xpath(".//m:oMath", namespaces=NS):
            structure = mathematical_structure(math)
            objects.append({
                "tokens": " ".join(math.xpath(".//m:t/text()", namespaces=NS)),
                "structure_sha256": hashlib.sha256(
                    json.dumps(structure, sort_keys=True).encode()).hexdigest(),
            })
    return objects


assembled_xml = xml(ASSEMBLED)
assembled_body = list(assembled_xml.find("w:body", namespaces=NS))
result = {"assembled_sha256": hashlib.sha256(ASSEMBLED.read_bytes()).hexdigest(),
          "chapters": {},
          "scope": "Ordered mathematical text and structure; run-font properties excluded."}
for number, part in ((5, "Chapter_5_Pose_Recovery.docx"),
                     (6, "Chapter_6_System_Integration.docx")):
    part_path = CONDENSED / part
    part_xml = xml(part_path)
    part_body = list(part_xml.find("w:body", namespaces=NS))
    title = next(words(node) for node in part_body
                 if words(node).startswith(f"Chapter {number}:"))
    candidates = [i for i, node in enumerate(assembled_body) if words(node) == title]
    heading_candidates = [i for i in candidates if assembled_body[i].xpath(
        "./w:pPr/w:pStyle[starts-with(@w:val, 'Heading')]", namespaces=NS)]
    if len(heading_candidates) != 1:
        raise RuntimeError(f"Expected one body heading for Chapter {number}; got {heading_candidates}")
    start = heading_candidates[0]
    stop = next(i for i in range(start + 1, len(assembled_body))
                if words(assembled_body[i]).startswith(f"Chapter {number + 1}:"))
    before = math_objects(part_body)
    after = math_objects(assembled_body[start:stop])
    differences = [
        {"index": i, "part": before[i] if i < len(before) else None,
         "assembled": after[i] if i < len(after) else None}
        for i in range(max(len(before), len(after)))
        if i >= len(before) or i >= len(after) or before[i] != after[i]
    ]
    result["chapters"][str(number)] = {
        "part_sha256": hashlib.sha256(part_path.read_bytes()).hexdigest(),
        "part_math_count": len(before), "assembled_math_count": len(after),
        "chapter_heading_candidates": candidates, "selected_body_heading": start,
        "same_ordered_math": not differences, "differences": differences,
    }
result["status"] = "PASS" if all(c["same_ordered_math"] for c in result["chapters"].values()) else "FAIL"
(HERE / "ch5_ch6_docmath.json").write_text(json.dumps(result, indent=2) + "\n")
print(result["status"], {n: c["part_math_count"] for n, c in result["chapters"].items()})
raise SystemExit(0 if result["status"] == "PASS" else 1)

"""Reproduce final PDF text-bound and unchanged-chapter identity checks.

These checks complement the recorded mathematical and raster reviews. They
cannot determine native Word typography or establish physical assumptions.
"""
import hashlib
import io
import json
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path

from docx import Document
from lxml import etree


OUT = Path(__file__).resolve().parent
REPO = OUT.parents[4]
V8 = REPO / "writing/v8"
DOCX = V8 / "Thesis_V8_Condensed.docx"
PDF = V8 / "Thesis_V8_Condensed.pdf"
BASELINE = "e69dfa62eda80bc0ba5d0c4607a3a183a69f71fb"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args):
    return subprocess.run(args, cwd=REPO, check=True, capture_output=True).stdout


with tempfile.TemporaryDirectory(prefix="thesis-final-bounds-") as temporary:
    bbox = Path(temporary) / "bbox.html"
    plain = Path(temporary) / "text.txt"
    run(["pdftotext", "-bbox-layout", str(PDF), str(bbox)])
    run(["pdftotext", "-layout", str(PDF), str(plain)])
    tree = etree.parse(str(bbox))
    pages = tree.xpath('//*[local-name()="page"]')
    overflow = []
    for number, page in enumerate(pages, 1):
        width, height = float(page.get("width")), float(page.get("height"))
        for word in page.xpath('.//*[local-name()="word"]'):
            box = [float(word.get(key)) for key in ("xMin", "yMin", "xMax", "yMax")]
            if box[0] < 0 or box[1] < 0 or box[2] > width or box[3] > height:
                overflow.append({"page": number, "word": word.text, "box": box})
    text = plain.read_text()
    compact = re.sub(r"\s+", " ", text)
    # Names occur here only to document and check their removal (D-082).
    patterns = {
        "removed_frame": r"(?i)Levelled|levelled\s+(?:frame|coordinates|axes)",
        "replacement_frame": r"GravityAligned|LeveledScene|DisplayLevelled|WorldLevel",
        "old_camera_frame": r"(?i)person\s+space|\{(?:Person|Sensor|P)\}",
        "deleted_figure_references": r"Figures?\s+7\.(?:[7-9]|1[0-9])(?!\d)",
        "old_example_rounding": r"0\.29[,;]?\s*0\.05[,;]?\s*[-\u2212]0\.02",
        "old_twelve_fields": r"(?i)twelve\s+nonzero\s+(?:angles?|fields?)",
    }
    stale = {name: re.findall(pattern, compact) for name, pattern in patterns.items()}
    qa = {
        "pdf_sha256": sha(PDF), "pages": len(pages),
        "words_outside_page": overflow, "stale_text_checks": stale,
        "status": "PASS" if not overflow and not any(stale.values()) else "FAIL",
        "limitations": [
            "Bounding boxes do not prove glyph appearance; actual raster review is separate.",
            "Historical diagnostic metadata and archived drafts are classified by the repository scanner.",
        ],
    }
    (OUT / "pdf_global_qa.json").write_text(json.dumps(qa, indent=2) + "\n")

equations = []
for table in Document(DOCX).tables:
    for row in table.rows:
        if len(row.cells) == 2:
            label = row.cells[-1].text.strip()
            if re.fullmatch(r"\([A-Z0-9]+\.\d+\)", label):
                equations.append(label)

same = {}
for name in ("Chapter_1_Introduction.docx", "Chapter_8_Real_Time_Feasibility.docx",
             "Chapter_10_Conclusions_Future_Work.docx"):
    path = V8 / "condensed" / name
    historical = run(["git", "show", f"{BASELINE}:{path.relative_to(REPO)}"])
    with zipfile.ZipFile(io.BytesIO(historical)) as old, zipfile.ZipFile(path) as new:
        same[name] = old.read("word/document.xml") == new.read("word/document.xml")

modified = set(run(["git", "diff", "--name-only", BASELINE]).decode().splitlines())
modified.update(run(["git", "ls-files", "--others", "--exclude-standard"]).decode().splitlines())
outside = sorted(path for path in modified if not path.startswith("writing/v8/"))
identity = {
    "docx_sha256": sha(DOCX), "pdf_sha256": sha(PDF),
    "numbered_equations": equations, "count": len(equations),
    "numbering_unique": len(set(equations)) == len(equations),
    "unaffected_part_xml_identical_to_e69dfa6": same,
    "scope_modified_paths_outside_v8": outside,
}
(OUT / "delivery_artifact_identity.json").write_text(json.dumps(identity, indent=2) + "\n")
assert qa["status"] == "PASS", qa
assert len(equations) == 56 and len(set(equations)) == 56, equations
assert all(same.values()) and not outside, identity
print("PASS: PDF text bounds and stale-reference scan; 56 numbered equations;")
print("PASS: Chapters 1, 8 and approved 10 body XML unchanged; V8-only change scope.")
print("DOCX_SHA256", identity["docx_sha256"])
print("PDF_SHA256", identity["pdf_sha256"])
print("PAGES", len(pages))

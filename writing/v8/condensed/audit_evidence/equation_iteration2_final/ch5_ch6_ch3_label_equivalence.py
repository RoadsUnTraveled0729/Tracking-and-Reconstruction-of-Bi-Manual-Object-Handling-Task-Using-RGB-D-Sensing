#!/usr/bin/env python3
"""Verify unchanged Chapter 5/6 evidence after the final Chapter 3 label edit.

Run the current numerical, assembled-math and raster diagnostics first.
This compares their current artifacts with the preserved accepted review;
it does not perform a new visual or other-chapter review.
"""
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SNAPSHOT = HERE / "visual_ch5_ch6_reviewed_99367be8_snapshot.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((HERE / name).read_text())


snapshot = json.loads(SNAPSHOT.read_text())
before = snapshot["evidence"]["visual_ch5_ch6_manifest.json"]["content"]
current = read("visual_ch5_ch6_manifest.json")
old_pages = {page["pdf_page"]: page for page in before["raster_pages"]}
new_pages = {page["pdf_page"]: page for page in current["raster_pages"]}
assert old_pages.keys() == new_pages.keys(), "Reviewed page coverage changed"
pages = [{
    "pdf_page": page,
    "reviewed_png_sha256": old_pages[page]["png_sha256"],
    "current_png_sha256": new_pages[page]["png_sha256"],
    "identical": old_pages[page]["png_sha256"] == new_pages[page]["png_sha256"],
} for page in sorted(new_pages)]
assert len(pages) == 34 and all(page["identical"] for page in pages)
assert digest(REPO / "writing/v8/Thesis_V8_Condensed.pdf") == current["pdf_sha256"]
assert current["pdf_sha256"] == "4e1e00cd0dd6c6c93a2b20d9f9abd6a2996c646e6aae3d38a35ee9ef2c727f9d"
unchanged = []
for name, value in current["artifact_sha256"].items():
    assert digest(REPO / name) == value, f"Current source hash differs: {name}"
    if name == "writing/v8/Thesis_V8_Condensed.docx":
        continue
    assert before["artifact_sha256"][name] == value, f"Chapter 5/6 artifact changed: {name}"
    unchanged.append(name)
math = read("ch5_ch6_docmath.json")
docx_hash = current["artifact_sha256"]["writing/v8/Thesis_V8_Condensed.docx"]
assert docx_hash == "d99335e683b9cf2cebcfdf424be495a9b1d9f9a52a4fbd30c6815036c4996b14"
assert math["assembled_sha256"] == docx_hash and math["status"] == "PASS"
assert math["chapters"]["5"]["part_math_count"] == 118
assert math["chapters"]["6"]["part_math_count"] == 22
ch5 = read("ch5_diagnostic.json")
ch6 = read("ch6_numeric.json")
assert ch5["summary"] == {"pass": 16, "fail": 0}
assert ch6["passed"] == 42 and ch6["failed"] == 0 and ch6["status"] == "PASS"
prior_pdf = Path(snapshot["reviewed_pdf_temporary_path"])
prior_file_check = "Prior temporary PDF absent; accepted raster hashes preserved in snapshot"
if prior_pdf.exists():
    assert digest(prior_pdf) == snapshot["reviewed_pdf_sha256"]
    prior_file_check = "PASS: preserved prior PDF hash equals the accepted review hash"
result = {
    "status": "PASS",
    "scope": "Chapter 5/6 artifact refresh after parent-reported Chapter 3 label-only reassembly; no new broad audit",
    "previous_reviewed_pdf_sha256": snapshot["reviewed_pdf_sha256"],
    "current_pdf_sha256": current["pdf_sha256"],
    "current_docx_sha256": docx_hash,
    "prior_pdf_file_check": prior_file_check,
    "review_snapshot_sha256": digest(SNAPSHOT),
    "page_count": len(pages),
    "identical_page_count": sum(page["identical"] for page in pages),
    "page_comparison": pages,
    "unchanged_chapter_artifacts": unchanged,
    "ordered_math_identity": {"chapter5": 118, "chapter6": 22, "status": math["status"]},
    "fresh_numerical_results": {"chapter5": ch5["summary"], "chapter6": {"pass": ch6["passed"], "fail": ch6["failed"]}},
    "current_evidence_sha256": {name: digest(HERE / name) for name in [
        "ch5_ch6_docmath.json", "ch5_diagnostic.json", "ch6_numeric.json",
        "visual_ch5_ch6_manifest.json",
    ]},
    "conclusion": "All 34 current Chapter 5/6 page rasters are identical to the accepted review; its visual dispositions carry forward unchanged.",
}
(HERE / "ch5_ch6_ch3_label_equivalence.json").write_text(json.dumps(result, indent=2) + "\n")
print("PASS: 34/34 accepted page rasters identical; math 118/22; numeric PASS16/PASS42")

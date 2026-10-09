#!/usr/bin/env python3
"""Render the final Chapter 5/6 review pages and pin their provenance.

This script records raster identity, not a machine judgement of visual
quality. The human-readable report records the actual visual inspection.
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
PDF = REPO / "writing/v8/Thesis_V8_Condensed.pdf"
OUT = Path("/tmp/final_ch5_ch6_raster")
PAGES = list(range(72, 93)) + list(range(100, 113))
DPI = 115


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(page):
    stem = OUT / f"page_{page:03d}"
    subprocess.run([
        "pdftoppm", "-f", str(page), "-l", str(page), "-singlefile",
        "-r", str(DPI), "-png", str(PDF), str(stem),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    image = stem.with_suffix(".png")
    return {
        "pdf_page": page,
        "printed_page": page - 20,
        "png_sha256": digest(image),
        "temporary_png": str(image),
    }


OUT.mkdir(parents=True, exist_ok=True)
pdf_before = digest(PDF)
with ThreadPoolExecutor(max_workers=4) as pool:
    pages = list(pool.map(render, PAGES))
if digest(PDF) != pdf_before:
    raise RuntimeError("PDF changed during raster generation; rerun on the stable final PDF.")
prior_path = HERE / "visual_ch5_ch6_first_pass.json"
prior = json.loads(prior_path.read_text())
prior_pages = {page["pdf_page"]: page for page in prior["raster_pages"]}
for page in pages:
    page["same_as_first_visual_pass"] = (
        page["png_sha256"] == prior_pages[page["pdf_page"]]["png_sha256"]
    )
artifacts = [
    "writing/v8/Thesis_V8_Condensed.docx",
    "writing/v8/condensed/Chapter_5_Pose_Recovery.docx",
    "writing/v8/condensed/Chapter_6_System_Integration.docx",
    "writing/v8/condensed/scripts/build_ch5.py",
    "writing/v8/condensed/scripts/build_ch6.py",
    "writing/v8/condensed/scripts/make_ch5_flow_final_fig.py",
    "writing/v8/condensed/scripts/make_ch5_offset_final_fig.py",
    "writing/v8/condensed/figures/ch5_fig_flow.png",
    "writing/v8/condensed/figures/ch5_fig_offset.png",
    "writing/v8/condensed/scripts/make_ch6_frames_final_fig.py",
    "writing/v8/condensed/figures/ch6_fig_frames.png",
]
for optional in (
    "writing/v8/condensed/scripts/make_ch5_ik_final_fig.py",
    "writing/v8/condensed/figures/ch5_fig_ik.png",
):
    if (REPO / optional).exists():
        artifacts.append(optional)
figure_embedding = {}
assembled = REPO / "writing/v8/Thesis_V8_Condensed.docx"
for name, chapter in (("ch5_fig_flow.png", "Chapter_5_Pose_Recovery.docx"),
                      ("ch5_fig_offset.png", "Chapter_5_Pose_Recovery.docx"),
                      ("ch5_fig_ik.png", "Chapter_5_Pose_Recovery.docx"),
                      ("ch6_fig_frames.png", "Chapter_6_System_Integration.docx")):
    source = REPO / "writing/v8/condensed/figures" / name
    if not source.exists():
        continue
    source_hash = digest(source)
    figure_embedding[name] = {}
    for label, path in (("part", REPO / "writing/v8/condensed" / chapter),
                        ("assembled", assembled)):
        with ZipFile(path) as archive:
            matches = [entry for entry in archive.namelist()
                       if entry.startswith("word/media/")
                       and hashlib.sha256(archive.read(entry)).hexdigest() == source_hash]
        figure_embedding[name][label + "_matches"] = matches
        if not matches:
            raise RuntimeError(f"Current {name} is missing from the {label} DOCX.")
manifest = {
    "scope": "Raster provenance; actual visual dispositions are in visual_ch5_ch6.md.",
    "pdf_sha256": pdf_before,
    "artifact_sha256": {name: digest(REPO / name) for name in artifacts},
    "first_visual_pass_manifest_sha256": digest(prior_path),
    "figure_embedding": figure_embedding,
    "render": {"tool": "pdftoppm", "dpi": DPI, "format": "png", "page_numbering": "physical PDF, one based"},
    "raster_pages": pages,
    "changed_pages_since_first_visual_pass": [
        page["pdf_page"] for page in pages if not page["same_as_first_visual_pass"]
    ],
}
(HERE / "visual_ch5_ch6_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(f"Rendered {len(pages)} pages; changed since first visual pass: "
      f"{manifest['changed_pages_since_first_visual_pass']}")

#!/usr/bin/env python3
"""Build a complete Chinese DRAFT of the thesis (docx) from the finished
literal translation in writing/v9/zh/<Part>_zh.md, one part at a time, in
the fixed part order below.

Figures are pulled from the built English chapter docx of the same part
(writing/v9/<Part>.docx): every paragraph in that docx carrying a
w:drawing/a:blip contributes its image, in document order, and the k-th
[FIGURE] marker in the Chinese Markdown gets the k-th image of that part.

Layout quality does not matter; completeness does: every heading,
paragraph, table, caption, equation line and figure must appear, in order.

Usage: python3 writing/v9/zh/make_zh_draft.py
(run from the repository root)
"""
import io
import re
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches
from docx.oxml.ns import qn

REPO_ROOT = Path(__file__).resolve().parents[3]
ZH_DIR = REPO_ROOT / "writing" / "v9" / "zh"
EN_DIR = REPO_ROOT / "writing" / "v9"

# Part order, matching the merged Thesis_V9_zh.md.
PARTS = [
    "FrontMatter_V9",
    "Chapter_1_Introduction",
    "Chapter_2_Experimental_Setup",
    "Chapter_3_Kinematic_Modeling",
    "Chapter_4_Object_Tracking",
    "Chapter_5_Pose_Recovery",
    "Chapter_6_System_Integration",
    "Chapter_7_Evaluation",
    "Chapter_8_Real_Time_Feasibility",
    "Chapter_9_Discussion",
    "Chapter_10_Conclusions_Future_Work",
    "Appendices",
]

# ---------------------------------------------------------------------------
# Font selection (step 3)
# ---------------------------------------------------------------------------


def pick_ea_font():
    try:
        out = subprocess.run(
            ["fc-list"], capture_output=True, text=True, check=True
        ).stdout
    except Exception:
        out = ""
    if re.search(r"noto sans cjk sc", out, re.IGNORECASE):
        return "Noto Sans CJK SC"
    return "AR PL UMing CN"


EA_FONT = pick_ea_font()
LATIN_FONT = "Times New Roman"
MONO_FONT = "Courier New"


def set_run_fonts(run, latin=LATIN_FONT, ea=EA_FONT, bold=None, italic=None):
    """Set Latin + eastAsia fonts on a run, per the required recipe."""
    run.font.name = latin
    run._element.rPr.rFonts.set(qn("w:eastAsia"), ea)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    return run


def set_style_fonts(style, latin=LATIN_FONT, ea=EA_FONT, bold=None, size=None):
    style.font.name = latin
    if size is not None:
        style.font.size = size
    if bold is not None:
        style.font.bold = bold
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        from docx.oxml import OxmlElement

        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), ea)


# ---------------------------------------------------------------------------
# Markdown block classification (step 1)
# ---------------------------------------------------------------------------

HAN_RE = re.compile(r"[一-鿿]")
EQNUM_RE = re.compile(r"\([0-9]+\.[0-9]+\)\s*[.。]?\s*$")
MATHTOK_RE = re.compile(r"[=×‖√∑∂≈≤≥±]")
CAP_RE = re.compile(r"^(图|表)\s*[A-Za-z0-9]+(\.[0-9]+)+\s*[.。]")
HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$")
TABLE_SEP_RE = re.compile(r"^[\s:|-]+$")


def split_blocks(text):
    raw = re.split(r"\n\s*\n", text)
    return [b.strip() for b in raw if b.strip()]


def join_lines(block):
    return " ".join(line.strip() for line in block.splitlines() if line.strip())


def classify_block(block):
    if block == "[FIGURE]":
        return "figure", None
    m = HEADING_RE.match(block)
    if m:
        level = len(m.group(1))
        return "heading", (level, join_lines(m.group(2)))
    if block.startswith("|"):
        rows = []
        for line in block.splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(TABLE_SEP_RE.match(c) or c == "" for c in cells):
                continue  # header separator row
            rows.append(cells)
        return "table", rows
    text = join_lines(block)
    han = len(HAN_RE.findall(text))
    if (EQNUM_RE.search(text) and han <= 4) or (han <= 2 and MATHTOK_RE.search(text)):
        return "equation", text
    if CAP_RE.match(text):
        return "caption", text
    return "paragraph", text


# ---------------------------------------------------------------------------
# Image extraction from the built English chapter docx (step 2)
# ---------------------------------------------------------------------------


def extract_images(docx_path):
    if not docx_path.exists():
        return []
    doc = Document(str(docx_path))
    body = doc.element.body
    images = []
    for p in body.findall(".//" + qn("w:p")):
        for blip in p.findall(".//" + qn("a:blip")):
            rid = blip.get(qn("r:embed"))
            if rid is None:
                continue
            try:
                part = doc.part.rels[rid].target_part
                images.append(part.blob)
            except KeyError:
                pass
    return images


# ---------------------------------------------------------------------------
# Document assembly
# ---------------------------------------------------------------------------


def configure_styles(doc):
    normal = doc.styles["Normal"]
    set_style_fonts(normal, latin=LATIN_FONT, ea=EA_FONT, size=Pt(12))
    for name in ("Heading 1", "Heading 2", "Heading 3"):
        style = doc.styles[name]
        set_style_fonts(style, latin=LATIN_FONT, ea=EA_FONT, bold=True)


def add_heading(doc, level, text, page_break=False):
    para = doc.add_heading(level=level)
    if page_break:
        para.paragraph_format.page_break_before = True
    run = para.add_run(text)
    set_run_fonts(run, bold=True)
    return para


def add_paragraph_text(doc, text, italic=False, center=False):
    para = doc.add_paragraph()
    if center:
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run(text)
    set_run_fonts(run, italic=italic)
    return para


def add_equation(doc, text):
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run(text)
    set_run_fonts(run, latin=MONO_FONT, ea=EA_FONT)
    return para


def add_table(doc, rows):
    if not rows:
        return
    ncols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=ncols)
    try:
        table.style = "Table Grid"
    except KeyError:
        pass
    for ri, row in enumerate(rows):
        for ci in range(ncols):
            text = row[ci] if ci < len(row) else ""
            cell = table.cell(ri, ci)
            cell.text = ""
            run = cell.paragraphs[0].add_run(text)
            set_run_fonts(run, bold=(ri == 0))


def add_image(doc, image_bytes):
    doc.add_picture(io.BytesIO(image_bytes), width=Inches(6))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER


def process_part(doc, part_name, report):
    md_path = ZH_DIR / f"{part_name}_zh.md"
    docx_path = EN_DIR / f"{part_name}.docx"
    text = md_path.read_text(encoding="utf-8")
    blocks = split_blocks(text)
    images = extract_images(docx_path)

    counts = dict(headings=0, paragraphs=0, tables=0, equations=0, figures=0)
    img_idx = 0
    is_chapter = part_name.startswith("Chapter_")
    is_appendices = part_name == "Appendices"

    for block in blocks:
        kind, payload = classify_block(block)
        if kind == "heading":
            level, htext = payload
            counts["headings"] += 1
            page_break = False
            if level == 1 and is_chapter:
                page_break = True
            elif level == 1 and is_appendices:
                page_break = True
            add_heading(doc, level, htext, page_break=page_break)
        elif kind == "table":
            counts["tables"] += 1
            add_table(doc, payload)
        elif kind == "figure":
            counts["figures"] += 1
            if img_idx < len(images):
                add_image(doc, images[img_idx])
                img_idx += 1
            else:
                add_paragraph_text(
                    doc,
                    f"[MISSING IMAGE: part {part_name}, figure marker #{counts['figures']}]",
                    italic=True,
                )
        elif kind == "equation":
            counts["equations"] += 1
            add_equation(doc, payload)
        elif kind == "caption":
            counts["paragraphs"] += 1
            add_paragraph_text(doc, payload, italic=True, center=True)
        else:  # paragraph
            counts["paragraphs"] += 1
            add_paragraph_text(doc, payload)

    mismatch = None
    if counts["figures"] != len(images):
        mismatch = (
            f"{part_name}: {counts['figures']} [FIGURE] markers vs "
            f"{len(images)} images found in {docx_path.name} "
            f"(used {min(img_idx, len(images))})"
        )

    report.append(
        {
            "part": part_name,
            "counts": counts,
            "images_found": len(images),
            "images_used": img_idx,
            "mismatch": mismatch,
        }
    )


def main():
    doc = Document()
    configure_styles(doc)

    report = []
    for part_name in PARTS:
        process_part(doc, part_name, report)

    out_docx = ZH_DIR / "Thesis_V9_zh_draft.docx"
    doc.save(str(out_docx))

    # Print machine-checkable summary; the caller can also inspect the
    # returned report dicts if this module is imported.
    print(f"EA_FONT={EA_FONT}")
    for row in report:
        c = row["counts"]
        print(
            f"{row['part']}: headings={c['headings']} paragraphs={c['paragraphs']} "
            f"tables={c['tables']} equations={c['equations']} "
            f"figures={c['figures']} images_found={row['images_found']} "
            f"images_used={row['images_used']}"
        )
        if row["mismatch"]:
            print(f"  MISMATCH: {row['mismatch']}")
    print(f"Saved: {out_docx}")


if __name__ == "__main__":
    main()

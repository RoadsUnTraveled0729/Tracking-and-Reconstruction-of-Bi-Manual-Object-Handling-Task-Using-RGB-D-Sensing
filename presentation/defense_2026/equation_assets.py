#!/usr/bin/env python3
"""Render exact equation crops from the immutable final thesis PDF.

These are source quotations, not re-typeset or simplified equations. Crop
coordinates are manually reviewed PDF points, measured from the top left.
The source's reference-frame labels, vector type, hats, bars, primes,
subscripts, superscripts, fractions and matrices are preserved by Poppler.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree
import zipfile

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "writing/v9/Thesis_V9.pdf"
SOURCE_SHA256 = "cab52bddd93b9ef40b9c42f718b9a17ba6af6f2a7a08124a8ce366ee30d9c929"
OUT = HERE / "equations"
CATALOG = HERE / "equation_catalog.json"
DPI = 600

# (key, one-based PDF page, exact body crop in PDF points, equation, title).
# Two to four PDF points of clear margin retain antialiased glyph edges.
SPECS = [
    ("eq_2_1", 27, (225, 315, 388, 341), "2.1", "Proper-rotation projection"),
    ("eq_3_1", 35, (212, 686, 400, 709), "3.1", "Camera point reflection"),
    ("eq_3_2", 37, (219, 315, 394, 364), "3.2", "Frame-labelled homogeneous transform"),
    ("eq_3_3", 37, (249, 425, 364, 452), "3.3", "Inverse rotation for a segment direction"),
    ("eq_3_4", 37, (212, 560, 401, 629), "3.4", "Inverse point and homogeneous transforms"),
    ("eq_3_7", 40, (220, 342, 392, 388), "3.7", "Torso right axis from the hips"),
    ("eq_3_8", 40, (232, 430, 380, 454), "3.8", "Torso spine-side vector"),
    ("eq_3_9", 40, (223, 567, 389, 614), "3.9", "Torso forward axis"),
    ("eq_3_10", 41, (219, 79, 394, 105), "3.10", "Torso up axis"),
    ("eq_3_11", 41, (193, 238, 420, 267), "3.11", "Torso rotation matrix"),
    ("eq_3_12", 41, (230, 329, 382, 378), "3.12", "Right-hip root transform"),
    ("eq_3_15", 45, (251, 255, 363, 278), "3.15", "Root Euler rotation order"),
    ("eq_3_16", 45, (196, 357, 418, 428), "3.16", "Expanded root rotation matrix"),
    ("eq_3_17", 45, (168, 488, 445, 513), "3.17", "Root Euler extraction"),
    ("eq_3_18", 46, (241, 248, 372, 273), "3.18", "Shoulder swing and twist composition"),
    ("eq_3_19", 46, (138, 381, 475, 408), "3.19", "Upper-arm direction and swing"),
    ("eq_3_20", 47, (272, 372, 341, 397), "3.20", "Shoulder elevation"),
    ("eq_3_21", 47, (255, 462, 358, 487), "3.21", "Shoulder azimuth"),
    ("eq_3_22", 47, (236, 683, 377, 709), "3.22", "Undo swing on the forearm vector"),
    ("eq_3_23", 48, (252, 178, 362, 203), "3.23", "Shoulder twist"),
    ("eq_3_24", 48, (221, 547, 392, 572), "3.24", "Elbow coordinate extraction"),
    ("eq_4_1", 55, (249, 598, 363, 622), "4.1", "Object pose in the desk world"),
    ("eq_5_1", 67, (208, 326, 405, 350), "5.1", "Rigid-grasp relation"),
    ("eq_5_2", 67, (189, 487, 424, 514), "5.2", "Object-local grasp observation"),
    ("eq_5_3", 68, (227, 571, 387, 609), "5.3", "Least-squares offset mean"),
    ("eq_5_4", 69, (181, 128, 432, 152), "5.4", "Recursive grasp-offset update"),
    ("eq_5_5", 71, (200, 191, 413, 237), "5.5", "Normalized direction-memory update"),
    ("eq_5_6", 71, (228, 388, 385, 415), "5.6", "Direction-memory wrist reconstruction"),
    ("eq_5_7", 72, (212, 80, 401, 105), "5.7", "Object-derived wrist target in Scene"),
    ("eq_5_8", 73, (179, 78, 434, 108), "5.8", "Two-link length constraints"),
    ("eq_5_9", 73, (253, 305, 360, 347), "5.9", "Two-link law of cosines"),
    ("eq_5_10", 73, (188, 455, 425, 481), "5.10", "Elbow-circle centre and radius"),
    ("eq_5_11", 73, (180, 568, 433, 595), "5.11", "Family of possible elbows"),
    ("eq_5_12", 74, (119, 150, 491, 195), "5.12", "Direction prior selects the elbow"),
    ("eq_6_1", 86, (248, 490, 365, 583), "6.1", "World-to-display coordinate conversion"),
    ("eq_6_2", 87, (157, 272, 456, 336), "6.2", "Person point and anchor transformation"),
    ("eq_6_3", 88, (152, 79, 460, 169), "6.3", "Anchor factorization and fixed rotation"),
    ("eq_6_4", 89, (238, 190, 375, 232), "6.4", "Upper-arm and forearm chain composition"),
    ("eq_6_5", 89, (230, 405, 383, 430), "6.5", "Scene bone rotation with captured rest axes"),
    ("eq_6_6", 92, (247, 511, 366, 588), "6.6", "Gravity alignment and floor placement"),
    ("eq_D_2", 147, (202, 533, 412, 573), "D.2", "Pixel-to-camera back-projection"),
    ("scene_anchor_rotation", 89, (255, 466, 358, 491), None, "Gravity-aligned person anchor"),
    # Round 8 (ROUND8_NOTES.md R8-E1): the remaining numbered equations of
    # Chapters 3, 4 and 7. Boxes are the measured ink bounds of each equation
    # body (ink = grey value below 250 at 600 dpi, numbers excluded) widened by
    # 4 pt horizontally and 5 pt vertically and rounded outward to whole points.
    # Appended after the earlier entries so earlier contact sheets keep their bytes.
    ("eq_3_5", 38, (221, 348, 390, 461), "3.5", "Root, shoulder and elbow transforms"),
    ("eq_3_6", 38, (239, 675, 373, 700), "3.6", "Chained right elbow frame in Camera'"),
    ("eq_3_13", 44, (197, 259, 414, 306), "3.13", "Shoulder frame relative to the root"),
    ("eq_3_14", 44, (190, 507, 422, 554), "3.14", "Elbow frame relative to the shoulder"),
    ("eq_4_2", 58, (180, 257, 433, 305), "4.2", "Object-track cleaning rule"),
    ("eq_7_1", 100, (259, 281, 352, 358), "7.1", "Segment length, absolute and relative error"),
    ("eq_7_2", 100, (242, 531, 370, 603), "7.2", "Sample mean and covariance"),
    ("eq_7_3", 101, (231, 82, 382, 138), "7.3", "Orthogonal least-squares line fit"),
    ("eq_7_4", 101, (248, 200, 364, 230), "7.4", "Perpendicular distance to the fitted line"),
    ("eq_7_5", 107, (224, 298, 388, 326), "7.5", "Rendered-rig positional error in Scene"),
    ("eq_7_6", 115, (199, 168, 413, 196), "7.6", "Masked-landmark deviation in Camera'"),
]
ROUND8_KEYS = ("eq_3_5", "eq_3_6", "eq_3_13", "eq_3_14", "eq_4_2", "eq_7_1",
               "eq_7_2", "eq_7_3", "eq_7_4", "eq_7_5", "eq_7_6")

SEMANTIC_NOTES = {
    "eq_2_1": "The translation arithmetic mean is stated in prose; no surrogate mean() formula is quoted.",
    "eq_3_1": "F applies to points. It is a reflection, not a proper rotation matrix.",
    "eq_3_7": "P_24 and P_23 are landmark points in Camera'; the hat denotes a unit axis.",
    "eq_3_8": "This spine-side vector is not necessarily perpendicular to the hip line.",
    "eq_3_18": "Right-arm composition. Left segment vectors are reflected before the same solve.",
    "eq_3_22": "Both input and output vectors are in L12. The operators are not frame-relative transforms.",
    "eq_3_23": "A zero perpendicular forearm component makes twist unobservable.",
    "eq_3_24": "Retain both coordinates exactly as printed. e_z carries no independent model information.",
    "eq_4_1": "The inverse of the calibrated desk-to-camera anchor maps Camera into World; camera must remain fixed.",
    "eq_5_2": "Measured wrist p_wr and marker origin are in Scene; h is in MappedMarker.",
    "eq_5_4": "The thesis uses gain c, set to 0.02; it is not the direction-memory gain alpha.",
    "eq_5_5": "The thesis uses gain alpha, set to 0.30; update only from measured endpoints.",
    "eq_5_7": "w denotes an inferred target in Scene. Convert it to Camera' before the arm solve.",
    "eq_5_8": "Both constraints are in Camera'. On recovery frames, transformed w replaces p_wr.",
    "eq_5_10": "The symbol j is the shoulder triangle angle; r_c is the elbow-circle radius.",
    "eq_5_11": "The scalar s is the remaining swivel, not a shoulder point or the torso spine vector.",
    "eq_5_12": "Exact reachable-target construction. Degenerate, out-of-reach and near-extension cases retain guards.",
    "eq_6_1": "S changes both world reference axes and object-marker axes; the result uses MappedMarker.",
    "eq_6_2": "Person anchor cancels the two handedness changes. Do not conjugate a body rotation by this anchor.",
    "eq_6_4": "Shown for the right arm. Root and shoulder frames share orientation; left signs follow Section 6.3.",
    "eq_6_5": "Three distinct frame relations: scene anchor, solved segment chain, and captured bone rest axes.",
    "eq_6_6": "t_f is recording-specific floor translation; it changes positions, not joint angles.",
    "eq_D_2": "The thesis uses lowercase x,y,z and Camera p. z is aligned sensor depth.",
    "eq_4_2": "Compiled Eq. 4.2 is the cleaning rule; the stale zh/src export numbers it 4.3 and has an extra inverse-anchor 4.2.",
    "eq_7_4": "d_i describes scatter about the fitted line; the thesis states it does not measure physical accuracy.",
    "eq_7_5": "Both positions are in Scene; the equation applies to both the kinematic-model and the rendered-rig error.",
    "eq_7_6": "Both positions are in Camera'; no display frame enters this measure.",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def docx_equation_numbers() -> set[str]:
    """Confirm every numbered crop also exists in native thesis OMML."""
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
                 "m": "http://schemas.openxmlformats.org/officeDocument/2006/math"}
    with zipfile.ZipFile(ROOT/"writing/v9/Thesis_V9.docx") as package:
        document = ElementTree.fromstring(package.read("word/document.xml"))
    found = set()
    for row in document.findall(".//w:tr", namespace):
        if row.find(".//m:oMath", namespace) is None:
            continue
        value = " ".join(node.text or "" for node in row.findall(".//w:t", namespace))
        found.update(re.findall(r"\(((?:[2-7]|D)\.\d+)\)", value))
    return found


def render_crop(page: int, box: tuple, path: Path) -> dict:
    scale = DPI / 72
    x0, y0 = math.floor(box[0] * scale), math.floor(box[1] * scale)
    x1, y1 = math.ceil(box[2] * scale), math.ceil(box[3] * scale)
    cmd = ["pdftocairo", "-f", str(page), "-l", str(page), "-r", str(DPI),
           "-png", "-transp", "-singlefile", "-x", str(x0), "-y", str(y0),
           "-W", str(x1-x0), "-H", str(y1-y0), str(SOURCE), str(path.with_suffix(""))]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    with Image.open(path) as image:
        alpha = image.convert("RGBA").getchannel("A")
        ink = alpha.getbbox()
        if ink is None:
            raise ValueError(f"Empty equation crop: {path}")
        # A nonempty clear border catches cropped hats, bars and subscripts.
        if ink[0] == 0 or ink[1] == 0 or ink[2] == image.width or ink[3] == image.height:
            raise ValueError(f"Equation touches crop boundary: {path}: {ink}")
        return {"path": str(path.relative_to(ROOT)), "width_px": image.width,
                "height_px": image.height, "aspect": image.width/image.height,
                "sha256": sha256(path), "crop_pts": list(box),
                "render_crop_px": [x0, y0, x1-x0, y1-y0],
                "nontransparent_bounds_px": list(ink)}


def contact_sheets(entries: dict) -> None:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    # Earlier entries and round-8 entries paginate separately, so adding
    # round-8 crops leaves the earlier sheets byte-identical.
    groups = [[item for item in entries.items() if item[0] not in ROUND8_KEYS],
              [item for item in entries.items() if item[0] in ROUND8_KEYS]]
    pages = [group[start:start+12] for group in groups for start in range(0, len(group), 12)]
    for number, values in enumerate(pages, start=1):
        canvas = Image.new("RGB", (1800, 1440), "white")
        draw = ImageDraw.Draw(canvas)
        for i, (key, entry) in enumerate(values):
            col, row = i % 2, i // 2
            left, top = col*900+24, row*240+12
            draw.text((left, top), f"{key} | p.{entry['printed_page']} | PDF {entry['pdf_page']}",
                      font=font, fill=(30, 40, 50))
            with Image.open(ROOT/entry["path"]) as equation:
                image = equation.convert("RGBA")
                image.thumbnail((844, 180), Image.Resampling.LANCZOS)
                canvas.paste(image, (left+(844-image.width)//2, top+42+(180-image.height)//2), image)
        canvas.save(OUT/f"contact-{number:02d}.png")


def white_variants(entries: dict, keys) -> None:
    """Write RGB-only white copies of the primary crops, as build_deck.py does.

    Same operation as build_deck.white_equation_source: every alpha byte and
    the dimensions are kept, RGB becomes 255. A file is written only when it
    is missing or its pixels differ, so existing white copies keep their bytes.
    build_deck.py still writes white_manifest.json for the keys a deck uses.
    """
    (OUT/"white").mkdir(exist_ok=True)
    for key in keys:
        original = ROOT/entries[key]["path"]
        output = OUT/"white"/original.name
        with Image.open(original) as image:
            alpha = image.convert("RGBA").getchannel("A")
        converted = Image.new("RGBA", alpha.size, (255, 255, 255, 255))
        converted.putalpha(alpha)
        if not output.exists() or Image.open(output).convert("RGBA").tobytes() != converted.tobytes():
            converted.save(output)
        if Image.open(output).getchannel("A").tobytes() != alpha.tobytes():
            raise ValueError(f"Equation recolor changed glyph alpha: {key}")


def build() -> None:
    if sha256(SOURCE) != SOURCE_SHA256:
        raise ValueError("Thesis PDF changed. Review source and crop specifications before regenerating.")
    docx_numbers = docx_equation_numbers()
    OUT.mkdir(exist_ok=True)
    entries = {}
    for key, page, box, number, title in SPECS:
        entry = render_crop(page, box, OUT/f"{key}.png")
        entry.update({"title": title, "pdf_page": page,
                      "printed_page": "D3" if page == 147 else str(page-14),
                      "equation_number": number,
                      "provenance": "exact thesis PDF equation crop",
                      "quoted_or_derived": "exact quotation; no re-typesetting or symbol substitution",
                      "semantic_note": SEMANTIC_NOTES.get(key, "See the cited equation and its surrounding assumptions.")})
        if number is not None:
            if number not in docx_numbers:
                raise ValueError(f"Equation {number} missing from native DOCX OMML.")
            numbered = render_crop(page, (box[0], box[1], 526, box[3]), OUT/f"{key}_numbered.png")
            entry["numbered"] = numbered
            entry["numbered_path"] = numbered["path"]
            entry["docx_omml_equation_verified"] = True
        entries[key] = entry
    catalog = {"schema_version": 1, "source_pdf": str(SOURCE.relative_to(ROOT)),
               "source_sha256": SOURCE_SHA256, "source_docx": "writing/v9/Thesis_V9.docx",
               "source_docx_sha256": sha256(ROOT/"writing/v9/Thesis_V9.docx"),
               "render_dpi": DPI, "background": "transparent; original black thesis glyphs",
               "crop_coordinate_system": "PDF points from top-left; one-based PDF page",
               "renderer": subprocess.run(["pdftocairo", "-v"], capture_output=True, text=True).stderr.splitlines()[0],
               "equations": entries}
    CATALOG.write_text(json.dumps(catalog, indent=2, ensure_ascii=True)+"\n")
    contact_sheets(entries)
    white_variants(entries, ROUND8_KEYS)
    print(f"PASS: {len(entries)} exact thesis equation assets; source and all crop borders verified.")
    print(CATALOG.relative_to(ROOT))


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    build()

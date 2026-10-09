#!/usr/bin/env python3
"""Normal-weight right-column variants of the verified memory diagrams.

Only drawing helpers change: timing, operations, state selection and source
geometry use the preserved teaching_flow renderers. Original files and media
are not overwritten. Native slide text identifies these as schematics.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

import teaching_flow as source

PALETTE = {"BG": "#FFFFFF", "INK": "#22313D", "MUTED": "#52606B",
           "LINE": "#DCE2E6", "TEAL": "#386C8C", "AMBER": "#AB783B",
           "PALE_TEAL": "#F2F6F9", "PALE_AMBER": "#FAF6F0", "PALE_INK": "#F5F6F7"}
OLD_COLORS = {getattr(source, name): value for name, value in PALETTE.items()}
VARIANTS = {
    "teaching_memory_copy_restrained": (source.memory_copy, 40),
    "teaching_merge_restrained": (source.merge, 40),
    "teaching_read_write_restrained": (source.read_write, 48),
}
ORIGINAL = {name: getattr(source, name) for name in ("block", "tile", "arrow")}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def color(value):
    return OLD_COLORS.get(value, value)


def text(draw, rect, value, size=48, ink=PALETTE["INK"], bold=False,
         layer=0, align="center", **kwargs):
    # Keep the exact operation labels and their suppression under moving
    # tiles, using the one requested normal-weight visual-label size.
    assert value.isascii()
    if value.isupper():
        value = "\n".join(line.capitalize() for line in value.splitlines())
    size = 48; bold = False
    x0, y0, x1, y1 = rect
    f = source.font(size, False)
    b = draw.multiline_textbbox((0, 0), value, font=f, spacing=12, align=align)
    tw, th = b[2]-b[0], b[3]-b[1]
    assert tw <= x1-x0 and th <= y1-y0, (value, rect)
    x = x0 if align == "left" else x0+(x1-x0-tw)/2
    y = y0+(y1-y0-th)/2
    xy = (x-b[0], y-b[1])
    actual = draw.multiline_textbbox(xy, value, font=f, spacing=12, align=align)
    assert min(actual[:2]) >= 0 and actual[2] <= source.W and actual[3] <= source.H
    source.TEXT.append((draw, xy, value, size, color(ink), False, layer, align, actual))


def base(title, stage, count):
    source.TEXT.clear(); source.OBSCURERS.clear()
    image = Image.new("RGB", (source.W, source.H), PALETTE["BG"])
    return image, ImageDraw.Draw(image)


def block(draw, rect, title, ink=PALETTE["INK"]):
    return ORIGINAL["block"](draw, rect, title, color(ink))


def tile(draw, center, label, ink=PALETTE["TEAL"], width=490, height=250, layer=0):
    return ORIGINAL["tile"](draw, center, label, color(ink), width, height, layer)


def arrow(draw, a, b, ink=PALETTE["LINE"], width=7):
    return ORIGINAL["arrow"](draw, a, b, color(ink), min(width, 4))


def configure():
    for name, value in PALETTE.items():
        setattr(source, name, value)
    source.text, source.base = text, base
    source.block, source.tile, source.arrow = block, tile, arrow


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview-only", action="store_true")
    parser.add_argument("--asset", choices=list(VARIANTS))
    args = parser.parse_args(); configure()
    names = [args.asset] if args.asset else list(VARIANTS)
    for name in names:
        renderer, duration = VARIANTS[name]
        report = source.export_asset(name, renderer, duration, args.preview_only,
            {"sources": source.SOURCES, "variant_generator": str(Path(__file__).relative_to(source.ROOT.parents[1])),
             "variant_generator_sha256": sha(__file__), "preserved_renderer": str(Path(source.__file__).relative_to(source.ROOT.parents[1])),
             "drawing_changes": "Normal-weight 48px labels; no title, stage counter or provenance heading; common white/gray/blue/amber palette",
             "unchanged": "Original operation logic, geometry, copy ownership, state conditions and timing",
             "intended_slide_width_in": 6.61, "nominal_label_size_on_slide_pt": 48*6.61/1440*72,
             "native_caption_required": "Schematic operation; timing does not measure execution or latency",
             "read_write_guard": "If retries fail remains explicit; a busy first sequence skips one attempt, and up to three attempts may occur in an Update"})
        if args.preview_only:
            continue
        renderer(duration-0.1).save(source.OUT/f"{name}.png")
        report["sha256"]["png"] = sha(source.OUT/f"{name}.png")
        report["poster_state"] = "Poster shows the final explanatory stage; GIF starts from the initial state"
        (source.REVIEW/f"{name}_checks.json").write_text(json.dumps(report, indent=2)+"\n", encoding="ascii")


if __name__ == "__main__":
    main()

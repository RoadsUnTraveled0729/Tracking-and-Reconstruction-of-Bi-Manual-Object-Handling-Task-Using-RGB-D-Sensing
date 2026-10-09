#!/usr/bin/env python3
"""Annotate the pages of Thesis_V9.pdf changed in the post-defence revision.

Renders PDF pages 2, 16, 17, 165 and 166 of writing/v9/Thesis_V9.pdf at
150 dpi with pdftoppm, locates each changed span from the word bounding
boxes reported by `pdftotext -bbox-layout`, and draws a red box around it
with a lettered tag in the left margin. A title band is added above each
page and a legend band below it.

The only pixel constants in this file are margins, band sizes, line widths
and font sizes. Every box position comes from the PDF: word boxes from
pdftotext -bbox-layout, the scanned approval block from the image placement
that `pdftohtml -xml` reports.

Run from anywhere with:
    /usr/bin/python3 writing/v9/audit_evidence/post_defence_2026-10-06/annotate_revision.py
"""

import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PDF = os.path.join(REPO, "writing", "v9", "Thesis_V9.pdf")
OUT_DIR = HERE

DPI = 150                      # brief: render at 150 dpi
SCALE = DPI / 72.0             # PDF points to pixels

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_TEXT = os.path.join(FONT_DIR, "DejaVuSans.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
# Body font of Thesis_V9.pdf (pdffonts: LiberationSerif), used only to trim
# a trailing period off a word box by its true advance width.
FONT_BODY = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"

RED = (220, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Layout margins (pixels), chosen for legibility at 150 dpi.
BOX_PAD_X = 5          # horizontal gap between text and the red box
BOX_PAD_Y = 4          # vertical gap between text and the red box
BOX_WIDTH = 3          # brief: 3 px red rectangle
TAG_SIZE = 30          # side of the square letter tag
TAG_GAP = 10           # gap between the tag and the text column
TITLE_BAND = 56        # height of the title band above the page
LEGEND_FONT = 20       # brief: 20 px legend text
LEGEND_LINE = 34       # legend line pitch
LEGEND_MARGIN = 24     # inner margin of the legend band
SEPARATOR = 2          # grey rule between page and bands

TITLE = ("Thesis_V9.pdf, printed page {printed} (PDF page {pdf}), "
         "post-defence revision 2026-10-06")

# Each mark: tag, kind, spec, legend line.
#   kind "lines": one box per text line over the words from `start` to `end`
#   kind "block": one box around all words from `start` to `end`
#   kind "image": the placed image on the page (scanned block)
# `start` must occur exactly once on the page; `end` is the first match at
# or after the start. `skip` drops leading context words of `start` from the
# box (so "Unity [19]" anchors the match but only "[19]" is boxed). `trim`
# removes trailing characters (a period) from the last word's box, measured
# with the body font's advance widths.
PAGES = [
    {
        "pdf": 2, "printed": "ii", "out": "page_ii_approval.png",
        "marks": [
            ("A", "image", {},
             "signed approval block, from the scanned page"),
            ("B", "block", {"start": "Date Approved:", "end": "2026"},
             "date approved set to October 6, 2026"),
        ],
    },
    {
        "pdf": 16, "printed": "2", "out": "page_2_introduction.png",
        "marks": [
            ("A", "block", {"start": "visualization [19].", "end": "[19].",
                            "skip": 1, "trim": 1},
             "new citation [19], Unity User Manual"),
            ("B", "block", {"start": "That laboratory work covers the hand,",
                            "end": "in this setting."},
             "new opening paragraph of Section 1.2 (transition from 1.1)"),
            ("C", "lines", {"start": "Deep learning approaches followed",
                            "end": "trackers and include"},
             "transition clause added"),
            ("D", "block", {"start": "[28], [29]", "end": "[29]"},
             "new citations [28], [29], Google MediaPipe documentation"),
            ("E", "lines", {"start": "A held object carries no landmarks,",
                            "end": "a different signal."},
             "new transition sentence"),
        ],
    },
    {
        "pdf": 17, "printed": "3", "out": "page_3_introduction.png",
        "marks": [
            ("A", "lines", {"start": "Occlusion between one hand",
                            "end": "hide the other."},
             "new opening sentence of Section 1.2.2 (transition from 1.2.1)"),
            ("B", "block", {"start": "Unity [19] has been", "end": "[19]",
                            "skip": 1},
             "new citation [19], Unity User Manual"),
        ],
    },
    {
        "pdf": 165, "printed": "R2", "out": "page_R2_references.png",
        "marks": [
            ("A", "block", {"start": "[19] Unity Technologies,",
                            "end": "Accessed: Oct. 6, 2026."},
             "new entry [19], Unity Technologies, Unity 6.6 User Manual"),
            ("B", "block", {"start": "[28] Google,",
                            "end": "Accessed: Oct. 6, 2026."},
             "new entry [28], Google, MediaPipe Solutions guide"),
        ],
    },
    {
        "pdf": 166, "printed": "R3", "out": "page_R3_references.png",
        "marks": [
            ("A", "block", {"start": "[29] Google,",
                            "end": "Accessed: Oct. 6, 2026."},
             "new entry [29], Google, Hand and Pose landmark detection "
             "guides"),
        ],
    },
]


def run(cmd, cwd=None):
    return subprocess.run(cmd, check=True, capture_output=True, cwd=cwd).stdout


def render(page, tmp):
    stem = os.path.join(tmp, "p%d" % page)
    run(["pdftoppm", "-r", str(DPI), "-png", "-f", str(page), "-l", str(page),
         "-singlefile", PDF, stem])
    return Image.open(stem + ".png").convert("RGB")


def words_of(page):
    """Words in reading order: (text, line_id, (x0, y0, x1, y1) in pixels)."""
    raw = run(["pdftotext", "-bbox-layout", "-f", str(page), "-l", str(page),
               PDF, "-"]).decode("utf-8")
    raw = re.sub(r"<!DOCTYPE[^>]*>", "", raw)
    root = ET.fromstring(raw)
    ns = "{http://www.w3.org/1999/xhtml}"
    words = []
    for li, line in enumerate(root.iter(ns + "line")):
        for w in line.iter(ns + "word"):
            box = tuple(float(w.get(k)) * SCALE
                        for k in ("xMin", "yMin", "xMax", "yMax"))
            words.append((w.text, li, box))
    return words


def find(tokens, phrase, start_at=0):
    ph = phrase.split()
    hits = []
    for i in range(start_at, len(tokens) - len(ph) + 1):
        if tokens[i:i + len(ph)] == ph:
            hits.append(i)
    return hits, len(ph)


def span_words(words, spec):
    tokens = [w[0] for w in words]
    hits, _ = find(tokens, spec["start"])
    if len(hits) != 1:
        raise SystemExit("ERROR: start %r matched %d times"
                         % (spec["start"], len(hits)))
    i0 = hits[0] + spec.get("skip", 0)
    ends, n = find(tokens, spec["end"], i0)
    if not ends:
        raise SystemExit("ERROR: end %r not found after %r"
                         % (spec["end"], spec["start"]))
    i1 = ends[0] + n - 1
    sel = [list(w) for w in words[i0:i1 + 1]]
    trim = spec.get("trim", 0)
    if trim:
        text, _, (x0, y0, x1, y1) = sel[-1]
        font = ImageFont.truetype(FONT_BODY, 100)
        full = font.getlength(text)
        kept = font.getlength(text[:-trim])
        sel[-1][2] = (x0, y0, x0 + (x1 - x0) * kept / full, y1)
    return sel


def union(boxes):
    return (min(b[0] for b in boxes) - BOX_PAD_X,
            min(b[1] for b in boxes) - BOX_PAD_Y,
            max(b[2] for b in boxes) + BOX_PAD_X,
            max(b[3] for b in boxes) + BOX_PAD_Y)


def image_box(page, tmp):
    """Placement of the single image on the page, from pdftohtml -xml."""
    run(["pdftohtml", "-xml", "-zoom", "1", "-f", str(page), "-l", str(page),
         PDF, os.path.join(tmp, "img")], cwd=tmp)
    root = ET.parse(os.path.join(tmp, "img.xml")).getroot()
    pg = root.find("page")
    imgs = pg.findall("image")
    if len(imgs) != 1:
        raise SystemExit("ERROR: expected one image on page %d, found %d"
                         % (page, len(imgs)))
    return pg, imgs[0]


def scan_box(page, tmp, img_w):
    pg, im = image_box(page, tmp)
    k = img_w / float(pg.get("width"))
    x0 = float(im.get("left")) * k
    y0 = float(im.get("top")) * k
    x1 = x0 + float(im.get("width")) * k
    y1 = y0 + float(im.get("height")) * k
    return (x0 - BOX_PAD_X, y0 - BOX_PAD_Y, x1 + BOX_PAD_X, y1 + BOX_PAD_Y)


def overlaps(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def place_tags(marks_boxes, words):
    """One tag per mark, in the left margin, level with the box top."""
    text_left = min(w[2][0] for w in words)
    for _, boxes in marks_boxes:
        text_left = min(text_left, min(b[0] for b in boxes))
    x1 = text_left - TAG_GAP - BOX_PAD_X
    x0 = x1 - TAG_SIZE
    if x0 < 0:
        raise SystemExit("ERROR: no room for tags in the left margin")
    tags = []
    for tag, boxes in marks_boxes:
        top = min(b[1] for b in boxes)
        rect = [x0, top, x1, top + TAG_SIZE]
        for other in tags:
            if overlaps(rect, other[1]):
                rect[1] = other[1][3] + 4
                rect[3] = rect[1] + TAG_SIZE
        rect = tuple(rect)
        for w in words:
            if overlaps(rect, w[2]):
                raise SystemExit("ERROR: tag %s overlaps word %r"
                                 % (tag, w[0]))
        tags.append((tag, rect))
    return tags


def annotate(spec, tmp):
    img = render(spec["pdf"], tmp)
    words = words_of(spec["pdf"])
    draw = ImageDraw.Draw(img)
    marks_boxes = []
    for tag, kind, mspec, _ in spec["marks"]:
        if kind == "image":
            boxes = [scan_box(spec["pdf"], tmp, img.width)]
        else:
            sel = span_words(words, mspec)
            if kind == "block":
                boxes = [union([w[2] for w in sel])]
            else:
                by_line = {}
                for w in sel:
                    by_line.setdefault(w[1], []).append(w[2])
                boxes = [union(by_line[k]) for k in sorted(by_line)]
        marks_boxes.append((tag, boxes))
    for _, boxes in marks_boxes:
        for b in boxes:
            draw.rectangle(b, outline=RED, width=BOX_WIDTH)
    tag_font = ImageFont.truetype(FONT_BOLD, LEGEND_FONT)
    for tag, rect in place_tags(marks_boxes, words):
        draw.rectangle(rect, fill=RED)
        cx = (rect[0] + rect[2]) / 2.0
        cy = (rect[1] + rect[3]) / 2.0
        draw.text((cx, cy), tag, fill=WHITE, font=tag_font, anchor="mm")
    return compose(img, spec)


def compose(page_img, spec):
    text_font = ImageFont.truetype(FONT_TEXT, LEGEND_FONT)
    title_font = ImageFont.truetype(FONT_BOLD, LEGEND_FONT)
    n = len(spec["marks"])
    legend_h = 2 * LEGEND_MARGIN + n * LEGEND_LINE
    W = page_img.width
    H = TITLE_BAND + SEPARATOR + page_img.height + SEPARATOR + legend_h
    out = Image.new("RGB", (W, H), WHITE)
    out.paste(page_img, (0, TITLE_BAND + SEPARATOR))
    d = ImageDraw.Draw(out)
    grey = (150, 150, 150)
    d.rectangle((0, TITLE_BAND, W, TITLE_BAND + SEPARATOR - 1), fill=grey)
    y_sep = TITLE_BAND + SEPARATOR + page_img.height
    d.rectangle((0, y_sep, W, y_sep + SEPARATOR - 1), fill=grey)
    title = TITLE.format(printed=spec["printed"], pdf=spec["pdf"])
    d.text((LEGEND_MARGIN, TITLE_BAND / 2.0), title, fill=BLACK,
           font=title_font, anchor="lm")
    y = y_sep + SEPARATOR + LEGEND_MARGIN
    for tag, _, _, legend in spec["marks"]:
        sw = (LEGEND_MARGIN, y, LEGEND_MARGIN + TAG_SIZE - 4,
              y + TAG_SIZE - 4)
        d.rectangle(sw, fill=RED)
        d.text(((sw[0] + sw[2]) / 2.0, (sw[1] + sw[3]) / 2.0), tag,
               fill=WHITE, font=title_font, anchor="mm")
        line = "%s: %s" % (tag, legend)
        d.text((sw[2] + 12, (sw[1] + sw[3]) / 2.0), line, fill=BLACK,
               font=text_font, anchor="lm")
        if sw[2] + 12 + text_font.getlength(line) > W - LEGEND_MARGIN:
            raise SystemExit("ERROR: legend line too long: %r" % line)
        y += LEGEND_LINE
    if d.textlength(title, font=title_font) > W - 2 * LEGEND_MARGIN:
        raise SystemExit("ERROR: title too long for page %d" % spec["pdf"])
    return out


def main():
    if not os.path.isfile(PDF):
        raise SystemExit("ERROR: missing %s" % PDF)
    with tempfile.TemporaryDirectory() as tmp:
        for spec in PAGES:
            out = annotate(spec, tmp)
            path = os.path.join(OUT_DIR, spec["out"])
            out.save(path, optimize=False)
            print("OK %s (%dx%d, %d marks)"
                  % (path, out.width, out.height, len(spec["marks"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())

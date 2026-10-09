#!/usr/bin/env python3
"""Build a journal note from Markdown to Word: by default
journal/KINEMATIC_ANGLES.md -> journal/KINEMATIC_ANGLES.docx; --src and --out
select another note (journal/KINEMATIC_ANGLES_SHORT.md) with the same parser,
styles, self-checks, core properties, page count and deterministic zip.

Word is the deliverable format of the journal derivation (author instruction
2026-10-07, journal/DECISIONS.md J-016); the Markdown file stays the source.
The document is built the way the thesis chapters are built
(writing/v9/scripts/build_ch3.py): python-docx, the thesis house style of
writing/v9/scripts/build_frontmatter.py (Times New Roman, black headings,
Letter page with 1 in top and bottom and 1.25 in side margins), and native
Word equations (OMML) assembled from the builders of writing/v9/scripts/eqn.py.
No LaTeX source text reaches the document.

Markdown reader. It handles exactly the constructs KINEMATIC_ANGLES.md uses
and raises NotImplementedError on any other line shape it cannot classify:
  - ATX headings "# ", "## ", "### " (Heading 1, 2, 3);
  - paragraphs (consecutive non-blank lines, joined with one space), the
    "Status:" preamble included;
  - "- " bullet items, continuation lines indented by two spaces;
  - pipe tables (header row, "| --- |" separator, body rows);
  - images "![Figure N](figures/x.png)" and the caption paragraphs that
    open with "Figure N." or "Table N.";
  - display blocks: a line "$$", the LaTeX body, a line "$$", with an
    optional \\tag{n} (numbered: eqn.add_display_eq, the tag as the
    number; untagged: eqn.add_display_math);
  - inline math $...$ inside paragraphs, bullets, captions and table cells
    (eqn.add_inline_math);
  - backtick code spans (Courier New runs) and fenced code blocks
    (Courier New 9 pt lines, as build_appendix.py prints its listings).

LaTeX-subset translator. Every construct is mapped onto an eqn.py builder or
a native OMML element of the same family; anything outside the subset raises
NotImplementedError, nothing is dropped silently. The subset (verified by
scanning the .md, 2026-10-07):
  leading scripts {}^{A}_{B}R, {}^{A}P_{k}, {}^{A}(...)  -> m:sPre (as
      build_ch3.py's pre(), described-frame slot left blank when absent);
  trailing ^{..}, _{..}, both (m:sSubSup), primes f', f'_y, f_y'^2;
  ^\\circ and {}^\\circ -> a degree sign run;
  \\hat, \\frac, \\dfrac, \\sqrt (m:rad), \\lVert..\\rVert (double-bar
      m:d), \\left( .. \\right) (m:d), \\begin{pmatrix} (eqn.mat with round
      brackets), \\begin{aligned} and \\begin{gathered} (eqn.eqArr, the
      alignment marks & dropped as the thesis's eqArr does), \\\\ and
      \\\\[2mm] row breaks;
  \\mathrm{..} -> upright runs (eqn.nor); \\text{..} -> normal-text runs
      (m:nor, see text_run); \\det, \\sin,
      \\cos, \\tan, \\arctan -> upright function names;
  \\cdot \\times \\approx \\propto \\ne \\neq \\le \\ge \\in \\mid \\pm
      \\lfloor \\rfloor \\{ \\} \\ell and the Greek letters \\alpha \\rho
      \\pi \\theta;
  spacing \\qquad \\quad \\; \\, \\! and "\\ ";
  digits, letters, + - = < > , . ; : / ( ) [ ] | * and '.
A display wider than the equation column is broken at its top-level
relations (=, approx), then if still too wide before a top-level matrix,
into stacked eqArr lines; no symbol is added or removed (J-016).

Run (deterministic; prints the counts and the self-checks):
  /home/luo/anaconda3/bin/python -B journal/scripts/build_docx.py
  /home/luo/anaconda3/bin/python -B journal/scripts/build_docx.py \
      --src journal/KINEMATIC_ANGLES_SHORT.md \
      --out journal/KINEMATIC_ANGLES_SHORT.docx
A relative --src or --out is taken relative to the current directory. Image
paths in the source resolve against the source's folder. The core-property
title is the "# " heading on line 1 of the source (set_core_properties).
"""
import argparse
import re
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "writing" / "v9" / "scripts"))

from docx import Document  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Inches, Pt  # noqa: E402

import build_frontmatter as fm  # noqa: E402
from eqn import (r, nor, sub, sup, hat, frac, mat, d, eqArr,  # noqa: E402
                 add_display_eq, add_display_math, add_inline_math)

# Defaults; main() rebinds them from --src and --out.
SRC = REPO / "journal" / "KINEMATIC_ANGLES.md"
OUT = REPO / "journal" / "KINEMATIC_ANGLES.docx"

MINUS = "\u2212"
TIMES = "\u00d7"
CDOT = "\u00b7"
DEG = "\u00b0"
PRIME = "\u2032"
DBAR = "\u2016"
# A zero-width space before a line or inline piece that opens with a relation
# or operator: Word shows nothing, and LibreOffice's formula import gets an
# operand instead of drawing its missing-operand mark (J-016).
ZWSP = "\u200b"
# A bar that is a separator (\mid, the column bars of (-X_B | Y_B | Z_B)) is
# U+2223; an absolute value is an m:d with bar delimiters, as the thesis
# writes d(.., "|", "|"). A plain "|" in a math run is read as a logical or
# by LibreOffice's formula import (J-016).
MID = "\u2223"

TABLE_PT = 10          # build_ch3.py table text size
TEXT_WIDTH_IN = 6.0    # 8.5 in page minus 2 x 1.25 in (house style)
# Figure widths in inches. 5.0 is build_ch3.py's width for a 4:3 frame
# (Figure 3.2); the square depth-check mosaic gets 5.5 so that it stays under
# half the 9 in text height plus its caption (J-016). The two wide figures
# had build_ch3.py's 6.3 in, wider than this note's 6.0 in text width, and
# ran 0.3 in into the right margin (pdfimages: 1891 px at 300 ppi on page 2,
# 1430 px at 227 ppi on page 34; render of 2026-10-08).
# - The T-pose figure gets 5.75 in: LibreOffice centres an inline picture in
#   this column only up to 5.75 in (picture left edge measured with
#   pdftohtml: 5.5 in -> 1.50 in, 5.75 in -> 1.38 in, 5.9 and 6.0 in -> still
#   1.38 in, so a wider picture runs past the right margin at 7.25 in).
# - The 2 x 2 forward-kinematics figure (1430 x 1166 px) gets 5.1 in, so
#   that it and its seven-line caption (13.8 pt per line in the LibreOffice
#   render) fit on the page below the opening of Section 4.3 with about 20 pt
#   to spare; at 6.3 in the caption ran from page 34 onto page 35, and at
#   6.0 in figure and caption no longer fit and moved to page 35 together.
FIG_WIDTH = {"fig1_tpose_frames.png": 5.75,
             "perfect_frame_overlay.png": 5.0,
             "perfect_frame_depth_check8.png": 5.5,
             "fk_reconstruction.png": 5.1}
# Width of the equation column of eqn.add_display_eq: 6 - 2 x 0.45 in.
EQ_COLUMN_IN = 6.0 - 2 * 0.45
# Estimated em widths (12 pt Cambria Math); calibrated on the rendered PDF.
EM_PER_IN = 72.0 / 12.0
DISPLAY_LIMIT_EM = EQ_COLUMN_IN * EM_PER_IN
# An inline span wider than this is emitted as several adjacent inline
# equations split at top-level relations (then operators), so that a renderer
# that cannot wrap inside an equation object (LibreOffice) wraps between them;
# 22 em is about 3.7 in, under the 6.0 in text width less the bullet indent
# (J-016).
INLINE_LIMIT_EM = 22.0
# In a table cell the pieces are cut shorter, at 8 em (about 1.3 in), and a
# vector (a, b, c)^T may also be cut after its commas, so that the columns of
# Table 6 fit the 6.0 in text width (J-016).
CELL_LIMIT_EM = 8.0
# Cell equations carry w:sz at the 10 pt table size (sized(), for Word), but
# LibreOffice draws them at 12 pt whatever w:sz, the paragraph-mark size or
# the paragraph style say (three variants rendered, 2026-10-08), so column
# widths are estimated at 12 pt (scale 1.0) and nothing is clipped there.
CELL_SCALE = 1.0

GREEK = {"alpha": "\u03b1", "rho": "\u03c1", "pi": "\u03c0",
         "theta": "\u03b8"}
SYMBOL = {  # name -> (text, class); class: bin, rel, ord
    "cdot": (CDOT, "dot"), "times": (TIMES, "bin"), "pm": ("\u00b1", "bin"),
    "approx": ("\u2248", "rel"), "propto": ("\u221d", "rel"),
    "ne": ("\u2260", "rel"), "neq": ("\u2260", "rel"),
    "le": ("\u2264", "rel"), "ge": ("\u2265", "rel"),
    "in": ("\u2208", "rel"), "mid": (MID, "rel"),
    "lfloor": ("\u230a", "open"), "rfloor": ("\u230b", "close"),
    "ell": ("\u2113", "ord"),
}
FUNCS = {"det", "sin", "cos", "tan", "arctan"}
SPACES = {"qquad": "        ", "quad": "    ", ";": " ", ",": " ",
          " ": " ", "!": ""}
SLOT = '<m:r><m:t xml:space="preserve"> </m:t></m:r>'


# ---------------------------------------------------------------------------
# OMML builders not in eqn.py (same element family, same string style)
# ---------------------------------------------------------------------------
def subsup(base, s, p):
    return (f"<m:sSubSup><m:e>{base}</m:e><m:sub>{s}</m:sub>"
            f"<m:sup>{p}</m:sup></m:sSubSup>")


def rad(e):
    return ('<m:rad><m:radPr><m:degHide m:val="1"/></m:radPr><m:deg/>'
            f"<m:e>{e}</m:e></m:rad>")


def pre(base, ref, desc=None):
    """Craig left indices, exactly build_ch3.py's pre()."""
    lower = desc if desc else SLOT
    upper = ref if ref else SLOT
    return ("<m:sPre>"
            f"<m:sub>{lower}</m:sub><m:sup>{upper}</m:sup>"
            f"<m:e>{base}</m:e></m:sPre>")


# ---------------------------------------------------------------------------
# Math tree
# ---------------------------------------------------------------------------
class Node:
    """kind: run, sub, sup, subsup, pre, hat, frac, rad, delim, mat, arr, seq.
    A run carries text, upright flag and a class (ord, bin, rel, dot, open,
    close, punct, space, func)."""

    def __init__(self, kind, *args, **kw):
        self.kind, self.args, self.kw = kind, list(args), kw

    def __repr__(self):
        return f"Node({self.kind}, {self.args!r})"


def run(text, upright=False, cls="ord"):
    return Node("run", text, upright=upright, cls=cls)


def text_run(text):
    """A \\text{..} word as an OMML normal-text run (m:nor). Word shows it
    upright in the text font, as it shows an m:sty p run; LibreOffice's
    formula import quotes an m:nor run as literal text, whereas it reads an
    m:sty p run as formula source, so that the word "or" became the
    logical-or sign there."""
    return (f'<m:r><m:rPr><m:nor/></m:rPr>'
            f'<m:t xml:space="preserve">{xml_escape(text)}</m:t></m:r>')


def emitter(upright):
    """OMML run builder for a run's upright flag: False italic math (eqn.r),
    True upright math (eqn.nor), "text" normal text (text_run)."""
    if upright == "text":
        return text_run
    return nor if upright else r


def seq(items):
    return Node("seq", items)


def width(n):
    """Estimated width in em of a node at display size."""
    k = n.kind
    if k == "run":
        t = n.args[0]
        return sum(0.25 if ch == " " else 0.0 if ch == ZWSP else 0.5
                   for ch in t)
    if k == "seq":
        return sum(width(c) for c in n.args[0]) + spacing_width(n.args[0])
    if k in ("sub", "sup"):
        return width(n.args[0]) + 0.7 * width(n.args[1])
    if k == "subsup":
        return width(n.args[0]) + 0.7 * max(width(n.args[1]),
                                             width(n.args[2]))
    if k == "pre":
        return width(n.args[0]) + 0.7 * max(width(n.args[1]),
                                             width(n.args[2]))
    if k == "hat":
        return width(n.args[0])
    if k == "frac":
        return max(width(n.args[0]), width(n.args[1])) + 0.3
    if k == "rad":
        return width(n.args[0]) + 1.0
    if k == "delim":
        return width(n.args[0]) + 0.8
    if k == "mat":
        rows = n.args[0]
        ncol = max(len(rw) for rw in rows)
        cols = [max(width(rw[j]) if j < len(rw) else 0 for rw in rows)
                for j in range(ncol)]
        return sum(cols) + (ncol - 1) * 1.0 + 0.8
    if k == "arr":
        return max(width(x) for x in n.args[0])
    raise AssertionError(k)


def spacing_width(items):
    w = 0.0
    for i, c in enumerate(items):
        if c.kind == "run" and c.kw["cls"] in ("bin", "rel") and \
                not is_unary(items, i):
            w += 0.5
    return w


def is_unary(items, i):
    """A + or - is unary when nothing that can end an operand precedes it."""
    c = items[i]
    if c.kind != "run" or c.kw["cls"] != "bin" or c.args[0] not in ("+", MINUS):
        return False
    j = i - 1
    while j >= 0 and items[j].kind == "run" and items[j].kw["cls"] == "space":
        j -= 1
    if j < 0:
        return True
    p = items[j]
    return p.kind == "run" and p.kw["cls"] in ("bin", "rel", "open", "punct",
                                                "dot")


def xml(n):
    k = n.kind
    if k == "run":
        return emitter(n.kw["upright"])(n.args[0])
    if k == "seq":
        return seq_xml(n.args[0])
    if k == "sub":
        return sub(xml(n.args[0]), xml(n.args[1]))
    if k == "sup":
        return sup(xml(n.args[0]), xml(n.args[1]))
    if k == "subsup":
        return subsup(xml(n.args[0]), xml(n.args[1]), xml(n.args[2]))
    if k == "pre":
        base, upper, lower = n.args
        return pre(xml(base), xml(upper) if not empty(upper) else None,
                   xml(lower) if not empty(lower) else None)
    if k == "hat":
        return hat(xml(n.args[0]))
    if k == "frac":
        return frac(xml(n.args[0]), xml(n.args[1]))
    if k == "rad":
        return rad(xml(n.args[0]))
    if k == "delim":
        return d(xml(n.args[0]), n.args[1], n.args[2])
    if k == "mat":
        rows = [[xml(c) for c in rw] for rw in n.args[0]]
        return mat(rows, "(", ")")
    if k == "arr":
        return eqArr(*[xml(x) for x in n.args[0]])
    raise AssertionError(k)


def empty(n):
    return n is None or (n.kind == "seq" and not n.args[0])


def seq_xml(items):
    """Concatenate items, spacing binary operators and relations as the
    thesis builders do (r(" = "), r(" - ")) and merging adjacent runs."""
    out, buf, buf_up = [], [], None

    def flush():
        nonlocal buf, buf_up
        if buf:
            out.append(emitter(buf_up)("".join(buf)))
        buf, buf_up = [], None

    for i, c in enumerate(items):
        if c.kind != "run":
            flush()
            out.append(xml(c))
            continue
        text, up, cls = c.args[0], c.kw["upright"], c.kw["cls"]
        if cls in ("bin", "rel") and not is_unary(items, i):
            text = " " + text + " "
        elif cls == "punct" and text == "," and c.kw.get("space_after"):
            text = ", "
        elif cls == "func" and i + 1 < len(items):
            nxt = items[i + 1]
            if not (nxt.kind == "delim" or (nxt.kind == "run" and
                                            nxt.args[0][:1] in "(" + " ")):
                text = text + " "
        if buf and buf_up != up:
            flush()
        buf_up = up
        buf.append(text)
    flush()
    return "".join(out)


# ---------------------------------------------------------------------------
# LaTeX tokenizer and parser
# ---------------------------------------------------------------------------
TOKEN_RE = re.compile(r"\\\\(?:\[[^\]]*\])?|\\[A-Za-z]+|\\[^A-Za-z]"
                      r"|[0-9]+(?:\.[0-9]+)?|\s+|.", re.S)


class Parser:
    def __init__(self, src):
        self.src = src
        self.toks = TOKEN_RE.findall(src)
        self.i = 0

    # token helpers
    def peek(self, skip_ws=True):
        j = self.i
        while skip_ws and j < len(self.toks) and self.toks[j].isspace():
            j += 1
        return self.toks[j] if j < len(self.toks) else None

    def next(self, skip_ws=True):
        while skip_ws and self.i < len(self.toks) and self.toks[self.i].isspace():
            self.i += 1
        if self.i >= len(self.toks):
            raise ValueError(f"unexpected end of math: {self.src!r}")
        t = self.toks[self.i]
        self.i += 1
        return t

    def expect(self, t):
        got = self.next()
        if got != t:
            raise ValueError(f"expected {t!r}, got {got!r} in {self.src!r}")

    def raw_group(self):
        """The literal text of a {...} argument (for \\mathrm, \\text)."""
        self.expect("{")
        depth, out = 1, []
        while True:
            t = self.next(skip_ws=False)
            if t == "{":
                depth += 1
            elif t == "}":
                depth -= 1
                if depth == 0:
                    break
            elif t.startswith("\\"):
                raise NotImplementedError(f"command {t} inside a text argument "
                                          f"in {self.src!r}")
            out.append(t)
        return "".join(out)

    # grammar
    def parse(self):
        items = self.parse_seq(set())
        if self.peek() is not None:
            raise ValueError(f"trailing {self.peek()!r} in {self.src!r}")
        return seq(items)

    def parse_seq(self, stops):
        items = []
        while True:
            t = self.peek()
            if t is None or t in stops:
                return mixed_intervals(items)
            node = self.parse_atom()
            if node is None:
                continue
            node = self.parse_scripts(node)
            items.append(node)

    def parse_arg(self):
        t = self.peek()
        if t == "{":
            self.next()
            items = self.parse_seq({"}"})
            self.expect("}")
            return seq(items)
        node = self.parse_atom()
        if node is None:
            raise ValueError(f"empty argument in {self.src!r}")
        return node

    def parse_scripts(self, base):
        lower = upper = None
        primes = ""
        while True:
            t = self.peek(skip_ws=False)
            if t == "'":
                self.next(skip_ws=False)
                if lower is None and upper is None and base.kind == "run" \
                        and base.kw["cls"] == "ord":
                    mark = "'" if base.kw["upright"] else PRIME
                    base = run(base.args[0] + mark, base.kw["upright"])
                else:
                    primes += PRIME
                continue
            if t not in ("^", "_"):
                break
            self.next(skip_ws=False)
            if t == "^" and self.peek() == "\\circ":
                self.next()
                if base.kind == "run" and base.kw["cls"] in ("ord", "close"):
                    base = run(base.args[0] + DEG, base.kw["upright"])
                else:
                    base = seq([base, run(DEG)])
                continue
            arg = self.parse_arg()
            if t == "_":
                if lower is not None:
                    raise ValueError(f"double subscript in {self.src!r}")
                lower = arg
            else:
                if upper is not None:
                    raise ValueError(f"double superscript in {self.src!r}")
                upper = arg
        if primes:
            upper = seq([run(primes)] + ([upper] if upper else []))
        if lower is not None and upper is not None:
            return Node("subsup", base, lower, upper)
        if lower is not None:
            return Node("sub", base, lower)
        if upper is not None:
            return Node("sup", base, upper)
        return base

    def parse_leading(self):
        """After an empty group {}: Craig left indices on the next atom."""
        upper = lower = None
        while self.peek(skip_ws=False) in ("^", "_"):
            t = self.next(skip_ws=False)
            if t == "^" and self.peek() == "\\circ":
                self.next()
                if lower is not None or upper is not None:
                    raise NotImplementedError("degree after a left index")
                return run(DEG)
            arg = self.parse_arg()
            if t == "^":
                upper = arg
            else:
                lower = arg
        if upper is None and lower is None:
            return None  # a bare {} is an empty group
        nxt = self.peek()
        if nxt == "(":
            self.next()
            inner = self.parse_seq({")"})
            self.expect(")")
            base = self.parse_scripts(Node("delim", seq(inner), "(", ")"))
        else:
            base = self.parse_atom()
            if base is None:
                raise ValueError(f"left index without a base in {self.src!r}")
            base = self.parse_scripts(base)
        return Node("pre", base, upper or seq([]), lower or seq([]))

    def parse_env(self):
        name = self.raw_group()
        if name not in ("pmatrix", "aligned", "gathered"):
            raise NotImplementedError(f"environment {name}")
        rows, row = [], []
        while True:
            cell = self.parse_seq({"&", "\\end"} | {t for t in self.toks
                                                    if t.startswith("\\\\")})
            row.append(seq(cell))
            t = self.next()
            if t == "&":
                continue
            if t.startswith("\\\\"):
                rows.append(row)
                row = []
                continue
            if t == "\\end":
                if self.raw_group() != name:
                    raise ValueError(f"mismatched \\end in {self.src!r}")
                if any(not empty(c) for c in row):
                    rows.append(row)
                break
        if name == "pmatrix":
            return Node("mat", rows)
        return Node("arr", [seq([c for c in rw]) for rw in rows])

    def parse_atom(self):
        t = self.next()
        if t == "{":
            items = self.parse_seq({"}"})
            self.expect("}")
            if not items and self.peek(skip_ws=False) in ("^", "_"):
                return self.parse_leading()
            return seq(items)
        if t.startswith("\\\\"):
            raise NotImplementedError(f"line break outside an environment "
                                      f"in {self.src!r}")
        if t.startswith("\\"):
            return self.parse_command(t[1:])
        if t[0].isdigit():
            return run(t)
        if t.isalpha():
            return run(t)
        if t == "-":
            return run(MINUS, cls="bin")
        if t == "+":
            return run("+", cls="bin")
        if t in "=<>":
            return run(t, cls="rel")
        if t in "([":
            return run(t, cls="open")
        if t in ")]":
            return run(t, cls="close")
        if t == ",":
            sp = self.i < len(self.toks) and self.toks[self.i].isspace()
            return Node("run", ",", upright=False, cls="punct",
                        space_after=sp)
        if t == "|":
            k = self.i - 2
            while k >= 0 and self.toks[k].isspace():
                k -= 1
            if k >= 0 and self.toks[k] == "\\;":
                return run(MID, cls="rel")
            inner = self.parse_seq({"|"})
            self.expect("|")
            return Node("delim", seq(inner), "|", "|")
        if t in ".;:/*":
            return run(t, cls="punct" if t in ",;:" else "ord")
        raise NotImplementedError(f"character {t!r} in {self.src!r}")

    def parse_command(self, name):
        if name in SPACES:
            text = SPACES[name]
            return run(text, cls="space") if text else None
        if name == "text":
            return run(self.raw_group(), upright="text")
        if name == "mathrm":
            # The star of a Method B frame label (L24*) is followed by a
            # zero-width space: Word shows the plain asterisk, and
            # LibreOffice's formula import reads an operand after it instead
            # of a multiplication with a missing factor (J-016).
            return run(self.raw_group().replace("*", "*" + ZWSP),
                       upright=True)
        if name == "hat":
            return Node("hat", self.parse_arg())
        if name in ("frac", "dfrac"):
            a = self.parse_arg()
            b = self.parse_arg()
            return Node("frac", a, b)
        if name == "sqrt":
            return Node("rad", self.parse_arg())
        if name == "lVert":
            inner = self.parse_seq({"\\rVert"})
            self.expect("\\rVert")
            return Node("delim", seq(inner), DBAR, DBAR)
        if name == "left":
            lch = self.next()
            if lch != "(":
                raise NotImplementedError(f"\\left{lch}")
            inner = self.parse_seq({"\\right"})
            self.expect("\\right")
            rch = self.next()
            if rch != ")":
                raise NotImplementedError(f"\\right{rch}")
            return Node("delim", seq(inner), "(", ")")
        if name == "begin":
            return self.parse_env()
        if name in GREEK:
            return run(GREEK[name])
        if name in SYMBOL:
            text, cls = SYMBOL[name]
            return run(text, cls=cls)
        if name in FUNCS:
            return run(name, upright=True, cls="func")
        if name == "{":
            return run("{", cls="open")
        if name == "}":
            return run("}", cls="close")
        raise NotImplementedError(f"LaTeX command \\{name}")


def mixed_intervals(items):
    """A half-open interval such as (-180 deg, 180 deg] becomes an m:d with
    those two delimiters; matched (..) and [..] stay plain runs, as typed.
    LibreOffice's formula import cannot read a lone ] in a run (J-016)."""
    while True:
        stack, hit = [], None
        for k, c in enumerate(items):
            if c.kind != "run":
                continue
            if c.kw["cls"] == "open" and c.args[0] in "([":
                stack.append(k)
            elif c.kw["cls"] == "close" and c.args[0] in ")]" and stack:
                o = stack.pop()
                if {"(": ")", "[": "]"}[items[o].args[0]] != c.args[0]:
                    hit = (o, k)
                    break
        if hit is None:
            return items
        o, k = hit
        node = Node("delim", seq(items[o + 1:k]), items[o].args[0],
                    items[k].args[0])
        items = items[:o] + [node] + items[k + 1:]


def parse_math(src):
    return Parser(src).parse()


# ---------------------------------------------------------------------------
# Display line breaking
# ---------------------------------------------------------------------------
def break_line(items):
    """Split one top-level item list into lines that fit the column."""
    if width(seq(items)) <= DISPLAY_LIMIT_EM:
        return [items]
    # segments start at a top-level relation or after a \qquad space
    segs, cur = [], []
    for c in items:
        is_rel = c.kind == "run" and c.kw["cls"] == "rel"
        is_gap = c.kind == "run" and c.kw["cls"] == "space" and \
            len(c.args[0]) >= 8
        if is_rel and cur:
            segs.append(cur)
            cur = []
        cur.append(c)
        if is_gap:
            # the gap stays at the end of its segment; strip_space removes
            # it where a line ends there
            segs.append(cur)
            cur = []
    if cur:
        segs.append(cur)
    # A segment that opens after a gap without a relation is the left-hand
    # side of the relation that follows (", \qquad y = ..." in 4.3, 3.4):
    # it is joined to that relation's segment.
    k = 1
    while k < len(segs) - 1:
        head, nxt = segs[k][0], segs[k + 1][0]
        if not (head.kind == "run" and head.kw["cls"] == "rel") and \
                nxt.kind == "run" and nxt.kw["cls"] == "rel":
            segs[k:k + 2] = [segs[k] + segs[k + 1]]
        k += 1
    # In a comma-separated list of equations (2.4, 3.4) the left-hand side
    # after the last top-level comma belongs to the relation that follows,
    # so that a break falls after the comma and never between a left-hand
    # side and its "=". Items move between segments only; the concatenation
    # of the segments is unchanged.
    for k in range(1, len(segs)):
        first = segs[k][0]
        if not (first.kind == "run" and first.kw["cls"] == "rel"):
            continue
        prev = segs[k - 1]
        commas = [j for j, c in enumerate(prev) if c.kind == "run" and
                  c.kw["cls"] == "punct" and c.args[0] == ","]
        if commas and commas[-1] > 0 and strip_space(prev[commas[-1] + 1:]):
            j = commas[-1] + 1
            segs[k - 1], segs[k] = prev[:j], prev[j:] + segs[k]
    # Greedy packing. When a segment does not fit, the line is cut at its
    # last gap (\qquad between two equations, 3.11) if it has one inside,
    # so that each equation of a list starts a line; otherwise at the end.
    def ends_gap(sg):
        c = sg[-1]
        return c.kind == "run" and c.kw["cls"] == "space" and \
            len(c.args[0]) >= 8
    lines, line, cut = [], [], 0
    for s in segs:
        if line and width(seq(line + s)) > DISPLAY_LIMIT_EM:
            if 0 < cut < len(line):
                lines.append(line[:cut])
                line = line[cut:]
            if width(seq(line + s)) > DISPLAY_LIMIT_EM:
                lines.append(line)
                line = []
            cut = 0
        line = line + s
        if ends_gap(s):
            cut = len(line)
    if line:
        lines.append(line)
    # a line still too wide is split before a top-level matrix
    final = []
    for ln in lines:
        if width(seq(ln)) <= DISPLAY_LIMIT_EM:
            final.append(ln)
            continue
        part = []
        for c in ln:
            if part and c.kind == "mat" and \
                    width(seq(part + [c])) > DISPLAY_LIMIT_EM and \
                    any(x.kind == "mat" for x in part):
                final.append(part)
                part = []
            part.append(c)
        final.append(part)
    return [strip_space(ln) for ln in final if ln]


def strip_space(items):
    while items and items[0].kind == "run" and items[0].kw["cls"] == "space":
        items = items[1:]
    while items and items[-1].kind == "run" and items[-1].kw["cls"] == "space":
        items = items[:-1]
    return items


def lead(items):
    """Prefix a zero-width operand when a line opens with a relation or a
    binary operator."""
    if items and items[0].kind == "run" and items[0].kw["cls"] in ("rel", "bin",
                                                                   "dot"):
        return [run(ZWSP)] + list(items)
    return list(items)


def split_at(items, classes, limit):
    """Greedy pieces of at most limit em, cut before top-level runs of the
    given classes (a unary sign is never a cut point)."""
    segs, cur = [], []
    for i, c in enumerate(items):
        cut = c.kind == "run" and c.kw["cls"] in classes and \
            not is_unary(items, i)
        if cut and cur:
            segs.append(cur)
            cur = []
        cur.append(c)
    if cur:
        segs.append(cur)
    pieces, piece = [], []
    for sg in segs:
        if piece and width(seq(piece + sg)) > limit:
            pieces.append(piece)
            piece = []
        piece = piece + sg
    if piece:
        pieces.append(piece)
    return pieces


def split_inline(items):
    if width(seq(items)) <= INLINE_LIMIT_EM:
        return [items]
    out = []
    for pc in split_at(items, ("rel",), INLINE_LIMIT_EM):
        if width(seq(pc)) > INLINE_LIMIT_EM:
            out.extend(split_at(pc, ("bin",), INLINE_LIMIT_EM))
        else:
            out.append(pc)
    return out


def sized(frag, pt):
    """Give every math run of an OMML fragment the font size pt (w:sz in
    the run's w:rPr, after its m:rPr), so a table cell's equations match
    the cell text."""
    tag = f'<w:rPr><w:sz w:val="{2 * pt}"/><w:szCs w:val="{2 * pt}"/></w:rPr>'
    return re.sub(r"<m:r>(<m:rPr>.*?</m:rPr>)?",
                  lambda m: m.group(0) + tag, frag)


def split_cell(items):
    """Inline pieces for a table cell: relations and operators first, then
    after top-level commas."""
    if width(seq(items)) <= CELL_LIMIT_EM:
        return [items]
    out = []
    for pc in split_at(items, ("rel", "bin"), CELL_LIMIT_EM):
        if width(seq(pc)) <= CELL_LIMIT_EM:
            out.append(pc)
            continue
        piece = []
        for c in pc:
            piece.append(c)
            if c.kind == "run" and c.kw["cls"] == "punct" and \
                    c.args[0] == "," and width(seq(piece)) > 0.5 * CELL_LIMIT_EM:
                out.append(piece)
                piece = []
        if piece:
            out.append(piece)
    return out


def layout_display(tree):
    """Return (fragments, n_lines) for a display: lines of an aligned or
    gathered block and over-wide lines are stacked with eqArr."""
    items = tree.args[0]
    if len(items) >= 1 and items[0].kind == "arr" and \
            all(c.kind == "run" and c.kw["cls"] in ("punct", "space")
                for c in items[1:]):
        src_lines = [ln.args[0] for ln in items[0].args[0]]
        tail = items[1:]
        if tail:
            src_lines[-1] = src_lines[-1] + tail
    else:
        src_lines = [items]
    lines = []
    for ln in src_lines:
        if width(seq(ln)) > DISPLAY_LIMIT_EM:
            # A row of an aligned or gathered block is a list of cell
            # sequences (one cell for gathered), which break_line cannot
            # cut; an over-wide row is flattened into its cells' items so
            # that it breaks at its relations like any other line. Rows that
            # fit stay as they were. Without this, rows of (2.2) and (3.1) of
            # KINEMATIC_ANGLES_SHORT.md ran past the right margin (render of
            # 2026-10-08).
            ln = [x for c in ln
                  for x in (c.args[0] if c.kind == "seq" else [c])]
        lines.extend(break_line(ln))
    if len(lines) == 1:
        return seq_xml(lead(lines[0])), 1
    return eqArr(*[seq_xml(lead(ln)) for ln in lines]), len(lines)


# ---------------------------------------------------------------------------
# Markdown reader
# ---------------------------------------------------------------------------
TAG_RE = re.compile(r"\\tag\{([^}]*)\}")
IMG_RE = re.compile(r"^!\[([^\]]*)\]\((figures/[^)]+\.png)\)$")
CAPTION_RE = re.compile(r"^(Figure|Table) \d+\. ")


def read_blocks(lines):
    blocks, i, n = [], 0, len(lines)
    para = []

    def flush_para():
        nonlocal para
        if para:
            text = " ".join(s.strip() for s in para)
            m = CAPTION_RE.match(text)
            blocks.append(("cap", m.group(1), text) if m else ("p", text))
            para = []

    while i < n:
        ln = lines[i]
        s = ln.rstrip("\n")
        if not s.strip():
            flush_para()
            i += 1
            continue
        if s.startswith("```"):
            flush_para()
            j = i + 1
            while not lines[j].startswith("```"):
                j += 1
            blocks.append(("code", [x.rstrip("\n") for x in lines[i + 1:j]]))
            i = j + 1
            continue
        if s.strip() == "$$":
            flush_para()
            j = i + 1
            while lines[j].strip() != "$$":
                if "$$" in lines[j]:
                    raise NotImplementedError(f"line {j + 1}: $$ inside a display")
                j += 1
            body = " ".join(x.strip() for x in lines[i + 1:j])
            tags = TAG_RE.findall(body)
            if len(tags) > 1:
                raise NotImplementedError(f"line {i + 1}: two tags")
            body = TAG_RE.sub(" ", body)
            blocks.append(("eq", body, tags[0] if tags else None, i + 1))
            i = j + 1
            continue
        m = re.match(r"^(#{1,3}) (.*)$", s)
        if m:
            flush_para()
            blocks.append(("h", len(m.group(1)), m.group(2).strip()))
            i += 1
            continue
        if s.startswith("#"):
            raise NotImplementedError(f"line {i + 1}: heading level")
        m = IMG_RE.match(s.strip())
        if m:
            flush_para()
            blocks.append(("img", m.group(2)))
            i += 1
            continue
        if s.startswith("!["):
            raise NotImplementedError(f"line {i + 1}: image form")
        if s.startswith("|"):
            flush_para()
            rows = []
            while i < n and lines[i].startswith("|"):
                rows.append(lines[i].rstrip("\n"))
                i += 1
            blocks.append(("tbl", rows))
            continue
        if s.startswith("- "):
            flush_para()
            item = [s[2:]]
            i += 1
            while i < n and lines[i].startswith("  ") and lines[i].strip():
                item.append(lines[i].strip())
                i += 1
            blocks.append(("bul", " ".join(x.strip() for x in item)))
            continue
        if re.match(r"^(\d+\.|\*|\+|>) ", s) or s.startswith("    "):
            raise NotImplementedError(f"line {i + 1}: unsupported block {s!r}")
        para.append(s)
        i += 1
    flush_para()
    return blocks


def split_cells(row):
    """Split a pipe-table row on | outside $...$."""
    cells, cur, in_math = [], [], False
    for ch in row.strip()[1:-1] if row.strip().endswith("|") else row.strip()[1:]:
        if ch == "$":
            in_math = not in_math
        if ch == "|" and not in_math:
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    cells.append("".join(cur).strip())
    return cells


def inline_parts(text):
    """(kind, value) parts: t text, c code span, m inline math."""
    if text.count("$") % 2:
        raise ValueError(f"unbalanced $ in {text[:80]!r}")
    parts = []
    for k, piece in enumerate(re.split(r"(`[^`]*`)", text)):
        if k % 2:
            parts.append(("c", piece[1:-1]))
            continue
        for j, chunk in enumerate(piece.split("$")):
            if j % 2:
                parts.append(("m", chunk))
            elif chunk:
                parts.append(("t", chunk))
    if any(kind == "t" and "$" in v for kind, v in parts):
        raise ValueError("$ left in text")
    return parts


# ---------------------------------------------------------------------------
# Emitters
# ---------------------------------------------------------------------------
COUNTS = {"display_tagged": 0, "display_untagged": 0, "display_broken": 0,
          "inline": 0, "inline_objects": 0, "tables": 0, "figures": 0, "headings": 0,
          "bullets": 0, "code_blocks": 0, "captions": 0, "paragraphs": 0}


# Punctuation that directly follows an inline equation (",", ".", ";", ":",
# ")") is moved into the end of that equation as a normal-text run
# (text_run), so that no renderer can break the line between the equation
# object and its punctuation. A U+2060 word joiner was tried first;
# LibreOffice still broke before it (orphan "." on page 21 of the 871-line
# build).
TRAILING_PUNCT = ",.;:)"


def fill(p, text, size=None, cell=False):
    parts = inline_parts(text)
    for k, (kind, val) in enumerate(parts):
        if kind == "m":
            tail = ""
            if k + 1 < len(parts) and parts[k + 1][0] == "t":
                nxt = parts[k + 1][1]
                n = len(nxt) - len(nxt.lstrip(TRAILING_PUNCT))
                tail, parts[k + 1] = nxt[:n], ("t", nxt[n:])
            items = parse_math(val).args[0]
            pieces = split_cell(items) if cell else split_inline(items)
            for j, pc in enumerate(pieces):
                frag = seq_xml(lead(pc))
                if tail and j == len(pieces) - 1:
                    frag += text_run(tail)
                add_inline_math(p, sized(frag, TABLE_PT) if cell else frag)
            COUNTS["inline"] += 1
            COUNTS["inline_objects"] += len(pieces)
        elif not val:
            continue
        else:
            rn = p.add_run(val)
            if kind == "c":
                rn.font.name = "Courier New"
                rn._element.get_or_add_rPr().get_or_add_rFonts().set(
                    qn("w:hAnsi"), "Courier New")
            if size:
                rn.font.size = Pt(size)


def cell_inches(text, bold=False):
    """(longest unbreakable piece, whole content) of a cell in inches: text
    at 0.07 in per character (10 pt Times New Roman digits are 5 pt wide),
    an inline equation at its estimated 12 pt width (0.5 em = 1/12 in per
    character), plus 0.16 in of cell padding and margin."""
    # bold header text: 0.085 in per character
    per = 0.085 if bold else 0.07
    longest, total = 0.0, 0.0
    for kind, val in inline_parts(text):
        if kind == "m":
            pieces = split_cell(parse_math(val).args[0])
            ws = [width(seq(pc)) / EM_PER_IN * CELL_SCALE for pc in pieces]
            longest, total = max([longest] + ws), total + sum(ws)
        else:
            for word in val.split():
                longest = max(longest, per * len(word))
            total += per * len(val)
    return longest + 0.16, total + 0.16


NUMBER_RE = re.compile(r"[+-]?\d+(\.\d+)?")


def add_table(doc, rows):
    header = split_cells(rows[0])
    if not re.match(r"^\|(\s*-+\s*\|)+$", rows[1].strip()):
        raise NotImplementedError(f"table separator {rows[1]!r}")
    body = [split_cells(x) for x in rows[2:]]
    allrows = [header] + body
    ncol = len(header)
    if any(len(rw) != ncol for rw in allrows):
        raise ValueError(f"ragged table {header}")
    t = doc.add_table(rows=len(allrows), cols=ncol)
    t.style = "Table Grid"
    t.autofit = False
    # every column at least its longest unbreakable piece; the rest of the
    # text width goes to the columns whose content would otherwise wrap
    # A header may wrap between its words (it is never wider than its longest
    # word), so only the body rows ask for unwrapped width; with the headers
    # counted, Table 8's "Implemented (deg)" and "Right-handed (deg)" took
    # the width that "right shoulder elevation" and "180 deg minus, wrapped"
    # needed, and "out-of-plane" broke at its hyphen.
    mins, prefs = [], []
    for j in range(ncol):
        sizes = [cell_inches(rw[j], bold=(i == 0))
                 for i, rw in enumerate(allrows)]
        mins.append(max(s_[0] for s_ in sizes))
        prefs.append(max([mins[-1]] + [s_[1] for s_ in sizes[1:]]))
    widths = list(mins)
    spare = TEXT_WIDTH_IN - sum(widths)
    if spare < 0:
        # the floors do not fit: shrink them in proportion (a header may wrap)
        widths = [w * TEXT_WIDTH_IN / sum(widths) for w in widths]
        spare = 0.0
    need = [max(0.0, pf - mn) for pf, mn in zip(prefs, mins)]
    if sum(need) > 0:
        give = min(spare, sum(need))
        widths = [w + give * n / sum(need) for w, n in zip(widths, need)]
        spare -= give
    widths = [w + spare * w / sum(widths) for w in widths]
    for i, rw in enumerate(allrows):
        for j, c in enumerate(rw):
            cell = t.cell(i, j)
            cell.width = Inches(widths[j])
            p = cell.paragraphs[0]
            fm.style_paragraph(p._p.get_or_add_pPr(), line=1.0, after=0)
            if NUMBER_RE.fullmatch(c):
                # a numeric cell carries the same minus sign as the equations
                c = c.replace("-", MINUS, 1)
            fill(p, c, size=TABLE_PT, cell=True)
            # every row but the last keeps with the next, so the table stays
            # on one page; the caption above keeps with the table
            if i < len(allrows) - 1:
                p.paragraph_format.keep_with_next = True
            if i == 0:
                for rn in p.runs:
                    rn.font.bold = True
    # the header row repeats on every page a table runs onto, and no row is
    # split across a page break
    for i, row in enumerate(t.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(trPr.makeelement(qn("w:cantSplit"), {}))
        if i == 0:
            trPr.append(trPr.makeelement(qn("w:tblHeader"), {}))
    for col, w in zip(t._tbl.find(qn("w:tblGrid")).findall(qn("w:gridCol")),
                      widths):
        col.set(qn("w:w"), str(round(w * 1440)))
    COUNTS["tables"] += 1


def add_code(doc, code_lines):
    for line in code_lines:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        fm.style_paragraph(p._p.get_or_add_pPr(), line=1.0, after=0)
        rn = p.add_run(line if line else " ")
        rn.font.name = "Courier New"
        rn._element.get_or_add_rPr().get_or_add_rFonts().set(
            qn("w:hAnsi"), "Courier New")
        rn.font.size = Pt(9)
    COUNTS["code_blocks"] += 1


def set_line_1(table):
    for p in table._tbl.iter(qn("w:p")):
        pPr = p.get_or_add_pPr()
        fm.style_paragraph(pPr, line=1.0)


def build():
    lines = SRC.read_text(encoding="ascii").splitlines(keepends=True)
    blocks = read_blocks(lines)
    # Journal convention: a table caption stands above its table. The source
    # writes it after the table, so the two blocks are swapped here.
    for i in range(len(blocks) - 1):
        if blocks[i][0] == "tbl" and blocks[i + 1][:2] == ("cap", "Table"):
            blocks[i], blocks[i + 1] = blocks[i + 1], blocks[i]
    doc = Document()
    fm.apply_house_style(doc)
    images = []
    after_table = False
    prev = ("start",)
    for b in blocks:
        kind = b[0]
        n_par = len(doc.paragraphs)
        if kind == "h":
            doc.add_heading(b[2], level=b[1])
            COUNTS["headings"] += 1
        elif kind == "p":
            fill(doc.add_paragraph(), b[1])
            COUNTS["paragraphs"] += 1
        elif kind == "cap":
            if (b[1] == "Table" and prev[0] == "p" and
                    prev[1].rstrip().endswith((":", "as follows."))):
                # a sentence that cannot stand without the table it
                # introduces stays on the table's page; Table 9's lead-in
                # "... as follows." was left alone at the foot of page 35
                doc.paragraphs[-1].paragraph_format.keep_with_next = True
            p = doc.add_paragraph(
                style="Figure Caption" if b[1] == "Figure" else "Table Caption")
            fill(p, b[2])
            # a caption is never split across pages (Figure 3's ran from
            # page 34 onto page 35); the figure above keeps with it
            p.paragraph_format.keep_together = True
            if b[1] == "Table":
                p.paragraph_format.keep_with_next = True
            COUNTS["captions"] += 1
        elif kind == "bul":
            p = doc.add_paragraph(style="List Bullet")
            fill(p, b[1])
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.first_line_indent = Inches(-0.25)
            p.paragraph_format.space_after = Pt(4)
            COUNTS["bullets"] += 1
        elif kind == "code":
            add_code(doc, b[1])
        elif kind == "tbl":
            add_table(doc, b[1])
            after_table = True
            continue
        elif kind == "img":
            path = SRC.parent / b[1]
            if not path.exists():
                raise FileNotFoundError(path)
            if path.name not in FIG_WIDTH:
                raise NotImplementedError(f"no width set for {path.name}")
            doc.add_picture(str(path), width=Inches(FIG_WIDTH[path.name]))
            p = doc.paragraphs[-1]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True
            fm.style_paragraph(p._p.get_or_add_pPr(), line=1.0, after=4)
            images.append(path.name)
            COUNTS["figures"] += 1
        elif kind == "eq":
            body, tag, lineno = b[1], b[2], b[3]
            try:
                tree = parse_math(body)
            except (NotImplementedError, ValueError) as exc:
                raise type(exc)(f"display at line {lineno}: {exc}") from exc
            frag, nlines = layout_display(tree)
            if nlines > 1 and tree.args[0][0].kind != "arr":
                COUNTS["display_broken"] += 1
            if tag:
                t = add_display_eq(doc, frag, tag, punctuation="")
                set_line_1(t)
                COUNTS["display_tagged"] += 1
            else:
                p = add_display_math(doc, frag, punctuation="")
                fm.style_paragraph(p._p.get_or_add_pPr(), line=1.0)
                COUNTS["display_untagged"] += 1
        else:
            raise AssertionError(kind)
        if after_table and len(doc.paragraphs) > n_par:
            # the paragraph after a table: the space a caption gave before
            # the captions moved above their tables (12 pt, one text line)
            doc.paragraphs[n_par].paragraph_format.space_before = Pt(12)
        after_table = False
        prev = b
    # centred page number in the footer, the thesis's footer helper
    fm._footer_page_number(doc.sections[0])
    set_core_properties(doc, lines)
    doc.save(str(OUT))
    set_page_count()
    return lines, images


# ---------------------------------------------------------------------------
# Document properties
# ---------------------------------------------------------------------------
BYLINE_RE = re.compile(r"^(.+), (\d{1,2}) (January|February|March|April|May|"
                       r"June|July|August|September|October|November|"
                       r"December) (\d{4})\.$")
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def set_core_properties(doc, lines):
    """Title = the "# " heading on line 1; author = fm.AUTHOR (the thesis
    title page), which must open the byline on line 3; created and modified
    = the byline date, so that the build stays deterministic."""
    m_title = re.match(r"^# (.+)$", lines[0].rstrip("\n"))
    m_by = BYLINE_RE.match(lines[2].rstrip("\n"))
    if not m_title or not m_by:
        raise NotImplementedError("line 1 must be '# title' and line 3 "
                                  "'<author>, <day> <Month> <year>.'")
    if m_by.group(1) != fm.AUTHOR:
        raise ValueError(f"byline author {m_by.group(1)!r} is not "
                         f"build_frontmatter.AUTHOR {fm.AUTHOR!r}")
    when = datetime(int(m_by.group(4)), MONTHS.index(m_by.group(3)) + 1,
                    int(m_by.group(2)), 12, 0, 0, tzinfo=timezone.utc)
    cp = doc.core_properties
    cp.title = m_title.group(1).strip()
    cp.author = fm.AUTHOR
    cp.last_modified_by = fm.AUTHOR
    cp.comments = ""
    cp.subject = ""
    cp.revision = 1
    cp.created = when
    cp.modified = when


def set_page_count():
    """Write the page count of the LibreOffice rendering into
    docProps/app.xml (python-docx's template leaves <Pages>1</Pages>).
    LibreOffice (soffice on PATH) converts a copy to PDF in a temporary
    directory with its own profile; the .docx itself is not re-saved by
    LibreOffice, so its OMML stays as built."""
    with tempfile.TemporaryDirectory(prefix="journal-pages-") as tmp:
        profile = Path(tmp, "profile").as_uri()
        subprocess.run(["soffice", f"-env:UserInstallation={profile}",
                        "--headless", "--convert-to", "pdf", "--outdir", tmp,
                        str(OUT)], check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        pdf = Path(tmp, OUT.with_suffix(".pdf").name)
        info = subprocess.run(["pdfinfo", str(pdf)], check=True,
                              capture_output=True, text=True).stdout
    pages = int(re.search(r"^Pages:\s+(\d+)$", info, re.M).group(1))
    with zipfile.ZipFile(OUT) as z:
        items = [(zi, z.read(zi.filename)) for zi in z.infolist()]
    out = []
    for zi, data in items:
        if zi.filename == "docProps/app.xml":
            text = data.decode("utf-8")
            new = re.sub(r"<Pages>\d+</Pages>", f"<Pages>{pages}</Pages>", text)
            if new == text and f"<Pages>{pages}</Pages>" not in text:
                raise ValueError("no <Pages> element in docProps/app.xml")
            data = new.encode("utf-8")
        out.append((zi, data))
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for zi, data in out:
            # fixed entry time (the DOS epoch): python-docx stamps every part
            # with the build time, which made two builds differ
            zi.date_time = (1980, 1, 1, 0, 0, 0)
            z.writestr(zi, data)
    COUNTS["pages"] = pages


# ---------------------------------------------------------------------------
# Self-checks on the saved file
# ---------------------------------------------------------------------------
def check(lines, images):
    results = []
    text = "".join(lines)
    md_displays = sum(1 for ln in lines if ln.strip() == "$$") // 2
    md_tags = len(TAG_RE.findall(text))
    doc = Document(str(OUT))
    body = doc.element.body
    n_omath = len(body.findall(".//" + qn("m:oMath")))
    expected = md_displays + COUNTS["inline_objects"]
    results.append(("display blocks in .md = emitted displays",
                    md_displays == COUNTS["display_tagged"] +
                    COUNTS["display_untagged"],
                    f"{md_displays} vs {COUNTS['display_tagged']} + "
                    f"{COUNTS['display_untagged']}"))
    results.append(("tags in .md = numbered displays",
                    md_tags == COUNTS["display_tagged"],
                    f"{md_tags} vs {COUNTS['display_tagged']}"))
    results.append(("m:oMath count = displays + inline equation objects",
                    n_omath == expected, f"{n_omath} vs {expected}"))
    md_inline = 0
    for ln in re.sub(r"\$\$.*?\$\$", "", text, flags=re.S).splitlines():
        md_inline += ln.count("$")
    # inline spans can cross lines, so count over the joined text instead
    joined = re.sub(r"\$\$.*?\$\$", "", text, flags=re.S)
    md_inline = joined.count("$") // 2
    results.append(("inline $ pairs in .md = inline spans emitted",
                    md_inline == COUNTS["inline"],
                    f"{md_inline} vs {COUNTS['inline']}"))
    bad = re.compile(r"\\[A-Za-z]|\$|\\tag|pmatrix|\{\}\^")
    hits = []
    for el in body.iter(qn("w:t"), qn("m:t")):
        if el.text and bad.search(el.text):
            hits.append(el.text[:60])
    results.append(("no LaTeX source in any run", not hits,
                    f"{len(hits)} hits {hits[:3]}"))
    md_imgs = re.findall(r"!\[[^\]]*\]\((figures/[^)]+)\)", text)
    with zipfile.ZipFile(OUT) as z:
        media = [nm for nm in z.namelist() if nm.startswith("word/media/")]
    results.append(("every referenced figure embedded",
                    len(md_imgs) == len(images) == len(media) and
                    [Path(x).name for x in md_imgs] == images,
                    f"md {len(md_imgs)}, embedded {len(images)}, "
                    f"media {len(media)}"))
    src = Path(__file__).read_bytes()
    results.append(("build_docx.py is ASCII",
                    all(b < 128 for b in src), ""))
    return results, n_omath


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description="Build a journal note from Markdown to Word.")
    ap.add_argument("--src", type=Path, default=SRC,
                    help="Markdown source (default: %(default)s)")
    ap.add_argument("--out", type=Path, default=OUT,
                    help="Word output (default: %(default)s)")
    return ap.parse_args(argv)


def main(argv=None):
    global SRC, OUT
    args = parse_args(argv)
    SRC, OUT = args.src.resolve(), args.out.resolve()
    if SRC == OUT:
        raise ValueError("--src and --out are the same file")
    lines, images = build()
    try:
        print("saved", OUT.relative_to(REPO))
    except ValueError:
        print("saved", OUT)
    for k in ("display_tagged", "display_untagged", "display_broken",
              "inline", "inline_objects", "tables", "figures", "headings", "bullets",
              "code_blocks", "captions", "paragraphs", "pages"):
        print(f"{k}: {COUNTS[k]}")
    results, n_omath = check(lines, images)
    print(f"m:oMath elements: {n_omath}")
    ok = True
    for name, passed, detail in results:
        ok &= passed
        print(f"{'PASS' if passed else 'FAIL'} {name} {detail}".rstrip())
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Banned-pattern sweep over the V7 chapter build scripts' prose.

Checks the string content of the chapter builders against the standing
rules (skill_set/thesis-statement-style.md, thesis-structure-rules.md,
writing/WRITING_SKILL.md): speed values or rate units, question-style
titles, sentence-opening numerals, data-credibility phrases, dashes as
punctuation, internal file names, and the excluded E-020 topic.

Run: python writing/v7/scripts/style_sweep.py   (exit 1 on any hit)
"""
import ast
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILDERS = ([f"build_ch{n}.py" for n in range(1, 10)]
            + ["build_appendix.py", "build_frontmatter.py"])

PATTERNS = [
    ("speed value/unit", re.compile(
        r"\b(cm/s|m/s|mm/s|deg/s|degrees per second|centimetres per second|"
        r"metres per second)\b", re.I)),
    ("question-style title", re.compile(
        r'^"?(Where|What|Why|How|Which|When)\b.*\?"?$')),
    ("rhetorical question mark", re.compile(r"\?(?=[\"']?\s*$|\s)")),
    ("credibility phrase", re.compile(
        r"\b(measured rather than assumed|provably|honest|honestly|"
        r"genuinely|actually|demonstrably)\b", re.I)),
    ("cleft construction", re.compile(
        r"\b(which is (what|why|also why|precisely what|the reason|the point)|"
        r"that is what|is what (makes|keeps|buys|separates)|"
        r"(?:^|[.!?]\s+)What (the|a|an|this|that|each|every|those|these) [^.?]{0,60}? is\b)", re.I)),
    ("em/en dash", re.compile(r"[—–]")),
    ("internal file name", re.compile(
        r"\b[\w/]+\.(py|csv|json|png|bag|docx|md)\b")),
    ("E-020 topic", re.compile(r"\bE-020\b|joint.limit", re.I)),
    ("sentence-opening numeral", re.compile(r"(?:^|[.!?]\s+)\d")),
]


HEADING = re.compile(r"^(Chapter \d|Appendix [A-F]|\d+(\.\d+)*\s+\S)")
LIST_ITEM = re.compile(r"^\d+\.\s")


def strings_of(path):
    src = path.read_text()
    tree = ast.parse(src)
    doc = ast.get_docstring(tree) or ""
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            v = node.value
            if len(v) <= 25 or v in doc or doc.startswith(v[:40]):
                continue
            if " " not in v.strip():          # bare path/filename argument
                continue
            yield node.lineno, v


bad = 0
for name in BUILDERS:
    path = HERE / name
    if not path.exists():
        print(f"[skip] {name} not built yet")
        continue
    for lineno, text in strings_of(path):
        body = text
        if HEADING.match(body):
            continue
        if LIST_ITEM.match(body):
            body = LIST_ITEM.sub("", body)    # keep checking the item's prose
        for label, pat in PATTERNS:
            if label == "sentence-opening numeral":
                # strip legitimate mid-sentence decimals before the check:
                # only flag a digit that starts a sentence
                m = pat.search(body)
            else:
                m = pat.search(body)
            if m:
                print(f"FAIL {name}:{lineno} [{label}] ...{body[max(0, m.start()-40):m.end()+40]}...")
                bad += 1

print("PASS: no banned patterns" if bad == 0 else f"{bad} hits")
sys.exit(1 if bad else 0)

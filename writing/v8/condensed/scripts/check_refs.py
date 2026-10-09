#!/usr/bin/env python3
"""Cross-reference check for the condensed thesis parts.

Dumps every chapter and appendix docx in writing/v8/condensed to text,
collects the items that exist (figure and table captions, numbered
display equations, section headings, appendix headings) and every
reference to them in the prose ("Figure 3.4", "Table 7.2", "equation
(5.7)", "equations (5.8)-(5.12)", "Section 4.2", "Appendix C"), and
prints the references that do not resolve, the items never referenced,
and the caption numbering gaps. Exit code 1 on unresolved references.

Run: python3 writing/v8/condensed/scripts/check_refs.py
"""
import re, sys
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PARTS = ["Chapter_1_Introduction", "Chapter_2_Experimental_Setup",
         "Chapter_3_Kinematic_Modeling", "Chapter_4_Object_Tracking",
         "Chapter_5_Pose_Recovery", "Chapter_6_System_Integration",
         "Chapter_7_Evaluation", "Chapter_8_Real_Time_Feasibility",
         "Chapter_9_Discussion", "Chapter_10_Conclusions_Future_Work", "Appendices"]

def dump(path):
    doc = Document(path); lines = []
    for ch in doc.element.body.iterchildren():
        tag = ch.tag.split('}')[1]
        if tag == 'p':
            txt = ''.join(t.text or '' for t in ch.iter(qn('w:t')))
            mt = ''.join(t.text or '' for t in ch.iter(M + 't'))
            st = ch.find('.//' + qn('w:pStyle'))
            style = st.get(qn('w:val')) if st is not None else ''
            lines.append((style, txt, mt))
        elif tag == 'tbl':
            txt = ' | '.join(''.join(t.text or '' for t in c.iter(qn('w:t'))) for c in ch.iter(qn('w:tc')))
            mt = ''.join(t.text or '' for t in ch.iter(M + 't'))
            lines.append(('table', txt, mt))
    return lines

defined = {"fig": set(), "tab": set(), "eq": set(), "sec": set(), "app": set()}
refs = []   # (part, kind, label, text)
for part in PARTS:
    p = ROOT / f"{part}.docx"
    if not p.exists():
        print("MISSING PART", p.name); continue
    for style, txt, mt in dump(p):
        s = txt.strip()
        m = re.match(r'^(Figure|Table) ([A-Z]?\d*\.\d+)\.', s)
        if m: defined["fig" if m.group(1) == "Figure" else "tab"].add(m.group(2))
        if style.lower().startswith('heading'):
            m = re.match(r'^(\d+\.\d+(?:\.\d+)?)\s', s)
            if m: defined["sec"].add(m.group(1))
            m = re.match(r'^Appendix ([A-Z])\b', s)
            if m: defined["app"].add(m.group(1))
        # numbered display equations are two-cell tables whose last cell
        # is the number; some builders put the number in the paragraph
        for n in re.findall(r'\((\d+\.\d+)\)\s*$', txt.strip()):
            defined["eq"].add(n)
        if style == 'table':
            for n in re.findall(r'\((\d+\.\d+)\)', txt):
                if re.search(r'\|\s*\(%s\)\s*$' % re.escape(n), txt): defined["eq"].add(n)
        body = txt if style != 'table' else ''
        if style == 'table':
            continue
        for n in re.findall(r'\bFigure ([A-Z]?\d*\.\d+)', body): refs.append((part, "fig", n, s[:70]))
        for n in re.findall(r'\bTable ([A-Z]?\d*\.\d+)', body): refs.append((part, "tab", n, s[:70]))
        for n in re.findall(r'[Ee]quations? \((\d+\.\d+)\)', body): refs.append((part, "eq", n, s[:70]))
        for a, b in re.findall(r'[Ee]quations \((\d+\.\d+)\)(?: to | and |-|, )\((\d+\.\d+)\)', body):
            refs.append((part, "eq", b, s[:70]))
        for n in re.findall(r'\bSections? (\d+\.\d+(?:\.\d+)?)', body): refs.append((part, "sec", n, s[:70]))
        for a, b in re.findall(r'\bSections (\d+\.\d+(?:\.\d+)?) (?:to|and) (\d+\.\d+(?:\.\d+)?)', body):
            refs.append((part, "sec", b, s[:70]))
        for n in re.findall(r'\bAppendix ([A-Z])\b', body): refs.append((part, "app", n, s[:70]))

bad = [r for r in refs if r[2] not in defined[r[1]] and not (r[1] == "fig" and r[3].startswith(f"Figure {r[2]}.")) and not (r[1] == "tab" and r[3].startswith(f"Table {r[2]}."))]
seen = set(); out = []
for r in bad:
    k = (r[0], r[1], r[2])
    if k in seen: continue
    seen.add(k); out.append(r)
print(f"defined: figures {len(defined['fig'])}, tables {len(defined['tab'])}, equations {len(defined['eq'])}, sections {len(defined['sec'])}, appendices {sorted(defined['app'])}")
print(f"references checked: {len(refs)}")
for kind in ("fig", "tab", "eq"):
    by = {}
    for n in defined[kind]:
        c, i = n.split('.'); by.setdefault(c, []).append(int(i))
    for c, idx in sorted(by.items()):
        idx.sort(); gaps = [i for i in range(1, idx[-1] + 1) if i not in idx]
        if gaps: print(f"NUMBERING GAP {kind} chapter {c}: missing {gaps}")
if out:
    print(f"UNRESOLVED ({len(out)}):")
    for part, kind, n, ctx in out: print(f"  {part}: {kind} {n}  <- {ctx}")
else:
    print("UNRESOLVED: none")
unref = {k: sorted(v - {r[2] for r in refs if r[1] == k}) for k, v in defined.items()}
for k in ("fig", "tab", "eq"):
    if unref[k]: print(f"never referenced {k}: {unref[k]}")
sys.exit(1 if out else 0)

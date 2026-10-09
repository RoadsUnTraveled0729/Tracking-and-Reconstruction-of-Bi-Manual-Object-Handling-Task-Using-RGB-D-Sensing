#!/usr/bin/env python3
"""Style sweep over the condensed parts (prose paragraphs only; headings,
captions' leading labels and table cells excluded where noted).

Flags: sentences that start with a numeral, a spelled-out number or an
ordinal (thesis-statement-style); any dash character (em, en, or a
hyphen used as a dash between spaces); internal recording names R5/R6B
and file names in prose; speed or velocity values; E-020; emojis and
decorative Unicode; sentences over 45 words; any number with three
or more decimals, in prose, captions, table cells or Word math
(supervisor round 5, C48: at most two decimals anywhere).

Run: python3 writing/v8/condensed/scripts/check_style.py [part ...]
"""
import re, sys
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
ROOT = Path(__file__).resolve().parent.parent
PARTS = ["Chapter_1_Introduction", "Chapter_2_Experimental_Setup",
         "Chapter_3_Kinematic_Modeling", "Chapter_4_Object_Tracking",
         "Chapter_5_Pose_Recovery", "Chapter_6_System_Integration",
         "Chapter_7_Evaluation", "Chapter_8_Real_Time_Feasibility",
         "Chapter_9_Discussion", "Chapter_10_Conclusions_Future_Work", "Appendices",
         "FrontMatter_V8_Condensed"]
NUMWORDS = r"(?:One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Eleven|Twelve|Twenty|Thirty|Fifty|Hundred|First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth)\b"
total = 0
for part in (sys.argv[1:] or PARTS):
    p = ROOT / f"{part}.docx"
    if not p.exists(): print("MISSING", p.name); continue
    doc = Document(p); hits = []
    for i, para in enumerate(doc.element.body.iterchildren()):
        if para.tag.split('}')[1] != 'p': continue
        st = para.find('.//' + qn('w:pStyle')); style = (st.get(qn('w:val')) if st is not None else '') or ''
        txt = ''.join(t.text or '' for t in para.iter(qn('w:t'))).strip()
        if not txt or style.lower().startswith('heading') or style.lower() in ('title', 'toc1', 'toc2', 'toc3'): continue
        code = any(rf.get(qn('w:ascii')) == 'Courier New' for rf in para.findall('.//' + qn('w:rFonts')))
        if code: continue
        body = re.sub(r'^(Figure|Table) [A-Z0-9]+\.\d+\.\s*', '', txt)
        for m in re.finditer(r'[—–]|\s-\s', body): hits.append(("dash", txt[:80])); break
        sents = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9(])', body)
        for s in sents:
            s = s.strip()
            if re.match(r'^\(?\d', s) or re.match(r'^' + NUMWORDS, s): hits.append(("number-led", s[:80]))
            if len(s.split()) > 45: hits.append(("long %d words" % len(s.split()), s[:80]))
        for pat, name in [(r'\bR5\b|\bR6[AB]?\b|recording_\d{8}', "internal name"), (r'\bE-0\d\d\b', "decision id"),
                          (r'\d+(\.\d+)?\s*(m/s|cm/s|mm/s|deg/s|degrees per second|metres per second|rad/s)', "speed value"),
                          (r'[\U0001F300-\U0001FAFF☀-➿←-⇿✅❌]', "emoji/decoration")]:
            if re.search(pat, body): hits.append((name, body[:80]))
    # precision (C48): every paragraph anywhere in the part, table cells and
    # Word math included; code-font paragraphs (file listings) excluded.
    # Math runs are joined with a separator so adjacent matrix cells do not
    # read as one number.
    M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
    for para in doc.element.body.iter(qn('w:p')):
        if any(rf.get(qn('w:ascii')) == 'Courier New' for rf in para.findall('.//' + qn('w:rFonts'))): continue
        txt = ' '.join((t.text or '') for t in para.iter() if t.tag in (qn('w:t'), M + 't'))
        for m in re.finditer(r'(?<![\d.])\d+\.\d{3,}', txt): hits.append(("decimals", m.group(0) + "  in: " + txt[:70]))
    print(f"== {part}: {len(hits)} hits"); total += len(hits)
    for kind, ctx in hits: print(f"   {kind}: {ctx}")
sys.exit(1 if total else 0)

#!/usr/bin/env python3
"""Write the manuscript inventory that verify_submission.py checks against.

The inventory is taken from the assembled Thesis_V9.docx with the same
extraction verify_submission.py uses: the token lists of every native
mathematical object, the sha256 of every embedded image, the cell text of
every data table (the glossary table excluded) and the names of any
comment parts. It is regenerated whenever the content legitimately changes
(a rebuilt table, a rewritten chapter), so that the submission check then
verifies formatting-only steps against that content. Run it after the
content build and before render_pdf.py and verify_submission.py.

Run: /home/luo/anaconda3/bin/python writing/v9/scripts/make_submission_baseline.py
"""
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile

from lxml import etree as E

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'audit_evidence/submission_checklist_v9'
DOCX = ROOT / 'Thesis_V9.docx'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'}


def plain(node):
    return ''.join(node.xpath('.//w:t/text()', namespaces=NS))


def main():
    with ZipFile(DOCX) as archive:
        body = E.fromstring(archive.read('word/document.xml')).find('w:body', NS)
        math = [[t.text for t in m.findall('.//m:t', NS)] for m in body.findall('.//m:oMath', NS)]
        media = {n: hashlib.sha256(archive.read(n)).hexdigest()
                 for n in sorted(archive.namelist()) if n.startswith('word/media/')}
        comments = [n for n in archive.namelist() if re.search(r'comments', n)]
    tables = [t for t in body.findall('w:tbl', NS)
              if t.xpath('./w:tblPr/w:tblStyle[@w:val="TableGrid"]', namespaces=NS)]
    data = [[plain(p) for p in table.findall('.//w:p', NS)] for table in tables[1:]]
    baseline = {'docx_sha256': hashlib.sha256(DOCX.read_bytes()).hexdigest(),
                'math_tokens': math, 'media': media, 'data_tables': data,
                'embedded_comments_parts': comments}
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    out = EVIDENCE / 'baseline.json'
    out.write_text(json.dumps(baseline, indent=2) + '\n')
    print(f'wrote {out}: {len(math)} math objects, {len(media)} images, '
          f'{len(data)} data tables, {len(comments)} comment parts')


if __name__ == '__main__':
    main()

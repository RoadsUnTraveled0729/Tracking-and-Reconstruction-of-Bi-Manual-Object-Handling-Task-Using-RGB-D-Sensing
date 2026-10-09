"""Dump the built Chapter 5 docx to numbered plain text for the reviewer."""
import sys
from docx import Document
from docx.oxml.ns import qn
doc = Document(sys.argv[1])
body = doc.element.body
lines = []
for child in body.iterchildren():
    tag = child.tag.split('}')[1]
    if tag == 'p':
        txt = ''.join(t.text or '' for t in child.iter(qn('w:t')))
        mt = child.findall('.//' + '{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath')
        if mt:
            # inline math: replace with [m] markers in order
            out = []
            for node in child.iter():
                if node.tag == qn('w:t'):
                    out.append(node.text or '')
                elif node.tag == '{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath':
                    ts = ''.join(t.text or '' for t in node.iter('{http://schemas.openxmlformats.org/officeDocument/2006/math}t'))
                    out.append('[' + ts + ']')
            txt = ''.join(out)
        if child.findall('.//' + qn('w:drawing')):
            txt = '[FIGURE]'
        if txt.strip():
            lines.append(txt)
    elif tag == 'tbl':
        rows = child.findall('.//' + qn('w:tr'))
        if len(rows) == 1 and len(rows[0].findall('.//' + qn('w:tc'))) == 2:
            cells = rows[0].findall('.//' + qn('w:tc'))
            m = cells[0]
            ts = ''.join(t.text or '' for t in m.iter('{http://schemas.openxmlformats.org/officeDocument/2006/math}t'))
            num = ''.join(t.text or '' for t in cells[1].iter(qn('w:t')))
            lines.append('[MATH] ' + ts + '   ' + num)
        else:
            for rw in rows:
                cells = []
                for tc in rw.findall('.//' + qn('w:tc')):
                    c = ''.join((t.text or '') for t in tc.iter() if t.tag in (qn('w:t'), '{http://schemas.openxmlformats.org/officeDocument/2006/math}t'))
                    cells.append(c)
                lines.append('TABLE | ' + ' | '.join(cells))
for i, l in enumerate(lines, 1):
    print(f"{i:3d}  {l}")

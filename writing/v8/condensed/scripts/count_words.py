"""Word counts per docx: body prose vs captions/tables/headings/equations."""
import sys, re
from docx import Document
from docx.oxml.ns import qn
M='{http://schemas.openxmlformats.org/officeDocument/2006/math}'
def count(path):
    doc=Document(path); body=doc.element.body
    prose=cap=head=tbl=eq=0
    for ch in body.iterchildren():
        tag=ch.tag.split('}')[1]
        if tag=='tbl':
            tbl+=len(''.join(t.text or '' for t in ch.iter(qn('w:t'))).split()); continue
        if tag!='p': continue
        txt=''.join(t.text or '' for t in ch.iter(qn('w:t'))).strip()
        n=len(txt.split())
        st=ch.find('.//'+qn('w:pStyle'))
        style=st.get(qn('w:val')) if st is not None else ''
        if ch.find('.//'+M+'oMathPara') is not None and not txt: eq+=1; continue
        if style.lower().startswith('heading') or style.lower()=='title': head+=n
        elif re.match(r'^(Figure|Table) [A-Z0-9]+\.\d+\.',txt) or style.lower()=='caption': cap+=n
        else: prose+=n
    return prose,cap,head,tbl,eq
if __name__ == "__main__":
  tot=[0]*5
  for p in sys.argv[1:]:
      c=count(p); tot=[a+b for a,b in zip(tot,c)]
      print(f"{p.split('/')[-1]:45s} prose={c[0]:6d} captions={c[1]:5d} headings={c[2]:4d} tables={c[3]:5d} eqs={c[4]:3d}")
  print(f"{'TOTAL':45s} prose={tot[0]:6d} captions={tot[1]:5d} headings={tot[2]:4d} tables={tot[3]:5d} eqs={tot[4]:3d}")

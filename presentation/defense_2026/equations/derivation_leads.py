#!/usr/bin/env python3
"""Write equations/derivation_leads.json: the sentence that introduces each
numbered equation of Chapters 3-7, quoted from the frozen V9 zh/src exports and
compared with the compiled PDF text (round 8, ROUND8_NOTES.md R8-E3).

Run from anywhere: /home/luo/anaconda3/bin/python presentation/defense_2026/equations/derivation_leads.py
With --check the leads are regenerated in memory and compared with the
committed JSON byte for byte (exit 1 and FAIL on any difference); nothing
is written. validate_deck.py runs the --check mode (D-289).
Requires Poppler pdftotext.
"""
import re, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'writing/v9/zh/src'
OUT=ROOT/'presentation/defense_2026/equations/derivation_leads.json'
def norm(s): return re.sub(r'[^a-z0-9]','',s.lower().replace('\u2019',"'"))
FAM=[("3.1-3.6","Camera' and the chain",["3.1","3.2","3.3","3.4","3.5","3.6"]),
     ("3.7-3.12","Torso and root frame",["3.7","3.8","3.9","3.10","3.11","3.12"]),
     ("3.13-3.14","Shoulder and elbow frames",["3.13","3.14"]),
     ("3.15-3.17","Root Euler angles",["3.15","3.16","3.17"]),
     ("3.18-3.23","Shoulder swing and twist",["3.18","3.19","3.20","3.21","3.22","3.23"]),
     ("3.24","Elbow coordinates",["3.24"]),
     ("4.1-4.2","Object pose in World and track cleaning",["4.1","4.2"]),
     ("5.1-5.4","Grasp offset",["5.1","5.2","5.3","5.4"]),
     ("5.5-5.7","Direction memory and wrist target",["5.5","5.6","5.7"]),
     ("5.8-5.12","Elbow circle and prior",["5.8","5.9","5.10","5.11","5.12"]),
     ("6.1-6.3","Mapping into Scene",["6.1","6.2","6.3"]),
     ("6.4-6.5","Rig chain and rest axes",["6.4","6.5"]),
     ("6.6","Gravity and floor",["6.6"]),
     ("7.1-7.6","Evaluation measures",["7.1","7.2","7.3","7.4","7.5","7.6"])]
family={n:f"{name} ({rng})" for rng,name,ns in FAM for n in ns}
# Export equation number -> compiled number. Only Chapter 4 differs (see note).
EXPORT_TO_COMPILED={"4.3":"4.2"}
SKIP_EXPORT={"4.2"}  # export-only numbered inverse anchor; unnumbered inline in the compiled PDF
split=re.compile(r'(?<=[.:,])\s+(?=[A-Z\[])')
out={}
COMPILED={"3.2":("With the origin of B expressed in A as the translation part APBORG, the two combine into the 4 by 4 homogeneous transformation matrix BAT:",37),
          "3.6":("Chaining the three describes the right elbow frame directly in the y-up camera frame,",38),
          "3.17":("The three angles follow from its entries:",45),
          # D-300 (round 9): the export cites the source number [44]; the
          # compiled PDF, PDF page 46, prints [52] (Dobrowolski).
          "3.18":("They separate into swing and twist [52], with the twist innermost:",46)}
MANUAL={"3.24":48,"4.1":55}
# D-292 (build 66, visual review V5): inline-math symbols that the export
# prints without bracket markup, listed per equation in the order they occur
# in source_text. A slide shows each as the omission mark, as it does the
# bracket spans (D-286); validate_deck.py and build_deck.py read the list
# from omission_spans and fail when a span is not found.
VISIBLE_OMISSIONS={"3.22":["L12"],"7.2":["p_i","c","C"],"7.4":["p_i"]}
def k_over(num,entry,notes):
    if num in COMPILED:
        t,p=COMPILED[num]
        entry["compiled_text"]=t
        notes.append(f'the export sentence differs from the compiled thesis; compiled_text is transcribed from the compiled PDF, PDF page {p}, with inline math flattened in the export style, and is the wording to quote on a slide')
    if num in MANUAL:
        entry["compiled_pdf_check"]=f'prose matches the compiled PDF, PDF page {MANUAL[num]}, by manual comparison; pdftotext interleaves the inline math, which defeats the automatic match'
    return False
def build():
  pdf=subprocess.run(['pdftotext','-layout',str(ROOT/'writing/v9/Thesis_V9.pdf'),'-'],check=True,capture_output=True,text=True).stdout.split('\f')
  pdfnorm=norm(' '.join(pdf[34:135]))  # PDF pages 35-135: Chapters 3-9
  out={}
  for f in sorted(SRC.glob('Chapter_[3-7]_*.txt')):
      lines=f.read_text().split('\n')
      for i,l in enumerate(lines):
          m=re.search(r'TABLE \|.*\((\d\.\d+)\)\s*$',l)
          if not m: continue
          exp=m.group(1)
          if exp in SKIP_EXPORT and f.name.startswith('Chapter_4'): continue
          num=EXPORT_TO_COMPILED.get(exp,exp) if f.name.startswith('Chapter_4') else exp
          prev=lines[i-1]; lineno=i  # 1-based line of the preceding paragraph
          body=re.sub(r'^\s*\d+\s\s','',prev)
          # sentence split at ". " before a capital or bracket; keep the last sentence
          sents=re.split(r'(?<=[.!?])\s+(?=[A-Z\[])',body)
          src=sents[-1]
          # repair splits after abbreviations such as "Section 3.1." are not needed: none end a sentence mid-number here
          notes=[]
          text=src
          if '\u200b' in text:
              text=text.replace('\u200b',''); notes.append('zero-width spaces (U+200B) of the export removed')
          stripped=re.sub(r'\[(?!\d+(?:, ?\d+)*\])\s*([^\[\]]*?)\s*\]',r'\1',text)
          if stripped!=text:
              text=stripped
              notes.append('square brackets that delimit inline math removed; the export flattens inline math (frame labels run together), so take those symbols from the compiled PDF, not from this text')
          # compiled PDF check
          segs=[s for s in re.split(r'\[[^\[\]]*\]',src.replace('\u200b','')) if len(norm(s))>=12]
          if norm(text) in pdfnorm: chk='full sentence matches the compiled PDF text'
          elif segs and all(norm(s) in pdfnorm for s in segs): chk='prose outside inline math matches the compiled PDF text'
          else:
              bad=[s.strip() for s in segs if norm(s) not in pdfnorm]
              chk='DIFFERS from the compiled PDF text in: '+' | '.join(bad)
          entry={"file":str(f.relative_to(ROOT)),"line":lineno,"text":text,"source_text":src,
                 "family":family[num],"compiled_pdf_check":chk}
          if exp!=num: notes.append(f'the zh/src export numbers this equation ({exp}); the compiled PDF numbers it ({num}) on PDF page 58')
          if k_over(num,entry,notes): pass
          if num in VISIBLE_OMISSIONS:
              entry["omission_spans"]=VISIBLE_OMISSIONS[num]
              notes.append('omission_spans lists inline-math symbols that the export prints without bracket markup; a slide shows each as the omission mark (D-292)')
          if notes: entry["note"]='; '.join(notes)+'.'
          out['eq_'+num.replace('.','_')]=entry
  keys=sorted(out,key=lambda k:tuple(int(x) for x in k[3:].split('_')))
  res={"_about":{"verified":"2026-09-30","source":"writing/v9/zh/src/Chapter_3..7 exports (frozen V9); each lead is the last sentence of the paragraph immediately before the equation row. 'line' is the 1-based file line of that paragraph (equal to the export's own paragraph number). 'source_text' is the exact export text; 'text' strips only the markup named in 'note'. 'compiled_pdf_check' compares letters and digits with pdftotext output of writing/v9/Thesis_V9.pdf PDF pages 35-135.","numbering":"Compiled numbering. Chapter 4 of the export is stale: its (4.2) inverse-anchor display is unnumbered inline in the compiled PDF and its (4.3) is compiled Eq. 4.2; there is no compiled Eq. 4.3."}}
  for k in keys: res[k]=out[k]
  return res,sum('DIFFERS' in out[k]['compiled_pdf_check'] for k in keys)


if __name__=='__main__':
    res,differ=build()
    text=json.dumps(res,indent=2,ensure_ascii=True)+'\n'
    if '--check' in sys.argv[1:]:
        same=OUT.read_text()==text
        print(('PASS' if same else 'FAIL')+f": {len(res)-1} derivation leads regenerated in memory; committed {OUT.name} "+('matches' if same else 'differs'))
        sys.exit(0 if same else 1)
    OUT.write_text(text)
    print(f"PASS: {len(res)-1} derivation leads written; {differ} differ from the compiled PDF and carry compiled_text.")

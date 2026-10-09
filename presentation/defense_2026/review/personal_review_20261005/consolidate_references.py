from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from PIL import ImageFont
import re,copy,json,hashlib,posixpath
B=Path(__file__).resolve().parent
D=Path('/Users/luolanqing/Desktop/Tracking-and-Reconstruction-of-Bi-Manual-Object-Handling-Task-Using-RGB-D-Sensing/presentation/defense_2026')
O=B/'three_reference_pages';O.mkdir(exist_ok=True)
N={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
EMU=914400
font=ImageFont.truetype('/Users/luolanqing/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/fonts/DejaVuSans.ttf',160)
def lines(text):
 out=['']
 for word in text.split():
  candidate=(out[-1]+' '+word).strip()
  if font.getlength(candidate)>11.35*72*10:out.append(word)
  else:out[-1]=candidate
 return len(out)
def txt(s):return ''.join(s.xpath('.//a:t/text()',namespaces=N))
def textset(s,t):
 ts=s.xpath('.//a:t',namespaces=N);ts[0].text=t
 for node in ts[1:]:node.text=''
def geom(s,y,h):
 x=s.find('p:spPr/a:xfrm',N);x.find('a:off',N).set('y',str(round(y*EMU)));x.find('a:ext',N).set('cy',str(round(h*EMU)))
src=D/'Thesis_Defence_2026_RESTRUCTURED_FIXED.pptx';dest=O/src.name
with ZipFile(src) as zi:
 parts={n:zi.read(n) for n in zi.namelist()};original=dict(parts);refs=[]
 for sn in [42,43,44,78]:
  r=E.fromstring(parts[f'ppt/slides/slide{sn}.xml']);ss=r.findall('p:cSld/p:spTree/p:sp',N)
  for i,s in enumerate(ss):
   if re.fullmatch(r'\[\d+\]',txt(s)):refs.append((txt(s),txt(ss[i+1])))
 assert [x[0] for x in refs]==[f'[{i}]' for i in range(1,24)]
 layout=[]
 for j,(sn,group) in enumerate([(42,refs[:8]),(43,refs[8:16]),(44,refs[16:])],1):
  r=E.fromstring(parts[f'ppt/slides/slide{sn}.xml']);tree=r.find('p:cSld/p:spTree',N)
  allsh=tree.findall('p:sp',N);label=next(s for s in allsh if re.fullmatch(r'\[\d+\]',txt(s)));desc=allsh[allsh.index(label)+1]
  label=copy.deepcopy(label);desc=copy.deepcopy(desc);rule=copy.deepcopy(tree.find('p:cxnSp',N))
  for s in list(tree):
   q=s.find('.//p:cNvPr',N)
   if q is not None and 8<=int(q.get('id'))<=25:tree.remove(s)
  title=next(s for s in tree.findall('p:sp',N) if s.find('.//p:cNvPr',N).get('id')=='2');textset(title,f'References ({j} of 3)')
  heights=[lines(t)*18.88/72+.018 for _,t in group];gap=(5.44-sum(heights))/(len(group)-1);assert gap>.08,(sn,gap)
  y=1.31
  for k,((lab,body),height) in enumerate(zip(group,heights)):
   for template,text,index in [(label,lab,100+3*k),(desc,body,101+3*k)]:
    s=copy.deepcopy(template);q=s.find('.//p:cNvPr',N);q.set('id',str(index));q.set('name',f'Reference {index}');textset(s,text);geom(s,y,height);tree.append(s)
   if k<len(group)-1:
    line=copy.deepcopy(rule);q=line.find('.//p:cNvPr',N);q.set('id',str(102+3*k));q.set('name',f'Reference separator {k+1}');geom(line,y+height+gap/2,0);tree.append(line)
   layout.append({'slide':sn,'reference':lab,'lines':lines(body),'top_in':y,'height_in':height,'following_gap_in':gap});y+=height+gap
  assert y-gap<=6.751
  parts[f'ppt/slides/slide{sn}.xml']=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
 # Remove the added page and its unique notes part from the presentation package.
 pres=E.fromstring(parts['ppt/presentation.xml']);rels=E.fromstring(parts['ppt/_rels/presentation.xml.rels'])
 rel=next(x for x in rels if x.get('Target')=='slides/slide78.xml');rid=rel.get('Id')
 ids=pres.find('p:sldIdLst',N);node=next(x for x in ids if x.get('{'+N['r']+'}id')==rid);sid=node.get('id');ids.remove(node);rels.remove(rel)
 for x in list(pres.xpath('//*[local-name()="sldId" and @id="'+sid+'"]')):x.getparent().remove(x)
 sr=E.fromstring(parts['ppt/slides/_rels/slide78.xml.rels']);note=next(x.get('Target') for x in sr if x.get('Type','').endswith('/notesSlide'));note=posixpath.normpath(posixpath.join('ppt/slides',note))
 removed={'ppt/slides/slide78.xml','ppt/slides/_rels/slide78.xml.rels',note,posixpath.dirname(note)+'/_rels/'+posixpath.basename(note)+'.rels'}
 for f in removed:parts.pop(f)
 parts['ppt/presentation.xml']=E.tostring(pres,xml_declaration=True,encoding='UTF-8',standalone=True);parts['ppt/_rels/presentation.xml.rels']=E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)
 ct=E.fromstring(parts['[Content_Types].xml'])
 for x in list(ct):
  if x.get('PartName','').lstrip('/') in removed:ct.remove(x)
 parts['[Content_Types].xml']=E.tostring(ct,xml_declaration=True,encoding='UTF-8',standalone=True)
 app=E.fromstring(parts['docProps/app.xml'])
 for x in app.iter():
  if E.QName(x).localname=='Slides':x.text='77'
  if E.QName(x).localname=='HiddenSlides':x.text='31'
 parts['docProps/app.xml']=E.tostring(app,xml_declaration=True,encoding='UTF-8',standalone=True)
 with ZipFile(dest,'w') as zo:
  for info in zi.infolist():
   if info.filename in parts:zo.writestr(info,parts[info.filename])
 changed=[n for n in parts if parts[n]!=original[n]]
 for n in zi.namelist():
  if n.startswith('ppt/media/'):assert parts[n]==original[n]
 for sn in range(1,78):
  if sn not in [42,43,44]:assert parts[f'ppt/slides/slide{sn}.xml']==original[f'ppt/slides/slide{sn}.xml']
 for n,b in parts.items():
  if n.endswith('.xml') or n.endswith('.rels'):E.fromstring(b)
  if n.endswith('.rels'):
   base=posixpath.dirname(posixpath.dirname(n))
   for q in E.fromstring(b):
    if q.get('TargetMode')=='External':continue
    target=q.get('Target');resolved=target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(base,target))
    assert resolved in parts,(n,resolved)
 assert len(ids)==77
 # Every animation target still resolves in its slide.
 for sn in range(1,78):
  r=E.fromstring(parts[f'ppt/slides/slide{sn}.xml']);shapeids=set(r.xpath('//p:cNvPr/@id',namespaces=N))
  for target in r.xpath('//@spid'):assert target in shapeids,(sn,target)
 print('PPT: 77 slides, three reference pages, all 23 sources retained; media and other 74 slides identical.')
# Keep the documents synchronized without rewriting styles or pagination settings.
for filename in ['Thesis_Defence_2026_Speaker_Script.docx','Thesis_Defence_2026_Outline_and_QA_Index.docx']:
 with ZipFile(D/filename) as zi,ZipFile(O/filename,'w') as zo:
  for info in zi.infolist():
   data=zi.read(info.filename)
   if info.filename=='word/document.xml':
    r=E.fromstring(data);wn={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    for p in list(r.xpath('//w:p',namespaces=wn)):
     ts=p.xpath('.//w:t',namespaces=wn);t=''.join(x.text or '' for x in ts)
     if t in ['Slide 78 Additional references','On demand. Reference list only; no prepared narration.']:p.getparent().remove(p);continue
     nt=t
     for i in range(1,4):nt=nt.replace(f'References {i} of 4',f'References {i} of 3')
     nt=nt.replace('Slide 78 contains the remaining IEEE references. ','')
     nt=nt.replace('参考文献：42–44 页；其余条目位于隐藏的第 78 页。QA 不计入正文演讲时间。','参考文献：42–44 页。QA 不计入正文演讲时间。')
     if nt!=t:
      ts[0].text=nt
      for x in ts[1:]:x.text=''
    data=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
   zo.writestr(info,data)
audit={'baseline_ppt_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'files':{},'slides':77,'shown':46,'hidden':31,'reference_pages':[42,43,44],'reference_count':23,'changed_ppt_parts':changed,'removed_ppt_parts':sorted(removed),'all_other_slides_and_media_byte_identical':True,'all_xml_and_relationships_valid':True,'animation_targets_valid':True,'native_verified':False,'layout':layout}
for p in O.glob('*'):
 if p.suffix in ['.pptx','.docx']:audit['files'][p.name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
(O/'reference_consolidation_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps(audit['files'],indent=2))

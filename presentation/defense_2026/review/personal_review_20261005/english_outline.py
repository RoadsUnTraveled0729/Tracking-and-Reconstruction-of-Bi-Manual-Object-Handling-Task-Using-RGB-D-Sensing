from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from PIL import Image,ImageDraw,ImageFont
import io,json,hashlib,re
B=Path(__file__).resolve().parent;O=B/'english_delivery';O.mkdir(exist_ok=True)
D=Path('/Users/luolanqing/Desktop/Tracking-and-Reconstruction-of-Bi-Manual-Object-Handling-Task-Using-RGB-D-Sensing/presentation/defense_2026')
font='/Users/luolanqing/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/fonts/DejaVuSans.ttf'
im=Image.new('RGB',(2800,1620),'white');draw=ImageDraw.Draw(im)
rootfont=ImageFont.truetype(font,42);branchfont=ImageFont.truetype(font,40);leaf=ImageFont.truetype(font,41)
branches=[
('1 Motivation and goal',180,[(100,'Current methods: wearables, optical motion capture, vision'),(180,'Goal: low-cost reconstruction with one RGB-D sensor and kinematics'),(260,'Output: upper-body motion and object pose in a shared scene')]),
('2 Offline reconstruction',715,[(400,'System overview: body and object branches, complete data flow'),(490,'Preprocessing: jumps / Hampel; gaps / interpolation; jitter / Butterworth'),(580,'Kinematics: linked model, T-pose, L24 root, shoulder and elbow frames'),(670,'ArUco: first 10 valid detections for static markers; dynamic object tracking'),(760,'Local recovery: direction memory; object support; two-link geometry'),(850,'Without reliable support: hold the last valid angles and retain state labels'),(940,'System integration: shared memory, skipped frames, overwrite and timing'),(1030,'Unity mapping: joint angles; object, table and wall poses')]),
('3 Results and next steps',1360,[(1170,'Results: object accuracy; body accuracy with and without occlusion'),(1260,'Real-time transition: causal replacements; accuracy and latency trade-off'),(1350,'Demonstration: recorded RGB on the left, Unity reconstruction on the right'),(1440,'Limitations: evaluation scope, object path reference and recorded replay'),(1530,'Future work: retain reliable pixels; combine kinematics and Bayesian estimation')])]
spine=310;branchx=360;join=970;leafx=1030;color='#888888'
draw.line((spine,180,spine,1360),fill=color,width=4)
draw.multiline_text((5,645),'Bimanual\ntracking and\nreconstruction',font=rootfont,fill='black',spacing=12)
draw.line((294,735,spine,735),fill=color,width=4)
for label,y,children in branches:
 width=draw.textlength(label,font=branchfont);assert branchx+width+25<join,(label,width)
 draw.line((spine,y,branchx-14,y),fill=color,width=4);draw.text((branchx,y-27),label,font=branchfont,fill='black');draw.line((branchx+width+20,y,join,y),fill=color,width=4)
 draw.line((join,children[0][0],join,children[-1][0]),fill=color,width=4)
 for cy,t in children:
  assert draw.textlength(t,font=leaf)<2800-leafx-10,(t,draw.textlength(t,font=leaf))
  draw.line((join,cy,leafx-15,cy),fill=color,width=4);draw.text((leafx,cy-26),t,font=leaf,fill='black')
buf=io.BytesIO();im.save(buf,format='PNG')
texts=[
'Defence outline',
'Slides 1-46. Three blocks, from overview to detail. Planned duration: 26 minutes, plus 1 minute of reserve.',
'QA index',
'Find topics by slide number. Hidden slides 47-77 contain 31 QA pages, starting with coordinate transforms and handedness.',
'Topic','Slides','Key points',
'Coordinate transforms','47','Rotation and origin; inverse transforms; chained transforms',
'Left- and right-handed body models','48','8 input points; 5 output rotations; comparison of the two workflows',
'ArUco and AprilTag','49-50','Published comparisons; corner error; detection time',
'Data transfer and frame packets','51-52','Shared memory, TCP and UDP; measurement scope',
'Filtering methods','53-57','Savitzky-Golay, median, Butterworth and One Euro',
'Body kinematics','58-65','Camera and chain frames; root; shoulder swing and twist; elbow frame',
'Object pose','66','Camera to World; pose composition; sample acceptance',
'Occlusion recovery','67-70','Grasp offset; direction memory; wrist targets; sphere-intersection circle',
'Unity mapping and scene calibration','71-74','Axis conversion; rig and rest axes; gravity and floor',
'Evaluation metrics','75-76','Length error; scatter around a line; joint positions and reference data',
'Real-time pipeline logs','77','Frame number; processing time and rate; dropped frames; merger ticks',
'References: slides 42-44. QA pages are outside the main presentation time.'
]
src=D/'Thesis_Defence_2026_Outline_and_QA_Index.docx';dst=O/src.name
with ZipFile(src) as zi,ZipFile(dst,'w') as zo:
 for info in zi.infolist():
  data=zi.read(info.filename)
  if info.filename=='word/media/image1.png':data=buf.getvalue()
  if info.filename=='word/document.xml':
   r=E.fromstring(data);paras=[p for p in r.xpath('//*[local-name()="p"]') if p.xpath('.//*[local-name()="t"]')];assert len(paras)==len(texts),(len(paras),len(texts))
   for p,t in zip(paras,texts):
    ts=p.xpath('.//*[local-name()="t"]');ts[0].text=t
    for x in ts[1:]:x.text=''
   for x in r.xpath('//*[local-name()="docPr"]'):x.set('descr','Three-block outline: motivation and goal, offline reconstruction, and results and next steps.')
   data=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
  if info.filename=='docProps/core.xml':
   r=E.fromstring(data)
   for x in r:
    if E.QName(x).localname=='title':x.text='Defence Outline and QA Index'
   data=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
  zo.writestr(info,data)
with ZipFile(dst) as z:
 for n in ['word/document.xml','docProps/core.xml']:
  assert not re.search('[\u4e00-\u9fff]',z.read(n).decode()),n
print(dst)
print(hashlib.sha256(dst.read_bytes()).hexdigest())

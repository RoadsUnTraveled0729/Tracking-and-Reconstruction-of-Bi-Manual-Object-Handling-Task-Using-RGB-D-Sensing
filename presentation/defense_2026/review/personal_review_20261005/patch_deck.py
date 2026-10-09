from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from copy import deepcopy
from lxml import etree as E
import json,re,hashlib

B=Path(__file__).resolve().parent; W=B.parents[1]
SRC=W/'outputs/Thesis_Defence_2026_RESTRUCTURED_FIXED.pptx'
N={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
R='http://schemas.openxmlformats.org/package/2006/relationships'; CT='http://schemas.openxmlformats.org/package/2006/content-types'
EMU=914400
with ZipFile(SRC)as z:data={i.filename:z.read(i.filename) for i in z.infolist()}
original=dict(data)
def read(part):return E.fromstring(data[part])
def save(part,r):data[part]=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
def sid(s):
 q=s.find('.//p:cNvPr',N);return int(q.get('id')) if q is not None else -1
def shapes(r):return r.find('p:cSld/p:spTree',N)
def replace_shape_text(r,id,txt):
 s=next(s for s in shapes(r) if sid(s)==id);ts=s.findall('.//a:t',N)
 assert ts,(id,txt);ts[0].text=txt
 for t in ts[1:]:t.text=''
def setbox(s,x=None,y=None,w=None,h=None):
 q=s.find('.//a:xfrm',N)
 if q is None:return
 off=q.find('a:off',N);ext=q.find('a:ext',N)
 for k,v in [('x',x),('y',y)]:
  if v is not None:off.set(k,str(round(v*EMU)))
 for k,v in [('cx',w),('cy',h)]:
  if v is not None:ext.set(k,str(round(v*EMU)))
def box(s):
 q=s.find('.//a:xfrm',N)
 if q is None:return None
 o=q.find('a:off',N);e=q.find('a:ext',N)
 return [float(o.get('x'))/EMU,float(o.get('y'))/EMU,float(e.get('cx'))/EMU,float(e.get('cy'))/EMU]
def transform_zone(r,ids,src,dest):
 x0,y0,w0,h0=src;x1,y1,w1,h1=dest
 for s in shapes(r):
  if sid(s)in ids:
   v=box(s)
   if v:setbox(s,x1+(v[0]-x0)*w1/w0,y1+(v[1]-y0)*h1/h0,v[2]*w1/w0,v[3]*h1/h0)

config=json.loads((B/'layout_content.json').read_text());mp=json.loads((B/'balanced_map.json').read_text())
with ZipFile(B/'balanced_elements.pptx') as z:
 for no,idx in mp.items():
  part=f'ppt/slides/slide{no}.xml';r=read(part);tree=shapes(r);num=int(no)
  rem=config.get(no,{}).get('remove',[])
  if num==2:rem=list(range(2,23))
  elif num in [6,11,16,19,31]:
   rem=[sid(s) for s in tree if s.tag==f'{{{N["p"]}}}sp' and (box(s) is None or box(s)[1]<6.7)]
  elif num in [34,36]:rem=list(range(3,9))
  for s in list(tree):
   if sid(s)in rem:tree.remove(s)
  elem=E.fromstring(z.read(f'ppt/slides/slide{idx}.xml'))
  for k,s in enumerate(shapes(elem)):
   if s.tag!=f'{{{N["p"]}}}sp':continue
   s=deepcopy(s);s.find('.//p:cNvPr',N).set('id',str(1000+k));tree.append(s)
  save(part,r)

# Compare approaches in one readable table, without a repeated list beside it.
part='ppt/slides/slide3.xml';r=read(part)
for s in list(shapes(r)):
 if sid(s) in range(3,11):shapes(r).remove(s)
transform_zone(r,set(range(11,36)),[6.22,1.34,6.61,4.91],[.5,1.45,12.33,4.8])
for s in shapes(r):
 if sid(s)==36:setbox(s,.5,6.32,12.33,.38)
save(part,r)

# Broader evidence tables use the available width instead of crowding one half.
for no,start,end in [(34,9,51),(36,9,30)]:
 part=f'ppt/slides/slide{no}.xml';r=read(part)
 transform_zone(r,set(range(start,end+1)),[6.22,1.34,6.61,4.91],[.5,2.35,12.33,3.86])
 cap=52 if no==34 else 31
 for s in shapes(r):
  if sid(s)==cap:setbox(s,.5,6.28,12.33,.44)
 if no==34:
  replace_shape_text(r,11,'Motion / joint');replace_shape_text(r,15,'Object-assisted')
  replace_shape_text(r,52,'Right arm · 45 frames per window · reference: unmasked reconstruction · values in cm')
 else:replace_shape_text(r,31,'The arm geometry is unchanged; future-dependent operations receive causal replacements.')
 save(part,r)

# Concise, full-width limitations table. The detailed explanations remain spoken.
part='ppt/slides/slide39.xml';r=read(part);tree=shapes(r)
for s in list(tree):
 if sid(s)in range(3,11):tree.remove(s)
transform_zone(r,set(range(11,30)),[6.22,1.34,6.61,4.91],[.5,1.55,12.33,4.6])
updates={13:'Scope',14:'Current boundary',16:'Participants and motion',17:'One subject · three slow recordings',19:'Object reference',20:'Endpoint separations · route not registered in World',22:'Body proportions',23:'Landmark-based lengths · 5.9 cm elbow landmark offset',25:'Occlusion recovery',26:'Different outcomes across hands and grip conditions',28:'Online deployment',29:'Recorded replay · live sensor validation pending'}
for k,v in updates.items():replace_shape_text(r,k,v)
for s in tree:
 if sid(s)==30:setbox(s,.5,6.35,12.33,.34)
save(part,r)

# The initial architecture is an overview. The detailed handoff log belongs to p25.
part='ppt/slides/slide5.xml';r=read(part)
for s in list(shapes(r)):
 if sid(s)in range(58,67):shapes(r).remove(s)
save(part,r)

text_updates={
 3:{17:'Gloves and wearables [19]',21:'Bimanual capture datasets [20]',25:'Landmark + depth fusion [21], [22]',29:'Two-hand reconstruction [23]',31:'No object tracking; depth ambiguity',36:'Goal: upper body and handled object in one metric scene'},
 14:{13:'Shoulder swing and twist; straight-arm twist is unobservable [15].'},
 18:{10:'Object pose in the calibrated World frame; ArUco [1].'},
 20:{10:'Landmark validity overlay'},
 23:{70:'Two-link geometry and its application to recorded data.'},
 26:{2:'Shared memory: frame access and dropped frames',354:'Sequence checks and frame selection; schematic timing.'},
 27:{2:'Shared records and time alignment',11:'One frame through the processing and display stages.'},
 29:{12:'Desk-marker reference and final scene axes.'},
 30:{10:'Recorded RGB and Unity replay at the same source frame.'},
 32:{37:'Absolute segment-length error (cm), measured against the tape reference.'},
 33:{31:'Single-hand grips · median distances · right n = 650, left n = 589'},
 36:{1004:'Accuracy and latency'},
 38:{2:'Recorded RGB and causal Unity reconstruction',4:'Matched recorded input · calibrated desk and wall · Unity scene view'},
 40:{18:'Kwok et al. [16] · Dong and Payandeh [17]',19:'Image evidence [16] and Bayesian kinematic estimation [17].'},
 62:{3:'They separate into swing and twist [15], with the twist innermost:'},
 76:{27:'(-1.00, -0.06, 0.00)',30:'(-0.05, 0.85, 0.52)',33:'(-0.03, 0.52, -0.85)',37:'Frame transforms [18]; positions from thesis Table 3.1.'}
}
for no,up in text_updates.items():
 part=f'ppt/slides/slide{no}.xml';r=read(part)
 for k,v in up.items():replace_shape_text(r,k,v)
 save(part,r)

# p23: one synchronized film, recorded RGB above dynamic two-sphere geometry.
# Original media11.mp4 remains embedded; only p23's three media links change.
part='ppt/slides/slide23.xml';r=read(part);tree=shapes(r)
for s in list(tree):
 if sid(s) in list(range(13,34))+[35,36]:tree.remove(s)
replace_shape_text(r,70,'Recorded input and same-frame two-length geometry')
timing=r.find('p:timing',N);lst=timing.find('p:tnLst/p:par/p:cTn/p:childTnLst',N)
for child in list(lst):
 if child.tag!=f'{{{N["p"]}}}video':lst.remove(child)
assert len(lst)==1 and lst[0].find('.//p:spTgt',N).get('spid')=='34'
for old_build_list in timing.findall('p:bldLst',N):timing.remove(old_build_list)
save(part,r)
rr=read('ppt/slides/_rels/slide23.xml.rels')
for q in rr:
 if q.get('Id') in ['rId5','rId6']:q.set('Target','../media/p23_synchronized_geometry.mp4')
 if q.get('Id')=='rId7':q.set('Target','../media/p23_synchronized_geometry.png')
save('ppt/slides/_rels/slide23.xml.rels',rr)
for name in ['p23_synchronized_geometry.mp4','p23_synchronized_geometry.png']:
 data['ppt/media/'+name]=(B/name).read_bytes()

speech={
2:'I will follow three blocks. First, motivation and goal: the current approaches and the reconstruction we want to achieve. Second, the offline reconstruction system: an overview of the architecture, followed by preprocessing, the kinematic model, object tracking, partial occlusion and integration. Third, results and next steps: the evaluation, the move to real-time reconstruction, and the limitations and future directions.',
3:'The methods reviewed in the thesis use several different sensing arrangements. Wearable systems place hardware on the user. Bimanual capture datasets use camera rigs, sometimes together with wearable sensors. The selected RGB-D methods reconstruct a hand or body landmarks, while RGB2Hands reconstructs two interacting hands from monocular video. Our goal is to bring the upper body and a handled object into one metric scene using one RGB-D camera and an explicit kinematic model.',
4:'The goal is a low-cost reconstruction using one Intel RealSense D435, three printed ArUco markers and a connected body model. The output places the person and the cube in one calibrated Unity scene. This clip shows the task: carrying a cube, lifting it onto a rail and handing it from one hand to the other. The handover is one of the recordings used to evaluate the system.',
12:'MediaPipe provides landmark positions. We organise eight of them into a connected model, starting at the right hip, L24, and continuing through the shoulders, elbows and wrists. Each local frame moves with its parent. This lets us apply segment lengths and joint relationships consistently across the chain. The T-pose defines zero for the arm angles and gives a common reference for constructing those frames. The next three pages explain the root, shoulder and elbow levels.',
20:'The six checks are listed on the left. Acquisition validity uses the visibility and depth flags. Segment length detects a departure of more than thirty-five percent from the clean median. Hip–shoulder alignment rejects an angle above twenty-two degrees, and the width-ratio check rejects a departure above twenty percent. Landmark displacement catches a step above five centimetres between usable frames. Finally, grasp plausibility flags a holding wrist more than thirty-five centimetres from the object centre. A flagged arm has its elbow and wrist removed before the solve. The recovery layer then works with the remaining reliable observations.',
31:'The evaluation has three parts. Object reconstruction is compared with tape-measured route lengths. The unoccluded body is checked at both the kinematic-model and avatar stages, with an additional grasp-distance comparison. Occlusion is evaluated through controlled removal and naturally occurring failures.',
34:'This test removes the right elbow and wrist inputs in three forty-five-frame windows with lower, intermediate and higher motion. The shoulder and torso remain available. Each method is compared with the unmasked reconstruction of the same frames. Across the wrist and elbow results, median deviations range from zero point three to two point five centimetres. The table shows how hold-last, direction memory and object assistance respond to each motion window. Their relative performance depends on the joint and the available geometric support.',
36:'The offline system gives us a repeatable basis for evaluation. It can use samples on both sides of a gap and smooth a complete recording before reconstruction. Motion capture and VR applications also need an output while data arrives. The table lists six operations that need future information and their causal replacements. The filters use past samples, the merger bridges short gaps within its delay, and the grasp state updates as observations arrive. The kinematic model stays the same. These changes introduce an accuracy–latency trade-off that the following replay evaluates.',
38:'The left panel shows the recorded RGB, and the right shows the corresponding causal reconstruction in Unity. Each recorded frame is paired with the latest available causal state at that time. The scene uses the calibrated desk and wall references, the pelvis position, thirteen body angles and the tracked object pose. The oblique Unity view makes the relative positions of the person, table and wall visible. The table and wall remain fixed while the person and cube move. This is a reconstruction from recorded input; the previous page reports the original processing-time measurements.',
39:'The evaluation covers one subject and three slow recordings. For the object, the physical reference provides endpoint separations; the route was not registered into the World frame for a point-by-point trajectory comparison. Body dimensions come from landmark tracks and therefore represent effective segment lengths. Recovery outcomes also vary with the hand and grasp conditions. Finally, the causal pipeline was evaluated through recorded replay, so direct live-sensor operation remains to be validated. These boundaries define the next evaluation steps.',
41:'The system reconstructs the upper body and a handled object in one calibrated scene using a single RGB-D camera. Kinematic and object constraints support recovery when observations fail, with explicit states for measured, constrained and held outputs. The causal version processes the recorded input within the frame budget. Together, these results establish a working reconstruction pipeline and a basis for broader evaluation and uncertainty-aware recovery. Thank you.'
}
speech.update({int(k):v for k,v in json.loads((B/'main_speech.json').read_text()).items()})
cues={2:'Indicate the three blocks: motivation and goal, offline reconstruction system, results and next steps.',20:'Follow the three main bullets. Briefly name the six indented checks, then explain rejection and the three output states.',23:'The single film plays automatically: recorded RGB above, same-frame geometry below. Point out the two circular outlines, the amber candidate circle and the selected elbow. The prior is an EMA derived from preceding usable observations for this geometric example, not an archived recovery result.',38:'Play the matched film once. Point out the fixed desk and wall before following the moving cube.'}
cues.update({3:'Compare the sensing arrangements, then indicate the thesis row.',16:'Introduce the fixed scene, static markers and dynamic marker.',31:'Introduce the three evaluation parts before showing their results.',42:'Advance without reading; references remain available for discussion.',43:'Advance without reading.',44:'Advance without reading.',45:'Face the committee.',46:'Open the relevant backup slide when it supports an answer.'})
note_changes={}
for no,new in speech.items():
 part=f'ppt/notesSlides/notesSlide{no}.xml';r=read(part)
 body=next(s for s in r.findall('.//p:sp',N) if s.find('.//p:ph',N) is not None and s.find('.//p:ph',N).get('type')=='body')
 paras=body.findall('p:txBody/a:p',N)
 for para in paras:
  ts=para.findall('.//a:t',N);old=''.join(t.text or '' for t in ts)
  if old.startswith('Sources:') or not old.strip():continue
  if old.startswith('['):
   if no not in cues:continue
   value='['+cues[no]+']'
  else:value=new
  if ts:
   ts[0].text=value
   for t in ts[1:]:t.text=''
   note_changes[old]=value
 save(part,r)
(B/'script_replacements.json').write_text(json.dumps({'speech':speech,'cues':cues,'exact':note_changes},indent=2))

# New introduction references use the deck's own IEEE numbering.
refs={}
for no in [42,43,44]:
 r=read(f'ppt/slides/slide{no}.xml')
 for i in range(6):
  ids=[8+3*i,9+3*i];ss=[next(s for s in shapes(r) if sid(s)==j) for j in ids]
  texts=[''.join(s.xpath('.//a:t/text()',namespaces=N)) for s in ss]
  refs[int(texts[0].strip('[]'))]=texts[1]
refs.update({
19:'C. Diaz and S. Payandeh, "Multimodal sensing interface for haptic interaction," Journal of Sensors, vol. 2017, art. 2072951, pp. 1–24, 2017, doi: 10.1155/2017/2072951.',
20:'X. Zhan et al., "OakInk2: A dataset of bimanual hands-object manipulation in complex task completion," in Proc. IEEE/CVF Conf. Computer Vision and Pattern Recognition (CVPR), 2024.',
21:'Y. Dong and S. Payandeh, "Hand kinematic model construction based on tracking landmarks," Applied Sciences, vol. 15, no. 16, art. 8921, 2025, doi: 10.3390/app15168921.',
22:'S. Dill et al., "Accuracy evaluation of 3D pose reconstruction algorithms through stereo camera information fusion for physical exercises with MediaPipe Pose," Sensors, vol. 24, no. 23, art. 7772, 2024.',
23:'J. Wang et al., "RGB2Hands: Real-time tracking of 3D hand interactions from monocular RGB video," ACM Transactions on Graphics, vol. 39, no. 6, art. 218, pp. 1–16, 2020, doi: 10.1145/3414685.3417852.'})
for key,value in refs.items():
 for full,short in [('Journal of Sensors','J. Sensors'),('Applied Sciences','Appl. Sci.'),('ACM Transactions on Graphics','ACM Trans. Graph.'),('Journal of the American Statistical Association','J. Amer. Stat. Assoc.'),('EURASIP Journal on Advances in Signal Processing','EURASIP J. Adv. Signal Process.'),('IEEE Transactions on Signal Processing','IEEE Trans. Signal Process.'),('Pattern Recognition','Pattern Recognit.'),('Journal of Intelligent Systems and Control','J. Intell. Syst. Control'),('Analytical Chemistry','Anal. Chem.'),('Image and Vision Computing','Image Vis. Comput.'),('Proc. SIGCHI Conf. Human Factors in Computing Systems','Proc. SIGCHI Conf. Hum. Factors Comput. Syst.'),('IEEE/CVF Conf. Computer Vision and Pattern Recognition','IEEE/CVF Conf. Comput. Vis. Pattern Recognit.')]:
  value=value.replace(full,short)
 refs[key]=value
order=[]
pres=read('ppt/presentation.xml');rels=read('ppt/_rels/presentation.xml.rels');relmap={q.get('Id'):q.get('Target') for q in rels}
parts=['ppt/'+relmap[q.get('{'+N['r']+'}id')] for q in pres.find('p:sldIdLst',N)]
for idx,part in enumerate(parts,1):
 if idx in [42,43,44]:continue
 for t in read(part).xpath('.//a:t/text()',namespaces=N):
  for m in re.findall(r'\[(\d+)\]',t):
   k=int(m)
   if k in refs and k not in order:order.append(k)
order += [k for k in refs if k not in order]
refmap={old:i+1 for i,old in enumerate(order)}
def remap(t):return re.sub(r'\[(\d+)\]',lambda m:'['+str(refmap.get(int(m[1]),int(m[1])))+']',t)
for part in list(data):
 if re.match(r'ppt/(?:slides/slide|notesSlides/notesSlide)\d+\.xml$',part):
  r=read(part)
  for t in r.findall('.//a:t',N):
   if t.text:t.text=remap(t.text)
  save(part,r)
for page in range(4):
 no=42+page if page<3 else 78
 r=read('ppt/slides/slide44.xml') if page==3 else read(f'ppt/slides/slide{no}.xml')
 replace_shape_text(r,2,f'References ({page+1} of 4)')
 for i in range(6):
  k=page*6+i
  replace_shape_text(r,8+3*i,'['+str(k+1)+']' if k<len(order) else '')
  replace_shape_text(r,9+3*i,refs[order[k]] if k<len(order) else '')
 for sh in list(shapes(r)):
  if sid(sh) in [3,4,5,6,7]:shapes(r).remove(sh)
 for j in range(6):
  y=1.45+.90*j
  for ident in [8+3*j,9+3*j]:
   sh=next(v for v in shapes(r) if sid(v)==ident);setbox(sh,y=y,h=.80)
  divider=next(v for v in shapes(r) if sid(v)==10+3*j)
  setbox(divider,y=y+.85)
 if page==3:
  r.set('show','0');replace_shape_text(r,27,'78')
  rr=read('ppt/slides/_rels/slide44.xml.rels')
  for q in rr:
   if q.get('Type','').endswith('/notesSlide'):q.set('Target','../notesSlides/notesSlide78.xml')
  save('ppt/slides/_rels/slide78.xml.rels',rr)
  nr=read('ppt/notesSlides/notesSlide44.xml')
  for t in nr.findall('.//a:t',N):t.text=''
  save('ppt/notesSlides/notesSlide78.xml',nr)
  nrr=read('ppt/notesSlides/_rels/notesSlide44.xml.rels')
  for q in nrr:
   if q.get('Type','').endswith('/slide'):q.set('Target','../slides/slide78.xml')
  save('ppt/notesSlides/_rels/notesSlide78.xml.rels',nrr)
  rid='rId'+str(max(int(q.get('Id')[3:]) for q in rels)+1)
  E.SubElement(rels,'{'+R+'}Relationship',Id=rid,Type=N['r']+'/slide',Target='slides/slide78.xml')
  l=pres.find('p:sldIdLst',N);E.SubElement(l,'{'+N['p']+'}sldId',id=str(max(int(q.get('id'))for q in l)+1),attrib={'{'+N['r']+'}id':rid})
  ct=read('[Content_Types].xml')
  for pp,typ in [('slides/slide78.xml','slide'),('notesSlides/notesSlide78.xml','notesSlide')]:E.SubElement(ct,'{'+CT+'}Override',PartName='/ppt/'+pp,ContentType=f'application/vnd.openxmlformats-officedocument.presentationml.{typ}+xml')
  save('[Content_Types].xml',ct)
 save(f'ppt/slides/slide{no}.xml',r)
save('ppt/presentation.xml',pres);save('ppt/_rels/presentation.xml.rels',rels)
app=read('docProps/app.xml')
for node in app:
 if E.QName(node).localname=='Slides':node.text='78'
save('docProps/app.xml',app)
(B/'reference_mapping.json').write_text(json.dumps({'old_to_new':refmap,'ordered_old_numbers':order,'references':refs},indent=2))

# Replace only the explicitly rejected p38 movie and its poster when ready.
for name,path in [('ppt/media/fable_repaired_causal38.mp4',B/'p38_corrected.mp4'),('ppt/media/fable_repaired_causal38.png',B/'p38_corrected.png')]:
 if path.exists():data[name]=path.read_bytes()
out=B/'Thesis_Defence_personal_review_candidate.pptx'
with ZipFile(out,'w',ZIP_DEFLATED)as z:
 for name,blob in data.items():z.writestr(name,blob)
changed=[k for k in data if data[k]!=original.get(k)]
(B/'changed_parts.json').write_text(json.dumps(changed,indent=2))
print(json.dumps({'candidate':str(out),'changed_parts':len(changed),'total_slides':len(parts)+1,'reference_map':refmap},indent=2))

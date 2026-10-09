"""Retain exact-source-frame old/new render comparisons for visual review."""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=HERE/'r5_archived';SOURCE=ROOT/'eval/output/unity_check_r5/side_by_side.mp4';frames=[900,1259,1380,1497,1520,1620]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20);checks=[]
(OUT/'comparisons').mkdir(exist_ok=True)
for f in frames:
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(SOURCE),'-vf',f'select=eq(n\\,{f})','-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-']);old=Image.frombytes('RGB',(1280,506),raw);left=old.crop((0,26,640,506));new=Image.open(OUT/'stills'/f'f{f:05d}.png').convert('RGB').resize((640,480),Image.Resampling.LANCZOS)
 panel=Image.new('RGB',(1280,516),'black');panel.paste(left,(0,36));panel.paste(new,(640,36));d=ImageDraw.Draw(panel);d.text((10,6),f'Archived render | source {f}',font=font,fill='white');d.text((650,6),f'Archived-packet replay + axes | source {f}',font=font,fill='white');p=OUT/'comparisons'/f'compare_f{f:05d}.png';panel.save(p)
 checks.append({'frame':f,'comparison':str(p.relative_to(ROOT)),'comparison_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mean_absolute_channel_difference':float(abs(np.array(left,dtype=float)-np.array(new,dtype=float)).mean())})
report={'status':'VISUAL_REVIEW_REQUIRED','source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'comparisons':checks,'meaning':'Pixel difference is descriptive only: new axes, higher capture resolution and unavailable exact historical renderer prevent a pixel-identity claim. Same source indices are decoded exactly, not nearest-time seeks.'};(OUT/'visual_comparison.json').write_text(json.dumps(report,indent=2)+'\n');print('Prepared six source-matched visual comparisons')

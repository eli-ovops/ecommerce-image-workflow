from pathlib import Path
import json,hashlib
from PIL import Image,ImageOps,ImageDraw
import numpy as np
ROOT=Path('/Volumes/EXTERNAL/电商 作图工作流');O=ROOT/'production/2026-10-24_三维主图试作/model_assets'
S=ROOT/'products/主推花洒/银色/原图/微信图片_20261022184342_89_2.jpg'
im=ImageOps.exif_transpose(Image.open(S)).convert('RGB').resize((1368,1824),Image.Resampling.LANCZOS)
# Source panel perimeter, manually observed in EXIF-upright SIL001; projective planar rectification.
src=[(756,246),(1094,580),(768,912),(435,575)];dst=[(1024,0),(2048,1024),(1024,2048),(0,1024)]
A=[];b=[]
for (x,y),(u,v) in zip(dst,src):A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);b.extend([u,v])
h=np.linalg.solve(np.array(A),np.array(b));tex=im.transform((2048,2048),Image.Transform.PERSPECTIVE,h,Image.Resampling.BICUBIC)
a=np.array(tex);yy,xx=np.mgrid[:2048,:2048];radius=((xx-1024)**2+(yy-1024)**2)**.5
red=(a[:,:,0]>a[:,:,1]*1.5)&(a[:,:,0]>90)&(radius<220);a[red]=[35,36,37]
a[radius>1022]=[28,29,30];Image.fromarray(a).save(O/'face-photo-rectified.png')
# White annuli detected from actual rectified photograph; no regular grid is synthesized.
small=Image.fromarray(a).resize((1024,1024));q=np.array(small);ys,xs=np.mgrid[:1024,:1024];rr=((xs-512)**2+(ys-512)**2)**.5
mask=(q.min(axis=2)>160)&(rr<435)&(rr>70);seen=np.zeros(mask.shape,bool);spots=[]
for y,x in zip(*np.nonzero(mask)):
 if seen[y,x]:continue
 stack=[(int(y),int(x))];seen[y,x]=True;comp=[]
 while stack:
  cy,cx=stack.pop();comp.append((cy,cx))
  for ny,nx in [(cy-1,cx),(cy+1,cx),(cy,cx-1),(cy,cx+1)]:
   if 0<=ny<1024 and 0<=nx<1024 and mask[ny,nx] and not seen[ny,nx]:seen[ny,nx]=True;stack.append((ny,nx))
 if 150<=len(comp)<=1500:
  ar=np.array(comp);cy,cx=ar.mean(axis=0);w=ar[:,1].max()-ar[:,1].min()+1;hh=ar[:,0].max()-ar[:,0].min()+1
  if .6<w/hh<1.6 and 12<w<48 and 12<hh<48:spots.append({'rectified_px':[float(cx*2),float(cy*2)],'plane_mm':[(float(cx)-512)/512*62.6,(512-float(cy))/512*62.6],'radius_mm':float((w+hh)/4/512*62.6),'threshold_area':len(comp)})
ann=tex.copy();d=ImageDraw.Draw(ann)
for z in spots:
 x,y=z['rectified_px'];d.ellipse((x-15,y-15,x+15,y+15),outline=(255,30,20),width=2)
ann.resize((1024,1024)).save(O/'hole-detection-evidence.jpg',quality=95)
record={'source':str(S),'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'source_exif_upright_working_size':[1368,1824],'source_perimeter_points_px':src,'destination_points_px':dst,'inverse_projective_coefficients':h.tolist(),'method':'Actual photograph perspective rectification and white-ring component detection; no random or regularized hole positions','count':len(spots),'holes':spots,'limitations':'Manual perimeter anchors; not calibrated photogrammetry. Outer dark microholes retained from source photo texture. Central red pixels are replaced by gray beneath separate red 3D control.'}
(O/'face-source-and-holes.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print('ACTUAL_WHITE_RING_COMPONENTS',len(spots))

from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont,ImageOps
P=Path(__file__).resolve().parent; R=P.parents[1]
# Photo 3's stored pixels are already landscape. Decode intentionally without EXIF rotation.
im=Image.open(P/'sources/real-3.jpg').convert('RGB')
# Trace only the outside boundary of the photographed housing and the real sleeve.
coords=[]; cur=np.array([22.7,101.])
def line(x,y):
 global cur
 cur=np.array([x,y]);coords.append(cur.tolist())
def curve(a,b,c,d,e,f):
 global cur
 v=cur.copy();p=np.array([a,b]);q=np.array([c,d]);u=np.array([e,f])
 for t in np.linspace(0,1,45)[1:]:coords.append(((1-t)**3*v+3*(1-t)**2*t*p+3*(1-t)*t*t*q+t**3*u).tolist())
 cur=u
line(22.7,101);curve(23,69,45,43,77,40.8);line(609,53.4);curve(638,54,661,73,664.8,103);line(672.4,418)
curve(673,446,657,466,631,474);curve(645,490,661,506,678,525);line(390,525);curve(384,513,376,497,368,484.8)
line(77,491.4);curve(43,491,19,470,18.8,440);line(22.7,101)
w,h=im.size;mask=Image.new('L',im.size);ImageDraw.Draw(mask).polygon([(x*w/700,y*h/525) for x,y in coords],fill=255);mask=mask.filter(ImageFilter.GaussianBlur(1.4))
# Mild colour lift only where the source already contains red-orange. Preserve pin centres.
# Process at 2x delivery resolution for antialiasing.
im=im.resize((2800,2100),Image.Resampling.LANCZOS);mask=mask.resize(im.size,Image.Resampling.LANCZOS)
a=np.asarray(im).astype('float32');r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
red=(r>g*1.42+12)&(r>b*1.45+12)&(g<170)
m=Image.fromarray(np.uint8(red)*255)
# Exclude broad red surfaces (skin/control): enhance only small, isolated coloured marks.
broad=m.filter(ImageFilter.MinFilter(11)).filter(ImageFilter.MaxFilter(23))
t=np.maximum(np.asarray(m,dtype=float)-np.asarray(broad,dtype=float),0)/255
a[:,:,0]=np.minimum(255,r+t*(255-r)*.56);a[:,:,1]=g*(1-.10*t);a[:,:,2]=b*(1-.16*t)
photo=Image.fromarray(a.astype('uint8')).convert('RGBA');photo.putalpha(mask)
# Four outer tangents of the photographed housing -> 1032 x 688 front envelope.
src=np.array([(23.8,39.7),(664,54),(674,478.5),(18,492.5)])*4
dst=np.array([(320,208),(1352,208),(1352,896),(320,896)])
A=[];B=[]
for (x,y),(u,v) in zip(dst,src):
 A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);B.extend([u,v])
co=np.linalg.solve(A,B)
size=(1672,941);fg=photo.transform(size,Image.Transform.PERSPECTIVE,co,Image.Resampling.BICUBIC)
bg=ImageOps.fit(Image.open(R/'production/2026-11-03_顶喷两张细节回源修订/backgrounds/399.png').convert('RGBA'),size)
sh=Image.new('RGBA',size);sh.putalpha(fg.getchannel('A').filter(ImageFilter.GaussianBlur(7)).point(lambda v:round(v*.55)));bg.alpha_composite(sh,(5,8));bg.alpha_composite(fg)
title='提拉除垢设计';font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Songti.ttc',114,index=0);box=font.getbbox(title)
tm=Image.new('L',(box[2]-box[0]+8,box[3]-box[1]+8));ImageDraw.Draw(tm).text((4-box[0],4-box[1]),title,font=font,fill=255,stroke_width=1)
colors=np.linspace([255,238,190],[203,146,64],tm.height).astype('uint8');tile=Image.fromarray(np.tile(colors[:,None,:],(1,tm.width,1))).convert('RGBA');tile.putalpha(tm)
pos=((size[0]-tm.width)//2,34);shadow=Image.new('RGBA',tm.size);shadow.putalpha(tm.filter(ImageFilter.GaussianBlur(2)));bg.alpha_composite(shadow,(pos[0]+3,pos[1]+4));bg.alpha_composite(tile,pos)
bg.convert('RGB').save(P/'提拉除垢设计_实拍孔位版.jpg',quality=98,subsampling=0)
(P/'来源与校正.json').write_text(json.dumps({'face_hand_pins':'real-3.jpg original photo, same projective transform','crosscheck':['real-1.jpg','real-2.jpg'],'nominal_projected_envelope':dst.tolist(),'pin_adjustment':'Local red colour only, original positions and outlines; no synthetic holes or pin dots','hidden_area':'covered by photographed hand, not reconstructed'},ensure_ascii=False,indent=2))

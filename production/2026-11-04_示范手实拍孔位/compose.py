from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageOps
import numpy as np,csv,json
P=Path(__file__).resolve().parent;R=P.parents[1]
ref=Image.open(P/'版式参考.png').convert('RGB'); size=ref.size
face=Image.open(R/'production/2026-10-31_顶喷孔位回源可控修复/372-front-rectified.jpg').convert('RGB')
gray=np.asarray(face.convert('L')).astype(float)
tip=Image.open(R/'production/2026-10-30_长方形拉钮顶喷_完整建模/382-native-detail.jpg').convert('RGB').crop((169,455,214,500))
v=np.asarray(tip).astype(float);tip.putalpha(Image.fromarray(np.uint8(np.clip((v[:,:,0]-v[:,:,1]-12)/65,0,1)*255)))
tip=tip.resize((16,16),Image.Resampling.LANCZOS)
rows=list(csv.DictReader((R/'production/2026-10-31_顶喷孔位回源可控修复/hole-map.csv').open()))
centres=[]
for rec in rows:
 if rec['kind']!='HOLE':continue
 x,y=round(float(rec['photo_rect_x'])),round(float(rec['photo_rect_y']))
 g=gray[y-15:y+16,x-15:x+16];dy,dx=np.mgrid[-15:16,-15:16]
 iy,ix=np.unravel_index(np.argmin(g+.085*(dx**2+dy**2)),g.shape)
 px,py=x+ix-15,y+iy-15
 face.paste(tip,(px-8,py-8),tip);centres.append([rec['id'],int(px),int(py)])
a=np.asarray(ref).astype('int32');r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
skin=(r>g+10)&(g>b+6)&(r>68)
yy,xx=np.mgrid[:size[1],:size[0]];skin&=(xx>760)&(yy<575)
mask=Image.fromarray(skin.astype('uint8')*255).copy();ImageDraw.floodfill(mask,(1100,300),127)
hand=Image.fromarray(np.uint8(np.asarray(mask)==127)*255).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(.55))
panel=Image.new('L',size);ImageDraw.Draw(panel).rounded_rectangle((320,179,1334,837),radius=84,fill=255);panel=panel.filter(ImageFilter.GaussianBlur(1.2))
layer=Image.new('RGB',size);layer.paste(face.resize((1042,695),Image.Resampling.LANCZOS),(302,166))
shadow=Image.new('L',size);shadow.paste(hand,(6,12));shadow=shadow.filter(ImageFilter.GaussianBlur(8))
shade=(.80-.38*np.asarray(shadow)/255)[:,:,None];layer=Image.fromarray(np.uint8(np.clip(np.asarray(layer)*shade,0,255)))
alpha=Image.fromarray(np.uint8(np.asarray(panel,dtype=float)*(1-np.asarray(hand)/255)))
out=Image.composite(layer,ref,alpha);out.save(P/'提拉除垢设计_示范手实拍孔位.jpg',quality=98,subsampling=0)
(P/'孔位记录.json').write_text(json.dumps(dict(mapped_photo_holes=centres,total=len(centres),kind='photo classification, some covered by demonstration hand',face_source='372-front-rectified.jpg',tip_source='382-native-detail.jpg',form='user supplied example, retained outside panel and on hand'),indent=2))

from PIL import Image,ImageOps
import numpy as np,json
from pathlib import Path
p=Path(__file__).parent; im=ImageOps.exif_transpose(Image.open('products/方形三键花洒/实拍原件20261104/照片/微信图片_20261104121549_465_2.jpg')).convert('RGB').resize((1600,1200));a=np.asarray(im); x0,y0=200,380; crop=a[y0:810,x0:690];m=(crop.min(axis=2)>150)&(crop.max(axis=2)-crop.min(axis=2)<65);seen=np.zeros(m.shape,dtype=bool);h,w=m.shape;items=[]
for y in range(h):
 for x in range(w):
  if not m[y,x] or seen[y,x]:continue
  stack=[(y,x)];seen[y,x]=1;pts=[]
  while stack:
   yy,xx=stack.pop();pts.append((yy,xx))
   for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
    ny,nx=yy+dy,xx+dx
    if 0<=ny<h and 0<=nx<w and m[ny,nx] and not seen[ny,nx]:seen[ny,nx]=1;stack.append((ny,nx))
  if 90<=len(pts)<=1000:
   ys=[v[0] for v in pts];xs=[v[1] for v in pts];items.append({'source_x':round(sum(xs)/len(xs)+x0,2),'source_y':round(sum(ys)/len(ys)+y0,2),'pixels':len(pts),'kind':'heart' if len(pts)>600 else 'round'})
items.sort(key=lambda v:(v['source_y'],v['source_x']));(p/'465_白嘴提取.json').write_text(json.dumps({'source':'465','resized_width':1600,'method':'亮度连通域粗提，边缘及分组需对实拍复核，不是实测尺寸','items':items},ensure_ascii=False,indent=2)+'\n');print(len(items),'白嘴，其中',sum(v['kind']=='heart' for v in items),'心形')

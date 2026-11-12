from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,csv,json,hashlib
P=Path(__file__).resolve().parent;src=P.parent/'372-front-rectified.jpg'
im=Image.open(src).convert('RGB');a=np.asarray(im,dtype=float);g=a.mean(2)
smooth=np.asarray(im.convert('L').filter(ImageFilter.BoxBlur(1)),float)
rows=list(csv.DictReader((P.parent/'hole-map.csv').open()));points=[]
for r in rows:
 if r['kind']!='HOLE':continue
 x,y=float(r['photo_rect_x']),float(r['photo_rect_y']);ix,iy=round(x),round(y)
 yy,xx=np.mgrid[iy-16:iy+17,ix-16:ix+17]
 score=smooth[iy-16:iy+17,ix-16:ix+17]+.065*((xx-x)**2+(yy-y)**2)
 k=np.unravel_index(score.argmin(),score.shape);px,py=float(xx[k]),float(yy[k])
 points.append(dict(id=r['id'],row=int(r['row']),x=x,y=y,dx=px-x,dy=py-y))
# Continuous row-wise warp, not circular patching. Only observed hole centers are anchors.
W,H=2400,1600;xs=np.linspace(903-.1474*123/.0202,903+.1474*123/.0202,W)
ys=np.linspace(590.6-.0974*60.7/.0101,590.6+.0974*60.7/.0101,H)
dx=[];dy=[];ry=[]
for row in sorted(set(p['row'] for p in points)):
 q=sorted([p for p in points if p['row']==row],key=lambda p:p['x']);ry.append(q[0]['y'])
 dx.append(np.interp(xs,[p['x'] for p in q],[p['dx'] for p in q]));dy.append(np.interp(xs,[p['x'] for p in q],[p['dy'] for p in q]))
dx=np.asarray(dx);dy=np.asarray(dy);X,Y=np.meshgrid(xs,ys)
for j in range(W):X[:,j]+=np.interp(ys,ry,dx[:,j]);Y[:,j]+=np.interp(ys,ry,dy[:,j])
X=np.clip(X,0,a.shape[1]-2);Y=np.clip(Y,0,a.shape[0]-2);xi=X.astype(int);yi=Y.astype(int);u=(X-xi)[...,None];v=(Y-yi)[...,None]
rgb=(a[yi,xi]*(1-u)*(1-v)+a[yi,xi+1]*u*(1-v)+a[yi+1,xi]*(1-u)*v+a[yi+1,xi+1]*u*v)/255
# Mild neutralization and broad illumination compensation, preserving photographed leaf edges and grain.
lum=rgb.mean(2);low=np.asarray(Image.fromarray(np.uint8(lum*255)).filter(ImageFilter.GaussianBlur(100)),float)/255
gain=np.clip((.38/np.maximum(low,.08))**.45,.75,1.35)
neutral=rgb*.35+lum[...,None]*.65
color=np.clip(neutral*gain[...,None]*.75,0,1)
Image.fromarray(np.uint8(color*255)).save(P/'372-color-registered.png')
rough=np.clip(.55+(lum-low)*.3,.42,.66)
Image.fromarray(np.uint8(rough*255)).save(P/'372-roughness-registered.png')
(P/'texture-method.json').write_text(json.dumps({'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'method':'Original372 photographic RGB and luminance-derived roughness. Continuous row-wise local registration using 96 detected dark centers; mild broad illumination and color cast compensation. No circular masks, no photo height/normal. Photo is not measured albedo or roughness. Blind dot registration interpolated, not independently measured.','anchors':points},indent=2))

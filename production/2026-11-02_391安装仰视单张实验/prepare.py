from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import csv,json,math,shutil,hashlib
P=Path(__file__).resolve().parent;S=P.parent/'2026-10-31_顶喷孔位回源可控修复'
im=Image.open(S/'372-front-rectified.jpg').convert('RGB');pix=im.load();gray=im.convert('L').filter(ImageFilter.BoxBlur(.6));gp=gray.load();pts=[];overlay=im.copy();d=ImageDraw.Draw(overlay)
for a in csv.DictReader((S/'hole-map.csv').open()):
 if a['kind']!='HOLE' or a['id'] in ['R03C06','R13C06']:continue
 x,y=float(a['photo_rect_x']),float(a['photo_rect_y']);q=min(((gp[xx,yy]+.07*((xx-x)**2+(yy-y)**2),xx,yy) for yy in range(round(y)-12,round(y)+13) for xx in range(round(x)-12,round(x)+13)))
 _,xx,yy=q;pts.append(dict(id=a['id'],px=xx,py=yy,x=(xx/im.width-.5)*.3,y=(.5-yy/im.height)*.2));d.ellipse((xx-8,yy-8,xx+8,yy+8),outline='#00ff77',width=2)
# Cover only original knob photograph footprint under the native3D knob, avoiding double knobs.
draw=ImageDraw.Draw(im);draw.ellipse((825,502,979,655),fill=(37,39,40));im.save(P/'single-photo-face.png')
overlay.save(P/'water-origin-overlay.jpg',quality=97);(P/'water-origins.json').write_text(json.dumps(pts,indent=2))
(P/'photo-method.json').write_text(json.dumps(dict(source=str(S/'372-front-rectified.jpg'),sha256=hashlib.sha256((S/'372-front-rectified.jpg').read_bytes()).hexdigest(),single_photo_face=True,geometry_circles_and_leaf_relief_removed=True,knob_photo_mask=[825,502,979,655],knob='Existing3D knob covers masked center; photo lighting remains baked; appearance approximation',water='94 retained photo-classified candidate hole anchors;2 visually uncertain anchors excluded refined to local dark minima; not manufacturer verified; illustrative flow'),indent=2))

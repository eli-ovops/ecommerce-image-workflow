from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter
import numpy as np,json,zipfile,io,xml.etree.ElementTree as ET,hashlib,shutil
ROOT=Path(__file__).resolve().parent;R=ROOT.parents[1];P=ROOT/'completed-five'
for folder in ['JPG','editable','review','sources']:(P/folder).mkdir(parents=True,exist_ok=True)
BG=R/'production/2026-11-03_\u9876\u55b7\u4e24\u5f20\u7ec6\u8282\u56de\u6e90\u4fee\u8ba2/backgrounds/399.png'
PRODUCT=ROOT/'lighting-refine/native/product.png'
original=next((R/'products/\u957f\u65b9\u5f62\u62c9\u94ae\u9876\u55b7/\u539f\u59cb\u5b9e\u62cd20261030').glob('*382*'))
raw=ImageOps.exif_transpose(Image.open(original)).convert('RGB');w,h=raw.size;crop=(round(w*.38),round(h*.40),round(w*.65),round(h*.73));pins=raw.crop(crop);pins.save(P/'sources/382-original-crop.png')
body=Image.open(PRODUCT).convert('RGBA');body=body.crop(body.getchannel('A').getbbox())
fontpath='/System/Library/Fonts/STHeiti Medium.ttc'
records=[]
for n,size,angle,bounds,xy,circle in [(392,(1254,1254),-28,(1000,930),(150,290),(1050,970,150)),(395,(940,1673),-17,(875,1050),(30,450),(750,1360,145))]:
 W,H=size;layers=[]
 layers.append(('Clean blackgold background',ImageOps.fit(Image.open(BG).convert('RGBA'),size)))
 product=Image.new('RGBA',size);rot=body.rotate(angle,Image.Resampling.BICUBIC,expand=True);scale=min(bounds[0]/rot.width,bounds[1]/rot.height);rot=rot.resize(tuple(round(v*scale) for v in rot.size),Image.Resampling.LANCZOS);product.alpha_composite(rot,xy)
 shadow=Image.new('RGBA',size);shadow.putalpha(product.getchannel('A').filter(ImageFilter.GaussianBlur(6)).point(lambda v:round(v*.48)));shift=Image.new('RGBA',size);shift.alpha_composite(shadow,(6,8));layers.extend([('Contact shadow',shift),('Reset product - original372 plus unchanged20mm shell',product)])
 detail=Image.new('RGBA',size);cx,cy,r=circle;photo=ImageOps.fit(pins,(r*2,r*2),Image.Resampling.LANCZOS);mask=Image.new('L',photo.size);ImageDraw.Draw(mask).ellipse((0,0,2*r-1,2*r-1),fill=255);photo.putalpha(mask);detail.alpha_composite(photo,(cx-r,cy-r));dd=ImageDraw.Draw(detail)
 dd.ellipse((cx-r-4,cy-r-4,cx+r+3,cy+r+3),outline='#f9d489',width=5);dd.ellipse((cx-r-8,cy-r-8,cx+r+7,cy+r+7),outline='#7f5425',width=2)
 pill=(48,325,310,390) if n==392 else (48,375,310,438)
 dd.rounded_rectangle(pill,30,fill=(18,17,16,245),outline='#c9a464',width=2)
 dd.line((45,55,45,274 if n==392 else 300),fill='#c9a464',width=2)
 layers.append(('Real382 pulled short-pin detail and reset label capsule',detail))
 text=Image.new('RGBA',size)
 def gold(words,box,italic=False):
  x,y,x2,y2=box;fs=y2-y
  while True:
   f=ImageFont.truetype(fontpath,fs);bb=f.getbbox(words,stroke_width=1);tw=bb[2]-bb[0]+8;th=bb[3]-bb[1]+8
   if tw+th*.16<x2-x and th<y2-y:break
   fs-=1
  m=Image.new('L',(tw+int(th*.17),th));ImageDraw.Draw(m).text((4-bb[0],4-bb[1]),words,font=f,fill=255,stroke_width=1)
  if italic:m=m.transform(m.size,Image.Transform.AFFINE,(1,.16,-th*.16,0,1,0),Image.Resampling.BICUBIC)
  arr=np.zeros((m.height,m.width,4),dtype=np.uint8)
  for yy in range(m.height):
   t=yy/max(1,m.height-1);arr[yy,:,:3]=np.array([255,238,186])*(1-t)+np.array([198,140,60])*t;arr[yy,:,3]=255
  color=Image.fromarray(arr);color.putalpha(m);pos=(x,y+(y2-y-m.height)//2)
  sh=Image.new('RGBA',m.size);sh.putalpha(m.filter(ImageFilter.GaussianBlur(1)));text.alpha_composite(sh,(pos[0]+3,pos[1]+4));text.alpha_composite(color,pos)
 if n==392:
  gold('\u63d0\u62c9\u7ea2\u94ae \u8f85\u52a9\u9664\u57a2',(70,50,1200,170),True);gold('\u5411\u5916\u63d0\u62c9',(70,190,460,250),True);gold('\u8f85\u52a9\u6e05\u7406\u51fa\u6c34\u5b54',(70,250,620,310))
 else:
  gold('\u63d0\u62c9\u7ea2\u94ae \u8f85\u52a9\u9664\u57a2',(70,90,910,200),True);gold('\u5411\u5916\u63d0\u62c9',(70,225,700,285),True);gold('\u8f85\u52a9\u6e05\u7406\u51fa\u6c34\u5b54',(70,292,860,350))
 gold('\u590d\u4f4d\u5916\u89c2',(pill[0]+26,pill[1]+6,pill[2]-10,pill[3]-6),True)
 gold('\u63d0\u62c9\u540e\u77ed\u9488\u5b9e\u62cd',(cx-r-10,cy+r+24,min(W-18,cx+r+17),cy+r+84),True)
 layers.append(('Independent Chinese lettering and explicit state labels',text))
 out=Image.new('RGBA',size)
 for name,im in layers:out.alpha_composite(im)
 D=P/'editable'/str(n);D.mkdir(exist_ok=True);out.save(D/'merged.png');out.convert('RGB').save(P/'JPG'/('%d.jpg'%n),quality=97,subsampling=0)
 root=ET.Element('image',w=str(W),h=str(H));stack=ET.SubElement(root,'stack')
 with zipfile.ZipFile(D/'layers.ora','w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('mimetype','image/openraster')
  for i,(name,im) in reversed(list(enumerate(layers))):
   b=io.BytesIO();im.save(b,format='PNG');src='data/layer%d.png'%i;z.writestr(src,b.getvalue());im.save(D/('layer%d.png'%i));ET.SubElement(stack,'layer',name=name,src=src,x='0',y='0',opacity='1.0',visibility='visible',**{'composite-op':'svg:src-over'})
  z.writestr('stack.xml',ET.tostring(root));b=io.BytesIO();out.save(b,format='PNG');z.writestr('mergedimage.png',b.getvalue())
 old=Image.open(R/'production/2026-11-03_\u9876\u55b7\u4e24\u5f20\u7ec6\u8282\u56de\u6e90\u4fee\u8ba2/JPG'/('%d.jpg'%n)).convert('RGB');pair=Image.new('RGB',(W*2,H));pair.paste(old,(0,0));pair.paste(out,(W,0));pair.thumbnail((1880,1673));pair.save(P/'review'/('%d-before-left-after-right.jpg'%n),quality=96)
 phone=out.convert('RGB');phone.thumbnail((390,700));phone.save(P/'review'/('%d-phone.jpg'%n),quality=95)
 records.append({'id':n,'product_source':str(PRODUCT),'product_state':'reset, no added red pins','angle_ccw':angle,'scale':scale,'xy':xy,'pin_source':str(original),'pin_crop_original_pixels':crop,'labels':['\u590d\u4f4d\u5916\u89c2','\u63d0\u62c9\u540e\u77ed\u9488\u5b9e\u62cd'],'reference':'Original commercial%d: blackgold diagonal large product and circular inset; unsupported claims and exaggerated pins excluded'%n})
(P/'transforms-and-states.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))

# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageChops
import json,zipfile,io,xml.etree.ElementTree as ET,shutil,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
for d in ['JPG','review','editable','sources']:(P/d).mkdir(exist_ok=True)
srcs=[(ROOT/'production/2026-10-30_长方形拉钮顶喷_完整建模/382-native-detail.jpg','short-pin-real.jpg'),(ROOT/'production/2026-11-02_顶喷13张整批返修/assets/connector.jpg','connector-real.jpg')]
for s,n in srcs:shutil.copy2(s,P/'sources'/n)
action=Image.open(P/'sources/short-pin-real.jpg').convert('RGB');conn=Image.open(P/'sources/connector-real.jpg').convert('RGB')
font='/System/Library/Fonts/STHeiti Medium.ttc'
changes={};checks=[]
def ora(path,layers,out):
 root=ET.Element('image',w=str(out.width),h=str(out.height));stack=ET.SubElement(root,'stack')
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('mimetype','image/openraster',compress_type=zipfile.ZIP_STORED)
  for i,(name,im) in enumerate(reversed(layers)):
   f=f'data/{i}.png';b=io.BytesIO();im.save(b,format='PNG');z.writestr(f,b.getvalue());ET.SubElement(stack,'layer',name=name,src=f,x='0',y='0',opacity='1',visibility='visible',**{'composite-op':'svg:src-over'})
  z.writestr('stack.xml',ET.tostring(root));b=io.BytesIO();out.save(b,format='PNG');z.writestr('mergedimage.png',b.getvalue())
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None;r=ET.fromstring(z.read('stack.xml'));im=Image.new('RGBA',out.size)
  for e in reversed(list(r.find('stack'))):im.alpha_composite(Image.open(io.BytesIO(z.read(e.attrib['src']))).convert('RGBA'))
  assert ImageChops.difference(im,out).getbbox() is None
for n in range(387,400):
 native=Image.open(P/f'native/{n}.png').convert('RGBA');layers=[('Original generated raster, not editable objects',native)];updates=[]
 def patch(photo,box,label=None,ellipse=False,radius=0):
  x,y,x2,y2=box;w,h=x2-x,y2-y;part=ImageOps.fit(photo,(w,h),method=Image.Resampling.LANCZOS).convert('RGBA');mask=Image.new('L',(w,h));dr=ImageDraw.Draw(mask)
  if ellipse:dr.ellipse((0,0,w-1,h-1),fill=255)
  else:dr.rounded_rectangle((0,0,w-1,h-1),radius,fill=255)
  part.putalpha(mask);lay=Image.new('RGBA',native.size);lay.alpha_composite(part,(x,y));layers.append(('Actual photo replacement',lay));updates.append(dict(box=list(box),source='382 actual crop' if photo is action else 'actual connector crop',ellipse=ellipse))
  if label:
   lay=Image.new('RGBA',native.size);dd=ImageDraw.Draw(lay);dd.rounded_rectangle((x+7,y+7,x+w-7,y+73),12,fill=(20,16,12,205));dd.text((x+23,y+15),label,font=ImageFont.truetype(font,42),fill='#f8dfad',stroke_width=1);layers.append(('Editable replacement caption '+label,lay))
 if n==387:patch(action,(33,505,394,811),radius=28)
 if n==392:patch(action,(924,779,1231,1086),ellipse=True)
 if n==395:patch(action,(582,1199,891,1514),ellipse=True)
 if n==396:
  patch(conn,(526,628,999,1020),'接头开口',radius=20)
  patch(action,(526,1052,999,1499),'短针细节',radius=20)
 out=Image.new('RGBA',native.size)
 for _,im in layers:out.alpha_composite(im)
 out.convert('RGB').save(P/f'JPG/{n}.jpg',quality=97,subsampling=0)
 if updates:
  d=P/'editable'/str(n);d.mkdir(exist_ok=True);ora(d/'layers.ora',layers,out);(d/'replacements.json').write_text(json.dumps(updates,ensure_ascii=False,indent=2));out.save(d/'merged.png');changes[str(n)]=updates
 # Full reference comparison, preserving aspect and all edges.
 ref=Image.open(ROOT/f'references/2026-10-31_同款商户电商参考/微信图片_20261031133902_{n}_2.jpg').convert('RGB')
 h=1000;a=ImageOps.contain(ref,(1000,h));b=ImageOps.contain(out.convert('RGB'),(1000,h));pair=Image.new('RGB',(a.width+b.width,h),'#ddd');pair.paste(a);pair.paste(b,(a.width,0));pair.save(P/f'review/{n}-reference-left-candidate-right.jpg',quality=96)
 thumb=ImageOps.contain(out.convert('RGB'),(360,640));thumb.save(P/f'review/{n}-mobile.jpg',quality=95)
 checks.append(dict(id=n,size=list(out.size),decode=True,local_replacement=bool(updates),ora_crc_recomposition=bool(updates)))
# Inspectable product crops, exact 2x pixel enlargement. Not an automated geometry test.
boxes={387:(.39,.24,.69,.58),388:(.04,.65,.40,.91),389:(.06,.55,.28,.84),390:(.13,.54,.32,.79),391:(.40,.27,.75,.46),392:(.32,.37,.67,.68),393:(.34,.27,.68,.40),394:(.30,.32,.67,.45),395:(.28,.34,.67,.60),396:(.08,.16,.43,.36),397:(.25,.35,.65,.46),398:(.34,.36,.74,.42),399:(.28,.40,.72,.67)}
for n,bb in boxes.items():
 im=Image.open(P/f'JPG/{n}.jpg');box=tuple(round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(bb));crop=im.crop(box);crop.resize((crop.width*2,crop.height*2),Image.Resampling.NEAREST).save(P/f'review/{n}-face-200pct.jpg',quality=97)
for group,ids,w,h,cols in [('square',range(387,394),400,400,4),('portrait',range(394,400),350,623,3)]:
 sheet=Image.new('RGB',(w*cols,(h+30)*2),'#ddd');d=ImageDraw.Draw(sheet)
 for i,n in enumerate(ids):
  im=ImageOps.contain(Image.open(P/f'JPG/{n}.jpg'),(w,h));x=i%cols*w;y=i//cols*(h+30);d.text((x+7,y+8),str(n),fill='black');sheet.paste(im,(x+(w-im.width)//2,y+30))
 sheet.save(P/f'review/contact-{group}.jpg',quality=96)
(P/'export-verification.json').write_text(json.dumps(dict(checks=checks,replacements=changes,notes='Other nine files are flat generated rasters; no invented editable layers. Native image aspect ratios preserved, no stretch.'),ensure_ascii=False,indent=2))
print(json.dumps(checks))

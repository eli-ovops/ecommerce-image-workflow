from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageOps,ImageChops
import numpy as np, json, shutil, hashlib, zipfile, io, xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent; R=P.parents[1]
OLD=R/'production/2026-11-03_顶喷13张_尺寸单列与卖点修订'
A=R/'production/2026-11-02_顶喷13张整批返修/assets'
S=P/'sources';S.mkdir(exist_ok=True)
for n in ['product372.png','face.jpg']:shutil.copy2(A/n,S/n)
shutil.copy2(R/'production/2026-11-02_顶喷实拍主体黑金实验/transforms.json',S/'original-cutout-provenance.json')
shutil.copy2('/Users/USER/.codex/generated_images/01a18bc9-5492-79e3-bfe3-678a64ea1c26/exec-003812e4-fadb-44a2-b804-38ac29980c24.png',P/'backgrounds/387.png')
shutil.copy2(A/'blackgold.png',P/'backgrounds/399.png')
for n in range(387,400):
 if n not in (387,399):shutil.copy2(OLD/'JPG'/('%d.jpg'%n),P/'JPG'/('%d.jpg'%n))
SERIF='/System/Library/Fonts/Supplemental/Songti.ttc';BOLD='/System/Library/Fonts/STHeiti Medium.ttc'
records=[]
for n,size,angle,bounds,xy in [(387,(1254,1254),87,(610,860),(425,190)),(399,(940,1673),68,(870,1090),(35,525))]:
 W,H=size;D=P/'editable'/str(n);D.mkdir(exist_ok=True)
 layers=[]
 def add(name,im):layers.append((name,im))
 add('Clean background',ImageOps.fit(Image.open(P/'backgrounds'/('%d.png'%n)).convert('RGBA'),size))
 raw=Image.open(S/'product372.png').convert('RGBA');rot=raw.rotate(angle,Image.Resampling.BICUBIC,expand=True)
 scale=min(bounds[0]/rot.width,bounds[1]/rot.height);sz=tuple(round(v*scale) for v in rot.size)
 rot=rot.resize(sz,Image.Resampling.LANCZOS)
 product=Image.new('RGBA',size);product.alpha_composite(rot,xy)
 shadow=Image.new('RGBA',size);shadow.putalpha(product.getchannel('A').filter(ImageFilter.GaussianBlur(13)).point(lambda v:round(v*.65)))
 shifted=Image.new('RGBA',size);shifted.alpha_composite(shadow,(12,17));add('Soft contact shadow',shifted);add('Original372 whole product similarity transform',product)
 decor=Image.new('RGBA',size);dd=ImageDraw.Draw(decor)
 if n==387:
  for box in [(28,195,438,295),(28,320,438,420)]:dd.rounded_rectangle(box,50,fill=(16,17,17,250),outline='#e4bc76',width=3)
  dd.rounded_rectangle((33,540,388,900),42,fill='#141414',outline='#e7c47c',width=3)
  detail=ImageOps.fit(Image.open(S/'product372.png').convert('RGBA').crop((1200,250,2000,880)),(348,275))
  mask=Image.new('L',detail.size);ImageDraw.Draw(mask).rounded_rectangle((0,0,347,320),38,fill=255);detail.putalpha(mask)
  decor.alpha_composite(detail,(37,544));dd=ImageDraw.Draw(decor);dd.line((37,820,385,820),fill='#e7c47c',width=3)
 else:dd.line((49,145,49,365),fill='#c9a360',width=2)
 add('Independent capsules and real photo detail',decor)
 textlayer=Image.new('RGBA',size)
 specs=[('宽幅大面板',(44,210,423,278),BOLD,True),('充沛大水量',(44,335,423,403),BOLD,True),('细密喷面',(47,832,376,887),BOLD,True),('银色顶喷',(355,1120,900,1225),SERIF,False)] if n==387 else [('大面板 大水量',(75,130,870,246),SERIF,False),('舒展沐浴空间',(75,264,835,364),SERIF,False)]
 for text,box,fontpath,italic in specs:
  x,y,x2,y2=box;fs=y2-y
  while True:
   font=ImageFont.truetype(fontpath,fs);bb=font.getbbox(text);tw=bb[2]-bb[0];th=bb[3]-bb[1]
   if tw+(th*.16 if italic else 0)<=x2-x and th<=y2-y:break
   fs-=1
  m=Image.new('L',(tw+5,th+5));ImageDraw.Draw(m).text((-bb[0]+2,-bb[1]+2),text,font=font,fill=255,stroke_width=0)
  if italic:m=m.transform((m.width+int(m.height*.18),m.height),Image.Transform.AFFINE,(1,.18,-m.height*.18,0,1,0),Image.Resampling.BICUBIC)
  colors=np.zeros((m.height,m.width,4),dtype=np.uint8)
  for yy in range(m.height):
   t=yy/max(1,m.height-1);c=np.array((255,238,186))*(1-t)+np.array((196,135,54))*t;colors[yy,:,:3]=c;colors[yy,:,3]=255
  gold=Image.fromarray(colors);gold.putalpha(m);pos=(x+((x2-x)-m.width)//2,y+((y2-y)-m.height)//2)
  sh=Image.new('RGBA',m.size,(0,0,0,0));sh.putalpha(m.filter(ImageFilter.GaussianBlur(1)));textlayer.alpha_composite(sh,(pos[0]+3,pos[1]+4));textlayer.alpha_composite(gold,pos)
 add('Editable independent lettering',textlayer)
 out=Image.new('RGBA',size)
 for name,im in layers:out.alpha_composite(im)
 out.save(D/'merged.png');out.convert('RGB').save(P/'JPG'/('%d.jpg'%n),quality=97,subsampling=0)
 root=ET.Element('image',w=str(W),h=str(H),name='Photo native rebuild');stack=ET.SubElement(root,'stack')
 with zipfile.ZipFile(D/'layers.ora','w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('mimetype','image/openraster')
  for i,(name,im) in reversed(list(enumerate(layers))):
   fn='data/layer%d.png'%i;b=io.BytesIO();im.save(b,format='PNG');z.writestr(fn,b.getvalue());im.save(D/('layer%d.png'%i));ET.SubElement(stack,'layer',name=name,src=fn,x='0',y='0',opacity='1.0',visibility='visible',**{'composite-op':'svg:src-over'})
  z.writestr('stack.xml',ET.tostring(root));b=io.BytesIO();out.save(b,format='PNG');z.writestr('mergedimage.png',b.getvalue())
 old=Image.open(OLD/'JPG'/('%d.jpg'%n)).convert('RGB');pair=Image.new('RGB',(W*2,H));pair.paste(old,(0,0));pair.paste(out.convert('RGB'),(W,0));pair.thumbnail((1880,1673));pair.save(P/'review'/('%d-old-left-new-right.jpg'%n),quality=96)
 for tag,box in [('face',(xy[0]+int(sz[0]*.25),xy[1]+int(sz[1]*.25),xy[0]+int(sz[0]*.75),xy[1]+int(sz[1]*.75)))]:
  crop=out.crop(box);crop.resize((crop.width*2,crop.height*2)).convert('RGB').save(P/'review'/('%d-%s-200pct.jpg'%(n,tag)),quality=97)
 records.append(dict(id=n,whole_product_source=str(S/'product372.png'),rotation_ccw=angle,scale=scale,rotated_size=sz,xy=xy,perspective_warp=False,ai_product_pixels=False,product_relighting=False,text=[x[0] for x in specs],source_limit='Photo372 front angle; thickness/back not reconstructed. Source knob occlusion and reflections remain.'))
(P/'transforms.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print('Rendered 387 and399; copied11 originals')

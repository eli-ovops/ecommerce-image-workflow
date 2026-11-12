from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter,ImageChops
import io,json,zipfile,xml.etree.ElementTree as ET,shutil,hashlib
P=Path(__file__).resolve().parent;OLD=P.parent/'2026-11-02_顶喷13张逐图新画面';N=P.parent/'2026-11-02_391安装仰视单张实验';SZ=(1200,1200);F='/System/Library/Fonts/STHeiti Medium.ttc'
layers=[];texts=[]
def add(n,im):layers.append((n,im))
def blank():return Image.new('RGBA',SZ)
def shape(n,fn):
 im=blank();fn(ImageDraw.Draw(im));add(n,im)
def text(s,xy,size,c,stroke=0):
 im=blank();ImageDraw.Draw(im).text(xy,s,font=ImageFont.truetype(F,size),fill=c,stroke_width=stroke,stroke_fill=c,anchor='lt');add('Text '+s,im);texts.append(dict(text=s,xy=xy,size=size,color=c,stroke=stroke))
bg=ImageOps.fit(Image.open(P/'reused-scene.png').convert('RGBA'),SZ);bg.save(P/'reused-scene.png');add('User accepted scene reused unchanged',bg)
# Native cached installed product + connected pipe +94 separate illustrative streams.
r=Image.open(P/'installed-native-render.png').convert('RGBA').resize((1920,1920),Image.Resampling.LANCZOS);l=blank();l.alpha_composite(r,(-320,-140));add('Native installed product pipe and illustrative water',l);l.save(P/'installed-layer.png')
# Beige information stage with slight natural gradient, rather than a flat poster slab.
band=blank();d=ImageDraw.Draw(band)
for y in range(960,1200):
 t=(y-960)/240;c=tuple(round(a*(1-t)+b*t) for a,b in zip((239,210,177),(208,165,127)));d.line((0,y,1200,y),fill=(*c,255))
add('Beige information band',band)
# Inset: genuine native3D shell with photo-only face, no flat photo cutout boundary.
raw=Image.open(P/'inset-native-render.png').convert('RGBA');box=raw.getchannel('A').getbbox();assert box[0]>0 and box[2]<raw.width and box[1]>0 and box[3]<raw.height,box
raw=raw.crop(box);raw.thumbnail((545,590),Image.Resampling.LANCZOS);xy=(30,1150-raw.height)
prod=blank();prod.alpha_composite(raw,xy)
shadow=blank();sd=ImageDraw.Draw(shadow);sd.ellipse((75,1110,565,1170),fill=(35,18,8,105));shadow=shadow.filter(ImageFilter.GaussianBlur(18));add('Soft stage contact shadow',shadow)
m=Image.new('L',SZ);m.paste(prod.getchannel('A'),(9,14));m=m.filter(ImageFilter.GaussianBlur(10)).point(lambda v:round(v*.4));sh=blank();sh.putalpha(m);add('Warm cast shadow',sh);add('Native inset product',prod);prod.save(P/'inset-layer.png')
# Heavy oblique white lettering with red dimensional edge, closely following388 typography.
mask=Image.new('L',(700,220));md=ImageDraw.Draw(mask);md.text((25,21),'提拉除垢',font=ImageFont.truetype(F,144),fill=255,stroke_width=4,anchor='lt')
mask=mask.transform(mask.size,Image.Transform.AFFINE,(1,.18,-39,0,1,0),Image.Resampling.BICUBIC)
outer=mask.filter(ImageFilter.MaxFilter(33));red=mask.filter(ImageFilter.MaxFilter(25));headxy=(470,536)
for name,ma,col,offset in [('Deep red extrusion',outer,'#640910',(7,11)),('Red edge highlight',outer,'#e27164',(0,-1)),('Red main outline',red,'#ad111f',(0,0)),('White heavy italic',mask,'#fffdf7',(0,0))]:
 q=Image.new('RGBA',ma.size,col);q.putalpha(ma);ll=blank();ll.alpha_composite(q,(headxy[0]+offset[0],headxy[1]+offset[1]));add(name,ll)
texts.append(dict(text='提拉除垢',xy=headxy,size=144,italic_shear=.18,stroke_width=4,outline_red=12,outline_outer=16,dimensional_offset=[7,11]))
# Delete the circled inset microcopy completely. Keep all product text off the inset.
shape('Demonstration badge',lambda d:d.rounded_rectangle((897,35,1170,92),27,fill=(83,23,18,230)))
text('安装出水示意',(920,52),31,'#fff6e9',1)
shape('Action dark ribbon',lambda d:d.rounded_rectangle((640,749,1020,831),16,fill=(44,26,19,230)))
text('红钮向外提拉',(665,768),45,'#fff6e9',1)
text('约30×20cm 大面板',(624,994),39,'#31221a',1)
text('长方形顶喷',(615,1063),83,'#201714',3)
out=blank()
for _,im in layers:out=Image.alpha_composite(out,im)
out.convert('RGB').save(P/'388_粗斜字体与融合_审阅.jpg',quality=97,subsampling=0)
small=out.copy();small.thumbnail((360,360));small.convert('RGB').save(P/'mobile-360.jpg',quality=95)
# Native layered image, and live editable typography counterpart.
root=ET.Element('image',w='1200',h='1200');st=ET.SubElement(root,'stack')
with zipfile.ZipFile(P/'388-editable.ora','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('mimetype','image/openraster')
 for i,(name,im) in enumerate(reversed(layers)):
  b=io.BytesIO();im.save(b,format='PNG');f=f'data/layer{i}.png';z.writestr(f,b.getvalue());ET.SubElement(st,'layer',name=name,src=f,x='0',y='0',opacity='1',visibility='visible',**{'composite-op':'svg:src-over'})
 z.writestr('stack.xml',ET.tostring(root));b=io.BytesIO();out.save(b,format='PNG');z.writestr('mergedimage.png',b.getvalue())
base=blank()
for name,im in layers:
 if not(name.startswith('Text ') or name in ['Deep red extrusion','Red edge highlight','Red main outline','White heavy italic']):base=Image.alpha_composite(base,im)
base.save(P/'editable-base.png')
svg='<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200"><image href="editable-base.png" width="1200" height="1200"/>'
for t in texts:
 s=t['text'];x,y=t['xy'];sz=t['size']
 if 'italic_shear' in t:
  svg+='<g transform="translate(535 705) skewX(-10)"><text x="7" y="11" font-family="Heiti SC" font-weight="900" font-size="144" fill="#640910" stroke="#640910" stroke-width="32" paint-order="stroke">提拉除垢</text><text font-family="Heiti SC" font-weight="900" font-size="144" fill="#fffdf7" stroke="#ad111f" stroke-width="24" paint-order="stroke">提拉除垢</text></g>'
 else:svg+=f'<text x="{x}" y="{y+sz*.85}" font-family="Heiti SC" font-weight="900" font-size="{sz}" fill="{t["color"]}" stroke="{t["color"]}" stroke-width="{t["stroke"]*2}" paint-order="stroke">{s}</text>'
(P/'editable-text.svg').write_text(svg+'</svg>');(P/'layout.json').write_text(json.dumps(dict(texts=texts,inset_crop=box,inset_xy=xy,inset_size=raw.size,installed_scale=1.6,installed_xy=[-320,-140],deleted_inset_microcopy=True,original_scene_sha=hashlib.sha256((P/'reused-scene.png').read_bytes()).hexdigest(),scene_reused_no_imagegen=True),ensure_ascii=False,indent=2))
ref=Image.open(P/'reference388.jpg').resize(SZ,Image.Resampling.LANCZOS);comp=Image.new('RGB',(2400,1200));comp.paste(ref,(0,0));comp.paste(out,(1200,0));comp.save(P/'388_左参考右返修.jpg',quality=95)
out.crop((0,550,600,1180)).resize((1200,1260)).convert('RGB').save(P/'inset-200pct.jpg',quality=97);out.crop((450,525,1190,760)).resize((1480,470)).convert('RGB').save(P/'type-200pct.jpg',quality=97)
print('Saved388 localized revision; other images untouched')

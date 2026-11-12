from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageChops,ImageOps
import numpy as np,json,zipfile,io,xml.etree.ElementTree as ET,hashlib
P=Path(__file__).resolve().parent
im=Image.open(P/'sources/372-oriented.png').convert('RGB');W,H=1200,1800
# Hand traced outer silver perimeter in the reviewed 1400px-wide original preview.
segments=[((325,219),(590,221),(900,224),(1137,227)),((1137,227),(1191,227),(1232,260),(1233,313)),((1233,313),(1238,485),(1245,660),(1251,826)),((1251,826),(1254,879),(1216,917),(1164,920)),((1164,920),(875,920),(560,918),(289,916)),((289,916),(233,916),(199,883),(201,826)),((201,826),(209,655),(217,476),(222,316)),((222,316),(225,257),(267,220),(325,219))]
pts=[]
for seg in segments:
 a,b,c,d=np.array(seg,float)
 for t in np.linspace(0,1,100):
  q=(1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d;pts.append(tuple(q*im.width/1400))
mask=Image.new('L',im.size);ImageDraw.Draw(mask).polygon(pts,fill=255);mask=mask.filter(ImageFilter.GaussianBlur(.65));mask.save(P/'sources/subject-mask.png')
cut=im.convert('RGBA');cut.putalpha(mask);box=mask.getbbox();cut=cut.crop(box);cut.save(P/'sources/subject-original-cutout.png')
angle=62
rot=cut.rotate(angle,Image.Resampling.BICUBIC,expand=True)
scale=min(1050/rot.width,1320/rot.height);size=(round(rot.width*scale),round(rot.height*scale));rot=rot.resize(size,Image.Resampling.LANCZOS)
xy=((W-size[0])//2,round(1050-size[1]/2))
product=Image.new('RGBA',(W,H));product.alpha_composite(rot,xy);product.save(P/'product-layer.png')
alpha=product.getchannel('A');alpha.save(P/'subject-mask-canvas.png')
if not (P/'background.png').exists():
 product.save(P/'cutout-layout.png');raise SystemExit('Prepared cutout; background pending')
bg=ImageOps.fit(Image.open(P/'background.png').convert('RGB'),(W,H),method=Image.Resampling.LANCZOS).convert('RGBA')
layers=[('AI empty marble background',bg)]
for name,radius,offset,opacity in [('Soft cast shadow',19,(11,22),.42),('Tight contact shadow',2.8,(2,5),.66)]:
 m=Image.new('L',(W,H));m.paste(alpha,offset);m=m.filter(ImageFilter.GaussianBlur(radius)).point(lambda v:round(v*opacity));layer=Image.new('RGBA',(W,H),(0,0,0,0));layer.putalpha(m);layer.save(P/(name.replace(' ','-')+'.png'));layers.append((name,layer))
layers.append(('Protected original372 whole product',product));out=Image.new('RGBA',(W,H))
for _,lay in layers:out=Image.alpha_composite(out,lay)
out.convert('RGB').save(P/'399_实拍主体_黑金实验.jpg',quality=97,subsampling=0)
# Standard editable OpenRaster: original-photo product, two shadows and background remain independent.
root=ET.Element('image',w=str(W),h=str(H),name='399 original photo composite');stack=ET.SubElement(root,'stack')
with zipfile.ZipFile(P/'399_可编辑合成.ora','w') as z:
 z.writestr('mimetype','image/openraster',compress_type=zipfile.ZIP_STORED)
 for i,(name,lay) in enumerate(reversed(layers)):
  path=f'data/layer{i}.png';buf=io.BytesIO();lay.save(buf,format='PNG');z.writestr(path,buf.getvalue());ET.SubElement(stack,'layer',name=name,src=path,x='0',y='0',opacity='1.0',visibility='visible',**{'composite-op':'svg:src-over'})
 z.writestr('stack.xml',ET.tostring(root));buf=io.BytesIO();out.save(buf,format='PNG');z.writestr('mergedimage.png',buf.getvalue())
# Same-scale source versus final: both panels use the exact same similarity transform.
raw=im.crop(box).convert('RGBA').rotate(angle,Image.Resampling.BICUBIC,expand=True).resize(size,Image.Resampling.LANCZOS)
source=Image.new('RGBA',(W,H),(100,100,100,255));source.alpha_composite(raw,xy)
comparison=Image.new('RGB',(2*W,H));comparison.paste(source.convert('RGB'),(0,0));comparison.paste(out.convert('RGB'),(W,0));comparison.save(P/'同尺度对照_左实拍右成图.jpg',quality=96)
# Three actual-size 200% crops, left source / right final.
regions={'panel':(460,800,740,1080),'upper-edge':(600,480,880,760),'lower-edge':(320,1320,600,1600)}
detail=Image.new('RGB',(1120,1680))
for i,(name,rect) in enumerate(regions.items()):
 for j,img in enumerate([source,out]):detail.paste(img.crop(rect).convert('RGB').resize((560,560),Image.Resampling.NEAREST),(j*560,i*560))
detail.save(P/'200pct_左实拍右成图_面板及银边.jpg',quality=97)
record={'source_original':'products/长方形拉钮顶喷/原始实拍20261030/微信图片_20261030154107_372_2.jpg','source_oriented_size':im.size,'mask_bezier_preview_width':1400,'mask_segments':segments,'crop_bbox':box,'rotation_ccw_degrees':angle,'uniform_scale_after_rotation':scale,'rotated_layer_size':size,'canvas_placement':xy,'canvas_size':[W,H],'perspective_warp':False,'product_relight_or_redraw':False,'resampling':'Bicubic rotation then Lanczos uniform scaling. Not pixel-identical original.','occlusion':'Original red knob hides center; back connector and most 20mm side thickness not visible from this source angle. No reconstruction.','detail_crop_regions':regions}
(P/'transforms.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
with zipfile.ZipFile(P/'399_可编辑合成.ora') as z:assert z.testzip() is None
print(record)

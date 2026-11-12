from pathlib import Path
from PIL import Image,ImageFilter,ImageChops
import json,zipfile,io,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent; R=P.parents[1]
B=R/'production/2026-11-03_顶喷两张细节回源修订'
(P/'candidates').mkdir(exist_ok=True)
source=Image.open(P/'native/product-v2.png').convert('RGBA');source=source.crop(source.getchannel('A').getbbox())
records=[]
for n,angle,bounds,xy in [(387,-3,(610,860),(425,190)),(399,-22,(870,1090),(35,525))]:
 old=B/'editable'/str(n); dest=P/'editable'/str(n);dest.mkdir(parents=True,exist_ok=True)
 layers=[Image.open(old/('layer%d.png'%i)).convert('RGBA') for i in range(5)];size=layers[0].size
 body=source.rotate(angle,Image.Resampling.BICUBIC,expand=True);s=min(bounds[0]/body.width,bounds[1]/body.height);body=body.resize(tuple(round(v*s) for v in body.size),Image.Resampling.LANCZOS)
 layers[2]=Image.new('RGBA',size);layers[2].alpha_composite(body,xy)
 shadow=Image.new('RGBA',size);shadow.putalpha(layers[2].getchannel('A').filter(ImageFilter.GaussianBlur(13)).point(lambda v:round(v*.65)))
 layers[1]=Image.new('RGBA',size);layers[1].alpha_composite(shadow,(12,17))
 out=Image.new('RGBA',size)
 for im in layers:out.alpha_composite(im)
 out.save(dest/'merged.png');out.convert('RGB').save(P/'candidates'/('%d.jpg'%n),quality=97,subsampling=0)
 names=['Original background unchanged','Adjusted soft shadow','Original372 face plus native20mm housing','Original decor unchanged','Original lettering unchanged']
 root=ET.Element('image',w=str(size[0]),h=str(size[1]));stack=ET.SubElement(root,'stack')
 with zipfile.ZipFile(dest/'layers.ora','w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('mimetype','image/openraster')
  for i in reversed(range(5)):
   im=layers[i];im.save(dest/('layer%d.png'%i));b=io.BytesIO();im.save(b,format='PNG');fn='data/layer%d.png'%i;z.writestr(fn,b.getvalue());ET.SubElement(stack,'layer',name=names[i],src=fn,x='0',y='0',opacity='1.0',visibility='visible',**{'composite-op':'svg:src-over'})
  z.writestr('stack.xml',ET.tostring(root));b=io.BytesIO();out.save(b,format='PNG');z.writestr('mergedimage.png',b.getvalue())
 prev=Image.open(B/'JPG'/('%d.jpg'%n)).convert('RGB');pair=Image.new('RGB',(size[0]*2,size[1]));pair.paste(prev,(0,0));pair.paste(out,(size[0],0));pair.thumbnail((1880,1673));pair.save(P/'review'/('%d-before-left-after-right.jpg'%n),quality=95)
 phone=out.convert('RGB');phone.thumbnail((390,700));phone.save(P/'review'/('%d-phone.jpg'%n),quality=95)
 records.append({'id':n,'rotation_ccw':angle,'scale':s,'xy':xy,'size':body.size,'unchanged_layers':[0,3,4],'unchanged_layers_pixel_check':all(ImageChops.difference(layers[i],Image.open(old/('layer%d.png'%i)).convert('RGBA')).getbbox() is None for i in (0,3,4))})
(P/'transforms.json').write_text(json.dumps(records,indent=2))

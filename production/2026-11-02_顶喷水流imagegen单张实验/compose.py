from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageOps,ImageChops
import numpy as np,json,zipfile,io,xml.etree.ElementTree as ET,hashlib
P=Path(__file__).resolve().parent; B=P.parent/'2026-11-02_顶喷13张整批返修'
dry=Image.open(P/'dry-product.png').convert('RGBA'); raw=Image.open(P/'water-generated-original.png').convert('RGBA').resize((1200,1200),Image.Resampling.LANCZOS)
pts=json.loads((P/'projected-origins.json').read_text()); gate=Image.new('L',(1200,1200));d=ImageDraw.Draw(gate)
# Native mask only: narrow openings immediately below candidate origins, expanding below face.
for q in pts:
 x,y=q['x'],q['y'];d.polygon([(x-1,y),(x+1,y),(x+2,425),(x+18,1200),(x-18,1200),(x-2,425)],fill=255)
gate=gate.filter(ImageFilter.GaussianBlur(.65)); gate.save(P/'water-origin-gate.png')
arr=np.array(raw).astype(float);lum=arr[:,:,:3].mean(2);arr[:,:,:3]=np.stack([lum*1.025,lum,lum*.98],axis=2)
# Suppress generated grey haze while preserving the generated droplet shapes and native alpha.
contrast=np.clip((lum-115)/120,0,1)**1.5
alpha=arr[:,:,3]/255*contrast*.62*np.array(gate)/255
arr[:,:,3]=alpha*255; water=Image.fromarray(np.uint8(np.clip(arr,0,255)),'RGBA');water.save(P/'water-masked.png')
native=dry.copy();native.alpha_composite(water);native.save(P/'native-water-composite.png')
protected=(np.array(dry)[:,:,3]>250)&(np.array(gate)==0); mask=Image.fromarray(np.uint8(protected)*255);mask.save(P/'product-protected-mask.png')
assert np.array_equal(np.array(native)[protected],np.array(dry)[protected])
# Recompose original editable393 scene, replacing only native installed layer.
layers=[]
with zipfile.ZipFile(B/'editable/393/layers.ora') as z:
 root=ET.fromstring(z.read('stack.xml'))
 for e in reversed(list(root.find('stack'))):layers.append((e.attrib['name'],Image.open(io.BytesIO(z.read(e.attrib['src']))).convert('RGBA')))
scale=1.6890756302521008;xy=(-399,49)
def placed(im):
 c=Image.new('RGBA',(1200,1200));c.alpha_composite(im.resize((round(1200*scale),round(1200*scale)),Image.Resampling.LANCZOS),xy);return c
out=Image.new('RGBA',(1200,1200));outlayers=[];before=Image.new('RGBA',(1200,1200))
for name,im in layers:
 before.alpha_composite(im)
 if name=='Native installed shell pipe and water illustration':
  for nm,li in [('Protected native product',placed(dry)),('Imagegen water masked',placed(water))]:out.alpha_composite(li);outlayers.append((nm,li))
 else:out.alpha_composite(im);outlayers.append((name,im))
out.save(P/'393-water-experiment.png');out.convert('RGB').save(P/'393-water-experiment.jpg',quality=97,subsampling=0)
# Additional uncluttered water study: reuse approved scene layer, no cards hiding lower breakup.
scene=ImageOps.fit(Image.open(B/'assets/warm-bath.png').convert('RGBA'),(1200,1200));clean=scene.copy();oldclean=scene.copy()
for target,subject in [(clean,native),(oldclean,Image.open(B/'assets/native-installed.png').convert('RGBA'))]:
 target.alpha_composite(subject.resize((1740,1740),Image.Resampling.LANCZOS),(-250,0))
clean.convert('RGB').save(P/'water-study.jpg',quality=97,subsampling=0)
clean.save(P/'water-study.png')
study=Image.new('RGB',(2400,1200));study.paste(oldclean.convert('RGB'),(0,0));study.paste(clean.convert('RGB'),(1200,0));study.save(P/'water-study-before-after.jpg',quality=97)
for name,box in [('study-origins',(400,300,800,520)),('study-droplets',(400,750,800,1100))]:
 pair=Image.new('RGB',((box[2]-box[0])*4,(box[3]-box[1])*2))
 for i,im in enumerate([oldclean,clean]):pair.paste(im.crop(box).convert('RGB').resize(((box[2]-box[0])*2,(box[3]-box[1])*2)),(i*(box[2]-box[0])*2,0))
 pair.save(P/f'{name}-200pct-before-after.jpg',quality=97)
before.convert('RGB').save(P/'393-before.jpg',quality=97,subsampling=0)
pair=Image.new('RGB',(2400,1200));pair.paste(before.convert('RGB'),(0,0));pair.paste(out.convert('RGB'),(1200,0));pair.save(P/'before-after.jpg',quality=95)
for name,box in [('origins',(350,360,750,600)),('droplets',(400,600,800,800))]:
 pair=Image.new('RGB',((box[2]-box[0])*4,(box[3]-box[1])*2))
 for i,im in enumerate([before,out]):pair.paste(im.crop(box).convert('RGB').resize(((box[2]-box[0])*2,(box[3]-box[1])*2)),(i*(box[2]-box[0])*2,0))
 pair.save(P/f'{name}-200pct-before-after.jpg',quality=97)
root=ET.Element('image',w='1200',h='1200');stack=ET.SubElement(root,'stack')
with zipfile.ZipFile(P/'393-water-editable.ora','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('mimetype','image/openraster',compress_type=zipfile.ZIP_STORED)
 for i,(name,im) in enumerate(reversed(outlayers)):
  f=f'data/layer{i}.png';buf=io.BytesIO();im.save(buf,format='PNG');z.writestr(f,buf.getvalue());ET.SubElement(stack,'layer',name=name,src=f,x='0',y='0',opacity='1',visibility='visible',**{'composite-op':'svg:src-over'})
 z.writestr('stack.xml',ET.tostring(root));buf=io.BytesIO();out.save(buf,format='PNG');z.writestr('mergedimage.png',buf.getvalue())
report=dict(candidate_origins=len(pts),generated_size=[1254,1254],registered_size=[1200,1200],protected_pixels=int(protected.sum()),protected_pixels_identical=True,full_product_pixels_identical=False,reason='Generated water can cover narrow corridors below candidate origins; all other fully opaque product pixels unchanged before final uniform composition resize.',per_hole_verified=False,generated_water_is_measured=False,source_product='Native 3D shell with single original372 photographic face',water_method='One built-in imagegen generation, then native alpha mask, desaturation and haze suppression; no generated image fed back to model.')
(P/'verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))

from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
import numpy as np,zipfile,io,json,hashlib,xml.etree.ElementTree as ET,shutil
P=Path(__file__).resolve().parent;S=P.parent/'2026-11-02_顶喷水流imagegen单张实验'
for name in ['water-generated-original.png','water-masked.png','dry-product.png','projected-origins.json','water-origin-gate.png','product-protected-mask.png']:
 shutil.copy2(S/name,P/name)
old=Image.open(P/'water-masked.png').convert('RGBA');dry=Image.open(P/'dry-product.png').convert('RGBA');raw=Image.open(P/'water-generated-original.png').convert('RGBA').resize((1200,1200),Image.Resampling.LANCZOS)
a=np.asarray(raw).astype(float);lum=a[:,:,:3].mean(2);a[:,:,:3]=np.stack([lum*1.025,lum,lum*.98],2)
gate=np.asarray(Image.open(P/'water-origin-gate.png'))/255
aa=a[:,:,3]/255*np.clip((lum-105)/130,0,1)**1.2*.90*gate
a[:,:,3]=aa*255;strong=Image.fromarray(np.uint8(np.clip(a,0,255)))
# Density increase starts below the product. Original origin corridors and product overlay remain byte-identical.
y=np.arange(1200)[:,None];fade=np.broadcast_to(np.clip((y-405)/95,0,1),(1200,1200)).copy();fade[np.asarray(dry)[:,:,3]>0]=0
base=np.asarray(old).astype(float)*(1-fade[:,:,None])+np.asarray(strong).astype(float)*fade[:,:,None]
water=Image.fromarray(np.uint8(base));extra=Image.new('RGBA',(1200,1200))
for dx,dy,opacity in [(-11,17,.22),(14,-9,.18)]:
 shifted=Image.new('RGBA',(1200,1200));shifted.alpha_composite(strong,(dx,dy));ar=np.array(shifted);below=np.broadcast_to(np.clip((y-465)/120,0,1),(1200,1200)).copy();below[np.asarray(dry)[:,:,3]>0]=0;ar[:,:,3]=np.uint8(ar[:,:,3]*below*opacity);extra.alpha_composite(Image.fromarray(ar))
water.alpha_composite(extra);water.save(P/'water-denser.png');extra.save(P/'additional-lower-water.png');Image.fromarray(np.uint8(fade*255)).save(P/'density-change-mask.png')
productmask=np.asarray(dry)[:,:,3]>0
assert np.array_equal(np.array(water)[productmask],np.array(old)[productmask])
def readora(f):
 with zipfile.ZipFile(f) as z:
  root=ET.fromstring(z.read('stack.xml'));return [(e.attrib['name'],Image.open(io.BytesIO(z.read(e.attrib['src']))).convert('RGBA')) for e in reversed(list(root.find('stack')))]
def place(im,scale,xy):
 out=Image.new('RGBA',(1200,1200));out.alpha_composite(im.resize((round(1200*scale),round(1200*scale)),Image.Resampling.LANCZOS),xy);return out
def ora(f,layers,out):
 root=ET.Element('image',w='1200',h='1200');stack=ET.SubElement(root,'stack')
 with zipfile.ZipFile(f,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('mimetype','image/openraster',compress_type=zipfile.ZIP_STORED)
  for i,(name,im) in enumerate(reversed(layers)):
   b=io.BytesIO();im.save(b,format='PNG');fn=f'data/{i}.png';z.writestr(fn,b.getvalue());ET.SubElement(stack,'layer',name=name,src=fn,x='0',y='0',opacity='1',visibility='visible',**{'composite-op':'svg:src-over'})
  z.writestr('stack.xml',ET.tostring(root));b=io.BytesIO();out.save(b,format='PNG');z.writestr('mergedimage.png',b.getvalue())
 with zipfile.ZipFile(f) as z:assert z.testzip() is None
 recomposed=Image.new('RGBA',(1200,1200))
 for _,im in readora(f):recomposed.alpha_composite(im)
 assert ImageChops.difference(recomposed,out).getbbox() is None
unchanged=[]
for key,src,scale,xy in [('393','393-water-editable.ora',1.6890756302521008,(-399,49)),('water-study','water-study-editable.ora',1.45,(-250,0))]:
 layers=readora(S/src);before=Image.new('RGBA',(1200,1200));out=before.copy();new=[]
 for name,im in layers:
  before.alpha_composite(im)
  if name in ['Imagegen water masked','Generated water with origin mask']:im=place(water,scale,xy)
  else:unchanged.append(key+':'+name)
  new.append((name,im));out.alpha_composite(im)
 out.save(P/f'{key}-denser.png');out.convert('RGB').save(P/f'{key}-denser.jpg',quality=97,subsampling=0)
 pair=Image.new('RGB',(2400,1200));pair.paste(before.convert('RGB'));pair.paste(out.convert('RGB'),(1200,0));pair.save(P/f'{key}-before-after.jpg',quality=96)
 ora(P/f'{key}-editable.ora',new,out)
 if key=='water-study':
  for label,box in [('origins',(400,300,800,520)),('water',(400,750,800,1100))]:
   w,h=box[2]-box[0],box[3]-box[1];pair=Image.new('RGB',(w*4,h*2))
   for i,im in enumerate([before,out]):pair.paste(im.crop(box).convert('RGB').resize((w*2,h*2)),(i*w*2,0))
   pair.save(P/f'{label}-200pct-before-after.jpg',quality=97)
oa=np.asarray(old)[:,:,3];na=np.asarray(water)[:,:,3];roi=np.zeros((1200,1200),bool);roi[500:1100,300:950]=True
report=dict(imagegen_calls=0,source_water=str(S/'water-generated-original.png'),product_region_water_pixels_identical=True,product_region_pixels=int(productmask.sum()),origin_positions_unchanged=True,per_hole_alignment_verified=False,unchanged_nonwater_layers=unchanged,lower_water_alpha_sum_ratio=float(na[roi].sum()/oa[roi].sum()),lower_visible_area_ratio=float((na[roi]>30).sum()/(oa[roi]>30).sum()),method='Increase existing generated water alpha and retain more weak droplets; two subtle offset copies below head only. Full product-region water unchanged; no new origins; no straight-line synthesis.',ora_crc_recomposition=True)
(P/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))

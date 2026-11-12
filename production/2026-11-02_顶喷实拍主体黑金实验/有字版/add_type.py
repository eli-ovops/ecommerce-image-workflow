from pathlib import Path
from PIL import Image,ImageFont,ImageDraw,ImageFilter,ImageChops
import numpy as np,zipfile,io,json,xml.etree.ElementTree as ET,hashlib
P=Path(__file__).resolve().parent;W,H=1200,1800
font='/System/Library/Fonts/Supplemental/Songti.ttc'
with zipfile.ZipFile(P.parent/'399_可编辑合成.ora') as z:
 base=Image.open(io.BytesIO(z.read('mergedimage.png'))).convert('RGBA')
 original={name:z.read(name) for name in z.namelist()}
texts=[{'text':'长方形 · 银色顶喷','x':88,'y':76,'size':38,'font_index':1},{'text':'提拉除垢','x':80,'y':155,'size':178,'font_index':0},{'text':'短针辅助清理出水孔','x':88,'y':372,'size':53,'font_index':1}]
mask=Image.new('L',(W,H));d=ImageDraw.Draw(mask)
for t in texts:d.text((t['x'],t['y']),t['text'],font=ImageFont.truetype(font,t['size'],index=t['font_index']),fill=255,anchor='lt')
# Local typographic veil is confined to empty header and never intersects product pixels.
alpha=np.zeros((H,W),dtype=np.uint8)
for y in range(480):alpha[y,:]=int(65*min(1,(480-y)/100))
veil=Image.new('RGBA',(W,H),(0,0,0,0));veil.putalpha(Image.fromarray(alpha))
product=Image.open(P.parent/'product-layer.png').getchannel('A');assert ImageChops.multiply(veil.getchannel('A'),product).getbbox() is None
shadow=Image.new('RGBA',(W,H),(0,0,0,0));shadow.putalpha(mask.filter(ImageFilter.GaussianBlur(3)).point(lambda x:round(x*.8)))
arr=np.zeros((H,W,4),dtype=np.uint8)
stops=[(0,(242,212,162)),(160,(255,232,189)),(240,(217,173,110)),(330,(245,215,170)),(450,(233,196,143))]
for c in range(3):arr[:,:,c]=np.interp(np.arange(H),[s[0] for s in stops],[s[1][c] for s in stops])[:,None]
arr[:,:,3]=np.asarray(mask);letters=Image.fromarray(arr)
deco=Image.new('RGBA',(W,H));dd=ImageDraw.Draw(deco);dd.line((88,133,426,133),fill=(183,137,77,220),width=2);dd.line((88,451,700,451),fill=(185,139,82,180),width=2);dd.polygon([(720,445),(726,451),(720,457),(714,451)],fill=(234,194,136,255))
newlayers=[('Header contrast veil',veil),('Title shadow',shadow),('Editable typography raster preview',letters),('Gold decorative rules',deco)]
out=base
for _,lay in newlayers:out=Image.alpha_composite(out,lay)
out.convert('RGB').save(P/'399_黑金电商有字版.jpg',quality=97,subsampling=0)
out.convert('RGB').resize((360,540),Image.Resampling.LANCZOS).save(P/'手机缩略_360.jpg',quality=95)
root=ET.fromstring(original['stack.xml']);stack=root.find('stack')
with zipfile.ZipFile(P/'399_有字分层合成.ora','w') as z:
 for name,data in original.items():
  if name not in ['stack.xml','mergedimage.png']:z.writestr(name,data)
 for i,(name,lay) in enumerate(newlayers):
  f=f'data/text-layer{i}.png';b=io.BytesIO();lay.save(b,format='PNG');z.writestr(f,b.getvalue());stack.insert(0,ET.Element('layer',name=name,src=f,x='0',y='0',opacity='1.0',visibility='visible',**{'composite-op':'svg:src-over'}))
 z.writestr('stack.xml',ET.tostring(root));b=io.BytesIO();out.save(b,format='PNG');z.writestr('mergedimage.png',b.getvalue())
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1800" viewBox="0 0 1200 1800">','<defs><linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#ffe8bd"/><stop offset=".55" stop-color="#d9ad6e"/><stop offset="1" stop-color="#f5d7aa"/></linearGradient></defs>','<g fill="url(#gold)" font-family="Songti SC" dominant-baseline="text-before-edge">']
for t in texts:svg.append(f'<text x="{t["x"]}" y="{t["y"]}" font-size="{t["size"]}" font-weight="{900 if t["font_index"]==0 else 700}">{t["text"]}</text>')
svg+=['</g><path d="M88 133H426 M88 451H700" stroke="#b98b52" stroke-width="2"/><path d="M720 445L726 451L720 457L714 451Z" fill="#eac288"/></svg>'];(P/'可编辑文字.svg').write_text('\n'.join(svg))
(P/'typography.json').write_text(json.dumps({'texts':texts,'font_path':font,'image_size':[W,H],'product_pixels_unmodified':True,'svg_note':'Editable live text; renderer font metrics may differ. Exact production rendering is reproducible via this script and typography.json.','source_sha256':hashlib.sha256((P.parent/'399_可编辑合成.ora').read_bytes()).hexdigest()},ensure_ascii=False,indent=2))
assert ImageChops.multiply(ImageChops.difference(base,out).convert('RGB').convert('L'),product).getbbox() is None
with zipfile.ZipFile(P/'399_有字分层合成.ora') as z:assert z.testzip() is None
print('Product pixels unchanged; no typography overlap; ORA CRC passed')

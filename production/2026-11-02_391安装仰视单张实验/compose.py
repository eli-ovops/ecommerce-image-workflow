from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import io,zipfile,xml.etree.ElementTree as ET,json
P=Path(__file__).resolve().parent;B=P.parent/'2026-11-02_顶喷13张逐图新画面/assets/model-bath.png'
bg=ImageOps.fit(Image.open(B).convert('RGBA'),(1200,1200));bg.save(P/'model-background.png')
render=Image.open(P/'391-render.png').convert('RGBA').resize((1320,1320),Image.Resampling.LANCZOS);layer=Image.new('RGBA',(1200,1200));layer.alpha_composite(render,(-70,70));layer.save(P/'installation-layer.png')
txt=Image.new('RGBA',(1200,1200));d=ImageDraw.Draw(txt);font='/System/Library/Fonts/Supplemental/Songti.ttc'
texts=[('银色顶喷 浴室美学',45,50,67),('长方形面板 · 中央提拉红钮',48,143,35),('3D安装与水流示意',42,1125,35)]
for i,(s,x,y,z) in enumerate(texts):
 if i==2:d.rounded_rectangle((28,1107,430,1182),15,fill=(10,22,35,225))
 d.text((x,y),s,font=ImageFont.truetype(font,z,index=0),fill='#f2d7ac',anchor='lt')
out=Image.alpha_composite(Image.alpha_composite(bg,layer),txt);out.convert('RGB').save(P/'391_三维安装单张实验.jpg',quality=97,subsampling=0)
small=out.copy();small.thumbnail((360,360));small.convert('RGB').save(P/'391-mobile.jpg',quality=95)
root=ET.Element('image',w='1200',h='1200');st=ET.SubElement(root,'stack')
with zipfile.ZipFile(P/'391-editable.ora','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('mimetype','image/openraster')
 for i,(name,im) in enumerate([('Editable text raster preview',txt),('Blender shell single photo face pipe illustrative water',layer),('New adult model bathroom',bg)]):
  b=io.BytesIO();im.save(b,format='PNG');f=f'data/{i}.png';z.writestr(f,b.getvalue());ET.SubElement(st,'layer',name=name,src=f,x='0',y='0',opacity='1',visibility='visible',**{'composite-op':'svg:src-over'})
 z.writestr('stack.xml',ET.tostring(root));b=io.BytesIO();out.save(b,format='PNG');z.writestr('mergedimage.png',b.getvalue())
base=Image.alpha_composite(bg,layer);base.save(P/'editable-base.png');svg='<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200"><image href="editable-base.png" width="1200" height="1200"/><rect x="28" y="1107" width="402" height="75" rx="15" fill="#0a1623"/>'
for s,x,y,z in texts:svg+=f'<text x="{x}" y="{y+z*.85}" font-family="Songti SC" font-weight="900" font-size="{z}" fill="#f2d7ac">{s}</text>'
(P/'editable-text.svg').write_text(svg+'</svg>');(P/'layout.json').write_text(json.dumps(dict(render_scale=1.1,render_xy=[-70,70],texts=texts),ensure_ascii=False,indent=2))
# Final-size visual diagnostic crop and source water-origin overlay.
out.crop((245,185,1035,545)).resize((1580,720)).convert('RGB').save(P/'391-head-200pct.jpg',quality=97)
print('Composited1200px experiment, layered ORA and live SVG')

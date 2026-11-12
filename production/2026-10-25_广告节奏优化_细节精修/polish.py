from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil
r=Path('/Volumes/EXTERNAL/电商 作图工作流/production');old=r/'2026-10-25_广告节奏优化_正向信息版';b=r/'2026-10-25_广告节奏优化_细节精修';out=b/'JPG';g=r/'2026-10-24_完整电商套图/generated';m=json.loads((b/'manifest.json').read_text());f='/System/Library/Fonts/STHeiti Medium.ttc';cream='#f7f0e5'
def save(id,im,note):
 a=next(a for a in m['assets'] if a['id']==id);im.save(out/a['file'],quality=95,subsampling=0);a.update(size=list(im.size),sha256=hashlib.sha256((out/a['file']).read_bytes()).hexdigest(),notes=note)
im=Image.new('RGB',(1254,1200),cream);d=ImageDraw.Draw(im);p=Image.new('RGBA',(1200,170));ImageDraw.Draw(p).text((20,8),'三色 自在搭配',font=ImageFont.truetype(f,112),fill='#211a17',anchor='lt',stroke_width=3);p=p.transform(p.size,Image.Transform.AFFINE,(1,.10,-10,0,1,0),Image.Resampling.BICUBIC);im.paste(p,(39,55),p)
for x,key,name in [(35,'silver','银色'),(442,'black','黑色'),(849,'gunmetal','枪灰色')]:
 d.rectangle((x,250,x+370,1035),fill='#ece2d4');p=Image.open(g/(key+'-cutout-v003.png')).convert('RGBA');p=p.resize((round(p.width*800/p.height),800),Image.Resampling.LANCZOS);im.paste(p,(x+(370-p.width)//2,280),p);d.rectangle((x,1035,x+370,1199),fill=cream);font=ImageFont.truetype(f,62);w=d.textlength(name,font=font);d.text((x+(370-w)/2,1090),name,font=font,fill='#211a17',anchor='lt')
save('D01',im,'删除上方重复色名；三款同800px高度、370px栏居中，头缘至少10px栏内余量；下柄自然裁切；顶部空白收紧')
for id,top,start,end,note in [('M04',190,300,None,'删除三档名称重复副标题，头部压缩110px；三档原图不重绘'),('D02',210,310,1490,'删除泛化副标题与重复按键底条；只保留正背主题、标签与商品，头部空白收紧100px')]:
 a=next(a for a in m['assets'] if a['id']==id);p=Image.open(old/'JPG'/a['file']);end=end or p.height;q=Image.new('RGB',(p.width,top+end-start),cream);q.paste(p.crop((0,0,p.width,top)),(0,0));q.paste(p.crop((0,start,p.width,end)),(0,top));save(id,q,note)
parts=[]
for id in m['long_sequence']:
 a=next(a for a in m['assets'] if a['id']==id);p=Image.open(out/a['file']);parts.append(p.resize((1000,round(p.height*1000/p.width)),Image.Resampling.LANCZOS))
im=Image.new('RGB',(1000,sum(p.height for p in parts)));y=0
for p in parts:im.paste(p,(0,y));y+=p.height
save('L01',im,'同步D01与D02新图；13章主题次序保持');m['long_size']=list(im.size);m['revision']='D01完整头缘/居中/去重复色名；M04去重复档名；D02去重复副标题与底条；L01同步';(b/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
s=(b/'package.py').read_text().replace('14721',str(im.height));(b/'package.py').write_text(s);print(im.size)

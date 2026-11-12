from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[2];F=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',25)
c=Image.new('RGB',(2000,1280),'#eeeeee');d=ImageDraw.Draw(c)
for j,p in enumerate(sorted((B/'审查图').glob('*.jpg'))):
 im=Image.open(p);im.thumbnail((490,590));x=j%4*500;y=j//4*640;c.paste(im,(x+(500-im.width)//2,y+40));d.text((x+20,y+5),p.stem,font=F,fill='black')
c.save(B/'八视图总览.jpg',quality=95)
P=ROOT/'products/主推花洒/结构基准20261027/原件'
for n,box,model,title in [(339,(65,115,780,470),'01_正面.jpg','正面'),(342,(90,245,785,385),'04_左侧.jpg','侧面')]:
 im=Image.open(next(P.glob(f'*_{n}_*')));im=im.resize((800,600));im=im.crop(box).rotate(-90,expand=True);im=im.resize((round(im.width*1120/im.height),1120))
 mo=Image.open(B/'审查图'/model);mo=mo.crop((260,65,940,1430));mo=mo.resize((round(mo.width*1120/mo.height),1120))
 out=Image.new('RGB',(1400,1280),'#eeeeee');d=ImageDraw.Draw(out);out.paste(im,((700-im.width)//2,75));out.paste(mo,(700+(700-mo.width)//2,75));d.text((45,20),f'银色实拍 {n} · {title}裁切',font=F,fill='black');d.text((745,20),'同一模型 · 正交审查',font=F,fill='black');d.text((45,1210),'全件等比缩放；真实透视与正交机位未标定，不代表毫米误差或轮廓硬锁。',font=F,fill='black');out.save(B/f'{title}实拍对照.jpg',quality=95)

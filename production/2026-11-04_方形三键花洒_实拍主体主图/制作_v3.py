from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageFilter
from pathlib import Path
import math
root=Path(__file__).parent
src=Path('products/方形三键花洒/实拍原件20261104/照片/微信图片_20261104121549_465_2.jpg')
im=ImageOps.exif_transpose(Image.open(src)).convert('RGB'); W,H=im.size; k=W/1600
# 以原照轮廓作手绘曲线，只裁出实物，沿实拍整体等比旋转缩放。
segments=[
 ((143,465),(140,390),(180,344),(257,336)),
 ((257,336),(365,325),(527,324),(626,339)),
 ((626,339),(681,343),(712,368),(737,414)),
 ((737,414),(770,461),(817,502),(869,516)),
 ((869,516),(895,522),(919,522),(951,523)),
 ((951,523),(1060,523),(1255,523),(1335,524)),
 ((1335,524),(1340,546),(1338,645),(1335,674)),
 ((1335,674),(1250,675),(1040,674),(944,675)),
 ((944,675),(901,675),(872,674),(846,681)),
 ((846,681),(801,692),(759,722),(737,768)),
 ((737,768),(719,809),(693,828),(644,837)),
 ((644,837),(537,851),(360,850),(257,846)),
 ((257,846),(238,846),(222,840),(210,831)),
 ((210,831),(197,824),(186,813),(180,803)),
 ((180,803),(169,793),(161,777),(159,758)),
 ((159,758),(151,700),(146,530),(143,465)),
]
pts=[]
for p0,p1,p2,p3 in segments:
 for j in range(51):
  t=j/50;u=1-t
  x=u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0]
  y=u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1]
  pts.append((round(x*k),round(y*k)))
mask=Image.new('L',im.size,0);ImageDraw.Draw(mask).polygon(pts,fill=255);mask=mask.filter(ImageFilter.GaussianBlur(1.2))
rgba=im.convert('RGBA');rgba.putalpha(mask)
box=mask.getbbox(); cut=rgba.crop(box).transpose(Image.Transpose.ROTATE_270)
cut.save(root/'465_实拍主体_轮廓层_v3.png')
background=Image.open(root/'独立背景_原生.png').convert('RGB').resize((1600,1600),Image.Resampling.LANCZOS).convert('RGBA')
# 保持单一比例，不单独变形头柄。下柄自然出画。
height=1580;width=round(cut.width*height/cut.height);cut=cut.resize((width,height),Image.Resampling.LANCZOS)
x=930-(width//2)+260;y=110
shadow=Image.new('RGBA',background.size); a=Image.new('L',background.size);a.paste(cut.getchannel('A'),(x+12,y+18));a=a.filter(ImageFilter.GaussianBlur(24)).point(lambda z:int(z*.22));shadow.putalpha(a);background=Image.alpha_composite(background,shadow);background.alpha_composite(cut,(x,y))
d=ImageDraw.Draw(background)
font='/System/Library/Fonts/STHeiti Medium.ttc'
ft=ImageFont.truetype(font,106,index=0); small=ImageFont.truetype(font,59,index=0)
# 独立文字，避免生成字误写。
d.text((78,270),'三键切换',font=ft,fill='#3a241a',stroke_width=2,stroke_fill='#3a241a')
d.text((80,420),'手持花洒',font=ft,fill='#3a241a',stroke_width=2,stroke_fill='#3a241a')
# 不添加内部业务用语。
background.convert('RGB').save(root/'银色主图_实拍主体_v3.jpg',quality=95,subsampling=0)
print('source',im.size,'mask_bbox',box,'cut',cut.size,'placed',x,y)

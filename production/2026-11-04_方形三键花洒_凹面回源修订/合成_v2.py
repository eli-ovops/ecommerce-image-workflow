from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
root=Path(__file__).parent
source=Path('products/方形三键花洒/实拍补充20261104_凹面/微信图片_20261104145456_523_2.jpg')
bg=Path('production/2026-11-04_方形三键花洒_实拍主体主图/独立背景_原生.png')
im=ImageOps.exif_transpose(Image.open(source)).convert('RGBA');k=im.width/1600
segments=[
 ((350,570),(390,500),(490,310),(557,230)),
 ((557,230),(604,167),(638,139),(685,145)),
 ((685,145),(800,148),(990,195),(1166,259)),
 ((1166,259),(1213,277),(1244,315),(1252,376)),
 ((1252,376),(1260,435),(1305,503),(1375,552)),
 ((1375,552),(1428,590),(1517,596),(1566,625)),
 ((1566,625),(1586,637),(1598,652),(1600,658)),
 ((1600,658),(1600,710),(1600,850),(1600,915)),
 ((1600,915),(1552,900),(1442,866),(1374,838)),
 ((1374,838),(1324,817),(1284,805),(1243,803)),
 ((1243,803),(1160,799),(1098,825),(1035,867)),
 ((1035,867),(972,913),(945,928),(902,927)),
 ((902,927),(805,917),(640,855),(520,785)),
 ((520,785),(457,749),(404,713),(375,691)),
 ((375,691),(352,670),(343,642),(349,602)),
 ((349,602),(350,588),(350,580),(350,570)),
]
pts=[]
for a,b,c,d in segments:
 for j in range(50):
  t=j/49;u=1-t;pts.append((round(k*(u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*d[0])),round(k*(u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*d[1]))))
mask=Image.new('L',im.size); ImageDraw.Draw(mask).polygon(pts,fill=255);mask=mask.filter(ImageFilter.GaussianBlur(1.1));im.putalpha(mask)
cut=im.crop(mask.getbbox()).rotate(-72,resample=Image.Resampling.BICUBIC,expand=True);cut=cut.crop(cut.getchannel('A').getbbox());cut.save(root/'523_商品实拍抠层_v2.png')
background=Image.open(bg).convert('RGBA').resize((1600,1600),Image.Resampling.LANCZOS)
# 保留原始透视与明暗，仅整体等比缩放。尾部按真实照片自然出画。
height=1580;w=round(cut.width*height/cut.height);cut=cut.resize((w,height),Image.Resampling.LANCZOS)
x=650;y=135
alpha=Image.new('L',(1600,1600));alpha.paste(cut.getchannel('A'),(x+10,y+15));alpha=alpha.filter(ImageFilter.GaussianBlur(25)).point(lambda z:round(z*.16));shadow=Image.new('RGBA',(1600,1600),(0,0,0,0));shadow.putalpha(alpha);background=Image.alpha_composite(background,shadow);background.alpha_composite(cut,(x,y))
d=ImageDraw.Draw(background);font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',100);d.polygon([(70,290),(600,290),(578,420),(48,420)],fill='#713b24');d.line([(70,290),(600,290)],fill='#f7d897',width=5);d.text((84,300),'三键切换',font=font,fill='#fff7e7',stroke_width=2,stroke_fill='#fff7e7');d.text((70,452),'手持花洒',font=font,fill='#3a241a',stroke_width=2,stroke_fill='#3a241a');d.polygon([(70,587),(472,587),(451,596),(70,596)],fill='#b47836')
background.convert('RGB').save(root/'银色主图_523凹面实拍_候选02.jpg',quality=95,subsampling=0)
print('cut',w,height,'position',x,y,'mask',mask.getbbox())

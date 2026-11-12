from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageFont
from pathlib import Path
p=Path(__file__).parent
src=ImageOps.exif_transpose(Image.open(p.parent/'2026-10-29_圆形花洒_实拍主体验证/新实拍368/实拍原件.jpg')).convert('RGBA')
mask=Image.open(p/'自动蒙版.png').convert('L')
if mask.size!=src.size: mask=mask.resize(src.size)
src.putalpha(mask)
bbox=mask.getbbox(); obj=src.crop(bbox)
obj.thumbnail((1450,1050),Image.Resampling.LANCZOS)
obj=obj.rotate(-20,expand=True,resample=Image.Resampling.BICUBIC)
bg=Image.open('/Users/USER/.codex/generated_images/01a18a5f-a7dc-7371-b3e3-1329812e5e95/exec-ecd992bb-cf68-40ee-a95b-a5ae0a6ef979.png').convert('RGBA').resize((1600,1600),Image.Resampling.LANCZOS)
obj.thumbnail((1480,1100),Image.Resampling.LANCZOS)
x,y=(1600-obj.width)//2,400
shadow=Image.new('RGBA',bg.size); a=obj.getchannel('A').filter(ImageFilter.GaussianBlur(23)).point(lambda n: int(n*.34)); shadow.paste((54,37,28,255),(x+10,y+34),a); bg=Image.alpha_composite(bg,shadow);bg.alpha_composite(obj,(x,y))
d=ImageDraw.Draw(bg); f='/System/Library/Fonts/STHeiti Medium.ttc'; font=ImageFont.truetype(f,135); sub=ImageFont.truetype(f,66)
d.text((85,100),'三档出水',font=font,fill='#542b1a',stroke_width=1,stroke_fill='#542b1a');d.rounded_rectangle((90,265,460,360),radius=22,fill='#8b4e2e');d.text((119,272),'按键切换',font=sub,fill='white')
bg.convert('RGB').save(p/'实拍主体_广告试作.jpg',quality=95)

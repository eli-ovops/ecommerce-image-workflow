from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageFont
from pathlib import Path
p=Path(__file__).parent
photo=ImageOps.exif_transpose(Image.open(p.parent/'2026-10-29_圆形花洒_实拍主体验证/新实拍368/实拍原件.jpg')).convert('RGBA')
mask=Image.open(p/'原照蒙版.png').convert('L')
if mask.size != photo.size: mask=mask.resize(photo.size,Image.Resampling.LANCZOS)
photo.putalpha(mask); item=photo.crop(mask.getbbox()); item.thumbnail((1450,850),Image.Resampling.LANCZOS)
item=item.rotate(-24,resample=Image.Resampling.BICUBIC,expand=True); item.thumbnail((1450,1040),Image.Resampling.LANCZOS)
bg=Image.open(p/'背景.png').convert('RGBA').resize((1600,1600),Image.Resampling.LANCZOS)
x=(1600-item.width)//2; y=470
shadow=Image.new('RGBA',bg.size); alpha=item.getchannel('A').filter(ImageFilter.GaussianBlur(17)).point(lambda n:int(n*.27));shadow.paste((44,39,35,255),(x+4,y+23),alpha);bg=Image.alpha_composite(bg,shadow);bg.alpha_composite(item,(x,y))
d=ImageDraw.Draw(bg); font='/System/Library/Fonts/STHeiti Medium.ttc'; a=ImageFont.truetype(font,137); b=ImageFont.truetype(font,67)
d.polygon([(730,80),(1530,80),(1480,280),(680,280)],fill=(77,39,25,255)); d.text((760,105),'三档出水',font=a,fill='#fff6e9',stroke_width=1,stroke_fill='#fff6e9')
d.polygon([(850,292),(1496,292),(1474,377),(828,377)],fill=(170,101,62,255)); d.text((895,298),'按键切换',font=b,fill='#fff9ef')
bg.convert('RGB').save(p/'实拍花洒_广告候选.jpg',quality=95)

from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=P.parents[1]/'references/2026-10-31_同款商户电商参考'
for n in range(387,400):
 ref=Image.open(R/f'微信图片_20261031133902_{n}_2.jpg');final=Image.open(P/f'JPG/{n}.jpg');h=1000;w=round(h*final.width/final.height)
 out=Image.new('RGB',(w*2,h));out.paste(ref.resize((w,h),Image.Resampling.LANCZOS),(0,0));out.paste(final.resize((w,h),Image.Resampling.LANCZOS),(w,0));out.save(P/f'review/{n}-comparison.jpg',quality=94)
 final.thumbnail((360,640));final.save(P/f'review/{n}-mobile.jpg',quality=94)

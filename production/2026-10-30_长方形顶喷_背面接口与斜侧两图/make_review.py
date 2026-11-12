from pathlib import Path
from PIL import Image,ImageOps
import json
P=Path(__file__).resolve().parent
back=Image.open(P/'03_背面去盖接口_v2.jpg');side=Image.open(P/'04_正面斜侧20mm.jpg')
for im in [back,side]:im.load();assert im.size==(1600,1600)
canvas=Image.new('RGB',(1600,800));canvas.paste(back.resize((800,800)),(0,0));canvas.paste(side.resize((800,800)),(800,0));canvas.save(P/'两张审阅总览.jpg',quality=97)
# Actual final-image crop enlarged for inspection, not extra generated product image.
render_crop=back.crop((700,660,910,900));render_crop.resize((630,720)).save(P/'接口成图局部放大.jpg',quality=97)
photo=Image.open(P/'接口实拍裁切.jpg');canvas=Image.new('RGB',(1400,800),'white');canvas.paste(ImageOps.contain(photo,(700,800)),(0,0));canvas.paste(ImageOps.contain(render_crop,(700,800)),(700,0));canvas.save(P/'接口实拍与成图对照_左实拍右渲染.jpg',quality=97)
thumb=Image.new('RGB',(720,360));thumb.paste(back.resize((360,360)),(0,0));thumb.paste(side.resize((360,360)),(360,0));thumb.save(P/'手机宽度对照.jpg',quality=96)
print('REVIEW_FILES_READY')

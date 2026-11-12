from pathlib import Path
from PIL import Image,ImageOps
P=Path(__file__).resolve().parent
names=['05_浴室安装全貌_v2','06_安装喷面与红钮','07_浴室台面背部接口']
imgs=[Image.open(P/(n+'.jpg')) for n in names]
for im in imgs:im.load();assert im.size==(1600,1600)
canvas=Image.new('RGB',(2400,800),'white')
for i,im in enumerate(imgs):canvas.paste(im.resize((800,800)),(800*i,0))
canvas.save(P/'三张浴室场景总览.jpg',quality=97)
canvas.resize((1080,360)).save(P/'手机宽度审阅.jpg',quality=96)
src=ImageOps.exif_transpose(Image.open(P/'sources/微信图片_20261030154107_376_2.jpg'))
back=ImageOps.exif_transpose(Image.open(P/'sources/codex-clipboard-6fa807ac-653c-44f8-a3cc-2941c017e31e.jpg'))
canvas=Image.new('RGB',(1600,1600),'white')
for im,x,y in [(src,0,0),(imgs[1],800,0),(back,0,800),(imgs[2],800,800)]:
 tile=ImageOps.contain(im,(800,800));canvas.paste(tile,(x+(800-tile.width)//2,y+(800-tile.height)//2))
canvas.save(P/'原照与场景对照_左实拍右渲染.jpg',quality=97)
imgs[1].crop((350,500,1050,1200)).save(P/'喷面与红钮原尺寸局部.jpg',quality=97)
print('REVIEW_READY')

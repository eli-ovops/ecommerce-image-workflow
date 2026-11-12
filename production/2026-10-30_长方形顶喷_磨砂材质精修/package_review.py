from pathlib import Path
from PIL import Image,ImageOps
import json,hashlib,zipfile,shutil
P=Path(__file__).resolve().parent
old=P.parent/'2026-10-30_长方形顶喷_同网格暖金两图'
names=['01_银色完整顶喷','02_静态红钮近景_非拉出']
canvas=Image.new('RGB',(1600,1600),'white')
for row,name in enumerate(names):
 for col,path in enumerate([old/(name+'_v2.jpg'),P/(name+'_磨砂精修.jpg')]):
  im=Image.open(path);im.load();assert im.size==(1600,1600)
  canvas.paste(im.resize((800,800)),(col*800,row*800))
canvas.save(P/'前后对照.jpg',quality=96)
src=P.parent/'2026-10-30_长方形拉钮顶喷_完整建模'/'372-native-detail.jpg'
shutil.copy2(src,P/'372实拍原始细节.jpg')
im=Image.open(P/(names[1]+'_磨砂精修.jpg'))
canvas=Image.new('RGB',(1600,800),'white')
canvas.paste(ImageOps.fit(Image.open(src),(800,800)),(0,0))
canvas.paste(im.crop((400,400,1200,1200)),(800,0));canvas.save(P/'实拍与材质对照.jpg',quality=97)
print('COMPARISONS_READY')

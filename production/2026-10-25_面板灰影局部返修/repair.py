from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageChops
import json
import numpy as np
B=Path(__file__).resolve().parent;src=B.parent/'2026-10-25_广告节奏优化_细节精修/JPG/M02_下方按键操作.jpg';im=Image.open(src).convert('RGB');orig=im.copy();allmask=Image.new('L',im.size)
# Each tuple records spurious grey-ring center, ellipse radii, and nearby intact panel texture donor.
patches=[(663,156,15,15,704,186),(649,237,15,17,666,256),(1224,285,10,17,1193,302),(1211,366,14,21,1187,343),(1188,405,15,20,1158,413),(1094,514,15,14,1065,489),(1018,548,8,10,1014,520)]
patches=[(x,y,rx,ry,945,640) for x,y,rx,ry,_,_ in patches]
for x,y,rx,ry,sx,sy in patches:
 pad=4;w=2*(rx+pad)+1;h=2*(ry+pad)+1;arr=np.array(orig.crop((945-w//2,640-h//2,945+w//2+1,640+h//2+1))).astype(float);local=np.array(orig.crop((x-rx-5,y-ry-5,x+rx+6,y+ry+6))).astype(float);target=np.percentile(local.reshape(-1,3),40,axis=0);arr=(arr-arr.mean(axis=(0,1)))*1.4+target;p=Image.fromarray(np.clip(arr,0,255).astype('uint8'));mask=Image.new('L',(w,h));ImageDraw.Draw(mask).ellipse((pad,pad,w-pad-1,h-pad-1),fill=255);mask=mask.filter(ImageFilter.GaussianBlur(1.4));im.paste(p,(x-w//2,y-h//2),mask);layer=Image.new("L",im.size);layer.paste(mask,(x-w//2,y-h//2));allmask=ImageChops.lighter(allmask,layer)
im.save(B/'M02_下方按键操作_候选.jpg',quality=98,subsampling=0);im.save(B/'review/working-lossless.png');allmask.save(B/'review/repair-mask.png');(B/'patches.json').write_text(json.dumps({'method':'local texture cloning, no nozzle synthesis','patches':patches,'source':str(src),'scope':'7 spurious grey rings/drag marks; no real white nozzle or outer black pore intentionally masked'},ensure_ascii=False,indent=2))
for name,box in [('right',(1100,240,1254,470)),('bottom',(985,485,1120,570)),('left',(625,125,715,260))]:
 a=orig.crop(box);b=im.crop(box);w=a.width*3;h=a.height*3;out=Image.new('RGB',(w*2+12,h),'white');out.paste(a.resize((w,h)),(0,0));out.paste(b.resize((w,h)),(w+12,0));out.save(B/'review'/('before-after-'+name+'.jpg'),quality=98,subsampling=0)

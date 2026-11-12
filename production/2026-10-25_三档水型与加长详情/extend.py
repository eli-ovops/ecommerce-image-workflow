from pathlib import Path
import json,hashlib,zipfile
from PIL import Image,ImageOps,ImageDraw
B=Path(__file__).resolve().parent
exec((B/'build.py').read_text().split('# Large product')[0])
m=json.loads((B/'manifest.json').read_text());assets=[a for a in m['assets'] if a['id'] not in ['L01','M04','W01','W02','W03','D06','D07','D08']]
for id,k,t,sub,tail in [('W01','normal','普通出水','常规档',95),('W02','mixed','混合出水','水柱与喷雾结合',97),('W03','mist','喷雾出水','喷雾档',96)]:
 im=Image.new('RGB',(N,1600),'#f7f0e5');im.paste(read(S/(k+'.png')),(0,346));title(im,t,sub,size=110);save(id,t,im,['R023','A016','A017','A018'],f'用户确认实拍尾号{tail}；实拍引导生成环境调整图，非原水流像素硬锁定。')
im=Image.new('RGB',(N,2340),'#f7f0e5');title(im,'三档出水','下方按键切换',size=110)
for i,(k,t) in enumerate([('normal','普通出水'),('mixed','混合出水'),('mist','喷雾出水')]):
 p=read(S/(k+'.png'));p=ImageOps.fit(p,(970,620),centering=(.5,.40));y=400+i*640;im.paste(p,(284,y));ImageDraw.Draw(im).rectangle((0,y,284,y+620),fill='#835336');text(im,40,y+80,76,'0'+str(i+1),'#f1d2a6');text(im,35,y+230,51,t[:2],'#fff9ed');text(im,35,y+305,51,t[2:],'#fff9ed')
save('M04','三档水型总览',im,['R023','A016','A017','A018'],'95普通96喷雾97混合，用户确认；不使用98–100推断')
# Detail chapters with large photographs, no tiny footnotes.
im=Image.new('RGB',(N,1600),'#f7f0e5');title(im,'面板细节','中央红钮 · 白色孔位',size=110);photo(im,'SIL005',(0,360,N,1240),(800,600,3500,3300));save('D06','面板近看',im,['A011','A025'],'原实拍面板裁切，保留真实孔位')
im=bg();im=im.resize((N,1600));p=Image.open(G/'silver-cutout-v003.png').convert('RGBA');p=p.crop((0,int(p.height*.31),p.width,int(p.height*.86)));p=ImageOps.contain(p,(1080,1250),Image.Resampling.LANCZOS);im.paste(p,(300,350),p);ImageDraw.Draw(im).rectangle((0,0,N,350),fill='#f7f0e5');title(im,'头柄连续过渡','银色外观细节',size=95);save('D07','头柄连接细节',im,['A023','R031'],'复用已有商品生成层，局部展示，非新增几何')
im=bg();im=im.resize((N,1600));prod(im,'rear',1850,300,390,-6);title(im,'背面弧线','银色背壳',size=110);save('D08','背面细节',im,['A023'],'复用现有背面商品层，保持比例')
seq=['M01','M05','M06','D01','W01','W02','W03','M02','D03','M03','D04','D06','D07','D08','D02','D05'];tiles=[]
for id in seq:
 a=next(a for a in assets if a['id']==id);p=read(OUT/a['file']);tiles.append(p.resize((1000,round(p.height*1000/p.width)),Image.Resampling.LANCZOS))
im=Image.new('RGB',(1000,sum(p.height for p in tiles)),'white');y=0
for p in tiles:im.paste(p,(0,y));y+=p.height
save('L01','三档加长详情',im,[],'16章节无重复图片串接；不添加无依据过滤抗菌材料承诺')
m.update(assets=assets,status='EXPORTED_FOR_USER_REVIEW',water='用户已确认95普通96喷雾97混合；三张为实拍引导生成候选，外形水流人工比对，非像素硬锁定',long_sequence=seq,long_size=list(im.size),customer_acceptance='待审')
(B/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
newids=['W01','W02','W03','M04','D06','D07','D08'];sheet=Image.new('RGB',(1400,1150),'#eee')
for i,id in enumerate(newids):
 a=next(a for a in assets if a['id']==id);p=read(OUT/a['file']);p.thumbnail((340,510));x=i%4*350;y=i//4*570;sheet.paste(p,(x,y));text(sheet,x+5,y+520,22,id+' '+a['name'])
sheet.save(B/'新增图审阅.jpg',quality=95)
# Long overview in four readable columns.
a=assets[-1];p=read(OUT/a['file']);sh=Image.new('RGB',(1600,2100),'white');h=(p.height+3)//4
for i in range(4):q=p.crop((0,i*h,1000,min((i+1)*h,p.height)));q.thumbnail((400,2100));sh.paste(q,(i*400,0))
sh.save(B/'长图分段预览.jpg',quality=94)
print(len(assets),im.size)

from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,shutil,hashlib,zipfile,html
B=Path(__file__).resolve().parent;R=B.parents[1];OLD=R/'production/2026-10-25_三档水型与加长详情';S=OLD/'sources';G=R/'production/2026-10-24_完整电商套图/generated';OUT=B/'JPG';N=1254
F='/System/Library/Fonts/STHeiti Medium.ttc';cream='#f7f0e5';brown='#835336';ink='#211a17';assets=[]
old=json.loads((OLD/'manifest.json').read_text());lookup={a['id']:a for a in old['assets']}
def read(p):return ImageOps.exif_transpose(Image.open(p)).convert('RGB')
def txt(im,x,y,s,t,c=ink):ImageDraw.Draw(im).text((x,y),t,font=ImageFont.truetype(F,s),fill=c,anchor='lt')
def head(im,t,x=54,y=55,size=100,c=ink):
 p=Image.new('RGBA',(1200,170));d=ImageDraw.Draw(p);d.text((20,8),t,font=ImageFont.truetype(F,size),fill=c,anchor='lt',stroke_width=3);p=p.transform(p.size,Image.Transform.AFFINE,(1,.10,-10,0,1,0),Image.Resampling.BICUBIC);im.paste(p,(x-15,y),p)
def save(id,name,im,refs,note):
 p=OUT/(id+'_'+name+'.jpg');im.save(p,quality=95,subsampling=0);assets.append(dict(id=id,name=name,file=p.name,size=list(im.size),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),refs=refs,notes=note,changed=True))
def reuse(id):
 a=lookup[id].copy();src=OLD/'JPG'/a['file'];shutil.copy2(src,OUT/a['file']);a['changed']=False;a['source']=str(src);assets.append(a)
def layer(key,h):
 p=Image.open(G/(key+'-cutout-v003.png')).convert('RGBA');return p.resize((round(p.width*h/p.height),h),Image.Resampling.LANCZOS)
def rect(im,box,c):ImageDraw.Draw(im).rectangle(box,fill=c)
# Keep accepted identity and original skin pixels. This is the leading hero.
reuse('M05')
# Larger product on a clean editorial field; three strong mode words instead of empty room.
im=Image.new('RGB',(N,N),cream);bath=read(S/'bath.png').crop((450,0,1254,1254));bath=ImageOps.fit(bath,(760,N));im.paste(bath,(494,0));p=layer('silver',1270);im.paste(p,(680,150),p)
head(im,'三档出水',size=126);txt(im,64,255,49,'下方按键切换',brown)
for i,t in enumerate(['普通','混合','喷雾']):
 y=490+i*180;txt(im,65,y,41,'0'+str(i+1),brown);txt(im,155,y-12,91,t);rect(im,(65,y+115,455,y+118),'#cfbca4')
save('M01','三档主图',im,['R001','R004','R023'],'加大商品与模式标题；仅对现有生成商品层等比放置，无新几何重绘')
# Existing factual operation and real pin imagery preserved.
for id in ['M02','M03','M06','K01','K02','K03']:reuse(id)
# Mode comparison: same square viewport, no crop of the head or water origin.
im=Image.new('RGB',(N,3260),cream);head(im,'三种水型 一眼看清',size=91);txt(im,62,205,49,'普通 / 混合 / 喷雾',brown)
for i,(key,label) in enumerate([('normal','普通出水'),('mixed','混合出水'),('mist','喷雾出水')]):
 y=330+i*960;p=read(S/(key+'.png')).resize((900,900),Image.Resampling.LANCZOS);im.paste(p,(354,y));rect(im,(0,y,354,y+900),brown);txt(im,48,y+65,82,'0'+str(i+1),'#ead3ad');txt(im,48,y+265,78,label[:2],'white');txt(im,48,y+370,78,label[2:],'white')
save('M04','三档同尺度对照',im,['R023','A016','A017','A018'],'复用95普通96喷雾97混合对应的既有实拍引导候选；同900方形视窗，不重绘不补水。源机位透视不同不伪装相同机位。')
# A neutral selection page avoids the repeated bathroom photograph behind three cutouts.
im=Image.new('RGB',(N,1450),cream);head(im,'三色 自在搭配',size=112);txt(im,60,230,46,'银色 / 黑色 / 枪灰色',brown)
for x,key,col in [(35,'silver','银色'),(448,'black','黑色'),(861,'gunmetal','枪灰色')]:
 rect(im,(x,340,x+358,1270),'#ece2d4');p=layer(key,1000);im.paste(p,(x+25,370),p);rect(im,(x,1250,x+358,1450),cream);txt(im,x+70,1315,62,col)
save('D01','三色搭配',im,['A008'],'使用三色各自商品层不换色；一致高度、展示台式色块与大色名，未显示接口')
# Front and rear together, plus ONE neck crop integrated into the page.
im=Image.new('RGB',(N,1730),cream);head(im,'正面到背面',size=124);txt(im,60,240,52,'细节  一起看',brown)
for x,key,label in [(65,'silver','正面'),(665,'rear','背面')]:
 p=layer(key,1150);im.paste(p,(x,400),p);txt(im,x+130,340,50,label,brown)
# Intentional clean lower crop with a full-width feature band, no floating detached fragments.
rect(im,(0,1490,N,1730),brown);txt(im,60,1580,65,'中央红钮  ·  下方切档按键','#fff7e9')
save('D02','正背一页看清',im,['A022','A023'],'合并旧D02 D07 D08的外观任务；等比保留现有前后商品层。未新增内部结构/材质断言')
reuse('D04')
# Product information on a legible clean field, no cutout repetition.
im=Image.new('RGB',(N,1550),cream);head(im,'选购信息',size=135);txt(im,65,245,56,'手持花洒 · 单花洒',brown)
for i,(a,b) in enumerate([('颜色','银色 / 黑色 / 枪灰色'),('三档出水','普通 / 喷雾 / 混合'),('下方按键','切换出水档位'),('中央红钮','手动按压辅助除垢'),('售卖范围','单花洒，不含软管与支架')]):
 y=420+i*210;rect(im,(55,y-20,N-55,y+155),'#ede1d0' if i%2==0 else cream);txt(im,85,y+15,53,a,brown);txt(im,85,y+87,53,b)
save('D05','选购信息',im,['A032','A033'],'集中必要交易信息，正文53px；不再用细小脚注，不填写未知参数')
# Mode singles retain full-frame original candidate pixels through one uniform resize.
for id,key,label,sub,tail in [('W01','normal','普通出水','常规水柱',95),('W02','mixed','混合出水','水柱与喷雾结合',97),('W03','mist','喷雾出水','六处喷雾点位',96)]:
 im=Image.new('RGB',(N,1540),cream);p=read(S/(key+'.png'));im.paste(p,(0,286));head(im,label,size=119);txt(im,64,200,48,sub,brown);save(id,label,im,['R023','A016','A017','A018'],f'对应实拍{tail}；现有生成水型图片不重绘。真实孔位/水流仍待客户复核')
reuse('D06')
# Preserve purposeful sequence, avoid consecutive duplicates. Mode overview is separate comparison asset.
seq=['M05','M01','D01','W01','W02','W03','M02','M03','D04','D06','D02','M06','D05']
parts=[]
for id in seq:
 a=next(a for a in assets if a['id']==id);p=read(OUT/a['file']);parts.append(p.resize((1000,round(p.height*1000/p.width)),Image.Resampling.LANCZOS))
long=Image.new('RGB',(1000,sum(p.height for p in parts)),cream);y=0
for p in parts:long.paste(p,(0,y));y+=p.height
save('L01','广告节奏完整详情',long,[],'13章；人物开场→三档→颜色→水型→操作→原拍细节→正背→静物→信息。删重复功能页，未为长度添加无事实卖点')
manifest={'status':'AWAITING_VISUAL_REVIEW','customer_acceptance':'待审','baseline':str(OLD),'assets':assets,'long_sequence':seq,'long_size':list(long.size),'reference_read_receipt':'production/2026-10-22_参考重构/reference-map.md:31-37','limitations':['产品层与水型为既有实拍引导生成图，不是3D或原像素硬锁定','原生人物图未改变，未重新生成人物','水型源机位不同；同尺寸视窗不等于同透视重建'],'merged':{'D03':'M02+M03','D07':'D02','D08':'D02'}}
(B/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
for start in range(0,len(assets)-1,6):
 batch=assets[start:start+6];sh=Image.new('RGB',(1500,1300),'#ddd')
 for j,a in enumerate(batch):
  p=read(OUT/a['file']);p.thumbnail((490,600));x=j%3*500;y=j//3*650;sh.paste(p,(x,y));txt(sh,x+10,y+610,25,a['id']+' '+a['name'])
 sh.save(B/'review'/f'sheet-{start//6+1}.jpg',quality=94)
print(len(assets),long.size)

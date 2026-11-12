from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageFilter
import json,hashlib,math
import numpy as np
B=Path(__file__).resolve().parent; ROOT=B.parents[1]; G=B/'generated'
IDX=json.loads((B/'recipes/source-index.json').read_text()); REFS=IDX['refs']; PHOTOS=IDX['photos']
FONT='/System/Library/Fonts/STHeiti Medium.ttc'; NORMAL='/System/Library/Fonts/Hiragino Sans GB.ttc'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):
 p=Path(p);return {'path':str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),'sha256':sha(p)}
def read(p):return ImageOps.exif_transpose(Image.open(p)).convert('RGB')
def txt(im,xy,t,s=64,c='#112c4c',bold=True):
 im.info.setdefault('copy',[]).append(t);ImageDraw.Draw(im).text(xy,t,font=ImageFont.truetype(FONT if bold else NORMAL,s),fill=c,anchor='lt',stroke_width=1 if bold else 0)
def rect(im,box,c,r=0):
 d=ImageDraw.Draw(im);d.rounded_rectangle(box,radius=r,fill=c) if r else d.rectangle(box,fill=c)
def grad(w,h,top=(107,159,208),bot=(221,238,249)):
 a=np.linspace(0,1,h)[:,None,None];rgb=np.array(top)[None,None,:]*(1-a)+np.array(bot)[None,None,:]*a
 return Image.fromarray(np.broadcast_to(rgb,(h,w,3)).astype('uint8'))
def fit(im,box,p,align=(.5,.5),crop=None,log=None):
 src=read(p);orig=src.size
 if crop:src=src.crop(tuple(crop))
 x,y,w,h=box;s=max(w/src.width,h/src.height);rs=(round(src.width*s),round(src.height*s));v=src.resize(rs,Image.Resampling.LANCZOS);off=(round((v.width-w)*align[0]),round((v.height-h)*align[1]));v=v.crop((off[0],off[1],off[0]+w,off[1]+h));im.paste(v,(x,y))
 if log is not None:
  layer_dir=G/'source-layers';layer_dir.mkdir(exist_ok=True);key=hashlib.sha256((str(p)+str(box)+str(crop)+str(align)).encode()).hexdigest()[:16];lp=layer_dir/(key+'.png');v.save(lp)
  log.append({'resampled_crop_layer':rec(lp),'source':rec(p),'exif_display_size':orig,'source_crop':crop,'uniform_scale':s,'scaled_crop_offset':off,'destination':[x,y,w,h],'operation':'uniform cover crop; source RGB retained through resampling'})
def cutout(p,name):
 out=G/(name+'-cutout-v003.png')
 if out.exists():return out
 src=read(p);a=np.array(src);gray=a.min(2);ob=Image.fromarray(np.where(gray>214,255,0).astype('uint8')).copy();ImageDraw.floodfill(ob,(0,0),128,thresh=0)
 # All enclosed highlight pixels remain opaque; only exterior white connected to the canvas is removed.
 mask=Image.fromarray(np.where(np.array(ob)==128,0,255).astype('uint8'))
 # Alpha-only cleanup: below lower barrel, bound each thread row by dark edge span.
 m=np.array(mask)
 for yy in range(1148,src.height):
  xs=np.where(gray[yy,500:740]<155)[0]+500;m[yy,:]=0
  if len(xs):m[yy,max(0,int(xs.min())-1):min(src.width,int(xs.max())+2)]=255
 mask=Image.fromarray(m).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.35))
 # Original RGB remains unchanged, only mask alpha is cleaned.

 bb=mask.getbbox();m=np.array(mask);ys=np.where((m>0).sum(1)>8)[0];
 mask.save(G/(name+'-cutout-v003-mask.png'));rgba=src.convert('RGBA');rgba.putalpha(mask);rgba=rgba.crop(bb);rgba.save(out)
 (G/(name+'-cutout-v003-evidence.json')).write_text(json.dumps({'source':rec(p),'threshold_exterior_min_rgb':214,'crop_bbox':bb,'tail_cleanup':{'y_start':1148,'x_search':[500,740],'dark_threshold':155,'alpha_only':True,'edge_erode_px':1},'method':'floodfill exterior only; original RGB unchanged; alpha mask; no AI product regeneration','output':rec(out)},ensure_ascii=False,indent=2));return out
def product(im,p,box,log,angle=0):
 src=Image.open(p).convert('RGBA');w,h=box[2:];s=min(w/src.width,h/src.height);src=src.resize((round(src.width*s),round(src.height*s)),Image.Resampling.LANCZOS)
 if angle:src=src.rotate(angle,Image.Resampling.BICUBIC,expand=True)
 x=round(box[0]+(w-src.width)/2);y=round(box[1]+(h-src.height)/2);im.paste(src,(x,y),src)
 log.append({'source':rec(p),'uniform_scale':s,'rotation_deg':angle,'destination_top_left':[x,y],'resampled_size':list(src.size),'operation':'alpha composite existing product RGB, no recolor or local geometry edits'})
def save(id,im,refs,role,sku,claims,layers,notes=''):
 ver='v005' if id in ['M06','M04','D04','D07','D08','D09'] else 'v004';p=G/f'{id}-{ver}.png';j=G/f'{id}-{ver}.jpg';im.save(p);im.save(j,quality=96,subsampling=0)
 d={'id':id,'role':role,'sku':sku,'refs_actual_viewed':[{'id':r,**rec(ROOT/REFS[r])} for r in refs],'actual_inputs':list({l['source']['path']:l['source'] for l in layers}.values()),'claims':claims,'copy':im.info.get('copy',[]),'source_files':list({l['source']['path']:l['source'] for l in layers}.values()),'source_layers':layers,'transform':'See source_layers; all photo transforms uniform scaling/cropping; no nonuniform product stretch','output':rec(j),'working':rec(p),'dims':list(im.size),'notes':notes,'status':'AWAITING_INDEPENDENT_VISUAL_REVIEW'}
 (B/'recipes'/f'{id}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2));sync();print(id,j,flush=True)
def sync():
 assets=[json.loads(p.read_text()) for p in sorted((B/'recipes').glob('*.json')) if p.name!='source-index.json'];(B/'design-output.json').write_text(json.dumps({'assets':assets,'generation_budget':6,'water_policy':'actual water photographs, no per-image mode identification','requested_model':'gpt-6-astra','requested_effort':'high','actual_model':'UNKNOWN','actual_effort':'UNKNOWN'},ensure_ascii=False,indent=2))
SIL=ROOT/'production/2026-10-24_实拍主导主图/generated/R01-v003-composite.png';BLK=ROOT/'production/2026-10-24_实拍主导续作/generated/K01-v001-native.png';GMT=ROOT/'production/2026-10-24_实拍主导续作/generated/K02-v001-native.png'
CUT={k:cutout(p,k) for k,p in [('silver',SIL),('black',BLK),('gunmetal',GMT)]}

def shadow(im,box):
 layer=Image.new('RGBA',im.size,(0,0,0,0));ImageDraw.Draw(layer).ellipse(box,fill=(22,31,42,90));layer=layer.filter(ImageFilter.GaussianBlur(18));im.paste(layer,(0,0),layer)

def first():
 for id,col,key,r in [('K01','银色','silver','A002'),('K02','黑色','black','A003'),('K03','枪灰色','gunmetal','A004')]:
  im=grad(1600,1600);d=ImageDraw.Draw(im);d.polygon([(0,1150),(750,350),(1600,250),(1600,1600),(0,1600)],fill='#c3def1');d.ellipse((-700,730,1530,2440),outline='#eaf6ff',width=34);ls=[]
  txt(im,(95,95),'三档出水',118,'#fff');txt(im,(100,250),'手持花洒',74,'#fff');rect(im,(98,363,640,443),'#1179d4',40);txt(im,(126,381),'下方按键 · 切换三档',38,'#fff')
  for y,t in [(535,'常规出水'),(655,'喷雾出水'),(775,'混合出水')]:rect(im,(100,y,555,y+93),'#eaf6ff',16);txt(im,(143,y+22),t,48,'#1d5183')
  txt(im,(100,1100),col,120,'#173c60');txt(im,(105,1265),'单花洒',50,'#285e86');txt(im,(105,1345),'中央红钮 · 手动按压除垢',32,'#285e86')
  product(im,CUT[key],(690,115,820,1390),ls);save(id,im,[r],'SKU 广告',col,['三档出水','常规出水','喷雾出水','混合出水','单花洒','下方按键切档','中央红钮手动按压除垢'],ls,'复用本色已核商品像素；同版蓝色定位、独立本色图层；未复刻参考未知滤芯/尺寸')
 # warm room 2/3 plus white product column
 im=Image.new('RGB',(1600,1600),'white');ls=[];fit(im,(0,0,1065,1600),G/'warm-room-native.png',(.42,.5),log=ls);rect(im,(1065,0,1600,1600),'#fff')
 txt(im,(70,88),'日常淋浴',92,'#fff');txt(im,(70,204),'三档随心选',92,'#fff');shadow(im,(280,1225,470,1270));product(im,CUT['silver'],(90,270,950,1000),ls,angle=-22)
 product(im,CUT['silver'],(1130,440,400,850),ls);txt(im,(1130,95),'银色',74);txt(im,(1130,190),'单花洒',42);rect(im,(1105,1435,1560,1530),'#34241c');txt(im,(1142,1460),'常规 · 喷雾 · 混合',31,'#fff')
 save('M06',im,['R008'],'暖浴室场景＋白栏单品','银色',['银色','单花洒','三档手持花洒','常规','喷雾','混合'],ls,'左2/3暖浴室、右1/3白栏完整商品；移除人物与未售配件')
 # cold hero with two bottom details
 im=Image.new('RGB',(1600,2000));ls=[];fit(im,(0,0,1600,1650),G/'blue-room-native.png',log=ls);txt(im,(85,100),'三档随心选',112,'#143b61');txt(im,(88,240),'日常好切换',112,'#143b61');txt(im,(94,405),'常规 / 喷雾 / 混合',40,'#315d84');shadow(im,(690,1450,870,1492));product(im,CUT['silver'],(390,400,1110,1100),ls,angle=-16)
 rect(im,(0,1650,1600,2000),'#eef7ff');fit(im,(50,1690,710,230),SIL,crop=(420,230,800,420),log=ls);fit(im,(820,1690,730,230),SIL,crop=(500,570,770,710),log=ls)
 rect(im,(50,1885,760,1960),'#173c60');txt(im,(84,1905),'中央红钮 · 手动按压除垢',34,'#fff');rect(im,(820,1885,1550,1960),'#173c60');txt(im,(858,1905),'下方按键 · 切换三档',34,'#fff')
 save('D01',im,['A006','A007','A009','A010'],'冷蓝浴室首屏＋双细节带','银色',['三档','常规','喷雾','混合','中央红钮手动按压除垢','下方按键切换三档'],ls,'人物停用，产品越框大主体；已验实拍引导的生成商品层复用，环境为新生成；非原实拍商品像素')


P=lambda k:ROOT/PHOTOS[k]
PANEL=ROOT/'production/2026-10-24_实拍主导主图/generated/R03-v001-native.png'
def actual(im,box,id,ls,crop=None):
 fit(im,box,P(id),crop=crop,log=ls);ls[-1]['source_kind']='original_real_photo';ls[-1]['photo_id']=id;ls[-1]['ai_redraw']=False

def states():
 im=grad(1600,1600,(39,23,15),(117,78,43));ls=[]
 fit(im,(565,70,965,1315),P('SIL007'),crop=(0,0,3024,3500),log=ls);ls[-1].update(source_kind='original_real_photo',photo_id='SIL007',ai_redraw=False)
 txt(im,(70,95),'三档出水',90,'#fff');txt(im,(74,225),'日常随心选',58,'#e6c496')
 for y,t in [(435,'常规出水'),(655,'喷雾出水'),(875,'混合出水')]:rect(im,(65,y,515,y+144),'#ead0a2',24);txt(im,(112,y+44),t,54,'#352116')
 txt(im,(74,1170),'下方按键切档',43,'#fff');rect(im,(0,1405,1600,1600),'#2e1b12');txt(im,(76,1455),'出水实拍',72,'#fff');txt(im,(650,1482),'常规 / 喷雾 / 混合',36,'#edd6b5')
 save('M04',im,['R002','A036'],'暖棕真实出水主图','银色',['三档出水','常规出水','喷雾出水','混合出水','下方按键切档','出水实拍'],ls,'原生SIL007水流/局部手；不标具体模式，不重绘水流；左三名称不与照片一对一')
 im=Image.new('RGB',(1600,1600));ls=[];fit(im,(0,0,1600,1600),PANEL,log=ls)
 for y,t in [(80,'中央红钮'),(190,'手动按压'),(300,'辅助除垢')]:txt(im,(65,y),t,74,'#113450')
 rect(im,(53,813,526,1423),'#fff',12);actual(im,(65,825,449,520),'SIL006',ls,crop=(0,600,4284,5000));rect(im,(65,1345,514,1410),'#164a77');txt(im,(91,1361),'按压状态 · 实拍',35,'#fff')
 rect(im,(0,1480,1600,1600),'#0b345b');txt(im,(80,1516),'红钮按压除垢   /   下方按键切档',56,'#fff')
 save('M05',im,['A035','A025'],'蓝白巨面板除垢广告','银色',['中央红钮','手动按压辅助除垢','下方按键切档','按压状态实拍'],ls,'大主体复用实拍引导生成商品素材；小窗为SIL006原实拍，红针与手未AI重画')
 im=Image.new('RGB',(1600,2200),'#eef7ff');ls=[];txt(im,(85,75),'看见真实出水',106);txt(im,(90,233),'常规 / 喷雾 / 混合',49,'#266da8')
 for y,num,id,crop in [(360,'01','SIL007',(0,300,3024,3500)),(1230,'02','SIL008',(0,350,3024,3550))]:
  rect(im,(60,y,1540,y+805),'#0c1721',30);actual(im,(255,y+30,1255,745),id,ls,crop);rect(im,(60,y,265,y+805),'#116ec0',24);txt(im,(94,y+55),num,83,'#fff');txt(im,(90,y+180),'实拍',40,'#fff');txt(im,(90,y+240),'视角',40,'#fff')
 txt(im,(85,2090),'下方按键 · 切换三档',35,'#365d7b',False)
 save('D04',im,['A012','A013','A016','A017','A018','R023'],'真实出水章节','银色',['出水实拍','常规','喷雾','混合'],ls,'01/02仅实拍视角序号；两原照均保留源水流，不生成或推定档位')
 im=grad(1600,2000,(228,243,253),(186,215,235));ls=[];txt(im,(80,80),'手动按压除垢',110);txt(im,(85,240),'找到中央红钮，按住后观察孔位',46,'#376583')
 for x,num,t in [(80,'01','找到红钮'),(590,'02','手动按住'),(1100,'03','观察孔位')]:
  rect(im,(x,355,x+420,490),'#176eaf',18);txt(im,(x+26,390),num,58,'#fff');txt(im,(x+125,399),t,40,'#fff')
 for x,id,t,c in [(65,'SIL005','未按压状态',(0,0,4284,5000)),(825,'SIL006','按住中央红钮',(0,0,4284,5000))]:
  actual(im,(x,560,710,1050),id,ls,c);rect(im,(x,1610,x+710,1730),'#163e60');txt(im,(x+65,1645),t,50,'#fff')
 txt(im,(83,1805),'按压中央红钮',52);txt(im,(85,1900),'辅助清理出水孔',34,'#376583',False)
 save('D07',im,['A024','A025','A026'],'手动除垢步骤与原生按压状态','银色',['中央红钮手动按压除垢','未按压状态','按住中央红钮'],ls,'A024状态排布、A025大面板、A026上下细节方法；过滤/耐久/永久不堵文案不采用；只复用SIL005/006原照')

BACKPAIR=ROOT/'production/2026-10-24_实拍主导续作/generated/R06-v002-native.png'
def more_details():
 # Three unequal heights, photo-album framing, colors are separate source products.
 im=grad(1600,2000,(159,189,219),(230,242,251));ls=[];txt(im,(85,85),'三色可选',110,'#fff');txt(im,(91,234),'把喜欢的颜色带进浴室',46,'#eff8ff');rect(im,(65,400,1535,1840),'#fff',30);rect(im,(95,440,1505,1740),'#c2d9e9')
 product(im,CUT['gunmetal'],(80,760,530,920),ls,12);product(im,CUT['silver'],(540,445,540,1040),ls,-5);product(im,CUT['black'],(1030,880,450,830),ls,-14)
 for x,y,t in [(160,1645,'枪灰色'),(685,1435,'银色'),(1210,1695,'黑色')]:rect(im,(x-20,y-12,x+200,y+65),'#fff',12);txt(im,(x,y),t,44)
 txt(im,(110,1780),'银色  /  黑色  /  枪灰色',44);save('D02',im,['A008'],'三色错落相册','三色',['银色','黑色','枪灰色'],ls,'各色独立已验生成商品层；没有银色换色；A008高低错落白框节奏')
 # Asymmetric five image windows, same hierarchy as A011/R017.
 im=Image.new('RGB',(1600,2100),'#e9f4fc');ls=[];txt(im,(75,78),'细节，看得见',110);txt(im,(80,235),'从出水到按键，逐一了解',43,'#3e6887')
 actual(im,(60,380,900,1030),'SIL009',ls,crop=(0,500,3024,3600));rect(im,(60,1330,960,1410),'#123e60');txt(im,(90,1352),'出水实拍',42,'#fff')
 actual(im,(995,380,545,450),'SIL005',ls,crop=(1350,1500,2850,3000));rect(im,(995,755,1540,830),'#2469a0');txt(im,(1025,776),'中央红钮',40,'#fff')
 actual(im,(995,865,545,545),'SIL005',ls,crop=(800,650,2400,2050));rect(im,(995,1330,1540,1410),'#2469a0');txt(im,(1025,1352),'白色孔位',40,'#fff')
 fit(im,(60,1450,710,520),SIL,crop=(510,550,740,760),log=ls);fit(im,(810,1450,730,520),BACKPAIR,crop=(700,110,1100,580),log=ls)
 for x,t in [(60,'下方切档按键'),(810,'背面外观')]:rect(im,(x,1890,x+710,1970),'#123e60');txt(im,(x+35,1912),t,40,'#fff')
 save('D03',im,['A011','R017'],'五窗细节总览','银色',['出水实拍','中央红钮','白色孔位','下方切档按键','背面外观'],ls,'保留不等大五窗；取消参考滤芯、机械、倍数。水窗/红钮/孔位为原实拍，其他已验生成商品局部')
 # Real location, no invented lower-key pressed photo or fixed cycle direction.
 im=grad(1600,2000,(229,243,252),(180,210,232));ls=[];txt(im,(78,72),'切档，找下方按键',101);txt(im,(84,221),'三种出水，按需选择',46,'#356b91')
 fit(im,(55,420,930,1480),PANEL,crop=(420,480,1020,1254),log=ls)
 for yy,num,title,sub in [(520,'01','找到下方按键','位于面板下方'),(910,'02','按下按键','切换出水档位'),(1300,'03','选择所需','常规 / 喷雾 / 混合')]:
  rect(im,(1040,yy,1540,yy+280),'#f5fbff',22);txt(im,(1080,yy+35),num,66,'#1978bd');txt(im,(1080,yy+125),title,50);txt(im,(1085,yy+209),sub,30,'#49718b')
 rect(im,(1040,1695,1540,1875),'#164c78',20);txt(im,(1080,1730),'中央红钮用于',32,'#fff');txt(im,(1080,1790),'手动按压除垢',36,'#fff')
 save('D05',im,['A014','A015','A028','R032'],'下方按键定位与操作','银色',['下方按键切档','常规','喷雾','混合','中央红钮手动按压除垢'],ls,'复用已验生成面板/下键；不画按下动作，不写固定循环顺序；参考A028/R032仅借步骤与外部定位')
 # Rear full hero with three real exterior details.
 backsrc=G/'rear-source-crop.png'
 if not backsrc.exists():read(BACKPAIR).crop((665,58,1135,1157)).save(backsrc)
 backcut=cutout(backsrc,'rear')
 im=grad(1600,2100,(215,235,250),(126,169,205));ls=[];txt(im,(78,80),'侧背之间',108);txt(im,(82,225),'看见连续的外观线条',49,'#315e82');product(im,backcut,(630,480,920,1490),ls,-5)
 for yy,title,source,crop in [(430,'头部侧壁',SIL,(710,130,865,470)),(960,'侧面实拍',P('SIL004'),(1600,200,2750,4550)),(1490,'头颈过渡',BACKPAIR,(720,380,1090,710))]:
  rect(im,(65,yy,565,yy+460),'#f7fbff',12);fit(im,(80,yy+15,470,365),source,crop=crop,log=ls);rect(im,(80,yy+380,550,yy+445),'#174e7b');txt(im,(110,yy+394),title,36,'#fff')
 save('D06',im,['A023','A027','R031'],'外观侧背大景与三局部窗','银色',['头部侧壁','侧面实拍','头颈过渡'],ls,'大背面来自本轮已验R06生成图，不用被否定旧侧面；SIL004侧窗为原实拍含原局部手；取消参考滤芯/喷枪/软管')

ROCK=ROOT/'production/2026-10-24_实拍主导主图/generated/R02-v002-composite.png'
def contain_photo(im,box,p,crop,ls):
 src=read(p).crop(crop);x,y,w,h=box;sc=min(w/src.width,h/src.height);v=src.resize((round(src.width*sc),round(src.height*sc)),Image.Resampling.LANCZOS);xx=x+(w-v.width)//2;yy=y+(h-v.height)//2;rect(im,(x,y,x+w,y+h),'#fff');im.paste(v,(xx,yy));fp=G/'source-layers'/('contain-'+hashlib.sha256((str(p)+str(crop)+str(box)).encode()).hexdigest()[:16]+'.png');v.save(fp);ls.append({'source':rec(p),'source_kind':'original_real_photo','source_crop':crop,'uniform_scale':sc,'destination':[xx,yy,*v.size],'container_box':box,'resampled_crop_layer':rec(fp),'operation':'uniform contain original photo crop; no AI redraw'})

def last_designs():
 im=Image.new('RGB',(1600,1600),'#f7f0e6');ls=[];rect(im,(0,0,1600,320),'#342218');txt(im,(80,65),'三档出水 · 双键分工',105,'#fff');txt(im,(85,218),'常规 / 喷雾 / 混合',44,'#dfbf8c')
 for x in [65,565,1065]:rect(im,(x,390,x+470,1490),'#4a2f1e',20)
 fit(im,(80,405,440,820),ROCK,crop=(380,20,1100,1150),log=ls)
 fit(im,(580,405,440,820),PANEL,crop=(470,650,950,1254),log=ls)
 actual(im,(1080,405,440,820),'SIL006',ls,crop=(1000,1300,3400,4800))
 for x,a,b in [(65,'三档出水','常规 / 喷雾 / 混合'),(565,'下方按键','按键切换三档'),(1065,'中央红钮','手动按压除垢')]:
  txt(im,(x+40,1285),a,68,'#fff');txt(im,(x+40,1390),b,32,'#ebd3ad')
 save('M08',im,['R012'],'棕金三竖卡功能广告','银色',['三档出水','常规','喷雾','混合','下方按键切换三档','中央红钮手动按压除垢'],ls,'保留R012三竖卡与强标题；第三卡为SIL006真实按压局部；无模式照片配对')
 im=Image.new('RGB',(1600,2000));ls=[];fit(im,(0,0,1600,1570),G/'stone-native.png',crop=(0,250,1254,1254),log=ls);txt(im,(80,80),'握柄与曲面',108,'#fff');txt(im,(85,235),'细看银色外观',47,'#d9e7f1');shadow(im,(230,1100,1350,1370));product(im,CUT['silver'],(0,350,1600,1250),ls,65)
 rect(im,(0,1570,1600,2000),'#e4edf4');fit(im,(60,1625,710,265),SIL,crop=(550,710,710,1120),log=ls);fit(im,(830,1625,710,265),SIL,crop=(690,100,865,480),log=ls)
 for x,t in [(60,'握柄细节'),(830,'头部侧壁')]:rect(im,(x,1890,x+710,1965),'#1b3a51');txt(im,(x+40,1908),t,41,'#fff')
 save('D08',im,['A029','A030','A031'],'灰蓝石材曲面静物','银色',['银色外观','握柄细节','头部侧壁'],ls,'石材仅广告环境，完整商品已验生成层旋转/等比复用；无跌落、材质、接口或耐久性能暗示')
 # Buyer-facing overview and known facts only.
 im=Image.new('RGB',(1600,2400),'#f4f8fb');ls=[];rect(im,(0,0,1600,340),'#112d46');txt(im,(80,70),'外观图鉴',110,'#fff');txt(im,(85,230),'看细节，再选色',47,'#cfdfec')
 tiles=[('正面',SIL,(350,25,900,720)),('背面',BACKPAIR,(680,60,1130,710)),('侧面实拍',P('SIL004'),(1600,400,2800,3200)),('白色孔位',P('SIL005'),(800,600,2400,2000)),('下方按键',PANEL,(580,850,850,1120)),('中央红钮',P('SIL005'),(1400,1700,2800,2900))]
 for n,(t,p,crop) in enumerate(tiles):
  x=65+n%3*505;y=395+n//3*450
  if n==0:rect(im,(x,y,x+465,y+340),'#fff');product(im,CUT['silver'],(x+5,y+5,455,330),ls)
  elif n==1:rect(im,(x,y,x+465,y+340),'#fff');product(im,G/'rear-cutout-v003.png',(x+5,y+5,455,330),ls)
  elif n==2:contain_photo(im,(x,y,465,340),P('SIL004'),(1500,0,3000,4500),ls)
  else:fit(im,(x,y,465,340),p,crop=crop,log=ls)
  rect(im,(x,y+340,x+465,y+415),'#e0eaf1');txt(im,(x+27,y+358),t,41)
 txt(im,(80,1330),'商品信息',78)
 facts=[('可选颜色','银色 / 黑色 / 枪灰色'),('销售内容','单花洒'),('出水档位','常规 / 喷雾 / 混合'),('切档位置','下方按键'),('除垢操作','手动按压中央红钮'),('配件说明','不含软管与支架')]
 for n,(a,b) in enumerate(facts):
  x=70+n%2*760;y=1460+n//2*225;rect(im,(x,y,x+710,y+185),'#e2edf5',16);txt(im,(x+35,y+25),a,36,'#4c708a');txt(im,(x+35,y+96),b,43)
 rect(im,(0,2190,1600,2400),'#112d46');txt(im,(80,2250),'三色可选 · 单花洒',73,'#fff')
 save('D09',im,['A032','A033','R034','R035'],'外观图鉴与已知商品信息收尾','三色',['银色','黑色','枪灰色','单花洒','常规','喷雾','混合','下方按键','手动按压中央红钮','不含软管与支架'],ls,'未知尺寸/材质/接口/售后不列；无证书/品牌/服务承诺；真实侧照与原孔/红钮窗明确来源')
 # Warm desert red-button advertising, factual pressed state insert.
 im=Image.new('RGB',(1600,2000));ls=[];fit(im,(0,0,1600,2000),G/'sand-native.png',log=ls);txt(im,(80,78),'中央红钮',112,'#432a19');txt(im,(82,224),'手动按压除垢',96,'#432a19')
 # Use upper portion of already accepted generated product cutout, cropping is intentional macro framing.
 headsrc=Image.open(CUT['silver']).convert('RGBA');headsrc=headsrc.crop((0,0,headsrc.width,round(headsrc.height*.58)));hp=G/'silver-head-macro.png';headsrc.save(hp);product(im,hp,(330,450,1180,1090),ls,-14)
 rect(im,(60,1450,1540,1940),'#f8ecdb',22);actual(im,(80,1470,620,450),'SIL006',ls,crop=(650,1000,3800,4000));txt(im,(760,1510),'找到中央红钮',58,'#4b2d19');txt(im,(760,1635),'手动按住',58,'#4b2d19');txt(im,(760,1760),'辅助清理出水孔',48,'#684a32')
 save('W01',im,['R024','R028'],'夕阳沙纹除垢广告','银色',['中央红钮手动按压除垢','辅助清理出水孔'],ls,'沙纹/夕阳/巨面板借R028，原按压窗SIL006；R024痛点三卡改正向操作；无健康恐吓或清除率')
 im=Image.new('RGB',(1600,2000),'#2e1b11');ls=[];fit(im,(0,0,1600,1600),ROCK,log=ls);txt(im,(75,85),'银色',120,'#fff');txt(im,(80,242),'手持花洒',76,'#fff');rect(im,(75,375,515,465),'#efd2a3',30);txt(im,(110,400),'单花洒',40,'#3b2313')
 rect(im,(0,1600,1600,2000),'#2d1b12');txt(im,(80,1665),'三档出水',112,'#efd0a0');txt(im,(85,1825),'常规 / 喷雾 / 混合',55,'#fff');txt(im,(940,1842),'下方按键切换',38,'#efd0a0')
 save('W02',im,['R033'],'棕金岩石舞台单品广告','银色',['银色','手持花洒','单花洒','三档出水','常规','喷雾','混合','下方按键切换'],ls,'复用已验R02修补版本的完整像素，全图等比；加粗主标题与深棕底带，不新增尺寸线/规格')

def reused():
 import shutil
 sources={'M01':('production/2026-10-24_实拍主导主图/final/R01.jpg',['A038'],'银色白底完整单品','production/2026-10-24_实拍主导主图/image-manifest.json'),'M02':('production/2026-10-24_参考广告主图/final/AD01.jpg',['R001'],'棕金斜托盘广告','production/2026-10-24_参考广告主图/image-manifest.json'),'M03':('production/2026-10-24_参考广告主图/final/AD02.jpg',['A034'],'冷蓝正背广告','production/2026-10-24_参考广告主图/image-manifest.json'),'M07':('production/2026-10-24_参考广告主图/final/AD03.jpg',['R004','R017'],'黑金冲击广告','production/2026-10-24_参考广告主图/image-manifest.json')}
 for id,(src,refs,role,manifest) in sources.items():
  src=ROOT/src;dest=G/f'{id}-reused.jpg';shutil.copy2(src,dest);im=read(src)
  d={'id':id,'role':role,'sku':'银色','refs_actual_viewed':[{'id':r,**rec(ROOT/REFS[r])} for r in refs],'review_reuse':'same approved current batch prior final visual review; no regeneration','source_files':[rec(src)],'actual_inputs':[rec(src)],'source_layers':[{'source':rec(src),'operation':'byte-identical JPG copy','source_kind':'prior_selected_final_jpg'}],'claims':['银色','单花洒'] if id=='M01' else ['三档出水','下方按键切档','中央红钮手动按压除垢'],'copy':'Reused unchanged; see upstream manifest approved_copy','output':rec(dest),'working':rec(dest),'dims':list(im.size),'transform':'byte copy, no recompression','notes':'复用当前已验JPG，不引用10/23失败旧商品','upstream_manifest':rec(ROOT/manifest),'status':'REUSED_AWAITING_PACKAGE_CHECK'}
  (B/'recipes'/f'{id}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2))
 sync()

def longs():
 sets={'L01':([f'D{i:02d}' for i in range(1,10)],'冷蓝详情长图'),'L02':(['M02','M04','M08','W01','W02'],'暖棕详情长图')}
 for id,(ids,role) in sets.items():
  kids=[];ims=[];ys=0
  for k in ids:
   a=json.loads((B/'recipes'/f'{k}.json').read_text());p=ROOT/a['output']['path'];im=read(p);crop=None
   if id=='L02' and k=='M08':crop=[0,320,1600,1600];im=im.crop(crop)
   scale=800/im.width;rs=(800,round(im.height*scale));v=im.resize(rs,Image.Resampling.LANCZOS);ims.append(v);kids.append({'id':k,'source':rec(p),'source_crop':crop,'uniform_scale':scale,'destination':[0,ys,*rs]});ys+=v.height
  out=Image.new('RGB',(800,ys))
  yy=0
  for im in ims:out.paste(im,(0,yy));yy+=im.height
  p=G/f'{id}-v001.jpg';out.save(p,quality=95,subsampling=0)
  d={'id':id,'role':role,'sku':'三色' if id=='L01' else '银色','children':ids,'source_layers':kids,'source_files':[k['source'] for k in kids],'actual_inputs':[k['source'] for k in kids],'refs_actual_viewed':['A039'] if id=='L01' else ['R001','R002','R012','R028','R033'],'claims':'Inherited from listed children, no new claims','copy':'Inherited from children','output':rec(p),'dims':[800,ys],'transform':'Uniform width800; no product redraw; L02 M08 redundant top headline removed by crop','notes':'冷蓝与暖棕路线分别串联；L01首屏→颜色→细节→出水→切档→外观→除垢→静物→信息；L02主角→出水→双键→按压→静物收尾','status':'AWAITING_INDEPENDENT_VISUAL_REVIEW'}
  (B/'recipes'/f'{id}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2));print(id,p,out.size)
 sync()
if __name__=='__main__':
 first();states();more_details();last_designs();reused();longs()

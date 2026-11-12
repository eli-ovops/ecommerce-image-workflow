from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageFilter
import json,shutil,hashlib,zipfile
B=Path(__file__).resolve().parent;R=B.parents[1];O=R/'production/2026-10-24_完整电商套图';G=O/'generated';OUT=B/'JPG';S=B/'sources';N=1254
IDX=json.loads((O/'recipes/source-index.json').read_text())
F='/System/Library/Fonts/STHeiti Medium.ttc'; assets=[]
native=Path('/Users/USER/.codex/generated_images/01a16319-d848-71d0-95e1-72970644c800')
for n,p in [('bath','exec-3829d7c2-075d-4fa7-abc7-67e1d7f64879.png'),('tray','exec-b4f9a4da-67ee-4f09-9873-93a3d59e1e84.png'),('press','exec-2cf28395-ce1b-46dd-b169-1249c1fa9f5a.png')]:shutil.copy2(native/p,S/(n+'.png'))
def read(p):return ImageOps.exif_transpose(Image.open(p)).convert('RGB')
def bg(n='bath'):return read(S/(n+'.png')).resize((N,N))
def text(im,x,y,s,t,c='#32261f',stroke=0):ImageDraw.Draw(im).text((x,y),t,font=ImageFont.truetype(F,s),fill=c,anchor='lt',stroke_width=stroke)
def title(im,a,b,x=55,y=65,size=103):
 size=round(size*1.38) if len(a)<=5 else size
 layer=Image.new('RGBA',(1150,220));d=ImageDraw.Draw(layer);font=ImageFont.truetype(F,size)
 d.text((24,12),a,font=font,fill='#e8cc9b',stroke_width=4,anchor='lt');d.text((20,6),a,font=font,fill='#211a17',stroke_width=4,anchor='lt')
 layer=layer.transform(layer.size,Image.Transform.AFFINE,(1,.12,-15,0,1,0),Image.Resampling.BICUBIC);im.paste(layer,(x-20,y),layer)
 w=int(len(b)*44+65);yy=y+size+47;d=ImageDraw.Draw(im);d.polygon([(x+12,yy),(x+w+15,yy),(x+w,yy+78),(x,yy+78)],fill='#c5a06e');d.polygon([(x+15,yy+3),(x+w+10,yy+3),(x+w-4,yy+72),(x+2,yy+72)],fill='#835336');text(im,x+29,yy+18,42,b,'#fff9ed',1)
def prod(im,key,h,x,y,angle=0,shadow=False):
 p=Image.open(G/(key+'-cutout-v003.png')).convert('RGBA');p=p.resize((round(p.width*h/p.height),h),Image.Resampling.LANCZOS)
 if angle:p=p.rotate(angle,Image.Resampling.BICUBIC,expand=True)
 if shadow:
  sh=Image.new('RGBA',im.size);a=p.getchannel('A');ink=Image.new('RGBA',p.size,(60,41,24,0));ink.putalpha(a.point(lambda v:int(v*.28)));sh.paste(ink,(x+14,y+20),ink);sh=sh.filter(ImageFilter.GaussianBlur(12));im.paste(sh,(0,0),sh)
 im.paste(p,(x,y),p)
def photo(im,k,box,crop):
 p=read(R/IDX['photos'][k]).crop(crop);p=ImageOps.fit(p,(box[2],box[3]),method=Image.Resampling.LANCZOS);im.paste(p,box[:2])
def save(id,name,im,refs,notes=''):
 p=OUT/(id+'_'+name+'.jpg');im.save(p,quality=95,subsampling=0);assets.append(dict(id=id,name=name,file=p.name,refs=refs,notes=notes,size=list(im.size),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
# Large product, handle continues beyond canvas instead of floating on bare thread.
im=bg();prod(im,'silver',1380,530,265,-12);title(im,'三档出水','常规 · 喷雾 · 混合',size=113);text(im,60,1105,39,'下方按键切档','#78553f');save('M01','三档主图',im,['R001','R004','A006'])
im=bg('press');title(im,'按键切档','下方按键  切换三档',size=85);save('M02','下方按键操作',im,['A014','A015','R032'],'生成操作示意，不作为实际按压测试证据')
im=Image.new('RGB',(N,N),'#f7f0e5');photo(im,'SIL006',(0,335,N,919),(350,1100,3850,3950));title(im,'手动按压除垢','按住中央红钮',size=100);save('M03','中央红钮按压',im,['A024','A025'],'原始实拍裁切，无红针重绘；未显示原拍摄房间')
im=Image.new('RGB',(N,N),'#f7f0e5');photo(im,'SIL007',(0,360,N,780),(900,1550,1880,2450));title(im,'三档随心选','常规 · 喷雾 · 混合',size=100);text(im,45,1172,31,'出水局部实拍  ·  下方按键切档');save('M04','出水细节',im,['A012','A016','R023'],'仅放大面板真实出水，不标注该照片具体档位')
p=R/'production/2026-10-25_代表图方向样稿/银色主图_电商字体版.jpg';q=OUT/'M05_日常淋浴人物.jpg';shutil.copy2(p,q);assets.append(dict(id='M05',name='日常淋浴人物',file=q.name,refs=['R022','A019'],notes='用户认可代表图，字节不变复用',size=list(Image.open(q).size),sha256=hashlib.sha256(q.read_bytes()).hexdigest()))
im=bg('tray');prod(im,'silver',760,710,430,0,True);title(im,'银色手持花洒','日常浴室搭配',size=83);save('M06','暖白静物',im,['R001','R008'],'托盘仅为布景，售卖范围为单花洒')
for id,key,col,ref in [('K01','silver','银色','A002'),('K02','black','黑色','A003'),('K03','gunmetal','枪灰色','A004')]:
 im=bg();prod(im,key,1090,620,220);title(im,col+'花洒','单花洒',size=105);text(im,65,500,42,'三档出水');text(im,65,574,32,'常规 / 喷雾 / 混合');text(im,65,1088,29,'不含软管及支架');save(id,col+'SKU',im,[ref],'各SKU独立现有生成商品层；等高等比例，底部自然出画')
im=bg();title(im,'三色可选','银色 · 黑色 · 枪灰色',size=107)
for x,key,col in [(55,'silver','银色'),(455,'black','黑色'),(855,'gunmetal','枪灰色')]:
 prod(im,key,790,x,365);text(im,x+90,1184,36,col)
save('D01','三色对比',im,['A008'],'三色同展示高度，无换色')
im=bg();prod(im,'rear',1140,130,340);prod(im,'silver',1140,690,300);title(im,'正背皆有细节','银色外观',size=95);save('D02','正背外观',im,['A022','A023'],'现有正背生成图层，保留比例与形状，不重新绘制')
im=Image.new('RGB',(N,1500),'#f7f0e5');title(im,'双按键 各有分工','切档与除垢',size=88);p=read(S/'press.png');im.paste(ImageOps.fit(p,(N,1050)),(0,350));d=ImageDraw.Draw(im);d.rectangle((0,1400,N,1500),fill='#835336');text(im,35,1428,32,'中央红钮：手动按压除垢   下方按键：切换三档','#fff9ed');save('D03','双按键分工',im,['R012','A028'])
im=Image.new('RGB',(N,1450),'#f7f0e5');title(im,'按压前后 看孔位','辅助清理出水孔',size=82)
photo(im,'SIL005',(35,385,570,880),(1100,1350,3000,4100));photo(im,'SIL006',(650,385,570,880),(1100,1400,3000,4150));text(im,150,1300,40,'未按压状态');text(im,735,1300,40,'按住中央红钮');save('D04','按压状态实拍',im,['A024','A025','A026'],'两张原实拍，不改变孔位红针；非清洁效果前后对比')
im=bg();prod(im,'silver',1000,750,390);title(im,'选购信息','单花洒 · 三色可选',size=107)
for y,a,b in [(430,'出水档位','常规 / 喷雾 / 混合'),(610,'下方按键','切换出水档位'),(790,'中央红钮','手动按压辅助除垢'),(970,'售卖范围','单花洒，不含软管与支架')]:text(im,65,y,42,a);text(im,65,y+65,30,b,'#745a48')
save('D05','商品信息',im,['A032','A033'],'未知材质尺寸规格不写')
# Assemble a single paced detail scroll from factual and scene pages.
seq=['M01','M05','M02','M03','D04','M04','D02','D01','D05'];tiles=[]
for id in seq:
 a=next(a for a in assets if a['id']==id);im=read(OUT/a['file']);tiles.append(im.resize((1000,round(im.height*1000/im.width)),Image.Resampling.LANCZOS))
long=Image.new('RGB',(1000,sum(i.height for i in tiles)),'white');y=0
for im in tiles:long.paste(im,(0,y));y+=im.height
save('L01','暖白完整详情',long,[], '独立图组合，不重复生成；顺序:'+','.join(seq))
(B/'manifest.json').write_text(json.dumps({'status':'AWAITING_VISUAL_REVIEW','assets':assets,'product_layers':'复用既有实拍引导生成层，非实拍像素或3D硬锁定','water':'实拍局部不标具体档位','customer_acceptance':'仅代表图风格已认可，本套待审'},ensure_ascii=False,indent=2))
# Internal contact sheets, not included in delivery ZIP.
for start in range(0,14,6):
 aa=assets[start:min(start+6,14)];sheet=Image.new('RGB',(1050,800),'#eee')
 for k,a in enumerate(aa):
  im=read(OUT/a['file']);im.thumbnail((340,345));x=k%3*350;y=k//3*400;sheet.paste(im,(x,y));text(sheet,x+5,y+352,20,a['id']+' '+a['name'])
 sheet.save(B/f'review-{start//6+1}.jpg',quality=92)
print(len(assets),'outputs')

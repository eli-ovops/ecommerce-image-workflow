from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageFilter
import sys,json,io,zipfile,xml.etree.ElementTree as ET,hashlib,html,shutil,math
P=Path(__file__).resolve().parent;ROOT=P.parents[1];OLD=ROOT/'production/2026-11-02_顶喷实拍主体黑金实验'
A=P/'assets';E=P/'editable';J=P/'JPG'
for d in (A,E,J):d.mkdir(exist_ok=True)
for src,name in [(OLD/'sources/subject-original-cutout.png','product372.png'),(OLD/'background.png','blackgold.png')]:
 if not (A/name).exists():shutil.copy2(src,A/name)
FONT='/System/Library/Fonts/Supplemental/Songti.ttc';SANS='/System/Library/Fonts/STHeiti Medium.ttc'
cut=Image.open(A/'product372.png').convert('RGBA');only={int(x) for x in sys.argv[1:]}
records=[r for r in json.loads((P/'manifest.json').read_text()) if r['id'] not in only] if only else []
def source(n):return ImageOps.exif_transpose(Image.open(ROOT/f'products/长方形拉钮顶喷/原始实拍20261030/微信图片_20261030154107_{n}_2.jpg')).convert('RGB')
def crop_thumb(im,box,thumbw):return im.crop(tuple(round(v*im.width/thumbw) for v in box))
# Actual source detail crops, no generated reconstruction.
ims={
 'side':crop_thumb(source(374),(730,255,955,345),1000),
 'action':Image.open(ROOT/'production/2026-10-30_长方形拉钮顶喷_完整建模/382-native-detail.jpg').convert('RGB'),
 'face':crop_thumb(Image.open(OLD/'sources/372-oriented.png'),(530,360,850,600),1400),
 'knob':crop_thumb(Image.open(OLD/'sources/372-oriented.png'),(590,475,850,700),1400),
}
cp=ROOT/'products/长方形拉钮顶喷/接头补充实拍20261030'
for name,f,box in [('connector','codex-clipboard-7faa2b7a-f100-46ef-bfc7-87454ab489d0.jpg',(209,299,465,558)),('connector-side','codex-clipboard-6fa807ac-653c-44f8-a3cc-2941c017e31e.jpg',(305,435,430,580))]:
 ims[name]=crop_thumb(ImageOps.exif_transpose(Image.open(cp/f)).convert('RGB'),box,750)
for name,im in ims.items():im.save(A/(name+'.jpg'),quality=98)
# Hand-traced perimeter from actually inspected376 full preview,1000px wide.
im376=source(376);segs=[((315,137),(500,140),(700,144),(855,148)),((855,148),(901,149),(922,165),(925,205)),((925,205),(930,320),(937,460),(941,560)),((941,560),(944,607),(922,635),(878,640)),((878,640),(650,626),(430,611),(257,599)),((257,599),(214,596),(198,574),(201,535)),((201,535),(212,421),(224,306),(239,203)),((239,203),(245,156),(272,137),(315,137))]
pts=[]
for seg in segs:
 for i in range(101):
  t=i/100;pts.append(tuple(sum(((1-t)**3,3*(1-t)**2*t,3*(1-t)*t*t,t**3)[j]*seg[j][k] for j in range(4))*im376.width/1000 for k in range(2)))
m=Image.new('L',im376.size);ImageDraw.Draw(m).polygon(pts,fill=255);m=m.filter(ImageFilter.GaussianBlur(.6));im376=im376.convert('RGBA');im376.putalpha(m);cut376=im376.crop(m.getbbox());cut376.save(A/'product376.png')
class Ad:
 def __init__(self,id,w=900,h=1600,bg='blackgold.png'):
  self.id=id;self.w=w;self.h=h;self.layers=[];self.texts=[];self.transforms=[]
  self.add('Background',ImageOps.fit(Image.open(A/bg).convert('RGBA'),(w,h)))
 def add(self,name,im):self.layers.append((name,im))
 def blank(self):return Image.new('RGBA',(self.w,self.h))
 def shape(self,name,fn):
  im=self.blank();fn(ImageDraw.Draw(im));self.add(name,im)
 def text(self,txt,x,y,size=64,color='#efd0a3',serif=True):
  # Distinct heavy ecommerce hierarchy: large oblique lettering, gradient gold and extrusion.
  size=max(size,31);primary=size>=50;pad=16 if primary else 7;fw=ImageFont.truetype(SANS,size)
  probe=ImageDraw.Draw(Image.new('L',(10,10)));width=round(probe.textlength(txt,font=fw));avail=self.w-x-25
  while width+pad*2+size*.12>avail and size>24:
   size-=1;fw=ImageFont.truetype(SANS,size);width=round(probe.textlength(txt,font=fw))
  mw=width+pad*2+round(size*.14);mh=size+pad*2+10;mask=Image.new('L',(mw,mh));md=ImageDraw.Draw(mask);md.text((pad,pad),txt,font=fw,anchor='lt',fill=255,stroke_width=2 if primary else 1)
  if primary:mask=mask.transform(mask.size,Image.Transform.AFFINE,(1,.11,-mh*.11,0,1,0),Image.Resampling.BICUBIC)
  gold=color.lower() in ['#efd0a3','#f2d7ac'];fill=Image.new('RGBA',mask.size,color)
  if gold:
   dd=ImageDraw.Draw(fill)
   for yy in range(mh):
    t=yy/max(mh-1,1);c=tuple(round(a*(1-t)+b*t) for a,b in zip((255,241,204),(195,135,70)));dd.line((0,yy,mw,yy),fill=(*c,255))
  fill.putalpha(mask);im=self.blank();outline=mask.filter(ImageFilter.MaxFilter(5 if primary else 3));shade=Image.new('RGBA',mask.size,'#49301a' if gold else '#15191f');shade.putalpha(outline.point(lambda v:round(v*.8)))
  dark=sum(int(color.lstrip('#')[i:i+2],16) for i in (0,2,4))<240
  if not dark:im.alpha_composite(shade,(x-pad+3,y-pad+5))
  im.alpha_composite(fill,(x-pad,y-pad));self.add('Text '+txt,im)
  self.texts.append(dict(text=txt,x=x,y=y,size=size,color=color,font='Heiti SC',bold=True,oblique=primary,gold_gradient=gold,extrusion_px=3))
 def installed(self,headbox):
  # Native product, connected pipe and94 illustrative water curves: no suspended flat cutout.
  raw=Image.open(A/'native-installed.png').convert('RGBA');scale=(headbox[2]-headbox[0])/595
  xy=(round(headbox[0]-325*scale),round(headbox[1]-140*scale));raw=raw.resize((round(raw.width*scale),round(raw.height*scale)),Image.Resampling.LANCZOS)
  im=self.blank();im.alpha_composite(raw,xy);self.add('Native installed shell pipe and water illustration',im);self.transforms.append(dict(source='native-installed.png',scale=scale,xy=xy,illustration=True))
 def product(self,angle,box):
  # Static native model with one original-photo face. Pose/lighting source is388 native layer.
  raw=Image.open(A/'native-static.png').convert('RGBA');raw=raw.crop(raw.getchannel('A').getbbox())
  delta=-8 if self.id in (392,395,399) else 0
  if self.id in (393,397):delta=-82
  raw=raw.rotate(delta,Image.Resampling.BICUBIC,expand=True);raw.thumbnail((box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS)
  xy=(box[0]+(box[2]-box[0]-raw.width)//2,box[1]+(box[3]-box[1]-raw.height)//2);im=self.blank();im.alpha_composite(raw,xy)
  for r,off,op in [(15,(10,18),.4),(3,(2,4),.55)]:
   mask=Image.new('L',(self.w,self.h));mask.paste(im.getchannel('A'),off);mask=mask.filter(ImageFilter.GaussianBlur(r)).point(lambda v:round(v*op));sh=self.blank();sh.putalpha(mask);self.add('Native product cast shadow',sh)
  self.add('Native shell single original372 photo face',im);self.transforms.append(dict(source='native-static.png',uniform=True,rotation=delta,xy=xy,size=raw.size))
 def detail(self,name,box,rounded=16):
  iw,ih=box[2]-box[0],box[3]-box[1]
  raw=Image.open(A/(name+'.jpg'))
  if name=='side':
   fitted=ImageOps.contain(raw,(iw,ih));im=Image.new('RGBA',(iw,ih),'#27221d');im.paste(fitted,((iw-fitted.width)//2,(ih-fitted.height)//2))
  else:im=ImageOps.fit(raw,(iw,ih)).convert('RGBA')
  m=Image.new('L',im.size);ImageDraw.Draw(m).rounded_rectangle((0,0,iw-1,ih-1),rounded,fill=255);im.putalpha(m);lay=self.blank();lay.alpha_composite(im,(box[0],box[1]));self.add('Original photo detail '+name,lay)
 def save(self,note):
  if only and self.id not in only:return
  out=self.blank()
  for _,im in self.layers:out=Image.alpha_composite(out,im)
  out.convert('RGB').save(J/f'{self.id}.jpg',quality=97,subsampling=0)
  folder=E/str(self.id);folder.mkdir(exist_ok=True)
  root=ET.Element('image',w=str(self.w),h=str(self.h),name=str(self.id));stack=ET.SubElement(root,'stack')
  with zipfile.ZipFile(folder/'layers.ora','w',zipfile.ZIP_DEFLATED) as z:
   z.writestr('mimetype','image/openraster',compress_type=zipfile.ZIP_STORED)
   for i,(name,im) in enumerate(reversed(self.layers)):
    b=io.BytesIO();im.save(b,format='PNG');path=f'data/layer{i}.png';z.writestr(path,b.getvalue());ET.SubElement(stack,'layer',name=name,src=path,x='0',y='0',opacity='1',visibility='visible',**{'composite-op':'svg:src-over'})
   z.writestr('stack.xml',ET.tostring(root));b=io.BytesIO();out.save(b,format='PNG');z.writestr('mergedimage.png',b.getvalue())
  # Native raster layers + genuinely live editable text overlay.
  base=self.blank()
  for name,im in self.layers:
   if not name.startswith('Text '):base=Image.alpha_composite(base,im)
  base.save(folder/'base.png')
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}"><image href="base.png" width="{self.w}" height="{self.h}"/>'
  for t in self.texts:svg+=f'<text x="{t["x"]}" y="{t["y"]+t["size"]*.85}" font-family="{t["font"]}" font-weight="900" font-size="{t["size"]}" fill="{t["color"]}">{html.escape(t["text"])}</text>'
  (folder/'editable.svg').write_text(svg+'</svg>');(folder/'layout.json').write_text(json.dumps(dict(text=self.texts,transforms=self.transforms,note=note),ensure_ascii=False,indent=2))
  records.append(dict(id=self.id,size=[self.w,self.h],note=note,source_transforms=self.transforms))
  print('Saved',self.id,flush=True)
# 399: original reference hierarchy, top gold copy, diagonal full product, dark marble.
a=Ad(399,bg='blackgold-mist.png')
shade=a.blank();sd=ImageDraw.Draw(shade)
for yy in range(460):sd.line((0,yy,900,yy),fill=(12,13,17,round(150*max(0,1-yy/460))))
a.add('Soft header shade',shade)
a.shape('Gold rule',lambda d:d.line((34,78,34,374),fill='#b39163',width=2))
a.text('银色顶喷',65,67,40)
a.text('提拉红钮 辅助除垢',63,148,70)
a.text('长方形大面板',63,242,74)
a.text('向外提拉 · 短针辅助清理',65,354,38)
a.product(68,(25,475,885,1550))
a.save('参考399黑金石材、斜置整件、上部金色宋体层级。商品376原始整件层等比旋转；无新造孔纹。原照近正视，厚度和参考透视不能等同。未使用侧边拼接伪造厚度。')
(P/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
# Individual reference treatments; unsupported dynamic/technical claims are explicit gaps.
a=Ad(387,1200,1200)
a.shape('Gold panel lines',lambda d:[d.line((x,0,x,1000),fill='#9a774b',width=3) for x in (80,330,930,1135)])
a.shape('Neutral display plinth',lambda d:d.polygon([(860,255),(1065,220),(1110,1000),(862,1030)],fill='#dedbd5'))
a.product(84,(350,150,1090,1035))
a.text('长方形顶喷',45,80,54)
a.text('提拉除垢',45,170,52)
a.detail('action',(40,435,340,750),28)
a.text('短针细节实拍',48,780,34)
a.shape('Bottom band',lambda d:d.rectangle((0,1050,1200,1200),fill='#1b1919'))
a.text('银色',42,1085,79);a.text('约30×20cm 大面板',290,1100,60)
a.save('参考387黑金、立式整件、浅色展示台、左操作窗、底规格带。无包装/防爆/大水量承诺；382局部只标短针细节，不认定其外缘SKU。原片厚度表达不足。')
# Pull-function pair: same blackgold theme and diagonal main + circular real detail.
for id,w,h in [(392,1200,1200),(395,900,1600)]:
 a=Ad(id,w,h,bg='blackgold-mist.png');k=w/900
 a.text('提拉红钮 辅助除垢',int(45*k),int(65*k),int(57*k))
 a.text('短针辅助清理出水孔',int(45*k),int(145*k),int(47*k))
 a.text('向外提拉 · 操作细节见实拍',int(45*k),int(225*k),int(29*k))
 a.product(66,(25,int(h*.25),w-25,h-60))
 # Inset covers limited lower-right area; no invented internal cross-section.
 ss=int(w*.30);x=w-ss-35;y=h-ss-110
 a.shape('Detail outer gold',lambda d:d.ellipse((x-5,y-5,x+ss+5,y+ss+5),fill='#b79566'))
 a.detail('action',(x,y,x+ss,y+ss),ss//2)
 a.shape('Detail caption back',lambda d:d.rounded_rectangle((x-10,y+ss+12,x+ss+10,y+ss+64),15,fill='#25201c'))
 a.text('短针实拍细节',x+4,y+ss+22,int(ss/6.8))
 a.save(f'参考{id}黑金斜置主体、上方金字、右下圆窗。圆窗用382实际短针局部，替换未知剖面；主体为复位实拍，未伪造拉出长针、碎垢或旋转箭头。不能声称完整提拉过程已演示。')
# Model pair: identity changed, original motif retained; no unverified flow synthesis.
for id,w,h in [(391,1200,1200),(394,900,1600)]:
 a=Ad(id,w,h,'model-bath.png')
 a.text('银色顶喷 浴室美学',45,55,67 if w==1200 else 61)
 a.text('长方形面板 · 中央提拉红钮',48,150 if w==1200 else 145,35)
 a.installed((235,235,1130,600) if w==1200 else (90,300,875,650))
 a.shape('Illustration badge',lambda d:d.rounded_rectangle((36,h-87,315,h-29),14,fill=(16,28,42,225)))
 a.text('安装出水示意',50,h-75,32)
 a.save(f'参考{id}蓝星空顶、暖大理石墙、上部大商品和下方模特。新原创成年短发模特，AI背景/模特+372实拍整件。缺安装仰视实拍，保留原片角度；未生成未经核对起点的水幕，故参考动态构图尚未完整覆盖。')
# Six-card layout faithful to reference396, factual visible details only.
a=Ad(396,900,1600,'warm-bath.png')
a.shape('Dark overall veil',lambda d:d.rectangle((0,0,900,1600),fill=(15,12,10,100)))
a.text('六处细节 看得见',43,85,72)
a.text('面板 · 红钮 · 银边 · 接头',48,180,36)
for i,(name,title,sub) in enumerate([('face','面板纹样','孔口与叶形纹样'),('knob','中央红钮','向外提拉除垢'),('side','银色侧边','实拍金属反射'),('connector','接头开口','内圈与网格可见'),('connector-side','背部接头','侧面外观实拍'),('action','短针细节','操作局部实拍')]):
 x=35+(i%2)*430;y=290+(i//2)*425
 a.shape('Card frame',lambda d:d.rounded_rectangle((x,y,x+400,y+400),18,fill='#302a25',outline='#a88c6a',width=2))
 a.detail(name,(x+8,y+96,x+392,y+390),12)
 a.text(title,x+20,y+16,36);a.text(sub,x+20,y+61,25,color='#f1e4d5',serif=False)
a.save('参考396六宫格层级，替换无依据六大功能为六处实拍细节。不复制材料层、防爆、硅胶、增压等。侧边局部保留真实环境反射。')
# AIR pair: keep warm scene/gold stepped visual hierarchy; external details replace exploded internals.
for id,w,h in [(393,1200,1200),(397,900,1600)]:
 a=Ad(id,w,h,'warm-bath.png')
 a.shape('Warm shade',lambda d:d.rectangle((0,0,w,h),fill=(16,10,5,70)))
 a.text('从面板到接头',50,65,76 if w==1200 else 67)
 a.text('细看顶喷外观',50,160,68 if w==1200 else 58)
 a.installed((150,285,w-45,int(h*.56))) if w==1200 else a.installed((55,420,w-35,800))
 a.text('安装出水示意',50,int(h*.62),31)
 # Gold-bordered external detail cards in place of misleading internal layers.
 yy=int(h*.65) if w==1200 else int(h*.69);ss=int(w*.28)
 for j,(name,title) in enumerate([('face','面板纹样'),('side','银色侧边'),('connector','接头开口')]):
  x=30+j*(ss+15);a.shape('Gold external-detail border',lambda d:d.rounded_rectangle((x-3,yy-3,x+ss+3,yy+ss+3),20,fill='#c8a875'))
  a.detail(name,(x,yy,x+ss,yy+ss),17);a.text(title,x+8,yy+ss+22,int(w*.034))
 a.save(f'参考{id}暖浴室、金色章节、主物和下部信息卡。AIR/节水/内部爆炸结构完全无证据，主题替换为外观三处；此图不标原AIR功能已覆盖。')
# Connector portrait: replace unsupported rotation/coverage comparison with visible details.
a=Ad(398,900,1600,'warm-bath.png')
a.text('银色顶喷 安装示意',45,82,62)
a.text('面板与接头 细看外观',48,173,50)
a.installed((105,340,865,720))
a.text('安装出水示意',48,1015,33)
a.shape('Bottom cards',lambda d:d.rounded_rectangle((30,1090,870,1530),20,fill=(28,23,20,220),outline='#a68a65',width=2))
a.detail('connector-side',(50,1120,435,1440),15);a.detail('connector',(465,1120,850,1440),15)
a.text('背部接头实拍',55,1472,37);a.text('接头开口实拍',470,1472,37)
a.save('参考398暖浴室、上标题、中主体、底部双卡。中部改接头实拍、双卡改外观，不画360箭头、安装效果或人体水量比较。安装和转动范围未验证。')
# Three comprehensive square treatments; lack of verified installed angle/water remains a visible difference.
for id in (389,390):
 bg='blue-bath.png' if id==389 else 'warm-bath.png'
 a=Ad(id,1200,1200,bg)
 if id==390:
  a.shape('Teal ambient layer',lambda d:d.rectangle((0,0,1200,1200),fill=(0,52,58,115)))
 if id==389:
  a.installed((30,60,775,485));a.product(83,(35,585,440,1120))
  a.text('提拉',805,65,120,color='#0c1720',serif=False);a.text('除垢',805,218,120,color='#0c1720',serif=False)
  a.text('长方形顶喷',765,390,65,color='#0c1720',serif=False)
  a.shape('Gold labels',lambda d:d.rounded_rectangle((775,510,1168,580),28,fill='#d6af81'))
  a.text('约30×20cm',797,529,42,color='#17212a',serif=False)
  a.text('安装出水示意',790,860,33,color='#15212a',serif=False)
  a.text('中央红钮',825,640,48,color='#15212a',serif=False);a.text('向外提拉',825,719,48,color='#15212a',serif=False)
  a.shape('Blue bottom',lambda d:d.rectangle((480,1030,1200,1200),fill='#213753'))
  a.text('银色长方形顶喷',500,1080,68,color='#fff7e9',serif=False)
 else:
  a.installed((125,75,1160,540));a.product(77,(15,610,495,985))
  a.shape('Bottom band',lambda d:d.rectangle((0,1000,1200,1200),fill='#c8986e' if id==388 else '#133334'))
  # Red/white ad emphasis for388, gold high-density lower right for390.
  if id==388:
   a.shape('Red slogan plaque',lambda d:d.rounded_rectangle((390,635,1170,770),20,fill='#9e161c'))
   a.text('提拉红钮 辅助除垢',413,668,68,color='#ffffff',serif=False)
   a.text('约30×20cm 面板',545,1028,45,color='#251a14',serif=False)
   a.text('银色长方形顶喷',530,1095,64,color='#251a14',serif=False)
  else:
   a.text('中央红钮 · 提拉除垢',500,1018,44)
   a.text('银色长方形顶喷',490,1090,90)
  a.shape('Illustration label back',lambda d:d.rounded_rectangle((850,35,1170,95),25,fill=(18,38,39,220)))
  a.text('安装出水示意',878,53,32,color='#ffffff',serif=False)
 a.save(f'参考{id}综合双主体构图、浴室主色和强标题。实拍整件只能保留现有视角，未添加水幕/支架/通用接口/增压等；动态安装主图覆盖不足，当前为静态版候选而非原参考完整复现。')
(P/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))

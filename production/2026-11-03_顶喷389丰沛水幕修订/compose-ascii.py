from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageChops,ImageOps
import json,random,math,shutil,io,zipfile,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent;W=H=1254;random.seed(389)
for n in ['editable','review']: (P/n).mkdir(exist_ok=True)
shutil.copy2('/Users/USER/.codex/generated_images/01a18bc9-5492-79e3-bfe3-678a64ea1c26/exec-9b7f28c8-c4d2-4c52-8484-d39228e35324.png',P/'background-water.png')
layers=[]
def blank():return Image.new('RGBA',(W,H))
def add(name,im):layers.append((name,im))
add('Generated independent bathroom and distal water',Image.open(P/'background-water.png').convert('RGBA').resize((W,H),Image.Resampling.LANCZOS))
curtain=Image.open(P/'water-only-native.png').convert('RGBA').resize((675,960),Image.Resampling.LANCZOS)
curtain.putalpha(curtain.getchannel('A').point(lambda v:round(v*.82)))
dense=blank();dense.alpha_composite(curtain,(65,150))
occlusion=Image.new('L',(W,H));ImageDraw.Draw(occlusion).polygon([(80,230),(320,335),(705,215),(750,1110),(65,1110)],fill=255)
dense.putalpha(ImageChops.multiply(dense.getchannel('A'),occlusion.filter(ImageFilter.GaussianBlur(.6))))
add('New water-only continuous bright abundant curtain',dense)
raw=Image.open(P/'native/installed-dry.png').convert('RGBA');scale=.7;xy=(-260,-90);im=blank();im.alpha_composite(raw.resize((1260,1260),Image.Resampling.LANCZOS),xy);add('Native installed 300x200x20 shell with single photo face',im)
# Short near-hole joins only: native projected photo anchors, no invented nozzle row.
S=3;water=Image.new('RGBA',(W*S,H*S));draw=ImageDraw.Draw(water);points=json.loads((P/'native/geometry-and-projection.json').read_text())['anchors'];joins=[]
for i,a in enumerate(points):
 x=a['x']*scale+xy[0];y=a['y']*scale+xy[1];end=410+random.uniform(-10,25);dx=random.uniform(-5,5);brightness=random.uniform(165,235);phase=random.uniform(0,6.28)
 prev=(x,y)
 for j in range(1,max(2,int((end-y)/3))):
  yy=y+j*3;t=(yy-y)/(end-y);xx=x+dx*t+math.sin(t*7+phase)*t*.5
  alpha=int(brightness*(1-.5*t)*max(0,min(1,(430-yy)/95)))
  draw.line((prev[0]*S,prev[1]*S,xx*S,yy*S),fill=(48,74,94,round(alpha*.5)),width=5)
  draw.line((prev[0]*S-1,prev[1]*S,xx*S-1,yy*S),fill=(232,245,255,alpha),width=max(1,round(S*1.1*(.8+.2*math.sin(t*35+phase)))))
  if j%random.randint(9,17)==0 and t>.15:
   rx=.65*S;ry=1.5*S;draw.ellipse((xx*S-rx,yy*S-ry,xx*S+rx,yy*S+ry),fill=(240,250,255,min(240,alpha+25)))
  prev=(xx,yy)
 joins.append(dict(id=a['id'],source_xy=[x,y],fade_end=end))
water=water.resize((W,H),Image.Resampling.LANCZOS)
# Occlude the joins behind native red knob; no water begins on knob.
pm=im.load();wa=water.getchannel('A');mask=Image.new('L',(W,H));mp=mask.load()
for y in range(80,350):
 for x in range(100,720):
  r,g,b,a=pm[x,y]
  if a>100 and r>g*1.5 and r>b*1.5:mp[x,y]=255
water.putalpha(ImageChops.subtract(wa,mask));add('Projected near-hole transition joins not measured flow',water)
raw=Image.open(P/'native/static-dry-v3.png').convert('RGBA');bbox=raw.getchannel('A').getbbox();raw=raw.crop(bbox);sc=min(360/raw.width,555/raw.height);raw=raw.resize((round(raw.width*sc),round(raw.height*sc)),Image.Resampling.LANCZOS);pos=(40,1110-raw.height)
static=blank();static.alpha_composite(raw,pos);shadow=blank();shadow.putalpha(static.getchannel('A').filter(ImageFilter.GaussianBlur(10)).point(lambda v:round(v*.35)));sh=blank();sh.alpha_composite(shadow,(9,12));add('Display contact shadow',sh)
decor=blank();ImageDraw.Draw(decor).rectangle((0,1070,1254,1254),fill=(15,56,111,255));add('Independent blue footer',decor);add('Native static product same geometry',static)
textlayer=blank();FONT='/System/Library/Fonts/STHeiti Medium.ttc'
specs=[('\u5bbd\u5e45\u96e8\u5e55',(775,155,1234,300),(0,0,0),False),('\u8212\u5c55\u7545\u6dcb',(775,365,1234,510),(0,0,0),False),('\u94f6\u8272\u957f\u65b9\u5f62\u9876\u55b7',(465,1110,1220,1230),(255,255,255),True)]
for text,(x,y,x2,y2),color,white in specs:
 fs=y2-y
 while True:
  font=ImageFont.truetype(FONT,fs);bb=font.getbbox(text,stroke_width=2);tw=bb[2]-bb[0];th=bb[3]-bb[1]
  if tw+th*.16<x2-x and th<y2-y:break
  fs-=1
 m=Image.new('L',(tw+8,th+8));ImageDraw.Draw(m).text((-bb[0]+4,-bb[1]+4),text,font=font,fill=255,stroke_width=2)
 m=m.transform((m.width+int(m.height*.18),m.height),Image.Transform.AFFINE,(1,.18,-m.height*.18,0,1,0),Image.Resampling.BICUBIC)
 ink=Image.new('RGBA',m.size,(*color,255));ink.putalpha(m);textlayer.alpha_composite(ink,(x+(x2-x-m.width)//2,y+(y2-y-m.height)//2))
add('Independent editable text source',textlayer)
out=blank()
for name,im in layers:out.alpha_composite(im)
out.save(P/'editable/merged.png');out.convert('RGB').save(P/'389-layered-candidate.jpg',quality=97,subsampling=0)
root=ET.Element('image',w=str(W),h=str(H));stack=ET.SubElement(root,'stack')
with zipfile.ZipFile(P/'editable/389-layers.ora','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('mimetype','image/openraster')
 for i,(name,im) in reversed(list(enumerate(layers))):
  fn='data/layer%d.png'%i;b=io.BytesIO();im.save(b,format='PNG');z.writestr(fn,b.getvalue());im.save(P/'editable'/('layer%d.png'%i));ET.SubElement(stack,'layer',name=name,src=fn,x='0',y='0',opacity='1.0',visibility='visible',**{'composite-op':'svg:src-over'})
 z.writestr('stack.xml',ET.tostring(root));b=io.BytesIO();out.save(b,format='PNG');z.writestr('mergedimage.png',b.getvalue())
for tag,box in [('holes-side',(70,50,740,370)),('display',(30,540,425,1110)),('water',(350,290,725,800))]:
 crop=out.crop(box);crop.resize((crop.width*2,crop.height*2)).convert('RGB').save(P/'review'/(tag+'-200pct.jpg'),quality=97)
(P/'composition-record.json').write_text(json.dumps(dict(installed_scale=scale,installed_xy=xy,static_crop=bbox,static_scale=sc,static_xy=pos,water_joins=joins,generated_water='Independent background water; not matched one-to-one with94 anchors, not CFD or measured flow',text=[a[0] for a in specs],no_ai_product_pixels=True),ensure_ascii=False,indent=2))

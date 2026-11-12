from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, math, json, hashlib
W=Path(__file__).resolve().parent
SPECS={
'D04-upper':dict(id='D04',crop=(95,390,400,740),poly=[(148,485),(177,457),(200,447),(228,446),(262,457),(291,478),(313,512),(327,548),(328,582),(312,616),(297,623),(266,623),(212,600),(168,557),(144,515)],red=(233,547,19,21),radii=[(2.0,2.1),(2.5,2.5)],gap=8,threshold=17,direction=(-.68,.733),length=480,clip=(0,390,400,1197)),
'D04-lower':dict(id='D04',crop=(140,1210,540,1550),poly=[(201,1295),(254,1278),(282,1278),(324,1290),(366,1305),(403,1329),(437,1361),(465,1398),(474,1427),(461,1451),(436,1468),(412,1470),(350,1445),(270,1401),(204,1351)],red=(343,1393,28,22),radii=[(2.4,2.0),(3,2.5)],gap=10,threshold=14,direction=(-.665,.747),length=580,clip=(0,1208,600,1670)),
'D11-upper':dict(id='D11',crop=(220,70,385,315),poly=[(249,129),(270,119),(287,122),(308,132),(328,154),(342,180),(346,204),(338,231),(323,247),(303,253),(276,236),(255,209),(243,174)],red=(296,187,13,15),radii=[(1.4,1.9),(1.8,2.3)],gap=6,threshold=15,direction=(-.995,.1),length=350,clip=(0,90,359,550)),
'D11-lower':dict(id='D11',crop=(575,945,735,1210),poly=[(602,1056),(611,1030),(634,1011),(655,1003),(678,1007),(691,1021),(700,1044),(699,1075),(688,1095),(669,1118),(647,1130),(627,1129),(611,1116),(602,1087)],red=(660,1068,13,14),radii=[(1.4,1.7),(1.8,2)],gap=6,threshold=15,direction=(.994,.11),length=370,clip=(593,995,899,1355)),
}
def shifted(a,dx,dy):return np.roll(np.roll(a,dy,0),dx,1)
def detect(im,s):
 a=np.asarray(im).astype(float); lum=a.mean(2); h,w=lum.shape
 mask=Image.new('L',(w,h)); d=ImageDraw.Draw(mask);d.polygon(s['poly'],fill=255)
 x,y,rx,ry=s['red'];d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=0)
 mask=np.array(mask)>0
 score=np.full((h,w),-1e6); white=a.min(2)
 for rx,ry in s['radii']:
  ring=np.mean([shifted(white,round(rx*math.cos(t)),round(ry*math.sin(t))) for t in np.linspace(0,2*math.pi,12,endpoint=False)],axis=0)
  outer=np.mean([shifted(lum,round(rx*1.9*math.cos(t)),round(ry*1.9*math.sin(t))) for t in np.linspace(0,2*math.pi,12,endpoint=False)],axis=0)
  sc=ring-.60*lum-.40*outer
  sc[(ring<140)|(lum>210)]=-1e6
  score=np.maximum(score,sc)
 score[~mask]=-1e6
 pts=[]
 for _ in range(280):
  y,x=np.unravel_index(np.argmax(score),score.shape); val=score[y,x]
  if val<s['threshold']:break
  pts.append([int(x),int(y),round(float(val),1)])
  yy,xx=np.ogrid[:h,:w];score[(xx-x)**2+(yy-y)**2<s['gap']**2]=-1e6
 return pts

def mapping(im,s,pts,name):
 c=im.crop(s['crop']).resize(((s['crop'][2]-s['crop'][0])*3,(s['crop'][3]-s['crop'][1])*3));d=ImageDraw.Draw(c)
 for n,(x,y,*_) in enumerate(pts):
  x=(x-s['crop'][0])*3;y=(y-s['crop'][1])*3;d.ellipse((x-7,y-7,x+7,y+7),outline='#ff4c22',width=2);d.text((x+7,y-6),str(n),fill='#ff4c22')
 c.save(W/(name+'-detected.jpg'),quality=94)
if __name__=='__main__':
 allp={}
 for name,s in SPECS.items():
  im=Image.open(W/'before-water'/(s['id']+'.png')).convert('RGB');pts=detect(im,s);allp[name]=pts;mapping(im,s,pts,name);print(name,len(pts))
 (W/'detected-port-points.json').write_text(json.dumps(allp,indent=2))

def detect_components(im,s):
 a=np.array(im);h,w=a.shape[:2];mim=Image.new('L',(w,h));d=ImageDraw.Draw(mim);d.polygon(s['poly'],fill=255)
 x,y,rx,ry=s['red'];d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=0)
 # Neutral white ports surrounded by charcoal; chrome boundary excluded by plate polygon.
 mim=mim.filter(ImageFilter.MaxFilter(7))
 m=(a.min(2)>125)&((a.max(2).astype(float)-a.min(2))<65)&(np.array(mim)>0)
 done=np.zeros(m.shape,bool);pts=[]
 for y,x in zip(*np.where(m)):
  if done[y,x]:continue
  stack=[(x,y)];done[y,x]=True;coords=[]
  while stack:
   xx,yy=stack.pop();coords.append((xx,yy))
   for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)):
    xn=xx+dx;yn=yy+dy
    if 0<=xn<w and 0<=yn<h and m[yn,xn] and not done[yn,xn]: done[yn,xn]=True;stack.append((xn,yn))
  ar=np.array(coords);bw=np.ptp(ar[:,0])+1;bh=np.ptp(ar[:,1])+1
  if 3<=len(coords)<=75 and max(bw,bh)<=11 and min(bw,bh)>=2 and max(bw,bh)/min(bw,bh)<2.7:
   cx,cy=ar.mean(0);pts.append([round(cx,2),round(cy,2),len(coords)])
 return pts
if __name__=='__main__':
 allp={}
 for name,s in SPECS.items():
  im=Image.open(W/'before-water'/(s['id']+'.png')).convert('RGB');pts=detect_components(im,s);allp[name]=pts;mapping(im,s,pts,name+'-cc');print(name,'cc',len(pts))
 (W/'cc-port-points.json').write_text(json.dumps(allp,indent=2))

def render_layer(im,s,points,seed):
 rng=np.random.default_rng(seed);S=3;w,h=im.size
 lay=Image.new('RGBA',(w*S,h*S));draw=ImageDraw.Draw(lay)
 def line(pts,col,width):draw.line([(round(x*S),round(y*S)) for x,y in pts],fill=col,width=max(1,round(width*S)))
 for x,y,*_ in points:
  dx,dy=s['direction']
  if s['id']=='D11':
   if s['direction'][0]<0:dy=.31+(y-186)*.0042
   else:dy=.29+(y-1060)*.004
   dx=-1 if dx<0 else 1
  dd=math.hypot(dx,dy);dx/=dd;dy/=dd
  theta=rng.normal(0,.005);dx,dy=dx*math.cos(theta)-dy*math.sin(theta),dx*math.sin(theta)+dy*math.cos(theta)
  L=s['length']*rng.uniform(.88,1.05);perp=(-dy,dx);phase=rng.uniform(0,7)
  def pos(t):
   j=(1-math.exp(-t/30))*(.25*math.sin(t/19+phase)+.12*math.sin(t/7+phase))
   return (x+dx*t+perp[0]*j,y+dy*t+perp[1]*j+.000008*t*t)
  pts=[pos(float(t)) for t in np.arange(0,L,3)]
  width=rng.uniform(.75,1.12) if s['id']=='D04' else rng.uniform(.62,.86)
  line(pts,(212,234,244,32),width+1.5)
  line(pts,(222,242,250,int(rng.uniform(105,155))),width)
  line([pos(t) for t in np.arange(0,22,1)],(240,251,255,210),width+.12)
  t=25.0
  while t<L:
   t+=rng.uniform(5,16);ll=rng.uniform(2,9)
   line([pos(t),pos(t+ll)],(247,254,255,int(rng.uniform(95,195))),width*rng.uniform(.8,1.2))
 lay=lay.resize((w,h),Image.Resampling.LANCZOS)
 alpha=np.array(lay.getchannel('A'));clip=Image.new('L',(w,h));d=ImageDraw.Draw(clip);d.rectangle(s['clip'],fill=255)
 x,y,rx,ry=s['red'];d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=0)
 if s['id']=='D11' and s['direction'][0]<0:d.rectangle((278,265,306,550),fill=0)
 alpha[np.array(clip)==0]=0;lay.putalpha(Image.fromarray(alpha))
 return lay

if __name__=='__main__':
 points=json.loads((W/'cc-port-points.json').read_text())
 # Only original, visibly white outlet components; remove isolated chrome reflection.
 points['D11-lower']=[p for p in points['D11-lower'] if not (p[0]<610 and p[1]>1110)]
 points['D11-lower']=[p for p in points['D11-lower'] if all(math.hypot(p[0]-x,p[1]-y)>3.5 for x,y in [(632,1019),(626.8,1026)])]
 points['D04-lower']=[p for p in points['D04-lower'] if math.hypot(p[0]-285,p[1]-1281)>5]
 for p in [[645,1049,0],[652,1050,0],[646,1057,0]]:
  if all(math.hypot(q[0]-p[0],q[1]-p[1])>3 for q in points['D11-lower']):points['D11-lower'].append(p)
 (W/'local-port-points.json').write_text(json.dumps(points,ensure_ascii=False,indent=2))
 for id in ('D04','D11'):
  im=Image.open(W/'before-water'/(id+'.png')).convert('RGB');layer=Image.new('RGBA',im.size)
  for n,(name,s) in enumerate(SPECS.items()):
   if s['id']!=id:continue
   l=render_layer(im,s,points[name],202610230+n);layer=Image.alpha_composite(layer,l)
  dest=W/(id+'-local');dest.mkdir(exist_ok=True);layer.save(dest/'water-layer.png')
  out=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB');out.save(dest/'composite.png')
  b=np.array(im);a=np.array(out);mask=np.array(layer.getchannel('A'))>0;diff=np.any(a!=b,axis=2)
  proof={'id':id,'method':'user-approved additive RGBA water compositing; immutable base','source_sha256':hashlib.sha256((W/'before-water'/(id+'.png')).read_bytes()).hexdigest(),'changed_pixels':int(diff.sum()),'outside_water_mask_changed_pixels':int((diff&~mask).sum()),'added_outlet_roots':{name:len(points[name]) for name,s in SPECS.items() if s['id']==id},'person_body_mode_key_and_grip':'No water layer reaches these regions; base is not regenerated','jpeg_encoding_note':'Exact pixel preservation proved on lossless composite; JPEG recompression is lossy.'}
  (dest/'pixel-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2))
  for name,s in SPECS.items():
   if s['id']==id:out.crop(s['crop']).resize(((s['crop'][2]-s['crop'][0])*3,(s['crop'][3]-s['crop'][1])*3)).save(dest/(name+'-water-crop.jpg'),quality=95)
  print(id,proof)

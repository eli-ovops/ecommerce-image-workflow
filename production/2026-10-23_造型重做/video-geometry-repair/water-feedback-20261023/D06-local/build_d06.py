from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np, json, hashlib, math, random
P=Path(__file__).resolve().parent
src=P.parent/'before-water/D06.png'
im=Image.open(src).convert('RGBA'); w,h=im.size
rgb=np.asarray(im)[:,:,:3].astype(float); lum=rgb.mean(2); neutral=rgb.min(2)
def detect(poly,rs,gap,threshold,red):
 m=Image.new('L',(w,h));d=ImageDraw.Draw(m);d.polygon(poly,fill=255);x,y,rx,ry=red;d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=0)
 score=np.full((h,w),-1e5)
 for rx,ry in rs:
  samples=np.array([np.roll(np.roll(neutral,round(ry*math.sin(t)),0),round(rx*math.cos(t)),1) for t in np.linspace(0,2*math.pi,16,endpoint=False)]); ring=np.mean(samples,0); ring_floor=np.quantile(samples,.30,axis=0)
  outer=np.mean([np.roll(np.roll(lum,round(ry*1.8*math.sin(t)),0),round(rx*1.8*math.cos(t)),1) for t in np.linspace(0,2*math.pi,16,endpoint=False)],0)
  a=ring-.55*lum-.45*outer;a[(ring<175)|(ring_floor<145)|(lum>195)]=-1e5;score=np.maximum(score,a)
 score[np.array(m)==0]=-1e5;pts=[];yy,xx=np.ogrid[:h,:w]
 for _ in range(220):
  y,x=np.unravel_index(score.argmax(),score.shape);v=score[y,x]
  if v<threshold:break
  pts.append([int(x),int(y),round(float(v),2)]);score[(xx-x)**2+(yy-y)**2<gap**2]=-1e5
 return sorted(pts,key=lambda a:(a[1],a[0]))
upperpoly=[(185,545),(280,489),(390,448),(520,420),(660,427),(780,459),(870,515),(923,604),(941,713),(910,804),(830,872),(710,914),(570,923),(420,895),(282,817),(205,711),(166,610)]
lowerpoly=[(458,1277),(475,1250),(542,1230),(641,1217),(733,1222),(815,1245),(876,1272),(895,1300),(836,1320),(710,1330),(588,1320),(489,1298)]
upper=detect(upperpoly,[(9,7),(11,9),(12,10)],28,20,(550,689,66,55))
lower=detect(lowerpoly,[(4,2),(5,2)],13,15,(678,1284,40,18))
# Visual triage: discard stream-crossing false positives in dense occluded areas.
upper=[q for q in upper if q[1]<=610]
lower=[q for q in lower if q[1]<=1240]
# Manual QA: separate upper mouth above existing lower mouth (715,1240).
lower.append([713,1229,999])
S=3; layer=Image.new('RGBA',(w*S,h*S));d=ImageDraw.Draw(layer);rng=random.Random(61023)
points={}
for name,pts,end in [('upper',upper,1094),('lower',lower,1478)]:
 points[name]=[]
 for i,(x,y,score) in enumerate(pts):
  pid=name+'-'+str(i+1).zfill(3);points[name].append({'id':pid,'x':x,'y':y,'detector_score':score,'water_origin':True})
  slope=(x-550)*.00048 if name=='upper' else (x-678)*.00018
  phase=rng.random()*6.28
  for offset in [-1.1,1.2]:
   last=None
   for dy in range(0,end-y+1,4):
    t=dy/max(1,end-y);xx=x+slope*dy+.45*math.sin(dy*.06+phase)+offset*(.3+.7*t);yy=y+dy
    if last:
     alpha=int((40+22*math.sin(dy*.025+phase)**2)*(1-.25*t))
     d.line((last[0]*S,last[1]*S,xx*S,yy*S),fill=(220,235,244,alpha),width=2)
    last=(xx,yy)
  # intermittent fine bright glints, not an opaque luminous rod
  for dy in range(4,end-y,19):
   if rng.random()<.45:continue
   xx=x+slope*dy;alpha=rng.randrange(35,85)
   d.line((xx*S,(y+dy)*S,(xx+slope*5)*S,(y+dy+5)*S),fill=(245,250,252,alpha),width=1)
layer=layer.resize((w,h),Image.Resampling.LANCZOS)
# Preserve chrome, buttons and external micro-hole annulus exactly; only allow
# water over the inner face and then free water after the projected face edge.
allow=Image.new('L',(w,h));ad=ImageDraw.Draw(allow)
ad.polygon(upperpoly,fill=255);ad.rectangle((0,929,w-1,1094),fill=255)
ad.polygon(lowerpoly,fill=255);ad.rectangle((0,1331,w-1,h-1),fill=255)
ad.ellipse((484,634,616,744),fill=0);ad.ellipse((638,1266,718,1302),fill=0)
# Extend only along each registered ray after its origin, retaining the plate's
# original pixels as immutable source; masks preserve all non-water pixels.
aa=np.asarray(layer).copy();aa[:,:,3]=(aa[:,:,3].astype(float)*np.array(allow)/255).astype('uint8');layer=Image.fromarray(aa)
com=Image.alpha_composite(im,layer)
layer.save(P/'water-layer.png');com.save(P/'composite.png');allow.save(P/'water-allow-mask.png')
diag=im.convert('RGB');dd=ImageDraw.Draw(diag)
for name,pts in points.items():
 for p in pts:
  x,y=p['x'],p['y'];dd.ellipse((x-7,y-7,x+7,y+7),outline='#ff6a00',width=2);dd.text((x+7,y-8),p['id'],fill='#ff6a00')
diag.save(P/'diagnostic-ports.jpg',quality=95)
(P/'port-coordinates.json').write_text(json.dumps(points,indent=2))
a=np.array(im);b=np.array(com);active=np.array(layer)[:,:,3]>0
ev={'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'size':[w,h],'upper_ports':len(upper),'lower_ports':len(lower),'base_image_redrawn':False,'outside_water_layer_changed_pixels':int(np.any(a!=b,2)[~active].sum()),'upper_water_below_y1094':int((np.array(layer)[1095:1190,:,3]>0).sum()),'red_button_upper_changed_pixels':int(np.any(a[649:730,510:590]!=b[649:730,510:590],2).sum()),'counts_are_candidates_pending_visual_QA':True,'coverage_limit':'Dense lower rows retain original streams; ambiguous water-crossing candidates discarded, not claimed as individually verified holes. Independent QA required.'}
(P/'pixel-protection-evidence.json').write_text(json.dumps(ev,indent=2));print(json.dumps(ev))

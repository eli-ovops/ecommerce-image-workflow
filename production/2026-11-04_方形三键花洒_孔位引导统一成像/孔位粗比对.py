from PIL import Image
import numpy as np,json
from pathlib import Path
p=Path(__file__).parent
src=json.loads(Path('production/2026-11-04_方形三键花洒_三维统一成像验证/465_白嘴提取.json').read_text())['items']
im=np.asarray(Image.open(p/'候选01_原生.png').convert('RGB'));x0,y0=675,75;a=im[y0:595,x0:1060];m=(a.min(axis=2)>150)&(a.max(axis=2)-a.min(axis=2)<80);h,w=m.shape;seen=np.zeros((h,w),bool);res=[]
for y in range(h):
 for x in range(w):
  if not m[y,x] or seen[y,x]:continue
  st=[(y,x)];seen[y,x]=True;pts=[]
  while st:
   yy,xx=st.pop();pts.append((yy,xx))
   for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
    u,v=yy+dy,xx+dx
    if 0<=u<h and 0<=v<w and m[u,v] and not seen[u,v]:seen[u,v]=True;st.append((u,v))
  if 28<len(pts)<800:
   cx=sum(t[1] for t in pts)/len(pts)+x0;cy=sum(t[0] for t in pts)/len(pts)+y0
   if (cx>1030 and cy>500) or (cx>1040 and cy<120):continue
   res.append({'x':round(cx,2),'y':round(cy,2),'area':len(pts),'kind':'heart' if len(pts)>480 else 'round'})
sh=sorted([v for v in src if v['kind']=='heart'],key=lambda v:-v['source_y']);dh=sorted([v for v in res if v['kind']=='heart'],key=lambda v:v['x']);print('白嘴源/候选:',len(src),len(res),'心形:',len(sh),len(dh))
# 图像旋转及仿射受透视和面板曲率影响，此项仅诊断可见对应，不是硬锁或实测。
S=np.array([[v['source_x'],v['source_y'],1] for v in sh]);D=np.array([[v['x'],v['y']] for v in dh]);S=np.vstack((S, np.array([[351,730,1],[351,600,1],[351,465,1],[550,730,1],[550,600,1],[550,465,1]]))); D=np.vstack((D,np.array([[755,267],[865,257],[979,249],[745,436],[857,430],[975,420]]))); M=np.linalg.lstsq(S,D,rcond=None)[0]
for kind in ['round','heart']:
 A=np.array([[v['source_x'],v['source_y'],1] for v in src if v['kind']==kind])@M; B=np.array([[v['x'],v['y']] for v in res if v['kind']==kind]);dist=np.linalg.norm(A[:,None,:]-B[None,:,:],axis=2);min_d=dist.min(axis=1); idx=dist.argmin(axis=1);print(kind,'source',len(A),'candidate',len(B),'median px',round(float(np.median(min_d)),1),'max px',round(float(max(min_d)),1),'matched unique',len(set(idx)),'>12px',int(sum(min_d>12)))
(p/'孔位粗比对.json').write_text(json.dumps({'source_white':len(src),'candidate_white':len(res),'source_hearts':len(sh),'candidate_hearts':len(dh),'note':'按七个心形和六个黑嘴近似中心估算仿射对应，再最近点粗比对；透视、摄影畸变、凹面影响，不等于真实三维位置或严格孔位验收','candidate_components':res},ensure_ascii=False,indent=2))

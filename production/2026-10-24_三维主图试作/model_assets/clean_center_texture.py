from pathlib import Path
from PIL import Image
import numpy as np,json
O=Path(__file__).resolve().parent;a=np.array(Image.open(O/'face-photo-rectified.png')).astype(float)
candidates=[]
for y in range(650,1400,16):
 for x in range(650,1400,16):
  if (x-1042)**2+(y-1065)**2<250**2:continue
  t=a[y:y+48,x:x+48]
  if t.shape!=(48,48,3):continue
  if t.max()<160 and t.min()>22:
   avg=t.mean();candidates.append((abs(avg-64)+abs(t.std()-15),x,y,avg))
_,dx,dy,avg=min(candidates);tile=a[dy:dy+48,dx:dx+48];yy,xx=np.mgrid[:2048,:2048];r=((xx-1042)**2+(yy-1065)**2)**.5;alpha=np.clip((183-r)/14,0,1);filled=tile[yy%48,xx%48];out=a*(1-alpha[:,:,None])+filled*alpha[:,:,None];Image.fromarray(np.clip(out,0,255).astype('uint8')).save(O/'face-photo-rectified-v003.png')
(O/'central-cleanup-provenance.json').write_text(json.dumps({'source':'face-photo-rectified.png','donor_rectangle_px':[dx,dy,48,48],'donor_mean_rgb':tile.mean(axis=(0,1)).tolist(),'destination_center_px':[1042,1065],'radius_px':183,'feather_px':14,'purpose':'Replace photographed old central control under the separate 3D red part with nearby real black panel grain; retain every detected nozzle location'},indent=2))
print('DONOR',dx,dy,avg)

from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
p=Path(__file__).parent;base=Image.open(p/'AD02-v002-native.png').convert('RGB');tool=Image.open(p/'AD02-roi-tool-native.png').convert('RGB')
source_box=(41,165,121,245);single=tool.crop(source_box);single.save(p/'AD02-v004-single-source.png');single=single.resize((21,21),Image.Resampling.LANCZOS);single.save(p/'AD02-v004-single-resampled.png')
canvas=base.copy();items=[{'id':'A','center':[455,208],'paste':[445,198],'radii':[9.5,9.5]},{'id':'B','center':[515,342],'paste':[505,332],'radii':[9.5,10]},{'id':'C','center':[706,382],'paste':[696,372],'radii':[10,10]}]
y,x=np.mgrid[0:base.height,0:base.width];alpha=np.zeros((base.height,base.width),dtype=np.uint8)
for e in items:
 canvas.paste(single,tuple(e['paste']));cx,cy=e['center'];rx,ry=e['radii'];r=np.sqrt(((x-cx)/rx)**2+((y-cy)/ry)**2);a=np.rint(np.clip((1-r)/0.1,0,1)*255).astype(np.uint8);alpha=np.maximum(alpha,a)
# Reuse only the previously effective D tail-removal area of actual tool patch.
roi=Image.open(p/'AD02-roi-resampled.png').convert('RGB');d_box=(551,193,568,206);tail=roi.crop((116,33,133,46));canvas.paste(tail,(551,193));tail.save(p/'AD02-v004-tail-source.png')
r=np.sqrt(((x-559)/8)**2+((y-199)/6)**2);a=np.rint(np.clip((1-r)/0.15,0,1)*255).astype(np.uint8);alpha=np.maximum(alpha,a)
mask=Image.fromarray(alpha);mask.save(p/'AD02-v004-mask.png');result=Image.composite(canvas,base,mask);result.save(p/'AD02-v004-composite.png');result.save(p/'AD02-v004-review.jpg',quality=95)
a=np.asarray(base);b=np.asarray(Image.open(p/'AD02-v004-composite.png').convert('RGB'));m=alpha>0;sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
def components(binary):
 v=binary.copy();h,w=v.shape;out=[]
 for yy in range(h):
  for xx in range(w):
   if not v[yy,xx]:continue
   todo=[(xx,yy)];v[yy,xx]=0;count=0
   while todo:
    qx,qy=todo.pop();count+=1
    for nx,ny in [(qx-1,qy),(qx+1,qy),(qx,qy-1),(qx,qy+1)]:
     if 0<=nx<w and 0<=ny<h and v[ny,nx]:v[ny,nx]=0;todo.append((nx,ny))
   if count>8:out.append(count)
 return out
counts={}
for e in items:
 cx,cy=e['center'];local=np.asarray(result.crop((cx-10,cy-10,cx+11,cy+11)));counts[e['id']]=components(local.min(axis=2)>160)
ev={'base':str(p/'AD02-v002-native.png'),'base_sha256':sha(p/'AD02-v002-native.png'),'tool_source':str(p/'AD02-roi-tool-native.png'),'tool_source_sha256':sha(p/'AD02-roi-tool-native.png'),'new_imagegen_calls':0,'single_ring_source_box_xyxy_exclusive':list(source_box),'single_ring_source_size':[80,80],'single_ring_resampled_size':[21,21],'single_ring_source_has_one_bright_connected_component':components(np.asarray(tool.crop(source_box)).min(axis=2)>160),'placements':items,'tail_removal':'D from same existing tool ROI; no new ring','tail_source_roi_crop_xyxy':[116,33,133,46],'tail_destination_xyxy':list(d_box),'mask':str(p/'AD02-v004-mask.png'),'mask_sha256':sha(p/'AD02-v004-mask.png'),'mask_pixels':int(m.sum()),'mask_fraction':float(m.sum()/m.size),'outside_changed_pixels':int(np.any(a[~m]!=b[~m],axis=1).sum()),'outside_max_channel_delta':int(abs(a[~m].astype(int)-b[~m].astype(int)).max()),'three_tight_roi_white_connected_component_areas':counts,'component_check_limit':'threshold160, components>8pixels; each tight21x21 destination contains one white ring component; this is local count not real-product nozzle mapping proof','output':str(p/'AD02-v004-composite.png'),'output_sha256':sha(p/'AD02-v004-composite.png'),'verification':'lossless PNG reopened, external pixels compared; no JPEG guarantee','previous_v003_retained':True,'method':'single actual AI patch ring extracted and uniformly scaled, individually positioned through tight masks; not original-photo clone, not drawn ring'}
(p/'AD02-v004-evidence.json').write_text(json.dumps(ev,ensure_ascii=False,indent=2))
# Native 1:1 crop pairs plus equal-scale larger viewing sheet.
comp=Image.new('RGB',(160,240),'white');draw=ImageDraw.Draw(comp)
for j,e in enumerate(items):
 cx,cy=e['center'];box=(cx-32,cy-32,cx+32,cy+32)
 for i,im in enumerate([base,result]):comp.paste(im.crop(box),(i*80,j*80+14))
 draw.text((2,j*80),e['id']+' v002',fill='black');draw.text((82,j*80),'v004',fill='black')
comp.save(p/'AD02-v004-before-after-1to1.png');comp.resize((640,960),Image.Resampling.NEAREST).save(p/'AD02-v004-before-after.jpg',quality=95)
print(json.dumps(ev,ensure_ascii=False,indent=2))

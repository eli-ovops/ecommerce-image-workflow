from pathlib import Path
from PIL import Image
import numpy as np,shutil,json,hashlib
p=Path(__file__).parent
src=Path('/Users/USER/.codex/generated_images/01a16d07-b34d-7ff3-afe5-dfc839dd6cb1/exec-db5e6152-f055-43cb-9262-ee5ca6cef425.png')
shutil.copy2(src,p/'AD02-roi-tool-native.png')
base=Image.open(p/'AD02-v002-native.png').convert('RGB')
patch=Image.open(src).convert('RGB').resize((300,300),Image.Resampling.LANCZOS);patch.save(p/'AD02-roi-resampled.png')
canvas=base.copy();canvas.paste(patch,(435,160))
y,x=np.mgrid[0:base.height,0:base.width];alpha=np.zeros((base.height,base.width),dtype=np.uint8)
ellipses=[{'id':'A','center':[455,208],'radii':[11,11]},{'id':'B','center':[515,342],'radii':[12,11]},{'id':'C','center':[704,382],'radii':[15,12]},{'id':'D_remove_tail','center':[559,199],'radii':[8,6]}]
for e in ellipses:
 cx,cy=e['center'];rx,ry=e['radii'];r=np.sqrt(((x-cx)/rx)**2+((y-cy)/ry)**2)
 a=np.rint(np.clip((1-r)/0.15,0,1)*255).astype(np.uint8);alpha=np.maximum(alpha,a)
mask=Image.fromarray(alpha);mask.save(p/'AD02-roi-mask.png')
result=Image.composite(canvas,base,mask);result.save(p/'AD02-v003-composite.png');result.save(p/'AD02-v003-review.jpg',quality=95)
a=np.asarray(base);b=np.asarray(Image.open(p/'AD02-v003-composite.png').convert('RGB'));m=alpha>0
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
ev={'base':str(p/'AD02-v002-native.png'),'base_sha256':sha(p/'AD02-v002-native.png'),'roi_rectangle_xyxy_exclusive':[435,160,735,460],'roi_original_size':[300,300],'edit_input_scale':3,'tool_output_path':str(src),'tool_native':str(p/'AD02-roi-tool-native.png'),'tool_native_sha256':sha(src),'tool_native_size':list(Image.open(src).size),'mapping':'uniform1254x1254 to300x300 Lanczos then paste435,160; no rotation/nonuniform warp','mask':str(p/'AD02-roi-mask.png'),'mask_sha256':sha(p/'AD02-roi-mask.png'),'mask_ellipses':ellipses,'feather':'alpha1 through normalized ellipse radius0.85, linear to0 at1.0','mask_pixels':int(m.sum()),'mask_fraction':float(m.sum()/m.size),'outside_changed_pixels':int(np.any(a[~m]!=b[~m],axis=1).sum()),'outside_max_channel_delta':int(abs(a[~m].astype(int)-b[~m].astype(int)).max()),'output':str(p/'AD02-v003-composite.png'),'output_sha256':sha(p/'AD02-v003-composite.png'),'verification':'lossless PNG reopened and compared; not JPEG pixel guarantee','not_fullframe_native_output':True,'not_exact_hole_mapping_claim':True}
(p/'AD02-roi-evidence.json').write_text(json.dumps(ev,ensure_ascii=False,indent=2))
comp=Image.new('RGB',(1200,600))
for i,im in enumerate([base,result]):comp.paste(im.crop((435,160,735,460)).resize((600,600)),(i*600,0))
comp.save(p/'AD02-roi-before-after.jpg',quality=95)
print(json.dumps(ev,ensure_ascii=False,indent=2))

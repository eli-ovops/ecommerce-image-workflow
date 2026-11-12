from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
p=Path(__file__).parent
base=Image.open(p/'R02-v001-native.png').convert('RGB')
source=Image.open(p/'R01-roi-tool-native.png').convert('RGB')
box=(380,480,640,740)
crop=source.crop(box);crop.save(p/'R02-reused-patch-source-crop.png')
patch=crop.resize((20,20),Image.Resampling.LANCZOS);patch.save(p/'R02-reused-patch-resampled.png')
canvas=base.copy();canvas.paste(patch,(651,462))
y,x=np.mgrid[0:base.height,0:base.width]
r=np.sqrt(((x-659.0)/9.7)**2+((y-472.7)/9.3)**2)
alpha=np.rint(np.clip((1-r)/0.06,0,1)*255).astype(np.uint8)
mask=Image.fromarray(alpha);mask.save(p/'R02-reuse-mask.png')
result=Image.composite(canvas,base,mask);result.save(p/'R02-v002-composite.png');result.save(p/'R02-v002-review.jpg',quality=95)
a=np.asarray(base);b=np.asarray(Image.open(p/'R02-v002-composite.png').convert('RGB'));m=alpha>0
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
ev={'operation':'Reuse actual image_gen ROI patch; deterministic crop/uniform-scale/masked-composite; zero new generation calls','source_original':str(p/'R02-v001-native.png'),'source_original_sha256':sha(p/'R02-v001-native.png'),'patch_tool_native':str(p/'R01-roi-tool-native.png'),'patch_tool_native_sha256':sha(p/'R01-roi-tool-native.png'),'patch_crop_rectangle_xyxy_exclusive':list(box),'patch_crop':str(p/'R02-reused-patch-source-crop.png'),'resample':'260x260 to20x20 uniform Lanczos, no rotation','paste_rectangle_xyxy_exclusive':[651,462,671,482],'observed_defect_dark_center_approx':[660.5,471.8],'projected_patch_dark_center_approx':[661.1,472.1],'center_limit':'subpixel visual estimates, center preserved to under1px, no intentional relocation','mask':str(p/'R02-reuse-mask.png'),'mask_sha256':sha(p/'R02-reuse-mask.png'),'mask_method':'ellipse center659.0,472.7 radii9.7,9.3; alpha full through normalized radius0.94, linear feather to0 at1.0','mask_nonzero_pixels':int(m.sum()),'outside_mask_pixels':int((~m).sum()),'outside_mask_changed_pixels':int(np.any(a[~m]!=b[~m],axis=1).sum()),'outside_mask_max_channel_delta':int(abs(a[~m].astype(int)-b[~m].astype(int)).max()),'output':str(p/'R02-v002-composite.png'),'output_sha256':sha(p/'R02-v002-composite.png'),'readback':'PNG reopened for actual pixel comparison; JPEG not covered by zero-change guarantee'}
(p/'R02-reuse-evidence.json').write_text(json.dumps(ev,ensure_ascii=False,indent=2))
comparison=Image.new('RGB',(1000,500))
for i,im in enumerate([base,result]):comparison.paste(im.crop((630,445,686,501)).resize((500,500)),(i*500,0))
comparison.save(p/'R02-reuse-before-after.jpg',quality=95)
print(json.dumps(ev,ensure_ascii=False,indent=2))

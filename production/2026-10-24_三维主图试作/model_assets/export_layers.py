from pathlib import Path
from PIL import Image
import json,hashlib,sys
O=Path(__file__).resolve().parent;R=O.parent/'renders';items=[]
for p in sorted(R.glob('*.png')):
 if p.name.endswith('-mask.png'):continue
 im=Image.open(p).convert('RGBA');alpha=im.getchannel('A');box=alpha.getbbox();alpha.save(p.with_name(p.stem+'-mask.png'))
 bg=Image.new('RGBA',im.size,(240,242,244,255));bg.alpha_composite(im);bg.convert('RGB').save(p.with_name(p.stem+'-review.jpg'),quality=95)
 items.append({'layer':str(p),'dimensions':list(im.size),'alpha_extrema':alpha.getextrema(),'product_alpha_bbox':box,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mask':str(p.with_name(p.stem+'-mask.png')),'review_only_jpg':str(p.with_name(p.stem+'-review.jpg'))})
(O/'render-layers.json').write_text(json.dumps(items,indent=2));print(json.dumps(items,indent=2))

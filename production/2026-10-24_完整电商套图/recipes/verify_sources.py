from pathlib import Path
from PIL import Image,ImageOps
import json,hashlib,numpy as np
B=Path(__file__).resolve().parents[1];ROOT=B.parents[1];G=B/'generated'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return ImageOps.exif_transpose(Image.open(p)).convert('RGB')
def rec(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
assets=json.loads((B/'design-output.json').read_text())['assets'];out={'outputs':[],'original_photo_layers':[],'cutout_rgb_checks':[],'reused_jpg_checks':[],'limitations':['Source-layer equality verifies deterministic compositing, not real-world product geometry or exact generated nozzle layout.','JPEG delivery uses normal compression. Exact RGB checks refer to saved intermediate PNG source layers.']}
for a in assets:
 p=ROOT/a['output']['path'];im=read(p);ok=sha(p)==a['output']['sha256'] and list(im.size)==a['dims'];out['outputs'].append({'id':a['id'],'sha_matches':ok,'dims':list(im.size),'decode':True})
 for l in a.get('source_layers',[]):
  if 'source' not in l:continue
  sp=ROOT/l['source']['path'];assert sp.exists() and sha(sp)==l['source']['sha256'],str(sp)
  if '/products/' in str(sp) and 'resampled_crop_layer' in l:
   src=read(sp);crop=l.get('source_crop');src=src.crop(crop) if crop else src;s=l['uniform_scale'];v=src.resize((round(src.width*s),round(src.height*s)),Image.Resampling.LANCZOS)
   if 'scaled_crop_offset' in l:
    x,y=l['scaled_crop_offset'];w,h=l['destination'][2:];v=v.crop((x,y,x+w,y+h))
   lp=ROOT/l['resampled_crop_layer']['path'];act=read(lp);arr=np.array(v).astype('int16');brr=np.array(act).astype('int16');maxdiff=int(abs(arr-brr).max());assert maxdiff==0
   whole=read(ROOT/a['working']['path']);x,y,w,h=l['destination'];cropfinal=np.array(whole.crop((x,y,x+w,y+h)));unchanged=int(np.all(cropfinal==np.array(act),axis=2).sum())
   out['original_photo_layers'].append({'asset':a['id'],'source':rec(sp),'saved_crop_layer':rec(lp),'source_crop':crop,'uniform_scale':s,'transform_recomputed_max_channel_delta':maxdiff,'final_png_matching_pixels':unchanged,'layer_pixels':w*h,'final_fraction_identical':round(unchanged/(w*h),6),'difference_note':'Remaining differences, if any, are caption overlays documented in design.py; source crop layer itself is exactly source-derived.'})
 if a.get('transform')=='byte copy, no recompression':out['reused_jpg_checks'].append({'id':a['id'],'same_sha':a['output']['sha256']==a['source_files'][0]['sha256']})
for f in G.glob('*-cutout-v003-evidence.json'):
 e=json.loads(f.read_text());src=read(ROOT/e['source']['path']).crop(e['crop_bbox']);got=Image.open(ROOT/e['output']['path']).convert('RGB');equal=np.array_equal(np.array(src),np.array(got));assert equal
 out['cutout_rgb_checks'].append({'evidence':rec(f),'original_rgb_unchanged':equal,'alpha_only':True})
old=np.array(Image.open(G/'D09-v004.png'));new=np.array(Image.open(G/'D09-v005.png'));allowed=np.zeros(old.shape[:2],bool)
for x in [65,570,1075]:allowed[395:735,x:x+466]=True
out['D09_top_row_only']={'outside_changed_pixels':int((np.any(old!=new,axis=2)&~allowed).sum()),'allowed_rectangles':[[x,395,466,340] for x in [65,570,1075]]}
assert len(assets)==24 and all(x['sha_matches'] for x in out['outputs']);(G/'source-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('Verified',len(assets),'outputs;',len(out['original_photo_layers']),'original-photo resampled layers;',len(out['cutout_rgb_checks']),'alpha-only RGB checks;',out['D09_top_row_only'])

"""Full-suite evidence checks. Manual visual and customer acceptance remain separate."""
from pathlib import Path
import hashlib,json
from PIL import Image

EXPECTED={*[f'M{i:02}' for i in range(1,9)],*[f'K{i:02}' for i in range(1,4)],*[f'D{i:02}' for i in range(1,10)],'W01','W02','L01','L02'}
REFERENCES={*[f'R{i:03}' for i in range(1,36)],*[f'A{i:03}' for i in range(1,40)]}

def evaluate(m,root,stage='review'):
 root=Path(root).resolve();issues=[]
 def fail(code,item,detail):issues.append({'code':code,'item':item,'detail':detail})
 def file(rec,item):
  if not isinstance(rec,dict) or not rec.get('path') or not rec.get('sha256'):
   fail('MISSING_FILE',item,'Current path/hash required');return None
  p=(root/rec['path']).resolve()
  if not p.is_relative_to(root) or not p.is_file():
   fail('INVALID_PATH',item,'Missing or outside project');return None
  if hashlib.sha256(p.read_bytes()).hexdigest()!=rec['sha256']:
   fail('HASH_CHANGED',item,'Current bytes differ');return None
  return p
 def read(rec,item):
  p=file(rec,item);return json.loads(p.read_text()) if p else {}
 if stage not in {'review','delivery'}:fail('STAGE','manifest','Unknown stage')
 if m.get('production_state')!='EXPERIMENT_ENABLED':fail('PAUSED','manifest','Not enabled')
 if m.get('source_priority')!='OWN_SKU_PHOTOS_PRIMARY_3D_SECONDARY' or m.get('hard_shape_lock') is not False:
  fail('FALSE_CONTROL_CLAIM','manifest','Cannot claim hard shape lock')
 if m.get('water_policy')!='REAL_PHOTOS_UNASSIGNED_MODES':fail('WATER_POLICY','manifest','User did not assign photographs to modes')
 assets=m.get('assets',[]);by_id={a.get('id'):a for a in assets}
 if len(assets)!=24 or set(by_id)!=EXPECTED:fail('SUITE_SCOPE','manifest','Need 22 distinct images and two composed long details')
 colors=[]
 for catalog in m.get('sku_photo_catalogs',[]):
  c=read(catalog,'sku_catalog');color=c.get('sku_color');colors.append({'silver':'银色'}.get(color,color))
  if c.get('asset_kind')!='real_product_photos':fail('SKU_CATALOGS','manifest','Own archived real-photo catalog required')
 if len(colors)!=3 or set(colors)!={'银色','黑色','枪灰色'}:fail('SKU_CATALOGS','manifest','Three distinct own-SKU catalogs required')
 coverage=read(m.get('reference_coverage'),'reference_coverage');rows=coverage.get('entries',[])
 if len(rows)!=74 or {x.get('reference_id') for x in rows}!=REFERENCES:fail('REFERENCE_SCOPE','coverage','All 74 distinct original reference entries required')
 for x in rows:
  rid=x.get('reference_id','?');out=x.get('outputs',[])
  if x.get('disposition')=='EXCLUDED_PORTRAIT':
   if not x.get('reason') or out:fail('COVERAGE',rid,'Explicit portrait cancellation only')
  elif not out or any(i not in by_id for i in out) or x.get('coverage_status')!='CHECKED_IN_CURRENT_SUITE':
   fail('COVERAGE',rid,'Applicable reference must bind checked current output')
 checked={}
 for a in assets:
  aid=a.get('id','?');p=file(a.get('output'),aid+':jpg')
  if a.get('has_model') is not False:fail('PORTRAIT',aid,'No model images in current suite')
  if not a.get('refs_actual_viewed'):fail('STYLE_REFERENCE',aid,'Related original reference required')
  for ref in a.get('refs_actual_viewed',[]):file(ref,aid+':style')
  inputs=a.get('actual_inputs',[])
  if not inputs:fail('LINEAGE',aid,'Actual photo/generated layer inputs required')
  for s in inputs:
   q=file(s,aid+':input')
   if q and any(old in str(q) for old in ['2026-10-23_造型重做/generated','2026-10-22_参考重构/generated','2026-10-22_花洒套图/generated']):
    fail('REJECTED_PRODUCT_SOURCE',aid,'Do not revive old rejected geometry')
  if a.get('has_water'):
   photos=a.get('water_photo_sources',[])
   if not photos or a.get('water_mode_assignment') is not None:fail('WATER_MAPPING',aid,'Real photos only; no per-photo mode label')
   for s in photos:
    q=file(s,aid+':water_photo')
    if q and '/products/主推花洒/银色/原图/' not in str(q):fail('WATER_SOURCE',aid,'Must be own archived original photograph')
  if p:
   with Image.open(p) as im:
    im.load()
    if im.format!='JPEG' or list(im.size)!=a.get('dims'):fail('JPG_EXPORT',aid,'Correct JPEG and actual canvas required')
   checked[aid]=a['output']['sha256']
  review=read(a.get('review'),aid+':review')
  if review.get('status')!='PASS' or review.get('jpg_sha256')!=a.get('output',{}).get('sha256') or not review.get('reviewer') or not review.get('finding') or not review.get('reviewed_at') or not all(review.get('checks',{}).get(k)=='PASS' for k in ['product','reference_style','copy','layout','export']):
   fail('VISUAL_REVIEW',aid,'Actual current product/style/copy/layout/JPG review required')
  if aid in {'L01','L02'} and (not a.get('children') or any(i not in EXPECTED-{'L01','L02'} for i in a.get('children',[]))):fail('LONG_DETAIL',aid,'Ordered current child panels required')
 if len(set(checked.values()))!=len(checked):fail('DUPLICATE_OUTPUT','manifest','No duplicate final roles')
 if stage=='delivery':
  accept=read(m.get('client_acceptance'),'client_acceptance')
  if accept.get('status')!='ACCEPTED' or accept.get('accepted_jpg_sha256')!=checked:fail('CUSTOMER_ACCEPTANCE','manifest','Current JPEG customer receipt missing')
 return {'stage':stage,'status':'REJECTED' if issues else 'PASS','issues':issues,'checked_jpg_count':len(checked),'limits':'Hash, scope, source, explicit water labeling and manual-review receipts only. No automatic product shape/style/flow recognition or customer acceptance. Source layers may include photo-guided generated product images, distinguished from original water/press photographs.'}

"""Incremental, JPG-only export of three independently reviewed local composites."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from html.parser import HTMLParser
from urllib.parse import unquote,quote
import hashlib,json,shutil,zipfile
W=Path(__file__).resolve().parent; B=W.parent.parent; BACK=W/'before-local-selection'
IDS=['D04','D06','D11']; STATUS='LOCAL_WATER_REPAIRED_CANDIDATE_USER_REVIEW_PENDING'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def preserve(p):
 if p.is_file():
  q=BACK/p.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True)
  assert not q.exists(),'Will not overwrite backup: '+str(q)
  shutil.copy2(p,q)
assert not (W/'selection-export-receipt.json').exists(),'Already applied'
review=read(W/'independent-local-water-review.json')
# Gate is finalized from current independently inspected candidates.
assert len(review['items'])==3 and sum(len(r['scenes']) for r in review['items'])==6
for id in IDS:
 r=next(r for r in review['items'] if r['id']==id)
 assert r['verdict']=='PASS_WITH_LIMITS' and all(s['status']=='PASS_WITH_LIMITS' for s in r['scenes'])
 assert r['sha256']==sha(W/(id+'-local')/'composite.png')
proof=read(W/'root-pixel-protection.json')
for id in IDS:
 assert proof[id]['candidate_sha256']==sha(W/(id+'-local')/'composite.png')
 assert proof[id]['outside_water_alpha_changed_pixels']==0
 assert all(x==0 for x in proof[id]['protected_boxes_changed_pixels'].values())
delivery=read(B/'delivery-manifest.json'); manifest=read(B/'image-manifest.json');ref=read(B/'reference-map.json');qa=read(B/'qa-review.json');check=read(B/'delivery-check.json');root=read(B/'root-delivery-review.json');prompts=read(B/'prompt-set.json')
unchanged={r['id']:sha(B/r['jpg']) for r in delivery['assets'] if r['id'] not in IDS}
meta=['delivery-manifest.json','image-manifest.json','reference-map.json','qa-review.json','qa-review.md','delivery-check.json','root-delivery-review.json','prompt-set.json','README.md','交付总览.html']
for p in meta:preserve(B/p)
selected=[]
for id in IDS:
 src=W/(id+'-local')/'composite.png';target=B/'final'/f'{id}.png';jpg=B/'exports/JPG'/f'{id}.jpg'
 preserve(target);preserve(jpg);shutil.copy2(src,target)
 with Image.open(src) as im:im.convert('RGB').save(jpg,quality=95,subsampling=0,optimize=True);dims=list(im.size)
 fingerprint=sha(src);selected.append({'id':id,'source':str(src),'native_sha256':fingerprint,'jpg_sha256':sha(jpg),'dimensions':dims})
 a=next(a for a in manifest['assets'] if a['id']==id);a.update(output=str(target),selected_source=str(src),sha256=fingerprint,actual_dimensions=dims,qa_status='PASS_WITH_LIMITATIONS',user_acceptance='PENDING',postprocess_method='local layered water composite from frozen geometry candidate')
 t=next(a for a in ref['actual_execution_32'] if a['id']==id);t.update(output=str(target),selected_sha256=fingerprint,production_status='LOCAL_WATER_REPAIR_PASS_WITH_LIMITATIONS',user_acceptance='PENDING')
 r=next(a for a in delivery['assets'] if a['id']==id);r.update(jpg_sha256=sha(jpg),visual_qa='PASS_WITH_LIMITATIONS',water_status='SIX_SCENES_INDEPENDENT_VISUAL_REVIEW_PASS_WITH_LIMITATIONS')
 p=next(a for a in prompts['assets'] if a['id']==id);p.update(selected_sha256=fingerprint,current_selected_source=str(src),local_postprocess={'user_authorized':True,'base':str(W/'before-water'/f'{id}.png'),'water_layer':str(W/(id+'-local')/'water-layer.png'),'method':'additive RGBA water only; no model call'})
 old=next((r for r in reversed(qa['reviews']) if r['id']==id),{})
 qa['reviews'].append({'id':id,'revision':'water-feedback-reopened-20261023','image_path':str(W/'before-water'/f'{id}.png'),'sha256':sha(W/'before-water'/f'{id}.png'),'overall_status':'FAIL_WATER_PARTIAL_VISIBLE_PORTS','evidence':'video-geometry-repair/water-feedback-20261023/independent-baseline.json','user_acceptance':'REJECTED_WATER'})
 entry=dict(old);entry.update(revision='local-water-20261023',image_path=str(src),sha256=fingerprint,overall_status='PASS_WITH_LIMITATIONS',candidate_only=True,user_acceptance='PENDING',water_review='video-geometry-repair/water-feedback-20261023/independent-local-water-review.json',pixel_protection='Lossless composite matches frozen base outside water alpha; faces, clothing, text, keys and grips separately tested; JPEG is lossy.',limitations=['保持既有造型候选，不证明精确3D；新增水线是视觉表达，不证明实测流量。','原有皮肤/商品底图未重绘；仅新增水流，JPG编码有损。'])
 entry['skin_review']={'status':'UNCHANGED_FROM_FROZEN_BASE','reason':'本轮不重绘人物；无损合成人物区域像素变化0，未宣称修复底图既有皮肤纹理。'}
 entry['actual_model']='NOT_APPLICABLE_LOCAL_COMPOSITE'
 qa['reviews'].append(entry)
# Affected scroll only. Old warm route remains untouched.
cold=next(r for r in delivery['scrolls'] if r['source_ids'][0].startswith('D'));preserve(B/cold['path']);pieces=[];ranges={};y=0
for r in delivery['assets']:
 if r['id'].startswith('D'):
  with Image.open(B/'final'/(r['id']+'.png')) as im:
   h=round(im.height*790/im.width);pieces.append(im.convert('RGB').resize((790,h),Image.Resampling.LANCZOS));ranges[r['id']]=[y,y+h];y+=h
scroll=Image.new('RGB',(790,y),'white');y=0
for im in pieces:scroll.paste(im,(0,y));y+=im.height
scroll.save(B/cold['path'],quality=95,subsampling=0,optimize=True);cold.update(sha256=sha(B/cold['path']),dimensions=list(scroll.size))
for id in IDS:
 lo,hi=ranges[id];scroll.crop((0,max(0,lo-80),790,min(scroll.height,hi+80))).save(W/('assembly-QC-'+id+'.jpg'),quality=94)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',23)
for start in [8,16]:
 p=B/'previews'/f'overview_{start//8+1:02d}.jpg';preserve(p);im=Image.new('RGB',(1600,1240),'#eeeef0');d=ImageDraw.Draw(im)
 for j,r in enumerate(delivery['assets'][start:start+8]):
  x,y=j%4*400,j//4*620
  with Image.open(B/r['jpg']) as src:
   src.thumbnail((372,558),Image.Resampling.LANCZOS);im.paste(src,(x+(400-src.width)//2,y+10+(558-src.height)//2))
  d.text((x+15,y+578),r['id'],fill='#222',font=font)
 im.save(p,quality=94,subsampling=0,optimize=True)
archive=B/'花洒_水流分层修正_JPG.zip';mini=W/'水流修正3张_JPG.zip'
for path,files in [(archive,[B/r['jpg'] for r in delivery['assets']]+[B/r['path'] for r in delivery['scrolls']]),(mini,[B/'exports/JPG'/f'{id}.jpg' for id in IDS])]:
 assert not path.exists(),'Do not overwrite archive'
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for f in files:z.write(f,str(f.relative_to(B)) if path==archive else f.name)
 with zipfile.ZipFile(path) as z:assert z.testzip() is None and len(z.namelist())==len(files) and all(f.endswith('.jpg') for f in z.namelist())
for id,v in unchanged.items():assert sha(B/'exports/JPG'/f'{id}.jpg')==v
for r in delivery['assets']:
 with Image.open(B/r['jpg']) as im:im.load();assert im.format=='JPEG' and list(im.size)==r['native_dimensions']
 assert r['jpg_sha256']==sha(B/r['jpg'])
gallery=(B/'交付总览.html').read_text();start=gallery.find('<!-- water-feedback-reopened -->')
# Remove only the previous feedback banner if present; preserve the gallery layout.
import re
gallery=re.sub(r'<div[^>]*>[^<]*最新反馈：D04[^<]*</div>','',gallery)
gallery=gallery.replace(quote('花洒_视频校准修订_JPG.zip'),quote(archive.name)).replace(quote('video-geometry-repair/本轮修正3张_JPG.zip'),quote(str(mini.relative_to(B))))
gallery=gallery.replace('本轮修正 D04、D06、D11；D04/D11从原始模特素材重新生成。','D04、D06、D11已采用本地分层补水，人物与商品底图未重绘；本轮六个场景已逐孔口复查。')
gallery=gallery.replace('本轮已修','本轮水流已修').replace('花洒·视频校准修订候选','花洒·水流分层修正候选')
# Earlier banner may be a paragraph inserted immediately after body/header.
gallery=re.sub(r'<p[^>]*>[^<]*最新反馈：D04[^<]*</p>','',gallery)
(B/'交付总览.html').write_text(gallery)
class Links(HTMLParser):
 def handle_starttag(self,t,attrs):
  for k,v in attrs:
   if k in ('href','src'):assert (B/unquote(v)).is_file() and not v.lower().endswith('.png'),v
Links().feed(gallery)
arc={'path':archive.name,'sha256':sha(archive),'bytes':archive.stat().st_size,'file_count':34}
for obj in [delivery,check,root]:obj.update(status=STATUS,user_acceptance='PENDING',modified_ids=IDS,client_archive=archive.name)
delivery['water_revision']={'method':'user-approved local layered compositing','review':str((W/'independent-local-water-review.json').relative_to(B)),'all_six_scenes_internal_review':'PASS_WITH_LIMITATIONS'}
check.update(archive=arc,water_feedback={'affected_ids':IDS,'status':'REPAIRED_INTERNAL_REVIEW_PASS_WITH_LIMITATIONS','user_acceptance':'PENDING','method':'local layered compositing'},incremental_checks={'unchanged_29_jpegs_same_hash':True,'six_water_scenes_independently_viewed':True,'outside_water_alpha_unchanged_lossless':True,'jpg_dimensions_decode':True,'archive_crc_jpg_only_34':True,'gallery_links':True})
root['water_increment']={'selected':selected,'review':str(W/'independent-local-water-review.json'),'assembly_review':'PENDING','overviews':['previews/overview_02.jpg','previews/overview_03.jpg'],'limitations':'Geometry suspects M03/D15/V01/V06 persist; customer acceptance pending.'}
ref.update(execution_status=STATUS,current_user_acceptance='PENDING',user_acceptance='PENDING');qa.update(batch_status=STATUS,user_acceptance='PENDING',latest_increment={'ids':IDS,'status':STATUS,'method':'local layered water only'})
qa['latest_status_by_id']={r['id']:r['overall_status'] for r in qa['reviews']}
for path,obj in [('delivery-manifest.json',delivery),('image-manifest.json',manifest),('reference-map.json',ref),('qa-review.json',qa),('delivery-check.json',check),('root-delivery-review.json',root),('prompt-set.json',prompts)]:write(B/path,obj)
with (B/'qa-review.md').open('a') as f:f.write('\n\n## 2026-10-23 水流分层修正\nD04/D06/D11六场景经独立放大复查，新增水线从现有白孔发出；保留人物/商品底图。内部PASS_WITH_LIMITATIONS，客户验收待定。相关证据：video-geometry-repair/water-feedback-20261023/。\n')
(B/'README.md').write_text('# 花洒·水流分层修正候选\n\nD04、D06、D11已按现有白孔补水，保留既有人物与商品底图；六场景已放大复查。其余29张JPG文件未改。\n\n[图片总览](交付总览.html)\n\n[下载32张JPG及两条长图]('+archive.name+')\n\n[仅下载水流修正3张]('+str(mini.relative_to(B))+')\n\nM03、D15、V01、V06仍保留此前低置信造型疑点，待客户核对。当前为审阅候选；不证明精确3D或实测流量，客户验收待定。JPG为交付格式；原件、旧版、失败候选、内部无损源和水层保留。\n')
receipt={'status':STATUS,'selected':selected,'unchanged_29_jpg_hashes':unchanged,'full_archive':arc,'mini_archive':{'path':str(mini.relative_to(B)),'sha256':sha(mini),'file_count':3},'assembly_review':'PENDING','user_acceptance':'PENDING'}
write(W/'selection-export-receipt.json',receipt)
print(json.dumps(receipt,ensure_ascii=False,indent=2))

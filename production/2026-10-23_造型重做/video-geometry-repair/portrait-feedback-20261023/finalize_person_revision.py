from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from urllib.parse import quote,unquote
from html.parser import HTMLParser
import json,shutil,hashlib,zipfile,re
W=Path(__file__).resolve().parent;B=W.parent.parent;IDS=['D04','D11'];BACK=W/'before-selection';STATUS='PORTRAIT_REPAIRED_CANDIDATE_USER_REVIEW_PENDING'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def preserve(p):
 if p.is_file():
  q=BACK/p.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);assert not q.exists(),str(q);shutil.copy2(p,q)
assert not (W/'selection-export-receipt.json').exists(),'Already applied'
selection=read(W/'selection-decision.json');assert selection['all_three_portraits_independent_pass'] is True
for id in IDS:assert selection['selected_sha256'][id]==sha(W/(id+'-portrait-new-person.png'))
proof=read(W/'root-product-water-preservation.json')
for id in IDS:
 assert proof[id]['candidate_sha256']==selection['selected_sha256'][id]
 assert proof[id]['outside_person_mask_changed_pixels']==proof[id]['water_layer_pixels_changed']==0
 assert all(v==0 for v in proof[id]['protected_regions_changed_pixels'].values())
d=read(B/'delivery-manifest.json');m=read(B/'image-manifest.json');r=read(B/'reference-map.json');qa=read(B/'qa-review.json');ck=read(B/'delivery-check.json');root=read(B/'root-delivery-review.json');ps=read(B/'prompt-set.json')
unchanged={x['id']:sha(B/x['jpg']) for x in d['assets'] if x['id'] not in IDS}
for p in ['delivery-manifest.json','image-manifest.json','reference-map.json','qa-review.json','qa-review.md','delivery-check.json','root-delivery-review.json','prompt-set.json','README.md','交付总览.html']:preserve(B/p)
selected=[]
for id in IDS:
 src=W/(id+'-portrait-new-person.png');dest=B/'final'/(id+'.png');jpg=B/'exports/JPG'/(id+'.jpg');preserve(dest);preserve(jpg);shutil.copy2(src,dest)
 with Image.open(src) as im:im.convert('RGB').save(jpg,quality=95,subsampling=0,optimize=True);dims=list(im.size)
 a=next(x for x in m['assets'] if x['id']==id);a.update(output=str(dest),selected_source=str(src),sha256=sha(src),qa_status='PASS_WITH_LIMITATIONS',user_acceptance='PENDING',postprocess_method='Fresh M001 face and neck locally composited; product/water frozen')
 t=next(x for x in r['actual_execution_32'] if x['id']==id);t.update(selected_sha256=sha(src),production_status='PORTRAIT_REPLACEMENT_PASS_WITH_LIMITATIONS',user_acceptance='PENDING')
 row=next(x for x in d['assets'] if x['id']==id);row.update(jpg_sha256=sha(jpg),visual_qa='PASS_WITH_LIMITATIONS',person_status='PASS_WITH_LIMITATIONS')
 old=next(x for x in reversed(qa['reviews']) if x['id']==id);entry=dict(old)
 qa['reviews'].append({'id':id,'revision':'person-feedback-reopened','overall_status':'FAIL_PERSON_ARTIFICIAL_SKIN','sha256':sha(W/'before-person'/(id+'.png')),'evidence':'video-geometry-repair/portrait-feedback-20261023/independent-person-baseline.json'})
 entry.update(revision='fresh-person-20261023',image_path=str(src),sha256=sha(src),overall_status='PASS_WITH_LIMITATIONS',skin_review={'status':'PASS_WITH_LIMITATIONS','evidence':'video-geometry-repair/portrait-feedback-20261023/independent-person-final.json','method':'Complete freshly rendered M001 faces and necks replace rejected regions; no skin blur, no previous rejected-face texture carried forward'},product_fidelity={'status':'UNCHANGED_LOSSLESS','reason':'All corrected water layer pixels and selected product/text/hand regions identical to frozen approved water base'},user_acceptance='PENDING',actual_model='UNKNOWN',actual_effort='UNKNOWN',limitations=['内部人像核验通过不代表用户验收','JPG有损编码；像素保护证据针对无损源','整套V01水膜下肤感仍UNKNOWN；此前4张造型疑点保留'])
 qa['reviews'].append(entry)
 p=next(x for x in ps['assets'] if x['id']==id);p.update(selected_sha256=sha(src),current_selected_source=str(src),portrait_postprocess={'fresh_source':str(W/'fresh-portrait-v2.png'),'production_record':str(W/'production-record.json'),'script':str(W/'compose_new_person.py'),'selected_sha256':sha(src)})
 selected.append({'id':id,'native_source':str(src),'native_sha256':sha(src),'jpg_sha256':sha(jpg),'dimensions':dims})
# Update only the cold detail scroll.
cold=next(x for x in d['scrolls'] if x['source_ids'][0].startswith('D'));preserve(B/cold['path']);pieces=[];ranges={};y=0
for x in d['assets']:
 if x['id'].startswith('D'):
  with Image.open(B/'final'/(x['id']+'.png')) as im:
   h=round(im.height*790/im.width);pieces.append(im.convert('RGB').resize((790,h),Image.Resampling.LANCZOS));ranges[x['id']]=[y,y+h];y+=h
scroll=Image.new('RGB',(790,y),'white');y=0
for im in pieces:scroll.paste(im,(0,y));y+=im.height
scroll.save(B/cold['path'],quality=95,subsampling=0,optimize=True);cold.update(sha256=sha(B/cold['path']),dimensions=list(scroll.size))
for id in IDS:
 lo,hi=ranges[id];scroll.crop((0,max(0,lo-60),790,min(scroll.height,hi+60))).save(W/('assembly-QC-'+id+'.jpg'),quality=94)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',23)
for start in [8,16]:
 path=B/'previews'/f'overview_{start//8+1:02d}.jpg';preserve(path);o=Image.new('RGB',(1600,1240),'#eeeef0');draw=ImageDraw.Draw(o)
 for j,x in enumerate(d['assets'][start:start+8]):
  X,Y=j%4*400,j//4*620
  with Image.open(B/x['jpg']) as im:
   im.thumbnail((372,558),Image.Resampling.LANCZOS);o.paste(im,(X+(400-im.width)//2,Y+10+(558-im.height)//2))
  draw.text((X+15,Y+578),x['id'],fill='#222',font=font)
 o.save(path,quality=94,subsampling=0,optimize=True)
# Review comparison, excluded from the client product archive.
boxes=[('D04',(515,180,785,660)),('D11',(420,80,680,435)),('D11',(235,975,500,1360))]
cmp=Image.new('RGB',(1080,940),'white');draw=ImageDraw.Draw(cmp)
for j,(id,box) in enumerate(boxes):
 for n,source in enumerate([W/'before-person'/(id+'.png'),W/(id+'-portrait-new-person.png')]):
  with Image.open(source) as im:
   t=im.crop(box);t.thumbnail((344,422),Image.Resampling.LANCZOS);cmp.paste(t,(j*360+(360-t.width)//2,n*470+35+(422-t.height)//2))
  draw.text((j*360+12,n*470+8),id+(' BEFORE' if n==0 else ' AFTER'),font=font,fill='#222')
cmp.save(W/'人像修正前后对比.jpg',quality=95,subsampling=0,optimize=True)
archive=B/'花洒_人物与水流修订_JPG.zip';mini=W/'人物修正2张_JPG.zip'
for path,files in [(archive,[B/x['jpg'] for x in d['assets']]+[B/x['path'] for x in d['scrolls']]),(mini,[B/'exports/JPG'/(id+'.jpg') for id in IDS])]:
 assert not path.exists(),str(path)
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in files:z.write(p,str(p.relative_to(B)) if path==archive else p.name)
 with zipfile.ZipFile(path) as z:assert z.testzip() is None and len(z.namelist())==len(files) and all(x.endswith('.jpg') for x in z.namelist())
for id,v in unchanged.items():assert sha(B/'exports/JPG'/(id+'.jpg'))==v
for x in d['assets']:
 with Image.open(B/x['jpg']) as im:im.load();assert im.format=='JPEG' and list(im.size)==x['native_dimensions']
 assert sha(B/x['jpg'])==x['jpg_sha256']
s=(B/'交付总览.html').read_text();s=re.sub(r'<p[^>]*>人物反馈已重开：[^<]*</p>','',s)
s=s.replace(quote('花洒_水流分层修正_JPG.zip'),quote(archive.name)).replace(quote('video-geometry-repair/water-feedback-20261023/水流修正3张_JPG.zip'),quote(str(mini.relative_to(B))))
s=s.replace('花洒·水流分层修正候选','花洒·人物与水流修订候选').replace('仅下载本轮修正3张','仅下载人物修正2张')
s=s.replace('D04、D06、D11已采用本地分层补水，人物与商品底图未重绘；本轮六个场景已逐孔口复查。','D04、D06、D11的水流已按孔位分层修复；本轮另更新D04、D11的人像，商品与已修水流保留。')
s=s.replace('<header>','<header><p class="note">本轮D04、D11的三处人像已换用新生成的完整脸颈，商品、水流与手持区域保留。V01水膜下肤感仍待核；整套仍为审阅候选。</p>',1)
for id in IDS:s=s.replace(id+' · '+next(x['title'] for x in d['assets'] if x['id']==id)+' · 本轮水流已修',id+' · '+next(x['title'] for x in d['assets'] if x['id']==id)+' · 人物与水流已修')
(B/'交付总览.html').write_text(s)
class Links(HTMLParser):
 def handle_starttag(self,t,attrs):
  for k,v in attrs:
   if k in ['href','src']:assert (B/unquote(v)).is_file() and not v.lower().endswith('.png'),v
Links().feed(s)
arc={'path':archive.name,'sha256':sha(archive),'bytes':archive.stat().st_size,'file_count':34}
for obj in [d,ck,root]:obj.update(status=STATUS,user_acceptance='PENDING',modified_ids=IDS,client_archive=archive.name)
d['person_revision']={'ids':IDS,'portrait_scenes':3,'status':'INTERNAL_PASS_WITH_LIMITATIONS','unknown_person_ids':['V01']}
ck.update(archive=arc,portrait_feedback={'status':'REPAIRED_INTERNAL_PASS_WITH_LIMITATIONS','repaired_ids':IDS,'unknown':['V01'],'user_acceptance':'PENDING'})
ck['incremental_checks'].update(unchanged_30_jpg_hashes=True,three_new_portraits_independent_review=True,product_water_lossless_unchanged=True,person_export_visual_review='PENDING')
root.update(archive_sha256=sha(archive));root['portrait_increment']={'selected':selected,'review':'video-geometry-repair/portrait-feedback-20261023/independent-person-final.json','preservation':'video-geometry-repair/portrait-feedback-20261023/root-product-water-preservation.json','assembly_review':'PENDING'}
r.update(execution_status=STATUS,current_user_acceptance='PENDING',user_acceptance='PENDING');qa.update(batch_status=STATUS,user_acceptance='PENDING',latest_increment={'ids':IDS,'status':STATUS,'method':'fresh M001 complete face and neck replacement'})
qa['latest_status_by_id']={x['id']:x['overall_status'] for x in qa['reviews']}
for path,obj in [('delivery-manifest.json',d),('image-manifest.json',m),('reference-map.json',r),('qa-review.json',qa),('delivery-check.json',ck),('root-delivery-review.json',root),('prompt-set.json',ps)]:write(B/path,obj)
with (B/'qa-review.md').open('a') as f:f.write('\n\n## 2026-10-23 人像失真返修\nD04/D11三处人像换用新生成完整脸颈，保持商品与水流。独立复核与当前SHA见portrait-feedback-20261023。V01水膜下肤感UNKNOWN，当前整套仍待用户验收。\n')
(B/'README.md').write_text('# 花洒·人物与水流修订候选\n\nD04、D11三处人像已用新生成的完整脸颈替换，商品、水流与手持关系保留。其余30张JPG未改。\n\n[图片总览](交付总览.html)\n\n[下载32张JPG及两条长图]('+archive.name+')\n\n[仅下载人物修正2张]('+str(mini.relative_to(B))+')\n\n[人像前后对比]('+str((W/'人像修正前后对比.jpg').relative_to(B))+')\n\n当前内部核验通过，用户验收待定。V01水膜下肤感UNKNOWN；M03、D15、V01、V06此前低置信造型疑点继续保留，整套不是全部已验收版本。旧图、原件与失败候选均保留，只交付JPG。\n')
receipt={'status':STATUS,'selected':selected,'unchanged_30_jpg_hashes':unchanged,'full_archive':arc,'mini_archive':{'path':str(mini.relative_to(B)),'sha256':sha(mini),'file_count':2},'assembly_review':'PENDING','user_acceptance':'PENDING','unresolved':['V01 person surface under water film UNKNOWN','M03/D15/V01/V06 low confidence geometry suspects retained']}
write(W/'selection-export-receipt.json',receipt);print(json.dumps({k:v for k,v in receipt.items() if k!='unchanged_30_jpg_hashes'},ensure_ascii=False,indent=2))

from pathlib import Path
from PIL import Image,ImageChops
import hashlib,json,shutil,zipfile,io,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent;P=ROOT/'lighting-refine';R=ROOT.parents[1]
B=R/'production/2026-11-03_\u9876\u55b7\u6574\u5957_\u7b2c\u4e09\u5f20\u4e24\u4e2a\u7248\u672c/\u9876\u55b7\u6574\u5957_\u7b2c\u4e09\u5f20\u4e24\u4e2a\u7248\u672c'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
D=P/'editable/396';base=Image.open(D/'original-base.png').convert('RGBA');layer=Image.open(D/'source-correction-layer.png').convert('RGBA');merged=Image.open(D/'merged.png').convert('RGBA')
assert ImageChops.difference(Image.alpha_composite(base,layer),merged).convert('RGB').getbbox() is None
root=ET.Element('image',w=str(base.width),h=str(base.height));stack=ET.SubElement(root,'stack')
with zipfile.ZipFile(D/'layers.ora','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('mimetype','image/openraster')
 for name,im,src in [('Three source-corrected windows',layer,'data/correction.png'),('Previous unchanged base',base,'data/base.png')]:
  b=io.BytesIO();im.save(b,format='PNG');z.writestr(src,b.getvalue());ET.SubElement(stack,'layer',name=name,src=src,x='0',y='0',opacity='1.0',visibility='visible',**{'composite-op':'svg:src-over'})
 z.writestr('stack.xml',ET.tostring(root));b=io.BytesIO();merged.save(b,format='PNG');z.writestr('mergedimage.png',b.getvalue())
unchanged_396={}
for name,box in [('main_title',(0,0,940,220)),('silver_side',(20,675,468,1078)),('connector',(477,675,921,1078)),('actual_short_pins',(477,1090,921,1618))]:
 unchanged_396[name]=ImageChops.difference(base.crop(box),merged.crop(box)).convert('RGB').getbbox() is None
assert all(unchanged_396.values())
layerchecks={}
for n in [387,399]:
 for i in [0,3,4]:
  a=Image.open(P/'editable'/str(n)/('layer%d.png'%i)).convert('RGBA')
  b=Image.open(R/'production/2026-11-03_\u9876\u55b7\u4e24\u5f20\u7ec6\u8282\u56de\u6e90\u4fee\u8ba2/editable'/str(n)/('layer%d.png'%i)).convert('RGBA')
  layerchecks['%d-layer%d'%(n,i)]=a.size==b.size and a.tobytes()==b.tobytes()
assert all(layerchecks.values())
(P/'layer-pixel-verification.json').write_text(json.dumps(layerchecks,indent=2))
review={'status':'THREE_IMPROVED_REVIEW_CANDIDATES_TWO_UNRESOLVED','updated':[387,396,399],'preserved_unresolved':[392,395],'visual_review':{'387':'Continuous sidewall with reduced blown highlights; orange-red shallow knob; closer contact shadow; some composite appearance remains','399':'Continuous gray/silver sidewall; orange-red knob; tighter shadow; original photographic face lighting remains baked','396':'Three corrected windows use original372 photo and current native shell; no added red pins; true382 short-pin detail unchanged'},'392_395_reason':{'source_382':'Hand obscures knob/upper panel; frame does not contain complete unobstructed silver product; outer SKU cannot be confirmed from this shot','missing':'Confirmed pull stroke, complete raised-pin state and unobstructed whole silver product in pulled state','decision':'Keep previous image unchanged; do not replace with reset texture or invent red pin positions; unchanged does not mean accepted'},'396_preserved_pixel_checks':unchanged_396,'native_geometry_verified':'native-reopen-verification.json','limited_highlight_measure':'highlight-check.json; selected sidewall ROI only, not full material realism score','customer_acceptance':'UNKNOWN','actual_runtime_model':'UNKNOWN','failed_candidate':'review/396-rejected-patch-v1.jpg has rectangular seams and is excluded'}
(P/'quality-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2))
(P/'README.md').write_text('''# \u9876\u55b7\u4fa7\u539a\u4e0e\u5149\u8272\u4fee\u8ba2\uff1a3\u5f20\u66f4\u65b0\u30012\u5f20\u4fdd\u7559\u5f85\u8865

\u6700\u65b0\u5019\u9009387\u3001396\u3001399\u3002\u76f8\u8f83\u4e0a\u4e00\u8f6e\uff1a387/399\u964d\u4f4e\u4fa7\u58c1\u9ad8\u5149\u3001\u6062\u590d\u5b9e\u62cd\u6a59\u7ea2\u94ae\u8272\uff0c\u6536\u7d27\u63a5\u89e6\u9634\u5f71\uff1b\u80cc\u666f\u3001\u6587\u5b57\u3001\u88c5\u9970\u5c42\u4e0d\u53d8\u3002396\u53ea\u6539\u9762\u677f\u7eb9\u6837\u3001\u4e2d\u592e\u7ea2\u94ae\u3001\u6574\u4ef6\u7f29\u7565\u56fe3\u7a97\uff0c\u540c\u6587\u6848\u91cd\u6392\u5b57\u5c42\uff1b\u539f\u4fa7\u8fb9\u3001\u63a5\u5934\u548c382\u5b9e\u62cd\u77ed\u9488\u7a97\u7684\u65e0\u635f\u6e90\u50cf\u7d20\u4e0d\u53d8\u3002

392/395\u4fdd\u7559\u4e0a\u4e00\u7248\uff0c\u4e0d\u89c6\u4f5c\u901a\u8fc7\uff1a382\u539f\u7167\u6709\u624b\u906e\u6321\u3001\u6574\u4ef6\u672a\u5165\u955c\uff0c\u65e0\u6cd5\u786e\u8ba4\u8be5\u5f20\u5b8c\u6574\u94f6\u8272SKU\uff1b\u7f3a\u5c11\u5b8c\u6574\u63d0\u62c9\u72b6\u6001\u3001\u5b9e\u9645\u884c\u7a0b\u548c\u5b8c\u6574\u4f38\u9488\u5bf9\u5e94\u3002\u4e0d\u80fd\u7528\u590d\u4f4d\u7eb9\u6837\u8986\u76d6\u77ed\u9488\uff0c\u4e5f\u4e0d\u80fd\u6309\u731c\u6d4b\u589e\u52a0\u7ea2\u70b9\u3002\u7ed3\u6784\u4e8b\u5b9e\u6587\u4ef6\u4ea6\u8bb0\u8fd9\u4e9b\u672a\u786e\u8ba4\u9879\u3002

\u4e24\u5957\u540413\u5f20\uff0c389\u5206\u522b\u4fdd\u7559Muse WEBP\u3001GPT PNG\uff0c\u539f\u5b57\u8282\u4e0e\u683c\u5f0f\u4e0d\u53d8\u3002\u65b0\u589e\u5019\u9009\u4ec5387/396/399\uff1b\u4e24\u5957\u5176\u4f5920\u4e2a\u6587\u4ef6\u5747\u4e0e\u524d\u5b8c\u6574\u5305SHA256\u76f8\u540c\u3002\u4e09\u56fe\u662f\u5185\u90e8\u5ba1\u9605\u5019\u9009\uff0c\u4e0d\u662f\u5ba2\u6237\u5b9a\u7a3f\uff0c\u4ecd\u6709\u8f85\u52a9\u6a21\u578b/\u5b9e\u62cd\u8d34\u9762\u5408\u6210\u611f\u3002

\u5b9e\u9645\u6253\u5f003\u5f20\u6574\u56fe\u3001\u624b\u673a\u5c3a\u5bf8\u9884\u89c8\u4e0e\u7ea2\u94ae/\u4fa7\u58c1\u653e\u5927\u88c1\u5207\u3002Blender\u91cd\u5f00\u9a8c\u8bc13\u4e2a\u5546\u54c1\u90e8\u4ef6\u7f51\u683c\u3001UV\u3001\u4e16\u754c\u53d8\u6362\u4e0e\u4e0a\u4e00\u6a21\u578b\u76f8\u540c\u3002300\xd7200\xd720mm\u4ec5\u4e3a\u8f85\u52a9\u58f3\u4f53\u5305\u7edc\uff0c\u6392\u9664\u7ea2\u94ae/\u63a5\u5934\uff0c\u4e0d\u662f\u7cbe\u5bc6\u5b9e\u7269\u6d4b\u91cf\u3002\u4fa7\u58c1\u9009\u533a\u7eaf\u767d\u5360\u6bd4\u4e0b\u964d\u4e3a0\u4ec5\u8bf4\u660e\u8be5\u533a\u8fc7\u66dd\u4fee\u590d\uff0c\u4e0d\u4ee3\u8868\u6574\u56fe\u7167\u7247\u7ea7\u901a\u8fc7\u3002

\u5165\u53e3\uff1apreview.html\uff08\u672a\u58f0\u79f0\u6d4f\u89c8\u5668\u9a8c\u6536\uff09\uff1b\u68c0\u67e5\uff1aquality-review.json\u3001verification.json\u3001native-reopen-verification.json\uff1b\u53ef\u7f16\u8f91\u6e90\uff1aeditable/*/layers.ora\u3001native/product.blend\u3002\u539f\u56fe\u3001\u65e7\u5019\u9009\u3001\u5931\u8d25\u5019\u9009\u5747\u4fdd\u7559\u3002
''')
sources=P/'sources';sources.mkdir(exist_ok=True)
rect=R/'production/2026-10-31_\u9876\u55b7\u5b54\u4f4d\u56de\u6e90\u53ef\u63a7\u4fee\u590d/372-front-rectified.jpg';shutil.copy2(rect,sources/'372-front-rectified.jpg')
sourcefiles=[rect,R/'products/\u957f\u65b9\u5f62\u62c9\u94ae\u9876\u55b7/\u7ed3\u6784\u4e8b\u5b9e\u4e0e\u5efa\u6a21\u72b6\u6001.md']+[next((R/'products/\u957f\u65b9\u5f62\u62c9\u94ae\u9876\u55b7/\u539f\u59cb\u5b9e\u62cd20261030').glob('*%d*'%n)) for n in [372,374,376,382]]
(P/'source-manifest.json').write_text(json.dumps([{'path':str(f),'sha256':sha(f)} for f in sourcefiles],ensure_ascii=False,indent=2))
S=P/'\u4e24\u5957\u5b8c\u6574\u5ba1\u9605\u56fe';S.mkdir(exist_ok=True);records=[]
for version in ['\u7248\u672c1_\u7b2c\u4e00\u5f20','\u7248\u672c2_\u7b2c\u4e8c\u5f20']:
 d=S/version;d.mkdir(exist_ok=True)
 files=sorted(f for f in (B/version).iterdir() if f.suffix.lower() in ['.jpg','.webp','.png']);assert len(files)==13
 for f in files:
  n=int(f.stem);src=P/'candidates'/f.name if n in [387,396,399] else f;t=d/f.name;shutil.copy2(src,t)
  with Image.open(t) as im:im.load();size=im.size;fmt=im.format
  same=sha(t)==sha(f)
  if n not in [387,396,399]:assert same
  records.append({'version':version,'name':f.name,'sha256':sha(t),'size':size,'format':fmt,'unchanged_baseline':same})
def archive(path,files,base):
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  for f in files:z.write(f,str(f.relative_to(base)))
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  for f in files:assert hashlib.sha256(z.read(str(f.relative_to(base)))).hexdigest()==sha(f)
 return {'path':path.name,'bytes':path.stat().st_size,'count':len(files),'sha256':sha(path),'crc_and_all_members_sha256':True}
receipts=[]
for d in sorted(S.iterdir()):receipts.append(archive(P/(d.name+'.zip'),sorted(d.iterdir()),S))
receipts.append(archive(P/'\u9876\u55b7\u5149\u8272\u4fee\u8ba2_\u4e24\u5957\u5b8c\u6574\u5ba1\u9605\u56fe.zip',sorted(S.rglob('*.*')),P))
(P/'verification.json').write_text(json.dumps({'image_records':records,'unchanged_file_count':sum(r['unchanged_baseline'] for r in records),'packages':receipts},ensure_ascii=False,indent=2))
cards=''.join('<article><h2>{}</h2><img src="candidates/{}.jpg"></article>'.format(n,n) for n in [387,399,396])
(P/'preview.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>\u9876\u55b7\u5149\u8272\u4fee\u8ba2\u5019\u9009</title><style>body{font:18px/1.7 system-ui;background:#181818;color:#eee;margin:24px}main{display:flex;gap:24px;flex-wrap:wrap}article{max-width:580px}img{width:100%}a{color:#e8c180}</style><h1>3\u5f20\u66f4\u65b0\uff0c2\u5f20\u4fdd\u7559\u5f85\u8865</h1><p>387/399\u4fee\u5149\u8272\u4e0e\u63a5\u89e6\uff1b396\u4fee3\u7a97\uff1b392/395\u672a\u89e3\u51b3\u3001\u672a\u66ff\u6362\u3002389\u4e24\u4efd\u539f\u6587\u4ef6\u4fdd\u7559\u3002</p><p><a href="\u9876\u55b7\u5149\u8272\u4fee\u8ba2_\u4e24\u5957\u5b8c\u6574\u5ba1\u9605\u56fe.zip">\u4e24\u5957\u5b8c\u657413\u56fe\u5305</a> \xb7 <a href="README.md">\u9650\u5236\u4e0e\u6838\u9a8c</a></p><main>'+cards+'</main>')
packfiles=[P/x for x in ['README.md','quality-review.json','verification.json','source-manifest.json','native-reopen-verification.json','highlight-check.json','lighting-changes.json','layer-pixel-verification.json','396-changes.json','transforms.json','native/product.blend','sources/372-front-rectified.jpg']]+sorted((P/'editable').rglob('*.ora'))
for name in ['lighting-refine.py','compose-refine.py','compose-396.py','verify-native.py','package-refine.py']:
 shutil.copy2(ROOT/name,P/name);packfiles.append(P/name)
sourcepack=archive(P/'\u5149\u8272\u4fee\u8ba2_\u53ef\u7f16\u8f91\u6e90\u4e0e\u8bb0\u5f55.zip',packfiles,P)
(P/'source-package-verification.json').write_text(json.dumps(sourcepack,ensure_ascii=False,indent=2))
print(json.dumps({'packages':receipts,'source_package':sourcepack,'396_unchanged_checks':unchanged_396},ensure_ascii=False))

from pathlib import Path
from PIL import Image
import json,hashlib,zipfile,shutil
P=Path(__file__).resolve().parent;R=P.parents[1]
B=R/'production/2026-11-03_\u9876\u55b7\u6574\u5957_\u7b2c\u4e09\u5f20\u4e24\u4e2a\u7248\u672c/\u9876\u55b7\u6574\u5957_\u7b2c\u4e09\u5f20\u4e24\u4e2a\u7248\u672c'
S=P/'\u4e24\u5957\u5b8c\u6574\u5ba1\u9605\u56fe';S.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for version in ['\u7248\u672c1_\u7b2c\u4e00\u5f20','\u7248\u672c2_\u7b2c\u4e8c\u5f20']:
 d=S/version;d.mkdir(exist_ok=True)
 files=sorted(f for f in (B/version).iterdir() if f.suffix.lower() in ['.jpg','.png','.webp'])
 assert len(files)==13
 for f in files:
  n=int(f.stem);src=P/'candidates'/f.name if n in [387,399] else f
  target=d/f.name;shutil.copy2(src,target)
  with Image.open(target) as im:im.load();size=im.size;fmt=im.format
  record={'version':version,'id':n,'name':f.name,'size':size,'format':fmt,'sha256':sha(target),'changed':n in [387,399],'unchanged_baseline':sha(target)==sha(f)}
  if n not in [387,399]:assert record['unchanged_baseline']
  records.append(record)
def archive(path,files,base):
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  for f in files:z.write(f,str(f.relative_to(base)))
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  for f in files:assert hashlib.sha256(z.read(str(f.relative_to(base)))).hexdigest()==sha(f)
 return {'path':path.name,'bytes':path.stat().st_size,'members':len(files),'sha256':sha(path),'crc_and_all_member_sha256':True}
zips=[]
for d in sorted(S.iterdir()):
 if d.is_dir():zips.append(archive(P/(d.name+'.zip'),sorted(d.iterdir()),S))
zips.append(archive(P/'\u9876\u55b7\u4fa7\u539a\u4f18\u5316_\u4e24\u5957\u5b8c\u6574\u5ba1\u9605\u56fe.zip',sorted(S.rglob('*.*')),P))
review={'status':'TWO_REVIEW_CANDIDATES_NOT_CUSTOMER_APPROVED','updated_ids':[387,399],'not_updated_ids':[392,395,396],'remaining_limitations':['Sidewall upper highlight remains bright, with some rendered appearance','Photo face retains original lighting and is darker than previous photo composite','392/395 flattened source has no independent product layer; pulling-pin composition cannot safely inherit static product','396 small cards require separate source reconstruction; unchanged','No matching oblique physical photograph; shell is auxiliary reconstruction'],'checks':['Opened both final JPEGs','Viewed390px preview of387','Viewed native knob and sidewall enlarged crops','Compared374 sidephoto and372 knobphoto','Background/decor/text layers pixel-identical'],'failed_v1':'Knob photo UV offset; excluded from review sets','dimensions':'Native housing300x200x20mm excluding knob/connector; shell mesh unchanged'}
(P/'quality-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2))
(P/'verification.json').write_text(json.dumps({'images':records,'packages':zips},ensure_ascii=False,indent=2))
sources=[]
for f in [R/'production/2026-10-31_\u9876\u55b7\u5b54\u4f4d\u56de\u6e90\u53ef\u63a7\u4fee\u590d/372-front-rectified.jpg',R/'production/2026-11-03_\u9876\u55b7389\u5206\u5c42\u539a\u5ea6\u4e0e\u6c34\u5e55/native/static-dry-v3.blend']:
 sources.append({'path':str(f),'sha256':sha(f)})
(P/'source-manifest.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2))
(P/'README.md').write_text('''# \u4fa7\u539a\u4f18\u5316\u5ba1\u9605\u5019\u9009

\u672c\u8f6e\u4ec5\u66f4\u65b0387\u3001399\uff1a\u6cbf\u539f\u59cb372\u7167\u7247\u9762\u677f\u4e0e\u7ea2\u94ae\u8868\u9762\u3001\u73b0\u6709300\xd7200\xd720mm\u8f85\u52a9\u58f3\u4f53\u91cd\u65b0\u6e32\u67d3\u3002\u58f3\u4f53\u7f51\u683c\u672a\u6539\uff0c\u8c03\u6574\u76f8\u673a\u4f7f\u8fde\u7eed\u4fa7\u58c1\u53ef\u89c1\u3002\u4e24\u5f20\u539f\u80cc\u666f\u3001\u6587\u5b57\u4e0e\u88c5\u9970\u5c42\u50cf\u7d20\u4e00\u81f4\uff1b\u4fdd\u7559\u65e7\u7248\u3002

\u4e24\u5957\u540413\u5f20\uff0c\u4ec5389\u4e0d\u540c\uff1a\u7248\u672c1\u4fdd\u7559Muse WEBP\uff0c\u7248\u672c2\u4fdd\u7559GPT PNG\u3002389\u53ca\u5176\u4f59\u672a\u4fee\u6539\u56fe\u7247\u4e0e\u4e0a\u4e00\u5b8c\u6574\u5305\u9010\u5b57\u8282\u4e00\u81f4\u3002\u4e24\u4e2a\u5355\u72ecZIP\u53ca\u5408\u5e76ZIP\u5747\u56de\u8bfbCRC\u3001\u5168\u90e8\u6210\u5458SHA256\u901a\u8fc7\u3002

\u8fd9\u662f\u5ba1\u9605\u5019\u9009\uff0c\u4e0d\u662f\u5ba2\u6237\u5b9a\u7a3f\u3002\u4e0a\u4fa7\u91d1\u5c5e\u9ad8\u5149\u504f\u4eae\uff0c\u4ecd\u6709\u6e32\u67d3\u611f\uff1b\u9762\u677f\u6cbf\u7528\u5b9e\u62cd\u5149\u7167\u4f46\u6574\u4f53\u8f83\u4e0a\u4e00\u7248\u6697\u3002\u6ca1\u6709\u540c\u673a\u4f4d\u5b9e\u62cd\uff0c\u8f85\u52a9\u58f3\u4f53\u4e0d\u80fd\u4ee3\u66ff\u7cbe\u5bc6\u5b9e\u7269\u6d4b\u91cf\u3002

392\u3001395\u7684\u73b0\u5b58\u753b\u9762\u6ca1\u6709\u72ec\u7acb\u5546\u54c1\u5c42\uff0c\u4e14\u6d89\u53ca\u77ed\u9488\u72b6\u6001\uff0c\u4e0d\u80fd\u76f4\u63a5\u5957\u9759\u6001\u5546\u54c1\uff1b396\u7684\u95ee\u9898\u5c0f\u7a97\u9700\u8981\u72ec\u7acb\u56de\u6e90\u91cd\u5efa\u3002\u672c\u8f6e\u4e09\u5f20\u4fdd\u7559\u539f\u5b57\u8282\uff0c\u5c1a\u672a\u89e3\u51b3\u3002\u672a\u56e0\u4e24\u4e2a\u9759\u6001\u6837\u56fe\u64c5\u81ea\u91cd\u7ed8\u8fd9\u4e9b\u753b\u9762\u3002

\u6838\u9a8c\uff1averification.json\uff1b\u89c6\u89c9\u8bb0\u5f55\uff1aquality-review.json\uff1b\u51e0\u4f55\u5c3a\u5bf8\uff1anative/geometry.json\uff1b\u5206\u5c42\u6e90\uff1aeditable/\uff1b\u6a21\u578b\uff1anative/product-v2.blend\u3002v1\u7ea2\u94ae\u6620\u5c04\u504f\u79fb\u5019\u9009\u672a\u8fdb\u5165\u4efb\u4f55\u5ba1\u9605\u5957\u56fe\u3002HTML\u4ec5\u4e3a\u672c\u5730\u9605\u8bfb\u5165\u53e3\uff0c\u672a\u58f0\u79f0\u6d4f\u89c8\u5668\u9a8c\u6536\u3002
''')
cards=''.join('<article><h2>{}</h2><img src="candidates/{}.jpg"></article>'.format(n,n) for n in [387,399])
(P/'preview.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>\u4fa7\u539a\u4f18\u5316\u6837\u56fe</title><style>body{background:#191919;color:#eee;font:18px/1.7 system-ui;margin:24px}main{display:flex;gap:24px;flex-wrap:wrap}article{max-width:600px}img{width:100%}a{color:#e2c181}</style><h1>387\u3001399\u4fa7\u539a\u4f18\u5316\u6837\u56fe</h1><p>\u4ec5\u4f9b\u5ba1\u9605\uff1b392\u3001395\u3001396\u5c1a\u672a\u4fee\u6539\u3002389\u4e24\u4e2a\u539f\u56fe\u5747\u4fdd\u7559\u3002</p><p><a href="\u9876\u55b7\u4fa7\u539a\u4f18\u5316_\u4e24\u5957\u5b8c\u6574\u5ba1\u9605\u56fe.zip">\u4e24\u5957\u5b8c\u657413\u56fe\u5305</a> \xb7 <a href="README.md">\u9650\u5236\u4e0e\u6838\u9a8c\u8bb0\u5f55</a></p><main>'+cards+'</main>')
sourcefiles=[P/'README.md',P/'quality-review.json',P/'verification.json',P/'source-manifest.json',P/'transforms.json',P/'native/geometry.json',P/'native/product-v2.blend',P/'render-v2.py',P/'compose.py',P/'package.py']+sorted((P/'editable').rglob('*.ora'))
receipt=archive(P/'\u4fa7\u539a\u4f18\u5316_\u53ef\u7f16\u8f91\u6e90\u4e0e\u8bb0\u5f55.zip',sourcefiles,P)
(P/'source-package-verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
print(json.dumps({'packages':zips,'source_package':receipt,'unchanged_count':sum(r['unchanged_baseline'] for r in records)},ensure_ascii=False))

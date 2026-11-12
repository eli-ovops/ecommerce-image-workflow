from pathlib import Path
from PIL import Image
import json,hashlib,zipfile,shutil
P=Path(__file__).resolve().parent;R=P.parents[1]
B=R/'production/2026-11-03_顶喷整套_第三张两个版本/顶喷整套_第三张两个版本'
S=P/'两套完整审阅图';S.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for version in ['版本1_第一张','版本2_第二张']:
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
zips.append(archive(P/'顶喷侧厚优化_两套完整审阅图.zip',sorted(S.rglob('*.*')),P))
review={'status':'TWO_REVIEW_CANDIDATES_NOT_CUSTOMER_APPROVED','updated_ids':[387,399],'not_updated_ids':[392,395,396],'remaining_limitations':['Sidewall upper highlight remains bright, with some rendered appearance','Photo face retains original lighting and is darker than previous photo composite','392/395 flattened source has no independent product layer; pulling-pin composition cannot safely inherit static product','396 small cards require separate source reconstruction; unchanged','No matching oblique physical photograph; shell is auxiliary reconstruction'],'checks':['Opened both final JPEGs','Viewed390px preview of387','Viewed native knob and sidewall enlarged crops','Compared374 sidephoto and372 knobphoto','Background/decor/text layers pixel-identical'],'failed_v1':'Knob photo UV offset; excluded from review sets','dimensions':'Native housing300x200x20mm excluding knob/connector; shell mesh unchanged'}
(P/'quality-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2))
(P/'verification.json').write_text(json.dumps({'images':records,'packages':zips},ensure_ascii=False,indent=2))
sources=[]
for f in [R/'production/2026-10-31_顶喷孔位回源可控修复/372-front-rectified.jpg',R/'production/2026-11-03_顶喷389分层厚度与水幕/native/static-dry-v3.blend']:
 sources.append({'path':str(f),'sha256':sha(f)})
(P/'source-manifest.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2))
(P/'README.md').write_text('''# 侧厚优化审阅候选

本轮仅更新387、399：沿原始372照片面板与红钮表面、现有300×200×20mm辅助壳体重新渲染。壳体网格未改，调整相机使连续侧壁可见。两张原背景、文字与装饰层像素一致；保留旧版。

两套各13张，仅389不同：版本1保留Muse WEBP，版本2保留GPT PNG。389及其余未修改图片与上一完整包逐字节一致。两个单独ZIP及合并ZIP均回读CRC、全部成员SHA256通过。

这是审阅候选，不是客户定稿。上侧金属高光偏亮，仍有渲染感；面板沿用实拍光照但整体较上一版暗。没有同机位实拍，辅助壳体不能代替精密实物测量。

392、395的现存画面没有独立商品层，且涉及短针状态，不能直接套静态商品；396的问题小窗需要独立回源重建。本轮三张保留原字节，尚未解决。未因两个静态样图擅自重绘这些画面。

核验：verification.json；视觉记录：quality-review.json；几何尺寸：native/geometry.json；分层源：editable/；模型：native/product-v2.blend。v1红钮映射偏移候选未进入任何审阅套图。HTML仅为本地阅读入口，未声称浏览器验收。
''')
cards=''.join('<article><h2>{}</h2><img src="candidates/{}.jpg"></article>'.format(n,n) for n in [387,399])
(P/'preview.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>侧厚优化样图</title><style>body{background:#191919;color:#eee;font:18px/1.7 system-ui;margin:24px}main{display:flex;gap:24px;flex-wrap:wrap}article{max-width:600px}img{width:100%}a{color:#e2c181}</style><h1>387、399侧厚优化样图</h1><p>仅供审阅；392、395、396尚未修改。389两个原图均保留。</p><p><a href="顶喷侧厚优化_两套完整审阅图.zip">两套完整13图包</a> · <a href="README.md">限制与核验记录</a></p><main>'+cards+'</main>')
sourcefiles=[P/'README.md',P/'quality-review.json',P/'verification.json',P/'source-manifest.json',P/'transforms.json',P/'native/geometry.json',P/'native/product-v2.blend',P/'render-v2.py',P/'compose.py',P/'package.py']+sorted((P/'editable').rglob('*.ora'))
receipt=archive(P/'侧厚优化_可编辑源与记录.zip',sourcefiles,P)
(P/'source-package-verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
print(json.dumps({'packages':zips,'source_package':receipt,'unchanged_count':sum(r['unchanged_baseline'] for r in records)},ensure_ascii=False))

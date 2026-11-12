from pathlib import Path
from PIL import Image,ImageOps,ImageChops
import json,hashlib,zipfile,shutil,xml.etree.ElementTree as ET,io
P=Path(__file__).resolve().parent;R=P.parents[1];OLD=R/'production/2026-11-03_\u9876\u55b713\u5f20_\u5c3a\u5bf8\u5355\u5217\u4e0e\u5356\u70b9\u4fee\u8ba2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
for n in range(387,400):
 p=P/'JPG'/('%d.jpg'%n);im=Image.open(p);im.load();same=sha(p)==sha(OLD/'JPG'/p.name)
 assert same==(n not in (387,399))
 checks.append(dict(id=n,size=im.size,sha256=sha(p),old_sha256=sha(OLD/'JPG'/p.name),unchanged=same))
ora=[]
for n in (387,399):
 d=P/'editable'/str(n)
 with zipfile.ZipFile(d/'layers.ora') as z:
  assert z.testzip() is None
  root=ET.fromstring(z.read('stack.xml'));merged=Image.new('RGBA',(int(root.get('w')),int(root.get('h'))))
  for node in reversed(list(root.find('stack'))):merged.alpha_composite(Image.open(io.BytesIO(z.read(node.get('src')))).convert('RGBA'))
  identical=merged.tobytes()==Image.open(d/'merged.png').convert('RGBA').tobytes();assert identical
 ora.append(dict(id=n,crc=True,recompose_pixel_equal=True,layers=5))
srcs=[]
for n in (372,376):
 orig=next((R/'products/\u957f\u65b9\u5f62\u62c9\u94ae\u9876\u55b7/\u539f\u59cb\u5b9e\u62cd20261030').glob('*_%d_2.jpg'%n));dest=P/'sources'/('%d-original.jpg'%n);shutil.copy2(orig,dest);srcs.append(dict(id=n,original_path=str(orig),copy=dest.relative_to(P).as_posix(),sha256=sha(orig)))
record=json.loads((P/'sources/original-cutout-provenance.json').read_text());im=ImageOps.exif_transpose(Image.open(P/'sources/372-original.jpg')).convert('RGB');cut=Image.open(P/'sources/product372.png').convert('RGB');match=im.crop(tuple(record['crop_bbox'])).tobytes()==cut.tobytes();assert match
(P/'verification.json').write_text(json.dumps(dict(images=checks,unchanged_count=11,ora=ora,source_photos=srcs,cutout_rgb_equals_original_crop=match,product_transform='rotation plus uniform scale only; no warp, no redraw, no relight',limitations=['No manufacturer-confirmed hole total; original knob occludes part of surface','Source photo resampled, not output-pixel identical','Real source angle exposes little side thickness; no invented side','387 background rebuilt;399 clean editable background reused; layout not pixel-identical to old advertisements']),ensure_ascii=False,indent=2))
rows=[]
for n in range(387,400):
 status='\u672c\u8f6e\u56de\u6e90\u4fee\u8ba2' if n in (387,399) else '\u539fJPG\u4fdd\u7559'
 rows.append('<figure><a href="JPG/{0}.jpg"><img src="JPG/{0}.jpg" loading="lazy"></a><figcaption>{0} \xb7 {1}</figcaption></figure>'.format(n,status))
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>\u9876\u55b713\u5f20\u5ba1\u9605</title><style>body{font:16px system-ui;background:#171717;color:#eee;max-width:1440px;margin:40px auto;padding:20px}a{color:#edca85}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:20px}figure{margin:0}img{width:100%;height:430px;object-fit:contain;background:#222}figcaption{padding:12px}p{line-height:1.7}</style><h1>\u9876\u55b713\u5f20 \xb7 \u4ec5387\u4e0e399\u56de\u6e90\u4fee\u8ba2</h1><p>\u5176\u4ed611\u5f20\u4e0e\u524d\u7248SHA\u4e00\u81f4\uff1b\u65b0\u8ba4\u53ef\u7684\u63d0\u62c9\u9664\u57a2\u56fe\u4fdd\u6301\u539f\u6837\u3002387/399\u4f7f\u7528\u5b8c\u6574372\u5b9e\u62cd\u5546\u54c1\uff0c\u4ec5\u65cb\u8f6c\u3001\u7b49\u6bd4\u7f29\u653e\uff1b\u80cc\u666f\u3001\u6587\u5b57\u3001\u9634\u5f71\u72ec\u7acb\u5206\u5c42\u3002\u672a\u91cd\u7ed8\u5b54\u7eb9\u3001\u7ea2\u94ae\u6216\u4fa7\u9762\u3002</p><p><a href="JPG-13-review.zip">13\u5f20JPG\u5305</a> \xb7 <a href="revision-source-records.zip">\u4e24\u5f20\u53ef\u7f16\u8f91\u6e90\u4e0e\u8bb0\u5f55</a> \xb7 <a href="review/387-old-left-new-right.jpg">387\u5de6\u65e7\u53f3\u65b0</a> \xb7 <a href="review/399-old-left-new-right.jpg">399\u5de6\u65e7\u53f3\u65b0</a></p><div class="grid">'''+''.join(rows)+'''</div><p>\u5b9e\u62cd\u89d2\u5ea6\u4e0b\u4fa7\u58c1\u539a\u5ea6\u8f83\u5f31\uff0c\u7ea2\u94ae\u906e\u6321\u533a\u57df\u672a\u91cd\u5efa\uff1b\u4e0d\u5ba3\u79f0\u5382\u5bb6\u786e\u8ba4\u5b54\u6570\u6216\u9010\u5b54\u7cbe\u5bc6\u6838\u51c6\u3002\u80cc\u666f\u3001\u706f\u5149\u4e0e\u5b57\u4f53\u4e3a\u91cd\u65b0\u6392\u7248\uff0c\u975e\u65e7\u56fe\u50cf\u7d20\u4e00\u81f4\u3002HTML\u4e3a\u672c\u5730\u7d22\u5f15\uff0c\u672a\u8fdb\u884c\u6d4f\u89c8\u5668\u9a8c\u6536\u3002</p></html>'''
(P/'preview.html').write_text(html)
(P/'README.md').write_text('''# \u4ec5387\u4e0e399\u56de\u6e90\u4fee\u8ba2

\u7528\u6237\u4e24\u5f20\u622a\u56fe\u5206\u522b\u5339\u914d399\u5546\u54c1\u5c40\u90e8\u548c387\u6574\u56fe\u3002\u5176\u4ed611\u5f20JPG\u539f\u5b57\u8282\u590d\u5236\uff0c\u89c1verification.json\u3002\u65b0\u589e\u201c\u8fd9\u4e2a\u4e0d\u9519\u201d\u7684\u6a2a\u5411\u624b\u62c9\u94ae\u9ed1\u91d1\u56fe\u4ec5\u8bb0\u5f55\u89c6\u89c9\u8ba4\u53ef\uff0c\u4e0d\u4fee\u6539\u6216\u63a8\u65ad\u9010\u5b54\u901a\u8fc7\u3002

\u672c\u8f6e\u4ece\u539f\u59cb372\u5b9e\u62cd\u4fdd\u7559\u5b8c\u6574\u5546\u54c1\uff0c376\u53ea\u4f5c\u7ed3\u6784\u4ea4\u53c9\u67e5\u770b\u3002\u590d\u7528\u7ecf\u6838\u5bf9\u7684\u539f\u59cb\u62a0\u56fe\uff0cRGB\u9010\u50cf\u7d20\u7b49\u4e8e372\u5bf9\u5e94\u539f\u7167\u88c1\u5207\uff1b\u6574\u4ef6\u53ea\u65cb\u8f6c\u3001\u7b49\u6bd4\u7f29\u653e\uff0c\u4e0d\u505a\u900f\u89c6\u53d8\u5f62\u3001\u91cd\u7ed8\u6216\u8865\u5b54\u3002387\u5c0f\u7a97\u4e3a\u540c\u4e00\u539f\u59cb372\u88c1\u5207\u3002\u539f\u59cb\u6e90\u548c\u53d8\u6362\u8bb0\u5f55\u5728sources\u53catransforms.json\u3002\u80cc\u666f\u4e0e\u6587\u5b57\u91cd\u65b0\u5efa\u7acb\u72ec\u7acb\u56fe\u5c42\uff1a387\u4e3a\u4e00\u6b21\u65b0\u751f\u6210\u5e72\u51c0\u80cc\u666f\uff0c399\u56e0\u4e00\u6b21\u8fde\u63a5\u5931\u8d25\uff0c\u590d\u7528\u65e2\u6709\u72ec\u7acb\u5e72\u51c0\u9ed1\u91d1\u80cc\u666f\u3002\u65e7AI\u6210\u54c1\u548c\u53cd\u9988\u622a\u56fe\u4ec5\u7528\u4e8e\u89c6\u89c9\u5bf9\u7167\uff0c\u672a\u9001\u5165\u751f\u56fe\uff0c\u672a\u4f5c\u50cf\u7d20\u5e95\u56fe\u3002

\u4e3b\u4f53\u771f\u5b9e\u5b54\u4e0e\u76f2\u70b9\u3001\u53f6\u74e3\u548c\u6d45\u7ea2\u94ae\u6765\u81ea\u7167\u7247\uff0c\u672a\u4eba\u4e3a\u6539\u6570\u91cf\u3002\u4f46\u4e0d\u5ba3\u79f0\u5382\u5bb6\u786e\u8ba4\u5b54\u6570\u6216\u9010\u5b54\u7cbe\u5bc6\u6838\u51c6\uff1a\u539f\u59cb\u94ae\u906e\u6321\u4ecd\u5728\uff0c\u63d2\u503c\u7f29\u653e\u6539\u53d8\u8f93\u51fa\u50cf\u7d20\uff1b\u6574\u4f53\u89c6\u89c9\u4ee5\u7528\u6237\u5ba1\u9605\u4e3a\u51c6\u3002\u4fdd\u7559\u9ed1\u91d1\u5e03\u5c40\u3001\u6807\u9898\u5356\u70b9\u53ca\u4e3b\u4f53\u65b9\u4f4d\uff0c\u4f46\u5e72\u51c0\u573a\u666f\u3001\u5b57\u5f62\u548c\u4e3b\u4f53\u89c6\u89d2\u4e0d\u662f\u65e7\u56fe\u50cf\u7d20\u4e00\u81f4\u3002\u5b9e\u62cd\u6b63\u9762\u4fa7\u58c1\u539a\u5ea6\u8f83\u5f31\uff0c\u672a\u8865\u753b\u4fa7\u9762\u3002

\u4e24\u5f20\u5206\u522b\u67095\u5c42ORA\uff0c\u5305\u542b\u5e72\u51c0\u80cc\u666f\u3001\u63a5\u89e6\u9634\u5f71\u3001\u5b8c\u6574\u5b9e\u62cd\u5546\u54c1\u3001\u88c5\u9970\u4e0e\u5b9e\u62cd\u5c0f\u7a97\u3001\u6587\u5b57\u3002ORA\u91cd\u7ec4\u50cf\u7d20\u4e00\u81f4\uff1b\u6587\u5b57\u5185\u5bb9\u548c\u5b57\u4f53\u5728compose.py\uff0c\u53ef\u4fee\u6539\u811a\u672c\u91cd\u5bfc\u51fa\uff0cORA\u6587\u5b57\u5c42\u4e3a\u6805\u683c\u3002compose.py\u4e3a\u5236\u4f5c\u8bb0\u5f55\uff0c\u4f9d\u8d56\u539f\u5de5\u4f5c\u533a\u7d20\u6750\uff1bORA\u53ca\u5bfc\u51fa\u56fe\u5c42\u53ef\u72ec\u7acb\u7f16\u8f91\u3002

review\u5185\u4e24\u5f20\u5de6\u65e7\u53f3\u65b0\u548c200%\u7ec6\u8282\u3002JPG-13-review.zip\u4e3a\u65b0\u5ba1\u9605\u603b\u5305\uff1b\u65e7\u7248\u4fdd\u7559\uff0c\u65e0\u5916\u53d1\u3002\u5c3a\u5bf8\u4ec5397\uff0c\u9664\u57a2\u4e3b\u6587\u6848\u4ec5392/395\uff1b\u5176\u4f5911\u5f20\u672a\u91cd\u65b0\u751f\u6210\u3002HTML\u672a\u6d4f\u89c8\u5668\u9a8c\u6536\u3002\u5b9e\u9645\u6a21\u578b\u5b57\u6bb5UNKNOWN\u3002
''')
packages=[]
for name,files in [('JPG-13-review.zip',sorted((P/'JPG').glob('*.jpg'))),('revision-source-records.zip',sorted(p for p in P.rglob('*') if p.is_file() and p.suffix!='.zip' and 'JPG' not in p.parts and p.name!='package-verification.json'))]:
 with zipfile.ZipFile(P/name,'w',zipfile.ZIP_DEFLATED) as z:
  for f in files:z.write(f,f.relative_to(P).as_posix())
 with zipfile.ZipFile(P/name) as z:
  assert z.testzip() is None
  assert all(hashlib.sha256(z.read(f.relative_to(P).as_posix())).hexdigest()==sha(f) for f in files)
 packages.append(dict(file=name,entries=len(files),bytes=(P/name).stat().st_size,sha256=sha(P/name),crc=True,all_member_sha=True))
(P/'package-verification.json').write_text(json.dumps(packages,indent=2));print(json.dumps(dict(unchanged=11,cutout_original_pixel_match=match,packages=packages),indent=2))

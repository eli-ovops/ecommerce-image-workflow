from pathlib import Path
from PIL import Image,ImageOps,ImageChops
import json,hashlib,zipfile,shutil,xml.etree.ElementTree as ET,io
P=Path(__file__).resolve().parent;R=P.parents[1];OLD=R/'production/2026-11-03_顶喷13张_尺寸单列与卖点修订'
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
 orig=next((R/'products/长方形拉钮顶喷/原始实拍20261030').glob('*_%d_2.jpg'%n));dest=P/'sources'/('%d-original.jpg'%n);shutil.copy2(orig,dest);srcs.append(dict(id=n,original_path=str(orig),copy=dest.relative_to(P).as_posix(),sha256=sha(orig)))
record=json.loads((P/'sources/original-cutout-provenance.json').read_text());im=ImageOps.exif_transpose(Image.open(P/'sources/372-original.jpg')).convert('RGB');cut=Image.open(P/'sources/product372.png').convert('RGB');match=im.crop(tuple(record['crop_bbox'])).tobytes()==cut.tobytes();assert match
(P/'verification.json').write_text(json.dumps(dict(images=checks,unchanged_count=11,ora=ora,source_photos=srcs,cutout_rgb_equals_original_crop=match,product_transform='rotation plus uniform scale only; no warp, no redraw, no relight',limitations=['No manufacturer-confirmed hole total; original knob occludes part of surface','Source photo resampled, not output-pixel identical','Real source angle exposes little side thickness; no invented side','387 background rebuilt;399 clean editable background reused; layout not pixel-identical to old advertisements']),ensure_ascii=False,indent=2))
rows=[]
for n in range(387,400):
 status='本轮回源修订' if n in (387,399) else '原JPG保留'
 rows.append('<figure><a href="JPG/{0}.jpg"><img src="JPG/{0}.jpg" loading="lazy"></a><figcaption>{0} · {1}</figcaption></figure>'.format(n,status))
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>顶喷13张审阅</title><style>body{font:16px system-ui;background:#171717;color:#eee;max-width:1440px;margin:40px auto;padding:20px}a{color:#edca85}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:20px}figure{margin:0}img{width:100%;height:430px;object-fit:contain;background:#222}figcaption{padding:12px}p{line-height:1.7}</style><h1>顶喷13张 · 仅387与399回源修订</h1><p>其他11张与前版SHA一致；新认可的提拉除垢图保持原样。387/399使用完整372实拍商品，仅旋转、等比缩放；背景、文字、阴影独立分层。未重绘孔纹、红钮或侧面。</p><p><a href="JPG-13-review.zip">13张JPG包</a> · <a href="revision-source-records.zip">两张可编辑源与记录</a> · <a href="review/387-old-left-new-right.jpg">387左旧右新</a> · <a href="review/399-old-left-new-right.jpg">399左旧右新</a></p><div class="grid">'''+''.join(rows)+'''</div><p>实拍角度下侧壁厚度较弱，红钮遮挡区域未重建；不宣称厂家确认孔数或逐孔精密核准。背景、灯光与字体为重新排版，非旧图像素一致。HTML为本地索引，未进行浏览器验收。</p></html>'''
(P/'preview.html').write_text(html)
(P/'README.md').write_text('''# 仅387与399回源修订

用户两张截图分别匹配399商品局部和387整图。其他11张JPG原字节复制，见verification.json。新增“这个不错”的横向手拉钮黑金图仅记录视觉认可，不修改或推断逐孔通过。

本轮从原始372实拍保留完整商品，376只作结构交叉查看。复用经核对的原始抠图，RGB逐像素等于372对应原照裁切；整件只旋转、等比缩放，不做透视变形、重绘或补孔。387小窗为同一原始372裁切。原始源和变换记录在sources及transforms.json。背景与文字重新建立独立图层：387为一次新生成干净背景，399因一次连接失败，复用既有独立干净黑金背景。旧AI成品和反馈截图仅用于视觉对照，未送入生图，未作像素底图。

主体真实孔与盲点、叶瓣和浅红钮来自照片，未人为改数量。但不宣称厂家确认孔数或逐孔精密核准：原始钮遮挡仍在，插值缩放改变输出像素；整体视觉以用户审阅为准。保留黑金布局、标题卖点及主体方位，但干净场景、字形和主体视角不是旧图像素一致。实拍正面侧壁厚度较弱，未补画侧面。

两张分别有5层ORA，包含干净背景、接触阴影、完整实拍商品、装饰与实拍小窗、文字。ORA重组像素一致；文字内容和字体在compose.py，可修改脚本重导出，ORA文字层为栅格。compose.py为制作记录，依赖原工作区素材；ORA及导出图层可独立编辑。

review内两张左旧右新和200%细节。JPG-13-review.zip为新审阅总包；旧版保留，无外发。尺寸仅397，除垢主文案仅392/395；其余11张未重新生成。HTML未浏览器验收。实际模型字段UNKNOWN。
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

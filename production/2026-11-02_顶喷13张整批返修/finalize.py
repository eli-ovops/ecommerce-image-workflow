from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageChops
import json, hashlib, zipfile, io, html, xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2))
notes={
387:('静态候选待审','黑金立式、白色展台、左侧短针实拍窗、底部规格带','展台偏平，银壳和红钮仍有CG感。'),
388:('原版保持，待审','沿用已交付粗斜白字红描边、安装水流与左下主体','本轮字节不变；水流仅示意，未获客户验收。'),
389:('待返工','蓝色浴室、上方安装主体、下方静态主体、右侧黑色粗斜字','黑字重影已消除；机位重复，细线水流和金属质感不达参考。'),
390:('待返工','青色浴室、上方安装主体、下方小主体和金色标题','机位重复，水流及金属质感不足，光色尚未贴近参考。'),
391:('待返工','蓝色星空顶、暖墙、原创短发成年模特、上方安装主体','水流没有自然接触人物或溅水，主体视角和质感不足。'),
392:('部分完成，待返工','黑金斜置大主体、右下真实短针圆窗、粗斜金字','整件仍是复位静态；未完成拉出状态，未用虚假长针或剖面替代。'),
393:('内容替换，待返工','保留金色层级和安装出水画面，换成可见外观细节','AIR和内部爆炸结构未经证实，未复刻；机位和水流重复。'),
394:('待返工','竖版蓝顶暖墙、原创模特、安装主体','人物与水流接触不真实，机位重复；未达到参考摄影质感。'),
395:('部分完成，待返工','竖版黑金斜置主体与真实短针圆窗','整件拉出状态未完成；真实局部只能证明短针可见。'),
396:('细节候选待审','六处真实细节，2×3卡片及粗金标题','细节照片清晰度、反射和侧边表现受原片限制。'),
397:('内容替换，待返工','竖版安装画面和外观细节，保留金色标题层级','未做未经证实的AIR或内部剖面；机位、水流重复且质感不足。'),
398:('内容替换，待返工','暖浴室安装示意与两张真实接头细节','360度和身体覆盖效果无依据，未展示；水流和机位仍需重做。'),
399:('静态候选待审','黑金石材、暖雾、斜置主体、大号粗斜金字','已更换照片剪贴主体，仍可见三维银壳和红钮质感，未达摄影级。')}
old=json.loads((P/'manifest.json').read_text()); byid={r['id']:r for r in old}
records=[]; checks=[]
for n in range(387,400):
 f=P/'JPG'/f'{n}.jpg'; im=Image.open(f); im.load(); expected=(1200,1200) if n<=393 else (900,1600); assert im.size==expected
 status,style,gap=notes[n]; r=byid.get(n,{'id':n,'size':list(im.size)})
 r.update(note=gap,status=status,reference=n,retained_visual_features=style,customer_acceptance='UNKNOWN',file=f'JPG/{n}.jpg',sha256=sha(f)); records.append(r)
 d=P/'editable'/str(n); ora=d/('388-editable.ora' if n==388 else 'layers.ora')
 with zipfile.ZipFile(ora) as z:
  assert z.testzip() is None
  root=ET.fromstring(z.read('stack.xml')); canvas=Image.new('RGBA',(int(root.attrib['w']),int(root.attrib['h'])))
  for layer in reversed(list(root.find('stack'))):
   assert layer.attrib.get('opacity','1')=='1'
   li=Image.open(io.BytesIO(z.read(layer.attrib['src']))).convert('RGBA'); canvas.alpha_composite(li,(int(layer.attrib.get('x',0)),int(layer.attrib.get('y',0))))
  merged=Image.open(io.BytesIO(z.read('mergedimage.png'))).convert('RGBA'); assert ImageChops.difference(canvas,merged).getbbox() is None
 if n!=388:
  layout=json.loads((d/'layout.json').read_text()); layout['note']=gap; write(d/'layout.json',layout)
  w,h=im.size
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#fff1cc"/><stop offset="1" stop-color="#c38746"/></linearGradient></defs><image href="base.png" width="{w}" height="{h}"/>'
  for t in layout['text']:
   x,y,s=t['x'],t['y'],t['size']; fill='url(#gold)' if t.get('gold_gradient') else t['color']; skew=f'translate({x} {y}) skewX(-6.3)' if t.get('oblique') else f'translate({x} {y})'
   svg+=f'<g transform="{skew}"><text x="0" y="{s*.85}" font-family="Heiti SC" font-weight="900" font-size="{s}" fill="{fill}" stroke="{fill}" stroke-width="1">{html.escape(t["text"])}</text></g>'
  (d/'editable.svg').write_text(svg+'</svg>')
 svgfile=d/('editable-text.svg' if n==388 else 'editable.svg'); ET.parse(svgfile)
 checks.append(dict(id=n,size=list(im.size),sha256=sha(f),ora_crc=True,ora_recomposed_equal=True,svg_xml_valid=True))
original388=ROOT/'production/2026-11-02_388局部返修_粗斜字体与融合/388_粗斜字体与融合_审阅.jpg'
assert sha(original388)==sha(P/'JPG/388.jpg')
prev=ROOT/'production/2026-11-02_顶喷13张逐图新画面'; previous=json.loads((prev/'verification.json').read_text())['checks']
assert all(sha(prev/'JPG'/f'{r["id"]}.jpg')==r['sha256'] for r in previous)
write(P/'manifest.json',records)
write(P/'verification.json',dict(stage='REVIEW_CANDIDATES_NOT_ACCEPTED',checks=checks,preserved_388_byte_identical=True,previous_13_unchanged=True,svg_visual_metrics='Not rendered; live text approximation. ORA layers are exact.',html_browser_test='NOT_RUN',native_geometry_claim='Water-refinement production record only; no independent mesh rerun this batch.'))
rows=['|编号|状态|参考对应与本轮处理|仍缺内容|','|---|---|---|---|']
for r in records: rows.append(f'|{r["id"]}|{r["status"]}|{r["retained_visual_features"]}|{r["note"]}|')
(P/'13张对应与状态.md').write_text('# 13张逐项审阅状态\n\n12张返修，388字节不变。全部为审阅候选；没有取得整套图面通过或客户验收。\n\n'+'\n'.join(rows)+'\n')
(P/'README.md').write_text('# 顶喷13张整批返修\n\n12张完成本轮局部修改，388保留原版。文件齐全不等于制作目标完成：安装类重复同机位，水流与人物互动不足；392/395整件拉出未完成；393/397的AIR内部结构及398的360/覆盖性能没有证据，已替换内容。见13张对应与状态.md。\n\nJPG：7张1200×1200、6张900×1600。review内左参考右候选对照。preview.html为本地索引，未做浏览器验收。\n\neditable内ORA为逐层原生合成，可重组且合成结果已核对；SVG为可编辑文字与底图，字体/渐变/斜体保留，但不同软件字形度量和阴影可能与JPG不同，未进行SVG视觉验收。388源文件原样复制。native内为完整安装场景Blender文件；静态主体源在editable/388。build.py需原项目实拍与目录，非独立一键工程；ORA/SVG和Blender源可独立打开。\n\n商品面板来自372原始实拍，银壳/红钮/管件为三维辅助；背景沿用已生成并获准复用的场景，未调用新的图像生成。94条水线和658水滴仅为安装出水示意，非实测孔数、真实水型、流体仿真或性能证据。\n\n旧文件与原件均保留，无外发。\n')
page='<html lang="zh-CN"><meta charset="utf-8"><title>13张返修审阅</title><style>body{background:#161718;color:#eee;font:18px sans-serif;max-width:1200px;margin:auto;padding:24px}img{max-width:100%}section{border-top:1px solid #666;padding:24px 0}a{color:#edc48a}</style><h1>13张返修审阅</h1><p>12张返修；388保持不变。以下均非已验收成品，逐项缺口见各图。</p><p><a href="13张对应与状态.md">逐项状态</a> · <a href="JPG-13-review.zip">13张JPG</a> · <a href="editable-source.zip">可编辑源包</a></p>'
for r in records:
 n=r['id']; comp=f'review/{n}-comparison.jpg' if (P/f'review/{n}-comparison.jpg').exists() else 'editable/388/388_左参考右返修.jpg'
 page+=f'<section><h2>{n}｜{r["status"]}</h2><p>{r["retained_visual_features"]}</p><p>{r["note"]}</p><a href="JPG/{n}.jpg">打开JPG</a><p><img loading="lazy" src="{comp}" alt="左参考右候选{n}"></p></section>'
(P/'preview.html').write_text(page+'</html>')
contact=Image.new('RGB',(1400,4*450),'#ddd'); draw=ImageDraw.Draw(contact)
for i,n in enumerate(range(387,400)):
 im=ImageOps.contain(Image.open(P/f'JPG/{n}.jpg'),(340,410)); x=(i%4)*350+(350-im.width)//2; y=(i//4)*450+30; contact.paste(im,(x,y));draw.text(((i%4)*350+12,(i//4)*450+10),str(n),fill='black')
contact.save(P/'review/contact-final.jpg',quality=95)
def pack(name,files):
 with zipfile.ZipFile(P/name,'w',zipfile.ZIP_DEFLATED) as z:
  for f in files:z.write(f,f.relative_to(P))
 with zipfile.ZipFile(P/name) as z:
  assert z.testzip() is None
  assert all(hashlib.sha256(z.read(i)).hexdigest()==sha(P/i.filename) for i in z.infolist())
 return dict(file=name,members=len(files),bytes=(P/name).stat().st_size,sha256=sha(P/name),crc=True,member_sha_equal=True)
a=pack('JPG-13-review.zip',sorted((P/'JPG').glob('*.jpg')))
files=[]
for folder in ['editable','assets','native']:
 for f in (P/folder).rglob('*'):
  if f.is_file() and f.suffix not in ['.zip','.blend1','.log'] and 'revision-v1' not in f.name:files.append(f)
files += [P/n for n in ['build.py','finalize.py','README.md','manifest.json','verification.json','13张对应与状态.md']]
b=pack('editable-source.zip',sorted(files))
write(P/'archives-verification.json',[a,b]);print(json.dumps(dict(images=len(checks),preserved388=True,previous13unchanged=True,archives=[a,b]),ensure_ascii=False,indent=2))

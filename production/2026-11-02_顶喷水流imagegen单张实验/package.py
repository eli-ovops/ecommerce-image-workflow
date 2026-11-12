from pathlib import Path
from PIL import Image,ImageOps,ImageChops
import json,zipfile,hashlib,shutil,io,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent;R=P.parents[1];B=P.parent/'2026-11-02_顶喷13张整批返修'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
S=P/'sources';S.mkdir(exist_ok=True)
sources=[(R/'products/长方形拉钮顶喷/原始实拍20261030/微信图片_20261030154107_372_2.jpg','372-original.jpg'),(R/'references/2026-10-31_同款商户电商参考/微信图片_20261031133902_393_2.jpg','393-reference.jpg'),(B/'assets/warm-bath.png','approved-scene.png'),(P.parent/'2026-11-02_391安装仰视单张实验/single-photo-face.png','single-photo-face.png')]
records=[]
for src,name in sources:
 shutil.copy2(src,S/name);records.append(dict(source=str(src),saved=f'sources/{name}',sha256=sha(src)))
(P/'sources.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
layers=[('Approved original scene layer',ImageOps.fit(Image.open(S/'approved-scene.png').convert('RGBA'),(1200,1200)))]
for name,f in [('Native dry product','dry-product.png'),('Generated water with origin mask','water-masked.png')]:
 im=Image.new('RGBA',(1200,1200));im.alpha_composite(Image.open(P/f).convert('RGBA').resize((1740,1740),Image.Resampling.LANCZOS),(-250,0));layers.append((name,im))
root=ET.Element('image',w='1200',h='1200');stack=ET.SubElement(root,'stack');out=Image.new('RGBA',(1200,1200))
for _,im in layers:out.alpha_composite(im)
out.save(P/'water-study.png');out.convert('RGB').save(P/'water-study.jpg',quality=97,subsampling=0)
with zipfile.ZipFile(P/'water-study-editable.ora','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('mimetype','image/openraster',compress_type=zipfile.ZIP_STORED)
 for i,(name,im) in enumerate(reversed(layers)):
  f=f'data/{i}.png';buf=io.BytesIO();im.save(buf,format='PNG');z.writestr(f,buf.getvalue());ET.SubElement(stack,'layer',name=name,src=f,x='0',y='0',opacity='1',visibility='visible',**{'composite-op':'svg:src-over'})
 z.writestr('stack.xml',ET.tostring(root));buf=io.BytesIO();out.save(buf,format='PNG');z.writestr('mergedimage.png',buf.getvalue())
for f in P.glob('*.ora'):
 with zipfile.ZipFile(f) as z:
  assert z.testzip() is None;root=ET.fromstring(z.read('stack.xml'));out=Image.new('RGBA',(1200,1200))
  for e in reversed(list(root.find('stack'))):out.alpha_composite(Image.open(io.BytesIO(z.read(e.attrib['src']))).convert('RGBA'))
  expected=Image.open(io.BytesIO(z.read('mergedimage.png'))).convert('RGBA');assert ImageChops.difference(out,expected).getbbox() is None
v=json.loads((P/'verification.json').read_text());v.update(ora_crc_and_recomposition=True,visual_review='Full JPG and 200pct origins/droplets reviewed. Breakup improved; source registration imperfect and intermittent connections remain. NOT_ACCEPTED_PHOTOREALISM',model_runtime='UNKNOWN',imagegen_calls=1,old_batch_changed=False)
(P/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2))
(P/'README.md').write_text('''# 单张水流 imagegen 实验（待审，真实感未通过）

本轮只尝试独立水层及单图合成，未改13张原包。主看 water-study.jpg；393-water-experiment.jpg 为回填原393布局的版本。water-study-before-after.jpg 左旧曲线、右生成水层；study-origins / study-droplets 的200pct文件是局部对照。

实际方法：原391 Blender场景隐藏水曲线，重新渲染干燥产品与管件；喷面继续使用原372实拍纹理。94个候选起点从原生场景投影，排除项沿用原记录，不是实测总孔数。将原生起点引导图和原393参考送入内置 imagegen，仅生成透明水幕（一次调用），未把任何上轮AI成品送回模型。prompt.txt为完整提示词。imagegen原生输出1254×1254 RGBA；water-generated-original.png完整保留。

原水素材偏密并有灰雾/暖色杂点，原生合成时统一去饱和、抑制灰雾、降低透明度，并按候选孔下方窄通道遮罩，得到water-masked.png。没有以新画直线替代生成水形。背景为此前获准复用的原始场景层，仅在本地合成，未再送模型。

产品保护范围：原生1200像素层上，99,153个不透明产品像素位于水通道外且逐像素不变。水通道内允许透明水层遮挡产品；因此不声称整件像素完全不变。模型银壳/红钮本来就是三维，非整件实拍像素。遮罩约束起点附近范围，不等于生成水流逐孔对齐；没有逐孔验证通过。

实际审图：下半段出现自然程度较高的断续水珠，较旧直线水幕明显丰富；但起点与水束仍有断接、部分水束偏粗和贴图感，喷面/金属仍有CG感。真实水型、流量、增压或AIR功能均未验证。当前结果只能作为方法实验，不是可直接交付客户的广告成品。

可编辑：water-study-editable.ora为背景/干产品/水三层；393-water-editable.ora为原布局全部层。dry-product.blend为可打开的本轮原生干模型，贴图已内嵌。water-origin-gate.png、product-protected-mask.png、projected-origins.json为遮罩和起点证据。prepare.py重渲染依赖项目原391源；compose.py依赖原393分层，独立打开ORA不依赖脚本。sources内有实际输入副本与哈希清单。未删除文件，全部为继续审阅所需。
''')
(P/'preview.html').write_text('<meta charset="utf-8"><title>水流单张实验</title><style>body{background:#222;color:white;max-width:1200px;margin:auto;font:18px sans-serif}img{max-width:100%}a{color:#efd0a3}</style><h1>水流单张实验：未通过真实感验收</h1><p>下方水珠有所改善；孔位起点与水束仍有断接，未逐孔验证。</p><img src="water-study.jpg"><h2>左旧曲线，右生成水层</h2><img src="water-study-before-after.jpg"><h2>起点200%</h2><img src="study-origins-200pct-before-after.jpg"><h2>水珠200%</h2><img src="study-droplets-200pct-before-after.jpg"><p><a href="README.md">方法与限制</a> · <a href="water-experiment-source.zip">源包</a></p>')
files=[f for f in P.rglob('*') if f.is_file() and f.suffix not in ['.zip','.blend1'] and f.name!='archive-verification.json']
with zipfile.ZipFile(P/'water-experiment-source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,f.relative_to(P))
with zipfile.ZipFile(P/'water-experiment-source.zip') as z:
 assert z.testzip() is None;assert all(hashlib.sha256(z.read(i)).hexdigest()==sha(P/i.filename) for i in z.infolist())
result=dict(members=len(files),bytes=(P/'water-experiment-source.zip').stat().st_size,sha256=sha(P/'water-experiment-source.zip'),crc=True,member_sha_equal=True)
(P/'archive-verification.json').write_text(json.dumps(result,indent=2));print(result)

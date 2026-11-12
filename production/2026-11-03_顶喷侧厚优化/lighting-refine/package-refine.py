from pathlib import Path
from PIL import Image,ImageChops
import hashlib,json,shutil,zipfile,io,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent;P=ROOT/'lighting-refine';R=ROOT.parents[1]
B=R/'production/2026-11-03_顶喷整套_第三张两个版本/顶喷整套_第三张两个版本'
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
  b=Image.open(R/'production/2026-11-03_顶喷两张细节回源修订/editable'/str(n)/('layer%d.png'%i)).convert('RGBA')
  layerchecks['%d-layer%d'%(n,i)]=a.size==b.size and a.tobytes()==b.tobytes()
assert all(layerchecks.values())
(P/'layer-pixel-verification.json').write_text(json.dumps(layerchecks,indent=2))
review={'status':'THREE_IMPROVED_REVIEW_CANDIDATES_TWO_UNRESOLVED','updated':[387,396,399],'preserved_unresolved':[392,395],'visual_review':{'387':'Continuous sidewall with reduced blown highlights; orange-red shallow knob; closer contact shadow; some composite appearance remains','399':'Continuous gray/silver sidewall; orange-red knob; tighter shadow; original photographic face lighting remains baked','396':'Three corrected windows use original372 photo and current native shell; no added red pins; true382 short-pin detail unchanged'},'392_395_reason':{'source_382':'Hand obscures knob/upper panel; frame does not contain complete unobstructed silver product; outer SKU cannot be confirmed from this shot','missing':'Confirmed pull stroke, complete raised-pin state and unobstructed whole silver product in pulled state','decision':'Keep previous image unchanged; do not replace with reset texture or invent red pin positions; unchanged does not mean accepted'},'396_preserved_pixel_checks':unchanged_396,'native_geometry_verified':'native-reopen-verification.json','limited_highlight_measure':'highlight-check.json; selected sidewall ROI only, not full material realism score','customer_acceptance':'UNKNOWN','actual_runtime_model':'UNKNOWN','failed_candidate':'review/396-rejected-patch-v1.jpg has rectangular seams and is excluded'}
(P/'quality-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2))
(P/'README.md').write_text('''# 顶喷侧厚与光色修订：3张更新、2张保留待补

最新候选387、396、399。相较上一轮：387/399降低侧壁高光、恢复实拍橙红钮色，收紧接触阴影；背景、文字、装饰层不变。396只改面板纹样、中央红钮、整件缩略图3窗，同文案重排字层；原侧边、接头和382实拍短针窗的无损源像素不变。

392/395保留上一版，不视作通过：382原照有手遮挡、整件未入镜，无法确认该张完整银色SKU；缺少完整提拉状态、实际行程和完整伸针对应。不能用复位纹样覆盖短针，也不能按猜测增加红点。结构事实文件亦记这些未确认项。

两套各13张，389分别保留Muse WEBP、GPT PNG，原字节与格式不变。新增候选仅387/396/399；两套其余20个文件均与前完整包SHA256相同。三图是内部审阅候选，不是客户定稿，仍有辅助模型/实拍贴面合成感。

实际打开3张整图、手机尺寸预览与红钮/侧壁放大裁切。Blender重开验证3个商品部件网格、UV、世界变换与上一模型相同。300×200×20mm仅为辅助壳体包络，排除红钮/接头，不是精密实物测量。侧壁选区纯白占比下降为0仅说明该区过曝修复，不代表整图照片级通过。

入口：preview.html（未声称浏览器验收）；检查：quality-review.json、verification.json、native-reopen-verification.json；可编辑源：editable/*/layers.ora、native/product.blend。原图、旧候选、失败候选均保留。
''')
sources=P/'sources';sources.mkdir(exist_ok=True)
rect=R/'production/2026-10-31_顶喷孔位回源可控修复/372-front-rectified.jpg';shutil.copy2(rect,sources/'372-front-rectified.jpg')
sourcefiles=[rect,R/'products/长方形拉钮顶喷/结构事实与建模状态.md']+[next((R/'products/长方形拉钮顶喷/原始实拍20261030').glob('*%d*'%n)) for n in [372,374,376,382]]
(P/'source-manifest.json').write_text(json.dumps([{'path':str(f),'sha256':sha(f)} for f in sourcefiles],ensure_ascii=False,indent=2))
S=P/'两套完整审阅图';S.mkdir(exist_ok=True);records=[]
for version in ['版本1_第一张','版本2_第二张']:
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
receipts.append(archive(P/'顶喷光色修订_两套完整审阅图.zip',sorted(S.rglob('*.*')),P))
(P/'verification.json').write_text(json.dumps({'image_records':records,'unchanged_file_count':sum(r['unchanged_baseline'] for r in records),'packages':receipts},ensure_ascii=False,indent=2))
cards=''.join('<article><h2>{}</h2><img src="candidates/{}.jpg"></article>'.format(n,n) for n in [387,399,396])
(P/'preview.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>顶喷光色修订候选</title><style>body{font:18px/1.7 system-ui;background:#181818;color:#eee;margin:24px}main{display:flex;gap:24px;flex-wrap:wrap}article{max-width:580px}img{width:100%}a{color:#e8c180}</style><h1>3张更新，2张保留待补</h1><p>387/399修光色与接触；396修3窗；392/395未解决、未替换。389两份原文件保留。</p><p><a href="顶喷光色修订_两套完整审阅图.zip">两套完整13图包</a> · <a href="README.md">限制与核验</a></p><main>'+cards+'</main>')
packfiles=[P/x for x in ['README.md','quality-review.json','verification.json','source-manifest.json','native-reopen-verification.json','highlight-check.json','lighting-changes.json','layer-pixel-verification.json','396-changes.json','transforms.json','native/product.blend','sources/372-front-rectified.jpg']]+sorted((P/'editable').rglob('*.ora'))
for name in ['lighting-refine.py','compose-refine.py','compose-396.py','verify-native.py','package-refine.py']:
 shutil.copy2(ROOT/name,P/name);packfiles.append(P/name)
sourcepack=archive(P/'光色修订_可编辑源与记录.zip',packfiles,P)
(P/'source-package-verification.json').write_text(json.dumps(sourcepack,ensure_ascii=False,indent=2))
print(json.dumps({'packages':receipts,'source_package':sourcepack,'396_unchanged_checks':unchanged_396},ensure_ascii=False))

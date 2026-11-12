from pathlib import Path
from PIL import Image,ImageOps
import hashlib,json,zipfile,shutil,io,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent;R=ROOT.parents[1];P=ROOT/'completed-five'
B=R/'production/2026-11-03_顶喷整套_第三张两个版本/顶喷整套_第三张两个版本'
LATEST=ROOT/'lighting-refine'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
T=P/'顶喷修订整套';T.mkdir(exist_ok=True);E=T/'核验与对照';E.mkdir(exist_ok=True)
updated=[387,392,395,396,399];records=[]
for version in ['版本1_第一张','版本2_第二张']:
 d=T/version;d.mkdir(exist_ok=True)
 files=sorted(f for f in (B/version).iterdir() if f.suffix.lower() in ['.jpg','.png','.webp']);assert len(files)==13
 for f in files:
  n=int(f.stem);src=P/'JPG'/f.name if n in updated else f;t=d/f.name;shutil.copy2(src,t)
  with Image.open(t) as im:im.load();size=im.size;fmt=im.format
  same=sha(t)==sha(f)
  if n not in updated:assert same
  if n in [387,396,399]:assert sha(t)==sha(LATEST/'candidates'/f.name)
  records.append({'version':version,'name':f.name,'sha256':sha(t),'size':size,'format':fmt,'changed_from_original_complete_set':not same,'same_as_previous_lighting_revision':n in [387,396,399]})
checks={}
for n in updated:
 d=(P if n in [392,395] else LATEST)/'editable'/str(n)
 with zipfile.ZipFile(d/'layers.ora') as z:
  assert z.testzip() is None
  xml=ET.fromstring(z.read('stack.xml'));canvas=Image.new('RGBA',(int(xml.attrib['w']),int(xml.attrib['h'])))
  for layer in reversed(list(xml.find('stack'))):
   img=Image.open(io.BytesIO(z.read(layer.attrib['src']))).convert('RGBA');canvas.alpha_composite(img,(int(layer.attrib.get('x',0)),int(layer.attrib.get('y',0))))
  expected=Image.open(d/'merged.png').convert('RGBA');checks[str(n)]=canvas.size==expected.size and canvas.tobytes()==expected.tobytes();assert checks[str(n)]
 for name in ['layers.ora','merged.png']:
  dest=P/'editable'/str(n)/name
  if dest.resolve()!=(d/name).resolve():dest.parent.mkdir(exist_ok=True);shutil.copy2(d/name,dest)
shutil.copy2(P/'review/five-phone-overview.jpg',E/'五张修订预览.jpg')
for n in updated:
 src=(P if n in [392,395] else LATEST)/'review'/('%d-before-left-after-right.jpg'%n)
 shutil.copy2(src,E/('%d_左旧右新.jpg'%n))
for n in [392,395]:
 for label in ['side','knob']:shutil.copy2(P/'review'/('%d-%s-200pct.jpg'%(n,label)),E/('%d-%s-200pct.jpg'%(n,label)))
quality={'status':'REVISION_COMPLETE_FOR_REVIEW','updated_ids':updated,'latest_change_ids':[392,395],'previous_three_byte_preserved':[387,396,399],'checks':{'original372_376_holes_and_blind_circles':'Single photo face preserved; no generated replacement holes','housing':'Unchanged auxiliary300x200x20mm shell; visible continuous sidewall','knob':'Shallow reset disc; orange-red original372 surface','state_separation':'Main product explicitly labeled reset; real382 crop explicitly labeled after-pull short-pin photo; no invented full-panel pins','layout':'Square392 and portrait395; blackgold diagonal composition, large product, circular detail; unsupported original claims excluded','visual_review':'Opened392/395 final full images; five-image390px overview; native face/knob/side detail','ora_recomposition':checks},'remaining_issues':['Silver sidewall reflections remain somewhat uniform and rendered; not claimed photograph-level realism','Main face retains original baked photo lighting','Actual pull stroke/full raised-pin state remains unmeasured; final design deliberately shows only authentic local evidence','Customer acceptance UNKNOWN'],'scope':'389 original Muse WEBP/GPT PNG preserved; all non-updated image bytes preserved; no publishing'}
(E/'逐图核验.json').write_text(json.dumps(quality,ensure_ascii=False,indent=2))
(E/'文件清单.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
for name in ['native-reopen-verification.json','highlight-check.json','layer-pixel-verification.json']:
 shutil.copy2(LATEST/name,E/name)
shutil.copy2(P/'transforms-and-states.json',E/'392-395来源与状态.json')
sources=[ROOT/'lighting-refine/native/product.blend',ROOT/'lighting-refine/native/product.png',R/'production/2026-10-31_顶喷孔位回源可控修复/372-front-rectified.jpg']
sources += [next((R/'products/长方形拉钮顶喷/原始实拍20261030').glob('*%d*'%n)) for n in [372,374,376,382]]
sources += [next((R/'references/2026-10-31_同款商户电商参考').glob('*%d*'%n)) for n in [392,395]]
(E/'来源哈希.json').write_text(json.dumps([{'path':str(f),'sha256':sha(f)} for f in sources],ensure_ascii=False,indent=2))
(T/'阅读说明.md').write_text('''# 顶喷厚度修订整套

两个版本各13张，区别仅第三张389：版本1保留Muse WEBP原文件，版本2保留GPT PNG原文件。

本轮厚度修订包含387、392、395、396、399。392/395主图为复位外观，短针仅在标注“提拉后短针实拍”的382原照小窗展示，不把复位图冒充全板提拉状态，不补画红点。387/396/399沿用上一轮光色修订版，字节未改；其余图片与原完整包一致。

五张已检查全图/手机尺寸总览及相关细节；分层源重组像素一致，原生模型几何沿用已验证版本。剩余限制：银边仍有均匀反射及一定渲染感，实拍贴面保留原光照；不称照片级或客户已验收。提拉行程和完整伸针状态仍未测量，本版以真实局部展示避免推断。

核验与对照目录含五张预览、左旧右新对照、细节裁切、逐图结论、来源和图片SHA256。SHA256SUMS.txt覆盖包内文件（不含清单自身）。打开preview.html可本地查看；该页面未声称完成浏览器验收。旧版与本地可编辑源保留。
''')
cards=''.join('<article><h2>{}</h2><img src="版本1_第一张/{}.jpg"></article>'.format(n,n) for n in updated)
(T/'preview.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>顶喷厚度修订</title><style>body{font:17px/1.65 system-ui;background:#191919;color:#eee;margin:24px}main{display:flex;gap:24px;flex-wrap:wrap}article{max-width:480px}img{width:100%}</style><h1>顶喷厚度修订 · 两套各13张</h1><p>下列5张为修订图。392/395主图展示复位外观，圆窗展示真实提拉后短针；389两份原图保留。银边仍有一定渲染感。</p><main>'+cards+'</main>')
payload=sorted(f for f in T.rglob('*') if f.is_file() and f.name!='SHA256SUMS.txt')
(T/'SHA256SUMS.txt').write_text('\n'.join(sha(f)+'  '+str(f.relative_to(T)) for f in payload)+'\n')
payload=sorted(f for f in T.rglob('*') if f.is_file());archive=P/'顶喷修订整套_双版本.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in payload:z.write(f,str(f.relative_to(P)))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for f in payload:assert hashlib.sha256(z.read(str(f.relative_to(P)))).hexdigest()==sha(f)
receipt={'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'members':len(payload),'image_sets':[13,13],'crc_and_all_member_sha256':True,'ora_exact_recomposition':checks,'original_complete_set_unchanged_files':sum(not x['changed_from_original_complete_set'] for x in records),'previous_three_byte_preserved':True}
(P/'final-verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
print(json.dumps(receipt,ensure_ascii=False))

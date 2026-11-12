from pathlib import Path
from PIL import Image,ImageOps
import hashlib,json,zipfile,shutil,io,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent;R=ROOT.parents[1];P=ROOT/'completed-five'
B=R/'production/2026-11-03_\u9876\u55b7\u6574\u5957_\u7b2c\u4e09\u5f20\u4e24\u4e2a\u7248\u672c/\u9876\u55b7\u6574\u5957_\u7b2c\u4e09\u5f20\u4e24\u4e2a\u7248\u672c'
LATEST=ROOT/'lighting-refine'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
T=P/'\u9876\u55b7\u4fee\u8ba2\u6574\u5957';T.mkdir(exist_ok=True);E=T/'\u6838\u9a8c\u4e0e\u5bf9\u7167';E.mkdir(exist_ok=True)
updated=[387,392,395,396,399];records=[]
for version in ['\u7248\u672c1_\u7b2c\u4e00\u5f20','\u7248\u672c2_\u7b2c\u4e8c\u5f20']:
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
shutil.copy2(P/'review/five-phone-overview.jpg',E/'\u4e94\u5f20\u4fee\u8ba2\u9884\u89c8.jpg')
for n in updated:
 src=(P if n in [392,395] else LATEST)/'review'/('%d-before-left-after-right.jpg'%n)
 shutil.copy2(src,E/('%d_\u5de6\u65e7\u53f3\u65b0.jpg'%n))
for n in [392,395]:
 for label in ['side','knob']:shutil.copy2(P/'review'/('%d-%s-200pct.jpg'%(n,label)),E/('%d-%s-200pct.jpg'%(n,label)))
quality={'status':'REVISION_COMPLETE_FOR_REVIEW','updated_ids':updated,'latest_change_ids':[392,395],'previous_three_byte_preserved':[387,396,399],'checks':{'original372_376_holes_and_blind_circles':'Single photo face preserved; no generated replacement holes','housing':'Unchanged auxiliary300x200x20mm shell; visible continuous sidewall','knob':'Shallow reset disc; orange-red original372 surface','state_separation':'Main product explicitly labeled reset; real382 crop explicitly labeled after-pull short-pin photo; no invented full-panel pins','layout':'Square392 and portrait395; blackgold diagonal composition, large product, circular detail; unsupported original claims excluded','visual_review':'Opened392/395 final full images; five-image390px overview; native face/knob/side detail','ora_recomposition':checks},'remaining_issues':['Silver sidewall reflections remain somewhat uniform and rendered; not claimed photograph-level realism','Main face retains original baked photo lighting','Actual pull stroke/full raised-pin state remains unmeasured; final design deliberately shows only authentic local evidence','Customer acceptance UNKNOWN'],'scope':'389 original Muse WEBP/GPT PNG preserved; all non-updated image bytes preserved; no publishing'}
(E/'\u9010\u56fe\u6838\u9a8c.json').write_text(json.dumps(quality,ensure_ascii=False,indent=2))
(E/'\u6587\u4ef6\u6e05\u5355.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
for name in ['native-reopen-verification.json','highlight-check.json','layer-pixel-verification.json']:
 shutil.copy2(LATEST/name,E/name)
shutil.copy2(P/'transforms-and-states.json',E/'392-395\u6765\u6e90\u4e0e\u72b6\u6001.json')
sources=[ROOT/'lighting-refine/native/product.blend',ROOT/'lighting-refine/native/product.png',R/'production/2026-10-31_\u9876\u55b7\u5b54\u4f4d\u56de\u6e90\u53ef\u63a7\u4fee\u590d/372-front-rectified.jpg']
sources += [next((R/'products/\u957f\u65b9\u5f62\u62c9\u94ae\u9876\u55b7/\u539f\u59cb\u5b9e\u62cd20261030').glob('*%d*'%n)) for n in [372,374,376,382]]
sources += [next((R/'references/2026-10-31_\u540c\u6b3e\u5546\u6237\u7535\u5546\u53c2\u8003').glob('*%d*'%n)) for n in [392,395]]
(E/'\u6765\u6e90\u54c8\u5e0c.json').write_text(json.dumps([{'path':str(f),'sha256':sha(f)} for f in sources],ensure_ascii=False,indent=2))
(T/'\u9605\u8bfb\u8bf4\u660e.md').write_text('''# \u9876\u55b7\u539a\u5ea6\u4fee\u8ba2\u6574\u5957

\u4e24\u4e2a\u7248\u672c\u540413\u5f20\uff0c\u533a\u522b\u4ec5\u7b2c\u4e09\u5f20389\uff1a\u7248\u672c1\u4fdd\u7559Muse WEBP\u539f\u6587\u4ef6\uff0c\u7248\u672c2\u4fdd\u7559GPT PNG\u539f\u6587\u4ef6\u3002

\u672c\u8f6e\u539a\u5ea6\u4fee\u8ba2\u5305\u542b387\u3001392\u3001395\u3001396\u3001399\u3002392/395\u4e3b\u56fe\u4e3a\u590d\u4f4d\u5916\u89c2\uff0c\u77ed\u9488\u4ec5\u5728\u6807\u6ce8\u201c\u63d0\u62c9\u540e\u77ed\u9488\u5b9e\u62cd\u201d\u7684382\u539f\u7167\u5c0f\u7a97\u5c55\u793a\uff0c\u4e0d\u628a\u590d\u4f4d\u56fe\u5192\u5145\u5168\u677f\u63d0\u62c9\u72b6\u6001\uff0c\u4e0d\u8865\u753b\u7ea2\u70b9\u3002387/396/399\u6cbf\u7528\u4e0a\u4e00\u8f6e\u5149\u8272\u4fee\u8ba2\u7248\uff0c\u5b57\u8282\u672a\u6539\uff1b\u5176\u4f59\u56fe\u7247\u4e0e\u539f\u5b8c\u6574\u5305\u4e00\u81f4\u3002

\u4e94\u5f20\u5df2\u68c0\u67e5\u5168\u56fe/\u624b\u673a\u5c3a\u5bf8\u603b\u89c8\u53ca\u76f8\u5173\u7ec6\u8282\uff1b\u5206\u5c42\u6e90\u91cd\u7ec4\u50cf\u7d20\u4e00\u81f4\uff0c\u539f\u751f\u6a21\u578b\u51e0\u4f55\u6cbf\u7528\u5df2\u9a8c\u8bc1\u7248\u672c\u3002\u5269\u4f59\u9650\u5236\uff1a\u94f6\u8fb9\u4ecd\u6709\u5747\u5300\u53cd\u5c04\u53ca\u4e00\u5b9a\u6e32\u67d3\u611f\uff0c\u5b9e\u62cd\u8d34\u9762\u4fdd\u7559\u539f\u5149\u7167\uff1b\u4e0d\u79f0\u7167\u7247\u7ea7\u6216\u5ba2\u6237\u5df2\u9a8c\u6536\u3002\u63d0\u62c9\u884c\u7a0b\u548c\u5b8c\u6574\u4f38\u9488\u72b6\u6001\u4ecd\u672a\u6d4b\u91cf\uff0c\u672c\u7248\u4ee5\u771f\u5b9e\u5c40\u90e8\u5c55\u793a\u907f\u514d\u63a8\u65ad\u3002

\u6838\u9a8c\u4e0e\u5bf9\u7167\u76ee\u5f55\u542b\u4e94\u5f20\u9884\u89c8\u3001\u5de6\u65e7\u53f3\u65b0\u5bf9\u7167\u3001\u7ec6\u8282\u88c1\u5207\u3001\u9010\u56fe\u7ed3\u8bba\u3001\u6765\u6e90\u548c\u56fe\u7247SHA256\u3002SHA256SUMS.txt\u8986\u76d6\u5305\u5185\u6587\u4ef6\uff08\u4e0d\u542b\u6e05\u5355\u81ea\u8eab\uff09\u3002\u6253\u5f00preview.html\u53ef\u672c\u5730\u67e5\u770b\uff1b\u8be5\u9875\u9762\u672a\u58f0\u79f0\u5b8c\u6210\u6d4f\u89c8\u5668\u9a8c\u6536\u3002\u65e7\u7248\u4e0e\u672c\u5730\u53ef\u7f16\u8f91\u6e90\u4fdd\u7559\u3002
''')
cards=''.join('<article><h2>{}</h2><img src="\u7248\u672c1_\u7b2c\u4e00\u5f20/{}.jpg"></article>'.format(n,n) for n in updated)
(T/'preview.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>\u9876\u55b7\u539a\u5ea6\u4fee\u8ba2</title><style>body{font:17px/1.65 system-ui;background:#191919;color:#eee;margin:24px}main{display:flex;gap:24px;flex-wrap:wrap}article{max-width:480px}img{width:100%}</style><h1>\u9876\u55b7\u539a\u5ea6\u4fee\u8ba2 \xb7 \u4e24\u5957\u540413\u5f20</h1><p>\u4e0b\u52175\u5f20\u4e3a\u4fee\u8ba2\u56fe\u3002392/395\u4e3b\u56fe\u5c55\u793a\u590d\u4f4d\u5916\u89c2\uff0c\u5706\u7a97\u5c55\u793a\u771f\u5b9e\u63d0\u62c9\u540e\u77ed\u9488\uff1b389\u4e24\u4efd\u539f\u56fe\u4fdd\u7559\u3002\u94f6\u8fb9\u4ecd\u6709\u4e00\u5b9a\u6e32\u67d3\u611f\u3002</p><main>'+cards+'</main>')
payload=sorted(f for f in T.rglob('*') if f.is_file() and f.name!='SHA256SUMS.txt')
(T/'SHA256SUMS.txt').write_text('\n'.join(sha(f)+'  '+str(f.relative_to(T)) for f in payload)+'\n')
payload=sorted(f for f in T.rglob('*') if f.is_file());archive=P/'\u9876\u55b7\u4fee\u8ba2\u6574\u5957_\u53cc\u7248\u672c.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in payload:z.write(f,str(f.relative_to(P)))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for f in payload:assert hashlib.sha256(z.read(str(f.relative_to(P)))).hexdigest()==sha(f)
receipt={'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'members':len(payload),'image_sets':[13,13],'crc_and_all_member_sha256':True,'ora_exact_recomposition':checks,'original_complete_set_unchanged_files':sum(not x['changed_from_original_complete_set'] for x in records),'previous_three_byte_preserved':True}
(P/'final-verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
print(json.dumps(receipt,ensure_ascii=False))

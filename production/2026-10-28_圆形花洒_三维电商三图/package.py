from pathlib import Path
import hashlib,json,zipfile
B=Path(__file__).resolve().parent;root=B.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();names=['A_暖白三档主图.jpg','B_深色质感主图.jpg','C_双控细节.jpg'];refs=[]
for code in ['R001','R004','R028']:
 p=next((root/'references/2026-10-22_首批参考/01_微信参考原图').glob(code+'_*'));refs.append({'path':str(p),'sha256':sha(p),'role':'Composition/color/type only; no product facts inherited'})
for code in ['339','344','345','348','350','351']:
 p=next((root/'products/主推花洒/结构基准20261027/原件').glob('*_'+code+'_*'));refs.append({'path':str(p),'sha256':sha(p),'role':'Actual SKU structure/controls; viewed, not rendered pixels'})
manifest={'status':'USER_REVIEW_PENDING','requested_model':'gpt-6-astra','requested_effort':'medium','actual_model':'UNKNOWN','method':'Complete deterministic Blender renders plus independent SVG Chinese titles; no AI product pixels or photo cutouts','images':[{'name':n,'width':1600,'height':1600,'sha256':sha(B/n)} for n in names],'baseline_sha256':sha(B/'sources/baseline.blend'),'references':refs,'saved_model_audit':json.loads((B/'saved-model-audit.json').read_text()),'visual_review':'Opened all three full native/composed images and 500px contact. Checked full head boundary, unchanged hole pattern/red control/silver selector, foreground interface occlusion, title clearance and C leader endpoints.','limitations':['Scenes are restrained studio-like spaces, not photoreal bathroom proof.','Black microtexture and neck highlights retain CG characteristics.','C is static control identification, not a physical operation or descaling test.','Model dimensions and peripheral pores are estimates, not calibrated measurements.'],'font':'PingFangSC-Semibold via CoreText glyph outlines, deterministic skew and stroke; editable text in title-strings.json/layout.js; font binary not bundled'}
(B/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(B/'preview.html').write_text('<!doctype html><meta charset="utf-8"><title>圆形花洒三维电商三图</title><style>body{max-width:1100px;margin:30px auto;font:18px system-ui;background:#eee}img{max-width:100%;height:auto}a{margin-right:20px}</style><h1>圆形花洒 · 三张审阅图</h1><p>完整Blender场景＋独立中文标题。造型沿已认可底座，非实物摄影或精密测量；客户接受待定。</p><p><a href="三维电商三图_JPG.zip">3张JPG包</a><a href="三维电商三图_可编辑源.zip">可编辑模型与源</a><a href="README.md">说明</a></p><img src="contact.jpg">'+''.join('<h2>'+n+'</h2><img src="'+n+'">' for n in names))
receipts=[]
for zn,files in [('三维电商三图_JPG.zip',names),('三维电商三图_可编辑源.zip',names+['sources/baseline.blend','A-scene.blend','B-scene.blend','C-scene.blend','A-editable.svg','B-editable.svg','C-editable.svg','render.py','layout.js','outline.swift','title-strings.json','title-paths.json','fonts.conf','audit.py','package.py','README.md','manifest.json','saved-model-audit.json','A-geometry.json','B-geometry.json','C-geometry.json','A-points.json','B-points.json','C-points.json','contact.jpg','preview.html'])]:
 z=B/zn
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as f:
  for n in files:f.write(B/n,n)
 with zipfile.ZipFile(z) as f:
  assert f.testzip() is None
  assert all(hashlib.sha256(f.read(n)).hexdigest()==sha(B/n) for n in files)
 receipts.append({'name':zn,'count':len(files),'bytes':z.stat().st_size,'sha256':sha(z),'crc_error':None,'member_sha256_equal':True})
(B/'package-verification.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2));print(json.dumps(receipts,ensure_ascii=False))

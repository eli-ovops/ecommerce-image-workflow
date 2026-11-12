from pathlib import Path
import hashlib,json,zipfile
B=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
photos=B.parents[2]/'products/主推花洒/结构基准20261027/原件';sources=[]
for code in ['348','345','342']:
 for p in photos.glob('*_'+code+'_*'):sources.append({'path':str(p),'sha256':sha(p),'role':'Actual surface and reflection appearance reference, not rendered pixels'})
r={'status':'USER_REVIEW_PENDING','requested_model':'gpt-6-astra','requested_effort':'medium','actual_model':'UNKNOWN','sources':sources,'saved_check':json.loads((B/'saved-verification.json').read_text()),'image_dimensions':[1600,1600],'visually_opened':['candidate-01.png','candidate-02.png','panel-200.png','neck-200.png','phone.png','圆形花洒_材质精修_棚拍验证.jpg'],'method':'Deterministic Blender material and physical reflection-card/light edits; complete render, no AI or photographic product pixels','iterations':'One main candidate plus one micro-normal correction; no further trials','remaining_limits':'Neck highlight still changes direction due to unchanged surface geometry. Fine panel texture remains weaker than close-up photograph. Rendered chrome/black plastic still not established as photographic realism.','geometry_notice':'No product mesh or transform/camera changes; previous finite-point hole sampling reused, not rerun','hashes':{n:sha(B/n) for n in ['sources/baseline.blend','sources/baseline.jpg','圆形花洒_材质精修.blend','圆形花洒_材质精修_棚拍验证.jpg']}}
(B/'verification.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
imgs=['圆形花洒_材质精修_棚拍验证.jpg','原版与精修等尺度对照.jpg'];(B/'preview.html').write_text('<!doctype html><meta charset="utf-8"><title>圆形花洒材质精修</title><style>body{max-width:1100px;margin:32px auto;font:18px system-ui;background:#eee}img{max-width:100%}</style><h1>材质精修 · 待审阅</h1><p>几何、孔位、相机不变；完整Blender重渲染。反射与微纹理改善不等于照片级成功，颈部仍有高光转折。</p><p><a href="README.md">说明</a> · <a href="verification.json">核验</a> · <a href="圆形花洒_材质精修.blend">可编辑模型</a></p>'+''.join('<h2>'+n+'</h2><img src="'+n+'">' for n in imgs))
files=imgs+['圆形花洒_材质精修.blend','sources/baseline.blend','sources/baseline.jpg','candidate-02.png','refine_final.py','verify_saved.py','refine.py','review.js','export.js','package.py','README.md','preview.html','verification.json','geometry-fingerprints.json','saved-verification.json','parameters.json','panel-200.png','neck-200.png','phone.png']
z=B/'材质精修_模型与验证源.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as f:
 for n in files:f.write(B/n,n)
with zipfile.ZipFile(z) as f:
 assert f.testzip() is None
 assert all(hashlib.sha256(f.read(n)).hexdigest()==sha(B/n) for n in files)
r={'path':str(z),'count':len(files),'bytes':z.stat().st_size,'sha256':sha(z),'crc_error':None,'member_sha256_equal':True};(B/'package-verification.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False))

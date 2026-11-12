from pathlib import Path
import json,hashlib,zipfile
B=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
photos=B.parents[2]/'products/主推花洒/结构基准20261027/原件'
# Project root is three levels above production/date/task.
photos=B.parents[2]/'products/主推花洒/结构基准20261027/原件'
sources=[]
for code in ['339','342','345','348']:
 for p in photos.glob('*_'+code+'_*'):sources.append({'path':str(p),'sha256':sha(p),'role':'actual appearance / geometry reference'})
final=json.loads((B/'final-camera-check.json').read_text())
ver={'status':'USER_REVIEW_PENDING','requested_model':'gpt-6-astra','requested_effort':'medium','actual_model':'UNKNOWN','image':'圆形花洒_截面重建_棚拍验证.jpg','dimensions_px':[1600,1600],'method':'Complete Blender render, no AI product pixels or cutouts','reopen_success':final['reopen_success'],'final_camera_white_rings_four_samples':final['white_rings_4_of_4_first_hits'],'final_camera_peripheral_center_silver_hits':final['peripheral_camera_centers_first_hit_silver'],'coverage':final['coverage'],'visually_opened':['structure-gray-v7.png','side-gray.png','正面实拍对照.jpg','侧面实拍对照.jpg','截面检查.jpg','studio-structure.png','圆形花洒_截面重建_棚拍验证.jpg'],'visual_result':'No prior large shoulder gap or fragments; white holes unobscured in selected image. Key reads silver. Matte face still visually uniform; neck chrome highlight has pointed turns; side gray has residual section traces. Photorealism not established.','dimensions_notice':'All geometry sizes are model values, not measurements','sources':sources,'sha256':{n:sha(B/n) for n in ['圆形花洒_截面重建.blend','圆形花洒_截面重建_棚拍验证.jpg','sources/baseline.blend','sources/white-hole-layout.json']}}
(B/'verification.json').write_text(json.dumps(ver,ensure_ascii=False,indent=2))
imgs=['圆形花洒_截面重建_棚拍验证.jpg','正面实拍对照.jpg','侧面实拍对照.jpg','结构灰模.jpg','截面检查.jpg']
(B/'preview.html').write_text('<!doctype html><meta charset="utf-8"><title>圆形花洒结构重建验证</title><style>body{max-width:1100px;margin:32px auto;font:18px system-ui;background:#eee;color:#222}img{max-width:100%;height:auto}section{margin:36px 0}</style><h1>截面重建 / 待审阅</h1><p>结构修复与单张完整Blender成像验证。非精密扫描、非照片级成功结论。孔口有限点验证见JSON，侧灰仍有分段痕与顶部斜纹，黑面微纹理及颈部银面高光仍有渲染感。</p><p><a href="README.md">说明</a> · <a href="verification.json">实际核验</a> · <a href="圆形花洒_截面重建.blend">可编辑模型</a></p>'+''.join('<section><h2>'+n+'</h2><img src="'+n+'"></section>' for n in imgs))
files=imgs+['圆形花洒_截面重建.blend','structure-master.blend','studio-structure.png','README.md','preview.html','verification.json','master.py','rebuild.py','studio_rebuilt.py','check_structure.py','check_final_camera.py','evidence.py','compose.js','export.js','package.py','parameters.json','scene-settings.json','shell-diagnosis.json','fold-evidence.json','structure-check.json','final-camera-check.json','sources/baseline.blend','sources/white-hole-layout.json','sources/photo339.jpg','sources/photo342.jpg']
z=B/'截面重建_模型与验证源.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as f:
 for n in files:f.write(B/n,n)
with zipfile.ZipFile(z) as f:
 assert f.testzip() is None
 assert all(hashlib.sha256(f.read(n)).hexdigest()==sha(B/n) for n in files)
r={'path':str(z),'count':len(files),'bytes':z.stat().st_size,'sha256':sha(z),'crc_error':None,'member_sha256_equal':True}
(B/'package-verification.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False))

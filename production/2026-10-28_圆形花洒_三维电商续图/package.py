from pathlib import Path
import json,hashlib,zipfile,shutil
B=Path(__file__).resolve().parent;old=B.parent/'2026-10-28_圆形花洒_三维电商三图'
names=['A_暖白三档主图.jpg','B_深色质感主图.jpg','C_双控细节.jpg','D_侧面弧度.jpg','E_银色背面.jpg','F_中央红钮细节.jpg']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for n in names[:3]:
 if (old/n).exists():
  shutil.copy2(old/n,B/n);assert sha(old/n)==sha(B/n)
 else:assert (B/n).exists()
photos=B.parents[1]/'products/主推花洒/结构基准20261027/原件'
refs=B.parents[1]/'references/2026-10-22_首批参考/01_微信参考原图'
inputs=list((B/'sources').glob('*'))+ [p for p in photos.glob('*.jpg') if any('_'+n+'_' in p.name for n in ['340','342','343','346','347','348','349'])]+[refs/'R001_主图_套装推荐.jpg',refs/'R028_细节_硅胶除垢.jpg']
m={'status':'USER_REVIEW_SAMPLES_NOT_FULL_SET','requested_model':'gpt-6-astra','requested_effort':'medium','actual_model':'UNKNOWN','rules':['PERMISSIONS-2026-10-14-v1','ROUTING-2026-10-27-v7','IMAGE-REVISION-2026-10-28-v1'],'inputs':([{'path':str(p),'sha256':sha(p)} for p in inputs] if all(p.exists() for p in inputs) else json.loads((B/'manifest.json').read_text())['inputs']),'jpg':[{'file':n,'sha256':sha(B/n)} for n in names],'existing_ABC_byte_preserved':True,'new_geometry':'Unchanged product mesh and topology; only common rigid flip/lift for E; cameras and set objects changed. See saved-model-audit.json.','reference_use':'Reuse current batch 74-image read receipt in previous three-image manifest; actual R001 copper-brown hierarchy and R028 large continuous head detail revisited. No reference product claims, accessories or materials inherited.','actual_visual_review':['342/343 side,340/346/347 back,348 panel,349 rim','low-resolution D/E/F complete frames and combined title preview','Final 1600 JPG full frames, panel/rim/neck crops and six-image phone-size contact reviewed'],'limitations':['Analytical model from photo estimates, not calibrated scan or dimensional truth.','E rear gradient card improves broad bright-dark chrome response, but neck retains visible source-surface section traces.','CG appearance and simplified stage; no photographic-realism or customer approval claim.','F static red actuator, no demonstrated pressing, pins, water or performance.']}
(B/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
(B/'preview.html').write_text('<meta charset="utf-8"><title>圆形花洒六张审阅样图</title><style>body{margin:30px;background:#e8e2d9;font:18px sans-serif;color:#482d20}main{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}img{width:100%}a{color:inherit}</style><h1>三维电商审阅样图 · 六张</h1><p>A–C 保留原字节；新增 D 侧面、E 背面、F 静态红钮近景。尚有 CG 感及背颈细分段高光痕，不是完整套图或客户验收。</p><main>'+''.join(f'<a href="{n}"><img src="{n}">{n}</a>' for n in names)+'</main>')
(B/'README.md').write_text('''# 圆形花洒三维电商续图（审阅样图）
新增 D/E/F，合并已交 A/B/C 共六张 1600×1600 JPG。旧三张字节不变。

商品来自 sources/baseline.blend（已确认材质精修资产），完整 Blender 场景渲染，无 AI 像素、实拍抠层、人物或水流。未修改商品网格/孔位/局部比例；E 为共同刚体翻面与落地平移，D/F 仅相机与场景。白接口以机位出画/前景石台遮挡，几何保留。

复现：Blender 5.2.2 `-b --python render.py -- final`；`swift outline.swift <本目录绝对路径>`；`node layout.js final`；Blender `-b --python audit.py`；`python3 package.py`。layout.js 依赖现有 Sharp，路径见脚本，字形已以 SVG 路径保存，正常导出无需字体。修改文字后重新运行 Swift（macOS PingFangSC-Semibold）。最终 scene.blend 可独立打开，SVG 内嵌渲染底图。

来源、SHA 与检查范围见 manifest.json / saved-model-audit.json。当前仅样图：背面大反射梯度已有改善，颈部仍有源曲面分段高光，整体有 CG 感；实拍参考未相机标定，模型不是尺寸或精密几何真值。F 仅静态控件，不表示按压测试或清洁效果已验证。未扩完整套图，用户/客户接受 UNKNOWN。
''')
checks={}
def pack(name,files):
 with zipfile.ZipFile(B/name,'w',zipfile.ZIP_DEFLATED) as z:
  for p in files:z.write(p,p.relative_to(B))
 with zipfile.ZipFile(B/name) as z:
  assert z.testzip() is None
  assert all(hashlib.sha256(z.read(i)).hexdigest()==sha(B/i) for i in z.namelist())
 checks[name]={'members':len(files),'bytes':(B/name).stat().st_size,'sha256':sha(B/name),'crc_and_member_sha_verified':True}
pack('圆形花洒_三维六图_JPG.zip',[B/n for n in names])
files=[B/n for n in ['render.py','layout.js','outline.swift','title-strings.json','title-paths.json','fonts.conf','audit.py','package.py','overview.js','review-crops.js','manifest.json','README.md','preview.html','saved-model-audit.json']]+list((B/'sources').glob('*.blend'))
for k in 'DEF':files += [B/(k+x) for x in ['-scene.blend','-editable.svg','-geometry.json']]
files += [B/n for n in names]
pack('三维续图_可编辑源.zip',files)
(B/'package-verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print(json.dumps(checks,ensure_ascii=False,indent=2))

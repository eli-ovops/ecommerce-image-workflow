from pathlib import Path
from PIL import Image
import json,zipfile,hashlib
B=Path(__file__).resolve().parent;R=B.parents[1];m=json.loads((B/'manifest.json').read_text());aa=m['assets'];z=B/'三档水型与加长详情_JPG_21张.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
 for a in aa:
  p=B/'JPG'/a['file'];Image.open(p).verify();assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'];f.write(p,a['file'])
with zipfile.ZipFile(z) as f:
 assert len(f.namelist())==21 and f.testzip() is None
 for a in aa:assert hashlib.sha256(f.read(a['file'])).hexdigest()==a['sha256']
(B/'package-check.json').write_text(json.dumps({'count':21,'jpg_only':True,'crc':'PASS','member_hashes':'21/21 MATCH','zip_sha256':hashlib.sha256(z.read_bytes()).hexdigest()},indent=2))
ordered=sorted(aa,key=lambda a:(a['id']!='M04',a['id']))
cards=''.join(f'<article><h2>{a["id"]} · {a["name"]}</h2><a href="JPG/{a["file"]}"><img loading="lazy" src="JPG/{a["file"]}"></a></article>' for a in ordered)
(B/'交付总览.html').write_text('<!doctype html><meta charset="utf-8"><title>三档水型与加长详情</title><style>body{font:16px system-ui;background:#f3eee7;margin:24px;color:#39281d}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}article{background:white;padding:16px}img{width:100%}h2{font-size:18px}</style><h1>三档水型与加长详情</h1><p>20张独立图＋1张长详情；95普通、96喷雾、97混合。长详情1000×18008，16章节。</p><main>'+cards+'</main>')
(B/'README.md').write_text('''# 三档水型与加长详情

用户已确认：95普通、96喷雾、97混合。98–100不推断。

新增W01普通、W02混合、W03喷雾独立展示，M04替换为三档总览。三张由内置image_gen使用各自实拍引导调整背景，实际查看并对照原图，保持整体水型区别；不能声称逐孔出水、商品几何或水流像素硬锁定，不作为性能实测证据。原生结果留在sources内。

新增面板、头柄、背面三个细节章节。长详情16章节，1000×18008，约旧版同宽1.9倍；参考790×25920。参考中的未知过滤、抗菌、增压倍数、材料、认证等不继承，不为达到相同长度编造卖点。

21项交付JPG（20独立+1长图）。已实际查看新图总览、三张原生水型和长图四段预览；未修改资产复用之前审阅。ZIP回读21项哈希一致。客户接受待审。

入口：交付总览.html。交付包：三档水型与加长详情_JPG_21张.zip。旧版保留，文件夹中历史复制文件不作为本轮交付；本轮准确范围以manifest及ZIP为准。extend.py为本轮新增排版源，package.py为本轮打包入口；旧finalize.py不用于本版。
''')
m['review']={'current_visual':'三张原生水型逐张查看；新增七图总览及长详情四段预览已查看。未改图复用旧审阅。','source_confirmation':'user:95普通96喷雾97混合','geometry':'人工外观比对，非自动逐孔或几何验收','customer':'AWAITING_REVIEW'};(B/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
p=R/'AGENTS.md';s=p.read_text().replace('# 电商图片项目规则','# 电商图片项目规则\n\n## 2026-10-25 最新：三档对应已确认及加长详情\n\n用户明确确认95普通、96喷雾、97混合；此前“不标具体档位”限制仅对未确认98–100继续适用。已按各自实拍引导制作三张水型及三档总览，追加面板/头柄/背面章节，长详情16章节1000×18008。本轮21项JPG（20独立+1长图），入口 `production/2026-10-25_三档水型与加长详情/README.md`。生成水型非原像素硬锁定，客户待审。用户仍拒绝细小脚注，延续暖白铜棕风格，无依据参考功能不继承。\n',1);p.write_text(s)
print(z,round(z.stat().st_size/1048576,1),'MiB')

from pathlib import Path
from PIL import Image
import json,hashlib,zipfile,html
B=Path(__file__).resolve().parent;m=json.loads((B/'manifest.json').read_text());out=B/'JPG';aa=m['assets']
notes={
'M05':'首屏使用已认可完整人物场景；文件哈希与旧版一致，没有重绘肤质。',
'M01':'主商品放大；三档以明显大字分组，减少左侧空背景。标题与产品不相交。',
'M04':'三个完整方形画面统一缩放，保留出水起点，标签放独立铜棕区。透视机位仍不同。',
'D01':'三色并列完整头部；颜色各自取旧SKU层；减少同浴室背景重复。',
'D02':'将前背/颈部视觉任务合成一页，取消重复D07/D08；底带65px大字。',
'D05':'仅保留正向商品信息；删除售卖范围及未包含配件说明。',
'W01':'普通档源95对应候选，完整面板与水流原点未裁掉；没有加水。',
'W02':'混合档源97对应候选，未为了差异额外加雾；与普通的细微视觉区别仍待客户判断。',
'W03':'喷雾档源96对应候选，六处雾束保留；未新增性能文案。',
'L01':'13章接缝与顺序检查；长图14721高比旧18008更紧凑，减少的是重复页，非声称比参考更长。'}
reviews=[]
for a in aa:
 p=out/a['file'];im=Image.open(p);im.load();assert im.format=='JPEG';assert list(im.size)==a['size'];assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
 reviews.append({'id':a['id'],'composition_review':'人工查看review/sheet-1至3全图预览；M01/D02/D05再打开原JPG检查','observation':notes.get(a['id'],'本轮未改图，源文件字节复用；整组预览确认保留已认可暖白铜棕风格。'),'technical':'JPEG decode and SHA256 PASS','acceptance':'用户待审'})
m['status']='REVIEW_PACKAGE_READY';m['visual_review']='已实际查看17张独立图接触表以及新M01/D02/D05原JPG；水型源图、95/96/97原实拍与R023及新增长参考关键段已对照。原生成图几何/肤质/水流未作自动保证。'
(B/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));(B/'visual-review.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2))
zp=B/'广告节奏优化_正向信息版_JPG_18张.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
 for a in aa:z.write(out/a['file'],'JPG/'+a['file'])
with zipfile.ZipFile(zp) as z:
 assert z.testzip() is None
 for a in aa:assert hashlib.sha256(z.read('JPG/'+a['file'])).hexdigest()==a['sha256']
receipt={'count':len(aa),'jpg_only':True,'all_hashes_match':True,'crc':'PASS','zip_sha256':hashlib.sha256(zp.read_bytes()).hexdigest(),'zip_bytes':zp.stat().st_size};(B/'package-check.json').write_text(json.dumps(receipt,indent=2))
css='body{margin:0;background:#eee7dc;color:#2b211a;font-family:system-ui}main{max-width:1180px;margin:auto;padding:32px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}article{background:white;padding:12px}img{width:100%;height:auto}article img{max-height:540px;object-fit:contain}a{color:#835336}h1{font-size:34px}p{line-height:1.7}.long{max-width:790px;margin:35px auto}.long img{display:block}'
items=''.join(f'<article><a href="JPG/{html.escape(a["file"])}"><img loading="lazy" src="JPG/{html.escape(a["file"])}"></a><h3>{a["id"]} · {a["name"]}</h3></article>' for a in aa if a['id']!='L01')
l=next(a for a in aa if a['id']=='L01')
(B/'交付总览.html').write_text(f'<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>广告节奏优化 · 审阅版</title><style>{css}</style><main><h1>广告节奏优化</h1><p>17张独立JPG + 1条完整详情。人物首屏、三档同画幅对照、合并重复外观与操作章节。<br>此版为排版优化审阅包，商品与水型沿用已有实拍引导生成资产，未宣称几何与水流硬锁定。</p><p><a href="{zp.name}">下载完整JPG压缩包</a>　<a href="JPG/{l["file"]}">打开完整长详情 1000 × 14721</a></p><div class="grid">{items}</div><div class="long"><img src="JPG/{l["file"]}"></div></main></html>')
(B/'README.md').write_text('''# 广告节奏优化（待用户审阅）

入口：交付总览.html；交付：广告节奏优化_正向信息版_JPG_18张.zip。

17张独立图 + 1条1000×14721详情。本次仅删除D05的售卖范围与未包含说明并重组长图，其余16图哈希不变。已读取现有源图、用户长参考关键段、R023和A022及95/96/97水型实拍；复用本批74参考全读记录（production/2026-10-22_参考重构/reference-map.md）。

改变：已认可人物场景移至首屏且字节不变；三档以完整同尺寸画幅展示，不裁掉出水起点；主图商品加大；三色转干净并列选色；旧D03并入M02/M03，D07/D08并入D02；商品信息大字集中，不增细小脚注。

未改图字节复制。未新增生成调用，未重绘人物、未补画水流。精简重复章节后长图由18008降至14721像素；这是节奏优化，不能称为加长。原图与旧版全部保留。

限制：水型和商品主体沿用既有实拍引导生成资产，不是实际照片原像素或3D硬约束。三档源机位不一致；普通/混合差异由源图决定，未夸张增强。人物与商品几何仍以客户审阅为准。此版并未解决新增多场景拍摄或水流物理还原的全部问题。

实际视觉审查见visual-review.json；JPEG解码、数量、ZIP CRC及逐项哈希回读见package-check.json。脚本optimize.py可重建本次排版。客户接受未取得。
''')
print(json.dumps(receipt,ensure_ascii=False))

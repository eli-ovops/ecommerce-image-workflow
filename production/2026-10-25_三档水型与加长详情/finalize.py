from pathlib import Path
from PIL import Image
import json,hashlib,zipfile,html
B=Path(__file__).resolve().parent;R=B.parents[1];m=json.loads((B/'manifest.json').read_text());aa=m['assets']
old=json.loads((R/'production/2026-10-24_完整电商套图/reference-coverage.json').read_text())
mp={'M01':['M01'],'M02':['M06'],'M03':['D02'],'M04':['M02','M04'],'M05':['M03'],'M06':['M05'],'M07':['M01'],'M08':['D03'],'K01':['K01'],'K02':['K02'],'K03':['K03'],'D01':['M01'],'D02':['D01'],'D03':['M03','M04','D03'],'D04':['M04'],'D05':['M02'],'D06':['D02'],'D07':['D04'],'D08':['M06'],'D09':['D02','D05'],'W01':['M03'],'W02':['M06']}
entries=[]
for e in old['entries']:
 targets=sorted(set(t for oid in e.get('outputs',[]) for t in mp.get(oid,[])))
 if e['reference_id'] in ['R019','R026','A019','A021']:targets=['M05']
 entries.append({'reference_id':e['reference_id'],'previous_outputs':e.get('outputs',[]),'current_outputs':targets,'previous_disposition':e['disposition'],'note':'沿原覆盖表承接内容任务；当前用户认可的暖白风格替换旧光色与碎片排版，不声称逐参考视觉复刻。' if targets else '保留原表的重复、集合或不适用说明，见原覆盖表。'})
(B/'reference-coverage.json').write_text(json.dumps({'entries':entries,'total':len(entries),'original_receipt':old['reference_read_receipt'],'old_to_new':mp,'limitation':'任务承接映射，不是本轮重新全读74张或逐张风格通过证明'},ensure_ascii=False,indent=2))
for a in aa:
 p=B/'JPG'/a['file'];im=Image.open(p);im.verify();assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
m['status']='EXPORTED_FOR_USER_REVIEW';m['review']={'visual':'14张独立图分三页查看，M02原尺寸复核，长图由同版图片等比串接；非自动几何识别。','checks':['未新增无依据功能/尺寸/材质','按压与水流使用原实拍裁切','三色独立来源且等高展示','人物复用用户认可版本，不再次重绘','文字与产品主体未发生重要遮挡'],'limitations':['现有生成商品层并非严格三维锁定，最终商品外观仍需用户审阅','出水仅为未标档位的实拍局部','本轮为14单图+1长图的合并修订，不沿用旧24张数量']}
(B/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
cards=''.join(f'<article><h2>{a["id"]} · {a["name"]}</h2><a href="JPG/{a["file"]}"><img loading="lazy" src="JPG/{a["file"]}"></a><p>{a["size"][0]} × {a["size"][1]}</p></article>' for a in aa)
(B/'交付总览.html').write_text('<!doctype html><meta charset="utf-8"><title>暖白电商修订</title><style>body{font:16px system-ui;background:#f3eee7;color:#39281d;margin:30px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px}article{background:white;padding:16px}img{width:100%;height:auto}h2{font-size:18px}</style><h1>暖白电商修订 · 14 张独立图 + 1 张长详情</h1><p>已统一广告字级、暖白场景与铜棕标题带。本套待用户审阅。</p><main>'+cards+'</main>')
z=B/'暖白电商修订_去小字_JPG_15张.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
 for a in aa:f.write(B/'JPG'/a['file'],a['file'])
with zipfile.ZipFile(z) as f:
 assert f.testzip() is None
 assert len(f.namelist())==15
 for a in aa:assert hashlib.sha256(f.read(a['file'])).hexdigest()==a['sha256']
(B/'package-check.json').write_text(json.dumps({'count':15,'jpg_only':True,'crc':'PASS','member_sha256':'15/15 MATCH','zip_sha256':hashlib.sha256(z.read_bytes()).hexdigest()},indent=2))
(B/'README.md').write_text('''# 暖白电商修订

用户已认可代表图风格并要求开始制作。本轮沿同一风格合并修订为14张独立图+1张长详情，包含6张主图、3色SKU、5张细节与商品信息图。

入口：交付总览.html；交付包：暖白电商修订_去小字_JPG_15张.zip。

背景与下键操作画面通过内置image_gen生成；人物沿用认可JPG，未再重绘。其余商品使用已有各色生成图层，保持等比；不等同实拍像素或CAD硬锁定。除垢状态和水流局部直接裁切原实拍，未标水型对应，不重画红针水流。

字体通过独立排版调整为粗斜黑字、浅金偏移与铜棕标题带。真实拍摄房间未作为生活场景，主图与SKU多用出画裁切隐藏裸螺纹。

build.py为可编辑制作源。manifest.json记录输出和限制，reference-coverage.json承接旧74项内容映射，package-check.json为15项JPG回读验证。旧版、原件全部保留。内部查看不等于客户对本套验收。
''')
print(z)

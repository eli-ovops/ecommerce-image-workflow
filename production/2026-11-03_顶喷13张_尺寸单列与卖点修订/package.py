# -*- coding: utf-8 -*-
from pathlib import Path
import json,zipfile,hashlib,html
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
notes={
387:('大面板／大水量／细密喷面','已移除尺寸、除垢标题和红针小窗。黑金构图保留。主面板局部叶纹断裂和黑色杂点仍明显，小窗也有一处黑色异物状伪影；产品细节未通过。'),
388:('丰沛雨幕／畅快淋浴','已去尺寸与除垢，保留上大下小和红边白字。下方纹样部分断裂，红钮偏深；水幕仍有规则珠链感，逐孔真实性UNKNOWN。'),
389:('宽幅雨幕／舒展畅淋','已去尺寸与除垢，并回源修正首次重复商品名。原冷蓝场景和主次保留；左下纹样比上一批杂乱候选改善，但孔序仍非实拍硬锁，水束偏规则。'),
390:('充沛出水／畅爽雨淋','已去尺寸与除垢，并回源修正首次左下多余管件。墨绿场景保留；纹样及孔序仍有近似，红钮偏深，上方中央水束与红钮投影重叠，真实起点UNKNOWN。'),
391:('淋浴体验（原版保留）','原JPG字节未改。沿用上一轮局部面板变形及生成水花限制，不当真人试用或性能证据。'),
392:('提拉清洁（原版保留）','原JPG字节未改，真实短针小窗保留。主面板暗红点与完整提拉状态对应UNKNOWN，孔纹未精确复现。'),
393:('空气增压／绵密雨幕／喷面接口','采用用户确认的同款卖点，保留完整商品，不画内部剖面和节水对比。新图管件为银色，暖石格栅场景延续；生成面板与开口微距不是实拍像素，水流仍有珠链感。'),
394:('竖版淋浴体验（原版保留）','原JPG字节未改。沿用上一轮人物、水花和局部纹样限制。'),
395:('竖版提拉清洁（原版保留）','原JPG字节未改，真实短针窗保留；主面板红点不能证明完整实际拉出状态，原有问题保留。'),
396:('喷面／红钮／侧边／接口／大面板／短针','原尺寸卡改为宽幅大面板，尺寸已去。短针空窗插入原始实拍裁片，提供真实两层ORA。其余生成卡片不能当实拍；大面板孔序及红钮深度仍近似。'),
397:('唯一规格图：约30×20×2cm','本套唯一尺寸标注，尺寸只写一处。保留暖石格栅和侧厚近景，无内部结构示意。上下面板纹样仍有交叠，生成水流不能证明真实流量。'),
398:('可调角度／接头／背部','依据用户同款卖点确认增加方向箭头，不写360度或性能对比；无尺寸。主喷面缩小时可看，200%可见明显密集纹样交叠，接头细节属生成近似。'),
399:('大面板／大水量／舒展空间','已去除尺寸及除垢标题，保留黑金斜轴静态商品。文字比其它图更接近参考衬线风格；主面板局部断纹、多余孔和红钮偏深仍待返工。')}
checks=json.loads((P/'export-verification.json').read_text());rows=[]
for c in checks:
    n=c['id'];purpose,note=notes[n];rows.append(dict(**c,purpose=purpose,findings=note,status='REVIEW_CANDIDATE_PRODUCT_DETAIL_NOT_ACCEPTED',copy_review='manual pass: size only on 397; descaling headings only on 392 and 395',dimensions_visible=n==397,descaling_headline=n in [392,395],whole_image_viewed=True,detail_200pct_viewed=c['changed'],reference_pair_viewed=c['changed'],customer_acceptance='UNKNOWN'))
dump('quality-review.json',dict(date='2026-11-03',owner='existing sole visual owner',runtime_model='UNKNOWN',generation_tool='image_gen.imagegen',successful_calls=11,failed_calls_this_round=0,changed=[c['id'] for c in checks if c['changed']],unchanged=[c['id'] for c in checks if not c['changed']],all13_present=True,dimension_images=[397],descaling_headline_images=[392,395],geometry_acceptance='NOT_PASSED',water_origin_accuracy='UNKNOWN',images=rows))
md=['# 顶喷13张：尺寸单列与卖点修订','','2026-11-03。已完成9张受影响图片回源生成＋4张原JPG保留，合成13张审阅集。尺寸只在397写一次约30×20×2cm，提拉除垢标题只在392、395。图组与文字调整已完成；商品几何和水流真实性未通过最终验收。','','## 制作与来源','','本轮11次内置生图均返回文件：9张首候选、389和390各一次定向纠正。全部输入为原始同行参考与本品实拍（部分等比缩至1280），没有旧AI成品作为模型输入。初版重复文字／多余管件候选保存在native下但不进入JPG包。','','391、392、394、395复制上一轮JPG，SHA一致。396的短针小窗为真实照片，源路径和SHA见photo-composite.json；native/396.png仍是留白原生图，最终JPG取editable/396/merged.png。其ORA只有扁平生成底图＋实拍小窗两层，不能声称文字、产品或水流可独立编辑。其它新图只有扁平原生PNG。','','新源包是本轮修改源与记录，不含同行参考图；未改4张的原生源仍在上一轮目录，provenance保留对应记录。JPG包为13张完整审阅图。无对外发送、发布、删除或覆盖旧版。','','卖点依据用户本次明确同款确认，不把空气增压和角度调节写成本轮独立性能测量。未使用未知内部机构、同行品牌、售后、31cm、数值性能或节水比例。','','## 逐图变动与问题','','| 编号 | 卖点 | 本轮 |','|---|---|---|']
md += ['| {} | {} | {} |'.format(r['id'],r['purpose'],'回源更新' if r['changed'] else '原字节保留') for r in rows]
md += ['','## 实际视觉审查','']+[f"- {r['id']}：{r['findings']}" for r in rows]
md += ['','查看了新图原生整图、导出总览、9张原参考左右对照、9张200%面板裁片及396合成后整图；4张未改图复用前次细节审查并核字节一致。原始实拍372和支持细节用于对照，生成纹样并非精确孔位。机械解码／尺寸／CRC／SHA与ORA重组检查通过不代表商品真实。HTML仅本地阅读入口，未声称浏览器或真机验收。','', '限制：多次回源仍不能稳定复现孔纹，已保留失败证据并停止同路线无依据抽图，不把目前候选称客户定稿。']
(P/'README.md').write_text('\n'.join(md),encoding='utf-8')
cards=[]
for r in rows:
    n=r['id'];extra=f'<a href="review/{n}-old-left-new-right.jpg">旧左／新右</a> · <a href="review/{n}-face-200pct.jpg">面板200%</a>' if r['changed'] else '原图字节保留'
    cards.append(f'<article><h2>{n} · {r["purpose"]}</h2><a href="JPG/{n}.jpg"><img loading="lazy" src="JPG/{n}.jpg" alt="{n}审阅图"></a><p>{html.escape(r["findings"])}</p><p>{extra}</p></article>')
(P/'preview.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>顶喷13张 · 尺寸单列</title><style>body{font:17px/1.65 system-ui;margin:24px;background:#171717;color:#eee}a{color:#f4cf88}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px}article{padding:16px;background:#292929;border-radius:10px}img{width:100%;height:auto}h2{font-size:20px}</style><h1>顶喷13张审阅集 · 尺寸单列</h1><p>9张回源更新，4张保留。尺寸仅在397，除垢标题仅在392、395。文字与图组调整完成；部分孔纹与水流仍有生成偏差，以下逐图注明。</p><p><a href="JPG-13-review.zip">13张JPG</a> · <a href="revision-source-records.zip">本轮修改源与记录</a> · <a href="README.md">完整检查记录</a></p><main>'+''.join(cards)+'</main></html>',encoding='utf-8')
sourcefiles=sorted([f for folder in ['native','editable','sources','provenance'] for f in (P/folder).rglob('*') if f.is_file()])+sorted([f for f in P.iterdir() if f.is_file() and f.suffix in ['.json','.py','.md'] and f.name!='package-verification.json'])
results=[]
for name,files in [('JPG-13-review.zip',sorted((P/'JPG').glob('*.jpg'))),('revision-source-records.zip',sourcefiles)]:
    zpath=P/name
    with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
        for f in files:z.write(f,f.relative_to(P).as_posix())
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None;members=[]
        for f in files:
            arc=f.relative_to(P).as_posix();digest=sha(f);assert hashlib.sha256(z.read(arc)).hexdigest()==digest;members.append(dict(path=arc,sha256=digest))
    results.append(dict(file=name,bytes=zpath.stat().st_size,sha256=sha(zpath),count=len(files),crc_pass=True,all_members_match=True,members=members))
dump('package-verification.json',results)
print(json.dumps([{k:v for k,v in r.items() if k!='members'} for r in results],ensure_ascii=False))

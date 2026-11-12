from pathlib import Path
import json, hashlib, zipfile, html
from PIL import Image

B=Path(__file__).resolve().parent
def save(name,obj): (B/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
notes={
387:('黑金竖置商品、白色台座、左侧细节窗、底部规格带','主面板局部纹样交叠、孔序未复现；短针窗已换实拍。'),
388:('上方安装出水、左下完整外观、白字红边粗斜标题、米色底栏','水柱有珠串感；主面板局部叶形错位，逐孔对应UNKNOWN。'),
389:('冷蓝浴室、左上安装、左下竖置商品、右侧黑色大标题','面板局部纹样拉伸，水柱有珠串感；逐孔对应UNKNOWN。'),
390:('墨绿浴室、上方大面板与水幕、左下产品、金色标题','上方面板纹样尺度偏粗；小产品纹样局部不规则；逐孔对应UNKNOWN。'),
391:('星空蓝顶、暖墙、仰视顶喷、原创成年人物','人物整图未见明显肢体异常；水花仍有摆拍感；面板局部纹样变形，逐孔对应UNKNOWN。'),
392:('黑金斜轴大主体、左上标题、右下圆形细节窗','已移除错误喷水候选并改为干态；真实短针窗可查，主面板孔中暗红点与实际状态对应UNKNOWN，纹样不精确。'),
393:('暖石墙与右侧格栅、安装顶喷、底部双细节卡','删除无依据AIR爆炸图和节水对比；生成接头及面板细节并非实拍像素；面板纹样与逐孔水源未核准。'),
394:('竖版星空暖墙、上方顶喷、下方原创成年人物','水流和人物接触为生成表现；顶喷局部纹样交叠，逐孔对应UNKNOWN。'),
395:('竖版黑金斜轴大主体、圆形短针窗','主面板大量红点未能证明真实提拉状态；纹样偏离。小窗已换实际短针照片；主商品待返工。'),
396:('黑金标题、两列三行细节卡','接头开口与短针两卡已换实拍；其余生成面板仍有红点状态与纹样问题。原生2:3画幅，未强拉为参考9:16。'),
397:('竖版暖石浴室、完整顶喷、底部侧面与尺寸卡','上方面板有明显重复纹样变形、交叠；逐孔对应UNKNOWN。原生画幅约5:8。'),
398:('暖石浴室静态安装、右侧黑玻璃、底部接头与背面卡','不含水流或360度宣称。商品较小，放大后纹样仍不规则；接头和背面为生成近似，精确结构UNKNOWN。'),
399:('竖版黑金斜轴商品、上方三组标题、静态无水','面板有明显叶形交叠、孔序和边缘纹样异常；待返工。')}
rows=[]
for n,(layout,note) in notes.items():
    p=B/'JPG'/f'{n}.jpg'
    with Image.open(p) as im: size=list(im.size)
    rows.append(dict(id=n,reference_id=n,file=str(p.relative_to(B)),size=size,sha256=sha(p),layout=layout,status='REVIEW_CANDIDATE_REWORK_REQUIRED',findings=note,per_hole_fidelity='UNKNOWN',customer_acceptance='UNKNOWN',whole_image_viewed=True,reference_comparison_viewed=True,face_200pct_viewed=True,editable_ora=f'editable/{n}/layers.ora' if n in [387,392,395,396] else None))
save('quality-review.json',dict(date='2026-11-03',method='manual qualitative review; diagnosis framework/script unavailable; no calibrated score',tool='image_gen.imagegen',runtime_model='UNKNOWN',successful_generations=14,pre_generation_input_limit_rejections=1,images=rows,overall='13张审阅集齐全，商品几何与水流真实性未通过最终验收。'))
intro='13张审阅候选：7张方图、6张竖图。按387–399逐张参考排版，原始实拍约束商品。生成商品不是原像素或几何硬锁定，所有图片均待用户审阅；可见纹样偏差需返工，逐孔水流对应UNKNOWN。'
md=['# 新Skill 13张完整审阅集','',intro,'','2026-11-02开始，2026-11-03完成本次审阅打包。','', '## 来源与可编辑范围','', '实际输入、提示词、原生输出见 generation-receipts.json、actual-jobs.json、input-manifest.json。全部生图从原始参考和实拍输入，未把上一轮AI成品送入模型。392首版错误水流候选单独保留，不进入JPG包。','', '387、392、395、396提供真实分层ORA：扁平AI底图＋实拍小窗（396另含文字层）；其余9张仅有扁平原生PNG，不是全元素分层源。原生生成文字不可单独编辑。export-verification.json中无ORA图的false表示不适用，不是重组失败。','', '人工查看13张整图、13张参考左右对照、13张面板200%裁片及4张合成后的整图。四个ORA已通过CRC与重组验证，JPG解码通过；这些不替代产品真实性和客户接受。HTML仅作本地阅读入口，未宣称浏览器验收。','', '源记录包供内部使用，包含实拍素材与来源路径；不包含商户参考图片及左右对照图。JPG包仅13张候选。无对外发送或发布。','', '## 逐图映射与诊断','']
for r in rows: md += [f"### {r['id']} · 待审阅／商品细节待返工",'',r['layout'],r['findings'],'']
(B/'README.md').write_text('\n'.join(md),encoding='utf-8')
cards=[]
for r in rows:
    n=r['id']; cards.append(f'<article><h2>{n} · 审阅候选</h2><a href="JPG/{n}.jpg"><img loading="lazy" src="JPG/{n}.jpg" alt="{n}审阅图"></a><p>{html.escape(r["findings"])}</p><p><a href="review/{n}-reference-left-candidate-right.jpg">参考左／候选右（内部）</a> · <a href="review/{n}-face-200pct.jpg">面板200%</a></p></article>')
(B/'preview.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>13张审阅集</title><style>body{font:17px/1.7 system-ui;margin:24px;background:#171717;color:#eee}a{color:#f4cf88}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px}article{background:#292929;padding:16px;border-radius:12px}img{width:100%;height:auto}h1{font-size:28px}</style><h1>13张完整审阅集</h1><p>'+intro+'</p><p><a href="JPG-13-review.zip">13张JPG下载</a> · <a href="source-records-internal.zip">内部源记录包</a> · <a href="README.md">检查记录</a></p><main>'+''.join(cards)+'</main></html>',encoding='utf-8')
manifest=json.loads((B/'input-manifest.json').read_text())
products=[Path(x['tool_input']) for x in manifest if '/products/' in x['original']]
files=[p for folder in ['native','editable','sources'] for p in (B/folder).rglob('*') if p.is_file()]+products
files += [p for p in B.iterdir() if p.is_file() and p.suffix in ['.json','.py','.md'] and p.name!='package-verification.json']
results=[]
for name,paths in [('JPG-13-review.zip',sorted((B/'JPG').glob('*.jpg'))),('source-records-internal.zip',sorted(set(files)))]:
    zpath=B/name
    with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
        for p in paths:z.write(p,p.relative_to(B).as_posix())
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None
        members=[]
        for p in paths:
            arc=p.relative_to(B).as_posix(); digest=sha(p)
            assert hashlib.sha256(z.read(arc)).hexdigest()==digest
            members.append(dict(path=arc,sha256=digest))
    results.append(dict(file=name,bytes=zpath.stat().st_size,sha256=sha(zpath),count=len(paths),crc_pass=True,all_members_match=True,members=members))
save('package-verification.json',results)
print(json.dumps([{k:v for k,v in r.items() if k!='members'} for r in results],ensure_ascii=False,indent=2))

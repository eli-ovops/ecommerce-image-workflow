# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import json,hashlib,shutil,zipfile,html
P=Path(__file__).resolve().parent;OLD=P.parent/'2026-11-02_新Skill_13张完整审阅集'
for d in ['JPG','context-old','review','provenance']:(P/d).mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
changed=[387,388,389];unchanged=[391,392,394,395,396];blocked=[390,393,397,398,399]
jobs=json.loads((P/'actual-generation-jobs.json').read_text(encoding='utf-8'));jobmap={j['id']:j for j in jobs}
findings={387:'主商品叶瓣纹变成斜向网格，盲圆点丢失明显，细节窗与主商品纹样不一致；实物忠实度未通过。文案和黑金版式已更新。',388:'下方商品纹样仍有断裂/错位；上方接头未连接管件，悬置感需复核。水幕仍有珠链感，逐孔起点UNKNOWN。文案更新清楚。',389:'左下商品右半部纹样出现明显重叠杂乱，实物忠实度未通过。水流有串珠感，逐孔起点UNKNOWN；冷蓝场景和新卖点可审阅。'}
purpose={387:'宽幅大面板／充沛水量／细密喷面',388:'丰沛雨幕',389:'宽幅雨幕／畅淋',390:'大面板／充沛出水／畅爽雨淋',391:'淋浴体验（保留）',392:'提拉清洁功能（保留）',393:'空气增压／绵密雨幕／喷面接口',394:'竖版淋浴体验（保留）',395:'竖版提拉清洁（保留）',396:'喷面、红钮、银边、接头、尺寸、短针六细节（保留）',397:'空气增压／绵密雨幕／30×20×2cm',398:'角度可调／连接与背部',399:'宽幅大面板／充沛出水'}
rows=[]
for n in range(387,400):
    src=OLD/'JPG'/f'{n}.jpg'
    if n in changed:
        im=Image.open(P/'native'/f'{n}.png').convert('RGB');dst=P/'JPG'/f'{n}.jpg';im.save(dst,quality=97,subsampling=0)
        status='新候选：文字已改，商品细节待返工';note=findings[n]
        before=ImageOps.contain(Image.open(src),(625,800));after=ImageOps.contain(im,(625,800));pair=Image.new('RGB',(before.width+after.width,max(before.height,after.height)),'white');pair.paste(before);pair.paste(after,(before.width,0));pair.save(P/'review'/f'{n}-before-after.jpg',quality=96)
        ref=Path(jobmap[n]['inputs'][0]);a=ImageOps.contain(Image.open(ref),(625,800));b=ImageOps.contain(im,(625,800));pair=Image.new('RGB',(a.width+b.width,max(a.height,b.height)),'white');pair.paste(a);pair.paste(b,(a.width,0));pair.save(P/'review'/f'{n}-reference-candidate.jpg',quality=96)
    else:
        dst=P/'context-old'/f'{n}.jpg';shutil.copy2(src,dst);assert sha(src)==sha(dst);im=Image.open(dst)
        status='原版保留，无需修改' if n in unchanged else '待完成：此处仅展示旧版'
        note='沿用上一轮审阅记录；本次未重绘，原有几何/水流限制继续保留。' if n in unchanged else ('本次生成连接失败，无返回产物；新文案已备好。' if n in [390,393,397] else '服务连续失败后停止，本张未调用生成；新文案已备好。')
    with Image.open(dst) as check:check.load();size=list(check.size)
    ImageOps.contain(im,(360,640)).save(P/'review'/f'{n}-mobile.jpg',quality=95)
    rows.append(dict(id=n,file=str(dst.relative_to(P)),status=status,purpose=purpose[n],note=note,size=size,sha256=sha(dst),changed=n in changed,planned_copy=jobmap[n]['copy'] if n in jobmap else '原版不变',customer_acceptance='UNKNOWN'))
    if n in changed:
        j=jobmap[n];j['input_hashes']=[dict(path=s,sha256=sha(Path(s))) for s in j['inputs']];j['output_sha256']=sha(P/'native'/f'{n}.png')
dump('completed-generation-records.json',[jobmap[n] for n in changed]);dump('review-manifest.json',dict(state='PARTIAL_BLOCKED_BY_IMAGEGEN_CONNECTION_ERRORS',completed_candidates=changed,unchanged=unchanged,pending=blocked,images=rows,runtime_model='UNKNOWN',new_generations=3,failed_requests=4,not_submitted_compact_jobs=True,abandoned_overlay_script_executed=False))
for name in ['input-manifest.json','generation-receipts.json','quality-review.json']:shutil.copy2(OLD/name,P/'provenance'/('previous-'+name))
md=['# 卖点重分配：部分完成，生图连接受阻','','2026-11-03。只有387、388、389三张回源新候选；不是13张返修完成。三张文案改好，但商品纹样仍有明确缺陷，不能称最终合格。','','391、392、394、395、396保留旧版。390、393、397生成连接失败；398、399尚未生成。共3次成功、4次失败请求（388首次失败，缩小原始输入后成功；随后390、393、397连续失败）。按协调方指令停止继续请求，无后台作业。','','## 方法和范围','','没有把旧AI图片再次送入模型；新图只用原始参考和实拍。未使用色块遮旧字；revise.py是未运行的弃用方案。inputs-1280及compact-generation-jobs.json只是准备，未提交。新3图为扁平原生PNG，文字也已嵌入，不提供伪造文字分层源。旧参考图不放入下载JPG包。','','用户本轮已确认同款卖点一致；空气增压、角度可调等为用户确认基础上的拟用表达，不冒充本轮独立性能测量。尺寸保持30×20×2cm；未复制品牌、31cm、售后和内部结构。','','## 逐图分配与状态','','| 编号 | 本轮卖点 | 状态 |','|---|---|---|']
md += [f"| {r['id']} | {r['purpose']} | {r['status']} |" for r in rows]
md += ['','## 新候选实看问题','']+[f"- {n}：{findings[n]}" for n in changed]
md += ['','已实际查看新图整图、原始实拍、参考布局和200%面板裁片。输出解码/尺寸、ZIP CRC与成员SHA另见package-verification.json；技术检查不代表商品图通过。','', '后续待内置生图服务恢复后继续5张，先查看本目录实际回执避免重复提交；新候选商品缺陷也需回源处理。原件与旧版未删除。']
(P/'README.md').write_text('\n'.join(md),encoding='utf-8')
cards=[]
for r in rows:
    n=r['id'];extra=f'<a href="review/{n}-before-after.jpg">旧左／新右</a> · <a href="review/{n}-face-200pct.png">面板200%</a>' if n in changed else ''
    cards.append(f'<article><h2>{n} · {r["status"]}</h2><p>{r["purpose"]}</p><a href="{r["file"]}"><img loading="lazy" src="{r["file"]}" alt="{n}"></a><p>{html.escape(r["note"])}</p><p>{extra}</p></article>')
(P/'preview.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>卖点调整 · 3张新候选</title><style>body{font:17px/1.6 system-ui;margin:24px;background:#171717;color:#eee}a{color:#f4cf88}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px}article{padding:16px;background:#292929;border-radius:10px}img{width:100%;height:auto}h2{font-size:20px}</style><h1>卖点调整：3张新候选，5张待生成</h1><p>生图服务连续连接失败，已停止请求。下方13张用于核对整组节奏：只有387–389是本轮新图，其余均明确标注旧版。新图商品纹样仍有问题。</p><p><a href="JPG-3-new-candidates.zip">下载3张新JPG</a> · <a href="source-records-partial.zip">本轮源图与记录</a> · <a href="README.md">逐图分配与未完成清单</a></p><main>'+''.join(cards)+'</main></html>',encoding='utf-8')
sheet=Image.new('RGB',(1500,530),'#eee');d=ImageDraw.Draw(sheet)
for i,n in enumerate(changed):
    im=ImageOps.contain(Image.open(P/'JPG'/f'{n}.jpg'),(500,500));sheet.paste(im,(i*500,30));d.text((i*500+10,8),str(n),fill='black')
sheet.save(P/'review'/'new-three-overview.jpg',quality=96)
results=[]
sourcefiles=sorted((P/'native').glob('*.png'))+[P/n for n in ['README.md','METHOD.md','generation-jobs.json','actual-generation-jobs.json','completed-generation-records.json','review-manifest.json','finish_partial.py']]+sorted(P.glob('*-receipt.json'))+sorted(P.glob('*-network-attempt.json'))
for name,files in [('JPG-3-new-candidates.zip',sorted((P/'JPG').glob('*.jpg'))),('source-records-partial.zip',sourcefiles)]:
    zpath=P/name
    with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
        for f in files:z.write(f,f.relative_to(P).as_posix())
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None
        members=[]
        for f in files:
            name2=f.relative_to(P).as_posix();digest=sha(f);assert hashlib.sha256(z.read(name2)).hexdigest()==digest;members.append(dict(path=name2,sha256=digest))
    results.append(dict(file=name,bytes=zpath.stat().st_size,sha256=sha(zpath),count=len(files),crc_pass=True,all_members_match=True,members=members))
dump('package-verification.json',results)
print(json.dumps([{k:v for k,v in r.items() if k!='members'} for r in results],ensure_ascii=False))

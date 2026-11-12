# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import json,hashlib,shutil,zipfile,html
P=Path(__file__).resolve().parent;OLD=P.parent/'2026-11-02_\u65b0Skill_13\u5f20\u5b8c\u6574\u5ba1\u9605\u96c6'
for d in ['JPG','context-old','review','provenance']:(P/d).mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
changed=[387,388,389];unchanged=[391,392,394,395,396];blocked=[390,393,397,398,399]
jobs=json.loads((P/'actual-generation-jobs.json').read_text(encoding='utf-8'));jobmap={j['id']:j for j in jobs}
findings={387:'\u4e3b\u5546\u54c1\u53f6\u74e3\u7eb9\u53d8\u6210\u659c\u5411\u7f51\u683c\uff0c\u76f2\u5706\u70b9\u4e22\u5931\u660e\u663e\uff0c\u7ec6\u8282\u7a97\u4e0e\u4e3b\u5546\u54c1\u7eb9\u6837\u4e0d\u4e00\u81f4\uff1b\u5b9e\u7269\u5fe0\u5b9e\u5ea6\u672a\u901a\u8fc7\u3002\u6587\u6848\u548c\u9ed1\u91d1\u7248\u5f0f\u5df2\u66f4\u65b0\u3002',388:'\u4e0b\u65b9\u5546\u54c1\u7eb9\u6837\u4ecd\u6709\u65ad\u88c2/\u9519\u4f4d\uff1b\u4e0a\u65b9\u63a5\u5934\u672a\u8fde\u63a5\u7ba1\u4ef6\uff0c\u60ac\u7f6e\u611f\u9700\u590d\u6838\u3002\u6c34\u5e55\u4ecd\u6709\u73e0\u94fe\u611f\uff0c\u9010\u5b54\u8d77\u70b9UNKNOWN\u3002\u6587\u6848\u66f4\u65b0\u6e05\u695a\u3002',389:'\u5de6\u4e0b\u5546\u54c1\u53f3\u534a\u90e8\u7eb9\u6837\u51fa\u73b0\u660e\u663e\u91cd\u53e0\u6742\u4e71\uff0c\u5b9e\u7269\u5fe0\u5b9e\u5ea6\u672a\u901a\u8fc7\u3002\u6c34\u6d41\u6709\u4e32\u73e0\u611f\uff0c\u9010\u5b54\u8d77\u70b9UNKNOWN\uff1b\u51b7\u84dd\u573a\u666f\u548c\u65b0\u5356\u70b9\u53ef\u5ba1\u9605\u3002'}
purpose={387:'\u5bbd\u5e45\u5927\u9762\u677f\uff0f\u5145\u6c9b\u6c34\u91cf\uff0f\u7ec6\u5bc6\u55b7\u9762',388:'\u4e30\u6c9b\u96e8\u5e55',389:'\u5bbd\u5e45\u96e8\u5e55\uff0f\u7545\u6dcb',390:'\u5927\u9762\u677f\uff0f\u5145\u6c9b\u51fa\u6c34\uff0f\u7545\u723d\u96e8\u6dcb',391:'\u6dcb\u6d74\u4f53\u9a8c\uff08\u4fdd\u7559\uff09',392:'\u63d0\u62c9\u6e05\u6d01\u529f\u80fd\uff08\u4fdd\u7559\uff09',393:'\u7a7a\u6c14\u589e\u538b\uff0f\u7ef5\u5bc6\u96e8\u5e55\uff0f\u55b7\u9762\u63a5\u53e3',394:'\u7ad6\u7248\u6dcb\u6d74\u4f53\u9a8c\uff08\u4fdd\u7559\uff09',395:'\u7ad6\u7248\u63d0\u62c9\u6e05\u6d01\uff08\u4fdd\u7559\uff09',396:'\u55b7\u9762\u3001\u7ea2\u94ae\u3001\u94f6\u8fb9\u3001\u63a5\u5934\u3001\u5c3a\u5bf8\u3001\u77ed\u9488\u516d\u7ec6\u8282\uff08\u4fdd\u7559\uff09',397:'\u7a7a\u6c14\u589e\u538b\uff0f\u7ef5\u5bc6\u96e8\u5e55\uff0f30\xd720\xd72cm',398:'\u89d2\u5ea6\u53ef\u8c03\uff0f\u8fde\u63a5\u4e0e\u80cc\u90e8',399:'\u5bbd\u5e45\u5927\u9762\u677f\uff0f\u5145\u6c9b\u51fa\u6c34'}
rows=[]
for n in range(387,400):
    src=OLD/'JPG'/f'{n}.jpg'
    if n in changed:
        im=Image.open(P/'native'/f'{n}.png').convert('RGB');dst=P/'JPG'/f'{n}.jpg';im.save(dst,quality=97,subsampling=0)
        status='\u65b0\u5019\u9009\uff1a\u6587\u5b57\u5df2\u6539\uff0c\u5546\u54c1\u7ec6\u8282\u5f85\u8fd4\u5de5';note=findings[n]
        before=ImageOps.contain(Image.open(src),(625,800));after=ImageOps.contain(im,(625,800));pair=Image.new('RGB',(before.width+after.width,max(before.height,after.height)),'white');pair.paste(before);pair.paste(after,(before.width,0));pair.save(P/'review'/f'{n}-before-after.jpg',quality=96)
        ref=Path(jobmap[n]['inputs'][0]);a=ImageOps.contain(Image.open(ref),(625,800));b=ImageOps.contain(im,(625,800));pair=Image.new('RGB',(a.width+b.width,max(a.height,b.height)),'white');pair.paste(a);pair.paste(b,(a.width,0));pair.save(P/'review'/f'{n}-reference-candidate.jpg',quality=96)
    else:
        dst=P/'context-old'/f'{n}.jpg';shutil.copy2(src,dst);assert sha(src)==sha(dst);im=Image.open(dst)
        status='\u539f\u7248\u4fdd\u7559\uff0c\u65e0\u9700\u4fee\u6539' if n in unchanged else '\u5f85\u5b8c\u6210\uff1a\u6b64\u5904\u4ec5\u5c55\u793a\u65e7\u7248'
        note='\u6cbf\u7528\u4e0a\u4e00\u8f6e\u5ba1\u9605\u8bb0\u5f55\uff1b\u672c\u6b21\u672a\u91cd\u7ed8\uff0c\u539f\u6709\u51e0\u4f55/\u6c34\u6d41\u9650\u5236\u7ee7\u7eed\u4fdd\u7559\u3002' if n in unchanged else ('\u672c\u6b21\u751f\u6210\u8fde\u63a5\u5931\u8d25\uff0c\u65e0\u8fd4\u56de\u4ea7\u7269\uff1b\u65b0\u6587\u6848\u5df2\u5907\u597d\u3002' if n in [390,393,397] else '\u670d\u52a1\u8fde\u7eed\u5931\u8d25\u540e\u505c\u6b62\uff0c\u672c\u5f20\u672a\u8c03\u7528\u751f\u6210\uff1b\u65b0\u6587\u6848\u5df2\u5907\u597d\u3002')
    with Image.open(dst) as check:check.load();size=list(check.size)
    ImageOps.contain(im,(360,640)).save(P/'review'/f'{n}-mobile.jpg',quality=95)
    rows.append(dict(id=n,file=str(dst.relative_to(P)),status=status,purpose=purpose[n],note=note,size=size,sha256=sha(dst),changed=n in changed,planned_copy=jobmap[n]['copy'] if n in jobmap else '\u539f\u7248\u4e0d\u53d8',customer_acceptance='UNKNOWN'))
    if n in changed:
        j=jobmap[n];j['input_hashes']=[dict(path=s,sha256=sha(Path(s))) for s in j['inputs']];j['output_sha256']=sha(P/'native'/f'{n}.png')
dump('completed-generation-records.json',[jobmap[n] for n in changed]);dump('review-manifest.json',dict(state='PARTIAL_BLOCKED_BY_IMAGEGEN_CONNECTION_ERRORS',completed_candidates=changed,unchanged=unchanged,pending=blocked,images=rows,runtime_model='UNKNOWN',new_generations=3,failed_requests=4,not_submitted_compact_jobs=True,abandoned_overlay_script_executed=False))
for name in ['input-manifest.json','generation-receipts.json','quality-review.json']:shutil.copy2(OLD/name,P/'provenance'/('previous-'+name))
md=['# \u5356\u70b9\u91cd\u5206\u914d\uff1a\u90e8\u5206\u5b8c\u6210\uff0c\u751f\u56fe\u8fde\u63a5\u53d7\u963b','','2026-11-03\u3002\u53ea\u6709387\u3001388\u3001389\u4e09\u5f20\u56de\u6e90\u65b0\u5019\u9009\uff1b\u4e0d\u662f13\u5f20\u8fd4\u4fee\u5b8c\u6210\u3002\u4e09\u5f20\u6587\u6848\u6539\u597d\uff0c\u4f46\u5546\u54c1\u7eb9\u6837\u4ecd\u6709\u660e\u786e\u7f3a\u9677\uff0c\u4e0d\u80fd\u79f0\u6700\u7ec8\u5408\u683c\u3002','','391\u3001392\u3001394\u3001395\u3001396\u4fdd\u7559\u65e7\u7248\u3002390\u3001393\u3001397\u751f\u6210\u8fde\u63a5\u5931\u8d25\uff1b398\u3001399\u5c1a\u672a\u751f\u6210\u3002\u51713\u6b21\u6210\u529f\u30014\u6b21\u5931\u8d25\u8bf7\u6c42\uff08388\u9996\u6b21\u5931\u8d25\uff0c\u7f29\u5c0f\u539f\u59cb\u8f93\u5165\u540e\u6210\u529f\uff1b\u968f\u540e390\u3001393\u3001397\u8fde\u7eed\u5931\u8d25\uff09\u3002\u6309\u534f\u8c03\u65b9\u6307\u4ee4\u505c\u6b62\u7ee7\u7eed\u8bf7\u6c42\uff0c\u65e0\u540e\u53f0\u4f5c\u4e1a\u3002','','## \u65b9\u6cd5\u548c\u8303\u56f4','','\u6ca1\u6709\u628a\u65e7AI\u56fe\u7247\u518d\u6b21\u9001\u5165\u6a21\u578b\uff1b\u65b0\u56fe\u53ea\u7528\u539f\u59cb\u53c2\u8003\u548c\u5b9e\u62cd\u3002\u672a\u4f7f\u7528\u8272\u5757\u906e\u65e7\u5b57\uff1brevise.py\u662f\u672a\u8fd0\u884c\u7684\u5f03\u7528\u65b9\u6848\u3002inputs-1280\u53cacompact-generation-jobs.json\u53ea\u662f\u51c6\u5907\uff0c\u672a\u63d0\u4ea4\u3002\u65b03\u56fe\u4e3a\u6241\u5e73\u539f\u751fPNG\uff0c\u6587\u5b57\u4e5f\u5df2\u5d4c\u5165\uff0c\u4e0d\u63d0\u4f9b\u4f2a\u9020\u6587\u5b57\u5206\u5c42\u6e90\u3002\u65e7\u53c2\u8003\u56fe\u4e0d\u653e\u5165\u4e0b\u8f7dJPG\u5305\u3002','','\u7528\u6237\u672c\u8f6e\u5df2\u786e\u8ba4\u540c\u6b3e\u5356\u70b9\u4e00\u81f4\uff1b\u7a7a\u6c14\u589e\u538b\u3001\u89d2\u5ea6\u53ef\u8c03\u7b49\u4e3a\u7528\u6237\u786e\u8ba4\u57fa\u7840\u4e0a\u7684\u62df\u7528\u8868\u8fbe\uff0c\u4e0d\u5192\u5145\u672c\u8f6e\u72ec\u7acb\u6027\u80fd\u6d4b\u91cf\u3002\u5c3a\u5bf8\u4fdd\u630130\xd720\xd72cm\uff1b\u672a\u590d\u5236\u54c1\u724c\u300131cm\u3001\u552e\u540e\u548c\u5185\u90e8\u7ed3\u6784\u3002','','## \u9010\u56fe\u5206\u914d\u4e0e\u72b6\u6001','','| \u7f16\u53f7 | \u672c\u8f6e\u5356\u70b9 | \u72b6\u6001 |','|---|---|---|']
md += [f"| {r['id']} | {r['purpose']} | {r['status']} |" for r in rows]
md += ['','## \u65b0\u5019\u9009\u5b9e\u770b\u95ee\u9898','']+[f"- {n}\uff1a{findings[n]}" for n in changed]
md += ['','\u5df2\u5b9e\u9645\u67e5\u770b\u65b0\u56fe\u6574\u56fe\u3001\u539f\u59cb\u5b9e\u62cd\u3001\u53c2\u8003\u5e03\u5c40\u548c200%\u9762\u677f\u88c1\u7247\u3002\u8f93\u51fa\u89e3\u7801/\u5c3a\u5bf8\u3001ZIP CRC\u4e0e\u6210\u5458SHA\u53e6\u89c1package-verification.json\uff1b\u6280\u672f\u68c0\u67e5\u4e0d\u4ee3\u8868\u5546\u54c1\u56fe\u901a\u8fc7\u3002','', '\u540e\u7eed\u5f85\u5185\u7f6e\u751f\u56fe\u670d\u52a1\u6062\u590d\u540e\u7ee7\u7eed5\u5f20\uff0c\u5148\u67e5\u770b\u672c\u76ee\u5f55\u5b9e\u9645\u56de\u6267\u907f\u514d\u91cd\u590d\u63d0\u4ea4\uff1b\u65b0\u5019\u9009\u5546\u54c1\u7f3a\u9677\u4e5f\u9700\u56de\u6e90\u5904\u7406\u3002\u539f\u4ef6\u4e0e\u65e7\u7248\u672a\u5220\u9664\u3002']
(P/'README.md').write_text('\n'.join(md),encoding='utf-8')
cards=[]
for r in rows:
    n=r['id'];extra=f'<a href="review/{n}-before-after.jpg">\u65e7\u5de6\uff0f\u65b0\u53f3</a> \xb7 <a href="review/{n}-face-200pct.png">\u9762\u677f200%</a>' if n in changed else ''
    cards.append(f'<article><h2>{n} \xb7 {r["status"]}</h2><p>{r["purpose"]}</p><a href="{r["file"]}"><img loading="lazy" src="{r["file"]}" alt="{n}"></a><p>{html.escape(r["note"])}</p><p>{extra}</p></article>')
(P/'preview.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>\u5356\u70b9\u8c03\u6574 \xb7 3\u5f20\u65b0\u5019\u9009</title><style>body{font:17px/1.6 system-ui;margin:24px;background:#171717;color:#eee}a{color:#f4cf88}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px}article{padding:16px;background:#292929;border-radius:10px}img{width:100%;height:auto}h2{font-size:20px}</style><h1>\u5356\u70b9\u8c03\u6574\uff1a3\u5f20\u65b0\u5019\u9009\uff0c5\u5f20\u5f85\u751f\u6210</h1><p>\u751f\u56fe\u670d\u52a1\u8fde\u7eed\u8fde\u63a5\u5931\u8d25\uff0c\u5df2\u505c\u6b62\u8bf7\u6c42\u3002\u4e0b\u65b913\u5f20\u7528\u4e8e\u6838\u5bf9\u6574\u7ec4\u8282\u594f\uff1a\u53ea\u6709387\u2013389\u662f\u672c\u8f6e\u65b0\u56fe\uff0c\u5176\u4f59\u5747\u660e\u786e\u6807\u6ce8\u65e7\u7248\u3002\u65b0\u56fe\u5546\u54c1\u7eb9\u6837\u4ecd\u6709\u95ee\u9898\u3002</p><p><a href="JPG-3-new-candidates.zip">\u4e0b\u8f7d3\u5f20\u65b0JPG</a> \xb7 <a href="source-records-partial.zip">\u672c\u8f6e\u6e90\u56fe\u4e0e\u8bb0\u5f55</a> \xb7 <a href="README.md">\u9010\u56fe\u5206\u914d\u4e0e\u672a\u5b8c\u6210\u6e05\u5355</a></p><main>'+''.join(cards)+'</main></html>',encoding='utf-8')
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

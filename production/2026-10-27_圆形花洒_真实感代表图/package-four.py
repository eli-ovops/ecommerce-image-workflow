# -*- coding: utf-8 -*-
from pathlib import Path
from urllib.parse import quote
import hashlib,html,json,zipfile,subprocess,re
B=Path(__file__).resolve().parent
items=[('已认可主图','银色花洒_暖白浴室主图.jpg'),('下方按键切档','追加三图/A_下键切档.jpg'),('中央红钮细节','追加三图/B_红钮细节.jpg'),('圆盘厚边','追加三图/C_圆盘厚边.jpg')]
expected='66ed25f685db7bd1a9523a6a25c501ecb336dead7f957e4cc1ed362a55c2bea4'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha((B/items[0][1]).read_bytes())==expected,'Approved original changed'
records=[]
for title,rel in items:
 p=B/rel
 info=subprocess.check_output(['sips','-g','pixelWidth','-g','pixelHeight',str(p)],text=True)
 w=int(re.search(r'pixelWidth: (\d+)',info).group(1));h=int(re.search(r'pixelHeight: (\d+)',info).group(1))
 assert (w,h)==(1440,1440)
 records.append(dict(title=title,path=rel,width=w,height=h,bytes=p.stat().st_size,sha256=sha(p.read_bytes())))
zipname='圆形花洒_暖白实拍四图_JPG.zip'
with zipfile.ZipFile(B/zipname,'w',compression=zipfile.ZIP_STORED) as z:
 for i,rec in enumerate(records,1):
  n=f'{i:02d}_{Path(rec["path"]).name}';zi=zipfile.ZipInfo(n,date_time=(2026,10,27,19,0,0));zi.external_attr=0o100644<<16;z.writestr(zi,(B/rec['path']).read_bytes());rec['zip_member']=n
with zipfile.ZipFile(B/zipname) as z:
 assert z.testzip() is None
 assert len(z.infolist())==4
 for rec in records:assert sha(z.read(rec['zip_member']))==rec['sha256']
cards=''.join(f'<article><a href="{quote(r["path"])}"><img src="{quote(r["path"])}" alt="{html.escape(r["title"])}"></a><h2>{html.escape(r["title"])}</h2><a download href="{quote(r["path"])}">下载 JPG</a></article>' for r in records)
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>圆形花洒 · 暖白实拍四图</title><style>body{margin:0;background:#f4f0e9;color:#30241b;font:17px system-ui}main{max-width:1400px;margin:auto;padding:28px}h1{font-size:30px}p{line-height:1.7}a{color:#805336}section{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}article{padding:14px;background:white;border-radius:16px}img{width:100%;display:block;border-radius:8px}h2{font-size:22px;margin:14px 0 6px}@media(max-width:700px){section{grid-template-columns:1fr}}</style><main><h1>圆形花洒 · 暖白实拍四图</h1><p>原认可首图＋本轮新增三张，均为1440×1440 JPG。点击图片查看原尺寸。</p>'''+f'<p><a download href="{quote(zipname)}">下载完整四图 JPG 包</a></p><section>'+cards+'''</section><p>本轮新三张供审阅。圆盘厚边采用原实拍，银边保留少量环境与肤色镜面反射。原认可首图保持不变。</p></main></html>'''
(B/'四张审阅总览.html').write_text(page)
report=dict(date='2026-10-27',status='新增三图制作及内部检查完成，待用户审阅',count=4,new_count=3,images=records,approved_image_unchanged=True,zip=dict(path=zipname,bytes=(B/zipname).stat().st_size,sha256=sha((B/zipname).read_bytes()),member_count=4,crc='PASS',member_hashes='PASS'),root_visual_review=['A/B/C最终JPG已实际打开','A下键mask截角已修','C343手部遮挡和C342窄条候选不交付','C345整头等比裁切，原反射保留'],limits=['A仅银面局部AI反射编辑；B/C商品取实拍','无水流或人物实验','C是斜正面头部厚边近景，不是完整侧背几何验收'],client_acceptance='UNKNOWN')
(B/'四图交付核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'count':4,'new_count':3,'zip_bytes':(B/zipname).stat().st_size,'crc':'PASS','member_hashes':'PASS','original_unchanged':True},ensure_ascii=False))

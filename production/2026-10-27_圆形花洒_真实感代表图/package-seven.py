# -*- coding: utf-8 -*-
from pathlib import Path
from urllib.parse import quote
import hashlib,html,json,zipfile,subprocess,re
B=Path(__file__).resolve().parent
items=[('已认可主图','银色花洒_暖白浴室主图.jpg'),('下方按键切档','追加三图/A_下键切档.jpg'),('中央红钮细节','追加三图/B清洁/B_红钮细节_清洁版.jpg'),('圆盘厚边','追加三图/C_圆盘厚边.jpg'),('日常手持','续作三图/D_日常手持.jpg'),('真实按压红钮','续作三图/E_按压红钮.jpg'),('银色背面','续作三图/F_银色背面.jpg')]
expected='66ed25f685db7bd1a9523a6a25c501ecb336dead7f957e4cc1ed362a55c2bea4'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha((B/items[0][1]).read_bytes())==expected,'Approved original changed'
preserved={
 '追加三图/A_下键切档.jpg':'3e349e25257d2a8f8fd806bd9fd0c2223b857b683f38252baf6a8cce8a1934b5',
 '追加三图/B清洁/B_红钮细节_清洁版.jpg':'9937a139de6780a133cc011c0e18e6aac1a9c0ced927302728d03125ffd31fe8',
 '追加三图/C_圆盘厚边.jpg':'84569113e08702560cbd0c44536856d3f449e4e6c8e30e92157cb17442f2b61c'}
for rel,h in preserved.items():assert sha((B/rel).read_bytes())==h,rel+' changed'
records=[]
for title,rel in items:
 p=B/rel
 info=subprocess.check_output(['sips','-g','pixelWidth','-g','pixelHeight',str(p)],text=True)
 w=int(re.search(r'pixelWidth: (\d+)',info).group(1));h=int(re.search(r'pixelHeight: (\d+)',info).group(1))
 assert (w,h)==(1440,1440)
 records.append(dict(title=title,path=rel,width=w,height=h,bytes=p.stat().st_size,sha256=sha(p.read_bytes())))
zipname='圆形花洒_暖白实拍七图_JPG.zip'
with zipfile.ZipFile(B/zipname,'w',compression=zipfile.ZIP_STORED) as z:
 for i,rec in enumerate(records,1):
  n=f'{i:02d}_{Path(rec["path"]).name}';zi=zipfile.ZipInfo(n,date_time=(2026,10,27,19,0,0));zi.external_attr=0o100644<<16;z.writestr(zi,(B/rec['path']).read_bytes());rec['zip_member']=n
with zipfile.ZipFile(B/zipname) as z:
 assert z.testzip() is None
 assert len(z.infolist())==7
 for rec in records:assert sha(z.read(rec['zip_member']))==rec['sha256']
cards=''.join(f'<article><a href="{quote(r["path"])}"><img src="{quote(r["path"])}" alt="{html.escape(r["title"])}"></a><h2>{html.escape(r["title"])}</h2><a download href="{quote(r["path"])}">下载 JPG</a></article>' for r in records)
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>圆形花洒 · 暖白实拍七图</title><style>body{margin:0;background:#f4f0e9;color:#30241b;font:17px system-ui}main{max-width:1400px;margin:auto;padding:28px}h1{font-size:30px}p{line-height:1.7}a{color:#805336}section{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}article{padding:14px;background:white;border-radius:16px}img{width:100%;display:block;border-radius:8px}h2{font-size:22px;margin:14px 0 6px}@media(max-width:700px){section{grid-template-columns:1fr}}</style><main><h1>圆形花洒 · 暖白实拍七图</h1><p>累计七张：此前四张＋本轮新增三张，均为1440×1440 JPG。点击图片查看原尺寸。</p>'''+f'<p><a download href="{quote(zipname)}">下载完整七图 JPG 包</a></p><section>'+cards+'''</section><p>本轮新增日常手持、真实按压红钮、银色背面。此前四张保持不变；点击图片查看原尺寸，背面金属反射经过局部编辑。</p></main></html>'''
(B/'七张审阅总览.html').write_text(page)
report=dict(date='2026-10-27',status='新增日常手持、真实按压、背面三图，待用户审阅',count=7,new_count=3,images=records,approved_image_unchanged=True,zip=dict(path=zipname,bytes=(B/zipname).stat().st_size,sha256=sha((B/zipname).read_bytes()),member_count=7,crc='PASS',member_hashes='PASS'),root_visual_review=['A/B/C最终JPG已实际打开','A下键mask截角已修','B三处水渍局部实拍纹理修补，root已看放大前后和最终JPG','B旧矩形微距窗被用户拒绝，改339大圆头近景，root已实开最终JPG','C343手部遮挡和C342窄条候选不交付','C345整头等比裁切，原反射保留','D/E/F最终JPG需root实开后运行本脚本；D持握不伪称实际按键动作；E短红针源于94真实按压；F外轮廓源于340，银色内面反射经过AI编辑'],limits=['A/F仅银面局部AI反射编辑；B/C/D/E商品取实拍','F反射为生成处理，仍需用户确认摄影真实感，不等于完整实物摄影','无水流或人物实验','C是斜正面头部厚边近景，不是完整侧背几何验收'],client_acceptance='UNKNOWN')
(B/'七图交付核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'count':7,'new_count':3,'zip_bytes':(B/zipname).stat().st_size,'crc':'PASS','member_hashes':'PASS','original_unchanged':True},ensure_ascii=False))

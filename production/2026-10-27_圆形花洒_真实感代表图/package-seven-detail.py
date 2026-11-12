# -*- coding: utf-8 -*-
from pathlib import Path
from urllib.parse import quote
import hashlib,html,json,zipfile,subprocess,re
B=Path(__file__).resolve().parent
items=[('已认可主图','银色花洒_暖白浴室主图.jpg'),('下方按键切档','细节返修/A_下键切档_精修.jpg'),('中央红钮细节','追加三图/B清洁/B_红钮细节_清洁版.jpg'),('圆盘厚边','追加三图/C_圆盘厚边.jpg'),('日常手持','细节返修/D_日常手持_精修.jpg'),('真实按压红钮','续作三图/E_按压红钮.jpg'),('银色背面','续作三图/F_银色背面.jpg')]
expected='66ed25f685db7bd1a9523a6a25c501ecb336dead7f957e4cc1ed362a55c2bea4'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha((B/items[0][1]).read_bytes())==expected,'Approved original changed'
preserved={'银色花洒_暖白浴室主图.jpg': '66ed25f685db7bd1a9523a6a25c501ecb336dead7f957e4cc1ed362a55c2bea4', '追加三图/B清洁/B_红钮细节_清洁版.jpg': '9937a139de6780a133cc011c0e18e6aac1a9c0ced927302728d03125ffd31fe8', '追加三图/C_圆盘厚边.jpg': '84569113e08702560cbd0c44536856d3f449e4e6c8e30e92157cb17442f2b61c', '续作三图/E_按压红钮.jpg': '28b1ceb27083f3d3f046a92c4ec51d6a302308e541817140c569d3f3d456dbde', '续作三图/F_银色背面.jpg': 'c[REDACTED_PHONE]e88e64bc56896c49614f30fabf770918f28ac6fac097768c5ce1'}
for rel,h in preserved.items():assert sha((B/rel).read_bytes())==h,rel+" changed"
records=[]
for title,rel in items:
 p=B/rel
 info=subprocess.check_output(['sips','-g','pixelWidth','-g','pixelHeight',str(p)],text=True)
 w=int(re.search(r'pixelWidth: (\d+)',info).group(1));h=int(re.search(r'pixelHeight: (\d+)',info).group(1))
 assert (w,h)==(1440,1440)
 records.append(dict(title=title,path=rel,width=w,height=h,bytes=p.stat().st_size,sha256=sha(p.read_bytes())))
zipname='圆形花洒_暖白七图_边缘精修_JPG.zip'
with zipfile.ZipFile(B/zipname,'w',compression=zipfile.ZIP_STORED) as z:
 for i,rec in enumerate(records,1):
  n=f'{i:02d}_{Path(rec["path"]).name}';zi=zipfile.ZipInfo(n,date_time=(2026,10,27,19,0,0));zi.external_attr=0o100644<<16;z.writestr(zi,(B/rec['path']).read_bytes());rec['zip_member']=n
with zipfile.ZipFile(B/zipname) as z:
 assert z.testzip() is None
 assert len(z.infolist())==7
 for rec in records:assert sha(z.read(rec['zip_member']))==rec['sha256']
cards=''.join(f'<article><a href="{quote(r["path"])}"><img src="{quote(r["path"])}" alt="{html.escape(r["title"])}"></a><h2>{html.escape(r["title"])}</h2><a download href="{quote(r["path"])}">下载 JPG</a></article>' for r in records)
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>圆形花洒 · 暖白实拍七图</title><style>body{margin:0;background:#f4f0e9;color:#30241b;font:17px system-ui}main{max-width:1400px;margin:auto;padding:28px}h1{font-size:30px}p{line-height:1.7}a{color:#805336}section{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}article{padding:14px;background:white;border-radius:16px}img{width:100%;display:block;border-radius:8px}h2{font-size:22px;margin:14px 0 6px}@media(max-width:700px){section{grid-template-columns:1fr}}</style><main><h1>圆形花洒 · 暖白实拍七图</h1><p>当前七张1440×1440 JPG，本轮仅修正切档细节图和日常手持图。点击图片查看原尺寸。</p>'''+f'<p><a download href="{quote(zipname)}">下载完整七图 JPG 包</a></p><section>'+cards+'''</section><p>本轮修正A柄侧肤色碎片、D手部边缘与金属反射，其余五张保持不变。背面高光仍供审阅。</p></main></html>'''
(B/'七张审阅总览_边缘精修.html').write_text(page)
report=dict(date='2026-10-27',status='A/D边缘精修完成，待用户审阅',count=7,new_count=0,revised_count=2,images=records,approved_image_unchanged=True,zip=dict(path=zipname,bytes=(B/zipname).stat().st_size,sha256=sha((B/zipname).read_bytes()),member_count=7,crc='PASS',member_hashes='PASS'),root_visual_review=['root实际打开A/D原照、用户两批注、两图修改预览及局部前后对照；最终JPG实际打开后执行打包','A产品mask越界带入肤色碎片已修；D手缘及皮肤局部精修、金属反射修饰','其他五张沿用有效审阅记录并核SHA一致'],limits=['A/D/F仅银面局部AI反射编辑；B/C/E商品取实拍','F反射为生成处理，仍需用户确认摄影真实感，不等于完整实物摄影','无水流或人物实验','C是斜正面头部厚边近景，不是完整侧背几何验收'],client_acceptance='UNKNOWN')
(B/'七图交付核验_边缘精修.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'count':7,'revised_count':2,'zip_bytes':(B/zipname).stat().st_size,'crc':'PASS','member_hashes':'PASS','original_unchanged':True},ensure_ascii=False))

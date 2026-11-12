from pathlib import Path
import json,hashlib,zipfile
from PIL import Image
P=Path(__file__).resolve().parent
images=['05_浴室安装全貌_v2.jpg','06_安装喷面与红钮.jpg','07_浴室台面背部接口.jpg']
for n in images:
 im=Image.open(P/n);im.load();assert im.size==(1600,1600)
verification=json.loads((P/'reopened-scene-verification.json').read_text())
assert all(all(v['checks'].values()) for v in verification['views'].values())
assert json.loads((P/'visual-review.json').read_text())['final_images_actually_viewed']==images
files=['README.md','单图任务卡.md','商品基线_v3.blend','商品输入_同网格磨砂去盖接口.blend','05_浴室安装全貌.blend','05_浴室安装全貌_v2.blend','06_安装喷面与红钮.blend','07_浴室台面背部接口.blend','render_bathroom.py','fix_niche.py','verify_bathroom.py','make_review.py','package_outputs.py','geometry-production.json','reopened-scene-verification.json','source-manifest.json','visual-review.json','三张浴室场景总览.jpg','手机宽度审阅.jpg','原照与场景对照_左实拍右渲染.jpg','喷面与红钮原尺寸局部.jpg','render-final.log','niche-fix-final.log','verify.log']
files += [str(f.relative_to(P)) for f in sorted((P/'sources').glob('*.jpg'))]
report={}
for filename,members in [('暖白浴室场景_三张JPG.zip',images),('暖白浴室场景_可编辑源与证据.zip',files)]:
 with zipfile.ZipFile(P/filename,'w',zipfile.ZIP_DEFLATED) as z:
  for name in members:z.write(P/name,name)
 with zipfile.ZipFile(P/filename) as z:
  assert z.testzip() is None
  hashes={name:hashlib.sha256(z.read(name)).hexdigest() for name in members}
  assert all(hashes[name]==hashlib.sha256((P/name).read_bytes()).hexdigest() for name in members)
 report[filename]={'count':len(members),'bytes':(P/filename).stat().st_size,'crc':'PASS','all_member_sha_matches':'PASS','member_sha256':hashes}
(P/'package-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
(P/'artifact-inventory.json').write_text(json.dumps([{'path':str(f.resolve()),'bytes':f.stat().st_size,'purpose':'本轮浴室场景制作、候选、审阅或可编辑交付；旧版保留'} for f in P.rglob('*') if f.is_file()],ensure_ascii=False,indent=2))
print(json.dumps({k:{n:v[n] for n in ['count','bytes','crc','all_member_sha_matches']} for k,v in report.items()},ensure_ascii=False))

from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
import hashlib,zipfile,json,shutil
P=Path(__file__).resolve().parent;root=P.parent.parent
f=P/'upright-advertising.jpg'
if not f.exists():
 candidates=list(P.glob('upright-advertising*0001.jpg'))
 assert len(candidates)==1,candidates
 shutil.copy2(candidates[0],f)
im=Image.open(f);im.load();assert im.size==(1600,1600) and im.format=='JPEG'
im.resize((390,390),Image.Resampling.LANCZOS).save(P/'phone.jpg',quality=95)
im.crop((400,350,1050,1000)).resize((1300,1300)).save(P/'final-200pct.jpg',quality=96)
if (P/'panel-detail-final.jpg').exists():
 source=Image.open(root/'production/2026-10-30_长方形拉钮顶喷_完整建模/372-front-rectified.jpg')
 # Source registration already used by the photo-candidate hole map; approximate scale only.
 source=source.crop((218,242,675,699)).rotate(90,expand=True).resize((800,800))
 source.save(P/'372-approx75mm-field.jpg',quality=97)
 out=Image.new('RGB',(1600,830),'white');d=ImageDraw.Draw(out);d.text((10,8),'372 photo - approx75mm rectified field, not metrology',fill='black');d.text((810,8),'New 3D - 75mm field, final lighting',fill='black');out.paste(source,(0,30));out.paste(Image.open(P/'panel-detail-final.jpg'),(800,30));out.save(P/'source-scale-comparison.jpg',quality=96)
ref=Image.new('RGB',(1600,830),'white');d=ImageDraw.Draw(ref)
for i,n in enumerate([387,399]):
 r=Image.open(next((root/'references/2026-10-31_同款商户电商参考').glob('*_'+str(n)+'_2.jpg')));r.thumbnail((400,800));ref.paste(r,(400*i+(400-r.width)//2,30));d.text((i*400+8,8),str(n)+' reference only',fill='black')
ref.paste(im.resize((800,800)),(800,30));d.text((810,8),'Our silver SKU - no text',fill='black');ref.save(P/'reference-comparison.jpg',quality=95)
if not (P/'visual-review.json').exists():print('Review images prepared');raise SystemExit(0)
names=['upright-advertising.jpg','upright-advertising.blend','advertising.blend','input.blend','长方形拉钮顶喷_v3.blend','baseline_recipe.py','build_scene.py','refine_scene.py','render_detail.py','verify.py','package.py','hole-map.csv','README.md','source-receipt.json','geometry-verification.json','visual-review.json','phone.jpg','final-200pct.jpg','panel-detail-final.jpg','372-native-detail.jpg','382-native-detail.jpg','372-approx75mm-field.jpg','source-scale-comparison.jpg','reference-comparison.jpg']
with zipfile.ZipFile(P/'editable-source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for n in names:z.write(P/n,n)
with zipfile.ZipFile(P/'editable-source.zip') as z:
 assert z.testzip() is None and len(z.namelist())==len(names)
 for n in names:assert hashlib.sha256(z.read(n)).digest()==hashlib.sha256((P/n).read_bytes()).digest()
r={'archive':'editable-source.zip','bytes':(P/'editable-source.zip').stat().st_size,'count':len(names),'CRC_member_SHA256':'PASS','archive_sha256':hashlib.sha256((P/'editable-source.zip').read_bytes()).hexdigest(),'members':[{'file':n,'sha256':hashlib.sha256((P/n).read_bytes()).hexdigest()} for n in names]}
(P/'package-verification.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print({k:v for k,v in r.items() if k!='members'})

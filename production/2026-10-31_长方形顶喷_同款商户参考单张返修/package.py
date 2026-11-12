from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,zipfile
P=Path(__file__).resolve().parent
new=Image.open(P/'01_advertising_refined.jpg');new.load();assert new.size==(1600,1600) and new.format=='JPEG'
old=Image.open(P.parent/'2026-10-31_长方形顶喷_74参考角度配色三图/01_warm_front.jpg')
pair=Image.new('RGB',(1600,830),'white');d=ImageDraw.Draw(pair);d.text((10,8),'PREVIOUS 01 - review only',fill='black');d.text((810,8),'NEW - same camera and mesh',fill='black')
pair.paste(old.resize((800,800),Image.Resampling.LANCZOS),(0,30));pair.paste(new.resize((800,800),Image.Resampling.LANCZOS),(800,30));pair.save(P/'before-after.jpg',quality=95)
new.resize((390,390),Image.Resampling.LANCZOS).save(P/'phone.jpg',quality=95)
new.crop((500,560,1050,1110)).resize((1100,1100)).save(P/'detail-200pct.jpg',quality=96)
source=Image.open(P/'372-detail.jpg');out=Image.new('RGB',(1800,930),'white');d=ImageDraw.Draw(out);d.text((10,8),'SOURCE 372 actual - pixel crop',fill='black');d.text((910,8),'RENDER - detail enlarged, not metrology',fill='black');out.paste(source.resize((900,900)),(0,30));out.paste(new.crop((500,560,1050,1110)).resize((900,900)),(900,30));out.save(P/'source-detail-comparison.jpg',quality=96)
if not (P/'visual-review.json').exists():raise SystemExit('Previews prepared; final review record not yet present, package not emitted.')
names=['01_advertising_refined.jpg','01_advertising_refined.blend','input.blend','商品基线_v3.blend','render.py','verify.py','package.py','README.md','source-receipt.json','reopened-scene-verification.json','visual-review.json','actual-sku-contact.jpg','372-detail.jpg','before-after.jpg','phone.jpg','detail-200pct.jpg','source-detail-comparison.jpg']
with zipfile.ZipFile(P/'editable-source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for n in names:z.write(P/n,n)
with zipfile.ZipFile(P/'editable-source.zip') as z:
 assert z.testzip() is None and len(z.namelist())==len(names)
 for n in names:assert hashlib.sha256(z.read(n)).digest()==hashlib.sha256((P/n).read_bytes()).digest()
report={'archive':'editable-source.zip','bytes':(P/'editable-source.zip').stat().st_size,'count':len(names),'crc_and_member_sha256':'PASS','archive_sha256':hashlib.sha256((P/'editable-source.zip').read_bytes()).hexdigest(),'members':[{'file':n,'sha256':hashlib.sha256((P/n).read_bytes()).hexdigest()} for n in names]}
(P/'package-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print({k:v for k,v in report.items() if k!='members'})

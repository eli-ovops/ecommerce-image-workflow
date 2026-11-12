from pathlib import Path
from PIL import Image,ImageOps
import json,hashlib,zipfile
P=Path(__file__).resolve().parent
names=['01_warm_front','02_blue_side','03_dark_back']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
overview=Image.new('RGB',(1600,534),'white')
phone=Image.new('RGB',(1080,360),'white')
detail=Image.new('RGB',(1200,600),'white')
for i,n in enumerate(names):
 f=P/(n+'.jpg')
 with Image.open(f) as im:
  im.load();assert im.size==(1600,1600) and im.format=='JPEG'
  overview.paste(im.resize((533,533),Image.Resampling.LANCZOS),(533*i,0))
  phone.paste(im.resize((360,360),Image.Resampling.LANCZOS),(360*i,0))
  if i in [0,2]:detail.paste(im.crop((650,650,950,950)).resize((600,600)),(0 if i==0 else 600,0))
overview.save(P/'overview.jpg',quality=95)
phone.save(P/'phone-review.jpg',quality=95)
detail.save(P/'detail-200pct.jpg',quality=95)
files=[P/(n+'.jpg') for n in names]
source=files+[P/(n+'.blend') for n in names]+[P/f for f in ['input.blend','商品基线_v3.blend','render.py','verify.py','package.py','README.md','reference-and-source-receipt.json','reopened-scene-verification.json','visual-review.json','source-contact.jpg','overview.jpg','phone-review.jpg','detail-200pct.jpg']]
manifest=[]
for label,items in [('JPG.zip',files),('editable-source.zip',source)]:
 if not all(f.exists() for f in items):continue
 with zipfile.ZipFile(P/label,'w',zipfile.ZIP_DEFLATED) as z:
  for f in items:z.write(f,f.name)
 with zipfile.ZipFile(P/label) as z:
  assert z.testzip() is None
  assert len(z.namelist())==len(items)
  for f in items:assert hashlib.sha256(z.read(f.name)).hexdigest()==sha(f)
 manifest.append({'file':label,'bytes':(P/label).stat().st_size,'sha256':sha(P/label),'count':len(items),'CRC_and_all_member_SHA256':'PASS','members':[{'file':f.name,'sha256':sha(f)} for f in items]})
(P/'package-verification.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps([{k:v for k,v in row.items() if k!='members'} for row in manifest],ensure_ascii=False))

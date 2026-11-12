from pathlib import Path
from PIL import Image,ImageChops
import json,zipfile,hashlib,io,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent
final=next(f for f in P.glob('391_*.jpg'));im=Image.open(final);im.load();assert im.size==(1200,1200)
with zipfile.ZipFile(P/'391-editable.ora') as z:
 assert z.testzip() is None
 root=ET.fromstring(z.read('stack.xml'));out=Image.new('RGBA',im.size)
 for el in reversed(list(root.find('stack'))):out=Image.alpha_composite(out,Image.open(io.BytesIO(z.read(el.attrib['src']))).convert('RGBA'))
 assert ImageChops.difference(out,Image.open(io.BytesIO(z.read('mergedimage.png'))).convert('RGBA')).getbbox() is None
ET.parse(P/'editable-text.svg');assert all(json.loads((P/'blend-check.json').read_text())['checks'].values())
files=[P/n for n in ['391-installation.blend','single-photo-face.png','model-background.png','installation-layer.png','391-render.png','391-editable.ora','editable-text.svg','editable-base.png','layout.json','water-origins.json','excluded-uncertain-origins.json','photo-method.json','render-record.json','blend-check.json','render-v3.log','README.md','render.py','prepare.py','compose.py','verify_blend.py','water-origin-overlay.jpg','391-head-200pct.jpg','391-mobile.jpg']]+[final]
manifest=[dict(file=f.name,bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in files]
(P/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=True,indent=2));files.append(P/'manifest.json')
with zipfile.ZipFile(P/'391-experiment-source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,f.name)
with zipfile.ZipFile(P/'391-experiment-source.zip') as z:
 assert z.testzip() is None
 for f in files:assert hashlib.sha256(z.read(f.name)).digest()==hashlib.sha256(f.read_bytes()).digest()
(P/'verification.json').write_text(json.dumps(dict(jpg_size=[1200,1200],ora_recomposition=True,ora_crc=True,svg_xml=True,blend_checks=True,zip_crc=True,zip_members_sha=True,zip_members=len(files),zip_bytes=(P/'391-experiment-source.zip').stat().st_size,visual_status='NOT_ACCEPTED_CG_MATERIAL_AND_WATER_CONTACT',browser='NOT_RUN'),indent=2))
print((P/'verification.json').read_text())

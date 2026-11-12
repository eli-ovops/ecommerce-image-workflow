from pathlib import Path
from PIL import Image,ImageChops
import json,zipfile,hashlib,io,shutil,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent;OLD=P.parent/'2026-11-02_顶喷13张逐图新画面';N=P.parent/'2026-11-02_391安装仰视单张实验'
shutil.copy2(N/'391-installation.blend',P/'388-installed-source.blend')
shutil.copy2(N/'391-render.png',P/'installed-native-render.png')
shutil.copy2(N/'water-origins.json',P/'water-origins.json');shutil.copy2(N/'excluded-uncertain-origins.json',P/'excluded-uncertain-origins.json')
ref=next((P.parents[1]/'references').glob('*同款*/'*0)) if False else P.parents[1]/'references/2026-10-31_同款商户电商参考/微信图片_20261031133902_388_2.jpg'
shutil.copy2(ref,P/'reference388.jpg')
# Make composite and inset scripts use packaged local source assets.
s=(P/'compose.py').read_text().replace("OLD/'assets/warm-bath.png'","P/'reused-scene.png'").replace("N/'391-render.png'","P/'installed-native-render.png'").replace("P.parents[1]/'references/2026-10-31_同款商户电商参考/微信图片_20261031133902_388_2.jpg'","P/'reference388.jpg'")
(P/'compose.py').write_text(s)
s=(P/'render_inset.py').read_text().replace("S/'391-installation.blend'","P/'388-installed-source.blend'");(P/'render_inset.py').write_text(s)
assert json.loads((P/'mesh-check.json').read_text())['all4_source_meshes_unchanged']
with zipfile.ZipFile(P/'388-editable.ora') as z:
 assert z.testzip() is None;root=ET.fromstring(z.read('stack.xml'));out=Image.new('RGBA',(1200,1200))
 for el in reversed(list(root.find('stack'))):out=Image.alpha_composite(out,Image.open(io.BytesIO(z.read(el.attrib['src']))).convert('RGBA'))
 assert ImageChops.difference(out,Image.open(io.BytesIO(z.read('mergedimage.png'))).convert('RGBA')).getbbox() is None
ET.parse(P/'editable-text.svg')
old=json.loads((OLD/'verification.json').read_text())['checks'];unchanged=[]
for r in old:
 f=OLD/f'JPG/{r["id"]}.jpg';assert hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'];unchanged.append(r['id'])
final=next(f for f in P.glob('388_*.jpg') if '审阅' in f.name);im=Image.open(final);im.load();assert im.size==(1200,1200)
files=[f for f in P.iterdir() if f.is_file() and f.suffix in ['.jpg','.png','.ora','.svg','.json','.py','.md','.html','.blend','.log'] and f.name not in ['388-revision-v1.jpg','package.py']]
manifest=[dict(file=f.name,bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in files]
(P/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=True,indent=2));files.append(P/'manifest.json')
with zipfile.ZipFile(P/'388-editable-source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,f.name)
with zipfile.ZipFile(P/'388-editable-source.zip') as z:
 assert z.testzip() is None
 for f in files:assert hashlib.sha256(z.read(f.name)).digest()==hashlib.sha256(f.read_bytes()).digest()
r=dict(jpg_size=[1200,1200],ora_crc=True,ora_recomposition=True,svg_xml=True,all4_meshes_unchanged=True,prior_13_jpg_sha_unchanged=unchanged,source_zip_members=len(files),source_zip_bytes=(P/'388-editable-source.zip').stat().st_size,zip_crc=True,zip_member_sha=True,visual_review='Full final, reference comparison, mobile and200percent type/product opened; review candidate only',real_flow_and_hole_acceptance=False,browser_preview='NOT_RUN',svg_render='NOT_VISUALLY_VERIFIED')
(P/'verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))

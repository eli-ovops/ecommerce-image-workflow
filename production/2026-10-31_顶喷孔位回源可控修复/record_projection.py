from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
P=Path(__file__).resolve().parent
base=Image.open(P/'399-preview.jpg');out=base.resize((base.width*4,base.height*4));d=ImageDraw.Draw(out)
colors={'HOLE':'#30ff70','BLIND_DOT':'#ffcf30','OCCLUDED_KNOB':'#ff30cf'}
points=json.loads((P/'399-projection.json').read_text())
for a in points:
 x=a['x_px']*4;y=a['y_px']*4;c=colors[a['kind']];d.ellipse((x-8,y-8,x+8,y+8),outline=c,width=2);d.text((x-20,y+10),a['id'],fill=c)
d.rectangle((0,0,out.width,45),fill='black');d.text((12,10),'GREEN: source-candidate HOLE | GOLD: BLIND_DOT | MAGENTA: OCCLUDED | projection IDs, not factory truth',fill='white')
out.save(P/'399-projection-IDs.jpg',quality=97)
files=[P/'input.blend',P/'hole-map.csv',P/'372-front-rectified.jpg',P/'372_registered_relief.png']
(P/'source-hashes.json').write_text(json.dumps([{'file':str(f.resolve()),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files],indent=2))

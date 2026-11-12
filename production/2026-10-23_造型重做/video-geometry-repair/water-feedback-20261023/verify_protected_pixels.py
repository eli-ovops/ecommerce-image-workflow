from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
w=Path(__file__).resolve().parent
boxes={'D04':{'face_body':(410,0,941,1196),'switch_grip':(300,670,395,966),'lower_grip':(510,1470,880,1670),'text':(0,50,445,345)},'D06':{'text':(0,0,1063,225),'left_mode_key':(0,675,70,785),'lower_grip':(0,1190,400,1320)},'D11':{'upper_person':(410,0,899,867),'lower_person':(0,875,580,1749),'upper_key_grip':(278,266,300,495),'lower_key_grip':(616,1150,672,1385)}}
proof={}
for id,rs in boxes.items():
 a=np.array(Image.open(w/'before-water'/(id+'.png')).convert('RGB'));b=np.array(Image.open(w/(id+'-local')/'composite.png').convert('RGB'));d=np.any(a!=b,2);alpha=np.array(Image.open(w/(id+'-local')/'water-layer.png').getchannel('A'))
 p={'candidate_sha256':hashlib.sha256((w/(id+'-local')/'composite.png').read_bytes()).hexdigest(),'outside_water_alpha_changed_pixels':int((d&(alpha==0)).sum()),'protected_boxes_changed_pixels':{k:int(d[y:Y,x:X].sum()) for k,(x,y,X,Y) in rs.items()},'note':'Exact equality on lossless internal composite. Delivered JPG is lossy encoding.'};proof[id]=p
 assert p['outside_water_alpha_changed_pixels']==0
 assert all(x==0 for x in p['protected_boxes_changed_pixels'].values())
(w/'root-pixel-protection.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2))
print(json.dumps(proof,ensure_ascii=False,indent=2))

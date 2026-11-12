from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json
B=Path(__file__).resolve().parent;ROOT=B.parent;O=B/'v003'
manifest=json.loads((ROOT/'source-manifest.json').read_text());entries={e['id']:e for e in manifest['entries']}
pairs=[('P01','front',(240,20,1090,1705),'FRONT | photo perspective vs orthographic candidate'),('P02','back',(350,300,1085,1735),'BACK | hand occlusion retained'),('P04','left',(555,85,840,1590),'SIDE | cameras not calibrated or pose registered')]
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',22)
for pid,name,box,title in pairs:
 src=ImageOps.exif_transpose(Image.open(entries[pid]['path'])).convert('RGB');src=src.resize((1368,1824))
 source=src.crop(box)
 ren=Image.open(O/'renders'/f'{name}.jpg');render=ren.crop((225,75,775,1125) if name!='left' else (410,75,650,1125))
 canvas=Image.new('RGB',(1000,1200),'#eeeeee');d=ImageDraw.Draw(canvas)
 d.text((20,15),title,font=font,fill='black')
 for im,x,lbl in [(source,30,pid+' real source'),(render,530,'v003 gray clay')]:
  im.thumbnail((440,1030));canvas.paste(im,(x+(440-im.width)//2,90+(1030-im.height)//2));d.text((x,55),lbl,font=font,fill='black')
 d.text((20,1140),'Equal image-height presentation only; no silhouette-fit / accuracy claim.',font=font,fill='black')
 canvas.save(O/f'comparison_{name}.jpg',quality=94)
marks={'coordinate_space':'EXIF-oriented photo resized to1368x1824, manual approximate marks','P01':{'top_y':31,'connector_bottom_y':1695,'head_left_x':270,'head_right_x':1077,'projected_head_width_over_total_length':807/1664},'P02':{'top_y':314,'connector_bottom_y':1730,'head_left_x':374,'head_right_x':1065,'projected_head_width_over_total_length':691/1416},'P04':{'front_plane_points':[[585,120],[645,850]],'lower_front_points':[[650,980],[580,1495]],'estimated_relative_angle_degrees':12.4,'uncertainty':'Approximate manual lines; perspective/occlusion/edge choice; use rough10-15degree range'},'model_v003':{'head_width_over_length':130/265,'upper_front_plane_tilt_deg':5.7106,'lower_front_endpoint_direction_deg':-4.94,'relative_angle_deg':10.65},'conclusion':'Ratios are close at coarse level; cameras not calibrated so no IoU, tolerance pass, metrology or customer acceptance.'}
(O/'photo-proportion-check.json').write_text(json.dumps(marks,indent=2))

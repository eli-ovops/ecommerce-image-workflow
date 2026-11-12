from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math,json,numpy as np
B=Path(__file__).resolve().parent;O=B/'v005';E=O/'evidence';D=json.loads((E/'actual-saved-mesh-profiles.json').read_text());rows=D['v003']['rows'];z=np.array([r['z'] for r in rows]);f=np.array([r['front'] for r in rows]);ft=float(np.interp(260,z,f));fb=float(np.interp(20,z,f));theta=math.atan2(fb-ft,240);c=math.cos(theta);s=math.sin(theta);ppm=1200/310
# Rigidly remove v003 front endpoint chord tilt. No scaling/deformation of old geometry.
def inv(px,py):
 u=17+(px-500)/ppm;v=127.5+(py-600)/ppm;old_y=ft+c*u+s*v;old_z=260-(-s*u+c*v)
 return 500+(old_y+8)*ppm,600-(old_z-132.5)*ppm
p0=inv(0,0);p1=inv(1,0);p2=inv(0,1);a=[p1[0]-p0[0],p2[0]-p0[0],p0[0],p1[1]-p0[1],p2[1]-p0[1],p0[1]]
old=Image.open(B/'v003/renders/left.jpg').transform((1000,1200),Image.Transform.AFFINE,a,Image.Resampling.BICUBIC,fillcolor=(235,235,235))
old.save(E/'v003-rigid-aligned-side.jpg',quality=95)
ims=[Image.open(E/'P04-aligned.jpg'),old,Image.open(O/'renders/left.jpg')];labels=['REAL PHOTO P04','REJECTED v003','CORRECTED v005'];canvas=Image.new('RGB',(1500,1290),'white');dr=ImageDraw.Draw(canvas);font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',25)
for i,(im,label) in enumerate(zip(ims,labels)):
 canvas.paste(im.crop((250,0,750,1200)),(i*500,55));dr.text((i*500+35,15),label,font=font,fill='black')
dr.text((25,1260),'Rigid alignment + identical scale. Uncalibrated side photo; auxiliary shape model.',font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',21),fill='black');canvas.save(O/'real-v003-v005-side-comparison.jpg',quality=95)
p=E/'overlay-transforms-and-comparison.json';d=json.loads(p.read_text());d['three_column_comparison']={'v003_rigid_rotation_degrees':math.degrees(theta),'v003_front_z_endpoints_mm':[20,260],'v003_endpoint_y_mm':[fb,ft],'output_to_original_v003_render_affine':a,'per_column_common_crop':[250,0,750,1200],'pixels_per_mm_all_columns':ppm,'no_nonuniform_scale':True,'v005_geometry_unchanged':True};p.write_text(json.dumps(d,indent=2))

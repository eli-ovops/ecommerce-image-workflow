from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,math,numpy as np
B=Path(__file__).resolve().parent;R=B.parent;O=B/'v005';E=O/'evidence';D=json.loads((B/'v004/evidence/digitized-contours.json').read_text());M=json.loads((E/'actual-saved-mesh-profiles.json').read_text());manifest=json.loads((R/'source-manifest.json').read_text());paths={e['id']:e['path'] for e in manifest['entries']};F=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',22)
ppm=1200/310;W,H=1000,1200;cx,cy=500,600;report={'render_projection':{'width':W,'height':H,'pixels_per_mm':ppm,'camera_target_z_mm':132.5,'side_camera_target_y_mm':17,'type':'orthographic'},'source_transforms':{}}
rows=M['v005']['rows']
for pid in ['P04','P03','P01']:
 src=ImageOps.exif_transpose(Image.open(paths[pid])).convert('RGB').resize((1368,1824))
 if pid=='P01':
  t=D['front_source'];ox,oy=t['origin_xy'];theta=math.radians(t['roll_degrees']);scale=t['uniform_mm_per_pixel'];sign=1;vt=t['top_v'];offset=0;view='front'
 else:
  t=D['side_sources'][pid]['transform'];ox,oy=t['origin_xy'];theta=math.radians(t['roll_angle_degrees']);scale=t['uniform_mm_per_pixel'];sign=t['mirror_u_sign'];vt=t['top_v'];offset=17;view='left'
 c,s=math.cos(theta),math.sin(theta)
 # explicit output pixel -> oriented source pixel affine. Similarity only, reflection for P03.
 def inverse(px,py):
  u=sign*(offset+(px-cx)/ppm)/scale;v=vt+(132.5+(py-cy)/ppm)/scale
  return ox+c*u+s*v,oy-s*u+c*v
 p0=inverse(0,0);p1=inverse(1,0);p2=inverse(0,1);aff=[p1[0]-p0[0],p2[0]-p0[0],p0[0],p1[1]-p0[1],p2[1]-p0[1],p0[1]]
 report['source_transforms'][pid]={'output_to_source_affine':aff,'mirror':sign==-1,'pose_fit':'Only declared roll+uniform total-height scale+translation; no perspective/yaw warp','source_metadata':t}
 aligned=src.transform((W,H),Image.Transform.AFFINE,aff,Image.Resampling.BICUBIC,fillcolor=(245,245,245));aligned.save(E/f'{pid}-aligned.jpg',quality=95)
 if view=='left':
  poly=[(cx+(r['front']-17)*ppm,cy-(r['z']-132.5)*ppm) for r in rows]+[(cx+(r['back']-17)*ppm,cy-(r['z']-132.5)*ppm) for r in reversed(rows)]
 else:
  poly=[(cx-r['halfwidth']*ppm,cy-(r['z']-132.5)*ppm) for r in rows]+[(cx+r['halfwidth']*ppm,cy-(r['z']-132.5)*ppm) for r in reversed(rows)]
 layer=Image.new('RGBA',(W,H));ld=ImageDraw.Draw(layer);ld.polygon(poly,fill=(0,200,240,65));ld.line(poly+[poly[0]],fill=(0,210,240,255),width=3)
 overlay=Image.alpha_composite(aligned.convert('RGBA'),layer).convert('RGB');od=ImageDraw.Draw(overlay);od.rectangle((0,0,1000,55),fill='white');od.text((15,15),pid+' + v005 actual shell projection (cyan, 25% opacity)',font=F,fill='black');overlay.save(E/f'{pid}-model-overlay.jpg',quality=95)
 canvas=Image.new('RGB',(2000,1260),'#eeeeee');canvas.paste(aligned,(0,60));canvas.paste(Image.open(O/'renders'/f'{view}.jpg'),(1000,60));dr=ImageDraw.Draw(canvas);dr.text((20,20),pid+' aligned real photo | uniform scale only',font=F,fill='black');dr.text((1020,20),'v005 same-scale orthographic render',font=F,fill='black');canvas.save(E/f'{pid}-same-scale-pair.jpg',quality=94)
# endpoint-detrended shapes from actual saved mesh. Common z20..260 region avoids caps.
Z=np.arange(20.,260.01,.5);stats={};curves={}
for version,color in [('v003',(210,70,60)),('v005',(20,100,210))]:
 rr=M[version]['rows'];x=np.array([r['z'] for r in rr]);y=np.array([r['front'] for r in rr]);fy=np.interp(Z,x,y);line=np.linspace(fy[0],fy[-1],len(Z));sag=fy-line;pk=int(np.argmax(sag));half=Z[sag>=sag[pk]/2]
 stats[version]={'range_z_mm':[20,260],'maximum_endpoint_detrended_sag_mm':float(sag[pk]),'maximum_over_total265':float(sag[pk]/265),'peak_z_mm':float(Z[pk]),'above_half_max_z_span_mm':[float(half[0]),float(half[-1])],'width_above_half_max_mm':float(half[-1]-half[0]),'limits':'Actual model profile diagnostic; not calibrated photo fit and no PASS'};curves[version]=(sag,color)
canvas=Image.new('RGB',(1300,760),'white');dr=ImageDraw.Draw(canvas);dr.text((35,20),'Actual saved-mesh FRONT curve after subtracting endpoint line',font=F,fill='black');dr.text((35,53),'Common z=20..260mm; model mm are candidate scale, not real metrology',font=F,fill='black')
for z in range(20,261,20):
 x=100+(z-20)/240*1100;dr.line((x,120,x,650),fill='#dddddd');dr.text((x-12,660),str(z),font=F,fill='black')
for val in range(0,21,2):
 y=650-val/20*500;dr.line((100,y,1200,y),fill='#dddddd');dr.text((45,y-10),str(val),font=F,fill='black')
for i,(version,(sag,color)) in enumerate(curves.items()):
 pts=[(100+(z-20)/240*1100,650-v/20*500) for z,v in zip(Z,sag)];dr.line(pts,fill=color,width=4);dr.text((125+i*450,95),version+' '+json.dumps(stats[version]['peak_z_mm'])+'mm peak Z',font=F,fill=color)
dr.text((470,710),'Z from connector toward head top (mm)',font=F,fill='black');canvas.save(E/'v003-v005-detrended-front-curve.jpg',quality=95)
report['endpoint_detrended_model_comparison']=stats
(E/'overlay-transforms-and-comparison.json').write_text(json.dumps(report,indent=2))
print(json.dumps(stats,indent=2))

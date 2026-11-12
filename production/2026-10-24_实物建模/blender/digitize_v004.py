from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import math,json,numpy as np
B=Path(__file__).resolve().parent;ROOT=B.parent;O=B/'v004';E=O/'evidence'
manifest=json.loads((ROOT/'source-manifest.json').read_text());entries={e['id']:e for e in manifest['entries']}
# Manual points read from original EXIF-oriented image, shown at1368x1824 with50px grid.
# tuple(y,x). No segmentation guess is silently promoted to observed contour.
D={
'P04':{'front_side':'image LEFT, same side as front face and lower selector', 'rear_side':'image RIGHT, smooth back shell','sign':1,'baseline':[[585,120],[580,1495]],'top':[585,100],'bottom':[648,1571],
'front':[(120,585),(200,587),(300,596),(400,608),(500,621),(600,634),(700,644),(800,652),(850,655),(1000,653),(1100,639),(1200,621),(1300,603),(1400,583),(1475,576),(1490,579)],
'back':[(120,699),(200,727),(300,755),(400,779),(500,798),(600,812),(700,822),(800,826),(900,826),(1000,818),(1100,805),(1200,785),(1300,766),(1400,747),(1475,734),(1490,728)],'front_occluded_y_ranges':[[850,1000]],'back_occluded_y_ranges':[]},
'P03':{'front_side':'image RIGHT, face and button visible', 'rear_side':'image LEFT, smooth back shell','sign':-1,'baseline':[[780,175],[817,1600]],'top':[780,150],'bottom':[738,1712],
'front':[(175,780),(250,778),(350,767),(450,755),(550,744),(650,735),(750,724),(850,715),(925,710),(1000,711),(1100,721),(1200,737),(1300,756),(1400,777),(1500,798),(1600,817)],
'back':[(175,645),(250,622),(350,593),(450,568),(550,553),(650,546),(750,547),(850,553),(950,561),(1050,571),(1150,581),(1250,597),(1350,613),(1450,635),(1550,658),(1600,669)],'front_occluded_y_ranges':[[900,1150]],'back_occluded_y_ranges':[]}
}
F=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',20)
for pid,d in D.items():
 im=ImageOps.exif_transpose(Image.open(entries[pid]['path'])).convert('RGB').resize((1368,1824));dr=ImageDraw.Draw(im)
 a,b=d['baseline'];dx=b[0]-a[0];dy=b[1]-a[1];ang=math.atan2(dx,dy);c=math.cos(ang);s=math.sin(ang)
 def uv(x,y):return d['sign']*(c*(x-a[0])-s*(y-a[1])),s*(x-a[0])+c*(y-a[1])
 vt=uv(*d['top'])[1];vb=uv(*d['bottom'])[1];scale=265/(vb-vt)
 d['transform']={'origin_xy':a,'roll_angle_degrees':math.degrees(ang),'mirror_u_sign':d['sign'],'uniform_mm_per_pixel':scale,'top_v':vt,'bottom_v':vb,'formula':'u=sign*(cos(theta)*(x-ox)-sin(theta)*(y-oy)); v=sin(theta)*(x-ox)+cos(theta)*(y-oy); modelY=u*scale; modelZ=265-(v-top_v)*scale','no_nonuniform_scale':True}
 d['original_image_coordinate_mapping']={'normalized_size':[1368,1824],'oriented_original_size':[4284,5712],'original_xy_equals_normalized_times':4284/1368}
 d['mapped']={}
 for kind,col in [('front',(255,60,60)),('back',(30,220,255))]:
  rows=[];poly=[]
  for y,x in d[kind]:
   occluded=any(l<=y<=h for l,h in d[kind+'_occluded_y_ranges']);u,v=uv(x,y)
   rows.append({'normalized_pixel_xy':[x,y],'original_oriented_pixel_xy':[x*4284/1368,y*5712/1824],'model_yz_mm':[u*scale,265-(v-vt)*scale],'visibility':'inferred_under_button_or_hand' if occluded else 'visible_manual_edge','pixel_uncertainty':12 if occluded else 5,'used_for_profile':not occluded})
   poly.append((x,y));dr.ellipse((x-4,y-4,x+4,y+4),fill=col);dr.text((x+6,y-12),str(y),font=F,fill=col)
  dr.line(poly,fill=col,width=3);d['mapped'][kind]=rows
 dr.line(d['baseline'],fill=(255,220,0),width=3);dr.text((40,40),pid+' RED front / CYAN rear / YELLOW endpoint baseline',font=F,fill='red')
 im.save(E/f'{pid}-digitized.jpg',quality=96)
 # Profile sag to baseline is actually measured from manual points, not a modeled input assertion.
 pts=[r for r in d['mapped']['front'] if r['used_for_profile']];p=max(pts,key=lambda r:r['model_yz_mm'][0]);d['front_sag']={'maximum_mm_candidate_scale':p['model_yz_mm'][0],'over_total_length':p['model_yz_mm'][0]/265,'z_at_maximum_mm':p['model_yz_mm'][1],'source_pixel':p['normalized_pixel_xy']}
# Use only visible samples; interpolate over documented occlusion with monotone cubic in builder.
# Cross-photo average in common rigid frame; equal weighting, discrepancies retained in report.
def natural_spline(xs,ys,x):
 n=len(xs);h=np.diff(xs);A=np.zeros((n,n));rhs=np.zeros(n);A[0,0]=A[-1,-1]=1
 for i in range(1,n-1):
  A[i,i-1]=h[i-1];A[i,i]=2*(h[i-1]+h[i]);A[i,i+1]=h[i];rhs[i]=6*((ys[i+1]-ys[i])/h[i]-(ys[i]-ys[i-1])/h[i-1])
 M=np.linalg.solve(A,rhs)
 if x<xs[0]:return float(ys[0]+(x-xs[0])*(ys[1]-ys[0])/h[0])
 if x>xs[-1]:return float(ys[-1]+(x-xs[-1])*(ys[-1]-ys[-2])/h[-1])
 i=min(n-2,max(0,int(np.searchsorted(xs,x)-1)));a=(xs[i+1]-x)/h[i];b=(x-xs[i])/h[i]
 return float(a*ys[i]+b*ys[i+1]+((a**3-a)*M[i]+(b**3-b)*M[i+1])*h[i]**2/6)
Z=[9]+list(range(10,266,5))
profiles={'front':[],'back':[]};dis=[]
for z in Z:
 row={'z_mm':z}
 for kind in ['front','back']:
  vals=[]
  for pid,d in D.items():
   pts=sorted((r['model_yz_mm'][1],r['model_yz_mm'][0]) for r in d['mapped'][kind] if r['used_for_profile'])
   zz=np.array([p[0] for p in pts]);yy=np.array([p[1] for p in pts]);val=natural_spline(zz,yy,z);vals.append(val);row[pid+'_'+kind]=val
  avg=sum(vals)/2;profiles[kind].append([z,avg]);row[kind+'_cross_photo_difference_mm']=abs(vals[0]-vals[1])
 dis.append(row)
# Front view independently observed width; preserve uniform similarity transform.
FR=[(35,650,690),(50,530,800),(100,438,894),(150,375,957),(200,331,1000),(250,303,1030),(300,283,1052),(350,271,1066),(400,266,1074),(450,266,1078),(500,272,1075),(550,282,1063),(600,300,1048),(650,325,1028),(700,359,997),(750,399,959),(800,452,903),(850,495,858),(900,531,827),(950,557,805),(1000,576,794),(1050,590,787),(1100,599,784),(1200,610,783),(1300,617,785),(1400,623,789),(1500,627,791),(1600,630,793),(1620,644,778)]
# Axis source center head(670,470) to handle(704,1620). Rotate only; make a symmetric candidate from L/R widths.
a=(670,470);b=(704,1620);ang=math.atan2(b[0]-a[0],b[1]-a[1]);c=math.cos(ang);s=math.sin(ang)
def uv(x,y):return c*(x-a[0])-s*(y-a[1]),s*(x-a[0])+c*(y-a[1])
vt=uv(670,35)[1];vb=uv(704,1695)[1];scale=265/(vb-vt);fw=[];mapped=[]
im=ImageOps.exif_transpose(Image.open(entries['P01']['path'])).convert('RGB').resize((1368,1824));dr=ImageDraw.Draw(im)
for y,l,r in FR:
 ul,vl=uv(l,y);ur,vr=uv(r,y);z=265-((vl+vr)/2-vt)*scale;w=(ur-ul)*scale/2
 fw.append([z,w]);mapped.append({'y':y,'left_x':l,'right_x':r,'model_z_halfwidth_mm':[z,w]});dr.ellipse((l-4,y-4,l+4,y+4),fill=(255,50,50));dr.ellipse((r-4,y-4,r+4,y+4),fill=(20,220,255))
dr.line([(l,y) for y,l,r in FR],fill='red',width=3);dr.line([(r,y) for y,l,r in FR],fill='cyan',width=3)
im.save(E/'P01-digitized-front.jpg',quality=96)
# last row is rounded body cap, not the cylindrical lower shaft; use y1600 width at body end9mm.
fw=sorted(fw[1:-1]);fw=[[9,fw[0][1]]]+fw+[ [265,.05] ]
report={'method':'Manual source-edge digitization with rigid roll and uniform scale only. No calibrated photogrammetry; source projection remains.','side_sources':D,'front_source':{'id':'P01','origin_xy':a,'roll_degrees':math.degrees(ang),'uniform_mm_per_pixel':scale,'top_v':vt,'bottom_v':vb,'samples':mapped,'symmetry_assumption':'average left/right halfwidth after rigid rotation; photo not warped'},'profile_inputs_mm':profiles,'interpolation':'Natural cubic through visible side-edge samples, with linear endpoint continuation. Hidden points retained as annotations but excluded; gap peak is inferred, not observed.', 'cross_photo_station_comparison':dis,'width_profile_z_halfwidth':fw,'limitations':['5px visible-edge uncertainty is a working manual mark estimate, not calibrated statistical error','Button and hand-hidden shell points explicitly excluded from interpolation input','Head and base cap endpoint continuation inferred over short unobserved edge arcs','No IoU or metrology PASS']}
(E/'digitized-contours.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:d['front_sag'] for k,d in D.items()},indent=2))

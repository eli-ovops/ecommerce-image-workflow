import math,json
from mathutils import Vector
from mathutils.kdtree import KDTree
U=1/math.sqrt(1.01);ZTOP=210+65*U;PMIN=210-100*U;PMAX=210+62.5*U
# All dimensions here are model millimetres, not measured engineering values.
def hermite(tab,z,first=None,last=None):
 if z<=tab[0][0]:return tab[0][1]
 if z>=tab[-1][0]:return tab[-1][1]
 for i in range(len(tab)-1):
  a,va=tab[i];b,vb=tab[i+1]
  if a<=z<=b:
   m0=(tab[i+1][1]-tab[max(0,i-1)][1])/(tab[i+1][0]-tab[max(0,i-1)][0]) if i else (first if first is not None else (vb-va)/(b-a))
   m1=(tab[min(len(tab)-1,i+2)][1]-tab[i][1])/(tab[min(len(tab)-1,i+2)][0]-tab[i][0]) if i+1<len(tab)-1 else (last if last is not None else (vb-va)/(b-a))
   t=(z-a)/(b-a);return (2*t**3-3*t*t+1)*va+(t**3-2*t*t+t)*(b-a)*m0+(-2*t**3+3*t*t)*vb+(t**3-t*t)*(b-a)*m1
W_TABLE=[(r['z'],r['half_width']) for r in json.loads((B/'shell-diagnosis.json').read_text())['sections_mm'] if r['z']<=175]
def W(z):
 if z>=175:return math.sqrt(max(0,65**2-((z-210)/U)**2))
 return hermite(W_TABLE,z,last=(210-175)/(U*U*math.sqrt(65**2-((175-210)/U)**2)))
def F_raw(z):
 if z>=155:return 5+(210-z)*.1
 if z>=110:
  t=(z-110)/45;return (2*t**3-3*t*t+1)*7+(t**3-2*t*t+t)*3.6+(-2*t**3+3*t*t)*10.5+(t**3-t*t)*(-4.5)
 return hermite([(10,-1.2875),(25,-2.4816),(50,-.6955),(80,2.4596),(100,4.8873),(110,7)],z,last=.08)
# Quintic Hermite bridges remove curvature jumps at profile segment joins.
def F(z):
 for c in (110,155):
  if c-8<z<c+8:
   a=c-8;b=c+8;h=b-a;t=(z-a)/h;e=.01
   ya=F_raw(a);yb=F_raw(b)
   da=(F_raw(a+e)-F_raw(a-e))/(2*e);db=(F_raw(b+e)-F_raw(b-e))/(2*e)
   aa=(F_raw(a+e)-2*ya+F_raw(a-e))/(e*e);ab=(F_raw(b+e)-2*yb+F_raw(b-e))/(e*e)
   C0=ya;C1=h*da;C2=.5*h*h*aa
   A=yb-C0-C1-C2;D=h*db-C1-2*C2;E=h*h*ab-2*C2
   C3=10*A-4*D+.5*E;C4=-15*A+7*D-E;C5=6*A-3*D+.5*E
   return C0+C1*t+C2*t*t+C3*t**3+C4*t**4+C5*t**5
 return F_raw(z)
def slope(z):return (F(z+.005)-F(z-.005))/.01
def normal(z):return Vector((0,1,-slope(z))).normalized() # inward
X=Vector((1,0,0))
def tangent(z):return Vector((0,slope(z),1)).normalized()
def P(x,z,d=0):return Vector((x,F(z),z))+normal(z)*d
PW=[(-88,15),(-80,18),(-72,22),(-65,27),(-58,33),(-50,41),(-42,47),(-35,math.sqrt(62.5**2-35**2))]
def WP(z):
 v=(z-210)/U
 if v<-100 or v>62.5:return 0
 if v<-88:return 15.9*math.sqrt(max(0,1-((v+82)/18)**2))
 if v<-35:return hermite(PW,v,last=35/math.sqrt(62.5**2-35**2))
 return math.sqrt(max(0,62.5**2-v*v))
# Signed Euclidean distance to explicit panel boundary; seat includes lateral tolerance.
outline=[Vector((WP(PMIN+(PMAX-PMIN)*j/400),0,PMIN+(PMAX-PMIN)*j/400)) for j in range(401)]
outline+= [Vector((-p.x,0,p.z)) for p in reversed(outline[1:-1])]
KD=KDTree(len(outline))
for i,p in enumerate(outline):KD.insert(p,i)
KD.balance()
def margin(x,z):
 pt=Vector((x,0,z));_,idx,_=KD.find(pt);ds=[]
 for a,b in [(outline[(idx-1)%len(outline)],outline[idx]),(outline[idx],outline[(idx+1)%len(outline)])]:
  ab=b-a;t=max(0,min(1,(pt-a).dot(ab)/max(1e-12,ab.length_squared)));ds.append((pt-(a+ab*t)).length)
 d=min(ds);return d if PMIN<z<PMAX and abs(x)<WP(z) else -d
SEAT=3.5;PANEL_THICKNESS=1.1;BACKING_DEPTH=2.5

def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def seat_depth(x,z):return 1.35*smooth((margin(x,z)+.35)/.30)+(SEAT-1.35)*smooth((margin(x,z)-.1)/.4)

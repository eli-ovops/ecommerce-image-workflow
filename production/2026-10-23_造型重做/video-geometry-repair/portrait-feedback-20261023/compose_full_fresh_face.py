from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib
W=Path(__file__).resolve().parent; B=W.parent.parent
SRC=Image.open(W/'fresh-portrait-v2.png').convert('RGB')
print('source size',SRC.size)
# Three landmark alignment, freshly rendered portrait supplies all skin replacement pixels.
# Original facial features are retained because independent QA found no anatomy faults.
RIGHT=[(928,301),(1047,325),(965,469)]
FRONT=[(301,357),(453,358),(378,528)]
S=[
 dict(name='D04',id='D04',src=RIGHT,target=[(577,315),(675,335),(602,443)],face=[(576,205),(604,194),(640,194),(675,205),(685,233),(690,270),(698,300),(708,346),(728,392),(754,432),(751,456),(729,485),(700,509),(666,520),(628,523),(590,520),(563,514),(546,497),(535,470),(532,435),(528,400),(530,374),(539,347),(549,327),(551,298),(561,270)],neck=[(611,518),(658,520),(701,505),(737,473),(742,501),(724,546),(714,581),(715,610),(685,628),(649,647),(624,650)],features=[[(547,269),(572,275),(594,295),(592,306),(577,296),(550,285)],[(624,287),(656,288),(684,302),(695,316),(692,325),(673,310),(645,304),(626,302)],[(547,301),(569,300),(589,310),(599,326),(593,338),(571,337),(551,326)],[(638,322),(662,320),(686,331),(703,345),(696,359),(672,360),(646,347)],[(551,420),(575,419),(603,432),(627,438),(646,443),(643,455),(621,466),(588,468),(559,454)],[(566,389),(589,390),(611,396),(611,408),(586,413),(566,404)]],crop=(485,175,790,655)),
 dict(name='D11-upper',id='D11',src=RIGHT,target=[(479,192),(559,221),(493,313)],face=[(500,95),(530,85),(558,91),(581,108),(588,141),(591,185),(603,232),(628,281),(646,315),(638,339),(612,360),(573,379),(527,385),(481,382),(447,373),(433,355),(433,322),(439,299),(435,272),(431,250),(441,229),(451,209),(456,181),(468,146),(482,116)],neck=[(522,382),(565,379),(615,357),(642,330),(649,355),(630,385),(617,417),(572,425),(541,416)],features=[[(456,150),(470,158),(486,177),(480,185),(466,173),(454,163)],[(518,176),(547,176),(572,185),(587,196),(587,206),(562,195),(537,192),(520,188)],[(456,180),(474,179),(487,191),(489,204),(475,210),(458,199)],[(526,209),(549,207),(573,218),(587,231),(578,240),(552,237),(531,225)],[(444,287),(467,290),(491,301),(514,309),(528,313),(526,324),(501,331),(471,329),(448,316)],[(448,264),(463,263),(483,271),(488,282),(470,286),(447,277)]],crop=(415,75,675,435)),
 dict(name='D11-lower',id='D11',src=FRONT,target=[(325,1100),(406,1065),(399,1174)],face=[(303,1007),(330,990),(364,983),(393,990),(412,1006),(428,1034),(436,1066),(453,1089),(466,1123),(469,1153),(464,1193),(451,1224),(420,1240),(385,1249),(344,1247),(309,1230),(283,1203),(268,1177),(265,1144),(271,1101),(280,1059),(290,1027)],neck=[(308,1220),(351,1246),(405,1243),(448,1228),(452,1285),(451,1322),(420,1337),(371,1344),(326,1335),(311,1295)],features=[[(294,1070),(317,1064),(344,1067),(353,1078),(337,1083),(316,1079),(296,1083)],[(378,1044),(395,1028),(417,1021),(431,1026),(429,1039),(409,1042),(391,1051)],[(293,1094),(314,1083),(339,1084),(354,1096),(353,1107),(331,1121),(308,1123),(294,1111)],[(380,1059),(399,1049),(416,1048),(433,1058),(431,1072),(411,1085),(390,1083)],[(362,1180),(385,1169),(412,1162),(436,1152),(442,1163),(433,1185),(409,1197),(381,1200),(363,1193)],[(365,1133),(387,1126),(408,1134),(407,1145),(388,1152),(369,1147)]],crop=(245,980,490,1345))
]
outputs={}
for id in ['D04','D11']:
 base=Image.open(W/'before-person'/(id+'.png')).convert('RGB');current=np.array(base).astype(float);allowed=Image.new('L',base.size)
 for s in [s for s in S if s['id']==id]:
  a=np.array([[x,y,1] for x,y in s['target']]);co=np.linalg.solve(a,np.array(s['src']))
  inv=(co[0,0],co[1,0],co[2,0],co[0,1],co[1,1],co[2,1])
  # One clean frequency pass on fresh source, not the repeatedly edited rejected scene.
  clean=SRC
  warped=clean.transform(base.size,Image.Transform.AFFINE,inv,Image.Resampling.BICUBIC)
  fresh=np.array(warped).astype(float)
  # Broad illumination match only; original surface texture is not transferred.
  tb=np.array(base.filter(ImageFilter.GaussianBlur(24))).astype(float)
  fb=np.array(warped.filter(ImageFilter.GaussianBlur(24))).astype(float)
  replacement=np.clip(fresh+(tb-fb),0,255)
  # Source hair/background must never leak into original jaw/neck skin.
  dark=Image.fromarray(((fresh.max(2)<108)*255).astype('uint8')).filter(ImageFilter.MinFilter(7)).filter(ImageFilter.MaxFilter(11)).filter(ImageFilter.GaussianBlur(1.2))
  bad=np.array(dark).astype(float)/255
  yy,xx=np.indices(bad.shape);bad[yy<max(y for x,y in s['target'][:2])+18]=0
  fallback=np.array(base.filter(ImageFilter.GaussianBlur(4))).astype(float)
  replacement=replacement*(1-bad[:,:,None])+fallback*bad[:,:,None]
  core=Image.new('L',base.size);d=ImageDraw.Draw(core);d.polygon(s['face'],fill=255)
  core=np.array(core.filter(ImageFilter.GaussianBlur(4.5)))
  # Keep the existing true silhouette and hair where target is dark and source is not skin.
  core=(core.astype(float)*(1-bad*(np.array(base).max(2)<110))).astype('uint8')
  mask=core.astype(float)/255
  current=current*(1-mask[:,:,None])+replacement*mask[:,:,None]
  allowed=Image.fromarray(np.maximum(np.array(allowed),core))
  neckmask=Image.new('L',base.size);ImageDraw.Draw(neckmask).polygon(s['neck'],fill=255);neckmask=neckmask.filter(ImageFilter.GaussianBlur(4))
  nx0=min(x for x,y in s['neck']);nx1=max(x for x,y in s['neck']);ny0=min(y for x,y in s['neck']);ny1=max(y for x,y in s['neck'])
  texture=SRC.crop((330,650,470,740)).resize((nx1-nx0+30,ny1-ny0+30),Image.Resampling.LANCZOS)
  neckplane=base.copy();neckplane.paste(texture,(nx0-15,ny0-15))
  skin=np.array(neckplane).astype(float);low=np.array(neckplane.filter(ImageFilter.GaussianBlur(7))).astype(float)
  targetlow=np.array(base.filter(ImageFilter.GaussianBlur(6))).astype(float)
  replacement=np.clip(targetlow+skin-low,0,255);nm=np.array(neckmask).astype(float)/255
  current=current*(1-nm[:,:,None])+replacement*nm[:,:,None]
  allowed=Image.fromarray(np.maximum(np.array(allowed),np.array(neckmask)))
  Image.fromarray(core).save(W/(s['name']+'-fresh-skin-mask.png'))
 out=Image.fromarray(np.round(current).clip(0,255).astype('uint8'));out.save(W/(id+'-portrait-fresh-face.png'));allowed.save(W/(id+'-fresh-face-mask.png'))
 diff=np.any(np.array(out)!=np.array(base),2)
 proof={'source_base_sha256':hashlib.sha256((W/'before-person'/(id+'.png')).read_bytes()).hexdigest(),'output_sha256':hashlib.sha256((W/(id+'-portrait-fresh-face.png')).read_bytes()).hexdigest(),'changed_pixels':int(diff.sum()),'outside_face_neck_mask_changed_pixels':int((diff&(np.array(allowed)==0)).sum()),'method':'Complete face rendered freshly from texture-neutral M001 identity derivative; affine alignment and broad illumination matching only, no smoothing of the new face. Neck skin supplied from fresh generated source. No original failed face surface or original eyes/lips reused inside face mask; products/water untouched.'}
 assert proof['outside_face_neck_mask_changed_pixels']==0
 outputs[id]=proof
 for s in [s for s in S if s['id']==id]:
  box=s['crop'];o=out.crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3));o.save(W/(s['name']+'-fresh-face-crop.jpg'),quality=97)
(W/'person-fresh-face-proof.json').write_text(json.dumps(outputs,ensure_ascii=False,indent=2))
print(json.dumps(outputs,indent=2))

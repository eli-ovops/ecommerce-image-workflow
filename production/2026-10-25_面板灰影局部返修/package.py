from pathlib import Path
from PIL import Image
import json,shutil,hashlib,zipfile,html
import numpy as np
B=Path(__file__).resolve().parent;old=B.parent/'2026-10-25_广告节奏优化_细节精修';out=B/'JPG';out.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((old/'manifest.json').read_text());a={x['id']:x for x in m['assets']}
for x in m['assets']:
 if x['id']!='L01':shutil.copy2(B/'M02_下方按键操作_候选.jpg' if x['id']=='M02' else old/'JPG'/x['file'],out/x['file'])
parts=[]
for k in m['long_sequence']:
 im=Image.open(out/a[k]['file']).convert('RGB');parts.append(im.resize((1000,round(im.height*1000/im.width)),Image.Resampling.LANCZOS))
long=Image.new('RGB',(1000,sum(im.height for im in parts)),'white');y=0
for im in parts:long.paste(im,(0,y));y+=im.height
long.save(out/a['L01']['file'],quality=95,subsampling=0)
for x in m['assets']:
 x['source']=str(old/'JPG'/x['file']);x['changed']=x['id'] in ['M02','L01'];x['sha256']=sha(out/x['file']);x['size']=list(Image.open(out/x['file']).size)
a['M02']['notes']='局部无孔纹理修复7处灰环/拖影；未补造喷嘴；保留原白嘴、外圈黑孔、手、标题和下键。仍为既有生成操作示意。'
a['L01']['notes']='原13章次序不变，仅同步M02面板局部修复。'
m.update(baseline=str(old),previous_version=str(old),revision='M02面板7处灰环局部修复；L01同步；16张其他JPG字节不变',visual_review='实际打开原尺寸M02及左右/底边3倍对照，灰环去除、未带入新白色月牙；真实外环黑孔保留。',long_size=list(long.size))
(B/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
name='鼎江10.25面板局部返修_JPG_18张.zip';zpath=B/name
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
 for x in m['assets']:z.write(out/x['file'],x['file'])
with zipfile.ZipFile(zpath) as z:
 assert z.testzip() is None
 assert len(z.namelist())==18
 for x in m['assets']:assert hashlib.sha256(z.read(x['file'])).hexdigest()==x['sha256']
unchanged=[x['id'] for x in m['assets'] if sha(old/'JPG'/x['file'])==x['sha256']];assert len(unchanged)==16
orig=np.array(Image.open(old/'JPG'/a['M02']['file']).convert('RGB'));work=np.array(Image.open(B/'review/working-lossless.png'));delta=np.any(orig!=work,axis=2);patches=json.loads((B/'patches.json').read_text())['patches'];allowed=np.zeros(delta.shape,bool)
for x,y,rx,ry,_,_ in patches:allowed[y-ry-4:y+ry+5,x-rx-4:x+rx+5]=True
assert not delta[~allowed].any()
rec={'zip':name,'sha256':sha(zpath),'count':18,'crc':'PASS','sha_readback':'18/18','unchanged_images':unchanged,'changed':['M02','L01'],'lossless_changed_pixels':int(delta.sum()),'lossless_outside_patch_bounds_changed':0,'note':'JPG re-encoding can alter pixels outside repaired patches; lossless working source is exact outside masks. Customer acceptance pending.'}
(B/'package-check.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
(B/'README.md').write_text('# 面板局部返修\n\n仅修M02内面板边缘7处灰环/拖影，同步L01；其余16图字节复用，18张JPG。\n\n保留白色喷嘴、外圈真实黑孔、原手部、下键、文字与背景。局部无孔面板纹理取样，不增补喷嘴，不全图重绘。候选曾因取样带入白嘴边缘而废弃，最终已改用无孔取样区。\n\n本次是局部伪影修复，不代表生成面板全局孔数、排列或商品几何已与实物完全吻合；客户整套接受待审。\n')
cards=''.join(f'<section><h2>{html.escape(x["id"]+" · "+x["name"])}</h2><a href="JPG/{x["file"]}"><img src="JPG/{x["file"]}"></a></section>' for x in m['assets'])
(B/'交付总览.html').write_text('<!doctype html><meta charset="utf-8"><title>面板局部返修</title><style>body{background:#f3f1ed;font-family:sans-serif;margin:40px}main{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}section{background:white;padding:16px}img{width:100%;height:auto}h2{font-size:18px}</style><h1>面板局部返修 · 18张JPG</h1><p><a href="'+name+'">下载JPG压缩包</a></p><main>'+cards+'</main>')
print(json.dumps(rec,ensure_ascii=False,indent=2))

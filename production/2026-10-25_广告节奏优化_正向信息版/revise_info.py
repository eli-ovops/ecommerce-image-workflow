from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import shutil,json,hashlib
R=Path('/Volumes/EXTERNAL/电商 作图工作流/production');old=R/'2026-10-25_广告节奏优化';b=R/'2026-10-25_广告节奏优化_正向信息版';out=b/'JPG';out.mkdir(parents=True,exist_ok=True)
m=json.loads((old/'manifest.json').read_text())
for a in m['assets']:shutil.copy2(old/'JPG'/a['file'],out/a['file'])
# Rebuild the native information panel only; omit the entire sale-scope row.
N=1254;F='/System/Library/Fonts/STHeiti Medium.ttc';im=Image.new('RGB',(N,1340),'#f7f0e5');d=ImageDraw.Draw(im)
def txt(x,y,s,t,c='#211a17'):d.text((x,y),t,font=ImageFont.truetype(F,s),fill=c,anchor='lt')
p=Image.new('RGBA',(1200,170));q=ImageDraw.Draw(p);q.text((20,8),'选购信息',font=ImageFont.truetype(F,135),fill='#211a17',anchor='lt',stroke_width=3);p=p.transform(p.size,Image.Transform.AFFINE,(1,.10,-10,0,1,0),Image.Resampling.BICUBIC);im.paste(p,(39,55),p);txt(65,245,56,'手持花洒','#835336')
for i,(a,v) in enumerate([('颜色','银色 / 黑色 / 枪灰色'),('三档出水','普通 / 喷雾 / 混合'),('下方按键','切换出水档位'),('中央红钮','手动按压辅助除垢')]):
 y=420+i*210;d.rectangle((55,y-20,N-55,y+155),fill='#ede1d0' if i%2==0 else '#f7f0e5');txt(85,y+15,53,a,'#835336');txt(85,y+87,53,v)
a=next(a for a in m['assets'] if a['id']=='D05');im.save(out/a['file'],quality=95,subsampling=0);a.update(size=list(im.size),sha256=hashlib.sha256((out/a['file']).read_bytes()).hexdigest(),notes='按用户最新纠正删除售卖范围及未包含说明；仅保留颜色、三档、切档与除垢正向信息')
parts=[]
for id in m['long_sequence']:
 a=next(a for a in m['assets'] if a['id']==id);p=Image.open(out/a['file']);parts.append(p.resize((1000,round(p.height*1000/p.width)),Image.Resampling.LANCZOS))
p=Image.new('RGB',(1000,sum(p.height for p in parts)));y=0
for t in parts:p.paste(t,(0,y));y+=t.height
a=next(a for a in m['assets'] if a['id']=='L01');p.save(out/a['file'],quality=95,subsampling=0);a.update(size=list(p.size),sha256=hashlib.sha256((out/a['file']).read_bytes()).hexdigest());m['long_size']=list(p.size);m['revision']='仅修改D05和L01；其余16张原字节复用，删除未包含项说明';m['previous_version']=str(old)
(b/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
s=(old/'package.py').read_text().replace('14888',str(p.height)).replace('广告节奏优化_JPG_18张.zip','广告节奏优化_正向信息版_JPG_18张.zip').replace('17张独立图 + 1条1000×'+str(p.height)+'详情。','17张独立图 + 1条1000×'+str(p.height)+'详情。本次仅删除D05的售卖范围与未包含说明并重组长图，其余16图哈希不变。').replace('必要选购信息集中为大字表；未知材质尺寸未写；不加脚注。','仅保留正向商品信息；删除售卖范围及未包含配件说明。')
(b/'package.py').write_text(s)
print(str(b),p.size)

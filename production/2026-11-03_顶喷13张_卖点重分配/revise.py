# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageChops
import json, shutil, hashlib, zipfile, io, math, xml.etree.ElementTree as ET

P=Path(__file__).resolve().parent
OLD=P.parent/'2026-11-02_新Skill_13张完整审阅集'
FONT='/System/Library/Fonts/STHeiti Medium.ttc'
for d in ['JPG','editable','review','provenance']:(P/d).mkdir(exist_ok=True)
# Native typography only. All coordinates refer to the accepted raster, not new AI inputs.
# Each spec: rectangle, lines, foreground, top/bottom plate colors, maximum font size, italic.
S={
387:[([36,195,425,265],['宽幅大面板'],'gold','#181817','#29241b',57,True),([35,314,425,390],['充沛大水量'],'gold','#171716','#29241b',57,True)],
388:[([224,487,1075,707],['丰沛雨幕'],'white','#a60010','#7d0812',170,True)],
389:[([845,79,1239,650],['宽幅','雨幕','畅淋'],'black','#cfdaec','#c1d1e7',158,True)],
390:[([482,963,1206,1035],['充沛出水  畅爽雨淋'],'gold','#07312d','#092a28',57,True)],
393:[([44,34,1006,158],['空气增压  绵密雨幕'],'gold','#342b23','#25211d',89,True),([59,168,569,228],['细密喷面  连接便捷'],'gold','#372e25','#2a251f',42,True)],
396:[([38,199,323,263],['细密喷面'],'gold','#332d24','#201d19',43,False),([39,638,327,702],['加厚外壳'],'gold','#332d24','#201d19',43,False),([40,1060,399,1124],['宽幅大面板'],'gold','#332d24','#201d19',43,False)],
397:[([49,57,903,298],['空气增压','畅享绵密雨幕'],'gold','#3c3027','#2d251f',105,True)],
398:[([48,135,803,327],['角度随需调','淋浴更自在'],'gold','#332c25','#27231e',77,True)],
399:[([51,127,839,228],['宽幅大面板  畅享淋浴'],'gold','#22201e','#30271f',66,True),([66,264,517,329],['充沛出水  舒展沐浴'],'gold','#242321','#2e2922',40,True)]}
def dump(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def gradient(size,a,b):
    out=Image.new('RGBA',size);d=ImageDraw.Draw(out)
    from PIL import ImageColor
    ca=ImageColor.getrgb(a);cb=ImageColor.getrgb(b)
    for y in range(size[1]):
        t=y/max(1,size[1]-1);d.line((0,y,size[0],y),fill=tuple(round(x*(1-t)+z*t) for x,z in zip(ca,cb))+(255,))
    return out
def letter(text,maxw,maxh,size,color,italic):
    while True:
        f=ImageFont.truetype(FONT,size);b=f.getbbox(text,stroke_width=1)
        mask=Image.new('L',(b[2]-b[0]+12,b[3]-b[1]+12));ImageDraw.Draw(mask).text((6-b[0],6-b[1]),text,font=f,fill=255,stroke_width=1)
        if italic:
            shift=round(mask.height*.19)
            mask=mask.transform((mask.width+shift,mask.height),Image.Transform.AFFINE,(1,.19,-shift,0,1,0),Image.Resampling.BICUBIC)
        if mask.width<=maxw and mask.height<=maxh:break
        size-=1
        assert size>12
    c={'gold':('#fff0b3','#e8b45b'),'white':('#ffffff','#fff5e8'),'black':('#080b13','#142039')}[color]
    im=gradient(mask.size,*c);im.putalpha(mask);return im,size
def ora(path,layers,out):
    root=ET.Element('image',w=str(out.width),h=str(out.height));stack=ET.SubElement(root,'stack')
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('mimetype','image/openraster',compress_type=zipfile.ZIP_STORED)
        for i,(name,im) in enumerate(reversed(layers)):
            b=io.BytesIO();im.save(b,format='PNG');src=f'data/{i}.png';z.writestr(src,b.getvalue());ET.SubElement(stack,'layer',name=name,src=src,x='0',y='0',opacity='1',visibility='visible',**{'composite-op':'svg:src-over'})
        z.writestr('stack.xml',ET.tostring(root));b=io.BytesIO();out.save(b,format='PNG');z.writestr('mergedimage.png',b.getvalue())
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        r=ET.fromstring(z.read('stack.xml'));a=Image.new('RGBA',out.size)
        for e in reversed(list(r.find('stack'))):a.alpha_composite(Image.open(io.BytesIO(z.read(e.attrib['src']))).convert('RGBA'))
        assert ImageChops.difference(a,out).convert('RGB').getbbox() is None

records=[]
for n in range(387,400):
    src=OLD/'JPG'/f'{n}.jpg';base=Image.open(src).convert('RGBA');out=base.copy();layers=[('Accepted prior raster - flattened image and old text',base)];mask=Image.new('L',base.size);specs=[]
    for box,lines,fg,c1,c2,fs,it in S.get(n,[]):
        x,y,x2,y2=box;w=x2-x;h=y2-y
        plate=gradient((w,h),c1,c2)
        # Existing visual hierarchy retained; thin accent lines make the cover a deliberate title plate.
        dp=ImageDraw.Draw(plate)
        if n not in [387,390,396]:dp.line((0,h-2,w,h-2),fill='#d8b879' if fg=='gold' else '#b80919' if fg=='white' else '#687f9f',width=2)
        lay=Image.new('RGBA',base.size);lay.alpha_composite(plate,(x,y));layers.append(('Editable title plate',lay));out.alpha_composite(lay);ImageDraw.Draw(mask).rectangle((x,y,x2-1,y2-1),fill=255)
        textlayer=Image.new('RGBA',base.size);sizes=[]
        for k,t in enumerate(lines):
            lh=h//len(lines);im,s=letter(t,w-24,lh-14,fs,fg,it);sizes.append(s);tx=x+(w-im.width)//2;ty=y+k*lh+(lh-im.height)//2;textlayer.alpha_composite(im,(tx,ty))
        layers.append(('New typesetting: '+ ' / '.join(lines),textlayer));out.alpha_composite(textlayer);specs.append(dict(box=box,text=lines,font=FONT,font_sizes=sizes,italic=it))
    if n==398:
        # Short two-headed arc is a direction cue, not a numeric range or 360-degree claim.
        lay=Image.new('RGBA',base.size);d=ImageDraw.Draw(lay);pts=[]
        for i in range(41):
            a=math.radians(-55+i*110/40);pts.append((829+45*math.cos(a),636+90*math.sin(a)))
        d.line(pts,fill='#f2cc80',width=6)
        for idx,nxt in [(0,1),(-1,-2)]:
            x,y=pts[idx];xx,yy=pts[nxt];a=math.atan2(y-yy,x-xx);d.polygon([(x,y),(x-20*math.cos(a-.55),y-20*math.sin(a-.55)),(x-20*math.cos(a+.55),y-20*math.sin(a+.55))],fill='#f2cc80')
        layers.append(('Editable angle direction arrow, no numeric range',lay));out.alpha_composite(lay);mask=ImageChops.lighter(mask,lay.getchannel('A'));specs.append(dict(vector='short two-headed angle arc; no numeric range'))
    if n in S:
        folder=P/'editable'/str(n);folder.mkdir(exist_ok=True);out.save(folder/'merged.png');mask.save(folder/'changed-area.png');dump(folder/'typography.json',specs);ora(folder/'layers.ora',layers,out)
        diff=ImageChops.difference(base,out).convert('RGB');outside=ImageChops.multiply(diff,ImageOps.invert(mask).convert('RGB'));assert outside.getbbox() is None
        out.convert('RGB').save(P/'JPG'/f'{n}.jpg',quality=97,subsampling=0)
    else:shutil.copy2(src,P/'JPG'/f'{n}.jpg')
    final=Image.open(P/'JPG'/f'{n}.jpg');final.load();assert final.size==base.size
    records.append(dict(id=n,changed=n in S,old_sha256=sha(src),new_sha256=sha(P/'JPG'/f'{n}.jpg'),size=list(base.size),specs=specs,lossless_outside_edit_mask_unchanged=True if n in S else None,unchanged_file_identical=sha(src)==sha(P/'JPG'/f'{n}.jpg') if n not in S else None,ora_recomposition=True if n in S else None))
    oldthumb=ImageOps.contain(base.convert('RGB'),(600,900));newthumb=ImageOps.contain(final,(600,900));pair=Image.new('RGB',(oldthumb.width+newthumb.width,max(oldthumb.height,newthumb.height)),'#eee');pair.paste(oldthumb);pair.paste(newthumb,(oldthumb.width,0));pair.save(P/'review'/f'{n}-before-after.jpg',quality=95)
    ImageOps.contain(final,(360,640)).save(P/'review'/f'{n}-mobile.jpg',quality=95)
for group,ids,w,h,cols in [('square',range(387,394),400,400,4),('portrait',range(394,400),350,623,3)]:
    sheet=Image.new('RGB',(w*cols,(h+30)*2),'#ddd');d=ImageDraw.Draw(sheet)
    for i,n in enumerate(ids):
        im=ImageOps.contain(Image.open(P/'JPG'/f'{n}.jpg'),(w,h));x=i%cols*w;y=i//cols*(h+30);d.text((x+8,y+6),str(n),fill='black');sheet.paste(im,(x+(w-im.width)//2,y+30))
    sheet.save(P/'review'/f'contact-{group}.jpg',quality=96)
dump(P/'revision-manifest.json',records)
for name in ['generation-receipts.json','input-manifest.json','quality-review.json']:
    shutil.copy2(OLD/name,P/'provenance'/('previous-'+name))
print(json.dumps(dict(changed=[r['id'] for r in records if r['changed']],unchanged=[r['id'] for r in records if not r['changed']],checks='decode, dimensions, unchanged-byte copies, native outside-mask preservation, ORA CRC and recomposition passed')))

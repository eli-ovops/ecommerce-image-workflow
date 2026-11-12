# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageChops
import json,hashlib,shutil,zipfile,io,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent;ROOT=P.parents[1];OLD=P.parent/'2026-11-02_新Skill_13张完整审阅集'
for d in ['JPG','review','editable','sources','provenance']:(P/d).mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
changed=[387,388,389,390,393,396,397,398,399];unchanged=[391,392,394,395]
photo=ROOT/'production/2026-10-30_长方形拉钮顶喷_完整建模/382-native-detail.jpg';shutil.copy2(photo,P/'sources/short-pin-real.jpg')
checks=[]
for n in range(387,400):
    dst=P/'JPG'/f'{n}.jpg'
    if n in unchanged:shutil.copy2(OLD/'JPG'/f'{n}.jpg',dst);assert sha(dst)==sha(OLD/'JPG'/f'{n}.jpg')
    else:
        base=Image.open(P/'native'/f'{n}.png').convert('RGBA');out=base.copy()
        if n==396:
            box=(495,1185,905,1595);layer=Image.new('RGBA',base.size);tile=ImageOps.fit(Image.open(photo).convert('RGB'),(410,410),method=Image.Resampling.LANCZOS).convert('RGBA');mask=Image.new('L',(410,410));ImageDraw.Draw(mask).rounded_rectangle((0,0,409,409),radius=15,fill=255);tile.putalpha(mask);layer.alpha_composite(tile,(box[0],box[1]));out.alpha_composite(layer)
            folder=P/'editable'/'396';folder.mkdir(exist_ok=True);base.save(folder/'generated-base.png');layer.save(folder/'real-photo-layer.png');out.save(folder/'merged.png')
            root=ET.Element('image',w=str(out.width),h=str(out.height));stack=ET.SubElement(root,'stack')
            with zipfile.ZipFile(folder/'layers.ora','w',zipfile.ZIP_DEFLATED) as z:
                z.writestr('mimetype','image/openraster',compress_type=zipfile.ZIP_STORED)
                for i,(name,im) in enumerate([('Real short-pin photo',layer),('Generated flattened base',base)]):
                    b=io.BytesIO();im.save(b,format='PNG');src=f'data/{i}.png';z.writestr(src,b.getvalue());ET.SubElement(stack,'layer',name=name,src=src,x='0',y='0',opacity='1',visibility='visible',**{'composite-op':'svg:src-over'})
                z.writestr('stack.xml',ET.tostring(root));b=io.BytesIO();out.save(b,format='PNG');z.writestr('mergedimage.png',b.getvalue())
            with zipfile.ZipFile(folder/'layers.ora') as z:
                assert z.testzip() is None;test=Image.new('RGBA',out.size)
                for node in reversed(list(ET.fromstring(z.read('stack.xml')).find('stack'))):test.alpha_composite(Image.open(io.BytesIO(z.read(node.attrib['src']))).convert('RGBA'))
                assert ImageChops.difference(test,out).convert('RGB').getbbox() is None
            diff=ImageChops.difference(base,out).convert('RGB');assert ImageChops.multiply(diff,ImageOps.invert(layer.getchannel('A')).convert('RGB')).getbbox() is None
            dump('photo-composite.json',dict(id=396,source=str(photo),source_sha256=sha(photo),box=box,method='uniform fit crop into deliberately empty window; no AI input or text covering',ora_crc=True,ora_recomposition=True,lossless_pixels_outside_photo_unchanged=True))
        out.convert('RGB').save(dst,quality=97,subsampling=0)
    im=Image.open(dst);im.load();checks.append(dict(id=n,changed=n in changed,size=list(im.size),sha256=sha(dst),decode=True,original_file_identical=n in unchanged and sha(dst)==sha(OLD/'JPG'/f'{n}.jpg')))
    ImageOps.contain(im,(360,640)).save(P/'review'/f'{n}-mobile.jpg',quality=95)
    if n in changed:
        old=ImageOps.contain(Image.open(OLD/'JPG'/f'{n}.jpg'),(600,850));new=ImageOps.contain(im,(600,850));pair=Image.new('RGB',(old.width+new.width,max(old.height,new.height)),'#eee');pair.paste(old);pair.paste(new,(old.width,0));pair.save(P/'review'/f'{n}-old-left-new-right.jpg',quality=95)
        ref=ImageOps.contain(Image.open(ROOT/f'references/2026-10-31_同款商户电商参考/微信图片_20261031133902_{n}_2.jpg'),(600,850));pair=Image.new('RGB',(ref.width+new.width,max(ref.height,new.height)),'#eee');pair.paste(ref);pair.paste(new,(ref.width,0));pair.save(P/'review'/f'{n}-reference-left-new-right.jpg',quality=95)
boxes={387:(.38,.24,.74,.70),388:(.05,.61,.46,.92),389:(.065,.55,.30,.94),390:(.08,.56,.32,.92),393:(.32,.27,.70,.40),396:(.05,.19,.44,.38),397:(.25,.35,.67,.44),398:(.35,.35,.82,.42),399:(.29,.41,.76,.74)}
for n,b in boxes.items():
    im=Image.open(P/'JPG'/f'{n}.jpg');box=tuple(round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(b));crop=im.crop(box);crop.resize((crop.width*2,crop.height*2),Image.Resampling.NEAREST).save(P/'review'/f'{n}-face-200pct.jpg',quality=97)
for group,ids,w,h,cols in [('square',range(387,394),400,400,4),('portrait',range(394,400),350,623,3)]:
    sheet=Image.new('RGB',(w*cols,(h+30)*2),'#ddd');d=ImageDraw.Draw(sheet)
    for i,n in enumerate(ids):
        im=ImageOps.contain(Image.open(P/'JPG'/f'{n}.jpg'),(w,h));x=i%cols*w;y=i//cols*(h+30);d.text((x+7,y+8),str(n),fill='black');sheet.paste(im,(x+(w-im.width)//2,y+30))
    sheet.save(P/'review'/f'contact-{group}.jpg',quality=96)
for name in ['quality-review.json','input-manifest.json','generation-receipts.json']:shutil.copy2(OLD/name,P/'provenance'/('previous-'+name))
dump('export-verification.json',checks);print(json.dumps(checks))

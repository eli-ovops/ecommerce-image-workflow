from pathlib import Path
from PIL import Image,ImageDraw,ImageOps,ImageFilter,ImageFont
import json,shutil
ROOT=Path(__file__).resolve().parent;P=ROOT/'lighting-refine';R=ROOT.parents[1]
im=Image.open(R/'production/2026-11-03_\u9876\u55b713\u5f20_\u5c3a\u5bf8\u5355\u5217\u4e0e\u5356\u70b9\u4fee\u8ba2/editable/396/merged.png').convert('RGBA')
layer=Image.new('RGBA',im.size)
photo=Image.open(R/'production/2026-10-31_\u9876\u55b7\u5b54\u4f4d\u56de\u6e90\u53ef\u63a7\u4fee\u590d/372-front-rectified.jpg').convert('RGBA')
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',44)
specs=[((24,232,463,658),(180,140,780,740),'\u9762\u677f\u7eb9\u6837'),((480,232,916,658),(600,240,1200,900),'\u4e2d\u592e\u7ea2\u94ae'),((25,1094,461,1609),None,'\u5bbd\u5e45\u5927\u9762\u677f')]
for box,crop,label in specs:
 size=(box[2]-box[0],box[3]-box[1])
 if crop:patch=ImageOps.fit(photo.crop(crop),size)
 else:
  bg=Image.open(R/'production/2026-11-03_\u9876\u55b7\u4e24\u5f20\u7ec6\u8282\u56de\u6e90\u4fee\u8ba2/backgrounds/399.png').convert('RGBA')
  patch=ImageOps.fit(bg,size)
  body=Image.open(P/'native/product.png').convert('RGBA');body=body.crop(body.getchannel('A').getbbox()).rotate(90,expand=True);body.thumbnail((415,300),Image.Resampling.LANCZOS)
  xy=((size[0]-body.width)//2,160)
  sh=Image.new('RGBA',size);a=Image.new('L',size);a.paste(body.getchannel('A'),(xy[0]+4,xy[1]+7));sh.putalpha(a.filter(ImageFilter.GaussianBlur(5)).point(lambda x:round(x*.5)));patch.alpha_composite(sh);patch.alpha_composite(body,xy)
 gradient=Image.new('RGBA',size);gd=ImageDraw.Draw(gradient)
 for y in range(160):gd.line((0,y,size[0],y),fill=(12,9,6,round(220*(1-y/160)**1.5)))
 patch.alpha_composite(gradient)
 title=Image.new('RGBA',(380,70));td=ImageDraw.Draw(title);td.text((9,2),label,font=font,fill='#ffdf98',stroke_width=1)
 title=title.transform(title.size,Image.Transform.AFFINE,(1,.14,-9,0,1,0),Image.Resampling.BICUBIC)
 sh=Image.new('RGBA',title.size);sh.putalpha(title.getchannel('A'));patch.alpha_composite(sh,(26,17));patch.alpha_composite(title,(24,15))
 mask=Image.new('L',size);ImageDraw.Draw(mask).rounded_rectangle((0,0,size[0]-1,size[1]-1),20,fill=255);patch.putalpha(mask);layer.alpha_composite(patch,box[:2])
out=Image.alpha_composite(im,layer);D=P/'editable/396';D.mkdir(parents=True,exist_ok=True)
im.save(D/'original-base.png');layer.save(D/'source-correction-layer.png');out.save(D/'merged.png')
out.convert('RGB').save(P/'candidates/396.jpg',quality=97,subsampling=0)
preview=out.convert('RGB');preview.thumbnail((470,900));preview.save(P/'review/396-phone.jpg',quality=95)
(P/'396-changes.json').write_text(json.dumps({'modified_windows':['face-pattern','reset-knob','full-reset-product'],'preserved':['main-title','silver-side','connector-opening','real382-short-pins'],'labels':'Same wording, rebuilt independent text in three corrected windows','photo_source':'Original372 rectified photograph','pin_state':'No added red pins; reset views only','boxes':[list(x[0]) for x in specs]},indent=2))

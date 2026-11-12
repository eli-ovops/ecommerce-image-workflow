"""Zero-generation-cost, photo-layer motion storyboard; not an AI-video result."""
from pathlib import Path
import math, subprocess, json
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageEnhance,ImageOps
B=Path(__file__).resolve().parent.parent;R=B/'预览/酷炫开场动态分镜';R.mkdir(exist_ok=True)
ROOT=B.parents[2]
src=ROOT/'products/主推花洒/银色/原图/微信图片_20261022184342_89_2.jpg'
im=ImageOps.exif_transpose(Image.open(src)).convert('RGB').resize((720,960),Image.Resampling.LANCZOS)
mask=Image.new('L',im.size);d=ImageDraw.Draw(mask)
d.ellipse((218,122,584,498),fill=255)
d.polygon([(290,449),(511,448),(472,489),(452,537),(438,577),(432,849),(354,849),(350,578),(338,539),(322,502)],fill=255)
mask=mask.filter(ImageFilter.GaussianBlur(.6));asset=im.convert('RGBA');asset.putalpha(mask);asset=asset.crop((214,120,588,852));asset.save(R/'商品照片分层.png')
font='/System/Library/Fonts/STHeiti Light.ttc';F=lambda n:ImageFont.truetype(font,n)
def ease(v):
 v=max(0,min(1,v));return v*v*(3-2*v)
def layer(bg,size,angle,center,brightness=1,alpha=1):
 a=asset.resize((max(2,int(asset.width*size)),max(2,int(asset.height*size))),Image.Resampling.BICUBIC)
 if brightness!=1:
  rgb=ImageEnhance.Brightness(a.convert('RGB')).enhance(brightness);rgb.putalpha(a.getchannel('A'));a=rgb
 if alpha<1:a.putalpha(a.getchannel('A').point(lambda v:int(v*alpha)))
 a=a.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
 bg.alpha_composite(a,(int(center[0]-a.width/2),int(center[1]-a.height/2)))
def centered(draw,y,text,font,fill):
 box=draw.textbbox((0,0),text,font=font);draw.text(((720-(box[2]-box[0]))/2,y),text,font=font,fill=fill)
out=R/'开场4秒-动态分镜.mp4'
cmd=['ffmpeg','-hide_banner','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size','720x1280','-framerate','30','-i','-','-an','-c:v','libx264','-crf','19','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart','-y',str(out)]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
macro=Image.open(B/'预览/素材可用性审查/05-crop0.jpg').convert('RGB')
macro=ImageOps.fit(macro,(720,1280))
for n in range(120):
 t=n/30;bg=Image.new('RGBA',(720,1280),(5,8,14,255))
 if t<2.3:
  a=ease(t/1.0);move=ease((t-.25)/1.15)
  layer(bg,.80,160+12*(1-move),(600-95*move,115+100*move),.12+.88*a)
  layer(bg,.80,-22-12*(1-move),(105+70*move,1175-125*move),.12+.88*a)
  # A brief moving light strip is an editorial cue, not a simulated product function.
  if .25<t<.95:
   strip=Image.new('RGBA',(720,1280));sd=ImageDraw.Draw(strip);x=int((t-.25)/.7*1000-140)
   sd.line((x,0,x-170,1280),fill=(175,205,255,65),width=12);strip=strip.filter(ImageFilter.GaussianBlur(18));bg=Image.alpha_composite(bg,strip)
  dr=ImageDraw.Draw(bg);a2=ease((t-.65)/.35)
  centered(dr,572,'三档出水',F(64),(242,246,255,int(255*a2)))
  centered(dr,665,'按压辅助除垢',F(36),(170,185,208,int(255*a2)))
  stage='01 轮廓显影' if t<.8 else '02 双产品对角入场'
 elif t<3.45:
  a=ease((t-2.3)/1.15);s=1.15+.58*a
  # Physical photo pixels only: planar position/scale, no invented side or back.
  cx=360+(asset.width/2-191)*s;cy=680+(asset.height/2-190)*s
  layer(bg,s,0,(cx,cy),1)
  stage='03 面板聚焦'
 else:
  bg=macro.convert('RGBA');stage='04 准备接真实按压'
 dr=ImageDraw.Draw(bg);dr.rectangle((0,0,720,66),fill=(5,8,14,245));dr.text((24,17),'导演动态分镜｜照片分层，不是AI成片',font=F(23),fill='#c2cfe0')
 dr.rectangle((0,1200,720,1280),fill=(5,8,14,245));dr.text((24,1225),stage,font=F(29),fill='#e3ebf7')
 rgb=bg.convert('RGB')
 if n in (15,45,87,111):rgb.save(R/f'关键帧-{n:03d}.jpg',quality=93)
 p.stdin.write(rgb.tobytes())
p.stdin.close();assert p.wait()==0
real=R/'真实按压-2秒.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss','0.3','-i',str(B/'预览/素材可用性审查/裁剪候选/05-中央红钮按压.mp4'),'-t','2','-vf',"drawbox=x=0:y=0:w=iw:h=66:color=0x05080e:t=fill,drawtext=fontfile=/System/Library/Fonts/STHeiti\\ Light.ttc:text='实拍裁剪接入｜非AI动作':x=24:y=18:fontsize=23:fontcolor=white",'-an','-r','30','-c:v','libx264','-crf','19','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart','-y',str(real)],check=True)
lst=R/'拼接单.txt';lst.write_text("file '"+str(out)+"'\nfile '"+str(real)+"'\n")
final=B/'输出/黑底酷炫开场-6秒动态分镜-未AI生成.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(lst),'-c','copy','-movflags','+faststart','-y',str(final)],check=True)
m=B/'工程/manifest.json';j=json.loads(m.read_text());j['directorAnimatic']={'status':'local_storyboard_not_ai_generation','source':str(src),'output':str(final),'duration':6,'newPaidRequests':0,'method':'Actual photo pixels masked and animated as two2D layers, then real press crop; no3D rotation or AI render claimed','checks':'Pending output verification','purpose':'Review composition, light cue, timing and cut to real action before buying any generation'};m.write_text(json.dumps(j,ensure_ascii=False,indent=2))
print(final)

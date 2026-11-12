from pathlib import Path
from PIL import Image,ImageOps
import subprocess,io,json,os
B=Path(__file__).resolve().parent
ROOT=B.parents[4]
R=ROOT/'products/主推花洒/银色/原图'
FONT=ROOT/'production/花洒视频/制作-v1/工程/fred/public/fonts/MiSans-Heavy.otf'
assert FONT.exists(),FONT
shots=[('95',4,'花洒模式','常规水型'),('96',4,'喷雾模式','喷雾水型'),('97',4,'综合模式','两种水型结合'),('93',3,'下方按键','用于切换三种模式'),('94',3,'中央红钮','按压辅助除垢')]
segments=[]
for i,(k,dur,title,desc) in enumerate(shots):
 
 if os.environ.get('TASK_ONLY_SHOT') and os.environ['TASK_ONLY_SHOT']!=k:
  segments.append(B/f'insert-{i}.mp4');continue
 src=next(R.glob('*_'+k+'_2.jpg'));im=ImageOps.exif_transpose(Image.open(src)).convert('RGB')
 if k=='93':im=im.crop((700,3650,2200,5700))
 if k=='94':im=im.crop((0,850,3900,4750))
 im.thumbnail((2000,2400));buf=io.BytesIO();im.save(buf,format='PNG')
 (B/f'title-{i}.txt').write_text(title);(B/f'desc-{i}.txt').write_text(desc)
 # Photo and product pixels are only uniformly scaled/cropped, no generated holes or water.
 vf=(f"loop=loop=-1:size=1:start=0,setpts=N/30/TB,scale=1080:1440:force_original_aspect_ratio=decrease,"
     f"pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=0xe9e6e1,setsar=1,"
     f"zoompan=z='1+0.025*on/{dur*30}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x1440:fps=30,"
     f"pad=1080:1920:0:230:color=0xe9e6e1,"
     f"drawtext=fontfile='{FONT}':textfile='{B/f'title-{i}.txt'}':fontsize=76:fontcolor=0x272625:x=(w-tw)/2:y=89,"
     f"drawbox=x=80:y=1760:w=920:h=3:color=0xb28a66:t=fill,"
     f"drawtext=fontfile='{FONT}':textfile='{B/f'desc-{i}.txt'}':fontsize=47:fontcolor=0x51483f:x=(w-tw)/2:y=1805,format=yuv420p")
 out=B/f'insert-{i}.mp4';log=B/f'insert-{i}.log'
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-f','image2pipe','-framerate','30','-i','pipe:0','-vf',vf,'-t',str(dur),'-an','-c:v','libx264','-preset','veryfast','-crf','20','-r','30','-threads','2','-y',str(out)]
 r=subprocess.run(cmd,input=buf.getvalue(),capture_output=True);log.write_bytes(r.stderr)
 assert r.returncode==0,r.stderr.decode();segments.append(out);print(k,'ready',flush=True)
(B/'concat.txt').write_text(''.join("file '"+str(p)+"'\n" for p in segments))
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(B/'concat.txt'),'-c','copy','-movflags','+faststart','-y',str(B/'扩展内容-18秒-剪辑素材.mp4')],check=True)
print('insert_complete',flush=True)

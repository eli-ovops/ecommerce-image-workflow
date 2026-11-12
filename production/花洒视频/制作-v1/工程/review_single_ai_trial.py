"""Build an honest silent review pack after the one generation finishes; does not call any API."""
from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;B=P.parent;R=P/'AI主视觉首帧-v1';Q=R/'视频候选核查';Q.mkdir(exist_ok=True)
raw=R/'AI试生成-主视觉-H3-803-原始.mp4';assert raw.exists(), 'Task has not produced a downloaded MP4'
def run(a):return subprocess.run(['ffmpeg','-hide_banner',*a],check=True,capture_output=True,text=True)
check=run(['-i',str(raw),'-map','0:v:0','-f','null','-']);(Q/'解码回执.txt').write_text(check.stderr)
preview=B/'输出/AI主视觉-H3-803-10秒候选-无音轨.mp4'
run(['-loglevel','error','-i',str(raw),'-map','0:v:0','-map_metadata','0','-c:v','copy','-an','-movflags','+faststart','-y',str(preview)])
F=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',20)
for board in range(2):
 sheet=Image.new('RGB',(1080,1980),'#151515');d=ImageDraw.Draw(sheet)
 for i in range(15):
  t=board*5+i/3
  path=Q/f'frame-{board*15+i:02d}.jpg'
  run(['-loglevel','error','-ss',str(t),'-i',str(raw),'-frames:v','1','-vf','scale=360:640:force_original_aspect_ratio=decrease,pad=360:640:(ow-iw)/2:(oh-ih)/2','-y',str(path)])
  im=Image.open(path);im.thumbnail((216,384));x=(i%5)*216;y=(i//5)*660;sheet.paste(im,(x,y));d.text((x+6,y+390),f'{t:.2f}s',font=F,fill='white')
 sheet.save(Q/f'候选时序-{board+1}.jpg',quality=93)
# Full-size start/middle/end remain separate from phone-scale contact sheets.
for name,t in [('start',0),('middle',5),('end',9.8)]:run(['-loglevel','error','-ss',str(t),'-i',str(raw),'-frames:v','1','-y',str(Q/(name+'.png'))])
m=P/'manifest.json';j=json.loads(m.read_text());j['singleAiTrial'].update(status='downloaded_pending_product_review',rawOutput=str(raw),silentCandidate=str(preview),reviewDirectory=str(Q),continuousViewing='not_performed',productDetailAcceptance='pending; not certified from decode or first frame');m.write_text(json.dumps(j,ensure_ascii=False,indent=2));print(preview)

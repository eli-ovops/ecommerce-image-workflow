from pathlib import Path
import subprocess,json
b=Path(__file__).resolve().parent.parent;eng=b/'工程';out=b/'输出/花洒广告-v3-重新剪辑-无BGM无配音.mp4'
paths=sorted((b/'CapCut重剪素材').glob('*.mp4'));(eng/'capcut-concat.txt').write_text(''.join("file '"+str(p)+"'\n"for p in paths))
rough=b/'预览/CapCut重剪-纯画面.mp4'
if not rough.exists():subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(eng/'capcut-concat.txt'),'-c','copy','-movflags','+faststart',str(rough)],check=True)
f="subtitles='"+str(b/'CapCut字幕-v3.srt')+"':force_style='FontName=Heiti SC,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00202020,BorderStyle=1,Outline=1,Shadow=1,Alignment=2,MarginV=40'"
if not out.exists():subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(rough),'-vf',f,'-an','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(out),'-f','null','-'],capture_output=True,text=True);(eng/'v3-技术回读.txt').write_text(r.stderr);assert r.returncode==0
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(out),'-vf','fps=1,scale=270:-1,tile=5x5','-frames:v','1',str(b/'预览/v3-整片.jpg')],check=True)
p=eng/'manifest.json';d=json.loads(p.read_text());d['capcutRevision']['preview']=str(out);d['capcutRevision']['native_status']='7段已在CapCut素材库可见，时间线仍空白，不能称原生工程已完成';d['capcutRevision']['checks']='完整解码及逐秒抽帧；非连续看听。无音轨，等待用户选免费配音与BGM。';p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
print(out)

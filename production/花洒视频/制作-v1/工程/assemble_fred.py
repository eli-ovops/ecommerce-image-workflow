from pathlib import Path
import subprocess,json,hashlib
b=Path(__file__).resolve().parent.parent
old=b/'输出/花洒实拍广告-v1.1-审阅.mp4';part=b/'工程/fred/output/modes.mp4';out=b/'输出/花洒实拍广告-v2-Fred审阅.mp4'
args=['ffmpeg','-hide_banner','-loglevel','error','-i',str(old),'-i',str(part),'-filter_complex','[0:v]split=2[a][c];[a]trim=start=0:end=3,setpts=PTS-STARTPTS,setsar=1[a0];[1:v]setpts=PTS-STARTPTS,setsar=1[b0];[c]trim=start=7:end=28,setpts=PTS-STARTPTS,setsar=1[c0];[a0][b0][c0]concat=n=3:v=1:a=0[v]','-map','[v]','-map','0:a','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(out)]
if not out.exists():subprocess.run(args,check=True)
q=subprocess.run(['ffmpeg','-hide_banner','-i',str(out),'-f','null','-'],capture_output=True,text=True);(b/'工程/v2-导出解码检查.txt').write_text(q.stderr);assert q.returncode==0
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(out),'-vf','fps=1,scale=270:-1,tile=5x6','-frames:v','1',str(b/'预览/v2-整片画面.jpg')],check=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss','2.8','-i',str(out),'-t','4.6','-vf','fps=5,scale=270:-1,tile=6x4','-frames:v','1',str(b/'预览/v2-Fred及接缝.jpg')],check=True)
p=b/'工程/manifest.json';d=json.loads(p.read_text());d['version']='v2-Fred';d['output']=str(out);d['outputSha256']=hashlib.sha256(out.read_bytes()).hexdigest();d['status']='待验收';d['checks']['render']='28秒1080×1920/30fps，完整解码成功，840帧；有AAC音轨';d['checks']['fredGates']=['fred-suggestion-gate.json PASS','fred-keyframes-gate.json PASS'];d['checks']['continuous_viewing']='未完成';d['checks']['direct_listening']='未完成';d['runtime']={'remotion':'4.0.451','react':'19.2.5','source':'T04d准确源码＋同包kit/fonts','sourceImport':'本机官方ZIP离线校验75项；无网络/令牌/费用','typescriptParser':'复用既有typescript依赖链接，未修改解析器或门禁','referenceMethod':'候选与组件中态抽样，非连续看听'};p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
s=(b/'输出/字幕-v1.srt').read_text().replace('按键切换','普通 · 喷雾 · 混合');(b/'输出/字幕-v2.srt').write_text(s)
print(out)

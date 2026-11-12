from pathlib import Path
import subprocess,json,shutil,hashlib,wave
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'原始素材'; PRE=ROOT/'预览'; OUT=ROOT/'输出'; ENG=ROOT/'工程'
files={'water_detail':'ef8070f47a1142bf4aa2042e1e3cd79d_raw.mp4','water_stable':'ee15c2f20a076d7642fdfbd7534e3660_raw.mp4','press':'fe3728b6728053cc0466e18dcaab7e58_raw.mp4','colors':'046c2a377a1eb743b693e04e40f6fa2d_raw.mp4'}
source_meta=[]
for key,name in files.items():
 src=Path('/Users/USER/Downloads')/name; dst=SRC/name
 if not dst.exists(): shutil.copy2(src,dst)
 sha=hashlib.sha256(dst.read_bytes()).hexdigest()
 assert sha==hashlib.sha256(src.read_bytes()).hexdigest()
 source_meta.append({'id':key,'original':str(src),'project_copy':str(dst),'sha256':sha,'content':key,'fps':30,'display_size':[2160,3840],'audio':True,'restriction':'用户实拍，仅本项目授权；原件保留'})
shots=[
 {'source':'water_detail','in':16.0,'duration':3.0,'title':'三档出水','sub':'普通 · 喷雾 · 混合'},
 {'source':'water_stable','in':5.0,'duration':4.0,'title':'按键切换','sub':''},
 {'source':'water_stable','in':17.0,'duration':4.0,'title':'喷雾出水','sub':''},
 {'source':'water_stable','in':27.0,'duration':4.0,'title':'','sub':''},
 {'source':'press','in':1.5,'duration':6.0,'title':'按压辅助除垢','sub':''},
 {'source':'press','in':8.0,'duration':3.0,'title':'短红针随按压伸出','sub':''},
 {'source':'colors','in':1.5,'duration':2.0,'title':'三色可选','sub':''},
 {'source':'colors','in':3.5,'duration':2.0,'title':'','sub':''},
]
cur=0
for s in shots:
 s['timeline_in']=cur;s['timeline_out']=cur+s['duration'];s['source_out']=s['in']+s['duration'];cur+=s['duration']
manifest={'version':'v1','status':'进行中','duration':cur,'size':[1080,1920],'fps':30,'route':{'target':'gpt-6-astra/medium','actual':'UNKNOWN'},'sources':source_meta,'shots':shots,'audio':{'source_audio_used':False,'reason':'尚未直接听音，首版不使用未经听审的现场音轨','music':'原创程序合成轻节奏，无引用第三方音轨','voiceover':False},'checks':{'source_visual':'每0.5秒抽帧及定向放大','continuous_viewing':'未完成','direct_listening':'未完成','customer_acceptance':'UNKNOWN','mode_mapping':'喷雾按可见雾束；普通/混合不逐镜头标定'},'generated_files':'本目录预览片段、粗剪、字幕、配乐、输出和QA均为本任务产物；保留用于返修'}
(ENG/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
font='/System/Library/Fonts/STHeiti Medium.ttc'
def run(cmd,label):
 print(label,flush=True)
 r=subprocess.run(cmd,capture_output=True,text=True)
 if r.returncode:
  (ENG/'last-error.txt').write_text(r.stderr);raise RuntimeError(r.stderr[-2500:])
for idx,s in enumerate(shots):
 dst=PRE/f'shot-{idx:02d}.mp4'
 if dst.exists(): continue
 run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(s['in']),'-i',str(SRC/files[s['source']]),'-t',str(s['duration']),'-an','-vf','scale=1080:1920:flags=lanczos,setsar=1,fps=30','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(dst)],f'剪辑镜头 {idx+1}/{len(shots)}')
concat=ENG/'concat.txt';concat.write_text(''.join("file '"+str(PRE/f'shot-{i:02d}.mp4')+"'\n" for i in range(len(shots))))
rough=PRE/'完整粗剪.mp4'
if not rough.exists():run(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(rough)],'合成完整粗剪')
# Original instrumental: own programmed notes, no third-party samples or melodies.
sr=48000;total=cur;x=np.zeros((int(sr*total),2),dtype=np.float64);rng=np.random.default_rng(251025)
def add(t,d,f,amp,pan=0):
 n=min(int(sr*d),len(x)-int(t*sr))
 if n<=0:return
 q=np.arange(n)/sr;env=(1-np.exp(-q*50))*np.exp(-q/(d*.45));z=(np.sin(2*np.pi*f*q)+.23*np.sin(2*np.pi*f*2*q))*env*amp
 start=int(t*sr);x[start:start+n,0]+=z*(.7-pan*.2);x[start:start+n,1]+=z*(.7+pan*.2)
beat=60/96
chords=[[57,60,64,67],[53,57,60,64],[48,55,60,64],[55,59,62,67]]
for b,t in enumerate(np.arange(0,total,beat)):
 ch=chords[(b//8)%4];m=ch[[0,2,1,3,2,1,3,2][b%8]]
 add(t,.65,440*2**((m+12-69)/12),.075,(-1 if b%2 else 1)*.5)
 if b%2==0:add(t,.48,440*2**((ch[0]-12-69)/12),.12)
 if b%4==0:
  n=min(int(sr*.18),len(x)-int(t*sr));q=np.arange(n)/sr
  z=np.sin(2*np.pi*(48*q+25*(1-np.exp(-q*28))/28))*np.exp(-q*25)*.12
  x[int(t*sr):int(t*sr)+n,:]+=z[:,None]
 if b%2==1:
  n=min(int(sr*.05),len(x)-int(t*sr));z=rng.normal(0,1,n)*np.exp(-np.arange(n)/sr*100)*.012
  x[int(t*sr):int(t*sr)+n,:]+=z[:,None]
fadein=np.minimum(np.arange(len(x))/sr/.4,1);fadeout=np.minimum((total-np.arange(len(x))/sr)/1.0,1);x*=np.minimum(fadein,fadeout)[:,None]
x=np.tanh(x)*.7
with wave.open(str(ENG/'原创配乐.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((x*32767).astype('<i2').tobytes())
filters=['scale=945:1680:flags=lanczos,pad=1080:1920:67:0:color=0x211b17'];srt=[];k=1
for i,s in enumerate(shots):
 if not s['title']:continue
 a=s['timeline_in'];b=s['timeline_out'];title=s['title'];path=ENG/f'title-{i}.txt';path.write_text(title)
 size=86 if len(title)<=7 else 70
 enable=f"between(t,{a},{b-.001})"
 filters += [f"drawbox=x=0:y=1680:w=1080:h=240:color=0x211b17@0.70:t=fill:enable='{enable}'",f"drawbox=x=60:y=1720:w=7:h=146:color=0xc58e60:t=fill:enable='{enable}'",f"drawtext=fontfile='{font}':textfile='{path}':fontsize={size}:fontcolor=white:x=100:y=1720:enable='{enable}'"]
 if s['sub']:
  sp=ENG/f'sub-{i}.txt';sp.write_text(s['sub']);filters.append(f"drawtext=fontfile='{font}':textfile='{sp}':fontsize=48:fontcolor=0xefd4ba:x=103:y=1830:enable='{enable}'")
 def ts(t):
  n=int(round(t*1000));return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
 srt.append(f"{k}\n{ts(a)} --> {ts(b)}\n{title}"+ ('\n'+s['sub'] if s['sub'] else '')+'\n');k+=1
(OUT/'字幕-v1.srt').write_text('\n'.join(srt));(ENG/'packaging-filter.txt').write_text(','.join(filters))
final=OUT/'花洒实拍广告-v1.1-审阅.mp4'
if not final.exists():run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(rough),'-i',str(ENG/'原创配乐.wav'),'-filter_script:v',str(ENG/'packaging-filter.txt'),'-map','0:v','-map','1:a','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',str(final)],'输出字幕配乐审阅版')
manifest['status']='待验收';manifest['output']=str(final);manifest['checks']['render']='完成，待技术回读与画面核对';(ENG/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(str(final),flush=True)

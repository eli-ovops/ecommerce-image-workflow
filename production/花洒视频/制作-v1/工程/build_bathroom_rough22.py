"""Local-only 22-second bathroom rough cut. No AI; no audio; original media stays read-only."""
from pathlib import Path
import json, subprocess, hashlib
from PIL import Image,ImageOps,ImageDraw,ImageFont
B=Path(__file__).resolve().parent.parent;ROOT=B.parents[2]
R=B/'预览/22秒粗剪核查';R.mkdir(exist_ok=True)
SEG=R/'分段';SEG.mkdir(exist_ok=True)
FONT=B/'工程/fred/public/fonts/MiSans-Heavy.otf'
FONT2=B/'工程/fred/public/fonts/MiSans-Medium.otf'
W,H=1080,1920
src=B/'原始素材'
photo=ROOT/'products/主推花洒/银色/原图/微信图片_20261022184342_89_2.jpg'
rows=[
 dict(id='S01',start=0,end=2.4,source=src/'ef8070f47a1142bf4aa2042e1e3cd79d_raw.mp4',si=16.2,crop=[520,900,180,40],text='三档出水',sub='真实水流展示'),
 dict(id='S02',start=2.4,end=4.2,source=src/'fe3728b6728053cc0466e18dcaab7e58_raw.mp4',si=1.5,crop=[360,640,200,120],text='中央红钮',sub=''),
 dict(id='S03',start=4.2,end=7.4,source=src/'fe3728b6728053cc0466e18dcaab7e58_raw.mp4',si=3.3,crop=[360,640,200,120],text='按压辅助除垢',sub=''),
 dict(id='S04',start=7.4,end=9.4,source=src/'fe3728b6728053cc0466e18dcaab7e58_raw.mp4',si=10.2,crop=[340,600,190,160],text='短红针细节',sub=''),
 dict(id='S05',start=9.4,end=11,source=photo,si=None,cropPhoto=[328,442,458,673],text='下方按键切档',sub=''),
 dict(id='S06',start=11,end=15,source=B/'工程/fred/output/bathroom-modes-rough.mp4',si=0,crop=None,text=None,sub=''),
 dict(id='S07',start=15,end=17,source=src/'ee15c2f20a076d7642fdfbd7534e3660_raw.mp4',si=17,crop=[440,782,250,230],text='喷雾出水',sub=''),
 dict(id='S08',start=17,end=19.8,source=src/'ee15c2f20a076d7642fdfbd7534e3660_raw.mp4',si=5,crop=[440,782,240,180],text='水流近景',sub=''),
 dict(id='S09',start=19.8,end=22,source=src/'ee15c2f20a076d7642fdfbd7534e3660_raw.mp4',si=27,crop=[440,782,240,280],text='三档出水',sub='按压辅助除垢'),
]
def run(c): subprocess.run(c,check=True)
def text_center(draw,txt,y,font,color):
 box=draw.textbbox((0,0),txt,font=font);draw.text(((W-box[2]+box[0])/2,y),txt,font=font,fill=color)
for row in rows:
 dur=round(row['end']-row['start'],4);row['source_in']=row['si'];row['source_out']=round(row['si']+dur,4) if row['si'] is not None else None
 out=SEG/(row['id']+'.mp4');row['segment']=str(out)
 if row['id']=='S06':
  run(['ffmpeg','-v','error','-i',str(row['source']),'-an','-vf','scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p','-r','30','-c:v','libx264','-crf','18','-preset','fast','-video_track_timescale','15360','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-y',str(out)]);continue
 cap=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(cap)
 d.rectangle((0,1620,W,H),fill=(18,19,21,255))
 text_center(d,row['text'],1672,ImageFont.truetype(str(FONT),82),(248,247,244,255))
 if row['sub']:text_center(d,row['sub'],1785,ImageFont.truetype(str(FONT2),46),(210,208,204,255))
 capfile=R/(row['id']+'-字幕.png');cap.save(capfile)
 inp=['-ss',str(row['si']),'-i',str(row['source'])] if row['si'] is not None else []
 if row['si'] is None:
  im=ImageOps.exif_transpose(Image.open(row['source'])).convert('RGB');factor=im.width/720
  im=im.crop(tuple(round(v*factor) for v in row['cropPhoto']))
  im=ImageOps.pad(im,(W,H),method=Image.Resampling.LANCZOS,color='#121315')
  pic=R/(row['id']+'-原图矩形裁剪.png');im.save(pic);inp=['-loop','1','-framerate','30','-i',str(pic)];row['preparedPhoto']=str(pic)
 if row.get('crop'):
  w,h,x,y=row['crop'];f=f'crop=iw*{w}/720:ih*{h}/1280:iw*{x}/720:ih*{y}/1280,'
 else:f=''
 f+='scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0x121315,setsar=1,setpts=PTS-STARTPTS[v];[v][1:v]overlay=0:0:format=auto,format=yuv420p[vout]'
 cmd=['ffmpeg','-hide_banner','-loglevel','error',*inp,'-loop','1','-i',str(capfile),'-filter_complex',f'[0:v]{f}','-map','[vout]','-an','-t',str(dur),'-r','30','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart','-y',str(out)]
 run(cmd);print(row['id']+' ready',flush=True)
playlist=R/'22秒拼接单.txt';playlist.write_text(''.join("file '"+row['segment']+"'\n" for row in rows))
final=B/'输出/花洒22秒-浴室素材粗剪-v1-无BGM无配音.mp4'
run(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(playlist),'-map','0:v:0','-an','-c:v','copy','-movflags','+faststart','-y',str(final)])
srt=[]
for i,row in enumerate(rows,1):
 def stamp(t):
  n=round(t*1000);return f'{n//3600000:02d}:{n//60000%60:02d}:{n//1000%60:02d},{n%1000:03d}'
 if row['text']:srt.append(f"{i}\n{stamp(row['start'])} --> {stamp(row['end'])}\n{row['text']}"+(('\n'+row['sub']) if row['sub'] else '')+'\n')
 else:srt.append(f"{i}\n{stamp(row['start'])} --> {stamp(row['end'])}\n三档出水：普通、喷雾、混合\n")
(B/'输出/花洒22秒-浴室素材粗剪-v1.srt').write_text('\n'.join(srt))
m=B/'工程/manifest.json';j=json.loads(m.read_text())
for row in rows:
 row['source']=str(row['source']);row['frameRate']=30;row['speed']=1;row['transition']='hard_cut' if row['id'] not in ('S01','S03') else ('start' if row['id']=='S01' else 'continuous_source_with_caption_change')
j['bathroomRough22']={'status':'rendered_pending_visual_checks','date':'2026-10-26','output':str(final),'durationSeconds':22,'width':W,'height':H,'fps':30,'audioStreams':0,'paidCalls':0,'aiGenerationCalls':0,'bathroomOnly':True,'officePhotosExcluded':True,'threeColorSequenceRemoved':True,'productProcessing':'Original bathroom media, rectangular crops and proportional scale only; no masking, recoloring, regeneration, relighting, interpolation or structural edits','bathroomTileRetained':True,'waterModeMapping':'Only spray labelled on actual spray; other dynamic flows unlabelled by mode','shots':rows,'checks':{'decode':'pending','sampledFrames':'pending','continuousViewing':'not_performed','productDetailAcceptance':'not_claimed'},'sourceHashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in set(row['source'] and Path(row['source']) for row in rows)},'editableEntry':str(Path(__file__).resolve()),'fredEntry':str(B/'工程/fred/src/bathroom-rough.tsx')}
j['currentProductionPlan']['status']='bathroom_only_rough_rendered_pending_review';j['currentProductionPlan']['bathroomRevision']='Latest user removes office/clutter sources; replace dual-photo opening with real water video; omit side-photo and three-color end; no paid generation, BGM or voice'
m.write_text(json.dumps(j,ensure_ascii=False,indent=2));print(final,flush=True)

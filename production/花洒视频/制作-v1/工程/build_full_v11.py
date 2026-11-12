"""22-second local assembly. No network, generated-video calls or audio."""
from pathlib import Path
import json, subprocess, hashlib

B = Path(__file__).resolve().parent.parent
R = B / '预览/整片-v11'
S = R / '分段'
S.mkdir(parents=True, exist_ok=True)
font = '/System/Library/Fonts/STHeiti Medium.ttc'
rows = [
    dict(id='01', source='/Users/USER/Downloads/01a177f8-1bb8-7123-9db8-faa5cc9fb6d6.mp4', source_in=0, duration=5, caption=''),
    dict(id='02', source=str(B/'输出/手动AI片-2至4.5秒-待保真复核-无声.mp4'), source_in=0, duration=2.5, caption=''),
    dict(id='03', source=str(B/'输出/三档同屏-v10-模式名称版-无声.mp4'), source_in=0, duration=5, caption=''),
    dict(id='04', source=str(B/'预览/素材可用性审查/裁剪候选/05-中央红钮按压.mp4'), source_in=.5, duration=4.5, caption='按压辅助除垢'),
    dict(id='05', source=str(B/'预览/素材可用性审查/裁剪候选/06-短红针状态变化.mp4'), source_in=0, duration=2.5, caption='短红针细节'),
    dict(id='06', source=str(B/'工程/正面干净首帧-v1/正面干净首帧-v2-连接软管.jpg'), source_in=None, duration=2.5, caption='三种模式 · 按压辅助除垢'),
]

def run(args):
    subprocess.run(args, check=True)

clock = 0
for row in rows:
    output = S / (row['id'] + '.mp4')
    args = ['ffmpeg', '-v', 'error', '-y']
    if row['source_in'] is None:
        args += ['-loop', '1', '-framerate', '30', '-i', row['source']]
    else:
        args += ['-ss', str(row['source_in']), '-i', row['source']]
    vf = 'scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1,setpts=PTS-STARTPTS,fps=30,format=yuv420p'
    if row['caption']:
        size = 58 if row['id'] == '06' else 68
        vf += f",drawtext=fontfile='{font}':text='{row['caption']}':fontsize={size}:fontcolor=white:borderw=3:bordercolor=black@0.7:shadowx=1:shadowy=3:x=(w-tw)/2:y=1640"
    args += ['-vf', vf, '-t', str(row['duration']), '-an', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', '-video_track_timescale', '15360', '-movflags', '+faststart', str(output)]
    run(args)
    row.update(segment=str(output), start=clock, end=clock+row['duration'], source_out=(row['source_in']+row['duration']) if row['source_in'] is not None else None)
    clock += row['duration']
    print(row['id']+' ready', flush=True)

playlist = R/'拼接单.txt'
playlist.write_text(''.join("file '"+r['segment']+"'\n" for r in rows))
final = B/'输出/花洒整片-v11-22秒粗剪-无BGM无配音.mp4'
run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(playlist),'-map','0:v:0','-c:v','copy','-an','-movflags','+faststart',str(final)])

def stamp(t):
    ms=round(t*1000)
    return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
subtitles = B/'输出/花洒整片-v11-字幕.srt'
captions = [r for r in rows if r['caption']]
subtitles.write_text('\n'.join(f"{i}\n{stamp(r['start'])} --> {stamp(r['end'])}\n{r['caption']}\n" for i,r in enumerate(captions,1)))
path = B/'工程/manifest.json'
manifest = json.loads(path.read_text())
manifest['fullAssemblyV11'] = dict(status='rendered_pending_review', output=str(final), editableEntry=str(Path(__file__).resolve()), subtitles=str(subtitles), duration=clock, width=1080,height=1920,fps=30,audioStreams=0,paidCalls=0,shots=rows,sourceHashes={r['source']:hashlib.sha256(Path(r['source']).read_bytes()).hexdigest() for r in rows},notes=['User approved latest middle-panel framing and mode names retained.','Real press and short-pin clips are noncontiguous source ranges joined by an explicit cut.','Closing is a static AI-cleaned reference image; not a real product motion recording.','Existing AI appearance and two water panels remain generated; exact product fidelity not independently certified.','No new Fred scenes added at rough-cut stage. Existing AI sweep supplies the visual transition.'],checks=dict(decode='pending',sampledFrames='pending',continuousViewing='not_performed'),artifacts=[str(playlist),str(subtitles)]+[str(p) for p in R.glob('*.jpg')])
path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
print(str(final), flush=True)

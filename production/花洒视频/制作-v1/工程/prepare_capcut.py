from pathlib import Path
import subprocess,json
b=Path(__file__).resolve().parent.parent;o=b/'CapCut重剪素材';o.mkdir(exist_ok=True)
shots=[
('01_水流开场','/Users/USER/Downloads/ef8070f47a1142bf4aa2042e1e3cd79d_raw.mp4',16.2,2.0,'scale=1080:1920'),
('02_Fred三档展开',str(b/'工程/fred/output/modes.mp4'),0,4.0,'crop=945:1680:67:0,scale=1080:1920'),
('03_喷雾水流','/Users/USER/Downloads/ee15c2f20a076d7642fdfbd7534e3660_raw.mp4',17.0,2.5,'scale=1080:1920'),
('04_水型近景','/Users/USER/Downloads/be191646e989a71496f3a2450e7946e6_raw.mp4',8.0,2.5,'scale=1080:1920'),
('05_红钮按压','/Users/USER/Downloads/fe3728b6728053cc0466e18dcaab7e58_raw.mp4',1.5,5.0,'scale=1080:1920'),
('06_红针回落','/Users/USER/Downloads/fe3728b6728053cc0466e18dcaab7e58_raw.mp4',10.0,2.5,'scale=1080:1920'),
('07_三色收尾','/Users/USER/Downloads/046c2a377a1eb743b693e04e40f6fa2d_raw.mp4',2.0,2.5,'scale=1080:1920')]
t=0;rows=[]
for name,src,start,dur,vf in shots:
 dst=o/(name+'.mp4')
 if not dst.exists():subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(start),'-i',src,'-t',str(dur),'-an','-vf',vf+',setsar=1,fps=30','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(dst)],check=True)
 rows.append({'name':name,'path':str(dst),'source':src,'source_in':start,'source_out':start+dur,'timeline_in':t,'timeline_out':t+dur});t+=dur
 print(name,flush=True)
p=b/'工程/manifest.json';d=json.loads(p.read_text());d['capcutRevision']={'duration':t,'shots':rows,'audio':'无BGM/无人声，等待用户选择','current_native_project':'待UI核验','design':'全幅竖屏实拍，无底部大黑块；保留Fred三档展开；字幕独立'};p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
(b/'CapCut字幕-v3.srt').write_text('''1
00:00:00,000 --> 00:00:02,000
三档出水

2
00:00:06,000 --> 00:00:08,500
喷雾出水

3
00:00:11,000 --> 00:00:16,000
按压辅助除垢

4
00:00:16,000 --> 00:00:18,500
短红针随按压伸出

5
00:00:18,500 --> 00:00:21,000
三色可选
''')

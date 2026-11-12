// Free local transition proof; still-frame animation is not an AI-video result.
const fs=require('fs'),path=require('path'),{execFileSync}=require('child_process');const d=__dirname,b=path.resolve(d,'../..');
const ff=(a)=>execFileSync('ffmpeg',['-hide_banner','-loglevel','error',...a],{stdio:'inherit'});
const image=path.join(d,'浴室主视觉首帧-v2-保真合成源.png');
const a=path.join(d,'主视觉本地试剪-3秒.mp4'),c=path.join(d,'真实出水试剪-3秒.mp4');
ff(['-i',image,'-vf',"zoompan=z='1+0.02*if(lt(on,15),0,if(gt(on,74),1,((on-15)/60)*((on-15)/60)*(3-2*((on-15)/60))))':x='iw*0.5324-iw*0.5324/zoom':y='ih*0.376-ih*0.376/zoom':d=90:s=1080x1920:fps=30,setsar=1,format=yuv420p",'-frames:v','90','-an','-c:v','libx264','-crf','18','-preset','fast','-video_track_timescale','15360','-movflags','+faststart','-y',a]);
ff(['-ss','5','-i',path.join(b,'原始素材/ee15c2f20a076d7642fdfbd7534e3660_raw.mp4'),'-vf','crop=iw*440/720:ih*782/1280:iw*240/720:ih*180/1280,scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0x121315,setsar=1,format=yuv420p','-frames:v','90','-r','30','-an','-c:v','libx264','-crf','18','-preset','fast','-video_track_timescale','15360','-movflags','+faststart','-y',c]);
const list=path.join(d,'衔接试剪单.txt');fs.writeFileSync(list,`file '${a}'\nfile '${c}'\n`);
const out=path.join(b,'输出/主视觉接实拍-6秒试剪-v1-未生成AI视频.mp4');
ff(['-f','concat','-safe','0','-i',list,'-map','0:v:0','-an','-c:v','copy','-movflags','+faststart','-y',out]);
const m=path.join(b,'工程/manifest.json'),j=JSON.parse(fs.readFileSync(m));j.heroTransitionPreview={status:'rendered_pending_checks',output:out,durationSeconds:6,fps:30,audioStreams:0,firstPart:'0–3s: approved v2 composite, deterministic2% planar zoom; not AI video generation',secondPart:'3–6s: authentic bathroom water, ee15 original5–8s, no per-mode label',transition:'Intentional hard cut between dry macro and real water; not a continuous operation or matched lighting claim',videoGenerationCalls:0,paidCalls:0,entry:__filename};fs.writeFileSync(m,JSON.stringify(j,null,2));console.log(out);

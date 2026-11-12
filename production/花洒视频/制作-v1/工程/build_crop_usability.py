from pathlib import Path
import subprocess, json
from PIL import Image, ImageDraw, ImageFont

B=Path(__file__).resolve().parent.parent
R=B/'预览/素材可用性审查'
C=R/'裁剪候选'
R.mkdir(exist_ok=True); C.mkdir(exist_ok=True)
FONT='/System/Library/Fonts/STHeiti Light.ttc'
F=lambda n:ImageFont.truetype(FONT,n)
SRC=B/'原始素材'
cases=[
 dict(id='01',name='斜向水流',file=str(SRC/'ef8070f47a1142bf4aa2042e1e3cd79d_raw.mp4'),start=16.2,dur=3,crop=[520,900,180,40],status='背景仍明显｜不能直接采用',color='#ff9c74',notes=['喷头与水线保留下来。','上方空墙减少，瓷砖纹仍贯穿水流。','再裁紧会损失喷头或水幕。','保留真实水流证据；干净外观需另补。'],decision='needs_background_solution',suggest='AI补干净外观/衔接；不能把本段标成已去背景。'),
 dict(id='02',name='稳定水流 A',file=str(SRC/'ee15c2f20a076d7642fdfbd7534e3660_raw.mp4'),start=5,dur=3,crop=[440,880,240,180],status='背景仍明显｜不能直接采用',color='#ff9c74',notes=['减少左右空墙，保留出水位置。','水线后面仍有清楚瓷砖接缝。','下柄被裁掉，无法演示按键切档。','普通/混合对应尚未最终核定。'],decision='needs_background_solution',suggest='只保留作真实水型核对；不能靠字幕指定档位。'),
 dict(id='03',name='喷雾水流',file=str(SRC/'ee15c2f20a076d7642fdfbd7534e3660_raw.mp4'),start=17,dur=3,crop=[440,880,250,230],status='背景仍明显｜不能直接采用',color='#ff9c74',notes=['喷头与雾束仍可见。','透明雾束后面的瓷砖无法靠裁剪去掉。','不要把雾束误当背景抠掉。','本轮未AI补水、换背景或调强水量。'],decision='needs_background_solution',suggest='真实喷雾保留作依据；单靠裁剪不满足干净背景。'),
 dict(id='04',name='稳定水流 B',file=str(SRC/'ee15c2f20a076d7642fdfbd7534e3660_raw.mp4'),start=27,dur=3,crop=[440,880,240,280],status='背景仍明显｜不能直接采用',color='#ff9c74',notes=['保留水流方向和喷头侧壁。','黑白纹理仍明显，裁剪并未解决背景。','不把此候选直接写成混合档。','没有通过不代表原素材需要删除。'],decision='needs_background_solution',suggest='保留作核对；正式片需重组镜头或额外背景方案。'),
 dict(id='05',name='中央红钮按压',file=str(SRC/'fe3728b6728053cc0466e18dcaab7e58_raw.mp4'),start=1.5,dur=5,crop=[360,640,200,120],status='裁剪后可用｜操作微距',color='#73e3b0',notes=['只保留红钮、拇指和周边真实孔位。','不展示完整外形或下方切档按钮。','需要检查整个动作中是否露出背景。','本段不需要AI重造按压。'],decision='usable_crop_pending_temporal_check',suggest='用于按压辅助除垢特写；保持真实动作，不延伸清垢效果。'),
 dict(id='06',name='短红针状态变化',file=str(SRC/'fe3728b6728053cc0466e18dcaab7e58_raw.mp4'),start=10,dur=2.5,crop=[340,600,190,160],status='裁剪后可用｜针孔局部',color='#73e3b0',notes=['面板填满取景，弱化原环境。','保留实际短红针，未增加或重画。','与前一段属于不同源时间。','后期不得拼成伪连续按压。'],decision='usable_crop_pending_temporal_check',suggest='用于独立细节插镜；如与上镜不连续，用明确切换。'),
 dict(id='07',name='倾斜水型近景',file=str(B/'CapCut重剪素材/04_水型近景.mp4'),start=0,dur=2.5,crop=[520,900,140,80],status='背景仍明显｜仅保留候选',color='#ff9c74',notes=['来源是此前截出的2.5秒片段。','对应原片约8.0–10.5秒。','原整段文件本轮未找到，未冒充看过。','裁后仍有大面积瓷砖纹。'],decision='needs_background_solution',suggest='不作为完整干净水流镜头；保留局部取证。'),
 dict(id='08',name='三色手持展示',file=str(SRC/'046c2a377a1eb743b693e04e40f6fa2d_raw.mp4'),start=2,dur=3,crop=[700,700,10,450],status='不建议采用｜照片重新排布',color='#f5ce75',notes=['裁掉大部分上方空墙。','三支产品依旧相互遮挡并被源画框裁切。','手和背景纹理仍占较多面积。','用现有三色照片后期排布，不必买AI。'],decision='replace_with_real_photo_composite',suggest='三色使用各SKU实拍重排；不以AI换色替代。'),
]

def run(cmd): subprocess.run(cmd,check=True)
def card(row=None,summary=False):
    im=Image.new('RGB',(1920,1080),'#10151c');d=ImageDraw.Draw(im)
    if row:
        d.text((48,20),row['id']+'  '+row['name'],font=F(42),fill='white')
        d.text((48,86),'原画面：绿色框为保留区域',font=F(28),fill='#b6c0ce')
        d.text((570,86),'裁剪后：保持比例，不拉伸',font=F(28),fill='#b6c0ce')
        d.text((1080,170),row['status'],font=F(35),fill=row['color'])
        y=255
        for n,line in enumerate(row['notes'],1):
            # Short fixed lines keep mobile/desktop readability predictable.
            d.text((1080,y),str(n)+'. '+line,font=F(28),fill='#e0e5eb');y+=80
        d.text((1080,680),'判定标准',font=F(30),fill='#b6c0ce')
        for n,line in enumerate(['背景干净 + 主体/动作完整','裁剪黑边仅用于展示保留范围','本片不是正式广告剪辑']):
            d.text((1080,735+n*50),line,font=F(27),fill='#b6c0ce')
        extra='（此前截取片段；原片8.0–10.5秒）' if row['id']=='07' else ''
        d.text((48,988),f"源片 {row['start']:.1f}–{row['start']+row['dur']:.1f}秒  |  不变速、不改水流、不加音乐  {extra}",font=F(27),fill='#c5ced9')
    elif summary:
        d.text((90,100),'本轮结论：先保留真实功能，再决定AI补哪里',font=F(50),fill='white')
        items=[('可用','#73e3b0','红钮按压、短红针局部：紧裁剪保留真实动作。'),('仍有背景','#ff9c74','四组水流与倾斜水型：瓷砖在水后面，裁剪无法清除。'),('后期替换','#f5ce75','三色手持：改用现有各SKU照片排布，不必生成。'),('AI候选','#a8b9ff','干净产品开场和必要衔接；本轮没有生成。')]
        for i,(label,col,line) in enumerate(items):
            y=260+i*145;d.text((90,y),label,font=F(36),fill=col);d.text((340,y),line,font=F(34),fill='white')
        d.text((90,920),'没有补拍要求 · 没有付费调用 · 没有把未解决的背景标成通过',font=F(32),fill='#b6c0ce')
    else:
        d.text((100,180),'现有素材裁剪可用性预览',font=F(64),fill='white')
        for i,line in enumerate(['左：原片与裁剪框    右：裁剪结果    最右：判断与用途','8组候选，覆盖项目中可恢复的视频素材','只做裁剪与编排：不AI生成、不补拍、不改真实水型','这是可用性检查，不是最终成片。可暂停查看说明。']):
            d.text((100,350+i*100),line,font=F(36),fill='#c5ced9')
    return im

def frame(path,t,out):
    run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(path),'-vf','scale=720:1280','-frames:v','1','-y',str(out)])

for row in cases:
    tag=row['id']; path=Path(row['file']); assert path.is_file(),path
    # Sample start/middle/end before classification is considered final.
    for j,off in enumerate((0,row['dur']/2,max(0,row['dur']-.1))):
        raw=R/f'{tag}-sample{j}.jpg'; frame(path,row['start']+off,raw)
        im=Image.open(raw);w,h,x,y=row['crop'];im.crop((x,y,x+w,y+h)).save(R/f'{tag}-crop{j}.jpg',quality=93)
    base=R/f'{tag}-card.png'; card(row).save(base)
    w,h,x,y=row['crop']; comp=R/f'{tag}-对比.mp4'; crop=C/f'{tag}-{row["name"]}.mp4'
    fc=(f'[1:v]scale=720:1280,setsar=1,split=3[o][c][e];'
        f'[o]drawbox=x={x}:y={y}:w={w}:h={h}:color=0x73e3b0:t=4,scale=450:800[ov];'
        f'[c]crop={w}:{h}:{x}:{y},scale=450:800:force_original_aspect_ratio=decrease,pad=450:800:(ow-iw)/2:(oh-ih)/2:color=black[cv];'
        f'[e]crop={w}:{h}:{x}:{y},scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2:color=black,fps=30[export];'
        '[0:v][ov]overlay=48:150:shortest=1[b];[b][cv]overlay=570:150:shortest=1,fps=30[v]')
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-loop','1','-i',str(base),'-ss',str(row['start']),'-t',str(row['dur']),'-i',str(path),'-filter_complex',fc,
         '-map','[v]','-an','-t',str(row['dur']),'-c:v','libx264','-crf','23','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart','-y',str(comp),
         '-map','[export]','-an','-t',str(row['dur']),'-c:v','libx264','-crf','20','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart','-y',str(crop)]
    run(cmd);row['comparison']=str(comp);row['cropped']=str(crop)
    print(tag+' rendered',flush=True)

for name,dur,is_summary in [('intro',3,False),('summary',6,True)]:
    img=R/(name+'.png');card(summary=is_summary).save(img)
    run(['ffmpeg','-hide_banner','-loglevel','error','-loop','1','-i',str(img),'-t',str(dur),'-r','30','-an','-c:v','libx264','-crf','23','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart','-y',str(R/(name+'.mp4'))])

playlist=R/'comparison-concat.txt'
files=[R/'intro.mp4']+[Path(c['comparison']) for c in cases]+[R/'summary.mp4']
playlist.write_text(''.join("file '"+str(p)+"'\n" for p in files))
out=B/'输出/素材可用性预览-v1-原片与裁剪对比.mp4'
run(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(playlist),'-c','copy','-movflags','+faststart','-y',str(out)])
# Results are written back into the existing project manifest, not a parallel manifest.
p=B/'工程/manifest.json';m=json.loads(p.read_text());m['cropUsabilityReview']={'version':'v1','date':'2026-10-26','output':str(out),'cases':cases,'method':'Actual crops rendered; first/middle/end and temporal samples require visual review','continuousViewing':'NOT_PERFORMED','directListening':'NOT_PERFORMED','audio':'No audio included','newPaidRequests':0,'requiresReshoot':False,'missingOriginals':['ebe595728400f9f45b47d6eca2400d43_raw.mp4','be191646e989a71496f3a2450e7946e6_raw.mp4'],'recoveredTrim':'be191 source8.0–10.5 from existing CapCut trim'}
m['currentProductionPlan']['status']='awaiting_crop_usability_review';m['currentProductionPlan']['requiresReshoot']=False;m['currentProductionPlan']['paidGenerationAllowed']=False
p.write_text(json.dumps(m,ensure_ascii=False,indent=2))
print(out,flush=True)

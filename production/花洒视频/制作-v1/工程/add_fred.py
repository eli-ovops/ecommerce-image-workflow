from pathlib import Path
import shutil,json,hashlib
base=Path(__file__).resolve().parent.parent
r=base/'工程/fred';r.mkdir(exist_ok=True)
src=Path('/Volumes/EXTERNAL/自媒体/Fred付费资料全站学习-20261016/解包只读副本/fred-wave2-42-20261012')
for sub in ['src/components','src/kit','public','output','evidence']:(r/sub).mkdir(parents=True,exist_ok=True)
for n in ['theme.ts','ui.tsx']:shutil.copy2(src/'src/kit'/n,r/'src/kit'/n)
shutil.copytree(src/'public/fonts',r/'public/fonts',dirs_exist_ok=True)
shutil.copy2(base/'预览/shot-01.mp4',r/'public/water.mp4')
p=r/'src/kit/ui.tsx';s=p.read_text();s=s.replace("background: background ?? (dark ? S.dark : '#fff')","background: background ?? 'transparent'")
s=s.replace('width: 1920, height: 1080, transform: `scale(${width / 1920})`','width: 1080, height: 1920, transform: `scale(1)`')
s=s.replace("brand = true","brand = false");p.write_text(s)
orig=src/'src/components/T04d-CategoryFocus.tsx';p=r/'src/components/T04d-CategoryFocus.tsx';s=orig.read_text()
s='// Adapted from Fred T04d CategoryFocus: complete branch reveal, focus and recede; native vertical overlay.\n'+s
s=s.replace('860 /','650 /').replace('1500 /','900 /').replace('Math.min(108,','Math.min(88,')
s=s.replace('960 -','540 -').replace('540 - treeH','1230 - treeH').replace('540 - root.h','1230 - root.h').replace('540 - fp.h','1230 - fp.h')
s=s.replace('Math.min(150, 1400','Math.min(125, 900').replace('width={1920} height={1080}','width={1080} height={1920}')
s='\n'.join(l for l in s.split('\n') if '<Sfx name=' not in l);p.write_text(s)
(r/'src/index.tsx').write_text('''// Actual call to adapted Fred T04d, with matching source kit and fonts.
import React from 'react';
import {AbsoluteFill,Composition,OffthreadVideo,registerRoot,staticFile} from 'remotion';
import {CategoryFocus} from './components/T04d-CategoryFocus';
export function Modes(){return <AbsoluteFill style={{background:'#211b17'}}>
<OffthreadVideo muted src={staticFile('water.mp4')} style={{position:'absolute',left:67,top:0,width:945,height:1680}}/>
<CategoryFocus topic="三档出水" categories={['普通','喷雾','混合']} focus={1} cues={[.85,1.15,1.45,2.4]}/>
</AbsoluteFill>}
const Root=()=> <Composition id="Modes" component={Modes} width={1080} height={1920} fps={30} durationInFrames={120}/>;
registerRoot(Root);
''')
mods=Path('/Volumes/EXTERNAL/自媒体/deepseek-deepinfer-20261021/04-Fred整片重制/node_modules')
if not (r/'node_modules').exists():(r/'node_modules').symlink_to(mods,target_is_directory=True)
(r/'package.json').write_text(json.dumps({'name':'shower-fred-overlay','private':True,'dependencies':{'remotion':'4.0.451','react':'19.2.5','react-dom':'19.2.5'}}))
(r/'render.cjs').write_text('''const path=require('path');const {bundle}=require('@remotion/bundler');const {selectComposition,openBrowser,renderStill,renderMedia}=require('@remotion/renderer');
(async()=>{const root=__dirname;const serveUrl=await bundle({entryPoint:path.join(root,'src/index.tsx'),outDir:path.join(root,'.bundle'),publicDir:path.join(root,'public')});const browser=await openBrowser('chrome',{browserExecutable:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});try{const composition=await selectComposition({serveUrl,id:'Modes',puppeteerInstance:browser});for(const frame of [15,45,60,80,105,119]){await renderStill({serveUrl,composition,frame,output:path.join(root,'evidence',`f${frame}.png`),puppeteerInstance:browser});}await renderMedia({serveUrl,composition,outputLocation:path.join(root,'output/modes.mp4'),codec:'h264',muted:true,crf:18,concurrency:2,puppeteerInstance:browser,onProgress:({progress})=>{if(Math.round(progress*100)%20===0)console.log(Math.round(progress*100))}});console.log('DONE');}finally{await browser.close({silent:true})}})().catch(e=>{console.error(e);process.exit(1)});
''')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=base/'工程/manifest.json';d=json.loads(m.read_text());page=d['pages'][0]
ids=['fred-wave2-42-t04d','library-legacy81-b019','fred-wave3-40-t17c'];names=['T04d','L81-B019','T17c'];reasons=['主题分出三类，再把喷雾移中，与下一段真实喷雾镜头衔接；保留分支、擦出和退焦。','三张图转为能力更适合案例归类，本片无需把真实水流缩成三张图片卡。','目录树及文件定位不符合花洒档位展示，无需文件图标或层级目录。']
page['componentPlan']['candidates']=[{'id':i,'decision':'selected' if j==0 else 'rejected','reason':reasons[j]}for j,i in enumerate(ids)]
page['componentPlan']['inspectedReferences']=[{'id':i,'path':f'/Volumes/EXTERNAL/自媒体/资产库/FredTalk/组件视频/{n}-1-preview.mp4','sha256':sha(f'/Volumes/EXTERNAL/自媒体/资产库/FredTalk/组件视频/{n}-1-preview.mp4'),'observations':reasons[j],'method':'每0.5秒时序抽帧，非连续视听','sheet':str(base/f'预览/Fred候选/{n}.jpg')} for j,(i,n) in enumerate(zip(ids,names))]
page['referenceChoices']=[{'id':ids[0],'reason':reasons[0],'preserve':'主题→三分支→喷雾聚焦，黑胶囊、原字体、阴影、弹簧、擦出和退焦完整关系','change':'画布改原生1080×1920，图形位于水流下半部，不遮喷头；取消作者品牌和组件音效；换本品文字和cue','useScope':'3–7秒','source':{'path':str(orig),'sha256':sha(orig),'symbol':'CategoryFocus'},'implementation':{'path':str(p),'sha256':sha(p),'symbol':'CategoryFocus'},'callSite':{'path':str(r/'src/index.tsx'),'sha256':sha(r/'src/index.tsx'),'symbol':'Modes','callee':'CategoryFocus'},'useMode':'local','keyAction':'三分支逐个擦出，喷雾居中放大，其他分支退焦'}]
d['componentDistributionReview']={'scope':'仅一段Fred组件，其余实拍和字幕','reason':'适量动效，避免整片转卡片讲解'}
d['status']='进行中';m.write_text(json.dumps(d,ensure_ascii=False,indent=2))

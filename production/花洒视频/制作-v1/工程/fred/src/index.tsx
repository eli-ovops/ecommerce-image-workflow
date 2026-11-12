// Actual call to adapted Fred T04d, with matching source kit and fonts.
import React from 'react';
import {AbsoluteFill,Composition,OffthreadVideo,registerRoot,staticFile} from 'remotion';
import {CategoryFocus} from './components/T04d-CategoryFocus';
export function Modes(){return <AbsoluteFill style={{background:'#211b17'}}>
<OffthreadVideo muted src={staticFile('water.mp4')} style={{position:'absolute',left:67,top:0,width:945,height:1680}}/>
<CategoryFocus topic="三档出水" categories={['普通','喷雾','混合']} focus={1} cues={[.85,1.15,1.45,2.4]}/>
</AbsoluteFill>}
const Root=()=> <Composition id="Modes" component={Modes} width={1080} height={1920} fps={30} durationInFrames={120}/>;
registerRoot(Root);

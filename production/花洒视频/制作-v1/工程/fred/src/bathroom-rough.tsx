// Existing Fred T04d + exact kit; actual bathroom photo is an independent unmodified rectangular crop.
import React from 'react';
import {AbsoluteFill,Composition,Img,registerRoot,staticFile} from 'remotion';
import {CategoryFocus} from './components/T04d-CategoryFocus';
export function BathroomModes(){return <AbsoluteFill style={{background:'#e7e3de'}}>
<Img src={staticFile('bathroom-head.jpg')} style={{position:'absolute',left:120,top:80,width:840,height:1014}}/>
<div style={{position:'absolute',inset:0,transform:'translateY(220px)'}}><CategoryFocus topic="三档出水" categories={['普通','喷雾','混合']} focus={1} cues={[.9,1.18,1.46,2.95]}/></div>
</AbsoluteFill>}
const Root=()=> <Composition id="BathroomModes" component={BathroomModes} width={1080} height={1920} fps={30} durationInFrames={120}/>;
registerRoot(Root);

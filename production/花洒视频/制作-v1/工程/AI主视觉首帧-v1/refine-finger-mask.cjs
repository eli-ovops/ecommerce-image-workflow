// Local mask correction only: remove source bathroom background between real fingers.
const fs=require('fs'),path=require('path'),{execFileSync}=require('child_process');const d=__dirname,W=2160,H=3840;
let input=fs.readFileSync(path.join(d,'手工背景遮罩.pgm'));let header=Buffer.from(`P5\n${W} ${H}\n255\n`);let mask=Buffer.from(input.subarray(header.length));
function hole(start,commands){let p=start,points=[p];for(let cmd of commands){if(cmd.length===2){p=cmd;points.push(p);}else{let o=p;for(let i=1;i<=80;i++){let t=i/80,u=1-t;points.push([u*u*u*o[0]+3*u*u*t*cmd[0]+3*u*t*t*cmd[2]+t*t*t*cmd[4],u*u*u*o[1]+3*u*u*t*cmd[1]+3*u*t*t*cmd[3]+t*t*t*cmd[5]]);}p=cmd.slice(4);}}
for(let y=2640;y<H;y++){let yy=y-2640+.5,xs=[];for(let i=0,j=points.length-1;i<points.length;j=i++){let [a,b]=points[j],[c,e]=points[i];if((b>yy)!=(e>yy))xs.push(a+(yy-b)*(c-a)/(e-b));}xs.sort((a,b)=>a-b);for(let i=0;i+1<xs.length;i+=2){let l=Math.max(0,Math.ceil(xs[i]+1560)),r=Math.min(W,Math.floor(xs[i+1]+1560));if(r>l)mask.fill(0,y*W+l,y*W+r);}}
}
// Deterministic colour separation only in narrow manually delimited background gaps.
// Handle boundary is protected independently; fingers are real original pixels.
const raw=execFileSync('ffmpeg',['-v','error','-i',path.join(d,'原视频-fe372-1.500秒.png'),'-vf','crop=600:1200:1560:2640,format=rgb24','-f','rawvideo','pipe:1'],{maxBuffer:4000000});
const edge=[[0,308],[100,303],[200,308],[300,319],[400,334],[500,355],[600,377],[700,399],[800,421],[900,445],[1000,466],[1200,485]];
function protectedEdge(y){for(let i=1;i<edge.length;i++)if(y<=edge[i][0]){let [a,b]=edge[i-1],[c,e]=edge[i];return b+(y-a)*(e-b)/(c-a)+2;}return 600;}
for(let y=0;y<1200;y++){
 if(!((y<160)||(y>340&&y<520)||(y>735&&y<915)))continue;
 for(let x=Math.ceil(protectedEdge(y));x<600;x++){
  let i=(y*600+x)*3,R=raw[i],G=raw[i+1];
  if(R-G<22)mask[(y+2640)*W+x+1560]=0;
 }
}
fs.writeFileSync(path.join(d,'手工背景遮罩-v2.pgm'),Buffer.concat([header,mask]));
const ff=(a)=>execFileSync('ffmpeg',['-hide_banner','-loglevel','error',...a],{stdio:'inherit'});
ff(['-i',path.join(d,'手工背景遮罩-v2.pgm'),'-vf','gblur=sigma=1.2:steps=2','-frames:v','1','-y',path.join(d,'手工背景遮罩-v2-soft.pgm')]);
ff(['-i',path.join(d,'浴室背景-2160x3840.png'),'-i',path.join(d,'原视频-fe372-1.500秒.png'),'-i',path.join(d,'手工背景遮罩-v2-soft.pgm'),'-filter_complex','[0:v]format=gbrp[b];[1:v]format=gbrp[s];[2:v]format=gray[m];[b][s][m]maskedmerge,format=rgb24[out]','-map','[out]','-frames:v','1','-y',path.join(d,'浴室主视觉首帧-v2-保真合成源.png')]);
ff(['-i',path.join(d,'浴室主视觉首帧-v2-保真合成源.png'),'-frames:v','1','-q:v','1','-y',path.join(d,'浴室主视觉首帧-v2.jpg')]);
ff(['-i',path.join(d,'浴室主视觉首帧-v2-保真合成源.png'),'-vf','crop=600:1200:1560:2640','-frames:v','1','-y',path.join(d,'指缝修订-v2.png')]);

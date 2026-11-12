// Original decoded video RGB + manual background mask; never generates product pixels.
const fs=require('fs'),path=require('path'),{execFileSync}=require('child_process');
const dir=__dirname,W=2160,H=3840;const polygon=[];
let cur=[0,300];polygon.push(cur);
const L=(x,y)=>{cur=[x,y];polygon.push(cur)};
const C=(a,b,c,d,e,f)=>{let p=cur;for(let i=1;i<=80;i++){let t=i/80,u=1-t;polygon.push([u*u*u*p[0]+3*u*u*t*a+3*u*t*t*c+t*t*t*e,u*u*u*p[1]+3*u*u*t*b+3*u*t*t*d+t*t*t*f]);}cur=[e,f];};
C(15,211,81,133,146,100);C(264,30,444,52,540,212);
L(540,490);C(499,543,473,610,466,684);L(540,678);L(540,960);L(365,960);
C(351,885,329,807,305,750);C(272,681,224,648,165,620);C(69,590,12,514,0,400);L(0,300);
const mask=Buffer.alloc(W*H);
for(let y=0;y<H;y++){
 const yy=(y+.5)/4,xs=[];
 for(let i=0,j=polygon.length-1;i<polygon.length;j=i++){
  let [x1,y1]=polygon[j],[x2,y2]=polygon[i];if((y1>yy)!=(y2>yy))xs.push((x1+(yy-y1)*(x2-x1)/(y2-y1))*4);
 }
 xs.sort((a,b)=>a-b);
 for(let i=0;i+1<xs.length;i+=2){let left=Math.max(0,Math.floor(xs[i]-4)),right=Math.min(W,Math.ceil(xs[i+1]+4));mask.fill(255,y*W+left,y*W+right);}
}
fs.writeFileSync(path.join(dir,'手工背景遮罩.pgm'),Buffer.concat([Buffer.from(`P5\n${W} ${H}\n255\n`),mask]));
const bg='/Users/USER/.codex/generated_images/01a1721a-bc9a-7620-b40e-20b6b2c1c9e3/exec-8df56d1d-8f44-43b8-bb68-24ca0ece8ad0.png';
fs.copyFileSync(bg,path.join(dir,'AI浴室背景-原生.png'));
const ff=(a)=>execFileSync('ffmpeg',['-hide_banner','-loglevel','error',...a],{stdio:'inherit'});
// Background reformat only. RGB planes of source foreground pass straight through masked merge.
ff(['-i',path.join(dir,'AI浴室背景-原生.png'),'-vf',`scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},format=rgb24`,'-frames:v','1','-y',path.join(dir,'浴室背景-2160x3840.png')]);
ff(['-i',path.join(dir,'浴室背景-2160x3840.png'),'-i',path.join(dir,'原视频-fe372-1.500秒.png'),'-i',path.join(dir,'手工背景遮罩.pgm'),'-filter_complex','[0:v]format=gbrp[b];[1:v]format=gbrp[s];[2:v]format=gray[m];[b][s][m]maskedmerge,format=rgb24[out]','-map','[out]','-frames:v','1','-y',path.join(dir,'浴室主视觉首帧-v1-保真合成源.png')]);
ff(['-i',path.join(dir,'浴室主视觉首帧-v1-保真合成源.png'),'-frames:v','1','-q:v','1','-y',path.join(dir,'浴室主视觉首帧-v1.jpg')]);
console.log('Composite saved; source video pixels retained by manual mask.');

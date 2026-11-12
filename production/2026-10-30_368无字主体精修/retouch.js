// Deterministic tonal retouch. No warping, hole reconstruction, or generated pixels.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const sharp=require('/Users/USER/.local/share/deepseek-harness/node_modules/sharp');
const B=__dirname,W=2220,H=1160;
const source=path.resolve(B,'../2026-10-29_圆形花洒_实拍主体验证/新实拍368/实拍原件.jpg');
const outline='M449 646 C332 644 238 706 205 788 C174 876 207 976 291 1022 C369 1066 484 1070 561 1033 C621 1003 652 975 696 963 C768 939 862 954 1142 955 Q1152 952 1151 936 L1187 937 Q1201 930 1196 895 Q1196 863 1185 862 L1150 861 L1145 845 C989 837 871 840 784 828 C699 819 674 797 640 750 C594 680 530 647 449 646Z';
const paths={
 protect:`<path d="${outline}" stroke="white" stroke-width="28"/>`,
 metal:'<path d="M720 821 Q865 844 1142 845 L1146 952 Q900 948 777 941 Q733 940 696 954 L690 939 Q722 917 730 882 Q737 853 720 821Z"/>',
 key:'<path d="M704 838 Q719 843 725 859 Q730 875 727 886 Q720 900 698 904 Q679 905 665 899 Q657 882 660 864 Q665 843 675 837 Q688 832 704 838Z"/>',
 shell:'<path d="M210 901 Q232 988 319 1022 Q422 1060 519 1037 Q573 1025 620 990 Q665 962 693 957 L683 973 Q613 994 569 1025 Q478 1082 371 1052 Q253 1037 220 967Z"/>'
};
async function mask(name,blur){const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}"><rect width="100%" height="100%" fill="black"/><g transform="translate(-280 -1160) scale(2)" fill="white">${paths[name]}</g></svg>`;fs.writeFileSync(path.join(B,`mask-${name}.svg`),svg);return sharp(Buffer.from(svg)).blur(blur).removeAlpha().raw().toBuffer();}
(async()=>{
 const original=await sharp(source).rotate().resize(2736,3648).extract({left:280,top:1160,width:W,height:H}).removeAlpha().raw().toBuffer();
 const blurred=await sharp(original,{raw:{width:W,height:H,channels:3}}).blur(12).raw().toBuffer();
 const keyblur=await sharp(original,{raw:{width:W,height:H,channels:3}}).blur(2.8).raw().toBuffer();
 const masks={};for(const n of Object.keys(paths))masks[n]=await mask(n,n==='protect'?8:3);
 const out=Buffer.from(original);let protectedChanges=0;
 const lum=(a,i)=>.2126*a[i]+.7152*a[i+1]+.0722*a[i+2];
 for(let i=0;i<out.length;i+=3){
  const bg=1-masks.protect[i]/255,metal=masks.metal[i]/255,key=masks.key[i]/255,shell=masks.shell[i]/255;
  const l=lum(original,i),lb=lum(blurred,i),lk=lum(keyblur,i);
  for(let c=0;c<3;c++){
   let v=original[i+c];
   // Background cleanup retains photographed shadow position and low-frequency shape.
   const bgValue=lb+(248-lb)*.39;
   v=v*(1-bg)+bgValue*bg;
   // Neutralize colored room reflections, preserve all original luminance transitions.
   const m=(l+.12*(255-l)*Math.sin(Math.PI*l/255))*.88+original[i+c]*.12;
   v=v*(1-metal)+m*metal;
   // Button: mild source-derived micro-reflection suppression, no painted highlight.
   const k=(.55*l+.45*lk)+.08*(255-l)*Math.sin(Math.PI*l/255);
   v=v*(1-key)+(.93*k+.07*original[i+c])*key;
   const sh=.92*(l+.1*(255-l))+.08*original[i+c];
   v=v*(1-shell)+sh*shell;
   out[i+c]=Math.max(0,Math.min(255,Math.round(v)));
  }
  if(masks.protect[i]===255&&metal===0&&key===0&&shell===0&&[0,1,2].some(c=>original[i+c]!==out[i+c]))protectedChanges++;
 }
 if(protectedChanges)throw Error('Protected panel pixels changed');
 await sharp(out,{raw:{width:W,height:H,channels:3}}).png().toFile(path.join(B,'精修像素母版.png'));
 await sharp(out,{raw:{width:W,height:H,channels:3}}).jpeg({quality:97,chromaSubsampling:'4:4:4'}).toFile(path.join(B,'368_无字主体精修.jpg'));
 await sharp(out,{raw:{width:W,height:H,channels:3}}).resize(720).jpeg({quality:95}).toFile(path.join(B,'缩略预览.jpg'));
 const panels=[{name:'整图',rect:{left:0,top:0,width:W,height:H},width:1110},{name:'喷面',rect:{left:95,top:125,width:960,height:850},width:960},{name:'头颈银键',rect:{left:870,top:340,width:580,height:440},width:870},{name:'银柄接口',rect:{left:1270,top:480,width:850,height:350},width:1020}];
 for(const p of panels){const a=await sharp(original,{raw:{width:W,height:H,channels:3}}).extract(p.rect).resize(p.width).png().toBuffer(),b=await sharp(out,{raw:{width:W,height:H,channels:3}}).extract(p.rect).resize(p.width).png().toBuffer();const h=(await sharp(a).metadata()).height;await sharp({create:{width:p.width*2+12,height:h,channels:3,background:'#fff'}}).composite([{input:a,left:0,top:0},{input:b,left:p.width+12,top:0}]).jpeg({quality:96,chromaSubsampling:'4:4:4'}).toFile(path.join(B,`对照_${p.name}_左原右修.jpg`));}
 fs.writeFileSync(path.join(B,'制作记录.json'),JSON.stringify({source,sourceSHA256:crypto.createHash('sha256').update(fs.readFileSync(source)).digest('hex'),operations:['EXIF rotate','isotropic resize 2736x3648','crop 280,1160,2220,1160','masked neutralize metal reflections','source-derived button microtexture suppression','background cleanup preserving original shadow'],geometryWarp:false,aiCalls:0,protectedInteriorPixelChanges:protectedChanges,actualModel:'UNKNOWN',actualEffort:'UNKNOWN',status:'候选待独立审阅',newFiles:fs.readdirSync(B)},null,2));
})();

// A/B selected builder. C historical definitions are inactive; use build-C.js for selected C345.
const fs=require('fs'),path=require('path'),sharp=require('/Users/USER/.local/share/deepseek-harness/node_modules/sharp');
const B=__dirname,S=path.join(B,'sources'),P=path.resolve(B,'../../../products/主推花洒/结构基准20261027/原件');
const bg=path.resolve(B,'../sources/background-native.png');
const generated='/Users/USER/.codex/generated_images/01a17c88-9784-7202-9a4a-0bf7830010e6/';
const edits={A:'exec-64ec3554-1a12-405f-8312-23c67e305c47.png',C:'exec-28ca40c4-a0e5-404b-8fec-d92fc43e920c.png'};
const outlineA='M 953 0 C 855 164 772 349 702 602 C 633 835 546 942 450 1114 C 345 1305 222 1534 40 1824 L 401 1824 C 516 1596 635 1390 727 1308 C 774 1270 833 1196 921 1102 C 1034 1035 1131 990 1222 921 C 1289 870 1332 810 1368 750 L 1368 0 Z';
const metalA='M 972 0 C 865 190 791 365 725 611 C 655 852 554 983 469 1135 C 350 1353 220 1572 86 1824 L 352 1824 C 470 1583 599 1401 690 1276 C 680 1240 690 1140 726 1073 C 760 1002 815 950 875 918 C 955 784 1021 632 1104 424 C 1157 279 1224 131 1283 0 Z';
const buttonA='M 875 966 C 892 969 929 997 937 1024 C 953 1055 929 1090 901 1118 L 777 1240 C 753 1261 741 1251 743 1227 C 745 1160 778 1085 810 1031 C 830 1000 851 973 875 966 Z';
const outlineC='M 236 579 C 500 600 740 630 992 660 L 1008 634 Q 1014 631 1026 633 C 1072 639 1092 661 1175 653 L 1200 674 L 1200 800 C 1045 810 850 823 708 820 C 500 792 310 751 230 711 Q 221 703 223 684 Z';
const metalC='M 207 698 C 282 664 363 634 468 607 C 655 558 865 557 1055 568 C 1271 580 1473 619 1671 644 Q 1691 648 1698 671 L 1696 778 Q 1690 791 1678 791 C 1485 756 1302 710 1133 700 C 1084 703 1024 718 974 718 C 749 743 498 783 212 800 Z';
const D=f=>`data:image/png;base64,${fs.readFileSync(path.join(S,f)).toString('base64')}`;
const defs=`<filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="12"/></filter><filter id="feather"><feGaussianBlur stdDeviation="2"/></filter>`;
function title(t,sub,fsz=126){return `<g transform="translate(82 55) skewX(-9)"><text x="12" y="137" font-family="Heiti SC" font-size="${fsz}" font-weight="bold" fill="#c7aa7d" stroke="#c7aa7d" stroke-width="5">${t}</text><text x="8" y="132" font-family="Heiti SC" font-size="${fsz}" font-weight="bold" fill="#241c17" stroke="#241c17" stroke-width="4">${t}</text></g><path d="M82 241 H720 L705 319 H67 Z" fill="#c9ae83"/><path d="M85 236 H711 L698 310 H72 Z" fill="#805336"/><text x="104" y="288" font-family="Heiti SC" font-size="45" font-weight="bold" fill="#fff9ee">${sub}</text>`}
function product(k,outline,metal,extra,w,h,transform){return `<defs><clipPath id="p${k}"><path d="${outline}"/></clipPath><mask id="m${k}"><rect width="${w}" height="${h}" fill="black"/><g fill="white" filter="url(#feather)"><path d="${metal}" ${k==='C'?'stroke="black" stroke-width="8"':''}/>${extra?`<path d="${extra}"/>`:''}</g></mask></defs><g transform="${transform}"><path d="${outline}" fill="#4b4239" opacity=".22" filter="url(#shadow)" transform="translate(11 13)"/><g clip-path="url(#p${k})"><image href="${D(k+'-photo.png')}" width="${w}" height="${h}"/><image href="${D(k+'-retouch.png')}" width="${w}" height="${h}" mask="url(#m${k})"/></g></g>`}
(async()=>{
 if(!fs.existsSync(path.join(S,'background.png')))fs.copyFileSync(bg,path.join(S,'background.png'));
 for(const [k,n,w,h] of [['A',350,1368,1824],['B',348,1368,1824]]){
  const f=fs.readdirSync(P).find(f=>f.includes('_'+n+'_'));const op=path.join(S,`original-${n}.jpg`);if(!fs.existsSync(op))fs.copyFileSync(path.join(P,f),op);
  await sharp(op).rotate().resize(w,h).png().toFile(path.join(S,k+'-photo.png'));
  if(edits[k]&&!fs.existsSync(path.join(S,k+'-retouch.png')))fs.copyFileSync(path.join(generated,edits[k]),path.join(S,k+'-retouch.png'));
 }
 let layers={
 A:product('A',outlineA,metalA,buttonA,1368,1824,'translate(-84 -432) scale(1.2)')+title('一键切换','普通 · 喷雾 · 混合'),
 B:`<defs><clipPath id="macro"><rect x="75" y="434" width="1290" height="930" rx="24"/></clipPath></defs><rect x="69" y="428" width="1302" height="942" rx="29" fill="#b69770"/><image href="${D('B-photo.png')}" x="-348" y="-180" width="2052" height="2736" clip-path="url(#macro)"/>`+title('中央除垢钮','按压辅助清理出水孔',119),
 C:`<defs><clipPath id="sideDetail"><rect x="65" y="0" width="1310" height="290" rx="18"/></clipPath></defs><g transform="translate(720 970) rotate(-25) translate(-720 -145)"><rect x="59" y="-6" width="1322" height="302" rx="24" fill="#b69770"/><rect x="65" y="0" width="1310" height="290" rx="18" fill="#f4eee4"/><g clip-path="url(#sideDetail)">`+product('C',outlineC,outlineC,'',1824,1368,'translate(-282 -928) scale(1.6)')+`</g></g>`+title('厚边细节','头颈前段近看')
 };
 for(let k of ['A','B']){
  const bgTransform=k==='B'?'translate(1440 1440) rotate(180)':k==='C'?'translate(1440 0) scale(-1 1)':'';
  let svg=`<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1440" viewBox="0 0 1440 1440"><defs>${defs}</defs><image href="${D('background.png')}" width="1440" height="1440" transform="${bgTransform}"/>${layers[k]}</svg>`;
  fs.writeFileSync(path.join(B,k+'-editable.svg'),svg);await sharp(Buffer.from(svg)).png().toFile(path.join(S,k+'-preview.png'));await sharp(Buffer.from(svg)).resize(360).png().toFile(path.join(S,k+'-phone.png'));
 }
 for(const [k,o,m,e,w,h] of [['A',outlineA,metalA,buttonA,1368,1824]]){
  fs.writeFileSync(path.join(B,k+'-product-mask.svg'),`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}"><path d="${o}" fill="white"/></svg>`);fs.writeFileSync(path.join(B,k+'-reflection-mask.svg'),`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}"><path d="${m}" fill="white" ${k==='C'?'stroke="black" stroke-width="8"':''}/>${e?`<path d="${e}" fill="white"/>`:''}</svg>`);
 }
 console.log('THREE_PREVIEWS_READY');
})().catch(e=>{console.error(e);process.exit(1)});

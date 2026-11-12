const fs=require('fs'),path=require('path');const sharp=require('/Users/USER/.local/share/deepseek-harness/node_modules/sharp');
const dir=__dirname;const root=path.resolve(dir,'../..');
const orig=path.join(root,'products/主推花洒/银色/原图/微信图片_20261022184355_94_2.jpg');
const data=(p,m)=>`data:${m};base64,${fs.readFileSync(p).toString('base64')}`;
(async()=>{
 await sharp(orig).rotate().resize(1368,1824,{fit:'fill'}).png().toFile(path.join(dir,'实拍94_等比预处理.png'));
 const bg=data(path.join(dir,'背景原图.png'),'image/png'), photo=data(path.join(dir,'实拍94_等比预处理.png'),'image/png');
 const mask=fs.readFileSync(path.join(dir,'实拍轮廓蒙版.svg'),'utf8').match(/<path d="([^"]+)"/)[1];
 const svg=`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1254" height="1254"><defs><clipPath id="p"><path d="${mask}"/></clipPath><filter id="shadow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="18"/></filter></defs>
 <image xlink:href="${bg}" width="1254" height="1254"/>
 <g transform="translate(0 200) scale(.92)"><path d="${mask}" fill="#3a251c" opacity=".36" filter="url(#shadow)" transform="translate(15 18)"/><image xlink:href="${photo}" width="1368" height="1824" clip-path="url(#p)"/></g>
 <g transform="translate(110 45) skewX(-7)" font-family="Heiti SC, PingFang SC, sans-serif" font-weight="900" paint-order="stroke fill">
 <text x="9" y="135" font-size="126" fill="#b86d31" stroke="#66341f" stroke-width="7">按压红钮</text><text x="3" y="129" font-size="126" fill="#fff4dc" stroke="#753e23" stroke-width="2">按压红钮</text>
 <path d="M3 187 H712 L694 268 H-12 Z" fill="#f3d2a3"/><path d="M0 181 H706 L690 258 H-13 Z" fill="#8a4729"/><text x="23" y="240" font-size="57" fill="#fff6e5">短针伸出 · 辅助除垢</text></g></svg>`;
 fs.writeFileSync(path.join(dir,'可编辑合成.svg'),svg);await sharp(Buffer.from(svg)).jpeg({quality:95,chromaSubsampling:'4:4:4'}).toFile(path.join(dir,'按压除垢_实拍广告候选.jpg'));console.log('DONE');
})().catch(e=>{console.error(e);process.exit(1)});
